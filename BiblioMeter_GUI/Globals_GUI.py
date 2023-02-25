__all__ = ['ROOT_PATH',
           'ARCHI_YEAR',
           'BDD_LIST',
           'DPT_LABEL_DICT',
           'CORPUSES_NUMBER',
           'COL_NAMES_BM',
           'COL_NAMES_ORPHAN',
           'PAGES_LABELS',
           'PAGES_NAMES',
           'SUBMIT_FILE_NAME', 
           'ORPHAN_FILE_NAME', 
           'SET_1', 
           'SET_OTP',
           'PPI'
           ]


# BiblioAnalysis_Utils package globals imports
from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
from BiblioAnalysis_Utils.BiblioSys import DISPLAYS

# Local globals imports
from BiblioMeter_GUI.Coordinates import BM_GUI_DISP
from BiblioMeter_FUNCTS.BiblioMeterEmployeesGlobals import EMPLOYEES_USEFUL_COLS
from BiblioMeter_FUNCTS.BiblioMeterEmployeesGlobals import EMPLOYEES_ADD_COLS
from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS

# Getting display resolution in pixels per inch 
PPI = DISPLAYS[BM_GUI_DISP]['ppi']

# Generals
ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.1-Dossiers en cours\03- Publications\BiblioMeter\BiblioMeter_Files"
#ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.2-Infos communes\BiblioMeter\BiblioMeter_Files"


BDD_LIST = ['wos','scopus']


PAGES_LABELS = {'first' : "Analyse élémentaire des corpus",
                'second': "Consolidation annuelle des corpus",
                'third' : "Mise à jour des IF",
               }

PAGES_NAMES = {'first' : 'Page_ParsingConcat',
               'second': 'Page_ParsingInstitution',
               'third' : 'Page_MultiAnnuelle',
              }


DPT_LABEL_DICT = {'DEHT': ['DEHT'],
                  'DTCH': ['DTCH', 'DTBH'],
                  'DTNM': ['DTNM'],
                  'DTS' : ['DTS']
                 }


ARCHI_YEAR = {"bdd mensuelle"                  : "0 - BDD multi mensuelle", 
              "submit file name"               : "submit.xlsx", 
              "orphan file name"               : "orphan.xlsx",            
              "homonymes folder"               : "1 - Consolidation Homonymes", 
              "homonymes file name base"       : "Fichier Consolidation",            
              "OTP folder"                     : "2 - OTP", 
              "OTP file name base"             : "fichier_ajout_OTP",            
              "pub list folder"                : "3 - Résultats Finaux", 
              "pub list file name base"        : "Liste consolidée",              
              "corpus"                         : "Corpus", 
              "concat"                         : "concatenation", 
              "dedup"                          : "deduplication", 
              "scopus"                         : "scopus", 
              "wos"                            : "wos", 
              "parsing"                        : "parsing", 
              "rawdata"                        : "rawdata",
             }


ARCHI_BDD_MULTI_ANNUELLE = {"root"                 : "BDD multi annuelle",
                            "concat file name base": "Concaténation par",}


ARCHI_IF = {"root"    : "Impact Factor",
            "all IF"  : "IF all years.xlsx",
            "missing" : "ISSN_manquants.xlsx"}

# Start : To be moved to BiblioMeterEmployeesGlobal
ARCHI_RH = {"root"                : "Listing RH",
            "effectifs"           : "Effectifs consolidés",
            "effectifs file name" : "All_effectifs.xlsx",
            "maj"                 : "A rajouter"}


ARCHI_SECOURS = {"root" : "Sauvegarde de secours"}
# End : To be moved to BiblioMeterEmployeesGlobal


COL_NAMES_BM = {'Dpts'      : EMPLOYEES_ADD_COLS['dpts_list'], 
                'Servs'     : EMPLOYEES_ADD_COLS['servs_list'],
                'First_name': EMPLOYEES_ADD_COLS['first_name_initials'],
                'Last_name' : 'Co_author_joined',  # 'Co_author_joined' DOE J --> DOE
                'Full_name' : 'Full_name', # DOE J
                'Homonym'   : COL_NAMES_BONUS['homonym'],
               }

# Building of 'COL_NAMES_ORPHAN' for setting the columns order in orphan file
# from 'COL_NAMES' imported from BiblioAnalysis_Utils and from 'COL_NAMES_BM' and 'COL_NAMES_BAU'
COL_NAMES_ORPHAN = COL_NAMES['auth_inst'].copy()
COL_NAMES_ORPHAN.extend(COL_NAMES['authors'][2])
COL_NAMES_ORPHAN.extend(COL_NAMES['articles'][1:])
COL_NAMES_ORPHAN.extend([COL_NAMES_BM['Last_name']])

CORPUSES_NUMBER = 6

# Setting the results file names
SUBMIT_FILE_NAME = 'submit.xlsx'
ORPHAN_FILE_NAME = 'orphan.xlsx'


# Première sélection des colonnes de submit
SET_1 = ['Pub_id', 'Idx_author', 'Address', 'Country',
       'Institutions', 'LITEN_France', 'Co_author', 'Authors', 'Year',
       'Journal', 'Volume', 'Page', 'DOI', 'Document_type', 'Language',
       'Title', 'ISSN', 'Matricule', 'Nom', 'Prénom', 'Nom Prénom', 
       'Sexe(lib)', 'Nationalité (lib)', 'Catégorie de salarié (lib)',
       'Statut de salarié (lib)', 'Filière classement (lib)',
       'Qualification classement (lib)', 'Spécialité poste (lib)',
       'Nature de contrat (lib)', 'Annexe classement',
       "Date d'effet classement", 'Date début contrat', 'Date dernière entrée',
       'Date de fin de contrat', 'Dpt/DOB (lib court)', 'Service (lib court)',
       'Laboratoire (lib court)', 'Laboratoire (lib long)',
       'N° id du poste budgétaire', 'Unité structurelle',
       'Unité structurelle (code R3)', 'Nature de dépenses', 'TA',
       "Taux d'Activité", "Règle de plan de roulement (lib)",
       'Regpt PR niveau 1(lib)', 'Date de naissance', 'Age',
       "Tranche d'age (5 ans)", 'Mois', 'Année', 'list of Dpt/DOB (lib court)',
       'list of Service (lib court)']


# Selection des colonnes à garder lorsque qu'on veut faire un fichier à OTP dans submit
SET_OTP = ['Pub_id', 'Idx_author', 'DOI', 'Title', 'Year', 'ISSN', 'Document_type', 'Journal', 'Dpt/DOB (lib court)']


# Global du nom des colonnes à garder
SUBMIT_COL_NAMES = {'pub_id'                  : COL_NAMES['pub_id'], 
                    'idx_authors'             : COL_NAMES['authors'][1],
                    'co_authors'              : COL_NAMES['authors'][2], 
                    'address'                 : COL_NAMES['address'][2], 
                    'country'                 : COL_NAMES['auth_inst'][3],  
                    'year'                    : COL_NAMES['articles'][2], 
                    'journal'                 : COL_NAMES['articles'][3], 
                    'volume'                  : COL_NAMES['articles'][4], 
                    'page'                    : COL_NAMES['articles'][5], 
                    'DOI'                     : COL_NAMES['articles'][6], 
                    'document_type'           : COL_NAMES['articles'][7], 
                    'language'                : COL_NAMES['articles'][8], 
                    'title'                   : COL_NAMES['articles'][9], 
                    'ISSN'                    : COL_NAMES['articles'][10],
                    'ID'                      : EMPLOYEES_USEFUL_COLS['matricule'], 
                    'nom'                     : EMPLOYEES_USEFUL_COLS['name'],
                    'prénom'                  : EMPLOYEES_USEFUL_COLS['first_name'], 
                    'sexe'                    : EMPLOYEES_USEFUL_COLS['gender'], 
                    'nation'                  : EMPLOYEES_USEFUL_COLS['nationality'], 
                    'catégorie'               : EMPLOYEES_USEFUL_COLS['category'],
                    'statut'                  : EMPLOYEES_USEFUL_COLS['status'],
                    'qualification classement': EMPLOYEES_USEFUL_COLS['qualification'],
                    'dpt'                     : EMPLOYEES_USEFUL_COLS['dpt'],
                    'service'                 : EMPLOYEES_USEFUL_COLS['serv'],
                    'labo'                    : EMPLOYEES_USEFUL_COLS['lab'],
                    'affiliation complete'    : EMPLOYEES_USEFUL_COLS['full_affiliation'],
                    'date naissance'          : EMPLOYEES_USEFUL_COLS['birth_date'], 
                    'nom prénom'              : COL_NAMES_BONUS['nom prénom'], 
                    'nom prénom liste'        : COL_NAMES_BONUS['nom prénom liste'], 
                    'liste biblio'            : COL_NAMES_BONUS['liste biblio'],
                   }

