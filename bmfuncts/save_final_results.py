""" Module of functions for saving final results.
"""

__all__ = ['save_final_countries',
           'save_final_continents',
           'save_final_doctypes',
           'save_final_ifs',
           'save_final_institutions',
           'save_final_kws',
           'save_final_hash_ids',
           'save_final_pub_lists',
           'save_final_results',
           'save_final_set_homonyms',
           'save_final_submit',
          ]


# Standard library imports
import os
import shutil
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.rename_cols import set_final_col_names


def save_final_hash_ids(bibliometer_path, corpus_year,
                        results_folder_path):
    """Saves final results of the hash-IDs of publications for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """


    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["hash_id"]

    # Setting aliases of common parts of file names
    origin_hash_id_folder_alias = pg.ARCHI_YEAR["bdd mensuelle"]
    hash_id_file_base_alias = pg.ARCHI_YEAR["hash_id file name"]
    year_hash_id_file_alias = corpus_year + " " + hash_id_file_base_alias

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_hash_id_path = origin_corpus_year_path / Path(origin_hash_id_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_hash_id_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_hash_id_path):
        os.makedirs(target_hash_id_path)

    origin_path = origin_hash_id_path / Path(hash_id_file_base_alias)
    target_path = target_hash_id_path / Path(year_hash_id_file_alias)

    # Copying file from origin path to target path
    shutil.copy2(origin_path, target_path)

    end_message = (f"Hash-IDs for year {corpus_year} saved in folder: "
                   f"\n  '{target_hash_id_path}'")
    return end_message


def save_final_submit(bibliometer_path, corpus_year,
                      results_folder_path):
    """Saves final results of the list of publications with one row per author 
    for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """


    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["submit"]

    # Setting aliases of common parts of file names
    origin_submit_folder_alias = pg.ARCHI_YEAR["bdd mensuelle"]
    submit_file_base_alias = pg.ARCHI_YEAR["submit file name"]
    year_submit_file_alias = corpus_year + " " + submit_file_base_alias

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_submit_path = origin_corpus_year_path / Path(origin_submit_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_submit_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_submit_path):
        os.makedirs(target_submit_path)

    origin_path = origin_submit_path / Path(submit_file_base_alias)
    target_path = target_submit_path / Path(year_submit_file_alias)

    # Copying file from origin path to target path
    shutil.copy2(origin_path, target_path)

    end_message = ("List of publications with one row per author "
                   f"for year {corpus_year} saved in folder: "
                   f"\n  '{target_submit_path}'")
    return end_message


def save_final_set_homonyms(bibliometer_path, corpus_year,
                            results_folder_path):
    """Saves final results of the list of publications with one row per author 
    for the corpus year after homonymies resolution.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["homonyms"]

    # Setting aliases of common parts of file names
    origin_submit_homonyms_alias = pg.ARCHI_YEAR["homonymes folder"]
    homonyms_file_base_alias = pg.ARCHI_YEAR["homonymes file name base"]
    origin_homonyms_file =  homonyms_file_base_alias + " " + corpus_year + ".xlsx"
    target_homonyms_file =  corpus_year + " " + homonyms_file_base_alias + ".xlsx"

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_submit_path = origin_corpus_year_path / Path(origin_submit_homonyms_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_homonyms_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_homonyms_path):
        os.makedirs(target_homonyms_path)

    origin_path = origin_submit_path / Path(origin_homonyms_file)
    target_path = target_homonyms_path / Path(target_homonyms_file)

    # Copying file from origin path to target path
    shutil.copy2(origin_path, target_path)

    end_message = (f"Solved homonyms for year {corpus_year} saved in folder: "
                   f"\n  '{target_homonyms_path}'")
    return end_message


def save_final_pub_lists(bibliometer_path,
                         corpus_year, results_folder_path):
    """Saves final results of the publications lists for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["pub-lists"]

    # Setting aliases of common parts of file names
    origin_pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    invalid_pub_file_base_alias = pg.ARCHI_YEAR["invalid file name base"]
    year_pub_list_file_alias = pub_list_file_base_alias + " " + corpus_year
    year_invalid_pub_file_alias = invalid_pub_file_base_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_pub_list_path = origin_corpus_year_path / Path(origin_pub_list_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_pub_list_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_pub_list_path):
        os.makedirs(target_pub_list_path)

    # Setting origin and target file paths
    origin_paths_dict = {}
    target_paths_dict = {}

    full_pub_list_file_alias = year_pub_list_file_alias + ".xlsx"
    origin_paths_dict["Full"] = origin_pub_list_path / Path(full_pub_list_file_alias)
    target_paths_dict["Full"] = target_pub_list_path / Path(full_pub_list_file_alias)

    for key, _ in pg.DOCTYPE_TO_SAVE_DICT.items():
        key_pub_list_file_alias = year_pub_list_file_alias + "_" + key + ".xlsx"
        origin_paths_dict[key] = origin_pub_list_path / Path(key_pub_list_file_alias)
        target_paths_dict[key] = target_pub_list_path / Path(key_pub_list_file_alias)

    other_pub_list_file_alias = year_pub_list_file_alias + "_Others.xlsx"
    origin_paths_dict["Others"] = origin_pub_list_path / Path(other_pub_list_file_alias)
    target_paths_dict["Others"] = target_pub_list_path / Path(other_pub_list_file_alias)

    invalid_pub_list_file_alias = year_invalid_pub_file_alias + ".xlsx"
    origin_paths_dict["Invalid"] = origin_pub_list_path / Path(invalid_pub_list_file_alias)
    target_paths_dict["Invalid"] = target_pub_list_path / Path(invalid_pub_list_file_alias)

    for key, origin_path in origin_paths_dict.items():
        # Copying file from origin path to target path
        shutil.copy2(origin_path, target_paths_dict[key])

    end_message = (f"Final publications lists for year {corpus_year} saved in folder: "
                   f"\n  '{target_pub_list_path}'")
    return end_message


def save_final_ifs(institute, org_tup, bibliometer_path,
                   corpus_year, results_folder_path, if_analysis_name):
    """Saves final results of number of publications per journal 
    with its impact factor for the corpus year.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
        if_analysis_name (str): Base for building file names for saving \
        impact-factors results.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Setting useful column names aliases
    _, depts_col_list = set_final_col_names(institute, org_tup)

    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["impact-factors"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_ifs_folder_alias = pg.ARCHI_YEAR["if analysis"]
    ifs_file_base_alias = f'{if_analysis_name}'

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_ifs_folder_path = origin_analysis_folder_path / Path(origin_ifs_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_ifs_folder_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_ifs_folder_path):
        os.makedirs(target_ifs_folder_path)

    for dept in [institute] + depts_col_list:

        # Setting origin and target file paths
        dept_file_name = ifs_file_base_alias + f'-{dept}' + '.xlsx'
        origin_dept_file_path = Path(origin_ifs_folder_path) / Path(dept_file_name)
        target_dept_file_path = Path(target_ifs_folder_path) / Path(dept_file_name)

        # Copying file from origin path to target path
        shutil.copy2(origin_dept_file_path, target_dept_file_path)

    end_message = (f"Final impact factors for year {corpus_year} saved in folder: "
                   f"\n  '{target_dept_file_path}'")
    return end_message


def save_final_authors(bibliometer_path, corpus_year,
                       results_folder_path):
    """Saves final results of publications per author for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Internal function
    def _copy_file(origin_file, target_file):
        origin_file_path = origin_authors_path / Path(origin_file)
        target_file_path = target_authors_path / Path(target_file)
        shutil.copy2(origin_file_path, target_file_path)

    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["authors_prod"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_authors_folder_alias = pg.ARCHI_YEAR["authors analysis"]
    authors_file_alias = pg.ARCHI_YEAR["authors file name"]
    authors_stat_file_alias = pg.ARCHI_YEAR["authors weight file name"]
    year_authors_file = authors_file_alias + " " + corpus_year
    year_authors_stat_file = authors_stat_file_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_authors_path = origin_analysis_folder_path / Path(origin_authors_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_authors_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_authors_path):
        os.makedirs(target_authors_path)

    # Setting full path 'origin_authors_file_path' and 'target_authors_file_path'
    # and copying file from origin path to target path for 'year_authors_file' file
    origin_authors_file = year_authors_file + ".xlsx"
    target_authors_file = year_authors_file + ".xlsx"
    _copy_file(origin_authors_file, target_authors_file)

    # Setting full path 'origin_authors_file_path' and 'target_authors_file_path'
    # and copying file from origin path to target path for 'year_authors_stat_file' file
    origin_authors_file = year_authors_stat_file + ".xlsx"
    target_authors_file = year_authors_stat_file + ".xlsx"
    _copy_file(origin_authors_file, target_authors_file)

    end_message = (f"Final authors for year {corpus_year} saved in folder: "
                   f"\n  '{target_authors_path}'")
    return end_message


def save_final_kws(institute, org_tup, bibliometer_path,
                   corpus_year, results_folder_path):
    """Saves final results of number of publications per keyword for the corpus year.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Setting useful column names aliases
    _, depts_col_list = set_final_col_names(institute, org_tup)

    # Setting useful aliases
    auth_kw_item_alias = bp.PARSING_ITEMS_LIST[6]
    index_kw_item_alias = bp.PARSING_ITEMS_LIST[7]
    title_kw_item_alias = bp.PARSING_ITEMS_LIST[8]

    # Setting useful filenames dict
    kw_item_alias_dict = {'AK' : auth_kw_item_alias,
                          'IK' : index_kw_item_alias,
                          'TK' : title_kw_item_alias,
                         }

    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["keywords"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_kws_folder_alias = pg.ARCHI_YEAR["keywords analysis"]

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_kws_folder_path = origin_analysis_folder_path / Path(origin_kws_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_kws_folder_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_kws_folder_path):
        os.makedirs(target_kws_folder_path)

    for dept in [institute] + depts_col_list:
        for kw_type, _ in kw_item_alias_dict.items():
            # Setting origin and target file paths
            dept_file_name = f'{dept} {corpus_year}-{kw_type}.xlsx'
            origin_dept_file_path = Path(origin_kws_folder_path) / Path(dept_file_name)
            target_dept_file_path = Path(target_kws_folder_path) / Path(dept_file_name)

            # Copying file from origin path to target path
            shutil.copy2(origin_dept_file_path, target_dept_file_path)

    end_message = (f"Final keywords for year {corpus_year} saved in folder: "
                   f"\n  '{target_kws_folder_path}'")
    return end_message


def save_final_countries(bibliometer_path,
                         corpus_year, results_folder_path):
    """Saves final results of publications per country for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["countries"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_countries_folder_alias = pg.ARCHI_YEAR["countries analysis"]
    countries_file_alias = pg.ARCHI_YEAR["country weight file name"]
    year_countries_file_alias = countries_file_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_countries_path = origin_analysis_folder_path / Path(origin_countries_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_countries_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_countries_path):
        os.makedirs(target_countries_path)

    # Setting full path 'origin_countries_file_path' and 'target_countries_file_path'
    origin_countries_file_alias = countries_file_alias + ".xlsx"
    origin_countries_file_path = origin_countries_path / Path(origin_countries_file_alias)
    target_countries_file_alias = year_countries_file_alias + ".xlsx"
    target_countries_file_path = target_countries_path / Path(target_countries_file_alias)

    # Copying file from origin path to target path
    shutil.copy2(origin_countries_file_path, target_countries_file_path)

    end_message = (f"Final countries statistics for year {corpus_year} saved in folder: "
                   f"\n  '{target_countries_file_path}'")
    return end_message


def save_final_continents(bibliometer_path,
                          corpus_year, results_folder_path):
    """Saves final results of publications per continent for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["countries"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_countries_folder_alias = pg.ARCHI_YEAR["countries analysis"]
    continents_file_alias = pg.ARCHI_YEAR["continent weight file name"]
    year_continents_file_alias = continents_file_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_countries_path = origin_analysis_folder_path / Path(origin_countries_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_countries_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_countries_path):
        os.makedirs(target_countries_path)

    # Setting full path 'origin_continents_file_path' and 'target_continents_file_path'
    origin_continents_file_alias = continents_file_alias + ".xlsx"
    origin_continents_file_path = origin_countries_path / Path(origin_continents_file_alias)
    target_continents_file_alias = year_continents_file_alias + ".xlsx"
    target_continents_file_path = target_countries_path / Path(target_continents_file_alias)

    # Copying file from origin path to target path
    shutil.copy2(origin_continents_file_path, target_continents_file_path)

    end_message = (f"Final continents statistics for year {corpus_year} saved in folder: "
                   f"\n  '{target_continents_file_path}'")
    return end_message


def save_final_institutions(bibliometer_path,
                            corpus_year, results_folder_path):
    """Saves final results of publications per institution for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["institutions"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_inst_folder_alias = pg.ARCHI_YEAR["institutions analysis"]

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_inst_folder_path = origin_analysis_folder_path / Path(origin_inst_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_inst_folder_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Copying origin dir into target dir
    shutil.copytree(origin_inst_folder_path, target_inst_folder_path, dirs_exist_ok=True)

    end_message = (f"Final stat per institutions for year {corpus_year} saved in folder: "
                   f"\n  '{target_inst_folder_path}'")
    return end_message


def save_final_doctypes(bibliometer_path,
                        corpus_year, results_folder_path):
    """Saves final results of number of publications per doctype for the corpus year.

    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["doctypes"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_doctypes_folder_alias = pg.ARCHI_YEAR["doctype analysis"]

    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_doctypes_folder_path = origin_analysis_folder_path / Path(origin_doctypes_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_doctypes_folder_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Copying origin dir into target dir
    shutil.copytree(origin_doctypes_folder_path, target_doctypes_folder_path, dirs_exist_ok=True)

    end_message = (f"Final stat per doctype for year {corpus_year} saved in folder: "
                   f"\n  '{target_doctypes_folder_path}'")
    return end_message


def save_final_results(institute, org_tup, bibliometer_path, datatype, corpus_year,
                       if_analysis_name, results_to_save_dict, verbose=False):
    """Saves final results of given datatype and corpus year according 
    to the saving status of the results.

    The results types are the following: publications lists, \
    impact factors, authors, keywords, countries and continents.

    To do: Saving the results of co-publication with other institutions \
    and publications per OTPs.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        if_analysis_name (str): Base for building file names for saving \
        impact-factors type of results.
        results_to_save_dict (dict): Dict keyed by the type of results \
        to save and valued by saving status (bool; True if the type of \
        results should be saved).
        verbose (bool): Status of prints (default = False).
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """

    # Setting aliases for saving results
    results_root_alias = pg.ARCHI_RESULTS["root"]
    results_folder_alias = pg.ARCHI_RESULTS[datatype]

    # Setting paths for saving results
    results_root_path = bibliometer_path / Path(results_root_alias)
    results_folder_path = results_root_path / Path(results_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(results_root_path):
        os.makedirs(results_root_path)
    if not os.path.exists(results_folder_path):
        os.makedirs(results_folder_path)

    if results_to_save_dict["hash_ids"]:
        message = save_final_hash_ids(bibliometer_path, corpus_year,
                                      results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["submit"]:
        message = save_final_submit(bibliometer_path, corpus_year,
                                    results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["homonyms"]:
        message = save_final_set_homonyms(bibliometer_path, corpus_year,
                                          results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["pub_lists"]:
        message = save_final_pub_lists(bibliometer_path, corpus_year,
                                       results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["ifs"]:
        message = save_final_ifs(institute, org_tup, bibliometer_path,
                                 corpus_year, results_folder_path,
                                 if_analysis_name)
        if verbose:
            print("\n",message)

    if results_to_save_dict["authors"]:
        message = save_final_authors(bibliometer_path, corpus_year,
                                     results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["kws"]:
        message = save_final_kws(institute, org_tup, bibliometer_path,
                                 corpus_year, results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["countries"]:
        message = save_final_countries(bibliometer_path, corpus_year,
                                       results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["continents"]:
        message = save_final_continents(bibliometer_path, corpus_year,
                                        results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["institutions"]:
        message = save_final_institutions(bibliometer_path, corpus_year,
                                          results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["doctypes"]:
        message = save_final_doctypes(bibliometer_path, corpus_year,
                                      results_folder_path)
        if verbose:
            print("\n",message)

    end_message = (f"Final results for year {corpus_year} saved in folder: "
                   f"\n  '{results_folder_path}'")
    return end_message
