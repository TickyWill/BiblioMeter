"""Module of functions for updating impact factors in database
and in publications lists.

"""
__all__ = ['update_inst_if_database',
           'journal_capwords',
          ]


# Standard library imports
import re
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl import Workbook

# local imports
import bmfuncts.pub_globals as pg
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.useful_functs import mise_en_page

def journal_capwords(text):
    """Capitalizes words in journal names except those given 
    by the 'BM_LOW_WORDS_LIST' global import from globals 
    module imported as pg.

    Args:
        text (str): Journal name to be capitalized by words.
    Returns:
        (str): Journal name capitalized by main words.
    """
    text_split_list = []
    for x in text.split():
        if x.lower() in pg.BM_LOW_WORDS_LIST:
            x = x.lower()
        else:
            x = x.capitalize()
        text_split_list.append(x)
    text = " ".join(text_split_list)
    return text


def _capwords_journal_col(journal_col):
    return lambda row: journal_capwords(row[journal_col])


def _formatting_wb_sheet(institute, org_tup, if_sheet_name, df,
                         wb, first, if_database):
    """Formats impact-factors (IFs) sheet in the 'wb' Openpyxl workbook 
    as first sheet of the workbook if first is True.

    This done through the `mise_en_page` function 
    imported from the `bmfuncts.useful_functs` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        if_sheet_name (str): 4-digits IFs sheet-name.
        df (dataframe): IFs database of a  year.
        wb (Openpyxl workbook): Workbook to be updated with the 'if_sheet_name' sheet.
        first (bool): True if the sheet to add is the first of the workbook.
        if_database (bool) : True if impact-factors database is concerned. 
    Returns:
        (Openpyxl workbook): The updated workbook with the 'if_sheet_name' sheet.
    """
    if first:
        wb, ws = mise_en_page(institute, org_tup, df, wb, if_database)
        ws.title = if_sheet_name
    else:
        wb.create_sheet(if_sheet_name)
        wb.active = wb[if_sheet_name]
        wb, _ = mise_en_page(institute, org_tup, df, wb, if_database)
    return wb


def _get_if(if_updated_file_path, useful_col_list,
            journal_col, year_if_col_alias):
    """Gets the impact-factors (IFs) dataframe from the file 
    updated with IFs values.

    Args:
        if_updated_file_path (path): Full path to the file updated with IFs values.
        useful_col_list (list): List of column names (str) to be used for IFs dataframe.
        journal_col (str): Column name of journal names to capitalized.
        year_if_col_alias (str): Column name of year IFs.
    Returns:
        (dataframe): Dataframe of IFs which columns are given by 'useful_col_list'.
    """
    # Setting useful aliases
    most_recent_year_if_col_base_alias = pg.COL_NAMES_BONUS["IF en cours"]

    if_updated_df = pd.read_excel(if_updated_file_path)
    
    # Replacing by 'year_if_col_alias' the column name containing 'most_recent_year_if_col_base_alias'
    if year_if_col_alias not in if_updated_df.columns:
        for col in if_updated_df.columns:
            if re.findall(most_recent_year_if_col_base_alias, col):
                if_updated_df.rename(columns = {col: year_if_col_alias}, inplace = True)

    # Selecting useful columns
    if_updated_df = if_updated_df[useful_col_list]
    if not if_updated_df.empty:
        if_updated_df[journal_col] = if_updated_df.\
            apply(_capwords_journal_col(journal_col), axis = 1)

    return if_updated_df


def _append_df(df1, df2, col_alias):
    """Allows to avoid warnings when using pandas concat of two dataframes 
    and drops duplicates on col_alias in the concatenated dataframe.

    Args:
        df1 (dataframe): First data to concatenate.
        df2 (dataframe): Second data to concatenate.
        col_alias (str): Name of the column used for deduplication \
        after concatenation.
    Returns:
        (dataframe): Result of the concatenation.    
    """
    concat_df = df1.copy()
    if df1.empty:
        concat_df = df2.copy()
    else:
        if not df2.empty:
            concat_df = pd.concat([df1, df2])
    concat_df = concat_df.drop_duplicates(subset = col_alias,
                                          keep = 'last')
    return concat_df


def _update_year_if_database(institute, org_tup, bibliometer_path,
                             corpus_year, year_if_db_df,
                             most_recent_year, files_tup):
    """Updates the dataframe of impact_factors (IFs) database of a year 
    with the IFs dataframes extracted from the files which full paths 
    are given by 'year_missing_if_path' and 'year_missing_issn_path'.

    The extraction is done through the `_get_if` internal function. 
    Also, the dataframe of IFs database of the most recent year is initialized.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4-digits year of the corpus.
        year_if_db_df (dataframe): IFs database of a given year to be updated.
        most_recent_year (str): 4-digits most-recent year in IFs database.
        files_tup (tup): Tuple = (publications-list folder name (str), \
        base for building missing-IFs file name (str), \
        base for building missing-ISSNs file name (str)).
    Returns:
        (tup): (fully updated IFs database of the given year (dataframe), \
        partial IFs database of most-recent-year limited to the \
        corpus journals data (dataframe))
    """

    # Setting parameters from args
    pub_list_folder, missing_if_filename_base, missing_issn_filename_base = files_tup
    
    # Setting aliases of useful columns
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    journal_col_alias = final_col_dic['journal']
    issn_col_alias = final_col_dic['issn']
    eissn_col_alias = pg.COL_NAMES_BONUS['e-ISSN']
    database_if_col_alias = pg.COL_NAMES_BONUS["IF clarivate"]
    most_recent_year_if_col_base_alias = pg.COL_NAMES_BONUS["IF en cours"]

    # Setting specific column names
    corpus_year_if_col = database_if_col_alias + " " + corpus_year
    most_recent_year_if_col_alias = most_recent_year_if_col_base_alias + \
                                    ", " + most_recent_year
    new_most_recent_year_if_col_alias = database_if_col_alias + " " + most_recent_year

    # Setting useful paths
    corpus_year_path = bibliometer_path / Path(corpus_year)
    pub_list_path = corpus_year_path / Path(pub_list_folder)
    year_missing_if_path = pub_list_path / Path(corpus_year + missing_if_filename_base)
    year_missing_issn_path = pub_list_path / Path(corpus_year + missing_issn_filename_base)

    # Setting useful columns list for the year files with IFs of corpus year
    corpus_year_useful_col_list = [journal_col_alias, issn_col_alias,
                                   eissn_col_alias, corpus_year_if_col]

    # Getting the IFs of the year for the ISSN or e-ISSN already present in the IF database
    missing_if_corpus_year_if_df = _get_if(year_missing_if_path,
                                           corpus_year_useful_col_list,
                                           journal_col_alias,
                                           corpus_year_if_col)

    # Getting the IFs of the year for the ISSN or e-ISSN not yet present in the IF database
    missing_issn_corpus_year_if_df = _get_if(year_missing_issn_path,
                                             corpus_year_useful_col_list,
                                             journal_col_alias,
                                             corpus_year_if_col)

    # Appending 'missing_if_corpus_year_if_df' to  'year_if_db_df'
    if_updated_year_if_db_df = _append_df(year_if_db_df,
                                          missing_if_corpus_year_if_df,
                                          journal_col_alias)

    # Appending 'missing_issn_corpus_year_if_df' to  'updated_year_if_db_df'
    fully_updated_year_if_db_df = _append_df(if_updated_year_if_db_df,
                                             missing_issn_corpus_year_if_df,
                                             journal_col_alias)

    # Sorting 'updated_year_if_db_df' by journal column
    fully_updated_year_if_db_df.sort_values(by = [journal_col_alias], inplace = True)

    # Setting useful columns list for the year files
    # with IFs of most recent year
    most_recent_year_useful_col_list = [journal_col_alias, issn_col_alias,
                                        eissn_col_alias, most_recent_year_if_col_alias]

    # Getting the IFs of the most recent year for the ISSN or e-ISSN
    # already present in the IF database
    missing_if_most_recent_year_if_df = _get_if(year_missing_if_path,
                                                most_recent_year_useful_col_list,
                                                journal_col_alias,
                                                most_recent_year_if_col_alias)

    # Getting the IFs of the most recent year for the ISSN or e-ISSN
    # not yet present in the IF database
    missing_issn_most_recent_year_if_df = _get_if(year_missing_issn_path,
                                                  most_recent_year_useful_col_list,
                                                  journal_col_alias,
                                                  most_recent_year_if_col_alias)

    # Initializing the dataframe of IFs of most recent year
    # that will be returned for completion of the most recent year IF database
    corpus_year_most_recent_year_if_df = _append_df(missing_if_most_recent_year_if_df,
                                                    missing_issn_most_recent_year_if_df,
                                                    journal_col_alias)
    corpus_year_most_recent_year_if_df.rename(columns = {most_recent_year_if_col_alias:
                                                         new_most_recent_year_if_col_alias,},
                                              inplace = True)

    return fully_updated_year_if_db_df, corpus_year_most_recent_year_if_df


def _build_previous_years_if_df(institute, org_tup, bibliometer_path,
                                if_db_df, if_db_years_list,
                                most_recent_year, journal_col,
                                files_tup, save_params_tup):
    """Updates the IFs database for the years in the 'previous_years_list' years list.

    1. Initializes the dataframe to add for building the IFs database of the most-recent year.
    2. Then, for each IFs-year, the steps are as follows:

        1. Gets the initial database of the IFs-year from the all-years database \
        and capitalizes the journal-names main words through the `_capwords_journal_col` \
        internal function.
        2. Builds the fully updated dataframes of IFs database for the IFs-year and \
        the partial dataframe of most-recent-year IFs limited to the corpus journals data \
        through the `_update_year_if_database` internal function, with corpus year set to IFs-year.
        3. Appends the partial dataframe of most-recent-year IFs to the dataframe to add \
        for building the IFs database of the most-recent year.
        4. Formats IFs sheet in the 'wb' Openpyxl workbookthrough the `_formatting_wb_sheet` \
        internal function with sheet name set to IFs-year given by 'if_db_year'.        

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        if_db_df (dataframe): IFs database of all years.
        most_recent_year (str): 4-digits most-recent year in IFs database.
        journal_col (str): Column name of journals.
        files_tup (tup): Files parameters used by `_update_year_if_database` \
        internal function.
        save_params_tup (tup): Tuple = (workbook to be updated (Openpyxl workbook), \
        sheets status, True no sheet yet added to the workbook (bool), \
        IFs-database status, True if IFs database concerned).
    Returns:
        (tup): Tuple = (updated workbook (Openpyxl workbook), \
        updated sheets status (bool), \
        the dataframe to add for building the IFs database \
        of the most-recent year (dataframe)).
    """

    # Setting parameters from args
    wb, first, if_database = save_params_tup

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN

    # Building fully updated IFs database for years
    # before the most recent year available for IFs
    most_recent_year_if_df_to_add = pd.DataFrame(columns = if_db_df[most_recent_year].\
                                                 columns)
    previous_years_list = if_db_years_list[:-1]
    for if_db_year in previous_years_list:
        year_if_db_df = if_db_df[if_db_year]
        year_if_db_df.fillna(unknown_alias, inplace = True)
        year_if_db_df[journal_col] = year_if_db_df.\
            apply(_capwords_journal_col(journal_col), axis = 1)
        corpus_year = if_db_year
        dfs_tup = _update_year_if_database(institute, org_tup, bibliometer_path,
                                           corpus_year, year_if_db_df,
                                           most_recent_year, files_tup)
        corpus_year_most_recent_year_if_df_to_add = dfs_tup[1]
        most_recent_year_if_df_to_add = _append_df(most_recent_year_if_df_to_add,
                                                   corpus_year_most_recent_year_if_df_to_add,
                                                   journal_col)
        fully_updated_year_if_db_df = dfs_tup[0]
        if_sheet_name = if_db_year
        wb = _formatting_wb_sheet(institute, org_tup,
                                  if_sheet_name, fully_updated_year_if_db_df,
                                  wb, first, if_database)
        first = False
    return wb, first, most_recent_year_if_df_to_add


def _build_recent_year_if_df(institute, org_tup, bibliometer_path,
                             if_db_df, off_if_db_years_list,
                             most_recent_year_if_df_to_add,
                             most_recent_year, journal_col,
                             files_tup, save_params_tup):
    """Updates the IFs database for the most-recent year.

    1. Initializes the dataframe of the IFs database of the most-recent year \
    from the all-years database and capitalizes the journal-names main words 
    through the `_capwords_journal_col` internal function.
    2. Then, for each corpus year in the 'off_if_db_years_list' years list, \
    the steps are as follows:

        1. Builds the partial dataframe of most-recent-year IFs limited to the journals data \
        of the corpus through the `_update_year_if_database` internal function.
        2. Appends the partial dataframe of most-recent-year IFs to the dataframe to add \
        for building the IFs database of the most-recent year and drops duplicates.

    3. Appends the resulting dataframe of the loop to the initial dataframe of the IFs \
    database of the most-recent year.
    4. Formats IFs-most-recent-year sheet in the 'wb' Openpyxl workbook through \
    the `_formatting_wb_sheet` internal function with sheet name set to the first \
    corpus-year in the 'off_if_db_years_list' years list given by 'off_if_db_years_list[0]'.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        if_db_df (dataframe): IFs database of all years.
        most_recent_year (str): 4-digits most-recent year in IFs database.
        journal_col (str): Column name of journals.
        files_tup (tup): Files parameters used by `_update_year_if_database` \
        internal function.
        save_params_tup (tup): Tuple = (workbook to be updated (Openpyxl workbook), \
        sheets status, True no sheet yet added to the workbook (bool), \
        IFs-database status, True if IFs database concerned).
    Returns:
        (Openpyxl workbook): The fully updated workbook of the IFs database.
    """

    # Setting parameters from args
    wb, first, if_database = save_params_tup

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN

    # Initializing 'most_recent_year_if_db_df' dataframe 
    most_recent_year_if_db_df = if_db_df[most_recent_year]
    most_recent_year_if_db_df.fillna(unknown_alias, inplace = True)
    most_recent_year_if_db_df[journal_col] = most_recent_year_if_db_df.\
        apply(_capwords_journal_col(journal_col), axis = 1)

    # Building fully updated Ifs database for years beginning
    # from the most recent year available for IFs    
    for corpus_year in off_if_db_years_list:
        tup = _update_year_if_database(institute, org_tup, bibliometer_path,
                                       corpus_year, most_recent_year_if_db_df,
                                       most_recent_year, files_tup)
        corpus_year_most_recent_year_if_df_to_add = tup[1]
        most_recent_year_if_df_to_add = _append_df(most_recent_year_if_df_to_add,
                                                   corpus_year_most_recent_year_if_df_to_add,
                                                   journal_col)

        most_recent_year_if_df_to_add.drop_duplicates(inplace = True)

    most_recent_year_if_db_df = _append_df(most_recent_year_if_db_df,
                                           most_recent_year_if_df_to_add,
                                           journal_col)
    if_sheet_name = off_if_db_years_list[0]
    wb = _formatting_wb_sheet(institute, org_tup, if_sheet_name,
                              most_recent_year_if_db_df,
                              wb, first, if_database)
    return wb


def update_inst_if_database(institute, org_tup, bibliometer_path,
                            corpi_years_list, progress_callback=None):
    """Updates the impact-factors (IFs) database of the Institute using the files 
    where IFs have been added by the user for each existing corpuses.

    1. Gets the initial all-years database which full path is given by \
    'inst_all_if_path'.
    2. Sets useful parameters for using `_build_previous_years_if_df` and \
    `_build_recent_year_if_df` internal functions, including 'wb' workbook \
    for saving updated IFs database as multisheet workbook.
    3. Updates 'wb' workbook through the `_build_previous_years_if_df` \
    internal function to build fully updated IFs database for years before \
    the most recent year available for IFs.
    4. Updates 'wb' workbook through the `_build_recent_year_if_df` \
    internal function to build fully updated IFs database for years beginning \
    from the most recent year available for IFs.
    5. Saves the 'wb' workbook using the 'inst_all_if_path' full path.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (tup): (end message recalling the full path to the saved file \
        of the IFs database (str), List of IFs-database years (4-digits strings)).
    """

    # Setting aliases of useful columns
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    journal_col_alias = final_col_dic['journal']

    # Setting useful aliases
    if_root_folder_alias             = pg.ARCHI_IF["root"]
    missing_if_filename_base_alias   = pg.ARCHI_IF["missing_if_base"]
    missing_issn_filename_base_alias = pg.ARCHI_IF["missing_issn_base"]
    inst_all_if_filename_alias       = institute + pg.ARCHI_IF["institute_if_all_years"]
    pub_list_folder_alias            = pg.ARCHI_YEAR["pub list folder"]

    # Setting useful paths
    if_root_folder_path = bibliometer_path / Path(if_root_folder_alias)
    inst_all_if_path    = if_root_folder_path / Path(inst_all_if_filename_alias)
    if progress_callback:
        progress_callback(20)

    # Getting the IFs database content and its IFSs available years list
    if_db_df = pd.read_excel(inst_all_if_path, sheet_name = None)
    if_db_years_list     = list(if_db_df.keys())

    # Setting useful parameters for the update of the IFs database
    most_recent_year = if_db_years_list[-1]
    off_if_db_years_list = sorted(list(set(corpi_years_list) - set(if_db_years_list[:-1])))
    if progress_callback:
        progress_callback(30)

    # Initialize parameters for saving results as multisheet workbook
    if_database = True
    first = True
    wb = Workbook()
    
    # Setting args tuples
    files_tup = (pub_list_folder_alias, missing_if_filename_base_alias,
                 missing_issn_filename_base_alias)

    # Building fully updated IFs database for years
    # before the most recent year available for IFs
    save_params_tup = (wb, first, if_database)
    return_tup = _build_previous_years_if_df(institute, org_tup, bibliometer_path,
                                             if_db_df, if_db_years_list,
                                             most_recent_year, journal_col_alias,
                                             files_tup, save_params_tup)
    wb, first, most_recent_year_if_df_to_add = return_tup
    if progress_callback:
        progress_callback(60)

    # Building fully updated Ifs database for years beginning
    # from the most recent year available for IFs
    save_params_tup = (wb, first, if_database)
    wb = _build_recent_year_if_df(institute, org_tup, bibliometer_path,
                                  if_db_df, off_if_db_years_list,
                                  most_recent_year_if_df_to_add,
                                  most_recent_year, journal_col_alias,
                                  files_tup, save_params_tup)
    if progress_callback:
        progress_callback(90)

    # Saving workbook
    wb.save(inst_all_if_path)
    if progress_callback:
        progress_callback(100)

    end_message = f"IFs database updated in file : \n  '{inst_all_if_path}'"
    return end_message, if_db_years_list
