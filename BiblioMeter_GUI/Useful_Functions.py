__all__ = ['last_available_years',
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


def existing_corpuses(bibliometer_path, corpuses_number = None):

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

    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    
    # Local globals imports
    from BiblioMeter_GUI.GUI_Globals import CORPUSES_NUMBER
    from BiblioMeter_GUI.Useful_Functions import last_available_years  
    
    # internal functions
    def _get_rawdata_filename_path(corpus_full_path, database_type):
        '''Returns the name of the rawdata file of a corpus pointed by the full path 'corpus_full_path'
        for the database type 'database_type'.
        '''

        # Standard library imports
        import os
        from pathlib import Path

        filenames_list = []

        if database_type == 'wos':
            for _, _, files in os.walk(corpus_full_path): 
                filenames_list.extend(file for file in files if file.endswith(".txt")) 

        if database_type == 'scopus':
            for _, _, files in os.walk(corpus_full_path):
                filenames_list.extend(file for file in files if file.endswith(".csv"))

        if filenames_list == []:
            return Path(f'{database_type} rawdata file not Found')
        else:
            return corpus_full_path / Path(filenames_list[0])
    
    
    def _get_database_paths(year_folder_path, rawdata_alias, parsing_alias, article_path_alias, database_type):
        '''Returns useful full-paths for the database type 'database_type'.
        '''
        database_folder_alias = FOLDER_NAMES[database_type]
        database_path_alias   = Path(corpus_alias) / Path(database_folder_alias)        
        rawdata_full_path     = year_folder_path / database_path_alias / Path(rawdata_alias)
        database_rawdata_path = _get_rawdata_filename_path(rawdata_full_path, database_type)
        database_parsing_path = year_folder_path / database_path_alias / Path(parsing_alias) / Path(article_path_alias)
        
        return database_rawdata_path, database_parsing_path
    
    
    if not corpuses_number: corpuses_number = CORPUSES_NUMBER
    
    years_folder_list = last_available_years(bibliometer_path, corpuses_number)

    # Setting useful aliases from globals
    corpus_alias       = FOLDER_NAMES['corpus']
    rawdata_alias      = FOLDER_NAMES['rawdata']
    parsing_alias      = FOLDER_NAMES['parsing']
    concat_alias       = FOLDER_NAMES['concat']
    dedup_alias        = FOLDER_NAMES['dedup']
    concat_path_alias  = Path(corpus_alias) / FOLDER_NAMES['concat']
    dedupli_path_alias = Path(corpus_alias) / FOLDER_NAMES['dedup']
    article_path_alias = DIC_OUTDIR_PARSING['A']
    
    # Initialization of lists    
    years_list = list()
    wos_rawdata_list = list()
    wos_parsing_list = list()
    scopus_rawdata_list = list()
    scopus_parsing_list = list()
    deduplication_list = list()

    for year in years_folder_list:
        
        year_folder_path = bibliometer_path / Path(year) 
        years_list.append(year)
        
        # Wos
        wos_rawdata_path, wos_parsing_path = _get_database_paths(year_folder_path, rawdata_alias, parsing_alias, article_path_alias, "wos")
        wos_rawdata_list.append(wos_rawdata_path.is_file())
        wos_parsing_list.append(wos_parsing_path.is_file())
        
        # Scopus
        scopus_rawdata_path, scopus_parsing_path = _get_database_paths(year_folder_path, rawdata_alias, parsing_alias, article_path_alias, "scopus")
        scopus_rawdata_list.append(scopus_rawdata_path.is_file())        
        scopus_parsing_list.append(scopus_parsing_path.is_file())
        
        # Concatenation and deduplication (by year)
        deduplication_path = year_folder_path / Path(dedupli_path_alias) / Path(parsing_alias) / Path(article_path_alias)
        deduplication_list.append(deduplication_path.is_file())

    return years_list, wos_rawdata_list, wos_parsing_list, scopus_rawdata_list, scopus_parsing_list, deduplication_list


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



