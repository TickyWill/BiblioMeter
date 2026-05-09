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
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import set_capwords_lambda


def _get_if(if_updated_file_path, useful_col_list):
    """Gets the impact-factors (IFs) data of journals from the file 
    updated with IFs values.

    The IFs column of the most-recent year is renamed by the last 
    item of the specified columns list. 
    The journal names are capitalized through the `set_capwords_lambda` 
    lambda function imported from the `bmfuncts.useful_functs` module.

    Args:
        if_updated_file_path (path): Full path to the file updated \
        by the user with IFs values.
        useful_col_list (list): List of column names (str) to be selected \
        in the IFs data per journals.
    Returns:
        (dataframe): Dataframe of IFs which columns are given by 'useful_col_list'.
    """
    # Setting useful aliases
    most_recent_year_if_col_base_alias = bm_pg.COL_NAMES_BONUS["IF en cours"]

    # Setting useful column names
    journal_col = useful_col_list[0]
    year_if_col = useful_col_list[-1]

    # Getting the IFs data per journals
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


def _get_missing_if_and_issn(wf_path, corpus_year, year_useful_col_list, if_params_list):
    """Gets missing-IFs data and missing-ISSNs data for the corpus year 
    through the `_get_if` internal function.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): The 4-digits corpus year.
        year_useful_col_list (list): Column names (str) to be selected in the files \
        of the missing IFs and ISSNs.
        if_params_list (list): The folder et the base of file names for building \
        the paths to the files of the missing IFs and ISSNs.
    """
    # Setting parameters from args
    pub_list_folder, missing_if_filename_base, missing_issn_filename_base = if_params_list

    # Setting useful paths dependent on year
    year_path = wf_path / Path(corpus_year)
    pub_list_path = year_path / Path(pub_list_folder)
    year_missing_if_path = pub_list_path / Path(corpus_year + missing_if_filename_base)
    year_missing_issn_path = pub_list_path / Path(corpus_year + missing_issn_filename_base)

    # Getting the IFs of the year for the ISSN or e-ISSN already present in the IF database
    missing_if_year_if_df = _get_if(year_missing_if_path,
                                    year_useful_col_list)

    # Getting the IFs of the year for the ISSN or e-ISSN not yet present in the IF database
    missing_issn_year_if_df = _get_if(year_missing_issn_path,
                                      year_useful_col_list)

    return missing_if_year_if_df, missing_issn_year_if_df


def _set_if_col_names(corpus_year, if_most_recent_year):
    """Sets the column names of IFs depending on the corpus year 
    and on the most recent year of available IFs.

    Args:
        corpus_year (str): The 4-digits corpus year.
        if_most_recent_year (str): The 4-digits most recent year \
        of available IFs.
    Returns:
        (list): [IFs column name (str) of corpus year, \
        Initial IFs column name (str) of IFs most-recent year, \
        Final IFs column name (str) of IFs most-recent year].
    """
    # Setting useful columns aliases
    database_if_col_alias = bm_pg.COL_NAMES_BONUS["IF clarivate"]
    most_recent_year_if_col_base_alias = bm_pg.COL_NAMES_BONUS["IF en cours"]

    # Setting specific column names
    corpus_year_if_col = database_if_col_alias + " " + corpus_year
    most_recent_year_if_col = most_recent_year_if_col_base_alias + ", "
    most_recent_year_if_col += if_most_recent_year
    new_most_recent_year_if_col = database_if_col_alias + " "
    new_most_recent_year_if_col += if_most_recent_year

    # Setting returns
    corpus_year_if_cols_list = [corpus_year_if_col,
                                most_recent_year_if_col,
                                new_most_recent_year_if_col]
    return corpus_year_if_cols_list


def _update_year_if_database(wf_path, corpus_year,
                             year_if_db_df, if_most_recent_year,
                             journal_cols_list, if_params_list,
                             add_corpus_years_list=None):
    """Updates the dataframe of impact_factors (IFs) database of a year 
    with the IFs data per journals extracted from the files which full paths 
    are given by 'year_missing_if_path' and 'year_missing_issn_path'.

    The extraction is done through the `_get_missing_if_and_issn` internal function. 
    Also, the dataframe of IFs data per journals of the most recent year is initialized.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4-digits year of the corpus.
        year_if_db_df (dataframe): IFs data per journals of a given year to be updated.
        if_most_recent_year (str): 4-digits most-recent year in IFs data per journals.
        if_params_list (list): [publications-list folder name (str), \
        base for building missing-IFs file name (str), \
        base for building missing-ISSNs file name (str)].
        add_corpus_years_list (list): List of corpuses of which the filled \
        missing-IFs and missing-ISSNs data have to be added to the ones of \
        the "corpus_year" corpus corresponding to the "if_most_recent_year" year.
    Returns:
        (tup): (fully updated IFs data per journals of the given year (dataframe), \
        partial IFs data per journals of most-recent-year limited to the \
        corpus journals data (dataframe))
    """
    # Setting useful columns names
    journal_col = journal_cols_list[0]
    corpus_year_if_cols_list = _set_if_col_names(corpus_year, if_most_recent_year)
    [corpus_year_if_col,
     most_recent_year_if_col,
     new_most_recent_year_if_col] = corpus_year_if_cols_list

    # Setting useful columns list for the year files with IFs of corpus year
    corpus_year_useful_col_list = sum([journal_cols_list, [corpus_year_if_col]], [])

    # Getting the IFs of the corpus year for the ISSN or e-ISSN
    # already present and not yet present in the IF database respectively
    return_tup = _get_missing_if_and_issn(wf_path, corpus_year,
                                          corpus_year_useful_col_list, if_params_list)
    missing_if_corpus_year_if_df, missing_issn_corpus_year_if_df = return_tup

    if add_corpus_years_list:
        for year in add_corpus_years_list:
            # Getting the IFs of the year for the ISSN or e-ISSN
            # already present and not yet present in the IF database respectively
            return_tup = _get_missing_if_and_issn(wf_path, year,
                                                  corpus_year_useful_col_list,
                                                  if_params_list)
            add_missing_if_year_if_df, add_missing_issn_year_if_df = return_tup

            # Completing "missing_if_corpus_year_if_df" and "missing_issn_corpus_year_if_df"
            missing_if_corpus_year_if_df = concat_dfs([missing_if_corpus_year_if_df,
                                                       add_missing_if_year_if_df])
            missing_issn_corpus_year_if_df = concat_dfs([missing_issn_corpus_year_if_df,
                                                         add_missing_issn_year_if_df])

    # Appending 'missing_if_corpus_year_if_df' to  'year_if_db_df'
    if_updated_year_if_db_df = concat_dfs([year_if_db_df,
                                           missing_if_corpus_year_if_df],
                                           dedup_cols=[journal_col],
                                           keep='last')

    # Appending 'missing_issn_corpus_year_if_df' to  'updated_year_if_db_df'
    fully_updated_year_if_db_df = concat_dfs([if_updated_year_if_db_df,
                                              missing_issn_corpus_year_if_df],
                                              dedup_cols=[journal_col],
                                              keep='last')

    # Sorting 'updated_year_if_db_df' by journal column
    fully_updated_year_if_db_df = fully_updated_year_if_db_df.sort_values(by=[journal_col])

    # Setting useful columns list for the year files
    # with IFs of the most recent year
    most_recent_year_useful_col_list = sum([journal_cols_list, [most_recent_year_if_col]], [])

    # Getting the IFs of the most recent year for the ISSN or e-ISSN
    # already present and not yet present in the IF database respectively
    return_tup = _get_missing_if_and_issn(wf_path, corpus_year,
                                          most_recent_year_useful_col_list,
                                          if_params_list)
    missing_if_most_recent_year_if_df, missing_issn_most_recent_year_if_df = return_tup

    # Initializing the dataframe of IFs of most recent year
    # that will be returned for completion of the most recent year IF database
    corpus_year_most_recent_year_if_df = concat_dfs([missing_if_most_recent_year_if_df,
                                                     missing_issn_most_recent_year_if_df],
                                                     dedup_cols=[journal_col],
                                                     keep='last')
    corpus_year_most_recent_year_if_df = corpus_year_most_recent_year_if_df.rename(
        columns={most_recent_year_if_col: new_most_recent_year_if_col,})

    return fully_updated_year_if_db_df, corpus_year_most_recent_year_if_df


def _build_previous_years_if_df(wf_path, if_db_dict,
                                if_db_years_list, if_most_recent_year,
                                journal_cols_list, if_params_list,
                                save_params_tup):
    """Updates the impact factors (IFs) database for the years in the 'previous_years_list' years list.

    1. Initializes the dataframe to add for building the IFs data per journals of the most-recent year.
    2. Then, for each IFs-year, the steps are as follows:

        1. Gets the initial database of the IFs-year from the all-years database \
        and capitalizes the journal-names main words through the `set_capwords_lambda` \
        function imported from `bmfuncts.useful_functs` module.
        2. Builds the fully updated dataframes of IFs data per journals for the IFs-year and \
        the partial dataframe of most-recent-year IFs limited to the corpus journals data \
        through the `_update_year_if_database` internal function, with corpus year set to IFs-year.
        3. Appends the partial dataframe of most-recent-year IFs to the dataframe to add \
        for building the IFs data per journals of the most-recent year.
        4. Formats IFs sheet in the 'wb' Openpyxl workbook with sheet name set to IFs-year \
        given by 'if_db_year' through the `formatting_wb_sheet` function imported from \
        `bmfuncts.format_files` module.

    Args:
        wf_path (path): Full path to working folder.
        if_db_dict (dict): IFs data per journals keyed by years (str) \
        and valued by data of IFs per journal (dataframe).
        if_most_recent_year (str): 4-digits most-recent year in IFs data per journals.
        journal_cols_list (list): [Column name of journal name (str), Column name of \
        journal ISSN (str), Column name of journal e-ISSN (str)].
        if_params_list (list): Files parameters used by `_update_year_if_database` \
        internal function.
        save_params_tup (tup): (workbook to be updated (Openpyxl workbook), \
        sheets status true if no sheet yet added to the workbook (bool)).
    Returns:
        (tup): (updated workbook (Openpyxl workbook), \
        updated sheets status (bool), \
        the dataframe to add for building the IFs data per journals \
        of the most-recent year (dataframe)).
    """
    # Setting parameters from args
    journal_col = journal_cols_list[0]
    wb, first = save_params_tup

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN

    # Building fully updated IFs data per journals for years
    # before the most recent year available for IFs
    most_recent_year_if_df_to_add = pd.DataFrame(columns=if_db_dict[if_most_recent_year].\
                                                 columns)
    previous_years_list = if_db_years_list[:-1]
    for if_db_year in previous_years_list:
        year_if_db_df = if_db_dict[if_db_year]
        year_if_db_df = year_if_db_df.fillna(unknown_alias)
        year_if_db_df[journal_col] = year_if_db_df.\
            apply(set_capwords_lambda(journal_col), axis=1)
        corpus_year = if_db_year
        dfs_tup = _update_year_if_database(wf_path, corpus_year,
                                           year_if_db_df, if_most_recent_year,
                                           journal_cols_list, if_params_list)
        corpus_year_most_recent_year_if_df_to_add = dfs_tup[1]
        most_recent_year_if_df_to_add = concat_dfs([most_recent_year_if_df_to_add,
                                                    corpus_year_most_recent_year_if_df_to_add],
                                                    dedup_cols=[journal_col],
                                                    keep='last')
        fully_updated_year_if_db_df = dfs_tup[0]
        if_sheet_name = if_db_year
        if_db_title = bm_pg.DF_TITLES_LIST[3]
        wb = format_wb_sheet(if_sheet_name, fully_updated_year_if_db_df,
                             if_db_title, wb, first)
        first = False
    return wb, first, most_recent_year_if_df_to_add


def _build_recent_year_if_df(wf_path, if_db_dict,
                             off_if_db_years_list, if_most_recent_year,
                             most_recent_year_if_df_to_add,
                             journal_cols_list, if_params_list,
                             save_params_tup):
    """Updates the impact factors (IFs) database for the most-recent year.

    1. Initializes the dataframe of the IFs data per journals of the most-recent year \
    from the all-years database and capitalizes the journal-names main words 
    through the `set_capwords_lambda` function imported from \
    `bmfuncts.useful_functs` module.
    2. Then, for each corpus year in the 'off_if_db_years_list' years list, \
    the steps are as follows:

        1. Builds the partial dataframe of most-recent-year IFs limited to the journals data \
        of the corpus through the `_update_year_if_database` internal function.
        2. Appends the partial dataframe of most-recent-year IFs to the dataframe to add \
        for building the IFs data per journals of the most-recent year and drops duplicates.

    3. Appends the resulting dataframe of the loop to the initial dataframe of the IFs \
    database of the most-recent year.
    4. Formats IFs-most-recent-year sheet in the 'wb' Openpyxl workbook with sheet name \
    set to the first corpus-year in the 'off_if_db_years_list' years list given by \
    'off_if_db_years_list[0]' through the `formatting_wb_sheet` function imported from \
    `bmfuncts.format_files` module.

    Args:
        wf_path (path): Full path to working folder.
        if_db_dict (hierarchical dict): IFs data per journals keyed by years (str) \
        and valued by data of IFs per journal (dataframe).
        off_if_db_years_list (list): The list of years not in the IFs data per journals.
        if_most_recent_year (str): 4-digits most-recent year in IFs data per journals.
        most_recent_year_if_df_to_add (dataframe): The data of the previous \
        corpus years to the IFs most-recent year that will be completed with \
        the data of the corpus years next to the IFs most-recent year.
        journal_cols_list (list): [Column name of journal name (str), Column name of \
        journal ISSN (str), Column name of journal e-ISSN (str)].
        if_params_list (list): Files parameters used by `_update_year_if_database` \
        internal function.
        save_params_tup (tup): (workbook to be updated (Openpyxl workbook), \
        sheets status true if no sheet yet added to the workbook (bool)).
    Returns:
        (Openpyxl workbook): The fully updated workbook of the IFs data per journals.
    """

    # Setting parameters from args
    journal_col = journal_cols_list[0]
    wb, first = save_params_tup

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN

    # Initializing 'most_recent_year_if_db_df' dataframe
    most_recent_year_if_db_df = if_db_dict[if_most_recent_year]
    most_recent_year_if_db_df = most_recent_year_if_db_df.fillna(unknown_alias)
    most_recent_year_if_db_df[journal_col] = most_recent_year_if_db_df.\
        apply(set_capwords_lambda(journal_col), axis=1)

    # Building fully updated IFs data per journals for years beginning
    # from the most recent year available for IFs
    corpus_years_list = sum([[if_most_recent_year], off_if_db_years_list], [])
    for corpus_year in corpus_years_list:
        add_corpus_years_list = None
        if corpus_year==if_most_recent_year:
            add_corpus_years_list = [x for x in off_if_db_years_list if x!=corpus_year]
        tup = _update_year_if_database(wf_path, corpus_year,
                                       most_recent_year_if_db_df, if_most_recent_year,
                                       journal_cols_list, if_params_list,
                                       add_corpus_years_list=add_corpus_years_list)
        corpus_year_most_recent_year_if_df_to_add = tup[1]
        most_recent_year_if_df_to_add = concat_dfs([most_recent_year_if_df_to_add,
                                                    corpus_year_most_recent_year_if_df_to_add],
                                                    dedup_cols=[journal_col],
                                                    keep='last')

        most_recent_year_if_df_to_add = most_recent_year_if_df_to_add.drop_duplicates()

    most_recent_year_if_db_df = concat_dfs([most_recent_year_if_db_df,
                                            most_recent_year_if_df_to_add],
                                            dedup_cols=[journal_col],
                                            keep='last')
    most_recent_year_if_db_df = most_recent_year_if_db_df.sort_values(by=journal_col)
    if_sheet_name = if_most_recent_year
    if_db_title = bm_pg.DF_TITLES_LIST[3]
    wb = format_wb_sheet(if_sheet_name, most_recent_year_if_db_df,
                         if_db_title, wb, first)
    return wb


def _set_if_files_param(institute, wf_path):
    """Sets list of useful files parameters for impact-factors update.

    Args:
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
    Returns:
       (tup): (Name bases (list of str) of files of missing IFs and missing ISSN, \
       Folder Name (str in list) of publications list, Full path (path in list) \
       to the IFs data per journals).
    """
    # Setting useful aliases
    if_root_folder_alias = bm_pg.ARCHI_IF["root"]
    missing_if_filename_base_alias = bm_pg.ARCHI_IF["missing_if_base"]
    missing_issn_filename_base_alias = bm_pg.ARCHI_IF["missing_issn_base"]
    inst_all_if_filename_alias = institute + bm_pg.ARCHI_IF["institute_if_all_years"]
    pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]

    # Setting useful paths
    if_root_folder_path = wf_path / Path(if_root_folder_alias)
    inst_all_if_path = if_root_folder_path / Path(inst_all_if_filename_alias)

    # Setting returns
    files_list = [missing_if_filename_base_alias, missing_issn_filename_base_alias]
    folders_list = [pub_list_folder_alias]
    paths_list = [inst_all_if_path]

    return files_list, folders_list, paths_list


def _set_years_lists(if_db_dict, corpus_years_list):
    """Sets the list of years of various kinds depending 
    on years of available IFs and on years of available corpuses.

    Args:
        if_db_dict (dict): The IFs data per journals keyed by years.
        corpus_years_list (list): The list of years (str) \
        of available corpuses.
    Returns:
        (tup): (The list of years (str) of available IFs part of corpus years, \
        The list of corpus years (str) not part of the years of available IFs, \
        The list of years (str) of available IFs not part of corpus years).
    """
    # Setting list of all years of available IFs
    full_if_db_years_list = list(if_db_dict.keys())

    # Setting list of years of available IFs part of corpus years
    if_db_years_list = sorted(list(set(full_if_db_years_list)\
                                   .intersection(set(corpus_years_list))))

    # Setting the list of available IFs not part of corpus years
    kept_if_db_years_list = sorted(list(set(full_if_db_years_list)\
                                        - set(if_db_years_list)))

    # Setting the list of corpus years not part of the years of available IFs
    off_if_db_years_list = sorted(list(set(corpus_years_list)\
                                       - set(if_db_years_list)))

    # Setting returned tuple
    if_db_years_tup = (if_db_years_list, off_if_db_years_list,
                       kept_if_db_years_list)

    return if_db_years_tup


def _clean_journals_data(if_db_dict, journal_cols_list):
    """Builds unique data per journal and ISSN.

    Args:
        if_db_dict (dict): IFs data per journals keyed by years (str) and valued \
        by data of IFs per journal (dataframe).
        journal_cols_list (list): [Column name of journal name (str), \
        Column name of journal ISSN (str), Column name of journal e-ISSN (str)]. 
    Returns:
        (dataframe): The data unique per journal and ISSN.
    """
    # Setting useful col names from journal_cols_list
    journal_col, issn_col, eissn_col = journal_cols_list

    # Building the journals data to homogenize over all IFs-database years
    all_journals_df = pd.DataFrame(columns=journal_cols_list)
    for _, year_if_db in if_db_dict.items():
        year_journal_df = year_if_db[journal_cols_list]
        all_journals_df = concat_dfs([all_journals_df, year_journal_df], dedup=False)
    all_journals_df[journal_col] = all_journals_df.apply(set_capwords_lambda(journal_col), axis=1)

    # Homogenizing the ISSN and e-ISSN per journal name
    data = []
    for journal, journal_df in all_journals_df.groupby(journal_col):
        issns_list = list(set(journal_df[issn_col].to_list()))
        eissns_list = list(set(journal_df[eissn_col].to_list()))
        if len(issns_list)>1 or len(eissns_list)>1:
            for issn, issn_df in journal_df.groupby(issn_col):
                for eissn,_ in issn_df.groupby(eissn_col):
                    if eissn!=issn:
                        data.append([journal, issn, eissn])
        else:
            issn, eissn = issns_list[0], eissns_list[0]
            data.append([journal, issn, eissn])
    new_journal_df = pd.DataFrame(data, columns=journal_cols_list)

    # Homogenizing the e-ISSN per ISSN value
    data = []
    for issn, issn_df in new_journal_df.groupby(issn_col):
        if issn!=bm_pg.NOT_AVAILABLE:
            eissns_list = list(set(issn_df[eissn_col].to_list()))
            while issn in eissns_list:
                eissns_list.remove(issn)
            if eissns_list:
                eissn = eissns_list[0]
            else:
                eissn = issn
            for journal in issn_df[journal_col]:
                data.append([journal, issn, eissn])
        else:
            for _, row in issn_df.iterrows():
                journal = row[journal_col]
                eissn = row[eissn_col]
                data.append([journal, issn, eissn])
    new_all_journals_df = pd.DataFrame(data, columns=journal_cols_list)
    return new_all_journals_df


def _clean_and_save_if_db(inst_all_if_path, journal_cols_list):
    """Rebuilds IF database after cleaning journals data and saves 
    it as multisheet Openpyxl workbook.

    Args:
        inst_all_if_path (path): Full path to the IFs data per journals.
        journal_cols_list (list): [Column name of journal name (str), \
        Column name of journal ISSN (str), Column name of journal e-ISSN (str)]. 
    """
    journal_col, issn_col, eissn_col = journal_cols_list

    # Getting the IFs data per journals and the IFs available years list
    if_db_dict = pd.read_excel(inst_all_if_path, sheet_name=None)

    # Setting unique data per journal name and per ISSN
    new_all_journals_df = _clean_journals_data(if_db_dict, journal_cols_list)

    # Initialize parameters for saving new IIFs data per journals as multisheet workbook
    first = True
    wb = openpyxl_Workbook()

    # Setting unique data per journal in IFs data per journals
    for if_year, year_if_df in if_db_dict.items():
        year_if_df[journal_col] = year_if_df.apply(set_capwords_lambda(journal_col), axis=1)
        new_year_if_df = pd.merge(year_if_df,
                                  new_all_journals_df,
                                  how='left',
                                  left_on=[journal_col],
                                  right_on=[journal_col])
        cols_to_drop = [issn_col + "_x", eissn_col + "_x"]
        new_year_if_df.drop(columns=cols_to_drop, inplace=True)
        new_year_if_df.rename(columns={issn_col + "_y": issn_col,
                                       eissn_col + "_y" : eissn_col},
                              inplace=True)
        new_year_if_df = new_year_if_df[year_if_df.columns.to_list()]
        if_sheet_name = if_year
        if_db_title = bm_pg.DF_TITLES_LIST[3]
        wb = format_wb_sheet(if_sheet_name, new_year_if_df,
                             if_db_title, wb, first)
        first = False
    # Saving the new IFs data per journals as Openpyxl workbook
    wb.save(inst_all_if_path)


def update_inst_if_database(update_db_params_list, progress_callback=None):
    """Updates the impact-factors (IFs) database of the Institute using the files 
    where IFs have been added by the user for each existing corpuses.

    1. Gets the initial all-years database which full path is given by \
    'inst_all_if_path'.
    2. Sets useful parameters for using `_build_previous_years_if_df` and \
    `_build_recent_year_if_df` internal functions, including 'wb' workbook \
    for saving updated IFs data per journals as multisheet workbook.
    3. Updates 'wb' workbook through the `_build_previous_years_if_df` \
    internal function to build fully updated IFs data per journals for years \
    before the most recent year available for IFs.
    4. Updates 'wb' workbook through the `_build_recent_year_if_df` \
    internal function to build fully updated IFs data per journals for years \
    beginning from the most recent year available for IFs.
    5. Saves the 'wb' workbook using the 'inst_all_if_path' full path.

    Args:
        update_db_params_list (list): The list composed of Institute's name (str), \
        the tuple that contains Institute's parameters (tup), the full path to the \
        working folder (path) and the list of years (4-digits strings) of available corpuses. 
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (tup): (end message recalling the full path to the saved file \
        of the IFs data per journals (str), List of IFs-database years (4-digits strings)).
    """
    # Setting parameters values from 'update_db_params_list'
    institute, org_tup, wf_path, print_params, corpus_years_list = update_db_params_list
    print_step_text("\nUpdating IFs data per journals...", print_params)

    # Setting useful columns names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    journal_cols_list = [final_col_dic['journal'], final_col_dic['issn'],
                         bm_pg.COL_NAMES_BONUS['e-ISSN']]

    # Setting IFs files parameters
    files_list, folders_list, paths_list = _set_if_files_param(institute, wf_path)
    if_params_list = sum([folders_list, files_list], [])
    inst_all_if_path = paths_list[0]
    if progress_callback:
        progress_callback(20)

    # Getting the IFs data per journals and the IFs available years list
    if_db_dict = pd.read_excel(inst_all_if_path, sheet_name=None)
    if_db_years_tup = _set_years_lists(if_db_dict, corpus_years_list)
    (if_db_years_list, off_if_db_years_list, kept_if_db_years_list)= if_db_years_tup

    # Setting most recent year of available IFs
    if_most_recent_year = if_db_years_list[-1]

    # Initialize parameters for saving results as multisheet workbook
    first = True
    wb = openpyxl_Workbook()

    # Setting the IFs-years sheets not to be updated (not part of corpus years)
    if kept_if_db_years_list:
        for if_year in kept_if_db_years_list:
            if_sheet_name = if_year
            if_db_title = bm_pg.DF_TITLES_LIST[3]
            wb = format_wb_sheet(if_sheet_name, if_db_dict[if_year],
                                 if_db_title, wb, first)
            first = False
    if progress_callback:
        progress_callback(30)

    # Building fully updated IFs data per journals for years
    # before the most recent year available for IFs
    print_step_text(f"  - For years before {if_most_recent_year}", print_params)
    save_params_tup = (wb, first)
    return_tup = _build_previous_years_if_df(wf_path, if_db_dict,
                                             if_db_years_list, if_most_recent_year,
                                             journal_cols_list, if_params_list,
                                             save_params_tup)
    wb, first, most_recent_year_if_df_to_add = return_tup
    if progress_callback:
        progress_callback(60)

    # Building fully updated IFs data per journals for years beginning
    # from the most recent year available for IFs
    print_step_text(f"  - For years from {if_most_recent_year} and after",
                    print_params)
    save_params_tup = (wb, first)
    wb = _build_recent_year_if_df(wf_path, if_db_dict,
                                  off_if_db_years_list, if_most_recent_year,
                                  most_recent_year_if_df_to_add,
                                  journal_cols_list, if_params_list,
                                  save_params_tup)
    if progress_callback:
        progress_callback(90)

    # Saving workbook
    wb.save(inst_all_if_path)
    if progress_callback:
        progress_callback(95)

    # Extending complementary IFs data to all years of the IFs data per journals
    _clean_and_save_if_db(inst_all_if_path, journal_cols_list)
    if progress_callback:
        progress_callback(100)
    print_step_text(f"  - IFs data updated in file : \n  '{inst_all_if_path}'",
                    print_params)
    return if_db_years_list
