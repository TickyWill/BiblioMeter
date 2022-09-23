__all__ = ['get_unique_numbers',
           
           'consolidation_homonyme',
           
           'concat_name_firstname',
           'add_authors_name_list',
           'ajout_OTP',
           
           'filtrer_par_departement', 
           
           'add_biblio_list',
           'ajout_IF',
           'clean_reorder_rename_submit', 
          
           'maj_listing_RH']

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
       
    ###########################
    # Getting the submit file #
    ###########################

    df_submit = pd.read_excel(in_path)
    
    # Remettre les Pub_ID dans l'ordre
    df_submit.sort_values(by=[pub_id_alias, dpt_alias], ascending=False, inplace = True)
    df_submit.sort_values(by=[pub_id_alias, idx_author], ascending=True, inplace = True)

    ############################################
    # Getting rid of the columns we don't want #
    ############################################

    # Useful alias
    col_conso_alias = COL_CONSOLIDATION
    
    df_submit = df_submit[col_conso_alias].copy()

    col_conso_alias = df_submit.columns.to_list()

    # Liste unique des Pub_id conservé
    list_of_Pub_id = df_submit[pub_id_alias].to_list()
    list_of_Pub_id = bmf.get_unique_numbers(list_of_Pub_id)

    #########################
    # Ouverture du workbook #
    #########################

    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    yellow_ft = PatternFill(fgColor = '00FFFF00', fill_type = "solid")
    red_ft = PatternFill(fgColor = '00FF0000', fill_type = "solid")
    blue_ft = PatternFill(fgColor = '0000FFFF', fill_type = "solid")
    bd = Side(style='medium', color="000000")
    active_color = 'red'

    for indice, r in enumerate(dataframe_to_rows(df_submit, index=False, header=True)):
        ws.append(r)
        last_row = ws[ws.max_row]
        if r[col_conso_alias.index(homonym_alias)] == homonym_alias and indice > 0:
            cell = last_row[col_conso_alias.index('Nom')]
            cell.fill = yellow_ft
            cell = last_row[col_conso_alias.index('Prénom')]
            cell.fill = yellow_ft

            column_letter = get_column_letter(col_conso_alias.index('Nom')+1)
            excel_cell_id = column_letter + str(indice+1)

        if ws.max_row > 1 and r[0] in list_of_Pub_id:
            if list_of_Pub_id.index(r[0])%2 == 0:
                cell = last_row[0]
                cell.fill = red_ft
                if active_color != 'red':
                    for cell_bis in last_row:
                        cell_bis.border = Border(top=bd)
                        active_color = 'red'
            else:
                cell = last_row[0]
                cell.fill = blue_ft
                if active_color != 'blue':
                    for cell_bis in last_row:
                        cell_bis.border = Border(top=bd)
                        active_color = 'blue'


    for cell in ws['A'] + ws[1]:
        cell.font = Font(bold=True)
        cell.border = Border(left=bd, top=bd, right=bd, bottom=bd)
        cell.alignment = Alignment(horizontal="center", vertical="center")

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
        #if df[pub_id_alias].iloc[i-1] == df['Pub_id'].iloc[i] and df[dpt_alias].iloc[i-1] == df[dpt_alias].iloc[i]: # VERSION AMAL
        if df[pub_id_alias].iloc[i-1] == df[pub_id_alias].iloc[i]: # VERSION DE JP
            
            lien_otp = '='+get_column_letter(columns_to_keep.index(OTP_alias)+1)+str(i+1) # ---------------------------> rendre robuste 

            #truc = '"'+','.join(lien_otp)+'"'
            
            df[OTP_alias].iloc[i] = lien_otp
            
        else:
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
    pub_id_alias = COL_NAMES['pub_id']
    dpt_alias = COL_NAMES_RH['dpt']
    OTP_alias = COL_NAMES_BONUS['list OTP']
    idx_author = COL_NAMES['authors'][1]
    
    add_authors_name_list(in_path, in_path)
    
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
        
    _=[_you_got_OTPed(df_submit,i) for i in range(len(df_submit))]
    
    #df_submit[OTP_alias] = ""
    
    # columns_to_keep = df_submit.columns.to_list()
    columns_to_keep = COL_OTP
    
    df_submit = df_submit[COL_OTP]
    
    filtre_DTNM = df_submit[dpt_alias] == 'DTNM'
    filtre_DTS = df_submit[dpt_alias] == 'DTS'
    filtre_DEHT = df_submit[dpt_alias] == 'DEHT'
    filtre_DTCH = (df_submit[dpt_alias] == 'DTCH') | (df_submit[dpt_alias] == 'DTBH')

    #########################
    # Ouverture du workbook #
    #########################

    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    df_DTNM = df_submit[filtre_DTNM]

    for indice, r in enumerate(dataframe_to_rows(df_DTNM, index=False, header=True)):
        ws.append(r)
    
    df_DTNM.reset_index(inplace = True)
    
    for r in range(0,ws.max_row-2):
            if df_DTNM[pub_id_alias].iloc[r-1] == df_DTNM[pub_id_alias].iloc[r]: 
                'Hello World'
            else:        
                validation_list = _liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index(OTP_alias)+1)+str(r+2)])

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTNM.xlsx'))
    


    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    df_DTS = df_submit[filtre_DTS]

    for indice, r in enumerate(dataframe_to_rows(df_DTS, index=False, header=True)):
        ws.append(r)
        
    df_DTS.reset_index(inplace = True)

    for r in range(0,ws.max_row-2):
            if df_DTS[pub_id_alias].iloc[r-1] == df_DTS[pub_id_alias].iloc[r]: 
                'Yo'
            else:        
                validation_list = _liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index(OTP_alias)+1)+str(r+2)])

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTS.xlsx'))


    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    df_DEHT = df_submit[filtre_DEHT]

    for indice, r in enumerate(dataframe_to_rows(df_DEHT, index=False, header=True)):
        ws.append(r)
        
    df_DEHT.reset_index(inplace = True)

    for r in range(0,ws.max_row-2):
            if df_DEHT[pub_id_alias].iloc[r-1] == df_DEHT[pub_id_alias].iloc[r]: 
                'Yo'
            else:        
                validation_list = _liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index(OTP_alias)+1)+str(r+2)])

    wb.save(out_path / Path(f'fichier_ajout_OTP_DEHT.xlsx'))


    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    df_DTCH = df_submit[filtre_DTCH]

    for indice, r in enumerate(dataframe_to_rows(df_DTCH, index=False, header=True)):
        ws.append(r)
        
    df_DTCH.reset_index(inplace = True)

    for r in range(0,ws.max_row-2):
            if df_DTCH[pub_id_alias].iloc[r-1] == df_DTCH[pub_id_alias].iloc[r]: 
                'Yo'
            else:        
                validation_list = _liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index(OTP_alias)+1)+str(r+2)])

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
    df_out.to_excel(out_path)
    
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
                
                print(f"La colonne {IF_publi_alias} a été rajoutée avec succès pour l'année {annee}")

                dict1 = dict(zip(df_IF[list(df_IF.keys())[-1]][ISSN_alias], df_IF[list(df_IF.keys())[-1]][IF_alias])) # Mon dictionnaire construit à partir de mon fichier excel
                s = df_inter[ISSN_alias] # Je récup la colonne clef de ma DF en Series
                r = s.map(dict1) # Je map la Series avec mon dictionnaire
                df_inter[IF_cours_alias] = r # Je rajoute la colonne à ma DataFrame
                
                # Appliquer nan --> unknow to df
                df_inter[IF_cours_alias] = df_inter[IF_cours_alias].fillna(FILL_EMPTY_KEY_WORD)
                
                print(f"La colonne {IF_cours_alias} a été rajoutée avec succès pour l'année {annee}, avec les IF de l'année {list(df_IF.keys())[-1]}")

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
                
                print(f"Les colonnes {IF_publi_alias} et {IF_cours_alias} ont été rajoutées avec succès pour l'année {annee}")

                df_submit_bis = df_submit_bis.append(df_inter)
            
        df_submit_bis.to_excel(out_path, index = False, columns = COL_OTP)
                
    
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
                        SUBMIT_COL_NAMES['ISSN'], ]]
    
    # Save in an excel file where leads out_path
    df_reordered.to_excel(out_path)
    
def maj_listing_RH():
    
    '''
    '''
    
    # Standard library imports
    import numpy as np
    from pathlib import Path
    
    # Local library imports
    from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # 3rd party library imports
    import pandas as pd 
    from openpyxl import load_workbook
    
    # useful alias
    bibliometer = Path(ROOT_PATH)

    def date_compare(list_of_dates, comparator):
        '''
        Args:
            list_of_dates (list of strings): a list of string of dates in format mmyyyy, mm being the number of the month and yyyy being the number of the year.
            comparator (string): a date in string format mmyyyy, mm being the number of the month and yyyy being the number of the year.

        Returns:
            L (list of strings): a list of the dates older than the comparator date.

        '''
        L = []
        for i in list_of_dates:
            if i[2:6] > comparator[2:6]:
                # Alors ok pas besoin de vérifier
                L.append(i)
            elif i[2:6] == comparator[2:6]:
                if i[0:2] > comparator[0:2]:
                    # Okay si le mois est supérieur
                    L.append(i)
        return L

    def concat_df_with_multidf_and_drop_dup(multi_df, df = pd.DataFrame()):
        '''
        Args:
            multi_df (DataFrame):
            df (DataFrame):
        Returns:
            df (DataFrame):
        '''
        for i in range(len(multi_df)):
            clef = list(df_month.keys())[i]
            df = df.append(multi_df[clef])
        df.drop_duplicates(subset=['Matricule'], keep='first', inplace=True, ignore_index=False)
        return df

    def different_years(list_of_dates):
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

    def dates_of_the_given_year(given_year, list_of_dates):
        '''
        Args:
            given_year (string):
            list_of_dates (list of strings): a list of string of dates in format mmyyyy, mm being the number of the month and yyyy being the number of the year.
        Returns:
            L (list of strings):
        '''
        L = []
        for i in list_of_dates:
            if i[2:6] == given_year:
                L.append(i)
        return L

    # Mise à jour fichier RH
    path_year = bibliometer / Path("Listing RH") / Path("All_effectifs.xlsx")
    path_month = bibliometer / Path("Listing RH") / Path("Effectifs_2010_2022.xlsx")
    path_maj = bibliometer / Path("Listing RH") /Path("MAJ.txt")

    # Récupérer la date de la dernière MAJ
    f = open(path_maj,'r')
    last_maj = f.readline()
    f.close()

    # Récupérer les pages dont les dates sont antérieures à last_maj
    xls = pd.ExcelFile(path_month, engine = 'openpyxl')
    sheets = xls.sheet_names
    excel_sheets = date_compare(sheets, last_maj)
    print(f"Toutes les pages à maj sont {excel_sheets}")

    # Récupérer les différentes années et boucler dessus
    diff_years = different_years(excel_sheets)
    print(f"Les années différentes sur ces pages sont {diff_years}")

    # Ouverture du workbook et writer
    book = load_workbook(path_year)
    writer = pd.ExcelWriter(path_year, engine = 'openpyxl', mode = 'a', if_sheet_exists = 'replace') 
    # writer.book = book

    for year in diff_years:
        # Les dates des pages à rajouter pour l'année en question
        month_pages = dates_of_the_given_year(year, excel_sheets)
        print(f"Pour l'année {year}, les mois sont {month_pages}")

        # La multi df à récupérer de l'année en question pour mettre à jour le fichier effectif de l'année
        df_month = pd.read_excel(path_month, sheet_name = month_pages)

        # Vérifier l'excistence de la page de l'année de path_year, et si elle existe la récupérer, sinon la créer.
        try:
            print('Test du try')
            df_year = pd.read_excel(path_year, sheet_name = year, engine = 'openpyxl')

            print(f"La page existe ! Tout est bon, on peut continuer")
            df_maj = concat_df_with_multidf_and_drop_dup(df_month, df_year)
            #book.remove(year)
            df_maj.to_excel(writer, sheet_name = year)

            print('Fin du try')

        except:
            print(f"La page n'existe pas ! Il faut donc la créer lors de l'ajout de la DataFrame")
            df_maj = concat_df_with_multidf_and_drop_dup(df_month)
            df_maj.to_excel(writer, sheet_name = year)

            print('Fin du except')

    writer.save()
    writer.close()

    print('Terminé, vous pouvez ouvrir le fichier excel')