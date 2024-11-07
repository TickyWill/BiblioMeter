"""The `config_utils.py` module gathers the useful functions 
for setting the configuration parameters for the use of the BiblioMeter application.

"""
__all__ = ['set_org_params',
           'set_user_config', ]


# Standard library imports
import json
from pathlib import Path

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.institute_globals as ig
import bmfuncts.pub_globals as pg


def _get_bm_parsing_config():
    """Reads the json file giving he architecture of the parsing folder 
    and the names of the parsing files.

    The name of this json file is given by the global 'PARSING_CONFIG_FILE' and 
    it is located in the folder of the `bmfuncts` package which name is given 
    by the global 'CONFIG_FOLDER'.
    These globals are defined in the `pub_globals.py` module 
    of the `bmfuncts` package.

    Args:
        None.
    Returns:
        (dict): The dict resulting from the parsing of the json file.
    """
    config_folder_name = pg.CONFIG_FOLDER
    config_json_file_name = pg.PARSING_CONFIG_FILE

    # Reads the json file
    config_folder_path = Path(__file__).parent / Path(config_folder_name)
    config_file_path = config_folder_path / Path(config_json_file_name)
    with open(config_file_path, encoding = 'utf-8') as file:
        config_dict = json.load(file)
    return config_dict


def _build_effective_config(db_list, parsing_folder_dict_init):
    """Sets the parsing-folder architecture common to all the corpus folders 
    taking into account the list of databases 'db_list'.

    Args:
        db_list (list): The list of the database string names.
        parsing_folder_dict_init (hierarchical dict): The architecture of the parsing \
        folder to be used for each database of the database list 'db_list'.
    Returns:
        (hierarchical dict): The hierachical dict giving the architecture \
        of the parsing folder for each database.
    """
    parsing_folder_dict = {}
    parsing_folder_dict['folder_root'] = parsing_folder_dict_init['folder_root']
    parsing_folder_dict['corpus'] = {}
    parsing_folder_dict['corpus']['corpus_root'] = parsing_folder_dict_init['corpus']['corpus_root']
    parsing_folder_dict['corpus']['concat'] = parsing_folder_dict_init['corpus']['concat']
    parsing_folder_dict['corpus']['dedup'] = parsing_folder_dict_init['corpus']['dedup']
    parsing_folder_dict['corpus']['databases'] = {}
    for db_num, db_label in enumerate(db_list):
        parsing_folder_dict['corpus']['databases'][str(db_num)] = {}
        parsing_folder_dict['corpus']['databases'][str(db_num)]['root'] = db_label
        rawdata_folder_name = parsing_folder_dict_init['corpus']['database']['rawdata']
        parsing_folder_dict['corpus']['databases'][str(db_num)]['rawdata'] = rawdata_folder_name
        parsing_folder_name = parsing_folder_dict_init['corpus']['database']['parsing']
        parsing_folder_dict['corpus']['databases'][str(db_num)]['parsing'] = parsing_folder_name
    return parsing_folder_dict


def _build_files_paths(bibliometer_path, year, db_list, parsing_folder_dict):
    """Sets the full paths to the rawdata folders and to the parsing folders.

    This is done for the working folder selected by the user, 
    the corpus year 'year' and for each database in the list 'db_list'.
    For that, it uses the `_build_effective_config` function of the same module.

    Args:
        bibliometer_path (path): The full path to the working folder.
        year (str): The name of the corpus folder defined by 4 digits \
        corresponding to the corpus year.
        db_list (list): The list of the database string names.
        parsing_folder_dict (hierachical dict): The architecture of the parsing folder \
        used to set the full paths.
    Returns:
        (tup of dicts): A tuple of two hierarchical dicts, the first giving the rawdata \
        full paths for each database and the second, the parsing full \
        paths for each parsing step and for each database.
    """

    # Internal functions
    def _get_folder_attributes(parsing_folder_dict, keys_list, folder_root):
        key_dict = parsing_folder_dict
        for key in keys_list:
            key_dict = key_dict[key]
        folder_name = key_dict
        folder_path = folder_root / Path(folder_name)
        return (folder_path, folder_name)

    # Updating 'parsing_folder_dict' using the list of databases 'db_list'
    parsing_folder_dict = _build_effective_config(db_list, parsing_folder_dict)

    # Getting the year folder attributes
    year_files_path = bibliometer_path / Path(str(year))

    # Getting the corpuses folder attributes
    keys_list = ['corpus', 'corpus_root']
    corpus_folder_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                   keys_list, year_files_path)

    rawdata_path_dict = {}
    parsing_path_dict = {}
    # Getting the databases folders attributes
    for db_num in list(parsing_folder_dict['corpus']['databases'].keys()):

        keys_list = ['corpus', 'databases', db_num, 'root']
        db_root_path, db_root_name = _get_folder_attributes(parsing_folder_dict,
                                                            keys_list,
                                                            corpus_folder_path)

        keys_list = ['corpus', 'databases', db_num, 'rawdata']
        db_rawdata_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                    keys_list, db_root_path)
        rawdata_path_dict[db_root_name] = db_rawdata_path

        keys_list = ['corpus', 'databases', db_num, 'parsing']
        db_parsing_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                    keys_list, db_root_path)
        parsing_path_dict[db_root_name] = db_parsing_path

    # Getting the concatenation folders attributes
    keys_list = ['corpus', 'concat', 'root']
    concat_root_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                 keys_list, corpus_folder_path)
    parsing_path_dict['concat_root'] = concat_root_path

    keys_list = ['corpus', 'concat', 'parsing']
    concat_parsing_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                    keys_list, concat_root_path)
    parsing_path_dict['concat'] = concat_parsing_path

    # Getting the deduplication folders attributes
    keys_list = ['corpus', 'dedup', 'root']
    dedup_root_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                keys_list, corpus_folder_path)
    parsing_path_dict['dedup_root'] = dedup_root_path

    keys_list = ['corpus', 'dedup', 'parsing']
    dedup_parsing_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                   keys_list, dedup_root_path)
    parsing_path_dict['dedup'] = dedup_parsing_path

    return (rawdata_path_dict, parsing_path_dict)


def set_user_config(bibliometer_path, year, db_list):
    """Sets the full paths to the rawdata folders and to the parsing folders.

    This is done for the working folder selected by the user, 
    the corpus year 'year' and for each database in the list 'db_list'.
    It also sets the names of the parsing file for each parsed item. 
    For that, it uses the configuration dict returned by the `_get_bm_parsing_config` 
    function and the `_build_files_paths` function of the same module.
    The set parameters are returned in a tuple as follows:

    - index 1 = the hierarchical dict giving the rawdata full paths (path) for each database.
    - index 2 = the hierarchical dict giving the parsing full paths (path) for each parsing step \
    and for each database.
    - index 3 = the dict giving the name of the parsing file for each parsed item.

    Args:
        bibliometer_path (path): The full path to the working folder.
        year (str): The name of the corpus folder defined by 4 digits \
        corresponding to the corpus year.
        db_list (list): The list of the database string names.
    Returns:
        (tup of dicts): A tuple of the 3 set parameters.
    """
    # Getting the configuration dict
    config_dict = _get_bm_parsing_config()

    # Getting the working folder architecture base
    parsing_folder_dict = config_dict['PARSING_FOLDER_ARCHI']

    # getting useful paths of the working folder architecture for a corpus single year "year"
    rawdata_path_dict, parsing_path_dict = _build_files_paths(bibliometer_path, year, db_list,
                                                              parsing_folder_dict)

    # Getting the filenames for each parsing item
    item_filename_dict = config_dict['PARSING_FILE_NAMES']

    return (rawdata_path_dict, parsing_path_dict, item_filename_dict)


def _get_insitute_config(institute, bibliometer_path):
    """Reads the json file giving the parameters of the organization 
    structure for the Institute.

    The name of this json file is given by the global 'CONFIG_JSON_FILES_DICT' 
    and it is located in the folder of the working folder which name is given 
    by the global 'EMPLOYEES_ARCHI' at key "root".
    The global 'CONFIG_JSON_FILES_DICT' is defined in the `institute_globals.py` 
    module of the `bmfuncts` package.
    The global 'EMPLOYEES_ARCHI' is defined in the `employees_globals.py` module 
    of the `bmfuncts` package.

Args:
        institute (str): The Intitute name.
        bibliometer_path (path): The full path to the working folder.
    Returns:
        (dict): The dict resulting from the parsing of the json file.
    """
    config_root_path = bibliometer_path / Path(eg.EMPLOYEES_ARCHI["root"])
    config_file_path = config_root_path / Path(ig.CONFIG_JSON_FILES_DICT[institute])

    # Reads the json_file
    with open(config_file_path, encoding = 'utf-8') as file:
        inst_org_dict = json.load(file)
    return inst_org_dict


def set_org_params(institute, bibliometer_path):
    """Sets the parameters of the organization structure for the Institute.

    For that, it uses the configuration dict returned by the `_get_insitute_config` 
    function of the same module. The set parameters are returned in a tuple as follows:

    - index 0 = the dict giving the column name (str) for each department (str).
    - index 1 = the dict giving the list of historical labels (str) for each department (str).
    - index 2 = the dict giving the list of attributes (OTPs, str) for each department (str).
    - index 3 = the list of tuples giving the potential labels (str) of the Institute \
    in the authors affiliations associated with the country (str) that will be used to filter \
    the authors affiliated to the Institute:
        ex: [("LITEN","France"), ("INES","France")].
    - index 4 = the list of columns names (str) that will be used for each of the potential labels \
    of the Institute filtering the authors affiliated to the Institute.
    - index 5 = the status (bool) of the impact factors database:
        - True, if the database specific to the Institute will be used; 
        - False, if a general database will be used.
    - index 6 = the list of document types (str) for which the impact factors will not be analysed.
    - index 7 = the index of the main institution among the tuples at index 3.
    - index 8 = the status of the combination of the tuples at index 3.
    - index 9 = the status of splitting the file of list of publications with one row per author \
    that has not been identified as Institute employee.
    - index 10 = the status of droping particular affiliation authors in the file of list of \
    publications with one row per author that has not been identified as Institute employee.

    Args:
        institute (str): The Intitute name.
        bibliometer_path (path): The full path to the working folder.
    Returns:
        (tup): A tuple of the 9 set parameters. 
    """

    config_root_path = bibliometer_path / Path(eg.EMPLOYEES_ARCHI["root"])
    config_file_path = config_root_path / Path(ig.CONFIG_JSON_FILES_DICT[institute])
    dpt_label_key = ig.DPT_LABEL_KEY
    dpt_otp_key = ig.DPT_OTP_KEY

    with open(config_file_path, encoding = 'utf-8') as file:
        inst_org_dict = json.load(file)

    col_names_dpt = inst_org_dict["COL_NAMES_DPT"]
    dpt_label_dict = inst_org_dict["DPT_LABEL_DICT"]
    dpt_otp_dict = inst_org_dict["DPT_OTP_DICT"]
    dpt_attributes_dict = {}
    for dpt in list(col_names_dpt.keys())[:-1]:
        dpt_attributes_dict[dpt] = {}
        dpt_attributes_dict[dpt][dpt_label_key] = dpt_label_dict[dpt]
        dpt_attributes_dict[dpt][dpt_otp_key] = dpt_otp_dict[dpt]

    dpt_otp_list = list(set(sum([dpt_otp_df[dpt_otp_key]
                                 for _, dpt_otp_df in dpt_attributes_dict.items()], [])))
    dpt_attributes_dict['DIR'] = {dpt_label_key: ['(' + institute.upper() + ')'],
                                 dpt_otp_key  : dpt_otp_list}
    for dpt in list(col_names_dpt.keys()):
        dpt_attributes_dict[dpt][dpt_otp_key] += [ig.INVALIDE]

    institutions_filter_list = [tuple(x) for x in inst_org_dict["INSTITUTIONS_FILTER_LIST"]]
    inst_col_list = [tup[1] for tup in institutions_filter_list]
    main_inst_idx = inst_org_dict["MAIN_INSTITUTION_IDX"]
    and_inst_status = inst_org_dict["MAIN_INSTITUTION_STATUS"]
    if_db_status = inst_org_dict["IF_DB_STATUS"]
    no_if_doctype_keys_list = inst_org_dict["NO_IF_DOCTYPE_KEYS_LIST"]
    orphan_split_status = inst_org_dict["ORPHAN_SPLIT_STATUS"]
    affil_drop_dict = inst_org_dict["AFFIL_DROP_DICT"]
    orphan_drop_dict = dict(zip(inst_col_list, affil_drop_dict.values()))

    return_tup = (col_names_dpt, dpt_label_dict, dpt_attributes_dict,
                  institutions_filter_list, inst_col_list,
                  if_db_status, no_if_doctype_keys_list,
                  main_inst_idx, and_inst_status, orphan_split_status,
                  orphan_drop_dict)
    return return_tup
