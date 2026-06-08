"""Module of functions for parsing data using the `BiblioParsing` package.
"""

__all__ = ['build_and_save_dedup_db_ids',
           'compute_dedup_pub_number',
           'convert_parsing_keys_to_bm',
           'deduplicate_parsing',
           'rawdata_parsing',
           'read_parsing_dict',
           'revers_parsing_keys_to_bp',
           'set_rawdata',
          ]


# Standard library imports
import copy
import os
import shutil
from pathlib import Path

# 3rd party imports
import pandas as pd
from bpfuncts import biblio_parser as bp_biblio_parser
from bpfuncts import concatenate_parsing as bp_concatenate_parsing
from bpfuncts import deduplicate_parsing as bp_deduplicate_parsing

# local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.config_utils import set_rawdata_and_parsing_paths
from bmfuncts.correct_parsing import build_and_save_unknown_country_data
from bmfuncts.correct_parsing import correct_parsing
from bmfuncts.save_final_results import save_db_ids_data
from bmfuncts.save_final_results import save_fails_dict
from bmfuncts.save_final_results import save_parsing_dict
from bmfuncts.save_final_results import save_rawdata_correction
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import print_step_title


def _get_database_file_path(database_folder_path, database_file_end):
    """Selects the most recent file ending with 'database_file_end'.

    This is done through the following steps:

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
    list_data_base = []
    for file in os.listdir(database_folder_path):
        if file.endswith(database_file_end):
            list_data_base.append(file)
    if list_data_base:
        database_file_path = database_folder_path / Path(list_data_base[0])
    else:
        database_file_path = None
    return database_file_path


def _set_database_extract_info(wf_path, datatype, database):
    """Builds the path to database extractions and the file 
    names ending that are specific to the data type 'datatype'.

    It also sets the folder name of the empty files required for 
    specific data types (ex: using only "WoS" datatype requires 
    empty files for Scopus extractions). 
    To do that, it uses the global 'ARCHI_EXTRACT' defined 
    in the module imported as bm_pg.

    Args:
        wf_path (path): The path to the working folder.
        datatype (str): The data type of data combination type \
        from databases.
        database (str): The database selected for the analysis.
    Returns:
        (tup): (path to database extractions (path), \
        file name ending (str), \
        path to the folder of empty files (path)).
    """
    # Setting useful aliases
    extraction_folder = bm_pg.ARCHI_EXTRACT["root"]
    empty_file_folder = bm_pg.ARCHI_EXTRACT["empty-file folder"]
    database_folder = bm_pg.ARCHI_EXTRACT[database]["root"]
    database_file_base = bm_pg.ARCHI_EXTRACT[database][datatype]
    database_file_extent = bm_pg.ARCHI_EXTRACT[database]["file_extent"]
    database_file_end = database_file_base + database_file_extent

    # Setting useful paths
    extraction_folder_path = wf_path / Path(extraction_folder)
    database_folder_path = extraction_folder_path / Path(database_folder)
    database_folder_paths = [database_folder_path]
    if database==bm_pg.SCOPUS:
        scopus_cat_folder_path = database_folder_path / Path(bm_pg.ARCHI_EXTRACT["categories"])
        scopus_cat_codes_path = scopus_cat_folder_path / Path(bm_pg.SCOPUS_CAT_CODES)
        scopus_journals_issn_cat_path = scopus_cat_folder_path / Path(bm_pg.SCOPUS_JOURNALS_ISSN_CAT)
        database_folder_paths = database_folder_paths + [scopus_cat_codes_path, scopus_journals_issn_cat_path]

    return database_folder_paths, database_file_end, empty_file_folder, database_file_extent


def _set_database_rawdata(set_rawdata_params, database):
    """Sets the rawdata to be used for the data type 'datatype' analysis.

    It copies the files ending with 'database_file_end' from database folder 
    targeted by the path 'database_folder_path' to the rawdata folder 
    targeted by the path 'rawdata_path'. 
    To do that it uses the `_set_database_extract_info` internal function. 
    When the data type to be analyzed is restricted to one of the possible rawdata,
    empty files ending with 'database_file_end' are used as the unused rawdata.

    Args:
        set_rawdata_params (list): Composed of the prints parameters, of the path \
        to the working folder, of the data type of data combination type \
        from databases and of the list of corpus years (4 digits str).
        database (str): The database selected for the analysis.
    Returns:
        (str): End message recalling the database and data type used.
    """
    # Setting parameters value from 'set_rawdata_params'
    print_params, wf_path, datatype, years_list = set_rawdata_params

    print_step_text(f"\nSetting rawdata for {database}", print_params)

    # Getting database extractions info
    return_tup = _set_database_extract_info(wf_path, datatype, database)
    database_folder_paths, database_file_end, empty_file_folder, database_file_extent = return_tup
    database_folder_path = database_folder_paths[0]

    # Setting specific parameters for Scopus-HAL data
    last_year_database_file_end = database_file_end
    if datatype==bm_pg.DATATYPE_LIST[1] and database==bm_pg.SCOPUS:
        last_year_datatype = bm_pg.DATATYPE_LIST[0]
        return_tup = _set_database_extract_info(wf_path, last_year_datatype,
                                                database)
        _, last_year_database_file_end, _, _ = return_tup

    # Cycling on year
    missing_rawdata = []
    for year in years_list:
        if database==bm_pg.SCOPUS and datatype==bm_pg.DATATYPE_LIST[2]:
            year_database_folder_path = database_folder_path / Path(empty_file_folder)
            year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                              database_file_end)
        elif database==bm_pg.WOS and datatype==bm_pg.DATATYPE_LIST[3]:
            year_database_folder_path = database_folder_path / Path(empty_file_folder)
            year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                              database_file_end)
        else:
            year_database_folder_path = database_folder_path / Path(year)
            year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                              database_file_end)
            if not year_database_file_path:
                year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                                  last_year_database_file_end)
        # Checking availability of rawdata
        if year_database_file_path:
            rawdata_path_dict, _ = set_rawdata_and_parsing_paths(wf_path, year, bm_pg.BDD_LIST)
            rawdata_path = rawdata_path_dict[database]
            if os.path.exists(rawdata_path):
                for item in os.listdir(rawdata_path):
                    if item.endswith(database_file_extent):
                        os.remove(os.path.join(rawdata_path, item))
            else:
                os.makedirs(rawdata_path)
            shutil.copy2(year_database_file_path, rawdata_path)
        else:
            missing_rawdata.append(year)
    if missing_rawdata:
        step_txt = ("  - Try cancelled because rawdata are missing "
                    f"for {missing_rawdata}")
    else:
        step_txt = f"  - Succeeded to set rawdata for all corpus-years"
    print_step_text(step_txt, print_params)
    return database_folder_path, missing_rawdata


def set_rawdata(set_rawdata_params):
    # Setting parameters value from 'set_rawdata_params'
    print_params, _, datatype, years_list = set_rawdata_params

    print_step_title(f"TRY SETTING RAWDATA FOR {years_list}", print_params)

    rawdata_status = True
    missing_rawdata_dic = {}
    for database in bm_pg.BDD_LIST:
        rawdata_return = _set_database_rawdata(set_rawdata_params, database)
        database_folder_path, missing_rawdata = rawdata_return
        if missing_rawdata:
            missing_rawdata_dic[database] = [database_folder_path, missing_rawdata]
            rawdata_status = False
    return missing_rawdata_dic, rawdata_status


def read_parsing_dict(parsing_path, parsing_filenames_dict, save_extent):
    """Reads the dataframes of the parsing results from files of a specified type.

    Args:
        parsing_path (path): Full path to the folder where the parsing \
        results are located.
        parsing_filenames_dict (dict): Dict keyed by the parsing items and valued \
        by the file names of the parsing results.
        save_extent (str): File type given by file extension without the dot separator \
        (ex: "xlsx" for Excel file type).
    Returns:
        (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from \
        the package imported as bp and valued by the dataframes \
        of parsing results.
    """
    parsing_dict = {}
    # Cycling on parsing items
    for item in bm_pg.PARSING_KEYS_DIC['parsing']:
        item_df = None
        if save_extent=="xlsx":
            item_xlsx_file = parsing_filenames_dict[item] + ".xlsx"
            item_xlsx_path = parsing_path / Path(item_xlsx_file)
            if item_xlsx_path.is_file():
                try:
                    item_df = pd.read_excel(item_xlsx_path)
                except pd.errors.EmptyDataError:
                    item_df = pd.DataFrame()
        elif save_extent=="dat":
            item_tsv_file = parsing_filenames_dict[item] + ".dat"
            item_tsv_path = parsing_path / Path(item_tsv_file)
            if item_tsv_path.is_file():
                try:
                    item_df = pd.read_csv(item_tsv_path, sep = "\t")
                except pd.errors.EmptyDataError:
                    item_df = pd.DataFrame()

        if item_df is not None:
            parsing_dict[item] = item_df
    return parsing_dict


def _compute_col_pub_number(cols, in_left_authorsinst_df, in_left_pub_ids):
    # Setting parameters from globals
    pub_id_col = bm_pg.COL_NAMES['pub_id']

    # Selecting the publication IDs tagged in 'col' column
    sub_data_dict = {}
    for col in cols:
        sub_data_dict[col] = in_left_authorsinst_df[in_left_authorsinst_df[col]==1]
        sub_data_dict[col] = sub_data_dict[col].drop_duplicates(subset=[pub_id_col])
    sub_data_df = concat_dfs(sub_data_dict.values())
    sub_data_df = sub_data_df.drop_duplicates(subset=[pub_id_col])

    # Computing the number of publications tagged in 'col' column
    col_pub_nb = len(sub_data_df)

    # Keeping only the data without tag in 'col' column
    pub_ids_to_drop = sub_data_df[pub_id_col].to_list()
    out_left_pub_ids = list(set(in_left_pub_ids)-set(pub_ids_to_drop))
    out_left_authorsinst_df = in_left_authorsinst_df[in_left_authorsinst_df[pub_id_col].isin(out_left_pub_ids)]

    return col_pub_nb, out_left_authorsinst_df, out_left_pub_ids


def compute_dedup_pub_number(org_tup, dedup_parsing_dict):
    """Computes publications numbers resulting from the deduplication of parsing results.

    The function builts a dictionary keyed by the tags of Institute's publications as given 
    by the 'org_tup' parameter and valued by corresponding computed number of publications. 
    The total number of publication is given at key "all".

    Args:
        org_tup (tup): Contains Institute parameters.
        dedup_parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as 'bp' and valued by the data (dataframes) of parsing results.
    Returns:
        (tup): (Total number of articles (int), Number of articles tagged \
        to be of the Institute).
    """
    # Setting parameters from globals
    pub_id_col = bm_pg.COL_NAMES['pub_id']

    # Setting useful Institute's parameters
    institute_cols = [col for col in org_tup[10] if not org_tup[10][col]]

    # Getting useful parsing results
    parsing_pub_df, authaddr_df = [dedup_parsing_dict[key]
                                   for key in bm_pg.PARSING_KEYS_DIC['dedup_pub_nb']]

    # Computing the total publications-number
    all_pub_nb = len(parsing_pub_df)
    all_pub_ids = parsing_pub_df[pub_id_col].to_list()

    # Computing the number of articles tagged as of the Institute
    return_tup = _compute_col_pub_number(institute_cols, authaddr_df, all_pub_ids)
    institute_pub_nb, _, _ = return_tup
    return all_pub_nb, institute_pub_nb


def build_and_save_dedup_db_ids(dedup_article_df, parsing_path_dict, dedup_db_infos):
    """Builds and save the list of the database identifiers kept after the deduplication process.

    It is based on the concatenation of the database identifiers through the `concat_dfs` function
    of the same module and the selection of the identifiers kept after the deduplication process.

    Args:
        dedup_article_df (dataframe): The articles data resulting from the deduplication process.
        parsing_path_dict (dict): The full path to the data resulting from all parsing steps.
        dedup_db_infos (list): Parameters for  final saving of deduplication results composed \
        of the Full path to working folder (path), of the data combination type from \
        corpuses databases (str), and of the 4 digits year of the corpus (str).
    Returns:
        (dict): Keyed by database types and valued by number of kept publications for each database type.
    """
    # Setting parameters from globals
    pub_id_col = bm_pg.COL_NAMES['pub_id']
    dbs_ids_col = bm_pg.DB_ID_COLS["all_dbs"]
    source_col = bm_pg.COL_NAMES_BONUS['source']

    # Building the list of identifiers data of each database type
    db_ids_dfs_list = []
    increment = 0
    for db_type in bm_pg.BDD_LIST:
        # Getting the identifiers list for the selected database-type
        db_ids_file = f"{db_type.capitalize()}{bm_pg.IDS_FILE_BASE}"
        db_ids_path = parsing_path_dict[db_type] / Path(db_ids_file)
        db_ids_df = pd.read_excel(db_ids_path)

        if not db_ids_df.empty:
            # Incrementing the Pub_id for the concatenation to align with the deduplication data
            db_ids_df[pub_id_col] = db_ids_df[pub_id_col].apply(lambda x: x + increment)

            # Enhancing the data with the database-type name set in a new column
            db_ids_df[source_col] = db_type

            # Setting the same column name for the database identifiers to allow data concatenation
            db_ids_df.rename({bm_pg.DB_ID_COLS[db_type]: dbs_ids_col}, axis=1, inplace=True)
            db_ids_dfs_list.append(db_ids_df)
            increment += len(db_ids_df)

    # Building the full identifiers data by concatenating the ones of each database type
    all_db_ids_df = concat_dfs(db_ids_dfs_list, dedup=False)

    # Selecting the identifiers data kept after the deduplication process
    pub_ids_list = dedup_article_df[pub_id_col].to_list()
    dedup_db_ids_df = all_db_ids_df[all_db_ids_df[pub_id_col].isin(pub_ids_list)]

    # Saving the resulting identifiers data
    save_db_ids_data(dedup_db_ids_df, parsing_path_dict["dedup"], "dedup", dedup_infos=dedup_db_infos)

    # Computing the number of kept identifiers per database type
    ids_nb_dict = {}
    for db_type in bm_pg.BDD_LIST:
        db_df = dedup_db_ids_df[dedup_db_ids_df[source_col]==db_type]
        ids_nb_dict[db_type] = len(db_df)
    return ids_nb_dict


def convert_parsing_keys_to_bm(bp_parsing_dict):
    parsing_dict = {key: bp_parsing_dict[bm_pg.PARSING_KEYS_CONVERT_DIC[key]]
                    for key in bm_pg.PARSING_KEYS_DIC['all']
                    if bm_pg.PARSING_KEYS_CONVERT_DIC[key] in bp_parsing_dict.keys()}
    return parsing_dict


def revers_parsing_keys_to_bp(parsing_dict):
    bp_parsing_dict = {key: parsing_dict[bm_pg.PARSING_KEYS_REVERT_DIC[key]]
                       for key in bm_pg.PARSING_ITEMS_LIST
                       if bm_pg.PARSING_KEYS_REVERT_DIC[key] in parsing_dict.keys()}
    return bp_parsing_dict


def _set_scopus_cat_info(wf_path):
    """Builds the path to database extractions and the file 
    names ending that are specific to the data type 'datatype'.

    It also sets the folder name of the empty files required for 
    specific data types (ex: using only "WoS" datatype requires 
    empty files for Scopus extractions). 
    To do that, it uses the global 'ARCHI_EXTRACT' defined 
    in the module imported as bm_pg.

    Args:
        wf_path (path): The path to the working folder.
    Returns:
        (tup): (path to database extractions (path), \
        file name ending (str), \
        path to the folder of empty files (path)).
    """
    # Setting useful aliases
    extraction_folder = bm_pg.ARCHI_EXTRACT["root"]
    database_folder = bm_pg.ARCHI_EXTRACT[bm_pg.SCOPUS]["root"]

    # Setting useful paths
    extraction_folder_path = wf_path / Path(extraction_folder)
    database_folder_path = extraction_folder_path / Path(database_folder)
    scopus_cat_folder_path = database_folder_path / Path(bm_pg.ARCHI_EXTRACT["categories"])
    scopus_cat_codes_path = scopus_cat_folder_path / Path(bm_pg.SCOPUS_CAT_CODES)
    scopus_journals_issn_cat_path = scopus_cat_folder_path / Path(bm_pg.SCOPUS_JOURNALS_ISSN_CAT)

    return scopus_cat_codes_path, scopus_journals_issn_cat_path


def rawdata_parsing(rawparse_params, rawdata_path, parsing_path,
                    database, progress_callback=None):

    # Setting parameters values from params_list
    (corpus_year, print_params, datatype, wf_path,
     parse_affil_params_dic, parsing_filenames_dict) = rawparse_params

    print_step_title(f"PARSING OF {database.upper()} DATA FOR {corpus_year}",
                     print_params)

    print_step_text("\nParsing...", print_params)
    scopus_cat_paths = _set_scopus_cat_info(wf_path)
    parsing_tup = bp_biblio_parser(rawdata_path, database, affil_filter_list=None,
                                   affil_params_dic=parse_affil_params_dic,
                                   scopus_cat_paths=scopus_cat_paths)
    bp_parsing_dict, fails_dict, db_ids_df = parsing_tup[0:3]
    parsing_dict = convert_parsing_keys_to_bm(bp_parsing_dict)
    if len(parsing_tup)>3:
        correction_dict = dict(zip(list(bm_pg.RAWDATA_CORRECT.keys()), parsing_tup[3:]))
        save_rawdata_correction(correction_dict, rawdata_path, database)
        print_step_text("  - Data of correction in rawdata of authors and addresses saved for control",
                        print_params)
    pubs_nb = 0
    if fails_dict:
        pubs_nb = fails_dict["number of article"]
    if progress_callback:
        progress_callback(80)

    save_parsing_dict(parsing_dict, parsing_path, parsing_filenames_dict, bm_pg.TSV_SAVE_EXTENT)
    if progress_callback:
        progress_callback(90)

    save_fails_dict(fails_dict, parsing_path)
    save_db_ids_data(db_ids_df, parsing_path, database)
    print_step_text(f"  - Parsing results built and saved for {pubs_nb} publications",
                    print_params)
    if progress_callback:
        progress_callback(95)

    # Building the data for addresses correction by the user
    unknown_countries_empty, all_countries_corrected, correct_files_list = True, True, []
    if database.lower() in datatype.lower():
        correct_params = [database, corpus_year, print_params]
        return_tup = build_and_save_unknown_country_data(parsing_dict, parsing_path,
                                                         bm_pg.UNKNOWN_COUNTRY, correct_params)
        unknown_countries_empty, all_countries_corrected, correct_files_list = return_tup
    raw_parse_tup = (pubs_nb, unknown_countries_empty, all_countries_corrected, correct_files_list)
    return raw_parse_tup


def deduplicate_parsing(dedup_params_list, progress_callback=None):
    (corpus_year, print_params, institute, org_tup, wf_path, datatype,
     dedup_affil_params_dic, parsing_filenames_dict) = dedup_params_list
    base_params_list = [corpus_year, print_params, institute, wf_path,
                        dedup_affil_params_dic, parsing_filenames_dict]

    print_step_title(f"DEDUPLICATION OF PARSINGS FOR {corpus_year}", print_params)

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    _, parsing_path_dict = set_rawdata_and_parsing_paths(wf_path, corpus_year, bm_pg.BDD_LIST)

    # Setting useful paths for corpus deduplication
    scopus_parse_path, wos_parse_path = parsing_path_dict[bm_pg.SCOPUS], parsing_path_dict[bm_pg.WOS]
    concat_path, dedup_path = parsing_path_dict["concat"], parsing_path_dict["dedup"]

    # Setting the Scopus and WoS parsing results before correction
    scopus_parsing_dict = read_parsing_dict(scopus_parse_path, parsing_filenames_dict,
                                            bm_pg.TSV_SAVE_EXTENT)

    wos_parsing_dict = read_parsing_dict(wos_parse_path, parsing_filenames_dict,
                                             bm_pg.TSV_SAVE_EXTENT)

    # Trying to correct the Scopus parsing results
    if bm_pg.SCOPUS.lower() in datatype.lower():
        # Correcting the Scopus parsing results
        scopus_params_list = [bm_pg.SCOPUS] + base_params_list
        correct_status = correct_parsing(scopus_params_list, scopus_parse_path,
                                         scopus_parsing_dict, bm_pg.UNKNOWN_COUNTRY)
        if correct_status:
            scopus_parsing_dict = read_parsing_dict(scopus_parse_path, parsing_filenames_dict,
                                                    bm_pg.TSV_SAVE_EXTENT)
    else:
        # Managing the case of a single database by Linking Scopus parsings
        # to WoS parsings what would be the changes in the WoS parsings
        scopus_parsing_dict = copy.deepcopy(wos_parsing_dict)
        print_step_text("  - Scopus parsing results set to WoS parsing results",
                        print_params)

    # Trying to correct the WoS parsing results
    if bm_pg.WOS.lower() in datatype.lower():
        # Correcting the WoS parsing results
        wos_params_list = [bm_pg.WOS] + base_params_list
        correct_status = correct_parsing(wos_params_list, wos_parse_path,
                                         wos_parsing_dict, bm_pg.UNKNOWN_COUNTRY)
        if correct_status:
            wos_parsing_dict = read_parsing_dict(wos_parse_path, parsing_filenames_dict,
                                                 bm_pg.TSV_SAVE_EXTENT)
    else:
        # Managing the case of a single database by Linking WoS parsings
        # to Scopus parsings what would be the changes in the Scopus parsings
        wos_parsing_dict = copy.deepcopy(scopus_parsing_dict)
        print_step_text("  - WoS parsing results set to Scopus parsing results",
                        print_params)
    if progress_callback:
        progress_callback(15)

    print_step_text("\nConcatenating parsing data...", print_params)
    bp_scopus_parsing_dict = revers_parsing_keys_to_bp(scopus_parsing_dict)
    bp_wos_parsing_dict = revers_parsing_keys_to_bp(wos_parsing_dict)
    if bm_pg.FIRST_BDD==bm_pg.SCOPUS:
        bp_concat_parsing_dict = bp_concatenate_parsing(bp_scopus_parsing_dict, bp_wos_parsing_dict,
                                                        affil_filter_list=org_tup[3])
    else:
        bp_concat_parsing_dict = bp_concatenate_parsing(bp_wos_parsing_dict, bp_scopus_parsing_dict,
                                                        affil_filter_list=org_tup[3])
    concat_parsing_dict = convert_parsing_keys_to_bm(bp_concat_parsing_dict)
    if progress_callback:
        progress_callback(25)

    save_parsing_dict(concat_parsing_dict, concat_path,
                      parsing_filenames_dict, bm_pg.TSV_SAVE_EXTENT)
    print_step_text("  - Parsing data concatenated and saved", print_params)
    if progress_callback:
        progress_callback(30)

    print_step_text("\nDeduplicating parsing data...", print_params)
    bp_dedup_parsing_dict = bp_deduplicate_parsing(bp_concat_parsing_dict, norm_affil_status=False,
                                                   affil_params_dic=dedup_affil_params_dic)

    dedup_parsing_dict = convert_parsing_keys_to_bm(bp_dedup_parsing_dict)
    dedup_pub_nb, dedup_institute_pub_nb = compute_dedup_pub_number(org_tup, dedup_parsing_dict)
    _dedup_infos=(wf_path, datatype, corpus_year)
    pubs_df = dedup_parsing_dict['pub']
    ids_nb_dict = build_and_save_dedup_db_ids(pubs_df, parsing_path_dict, _dedup_infos)
    if progress_callback:
        progress_callback(90)

    save_parsing_dict(dedup_parsing_dict, dedup_path, parsing_filenames_dict, bm_pg.TSV_SAVE_EXTENT,
                      dedup_infos=_dedup_infos)
    step_txt = ("  - All parsing results deduplicated and saved as final results "
                f"for {dedup_pub_nb} publications "
                f"including {dedup_institute_pub_nb} of {institute}"
                "\n  - After deduplication, the number of kept publications from each database are:")
    for db_type, db_nb in ids_nb_dict.items():
        step_txt += f"\n      - {db_nb} for {db_type}"
    print_step_text(step_txt, print_params)
    return dedup_pub_nb, dedup_institute_pub_nb, ids_nb_dict
