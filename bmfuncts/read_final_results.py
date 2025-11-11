"""Module of useful functions for getting final results.
"""

__all__ = ['build_pub_ids_lists',
           'read_final_dedup',
           'read_final_pub_list_data',
           'read_final_set_homonyms_data',
           'read_final_submit_data',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import pandas as pd

# local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.config_utils import set_user_config
from bmfuncts.useful_functs import read_parsing_dict
from bmfuncts.useful_functs import set_capwords_lambda


def read_final_dedup(wf_path, final_results_path, corpus_year):
    """Reads saved final-parsing data as dict resulting from the parsing step.

    It uses the `read_parsing_dict` function of 
    the `bmfuncts.useful_functs` module.

    Args:
        wf_path (path): Full path to working folder.
        final_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dict): Parsing results keyed by parsing items (str) and valued \
        by data (dataframe) of the parsing item.
    """
    # Setting useful aliases
    parsing_save_extent_alias = bm_pg.TSV_SAVE_EXTENT
    saved_dedup_parsing_folder_alias = bm_pg.ARCHI_RESULTS["dedup_parsing"]

    # Getting the item-filename dict of the user for getting deduplication results
    config_tup = set_user_config(wf_path, corpus_year, bm_pg.BDD_LIST)
    item_filename_dict = config_tup[2]

    # Setting path of deduplicated parsings
    year_final_results_path = final_results_path / Path(corpus_year)
    saved_dedup_parsing_path = year_final_results_path / Path(saved_dedup_parsing_folder_alias)

    # Getting the dict of deduplication results
    dedup_parsing_dict = read_parsing_dict(saved_dedup_parsing_path, item_filename_dict,
                                           parsing_save_extent_alias)
    return dedup_parsing_dict


def read_final_submit_data(final_results_path, corpus_year):
    """Reads saved publications list with one row per Institute author 
    and its attributes.
    
    This data have been initially built through the `recursive_year_search` 
    function of the `bmfuncts.merge_pub_employees` module.

    Args:
        final_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The resulting dataframe from the read.
    """

    # Setting useful aliases
    saved_submit_folder_alias = bm_pg.ARCHI_RESULTS["submit"]
    saved_submit_file_base_alias = bm_pg.ARCHI_YEAR["submit file name"]
    year_submit_filename = corpus_year + " " + saved_submit_file_base_alias

    # Setting useful paths
    year_final_results_path = final_results_path / Path(corpus_year)
    saved_submit_path = year_final_results_path / Path(saved_submit_folder_alias)
    submit_file_path = saved_submit_path / Path(year_submit_filename)

    # Reading the submit file
    submit_df = pd.read_excel(submit_file_path)
    return submit_df


def read_final_pub_list_data(final_results_path,
                             corpus_year, cols_list):
    """Reads saved final data of papers lists resulting from 
    the consolidation step.

    Args:
        final_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
        cols_list (list): Used columns names for the file read.
    Returns:
        (tup): (papers data (dataframe), full path to the books data file).
    """
    # Setting useful aliases
    pub_list_filename_base = bm_pg.ARCHI_YEAR["pub list file name base"]
    saved_pub_list_folder_alias = bm_pg.ARCHI_RESULTS["pub-lists"]

    # Setting useful xlsx file names for input data
    year_pub_list_filename = pub_list_filename_base + " " + corpus_year
    pub_list_filename = year_pub_list_filename + ".xlsx"

    # Setting input-data paths
    year_final_results_path = final_results_path / Path(corpus_year)
    saved_pub_list_path = year_final_results_path / Path(saved_pub_list_folder_alias)
    pub_list_file_path = saved_pub_list_path / Path(pub_list_filename)

    # Initializing the dataframe to be analysed
    pub_df = pd.read_excel(pub_list_file_path,
                           usecols=cols_list)
    return pub_df


def read_final_set_homonyms_data(final_results_path, corpus_year):
    """Reads saved publications list with one row per Institute author 
    and its attributes after resolving homonyms.
    
    This data have been initially built through the `set_saved_homonyms` 
    function of the `bmfuncts.use_homonyms` module.

    Args:
        final_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The resulting dataframe from the read.
    """

    # Setting useful aliases
    saved_homonyms_folder_alias = bm_pg.ARCHI_RESULTS["homonyms"]
    homonyms_file_base_alias = bm_pg.ARCHI_YEAR["homonymes file name base"]

    # Setting input file
    year_homonyms_file =  corpus_year + " " + homonyms_file_base_alias + ".xlsx"

    # Setting useful paths
    year_final_results_path = final_results_path / Path(corpus_year)
    saved_homonyms_path = year_final_results_path / Path(saved_homonyms_folder_alias)
    homonyms_file_path = saved_homonyms_path / Path(year_homonyms_file)

    # Reading the submit file
    set_homonyms_df = pd.read_excel(homonyms_file_path)
    return set_homonyms_df


def build_pub_ids_lists(final_results_path, year, cols_list):
    """Builds the lists of publication IDs from the final list of publications 
    of the institute for each document type.

    The useful data are obtained from the final list of publications of the institute 
    through the `read_final_pub_list_data` function imported from 
    the `bmfuncts.useful_functs` module. 
    The document types are capitalized through the `set_capwords_lambda` lambda function 
    imported from the `bmfuncts.useful_functs` module.

    Args:
        final_results_path (path): Full path to the folder where final results are saved.
        year (str): 4 digits year of the corpus.
        cols_list (list): The column names (str) of publication IDs and document type \
        in the final list of publications.
    Returns:
        (tuple): (list of all publication IDs of the institute, \
        list of the IDs of publications in journals, \
        list of the IDs of publications in conference proceedings, \
        list of the IDS of publications in books).
    """
    final_pub_id_col, final_doctype_col = cols_list
    pub_type_df = read_final_pub_list_data(final_results_path, year, cols_list)
    pub_type_df[final_doctype_col] = pub_type_df.apply(set_capwords_lambda(final_doctype_col), axis=1)

    journal_pub_id_df = pub_type_df[pub_type_df[final_doctype_col].isin(bm_pg.DOC_TYPE_DICT['articles'])]
    proceedings_pub_id_df = pub_type_df[pub_type_df[final_doctype_col].isin(bm_pg.DOC_TYPE_DICT['proceedings'])]
    books_pub_id_df = pub_type_df[pub_type_df[final_doctype_col].isin(bm_pg.DOC_TYPE_DICT['books'])]
    institute_pub_ids_list = pub_type_df[final_pub_id_col].to_list()
    journal_pub_ids_list = journal_pub_id_df[final_pub_id_col].to_list()
    proceedings_pub_ids_list = proceedings_pub_id_df[final_pub_id_col].to_list()
    book_pub_ids_list = books_pub_id_df[final_pub_id_col].to_list()
    return institute_pub_ids_list, journal_pub_ids_list, proceedings_pub_ids_list, book_pub_ids_list
