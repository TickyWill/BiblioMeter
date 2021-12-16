__all__ = ['common_files',
           '_get_indexer',
           'concatenate_dat',
           'df_with_no_more_doubles',
          'get_the_doubles',
          'complete_deduplicate_and_save_articles',
          'deduplicated_all_but_articles',
          'you_got_OTPed',
          'liste_de_validation']

def common_files(path_1 = None,path_2 = None):
    
    '''Builds a list containing the list of the names of the files present in both 
    scopus and wos parsing file
    
    ['addresses.dat', 'articles.dat', 'authors.dat', 'authorskeywords.dat',
    'countries.dat','institutions.dat', 'journalkeywords.dat', 'keywords.dat',
    'references.dat','subjects.dat', 'subjects2.dat', 'titlekeywords.dat']
    
    Args : 
        path_1 (string) : the path leading to where the .dat documents are saved
        path_2 (string) : the path leading to where the .dat documents are saved
        
    Returns :
        The list of common_files'''
    
    # Local library imports
    if path_1 is None:
        from .BiblioMeterGlobalsVariables import PATH_SCOPUS_PARSING
        path_1 = PATH_SCOPUS_PARSING
    if path_2 is None:
        from .BiblioMeterGlobalsVariables import PATH_WOS_PARSING
        path_2 = PATH_WOS_PARSING
        
    # Standard and 3rd party library imports
    import os
    import pandas as pd
    
    list_dir_1=set(os.listdir(path_1))

    list_dir_2=set(os.listdir(path_2))

    union = list_dir_1.union(list_dir_2)
    
    union.remove('failed.json')

    print('\nThe common files list of documents.dat is : ', union)
    
    return union
    
def _get_indexer(path = None, document_name ='articles.dat'):
    
    '''Returns the length of articles.dat from wos or scopus, to later be used to 
    increment when concatening before getting rid of doublons. If path isn't specified
    then the default path will be PATH_SCOPUS_PARSING which is where parsed.dat documents
    from the scopus corpuses are stored.
    
    Args : 
        path (string) : the path leading to where the articles.dat document is saved     
        
    Returns :
        The number by which we need to increment Pub_id when concatening articles.dat 
        from wos to scopus'''
    
    # Global variable imports
    if path is None:
        from .BiblioMeterGlobalsVariables import PATH_SCOPUS_PARSING
        path = PATH_SCOPUS_PARSING
        
    # Standard and 3rd party library imports
    import pandas as pd
    
    df = pd.DataFrame()
    df = pd.read_csv(path + document_name,sep="\t")
    indexer = df.shape[0]
    
    return indexer

def concatenate_dat(document_name, indexer = _get_indexer(), path_1 = None, path_2 = None, path_3 = None):
    
    '''Concatenates the documents.dat having the same name from the wos parsing and the 
    scopus parsing.
    
    Args : 
        document_name (string) : name of the document wanting to be concatenated3
        indexer (int) : number by which we increment the Pub_ids
        path_1 (string) : path leading to where the .dat documents are saved
        path_2 (string) : path leading to where the .dat documents are saved
        path_3 (string) : path leading to where the new concatenated .dat will be saved
        
    Returns :
        A .dat file saved in path_3'''
    
    # Local library imports
    if path_1 is None:
        from .BiblioMeterGlobalsVariables import PATH_SCOPUS_PARSING
        path_1 = PATH_SCOPUS_PARSING
    if path_2 is None:
        from .BiblioMeterGlobalsVariables import PATH_WOS_PARSING
        path_2 = PATH_WOS_PARSING
    if path_3 is None:
        from .BiblioMeterGlobalsVariables import PATH_DAT_CONCATENATED
        path_3 = PATH_DAT_CONCATENATED
        
    # Standard and 3rd party library imports
    import pandas as pd
    
    df_scopus = pd.read_csv(path_1 + document_name, sep="\t")
    
    df_wos = pd.read_csv(path_2 + document_name, sep="\t")
    df_wos['Pub_id']=df_wos['Pub_id']+indexer
    
    list_df = [df_wos,df_scopus]
    df_inter = pd.concat(list_df,ignore_index=False)
    df_inter.set_index('Pub_id',inplace=True)
    df_inter.sort_index(inplace=True)
    
    df_inter.to_csv(path_3 + document_name,
                    index=True,
                    columns=df_inter.columns.tolist(),
                    sep='\t',
                    header=True)
    return document_name, 'Document was successfully concatenated and saved in ', path_3

def df_with_no_more_doubles(path = None):
    
    '''Uses the concatenated articles.dat document and applies a succesion of filters
    to get rid of doubled information and returns a df containing an index of Pub_ids
    with no doubled lines.
    
    Args :
        path (string) : path leading to where the .dat document is saved
        
    Returns :
        A df with no duplicates but unfull information and a list with the index of this df'''
    
    # Global imports
    if path is None:
        from .BiblioMeterGlobalsVariables import PATH_DAT_CONCATENATED
        path = PATH_DAT_CONCATENATED
    
    # Standard and 3rd party library imports
    import pandas as pd
    
    df_articles_concat = pd.read_csv(path + '/articles.dat',
                                     sep="\t",
                                     index_col='Pub_id')

    # Get rid of unusable lines (Title and Document Type both empty as well as DOI)
    filtre_Title_DT = (df_articles_concat['Title'].isna()) & (df_articles_concat['Document_type'].isna())
    filtre_Title_DOI = (df_articles_concat['Title'].isna()) & (df_articles_concat['DOI'].isna())
    df_articles_concat=df_articles_concat[~filtre_Title_DOI]
    df_articles_concat=df_articles_concat[~filtre_Title_DT]

    # On récupère un indice unique des duplicats sur le DOI, on traitera les cas particulier après.
    # On les retire donc pour les gérer séparement en les rajouter à la DF une fois traités
    # Pour ce faire on va utiliser DateFrame.drop_duplicates pour récupérer l'index
    # On les rajoutera après

    filtre_DOI_NA = (df_articles_concat['DOI'].isna())
    df_inter_1=df_articles_concat[~filtre_DOI_NA]
    df_inter_1 = df_inter_1.drop_duplicates(subset=['DOI'],
                                            keep='first')

    # On rajoute les articles sans DOI
    df_inter_2 = pd.concat([df_inter_1,df_articles_concat[filtre_DOI_NA]])

    # Pour gérer les DOI isna(), on va simplement récépérer la DataFrame qui ne possède que les DOI isna()
    # On fera un filtre sur la colonne Title et Document Type (sinon risque de perdre de l'information)

    df_no_doubles = df_inter_2.drop_duplicates(subset=['Document_type','Title'], 
                                               keep='first')

    indices_of_duplicates = df_no_doubles.index.tolist()
    
    return [df_no_doubles, indices_of_duplicates]

def get_the_doubles(indice, df_DOI, df_no_DOI, df_articles_concat):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        A list of the duplicats of indice'''
    
    # Standard and 3rd party library imports
    import pandas as pd
    
    list_df_dup=[]
    
    filt_inter_DOI = (df_DOI['DOI'] == df_articles_concat['DOI'].loc[indice]) # Renvoie un filtre intermédiaire des mêmes DOI
    df_inter_DOI = df_DOI[filt_inter_DOI] # On récupère une DF avec les doublons, pour permettre de choisir quoi garder ensuite

    filt_inter_Title_DT = (df_no_DOI['Title'] == df_articles_concat['Title'].loc[indice]) & (df_no_DOI['Document_type'] == df_articles_concat['Document_type'].loc[indice])
    df_inter_Title_DT = df_no_DOI[filt_inter_Title_DT]

    if df_inter_DOI.index.tolist() != df_inter_Title_DT.index.tolist():
        df_inter = pd.concat([df_inter_DOI,df_inter_Title_DT])
        
    return [df_inter,df_inter.index.tolist()]

def complete_deduplicate_and_save_articles(list_df_dup = None, indices_of_duplicates = None, path = None):
    
    '''_____
    
    Args : 
       _____
    
    Returns :
        Nothing, but saves documents in path'''
    
    # Local imports
    import BiblioMeter_Utils as bmu
    
    # Standard and 3rd party library imports
    import pandas as pd
    
    # Global variable imports
    if path is None:
        from .BiblioMeterGlobalsVariables import PATH_DAT_DEDUPLICATED
        path = PATH_DAT_DEDUPLICATED
    
    if list_df_dup is None:
        raise Exception('''None case for list_df_dup hasn't been taken cared of yet, please enter a value for list_of_dup''')
        
    if indices_of_duplicates is None:
        [_,indices_of_duplicates] = bmu.df_with_no_more_doubles()

    df_dup_full_unique=pd.DataFrame()
    tour = 0

    for i in range(len(list_df_dup)):
        working_df = list_df_dup[i]
        nombre_duplication = working_df.shape[0]
        nombre_colonne = working_df.shape[1]
        if nombre_duplication != 1:
            for j in range(nombre_colonne):
                if working_df.iloc[[0],[j]].isna().bool():
                    for k in range(1,nombre_duplication):
                        if working_df.iloc[[k],[j]].isna().bool():
                            working_df.iloc[[0],[j]] = working_df.iloc[[k],[j]]

        if tour == 0:
            tour = 1
            df_dup_full_unique = working_df
        else:
            df_dup_full_unique = pd.concat([df_dup_full_unique,working_df])

    df_dup_full_unique.reset_index(inplace = True)

    df_AAH=pd.DataFrame()        
    df_AAH = df_AAH.append([df_dup_full_unique[df_dup_full_unique['Pub_id'] == i] for i in indices_of_duplicates])

    df_AAH.to_csv(path + 'articles.dat',
                        index=False,
                        columns=df_AAH.columns.tolist(),
                        sep='\t',
                        header=True)    

    print('Etape terminée')
    
def deduplicated_all_but_articles(file_name, indices_of_duplicates = None, path_1 = None, path_2 = None):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        Nothing, but saves documents in path'''
    
    # Local imports
    import BiblioMeter_Utils as bmu
    
    # Standard and 3rd party library imports
    import pandas as pd
    
    # Global variable imports
    if path_1 is None:
        from .BiblioMeterGlobalsVariables import PATH_DAT_CONCATENATED
        path_1 = PATH_DAT_CONCATENATED
    
    if path_2 is None:
        from .BiblioMeterGlobalsVariables import PATH_DAT_DEDUPLICATED
        path_2 = PATH_DAT_DEDUPLICATED
        
    if indices_of_duplicates is None:
        [_,indices_of_duplicates] = bmu.df_with_no_more_doubles()
        
    
    
    exported_df = pd.read_csv(path_1 + file_name, sep="\t")
    
    filt = (exported_df['Pub_id'].isin(indices_of_duplicates))
    exported_df=exported_df[filt]

    if file_name == 'authors.dat':
        exported_df.sort_values(['Pub_id','Idx_author'], inplace=True)
    if file_name == 'addresses.dat':
        exported_df.sort_values(['Pub_id','Idx_address'], inplace=True)
        
    # Terminer les cas particuliers sur le tri des lignes
            
    exported_df.to_csv(path_2 + file_name,
                    index=False,
                    columns=exported_df.columns.tolist(),
                    sep='\t',
                    header=True)
    
def you_got_OTPed(df,i):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        Adds OTP to df'''
    
    # Local imports
    import BiblioMeter_Utils as bmu
    
    # Standard and 3rd party library imports
    import pandas as pd
    
    # Global variable imports
    from .BiblioMeterGlobalsVariables import OTP_STRING
    
    if 'List_of_OTP' in df.columns:
        df['List_of_OTP'].iloc[i] = OTP_STRING[df.iloc[i]['Service (lib court)']]
    else:
        df['List_of_OTP'] = pd.Series()
        df['List_of_OTP'].iloc[i] = OTP_STRING[df.iloc[i]['Service (lib court)']]
    
    return df

def liste_de_validation(df,i):
    
    '''_____
    
    Args : 
       _____
        
    Returns :
        Adds OTP to df'''
    
    # Local imports
    import BiblioMeter_Utils as bmu
    
    # Global variable imports
    from .BiblioMeterGlobalsVariables import OTP_LIST
    
    validation_list = OTP_LIST[df.iloc[i]['Service (lib court)']]
    
    truc = '"'+','.join(validation_list)+'"'
    
    return truc