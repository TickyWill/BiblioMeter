__all__ = ['five_last_available_years', 
           'get_corpus_filename_by_year',
           'la_liste_des_filtres_disponibles',
           'existing_corpuses']

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
    
    # Récupérer les corpus disponibles
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

    from BiblioMeter_GUI.BiblioMeter_AllPagesFunctions import five_last_available_years
    from BiblioMeter_GUI.BiblioMeter_AllPagesFunctions import get_corpus_filename_by_year
    
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