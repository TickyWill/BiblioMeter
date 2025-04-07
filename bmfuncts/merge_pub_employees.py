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
import pandas as pd
import BiblioParsing as bp

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg
from bmfuncts.build_pub_authors import build_institute_pubs_authors
from bmfuncts.build_year_pub_empl import build_submit_df
from bmfuncts.create_hash_id import create_hash_id
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import keep_initials
from bmfuncts.useful_functs import set_year_pub_id
from bmfuncts.useful_functs import standardize_txt


def _add_author_job_type(in_path, out_path, empl_dict, years):
    """Adds a new column containing the job type for each author 
    of the publications list with one row per author.

    The job type is got from the employee information available 
    in 3 columns which names are given by 'category_col_alias', 
    'status_col_alias' and 'qualification_col_alias'. 
    The name of the new column is given by 'author_type_col_alias'. 
    The updated publications list is saved as xlsx file.

    Args:
        in_path (path):  Full path to the file of the publications list \
        with one row per author with attributes as Institute employee.
        out_path (path): Full path for saving the modified publications list.
        empl_dict (dict): The employees database as a dict keyed by the years \
        and valued by the employees data for each year.
        years (list): The years list for recursive search in the employees database.
    Returns:
        (str): End message recalling the full path to the saved file of \
        the modified publications list.
    """
    # internal functions:
    def _get_author_type(row):
        mat = row[mat_col_alias]
        if mat!="externe":
            author_type = '-'
            years_nb = len(years)
            year_idx = 0
            set_author_type = "FIN"
            while set_author_type=="FIN" and year_idx<years_nb:
                year_empl_df = empl_dict[years[year_idx]]
                year_mat_df = year_empl_df[year_empl_df[mat_col_alias]==str(mat)]
                for col_name, dic in author_types_dic.items():
                    mat_value = ""
                    if not year_mat_df[col_name].empty:
                        mat_value = list(year_mat_df[col_name])[0]
                    for key, values_list in dic.items():
                        values_status = [True for value in values_list if value in mat_value]
                        if any(values_status):
                            set_author_type = key
                year_idx += 1
            author_type = set_author_type
        else:
            author_type = 'Coll'
            for col_name, dic in author_types_dic.items():
                mat_value = row[col_name]
                for key, values_list in dic.items():
                    values_status = [True for value in values_list if value in mat_value]
                    if any(values_status):
                        author_type = key
                        break
                if author_type!='Coll':
                    break
        return author_type

    # Setting useful aliases
    mat_col_alias = eg.EMPLOYEES_USEFUL_COLS['matricule']
    category_col_alias = eg.EMPLOYEES_USEFUL_COLS['category']
    status_col_alias = eg.EMPLOYEES_USEFUL_COLS['status']
    qualification_col_alias = eg.EMPLOYEES_USEFUL_COLS['qualification']
    author_type_col_alias = pg.COL_NAMES_BONUS['author_type']

    author_types_dic = {category_col_alias      : eg.CATEGORIES_DIC,
                        status_col_alias        : eg.STATUS_DIC,
                        qualification_col_alias : eg.QUALIFICATION_DIC}

    # Read of the xlsx file with dates conversion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(in_path, converters=eg.EMPLOYEES_CONVERTERS_DIC)

    submit_df[author_type_col_alias] = submit_df.apply(_get_author_type, axis=1)

    submit_df.to_excel(out_path, index=False)

    end_message = f"Column with author job type added in file: \n  '{out_path}'"
    return end_message


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
    full_ref += f'{first_author}. et al., '      # add the reference's first author
    full_ref += f'{journal_name.capitalize()}, ' # add the reference's journal name
    full_ref += f'{pub_year}, '                  # add the reference's publication year
    full_ref += f'{doi}'                         # add the reference's DOI
    return full_ref


def _add_biblio_list(in_path, out_path):
    """Adds a new column containing the full reference of each publication 
    of the publications list with one row per author.

    The full reference is built by concatenating the folowing items: 
    title, first author, year, journal, DOI. 
    These items are got from the columns which names are given by 
    'pub_title_alias', 'pub_first_author_alias', 'pub_year_alias', 
    'pub_journal_alias' and 'pub_doi_alias', respectively. 
    The name of the new column is given by 'pub_full_ref_alias'. 
    The updated publications list is saved as an xlsx file.

    Args:
        in_path (path): Full path to the xlsx file of the publications list.
        out_path (path): Full path for saving the modified publications list.
    Returns:
        (str): End message recalling the full path to the saved file \
        of the modified publications list.
    """

    # Setting useful aliases
    pub_id_alias = bp.COL_NAMES['pub_id']
    pub_first_author_alias = bp.COL_NAMES['articles'][1]
    pub_year_alias = bp.COL_NAMES['articles'][2]
    pub_journal_alias = bp.COL_NAMES['articles'][3]
    pub_doi_alias = bp.COL_NAMES['articles'][6]
    pub_title_alias = bp.COL_NAMES['articles'][9]
    pub_full_ref_alias = pg.COL_NAMES_BONUS['liste biblio']

    # Read of the xlsx file with dates convertion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(in_path, converters=eg.EMPLOYEES_CONVERTERS_DIC)

    articles_plus_full_ref_df = pd.DataFrame()
    # Splitting the frame into subframes with same Pub_id
    for _, pub_id_df in submit_df.groupby(pub_id_alias):
        # Select the first row and build the full reference
        pub_id_first_row = pub_id_df.iloc[0]
        title = str(pub_id_first_row[pub_title_alias])
        first_author = str(pub_id_first_row[pub_first_author_alias])
        journal_name = str(pub_id_first_row[pub_journal_alias])
        pub_year = str(pub_id_first_row[pub_year_alias])
        doi = str(pub_id_first_row[pub_doi_alias])
        pub_id_df[pub_full_ref_alias] = _set_full_ref(title, first_author,
                                                      journal_name, pub_year, doi)
        articles_plus_full_ref_df = concat_dfs([articles_plus_full_ref_df, pub_id_df])
    articles_plus_full_ref_df.to_excel(out_path, index=False)

    end_message = f"Column with full reference of publication added in file: \n  '{out_path}'"
    return end_message


def _add_ext_docs(submit_path, orphan_path, ext_docs_path):
    """Adds to the publications-list dataframe with one row per author 
    new rows containing the information of specific authors.

    The specific authors are PhD students at the Institute but not as employees of it. 
    The list of these PhD students with the required information is got from 
    the xlsx file which full path is given by 'ext_docs_path' in sheet which 
    name is given by 'ext_docs_sheet_name_alias'. 
    The row of the added PhD students is dropped in the publications list 
    with one row per author that has not been identified as Institute employee. 
    The new publications lists are saved as an xlsx files.

    Args:
        submit_path (path): Full path to the xlsx file of the publications list \
        with one row per author with attributes as Institute employee.
        orphan_path (path): Full path to the xlsx file of the publications list \
        with one row per author that has not been identified as Institute employee.
        ext_docs_path (path): Full path to the xlsx file giving the PhD students \
        at the Institute but not employees of it.
    Returns:
        (tup): (updated dataframe of the publications list with one row \
        per Institute author including external PhD students, updated dataframe \
        of publications list with one row per author that has not been identified \
        as Institute employee).
    Note:
        Care is taken to keep 'NA' value for the first name initiales \
        that are set to NaN by default through the `keep_initials` function \
        imported from "bmfuncts.useful_functs" internal module.
    """

    # Setting aliases for useful column names
    pub_id_alias = bp.COL_NAMES['authors'][0]
    author_id_alias = bp.COL_NAMES['authors'][1]
    converters_alias = eg.EMPLOYEES_CONVERTERS_DIC
    firstname_initials_col_base_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    ext_docs_full_name_alias = eg.EMPLOYEES_ADD_COLS['employee_full_name']
    ext_docs_useful_col_list_alias = eg.EXT_DOCS_USEFUL_COL_LIST
    ext_docs_pub_last_name_alias = pg.COL_NAMES_PUB_NAMES['last name']
    ext_docs_pub_initials_alias = pg.COL_NAMES_PUB_NAMES['initials']
    ext_docs_sheet_name_alias = pg.SHEET_NAMES_ORPHAN["docs to add"]
    ext_docs_col_adds_list_alias = pg.EXT_DOCS_COL_ADDS_LIST
    orphan_full_name_alias = pg.COL_NAMES_BM['Full_name']
    orphan_last_name_alias = pg.COL_NAMES_BM['Last_name']

    # Reading of the existing submit xlsx file of the corpus year
    # with dates conversion through converters_alias
    init_submit_df = pd.read_excel(submit_path, converters=converters_alias)
    init_orphan_df = pd.read_excel(orphan_path, converters=converters_alias)

    # Replace in "init_submit_df" and "init_orphan_df" NaN values "NA" in first name initials
    init_submit_df = keep_initials(init_submit_df, firstname_initials_col_base_alias,
                                   missing_fill=bp.UNKNOWN)
    init_orphan_df = keep_initials(init_orphan_df, firstname_initials_col_base_alias,
                                   missing_fill=bp.UNKNOWN)

    # Initializing the dataframe to be concatenated with init_submit_df
    # with same column names as init_submit_df
    new_submit_adds_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Aligning column names between init_submit_df and init_orphan_df
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {firstname_initials_col_base_alias : firstname_initials_col_base_alias + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_initials_alias = col_rename_dic[firstname_initials_col_base_alias]

    # Initializing new_orphan_df as copy of init_orphan_df
    #new_orphan_df = init_orphan_df.copy()
    new_orphan_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external phd students xlsx file
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    ext_docs_usecols = sum([[ext_docs_pub_last_name_alias, ext_docs_pub_initials_alias],
                            ext_docs_col_adds_list_alias,
                            ext_docs_useful_col_list_alias,],
                           [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    ext_docs_df = pd.read_excel(ext_docs_path,
                                sheet_name=ext_docs_sheet_name_alias,
                                usecols=ext_docs_usecols,
                                converters=converters_alias)

    # Replace in "ext_docs_df" NaN values "NA" in first name initials
    ext_docs_df = keep_initials(ext_docs_df, ext_docs_pub_initials_alias)
    ext_docs_df = ext_docs_df.dropna(how='any')

    # Searching for last names of init_orphan_df in ext_docs_df
    # to update submit and orphan files using new_submit_adds_df and new_orphan_drop_df
    for orphan_row_num, _ in init_orphan_df.iterrows():
        author_last_name = init_orphan_df.loc[orphan_row_num, orphan_last_name_alias]
        author_last_name = standardize_txt(author_last_name)
        author_initials = init_orphan_df.loc[orphan_row_num, orphan_initials_alias]
        for ext_docs_row_num, _ in ext_docs_df.iterrows():
            ext_docs_pub_last_name = ext_docs_df.loc[ext_docs_row_num, ext_docs_pub_last_name_alias]
            ext_docs_pub_last_name = standardize_txt(ext_docs_pub_last_name)
            ext_docs_pub_initials = ext_docs_df.loc[ext_docs_row_num, ext_docs_pub_initials_alias]
            if (ext_docs_pub_last_name==author_last_name
                    and ext_docs_pub_initials==author_initials):
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = init_orphan_df.loc[orphan_row_num].to_frame().T

                # Setting the row to copy from ext_docs_df as a dataframe
                row_to_copy_df = ext_docs_df.loc[ext_docs_row_num].to_frame().T

                # Dropping the columns of row_to_copy_df that should not be present in row_to_add_df
                row_to_copy_df = row_to_copy_df.drop([ext_docs_pub_last_name_alias,
                                                      ext_docs_pub_initials_alias],
                                                     axis = 1)

                # Merging the two dataframes on respective full name column
                row_to_add_df = pd.merge(row_to_move_df,
                                         row_to_copy_df,
                                         left_on=[orphan_full_name_alias],
                                         right_on=[ext_docs_full_name_alias],
                                         how='left')

                # Appending the merged df to new_submit_adds_df
                new_submit_adds_df = concat_dfs([new_submit_adds_df, row_to_add_df],
                                                concat_ignore_index=True)

                # Appending row_to_move_df to  orphan_drop_df
                orphan_drop_df = concat_dfs([orphan_drop_df, row_to_move_df],
                                            concat_ignore_index=True)

    # Concatenating init_submit_df and new_submit_adds_df
    new_submit_df = concat_dfs([init_submit_df, new_submit_adds_df])
    new_submit_df = new_submit_df.sort_values([pub_id_alias, author_id_alias])

    # Droping orphan_drop_df rows from init_orphan_df
    new_orphan_df = concat_dfs([init_orphan_df, orphan_drop_df], keep=False)

    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {firstname_initials_col_base_alias + "_x": \
                                 firstname_initials_col_base_alias}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    # Saving new_submit_df and new_orphan_df replacing init_submit_df and init_submit_df
    new_submit_df.to_excel(submit_path, index=False)
    new_orphan_df.to_excel(orphan_path, index=False)

    print("    External PhD students added")
    return (new_submit_df, new_orphan_df)


def _add_other_ext(submit_path, orphan_path, others_path):
    """Adds to the publications-list dataframe with one row per author 
    new rows containing the information of specific authors.

    The specific authors are under external hiring contract at the Institute. 
    The list of these employees with the required information is got from 
    the xlsx file which full path is given by 'others_path' in sheet which 
    name is given by 'others_sheet_name_alias'. 
    The row of the added employees is dropped in the publications list 
    with one row per author that has not been identified as Institute employee. 
    The new publications lists are saved as an xlsx files.

    Args:
        submit_path (path): Full path to the xlsx file of the publications list \
        with one row per author with attributes as Institute employee.
        orphan_path (path): Full path to the xlsx file of the publications list \
        with one row per author that has not been identified as Institute employee.
        others_path (path): Full path to the xlsx file giving the employees \
        under external hiring contract at the Institute.
    Returns:
        (tup): (updated dataframe of the publications list with one row \
        per Institute author including employees under external hiring contract \
        at the Institute, updated dataframe of publications list with one row \
        per author that has not been identified as Institute employee).
    Note:
        Care is taken to keep 'NA' value for the first name initiales \
        that are set to NaN by default through the `keep_initials` function \
        imported from "bmfuncts.useful_functs" internal module.
    """

    # Setting aliases for useful column names
    pub_id_alias = bp.COL_NAMES['authors'][0]
    author_id_alias = bp.COL_NAMES['authors'][1]
    converters_alias = eg.EMPLOYEES_CONVERTERS_DIC
    firstname_initials_col_base_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    others_full_name_alias = eg.EMPLOYEES_ADD_COLS['employee_full_name']
    ext_docs_useful_col_list_alias = eg.EXT_DOCS_USEFUL_COL_LIST
    others_pub_last_name_alias = pg.COL_NAMES_PUB_NAMES['last name']
    others_pub_initials_alias = pg.COL_NAMES_PUB_NAMES['initials']
    others_sheet_name_alias = pg.SHEET_NAMES_ORPHAN["others to add"]
    ext_docs_col_adds_list_alias = pg.EXT_DOCS_COL_ADDS_LIST
    orphan_full_name_alias = pg.COL_NAMES_BM['Full_name']
    orphan_last_name_alias = pg.COL_NAMES_BM['Last_name']

    # Reading of the existing submit xlsx file of the corpus year
    # with dates conversion through converters_alias
    init_submit_df = pd.read_excel(submit_path, converters=converters_alias)
    init_orphan_df = pd.read_excel(orphan_path, converters=converters_alias)

    # Replace in "init_submit_df" and "init_orphan_df" NaN values "NA" in first name initials
    init_submit_df = keep_initials(init_submit_df, firstname_initials_col_base_alias,
                                   missing_fill=bp.UNKNOWN)
    init_orphan_df = keep_initials(init_orphan_df, firstname_initials_col_base_alias,
                                   missing_fill=bp.UNKNOWN)

    # Initializing new_submit_df with same column names as init_submit_df
    new_submit_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Initializing the dataframe to be concatenated to init_submit_df in new_submit_df
    # with same column names as init_submit_df
    new_submit_adds_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Aligning column names between init_submit_df and init_orphan_df
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {firstname_initials_col_base_alias : firstname_initials_col_base_alias + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_initials_alias = col_rename_dic[firstname_initials_col_base_alias]

    # Initializing new_orphan_df as copy of init_orphan_df
    #new_orphan_df = init_orphan_df.copy()
    new_orphan_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external phd students xlsx file
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    others_usecols = sum([[others_pub_last_name_alias, others_pub_initials_alias],
                          ext_docs_col_adds_list_alias,
                          ext_docs_useful_col_list_alias,],
                         [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    others_df = pd.read_excel(others_path,
                              sheet_name=others_sheet_name_alias,
                              usecols=others_usecols,
                              converters=converters_alias)

    # Replace in "other_df" NaN values "NA" in first name initials
    others_df = keep_initials(others_df, others_pub_initials_alias)
    others_df = others_df.dropna(how='any')

    # Searching for last names of init_orphan_df in others_df
    # to update submit and orphan files using new_submit_adds_df and new_orphan_drop_df
    for orphan_row_num, _ in init_orphan_df.iterrows():
        author_last_name = init_orphan_df.loc[orphan_row_num, orphan_last_name_alias]
        author_last_name = standardize_txt(author_last_name)
        author_initials = init_orphan_df.loc[orphan_row_num, orphan_initials_alias]
        for others_row_num, _ in others_df.iterrows():
            others_pub_last_name = others_df.loc[others_row_num, others_pub_last_name_alias]
            others_pub_last_name = standardize_txt(others_pub_last_name)
            others_pub_initials = others_df.loc[others_row_num, others_pub_initials_alias]
            if others_pub_last_name==author_last_name and others_pub_initials==author_initials:
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = init_orphan_df.loc[orphan_row_num].to_frame().T

                # Setting the row to copy from others_df as a dataframe
                row_to_copy_df = others_df.loc[others_row_num].to_frame().T

                # Droping the columns of row_to_copy_df that should not be present in row_to_add_df
                row_to_copy_df = row_to_copy_df.drop([others_pub_last_name_alias, others_pub_initials_alias],
                                                     axis=1)

                # Merging the two dataframes on respective full name column
                row_to_add_df = pd.merge(row_to_move_df,
                                         row_to_copy_df,
                                         left_on=[orphan_full_name_alias],
                                         right_on=[others_full_name_alias],
                                         how='left')

                # Appending the merged df to new_submit_adds_df
                new_submit_adds_df = concat_dfs([new_submit_adds_df, row_to_add_df],
                                                concat_ignore_index=True)

                # Appending row_to_move_df to  orphan_drop_df
                orphan_drop_df = concat_dfs([orphan_drop_df, row_to_move_df],
                                            concat_ignore_index=True)

    # Concatenating init_submit_df and new_submit_adds_df
    new_submit_df = concat_dfs([init_submit_df, new_submit_adds_df])
    new_submit_df = new_submit_df.sort_values([pub_id_alias, author_id_alias])

    # Dropping orphan_drop_df rows from init_orphan_df
    new_orphan_df = concat_dfs([init_orphan_df, orphan_drop_df], keep=False)

    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {firstname_initials_col_base_alias + "_x": \
                                 firstname_initials_col_base_alias}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    # Saving new_submit_df and new_orphan_df replacing init_submit_df and init_submit_df
    new_submit_df.to_excel(submit_path, index=False)
    new_orphan_df.to_excel(orphan_path, index=False)

    print("    Other external collaborators added")
    return (new_submit_df, new_orphan_df)


def _change_col_names(institute, org_tup, submit_path, orphan_path):
    """Sets new column names to the files pointed by 'submit_path' 
    and 'orphan_path' paths.

    For that it uses the `build_col_conversion_dic` function 
    imported from `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        submit_path (path): Full path to the xlsx file of the publications list \
        with one row per author with attributes as Institute employee.
        orphan_path (path): Full path to the xlsx file of the publications list \
        with one row per author that has not been identified as Institute employee.
    Returns:
        (str): End message recalling the full paths to the modified files.        
    """

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    orphan_col_rename_dic = col_rename_tup[0]
    submit_col_rename_dic = col_rename_tup[1]

    # Read of the 'submit' file with dates convertion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(submit_path, converters=eg.EMPLOYEES_CONVERTERS_DIC,
                              keep_default_na=False)
    submit_df = submit_df.rename(columns=submit_col_rename_dic)

    # Resaving submit_df
    submit_df.to_excel(submit_path, index=False)

    # Read of the 'orphan' file
    orphan_df = pd.read_excel(orphan_path, keep_default_na=False)
    orphan_df = orphan_df.rename(columns=orphan_col_rename_dic)

    # Resaving orphan_df
    orphan_df.to_excel(orphan_path, index=False)

    end_message = f"Column renamed in files: \n  '{submit_path}' \n  '{orphan_path}' "
    return end_message


def _split_orphan(org_tup, working_folder_path, orphan_file_name, verbose=False):
    """Splits the publications list with one row per author that has not been identified 
    as Institute employees.

    The split is in separate lists of publications depending on values in columns 
    given by 'inst_col_list' list that is specific to the Institute. Some lists 
    of publications identified by 'orphan_drop_dict' dict that is specific to 
    the Institute, are dropped from the initial publications list with one row 
    per author that has not been identified as Institute employees. The lists 
    resulting from the split are saved as xlsx files in the folder which full path 
    is given by 'orphan_path'.

    Args:
        org_tup (tup): Contains Institute parameters.
        working_folder_path (path): Full path to working folder.
        orphan_file_name (str): File name of the xlsx file of the publications list \
        with one row per author that has not been identified as Institute employee.
        verbose (bool): Status of prints (default = False).
    Returns:
        (bool): The empty status of the publications list with authors \
        not found in the employees database.
    """

    # Internal function
    def _save_inst_col_df(inst_col, df_to_save):
        if inst_col=="all_undrop":
            file_path = orphan_path
        else:
            file_name = inst_col + "_" + orphan_file_name
            file_path = working_folder_path / Path(file_name)
        df_to_save.to_excel(file_path, index=False)
        message = f"    File of orphan authors created for Institute subdivision: {inst_col}"
        if verbose:
            print(message)

    # Setting useful aliases
    converters_alias = eg.EMPLOYEES_CONVERTERS_DIC

    # Setting useful column names list and droping status
    inst_col_list = org_tup[4]
    orphan_drop_dict = org_tup[10]

    # Reading of the existing orphan xlsx file
    # with dates conversion through converters_alias
    orphan_path = working_folder_path / Path(orphan_file_name)
    orphan_df = pd.read_excel(orphan_path, converters=converters_alias, keep_default_na=False)

    # Creating, and saving as an xlsx file, orphan authors for each Institute subdivision
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

    # Updating orphab status
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


def recursive_year_search(out_path, empl_dict, institute, org_tup,
                          bibliometer_path, datatype, corpus_year, search_depth,
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
    10. An xlsx file containing the unique hash ID built for each publication \
    is created through the `create_hash_id` function imported from "bmfuncts.create_hash_id" \
    module.

    Args:
        out_path (path): Full path to the folder for saving built dataframes. 
        empl_dict (dict): The employees database as a dict keyed by the years \
        and valued by the employees data for each year.
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): Contains the corpus year defined by 4 digits.
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
        Care is taken to keep 'NA' value for the first name initiales \
        that are set to NaN by default through the `keep_initials` function \
        imported from "bmfuncts.useful_functs" internal module.
    """
    print(f"\nMerge publications and employees information launched for year {corpus_year}...")

    # Setting useful aliases
    pub_id_alias = bp.COL_NAMES['pub_id']
    mat_col_alias = eg.EMPLOYEES_USEFUL_COLS['matricule']
    initials_col_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    submit_file_name_alias = pg.ARCHI_YEAR["submit file name"]
    orphan_file_name_alias = pg.ARCHI_YEAR["orphan file name"]
    orphan_treat_alias = pg.ARCHI_ORPHAN["root"]
    adds_file_name_alias = pg.ARCHI_ORPHAN["employees adds file"]

    # Setting local parameters
    orphan_split_status = org_tup[9]

    # Setting useful paths
    submit_path = out_path / Path(submit_file_name_alias)
    orphan_path = out_path / Path(orphan_file_name_alias)
    ext_docs_path = bibliometer_path / Path(orphan_treat_alias) / Path(adds_file_name_alias)
    others_path = bibliometer_path / Path(orphan_treat_alias) / Path(adds_file_name_alias)

    # Building the articles dataframe
    pub_df = build_institute_pubs_authors(institute, org_tup, bibliometer_path,
                                          datatype, corpus_year)

    # Replace in "pub_df" NaN values by UNKNOWN string except in first name initials
    pub_df = keep_initials(pub_df, initials_col_alias, missing_fill=bp.UNKNOWN)

    # Setting the years list for recursive search of author-employee match
    years = _adapt_depth_search(empl_dict, corpus_year, search_depth)

    # Replace in "empl_dict" NaN values by UNKNOWN string except in first name initials
    for year in years:
        empl_dict[year] = keep_initials(empl_dict[year], initials_col_alias,
                                        missing_fill=bp.UNKNOWN)
        empl_dict[year] = empl_dict[year].astype({mat_col_alias: 'str'})
    if progress_callback:
        step = (100 - progress_bar_state) / 100
        progress_callback(progress_bar_state + step * 10)

    # *******************************************************************
    # * Building recursively the `submit_df` and `orphan_df` dataframes *
    # *                 using `empl_dict` files of years                   *
    # *******************************************************************

    # Initializing the dataframes to be built
    # a Data frame containing all matches between article Institute authors and employee names
    submit_df = pd.DataFrame()
    # a Data frame containing containing article Institute authors
    # not matching with any employee name
    orphan_df = pd.DataFrame()

    # Building the initial dataframes
    print("    Initializing cross pub_employees data")
    submit_df, orphan_df = build_submit_df(empl_dict[years[0]],
                                           pub_df, bibliometer_path,
                                           test_case=set_test_case,
                                           test_name=set_test_name)

    # Saving initial files of submit_df and orphan_df
    submit_df.to_excel(submit_path, index=False)
    orphan_df.to_excel(orphan_path, index=False)
    if progress_callback:
        progress_callback(progress_bar_state + step * 20)

    # Adding authors from list of external_phd students and saving new submit_df and orphan_df
    submit_df, orphan_df = _add_ext_docs(submit_path, orphan_path, ext_docs_path)
    if progress_callback:
        progress_callback(progress_bar_state + step * 25)

    # Adding authors from list of external employees under other hiring contract
    # and saving new submit_df and orphan_df
    submit_df, orphan_df = _add_other_ext(submit_path, orphan_path, others_path)
    if progress_callback:
        new_progress_bar_state = progress_bar_state + step * 30
        progress_callback(new_progress_bar_state)
        progress_bar_loop_progression = step * 50 // len(years)

    for _, year in enumerate(years):
        print(f"    Search among employees of {year}")
        # Updating the dataframes submit_df_add and orphan_df
        submit_df_add, orphan_df = build_submit_df(empl_dict[year],
                                                   orphan_df,
                                                   bibliometer_path,
                                                   test_case=set_test_case,
                                                   test_name=set_test_name)

        # Updating submit_df and orphan_df
        submit_df = concat_dfs([submit_df, submit_df_add])

        # Updating progress bar state
        if progress_callback:
            new_progress_bar_state += progress_bar_loop_progression
            progress_callback(new_progress_bar_state)

    # *************************************************************************************
    # * Saving results in 'submit_file_name_alias' file and 'orphan_file_name_alias' file *
    # *************************************************************************************

    # Replace NaN values by UNKNOWN string except in first name initials
    submit_df = keep_initials(submit_df, initials_col_alias, missing_fill=bp.UNKNOWN)
    orphan_df = keep_initials(orphan_df, initials_col_alias, missing_fill=bp.UNKNOWN)
    orphan_status = orphan_df.empty

    # Changing Pub_id columns to a unique Pub_id depending on the year
    print("    Setting year pub IDs")
    submit_df = set_year_pub_id(submit_df, corpus_year, pub_id_alias)
    if not orphan_status:
        orphan_df = set_year_pub_id(orphan_df, corpus_year, pub_id_alias)

    # Saving orphan_df
    orphan_df.to_excel(orphan_path, index=False)

    # Saving submit_df
    submit_df.to_excel(submit_path, index=False)

    # Adding author job type and saving new submit_df
    print("    Adding column with author job type")
    _add_author_job_type(submit_path, submit_path, empl_dict, years)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 5)

    # Adding full article reference and saving new submit_df
    _add_biblio_list(submit_path, submit_path)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 10)

    # Renaming column names using submit_col_rename_dic and orphan_col_rename_dic
    _change_col_names(institute, org_tup, submit_path, orphan_path)

    # Splitting orphan file in subdivisions of Institute
    if orphan_split_status:
        orphan_status = _split_orphan(org_tup, out_path, orphan_file_name_alias)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 15)

    # Creating universal identification of articles independent of database extraction
    file_names_tup = (submit_file_name_alias, orphan_file_name_alias)
    create_hash_id(institute, org_tup, out_path, file_names_tup)
    if progress_callback:
        progress_callback(100)

    end_message = ("Results of search of authors in employees list "
                   f"saved in folder: \n  {out_path}")
    return end_message, orphan_status
