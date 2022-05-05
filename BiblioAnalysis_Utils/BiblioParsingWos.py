__all__ = ['biblio_parser_wos','read_database_wos']

# Globals used from BiblioAnalysis_Utils.BiblioSpecificGlobals: DIC_OUTDIR_PARSING, DIC_DOCTYPE, 
#                                                               ENCODING, FIELD_SIZE_LIMIT,
#                                                               RE_ADDRESS, RE_AUTHOR,
#                                                               RE_REF_AUTHOR_WOS, RE_REF_JOURNAL_WOS,
#                                                               RE_REF_PAGE_WOS, RE_REF_VOL_WOS, 
#                                                               RE_REF_YEAR_WOS, RE_SUB, SYMBOL, 
#                                                               UNKNOWN, USECOLS_WOS, WOS

# Functions used from BiblioAnalysis_Utils.BiblioParsingUtils: build_title_keywords, build_institutions_dic
#                                                              country_normalization, normalize_journal_names, name_normalizer 
                                                              


def _build_authors_wos(df_corpus):
    
    '''Builds the dataframe "df_co_authors" of the co-authors of the article
    referenced with the key publi_id:
    
               pub_id  idx_author   co-author
          0        0      0          Boujjat H.
          1        0      1          Rodat S.

    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus

    Returns:
        The dataframe df_country
    '''

    # Standard library imports
    from collections import namedtuple
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import name_normalizer
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS
    
    co_author = namedtuple('co_author',COL_NAMES['authors'] )
    
    authors_alias = COL_NAMES['authors'][2]
    
    list_author = []
    for pub_id,x in zip(df_corpus.index,
                        df_corpus[COLUMN_LABEL_WOS['authors']]):
        idx_author = 0
        for y in x.split(';'):
            author = name_normalizer(y.replace('.','').replace(',',''))  # <----- to be checked
            if author not in ['Dr','Pr','Dr ','Pr ']:
                list_author.append(co_author(pub_id,
                                             idx_author,
                                             author))
                idx_author += 1
    
    df_co_authors = pd.DataFrame.from_dict({label:[s[idx] for s in list_author] 
                                            for idx,label in enumerate(COL_NAMES['authors'])})
    df_co_authors = df_co_authors[df_co_authors[authors_alias] != ''] 
    
    return df_co_authors


def _build_keywords_wos(df_corpus,dic_failed):
    
    '''Builds the dataframe "df_keyword" with three columns:
                pub_id  type  keyword
            0     0      AK    Biomass
            1     0      AK    Gasification
            2     0      AK    Solar energy
    with: 
         type = AK for author keywords 
         type = IK for journal keywords
         type = TK for title keywords
         
    The title keywords are builds out of the set TK_corpus of the most cited nouns 
    (at leat N times) in the set of all the articles. The keywords of type TK of an
    article, referenced by the key pub_id, are the elements of the intersection
    between the set TK_corpus and the set of the nouns of the article title.
    
        
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus

    Returns:
        df_keyword (dataframe): pub_id | type | keyword 
        dic_failed (dict): dic_failed[type] = {"success (%)":rate of success,
                            "pub_id":list of orphan article}
    '''
    
    # Standard library imports
    from collections import namedtuple
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import build_title_keywords    
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN

    key_word = namedtuple('key_word',COL_NAMES['keywords'] )
    
    pub_id_alias = COL_NAMES['keywords'][0]
    type_alias = COL_NAMES['keywords'][1]
    keyword_alias = COL_NAMES['keywords'][1]
    
    list_keyword_AK = [] 
    df_AK = df_corpus[COLUMN_LABEL_WOS['author_keywords']].fillna('')
    for pub_id,keywords_AK in zip(df_AK.index,df_AK):
        list_keywords_AK = keywords_AK.split(';')      
        for keyword_AK in list_keywords_AK:
            keyword_AK = keyword_AK.lower().strip()
            list_keyword_AK.append(key_word(pub_id,
                                   keyword_AK if keyword_AK != 'null' else '”null”'))

    list_keyword_IK = []
    df_IK = df_corpus[COLUMN_LABEL_WOS['index_keywords']].fillna('')
    for pub_id,keywords_IK in zip(df_IK.index,df_IK):
        list_keywords_IK = keywords_IK.split(';')
        for keyword_IK in list_keywords_IK:
            keyword_IK = keyword_IK.lower().strip()
            if keyword_IK == 'null': keyword_IK = UNKNOWN # replace 'null' by the keyword UNKNOWN
            list_keyword_IK.append(key_word(pub_id,
                                            keyword_IK if keyword_IK != 'null' else '”null”'))
            
    list_keyword_TK = []
    df_title = pd.DataFrame(df_corpus[COLUMN_LABEL_WOS['title']].fillna('')) # Tranform a data list into dataframe
    df_title.columns = ['Title']  # To be coherent with the convention of function build_title_keywords
    df_TK,list_of_words_occurrences = build_title_keywords(df_title)
    for pub_id in df_TK.index:
        for token in df_TK.loc[pub_id,'kept_tokens']:
            token = token.lower().strip()
            list_keyword_TK.append(key_word(pub_id,
                                         token if token != 'null' else '”null”'))                                    
    
    df_keyword_AK = pd.DataFrame.from_dict({label:[s[idx] for s in list_keyword_AK] 
                                         for idx,label in enumerate(COL_NAMES['keywords'])})
    df_keyword_IK = pd.DataFrame.from_dict({label:[s[idx] for s in list_keyword_IK] 
                                         for idx,label in enumerate(COL_NAMES['keywords'])})
    df_keyword_TK = pd.DataFrame.from_dict({label:[s[idx] for s in list_keyword_TK] 
                                         for idx,label in enumerate(COL_NAMES['keywords'])})
    
    df_failed_AK = df_keyword_AK[df_keyword_AK[keyword_alias] == '']
    list_id = df_failed_AK[pub_id_alias].values
    dic_failed['AK'] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                            pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_failed_IK = df_keyword_IK[df_keyword_IK[keyword_alias] == '']
    list_id = df_failed_IK[pub_id_alias].values
    dic_failed['IK'] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                            pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_failed_TK = df_keyword_TK[df_keyword_TK[keyword_alias] == '']
    list_id = df_failed_TK[pub_id_alias].values
    dic_failed['TK'] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                            pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_keyword_AK = df_keyword_AK[df_keyword_AK[keyword_alias] != '']
    df_keyword_IK = df_keyword_IK[df_keyword_IK[keyword_alias] != '']
    df_keyword_TK = df_keyword_TK[df_keyword_TK[keyword_alias] != '']    
    
    return df_keyword_AK,df_keyword_IK, df_keyword_TK


def _build_addresses_countries_institutions_wos(df_corpus,dic_failed):
    
    '''Parse the field 'C1' of wos database to retrieve the article author address (without duplicates),
       the author country and affiliation. Beware, multiple formats may exist for the 'C1' field. 
       We take care for two different formats in this implementation.
       
    For example the string:

    '[Boujjat, Houssame] CEA, LITEN Solar & Thermodynam Syst Lab L2ST, F-38054 Grenoble, France;
     [Boujjat, Houssame] Univ Grenoble Alpes, F-38000 Grenoble, France; 
     [Rodat, Sylvain; Chuayboon, Srirat; Abanades, Stephane] CNRS, Proc Mat & Solar Energy Lab,
     PROMES, 7 Rue Four Solaire, F-66120 Font Romeu, France'

       will be parsed in:
    
    df_address:
    
    pub_id  idx_address                     address   
        0       0        CEA, LITEN Solar & Thermodynam Syst Lab L2ST, ...
        0       1        Univ    Grenoble Alpes, F-38000 Grenoble, France;
        0       2        CNRS,   Proc Mat & Solar Energy Lab, PROMES, 7 ...
    
    df_country:
        
    pub_id  idx_author   country
      0        0         France
      0        1         France
      0        2         France
      0        3         France
      0        4         France
      
   df_institution: 
   
   pub_id  idx_author   institution
     0       0          CEA
     0       1          University Grenoble Alpes
     0       2          CNRS
     0       3          CNRS
     0       4          CNRS

    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus.

    Returns:
        The dataframe df_address, df_country, df_institution.
        
    Notes:
        The globals 'COL_NAMES', 'COLUMN_LABEL_WOS', 'RE_ADDRESS', 'RE_AUTHOR' and 'RE_SUB' are used.
        The function `country_normalization`is used from `BiblioAnalysis_utils` package.
    '''

    # Standard library imports
    import re
    from colorama import Fore
    from collections import namedtuple
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import country_normalization
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_ADDRESS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_AUTHOR
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_SUB
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN

    address = namedtuple('address',COL_NAMES['address'] )
    country = namedtuple('country',COL_NAMES['country'] )
    institution = namedtuple('institution', COL_NAMES['institution'] )
      
    pub_id_alias = COL_NAMES['address'][0]
    address_alias = COL_NAMES['address'][2]
    country_alias = COL_NAMES['country'][2]
    institution_alias = COL_NAMES['institution'][2]

    list_addresses = []
    list_countries = []
    list_institutions = []

    for pub_id, affiliation in zip(df_corpus.index,
                                   df_corpus[COLUMN_LABEL_WOS['authors_with_affiliations']]):
        
        try:
            if '[' in affiliation:                           # ex: '[Author1] address1;[Author1, Author2] address2...'
                #authors = RE_AUTHOR.findall(affiliation)    # for future use
                addresses = RE_ADDRESS.findall(affiliation)
            else:                                            # ex: 'address1;address2...'
                addresses = affiliation.split(';')   
        except:
            print(pub_id,affiliation)
        
        if addresses:
            for idx, author_address in enumerate(addresses): 

                list_addresses.append(address(pub_id,
                                              idx,
                                              author_address))

                author_institution_raw = author_address.split(',')[0]
                author_institution = re.sub(RE_SUB,'University'+' ', author_institution_raw)
                list_institutions.append(institution(pub_id,
                                                     idx,
                                                     author_institution))

                author_country_raw = author_address.split(',')[-1].replace(';','').strip()
                author_country = country_normalization(author_country_raw)
                if author_country == '':
                    author_country = UNKNOWN
                    warning = (f'WARNING: the invalid country name "{author_country_raw}" '
                               f'in pub_id {pub_id} has been replaced by "{UNKNOWN}" '
                               f'in "_build_addresses_countries_institutions_wos" function of "BiblioParsingWos.py" module')
                    print(Fore.BLUE + warning + Fore.BLACK)

                list_countries.append(country(pub_id,
                                              idx,
                                              author_country))
        else:
            list_addresses.append(address(pub_id,
                                          0,
                                          ''))
            list_institutions.append(institution(pub_id,
                                                 0,
                                                 ''))
            list_countrieslist_countries.append(country(pub_id,
                                                        0,
                                                        ''))
            
    df_address = pd.DataFrame.from_dict({label:[s[idx] for s in list_addresses] 
                                         for idx,label in enumerate(COL_NAMES['address'])})

    df_country = pd.DataFrame.from_dict({label:[s[idx] for s in list_countries] 
                                         for idx,label in enumerate(COL_NAMES['country'])})

    df_institution = pd.DataFrame.from_dict({label:[s[idx] for s in list_institutions] 
                                             for idx,label in enumerate(COL_NAMES['institution'])})
    
    list_id = df_address[df_address[address_alias] == ''][pub_id_alias].values
    list_id = list(set(list_id))
    dic_failed[address_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                 pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_address = df_address[df_address[address_alias] != '']

    list_id = df_country[df_country[country_alias] == ''][pub_id_alias].values
    list_id = list(set(list_id))
    dic_failed[country_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                 pub_id_alias:[int(x) for x in list(list_id)]}
    df_country = df_country[df_country[country_alias] != '']
    
    list_id = df_institution[df_institution[institution_alias] == ''][pub_id_alias].values
    list_id = list(set(list_id))
    dic_failed[institution_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                     pub_id_alias:[int(x) for x in list(list_id)]}
    df_institution = df_institution[df_institution[institution_alias] != '']
    
    if not(len(df_address)==len(df_country)==len(df_institution)):
        warning = (f'WARNING: Lengths of "df_address", "df_country" and "df_institution" dataframes are not equal'
                   f'in "_build_addresses_countries_institutions_wos" function of "BiblioParsingWos.py" module')
        print(Fore.BLUE + warning + Fore.BLACK)
    
    return df_address, df_country, df_institution


def _build_authors_countries_institutions_wos(df_corpus, dic_failed, inst_filter_list):
    
    '''The `_build_authors_countries_institutions_wos' function parses the fields 'C1' 
       of wos database to retrieve the article authors with their addresses, affiliations and country. 
       In addition, a secondary affiliations list may be added according to a filtering of affiliations.
       
       Beware, multiple formats may exist for the 'C1' field. 
       The parsing is effective only for the format of the following example.
       Otherwise, the parsing fields are set to empty strings.
       
       For example, the 'C1' field string:
       '[Boujjat, Houssame] CEA, LITEN Solar & Thermodynam Syst Lab L2ST, F-38054 Grenoble, France;
       [Boujjat, Houssame] Univ Grenoble Alpes, F-38000 Grenoble, France; 
       [Rodat, Sylvain; Chuayboon, Srirat] CNRS, Proc Mat & Solar Energy Lab,
       PROMES, 7 Rue Four Solaire, F-66120 Font Romeu, France;
       [Abanades, Stephane] CEA, Leti, 17 rue des Martyrs, F-38054 Grenoble, France;
       [Dupont, Sylvain] CEA, Liten, INES. 50 avenue du Lac Leman, F-73370 Le Bourget-du-Lac, France;
       [Durand, Maurice] CEA, INES, DTS, 50 avenue du Lac Leman, F-73370 Le Bourget-du-Lac, France;
       [David, David] Lund University, Department of Physical Geography and Ecosystem Science (INES), Lund, Sweden'

        will be parsed in the "df_addr_country_inst" dataframe if affiliation filter is not defined (initialization step):
   
        pub_id  idx_author                     address               country    institutions                   
            0       0        CEA, LITEN Solar & Thermodynam , ...    France     CEA_France;LITEN_France        
            0       0        Univ Grenoble Alpes,...                 France     UGA_France;Universities_France      
            0       1        CNRS, Proc Mat Lab, PROMES,...          France     CNRS_France;PROMES_France                                  
            0       2        CNRS, Proc Mat Lab, PROMES, ...         France     CNRS_France;PROMES_France           
            0       3        CEA, Leti, 17 rue des Martyrs,...       France     CEA_France;LETI_France                        
            0       4        CEA, Liten, INES. 50 avenue...          France     CEA_France;LITEN_France;INES_France               
            0       5        CEA, INES, DTS, 50 avenue...            France     CEA_France;INES_France             
            0       6        Lund University,...(INES),...           Sweden     Lund Univ_Sweden;Universities_Sweden               
        
        The institutions are identified and normalized using "inst_dic" dict which should be specified by the user.
        
        If affiliation filter is defined based on the following list of tuples (institution, country), 
        inst_filter_list = [('LITEN','France'),('INES','France'),('PROMES','France'), (Lund University, Sweden)]. 
        
        The "df_addr_country_inst" dataframe will be expended with the following columns (for pub_id = 0):
            LITEN_France  INES_France  PROMES_France  Lund University_Sweden                   
                 1            0              0                  0             
                 0            0              0                  0                              
                 0            0              1                  0                     
                 0            0              1                  0             
                 0            0              0                  0             
                 1            1              0                  0                              
                 0            1              0                  0                              
                 0            0              0                  1                      
                 
                 
    Args:
        df_corpus (dataframe): the dataframe of the wos corpus.
        dic_failed (dict): the dict to be extended with key "'authors_inst'" and value (%) of the parsing success.
        inst_filter_list (list): the affiliation filter list of tuples (institution, country) 
                                 which value is 'None' at initialization of the parsing.
                            
    Returns:
        (dataframe):  "df_addr_country_inst".
        
    Notes:
        The globals 'COL_NAMES', 'COLUMN_LABEL_WOS', 'RE_ADDRESS', 'RE_AUTHOR', 'RE_SUB' and 'SYMBOL' are used.
        The functions `build_institutions_dic`and `country_normalization` are used 
        from `BiblioAnalysis_utils` package.
    '''
    
    # Standard library imports
    import itertools
    import re
    from colorama import Fore
    from collections import namedtuple
    from string import Template
    
    # 3rd party imports
    import pandas as pd
    from fuzzywuzzy import process
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import build_institutions_dic
    from BiblioAnalysis_Utils.BiblioParsingUtils import country_normalization
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_ADDRESS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_AUTHOR
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_SUB
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SYMBOL
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN
    
    addr_country_inst = namedtuple('address',COL_NAMES['auth_inst'][:-1] )
    author_address_tup = namedtuple('author_address','author address')
    
    template_inst = Template('[$symbol1]?($inst)[$symbol2].*($country)(?:$$|;)')  
    
    # Definition of internal functions
    def _address_inst_full_list(address, inst_dic):

        country_raw = address.split(',')[-1].strip()
        country = country_normalization(country_raw)

        inst_full_list = []        
        for raw_inst, norm_inst in inst_dic.items():  
            raw_inst_split = raw_inst.split()
            template_inst = Template(r'\s+'.join([r'(\b$inst'+str(i)+r'\b)' for i in range(len(raw_inst_split))]))
            dic = {'inst'+str(i):inst for i,inst in enumerate(raw_inst_split)}
            re_inst  = re.compile(template_inst.substitute(dic), re.IGNORECASE)
            if re_inst.findall(address):
                inst_full_list.append(norm_inst + '_' + country)
        if inst_full_list:
            inst_full_list_str = ';'.join(inst_full_list)
        else:
            inst_full_list_str = address.split(',')[0] + '_' + country

        return inst_full_list_str

    def _address_inst_list(inst_filter_list,address):

        secondary_institutions = []
        for inst,country in inst_filter_list:
            re_inst  = re.compile(template_inst.substitute({'symbol1':SYMBOL,
                                                            'symbol2':SYMBOL,
                                                            'inst':inst,
                                                            'country':country}),
                                                             re.IGNORECASE)
            if len(re_inst.findall(address))!=0:
                secondary_institutions.append(1)
            else:
                secondary_institutions.append(0)  
             
        return secondary_institutions
        
    pub_id_alias = COL_NAMES['auth_inst'][0]
    pub_idx_author_alias = COL_NAMES['auth_inst'][1]
    address_alias = COL_NAMES['auth_inst'][2]
    institution_alias = COL_NAMES['auth_inst'][4]
    sec_institution_alias = COL_NAMES['auth_inst'][5]
    
    inst_dic = build_institutions_dic(rep_utils = None, dic_inst_filename = None)    
    
    list_addr_country_inst = []
    
    for pub_id, affiliation in zip(df_corpus.index,
                                   df_corpus[COLUMN_LABEL_WOS['authors_with_affiliations']]):
        if '['  in affiliation:  # Proceed if the field author is present in affiliation.

            
            # From the wos column C1 builds the list of tuples [([Author1, Author2,...], address1),...].
            list_authors = [[x.strip() for x in authors.split(';')] for authors in RE_AUTHOR.findall(affiliation)]
            list_affiliation = [x.strip() for x in RE_ADDRESS.findall(affiliation)]
            list_affiliation = list_affiliation if list_affiliation else ['']
            list_tuples = tuple(zip(list_authors, list_affiliation)) 

            # Builds the list of tuples [(Author<0>, address<0>),(Author<0>, address<1>),...,(Author<i>, address<j>)...]
            list_author_address_tup = [author_address_tup(y,x[1]) for x in list_tuples for y in x[0]]            
            
            # Build the dict {author:idx_author} preserving the author index in the author list
            authors_list = list(itertools.chain(*list_authors)) # flatten a list of lists of authors.
            authors_list = list(dict.fromkeys(authors_list)) # Drops duplicate preserving the author rank.
            
            authors_list_ordered = df_corpus.loc[pub_id,COLUMN_LABEL_WOS['authors']].split(';')                                                    
            dict_idx = {}
            for author in authors_list:
                results = process.extract(author,authors_list_ordered,limit=3)
                dict_idx[author] = authors_list_ordered.index(results[0][0])
                        
            for tup in list_author_address_tup:
                idx_author = dict_idx[tup.author]
                
                author_country_raw = tup.address.split(',')[-1].replace(';','').strip()
                author_country = country_normalization(author_country_raw)
                if author_country == '':
                    author_country = UNKNOWN
                    warning = (f'WARNING: the invalid country name "{author_country_raw}" '
                               f'in pub_id {pub_id} has been replaced by "{UNKNOWN}" '
                               f'in "_build_addresses_countries_institutions_wos" function of "BiblioParsingWos.py" module')
                    print(Fore.BLUE + warning + Fore.BLACK)

                
                author_address_raw = tup.address
                author_address = re.sub(RE_SUB,'University' + ' ', author_address_raw)
                author_institutions = _address_inst_full_list(author_address, inst_dic)

                list_addr_country_inst.append(addr_country_inst(pub_id,
                                                                idx_author,
                                                                tup.address,
                                                                author_country,
                                                                author_institutions))
                
        else:  # If the field author is not present in affiliation complete namedtuple with ''
            list_addr_country_inst.append(addr_country_inst(pub_id,
                                                                '',
                                                                '',
                                                                '',
                                                                ''))
    # Building the a first version of the returned dataframe with 'list_addr_country_inst'
    # with columns "COL_NAMES['auth_inst'][:-1]"
    df_addr_country_inst = pd.DataFrame.from_dict({label:[s[idx] for s in list_addr_country_inst] 
                                                   for idx,label in enumerate(COL_NAMES['auth_inst'][:-1])})

    if inst_filter_list is not None:        
        # Building the "sec_institution_alias" column in the returned dataframe using "inst_filter_list"
        df_addr_country_inst[sec_institution_alias] = df_addr_country_inst.apply(lambda row:
                                                                                 _address_inst_list(inst_filter_list,row[address_alias]),
                                                                                 axis = 1)

        # Adding a column in the return dataframe for each of the institutions indicated in the institutions filter
        col_names = [f'{x[0]}_{x[1]}' for x in inst_filter_list]        
        df_addr_country_inst_split = pd.DataFrame(df_addr_country_inst['Secondary_institutions'].sort_index().to_list(),
                                              columns=col_names)
        df_addr_country_inst = pd.concat([df_addr_country_inst, df_addr_country_inst_split], axis=1)

        df_addr_country_inst.drop([sec_institution_alias], axis=1, inplace=True)
        
    # Sorting the values in the dataframe returned by two columns
    df_addr_country_inst.sort_values(by=[pub_id_alias,pub_idx_author_alias], inplace=True)
    
    # Updating the dic_failed dict
    list_id = df_addr_country_inst[df_addr_country_inst[institution_alias] == ''][pub_id_alias].values
    dic_failed['authors_inst'] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                  pub_id_alias:[int(x) for x in list(list_id)]}    

    return df_addr_country_inst


def _build_subjects_wos(df_corpus,dic_failed):
    
    '''Builds the dataframe "df_subject" using the column "SC":
    
            pub_id  subject
               0    Neurosciences & Neurology
               1    Psychology
               1    Environmental Sciences & Ecology
               2    Engineering
               2    Physics
               3    Philosophy
    
    
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus

    Returns:
        The dataframe df_subject
    '''    
    
    # Standard library imports
    from collections import namedtuple
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS
  
    subject = namedtuple('subject',COL_NAMES['subject'] )
    
    pub_id_alias = COL_NAMES['subject'][0]
    subject_alias = COL_NAMES['subject'][1]
    
    list_subject = []
    for pub_id,scs in zip(df_corpus.index,df_corpus[COLUMN_LABEL_WOS['sub_subjects']]):
        for sc in scs.split(';'):
            list_subject.append(subject(pub_id,
                                        sc.strip()))
            
    df_subject = pd.DataFrame.from_dict({label:[s[idx] for s in list_subject] 
                                         for idx,label in enumerate(COL_NAMES['subject'])})
    
    list_id = df_subject[df_subject[subject_alias] == ''][pub_id_alias].values
    list_id = list(set(list_id))
    dic_failed[subject_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                 pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_subject = df_subject[df_subject[subject_alias] != '']

    return   df_subject


def _build_sub_subjects_wos(df_corpus,dic_failed):
    
    '''Builds the dataframe "df_wos_category" using the column "WC":
    
            pub_id  wos_category
               0    Engineering
               1    Materials Science
               1    Physics
               2    Materials Science
               2    Physics
               3    Chemistry
        
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus

    Returns:
        The dataframe df_gross_subject
    '''
    
    # Standard library imports
    from collections import namedtuple
    
    # 3rd party imports
    import pandas as pd

    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS

    keyword = namedtuple('keyword',COL_NAMES['sub_subject'])
    
    pub_id_alias = COL_NAMES['sub_subject'][0]
    sub_subject_alias = COL_NAMES['sub_subject'][1]

    list_sub_subject = []
    for pub_id, sub_subjects in zip(df_corpus.index,df_corpus[COLUMN_LABEL_WOS['subjects']]):
        if isinstance(sub_subjects,str):
            for sub_subject in sub_subjects.split(';'):
                list_sub_subject.append(keyword(pub_id,
                                                sub_subject.strip()))

    df_sub_subject = pd.DataFrame.from_dict({label:[s[idx] for s in list_sub_subject] 
                                             for idx,label in enumerate(COL_NAMES['sub_subject'])})            
    
    list_id = df_sub_subject[df_sub_subject[sub_subject_alias] == ''][pub_id_alias].values
    list_id = list(set(list_id))
    dic_failed[sub_subject_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                     pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_sub_subject = df_sub_subject[df_sub_subject[sub_subject_alias] != '']
    
    return  df_sub_subject


def _build_articles_wos(df_corpus):
 
    '''Builds the dataframe "df_article" with ten columns:
   
    Authors|Year|Source title|Volume|Page start|DOI|Document Type|
    Language of Original Document|Title|EID
 
    Args:
        df_corpus (dataframe): the dataframe of the wos corpus
 
 
    Returns:
        The dataframe df_institution
        
    '''
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import CHANGE
    from BiblioAnalysis_Utils.BiblioParsingUtils import name_normalizer
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_DOCTYPE

    def _str_int_convertor(x):
        if x:
            return(str(x))
        else:
            return '0'
    
    def _treat_author(list_authors):
        first_author = list_authors.split(';')[0] # we pick the first author
        return  name_normalizer(first_author)
    
    def _treat_doctype(doctype):
        for doctype_key,doctype_list in DIC_DOCTYPE.items():
            if doctype in doctype_list: doctype = doctype_key
        return doctype
    
    def _treat_title(title):
        title = title.translate(CHANGE)
        return title
    
    pub_id_alias = COL_NAMES['articles'][0]
    author_alias = COL_NAMES['articles'][1]
    year_alias = COL_NAMES['articles'][2]
    doc_type_alias = COL_NAMES['articles'][7] 
    title_alias = COL_NAMES['articles'][9] 

    wos_columns = [COLUMN_LABEL_WOS['authors'],
                   COLUMN_LABEL_WOS['year'],
                   COLUMN_LABEL_WOS['journal'], 
                   COLUMN_LABEL_WOS['volume'],
                   COLUMN_LABEL_WOS['page_start'],
                   COLUMN_LABEL_WOS['doi'],
                   COLUMN_LABEL_WOS['document_type'],
                   COLUMN_LABEL_WOS['language'],
                   COLUMN_LABEL_WOS['title'],
                   COLUMN_LABEL_WOS['issn']]
                   
    df_article = df_corpus.loc[:,wos_columns].astype(str)

    df_article.rename (columns = dict(zip(wos_columns,COL_NAMES['articles'][1:])),
                       inplace = True)    
                                                                                                
    df_article[author_alias] = df_article[author_alias].apply(_treat_author)    
    df_article[year_alias] = df_article[year_alias].apply(_str_int_convertor)
    df_article[doc_type_alias] = df_article[doc_type_alias].apply(_treat_doctype)
    df_article[title_alias] = df_article[title_alias].apply(_treat_title)
    
    df_article.insert(0, pub_id_alias, list(df_corpus.index))
   
    return df_article


def _build_references_wos(df_corpus):
   
    '''Builds the dataframe "df_references" of cited references by the article
    referenced with the key publi_id:
   
            pub_id  author     year         journal          volume  page
        0    0    Bellouard Q  2017   INT. J. HYDROG. ENERGY   42    13486
        1    0    Bellouard Q  2017   ENERGY FUELS             31    10933
        2    0    Bellouard Q  2018   INT. J. HYDROG. ENERGY   44    19193
 
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus
 
 
    Returns:
        A dataframe df_keyword
    '''
 
    # Standard library imports
    import re
    from collections import namedtuple
 
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import name_normalizer
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_AUTHOR_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_JOURNAL_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_PAGE_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_VOL_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_YEAR_WOS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN
 
    ref_article = namedtuple('ref_article', COL_NAMES['references'])
 
    list_ref_article =[]
    for pub_id, row in zip(list(df_corpus.index),
                                df_corpus[COLUMN_LABEL_WOS['references']]):
 
        if isinstance(row, str): # if the reference field is not empty and not an URL
 
                for field in row.split(";"):
 
                    year = re.findall(RE_REF_YEAR_WOS, field) 
                    if len(year):
                        year = year[0][1:-1]
                    else:
                        year = 0
 
                    vol = re.findall(RE_REF_VOL_WOS, field)
                    if len(vol):
                        vol = vol[0][3:]
                    else:
                        vol = 0
 
                    page = re.findall(RE_REF_PAGE_WOS, field)
                    if len(page):
                        page = page[0][3:]
                    else:
                        page = 0
 
                    journal = re.findall(RE_REF_JOURNAL_WOS, field)
                    if len(journal):
                        journal = journal[0].strip()
                    else:
                        journal = UNKNOWN
 
                    author = re.findall(RE_REF_AUTHOR_WOS, field)
                    if len(author):
                        author = name_normalizer(author[0][:-1])
                    else:
                        author = UNKNOWN
 
                    if (author != UNKNOWN) and (journal != UNKNOWN):
                        list_ref_article.append(ref_article(pub_id,author,year,journal,vol,page))
 
                    if (vol==0) & (page==0) & (author != UNKNOWN):
                        pass
 
    df_references = pd.DataFrame.from_dict({label:[s[idx] for s in list_ref_article] 
                                            for idx,label in enumerate(COL_NAMES['references'])})
    
    return df_references


def read_database_wos(filename):
    
    '''The `read_database_wos`function allows to circumvent the error ParserError: '	' 
       expected after '"' generated by the method `pd.read_csv`.
       
    Args:
        filename ()   
    '''
    # Standard library imports
    import sys
    import csv
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import check_and_drop_columns
    from BiblioAnalysis_Utils.BiblioParsingUtils import normalize_journal_names
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import ENCODING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FIELD_SIZE_LIMIT
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import WOS
        
    csv.field_size_limit(FIELD_SIZE_LIMIT) # To extend the field size limit for reading .txt files

    with open(filename,'rt',encoding=ENCODING) as csv_file: 
        csv_reader = csv.reader(csv_file, delimiter = '\t')
        csv_list = []
        for row in csv_reader:
            csv_list.append(row)

    df = pd.DataFrame(csv_list)
    df.columns = df.iloc[0]                  # Sets columns name to raw 0
    df = df.drop(0)                          # Drops the raw 0 from df 
    
    df = check_and_drop_columns("wos",df,filename)
    df = df.dropna()
    df.index = list(range(len(df)))
    df = df.replace('',UNKNOWN,regex=True)
    df = normalize_journal_names(WOS,df)
        
    return df


def biblio_parser_wos(in_dir_parsing, out_dir_parsing, inst_filter_list):
    
    '''Using the file xxxx.txt stored in the folder rawdata, the function biblio_parser_wos
    generates the files xxxx.dat stored in the folder parsing.
    home path/myfoldername/BiblioAnalysis Data/
    |-- myprojectname/
    |   |-- rawdata/
    |   |   |-- xxxx.txt
    |   |-- parsing/
    |   |   |-- addresses.dat, articles.dat, authors.dat, countries.dat, database.dat  
    |   |   |-- institutions.dat, keywords.dat, references.dat, subjects.dat, subjects2.dat
    
    The columns USECOLS_WOS of the tsv file xxxx.txt are read and the parsed using the 
    functions:
        _build_references_wos which parses the column 'CR'
        _build_authors_wos which parses the column 'AU'
        _build_keywords_wos which parses the column 'ID' (for author keywords AK),
                                        the column 'DE' (for journal keywords IK),
                                        the column 'TI' (for title keywords IK)
        _build_addresses_countries_institutions_wos which parses the column 'C1' by pub_id
        _build_authors_countries_institutions_wos which parses the column 'C1' by authors
        _build_subjects_wos which parses the column 'SC'
        _build_sub_subjects_wos which parses the column 'WC'
        _build_articles_wos which parses the column 'AU', 'PY', 'SO', 'VL', 'BP',
                                                   'DI', 'DT', 'LA', 'TI', 'SN'
    '''
    
    # Standard library imports
    import os
    import json
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    
    pub_id_alias = COL_NAMES['keywords'][0]
    keyword_alias = COL_NAMES['keywords'][1]

    list_data_base = []
    for path, _, files in os.walk(in_dir_parsing):
        list_data_base.extend(Path(path) / Path(file) for file in files
                                                      if file.endswith(".txt"))
    filename = list_data_base[0]
    
    # Reading and checking the corpus file
    df_corpus = read_database_wos(filename)
    
    # Initializing the dic_failed dict for the parsing control
    dic_failed = {}
    dic_failed['number of article'] = len(df_corpus)
    
    # Building the file for authors (.dat)
    item = 'AU' 
    df_AU = _build_authors_wos(df_corpus)
    df_AU.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item] ), 
                 index=False,
                 sep='\t')
    
    # Building and saving the files for keywords
    df_keyword_AK,df_keyword_IK, df_keyword_TK = _build_keywords_wos(df_corpus,dic_failed)   
      # Saving author keywords file (.dat)
    item = 'AK' 
    df_keyword_AK.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')    
      # Saving journal (indexed) keywords file (.dat)
    item = 'IK'  
    df_keyword_IK.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')    
      # Saving title keywords file (.dat)
    item = 'TK'
    df_keyword_TK.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')    
                    
    # Building and saving the files for addresses, countries and institutions
    item = 'AD' 
    df_AD, df_CU, df_I = _build_addresses_countries_institutions_wos(df_corpus,dic_failed)
      # Saving addresses file (.dat)
    df_AD.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                 index=False,
                 sep='\t')
      # Saving countries file (.dat) 
    item = 'CU'  # Deals with countries
    df_CU.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                 index=False, 
                 sep='\t')
      # Saving institutions file (.dat)
    item = 'I'   # Deals with institutions
    df_I.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                 index=False, 
                 sep='\t')
    
    # Building and saving the file for authors and their institutions (.dat)
    item = 'I2'
    df_I2 = _build_authors_countries_institutions_wos(df_corpus, dic_failed, inst_filter_list)
    df_I2.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item] ), 
                 index=False,
                sep='\t') 
    
    # Building and saving the file for subjects (.dat)
    item = 'S' 
    df_S = _build_subjects_wos(df_corpus,dic_failed)
    df_S.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')

    # Building and saving the file for sub-subjects (.dat)
    item = 'S2' 
    df_S2 = _build_sub_subjects_wos(df_corpus,dic_failed)
    df_S2.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')
    
    # Building and saving the file for articles (.dat)
    item = 'A'
    df_A = _build_articles_wos(df_corpus)
    df_A.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')
    
    # Building and saving the file for references (.dat)
    item = 'R' 
    df_R = _build_references_wos(df_corpus)
    df_R.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False, 
                sep='\t')
                
    # Saving the dic_failed dict for the parsing control (.json)
    with open(Path(out_dir_parsing) / Path('failed.json'), 'w') as write_json:
        json.dump(dic_failed, write_json,indent=4)