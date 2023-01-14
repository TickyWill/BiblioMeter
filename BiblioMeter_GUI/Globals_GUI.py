__all__ = ['ROOT_PATH',
           'ARCHI_YEAR',
           'BDD_LIST',
           'DPT_LABEL_DICT',
           'STOCKAGE_ARBORESCENCE', 
           'COL_NAMES_BM', 
           'COL_NAMES_RH', 
           'COL_NAMES_ORPHAN',
           'PAGES_LABELS',
           'PAGES_NAMES',
           'SUBMIT_FILE_NAME', 
           'ORPHAN_FILE_NAME', 
           'SET_1', 
           'SET_OTP', 
           'PPI', 
           'GUI_DISP', 
           'DISPLAYS']

# BiblioAnalysis_Utils imports
from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

# Local imports
from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS

# Generals
#ROOT_PATH = "S:/130-LITEN/130.1-Direction/130.1.2-Direction Scientifique/130.1.2.1-Dossiers en cours/110-Alternants/2021-22 Ludovic Desmeuzes/BiblioMeter_Files"
ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.1-Dossiers en cours\03- Publications\BiblioMeter\BiblioMeter_Files"
#ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.2-Infos communes\BiblioMeter\BiblioMeter_Files"


BDD_LIST = ['wos','scopus']


PAGES_LABELS = {'first':  "Analyse élémentaire des corpus",
                'second': "Consolidation annuelle des corpus",
                'third':  "Mise à jour des IF",
               }

PAGES_NAMES = {'first':  'Page_ParsingConcat',
               'second': 'Page_ParsingInstitution',
               'third':  'Page_MultiAnnuelle',
              }


DPT_LABEL_DICT = {'DEHT': ['DEHT'],
                  'DTCH': ['DTCH', 'DTBH'],
                  'DTNM': ['DTNM'],
                  'DTS' : ['DTS']
                 }


# Variables organisées en fonction de l'architecture de la base de donnée
#ARCHI_YEAR = {"bdd mensuelle"           : "0 - BDD multi mensuelle", 
#              "submit file name"        : "submit.xlsx", 
#              "orphan file name"        : "orphan.xlsx", 
#              
#              "consolidation"           : "1 - Consolidation Homonymes", 
#              "consolidation file name" : "Fichier Consolidation", 
#              
#              "OTP"                     : "2 - OTP", 
#              "OTP file name"           : "fichier_ajout_OTP", 
#              
#              "resultats"               : "3 - Résultats Finaux", 
#              "resultats file name"     : "Liste consolidée", 
#              
#              "corpus"                  : "Corpus", 
#              "concat"                  : "concatenation", 
#              "dedup"                   : "deduplication", 
#              "scopus"                  : "scopus", 
#              "wos"                     : "wos", 
#              "parsing"                 : "parsing", 
#              "rawdata"                 : "rawdata",
#             }

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


ARCHI_RH = {"root"                : "Listing RH",
            "effectifs"           : "Effectifs consolidés",
            "effectifs file name" : "All_effectifs.xlsx",
            "maj"                 : "A rajouter"}


ARCHI_SECOURS = {"root" : "Sauvegarde de secours"}


STOCKAGE_ARBORESCENCE = {'wos' : ['Corpus/wos', 
                                  'savedrecs.txt'], 
                         'scopus' : ['Corpus/scopus', 
                                     'scopus.csv', 
                                     'BiblioAnalysis_RefFiles'], 
                         'effectif' : ['Listing RH', 
                                       'All_effectifs.xlsx', 
                                       'Effectifs_2010_2022.xlsx', 'MAJ.txt'],
                         'general' : ['0 - BDD multi mensuelle', 
                                      'BDD multi annuelle',
                                      'Filtres', 
                                      '2 - OTP', 
                                      '1 - Consolidation Homonymes', 
                                      '3 - Résultats Finaux', 
                                      'Results', 
                                      'Impact Factor', 
                                      'Sauvegarde de secours'], 
                         'all IF' : 'IF all years.xlsx'
                        }

COL_NAMES_BM = {'Dpts'      :'list of Dpt/DOB (lib court)', 
                'Servs'     :'list of Service (lib court)',
                'First_name':'Initials_prenom',
                'Last_name' : 'Co_author_joined',  # 'Co_author_joined' DOE J --> DOE
                'Full_name' : 'Full_name', # DOE J
                'Homonym'   : 'HOMONYM',
               }


# Building of 'COL_NAMES_ORPHAN' for setting the columns order in orphan file
# from 'COL_NAMES' imported from BiblioAnalysis_Utils and from 'COL_NAMES_BM' and 'COL_NAMES_BAU'
COL_NAMES_ORPHAN = COL_NAMES['auth_inst'].copy()
COL_NAMES_ORPHAN.extend(COL_NAMES['authors'][2])
COL_NAMES_ORPHAN.extend(COL_NAMES['articles'][1:])
COL_NAMES_ORPHAN.extend([COL_NAMES_BM['Last_name']])

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

# Selection des colonnes à garder lorsque qu'on veut faire un fichier à OTP
SET_OTP = ['Pub_id', 'Idx_author', 'DOI', 'Title', 'Year', 'ISSN', 'Document_type', 'Journal', 'Dpt/DOB (lib court)']

# Global du nom des colonnes à garder
SUBMIT_COL_NAMES = { 
    'pub_id': COL_NAMES['pub_id'], 
    # 'authors' : COL_NAMES['articles'][1],
    'idx_authors' : COL_NAMES['authors'][1],
    'co_authors' : COL_NAMES['authors'][2], 
    'address' : COL_NAMES['address'][2], 
    'country' : COL_NAMES['auth_inst'][3],  
    'year' : COL_NAMES['articles'][2], 
    'journal' : COL_NAMES['articles'][3], 
    'volume' : COL_NAMES['articles'][4], 
    'page' : COL_NAMES['articles'][5], 
    'DOI' : COL_NAMES['articles'][6], 
    'document_type' : COL_NAMES['articles'][7], 
    'language' : COL_NAMES['articles'][8], 
    'title' : COL_NAMES['articles'][9], 
    'ISSN' : COL_NAMES['articles'][10],
    'nom prénom' : COL_NAMES_BONUS['nom prénom'], 
    'nom prénom liste' : COL_NAMES_BONUS['nom prénom liste'], 
    'ID' : COL_NAMES_RH['ID'], 
    'nom' : COL_NAMES_RH['nom'],
    'prénom' : COL_NAMES_RH['prénom'], 
    'sexe' : COL_NAMES_RH['sexe'], 
    'nation' : COL_NAMES_RH['nation'], 
    'catégorie' : COL_NAMES_RH['catégorie'],
    'statut' : COL_NAMES_RH['statut'],
    'qualification classement' : COL_NAMES_RH['qualification classement'],
    'dpt' : COL_NAMES_RH['dpt'],
    'service' : COL_NAMES_RH['service'],
    'labo' : COL_NAMES_RH['labo'],
    'affiliation complete' : COL_NAMES_RH['affiliation complete'],
    'date naissance' : COL_NAMES_RH['date naissance'], 
    'nom prénom' : COL_NAMES_BONUS['nom prénom'], 
    'nom prénom liste' : COL_NAMES_BONUS['nom prénom liste'], 
    'liste biblio' : COL_NAMES_BONUS['liste biblio']
}

from BiblioMeter_GUI.Useful_Functions import get_displays

# Get screens
DISPLAYS = get_displays()

displays_nb = len(DISPLAYS)
GUI_DISP = [i for i in range(displays_nb) if DISPLAYS[i]['is_primary']][0]
PPI = DISPLAYS[GUI_DISP]["ppi"]
