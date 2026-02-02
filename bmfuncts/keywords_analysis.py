"""Module of functions for publications-list analysis
in terms of keywords.

"""

__all__ = ['keywords_analysis']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import format_page
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.read_final_results import read_final_pub_list_data
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.save_final_results import set_results_folder_path


def _create_kw_analysis_data(institute, corpus_year, analysis_df, kw_type, kw_df, cols_tup,
                             kw_analysis_folder_path, verbose=False):
    """Creates publications-keywords (KW) data for the 'kw_type' KW type 
    for each department of the Institute including itself.

    This is done through the following steps:

    1. Builds the list of publication IDs of the department \
    extracted from the 'analysis_df' dataframe;
    2. Builds the list of KWs for the 'kw_type' KW type extracted \
    from the 'kw_df' dataframe using the built list of publication IDs \
    of the department;
    3. Builds the 'dept_kw_df' dataframe by computing the number \
    of occurrences of each KW in the built list of KWs;
    4. Saves the 'dept_kw_df' dataframe as openpyxl workbook using the \
    `format_page` function imported from the `bmfuncts.format_files` \
    module.

    Args:
        institute (str): Institute name.
        corpus_year (str): 4 digits year of the corpus.
        analysis_df (dataframe): Publications list to be analyzed.
        kw_type (str): Type of keyword to be analyzed.
        kw_df (dataframe): Keywords list of 'kw_type' type to be analyzed.
        cols_tup (tup): Tuple = (list of column name for each department of the Institute, \
        publication-IDs column name in 'analysis_df' dataframe, \
        publication-IDs column name in 'kw_df' dataframe, \
        keywords column name, keyword-weight column name).
        kw_analysis_folder_path (path): Full path to the folder for saving results.
        verbose (bool): Status of prints (default = False).
    """

    # Setting useful column names aliases
    depts_col_list, final_pub_id_col, parsing_pub_id_col, keywords_col, weight_col = cols_tup

    # Analyzing the keywords for each of the department in 'depts_col_list'
    for dept in [institute] + depts_col_list:
        # Collecting and normalizing all the Pub_ids of the department 'dept'
        # by removing the 4 first characters corresponding to the corpus year
        # in order to make them comparable to 'parsing_pub_id_col' values
        if dept != institute:
            raw_pub_id_list = analysis_df[analysis_df[dept] == 1][final_pub_id_col].tolist()
            dept_pub_id_list = [int(x[5:8]) for x in raw_pub_id_list]
        else:
            dept_pub_id_list = [int(x[5:8]) for x in analysis_df[final_pub_id_col].tolist()]

        # Building the list of keywords for the keywords type 'kw_type' and the department 'dept'
        dept_kw_list = []
        for _, row in kw_df.iterrows():
            pub_id = row[parsing_pub_id_col]
            keyword = row[keywords_col]
            if pub_id in dept_pub_id_list:
                pub_kw_list = [word.strip() for word in keyword.split(";")]
                dept_kw_list = dept_kw_list + pub_kw_list

        # Building a dataframe with the keywords and their weight for the keywords type 'kw_type'
        # and the department 'dept'
        dept_kw_df = pd.DataFrame(columns=[keywords_col, weight_col])
        dept_kw_set_to_list = sorted(list(set(dept_kw_list)))
        kw_drop = 0
        for idx, keyword in enumerate(dept_kw_set_to_list):
            if len(keyword) > 1:
                dept_kw_df.loc[idx, keywords_col] = keyword
                dept_kw_df.loc[idx, weight_col] = dept_kw_list.count(keyword)
            else:
                kw_drop += 1
        if kw_drop and dept == institute:
            print(f"    WARNING: {kw_drop} dropped keywords of 1 character "
                  f"among {len(dept_kw_set_to_list)} {kw_type} ones of {institute}")

        # Saving the keywords dataframe as EXCEL file
        dept_xlsx_file_path = Path(kw_analysis_folder_path) / Path(f'{dept} {corpus_year}-{kw_type}.xlsx')
        kw_df_title = bm_pg.DF_TITLES_LIST[7]
        wb, ws = format_page(dept_kw_df, kw_df_title)
        ws.title = dept + ' ' + kw_type
        wb.save(dept_xlsx_file_path)

    message = ("\n    Keywords of all types and all departments "
               f"saved in : \n {kw_analysis_folder_path}")
    if verbose:
        print(message, "\n")


def _get_clean_kw_data(kw_df, keywords_col):
    """Building the keywords data from 'dedup_parsing_dict' dict 
    at 'kw_item' key.

    Args:
        kw_df (dataframe): The data of keywords to be cleaned.
        keywords_col (str): The column name where data are cleaned.
    Returns:
        (dataframe): The cleaned data.
    """
    kw_df[keywords_col] = kw_df[keywords_col]. \
        apply(lambda x: x.replace(' ', '_').replace('-', '_'))
    kw_df[keywords_col] = kw_df[keywords_col]. \
        apply(lambda x: x.replace('_(', ';').replace(')', ''))
    kw_df[keywords_col] = kw_df[keywords_col].apply(lambda x: x.lower())
    return kw_df


def _set_kw_files_params(wf_path, corpus_year):
    """Sets IFs specific file and folder 
    
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
    auth_kw_item_alias = bp.PARSING_ITEMS_LIST[6]
    index_kw_item_alias = bp.PARSING_ITEMS_LIST[7]
    title_kw_item_alias = bp.PARSING_ITEMS_LIST[8]
    analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    kw_analysis_folder_alias = bm_pg.ARCHI_YEAR["keywords analysis"]

    # Setting useful filenames dict
    kw_items_dict = {'AK': auth_kw_item_alias,
                     'IK': index_kw_item_alias,
                     'TK': title_kw_item_alias,
                    }

    # Setting output-data paths
    year_folder_path = wf_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    kw_analysis_folder_path = analysis_folder_path / Path(kw_analysis_folder_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(kw_analysis_folder_path):
        os.makedirs(kw_analysis_folder_path)

    return kw_items_dict, kw_analysis_folder_path


def keywords_analysis(params_list, progress_callback=None, verbose=False):
    """ Performs the analysis of publications keywords (KWs) of the corpus.

    This is done through the following steps:

    1. Gets deduplication results of the parsing step through the \
    `read_final_dedup` function imported from `bmfuncts.read_final_results` module.
    2. Builds the dataframe of publications list to be analyzed specifying \
    the useful columns;
    3. Loops on KW type among author KW (AK), indexed KW (IK) and title KW (TK) for:

        1. building the dataframe of KW list to be analyzed given by the deduplication \
        results of the parsing step;
        2. creating KW analysis data through the `_create_kw_analysis_data` internal function;

    4. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        params_list (list):  The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path), the data combination type \
        of corpuses databases (str) and the 4 digits year of the corpus (str).
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).
    Returns:
        (path): Full path to the folder where results of keywords analysis are saved.
    """
    # Setting parameters values from params_list
    institute, org_tup, wf_path, datatype, _, corpus_year = params_list

    # Setting input-data path
    final_results_path = set_results_folder_path(wf_path, datatype)

    # Setting useful files params
    kw_items_dict, kw_analysis_folder_path = _set_kw_files_params(wf_path, corpus_year)
    if progress_callback:
        progress_callback(10)

    # Setting useful column names aliases
    parsing_pub_id_col_alias = bp.COL_NAMES['pub_id']
    keywords_col_alias = bp.COL_NAMES['keywords'][1]
    weight_col_alias = bm_pg.COL_NAMES_BONUS['weight']

    # Setting useful column names
    final_col_dic, depts_col_list = set_final_col_names(institute, org_tup)
    final_pub_id_col = final_col_dic['pub_id']
    if progress_callback:
        progress_callback(15)

    # Getting the dict of deduplication results
    dedup_parsing_dict = read_final_dedup(wf_path, final_results_path, corpus_year)
    if progress_callback:
        progress_callback(25)

    # Building the dataframe to be analyzed
    cols_list = [final_pub_id_col] + depts_col_list
    pub_df = read_final_pub_list_data(final_results_path,
                                      corpus_year, cols_list)
    if progress_callback:
        progress_callback(30)

    # Plotting the words-cloud of the different kinds of keywords
    progress_bar_state, progress_bar_loop_progression = [None] * 2
    if progress_callback:
        progress_bar_state = 30
        progress_bar_loop_progression = 50 // len(kw_items_dict.keys())
    for kw_type, kw_item in kw_items_dict.items():
        # Building the keywords dataframe for the keywords type 'kw_type'
        # from 'dedup_parsing_dict' dict at 'kw_item' key
        init_kw_df = dedup_parsing_dict[kw_item]
        kw_df = _get_clean_kw_data(init_kw_df, keywords_col_alias)

        # Creating keywords-analysis data and saving them as xlsx files
        cols_tup = (depts_col_list, final_pub_id_col, parsing_pub_id_col_alias,
                    keywords_col_alias, weight_col_alias)
        _create_kw_analysis_data(institute, corpus_year, pub_df, kw_type, kw_df, cols_tup,
                                 kw_analysis_folder_path, verbose=verbose)

        # Updating progress bar state
        if progress_callback:
            progress_bar_state += progress_bar_loop_progression
            progress_callback(progress_bar_state)

    # Saving keywords analysis as final result
    status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["kws"] = True
    _ = save_final_results(params_list, results_to_save_dict)
    if progress_callback:
        progress_callback(100)
    return kw_analysis_folder_path
