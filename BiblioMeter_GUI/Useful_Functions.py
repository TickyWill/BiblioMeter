__all__ = ['last_available_years', 
           'get_corpus_filename_by_year',
           'existing_corpuses', 
           'place_after', 
           'place_bellow', 
           'place_bellow_LabelEntry', 
           'encadre_RL', 
           'encadre_UD', 
           'font_size']
    
def last_available_years(bibliometer_path, year_number):
    
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
    return list_annee[-year_number:]

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
    
    from BiblioMeter_GUI.Globals_GUI import CORPUSES_NUMBER
    from BiblioMeter_GUI.Useful_Functions import last_available_years
    from BiblioMeter_GUI.Useful_Functions import get_corpus_filename_by_year
    
    list_dir = last_available_years(bibliometer_path, CORPUSES_NUMBER)

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
    

def font_size(size, scale_factor):
    '''Set the fontsize based on scale_factor.
    If the fontsize is less than minimum_size, 
    it is set to the minimum size.'''
    
    fontsize = int(size * scale_factor)    
    if fontsize < 8:
        fontsize = 8
    return fontsize



