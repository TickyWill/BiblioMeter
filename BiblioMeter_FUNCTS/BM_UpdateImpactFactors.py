__all__ = ['update_inst_if_database',          
          ]

# to move from BM_ConsolidatePubList : 'find_missing_if', 'update_if_multi', 'update_if_single' 

def _update_year_if_database(bibliometer_path, corpus_year, year_if_db_df, 
                            pub_list_path_alias, inst_if_filename_base_alias, recent_year):
    """
    Args:
       year_if_db_df (dataframe): IFs database of the year.
    """
    # Standard library imports
    from pathlib import Path

    # 3rd party import
    import pandas as pd    
    
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN 
    
    # Local library imports
    from BiblioMeter_FUNCTS.BM_RenameCols import set_final_col_names
    
    # Local globals imports
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BONUS
    
    # Setting useful column names
    col_final_list = set_final_col_names()

    # Setting useful column aliases
    journal_col_alias             = col_final_list[6]
    issn_col_alias                = col_final_list[10]
    eissn_col_alias               = COL_NAMES_BONUS['e-ISSN']
    database_if_col_alias         = COL_NAMES_BONUS["IF clarivate"]
    new_if_col_base_alias         = COL_NAMES_BONUS["IF en cours"]
    year_if_db_alias              = database_if_col_alias + " " + recent_year
    year_if_col                   = database_if_col_alias + " " + corpus_year
    recent_year_if_col_alias      = new_if_col_base_alias + ", " + recent_year
    new_recent_year_if_col_alias  = database_if_col_alias + " " + recent_year
    
    # Setting useful paths
    corpus_year_path    = bibliometer_path / Path(corpus_year)     
    pub_list_path       = corpus_year_path / Path(pub_list_path_alias)
    year_inst_if_path   = pub_list_path / Path(corpus_year + inst_if_filename_base_alias) 
        
    # Duplicating rows for existing e-ISSN  
    ref_year_if_db_df = year_if_db_df.copy()
    idy = len(year_if_db_df)
    for idx, row in year_if_db_df.iterrows():
        eissn = row[eissn_col_alias]   
        if eissn != UNKNOWN:
            idy += 1
            ref_year_if_db_df.loc[idy] = row
            ref_year_if_db_df.loc[idy, issn_col_alias] = eissn       
    
    # Getting the IFs of the year extracted from the corpus_year
    #useful_col_list = [x for x in year_if_db_df.columns.to_list() if x != eissn_col_alias]
    useful_col_list = [journal_col_alias, issn_col_alias, year_if_col]
    year_if_df = pd.read_excel(year_inst_if_path, usecols = useful_col_list) 
    
    # Getting the IFs of the most recent year extracted from the corpus_year
    useful_col_list = [journal_col_alias, issn_col_alias, recent_year_if_col_alias]
    recent_year_if_df = pd.read_excel(year_inst_if_path, usecols = useful_col_list) 
    recent_year_if_df.rename({recent_year_if_col_alias : new_recent_year_if_col_alias}, 
                             axis = 1, inplace = True)
    recent_year_if_df[journal_col_alias] = recent_year_if_df.apply(lambda row: row[journal_col_alias].upper(), 
                                                                   axis=1)

    # Merging the two IFs dataframes
    new_year_if_db_df = ref_year_if_db_df.merge(year_if_df, 
                                                left_on  = issn_col_alias,
                                                right_on = issn_col_alias,
                                                how = "outer")
    
    # Combining IF values in the merged df
    if int(recent_year) >= int(corpus_year):
        year_if_col_x = year_if_col + "_x"
        year_if_col_y = year_if_col + "_y"
    else:
        year_if_col_x = year_if_db_alias
        year_if_col_y = year_if_col 
        
    for idx, row in new_year_if_db_df.iterrows():
        year_if_x = row[year_if_col_x]
        year_if_y = row[year_if_col_y]
        if year_if_x == UNKNOWN and year_if_y:
            new_year_if_db_df.loc[idx, year_if_col_x] = year_if_y     
            
    # Cleaning the merged df
    new_year_if_db_df.drop([journal_col_alias + "_y", year_if_col_y], axis = 1, inplace = True)
    new_year_if_db_df.rename({journal_col_alias + "_x": journal_col_alias,
                              year_if_col_x           : year_if_col,
                             }, axis = 1, inplace = True)
    new_year_if_db_df.fillna(UNKNOWN, inplace = True)
    
    # Distributing the available IF value per journal name
    temp_df = pd.DataFrame(columns = new_year_if_db_df.columns)
    for idx, journal_df in new_year_if_db_df.groupby(journal_col_alias):
        year_if_list = list(set(journal_df[year_if_col].to_list()) - set(UNKNOWN))
        year_if = year_if_list[0]
        if not year_if : year_if = UNKNOWN
        for idy, row in journal_df.iterrows():
            journal_df.loc[idy,year_if_col] = year_if
        temp_df = temp_df.append(journal_df)
        
    # Building the updated IF database of the year keeping the first of duplicated row
    # assuming that it the one with true ISSN and e-ISSN values
    updated_year_if_db_df =  temp_df.drop_duplicates(journal_col_alias)
    
    return updated_year_if_db_df, recent_year_if_df


def update_inst_if_database(bibliometer_path, corpi_years_list):
    """
    
    """
    
    # Standard library imports
    from pathlib import Path

    # 3rd party import
    from openpyxl import Workbook
    import pandas as pd
    
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN 

    # Local library imports
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import mise_en_page

    # Local globals imports
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_IF
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_YEAR
    
    # Internal function    
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

    # Setting useful aliases
    if_root_folder_alias        = ARCHI_IF["root"]
    inst_if_filename_base_alias = ARCHI_IF["institute_if_base"]
    inst_all_if_filename_alias  = ARCHI_IF["institute_if_all_years"]
    pub_list_path_alias         = ARCHI_YEAR["pub list folder"]

    # Setting useful paths
    if_root_folder_path = bibliometer_path / Path(if_root_folder_alias)
    inst_all_if_path    = if_root_folder_path / Path(inst_all_if_filename_alias)

    if_db_df = pd.read_excel(inst_all_if_path, sheet_name = None)
    years_list = list(if_db_df.keys())
    recent_year = years_list[-1]
    last_corpus_year = corpi_years_list[-1] 
    
    if_database = True
    wb = Workbook()
    first = True
    
    recent_year_if_df = pd.DataFrame(columns = if_db_df[recent_year].columns)
    for year in years_list:
        year_if_db_df = if_db_df[year]
        year_if_db_df.fillna(UNKNOWN, inplace = True)        
        final_year_if_db_df, temp_df = _update_year_if_database(bibliometer_path, 
                                                                year, 
                                                                year_if_db_df, 
                                                                pub_list_path_alias, 
                                                                inst_if_filename_base_alias,
                                                                recent_year)               
        recent_year_if_df = recent_year_if_df.append(temp_df)
        if year == recent_year:
            if int(recent_year) < int(last_corpus_year):
                for corpus_year in range(int(recent_year)+1,int(last_corpus_year)+1):
                    _, temp_df = _update_year_if_database(bibliometer_path, 
                                                          str(corpus_year), 
                                                          recent_year_if_df, 
                                                          pub_list_path_alias, 
                                                          inst_if_filename_base_alias,
                                                          recent_year)
                    recent_year_if_df = recent_year_if_df.append(temp_df)
                
            recent_year_if_df.drop_duplicates()
            final_year_if_db_df, _ = _update_year_if_database(bibliometer_path, 
                                                              year, 
                                                              recent_year_if_df, 
                                                              pub_list_path_alias, 
                                                              inst_if_filename_base_alias,
                                                              recent_year)               
        wb = _formatting_wb_sheet(year, final_year_if_db_df, wb, first, if_database)
        first = False
    wb.save(inst_all_if_path)
       
    end_message = f"IFs database updated in file : \n  '{inst_all_if_path}'"
    return end_message, years_list