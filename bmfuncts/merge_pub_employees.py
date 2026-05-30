"""Module of functions for the merge of employees information with the publications list 
of the Institute taking care of:

- Creation of list of Institute authors with selected attributes;
- Creation of full reference for each publication;
- Creation of publications hash-ID

"""

__all__ = ['recursive_year_search']


# Standard Library imports
import warnings
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.pub_globals as bm_pg
from bmfuncts.build_pub_authors import build_institute_pubs_authors
from bmfuncts.build_year_pub_empl import build_submit_df
from bmfuncts.create_hash_id import create_hash_id
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import keep_initials
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import set_year_pub_id
from bmfuncts.useful_functs import standardize_full_name_order
from bmfuncts.useful_functs import standardize_txt


def _add_author_job_type(submit_df, empl_dict, years, cols_list):
    """Adds a new column containing the job type for each author 
    of the publications list with one row per author.

    The job type is got from the employee information available 
    in 3 columns which names are given by 'category_col', 
    'status_col' and 'qualification_col'. 
    The name of the new column is given by 'author_type_col'. 

    Args:
        submit_df (dataframe): The data of the publications list \
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
    submit_df[author_type_col] = submit_df.apply(_get_author_type, axis=1)
    return submit_df


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
    full_ref  = f'{title}, '                     # add the reference's title
    full_ref += f'{first_author} et al., '       # add the reference's first author
    full_ref += f'{journal_name.capitalize()}, ' # add the reference's journal name
    full_ref += f'{pub_year}, '                  # add the reference's publication year
    full_ref += f'{doi}'                         # add the reference's DOI
    return full_ref


def _add_biblio_list(submit_df, cols_list):
    """Adds a new column containing the full reference of each publication 
    of the publications list with one row per author.

    The full reference is built by concatenating the following items:
    title, first author, year, journal, DOI. 
    These items are got from the columns which names are given by 
    'title_col', 'first_author_col', 'year_col', 
    'journal_col' and 'doi_col', respectively. 
    The name of the new column is given by 'full_ref_col'.

    Args:
        submit_df (dataframe): The data of the publications list \
        with one row per author with attributes as Institute employee.
        cols_list (list): The useful column names.
    Returns:
        (str): End message recalling the full path to the saved file \
        of the modified publications list.
    """
    # Setting col names from cols_list
    (full_ref_col, pub_id_col, first_author_col,
     year_col, journal_col, doi_col, title_col) = cols_list

    new_submit_df = pd.DataFrame()
    # Splitting the data into subdata with same Pub_id
    for _, pub_id_df in submit_df.groupby(pub_id_col):
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
        new_submit_df = concat_dfs([new_submit_df, pub_id_df])
    return new_submit_df


def _add_ext_docs(init_submit_df, init_orphan_df, ext_docs_path, cols_list, print_params):
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
        init_submit_df (dataframe): The data of the publications list \
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
    (pub_id_col, author_id_col, orphan_fullname_col, ext_empl_fullname_col,
     orphan_lastname_col, ext_auth_lastname_col,
     submit_firstname_short_col, ext_auth_firstname_short_cols) = cols_list

    # Replace in "init_submit_df" data and "init_orphan_df" data, NaN values
    # except "NA" in first name initials
    init_submit_df = keep_initials(init_submit_df, submit_firstname_short_col,
                                   missing_fill=bp.UNKNOWN)
    init_orphan_df = keep_initials(init_orphan_df, submit_firstname_short_col,
                                   missing_fill=bp.UNKNOWN)

    # Initializing the data to be concatenated with init_submit_df
    # with same column names as init_submit_df
    new_submit_adds_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Aligning column names between init_submit_df and init_orphan_df
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {submit_firstname_short_col : submit_firstname_short_col + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_firstname_short_col = col_rename_dic[submit_firstname_short_col]

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external PhD students xlsx file
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    ext_docs_usecols = sum([[ext_auth_lastname_col, ext_auth_firstname_short_cols],
                            bm_pg.EXT_DOCS_COL_ADDS_LIST,
                            bm_eg.EXT_DOCS_USEFUL_COL_LIST,],
                           [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    ext_docs_df = pd.read_excel(ext_docs_path,
                                sheet_name=bm_pg.SHEET_NAMES_ORPHAN["docs to add"],
                                usecols=ext_docs_usecols,
                                converters=bm_eg.EMPLOYEES_CONVERTERS_DIC)

    # Replace in "ext_docs_df" NaN values "NA" in first name initials
    ext_docs_df = keep_initials(ext_docs_df, ext_auth_firstname_short_cols)
    ext_docs_df = ext_docs_df.dropna(how='any')

    # Searching for last names of init_orphan_df in ext_docs_df
    # to update 'submit_df' and 'orphan_df' data using 'new_submit_adds_df' and 'orphan_drop_df' data
    for _, init_orphan_row in init_orphan_df.iterrows():
        author_last_name = str(init_orphan_row[orphan_lastname_col])
        author_last_name = standardize_txt(author_last_name)
        author_initials = str(init_orphan_row[orphan_firstname_short_col])
        for _, ext_docs_row in ext_docs_df.iterrows():
            ext_docs_pub_last_name = str(ext_docs_row[ext_auth_lastname_col])
            ext_docs_pub_last_name = standardize_txt(ext_docs_pub_last_name)
            ext_docs_pub_initials = str(ext_docs_row[ext_auth_firstname_short_cols])
            if (ext_docs_pub_last_name==author_last_name
                    and ext_docs_pub_initials==author_initials):
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = init_orphan_row.to_frame().T

                # Setting the row to copy from ext_docs_df as a dataframe
                row_to_copy_df = ext_docs_row.to_frame().T

                # Dropping the columns of 'row_to_copy_df' data that should not be present in 'row_to_add_df' data
                row_to_copy_df = row_to_copy_df.drop([ext_auth_lastname_col, ext_auth_firstname_short_cols],
                                                     axis=1)

                # Merging the two dataframes on respective full name column
                row_to_add_df = pd.merge(row_to_move_df, row_to_copy_df,
                                         left_on=[orphan_fullname_col],
                                         right_on=[ext_empl_fullname_col],
                                         how='left')

                # Appending the merged df to 'new_submit_adds_df' data
                new_submit_adds_df = concat_dfs([new_submit_adds_df, row_to_add_df],
                                                concat_ignore_index=True)

                # Appending row_to_move_df to 'orphan_drop_df' data
                orphan_drop_df = concat_dfs([orphan_drop_df, row_to_move_df],
                                            concat_ignore_index=True)

    # Concatenating init_submit_df and new_submit_adds_df
    new_submit_df = concat_dfs([init_submit_df, new_submit_adds_df])
    new_submit_df = new_submit_df.sort_values([pub_id_col, author_id_col])

    # Dropping orphan_drop_df rows from init_orphan_df
    new_orphan_df = concat_dfs([init_orphan_df, orphan_drop_df], keep='False')

    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {submit_firstname_short_col + "_x":\
                             submit_firstname_short_col}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    print_step_text("      - External PhD students added", print_params)
    return new_submit_df, new_orphan_df


def _add_other_ext(init_submit_df, init_orphan_df, others_path, cols_list, print_params):
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
        init_submit_df (dataframe): The data of the publications list \
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
    (pub_id_col, author_id_col, orphan_fullname_col, ext_empl_fullname_col,
     orphan_lastname_col, ext_auth_lastname_col,
     submit_firstname_short_col, ext_auth_firstname_short_cols) = cols_list

    # Replace in "init_submit_df" data and "init_orphan_df" data, NaN values
    # except "NA" in first name initials
    init_submit_df = keep_initials(init_submit_df, submit_firstname_short_col,
                                   missing_fill=bp.UNKNOWN)
    init_orphan_df = keep_initials(init_orphan_df, submit_firstname_short_col,
                                   missing_fill=bp.UNKNOWN)

    # Initializing the data to be concatenated to 'init_submit_df' data in 'new_submit_df' data
    # with same column names as init_submit_df
    new_submit_adds_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Aligning column names between init_submit_df and init_orphan_df
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {submit_firstname_short_col : submit_firstname_short_col + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_firstname_short_col = col_rename_dic[submit_firstname_short_col]

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external PhD students xlsx file
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    others_usecols = sum([[ext_auth_lastname_col, ext_auth_firstname_short_cols],
                          bm_pg.EXT_DOCS_COL_ADDS_LIST,
                          bm_eg.EXT_DOCS_USEFUL_COL_LIST,],
                         [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    others_df = pd.read_excel(others_path,
                              sheet_name=bm_pg.SHEET_NAMES_ORPHAN["others to add"],
                              usecols=others_usecols,
                              converters=bm_eg.EMPLOYEES_CONVERTERS_DIC)

    # Replace in "other_df" NaN values "NA" in first name initials
    others_df = keep_initials(others_df, ext_auth_firstname_short_cols)
    others_df = others_df.dropna(how='any')

    # Searching for last names of init_orphan_df in others_df
    # to update 'submit_df' and 'orphan_df' data using 'new_submit_adds_df' and 'orphan_drop_df' data
    for _, orphan_row in init_orphan_df.iterrows():
        author_last_name = str(orphan_row[orphan_lastname_col])
        author_last_name = standardize_txt(author_last_name)
        author_initials = str(orphan_row[orphan_firstname_short_col])
        for _, others_row in others_df.iterrows():
            others_pub_last_name = str(others_row[ext_auth_lastname_col])
            others_pub_last_name = standardize_txt(others_pub_last_name)
            others_pub_initials = str(others_row[ext_auth_firstname_short_cols])
            if others_pub_last_name==author_last_name and others_pub_initials==author_initials:
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = orphan_row.to_frame().T

                # Setting the row to copy from others_df as a dataframe
                row_to_copy_df = others_row.to_frame().T

                # Dropping the columns of 'row_to_copy_df' data that should not be present in 'row_to_add_df' data
                row_to_copy_df = row_to_copy_df.drop([ext_auth_lastname_col, ext_auth_firstname_short_cols],
                                                     axis=1)

                # Merging the two dataframes on respective full name column
                row_to_add_df = pd.merge(row_to_move_df, row_to_copy_df,
                                         left_on=[orphan_fullname_col],
                                         right_on=[ext_empl_fullname_col],
                                         how='left')

                # Appending the merged df to 'new_submit_adds_df' data
                new_submit_adds_df = concat_dfs([new_submit_adds_df, row_to_add_df],
                                                concat_ignore_index=True)

                # Appending row_to_move_df to  'orphan_drop_df' data
                orphan_drop_df = concat_dfs([orphan_drop_df, row_to_move_df],
                                            concat_ignore_index=True)

    # Concatenating 'init_submit_df' data and 'new_submit_adds_df' data
    new_submit_df = concat_dfs([init_submit_df, new_submit_adds_df])
    new_submit_df = new_submit_df.sort_values([pub_id_col, author_id_col])

    # Dropping 'orphan_drop_df' data from 'init_orphan_df' data
    new_orphan_df = concat_dfs([init_orphan_df, orphan_drop_df], keep='False')

    # Recovering the initial column names of 'init_orphan_df' data
    col_invert_rename_dic = {submit_firstname_short_col + "_x":\
                             submit_firstname_short_col}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    print_step_text("      - Other external collaborators added", print_params)
    return new_submit_df, new_orphan_df


def _change_col_names(institute, org_tup, submit_df, orphan_df):
    """Sets new column names to the files pointed by 'submit_path' 
    and 'orphan_path' paths.

    For that it uses the `build_col_conversion_dic` function 
    imported from `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        submit_df (dataframe): The data of the publications list \
        with one row per author with attributes as Institute employee.
        orphan_df (dataframe): The data of the publications list \
        with one row per author that has not been identified as Institute employee.
    Returns:
        (str): End message recalling the full paths to the modified files.
    """
    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    orphan_col_rename_dic = col_rename_tup[0]
    submit_col_rename_dic = col_rename_tup[1]

    # Renaming columns
    submit_df = submit_df.rename(columns=submit_col_rename_dic)
    orphan_df = orphan_df.rename(columns=orphan_col_rename_dic)
    return submit_df, orphan_df


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
        (bool): The empty status of the publications list with authors \
        not found in the employees' database.
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
            message = f"    File of orphan authors created for Institute subdivision: {_inst_col}"
            print(message)

    # Setting useful column names list and dropping status
    inst_col_list = org_tup[4]
    orphan_drop_dict = org_tup[10]

    # Creating, and saving as an 'xlsx' file, orphan authors for each Institute subdivision
    institute_df = orphan_df.copy()
    new_orphan_df = orphan_df.copy()
    droped_indexes = set()
    for inst_col in inst_col_list[1:]:
        inst_col_df = orphan_df[orphan_df[inst_col]==1]
        _save_inst_col_df(inst_col, inst_col_df)
        indexes_to_drop = list(set(inst_col_df.index) - droped_indexes)
        institute_df = institute_df.drop(indexes_to_drop)
        droped_indexes = set(inst_col_df.index)
        if orphan_drop_dict[inst_col]:
            new_orphan_df = new_orphan_df.drop(inst_col_df.index)
    _save_inst_col_df(inst_col_list[0], institute_df)
    _save_inst_col_df("all_undrop", new_orphan_df)

    # Updating orphan status
    orphan_status = new_orphan_df.empty
    return orphan_status


def _adapt_depth_search(empl_dict, corpus_year, search_depth):
    """Sets the list of years for recursive search of author-employee match.

    Args:
        empl_dict (dict): The employees database as a dict keyed by the years \
        and valued by the employees data for each year.
        corpus_year (str): Contains the corpus year defined by 4 digits.
        search_depth (int): Depth for search in 'empl_dict'.
    """
    eff_available_years = list(empl_dict.keys())
    corpus_year_status = corpus_year in eff_available_years
    year_start = int(corpus_year)
    if not corpus_year_status:
        year_start = int(corpus_year)-1
    year_stop = year_start - (search_depth - 1)
    years = [str(i) for i in range(year_start, year_stop-1,-1)]
    return years


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
    author_type_col, full_ref_col = (bm_pg.COL_NAMES_BONUS['author_type'],
                                     bm_pg.COL_NAMES_BONUS['liste biblio'])

    # Setting the names of IDs columns
    pub_id_col, author_id_col, mat_col = (bp.COL_NAMES['pub_id'],
                                          bp.COL_NAMES['authors'][1],
                                          bm_eg.EMPLOYEES_USEFUL_COLS['matricule'])

    # Setting the names of columns of publications info
    pub_cols_list = [bp.COL_NAMES['articles'][1],
                     bp.COL_NAMES['articles'][2],
                     bp.COL_NAMES['articles'][3],
                     bp.COL_NAMES['articles'][6],
                     bp.COL_NAMES['articles'][9]]

    # Setting the names of columns of job types in employees data
    job_cols_list = [bm_eg.EMPLOYEES_USEFUL_COLS['category'],
                     bm_eg.EMPLOYEES_USEFUL_COLS['status'],
                     bm_eg.EMPLOYEES_USEFUL_COLS['qualification']]

    # Setting the names of columns of full names in data
    fullname_cols_list = [bm_pg.COL_NAMES_BM['Full_name'],
                          bm_eg.EMPLOYEES_ADD_COLS['employee_full_name']]

    # Setting the names of columns of last names in data
    lastname_cols_list = [bm_pg.COL_NAMES_BM['Last_name'],
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


def _config_empl(empl_dict, years, initials_col, mat_col):
    """Replace in "empl_dict" NaN values by UNKNOWN string except 
    in first name initials and set the values type in the "mat_col" 
    col as string.

    Care is taken to keep 'NA' value for the first name initiales 
    through the `keep_initials` function imported from the 
    "bmfuncts.useful_functs" internal module. This is done to avoid 
    this value to be set to NaN by default.

    Args:
        empl_dict (dict): The employees dict keyed by year 
        and valued by employees data (dataframe).
        years (list): The keys (str) at which the employees dict 
        will to be modified.
        initials_col (str): The col name of the firstnames initials.
        mat_col (str): The col name of the employees ID (matriculate).
    Returns:
        (dict): The modified dict.
    """
    new_empl_dict = {}
    for year in years:
        new_empl_dict[year] = keep_initials(empl_dict[year], initials_col,
                                            missing_fill=bp.UNKNOWN)
        new_empl_dict[year] = new_empl_dict[year].astype({mat_col: 'str'})
    return new_empl_dict


def recursive_year_search(*, orphan_file, merge_paths, empl_dict, params_list, search_depth,
                          progress_callback=None, progress_bar_state=None,
                          set_test_case="No test", set_test_name="No name"):
    """Searches in the employees database of the Institute the information for the authors 
    of the publications of a corpus.

    This is done through the following steps:

    1. The publications list dataframe with one row per Institute author for each \
    publication is built from the results of the corpus parsing through \
    the `build_institute_pubs_authors` function imported from \
    the `bmfuncts.build_pub_authors` module.
    2. The 'submit_df' dataframe of the publications list containing all matches \
    between Institute authors and employee names is initialized using the most recent year \
    of the employees database through the `build_submit_df` function imported from \
    `bmfuncts.build_year_pub_empl` module; this is done together with the initialization \
    of 'orphan_df' dataframe of the publications list with authors not found in the \
    employees database; these two dataframes contains one row per author of each publication.
    3. New rows containing the information of authors that are PhD students \
    at the Institute but not as employees of it are added through the `_add_ext_docs` \
    internal function updating 'submit_df' and 'orphan_df' dataframes.
    4. New rows containing the information of authors that are under external hiring \
    contract at the Institute are added through the `_add_other_ext` internal function \
    updating 'submit_df' and 'orphan_df' dataframes.
    5. The 'submit_df' and 'orphan_df' dataframes are updated by search in the employees \
    database through the `build_submit_df` function using recursively items from \
    'years' list for the search year.
    6. The dataframes are refactored by replacing NaN values by the UNKNOWN global and \
    modifying the publications IDs through the `set_year_pub_id` function imported from \
    the `bmfuncts.useful_functs`module. Then they are saved as xlsx files which full \
    paths are given by 'submit_path' and 'orphan_path', respectively.
    7. A new column containing the job type for each author is added in the file which \
    full path is given by 'submit_path' through the `_add_author_job_type` internal function.
    8. A new column containing the full reference of each publication is added \
    in the file which full path is given by 'submit_path' through the `_add_biblio_list` \
    internal function.
    9. Column names are changed in the two files which full path are given by respectively, \
    'submit_path' and 'orphan_path' through the `_change_col_names` internal function.
    10. An 'xlsx' file containing the unique hash ID built for each publication \
    is created through the `create_hash_id` function imported from "bmfuncts.create_hash_id" \
    module.

    Args:
        orphan_file (str): The file name for saving the built data of the publications list \
        with one row per author that has not been identified as Institute employee.
        merge_paths (list): The full paths to (1) the folder where the built data are saved and \
        (2, 3 and 4) the files of the built data including the Hash-IDs data.
        empl_dict (dict): The employees database as a dict keyed by the years \
        and valued by the employees data for each year.
        params_list (list):  The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path), the data combination type \
        of corpuses databases (str), the pParameters (list) for the `print_step_text` function \
        imported from the `bmfuncts.useful_functs` module and the 4 digits year of the corpus (str).
        search_depth (int): Depth for search in 'empl_dict' using 'years' list.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (optional, default = None).
        progress_bar_state (int): Initial status of ProgressBar tkinter widget \
        (optional, default = None).
        set_test_case (str): Test case for testing the `build_submit_df` function \
        (optional, default = "No test").
        set_test_name (str): Author last-name for testing the `build_submit_df` function \
        (optional, default = "No name").
    Returns:
        (tup): (end_message (str), empty status (bool) of the publications \
        list with authors not found in the employees database).
    Note:
        Care is taken to keep 'NA' value for the first name initials \
        that are set to NaN by default through the `keep_initials` function \
        imported from "bmfuncts.useful_functs" internal module.
    """
    # Setting parameters values from params_list
    corpus_year, print_params, institute, org_tup, wf_path = params_list[0:5]

    print_step_text("\nMerge publications authors and employees information...",
                        print_params)

    # Setting useful params of merge files from args
    merge_folder_path, submit_path, orphan_path = merge_paths[:3]

    # Setting path to the file of external employees
    ext_empl_path = _set_ext_files_paths(wf_path)

    # Setting useful parameters for setting col names
    cols_param_tup = _set_merge_cols_lists()
    (reshape_cols_list, add_ext_cols_list,
     add_job_cols_list, add_ref_cols_list) = cols_param_tup
    pub_id_col, mat_col, initials_col = reshape_cols_list

    # Setting local parameters
    orphan_split_status = org_tup[9]

    # Building the articles dataframe
    pub_df = build_institute_pubs_authors(params_list)

    # Replace in "pub_df" NaN values by UNKNOWN string except in first name initials
    pub_df = keep_initials(pub_df, initials_col, missing_fill=bp.UNKNOWN)

    # Setting the years list for recursive search of author-employee match
    years = _adapt_depth_search(empl_dict, corpus_year, search_depth)

    # Replace in "empl_dict" NaN values by UNKNOWN string except in first name initials
    # and set type of employees IDs to string
    empl_dict = _config_empl(empl_dict, years, initials_col, mat_col)
    step, new_progress_bar_state, progress_bar_loop_progression = [None] * 3
    if progress_callback:
        step = (100 - progress_bar_state) / 100
        progress_callback(progress_bar_state + step * 10)

    # **************************************************************
    # * Building recursively the `submit_df` and `orphan_df` data *
    # *                 using `empl_dict` files of years          *
    # **************************************************************

    # Building the initial dataframes
    print_step_text("\n  - Initializing search of authors among employees data...",
                        print_params)
    submit_df, orphan_df = build_submit_df(empl_dict[years[0]], pub_df, wf_path, print_params,
                                           test_case=set_test_case, test_name=set_test_name, init_status=True)
    if progress_callback:
        progress_callback(progress_bar_state + step * 20)

    # Adding authors from list of external_phd students
    # to 'submit_df' data and updating 'orphan_df' data
    submit_df, orphan_df = _add_ext_docs(submit_df, orphan_df, ext_empl_path, add_ext_cols_list, print_params)
    if progress_callback:
        progress_callback(progress_bar_state + step * 25)

    # Adding authors from list of external employees under other hiring contract
    # to 'submit_df' data  and updating 'orphan_df' data
    submit_df, orphan_df = _add_other_ext(submit_df, orphan_df, ext_empl_path, add_ext_cols_list, print_params)
    if progress_callback:
        new_progress_bar_state = progress_bar_state + step * 30
        progress_callback(new_progress_bar_state)
        progress_bar_loop_progression = step * 50 // len(years)

    print_step_text("\n  - Recursive search of authors among employees data...", print_params)
    print(f"        Search period: {years[0]}...{years[-1]}")
    for _, year in enumerate(years):
        print(f"        Search year:   {year}", end="\r")
        # Updating the 'submit_df_add' and 'orphan_df' data
        submit_df_add, orphan_df = build_submit_df(empl_dict[year], orphan_df, wf_path, print_params,
                                                   test_case=set_test_case, test_name=set_test_name)

        # Updating the 'submit_df' data
        submit_df = concat_dfs([submit_df, submit_df_add])

        # Updating progress bar state
        if progress_callback:
            new_progress_bar_state += progress_bar_loop_progression
            progress_callback(new_progress_bar_state)
    print_step_text("      - Search period results used to update data", print_params)

    print_step_text("\n  - Enhancing search results...", print_params)
    # Replace NaN values by UNKNOWN string except in first name initials
    submit_df = keep_initials(submit_df, initials_col, missing_fill=bp.UNKNOWN)
    orphan_df = keep_initials(orphan_df, initials_col, missing_fill=bp.UNKNOWN)
    orphan_status = orphan_df.empty

    # Changing Pub_id columns to a unique Pub_id depending on the year
    submit_df = set_year_pub_id(submit_df, corpus_year, pub_id_col)
    print_step_text("      - Publication IDs tagged with corpus year", print_params)
    if not orphan_status:
        orphan_df = set_year_pub_id(orphan_df, corpus_year, pub_id_col)

    # Adding author job type to 'submit_df' data
    submit_df = _add_author_job_type(submit_df, empl_dict, years, add_job_cols_list)
    print_step_text("      - Column with author job-type added", print_params)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 5)

    # Adding full publication reference to 'submit_df' data
    submit_df = _add_biblio_list(submit_df, add_ref_cols_list)
    print_step_text("      - Column with full publication reference added", print_params)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 10)

    # Renaming column names in submit_df' and 'orphan_df' data
    submit_df, orphan_df = _change_col_names(institute, org_tup, submit_df, orphan_df)
    print_step_text("      - Columns renamed with final names", print_params)

    # Saving submit_df' and 'orphan_df' data
    submit_df.to_excel(submit_path, index=False)
    orphan_df.to_excel(orphan_path, index=False)

    # Splitting orphan file in subdivisions of Institute when indicated
    if orphan_split_status:
        orphan_status = _split_orphan(org_tup, merge_folder_path, orphan_path, orphan_file, orphan_df)
        print_step_text("      - Not found authors split in the specified subdivisions", print_params)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 15)

    # Creating universal identifiers of publications independent of data extraction
    create_hash_id(institute, org_tup, merge_paths[1:], print_params)
    if progress_callback:
        progress_callback(100)
    step_txt = "\nResults of search of authors in employees list saved"
    if orphan_status:
        step_txt += " with all authors identified as employees."
    else:
        step_txt += " with remaining authors not identified as employees."
    print_step_text(step_txt, print_params)
    return orphan_status
