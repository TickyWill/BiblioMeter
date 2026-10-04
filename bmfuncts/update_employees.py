"""Module of functions for the update of the employees' database.
"""
__all__ = ['set_empl_data',
           'set_corpus_empl_data',
           'update_employees',]

# Standard library imports
import os
import re
import shutil
from pathlib import Path
from tkinter import messagebox

# 3rd party imports
import pandas as pd

# local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.pub_globals as bm_pg
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import get_sheet_names
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import print_temp_text
from bmfuncts.useful_functs import standardize_txt


def _set_employees_cols():
    """Builds two dicts giving columns' names and lists of columns'names 
    for the process of updating employees' data.

    Returns:
        (tup): The two built dicts.
    """
    empl_cols_dic = {'firstname_col'         : bm_eg.EMPLOYEES_USEFUL_COLS['first_name'],
                     'lastname_col'          : bm_eg.EMPLOYEES_USEFUL_COLS['name'],
                     'firstname_initials_col': bm_eg.EMPLOYEES_ADD_COLS['first_name_initials'],
                     'fullname_col'          : bm_eg.EMPLOYEES_ADD_COLS['employee_full_name'],
                     'mat_col'               : bm_eg.EMPLOYEES_USEFUL_COLS['matricule'],
                     'dpt_col'               : bm_eg.EMPLOYEES_USEFUL_COLS['dpt'],
                     'serv_col'              : bm_eg.EMPLOYEES_USEFUL_COLS['serv'],
                     'dpts_col'              : bm_eg.EMPLOYEES_ADD_COLS['dpts_list'],
                     'servs_col'             : bm_eg.EMPLOYEES_ADD_COLS['servs_list'],
                     'months_col'            : bm_eg.EMPLOYEES_ADD_COLS['months_list'],
                     'years_col'             : bm_eg.EMPLOYEES_ADD_COLS['years_list'],
                    }

    empl_col_lists_dic = {'useful_col_list': list(bm_eg.EMPLOYEES_USEFUL_COLS.values()),
                          'add_col_list'   : list(bm_eg.EMPLOYEES_ADD_COLS.values()),
                         }
    return empl_cols_dic, empl_col_lists_dic


def _set_employees_paths(wf_path):
    """Sets the full paths to the employees' working folders and  to the employees' files.

    The paths of the  folders are as follows:
    - 'months2add_employees_folder_path' - The full path to the folder \
    which name is given by the 'EMPLOYEES_ARCHI' global at \
    'complementary_employees' key and hosting the employees' XLSX file(s) \
    to add; this file must contain one sheet per month for a given year.
    - 'all_years_employees_folder_path' - The full path to the folder \
    which name is given by the 'EMPLOYEES_ARCHI' global at \
    'all_years_employees' key and hosting the employees' XLSX file; \
    this file contains a sheet per year.
    - 'one_year_employees_folder_path' - The full path to the folder \
     which name is given by the 'EMPLOYEES_ARCHI' global at \
    'one_year_employees' key and hosting the annual employees' XLSX files.
    - 'backup_folder_path' - The full path to the folder which name \
     is given by the 'ARCHI_BACKUP' global at 'root' key and hosting \
     the backup file of the employees' XLSX file in case of corruption \
     of the active employees' file.

    Args:
        wf_path (path): Full path to working folder.
    Returns:
        (tup): Composed of the list of full paths to the useful folders and of the full paths to the useful files.
    """
    # Setting folder of the Institute parameters
    wf_root_path = wf_path.parent

    # Setting useful aliases
    year_empl_name_base_alias = bm_eg.EMPLOYEES_ARCHI["one_year_employees_filebase"]
    all_years_empl_file_alias = bm_eg.EMPLOYEES_ARCHI["employees_file_name"]
    root_empl_folder_alias = bm_eg.EMPLOYEES_ARCHI["root"]
    all_years_empl_folder_alias = bm_eg.EMPLOYEES_ARCHI["all_years_employees"]
    year_empl_folder_alias = bm_eg.EMPLOYEES_ARCHI["one_year_employees"]
    months2add_empl_folder_alias = bm_eg.EMPLOYEES_ARCHI["complementary_employees"]
    backup_folder_alias = bm_pg.ARCHI_BACKUP["root"]

    # Setting useful paths
    root_empl_folder_path = wf_root_path / Path(root_empl_folder_alias)
    months2add_empl_folder_path = root_empl_folder_path / Path(months2add_empl_folder_alias)
    all_years_empl_folder_path = root_empl_folder_path / Path(all_years_empl_folder_alias)
    year_empl_folder_path = root_empl_folder_path / Path(year_empl_folder_alias)
    backup_folder_path = wf_root_path / Path(backup_folder_alias)

    # Setting full paths to useful files
    all_years_file_path = all_years_empl_folder_path / Path(all_years_empl_file_alias)
    all_years_file_backup_path = backup_folder_path / Path(all_years_empl_file_alias)

    folder_paths = [months2add_empl_folder_path, all_years_empl_folder_path,
                    year_empl_folder_path, backup_folder_path]
    file_paths = [all_years_file_path, all_years_file_backup_path]

    return folder_paths, file_paths, year_empl_name_base_alias


# ******************************************************
# * Functions for updating the file of employees' data *
# *            by adding complementary data            *
# ******************************************************

def _check_sheet_month(df, sheet_name, useful_col_list):
    """Checks if the mandatory column names are present in the dataframe 
    'df' and if the sheet name is correctly formatted.

    The sheet name should be formatted as 'mmyyyy' where 'yyyy' stands for
    the 'year' and mm stands for the month (always written with two digits). 
    It returns messages related to the check status. 
    The year returned is None if the sheet name is not correctly formatted 
    or the month is not in possible months.

    Args:
        df (dataframe): The dataframe to be checked.
        sheet_name (str): The sheet name to be checked.
        useful_col_list (list): The useful columns' names as set at key 'useful_col_list' \
        in the dict of lists of columns' names built through the `_set_employees_cols` \
        internal function.
    Returns:
        (tup): Tuple of 3 strings = (year, sheet_name_error, col_error).
    """
    # Initializing returned parameters
    year, sheet_name_error, col_error = [None] * 3

    missing_column = set(useful_col_list)-set(df.columns)
    if len(missing_column)!=0:
        col_error  = f"The column(s) '{list(missing_column)}' is (are) missing or misspelled "
        col_error += f"in sheet name '{sheet_name}'."

    possible_months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    re_mmyyyy = re.compile(r'^\d{6}$')
    if re_mmyyyy.findall(sheet_name):
        month = sheet_name[0:2]
        if month in possible_months:
            year = sheet_name[2:6]
        else:
            sheet_name_error = (f"Month '{month}' is not among possible months "
                                f"in sheet name '{sheet_name}'.")
    else:
        sheet_name_error = (f"The sheet name '{sheet_name}' "
                            f"is not correctly formated as mmyyyy.")
    return year, sheet_name_error, col_error


def _add_sheets_to_workbook(file_full_path, df_to_add, sheet_name):
    """Adds the dataframe 'df_to_add' as sheet named 'sheet_name' 
    to the existing EXCEL file with full path 'file_full_path'.

    If the sheet name already exists it is overwritten by the new one.
    """
    with pd.ExcelWriter(file_full_path,# https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
                        engine='openpyxl',
                        mode='a',
                        if_sheet_exists='replace') as writer:
        df_to_add.to_excel(writer, sheet_name=sheet_name, index=False)


def _update_months_history(year, year_months_file_path, all_months_to_add, df_months_to_add,
                           not_replace, update_progress_params):
    progress_callback, progress_bar_state, step = update_progress_params
    if os.path.isfile(year_months_file_path):
        # if the year file already exits we update with new sheets
        df_months_dict = pd.read_excel(year_months_file_path, sheet_name=None)
        months_to_add = all_months_to_add
        if not_replace: # we only add missing months
            months_present = list(df_months_dict.keys())
            months_to_add = list(set(all_months_to_add) - set(months_present))
            months_to_add = sorted(months_to_add)
        for month in months_to_add:
            _add_sheets_to_workbook(year_months_file_path, df_months_to_add[month], month)
            if progress_callback:
                progress_bar_state += step
                progress_callback(progress_bar_state)
    else:
        # if the file is not present we create a new Excel file with one sheet per month
        month = all_months_to_add[0]
        # we add the first month
        df_months_to_add[month].to_excel(year_months_file_path, sheet_name=month)
        for month in all_months_to_add[1:]:
            # we add the other months
            _add_sheets_to_workbook(year_months_file_path, df_months_to_add[month], month)
            if progress_callback:
                progress_bar_state = int(progress_bar_state + step)
                progress_callback(progress_bar_state)
        if progress_callback:
            progress_bar_state += step
    return year_months_file_path, progress_bar_state


def _try_update_months_history(months2add_file_path, year_empl_folder_path, year_empl_base_name,
                               useful_col_list, not_replace, progress_params):
    """Updates the file pointed by 'year_months_file_path' for a year.

    More specifically only the new months contained in the EXCEL file 
    pointed by 'months2add_file_path' are added as new sheets 
    named 'mmyyyy' where 'mm' stands for the month and 'yyyy' for the year.

    The sheets are checked using the local function '_check_sheet_month' 
    of the module 'bmfuncts.update_employees of the package 'bmfuncts'.

    This function returns error messages if the sheets to add are misconfigured. 
    If no error is returned, the sheets are added using the '_add_sheets_to_workbook' \
    internal function.

    Args:
        months2add_file_path (path): Full path to the employees' EXCEL file \
        with one sheet per months to update the employees' file.
        year_empl_folder_path (path): Full path to the folder containing \
        the files gathering the employees per year.
        year_empl_base_name (path): Base for building the file \
        name of the file gathering the employees for a year.
        useful_col_list (list): The useful columns' names as set at key 'useful_col_list' \
        in the dict of lists of columns' names built through the `_set_employees_cols` \
        internal function.
        not_replace (bool): if True, existing sheets are kept in the XLSX file and only \
        missing months are added as new sheets.
        progress_params (list): Composed of the function for updating ProgressBar tkinter \
        widget status and of the initial status of ProgressBar tkinter widget.
    Returns:
        (list): Composed of 5 strings and 1 integer = [year, year_months_file_path, \
        sheet_name_message, col_message, years2add_message, progress_bar_state].
    """
    # Setting parameters' values from 'progress_params'
    progress_callback, progress_bar_state = progress_params

    # Initializing errors messages and local parameters
    months_errors_list = [None] * 5
    step = None
    years_list = []

    # Setting data to add
    df_months_to_add = pd.read_excel(months2add_file_path, sheet_name=None)
    all_months_to_add = list(df_months_to_add.keys())
    months_to_add_nb = len(all_months_to_add)
    if progress_callback:
        step = 20 / months_to_add_nb

    for month in all_months_to_add:
        month_return = _check_sheet_month(df_months_to_add[month], month, useful_col_list)
        month_year, month_sheet_name_error, month_col_error = month_return
        if any([not month_year, month_sheet_name_error, month_col_error]):
            months_errors_list = [None, None, month_sheet_name_error, month_col_error, None]
            break
        years_list.append(month_year)
        if progress_callback:
            progress_bar_state += step
            progress_callback(progress_bar_state)

    if not any(months_errors_list):
        years_list = list(set(years_list))
        if len(years_list)>1:
            years2add_error = ("Too many years covered by the file of months to add "
                               "while only one was expected.")
            months_errors_list = [None, None, None, None, years2add_error]
        else:
            year = years_list[0]
            file_name = f'{year}' + year_empl_base_name
            year_months_file_path = year_empl_folder_path / Path(file_name)
            update_progress_params = [progress_callback, progress_bar_state, step]
            update_return = _update_months_history(year, year_months_file_path, all_months_to_add,
                                                   df_months_to_add, not_replace, update_progress_params)
            year_months_file_path, progress_bar_state = update_return
            months_errors_list = [year, year_months_file_path, None, None, None]
    if progress_callback:
        progress_bar_state = int(progress_bar_state)
    return months_errors_list, progress_bar_state


def _add_column_keep_history(df, empl_cols_dic):
    """Creates 4 new columns defined by the global 'EFFECTIF_ADD_COLS' 
    at the keys 'dpts_list', 'servs_list', 'months_list' and 'years_list'.

    These columns contain, for each employee, the lists of its departments 
    and services affiliation per available months.

        ex: The employee was part of 'DTCH' from January to March and was part 
        of 'DTNM' from April to September, if for this employee:

        - the column of key 'months_list' contains \
        ['01', '02', '03', '04', '05', '06', '07', '08', '09'] \
        - and the column of key dpts_list' contains \
        ['DTCH', 'DTCH', 'DTCH', 'DTNM', 'DTNM', 'DTNM', 'DTNM', 'DTNM', 'DTNM'].

    The function uses the columns defined by the global `EMPLOYEES_USEFUL_COLS`
    at keys 'dpt' and 'serv' that contain, for each employee,
    a list of at most 12 tuples:

        [(mm_1, yyyy_1, dep_1),(mm_2, yyyy_2, dep_2), ..., (mm_n, yyyy_n, dep_n)]

    witch are re-casted in 3 lists [mm_1, mm_2, ..., mm_n]:

        [yyyy_1, yyyy_2, ..., yyyy_n], [dep_1, dep_2, ..., dep_n].

    Args:
        df (dataframe): The dataframe to which the 4 columns are added.
        empl_cols_dic (dict): Useful columns' names as built through \
        the `_set_employees_cols` internal function.
    Returns:
        (dataframe): The updated dataframe.
    """
    # Setting useful col names
    cols_keys = ['dpt_col', 'serv_col', 'dpts_col', 'servs_col', 'months_col', 'years_col']
    (dpt_col, serv_col, dpts_col, servs_col, months_col,
     years_col) = [empl_cols_dic[key] for key in cols_keys]

    # Converting the list of tuples[(mm_1, yyyy_1, item_1), ...(mm_n, yyyy_n, item_n)]
    # into a list of 3 lists [[mm_1,...,mm_n], [yyyy_1,....yyyy_n],[item_1,....,item_n]]
    # where 'item' stands for department.
    # The 2 lists of 3 lists are put into the two new columns
    # 'dpts_col' and 'servs_col'
    cols_tup_list = [(dpt_col, dpts_col), (serv_col, servs_col)]
    for cols_tup in cols_tup_list:
        col_in, col_out = cols_tup[0], cols_tup[1]
        df[col_out] = df[col_in].apply(lambda x: [list(x) for x in list(zip(*x))])

    # Exploding the 2 lists of 3 lists into the columns
    # 'months_cal', 'years_col', 'depts_col' and 'servs_col'
    for col in [dpts_col, servs_col]:
        new_col = [months_col, years_col, col]
        df[new_col] = pd.DataFrame(df[col].tolist(), index=df.index)
    return df


def _add_column_firstname_initial(df, firstname_col, firstname_initials_col):
    """Adds a new column defined by the global 'EMPLOYEES_ADD_COLS' 
    at the key 'first_name_initials' containing the initials of the firstname.

    It uses the columns defined by the global `EMPLOYEES_USEFUL_COLS` at key 'first_name' 
    that contains the full first name for each employee:

        ex: PIERRE -->P, JEAN-PIERRE --> JP , JEAN-PIERRE MARIE --> JPM.

    Args:
        df (dataframe): The dataframe to which the column is added.
        firstname_col (str): The column name of employee's firstname.
        firstname_initials_col (str): The column name of employee's firstname.
    Returns:
        (dataframe): The updated dataframe.
    """
    # Internal functions
    def _get_firstname_initials(row):
        row = row[0] if isinstance(row, list) else row
        row = row.replace('-',' ').strip(' ')
        row_list = row.split(' ')
        initial_list = [x[0] for x in row_list]
        initials = ''.join(initial_list)
        return initials

    df[firstname_initials_col] = df[firstname_col].apply(_get_firstname_initials)
    return df


def _add_column_full_name(df, lastname_col, firstname_initials_col, fullname_col):
    """Adds a new column key containing the employee full name
    composed by the last name and the first name initials.

    The employee lastname is first standardized through the `standardize_txt` 
    function imported from `bmfuncts.useful_functs` module.

    Args:
        df (dataframe): The data to which the column is added.
        empl_cols_dic (dict): Useful columns' names as built through \
        the `_set_employees_cols` internal function.
    Returns:
        (dataframe): The updated data.
    """
    new_df = df.copy()
    new_df = new_df.assign(temp_col=new_df[lastname_col])
    new_df["temp_col"] = new_df["temp_col"].apply(standardize_txt)
    new_df[fullname_col] = new_df["temp_col"] + " " + new_df[firstname_initials_col]
    new_df = new_df.drop(columns="temp_col")
    return new_df


def _select_employee_dpt_and_serv(df, dpt_col, serv_col):
    """Selects the department and the service of an employee 
    among the list of departments and services of affiliation 
    during the year.

    The rule is to choose the department and the service corresponding 
    to the first available month of the year.

        ex: The column defined by the global  'EMPLOYEES_USEFUL_COLS' \
        at key 'dpt' contains the list of tuples (mm, yyyy, dpt) such as:

            x = [('04', '2019', 'DTBH'), ('05', '2019', 'DTBH'), \
            ('06', '2019', 'DTNM'), ..., ('12', '2019', 'DTNM')].

        We select DTBH = x[0][-1] as the first occurrence. \
        The last occurrence would be DTNM = x[-1][-1].

    Args:
        df (dataframe): The dataframe to be modified.
        dpt_col (str): The column name of employee's department.
        serv_col (str): The column name of employee's service.
    Returns:
        (dataframe): The updated dataframe.
    Note:
        A more fair full allocation would be department/service \
        where the employee spent the maximum time during the year.
        This may be done using the lambda function where 'Counter' \
        is a method of the 'collections' library:
        >lambda x: max((count := Counter([y[2] for y in x])), key = count.get).
    """
    for col in [dpt_col, serv_col]:
        df[col] = df[col].apply(lambda x: x[0][-1])
    return df


def _build_year_month_dpt(year_months_file_path, print_params, empl_cols_dic, empl_col_lists_dic,
                          progress_params):
    """Merges all employees' information of a year available by month
    in an XLSX workbook.

    This workbook contains a worksheet per month. 
    Each worksheet is labeled 'mmyyyy' where 'mm' stands for the month
    (01, 02, ..., 12) and 'yyyy' stands for the year (2019, 2020, ...).
    All the worksheets must at least contain the columns which names 
    are defined at the 'matricule', 'first_name', 'name', 'dpt'
    and 'serv' keys in the 'EMPLOYEES_USEFUL_COLS' global.
    The function merges the list of the sheets. Then, it builds the new columns
    defined by the 'EMPLOYEES_ADD_COLS' global using the internal functions:
    '_add_column_keep_history', '_add_column_firstname_initial' and 
    '_add_column_full_name'.
    The added columns at keys 'months_list', 'years_list', 'dpts_list' and 'servs_list'
    contains lists of the n items of the n available months.
    The lists are formated as follows: [item_1, item_2, ... items_n]
    where item_i stands for month, year, department and service respectively.
    Finally, a single department and service is selected for each employee using 
    the '_select_employee_dpt_and_serv' internal function.

    Args:
        year_months_file_path (path): The path to the XLSX file \
        that contains a sheet per month of a year.
        print_params (list): The print parameters.
        empl_cols_dic (dict): Useful columns' names as built through \
        the `_set_employees_cols` internal function.
        empl_col_lists_dic (dict) : Useful lists of columns' names as built through \
        the `_set_employees_cols` internal function.
        progress_params (list): Composed of the function for updating ProgressBar \
        tkinter widget status and of the initial status of ProgressBar tkinter widget.
    Returns:
        (dataframe): The built employees' data.
    """
    print_step_text(f"{bm_pg.TAB}- Updating employees' data of current year with the additional data",
                    print_params)
    # Internal functions
    def _set_tup(_month, _year):
        return lambda x: (_month, _year, x)

    # Setting parameters' values from 'progress_params'
    progress_callback, progress_bar_state = progress_params

    # Setting useful columns' parameters
    useful_col_list, add_col_list = empl_col_lists_dic.values()
    cols_keys = ['mat_col', 'firstname_col', 'lastname_col', 'firstname_initials_col',
                 'fullname_col', 'dpt_col', 'serv_col']
    (mat_col, firstname_col, lastname_col, firstname_initials_col, fullname_col,
     dpt_col, serv_col) = [empl_cols_dic[key] for key in cols_keys]

    # Reading the sheets from the Excel file as a dict
    year_empl_dict = pd.read_excel(year_months_file_path, sheet_name=None, usecols=useful_col_list)
    months_nb = len(year_empl_dict.keys())
    step = None
    if progress_callback:
        step = 20 / months_nb

    # Concatenating the sheets from the 'sheet_names' list into the dataframe 'year_empl_df'
    month_empl_df_list = []
    for sheet_name, month_empl_df in year_empl_dict.items():
        month = str(sheet_name)[0:2] # Extraction of the month mm for the sheet name mmyyyy
        year = str(sheet_name)[2:] # Extraction of year yyyy for the sheet name mmyyyy

        # For the sheet 'sheet_name' of the dataframe 'month_empl_df'
        # replacing each cell of column 'dpt_col'/'serv_col' that specifies
        # the employee department dpt/service by a tuple (month, year, dpt)/(month, year, serv)
        for col_keep_history in [dpt_col, serv_col]:
            month_empl_df[col_keep_history] = month_empl_df[col_keep_history].apply(_set_tup(month, year))

        month_empl_df_list.append(month_empl_df)
        if progress_callback:
            progress_bar_state += step
            progress_callback(progress_bar_state)

    year_empl_df = concat_dfs(month_empl_df_list)
    print_step_text(f"{bm_pg.TAB*2}- Concatenated the additionnal data of the year months", print_params)

    # Aggregating all the information related to one employee's identifier
    # as a list without duplicates, for each column (except mat_col)
    singlemat_year_empl_df = year_empl_df.groupby(mat_col).\
                                                  agg(lambda x :list(dict.fromkeys(x))).\
                                                  reset_index()

    # Recasting lists into string if its length is equal to 1
    col_set = {mat_col, lastname_col, firstname_col, serv_col, dpt_col}
    for col in set(useful_col_list) - col_set:
        singlemat_year_empl_df[col] = singlemat_year_empl_df[col].apply(lambda x: x[0] if len(x)==1
                                                                        else list(x))

    # Dealing with same matriculate for different lastnames and firstnames
    employees_df = singlemat_year_empl_df.explode([lastname_col])
    employees_df = employees_df.explode([firstname_col])
    print_step_text(f"{bm_pg.TAB*2}- Cleaned the additional data from duplicate information per employee",
                    print_params)

    # Adding 6 new columns
    employees_df = _add_column_keep_history(employees_df, empl_cols_dic)
    print_step_text(f"{bm_pg.TAB*2}- Added column with employee's affiliation history", print_params)
    employees_df = _add_column_firstname_initial(employees_df, firstname_col, firstname_initials_col)
    print_step_text(f"{bm_pg.TAB*2}- Added column with employee's firstname initials", print_params)
    employees_df = _add_column_full_name(employees_df, lastname_col, firstname_initials_col, fullname_col)
    print_step_text(f"{bm_pg.TAB*2}- Added column with employee's full name", print_params)
    employees_df = _select_employee_dpt_and_serv(employees_df, dpt_col, serv_col)
    print_step_text(f"{bm_pg.TAB*2}- Selected employee's department and service", print_params)

    employees_df = employees_df[useful_col_list + add_col_list]
    if progress_callback:
        progress_bar_state += 10
        progress_callback(progress_bar_state)
    return employees_df, progress_bar_state


def _check_available_empl_file_path(check_paths, print_params):
    all_years_file_path, backup_folder_path, all_years_file_backup_path = check_paths

    all_years_file_status = os.path.exists(all_years_file_path)
    all_years_file_backup_status = os.path.exists(all_years_file_backup_path)
    if os.path.exists(all_years_file_path):
        all_years_file_status = "exists"
        all_empl_years = get_sheet_names(all_years_file_path)
        print_step_text(f"{bm_pg.TAB}- Employees-data file available for "
                        f"{all_empl_years[0]} to {all_empl_years[-1]}", print_params)
    elif all_years_file_backup_status:
        all_years_file_status = "backup-copy"
        all_empl_years = get_sheet_names(all_years_file_backup_path)
        _ = shutil.copy(all_years_file_backup_path, all_years_file_path)
        print_step_text(f"{bm_pg.TAB}- Employees-data file copied from backup file for "
                        f"{all_empl_years[0]} to {all_empl_years[-1]}", print_params)
    else:
        all_years_file_status = "new"
        all_empl_years = None
        print_step_text(f"{bm_pg.TAB}- No employees-data file exists yet", print_params)
    return all_years_file_status, all_empl_years


def _set_empl_data_to_add_file(months2add_empl_folder_path):
    months2add_files = [file for file in os.listdir(months2add_empl_folder_path)
                        if file.endswith(".xlsx") and file[0] != '~']
    files_number_error = None
    if len(months2add_files)>1:
        files_number_error = (f"Too many files are present while expecting only one in:"
                              f"\n{bm_pg.TAB}'{months2add_empl_folder_path}'")
    if not months2add_files:
        files_number_error = (f"No update is possible since no file is available in:"
                              f"\n{bm_pg.TAB}'{months2add_empl_folder_path}'")
    return months2add_files, files_number_error


def _save_empl_data(all_years_file_params, empl_df, empl_year, print_params):
    # Setting parameters' values from 'all_years_file_params'
    all_years_file_status, all_years_file_path, backup_folder_path = all_years_file_params

    # Saving empl_df as a sheet name after empl_year,
    # in the workbook pointed by all_years_file_path
    all_years_file_error = None
    if all_years_file_status!="new":
        txt_len = print_temp_text(f"{bm_pg.TAB}- Updating the employees' file with the updated current-year data...",
                                  txt_end=True)
        _add_sheets_to_workbook(all_years_file_path, empl_df, empl_year)
        print_step_text(f"{bm_pg.TAB}- Employees' file updated with the updated current-year data",
                        print_params, prev_txt_len=txt_len)
    else:
        empl_df.to_excel(all_years_file_path, sheet_name=empl_year)
        all_years_file_error = f"Employees' file created with the current-year data"
        print_step_text(f"{bm_pg.TAB}- {all_years_file_error}", print_params)

    # Copying the all-years employees' file updated to the backup folder
    shutil.copy(all_years_file_path, backup_folder_path)
    print_step_text(f"{bm_pg.TAB}- Updated employees' data saved as backup file", print_params)
    return all_years_file_error


def update_employees(wf_path, print_params, progress_callback=None, progress_bar_state_init=None,
                     replace=True):
    """Updates the file of employees' data with the potentially available data to add.

    Args:
        wf_path (path): The path to the working folder.
        print_params (list): The prints' parameters.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
        progress_bar_state_init (int): Initial value of the progress bar.
        replace (bool): Optional (default = True); if true, existing sheets \
        are replaced in employees' EXCEL files specific to a year.
    Returns:
        (list): Composed of 5 strings; a first string giving the employees' year \
        if no error is raised otherwise set to "None"; then 4 strings specifying errors related \
        respectively to files number, sheet-name, column name and number \
        of years to update; these 4 strings are set to "None" when no error is raised.
    """
    print_step_text("\nTrying to update employees' data...", print_params)

    # Setting useful cols parameters
    empl_cols_dic, empl_col_lists_dic = _set_employees_cols()
    useful_col_list = empl_col_lists_dic['useful_col_list']

    # Getting useful employees' paths
    folder_paths, file_paths, year_empl_name_base = _set_employees_paths(wf_path)
    (months2add_empl_folder_path, _, year_empl_folder_path, backup_folder_path) = folder_paths
    all_years_file_path, all_years_file_backup_path = file_paths

    # Checking the availability of employees' data
    check_paths = [all_years_file_path, backup_folder_path, all_years_file_backup_path]
    all_years_file_status, _ = _check_available_empl_file_path(check_paths, print_params)

    # Setting the list of files available to add (expected only one)
    months2add_files, files_number_error =  _set_empl_data_to_add_file(months2add_empl_folder_path)

    # Initializing the returned errors
    update_errors = [None] * 6

    if files_number_error:
        print_step_text(f"{bm_pg.TAB}- {files_number_error}", print_params)
        update_errors = [None, files_number_error, None, None, None, None]
    else:
        print_step_text(f"{bm_pg.TAB}- A file is available for the update", print_params)
        months2add_file_path = months2add_empl_folder_path / Path(months2add_files[0])
        progress_params = [progress_callback, progress_bar_state_init]
        try_return = _try_update_months_history(months2add_file_path, year_empl_folder_path, year_empl_name_base,
                                                useful_col_list, replace, progress_params)
        months_errors, progress_bar_state_1 = try_return
        empl_year, year_months_file_path, sheet_name_error, column_error, years2add_error = months_errors
        print_step_text(f"{bm_pg.TAB}- The data to add checked", print_params)

        if not empl_year or not year_months_file_path:
            print_step_text(f"{bm_pg.TAB}- Format errors of additional data found", print_params)
            update_errors = [None, None, sheet_name_error, column_error, years2add_error, None]
        else:
            print_step_text(f"{bm_pg.TAB}- Format of data to add is correct", print_params)
            # Concatenating the months' data of the current year to the employees' data of the current year
            progress_params = [progress_callback, progress_bar_state_1]
            empl_df, progress_bar_state_2 = _build_year_month_dpt(year_months_file_path, print_params, empl_cols_dic,
                                                                  empl_col_lists_dic, progress_params)
            print_step_text(f"{bm_pg.TAB}- Employees' data of current year updated with the additional data", print_params)

            # Saving empl_df as a sheet name after empl_year,
            # in the workbook pointed by all_years_file_path
            all_years_file_params = [all_years_file_status, all_years_file_path, backup_folder_path]
            all_years_file_error = _save_empl_data(all_years_file_params, empl_df, empl_year, print_params)

            update_errors = [empl_year, None, None, None, None, all_years_file_error]
            if progress_callback:
                progress_bar_left = 100 - progress_bar_state_2
                progress_callback(progress_bar_state_2 + progress_bar_left * 0.5)
    if progress_callback:
        progress_callback(100)
    return update_errors


# **********************************************************************
# * Functions for selecting employees' data for a list of corpus years *
# **********************************************************************

def _select_empl_years(empl_file_path, corpus_years):
    # Setting available years in employees' data
    all_empl_years = get_sheet_names(empl_file_path)

    # Selecting the useful available years in employees' data for the corpus list
    int_all_empl_years = sorted([int(x) for x in all_empl_years])
    int_empl_years = sorted(int_all_empl_years, reverse=True)
    int_corpus_years = sorted([int(x) for x in corpus_years])
    min_empl_year = int_corpus_years[0] - bm_eg.SEARCH_DEPTH
    if min_empl_year in int_all_empl_years:
        min_empl_year_index = int_all_empl_years.index(min_empl_year)
        int_empl_years = sorted(int_all_empl_years[min_empl_year_index:], reverse=True)
    empl_years = [str(i) for i in int_empl_years]
    return empl_years


def set_empl_data(empl_file_path, corpus_years, print_params):
    print_step_text(f"\nSetting the employees' 'data for {corpus_years[0]} to {corpus_years[-1]} corpus...",
                    print_params)

    # Setting useful columns' names
    _, empl_col_lists_dic = _set_employees_cols()
    full_cols_list = list(empl_col_lists_dic['useful_col_list']) + list(empl_col_lists_dic['add_col_list'])

    # Selecting the useful available years in employees' data for the corpus list
    empl_years = _select_empl_years(empl_file_path, corpus_years)
    print_step_text(f"{bm_pg.TAB}- Selected years of employees' data: {empl_years[0]} down to {empl_years[-1]}",
                        print_params)

    # Getting the employees' data for the useful available years
    print_step_text(f"{bm_pg.TAB}- Reading the multisheet file of employees' data...", print_params)
    empl_dict = {}
    for year in empl_years:
        txt_len = print_temp_text(f"{bm_pg.TAB*2}- Reading sheet: {year}", txt_end=True)
        empl_dict[year] = pd.read_excel(empl_file_path, sheet_name=year,
                          dtype=bm_eg.EMPLOYEES_COL_TYPES,
                          usecols=full_cols_list, keep_default_na=False)
    print_step_text(f"{bm_pg.TAB*2}- Employees' data of the selected years available", print_params,
                    prev_txt_len=txt_len)
    return empl_dict


# ************************************************************
# * Functions for selecting employees' data for a corpus year *
# *        from data built for a list of corpus years        *
# ************************************************************

def _build_useful_employees_years(empl_years, corpus_year, init_search_depth):
    # Identifying available years in employees' data
    int_empl_years = [int(x) for x in empl_years]
    int_years_to_check = [int(corpus_year) - i for i in range(int(init_search_depth))]
    int_corpus_empl_years = [i for i in int_years_to_check if i in int_empl_years]
    corpus_empl_years = [str(int_year) for int_year in int_corpus_empl_years]

    if len(int_corpus_empl_years)>0:
        corpus_search_depth = min(int(init_search_depth), len(int_corpus_empl_years))
    else:
        corpus_search_depth = 0
    return corpus_search_depth, corpus_empl_years


def set_corpus_empl_data(corpus_year, empl_dict, init_search_depth, print_params):
    """Sets employees' data for the corpus.

    Args:
        corpus_year (str): Corpus year defined by 4 digits.
        empl_file_path (path): Full path to file of Institute \
        employees' data.
        init_search_depth (int): Initial search depth.
        print_params (list): The prints' parameters.
    Returns:
        (tup): (employees' data (df), adapted search depth (int), \
        list of available years of employees' data).
    """
    print_step_text("\nSetting the adequate years-selection of employees' data...", print_params)

    # Getting the employees' years available
    empl_years = empl_dict.keys()

    # Identifying available years in employees' data for the corpus
    corpus_search_depth, corpus_empl_years = _build_useful_employees_years(empl_years, corpus_year,
                                                                          init_search_depth)
    corpus_empl_dict = {}
    corpus_empl_years_str = ""
    if corpus_search_depth!=0:
        # Getting employees' data for the corpus
        corpus_empl_dict = {key: empl_dict[key] for key in corpus_empl_years}
        corpus_empl_years_str = ', '.join(corpus_empl_years)
        print_step_text(f"{bm_pg.TAB}- Selected years of employees' data: "
                        f"{corpus_empl_years[0]} to {corpus_empl_years[-1]}", print_params)
    else:
        print_step_text(f"{bm_pg.TAB}- No employees' data available for the corpus {corpus_year}", print_params)
    return corpus_empl_dict, corpus_search_depth, corpus_empl_years_str
