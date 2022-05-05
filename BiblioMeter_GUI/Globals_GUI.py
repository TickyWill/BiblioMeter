__all__ = ['ROOT_PATH', 
           'STOCKAGE_ARBORESCENCE', 
           'COL_NAMES_BM', 
           'COL_NAMES_RH', 
           'COL_NAMES_ORPHAN', 
           'SUBMIT_FILE_NAME', 
           'ORPHAN_FILE_NAME']

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
                                      'BDD multi annuelle']
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