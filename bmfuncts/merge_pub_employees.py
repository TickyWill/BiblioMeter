"""Module of functions for the merge of employees information with the publications list 
of the Institute taking care of:

- Creation of list of Institute authors with selected attributes;
- Creation of full reference for each publication;
- Creation of publications hash-ID

"""

__all__ = ['recursive_year_search',
          ]


# Standard Library imports
import warnings
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.pub_globals as bm_pg
from bmfuncts.build_pub_authors import build_institute_pubs_authors_data
from bmfuncts.build_year_pub_empl import build_pub_empl_data
from bmfuncts.create_hash_id import create_hash_id
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import keep_initials
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import print_temp_text
from bmfuncts.useful_functs import set_year_pub_id
from bmfuncts.useful_functs import standardize_full_name_order
from bmfuncts.useful_functs import standardize_txt


def _add_author_job_type(merge_df, empl_dict, years, cols_list):
    """Adds a new column containing the job type for each author 
    of the publications list with one row per author.

    The job type is got from the employee information available 
    in 3 columns which names are given by 'category_col', 
    'status_col' and 'qualification_col'. 
    The name of the new column is given by 'author_type_col'. 

    Args:
        merge_df (dataframe): The data of the publications list \
        with one row per author with attributes as Institute employee.
        empl_dict (dict): The employees database as a dict keyed by the years \
        and valued by the employees data for each year.
        years (list): The years list for recursive search in the employees' database.
        cols_list (list): The useful column names.
    Returns:
        (str): End message recalling the full path to the saved file of \
        the modified publications list.
    """
    # internal functions:
    def _get_mat_author_type(_col_name, _dic, _year_mat_df, _set_author_type):
        mat_value = ""
        if not _year_mat_df[_col_name].empty:
            mat_value = list(_year_mat_df[_col_name])[0]
        for key, values_list in _dic.items():
            values_status = [True for value in values_list if value in mat_value]
            if any(values_status):
                _set_author_type = key
        return _set_author_type

    def _search_mat_author_type(_mat):
        years_nb = len(years)
        year_idx = 0
        set_author_type = "FIN"
        while set_author_type=="FIN" and year_idx<years_nb:
            year_empl_df = empl_dict[years[year_idx]]
            year_mat_df = year_empl_df[year_empl_df[mat_col]==str(_mat)]
            for col_name, dic in author_types_dic.items():
                set_author_type = _get_mat_author_type(col_name, dic,
                                                       year_mat_df, set_author_type)
            year_idx += 1
        author_type = set_author_type
        return author_type

    def _get_ext_author_type(_mat_value, _dic, _author_type):
        for key, values_list in _dic.items():
            values_status = [True for value in values_list if value in _mat_value]
            if any(values_status):
                _author_type = key
                break
        return _author_type

    def _search_ext_author_type(_row):
        author_type = 'Coll'
        for col_name, dic in author_types_dic.items():
            mat_value = _row[col_name]
            author_type = _get_ext_author_type(mat_value, dic, author_type)
            if author_type!='Coll':
                break
        return author_type

    def _get_author_type(row):
        mat = row[mat_col]
        if mat!="externe":
            author_type = _search_mat_author_type(mat)
        else:
            author_type = _search_ext_author_type(row)
        return author_type

    # Setting col names from cols_list
    (author_type_col, mat_col, category_col,
     status_col, qualification_col) = cols_list

    author_types_dic = {category_col      : bm_eg.CATEGORIES_DIC,
                        status_col        : bm_eg.STATUS_DIC,
                        qualification_col : bm_eg.QUALIFICATION_DIC}
    merge_df[author_type_col] = merge_df.apply(_get_author_type, axis=1)
    return merge_df


def _set_full_ref(title, first_author, journal_name, pub_year, doi):
    """Builds the full reference of a publication.

    Args:
        title (str): Title of the publication.
        first_author (str): First author of the publication formated as 'NAME IJ' \
        with 'NAME' the lastname and 'IJ' the initials of the firstname of the author.
        journal_name (str): Name of the journal where the publication is published.
        pub_year (str): Publication year defined by 4 digits.
        doi (str): Digital identification of the publication.
    Returns:
        (str): Full reference of the publication.
    """
    full_ref  = f'{title}, '                     # adds the reference's title
    full_ref += f'{first_author} et al., '       # adds the reference's first author
    full_ref += f'{journal_name.capitalize()}, ' # adds the reference's journal name
    full_ref += f'{pub_year}, '                  # adds the reference's publication year
    full_ref += f'{doi}'                         # adds the reference's DOI
    return full_ref


def _add_biblio_list(merge_df, cols_list):
    """Adds a new column containing the full reference of each publication 
    of the publications list with one row per author.

    The full reference is built by concatenating the following items:
    title, first author, year, journal, DOI. 
    These items are got from the columns which names are given by 
    'title_col', 'first_author_col', 'year_col', 
    'journal_col' and 'doi_col', respectively. 
    The name of the new column is given by 'full_ref_col'.

    Args:
        merge_df (dataframe): The data of the publications list \
        with one row per author with attributes as Institute employee.
        cols_list (list): The useful column names.
    Returns:
        (str): End message recalling the full path to the saved file \
        of the modified publications list.
    """
    # Setting col names from cols_list
    (full_ref_col, pub_id_col, first_author_col,
     year_col, journal_col, doi_col, title_col) = cols_list

    new_merge_df = pd.DataFrame()
    # Splitting the data into subdata with same Pub_id
    for _, pub_id_df in merge_df.groupby(pub_id_col):
        # Select the first row and build the full reference
        pub_id_first_row = pub_id_df.iloc[0]
        title = str(pub_id_first_row[title_col])
        first_author = str(pub_id_first_row[first_author_col])
        first_author = standardize_full_name_order(first_author)
        journal_name = str(pub_id_first_row[journal_col])
        pub_year = str(pub_id_first_row[year_col])
        doi = str(pub_id_first_row[doi_col])
        pub_id_df[full_ref_col] = _set_full_ref(title, first_author,
                                                journal_name, pub_year, doi)
        new_merge_df = concat_dfs([new_merge_df, pub_id_df])
    return new_merge_df


def _add_ext_auth(ext_row, orphan_row, new_merge_adds_df, orphan_drop_df, cols_list):
    (ext_auth_lastname_col, ext_auth_firstname_short_cols, orphan_fullname_col,
     ext_empl_fullname_col) = cols_list

    # Setting the row to move from init_orphan_df as a dataframe
    row_to_move_df = orphan_row.to_frame().T

    # Setting the row to copy from ext_docs_df as a dataframe
    row_to_copy_df = ext_row.to_frame().T

    # Dropping the columns of 'row_to_copy_df' data that should not be present in 'row_to_add_df' data
    row_to_copy_df = row_to_copy_df.drop([ext_auth_lastname_col, ext_auth_firstname_short_cols], axis=1)

    # Merging the two dataframes on respective full name column
    row_to_add_df = pd.merge(row_to_move_df, row_to_copy_df, left_on=[orphan_fullname_col],
                             right_on=[ext_empl_fullname_col], how='left')

    # Appending the merged df to 'new_merge_adds_df' data
    new_merge_adds_df = concat_dfs([new_merge_adds_df, row_to_add_df], concat_ignore_index=True)

    # Appending row_to_move_df to 'orphan_drop_df' data
    orphan_drop_df = concat_dfs([orphan_drop_df, row_to_move_df], concat_ignore_index=True)
    return new_merge_adds_df, orphan_drop_df


def _add_ext_docs(init_merge_df, init_orphan_df, ext_docs_path, cols_list, print_params):
    """Adds to the publications-list dataframe with one row per author 
    new rows containing the information of specific authors.

    The specific authors are PhD students at the Institute but not as employees of it. 
    The list of these PhD students with the required information is got from 
    the xlsx file which full path is given by 'ext_docs_path' in sheet which 
    name is given by 'SHEET_NAMES_ORPHAN["docs to add"]' global imported from 
    `bmfunct.pub_globals` module. 
    The row of the added PhD students is dropped in the publications list 
    with one row per author that has not been identified as Institute employee.

    Args:
        init_merge_df (dataframe): The data of the publications list \
        with one row per author with attributes as Institute employee.
        init_orphan_df (dataframe): The data of the publications list \
        with one row per author that has not been identified as Institute employee.
        ext_docs_path (path): Full path to the XLSX file giving the PhD students \
        at the Institute but not employees of it.
        cols_list (list): The useful column names.
    Returns:
        (tup): (updated dataframe of the publications list with one row \
        per Institute author including external PhD students, updated dataframe \
        of publications list with one row per author that has not been identified \
        as Institute employee).
    Note:
        Care is taken to keep 'NA' value for the first name initials \
        that are set to NaN by default through the `keep_initials` function \
        imported from "bmfuncts.useful_functs" internal module.
    """
    # Setting col names from cols_list
    (pub_id_col, author_id_col, orphan_fullname_col, ext_empl_fullname_col, orphan_lastname_col,
     ext_auth_lastname_col, merge_firstname_short_col, ext_auth_firstname_short_cols) = cols_list

    # Replace in "init_merge_df" data and "init_orphan_df" data, NaN values
    # except "NA" in first name initials
    init_merge_df = keep_initials(init_merge_df, merge_firstname_short_col, missing_fill=bm_pg.UNKNOWN)
    init_orphan_df = keep_initials(init_orphan_df, merge_firstname_short_col, missing_fill=bm_pg.UNKNOWN)

    # Initializing the data to be concatenated with init_merge_df
    # with same column names as init_merge_df
    new_merge_adds_df = pd.DataFrame(columns=list(init_merge_df.columns))

    # Aligning column names between init_merge_df and init_orphan_df
    # to feed new_merge_adds_df with same column names as init_merge_df
    col_rename_dic = {merge_firstname_short_col : merge_firstname_short_col + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_firstname_short_col = col_rename_dic[merge_firstname_short_col]

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external-PhD-students XLSX file using the same useful columns
    # as init_merge_df defined by EXT_DOCS_USEFUL_COL_LIST with dates conversion
    # through converters_alias and drop of empty rows
    ext_docs_usecols = sum([[ext_auth_lastname_col, ext_auth_firstname_short_cols],
                            bm_pg.EXT_DOCS_COL_ADDS_LIST, bm_eg.EXT_DOCS_USEFUL_COL_LIST,], [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    ext_docs_df = pd.read_excel(ext_docs_path, sheet_name=bm_pg.SHEET_NAMES_ORPHAN["docs to add"],
                                usecols=ext_docs_usecols, converters=bm_eg.EMPLOYEES_CONVERTERS_DIC)

    # Replace in "ext_docs_df" NaN values "NA" in first name initials
    ext_docs_df = keep_initials(ext_docs_df, ext_auth_firstname_short_cols)
    ext_docs_df = ext_docs_df.dropna(how='any')

    # Searching for last names of init_orphan_df in ext_docs_df
    # to update 'merge_df' and 'orphan_df' data using 'new_merge_adds_df' and 'orphan_drop_df' data
    sub_cols_list = [ext_auth_lastname_col, ext_auth_firstname_short_cols, orphan_fullname_col, ext_empl_fullname_col]
    txt_len = 0
    orphan_lines_nb, orphan_nb = len(init_orphan_df), 0
    for _, orphan_row in init_orphan_df.iterrows():
        orphan_nb += 1
        txt_len = print_temp_text(f"{bm_pg.TAB*2}- Search authors as external PhD students of the Institute:"
                                  f"{bm_pg.TAB}{orphan_nb} / {orphan_lines_nb}", txt_end=True)
        author_last_name = str(orphan_row[orphan_lastname_col])
        author_last_name = standardize_txt(author_last_name)
        author_initials = str(orphan_row[orphan_firstname_short_col])
        for _, ext_docs_row in ext_docs_df.iterrows():
            ext_docs_pub_last_name = str(ext_docs_row[ext_auth_lastname_col])
            ext_docs_pub_last_name = standardize_txt(ext_docs_pub_last_name)
            ext_docs_pub_initials = str(ext_docs_row[ext_auth_firstname_short_cols])
            if ext_docs_pub_last_name==author_last_name and ext_docs_pub_initials==author_initials:
                return_tup = _add_ext_auth(ext_docs_row, orphan_row, new_merge_adds_df, orphan_drop_df, sub_cols_list)
                new_merge_adds_df, orphan_drop_df = return_tup

    # Concatenating init_merge_df and new_merge_adds_df
    new_merge_df = concat_dfs([init_merge_df, new_merge_adds_df])
    new_merge_df = new_merge_df.sort_values([pub_id_col, author_id_col])

    # Dropping orphan_drop_df rows from init_orphan_df
    new_orphan_df = concat_dfs([init_orphan_df, orphan_drop_df], keep='False')

    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {merge_firstname_short_col + "_x":\
                             merge_firstname_short_col}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    print_step_text(f"{bm_pg.TAB*2}- Authors searched as external PhD students",
                    print_params, prev_txt_len=txt_len)
    return new_merge_df, new_orphan_df


def _add_other_ext(init_merge_df, init_orphan_df, others_path, cols_list, print_params):
    """Adds to the publications-list dataframe with one row per author 
    new rows containing the information of specific authors.

    The specific authors are under external hiring contract at the Institute. 
    The list of these employees with the required information is got from 
    the xlsx file which full path is given by 'others_path' in sheet which 
    name is given by 'SHEET_NAMES_ORPHAN["others to add"]' global imported from 
    `bmfunct.pub_globals` module. 
    The row of the added employees is dropped in the publications list 
    with one row per author that has not been identified as Institute employee.

    Args:
        init_merge_df (dataframe): The data of the publications list \
        with one row per author with attributes as Institute employee.
        init_orphan_df (dataframe): The data of the publications list \
        with one row per author that has not been identified as Institute employee.
        others_path (path): Full path to the XLSX file giving the employees \
        under external hiring contract at the Institute.
        cols_list (list): The useful column names.
    Returns:
        (tup): (updated dataframe of the publications list with one row \
        per Institute author including employees under external hiring contract \
        at the Institute, updated dataframe of publications list with one row \
        per author that has not been identified as Institute employee).
    Note:
        For the first name initials, care is taken to keep 'NA' value \
        to avoid setting to NaN by default, through the `keep_initials` function \
        imported from "bmfuncts.useful_functs" internal module.
    """
    # Setting col names from cols_list
    (pub_id_col, author_id_col, orphan_fullname_col, ext_empl_fullname_col, orphan_lastname_col,
     ext_auth_lastname_col, merge_firstname_short_col, ext_auth_firstname_short_cols) = cols_list

    # Replace in "init_merge_df" data and "init_orphan_df" data, NaN values
    # except "NA" in first name initials
    init_merge_df = keep_initials(init_merge_df, merge_firstname_short_col, missing_fill=bm_pg.UNKNOWN)
    init_orphan_df = keep_initials(init_orphan_df, merge_firstname_short_col, missing_fill=bm_pg.UNKNOWN)

    # Initializing the data to be concatenated to 'init_merge_df' data in 'new_merge_df' data
    # with same column names as init_merge_df
    new_merge_adds_df = pd.DataFrame(columns=list(init_merge_df.columns))

    # Aligning column names between init_merge_df and init_orphan_df
    # to feed new_merge_adds_df with same column names as init_merge_df
    col_rename_dic = {merge_firstname_short_col : merge_firstname_short_col + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_firstname_short_col = col_rename_dic[merge_firstname_short_col]

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external-collaborators XLSX file using the same useful columns
    # as init_merge_df defined by EXT_DOCS_USEFUL_COL_LIST with dates conversion
    # through converters_alias and drop of empty rows
    others_usecols = sum([[ext_auth_lastname_col, ext_auth_firstname_short_cols],
                          bm_pg.EXT_DOCS_COL_ADDS_LIST, bm_eg.EXT_DOCS_USEFUL_COL_LIST,], [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    others_df = pd.read_excel(others_path, sheet_name=bm_pg.SHEET_NAMES_ORPHAN["others to add"],
                              usecols=others_usecols, converters=bm_eg.EMPLOYEES_CONVERTERS_DIC)

    # Replace in "other_df" NaN values "NA" in first name initials
    others_df = keep_initials(others_df, ext_auth_firstname_short_cols)
    others_df = others_df.dropna(how='any')

    # Searching for last names of init_orphan_df in others_df
    # to update 'merge_df' and 'orphan_df' data using 'new_merge_adds_df' and 'orphan_drop_df' data
    sub_cols_list = [ext_auth_lastname_col, ext_auth_firstname_short_cols, orphan_fullname_col, ext_empl_fullname_col]
    txt_len = 0
    orphan_lines_nb, orphan_nb = len(init_orphan_df), 0
    for _, orphan_row in init_orphan_df.iterrows():
        orphan_nb += 1
        txt_len = print_temp_text(f"{bm_pg.TAB*2}- Search authors as other external collaborators:"
                                  f"{bm_pg.TAB}{orphan_nb} / {orphan_lines_nb}", txt_end=True)
        author_last_name = str(orphan_row[orphan_lastname_col])
        author_last_name = standardize_txt(author_last_name)
        author_initials = str(orphan_row[orphan_firstname_short_col])
        for _, others_row in others_df.iterrows():
            others_pub_last_name = str(others_row[ext_auth_lastname_col])
            others_pub_last_name = standardize_txt(others_pub_last_name)
            others_pub_initials = str(others_row[ext_auth_firstname_short_cols])
            if others_pub_last_name==author_last_name and others_pub_initials==author_initials:
                return_tup = _add_ext_auth(others_row, orphan_row, new_merge_adds_df, orphan_drop_df, sub_cols_list)
                new_merge_adds_df, orphan_drop_df = return_tup

    # Concatenating 'init_merge_df' data and 'new_merge_adds_df' data
    new_merge_df = concat_dfs([init_merge_df, new_merge_adds_df])
    new_merge_df = new_merge_df.sort_values([pub_id_col, author_id_col])

    # Dropping 'orphan_drop_df' data from 'init_orphan_df' data
    new_orphan_df = concat_dfs([init_orphan_df, orphan_drop_df], keep='False')

    # Recovering the initial column names of 'init_orphan_df' data
    col_invert_rename_dic = {merge_firstname_short_col + "_x": merge_firstname_short_col}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    print_step_text(f"{bm_pg.TAB*2}- Authors searched as other external collaborators",
                    print_params, prev_txt_len=txt_len)
    return new_merge_df, new_orphan_df


def _change_col_names(institute, org_tup, merge_df, orphan_df):
    """Renames the columns of the two data passed as args according to conversion dicts.

    The conversion dicts are built through the  the `build_col_conversion_dic` function 
    imported from `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute's name.
        org_tup (tup): Contains Institute's parameters.
        merge_df (dataframe): The data of the publications list \
        with one row per author with attributes as Institute's employee.
        orphan_df (dataframe): The data of the publications list \
        with one row per author that has not been identified as Institute's employee.
    Returns:
        (tup): The  two data with renamed columns.
    """
    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    orphan_col_rename_dic = col_rename_tup[0]
    merge_col_rename_dic = col_rename_tup[1]

    # Renaming columns
    merge_df = merge_df.rename(columns=merge_col_rename_dic)
    orphan_df = orphan_df.rename(columns=orphan_col_rename_dic)
    return merge_df, orphan_df


def _split_orphan(org_tup, merge_folder_path, orphan_path, orphan_file, orphan_df, verbose=False):
    """Splits the publications list with one row per author that has not been identified 
    as Institute employees.

    The split is in separate lists of publications depending on values in columns 
    given by 'inst_col_list' list that is specific to the Institute. Some lists 
    of publications identified by 'orphan_drop_dict' dict that is specific to 
    the Institute, are dropped from the initial publications list with one row 
    per author that has not been identified as Institute employees. The lists 
    resulting from the split are saved as XLSX files in the folder which full path 
    is given by 'orphan_path'.

    Args:
        org_tup (tup): Contains Institute parameters.
        merge_folder_path (path): Full path to working folder.
        orphan_file (str): File name of the xlsx file of the publications list \
        with one row per author that has not been identified as Institute employee.
        orphan_df (dataframe): The data of the publications list \
        with one row per author that has not been identified as Institute employee.
        verbose (bool): Status of prints (default: False).
    Returns:
        (dataframe): The publications' list with authors \
        not found in the employees' data.
    """
    # Internal function
    def _save_inst_col_df(_inst_col, df_to_save):
        if _inst_col=="all_undrop":
            file_path = orphan_path
        else:
            file_name = _inst_col + "_" + orphan_file
            file_path = merge_folder_path / Path(file_name)
        df_to_save.to_excel(file_path, index=False)
        if verbose:
            message = f"\tFile of orphan authors created for Institute subdivision: {_inst_col}"
            print(message)

    # Setting useful column names list and dropping status
    inst_col_list = org_tup[4]
    orphan_drop_dict = org_tup[10]

    # Creating, and saving as a XLSX file, orphan authors for each Institute subdivision
    institute_df = orphan_df.copy()
    new_orphan_df = orphan_df.copy()
    dropped_indexes = set()
    for inst_col in inst_col_list[1:]:
        inst_col_df = orphan_df[orphan_df[inst_col]==1]
        _save_inst_col_df(inst_col, inst_col_df)
        indexes_to_drop = list(set(inst_col_df.index) - dropped_indexes)
        institute_df = institute_df.drop(indexes_to_drop)
        dropped_indexes = set(inst_col_df.index)
        if orphan_drop_dict[inst_col]:
            new_orphan_df = new_orphan_df.drop(inst_col_df.index)
    _save_inst_col_df(inst_col_list[0], institute_df)
    _save_inst_col_df("all_undrop", new_orphan_df)
    return new_orphan_df


def _set_ext_files_paths(wf_path):
    """Builds the full path to file of the employees external 
    to the institute.

    Args:
        wf_path (path): The full path to working folder.
    Returns:
        (path): The built full path.
    """
    orphan_treat_alias = bm_pg.ARCHI_ORPHAN["root"]
    adds_file_alias = bm_pg.ARCHI_ORPHAN["employees adds file"]

    # Setting useful path
    ext_empl_path = wf_path / Path(orphan_treat_alias) / Path(adds_file_alias)
    return ext_empl_path


def _set_merge_cols_lists():
    """Sets lists of names of useful columns for the module from globals.
    """
    # Setting the names of columns that will be added to the data
    author_type_col, full_ref_col = (bm_pg.COL_NAMES_ADD['author_type'],
                                     bm_pg.COL_NAMES_ADD['liste biblio'])

    # Setting the names of IDs columns
    pub_id_col, author_id_col, mat_col = (bm_pg.COL_NAMES['pub_id'],
                                          bm_pg.COL_NAMES['authors'][1],
                                          bm_eg.EMPLOYEES_USEFUL_COLS['matricule'])

    # Setting the names of columns of publications info
    pub_cols_list = [bm_pg.COL_NAMES['articles'][1],
                     bm_pg.COL_NAMES['articles'][2],
                     bm_pg.COL_NAMES['articles'][3],
                     bm_pg.COL_NAMES['articles'][6],
                     bm_pg.COL_NAMES['articles'][9]]

    # Setting the names of columns of job types in employees data
    job_cols_list = [bm_eg.EMPLOYEES_USEFUL_COLS['category'],
                     bm_eg.EMPLOYEES_USEFUL_COLS['status'],
                     bm_eg.EMPLOYEES_USEFUL_COLS['qualification']]

    # Setting the names of columns of full names in data
    fullname_cols_list = [bm_pg.COL_NAMES_ADD['full_name'],
                          bm_eg.EMPLOYEES_ADD_COLS['employee_full_name']]

    # Setting the names of columns of last names in data
    lastname_cols_list = [bm_pg.COL_NAMES_ADD['last_name'],
                          bm_pg.COL_NAMES_PUB_NAMES['last name']]

    # Setting the names of columns of initials of first names in data
    short_firstname_cols_list = [bm_eg.EMPLOYEES_ADD_COLS['first_name_initials'],
                                 bm_pg.COL_NAMES_PUB_NAMES['initials']]

    # Building the useful lists of column names for the module functions
    reshape_cols_list = [pub_id_col, mat_col, short_firstname_cols_list[0]]
    add_ext_cols_list = ([pub_id_col, author_id_col] + fullname_cols_list
                         + lastname_cols_list + short_firstname_cols_list)
    add_job_cols_list = [author_type_col, mat_col] + job_cols_list
    add_ref_cols_list = [full_ref_col, pub_id_col] + pub_cols_list

    return_tup = (reshape_cols_list, add_ext_cols_list, add_job_cols_list, add_ref_cols_list)
    return return_tup


def _init_year_search(search_dfs, wf_path, print_params, add_ext_cols_list,
                      progress_params, test_params):
    """Initializes the merge-data and the orphan-data using the most-recent year 
    of the employee's data and the data of the external-collaborators.

    This done through the following steps:
    1. The merge-data and the orphan-data are created using the most-recent year \
    of the employee's data through the `build_pub_empl_data` function imported \
    from the `bmfuncts.build_pub_authors` module;
    2. New rows containing the information of authors that are PhD students \
    at the Institute but not as employees of it are added through the `_add_ext_docs` \
    internal function for updating the merge-data and the orphan-data;
    4. New rows containing the information of authors that are under external hiring \
    contract at the Institute are added through the `_add_other_ext` internal function \
    for updating the merge-data and the orphan-data.

    Args:
        search_dfs (list): Composed of the employees' data (dataframe) of the most recent year \
        and of the data (dataframe) of publications with one row per authors affiliated \
        to the Institute.
        wf_path (path): The full path to working folder.
        print_params (list): Composed of the 4 digits year of the corpus (str), of the parameters (list) \
        for the `print_step_text` function imported from the `bmfuncts.useful_functs` module, \
        of the Institute's name (str), of the org_tup (tup) that contains parameters of Institute's \
        organization, of the full path to working folder (path), of the data combination type \
        of corpuses databases (str), and of the dict giving the name of the parsing file for each parsed item.
        add_ext_cols_list (list): The useful columns' names parameters as built through \
        the `_set_merge_cols_lists` internal function.
        progress_params (list): Composed of the function for updating the status of the ProgressBar \
        tkinter widget and of the initial status (int) of ProgressBar tkinter widget and of \
        the increment unit (int) of the status of the ProgressBar tkinter widget.
        test_params (list): Composed of the test case (str) and of the author's lastname (str) \
        for testing the `build_pub_empl_data` function imported from the \
        `bmfuncts.build_year_pub_employees` module.
    Returns:
        (tup): Composed of the initialized merge-data and the orphan-data (dataframes) \
        and of the status (int if not None) of the ProgressBar tkinter widget.
    """
    # Setting the progress parameters for the update of the ProgressBar Tkinter widget
    progress_callback, inter_progress_bar_state, step = progress_params

    # Setting data for search from args
    empl_df, pub_df = search_dfs

    # Setting parameters values for test from 'test_params' arg
    set_test_case, set_test_name = test_params

    # Building the initial dataframes
    print_step_text(f"\n{bm_pg.TAB}- Initializing search of authors among employees data...", print_params)
    merge_df, orphan_df = build_pub_empl_data(empl_df, pub_df, wf_path, print_params,
                                              test_case=set_test_case, test_name=set_test_name,
                                              init_status=True)
    if progress_callback:
        progress_callback(inter_progress_bar_state + step * 20)

    # Setting path to the file of external employees
    ext_empl_path = _set_ext_files_paths(wf_path)

    # Adding authors from list of external_PhD students
    # to 'merge_df' data and updating 'orphan_df' data
    merge_df, orphan_df = _add_ext_docs(merge_df, orphan_df, ext_empl_path, add_ext_cols_list, print_params)
    if progress_callback:
        progress_callback(inter_progress_bar_state + step * 25)

    # Adding authors from list of external employees under other hiring contract
    # to 'merge_df' data  and updating 'orphan_df' data
    merge_df, orphan_df = _add_other_ext(merge_df, orphan_df, ext_empl_path, add_ext_cols_list, print_params)
    progress_bar_state = None
    if progress_callback:
        progress_bar_state = inter_progress_bar_state + step * 30
        progress_callback(progress_bar_state)
    return merge_df, orphan_df, progress_bar_state


def _previous_year_search(search_dfs, wf_path, print_params, progress_params,
                          test_params):
    """Updates the merge-data and the orphan-data using the employee's data of a year.

    This done through the following steps:
    1. The orphan-data are searched using the employee's data of the year to built the data \
    to be added to the merge-data and updated through the `build_pub_empl_data` function \
    imported from the `bmfuncts.build_year_pub_employees` module;
    2. The merge-data are updated by concatenation with the data built at the previous step 1.

    Args:
        search_dfs (list): Composed of the employees' data (dataframe) of a year \
        and of the previous merge-data (dataframe) and of the previous orphan-data (dataframe).
        wf_path (path): The full path to working folder.
        print_params (list): Composed of the 4 digits year of the corpus (str), of the parameters (list) \
        for the `print_step_text` function imported from the `bmfuncts.useful_functs` module, \
        of the Institute's name (str), of the org_tup (tup) that contains parameters of Institute's \
        organization, of the full path to working folder (path), of the data combination type \
        of corpuses databases (str), and of the dict giving the name of the parsing file for each parsed item.
        progress_params (list): Composed of the function for updating the status of the ProgressBar \
        tkinter widget and of the initial status (int) of ProgressBar tkinter widget and of \
        the increment unit (int) of the status of the ProgressBar tkinter widget.
        test_params (list): Composed of the test case (str) and of the author's lastname (str) \
        for testing the `build_pub_empl_data` function.
    Returns:
        (tup): Composed of the updated merge-data and the orphan-data (dataframes) \
        and of the status of the ProgressBar tkinter widget (int if not None).
    """
    # Setting the progress parameters for the update of the ProgressBar Tkinter widget
    progress_callback, progress_bar_state, progress_bar_loop_progression = progress_params

    # Setting data for search from args
    empl_df, merge_df, orphan_df = search_dfs

    # Setting parameters values for test from 'test_params' arg
    set_test_case, set_test_name = test_params

    # Updating the 'merge_df_add' and 'orphan_df' data
    merge_df_add, orphan_df = build_pub_empl_data(empl_df, orphan_df, wf_path, print_params,
                                                  test_case=set_test_case, test_name=set_test_name)

    # Updating the merged data
    merge_df = concat_dfs([merge_df, merge_df_add])

    # Updating progress bar state
    if progress_callback:
        progress_bar_state += progress_bar_loop_progression
        progress_callback(progress_bar_state)
    return merge_df, orphan_df, progress_bar_state


def _enhance_search_results(search_results, empl_dict, years, sub_params_list,
                            cols_info_list, progress_params):
    """Enhances the merge-data and orphan-data by adding complementary information.

    The enhancement is performed as follows:
    1. The merge-data and orphan-data are refactored by replacing NaN values by \
    the UNKNOWN global except for the firstnames' initials through the `keep_initials` \
    function imported from the `bmfuncts.useful_functs` module.
    2. The publications' IDs in the merge-data and orphan-data are modifyed through \
    the `set_year_pub_id` function imported from the `bmfuncts.useful_functs` module.
    3. A column containing the job type for each author is added to the merge-data \
    through the `_add_author_job_type` internal function.
    4. A column containing the full reference of each publication is added to the merge-data \
    merge-data through the `_add_biblio_list` internal function.
    5. Column names are changed in the merge-data and orphan-data through \
    the `_change_col_names` internal function.

    Args:
        search_results (list): Composed of the merge-data (dataframe) and of the orphan-data (dataframe) \
        resulting from the recursive search of authors among employees'data.
        empl_dict (dict): The employees' data as a dict keyed by the years \
        and valued by the employees data for each year.
        years (list): The years list for recursive search in the employees' database.
        sub_params_list (list): Composed of the 4 digits year of the corpus (str), of the parameters (list) \
        for the `print_step_text` function imported from the `bmfuncts.useful_functs` module, \
        of the Institute's name (str) and of the org_tup (tup) that contains parameters of Institute's \
        organization.
        cols_info_list (list): The useful columns' names parameters as built through \
        the `_set_merge_cols_lists` internal function.
        progress_params (list): Composed of the function for updating the status of the ProgressBar \
        tkinter widget and of the previous status (int) of ProgressBar tkinter widget and of \
        the increment unit (int) of the status of the ProgressBar tkinter widget.
    Returns:
        (list): Composed of the enhanced merge-data (dataframe) \
        and of the enhanced orphan-data (dataframe).
    """
    # Setting the progress parameters for the update of the ProgressBar Tkinter widget
    progress_callback, search_progress_bar_state, step = progress_params

    # Setting parameters' value from args
    corpus_year, print_params, institute, org_tup = sub_params_list
    initials_col, pub_id_col, add_job_cols_list, add_ref_cols_list = cols_info_list

    # Setting the results to enhance from args
    merge_df, orphan_df = search_results

    # Replace NaN values by UNKNOWN string except in first name initials
    merge_df = keep_initials(merge_df, initials_col, missing_fill=bm_pg.UNKNOWN)
    orphan_df = keep_initials(orphan_df, initials_col, missing_fill=bm_pg.UNKNOWN)
    print_step_text(f"{bm_pg.TAB*2}- Initials NA kept and not set to NaN", print_params)

    # Changing Pub_id columns to a unique Pub_id depending on the year
    merge_df = set_year_pub_id(merge_df, corpus_year, pub_id_col)
    if not orphan_df.empty:
        orphan_df = set_year_pub_id(orphan_df, corpus_year, pub_id_col)
    print_step_text(f"{bm_pg.TAB*2}- Publication IDs tagged with corpus year", print_params)

    # Adding author job type to 'merge_df' data
    merge_df = _add_author_job_type(merge_df, empl_dict, years, add_job_cols_list)
    print_step_text(f"{bm_pg.TAB*2}- Column with author job-type added", print_params)
    if progress_callback:
        progress_callback(search_progress_bar_state + step * 5)

    # Adding full publication reference to 'merge_df' data
    merge_df = _add_biblio_list(merge_df, add_ref_cols_list)
    print_step_text(f"{bm_pg.TAB*2}- Column with full publication reference added", print_params)
    if progress_callback:
        progress_callback(search_progress_bar_state + step * 10)

    # Renaming column names in merge_df' and 'orphan_df' data
    merge_df, orphan_df = _change_col_names(institute, org_tup, merge_df, orphan_df)
    print_step_text(f"{bm_pg.TAB*2}- Columns renamed with final names", print_params)

    enhanced_results = [merge_df, orphan_df]
    return enhanced_results


def _build_and_save_final_search_results(enhanced_results, sub_params_list, merge_paths,
                                         orphan_file, progress_params):
    """Builds the final merge-data and orphan-data before to be saved.

    The final data are built as follows:
    1. The orphan-data are split in subdivisions of Institute when indicated by the parameters \
    of the Institute's organization through the `_split_orphan` internal function;
    2. A column containing the unique ID of the publications is added to the merge-data and orphan-data \
    through the `create_hash_id` function imported from the `bmfuncts.create_hash_id` module;
    3. The final merge-data, the final orphan-data and the built Hash-IDs data are saved as XLSX files.

    Args:
        enhanced_results (list): Composed of the merge-data (dataframe) and of the orphan-data (dataframe) \
        enhanced through the `_enhance_search_results` internal function.
        sub_params_list (list): Composed of the parameters (list) for the `print_step_text` function \
        imported from the `bmfuncts.useful_functs` module, of the Institute's name (str) and of \
        the org_tup (tup) that contains parameters of Institute's organization.
        merge_paths (list): The full paths to (1) the folder where the built data are saved and \
        (2, 3 and 4) the files for saving the final merge-data, the final orphan-data \
        and the built Hash-IDs data.
        orphan_file (str): The file name used as base for saving the split results \
        of the orphan-data when this split is performed.
        progress_params (list): Composed of the function for updating the status of the ProgressBar \
        tkinter widget and of the previous status (int) of ProgressBar tkinter widget and of \
        the increment unit (int) of the status of the ProgressBar tkinter widget.
    Returns:
        (bool): The empty status of the final orphan-data.
    """
    # Setting the progress parameters for the update of the ProgressBar Tkinter widget
    progress_callback, search_progress_bar_state, step = progress_params

    # Setting parameters' value from args
    print_params, institute, org_tup = sub_params_list
    merge_folder_path, merge_path, orphan_path, hash_id_path = merge_paths

    # Setting the results to further enhance before to be saved
    merge_df, orphan_df = enhanced_results

    # Setting local parameters
    orphan_split_status = org_tup[9]

    # Splitting orphan data in subdivisions of Institute when indicated
    if orphan_split_status:
        split_orphan_df = orphan_df.copy()
        orphan_df = _split_orphan(org_tup, merge_folder_path, orphan_path, orphan_file, split_orphan_df)
        print_step_text(f"{bm_pg.TAB*2}- Not-found authors split in the specified subdivisions", print_params)
    if progress_callback:
        progress_callback(search_progress_bar_state + step * 15)

    # Creating universal identifiers of publications independent of data extraction
    final_return_tup = create_hash_id(institute, org_tup, merge_df, orphan_df)
    final_merge_df, final_orphan_df, hash_id_df, hash_id_nb = final_return_tup

    # Saving the data
    final_merge_df.to_excel(merge_path, index=False)
    final_orphan_df.to_excel(orphan_path, index=False)
    hash_id_df.to_excel(hash_id_path, index=False)

    # Updating orphan_status
    orphan_status = final_orphan_df.empty

    print_step_text(f"{bm_pg.TAB*2}- Number of publications' hash-IDs created and saved: {hash_id_nb}",
                    print_params)
    step_txt = f"\n{bm_pg.TAB}- Results of search of authors among employees data saved "
    if orphan_status:
        step_txt += "with all authors identified as employees or close collaborators."
    else:
        step_txt += "with remaining authors not identified as employees or close collaborators."
    print_step_text(step_txt, print_params)
    return orphan_status


def recursive_year_search(*, orphan_file, merge_paths, empl_dict, params_list, progress_params=None,
                          set_test_case="No test", set_test_name="No name"):
    """Searches in the employees' data the information for the authors affiliated to the Institute.

    The following short names are used for the description of this function and used internal functions:
    - pub-data = The data of publications with one row per authors affiliated to the Institute;
    - merge-data = The pub-data with authors found in the employees' data;
    - orphan-data = The pub-data with authors not found in the employees' data.

    The search is done through the following steps:
    1. The pub-data are built from the results of the corpus parsing through \
    the `build_institute_pubs_authors_data` function imported from \
    the `bmfuncts.build_pub_authors` module;
    2. The merge-data and orphan-data are initialized using the most-recent year \
    of the employees' data and the external-collaborators' data through \
    the `_init_year_search` internal function;
    3. The merge-data and orphan-data are updated using the employees' data of all available \
    previous years through the `_previous_year_search` internal function unless orphan-data \
    becomes empty earlier;
    4. The merge-data and orphan-data are added with useful information and reformatted \
    through the `_enhance_search_results` internal function;
    5. The merge-data and orphan-data are further enhance before to be saved through \
    the `_build_and_save_final_search_results` internal function.

    Args:
        orphan_file (str): The file name for saving the built data of the publications list \
        with one row per author that has not been identified as Institute employee.
        merge_paths (list): The full paths to (1) the folder where the built data are saved and \
        (2, 3 and 4) the files of the built data including the Hash-IDs data.
        empl_dict (dict): The employees' data as a dict keyed by the years \
        and valued by the employees data for each year.
        params_list (list): Composed of the 4 digits year of the corpus (str), of the parameters (list) \
        for the `print_step_text` function imported from the `bmfuncts.useful_functs` module, \
        of the Institute's name (str), of the org_tup (tup) that contains parameters of Institute's \
        organization, of the full path to working folder (path), of the data combination type \
        of corpuses databases (str), and of the dict giving the name of the parsing file for each parsed item.
        progress_params (list): Composed of the function for updating the status of the ProgressBar tkinter widget \
        and of the initial status of ProgressBar tkinter widget (optional, default: None).
        set_test_case (str): Optional test case (default: "No test") for testing the search process.
        set_test_name (str): Optional author's lastname (default: "No name") for testing the search process.
    Returns:
        (bool): The empty status of the publications list with authors not found in the employees' data.
    """
    # Setting parameters values from params_list
    corpus_year, print_params, institute, org_tup, wf_path = params_list[0:5]

    print_step_text("\nMerge publications authors and employees information...", print_params)

    # Setting useful params of merge files from args
    merge_folder_path, merge_path, orphan_path, hash_id_path = merge_paths

    # Setting useful parameters for setting col names
    cols_param_tup = _set_merge_cols_lists()
    (reshape_cols_list, add_ext_cols_list, add_job_cols_list, add_ref_cols_list) = cols_param_tup
    pub_id_col, mat_col, initials_col = reshape_cols_list

    # Setting parameters list for search test
    test_params = [set_test_case, set_test_name]

    # Initialize progress parameters
    (progress_callback, start_progress_bar_state, inter_progress_bar_state,
     inter_progress_params) = [None] * 4
    if progress_params:
        progress_callback, start_progress_bar_state = progress_params
        inter_progress_bar_state = 70

    # Building the publications' data with authors affiliated to the Institute
    start_progress_params = [progress_callback, start_progress_bar_state, inter_progress_bar_state]
    pub_df = build_institute_pubs_authors_data(params_list, start_progress_params)

    # Setting the years list for recursive search of author-employee match
    # The years are listed in descending order
    search_years = sorted(list(empl_dict.keys()), reverse=True)

    # Updating progress parameters
    progress_bar_loop_progression, step = [None] * 2
    if progress_callback:
        step = (100 - inter_progress_bar_state) / 100
        progress_bar_loop_progression = step * 50 // len(search_years)

    # Building the initial data through search using the most recent year of employees data
    print_step_text(f"\n{bm_pg.TAB}- Initializing search of authors among employees data...", print_params)
    init_progress_params = [progress_callback, inter_progress_bar_state, step]
    init_search_dfs = [empl_dict[search_years[0]], pub_df]
    init_return_tup = _init_year_search(init_search_dfs, wf_path, print_params, add_ext_cols_list,
                                        init_progress_params, test_params)
    merge_df, orphan_df, search_progress_bar_state = init_return_tup

    print_step_text(f"\n{bm_pg.TAB}- Recursive search of authors among employees data "
                    f"on {search_years[1]}...{search_years[-1]} period", print_params)
    txt_len = 0
    year_break = search_years[-1]
    for year in search_years[1:]:
        txt_len = print_temp_text(f"{bm_pg.TAB*2}Search year:{bm_pg.TAB}{year}", txt_end=True)
        next_progress_params = [progress_callback, search_progress_bar_state, progress_bar_loop_progression]
        year_search_dfs = [empl_dict[year], merge_df, orphan_df]
        next_return_tup = _previous_year_search(year_search_dfs, wf_path, print_params,
                                                next_progress_params, test_params)
        merge_df, orphan_df, search_progress_bar_state = next_return_tup
        if orphan_df.empty:
            year_break = year
            break
    end_search_progress_params = [progress_callback, search_progress_bar_state, step]
    print_step_text(f"{bm_pg.TAB*2}- Search down to {year_break} used to update publications' data of the Institute",
                    print_params, prev_txt_len=txt_len)

    print_step_text(f"\n{bm_pg.TAB}- Enhancing search results...", print_params)
    sub_params_list = [corpus_year, print_params, institute, org_tup]
    cols_info_list = [initials_col, pub_id_col, add_job_cols_list, add_ref_cols_list]
    search_results = [merge_df, orphan_df]
    enhanced_results = _enhance_search_results(search_results, empl_dict, search_years, sub_params_list,
                                                 cols_info_list, end_search_progress_params)

    print_step_text(f"\n{bm_pg.TAB}- Building and saving final search results...", print_params)
    sub_params_list = [print_params, institute, org_tup]
    orphan_status = _build_and_save_final_search_results(enhanced_results, sub_params_list, merge_paths,
                                                         orphan_file, end_search_progress_params)

    if progress_callback:
        progress_callback(100)
    return orphan_status
