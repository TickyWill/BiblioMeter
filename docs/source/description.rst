BiblioMeter description
***********************

Purpose
=======

- Outil d’aide à l’analyse de la production scientifique d’un institut
- Outil utilisable sans prérequis
    - d’installation du language de développement (lancement par un exécutable autoportant)
    - en connaissance de programmation
- La production scientifique brute est issue des bases de données bibliographiques courantes (WoS, Scopus, HAL, PubMed...)
- L’outil produit des données nettoyées compatibles avec un traitement par les outils de bureautique disponibles de manière standard chez les utilisateurs (xlsx, txt...)

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
    - Par département
    - Attributions pérennes indépendament du renouvellement des extractions
- Consolidation de la liste des publications intégrant toutes les informations traitées
    - Attributions des IFs disponibles et identification des manques

3. Analyse approfondie des corpus et calcul des indicateurs
-----------------------------------------------------------
- Analyse de la distribution de la production par type de publication
    - Journaux, actes de conférence, ouvrages...
- Analyse de l’évolution temporelle des IFs
    - Max, min, moyen...
- Analyse des mots clefs par type
    - Auteurs, titre, journal...
- Analyses en cours de mise en place
    - Fonction des auteurs, Institutions, éditeurs, type d’accès (abonnement, libre, hybride)...

4. Interface d’utilisation
--------------------------
- Fenêtre principale de lancement
    - Gestion du dossier de travail
- Fenêtre de travail avec 4 onglets spécialisés
    - Analyse élémentaire des corpus (6 corpus annuels possibles)
    - Consolidation annuelle des corpus
    - Mise à jour des facteurs d’impact (au fur et à mesure de leur disponibilité)
    - KPIs (analyse approfondie des corpus et calcul des indicateurs)
- Fenêtres « messages » en fonction de l’avancement du traitement
    - Gestion des erreurs prévisibles (ex : fichier attendu indisponible)
    - Gestion des erreurs non traitées sans arrêt fatal de l’outil

Input Data
==========

**La position de ces fichiers est prédéterminée dans l’arborescence du dossier de travail**

- Les variables globales spécifiques à chaque groupe de fonctions
    - Actuellement modifiables par intervention dans les modules dédiés du programme
    - En cours de basculement dans des fichiers « texte » structurés (yaml ou json)
- Fichiers annuels d’extraction des bases de données (Scopus, WoS...) spécifiques de l’Institut
    - Fichiers annuels sur 10 ans des effectifs spécifiques de l’Institut
    - Fichiers annuels sur 6 ans des facteurs d’impact pour les journaux spécifiques de l’Institut

Output Data
===========

**La position de ces fichiers est prédéterminée dans l’arborescence du dossier de travail**

- Les fichiers issus de l’analyse élémentaire des extractions
    - Fichiers « texte » structurés (dat) pour chaque type d’information
- Les fichiers issus des étapes de consolidation des corpus
    - Fichiers « xlsx » pour les interventions manuelles (erreurs d’affiliation, homonymes, OTPs, IFs)
    - Fichiers « xlsx » des listes consolidées des publications pour une exploitation ultérieure libre
- Les fichiers issus des étapes d’analyse approfondie
    - Fichiers « xlsx » issus de l’analyse annuelle de la production par type de publication
    - Fichiers « xlsx » issus de l’analyse annuelle de la production par type de mots clefs
    - Fichiers « xlsx » issus de l’analyse annuelle de la production en terme de collaborations
        - Nombre de publications par pays
        - Nombre de publications par continent
        - Liste des institutions normalisées par publication
        - Liste des institutions non encore normalisées par publication
    - Fichier « xlsx » rassemblant les indicateurs de l’ensemble des années disponibles
