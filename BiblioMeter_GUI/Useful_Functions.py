__all__ = ['five_last_available_years', 
           'get_corpus_filename_by_year',
           'la_liste_des_filtres_disponibles',
           'existing_corpuses', 
           'place_after', 
           'place_bellow', 'place_bellow_LabelEntry', 
           'encadre_RL', 'encadre_UD', 'get_displays', 'mm_to_px', 'str_size_mm', 'font_size']

def la_liste_des_filtres_disponibles(bibliometer_path):
    
    '''
    Returns the list of the available created filters
    '''
    # Standard library imports
    import os
    from pathlib import Path
    
    # Local imports
    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    
    return os.listdir(bibliometer_path / Path(STOCKAGE_ARBORESCENCE['general'][2]))
    
def five_last_available_years(bibliometer_path):
    
    '''
    Returns a list of the available five last available years where corpuses are stored
    '''
        
    # Standard library imports
    import os
    
    # Récupérer les corpus disponibles TO DO : consolider le choix des années
    list_dir = os.listdir(bibliometer_path)
    list_annee = list()
    for annee in list_dir:
        if len(annee) == 4:
            list_annee.append(annee)
    return list_annee[-5:]

def get_corpus_filename_by_year(full_path, database_type):
    
    '''
    Returns the name of the rawdata file
    '''
        
    # Standard library imports
    import os
    from pathlib import Path
    
    path_filename = []
    
    if database_type == 'wos':
        for path, _, files in os.walk(full_path):
                path_filename.extend(Path(path) / Path(file) for file in files
                                                              if file.endswith(".txt"))
        if path_filename == []:
            return Path('Not Found')
        else:
            return Path(path_filename[0])
                    
    if database_type == 'scopus':
        for path, _, files in os.walk(full_path):
                path_filename.extend(Path(path) / Path(file) for file in files
                                                              if file.endswith(".csv"))
        if path_filename == []:
            return Path('Not Found')
        else:
            return Path(path_filename[0])

def existing_corpuses(bibliometer_path):

    """ 
    Description : Returns a list of list of zeros and ones displaying available or not
    rawdata and parsing where documents are stocked by year.
    [[2018, 2019, 2020, 2021, 2022],   #Years
     [0, 0, 0, 0, 0],                  #Wos Rawdata
     [0, 0, 0, 0, 0],                  #Scopus Rawdata
     [0, 0, 0, 0, 0],                  #Wos Parsing
     [0, 0, 0, 0, 0],                  #Scopus Parsing
     [0, 0, 0, 0, 0]]                  #Concatenation & Deduplication

    Uses the following globals :
    - DIC_OUTIR_PARSING
    - FOLDER_NAMES

    Args : 
    - root_path is where the first foler of BilioMeter is, inside this folder is where all
    useful and necessary files for BiblioMeter to be working are placed in a very specific. way.

    Returns : A list of lists.

    """

    # Standard library imports
    import os
    from pathlib import Path

    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES

    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import get_corpus_filename_by_year
    
    list_dir = five_last_available_years(bibliometer_path)

    # Création des alias pour simplifier les accès
    wos_alias = FOLDER_NAMES['wos']
    scopus_alias = FOLDER_NAMES['scopus']
    corpus_path_alias = FOLDER_NAMES['corpus']

    scopus_path_alias = Path(corpus_path_alias) / Path(scopus_alias)
    wos_path_alias = Path(corpus_path_alias) / Path(wos_alias)

    parsing_path_alias = FOLDER_NAMES['parsing']
    rawdata_path_alias = FOLDER_NAMES['rawdata']

    concat_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['concat']
    dedupli_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['dedup']

    article_path_alias = DIC_OUTDIR_PARSING['A']
    
    # Set of variables
    list_annee = list()
    list_wos_rawdata = list()
    list_wos_parsing = list()
    list_scopus_rawdata = list()
    list_scopus_parsing = list()
    list_deduplication = list()

    for i, annee in enumerate(list_dir):
        list_annee.append(annee)

        # Concatenation and deduplication (by year)
        path_dedupli = Path(bibliometer_path) / Path(list_annee[i]) / Path(dedupli_path_alias) / Path(parsing_path_alias) / Path(article_path_alias)
        list_deduplication.append(path_dedupli.is_file())

        # Wos
        path_wos_parsing = Path(bibliometer_path) / Path(list_annee[i]) / Path(wos_path_alias) / Path(parsing_path_alias) / Path(article_path_alias)
        list_wos_parsing.append(path_wos_parsing.is_file())
        path_wos_rawdata = get_corpus_filename_by_year(Path(bibliometer_path) / Path(list_annee[i]), 'wos')
        list_wos_rawdata.append(path_wos_rawdata.is_file())

        # Scopus
        path_scopus_parsing = Path(bibliometer_path) / Path(list_annee[i]) / Path(scopus_path_alias) / Path(parsing_path_alias) / Path(article_path_alias)
        list_scopus_parsing.append(path_scopus_parsing.is_file())
        path_scopus_rawdata = get_corpus_filename_by_year(Path(bibliometer_path) / Path(list_annee[i]), 'scopus')
        list_scopus_rawdata.append(path_scopus_rawdata.is_file())

    return list_annee, list_wos_rawdata, list_wos_parsing, list_scopus_rawdata, list_scopus_parsing, list_deduplication

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
    
def get_displays(in_to_mm = None): 
    
    ''' The function `get_displays` allows to identify the set of displays
        available within the user hardware and to get their parameters.
        If the width or the height of a display are not available in mm 
        through the `get_monitors` method (as for Darwin platforms), 
        the user is asked to specify the displays diagonal size to compute them.
        
    Returns:
        `list`: list of dicts with one dict per detected display,
                each dict is keyed by 8 display parameters.   
    '''
    # To Do: convert prints and inputs to gui displays and inputs
    
    # Standard library imports
    import math
    
    # 3rd party imports
    from screeninfo import get_monitors
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM

    if in_to_mm==None: in_to_mm = IN_TO_MM
    
    displays = [{'x':m.x,'y':m.y,'width':m.width,
                 'height':m.height,'width_mm':m.width_mm,
                 'height_mm':m.height_mm,'name':m.name,
                 'is_primary':m.is_primary} for m in get_monitors()]
    

    print('Number of detected displays:',len(displays))
    
    for disp in range(len(displays)):
        width_px = displays[disp]['width']
        height_px = displays[disp]['height']
        diag_px = math.sqrt(int(width_px)**2 + int(height_px)**2)    
        width_mm = displays[disp]['width_mm']
        height_mm = displays[disp]['height_mm']
        if width_mm is None or height_mm is None: 
            diag_in = float(input('Enter the diagonal size of the screen n°' + str(disp) + ' (inches)'))
            width_mm = round(int(width_px) * (diag_in/diag_px) * in_to_mm,1)
            height_mm = round(int(height_px) * (diag_in/diag_px) * in_to_mm,1)
            displays[disp]['width_mm'] = str(width_mm)
            displays[disp]['height_mm'] = str(height_mm)
        else:
            diag_in = math.sqrt(float(width_mm) ** 2 + float(height_mm) ** 2) / in_to_mm
        displays[disp]['ppi'] = round(diag_px/diag_in,2)
        
    return displays


def mm_to_px(size_mm, ppi ,fact = 1.0):
    '''The `_mm_to_px' function converts a value in mm to a value in pixels
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
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM

    size_px = math.ceil((size_mm * fact / IN_TO_MM) * ppi)
    
    return size_px

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
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM
       
    (w_px, h_px) = (font.measure(text), font.metrics("linespace"))
    w_mm = w_px * IN_TO_MM / ppi
    h_mm = h_px * IN_TO_MM / ppi

    return (w_mm, h_mm)

# Set the fontsize based on scale_factor,
# if the fontsize is less than minimum_size
# it is set to the minimum size
def font_size(size, scale_factor):

    fontsize = int(size * scale_factor)
    
    if fontsize < 8:
        fontsize = 8

    return fontsize