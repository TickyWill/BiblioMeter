__all__ = ['create_ParsingConcat']

    
def _create_table(self, bibliometer_path, pos_x_init):    
    """The internal function `_create_table` creates the column names of the table used by 'Page_ParsingConcat.py'
    to display which files of the parsing treatment are available in the folder 'BiblioMeter_Files'. 
    The full path of this folder is given by the argument 'bibliometer_path'.
    The positions of the table items in the gui window 'root' are set using the argument 'pos_x_init',  
    and the returns of the function 'root_properties'.
    
    Args:
        bibliometer_path (path): The files root path for "BiblioMeter_Files" folder.
        pos_x_init (int): The initial horizontal position in pixels to be used for widgets 
                          positionning by classes of module "Page_ParsingConcat.py".
                         
    Returns:
        None.
        
    Note:
        The function 'root_propertier' is imported from the module 'Coordinates' 
        of the package 'BiblioMeter_GUI'.
        The functions 'font_size' and 'mm_to_px' are imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The global 'FONT_NAME' is imported from the module 'Coordinates' 
        of the package 'BiblioMeter_GUI'.
        The global 'PPI' is imported from the module 'Globals_GUI' of the package 
        'BiblioMeter_GUI'.

    """
    
    # 3rd party imports
    import tkinter as tk
    from tkinter import font as tkFont    
    
    # Local imports    
    from BiblioMeter_GUI.Coordinates import root_properties
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px    
    
    from BiblioMeter_GUI.Coordinates import FONT_NAME
    from BiblioMeter_GUI.Globals_GUI import PPI  
    
    # Internal function
    def _set_table_item(item_text, item_pos_x):
        item_case = tk.Label(self, 
                       text = item_text, 
                       font = header_font)
        item_case.place(x = item_pos_x, y = pos_y_ref, anchor = 'center')
        self.TABLE.append(item_case)
    
    # Getting useful window sizes and scale factors depending on displays properties
    sizes_tuple   = root_properties(self)
    win_width_px  = sizes_tuple[0]    # unused here
    win_height_px = sizes_tuple[1]    # unused here
    width_sf_px   = sizes_tuple[2] 
    height_sf_px  = sizes_tuple[3]    # unused here
    width_sf_mm   = sizes_tuple[4]
    height_sf_mm  = sizes_tuple[5]    # unused here
    width_sf_min  = min(width_sf_mm, width_sf_px)     # ! check why using min(width_sf_mm, width_sf_px)
    
    # Setting specific font properties
    ref_font_size = 11
    local_font_size = font_size(ref_font_size, width_sf_min)    
    header_font = tkFont.Font(family = FONT_NAME, 
                              size = local_font_size)
    
    # Setting useful x position shift and y position reference in pixels    
    pos_x_shift = mm_to_px(25 * width_sf_mm, PPI)                                 
    pos_y_ref = mm_to_px(35 * height_sf_mm, PPI) 
    
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
        nothing
        
    Note:
        The function 'root_properties' is imported from the module 'Coordinates' 
        of the package 'BiblioMeter_GUI'.
        The functions 'existing_corpuses', 'font_size', 'mm_to_px' and 'place_after'
        are imported from the module 'Useful_Functions' of the package 'BiblioMeter_GUI'.
        The class 'CheckBoxCorpuses' is imported from the module 'Useful_Classes' 
        of the package 'BiblioMeter_GUI'. 
        The globals ARCHI_YEAR and PPI are imported from the module 'Globals_GUI' 
        of the package 'BiblioMeter_GUI'.
        The global FONT_NAME is imported from the module 'Coordinates' 
        of the package 'BiblioMeter_GUI'.
    
    
    '''
    
    # 3rd party imports
    import tkinter as tk
    from tkinter import font as tkFont
    
    # Local imports        
    from BiblioMeter_GUI.Coordinates import root_properties
    
    from BiblioMeter_GUI.Useful_Classes import CheckBoxCorpuses
    
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    
    from BiblioMeter_GUI.Coordinates import FONT_NAME
    
    from BiblioMeter_GUI.Globals_GUI import ARCHI_YEAR
    from BiblioMeter_GUI.Globals_GUI import PPI
    
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
    eff_font_size = font_size(11, width_sf_min)
    eff_dx        = mm_to_px(1 * width_sf_mm,  PPI)
    eff_dy        = mm_to_px(1 * height_sf_mm, PPI)

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
    font_year_pc_1 = tkFont.Font(family = FONT_NAME, 
                                 size = eff_font_size)
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
    font_year_pc_2 = tkFont.Font(family = FONT_NAME, 
                                 size = eff_font_size)
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
        of the package 'BiblioAnalysis_Utils'.
        The function 'existing_corpuses' is imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The global 'PARSING_PERF' is imported from the module 'BiblioSpecificGlobals' 
        of the package 'BiblioAnalysis_Utils'.
        The global 'ARCHI_YEAR' is imported from the module 'Globals_GUI' of the package 
        'BiblioMeter_GUI'.

    """
    
    # Standard library imports
    import os
    import json
    from pathlib import Path
    
    # 3rd party imports
    import tkinter as tk
    from tkinter import messagebox
    
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import biblio_parser
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import PARSING_PERF
    
    # Local imports
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses   
    from BiblioMeter_GUI.Globals_GUI import ARCHI_YEAR
    
    # Internal functions    
    def _corpus_parsing(rawdata_path, parsing_path, database_type, failed_json_path, expert):        
        biblio_parser(rawdata_path, parsing_path, database_type, expert) 
        with open(failed_json_path, 'r') as failed_json:
            data_failed = failed_json.read()
        dic_failed      = json.loads(data_failed)
        articles_number = dic_failed["number of article"]
        info_title      = 'Information'
        info_text       = f"""'Parsing' effectué."""
        info_text      += f"""\nNombre d'articles du corpus : {articles_number}"""
        messagebox.showinfo(info_title, info_text)
        
    # Setting variables for functions imported from BiblioAnalysis_Utils package
    expert = False   # for call of biblio_parser                        

    # Creating useful aliases from imported global ARCHI_YEAR 
    corpus_folder_alias   = ARCHI_YEAR["corpus"]
    database_folder_alias = ARCHI_YEAR[database_type]
    rawdata_folder_alias  = ARCHI_YEAR['rawdata']
    parsing_folder_alias  = ARCHI_YEAR['parsing'] 
       
    # Setting useful paths
    root_folder_path = bibliometer_path / Path(corpus_year) / Path(corpus_folder_alias) / Path(database_folder_alias)
    rawdata_path     = root_folder_path / Path(rawdata_folder_alias) 
    parsing_path     = root_folder_path / Path(parsing_folder_alias)
    failed_json_path = parsing_path / Path(PARSING_PERF)
    
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
        warning_title = 'Attention : Erreur type de BDD'
        warning_text  = f"""Le type de BDD {database_type}"""
        warning_text += f""" n'est pas encore pris en compte."""
        warning_text += f"""\nLe 'parsing' correspondant ne peut être construit !"""
        warning_text += f"""\nModifiez le type de BDD sélectionné et relancez le 'parsing'."""
        messagebox.showwarning(warning_title, warning_text)
        return
    rawdata_status = list_rawdata[list_corpus_year.index(corpus_year)]
    parsing_status = list_parsing[list_corpus_year.index(corpus_year)]
       
    # Asking for confirmation of corpus year to parse
    ask_title = """Confirmation de l'année de traitement"""
    ask_text  = f"""Une procédure de 'parsing' pour l'année {corpus_year} a été lancée."""
    ask_text += f"""\nConfirmer ce choix ?"""
    answer_1  = messagebox.askokcancel(ask_title, ask_text)
    if answer_1:        
        if rawdata_status == False:
            warning_title = 'Attention ! Fichier manquant'
            warning_text  = f"""Le fichier brut d'extraction de {database_type}"""
            warning_text += f""" de l'année {corpus_year} n'est pas disponible. """
            warning_text += f"""\nLe 'parsing' correspondant ne peut être construit !"""
            warning_text += f"""\nAjoutez le fichier à l'emplacement attendu et relancez le 'parsing'."""
            messagebox.showwarning(warning_title, warning_text)
            return
        else:
            if not os.path.exists(parsing_path):
                os.mkdir(parsing_path)

            if parsing_status == 1:
                # Ask to carry on with parsing if already done
                ask_title = 'Confirmation de traitement'
                ask_text  =  f"""Le 'parsing' pour le corpus {database_type} """
                ask_text += f"""de l'année {corpus_year} est déjà disponible."""
                ask_text += f"""\nReconstruire le 'parsing' ?"""
                answer_2  = messagebox.askokcancel(ask_title, ask_text)
                if not answer_2:                                        
                    info_title = 'Information'
                    info_text  = f"""Le 'parsing' existant a été conservé."""                   
                    messagebox.showinfo(info_title, info_text)
                    return
            
            # Parse when not parsed yet or ok for reconstructing parsing                      
            _corpus_parsing(rawdata_path, parsing_path, database_type, failed_json_path, expert)
    else:
        info_title = 'Information'
        info_text  = f"""Modifiez l'année sélectionnée et relancez le 'parsing'."""                   
        messagebox.showinfo(info_title, info_text)
        return
    
    # update files status
    _update(self, bibliometer_path, pos_x, pos_y, esp_ligne)

    
def _launch_synthese(self, corpus_year, bibliometer_path, pos_x, pos_y, esp_ligne):
    """The internal function `_launch_synthese` concatenates the parsing 
    from wos or scopus databases using the function 'parsing_concatenate_deduplicate'.
    It tags the LITEN authors using the function 'extend_author_institutions' 
    and using the global 'LITEN_INST_LIST'.
    It checks if all useful files are available in the 'BiblioMeter_Files' folder 
    using the function 'existing_corpuses'.
    It saves the parsing files using paths set from the global 'ARCHI_YEAR'.
    It displays the number of articles parsed using the file path set using 
    the global 'PARSING_PERF'.
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
        the module 'BiblioParsingConcat' of the package 'BiblioAnalysis_Utils'.
        The function 'extend_author_institutions' is imported from 
        the module 'BiblioParsingUtils' of the package 'BiblioAnalysis_Utils'.
        The function 'existing_corpuses' is imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The global 'PARSING_PERF' is imported from the module 'BiblioSpecificGlobals' 
        of the package 'BiblioAnalysis_Utils'.
        The global 'LITEN_INST_LIST' is imported from the module 'BiblioMeterGlobalsVariables' 
        of the package 'BiblioMeter_FUNCTS'.
        The global 'ARCHI_YEAR' is imported from the module 'Globals_GUI' of the package 
        'BiblioMeter_GUI'.

    """
    # Standard library imports
    import os
    from pathlib import Path

    # 3rd party imports
    from tkinter import messagebox

    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioParsingConcat import parsing_concatenate_deduplicate
    from BiblioAnalysis_Utils.BiblioParsingUtils import extend_author_institutions
    
    # BiblioMeter_FUNCTS package imports
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import LITEN_INST_LIST
    
    # Local imports
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Globals_GUI import ARCHI_YEAR
    
    # Internal functions
    def _rationalize_corpus_parsing():
        if not os.path.exists(concat_parsing_path):
            if not os.path.exists(concat_path): os.mkdir(concat_path)
            os.mkdir(concat_parsing_path)

        if not os.path.exists(rational_parsing_path):
            if not os.path.exists(rational_path): os.mkdir(rational_path)
            os.mkdir(rational_parsing_path)
  
        parsing_concatenate_deduplicate(useful_path_list)
        extend_author_institutions(rational_parsing_path, 
                                   LITEN_INST_LIST)         
        
    # Creating useful aliases from imported global ARCHI_YEAR 
    corpus_folder_alias  = ARCHI_YEAR["corpus"]
    scopus_folder_alias  = ARCHI_YEAR["scopus"]
    wos_folder_alias     = ARCHI_YEAR["wos"]
    parsing_folder_alias = ARCHI_YEAR['parsing'] 
    concat_folder_alias  = ARCHI_YEAR['concat']
    dedup_folder_alias   = ARCHI_YEAR['dedup']
    
    # Setting useful paths
    root_folder_path = bibliometer_path / Path(corpus_year) / Path(corpus_folder_alias)
    
    scopus_parsing_path   = root_folder_path / Path(scopus_folder_alias) / Path(parsing_folder_alias) 
    wos_parsing_path      = root_folder_path / Path(wos_folder_alias) / Path(parsing_folder_alias)
    concat_path           = root_folder_path / Path(concat_folder_alias)
    concat_parsing_path   = concat_path / Path(parsing_folder_alias)
    rational_path         = root_folder_path / Path(dedup_folder_alias)
    rational_parsing_path = rational_path / Path(parsing_folder_alias)
    
    useful_path_list = [scopus_parsing_path, 
                        wos_parsing_path, 
                        concat_parsing_path, 
                        rational_parsing_path]
    
    # Getting files status for corpus concatenation and deduplication
    files_status = existing_corpuses(bibliometer_path)     
    list_corpus_year = files_status[0]
    list_wos_parsing = files_status[2]
    list_scopus_parsing = files_status[4]
    list_rational = files_status[5]
    
    wos_parsing_status = list_wos_parsing[list_corpus_year.index(corpus_year)]
    scopus_parsing_status = list_scopus_parsing[list_corpus_year.index(corpus_year)]
    rational_parsing_status = list_rational[list_corpus_year.index(corpus_year)]

    # Asking for confirmation of corpus year to concatenate and deduplicate
    ask_title = """Confirmation de l'année de traitement"""
    ask_text = f"""la synthèse pour l'année {corpus_year} a été lancée."""
    ask_text += f"""\nConfirmer ce choix ?"""
    answer_1 = messagebox.askokcancel(ask_title, ask_text)
    if answer_1: # Alors on lance la synthèse
        
        # Vérification de la présence des fichiers
        if not wos_parsing_status:
            warning_title = 'Attention ! Fichiers manquants'
            warning_text = f"""Le 'parsing' de 'wos' """
            warning_text += f"""de l'année {corpus_year} n'est pas disponible. """
            warning_text += f"""\nLa synthèse correspondante ne peut pas encore être construite !"""
            messagebox.showwarning(warning_title, warning_text)
            return

        if not scopus_parsing_status:
            warning_title = 'Attention ! Fichiers manquants'
            warning_text = f"""Le 'parsing' de 'scopus' """
            warning_text += f"""de l'année {corpus_year} n'est pas disponible. """
            warning_text += f"""\nLa synthèse correspondante ne peut pas encore être construite !"""
            messagebox.showwarning(warning_title, warning_text)
            return

        if rational_parsing_status:
            # Ask to carry on with parsing if already done
            ask_title = 'Reconstruction de la synthèse'
            ask_text =  f"""La synthèse pour l'année {corpus_year} est déjà disponible."""
            ask_text += f"""\nReconstruire la synthèse ?"""
            answer_2 = messagebox.askokcancel(ask_title, ask_text)            
            if answer_2: # Alors on effectue la synthèse
                _rationalize_corpus_parsing()
                info_title = 'Information'
                info_text = f"""La synthèse pour l'année {corpus_year} a été reconstruite."""                   
                messagebox.showinfo(info_title, info_text)
            else:
                info_title = 'Information'
                info_text = f"""La synthèse dejà disponible est conservée."""                   
                messagebox.showinfo(info_title, info_text)
        else:
            _rationalize_corpus_parsing()            
            info_title = 'Information'
            info_text = f"""La construction de la synthèse pour l'année {corpus_year} est terminée."""                   
            messagebox.showinfo(info_title, info_text)
                
    # update files status
    _update(self, bibliometer_path, pos_x, pos_y, esp_ligne)
    

def create_ParsingConcat(self, bibliometer_path, parent):
    """ The function `create_ParsingConcat` creates the first page of the application GUI 
    using internal functions  `_launch_parsing`, `_launch_synthese` and `_update`.
    It calls also the functions `_launch_parsing``and `_launch_synthese` internal 
    to the module 'Page_ParsingConcat' of the package 'BiblioMeter_GUI' through GUI buttons.

    Args:
        bibliometer_path (path): The path leading to the file folder 'BilioMeter_Files'.
        parent (): ????
    
    Returns:
        None.
        
    Note:
        The function 'root_properties' is imported from the module 'Coordinates' 
        of the package 'BiblioMeter_GUI'.
        The functions 'existing_corpuses', 'five_last_available_years', 'font_size', 'mm_to_px', 
        'place_after' and 'str_size_mm' are imported from the module 'Useful_Functions' 
        of the package 'BiblioMeter_GUI'.
        The globals ARCHI_YEAR, BDD_LIST and PPI are imported from the module 'Globals_GUI' 
        of the package 'BiblioMeter_GUI'.
        The global FONT_NAME and TEXT_* are imported from the module 'Coordinates' 
        of the package 'BiblioMeter_GUI'.
    
    """

    # Standard library imports
    import os
    from pathlib import Path

    # 3rd party imports
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import font as tkFont
    
    # Local imports
    from BiblioMeter_GUI.Coordinates import root_properties
    
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import str_size_mm
    
    from BiblioMeter_GUI.Coordinates import FONT_NAME
    from BiblioMeter_GUI.Coordinates import TEXT_BDD_PC
    from BiblioMeter_GUI.Coordinates import TEXT_LAUNCH_PARSING
    from BiblioMeter_GUI.Coordinates import TEXT_LAUNCH_SYNTHESE
    from BiblioMeter_GUI.Coordinates import TEXT_PARSING
    from BiblioMeter_GUI.Coordinates import TEXT_PAUSE
    from BiblioMeter_GUI.Coordinates import TEXT_STATUT
    from BiblioMeter_GUI.Coordinates import TEXT_SYNTHESE    
    from BiblioMeter_GUI.Coordinates import TEXT_UPDATE_STATUS        
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PC
        
    from BiblioMeter_GUI.Globals_GUI import ARCHI_YEAR
    from BiblioMeter_GUI.Globals_GUI import BDD_LIST
    from BiblioMeter_GUI.Globals_GUI import PPI
    
    # Defining internal functions
    def _launch_exit():
        ask_title = 'Arrêt de BiblioMeter'
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
    # numbers  are reference values in mm for reference screen
    position_selon_x_check   = mm_to_px(70  * width_sf_mm,  PPI)
    position_selon_y_check   = mm_to_px(45  * height_sf_mm, PPI)
    espace_entre_ligne_check = mm_to_px(10  * height_sf_mm, PPI)    
    labels_x_pos             = mm_to_px(10  * width_sf_mm,  PPI)
    labels_y_space           = mm_to_px(10  * height_sf_mm, PPI)
    status_label_y_pos       = mm_to_px(30  * height_sf_mm, PPI)  
    parsing_label_y_pos      = mm_to_px(107 * height_sf_mm, PPI)  #102
    synthese_label_y_pos     = mm_to_px(135 * height_sf_mm, PPI)  #130                           
    status_button_x_pos      = mm_to_px(40  * width_sf_mm,  PPI)       
    status_button_y_pos      = mm_to_px(92  * height_sf_mm, PPI)
    exit_button_x_pos        = mm_to_px(193 * width_sf_mm,  PPI) 
    exit_button_y_pos        = mm_to_px(145 * height_sf_mm, PPI)
    dx_year_select           = mm_to_px(1   * width_sf_mm,  PPI)
    dy_year_select           = mm_to_px(1   * height_sf_mm, PPI)
    dx_bdd_select            = mm_to_px(12  * width_sf_mm,  PPI)    #15
    dy_bdd_select            = mm_to_px(1   * height_sf_mm, PPI)
    dx_launch                = mm_to_px(15  * width_sf_mm,  PPI)    #20
    dy_launch                = mm_to_px(0.2 * height_sf_mm, PPI)
    eff_labels_font_size     = font_size(14, width_sf_min)
    eff_select_font_size     = font_size(12, width_sf_min) 
    eff_buttons_font_size    = font_size(11, width_sf_min)

                
    year_x_pos = labels_x_pos           
    parsing_year_y_pos =  parsing_label_y_pos + labels_y_space
    synthese_year_y_pos  =  synthese_label_y_pos + labels_y_space
    
    # Getting files status for corpus concatenation and deduplication
    files_status = existing_corpuses(bibliometer_path)     
    list_corpus_year    = files_status[0]
    list_wos_rawdata    = files_status[1]     # unused here
    list_wos_parsing    = files_status[2]     # unused here
    list_scopus_rawdata = files_status[3]     # unused here
    list_scopus_parsing = files_status[4]     # unused here
    list_rational       = files_status[5]     # unused here
    
    # Setting useful local variables for default selection items in selection lists 
    default_year = list_corpus_year[-1]    
    default_bdd  = BDD_LIST[0]
    
    ################### Zone Statut des fichiers de "parsing"
    # Liste des checkbox des corpuses
    self.CHECK = []
    self.TABLE = []

    font_statut = tkFont.Font(family = FONT_NAME, 
                              size   = eff_labels_font_size,
                              weight = 'bold')
    label_statut = tk.Label(self, 
                            text = TEXT_STATUT, 
                            font = font_statut)
    label_statut.place(x = labels_x_pos, 
                       y = status_label_y_pos, 
                       anchor = "nw")
    
    ################## Bouton pour actualiser la zone de stockage
    font_exist_button = tkFont.Font(family = FONT_NAME, 
                                    size = eff_buttons_font_size)
    exist_button = tk.Button(self, 
                             text = TEXT_UPDATE_STATUS, 
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
    font_parsing = tkFont.Font(family = FONT_NAME, 
                               size   = eff_labels_font_size,
                               weight = 'bold')
    label_parsing = tk.Label(self, 
                             text = TEXT_PARSING, 
                             font = font_parsing)
    label_parsing.place(x = labels_x_pos, 
                        y = parsing_label_y_pos, anchor = "nw")

    # Choix de l'année
    font_year_pc_1 = tkFont.Font(family = FONT_NAME, 
                                 size = eff_select_font_size)
    self.label_year_pc_1 = tk.Label(self, 
                                    text = TEXT_YEAR_PC, 
                                    font = font_year_pc_1)
    self.label_year_pc_1.place(x = year_x_pos, 
                               y = parsing_year_y_pos, 
                               anchor = "nw")
    
    self.var_year_pc_1 = tk.StringVar(self)
    self.var_year_pc_1.set(default_year)
    self.OM_year_pc_1 = tk.OptionMenu(self, 
                                      self.var_year_pc_1, 
                                      *list_corpus_year)
    font_year_pc_1 = tkFont.Font(family = FONT_NAME, 
                                 size = eff_buttons_font_size)
    self.OM_year_pc_1.config(font = font_year_pc_1)
    place_after(self.label_year_pc_1, 
                self.OM_year_pc_1, 
                dx = + dx_year_select,
                dy = - dy_year_select)
    
    # Choix de la BDD
    font_bdd_pc_1 = tkFont.Font(family = FONT_NAME, 
                                size = eff_select_font_size)
    label_bdd_pc_1 = tk.Label(self, 
                              text = TEXT_BDD_PC, 
                              font = font_bdd_pc_1)
    place_after(self.OM_year_pc_1, 
                label_bdd_pc_1, 
                dx = dx_bdd_select, 
                dy = dy_bdd_select)
    
    var_bdd_pc_1 = tk.StringVar(self)
    var_bdd_pc_1.set(default_bdd)
    OM_bdd_pc_1 = tk.OptionMenu(self, 
                                var_bdd_pc_1, 
                                *BDD_LIST)
    font_bdd_pc_1 = tkFont.Font(family = FONT_NAME, 
                                size = eff_buttons_font_size)
    OM_bdd_pc_1.config(font = font_bdd_pc_1)
    place_after(label_bdd_pc_1, 
                OM_bdd_pc_1, 
                dx = + dx_year_select,
                dy = - dy_year_select)
    
    # Lancement du parsing
    font_launch_parsing = tkFont.Font(family = FONT_NAME, 
                                      size = eff_buttons_font_size)
    button_launch_parsing = tk.Button(self, 
                                      text = TEXT_LAUNCH_PARSING, 
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
    font_synthese = tkFont.Font(family = FONT_NAME, 
                                size   = eff_labels_font_size,
                                weight = 'bold')
    label_synthese = tk.Label(self, 
                              text = TEXT_SYNTHESE, 
                              font = font_synthese)
    label_synthese.place(x = labels_x_pos, 
                         y = synthese_label_y_pos,
                         anchor = "nw")
    
    # Choix de l'année
    font_year_pc_2 = tkFont.Font(family = FONT_NAME, 
                                 size = eff_select_font_size)
    self.label_year_pc_2 = tk.Label(self, 
                                    text = TEXT_YEAR_PC, 
                                    font = font_year_pc_2)
    self.label_year_pc_2.place(x = year_x_pos, 
                               y = synthese_year_y_pos,
                               anchor = "nw")
    
    self.var_year_pc_2 = tk.StringVar(self)
    self.var_year_pc_2.set(list_corpus_year[-1])
    self.OM_year_pc_2 = tk.OptionMenu(self, 
                                      self.var_year_pc_2, 
                                      *list_corpus_year)
    font_year_pc_2 = tkFont.Font(family = FONT_NAME, 
                                 size = eff_buttons_font_size)
    self.OM_year_pc_2.config(font = font_year_pc_2)
    place_after(self.label_year_pc_2, 
                self.OM_year_pc_2, 
                dx = + dx_year_select, 
                dy = - dy_year_select)
        
    # Lancement de la synthèse
    font_launch_synthese = tkFont.Font(family = FONT_NAME, 
                                     size = eff_buttons_font_size)
    button_launch_synthese = tk.Button(self, 
                                     text = TEXT_LAUNCH_SYNTHESE, 
                                     font = font_launch_synthese, 
                                     command = lambda: _launch_synthese(self, 
                                                                        self.var_year_pc_2.get(),
                                                                        bibliometer_path,
                                                                        position_selon_x_check, 
                                                                        position_selon_y_check, 
                                                                        espace_entre_ligne_check))
    place_after(self.OM_year_pc_2, 
                button_launch_synthese, 
                dx = dx_launch,
                dy = dy_launch)

    ################## Placement de CHECKBOXCORPUSES :
    _update(self, bibliometer_path, position_selon_x_check, position_selon_y_check, espace_entre_ligne_check)
    
    ################## Bouton pour sortir de la page
    font_button_quit = tkFont.Font(family = FONT_NAME, 
                                   size = eff_buttons_font_size)
    button_quit = tk.Button(self, 
                            text = TEXT_PAUSE, 
                            font = font_button_quit, 
                            command = lambda: _launch_exit()).place(x = exit_button_x_pos, 
                                                                    y = exit_button_y_pos, 
                                                                    anchor = 'n')