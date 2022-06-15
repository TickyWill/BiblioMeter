__all__ = ['you_got_OTPed',
           'liste_de_validation',
           'get_unique_numbers',
           'filtrer_par_departement', 
           'consolidation_anonymat', 
           'ajout_OTP', 
           'add_authors_name_list', 
           'concat_name_firstname']
    
def you_got_OTPed(df,i):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        Adds OTP to df'''
    
    # Standard library imports
    from pathlib import Path
    
    # Local library imports   
    import BiblioMeter_FUNCTS as bmf
    
    # 3rd party library imports
    import pandas as pd
    from openpyxl.utils.cell import get_column_letter
    
    # Global variable imports
    from .BiblioMeterGlobalsVariables import OTP_STRING
    
    columns_to_keep = ['Pub_id', 
                       'Idx_author', 
                       'Authors',  
                       'DOI', 
                       'ISSN', 
                       'LITEN_France',
                       'Secondary_institutions', 
                       'Document_type',
                       'Matricule', 
                       'Nom', 
                       'Prénom', 
                       'Dpt/DOB (lib court)', 
                       'Service (lib court)', 
                       'Laboratoire (lib court)', 
                       'Laboratoire (lib long)',
                       'List_of_OTP',
                       'HOMONYM']
    
    if 'List_of_OTP' in df.columns:
        #if df['Pub_id'].iloc[i-1] == df['Pub_id'].iloc[i] and df['Dpt/DOB (lib court)'].iloc[i-1] == df['Dpt/DOB (lib court)'].iloc[i]: VERSION AMAL
        if df['Pub_id'].iloc[i-1] == df['Pub_id'].iloc[i]: # VERSION DE JP
            
            lien_otp = '='+get_column_letter(columns_to_keep.index('List_of_OTP')+1)+str(i+1) # ---------------------------> rendre robuste 

            #truc = '"'+','.join(lien_otp)+'"'
            
            df['List_of_OTP'].iloc[i] = lien_otp
            
        else:
            df['List_of_OTP'].iloc[i] = OTP_STRING[df.iloc[i]['Dpt/DOB (lib court)']]
    else:
        df['List_of_OTP'] = pd.Series()
        df['List_of_OTP'].iloc[i] = OTP_STRING[df.iloc[i]['Dpt/DOB (lib court)']]
    
    return df

def liste_de_validation(df, i):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        Adds OTP to df'''
    
    # Local imports
    import BiblioMeter_FUNCTS as bmf
    
    # Global variable imports
    from .BiblioMeterGlobalsVariables import OTP_LIST
    
    validation_list = OTP_LIST[df.iloc[i]['Dpt/DOB (lib court)']]
    
    truc = '"'+','.join(validation_list)+'"'
    
    return truc

def get_unique_numbers(numbers):

    list_of_unique_numbers = []

    unique_numbers = set(numbers)

    for number in unique_numbers:
        list_of_unique_numbers.append(number)

    return list_of_unique_numbers

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

    # Local imports
    from BiblioMeter_GUI.Globals_GUI import SET_OTP

    # 3rd party imports
    import pandas as pd

    ### Charger les df et ajouter les 4 colonnes ###################################################################################################################
    df_DTNM = pd.read_excel(in_path / Path('fichier_ajout_OTP_DTNM.xlsx'))
    df_DTS = pd.read_excel(in_path / Path('fichier_ajout_OTP_DTS.xlsx'))
    df_DEHT = pd.read_excel(in_path / Path('fichier_ajout_OTP_DEHT.xlsx'))
    df_DTCH = pd.read_excel(in_path / Path('fichier_ajout_OTP_DTCH.xlsx'))
    
    df_OTP = df_DTNM.copy()
    df_OTP = df_OTP.append(df_DTS)
    df_OTP = df_OTP.append(df_DEHT)
    df_OTP = df_OTP.append(df_DTCH)
    
    df_OTP.fillna('', inplace=True)
    df_OTP.set_index('Pub_id', inplace = True)
   
    df_OTP.sort_values(['Pub_id','Idx_author'], inplace = True)
    df_OTP.drop(['Idx_author'], axis=1, inplace = True)
    df_OTP.reset_index(inplace = True)
    df_OTP.drop_duplicates(subset = ['Pub_id'], inplace = True)
    df_OTP.set_index('Pub_id', inplace = True)
    df_OTP.to_excel(out_path)
    

def consolidation_anonymat(in_path, out_path):

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

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME
    from BiblioMeter_GUI.Globals_GUI import ORPHAN_FILE_NAME

    ###########################
    # Getting the submit file #
    ###########################

    df_submit = pd.read_excel(in_path)

    # Remettre les Pub_ID dans l'ordre
    df_submit.sort_values(by=['Pub_id', 'Dpt/DOB (lib court)'], ascending=False, inplace = True)
    df_submit.sort_values(by=['Pub_id', 'Idx_author'], ascending=True, inplace = True)

    ############################################
    # Getting rid of the columns we don't want #
    ############################################

    # TO DO : METTRE EN VARIABLE GLOBAL
    columns_to_keep = ['Pub_id', 'Idx_author', 'Title', 'Journal',
                       'Authors',  
                       'DOI', 
                       'ISSN', 
                       'Document_type',
                       'Matricule', 
                       'Nom', 
                       'Prénom', 
                       'Dpt/DOB (lib court)', 
                       'Service (lib court)', 
                       'Laboratoire (lib court)',
                       'HOMONYM']

    df_submit = df_submit[columns_to_keep].copy()

    # La colonne 0/1 pour afficher ou pas
    #list_de_1 = [1] * len(df_submit)
    #df_submit['Affichage'] = list_de_1

    columns_to_keep = df_submit.columns.to_list()

    # Liste unique des Pub_id conservé
    list_of_Pub_id = df_submit['Pub_id'].to_list()
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
        if r[columns_to_keep.index('HOMONYM')] == 'HOMONYM' and indice > 0:
            cell = last_row[columns_to_keep.index('Nom')]
            cell.fill = yellow_ft
            cell = last_row[columns_to_keep.index('Prénom')]
            cell.fill = yellow_ft

            column_letter = get_column_letter(columns_to_keep.index('Nom')+1)
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
    

def ajout_OTP(in_path, out_path):

    '''
    '''
    
    # Standard library imports
    from pathlib import Path

    # Local library imports
    import BiblioMeter_FUNCTS as bmf

    # 3rd party import
    import pandas as pd
    from openpyxl import Workbook, load_workbook
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.utils.cell import get_column_letter

    df_submit = pd.read_excel(in_path)
    
    df_submit.fillna('', inplace=True)
    df_submit.set_index('Pub_id', inplace = True)
        
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

        for j in df_inter_pub_id['Idx_author']:

            filtre_inter_author = df_inter_pub_id['Idx_author'] == j
            df_inter_inter = df_inter_pub_id[filtre_inter_author]

            if df_inter_inter['Dpt/DOB (lib court)'].to_list()[0] == 'DTNM':
                df_submit.loc[i,'DTNM'] = 1

            elif df_inter_inter['Dpt/DOB (lib court)'].to_list()[0] == 'DTS':
                df_submit.loc[i,'DTS'] = 1

            elif df_inter_inter['Dpt/DOB (lib court)'].to_list()[0] == 'DEHT':
                df_submit.loc[i,'DEHT'] = 1

            else:
                df_submit.loc[i,'DTCH'] = 1
                
    df_submit.sort_values(['Pub_id','Idx_author'], inplace = True)
    df_submit.reset_index(inplace = True)
    df_submit.drop_duplicates(subset = ['Pub_id'], inplace = True)
    
    _=[bmf.you_got_OTPed(df_submit,i) for i in range(len(df_submit))]

    columns_to_keep = df_submit.columns.to_list()

    filtre_DTNM = df_submit['Dpt/DOB (lib court)'] == 'DTNM'
    filtre_DTS = df_submit['Dpt/DOB (lib court)'] == 'DTS'
    filtre_DEHT = df_submit['Dpt/DOB (lib court)'] == 'DEHT'
    filtre_DTCH = (df_submit['Dpt/DOB (lib court)'] == 'DTCH') | (df_submit['Dpt/DOB (lib court)'] == 'DTBH')

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
            if df_DTNM['Pub_id'].iloc[r-1] == df_DTNM['Pub_id'].iloc[r]: 
                'Yo'
            else:        
                validation_list = bmf.liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index('List_of_OTP')+1)+str(r+2)])

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTNM.xlsx'))


    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    df_DTS = df_submit[filtre_DTS]

    for indice, r in enumerate(dataframe_to_rows(df_DTS, index=False, header=True)):
        ws.append(r)
        
    df_DTS.reset_index(inplace = True)

    for r in range(0,ws.max_row-2):
            if df_DTS['Pub_id'].iloc[r-1] == df_DTS['Pub_id'].iloc[r]: 
                'Yo'
            else:        
                validation_list = bmf.liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index('List_of_OTP')+1)+str(r+2)])

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTS.xlsx'))


    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    df_DEHT = df_submit[filtre_DEHT]

    for indice, r in enumerate(dataframe_to_rows(df_DEHT, index=False, header=True)):
        ws.append(r)
        
    df_DEHT.reset_index(inplace = True)

    for r in range(0,ws.max_row-2):
            if df_DEHT['Pub_id'].iloc[r-1] == df_DEHT['Pub_id'].iloc[r]: 
                'Yo'
            else:        
                validation_list = bmf.liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index('List_of_OTP')+1)+str(r+2)])

    wb.save(out_path / Path(f'fichier_ajout_OTP_DEHT.xlsx'))


    wb = Workbook()
    ws = wb.active
    ws.title = 'Publi x Effectifs'

    df_DTCH = df_submit[filtre_DTCH]

    for indice, r in enumerate(dataframe_to_rows(df_DTCH, index=False, header=True)):
        ws.append(r)
        
    df_DTCH.reset_index(inplace = True)

    for r in range(0,ws.max_row-2):
            if df_DTCH['Pub_id'].iloc[r-1] == df_DTCH['Pub_id'].iloc[r]: 
                'Yo'
            else:        
                validation_list = bmf.liste_de_validation(df_submit,r)

                data_val = DataValidation(type="list",formula1=validation_list, showErrorMessage=False)
                ws.add_data_validation(data_val)

                data_val.add(ws[get_column_letter(columns_to_keep.index('List_of_OTP')+1)+str(r+2)])

    wb.save(out_path / Path(f'fichier_ajout_OTP_DTCH.xlsx'))

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
    
    # 3rd party imports
    import pandas as pd
    
    # Useful alias
    pub_id_alias = COL_NAMES['pub_id']
    
    # Read of the excel file
    df_in = pd.read_excel(in_path)
    
    # Add of the column 'Nom Prénom' that will be used to create the authors fullname list
    df_in = concat_name_firstname(df_in)
    
    # Sort on Pub_id and then add the authors fullname list
    if pub_id_alias not in df_in:
        raise KeyError(f"The column {pub_id_alias} is not in DataFrame. Cannot carry on. Please make sure the DataFrame has a column named 'Pub_id'.")
    
    df_out = pd.DataFrame()
    unique_pub_id_list = df_in['Pub_id'].unique().tolist()
    
    for i in unique_pub_id_list:
        filtre_inter_pub_id = (df_in[pub_id_alias] == i)
        df_inter = df_in[filtre_inter_pub_id]
        authors_fullname_list = '; '.join(df_inter['Nom Prénom'].tolist())
        df_inter['Authors Fullname List'] = authors_fullname_list
        df_out = df_out.append(df_inter)
        
    # Save in an excel file where leads out_path
    df_out.to_excel(out_path)
    
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
    
    # 3rd party imports
    import pandas as pd
    
    # Check is df is a DataFrame and if it contains the colomns needed which are 'Nom' and 'Prénom' and 'Pub_id'
    if isinstance(df, pd.DataFrame):
        to_check = ['Nom', 'Prénom']
        for i in to_check:
            if 'Nom' not in df:
                raise KeyError(f"The column {i} is not in DataFrame")
    else:
        raise TypeError(f"The variable {df} is not of proper type, it has to be a DataFrame")
        
    # Add of the colomn 'Nom Prénom' meaning full name.
    df['Nom Prénom'] = df['Nom'] + ', ' + df['Prénom']
    
    return df
