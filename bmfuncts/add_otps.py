"""Module of functions for the consolidation of the publications-list 
in terms of attributing OTPs to each publication.

"""

__all__ = ['add_data_val',
           'add_otp',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl import Workbook as openpyxl_Workbook

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.institute_globals as ig
import bmfuncts.pub_globals as pg
from bmfuncts.build_otps_info import set_lab_otps
from bmfuncts.format_files import build_data_val
from bmfuncts.format_files import format_page
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.format_files import get_col_letter
from bmfuncts.format_files import set_base_keys_list
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.rename_cols import set_otp_col_names
from bmfuncts.useful_functs import concat_dfs


def add_data_val(ws, data_val, df_len, col_letter, xl_idx_base):
    """Adding a list-data-validation rule to each row of an openpyxl worksheet.
    
    Args:
        ws (openpyxl worksheet): Worksheet to be added with validation data list.
        data_val (openpyxl DataValidation): list-data-validation rule that can \
        be build through the `build_data_val` function imported from the \
        `bmfuncts.format_files` module.
        df_len (int): Number of rows of dataframe composing 'ws' (excludes column \
        headers). 
        col_letter (str): Letter (or couple of letters) targetting the column
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


def _set_otps_dept_affil(org_tup, in_df, otp_col_dict, otp_dept_col, dpt_label):
    # Internal functions
    def _set_dpt(dpt_label_list):
        return lambda x: 1 if x in dpt_label_list else 0

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]
    dpt_list = list(dpt_attributs_dict.keys())

    dpt_col = otp_col_dict['dpt']

    out_df = pd.DataFrame()
    for dept, dg in in_df.groupby(dpt_col):
        if dept not in dpt_list:
            for dpt in dpt_list:
                if dept in dpt_attributs_dict[dpt][dpt_label]:
                    dg[otp_dept_col] = dpt
        else:
            dg[otp_dept_col] = dept
        out_df = concat_dfs([out_df, dg])

    # For each department adding a column containing 1 or 0
    # depending on if the author belongs or not to the department
    for dpt in dpt_list:
        dpt_label_list = dpt_attributs_dict[dpt][dpt_label]
        out_df[dpt] = out_df[dpt_col]
        out_df[dpt] = out_df[dpt].apply(_set_dpt(dpt_label_list))

    # Reordering columns
    cols = list(out_df.columns)
    a, b = cols.index(dpt_col), cols.index(otp_dept_col)
    cols[b], cols[a] = cols[a], cols[b]
    out_df = out_df[cols]

    # Droping the initial 'dpt_col' column of affiliation department
    out_df = out_df.drop(columns=[dpt_col])

    # Renaming the 'otp_dept_col' as 'dpt_col'
    out_df = out_df.rename(columns={otp_dept_col: dpt_col})

    end_message = ("Column with department for OTPs atribution and columns "
                   "for each department of the institute added")
    return end_message, out_df


def _add_authors_name_list(institute, org_tup, in_df):
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
    pub_id_alias = bm_col_rename_dic[bp.COL_NAMES['pub_id']]
    idx_authors_alias = bm_col_rename_dic[bp.COL_NAMES['authors'][1]]
    nom_alias = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['name']]
    prenom_alias = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['first_name']]
    matricule_alias = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['matricule']]
    full_name_alias = bm_col_rename_dic[pg.COL_NAMES_BONUS['nom prénom'] + institute]
    author_type_alias = bm_col_rename_dic[pg.COL_NAMES_BONUS['author_type']]
    full_name_list_alias = bm_col_rename_dic[pg.COL_NAMES_BONUS['nom prénom liste'] + institute]
    dept_alias = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['dpt']]
    serv_alias = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['serv']]
    lab_alias = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['lab']]

    # Adding the column 'full_name_alias' that will be used to create the authors fullname list
    in_df[prenom_alias] = in_df[prenom_alias].apply(lambda x: x.capitalize())
    in_df[full_name_alias] = in_df[nom_alias] + ', ' + in_df[prenom_alias]

    out_df = pd.DataFrame()
    for _, pub_id_df in in_df.groupby(pub_id_alias):

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
        out_df = concat_dfs([out_df, pub_id_df])
    out_df.fillna('')

    end_message = "Column with co-authors list added"
    return end_message, out_df


def _enhance_homonyms_file(institute, org_tup, in_path):
    """Enhances the file of resolved homonymies by checking department attribution 
    and adding a column for the department to be used for OTPs attribution.

    First, useful columns are added to the dataframe got from the Excel file 
    where homonyms have been solved by the user and pointed by 'in_path' path 
    through the `_add_authors_name_list` internal function. 

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        in_path (path): Full path to the file where homonyms have been solved.
    Returns:
        (dataframe): 
    """
    # Setting OTP df column names
    otp_col_dict = set_otp_col_names(institute, org_tup)
    dpt_alias = otp_col_dict['dpt']

    # Setting useful alias
    dpt_label_alias = ig.DPT_LABEL_KEY

    # Setting name of the column for setting the department to be used for OTPs attribution
    otp_dept_col = "otp_dept"

    solved_homonymies_df = pd.read_excel(in_path)
    solved_homonymies_df = solved_homonymies_df.fillna('')

    # Removing possible spaces in dept name
    solved_homonymies_df[dpt_alias] = solved_homonymies_df[dpt_alias].apply(lambda x: x.strip())

    # Setting the affiliation department for OTPs attribution in 'otp_dept_col' column
    end_message, new_solved_homonymies_df = _set_otps_dept_affil(org_tup, solved_homonymies_df,
                                                                 otp_col_dict, otp_dept_col,
                                                                 dpt_label_alias)
    print('\n ',end_message)

    # Adding a column with a list of the authors in the file where homonymies
    # have been solved and pointed by in_path
    end_message, final_solved_homonymies_df = _add_authors_name_list(institute, org_tup,
                                                                     new_solved_homonymies_df)
    print('\n ',end_message)

    return final_solved_homonymies_df


def _save_dpt_otp_file(institute, org_tup, dpt, dpt_df, dpt_otp_list,
                       otp_alias, xl_dpt_path, otp_col_list):
    """Creates an openpyxl file to allow the user to set the OTP attribute   
    of the publications for the Institute department labelled 'dpt'.

    First, a validation list and a list-data-validation rule are defined 
    based on the list of OTPs of the department given by 'dpt_otp_list' list 
    and through the `build_data_val` function imported from the 
    `bmfuncts.format_files` module. 
    A new column named 'otp_alias' is added to the dataframe 'dpt_df' 
    with values set to the validation list. 
    The dataframe columns are renamed using 'otp_col_list'. 
    Then the dataframe is formatted as an openpyxl workbook through 
    the `format_page` function imported from `bmfuncts.format_files` 
    module. 
    The letter targetting the 'otp_alias' column in an openpyxl object 
    is got through the `get_col_letter` function imported from 
    the `bmfuncts.format_files` module. 
    The list-data-validation rule is added to each cells of the column 
    'otp_alias' through the `add_data_val` function of this module. 
    Finally, the built openpyxl workbook is saved using the full path 
    'xl_dpt_path'.

    Arg:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        dpt (str): Institute department.
        dpt_df (dataframe): The publications-list dataframe of the 'dpt' department.
        dpt_otp_list (list): List of Institute departments (str).
        otp_alias (str): OTPs column name.
        xl_dpt_path (path): Full path to the file for setting publication OTP.
        otp_col_list (list): Column names for rename of columns of the file created \
        for setting publications OTP.
    """
    # Setting num of first col and first row in EXCEL files
    xl_idx_base = pg.XL_INDEX_BASE

    # Building validation list of OTPs for 'dpt' department
    validation_list, data_val = build_data_val(dpt_otp_list)

    # Adding a column containing OTPs of 'dpt' department
    dpt_df[otp_alias] = validation_list

    # Renaming the columns
    dpt_df = dpt_df.reindex(columns=otp_col_list)

    # Formatting 'dpt_df' as openpyxl workbook
    attr_keys_list = set_base_keys_list(institute, org_tup)
    dpt_df_title = pg.DF_TITLES_LIST[2]
    wb, ws = format_page(dpt_df, dpt_df_title, attr_keys_list=attr_keys_list)
    ws.title = pg.OTP_SHEET_NAME_BASE + " " +  dpt

    # Activating the validation data list in all cells of the OTPs column
    dpt_df_len = len(dpt_df)
    if dpt_df_len:
        # Getting the column letter for the OTPs column
        otp_col_letter = get_col_letter(dpt_df, otp_alias, xl_idx_base)
        ws = add_data_val(ws, data_val, dpt_df_len, otp_col_letter,
                          xl_idx_base)
    # Saving the workbook
    wb.save(xl_dpt_path)


def _add_dept_otp(institute, org_tup, in_path, out_path, out_file_base):
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
        (str): End message recalling out_path.
    """
    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting useful column names
    otp_col_dic = set_otp_col_names(institute, org_tup)
    otp_col_list = list(otp_col_dic.values())

    # Setting useful aliases
    pub_id_alias = otp_col_dic['pub_id']
    idx_author_alias = otp_col_dic['author_id']
    dpt_alias = otp_col_dic['dpt']
    otp_alias = otp_col_dic['otp_list']
    dpt_label_alias = ig.DPT_LABEL_KEY
    dpt_otp_alias = ig.DPT_OTP_KEY

    # Enhancing file where homonymies have been solved by the user
    init_df = _enhance_homonyms_file(institute, org_tup, in_path)

    # Building 'out_df' out of 'init_df' with a row per pub_id
    # 1 or 0 is assigned to each department column depending
    # on if at least one co-author is a member of this department,
    # the detailed information is related to the first author only
    out_df = pd.DataFrame()
    for _, dg in init_df.groupby(pub_id_alias):
        dg = dg.sort_values(by=[idx_author_alias])
        for dpt in dpt_list:
            x = dg[dpt].any().astype(int)
            dg[dpt] = x
        out_df = concat_dfs([out_df, dg.iloc[:1]])

    # Removing possible spaces in dept name
    out_df[dpt_alias] = out_df[dpt_alias].apply(lambda x: x.strip())

    # Configuring an Excel file per department with the list of OTPs
    for dpt in sorted(dpt_list):
        # Setting dpt_df with only pub_ids for which the first author
        # is from the 'dpt' department
        filtre_dpt = False
        for dpt_value in dpt_attributs_dict[dpt][dpt_label_alias]:
            filtre_dpt = filtre_dpt | (out_df[dpt_alias]==dpt_value)
        dpt_df = out_df[filtre_dpt].copy()

        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = dpt_attributs_dict[dpt][dpt_otp_alias]

        # Setting the full path of the EXCEl file for the 'dpt' department
        otp_file_name_dpt = f'{out_file_base}_{dpt}.xlsx'
        xl_dpt_path = out_path / Path(otp_file_name_dpt)

        # Adding a column with validation list for OTPs and saving the file
        _save_dpt_otp_file(institute, org_tup, dpt, dpt_df, dpt_otp_list,
                           otp_alias, xl_dpt_path, otp_col_list)


def _save_dpt_lab_otp_file(institute, org_tup, dpt_df, dpt_otp_dict,
                           xl_dpt_path, otp_col_dic, otp_lab_name_col, dpt):
    """Creates an openpyxl file to allow the user to set the OTP attribute   
    of the publications for each laboratory of a department of the Institute. 

    First, a validation list and a list-data-validation rule are defined 
    based on the list of OTPs of the laboratory given by 'lab_otp_list' list 
    and through the `build_data_val` function imported from the 
    `bmfuncts.format_files` module. 
    A new column named 'otp_alias' is added to the dataframe 'otp_lab_df' 
    with values set to the validation list. 
    The dataframe columns are renamed using 'otp_col_list'. 
    Then the dataframe is formatted as a multisheet openpxl workbook through 
    the `format_wb_sheet` function imported from `bmfuncts.format_files` 
    module. 
    The letter targetting the 'otp_alias' column in an openpyxl object 
    is got through the `get_col_letter` function imported from 
    the `bmfuncts.format_files` module. 
    The list-data-validation rule is added to each cells of the column 
    'otp_alias' through the `add_data_val` function of this module. 
    Finally, the built openpyxl workbook is saved using the full path 
    'xl_dpt_path'.

    Arg:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        dpt_df (dataframe): The publications-list dataframe of a departmentof \
        the Institute.
        dpt_otp_dict (dict): Dict keyed by lab-names and valued by lab-OTPs lists.
        xl_dpt_path (path): Full path to the file for setting publication OTP.  
        otp_col_dic (dict): Dict valued by the column names for rename of columns \
        of the file created for setting publications OTP.
        otp_lab_name_col (str): Column name of lab name to be used for the selection \
        of the OTPs validation list.
    """
    # Setting num of first col and first row in EXCEL files
    xl_idx_base = pg.XL_INDEX_BASE

    # Setting useful aliases
    otp_alias = otp_col_dic['otp_list']

    # Setting col attributes keys
    attr_keys_list = set_base_keys_list(institute, org_tup)

    # Setting useful-columns list of OTP df
    otp_col_list = list(otp_col_dic.values())

    # Creating workbook
    wb = openpyxl_Workbook()

    # Activating the validation data list in all cells of the OTPs column
    if len(dpt_df):
        first = True
        for otp_lab, otp_lab_df in dpt_df.groupby(otp_lab_name_col):
            # Setting a validation list per lab
            lab_otp_list = dpt_otp_dict[otp_lab]
            validation_list, data_val = build_data_val(lab_otp_list)

            # Adding a column containing OTPs of 'otp_lab' laboratory
            otp_lab_df[otp_alias] = validation_list

            # Renaming the columns
            otp_lab_df = otp_lab_df.reindex(columns=otp_col_list)

            # Formatting 'otp_lab_df' as a new sheet of the 'wb'
            # multisheet openpyxl workbook
            sheet_name = otp_lab
            otp_lab_df_title = pg.DF_TITLES_LIST[2]
            wb = format_wb_sheet(sheet_name, otp_lab_df,
                                 otp_lab_df_title, wb, first,
                                 attr_keys_list=attr_keys_list)
            ws = wb.active

            # Getting the column letter for the OTPs column
            otp_col_letter = get_col_letter(otp_lab_df, otp_alias, xl_idx_base)

            # Adding a validation data list
            ws = add_data_val(ws, data_val, len(otp_lab_df), otp_col_letter,
                              xl_idx_base)
            first = False
    else:
        # Renaming the columns
        dpt_df = dpt_df.rename(columns={otp_lab_name_col:otp_alias})
        dpt_df = dpt_df.reindex(columns=otp_col_list)

        # Formatting 'dpt_df' as openpyxl workbook
        dpt_df_title = pg.DF_TITLES_LIST[2]
        wb, ws = format_page(dpt_df, dpt_df_title, attr_keys_list=attr_keys_list)
        dpt_label = dpt
        if dpt=="DIR":
            dpt_label = "(" + institute.upper() + ")"
        ws.title = "(full-" + dpt_label + ")"

    # Saving the workbook
    wb.save(xl_dpt_path)


def _set_otp_lab(institute, org_tup, otp_col_dic,
                 dpt_labs_list, lab_df, lab):
    """Sets the lab name to be used for the determination 
    of the OTPs list of the 'lab' lab.
    """
    # Setting institute parameters
    nolab_depts = org_tup[16]

    # Setting useful aliases
    dpt_col = otp_col_dic['dpt']
    srv_col = otp_col_dic['serv']

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


def _build_otp_dept_df(institute, org_tup, otp_col_dic,
                       dpt_attributs_dict, dpt_labs_list,
                       otp_lab_name_col, full_df, dpt):
    """Builds a dataframe extracted from 'full_df' dataframe by 
    electing rows of publications where at least one author is 
    affiliated to the department 'dpt'.
    
    A column is added with the lab to be used for the determination 
    of the OTPs list through the `_set_otp_lab` internal function.
    """

    # Setting useful aliases
    dpt_label_alias = ig.DPT_LABEL_KEY

    # Setting useful col names
    dpt_col = otp_col_dic['dpt']
    lab_col = otp_col_dic['lab']

    # Setting dpt_df with only pub_ids for which the first author
    # is from the 'dpt' department
    filtre_dpt = False
    for dpt_value in dpt_attributs_dict[dpt][dpt_label_alias]:
        filtre_dpt = filtre_dpt | (full_df[dpt_col]==dpt_value)
    dpt_df = full_df[filtre_dpt].copy()

    # Adding column for lab names to be used for OTPs list setting
    usecols = list(dpt_df.columns) + [otp_lab_name_col]
    otp_dpt_df = pd.DataFrame(columns=usecols)
    if len(dpt_df):
        for lab, lab_df in dpt_df.groupby(lab_col):
            otp_lab = _set_otp_lab(institute, org_tup, otp_col_dic,
                                   dpt_labs_list, lab_df, lab)
            lab_df[otp_lab_name_col] = otp_lab
            otp_dpt_df = concat_dfs([otp_dpt_df, lab_df])
    return otp_dpt_df


def _add_lab_otp(institute, org_tup, in_path, out_path, out_file_base, lab_otps_dict):
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
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        in_path (path): Full path to the file where homonyms have been solved.
        out_path (path): Full path to the files for setting OTPs attributes by the user.
        out_file_base (str): Base for building created-files names.
        lab_otps_dict (dict): OTPs hierarchical dict keyed by departments \
        and valued by dicts keyed by labs and valued by OTPs lists.
    """

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]
    dpt_list = list(dpt_attributs_dict.keys())

    # Setting OTP df column names dict
    otp_col_dic = set_otp_col_names(institute, org_tup)

    # Setting useful col names
    pub_id_col = otp_col_dic['pub_id']
    idx_author_col = otp_col_dic['author_id']
    dpt_col = otp_col_dic['dpt']

    # Setting specific col names
    otp_lab_name_col = "otp_lab"

    # Enhancing file where homonymies have been solved by the user
    init_df = _enhance_homonyms_file(institute, org_tup, in_path)

    # Building 'new_df' out of 'init_df' with one row per pub_id
    # 1 or 0 is assigned to each department column depending
    # on if at least one co-author is a member of this department,
    # the detailed information is related to the first author only
    new_df = pd.DataFrame()
    for _, dg in init_df.groupby(pub_id_col):
        dg = dg.sort_values(by=[idx_author_col])
        for dpt in dpt_list:
            x = dg[dpt].any().astype(int)
            dg[dpt] = x
        new_df = concat_dfs([new_df, dg.iloc[:1]])

    # Removing possible spaces in dept name
    new_df[dpt_col] = new_df[dpt_col].apply(lambda x: x.strip())

    # Configuring an Excel file per department with the list of OTPs
    for dpt in sorted(dpt_list):
        # Setting the dict of list of OTPs for the 'dpt' department
        dpt_otp_dict = lab_otps_dict[dpt]

        # Setting list of the labs of the department
        dpt_labs_list = dpt_otp_dict.keys()

        # Setting the data with pub info and list of OTPs
        # for the 'dpt' department
        otp_dpt_df = _build_otp_dept_df(institute, org_tup, otp_col_dic,
                                        dpt_attributs_dict, dpt_labs_list,
                                        otp_lab_name_col, new_df, dpt)

        # Setting the full path of the EXCEl file for the 'dpt' department
        otp_file_name_dpt = f'{out_file_base}_{dpt}.xlsx'
        xl_dpt_path = out_path / Path(otp_file_name_dpt)

       # Adding a column with validation list for OTPs and saving the file
        _save_dpt_lab_otp_file(institute, org_tup, otp_dpt_df, dpt_otp_dict,
                               xl_dpt_path, otp_col_dic, otp_lab_name_col, dpt)


def add_otp(institute, org_tup, bibliometer_path, in_path, out_path, out_file_base):
    """Creates the files for setting OTP attribute of publications by the user 
    for the Institute departments either among OTPs list at department level 
    or lab level.
    
    Depending on the specified level: 
    - The file is created through the `_add_dept_otp` or `_add_lab_otp` \
    internal functions. 
    - The OTPs info are got through 'org_tup' parameter or `set_lab_otps` \
    function imported from `bmfuncts.build_otps_info` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        in_path (path): Full path to the file where homonyms have been solved.
        out_path (path): Full path to the files for setting OTPs attributes by the user.
        out_file_base (str): Base for building created-files names.
    Returns:
        (str): end message recalling out_path.
    """
    # Setting institute parameters
    otp_level = org_tup[11]

    if otp_level=="LAB":
        lab_otps_dict = set_lab_otps(institute, org_tup, bibliometer_path)
        _add_lab_otp(institute, org_tup, in_path, out_path, out_file_base, lab_otps_dict)
    else:
        _add_dept_otp(institute, org_tup, in_path, out_path, out_file_base)

    end_message = ("Files for setting publication OTPs per department "
                   f"saved in folder: \n  '{out_path}'")
    return end_message
