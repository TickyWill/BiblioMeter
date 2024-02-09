__all__ = ['create_archi',
           'create_folder',
           'read_parsing_dict',
           'save_fails_dict',
           'save_parsing_dict',
          ]

def create_folder(root_path, folder, verbose = False):
    # Standard library imports
    import os
    from pathlib import Path
    
    folder_path = root_path / Path(folder)
    if not os.path.exists(folder_path): 
        os.makedirs(folder_path)
        message = f"{folder_path} created"
    else:
        message = f"{folder_path} already exists"
    
    if verbose : print(message)
    return folder_path


def create_archi(bibliometer_path, corpus_year_folder, verbose = False):
    '''The `create_archi` function creates a corpus folder with the required architecture.
    It uses the global "ARCHI_YEAR" for the names of the sub_folders.
    
    Args:
        bibliometer_path (path): The full path of the working folder.
        corpus_year_folder (str): The name of the folder of the corpus.
        
    Returns:
        (str): The message giving the folder creation status.
    
    '''
   
    # local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    # Setting useful alias
    archi_alias = pg.ARCHI_YEAR
        
    corpus_year_folder_path = create_folder(bibliometer_path, corpus_year_folder, verbose = verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["bdd mensuelle"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["homonymes folder"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["OTP folder"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["pub list folder"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, archi_alias["history folder"], verbose = verbose)

    analysis_folder = create_folder(corpus_year_folder_path, archi_alias["analyses"], verbose = verbose)
    _ = create_folder(analysis_folder, archi_alias["if analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, archi_alias["keywords analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, archi_alias["subjects analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, archi_alias["countries analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, archi_alias["institutions analysis"], verbose = verbose)

    corpus_folder = create_folder(corpus_year_folder_path, archi_alias["corpus"], verbose = verbose)

    concat_folder = create_folder(corpus_folder, archi_alias["concat"], verbose = verbose)
    _ = create_folder(concat_folder, archi_alias["parsing"], verbose = verbose)

    dedup_folder = create_folder(corpus_folder, archi_alias["dedup"], verbose = verbose)
    _ = create_folder(dedup_folder, archi_alias["parsing"], verbose = verbose)

    scopus_folder = create_folder(corpus_folder, ARCHI_YEAR["scopus"], verbose = verbose)
    _ = create_folder(scopus_folder, archi_alias["parsing"], verbose = verbose)
    _ = create_folder(scopus_folder, archi_alias["rawdata"], verbose = verbose)

    wos_folder = create_folder(corpus_folder, archi_alias["wos"], verbose = verbose)
    _ = create_folder(wos_folder, archi_alias["parsing"], verbose = verbose)
    _ = create_folder(wos_folder, archi_alias["rawdata"], verbose = verbose)
    
    message = f"Architecture created for {corpus_year_folder} folder"
    return message


def save_parsing_dict(parsing_dict, parsing_path, 
                      item_filename_dict, save_extent):
    """
    """
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import BiblioParsing as bp
    
    # Cycling on parsing items 
    for item in bp.PARSING_ITEMS_LIST:
        if item in parsing_dict.keys():
            item_df = parsing_dict[item]
            if save_extent == "xlsx":
                item_xlsx_file = item_filename_dict[item] + ".xlsx"
                item_xlsx_path = parsing_path / Path(item_xlsx_file)
                item_df.to_excel(item_xlsx_path, index = False)
            elif save_extent == "dat":
                item_tsv_file = item_filename_dict[item] + ".dat"
                item_tsv_path = parsing_path / Path(item_tsv_file)
                item_df.to_csv(item_tsv_path, index = False, sep = '\t')
            else:
                item_tsv_file = item_filename_dict[item] + ".csv"
                item_tsv_path = parsing_path / Path(item_tsv_file)
                item_df.to_csv(item_tsv_path, index = False, sep = '\,')
        else:
            pass
        
        
def read_parsing_dict(parsing_path, item_filename_dict, save_extent):
    """
    """
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # 3rd party imports
    import BiblioParsing as bp
    
    parsing_dict = {}
    # Cycling on parsing items 
    for item in bp.PARSING_ITEMS_LIST:
        item_df = None
        if save_extent == "xlsx":
            item_xlsx_file = item_filename_dict[item] + ".xlsx"
            item_xlsx_path = parsing_path / Path(item_xlsx_file)
            if item_xlsx_path.is_file():
                item_df = pd.read_excel(item_xlsx_path)
        elif save_extent == "dat":
            item_tsv_file = item_filename_dict[item] + ".dat"
            item_tsv_path = parsing_path / Path(item_tsv_file)
            if item_tsv_path.is_file():
                item_df = pd.read_csv(item_tsv_path, sep = "\t")
        else:
            pass
        if item_df is not None: parsing_dict[item] = item_df
    return parsing_dict  


def save_fails_dict(fails_dict, parsing_path):
    '''The function `save_fails_dict` saves parsing fails in a json file
    named by the global PARSING_PERF.
    
    Args:
        fails_dict (dict): The dict of parsing fails.
        parsing_path (path): The full path of the parsing results folder 
        where the json file is being saved.
        
    Returns:
        None
        
    '''
    # Standard library imports
    import json
    from pathlib import Path
    
    # local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    with open(parsing_path / Path(pg.PARSING_PERF), 'w') as write_json:
        json.dump(fails_dict, write_json, indent = 4)
