__all__ = ['ANALYSIS_IF',
           'ARCHI_BACKUP',
           'ARCHI_BDD_MULTI_ANNUELLE',
           'ARCHI_IF',
           'ARCHI_ORPHAN',
           'ARCHI_YEAR',
           'BAR_COLOR_RANGE',
           'BAR_COLOR_SCALE',
           'BAR_HEIGHT',
           'BAR_HEIGHT_RATIO',
           'BAR_X_RANGE',
           'BAR_Y_LABEL_MAX',
           'BAR_Y_MAX',
           'BAR_WIDTH',
           'BDD_LIST',
           'BM_COL_RENAME_DIC',
           'BM_LOW_WORDS_LIST',
           'CLOUD_BCKG', 
           'CLOUD_HEIGHT',
           'CLOUD_MAX_WORDS',
           'CLOUD_MAX_WORDS_LENGTH',
           'CLOUD_WIDTH',
           'COL_HASH',
           'COL_NAMES_BM',
           'COL_NAMES_BONUS',
           'COL_NAMES_COMPL',
           'COL_NAMES_EXT',
           'COL_NAMES_IF_ANALYSIS',
           'COL_NAMES_ORTHO',
           'COL_NAMES_PUB_NAMES',
           'DOC_TYPE_DICT',
           'EXT_DOCS_COL_ADDS_LIST',
           'FILL_EMPTY_KEY_WORD',
           'HOMONYM_FLAG',
           'KPI_KEYS_ORDER_DICT',
           'NO_IF_DOCTYPE',
           'NOT_AVAILABLE_IF',
           'ORPHAN_COL_RENAME_DIC',
           'OTP_SHEET_NAME_BASE',
           'PARSING_PERF',
           'ROW_COLORS',
           'SHEET_NAMES_ORPHAN',
           'SUBMIT_COL_RENAME_DIC',
           'TSV_SAVE_EXTENT'
          ]

# 3rd party imports
import BiblioParsing as bp

# local imports
import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg 
import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig 

# Setting the databases of corpuses extraction
BDD_LIST = [bp.SCOPUS, bp.WOS]

PARSING_PERF = "Parsing_perf.json"    # 'failed.json'

TSV_SAVE_EXTENT = "dat"

ARCHI_BACKUP = {"root" : "Sauvegarde de secours"}


ARCHI_BDD_MULTI_ANNUELLE = {"root"                      : "BDD multi annuelle",
                            "concat file name base"     : "Concaténation par",
                            "IF analysis file name base": "Synthèse des KPIs",
                           }


ARCHI_IF = {"root"                   : "Impact Factor",
            "all IF"                 : "IF all years.xlsx",
            "missing"                : "ISSN_manquants.xlsx",
            "missing_issn_base"      : "_ISSN manquants.xlsx",
            "missing_if_base"        : "_IF manquants.xlsx",
            "institute_if_all_years" : ig.INSTITUTE + "_IF all years.xlsx"}


ARCHI_ORPHAN = {"root"                : "Traitement Orphan",
                "orthograph file"     : "Orthographe.xlsx",
                "employees adds file" : "Effectifs additionnels.xlsx",
                "complementary file"  : "Autres corrections.xlsx",
               }


ARCHI_YEAR = {
              "analyses"                       : "5 - Analyses",
              "if analysis"                    : "IFs",
              "keywords analysis"              : "Mots clefs",
              "subjects analysis"              : "Thématique",
              "countries analysis"             : "Géographique",
              "institutions analysis"          : "Collaborations",
              "bdd mensuelle"                  : "0 - BDD multi mensuelle", 
              "submit file name"               : "submit.xlsx", 
              "orphan file name"               : "orphan.xlsx",
              "hash_id file name"              : "hash_id.xlsx",
              "homonymes folder"               : "1 - Consolidation Homonymes", 
              "homonymes file name base"       : "Fichier Consolidation",            
              "OTP folder"                     : "2 - OTP", 
              "OTP file name base"             : "fichier_ajout_OTP",            
              "pub list folder"                : "3 - Résultats Finaux", 
              "pub list file name base"        : "Liste consolidée",
              "history folder"                 : "4 - Informations",
              "kept homonyms file name"        : "Homonymes conservés.xlsx",
              "kept otps file name"            : "OTPs conservés.xlsx",
              "corpus"                         : "Corpus", 
              "concat"                         : "concatenation", 
              "dedup"                          : "deduplication", 
              "scopus"                         : "scopus", 
              "wos"                            : "wos", 
              "parsing"                        : "parsing", 
              "rawdata"                        : "rawdata",
             }


BM_LOW_WORDS_LIST = ["of", "and", "on"]

OTP_SHEET_NAME_BASE = "OTP"

# Colors for row background in EXCEL files
ROW_COLORS = {'odd'      : '0000FFFF',
              'even'     : '00CCFFCC',
              'highlight': '00FFFF00',
             }


DOC_TYPE_DICT = {'Articles'   : ['Article', 'Article; Early Access', 'Correction', 'Data Paper',
                                 'Erratum', 'Note', 'Review', 'Short Survey'],
                 'Books'      : ['Book', 'Book chapter', 'Article; Book Chapter', 'Editorial Material'],
                 'Proceedings': ['Conference Paper', 'Meeting Abstract', 'Article; Proceedings Paper']}

NO_IF_DOCTYPE = DOC_TYPE_DICT['Books'] + DOC_TYPE_DICT['Proceedings']
NO_IF_DOCTYPE = [x.upper() for x in NO_IF_DOCTYPE]

DOCTYPE_TO_SAVE_DICT = {'Articles & Proceedings' : DOC_TYPE_DICT['Articles'] + DOC_TYPE_DICT['Proceedings'],
                        'Books & Editorials'     : DOC_TYPE_DICT['Books'],
                       } 


FILL_EMPTY_KEY_WORD = 'unknown' 


NOT_AVAILABLE_IF    = 'Not available'


HOMONYM_FLAG = "HOMONYM"


COL_HASH = {'hash_id'    : "Hash_id",
            'homonym_id' : "Homonyme auteur",
            'otp'        : "OTP",
           }


COL_NAMES_BONUS = {'nom prénom'       : "Nom, Prénom de l'auteur " + ig.INSTITUTE, 
                   'nom prénom liste' : "Liste ordonnée des auteurs " + ig.INSTITUTE, 
                   'liste biblio'     : "Référence bibliographique complète", 
                   'author_type'      : "Type de l'auteur " + ig.INSTITUTE,
                   'homonym'          : 'Homonymes',
                   'list OTP'         : "Choix de l'OTP",
                   'final OTP'        : "OTP",
                   'corpus_year'      : "Année de première publication",
                   'IF en cours'      : "IF en cours", 
                   'IF année publi'   : "IF de l'année de première publication",
                   'IF clarivate'     : 'IF',
                   'e-ISSN'           : 'e-ISSN',
                   'database ISSN'    : "ISSN via source",
                   'pub number'       : "Nombre de publications",
                   'weight'           : "Weight",
                  }



COL_NAMES_BM = {'Dpts'      : eg.EMPLOYEES_ADD_COLS['dpts_list'], 
                'Servs'     : eg.EMPLOYEES_ADD_COLS['servs_list'],
                'First_name': eg.EMPLOYEES_ADD_COLS['first_name_initials'],
                'Last_name' : 'Co_author_joined',  # 'Co_author_joined' DOE J --> DOE
                'Full_name' : 'Full_name', # DOE J
                'Homonym'   : COL_NAMES_BONUS['homonym'],
               }

pub_last_name      = 'Nom pub'
pub_initials       = 'Initiales pub'
employee_last_name = 'Nom eff'
employee_initials  = 'Initiales eff'

COL_NAMES_ORTHO = {'last name init' : pub_last_name,
                   'initials init'  : pub_initials,
                   'last name new'  : employee_last_name,
                   'initials new'   : employee_initials,
                  }


COL_NAMES_COMPL = {'last name init'   : pub_last_name,
                   'initials init'    : pub_initials,
                   'matricule'        : 'Matricule',
                   'last name new'    : employee_last_name,
                   'initials new'     : employee_initials,
                   'dept'             : 'Dept',
                   'publication year' : 'Année pub',
                   'hash id'          : 'Hash_id',
                  }

COL_NAMES_EXT = {'last name'   : pub_last_name,
                 'initials'    : pub_initials,
                }


SHEET_NAMES_ORPHAN = {"to replace"    : "Spécifique par publi",
                      "to remove"     : "Externes " + ig.INSTITUTE,
                      "docs to add"   : "Doctorants externes",
                      "others to add" : "Autres externes",
                     }


COL_NAMES_PUB_NAMES = {'last name' : pub_last_name,
                       'initials'  : pub_initials,
                      }

EXT_DOCS_COL_ADDS_LIST = [COL_NAMES_BONUS['homonym'],          
                          COL_NAMES_BONUS['author_type'],] 

ANALYSIS_IF = COL_NAMES_BONUS['IF année publi']

COL_NAMES_IF_ANALYSIS = {'corpus_year'   : "Corpus year",
                         'journal_short' : "Journal_court",
                         'articles_nb'   : "Number",
                         'analysis_if'   : "Analysis IF",
                        } 

KPI_KEYS_ORDER_DICT = {0  : "Année de publication",
                       1  : "Nombre de publications",
                       2  : "Ouvrages",
                       3  : "Chapitres",
                       4  : "Moyenne de chapitres par ouvrage",
                       5  : "Maximum de chapitres par ouvrage",
                       6  : "Journaux & actes de conférence",
                       7  : "Journaux",
                       8  : "Articles & communications", 
                       9  : "Communications",
                       10 : "Communications (%)",
                       11 : "Articles",
                       12 : "Moyenne d'articles par journal",
                       13 : "Maximum d'articles par journal",
                       14 : "Facteur d'impact d'analyse",
                       15 : "Facteur d'impact maximum",
                       16 : "Facteur d'impact minimum",
                       17 : "Facteur d'impact moyen",
                       18 : "Articles sans facteur d'impact",
                       19 : "Articles sans facteur d'impact (%)",          
                      }


def _build_col_conversion_dic():
    """
    """
    
    # 3rd party imports
    import BiblioParsing as bp

    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
    
    dpt_col_list   = list(ig.COL_NAMES_DPT.values())     
    inst_col_list  = [tup[0] + '_' + tup[1] for tup in ig.INSTITUTE_INST_LIST]
    
    init_orphan_col_list = sum([bp.COL_NAMES['auth_inst'][:5],
                                inst_col_list,
                                [bp.COL_NAMES['authors'][2]], 
                                bp.COL_NAMES['articles'][1:11],
                                [COL_NAMES_BONUS['corpus_year']],
                                [COL_NAMES_BM['Full_name'], 
                                 COL_NAMES_BM['Last_name'], 
                                 COL_NAMES_BM['First_name']],
                               ],
                               [],
                              )

    init_submit_col_list = sum([init_orphan_col_list,
                                [COL_NAMES_BONUS['homonym']],
                                list(eg.EMPLOYEES_USEFUL_COLS.values()),
                                list(eg.EMPLOYEES_ADD_COLS.values()),
                                [COL_NAMES_BONUS['author_type'], 
                                 COL_NAMES_BONUS['liste biblio']],
                               ],
                               [],
                              )

    init_bm_col_list = sum([init_submit_col_list,
                           [COL_NAMES_BONUS['nom prénom liste'],
                            COL_NAMES_BONUS['nom prénom'],
                             ],
                            dpt_col_list, 
                           [COL_NAMES_BONUS['list OTP'],
                            COL_NAMES_BONUS['IF en cours'],
                            COL_NAMES_BONUS['IF année publi'],
                           ]
                          ],
                          [],
                         )

    final_bm_col_list = sum([["Pub_id",
                              "Auteur_id",
                              "Adresse",
                              "Pays",
                              "Institutions",
                             ],
                             inst_col_list,
                             ["Co_auteur " + ig.INSTITUTE,
                             "Premier auteur",
                             "Année de publication finale",
                             "Journal",
                             "Volume",
                             "Page",
                             "DOI",
                             "Type du document",
                             "Langue",
                             "Titre",
                             "ISSN",
                             "Année de première publication",
                             ],
                             [COL_NAMES_BM['Full_name'],
                              COL_NAMES_BM['Last_name'],
                              COL_NAMES_BM['First_name'],
                             ],
                             ["Homonymes",
                              "Matricule",
                              "Nom",
                              "Prénom",
                              "Genre",
                              "Nationalité", 
                              "Catégorie de salarié",
                              "Statut de salarié",
                              "Qualification classement",
                              "Date début contrat",
                              "Date dernière entrée",
                              "Date de fin de contrat",
                              "Dept",
                              "Serv",
                              "Labo",
                              "Affiliation",
                              "Date de naissance",
                              "Tranche d'age (5 ans)",
                             ],
                             list(eg.EMPLOYEES_ADD_COLS.values()),
                             [COL_NAMES_BONUS['author_type'], 
                              COL_NAMES_BONUS['liste biblio'],
                              COL_NAMES_BONUS['nom prénom liste'],
                              COL_NAMES_BONUS['nom prénom'],
                             ],
                              dpt_col_list,
                             [COL_NAMES_BONUS['list OTP'],
                              COL_NAMES_BONUS['IF en cours'],
                              COL_NAMES_BONUS['IF année publi'],
                             ]
                            ],
                            [],
                           )
    
    all_col_rename_dic     = dict(zip(init_bm_col_list,final_bm_col_list))
    
    final_submit_col_list  = [all_col_rename_dic[col] for col in init_submit_col_list]
    submit_col_rename_dic  = dict(zip(init_submit_col_list,final_submit_col_list))
    
    final_orphan_col_list  = [all_col_rename_dic[col] for col in init_orphan_col_list]
    orphan_col_rename_dic  = dict(zip(init_orphan_col_list,final_orphan_col_list))
    
    return (orphan_col_rename_dic, submit_col_rename_dic, all_col_rename_dic)

ORPHAN_COL_RENAME_DIC, SUBMIT_COL_RENAME_DIC, BM_COL_RENAME_DIC = _build_col_conversion_dic()


# Parameters of cloud representation 
CLOUD_BCKG             = 'ivory'
CLOUD_HEIGHT           = 600
CLOUD_WIDTH            = 400
CLOUD_MAX_WORDS        = 100
CLOUD_MAX_WORDS_LENGTH = 60

# Parameters of bar chart representation 
import plotly
import plotly.express as px

BAR_Y_LABEL_MAX  = 35          # Nb of characters
BAR_X_RANGE      = [0,10]      # Nb of articles
BAR_Y_MAX        = 60          # Nb journals (max per barchart plot)
BAR_WIDTH        = 800
BAR_HEIGHT       = 1600
BAR_HEIGHT_RATIO = 1.7
BAR_COLOR_RANGE  = [0,30]     # IFs
BAR_COLOR_SCALE  = px.colors.sequential.Rainbow
