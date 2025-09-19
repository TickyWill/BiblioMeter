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
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
from bmfuncts.add_ifs import add_if
from bmfuncts.format_files import format_page
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.use_otps import save_otps
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import reorder_df


def _set_year_file_paths(wf_path, file_folder, file_base, corpus_year,
                         add_key=None):
    """Sets useful full paths to a publications list file for a corpus year.

    Args:
        wf_path (path): Full path to working folder.
        file_folder (str): The folder name where the file is located.
        file_base (str) : The file name base for building the name \
        of the file of which the paths are sets.
        corpus_year (str): Corpus year defined by 4 digits.
        add_key (str): The optional string to add to the file name \
        base (default: None).
    Returns:
        (tup): (The full path (path) to the folder of the publications list, \
        The full path (path) the publications-list file).
    """
    corpus_folder_path = wf_path / Path(corpus_year)
    file_folder_path = corpus_folder_path / Path(file_folder)
    year_file_base = f"{file_base} {corpus_year}"
    if add_key:
        year_file_base = f"{year_file_base}_{add_key}"
    file_name = f"{year_file_base}.xlsx"
    file_path = file_folder_path / Path(file_name)
    return file_folder_path, file_path


def _set_split_pub_files_params(wf_path, corpus_year):
    """Sets a dict of useful full paths for spliting the consolidated 
    publications list and the full path to this list.

    The full paths are built through the `_set_year_file_paths` 
    internal function.
    The built dict is keyed by the splitting doctypes given by 
    the `DOCTYPE_TO_SAVE_DICT` and `OTHER_DOCTYPE` globals 
    imported from the `bmfuncts.pub_globals`module. 
    The values of the dict are the built full paths.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): Corpus year defined by 4 digits.
    Returns:
        (tup): (The full path to the file of the consolidated \
        publications list (str), The built full paths for \
        splitting this file (dict)).
    """
    # Setting useful aliases
    pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    doctype_keys_alias = bm_pg.DOCTYPE_TO_SAVE_DICT.keys()
    others_key_alias = bm_pg.OTHER_DOCTYPE

    # Setting useful folders paths dependent on year select
    _, pub_list_file_path = _set_year_file_paths(wf_path, pub_list_folder_alias,
                                                 pub_list_file_base_alias, corpus_year)

    all_doctypes_list = list(doctype_keys_alias) + [others_key_alias]
    doctype_split_paths = {}
    for key in all_doctypes_list:
        _, doctype_split_paths[key] = _set_year_file_paths(wf_path, pub_list_folder_alias,
                                                           pub_list_file_base_alias,
                                                           corpus_year, add_key=key)
    return pub_list_file_path, doctype_split_paths


def split_pub_list_by_doc_type(sub_params_list):
    """Splits the dataframe of the publications final list into dataframes 
    corresponding to different documents types.

    This is done for the 'corpus_year' corpus. 
    These dataframes are saved through the `format_page` function 
    imported from `bmfuncts.format_files` module. 
    The useful full paths are set through the `_set_split_pub_files_params` 
    internal function.

    Args:
        sub_params_list (list):  The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path) and the 4 digits year of the corpus (str).
    Returns:
        (tup): (split ratio in % of the publications final list (int), 
        consolidated publications number (int)).
    """
    # Setting parameters values from params_list
    institute, org_tup, wf_path, corpus_year = sub_params_list

    # Setting useful parameters for use of 'format_page' function
    common_df_title = bm_pg.DF_TITLES_LIST[0]

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    pub_id_col = final_col_dic['pub_id']
    doc_type_col = final_col_dic['doc_type']

    # Setting useful paths
    return_tup = _set_split_pub_files_params(wf_path, corpus_year)
    pub_list_file_path, doctype_split_paths = return_tup

    full_pub_list_df = pd.read_excel(pub_list_file_path)
    other_dg = full_pub_list_df.copy()
    pub_nb = len(full_pub_list_df)
    key_pub_nb = 0
    for key, doctype_list in bm_pg.DOCTYPE_TO_SAVE_DICT.items():
        doctype_list = [x.upper() for x in doctype_list]
        key_dg = pd.DataFrame(columns=full_pub_list_df.columns)

        for doc_type, dg in full_pub_list_df.groupby(doc_type_col):
            if doc_type.upper() in doctype_list:
                key_dg = concat_dfs([key_dg, dg])
                other_dg = other_dg.drop(dg.index)

        key_pub_nb += len(key_dg)

        key_dg = key_dg.sort_values(by=[pub_id_col])
        wb, ws = format_page(key_dg, common_df_title)
        ws.title = key + " " + corpus_year
        wb.save(doctype_split_paths[key])

    other_dg = other_dg.sort_values(by=[pub_id_col])
    wb, ws = format_page(other_dg, common_df_title)
    ws.title = "Others " + corpus_year
    wb.save(doctype_split_paths[bm_pg.OTHER_DOCTYPE])

    split_ratio = 100
    if pub_nb!=0:
        split_ratio = round(key_pub_nb / pub_nb*100)
    return split_ratio, pub_nb


def _set_build_pub_files_params(wf_path, corpus_year):
    """Sets a list of useful full paths for building the consolidated 
    publications list.

    The list is composed of:
    - the path to the folder of files where OTPs have been attributed \
    by the user; \
    - the path to the file of the publications list; \
    - the path to the file of the invalid publications list; \
    - the path to the file of missing Ifs in the publications list; \
    - the path to the file of missing ISSNs in the publications list.
    When needed, the full paths are built through the `_set_year_file_paths` 
    internal function.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): Corpus year defined by 4 digits.
    Returns:
        (tup): (Base of OTPs files names (str), The full paths list (list).
    """
    # Setting useful aliases
    pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    invalid_pub_file_base_alias = bm_pg.ARCHI_YEAR["invalid file name base"]
    missing_if_base_alias = bm_pg.ARCHI_IF["missing_if_base"]
    missing_issn_base_alias = bm_pg.ARCHI_IF["missing_issn_base"]

    # Setting useful files names dependent on year select
    invalids_file = f'{invalid_pub_file_base_alias} {corpus_year}.xlsx'
    missing_if_file = f'{corpus_year}{missing_if_base_alias}'
    missing_issn_file = f'{corpus_year}{missing_issn_base_alias}'

    # Setting useful folders and files paths dependent on corpus year
    pub_list_paths_tup = _set_year_file_paths(wf_path, pub_list_folder_alias,
                                              pub_list_file_base_alias, corpus_year)
    pub_list_folder_path, pub_list_file_path = pub_list_paths_tup
    invalids_file_path = pub_list_folder_path / Path(invalids_file)
    missing_if_path = pub_list_folder_path / Path(missing_if_file)
    missing_issn_path = pub_list_folder_path / Path(missing_issn_file)

    paths_list = [pub_list_file_path, invalids_file_path,
                  missing_if_path, missing_issn_path]

    return paths_list


def built_final_pub_list(params_list):
    """Builds the dataframe of the publications final list
    of the 'corpus_year' corpus.

    This is done through the following steps:

    1. A 'consolidate_pub_list_df' dataframe is built through \
    the concatenation of the dataframes got from the files of \
    OTPs attribution to publications of each of the Institute \
    departments and the set OTPS are saved through the `save_otps` \
    function imported from the `bmfuncts.use_otps` module. 
    2. The publications attributed with 'INVALIDE' OTP value, \
    (imported from `bmfuncts.institute_globals` module) are dropped \
    in the 'consolidate_pub_list_df' dataframe and kept in \
    the 'invalids_df' dedicated dataframe.
    3. These two dataframes are then saved respectively as EXCEL file \
    and openpyxl file through the `format_page` function imported \
    from `bmfuncts.format_files` module.
    4. The file saved from the 'consolidate_pub_list_df' dataframe \
    is added with impact factors values through the `add_if` function \
    of the present module.
    5. This dataframe is split by documents type through the \
    `split_pub_list_by_doc_type` function of the present module.
    6. A copy of all the created files (including hash-IDs) is made \
    in a folder specific to the combination type of data specified \
    by 'datatype' parameter through the `save_final_results` function \
    imported from the `bmfuncts.save_final_results` module.

    The useful full paths are set through the `_set_build_pub_files_params` 
    internal function.

    Args:
        params_list (list):  The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path), the data combination type \
        of corpuses databases (str) and the 4 digits year of the corpus (str).
    Returns :
        (tup): (end message recalling the full path to the saved file \
        of the publication final list, split ratio in % of the publications \
        final list, completion status of the impact-factors database).
    """
    # Setting parameters values from params_list
    institute, org_tup, wf_path, datatype, corpus_year = params_list
    sub_params_list = [institute, org_tup, wf_path, corpus_year]

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    pub_id_col = final_col_dic['pub_id']
    otp_col = final_col_dic['otp'] # Choix de l'OTP
    otp_col_new_alias = bm_pg.COL_NAMES_BONUS['final OTP'] # OTP

    # Setting files params
    paths_list = _set_build_pub_files_params(wf_path, corpus_year)
    (pub_list_file_path, invalids_file_path,
     missing_if_path, missing_issn_path) = paths_list

    # Saving the OTPs set by user
    return_tup = save_otps(sub_params_list)
    otp_message, consolidate_pub_list_df = return_tup

    # Setting pub ID as index for unique identification of rows
    consolidate_pub_list_df = consolidate_pub_list_df.set_index(pub_id_col)

    # Droping invalid publications by pub Id as index
    invalids_idx_list = consolidate_pub_list_df[consolidate_pub_list_df[otp_col]\
                                                !=bm_ig.INVALIDE].index
    invalids_df = consolidate_pub_list_df.drop(index=invalids_idx_list)
    valids_idx_list = consolidate_pub_list_df[consolidate_pub_list_df[otp_col]\
                                                         ==bm_ig.INVALIDE].index
    consolidate_pub_list_df = consolidate_pub_list_df.drop(index=valids_idx_list)

    # Resetting pub ID as a standard column with position after Hash-ID
    col_dict = {pub_id_col: 1}
    consolidate_pub_list_df = reorder_df(consolidate_pub_list_df, col_dict)
    invalids_df = reorder_df(invalids_df, col_dict)

    # Saving df to EXCEL file
    consolidate_pub_list_df.to_excel(pub_list_file_path, index=False)

    # Formatting and saving 'invalids_df' as openpyxl file
    # at full path 'invalids_file_path'
    invalids_df_title = bm_pg.DF_TITLES_LIST[17]
    invalids_df = invalids_df.rename(columns={otp_col: otp_col_new_alias})
    wb, ws = format_page(invalids_df, invalids_df_title)
    ws.title = "Invalides " +  corpus_year
    wb.save(invalids_file_path)

    # Adding Impact Factors and saving new consolidate_pub_list_df
    # this also for saving results files to complete IFs database
    add_if_paths_list = [pub_list_file_path, pub_list_file_path,
                         missing_issn_path, missing_if_path]
    _, if_database_complete = add_if(sub_params_list, add_if_paths_list)

    # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
    split_ratio, pub_nb = split_pub_list_by_doc_type(sub_params_list)

    # Saving pub list and hash-IDs as final results
    status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
    keys_list = ["pub_lists", "hash_ids", "submit", "homonyms"]
    for key in keys_list:
        results_to_save_dict[key] = True
    if_analysis_name = None
    final_save_message = save_final_results(institute, org_tup, wf_path,
                                            datatype, corpus_year, if_analysis_name,
                                            results_to_save_dict, verbose=False)

    end_message  = (f"\n{otp_message}"
                    f"\nOTPs identification integrated in file: \n  '{pub_list_file_path}'"
                    f"\n\nPublications list for year {corpus_year} "
                    f"has been {split_ratio} % split "
                    "in several files by group of document types. \n"
                    f"{final_save_message}")

    return end_message, pub_nb, split_ratio, if_database_complete


def _set_concat_pub_list_path(wf_path, available_pub_lists):
    """Sets the full path to the file of the concatenation 
    of the consolidated publications list.

    Args:
        wf_path (path): Full path to working folder.
        available_pub_lists (list): The list of the available \
        corpus years (4 digits string) in the working folder.
    Returns:
        (tup): (Base of OTPs files names (str), The full paths list (list).
    """
    multi_year_folder_alias = bm_pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    multi_year_base_alias = bm_pg.ARCHI_BDD_MULTI_ANNUELLE["concat file name base"]
    date = str(datetime.now())[:16].replace(':', 'h')
    multi_year_file = (f"{date} {multi_year_base_alias} "
                       f"{os.getlogin()}_{available_pub_lists}.xlsx")
    multi_year_folder_path = wf_path / Path(multi_year_folder_alias)
    multi_year_file_path = multi_year_folder_path / Path(multi_year_file)
    return multi_year_file_path


def concatenate_pub_lists(wf_path, years_list):
    """Builds the concatenated publications list of the corpuses 
    listed in 'years_list'.

    The full paths of the consolidated publications lists are set
    through the `_set_year_file_paths` internal function.
    The built data are saved through the `format_page` function 
    imported from `bmfuncts.format_files` module. 
    The full path to save the data is set through 
    the `_set_concat_pub_list_path` internal function.

    Args:
        wf_path (path): Full path to working folder.
        years_list (list): List of 4 digits years of the available \
        publications lists.
    Returns :
        (str): End message recalling folder and file name \
        where the file is saved.
    """
    # Setting useful aliases
    pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]

    # Building the concatenated dataframe of available publications lists
    concat_df = pd.DataFrame()
    available_pub_lists = ""
    for year in years_list:
        try:
            _, pub_list_path = _set_year_file_paths(wf_path, pub_list_folder_alias,
                                                    pub_list_file_base_alias, year)
            inter_df = pd.read_excel(pub_list_path)
            concat_df = concat_dfs([concat_df, inter_df])
            available_pub_lists += f" {year}"
        except FileNotFoundError:
            pass

    # Formatting and saving the concatenated dataframe in an EXCEL file
    multi_year_file_path = _set_concat_pub_list_path(wf_path, available_pub_lists)
    concat_df_title = bm_pg.DF_TITLES_LIST[0]
    wb, ws = format_page(concat_df, concat_df_title)
    ws.title = "Publications de " + available_pub_lists
    wb.save(multi_year_file_path)

    end_message  = ("Concatenation of consolidated pub lists under: "
                    f"\n\n  '{multi_year_file_path}'")
    return end_message
