"""Module of functions for using publications attributes
such as homonyms and OTPs.

"""

__all__ = ['save_otps',
           'set_saved_otps',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl import Workbook as openpyxl_Workbook

# Local imports
import bmfuncts.institute_globals as ig
import bmfuncts.pub_globals as pg
from bmfuncts.add_otps import add_data_val
from bmfuncts.build_otps_info import set_lab_otps
from bmfuncts.format_files import align_cell
from bmfuncts.format_files import build_data_val
from bmfuncts.format_files import build_cell_fill_patterns
from bmfuncts.format_files import color_row
from bmfuncts.format_files import format_heading
from bmfuncts.format_files import format_page
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.format_files import get_col_letter
from bmfuncts.format_files import set_base_keys_list
from bmfuncts.format_files import set_df_attributes
from bmfuncts.rename_cols import build_col_conversion_dic


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
    bdd_mensuelle_alias = pg.ARCHI_YEAR["bdd mensuelle"]
    pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    history_folder_alias = pg.ARCHI_YEAR["history folder"]
    kept_otps_file_alias = pg.ARCHI_YEAR["kept OTPs file name"]
    hash_id_file_alias = pg.ARCHI_YEAR["hash_id file name"]
    pub_list_file_alias = pub_list_file_base_alias + f' {corpus_year}.xlsx'

    # Setting useful column name aliases
    pub_id_alias = all_col_rename_dic[bp.COL_NAMES['pub_id']]
    author_col_alias = all_col_rename_dic[bp.COL_NAMES['articles'][1]]
    doi_col_alias = all_col_rename_dic[bp.COL_NAMES['articles'][6]]
    otp_list_col_alias = all_col_rename_dic[pg.COL_NAMES_BONUS['list OTP']]
    otp_col_alias = pg.COL_NAMES_BONUS['final OTP']
    hash_otp_sheet_alias = pg.SHEET_SAVE_OTP['hash_OTP']
    doi_otp_sheet_alias = pg.SHEET_SAVE_OTP['doi_OTP']

    # Setting useful paths
    corpus_year_path = bibliometer_path / Path(corpus_year)
    bdd_mensuelle_path = corpus_year_path / Path(bdd_mensuelle_alias)
    hash_id_file_path = bdd_mensuelle_path / Path(hash_id_file_alias)
    pub_list_folder_path = corpus_year_path / Path(pub_list_folder_alias)
    pub_list_file_path = pub_list_folder_path / Path(pub_list_file_alias)
    history_folder_path = corpus_year_path / Path(history_folder_alias)
    kept_otps_file_path = history_folder_path / Path(kept_otps_file_alias)

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


def _use_hash_id_set_otps(dpt_df, otps_history_tup):
    """Uses set otps by Hash-IDs.
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
    dfs_tup = (otp_set_dpt_df, otp_to_set_dpt_df)
    return dfs_tup


def _use_known_doi_otps(dfs_tup, cols_tup, dpt_df,
                        doi_to_check, doi_otp_to_set):
    """Manages case of known DOIs.
    """
    # Setting parameters from args
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup
    doi_col = cols_tup[3]
    otp_list_col = cols_tup[4]

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
    dfs_tup = (otp_set_dpt_df, otp_to_set_dpt_df)
    return dfs_tup


def _use_authors_otps(dfs_tup, cols_tup, dpt_df_to_add,
                      auth_idx, auth_to_check, auth_otp_to_set):
    """Uses set OTPs by first-author name of unknown DOIs.
    """
    # Setting parameters from args
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup
    author_col = cols_tup[2]
    otp_list_col = cols_tup[4]

    auth_idx_to_replace_list = []
    if auth_idx in otp_to_set_dpt_df.index:
        auth_idx_to_replace_list.append(auth_idx)
        if auth_idx in otp_set_dpt_df.index:
            otp_set_dpt_df.drop(index=auth_idx, inplace=True)

        for auth_idx_to_replace in auth_idx_to_replace_list:
            dpt_df_to_add.loc[auth_idx_to_replace, otp_list_col] = auth_otp_to_set
            new_dpt_df_to_add = dpt_df_to_add[dpt_df_to_add[author_col]==auth_to_check].copy()
            new_dpt_df_to_add.loc[auth_idx_to_replace, otp_list_col] = auth_otp_to_set
            otp_set_dpt_df = pd.concat([otp_set_dpt_df, new_dpt_df_to_add])
            otp_set_dpt_df.drop_duplicates(inplace=True)
            otp_to_set_dpt_df.drop(index=auth_idx_to_replace, inplace=True)
    else:
        pass
    dfs_tup = (otp_set_dpt_df, otp_to_set_dpt_df)
    return dfs_tup


def _use_unknown_doi_otps(dfs_tup, otps_history_tup, dpt_df,
                          doi_to_check):
    """Manages case of unknown DOIs.
    """
    # Setting parameters from args
    otp_to_set_dpt_df = dfs_tup[1]
    lists_tup, cols_tup, doi_otp_history_df = otps_history_tup
    author_to_check_list = lists_tup[2]
    author_col = cols_tup[2]
    doi_col = cols_tup[3]
    otp_col = cols_tup[5]

    new_otp_to_set_dpt_df = otp_to_set_dpt_df[otp_to_set_dpt_df[doi_col]==doi_to_check].copy()
    otp_to_set_auth_list = new_otp_to_set_dpt_df[author_col].to_list()

    new_doi_otp_history_df = doi_otp_history_df[doi_otp_history_df[doi_col]==doi_to_check].copy()
    author_to_check_list = new_doi_otp_history_df[author_col].to_list()
    auth_otp_to_set_list = new_doi_otp_history_df[otp_col].to_list()

    for auth_otp_idx, auth_to_check in enumerate(author_to_check_list):
        if auth_to_check in otp_to_set_auth_list:
            auth_otp_to_set = auth_otp_to_set_list[auth_otp_idx]
            dpt_df_to_add = dpt_df[dpt_df[doi_col]==doi_to_check].copy()
            dept_auth_list = dpt_df[author_col].to_list()
            dpt_auth_idx_list = [i for i,e in enumerate(dept_auth_list) if e==auth_to_check]

            for auth_idx in dpt_auth_idx_list:
                dfs_tup = _use_authors_otps(dfs_tup, cols_tup, dpt_df_to_add,
                                            auth_idx, auth_to_check, auth_otp_to_set)
        else:
            continue
    return dfs_tup


def _use_doi_set_otps(dpt_df, otps_history_tup, dfs_tup):
    """Uses set OTPs by DOI.
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
                # Case of unknown DOIs (use of first author name)
                dfs_tup = _use_unknown_doi_otps(dfs_tup, otps_history_tup, dpt_df,
                                                doi_to_check)
        else:
            continue
    return dfs_tup


def _add_set_otp_rows(ws, otp_set_df, df_len, cell_colors):
    """Adds rows with set OTPs to the openpyxl sheet 
    and colors them alternatively.
    """
    # use of a continuously incremented index
    # because row index is not continuously incremented
    idx = 1
    for _, row in otp_set_df.iterrows():
        ws.append(row.values.flatten().tolist())
        row_color_idx = df_len + idx
        ws = color_row(ws, row_color_idx, cell_colors)
        idx += 1
    return ws


def _set_lab_otp_ws(lab, dfs_tup, lab_otp_list, wb, first, common_args_tup):
    """Builts the openpyxl sheet of a laboratory in the openpyxl workbook 
    of the department it belongs, to using set OTPs and keeping validation 
    rules for not set OTPs.
    """
    # Setting parameters from args
    otp_set_lab_df, otp_to_set_lab_df = dfs_tup
    (attr_keys_list, otp_list_col, cell_colors,
     xl_idx_base, otp_col_letter) = common_args_tup

    # Initializing new_lab_df with the publications which otp is not yet set
    new_lab_df = otp_to_set_lab_df.copy()

    # Building validation list of OTP for 'lab' laboratory
    validation_list, data_val = build_data_val(lab_otp_list)

    # Adding a column containing OTPs of 'dpt' department
    new_lab_df[otp_list_col] = validation_list

    # Formatting the openpyxl workbook
    sheet_name = lab
    new_lab_df_title = pg.DF_TITLES_LIST[2]
    wb = format_wb_sheet(sheet_name, new_lab_df,
                         new_lab_df_title, wb, first,
                         attr_keys_list=attr_keys_list)
    ws = wb.active

    # Activating the validation data list in the OTPs column of new_lab_df
    new_lab_df_len = len(new_lab_df)
    if new_lab_df_len:
        ws = add_data_val(ws, data_val, new_lab_df_len, otp_col_letter,
                          xl_idx_base)

    # Appending rows of the publications which OTP is already set to ws
    # and coloring the rows alternatively
    if len(otp_set_lab_df):
        ws = _add_set_otp_rows(ws, otp_set_lab_df, new_lab_df_len, cell_colors)

    # Re-shaping the alignment and the border of the columns
    df_cols_list = new_lab_df.columns
    col_attr_dict, _, _ = set_df_attributes(new_lab_df_title, df_cols_list,
                                            attr_keys_list)
    ws = align_cell(ws, df_cols_list, col_attr_dict, xl_idx_base)

    # Re-shaping header
    ws = format_heading(ws, new_lab_df_title)

    return wb, ws

def _re_save_labs_otp_file(institute, org_tup, dpt_pub_dict, dpt_lab_otps_dict,
                           dpt_otp_file_name_path, otps_history_tup):

    """Rebuilds and saves the openpyxl workbook for the department labelled 'dpt'.

    A data validation list is added to the cells 'otp_cell_alias' only when 
    the OTP in not already attributed.

    The openpyxl workbook is created through the `format_page` function imported from 
    the `bmfuncts.format_files` module and is re-configured in the same way as in this 
    function after being modified and before being saved.

    The columns attributes for formatting the workbook are defined through the `set_col_attr` 
    function imported from `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        dpt_pub_dict (dict): The data of the department keyed by laboratory \
        names (str) and valued by publications data (dataframe).
        dpt_lab_otps_dict (dict): The data of the department keyed \
        by laboratory names (str) and valued by OTPs lists (list). 
        dpt_otp_file_name_path (path): Full path to where the workbook is saved.
        otps_history_tup (tup): (useful lists (tup), useful column names (tup), \
        data of OTPs set by DOI (dataframe).
    """
    # Setting num of first col and first row in EXCEL files
    xl_idx_base = pg.XL_INDEX_BASE

    # Setting cell colors
    cell_colors = build_cell_fill_patterns()

    # Setting parameters from args
    cols_tup = otps_history_tup[1]

    # Setting col attributes keys
    attr_keys_list = set_base_keys_list(institute, org_tup)

    # Setting parameters from args
    otp_list_col = cols_tup[4]
    otp_col_letter = " "

    # Initialize parameters for saving results as multisheet workbook
    first = True
    wb = openpyxl_Workbook()

    for lab, lab_df in dpt_pub_dict.items():
        if first:
            # Getting the column letter for the OTPs column
            otp_col_letter = get_col_letter(lab_df, otp_list_col, xl_idx_base)

        # Setting common args
        common_args_tup = (attr_keys_list, otp_list_col, cell_colors,
                           xl_idx_base, otp_col_letter)

        # Using set OTPs by Hash-ID
        dfs_tup = _use_hash_id_set_otps(lab_df, otps_history_tup)
        _, otp_to_set_lab_df = dfs_tup

        # Using set OTPs by DOI
        if len(otp_to_set_lab_df):
            dfs_tup = _use_doi_set_otps(lab_df, otps_history_tup, dfs_tup)

        # Setting OTPs list for "lab" laboratory
        lab_otp_list = dpt_lab_otps_dict[lab]

        # Formatting the worksheet for "lab" lboratory of the department
        wb, _ = _set_lab_otp_ws(lab, dfs_tup, lab_otp_list,
                                wb, first, common_args_tup)
        first = False

    # Saving the workbook
    wb.save(dpt_otp_file_name_path)


def _set_saved_lab_otps(institute, org_tup, otps_history_tup,
                        otp_folder_path, otp_file_base,
                        lab_otps_dict):
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
        otps_history_tup (tup): (useful lists (tup), useful column names (tup), \
        data of OTPs set by DOI (dataframe).
        otp_folder_path (path): The full path to the folder where the file is saved.
        otp_file_base (str): The name base of the file to be saved.
        lab_otps_dict (hierarchical dict): The data keyed by department names (str) \
        and valued by OTPs data given by laboratory of each department (dict).
    """

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]

    # Setting departments list
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting the already attributed OTPs for each department
    for dpt in sorted(dpt_list):
        # Setting the full path of the EXCEl file for the 'dpt' department
        dpt_otp_file_name = f'{otp_file_base}_{dpt}.xlsx'
        dpt_otp_file_name_path = otp_folder_path / Path(dpt_otp_file_name)

        # Setting the dict of list of OTPs per lab for the 'dpt' department
        dpt_lab_otps_dict = lab_otps_dict[dpt]

        # Getting the pub list for department dpt and per lab
        dpt_pub_dict = pd.read_excel(dpt_otp_file_name_path, sheet_name=None)

        # Resetting validation list for OTPs when not already set and saving the file
        _re_save_labs_otp_file(institute, org_tup, dpt_pub_dict, dpt_lab_otps_dict,
                               dpt_otp_file_name_path, otps_history_tup)


def _re_save_dpt_otp_file(institute, org_tup, dfs_tup, cols_tup, dpt_otp_list,
                          dpt_otp_file_name_path, dpt_otp_sheet_name):
    """Rebuilds and saves the openpyxl workbook of the publications list with set OTPs 
    and list-data-validation rules for not yet set OTPs for a department.

    A data validation list is added to the cells 'otp_cell_alias' only when 
    the OTP in not already attributed.

    The openpyxl workbook is created through the `format_page` function imported from 
    the `bmfuncts.format_files` module and is re-configured in the same way as in this 
    function after being modified and before being saved.

    The columns attributes for formatting the workbook are defined through the `set_col_attr` 
    function imported from `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        dfs_tup (tup): (Data of the already attributed OTPs for the department (dataframe), \
        Data of the OTPs still to be attributed for the department (dataframe)).
        cols_tup (tup): Useful column names (str).
        dpt_otp_list (list): The OTPs list of the department.
        dpt_otp_file_name_path (path): Full path to where the workbook is saved. 
        dpt_otp_sheet_name (str): Name of the openpyxl sheet of the workbook.
    """
    # Setting num of first col and first row in EXCEL files
    xl_idx_base = pg.XL_INDEX_BASE

    # Setting cell colors
    cell_colors = build_cell_fill_patterns()

    # Setting parameters from args
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup
    otp_list_col = cols_tup[4]

    # Setting formatting attributes
    attr_keys_list = set_base_keys_list(institute, org_tup)
    dpt_df_title = pg.DF_TITLES_LIST[2]

    # Building validation list of OTP for the department
    validation_list, data_val = build_data_val(dpt_otp_list)

    # Initializing new_dpt_df with the publications which otp is not yet set
    new_dpt_df = otp_to_set_dpt_df.copy()

    # Adding a column containing OTPs of the department
    new_dpt_df[otp_list_col] = validation_list

    # Creating and formatting the openpyxl workbook
    wb, ws = format_page(new_dpt_df, dpt_df_title, attr_keys_list=attr_keys_list)

    # Getting the column letter for the OTPs column
    otp_col_letter = get_col_letter(new_dpt_df, otp_list_col, xl_idx_base)

    # Activating the validation data list in the OTPs column of new_dpt_df
    dpt_df_len = len(new_dpt_df)
    if dpt_df_len:
        ws = add_data_val(ws, data_val, dpt_df_len, otp_col_letter,
                          xl_idx_base)

    # Appending rows of the publications which OTP is already set to ws
    # and coloring the rows alternatively
    if len(otp_set_dpt_df):
        ws = _add_set_otp_rows(ws, otp_set_dpt_df, dpt_df_len, cell_colors)

    # Re-shaping the alignment and the border of the columns
    df_cols_list = new_dpt_df.columns
    col_attr_dict, _, _ = set_df_attributes(dpt_df_title, df_cols_list, attr_keys_list)
    ws = align_cell(ws, df_cols_list, col_attr_dict, xl_idx_base)

    # Re-shaping header
    ws = format_heading(ws, dpt_df_title)

    # Setting the worksheet label
    ws.title = dpt_otp_sheet_name

    # Saving the workbook
    wb.save(dpt_otp_file_name_path)


def _set_saved_dept_otps(institute, org_tup, otps_history_tup,
                         otp_folder_path, otp_file_base):
    """Attributes the OTPs from the history of the attributed OTPs 
    at department level before submiting to the user the file 
    for attributing the not-yet attributed OTPs.

    Loops on department to:

        1. Build the dataframe with already attributed OTPs \
    and OTPs remaining to be attributed. 
        2. Save the file to be submitted to the user through the \
    `_re_save_dpt_otp_file` internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        otps_history_tup (tup): (useful lists (tup), useful column names (tup), \
        data of OTPs set by DOI (dataframe).
        otp_folder_path (path): The full path to the folder where the file is saved.
        otp_file_base (str): The name base of the file to be saved.
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
        dpt_otp_file_name = f'{otp_file_base}_{dpt}.xlsx'
        dpt_otp_file_name_path = otp_folder_path / Path(dpt_otp_file_name)

        # Setting the sheet name of the EXCEl file for the 'dpt' department
        dpt_otp_sheet_name = pg.OTP_SHEET_NAME_BASE + " " +  dpt

        # Getting the pub list for department dpt
        dpt_df = pd.read_excel(dpt_otp_file_name_path)

        # Using set OTPs by Hash-ID
        dfs_tup = _use_hash_id_set_otps(dpt_df, otps_history_tup)
        _, otp_to_set_dpt_df = dfs_tup

        # Using set OTPs by DOI
        if len(otp_to_set_dpt_df):
            dfs_tup = _use_doi_set_otps(dpt_df, otps_history_tup, dfs_tup)

        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = dpt_attributs_dict[dpt][ig.DPT_OTP_KEY]

        # Resetting validation list for OTPs when not already set and saving the file
        _re_save_dpt_otp_file(institute, org_tup, dfs_tup, cols_tup, dpt_otp_list,
                              dpt_otp_file_name_path, dpt_otp_sheet_name)


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
        if otp_level=="LAB":
            lab_otps_dict = set_lab_otps(institute, org_tup, bibliometer_path)
            _set_saved_lab_otps(institute, org_tup, otps_history_tup,
                                otp_folder_path, otp_file_base_alias,
                                lab_otps_dict)
        else:
            _set_saved_dept_otps(institute, org_tup, otps_history_tup,
                                 otp_folder_path, otp_file_base_alias)

        message = "Already set OTPS used"
    else:
        message = "No already set OTPS available"
    return message
