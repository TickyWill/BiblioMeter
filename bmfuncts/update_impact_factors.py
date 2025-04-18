"""Module of functions for updating impact factors in database
and in publications lists.
"""
__all__ = ['update_inst_if_database',
          ]


# Standard library imports
import re
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl import Workbook as openpyxl_Workbook

# local imports
import bmfuncts.pub_globals as pg
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.useful_functs import set_capwords_lambda
from bmfuncts.useful_functs import concat_dfs


def _get_if(if_updated_file_path, useful_col_list):
    """Gets the impact-factors (IFs) dataframe from the file 
    updated with IFs values.

    Args:
        if_updated_file_path (path): Full path to the file updated with IFs values.
        useful_col_list (list): List of column names (str) to be used for IFs dataframe.
    Returns:
        (dataframe): Dataframe of IFs which columns are given by 'useful_col_list'.
    """
    # Setting useful aliases
    most_recent_year_if_col_base_alias = pg.COL_NAMES_BONUS["IF en cours"]

    # Setting useful column names
    journal_col = useful_col_list[0]
    year_if_col = useful_col_list[3]

    # Getting th IFs data
    if_updated_df = pd.read_excel(if_updated_file_path)

    # Replacing by 'year_if_col' the column name containing 'most_recent_year_if_col_base_alias'
    if year_if_col not in if_updated_df.columns:
        for col in if_updated_df.columns:
            if re.findall(most_recent_year_if_col_base_alias, col):
                if_updated_df = if_updated_df.rename(columns={col: year_if_col})

    # Selecting useful columns
    if_updated_df = if_updated_df[useful_col_list]
    if not if_updated_df.empty:
        if_updated_df[journal_col] = if_updated_df.\
            apply(set_capwords_lambda(journal_col), axis=1)

    return if_updated_df


def _get_missing_if_and_issn(bibliometer_path, year, year_useful_col_list, files_tup):
    """Gets missing-IFs data and missing-ISSNs data for the corpus year 
    through the `_get_if` internal function.
    """
    # Setting parameters from args
    pub_list_folder, missing_if_filename_base, missing_issn_filename_base = files_tup

    # Setting useful paths
    year_path = bibliometer_path / Path(year)
    pub_list_path = year_path / Path(pub_list_folder)
    year_missing_if_path = pub_list_path / Path(year + missing_if_filename_base)
    year_missing_issn_path = pub_list_path / Path(year + missing_issn_filename_base)

    # Getting the IFs of the year for the ISSN or e-ISSN already present in the IF database
    missing_if_year_if_df = _get_if(year_missing_if_path,
                                    year_useful_col_list)

    # Getting the IFs of the year for the ISSN or e-ISSN not yet present in the IF database
    missing_issn_year_if_df = _get_if(year_missing_issn_path,
                                      year_useful_col_list)

    return missing_if_year_if_df, missing_issn_year_if_df


def _update_year_if_database(institute, org_tup, bibliometer_path,
                             corpus_year, year_if_db_df,
                             most_recent_year, files_tup,
                             add_corpus_years_list=None):
    """Updates the dataframe of impact_factors (IFs) database of a year 
    with the IFs dataframes extracted from the files which full paths 
    are given by 'year_missing_if_path' and 'year_missing_issn_path'.

    The extraction is done through the `_get_missing_if_and_issn` internal function. 
    Also, the dataframe of IFs database of the most recent year is initialized.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4-digits year of the corpus.
        year_if_db_df (dataframe): IFs database of a given year to be updated.
        most_recent_year (str): 4-digits most-recent year in IFs database.
        files_tup (tup): (publications-list folder name (str), \
        base for building missing-IFs file name (str), \
        base for building missing-ISSNs file name (str)).
        add_corpus_years_list (list): List of corpuses of which the filled \
        missing-IFs and missing-ISSNs data have to be added to the ones of \
        the "corpus_year" corpus corresponding to the "most_recent_year" year.
    Returns:
        (tup): (fully updated IFs database of the given year (dataframe), \
        partial IFs database of most-recent-year limited to the \
        corpus journals data (dataframe))
    """
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

    # Setting useful columns list for the year files with IFs of corpus year
    corpus_year_useful_col_list = [journal_col_alias, issn_col_alias,
                                   eissn_col_alias, corpus_year_if_col]

    # Getting the IFs of the corpus year for the ISSN or e-ISSN
    # already present and not yet present in the IF database respectively
    return_tup = _get_missing_if_and_issn(bibliometer_path, corpus_year,
                                          corpus_year_useful_col_list, files_tup)
    missing_if_corpus_year_if_df, missing_issn_corpus_year_if_df = return_tup

    if add_corpus_years_list:
        for year in add_corpus_years_list:
            # Getting the IFs of the year for the ISSN or e-ISSN
            # already present and not yet present in the IF database respectively
            return_tup = _get_missing_if_and_issn(bibliometer_path, year,
                                                  corpus_year_useful_col_list, files_tup)
            add_missing_if_year_if_df, add_missing_issn_year_if_df = return_tup

            # Completing "missing_if_corpus_year_if_df" and "missing_issn_corpus_year_if_df"
            missing_if_corpus_year_if_df = concat_dfs([missing_if_corpus_year_if_df,
                                                       add_missing_if_year_if_df])
            missing_issn_corpus_year_if_df = concat_dfs([missing_issn_corpus_year_if_df,
                                                         add_missing_issn_year_if_df])

    # Appending 'missing_if_corpus_year_if_df' to  'year_if_db_df'
    if_updated_year_if_db_df = concat_dfs([year_if_db_df,
                                           missing_if_corpus_year_if_df],
                                           dedup_cols=[journal_col_alias])

    # Appending 'missing_issn_corpus_year_if_df' to  'updated_year_if_db_df'
    fully_updated_year_if_db_df = concat_dfs([if_updated_year_if_db_df,
                                              missing_issn_corpus_year_if_df],
                                              dedup_cols=[journal_col_alias])

    # Sorting 'updated_year_if_db_df' by journal column
    fully_updated_year_if_db_df = fully_updated_year_if_db_df.sort_values(by=[journal_col_alias])

    # Setting useful columns list for the year files
    # with IFs of the most recent year
    most_recent_year_useful_col_list = [journal_col_alias, issn_col_alias,
                                        eissn_col_alias, most_recent_year_if_col_alias]

    # Getting the IFs of the most recent year for the ISSN or e-ISSN
    # already present and not yet present in the IF database respectively
    return_tup = _get_missing_if_and_issn(bibliometer_path, corpus_year,
                                          most_recent_year_useful_col_list, files_tup)
    missing_if_most_recent_year_if_df, missing_issn_most_recent_year_if_df = return_tup

    # Initializing the dataframe of IFs of most recent year
    # that will be returned for completion of the most recent year IF database
    corpus_year_most_recent_year_if_df = concat_dfs([missing_if_most_recent_year_if_df,
                                                     missing_issn_most_recent_year_if_df],
                                                     dedup_cols=[journal_col_alias])
    corpus_year_most_recent_year_if_df = corpus_year_most_recent_year_if_df.rename(
        columns={most_recent_year_if_col_alias: new_most_recent_year_if_col_alias,})

    return fully_updated_year_if_db_df, corpus_year_most_recent_year_if_df


def _build_previous_years_if_df(institute, org_tup, bibliometer_path,
                                if_db_dict, if_db_years_list,
                                most_recent_year, journal_col,
                                files_tup, save_params_tup):
    """Updates the impact factors (IFs) database for the years in the 'previous_years_list' years list.

    1. Initializes the dataframe to add for building the IFs database of the most-recent year.
    2. Then, for each IFs-year, the steps are as follows:

        1. Gets the initial database of the IFs-year from the all-years database \
        and capitalizes the journal-names main words through the `set_capwords_lambda` \
        function imported from `bmfuncts.useful_functs` module.
        2. Builds the fully updated dataframes of IFs database for the IFs-year and \
        the partial dataframe of most-recent-year IFs limited to the corpus journals data \
        through the `_update_year_if_database` internal function, with corpus year set to IFs-year.
        3. Appends the partial dataframe of most-recent-year IFs to the dataframe to add \
        for building the IFs database of the most-recent year.
        4. Formats IFs sheet in the 'wb' Openpyxl workbook with sheet name set to IFs-year \
        given by 'if_db_year' through the `formatting_wb_sheet` function imported from \
        `bmfuncts.format_files` module.        

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        if_db_dict (hierarchical dict): IFs database keyed by years (str) \
        and valued by data of IFs per journal (dataframe).
        most_recent_year (str): 4-digits most-recent year in IFs database.
        journal_col (str): Column name of journals.
        files_tup (tup): Files parameters used by `_update_year_if_database` \
        internal function.
        save_params_tup (tup): (workbook to be updated (Openpyxl workbook), \
        sheets status true if no sheet yet added to the workbook (bool)).
    Returns:
        (tup): (updated workbook (Openpyxl workbook), \
        updated sheets status (bool), \
        the dataframe to add for building the IFs database \
        of the most-recent year (dataframe)).
    """

    # Setting parameters from args
    wb, first = save_params_tup

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN

    # Building fully updated IFs database for years
    # before the most recent year available for IFs
    most_recent_year_if_df_to_add = pd.DataFrame(columns=if_db_dict[most_recent_year].\
                                                 columns)
    previous_years_list = if_db_years_list[:-1]
    for if_db_year in previous_years_list:
        year_if_db_df = if_db_dict[if_db_year]
        year_if_db_df = year_if_db_df.fillna(unknown_alias)
        year_if_db_df[journal_col] = year_if_db_df.\
            apply(set_capwords_lambda(journal_col), axis=1)
        corpus_year = if_db_year
        dfs_tup = _update_year_if_database(institute, org_tup, bibliometer_path,
                                           corpus_year, year_if_db_df,
                                           most_recent_year, files_tup)
        corpus_year_most_recent_year_if_df_to_add = dfs_tup[1]
        most_recent_year_if_df_to_add = concat_dfs([most_recent_year_if_df_to_add,
                                                    corpus_year_most_recent_year_if_df_to_add],
                                                    dedup_cols=[journal_col])
        fully_updated_year_if_db_df = dfs_tup[0]
        if_sheet_name = if_db_year
        if_db_title = pg.DF_TITLES_LIST[3]
        wb = format_wb_sheet(if_sheet_name, fully_updated_year_if_db_df,
                             if_db_title, wb, first)
        first = False
    return wb, first, most_recent_year_if_df_to_add


def _build_recent_year_if_df(institute, org_tup, bibliometer_path,
                             if_db_dict, off_if_db_years_list,
                             most_recent_year_if_df_to_add,
                             most_recent_year, journal_col,
                             files_tup, save_params_tup):
    """Updates the impact factors (IFs) database for the most-recent year.

    1. Initializes the dataframe of the IFs database of the most-recent year \
    from the all-years database and capitalizes the journal-names main words 
    through the `set_capwords_lambda` function imported from \
    `bmfuncts.useful_functs` module.
    2. Then, for each corpus year in the 'off_if_db_years_list' years list, \
    the steps are as follows:

        1. Builds the partial dataframe of most-recent-year IFs limited to the journals data \
        of the corpus through the `_update_year_if_database` internal function.
        2. Appends the partial dataframe of most-recent-year IFs to the dataframe to add \
        for building the IFs database of the most-recent year and drops duplicates.

    3. Appends the resulting dataframe of the loop to the initial dataframe of the IFs \
    database of the most-recent year.
    4. Formats IFs-most-recent-year sheet in the 'wb' Openpyxl workbook with sheet name \
    set to the first corpus-year in the 'off_if_db_years_list' years list given by \
    'off_if_db_years_list[0]' through the `formatting_wb_sheet` function imported from \
    `bmfuncts.format_files` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        if_db_dict (hierarchical dict): IFs database keyed by years (str) \
        and valued by data of IFs per journal (dataframe).
        off_if_db_years_list (list): The list of years not in the IFs database.
        most_recent_year (str): 4-digits most-recent year in IFs database.
        journal_col (str): Column name of journals.
        files_tup (tup): Files parameters used by `_update_year_if_database` \
        internal function.
        save_params_tup (tup): (workbook to be updated (Openpyxl workbook), \
        sheets status true if no sheet yet added to the workbook (bool)).
    Returns:
        (Openpyxl workbook): The fully updated workbook of the IFs database.
    """

    # Setting parameters from args
    wb, first = save_params_tup

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN

    # Initializing 'most_recent_year_if_db_df' dataframe
    most_recent_year_if_db_df = if_db_dict[most_recent_year]
    most_recent_year_if_db_df = most_recent_year_if_db_df.fillna(unknown_alias)
    most_recent_year_if_db_df[journal_col] = most_recent_year_if_db_df.\
        apply(set_capwords_lambda(journal_col), axis=1)

    # Building fully updated Ifs database for years beginning
    # from the most recent year available for IFs
    for corpus_year in off_if_db_years_list:
        add_corpus_years_list = None
        if corpus_year==most_recent_year:
            add_corpus_years_list = [x for x in off_if_db_years_list if x!=corpus_year]
        tup = _update_year_if_database(institute, org_tup, bibliometer_path,
                                       corpus_year, most_recent_year_if_db_df,
                                       most_recent_year, files_tup,
                                       add_corpus_years_list=add_corpus_years_list)
        corpus_year_most_recent_year_if_df_to_add = tup[1]
        most_recent_year_if_df_to_add = concat_dfs([most_recent_year_if_df_to_add,
                                                    corpus_year_most_recent_year_if_df_to_add],
                                                    dedup_cols=[journal_col])

        most_recent_year_if_df_to_add = most_recent_year_if_df_to_add.drop_duplicates()

    most_recent_year_if_db_df = concat_dfs([most_recent_year_if_db_df,
                                            most_recent_year_if_df_to_add],
                                            dedup_cols=[journal_col])
    most_recent_year_if_db_df = most_recent_year_if_db_df.sort_values(by=journal_col)
    if_sheet_name = off_if_db_years_list[0]
    if_db_title = pg.DF_TITLES_LIST[3]
    wb = format_wb_sheet(if_sheet_name, most_recent_year_if_db_df,
                         if_db_title, wb, first)
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
    print("\nUpdate of IF database launched...")

    # Setting aliases of useful columns
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    journal_col_alias = final_col_dic['journal']

    # Setting useful aliases
    if_root_folder_alias = pg.ARCHI_IF["root"]
    missing_if_filename_base_alias = pg.ARCHI_IF["missing_if_base"]
    missing_issn_filename_base_alias = pg.ARCHI_IF["missing_issn_base"]
    inst_all_if_filename_alias = institute + pg.ARCHI_IF["institute_if_all_years"]
    pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]

    # Setting useful paths
    if_root_folder_path = bibliometer_path / Path(if_root_folder_alias)
    inst_all_if_path = if_root_folder_path / Path(inst_all_if_filename_alias)
    if progress_callback:
        progress_callback(20)

    # Getting the IFs database content and its IFSs available years list
    if_db_dict = pd.read_excel(inst_all_if_path, sheet_name=None)
    full_if_db_years_list = list(if_db_dict.keys())
    if_db_years_list = sorted(list(set(full_if_db_years_list).intersection(set(corpi_years_list))))

    # Setting useful parameters for the update of the IFs database
    most_recent_year = if_db_years_list[-1]
    off_if_db_years_list = sorted(list(set(corpi_years_list) - set(if_db_years_list[:-1])))
    if progress_callback:
        progress_callback(30)

    # Initialize parameters for saving results as multisheet workbook
    first = True
    wb = openpyxl_Workbook()

    # Setting the IFs-years sheets not to be updated (not part of corpus years)
    kept_if_db_years_list = sorted(list(set(full_if_db_years_list) - set(if_db_years_list)))
    if kept_if_db_years_list:
        for if_year in kept_if_db_years_list:
            if_sheet_name = if_year
            if_db_title = pg.DF_TITLES_LIST[3]
            wb = format_wb_sheet(if_sheet_name, if_db_dict[if_year],
                                 if_db_title, wb, first)
            first = False

    # Setting args tuples
    files_tup = (pub_list_folder_alias, missing_if_filename_base_alias,
                 missing_issn_filename_base_alias)

    # Building fully updated IFs database for years
    # before the most recent year available for IFs
    save_params_tup = (wb, first)
    return_tup = _build_previous_years_if_df(institute, org_tup, bibliometer_path,
                                             if_db_dict, if_db_years_list,
                                             most_recent_year, journal_col_alias,
                                             files_tup, save_params_tup)
    wb, first, most_recent_year_if_df_to_add = return_tup
    if progress_callback:
        progress_callback(60)

    # Building fully updated Ifs database for years beginning
    # from the most recent year available for IFs
    save_params_tup = (wb, first)
    wb = _build_recent_year_if_df(institute, org_tup, bibliometer_path,
                                  if_db_dict, off_if_db_years_list,
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
