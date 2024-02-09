'''
'''
__all__ = ['set_user_config',
          ]

def _get_bm_config():
    # Standard library imports
    import json
    from pathlib import Path
    
    config_json_file_name = 'BiblioParsing_config.json'
    
    # Reads the default json_file_name config file
    pck_config_file_path = Path(__file__).parent / Path('ConfigFile') / Path(config_json_file_name)
    with open(pck_config_file_path) as file:
        config_dict = json.load(file)       

    return config_dict

def _build_effective_config(parsing_folder_dict, db_list):
    parsing_folder_dict_init = parsing_folder_dict
    parsing_folder_dict = {}
    parsing_folder_dict['folder_root'] = parsing_folder_dict_init['folder_root']
    parsing_folder_dict['corpus'] = {}
    parsing_folder_dict['corpus']['corpus_root'] = parsing_folder_dict_init['corpus']['corpus_root']
    parsing_folder_dict['corpus']['concat'] = parsing_folder_dict_init['corpus']['concat']
    parsing_folder_dict['corpus']['dedup'] = parsing_folder_dict_init['corpus']['dedup']
    parsing_folder_dict['corpus']['databases'] = {}
    for db_num, db_label in enumerate(db_list):
        parsing_folder_dict['corpus']['databases'][str(db_num)]= {}
        parsing_folder_dict['corpus']['databases'][str(db_num)]['root'] = db_label
        rawdata_folder_name = parsing_folder_dict_init['corpus']['database']['rawdata']
        parsing_folder_dict['corpus']['databases'][str(db_num)]['rawdata'] = rawdata_folder_name
        parsing_folder_name = parsing_folder_dict_init['corpus']['database']['parsing']
        parsing_folder_dict['corpus']['databases'][str(db_num)]['parsing'] = parsing_folder_name    

    return parsing_folder_dict


def _build_files_paths(year, parsing_folder_dict, BiblioMeter_path, db_list):
    
    # Standard library imports
    from pathlib import Path
    
    # Internal functions
    def _get_folder_attributes(parsing_folder_dict, keys_list, folder_root):
        key_dict = parsing_folder_dict
        for key in keys_list: key_dict = key_dict[key]
        folder_name = key_dict
        folder_path = folder_root / Path(folder_name)
        return (folder_path, folder_name)
    
    # Updating 'parsing_folder_dict' using the list of databases 'db_list'
    parsing_folder_dict = _build_effective_config(parsing_folder_dict, db_list)
        
    # Getting the year folder attributes
    year_files_path = BiblioMeter_path / Path(str(year))
    
    # Getting the corpuses folder attributes
    keys_list = ['corpus', 'corpus_root']
    corpus_folder_path,_ = _get_folder_attributes(parsing_folder_dict, keys_list, year_files_path)
    
    rawdata_path_dict = {}
    parsing_path_dict = {}
    # Getting the databases folders attributes
    for db_num in list(parsing_folder_dict['corpus']['databases'].keys()):          
        
        keys_list = ['corpus', 'databases', db_num, 'root']
        db_root_path, db_root_name = _get_folder_attributes(parsing_folder_dict, keys_list, corpus_folder_path)
        
        keys_list = ['corpus', 'databases', db_num, 'rawdata']
        db_rawdata_path, _ = _get_folder_attributes(parsing_folder_dict, keys_list, db_root_path)
        rawdata_path_dict[db_root_name] = db_rawdata_path
        
        keys_list = ['corpus', 'databases', db_num, 'parsing']
        db_parsing_path, _ = _get_folder_attributes(parsing_folder_dict, keys_list, db_root_path)
        parsing_path_dict[db_root_name] = db_parsing_path
            
    # Creating the concatenation folder if not available    
    keys_list = ['corpus', 'concat', 'root']
    concat_root_path, concat_root_name = _get_folder_attributes(parsing_folder_dict, keys_list, corpus_folder_path)
    
    keys_list = ['corpus', 'concat', 'parsing']
    concat_parsing_path, _ = _get_folder_attributes(parsing_folder_dict, keys_list, concat_root_path)
    parsing_path_dict['concat'] = concat_parsing_path   
    
    # Creating the deduplication folder if not available
    keys_list = ['corpus', 'dedup', 'root']
    dedup_root_path, dedup_root_name = _get_folder_attributes(parsing_folder_dict, keys_list, corpus_folder_path)
    
    keys_list = ['corpus', 'dedup', 'parsing']
    dedup_parsing_path, _ = _get_folder_attributes(parsing_folder_dict, keys_list, dedup_root_path)
    parsing_path_dict['dedup'] = dedup_parsing_path       
    
    return (rawdata_path_dict, parsing_path_dict)


def set_user_config(bibliometer_path, year, db_list):
    '''
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # Getting the configuration dict
    config_dict = _get_bm_config()
    
    # Getting the working folder architecture base
    parsing_folder_dict = config_dict['PARSING_FOLDER_ARCHI']

    # getting useful paths of the working folder architecture for a corpus single year "year"
    rawdata_path_dict, parsing_path_dict = _build_files_paths(year, parsing_folder_dict, bibliometer_path, db_list)
        
    # Getting the filenames for each parsing item
    item_filename_dict = config_dict['PARSING_FILE_NAMES']    

    return (rawdata_path_dict, parsing_path_dict, item_filename_dict)