"""The `gui_globals` module  defines the global parameters useful for the GUI settings.
"""

__all__ = ['ADD_SPACE_MM',
           'ANALYSIS_TEXT_DICT',
           'APPLICATION_WINDOW_TITLE',
           'BM_GUI_DISP',
           'CORPUSES_NUMBER',
           'ETAPE_LABEL_TEXT_LIST',
           'FONT_NAME',
           'HELP_ETAPE_5',
           'HELP_ETAPE_6',
           'IN_TO_MM',
           'PAGEBUTTON_HEIGHT_PX',
           'PAGES_LABELS',
           'PPI',
           'REF_WF_POS_X_MM',
           'REF_WF_POS_Y_MM',
           'REF_BUTTON_DX_MM',
           'REF_BUTTON_DY_MM',
           'REF_BUTTON_FONT_SIZE',
           'REF_CHECK_BOXES_SEP_SPACE',
           'REF_COPYRIGHT_FONT_SIZE',
           'REF_COPYRIGHT_X_MM',
           'REF_COPYRIGHT_Y_MM',
           'REF_CORPI_POS_X_MM',
           'REF_CORPI_POS_Y_MM',
           'REF_DATATYPE_POS_X_MM',
           'REF_DATATYPE_POS_Y_MM',
           'REF_ENTRY_NB_CHAR',
           'REF_ETAPE_BUT_DX_MM',
           'REF_ETAPE_BUT_DY_MM',
           'REF_ETAPE_FONT_SIZE',
           'REF_ETAPE_POS_X_MM',
           'REF_ETAPE_POS_Y_MM_LIST',
           'REF_EXIT_BUT_POS_X_MM',
           'REF_EXIT_BUT_POS_Y_MM',
           'REF_INST_POS_X_MM',
           'REF_INST_POS_Y_MM',
           'REF_LABEL_DX_Y_MM',
           'REF_LABEL_FONT_SIZE',
           'REF_LABEL_POS_Y_MM',
           'REF_LAUNCH_FONT_SIZE',
           'REF_MENU_NB_CHAR',
           'REF_PAGE_TITLE_FONT_SIZE',
           'REF_PAGE_TITLE_POS_Y_MM',
           'REF_SCREEN_WIDTH_PX',
           'REF_SCREEN_HEIGHT_PX',
           'REF_SCREEN_WIDTH_MM',
           'REF_SCREEN_HEIGHT_MM',
           'REF_SUB_TITLE_FONT_SIZE',
           'REF_WINDOW_WIDTH_MM',
           'REF_WINDOW_HEIGHT_MM',
           'REF_VERSION_FONT_SIZE',
           'REF_VERSION_X_MM',
           'REF_YEAR_BUT_POS_X_MM',
           'REF_YEAR_BUT_POS_Y_MM',
           'TEXT_CROISEMENT',
           'TEXT_ETAPE_1',
           'TEXT_ETAPE_2',
           'TEXT_ETAPE_3',
           'TEXT_ETAPE_4',
           'TEXT_ETAPE_5',
           'TEXT_ETAPE_6',
           'TEXT_HOMONYMES',
           'TEXT_MAJ_BDD_IF',
           'TEXT_MAJ_PUB_IF',
           'TEXT_OTP',
           'TEXT_PUB_CONSO',
           'TEXT_YEAR_PI', # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
           'BOX_POS_MM_LIST',
           'BOX_TABLE_COLS',
           'GUI_BUTTONS',
           'VERSION',
           'APP_COPYRIGHT',
           'APP_VERSION',
           'CORPUSES_TXT',
           'CREATE_CORPUS_BUTTON_TXT',
           'DATATYPE_TXT',
           'EMPL_UPDATE_TXT',
           'EXIT_BUTTON_TXT',
           'INSTITUTE_TXT',
           'LABELS_POS_Y_MM_REF',
           'LAUNCH_BUTTON_TXT',
           'LAUNCH_DPOS_MM_LIST',
           'MAIN_PAGE_TITLE',
           'OPTION_SELECT',
           'PARSING_LABELS',
           'PARSING_LAUNCH',
           'PROGRESS_BAR_DX_PX',
           'PROGRESS_BAR_DY_PX',
           'PROGRESS_BAR_LEN_MM',
           'STEP_HELPS_LIST',
           'STEP_LABELS_LIST',
           'STEP_LAUNCHS_LIST',
           'STEP_BUT_DX_MM_REF',
           'STEP_BUT_DY_MM_REF',
           'STEP_FONT_SIZE_REF',
           'STEP_POS_X_MM_REF',
           'STEP_POS_Y_MM_REF_LIST', 
           'STEPS_NB',
           'WF_TXT',
           'WF_CHANGE_TXT',
           'YEAR_SELECT_TXT',
           'YEAR_BUT_POS_X_MM_REF',
           'YEAR_BUT_POS_Y_MM_REF',
           ]

# Standard library imports
import math

# 3rd party imports
from screeninfo import get_monitors

# *****************************************
# ************ GENERAL GLOBALS ************
# *****************************************

# Setting BiblioMeter version value (internal)
VERSION = '6.2.0'

# Setting the number of corpuses to analyse
CORPUSES_NUMBER = 6

# Setting the title of the application main window (internal)
APPLICATION_WINDOW_TITLE = "Analyse de la production scientifique d'un institut"

# *****************************************
# ************ DISPLAY GLOBALS ************
# *****************************************

def _get_displays(in_to_mm):
    """ The function `get_displays` allows to identify the set of displays
        available within the user hardware and to get their parameters.
        If the width or the height of a display are not available in mm
        through the `get_monitors` method (as for Darwin platforms),
        the user is asked to specify the displays diagonal size to compute them.

    Returns:
        `list`: list of dicts with one dict per detected display,
                each dict is keyed by 8 display parameters.
    """
    displays = [{'x': m.x, 'y': m.y, 'width': m.width,
                 'height': m.height, 'width_mm': m.width_mm,
                 'height_mm': m.height_mm, 'name': m.name,
                 'is_primary': m.is_primary} for m in get_monitors()]

    for disp, _ in enumerate(displays):
        width_px = displays[disp]['width']
        height_px = displays[disp]['height']
        diag_px = math.sqrt(int(width_px)**2 + int(height_px)**2)
        width_mm = displays[disp]['width_mm']
        height_mm = displays[disp]['height_mm']
        if width_mm is None or height_mm is None:
            quest = 'Enter the diagonal size of the screen n°' + str(disp) + ' (inches)'
            diag_in = float(input(quest))
            width_mm = round(int(width_px) * (diag_in/diag_px) * in_to_mm, 1)
            height_mm = round(int(height_px) * (diag_in/diag_px) * in_to_mm, 1)
            assert isinstance(width_mm, int)
            displays[disp]['width_mm'] = str(width_mm)
            assert isinstance(height_mm, int)
            displays[disp]['height_mm'] = str(height_mm)
        else:
            diag_in = math.sqrt(float(width_mm) ** 2 + float(height_mm) ** 2) / in_to_mm
        displays[disp]['ppi'] = round(diag_px/diag_in, 2)

    return displays


# Conversion factor for inch to millimeter
IN_TO_MM = 25.4

DISPLAYS = _get_displays(IN_TO_MM)

# Setting primary display
BM_GUI_DISP = 0

# Getting display resolution in pixels per inch
PPI = DISPLAYS[BM_GUI_DISP]['ppi']

# Setting display reference sizes in pixels and mm
REF_SCREEN_WIDTH_PX = 1920
REF_SCREEN_HEIGHT_PX = 1080
REF_SCREEN_WIDTH_MM = 467
REF_SCREEN_HEIGHT_MM = 267

# Application window reference sizes in mm for the display reference sizes
REF_WINDOW_WIDTH_MM = 219
REF_WINDOW_HEIGHT_MM = 173

# ************* PAGES GLOBALS *************

# Setting general globals for text edition
FONT_NAME = "Helvetica"

# **** REFERENCE COORDINATES FOR PAGES ****

# Number of characters reference for editing the entered files-folder path
REF_ENTRY_NB_CHAR = 110

# Number of characters reference for editing the selected item in menu
REF_MENU_NB_CHAR = 30

# Font size references for page label and button
REF_SUB_TITLE_FONT_SIZE = 15
REF_PAGE_TITLE_FONT_SIZE = 30
REF_LAUNCH_FONT_SIZE = 25
REF_COPYRIGHT_FONT_SIZE = 12
REF_VERSION_FONT_SIZE = 12

# Y position reference in mm for page label
REF_PAGE_TITLE_POS_Y_MM = 20

# Positions reference in mm for institute selection button
REF_INST_POS_X_MM = 5
REF_INST_POS_Y_MM = 40

# Positions reference in mm for data type selection button
REF_DATATYPE_POS_X_MM = 110
REF_DATATYPE_POS_Y_MM = 40

# Positions reference in mm for wf label and button
REF_WF_POS_X_MM = 5
REF_WF_POS_Y_MM = 55
REF_BUTTON_DX_MM = -147
REF_BUTTON_DY_MM = 10

# Positions reference in mm for corpus creation button
REF_CORPI_POS_X_MM = 5
REF_CORPI_POS_Y_MM = 85

# Space between label and value
ADD_SPACE_MM = 10

# Setting X and Y positions reference in mm for copyright
REF_COPYRIGHT_X_MM = 5
REF_COPYRIGHT_Y_MM = 170
REF_VERSION_X_MM = 185

# Font size references for page label and button
REF_LABEL_FONT_SIZE = 25
REF_ETAPE_FONT_SIZE = 14
REF_BUTTON_FONT_SIZE = 10

# Positions reference in mm for pages widgets
REF_LABEL_POS_Y_MM = 7
REF_LABEL_DX_Y_MM  = 10
REF_ETAPE_POS_X_MM = 10
REF_ETAPE_POS_Y_MM_LIST = [40, 74, 101, 129]
REF_ETAPE_BUT_DX_MM = 5
REF_ETAPE_BUT_DY_MM = 5
#REF_ETAPE_CHECK_DY_MM = -8
REF_EXIT_BUT_POS_X_MM = 198
REF_EXIT_BUT_POS_Y_MM = 150
REF_YEAR_BUT_POS_X_MM = 10
REF_YEAR_BUT_POS_Y_MM = 26

# Separation space in mm for check boxes
REF_CHECK_BOXES_SEP_SPACE = 25

# Container button height in pixels
PAGEBUTTON_HEIGHT_PX = 50

# Setting label for each gui page
PAGES_LABELS = {'ParseCorpusPage': "Analyse élémentaire des corpus",
                'ConsolidateCorpusPage': "Consolidation annuelle des corpus",
                'UpdateIfPage': "Mise à jour des facteurs d'impact",
                'AnalyzeCorpusPage': "Analyse et KPIs", }

# *************** MAIN PAGE ***************

# Titre de la page
MAIN_PAGE_TITLE = "- BiblioMeter -\nInitialisation de l'analyse"

# Choix de l'Institut
INSTITUTE_TXT = "Sélection de l'Institut"

# Titre du dossier de travail
WF_TXT = "Dossier de travail "

# Titre bouton changement de dossier de travail
WF_CHANGE_TXT = "Changer de dossier de travail"

# Titre liste des corpus analysés
CORPUSES_TXT = "Liste des corpus "

# Titre bouton création d'un nouveau dossier de corpus
CREATE_CORPUS_BUTTON_TXT = "Créer un nouveau dossier de corpus annuel"

# Choix du type de données brutes
DATATYPE_TXT = "Type de données"

# Titre bouton de lancement
LAUNCH_BUTTON_TXT = "Lancer l'analyse"

# Copyright and contacts
APP_COPYRIGHT = "Contributeurs et contacts :"
APP_COPYRIGHT += "\n- Amal Chabli : amal.chabli@orange.fr"
APP_COPYRIGHT += "\n- François Bertin : francois.bertin7@wanadoo.fr"
APP_COPYRIGHT += "\n- Baptiste Refalo : baptiste.refalo@cea.fr"
APP_COPYRIGHT += "\n- Ludovic Desmeuzes"
APP_VERSION = f"\nVersion {VERSION}"

# ************ SECONDARY PAGES ************

# Common to secondary pages
EXIT_BUTTON_TXT = "Quitter"

# Setting label of help button
HELP_BUTTON = "Description"

# Setting reference positions in mm for help buttons
REF_HELP_BUT_POS_X_MM = 180
REF_HELP_BUT_POS_Y_MM = 0

# - Setting year selection parameters
YEAR_SELECT_TXT = "Sélection de l'année "

# Setting reference positions in mm for year selection button
YEAR_BUT_POS_X_MM_REF = 80 # 10
YEAR_BUT_POS_Y_MM_REF = 45 # 40

# Setting reference progress-bar lengths in mm
PROGRESS_BAR_LEN_MM = {'parse' : 50,
                       'conso' : 100,
                       'if_upd': 75,
                       'analys': 100}

# Setting relative positions shift in px
PROGRESS_BAR_DX_PX = {'parse' : -80,
                      'synth' : 40,
                      'conso' : 40,
                      'if_upd': 40,
                      'analys': 40}

PROGRESS_BAR_DY_PX = {'parse' : 15,
                      'synth' : 0,
                      'conso' : 0,
                      'if_upd': 0,
                      'analys': 0}

# *************************** Parsing page globals
BOX_POS_MM_LIST = [70, 40, 10]

BOX_TABLE_COLS = {'raw_wos'     : 'Wos\nDonnées brutes',
                  'wos_parse'   : 'Wos\nParsing',
                  'raw_scopus'  : 'Scopus\nDonnées brutes',
                  'scopus_parse': 'Scopus\nParsing',
                  'dedup'       : 'Synthèse\nParsing',
                 }

LAUNCH_DPOS_MM_LIST = [15, 0.2]

STEP_KEYS_LIST = ['status', 'parsing', 'dedup']

LABELS_POS_Y_MM_REF_LIST = [25, 107, 135]
LABELS_POS_Y_MM_REF = dict(zip(STEP_KEYS_LIST, LABELS_POS_Y_MM_REF_LIST))

LABELS_LIST = ["Statut des fichiers de Parsing",
               "Construction des fichiers de Parsing par BDD",
               "Synthèse des fichiers de Parsing de toutes les BDD"]
PARSING_LABELS = dict(zip(STEP_KEYS_LIST, LABELS_LIST))

LAUNCH_LIST = ["Mettre à jour le statut des fichiers",
               "Lancer le Parsing",
               "Lancer la synthèse"]
PARSING_LAUNCH = dict(zip(STEP_KEYS_LIST, LAUNCH_LIST))

OPTION_SELECT = {'year': "Sélection de l'année ",
                 'data': "Sélection de la BDD ",
                }

# - Label STATUT
STATUT_TXT = "Statut des fichiers de Parsing"

# - Label Parsing
TEXT_PARSING = "Construction des fichiers de Parsing par BDD"

# - Label SYNTHESE
TEXT_SYNTHESE = "Synthèse des fichiers de Parsing de toutes les BDD"

# - Label ANNEE
TEXT_YEAR_PC = "Sélection de l'année "

# -Label choix de BDD
TEXT_BDD_PC = "Sélection de la BDD "

# - Bouton mise à jour du statut des fichiers
UPDATE_STATUS_TXT = "Mettre à jour le statut des fichiers"

# - Bouton lancement parsing
TEXT_LAUNCH_PARSING = "Lancer le Parsing"

# - Bouton lancement concatenation et deduplication des parsings
TEXT_LAUNCH_SYNTHESE = "Lancer la synthèse"



# Consolidation page

STEP_FONT_SIZE_REF = 14

STEP_POS_X_MM_REF = 10
STEP_BUT_DX_MM_REF = 5
STEP_BUT_DY_MM_REF = 4

# Setting parameters for each step
STEPS_NB = 5
STEPS_DY = 24
STEPS_Y_INIT = 60
STEP_POS_Y_MM_REF_LIST = sum([[22], [STEPS_Y_INIT + n * STEPS_DY for n in range(STEPS_NB-1)]], [])
STEP_LABEL, STEP_HELP, STEP_LAUNCH = [], [], []

# Step 0
STEP_LABEL.append("Effectifs - Mise à jour des données")
STEP_HELP.append("Le fichier original des effectifs va être complété "
                 "avec les données du fichier de mise à jour disponible."
                 "\n\nCette mise à jour n'a besoin d'être effectuée "
                 "que si un nouveau fichier de mise à jour est disponible.")
STEP_LAUNCH.append("Lancer la mise à jour")

# Step 1
STEP_LABEL.append("Étape 1 - Croisement auteurs-efffectifs de l'institut")
STEP_HELP.append("Deux fichiers avec une ligne par auteur de l'institut "
                 "et par publication vont être créés à cette étape :"
                 "\n\n - Un fichier avec les auteurs trouvés dans les effectifs "
                 "qui permettra de construire la liste consolidée ;"
                 "\n - Un fichier avec les auteurs non trouvés dans les effectifs "
                 "dont l'examen permet d'alimenter les fichiers de correction.")
STEP_LAUNCH.append("Effectuer le croisement auteurs-efffectifs")

# Step 2
STEP_LABEL.append("Étape 2 - Résolution des homonymies")
STEP_HELP.append("Un fichier avec une ligne par auteur de l'institut "
                 "et par publication va être créé à cette étape indiquant "
                 "les homonymes à traiter."
                 "\nL'historique des résolutions va être pris en compte.")
STEP_LAUNCH.append("Créer le fichier pour la résolution des homonymies")

# Step 3
STEP_LABEL.append("Étape 3 - Attribution des OTPs")
STEP_HELP.append("Un fichier par département avec une ligne par publication "
                 "va être créé à cette étape avec une colonne pour l'attribution des OTPs."
                 "\nL'historique des attributions va être pris en compte.")
STEP_LAUNCH.append("Créer les fichiers pour l'attribution des OTPs")

# Step 4
STEP_LABEL.append("Étape 4 - Consolidation de la liste des publications")
STEP_HELP.append("Un fichier avec avec une ligne par publication avec "
                 "l'OTP éventuellement attribué et le facteur d'impact trouvé "
                 "pour le journal dans la base de données des IFs va être créé à cette étape."
                 "\nDeux fichiers vont être également créés indiquant les informations manquantes "
                 "dans la base de données des facteurs d'impact.")
STEP_LAUNCH.append("Créer la liste consolidée des publications")

# Building lists of steps parameters 
STEP_LABELS_LIST = [STEP_LABEL[step] for step in range(STEPS_NB)]
STEP_HELPS_LIST = [STEP_HELP[step] for step in range(STEPS_NB)]
STEP_LAUNCHS_LIST = [STEP_LAUNCH[step] for step in range(STEPS_NB)]


# - Choix de l'année de travail
TEXT_YEAR_PI = "Sélection de l'année "

# - Etape 1
TEXT_ETAPE_1 = "Etape 1 : Croisement auteurs-efffectifs de l'institut"
EMPL_UPDATE_TXT = "Mettre à jour les effectifs de l'institut avant le croisement (coché = OUI) ?"
TEXT_CROISEMENT = "Effectuer le croisement auteurs-efffectifs"

# - Etape 2
TEXT_ETAPE_2 = "Etape 2 : Résolution des homonymies"
TEXT_HOMONYMES = "Créer le fichier pour la résolution des homonymies"

# - Etape 3
TEXT_ETAPE_3 = "Etape 3 : Attribution des OTPs"
TEXT_OTP = "Créer les fichiers pour l'attribution des OTPs"

# - Etape 4
TEXT_ETAPE_4 = "Etape 4 : Consolidation de la liste des publications"
TEXT_MAJ_DB_IF = " Mettre à jour la base de données IF avant la consolidation (coché = OUI) ?"
TEXT_PUB_CONSO = "Créer la liste consolidée des publications"

ETAPE_LABEL_TEXT_LIST = [TEXT_ETAPE_1, TEXT_ETAPE_2, TEXT_ETAPE_3, TEXT_ETAPE_4]

# Impact-factors update page

# - Etape 5
TEXT_ETAPE_5 = "Mise à jour de la base de données des IFs"
HELP_ETAPE_5 = " La base de données sera mise à jour à partir des fichiers : "
HELP_ETAPE_5 += "\n  'IF manquants.xlsx' et 'ISSN manquants.xlsx' annuels"
HELP_ETAPE_5 += "\ncomplétés manuellement."
TEXT_MAJ_BDD_IF = "Lancer la mise à jour de la base de données des IFs"

# - Etape 6
TEXT_ETAPE_6 = "Mise à jour des IFs dans les listes consolidées"
HELP_ETAPE_6 = " Dans cette partie, vous pouvez mettre à jour les IFs"
HELP_ETAPE_6 += " dans les listes consolidées de publications existantes."
TEXT_MAJ_PUB_IF = "Lancer la mise à jour des IFs dans les listes consolidées existantes"

# Analysis page

# - Etape IF
if_analysis_title = "Analyse des IFs et mise à jour des KPIs"
if_analysis_help = " L'analyse des IFS est effectuée à partir des fichiers"
if_analysis_help += " des listes consolidées des publications."
if_analysis_launch = "Lancer l'analyse des IFs"

# - Etape AU
au_analysis_title = "Analyse des auteurs"
au_analysis_help = " L'analyse des auteurs est effectuée à partir des fichiers"
au_analysis_help += " issus de l'étape de croisement avec les effectifs."
au_analysis_launch = "Lancer l'analyse des auteurs"

# - Etape CO
co_analysis_title = "Analyse des collaborations"
co_analysis_help = " L'analyse des collaborations est effectuée à partir des fichiers"
co_analysis_help += " issus de l'étape de parsing des corpus."
co_analysis_launch = "Lancer l'analyse des collaborations"

# - Etape KW
kw_analysis_title = "Analyse des mots clefs"
kw_analysis_help = " L'analyse des mots clefs est effectuée à partir des fichiers"
kw_analysis_help += " issus de l'étape de parsing des corpus."
kw_analysis_launch = "Lancer l'analyse des mots clefs"

ANALYSIS_TEXT_DICT = {"if": [if_analysis_title, if_analysis_help, if_analysis_launch],
                      "au": [au_analysis_title, au_analysis_help, au_analysis_launch],
                      "co": [co_analysis_title, co_analysis_help, co_analysis_launch],
                      "kw": [kw_analysis_title, kw_analysis_help, kw_analysis_launch],
                     }

# List of all the buttons
GUI_BUTTONS = []
