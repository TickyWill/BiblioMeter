__all__ = ['get_unique_numbers',
           
           'consolidation_homonyme',
           
           'concat_name_firstname',
           'add_authors_name_list',
           'ajout_OTP',
           
           'filtrer_par_departement', 
           
           'add_biblio_list',
           'ajout_IF',
           'clean_reorder_rename_submit',
           
           'concat_listes_consolidees',
          
           'maj_rh',
           
           'mise_en_page', 
           
           'rename_column_names', 
          
           'ISSN_manquant']

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

    # Local library imports
    import BiblioMeter_FUNCTS as bmf
        
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME
    from BiblioMeter_GUI.Globals_GUI import ORPHAN_FILE_NAME
    
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
    import BiblioMeter_FUNCTS as bmf
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
    
    # Local imports
    import BiblioMeter_FUNCTS as bmf
    
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
    If so, it combines the column 'Nom' and 'Prénom' adding a ', ' in between the two values of the columns, into a new column named 'Nom Prénom'.
    
    Args:
        df (dataframe): dataframe in which we want to combine the Nom and Prénom.
        
    Returns:
        df (dataframe): the dataframe given as variable but with the new column.
    
    Notes:
        None.
    '''
    
    # Local library imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
    
    # 3rd party imports
    import pandas as pd
    
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
    
    ''' The `add_authors_fullname_list` function fetches an EXCEL file and saves it in 'df_in'. It then uses `concat_name_firstname` to create the column 'Nom Prénom'.
    Then it goes through a unique list of Pub_id and adds in every single row of a new dataframe, which is a slice of df_in by the Pub_id, called 'df_inter' a new column 
    called 'Authors Fullname List', a list of all the authors who participated in writting the article. Happens this new dataframe to 'df_out' and when done going through
    all of the different Pub_id, it saves it into out_path as an EXCEL file.
    
    Args:
        in_path (path): path (including name of the file) leading to the working excel file. 
        out_path (path): path (including name of the file) leading to where the file will be saved after going through its treatment.
    
    Returns:
        None.
    
    Notes:
        The global 'COL_NAMES' is imported from 'BiblioSpecificGlobals' module of 'BiblioAnalysis_Utils' package.
        The function `concat_name_firstname` is imported from 'BiblioMeterFonctions' module of 'BiblioMeter_FUNCTS' package.    
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
        raise KeyError(f"The column {pub_id_alias} is not in DataFrame. Cannot carry on. Please make sure the DataFrame has a column named 'Pub_id'.")
    
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
    
def ajout_OTP(in_path, out_path):

    '''
    '''
    
    # Standard library imports
    from pathlib import Path

    # Local library imports
    import BiblioMeter_FUNCTS as bmf
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_OTP
    
    # 3rd party import
    import pandas as pd
    from openpyxl import Workbook, load_workbook
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.utils.cell import get_column_letter

    # Useful alias
    pub_id_alias = COL_NAMES['pub_id'] # Pub_id
    dpt_alias = COL_NAMES_RH['dpt'] # Dpt/DOB (lib court)
    OTP_alias = COL_NAMES_BONUS['list OTP'] # Choix de l'OTP
    idx_author = COL_NAMES['authors'][1] # Idx_author
    
    add_authors_name_list(in_path, in_path) # Adds a column with a list of the authors
    
    df_submit = pd.read_excel(in_path)
    df_submit.fillna('', inplace=True)
    df_submit.set_index(pub_id_alias, inplace = True)
        
    data = [0] * len(df_submit)
    df_submit['DTNM'] = data
    df_submit['DTS'] = data
    df_submit['DTCH'] = data
    df_submit['DEHT'] = data
    ###############################################################################################################################################################

    for i in df_submit.index.unique().to_list():
        
        if isinstance(df_submit.loc[i], pd.Series):
            df_inter_pub_id = df_submit.loc[i].to_frame().T
        else:
            df_inter_pub_id = df_submit.loc[i]

        for j in df_inter_pub_id[idx_author]:

            filtre_inter_author = df_inter_pub_id[idx_author] == j
            df_inter_inter = df_inter_pub_id[filtre_inter_author]

            if df_inter_inter[dpt_alias].to_list()[0] == 'DTNM':
                df_submit.loc[i,'DTNM'] = 1

            elif df_inter_inter[dpt_alias].to_list()[0] == 'DTS':
                df_submit.loc[i,'DTS'] = 1

            elif df_inter_inter[dpt_alias].to_list()[0] == 'DEHT':
                df_submit.loc[i,'DEHT'] = 1

            elif df_inter_inter[dpt_alias].to_list()[0] == 'DTCH':
                df_submit.loc[i,'DTCH'] = 1
                
            elif df_inter_inter[dpt_alias].to_list()[0] == 'DTBH':
                df_submit.loc[i,'DTCH'] = 1
                
    df_submit.sort_values([pub_id_alias, idx_author], inplace = True)
    df_submit.reset_index(inplace = True)
    df_submit.drop_duplicates(subset = [pub_id_alias], inplace = True)
    
    ### DTNM
    filtre_DTNM = df_submit[dpt_alias] == 'DTNM'
    df_DTNM = df_submit[filtre_DTNM].copy()
    _=[_you_got_OTPed(df_DTNM, i) for i in range(len(df_DTNM))]
    
    df_DTNM = df_DTNM.reindex(columns = COL_OTP)
    
    wb, ws = mise_en_page(df_DTNM)
    ws.title = 'OTP DTNM'
         
    for i in range(2, len(df_DTNM)+2):
            
            validation_list = _liste_de_validation(df_DTNM, i-2) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

            data_val = DataValidation(type="list", formula1 = validation_list, showErrorMessage=False)
            ws.add_data_validation(data_val)
            
            data_val.add(ws[get_column_letter(list(df_DTNM.columns).index(OTP_alias)+1)+str(i)]) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTNM.xlsx'))
    
    ### DTS
    filtre_DTS = df_submit[dpt_alias] == 'DTS'
    df_DTS = df_submit[filtre_DTS].copy()
    _=[_you_got_OTPed(df_DTS, i) for i in range(len(df_DTS))]
    
    df_DTS = df_DTS.reindex(columns = COL_OTP)
    
    wb, ws = mise_en_page(df_DTS)
    ws.title = 'OTP DTS'
        
    for i in range(2, len(df_DTS)+2):
            
            validation_list = _liste_de_validation(df_DTS, i-2) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

            data_val = DataValidation(type="list", formula1 = validation_list, showErrorMessage=False)
            ws.add_data_validation(data_val)
            
            data_val.add(ws[get_column_letter(list(df_DTS.columns).index(OTP_alias)+1)+str(i)]) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTS.xlsx'))
    
    ### DEHT
    filtre_DEHT = df_submit[dpt_alias] == 'DEHT'
    df_DEHT = df_submit[filtre_DEHT].copy()
    _=[_you_got_OTPed(df_DEHT, i) for i in range(len(df_DEHT))]
    
    df_DEHT = df_DEHT.reindex(columns = COL_OTP)
    
    wb, ws = mise_en_page(df_DEHT)
    ws.title = 'OTP DEHT'
    
    for i in range(2, len(df_DEHT)+2):
            
            validation_list = _liste_de_validation(df_DEHT, i-2) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

            data_val = DataValidation(type="list", formula1 = validation_list, showErrorMessage=False)
            ws.add_data_validation(data_val)
            
            data_val.add(ws[get_column_letter(list(df_DEHT.columns).index(OTP_alias)+1)+str(i)]) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

    wb.save(out_path / Path(f'fichier_ajout_OTP_DEHT.xlsx'))
    
    ### DTCH
    filtre_DTCH = (df_submit[dpt_alias] == 'DTCH') | (df_submit[dpt_alias] == 'DTBH')
    df_DTCH = df_submit[filtre_DTCH].copy()
    _=[_you_got_OTPed(df_DTCH, i) for i in range(len(df_DTCH))]
    
    df_DTCH = df_DTCH.reindex(columns = COL_OTP)
    
    wb, ws = mise_en_page(df_DTCH)
    ws.title = 'OTP DTCH'
        
    for i in range(2, len(df_DTCH)+2):
            
            validation_list = _liste_de_validation(df_DTCH, i-2) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

            data_val = DataValidation(type="list", formula1 = validation_list, showErrorMessage=False)
            ws.add_data_validation(data_val)
            
            data_val.add(ws[get_column_letter(list(df_DTCH.columns).index(OTP_alias)+1)+str(i)]) # Décalage obligatoire car Excel et Python ne réagisse pas de la même manière

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTCH.xlsx'))

def filtrer_par_departement(in_path, out_path):
    
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

    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # 3rd party imports
    import pandas as pd
    
    # Useful alias
    pub_id_alias = COL_NAMES['pub_id']
    chemin_DTNM = in_path / Path('fichier_ajout_OTP_DTNM_ok.xlsx')
    chemin_DTS = in_path / Path('fichier_ajout_OTP_DTS_ok.xlsx')
    chemin_DEHT = in_path / Path('fichier_ajout_OTP_DEHT_ok.xlsx')
    chemin_DTCH = in_path / Path('fichier_ajout_OTP_DTCH_ok.xlsx')

    ### Charger les df et ajouter les 4 colonnes ###################################################################################################################
    if os.path.exists(chemin_DTNM):
        df_DTNM = pd.read_excel(chemin_DTNM)
    else:
        chemin_DTNM = in_path / Path('fichier_ajout_OTP_DTNM.xlsx')
        df_DTNM = pd.read_excel(chemin_DTNM)

    if os.path.exists(chemin_DTS):
        df_DTS = pd.read_excel(chemin_DTS)
    else:
        chemin_DTS = in_path / Path('fichier_ajout_OTP_DTS.xlsx')
        df_DTS = pd.read_excel(chemin_DTS)
    if os.path.exists(chemin_DEHT):
        df_DEHT = pd.read_excel(chemin_DEHT)
    else:
        chemin_DEHT = in_path / Path('fichier_ajout_OTP_DEHT.xlsx')
        df_DEHT = pd.read_excel(chemin_DEHT)
    if os.path.exists(chemin_DTCH):
        df_DTCH = pd.read_excel(chemin_DTCH)
    else:
        chemin_DTCH = in_path / Path('fichier_ajout_OTP_DTCH.xlsx')
        df_DTCH = pd.read_excel(chemin_DTCH)

    df_OTP = df_DTNM.copy()
    df_OTP = df_OTP.append(df_DTS)
    df_OTP = df_OTP.append(df_DEHT)
    df_OTP = df_OTP.append(df_DTCH)
    
    # df_OTP.fillna('', inplace=True)
    df_OTP.set_index(pub_id_alias, inplace = True)
   
    df_OTP.sort_values([pub_id_alias], inplace = True)
    df_OTP.reset_index(inplace = True)
    df_OTP.drop_duplicates(subset = [pub_id_alias], inplace = True)
    df_OTP.set_index(pub_id_alias, inplace = True)
    rename_column_names(df_OTP)
    df_OTP.to_excel(out_path)
    return 1

def add_biblio_list(in_path, out_path):
    ''' 
    
    Args:
        in_path (path): path (including name of the file) leading to the working excel file. 
        out_path (path): path (including name of the file) leading to where the file will be saved after going through its treatment.
    
    Returns:
        None.
    
    Notes:
        The global 'COL_NAMES' is imported from 'BiblioSpecificGlobals' module of 'BiblioAnalysis_Utils' package.
        The function `concat_name_firstname` is imported from 'BiblioMeterFonctions' module of 'BiblioMeter_FUNCTS' package.    
    '''
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS

    # 3rd party imports
    import pandas as pd

    # Useful alias
    pub_id_alias = COL_NAMES['pub_id']

    # Read of the excel file
    df_in = pd.read_excel(in_path)

    # Sort on Pub_id and then add the authors fullname list
    if pub_id_alias not in df_in:
        raise KeyError(f"The column {pub_id_alias} is not in DataFrame. Cannot carry on. Please make sure the DataFrame has a column named 'Pub_id'.")

    df_out = pd.DataFrame()
    unique_pub_id_list = df_in['Pub_id'].unique().tolist()

    for indice, i in enumerate(unique_pub_id_list):
        filtre_inter_pub_id = (df_in[pub_id_alias] == i)
        df_inter = df_in[filtre_inter_pub_id]

        # Remettre sous le bon format
        if len(df_inter) > 1:
            df_inter_2 = df_inter.iloc[0].to_frame().T
            
        df_inter_2 = df_inter

        list_biblio_inter = ''
        title_inter = ''
        auteur_inter = ''
        year_inter = ''
        journal_inter = ''
        DOI_inter = ''

        # Construction de la liste bibliographique :
        title_inter = ''.join(df_inter_2['Title'].to_list()[0])
        auteur_inter = ', '.join(''.join(df_inter_2['Full_name_eff'].to_list()[0]).split())
        year_inter = str(df_inter_2['Year'].iloc[0])
        journal_inter = ''.join(df_inter_2['Journal'].to_list()[0])
        DOI_inter = ''.join(df_inter_2['DOI'].to_list()[0])
        
        list_biblio_inter = title_inter + ', ' + auteur_inter + '. et al., ' + year_inter + ', ' + journal_inter + ', ' + DOI_inter

        df_inter[COL_NAMES_BONUS['liste biblio']] = list_biblio_inter
        df_out = df_out.append(df_inter)

    # Save in an excel file where leads out_path
    df_out.to_excel(out_path, index = False)
    
def ajout_IF(in_path, out_path, IF_path, year):
    
    ''' 

    Args:
        in_path (path): path (including name of the file if year != None) leading to the working excel file. 
        out_path (path): path (including name of the file) leading to where the file will be saved after going through its treatment.
        IF_path (path): path (including name of the file) leading to the impact factor excel file.
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

    # Useful alias
    ISSN_alias = COL_NAMES['articles'][10]
    EISSN_alias = COL_NAMES_BONUS['EISSN']
    IF_alias = COL_NAMES_BONUS['IF clarivate']
    IF_cours_alias = COL_NAMES_BONUS['IF en cours']
    IF_publi_alias = COL_NAMES_BONUS['IF année publi']
    
    df_submit = pd.read_excel(in_path) # Ma DataFrame
    
    #print(COL_MAJ_IF)
    #print(df_submit.columns)
    
    if year == None:
        df_IF = pd.read_excel(IF_path, sheet_name = None)
        
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
                dict1 = dict(zip(df_IF[annee][ISSN_alias], df_IF[annee][IF_alias]))
                s = df_inter[ISSN_alias] # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1) # Je map la Series avec mon dictionnaire
                df_inter[IF_publi_alias] = r # Je rajoute la colonne à ma DataFrame
                
                # Appliquer nan --> unknow to df
                df_inter[IF_publi_alias] = df_inter[IF_publi_alias].fillna(FILL_EMPTY_KEY_WORD)
                
                #print(f"La colonne {IF_publi_alias} a été rajoutée avec succès pour l'année {annee}")

                dict1 = dict(zip(df_IF[list(df_IF.keys())[-1]][ISSN_alias], df_IF[list(df_IF.keys())[-1]][IF_alias])) # Mon dictionnaire construit à partir de mon fichier excel
                s = df_inter[ISSN_alias] # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1) # Je map la Series avec mon dictionnaire
                df_inter[IF_cours_alias] = r # Je rajoute la colonne à ma DataFrame
                
                # Appliquer nan --> unknow to df
                df_inter[IF_cours_alias] = df_inter[IF_cours_alias].fillna(FILL_EMPTY_KEY_WORD)
                
                #print(f"La colonne {IF_cours_alias} a été rajoutée avec succès pour l'année {annee}, avec les IF de l'année {list(df_IF.keys())[-1]}")

                df_submit_bis = df_submit_bis.append(df_inter)
                
            except KeyError:
                
                dict1 = dict(zip(df_IF[list(df_IF.keys())[-1]][ISSN_alias], df_IF[list(df_IF.keys())[-1]][IF_alias])) # Mon dictionnaire construit à partir de mon fichier excel
                s = df_inter[ISSN_alias] # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1) # Je map la Series avec mon dictionnaire

                df_inter[IF_cours_alias] = r # Je rajoute la colonne à ma DataFrame
                df_inter[IF_publi_alias] = 'Not available' # Je rajoute la colonne à ma DataFrame

                # Appliquer nan --> unknow to df
                df_inter[IF_cours_alias] = df_inter[IF_cours_alias].fillna(FILL_EMPTY_KEY_WORD)
                df_inter[IF_publi_alias] = df_inter[IF_publi_alias].fillna(FILL_EMPTY_KEY_WORD)
                
                #print(f"Les colonnes {IF_publi_alias} et {IF_cours_alias} ont été rajoutées avec succès pour l'année {annee}")

                df_submit_bis = df_submit_bis.append(df_inter)
            
        #print(df_submit_bis.columns)
            
        df_submit_bis.to_excel(out_path, index = False, columns = COL_MAJ_IF)
                
    
    else: # Mode de fonctionnement par année
        # Check if the year is available
        try:
            df_IF = pd.read_excel(IF_path, sheet_name = str(year))
            # Ca fonctionne, alors on ajoute la colonne IF de l'année de publication
            print(f"Les IF sortis en {year} sont utilisés pour créer la colonne {IF_publi_alias}")

            dict1 = dict(zip(df_IF[ISSN_alias], df_IF[IF_alias])) # Mon dictionnaire construit à partir de mon fichier excel
            s = df_submit[ISSN_alias] # Je récup la colonne clef de ma DF en Series
            r = s.map(dict1) # Je map la Series avec mon dictionnaire
            df_submit[IF_publi_alias] = r # Je rajoute la colonne à ma DataFrame

            # Appliquer nan --> unknow to df
            df_submit[IF_publi_alias] = df_submit[IF_publi_alias].fillna(FILL_EMPTY_KEY_WORD)

            # Et on fait pareil avec les IF de l'année en cours
            df_IF = pd.read_excel(IF_path, sheet_name = None)
            print(f"Les IF sortis en {int(list(df_IF.keys())[-1])} sont utilisés pour créer la colonne {IF_cours_alias}")

            dict1 = dict(zip(df_IF[list(df_IF.keys())[-1]][ISSN_alias], df_IF[list(df_IF.keys())[-1]][IF_alias])) # Mon dictionnaire construit à partir de mon fichier excel
            s = df_submit[ISSN_alias] # Je récup la colonne clef de ma DF en Series
            r = s.map(dict1) # Je map la Series avec mon dictionnaire
            df_submit[IF_cours_alias] = r # Je rajoute la colonne à ma DataFrame

            # Appliquer nan --> unknow to df
            df_submit[IF_cours_alias] = df_submit[IF_cours_alias].fillna(FILL_EMPTY_KEY_WORD)

            df_submit.to_excel(out_path, index = False)

        except ValueError:
            # Check if the year is available, if not, terminate function
            try:
                # Et on fait pareil avec les IF de l'année en cours
                df_IF = pd.read_excel(IF_path, sheet_name = None)
                print(f"Les IF sortis en {int(list(df_IF.keys())[-1])} sont utilisés pour créer la colonne {IF_cours_alias}")

                dict1 = dict(zip(df_IF[list(df_IF.keys())[-1]][ISSN_alias], df_IF[list(df_IF.keys())[-1]][IF_alias])) # Mon dictionnaire construit à partir de mon fichier excel
                s = df_submit[ISSN_alias] # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1) # Je map la Series avec mon dictionnaire

                df_submit[IF_cours_alias] = r # Je rajoute la colonne à ma DataFrame
                df_submit[IF_publi_alias] = 'Not available' # Je rajoute la colonne à ma DataFrame

                # Appliquer nan --> unknow to df
                df_submit[IF_cours_alias] = df_submit[IF_cours_alias].fillna(FILL_EMPTY_KEY_WORD)
                df_submit[IF_publi_alias] = df_submit[IF_publi_alias].fillna(FILL_EMPTY_KEY_WORD)

                df_submit.to_excel(out_path, index = False)

            except ValueError:
                print('Mettre à jour le fichier Impact Factor')

def clean_reorder_rename_submit(in_path, out_path):
    
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
    df_in = pd.read_excel(in_path)
    
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
    df_reordered.to_excel(out_path)
    
def concat_listes_consolidees(bibliometer_path, years_list, R_path_alias, bdd_annuelle_alias):
    
    """
    """
    # Standard library imports
    from pathlib import Path
    import os
    from datetime import datetime
    
    # Local library imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import FILE_NAMES
    
    # 3rd library imports
    import pandas as pd
    
    df_concat = pd.DataFrame()
    
    available_liste_conso = ""
    
    for i in range(len(years_list)):
        try:
            path = Path(bibliometer_path) / Path(years_list[i]) / Path(R_path_alias) / Path(f"""{FILE_NAMES['liste conso']} {years_list[i]}.xlsx""")
            df_inter = pd.read_excel(path)
            df_concat = df_concat.append(df_inter)
        
            available_liste_conso = available_liste_conso + f""" {years_list[i]}"""
        
        except FileNotFoundError:
            pass

    date = str(datetime.now())[:16].replace(':', '')
    df_concat.to_excel(Path(bibliometer_path) / Path(bdd_annuelle_alias) / Path(f"""{date} Concaténation par {os.getlogin()}{available_liste_conso}.xlsx"""))
        
def maj_rh(bibliometer_path):

    # Imports
    import pandas as pd
    import os
    from pathlib import Path
    import shutil
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
    from BiblioMeter_GUI.Globals_GUI import COL_NAMES_BM
    from BiblioMeter_GUI.Globals_GUI import ARCHI_RH
    from BiblioMeter_GUI.Globals_GUI import ARCHI_SECOURS
    
    # Useful alias and path
    listing_alias = ARCHI_RH["root"]
    effectif_folder_name_alias = ARCHI_RH["effectifs"]
    effectif_file_name_alias = ARCHI_RH["effectifs file name"]
    secours_alias = ARCHI_SECOURS["root"]
    
    path_secours = Path(bibliometer_path) / Path(secours_alias)

    # Fonctions outil
    def _get_year(mmyyyy):
        return(mmyyyy[2:6])

    def _check_year_format(mmyyyy):

        '''
        The `_check_year_format` function, checks if the string argument mmyyyy is in the right format.

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
            years_to_check = [str(year) for year in range(today_year - taille_fourchette, today_year + 1 + taille_fourchette)]
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
            list_of_dates (list of strings): a list of string of dates in format mmyyyy, mm being the number of the month and yyyy being the number of the year.
        Returns:
            L (list of strings):
        '''

        L = []
        for i in list_of_dates:
            L.append(i[2:6])
        return list(set(L))

    # Alias
    path_effectif_folder = Path(bibliometer_path) / Path(ARCHI_RH["root"]) / Path(ARCHI_RH["effectifs"])
    path_to_add_folder = Path(bibliometer_path) / Path(ARCHI_RH["root"]) / Path(ARCHI_RH["maj"])
    matricule_alias = COL_NAMES_RH["ID"] # A importer depuis les globales

    # Accéder aux chemins des deux fichiers
    try:
        path_effectif_file = Path(bibliometer_path) / Path(ARCHI_RH["root"]) / Path(ARCHI_RH["effectifs"]) / os.listdir(path_effectif_folder)[0]
    except FileNotFoundError:
        print(f"""Il y a un problème dans le nom du répertoire {ARCHI_RH["effectifs"]}""")
    except IndexError:
        print(f"Le fichier des effectifs consolidés est introuvable, vérifiez qu'il est bien présent à l'emplacement suivant : {path_effectif_folder}")

    try:
        path_to_add_file = Path(bibliometer_path) / Path(ARCHI_RH["root"]) / Path(ARCHI_RH["maj"]) / os.listdir(path_to_add_folder)[0]
    except FileNotFoundError:
        print(f"""Il y a un problème dans le nom du répertoire {ARCHI_RH["maj"]}""")
    except IndexError:
        print(f"Le fichier à rajouter pour la mise à jour est introuvable, vérifiez qu'il est bien présent à l'emplacement suivant : {path_to_add_folder}")

    # Importer sous pandas
    df_effectif = pd.read_excel(path_effectif_file, sheet_name = None)
    df_to_add = pd.read_excel(path_to_add_file, sheet_name = None)

    # Récupérer le nom des pages de chaque fichier excel
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

    def _get_firstname_initiales(row):
        row = row.replace('-',' ')
        row_list = row.split(' ')
        initiale_list = [x[0] for x in row_list]
        initiales = ''.join(initiale_list)        
        return initiales

    # Et dédupliquer en ajoutant les colonnes Initials et Name + Initials
    years_to_dedup = _different_years(to_add_sheets)
    for page_to_dedup in years_to_dedup:
        df_effectif[page_to_dedup].drop_duplicates(subset = [matricule_alias], inplace = True)
    
        # Creating a column with first name initials as a list
        # ex PIERRE -->P, JEAN-PIERRE --> JP , JEAN-PIERRE MARIE --> JPM 
        col_in, col_out = COL_NAMES_RH['prénom'], COL_NAMES_BM['First_name']
        df_effectif[page_to_dedup][col_out] = df_effectif[page_to_dedup].apply(lambda row: _get_firstname_initiales(row[col_in]), axis = 1)

        # Creating the column ['Full_name'] by combining COL_NAMES_RH['Nom'] and COL_NAMES_BM['First_name']
        new_col = COL_NAMES_RH['Full_name']
        df_effectif[page_to_dedup][new_col] = df_effectif[page_to_dedup][COL_NAMES_RH['nom']] + ' ' + df_effectif[page_to_dedup][COL_NAMES_BM['First_name']]

    # Création de l'Excel Writer Object
    with pd.ExcelWriter(path_effectif_file) as writer:
        for page_effectif in effectif_sheets:
            df_effectif[page_effectif].to_excel(writer, sheet_name = page_effectif, index = False)
    
    # Copie de la mise à jour dans la zone de sauvegarde
    filePath = shutil.copy(path_effectif_file, path_secours)
            
def mise_en_page(df):

    # 3rd party import
    import pandas as pd
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.styles.colors import Color

    # Local library import
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
    
    # 3rd Library imports
    import pandas as pd
    
    if dictionnary == None:
        # Local library imports
        from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_FINALE
        dictionnary = COL_NAMES_FINALE
        
    df.rename(columns = dictionnary, inplace = True)
    
    return df

def ISSN_manquant(bibliometer_path, in_path):
    
    '''
    Genère un fichier des ISSN dont l'impact factor n'est pas dans la base de donnée
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # Local library imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    
    # 3rd party library imports
    import pandas as pd 
    
    # useful alias
    alias_IF_annee_publi = COL_NAMES_BONUS['IF année publi']
    
    ISSN_Liste = list()
    out_path = bibliometer_path / Path(STOCKAGE_ARBORESCENCE['general'][7])

    df = pd.read_excel(in_path)
    
    for i in range(len(df)):
        if df[alias_IF_annee_publi][i] == 'unknow' or df[alias_IF_annee_publi][i] == 'Not available':
            ISSN_Liste.append([df['ISSN'][i], df['Year'][i], df['Journal'][i]])
    
    df = pd.DataFrame(ISSN_Liste, columns = ['ISSN', 'Year', 'Journal'])
    df.drop_duplicates(inplace = True)
    
    df.to_excel(out_path / Path('ISSN_manquants.xlsx'))
    
    return print('Done')