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
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import format_page
from bmfuncts.read_final_results import keep_only_final_pub_data
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.read_final_results import read_final_set_homonyms_data
from bmfuncts.rename_cols import set_homonym_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import name_capwords
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import set_year_pub_id


def _read_authors_data(wf_path, final_results_path,
                       corpus_year):
    """Reads saved authors data resulting from the parsing step.

    It uses the `read_final_dedup` function of 
    the `bmfuncts.useful_functs` module.

    Args:
        wf_path (path): Full path to working folder.
        final_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The dataframe of the authors' data.
    """
    # Setting useful aliases
    authors_item_alias = bp.PARSING_ITEMS_LIST[1]

    # Getting the dict of deduplication results
    dedup_parsing_dict = read_final_dedup(wf_path,
                                          final_results_path,
                                          corpus_year)

    # Getting ID of each author with author name
    authors_df = dedup_parsing_dict[authors_item_alias]
    return authors_df


def _set_au_analysis_cols(institute, org_tup):
    """Builds a dict setting selected columns names for the process 
    of building authors analysis data.

    This is done through the `set_homonym_col_names` function imported from the 
    `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains parameters of Institute organization.
    Returns:
        (dict): The built dict.
    """
    # Setting useful column names from homonyms file
    homonyms_col_dic = set_homonym_col_names(institute, org_tup)

    au_analysis_cols_dic = {'pub_id_col'       : homonyms_col_dic['pub_id'],
                            'au_id_col'        : homonyms_col_dic['author_id'],
                            'inst_au_col'      : homonyms_col_dic['inst_author'],
                            'first_au_col'     : homonyms_col_dic['first_author'],
                            'mat_col'          : homonyms_col_dic['matricul'],
                            'type_col'         : homonyms_col_dic['author_type'],
                            'empl_col'         : homonyms_col_dic['empl_full_name'],
                            'doctype_col'      : homonyms_col_dic['doc_type'],
                            'nb_au_col'        : bm_pg.COL_NAMES_AUTHOR_ANALYSIS['author_nb'],
                            'is_first_col'     : bm_pg.COL_NAMES_AUTHOR_ANALYSIS['is_first_author'],
                            'is_last_col'      : bm_pg.COL_NAMES_AUTHOR_ANALYSIS['is_last_author'],
                            'nb_pub_col'       : bm_pg.COL_NAMES_AUTHOR_ANALYSIS['pub_nb'],
                            'pub_list_col'     : bm_pg.COL_NAMES_BONUS['pub_ids list'],
                            'final_inst_au_col': bm_pg.COL_NAMES_BONUS['name_as_auth'],
                            'final_empl_col'   : bm_pg.COL_NAMES_BONUS['name_as_empl'],
                           }

    return au_analysis_cols_dic


def _build_auth_nb_per_pub(wf_path, final_results_path,
                           corpus_year, cols_list):
    """Builds the data of authors number per publications.

    It uses the `_read_authors_data` internal function to get 
    the authors data resulting from the parsing step.

    Args:
        wf_path (path): Full path to working folder.
        final_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
        cols_list (list):  Composed of Pub-ID column name (str) and \
        of authors-number column name (str).
    Returns:
        (dataframe): The dataframe of the authors number per publications.
    """
    # Setting useful col list from args
    pub_id_col, nb_au_col = cols_list

    # Getting the authors per pub-ID file from parsing results
    authors_df = _read_authors_data(wf_path, final_results_path,
                                    corpus_year)

    # Creating a dataframe with a column with number of authors per pub-ID
    count_auth_df = pd.DataFrame()
    for _, pub_df in authors_df.groupby(pub_id_col):
        pub_count_auth_df = pub_df[pub_id_col].value_counts().to_frame()
        pub_count_auth_df = pub_count_auth_df.rename(columns={"count": nb_au_col})
        pub_count_auth_df = pub_count_auth_df.reset_index()
        count_auth_df = concat_dfs([count_auth_df, pub_count_auth_df])

    count_auth_df = set_year_pub_id(count_auth_df, corpus_year, pub_id_col)
    return count_auth_df


def _build_author_employee_df(sub_params_list, au_analysis_cols_dic):
    """Builds data of authors per publication with corresponding employee name, 
    number of authors, author position in the authors list.

    The input data are as follows:
    - The publications list with one row per Institute author and its attributes 
    got through the `read_final_set_homonyms_data` internal function; this list 
    has been initially built through the `set_saved_homonyms` 
    function of the `bmfuncts.use_homonyms` module.
    - The number of authors per pub-ID got from the saved parsing results through 
    the `_build_auth_nb_per_pub` internal function.

    Args:
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        au_analysis_cols_dic (dict): The dict giving the columns names for the \
        process of building authors analysis data.
    Returns:
        (dataframe): The dataframe of the authors data per publications.
    """
    wf_path, datatype, print_params, corpus_year = sub_params_list
    # Setting input-data path
    final_results_path = set_results_folder_path(wf_path, datatype)

    # Setting useful columns names from 'au_analysis_cols_dic'
    col_keys = ['pub_id_col', 'au_id_col', 'inst_au_col', 'first_au_col',
                'mat_col', 'type_col', 'empl_col', 'nb_au_col',
                'is_first_col', 'is_last_col', 'doctype_col']
    au_empl_cols = [au_analysis_cols_dic[key] for key in col_keys]
    homonyms_select_cols = au_empl_cols[0:7]
    (pub_id_col, au_id_col, inst_au_col, first_au_col, mat_col, type_col, empl_col,
     nb_au_col, is_first_col, is_last_col, doctype_col) = au_empl_cols

    # Getting the number of authors per pub-ID from parsing results
    print("  - Computing the number of authors per publication from parsing results...", end="\r")
    count_select_cols = [pub_id_col, nb_au_col]
    count_auth_df = _build_auth_nb_per_pub(wf_path, final_results_path,
                                           corpus_year, count_select_cols)
    print_step_text("  - Data of number of authors per publication built from parsing results       ",
                    print_params)

    # Getting the publications list with one row per Institute author
    # and its attributes columns
    print("  - Get the final results of homonyms resolution...", end="\r")
    all_pub_authors_df = read_final_set_homonyms_data(final_results_path, corpus_year)
    print_step_text("  - Employees data of Institute's authors set from homonyms-resolution results    ",
                    print_params)

    # Selecting only data related to the consolidated publications list
    cols_list = [pub_id_col, doctype_col]
    kept_pub_authors_df = keep_only_final_pub_data(all_pub_authors_df, final_results_path,
                                                   corpus_year, cols_list)

    # Initializing dataframe to build
    print("  - Enhancing data of Institute's authors per publication...", end="\r")
    author_employee_df = pd.DataFrame(columns=au_empl_cols)
    for col in homonyms_select_cols:
        author_employee_df[col] = kept_pub_authors_df[col].copy()

    # Initializing new columns values
    author_employee_df[nb_au_col] = 0
    author_employee_df[is_first_col] = 0
    author_employee_df[is_last_col] = 0
    for idx, row in author_employee_df.iterrows():
        # Setting useful values
        pub_id = row[pub_id_col]
        author_pos = int(row[au_id_col]) + 1
        authors_nb = int(count_auth_df[count_auth_df[pub_id_col]==pub_id][nb_au_col][0])

        # Completing row
        author_employee_df.loc[idx, nb_au_col] = authors_nb
        if author_pos==1:
            author_employee_df.loc[idx, is_first_col] = 1
        if author_pos==authors_nb:
            author_employee_df.loc[idx, is_last_col] = 1

    author_employee_df = author_employee_df.sort_values(by=[pub_id_col, au_id_col],
                                                        axis=0)
    cols_order = [pub_id_col, nb_au_col, au_id_col, inst_au_col,
                  first_au_col, empl_col, mat_col, type_col, is_first_col, is_last_col]
    author_employee_df = author_employee_df[cols_order]

    # Capitalize names
    author_employee_df[inst_au_col] = author_employee_df[inst_au_col].apply(name_capwords)
    author_employee_df[empl_col] = author_employee_df[empl_col].apply(name_capwords)
    print_step_text("  - Institute's authors data per publication enhanced       ", print_params)
    return author_employee_df


def _build_pub_nb_per_author_df(author_employee_df, au_analysis_cols_dic, print_params):
    """Builds the data of publications number per author.

    Args:
        author_employee_df (dataframe): The dataframe of the authors \
        data per publications.
        au_analysis_cols_dic (dict): The dict giving the columns names for the \
        process of building authors analysis data.
    Returns:
        (dataframe): The data of publications number per author.
    """
    # Setting useful columns names from 'au_analysis_cols_dic'
    col_keys = ['pub_id_col', 'inst_au_col', 'mat_col', 'type_col',
                'empl_col', 'nb_pub_col', 'pub_list_col']
    au_pub_cols = [au_analysis_cols_dic[key] for key in col_keys]
    (pub_id_col, inst_au_col, mat_col, type_col,
     empl_col, nb_pub_col, pub_list_col) = au_pub_cols

    # Selecting useful columns in author_employee_df
    sub_au_empl_cols = [pub_id_col, empl_col, mat_col,
                        type_col, inst_au_col]
    sub_author_employee_df = author_employee_df[sub_au_empl_cols].copy()

    # Initializing the dataframe to built with useful columns
    au_pub_select_cols = [mat_col, type_col, empl_col,
                          inst_au_col, nb_pub_col, pub_list_col]
    pub_nb_per_auth_df = pd.DataFrame(columns = au_pub_select_cols)

    # Building the targeted dataframe
    print("  - Building the data of publications number per Institute's author...", end="\r")
    for _, empl_df in sub_author_employee_df.groupby(empl_col):
        pub_id_list = list(empl_df[pub_id_col])
        author_names_list = list(set(list(empl_df[inst_au_col])))
        author_names = author_names_list[0]
        if len(author_names_list)>1:
            author_names = "; ".join(author_names_list)
        empl_df[inst_au_col] = author_names
        empl_df[nb_pub_col] = len(pub_id_list)
        empl_df[pub_list_col] = "; ".join(pub_id_list)
        empl_df = empl_df[au_pub_select_cols]
        empl_df.drop_duplicates()
        pub_nb_per_auth_df = concat_dfs([pub_nb_per_auth_df, empl_df])
    pub_nb_per_auth_df = pub_nb_per_auth_df.drop_duplicates()

    # Renaming cols
    rename_dic = {empl_col   : au_analysis_cols_dic['final_empl_col'],
                  inst_au_col: au_analysis_cols_dic['final_inst_au_col']}
    author_employee_df = author_employee_df.rename(columns=rename_dic)
    pub_nb_per_auth_df = pub_nb_per_auth_df.rename(columns=rename_dic)
    print_step_text("  - Data of publications number per Institute's author built          ",
                    print_params)

    return author_employee_df, pub_nb_per_auth_df


def _set_au_files_params(wf_path, corpus_year):
    """Sets authors analysis specific files and folder paths. 

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): publications-lists folder name, \
        base for building names of publications-list files, \
        base for building names of missing-IFs files, \
        name for building names of missing-ISSNs files.
    """
    # Setting useful aliases
    analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    au_analysis_folder_alias = bm_pg.ARCHI_YEAR["authors analysis"]
    au_file_alias = bm_pg.ARCHI_YEAR["authors file name"]
    au_stat_file_alias = bm_pg.ARCHI_YEAR["authors weight file name"]

    # Setting useful files names
    year_au_file = au_file_alias + " " + corpus_year + ".xlsx"
    year_au_stat_file = au_stat_file_alias + " " + corpus_year + ".xlsx"

    # Setting useful paths
    year_folder_path = wf_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    au_analysis_folder_path = analysis_folder_path / Path(au_analysis_folder_alias)
    au_empl_xlsx_file_path = Path(au_analysis_folder_path) / Path(year_au_file)
    au_stat_xlsx_file_path = Path(au_analysis_folder_path) / Path(year_au_stat_file)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(au_analysis_folder_path):
        os.makedirs(au_analysis_folder_path)

    return au_analysis_folder_path, au_empl_xlsx_file_path, au_stat_xlsx_file_path


def authors_analysis(params_list, progress_callback=None):
    """Performs the analysis of authors data of the 'corpus_year' corpus.

    This is done through the following steps:

    1. Sets the column names  useful for building authors analysis data 
    through the `_set_useful_cols` internal function.
    2. Builds data of authors per publication with corresponding employee name, 
    number of authors, author position in the authors list through the 
    `_build_author_employee_df` internal function.
    3. Builds the data of publications number per author through the 
    `_build_pub_nb_per_author_df` internal function.
    4. Saves the results of this analysis as openpyxl workbooks through the \
    `format_page` function imported from `bmfuncts.format_files` module.
    5. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    To Do: Updates database of key performance indicators (KPIs) of the Institute \
    with the results of this analysis through the `_update_kpi_database` internal function.

    Args:
        params_list (list): The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path), the data combination type \
        of corpuses databases (str) and the 4 digits year of the corpus (str).
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (path): Full path to the folder where results of authors analysis \
        are saved.
    """
    # Setting parameters values from params_list
    institute, org_tup, wf_path, datatype, print_params, corpus_year = params_list
    sub_params_list = [wf_path, datatype, print_params, corpus_year]

    # Setting useful paths
    return_tup = _set_au_files_params(wf_path, corpus_year)
    (au_analysis_folder_path, au_empl_xlsx_file_path,
     au_stat_xlsx_file_path) = return_tup
    if progress_callback:
        progress_callback(10)

    # Setting dict giving column names
    au_analysis_cols_dic = _set_au_analysis_cols(institute, org_tup)

    # Building author_employee_df
    print_step_text("\nBuilding enhanced data of Institute's authors per publication...", print_params)
    author_employee_df = _build_author_employee_df(sub_params_list, au_analysis_cols_dic)
    if progress_callback:
        progress_callback(50)

    # Building pub_nb_per_author_df
    print_step_text("\nBuilding statistics data per Institute's author...", print_params)
    return_tup = _build_pub_nb_per_author_df(author_employee_df, au_analysis_cols_dic, print_params)
    author_employee_df, pub_nb_per_author_df = return_tup
    if progress_callback:
        progress_callback(60)

    print_step_text("\nSaving author's scientific production data...", print_params)
    # Saving the author-employee dataframe as formatted EXCEL file
    auth_df_title = bm_pg.DF_TITLES_LIST[4]
    wb, ws = format_page(author_employee_df, auth_df_title)
    ws.title = 'Auteurs ' + corpus_year
    wb.save(au_empl_xlsx_file_path)
    if progress_callback:
        progress_callback(70)

    # Saving the author-statistics dataframe as formatted EXCEL file
    auth_stat_df_title = bm_pg.DF_TITLES_LIST[5]
    wb, ws = format_page(pub_nb_per_author_df, auth_stat_df_title)
    ws.title = 'Stat auteurs ' + corpus_year
    wb.save(au_stat_xlsx_file_path)
    if progress_callback:
        progress_callback(80)

    # Saving authors analysis as final result
    status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["authors"] = True
    _ = save_final_results(params_list, results_to_save_dict)
    if progress_callback:
        progress_callback(100)

    print_step_text("  - Data saved as final results", print_params)
    return au_analysis_folder_path
