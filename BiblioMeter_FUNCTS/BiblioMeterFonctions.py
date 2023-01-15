__all__ = ['get_unique_numbers',           
           'consolidation_homonyme',          
           'concat_name_firstname',
           'add_authors_name_list',
           'add_OTP',           
           'filtrer_par_departement',            
           'add_biblio_list',
           'add_if',
           'clean_reorder_rename_submit',           
           'concat_listes_consolidees',          
           'maj_rh',           
           'mise_en_page',            
           'rename_column_names',          
           'find_missing_if']

def get_unique_numbers(numbers):

    list_of_unique_numbers = []

    unique_numbers = set(numbers)

    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

def consolidation_homonyme(in_path, out_path):

    # Standard library imports
    from pathlib import Path
    import math

    # 3rd party import
    import pandas as pd
    from openpyxl import Workbook, load_workbook
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.utils.cell import get_column_letter
    from openpyxl.comments import Comment
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.styles.colors import Color

    # BiblioAnalysis_Utils package imports    
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH 
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_CONSOLIDATION

    # Useful alias
    pub_id_alias = COL_NAMES['pub_id']
    idx_author = COL_NAMES['authors'][1]
    dpt_alias = COL_NAMES_RH['dpt']
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
    
    yellow_ft = PatternFill(fgColor = '00FFFF00', fill_type = "solid")

    for indice, r in enumerate(dataframe_to_rows(df_submit, index=False, header=True)):
        ws.append(r)
        last_row = ws[ws.max_row]
        if r[col_conso_alias.index(homonym_alias)] == homonym_alias and indice > 0:
            cell = last_row[col_conso_alias.index('Nom')]
            cell.fill = yellow_ft
            cell = last_row[col_conso_alias.index('Prénom')]
            cell.fill = yellow_ft
            
    wb.save(out_path)
    
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
    
    ''' The `add_authors_fullname_list` function fetches an EXCEL file and saves it in 'df_in'. 
    It then uses `concat_name_firstname` to create the column 'Nom Prénom'.
    Then it goes through a unique list of Pub_id and adds in every single row of a new dataframe, 
    which is a slice of df_in by the Pub_id, called 'df_inter' a new column 
    called 'Authors Fullname List', a list of all the authors who participated in writting the article. 
    Happens this new dataframe to 'df_out' and when done going through
    all of the different Pub_id, it saves it into out_path as an EXCEL file.
    
    Args:
        in_path (path): path (including name of the file) leading to the working excel file. 
        out_path (path): path (including name of the file) leading to where the file will be 
                         saved after going through its treatment.
    
    Returns:
        None.
    
    Notes:
        The global 'COL_NAMES' is imported from 'BiblioSpecificGlobals' module 
        of 'BiblioAnalysis_Utils' package.
        The function `concat_name_firstname` is imported from 'BiblioMeterFonctions' 
        module of 'BiblioMeter_FUNCTS' package.    
    '''
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    
    # 3rd party imports
    import pandas as pd
    
    # Useful alias
    pub_id_alias = COL_NAMES['pub_id']
    full_name_alias = COL_NAMES_BONUS['nom prénom']
    full_name_list_alias = COL_NAMES_BONUS['nom prénom liste']
    idx_authors_alias = COL_NAMES['authors'][1]
    
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
    unique_pub_id_list = df_in[pub_id_alias].unique().tolist()
    
    for i in unique_pub_id_list:
        filtre_inter_pub_id = (df_in[pub_id_alias] == i)
        df_inter = df_in[filtre_inter_pub_id]
        df_inter.sort_values(by = idx_authors_alias, inplace = True)
        authors_fullname_list = '; '.join(df_inter[full_name_alias].tolist())
        df_inter[full_name_list_alias] = authors_fullname_list
        df_out = df_out.append(df_inter)
        
    # Save in an excel file where leads out_path
    df_out.to_excel(out_path, index = False)
    
def add_OTP(in_path, out_path, out_file_base):

    '''
    '''
    
    # Standard library imports
    from pathlib import Path

    # 3rd party import
    import pandas as pd
    from openpyxl import Workbook, load_workbook
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.utils.cell import get_column_letter
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_OTP
    from BiblioMeter_GUI.Globals_GUI import DPT_LABEL_DICT
    
    # Internal functions
    def _save_dpt_OTP_file(dpt_label):
        '''
        '''
        filtre_dpt = df_submit[dpt_alias] == dpt_label
        df_dpt= df_submit[filtre_dpt].copy()
        _=[_you_got_OTPed(df_dpt, i) for i in range(len(df_dpt))]        
        df_dpt = df_dpt.reindex(columns = COL_OTP)        
        wb, ws = mise_en_page(df_dpt)
        ws.title = 'OTP ' +  dpt_label             
        for i in range(2, len(df_dpt)+2):
                # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière
                validation_list = _liste_de_validation(df_dpt, i-2)     
                data_val = DataValidation(type="list", formula1 = validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)
                # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière
                data_val.add(ws[get_column_letter(list(df_dpt.columns).index(OTP_alias)+1)+str(i)]) 
        OTP_file_name_dpt = out_file_base + '_' + dpt_label + '.xlsx'
        wb.save(out_path / Path(OTP_file_name_dpt))
        

    # Useful aliases
    pub_id_alias = COL_NAMES['pub_id']      # Pub_id
    dpt_alias = COL_NAMES_RH['dpt']         # Dpt/DOB (lib court)
    OTP_alias = COL_NAMES_BONUS['list OTP'] # Choix de l'OTP
    idx_author = COL_NAMES['authors'][1]    # Idx_author
    
    add_authors_name_list(in_path, in_path) # Adds a column with a list of the authors
    
    df_submit = pd.read_excel(in_path)
    df_submit.fillna('', inplace=True)
    df_submit.set_index(pub_id_alias, inplace = True)
    
    dpt_label_list = list(DPT_LABEL_DICT.keys())
        
    data = [0] * len(df_submit)
    for dpt_label in dpt_label_list: df_submit[dpt_label] = data
    
    for i in df_submit.index.unique().to_list():
        
        if isinstance(df_submit.loc[i], pd.Series):
            df_inter_pub_id = df_submit.loc[i].to_frame().T
        else:
            df_inter_pub_id = df_submit.loc[i]

        for j in df_inter_pub_id[idx_author]:

            filtre_inter_author = df_inter_pub_id[idx_author] == j
            df_inter_inter = df_inter_pub_id[filtre_inter_author]
            
            for dpt_label in dpt_label_list:
                for dpt_name in DPT_LABEL_DICT[dpt_label]:
                    if df_inter_inter[dpt_alias].to_list()[0] == dpt_name:
                        df_submit.loc[i,dpt_label] = 1    

    df_submit.sort_values([pub_id_alias, idx_author], inplace = True)
    df_submit.reset_index(inplace = True)
    df_submit.drop_duplicates(subset = [pub_id_alias], inplace = True)
    
    for dpt_label in dpt_label_list: _save_dpt_OTP_file(dpt_label)
    

def filtrer_par_departement(in_path, out_path, in_file_base):
    
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
    OTP_df_init = True
    for dpt_label in dpt_label_list:
        dpt_df =  _set_df_OTP_dpt(dpt_label)
        if OTP_df_init:
            OTP_df = dpt_df.copy()            
        else:
            OTP_df = OTP_df.append(dpt_df)
        OTP_df_init = False
    
    # df_OTP.fillna('', inplace=True)
    OTP_df.set_index(pub_id_alias, inplace = True)
   
    OTP_df.sort_values([pub_id_alias], inplace = True)
    OTP_df.reset_index(inplace = True)
    OTP_df.drop_duplicates(subset = [pub_id_alias], inplace = True)
    OTP_df.set_index(pub_id_alias, inplace = True)
    rename_column_names(OTP_df)
    OTP_df.to_excel(out_path, index = False)
    return 1
    

def add_biblio_list(in_path, out_path):
    ''' The function `add_biblio_list` adds a new column containing the full reference of each publication listed in an EXCEL file and saves it.
    The full reference is built by concatenating the folowing items: title, first author, year, journal, DOI.
    These items sould be available in the initial EXCEL file with columns names defined by the global 'COL_NAMES' with the keys 'pub_id' and 'articles'.
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

    # Setting useful aliases
    pub_id_alias           = COL_NAMES['pub_id']
    pub_first_author_alias = COL_NAMES['articles'][1]
    pub_year_alias         = COL_NAMES['articles'][2]
    pub_journal_alias      = COL_NAMES['articles'][3]
    pub_doi_alias          = COL_NAMES['articles'][6]
    pub_title_alias        = COL_NAMES['articles'][9]   
    pub_full_ref_alias     = COL_NAMES_BONUS['liste biblio']

    # Read of the excel file
    articles_df = pd.read_excel(in_path)

    articles_plus_fullref_df = pd.DataFrame()
    for pub_id, pub_id_df in articles_df.groupby(pub_id_alias): # Split the frame into subframes with same Pub_id
        
        pub_id_first_row = pub_id_df.iloc[0]                                # Select the first row and build the full reference
        full_ref  = f'{pub_id_first_row[pub_title_alias]}, '                # add the reference's title
        full_ref += f'{pub_id_first_row[pub_first_author_alias]}. et al., ' # add the reference's first author
        full_ref += f'{pub_id_first_row[pub_journal_alias]}, '              # add the reference's journal name
        full_ref += f'{str(pub_id_first_row[pub_year_alias])}, '            # add the reference's publication year
        full_ref += f'{pub_id_first_row[pub_doi_alias]}'                    # add the reference's DOI
        
        pub_id_df[pub_full_ref_alias] = full_ref
        articles_plus_fullref_df = pd.concat([articles_plus_fullref_df, pub_id_df])

    articles_plus_fullref_df.to_excel(out_path, index = False)  
    
    
def add_if(in_file_path, out_file_path, if_path, year):
    
    ''' 

    Args:
        in_file_path (path): path (including name of the file if year != None) leading to the working excel file. 
        out_path (path): path (including name of the file) leading to where the file will be saved after going through its treatment.
        if_path (path): path (including name of the file) leading to the impact factor excel file.
        year (int):
    
    Returns:
    
    Notes:
    
    '''
        
    # Standard imports
    from pathlib import Path

    # Local imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_OTP
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_MAJ_IF
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import FILL_EMPTY_KEY_WORD

    # 3rd party imports
    import pandas as pd

    # Setting useful aliases
    issn_alias     = COL_NAMES['articles'][10]
    eissn_alias    = COL_NAMES_BONUS['EISSN']
    if_alias       = COL_NAMES_BONUS['IF clarivate']
    if_cours_alias = COL_NAMES_BONUS['IF en cours']
    if_publi_alias = COL_NAMES_BONUS['IF année publi']
    
    df_submit = pd.read_excel(in_file_path) # Ma DataFrame
    
    if year == None:
        df_if = pd.read_excel(if_path, sheet_name = None)
        
        # using dictionary to convert type of  Year column
        convert_dict = {'Year': str}
        df_submit = df_submit.astype(convert_dict)

        list_annee = list(df_submit['Year'].unique())
        try :
            list_annee.remove(FILL_EMPTY_KEY_WORD)
        except ValueError:
            pass
        
        # Maintenant qu'on a les années, on boucle dessus pour appliquer un filtre sur la df et changer les IF en conséquence.
        df_submit_bis = pd.DataFrame()
        for annee in list_annee:
            print(f"L'année en cours de traitement est la suivante : {annee}")
            df_inter = df_submit[df_submit['Year'] == annee]
            
            try:
                dict1 = dict(zip(df_if[annee][issn_alias], df_if[annee][if_alias]))
                s = df_inter[issn_alias]     # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1)             # Je map la Series avec mon dictionnaire
                df_inter[if_publi_alias] = r # Je rajoute la colonne à ma DataFrame
                
                # Appliquer nan --> unknow to df
                df_inter[if_publi_alias] = df_inter[if_publi_alias].fillna(FILL_EMPTY_KEY_WORD)
                
                #print(f"La colonne {if_publi_alias} a été rajoutée avec succès pour l'année {annee}")
                # Mon dictionnaire construit à partir de mon fichier excel
                dict1 = dict(zip(df_if[list(df_if.keys())[-1]][issn_alias], df_if[list(df_if.keys())[-1]][if_alias])) 
                s = df_inter[issn_alias]     # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1)             # Je map la Series avec mon dictionnaire
                df_inter[if_cours_alias] = r # Je rajoute la colonne à ma DataFrame
                
                # Appliquer nan --> unknown to df
                df_inter[if_cours_alias] = df_inter[if_cours_alias].fillna(FILL_EMPTY_KEY_WORD)
                
                #print(f"La colonne {if_cours_alias} a été rajoutée avec succès pour l'année {annee}, \
                #avec les IF de l'année {list(df_if.keys())[-1]}")

                df_submit_bis = df_submit_bis.append(df_inter)
                
            except KeyError:
                # Mon dictionnaire construit à partir de mon fichier excel
                dict1 = dict(zip(df_if[list(df_if.keys())[-1]][issn_alias], df_if[list(df_if.keys())[-1]][if_alias])) 
                s = df_inter[issn_alias]                   # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1)                           # Je map la Series avec mon dictionnaire
                df_inter[if_cours_alias] = r               # Je rajoute la colonne à ma DataFrame
                df_inter[if_publi_alias] = 'Not available' # Je rajoute la colonne à ma DataFrame

                # Appliquer nan --> unknow to df
                df_inter[if_cours_alias] = df_inter[if_cours_alias].fillna(FILL_EMPTY_KEY_WORD)
                df_inter[if_publi_alias] = df_inter[if_publi_alias].fillna(FILL_EMPTY_KEY_WORD)
                
                #print(f"Les colonnes {if_publi_alias} et {if_cours_alias} ont été rajoutées avec succès pour l'année {annee}")

                df_submit_bis = df_submit_bis.append(df_inter)
            
        #print(df_submit_bis.columns)
            
        df_submit_bis.to_excel(out_file_path, index = False, columns = COL_MAJ_IF)
                
    
    else: # Mode de fonctionnement par année
        # Check if the year is available
        try:
            df_if = pd.read_excel(if_path, sheet_name = str(year))
            # Ca fonctionne, alors on ajoute la colonne IF de l'année de publication
            print(f"Les IF sortis en {year} sont utilisés pour créer la colonne {if_publi_alias}")

            dict1 = dict(zip(df_if[issn_alias], df_if[if_alias])) # Mon dictionnaire construit à partir de mon fichier excel
            s = df_submit[issn_alias]     # Je récup la colonne clef de ma DF en Series
            r = s.map(dict1)              # Je map la Series avec mon dictionnaire
            df_submit[if_publi_alias] = r # Je rajoute la colonne à ma DataFrame

            # Appliquer nan --> unknow to df
            df_submit[if_publi_alias] = df_submit[if_publi_alias].fillna(FILL_EMPTY_KEY_WORD)

            # Et on fait pareil avec les IF de l'année en cours
            df_if = pd.read_excel(if_path, sheet_name = None)
            print(f"Les IF sortis en {int(list(df_if.keys())[-1])} sont utilisés pour créer la colonne {if_cours_alias}")
            
            # Mon dictionnaire construit à partir de mon fichier excel
            dict1 = dict(zip(df_if[list(df_if.keys())[-1]][issn_alias], df_if[list(df_if.keys())[-1]][if_alias])) 
            s = df_submit[issn_alias]     # Je récup la colonne clef de ma DF en Series
            r = s.map(dict1)              # Je map la Series avec mon dictionnaire
            df_submit[if_cours_alias] = r # Je rajoute la colonne à ma DataFrame

            # Appliquer nan --> unknow to df
            df_submit[if_cours_alias] = df_submit[if_cours_alias].fillna(FILL_EMPTY_KEY_WORD)

            df_submit.to_excel(out_file_path, index = False)

        except ValueError:
            # Check if the year is available, if not, terminate function
            try:
                # Et on fait pareil avec les IF de l'année en cours
                df_if = pd.read_excel(if_path, sheet_name = None)
                print(f"Les IF sortis en {int(list(df_if.keys())[-1])} sont utilisés pour créer la colonne {if_cours_alias}")
                # Mon dictionnaire construit à partir de mon fichier excel
                dict1 = dict(zip(df_if[list(df_if.keys())[-1]][issn_alias], df_if[list(df_if.keys())[-1]][if_alias])) 
                s = df_submit[issn_alias]                    # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1)                            # Je map la Series avec mon dictionnaire
                df_submit[if_cours_alias] = r               # Je rajoute la colonne à ma DataFrame
                df_submit[if_publi_alias] = 'Not available' # Je rajoute la colonne à ma DataFrame

                # Appliquer nan --> unknow to df
                df_submit[if_cours_alias] = df_submit[if_cours_alias].fillna(FILL_EMPTY_KEY_WORD)
                df_submit[if_publi_alias] = df_submit[if_publi_alias].fillna(FILL_EMPTY_KEY_WORD)

                df_submit.to_excel(out_file_path, index = False)

            except ValueError:
                print('Mettre à jour le fichier Impact Factor')
                

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
    
    
def concat_listes_consolidees(bibliometer_path, years_list):
    
    """
    """
    # Standard library imports
    from pathlib import Path
    import os
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
    
        
def maj_rh(bibliometer_path):
    '''
    '''
    
    # Standard library imports
    import os
    from pathlib import Path
    from datetime import datetime
    
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

        # Imports
        import datetime

        try:
            today_year = datetime.date.today().year
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

    # Alias
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
        #path_effectif_file = Path(bibliometer_path) / Path(ARCHI_RH["root"]) / Path(ARCHI_RH["effectifs"]) / os.listdir(effectifs_folder_path)[0]
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
        #path_to_add_file = Path(bibliometer_path) / Path(ARCHI_RH["root"]) / Path(ARCHI_RH["maj"]) / os.listdir(maj_effectifs_folder_path)[0]
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
    import pandas as pd
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.styles.colors import Color

    # Local library imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_SIZES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    wb = Workbook()
    ws = wb.active

    red_ft = PatternFill(fgColor = '00FF0000', fill_type = "solid")
    blue_ft = PatternFill(fgColor = '0000FFFF', fill_type = "solid")
    bd = Side(style='medium', color="000000")
    active_color = 'red'

    pub_id_unique_list = list(df[COL_NAMES['pub_id']].unique())
    columns_list = list(df.columns)

    def _le_reste(num, la_list):
        return la_list.index(num)%2 == 0

    for indice, r in enumerate(dataframe_to_rows(df, index=False, header=True)):
        ws.append(r)        
        last_row = ws[ws.max_row]
        if indice >= 1:
            if _le_reste(df[COL_NAMES['pub_id']].iloc[indice-1], pub_id_unique_list):
                cell = last_row[0]
                cell.fill = red_ft
                if active_color != 'red':
                    for cell_bis in last_row:
                        cell_bis.border = Border(top = bd)
                        active_color = 'red'
            else:
                cell = last_row[0]
                cell.fill = blue_ft
                if active_color != 'blue':
                    for cell_bis in last_row:
                        cell_bis.border = Border(top = bd)
                        active_color = 'blue'

    for cell in ws['A'] + ws[1]:
        cell.font = Font(bold=True)
        cell.border = Border(left = bd, top = bd, right = bd, bottom = bd)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for i, col in enumerate(columns_list):
        if i >= 1:
            try:
                ws.column_dimensions[get_column_letter(i+1)].width = COL_SIZES[col]
                # ws.column_dimensions[get_column_letter(i+1)].set_text_wrap()
            except:
                ws.column_dimensions[get_column_letter(i+1)].width = 15
                
    #format = wb.add_format({'text_wrap': True})

    ## Setting the format but not setting the column width.
    #ws.set_column('H:I', None, format)

    ws.row_dimensions[1].height = 30

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
    
    return print('Done')