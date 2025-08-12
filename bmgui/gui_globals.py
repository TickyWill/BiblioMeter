"""The `gui_globals` module  defines the global parameters useful for the GUI settings.
"""

__all__ = ['APP_WIN_TITLE',
           'APP_COPYRIGHT',
           'BM_GUI_DISP',
           'CORPUSES_NUMBER',
           'FONT_NAME',
           'BOX_POS_TUP',
           'BOX_SEP_SPACE',
           'BOX_TABLE_COLS_DICT',
           'BOX_TABLE_POS_DICT',
           'BOX_Y_DPOS',
           'EXIT_BUT_POS_TUP',
           'EXIT_LABEL',
           'GUI_BUTTONS',
           'HELP_BUT_DPOS_TUP',
           'HELP_LABEL',
           'IN_TO_MM',
           'KEY_ANALYS',
           'KEY_ANALYS_YEAR',
           'KEY_CONSO',
           'KEY_CONSO_YEAR',
           'KEY_IF',
           'KEY_PARSE',
           'KEY_PARSE_YEAR', 
           'MAIN_BUT_LABEL_DICT',
           'MAIN_BUT_DPOS_TUP',
           'MAIN_BUT_POS_TUP',
           'MAIN_CHAR_NB_DICT',
           'MAIN_DISP_LABEL_POS_DICT',
           'MAIN_FONT_SIZE_DICT',
           'MAIN_INFO_POS_DICT',
           'MAIN_OPT_BUT_DPOS_TUP',
           'MAIN_PAGE_TITLE',
           'MAIN_SELECT_LABEL_DICT',
           'MAIN_SELECT_LABEL_POS_DICT',
           'PAGE_BUTTON_HEIGHT',
           'PAGE_FONT_SIZE_DICT',
           'PAGE_SELECT_LABEL_DICT',
           'PAGES_LABELS',
           'PAGE_SELECT_BUT_DPOS_DICT',
           'PAGE_SELECT_LABEL_DPOS_DICT',
           'PAGE_SELECT_LABEL_POS_DICT',
           'PAGE_TITLE_POS_DICT',
           'PPI',
           'PROGRESS_BAR_DPOS_DICT',
           'PROGRESS_BAR_LEN_DICT',
           'STATUS_BUT_POS_TUP',
           'STEP_BUT_DPOS_DICT',
           'STEPS_HELPS_DICT',
           'STEPS_LABELS_DICT',
           'STEPS_LAUNCHES_DICT',
           'STEPS_NB_DICT',
           'STEP_POS_TUPS_DICT',
           'TK_SIZES_REF',
           'VAL_DISPLAY_DX',
           'VERSION',
           ]

# Standard library imports
import math

# 3rd party imports
from screeninfo import get_monitors

# *****************************************
# ************ GENERAL GLOBALS ************
# *****************************************

# Setting application version value
VERSION = '6.2.0'

# Setting the number of corpuses to analyse
CORPUSES_NUMBER = 6

# Setting the title of the application main window
APP_WIN_TITLE = "Analyse de la production scientifique d'un institut"

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

# 
TK_SIZES_REF = {'display_px': (1920, 1080),
                'display_mm': (467, 267),
                'window_mm' : (219, 173),
               }

# *****************************************
# ********** PAGES JOINT GLOBALS **********
# *****************************************

# Initialization of the List of all the buttons
GUI_BUTTONS = []

# Setting label for each gui page
PAGES_LABELS = {'ParseCorpusPage': "Analyse élémentaire des corpus",
                'ConsolidateCorpusPage': "Consolidation annuelle des corpus",
                'UpdateIfPage': "Mise à jour des facteurs d'impact",
                'AnalyzeCorpusPage': "Analyse et KPIs", }

# Short_names for dict keys appearing multiple times
KEY_MAIN = 'main'
KEY_PARSE = 'parse'
KEY_PARSE_YEAR = 'parse_year'
KEY_DEDUP = 'dedup'
KEY_CONSO = 'conso'
KEY_CONSO_YEAR = 'conso_year'
KEY_IF = 'if_upd'
KEY_ANALYS = 'analys'
KEY_ANALYS_YEAR = 'analys_year'

# Font name for all characters
FONT_NAME = "Helvetica"

# *****************************************
# *********** MAIN PAGE GLOBALS ***********
# *****************************************

# Font size per widget type 
# (title, parameter selection, information display, button)
MAIN_FONT_SIZE_DICT = {'copyright'     : 12,
                       'main_title'    : 30,
                       'main_select'   : {'label' : 18,
                                          'button': 14,},
                       'main_disp'     : {'label' : 16,
                                          'button': 14,},
                       'main_launch'   : 25,
                       'page_button'   : 11,
                       'version'       : 12,
                      }

# Copyright and contacts
APP_COPYRIGHT = ("Contributeurs et contacts :"
                 "\n- Amal Chabli : amal.chabli@orange.fr"
                 "\n- François Bertin : francois.bertin7@wanadoo.fr"
                 "\n- Baptiste Refalo : baptiste.refalo@cea.fr"
                 "\n- Ludovic Desmeuzes")

# Title of main page
MAIN_PAGE_TITLE = "- BiblioMeter -\nInitialisation de l'analyse"

# Positions of application information
MAIN_INFO_POS_DICT = {'main_title': ("mid_page", 20),
                      'copyright' : (5, 170),
                      'version'   : (185, 170),
                     }

# Labels of items selection
MAIN_SELECT_LABEL_DICT = {'institute': "Institut ",
                          'datatype' : "Type de données ",}

# Positions of labels for items selection
MAIN_SELECT_LABEL_POS_DICT = {'institute': (10, 40),
                              'datatype' : (100, 40),}

# Relative positions of option-buttons for items selection
MAIN_OPT_BUT_DPOS_TUP = (0, -2)

# Labels of command buttons 
MAIN_BUT_LABEL_DICT = {'wf_change' : "Changer de dossier de travail",
                       'corpus_add': "Créer un nouveau dossier de corpus annuel",
                       'launch'    : "Lancer l'application",}

# Positions of command buttons
MAIN_BUT_POS_TUP = ("mid_page", 135) # Application launch button
MAIN_BUT_DPOS_TUP = (0, 4)

# Labels of display fields
MAIN_DISP_LABEL_DICT = {'wf'      : "Dossier de travail",
                        'corpuses': "Liste des corpus",}

# Number of characters for display fields
MAIN_CHAR_NB_DICT = {'work_folder': 110,
                     'datatype'   : 30,
                     'corpus_list': 110,
                    }

# Positions of display fields
MAIN_DISP_LABEL_POS_DICT = {'work_folder': (10, 60),
                            'corpus_list': (10, 90),}

# Space between label and display field
VAL_DISPLAY_DX = 10

# Container button height
PAGE_BUTTON_HEIGHT = 13

# ******************************************
# **** JOINT GLOBALS OF SECONDARY-PAGES ****
# ******************************************

# Font size per page-widget type 
# (title, parameter selection, information display, button)
PAGE_FONT_SIZE_DICT = {'box_header'    : 11,
                       'exit_button'   : 12,
                       'page_title'    : 25,
                       'page_sub_title': 17,
                       'step_help'     : 12,
                       'step_label'    : 16,
                       'step_launch'   : 14,
                       'step_select'   : {'label' : 14,
                                          'button': 11,},
                       'year_select'   : {'label' : 17,
                                          'button': 11,},
                      }

# Progress-bar lengths
PROGRESS_BAR_LEN_DICT = {KEY_PARSE : 80,
                         KEY_CONSO : 80,
                         KEY_IF    : 100,
                         KEY_ANALYS: 90,
                        }

# Relative positions of progress-bar
PROGRESS_BAR_DPOS_DICT = {KEY_PARSE : (10, 0.5),
                          KEY_CONSO : (10, 0.5),
                          KEY_IF    : (20, 10),
                          KEY_ANALYS: (10, 0.5),
                         }

PAGE_TITLE_POS_DICT = {'page_title'    : ("mid_page", 7), 
                       'page_sub_title': ("mid_page", 17),
                      }

# Label of exit buttons
EXIT_LABEL = "Quitter"

# Positions of exit buttons
EXIT_BUT_POS_TUP = (198, 150)

# Label of help buttons
HELP_LABEL = "Description"

# Reference positions of help buttons
HELP_BUT_DPOS_TUP = {'status': (10, 10),
                     'other' : (185, -2),
                    }


# Labels of items selection
PAGE_SELECT_LABEL_DICT = {'year': "Sélection de l'année ",
                          'data': "Données ",}

# Positions of labels for items selection
PAGE_SELECT_LABEL_POS_DICT = {KEY_PARSE_YEAR : (10, 100),
                              KEY_CONSO_YEAR : (80, 48),
                              KEY_ANALYS_YEAR: (10, 26),
                             }

# Relative positions of label for items selection 
PAGE_SELECT_LABEL_DPOS_DICT = {KEY_PARSE: (10, 2),}

PAGE_SELECT_BUT_DPOS_DICT = {KEY_PARSE : (1, -2),
                             KEY_CONSO : (0, -1.2),
                             KEY_ANALYS: (0, -1.2),
                            }

# Relative positions for step-launch buttons
STEP_BUT_DPOS_DICT = {KEY_PARSE : (15, 0.2),
                      KEY_DEDUP : (20, 0.2),
                      KEY_CONSO : (5, 2),
                      KEY_IF    : (10, 4),
                      KEY_ANALYS: (10, 2),
                     }

# Reference of positions and sizes
STEP_X_POS_REF = 15

# ******************************************
# **** STEPS GLOBALS OF SECONDARY-PAGES ****
# ******************************************

# Internal function
def _set_step_pos_tups(steps_nb, step_x_pos, steps_y_pos_init,
                       steps_dy, step0_pos_tup=None):
    if step0_pos_tup:
        step_y_pos_list = [steps_y_pos_init + n * steps_dy
                           for n in range(steps_nb-1)]
        step_pos_tups_part = [(step_x_pos, step_y_pos)
                              for step_y_pos in step_y_pos_list]
        step_pos_tups = sum([[step0_pos_tup], step_pos_tups_part], [])
        
    else:
        step_y_pos_list = [steps_y_pos_init + n * steps_dy
                           for n in range(steps_nb)]
        step_pos_tups = [(step_x_pos, step_y_pos)
                         for step_y_pos in step_y_pos_list]
    return step_pos_tups

# Initializing dicts for all pages and page steps
# -----------------------------------------------
STEPS_NB_DICT, STEP_POS_TUPS_DICT = {}, {}
STEPS_LABELS_DICT, STEPS_HELPS_DICT, STEPS_LAUNCHES_DICT = {}, {}, {}


# Parameters for all parsing-deduplication steps
# ----------------------------------------------
STEPS_NB_DICT[KEY_PARSE] = 3
STEP_POS_TUPS_DICT[KEY_PARSE] = _set_step_pos_tups(STEPS_NB_DICT[KEY_PARSE], STEP_X_POS_REF,
                                                   steps_y_pos_init=111, steps_dy=24,
                                                   step0_pos_tup=(10, 25))
STEPS_LABELS_DICT[KEY_PARSE], STEPS_HELPS_DICT[KEY_PARSE], STEPS_LAUNCHES_DICT[KEY_PARSE] = [], [], []

    # Parsing step 0
STEPS_LABELS_DICT[KEY_PARSE].append("Statut des fichiers")
STEPS_HELPS_DICT[KEY_PARSE].append("La disponibilté des fichiers bruts et des fichiers "
                                   "issus de leur analyse élémentaire va être examinée."
                                   "\n\nL'affichage va être mis à jour avec le résultat "
                                   "de cet examen.")
STEPS_LAUNCHES_DICT[KEY_PARSE].append("Mise à jour")

    # Parsing step 1
STEPS_LABELS_DICT[KEY_PARSE].append("Analyse élémentaire des extractions")
STEPS_HELPS_DICT[KEY_PARSE].append("Les données extraites de la base de donnée sélectionnée "
                                   "vont être analysées et les informations redistribuées "
                                   "par type dans plusieurs fichiers.")
STEPS_LAUNCHES_DICT[KEY_PARSE].append("Lancer l'analyse")

    # Parsing step 2
STEPS_LABELS_DICT[KEY_PARSE].append("Synthèse de l'analyse élémentaire")
STEPS_HELPS_DICT[KEY_PARSE].append("Les résultats de l'analyse des données extraites "
                                   "des différentes bases de données vont être concaténés "
                                   "et dédupliqués par type d'information")
STEPS_LAUNCHES_DICT[KEY_PARSE].append("Lancer la synthèse")


# Parameters for all consolidation steps
# -------------------------------------
STEPS_NB_DICT[KEY_CONSO] = 5
STEP_POS_TUPS_DICT[KEY_CONSO] = _set_step_pos_tups(STEPS_NB_DICT[KEY_CONSO], STEP_X_POS_REF,
                                                   steps_y_pos_init=60, steps_dy=24,
                                                   step0_pos_tup=(10, 25))
STEPS_LABELS_DICT[KEY_CONSO], STEPS_HELPS_DICT[KEY_CONSO], STEPS_LAUNCHES_DICT[KEY_CONSO] = [], [], []

    # Consolidation step 0
STEPS_LABELS_DICT[KEY_CONSO].append("Effectifs - Mise à jour des données")
STEPS_HELPS_DICT[KEY_CONSO].append("Le fichier original des effectifs va être complété "
                                   "avec les données du fichier de mise à jour disponible."
                                   "\n\nCette mise à jour n'a besoin d'être effectuée "
                                   "que si un nouveau fichier de mise à jour est disponible.")
STEPS_LAUNCHES_DICT[KEY_CONSO].append("Lancer la mise à jour")

    # Consolidation step 1
STEPS_LABELS_DICT[KEY_CONSO].append("Étape 1 - Croisement auteurs-efffectifs de l'institut")
STEPS_HELPS_DICT[KEY_CONSO].append("Deux fichiers avec une ligne par auteur de l'institut "
                                   "et par publication vont être créés à cette étape :"
                                   "\n\n - Un fichier avec les auteurs trouvés dans les effectifs "
                                   "qui permettra de construire la liste consolidée ;"
                                   "\n - Un fichier avec les auteurs non trouvés dans les effectifs "
                                   "dont l'examen permet d'alimenter les fichiers de correction.")
STEPS_LAUNCHES_DICT[KEY_CONSO].append("Effectuer le croisement auteurs-efffectifs")

    # Consolidation step 2
STEPS_LABELS_DICT[KEY_CONSO].append("Étape 2 - Résolution des homonymies")
STEPS_HELPS_DICT[KEY_CONSO].append("Un fichier avec une ligne par auteur de l'institut "
                                   "et par publication va être créé à cette étape indiquant "
                                   "les homonymes à traiter."
                                   "\nL'historique des résolutions va être pris en compte.")
STEPS_LAUNCHES_DICT[KEY_CONSO].append("Créer le fichier pour la résolution des homonymies")

    # Consolidation step 3
STEPS_LABELS_DICT[KEY_CONSO].append("Étape 3 - Attribution des OTPs")
STEPS_HELPS_DICT[KEY_CONSO].append("Un fichier par département avec une ligne par publication "
                                   "va être créé à cette étape avec une colonne pour l'attribution des OTPs."
                                   "\nL'historique des attributions va être pris en compte.")
STEPS_LAUNCHES_DICT[KEY_CONSO].append("Créer les fichiers pour l'attribution des OTPs")

    # Consolidation step 4
STEPS_LABELS_DICT[KEY_CONSO].append("Étape 4 - Consolidation de la liste des publications")
STEPS_HELPS_DICT[KEY_CONSO].append("Un fichier avec avec une ligne par publication avec "
                                   "l'OTP éventuellement attribué et le facteur d'impact trouvé "
                                   "pour le journal dans la base de données des IFs va être créé à cette étape."
                                   "\nDeux fichiers vont être également créés indiquant les informations manquantes "
                                   "dans la base de données des facteurs d'impact.")
STEPS_LAUNCHES_DICT[KEY_CONSO].append("Créer la liste consolidée des publications")


# Parameters for all IFs-update steps
# -----------------------------------
STEPS_NB_DICT[KEY_IF] = 2
STEP_POS_TUPS_DICT[KEY_IF] = _set_step_pos_tups(STEPS_NB_DICT[KEY_IF], STEP_X_POS_REF,
                                                steps_y_pos_init=35, steps_dy=50)
STEPS_LABELS_DICT[KEY_IF], STEPS_HELPS_DICT[KEY_IF], STEPS_LAUNCHES_DICT[KEY_IF] = [], [], []

    # IFs-update step 0
STEPS_LABELS_DICT[KEY_IF].append("Mise à jour de la base de données des IFs")
STEPS_HELPS_DICT[KEY_IF].append("La base de données sera mise à jour à partir des 2 fichiers annuels "
                                "complétés manuellement et contenant, respectivement :"
                                "\n- La liste des journaux dont l'IF est manquant;"
                                "\n- La liste des journaux dont l'ISSN est manquant.")
STEPS_LAUNCHES_DICT[KEY_IF].append("Lancer la mise à jour de la base de données des IFs")

    # IFs-update step 1
STEPS_LABELS_DICT[KEY_IF].append("Mise à jour des IFs dans les listes consolidées")
STEPS_HELPS_DICT[KEY_IF].append("Les IFs vont être mis à jour dans les listes consolidées "
                                "de publications existantes à partir de la base de données "
                                "des IFs."
                                "\n Cette opération n'est utile que si la base de données "
                                "des IFS a été mise à jour.")
STEPS_LAUNCHES_DICT[KEY_IF].append("Lancer la mise à jour des IFs dans les listes consolidées existantes")


# Parameters for all analysis steps
# ---------------------------------
STEPS_NB_DICT[KEY_ANALYS] = 4
STEP_POS_TUPS_DICT[KEY_ANALYS] = _set_step_pos_tups(STEPS_NB_DICT[KEY_ANALYS], STEP_X_POS_REF,
                                                    steps_y_pos_init=45, steps_dy=28)
STEPS_LABELS_DICT[KEY_ANALYS], STEPS_HELPS_DICT[KEY_ANALYS], STEPS_LAUNCHES_DICT[KEY_ANALYS] = [], [], []

    # Analysis step 0
STEPS_LABELS_DICT[KEY_ANALYS].append("Analyse des IFs et mise à jour des KPIs")
STEPS_HELPS_DICT[KEY_ANALYS].append("L'analyse des IFS est effectuée pour l'année sélectionnée "
                                    "à partir du fichier de la liste consolidée des publications."
                                    "\nLe fichier synthétisant les KPIs de toutes les années sera "
                                    "mis à jour avec les résultats de cette analyse.")
STEPS_LAUNCHES_DICT[KEY_ANALYS].append("Lancer l'analyse des IFs")

    # Analysis step 1
STEPS_LABELS_DICT[KEY_ANALYS].append("Analyse de la production des auteurs")
STEPS_HELPS_DICT[KEY_ANALYS].append("L'analyse des auteurs est effectuée pour l'année sélectionnée "
                                    "à partir du fichier issu de l'étape de croisement avec les effectifs.")
STEPS_LAUNCHES_DICT[KEY_ANALYS].append("Lancer l'analyse des auteurs")

    # Analysis step 2
STEPS_LABELS_DICT[KEY_ANALYS].append("Analyse des collaborations")
STEPS_HELPS_DICT[KEY_ANALYS].append("L'analyse des collaborations est effectuée pour l'année sélectionnée "
                                    "à partir des fichiers issus de l'étape de parsing du corpus.")
STEPS_LAUNCHES_DICT[KEY_ANALYS].append("Lancer l'analyse des collaborations")

    # Analysis step 3
STEPS_LABELS_DICT[KEY_ANALYS].append("Analyse des mots clefs")
STEPS_HELPS_DICT[KEY_ANALYS].append("L'analyse des mots clefs est effectuée pour l'année sélectionnée "
                                    "à partir des fichiers issus de l'étape de parsing du corpus.")
STEPS_LAUNCHES_DICT[KEY_ANALYS].append("Lancer l'analyse des mots clefs")


# ******************************************
# **** SPECIFIC GLOBALS OF PARSING PAGE ****
# ******************************************

# Parameters for display of parsing files status
BOX_POS_TUP = (70, 40)
BOX_Y_DPOS = 10
BOX_SEP_SPACE = 25

BOX_TABLE_COLS_DICT = {'raw_wos'     : 'Wos\nDonnées',
                       'wos_parse'   : 'Wos\nAnalyse',
                       'raw_scopus'  : 'Scopus\nDonnées',
                       'scopus_parse': 'Scopus\nAnalyse',
                       KEY_DEDUP     : 'Synthèse\n',
                      }

BOX_TABLE_POS_DICT = {'x_shift': 25,
                      'y_pos'  : 30,}

STATUS_BUT_POS_TUP = (20, 62)
