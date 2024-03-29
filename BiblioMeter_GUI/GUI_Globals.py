__all__ = ['general_properties',
           'root_properties',
           'ADD_SPACE_MM',
           'BDD_LIST',           
           'BM_GUI_DISP',
           'CONTAINER_BUTTON_HEIGHT_PX',
           'CORPUSES_NUMBER',
           'ETAPE_LABEL_TEXT_LIST',
           'FONT_NAME',
           'HELP_ETAPE_5',
           'HELP_ETAPE_6',
           'HELP_ETAPE_7',
           'HELP_ETAPE_8',
           'INSTITUTE',
           'PAGES_LABELS',
           'PAGES_NAMES',
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
           'REF_LABEL_FONT_SIZE',
           'REF_LABEL_POS_Y_MM',
           'REF_LAUNCH_FONT_SIZE',
           'REF_PAGE_TITLE_FONT_SIZE',
           'REF_PAGE_TITLE_POS_Y_MM',
           'REF_VERSION_FONT_SIZE',
           'REF_VERSION_X_MM',
           'REF_YEAR_BUT_POS_X_MM',
           'REF_YEAR_BUT_POS_Y_MM',
           'ROOT_PATH',
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


# BiblioAnalysis_Utils package globals imports
from BiblioAnalysis_Utils.BiblioSys import DISPLAYS


################################## General globals ##################################

# Setting BiblioMeter version value (internal)
VERSION ='3.7.0'

# Setting the default value for the working directory
ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.2-Infos communes\BiblioMeter\BiblioMeter_Files"

# Setting the number of corpuses to analyse
CORPUSES_NUMBER = 6

# Setting the databases of corpuses extraction
BDD_LIST = ['wos','scopus']

# Setting institute name
INSTITUTE = "Liten"

# Setting the title of the application main window (internal)
APPLICATION_WINDOW_TITLE = f"BiblioMeter - Analyse de la production scientifique de l'institut {INSTITUTE}"

# Setting primery display
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

def general_properties(self):
    '''The function `general_properties` calculate the window sizes 
    and useful scale factors for the application launch window.
    For that, it uses reference values for the display sizes in pixels
    and mm through the globals:
    - "REF_SCREEN_WIDTH_PX" and "REF_SCREEN_HEIGHT_PX";
    - "REF_SCREEN_WIDTH_MM" and "REF_SCREEN_HEIGHT_MM".
    The secondary window sizes in mm are set through the globals: 
    - "REF_WINDOW_WIDTH_MM" and "REF_WINDOW_HEIGHT_MM".
    The window title is set through the global "APPLICATION_TITLE".
    These globals are defined locally in the module "Coordinates.py" 
    of the package "BiblioMeter_GUI".
    
    Args:
        self (???): ????.
        
    Returns:
        (tuple): self, 2 window sizes in pixels, 2 scale factors for sizes in mm 
                 and 2 scale factors for sizes in pixels.
    '''
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS
    
    # Getting number of pixels per inch screen resolution from imported global DISPLAYS
    ppi = DISPLAYS[BM_GUI_DISP]["ppi"]
    
    # Getting screen effective sizes in pixels for window "root" (not woring for Darwin platform)
    screen_width_px  = self.winfo_screenwidth()
    screen_height_px = self.winfo_screenheight()
    
    # Setting screen effective sizes in mm from imported global DISPLAYS
    screen_width_mm  = DISPLAYS[BM_GUI_DISP]["width_mm"]
    screen_height_mm = DISPLAYS[BM_GUI_DISP]["height_mm"]
    
    # Setting screen reference sizes in pixels and mm from globals internal to module "Coordinates.py"
    ref_width_px  = REF_SCREEN_WIDTH_PX
    ref_height_px = REF_SCREEN_HEIGHT_PX
    ref_width_mm  = REF_SCREEN_WIDTH_MM
    ref_height_mm = REF_SCREEN_HEIGHT_MM
    
    # Setting secondary window reference sizes in mm from globals internal to module "Coordinates.py"
    ref_window_width_mm  = REF_WINDOW_WIDTH_MM
    ref_window_height_mm = REF_WINDOW_HEIGHT_MM
    
    # Computing ratii of effective screen sizes to screen reference sizes in pixels
    scale_factor_width_px  = screen_width_px / ref_width_px
    scale_factor_height_px = screen_height_px / ref_height_px
        
    # Computing ratii of effective screen sizes to screen reference sizes in mm   
    scale_factor_width_mm  = screen_width_mm / ref_width_mm
    scale_factor_height_mm = screen_height_mm / ref_height_mm
    
    # Computing secondary window sizes in pixels depending on scale factors
    win_width_px  = _mm_to_px(ref_window_width_mm * scale_factor_width_mm, ppi)    
    win_height_px = _mm_to_px(ref_window_height_mm * scale_factor_height_mm, ppi)
    
    # Setting window size depending on scale factor
    self.geometry(f"{win_width_px}x{win_height_px}")
    self.resizable(False, False)
    
    # Setting title window
    self.title(APPLICATION_WINDOW_TITLE)
    
    sizes_tuple = (win_width_px, win_height_px, 
                   scale_factor_width_px, scale_factor_height_px, 
                   scale_factor_width_mm, scale_factor_height_mm)
    return self, sizes_tuple


def root_properties(root):
    '''The function `root_properties` calculate the window sizes 
    and useful scale factors for the application secondary windows.
    For that, it uses reference values for the display sizes in pixels
    and mm through the globals:
    - "REF_SCREEN_WIDTH_PX" and "REF_SCREEN_HEIGHT_PX";
    - "REF_SCREEN_WIDTH_MM" and "REF_SCREEN_HEIGHT_MM".
    The secondary window sizes in mm are set by the globals: 
    - "REF_WINDOW_WIDTH_MM" and "REF_WINDOW_HEIGHT_MM".
    These globals are defined locally in the module "Coordinates.py" 
    of the package "BiblioMeter_GUI".
    
    Args:
        root (str): reference window for getting screen information
        
    Returns:
        (tuple): 2 window sizes in pixels, 2 scale factors for sizes in mm 
                 and 2 scale factors for sizes in pixels.
    '''
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS
    
    # Getting number of pixels per inch screen resolution from imported global DISPLAYS
    ppi = DISPLAYS[BM_GUI_DISP]["ppi"]
    
    # Getting screen effective sizes in pixels for window "root" (not woring for Darwin platform)
    screen_width_px  = root.winfo_screenwidth()
    screen_height_px = root.winfo_screenheight()
    
    # Setting screen effective sizes in mm from imported global DISPLAYS
    screen_width_mm  = DISPLAYS[BM_GUI_DISP]["width_mm"]
    screen_height_mm = DISPLAYS[BM_GUI_DISP]["height_mm"]
    
    # Setting screen reference sizes in pixels and mm from globals internal to module "Coordinates.py"
    ref_width_px  = REF_SCREEN_WIDTH_PX
    ref_height_px = REF_SCREEN_HEIGHT_PX
    ref_width_mm  = REF_SCREEN_WIDTH_MM
    ref_height_mm = REF_SCREEN_HEIGHT_MM
    
    # Setting secondary window reference sizes in mm from globals internal to module "Coordinates.py"
    ref_window_width_mm  = REF_WINDOW_WIDTH_MM
    ref_window_height_mm = REF_WINDOW_HEIGHT_MM
    
    # Computing ratii of effective screen sizes to screen reference sizes in pixels
    scale_factor_width_px  = screen_width_px / ref_width_px
    scale_factor_height_px = screen_height_px / ref_height_px
        
    # Computing ratii of effective screen sizes to screen reference sizes in mm   
    scale_factor_width_mm  = screen_width_mm / ref_width_mm
    scale_factor_height_mm = screen_height_mm / ref_height_mm
    
    # Computing secondary window sizes in pixels depending on scale factors
    win_width_px  = _mm_to_px(ref_window_width_mm * scale_factor_width_mm, ppi)    
    win_height_px = _mm_to_px(ref_window_height_mm * scale_factor_height_mm, ppi)
    
    sizes_tuple = (win_width_px, win_height_px, 
                   scale_factor_width_px, scale_factor_height_px, 
                   scale_factor_width_mm, scale_factor_height_mm)
    return sizes_tuple


#################################################################### 
##########################  Pages globals ########################## 
#################################################################### 


# Setting general globals for text edition
FONT_NAME = "Helvetica"

########################## Reference coordinates for pages ##########################

# Number of characters reference for editing the entered files-folder path 
REF_ENTRY_NB_CHAR          = 100     #100

# Font size references for page label and button
REF_PAGE_TITLE_FONT_SIZE   = 30      #30
REF_LAUNCH_FONT_SIZE       = 25      #25
REF_BMF_FONT_SIZE          = 15      #15
REF_BUTTON_FONT_SIZE       = 12      #10
REF_COPYRIGHT_FONT_SIZE    = 12      #10
REF_VERSION_FONT_SIZE      = 12      #10

# Y position reference in mm for page label
REF_PAGE_TITLE_POS_Y_MM    = 20      #20 

# Positions reference in mm for bmf label and button
REF_BMF_POS_X_MM           = 5       #5
REF_BMF_POS_Y_MM           = 45      #45
REF_BUTTON_DX_MM           = -147    #-147
REF_BUTTON_DY_MM           = 10      #10

# Positions reference in mm for corpus creation button
REF_CORPI_POS_X_MM         = 5       #5
REF_CORPI_POS_Y_MM         = 75      #75

# Space between label and value
ADD_SPACE_MM               = 10      #10

# Setting X and Y positions reference in mm for copyright
REF_COPYRIGHT_X_MM         = 5       #5
REF_COPYRIGHT_Y_MM         = 170     #170
REF_VERSION_X_MM           = 185     #185

# Container button height in pixels
CONTAINER_BUTTON_HEIGHT_PX = 50      #50

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

# Setting label for each gui page
PAGES_LABELS = {'first' : "Analyse élémentaire des corpus",
                'second': "Consolidation annuelle des corpus",
                'third' : "Mise à jour des facteurs d'impact",
                'fourth': "KPIs et graphes"
               }


# Setting module name for each gui page
PAGES_NAMES = {'first' : 'Page_ParseCorpus',
               'second': 'Page_ConsolidateCorpus',
               'third' : 'Page_UpdateIFs',
               'fourth': 'Page_Analysis'
              }


########################## Cover Page (BiblioMeter launching Page) ##########################

# Titre de la page
TEXT_TITLE                  = "- BiblioMeter -\nInitialisation de l'analyse"

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
TEXT_ETAPE_1       = f"Etape 1 : Croisement auteurs-efffectifs de l'institut {INSTITUTE}"
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