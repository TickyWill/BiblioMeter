__all__ = ['create_ParsingInstitution']

def create_ParsingInstitution(self, bibliometer_path, parent):
    
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

    # 3rd party imports    
    import pandas as pd
    import tkinter as tk
    from datetime import date
    from tkinter import font as tkFont
    from tkinter import filedialog
    from tkinter import messagebox
    
    # Local imports    
    from BiblioMeter_FUNCTS.BiblioMeter_MergeEffectif import recursive_year_search
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import add_OTP
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import concatenate_pub_lists
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import solving_homonyms
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import consolidate_pub_list
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import update_employees
    
    from BiblioMeter_GUI.Coordinates import root_properties
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PI
    from BiblioMeter_GUI.Coordinates import ETAPE_LABEL_TEXT_LIST    
    from BiblioMeter_GUI.Coordinates import TEXT_CROISEMENT
    from BiblioMeter_GUI.Coordinates import TEXT_CROISEMENT_L
    from BiblioMeter_GUI.Coordinates import TEXT_HOMONYMES
    from BiblioMeter_GUI.Coordinates import TEXT_MAJ_EFFECTIFS
    from BiblioMeter_GUI.Coordinates import TEXT_PAUSE
    from BiblioMeter_GUI.Coordinates import TEXT_PUB_CONSO
    from BiblioMeter_GUI.Coordinates import TEXT_OTP
    from BiblioMeter_GUI.Coordinates import FONT_NAME

    from BiblioMeter_GUI.Globals_GUI import ARCHI_BDD_MULTI_ANNUELLE
    from BiblioMeter_GUI.Globals_GUI import ARCHI_RH
    from BiblioMeter_GUI.Globals_GUI import ARCHI_SECOURS
    from BiblioMeter_GUI.Globals_GUI import ARCHI_YEAR
    from BiblioMeter_GUI.Globals_GUI import DPT_LABEL_DICT
    from BiblioMeter_GUI.Globals_GUI import PPI
    
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import encadre_RL
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import place_bellow
    
    # Defining internal functions
    def _etape_frame(self, num):
        '''The local function `_etape_frame` sets the 'etape' and place in the page
        using the global 'ETAPE_LABEL_TEXT_LIST' and the local variables 'etape_label_format', 
        'etape_label_font', 'etape_underline', 'etape_label_pos_x' and 'etape_label_pos_y_list'.
        
        Args:
            num (int): The order of the 'etape' in 'ETAPE_LABEL_TEXT_LIST'.
        '''
        etape = tk.Label(self, 
                         text      = ETAPE_LABEL_TEXT_LIST[num], 
                         justify   = etape_label_format, 
                         font      = etape_label_font, 
                         underline = etape_underline)
        etape.place(x = etape_label_pos_x, 
                    y = etape_label_pos_y_list[num])
        return etape
       
    def _launch_exit():
        ask_title = "Arrêt de BiblioMeter"
        ask_text =  "Après la fermeture des fenêtres, "
        ask_text += "les traitements effectués sont sauvegardés."
        ask_text += "\nLe traitement peut être repris ultérieurement."
        ask_text += "\nConfirmez la mise en pause ?"
        exit_answer = messagebox.askokcancel(ask_title, ask_text)
        if exit_answer:
            parent.destroy()
    
    # Getting useful window sizes and scale factors depending on displays properties
    sizes_tuple   = root_properties(self)
    win_width_px  = sizes_tuple[0]    # unused here
    win_height_px = sizes_tuple[1]    # unused here
    width_sf_px   = sizes_tuple[2] 
    height_sf_px  = sizes_tuple[3]    # unused here
    width_sf_mm   = sizes_tuple[4]
    height_sf_mm  = sizes_tuple[5]
    width_sf_min  = min(width_sf_mm, width_sf_px)
    
    # Setting useful local variables for positions modification (globals to create ??)
    # numbers are reference values in mm for reference screen
    eff_etape_font_size      = font_size(14, width_sf_min)
    eff_launch_font_size     = font_size(13, width_sf_min)
    eff_answer_font_size     = font_size(13, width_sf_min)
    eff_select_font_size     = font_size(12, width_sf_min)
    eff_buttons_font_size    = font_size(11, width_sf_min)                                         
    
    etape_label_pos_x        = mm_to_px( 10 * width_sf_mm, PPI)
    etape_label_pos_y_list   = [mm_to_px( y * height_sf_mm, PPI) for y in [40, 74, 101, 129]]
    etape_button_dx          = mm_to_px( 10 * width_sf_mm, PPI)
    etape_button_dy          = mm_to_px(  5 * height_sf_mm, PPI)
    etape_check_dy           = mm_to_px( -8 * height_sf_mm, PPI)
    
    exit_button_x_pos        = mm_to_px(193 * width_sf_mm,  PPI) 
    exit_button_y_pos        = mm_to_px(145 * height_sf_mm, PPI)
    
    year_button_x_pos        = mm_to_px( 10 * width_sf_mm,  PPI) 
    year_button_y_pos        = mm_to_px( 26 * height_sf_mm, PPI)    
    dy_year                  = -6
    ds_year                  = 5

    # Setting useful aliases
    bdd_multi_annuelle_folder_alias = ARCHI_BDD_MULTI_ANNUELLE["root"]
    bdd_mensuelle_alias             = ARCHI_YEAR["bdd mensuelle"] 
    homonymes_path_alias            = ARCHI_YEAR["homonymes folder"]
    homonymes_file_base_alias       = ARCHI_YEAR["homonymes file name base"]
    OTP_path_alias                  = ARCHI_YEAR["OTP folder"]
    OTP_file_base_alias             = ARCHI_YEAR["OTP file name base"]
    pub_list_path_alias             = ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias        = ARCHI_YEAR["pub list file name base"]
    corpus_alias                    = ARCHI_YEAR['corpus']
    dedup_alias                     = ARCHI_YEAR['dedup']
    parsing_alias                   = ARCHI_YEAR['parsing']
    submit_alias                    = ARCHI_YEAR["submit file name"]
    listing_alias                   = ARCHI_RH["root"]
    effectifs_folder_name_alias     = ARCHI_RH["effectifs"]
    effectifs_file_name_alias       = ARCHI_RH["effectifs file name"]
    maj_effectifs_folder_name_alias = ARCHI_RH["maj"] 
    backup_folder_name_alias    = ARCHI_SECOURS["root"]
    
    # Setting useful paths independent from corpus year
    backup_root_path    = bibliometer_path / Path(backup_folder_name_alias)
    effectifs_root_path = bibliometer_path / Path(listing_alias)
    effectifs_folder_path     = effectifs_root_path / Path(effectifs_folder_name_alias)
    maj_effectifs_folder_path = effectifs_root_path / Path(maj_effectifs_folder_name_alias)    
    all_effectifs_path        = effectifs_folder_path / Path(effectifs_file_name_alias)
    all_effectifs_backup_path = backup_root_path      / Path(effectifs_file_name_alias) 
    
    dpt_label_list = list(DPT_LABEL_DICT.keys()) 
    
    ### Décoration de la page
    # - Canvas
    fond = tk.Canvas(self, 
                     width = win_width_px, 
                     height = win_height_px)
    fond.place(x = 0, y = 0)
    
    # - Etapes labels
    etape_label_font   = tkFont.Font(family = FONT_NAME, 
                                     size = eff_etape_font_size,
                                     weight = 'bold')
    etapes_number      = len(ETAPE_LABEL_TEXT_LIST)
    etape_label_format = 'left'
    etape_underline    = -1
    etapes             = [_etape_frame(self, etape_num) for etape_num in range(etapes_number)]    
    
    ### Choix de l'année 
    years_list = five_last_available_years(bibliometer_path)
    default_year = years_list[-1]  
    variable_years = tk.StringVar(self)
    variable_years.set(default_year)
    
    # Création de l'option button des années    
    self.font_OptionButton_years = tkFont.Font(family = FONT_NAME, 
                                               size = eff_buttons_font_size)
    self.OptionButton_years = tk.OptionMenu(self, 
                                            variable_years, 
                                            *years_list)
    self.OptionButton_years.config(font = self.font_OptionButton_years)
    
        # Création du label
    self.font_Label_years = tkFont.Font(family = FONT_NAME, 
                                        size = eff_select_font_size)
    self.Label_years = tk.Label(self, 
                                text = TEXT_YEAR_PI, 
                                font = self.font_Label_years)
    self.Label_years.place(x = year_button_x_pos, y = year_button_y_pos)
    
    place_after(self.Label_years, self.OptionButton_years, dy = dy_year)
    encadre_RL(fond, self.Label_years, self.OptionButton_years, ds = ds_year)

    ################## Etape 1 : Croisement auteurs-effectifs 
    ### Fonction executée par le bouton 'button_croisement' 
    def _launch_recursive_year_search():
        '''       
        '''
                                         
        # Standard library imports
        import os
        import shutil

        # 3rd party imports    
        import pandas as pd
        from pathlib import Path
                                         
        def _annee_croisement(corpus_year):
            all_effectifs_df = pd.read_excel(all_effectifs_path, sheet_name = None)
            annees_dispo = [int(x) for x in list(all_effectifs_df.keys())]
            annees_a_verifier = [int(corpus_year) - int(search_depth) + (i+1) for i in range(int(search_depth))]
            annees_verifiees = list()
            for i in annees_a_verifier:
                if i in annees_dispo: annees_verifiees.append(i)
            if len(annees_verifiees) > 0:
                return annees_verifiees
            else:
                warning_title = "!!! Attention !!!"
                warning_text  = f"Le nombre d'années disponibles est insuffisant "
                warning_text += f"dans le fichier des effectifs du LITEN."
                warning_text += f"\nLe croisement auteurs-effectifs ne peut être effectué !"
                warning_text += f"\n1- Complétez le fichier des effectifs du LITEN ;"
                warning_text += f"\n2- Puis relancer le croisement auteurs-effectifs."                    
                messagebox.showwarning(warning_title, warning_text)                         
                return None 
                                         
        def _recursive_year_search_try():
            try:             
                end_message = recursive_year_search(bdd_mensuelle_path, 
                                                    all_effectifs_path,
                                                    bibliometer_path,
                                                    year_select, 
                                                    search_depth)
                print('\n',end_message)
                info_title = '- Information -'
                info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} a été effectué."
                info_text += f"\n\nLes IFs disponibles ont été automatiquement attribués."  
                info_text += f"\nLa résolution des homonymes peut être lancée."                 
                messagebox.showinfo(info_title, info_text)
                return 'ok'

            except FileNotFoundError:
                warning_title = "!!! ATTENTION : fichier manquant !!!"
                warning_text  = f"La synthèse de l'année {year_select} n'est pas disponible."
                warning_text += f"\n1- Revenez à l'onglet 'Analyse élémentaire des corpus' ;"
                warning_text += f"\n2- Effectuez la synthèse pour cette année ;"
                warning_text += f"\n3- Puis relancez le croisement pour cette année."                         
                messagebox.showwarning(warning_title, warning_text)
                return None
        
        # Getting year selection, search depth selection and check_effectif_status
        year_select =  variable_years.get()
        search_depth = go_back_years.get()
        check_effectif_status = check_effectif_var.get()
        
        # Setting paths dependent on year_select
        corpus_year_path = bibliometer_path / Path(year_select)                 
        parsing_path = corpus_year_path / Path(corpus_alias) / Path(dedup_alias) / Path(parsing_alias)
        bdd_mensuelle_path =  corpus_year_path / Path(bdd_mensuelle_alias)
        submit_path = corpus_year_path / Path(bdd_mensuelle_alias) / Path(submit_alias)        
        
        # Linking Liten authors with Liten workers
        if check_effectif_status:
            # Lancement de la fonction MAJ Effectif
            ask_title = "- Confirmation de la mise à jour des effectifs -"
            ask_text  = f"Le fichier des effectifs LITEN va être mis à jour "
            ask_text += f"avec les nouvelles données disponibles dans le dossier :"
            ask_text += f"\n\n '{maj_effectifs_folder_path}'."
            ask_text += f"\n\nCette opération peut prendre quelques minutes."
            ask_text += f"\nDans l'attente, ne pas fermer 'BiblioMeter'."
            ask_text += f"\n\nAvant de poursuivre le croisement auteurs-effectifs, "
            ask_text += f"confirmez la mise à jour ?"            
            answer_1  = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:                                                                                  
                update_employees(bibliometer_path)
                info_title = "- Information -"
                info_text  = f"La mise à jour des effectifs a été effectuée."
                info_text += f"\nLe croisement pour l'année {year_select} va être poursuivi."
                messagebox.showinfo(info_title, info_text)
            else:
            # Arrêt de la procédure
                ask_title = "- Confirmation du croisement auteurs-effectifs -"
                ask_text  = f"La mise à jour des effectifs est abandonnée."
                ask_text += f"\n\nConfirmez le croisement pour l'année {year_select} "
                ask_text += f"sans cette mise à jour ?"            
                answer_2  = messagebox.askokcancel(ask_title, ask_text)
                if not answer_2:
                    info_title = "- Information -"
                    info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} est annulé."
                    messagebox.showinfo(info_title, info_text)            
                    return
 
        # Vérification de la disponibilité du fichier All_effectifs.xlsx    
        all_effectifs_status = os.path.exists(all_effectifs_path) 
        all_effectifs_backup_status = os.path.exists(all_effectifs_backup_path)
        if not all_effectifs_status:
            if all_effectifs_backup_status:
                ask_title = "- Régénération du fichier des effectifs LITEN -"
                ask_text  = f"Le fichier des effectifs LITEN n'est pas disponible à l'emplacement attendu. "
                ask_text += f"\nL'utilisation de la dernière sauvegarde de secours est possible "
                ask_text += f"pour effectuer le croisement auteurs-effectifs."
                ask_text += f"\n\nConfirmer cette utilisation ?"
                answer_3  = messagebox.askokcancel(ask_title, ask_text)
                if answer_3:
                    # Alors comme c'est oui, il faut aller chercher le fichier et le copier au bon endroit 
                    _ = shutil.copy(all_effectifs_backup_path, all_effectifs_path)
                else:
                     # Arrêt de la procédure
                    info_title = "- Information -"
                    info_text  = f"Le fichier des effectifs est indisponible "
                    info_text += f"et sa sauvegarde n'est pas utilisée."
                    info_text += f"\nLe croisement auteurs-effectifs est annulé."
                    messagebox.showinfo(info_title, info_text)
                    return        
            else:
                # Arrêt de la procédure
                info_title = "- Information -"
                info_text  = f"Le fichier des effectifs et sa sauvegarde sont indisponibles."
                info_text += f"\nLe croisement auteurs-effectifs est abandonné."
                messagebox.showinfo(info_title, info_text)
                return
                                
        # Vérifier les années disponibles                                         
        annees_disponibles = _annee_croisement(year_select)
        if annees_disponibles == None:
            return        
                                                 
        ask_title = "- Confirmation du croisement auteurs-effectifs -"
        ask_text  = f"Le croisement  avec les effectifs des années "
        ask_text += f"{', '.join([str(i) for i in annees_disponibles])} "
        ask_text += f"a été lancé pour l'année {year_select}."
        ask_text += f"\nCette opération peut prendre quelques minutes."
        ask_text += f"\nDans l'attente, ne pas fermer 'BiblioMeter'."
        ask_text += f"\n\nContinuer ?"
        answer    = messagebox.askokcancel(ask_title, ask_text)
        if answer:
            submit_status = os.path.exists(submit_path)                             
            if not submit_status:
                _recursive_year_search_try()
            else: 
                ask_title = "- Reconstruction du croisement auteurs-effectifs -"
                ask_text  = f"Le croisement pour l'année {year_select} est déjà disponible."
                ask_text += f"\n\nReconstruire le croisement ?"
                answer_4  = messagebox.askokcancel(ask_title, ask_text)                         
                if answer_4:
                    _recursive_year_search_try()
                else:
                    info_title = "- Information -"
                    info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} "
                    info_text += f"dejà disponible est conservé."                   
                    messagebox.showinfo(info_title, info_text)                     
        else:
            info_title = "- Information -"
            info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} "
            info_text += f"est annulé."            
            messagebox.showinfo(info_title, info_text)
        return

    ### Définition ou choix de la profondeur de recherche
    # Fixe la profondeur de recherche à 5 ans dans l'historique des effectifs
    go_back_years_list_rh = [i for i in range(1,date.today().year-2009)]
    go_back_years = tk.StringVar(self)
    go_back_years.set(go_back_years_list_rh[4])
    
    # Création de l'option de choix de la profondeur de recherche
    #font_croisement_l = tkFont.Font(family = FONT_NAME, 
    #                                size   = eff_launch_font_size)
    #label_format_l = 'left'
    #Label_croisement_l = tk.Label(self, 
    #                              text = TEXT_CROISEMENT_L, 
    #                              font = font_croisement_l, 
    #                              justify = label_format_l)
    #etape_1 = etapes[0]
    #place_bellow(etape_1, Label_croisement_l, dy = mm_to_px(5 * height_sf_mm , PPI))
    #OptionButton_goback = tk.OptionMenu(self, go_back_years, *go_back_years_list_rh)
    #OptionButton_goback.configure(font = font_croisement_l)   
    
    ### Définition du  bouton 'button_croisement' 
    font_croisement = tkFont.Font(family = FONT_NAME, 
                                  size   = eff_launch_font_size)
    button_croisement = tk.Button(self, 
                                  text = TEXT_CROISEMENT,
                                  font = font_croisement, 
                                  command = lambda: _launch_recursive_year_search())
    
    check_effectif_var = tk.IntVar()
    check_effectif_box = tk.Checkbutton(self, 
                                        text = TEXT_MAJ_EFFECTIFS, 
                                        variable = check_effectif_var, 
                                        onvalue = 1, 
                                        offvalue = 0)
    
    font_check = tkFont.Font(family = FONT_NAME, 
                             size = eff_answer_font_size)

    etape_1 = etapes[0]
    place_bellow(etape_1, 
                 check_effectif_box, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy / 2)
    place_bellow(check_effectif_box, 
                 button_croisement, 
                 dy = etape_button_dy / 2)
    
    # Dextruction de croisement car on ne l'autorise plus pour le moment
    #Label_croisement.destroy()    
                                             
    ################## Etape 2 : Résolution des homonymies
    ### Fonction executée par le bouton 'button_homonymes'     
    def _launch_resolution_homonymies():
        '''
        
        '''
    
        def _resolution_homonymies_try():
            try: 
                end_message = solving_homonyms(submit_path, homonymes_file_path)
                print('\n',end_message)
                info_title = "- Information -"
                info_text  = f"Le fichier pour la résolution des homonymies de l'année {year_select} a été créé "
                info_text += f"dans le dossier :\n\n  '{homonymes_path}' "
                info_text += f"\n\nsous le nom :  '{homonymes_file_alias}'."
                info_text += f"\n\n1- Ouvrez ce fichier, "
                info_text += f"\n2- Supprimez manuellement les lignes des homonymes non-auteurs, "
                info_text += f"\n3- Puis sauvegardez le fichier sous le même nom."
                info_text += f"\n\nDès que le fichier est traité, "                
                info_text += f"\nl'affectation des OTPs peut être lancée."                 
                messagebox.showinfo(info_title, info_text)
                return 'ok'

            except FileNotFoundError:
                warning_title = "!!! ATTENTION : fichier manquant !!!"
                warning_text  = f"Le fichier contenant le croisement auteurs-effectifs "
                warning_text += f"de l'année {year_select} n'est pas disponible."
                warning_text += f"\n1- Effectuez d'abord le croisement pour cette année."
                warning_text += f"\n2- Puis relancez la résolution des homonymies pour cette année."                         
                messagebox.showwarning(warning_title, warning_text)
                return None 
            
            except:
                warning_title = "!!! ATTENTION : erreur inconnue !!!"
                warning_text  = f"Contactez les auteurs de l'application."                        
                messagebox.showwarning(warning_title, warning_text)                
                return None
            
        # Renewing year selection
        year_select = variable_years.get()
        
        # Setting paths and aliases dependent pn year_select  
        homonymes_file_alias =  homonymes_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path = bibliometer_path / Path(year_select)                 
        submit_path = corpus_year_path / Path(bdd_mensuelle_alias) / Path(submit_alias) 
        homonymes_path = corpus_year_path / Path(homonymes_path_alias)
        homonymes_file_path = homonymes_path / Path(homonymes_file_alias)
        
        ask_title = "- Confirmation de l'étape de résolution des homonymies -"
        ask_text  = f"La création du fichier pour cette résolution "
        ask_text += f"a été lancée pour l'année {year_select}."
        ask_text += f"\n\nContinuer ?"
        answer    = messagebox.askokcancel(ask_title, ask_text)        
        if answer:
            homonymes_status = os.path.exists(homonymes_file_path)                           
            if not homonymes_status:
                _resolution_homonymies_try()
            else: 
                ask_title = "- Reconstruction de la résolution des homonymes -"
                ask_text  = f"Le fichier pour la résolution des homonymies "
                ask_text += f"de l'année {year_select} est déjà disponible."
                ask_text += f"\n\nReconstruire ce fichier ?"
                answer_1  = messagebox.askokcancel(ask_title, ask_text)                         
                if answer_1:
                    _resolution_homonymies_try()
                else:
                    info_title = "- Information -"
                    info_text  = f"Le fichier pour la résolution des homonymies "
                    info_text += f"de l'année {year_select} dejà disponible est conservé."                   
                    messagebox.showinfo(info_title, info_text)                     
        else:
            info_title = "- Information -"
            info_text = f"La création du fichier pour la résolution "
            info_text += f"des homonymies de l'année {year_select} est annulée."            
            messagebox.showinfo(info_title, info_text)
            return
    
    ### Définition du bouton "button_homonymes"
    font_homonymes = tkFont.Font(family = FONT_NAME, 
                                 size   = eff_launch_font_size)
    button_homonymes = tk.Button(self, 
                                     text = TEXT_HOMONYMES, 
                                     font = font_homonymes, 
                                     command = lambda: _launch_resolution_homonymies())
    etape_2 = etapes[1]
    place_bellow(etape_2, 
                 button_homonymes, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy)
    
    ################## Etape 3 : Attribution des OTPs
    ### Fonction executée par le bouton 'button_OTP' 
    def _launch_add_OTP():
        '''
        
        '''
    
        def _add_OTP_try():
            try:
                end_message = add_OTP(homonymes_file_path, OTP_path, OTP_file_base_alias)
                print('\n',end_message)
                info_title = "- Information -"
                info_text  = f"Les fichiers de l'année {year_select} pour l'attribution des OTPs "
                info_text += f"ont été créés dans le dossier : \n\n'{OTP_path}' "
                info_text += f"\n\n1- Ouvrez le fichier du département ad-hoc, "
                info_text += f"\n2- Attribuez manuellement à chacune des publications un OTP, "
                info_text += f"\n3- Sauvegardez le fichier en ajoutant à son nom '_ok'."
                info_text += f"\n\nDès que les fichiers de tous les départements sont traités, "
                info_text += f"\nla liste consolidée des publications de l'année {year_select} peut être créée."                 
                messagebox.showinfo(info_title, info_text)
                return 'ok'

            except FileNotFoundError:
                warning_title = "!!! ATTENTION : fichier manquant !!!"
                warning_text  = f"Le fichier contenant la résolution des homonymies "
                warning_text += f"de l'année {year_select} n'est pas disponible."
                warning_text += f"\n1- Effectuez la résolution des homonymies pour cette année."
                warning_text += f"\n2- Relancez l'attribution des OTPs pour cette année."                         
                messagebox.showwarning(warning_title, warning_text)
                return None 
            
            except:
                warning_title = "!!! ATTENTION : erreur inconnue !!!"
                warning_text  = f"Contactez les auteurs de l'application."                        
                messagebox.showwarning(warning_title, warning_text)                
                return None
            
        # Renewing year selection
        year_select = variable_years.get()
        
        # Setting paths and aliases dependent on year_select  
        homonymes_file_alias =  homonymes_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path = bibliometer_path / Path(year_select)                 
        homonymes_path = corpus_year_path / Path(homonymes_path_alias)
        homonymes_file_path = homonymes_path / Path(homonymes_file_alias) 
        OTP_path = corpus_year_path / Path(OTP_path_alias)
        
        ask_title = "- Confirmation de l'étape d'attribution des OTPs -"
        ask_text  = f"La création des fichiers pour cette attribution "
        ask_text += f"a été lancée pour l'année {year_select}."
        ask_text += f"\n\nContinuer ?"
        answer    = messagebox.askokcancel(ask_title, ask_text)        
        if answer:
            OTP_path_status = os.path.exists(OTP_path)
            if OTP_path_status:
                OTP_files_status_list = []
                for dpt_label in dpt_label_list:
                    OTP_file_name_dpt = OTP_file_base_alias + '_' + dpt_label + '.xlsx'
                    OTP_files_status_list.append(not(os.path.exists(OTP_file_name_dpt)))
                if any(OTP_files_status_list):                           
                    _add_OTP_try()
                else: 
                    ask_title = "- Reconstruction de l'attribution des OTPs -"
                    ask_text  = f"Les fichiers pour l'attribution des OTPs "
                    ask_text += f"de l'année {year_select} sont déjà disponibles."
                    ask_text += f"\n\nReconstruire ces fichiers ?"
                    answer_1  = messagebox.askokcancel(ask_title, ask_text)                         
                    if answer_1:
                        _add_OTP_try()
                    else:
                        info_title = "- Information -"
                        info_text  = f"Les fichiers pour l'attribution des OTPs "
                        info_text += f"de l'année {year_select} dejà disponibles sont conservés."                   
                        messagebox.showinfo(info_title, info_text)
            else:
                os.mkdir(OTP_path)
                _add_OTP_try()
        else:
            info_title = "- Information -"
            info_text = f"La création des fichiers pour l'attribution des OTPs "
            info_text += f"de l'année {year_select} est annulée."            
            messagebox.showinfo(info_title, info_text)
            return    

    ### Définition du bouton "button_OTP"
    font_OTP = tkFont.Font(family = FONT_NAME, 
                           size   = eff_launch_font_size)
    button_OTP = tk.Button(self, 
                           text = TEXT_OTP, 
                           font = font_OTP,  
                           command = lambda: _launch_add_OTP())
    etape_3 = etapes[2]
    place_bellow(etape_3, 
                 button_OTP, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy)
    
    ################## Etape 4 : Liste consolidée des publications
    ### Fonction executée par le bouton 'button_OTP' 
    def _launch_pub_list_conso():
        '''
        
        '''
    
        def _consolidate_pub_list():
            try:
                end_message = consolidate_pub_list(OTP_path, pub_list_file_path, OTP_file_base_alias)
                print('\n',end_message)
                end_message = concatenate_pub_lists(bibliometer_path, years_list)
                print('\n',end_message)
                info_title = "- Information -"
                info_text  = f"La liste consolidée des publications de l'année {year_select} "
                info_text += f"a été créée dans le dossier :\n\n '{pub_list_path}' "
                info_text += f"\n\nsous le nom :   '{pub_list_file_alias}'."
                info_text += f"\n\nDe plus, la concaténation des listes consolidées des publications "
                info_text += f"disponibles, à été créée dans le dossier :\n\n '{bdd_multi_annuelle_folder_alias}' "
                info_text += f"\n\nsous un nom vous identifiant ainsi que la liste des années prises en compte "
                info_text += f"et caractérisé par la date et l'heure de la création."
                info_text += f"\n\nLes IFs disponibles ont été automatiquement attribués."                
                messagebox.showinfo(info_title, info_text)
                return 'ok'

            except FileNotFoundError:
                warning_title = "!!! ATTENTION : fichiers manquants !!!"
                warning_text  = f"Les fichiers d'attribution des OTPs "
                warning_text += f"de l'année {year_select} ne sont pas tous disponibles."
                warning_text += f"\n1- Effectuez l'attribution des OTPs pour cette année."
                warning_text += f"\n2- Relancez la consolidation de la liste des publications pour cette année."                         
                messagebox.showwarning(warning_title, warning_text)
                return None 
            
            except:
                warning_title = "!!! ATTENTION : erreur inconnue !!!"
                warning_text  = f"Contactez les auteurs de l'application."                        
                messagebox.showwarning(warning_title, warning_text)                
                return None
            
        # Renewing year selection and years 
        year_select = variable_years.get()
                
        # Setting year_select dependent paths and aliases
        pub_list_file_alias =  pub_list_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path = bibliometer_path / Path(year_select)                  
        OTP_path = corpus_year_path / Path(OTP_path_alias)
        pub_list_path = corpus_year_path / Path(pub_list_path_alias)
        pub_list_file_path = pub_list_path / Path(pub_list_file_alias)
        
        ask_title = "- Confirmation de l'étape de consolidation de la liste des publications -"
        ask_text  = f"La création du fichier de la liste consolidée des publications "
        ask_text += f"a été lancée pour l'année {year_select}."
        ask_text += f"\n\nContinuer ?"
        answer    = messagebox.askokcancel(ask_title, ask_text)        
        if answer:
            pub_list_status = os.path.exists(pub_list_file_path)                           
            if not pub_list_status:
                _consolidate_pub_list()
            else: 
                ask_title = "- Reconstruction de la liste consolidée des publications -"
                ask_text  = f"Le fichier de la liste consolidée des publications "
                ask_text += f"de l'année {year_select} est déjà disponible."
                ask_text += f"\n\nReconstruire ce fichier ?"
                answer_1  = messagebox.askokcancel(ask_title, ask_text)                         
                if answer_1:
                    _consolidate_pub_list()
                else:
                    info_title = "- Information -"
                    info_text  = f"Le fichier de la liste consolidée des publications "
                    info_text += f"de l'année {year_select} dejà disponible est conservé."                   
                    messagebox.showinfo(info_title, info_text)                     
        else:
            info_title = "- Information -"
            info_text = f"La création du fichier de la liste consolidée des publications "
            info_text += f"de l'année {year_select} est annulée."            
            messagebox.showinfo(info_title, info_text)
            return                                     

    # Bouton pour créer fichier excel d'un filtre par département ???
    font_finale = tkFont.Font(family = FONT_NAME, 
                              size   = eff_launch_font_size)
    Button_finale = tk.Button(self, 
                              text = TEXT_PUB_CONSO, 
                              font = font_finale, 
                              command = lambda: _launch_pub_list_conso())
    etape_4 = etapes[3]
    place_bellow(etape_4, 
                 Button_finale, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy)
              
    
    ################## Bouton pour sortir de la page
    font_button_quit = tkFont.Font(family = FONT_NAME, 
                                   size   = eff_buttons_font_size)
    button_quit = tk.Button(self, 
                            text = TEXT_PAUSE, 
                            font = font_button_quit, 
                            command = lambda: _launch_exit()).place(x = exit_button_x_pos, 
                                                                    y = exit_button_y_pos, 
                                                                    anchor = 'n')