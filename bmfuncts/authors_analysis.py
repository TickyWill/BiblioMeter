"""Module of functions for authors-list analysis
in terms of author position in authors list and number of publications per authors.

"""
__all__ = ['authors_analysis']


# Standard library imports
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg
from bmfuncts.format_files import format_page
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.save_final_results import save_final_results
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import get_final_dedup
from bmfuncts.useful_functs import read_final_submit_data
from bmfuncts.useful_functs import set_saved_results_path
from bmfuncts.useful_functs import set_year_pub_id


def name_capwords(text):
    """Capitalizes words in full names of authors getting 
    rid of particular separators and keeping firstname initiales.

    Args:
        text (str): Full name to be capitalized by words.
    Returns:
        (str): Full name capitalized by words.
    """
    sep_list = ["-", "'"]
    sub_text_list = text.split()[:-1]
    text_split_list = []
    for sub_text in sub_text_list:
        for sep in sep_list:
            if sep in sub_text:
                words_list = [x.capitalize() for x in sub_text.split(sep)]
                sub_text = sep.join(words_list)
            else:
                sub_text = sub_text.capitalize()
        text_split_list.append(sub_text)
    text_split_list.append(text.split()[-1])
    text = " ".join(text_split_list)
    return text


def _read_authors_data(bibliometer_path, saved_results_path,
                       corpus_year):
    """Reads saved authors data resulting from the parsing step.

    It uses the `get_final_dedup` function of 
    the `bmfuncts.useful_functs` module.

    Args:
        bibliometer_path (path): Full path to working folder.
        saved_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The dataframe of the authors data.
    """
    # Setting useful aliases
    authors_item_alias = bp.PARSING_ITEMS_LIST[1]

    # Getting the dict of deduplication results
    dedup_parsing_dict = get_final_dedup(bibliometer_path,
                                         saved_results_path,
                                         corpus_year)

    # Getting ID of each author with author name
    authors_df = dedup_parsing_dict[authors_item_alias]
    return authors_df


def _set_useful_cols(institute, org_tup):
    """Sets the column names  useful for building authors analysis data.

    It uses 'build_col_conversion_dic' function imported from 
    'bmfuncts.rename_cols' module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
    Returns:
        (tup): (list of useful cols returned by 'build_col_conversion_dic' function \
        at seconde position of the returned tuple, list of cols to be added).
    """

    #  Setting useful col names alias
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    submit_col_rename_dic = col_rename_tup[1]
    pub_id_col_alias = submit_col_rename_dic[bp.COL_NAMES["pub_id"]]
    author_idx_col_alias = submit_col_rename_dic[bp.COL_NAMES["authors"][1]]
    inst_author_col_alias = submit_col_rename_dic[bp.COL_NAMES["authors"][2]]
    first_author_col_alias = submit_col_rename_dic[bp.COL_NAMES["articles"][1]]
    employee_col_alias = submit_col_rename_dic[eg.EMPLOYEES_ADD_COLS['employee_full_name']]
    nb_auth_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['author_nb']
    is_first_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['is_first_author']
    is_last_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['is_last_author']
    nb_pub_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['pub_nb']
    pub_list_col_alias = pg.COL_NAMES_BONUS['pub_ids list']

    # Building cols lists
    submit_useful_cols = [pub_id_col_alias, author_idx_col_alias,
                          inst_author_col_alias, first_author_col_alias,
                          employee_col_alias]
    add_cols = [nb_auth_col_alias, is_first_col_alias, is_last_col_alias,
                nb_pub_col_alias, pub_list_col_alias]

    return submit_useful_cols, add_cols


def _build_auth_nb_per_pub(bibliometer_path, saved_results_path,
                           corpus_year, cols_tup):
    """Builds the data of authors number per publications.

    It uses the `_read_authors_data` internal function to get 
    the authors data resulting from the parsing step.

    Args:
        bibliometer_path (path): Full path to working folder.
        saved_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
        cols_tup (tup): (Pub-ID column name, authors-number column name).
    Returns:
        (dataframe): The dataframe of the authors number per publications.
    """
    # Setting useful col list from args
    pub_id_col, nb_auth_col = cols_tup

    # Getting the authors per pub-ID file from parsing results
    authors_df = _read_authors_data(bibliometer_path, saved_results_path,
                                    corpus_year)

    # Creating a dataframe with a column with number of authors per pub-ID
    count_auth_df = pd.DataFrame()
    for _, pub_df in authors_df.groupby(pub_id_col):
        pub_count_auth_df = pub_df[pub_id_col].value_counts().to_frame()
        pub_count_auth_df = pub_count_auth_df.rename(columns={"count": nb_auth_col})
        pub_count_auth_df = pub_count_auth_df.reset_index()
        count_auth_df = concat_dfs([count_auth_df, pub_count_auth_df])

    count_auth_df = set_year_pub_id(count_auth_df, corpus_year, pub_id_col)
    return count_auth_df


def _build_author_employee_df(bibliometer_path, datatype,
                              corpus_year, all_cols_tup):
    """Builds data of authors per publication with corresponding employee name, 
    number of authors, author position in the authors list.

    The input data are as follows:
    - The publications list with one row per Institute author and its attributes 
    got through the `read_final_submit_data` internal function; this list has been 
    initially built through the `resursive_year_search` function of 
    the `bmfuncts.merge_pub_employees` module.
    - The number of authors per pub-ID got from the saved parsing results through 
    the `_build_auth_nb_per_pub` internal function.

    Args:
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        all_cols_tup (tup): (list of useful cols of the publications list \
        with one row per Institute author and its attributes, list of cols \
        to be added).
    Returns:
        (dataframe): The dataframe of the authors data per publications.
    """
    # Setting input-data path
    saved_results_path = set_saved_results_path(bibliometer_path, datatype)

    # Setting useful columns names
    submit_select_cols, add_cols_list = all_cols_tup
    pub_id_col = submit_select_cols[0]
    author_idx_col = submit_select_cols[1]
    inst_author_col = submit_select_cols[2]
    first_author_col = submit_select_cols[3]
    employee_col = submit_select_cols[4]
    nb_auth_col = add_cols_list[0]
    is_first_col = add_cols_list[1]
    is_last_col = add_cols_list[2]

    # Getting the publications list with one row per Institute author
    # and its attributes columns
    submit_df = read_final_submit_data(saved_results_path, corpus_year)

    # Getting the number of authors per pub-ID from parsing results
    select_cols_tup = (pub_id_col, nb_auth_col)
    count_auth_df = _build_auth_nb_per_pub(bibliometer_path, saved_results_path,
                                           corpus_year, select_cols_tup)

    # Initializing dataframe to build
    add_select_cols_list = [nb_auth_col, is_first_col, is_last_col]
    author_employee_df = pd.DataFrame(columns=submit_select_cols + add_select_cols_list)
    for col in submit_select_cols:
        author_employee_df[col] = submit_df[col].copy()
    author_employee_df[is_first_col] = 0
    author_employee_df[is_last_col] = 0

    for idx, row in author_employee_df.iterrows():
        # Setting useful values
        pub_id = row[pub_id_col]
        author_pos = row[author_idx_col] + 1
        authors_nb = count_auth_df[count_auth_df[pub_id_col]==pub_id][nb_auth_col][0]

        # Completing row
        author_employee_df.loc[idx, nb_auth_col] = authors_nb
        if author_pos==1:
            author_employee_df.loc[idx, is_first_col] = 1
        if author_pos==authors_nb:
            author_employee_df.loc[idx, is_last_col] = 1

    author_employee_df = author_employee_df.sort_values(by=[pub_id_col, author_idx_col],
                                                        axis=0)
    cols_order = [pub_id_col, nb_auth_col, author_idx_col, inst_author_col,
                  first_author_col, employee_col, is_first_col, is_last_col]
    author_employee_df = author_employee_df[cols_order]

    # Capitalize names
    author_employee_df[inst_author_col] = author_employee_df[inst_author_col].\
    apply(name_capwords)

    author_employee_df[employee_col] = author_employee_df[employee_col].\
    apply(name_capwords)

    return author_employee_df


def _build_pub_nb_per_author_df(author_employee_df, all_cols_tup):
    """Builds the data of publications number per author.

    Args:
        author_employee_df (dataframe): The dataframe of the authors \
        data per publications.
        all_cols_tup (tup): (list of useful cols of the excel file targetted \
        by 'in_path', list of cols to be added).
    Returns:
        (dataframe): The data of publications number per author.
    """
    # Setting useful columns names
    submit_select_cols, add_cols_list = all_cols_tup
    pub_id_col = submit_select_cols[0]
    inst_author_col = submit_select_cols[2]
    employee_col = submit_select_cols[4]
    nb_pub_col = add_cols_list[3]
    pub_list_col = add_cols_list[4]

    # Selecting useful columns in author_employee_df
    sub_author_employee_df = author_employee_df[[pub_id_col, employee_col, inst_author_col]].copy()

    # Initializing the dataframe to built with useful columns
    useful_cols_list = [employee_col, inst_author_col, nb_pub_col, pub_list_col]
    pub_nb_per_auth_df = pd.DataFrame(columns = useful_cols_list)

    # Building the targetted dataframe
    for _, empl_df in sub_author_employee_df.groupby(employee_col):
        pub_id_list = list(empl_df[pub_id_col])
        author_names_list = list(set(list(empl_df[inst_author_col])))
        author_names = author_names_list[0]
        if len(author_names_list)>1:
            author_names = "; ".join(author_names_list)
        empl_df[inst_author_col] = author_names
        empl_df[nb_pub_col] = len(pub_id_list)
        empl_df[pub_list_col] = "; ".join(pub_id_list)
        empl_df = empl_df[useful_cols_list]
        empl_df.drop_duplicates()
        pub_nb_per_auth_df = concat_dfs([pub_nb_per_auth_df, empl_df])
    pub_nb_per_auth_df = pub_nb_per_auth_df.drop_duplicates()

    return pub_nb_per_auth_df


def authors_analysis(institute, org_tup, bibliometer_path, datatype,
                     corpus_year, progress_callback=None):
    """Performs the analysis of authors data of the 'corpus_year' corpus.

    This is done through the following steps:

    1. Sets the column names  useful for building authors analysis data 
    trough the `_set_useful_cols` internal function.
    2. Builds data of authors per publication with corresponding employee name, 
    number of authors, author position in the authors list trough the 
    `_build_author_employee_df` internal function.
    3. Builds the data of publications number per author trough the 
    `_build_pub_nb_per_author_df` internal function.
    4. Saves the results of this analysis as openpyxl workbooks through the \
    `format_page` function imported from `bmfuncts.format_files` module.
    5. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    To Do: Updates database of key performance indicators (KPIs) of the Institute \
    with the results of this analysis through the `_update_kpi_database` internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (path): Full path to the folder where results of authors analysis \
        are saved.
    """
    # Setting useful aliases
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    auth_analysis_folder_alias = pg.ARCHI_YEAR["authors analysis"]
    authors_file_alias = pg.ARCHI_YEAR["authors file name"]
    authors_stat_file_alias = pg.ARCHI_YEAR["authors weight file name"]
    year_authors_file = authors_file_alias + " " + corpus_year
    year_authors_stat_file = authors_stat_file_alias + " " + corpus_year

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    auth_analysis_folder_path = analysis_folder_path / Path(auth_analysis_folder_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(auth_analysis_folder_path):
        os.makedirs(auth_analysis_folder_path)
    if progress_callback:
        progress_callback(10)

    useful_col_tup = _set_useful_cols(institute, org_tup)

    # Building author_employee_df
    author_employee_df = _build_author_employee_df(bibliometer_path, datatype,
                                                   corpus_year, useful_col_tup)
    if progress_callback:
        progress_callback(50)

    # Building pub_nb_per_author_df
    pub_nb_per_author_df = _build_pub_nb_per_author_df(author_employee_df, useful_col_tup)
    if progress_callback:
        progress_callback(60)

    # Saving the author-employee dataframe as EXCEL file
    author_employee_xlsx_file_path = Path(auth_analysis_folder_path) / Path(year_authors_file + ".xlsx")
    auth_df_title = pg.DF_TITLES_LIST[4]
    wb, ws = format_page(author_employee_df, auth_df_title)
    ws.title = 'Auteurs' + corpus_year
    wb.save(author_employee_xlsx_file_path)
    if progress_callback:
        progress_callback(70)

    # Saving the author-statistics dataframe as EXCEL file
    author_stat_xlsx_file_path = Path(auth_analysis_folder_path) / Path(year_authors_stat_file + ".xlsx")
    auth_stat_df_title = pg.DF_TITLES_LIST[5]
    wb, ws = format_page(pub_nb_per_author_df, auth_stat_df_title)
    ws.title = 'Auteurs' + corpus_year
    wb.save(author_stat_xlsx_file_path)
    if progress_callback:
        progress_callback(80)

    # Saving authors analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["authors"] = True
    if_analysis_name = None
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype, corpus_year,
                           if_analysis_name, results_to_save_dict, verbose=False)
    if progress_callback:
        progress_callback(100)

    return auth_analysis_folder_path
