"""Module for setting globals specific to publications management and analysis.
"""

__all__ = ['AFFIL_TYPES_USECOLS',
           'ANALYSIS_IF',
           'ARCHI_BACKUP',
           'ARCHI_EXTRACT',
           'ARCHI_IF',
           "ARCHI_AFFILIATIONS",
           'ARCHI_ORPHAN',
           'ARCHI_RESULTS',
           'ARCHI_YEAR',
           'AUTHORS_FULL_LIST_NAME_CORRECTION',
           'BDD_LIST',
           'BM_LOW_WORDS_LIST',
           'COL_HASH',
           'COL_NAMES',
           'COL_NAMES_ADD',
           'COL_NAMES_AUTHOR_ANALYSIS',
           'COL_NAMES_COMPL',
           'COL_NAMES_DOCTYPE_ANALYSIS',
           'COL_NAMES_EXT',
           'COL_NAMES_IF_ANALYSIS',
           'COL_NAMES_ORTHO',
           'COL_NAMES_PUB_NAMES',
           'CONFIG_FOLDER',
           'COUNTRIES_CONTINENT',
           'DATATYPE_LIST',
           'DB_ID_COLS',
           'DOC_TYPE_DICT',
           'EMPTY',
           'EXT_DOCS_COL_ADDS_LIST',
           'FILL_EMPTY_KEY_WORD',
           'FIRST_BDD',
           'HOMONYM_FLAG',
           'IDS_FILE_BASE',
           'KPI_KEYS_DICT',
           'KPI_KEYS_ORDER_DICT',
           'LOG_FILE',
           'LOG_FOLDER',
           'NOT_AVAILABLE',
           'OTHER_DOCTYPE',
           'OTP_SHEET_NAME_BASE',
           'OUTSIDE_ANALYSIS',
           'PARSING_CONFIG_FILE',
           'PARSING_ITEMS_LIST',
           'PARSING_KEYS_CONVERT_DIC',
           'PARSING_KEYS_DIC',
           'PARSING_PERF',
           'PRINT_DICT',
           'RAWDATA_CORRECT',
           'RESULTS_TO_SAVE',
           'ROW_COLORS',
           'SCOPUS',
           'SCOPUS_CAT_CODES',
           'SCOPUS_JOURNALS_ISSN_CAT',
           'SCOPUS_RAWDATA_EXTENT',
           'SHEET_NAMES_ORPHAN',
           'SHEET_SAVE_OTP',
           'SHEETS_SEARCH',
           'STAT_FILE_DICT',
           'STAT_ROW_NAMES',
           'SYMB_CHANGE',
           'TAB',
           'TSV_SAVE_EXTENT',
           'UNKNOWN',
           'UNKNOWN_COUNTRY',
           'WOS',
           'WOS_RAWDATA_EXTENT',
           'XL_INDEX_BASE',
          ]

# 3rd party imports
import bpfuncts as bp

# local imports
import bmfuncts.employees_globals as bm_eg


# Setting 3rd party globals
AFFIL_TYPES_USECOLS = bp.AFFIL_TYPES_USECOLS
COL_NAMES = bp.COL_NAMES
COUNTRIES_CONTINENT = bp.COUNTRIES_CONTINENT
EMPTY = bp.EMPTY
PARSING_ITEMS_LIST = bp.PARSING_ITEMS_LIST
SCOPUS = bp.SCOPUS
SCOPUS_CAT_CODES = bp.SCOPUS_CAT_CODES
SCOPUS_JOURNALS_ISSN_CAT = bp.SCOPUS_JOURNALS_ISSN_CAT
SCOPUS_RAWDATA_EXTENT = bp.SCOPUS_RAWDATA_EXTENT
SYMB_CHANGE = bp.SYMB_CHANGE
UNKNOWN = bp.UNKNOWN
UNKNOWN_COUNTRY = bp.UNKNOWN_COUNTRY
WOS = bp.WOS
WOS_RAWDATA_EXTENT = bp.WOS_RAWDATA_EXTENT

# Setting the number of spaces for indentation of prints
# Use of "\t" in prints will set 8 spaces by default
TAB = bp.TAB

# Setting parameters of corpuses extraction
BDD_LIST = [SCOPUS, WOS]
FIRST_BDD = SCOPUS

DB_ID_COLS = {WOS      : COL_NAMES['wos_id'][0],
              SCOPUS   : COL_NAMES['scopus_id'][0],
              "all_dbs": "DB_id_col",
              }

# Setting general parameters for files
LOG_FILE = "Log"
LOG_FOLDER = "BM-Log files"
CONFIG_FOLDER = 'ConfigFiles'
PARSING_CONFIG_FILE = 'BiblioParsing_config.json'
PARSING_PERF = "Parsing_perf.json"
IDS_FILE_BASE = "_IDs.xlsx"
RAWDATA_CORRECT = {'authors'  : "_Auteurs corrigés.xlsx",
                   'addresses': "_Adresses corrigées.xlsx",}
SHEETS_SEARCH = ".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"
TSV_SAVE_EXTENT = "dat"
XL_INDEX_BASE = 1

# Setting if the full list of authors is based on the corrected author names
AUTHORS_FULL_LIST_NAME_CORRECTION = False

# Setting list of raw data types
DATATYPE_LIST = ["Scopus & WoS", "Scopus-HAL & WoS", "WoS", "Scopus"]

ARCHI_BACKUP = {"root": "Sauvegarde de secours"}

ARCHI_EXTRACT = {"root"             : "Extractions Institut",
                 SCOPUS             : {"root"           : "ScopusExtractions_Files",
                                       DATATYPE_LIST[0] : "scopus",
                                       DATATYPE_LIST[1] : "scopus_hal",
                                       DATATYPE_LIST[2] : "scopus",
                                       DATATYPE_LIST[3] : "scopus",
                                       "file_extent"    : '.' + SCOPUS_RAWDATA_EXTENT,
                                       "added_dois_file": " hal_added_dois.xlsx",
                                      },
                 WOS                : {"root"           : "WosExtractions_Files",
                                       DATATYPE_LIST[0] : "wos",
                                       DATATYPE_LIST[1] : "wos",
                                       DATATYPE_LIST[2] : "wos",
                                       DATATYPE_LIST[3] : "wos",
                                       "file_extent"    : '.' + WOS_RAWDATA_EXTENT,
                                      },
                 "empty-file folder": "Fichier vierge",
                 "archiv"           : "Archives",
                 "categories"       : "Catégories"
                }

ARCHI_IF = {"root"                  : "Impact Factor",
            "all IF"                : "IF all years.xlsx",
            "missing"               : "ISSN_manquants.xlsx",
            "missing_issn_base"     : "_ISSN manquants.xlsx",
            "missing_if_base"       : "_IF manquants.xlsx",
            "institute_if_all_years": "_IF all years.xlsx",
           }

ARCHI_AFFILIATIONS = {"root"                : "Traitement Institutions",
                      "institute_affil_base": "Institute_affiliations.xlsx",
                      "inst_types_base"     : "Institutions_types.xlsx",
                      "affiliations_base"   : "Country_affiliations.xlsx",
                      "country_towns_base"  : "Country_towns.xlsx",
                      "unkept_affil_base"   : "Unkept_affiliations.xlsx",
                     }

ARCHI_ORPHAN = {"root"               : "Traitement Orphan",
                "orthograph file"    : "Orthographe.xlsx",
                "employees adds file": "Effectifs additionnels.xlsx",
                "complementary file" : "Autres corrections.xlsx",
               }

ARCHI_RESULTS = {"root"                    : "Sauvegarde des résultats",
                 "dedup_parsing"           : "Synthèse des extractions",
                 "false_addresses_file"    : 'Adresses à corriger.xlsx',
                 "corrected_addresses_file": 'Adresses corrigées conservées.xlsx',
                 "hash_id"                 : "Identifiants universels",
                 "merge"                   : "Croisement auteurs-effectifs",
                 "homonyms"                : "Résolution homonymes",
                 "pub-lists"               : "Listes consolidées des publications",
                 "doctypes"                : "Analyse par types de document",
                 "impact-factors"          : "Analyse des facteurs d'impact",
                 "authors_prod"            : "Analyse par auteurs",
                 "keywords"                : "Analyse des mots clefs",
                 "countries"               : "Analyse géographique",
                 "affiliations"            : "Analyse des collaborations",
                 "subjects"                : "Analyse des thématiques",
                 "kpis"                    : "Synthèse des indicateurs",
                 "kpis file name base"     : "Synthèse des KPIs",
                 DATATYPE_LIST[0]          : "Scopus&Wos",
                 DATATYPE_LIST[1]          : "HalScopus&Wos",
                 DATATYPE_LIST[2]          : "Wos",
                 DATATYPE_LIST[3]          : "Scopus",
                }

ARCHI_YEAR = {"analyses"                           : "5 - Analyses",
              "authors analysis"                   : "Auteurs",
              "doctype analysis"                   : "Edition",
              "if analysis"                        : "IFs",
              "keywords analysis"                  : "Mots clefs",
              "subjects analysis"                  : "Thématique",
              "countries analysis"                 : "Géographique",
              "institute-country weight file base" : "Statistiques_",
              "affiliations analysis"              : "Collaborations",
              "authors file name"                  : "Informations auteur par publication",
              "authors weight file name"           : "Statistiques par auteurs",
              "countries file name"                : "Pays par publication",
              "book weight file name"              : "Statistiques par ouvrage",
              "country weight file name"           : "Statistiques par pays",
              "continent weight file name"         : "Statistiques par continent",
              "journal weight file name"           : "Statistiques par journal",
              "proceedings weight file name"       : "Statistiques par actes de conférence",
              "norm affils file name"              : "Institutions normalisées",
              "raw affils file name"               : "Institutions brutes",
              "affiliations distribution file name": "Distribution institutions par types",
              "merge folder name"                  : "0 - BDD multi mensuelle",
              "merge file name"                    : "submit.xlsx",
              "orphan file name"                   : "orphan.xlsx",
              "hash_id file name"                  : "hash_id.xlsx",
              "homonymes folder"                   : "1 - Consolidation Homonymes",
              "homonymes file name base"           : "Fichier Consolidation",
              "OTP folder"                         : "2 - OTP",
              "OTP file name base"                 : "fichier_ajout_OTP",
              "pub list folder"                    : "3 - Résultats Finaux",
              "pub list file name base"            : "Liste consolidée",
              "invalid file name base"             : "Liste des invalides",
              "history folder"                     : "4 - Informations",
              "kept homonyms file name"            : "Homonymes conservés.xlsx",
              "kept OTPs file name"                : "OTPs conservés.xlsx",
              "corpus"                             : "Corpus",
              "concat"                             : "concatenation",
              "dedup"                              : "deduplication",
              "scopus"                             : "scopus",
              "wos"                                : "wos",
              "parsing"                            : "parsing",
              "rawdata"                            : "rawdata",
              "addresses_to_correct_file_base"     : '_Adresses à corriger.xlsx',
              "corrected_addresses_file_base"      : '_Adresses corrigées conservées.xlsx',
              "drop articles file name"            : "drop_articles.xlsx",
              "drop authaffils file name"          : "drop_authsinst.xlsx",
             }

# Setting list of final results to save
RESULTS_TO_SAVE = ["hash_ids", "merge", "pub_lists", "ifs", "kws","countries", "continents",
                   "authors", "affiliations", "doctypes", "homonyms", "institute_country"]

BM_LOW_WORDS_LIST = ["of", "and", "on"]

OTP_SHEET_NAME_BASE = "OTP"

# Colors for row background in EXCEL files
ROW_COLORS = {'odd'      : '0000FFFF',
              'even'     : '00CCFFCC',
              'highlight': '00FFFF00',
             }


DOC_TYPE_DICT = {'articles'   : ['Article', 'Article; Early Access', 'Correction',
                                 'Correction; Early Access', 'Data Paper', 'Erratum',
                                 'Letter', 'Note', 'Review', 'Review; Early Access',
                                 'Short Survey'],
                 'books'      : ['Article; Book Chapter', 'Book', 'Book Chapter',
                                 'Biographical-Item', 'Editorial', 'Editorial Material'],
                 'proceedings': ['Conference Paper', 'Meeting Abstract',
                                 'Article; Proceedings Paper'],
                }

DOCTYPE_TO_SAVE_DICT = {'Articles & Proceedings': DOC_TYPE_DICT['articles'] + \
                                                  DOC_TYPE_DICT['proceedings'],
                        'Books & Editorials'    : DOC_TYPE_DICT['books'],
                       }

OTHER_DOCTYPE = 'Others'

FILL_EMPTY_KEY_WORD = 'unknown'
NOT_AVAILABLE       = 'Not available'
OUTSIDE_ANALYSIS    = 'Not analysed'
HOMONYM_FLAG        = "HOMONYM"


COL_HASH = {'hash_id'   : "Hash_id",
            'homonym_id': "Homonyme auteur",
            'OTP'       : "OTP",
           }


SHEET_SAVE_OTP = {'hash_OTP': 'Hash_ID-OTP',
                  'doi_OTP' : 'DOI-OTP'}


COL_NAMES_ADD = {'nom prénom'        : "Nom, Prénom de l'auteur ",
                 'nom prénom liste'  : "Liste ordonnée des auteurs de l'institut",
                 'liste biblio'      : "Référence bibliographique complète",
                 'liste auteurs'     : "Liste ordonnée de tous les auteurs",
                 'author_type'       : "Type de l'auteur",
                 'homonym'           : "Homonymes",
                 'list OTP'          : "Choix de l'OTP",
                 'final OTP'         : "OTP",
                 'corpus_year'       : "Année de première publication",
                 'IF en cours'       : "IF en cours",
                 'IF année publi'    : "IF de l'année de première publication",
                 'IF clarivate'      : "IF",
                 'e-ISSN'            : "e-ISSN",
                 'database ISSN'     : "ISSN via source",
                 'pub number'        : "Nombre de publications",
                 'weight'            : "Weight",
                 'country'           : "Pays",
                 'continent'         : "Continent",
                 'affiliations'      : "Institution",
                 'affils number'     : "Nombre d'entités",
                 'affils list'       : "Liste des entités",
                 'pub_ids list'      : "Liste des Pub_ids",
                 'co-auth affils'    : "Institutions co-autrices",
                 'address ID'        : "Adresse_id",
                 'journal_pub_nb'    : "Nombre de publications de journal",
                 'proceedings_pub_nb': "Nombre de publications d'actes de conférence",
                 'book_pub_nb'       : "Nombre d'ouvrages ou de chapitres",
                 'name_as_auth'      : "Nom d'auteur",
                 'name_as_empl'      : "Nom de salarié",
                 'pub_type'          : "Type des co-auteurs",
                 'source'            : "Extraction",
                 'full_name'         : 'Full_name',
                 'last_name'         : 'Co_author_joined',
                 'first_name'        : bm_eg.EMPLOYEES_ADD_COLS['first_name_initials'],
                }

PUB_LAST_NAME      = 'Nom pub'
PUB_INITIALS       = 'Initiales pub'
EMPLOYEE_LAST_NAME = 'Nom eff'
EMPLOYEE_INITIALS  = 'Initiales eff'

COL_NAMES_ORTHO = {'last name init': PUB_LAST_NAME,
                   'initials init' : PUB_INITIALS,
                   'last name new' : EMPLOYEE_LAST_NAME,
                   'initials new'  : EMPLOYEE_INITIALS,
                  }


COL_NAMES_COMPL = {'last name init'  : PUB_LAST_NAME,
                   'initials init'   : PUB_INITIALS,
                   'matricule'       : 'Matricule',
                   'last name new'   : EMPLOYEE_LAST_NAME,
                   'initials new'    : EMPLOYEE_INITIALS,
                   'dept'            : 'Dept',
                   'publication year': 'Année pub',
                   'hash id'         : 'Hash_id',
                  }

COL_NAMES_EXT = {'last name': PUB_LAST_NAME,
                 'initials' : PUB_INITIALS,
                }


SHEET_NAMES_ORPHAN = {"to replace"   : "Spécifique par publi",
                      "to remove"    : "Externes ",
                      "docs to add"  : "Doctorants externes",
                      "others to add": "Autres externes",
                     }


COL_NAMES_PUB_NAMES = {'last name': PUB_LAST_NAME,
                       'initials' : PUB_INITIALS,
                      }

EXT_DOCS_COL_ADDS_LIST = [COL_NAMES_ADD['homonym'],
                          COL_NAMES_ADD['author_type'],]

ANALYSIS_IF = COL_NAMES_ADD['IF année publi']

COL_NAMES_IF_ANALYSIS = {'corpus_year'  : "Corpus year",
                         'journal_short': "Journal_court",
                         'articles_nb'  : "Number",
                         'analysis_if'  : "Analysis IF",
                        }

COL_NAMES_AUTHOR_ANALYSIS = {'author_nb'      : "Nombre d'auteurs",
                             'is_first_author': "Status premier auteur",
                             'is_last_author' : "Status dernier auteur",
                             'pub_nb'         : "Nombre de publications",
                            }

COL_NAMES_DOCTYPE_ANALYSIS = {'articles'   : {'doctype_col': "Journal",
                                              'weight_col' : "Nombre d'articles"},
                              'proceedings': {'doctype_col': "Actes de conférence",
                                              'weight_col' : "Nombre d'articles"},
                              'books'      : {'doctype_col': "Ouvrage",
                                              'weight_col' : "Nombre de chapitres"},
                             }

KPI_KEYS_ORDER_DICT = {0  : "Année de publication",
                       1  : "Publications",
                       2  : "Articles",
                       3  : "Articles de journal",
                       4  : "Articles de conférence",
                       5  : "Chapitres d'ouvrage",
                       6  : "Journaux",
                       7  : "Actes de conférence",
                       8  : "Ouvrages",
                       9  : "Moyenne d'articles par journal",
                       10 : "Moyenne d'articles par conférence",
                       11 : "Moyenne de chapitres par ouvrage",
                       12 : "Maximum d'articles par journal",
                       13 : "Maximum d'articles par conférence",
                       14 : "Maximum de chapitres par ouvrage",
                       15 : "Articles de conférence (%)",
                       16 : "Chapitres d'ouvrage (%)",
                       17 : "Facteur d'impact d'analyse",
                       18 : "Facteur d'impact maximum",
                       19 : "Facteur d'impact minimum",
                       20 : "Facteur d'impact moyen",
                       21 : "Articles sans facteur d'impact",
                       22 : "Articles sans facteur d'impact (%)",
                      }

KPI_KEYS_DICT = {'articles'   : [6,3,9,12],
                 'proceedings': [7,4,10,13],
                 'books'      : [8,5,11,14],
                 'complements': [1,2,15,16],
                }


STAT_KEYS_LIST = ["country per pub",
                  "affils per country per pub",
                  "affils and pub per country"]

STAT_NAMES_LIST = ["Stat-Publications par institutions",
                   "Stat-Institutions par publication",
                   "Stat_Institutions & Publications par pays",]

STAT_DF_TITLES_LIST = ['affil_country_pub', 'pub_country_affils', 'country_affils_pub']

STAT_VALUES_TUP = tuple(zip(STAT_NAMES_LIST, STAT_DF_TITLES_LIST))

STAT_FILE_DICT = dict(zip(STAT_KEYS_LIST, STAT_VALUES_TUP))

STAT_ROW_NAMES = {'all'                : "Au moins un de l'Institut",
                  'institute_only'     : "Uniquement de l'Institut",
                  'country_only'       : "Nationaux uniquement",
                  'country_at_least'   : "Nationaux et internationaux",
                  'out_of_country_only': "Internationaux uniquement",
                 }

PRINT_DICT = {'purple'   : '\033[95m',
              'cyan'     : '\033[96m',
              'darkcyan' : '\033[36m',
              'blue'     : '\033[94m',
              'green'    : '\033[92m',
              'yellow'   : '\033[93m',
              'red'      : '\033[91m',
              'bold'     : '\033[1m',
              'underline': '\033[4m',
              'end'      : '\033[0m',
             }


# Order in the following lists should not be changed

PARSING_KEYS_DIC = {'all'             : ["pub", "auth", "addr", "countries", "affils",
                                         "authaddr", "aukw", "ikw", "tkw", "subj",
                                         "subsubj", "refs", "normaffils", "rawaddr"],
                    'parsing'         : ["pub", "auth", "addr", "countries", "affils",
                                         "authaddr", "aukw", "ikw", "tkw", "subj",
                                         "subsubj", "refs"],
                    'parsing_pub'     : "pub",
                    'dedup_pub_nb'    : ["pub", "authaddr"],
                    'merge'           : ["pub", "addr", "auth", "authaddr"],
                    'unknown_country' : ["addr", "auth", "authaddr", "countries"],
                    'correct_parsing' : ["addr", "authaddr", "countries"],
                    'build_addresses' : ["addr", "authaddr"],
                    'au_analysis'     : ["auth"],
                    'kw_analysis'     : ["aukw", "ikw", "tkw"],
                   }

PARSING_KEYS_CONVERT_DIC = dict(zip(PARSING_KEYS_DIC['all'], PARSING_ITEMS_LIST))

PARSING_KEYS_REVERT_DIC = {PARSING_KEYS_CONVERT_DIC[key]: key for key in PARSING_KEYS_DIC['all']}
