__all__ = ['parsing_concatenate_deduplicate',]


def parsing_concatenate_deduplicate(useful_path_list, inst_filter_list=None):
    ''' The `parsing_concatenate_deduplicate` function concatenates parsing files of two corpuses 
    using the `_get_common_files` and `_concatenate_dat` functions. 
    Then it proceeds with deduplication of article lines using the `_deduplicate_articles` function.
    Finally, it rationalizes the content of the other parsing files using the IDs of the droped articles lines
    in the `_deduplicate_dat` function.
    The functions used are got from `BiblioParsingConcat.py` module of 'BiblioAnalysis_Utils' package.
    The results are saved in folders defined through the global 'FOLDER_NAMES'.
    
    Args:
        project_folder (string): path of the folder where the corpuses are saved.
        
    Returns: 
        None.
        
    Note:
        The globals 'CONCATENATED_XLSX', 'DEDUPLICATED_XLSX', 'DIC_OUTDIR_PARSING' and 'FOLDER_NAMES' are used.
                                  
    '''
    
    # Standard libraries import
    import os
    from pathlib import Path

    # 3rd party library imports
    import pandas as pd

    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import extend_author_institutions
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import CONCATENATED_XLSX
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DEDUPLICATED_XLSX
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    
    # Setting global aliases
    articles_dat_alias = DIC_OUTDIR_PARSING['A']
    norm_journal_alias = COL_NAMES['temp_col'][1]

    # Setting the useful paths
    path_scopus_parsing = useful_path_list[0]
    path_wos_parsing = useful_path_list[1]
    path_concat_parsing = useful_path_list[2]
    path_rational_parsing = useful_path_list[3]        

    # Getting a list of the .dat files to be concatenated
    files_list = sorted(_get_common_files(path_scopus_parsing, path_wos_parsing))

    # Concatenating the .dat files having the same same name .dat file of the list of files files_list 
    # of the first corpus with the one of the second corpus 
    for file in files_list: 
        _concatenate_dat(file, path_scopus_parsing, path_wos_parsing, path_concat_parsing)
    print(f'\nParsing files successfully concatenated and saved in:\n{path_concat_parsing}')
    
    # Setting the secondary institutions
    if inst_filter_list: 
        # Extending the author with institutions parsing file
        extend_author_institutions(path_concat_parsing, inst_filter_list)

    # Saving concatenated articles list to .xlsx file for checking concatenation
    df_articles_concat = pd.read_csv(path_concat_parsing / Path(articles_dat_alias), 
                                     sep="\t")
    df_articles_concat.to_excel(path_concat_parsing / Path(CONCATENATED_XLSX)) 
    print(f'\nConcatenated articles list file successfully saved as EXCEL file in: \n{path_concat_parsing}')

    # Getting rid of duplicates 
    df_articles_dedup, pub_id_to_drop = _deduplicate_articles(path_concat_parsing)

    # Saving deduplicated articles list to .xlsx file for checking deduplication
    df_articles_dedup.to_excel(path_rational_parsing / Path(DEDUPLICATED_XLSX))
    print(f'\nDeduplicated articles list file successfully saved as EXCEL file in: \n{path_rational_parsing}')    
      
    # Dropping the temporarily created column of normalized journal names in the deduplicated articles dataframe
    df_articles_dedup = df_articles_dedup.drop([norm_journal_alias], axis = 1)
    
    # Saving deduplicated articles list to .dat file  
    df_articles_dedup.to_csv(path_rational_parsing / Path(articles_dat_alias),
                             index=False,
                             sep='\t')
    print(f'\nArticles list file successfully deduplicated and saved in: \n{path_rational_parsing}')    

    # Updating and saving all other .dat files except the one of articles list
    files_list_wo_articles_dat = files_list
    files_list_wo_articles_dat.remove(articles_dat_alias)
    for file in files_list_wo_articles_dat: 
        _deduplicate_dat(file, pub_id_to_drop, path_concat_parsing, path_rational_parsing)
    print(f'\nOther parsing files successfully deduplicated and saved in: \n{path_rational_parsing}')

    
def _get_common_files(path_first_corpus,path_second_corpus):
    
    '''The `_common_files_new` builds a list of the names of the files present in the parsing folder 
    of two corpuses referenced as first_corpus and second_corpus. 
    
    Args : 
        path_first_corpus (path) : path of the folder where the files of the first_corpus are saved.
        path_second_corpus (path) : path of the folder where the files of the second_corpus are saved.
        
    Returns :
        (list): The list of common files.
        
    '''
        
    # Standard library imports
    import os
    
    # 3rd party library imports
    import pandas as pd
    
    def _list_dat(path_corpus):    
        list_dat =[file for file in os.listdir(path_corpus) if file.endswith('.dat')]            
        return list_dat
    
    list_dir_first_corpus=set(_list_dat(path_first_corpus))
    list_dir_second_corpus=set(_list_dat(path_second_corpus))

    common_list = list_dir_first_corpus.intersection(list_dir_second_corpus)    
    
    return common_list
    

def _concatenate_dat(filename, path_first_corpus, path_second_corpus, path_concat_result):
    
    '''The `_concatenate_dat` function concatenates the .dat files having the same name "filename" 
    in the parsing folders of two corpuses referenced as first corpus and second corpus.
     
    Args : 
        filename (string): name of the files to be concatenated.
        path_first_corpus (path): path of the folder where the .dat file "filename" is saved 
                                  for the first corpus.
        path_second_corpus (path): path of the folder where the .dat file "filename" is saved 
                                   for the second corpus.
        path_concat_result (path): path of the folder where the concatenated .dat file will be saved 
                            with the name "filename".
    
    '''
    # Standard libraries import
    from pathlib import Path

    # 3rd party library imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    pub_id_alias = COL_NAMES['pub_id']
    
    # Setting corpuses dataframes from "filename" file
    df_first_corpus = pd.read_csv(path_first_corpus / Path(filename), sep="\t")
    df_second_corpus = pd.read_csv(path_second_corpus / Path(filename), sep="\t")
    
    # Incrementing the "pub_id_alias" column values of second corpus by first corpus length 
    first_corpus_articles_nb = len(df_first_corpus)
    df_second_corpus[pub_id_alias] = df_second_corpus[pub_id_alias] + first_corpus_articles_nb
    
    # Cancatenating the two dataframes
    dfs_list = [df_second_corpus,df_first_corpus]
    df_concat = pd.concat(dfs_list)
    df_concat.sort_values([pub_id_alias],inplace=True)
    
    # Saving the concatenated dataframe 
    df_concat.to_csv(path_concat_result / Path(filename),
                             index=False,
                             sep='\t')
    

def _deduplicate_articles(path_in):
    
    '''The `_deduplicate_articles` uses the concatenated articles list and applies a succesion of filters
    to get rid of duplicated information.
    
    Args :
        path_in (string) : folder path where the .dat file of the concatenated articles list is available.
        
    Returns :
        (list): the list contains a dataframe of articles with no duplicates but unfull information, 
                a list of dataframes each of them containing a line that is a duplicate in the articles dataframe,
                and a list of the duplicate indices.
        
    Notes:
       The globals `BOLD_TEXT`, `LIGHT_TEXT`, `COL_NAMES`, `DIC_OUTDIR_PARSING`, 
       `LENGTH_THRESHOLD`, `SIMILARITY_THRESHOLD` and `UNKNOWN` are used.
    
    '''
    # Standard library imports
    from colorama import Fore
    from pathlib import Path
    from difflib import SequenceMatcher
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import BOLD_TEXT
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import LIGHT_TEXT
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import LENGTH_THRESHOLD
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SIMILARITY_THRESHOLD
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN
    
    def _find_value_to_keep(column_name):
        col_values_list = dg[column_name].to_list()
        col_values_list = list(dict.fromkeys(col_values_list)) 
        if UNKNOWN in col_values_list: col_values_list.remove(UNKNOWN) 
        value_to_keep = col_values_list[0] if len(col_values_list)>0 else UNKNOWN
        return value_to_keep 
    
    similar = lambda a,b:SequenceMatcher(None, a, b).ratio()
    
    # Defining aliases for text format control
    bold_text = BOLD_TEXT
    light_text = LIGHT_TEXT
    
    # Defining aliases for column names of the articles file (.dat)
    pub_id_alias = COL_NAMES['pub_id']
    author_alias = COL_NAMES['articles'][1]
    journal_alias = COL_NAMES['articles'][3]    
    doi_alias = COL_NAMES['articles'][6]
    doc_type_alias = COL_NAMES['articles'][7]
    title_alias = COL_NAMES['articles'][9]
    issn_alias = COL_NAMES['articles'][10]
    
    # Setting the name of a temporal column of titles in lower case 
    # to be added to working dataframes for case unsensitive dropping of duplicates
    lc_title_alias = COL_NAMES['temp_col'][0] 
    
    # Setting the name of a temporal column of journals normalized 
    # to be added to working dataframes for dropping of duplicates
    norm_journal_alias = COL_NAMES['temp_col'][1]
    
    # Setting alias for the articles file (.dat)
    articles_dat_alias = DIC_OUTDIR_PARSING['A']
    
    # Reading the articles file (.dat)
    df_articles_concat_init = pd.read_csv(path_in / Path(articles_dat_alias), 
                                         sep="\t") 
 
    # Setting same journal name for similar journal names                                            
    journals_list = df_articles_concat_init[journal_alias].to_list()
    df_journal = pd.DataFrame(journals_list, columns = [norm_journal_alias])
    for j1 in df_journal[norm_journal_alias]:     
        for j2 in df_journal[norm_journal_alias]:
            if j2 != j1 and (len(j1) > LENGTH_THRESHOLD and len(j2) > LENGTH_THRESHOLD):
                j1_set, j2_set = set(j1.split()), set(j2.split())
                common_words =  j2_set.intersection(j1_set)
                j1_specific_words, j2_specific_words = (j1_set - common_words), (j2_set - common_words)
                similarity = round(similar(j1,j2)*100)    
                if (similarity > SIMILARITY_THRESHOLD) or (j1_specific_words == set() or j2_specific_words == set()):
                    df_journal.loc[df_journal[norm_journal_alias] == j2] = j1
    df_articles_concat_inter = pd.concat([df_articles_concat_init, df_journal], axis = 1)
    
    # Setting issn when unknown for given article ID using available issn values 
    # of journals of same normalized names from other article IDs
    df_list = []
    for j, dg in df_articles_concat_inter.groupby(norm_journal_alias): 
        dg[issn_alias] = _find_value_to_keep(issn_alias)
        df_list.append(dg) 
    df_articles_concat = pd.concat(df_list)
        
    # Dropping duplicated article lines after merging by doi or, for unknown doi, by title and document type 
    df_list = []
    for doi, dg in df_articles_concat.groupby(doi_alias):
        if doi != UNKNOWN:
            # Deduplicating article lines by DOI
            dg[title_alias] = _find_value_to_keep(title_alias)
            dg[doc_type_alias] = _find_value_to_keep(doc_type_alias)
            dg.drop_duplicates(subset=[doi_alias],keep='first',inplace=True)
        else:
            # Deduplicating article lines without DOI by title and document type
                # Adding temporarily a column with lower-case titles for case-unsensitive duplicates droping 
            dg[lc_title_alias] = dg[title_alias].str.lower()
            dg.drop_duplicates(subset=[lc_title_alias,doc_type_alias],keep='first',inplace=True)
                # Dropping the temporarily created column of lower_case titles
            dg = dg.drop([lc_title_alias], axis = 1)
        df_list.append(dg)
    df_inter = pd.concat(df_list)
    
    # Dropping duplicated article lines after merging by titles, document type, first author and journal
        # Adding temporarily a column with lower-case titles for case_insensitive grouping
    df_inter[lc_title_alias] = df_inter[title_alias].str.lower() 
    df_list = []   
    for idx, dg in df_inter.groupby([lc_title_alias,doc_type_alias,norm_journal_alias]): 
        if len(dg)<3:
            # Deduplicating article lines with same title, document type, first author and journal
            # and also with same DOI if not UNKNOWN
            dg[doi_alias] = _find_value_to_keep(doi_alias)
            dg.drop_duplicates(subset=[doi_alias],keep='first',inplace=True)          
        else:   
            # Dropping article lines with DOI UNKNOWN from group of articles with same title, 
            # document type, first author and journal but different DOIs 
            unkown_indices = dg[dg[doi_alias]==UNKNOWN].index
            dg.drop(unkown_indices,inplace=True)
            pub_id_list = [x for x in dg[pub_id_alias]]
            warning = (f'WARNING: Multiple DOI values for same title, document type, first author and journal '
                                  f'are found in the group of article lines with IDs {pub_id_list} '
                                  f'in "_deduplicate_articles" function '
                                  f'called by "parsing_concatenate_deduplicate" function '
                                  f'of "BiblioParsingConcat.py" module.\n'
                                  f'Article lines with DOIs "{UNKNOWN}" has been droped.')                      
            print(Fore.BLUE + warning + Fore.BLACK)
        dg = dg.drop([lc_title_alias], axis = 1)
        df_list.append(dg) 
    if df_list != []:
        df_articles_dedup = pd.concat(df_list)
    else:
        df_articles_dedup = df_inter
    df_articles_dedup.sort_values([pub_id_alias], inplace=True)
    
    # Identifying the set of articles IDs to drop in the other parsing files of the concatenated corpus
    pub_id_set_init =  set(df_articles_concat[pub_id_alias].to_list())
    pub_id_set_end =  set(df_articles_dedup[pub_id_alias].to_list())    
    pub_id_to_drop = pub_id_set_init - pub_id_set_end 
    
    # Setting usefull prints
    articles_nb_init = len(df_articles_concat)    
    articles_nb_end = len(df_articles_dedup)
    articles_nb_drop = articles_nb_init - articles_nb_end
    
    print('\nDeduplication results:')
    print(f'    Initial articles number: {articles_nb_init}')
    print(f'    Final articles number: {articles_nb_end}')
    warning = (f'    WARNING: {articles_nb_drop} articles have been dropped as duplicates')
    print(Fore.BLUE +  bold_text + warning + light_text + Fore.BLACK)
                                
    return df_articles_dedup, pub_id_to_drop


def _deduplicate_dat(file_name, pub_id_to_drop, path_in, path_out ):
    
    '''The `deduplicate_dat`function drops the lines corresponding to `pub_id_to_drop' list of articles IDs
    in the '.dat' files issued from concatenation of parsing files of corpuses, exept the one of articles list.
    
    Args : 
       file_name (str): The name of the file among the '.dat' files issued from concatenation of parsing files 
                        of corpuses
        
    Returns :
        Nothing, but saves documents in path'''
    
    # 3rd party imports   
    import pandas as pd
    from pathlib import Path
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    
    # Defining aliases for column names of the file_name file 
    pub_id_alias = COL_NAMES['pub_id']
        
    df = pd.read_csv(path_in / Path(file_name), sep="\t")
    
    filt = (df[pub_id_alias].isin(pub_id_to_drop))
    df = df[~filt]
    df.sort_values([pub_id_alias], inplace=True)

    if file_name == DIC_OUTDIR_PARSING['AU']:
        idx_author_alias = COL_NAMES['authors'][1]
        df.sort_values([pub_id_alias,idx_author_alias], inplace=True)
    if file_name == DIC_OUTDIR_PARSING['AD']:
        idx_address_alias = COL_NAMES['address'][1]
        df.sort_values([pub_id_alias,idx_address_alias], inplace=True)        
    if file_name == DIC_OUTDIR_PARSING['CU']:
        idx_address_alias = COL_NAMES['country'][1]
        df.sort_values([pub_id_alias,idx_address_alias], inplace=True)
    if file_name == DIC_OUTDIR_PARSING['I']:
        idx_address_alias = COL_NAMES['institution'][1]
        df.sort_values([pub_id_alias,idx_address_alias], inplace=True) 
    if file_name == DIC_OUTDIR_PARSING['I2']:
        idx_author_alias = COL_NAMES['auth_inst'][1]
        df.sort_values([pub_id_alias,idx_author_alias], inplace=True)
            
    df.to_csv(path_out / Path(file_name),
              index=False,
              sep='\t')

    
