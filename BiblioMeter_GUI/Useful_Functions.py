__all__ = ['existing_corpuses',
           'encadre_RL', 
           'encadre_UD', 
           'font_size',
           'general_properties',
           'last_available_years',
           'mm_to_px',
           'place_after', 
           'place_bellow', 
           'place_bellow_LabelEntry',
           'str_size_mm',
           'show_frame',
          ]

def show_frame(self, page_name):        
    '''Show a frame for the given page name'''
    frame = self.frames[page_name]
    frame.tkraise()
    

def last_available_years(bibliometer_path, year_number):
    
    '''
    Returns a list of the available five last available years where corpuses are stored
    '''
        
    # Standard library imports
    import os
    from tkinter import messagebox
    
    # Récupérer les corpus disponibles TO DO : consolider le choix des années
    try:
        list_dir = os.listdir(bibliometer_path)
        years_full_list = list()
        for year in list_dir:
            if len(year) == 4:
                years_full_list.append(year)
        years_list = years_full_list[-year_number:]
    except FileNotFoundError:
        warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
        warning_text  = f"L'accès au dossier {bibliometer_path} est impossible."
        warning_text += f"\nChoisissez un autre dossier de travail."                       
        messagebox.showwarning(warning_title, warning_text)
        years_list = []
    return years_list


def existing_corpuses(bibliometer_path, corpuses_number = None):
    """ 
    Description: Returns a list of list of booleans displaying True 
    if rawdata and parsing results are available, and False if they are not 
    this for each of the available year folder.
    ex: 
    If only 2023 files are not present, the returned list of lists is the following: 
    [[2018, 2019, 2020, 2021, 2022, 2023],   #Years
     [True,True,True,True,True,False],       #Wos Rawdata
     [True,True,True,True,True,False],       #Scopus Rawdata
     [True,True,True,True,True,False],       #Wos Parsing
     [True,True,True,True,True,False],       #Scopus Parsing
     [True,True,True,True,True,False]]       #Concatenation & Deduplication.

    Args : 
        bibliometer_path (path):  The working folder path.
        corpuses_number (int): The number of corpuses to be checked 
        (default: CORPUSES_NUMBER global)

    Returns : 
        (list of lists)

    """

    # Standard library imports
    import os
    from pathlib import Path
    
    # 3rd party imports
    import BiblioParsing as bp
    
    # Local imports 
    import BiblioMeter_GUI.GUI_Globals as gg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_GUI.Useful_Functions import last_available_years
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_user_config
    
    # internal functions
    def _get_rawdata_file_path(rawdata_path, rawdata_extent):
        '''Returns the name of the rawdata file with 'rawdata_extent' extention 
        pointed by the full path 'rawdata_path'.
        '''
        # Standard library imports
        import os
        from pathlib import Path

        filenames_list = []
        for _, _, files in os.walk(rawdata_path): 
            filenames_list.extend(file for file in files if file.endswith("." + rawdata_extent)) 

        if filenames_list == []:
            return Path(f'{database_type} rawdata file not Found')
        else:
            return rawdata_path / Path(filenames_list[0])
    
    
    def _get_parsing_file_paths(parsing_path):
        '''.
        '''
        file_name = articles_item_alias + "." + parsing_save_extent
        parsing_file_path = parsing_path / Path(file_name)
        
        return parsing_file_path
    
    # Getting the last available corpus years
    if not corpuses_number: corpuses_number = gg.CORPUSES_NUMBER    
    years_folder_list = last_available_years(bibliometer_path, corpuses_number)
    
    # Setting the files type of raw data and saved parsing results
    parsing_save_extent   = pg.TSV_SAVE_EXTENT
    wos_rawdata_extent    = bp.WOS_RAWDATA_EXTENT
    scopus_rawdata_extent = bp.SCOPUS_RAWDATA_EXTENT
    
    # Setting articles item alias for checking availability of parsing
    articles_item_alias = bp.PARSING_ITEMS_LIST[0]
    
    # Initialization of lists    
    years_list          = list()
    wos_rawdata_list    = list()
    wos_parsing_list    = list()
    scopus_rawdata_list = list()
    scopus_parsing_list = list()
    dedup_parsing_list  = list()

    for year in years_folder_list:
        
        # Getting the full paths of the working folder architecture for the corpus "year"
        config_tup = set_user_config(bibliometer_path, year, pg.BDD_LIST)
        rawdata_path_dict, parsing_path_dict = config_tup[0], config_tup[1]
        
        # Setting useful paths for database 'database_type'
        scopus_rawdata_path = rawdata_path_dict["scopus"] 
        wos_rawdata_path    = rawdata_path_dict["wos"] 
        scopus_parsing_path = parsing_path_dict["scopus"] 
        wos_parsing_path    = parsing_path_dict["wos"]
        dedup_parsing_path  = parsing_path_dict["dedup"]
        
        year_folder_path = bibliometer_path / Path(year) 
        years_list.append(year)
        
        # Wos
        database_type = bp.WOS
        wos_rawdata_file_path     = _get_rawdata_file_path(wos_rawdata_path, wos_rawdata_extent)
        wos_parsing_articles_path = _get_parsing_file_paths(wos_parsing_path)
        wos_rawdata_list.append(wos_rawdata_file_path.is_file())
        wos_parsing_list.append(wos_parsing_articles_path.is_file())
        
        # Scopus
        database_type = bp.SCOPUS
        scopus_rawdata_file_path     = _get_rawdata_file_path(scopus_rawdata_path, scopus_rawdata_extent)
        scopus_parsing_articles_path = _get_parsing_file_paths(scopus_parsing_path)
        scopus_rawdata_list.append(scopus_rawdata_file_path.is_file())        
        scopus_parsing_list.append(scopus_parsing_articles_path.is_file())
        
        # Concatenation and deduplication
        dedup_parsing_articles_path = _get_parsing_file_paths(dedup_parsing_path)
        dedup_parsing_list.append( dedup_parsing_articles_path.is_file())

    return (years_list, wos_rawdata_list, wos_parsing_list, scopus_rawdata_list, scopus_parsing_list, dedup_parsing_list)


def place_after(gauche, droite, dx = 5, dy = 0):
    gauche_info = gauche.place_info()
    x = int(gauche_info['x']) + gauche.winfo_reqwidth() + dx
    y = int(gauche_info['y']) + dy
    droite.place(x = x, y = y)
    
def place_bellow(haut, bas, dx = 0, dy = 5):
    haut_info = haut.place_info()
    x = int(haut_info['x']) + dx
    y = int(haut_info['y']) + haut.winfo_reqheight() + dy
    bas.place(x = x, y = y)
    
def encadre_RL(fond, gauche, droite, color = "red", dn = 10, de = 10, ds = 10, dw = 10):
    
    gauche_info = gauche.place_info()
    droite_info = droite.place_info()

    x1 = int(gauche_info['x']) - dw
    y1 = int(gauche_info['y']) - dn
    
    x2 = int(gauche_info['x']) + gauche.winfo_reqwidth() + droite.winfo_reqwidth() + de
    y2 = int(droite_info['y']) + max(gauche.winfo_reqheight(), droite.winfo_reqheight()) + ds

    rectangle = fond.create_rectangle(x1, y1, x2, y2, outline = color, width = 2)
    fond.place(x = 0, y = 0)
    
def encadre_UD(fond, haut, bas, color = "red", dn = 10, de = 10, ds = 10, dw = 10):
    
    haut_info = haut.place_info()
    bas_info = bas.place_info()

    x1 = int(haut_info['x']) - dw
    y1 = int(haut_info['y']) - dn
    
    x2 = int(bas_info['x']) + max(haut.winfo_reqwidth(), bas.winfo_reqwidth()) + de
    y2 = int(bas_info['y']) + haut.winfo_reqheight() + bas.winfo_reqheight() + ds

    rectangle = fond.create_rectangle(x1, y1, x2, y2, outline = color, width = 2)
    fond.place(x = 0, y = 0)
    
def place_bellow_LabelEntry(haut, label_entry, dx = 0, dy = 5):
    
    haut_info = haut.place_info()
    x = int(haut_info['x']) + dx
    y = int(haut_info['y']) + haut.winfo_reqheight() + dy
    label_entry.place(x = x, y = y)
    

def font_size(size, scale_factor):
    '''Set the fontsize based on scale_factor.
    If the fontsize is less than minimum_size, 
    it is set to the minimum size.'''
    
    fontsize = int(size * scale_factor)    
    if fontsize < 8:
        fontsize = 8
    return fontsize


def str_size_mm(text, font, ppi):
    '''The function `_str_size_mm` computes the sizes in mm of a string.

    Args:
        text (str): the text of which we compute the size in mm.
        font (tk.font): the font of the text.
        ppi (int): pixels per inch of the display.

    Returns:
        `(tuple)`: width in mm `(float)`, height in mm `(float)`.

    Note:
        The use of this function requires a tkinter window availability 
        since it is based on a tkinter font definition.

    '''

    # Local imports
    from BiblioMeter_GUI.GUI_Globals import IN_TO_MM
       
    (w_px,h_px) = (font.measure(text),font.metrics("linespace"))
    w_mm = w_px * IN_TO_MM / ppi
    h_mm = h_px * IN_TO_MM / ppi

    return (w_mm,h_mm )


def mm_to_px(size_mm, ppi, fact = 1.0):
    '''The `mm_to_px' function converts a value in mm to a value in pixels
    using the ppi of the used display and a factor fact.
    
    Args:
        size_mm (float): value in mm to be converted.
        ppi ( float): pixels per inch of the display.
        fact (float): factor (default= 1).
        
    Returns:
        `(int)`: upper integer value of the conversion to pixels
        
    '''
    
    # Standard library imports 
    import math
    
    # Local imports
    from BiblioMeter_GUI.GUI_Globals import IN_TO_MM

    size_px = math.ceil((size_mm * fact / IN_TO_MM) * ppi)
    
    return size_px


def _window_properties(screen_width_px, screen_height_px):
    # Local imports
    import BiblioMeter_GUI.GUI_Globals as gg
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    
    # Getting number of pixels per inch screen resolution from imported global DISPLAYS
    ppi = gg.DISPLAYS[gg.BM_GUI_DISP]["ppi"]
    
    # Setting screen effective sizes in mm from imported global DISPLAYS
    screen_width_mm  = gg.DISPLAYS[gg.BM_GUI_DISP]["width_mm"]
    screen_height_mm = gg.DISPLAYS[gg.BM_GUI_DISP]["height_mm"]
    
    # Setting screen reference sizes in pixels and mm from globals internal to module "Coordinates.py"
    ref_width_px  = gg.REF_SCREEN_WIDTH_PX
    ref_height_px = gg.REF_SCREEN_HEIGHT_PX
    ref_width_mm  = gg.REF_SCREEN_WIDTH_MM
    ref_height_mm = gg.REF_SCREEN_HEIGHT_MM
    
    # Setting secondary window reference sizes in mm from globals internal to module "Coordinates.py"
    ref_window_width_mm  = gg.REF_WINDOW_WIDTH_MM
    ref_window_height_mm = gg.REF_WINDOW_HEIGHT_MM
    
    # Computing ratii of effective screen sizes to screen reference sizes in pixels
    scale_factor_width_px  = screen_width_px / ref_width_px
    scale_factor_height_px = screen_height_px / ref_height_px
        
    # Computing ratii of effective screen sizes to screen reference sizes in mm   
    scale_factor_width_mm  = screen_width_mm / ref_width_mm
    scale_factor_height_mm = screen_height_mm / ref_height_mm
    
    # Computing secondary window sizes in pixels depending on scale factors
    win_width_px  = mm_to_px(ref_window_width_mm * scale_factor_width_mm, ppi)    
    win_height_px = mm_to_px(ref_window_height_mm * scale_factor_height_mm, ppi)
    
    sizes_tuple = (win_width_px, win_height_px, 
                   scale_factor_width_px, scale_factor_height_px, 
                   scale_factor_width_mm, scale_factor_height_mm)
    
    return sizes_tuple

def general_properties(self):
    '''The function `general_properties` calculate the window sizes 
    and useful scale factors for the application launch window.
    For that, it uses reference values for the display sizes in pixels
    and mm through the globals:
    - "REF_SCREEN_WIDTH_PX" and "REF_SCREEN_HEIGHT_PX";
    - "REF_SCREEN_WIDTH_MM" and "REF_SCREEN_HEIGHT_MM".
    The secondary window sizes in mm are set through the globals: 
    - "REF_WINDOW_WIDTH_MM" and "REF_WINDOW_HEIGHT_MM".
    The window title is set through the global "APPLICATION_TITLE".
    These globals are defined locally in the module "GUI_Globals.py" 
    of the package "BiblioMeter_GUI".
    
    Args:
        None.
        
    Returns:
        (tuple): self, 2 window sizes in pixels, 2 scale factors for sizes in mm 
                 and 2 scale factors for sizes in pixels.
    '''
    # Local imports
    import BiblioMeter_GUI.GUI_Globals as gg
    
    # Getting screen effective sizes in pixels for window "root" (not woring for Darwin platform)
    screen_width_px  = self.winfo_screenwidth()
    screen_height_px = self.winfo_screenheight()
    
    sizes_tuple = _window_properties(screen_width_px, screen_height_px)
    
    win_width_px  = sizes_tuple[0]
    win_height_px = sizes_tuple[1]
    
    # Setting window size depending on scale factor
    self.geometry(f"{win_width_px}x{win_height_px}")
    self.resizable(False, False)    
    
    # Setting title window
    self.title(gg.APPLICATION_WINDOW_TITLE)
        
    return sizes_tuple

