# Taille de l'application

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 900

### Page_ParsingInstitutions

# - "Choix de l'année de travail
TEXT_YEAR_PI = "Choix de l'année de travail :"
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
TEXT_ETAPE_1 = f"Etape 1 : Croisement des pulications avec le fichier RH ainsi que création du fichier excel\npermettant mise en évidence et suppression des homonymes"
FONT_ETAPE_1 = ("Helvetica", 14)
FORMAT_TEXT_ETAPE_1 = 'left'
X_ETAPE_1 = x_etapes
Y_ETAPE_1 = 140
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
TEXT_CROISEMENT_L = f"Revenir en arrière sur combien d'année ?  N ="
FONT_CROISEMENT_L = ("Helvetica", taille_font_1)
FORMAT_CROISEMENT_L = 'left'

# - OptionMenu croisement
FONT_GOBACK = ("Helvetica", taille_font_1)

# - Consolidation homonymes
TEXT_CONSOLIDATION = "Consolidation homonymes"
FONT_CONSOLIDATION = ("Helvetica", taille_font_1)
X_CONSOLIDATION = 20
Y_CONSOLIDATION = 290

### - Etape 2
TEXT_ETAPE_2 = "Etape 2 : Si les homonymes ont été supprimés, vous pouvez maintenant passer à l'étape\nsuivante d'attribution des OTPs"
FONT_ETAPE_2 = ("Helvetica", 14)
FORMAT_TEXT_ETAPE_2 = 'left'
X_ETAPE_2 = x_etapes
Y_ETAPE_2 = 340
UNDERLINE_ETAPE_2 = -1

# - OTP
FONT_OTP = ("Helvetica", taille_font_1)

### - Etape 3
TEXT_ETAPE_3 = "Etape 3 : Et pour finir, après avoir enregistré les fichiers OTPs rempli sous le nom\nOTP_XXX_ok.xlsx, vous pouvez créer le fichier liste finale de l'année de travail"
FONT_ETAPE_3 = ("Helvetica", 14)
FORMAT_TEXT_ETAPE_3 = 'left'
X_ETAPE_3 = x_etapes
Y_ETAPE_3 = 500
UNDERLINE_ETAPE_3 = -1

# - Finale
FONT_FINALE = ("Helvetica", taille_font_1)

# - Concat
FONT_CONCAT = ("Helvetica", taille_font_1)