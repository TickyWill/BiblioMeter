__all__ = ['five_last_available_years', 
           'get_corpus_filename_by_year']

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