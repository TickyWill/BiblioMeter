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
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_user_config
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.save_final_results import save_final_results
from bmfuncts.useful_functs import format_df_for_excel
from bmfuncts.useful_functs import read_parsing_dict


def _read_authors_df(parsing_path_dict, item_filename_dict):
    """Reads authors data resulting from the parsing step.

    It uses the `read_parsing_dict` function of 
    the `bmfuncts.useful_functs` module.

    Args:
        parsing_path_dict (dict): The dict keyyed by the parsing steps \
        and valued by the full path to the folder of the corresponding \
        parsing results.
        item_filename_dict (dict): The dict keyyed by the parsing items \
        and valued by the corresponding file name.
    Returns:
        (dataframe): The dataframe of the authors data.
    """

    # Setting useful aliases
    authors_item_alias = bp.PARSING_ITEMS_LIST[1]

    # Setting parsing files extension of saved results
    parsing_save_extent = pg.TSV_SAVE_EXTENT

    # Setting path of deduplicated parsings
    dedup_parsing_path = parsing_path_dict['dedup']

    # Getting the dict of deduplication results
    dedup_parsing_dict = read_parsing_dict(dedup_parsing_path, item_filename_dict,
                                           parsing_save_extent)

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
    _, submit_col_rename_dic, _ = build_col_conversion_dic(institute, org_tup)
    submit_col_list = list(submit_col_rename_dic.values())
    pub_id_col_alias = submit_col_list[0]
    author_idx_col_alias = submit_col_list[1]
    inst_author_col_alias = submit_col_list[7]
    first_author_col_alias = submit_col_list[8]
    employee_col_alias = submit_col_list[44]
    nb_auth_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['author_nb']
    is_first_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['is_first_author']
    is_last_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['is_last_author']
    nb_pub_col_alias = pg.COL_NAMES_AUTHOR_ANALYSIS['pub_nb']
    pub_list_col_alias = pg.COL_NAMES_BONUS['pub_ids list']
    submit_useful_cols = [pub_id_col_alias, author_idx_col_alias,
                          inst_author_col_alias, first_author_col_alias,
                          employee_col_alias]
    add_cols = [nb_auth_col_alias, is_first_col_alias, is_last_col_alias,
                nb_pub_col_alias, pub_list_col_alias]
    return submit_useful_cols, add_cols


def _set_year_pub_id(df, year, pub_id_col):
    """Transforms the pub-ID column of df by adding "yyyy_" 
    (year in 4 digits) to the values.

    Args:
        df (pandas.DataFrame): The data we want to modify.
        year (str): The 4 digits year to add as "yyyy".
        pub_id_col (str): The name of the pub-ID column to transform.
    Returns:
        (pandas.DataFrame): The data with its changed column.
    """

    def _rename_pub_id(old_pub_id, year):
        pub_id_str = str(int(old_pub_id))
        while len(pub_id_str)<3:
            pub_id_str = "0" + pub_id_str
        new_pub_id = str(int(year)) + '_' + pub_id_str
        return new_pub_id

    df[pub_id_col] = df[pub_id_col].apply(lambda x: _rename_pub_id(x, year))
    return df


def _build_auth_nb_per_pub(bibliometer_path, corpus_year, cols_tup):
    """Builds the data of authors number per publications.

    It uses the `_read_authors_df` internal function to get 
    the authors data resulting from the parsing step.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        cols_tup (tup): (Pub-ID column name, authors-number column name).
    Returns:
        (dataframe): The dataframe of the authors number per publications.
    """
    # Setting useful col list from args
    pub_id_col, nb_auth_col = cols_tup

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, corpus_year, pg.BDD_LIST)
    parsing_path_dict, item_filename_dict = config_tup[1], config_tup[2]

    # Getting the authors per pub-ID file from parsing results
    authors_df = _read_authors_df(parsing_path_dict, item_filename_dict)

    # Creating a dataframe with a column with number of authors per pub-ID
    count_auth_df = pd.DataFrame()
    for pub_id, pub_df in authors_df.groupby(pub_id_col):
        pub_count_auth_df = pub_df[pub_id_col].value_counts().to_frame()
        pub_count_auth_df.rename(columns={"count": nb_auth_col}, inplace=True)
        pub_count_auth_df.reset_index(inplace=True)
        count_auth_df = pd.concat([count_auth_df, pub_count_auth_df], axis=0)

    _set_year_pub_id(count_auth_df, corpus_year, pub_id_col)
    return count_auth_df


def _build_author_employee_df(bibliometer_path, in_path, corpus_year, all_cols_tup):
    """Builds data of authors per publication with corresponding employee name, 
    number of authors, author position in the authors list.

    It uses the `_build_auth_nb_per_pub` internal function.

    Args:
        in_path (path): Fullpath of the excel file of the publications list \
        with a row per Institute author and their attributes columns.
        corpus_year (str): 4 digits year of the corpus.
        all_cols_tup (tup): (list of useful cols of the excel file targetted \
        by 'in_path', list of cols to be added).
    Returns:
        (dataframe): The dataframe of the authors data per publications.
    """

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

    # Getting the number of authors per pub-ID from parsing results
    select_cols_tup = (pub_id_col, nb_auth_col)
    count_auth_df = _build_auth_nb_per_pub(bibliometer_path, corpus_year, select_cols_tup)

    # Reading the submit file
    submit_df = pd.read_excel(in_path)

    # Initializing dataframe to build
    add_select_cols_list = [nb_auth_col, is_first_col, is_last_col]
    author_employee_df = pd.DataFrame(columns = submit_select_cols + add_select_cols_list)
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

    author_employee_df.sort_values(by=[pub_id_col, author_idx_col], axis=0, inplace=True)
    cols_order = [pub_id_col, nb_auth_col, author_idx_col, inst_author_col, first_author_col,
                  employee_col, is_first_col, is_last_col]
    author_employee_df = author_employee_df[cols_order]

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
    first_author_col = submit_select_cols[3]
    employee_col = submit_select_cols[4]
    nb_pub_col = add_cols_list[3]
    pub_list_col = add_cols_list[4]

    # Selecting useful columns in author_employee_df
    sub_author_employee_df = author_employee_df[[pub_id_col, employee_col, inst_author_col]].copy()

    # Initializing the dataframe to built with useful columns
    useful_cols_list = [employee_col, inst_author_col, nb_pub_col, pub_list_col]
    pub_nb_per_auth_df = pd.DataFrame(columns = useful_cols_list)

    # Building the targetted dataframe
    for empl, empl_df in sub_author_employee_df.groupby(employee_col):
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
        pub_nb_per_auth_df = pd.concat([pub_nb_per_auth_df, empl_df])
    pub_nb_per_auth_df.drop_duplicates(inplace=True)
    return pub_nb_per_auth_df


def authors_analysis(institute, org_tup, bibliometer_path, datatype,
                     corpus_year, progress_callback=None, verbose=False):
    """ Performs the analysis of authors data of the 'corpus_year' corpus.

    This is done through the following steps:

    1. Sets the column names  useful for building authors analysis data 
    trough the `_set_useful_cols` internal function.
    2. Builds data of authors per publication with corresponding employee name, 
    number of authors, author position in the authors list trough the 
    `_build_author_employee_df` internal function.
    3. Builds the data of publications number per author trough the 
    `_build_pub_nb_per_author_df` internal function.
    4. Saves the results of this analysis for the 'datatype' case through the \
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
        verbose (bool): Status of prints (default = False).
    Returns:
        (path): Full path to the folder where results of authors analysis \
        are saved.
    """
    # Setting useful aliases
    submit_alias = pg.ARCHI_YEAR["submit file name"]
    bdd_mensuelle_alias = pg.ARCHI_YEAR["bdd mensuelle"]
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    auth_analysis_folder_alias = pg.ARCHI_YEAR["authors analysis"]
    authors_file_alias = pg.ARCHI_YEAR["authors file name"]
    authors_stat_file_alias = pg.ARCHI_YEAR["authors weight file name"]
    year_authors_file = authors_file_alias + " " + corpus_year
    year_authors_stat_file = authors_stat_file_alias + " " + corpus_year

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(corpus_year)
    bdd_mensuelle_path = year_folder_path / Path(bdd_mensuelle_alias)
    submit_path = bdd_mensuelle_path / Path(submit_alias)
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
    author_employee_df = _build_author_employee_df(bibliometer_path, submit_path,
                                                   corpus_year, useful_col_tup)
    if progress_callback:
        progress_callback(50)

    # Building pub_nb_per_author_df
    pub_nb_per_author_df = _build_pub_nb_per_author_df(author_employee_df, useful_col_tup)
    if progress_callback:
        progress_callback(60)

    # Saving the keywords dataframe as EXCEL file
    author_employee_xlsx_file_path = Path(auth_analysis_folder_path) / Path(year_authors_file + ".xlsx")
    col_names = list(author_employee_df.columns)
    col_attr_dict = {col_names[0]: [12, "center"],
                     col_names[1]: [12, "center"],
                     col_names[2]: [12, "center"],
                     col_names[3]: [30, "left"],
                     col_names[4]: [30, "left"],
                     col_names[5]: [30, "left"],
                     col_names[6]: [15, "center"],
                     col_names[7]: [15, "center"],
                    }
    wb, ws = format_df_for_excel(author_employee_df, col_attr_dict=col_attr_dict)
    ws.title = 'Auteurs' + corpus_year
    wb.save(author_employee_xlsx_file_path)
    if progress_callback:
        progress_callback(70)

    # Saving the keywords dataframe as EXCEL file
    author_stat_xlsx_file_path = Path(auth_analysis_folder_path) / Path(year_authors_stat_file + ".xlsx")
    col_names = list(pub_nb_per_author_df.columns)
    col_attr_dict = {col_names[0]: [30, "left"],
                     col_names[1]: [30, "left"],
                     col_names[2]: [15, "center"],
                     col_names[3]: [95, "left"],
                    }
    wb, ws = format_df_for_excel(pub_nb_per_author_df, col_attr_dict=col_attr_dict)
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
