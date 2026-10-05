BiblioMeter description
***********************

Purpose
=======

- Outil d’aide à l’analyse de la production scientifique d’un institut
- Outil utilisable sans prérequis
    - d’installation du language de développement (lancement par un exécutable autoportant)
    - en connaissance de programmation
- La production scientifique brute est issue des bases de données bibliographiques courantes (WoS, Scopus, HAL...)
- L’outil produit des données nettoyées compatibles avec un traitement par les outils de bureautique disponibles de manière standard chez les utilisateurs (XLSX, TXT...)

Interfaces
==========

1. Analyse élémentaire des extractions des bases de données
-----------------------------------------------------------

- Redistribution des informations extraites de chaque base de données par type
    - Index des publications, auteurs, affiliations, pays, institutions, références, mots clefs par type, catégories de journal...
- Synthèse de ces informations à partir de toutes les bases de données utilisées
    - Normalisation de certaines informations pour le retrait des doublons
- Les informations disponibles ne sont pas toutes exploitées dans l’analyse approfondie mais sont prévues de l’être
    - Éditeur, nature du journal, auteur contact...

2. Consolidation des corpus par les données de l’Institut
---------------------------------------------------------
- Identification des attributs des auteurs affiliés à l’Institut
    - Matricule, département, service, labo, statut (CDI, CDD, Postdoctorants, Doctorants...)
- Gestion des homonymies et des erreurs (interventions manuelles)
    - Orthographe, métadonnées, collaborateurs externes...
    - Corrections pérennes indépendament du renouvellement des extractions
- Gestion de l’attribution des OTPs (interventions manuelles de validation)
    - Par département et/ou par laboratoire (choix par l'Institut)
    - Attributions pérennes indépendament du renouvellement des extractions
- Consolidation de la liste des publications intégrant toutes les informations traitées
    - Attributions des IFs disponibles et identification des manques

3. Analyse approfondie des corpus et calcul des indicateurs
-----------------------------------------------------------
- Analyse de la distribution de la production par type de publication
    - Journaux, actes de conférence, ouvrages...
- Analyses de la distribution de la production par auteurs de l'Institut
    - Nombre de publications par auteur, position de l'auteur...
- Analyses de la distribution de la production par affiliations des co-auteurs
    - Nombre de publications par type d'affiliation, par affiliation...
- Analyses de la distribution géographique des affiliations des co-auteurs
    - Nombre de publications par pays, par continents...
- Analyse de l’évolution temporelle des IFs
    - Max, min, moyen...
- Analyse des mots clefs par type
    - Auteurs, titre, journal...
- Analyses en cours de mise en place
    - Fonction des sujets, des éditeurs, du type d’accès (abonnement, libre, hybride)...

4. Interface d’utilisation
--------------------------
- Fenêtre principale de lancement
    - Gestion du dossier de travail
- Fenêtre de travail avec 4 onglets spécialisés
    - Analyse élémentaire des corpus (6 corpus annuels possibles)
    - Consolidation annuelle des corpus
    - Mise à jour des facteurs d’impact (au fur et à mesure de leur disponibilité)
    - Analyse et KPIs (analyse approfondie des corpus et calcul des indicateurs)
- Fenêtres « messages » en fonction de l’avancement du traitement
    - Gestion des erreurs prévisibles (ex : fichier attendu indisponible)
    - Gestion des erreurs non traitées sans arrêt fatal de l’outil
- Création d'un fichier contenant l'historique des tratements de chaque session

Input Data
==========

**La position de ces fichiers est prédéterminée dans l’arborescence du dossier de travail**

- Les variables globales spécifiques à chaque groupe de fonctions
    - Actuellement modifiables par intervention dans les modules dédiés du programme
    - En cours de basculement dans des fichiers « texte » structurés (yaml ou json)
- Fichiers annuels d’extraction des bases de données (Scopus, WoS...) spécifiques de l’Institut
- Fichiers annuels sur 10 ans des effectifs spécifiques de l’Institut
- Fichiers annuels sur 6 ans des facteurs d’impact pour les journaux spécifiques de l’Institut
- Fichier descriptif de l'organisation de l'Institut
    - Fichier JSON dont la structure du contenu est prédéterminée
- Fichier utiles pour la normalisation des affiliations
    - Fichier donnant des informations sur la structure des adresses pour chaque pays (ie. code postal)
    - Fichier donnant la liste des villes par pays
    - Fichier donnant le nom normalisé et les dénominations pouvant être rencontrées dans les métadonnées des publications pour chaque affiliation par pays
    - Fichier donnant le nom normalisé et les dénominations pouvant être rencontrées dans les métadonnées des publications pour l'Institut
    - Fichier donnant les différents types d'affiliation et leur ordre de priorité

Output Data
===========

**La position de ces fichiers est prédéterminée dans l’arborescence du dossier de travail**

- Les fichiers issus de l’analyse élémentaire des extractions
    - Fichiers TXT structurés (extension .DAT) pour chaque type d’information
- Les fichiers issus des étapes de consolidation des corpus
    - Fichiers XLSX pour les interventions manuelles (erreurs d’affiliation, homonymes, OTPs, IFs)
    - Fichiers XLSX des listes consolidées des publications pour une exploitation ultérieure libre
- Les fichiers issus des étapes d’analyse approfondie
    - Fichiers XLSX issus de l’analyse annuelle de la production par type de publication
    - Fichiers XLSX issus de l’analyse annuelle de la production par auteurs
    - Fichiers XLSX issus de l’analyse annuelle de la production en terme de collaborations
        - Nombre de publications par pays
        - Nombre de publications par continent
        - Liste des affiliations normalisées par publication
        - Liste des affiliations non encore normalisées par publication
    - Fichier XLSX rassemblant les indicateurs de l’ensemble des corpus annuels disponibles
    - Fichiers XLSX issus de l’analyse annuelle de la production par type de mots clefs
