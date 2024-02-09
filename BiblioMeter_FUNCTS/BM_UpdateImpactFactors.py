__all__ = ['update_inst_if_database', 
           'journal_capwords',
          ]

# to move from BM_ConsolidatePubList : 'find_missing_if', 'update_if_multi', 'update_if_single' 

def journal_capwords(text):
    # local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg 
    from BiblioMeter_FUNCTS.BM_PubGlobals import BM_LOW_WORDS_LIST
    
    text_split_list = []
    for x in text.split():
        if x.lower() in pg.BM_LOW_WORDS_LIST: 
            x = x.lower()
        else:
            x = x.capitalize()
        text_split_list.append(x)
    text = " ".join(text_split_list)
    return text


def _update_year_if_database(bibliometer_path, corpus_year, year_if_db_df, 
                             pub_list_path_alias, missing_if_filename_base_alias, 
                             missing_issn_filename_base_alias, most_recent_year):
    """
    Args:
       year_if_db_df (dataframe): IFs database of the year.
       
    Note:
        Uses internal fonction `journal_capwords`
    """
    # Standard library imports
    from pathlib import Path

    # 3rd party import
    import pandas as pd 
    import string 
    
    # local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg 
    from BiblioMeter_FUNCTS.BM_RenameCols import set_final_col_names
    
    # Internal functions    
    _capwords_journal_col = lambda row: journal_capwords(row[journal_col_alias])
    
    def _get_if(missing_file_path, useful_col_list):
        missing_df = pd.read_excel(missing_file_path, usecols = useful_col_list)
        if not missing_df.empty:
            missing_df[journal_col_alias] = missing_df.apply(_capwords_journal_col, axis=1) 
        return missing_df

    # Setting aliases of useful columns 
    col_final_list = set_final_col_names()
    journal_col_alias                  = col_final_list[6]
    issn_col_alias                     = col_final_list[10]
    eissn_col_alias                    = pg.COL_NAMES_BONUS['e-ISSN']
    database_if_col_alias              = pg.COL_NAMES_BONUS["IF clarivate"]
    most_recent_year_if_col_base_alias = pg.COL_NAMES_BONUS["IF en cours"]
    
    # Setting specific column names
    corpus_year_if_col                 = database_if_col_alias + " " + corpus_year
    most_recent_year_if_col_alias      = most_recent_year_if_col_base_alias + ", " + most_recent_year
    new_most_recent_year_if_col_alias  = database_if_col_alias + " " + most_recent_year
    
    # Setting useful paths
    corpus_year_path       = bibliometer_path / Path(corpus_year)     
    pub_list_path          = corpus_year_path / Path(pub_list_path_alias)
    year_missing_if_path   = pub_list_path / Path(corpus_year + missing_if_filename_base_alias)
    year_missing_issn_path = pub_list_path / Path(corpus_year + missing_issn_filename_base_alias)
    
    # Setting useful columns list for the year files with IFs of corpus year 
    corpus_year_useful_col_list = [journal_col_alias, issn_col_alias, eissn_col_alias, corpus_year_if_col ]
    
    # Getting the IFs of the year for the ISSN or e-ISSN already present in the IF database
    missing_if_corpus_year_if_df = _get_if(year_missing_if_path, corpus_year_useful_col_list)
        
    # Getting the IFs of the year for the ISSN or e-ISSN not yet present in the IF database 
    missing_issn_corpus_year_if_df = _get_if(year_missing_issn_path, corpus_year_useful_col_list)

    # Appending 'missing_if_corpus_year_if_df' to  'year_if_db_df'     
    if_appended_year_if_db_df = pd.concat([year_if_db_df, missing_if_corpus_year_if_df])  
    if_updated_year_if_db_df  = if_appended_year_if_db_df.drop_duplicates(subset = journal_col_alias, keep = 'last')
   
    # Appending 'missing_issn_corpus_year_if_df' to  'updated_year_if_db_df' 
    fully_appended_year_if_db_df = pd.concat([if_updated_year_if_db_df, missing_issn_corpus_year_if_df])  
    fully_updated_year_if_db_df  = fully_appended_year_if_db_df.drop_duplicates(subset = journal_col_alias, keep = 'last')
    
    # Sorting 'updated_year_if_db_df' by journal column
    fully_updated_year_if_db_df.sort_values(by=[journal_col_alias], inplace = True)
    
    # Setting useful columns list for the year files with IFs of most recent year  
    most_recent_year_useful_col_list = [journal_col_alias, issn_col_alias, eissn_col_alias, most_recent_year_if_col_alias]
    
    # Getting the IFs of the year for the ISSN or e-ISSN already present in the IF database
    missing_if_most_recent_year_if_df = _get_if(year_missing_if_path, most_recent_year_useful_col_list)
        
    # Getting the IFs of the year for the ISSN or e-ISSN not yet present in the IF database 
    missing_issn_most_recent_year_if_df = _get_if(year_missing_issn_path, most_recent_year_useful_col_list)
    
    # Initializing the dataframe of IFs of most recent year that will be returned for completion of the most recent year IF database
    corpus_year_most_recent_year_if_df = pd.concat([missing_if_most_recent_year_if_df, missing_issn_most_recent_year_if_df])
    corpus_year_most_recent_year_if_df.rename(columns = {most_recent_year_if_col_alias : new_most_recent_year_if_col_alias,}, 
                                              inplace = True)
    
    return (fully_updated_year_if_db_df, corpus_year_most_recent_year_if_df) 


def update_inst_if_database(bibliometer_path, corpi_years_list):
    """
    Note:
        Uses internal fonction `journal_capwords`
    """

    # Standard library imports
    import numpy as np
    from pathlib import Path

    # 3rd party import
    import BiblioParsing as bp
    import pandas as pd
    from openpyxl import Workbook

    # local imports    
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_RenameCols import set_final_col_names
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import mise_en_page

    # Internal functions   
    _capwords_journal_col = lambda row: journal_capwords(row[journal_col_alias])
    
    def _formatting_wb_sheet(year, df, wb, first, if_database):    
        if first:
            ws = wb.active
            ws.title = year
            wb,ws = mise_en_page(df, wb, if_database)        
        else:
            wb.create_sheet(year)
            wb.active = wb[year]
            ws = wb.active
            wb,_ = mise_en_page(df, wb, if_database)
        return wb       

    # Setting aliases of useful columns 
    col_final_list = set_final_col_names()
    journal_col_alias = col_final_list[6]    

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN
    if_root_folder_alias             = pg.ARCHI_IF["root"]
    missing_if_filename_base_alias   = pg.ARCHI_IF["missing_if_base"]
    missing_issn_filename_base_alias = pg.ARCHI_IF["missing_issn_base"]
    inst_all_if_filename_alias       = pg.ARCHI_IF["institute_if_all_years"]
    pub_list_path_alias              = pg.ARCHI_YEAR["pub list folder"]

    # Setting useful paths
    if_root_folder_path = bibliometer_path / Path(if_root_folder_alias)
    inst_all_if_path    = if_root_folder_path / Path(inst_all_if_filename_alias)

    # Getting the IFs database content and its IFS available years list
    if_db_df = pd.read_excel(inst_all_if_path, sheet_name = None)
    if_db_years_list     = list(if_db_df.keys())
    
    # Setting useful parameters for the update of the IFs database
    most_recent_year     = if_db_years_list[-1]
    off_if_db_years_list = sorted(list(set(corpi_years_list) - set(if_db_years_list[:-1])))
    
    # Initialize parameters for saving results as multisheet workbook
    if_database = True
    wb = Workbook()
    first = True
    
    # Building fully updated IFs database for years before the most recent year available for IFs
    most_recent_year_if_df_to_add = pd.DataFrame(columns = if_db_df[most_recent_year].columns)
    for if_db_year in if_db_years_list[:-1]:
        year_if_db_df = if_db_df[if_db_year]
        year_if_db_df.fillna(unknown_alias, inplace = True)
        year_if_db_df[journal_col_alias] = year_if_db_df.apply(_capwords_journal_col, axis=1)
        corpus_year = if_db_year
        dfs_tup = _update_year_if_database(bibliometer_path, 
                                           corpus_year, 
                                           year_if_db_df,
                                           pub_list_path_alias, 
                                           missing_if_filename_base_alias,
                                           missing_issn_filename_base_alias, 
                                           most_recent_year)
        fully_updated_year_if_db_df, corpus_year_most_recent_year_if_df_to_add = dfs_tup[0], dfs_tup[1]
        wb = _formatting_wb_sheet(if_db_year, fully_updated_year_if_db_df, 
                                  wb, first, if_database)
        first = False   
        most_recent_year_if_df_to_add = pd.concat([most_recent_year_if_df_to_add, 
                                                   corpus_year_most_recent_year_if_df_to_add])                          
    
    # Building fully updated Ifs database for years begening from the most recent year available for IFs
    most_recent_year_if_db_df = if_db_df[most_recent_year]
    most_recent_year_if_db_df.fillna(unknown_alias, inplace = True)
    most_recent_year_if_db_df[journal_col_alias] = most_recent_year_if_db_df.apply(_capwords_journal_col, 
                                                                                   axis = 1)
    for corpus_year in off_if_db_years_list:      
        _, corpus_year_most_recent_year_if_df_to_add = _update_year_if_database(bibliometer_path, 
                                                                         corpus_year, 
                                                                         most_recent_year_if_db_df,
                                                                         pub_list_path_alias, 
                                                                         missing_if_filename_base_alias,
                                                                         missing_issn_filename_base_alias, 
                                                                         most_recent_year)  
        most_recent_year_if_df_to_add = pd.concat([most_recent_year_if_df_to_add, 
                                                   corpus_year_most_recent_year_if_df_to_add])  
    
    most_recent_year_if_df_to_add.drop_duplicates(inplace = True)    
    most_recent_year_if_db_df = pd.concat([most_recent_year_if_db_df, 
                                           most_recent_year_if_df_to_add])  
    most_recent_year_if_db_df = most_recent_year_if_db_df.drop_duplicates(subset = journal_col_alias, 
                                                                          keep = 'last')
    
    wb = _formatting_wb_sheet(most_recent_year, 
                              most_recent_year_if_db_df, wb, first, if_database)
    wb.save(inst_all_if_path)
    
    end_message = f"IFs database updated in file : \n  '{inst_all_if_path}'"
    return end_message, if_db_years_list