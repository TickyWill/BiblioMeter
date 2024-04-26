__all__ = ['create_parsing_concat']

    
def _create_table(self, bibliometer_path, pos_x_init):    
    """The internal function `_create_table` creates the column names of the table used by 'Page_ParsingConcat.py'
    to display which files of the parsing treatment are available in the folder 'BiblioMeter_Files'. 
    The full path of this folder is given by the argument 'bibliometer_path'.
    The positions of the table items in the gui window 'root' are set using the argument 'pos_x_init',  
    and the tk window general properties as 'app_main' class variables.
    
    Args:
        bibliometer_path (path): The files root path for "BiblioMeter_Files" folder.
        pos_x_init (int): The initial horizontal position in pixels to be used for widgets 
                          positionning by classes of module "Page_ParsingConcat.py".
                         
    Returns:
        None.
        
    Note:
        The functions 'font_size' and 'mm_to_px' are imported 
        from the module 'Useful_Functions' of the package 'BiblioMeter_GUI'.
        The globals 'FONT_NAME' and 'PPI' are imported from the module 'GUI_Globals' 
        of the package 'BiblioMeter_GUI'.

    """
    
    # Standard library imports
    import tkinter as tk
    from tkinter import font as tkFont
    
    # Local imports
    import BiblioMeter_GUI.GUI_Globals as gg
    from BiblioMeter_GUI.Page_Classes import app_main
    from BiblioMeter_GUI.Useful_Functions import font_size 
    from BiblioMeter_GUI.Useful_Functions import mm_to_px 
    
    # Internal functions
    def _set_table_item(item_text, item_pos_x):
        item_case = tk.Label(self, 
                       text = item_text, 
                       font = header_font)
        item_case.place(x = item_pos_x, y = pos_y_ref, anchor = 'center')
        self.TABLE.append(item_case)
    
    # Setting specific font properties
    ref_font_size = 11
    local_font_size = font_size(ref_font_size, app_main.width_sf_min)    
    header_font = tkFont.Font(family = gg.FONT_NAME, 
                              size   = local_font_size)
    
    # Setting useful x position shift and y position reference in pixels    
    pos_x_shift = mm_to_px(25 * app_main.width_sf_mm,  gg.PPI)                                 
    pos_y_ref   = mm_to_px(30 * app_main.height_sf_mm, gg.PPI) # 35
    
    # Initializing x position in pixels
    pos_x = pos_x_init

    # Mise en page tableau
    item_text = 'Wos\nDonnées brutes'
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)
    
    item_text = 'Wos\nParsing' 
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)
    
    item_text = 'Scopus\nDonnées brutes' 
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)
    
    item_text = 'Scopus\nParsing' 
    pos_x += pos_x_shift    
    _set_table_item(item_text, pos_x)

    item_text = 'Synthèse du\nparsing des BDD' 
    pos_x += pos_x_shift    
    _set_table_item(item_text, pos_x)


def _update(self, bibliometer_path, pos_x, pos_y, esp_ligne):
    '''The internal function `_update` refreshes the current state 
    of the files in BiblioMeter_Files using the function `_create_table` 
    internal to the module 'Page_ParsingConcat' of the package 'BiblioMeter_GUI'. 
    It also updates the OptionMenu buttons used to select the year to be used.

    Args:
        bibliometer_path (path): The path leading to the file folder 'BilioMeter_Files'.
        pos_x (int): x axe's position for widgets of Page_ParsingConcat class.
        pos_y (int): y axe's position for widgets of Page_ParsingConcat class.
        esp_ligne (int): space in between some widgets of Page_ParsingConcat class.

    Returns:
        
    Note:
        The function 'mm_to_px' is imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The functions 'existing_corpuses', 'font_size' and 'place_after'
        are imported from the module 'Useful_Functions' of the package 'BiblioMeter_GUI'.
        The class 'CheckBoxCorpuses' is imported from the module 'Useful_Classes' 
        of the package 'BiblioMeter_GUI'.
        The globals FONT_NAME and PPI are imported from the module 'GUI_Globals' 
        of the package 'BiblioMeter_GUI'.
            
    '''
    
    # Standard library imports
    import tkinter as tk
    from tkinter import font as tkFont
    
    # Local imports
    import BiblioMeter_GUI.GUI_Globals as gg
    from BiblioMeter_GUI.Page_Classes import app_main
    from BiblioMeter_GUI.Useful_Classes import CheckBoxCorpuses
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import font_size 
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    
    # Setting useful local variables for positions modification (globals to create ??)
    # numbers are reference values in mm for reference screen 
    eff_font_size = font_size(11, app_main.width_sf_min)
    eff_dx        = mm_to_px(1 * app_main.width_sf_mm,  gg.PPI)
    eff_dy        = mm_to_px(1 * app_main.height_sf_mm, gg.PPI)

    # Getting files status for corpus concatenation and deduplication
    files_status = existing_corpuses(bibliometer_path)     
    list_corpus_year    = files_status[0]
    list_wos_rawdata    = files_status[1]
    list_wos_parsing    = files_status[2]
    list_scopus_rawdata = files_status[3]
    list_scopus_parsing = files_status[4]
    list_rational       = files_status[5]
    
    # Setting useful local variables for default selection items in selection lists 
    default_year = list_corpus_year[-1]   
    
    # ????
    for i in range(len(self.CHECK)):
        self.CHECK[i].efface()    

    for i, annee in enumerate(list_corpus_year):
        tmp = CheckBoxCorpuses(self, 
                               annee, 
                               list_wos_rawdata[i], 
                               list_wos_parsing[i], 
                               list_scopus_rawdata[i], 
                               list_scopus_parsing[i], 
                               list_rational[i])
        tmp.place(x = pos_x, 
                  y = i * esp_ligne + pos_y)
        self.CHECK.append(tmp)

    _create_table(self, bibliometer_path, pos_x)
    
    # Destruction puis reconstruction obligatoire 
    # pour mettre à jour les boutons années 
    # lors de mise à jour de l'état de la base
    
    # Destruct files status display
    self.OM_year_pc_1.destroy() 
    
    # Reconstruct files status display
    self.var_year_pc_1 = tk.StringVar(self) 
    self.var_year_pc_1.set(default_year)
    self.OM_year_pc_1 = tk.OptionMenu(self, 
                                      self.var_year_pc_1, 
                                      *list_corpus_year)
    font_year_pc_1 = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_font_size)
    self.OM_year_pc_1.config(font = font_year_pc_1)
    place_after(self.label_year_pc_1, 
                self.OM_year_pc_1, 
                dx = eff_dx,
                dy = - eff_dy)
    
    # Destruct files status display
    self.OM_year_pc_2.destroy() 
    
    # Reconstruct files status display    
    self.var_year_pc_2 = tk.StringVar(self)
    self.var_year_pc_2.set(default_year)
    self.OM_year_pc_2 = tk.OptionMenu(self, 
                                      self.var_year_pc_2, 
                                      *list_corpus_year)
    font_year_pc_2 = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_font_size)
    self.OM_year_pc_2.config(font = font_year_pc_2)
    place_after(self.label_year_pc_2, 
                self.OM_year_pc_2, 
                dx = eff_dx, 
                dy = - eff_dy)

    
def _launch_parsing(self, corpus_year, database_type, bibliometer_path, pos_x, pos_y, esp_ligne):
    """The internal function `_launch_parsing` parses corpuses from wos or scopus
    using the function 'biblio_parser'. It checks if all useful files are available
    in the 'BiblioMeter_Files' folder using the function 'existing_corpuses'.
    It saves the parsing files using paths set from the global 'ARCHI_YEAR'.
    It displays the number of articles parsed using the file path set using 
    the global 'PARSING_PERF'.
    It updates the files status using the function `_update` internal 
    to the module 'Page_ParsingConcat' of the package 'BiblioMeter_GUI'.
    
    Args:
        corpus_year (str): A string of 4 digits corresponding to the year of the corpus.
        database_type (str): The database type, ie: 'wos' or 'scopus'. 
        bibliometer_path (path): The full path for "BiblioMeter_Files" folder.
        pos_x (int): The x position to be used for widgets positionning 
                     by classes of module "Page_ParsingConcat.py".
        pos_y (int): The y position to be used for widgets positionning 
                     by classes of module "Page_ParsingConcat.py".
        esp_ligne (int): The space value for widgets spacing 
                         by classes of module "Page_ParsingConcat.py".
                         
    Returns:
        None.
        
    Note:
        The function 'biblio_parser' is imported from the module 'BiblioParsingUtils' 
        of the package 'BiblioParsing'.
        The function 'existing_corpuses' is imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The global 'ARCHI_YEAR' is imported from the module 'BM_PubGlobals' of the package 
        'BiblioMeter_FUNCTS'.

    """
    
    # Standard library imports
    import os
    import tkinter as tk
    from tkinter import messagebox
    
    # 3rd party imports
    import BiblioParsing as bp
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import save_fails_dict
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import save_parsing_dict
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_user_config
    
    # Internal functions    
    def _corpus_parsing(rawdata_path, parsing_path, database_type):
        if not os.path.exists(parsing_path): os.mkdir(parsing_path)
        parsing_dict, dic_failed = bp.biblio_parser(rawdata_path, database_type)
        save_parsing_dict(parsing_dict, parsing_path, 
                          item_filename_dict, parsing_save_extent)
        save_fails_dict(dic_failed, parsing_path)

        articles_number = dic_failed["number of article"]
        info_title      = "Information"
        info_text       = f"'Parsing' de '{database_type}' effectué pour l'année {corpus_year}."
        info_text      += f"\n\n  Nombre d'articles du corpus : {articles_number}"
        messagebox.showinfo(info_title, info_text)                       

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, corpus_year, pg.BDD_LIST)
    rawdata_path_dict, parsing_path_dict, item_filename_dict = config_tup[0], config_tup[1], config_tup[2]
    
    # Setting useful paths for database 'database_type'
    rawdata_path = rawdata_path_dict[database_type] 
    parsing_path = parsing_path_dict[database_type]
    
    # Setting parsing files extension for saving
    parsing_save_extent = pg.TSV_SAVE_EXTENT
    
    # Getting files status for corpus parsing
    files_status = existing_corpuses(bibliometer_path)    
    list_corpus_year = files_status[0]
    if database_type == 'wos':
        list_rawdata = files_status[1]
        list_parsing = files_status[2]
    elif database_type == 'scopus': 
        list_rawdata = files_status[3]
        list_parsing = files_status[4]
    else:
        warning_title = "Attention : Erreur type de BDD"
        warning_text  = f"Le type de BDD {database_type}"
        warning_text += f" n'est pas encore pris en compte."
        warning_text += f"\nLe 'parsing' correspondant ne peut être construit !"
        warning_text += f"\n\nModifiez le type de BDD sélectionné et relancez le 'parsing'."
        messagebox.showwarning(warning_title, warning_text)
        return
    rawdata_status = list_rawdata[list_corpus_year.index(corpus_year)]
    parsing_status = list_parsing[list_corpus_year.index(corpus_year)]
       
    # Asking for confirmation of corpus year to parse
    ask_title = "Confirmation de l'année de traitement"
    ask_text  = f"Une procédure de 'parsing' de '{database_type}' "
    ask_text += f"pour l'année {corpus_year} a été lancée."
    ask_text += f"\n\n Confirmer ce choix ?"
    answer_1  = messagebox.askokcancel(ask_title, ask_text)
    if answer_1:        
        if rawdata_status == False:
            warning_title = "Attention ! Fichier manquant"
            warning_text  = f"Le fichier brut d'extraction de '{database_type}' "
            warning_text += f"de l'année {corpus_year} n'est pas disponible."
            warning_text += f"\nLe 'parsing' correspondant ne peut être construit !"
            warning_text += f"\n\nAjoutez le fichier à l'emplacement attendu et relancez le 'parsing'."
            messagebox.showwarning(warning_title, warning_text)
            return
        else:
            if not os.path.exists(parsing_path):
                os.mkdir(parsing_path)

            if parsing_status == 1:
                # Ask to carry on with parsing if already done
                ask_title = "Confirmation de traitement"
                ask_text  = f"Le 'parsing' du corpus '{database_type}' "
                ask_text += f"de l'année {corpus_year} est déjà disponible."
                ask_text += f"\n\nReconstruire le 'parsing' ?"
                answer_2  = messagebox.askokcancel(ask_title, ask_text)
                if not answer_2:                                        
                    info_title = "Information"
                    info_text  = f"Le 'parsing' existant du corpus '{database_type}' "
                    info_text += f"de l'année {corpus_year} a été conservé."                   
                    messagebox.showinfo(info_title, info_text)
                    return
            
            # Parse when not parsed yet or ok for reconstructing parsing                      
            _corpus_parsing(rawdata_path, parsing_path, database_type)
    else:
        info_title = "Information"
        info_text  = f"Modifiez l'année sélectionnée et relancez le 'parsing'."                  
        messagebox.showinfo(info_title, info_text)
        return
    
    # update files status
    _update(self, bibliometer_path, pos_x, pos_y, esp_ligne)

    
def _launch_synthese(self, corpus_year, institute, org_tup, bibliometer_path,  
                     pos_x, pos_y, esp_ligne):
    """The internal function `_launch_synthese` concatenates the parsing 
    from wos or scopus databases using the function 'parsing_concatenate_deduplicate'.
    It tags the Institute authors using the function 'extend_author_institutions' 
    and using the global 'INSTITUTE_INST_LIST'.
    It checks if all useful files are available in the 'BiblioMeter_Files' folder 
    using the function 'existing_corpuses'.
    It saves the parsing files using paths set from the global 'ARCHI_YEAR'.
    It updates the files status using the function `_update` internal 
    to the module 'Page_ParsingConcat' of the package 'BiblioMeter_GUI'.
    
    Args:
        corpus_year (str): A string of 4 digits corresponding to the year of the corpus. 
        bibliometer_path (path): The full path for "BiblioMeter_Files" folder.
        pos_x (int): The x position to be used for widgets positionning 
                     by classes of module "Page_ParsingConcat.py".
        pos_y (int): The y position to be used for widgets positionning 
                     by classes of module "Page_ParsingConcat.py".
        esp_ligne (int): The space value for widgets spacing 
                         by classes of module "Page_ParsingConcat.py".
                         
    Returns:
        None.
        
    Note:
        The function 'parsing_concatenate_deduplicate' is imported from 
        the module 'BiblioParsingConcat' of the package 'BiblioParsing'.
        The function 'extend_author_institutions' is imported from 
        the module 'BiblioParsingUtils' of the package 'BiblioParsing'.
        The function 'existing_corpuses' is imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The globals 'ARCHI_YEAR' and 'INSTITUTE_INST_LIST' are imported from the module 
        'BM_PubGlobals' of the package 'BiblioMeter_FUNCTS'.

    """
    # Standard library imports
    import os
    from tkinter import messagebox

    # 3rd party imports
    import BiblioParsing as bp
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import read_parsing_dict
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import save_parsing_dict
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_user_config
       
    # Internal functions
    def _deduplicate_corpus_parsing():
        if not os.path.exists(concat_parsing_path): os.mkdir(concat_parsing_path)
        if not os.path.exists(dedup_parsing_path): os.mkdir(dedup_parsing_path)           
  
        scopus_parsing_dict = read_parsing_dict(scopus_parsing_path, item_filename_dict, 
                                                parsing_save_extent)
        wos_parsing_dict    = read_parsing_dict(wos_parsing_path, item_filename_dict, 
                                                parsing_save_extent)
        concat_parsing_dict = bp.concatenate_parsing(scopus_parsing_dict, wos_parsing_dict, 
                                                     inst_filter_list = institutions_filter_list)
        save_parsing_dict(concat_parsing_dict, concat_parsing_path, 
                          item_filename_dict, parsing_save_extent)
        dedup_parsing_dict  = bp.deduplicate_parsing(concat_parsing_dict)
        save_parsing_dict(dedup_parsing_dict, dedup_parsing_path, 
                          item_filename_dict, parsing_save_extent)
        
    # Setting institute parameters
    institutions_filter_list = org_tup[3]

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, corpus_year, pg.BDD_LIST)
    rawdata_path_dict, parsing_path_dict, item_filename_dict = config_tup[0], config_tup[1], config_tup[2]
    
    # Setting useful paths for database 'database_type'
    scopus_parsing_path = parsing_path_dict["scopus"] 
    wos_parsing_path    = parsing_path_dict["wos"] 
    concat_parsing_path = parsing_path_dict["concat"]
    dedup_parsing_path  = parsing_path_dict["dedup"]
    
    # Setting parsing files extension for saving
    parsing_save_extent = pg.TSV_SAVE_EXTENT
    
    # Getting files status for corpus concatenation and deduplication
    files_status = existing_corpuses(bibliometer_path)     
    list_corpus_year    = files_status[0]
    list_wos_parsing    = files_status[2]
    list_scopus_parsing = files_status[4]
    list_dedup          = files_status[5]
    
    wos_parsing_status    = list_wos_parsing[list_corpus_year.index(corpus_year)]
    scopus_parsing_status = list_scopus_parsing[list_corpus_year.index(corpus_year)]
    dedup_parsing_status  = list_dedup[list_corpus_year.index(corpus_year)]

    # Asking for confirmation of corpus year to concatenate and deduplicate
    ask_title = "Confirmation de l'année de traitement"
    ask_text  = f"La synthèse pour l'année {corpus_year} a été lancée."
    ask_text += f"\n\nConfirmer ce choix ?"
    answer_1 = messagebox.askokcancel(ask_title, ask_text)
    if answer_1: # Alors on lance la synthèse
        
        # Vérification de la présence des fichiers
        if not wos_parsing_status:
            warning_title = "Attention ! Fichiers manquants"
            warning_text  = f"Le 'parsing' de 'wos' "
            warning_text += f"de l'année {corpus_year} n'est pas disponible."
            warning_text += f"\nLa synthèse correspondante ne peut pas encore être construite !"
            warning_text += f"\n\n-1 Lancez le 'parsing' manquant;"
            warning_text += f"\n-2 Relancez la synthèse."
            messagebox.showwarning(warning_title, warning_text)
            return

        if not scopus_parsing_status:
            warning_title = "Attention ! Fichiers manquants"
            warning_text  = f"Le 'parsing' de 'scopus' "
            warning_text += f"de l'année {corpus_year} n'est pas disponible."
            warning_text += f"\nLa synthèse correspondante ne peut pas encore être construite !"
            warning_text += f"\n\n-1 Lancez le 'parsing' manquant;"
            warning_text += f"\n-2 Relancez la synthèse."
            messagebox.showwarning(warning_title, warning_text)
            return

        if dedup_parsing_status:
            # Ask to carry on with parsing if already done
            ask_title = "Reconstruction de la synthèse"
            ask_text  =  f"La synthèse pour l'année {corpus_year} est déjà disponible."
            ask_text += f"\n\nReconstruire la synthèse ?"
            answer_2 = messagebox.askokcancel(ask_title, ask_text)            
            if answer_2: # Alors on effectue la synthèse
                _deduplicate_corpus_parsing()
                info_title = "Information"
                info_text = f"La synthèse pour l'année {corpus_year} a été reconstruite."                   
                messagebox.showinfo(info_title, info_text)
            else:
                info_title = "Information"
                info_text = f"La synthèse dejà disponible est conservée."                   
                messagebox.showinfo(info_title, info_text)
        else:
            _deduplicate_corpus_parsing()            
            info_title = "Information"
            info_text = f"La construction de la synthèse pour l'année {corpus_year} est terminée."                   
            messagebox.showinfo(info_title, info_text)
                
    # update files status
    _update(self, bibliometer_path, pos_x, pos_y, esp_ligne)
    

def create_parsing_concat(self, master, institute, bibliometer_path):
    """ The function `create_parsing_concat` creates the first page of the application GUI 
    using internal functions  `_launch_parsing`, `_launch_synthese` and `_update`.
    It calls also the functions `_launch_parsing``and `_launch_synthese` internal 
    to the module 'Page_ParsingConcat' of the package 'BiblioMeter_GUI' through GUI buttons.

    Args:
        bibliometer_path (path): The path leading to the file folder 'BilioMeter_Files'.
        master (): ????
    
    Returns:
        
    Note:
        The function 'mm_to_px' is imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The functions 'existing_corpuses', 'font_size' and 'place_after' 
        are imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The globals BDD_LIST, FONT_NAME, PPI and TEXT_* are imported from the module 'GUI_Globals' 
        of the package 'BiblioMeter_GUI'.
    
    """

    # Standard library imports
    import os
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import font as tkFont    
    
    # Local imports
    import BiblioMeter_GUI.GUI_Globals as gg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_GUI.Page_Classes import app_main
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import font_size 
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_org_params  
    
    # Internal functions
    def _launch_exit():
        ask_title = 'Arrêt de BiblioMeter'
        ask_text =  "Après la fermeture des fenêtres, "
        ask_text += "les traitements effectués sont sauvegardés."
        ask_text += "\nLe traitement peut être repris ultérieurement."
        ask_text += "\nConfirmez la mise en pause ?"
        exit_answer = messagebox.askokcancel(ask_title, ask_text)
        if exit_answer:
            master.destroy()                    
                
    # Setting useful local variables for positions modification (globals to create ??)
    # numbers are reference values in mm for reference screen
    position_selon_x_check   = mm_to_px(70  * app_main.width_sf_mm,  gg.PPI)
    position_selon_y_check   = mm_to_px(40  * app_main.height_sf_mm, gg.PPI)  #40   
    espace_entre_ligne_check = mm_to_px(10  * app_main.height_sf_mm, gg.PPI)    
    labels_x_pos             = mm_to_px(10  * app_main.width_sf_mm,  gg.PPI)
    labels_y_space           = mm_to_px(10  * app_main.height_sf_mm, gg.PPI)
    status_label_y_pos       = mm_to_px(25  * app_main.height_sf_mm, gg.PPI)  #25      
    parsing_label_y_pos      = mm_to_px(107 * app_main.height_sf_mm, gg.PPI)  
    synthese_label_y_pos     = mm_to_px(135 * app_main.height_sf_mm, gg.PPI)                             
    status_button_x_pos      = mm_to_px(148 * app_main.width_sf_mm, gg.PPI)  #148       
    status_button_y_pos      = mm_to_px(98  * app_main.height_sf_mm, gg.PPI)  #98                         
    exit_button_x_pos        = mm_to_px(gg.REF_EXIT_BUT_POS_X_MM * app_main.width_sf_mm,  gg.PPI)  #193 
    exit_button_y_pos        = mm_to_px(gg.REF_EXIT_BUT_POS_Y_MM * app_main.height_sf_mm, gg.PPI)  #145
    dx_year_select           = mm_to_px(1   * app_main.width_sf_mm,  gg.PPI)
    dy_year_select           = mm_to_px(1   * app_main.height_sf_mm, gg.PPI)
    dx_bdd_select            = mm_to_px(12  * app_main.width_sf_mm,  gg.PPI)  #12
    dy_bdd_select            = mm_to_px(1   * app_main.height_sf_mm, gg.PPI)
    dx_launch                = mm_to_px(15  * app_main.width_sf_mm,  gg.PPI)  #15
    dy_launch                = mm_to_px(0.2 * app_main.height_sf_mm, gg.PPI)
    eff_labels_font_size     = font_size(14, app_main.width_sf_min)
    eff_select_font_size     = font_size(12, app_main.width_sf_min) 
    eff_buttons_font_size    = font_size(11, app_main.width_sf_min)
                
    year_x_pos = labels_x_pos           
    parsing_year_y_pos  = parsing_label_y_pos + labels_y_space
    synthese_year_y_pos = synthese_label_y_pos + labels_y_space
    
    # Getting files status for corpus concatenation and deduplication
    files_status = existing_corpuses(bibliometer_path)     
    list_corpus_year    = files_status[0]
    list_wos_rawdata    = files_status[1]     # unused here
    list_wos_parsing    = files_status[2]     # unused here
    list_scopus_rawdata = files_status[3]     # unused here
    list_scopus_parsing = files_status[4]     # unused here
    list_dedup          = files_status[5]     # unused here
    
    # Setting useful local variables for default selection items in selection lists 
    default_year = list_corpus_year[-1]    
    default_bdd  = pg.BDD_LIST[0]
    
    # Getting institute parameters
    org_tup = set_org_params(institute, bibliometer_path)
    
    ################### Zone Statut des fichiers de "parsing"
    # Liste des checkbox des corpuses
    self.CHECK = []
    self.TABLE = []

    font_statut = tkFont.Font(family = gg.FONT_NAME, 
                              size   = eff_labels_font_size,
                              weight = 'bold')
    label_statut = tk.Label(self, 
                            text = gg.TEXT_STATUT, 
                            font = font_statut)
    label_statut.place(x = labels_x_pos, 
                       y = status_label_y_pos, 
                       anchor = "nw")
    
    ################## Bouton pour actualiser la zone de stockage
    font_exist_button = tkFont.Font(family = gg.FONT_NAME, 
                                    size   = eff_buttons_font_size)
    exist_button = tk.Button(self, 
                             text = gg.TEXT_UPDATE_STATUS, 
                             font = font_exist_button, 
                             command = lambda: _update(self, 
                                                       bibliometer_path, 
                                                       position_selon_x_check, 
                                                       position_selon_y_check, 
                                                       espace_entre_ligne_check))
    exist_button.place(x = status_button_x_pos, 
                       y = status_button_y_pos, 
                       anchor = 'n')
    
    ################## Zone Construction des fichiers de "parsing" par BDD
    font_parsing = tkFont.Font(family = gg.FONT_NAME, 
                               size   = eff_labels_font_size,
                               weight = 'bold')
    label_parsing = tk.Label(self, 
                             text = gg.TEXT_PARSING, 
                             font = font_parsing)
    label_parsing.place(x = labels_x_pos, 
                        y = parsing_label_y_pos, anchor = "nw")

    # Choix de l'année
    font_year_pc_1 = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_select_font_size)
    self.label_year_pc_1 = tk.Label(self, 
                                    text = gg.TEXT_YEAR_PC, 
                                    font = font_year_pc_1)
    self.label_year_pc_1.place(x = year_x_pos, 
                               y = parsing_year_y_pos, 
                               anchor = "nw")
    
    self.var_year_pc_1 = tk.StringVar(self)
    self.var_year_pc_1.set(default_year)
    self.OM_year_pc_1 = tk.OptionMenu(self, 
                                      self.var_year_pc_1, 
                                      *list_corpus_year)
    font_year_pc_1 = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_buttons_font_size)
    self.OM_year_pc_1.config(font = font_year_pc_1)
    place_after(self.label_year_pc_1, 
                self.OM_year_pc_1, 
                dx = + dx_year_select,
                dy = - dy_year_select)
    
    # Choix de la BDD
    font_bdd_pc_1 = tkFont.Font(family = gg.FONT_NAME, 
                                size   = eff_select_font_size)
    label_bdd_pc_1 = tk.Label(self, 
                              text = gg.TEXT_BDD_PC, 
                              font = font_bdd_pc_1)
    place_after(self.OM_year_pc_1, 
                label_bdd_pc_1, 
                dx = dx_bdd_select, 
                dy = dy_bdd_select)
    
    var_bdd_pc_1 = tk.StringVar(self)
    var_bdd_pc_1.set(default_bdd)
    OM_bdd_pc_1 = tk.OptionMenu(self, 
                                var_bdd_pc_1, 
                                *pg.BDD_LIST)
    font_bdd_pc_1 = tkFont.Font(family = gg.FONT_NAME, 
                                size   = eff_buttons_font_size)
    OM_bdd_pc_1.config(font = font_bdd_pc_1)
    place_after(label_bdd_pc_1, 
                OM_bdd_pc_1, 
                dx = + dx_year_select,
                dy = - dy_year_select)
    
    # Lancement du parsing
    font_launch_parsing = tkFont.Font(family = gg.FONT_NAME, 
                                      size   = eff_buttons_font_size)
    button_launch_parsing = tk.Button(self, 
                                      text = gg.TEXT_LAUNCH_PARSING, 
                                      font = font_launch_parsing, 
                                      command = lambda: _launch_parsing(self, 
                                                                        self.var_year_pc_1.get(), 
                                                                        var_bdd_pc_1.get(),
                                                                        bibliometer_path,
                                                                        position_selon_x_check, 
                                                                        position_selon_y_check, 
                                                                        espace_entre_ligne_check))
    place_after(OM_bdd_pc_1, 
                button_launch_parsing, 
                dx = dx_launch,
                dy = dy_launch)
    
    ################## Zone Synthèse des fichiers de parsing de toutes les BDD
    font_synthese = tkFont.Font(family = gg.FONT_NAME, 
                                size   = eff_labels_font_size,
                                weight = 'bold')
    label_synthese = tk.Label(self, 
                              text = gg.TEXT_SYNTHESE, 
                              font = font_synthese)
    label_synthese.place(x = labels_x_pos, 
                         y = synthese_label_y_pos,
                         anchor = "nw")
    
    # Choix de l'année
    font_year_pc_2 = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_select_font_size)
    self.label_year_pc_2 = tk.Label(self, 
                                    text = gg.TEXT_YEAR_PC, 
                                    font = font_year_pc_2)
    self.label_year_pc_2.place(x = year_x_pos, 
                               y = synthese_year_y_pos,
                               anchor = "nw")
    
    self.var_year_pc_2 = tk.StringVar(self)
    self.var_year_pc_2.set(list_corpus_year[-1])
    self.OM_year_pc_2 = tk.OptionMenu(self, 
                                      self.var_year_pc_2, 
                                      *list_corpus_year)
    font_year_pc_2 = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_buttons_font_size)
    self.OM_year_pc_2.config(font = font_year_pc_2)
    place_after(self.label_year_pc_2, 
                self.OM_year_pc_2, 
                dx = + dx_year_select, 
                dy = - dy_year_select)
        
    # Lancement de la synthèse
    font_launch_synthese = tkFont.Font(family = gg.FONT_NAME, 
                                       size   = eff_buttons_font_size)
    button_launch_synthese = tk.Button(self, 
                                     text = gg.TEXT_LAUNCH_SYNTHESE, 
                                     font = font_launch_synthese, 
                                     command = lambda: _launch_synthese(self, 
                                                                        self.var_year_pc_2.get(),
                                                                        institute, org_tup, 
                                                                        bibliometer_path, 
                                                                        position_selon_x_check, 
                                                                        position_selon_y_check, 
                                                                        espace_entre_ligne_check))
    place_after(self.OM_year_pc_2, 
                button_launch_synthese, 
                dx = dx_launch,
                dy = dy_launch)

    ################## Placement de CHECKBOXCORPUSES :
    _update(self, bibliometer_path, position_selon_x_check, position_selon_y_check, 
            espace_entre_ligne_check)
    
    ################## Bouton pour sortir de la page
    font_button_quit = tkFont.Font(family = gg.FONT_NAME, 
                                   size   = eff_buttons_font_size)
    button_quit = tk.Button(self, 
                            text = gg.TEXT_PAUSE, 
                            font = font_button_quit, 
                            command = lambda: _launch_exit()).place(x = exit_button_x_pos, 
                                                                    y = exit_button_y_pos, 
                                                                    anchor = 'n')