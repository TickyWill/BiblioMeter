"""Module for setting globals specific to publications
management and analysis.
"""

__all__ = ['ANALYSIS_IF',
           'ARCHI_BACKUP',
           'ARCHI_BDD_MULTI_ANNUELLE',
           'ARCHI_EXTRACT',
           'ARCHI_IF',
           "ARCHI_INSTITUTIONS",
           'ARCHI_ORPHAN',
           'ARCHI_RESULTS',
           'ARCHI_YEAR',
           'BDD_LIST',
           'BM_LOW_WORDS_LIST',
           'COL_HASH',
           'COL_NAMES_AUTHOR_ANALYSIS',
           'COL_NAMES_BM',
           'COL_NAMES_BONUS',
           'COL_NAMES_COMPL',
           'COL_NAMES_EXT',
           'COL_NAMES_IF_ANALYSIS',
           'COL_NAMES_ORTHO',
           'COL_NAMES_PUB_NAMES',
           'CONFIG_FOLDER',
           'DATATYPE_LIST',
           'DF_TITLES_LIST',
           'DOC_TYPE_DICT',
           'EXT_DOCS_COL_ADDS_LIST',
           'FILL_EMPTY_KEY_WORD',
           'HOMONYM_FLAG',
           'KPI_KEYS_ORDER_DICT',
           'NOT_AVAILABLE_IF',
           'OTHER_DOCTYPE',
           'OTP_SHEET_NAME_BASE',
           'OUTSIDE_ANALYSIS',
           'PARSING_CONFIG_FILE',
           'PARSING_PERF',
           'RESULTS_TO_SAVE',
           'ROW_COLORS',
           'SHEET_NAMES_ORPHAN',
           'SHEET_SAVE_OTP',
           'TSV_SAVE_EXTENT',
           'XL_INDEX_BASE'
          ]

# 3rd party imports
import BiblioParsing as bp

# local imports
import bmfuncts.employees_globals as eg

# Setting the databases of corpuses extraction
BDD_LIST = [bp.SCOPUS, bp.WOS]

# Setting list of raw data types
DATATYPE_LIST = ["Scopus & WoS", "Scopus-HAL & WoS", "WoS"]

DF_TITLES_LIST = ["Pub_df", "Homonyms_df", "OTP_df", "IF_db_df",
                  "Authors_df", "Authors_stat_df", "KPI_df",
                  "KW_df", "Geo_df", "Institutions_df", "IF_anal_df"]

CONFIG_FOLDER = 'ConfigFiles'

PARSING_CONFIG_FILE = 'BiblioParsing_config.json'

PARSING_PERF = "Parsing_perf.json"    # 'failed.json'

TSV_SAVE_EXTENT = "dat"

XL_INDEX_BASE = 1

ARCHI_BACKUP = {"root" : "Sauvegarde de secours"}

ARCHI_BDD_MULTI_ANNUELLE = {"root"                  : "BDD multi annuelle",
                            "concat file name base" : "Concaténation par",
                            "kpis file name base"   : "Synthèse des KPIs",
                           }

ARCHI_EXTRACT = {"root"             : "Extractions Institut",
                 bp.SCOPUS          : {"root"          : "ScopusExtractions_Files",
                                       DATATYPE_LIST[0]: "scopus",
                                       DATATYPE_LIST[1]: "scopus_hal",
                                       DATATYPE_LIST[2]: "scopus",
                                       "file_extent"   : '.' + bp.SCOPUS_RAWDATA_EXTENT,
                                      },
                 bp.WOS             : {"root"          : "WosExtractions_Files",
                                       DATATYPE_LIST[0]: "wos",
                                       DATATYPE_LIST[1]: "wos",
                                       DATATYPE_LIST[2]: "wos",
                                       "file_extent"   : '.' + bp.WOS_RAWDATA_EXTENT,
                                      },
                 "empty-file folder": "Fichier vierge"
                }

ARCHI_IF = {"root"                   : "Impact Factor",
            "all IF"                 : "IF all years.xlsx",
            "missing"                : "ISSN_manquants.xlsx",
            "missing_issn_base"      : "_ISSN manquants.xlsx",
            "missing_if_base"        : "_IF manquants.xlsx",
            "institute_if_all_years" : "_IF all years.xlsx",
           }

ARCHI_INSTITUTIONS = {"root"                 : "Traitement Institutions",
                      "institute_affil_base" : "Institute_affiliations.xlsx",
                      "inst_types_base"      : "Institutions_types.xlsx",
                      "affiliations_base"    : "Country_affiliations.xlsx",
                      "country_towns_base"   : "Country_towns.xlsx",
                      "unkept_affil_base"    : "Unkept_affiliations.xlsx",
                     }

ARCHI_ORPHAN = {"root"                : "Traitement Orphan",
                "orthograph file"     : "Orthographe.xlsx",
                "employees adds file" : "Effectifs additionnels.xlsx",
                "complementary file"  : "Autres corrections.xlsx",
               }

ARCHI_RESULTS = {"root"                : "Sauvegarde des résultats",
                 "dedup_parsing"       : "Synthèse des extractions",
                 "hash_id"             : "Identifiants universels",
                 "pub-lists"           : "Listes consolidées des publications",
                 "impact-factors"      : "Analyse des facteurs d'impact",
                 "authors_prod"        : "Analyse par auteurs",
                 "keywords"            : "Analyse des mots clefs",
                 "countries"           : "Analyse géographique",
                 "institutions"        : "Analyse des collaborations",
                 "subjects"            : "Analyse des thématiques",
                 "kpis"                : "Synthèse des indicateurs",
                 "kpis file name base" : "Synthèse des KPIs",
                 DATATYPE_LIST[0]      : "Scopus&Wos",
                 DATATYPE_LIST[1]      : "HalScopus&Wos",
                 DATATYPE_LIST[2]      : "Wos",
                }


ARCHI_YEAR = {
              "analyses"                  : "5 - Analyses",
              "authors analysis"          : "Auteurs",
              "if analysis"               : "IFs",
              "keywords analysis"         : "Mots clefs",
              "subjects analysis"         : "Thématique",
              "countries analysis"        : "Géographique",
              "institutions analysis"     : "Collaborations",
              "authors file name"         : "Informations auteur par publication",
              "authors weight file name"  : "Statistiques par auteurs",
              "countries file name"       : "Pays par publication",
              "country weight file name"  : "Statistiques par pays",
              "continent weight file name": "Statistiques par continent",
              "norm inst file name"       : "Institutions normalisées",
              "raw inst file name"        : "Institutions brutes",
              "bdd mensuelle"             : "0 - BDD multi mensuelle",
              "submit file name"          : "submit.xlsx",
              "orphan file name"          : "orphan.xlsx",
              "hash_id file name"         : "hash_id.xlsx",
              "homonymes folder"          : "1 - Consolidation Homonymes",
              "homonymes file name base"  : "Fichier Consolidation",
              "OTP folder"                : "2 - OTP",
              "OTP file name base"        : "fichier_ajout_OTP",
              "pub list folder"           : "3 - Résultats Finaux",
              "pub list file name base"   : "Liste consolidée",
              "invalid file name base"    : "Liste des invalides",
              "history folder"            : "4 - Informations",
              "kept homonyms file name"   : "Homonymes conservés.xlsx",
              "kept OTPs file name"       : "OTPs conservés.xlsx",
              "corpus"                    : "Corpus",
              "concat"                    : "concatenation",
              "dedup"                     : "deduplication",
              "scopus"                    : "scopus",
              "wos"                       : "wos",
              "parsing"                   : "parsing",
              "rawdata"                   : "rawdata",
             }

# Setting list of final results to save
RESULTS_TO_SAVE = ["hash_ids", "pub_lists", "ifs", "kws", "countries", "continents", "authors"]

BM_LOW_WORDS_LIST = ["of", "and", "on"]

OTP_SHEET_NAME_BASE = "OTP"

# Colors for row background in EXCEL files
ROW_COLORS = {'odd'      : '0000FFFF',
              'even'     : '00CCFFCC',
              'highlight': '00FFFF00',
             }


DOC_TYPE_DICT = {'Articles'   : ['Article', 'Article; Early Access', 'Correction',
                                 'Correction; Early Access', 'Data Paper', 'Erratum',
                                 'Letter', 'Note', 'Review', 'Review; early access',
                                 'Short Survey'],
                 'Books'      : ['Article; Book Chapter', 'Book', 'Book chapter',
                                 'Biographical-Item', 'Editorial', 'Editorial Material'],
                 'Proceedings': ['Conference Paper', 'Meeting Abstract',
                                 'Article; Proceedings Paper'],
                }

DOCTYPE_TO_SAVE_DICT = {'Articles & Proceedings' : DOC_TYPE_DICT['Articles'] + \
                                                   DOC_TYPE_DICT['Proceedings'],
                        'Books & Editorials'     : DOC_TYPE_DICT['Books'],
                       }

OTHER_DOCTYPE = 'Others'

FILL_EMPTY_KEY_WORD = 'unknown'
NOT_AVAILABLE_IF    = 'Not available'
OUTSIDE_ANALYSIS    = 'Not analysed'
HOMONYM_FLAG        = "HOMONYM"


COL_HASH = {'hash_id'    : "Hash_id",
            'homonym_id' : "Homonyme auteur",
            'OTP'        : "OTP",
           }


SHEET_SAVE_OTP = {'hash_OTP': 'Hash_ID-OTP',
                  'doi_OTP' : 'DOI-OTP'}


COL_NAMES_BONUS = {'nom prénom'       : "Nom, Prénom de l'auteur ",
                   'nom prénom liste' : "Liste ordonnée des auteurs ",
                   'liste biblio'     : "Référence bibliographique complète",
                   'author_type'      : "Type de l'auteur",
                   'homonym'          : "Homonymes",
                   'list OTP'         : "Choix de l'OTP",
                   'final OTP'        : "OTP",
                   'corpus_year'      : "Année de première publication",
                   'IF en cours'      : "IF en cours",
                   'IF année publi'   : "IF de l'année de première publication",
                   'IF clarivate'     : "IF",
                   'e-ISSN'           : "e-ISSN",
                   'database ISSN'    : "ISSN via source",
                   'pub number'       : "Nombre de publications",
                   'weight'           : "Weight",
                   'country'          : "Pays",
                   'continent'        : "Continent",
                   'pub_ids list'     : "Liste des Pub_ids",
                  }



COL_NAMES_BM = {'Dpts'      : eg.EMPLOYEES_ADD_COLS['dpts_list'],
                'Servs'     : eg.EMPLOYEES_ADD_COLS['servs_list'],
                'First_name': eg.EMPLOYEES_ADD_COLS['first_name_initials'],
                'Last_name' : 'Co_author_joined',
                'Full_name' : 'Full_name',
                'Homonym'   : COL_NAMES_BONUS['homonym'],
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


COL_NAMES_COMPL = {'last name init'   : PUB_LAST_NAME,
                   'initials init'    : PUB_INITIALS,
                   'matricule'        : 'Matricule',
                   'last name new'    : EMPLOYEE_LAST_NAME,
                   'initials new'     : EMPLOYEE_INITIALS,
                   'dept'             : 'Dept',
                   'publication year' : 'Année pub',
                   'hash id'          : 'Hash_id',
                  }

COL_NAMES_EXT = {'last name'   : PUB_LAST_NAME,
                 'initials'    : PUB_INITIALS,
                }


SHEET_NAMES_ORPHAN = {"to replace"    : "Spécifique par publi",
                      "to remove"     : "Externes ",
                      "docs to add"   : "Doctorants externes",
                      "others to add" : "Autres externes",
                     }


COL_NAMES_PUB_NAMES = {'last name' : PUB_LAST_NAME,
                       'initials'  : PUB_INITIALS,
                      }

EXT_DOCS_COL_ADDS_LIST = [COL_NAMES_BONUS['homonym'],
                          COL_NAMES_BONUS['author_type'],]

ANALYSIS_IF = COL_NAMES_BONUS['IF année publi']

COL_NAMES_IF_ANALYSIS = {'corpus_year'   : "Corpus year",
                         'journal_short' : "Journal_court",
                         'articles_nb'   : "Number",
                         'analysis_if'   : "Analysis IF",
                        }

COL_NAMES_AUTHOR_ANALYSIS = {'author_nb'       : "Nombre d'auteurs",
                             'is_first_author' : "Status premier auteur",
                             'is_last_author'  : "Status dernier auteur",
                             'pub_nb'          : "Nombre de publications",
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
