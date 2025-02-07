"""Module of useful functions used by several modules of package `bmfuncts`.

"""

__all__ = ['check_dedup_parsing_available',
           'concat_dfs',
           'create_archi',
           'create_folder',
           'read_parsing_dict',
           'save_fails_dict',
           'save_parsing_dict',
           'set_rawdata',
           'standardize_firstname_initials',
           'standardize_txt',
          ]


# Standard library imports
import json
import os
import shutil
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# local imports
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_user_config


def concat_dfs(dfs_list, dedup_cols=None, keep='first', axis=0,
               concat_ignore_index=False, drop_ignore_index=False):
    """Allows to avoid warnings when using pandas concat of a list of dataframes 
    with empty dataframe in it and drops duplicates in the concatenated dataframe.

    Args:
        dfs_list (list): The list of pandas dataframes to concatenate.
        dedup_cols (list): Same as 'subset' parameter of 'drop_duplicates' method \
        of 'pandas.DataFrame' method, optional, default None.
        keep (str): Same as 'keep' parameter of 'drop_duplicates' method \
        of 'pandas.DataFrame' method, optional, default 'first'.
        axis (int): Same as 'axis' parameter of 'concat' method of 'pandas.DataFrame' \
        method, optional, default 0.
        concat_ignore_index (bool): Same as 'ignore_index' parameter of concat \
        method of 'pandas.DataFrame' method, optional, default False.
        drop_ignore_index (bool): Same as 'ignore_index' parameter of drop_duplicates \
        method of 'pandas.DataFrame' method, optional, default False.
    Returns:
        (dataframe): Result of the concatenation.    
    """

    # Setting list of not empty dataframes
    dfs_clean_list = []
    for df in dfs_list:
        if not df.empty:
            dfs_clean_list.append(df)
    dfs_clean_nb = len(dfs_clean_list)

    # Concatenating dataframes
    if dfs_clean_nb==0:
        concat_df = dfs_list[0].copy()
    elif dfs_clean_nb==1:
        concat_df = dfs_clean_list[0].copy()
    else:
        concat_df = pd.concat(dfs_clean_list, axis=axis,
                              ignore_index=concat_ignore_index)

    # Removing duplicates
    full_col_list = list(concat_df.columns)
    if dedup_cols and all(i in full_col_list for i in dedup_cols):
        concat_df = concat_df.drop_duplicates(subset=dedup_cols,
                                              keep=keep,
                                              ignore_index=drop_ignore_index)
    else:
        concat_df = concat_df.drop_duplicates(keep=keep,
                                              ignore_index=drop_ignore_index)
    return concat_df


def standardize_firstname_initials(initials_init):
    """Standardizes the initials of a firstname by removing minus symbol 
    between initials. 
    
    For example, changes "P-Y" into "PY"

    Args:
        initials_init (str): String containing raw firstname initials 
        to be standardized.
    Returns:
        (str): The standardized string."""
    initials_init = initials_init.replace('-',' ')
    initials = ''.join(initials_init.split(' '))
    return initials


def standardize_txt(text):
    """Standardizes text by keeping only ASCII characters
    and replacing minus symbol between words by space.

    Args:
        text (str): String to be standardized.
    Returns:
        (str): The standardized string."""
    # Removing accentuated characters
    new_text = bp.remove_special_symbol(text, only_ascii=True, strip=True)

    # Remove minus
    new_text = new_text.replace("-", " ").strip()
    return new_text


def check_dedup_parsing_available(bibliometer_path, year):
    """Checks if deduplication parsing folder exist and not empty.

    Args:
        bibliometer_path (path): Full path to working folder.
        year (str): 4 digits year of the corpus.
    Returns:
        (bool): Status of the deduplication parsing folder \
        (False if folder didn't exist or is empty).
    """
    # To Do:  Checks if a specific parsing file is available not only if folder is empty

    # Setting default returned status
    dedup_parsing_status = False

    # Getting the full paths of the working folder architecture for the corpus "year select"
    config_tup = set_user_config(bibliometer_path, year, pg.BDD_LIST)
    parsing_path_dict = config_tup[1]

    # Setting parsing files extension of saved results
    parsing_save_extent = pg.TSV_SAVE_EXTENT

    # Setting path of deduplicated parsings
    dedup_parsing_path = parsing_path_dict['dedup']
    if os.path.isdir(dedup_parsing_path):
        dedup_files_list = []
        for path, _, files in os.walk(dedup_parsing_path):
            dedup_files_list.extend(Path(path) / Path(file) for file in files
                                    if file.endswith(parsing_save_extent))
        if len(dedup_files_list)!=0:
            dedup_parsing_status = True
    return dedup_parsing_status


def _get_database_file_path(database_folder_path, database_file_end):
    """Selects the most recent file ending with 'database_file_end'.

    This done through the following steps:

    1. Lists all the files with this ending present in the \
    folder targeted by "database_folder_path".
    2. Selects the most recent one in this list using date \
    of last modification.

    Args:
        database_folder_path (path): The path to the folder where files \
        with names ending with 'database_file_end' will be searched.
        database_file_end (str): Ending of the names of the files \
        to be searched.
    Returns:
        (path): Path targeting the file found and selected.
    """

    # Listing the available files ending with database_file_end
    list_data_base = []
    for path, _, files in os.walk(database_folder_path):
        list_data_base.extend(Path(path) / Path(file) for file in files
                              if file.endswith(database_file_end))

    if list_data_base:
        # Selecting the most recent file with raw_extent extension
        list_data_base.sort(key = os.path.getmtime, reverse=True)
        database_file_path = list_data_base[0]
    else:
        database_file_path = None
    return database_file_path


def _set_database_extract_info(bibliometer_path, datatype, database):
    """Builds the path to database extractions and the file 
    names ending that are specific to the data type 'datatype'.

    It also sets the folder name of the empty files required for 
    specific data types (ex: using only "WoS" datatype requires 
    empty files for Scopus extractions). 
    To do that, it uses the global 'ARCHI_EXTRACT' defined 
    in the module imported as pg.

    Args:
        bibliometer_path (path): The path to the working folder.
        datatype (str): The data type of data combination type \
        from databases.
        database (str): The database selected for the analysis.
    Returns:
        (tup): Tuple = (path to database extractions (path), \
        file name ending (str), \
        path to the folder of empty files (path)).
    """

    # Setting useful aliases
    extraction_folder = pg.ARCHI_EXTRACT["root"]
    empty_file_folder = pg.ARCHI_EXTRACT["empty-file folder"]
    database_folder = pg.ARCHI_EXTRACT[database]["root"]
    database_file_base = pg.ARCHI_EXTRACT[database][datatype]
    database_file_extent = pg.ARCHI_EXTRACT[database]["file_extent"]
    database_file_end = database_file_base + database_file_extent

    # Setting useful paths
    extraction_folder_path = bibliometer_path / Path(extraction_folder)
    database_folder_path = extraction_folder_path / Path(database_folder)

    return database_folder_path, database_file_end, empty_file_folder


def set_rawdata(bibliometer_path, datatype, years_list, database):
    """The function sets the rawdata to be used for the data type 'datatype' analysis.

    It copies the files ending with 'database_file_end' from database folder 
    targeted by the path 'database_folder_path' to the rawdata folder 
    targeted by the path 'rawdata_path'. 
    To do that it uses the `_set_database_extract_info` internal function. 
    When the database is Scopus and the data type to be analysed is restricted to WoS, 
    empty files ending with 'database_file_end' are used as Scopus rawdata.

    Args:
        bibliometer_path (path): The path to the working folder.
        datatype (str): The data type of data combination type \
        from databases.
        years_list (list): List of corpus years (4 digits str).
        database (str): The database selected for the analysis.
    Returns:
        (str): End message recalling the database and data type used.
    """

    # Getting database extractions info
    return_tup = _set_database_extract_info(bibliometer_path, datatype, database)
    database_folder_path, database_file_end, empty_file_folder = return_tup

    last_year_database_file_end = database_file_end
    if datatype==pg.DATATYPE_LIST[1] and database==bp.SCOPUS:
        last_year_datatype = pg.DATATYPE_LIST[0]
        return_tup = _set_database_extract_info(bibliometer_path, last_year_datatype,
                                                database)
        _, last_year_database_file_end, _ = return_tup

    # Cycling on year
    for year in years_list:
        if database==bp.SCOPUS and datatype==pg.DATATYPE_LIST[2]:
            year_database_folder_path = database_folder_path / Path(empty_file_folder)
        else:
            year_database_folder_path = database_folder_path / Path(year)
            year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                              database_file_end)
            if not year_database_file_path:
                year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                                  last_year_database_file_end)

        rawdata_path_dict, _, _ = set_user_config(bibliometer_path, year, pg.BDD_LIST)
        rawdata_path = rawdata_path_dict[database]
        if os.path.exists(rawdata_path):
            shutil.rmtree(rawdata_path)
        os.makedirs(rawdata_path)
        shutil.copy2(year_database_file_path, rawdata_path)

    message = f"\n{database} rawdata set for {datatype} data type."
    return message


def create_folder(root_path, folder, verbose=False):
    """Creates a folder checking first if it already exists.

    Args:
        root_path (path): Full path to the folder where \
        the new folder is created.
        folder (str): Name of the folder to be created.
        verbose (bool): Optional status of prints (default = False).
    Returns:
        (path): Full path to the created folder.
    """

    folder_path = root_path / Path(folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        message = f"{folder_path} created"
    else:
        message = f"{folder_path} already exists"

    if verbose:
        print(message)
    return folder_path


def create_archi(bibliometer_path, corpus_year_folder, verbose=False):
    """Creates a corpus folder with the required architecture.

    It uses the global "ARCHI_YEAR" for the names of the sub_folders.

    Args:
        bibliometer_path (path): The full path of the working folder.
        corpus_year_folder (str): The name of the folder of the corpus.
        verbose (bool): Optional status of prints (default = False).
    Returns:
        (str): End message recalling the corpus-year architecture created.
    """
    # Setting useful alias
    archi_alias = pg.ARCHI_YEAR
    extract_folder_alias = pg.ARCHI_EXTRACT["root"]
    archiv_folder_alias = pg.ARCHI_EXTRACT["archiv"]

    # Creating folders for corpus extractions from databases for the corpus year
    extract_folder_path = bibliometer_path / Path(extract_folder_alias)
    for bdd in pg.BDD_LIST:
        bdd_extract_folder_alias = pg.ARCHI_EXTRACT[bdd]["root"]
        bdd_extract_folder_path = extract_folder_path / Path(bdd_extract_folder_alias)
        year_bdd_extract_folder_path = create_folder(bdd_extract_folder_path,
                                                     corpus_year_folder, verbose=verbose)
        _ = create_folder(year_bdd_extract_folder_path, archiv_folder_alias, verbose=verbose)

    # Creating architecture for corpus-year working-folder
    corpus_year_folder_path = create_folder(bibliometer_path, corpus_year_folder, verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["bdd mensuelle"], verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["homonymes folder"], verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["OTP folder"], verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["pub list folder"], verbose=verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["history folder"], verbose=verbose)

    analysis_folder = create_folder(corpus_year_folder_path, archi_alias["analyses"],
                                    verbose=verbose)
    _ = create_folder(analysis_folder, archi_alias["if analysis"], verbose=verbose)
    _ = create_folder(analysis_folder, archi_alias["keywords analysis"], verbose=verbose)
    _ = create_folder(analysis_folder, archi_alias["subjects analysis"], verbose=verbose)
    _ = create_folder(analysis_folder, archi_alias["countries analysis"], verbose=verbose)
    _ = create_folder(analysis_folder, archi_alias["institutions analysis"], verbose=verbose)

    corpus_folder = create_folder(corpus_year_folder_path, archi_alias["corpus"], verbose=verbose)

    concat_folder = create_folder(corpus_folder, archi_alias["concat"], verbose=verbose)
    _ = create_folder(concat_folder, archi_alias["parsing"], verbose=verbose)

    dedup_folder = create_folder(corpus_folder, archi_alias["dedup"], verbose=verbose)
    _ = create_folder(dedup_folder, archi_alias["parsing"], verbose=verbose)

    scopus_folder = create_folder(corpus_folder, archi_alias["scopus"], verbose=verbose)
    _ = create_folder(scopus_folder, archi_alias["parsing"], verbose=verbose)
    _ = create_folder(scopus_folder, archi_alias["rawdata"], verbose=verbose)

    wos_folder = create_folder(corpus_folder, archi_alias["wos"], verbose=verbose)
    _ = create_folder(wos_folder, archi_alias["parsing"], verbose=verbose)
    _ = create_folder(wos_folder, archi_alias["rawdata"], verbose=verbose)

    message = f"Architecture created for {corpus_year_folder} folder"
    return message


def _set_item_path(item_filename_base, save_extent, parsing_path):
    item_file_name = item_filename_base + "." + save_extent
    item_path = parsing_path / Path(item_file_name)
    return item_path


def _save_item(item_df, item_filename_base, save_extent, parsing_path):
    item_working_path = _set_item_path(item_filename_base, save_extent, parsing_path)
    if save_extent=="xlsx":
        item_df.to_excel(item_working_path, index=False)
    elif save_extent=="dat":
        item_df.to_csv(item_working_path, index=False, sep='\t')
    else:
        item_df.to_csv(item_working_path, index=False, sep=',')


def _save_final_dedup(item_df, item_filename_base, save_extent, dedup_infos):
    # Setting parameters from args
    bibliometer_path, datatype, corpus_year = dedup_infos

    # Setting aliases for final saving deduplication results
    results_root_alias = pg.ARCHI_RESULTS["root"]
    results_folder_alias = pg.ARCHI_RESULTS[datatype]
    results_sub_folder_alias = pg.ARCHI_RESULTS["dedup_parsing"]

    # Setting path for final saving deduplication results
    results_root_path   = bibliometer_path / Path(results_root_alias)
    results_folder_path = results_root_path / Path(results_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_parsing_path = year_target_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required final results folders
    if not os.path.exists(year_target_folder_path):
        os.makedirs(year_target_folder_path)
    if not os.path.exists(target_parsing_path):
        os.makedirs(target_parsing_path)

    item_final_path = _set_item_path(item_filename_base, save_extent, target_parsing_path)
    if save_extent=="xlsx":
        item_df.to_excel(item_final_path, index=False)
    elif save_extent=="dat":
        item_df.to_csv(item_final_path, index=False, sep='\t')
    else:
        item_df.to_csv(item_final_path, index=False, sep=',')
    return corpus_year, target_parsing_path


def save_parsing_dict(parsing_dict, parsing_path,
                      item_filename_dict, save_extent,
                      dedup_infos=None):
    """Saves the dataframes passed through the dict of parsing results 
    as files of a specifyed type.

    It may manage the final saving of the deduplication results.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the dataframes of parsing results.
        parsing_path (path): Full path to the folder for saving \
        the parsing results.
        item_filename_dict (dict): Dict keyed by the parsing items \
        and valued by the file names for saving the parsing results.
        save_extent (str): File type given by file extension without \
        the dot seprator (ex: "xlsx" for Excel file type).
        dedup_infos (tup): Optional tuple for final saving of deduplication \
        results = (Full path to working folder (path), \
        Data combination type from corpuses databases (str), \
        4 digits year of the corpus (str)) (default = None).
    """
    parsing_items_nb = len(parsing_dict.keys())
    item_idx = 0
    # Cycling on parsing items
    for item in bp.PARSING_ITEMS_LIST:
        if item in parsing_dict.keys():
            item_df = parsing_dict[item]
            item_filename_base = item_filename_dict[item]
            _save_item(item_df, item_filename_base, save_extent, parsing_path)

            if dedup_infos:
                item_idx += 1
                return_tup = _save_final_dedup(item_df, item_filename_base, save_extent, dedup_infos)
                if item_idx==parsing_items_nb:
                    corpus_year, final_dedup_path = return_tup
                    end_message = (f"Deduplication files for year {corpus_year} saved in folder: "
                                   f"\n  '{final_dedup_path}'")
                    print(end_message)


def read_parsing_dict(parsing_path, item_filename_dict, save_extent):
    """Reads the dataframes of the parsing results from files of a specifyed type.

    Args:
        parsing_path (path): Full path to the folder where the the parsing \
        results are located.
        item_filename_dict (dict): Dict keyed by the parsing items and valued \
        by the file names of the parsing results.
        save_extent (str): File type given by file extension without the dot \
        seprator (ex: "xlsx" for Excel file type).
    Returns:
        (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from \
        the package imported as bp and valued by the dataframes \
        of parsing results.
    """

    parsing_dict = {}
    # Cycling on parsing items
    for item in bp.PARSING_ITEMS_LIST:
        item_df = None
        if save_extent == "xlsx":
            item_xlsx_file = item_filename_dict[item] + ".xlsx"
            item_xlsx_path = parsing_path / Path(item_xlsx_file)
            if item_xlsx_path.is_file():
                try:
                    item_df = pd.read_excel(item_xlsx_path)
                except pd.errors.EmptyDataError:
                    item_df = pd.DataFrame()
        elif save_extent=="dat":
            item_tsv_file = item_filename_dict[item] + ".dat"
            item_tsv_path = parsing_path / Path(item_tsv_file)
            if item_tsv_path.is_file():
                try:
                    item_df = pd.read_csv(item_tsv_path, sep = "\t")
                except pd.errors.EmptyDataError:
                    item_df = pd.DataFrame()
        else:
            pass

        if item_df is not None:
            parsing_dict[item] = item_df
    return parsing_dict


def save_fails_dict(fails_dict, parsing_path):
    """The function `save_fails_dict` saves parsing fails in a json file 
    named by the global PARSING_PERF imported from the module imported as pg.

    Args:
        fails_dict (dict): The dict of parsing fails.
        parsing_path (path): The full path to the parsing results folder \
        where the json file is saved.
    """
    parsing_perf_path = parsing_path / Path(pg.PARSING_PERF)
    with open(parsing_perf_path, 'w', encoding="utf-8") as write_json:
        json.dump(fails_dict, write_json, indent=4)
