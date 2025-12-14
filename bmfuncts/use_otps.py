"""Module of functions for using publications attributes
such as homonyms and OTPs.

"""

__all__ = ['save_otps',
           'set_pub_otp_df',
           'set_saved_otps',
          ]


# Standard library imports
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl import Workbook as openpyxl_Workbook

# Local imports
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
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
from bmfuncts.format_files import set_df_attributes
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.rename_cols import set_otp_col_names
from bmfuncts.useful_functs import concat_dfs


def _set_use_otps_cols(institute, org_tup):
    """Builds a dict setting selected columns names for the process 
    of OTPs attribution resolution.

    This is done through the `set_otp_col_names` function imported from the 
    `bmfuncts.rename_cols` module.
    
    Args:
        institute (str): Institute name.
        org_tup (tup): Contains parameters of Institute organization.
    Returns:
        (tup): The built dict and the full list of final column names \
        got from the `set_final_col_names` function imported from the \
        `bmfuncts.rename_cols` module.
    """
    # Setting final column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)

    # Setting the final column names of the data for OTPs attribution by the user
    otp_col_dic = set_otp_col_names(institute, org_tup)

    use_otps_cols_dic = {'hash_id_col'  : otp_col_dic['hash_id'],
                         'pub_id_col'   : otp_col_dic['pub_id'],
                         'author_col'   : otp_col_dic['first_author'],
                         'doi_col'      : otp_col_dic['doi'],
                         'otp_list_col' : otp_col_dic['otp_list'],
                         'otp_col'      : bm_pg.COL_NAMES_BONUS['final OTP'],
                        }

    final_col_list = list(final_col_dic.values())
    return use_otps_cols_dic, final_col_list


def _set_save_otp_file_params(save_otp_params_list):
    """Sets the files parameters for saving the history 
    of attributed OTPs by the user.
    
    Args:
        save_otp_params_list (list): Composed of the Full path \
        to working folder and of the corpus year (str) defined \
        by 4 digits.
    Returns:
        (tup): (The base (str) for building OTPs file names, \
        The full path to the folder of OTPs attribution, \
        The full path (path) to the file of Hash-IDs, \
        The full path (path) to the file of history of attributed OTPs, \
        The sheet names (dict) of the file of history of attributed OTPs).
    """
    # setting parameters value from save_otp_params_list
    wf_path, corpus_year = save_otp_params_list

    # Setting useful folder and file aliases
    merge_folder_alias = bm_pg.ARCHI_YEAR["bdd mensuelle"]
    otp_folder_alias = bm_pg.ARCHI_YEAR["OTP folder"]
    otp_file_base_alias = bm_pg.ARCHI_YEAR["OTP file name base"]
    history_folder_alias = bm_pg.ARCHI_YEAR["history folder"]
    kept_otps_file_alias = bm_pg.ARCHI_YEAR["kept OTPs file name"]
    hash_id_file_alias = bm_pg.ARCHI_YEAR["hash_id file name"]

    # Setting useful paths
    corpus_year_path = wf_path / Path(corpus_year)
    merge_folder_path = corpus_year_path / Path(merge_folder_alias)
    hash_id_file_path = merge_folder_path / Path(hash_id_file_alias)
    history_folder_path = corpus_year_path / Path(history_folder_alias)
    kept_otps_file_path = history_folder_path / Path(kept_otps_file_alias)
    otp_folder_path = corpus_year_path / Path(otp_folder_alias)

    # Setting dict of useful sheets
    otp_sheets_dict = {'hash_id': bm_pg.SHEET_SAVE_OTP['hash_OTP'],
                       'doi'    : bm_pg.SHEET_SAVE_OTP['doi_OTP'],
                      }

    file_params_tup = (otp_file_base_alias, otp_folder_path,
                       hash_id_file_path, kept_otps_file_path,
                       otp_sheets_dict)

    return file_params_tup


def _set_read_otp_file_params(dpt_label_list, set_hist_file_params_list):
    """Sets the full paths to the files where the OTPs have been 
    attributed by the user for the Institute departments.

    The name of the files is build using the file-name base given 
    by a global and the department label. This name is added '_ok' if 
    this file exists in the folder of the files.

    Args:
        dpt_label_list (list): The names (str) list of Institute \
        departments.
        set_hist_file_params_list (list): Composed of the base (str) for \
        building OTPs file names and of the full path to the folder \
        of OTPs attribution.
    Returns:
        (dict): The dict keyed by department names and valued \
        by the full path (path) to the file where the attributed \
        OTPs for the department are saved.
    """
    otp_file_base_alias, otp_folder_path = set_hist_file_params_list

    dpt_otp_paths = {}
    for dpt_label in dpt_label_list:
        dpt_otp_file_base = f'{otp_file_base_alias}_{dpt_label}'
        dpt_otp_file = f'{dpt_otp_file_base}_ok.xlsx'
        dpt_otp_path = otp_folder_path / Path(dpt_otp_file)
        if not os.path.exists(dpt_otp_path):
            dpt_otp_file = f'{dpt_otp_file_base}.xlsx'
            dpt_otp_path = otp_folder_path / Path(dpt_otp_file)
        dpt_otp_paths[dpt_label] = dpt_otp_path
    return dpt_otp_paths


def _build_dpt_otp_df(dpt_otp_path):
    """Builds the publications list of the department 
    from the file where the user has attributed the OTPs.

    The attributed OTPs data are got from a multisheet xlsx file. 
    The final publications list of the department results from 
    the concatenation of the content of all the existing sheets.

    Args:
        dpt_otp_path (path): The full path to the file where \
        the attributed OTPs for the department are saved.
    Returns:
        (dataframe): The publications list with OTPs for the department.        
    """
    dpt_otp_dict = pd.read_excel(dpt_otp_path, sheet_name=None)
    dpt_otp_df = pd.DataFrame()
    for _, lab_df in dpt_otp_dict.items():
        dpt_otp_df = concat_dfs([dpt_otp_df, lab_df])
    return dpt_otp_df


def _concat_dept_otps_dfs(dpt_label_list, set_hist_file_params_list):
    """Concatenates the publications list of the Institute departments 
    after getting them through the `_build_dpt_otp_df` internal function.

    Args:
        dpt_label_list (list): The names (str) list of Institute \
        departments.
        set_hist_file_params_list (list): Composed of the base (str) for \
        building OTPs file names and of the full path to the folder \
        of OTPs attribution.
    Returns:
        (dataframe): The concatenated publications list with OTPs.        
    """
    # Setting dict of full path per institute departments
    dpt_otp_paths = _set_read_otp_file_params(dpt_label_list, set_hist_file_params_list)

    # Concatenating publications list with OTPs of the Institute departments
    otp_df_init_status = True
    for dpt_label in dpt_label_list:
        # Getting department publications list with OTPs
        dpt_otp_df = _build_dpt_otp_df(dpt_otp_paths[dpt_label])

        # Appending department publications list with OTPs
        # to the full publication list to be returned
        if otp_df_init_status:
            otp_df = dpt_otp_df.copy()
            otp_df_init_status = False
        else:
            otp_df = concat_dfs([otp_df, dpt_otp_df])
    return otp_df


def set_pub_otp_df(dpt_label_list, set_hist_file_params_list, final_col_list, pub_id_col):
    """Builds the data of publications list with OTPs from the files where OTPs 
    have been set by the user for each department.
 
    For that it uses the `_concat_dept_otps_dfs` internal function.

    Args:
        dpt_label_list (list): The names (str) list of Institute \
        departments.
        set_hist_file_params_list (list): Composed of the base (str) for \
        building OTPs file names and of the full path to the folder \
        of OTPs attribution.
        final_col_list (list): The list of column names of the built data.
        pub_id_col (str): The column name of publications IDs.
    Returns:
        (dataframe): The built data. 
    """
    # Getting dept OTPs df and concatenating them
    init_pub_otp_df = _concat_dept_otps_dfs(dpt_label_list, set_hist_file_params_list)

    # Deduplicating rows on Pub_id
    init_pub_otp_df = init_pub_otp_df.drop_duplicates(subset=[pub_id_col])

    # Selecting useful columns using final_col_list
    pub_otp_df = init_pub_otp_df[final_col_list].copy()
    pub_otp_df = pub_otp_df.reset_index()

    return pub_otp_df


def _update_otps_history(kept_otps_file_path, otp_sheets_dict, otps_history_dfs):
    """The file of the history of OTPs attributed by the user is updated 
    with the refreshed data of attributed OTPs.

    The file is composed of two sheets:

    - A first sheet with the following columns:

        - Hash-ID of the publication for which OTPs have been attributed. 
        - The OTPs value attributed.

    - A second sheet with the following columns:

        - Full name (last name + first name initials) of the first author \
        of the publication for which OTPs have been attributed.
        - DOI of the publication for which OTPs have been attributed.
        - The OTPs value attributed.

    Args:
        kept_otps_file_path (path): The full path to the file \
        of the history of attributed OTPs.
        otp_sheets_dict (dict): The dict giving the sheet names as built \
        by the `_set_save_otp_file_params` internal function.
        otps_history_dfs (list): The list of the two dataframes of the refreshed \
        data of attributed OTPs with the same structure as the sheets \
        of the file to be updated.
    Returns:
        (str): End message.
    """
    # Setting parameters values from args
    hash_otp_sheet, doi_otp_sheet = otp_sheets_dict['hash_id'], otp_sheets_dict['doi']
    hash_otps_history_df, doi_otps_history_df = otps_history_dfs

    # Concatenating with the dataframes of already saved solved OTPs by hash_id and by DOI
    if kept_otps_file_path.is_file():
        existing_otps_history_dict = pd.read_excel(kept_otps_file_path, sheet_name=None)
        existing_hash_otps_history_df = existing_otps_history_dict[hash_otp_sheet]
        existing_doi_otps_history_df = existing_otps_history_dict[doi_otp_sheet]
    else:
        existing_hash_otps_history_df = pd.DataFrame(columns=hash_otps_history_df.columns)
        existing_doi_otps_history_df = pd.DataFrame(columns=doi_otps_history_df.columns)
        with pd.ExcelWriter(kept_otps_file_path) as writer: # https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
            existing_hash_otps_history_df.to_excel(writer, sheet_name=hash_otp_sheet, index=False)
            existing_doi_otps_history_df.to_excel(writer, sheet_name=doi_otp_sheet, index=False)

    hash_otps_nb = len(existing_hash_otps_history_df)-1
    if hash_otps_nb:
        hash_otps_history_df = concat_dfs([existing_hash_otps_history_df, hash_otps_history_df])
    hash_otps_history_df = hash_otps_history_df.astype('str')
    hash_otps_history_df = hash_otps_history_df.drop_duplicates()

    doi_otps_nb = len(existing_doi_otps_history_df)-1
    if doi_otps_nb:
        doi_otps_history_df = concat_dfs([existing_doi_otps_history_df, doi_otps_history_df])
    doi_otps_history_df = doi_otps_history_df.astype('str')
    doi_otps_history_df = doi_otps_history_df.drop_duplicates()

    with pd.ExcelWriter(kept_otps_file_path,  # https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
                        mode='a', if_sheet_exists='replace') as writer:
        hash_otps_history_df.to_excel(writer, sheet_name=hash_otp_sheet, index=False)
        doi_otps_history_df.to_excel(writer, sheet_name=doi_otp_sheet, index=False)

    message = "History of kept OTPs saved"
    return message


def save_otps(sub_params_list):
    """Saves the history of the attributed OTPs by the user.

    First, it builds the data of publications list with OTPs set by the user \
    through the `set_pub_otp_df` function of the same module.

    Then it saves the history data as a multisheet xlsx file through 
    the `_update_otps_history` internal function.

    Args:
        sub_params_list (list): The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path) and the 4 digits year \
        of the corpus (str).
    Returns:
        (tup): (End message (str), the built data of publications list \
        with OTPs attributed by the user (dataframe)).
    """
    # Setting useful params values and lists from sub_params_list
    institute, org_tup, wf_path, corpus_year = sub_params_list
    save_otp_params_list = [wf_path, corpus_year]
    dpt_label_dict = org_tup[1]
    dpt_label_list = list(dpt_label_dict.keys())

    # Setting useful selected column names for saving the history of attributed OTPS
    use_otps_cols_dic, final_col_list = _set_use_otps_cols(institute, org_tup)
    col_keys = ['pub_id_col', 'author_col', 'doi_col', 'otp_list_col', 'otp_col']
    (pub_id_col, author_col, doi_col,
     otp_list_col, otp_col) = [use_otps_cols_dic[key] for key in col_keys]

    # Setting useful file parameters
    file_params_tup = _set_save_otp_file_params(save_otp_params_list)
    hash_id_file_path, kept_otps_file_path, otp_sheets_dict = file_params_tup[2:]
    set_hist_file_params_list = list(file_params_tup)[0:2]

    # Getting the hash_id dataframe
    hash_id_df  = pd.read_excel(hash_id_file_path)

    # Setting the publication list with OTP info
    pub_otp_df = set_pub_otp_df(dpt_label_list, set_hist_file_params_list,
                                final_col_list, pub_id_col)

    # Building set OTPs df
    if otp_col in pub_otp_df.columns:
        data_otp_col = otp_col
    else:
        data_otp_col = otp_list_col
    otps_df = pub_otp_df[[pub_id_col, author_col, doi_col, data_otp_col]].copy()
    otps_df = otps_df.fillna(0)
    otps_df = otps_df.astype(str)
    set_otps_df = otps_df.copy()
    sep = ","
    for idx, row in otps_df.iterrows():
        if sep in row[data_otp_col] or row[data_otp_col]=="0":
            set_otps_df = set_otps_df.drop(idx)

    # Building kept OTPs data per Hash_ID
    hash_otps_history_df = hash_id_df.merge(set_otps_df,
                                            how='inner',
                                            on=pub_id_col)
    hash_otps_history_df = hash_otps_history_df.drop(columns=[pub_id_col, author_col, doi_col])
    hash_otps_history_df = hash_otps_history_df.rename(columns={data_otp_col:otp_col})

    # Building kept OTPs data per DOI
    doi_otps_history_df = set_otps_df[[author_col, doi_col, data_otp_col]].copy()
    doi_otps_history_df = doi_otps_history_df.rename(columns={data_otp_col:otp_col})

    # Concatenating with the data of already saved solved OTPs by hash_id and by DOI
    otps_history_dfs = [hash_otps_history_df, doi_otps_history_df]
    message = _update_otps_history(kept_otps_file_path, otp_sheets_dict, otps_history_dfs)

    return message, pub_otp_df


def _use_hash_id_set_otps(dpt_df, otps_history_tup, use_otps_cols_dic):
    """Uses set otps by Hash-IDs.
    """
    # Setting parameters values from 'otps_history_tup'
    lists_dict, _ = otps_history_tup
    pub_id_to_check_list = lists_dict['pub_id_to_check']
    otp_to_set_list = lists_dict['otp_to_set']

    # Setting useful col names
    pub_id_col = use_otps_cols_dic['pub_id_col']
    otp_list_col = use_otps_cols_dic['otp_list_col']

    # Setting the pub-id list for department dpt
    dept_pub_id_list = dpt_df[pub_id_col].to_list()

    # Building the 'otp_set_dpt_df' dataframe of publication with OTP set
    otp_set_dpt_df = pd.DataFrame(columns=list(dpt_df.columns))

    # Building the 'otp_to_set_dpt_df' dataframe of publication
    # with OTP still to be defined
    otp_to_set_dpt_df = dpt_df.copy()
    otp_to_set_dpt_df = otp_to_set_dpt_df.drop(columns=[otp_list_col])

    for otp_idx, pub_id_to_check in enumerate(pub_id_to_check_list):
        if pub_id_to_check in dept_pub_id_list:
            otp_to_set = otp_to_set_list[otp_idx]
            pub_id_idx = [i for i,e in enumerate(dept_pub_id_list)
                          if e==pub_id_to_check][0]
            dpt_df.loc[pub_id_idx, otp_list_col] = otp_to_set
            dpt_pub_id_to_check_df = dpt_df[dpt_df[pub_id_col]==pub_id_to_check]
            otp_set_dpt_df = concat_dfs([otp_set_dpt_df, dpt_pub_id_to_check_df])
            otp_to_set_dpt_df = otp_to_set_dpt_df.drop(index=pub_id_idx)
        else:
            continue
    dfs_tup = (otp_set_dpt_df, otp_to_set_dpt_df)
    return dfs_tup


def _use_known_doi_otps(dfs_tup, use_otps_cols_dic, dpt_df,
                        doi_to_check, doi_otp_to_set):
    """Manages case of known DOIs.
    """
    # Setting parameters values from 'dfs_tup'
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup

    # Setting useful col names
    doi_col = use_otps_cols_dic['doi_col']
    otp_list_col = use_otps_cols_dic['otp_list_col']

    # Setting the DOI index in 'dpt_df' to fill with 'doi_otp_to_set'
    # at 'otp_list_col' col
    dept_doi_list = dpt_df[doi_col].to_list()
    dpt_doi_idx_list = [i for i,e in enumerate(dept_doi_list)
                        if e==doi_to_check]
    doi_idx = dpt_doi_idx_list[0]

    dpt_df_to_add = dpt_df[dpt_df[doi_col]==doi_to_check].copy()
    dpt_df_to_add.loc[doi_idx, otp_list_col] = doi_otp_to_set
    otp_set_dpt_df = concat_dfs([otp_set_dpt_df, dpt_df_to_add])
    otp_to_set_dpt_df = otp_to_set_dpt_df.drop(index=doi_idx)
    dfs_tup = (otp_set_dpt_df, otp_to_set_dpt_df)
    return dfs_tup


def _use_authors_otps(dfs_tup, use_otps_cols_dic, dpt_df_to_add,
                      auth_idx, auth_to_check, auth_otp_to_set):
    """Uses set OTPs by first-author name of unknown DOIs.
    """
    # Setting parameters values from 'dfs_tup'
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup

    # Setting useful col names
    author_col = use_otps_cols_dic['author_col']
    otp_list_col = use_otps_cols_dic['otp_list_col']

    auth_idx_to_replace_list = []
    if auth_idx in otp_to_set_dpt_df.index:
        auth_idx_to_replace_list.append(auth_idx)
        if auth_idx in otp_set_dpt_df.index:
            otp_set_dpt_df = otp_set_dpt_df.drop(index=auth_idx)

        for auth_idx_to_replace in auth_idx_to_replace_list:
            dpt_df_to_add.loc[auth_idx_to_replace, otp_list_col] = auth_otp_to_set
            new_dpt_df_to_add = dpt_df_to_add[dpt_df_to_add[author_col]==auth_to_check].copy()
            new_dpt_df_to_add.loc[auth_idx_to_replace, otp_list_col] = auth_otp_to_set
            otp_set_dpt_df = concat_dfs([otp_set_dpt_df, new_dpt_df_to_add])
            otp_to_set_dpt_df = otp_to_set_dpt_df.drop(index=auth_idx_to_replace)
    dfs_tup = (otp_set_dpt_df, otp_to_set_dpt_df)
    return dfs_tup


def _use_unknown_doi_otps(dfs_tup, otps_history_tup, use_otps_cols_dic,
                          dpt_df, doi_to_check):
    """Manages case of unknown DOIs.
    """
    # Setting parameters values from 'dfs_tup'
    otp_to_set_dpt_df = dfs_tup[1]

    # Setting parameters values from 'otps_history_tup'
    _, doi_otp_history_df = otps_history_tup

    # Setting useful col names
    author_col = use_otps_cols_dic['author_col']
    doi_col = use_otps_cols_dic['doi_col']
    otp_col = use_otps_cols_dic['otp_col']

    new_otp_to_set_dpt_df = otp_to_set_dpt_df[otp_to_set_dpt_df[doi_col]==doi_to_check].copy()
    otp_to_set_auth_list = new_otp_to_set_dpt_df[author_col].to_list()

    new_doi_otp_history_df = doi_otp_history_df[doi_otp_history_df[doi_col]==doi_to_check].copy()
    new_author_to_check_list = new_doi_otp_history_df[author_col].to_list()
    auth_otp_to_set_list = new_doi_otp_history_df[otp_col].to_list()

    for auth_otp_idx, auth_to_check in enumerate(new_author_to_check_list):
        if auth_to_check in otp_to_set_auth_list:
            auth_otp_to_set = auth_otp_to_set_list[auth_otp_idx]
            dpt_df_to_add = dpt_df[dpt_df[doi_col]==doi_to_check].copy()
            dept_auth_list = dpt_df[author_col].to_list()
            dpt_auth_idx_list = [i for i,e in enumerate(dept_auth_list) if e==auth_to_check]

            for auth_idx in dpt_auth_idx_list:
                dfs_tup = _use_authors_otps(dfs_tup, use_otps_cols_dic, dpt_df_to_add,
                                            auth_idx, auth_to_check, auth_otp_to_set)
        else:
            continue
    return dfs_tup


def _use_doi_set_otps(dpt_df, otps_history_tup, use_otps_cols_dic, dfs_tup):
    """Uses set OTPs by DOI.
    """
    # Setting parameters values from 'otps_history_tup'
    lists_dict, _ = otps_history_tup
    doi_to_check_list = lists_dict['doi_to_check']
    doi_otp_to_set_list = lists_dict['doi_otp_to_set']

    # Setting useful col names
    doi_col = use_otps_cols_dic['doi_col']

    # Setting parameters from args
    _, otp_to_set_dpt_df = dfs_tup

    # Setting the DOIs list of otp_to_set_dpt_df
    otp_to_set_doi_list = otp_to_set_dpt_df[doi_col].to_list()

    for otp_idx, doi_to_check in enumerate(doi_to_check_list):
        if doi_to_check in otp_to_set_doi_list:
            if doi_to_check!=bp.UNKNOWN:
                # Case of known DOIs
                doi_otp_to_set = doi_otp_to_set_list[otp_idx]
                dfs_tup = _use_known_doi_otps(dfs_tup, use_otps_cols_dic, dpt_df,
                                              doi_to_check, doi_otp_to_set)
            else:
                # Case of unknown DOIs (use of first author name)
                dfs_tup = _use_unknown_doi_otps(dfs_tup, otps_history_tup, use_otps_cols_dic,
                                                dpt_df, doi_to_check)
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


def _set_otp_save_params(use_otps_cols_dic):
    """Builds the list of parameters for the process of saving OTPs data."""
    # Setting num of first col and first row in EXCEL files
    xl_idx_base = bm_pg.XL_INDEX_BASE

    # Setting formatting attributes
    df_title = bm_pg.DF_TITLES_LIST[2]

    # Setting cell colors
    cell_colors = build_cell_fill_patterns()

    # Setting useful col names
    otp_list_col = use_otps_cols_dic['otp_list_col']

    save_params = [cell_colors, df_title, xl_idx_base, otp_list_col]
    return save_params


def _update_common_params(df, init_common_params):
    """Updates the shared parameters by all departments with the openpyxl 
    letter associated with the column of OTPs values."""
    # Setting parameters values from 'init_common_params'
    xl_idx_base, otp_list_col = init_common_params[2:]

    # Getting the column letter for the OTPs column
    otp_col_letter = get_col_letter(df, otp_list_col, xl_idx_base)

    # Setting shared params by all units
    new_common_params = init_common_params + [otp_col_letter]
    return new_common_params


def _set_lab_otp_ws(lab, dfs_tup, lab_otp_list, wb, first, labs_common_params):
    """Builds the openpyxl sheet of a laboratory in the openpyxl workbook 
    of the department it belongs, to using set OTPs and keeping validation 
    rules for not set OTPs.
    """
    # Setting parameters from args
    otp_set_lab_df, otp_to_set_lab_df = dfs_tup
    (cell_colors, lab_df_title,
     xl_idx_base, otp_list_col, otp_col_letter) = labs_common_params

    # Initializing new_lab_df with the publications which otp is not yet set
    new_lab_df = otp_to_set_lab_df.copy()

    # Building validation list of OTP for 'lab' laboratory
    validation_list, data_val = build_data_val(lab_otp_list)

    # Adding a column containing OTPs of 'dpt' department
    new_lab_df[otp_list_col] = validation_list

    # Formatting the openpyxl workbook
    sheet_name = lab
    wb = format_wb_sheet(sheet_name, new_lab_df,
                         lab_df_title, wb, first)
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
    col_attr_dict, _, _ = set_df_attributes(lab_df_title, df_cols_list)
    ws = align_cell(ws, df_cols_list, col_attr_dict, xl_idx_base)

    # Re-shaping header
    ws = format_heading(ws, lab_df_title)
    return wb, ws


def _re_save_labs_otp_file(dicts_list, use_otps_cols_dic, dpt_otp_file_name_path,
                           otps_history_tup, dpts_common_params):
    """Rebuilds and saves the OTPs data for a department as a multi-sheet 
    Openpyxl workbook with one sheet per lab.

    A data validation list is added to the cells 'otp_cell_alias' only when 
    the OTP in not already attributed. 
    It loops on lab of the department to:
    - To use the set OTPs by Hash-ID through the `_use_hash_id_set_otps` internal function.
    - To use the set OTPs by DOI through the `_use_doi_set_otps` internal function.
    - To create and configure a sheet in the workbook with the OTPs data for the lab _
    through the `_set_lab_otp_ws` internal function.

    Args:
        dicts_list (list): Composed of the data (dict) of the department keyed by \
        laboratory names (str) and valued by publications data (dataframe) and of \
        the data (dict) of the department keyed by laboratory names (str) and \
        valued by OTPs list (list).
        use_otps_cols_dic (dict): selected columns names for the process of OTPs \
        attribution resolution as built through the `_set_use_otps_cols` internal function.
        dpt_otp_file_name_path (path): Full path to where the workbook is saved.
        otps_history_tup (tup): (useful lists (tup), useful column names (tup), \
        data of OTPs set by DOI (dataframe).
        dpts_common_params (list): The shared parameters by all Institute's departments \
        as built through the `_set_otp_save_params` internal function.
    """
    # Setting parameters values from 'dicts_list'
    dpt_pub_dict, dpt_lab_otps_dict = dicts_list

    # Initialize parameters for saving results as multisheet workbook
    first = True
    labs_common_params = dpts_common_params
    wb = openpyxl_Workbook()

    for lab, lab_df in dpt_pub_dict.items():
        if first:
            labs_common_params = _update_common_params(lab_df, labs_common_params)
            first = False

        # Using set OTPs by Hash-ID
        dfs_tup = _use_hash_id_set_otps(lab_df, otps_history_tup, use_otps_cols_dic)
        _, otp_to_set_lab_df = dfs_tup

        # Using set OTPs by DOI
        if len(otp_to_set_lab_df):
            dfs_tup = _use_doi_set_otps(lab_df, otps_history_tup, use_otps_cols_dic, dfs_tup)

        # Setting OTPs list for "lab" laboratory
        lab_otp_list = dpt_lab_otps_dict[lab]

        # Formatting the worksheet for "lab" laboratory of the department
        wb, _ = _set_lab_otp_ws(lab, dfs_tup, lab_otp_list,
                                wb, first, labs_common_params)

    # Saving the workbook
    if "Sheet" in wb.sheetnames:
        wb.remove(wb['Sheet'])
    wb.save(dpt_otp_file_name_path)


def _set_saved_lab_otps(org_tup, otps_history_tup, use_otps_cols_dic,
                        set_hist_file_params_list, lab_otps_dict):
    """Attributes the OTPs from the history of the attributed OTPs 
    before submitting to the user the file for attributing the not yet
    attributed OTPs.

    Loops on department to:

        1. Build the dataframe with already attributed OTPs \
    and OTPs remaining to be attributed. 
        2. Save the dataframe as openpyxl file through the \
    `_re_save_dpt_otp_file` internal function.

    Args:
        org_tup (tup): Contains Institute parameters.
        otps_history_tup (tup): (useful lists (tup), useful column names (tup), \
        data of OTPs set by DOI (dataframe).
        use_otps_cols_dic (dict): selected columns names for the process of OTPs \
        attribution resolution as built through the `_set_use_otps_cols` internal function.
        set_hist_file_params_list (list): Composed of the base (str) for \
        building OTPs file names and of the full path to the folder \
        of OTPs attribution.
        lab_otps_dict (hierarchical dict): The data keyed by department names (str) \
        and valued by OTPs data given by laboratory of each department (dict).
    """
    # Setting parameters shared by all departments for saving OTPs data
    dpts_common_params = _set_otp_save_params(use_otps_cols_dic)

    # Setting parameters values from 'set_hist_file_params_list'
    otp_file_base, otp_folder_path = set_hist_file_params_list

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
        dicts_list = [dpt_pub_dict, dpt_lab_otps_dict]
        _re_save_labs_otp_file(dicts_list, use_otps_cols_dic, dpt_otp_file_name_path,
                               otps_history_tup, dpts_common_params)


def _re_save_dpt_otp_file(dfs_tup, dpt_otp_list, dpt_otp_file_name_path,
                          dpt_otp_sheet_name, dpts_common_params):
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
        dfs_tup (tup): (Data of the already attributed OTPs for the department (dataframe), \
        Data of the OTPs still to be attributed for the department (dataframe)).
        dpt_otp_list (list): The OTPs list of the department.
        dpt_otp_file_name_path (path): Full path to where the workbook is saved. 
        dpt_otp_sheet_name (str): Name of the openpyxl sheet of the workbook.
        dpts_common_params (list): The shared parameters by all Institute's departments \
        as built through the `_set_otp_save_params` internal function.
    """
    # Setting parameters from args
    otp_set_dpt_df, otp_to_set_dpt_df = dfs_tup
    (cell_colors, dpt_df_title,
     xl_idx_base, otp_list_col, otp_col_letter) = dpts_common_params

    # Building validation list of OTP for the department
    validation_list, data_val = build_data_val(dpt_otp_list)

    # Initializing new_dpt_df with the publications which otp is not yet set
    new_dpt_df = otp_to_set_dpt_df.copy()

    # Adding a column containing OTPs of the department
    new_dpt_df[otp_list_col] = validation_list

    # Creating and formatting the openpyxl workbook
    wb, ws = format_page(new_dpt_df, dpt_df_title)

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
    col_attr_dict, _, _ = set_df_attributes(dpt_df_title, df_cols_list)
    ws = align_cell(ws, df_cols_list, col_attr_dict, xl_idx_base)

    # Re-shaping header
    ws = format_heading(ws, dpt_df_title)

    # Setting the worksheet label
    ws.title = dpt_otp_sheet_name

    # Saving the workbook
    wb.save(dpt_otp_file_name_path)


def _set_saved_dept_otps(org_tup, otps_history_tup, use_otps_cols_dic,
                         set_hist_file_params_list):
    """Attributes the OTPs from the history of the attributed OTPs 
    at department level before submitting to the user the file
    for attributing the not-yet attributed OTPs.

    Loops on department to:

        1. Build the dataframe with already attributed OTPs \
    and OTPs remaining to be attributed. 
        2. Save the file to be submitted to the user through the \
    `_re_save_dpt_otp_file` internal function.

    Args:
        org_tup (tup): Contains Institute parameters.
        otps_history_tup (tup): (useful lists (tup), useful column names (tup), \
        data of OTPs set by DOI (dataframe).
        use_otps_cols_dic (dict): selected columns names for the process of OTPs \
        attribution resolution as built through the `_set_use_otps_cols` internal function.
        set_hist_file_params_list (list): Composed of the base (str) for \
        building OTPs file names and of the full path to the folder \
        of OTPs attribution.
    """
    # Setting parameters values from 'set_hist_file_params_list'
    otp_file_base, otp_folder_path = set_hist_file_params_list

    # Initialize parameters for saving OTPs data as openpyxl workbook
    first = True
    dpts_common_params = _set_otp_save_params(use_otps_cols_dic)

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]

    # Setting departments list
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting the already attributed OTPs for each department
    for dpt in sorted(dpt_list):
        # Setting the full path of the EXCEl file for the 'dpt' department
        dpt_otp_file_name = f'{otp_file_base}_{dpt}.xlsx'
        dpt_otp_file_name_path = otp_folder_path / Path(dpt_otp_file_name)

        # Setting the sheet name of the EXCEl file for the 'dpt' department
        dpt_otp_sheet_name = bm_pg.OTP_SHEET_NAME_BASE + " " +  dpt

        # Getting the pub list for department dpt
        dpt_df = pd.read_excel(dpt_otp_file_name_path)

        if first:
            dpts_common_params = _update_common_params(dpt_df, dpts_common_params)
            first = False

        # Using set OTPs by Hash-ID
        dfs_tup = _use_hash_id_set_otps(dpt_df, otps_history_tup, use_otps_cols_dic)
        _, otp_to_set_dpt_df = dfs_tup

        # Using set OTPs by DOI
        if len(otp_to_set_dpt_df):
            dfs_tup = _use_doi_set_otps(dpt_df, otps_history_tup, use_otps_cols_dic, dfs_tup)

        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = dpt_attributs_dict[dpt][bm_ig.DPT_OTP_KEY]

        # Resetting validation list for OTPs when not already set and saving the file
        _re_save_dpt_otp_file(dfs_tup, dpt_otp_list, dpt_otp_file_name_path,
                              dpt_otp_sheet_name, dpts_common_params)


def _get_otps_history(get_hist_file_params_list, use_otps_cols_dic):
    """Gets the history of previously set OTPs.

    Args:
        get_hist_file_params_list (list):  Composed of the full path (path) to the file \
        of Hash-IDs, the full path (path) to the file of history of attributed OTPs, \
        the sheet names (dict) of the file of history of attributed OTPs.
        use_otps_cols_dic (dict): selected columns names for the process of OTPs \
        attribution resolution as built through the `_set_use_otps_cols` internal function.
    Returns:
        (tup): (Dict valued by lists of infos for using previously set OTPs, \
        The data of the history of previously set OTPs by DOI).
    """
    # Setting useful col names
    col_keys = ['hash_id_col', 'pub_id_col', 'author_col', 'doi_col', 'otp_col']
    (hash_id_col, pub_id_col, author_col,
     doi_col, otp_col) = [use_otps_cols_dic[key] for key in col_keys]

    # Setting parameters values from get_hist_file_params_list
    hash_id_file_path, kept_otps_file_path, otp_sheets_dict = get_hist_file_params_list
    hash_otp_sheet = otp_sheets_dict['hash_id']
    doi_otp_sheet = otp_sheets_dict['doi']

    # Getting the hash_id dataframe
    hash_id_df = pd.read_excel(hash_id_file_path)

    # Getting the kept OTPs dataframe by hash_id
    hash_otp_history_df = pd.read_excel(kept_otps_file_path,
                                        sheet_name=hash_otp_sheet)

    # Building data of pub_id and OTPs to set related to hash_id
    pub_id_otp_to_set_df = pd.merge(hash_id_df,
                                    hash_otp_history_df,
                                    how='inner',
                                    on=hash_id_col)

    pub_id_otp_to_set_df = pub_id_otp_to_set_df.astype(str)
    pub_id_otp_to_set_df = pub_id_otp_to_set_df.drop(columns=[hash_id_col])
    pub_id_to_check_list = [str(row[pub_id_col]) for _,row
                            in pub_id_otp_to_set_df.iterrows()]
    otp_to_set_list = [str(row[otp_col]) for _,row
                       in pub_id_otp_to_set_df.iterrows()]

    # Getting the kept OTPs dataframe by DOI and first author
    doi_otp_history_df = pd.read_excel(kept_otps_file_path,
                                       sheet_name=doi_otp_sheet)
    author_to_check_list = doi_otp_history_df[author_col].to_list()
    doi_to_check_list = doi_otp_history_df[doi_col].to_list()
    doi_otp_to_set_list = doi_otp_history_df[otp_col].to_list()

    # Setting dict to return
    otps_hist_dict = {'pub_id_to_check': pub_id_to_check_list,
                      'otp_to_set'     : otp_to_set_list,
                      'author_to_check': author_to_check_list,
                      'doi_to_check'   : doi_to_check_list,
                      'doi_otp_to_set' : doi_otp_to_set_list,
                     }

    return otps_hist_dict, doi_otp_history_df


def set_saved_otps(sub_params_list):
    """Attributes the OTPs from the history of the attributed OTPs 
    before submitting to the user the file for attributing the not yet
    attributed OTPs.

    First, it gets the history of the previously set OTPs through \
    the `_get_otps_history` internal function. 
    Then, if the level at which the OTPs are set by the user is the laboratory:

    1. The data of OTPs data given by laboratory of each department are set \
    through `set_lab_otps` function imported from the `bmfuncts.build_otps_info` module.
    2. The history of the attributed OTPs is used to build the files to be submitted \
    to the user through the `_set_saved_lab_otps` internal function.

    Otherwise, The level is kept to the department. Then, the history of the attributed \
    OTPs is used to build the files to be submitted to the user through \
    the `_set_saved_dept_otps` internal function.

    Args:
        sub_params_list (list): The list composed of the Institute \
        name (str), the org_tup (tup) that contains parameters of Institute \
        organization, the full path to working folder (path) and the 4 digits \
        year of the corpus (str).
    Returns:
        (str): End message giving the status of the OTPs attribution.
    """
    # Setting useful params values and lists from sub_params_list
    institute, org_tup, wf_path, corpus_year = sub_params_list
    save_otp_params_list = [wf_path, corpus_year]
    set_otp_params_list = sub_params_list[:-1]
    otp_level = org_tup[11]

    # Setting selected column names for using the saved history of attributed OTPs
    use_otps_cols_dic, _ = _set_use_otps_cols(institute, org_tup)

    # Setting useful lists of file parameters
    file_params_tup = _set_save_otp_file_params(save_otp_params_list)
    get_hist_file_params_list = list(file_params_tup)[2:]
    set_hist_file_params_list = list(file_params_tup)[0:2]
    kept_otps_file_path = file_params_tup[3]

    if kept_otps_file_path.is_file():
        otps_history_tup = _get_otps_history(get_hist_file_params_list,
                                             use_otps_cols_dic)
        if otp_level=="LAB":
            lab_otps_dict = set_lab_otps(set_otp_params_list)
            _set_saved_lab_otps(org_tup, otps_history_tup, use_otps_cols_dic,
                                set_hist_file_params_list, lab_otps_dict)
        else:
            _set_saved_dept_otps(org_tup, otps_history_tup, use_otps_cols_dic,
                                 set_hist_file_params_list)

        message = "Already set OTPs used"
    else:
        message = "No file of already set OTPs available"
    return message
