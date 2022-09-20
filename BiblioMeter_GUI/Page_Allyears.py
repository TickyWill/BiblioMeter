__all__ = ['create_Allyears']

def create_Allyears(self, bibliometer_path):

    """
    Description : 
    
    Uses the following globals :
    
    Args :
    
    Returns :
    
    """

    # Standard library imports
    import os
    from pathlib import Path
    from datetime import datetime

    # 3rd party imports
    import tkinter as tk
    from tkinter import ttk
    import pandas as pd

    # Local imports
    import BiblioAnalysis_Utils as bau
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import la_liste_des_filtres_disponibles
    from BiblioMeter_GUI.Useful_Classes import ColumnFilter
    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Globals_GUI import SET_1
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    
    # Useful alias
    bdd_mensuelle_alias = STOCKAGE_ARBORESCENCE['general'][0]
    bdd_annuelle_alias = STOCKAGE_ARBORESCENCE['general'][1]
    filtre_path_alias = STOCKAGE_ARBORESCENCE['general'][2]
    OTP_path_alias = STOCKAGE_ARBORESCENCE['general'][3]
    Homonyme_path_alias = STOCKAGE_ARBORESCENCE['general'][4]
    R_path_alias = STOCKAGE_ARBORESCENCE['general'][5]
    R_bis_path_alias = STOCKAGE_ARBORESCENCE['general'][6]
    submit_alias = SUBMIT_FILE_NAME
    
    # Récupérer les corpus disponibles
    list_annee = five_last_available_years(bibliometer_path)

    Button_concat = tk.Button(self, 
                                     text = 'Concat 5 dernières années des submits', 
                                     font = ("Helvetica", 18), 
                                     command = lambda: _concat_submit())
    Button_concat.place(anchor = 'center', relx = 0.5, rely = 0.2)

    def _concat_submit():

        df_concat = pd.DataFrame()

        for i in range(len(list_annee)):
            path = Path(bibliometer_path) / Path(list_annee[i]) / Path(bdd_mensuelle_alias) / Path(f'submit.xlsx')
            df_inter = pd.read_excel(path)
            df_concat = df_concat.append(df_inter)

        date = str(datetime.now())[:16].replace(':', '')
        df_concat.to_excel(Path(bibliometer_path) / Path(bdd_annuelle_alias) / Path(f'{date}_concat_submit_{os.getlogin()}.xlsx'))
    
    
    ### Bouton qui va permettre de lancer la création du filtre ###################################################################################################
    Button_1 = tk.Button(self, 
                       text = '''Création d'un filtre''', 
                       command = lambda: _create_filter(OptionButton_filtre))
    Button_1.place(anchor = 'center', relx = 0.5, rely = 0.3)
    ###############################################################################################################################################################
    
    ### Choose which filter you want to be working with #############################################################################################################
    filter_list = la_liste_des_filtres_disponibles(bibliometer_path)
    variable_bis = tk.StringVar(self)
    variable_bis.set(filter_list[0])
    
        # Création de l'optionbutton des filtres
    OptionButton_filtre = tk.OptionMenu(self, variable_bis, *filter_list)
    OptionButton_filtre.place(anchor = 'center', relx = 0.25, rely = 0.4)
    
        # Création du label
    Label = tk.Label(self, text = '''Choisir le filtre :''')
    Label.place(anchor = 'center', relx = 0.10, rely = 0.4)
    
            # Nom du fichier à sauvegarder
    Entry_bis = tk.Entry(self)
    Entry_bis.place(anchor = 'center', relx = 0.45, rely = 0.4)
    
        # Buton pour creer fichier excel
    Button = tk.Button(self, 
                       text = 'Création du fichier excel', 
                       command = lambda: _save_to_excel(variable_bis.get(), Entry_bis.get()))
    Button.place(anchor = 'center', relx = 0.75, rely = 0.4)
    ###############################################################################################################################################################
        
    def _save_to_excel(filtre, nom):
        
        ### Path to the submit file ###################################################################################################################################
        submit_path = Path(bibliometer_path) / Path(bdd_annuelle_alias) / Path(os.listdir(Path(bibliometer_path) / Path(bdd_annuelle_alias))[-1])
        ###############################################################################################################################################################
        
        ### Charger la df #############################################################################################################################################
        df = pd.read_excel(submit_path)
        df['Nom Prénom']=df.apply(lambda x:'%s %s' % (x['Nom'], x['Prénom']),axis=1)
        #df_1 = df[SET_1]
        df_1 = df.copy()
        df_1.fillna('', inplace=True)
        ###############################################################################################################################################################
        
        filter_path = Path(bibliometer_path) / Path(filtre_path_alias) / Path(filtre)
        df_filtre = pd.read_excel(filter_path)
        print(df_filtre)
        list_filtre = df_filtre[0].tolist()
        
        df_to_save = df_1[df_filtre[0].tolist()]
        
        df_to_save.to_excel(Path(bibliometer_path) / Path(R_bis_path_alias) / Path(nom + '.xlsx'))
        
    def _create_filter(OptionButton_filtre):
        
        newWindow = tk.Toplevel(self)
        newWindow.title('Création du filtre')
        newWindow.geometry(f"600x600+{self.winfo_rootx()}+{self.winfo_rooty()}")
        newWindow.resizable(False, False)
        newWindow.grab_set()

        # Create frames
        main_frame = tk.LabelFrame(newWindow, highlightbackground = 'red', highlightthickness = 1)
        backup_frame = tk.LabelFrame(newWindow, highlightbackground = 'red', highlightthickness = 1)

        # Create a canvas
        my_canvas = tk.Canvas(main_frame)
        my_canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

        # Add a scrollbar to the canvas
        my_scrollbar = ttk.Scrollbar(main_frame, orient = tk.VERTICAL, command = my_canvas.yview)
        my_scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        # Configure the canvas
        my_canvas.configure(yscrollcommand = my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e : my_canvas.configure(scrollregion = my_canvas.bbox("all")))

        # Create another frame inside the canvas
        second_frame = tk.Frame(my_canvas)
        second_frame.pack()

        main_frame.pack(fill = tk.BOTH, expand = 1, padx = 10, pady = 10)
        backup_frame.pack(fill = tk.BOTH, expand = 1, padx = 10, pady = 10)

        # Add that new frame to a window in the canvas
        my_canvas.create_window((0,0), window = second_frame, anchor = 'nw')

        ### Path to the submit file ###################################################################################################################################       
        submit_path = Path(bibliometer_path) / Path(bdd_annuelle_alias) / Path(os.listdir(Path(bibliometer_path) / Path(bdd_annuelle_alias))[-1])
        ###############################################################################################################################################################

        ### Charger la df #############################################################################################################################################
        df = pd.read_excel(submit_path)
        df['Nom Prénom']=df.apply(lambda x:'%s %s' % (x['Nom'], x['Prénom']),axis=1)
        #df_1 = df[SET_1]
        df_1 = df.copy()
        df_1.fillna('', inplace=True)
        ###############################################################################################################################################################
        
        list_tmp = list()
        for i in range(len(df_1.columns)):
            tmp = ColumnFilter(second_frame, df_1.columns[i], df_1)
            tmp.place(y = i)
            list_tmp.append(tmp)
            
        ### Bouton qui va permettre de sauvegarder le filtre #########################################################################################################
        Entry = tk.Entry(backup_frame)
        Entry.place(anchor = 'center', relx = 0.45, rely = 0.15)
        ###############################################################################################################################################################
        
        ### Bouton qui va permettre de sauvegarder le filtre #########################################################################################################
        Button = tk.Button(backup_frame, 
                           text = 'Sauvegarde du filtre', 
                           command = lambda: _save_filter(OptionButton_filtre))
        Button.place(anchor = 'center', relx = 0.45, rely = 0.35)
        ###############################################################################################################################################################
        
        def _save_filter(OptionButton_filtre):
            filter_name = Entry.get() + ".xlsx"
            
            list_to_keep = []
            
            for i in range(len(list_tmp)):
                if list_tmp[i].get_check_1() == 1:
                    list_to_keep.append(str(list_tmp[i].get_label()))
                    
            columns_to_keep = set(list_to_keep)
            
            df_submit = df_1.copy()

            columns_to_remove = list(set(df_submit.columns.tolist()) - columns_to_keep)

            # Remettre les Pub_ID dans l'ordre
            df_submit.sort_values(by=['Pub_id', 'Dpt/DOB (lib court)'], ascending=False, inplace = True)
            df_submit.sort_values(by=['Pub_id', 'Idx_author'], ascending=True, inplace = True)

            for column in columns_to_remove:
                df_submit.drop(column, 1, inplace = True)
            
            new_df = pd.DataFrame(df_submit.columns)
            
            save_path = Path(bibliometer_path) / Path(filtre_path_alias) / Path(filter_name)
            
            new_df.to_excel(save_path)
            
            #OptionButton_filtre.destroy()
            
            #filter_list = la_liste_des_filtres_disponibles(bibliometer_path)
            #variable_bis = tk.StringVar(self)
            #variable_bis.set(filter_list[0])

                # Création de l'optionbutton des années
            #OptionButton_filtre = tk.OptionMenu(self, variable_bis, *filter_list)
            #OptionButton_filtre.place(anchor = 'center', relx = 0.25, rely = 0.4)
            
            newWindow.destroy()