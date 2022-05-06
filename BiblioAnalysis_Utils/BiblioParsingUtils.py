__all__ = ['biblio_parser',
           'build_institutions_dic',
           'build_title_keywords',
           'check_and_drop_columns',
           'country_normalization',
           'extend_author_institutions',
           'getting_secondary_inst_list',
           'merge_database',
           'name_normalizer',
           'normalize_journal_names',
           'setting_secondary_inst_filter',
           'upgrade_col_names',
           ]

# 
# Globals used from BiblioAnalysis_Utils.BiblioGeneralGlobals:  ALIAS_UK, CHANGE, COUNTRIES,
# Globals used from BiblioAnalysis_Utils.BiblioSpecificGlobals: BLACKLISTED_WORDS, COL_NAMES,
#                                                               DIC_INST_FILENAME, DIC_LOW_WORDS, DIC_OUTDIR_PARSING ,              
#                                                               INST_FILTER_LIST, REP_UTILS, 
#                                                               NLTK_VALID_TAG_LIST, NOUN_MINIMUM_OCCURRENCES,
#                                                               RE_NUM_CONF, RE_YEAR_JOURNAL,
#                                                               SCOPUS, USECOLS_SCOPUS, WOS

# Functions used from BiblioAnalysis_Utils.BiblioGui: Select_multi_items
# Functions used from BiblioAnalysis_Utils.BiblioParsingScopus: biblio_parser_scopus
# Functions used from BiblioAnalysis_Utils.BiblioParsingWos: biblio_parser_wos


def build_title_keywords(df):
    
    '''Given the dataframe 'df' with one column 'title':
    
                    Title
            0  Experimental and CFD investigation of inert be...
            1  Impact of Silicon/Graphite Composite Electrode...
            
    the function 'build_title_keywords':
    
       1- Builds the set "keywords_TK" of the tokens appearing at least NOUN_MINIMUM_OCCURRENCE times 
    in all the article titles of the corpus. The tokens are the words of the title with nltk tags 
    belonging to the global list 'NLTK_VALID_TAG_LIST'.
       2- Adds two columns 'token' and 'pub_token' to the dataframe 'df'. The column 'token' contains
    the set of the tokenized and lemmelized (using the nltk WordNetLemmatizer) title. The column
    'pub_token' contains the list of words common to the set "keywords_TK" and to the column 'kept_tokens'
       3- Buids the list of tuples 'list_of_words_occurrences.sort'
    [(token_1,# occurrences token_1), (token_2,# occurrences token_2),...] ordered by decreasing values
    of # occurrences token_i.
       4- Suppress words pertening to BLACKLISTED_WORDS to the list  from the bag of words
    
    Args:
       df (dataframe): pub_id | Title 
       
    Returns:
       df (dataframe): pub_id | title_token | kept_tokens where title_token is the list of token of the title
         and kept_token the list of tokens with a frequency occurrence >= NOUN_MINIMUM_OCCURRENCES
       bag_of_words_occurrences (list of tuples): [(word_1,# occurrence_1), (word_2,# occurrence_2), ...]
        
    '''

    # Standard library imports
    import operator
    from collections import Counter
       
    # 3rd party imports
    import nltk
    import numpy as np
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import NLTK_VALID_TAG_LIST
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import NOUN_MINIMUM_OCCURRENCES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import BLACKLISTED_WORDS
    
    def tokenizer(text):
        
        '''
        Tokenizes, lemmelizes the string 'text'. Only the words with nltk tags in the global
        NLTK_VALID_TAG_LIST are kept.
        
        ex 'Thermal stability of Mg2Si0.55Sn0.45 for thermoelectric applications' 
        gives the list : ['thermal', 'stability', 'mg2si0.55sn0.45', 'thermoelectric', 'application']
        
        Args:
            text (string): string to tokenize
            
        Returns
            The list valid_words_lemmatized 
        '''
            
        tokenized = nltk.word_tokenize(text.lower())
        valid_words = [word for (word, pos) in nltk.pos_tag(tokenized) 
                       if pos in NLTK_VALID_TAG_LIST] 

        stemmer = nltk.stem.WordNetLemmatizer()
        valid_words_lemmatized = [stemmer.lemmatize(valid_word) for valid_word in valid_words]
    
        return valid_words_lemmatized        

    df['title_token'] = df['Title'].apply(tokenizer)

    bag_of_words = np.array(df.title_token.sum()) # remove the blacklisted words from the bag of words
    for remove in BLACKLISTED_WORDS:
        bag_of_words = bag_of_words[bag_of_words != remove] 

    bag_of_words_occurrences = list(Counter(bag_of_words).items())
    bag_of_words_occurrences.sort(key = operator.itemgetter(1),reverse=True)

    keywords_TK = set([x for x,y in bag_of_words_occurrences if y>=NOUN_MINIMUM_OCCURRENCES])
    
    df['kept_tokens'] = df['title_token'].apply(lambda x :list(keywords_TK.intersection(set(x))))
   
    return df,bag_of_words_occurrences

def country_normalization(country):
    '''
    Normalize the country name for coherence seeking between wos and scopus corpuses.
    '''

    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import ALIAS_UK
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import COUNTRIES
    
    country_clean = country
    if country not in COUNTRIES:
        if country in  ALIAS_UK:
            country_clean = 'United Kingdom'
        elif 'USA' in country:
            country_clean = 'United States'
        elif ('china' in country) or ('China' in country):
            country_clean = 'China'
        elif country == 'Russia':    
            country_clean = 'Russian Federation'
        elif country == 'U Arab Emirates':    
            country_clean = 'United Arab Emirates'
        elif country == 'Vietnam':   
            country_clean = 'Viet Nam'
        else:
            country_clean = ''

    return country_clean


def build_institutions_dic(rep_utils = None, dic_inst_filename = None):
    '''
    The `builds_institutions_dic` fuction builds the dict 'inst_dic' 
    giving the mormalized names of institutions from a csv file `dic_inst_filename`.
    The name of the csv file is set in the `DIC_INST_FILENAME` global.
    
    Args: 
        rep_utils (str): name of the folder where the csv file is stored
        dic_inst_filename (str): name of the csv file.        
    
    Returns:       
        `dict`: `inst_dic` as {raw_inst:norm_inst} where 
                - raw_inst a raw institution name 
                - norm_inst is the normalized institution name.
        
    Note:
        The globals `REP_UTILS` and `DIC_INST_FILENAME` are used.
    
    '''

    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals  import DIC_INST_FILENAME
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import REP_UTILS    
    
    if dic_inst_filename == None: dic_inst_filename = DIC_INST_FILENAME
    if rep_utils == None: rep_utils = REP_UTILS 
    
    # Setting the file path for dic_inst_filename file reading    
    path_dic_inst = Path(__file__).parent / rep_utils / Path(dic_inst_filename)
    
    # Reading and cleaning the dic_inst_filename file
    inst_dic = pd.read_csv(path_dic_inst,sep=':',header=None)
    inst_dic.sort_values([0],inplace=True)
    inst_dic[0] = inst_dic[0].str.strip()
    inst_dic[1] = inst_dic[1].str.strip()
    inst_dic = dict(zip(inst_dic[0],inst_dic[1]))
    
    return inst_dic


def setting_secondary_inst_filter(out_dir_parsing):
    '''The `setting_secondary_inst_filter` function allows building the affiliation filter "inst_filter_list"
    fron the institutions list of the corpus using the `Select_multi_items` GUI.
    
    Args:
        out_dir_parsing (path): the corpus parsing path for reading the "DIC_OUTDIR_PARSING['I2']" file.
        
    Returns:
        (list): list of tuples (institution,country) selected by the user.
        
    Notes:
        The globals 'COL_NAMES'and 'DIC_OUTDIR_PARSING' are used.
        The function `Select_multi_items`is used from `BiblioAnalysis_utils` package.
        
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import numpy as np
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGui import Select_multi_items
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    
    
    institutions_alias = COL_NAMES['auth_inst'][4]
    country_alias = COL_NAMES['country'][2]    
    
    df_auth_inst = pd.read_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING['I2']),
                                sep = '\t')
    raw_institutions_list = []
    for auth_inst in df_auth_inst[institutions_alias]:
        raw_institutions_list.append(auth_inst)
        
    institutions_list = list(np.concatenate([raw_inst.split(';') for raw_inst in raw_institutions_list]))
    institutions_list  = sorted(list(set(institutions_list)))

    country_institution_list = [x.split('_')[1] + ':' + x.split('_')[0] for x in institutions_list]
    country_institution_list = sorted(country_institution_list)

    selected_list = Select_multi_items(country_institution_list,
                                       mode='multiple',
                                       fact=2,
                                       win_widthmm=80,
                                       win_heightmm=100,
                                       font_size=16)

    inst_filter_list = [(x.split(':')[1].strip(),x.split(':')[0].strip()) for x in selected_list]
    
    return inst_filter_list


def merge_database(database,filename,in_dir,out_dir):
    
    '''Merges several databases in one database
    
    Args:
        database (string): database type (scopus or wos)
        filename (str): name of the merged database
        in_dir (str): name of the folder where the databases are stored
        out_dir (str): name of the folder where the merged databases will be stored
    
    Notes:
        The USECOLS_SCOPUS global is used.
        
    '''
    # Standard library imports
    import os
    from pathlib import Path
    import sys

    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import USECOLS_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import WOS

    list_data_base = []
    list_df = []
    if database == WOS:
        for path, _, files in os.walk(in_dir):
            list_data_base.extend(Path(path) / Path(file) for file in files
                                                          if file.endswith(".txt"))
        for file in list_data_base:
            list_df.append(read_database_wos(file))

    elif database == SCOPUS:
        for path, _, files in os.walk(in_dir):
            list_data_base.extend(Path(path) / Path(file) for file in files
                                                          if file.endswith(".csv"))
        for file in list_data_base:
            df = pd.read_csv(file,usecols=USECOLS_SCOPUS) # reads the database
            list_df.append(df)
            
    else:
        raise Exception(f"Sorry, unrecognized database {database} : should be {WOS} or {SCOPUS} ")
        
    result = pd.concat(list_df,ignore_index=True)
    result.to_csv(out_dir / Path(filename),sep='\t')

def name_normalizer(text):
    
    '''Normalizes the author name spelling according the three debatable rules:
            - replacing none ascii letters by ascii ones
            - capitalizing first name 
            - capitalizing surnames
            - supressing comma and dot
            
       ex: name_normalizer(" GrÔŁ-biçà-vèLU D'aillön, E-kj. ")
        >>> "Grol-Bica-Velu D'Aillon E-KJ"
        
    Args:
        text (str): text to normalize
    
    Returns
        The normalized text
        
    Notes:
        The CHANGE global is used.
    '''

    # Standard library imports
    import functools
    import re
    import unicodedata
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import CHANGE

    nfc = functools.partial(unicodedata.normalize,'NFD')
    
    text = text.translate(CHANGE) # Translate special character using global CHANGE dict
    text = nfc(text). \
           encode('ascii', 'ignore'). \
           decode('utf-8').\
           strip()
    
    re_minus = re.compile('(-[a-zA-Z]+)')       # Captures: "cCc-cC-ccc-CCc"
    for text_minus_texts in re.findall(re_minus,text):
        text = text.replace(text_minus_texts,'-' + text_minus_texts[1:].capitalize() )
    
    re_apostrophe = re.compile("('[a-zA-Z]+)")  # Captures: "cCc'cC'ccc'cc'CCc"
    for text_minus_texts in re.findall(re_apostrophe,text):
        text = text.replace(text_minus_texts,"'" + text_minus_texts[1:].capitalize() )
        
    re_minus = re.compile('([a-zA-Z]+-)')       # Captures: "cCc-" 
    for text_minus_texts in re.findall(re_minus,text):
        text = text.replace(text_minus_texts,text_minus_texts[:-1].capitalize() + '-')
        
    re_apostrophe = re.compile("([a-zA-Z]+')")  # Captures: "cCc'"
    for text_minus_texts in re.findall(re_apostrophe,text):
        text = text.replace(text_minus_texts,text_minus_texts[:-1].capitalize() + "'")
        
    re_surname = "[a-zA-Z]+\s"                  # Captures: "cCccC "
    for text_minus_texts in re.findall(re_surname,text):
        text = text.replace(text_minus_texts,text_minus_texts.capitalize())
        
    re_minus_first_name = '\s[a-zA-Z]+-[a-zA-Z]+$'     # Captures: "cCc-cC" in the first name
    for x in  re.findall(re_minus_first_name,text):
        text = text.replace(x,x.upper())
           
    return text


def normalize_journal_names(database,df_corpus):
    '''The `normalize_journal_names` function normalizes the journal names in the journals specific column 
    of the corpus dataframe through the replace of low words defined in the global 'DIC_LOW_WORDS' 
    and the drop of particular items using the regular expressions defined by 'RE_ADDS_JOURNAL' and 'RE_YEAR_JOURNAL'
    globals.
    
    Args:
        database (string): type of database among the ones defined by SCOPUS and WOS globals.
        df_corpus (dataframe): corpus dataframe to be normalized in terms of journal names.
        
    Returns:
        (dataframe): the dataframe with normalized journal names.
        
    Note:
        The globals 'COLUMN_LABEL_WOS', 'COLUMN_LABEL_SCOPUS','DIC_LOW_WORDS', 'RE_YEAR_JOURNAL', 'SCOPUS' and 'WOS' are used.
    
    '''
    # Standard library imports
    import re
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS 
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_LOW_WORDS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_NUM_CONF
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_YEAR_JOURNAL
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import WOS
    
   
    def _normalize_low_words(text): 
        for low_word in DIC_LOW_WORDS.keys():
            text = text.replace(low_word, DIC_LOW_WORDS[low_word]).strip()
        text = " ".join(text.split())
        return text

    def _journal_normalizer(journal):
        journal = ' ' + journal + ' '
        journal = journal.lower()
        journal_list = [" " + x + " " for x in journal.split()]
        new_journal = " ".join(journal_list)
        if RE_YEAR_JOURNAL.findall(journal) or RE_NUM_CONF.findall(journal): 
            to_remove = [x for x in journal_list if (RE_YEAR_JOURNAL.findall(x) or RE_NUM_CONF.findall(x))]
            for x in to_remove: new_journal = new_journal.replace(x,'')
        new_journal = " ".join(new_journal.split())
        new_journal = _normalize_low_words(new_journal) 
        return new_journal
    
    if database == WOS:
        journal_alias = COLUMN_LABEL_WOS['journal']
    elif database == SCOPUS:
        journal_alias = COLUMN_LABEL_SCOPUS['journal']
    else:
        raise Exception(f"Sorry, unrecognized database {database}: should be {WOS} or {SCOPUS} ") 
    
    df_corpus[journal_alias] = df_corpus[journal_alias].apply(_journal_normalizer)
    
    return df_corpus


def biblio_parser(in_dir_parsing, out_dir_parsing, database, expert, rep_utils=None, inst_filter_list=None):
    
    '''Chooses the appropriate parser to parse wos or scopus databases.
    '''
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingScopus import biblio_parser_scopus
    from BiblioAnalysis_Utils.BiblioParsingWos import biblio_parser_wos
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import INST_FILTER_LIST
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import REP_UTILS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import WOS
    
    if database == WOS:
        biblio_parser_wos(in_dir_parsing, out_dir_parsing, inst_filter_list)
    elif database == SCOPUS:
        if rep_utils == None: rep_utils = REP_UTILS
        biblio_parser_scopus(in_dir_parsing, out_dir_parsing, rep_utils, inst_filter_list)
    else:
        raise Exception(f"Sorry, unrecognized database {database} : should be wos or scopus ")

def check_and_drop_columns(database,df,filename):

    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS 
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import WOS

    # Check for missing mandatory columns
    if database == WOS:
        cols_mandatory = set([val for val in COLUMN_LABEL_WOS.values() if val])
    elif database == SCOPUS:
        cols_mandatory = set([val for val in COLUMN_LABEL_SCOPUS.values() if val])    
    else:
        raise Exception(f"Sorry, unrecognized database {database} : should be {WOS} or {SCOPUS} ")
        
    cols_available = set(df.columns)
    missing_columns = cols_mandatory.difference(cols_available)
    if missing_columns:
        raise Exception(f'The mandarory columns: {",".join(missing_columns)} are missing from {filename}\nplease correct before proceeding')
    
    # Columns selection and dataframe reformatting
    cols_to_drop = list(cols_available.difference(cols_mandatory))
    df.drop(cols_to_drop,
            axis=1,
            inplace=True)                    # Drops unused columns
    df.index = range(len(df))                # Sets the pub_id in df index
    
    return df

                    
def upgrade_col_names(corpus_folder):
    
    '''Add names to the colummn of the parsing and filter_<i> files to take into account the
    upgrage of BiblioAnalysis_Utils.
    
    Args:
        corpus_folder (str): folder of the corpus to be adapted
    '''
    # Standard library imports
    import os
    
    # 3rd party imports
    import colorama
    import pandas as pd
    from colorama import Back
    from colorama import Fore
    from colorama import Style
    from pandas.core.groupby.groupby import DataError
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    
    # Beware: the new file authorsinst.dat is not present in the old parsing folders
    dict_filename_conversion  = {'addresses.dat':'address',
                                'articles.dat': 'articles',
                                'authors.dat':'authors',
                                'authorsinst.dat':'auth_inst',
                                'authorskeywords.dat':'keywords',
                                'countries.dat':'country',
                                'institutions.dat':'institution',
                                'journalkeywords.dat':'keywords',
                                'references.dat':'references',
                                'subjects.dat': 'subject',
                                'subjects2.dat':'sub_subject',
                                'titlekeywords.dat':'keywords'}

    for dirpath, dirs, files in os.walk(corpus_folder):  
        if ('parsing' in   dirpath) |  ('filter_' in  dirpath):
            for file in  [file for file in files
                          if (file.split('.')[1]=='dat') 
                          and (file!='database.dat')      # Not used this file is no longer generated
                          and (file!='keywords.dat') ]:   # Not used this file is no longer generated
                try:
                    df = pd.read_csv(os.path.join(dirpath,file),sep='\t',header=None)
                    
                    if df.loc[0].tolist() == COL_NAMES[dict_filename_conversion[file]]:
                        print(f'The file {os.path.join(dirpath,file)} is up to date')
                    else:
                        df.columns = COL_NAMES[dict_filename_conversion[file]]
                        df.to_csv(os.path.join(dirpath,file),sep='\t',index=False)
                        print(Fore.GREEN + f'*** The file {os.path.join(dirpath,file)} has been upgraded ***' + Style.RESET_ALL)
                except  pd.errors.EmptyDataError:
                    df = pd.DataFrame(columns=COL_NAMES[dict_filename_conversion[file]])
                    df.to_csv(os.path.join(dirpath,file),sep='\t',index=False)
                    print(Fore.BLUE + f'*** The EMPTY file {os.path.join(dirpath,file)} has been upgraded ***' + Style.RESET_ALL)
                except:
                    print(Fore.WHITE + Back.RED + f'Warning: File {os.path.join(dirpath,file)} not recognized as a parsing file' + Style.RESET_ALL)

                
def extend_author_institutions(in_dir,inst_filter_list):
    ''' The `extend_author_institutions`function extends the .dat file of authors with institutions 
    initialy obtained by the parsing of the corpus, with complementary information about institutions
    selected by the user.
    
    Args:
        in_dir (path): path to the .dat file of authors with institutions
        inst_filter_list (list): the affiliation filter list of tuples (institution, country) 

    Retruns:
        None
        
    Notes:
        The globals 'COL_NAMES' and 'DIC_OUTDIR_PARSING' are used
        from `BiblioAnalysis_utils` package.
    
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    
    def _address_inst_list(inst_names_list,institutions):

        secondary_institutions = []
        for inst in inst_names_list:
            if inst in institutions:
                secondary_institutions.append(1)
            else:
                secondary_institutions.append(0)  
             
        return secondary_institutions
    
    institutions_alias = COL_NAMES['auth_inst'][4]
    sec_institutions_alias = COL_NAMES['auth_inst'][5]
    
    # Setting the key for the name of the '.dat' file of authors with institutions 
    # obtained by parsing the corpus
    item = 'I2' 
    
    # Reading the '.dat' file                   
    read_usecols = [COL_NAMES['auth_inst'][x] for x in [0,1,2,3,4]]     
    df_I2= pd.read_csv(in_dir / Path(DIC_OUTDIR_PARSING[item]),
                     sep='\t',
                     usecols=read_usecols)
    
    # Setting an institution name for each of the institutions indicated in the institutions filter
    inst_names_list = [f'{x[0]}_{x[1]}' for x in inst_filter_list]   
    
    # Building the "sec_institution_alias" column in the 'df_I2' dataframe using "inst_filter_list"
    df_I2[sec_institutions_alias] = df_I2.apply(lambda row:
                                             _address_inst_list(inst_names_list,row[institutions_alias]),
                                             axis = 1)

    # Distributing in a 'df_inst_split' df the value lists of 'df_I2[sec_institutions_alias]' column  
    # into columns which names are in 'inst_names_list' list     
    df_inst_split = pd.DataFrame(df_I2[sec_institutions_alias].sort_index().to_list(),
                                          columns=inst_names_list)
    
    # Extending the 'df' dataframe with 'df_inst_split' dataframe
    df_I2 = pd.concat([df_I2, df_inst_split], axis=1)

    # Droping the 'df[sec_institutions_alias]' column which is no more usefull
    df_I2.drop([sec_institutions_alias], axis=1, inplace=True)
    
    # Saving the extended 'df_I2' dataframe in the same '.dat' file 
    df_I2.to_csv(in_dir/ Path(DIC_OUTDIR_PARSING[item]), 
                 index=False,
                 sep='\t') 
    
    
def getting_secondary_inst_list(out_dir_parsing):
    '''The `getting_secondary_inst_list` function provides the list of institutions of the corpus.
   
    Args:
        out_dir_parsing (path): the corpus parsing path for reading the "DIC_OUTDIR_PARSING['I2']" file 
                                that lists the authors with their institutions for each article.
       
    Returns:
        (list): list of strings 'country:institution'
       
    Notes:
        The globals 'COL_NAMES'and 'DIC_OUTDIR_PARSING' are used.       
    '''
   
    # Standard library imports
    from pathlib import Path
   
    # 3rd party imports
    import numpy as np
    import pandas as pd
   
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
   
    
    institutions_alias = COL_NAMES['auth_inst'][4]
    country_alias = COL_NAMES['country'][2]   
    
    df_auth_inst = pd.read_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING['I2']),
                                sep = '\t')
    raw_institutions_list = []
    for auth_inst in df_auth_inst[institutions_alias]:
        raw_institutions_list.append(auth_inst)
       
    institutions_list = list(np.concatenate([raw_inst.split(';') for raw_inst in raw_institutions_list]))
    institutions_list  = sorted(list(set(institutions_list)))
 
    country_institution_list = [x.split('_')[1] + ':' + x.split('_')[0] for x in institutions_list]
    country_institution_list = sorted(country_institution_list)
   
    return country_institution_list
            
            
            