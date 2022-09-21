__all__ = ['create_ParsingInstitution']

def create_ParsingInstitution(self, bibliometer_path):
    
    """
    Description : function working as a bridge between the BiblioMeter 
    App and the functionalities needed for the use of the app
    
    Uses the following globals : 
    - DIC_OUT_PARSING
    - FOLDER_NAMES
    
    Args : takes only self and bibliometer_path as arguments. 
    self is the intense in which PageThree will be created
    bibliometer_path is a type Path, and is the path to where the folders
    organised in a very specific way are stored
    
    Returns : nothing, it create the page in self
    """
    
    # Standard library imports
    import os
    from pathlib import Path
    from datetime import datetime

    # 3rd party imports
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    import pandas as pd
    from datetime import date

    # Local imports
    import BiblioAnalysis_Utils as bau
    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME

    from BiblioMeter_FUNCTS.BiblioMeter_MergeEffectif import recursive_year_search
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import filtrer_par_departement
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import consolidation_homonyme
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ajout_OTP

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    
    ### Choose which year you want to be working with #############################################################################################################
    years_list = five_last_available_years(bibliometer_path)
    variable_years = tk.StringVar(self)
    variable_years.set(years_list[0])
    
        # Création de l'option button des années
    OptionButton = tk.OptionMenu(self, variable_years, *years_list)
    OptionButton.place(anchor = 'center', relx = 0.32, rely = 0.20)
    
        # Création du label
    Label = tk.Label(self, text = '''Choisir l'année de travail :''')
    Label.place(anchor = 'center', relx = 0.20, rely = 0.20)
    ###############################################################################################################################################################
    
    
    ### Bouton qui va permettre d'utiliser seeting_secondary_inst_filter sur un corpus concatené ##################################################################
    Button = tk.Button(self, 
                       text = 'Choix d’affiliations supplémentaires\nautres que LITEN et INES', 
                       command = lambda: _setting_extend())
    Button.place(anchor = 'center', relx = 0.70, rely = 0.2)
    ###############################################################################################################################################################
    
    def _setting_extend():

        """
        Description :

        Uses the following globals :

        Args :

        Returns :
        """

        # Setting path_to_folder
        path_to_folder = bibliometer_path / Path(variable_years.get()) / Path(FOLDER_NAMES['corpus']) / Path(FOLDER_NAMES['dedup']) / Path(FOLDER_NAMES['parsing'])
        
        ### On récupère la présence ou non des fichiers #################################        
        results = existing_corpuses(bibliometer_path)

        list_corpus_year = results[0]
        list_wos_rawdata = results[1]
        list_wos_parsing = results[2]
        list_scopus_rawdata = results[3]
        list_scopus_parsing = results[4]
        list_concatenation = results[5]
        #################################################################################
        
        if list_wos_parsing[list_corpus_year.index(variable_years.get())] == False:
            messagebox.showwarning('Fichiers manquants', f"Warning : le fichier authorsinst.dat de wos de l'année {variable_years.get()} n'est pas disponible.\nVeuillez effectuer le parsing avant de parser les instituts")
            return
        
        full_list = bau.getting_secondary_inst_list(path_to_folder)

        _open_list_box_filter(self, full_list, path_to_folder)

    def _open_list_box_filter(self, full_list, path_to_folder):

        """
        Description :

        Uses the following globals :

        Args :

        Returns :
        """

        newWindow = tk.Toplevel(self)
        newWindow.grab_set()
        newWindow.title('Selection des institutions à parser')

        newWindow.geometry(f"600x600+{self.winfo_rootx()}+{self.winfo_rooty()}")

        label = tk.Label(newWindow, text="Selectionner les\ninstitutions", font = ("Helvetica", 20))
        label.place(anchor = 'n', relx = 0.5, rely = 0.025)

        yscrollbar = tk.Scrollbar(newWindow)
        yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        my_listbox = tk.Listbox(newWindow, 
                                selectmode = tk.MULTIPLE, 
                                yscrollcommand = yscrollbar.set)
        my_listbox.place(anchor = 'center', width = 400, height = 400, relx = 0.5, rely = 0.5)

        # TO DO : Ajouter une présélection

        x = full_list
        for idx, item in enumerate(x):
            my_listbox.insert(idx, item)
            my_listbox.itemconfig(idx,
                                  bg = "white" if idx % 2 == 0 else "white")
            
        # TO DO : Utiliser la global INST_FILTER_LIST quand feu vert de Amal et François
        n = x.index('France:LITEN')
        my_listbox.selection_set(first = n)
        n = x.index('France:INES')
        my_listbox.selection_set(first = n)
            
        # TO DO : Nommer la variable_years dans la commande
        
        button = tk.Button(newWindow, text ="Lancer le parsing des institutions", 
                           command = lambda: launch())
        button.place(anchor = 'n', relx = 0.5, rely = 0.9)
    
        def launch():
                        
            bau.extend_author_institutions(path_to_folder, [(x.split(':')[1].strip(),x.split(':')[0].strip()) for x in [my_listbox.get(i) for i in my_listbox.curselection()]])
            
            messagebox.showinfo('Information', f"Le parsing des institutions sélectionnées a été efectué.")
            
            newWindow.destroy()
    
    ### Bouton qui va permettre d'utiliser seeting_secondary_inst_filter sur un corpus concatené ##################################################################
    Button = tk.Button(self, 
                       text = 'Croiser les publications avec les effectifs Liten des N dernières années', 
                       command = lambda: _launch_recursive_year_search())
    
    Button.place(anchor = 'center', relx = 0.30, rely = 0.4)
    
    def _launch_recursive_year_search():
        
        recursive_year_search(Path(bibliometer_path) / 
                              Path(variable_years.get()) / 
                              Path(FOLDER_NAMES['corpus']) / 
                              Path(FOLDER_NAMES['dedup']) / 
                              Path(FOLDER_NAMES['parsing']),
                              Path(bibliometer_path) / 
                              Path(variable_years.get()) / 
                              Path(STOCKAGE_ARBORESCENCE['general'][0]), 
                              Path(bibliometer_path) / 
                              Path(STOCKAGE_ARBORESCENCE['effectif'][0]) / 
                              Path(STOCKAGE_ARBORESCENCE['effectif'][1]),
                              Path(bibliometer_path) / 
                              Path(STOCKAGE_ARBORESCENCE['effectif'][0]) / 
                              Path(STOCKAGE_ARBORESCENCE['effectif'][2]),
                              Path(bibliometer_path),
                              variable_years.get(), 
                              go_back_years.get())
        
        messagebox.showinfo('Information', f"Le croisement est terminé, vous pouvez maintenant passer aux étapes suivantes dans l'ordre :\n1 - Consolidation\n2- OTP\n3 - Création fichier final")
    
    ### Choix du nombre d'année du recursive_year_search
    Label = tk.Label(self, 
                     text = "Revenir en arrière sur combien d'année ?  N =")
    Label.place(anchor = 'center', relx = 0.65, rely = 0.4)
    
    go_back_years_list_rh = [i for i in range(1,date.today().year-2009)]
    go_back_years = tk.StringVar(self)
    go_back_years.set(go_back_years_list_rh[4])
    
        # Création de l'option button des années
    OptionButton = tk.OptionMenu(self, go_back_years, *go_back_years_list_rh)
    OptionButton.place(anchor = 'center', relx = 0.82, rely = 0.4)
    ###############################################################################################################################################################
    
    # Useful alias
    bdd_mensuelle_alias = STOCKAGE_ARBORESCENCE['general'][0]
    bdd_annuelle_alias = STOCKAGE_ARBORESCENCE['general'][1]
    OTP_path_alias = STOCKAGE_ARBORESCENCE['general'][3]
    Homonyme_path_alias = STOCKAGE_ARBORESCENCE['general'][4]
    R_path_alias = STOCKAGE_ARBORESCENCE['general'][5]
    submit_alias = SUBMIT_FILE_NAME
    
    # PREMIERE PARTIE : CONSOLIDATION    
    Button_mise_en_forme = tk.Button(self, 
                                     text = 'Consolidation homonymes', 
                                     command = lambda: _launch_consolidation_homonyme())
    
    Button_mise_en_forme.place(anchor = 'center', relx = 0.25, rely = 0.55)
    
    def _launch_consolidation_homonyme():
        
        consolidation_homonyme(Path(bibliometer_path) / 
                              Path(variable_years.get()) / 
                              Path(bdd_mensuelle_alias) / 
                              Path(submit_alias), 
                              Path(bibliometer_path) / 
                              Path(variable_years.get()) / 
                              Path(Homonyme_path_alias) / 
                              Path(f'Fichier Consolisation {variable_years.get()}.xlsx'))
        
        messagebox.showinfo('Information', f"Aller dans le dossier\n1 - Consolidation Homonymes / Fichier Consolidation\nde l'année de travail pour supprimer les mauvais homonymes")
    
    # DEUXIEME PARTIE : DEFINITION DE L'OTP
    
    Button_mise_en_forme = tk.Button(self, 
                                     text = 'Ajouter OTP à\nfichier consolidé', 
                                     command = lambda: _launch_ajout_OTP())
    
    Button_mise_en_forme.place(anchor = 'center', relx = 0.50, rely = 0.55)
    
    def _launch_ajout_OTP():
        
        ajout_OTP(Path(bibliometer_path) / 
                  Path(variable_years.get()) / 
                  Path(Homonyme_path_alias) / 
                  Path(f'Fichier Consolisation {variable_years.get()}.xlsx'), 
                  Path(bibliometer_path) / 
                  Path(variable_years.get()) / 
                  Path(OTP_path_alias))
        
        messagebox.showinfo('Information', f"Les fichiers OTP ont été créés dans 2 - OTP, il faut sélectionner le bon OTP et enregistrer le document sous le nom fichier_ajout_OTP_XXXX_ok")
    
    # TROISIEME PARTIE : CONSTRUCTION DU FICHIER FINAL  
    # Buton pour creer fichier excel d'une filtre par département
    Button = tk.Button(self, 
                       text = "Création fichier final\npour l'année sélectionnée", 
                       command = lambda: launch_filtrer_par_departement())
    
    Button.place(anchor = 'center', relx = 0.75, rely = 0.55)
    
    def launch_filtrer_par_departement():
        
        a = filtrer_par_departement(Path(bibliometer_path) / 
                                    Path(variable_years.get()) / 
                                    Path(OTP_path_alias), 
                                    Path(bibliometer_path) / 
                                    Path(variable_years.get()) / 
                                    Path(R_path_alias) / 
                                    Path(f'Liste finale publication {variable_years.get()}.xlsx'))
        
        if a:
            messagebox.showinfo('Information', f"Le document final a été créé, vous pouvez le retrouver dans\n3 - Résultats Finaux")
        else:
            messagebox.showinfo('Information', f"La création de la liste finale n'a pas pu être faite, il manque un fichier OTP. Vérifiez bien que les fichiers soient au bon emplacement sous le bon nom (fichier_ajout_OTP_XXXX_ok")
    
    # QUATRIEME PARTIE : CONCATENER LES 5 DERNIERS ANNEES
    Button = tk.Button(self, 
                       text = 'Concat sur 5 dernières\nannées dispo', 
                       command = lambda: _concat_filtre_depar())
    
    Button.place(anchor = 'center', relx = 0.5, rely = 0.75)
    
    def _concat_filtre_depar():
        
        '''
        '''
        
        df_concat = pd.DataFrame()
    
        for i in range(len(years_list)):
            path = Path(bibliometer_path) / Path(years_list[i]) / Path(R_path_alias) / Path(f'Liste finale publication {years_list[i]}.xlsx')
            df_inter = pd.read_excel(path)
            df_concat = df_concat.append(df_inter)
            
        date = str(datetime.now())[:16].replace(':', '')
        df_concat.to_excel(Path(bibliometer_path) / Path(bdd_annuelle_alias) / Path(f'{date}_concat_dep_{os.getlogin()}.xlsx'))
        
        messagebox.showinfo('Information', f"La concatenation des documents finaux des dernières années disponibles a été faite, vous pouvez la retrouver dans BDD Multi-annuelle")

    