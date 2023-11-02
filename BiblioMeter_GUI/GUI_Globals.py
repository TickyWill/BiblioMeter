__all__ = ['ROOT_PATH',
           'BDD_LIST',
           'CORPUSES_NUMBER',
           'PAGES_LABELS',
           'PAGES_NAMES',
           'PPI',
           ]


# BiblioAnalysis_Utils package globals imports
from BiblioAnalysis_Utils.BiblioSys import DISPLAYS

# Local globals imports
from BiblioMeter_GUI.Coordinates import BM_GUI_DISP


# Getting display resolution in pixels per inch 
PPI = DISPLAYS[BM_GUI_DISP]['ppi']

# Generals
#ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.1-Dossiers en cours\03- Publications\BiblioMeter\BiblioMeter_Files"
ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.2-Infos communes\BiblioMeter\BiblioMeter_Files"


CORPUSES_NUMBER = 6


BDD_LIST = ['wos','scopus']


PAGES_LABELS = {'first' : "Analyse élémentaire des corpus",
                'second': "Consolidation annuelle des corpus",
                'third' : "Mise à jour des facteurs d'impact",
                'fourth': "KPIs et graphs"
               }


PAGES_NAMES = {'first' : 'Page_ParseCorpus',
               'second': 'Page_ConsolidateCorpus',
               'third' : 'Page_UpdateIFs',
               'fourth': 'Page_Analysis'
              }

