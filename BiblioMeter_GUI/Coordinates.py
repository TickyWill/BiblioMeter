# Taille de l'application

### Cover Page (launching BiblioMeter Page)

def general_properties(self):
    
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    
    from BiblioMeter_GUI.Globals_GUI import DISPLAYS
    from BiblioMeter_GUI.Globals_GUI import GUI_DISP
    from BiblioMeter_GUI.Globals_GUI import PPI
    
    #print("Dans la fonction general_properties()")
     
    # Base size
    normal_width = 1920
    normal_height = 1080

    # Get screen size
    screen_width = self.winfo_screenwidth()
    print(f"Screen width in pixels : {screen_width}")
    screen_height = self.winfo_screenheight()
    print(f"Screen height in pixels : {screen_height}")
    
    # Get percentage of screen size from Base size
    p_scale_factor_W = screen_width / normal_width
    print(f"Width scale factor in pixels : {p_scale_factor_W}")
    p_scale_factor_H = screen_height / normal_height
    print(f"Height scale factor in pixels : {p_scale_factor_H}")
    
    # Base size mm
    normal_mm_w = 467
    normal_mm_h = 267

    scale_factor_W = DISPLAYS[GUI_DISP]["width_mm"] / normal_mm_w
    print(f"Width scale factor in mm : {scale_factor_W}")
    scale_factor_H = DISPLAYS[GUI_DISP]["height_mm"] / normal_mm_h
    print(f"Height scale factor in mm : {scale_factor_H}")
    
    # Set window size depending on scale factor
    win_width = int(mm_to_px(219, PPI) * scale_factor_W)
    win_height = int(mm_to_px(173, PPI) * scale_factor_H)
    print(f"Width in pixels of root window is {win_width} and height in pixels is {win_height}")

    # Set window size depending on scalre factor
    self.geometry(f"{win_width}x{win_height}")
    self.resizable(False, False)
    
    # Set title window
    self.title("BiblioMeter - Analyse des articles scientifiques")
    
    return self, win_width, win_height, scale_factor_W, scale_factor_H, p_scale_factor_W, p_scale_factor_H

def root_properties(root):
    
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    
    from BiblioMeter_GUI.Globals_GUI import DISPLAYS
    from BiblioMeter_GUI.Globals_GUI import GUI_DISP
    from BiblioMeter_GUI.Globals_GUI import PPI

    # Base size
    normal_width = 1920
    normal_height = 1080
    
    #print("Dans la fonction root_properties()")
    
    # Get screen size
    screen_width = root.winfo_screenwidth()
    #print(f"Screen width in pixels : {screen_width}")
    screen_height = root.winfo_screenheight()
    #print(f"Screen height in pixels : {screen_height}")
    
    # Get percentage of screen size from Base size
    p_scale_factor_W = screen_width / normal_width
    #print(f"SFWP : {p_scale_factor_W}")
    p_scale_factor_H = screen_height / normal_height
    #print(f"SFHP : {p_scale_factor_H}")
    
    # Base size mm
    normal_mm_w = 467
    normal_mm_h = 267

    scale_factor_W = DISPLAYS[GUI_DISP]["width_mm"] / normal_mm_w
    #print(f"SFW : {scale_factor_W}")
    scale_factor_H = DISPLAYS[GUI_DISP]["height_mm"] / normal_mm_h
    #print(f"SFH : {scale_factor_H}")
    
    # Set window size depending on scale factor
    win_width = int(mm_to_px(219, PPI) * scale_factor_W)
    win_height = int(mm_to_px(173, PPI) * scale_factor_H)
    #print(f"Width in pixels of root window is {win_width} and height in pixels is {win_height}")
    
    return win_width, win_height, scale_factor_W, scale_factor_H, p_scale_factor_W, p_scale_factor_H


# Titre de la page
TEXT_TITLE = "- BiblioMeter -\nAnalyse de la production scientifique du LITEN"

# Titre LabelEntry BMF
TEXT_LE_BMF = "Dossier de travail :"

# Titre bouton de lancement
TEXT_BOUTON_LANCEMENT = "Lancement de BiblioMeter"

### Page_ParsingConcat ######################################################

# - Label STATUT
TEXT_STATUT = "Statut des fichiers de parsing"

# - Label CONSTRU_PAR
TEXT_CONSTRU = "Construction des fichiers de parsing par BDD"

# - Label SYNTHESE
TEXT_SYNTHESE = "Synthèse des fichiers parsing de toutes les BDD"

# - Label ANNEE
TEXT_YEAR_PC = "Sélection de l'année :"

# -Label choix de BDD
TEXT_BDD_PC = "Sélection de la BDD :"

# - Bouton lancement parsing
TEXT_LAUNCH_PARSING = "Lancer le parsing"

TEXT_LAUNCH_SYNTHESE = "Lancer la synthèse"

### Page_ParsingInstitutions ################################################

# - "Choix de l'année de travail
TEXT_YEAR_PI = "Sélection de l'année :"
X_YEAR_PI = 90
Y_YEAR_PI = 90

# - "Choix de l'année de travail
TEXT_AFFI = "Choix d’affiliations supplémentaires\nautres que LITEN et INES"
X_AFFI = 400
Y_AFFI = 90

# Commun toutes les étapes
x_etapes = 15

### - Etape 1
# - Titre
TEXT_ETAPE_1 = f"Etape 1 : Croisement avec le fichier des efffectifs LITEN"
SOUS_TEXT_ETAPE_1 = f"Croisement des publications avec le fichier effectifs Liten. Les fichiers créés sont situés dans 0 - BDD multi mensuelle.\nSe référer à la doc dans MOD OP pour plus d'information."
FONT_ETAPE_1 = ("Helvetica", 14)
FONT_SOUS_ETAPE_1 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_1 = 'left'
X_ETAPE_1 = x_etapes
Y_ETAPE_1 = 135
UNDERLINE_ETAPE_1 = -1

# - Commun 
taille_font_1 = 13

# - Bouton croisement des publications
TEXT_CROISEMENT = f"Croiser les publications avec les effectifs Liten des N dernières années"
FONT_CROISEMENT = ("Helvetica", taille_font_1)
X_CROISEMENT = 20
Y_CROISEMENT = 200
UNDERLINE_CROISEMENT = -1

# - Label croisement des publications
TEXT_CROISEMENT_L = f"Nombre années de profondeur de recherche des auteurs dans les effectifs du LITEN.  N ="
FONT_CROISEMENT_L = ("Helvetica", taille_font_1)
FORMAT_CROISEMENT_L = 'left'

# - OptionMenu croisement
FONT_GOBACK = ("Helvetica", taille_font_1)

# - Consolidation homonymes
TEXT_CONSOLIDATION = "Création du fichier résolution des homonymies"
FONT_CONSOLIDATION = ("Helvetica", taille_font_1)
X_CONSOLIDATION = 20
Y_CONSOLIDATION = 290

### - Etape 2
TEXT_ETAPE_2 = "Etape 2 : Résolution des homonymies"
SOUS_TEXT_ETAPE_2 = f"Création du fichier qui permet de supprimer les faux homonymes. Le fichier sera dans Année / 1 - Consolidation."
FONT_ETAPE_2 = ("Helvetica", 14)
FONT_SOUS_ETAPE_2 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_2 = 'left'
X_ETAPE_2 = x_etapes
Y_ETAPE_2 = 267
UNDERLINE_ETAPE_2 = -1

# - OTP
TEXT_OTP = "Création des quatre fichiers permettant l'ajout des OTP"
FONT_OTP = ("Helvetica", taille_font_1)

### - Etape 3
TEXT_ETAPE_3 = "Etape 3 : Attribution des OTP"
SOUS_TEXT_ETAPE_3 = f"Après suppression des faux homonymes, vous pouvez passer à l'attribution d'OTP à chacune des publications.\nQuatre fichiers seront crées dans Année / 2 - OTP, qui permettront l'attribution d'OTP."
FONT_ETAPE_3 = ("Helvetica", 14)
FONT_SOUS_ETAPE_3 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_3 = 'left'
X_ETAPE_3 = x_etapes
Y_ETAPE_3 = 340
UNDERLINE_ETAPE_3 = -1

### - Etape 4
TEXT_ETAPE_4 = "Etape 4 : Création de la liste consolidée des publications"
SOUS_TEXT_ETAPE_4 = f"Avec les OTP renseignés dans les quatre documents crées dans l'étape 3 il est possible de créer le fichier\nListe Finale dans Année / 3 - Résultats Finaux qui rassemblent toutes les informations de l'année."
FONT_ETAPE_4 = ("Helvetica", 14)
FONT_SOUS_ETAPE_4 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_4 = 'left'
X_ETAPE_4 = x_etapes
Y_ETAPE_4 = 425
UNDERLINE_ETAPE_4 = -1

### - Etape 5
TEXT_ETAPE_5 = "Affectation et Mise à jour des IFs"
SOUS_TEXT_ETAPE_5 = f"Concatenation des différentes années et mise à jour des (fin de phrase) IF sur le fichier des années concatenées entre elles. Le fichier\ncréé sera dans le répertoire BDD multi annuelle et sera nommé en fonction de la date, de l'heure et de votre nom de compte."
FONT_ETAPE_5 = ("Helvetica", 14)
FONT_SOUS_ETAPE_5 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_5 = 'left'
X_ETAPE_5 = x_etapes
Y_ETAPE_5 = 120
UNDERLINE_ETAPE_5 = -1
HELP_ETAPE_5 = """Dans cette partie sont mis à jour les IF lorsqu'ils sont diponibles en juillet de chaque année.\nVeuillez sélectionner, dans le dossier BDD multi annuelle, le fichier de liste consolidée de publications à mettre à jour."""

# - Finale
TEXT_FINALE = "Concatener les fichiers listes finales\ndes différentes années"
FONT_FINALE = ("Helvetica", taille_font_1)

# - Concat
FONT_CONCAT = ("Helvetica", taille_font_1)

# - MAJ_IF
TEXT_MAJ_IF = "Lancement de la mise à jour des IF"
FONT_MAJ_IF = ("Helvetica", taille_font_1)