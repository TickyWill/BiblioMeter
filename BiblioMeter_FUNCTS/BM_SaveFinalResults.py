__all__ = ['save_final_countries',
           'save_final_ifs',
           'save_final_kws',
           'save_final_pub_lists',
           'save_final_results',
          ]

def save_final_pub_lists(institute, org_tup, bibliometer_path, 
                         corpus_year, results_folder_path): 
    """
    
    """
    # Standard library imports
    import os
    from pathlib import Path

    # 3rd party import
    import pandas as pd

    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg 
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import mise_en_page
    
    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["pub-lists"]
    
    # Setting aliases of common parts of file names
    origin_pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias     = pg.ARCHI_YEAR["pub list file name base"]
    year_pub_list_file_alias     = pub_list_file_base_alias + " " + corpus_year
    
    # Setting common paths
    origin_corpus_year_path = bibliometer_path / Path(corpus_year)                  
    origin_pub_list_path    = origin_corpus_year_path / Path(origin_pub_list_folder_alias)
    year_target_folder_path = results_folder_path / Path(corpus_year)
    target_pub_list_path    = year_target_folder_path / Path(results_sub_folder_alias)  
    
    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path): os.makedirs(year_target_folder_path)
    if not os.path.exists(target_pub_list_path): os.makedirs(target_pub_list_path)
    
    # Setting origin and target file paths
    origin_paths_dict = {}
    target_paths_dict = {}
    
    full_pub_list_file_alias =  year_pub_list_file_alias + ".xlsx"    
    origin_paths_dict["Full"] = origin_pub_list_path / Path(full_pub_list_file_alias)
    target_paths_dict["Full"] = target_pub_list_path / Path(full_pub_list_file_alias)
    
    for key, doctype_list in pg.DOCTYPE_TO_SAVE_DICT.items():
        key_pub_list_file_alias = year_pub_list_file_alias + "_" + key + ".xlsx"
        origin_paths_dict[key] = origin_pub_list_path / Path(key_pub_list_file_alias)
        target_paths_dict[key] = target_pub_list_path / Path(key_pub_list_file_alias)

    other_pub_list_file_alias = year_pub_list_file_alias + "_Others.xlsx"
    origin_paths_dict["Others"] = origin_pub_list_path / Path(other_pub_list_file_alias)
    target_paths_dict["Others"] = target_pub_list_path / Path(other_pub_list_file_alias)
    
    for key in origin_paths_dict.keys():
        # Get "key_df" from EXCEL file at full path 'origin_paths_dict[key]'
        key_df = pd.read_excel(origin_paths_dict[key])

        # Saving 'key_df' as EXCEL file at full path 'target_paths_dict[key]'
        wb, _ = mise_en_page(institute, org_tup, key_df)
        wb.save(target_paths_dict[key])

    end_message = f"Final publications lists for year {corpus_year} saved in folder: \n  '{target_pub_list_path}'"
    return end_message

def save_final_ifs(institute, org_tup, bibliometer_path, 
                   corpus_year, results_folder_path, if_analysis_name): 
    """    
    """
    # Standard library imports
    import os
    from pathlib import Path

    # 3rd party import
    import pandas as pd

    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import format_df_4_excel
    from BiblioMeter_FUNCTS.BM_RenameCols import set_final_col_names
    
    # Setting useful column names aliases
    col_final_list = set_final_col_names(institute, org_tup)
    depts_col_list = col_final_list[11:16]
    
    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["impact-factors"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    origin_ifs_folder_alias      = pg.ARCHI_YEAR["if analysis"]
    ifs_file_base_alias          = f'{if_analysis_name}'
    
    # Setting common paths
    origin_corpus_year_path     = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_ifs_folder_path      = origin_analysis_folder_path / Path(origin_ifs_folder_alias)
    year_target_folder_path     = results_folder_path / Path(corpus_year)
    target_ifs_folder_path      = year_target_folder_path / Path(results_sub_folder_alias) 
    
    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path): os.makedirs(year_target_folder_path)
    if not os.path.exists(target_ifs_folder_path): os.makedirs(target_ifs_folder_path)
            
    for dept in [institute] + depts_col_list:
        
        # Setting origin and target file paths
        dept_file_name = ifs_file_base_alias + f'-{dept}' + '.xlsx'
        origin_dept_file_path = Path(origin_ifs_folder_path) / Path(dept_file_name)
        target_dept_file_path = Path(target_ifs_folder_path) / Path(dept_file_name)
        
        # Get "dept_df" from EXCEL file at full path 'origin_dept_file_path'
        dept_df = pd.read_excel(origin_dept_file_path)

        # Saving 'dept_df' as EXCEL file at full path 'target_dept_file_path'
        first_col_width = 50
        wb, ws = format_df_4_excel(dept_df, first_col_width)
        ws.title = dept + ' IFs '
        wb.save(target_dept_file_path) 
        
    end_message = f"Final impact factors for year {corpus_year} saved in folder: \n  '{target_dept_file_path}'"
    return end_message

def save_final_kws(institute, org_tup, bibliometer_path, 
                   corpus_year, results_folder_path): 
    """
    
    """
    # Standard library imports
    import os
    from pathlib import Path

    # 3rd party imports
    import BiblioParsing as bp
    import pandas as pd

    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import format_df_4_excel
    from BiblioMeter_FUNCTS.BM_RenameCols import set_final_col_names
    
    # Setting useful column names aliases
    col_final_list = set_final_col_names(institute, org_tup)
    depts_col_list = col_final_list[11:16]
    
    # Setting useful aliases
    auth_kw_item_alias  = bp.PARSING_ITEMS_LIST[6]
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
    origin_kws_folder_alias      = pg.ARCHI_YEAR["keywords analysis"]
    
    # Setting common paths
    origin_corpus_year_path     = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_kws_folder_path      = origin_analysis_folder_path / Path(origin_kws_folder_alias)
    year_target_folder_path     = results_folder_path / Path(corpus_year)
    target_kws_folder_path      = year_target_folder_path / Path(results_sub_folder_alias) 
    
    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path): os.makedirs(year_target_folder_path)
    if not os.path.exists(target_kws_folder_path): os.makedirs(target_kws_folder_path)
            
    for dept in [institute] + depts_col_list:
        for kw_type, kw_item_alias in kw_item_alias_dict.items():
            # Setting origin and target file paths
            dept_file_name = f'{dept} {corpus_year}-{kw_type}.xlsx'
            origin_dept_file_path = Path(origin_kws_folder_path) / Path(dept_file_name)
            target_dept_file_path = Path(target_kws_folder_path) / Path(dept_file_name)

            # Get "dept_df" from EXCEL file at full path 'origin_dept_file_path'
            dept_df = pd.read_excel(origin_dept_file_path)

            # Saving 'dept_df' as EXCEL file at full path 'target_dept_file_path'
            first_col_width = 50
            wb, ws = format_df_4_excel(dept_df, first_col_width)
            ws.title = dept + ' ' + kw_type
            wb.save(target_dept_file_path) 
        
    end_message = f"Final keywords for year {corpus_year} saved in folder: \n  '{target_kws_folder_path}'"
    return end_message

def save_final_countries(institute, org_tup, bibliometer_path, 
                         corpus_year, results_folder_path): 
    """
    
    """
    # Standard library imports
    import os
    from pathlib import Path

    # 3rd party import
    import pandas as pd

    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import format_df_4_excel
    
    # Setting aliases for saving results
    results_sub_folder_alias = pg.ARCHI_RESULTS["countries"]

    # Setting aliases of common parts of file names
    origin_analysis_folder_alias  = pg.ARCHI_YEAR["analyses"]
    origin_countries_folder_alias = pg.ARCHI_YEAR["countries analysis"]
    countries_file_alias          = pg.ARCHI_YEAR["country weight file name"]
    year_countries_file_alias     = countries_file_alias + " " + corpus_year
    
    # Setting common paths
    origin_corpus_year_path     = bibliometer_path / Path(corpus_year)
    origin_analysis_folder_path = origin_corpus_year_path / Path(origin_analysis_folder_alias)
    origin_countries_path       = origin_analysis_folder_path / Path(origin_countries_folder_alias)    
    year_target_folder_path     = results_folder_path / Path(corpus_year)
    target_countries_path       = year_target_folder_path / Path(results_sub_folder_alias)  
    
    # Checking availability of required results folders
    if not os.path.exists(year_target_folder_path): os.makedirs(year_target_folder_path)
    if not os.path.exists(target_countries_path): os.makedirs(target_countries_path)
    
    # Get 'countries_df' from EXCEL file at full path 'origin_countries_file_path'
    origin_countries_file_alias = countries_file_alias + ".xlsx"
    origin_countries_file_path  = origin_countries_path / Path(origin_countries_file_alias)    
    countries_df = pd.read_excel(origin_countries_file_path)
    
    # Saving 'countries_df' as EXCEL file at full path 'target_countries_file_path'
    target_countries_file_alias = year_countries_file_alias + ".xlsx"     
    target_countries_file_path  = target_countries_path / Path(target_countries_file_alias)
    first_col_width = 32
    last_col_width  = 80
    wb, ws = format_df_4_excel(countries_df, first_col_width, last_col_width)
    ws.title = 'Pays ' + corpus_year
    wb.save(target_countries_file_path) 

    end_message = f"Final countries for year {corpus_year} saved in folder: \n  '{target_countries_file_path}'"
    return end_message

def save_final_results(institute, org_tup, bibliometer_path, datatype, corpus_year, 
                       if_analysis_name, results_to_save_dict, verbose = False):
    """
    """
    # Standard library imports
    import os
    from pathlib import Path

    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg 
    from BiblioMeter_FUNCTS.BM_SaveFinalResults import save_final_countries
    from BiblioMeter_FUNCTS.BM_SaveFinalResults import save_final_ifs
    from BiblioMeter_FUNCTS.BM_SaveFinalResults import save_final_kws
    from BiblioMeter_FUNCTS.BM_SaveFinalResults import save_final_pub_lists
    
    # Setting aliases for saving results
    results_root_alias   = pg.ARCHI_RESULTS["root"]
    results_folder_alias = pg.ARCHI_RESULTS[datatype]
    
    # Setting paths for saving results
    results_root_path   = bibliometer_path / Path(results_root_alias)
    results_folder_path = results_root_path / Path(results_folder_alias)
    
    # Checking availability of required results folders
    if not os.path.exists(results_root_path): os.makedirs(results_root_path)
    if not os.path.exists(results_folder_path): os.makedirs(results_folder_path)
    
    if results_to_save_dict["pub_lists"]:
        message = save_final_pub_lists(institute, org_tup, bibliometer_path,  
                                       corpus_year, results_folder_path)
        if verbose: print(message)
    
    if results_to_save_dict["ifs"]:
        message = save_final_ifs(institute, org_tup, bibliometer_path, 
                                 corpus_year, results_folder_path, if_analysis_name)
        if verbose: print("\n",message)

    if results_to_save_dict["kws"]:    
        message = save_final_kws(institute, org_tup, bibliometer_path, 
                                 corpus_year, results_folder_path)
        if verbose: print("\n",message)

    if results_to_save_dict["countries"]:    
        message = save_final_countries(institute, org_tup, bibliometer_path, 
                                       corpus_year, results_folder_path)
        if verbose: print("\n",message)
    
    end_message = f"Final results for year {corpus_year} saved in folder:  \n  '{results_folder_path}'"
    return end_message