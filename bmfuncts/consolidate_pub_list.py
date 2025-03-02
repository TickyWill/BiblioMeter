"""Module of functions for the consolidation of the publications-list 
in terms of:

- effective affiliation of the authors to the Institute;
- attributing department affiliation to the Institute authors.

"""

__all__ = ['built_final_pub_list',
           'concatenate_pub_lists',
           'split_pub_list_by_doc_type',
          ]


# Standard library imports
import os
from datetime import datetime
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import bmfuncts.institute_globals as ig
import bmfuncts.pub_globals as pg
from bmfuncts.add_ifs import add_if
from bmfuncts.format_files import format_page
from bmfuncts.format_files import set_base_keys_list
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.use_otps import save_otps
from bmfuncts.useful_functs import concat_dfs


def split_pub_list_by_doc_type(institute, org_tup, bibliometer_path, corpus_year):
    """Splits the dataframe of the publications final list into dataframes 
    corresponding to different documents types.

    This is done for the 'corpus_year' corpus. 
    These dataframes are saved through the `format_page` function 
    imported from `bmfuncts.format_files` module after setting 
    the attrubutes keys list through the `set_base_keys_list` 
    function imported from the same module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (int): Split ratio in % of the publications final list.
    """
    # Setting useful parameters for use of 'format_page' function
    common_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)

    # Setting useful aliases
    pub_list_path_alias = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    year_pub_list_file_alias = pub_list_file_base_alias + " " + corpus_year
    pub_list_file_alias = year_pub_list_file_alias + ".xlsx"
    other_dg_file_alias = year_pub_list_file_alias + "_" + pg.OTHER_DOCTYPE + ".xlsx"
    corpus_year_path = bibliometer_path / Path(corpus_year)
    pub_list_path = corpus_year_path / Path(pub_list_path_alias)
    pub_list_file_path = pub_list_path / Path(pub_list_file_alias)
    other_dg_path = pub_list_path / Path(other_dg_file_alias)

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    pub_id_col_alias = final_col_dic['pub_id']
    doc_type_alias = final_col_dic['doc_type']

    full_pub_list_df = pd.read_excel(pub_list_file_path)
    other_dg = full_pub_list_df.copy()
    pub_nb = len(full_pub_list_df)
    key_pub_nb = 0
    for key, doctype_list in pg.DOCTYPE_TO_SAVE_DICT.items():
        doctype_list = [x.upper() for x in  doctype_list]
        key_dg = pd.DataFrame(columns=full_pub_list_df.columns)

        for doc_type, dg in full_pub_list_df.groupby(doc_type_alias):
            if doc_type.upper() in doctype_list:
                key_dg = concat_dfs([key_dg, dg])
                other_dg = other_dg.drop(dg.index)

        key_pub_nb += len(key_dg)
        key_dg_file_alias = year_pub_list_file_alias + "_" + key + ".xlsx"
        key_dg_path = pub_list_path / Path(key_dg_file_alias)

        key_dg = key_dg.sort_values(by=[pub_id_col_alias])
        wb, _ = format_page(key_dg, common_df_title,
                            attr_keys_list=format_cols_list)
        wb.save(key_dg_path)

    other_dg = other_dg.sort_values(by=[pub_id_col_alias])
    wb, _ = format_page(other_dg, common_df_title,
                        attr_keys_list=format_cols_list)
    wb.save(other_dg_path)

    split_ratio = 100
    if pub_nb != 0:
        split_ratio = round(key_pub_nb / pub_nb*100)
    return split_ratio


def _set_dpt_otp_df(dpt_label, in_file_base, in_path):
    """Gets the publications list of the a department 
    from the EXCEL files where the user has set the OTPs.

    The name of the file is build using the file-name base 
    and the department label. This name is added '_ok' if 
    this file exists in the folder of files. 
    Then the file is read as a multisheet EXCEL file. 
    The final publication list of the department results from 
    the concatenation of the containt of all the existing sheets.  

    Args:
        dpt_label (str): Label of the department.
        in_file_base (str): Base of OTPs files names.
        in_path (path): Full path to folder of files where OTPs \
        have been attributed.
    Returns:
        (dataframe): The concatenated publications list with OTPs.        
    """
    otp_file_name_dpt = in_file_base + '_' + dpt_label
    otp_file_name_dpt_ok = otp_file_name_dpt + '_ok'
    dpt_otp_path = in_path / Path(otp_file_name_dpt_ok + '.xlsx')
    if not os.path.exists(dpt_otp_path):
        dpt_otp_path = in_path / Path(otp_file_name_dpt + '.xlsx')
    dpt_otp_dict = pd.read_excel(dpt_otp_path, sheet_name=None)
    dpt_otp_df = pd.DataFrame()
    for _, lab_df in dpt_otp_dict.items():
        dpt_otp_df = concat_dfs([dpt_otp_df, lab_df])
    return dpt_otp_df


def _concat_dept_otps_dfs(org_tup, in_file_base, in_path):
    """Concatenates the publications list of the Institute departments 
    after getting them through the `_set_dpt_otp_df` internal function.

    Args:
        org_tup (tup): Contains Institute parameters.
        in_file_base (str): Base of OTPs files names.
        in_path (path): Full path to folder of files where OTPs \
        have been attributed.
    Returns:
        (dataframe): The concatenated publications list with OTPs.        
    """
    # Setting institute parameters
    dpt_label_dict = org_tup[1]
    dpt_label_list = list(dpt_label_dict.keys())

    # Concatenating publications list with OTPs of the Institute departments
    otp_df_init_status = True
    for dpt_label in dpt_label_list:
        # Getting department publications list with OTPs
        dpt_otp_df = _set_dpt_otp_df(dpt_label, in_file_base, in_path)

        # Appending department publications list with OTPs
        # to the full publication list to be returned
        if otp_df_init_status:
            otp_df = dpt_otp_df.copy()
            otp_df_init_status = False
        else:
            otp_df = concat_dfs([otp_df, dpt_otp_df])
    return otp_df


def built_final_pub_list(institute, org_tup, bibliometer_path, datatype,
                         in_path, out_path, in_file_base, corpus_year):
    """Builds the dataframe of the publications final list
    of the 'corpus_year' corpus.

    This is done through the following steps:

    1. A 'consolidate_pub_list_df' dataframe is built through \
    the concatenation of the dataframes got from the files of \
    OTPs attribution to publications of each of the Institute \
    departments through the `_concat_dept_otps_dfs` internal function.
    2. Meanwhile, the set OTPS are saved through the `save_otps` \
    function imported from `bmfuncts.use_pub_attributes` module. 
    3. The publications attributed with 'INVALIDE' OTP value, \
    (imported from `bmfuncts.institute_globals` module) are dropped \
    in the 'consolidate_pub_list_df' dataframe and kept in \
    the 'invalids_df' dedicated dataframe.
    4. These two dataframes are then saved respectively as EXCEL file \
    and openpyxl file through the `format_page` function imported \
    from `bmfuncts.format_files` module after setting the attrubutes \
    keys list through the `set_base_keys_list` function imported \
    from the same module.
    5. The file saved from the 'consolidate_pub_list_df' dataframe \
    is added with impact factors values through the `add_if` function \
    of the present module.
    6. This dataframe is split by documents type through the \
    `split_pub_list_by_doc_type` function of the present module.
    7. A copy of all the created files (including hash-IDs) is made \
    in a folder specific to the combination type of data specified \
    by 'datatype' arg through the `save_final_results` function \
    imported from the `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        in_path (path): Full path to folder of files where OTPs \
        have been attributed.
        out_path (path): Full path to folder where file of publications \
        final list and associated files are saved.
        in_file_base (str): Base of OTPs files names.
        corpus_year (str): 4 digits year of the corpus.
    Returns :
        (tup): (end message recalling the full path to the saved file \
        of the publication final list, split ratio in % of the publications \
        final list, completion status of the impact-factors database).
    """

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    final_col_list = list(final_col_dic.values())

    # Setting useful aliases
    pub_list_filename_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    missing_if_filename_base_alias = pg.ARCHI_IF["missing_if_base"]
    missing_issn_filename_base_alias = pg.ARCHI_IF["missing_issn_base"]
    invalid_pub_filename_base_alias = pg.ARCHI_YEAR["invalid file name base"]
    pub_id_alias = final_col_dic['pub_id']
    otp_alias = final_col_dic['otp'] # Choix de l'OTP
    otp_col_new_alias = pg.COL_NAMES_BONUS['final OTP'] # OTP

    # Setting useful paths
    pub_list_file_path = out_path / Path(pub_list_filename_base_alias
                                         + " " + corpus_year + ".xlsx")
    missing_if_path = out_path / Path(corpus_year + missing_if_filename_base_alias)
    missing_issn_path = out_path / Path(corpus_year + missing_issn_filename_base_alias)
    invalids_file_path = out_path / Path(invalid_pub_filename_base_alias
                                        + " " + corpus_year + ".xlsx")

    # Getting dept OTPs df and concatenating them
    otp_df = _concat_dept_otps_dfs(org_tup, in_file_base, in_path)

    # Deduplicating rows on Pub_id
    otp_df = otp_df.drop_duplicates(subset=[pub_id_alias])

    # Selecting useful columns using final_col_list
    consolidate_pub_list_df = otp_df[final_col_list].copy()

    # Saving df to EXCEL file
    consolidate_pub_list_df.to_excel(pub_list_file_path, index=False)

    # Saving set OTPs
    otp_message = save_otps(institute, org_tup, bibliometer_path, corpus_year)

    # Setting pub ID as index for unique identification of rows
    consolidate_pub_list_df = consolidate_pub_list_df.set_index(pub_id_alias)

    # Droping invalid publications by pub Id as index
    invalids_idx_list = consolidate_pub_list_df[consolidate_pub_list_df[otp_alias]\
                                                !=ig.INVALIDE].index
    invalids_df = consolidate_pub_list_df.drop(index=invalids_idx_list)
    valids_idx_list = consolidate_pub_list_df[consolidate_pub_list_df[otp_alias]\
                                                         ==ig.INVALIDE].index
    consolidate_pub_list_df = consolidate_pub_list_df.drop(index=valids_idx_list)

    # Resetting pub ID as a standard column
    consolidate_pub_list_df = consolidate_pub_list_df.reset_index()
    invalids_df = invalids_df.reset_index()

    # Re_saving df to EXCEL file
    consolidate_pub_list_df.to_excel(pub_list_file_path, index=False)

    # Formatting and saving 'invalids_df' as openpyxl file
    # at full path 'invalids_file_path'
    invalids_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)
    invalids_df = invalids_df.rename(columns={otp_alias: otp_col_new_alias})
    wb, _ = format_page(invalids_df, invalids_df_title,
                        attr_keys_list=format_cols_list)
    wb.save(invalids_file_path)

    # Adding Impact Factors and saving new consolidate_pub_list_df
    # this also for saving results files to complete IFs database
    paths_tup = (pub_list_file_path, pub_list_file_path,
                 missing_if_path, missing_issn_path)
    _, if_database_complete = add_if(institute, org_tup, bibliometer_path,
                                     paths_tup, corpus_year)

    # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
    split_ratio = split_pub_list_by_doc_type(institute, org_tup,
                                             bibliometer_path, corpus_year)

    # Saving pub list and hash-IDs as final results
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["pub_lists"] = True
    results_to_save_dict["hash_ids"] = True
    results_to_save_dict["submit"] = True
    if_analysis_name = None
    final_save_message = save_final_results(institute, org_tup, bibliometer_path,
                                            datatype, corpus_year, if_analysis_name,
                                            results_to_save_dict, verbose=False)

    end_message  = (f"\n{otp_message}"
                    f"\nOTPs identification integrated in file: \n  '{pub_list_file_path}'"
                    f"\n\nPublications list for year {corpus_year} "
                    f"has been {split_ratio} % split "
                    "in several files by group of document types. \n"
                    f"{final_save_message}")

    return end_message, split_ratio, if_database_complete


def concatenate_pub_lists(institute, org_tup, bibliometer_path, years_list):
    """Builds the concatenated dataframe of the publications lists 
    of the corpuses listed in 'years_list'.

    The dataframe is saved through the `format_page` function 
    imported from `bmfuncts.format_files` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        years_list (list): List of 4 digits years of the available \
        publications lists.
    Returns :
        (str): End message recalling folder and file name where file is saved.
    """

    # Setting useful aliases
    pub_list_path_alias = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    bdd_multi_annuelle_folder_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    bdd_multi_annuelle_file_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["concat file name base"]

    # Building the concatenated dataframe of available publications lists
    concat_df = pd.DataFrame()
    available_liste_conso = ""
    for year in years_list:
        try:
            corpus_folder_path = bibliometer_path / Path(year)
            pub_list_folder_path = corpus_folder_path / Path(pub_list_path_alias)
            pub_list_file_name = f"{pub_list_file_base_alias} {year}.xlsx"
            pub_list_path = pub_list_folder_path / Path(pub_list_file_name)
            inter_df = pd.read_excel(pub_list_path)
            concat_df = concat_dfs([concat_df, inter_df])
            available_liste_conso += f" {year}"

        except FileNotFoundError:
            pass

    # Formatting and saving the concatenated dataframe in an EXCEL file
    date = str(datetime.now())[:16].replace(':', 'h')
    out_file = (f"{date} {bdd_multi_annuelle_file_alias} "
                f"{os.getlogin()}_{available_liste_conso}.xlsx")
    out_path = bibliometer_path / Path(bdd_multi_annuelle_folder_alias)
    out_file_path = out_path / Path(out_file)
    concat_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)
    wb, _ = format_page(concat_df, concat_df_title,
                        attr_keys_list=format_cols_list)
    wb.save(out_file_path)

    end_message  = f"Concatenation of consolidated pub lists saved in folder: \n  '{out_path}'"
    end_message += f"\n\n under filename: \n  '{out_file}'."
    return end_message
