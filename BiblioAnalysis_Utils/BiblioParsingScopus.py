__all__ = ['biblio_parser_scopus']

# Globals used from BiblioAnalysis_Utils.BiblioSpecificGlobals: CHANGE, DIC_OUTDIR_PARSING, DIC_DOCTYPE,
#                                                               RE_REF_AUTHOR_SCOPUS, RE_REF_JOURNAL_SCOPUS,
#                                                               RE_REF_PAGE_SCOPUS, RE_REF_VOL_SCOPUS,
#                                                               RE_REF_YEAR_SCOPUS, RE_SUB, SCOPUS
#                                                               SCOPUS_CAT_CODES, SCOPUS_JOURNALS_ISSN_CAT,
#                                                               UNKNOWN, USECOLS_SCOPUS


# Functions used from BiblioAnalysis_Utils.BiblioParsingUtils: build_title_keywords, build_institutions_dic
#                                                              country_normalization, normalize_journal_names, name_normalizer 

def _build_authors_scopus(df_corpus):
    
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
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
        
    co_author = namedtuple('co_author',COL_NAMES['authors'])
    
    co_author_alias = COL_NAMES['authors'][2]
    
    list_author = []
    for pub_id,x in zip(df_corpus.index,
                        df_corpus[COLUMN_LABEL_SCOPUS['authors']]):
        idx_author = 0
        for y in x.split(","):
            author = name_normalizer(y.replace('.',''))
            
            if author not in ['Dr','Pr','Dr ','Pr ']:
                list_author.append(co_author(pub_id,
                                             idx_author,
                                             author))
                idx_author += 1
                
    df_co_authors = pd.DataFrame.from_dict({label:[s[idx] for s in list_author] 
                                            for idx,label in enumerate(COL_NAMES['authors'])})    
    
    df_co_authors = df_co_authors[df_co_authors[co_author_alias] != '']
    
    return df_co_authors


def _build_keywords_scopus(df_corpus,dic_failed):
    
    '''Builds the dataframe "df_keyword" with three columns:
                pub_id  type  keyword
            0     0      AK    Biomass
            1     0      AK    Gasification
            2     0      AK    Solar energy
    with: 
         type = AK for author keywords 
         type = IK for journal keywords
         type = TK for title keywords 
         
    The author keywords are extracted from the scopus column 'Author Keywords' 
    The journal keywords are extracted from the scopus column 'Index Keywords' 
    The title keywords are builds out of the set TK_corpus of the most cited nouns 
      (at leat N times) in the set of all the articles. The keywords of type TK of an
      article, referenced by the key pub_id, are the elements of the intersection
      between the set TK_corpus and the set of the nouns of the article title.
    
        
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus

    Returns:
        The dataframe df_keyword
    '''
    
    # Standard library imports
    from collections import namedtuple
    from collections import Counter
    from operator import attrgetter
    
    # 3rd party imports
    import nltk
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import build_title_keywords
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN
    
    COL_NAMES = {}
    COL_NAMES['keywords'] = ['Pub_id', 'Keyword']

    key_word = namedtuple('key_word',COL_NAMES['keywords'])
    
    pub_id_alias = COL_NAMES['keywords'][0]
    type_alias = COL_NAMES['keywords'][1]
    keyword_alias = COL_NAMES['keywords'][1]
    
    list_keyword_AK = []
    df_AK = df_corpus[COLUMN_LABEL_SCOPUS['author_keywords']].fillna('')
    for pub_id,keywords_AK in zip(df_AK.index,df_AK):
        list_keywords_AK = keywords_AK.split(';')      
        for keyword_AK in list_keywords_AK:
            keyword_AK = keyword_AK.strip()
            list_keyword_AK.append(key_word(pub_id,
                                   keyword_AK if keyword_AK != 'null' else '”null”'))

    list_keyword_IK = []
    df_IK = df_corpus[COLUMN_LABEL_SCOPUS['index_keywords']].fillna('')
    for pub_id,keywords_IK in zip(df_IK.index,df_IK):
        list_keywords_IK = keywords_IK.split(';')
        for keyword_IK in list_keywords_IK:
            keyword_IK = keyword_IK.strip()
            if keyword_IK == 'null': keyword_IK = UNKNOWN # replace 'null' by the keyword UNKNOWN
            list_keyword_IK.append(key_word(pub_id,
                                            keyword_IK if keyword_IK != 'null' else '”null”'))
            
    list_keyword_TK = []
    df_title = pd.DataFrame(df_corpus[COLUMN_LABEL_SCOPUS['title']].fillna(''))
    df_title.columns = ['Title']  # To be coherent with the convention of function build_title_keywords          # To check
    df_TK,list_of_words_occurrences = build_title_keywords(df_title)
    for pub_id in df_TK.index:
        for token in df_TK.loc[pub_id,'kept_tokens']:
            token = token.strip()
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


def _build_addresses_countries_institutions_scopus(df_corpus,dic_failed):
    
    '''Builds the dataframe "df_address" from the column "Affiliations" of the scopus corpus:
    
            pub_id  idx_address  address
              0         0         CEA-LITEN Solar and ...
              0         1         Univ. Grenoble Alpes, Grenoble, F-38000, France
              0         2         Processes, Materials and Solar Energy Laboratory,...
        
    where: idx_address is the rank of the address in the list of affiliations
    of the article referenced with the key pub_id.
    We use the column 'Affiliations' formated as :
    
    'CEA-LITEN Solar and Thermodynamic Systems Laboratory (L2ST), Grenoble, F-38054, France;
    Univ. Grenoble Alpes, Grenoble, F-38000, France;
    Processes, Materials and Solar Energy Laboratory, PROMES-CNRS, 
    7 Rue du Four Solaire, Font-Romeu, 66120, France'
    
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus


    Returns:
        The dataframe df_address
         
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
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_SUB
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN

    address = namedtuple('address',COL_NAMES['address'] )
    ref_country = namedtuple('country',COL_NAMES['country'] )
    ref_institution = namedtuple('ref_institution',COL_NAMES['institution'] )
    
    pub_id_alias = COL_NAMES['address'][0]
    address_alias = COL_NAMES['address'][2]
    country_alias = COL_NAMES['country'][2]
    institution_alias = COL_NAMES['institution'][2]

    list_addresses = []
    list_countries =[]
    list_institutions = []    
    
    for pub_id, affiliation in zip(df_corpus.index,
                                   df_corpus[COLUMN_LABEL_SCOPUS['affiliations']]):
        list_affiliation = affiliation.split(';')
        
        if list_affiliation:
            for idx_address, address_pub in enumerate(list_affiliation):

                list_addresses.append(address(pub_id,
                                              idx_address,
                                              address_pub))

                institution = address_pub.split(',')[0]
                institution = re.sub(RE_SUB,'University'+' ', institution)
                list_institutions.append(ref_institution(pub_id,
                                                         idx_address,
                                                         institution))
                country_raw = address_pub.split(',')[-1].replace(';','').strip()  
                country = country_normalization(country_raw)
                if country == '':
                    country=UNKNOWN
                    warning = (f'WARNING: the invalid country name "{country_raw}" '
                               f'in pub_id {pub_id} has been replaced by "{UNKNOWN}"'
                               f'in "_build_addresses_countries_institutions_scopus" function of "BiblioParsingScopus.py" module')
                    print(Fore.BLUE + warning + Fore.BLACK)

                list_countries.append(ref_country(pub_id,
                                                  idx_address,
                                                  country))
        else:
            list_addresses.append(address(pub_id,
                                          0,
                                          ''))
            list_institutions.append(ref_institution(pub_id,
                                                     0,
                                                     ''))
            list_countries.append(country(pub_id,
                                          0,
                                          ''))
            

    df_address = pd.DataFrame.from_dict({label:[s[idx] for s in list_addresses] 
                                         for idx,label in enumerate(COL_NAMES['address'])})

    df_country = pd.DataFrame.from_dict({label:[s[idx] for s in list_countries] 
                                         for idx,label in enumerate(COL_NAMES['country'])})

    df_institution = pd.DataFrame.from_dict({label:[s[idx] for s in list_institutions] 
                                             for idx,label in enumerate(COL_NAMES['institution'])})
    
    list_id = df_address[df_address[address_alias] == ''][pub_id_alias].values
    dic_failed[address_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                 pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_address = df_address[df_address[address_alias] != '']
    
    
    list_id = df_country[df_country[country_alias] == ''][pub_id_alias].values
    list_id = list(set(list_id))
    dic_failed[country_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                 pub_id_alias:[int(x) for x in list(list_id)]}
    df_country = df_country[df_country[country_alias] != '']
    
    list_id = df_institution[df_institution[institution_alias] == ''][pub_id_alias].values
    dic_failed[institution_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                     pub_id_alias:[int(x) for x in list(list_id)]}
    df_institution = df_institution[df_institution[institution_alias] != '']
    
    if not(len(df_address)==len(df_country)==len(df_institution)):
        warning = (f'WARNING: Lengths of "df_address", "df_country" and "df_institution" dataframes are not equal'
                   f'in "_build_addresses_countries_institutions_scopus" function of "BiblioParsingScopus.py" module')
        print(Fore.BLUE + warning + Fore.BLACK)
    
    return df_address, df_country, df_institution


def _build_authors_countries_institutions_scopus(df_corpus, dic_failed, inst_filter_list):
    
    '''The `_build_authors_countries_institutions_scopus' function parses the fields 'Affiliations' 
       and 'Authors with affiliations' of a scopus database to retrieve the article authors 
       with their addresses, affiliations and country. 
       In addition, a secondary affiliations list may be added according to a filtering of affiliations.
       
       The parsing is effective only for the format of the following example.
       Otherwise, the parsing fields are set to empty strings.
       
       For example, the 'Authors with affiliations' field string:

       'Boujjat, H., CEA, LITEN Solar & Thermodynam Syst Lab L2ST, F-38054 Grenoble, France,
        Univ Grenoble Alpes, F-38000 Grenoble, France; 
        Rodat, S., CNRS, Proc Mat & Solar Energy Lab, PROMES, 7 Rue Four Solaire, F-66120 Font Romeu, France;
        Chuayboon, S., CNRS, Proc Mat & Solar Energy Lab, PROMES, 7 Rue Four Solaire, F-66120 Font Romeu, France;
        Abanades, S., CEA, Leti, 17 rue des Martyrs, F-38054 Grenoble, France;
        Dupont, S., CEA, Liten, INES. 50 avenue du Lac Leman, F-73370 Le Bourget-du-Lac, France;
        Durand, M., CEA, INES, DTS, 50 avenue du Lac Leman, F-73370 Le Bourget-du-Lac, France;
        David, D., Lund University, Department of Physical Geography and Ecosystem Science (INES), Lund, Sweden'

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
        
        given that the 'Affiliations' field string is:
        
        'CEA, LITEN Solar & Thermodynam Syst Lab L2ST, F-38054 Grenoble, France; 
        Univ Grenoble Alpes, F-38000 Grenoble, France; 
        CNRS, Proc Mat & Solar Energy Lab, PROMES, 7 Rue Four Solaire, F-66120 Font Romeu, France;
        CEA, Leti, 17 rue des Martyrs, F-38054 Grenoble, France;
        CEA, Liten, INES. 50 avenue du Lac Leman, F-73370 Le Bourget-du-Lac, France;
        CEA, INES, DTS, 50 avenue du Lac Leman, F-73370 Le Bourget-du-Lac, France;
        Lund University, Department of Physical Geography and Ecosystem Science (INES), Lund, Sweden'
        
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
        df_corpus (dataframe): the dataframe of the scopus corpus.
        inst_filter_list (list): the affiliation filter list of tuples (institution, country)

    Returns:
        The dataframe df_addr_country_inst.
    '''
    
    # Standard library imports
    import re
    from colorama import Fore
    from collections import namedtuple
    from string import Template
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import build_institutions_dic
    from BiblioAnalysis_Utils.BiblioParsingUtils import country_normalization
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_SUB
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SYMBOL
    
    addr_country_inst = namedtuple('address',COL_NAMES['auth_inst'][:-1])
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
    
    for pub_id, affiliations, authors_affiliations in zip(df_corpus.index,
                                                         df_corpus[COLUMN_LABEL_SCOPUS['affiliations']],
                                                         df_corpus[COLUMN_LABEL_SCOPUS['authors_with_affiliations']]):
        
        idx_author, last_author = -1, '' # Initialization for the author and address counter
        
        list_affiliations = affiliations.split(';')
        list_authors_affiliations = authors_affiliations.split(';')
        
        for x in list_authors_affiliations:
            author = (','.join(x.split(',')[0:2])).strip()
            if last_author != author:
                idx_author += 1
            last_author = author

            author_list_addresses = ','.join(x.split(',')[2:])
            author_address_list_raw = []
            for affiliation in list_affiliations:
                if affiliation in author_list_addresses:
                    affiliation = re.sub(RE_SUB,'University' + ' ',affiliation)
                    author_address_list_raw.append(affiliation)   

            author_institutions = []
            for address in author_address_list_raw:
                author_country_raw = address.split(',')[-1].strip()
                author_country = country_normalization(author_country_raw)

                author_institutions = _address_inst_full_list(address, inst_dic)

                list_addr_country_inst.append(addr_country_inst(pub_id,
                                                          idx_author,
                                                          address,
                                                          author_country,                  
                                                          author_institutions))
                
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

        df_addr_country_inst.drop(['Secondary_institutions'], axis=1, inplace=True)
    
    # Sorting the values in the dataframe returned by two columns
    df_addr_country_inst.sort_values(by=[pub_id_alias,pub_idx_author_alias], inplace=True)
    
    # Updating the dic_failed dict
    list_id = df_addr_country_inst[df_addr_country_inst[institution_alias] == ''][pub_id_alias].values
    dic_failed['authors_inst'] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                  pub_id_alias:[int(x) for x in list(list_id)]}
    
    return df_addr_country_inst



def _build_subjects_scopus(df_corpus,
                          path_scopus_cat_codes,
                          path_scopus_journals_issn_cat,
                          dic_failed):
    
    '''Builds the dataframe "df_gross_subject" with two columns 'publi_id' 
    and 'ASJC_description'
    
    ex:       pub_id   ASJC_description
        0       0      Mathematics
        1       0      Engineering
         
    the AJS_description is the generic name of category given every multiple of 1OO in the 
    scopus_cat_codes.txt file. For exemple an extract of the scopus_cat_codes.txt file:
    
    General Medicine                 2700  mutiple of 100 General category
    Medicine (miscellaneous)         2701  subcategory
    Anatomy                          2702
    Anesthesiology and Pain Medicine 2703
    Biochemistry, medical            2704
    
    The codes attached to a journal are given in the tcv file scopus_journals_issn_cat:
    
    21st Century Music \t 15343219 \t 1210; 
    2D Materials \t \t     2210; 2211; 3104; 2500; 1600; 
    3 Biotech \t 2190572X \t1101; 2301; 1305;
    
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus
        path_scopus_cat_codes=None,
        path_scopus_journals_issn_cat=None):

    Returns:
        The dataframe df_gross_subject
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS

    pub_id_alias = COL_NAMES['subject'][0]
    subject_alias = COL_NAMES['subject'][1] 

    # Builds the dict "code_cat" {ASJC classification codes:description} out 
    # of the file "scopus_cat_codes.txt"
    # ex: {1000: 'Multidisciplinary', 1100: 'General Agricultural',...}
    # -----------------------------------------------------------------------
    df_scopus_cat_codes = pd.read_csv(path_scopus_cat_codes,
                                      sep='\t',
                                      header=None)
    code_cat = dict(zip(df_scopus_cat_codes[1].fillna(0.0).astype(int),
                        df_scopus_cat_codes[0]))

    # Builds the dataframe "df_scopus_journals_issn_cat" out of the file
    # "scopus_journals_issn_cat.txt"
    # "df_scopus_journals_issn_cat" has three columns:
    #       "journal": scopus journal name
    #       "issn": journal issn
    #       "keyword_id": list of keywords id asociated to the journal or the issn
    # -----------------------------------------------------------------------------
    df_scopus_journals_issn_cat = pd.read_csv(path_scopus_journals_issn_cat,
                                              sep='\t',
                                              header=None).fillna(0) 
    df_scopus_journals_issn_cat[2] = df_scopus_journals_issn_cat[2].str.split(';')
    df_scopus_journals_issn_cat.columns = ['journal','issn','keyword_id']

    # Builds the list "res" of tuples [(publi_id,scopus category),...]
    # ex: [(0, 'Applied Mathematics'), (0, 'Materials Chemistry'),...]
    # ----------------------------------------------------------------
    res = [] 
    for pub_id,journal, issn in zip(df_corpus.index,
                                    df_corpus[COLUMN_LABEL_SCOPUS['journal']],
                                    df_corpus[COLUMN_LABEL_SCOPUS['issn']] ):
        keywords = df_scopus_journals_issn_cat.query('journal==@journal ')['keyword_id']

        if len(keywords):                # Checks if journal found in scopus journal list
            try:                         # Checks if keywords id not empty (nan)
                keywords = keywords.tolist()
                for keyword in keywords: # append keyword dont take care of duplicates
                                         # takes index multiple of 100 to select "generic" keyword
                    res.extend([(pub_id,code_cat[int(i.strip()[0:2] + "00")].replace("General",""))
                                for i in keyword[:-1]])
            except:
                res.extend([(pub_id,'')])

        else:                            # check if journal found in scopus issn list
            keywords = df_scopus_journals_issn_cat.query('issn==@issn')['keyword_id']

            if len(keywords):
                try:
                    keywords = keywords.tolist()
                    for keyword in keywords: # append keyword dont take care of duplicates
                                             # takes index multiple of 100 to select "generic" keyword
                        res.extend([(pub_id,code_cat[int(i.strip()[0:2] + "00")].\
                                     replace("General",""))
                                     for i in keyword[:-1]])
                except:
                    res.extend([(pub_id,'')])

    # Builds the dataframe "df_keyword" out of tuples [(publi_id,scopus category),...]
    # "df_keyword" has two columns "pub_id" and "scopus_keywords". 
    # The duplicated rows are supressed.
    # ----------------------------------------------------------------            
    list_pub_id,list_keywords = zip(*res)
    
    df_subject = pd.DataFrame.from_dict({pub_id_alias:list_pub_id,
                                         subject_alias:list_keywords})
 
    list_id = df_subject[df_subject[subject_alias] == ''][pub_id_alias].values
    dic_failed[subject_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                 pub_id_alias:[int(x) for x in list(list_id)]}

    df_subject.drop_duplicates(inplace=True)
    df_subject = df_subject[df_subject[subject_alias] != '']
    
    return df_subject


def _build_sub_subjects_scopus(df_corpus,
                     path_scopus_cat_codes,
                     path_scopus_journals_issn_cat,
                     dic_failed):
    
    '''Builds the dataframe "df_sub_subjects" with two columns 'publi_id' and 'ASJC_description'
    ex:       pub_id   ASJC_description
        0       0      Applied Mathematics
        1       0      Industrial and Manufacturing Engineering

    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus
        path_scopus_cat_codes (path): full path of the file path_scopus_cat_codes.txt
        path_scopus_journals_issn_cat (path): full path of the file scopus_journals_issn_cat.txt

    Returns:
        The dataframe sub_subjects
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    
    pub_id_alias = COL_NAMES['sub_subject'][0]
    sub_subject_alias = COL_NAMES['sub_subject'][1] 

    # Builds the dict "code_cat" {ASJC classification codes:description} out of the file "scopus_cat_codes.txt"
    # ex: {1000: 'Multidisciplinary', 1100: 'General Agricultural and Biological Sciences',...}
    # -------------------------------------------------------------------------------------------------
    df_scopus_cat_codes = pd.read_csv(path_scopus_cat_codes,
                                      sep='\t',
                                      header=None)
    code_cat = dict(zip(df_scopus_cat_codes[1].fillna(0.0).astype(int),df_scopus_cat_codes[0]))

    # Builds the dataframe "df_scopus_journals_issn_cat" out of the file "scopus_journals_issn_cat.txt"
    # "df_scopus_journals_issn_cat" has three columns:
    #       "journal": scopus journal name
    #       "issn": journal issn
    #       "keyword_id": list of keywords id asoociated to the journal or the issn
    # -----------------------------------------------------------------------------
    df_scopus_journals_issn_cat = pd.read_csv(path_scopus_journals_issn_cat,
                                              sep='\t',
                                              header=None).fillna(0) 
    df_scopus_journals_issn_cat[2] = df_scopus_journals_issn_cat[2].str.split(';')
    df_scopus_journals_issn_cat.columns = ['journal','issn','keyword_id']


    # Builds the list "res" of tuples [(publi_id,scopus category),...]
    # ex: [(0, 'Applied Mathematics'), (0, 'Materials Chemistry'),...]
    # ----------------------------------------------------------------
    res = [] 
    for pub_id,journal, issn in zip(df_corpus.index,
                                    df_corpus[COLUMN_LABEL_SCOPUS['journal']],
                                    df_corpus[COLUMN_LABEL_SCOPUS['issn']] ):
        keywords = df_scopus_journals_issn_cat.query('journal==@journal ')['keyword_id']

        if len(keywords):                # Checks if journal found in scopus journal list
            try:                         # Checks if keywords id not empty (nan)
                keywords = keywords.tolist()
                for keyword in keywords: # append keyword dont take care of duplicates
                    res.extend([(pub_id,code_cat[int(i)]) for i in keyword[:-1]])
            except:
                res.extend([(pub_id,'')])

        else:                            # check if journal found in scopus issn list
            keywords = df_scopus_journals_issn_cat.query('issn==@issn')['keyword_id']

            if len(keywords):
                try:
                    keywords = keywords.tolist()
                    for keyword in keywords: # append keyword dont take care of duplicates
                        res.extend([(pub_id,code_cat[int(i)]) for i in keyword[:-1]])
                except:
                    res.extend([(pub_id,'')])

    # Builds the dataframe "df_keyword" out of tuples [(publi_id,scopus category),...]
    # "df_keyword" has two columns "pub_id" and "scopus_keywords". 
    # The duplicated rows are supressed.
    # ----------------------------------------------------------------            
    list_pub_id,list_keywords = zip(*res)
    df_sub_subject = pd.DataFrame.from_dict({pub_id_alias:list_pub_id,
                                              sub_subject_alias:list_keywords})    
    
    list_id = df_sub_subject[df_sub_subject[sub_subject_alias] == ''][pub_id_alias].values
    dic_failed[sub_subject_alias] = {'success (%)':100*(1-len(list_id)/len(df_corpus)),
                                     pub_id_alias:[int(x) for x in list(list_id)]}
    
    df_sub_subject.drop_duplicates(inplace=True)
    
    df_sub_subject = df_sub_subject[df_sub_subject[sub_subject_alias] != '']
    
    return df_sub_subject


def _build_articles_scopus(df_corpus):
 
    '''Builds the dataframe "df_article" with three columns:
   
    Authors|Year|Source title|Volume|Page start|DOI|Document Type|
    Language of Original Document|Title|ISSN
 
    Args:
        df_corpus (dataframe): the dataframe of the wos/scopus corpus
 
 
    Returns:
        The dataframe df_institution
        
    '''
    
    # Standard library imports
    import re
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import CHANGE
    from BiblioAnalysis_Utils.BiblioParsingUtils import name_normalizer
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_DOCTYPE
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN

    re_issn = re.compile(r'^[0-9]{8}|[0-9]{4}|[0-9]{3}X') # Use to normalize the ISSN to the
                                                          # form dddd-dddd or dddd-dddX used by wos
    
    def _convert_issn(text):        
        y = ''.join(re.findall(re_issn,  text))
        if len(y) != 0:
            return y[0:4] + "-" + y[4:]
        else:
            return UNKNOWN
   
    def _str_int_convertor(x):
        try:
            return(int(float(x)))
        except:
            return 0
        
    def _treat_author(list_authors):
        first_author = name_normalizer(list_authors.split(',')[0]) # we pick the first author
        return first_author
    
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
    issn_alias = COL_NAMES['articles'][-1]
    
    scopus_columns = [COLUMN_LABEL_SCOPUS['authors'],
                      COLUMN_LABEL_SCOPUS['year'],
                      COLUMN_LABEL_SCOPUS['journal'],
                      COLUMN_LABEL_SCOPUS['volume'],
                      COLUMN_LABEL_SCOPUS['page_start'],
                      COLUMN_LABEL_SCOPUS['doi'],
                      COLUMN_LABEL_SCOPUS['document_type'],
                      COLUMN_LABEL_SCOPUS['language'],
                      COLUMN_LABEL_SCOPUS['title'],
                      COLUMN_LABEL_SCOPUS['issn']]

    df_article = df_corpus[scopus_columns].astype(str)

    df_article.rename (columns = dict(zip(scopus_columns,COL_NAMES['articles'][1:])),
                       inplace = True)                      
   
    df_article[author_alias] = df_article[author_alias].apply(_treat_author)
    df_article[year_alias] = df_article[year_alias].apply(_str_int_convertor)
    df_article[doc_type_alias] = df_article[doc_type_alias].apply(_treat_doctype)
    df_article[title_alias] = df_article[title_alias].apply(_treat_title)
    df_article[issn_alias] = df_article[issn_alias].apply(_convert_issn)
    
    df_article.insert(0, pub_id_alias, list(df_corpus.index))

    return df_article


def _build_references_scopus(df_corpus):
    
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
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_AUTHOR_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_JOURNAL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_PAGE_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_VOL_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import RE_REF_YEAR_SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN

    ref_article = namedtuple('ref_article',COL_NAMES['references'])
                   
    list_ref_article =[]
    dic_ref = {}
                   
    for pub_id, row in zip(list(df_corpus.index),
                                df_corpus[COLUMN_LABEL_SCOPUS['references']]):

        if isinstance(row, str): # if the reference field is not empty and not an URL

            for field in row.split(";"):
                author = re.findall(RE_REF_AUTHOR_SCOPUS, field)
                if len(author):
                    author = name_normalizer(author[0])
                else:
                    author = UNKNOWN

                year = re.findall(RE_REF_YEAR_SCOPUS, field)  
                if len(year):
                    year = year[0]
                else:
                    year = 0

                journal = re.findall(RE_REF_JOURNAL_SCOPUS, field)
                if journal:
                    if ',' in journal[0] :
                        journal = journal[0][6:-1].upper()
                    else:
                        journal = journal[0][6:].upper()
                else:
                    journal = UNKNOWN

                vol = re.findall(RE_REF_VOL_SCOPUS, field)
                if len(vol):
                    if ',' in vol[0]:
                        vol = re.findall(r'\d{1,6}',vol[0])[0]
                    else:
                        vol = vol[0].strip()
                else:
                    vol = 0

                page = re.findall(RE_REF_PAGE_SCOPUS, field)
                if len(page) == 0:
                    page = 0
                else:
                    page = page[0].split('p.')[1]

                if (author != UNKNOWN) and (journal != UNKNOWN):
                    list_ref_article.append(ref_article(pub_id,author,year,journal,vol,page))

                if (vol==0) & (page==0) & (author != UNKNOWN):
                    pass

    df_references = pd.DataFrame.from_dict({label:[s[idx] for s in list_ref_article] 
                                            for idx,label in enumerate(COL_NAMES['references'])})
    
    return df_references


def _check_affiliation_column_scopus(df):
    
    '''
    The `_check_affiliation_column_scopus` function checks the correcteness of the column affiliation of a df 
    read from a csv scopus file.
    A cell of the column affiliation should reads:
    address<0>, country<0>;...; address<i>, country<i>;...
    
    Some cells can be misformatted with an uncorrect country field. The function eliminates, for each
    cell of the column, those items address<i>, country<i> uncorrectly formatted. When such an item is detected
    a warning message is printed.    
    '''
    # Standard library imports
    from colorama import Fore
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioParsingUtils import country_normalization 
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COLUMN_LABEL_SCOPUS
        
    def _valid_affiliation(row):
        nonlocal idx
        idx += 1
        valid_affiliation_list = []
        for affiliation in row[COLUMN_LABEL_SCOPUS['affiliations']].split(';'):
            raw_country = affiliation.split(',')[-1].strip()
            if country_normalization(raw_country):
                valid_affiliation_list.append(affiliation)
            else:
                warning = (f'\nWARNING in "_check_affiliation_column_scopus" function of "BiblioParsingScopus.py" module:'
                           f'\nAt row {idx} of the scopus corpus, the invalid affiliation "{affiliation}" '
                           f'has been droped from the list of affiliations. '
                           f'\nTherefore, attention should be given to the resulting list of affiliations for each of the authors of this publication.\n' )           
                print(Fore.BLUE + warning + Fore.BLACK)
        if  valid_affiliation_list:  
            return ';'.join(valid_affiliation_list)
        else:
            return 'unkown'
    
    idx = -1
    df[COLUMN_LABEL_SCOPUS['affiliations']] = df.apply(_valid_affiliation,axis=1) 
    
    return df


def biblio_parser_scopus(in_dir_parsing, out_dir_parsing, rep_utils, inst_filter_list):
    
    '''Using the files xxxx.csv stored in the folder rawdata, the function biblio_parser_scopus
    generates the tsv files xxxx.dat stored in the folder parsing.
    home path//BiblioAnalysis Data/
    |-- myprojectname/
    |   |-- rawdata/
    |   |   |-- xxxx.txt
    |   |-- parsing/
    |   |   |-- addresses.dat, articles.dat, authors.dat, countries.dat, database.dat  
    |   |   |-- institutions.dat, keywords.dat, references.dat, subjects.dat, subjects2.dat 
    
    The columns USECOLS_SCOPUS of the tsv file xxxx.csv are read and the parsed using the 
    functions:
        _build_references_scopus which parses the column 'References'
        _build_authors_scopus which parses the column 'Authors'
        _build_keywords_scopus which parses the column 'Author Keywords' (for author keywords AK),
                                        the column 'Index Keywords' (for journal keywords IK),
                                        the column 'title' (for title keywords IK)
        _build_addresses_countries_institutions_scopus which parses the column 'Affiliations'
        _build_authors_countries_institutions_scopus which parses the column 'Authors with affiliations'
        _build_subjects_scopus which parses the column 'Source title', 'ISSN'
        _build_sub_subjects_scopus which parses the column 'Source title', 'ISSN'
        _build_articles_scopus which parses the columns 'Authors','Year','Source title','Volume',
            'Page start','DOI','Document Type','Language of Original Document','Title','ISSN'

    '''
    
    # Standard library imports
    import json
    import os
    from pathlib import Path
    
    # 3rd party imports
    import numpy as np
    import pandas as pd 
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SCOPUS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SCOPUS_CAT_CODES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import SCOPUS_JOURNALS_ISSN_CAT
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import UNKNOWN
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import USECOLS_SCOPUS
    from BiblioAnalysis_Utils.BiblioParsingUtils import check_and_drop_columns
    from BiblioAnalysis_Utils.BiblioParsingUtils import normalize_journal_names
    
    pub_id_alias = COL_NAMES['keywords'][0]
    keyword_alias = COL_NAMES['keywords'][1]

    list_data_base = []
    for path, _, files in os.walk(in_dir_parsing):
        list_data_base.extend(Path(path) / Path(file) for file in files 
                                                      if file.endswith(".csv"))
    
    # Selecting the first csv file
    filename = list_data_base[0]
    
    # Setting the specific file paths for subjects ans sub-subjects assignement for scopus corpuses    
    path_scopus_cat_codes = Path(__file__).parent / rep_utils / Path(SCOPUS_CAT_CODES)
    path_scopus_journals_issn_cat = Path(__file__).parent / rep_utils / Path(SCOPUS_JOURNALS_ISSN_CAT)

    # Reading and checking the corpus file
    df_corpus = pd.read_csv(in_dir_parsing / Path(filename))     
    df_corpus = check_and_drop_columns(SCOPUS,df_corpus,filename)    
    df_corpus = _check_affiliation_column_scopus(df_corpus)
    df_corpus = df_corpus.replace(np.nan,UNKNOWN,regex=True)
    df_corpus = normalize_journal_names(SCOPUS,df_corpus)

    # Initializing the dic_failed dict for the parsing control
    dic_failed = {}
    dic_failed['number of article'] = len(df_corpus)
    
    # Building the file for authors (.dat)
    item = 'AU' 
    df_AU = _build_authors_scopus(df_corpus)
    df_AU.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]), 
                 index=False,
                 sep='\t')

    # Building and saving the files for keywords
    df_keyword_AK,df_keyword_IK, df_keyword_TK = _build_keywords_scopus(df_corpus,dic_failed=dic_failed)    
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
    df_AD, df_CU, df_I  = _build_addresses_countries_institutions_scopus(df_corpus, dic_failed)
      # Saving addresses file (.dat)
    df_AD.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                 index=False,
                 sep='\t')
      # Saving countries file (.dat)  
    item = 'CU'       
    df_CU.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                 index=False, 
                 sep='\t')
      # Saving institutions file (.dat)    
    item = 'I'   
    df_I.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')    

    # Building and saving the file for authors and their institutions (.dat) 
    item = 'I2'
    df_I2 = _build_authors_countries_institutions_scopus(df_corpus, dic_failed, inst_filter_list)
    df_I2.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item] ), 
                 index=False,
                 sep='\t')

    # Building and saving the file for subjects (.dat)
    item = 'S'
    df_S = _build_subjects_scopus(df_corpus,
                                  path_scopus_cat_codes,
                                  path_scopus_journals_issn_cat,
                                  dic_failed=dic_failed)
    df_S.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')

    # Building and saving the file for sub-subjects (.dat)
    item = 'S2'  
    df_S2 = _build_sub_subjects_scopus(df_corpus,
                                       path_scopus_cat_codes,
                                       path_scopus_journals_issn_cat,
                                       dic_failed=dic_failed)
    df_S2.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                 index=False, 
                 sep='\t')

    # Building and saving the file for articles (.dat)
    item = 'A'  
    df_A = _build_articles_scopus(df_corpus)
    df_A.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False,
                sep='\t')

    # Building and saving the file for references (.dat)
    item = 'R'  
    df_R = _build_references_scopus(df_corpus)
    df_R.to_csv(Path(out_dir_parsing) / Path(DIC_OUTDIR_PARSING[item]),
                index=False, 
                sep='\t')
    
    # Saving the dic_failed dict for the parsing control (.json)
    with open(Path(out_dir_parsing) / Path('failed.json'), 'w') as write_json:
        json.dump(dic_failed, write_json,indent=4)
        
        