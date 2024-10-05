"""Module of functions for the update of the employees database."""
__all__ = ['update_employees',]

# Standard library imports
import os
import re
import shutil
from pathlib import Path

# 3rd party imports
import pandas as pd

# local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg

def _set_employees_paths(bibliometer_path):
    """The function `_set_employees_paths` sets the full paths towards
    4 working folders:
    - 'months2add_employees_folder_path': the folder containing
    the employees Excel file(s) to add; this file must contain
    one sheet per month for a given year.
    - 'all_years_employees_folder_path': the folder hosting
    the employees ExcelL file which name is given by the global
    'EMPLOYEES_ARCHI' at key 'all_years_employees' containing a sheet per year.
    - 'one_year_employees_folder_path': the folder hosting
    the annual employees Excel files which names are built
    by adding the year value to the string given by the global
    'EMPLOYEES_ARCHI' at key 'one_year_employees_filebase'.
    - 'backup_folder_path': the folder hosting the back-up file
    of the employees EXCEL file in case of a potential corruption
    of the active employees file.

    Args:
        bibliometer_path (path): Full path to working folder.
    
    Returns:
        (tup): Tuple of the 4 built paths.
    """

    # Setting useful aliases
    root_employees_folder_alias       = eg.EMPLOYEES_ARCHI["root"]
    all_years_employees_folder_alias  = eg.EMPLOYEES_ARCHI["all_years_employees"]
    one_year_employees_folder_alias   = eg.EMPLOYEES_ARCHI["one_year_employees"]
    months2add_employees_folder_alias = eg.EMPLOYEES_ARCHI["complementary_employees"]
    backup_folder_alias = pg.ARCHI_BACKUP["root"]

    # Setting useful paths
    root_employees_folder_path       = bibliometer_path / Path(root_employees_folder_alias)
    months2add_employees_folder_path = root_employees_folder_path / \
                                       Path(months2add_employees_folder_alias)
    all_years_employees_folder_path  = root_employees_folder_path / \
                                       Path(all_years_employees_folder_alias)
    one_year_employees_folder_path   = root_employees_folder_path / \
                                       Path(one_year_employees_folder_alias)
    backup_folder_path               = bibliometer_path / Path(backup_folder_alias)

    return (months2add_employees_folder_path, all_years_employees_folder_path,
            one_year_employees_folder_path, backup_folder_path)


def _check_sheet_month(df, sheet_name):
    """The function `_check_sheet_month` checks if the mandatory column names
    of the dataframe 'df' are present and if the sheet name 'sheet_name' is
    formatted as mmyyyy where yyyy stands for the 'year' and mm stands
    for the month (always written with two digits). It returns messages
    related to the check status. The year returned is None if the sheet name
    is not correctly formatted or the month is not in possible months.

    Args:
        df (dataframe): The dataframe to be checked.
        sheet_name (str): The sheet name to be checked.

    Returns:
        (tup): Tuple of 3 strings = (year, sheet_name_error, col_error).
    """

    # Setting lists of columns
    useful_col_list = list(eg.EMPLOYEES_USEFUL_COLS.values())

    # Initializing error messages
    col_error = None
    sheet_name_error = None

    missing_column = set(useful_col_list)-set(df.columns)
    if len(missing_column)!=0:
        col_error  = f"The column(s) '{list(missing_column)}' is (are) missing or misspelled "
        col_error += f"in sheet name '{sheet_name}'."


    possible_months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    year = None
    re_mmyyyy = re.compile(r'^\d{6}$')
    if re_mmyyyy.findall(sheet_name):
        month = sheet_name[0:2]
        if month in possible_months:
            year  = sheet_name[2:6]
        else:
            sheet_name_error = (f"Month '{month}' is not among possible months "
                                f"in sheet name '{sheet_name}'.")
    else:
        sheet_name_error = (f"The sheet name '{sheet_name}' "
                            f"is not correctly formated as mmyyyy.")

    return year, sheet_name_error, col_error


def _add_sheets_to_workbook(file_full_path, df_to_add, sheet_name):
    """The function `_add_sheets_to_workbook` add the dataframe 'df_to_add'
    as sheet named 'sheet_name' to the existing Excel file
    with full path 'file_full_path'. If the sheet name already
    exists it is overwritten by the new one.
    """

    with pd.ExcelWriter(file_full_path,  # https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
                        engine = 'openpyxl',
                        mode = 'a',
                        if_sheet_exists = 'replace') as writer:
        df_to_add.to_excel(writer, sheet_name = sheet_name, index = False)

def _update_months_history(months2add_file_path,
                           one_year_employees_folder_path,
                           one_year_employees_basename_alias,
                           replace = True,):
    """The function `_update_months_history` update the file
    pointed by 'year_months_file_path' for a year.
    More specifically only the new months contained in the EXCEL file
    pointed by 'months2add_file_path' are added as new sheets
    named mmyyyy where mm stands for the month and yyyy for the year.
    The sheets are checked using the local function '_check_sheet_month'
    of the module 'BiblioMeterUpdateEmployees' of the package 'bmfuncts'.
    This function returns error messages if the sheets to add are misconfigured.
    If no error is returned, the sheets are added using the local function
    '_add_sheets_to_workbook' of the module 'BiblioMeterUpdateEmployees'
    of the package 'bmfuncts'.

    Args:
        months2add_file_path (path): Full path to the employees EXCEL file
                                     with one sheet per months to update the employees file.
        one_year_employees_folder_path (path): Full path to the folder containing
                                               the files gathering the employees per year.
        one_year_employees_basename_alias (path): Base for building the file name of the file
                                                  gathering the employees for a year.
        replace (bool): If true, existing sheets are replaced in the EXCEL file (default: True).

    Returns:
        (tuple of 5 str): (year, year_months_file_path, sheet_name_message,
                           col_message, years2add_message).

    """

    df_months_to_add = pd.read_excel(months2add_file_path, sheet_name=None)
    months_to_add = list(df_months_to_add.keys())

    years_list = []
    for month in months_to_add:
        tup = _check_sheet_month(df_months_to_add[month], month)
        month_year, month_sheet_name_error, month_col_error = tup[0], tup[1], tup[2]
        if month_sheet_name_error:
            return (None, None, month_sheet_name_error, None, None)
        if month_col_error:
            return (None, None, None, month_col_error, None)
        if month_year is None:
            return (None, None, month_sheet_name_error, None, None)
        years_list.append(month_year)

    years_list = list(set(years_list))
    if len(years_list)>1:
        years2add_error = ('Too many years covered by the file of months '
                           'to add while expected only one.')
        return None, None, None, None, years2add_error

    year = years_list[0]
    file_name = f'{year}' + one_year_employees_basename_alias
    year_months_file_path = one_year_employees_folder_path / Path(file_name)

    if os.path.isfile(year_months_file_path):
        # if the file already exits we update with new sheets
        df_months_dict = pd.read_excel(year_months_file_path, sheet_name=None)
        if not replace: # we only add missing months
            months_present = list(df_months_dict.keys())
            months_to_add  = list(set(months_to_add) - set(months_present))
            months_to_add  = sorted(months_to_add)
        for month in months_to_add:
            _add_sheets_to_workbook(year_months_file_path, df_months_to_add[month], month)

    else:
        # if the file is not present we create a new Excel file with one sheet per month
        month = months_to_add[0]
        # we add the first month
        df_months_to_add[month].to_excel(year_months_file_path, sheet_name=month)
        for month in months_to_add[1:]:
            # we add the other months
            _add_sheets_to_workbook(year_months_file_path, df_months_to_add[month], month)

    return year, year_months_file_path, None, None, None


def _add_column_keep_history(df):
    """The function `_add_column_keep_history` creates 4 new columns
    defined by the global 'EFFECTIF_ADD_COLS' at the keys 'dpts_list',
    'servs_list', 'months_list' and 'years_list'.
    These columns contain, for each employee, the lists of its departments
    and services affiliation per available months.
        ex: if for an employee the column of key 'months_list' contains
        ['01', '02', '03', '04', '05', '06', '07', '08', '09']
        and the colummn of key dpts_list' contains
        ['DTCH', 'DTCH', 'DTCH', 'DTNM', 'DTNM', 'DTNM', 'DTNM', 'DTNM', 'DTNM'],
        then the employee was part of 'DTCH' from January to March and was part
        of 'DTNM' from April to September.
    The function uses the columns defined by the global `EMPLOYEES_USEFUL_COLS`
    at keys 'dpt' and 'serv' that contain, for each employee,
    a list of at most 12 tuples:
        [(mm_1, yyyy_1, dep_1),(mm_2, yyyy_2, dep_2), ..., (mm_n, yyyy_n, dep_n)]
    witch are re-casted in 3 lists [mm_1, mm_2, ..., mm_n],
        [yyyy_1, yyyy_2, ..., yyyy_n], [dep_1, dep_2, ..., dep_n].

    Args:
        df (dataframe): The dataframe to which the 4 columns are added.

    Returns:
        (dataframe): The updated dataframe.
    """

    # Setting useful aliases
    col_eff_dpt_alias     = eg.EMPLOYEES_USEFUL_COLS['dpt']
    col_eff_service_alias = eg.EMPLOYEES_USEFUL_COLS['serv']
    col_add_dpts_alias    = eg.EMPLOYEES_ADD_COLS['dpts_list']
    col_add_servs_alias   = eg.EMPLOYEES_ADD_COLS['servs_list']
    col_add_month_alias   = eg.EMPLOYEES_ADD_COLS['months_list']
    col_add_year_alias    = eg.EMPLOYEES_ADD_COLS['years_list']

    # Converting the list of tuples[(mm_1, yyyy_1, item_1), ...(mm_n, yyyy_n, item_n)]
    # into a list of 3 lists [[mm_1,...,mm_n], [yyyy_1,....yyyy_n],[item_1,....,item_n]]
    # where 'item' stands for department.
    # The 2 lists of 3 lists are put into the two new columns
    # named 'col_add_dpts_alias' and 'col_add_servs_alias'
    cols_tup_list = [(col_eff_dpt_alias, col_add_dpts_alias),
                     (col_eff_service_alias, col_add_servs_alias)]
    for cols_tup in cols_tup_list:
        col_in, col_out =  cols_tup[0], cols_tup[1]
        df[col_out] = df[col_in].apply(lambda x: [list(x) for x in list(zip(*x))])

    # Exploding the 2 lists of 3 lists into the columns
    # named 'months', 'years', 'Dpts' and 'Servs'
    for col in [col_add_dpts_alias, col_add_servs_alias]:
        new_col = [col_add_month_alias,col_add_year_alias,col]
        df[new_col] = pd.DataFrame(df[col].tolist(), index = df.index)

    return df


def _add_column_firstname_initial(df):
    """The function `_add_column_firstname_initial` adds a new column defined by
    the global 'EMPLOYEES_ADD_COLS' at the key 'first_name_initials' containing
    the initials of the firstname.
        ex: PIERRE -->P, JEAN-PIERRE --> JP , JEAN-PIERRE MARIE --> JPM.
    It uses the columns defined by the global `EMPLOYEES_USEFUL_COLS` at key 'first_name'
    that contains the full first name for each employee.

    Args:
        df (dataframe): The dataframe to which the column is added.

    Returns:
        (dataframe): The updated dataframe.
    """

    # Internal functions
    def _get_firstname_initials(row):
        row = row[0] if isinstance(row, list) else row
        row = row.replace('-',' ')
        row_list = row.split(' ')
        initial_list = [x[0] for x in row_list]
        initials = ''.join(initial_list)
        return initials

    col_in  = eg.EMPLOYEES_USEFUL_COLS['first_name']
    col_out = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    df[col_out] = df[col_in].apply(_get_firstname_initials)
    return df


def _add_column_full_name(df):
    """The function `_add_column_full_name` adds a new column defined by
    the global 'EMPLOYEES_ADD_COLS' at the key 'employee_full_name' containing
    the employee full name composed by the last name and the first name initials.
        ex: if last name is SIMONATO and first name initials are JP --> full name is SIMONATO JP.
    It uses the columns defined by the global `EMPLOYEES_USEFUL_COLS` at key 'name'
    that contains the last name for each employee and it uses the previously added column
    defined by the global `EMPLOYEES_ADD_COLS` at key 'first_name_initials'.

    Args:
        df (dataframe): The dataframe to which the column is added.

    Returns:
        (dataframe): The updated dataframe.
    """

    col_last_name_alias          = eg.EMPLOYEES_USEFUL_COLS['name']
    col_first_name_initial_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    col_full_name_alias          = eg.EMPLOYEES_ADD_COLS['employee_full_name']

    df[col_full_name_alias] = df[col_last_name_alias] + ' ' + df[col_first_name_initial_alias]

    return df


def _select_employee_dpt_and_serv(df):
    """The function `_select_employee_dpt_and_serv` select the department
    and the service of an employee among the list of departments
    and services of affiliation during the year.
    The rule is to choose the department and the service corresponding
    to the first available month of the year.
        ex: The column defined by the global  'EMPLOYEES_USEFUL_COLS'
        at key 'dpt' contains the list of tuples (mm, yyyy, dpt) such as
        x = [('04', '2019', 'DTBH'), ('05', '2019', 'DTBH'),
        ('06', '2019', 'DTNM'), ..., ('12', '2019', 'DTNM')].
        We select DTBH = x[0][-1] as the first occurrence.
        The last occurrence would be DTNM = x[-1][-1].

    Args:
        df (dataframe): The dataframe to be modified.

    Returns:
        (dataframe): The updated dataframe.

    Note:
        A more fair full allocation would be department/service where the employee
        spent the maximum time during the year
        using: lambda x: max((count := Counter([y[2] for y in x])), key = count.get)
        where 'Counter' is a method of 'collections'.

    """

    col_dpt_alias  = eg.EMPLOYEES_USEFUL_COLS['dpt']
    col_serv_alias = eg.EMPLOYEES_USEFUL_COLS['serv']

    cols_list = [col_dpt_alias, col_serv_alias]
    for col in cols_list:
        df[col] = df[col].apply(lambda x: x[0][-1])

    return df


def _build_year_month_dpt(year_months_file_path):
    """The function `_build_year_month_dpt` builds a dataframe
    for a year by merging all employees information available
    by month in an Excel workbook, which full path is defined
    by the variable 'year_months_file_path'.
    This workbook contains a worksheet per month.
    These worksheets are labelled mmyyyy where mm stands for the month
    (01, 02, ..., 12) and yyyy stands for the year (2019, 2020, ...).
    All the worksheets must at least contain the columns which names
    are defined by the keys 'matricule', 'first_name', 'name', 'dpt'
    and 'serv' in the global 'EMPLOYEES_USEFUL_COLS'.
    The function merges the list of sheets and builds the new columns
    defined by the global 'EMPLOYEES_ADD_COLS' using the local functions
    '_add_column_keep_history', '_add_column_firstname_initial' and '_add_column_full_name'
    of the module 'update_employees' of the package 'bmfuncts'.
    The columns added at keys 'months_list', 'years_list', 'dpts_list' and 'servs_list'
    contains lists formated as : [item_1, item_2, ... items_n] of the n items
    of the n available months and where item_i stands for month, year, department
    and service respectively.
    Finally, a single department and service is selected for each employee using
    the local function '_select_employee_dpt_and_serv' of the module 'update_employees'
    of the package 'bmfuncts'.

    Args:
       year_months_file_path (path): The path to the Excel file
                                     that contains a sheet per month of a year.

    Returns:
       (dataframe): The built employees dataframe.

    Notes:
        The globals EMPLOYEES_ADD_COLS and EMPLOYEES_USEFUL_COLS are imported
        from the module 'employees_globals' of the package 'bmfuncts'.

    """

    # Internal functions
    def _set_tup(month, year):
        return lambda x: (month, year, x)

    # Setting lists of columns
    useful_col_list = list(eg.EMPLOYEES_USEFUL_COLS.values())
    add_col_list    = list(eg.EMPLOYEES_ADD_COLS.values())

    # Setting useful aliases from globals
    dpt_col_alias       = eg.EMPLOYEES_USEFUL_COLS['dpt']
    firstname_col_alias = eg.EMPLOYEES_USEFUL_COLS['first_name']
    name_col_alias      = eg.EMPLOYEES_USEFUL_COLS['name']
    matricule_col_alias = eg.EMPLOYEES_USEFUL_COLS['matricule']
    serv_col_alias      = eg.EMPLOYEES_USEFUL_COLS['serv']

    # Reading the sheets from the excel file as a dict
    # {sheet-name: sheet-content dataframe}
    df_dict = pd.read_excel(year_months_file_path,
                            sheet_name = None,
                            usecols = useful_col_list)

    # Concatenating the sheets from the 'sheet_names'
    # list into the dataframe 'df_eff_year'
    list_df_eff_month = []
    for sheet_name,df_eff_month in df_dict.items():
        month = sheet_name[0:2]  # Extraction of the month mm for the sheet name mmyyyy
        year = sheet_name[2:]    # Extraction of year yyyy for the sheet name mmyyyy

        # For the sheet 'sheet_name' of the dataframe 'df_eff_month'
        # replacing each cell of column 'dpt_col_alias'/'serv_col_alias' that specifies
        # the employee department dpt/service by a tuple (month,year,dpt)/(month,year,serv)
        for col_keep_history in [dpt_col_alias, serv_col_alias]:
            df_eff_month[col_keep_history] = df_eff_month[col_keep_history].\
                                             apply(_set_tup(month, year))

        list_df_eff_month.append(df_eff_month)

    df_eff_year = pd.concat(list_df_eff_month, axis=0)

    # Aggregating all the information related to one matriculate
    # as a list without duplicates, for each column (except 'Matricule')
    df_eff_year_singlemat = df_eff_year.groupby(matricule_col_alias).\
                                                agg(lambda x :list(dict.fromkeys(x))).\
                                                reset_index()

    # Recasting lists into string if its length is equal to 1
    col_set = {matricule_col_alias,
               name_col_alias,
               serv_col_alias,
               dpt_col_alias,
               firstname_col_alias}
    for col in set(useful_col_list) - col_set:
        df_eff_year_singlemat[col] = df_eff_year_singlemat[col].\
                                     apply(lambda x: x[0] if len(x)==1 else list(x))

    # Dealing with same matriculate for different lastnames and firstnames
    employees_df = df_eff_year_singlemat.explode([name_col_alias])
    employees_df = employees_df.explode([firstname_col_alias])

    # Adding 6 new columns
    employees_df = _add_column_keep_history(employees_df)
    employees_df = _add_column_firstname_initial(employees_df)
    employees_df = _add_column_full_name(employees_df)
    employees_df = _select_employee_dpt_and_serv(employees_df)

    employees_df = employees_df[useful_col_list + add_col_list]

    return employees_df


def update_employees(bibliometer_path, progress_callback=None, replace = True):
    """The function `update_employees` update the file defined by the global
    'EMPLOYEES_ARCHI' at key 'employees_file_name' using the file defined
    by the global 'EMPLOYEES_ARCHI' at key "one_year_employees_filebase"
    and the year 'year'.

    Args:
        bibliometer_path (path): The path to the working folder.
        progress_callback (function): Function for updating ProgressBar 
                                      tkinter widget status (default = None).
        replace (bool): Optional (default = True); if true, existing sheets
                        are replaced in employees EXCEL files specific to a year.

    Returns:
        (tuple): Tuple of 5 strings; a first string giving the employees year
                 if no error is raised; then 4 strings specifying errors related
                 respectively to files number, sheet-name, column name and number
                 of years to update; these 4 strings are set to "None" when no error is raised.

    """

    # Setting useful file name aliases
    one_year_employees_basename_alias = eg.EMPLOYEES_ARCHI["one_year_employees_filebase"]
    all_years_employees_file_alias    = eg.EMPLOYEES_ARCHI["employees_file_name"]

    # Getting useful employees paths
    (months2add_employees_folder_path,
     all_years_employees_folder_path,
     one_year_employees_folder_path,
     backup_folder_path) = _set_employees_paths(bibliometer_path)

    # Setting full paths to useful files
    all_years_file_path        = all_years_employees_folder_path / \
                                 Path(all_years_employees_file_alias)
    all_years_file_backup_path = backup_folder_path / Path(all_years_employees_file_alias)

    # Setting the list of files available to add (expected only one)
    months2add_files = [file for file in os.listdir(months2add_employees_folder_path)
                             if file.endswith(".xlsx") and file[0] != '~']
    if progress_callback:
        progress_callback(15)

    if len(months2add_files)>1:
        files_number_error = (f"Too many files present in  '{months2add_employees_folder_path}' "
                              "while expecting only one")
        return None, files_number_error, None, None, None, None
    if not months2add_files:
        files_number_error = (f"No file present in '{months2add_employees_folder_path}', "
                              "no update possible")
        return None, files_number_error, None, None, None, None

    months2add_file_path = months2add_employees_folder_path / Path(months2add_files[0])

    (employees_year,
     year_months_file_path,
     sheet_name_error,
     column_error,
     years2add_error) = _update_months_history(months2add_file_path,
                                               one_year_employees_folder_path,
                                               one_year_employees_basename_alias,
                                               replace)
    if progress_callback:
        progress_callback(20)

    if employees_year is None or year_months_file_path is None:
        return None, None, sheet_name_error, column_error, years2add_error, None

    # Building the dataframe employees_df by concatenating
    # the months of the current year
    employees_df = _build_year_month_dpt(year_months_file_path)
    if progress_callback:
        progress_callback(25)

    # Saving employees_df as a sheet mame after employees_year,
    # in the workbook pointed by all_years_file_path
    all_years_file_status = os.path.exists(all_years_file_path)
    all_years_file_backup_status = os.path.exists(all_years_file_backup_path)
    all_years_file_error = None
    if all_years_file_status:
        _add_sheets_to_workbook(all_years_file_path, employees_df, employees_year)
    elif all_years_file_backup_status:
        _ = shutil.copy(all_years_file_backup_path, all_years_file_path)
        _add_sheets_to_workbook(all_years_file_path, employees_df, employees_year)
        all_years_file_error  = ("The file:"
                                 f"\n '{all_years_file_path}' \n"
                                 "\nhas been copied from the backup file:"
                                 f"\n '{all_years_file_backup_path}' \n"
                                 "\nand then updated.")
    else:
        employees_df.to_excel(all_years_file_path, sheet_name=employees_year)
        all_years_file_error  = f"The file '{all_years_file_path}' has been "
        all_years_file_error += f"created with a sheet named '{employees_year}'"

    # Copying the all-years employees file updated to the backup folder
    shutil.copy(all_years_file_path, backup_folder_path)

    return employees_year, None, None, None, None, all_years_file_error
