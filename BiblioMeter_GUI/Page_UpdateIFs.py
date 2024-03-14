__all__ = ['create_update_ifs']

# Nom de module et nom de fonctions à revoir !!!

def _launch_update_if_db(institute, 
                         bibliometer_path,
                         corpus_years_list,
                         pub_list_folder_path,
                         all_if_path,
                        ):
    """
    """
    
    # 3rd party imports    
    from tkinter import messagebox
    
    # Local imports     
    from BiblioMeter_FUNCTS.BM_UpdateImpactFactors import update_inst_if_database
    
    # Lancement de la fonction de MAJ base de données des IFs
    ask_title = "- Confirmation de la mise à jour de la base de données des IFs -"
    ask_text  = f"La base de données des IFs va être mise à jour "
    ask_text += f"avec les nouvelles données disponibles dans les dossiers :"
    ask_text += f"\n\n '{pub_list_folder_path}' "
    ask_text += f"\n\n des corpus des années \n\n  {corpus_years_list} ."
    ask_text += f"\n\nCette opération peut prendre quelques secondes."
    ask_text += f"\nDans l'attente, ne pas fermer 'BiblioMeter'."        
    ask_text += f" \n\nEffectuer la mise à jour ?"            
    answer    = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        # Mise à jour de la base de données des IFs
        _, if_years_list = update_inst_if_database(institute, bibliometer_path, corpus_years_list)
        info_title = "- Information -"
        info_text  = f"La mise à jour de la base de données des IFs a été effectuée "
        info_text += f"pour les années  {if_years_list}."
        info_text += f"\n\nLa consolidation des corpus des années "
        info_text += f"\n {corpus_years_list} "
        info_text += f"\npeut être lancée."
        messagebox.showinfo(info_title, info_text)
        update_status = True
    else:
        # Arrêt de la procédure
        info_title = "- Information -"
        info_text  = f"La mise à jour de la base de données des IFs est abandonnée."            
        messagebox.showwarning(info_title, info_text)          
        update_status = False
    return update_status 
    
def _launch_update_pub_if(institute, 
                          bibliometer_path, 
                          corpus_years_list,
                          pub_list_folder_alias,
                          pub_list_file_base_alias,
                          missing_if_base_alias,
                          missing_issn_base_alias,
                          all_if_path,
                         ):
    """
    """
    # Standard library imports
    import os
    from pathlib import Path
    
    # 3rd party imports    
    from tkinter import messagebox
    
    # Local imports
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import add_if
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import split_pub_list
    
    if_database_complete = None
    missing_pub_file_year = None
    for corpus_year in corpus_years_list:
        # Setting corpus dependant paths
        pub_list_file = pub_list_file_base_alias + " " + corpus_year + ".xlsx"
        year_pub_list_folder_path = bibliometer_path / Path(corpus_year) / pub_list_folder_alias
        out_file_path     = year_pub_list_folder_path / Path(pub_list_file)
        missing_if_path   = year_pub_list_folder_path / Path(corpus_year + missing_if_base_alias)
        missing_issn_path = year_pub_list_folder_path / Path(corpus_year + missing_issn_base_alias)
        
        # Cheking availability of pub_list file of the year
        out_file_status = os.path.exists(out_file_path) 
        if out_file_status:
            # Updating Impact Factors and saving new consolidated list of publications 
            # this also for saving results files to complete IFs database
            _, if_database_complete = add_if(institute, 
                                             bibliometer_path,
                                             out_file_path, 
                                             out_file_path, 
                                             missing_if_path,
                                             missing_issn_path, 
                                             corpus_year)

            # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
            split_pub_list(institute, bibliometer_path, corpus_year)
            if not if_database_complete:
                info_title = "- Information -"
                info_text  = f"La base de données des facteurs d'impact étant incomplète, "
                info_text += f"les listes des journaux avec IFs ou ISSNs inconnus "
                info_text += f"ont été créées dans le dossier \n\n '{year_pub_list_folder_path}' \n\nsous les noms :"
                info_text += f"\n\n '{missing_if_path}' "
                info_text += f"\n\n '{missing_issn_path}' "
                info_text += f"\n\n Ces fichiers peuvent être modifiés pour compléter la base de donnée des IFs :"
                info_text += f"\n\n1- Ouvrez chacun de ces fichiers, "
                info_text += f"\n2- Complétez manuellement les IFs inconnus ou les ISSNs et IFs inconnus, selon le fichier,"
                info_text += f"\n3- Puis sauvegardez les fichiers sous le même nom."
                info_text += f"\n\nChaque fois que ces compléments sont apportés, "
                info_text += f"la base de données des IFs doit être mise à jour, "
                info_text += f"ainsi que toutes les listes consolidées des publications existantes."
                info_text += f"\n\nCependant, la mise à jour va être poursuivie avec la base de données des IFs incomplète."
                messagebox.showinfo(info_title, info_text)
        else:
            warning_title = "!!! ATTENTION : fichier absent !!!"
            warning_text  = f"La liste consolidée des publications du corpus de l'année {corpus_year} "
            warning_text += f"\nn'est pas disponible à l'emplacement attendu. "
            warning_text += f"\n1- Relancer la consolidation annuelle pour ce corpus ;"
            warning_text += f"\n2- Puis relancez la mise à jour des IFs des listes consolidées."
            messagebox.showwarning(warning_title, warning_text) 
            missing_pub_file_year = corpus_year 
            return missing_pub_file_year, if_database_complete
    return missing_pub_file_year, if_database_complete


def create_update_ifs(self, institute, bibliometer_path, parent):
    
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
    import tkinter as tk
    from tkinter import font as tkFont
    from tkinter import messagebox
    
    # Local imports
    import BiblioMeter_GUI.GUI_Globals as gg
    import BiblioMeter_GUI.Useful_Functions as guf
    import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_inst_org
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import concatenate_pub_lists  
    
    # Internal functions    
    def _launch_update_if_db_try():
        # Cheking availability of IF-all-years file
        if_db_file_status = os.path.exists(if_db_path)    
        if if_db_file_status:
            print("Update of IFs database launched")
            if_db_update_status = _launch_update_if_db(institute, 
                                                       bibliometer_path,
                                                       corpus_years_list,
                                                       pub_list_folder_path,
                                                       if_db_path,
                                                      )
        else:
            warning_title = "!!! ATTENTION : fichier absent !!!"
            warning_text  = f"Le fichier {if_file_name_alias} de la base de données des IFs "
            warning_text += f"\nn'est pas disponible à l'emplacement attendu. "
            warning_text += f"\nL'utilisation de la dernière sauvegarde de secours du dossier \n {backup_if_folder_path} "
            warning_text += f"\nest possible : "
            warning_text += f"\n1- Copier le fichier de secours dans le dossier : \n {if_root_path} ;"
            warning_text += f"\n2- Puis relancez la mise à jour de la base de données des IFs."
            messagebox.showwarning(warning_title, warning_text) 
            if_db_update_status = False
        return

    def _missing_pub_file_year_check():
        missing_pub_file_year, if_database_complete = _launch_update_pub_if(institute, 
                                                                            bibliometer_path, 
                                                                            corpus_years_list,
                                                                            pub_list_folder_alias,
                                                                            pub_list_file_base_alias,
                                                                            missing_if_base_alias,
                                                                            missing_issn_base_alias,
                                                                            if_db_path,
                                                                           )
        if not missing_pub_file_year:
            concatenate_pub_lists(institute, bibliometer_path, corpus_years_list)
            print("Consolidated lists of publications concatenated after IFs update")
            info_title = '- Information -'
            info_text  = f"La mise à jour des IFs dans les listes consolidées des publications des corpus :"
            info_text += f"\n\n   {corpus_years_list}"
            info_text += f"\n\na été effectuée avec une base de données des IFs "
            if if_database_complete:
                info_text += f"complète."
            else:              
                info_text += f"incomplète."
            info_text += f"\n\nDe plus, la liste consolidée des publications a été décomposée "
            info_text += f"en trois fichiers disponibles dans le même dossier correspondant aux différentes "
            info_text += f"classes de documents (les classes n'étant pas exhaustives, la décomposition peut être partielle)."            
            info_text += f"\n\nEnfin, la concaténation des listes consolidées des publications "
            info_text += f"disponibles, à été créée dans le dossier :\n\n '{bdd_multi_annuelle_folder_alias}' "
            info_text += f"\n\nsous un nom vous identifiant ainsi que la liste des années prises en compte "
            info_text += f"et caractérisé par la date et l'heure de la création." 
            messagebox.showinfo(info_title, info_text)
            
        else:
            info_title = '- Information -'
            info_text  = f"La mise à jour des IFs dans les listes consolidées a été interrompue par l'absence "
            info_text += f"de la liste consolidée des publications du corpus :"
            info_text += f" {missing_pub_file_year}"
            messagebox.showinfo(info_title, info_text)             
        return
    
    def _launch_update_pub_if_try():
        if if_db_update_status:
            print("Update of IFs in consolidated lists of publications launched")
            _missing_pub_file_year_check()                              
        else:
            # Confirmation du lancement de la fonction de MAJ des IFs dans les listes consolidées
            # sans MAJ de la base de données des IFs
            ask_title = "- Confirmation de la mise à jour des IFs dans les listes consolidées des publications -"
            ask_text  = f"La base de données des IFs n'a pas été préalablement mise à jour."
            ask_text += f"\n\nLa mise à jour des IFs dans les listes consolidées des corpus des années "
            ask_text += f"\n\n  {corpus_years_list} "
            ask_text += f"\n\nva être effectuée avec la version de la base de données des IFs qui est disponible."           
            ask_text += f"\n\nCette opération peut prendre quelques secondes."
            ask_text += f"\nDans l'attente, ne pas fermer 'BiblioMeter'."        
            ask_text += f" \n\nEffectuer la mise à jour ?"            
            answer    = messagebox.askokcancel(ask_title, ask_text)
            if answer:
                _missing_pub_file_year_check()
            else:                           
                info_title = '- Information -'
                info_text  = f"La lmise à jour des listes consolidées des publications est abandonnée."
                messagebox.showinfo(info_title, info_text)
        return   
            
    def _launch_exit():
        message =  "Vous allez fermer BiblioMeter. "
        message += "\nRien ne sera perdu et vous pourrez reprendre le traitement plus tard."
        message += "\n\nSouhaitez-vous faire une pause dans le traitement ?"
        answer_1 = messagebox.askokcancel('Information', message)
        if answer_1:
            parent.destroy()
            
    # Getting useful window sizes and scale factors depending on displays properties
    sizes_tuple   = guf.root_properties(self)
    win_width_px  = sizes_tuple[0]    # unused here
    win_height_px = sizes_tuple[1]    # unused here
    width_sf_px   = sizes_tuple[2] 
    height_sf_px  = sizes_tuple[3]    # unused here
    width_sf_mm   = sizes_tuple[4]
    height_sf_mm  = sizes_tuple[5]
    width_sf_min  = min(width_sf_mm, width_sf_px)
    
    # Setting effective font sizes and positions (numbers are reference values in mm)
    eff_etape_font_size      = guf.font_size(gg.REF_ETAPE_FONT_SIZE, width_sf_min)           #14
    eff_launch_font_size     = guf.font_size(gg.REF_ETAPE_FONT_SIZE-1, width_sf_min)
    eff_help_font_size       = guf.font_size(gg.REF_ETAPE_FONT_SIZE-2, width_sf_min)
    eff_buttons_font_size    = guf.font_size(gg.REF_ETAPE_FONT_SIZE-3, width_sf_min)      
    
    if_db_update_x_pos_px    = guf.mm_to_px(10 * width_sf_mm,  gg.PPI)
    if_db_update_y_pos_px    = guf.mm_to_px(35 * height_sf_mm, gg.PPI)     
    update_if_label_dx_px    = guf.mm_to_px( 0 * width_sf_mm,  gg.PPI)  
    update_if_label_dy_px    = guf.mm_to_px(15 * height_sf_mm, gg.PPI)   
    launch_dx_px             = guf.mm_to_px( 0 * width_sf_mm,  gg.PPI)    
    launch_dy_px             = guf.mm_to_px( 5 * height_sf_mm, gg.PPI)   
    exit_button_x_pos_px     = guf.mm_to_px(gg.REF_EXIT_BUT_POS_X_MM * width_sf_mm,  gg.PPI)    #193 
    exit_button_y_pos_px     = guf.mm_to_px(gg.REF_EXIT_BUT_POS_Y_MM * height_sf_mm, gg.PPI)    #145    
    
    # Setting common attributs
    etape_label_format = 'left'
    etape_underline    = -1                              
    
    # Setting useful aliases
    bdd_multi_annuelle_folder_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    pub_list_folder_alias           = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias        = pg.ARCHI_YEAR["pub list file name base"]
    backup_folder_name_alias        = pg.ARCHI_BACKUP["root"]    
    if_root_path_alias              = pg.ARCHI_IF["root"]
    if_file_name_alias              = pg.ARCHI_IF["all IF"]
    missing_if_base_alias           = pg.ARCHI_IF["missing_if_base"]
    missing_issn_base_alias         = pg.ARCHI_IF["missing_issn_base"]
    inst_if_file_name_alias         = pg.ARCHI_IF["institute_if_all_years"] 

    # Gettting institute parameters
    org_tup = set_inst_org(ig.CONFIG_JSON_FILES_DICT[institute], 
                           dpt_label_key = ig.DPT_LABEL_KEY, 
                           dpt_otp_key = ig.DPT_OTP_KEY)
    inst_if_status = org_tup[6] 
    if inst_if_status: if_file_name_alias = institute + inst_if_file_name_alias
       
    # Setting useful paths
    if_root_path = bibliometer_path / Path(if_root_path_alias)
    if_db_path   = if_root_path / Path(if_file_name_alias)
    backup_if_folder_path = bibliometer_path / Path(backup_folder_name_alias)
    backup_if_file_path   = backup_if_folder_path / Path (if_file_name_alias)
    pub_list_folder_path  =  bibliometer_path / Path(pub_list_folder_alias)
    
    # Setting list of corpus years
    corpus_years_list = guf.last_available_years(bibliometer_path, gg.CORPUSES_NUMBER)
    
    # Initializing status of IFs database update
    if_db_update_status = False
    
    ################## Mise à jour de la base de données des IFs

    ### Titre
    if_db_update_font = tkFont.Font(family = gg.FONT_NAME, 
                                 size = eff_etape_font_size,
                                 weight = 'bold')
    if_db_update_label = tk.Label(self,
                               text = gg.TEXT_ETAPE_5,
                               justify = etape_label_format,
                               font = if_db_update_font,
                               underline = etape_underline)
    
    if_db_update_label.place(x = if_db_update_x_pos_px, 
                             y = if_db_update_y_pos_px)   
    
    ### Explication
    help_label_font = tkFont.Font(family = gg.FONT_NAME, 
                                  size = eff_help_font_size)
    help_label = tk.Label(self, 
                          text = gg.HELP_ETAPE_5, 
                          justify = "left", 
                          font = help_label_font)
    guf.place_bellow(if_db_update_label, 
                     help_label)     
                                         
    ### Bouton pour lancer l'étape
    if_db_update_launch_font = tkFont.Font(family = gg.FONT_NAME, 
                                        size = eff_launch_font_size)
    if_db_update_launch_button = tk.Button(self,
                                        text = gg.TEXT_MAJ_BDD_IF,
                                        font = if_db_update_launch_font,
                                        command = lambda: _launch_update_if_db_try())
    guf.place_bellow(help_label, 
                     if_db_update_launch_button, 
                     dx = launch_dx_px, 
                     dy = launch_dy_px)
    
    ################## Mise à jour des Ifs dans les listes consolidées
    
    ### Titre 
    update_if_label_font = tkFont.Font(family = gg.FONT_NAME, 
                                        size = eff_etape_font_size,
                                        weight = 'bold')
    update_if_label = tk.Label(self, 
                               text = gg.TEXT_ETAPE_6, 
                               justify = "left", 
                               font = update_if_label_font)
    guf.place_bellow(if_db_update_launch_button, 
                     update_if_label, 
                     dx = update_if_label_dx_px, 
                     dy = update_if_label_dy_px)
    
    ### Explication de l'étape
    help_label_font = tkFont.Font(family = gg.FONT_NAME,
                               size = eff_help_font_size)
    help_label = tk.Label(self, 
                          text = gg.HELP_ETAPE_6, 
                          justify = "left", 
                          font = help_label_font)
    guf.place_bellow(update_if_label, 
                     help_label) 
    
    ### Bouton pour lancer la mise à jour des IFs dans les listes consolidées existantes 
    button_update_if_font = tkFont.Font(family = gg.FONT_NAME, 
                                         size = eff_launch_font_size)
    button_update_if = tk.Button(self, 
                                  text = gg.TEXT_MAJ_PUB_IF, 
                                  font = button_update_if_font, 
                                  command = lambda: _launch_update_pub_if_try())  
    guf.place_bellow(help_label, 
                     button_update_if, 
                     dx = launch_dx_px, 
                     dy = launch_dy_px)
    
    
    ################## Bouton pour sortir de la page
    font_button_quit = tkFont.Font(family =gg.FONT_NAME, 
                                   size   = eff_buttons_font_size)
    button_quit = tk.Button(self, 
                            text = gg.TEXT_PAUSE, 
                            font = font_button_quit, 
                            command = lambda: _launch_exit()).place(x = exit_button_x_pos_px, 
                                                                    y = exit_button_y_pos_px, 
                                                                    anchor = 'n')