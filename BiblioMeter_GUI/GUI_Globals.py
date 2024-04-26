__all__ = ['ADD_SPACE_MM',           
           'BM_GUI_DISP',
           'CORPUSES_NUMBER',
           'ETAPE_LABEL_TEXT_LIST',
           'FONT_NAME',
           'HELP_ETAPE_5',
           'HELP_ETAPE_6',
           'HELP_ETAPE_7',
           'HELP_ETAPE_8',
           'IN_TO_MM',
           'PAGEBUTTON_HEIGHT_PX',
           'PAGES_LABELS',
           'PPI',
           'REF_BMF_FONT_SIZE',
           'REF_BMF_POS_X_MM',
           'REF_BMF_POS_Y_MM',
           'REF_BUTTON_DX_MM',
           'REF_BUTTON_DY_MM',
           'REF_BUTTON_FONT_SIZE',
           'REF_CHECK_BOXES_SEP_SPACE',
           'REF_COPYRIGHT_FONT_SIZE',
           'REF_COPYRIGHT_X_MM',
           'REF_COPYRIGHT_Y_MM',
           'REF_CORPI_POS_X_MM',
           'REF_CORPI_POS_Y_MM',
           'REF_ENTRY_NB_CHAR',
           'REF_ETAPE_BUT_DX_MM',
           'REF_ETAPE_BUT_DY_MM',
           'REF_ETAPE_CHECK_DY_MM',
           'REF_ETAPE_FONT_SIZE',
           'REF_ETAPE_POS_X_MM',
           'REF_ETAPE_POS_Y_MM_LIST',
           'REF_EXIT_BUT_POS_X_MM',
           'REF_EXIT_BUT_POS_Y_MM',
           'REF_INST_POS_X_MM',
           'REF_INST_POS_Y_MM',
           'REF_LABEL_FONT_SIZE',
           'REF_LABEL_POS_Y_MM',
           'REF_LAUNCH_FONT_SIZE',
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
           'TEXT_BDD_PC',
           'TEXT_BMF',
           'TEXT_BMF_CHANGE',
           'TEXT_BOUTON_CREATION_CORPUS',
           'TEXT_BOUTON_LANCEMENT',
           'TEXT_COPYRIGHT',
           'TEXT_CORPUSES',
           'TEXT_CROISEMENT',
           'TEXT_ETAPE_1',
           'TEXT_ETAPE_2',
           'TEXT_ETAPE_3',
           'TEXT_ETAPE_4',
           'TEXT_ETAPE_5',
           'TEXT_ETAPE_6',
           'TEXT_ETAPE_7',
           'TEXT_ETAPE_8',
           'TEXT_HOMONYMES',
           'TEXT_KW_ANALYSIS', 
           'TEXT_IF_ANALYSIS',
           'TEXT_INSTITUTE',
           'TEXT_LAUNCH_PARSING', 
           'TEXT_LAUNCH_SYNTHESE',
           'TEXT_MAJ_BDD_IF',
           'TEXT_MAJ_EFFECTIFS',
           'TEXT_MAJ_PUB_IF',
           'TEXT_OTP',
           'TEXT_PAUSE',
           'TEXT_PARSING',
           'TEXT_PUB_CONSO',
           'TEXT_STATUT',
           'TEXT_SYNTHESE',
           'TEXT_TITLE',
           'TEXT_UPDATE_STATUS',
           'TEXT_VERSION',
           'TEXT_YEAR_PC',
           'TEXT_YEAR_PI',                     
           ]


################################## General globals ##################################

# Setting BiblioMeter version value (internal)
VERSION ='4.0.0'

# Setting the number of corpuses to analyse
CORPUSES_NUMBER = 6

# Setting the title of the application main window (internal)
APPLICATION_WINDOW_TITLE = f"BiblioMeter - Analyse de la production scientifique d'un institut"

######################## Definition of display globals ###########################

def _get_displays(in_to_mm): 
    
    ''' The function `get_displays` allows to identify the set of displays
        available within the user hardware and to get their parameters.
        If the width or the height of a display are not available in mm 
        through the `get_monitors` method (as for Darwin platforms), 
        the user is asked to specify the displays diagonal size to compute them.
        
    Returns:
        `list`: list of dicts with one dict per detected display,
                each dict is keyed by 8 display parameters.   
    '''
    # To Do: convert prints and inputs to gui displays and inputs
    
    # Standard library imports
    import math
    
    # 3rd party imports
    from screeninfo import get_monitors
    
    displays = [{'x':m.x,'y':m.y,'width':m.width,
                 'height':m.height,'width_mm':m.width_mm,
                 'height_mm':m.height_mm,'name':m.name,
                 'is_primary':m.is_primary} for m in get_monitors()]
    
    for disp in range(len(displays)):
        width_px = displays[disp]['width']
        height_px = displays[disp]['height']
        diag_px = math.sqrt(int(width_px)**2 + int(height_px)**2)    
        width_mm = displays[disp]['width_mm']
        height_mm = displays[disp]['height_mm']
        if width_mm is None or height_mm is None: 
            diag_in = float(input('Enter the diagonal size of the screen n°' + str(disp) + ' (inches)'))
            width_mm = round(int(width_px) * (diag_in/diag_px) * in_to_mm,1)
            height_mm = round(int(height_px) * (diag_in/diag_px) * in_to_mm,1)
            displays[disp]['width_mm'] = str(width_mm)
            displays[disp]['height_mm'] = str(height_mm)
        else:
            diag_in = math.sqrt(float(width_mm) ** 2 + float(height_mm) ** 2) / in_to_mm
        displays[disp]['ppi'] = round(diag_px/diag_in,2)
        
    return displays

# Conversion factor for inch to millimeter
IN_TO_MM = 25.4 

DISPLAYS = _get_displays(IN_TO_MM)

# Setting primary display
BM_GUI_DISP = 0

# Getting display resolution in pixels per inch 
PPI = DISPLAYS[BM_GUI_DISP]['ppi']

# Setting display reference sizes in pixels and mm (internal)
REF_SCREEN_WIDTH_PX       = 1920
REF_SCREEN_HEIGHT_PX      = 1080
REF_SCREEN_WIDTH_MM       = 467
REF_SCREEN_HEIGHT_MM      = 267

# Application window reference sizes in mm for the display reference sizes (internal)
REF_WINDOW_WIDTH_MM       = 219
REF_WINDOW_HEIGHT_MM      = 173


#################################################################### 
##########################  Pages globals ########################## 
#################################################################### 


# Setting general globals for text edition
FONT_NAME = "Helvetica"

########################## Reference coordinates for pages ##########################

# Number of characters reference for editing the entered files-folder path 
REF_ENTRY_NB_CHAR          = 100     #100

# Font size references for page label and button
REF_SUB_TITLE_FONT_SIZE    = 15      #15
REF_PAGE_TITLE_FONT_SIZE   = 30      #30
REF_LAUNCH_FONT_SIZE       = 25      #25
REF_BMF_FONT_SIZE          = 15      #15        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
REF_BUTTON_FONT_SIZE       = 12      #10
REF_COPYRIGHT_FONT_SIZE    = 12      #10
REF_VERSION_FONT_SIZE      = 12      #10

# Y position reference in mm for page label
REF_PAGE_TITLE_POS_Y_MM    = 20      #20 

# Positions reference in mm for institute selection button
REF_INST_POS_X_MM          = 5       #5
REF_INST_POS_Y_MM          = 40      #45

# Positions reference in mm for bmf label and button
REF_BMF_POS_X_MM           = 5       #5
REF_BMF_POS_Y_MM           = 55      #45
REF_BUTTON_DX_MM           = -147    #-147
REF_BUTTON_DY_MM           = 10      #10

# Positions reference in mm for corpus creation button
REF_CORPI_POS_X_MM         = 5       #5
REF_CORPI_POS_Y_MM         = 85      #75

# Space between label and value
ADD_SPACE_MM               = 10      #10

# Setting X and Y positions reference in mm for copyright
REF_COPYRIGHT_X_MM         = 5       #5
REF_COPYRIGHT_Y_MM         = 170     #170
REF_VERSION_X_MM           = 185     #185

# Font size references for page label and button
REF_LABEL_FONT_SIZE        = 25      #25
REF_ETAPE_FONT_SIZE        = 14      #14
REF_BUTTON_FONT_SIZE       = 10      #10

# Positions reference in mm for pages widgets
REF_LABEL_POS_Y_MM         = 15      #15
REF_ETAPE_POS_X_MM         = 10      #10
REF_ETAPE_POS_Y_MM_LIST    = [40, 74, 101, 129]   #[40, 74, 101, 129]
REF_ETAPE_BUT_DX_MM        = 10      #10
REF_ETAPE_BUT_DY_MM        = 5       #5
REF_ETAPE_CHECK_DY_MM      = -8      #-8
REF_EXIT_BUT_POS_X_MM      = 193     #193
REF_EXIT_BUT_POS_Y_MM      = 145     #145
REF_YEAR_BUT_POS_X_MM      = 10      #10
REF_YEAR_BUT_POS_Y_MM      = 26      #26

# Separation space in mm for check boxes
REF_CHECK_BOXES_SEP_SPACE  = 25      #25

# Container button height in pixels
PAGEBUTTON_HEIGHT_PX = 50      #50

# Setting label for each gui page
PAGES_LABELS = {'Page_ParseCorpus'      : "Analyse élémentaire des corpus",
                'Page_ConsolidateCorpus': "Consolidation annuelle des corpus",
                'Page_UpdateIFs'        : "Mise à jour des facteurs d'impact",
                'Page_Analysis'        : "KPIs et graphes"
               }

########################## Cover Page (BiblioMeter launching Page) ##########################

# Titre de la page
TEXT_TITLE                  = "- BiblioMeter -\nInitialisation de l'analyse"

# Choix de l'année de l'Institut
TEXT_INSTITUTE              = "Sélection de l'Institut"

# Titre LabelEntry of BiblioMeter_Files folder
TEXT_BMF                    = "Dossier de travail "

# Titre bouton changement de dossier de travail
TEXT_BMF_CHANGE             = "Changer de dossier de travail"

# Titre liste des corpus analysés
TEXT_CORPUSES               = "Liste des corpus "

# Titre bouton création d'un dossier nouveau de corpus
TEXT_BOUTON_CREATION_CORPUS = "Créer un nouveau dossier de corpus annuel"

# Titre bouton de lancement
TEXT_BOUTON_LANCEMENT       = "Lancer l'analyse"

# Copyright and contacts
TEXT_COPYRIGHT              =   "Contributeurs et contacts :"
TEXT_COPYRIGHT             +=  "\n- Amal Chabli : amal.chabli@orange.fr"
TEXT_COPYRIGHT             +=  "\n- François Bertin : francois.bertin7@wanadoo.fr"
TEXT_COPYRIGHT             +=  "\n- Ludovic Desmeuzes"
TEXT_VERSION                = f"\nVersion {VERSION}"

##########################  Secondary pages ########################## 

# Common to secondary pages
TEXT_PAUSE           = "Mettre en pause"

###############  Parsing page

# - Label STATUT
TEXT_STATUT          = "Statut des fichiers de Parsing"

# - Label Parsing
TEXT_PARSING         = "Construction des fichiers de Parsing par BDD"

# - Label SYNTHESE
TEXT_SYNTHESE        = "Synthèse des fichiers de Parsing de toutes les BDD"

# - Label ANNEE
TEXT_YEAR_PC         = "Sélection de l'année "

# -Label choix de BDD
TEXT_BDD_PC          = "Sélection de la BDD "

# - Bouton mise à jour du statut des fichiers
TEXT_UPDATE_STATUS   = "Mettre à jour le statut des fichiers"

# - Bouton lancement parsing
TEXT_LAUNCH_PARSING  = "Lancer le Parsing"

# - Bouton lancement concatenation et deduplication des parsings
TEXT_LAUNCH_SYNTHESE = "Lancer la synthèse"


###############  Consolidation page

# Choix de l'année de travail
TEXT_YEAR_PI       = "Sélection de l'année "

### - Etape 1
TEXT_ETAPE_1       = f"Etape 1 : Croisement auteurs-efffectifs de l'institut"
TEXT_MAJ_EFFECTIFS = "Mettre à jour les effectifs de l'institut avant le croisement (coché = OUI) ?"
TEXT_CROISEMENT    = f"Effectuer le croisement auteurs-efffectifs"

### - Etape 2
TEXT_ETAPE_2       = "Etape 2 : Résolution des homonymies"
TEXT_HOMONYMES     = "Créer le fichier pour la résolution des homonymies"

### - Etape 3
TEXT_ETAPE_3       = "Etape 3 : Attribution des OTPs"
TEXT_OTP           = "Créer les fichiers pour l'attribution des OTPs"

### - Etape 4
TEXT_ETAPE_4       = "Etape 4 : Consolidation de la liste des publications" 
TEXT_MAJ_DB_IF     = " Mettre à jour la base de données IF avant la consolidation (coché = OUI) ?"
TEXT_PUB_CONSO     = "Créer la liste consolidée des publications"


ETAPE_LABEL_TEXT_LIST = [TEXT_ETAPE_1, TEXT_ETAPE_2, TEXT_ETAPE_3, TEXT_ETAPE_4]

###############  Impact-factors update page

### - Etape 5
TEXT_ETAPE_5    = "Mise à jour de la base de données des IFs"
HELP_ETAPE_5    = " La base de données sera mise à jour à partir des fichiers : "
HELP_ETAPE_5   += "\n  'IF manquants.xlsx' et 'ISSN manquants.xlsx' annuels"
HELP_ETAPE_5   += "\ncomplétés manuellement."
TEXT_MAJ_BDD_IF = "Lancer la mise à jour de la base de données des IFs"


### - Etape 6
TEXT_ETAPE_6    = "Mise à jour des IFs dans les listes consolidées"
HELP_ETAPE_6    = " Dans cette partie, vous pouvez mettre à jour les IFs"
HELP_ETAPE_6   += " dans les listes consolidées de publications existantes."
TEXT_MAJ_PUB_IF = "Lancer la mise à jour des IFs dans les listes consolidées existantes"


###############  Analysis page

### - Etape 7
TEXT_ETAPE_7     = "Analyse des IFs et mise à jour des KPIs"
HELP_ETAPE_7     = " L'analyse des IFS est effectuée à partir des fichiers"
HELP_ETAPE_7    += " des listes consolidées des publications."
TEXT_IF_ANALYSIS = "Lancer l'analyse des IFs"


### - Etape 8
TEXT_ETAPE_8     = "Analyse des mots clefs"
HELP_ETAPE_8     = " L'analyse des mots clefs est effectuée à partir des fichiers"
HELP_ETAPE_8    += " issus de l'étape de parsing des corpus."
TEXT_KW_ANALYSIS = "Lancer l'analyse des mots clefs"