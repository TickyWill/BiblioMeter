__all__ = ['get_unique_numbers',           
           'solving_homonyms',          
           'concat_name_firstname',
           'add_authors_name_list',
           'add_OTP',           
           'consolidate_pub_list',            
           'add_biblio_list',
           'add_if',
           'clean_reorder_rename_submit',           
           'concatenate_pub_lists',          
           'update_employees',           
           'mise_en_page',            
           'rename_column_names',          
           'find_missing_if']

def get_unique_numbers(numbers):

    list_of_unique_numbers = []

    unique_numbers = set(numbers)

    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

def solving_homonyms(in_path, out_path):

    # Standard library imports
    from pathlib import Path
    import math

    # 3rd party imports
    import pandas as pd
    from openpyxl import Workbook, load_workbook
    from openpyxl.utils.dataframe import dataframe_to_rows as openpyxl_dataframe_to_rows
    from openpyxl.styles import PatternFill as openpyxl_PatternFill

    # BiblioAnalysis_Utils package imports    
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH 
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_CONSOLIDATION
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import ROW_COLORS

    # Useful alias
    pub_id_alias = COL_NAMES['pub_id']
    idx_author   = COL_NAMES['authors'][1]
    dpt_alias    = COL_NAMES_RH['dpt']
    homonym_alias = 'HOMONYM'
    col_conso_alias = COL_CONSOLIDATION
        
    ###########################
    # Getting the submit file #
    ###########################

    df_submit = pd.read_excel(in_path)
    
    ############################################
    # Getting rid of the columns we don't want #
    ############################################
    df_submit = df_submit[col_conso_alias].copy()
    
    ## Remettre les Pub_ID dans l'ordre
    #df_submit.sort_values(by=[pub_id_alias, dpt_alias], ascending=False, inplace = True)
    #df_submit.sort_values(by=[pub_id_alias, idx_author], ascending=True, inplace = True)
    
    #wb, ws = mise_en_page(df_submit)
    
    wb = Workbook()
    ws = wb.active
    
    ws.title = 'Consolidation Homonymes'
    
    yellow_ft = openpyxl_PatternFill(fgColor = ROW_COLORS['highlight'], fill_type = "solid")

    for indice, r in enumerate(openpyxl_dataframe_to_rows(df_submit, index=False, header=True)):
        ws.append(r)
        last_row = ws[ws.max_row]
        if r[col_conso_alias.index(homonym_alias)] == homonym_alias and indice > 0:
            cell = last_row[col_conso_alias.index('Nom')]
            cell.fill = yellow_ft
            cell = last_row[col_conso_alias.index('Prénom')]
            cell.fill = yellow_ft
            
    wb.save(out_path)
    
    end_message = f"File for solving homonymies saved in folder: \n  '{out_path}'"
    return end_message
    
    
def _you_got_OTPed(df, i):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        Adds OTP to df'''
    
    # Standard library imports
    from pathlib import Path
    
    # Local library imports   
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import OTP_STRING
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS 
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH 
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # 3rd party library imports
    import pandas as pd
    from openpyxl.utils.cell import get_column_letter
    
    # Useful alias   
    OTP_alias = COL_NAMES_BONUS['list OTP']
    dpt_alias = COL_NAMES_RH['dpt']
    pub_id_alias = COL_NAMES['pub_id']
    
    if OTP_alias in df.columns:
            df[OTP_alias].iloc[i] = OTP_STRING[df.iloc[i][dpt_alias]]
    else:
        df[OTP_alias] = pd.Series()
        df[OTP_alias].iloc[i] = OTP_STRING[df.iloc[i][dpt_alias]]
    
    return df

def _liste_de_validation(df, i):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        Adds OTP to df'''
    
    # Global variable imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import OTP_LIST
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH 
    
    # Useful alias
    dpt_alias = COL_NAMES_RH['dpt']
    
    validation_list = OTP_LIST[df.iloc[i][dpt_alias]]
    
    truc = '"'+','.join(validation_list)+'"'
    
    return truc

def concat_name_firstname(df):
    
    ''' The `concat_name_firstname` function checks if the given variable is a of type DataFrame.
    Then it verifies if the columns 'Nom', 'Prénom' are in the given dataframe.
    If so, it combines the column 'Nom' and 'Prénom' adding a ', ' in between the two values 
    of the columns, into a new column named 'Nom Prénom'.
    
    Args:
        df (dataframe): dataframe in which we want to combine the Nom and Prénom.
        
    Returns:
        df (dataframe): the dataframe given as variable but with the new column.
    
    Notes:
        None.
    '''
    # 3rd party imports
    import pandas as pd
    
     # Global variable imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
       
    # Useful alias
    nom_alias = COL_NAMES_RH['nom']
    prenom_alias = COL_NAMES_RH['prénom']
    full_name_alias = COL_NAMES_BONUS['nom prénom']
    
    # Check is df is a DataFrame and if it contains the colomns needed which are 'Nom' and 'Prénom' and 'Pub_id'
    if isinstance(df, pd.DataFrame):
        to_check = [nom_alias, prenom_alias]
        for i in to_check:
            if nom_alias not in df:
                raise KeyError(f"The column {i} is not in DataFrame")
    else:
        raise TypeError(f"The variable {df} is not of proper type, it has to be a DataFrame")
        
    # Add of the colomn 'Nom Prénom' meaning full name.
    df[full_name_alias] = df[nom_alias] + ', ' + df[prenom_alias]
    
    # TO DO : df['Nom Prénom'] = df.apply()

    return df

def add_authors_name_list(in_path, out_path):    
    ''' The function `add_authors_fullname_list` adds two columns to the dataframe 'df_in'.
    These columns contain respectivelly the co-authors identity (name, abreviated surname) 
    and the article co-authors list.
    
    Args:
        in_path (path): Fullpath of the working excel file. 
        out_path (path): Fullpath of the processed dataframe as an Excel file 
                         saved after going through its treatment.
    
    Returns:
        None.
    
    Notes:
        The global 'COL_NAMES' is imported from 'BiblioSpecificGlobals' module 
        of 'BiblioAnalysis_Utils' package.
        The function `concat_name_firstname` is imported from 'BiblioMeterFonctions' 
        module of 'BiblioMeter_FUNCTS' package.    
    '''
    # 3rd party imports
    import pandas as pd
    
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import concat_name_firstname
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    
    # Useful alias
    pub_id_alias      = COL_NAMES['pub_id']
    idx_authors_alias = COL_NAMES['authors'][1]
    full_name_alias      = COL_NAMES_BONUS['nom prénom']
    full_name_list_alias = COL_NAMES_BONUS['nom prénom liste']   
    
    # Read of the excel file
    df_in = pd.read_excel(in_path)
    
    # Add of the column 'Nom Prénom' that will be used to create the authors fullname list
    df_in = concat_name_firstname(df_in)
    
    # Sort on Pub_id and then add the authors fullname list
    if pub_id_alias not in df_in:
        error_text  = f"The column {pub_id_alias} is missing in the file "
        error_text += f"\n {in_path}."
        error_text += f"\n\nPlease make sure that a column indexing the articles "
        error_text += f"is named 'Pub_id' in this file."
        raise KeyError(error_text)
        
    df_out = pd.DataFrame()
    for pub_id, pub_id_df in df_in.groupby(pub_id_alias): 
        list_authors =";".join(pub_id_df[full_name_alias].unique())
        pub_id_df[full_name_list_alias] = list_authors
        df_out = pd.concat([df_out, pub_id_df])

    # Saving 'df_out' in an excel file 'out_path'
    df_out.to_excel(out_path, index = False)
    
    end_message = f"Column with co-authors list is added to the file: \n  '{out_path}'"
    return end_message


def add_OTP(in_path, out_path, out_file_base):

    '''    
    Args:
        in_path (path): fullpath of the working excel file. 
        out_path (path): fullpatho of the saves prosseced file
    
    Returns:
        None.
    
    Notes:
        The global 'COL_NAMES' is imported from 'BiblioSpecificGlobals' module 
        of 'BiblioAnalysis_Utils' package.
        The function `concat_name_firstname` is imported from 'BiblioMeterFonctions' 
        part of 'BiblioMeter_FUNCTS' package.    
    '''
    
    # Standard library imports
    from pathlib import Path

    # 3rd party imports
    import pandas as pd
    from openpyxl.worksheet.datavalidation import DataValidation as openpyxl_DataValidation
    from openpyxl.utils import get_column_letter as openpyxl_get_column_letter
    
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import add_authors_name_list
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import mise_en_page
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_OTP
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import DPT_ATTRIBUTS_DICT       

    # Internal functions    
    def _save_dpt_OTP_file(dpt, df_dpt, dpt_otp_list, excel_dpt_path):
        
        ''' Create and store an Excel file under 'excel_dpt_path' for the department labelled 'dpt'.
        The OPTs of the choosen department are added in a new column named 'OTP_alias' definined after the
        global `COL_NAMES_BONUS['list OTP']`. 
        A list data validation rules is added to each celles of the column
        'OTP_alias'. The data frame column are renamed after the  global 'COL_OTP'. The Excel frame is
        configurated by the `mise_en_page` function.
        
        '''
        
        # Building validation list of OTP for 'dpt' department
        validation_list = '"'+','.join(dpt_otp_list) + '"' 
        data_val = openpyxl_DataValidation(type = "list", 
                                           formula1 = validation_list, 
                                           showErrorMessage = False)
        
        # Adding a column containing OTPs of 'dpt' department
        df_dpt[OTP_alias] = validation_list
        
        # Renaming the columns 
        df_dpt = df_dpt.reindex(columns = COL_OTP)
        # to replace by :
        # COL_OTP_DICT {col_old_name : col_new_name}
        # df_dpt = df_dpt.rename(columns = COL_OTP_DICT) 
        
        # Formatting the EXCEL file
        wb, ws = mise_en_page(df_dpt)
        ws.title = 'OTP ' +  dpt    # To define via a global
        
        # Setting num of first col and first row in EXCEL files
        excel_first_col_num = 1
        excel_first_row_num = 2
        
        # Getting the column letter for the OTPs column 
        OTP_alias_df_index = list(df_dpt.columns).index(OTP_alias)        
        OTP_alias_excel_index = OTP_alias_df_index + excel_first_col_num 
        OTP_alias_column_letter = openpyxl_get_column_letter(OTP_alias_excel_index)
                
        # Activating the validation data list in all cells of the OTPs column
        if len(df_dpt):
            # Adding a validation data list
            ws.add_data_validation(data_val)
            for df_index_row in range(len(df_dpt)):  
                OTP_cell_alias = OTP_alias_column_letter + str(df_index_row + excel_first_row_num)
                data_val.add(ws[OTP_cell_alias])

        wb.save(excel_dpt_path)
        
    # Setting useful aliases
    pub_id_alias = COL_NAMES['pub_id']      # Pub_id
    idx_author   = COL_NAMES['authors'][1]  # Idx_author
    dpt_alias = COL_NAMES_RH['dpt']         # Dpt/DOB (lib court)
    OTP_alias = COL_NAMES_BONUS['list OTP'] # Choix de l'OTP
    
    # Adding a column with a list of the authors
    end_message = add_authors_name_list(in_path, in_path)
    print('\n ',end_message)
    
    solved_homonymies_df = pd.read_excel(in_path)
    solved_homonymies_df.fillna('', inplace = True)
    
    dpt_list = list(DPT_ATTRIBUTS_DICT.keys())
     
    # For each department adding a column containing 1 or 0 
    # depending if the author belongs or not to the department
    for dpt in  dpt_list:
        dpt_label_list = DPT_ATTRIBUTS_DICT[dpt]['dpt_label']
        solved_homonymies_df[dpt] = solved_homonymies_df[dpt_alias].apply(lambda x: 1 
                                                                          if x in dpt_label_list 
                                                                          else 0)
    
    # Building 'df_out' out of 'solved_homonymies_df' with a row per pub_id 
    # 1 or 0 is assigned to each department column depending 
    # on if at least one co-author is a member of this department,
    # the detailed information is related to the first author only
    df_out = pd.DataFrame()
    for pub_id, dg in solved_homonymies_df.groupby('Pub_id'):
        dg = dg.sort_values(by=['Idx_author'])
        x = dg[dpt_list].any().astype(int) #sum()
        dg[dpt_list] = x
        df_out = pd.concat([df_out,dg.iloc[:1]]) 
    
    # Configuring an Excel file per department with the list of OTPs
    for dpt in sorted(dpt_list):
        # Setting df_dpt with only pub_ids for which the first author
        # is from the 'dpt' department
        filtre_dpt = False
        for dpt_value in DPT_ATTRIBUTS_DICT[dpt]['dpt_label']:
            filtre_dpt = filtre_dpt | (df_out[dpt_alias] == dpt_value)
        df_dpt = df_out[filtre_dpt].copy()
        
        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = DPT_ATTRIBUTS_DICT[dpt]['dpt_otp']
        
        # Setting the full path of the EXCEl file for the 'dpt' department
        OTP_file_name_dpt = f'{out_file_base}_{dpt}.xlsx'
        excel_dpt_path = out_path / Path(OTP_file_name_dpt)
        
        # Adding a column with validation list for OTPs and saving the file
        _save_dpt_OTP_file(dpt,df_dpt,dpt_otp_list,excel_dpt_path)

    end_message  = f"Files for setting publication OTPs per department "
    end_message += f"saved in folder: \n  '{out_path}'"
    return end_message
    

def consolidate_pub_list(in_path, out_path, in_file_base):
    
    '''
    Faire attention à ce que path mène à un fichier submit
    
    Args : 
    path : chemin vers fichier submit
    dep_to_keep : liste de 0 et 1 disant quel département inclure
        
    Returns :
    un fichier excel
    '''
    
    # Standard imports
    from pathlib import Path
    import os
    
    # 3rd party imports
    import pandas as pd    

    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # local imports
    from BiblioMeter_GUI.Globals_GUI import DPT_LABEL_DICT
    
    # internal functions
    def _set_df_OTP_dpt(dpt_label):        
        OTP_file_name_dpt_ok = in_file_base + '_' + dpt_label + '_ok.xlsx'
        dpt_path = in_path / Path(OTP_file_name_dpt_ok)       
        if not os.path.exists(dpt_path):
            OTP_file_name_dpt = in_file_base + '_' + dpt_label + '.xlsx'
            dpt_path = in_path / Path(OTP_file_name_dpt)
        dpt_df = pd.read_excel(dpt_path)
        return dpt_df
    
    # Useful alias
    pub_id_alias = COL_NAMES['pub_id']
    
    ### Charger les df et ajouter les 4 colonnes 
    dpt_label_list = list(DPT_LABEL_DICT.keys())
    OTP_df_init_status = True
    for dpt_label in dpt_label_list:
        dpt_df =  _set_df_OTP_dpt(dpt_label)
        if OTP_df_init_status:
            OTP_df = dpt_df.copy()            
        else:
            OTP_df = OTP_df.append(dpt_df)
        OTP_df_init_status = False

    OTP_df.drop_duplicates(subset = [pub_id_alias], inplace = True)    
    rename_column_names(OTP_df)
    OTP_df.to_excel(out_path, index = False)
    end_message = f"OTPs identification integrated in file : \n  '{out_path}'"
    return end_message
    

def add_biblio_list(in_path, out_path):
    ''' The function `add_biblio_list` adds a new column containing the full reference 
    of each publication listed in an EXCEL file and saves it.
    The full reference is built by concatenating the folowing items: title, first author, year, journal, DOI.
    These items sould be available in the initial EXCEL file with columns names 
    defined by the global 'COL_NAMES' with the keys 'pub_id' and 'articles'.
    The name of the new column is defined by the global "COL_NAMES_BONUS['liste biblio']".
    
    Args:
        in_path (path): path (including name of the file) leading to the working EXCEL file. 
        out_path (path): path (including name of the file) leading to where the file with the new column will be saved.
    
    Returns:
        None.
    
    Notes:
        The global 'COL_NAMES' is imported from 'BiblioSpecificGlobals' module of 'BiblioAnalysis_Utils' package.
        The function `concat_name_firstname` is imported from 'BiblioMeterFonctions' module of 'BiblioMeter_FUNCTS' package.    
    '''
    # 3rd party imports
    import pandas as pd 
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import EFF_CONVERTERS_DIC

    # Setting useful aliases
    pub_id_alias           = COL_NAMES['pub_id']
    pub_first_author_alias = COL_NAMES['articles'][1]
    pub_year_alias         = COL_NAMES['articles'][2]
    pub_journal_alias      = COL_NAMES['articles'][3]
    pub_doi_alias          = COL_NAMES['articles'][6]
    pub_title_alias        = COL_NAMES['articles'][9]   
    pub_full_ref_alias     = COL_NAMES_BONUS['liste biblio']

    # Read of the excel file
    articles_df = pd.read_excel(in_path, converters = EFF_CONVERTERS_DIC)

    articles_plus_full_ref_df = pd.DataFrame()
    for pub_id, pub_id_df in articles_df.groupby(pub_id_alias): # Split the frame into subframes with same Pub_id
        
        pub_id_first_row = pub_id_df.iloc[0]                                # Select the first row and build the full reference
        full_ref  = f'{pub_id_first_row[pub_title_alias]}, '                # add the reference's title
        full_ref += f'{pub_id_first_row[pub_first_author_alias]}. et al., ' # add the reference's first author
        full_ref += f'{pub_id_first_row[pub_journal_alias].capitalize()}, '              # add the reference's journal name
        full_ref += f'{str(pub_id_first_row[pub_year_alias])}, '            # add the reference's publication year
        full_ref += f'{pub_id_first_row[pub_doi_alias]}'                    # add the reference's DOI
        
        pub_id_df[pub_full_ref_alias] = full_ref
        articles_plus_full_ref_df = pd.concat([articles_plus_full_ref_df, pub_id_df])

    articles_plus_full_ref_df.to_excel(out_path, index = False)
    
    end_message = f"Column with full reference of publication added in file: \n  '{out_path}'"
    return end_message
    
    
def add_if(in_file_path, out_file_path, if_path, year = None):
    
    '''The function `add_if` adds two new columns containing impact factors
    to the corpus dataframe 'corpus_df' got from a file which full path is 'in_file_path'. 
    The two columns are named through 'corpus_year_if_col_alias' and 'current_year_if_col_alias'.
    The impact factors are got from an Excel workbook with a worksheet per year 
    which full path is 'if_path' and put in the IFs dataframe 'if_df'.
    The column 'corpus_year_if_col_alias' is filled with the IFs values 
    of the corpus year 'year' if available in the dataframe 'if_df', 
    else the values are set to 'not_available_if_alias'.
    The column 'current_year_if_col_alias' is filled with the IFs values 
    of the most recent year available in the dataframe 'if_df'.
    In these columns, the nan values of IFs are replaced by 'unknown_if_fill_alias'.
    If 'year' is None, this is performed for all the years found in the corpus dataframe 
    and results in the update of the two columns.
    If 'year' is not None, this is performed for the corpus dataframe of the year 'year' 
    and results in the creation of the two columns.
    
    Args:
        in_file_path (path): The full path to get the corpus dataframe 'corpus_df'. 
        out_file_path (path): The full path to save the new corpus dataframe with the two columns.
        if_path (path): The full path to get the dataframe 'if_df'.
        year (int): The year of the corpus to be appended with the two new IF columns.
    Returns:
        (str): Message indicating which file has been affected and how. 
    
    Notes:
        The global 'COL_NAMES' is imported from the module 'BiblioSpecificGlobals' 
        of the package 'BiblioAnalysis_Utils'.
        The globals 'COL_MAJ_IF', 'COL_NAMES_BONUS', 'FILL_EMPTY_KEY_WORD' 
        and 'NOT_AVAILABLE_IF' are imported from the module 'BiblioMeterGlobalsVariables' 
        of the package 'BiblioMeter_FUNCTS'.    
    '''
    
    # 3rd party imports
    import pandas as pd    
    
    # BiblioAnalysis_Utils imports 
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_MAJ_IF
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import FILL_EMPTY_KEY_WORD
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import NOT_AVAILABLE_IF
    
    # Internal functions    
    def _create_if_column(issn_column, if_dict, if_empty_word):
        ''' The function `_create_if_column` builds a dataframe column 'if_column'
        using the column 'issn_column' of this dataframe and the dict 'if_dict' 
        that make the link between ISSNs ('if_dict' keys) and IFs ('if_dict' values). 
        The 'nan' values in the column 'if_column' are replaced by 'empty_word'
        
        Args:
            issn_column (pandas serie): The column of the dataframe of interest 
                                        that contains the ISSNs values.
            if_dict (dict): The dict which keys are ISSNs and values are IFs.
            if_empty_word (str): The word that will replace nan values in column the returned column.
        
        Returns:
            (pandas serie): The column of the dataframe of interest 
                            that contains the IFs values. 
        '''
        if_column = issn_column.map(if_dict)
        if_column = if_column.fillna(if_empty_word)
        return if_column

    # Setting useful aliases
    year_col_alias = COL_NAMES['articles'][2]
    issn_col_alias = COL_NAMES['articles'][10]
    eissn_col_alias           = COL_NAMES_BONUS['EISSN']
    database_if_col_alias     = COL_NAMES_BONUS['IF clarivate']
    current_year_if_col_alias = COL_NAMES_BONUS['IF en cours']
    corpus_year_if_col_alias  = COL_NAMES_BONUS['IF année publi']
    if_update_col_list_alias  = COL_MAJ_IF
    not_available_if_alias = NOT_AVAILABLE_IF
    unknown_if_fill_alias  = FILL_EMPTY_KEY_WORD
    unknown_alias          = FILL_EMPTY_KEY_WORD
    
    # Getting the df of the IFs database
    if_df = pd.read_excel(if_path, sheet_name = None)
    
    # Getting the df where to add IFs
    corpus_df = pd.read_excel(in_file_path)
    
    # Setting useful internal variables
    if_available_years_list = list(if_df.keys())
    if_most_recent_year = if_available_years_list[-1]
    most_recent_year_if_dict = dict(zip(if_df[if_most_recent_year][issn_col_alias], 
                                        if_df[if_most_recent_year][database_if_col_alias]))
        
    if year == None:
        # Setting type of values in 'year_col_alias' as string
        corpus_df = corpus_df.astype({year_col_alias : str})
        
        # Building the 'years' list of years in 'corpus_df' removing 'unkown_alias' years
        years = list(corpus_df[year_col_alias].unique())
        if unknown_alias in years : years.remove(unknown_alias)
        
        # Initializing 'corpus_df_bis' that will concatenate, on all years, 
        # the 'corpus_df' info added with IF values
        corpus_df_bis = pd.DataFrame()
        
        # Appending, year by year in 'years', the 'corpus_df' info completed with IF values, to 'corpus_df_bis' 
        for year in years:
            # Initialize 'inter_df' as copy of 'corpus_df' for column 'year_col_alias' value = 'year'
            inter_df = corpus_df[corpus_df[year_col_alias] == year].copy()
            
            # Adding 'current_year_if_col_alias' column to 'inter_df' 
            # with values defined by internal function '_create_if_column' 
            inter_df[current_year_if_col_alias] = _create_if_column(inter_df[issn_col_alias],
                                                                    most_recent_year_if_dict,
                                                                    unknown_if_fill_alias)            
            
            # Adding 'corpus_year_if_col_alias' column to 'inter_df' 
            if year in if_available_years_list:
                # with values defined by internal function '_create_if_column'
                year_if_dict = dict(zip(if_df[year][issn_col_alias], 
                                        if_df[year][database_if_col_alias]))
                inter_df[corpus_year_if_col_alias] = _create_if_column(inter_df[issn_col_alias],
                                                                       year_if_dict,
                                                                       unknown_if_fill_alias)
            else:
                # with 'not_available_if_alias' value 
                inter_df[corpus_year_if_col_alias] = not_available_if_alias
            
            # Appending 'inter_df' to 'corpus_df_bis' 
            corpus_df_bis = corpus_df_bis.append(inter_df)
            
        # Saving 'corpus_df_bis' as EXCEL file at full path 'out_file_path'
        corpus_df_bis.to_excel(out_file_path, columns = if_update_col_list_alias, index = False)    
        end_message = f"IFs updated in file : \n  '{out_file_path}'"
    
    else: 
        # Initialize 'corpus_df_bis' as copy of 'corpus_df'
        corpus_df_bis = corpus_df.copy()
        
        # Adding 'current_year_if_col_alias' column to 'corpus_df_bis' 
        # with values defined by internal function '_create_if_column'
        corpus_df_bis[current_year_if_col_alias] = _create_if_column(corpus_df_bis[issn_col_alias],
                                                                     most_recent_year_if_dict,
                                                                     unknown_if_fill_alias)        

        # Adding 'corpus_year_if_col_alias' column to 'corpus_df_bis' 
        if year in if_available_years_list:
            # with values defined by internal function '_create_if_column'
            current_year_if_dict = dict(zip(if_df[year][issn_col_alias], 
                                            if_df[year][database_if_col_alias]))
            corpus_df_bis[corpus_year_if_col_alias] = _create_if_column(corpus_df_bis[issn_col_alias],
                                                                        current_year_if_dict,
                                                                        unknown_if_fill_alias)
        else:
            # with 'not_available_if_alias' value
            corpus_df_bis[corpus_year_if_col_alias] = not_available_if_alias
        
        
        # Saving 'corpus_df_bis' as EXCEL file at full path 'out_file_path'
        corpus_df_bis.to_excel(out_file_path, index = False)
        end_message = f"IFs added for year {year} in file : \n  '{out_file_path}'"
    
    return end_message
                

def clean_reorder_rename_submit(in_file_path, out_file_path):
    
    ''' The `clean_reorder_rename_submit` etc ...
    
    Args:
        in_path (path): path (including name of the file) leading to the working excel file. 
        out_path (path): path (including name of the file) leading to where the file will be saved after going through its treatment.
    
    Returns:
        None.
    
    Notes:
   
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # Local library imports
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_COL_NAMES
    
    # 3rd party imports
    import pandas as pd
    
    # Read of the excel file
    df_in = pd.read_excel(in_file_path)
    
    df_reordered = df_in[[SUBMIT_COL_NAMES['pub_id'], 
                          SUBMIT_COL_NAMES['idx_authors'], 
                          SUBMIT_COL_NAMES['co_authors'], 
                          SUBMIT_COL_NAMES['address'], 
                          SUBMIT_COL_NAMES['country'], 
                          SUBMIT_COL_NAMES['year'], 
                          SUBMIT_COL_NAMES['journal'], 
                          SUBMIT_COL_NAMES['volume'], 
                          SUBMIT_COL_NAMES['page'], 
                          SUBMIT_COL_NAMES['DOI'], 
                          SUBMIT_COL_NAMES['document_type'], 
                          SUBMIT_COL_NAMES['language'], 
                          SUBMIT_COL_NAMES['title'], 
                          SUBMIT_COL_NAMES['ISSN'] ]]
    
    # Save in an excel file where leads out_path
    df_reordered.to_excel(out_file_path, index = False)
    
    
def concatenate_pub_lists(bibliometer_path, years_list):
    
    """
    """
    # Standard library imports
    import os
    from pathlib import Path
    from datetime import datetime
    
    # 3rd library imports
    import pandas as pd    
    
    # Local library imports
    from BiblioMeter_GUI.Globals_GUI import ARCHI_BDD_MULTI_ANNUELLE
    from BiblioMeter_GUI.Globals_GUI import ARCHI_YEAR
    
    # Setting useful aliases
    pub_list_path_alias      = ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = ARCHI_YEAR["pub list file name base"]
    bdd_multi_annuelle_folder_alias = ARCHI_BDD_MULTI_ANNUELLE["root"]
    bdd_multi_annuelle_file_alias   = ARCHI_BDD_MULTI_ANNUELLE["concat file name base"]
    
    # Building the concatenated dataframe of available publications lists
    df_concat = pd.DataFrame()    
    available_liste_conso = ""    
    for i in range(len(years_list)):
        try:
            year = years_list[i]
            pub_list_file_name = f"{pub_list_file_base_alias} {year}.xlsx"
            pub_list_path = bibliometer_path / Path(year) / Path(pub_list_path_alias) / Path(pub_list_file_name)
            df_inter = pd.read_excel(pub_list_path)
            df_concat = df_concat.append(df_inter)        
            available_liste_conso += f" {year}"
        
        except FileNotFoundError:
            pass
    
    # Saving the concatenated dataframe in an EXCEL file
    date = str(datetime.now())[:16].replace(':', 'h')
    out_file = f"{date} {bdd_multi_annuelle_file_alias} {os.getlogin()}_{available_liste_conso}.xlsx"
    out_path = bibliometer_path / Path(bdd_multi_annuelle_folder_alias)
    df_concat.to_excel(out_path / Path(out_file), index = False)
    
    end_message  = f"Concatenation of consolidated pub lists saved in folder: \n  '{out_path}'"
    end_message += f"\n\n under filename: \n  '{out_file}'."
    return end_message
 
    
def update_employees(bibliometer_path):
    '''
    '''
    
    # Standard library imports
    import os
    from pathlib import Path
    from datetime import date
    
    # 3rd party imports
    import pandas as pd    
    import shutil
    
    # Local library imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
    from BiblioMeter_GUI.Globals_GUI import COL_NAMES_BM
    from BiblioMeter_GUI.Globals_GUI import ARCHI_RH
    from BiblioMeter_GUI.Globals_GUI import ARCHI_SECOURS    

    # Internal functions
    def _get_year(mmyyyy):
        return (mmyyyy[2:6])

    def _check_year_format(mmyyyy):
        '''The `_check_year_format` function, checks if the string argument mmyyyy
        is in the right format.

        Args:
            mmyyyy (string) : string formatted as mmyyyy to be checked.

        Returns:
            O or 1 (boolean) : 0 if not in the right format, 1 if in the right format.
        '''

        try:
            today_year = date.today().year
            taille_fourchette = 5
            range_min = today_year - taille_fourchette
            range_max = today_year + taille_fourchette
            years_to_check = [str(year) for year in range(range_min, range_max + 1)]
            months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
            all_possible_dates = [mm + year for mm in months for year in years_to_check]

            if mmyyyy in all_possible_dates:
                return 1
            else:
                return 0
        except:
            return 0

    def _different_years(list_of_dates):
        '''
        Args:
            list_of_dates (list of strings): a list of string of dates in format mmyyyy, 
            mm being the number of the month and yyyy being the number of the year.
            
        Returns:
            L (list of strings):
        '''

        L = []
        for i in list_of_dates:
            L.append(i[2:6])
            
        return list(set(L))
    
    def _get_firstname_initiales(row):
        row = row.replace('-',' ')
        row_list = row.split(' ')
        initiale_list = [x[0] for x in row_list]
        initiales = ''.join(initiale_list) 
        
        return initiales

    # Setting useful aliases and path
    matricule_alias = COL_NAMES_RH["ID"] # A importer depuis les globales
    listing_alias                   = ARCHI_RH["root"]
    effectifs_folder_name_alias     = ARCHI_RH["effectifs"]
    effectifs_file_name_alias       = ARCHI_RH["effectifs file name"]
    maj_effectifs_folder_name_alias = ARCHI_RH["maj"] 
    backup_folder_name_alias        = ARCHI_SECOURS["root"]
    
    # Setting useful paths
    effectifs_root_path       = bibliometer_path / Path(listing_alias)
    effectifs_folder_path     = effectifs_root_path / Path(effectifs_folder_name_alias)
    maj_effectifs_folder_path = effectifs_root_path / Path(maj_effectifs_folder_name_alias)    
    backup_root_path          = bibliometer_path / Path(backup_folder_name_alias)    
    
    # Setting path of employees file 
    try:
        effectifs_file_name = os.listdir(effectifs_folder_path)[0]
        effectifs_file_path = effectifs_folder_path / Path(effectifs_file_name)
    except FileNotFoundError:
        print(f"""Il y a un problème dans le nom du répertoire {ARCHI_RH["effectifs"]}""")
    except IndexError:
        error_message  = f"Le fichier des effectifs consolidés est introuvable "
        error_message += f"dans le dossier : \n\n {effectifs_folder_path}"
        print(error_message)
    
    # Setting path of file for update of employees file 
    try:
        maj_effectifs_file_name = os.listdir(maj_effectifs_folder_path)[0]
        maj_effectifs_file_path = maj_effectifs_folder_path / Path(maj_effectifs_file_name)
    except FileNotFoundError:
        print(f"Le nom de répertoire {maj_effectifs_folder_name_alias} est incorrect.")
    except IndexError:
        error_message  = f"Aucun fichier de mise à jour des effectifs n'est disponible "
        error_message += f"dans le dossier : \n\n {maj_effectifs_folder_path}"
        print(error_message)

    # Setting dataframes from the files
    df_effectif = pd.read_excel(effectifs_file_path, sheet_name = None)
    df_to_add = pd.read_excel(maj_effectifs_file_path, sheet_name = None)

    # Getting sheets names
    effectif_sheets = list(df_effectif.keys())
    to_add_sheets = list(df_to_add.keys())

    # Ajouter
    step = 0
    for page_to_add in to_add_sheets:
        year = _get_year(page_to_add)
        if year in effectif_sheets:
            df_effectif[year] = pd.concat([df_effectif[year], df_to_add[page_to_add]], ignore_index = False)
        else:
            df_effectif[year] = pd.DataFrame(df_to_add[page_to_add].copy())
            effectif_sheets.append(year)

    # Et dédupliquer en ajoutant les colonnes Initials et Name + Initials
    years_to_dedup = _different_years(to_add_sheets)
    for page_to_dedup in years_to_dedup:
        df_effectif[page_to_dedup].drop_duplicates(subset = [matricule_alias], inplace = True)
    
        # Creating a column with first name initials as a list
        # ex PIERRE -->P, JEAN-PIERRE --> JP , JEAN-PIERRE MARIE --> JPM 
        col_in, col_out = COL_NAMES_RH['prénom'], COL_NAMES_BM['First_name']
        df_effectif[page_to_dedup][col_out] = df_effectif[page_to_dedup].apply(lambda row: 
                                                                               _get_firstname_initiales(row[col_in]), 
                                                                               axis = 1)

        # Creating the column ['Full_name'] by combining COL_NAMES_RH['Nom'] and COL_NAMES_BM['First_name']
        new_col = COL_NAMES_RH['Full_name']
        df_effectif[page_to_dedup][new_col]  = df_effectif[page_to_dedup][COL_NAMES_RH['nom']] 
        df_effectif[page_to_dedup][new_col] += ' ' + df_effectif[page_to_dedup][COL_NAMES_BM['First_name']]
        
    # Création de l'Excel Writer Object
    with pd.ExcelWriter(effectifs_file_path) as writer:
        for page_effectif in effectif_sheets:
            df_effectif[page_effectif].to_excel(writer, 
                                                sheet_name = page_effectif, 
                                                index = False)
    
    # Copie de la mise à jour dans la zone de sauvegarde
    filePath = shutil.copy(effectifs_file_path, backup_root_path)
    
            
def mise_en_page(df):
    
    ''' 
        
    '''
    
    # 3rd party imports
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows as openpyxl_dataframe_to_rows
    from openpyxl.utils import get_column_letter as openpyxl_get_column_letter
    from openpyxl.styles import Font as openpyxl_Font  
    from openpyxl.styles import PatternFill as openpyxl_PatternFill 
    from openpyxl.styles import Alignment as openpyxl_Alignment
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_SIZES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import ROW_COLORS

    cell_colors = [openpyxl_PatternFill(fgColor = ROW_COLORS['odd'], fill_type = "solid"),
                  openpyxl_PatternFill(fgColor = ROW_COLORS['even'], fill_type = "solid")]

    columns_list = list(df.columns)
    
    # Initialize wb as a workbook and ws its active worksheet
    wb = Workbook()
    ws = wb.active
    ws_rows = openpyxl_dataframe_to_rows(df, index=False, header=True)
    
    #  Coloring alternatly rows in ws
    for idx, row in enumerate(ws_rows):
        ws.append(row)        
        last_row = ws[ws.max_row]            
        if idx >= 1:
            cell_color = cell_colors[idx%2]
            for cell in last_row:
                cell.fill = cell_color

    for cell in ws['A'] + ws[1]:
        cell.font = openpyxl_Font(bold=True)
        cell.alignment = openpyxl_Alignment(horizontal="center", vertical="center")

    for idx, col in enumerate(columns_list):
        if idx >= 1:
            column_letter = openpyxl_get_column_letter(idx + 1)
            try:
                ws.column_dimensions[column_letter].width = COL_SIZES[col]
            except:
                ws.column_dimensions[column_letter].width = 20
    
    first_row_num = 1
    ws.row_dimensions[first_row_num].height = 30

    return wb, ws


def rename_column_names(df, dictionnary = None):
    '''
    The function `rename_column_names` changes names of columns of the DataFrame.
    
    Args:
        df (pandas.DataFrame()):
        dictionnary (dict):
    
    Returns:
        df (pandas.DataFrame()):
    
    Notes:
        Uses COL_NAMES_FINALE from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables
    '''
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_FINALE
    
    if dictionnary == None: dictionnary = COL_NAMES_FINALE        
    df.rename(columns = dictionnary, inplace = True)
    
    return df


def find_missing_if(bibliometer_path, in_file_path):
    
    '''
    Genère un fichier des ISSN dont l'impact factor n'est pas dans la base de donnée.
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd 
    
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_GUI.Globals_GUI import ARCHI_IF

    # setting useful aliases
    if_issn_alias    = COL_NAMES['articles'][10]
    if_year_alias    = COL_NAMES['articles'][2]
    if_journal_alias = COL_NAMES['articles'][3]    
    if_annee_publi_alias = COL_NAMES_BONUS['IF année publi']
    if_root_folder_alias    = ARCHI_IF["root"]
    if_manquants_file_alias = ARCHI_IF["missing"] 
       
    out_folder_path = bibliometer_path / Path(if_root_folder_alias)
    out_file_path = out_folder_path / Path(if_manquants_file_alias)

    df = pd.read_excel(in_file_path)
    
    issn_list = list()
    for i in range(len(df)):
        if_value = df[if_annee_publi_alias][i]
        if if_value == 'unknown' or if_value == 'Not available':
            issn_value    = df[if_issn_alias][i]
            year_value    = df[if_year_alias][i]
            journal_value = df[if_journal_alias][i]
            issn_list.append([issn_value, year_value, journal_value])
    
    df = pd.DataFrame(issn_list, columns = [if_issn_alias, if_year_alias, if_journal_alias])
    df.drop_duplicates(inplace = True)
    
    df.to_excel(out_file_path, index = False)
    
    end_message  = f"List of ISSNs without IF saved in folder: \n '{out_folder_path}'"
    end_message += f"\n\n under file '{if_manquants_file_alias}'"
    return end_message