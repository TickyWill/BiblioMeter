__all__ = ['general_properties',
           'root_properties',
           'BM_GUI_DISP',
           'CONTAINER_BUTTON_HEIGHT_PX',
           'FONT_NAME',
           'REF_BUTTON_FONT_SIZE',
           'REF_CHECK_BOXES_SEP_SPACE',
           'REF_COPYRIGHT_FONT_SIZE',
           'REF_COPYRIGHT_X_MM',
           'REF_COPYRIGHT_Y_MM',
           'REF_ENTRY_NB_CHAR',
           'REF_LABEL_FONT_SIZE',
           'REF_LABEL_POS_Y_MM',
           'REF_LAUNCH_FONT_SIZE',
           'REF_LE_BMF_POS_Y_MM',
           'REF_LE_BUTTON_FONT_SIZE',
           'REF_LE_LABEL_FONT_SIZE',
           'REF_PAGE_TITLE_POS_Y_MM',
           'REF_PAGE_TITLE_FONT_SIZE',
           'TEXT_PAUSE',
           'TEXT_TITLE', 
           'TEXT_LE_BMF', 
           'TEXT_BOUTON_LANCEMENT', 
           'TEXT_COPYRIGHT',
           'TEXT_STATUT', 
           'TEXT_PARSING', 
           'TEXT_SYNTHESE',
           'TEXT_YEAR_PC', 
           'TEXT_BDD_PC', 
           'TEXT_UPDATE_STATUS', 
           'TEXT_LAUNCH_PARSING', 
           'TEXT_LAUNCH_SYNTHESE',
           'TEXT_YEAR_PI',
           'ETAPE_LABEL_TEXT_LIST',
           'TEXT_ETAPE_1',
           'TEXT_CROISEMENT',
           'TEXT_MAJ_EFFECTIFS',
           'TEXT_ETAPE_2',
           'TEXT_HOMONYMES',
           'TEXT_ETAPE_3',
           'TEXT_OTP',
           'TEXT_ETAPE_4',
           'TEXT_PUB_CONSO',
           'TEXT_ETAPE_5',  
           'HELP_ETAPE_5',
           'TEXT_MAJ_BDD_IF',
           'TEXT_ETAPE_6',  
           'HELP_ETAPE_6',
           'TEXT_MAJ_PUB_IF',
           'TEXT_ETAPE_7',  
           'HELP_ETAPE_7',
           'TEXT_IF_ANALYSIS',
           'TEXT_ETAPE_8',  
           'HELP_ETAPE_8',
           'TEXT_KW_ANALYSIS',
          ]


# Setting version value
VERSION ='3.6.0'

# Setting general globals for text edition
FONT_NAME = "Helvetica"

######################################################## Cover Page (launching BiblioMeter Page) ##################################

# Setting the title of the application launch window
APPLICATION_WINDOW_TITLE = "BiblioMeter - Analyse de la production scientifique du LITEN"

# Setting primery display
BM_GUI_DISP = 0

# Setting display reference sizes in pixels and mm
REF_SCREEN_WIDTH_PX       = 1920
REF_SCREEN_HEIGHT_PX      = 1080
REF_SCREEN_WIDTH_MM       = 467
REF_SCREEN_HEIGHT_MM      = 267

# Application window reference sizes in mm for the display reference sizes
REF_WINDOW_WIDTH_MM       = 219
REF_WINDOW_HEIGHT_MM      = 173
REF_CHECK_BOXES_SEP_SPACE = 25


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


########################## Main page ##########################

# Number of characters reference for editing the entered files-folder path 
REF_ENTRY_NB_CHAR          = 80      #80

# Font size references for page label and button
REF_PAGE_TITLE_FONT_SIZE   = 30      #30
REF_LAUNCH_FONT_SIZE       = 25      #25
REF_LE_LABEL_FONT_SIZE     = 15      #15
REF_LE_BUTTON_FONT_SIZE    = 10      #10
REF_COPYRIGHT_FONT_SIZE    = 10      #10

# Y position reference in mm for page label
REF_PAGE_TITLE_POS_Y_MM    = 20      #20 

# Y position reference in mm for le_bmf 
REF_LE_BMF_POS_Y_MM        = 45      #45

# Setting X and Y positions reference in mm for copyright
REF_COPYRIGHT_X_MM         = 5       #5
REF_COPYRIGHT_Y_MM         = 170     #170

## Container button height in pixels
CONTAINER_BUTTON_HEIGHT_PX = 50      #50

## Font size references for page label and button
REF_LABEL_FONT_SIZE        = 25      #25
REF_BUTTON_FONT_SIZE       = 10      #10

## Y_position reference in mm for page label
REF_LABEL_POS_Y_MM         = 15      #15

# Titre de la page
TEXT_TITLE            = "- BiblioMeter -\nInitialisation de l'analyse"

# Titre LabelEntry of BiblioMeter_Files folder
TEXT_LE_BMF           = "Dossier de travail :"

# Titre bouton de lancement
TEXT_BOUTON_LANCEMENT = "Lancer l'analyse"

# Copyright and contacts
TEXT_COPYRIGHT        =   "Contributeurs et contacts :"
TEXT_COPYRIGHT       +=  "\n- Amal Chabli : amal.chabli@orange.fr"
TEXT_COPYRIGHT       +=  "\n- François Bertin : francois.bertin7@wanadoo.fr"
TEXT_COPYRIGHT       +=  "\n- Ludovic Desmeuzes"
TEXT_COPYRIGHT       += f"\nVersion {VERSION}"



# Common to following pages
TEXT_PAUSE           = "Mettre en pause"

##########################  Page_ParseCorpus ########################## 

# - Label STATUT
TEXT_STATUT          = "Statut des fichiers de Parsing"

# - Label Parsing
TEXT_PARSING         = "Construction des fichiers de Parsing par BDD"

# - Label SYNTHESE
TEXT_SYNTHESE        = "Synthèse des fichiers de Parsing de toutes les BDD"

# - Label ANNEE
TEXT_YEAR_PC         = "Sélection de l'année :"

# -Label choix de BDD
TEXT_BDD_PC          = "Sélection de la BDD :"

# - Bouton mise à jour du statut des fichiers
TEXT_UPDATE_STATUS   = "Mettre à jour le statut des fichiers"

# - Bouton lancement parsing
TEXT_LAUNCH_PARSING  = "Lancer le Parsing"

# - Bouton lancement concatenation et deduplication des parsings
TEXT_LAUNCH_SYNTHESE = "Lancer la synthèse"


########################## Page_ConsolidateCorpus ##########################

# Variables communes à toutes les étapes mais pas globales
etape_taille_font    = 14
ss_etape_taille_font = etape_taille_font-3
else_taille_font     = etape_taille_font-1
x_etapes             = 15

# Choix de l'année de travail
TEXT_YEAR_PI       = "Sélection de l'année :"

### - Etape 1
TEXT_ETAPE_1       = f"Etape 1 : Croisement auteurs-efffectifs du LITEN"
TEXT_MAJ_EFFECTIFS = "Mettre à jour les effectifs du LITEN avant le croisement (coché = OUI) ?"
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

########################## Page_UpdateIFs ##########################

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


########################## Page_Analysis ##########################

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