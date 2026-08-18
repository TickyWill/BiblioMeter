""" Module of functions for saving final results.
"""

__all__ = ['save_db_ids_data',
           'save_fails_dict',
           'save_final_countries',
           'save_final_continents',
           'save_final_dedup',
           'save_final_doctypes',
           'save_final_ifs',
           'save_final_affiliations',
           'save_final_kws',
           'save_final_hash_ids',
           'save_final_pub_lists',
           'save_final_results',
           'save_final_set_homonyms',
           'save_final_merge',
           'save_parsing_dict',
           'save_rawdata_correction',
           'set_results_folder_path',
          ]


# Standard library imports
import json
import os
import shutil
from pathlib import Path

# 3rd party imports
#import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.rename_cols import set_final_col_names


def _set_item_path(item_filename_base, save_extent, parsing_path):
    """Build the full path to the item parsing file.

    Args:
        item_filename_base (str): The file name part to be added with the file extent.
        save_extent (str): The extent to be used for building the item file name.
        parsing_path (path): The full path to the folder where the item parsing file is saved.
    Returns:
        (path): The built full path.
    """
    item_file_name = item_filename_base
    if save_extent and not item_file_name.endswith(save_extent):
        item_file_name = item_filename_base + "." + save_extent
    item_path = parsing_path / Path(item_file_name)
    return item_path


def _save_item(item_df, item_filename_base, save_extent, parsing_path):
    """Saves the item parsing data.

    Args:
        item_df (dataframe): The item parsing data to be saved.
        item_filename_base (str): The file name part to be added with the file extent.
        save_extent (str): The extent to be used for building the item file name.
        parsing_path (path): The full path to the folder where the item parsing file is saved.
    """
    item_working_path = _set_item_path(item_filename_base, save_extent, parsing_path)
    if save_extent=="xlsx":
        item_df.to_excel(item_working_path, index=False)
    elif save_extent=="dat":
        item_df.to_csv(item_working_path, index=False, sep='\t')
    else:
        item_df.to_csv(item_working_path, index=False, sep=',')


def save_final_dedup(item_df, item_filename_base, save_extent, dedup_infos):
    """Saves the data of an item of the deduplication results of the parsing step
    as final results.

    Args:
        item_df (dataframe): The data of the deduplication item to be saved.
        item_filename_base (str): The file name base to build the name of the file \
        for saving the item data.
        save_extent (str): The extent for building the name of the file for saving \
        the data.
        dedup_infos (list): The full path to the working folder (path), \
        Data combination type from corpuses databases (str) and \
        4 digits year of the corpus (str).
    """
    # Setting parameters from args
    wf_path, datatype, corpus_year = dedup_infos

    # Setting aliases for final saving deduplication results
    results_root_alias = bm_pg.ARCHI_RESULTS["root"]
    results_folder_alias = bm_pg.ARCHI_RESULTS[datatype]
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["dedup_parsing"]

    # Setting path for final saving deduplication results
    results_root_path = wf_path / Path(results_root_alias)
    results_folder_path = results_root_path / Path(results_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_parsing_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required final results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_parsing_path):
        os.makedirs(target_parsing_path)
    _save_item(item_df, item_filename_base, save_extent, target_parsing_path)


def save_parsing_dict(parsing_dict, parsing_path, parsing_filenames_dict,
                      save_extent, dedup_infos=None):
    """Saves the data passed through the dict of parsing results 
    as files of a specified type.

    It may manage the final saving of the parsing-deduplication results 
    depending on the optional argument 'dedup_infos'.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the data (dataframes) of parsing results.
        parsing_path (path): Full path to the folder for saving \
        the parsing results.
        parsing_filenames_dict (dict): Dict keyed by the parsing items \
        and valued by the file names for saving the parsing results.
        save_extent (str): File type given by file extension without \
        the dot separator (ex: "xlsx" for Excel file type).
        dedup_infos (list): Optional list for final saving of deduplication \
        results = [Full path to working folder (path), \
        Data combination type from corpuses databases (str), \
        4 digits year of the corpus (str) ] (default=[]).
    """
    # Cycling on parsing items
    for item in bm_pg.PARSING_KEYS_DIC['parsing']:
        item_df = parsing_dict[item]
        item_filename_base = parsing_filenames_dict[item]
        _save_item(item_df, item_filename_base, save_extent, parsing_path)

        if dedup_infos:
            save_final_dedup(item_df, item_filename_base, save_extent, dedup_infos)


def save_fails_dict(fails_dict, parsing_path):
    """Saves parsing fails in a JSON file named by the global PARSING_PERF 
    imported from the module imported as bm_pg.

    Args:
        fails_dict (dict): The dict of parsing fails.
        parsing_path (path): The full path to the parsing results folder \
        where the JSON file is saved.
    """
    parsing_perf_path = parsing_path / Path(bm_pg.PARSING_PERF)
    with open(parsing_perf_path, 'w', encoding="utf-8") as write_json:
        json.dump(fails_dict, write_json, indent=4)


def save_db_ids_data(db_ids_df, parsing_path, database_type, dedup_infos=None):
    """Saves database-IDs data as XLSX file.

    Args:
        db_ids_df (dataframe): The database-IDs data.
        parsing_path (path): The full path of the parsing results folder \
        for saving the XLSX file.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        dedup_infos (list): Optional list for final saving of deduplication \
        results = [Full path to working folder (path), \
        Data combination type from corpuses databases (str), \
        4 digits year of the corpus (str) ] (default=[]).
    """
    file_name = database_type.capitalize() + bm_pg.IDS_FILE_BASE
    file_path = parsing_path / Path(file_name)
    db_ids_df.to_excel(file_path, index=False)

    if dedup_infos:
        save_final_dedup(db_ids_df, file_name, "xlsx", dedup_infos)


def save_rawdata_correction(correction_dict, rawdata_path, database_type):
    """Saves the results of rawdata correction as XLSX files.

    Args:
        correction_dict (dict): Composed of the data of corrected authors' names \
        and of the data of corrected addresses.
        rawdata_path (path): The full path of the rawdata folder \
        for saving the XLSX files .
        database_type (str): Database name (ex: 'wos' or 'scopus').
    """
    for key, df in correction_dict.items():
        file_name = database_type.capitalize() + bm_pg.RAWDATA_CORRECT[key]
        file_path = rawdata_path / Path(file_name)
        df.to_excel(file_path, index=False)


def save_final_hash_ids(wf_path, corpus_year, results_folder_path):
    """Saves final results of the hash-IDs of publications for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["hash_id"]

    # Setting aliases of common parts of file names
    origin_hash_id_folder_alias = bm_pg.ARCHI_YEAR["bdd mensuelle"]
    hash_id_file_base_alias = bm_pg.ARCHI_YEAR["hash_id file name"]
    year_hash_id_file_alias = corpus_year + " " + hash_id_file_base_alias

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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


def save_final_merge(wf_path, corpus_year, results_folder_path):
    """Saves final results of the list of publications with one row per author 
    for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["merge"]

    # Setting aliases of common parts of file names
    origin_merge_folder_alias = bm_pg.ARCHI_YEAR["bdd mensuelle"]
    merge_file_base_alias = bm_pg.ARCHI_YEAR["merge file name"]
    year_merge_file_alias = corpus_year + " " + merge_file_base_alias

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
    origin_merge_path = origin_corpus_year_path / Path(origin_merge_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_merge_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_merge_path):
        os.makedirs(target_merge_path)

    origin_path = origin_merge_path / Path(merge_file_base_alias)
    target_path = target_merge_path / Path(year_merge_file_alias)

    # Copying file from origin path to target path
    shutil.copy2(origin_path, target_path)

    end_message = ("List of publications with one row per author "
                   f"for year {corpus_year} saved in folder: "
                   f"\n  '{target_merge_path}'")
    return end_message


def save_final_set_homonyms(wf_path, corpus_year, results_folder_path):
    """Saves final results of the list of publications with one row per author 
    for the corpus year after homonymies resolution.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["homonyms"]

    # Setting aliases of common parts of file names
    origin_merge_homonyms_alias = bm_pg.ARCHI_YEAR["homonymes folder"]
    homonyms_file_base_alias = bm_pg.ARCHI_YEAR["homonymes file name base"]
    origin_homonyms_file =  homonyms_file_base_alias + " " + corpus_year + ".xlsx"
    target_homonyms_file =  corpus_year + " " + homonyms_file_base_alias + ".xlsx"

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
    origin_merge_path = origin_corpus_year_path / Path(origin_merge_homonyms_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_homonyms_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_homonyms_path):
        os.makedirs(target_homonyms_path)

    origin_path = origin_merge_path / Path(origin_homonyms_file)
    target_path = target_homonyms_path / Path(target_homonyms_file)

    # Copying file from origin path to target path
    shutil.copy2(origin_path, target_path)

    end_message = (f"Solved homonyms for year {corpus_year} saved in folder: "
                   f"\n  '{target_homonyms_path}'")
    return end_message


def save_final_pub_lists(wf_path, corpus_year, results_folder_path):
    """Saves final results of the publications lists for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["pub-lists"]

    # Setting aliases of common parts of file names
    origin_pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    invalid_pub_file_base_alias = bm_pg.ARCHI_YEAR["invalid file name base"]
    year_pub_list_file_alias = pub_list_file_base_alias + " " + corpus_year
    year_invalid_pub_file_alias = invalid_pub_file_base_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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

    for key, _ in bm_pg.DOCTYPE_TO_SAVE_DICT.items():
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


def save_final_ifs(institute, org_tup, wf_path, corpus_year, results_folder_path, if_analysis_name):
    """Saves final results of number of publications per journal 
    with its impact factor for the corpus year.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
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
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["impact-factors"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_ifs_folder_alias = bm_pg.ARCHI_YEAR["if analysis"]
    ifs_file_base_alias = f'{if_analysis_name}'

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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
                   f"\n  '{target_ifs_folder_path}'")
    return end_message


def save_final_authors(wf_path, corpus_year, results_folder_path):
    """Saves final results of publications per author for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
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
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["authors_prod"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_authors_folder_alias = bm_pg.ARCHI_YEAR["authors analysis"]
    authors_file_alias = bm_pg.ARCHI_YEAR["authors file name"]
    authors_stat_file_alias = bm_pg.ARCHI_YEAR["authors weight file name"]
    year_authors_file = authors_file_alias + " " + corpus_year
    year_authors_stat_file = authors_stat_file_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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


def save_final_kws(institute, org_tup, wf_path, corpus_year, results_folder_path):
    """Saves final results of number of publications per keyword for the corpus year.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting useful column names aliases
    _, depts_col_list = set_final_col_names(institute, org_tup)

#    # Setting useful aliases
#    auth_kw_item_alias = bp.PARSING_ITEMS_LIST[6]
#    index_kw_item_alias = bp.PARSING_ITEMS_LIST[7]
#    title_kw_item_alias = bp.PARSING_ITEMS_LIST[8]
#
#    # Setting useful filenames dict
#    kw_item_alias_dict = {'AK' : auth_kw_item_alias,
#                          'IK' : index_kw_item_alias,
#                          'TK' : title_kw_item_alias,
#                         }
#
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["keywords"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_kws_folder_alias = bm_pg.ARCHI_YEAR["keywords analysis"]

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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
        for kw_type in ['AK', 'IK', 'TK']:
            # Setting origin and target file paths
            dept_file_name = f'{dept} {corpus_year}-{kw_type}.xlsx'
            origin_dept_file_path = Path(origin_kws_folder_path) / Path(dept_file_name)
            target_dept_file_path = Path(target_kws_folder_path) / Path(dept_file_name)

            # Copying file from origin path to target path
            shutil.copy2(origin_dept_file_path, target_dept_file_path)

    end_message = (f"Final keywords for year {corpus_year} saved in folder: "
                   f"\n  '{target_kws_folder_path}'")
    return end_message


def save_final_countries(wf_path, corpus_year, results_folder_path):
    """Saves final results of publications per country for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["countries"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_countries_folder_alias = bm_pg.ARCHI_YEAR["countries analysis"]
    countries_file_alias = bm_pg.ARCHI_YEAR["country weight file name"]
    year_countries_file_alias = countries_file_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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


def save_final_continents(wf_path, corpus_year, results_folder_path):
    """Saves final results of publications per continent for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["countries"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_countries_folder_alias = bm_pg.ARCHI_YEAR["countries analysis"]
    continents_file_alias = bm_pg.ARCHI_YEAR["continent weight file name"]
    year_continents_file_alias = continents_file_alias + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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


def save_final_institute_country(wf_path, corpus_year, results_folder_path, institute_country):
    """Saves final results of publications per country for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
        institute_country (str): Country of the Institute.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["countries"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_countries_folder_alias = bm_pg.ARCHI_YEAR["countries analysis"]
    institute_country_file_base_alias = bm_pg.ARCHI_YEAR["institute-country weight file base"]

    # Setting useful file names
    institute_country_file_name = institute_country_file_base_alias + institute_country
    year_institute_country_file_name = institute_country_file_name + " " + corpus_year

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
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
    origin_institute_country_file_name = institute_country_file_name + ".xlsx"
    origin_institute_country_file_path = origin_countries_path / Path(origin_institute_country_file_name)
    target_institute_country_file_name = year_institute_country_file_name + ".xlsx"
    target_institute_country_file_path = target_countries_path / Path(target_institute_country_file_name)

    # Copying file from origin path to target path
    shutil.copy2(origin_institute_country_file_path, target_institute_country_file_path)

    end_message = (f"Final Institute country statistics for year {corpus_year} saved in folder: "
                   f"\n  '{target_countries_path}'")
    return end_message


def save_final_affiliations(wf_path, corpus_year, results_folder_path):
    """Saves final results of publications per affiliation for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["institutions"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_affils_folder_alias = bm_pg.ARCHI_YEAR["institutions analysis"]

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_affils_folder_path = origin_analysis_folder_path / Path(origin_affils_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_affils_folder_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Copying origin dir into target dir
    shutil.copytree(origin_affils_folder_path, target_affils_folder_path, dirs_exist_ok=True)

    end_message = (f"Final stat per affiliation for year {corpus_year} saved in folder: "
                   f"\n  '{target_affils_folder_path}'")
    return end_message


def save_final_doctypes(wf_path, corpus_year, results_folder_path):
    """Saves final results of number of publications per doctype for the corpus year.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        results_folder_path (path): Full path to the folder where final \
        results have to be saved.
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting aliases for saving results
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["doctypes"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    origin_doctypes_folder_alias = bm_pg.ARCHI_YEAR["doctype analysis"]

    # Setting common paths
    origin_corpus_year_path = wf_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_doctypes_folder_path = origin_analysis_folder_path / Path(origin_doctypes_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_doctypes_folder_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Copying origin dir into target dir
    shutil.copytree(origin_doctypes_folder_path, target_doctypes_folder_path, dirs_exist_ok=True)

    end_message = (f"Final stat per doctype for year {corpus_year} saved in folder: "
                   f"\n  '{target_doctypes_folder_path}'")
    return end_message


def set_results_folder_path(wf_path, datatype):
    """Sets the path to the folder where the final results
    will be saved given the datatype.

    Args:
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    Returns:
        (path): The full path of the saved results.
    """
    # Setting aliases for saving results
    results_root_alias = bm_pg.ARCHI_RESULTS["root"]
    results_folder_alias = bm_pg.ARCHI_RESULTS[datatype]

    # Setting paths for saving results
    results_root_path = wf_path / Path(results_root_alias)
    results_folder_path = results_root_path / Path(results_folder_alias)

    # Checking availability of required results folders
    if not os.path.exists(results_root_path):
        os.makedirs(results_root_path)
    if not os.path.exists(results_folder_path):
        os.makedirs(results_folder_path)
    return results_folder_path


def save_final_results(params_list, results_to_save_dict, if_analysis_name="None",
                       institute_country="None", verbose=False):
    """Saves final results of given datatype and corpus year according 
    to the saving status of the results.

    The results types are the following: publications lists, \
    impact factors, authors, keywords, countries and continents.

    To do: Saving the results of co-publication with other affiliations \
    and publications per OTPs.

    Args:
        params_list (list): The list composed of the 4 digits year of \
        the corpus (str), of the Institute's name (str), of the org_tup (tup) \
        that contains parameters of Institute's organization, \
        of the full path to working folder (path), and of the data combination type \
        of corpus databases (str).
        results_to_save_dict (dict): Dict keyed by the type of results \
        to save and valued by saving status (bool; True if the type of \
        results should be saved).
        if_analysis_name (str): Optional base (str) building file names \
        for saving impact-factors type of results (default: "None").
        institute_country (str): Optional country of the institute \
        for building the file names for saving related stat data (default: "None").
        verbose (bool): Status of prints (default: False).
    Returns:
        (str): End message recalling corpus year and full path to \
        the folder where final results have been saved.
    """
    # Setting parameters values from 'params_list'
    corpus_year, institute, org_tup, wf_path, datatype = params_list

    # Setting path for saving results
    results_folder_path = set_results_folder_path(wf_path, datatype)

    if results_to_save_dict["hash_ids"]:
        message = save_final_hash_ids(wf_path, corpus_year,
                                      results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["merge"]:
        message = save_final_merge(wf_path, corpus_year,
                                    results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["homonyms"]:
        message = save_final_set_homonyms(wf_path, corpus_year,
                                          results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["pub_lists"]:
        message = save_final_pub_lists(wf_path, corpus_year,
                                       results_folder_path)
        if verbose:
            print(message)

    if results_to_save_dict["ifs"]:
        message = save_final_ifs(institute, org_tup, wf_path,
                                 corpus_year, results_folder_path,
                                 if_analysis_name)
        if verbose:
            print("\n",message)

    if results_to_save_dict["authors"]:
        message = save_final_authors(wf_path, corpus_year,
                                     results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["kws"]:
        message = save_final_kws(institute, org_tup, wf_path,
                                 corpus_year, results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["countries"]:
        message = save_final_countries(wf_path, corpus_year,
                                       results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["continents"]:
        message = save_final_continents(wf_path, corpus_year,
                                        results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["institute_country"]:
        message = save_final_institute_country(wf_path, corpus_year,
                                               results_folder_path,
                                               institute_country)
        if verbose:
            print("\n",message)

    if results_to_save_dict["affiliations"]:
        message = save_final_affiliations(wf_path, corpus_year,
                                          results_folder_path)
        if verbose:
            print("\n",message)

    if results_to_save_dict["doctypes"]:
        message = save_final_doctypes(wf_path, corpus_year,
                                      results_folder_path)
        if verbose:
            print("\n",message)
