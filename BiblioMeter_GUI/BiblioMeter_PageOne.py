__all__ = ['data_parsing','existing_corpuses','concatenate_and_deduplicate']

def data_parsing(annee, source, results, second_inst):
    
    """
    Description à venir
    """
    
    # Standard library imports
    import os
    import json
    from pathlib import Path
    
    # 3rd party imports
    import tkinter as tk
    from tkinter import messagebox
    
    # Local imports
    import BiblioAnalysis_Utils as bau
    from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
    from BiblioMeter_GUI.Globals_GUI import WOS_PATH
    from BiblioMeter_GUI.Globals_GUI import RAWDATA_PATH
    from BiblioMeter_GUI.Globals_GUI import PARSING_PATH
    from BiblioMeter_GUI.Globals_GUI import SCOPUS_PATH
    from BiblioMeter_GUI.Globals_GUI import REFUTILS_PATH

    # Eclaircissage de la variable results
    list_annee = results[0]
    list_wos_rawdata = results[1]
    list_wos_parsing = results[2]
    list_scopus_rawdata = results[3]
    list_scopus_parsing = results[4]

    # TO DO : Changer la manière dont est renseigné database_type ET expert ET venv ET rep_utils
    venv = False
    expert =  False
    database_type = source

    # Création de la variable path_rawdata, path_parsing et parser_done qui correspond au chemin pour aller au rawdata
    # avec ici la première vérification de disponibilité du fichier rawdata et de demande de parsing
    if source == 'wos':
        if list_wos_rawdata[list_annee.index(annee)] == False:
            messagebox.showwarning('Missing files', f"Warning : le fichier rawdata de {source} de l'année {annee} n'est pas disponible")
            return
        else:
            rep_utils = '' # TO DO, changer la manière dont est rensigné le ref_utils
            path_rawdata = Path(ROOT_PATH) / Path(annee) / Path(WOS_PATH) / Path(RAWDATA_PATH) 
            path_parsing = Path(ROOT_PATH) / Path(annee) / Path(WOS_PATH) / Path(PARSING_PATH)
            parser_done = list_wos_parsing[list_annee.index(annee)]
    else:

        if list_scopus_rawdata[list_annee.index(annee)] == False:
            messagebox.showwarning('Missing files', f"Warning : le fichier rawdata de {source} de l'année {annee} n'est pas disponible")
            return
        else:
            rep_utils = REFUTILS_PATH # TO DO, changer la manière dont est renseigné le ref_utils
            path_rawdata = Path(ROOT_PATH) / Path(annee) / Path(SCOPUS_PATH) / Path(RAWDATA_PATH)
            path_parsing = Path(ROOT_PATH) / Path(annee) / Path(SCOPUS_PATH) / Path(PARSING_PATH)
            parser_done = list_scopus_parsing[list_annee.index(annee)]

    ## Building the names of the useful folders
    in_dir_parsing = path_rawdata
    out_dir_parsing = path_parsing

    if not os.path.exists(out_dir_parsing):
        os.mkdir(out_dir_parsing)

    ## Running function biblio_parser
    # TO DO : IL FAUT REPONDRE NON SINON BUG POUR LE MOMENT
    if parser_done == False:
        # Setting the specific affiliations filter (default = None)

        # TO DO : IL FAUT REPONDRE OUI SINON BUG POUR LE MOMENT
        
        if second_inst == 1: 
            inst_filter_dic = [('Liten','France'),('Ines','France'),('Simap','France')]
        else:
            inst_filter_dic = None
            
        bau.biblio_parser(in_dir_parsing, out_dir_parsing, database_type, expert, rep_utils, inst_filter_dic) 
        with open(Path(out_dir_parsing) / Path('failed.json'), 'r') as failed_json:
                data_failed=failed_json.read()
        dic_failed = json.loads(data_failed)
        articles_number = dic_failed["number of article"]

    #print("\n\nCorpus parsing saved in folder:\n", str(out_dir_parsing))
    #print('\nNumber of articles in the corpus : ', articles_number)

    messagebox.showinfo('Information', f"Parsing effectué \n Parsing processed on full corpus \n Number of articles in the corpus : {articles_number}")

def existing_corpuses(emplacement_BM):
    
    """ Renvoie une liste des corpus disponibles par année et par source """
    
    # Standard library imports
    import os
    from pathlib import Path
    
    # 3rd party imports
    # None
    
    # Local imports
    from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
    from BiblioMeter_GUI.Globals_GUI import WOS_PATH
    from BiblioMeter_GUI.Globals_GUI import RAWDATA_PATH
    from BiblioMeter_GUI.Globals_GUI import PARSING_PATH
    from BiblioMeter_GUI.Globals_GUI import SCOPUS_PATH
    from BiblioMeter_GUI.Globals_GUI import CONCATENATION_PATH
    from BiblioMeter_GUI.Globals_GUI import ARTICLE_PATH
    from BiblioMeter_GUI.Globals_GUI import WOS_FILE_NAME
    from BiblioMeter_GUI.Globals_GUI import SCOPUS_FILE_NAME
    
    
    # Recherche des années disponibles
    root_path = emplacement_BM
    
    # Récupérer les corpus disponibles
    list_dir = os.listdir(ROOT_PATH)
    list_annee = list()
    list_wos_rawdata = list()
    list_wos_parsing = list()
    list_scopus_rawdata = list()
    list_scopus_parsing = list()
    list_concatenation = list()

    for i,annee in enumerate(list_dir):
        if len(annee) == 4: # TO DO : Bancale, à reprendre
            list_annee.append(annee)
            
            # Concatenation (by year)
            path_concat = Path(ROOT_PATH) / Path(list_annee[i]) / Path(CONCATENATION_PATH) / Path(ARTICLE_PATH)
            list_concatenation.append(path_concat.is_file())
            
            # Wos
            path_wos_parsing = Path(ROOT_PATH) / Path(list_annee[i]) / Path(WOS_PATH) / Path(PARSING_PATH) / Path(ARTICLE_PATH)
            list_wos_parsing.append(path_wos_parsing.is_file())
            path_wos_rawdata = Path(ROOT_PATH) / Path(list_annee[i]) / Path(WOS_PATH) / Path(RAWDATA_PATH) / Path(WOS_FILE_NAME)
            list_wos_rawdata.append(path_wos_rawdata.is_file())
            
            # Scopus
            path_scopus_parsing = Path(ROOT_PATH) / Path(list_annee[i]) / Path(SCOPUS_PATH) / Path(PARSING_PATH) / Path(ARTICLE_PATH)
            list_scopus_parsing.append(path_scopus_parsing.is_file())
            path_scopus_rawdata = Path(ROOT_PATH) / Path(list_annee[i]) / Path(SCOPUS_PATH) / Path(RAWDATA_PATH) / Path(SCOPUS_FILE_NAME)
            list_scopus_rawdata.append(path_scopus_rawdata.is_file())
            
    return list_annee, list_wos_rawdata, list_wos_parsing, list_scopus_rawdata, list_scopus_parsing, list_concatenation

def concatenate_and_deduplicate(annee):
    
    """
    Description et consolidation/correction à venir
    """
    
    # Standard library imports
    from pathlib import Path
    
    # Local imports
    import BiblioMeter_Utils as bmu
    from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
    from BiblioMeter_GUI.Globals_GUI import WOS_PATH
    from BiblioMeter_GUI.Globals_GUI import PARSING_PATH
    from BiblioMeter_GUI.Globals_GUI import SCOPUS_PATH
    from BiblioMeter_GUI.Globals_GUI import ARTICLE_PATH
    from BiblioMeter_GUI.Globals_GUI import CONCAT_PATH
    from BiblioMeter_GUI.Globals_GUI import DEDUPLI_PATH
    
    # 3rd party library imports
    import pandas as pd
    
    # Creation des chemins vers les corpus
    path_wos_parsing = Path(ROOT_PATH) / Path(annee) / Path(WOS_PATH) / Path(PARSING_PATH)
    path_scopus_parsing = Path(ROOT_PATH) / Path(annee) / Path(SCOPUS_PATH) / Path(PARSING_PATH)
    path_concat = Path(ROOT_PATH) / Path(annee) / Path(CONCAT_PATH)
    path_dedupli = Path(ROOT_PATH) / Path(annee) / Path(DEDUPLI_PATH)

    # Allows us to get a list of the documents.dat that will be concatenated
    list_files = bmu.common_files(path_wos_parsing, path_scopus_parsing)

    # Allows us to get the number by which we need to increment the Pub_id so they can
    # all be unique
    indexer = bmu._get_indexer(path_wos_parsing / Path(ARTICLE_PATH))
    
    # Now we'll concatenate each documents.dat that was returned by _common_files
    _=[bmu.concatenate_dat(i, indexer, path_wos_parsing, path_scopus_parsing, path_concat) for i in list_files]
    
    print(f'Documents were successfully concatenated and saved in {path_concat}')
    
    # Now we'll try and get the a clean and full as possible df and store it in a new folder

    df_articles_concat = pd.read_csv(path_concat / Path(ARTICLE_PATH), 
                                         sep="\t", 
                                         index_col='Pub_id')
    
    filtre_DOI_NA = (df_articles_concat['DOI'].isna())
    
    df_inter_1 = df_articles_concat[~filtre_DOI_NA]
    df_inter_2 = df_articles_concat[filtre_DOI_NA]

    [df_no_doubles,L]=bmu.df_with_no_more_doubles(path_concat / Path(ARTICLE_PATH))

    LL=[]
    df_LL = []

    for i in L:
        A = bmu.get_the_doubles(i, df_inter_1, df_inter_2, df_articles_concat)
        LL.append(A[1])
        df_LL.append(A[0])
        

    # Il reste l'import vers déduplicated à faire

    bmu.complete_deduplicate_and_save_articles(list_df_dup = df_LL, indices_of_duplicates = L, path = path_dedupli / Path(ARTICLE_PATH))

    list_files_without_articles = list_files
    list_files_without_articles.remove('articles.dat')

    _ = [bmu.deduplicated_all_but_articles(file_name, 
                                           indices_of_duplicates = L, 
                                           path_concat = path_concat,
                                           path_dedupli = path_dedupli) for file_name in list_files_without_articles]

    print(f'Documents were successfully deduplicated and saved in {path_dedupli}')