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
TEXT_ETAPE_1 = f"Etape 1 :"
SOUS_TEXT_ETAPE_1 = f"Croisement des publications avec le fichier RH. Les fichiers créés sont situés dans 0 - BDD multi mensuelle.\nSe référer à la doc dans MOD OP pour plus d'information."
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
TEXT_CROISEMENT_L = f"Revenir en arrière sur combien d'année depuis aujourd'hui ?  N ="
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
TEXT_ETAPE_2 = "Etape 2 :"
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
TEXT_ETAPE_3 = "Etape 3 :"
SOUS_TEXT_ETAPE_3 = f"Après suppression des faux homonymes, vous pouvez passer à l'attribution d'OTP à chacune des publications.\nQuatre fichiers seront crées dans Année / 2 - OTP, qui permettront l'attribution d'OTP."
FONT_ETAPE_3 = ("Helvetica", 14)
FONT_SOUS_ETAPE_3 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_3 = 'left'
X_ETAPE_3 = x_etapes
Y_ETAPE_3 = 340
UNDERLINE_ETAPE_3 = -1

### - Etape 4
TEXT_ETAPE_4 = "Etape 4 :"
SOUS_TEXT_ETAPE_4 = f"Avec les OTP renseignés dans les quatre documents crées dans l'étape 3 il est possible de créer le fichier\nListe Finale dans Année / 3 - Résultats Finaux qui rassemblent toutes les informations de l'année."
FONT_ETAPE_4 = ("Helvetica", 14)
FONT_SOUS_ETAPE_4 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_4 = 'left'
X_ETAPE_4 = x_etapes
Y_ETAPE_4 = 425
UNDERLINE_ETAPE_4 = -1

### - Etape 5
TEXT_ETAPE_5 = "Etape 5 :"
SOUS_TEXT_ETAPE_5 = f"Concatenation des différentes années et mise à jour des IF sur le fichier des années concatenées entre elles. Le fichier\ncréé sera dans le répertoire BDD multi annuelle et sera nomé en fonction de la date, de l'heure et de votre nom de compte."
FONT_ETAPE_5 = ("Helvetica", 14)
FONT_SOUS_ETAPE_5 = ("Helvetica", 11)
FORMAT_TEXT_ETAPE_5 = 'left'
X_ETAPE_5 = x_etapes
Y_ETAPE_5 = 530
UNDERLINE_ETAPE_5 = -1

# - Finale
TEXT_FINALE = "Concatener les fichiers listes finales\ndes différentes années"
FONT_FINALE = ("Helvetica", taille_font_1)

# - Concat
FONT_CONCAT = ("Helvetica", taille_font_1)

# - MAJ_IF
TEXT_MAJ_IF = "Mettre à jour les IF\nde toutes les années confondues"
FONT_MAJ_IF = ("Helvetica", taille_font_1)