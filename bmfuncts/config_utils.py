"""The `config_utils.py` module gathers the useful functions 
for setting the configuration parameters for the use of the BiblioMeter application.

"""
__all__ = ['set_affil_params',
           'set_org_params',
           'set_parsing_items_params',
           'set_rawdata_and_parsing_paths',
          ]


# Standard library imports
import json
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp

# Local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg


def _get_bm_parsing_config():
    """Reads the JSON file giving the architecture of the parsing folder
    and the names of the parsing files.

    The name of this JSON file is given by the global 'PARSING_CONFIG_FILE' and
    it is located in the folder of the `bmfuncts` package which name is given 
    by the global 'CONFIG_FOLDER'.
    These globals are defined in the `pub_globals.py` module 
    of the `bmfuncts` package.

    Returns:
        (dict): The dict resulting from the parsing of the JSON file.
    """
    config_folder_name = bm_pg.CONFIG_FOLDER
    config_json_file_name = bm_pg.PARSING_CONFIG_FILE

    # Reading the JSON file
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
        (hierarchical dict): The hierarchical dict giving the architecture \
        of the parsing folder for each database.
    """
    parsing_folder_dict = {'folder_root': parsing_folder_dict_init['folder_root'], 'corpus': {}}
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


def _get_folder_attributes(parsing_folder_dict, keys_list, folder_root):
    key_dict = parsing_folder_dict
    for key in keys_list:
        key_dict = key_dict[key]
    folder_name = key_dict
    folder_path = folder_root / Path(folder_name)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return folder_path, folder_name


def set_rawdata_and_parsing_paths(wf_path, year, db_list):
    """Sets the full paths to the rawdata folders and to the parsing folders.

    This is done for the working folder selected by the user, 
    the corpus year 'year' and for each database in the list 'db_list'.
    For that, it uses the `_build_effective_config` function of the same module.

    Args:
        wf_path (path): The full path to the working folder.
        year (str): The name of the corpus folder defined by 4 digits \
        corresponding to the corpus year.
        db_list (list): The list of the database string names.
    Returns:
        (tup of dicts): A tuple of two hierarchical dicts, the first giving the rawdata \
        full paths for each database and the second, the parsing full \
        paths for each parsing step and for each database.
    """
    # Setting the working folder architecture base
    config_dict = _get_bm_parsing_config()
    parsing_folder_dict = config_dict['PARSING_FOLDER_ARCHI']

    # Updating 'parsing_folder_dict' using the list of databases 'db_list'
    parsing_folder_dict = _build_effective_config(db_list, parsing_folder_dict)

    # Getting the year folder attributes
    year_files_path = wf_path / Path(str(year))

    # Getting the corpuses folder attributes
    keys_list = ['corpus', 'corpus_root']
    corpus_folder_path, _ = _get_folder_attributes(parsing_folder_dict,
                                                   keys_list, year_files_path)

    rawdata_path_dict, parsing_path_dict = {}, {}
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

    return rawdata_path_dict, parsing_path_dict



def set_parsing_items_params():
    """ Sets the names of the parsing file for each parsed item.

    It also sets two lists of keys:
    - keys of parsing items for building data of addresses with unknown-country;
    - keys of parsing items to be corrected through authors' addresses correction.
    For that, it uses the configuration dict returned by the `_get_bm_parsing_config` 
    internal function. 
    The built data are returned in a tuple as follows:
    - index 1 = the dict giving the name of the parsing file for each parsed item.
    - index 2 = the list of keys of parsing items for building data of addresses with unknown-country.
    - index 3 = the list of keys of parsing items to be corrected through authors' addresses correction.

    Returns:
        (dict): The dict giving the name of the parsing file for each parsed item.
    """
    # Getting the configuration dict
    config_dict = _get_bm_parsing_config()

    # Setting the filenames for each parsing item
    config_parsing_filenames_dict = config_dict['PARSING_FILE_NAMES']
    parsing_filenames_dict = {key: config_parsing_filenames_dict[bm_pg.PARSING_KEYS_CONVERT_DIC[key]]
                              for key in bm_pg.PARSING_KEYS_DIC['all']}

#    # Setting the list of keys of parsing items for merge of publications list
#    # with employees data
#    merge_employees_items_keys = config_dict['MERGE_EMPLOYEES_PARSING_ITEMS']
#
#    # Setting the list of keys of parsing items for building data of addresses
#    # with unknown-country
#    unknown_countries_items_keys = config_dict['UNKNOWN_COUNTRIES_PARSING_ITEMS']
#
#    # Setting the list of keys of parsing items to be corrected
#    correction_items_keys = config_dict['CORRECTION_PARSING_ITEMS']
#
#    parsing_items_params = (item_filename_dict, merge_employees_items_keys,
#                            unknown_countries_items_keys, correction_items_keys)
    return parsing_filenames_dict


def _get_institute_config(institute, wf_path):
    """Reads the JSON file giving the parameters of the organization
    structure for the Institute.

    The name of this JSON file is given by the global 'CONFIG_JSON_FILES_DICT'
    and it is located in the folder of the working folder which name is given 
    by the global 'EMPLOYEES_ARCHI' at key "root".
    The global 'CONFIG_JSON_FILES_DICT' is defined in the `institute_globals.py` 
    module of the `bmfuncts` package.
    The global 'EMPLOYEES_ARCHI' is defined in the `employees_globals.py` module 
    of the `bmfuncts` package.

Args:
        institute (str): The Institute's name.
        wf_path (path): The full path to the working folder.
    Returns:
        (dict): The dict resulting from the parsing of the JSON file.
    """
    config_root_path = wf_path / Path(bm_eg.EMPLOYEES_ARCHI["root"])
    config_file_path = config_root_path / Path(bm_ig.CONFIG_JSON_FILES_DICT[institute])

    # Reads the JSON file
    with open(config_file_path, encoding = 'utf-8') as file:
        institute_org_dict = json.load(file)
    return institute_org_dict


def set_org_params(institute, wf_path):
    """Sets the parameters of the organization structure for the Institute.

    For that, it uses the configuration dict returned by the `_get_institute_config`
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
    - index 6 = the list of document types (str) for which the impact factors are not analyzed.
    - index 7 = the index of the main institution among the tuples at index 3.
    - index 8 = the status of the combination of the tuples at index 3.
    - index 9 = the status of splitting the file of list of publications with one row per author \
    that has not been identified as Institute employee.
    - index 10 = the status of dropping particular affiliation authors in the file of list of \
    publications with one row per author that has not been identified as Institute employee.
    - index 11 = the level at which the OTPs are predefined before final set by the user.
    - index 12 = the name of the database file of OTPs per department, service and labs.
    - index 13 = the name of the sheet to be read in the database file of OTPs.
    - index 14 = the lines number of the header in the database file of OTPs.
    - index 15 = the column names to be read in the database file of OTPs.
    - index 16 = the list of departments that have not lab-OTPs available.

    Args:
        institute (str): The Institute's name.
        wf_path (path): The full path to the working folder.
    Returns:
        (tup): A tuple of the 9 set parameters.
    """
    institute_org_dict = _get_institute_config(institute, wf_path)
    dpt_label_key = bm_ig.DPT_LABEL_KEY
    dpt_otp_key = bm_ig.DPT_OTP_KEY

    col_names_dpt = institute_org_dict["COL_NAMES_DPT"]
    dpt_label_dict = institute_org_dict["DPT_LABEL_DICT"]
    dpt_otp_dict = institute_org_dict["DPT_OTP_DICT"]
    dpt_attributes_dict = {}
    for dpt in list(col_names_dpt.keys())[:-1]:
        dpt_attributes_dict[dpt] = {}
        dpt_attributes_dict[dpt][dpt_label_key] = dpt_label_dict[dpt]
        dpt_attributes_dict[dpt][dpt_otp_key] = dpt_otp_dict[dpt]

    dpt_otp_list = list(set(sum([dpt_otp_df[dpt_otp_key]
                                 for _, dpt_otp_df in dpt_attributes_dict.items()], [])))
    dpt_attributes_dict['DIR'] = {dpt_label_key: dpt_label_dict['DIR'],
                                 dpt_otp_key  : dpt_otp_list}
    for dpt in list(col_names_dpt.keys()):
        dpt_attributes_dict[dpt][dpt_otp_key] += [bm_ig.INVALIDE]

    institutions_filter_list = [tuple(x) for x in institute_org_dict["INSTITUTIONS_FILTER_LIST"]]
    institute_cols_list = [tup[1] for tup in institutions_filter_list]
    institute_main_idx = institute_org_dict["MAIN_INSTITUTION_IDX"]
    and_institute_status = institute_org_dict["MAIN_INSTITUTION_STATUS"]
    if_db_status = institute_org_dict["IF_DB_STATUS"]
    no_if_doctype_keys_list = institute_org_dict["NO_IF_DOCTYPE_KEYS_LIST"]
    orphan_split_status = institute_org_dict["ORPHAN_SPLIT_STATUS"]
    affil_drop_dict = institute_org_dict["AFFIL_DROP_DICT"]
    orphan_drop_dict = dict(zip(institute_cols_list, affil_drop_dict.values()))
    otps_level = institute_org_dict["OTPS_LEVEL"]
    lab_otps_bdd = institute_org_dict["LAB_OTPS_BDD"]
    otps_sheet = institute_org_dict["OTPS_SHEET"]
    otps_header = institute_org_dict["OTPS_HEADER"]
    otps_cols = institute_org_dict["OTPS_COL"]
    nolab_depts = institute_org_dict["NO_LAB_DEPTS"]

    return_tup = (col_names_dpt, dpt_label_dict, dpt_attributes_dict,
                  institutions_filter_list, institute_cols_list,
                  if_db_status, no_if_doctype_keys_list,
                  institute_main_idx, and_institute_status, orphan_split_status,
                  orphan_drop_dict, otps_level, lab_otps_bdd,
                  otps_sheet, otps_header, otps_cols, nolab_depts)
    return return_tup


def _build_institute_file_name(institute, file_base):
    file = institute + "_" + file_base
    return file


def _set_institute_affil_params(wf_path, institute):
    # Setting user's affiliations root path
    affils_rep_utils = wf_path / Path(bm_pg.ARCHI_INSTITUTIONS['root'])

    # Setting user's affiliations-parsing files
    affil_files_keys = [x[:-5] + "_file" for x in list(bm_pg.ARCHI_INSTITUTIONS.keys())[1:]]
    affil_file_base_values = list(bm_pg.ARCHI_INSTITUTIONS.values())[1:]
    institute_affil_files_values = [_build_institute_file_name(institute, v) for v in affil_file_base_values]
    institute_affil_files_dic = dict(zip(affil_files_keys, institute_affil_files_values))

    return affils_rep_utils, institute_affil_files_dic


def set_affil_params(institute, wf_path):
    """Sets paths to Institute's files to use for authors' affiliations parsing.

    Args:
        institute (str): The Institute's name.
        wf_path (path): The full path to the working folder.
    Returns:
        (tup): Composed of the dict giving the full paths to the Institute's files to use for \
        affiliations parsing of Institute's authors at rawdata-parsing step, \
        of the dict giving the full paths to the Institute's files to use for \
        authors' affiliations parsing at parsing deduplication step and \
        of the dict giving the full paths to the Institute's complementary-files \
        to use for authors' affiliations parsing at coupling analysis step.
    """
    affils_rep_utils, institute_affil_files_dic = _set_institute_affil_params(wf_path, institute)

    # Setting the filename for the affiliations-per-country data for parsings deduplication step
    dedup_norm_affil_file = institute_affil_files_dic['affiliations_file']
    parse_norm_affil_file = institute_affil_files_dic['institute_affil_file']

    # Setting user's affiliations-parsing paths
    affil_types_file_path = affils_rep_utils / Path(institute_affil_files_dic['inst_types_file'])
    dedup_affils_file_path = affils_rep_utils / Path(institute_affil_files_dic['affiliations_file'])
    parse_affils_file_path = affils_rep_utils / Path(institute_affil_files_dic['institute_affil_file'])
    unkept_affils_file_path = affils_rep_utils / Path(institute_affil_files_dic['unkept_affil_file'])

    sub_affil_params_dic = {'affil_types_file_path'    : affil_types_file_path,
                            'country_towns_folder_path': affils_rep_utils,
                            'country_towns_file'       : institute_affil_files_dic['country_towns_file'],
                           }
    dedup_affil_params_dic = sub_affil_params_dic.copy()
    dedup_affil_params_dic['country_affils_file_path'] = dedup_affils_file_path
    parse_affil_params_dic = sub_affil_params_dic.copy()
    parse_affil_params_dic['country_affils_file_path'] = parse_affils_file_path
    co_affil_param_dic = {'unkept_affils_file_path': unkept_affils_file_path}
    return parse_affil_params_dic, dedup_affil_params_dic, co_affil_param_dic
