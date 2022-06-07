__all__ = ['ROOT_PATH', 
           'STOCKAGE_ARBORESCENCE', 
           'COL_NAMES_BM', 
           'COL_NAMES_RH', 
           'COL_NAMES_ORPHAN', 
           'SUBMIT_FILE_NAME', 
           'ORPHAN_FILE_NAME', 
           'SET_1', 
           'SET_OTP']

# Local imports
from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

# Generals

ROOT_PATH = "S:/130-LITEN/130.1-Direction/130.1.2-Direction Scientifique/130.1.2.1-Dossiers en cours/111- Ludovic Desmeuzes/BiblioMeter_Files"

# To be removed
STOCKAGE_ARBORESCENCE = {'wos' : ['Corpus/wos', 
                                  'savedrecs.txt'], 
                         'scopus' : ['Corpus/scopus', 
                                     'scopus.csv', 
                                     'BiblioAnalysis_RefFiles'], 
                         'effectif' : ['Listing RH', 
                                       'All_effectifs.xlsx', 
                                       'Effectifs_2010_2022.xlsx'],
                         'general' : ['BDD multi mensuelle', 
                                      'BDD multi annuelle',
                                      'Filtres', 
                                      'OTP', 
                                      'Consolidation Homonymes', 
                                      'Résultats', 
                                      'Results']
                        }

COL_NAMES_BM = {'Dpts':'list of Dpt/DOB (lib court)', 
                'Servs':'list of Service (lib court)',
                'First_name':'Initials_prenom',
                'Last_name': 'Co_author_joined',  # 'Co_author_joined' DOE J --> DOE
                'Full_name': 'Full_name', # DOE J
                'Homonym': 'HOMONYM',
               }

# Setting useful column names from the employees file (To Do: to be set as globals)
COL_NAMES_RH = {'Dpt': 'Dpt/DOB (lib court)',
                'Service': 'Service (lib court)',
                'Matricule':'Matricule',
                'Nom':'Nom',
                'Prénom':'Prénom',
                'Full_name': 'Full_name_eff',
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
SET_OTP = ['Pub_id', 'Idx_author', 'DOI', 'Title', 'ISSN', 'Document_type', 'Journal', 'Dpt/DOB (lib court)']