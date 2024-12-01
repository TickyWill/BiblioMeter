"""Module of functions for using publications attributes
such as homonyms and OTPs.

"""

__all__ = ['add_otp',
           'save_otps',
           'set_saved_otps',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl.worksheet.datavalidation import DataValidation \
    as openpyxl_DataValidation
from openpyxl.utils import get_column_letter \
    as openpyxl_get_column_letter
from openpyxl.styles import PatternFill as openpyxl_PatternFill

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.institute_globals as ig
import bmfuncts.pub_globals as pg
from bmfuncts.format_files import align_cell
from bmfuncts.format_files import color_row
from bmfuncts.format_files import format_heading
from bmfuncts.format_files import format_page
from bmfuncts.format_files import set_base_keys_list
from bmfuncts.format_files import set_df_attributes
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.rename_cols import set_otp_col_names


def _save_dpt_otp_file(institute, org_tup, dpt, dpt_df, dpt_otp_list,
                       otp_alias, excel_dpt_path, otp_col_list):
    """Creates the file for setting OTP attribute of publications by the user 
    for the Institute department labelled 'dpt'.

    A new column named 'otp_alias' is added to the dataframe 'dpt_df'. 
    A list data validation rules is added to each cells of the column 
    'otp_alias' based on the list of OTPs of the department given 
    by 'dpt_otp_list' list. 
    The dataframe columns are renamed using 'otp_col_list'. 
    Then the dataframe is saved as a formatted Excel file pointed 
    by 'excel_dpt_path' path through the `ormat_page` function 
    imported from `bmfuncts.format_files` module.

    Arg:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        dpt (str): Institute department.
        dpt_df (dataframe): The publications-list dataframe of the 'dpt' department.
        dpt_otp_list (list): List of Institute departments (str).
        otp_alias (str): OTPs column name.
        excel_dpt_path (path): Full path to the file for setting publication OTP.  
        otp_col_list (list): Column names for rename of columns of the file created \
        for setting publications OTP.
    """

    # Building validation list of OTPs for 'dpt' department
    validation_list = '"'+','.join(dpt_otp_list) + '"'
    data_val = openpyxl_DataValidation(type = "list",
                                       formula1 = validation_list,
                                       showErrorMessage = False)

    # Adding a column containing OTPs of 'dpt' department
    dpt_df[otp_alias] = validation_list

    # Renaming the columns
    dpt_df = dpt_df.reindex(columns=otp_col_list)

    # Formatting the EXCEL file
    cols_list = set_base_keys_list(institute, org_tup)
    dpt_df_title = pg.DF_TITLES_LIST[2]
    wb, ws = format_page(dpt_df, dpt_df_title, attr_keys_list=cols_list,
                         wb=None, header=True, cell_colors=None)
    ws.title = pg.OTP_SHEET_NAME_BASE + " " +  dpt

    # Setting num of first col and first row in EXCEL files
    excel_first_col_num = 1
    excel_first_row_num = 2

    # Getting the column letter for the OTPs column
    otp_alias_df_index = list(dpt_df.columns).index(otp_alias)
    otp_alias_excel_index = otp_alias_df_index + excel_first_col_num
    otp_alias_column_letter = openpyxl_get_column_letter(otp_alias_excel_index)

    # Activating the validation data list in all cells of the OTPs column
    if len(dpt_df):
        # Adding a validation data list
        ws.add_data_validation(data_val)
        for df_index_row in range(len(dpt_df)):
            otp_cell_alias = otp_alias_column_letter + str(df_index_row + excel_first_row_num)
            data_val.add(ws[otp_cell_alias])

    wb.save(excel_dpt_path)


def _add_authors_name_list(institute, org_tup, in_path, out_path):
    """Adds two columns to the dataframe got from the Excel file pointed by 'in_path'.

    The columns contain respectively the full name of each author as "NAME, Firstname" 
    and the institute co-authors list with attributes of each author in a string as follows:

        - "NAME1, Firstame1 (matricule,job type,department affiliation, \
        service affiliation,laboratoire affiliation);
        - NAME2, Firstame2 (matricule,job type,department affiliation, \
        service affiliation,laboratoire affiliation);
        - ...".

    Args:
        institute (str): The Intitute name.
        org_tup (tup): Contains Institute parameters.
        in_path (path): Fullpath of the excel file of the publications list \
        with a row per Institute author and their attributes columns.
        out_path (path): Fullpath of the processed dataframe as an Excel file \
        saved after going through its treatment.
    Returns:
        (str): End message recalling out_path.
    """

    # Internal functions
    def _get_dpt_key(dpt_raw):
        return_key = None
        for key, values in dpt_label_dict.items():
            if dpt_raw in values:
                return_key = key
        return return_key


    # Setting institute parameters
    dpt_label_dict = org_tup[1]

    # Setting useful column names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    bm_col_rename_dic = col_rename_tup[2]

    # Setting useful aliases
    pub_id_alias         = bm_col_rename_dic[bp.COL_NAMES['pub_id']]
    idx_authors_alias    = bm_col_rename_dic[bp.COL_NAMES['authors'][1]]
    nom_alias            = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['name']]
    prenom_alias         = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['first_name']]
    matricule_alias      = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['matricule']]
    full_name_alias      = bm_col_rename_dic[pg.COL_NAMES_BONUS['nom prénom'] + institute]
    author_type_alias    = bm_col_rename_dic[pg.COL_NAMES_BONUS['author_type']]
    full_name_list_alias = bm_col_rename_dic[pg.COL_NAMES_BONUS['nom prénom liste'] + institute]
    dept_alias           = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['dpt']]
    serv_alias           = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['serv']]
    lab_alias            = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['lab']]

    # Reading the excel file
    df_in = pd.read_excel(in_path)

    # Adding the column 'full_name_alias' that will be used to create the authors fullname list
    df_in[prenom_alias]    = df_in[prenom_alias].apply(lambda x: x.capitalize())
    df_in[full_name_alias] = df_in[nom_alias] + ', ' + df_in[prenom_alias]

    df_out = pd.DataFrame()
    for _, pub_id_df in df_in.groupby(pub_id_alias):

        authors_tup_list = sorted(list(set(zip(pub_id_df[idx_authors_alias],
                                               pub_id_df[full_name_alias],
                                               pub_id_df[matricule_alias],
                                               pub_id_df[author_type_alias],
                                               pub_id_df[dept_alias],
                                               pub_id_df[serv_alias],
                                               pub_id_df[lab_alias]))))

        authors_str_list = [(f'{x[1]} ({x[2]},'
                             f'{x[3]},{_get_dpt_key(x[4])},{x[5]},{x[6]})')
                            for x in authors_tup_list]
        authors_full_str = "; ".join(authors_str_list)
        pub_id_df[full_name_list_alias] = authors_full_str
        df_out = pd.concat([df_out, pub_id_df])

    # Saving 'df_out' in an excel file 'out_path'
    df_out.to_excel(out_path, index = False)

    end_message = f"Column with co-authors list is added to the file: \n  '{out_path}'"
    return end_message


def add_otp(institute, org_tup, in_path, out_path, out_file_base):
    """Creates the files for setting OTP attribute of publications by the user 
    for the Institute departments.

    First, useful columns are added to the dataframe got from the Excel file 
    where homonyms have been solved by the user and pointed by 'in_path' path 
    through the `_add_authors_name_list` internal function. 
    Then, for each department, a sub_dataframe is extracted selecting rows 
    of publications where at least one author is affiliated to the department. 
    Each sub-dataframe is saved through the `_save_dpt_otp_file` internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        in_path (path): Full path to the file where homonyms have been solved.
        out_path (path): Full path to the files for setting OTPs attributes by the user.
        out_file_base (str): Base for building created-files names.
    Returns:
        (str): end message recalling out_path.
    """

    # Internal functions
    def _set_dpt(dpt_label_list):
        return lambda x: 1 if x in dpt_label_list else 0

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]

    # Setting useful column names
    otp_col_dic = set_otp_col_names(institute, org_tup)
    otp_col_list = list(otp_col_dic.values())

    # Setting useful aliases
    pub_id_alias     = otp_col_dic['pub_id']
    idx_author_alias = otp_col_dic['author_id']
    dpt_alias        = otp_col_dic['dpt']
    otp_alias        = otp_col_dic['otp_list']
    dpt_label_alias  = ig.DPT_LABEL_KEY
    dpt_otp_alias    = ig.DPT_OTP_KEY

    # Adding a column with a list of the authors in the file where homonymies
    # have been solved and pointed by in_path
    end_message = _add_authors_name_list(institute, org_tup, in_path, in_path)
    print('\n ',end_message)

    solved_homonymies_df = pd.read_excel(in_path)
    solved_homonymies_df.fillna('', inplace = True)

    dpt_list = list(dpt_attributs_dict.keys())

    # For each department adding a column containing 1 or 0
    # depending on if the author belongs or not to the department
    for dpt in dpt_list:
        dpt_label_list = dpt_attributs_dict[dpt][dpt_label_alias]
        solved_homonymies_df[dpt] = solved_homonymies_df[dpt_alias]
        solved_homonymies_df[dpt] = solved_homonymies_df[dpt].apply(_set_dpt(dpt_label_list))

    # Building 'df_out' out of 'solved_homonymies_df' with a row per pub_id
    # 1 or 0 is assigned to each department column depending
    # on if at least one co-author is a member of this department,
    # the detailed information is related to the first author only
    df_out = pd.DataFrame()
    for _, dg in solved_homonymies_df.groupby(pub_id_alias):
        dg = dg.sort_values(by = [idx_author_alias])
        for dpt in dpt_list:
            x = dg[dpt].any().astype(int)
            dg[dpt] = x
        df_out = pd.concat([df_out, dg.iloc[:1]])

    # Removing possible spaces in dept name
    df_out[dpt_alias] = df_out[dpt_alias].apply(lambda x: x.strip())

    # Configuring an Excel file per department with the list of OTPs
    for dpt in sorted(dpt_list):
        # Setting df_dpt with only pub_ids for which the first author
        # is from the 'dpt' department
        filtre_dpt = False
        for dpt_value in dpt_attributs_dict[dpt][dpt_label_alias]:
            filtre_dpt = filtre_dpt | (df_out[dpt_alias] == dpt_value)
        df_dpt = df_out[filtre_dpt].copy()

        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = dpt_attributs_dict[dpt][dpt_otp_alias]

        # Setting the full path of the EXCEl file for the 'dpt' department
        otp_file_name_dpt = f'{out_file_base}_{dpt}.xlsx'
        excel_dpt_path    = out_path / Path(otp_file_name_dpt)

        # Adding a column with validation list for OTPs and saving the file
        _save_dpt_otp_file(institute, org_tup, dpt, df_dpt, dpt_otp_list,
                           otp_alias, excel_dpt_path, otp_col_list)

    end_message  = ("Files for setting publication OTPs per department "
                    f"saved in folder: \n  '{out_path}'")
    return end_message


def save_otps(institute, org_tup, bibliometer_path, corpus_year):
    """Saves the history of the attributed OTPs by the user.

    First, builds the dataframe to save with 2 sheets:

    - A sheet which name is given by 'SHEET_SAVE_OTP' global at key 'hash_OTP' \
    with the following columns:

        - Hash-ID of the publication for which OTPs have been attributed. 
        - The OTPs value attributed.

    - A sheet which name is given by 'SHEET_SAVE_OTP' global at key 'doi_OTP' \
    with the following columns:

        - Full name (last name + first name initials) of the first author \
        of the publication for which OTPs have been attributed.
        - DOI of the publication for which OTPs have been attributed.
        - The OTPs value attributed.

    Finally, saves the dataframe as Excel file.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (str): End message.
    """

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    all_col_rename_dic = col_rename_tup[2]

    # Setting useful folder and file aliases
    bdd_mensuelle_alias      = pg.ARCHI_YEAR["bdd mensuelle"]
    pub_list_folder_alias    = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    history_folder_alias     = pg.ARCHI_YEAR["history folder"]
    kept_otps_file_alias     = pg.ARCHI_YEAR["kept OTPs file name"]
    hash_id_file_alias       = pg.ARCHI_YEAR["hash_id file name"]
    pub_list_file_alias      = pub_list_file_base_alias + f' {corpus_year}.xlsx'

    # Setting useful column name aliases
    pub_id_alias         = all_col_rename_dic[bp.COL_NAMES['pub_id']]
    author_col_alias     = all_col_rename_dic[bp.COL_NAMES['articles'][1]]
    doi_col_alias        = all_col_rename_dic[bp.COL_NAMES['articles'][6]]
    otp_list_col_alias   = all_col_rename_dic[pg.COL_NAMES_BONUS['list OTP']]
    otp_col_alias        = pg.COL_NAMES_BONUS['final OTP']
    hash_otp_sheet_alias = pg.SHEET_SAVE_OTP['hash_OTP']
    doi_otp_sheet_alias  = pg.SHEET_SAVE_OTP['doi_OTP']

    # Setting useful paths
    corpus_year_path     = bibliometer_path / Path(corpus_year)
    bdd_mensuelle_path   = corpus_year_path / Path(bdd_mensuelle_alias)
    hash_id_file_path    = bdd_mensuelle_path / Path(hash_id_file_alias)
    pub_list_folder_path = corpus_year_path / Path(pub_list_folder_alias)
    pub_list_file_path   = pub_list_folder_path / Path(pub_list_file_alias)
    history_folder_path  = corpus_year_path / Path(history_folder_alias)
    kept_otps_file_path  = history_folder_path / Path(kept_otps_file_alias)

    # Getting the hash_id dataframe
    hash_id_df  = pd.read_excel(hash_id_file_path)

    # Getting the dataframe of consolidated pub list with OTPs
    pub_df = pd.read_excel(pub_list_file_path)

    # Building set OTPs df
    if otp_col_alias in pub_df.columns:
        otp_col = otp_col_alias
    else:
        otp_col = otp_list_col_alias
    otps_df = pub_df[[pub_id_alias, author_col_alias, doi_col_alias, otp_col]].copy()
    otps_df = otps_df.fillna(0)
    otps_df = otps_df.astype(str)
    set_otps_df = otps_df.copy()
    sep = ","
    for idx,row in otps_df.iterrows():
        if sep in row[otp_col] or row[otp_col] == "0":
            set_otps_df = set_otps_df.drop(idx)

    # Building hash_id and kept otp df
    hash_otps_history_df = pd.merge(hash_id_df,
                                    set_otps_df,
                                    how = 'inner',
                                    on = pub_id_alias)
    hash_otps_history_df.drop(columns = [pub_id_alias, author_col_alias, doi_col_alias],
                              inplace = True)
    hash_otps_history_df.rename(columns = {otp_col:otp_col_alias}, inplace = True)

    # Building DOI and kept otp df
    doi_otps_history_df = set_otps_df[[author_col_alias, doi_col_alias, otp_col]].copy()
    doi_otps_history_df.rename(columns={otp_col:otp_col_alias}, inplace=True)

    # Concatenating with the dataframes of already saved solved OTPs by hash_id and by DOI
    if kept_otps_file_path.is_file():
        existing_otps_history_dict = pd.read_excel(kept_otps_file_path, sheet_name = None)

        existing_hash_otps_history_df = existing_otps_history_dict[hash_otp_sheet_alias]
        if len(existing_hash_otps_history_df)-1:
            hash_otps_history_df = pd.concat([existing_hash_otps_history_df, hash_otps_history_df])
        hash_otps_history_df = hash_otps_history_df.astype('str')
        hash_otps_history_df.drop_duplicates(inplace=True)

        existing_doi_otps_history_df = existing_otps_history_dict[doi_otp_sheet_alias]
        if len(existing_doi_otps_history_df)-1:
            doi_otps_history_df = pd.concat([existing_doi_otps_history_df, doi_otps_history_df])
        doi_otps_history_df = doi_otps_history_df.astype('str')
        doi_otps_history_df.drop_duplicates(inplace=True)

    with pd.ExcelWriter(kept_otps_file_path,  # https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
                        mode='a', if_sheet_exists='replace') as writer:
        hash_otps_history_df.to_excel(writer, sheet_name=hash_otp_sheet_alias, index=False)
        doi_otps_history_df.to_excel(writer, sheet_name=doi_otp_sheet_alias, index=False)

    message = "History of kept OTPs saved"
    return message


def _get_otps_history(institute, org_tup,
                      hash_id_file_path,
                      kept_otps_file_path):
    """
    """
    # Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    all_col_rename_dic = col_rename_tup[2]

    # Setting useful column and sheet names aliases
    hash_id_col_alias = pg.COL_HASH['hash_id']
    pub_id_alias = all_col_rename_dic[bp.COL_NAMES['pub_id']]
    author_col_alias = all_col_rename_dic[bp.COL_NAMES['articles'][1]]
    doi_col_alias = all_col_rename_dic[bp.COL_NAMES['articles'][6]]
    otp_list_col_alias = all_col_rename_dic[pg.COL_NAMES_BONUS['list OTP']]
    otp_col_alias = pg.COL_NAMES_BONUS['final OTP']
    hash_otp_sheet_alias = pg.SHEET_SAVE_OTP['hash_OTP']
    doi_otp_sheet_alias = pg.SHEET_SAVE_OTP['doi_OTP']

    # Getting the hash_id dataframe
    hash_id_df = pd.read_excel(hash_id_file_path)

    # Getting the kept OTPs dataframe by hash_id
    hash_otp_history_df = pd.read_excel(kept_otps_file_path,
                                        sheet_name=hash_otp_sheet_alias)

    # Building df of pub_id and OTPs to set related to hash_id
    pub_id_otp_to_set_df = pd.merge(hash_id_df,
                                    hash_otp_history_df,
                                    how='inner',
                                    on=hash_id_col_alias)

    pub_id_otp_to_set_df = pub_id_otp_to_set_df.astype(str)
    pub_id_otp_to_set_df.drop(columns=[hash_id_col_alias], inplace=True)
    pub_id_to_check_list = [str(row[pub_id_alias]) for _,row
                            in pub_id_otp_to_set_df.iterrows()]
    otp_to_set_list = [str(row[otp_col_alias]) for _,row
                       in pub_id_otp_to_set_df.iterrows()]

    # Getting the kept OTPs dataframe by DOI and first author
    doi_otp_history_df = pd.read_excel(kept_otps_file_path,
                                       sheet_name=doi_otp_sheet_alias)
    author_to_check_list = doi_otp_history_df[author_col_alias].to_list()
    doi_to_check_list = doi_otp_history_df[doi_col_alias].to_list()
    doi_otp_to_set_list = doi_otp_history_df[otp_col_alias].to_list()

    # Setting parameters tuples to return
    lists_tup = (pub_id_to_check_list, otp_to_set_list,
                 author_to_check_list, doi_to_check_list, doi_otp_to_set_list)

    cols_tup = (hash_id_col_alias, pub_id_alias, author_col_alias,
                doi_col_alias, otp_list_col_alias, otp_col_alias)

    return lists_tup, cols_tup, doi_otp_history_df


def _use_authors_otps(dfs_tup, cols_tup, dpt_df_to_add, auth_to_check,
                      auth_otp_to_set, dpt_auth_idx_list):
    """
    """
    # Setting parameters from args
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup
    author_col = cols_tup[2]  
    otp_list_col = cols_tup[4]

    for auth_idx in dpt_auth_idx_list:
        auth_idx_to_replace_list = []
        if auth_idx in otp_to_set_dpt_df.index:
            auth_idx_to_replace_list.append(auth_idx)
            if auth_idx in otp_set_dpt_df.index:
                otp_set_dpt_df.drop(index=auth_idx, inplace=True)

            for auth_idx_to_replace in auth_idx_to_replace_list:
                dpt_df_to_add.loc[auth_idx_to_replace, otp_list_col] = auth_otp_to_set
                new_dpt_df_to_add = dpt_df_to_add[dpt_df_to_add[author_col]\
                                                  ==auth_to_check].copy()
                new_dpt_df_to_add.loc[auth_idx_to_replace, otp_list_col] = auth_otp_to_set
                otp_set_dpt_df = pd.concat([otp_set_dpt_df, new_dpt_df_to_add])
                otp_set_dpt_df.drop_duplicates(inplace=True)
                otp_to_set_dpt_df.drop(index=auth_idx_to_replace, inplace=True)
        else:
            continue
    return otp_set_dpt_df, otp_to_set_dpt_df


def _use_known_doi_otps(dfs_tup, cols_tup, dpt_df,
                        doi_to_check, doi_otp_to_set):
    """Manages case of known DOIs.
    """
    # Setting parameters from args    
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup
    doi_col = cols_tup[3]
    otp_list_col = cols_tup[4]
    otp_col = cols_tup[5]

    # Setting the DOI index in 'dpt_df' to fill with 'doi_otp_to_set' 
    # at 'otp_list_col' col 
    dept_doi_list = dpt_df[doi_col].to_list()
    dpt_doi_idx_list = [i for i,e in enumerate(dept_doi_list)
                        if e==doi_to_check]
    doi_idx = dpt_doi_idx_list[0]

    dpt_df_to_add = dpt_df[dpt_df[doi_col]==doi_to_check].copy()
    dpt_df_to_add.loc[doi_idx, otp_list_col] = doi_otp_to_set
    otp_set_dpt_df = pd.concat([otp_set_dpt_df, dpt_df_to_add])
    otp_to_set_dpt_df.drop(index=doi_idx, inplace=True)

    return otp_set_dpt_df, otp_to_set_dpt_df


def _use_unknown_doi_otps(dfs_tup, otps_history_tup, dpt_df,
                          doi_to_check):
    """Manages case of first author name of unknown DOIs.
    """
    # Setting parameters from args
    otp_to_set_dpt_df = dfs_tup[1]
    lists_tup, cols_tup, doi_otp_history_df = otps_history_tup
    author_to_check_list = lists_tup[2]
    author_col = cols_tup[2]
    doi_col = cols_tup[3]
    otp_col = cols_tup[5]

    new_otp_to_set_dpt_df = otp_to_set_dpt_df[otp_to_set_dpt_df[doi_col]\
                                              ==doi_to_check].copy()
    otp_to_set_auth_list = new_otp_to_set_dpt_df[author_col].to_list()

    new_doi_otp_history_df = doi_otp_history_df[doi_otp_history_df[doi_col]\
                                                ==doi_to_check].copy()
    author_to_check_list = new_doi_otp_history_df[author_col].to_list()
    auth_otp_to_set_list = new_doi_otp_history_df[otp_col].to_list()

    for auth_otp_idx, auth_to_check in enumerate(author_to_check_list):
        if auth_to_check in otp_to_set_auth_list:
            auth_otp_to_set = auth_otp_to_set_list[auth_otp_idx]
            dpt_df_to_add = dpt_df[dpt_df[doi_col]==doi_to_check].copy()
            dept_auth_list = dpt_df[author_col].to_list()
            dpt_auth_idx_list = [i for i,e in enumerate(dept_auth_list) \
                                 if e==auth_to_check]
            dfs_tup = _use_authors_otps(dfs_tup, cols_tup, dpt_df_to_add,
                                        auth_to_check, auth_otp_to_set,
                                        dpt_auth_idx_list)
        else:
            continue    
    return dfs_tup


def _use_hash_id_set_otps(dpt_df, otps_history_tup):
    """
    """

    # Setting parameters from args
    lists_tup, cols_tup, _ = otps_history_tup
    pub_id_to_check_list, otp_to_set_list = lists_tup[0], lists_tup[1]
    pub_id_col, otp_list_col = cols_tup[1], cols_tup[4]
    
    # Setting columns list
    col_list = list(dpt_df.columns)

    # Setting the pub-id list for department dpt
    dept_pub_id_list = dpt_df[pub_id_col].to_list()

    # Building the 'otp_set_dpt_df' dataframe of publication with OTP set
    otp_set_dpt_df = pd.DataFrame(columns=col_list)

    # Building the 'otp_to_set_dpt_df' dataframe of publication
    # with OTP still to be defined
    otp_to_set_dpt_df = dpt_df.copy()
    otp_to_set_dpt_df.drop(columns=[otp_list_col], inplace=True)

    for otp_idx, pub_id_to_check in enumerate(pub_id_to_check_list):
        if pub_id_to_check in dept_pub_id_list:
            otp_to_set = otp_to_set_list[otp_idx]
            pub_id_idx = [i for i,e in enumerate(dept_pub_id_list)
                          if e==pub_id_to_check][0]
            dpt_df.loc[pub_id_idx, otp_list_col] = otp_to_set
            dpt_pub_id_to_check_df = dpt_df[dpt_df[pub_id_col]==pub_id_to_check]
            otp_set_dpt_df = pd.concat([otp_set_dpt_df, dpt_pub_id_to_check_df])
            otp_to_set_dpt_df.drop(index=pub_id_idx, inplace=True)
        else:
            continue
    return otp_set_dpt_df, otp_to_set_dpt_df


def _use_doi_set_otps(dpt_df, otps_history_tup, dfs_tup):
    """
    """
    # Setting parameters from args
    lists_tup, cols_tup, _ = otps_history_tup
    doi_to_check_list = lists_tup[3]    
    doi_otp_to_set_list = lists_tup[4]
    doi_col = cols_tup[3]
    otp_to_set_dpt_df = dfs_tup[1]

    # Setting the DOIs list of otp_to_set_dpt_df
    otp_to_set_doi_list = otp_to_set_dpt_df[doi_col].to_list()

    for otp_idx, doi_to_check in enumerate(doi_to_check_list):
        if doi_to_check in otp_to_set_doi_list:
            if doi_to_check!=bp.UNKNOWN:
                # Case of known DOIs
                doi_otp_to_set = doi_otp_to_set_list[otp_idx]
                dfs_tup = _use_known_doi_otps(dfs_tup, cols_tup, dpt_df,
                                              doi_to_check, doi_otp_to_set)
            else:
                # Case of first author name of unknown DOIs
                dfs_tup = _use_unknown_doi_otps(dfs_tup, otps_history_tup, dpt_df,
                                                doi_to_check)
        else:
            continue
    return dfs_tup


def _re_save_dpt_otp_file(institute, org_tup, dfs_tup, cols_tup, dpt_otp_list,
                          dpt_otp_file_name_path, dpt_otp_sheet_name):
    """Rebuilds and saves the openpyxl workbook for the department labelled 'dpt'.

    A data validation list is added to the cells 'otp_cell_alias' only when 
    the OTP in not already attributed.

    The openpyxl workbook is created through the `format_page` function imported from 
    the `bmfuncts.format_files` module and is re-configured in the same way as in this 
    function after being modified and before being saved.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        dpt (str): Department of the Institute.
        otp_set_dpt_df (dataframe): Data of the already attributed OTPs for the department.
        otp_to_set_dpt_df (dataframe): Data of the OTPs still to be attributed for the department.
        dpt_otp_list (list): String containing the OTPs of the department seperated by semicolons.
        excel_dpt_path (path): Full path to where the workbook is saved. 
        otp_list_col (str): Name of the column that contains the OTPs list.
    """

    # Setting parameters from args
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup
    otp_list_col = cols_tup[4]
    
    # Setting cell colors
    cell_colors = [openpyxl_PatternFill(fgColor = pg.ROW_COLORS['odd'],
                                        fill_type = "solid"),
                   openpyxl_PatternFill(fgColor = pg.ROW_COLORS['even'],
                                        fill_type = "solid")]

    # Building validation list of OTP for the department
    validation_list = '"'+','.join(dpt_otp_list) + '"'
    data_val = openpyxl_DataValidation(type = "list",
                                       formula1 = validation_list,
                                       showErrorMessage = False)

    # Initializing new_dpt_df with the publications which otp is not yet set
    new_dpt_df = otp_to_set_dpt_df.copy()

    # Adding a column containing OTPs of the department
    new_dpt_df[otp_list_col] = validation_list

    # Creating and formatting the openpyxl workbook
    cols_list = set_base_keys_list(institute, org_tup)
    new_dpt_df_title = pg.DF_TITLES_LIST[2]
    wb, ws = format_page(new_dpt_df, new_dpt_df_title, attr_keys_list=cols_list,
                         wb=None, header=True, cell_colors=None)

    # Setting num of first col and first row in EXCEL files
    excel_first_col_num = 1
    excel_first_row_num = 2

    # Getting the column letter for the OTPs column
    otp_alias_df_index = list(new_dpt_df.columns).index(otp_list_col)
    otp_alias_excel_index = otp_alias_df_index + excel_first_col_num
    otp_alias_column_letter = openpyxl_get_column_letter(otp_alias_excel_index)

    # Activating the validation data list in the OTPs column of new_dpt_df
    dpt_df_len = len(new_dpt_df)
    if dpt_df_len:
        # Adding a validation data list
        ws.add_data_validation(data_val)
        for df_index_row in range(dpt_df_len):
            otp_cell_alias = otp_alias_column_letter + \
                             str(df_index_row + excel_first_row_num)
            data_val.add(ws[otp_cell_alias])

    # Appending rows of the publications which OTP is already set to ws
    # and coloring the rows alternatively
    if len(otp_set_dpt_df):
        # use of a continuously incremented index
        # because row index is not continuously incremented
        idx = 1 
        for _, row in otp_set_dpt_df.iterrows():
            ws.append(row.values.flatten().tolist())
            color_idx_row = dpt_df_len + idx
            ws = color_row(ws, color_idx_row, cell_colors)
            idx += 1

    # Re-shaping the alignment and the border of the columns
    df_cols_list = new_dpt_df.columns
    col_attr_dict, _, _ = set_df_attributes(new_dpt_df_title, df_cols_list, cols_list)
    ws = align_cell(ws, df_cols_list, col_attr_dict)

    # Re-shaping header
    ws = format_heading(ws, new_dpt_df_title)
            
    # Setting the worksheet label
    ws.title = dpt_otp_sheet_name

    # Saving the workbook
    wb.save(dpt_otp_file_name_path)


def _set_saved_dept_otps(institute, org_tup, otps_history_tup,
                         otp_folder_path, otp_file_base_alias):
    """Attributes the OTPs from the history of the attributed OTPs 
    before submiting to the user the file for attributing the not yet 
    attributed OTPs.

    Loops on department to:

        1. Build the dataframe with already attributed OTPs \
    and OTPs remaining to be attributed. 
        2. Save the file to be submitted to the user through the \
    `_re_save_dpt_otp_file` internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (str): End message giving the status of the OTPs attribution.
    """

    # Setting parameters from args
    cols_tup = otps_history_tup[1]

    # Setting institute parameters
    dpt_attributs_dict  = org_tup[2]

    # Setting departments list
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting the already attributed OTPs for each department
    for dpt in sorted(dpt_list):
        # Setting the full path of the EXCEl file for the 'dpt' department
        dpt_otp_file_name = f'{otp_file_base_alias}_{dpt}.xlsx'
        dpt_otp_file_name_path = otp_folder_path / Path(dpt_otp_file_name)

        # Setting the sheet name of the EXCEl file for the 'dpt' department
        dpt_otp_sheet_name = pg.OTP_SHEET_NAME_BASE + " " +  dpt

        # Getting the pub list for department dpt
        dpt_df = pd.read_excel(dpt_otp_file_name_path)

        # Using set OTPs by Hash-ID
        dfs_tup = _use_hash_id_set_otps(dpt_df, otps_history_tup)
        _, otp_to_set_dpt_df = dfs_tup

        # Si tous les OTPs non affectés compléter avec DOI_otp
        if len(otp_to_set_dpt_df):
            dfs_tup = _use_doi_set_otps(dpt_df, otps_history_tup, dfs_tup)

        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = dpt_attributs_dict[dpt][ig.DPT_OTP_KEY]

        # Resetting validation list for OTPs when not already set and saving the file
        _re_save_dpt_otp_file(institute, org_tup, dfs_tup, cols_tup, dpt_otp_list,
                              dpt_otp_file_name_path, dpt_otp_sheet_name)


def set_saved_otps(institute, org_tup, bibliometer_path, corpus_year):
    """Attributes the OTPs from the history of the attributed OTPs 
    before submiting to the user the file for attributing the not yet 
    attributed OTPs.

    Loops on department to:

        1. Build the dataframe with already attributed OTPs \
    and OTPs remaining to be attributed. 
        2. Save the file to be submitted to the user through the \
    `_re_save_dpt_otp_file` internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (str): End message giving the status of the OTPs attribution.
    """
    # Setting institute parameters
    otp_level = org_tup[11]  

    # Setting useful folder and file aliases
    bdd_mensuelle_alias  = pg.ARCHI_YEAR["bdd mensuelle"]
    otp_folder_alias     = pg.ARCHI_YEAR["OTP folder"]
    otp_file_base_alias  = pg.ARCHI_YEAR["OTP file name base"]
    history_folder_alias = pg.ARCHI_YEAR["history folder"]
    kept_otps_file_alias = pg.ARCHI_YEAR["kept OTPs file name"]
    hash_id_file_alias   = pg.ARCHI_YEAR["hash_id file name"]
    
    # Setting useful paths
    corpus_year_path    = bibliometer_path / Path(corpus_year)
    bdd_mensuelle_path  = corpus_year_path / Path(bdd_mensuelle_alias)
    hash_id_file_path   = bdd_mensuelle_path / Path(hash_id_file_alias)
    history_folder_path = corpus_year_path / Path(history_folder_alias)
    kept_otps_file_path = history_folder_path / Path(kept_otps_file_alias)
    otp_folder_path     = corpus_year_path / Path(otp_folder_alias)

    if kept_otps_file_path.is_file():
        otps_history_tup = _get_otps_history(institute, org_tup,
                                             hash_id_file_path,
                                             kept_otps_file_path)
        if otp_level=="LAB":# ! encore à modifier
            print("Not yet umpdated")
#            lab_otps_dict = set_lab_otps(institute, org_tup, bibliometer_path)
#            _set_saved_lab_otps(institute, org_tup, otp_folder_path,
#                                otp_file_base_alias, otps_history_tup,
#                                lab_otps_dict)
        else:
            _set_saved_dept_otps(institute, org_tup, otps_history_tup,
                                 otp_folder_path, otp_file_base_alias)

        message = "Already set OTPS used"
    else:
        message = "No already set OTPS available"
    return message