__all__ = ['create_archi',
           'create_folder',
          ]


def create_folder(root_path, folder, verbose = False):
    # Standard library imports
    import os
    from pathlib import Path
    
    folder_path = root_path / Path(folder)
    if not os.path.exists(folder_path): 
        os.makedirs(folder_path)
        message = f"{folder_path} created"
    else:
        message = f"{folder_path} already exists"
    
    if verbose : print(message)
    return folder_path


def create_archi(bibliometer_path, corpus_year_folder, verbose = False):
    """
    
    """
   
    # Local globals imports
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_YEAR
        
    corpus_year_folder_path = create_folder(bibliometer_path, corpus_year_folder, verbose = verbose)
    _ = create_folder(corpus_year_folder_path, ARCHI_YEAR["bdd mensuelle"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, ARCHI_YEAR["homonymes folder"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, ARCHI_YEAR["OTP folder"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, ARCHI_YEAR["pub list folder"], verbose = verbose)
    _ = create_folder(corpus_year_folder_path, ARCHI_YEAR["history folder"], verbose = verbose)

    analysis_folder = create_folder(corpus_year_folder_path, ARCHI_YEAR["analyses"], verbose = verbose)
    _ = create_folder(analysis_folder, ARCHI_YEAR["if analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, ARCHI_YEAR["keywords analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, ARCHI_YEAR["subjects analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, ARCHI_YEAR["countries analysis"], verbose = verbose)
    _ = create_folder(analysis_folder, ARCHI_YEAR["institutions analysis"], verbose = verbose)

    corpus_folder = create_folder(corpus_year_folder_path, ARCHI_YEAR["corpus"], verbose = verbose)

    concat_folder = create_folder(corpus_folder, ARCHI_YEAR["concat"], verbose = verbose)
    _ = create_folder(concat_folder, ARCHI_YEAR["parsing"], verbose = verbose)

    dedup_folder = create_folder(corpus_folder, ARCHI_YEAR["dedup"], verbose = verbose)
    _ = create_folder(dedup_folder, ARCHI_YEAR["parsing"], verbose = verbose)

    scopus_folder = create_folder(corpus_folder, ARCHI_YEAR["scopus"], verbose = verbose)
    _ = create_folder(scopus_folder, ARCHI_YEAR["parsing"], verbose = verbose)
    _ = create_folder(scopus_folder, ARCHI_YEAR["rawdata"], verbose = verbose)

    wos_folder = create_folder(corpus_folder, ARCHI_YEAR["wos"], verbose = verbose)
    _ = create_folder(wos_folder, ARCHI_YEAR["parsing"], verbose = verbose)
    _ = create_folder(wos_folder, ARCHI_YEAR["rawdata"], verbose = verbose)
    
    message = f"Architecture created for {corpus_year_folder} folder"
    return message