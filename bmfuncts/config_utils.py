"""
"""
__all__ = ['set_org_params',
           'set_user_config', ]


def _get_bm_config():
    # Standard library imports
    import json
    from pathlib import Path

    config_json_file_name = 'BiblioParsing_config.json'

    # Reads the default json_file_name config file
    pck_config_file_path = Path(__file__).parent / Path('ConfigFiles') / Path(config_json_file_name)
    with open(pck_config_file_path) as file:
        config_dict = json.load(file)
    return config_dict


def _build_effective_config(parsing_folder_dict_init, db_list):
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


def _build_files_paths(year, parsing_folder_dict, bibliometer_path, db_list):

    # Standard library imports
    from pathlib import Path

    # Internal functions
    def _get_folder_attributes(parsing_folder_dict, keys_list, folder_root):
        key_dict = parsing_folder_dict
        for key in keys_list:
            key_dict = key_dict[key]
        folder_name = key_dict
        folder_path = folder_root / Path(folder_name)
        return (folder_path, folder_name)

    # Updating 'parsing_folder_dict' using the list of databases 'db_list'
    parsing_folder_dict = _build_effective_config(parsing_folder_dict, db_list)

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
    """

    """
    # Getting the configuration dict
    config_dict = _get_bm_config()

    # Getting the working folder architecture base
    parsing_folder_dict = config_dict['PARSING_FOLDER_ARCHI']

    # getting useful paths of the working folder architecture for a corpus single year "year"
    rawdata_path_dict, parsing_path_dict = _build_files_paths(year, parsing_folder_dict,
                                                              bibliometer_path, db_list)

    # Getting the filenames for each parsing item
    item_filename_dict = config_dict['PARSING_FILE_NAMES']

    return (rawdata_path_dict, parsing_path_dict, item_filename_dict)


def set_org_params(institute, bibliometer_path):
    """

    """
    # Standard library imports
    import json
    from pathlib import Path

    # Local imports
    import bmfuncts.employees_globals as eg
    import bmfuncts.institute_globals as ig

    config_root_path = bibliometer_path / Path(eg.EMPLOYEES_ARCHI["root"])
    config_file_path = config_root_path / Path(ig.CONFIG_JSON_FILES_DICT[institute])
    dpt_label_key = ig.DPT_LABEL_KEY
    dpt_otp_key = ig.DPT_OTP_KEY

    with open(config_file_path) as file:
        inst_org_dict = json.load(file)

    col_names_dpt = inst_org_dict["COL_NAMES_DPT"]
    dpt_label_dict = inst_org_dict["DPT_LABEL_DICT"]
    dpt_otp_dict = inst_org_dict["DPT_OTP_DICT"]
    dpt_attributs_dict = {}
    for dpt in list(col_names_dpt.keys())[:-1]:
        dpt_attributs_dict[dpt] = {}
        dpt_attributs_dict[dpt][dpt_label_key] = dpt_label_dict[dpt]
        dpt_attributs_dict[dpt][dpt_otp_key] = dpt_otp_dict[dpt]

    dpt_attributs_dict['DIR'] = {dpt_label_key: ['(' + institute.upper() + ')'],
                                 dpt_otp_key: list(set(sum([dpt_attributs_dict[dpt_label][dpt_otp_key]
                                                            for dpt_label in dpt_attributs_dict.keys()], []))), }
    for dpt in list(col_names_dpt.keys()):
        dpt_attributs_dict[dpt][dpt_otp_key] += [ig.INVALIDE]

    institutions_filter_list = [tuple(x) for x in inst_org_dict["INSTITUTIONS_FILTER_LIST"]]
    institute_institutions_list = [tuple(x) for x in inst_org_dict["INSTITUTE_INSTITUTIONS_LIST"]]
    inst_col_list = [tup[0] + '_' + tup[1] for tup in institute_institutions_list]
    if_db_status = inst_org_dict["IF_DB_STATUS"]
    no_if_doctype_keys_list = inst_org_dict["NO_IF_DOCTYPE_KEYS_LIST"]

    return_tup = (col_names_dpt, dpt_label_dict, dpt_attributs_dict,
                  institutions_filter_list, inst_col_list,
                  if_db_status, no_if_doctype_keys_list)
    return return_tup
