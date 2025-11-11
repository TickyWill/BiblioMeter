"""Module of functions for the consolidation of the publications-list 
in terms of attributing OTPs to each publication.

"""

__all__ = ['add_data_val',
           'add_otp',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import pandas as pd
from openpyxl import Workbook as openpyxl_Workbook

# Local imports
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
from bmfuncts.build_otps_info import set_lab_otps
from bmfuncts.format_files import build_data_val
from bmfuncts.format_files import format_page
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.format_files import get_col_letter
from bmfuncts.rename_cols import set_homonym_col_names
from bmfuncts.rename_cols import set_otp_col_names
from bmfuncts.use_homonyms import save_homonyms
from bmfuncts.useful_functs import concat_dfs


def _set_otps_homonyms_cols_dic(add_otp_params_list):
    """Builds a dict setting selected columns names for the process 
    of enhancing the file where homonyms have been resolved.

    This is done through the `set_homonym_col_names` and 
    the `set_otp_col_names` functions imported from the 
    `bmfuncts.rename_cols` module.
    
    Args:
        add_otp_params_list (list): The list composed of the Institute \
        name (str) and of the org_tup (tup) that contains parameters \
        of Institute organization.
    Returns:
        (dict): The built dict.
    """
    # Setting parameters values from 'add_otp_params_list'
    institute, org_tup = add_otp_params_list

    # Setting useful column names from homonyms file
    homonyms_col_dic = set_homonym_col_names(institute, org_tup)

    # Setting useful column names from OTPs file
    otp_col_dic = set_otp_col_names(institute, org_tup)

    otps_homonyms_cols_dic = {'pub_id_col'      : homonyms_col_dic['pub_id'],
                              'author_id_col'   : homonyms_col_dic['author_id'],
                              'mat_col'         : homonyms_col_dic['matricul'],
                              'lastname_col'    : homonyms_col_dic['last_name'],
                              'firstname_col'   : homonyms_col_dic['first_name'],
                              'author_type_col' : homonyms_col_dic['author_type'],
                              'dpt_col'         : homonyms_col_dic['dpt'],
                              'srv_col'         : homonyms_col_dic['serv'], 
                              'lab_col'         : homonyms_col_dic['lab'],
                              'fullname_col'    : otp_col_dic['institute_author'],
                              'inst_authors_col': otp_col_dic['institute_authors'],
                              'otp_dpt_col'     : "otp_dpt",
                             }

    return otps_homonyms_cols_dic


def add_data_val(ws, data_val, df_len, col_letter, xl_idx_base):
    """Adding a list-data-validation rule to each row of an openpyxl worksheet.
    
    Args:
        ws (openpyxl worksheet): Worksheet to be added with validation data list.
        data_val (openpyxl DataValidation): list-data-validation rule that can \
        be build through the `build_data_val` function imported from the \
        `bmfuncts.format_files` module.
        df_len (int): Number of rows of dataframe composing 'ws' (excludes column \
        headers). 
        col_letter (str): Letter (or a couple of letters) targeting the column
        to be added with validation data list in each cell.
        xl_idx_base (int): Base of row indexes in openpyxl objects.
    Returns:
        (openpyxl worksheet): Worksheet added with validation data list.
    """
    ws.add_data_validation(data_val)
    lab_df_rows_nb = df_len + 1
    for df_row_idx in range(1, lab_df_rows_nb):
        xl_row_idx = df_row_idx + xl_idx_base
        cell_name = col_letter + str(xl_row_idx)
        data_val.add(ws[cell_name])
    return ws


def _set_otps_dept_affil(org_tup, in_df, otps_homonyms_cols_dic):
    """Replaces the 'dpt_col' column of affiliation department by 'otp_dpt_col'
    new column filled with the department label to be used for the OTP attribution.

    Args:
        org_tup (tup): Contains Institute parameters.
        in_df (dataframe): Data of the publications list \
        with a row per Institute author and their attributes columns.
        otps_homonyms_cols_dic (dict): The dict built through \
        the `_set_otps_homonyms_cols_dic` internal function giving useful columns.
    returns:
        (tup): (End message (str), modified data (dataframe)).
    """
    # Internal functions
    def _set_dpt(_dpt_label_list):
        return lambda x: 1 if x in _dpt_label_list else 0

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting col name values from dept_cols_list
    dpt_col, otp_dpt_col = (otps_homonyms_cols_dic['dpt_col'],
                            otps_homonyms_cols_dic['otp_dpt_col'])

    # Removing possible spaces in dept names
    in_df[dpt_col] = in_df[dpt_col].apply(lambda x: x.strip())

    out_df = pd.DataFrame()
    for dept, dg in in_df.groupby(dpt_col):
        if dept not in dpt_list:
            for dpt in dpt_list:
                if dept in dpt_attributs_dict[dpt][bm_ig.DPT_LABEL_KEY]:
                    dg[otp_dpt_col] = dpt
        else:
            dg[otp_dpt_col] = dept
        out_df = concat_dfs([out_df, dg])

    # For each department adding a column containing 1 or 0
    # depending on if the author belongs or not to the department
    for dpt in dpt_list:
        dpt_label_list = dpt_attributs_dict[dpt][bm_ig.DPT_LABEL_KEY]
        out_df[dpt] = out_df[dpt_col]
        out_df[dpt] = out_df[dpt].apply(_set_dpt(dpt_label_list))

    # Reordering columns
    cols = list(out_df.columns)
    a, b = cols.index(dpt_col), cols.index(otp_dpt_col)
    cols[b], cols[a] = cols[a], cols[b]
    out_df = out_df[cols]

    # Dropping the initial 'dpt_col' column of affiliation department
    out_df = out_df.drop(columns=[dpt_col])

    # Renaming the 'otp_dpt_col' as 'dpt_col'
    out_df = out_df.rename(columns={otp_dpt_col: dpt_col})

    end_message = ("Column with department for OTPs attribution and columns "
                   "for each department of the institute added")
    return end_message, out_df


def _add_authors_name_list(org_tup, in_df, otps_homonyms_cols_dic):
    """Adds two columns to the dataframe got from the Excel file pointed by 'in_path'.

    The columns contain respectively the full name of each author as "NAME, Firstname" 
    and the institute co-authors list with attributes of each author in a string as follows:

        - "NAME1, Firstname1 (matricule,job type,department affiliation, \
        service affiliation,laboratoire affiliation);
        - NAME2, Firstname2 (matricule,job type,department affiliation, \
        service affiliation,laboratoire affiliation);
        - ...".

    Args:
        org_tup (tup): Contains Institute parameters.
        in_df (dataframe): Data of the publications list \
        with a row per Institute author and their attributes columns.
        otps_homonyms_cols_dic (dict): The dict built through \
        the `_set_otps_homonyms_cols_dic` internal function giving useful columns.
    Returns:
        (tup): (End message (str), the data of the publication list \
        added with the new columns (dataframe)).
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

    # Setting useful col names
    use_keys_list = list(otps_homonyms_cols_dic.keys())[:-1]
    (pub_id_col, author_id_col, mat_col, lastname_col, firstname_col,
     author_type_col, dpt_col, srv_col, lab_col,
     fullname_col, inst_authors_col) = [otps_homonyms_cols_dic[key] for key in use_keys_list]

    # Adding the column 'fullname_col' that will be used to create the authors fullname list
    in_df[firstname_col] = in_df[firstname_col].apply(lambda x: x.capitalize())
    in_df[fullname_col] = in_df[lastname_col] + ', ' + in_df[firstname_col]

    out_df = pd.DataFrame()
    for _, pub_id_df in in_df.groupby(pub_id_col):

        authors_tup_list = sorted(list(set(zip(pub_id_df[author_id_col],
                                               pub_id_df[fullname_col],
                                               pub_id_df[mat_col],
                                               pub_id_df[author_type_col],
                                               pub_id_df[dpt_col],
                                               pub_id_df[srv_col],
                                               pub_id_df[lab_col]))))

        authors_str_list = [(f'{x[1]} ({x[2]},'
                             f'{x[3]},{_get_dpt_key(x[4])},{x[5]},{x[6]})')
                            for x in authors_tup_list]
        authors_full_str = "; ".join(authors_str_list)
        pub_id_df[inst_authors_col] = authors_full_str
        out_df = concat_dfs([out_df, pub_id_df])
    out_df.fillna('')

    end_message = "Column with co-authors list added"
    return end_message, out_df


def _enhance_homonyms_file(add_otp_params_list, in_path):
    """Enhances the data got from the Excel file where homonyms 
    have been solved by the user by checking department 
    attribution and adding useful columns.

    First, the columns names used to enhance the data for OTPs attribution 
    by the user are set through the '_set_otps_homonyms_cols_dic' internal function. 
    Then, a new column with the department to be used for OTPs attribution 
    is added to the data through the `_set_otps_dept_affil` internal function. 
    Finally, useful columns with authors names list are added to the data through 
    the `_add_authors_name_list` internal function. 

    Args:
        add_otp_params_list (list): The list composed of the Institute \
        name (str) and of the org_tup (tup) that contains parameters \
        of Institute organization.
        in_path (path): Full path to the file where homonyms have been solved.
    Returns:
        (dataframe): The enhanced data. 
    """
    # Setting parameters value from add_otp_params_list
    _, org_tup = add_otp_params_list

    # Setting useful column names
    otps_homonyms_cols_dic = _set_otps_homonyms_cols_dic(add_otp_params_list)

    # Getting data where homonymies have been solved
    solved_homonymies_df = pd.read_excel(in_path)
    solved_homonymies_df = solved_homonymies_df.fillna('')

    # Setting the affiliation department for OTPs attribution
    end_message, new_solved_homonymies_df = _set_otps_dept_affil(org_tup, solved_homonymies_df,
                                                                 otps_homonyms_cols_dic)
    print('\n ',end_message)

    # Adding a column with a list of the authors in the file where homonymies
    # have been solved and pointed by in_path
    end_message, final_solved_homonymies_df = _add_authors_name_list(org_tup,
                                                                     new_solved_homonymies_df,
                                                                     otps_homonyms_cols_dic)
    print('\n ',end_message)

    return final_solved_homonymies_df


def _set_add_otps_cols_dic(add_otp_params_list):
    """Builds a dict setting selected columns names for the process 
    of OTPs attribution.

    This is done through the `set_otp_col_names` function imported 
    from the `bmfuncts.rename_cols` module.
    
    Args:
        add_otp_params_list (list): The list composed of the Institute \
        name (str) and of the org_tup (tup) that contains parameters \
        of Institute organization.
    Returns:
        (tup): The built dict and the full list of final column names \
        got from the `set_otp_col_names` function.
    """
    institute, org_tup = add_otp_params_list
    # Setting useful column names
    otp_col_dic = set_otp_col_names(institute, org_tup)

    # Setting useful col names

    add_otps_cols_dic = {'pub_id_col'   : otp_col_dic['pub_id'],
                         'author_id_col': otp_col_dic['author_id'], 
                         'dpt_col'      : otp_col_dic['dpt'],
                         'srv_col'      : otp_col_dic['serv'],
                         'lab_col'      : otp_col_dic['lab'],
                         'otp_col'      : otp_col_dic['otp_list'],
                         'otp_lab_col'  : 'otp_lab'
                        }

    otp_base_col_list = list(otp_col_dic.values())
    return add_otps_cols_dic, otp_base_col_list


def _save_dpt_otp_file(dpt, save_otp_cols_tup, dpt_df, dpt_otp_list, xl_dpt_path):
    """Creates an openpyxl file to allow the user to set the OTP attribute   
    of the publications for the Institute department labelled 'dpt'.

    First, a validation list and a list-data-validation rule are defined 
    based on the list of OTPs of the department given by 'dpt_otp_list' list 
    and through the `build_data_val` function imported from the 
    `bmfuncts.format_files` module. 
    A new column named 'otp_col' is added to the dataframe 'dpt_df' 
    with values set to the validation list. 
    The dataframe columns are renamed using 'add_otps_cols_tup'. 
    Then the dataframe is formatted as an openpyxl workbook through 
    the `format_page` function imported from `bmfuncts.format_files` 
    module. 
    The letter targeting the 'otp_col' column in an openpyxl object
    is got through the `get_col_letter` function imported from 
    the `bmfuncts.format_files` module. 
    The list-data-validation rule is added to each cell of the column
    'otp_col' through the `add_data_val` function of this module. 
    Finally, the built openpyxl workbook is saved using the full path 
    'xl_dpt_path'.

    Arg:
        dpt (str): Institute department.
        save_otp_cols_tup (tup): (The name (str) of the OTPs column, \
        The full list of final column names of OTPs data).
        dpt_df (dataframe): The publications-list dataframe of the 'dpt' department.
        dpt_otp_list (list): List of Institute departments (str).
        xl_dpt_path (path): Full path to the file for setting publication OTP.
    """
    # Setting num of first col and first row in EXCEL files
    xl_idx_base = bm_pg.XL_INDEX_BASE

    # Setting useful col names and cols list
    otp_col, otp_base_col_list = save_otp_cols_tup

    # Building validation list of OTPs for 'dpt' department
    validation_list, data_val = build_data_val(dpt_otp_list)

    # Adding a column containing OTPs of 'dpt' department
    dpt_df[otp_col] = validation_list

    # Renaming the columns
    dpt_df = dpt_df.reindex(columns=otp_base_col_list)

    # Formatting 'dpt_df' as openpyxl workbook
    dpt_df_title = bm_pg.DF_TITLES_LIST[2]
    wb, ws = format_page(dpt_df, dpt_df_title)
    ws.title = bm_pg.OTP_SHEET_NAME_BASE + " " +  dpt

    # Activating the validation data list in all cells of the OTPs column
    dpt_df_len = len(dpt_df)
    if dpt_df_len:
        # Getting the column letter for the OTPs column
        otp_col_letter = get_col_letter(dpt_df, otp_col, xl_idx_base)
        _ = add_data_val(ws, data_val, dpt_df_len, otp_col_letter,
                         xl_idx_base)
    # Saving the workbook
    wb.save(xl_dpt_path)


def _add_dept_otp(add_otp_params_list, in_path, out_path, out_file_base, add_otps_cols_tup):
    """Creates the files for setting OTP attribute of publications by the user 
    for the Institute departments.

    First, useful columns are added to the dataframe got from the Excel file 
    where homonyms have been solved by the user and pointed by 'in_path' path 
    through the `_add_authors_name_list` internal function. 
    Then, for each department, a sub_dataframe is extracted selecting rows 
    of publications where at least one author is affiliated to the department. 
    Each sub-dataframe is saved through the `_save_dpt_otp_file` internal function.

    Args:
        add_otp_params_list (list): The list composed of the Institute name (str) and \
        the org_tup (tup) that contains parameters of Institute organization.
        in_path (path): Full path to the file where homonyms have been solved.
        out_path (path): Full path to the files for setting OTPs attributes by the user.
        out_file_base (str): Base for building created-files names.
        add_otps_cols_tup (tup): (Selected columns names (dict) for the OTPs-attribution \
        process and the full list of final column names of OTPs data as set \
        through the `_set_add_otps_cols_dic` internal function).
    Returns:
        (str): End message recalling out_path.
    """
    # Set parameters value from add_otp_params_list
    _, org_tup = add_otp_params_list

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting useful col names and cols list
    add_otps_cols_dic, otp_base_col_list = add_otps_cols_tup
    otps_col_keys = ['pub_id_col', 'author_id_col', 'dpt_col']
    (pub_id_col, author_id_col,
     dpt_col) = [add_otps_cols_dic[key] for key in otps_col_keys]
    save_otp_cols_tup = (add_otps_cols_dic['otp_col'], otp_base_col_list)

    # Enhancing file where homonymies have been solved by the user
    init_df = _enhance_homonyms_file(add_otp_params_list, in_path)

    # Building 'out_df' out of 'init_df' with a row per pub_id
    # 1 or 0 is assigned to each department column depending
    # on if at least one co-author is a member of this department,
    # the detailed information is related to the first author only
    out_df = pd.DataFrame()
    for _, dg in init_df.groupby(pub_id_col):
        dg = dg.sort_values(by=[author_id_col])
        for dpt in dpt_list:
            x = dg[dpt].any().astype(int)
            dg[dpt] = x
        out_df = concat_dfs([out_df, dg.iloc[:1]])

    # Removing possible spaces in dept name
    out_df[dpt_col] = out_df[dpt_col].apply(lambda _x: _x.strip())

    # Configuring an Excel file per department with the list of OTPs
    for dpt in sorted(dpt_list):
        # Setting dpt_df with only pub_ids for which the first author
        # is from the 'dpt' department
        filtre_dpt = False
        for dpt_value in dpt_attributs_dict[dpt][bm_ig.DPT_LABEL_KEY]:
            filtre_dpt = filtre_dpt | (out_df[dpt_col]==dpt_value)
        dpt_df = out_df[filtre_dpt].copy()

        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = dpt_attributs_dict[dpt][bm_ig.DPT_OTP_KEY]

        # Setting the full path of the EXCEl file for the 'dpt' department
        otp_file_name_dpt = f'{out_file_base}_{dpt}.xlsx'
        xl_dpt_path = out_path / Path(otp_file_name_dpt)

        # Adding a column with validation list for OTPs and saving the file
        _save_dpt_otp_file(dpt, save_otp_cols_tup, dpt_df, dpt_otp_list,
                           xl_dpt_path)


def _save_dpt_lab_otp_file(institute, dpt, save_otp_cols_tup, dpt_df,
                           dpt_otp_dict, xl_dpt_path):
    """Creates an openpyxl file to allow the user to set the OTP attribute   
    of the publications for each laboratory of a department of the Institute. 

    First, a validation list and a list-data-validation rule are defined 
    based on the list of OTPs of the laboratory given by 'lab_otp_list' list 
    and through the `build_data_val` function imported from the 
    `bmfuncts.format_files` module. 
    A new column named 'otp_col' is added to the dataframe 'otp_lab_df' 
    with values set to the validation list. 
    The dataframe columns are renamed using 'add_otps_cols_tup'. 
    Then the dataframe is formatted as a multisheet openpxl workbook through 
    the `format_wb_sheet` function imported from `bmfuncts.format_files` 
    module. 
    The letter targeting the 'otp_col' column in an openpyxl object
    is got through the `get_col_letter` function imported from 
    the `bmfuncts.format_files` module. 
    The list-data-validation rule is added to each cell of the column
    'otp_col' through the `add_data_val` function of this module. 
    Finally, the built openpyxl workbook is saved using the full path 
    'xl_dpt_path'.

    Arg:
        institute (str): Institute name. 
        dpt (str): The department label.
        save_otp_cols_tup (tup): (The names (list of str) of the OTPs column \
        and the column of lab names to be used for the selection \
        of the OTPs validation list, The full list of final column names of OTPs data).
        dpt_df (dataframe): The publications-list dataframe of a department of \
        the Institute.
        dpt_otp_dict (dict): Dict keyed by lab-names and valued by lab-OTPs lists.
        xl_dpt_path (path): Full path to the file for setting publication OTP.
    """
    # Setting num of first col and first row in EXCEL files
    xl_idx_base = bm_pg.XL_INDEX_BASE

    # Setting useful col names and cols list
    save_otp_cols_list, otp_base_col_list = save_otp_cols_tup
    otp_col, otp_lab_col = save_otp_cols_list

    # Creating workbook
    wb = openpyxl_Workbook()

    # Activating the validation data list in all cells of the OTPs column
    if len(dpt_df):
        first = True
        for otp_lab, otp_lab_df in dpt_df.groupby(otp_lab_col):
            # Setting a validation list per lab
            lab_otp_list = dpt_otp_dict[otp_lab]
            validation_list, data_val = build_data_val(lab_otp_list)

            # Adding a column containing OTPs of 'otp_lab' laboratory
            otp_lab_df[otp_col] = validation_list

            # Renaming the columns
            otp_lab_df = otp_lab_df.reindex(columns=otp_base_col_list)

            # Formatting 'otp_lab_df' as a new sheet of the 'wb'
            # multisheet openpyxl workbook
            sheet_name = otp_lab
            otp_lab_df_title = bm_pg.DF_TITLES_LIST[2]
            wb = format_wb_sheet(sheet_name, otp_lab_df,
                                 otp_lab_df_title, wb, first)
            ws = wb.active

            # Getting the column letter for the OTPs column
            otp_col_letter = get_col_letter(otp_lab_df, otp_col, xl_idx_base)

            # Adding a validation data list
            _ = add_data_val(ws, data_val, len(otp_lab_df), otp_col_letter,
                             xl_idx_base)
            first = False
    else:
        # Renaming the columns
        dpt_df = dpt_df.rename(columns={otp_lab_col:otp_col})
        dpt_df = dpt_df.reindex(columns=otp_base_col_list)

        # Formatting 'dpt_df' as openpyxl workbook
        dpt_df_title = bm_pg.DF_TITLES_LIST[2]
        wb, ws = format_page(dpt_df, dpt_df_title)
        dpt_label = dpt
        if dpt=="DIR":
            dpt_label = "(" + institute.upper() + ")"
        ws.title = "(full-" + dpt_label + ")"

    # Saving the workbook
    wb.save(xl_dpt_path)


def _set_otp_lab(add_otp_params_list, cols_list, dpt_labs_list, lab_df, lab):
    """Sets the laboratory name to be used for the determination 
    of the OTPs list of the 'lab' laboratory.

    Arg:
        add_otp_params_list (list): The list composed of the Institute name (str) and \
        the org_tup (tup) that contains parameters of Institute organization. 
        cols_list (list ): The list composed of the columns names (str) of \
        departments and services.
        dpt_labs_list (list): The list of the laboratories labels of the department.
        lab_df (dataframe): The publications-list data of a laboratory of \
        a department of the Institute.
        lab (str): The laboratory label.
    Returns:
        (str): The laboratory name to be used for setting the OTPs list.
    """
    # Set parameters value from add_otp_params_list
    institute, org_tup = add_otp_params_list
    dpt_col, srv_col = cols_list

    # Setting institute parameters
    nolab_depts = org_tup[16]

    otp_lab = lab
    serv = lab_df[srv_col].to_list()[0]
    dept = lab_df[dpt_col].to_list()[0]
    full_serv = "(" + serv + ")"

    if dept=="DIR":
        full_dept = "(full-(" + institute.upper() + "))"
    else:
        full_dept = "(full-" + dept + ")"

    if dept in nolab_depts:
        otp_lab = full_dept

    if "((" in lab:
        if institute.upper() not in lab:
            otp_lab = lab[1:-1]
        else:
            otp_lab = full_dept

    if otp_lab not in dpt_labs_list:
        if full_serv in dpt_labs_list:
            otp_lab = full_serv
        else:
            otp_lab = full_dept

    return otp_lab


def _build_otp_dept_df(add_otp_params_list, build_otp_cols_list, dpt_attributs_dict,
                       dpt_labs_list, full_df, dpt):
    """Builds a data extracted from 'full_df' data by selecting rows 
    of publications where at least one author is affiliated to the 
    given department.
    
    A column is added with the lab to be used for the determination 
    of the OTPs list through the `_set_otp_lab` internal function.

    Args:
        add_otp_params_list (list): The list composed of the Institute name (str) and \
        the org_tup (tup) that contains parameters of Institute organization.
        build_otp_cols_list (list ): The names (str) of the departments column, \
        the services column, the laboratories column and the column of laboratories \
        names to be used for the selection of the OTPs validation list.
        dpt_attributs_dict (dict): the dict keyed by departments of the Institute \
        and valued by the list of possible labels of each department.
        dpt_labs_list (list): The list of the laboratories labels of the department.
        full_df (dataframe): The publications data of one row per publication ID \
        with 1 or 0 assigned to each department column depending on if at least \
        one co-author is a member of this department and with the detailed information \
        related to the first author only
        dpt (str): The department label.
    Returns:
        (dataframe): The built data.
    """
    # Setting useful col names and cols list
    dpt_col, srv_col, lab_col, otp_lab_col = build_otp_cols_list
    sub_cols_list = [dpt_col, srv_col]

    # Setting dpt_df with only pub_ids for which the first author
    # is from the 'dpt' department
    filtre_dpt = False
    for dpt_value in dpt_attributs_dict[dpt][bm_ig.DPT_LABEL_KEY]:
        filtre_dpt = filtre_dpt | (full_df[dpt_col]==dpt_value)
    dpt_df = full_df[filtre_dpt].copy()

    # Adding column for lab names to be used for OTPs list setting
    usecols = list(dpt_df.columns) + [otp_lab_col]
    otp_dpt_df = pd.DataFrame(columns=usecols)
    if len(dpt_df):
        for lab, lab_df in dpt_df.groupby(lab_col):
            otp_lab = _set_otp_lab(add_otp_params_list, sub_cols_list,
                                   dpt_labs_list, lab_df, lab)
            lab_df[otp_lab_col] = otp_lab
            otp_dpt_df = concat_dfs([otp_dpt_df, lab_df])
    return otp_dpt_df


def _set_full_pub_df(init_pub_df, add_otps_cols_dic, dpt_list):
    """Adds the publications data of one row per publication ID 
    with 1 or 0 assigned to each department column depending
    on if at least one co-author is a member of this department and with
    the detailed information related to the first author only.

    Args:
        init_pub_df (dataframe): The initial publications data \
        with one row per publication ID.
        add_otps_cols_dic (dict): Selected columns names for the OTPs-attribution \
        process as set through the `_set_add_otps_cols_dic` internal function.
        dpt_list (list): The departments names of the Institute \
        used as column names.
    Returns:
        (dataframe): The modified data of publications.
    """
    # Setting col names to be used
    col_keys = ['pub_id_col', 'author_id_col', 'dpt_col']
    pub_id_col, author_id_col, dpt_col = [add_otps_cols_dic[key] for key in col_keys]

    full_pub_df = pd.DataFrame()
    for _, dg in init_pub_df.groupby(pub_id_col):
        dg = dg.sort_values(by=[author_id_col])
        for dpt in dpt_list:
            x = dg[dpt].any().astype(int)
            dg[dpt] = x
        full_pub_df = concat_dfs([full_pub_df, dg.iloc[:1]])

    # Removing possible spaces in dept name
    full_pub_df[dpt_col] = full_pub_df[dpt_col].apply(lambda _x: _x.strip())
    return full_pub_df


def _add_lab_otp(add_otp_params_list, in_path, out_path, out_file_base,
                 add_otps_cols_tup, lab_otps_dict):
    """Creates the files for setting OTP attribute of publications by the user 
    for each of the laboratories of the Institute departments.

    First, useful columns are added to the dataframe got from the Excel file 
    where homonyms have been solved by the user and pointed by 'in_path' path 
    through the `_enhance_homonyms_file` internal function. 
    Then, for each department, a sub_dataframe is extracted selecting rows 
    of publications where at least one author is affiliated to the department 
    through the `_build_otp_dept_df` internal function.
    Each sub-dataframe is saved through the `_save_dpt_lab_otp_file` internal 
    function.

    Args:
        add_otp_params_list (list): The list composed of the Institute name (str) and \
        the org_tup (tup) that contains parameters of Institute organization.
        in_path (path): Full path to the file where homonyms have been solved.
        out_path (path): Full path to the files for setting OTPs attributes by the user.
        out_file_base (str): Base for building created-files names.
        add_otps_cols_tup (tup): (Selected columns names (dict) for the OTPs-attribution \
        process and the full list of final column names of OTPs data as set \
        through the `_set_add_otps_cols_dic` internal function).
        lab_otps_dict (dict): OTPs hierarchical dict keyed by departments \
        and valued by dicts keyed by labs and valued by OTPs lists.
    """
    # Set parameters value from 'add_otp_params_list'
    institute, org_tup = add_otp_params_list

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting useful col names and cols list
    add_otps_cols_dic, otp_base_col_list = add_otps_cols_tup
    col_keys = ['dpt_col', 'srv_col', 'lab_col', 'otp_lab_col']
    build_otp_cols_list = [add_otps_cols_dic[key] for key in col_keys]
    save_otp_cols_list = [add_otps_cols_dic['otp_col'],
                          add_otps_cols_dic['otp_lab_col']]
    save_otp_cols_tup = (save_otp_cols_list, otp_base_col_list)

    # Enhancing file where homonymies have been solved by the user
    init_pub_df = _enhance_homonyms_file(add_otp_params_list, in_path)

    # Building 'full_pub_df' data out of 'init_pub_df' data.
    # 1 or 0 is assigned to each department column depending
    # on if at least one co-author is a member of this department.
    # The detailed information is related to the first author only.
    full_pub_df = _set_full_pub_df(init_pub_df, add_otps_cols_dic, dpt_list)

    # Configuring an Excel file per department with the list of OTPs
    for dpt in sorted(dpt_list):
        # Setting the dict of list of OTPs for the 'dpt' department
        dpt_otp_dict = lab_otps_dict[dpt]

        # Setting list of the labs of the department
        dpt_labs_list = dpt_otp_dict.keys()

        # Setting the data with pub info and list of OTPs
        # for the 'dpt' department
        otp_dpt_df = _build_otp_dept_df(add_otp_params_list, build_otp_cols_list,
                                        dpt_attributs_dict, dpt_labs_list,
                                        full_pub_df, dpt)

        # Setting the full path of the EXCEl file for the 'dpt' department
        otp_file_name_dpt = f'{out_file_base}_{dpt}.xlsx'
        xl_dpt_path = out_path / Path(otp_file_name_dpt)

       # Adding a column with validation list for OTPs and saving the file
        _save_dpt_lab_otp_file(institute, dpt, save_otp_cols_tup, otp_dpt_df,
                               dpt_otp_dict, xl_dpt_path)


def add_otp(sub_params_list, in_path, out_path, out_file_base):
    """Creates the files for setting OTP attribute of publications by the user 
    for the Institute departments either among OTPs list at department level 
    or lab level.

    This done after saving the resolved homonyms through `save_homonyms` function \
    imported from `bmfuncts.use_homonyms` module. 
    Depending on the specified level: 
    - The files are created through the `_add_dept_otp` or `_add_lab_otp` \
    internal functions. 
    - The OTPs info are got through 'org_tup' parameter or `set_lab_otps` \
    function imported from `bmfuncts.build_otps_info` module.

    Args:
        sub_params_list (list): The list composed of the Institute \
        name (str), the org_tup (tup) that contains parameters of Institute \
        organization, the full path to working folder (path) and the 4 digits \
        year of the corpus (str).
        in_path (path): Full path to the file where homonyms have been solved.
        out_path (path): Full path to the files for setting OTPs attributes by the user.
        out_file_base (str): Base for building created-files names.
    Returns:
        (str): end message recalling out_path.
    """
    # Saving the homonyms resolved by the user
    end_message = save_homonyms(sub_params_list)
    print('\n',end_message)

    # Setting useful params values and lists from sub_params_list
    set_otp_params_list = sub_params_list[:-1]
    add_otp_params_list = sub_params_list[0:2]
    org_tup = sub_params_list[1]

    # Setting the selected columns of OTPs data for OTPs-attribution process
    add_otps_cols_tup = _set_add_otps_cols_dic(add_otp_params_list)

    # Setting institute parameters
    otp_level = org_tup[11]

    if otp_level=="LAB":
        lab_otps_dict = set_lab_otps(set_otp_params_list)
        _add_lab_otp(add_otp_params_list, in_path, out_path, out_file_base,
                     add_otps_cols_tup, lab_otps_dict)
    else:
        _add_dept_otp(add_otp_params_list, in_path, out_path, out_file_base,
                      add_otps_cols_tup)

    end_message = ("Files for setting publication OTPs per department "
                   f"saved in folder: \n  '{out_path}'")
    return end_message
