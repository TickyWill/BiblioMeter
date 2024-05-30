"""The `consolidate_corpus_page` module allows to built consolidated publication lists 
for the Institute selected and the data type selected. It performs the merge 
of the publications list with the employees database of the Institute. 
Then it provides to the users xlsx files for :
- Authors metadata correction when not found in the employees database;
- Homonymies resolution;
- Publications OTPs setting;
- Completion of impact-factors database.
Finally it saves the consolidated publications list in a dedicated directory.
"""
__all__ = ['create_consolidate_corpus']


# Standard library imports
import os
import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import bmgui.gui_globals as gg
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_org_params
from bmfuncts.consolidate_pub_list import concatenate_pub_lists
from bmfuncts.consolidate_pub_list import consolidate_pub_list
from bmfuncts.consolidate_pub_list import solving_homonyms
from bmfuncts.consolidate_pub_list import add_otp
from bmfuncts.merge_pub_employees import recursive_year_search
from bmfuncts.update_employees import update_employees
from bmfuncts.use_pub_attributes import save_homonyms
from bmfuncts.use_pub_attributes import set_saved_otps
from bmfuncts.use_pub_attributes import set_saved_homonyms
from bmfuncts.useful_functs import check_dedup_parsing_available
from bmgui.gui_functions import font_size
from bmgui.gui_functions import mm_to_px
from bmgui.gui_functions import place_after
from bmgui.gui_functions import place_bellow
from bmgui.gui_functions import set_exit_button
from bmgui.gui_functions import set_page_title


def _launch_update_employees(bibliometer_path,
                             year_select,
                             maj_effectifs_folder_path,
                             effectifs_file_name_alias,
                             effectifs_folder_path,
                             check_effectif_status,
                             ):
    """
    """
    update_status = False
    if check_effectif_status:
        # Launch employees database update
        ask_title = "- Confirmation de la mise à jour des effectifs -"
        ask_text  = "Le fichier des effectifs de l'Institut va être mis à jour "
        ask_text += "avec les nouvelles données disponibles dans le dossier :"
        ask_text += f"\n\n '{maj_effectifs_folder_path}'."
        ask_text += "\n\nCette opération peut prendre quelques minutes."
        ask_text += "\nDans l'attente, ne pas fermer 'BiblioMeter'."
        ask_text += "\n\nAvant de poursuivre le croisement auteurs-effectifs, "
        ask_text += "confirmez la mise à jour ?"
        answer_1  = messagebox.askokcancel(ask_title, ask_text)
        if answer_1:
            (employees_year,
             files_number_error,
             sheet_name_error,
             column_error,
             years2add_error,
             all_years_file_error) = update_employees(bibliometer_path)
            if not any(files_number_error, sheet_name_error, column_error,
                        years2add_error, all_years_file_error):
                info_title = "- Information -"
                info_text  = f"La mise à jour des effectifs a été effectuée pour l'année {employees_year}."
                info_text += f"\nLe croisement pour l'année {year_select} va être poursuivi."
                messagebox.showinfo(info_title, info_text)
                update_status = True
            elif all_years_file_error:
                info_title = "- Information -"
                info_text  = f"La mise à jour des effectifs a été effectuée pour l'année {employees_year}."
                info_text += f"\nMais le fichier des effectifs consolidés '{effectifs_file_name_alias}' "
                info_text += "non disponible a été créé dans le dossier :"
                info_text += f"\n '{effectifs_folder_path}'.\n"
                info_text += "\nErreur précise retournée :"
                info_text += f"\n '{all_years_file_error}'.\n"
                info_text += f"\nLe croisement pour l'année {year_select} va être poursuivi."
                messagebox.showinfo(info_title, info_text)
                update_status = True
            else:
                warning_title = "!!! ATTENTION : Erreurs dans les fichiers des effectifs !!!"
                if files_number_error:
                    warning_text  = "Absence de fichier ou plus d'un fichier présent dans le dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'."
                    warning_text += "\n\nNe conservez que le fichier utile et relancer la mise à jour,"
                    warning_text += "\n\nou bien relancez le traitement sans mise à jour des effectifs."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                if sheet_name_error:
                    warning_text  = "Un nom de feuille du fichier des effectifs additionnels est de format incorrect "
                    warning_text += "dans le fichier des effectifs additionnels du dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'.\n"
                    warning_text += "\nErreur précise retournée :\n"
                    warning_text += f"\n '{sheet_name_error}'.\n"
                    warning_text += "\n 1- Ouvrez le fichier;"
                    warning_text += "\n 2- Vérifiez et corrigez les noms des feuilles dans ce fichier;"
                    warning_text += "\n 3- Sauvegardez le ficher;"
                    warning_text += "\n 4- Relancez la mise à jour des effectifs (via le croisement auteurs-effectifs)."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                if column_error:
                    warning_text  = "Une colonne est manquante ou mal nommée dans une feuille "
                    warning_text += "dans le fichier des effectifs additionnels du dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'.\n"
                    warning_text += "\nErreur précise retournée :\n"
                    warning_text += f"\n '{column_error}'.\n"
                    warning_text += "\n 1- Ouvrez le fichier;"
                    warning_text += "\n 2- Vérifiez et corrigez les noms des colonnes des feuilles dans ce fichier;"
                    warning_text += "\n 3- Sauvegardez le ficher."
                    warning_text += "\n 4- Relancez la mise à jour des effectifs (via le croisement auteurs-effectifs)."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                if years2add_error:
                    warning_text  = "Le fichier des effectifs additionnels couvre plusieurs années "
                    warning_text += "dans le fichier des effectifs additionnels du dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'.\n"
                    warning_text += "\n 1- Séparez les feuilles d'années différentes en fichiers d'effectifs additionnels différents;"
                    warning_text += "\n 2- Relancer la mise à jour des effectifs (via le croisement auteurs-effectifs) "
                    warning_text += "\n    pour chacun des fichiers créés en les positionant seul dans le dossier successivement."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
        else:
            # Cancel employees database update
            warning_title = "- Information -"
            warning_text  = "La mise à jour des effectifs est abandonnée."
            warning_text += f"\n\nSi le croisement auteurs-effectifs pour l'année {year_select} "
            warning_text += "est confirmé, il se fera sans cette mise à jour."
            messagebox.showwarning(warning_title, warning_text)
            update_status = False
    return update_status


def _launch_recursive_year_search_try(year_select,
                                      search_depth_init,
                                      institute,
                                      org_tup,
                                      bibliometer_path,
                                      bdd_mensuelle_path,
                                      submit_path,
                                      all_effectifs_path,
                                      employees_update_status,
                                      orphan_alias,
                                  ):
    """
    """

    def _recursive_year_search_try():
        dedup_parsing_status = check_dedup_parsing_available(bibliometer_path, year_select)
        if dedup_parsing_status:
            end_message, orphan_status = recursive_year_search(bdd_mensuelle_path,
                                                               all_effectifs_df,
                                                               institute,
                                                               org_tup,
                                                               bibliometer_path,
                                                               year_select,
                                                               search_depth)
            print('\n',end_message)
            info_title = '- Information -'
            info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} a été effectué."
            if orphan_status:
                info_text += "\n\nTous les auteurs de l'Institut ont été identifiés dans les effectifs."
                info_text += "\n\nLa résolution des homonymes peut être lancée."
            else:
                info_text += "\n\nMais, des auteurs affiiés à l'Institut n'ont pas été identifiés dans les effectifs."
                info_text += f"\n1- Ouvrez le fichier {orphan_alias} du dossier :\n  {bdd_mensuelle_path} ;"
                info_text += "\n\n2- Suivez le mode opératoire disponible pour son utilisation ;"
                info_text += "\n3- Puis relancez le croisement pour cette année."
                info_text += "\n\nNéanmoins, la résolution des homonymes peut être lancée sans cette opération, "
                info_text += "mais la liste consolidée des publications sera incomplète."
            messagebox.showinfo(info_title, info_text)

        else:
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = f"La synthèse de l'année {year_select} n'est pas disponible."
            warning_text += "\n1- Revenez à l'onglet 'Analyse élémentaire des corpus' ;"
            warning_text += "\n2- Effectuez la synthèse pour cette année ;"
            warning_text += "\n3- Puis relancez le croisement pour cette année."
            messagebox.showwarning(warning_title, warning_text)

    # Adapting search depth to available years for search
    all_effectifs_df, search_depth, annees_disponibles = _annee_croisement(year_select, all_effectifs_path, search_depth_init)
    if annees_disponibles:
        status = "sans"
        if employees_update_status:
            status = "avec"
        ask_title = "- Confirmation du croisement auteurs-effectifs -"
        ask_text  = "Le croisement avec les effectifs des années "
        ask_text += f"{', '.join([str(i) for i in annees_disponibles])} "
        ask_text += f"a été lancé pour l'année {year_select}."
        ask_text += f"\nCe croisement se fera {status} la mise à jour "
        ask_text += "du fichier des effectifs."
        ask_text += "\n\nCette opération peut prendre quelques minutes."
        ask_text += "\nDans l'attente, ne pas fermer 'BiblioMeter'."
        ask_text += "\n\nContinuer ?"
        answer    = messagebox.askokcancel(ask_title, ask_text)
        if answer:
            submit_status = os.path.exists(submit_path)
            if not submit_status:
                _recursive_year_search_try()
            else:
                ask_title = "- Reconstruction du croisement auteurs-effectifs -"
                ask_text  = f"Le croisement pour l'année {year_select} est déjà disponible."
                ask_text += "\n\nReconstruire le croisement ?"
                answer_4  = messagebox.askokcancel(ask_title, ask_text)
                if answer_4:
                    _recursive_year_search_try()
                else:
                    info_title = "- Information -"
                    info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} "
                    info_text += "dejà disponible est conservé."
                    messagebox.showinfo(info_title, info_text)
        else:
            info_title = "- Information -"
            info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} "
            info_text += "est annulé."
            messagebox.showinfo(info_title, info_text)


def _annee_croisement(corpus_year, all_effectifs_path, search_depth):
    """
    """
    # Getting employees df
    useful_col_list = list(eg.EMPLOYEES_USEFUL_COLS.values()) + list(eg.EMPLOYEES_ADD_COLS.values())
    all_effectifs_df = pd.read_excel(all_effectifs_path,
                                     sheet_name = None,
                                     dtype = eg.EMPLOYEES_COL_TYPES,
                                     usecols = useful_col_list)

    # Identifying available years in employees df
    annees_dispo = [int(x) for x in list(all_effectifs_df.keys())]
    annees_a_verifier = [int(corpus_year) - int(search_depth) + (i+1) for i in range(int(search_depth))]
    annees_verifiees = []
    for i in annees_a_verifier:
        if i in annees_dispo:
            annees_verifiees.append(i)

    if len(annees_verifiees) > 0:
        search_depth = min(int(search_depth), len(annees_verifiees))
    else:
        search_depth = 0
        warning_title = "!!! Attention !!!"
        warning_text  = "Le nombre d'années disponibles est insuffisant "
        warning_text += "dans le fichier des effectifs de l'Institut."
        warning_text += "\nLe croisement auteurs-effectifs ne peut être effectué !"
        warning_text += "\n1- Complétez le fichier des effectifs de l'Institut ;"
        warning_text += "\n2- Puis relancer le croisement auteurs-effectifs."
        messagebox.showwarning(warning_title, warning_text)
    return (all_effectifs_df, search_depth, annees_verifiees)


def _launch_resolution_homonymies_try(institute,
                                      org_tup,
                                      bibliometer_path,
                                      submit_path,
                                      homonymes_path,
                                      homonymes_file_path,
                                      homonymes_file_alias,
                                      year_select):
    """
    """

    def _resolution_homonymies_try():
        if os.path.isfile(submit_path):
            end_message, actual_homonym_status = solving_homonyms(institute, org_tup, submit_path, homonymes_file_path)
            print(end_message)
            print('\n Actual homonyms status before setting saved homonyms:', actual_homonym_status)
            if actual_homonym_status:
                end_message, actual_homonym_status = set_saved_homonyms(institute, org_tup, bibliometer_path,
                                                                        year_select, actual_homonym_status)
            print('\n',end_message)
            print('\n Actual homonyms status after setting saved homonyms:', actual_homonym_status)
            info_title = "- Information -"
            info_text  = f"Le fichier pour la résolution des homonymies de l'année {year_select} a été créé "
            info_text += f"dans le dossier :\n\n  '{homonymes_path}' "
            info_text += f"\n\nsous le nom :  '{homonymes_file_alias}'."
            if actual_homonym_status:
                info_text += "\n\nDes homonymes existent parmi les auteurs dans les effectifs."
                info_text += "\n\n1- Ouvrez ce fichier, "
                info_text += "\n2- Supprimez manuellement les lignes des homonymes non-auteurs, "
                info_text += "\n3- Puis sauvegardez le fichier sous le même nom."
                info_text += "\n\nDès que le fichier est traité, "
                info_text += "\nl'affectation des OTPs peut être lancée."
            else:
                info_text += "\n\nAucun homonyme n'est trouvé parmi les auteurs dans les effectifs."
                info_text += "\n\nL'affectation des OTPs peut être lancée."
            messagebox.showinfo(info_title, info_text)

        else:
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = "Le fichier contenant le croisement auteurs-effectifs "
            warning_text += f"de l'année {year_select} n'est pas disponible."
            warning_text += "\n1- Effectuez d'abord le croisement pour cette année."
            warning_text += "\n2- Puis relancez la résolution des homonymies pour cette année."
            messagebox.showwarning(warning_title, warning_text)

    ask_title = "- Confirmation de l'étape de résolution des homonymies -"
    ask_text  = "La création du fichier pour cette résolution "
    ask_text += "a été lancée pour l'année {year_select}."
    ask_text += "\n\nContinuer ?"
    answer    = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        homonymes_status = os.path.exists(homonymes_file_path)
        if not homonymes_status:
            _resolution_homonymies_try()
        else:
            ask_title = "- Reconstruction de la résolution des homonymes -"
            ask_text  = "Le fichier pour la résolution des homonymies "
            ask_text += f"de l'année {year_select} est déjà disponible."
            ask_text += "\n\nReconstruire ce fichier ?"
            answer_1  = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:
                _resolution_homonymies_try()
            else:
                info_title = "- Information -"
                info_text  = "Le fichier pour la résolution des homonymies "
                info_text += f"de l'année {year_select} dejà disponible est conservé."
                messagebox.showinfo(info_title, info_text)
    else:
        info_title = "- Information -"
        info_text = "La création du fichier pour la résolution "
        info_text += f"des homonymies de l'année {year_select} est annulée."
        messagebox.showinfo(info_title, info_text)


def _launch_add_otp_try(institute,
                        org_tup,
                        bibliometer_path,
                        homonymes_file_path,
                        otp_path,
                        otp_file_base_alias,
                        year_select):
    """
    """
    def _add_otp_try():
        if os.path.isfile(homonymes_file_path):
            end_message = save_homonyms(institute, org_tup, bibliometer_path, year_select)
            print('\n',end_message)
            end_message = add_otp(institute, org_tup, homonymes_file_path, otp_path, otp_file_base_alias)
            print(end_message)
            end_message = set_saved_otps(institute, org_tup, bibliometer_path, year_select)
            print(end_message)
            info_title = "- Information -"
            info_text  = f"Les fichiers de l'année {year_select} pour l'attribution des OTPs "
            info_text += f"ont été créés dans le dossier : \n\n'{otp_path}' "
            info_text += "\n\n1- Ouvrez le fichier du département ad-hoc, "
            info_text += "\n2- Attribuez manuellement à chacune des publications un OTP, "
            info_text += "\n3- Sauvegardez le fichier en ajoutant à son nom '_ok'."
            info_text += "\n\nDès que les fichiers de tous les départements sont traités, "
            info_text += f"\nla liste consolidée des publications de l'année {year_select} peut être créée."
            messagebox.showinfo(info_title, info_text)

        else:
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = "Le fichier contenant la résolution des homonymies "
            warning_text += f"de l'année {year_select} n'est pas disponible."
            warning_text += "\n1- Effectuez la résolution des homonymies pour cette année."
            warning_text += "\n2- Relancez l'attribution des OTPs pour cette année."
            messagebox.showwarning(warning_title, warning_text)

    # Getting institute parameters
    dpt_label_list = list(org_tup[1].keys())

    ask_title = "- Confirmation de l'étape d'attribution des OTPs -"
    ask_text  = "La création des fichiers pour cette attribution "
    ask_text += f"a été lancée pour l'année {year_select}."
    ask_text += "\n\nContinuer ?"
    answer    = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        otp_path_status = os.path.exists(otp_path)
        if otp_path_status:
            otp_files_status_list = []
            for dpt_label in dpt_label_list:
                dpt_otp_file_name = otp_file_base_alias + '_' + dpt_label + '.xlsx'
                dpt_otp_file_path = otp_path / Path(dpt_otp_file_name)
                otp_files_status_list.append(not dpt_otp_file_path.is_file())
            if any(otp_files_status_list):
                _add_otp_try()
            else:
                ask_title = "- Reconstruction de l'attribution des OTPs -"
                ask_text  = "Les fichiers pour l'attribution des OTPs "
                ask_text += f"de l'année {year_select} sont déjà disponibles."
                ask_text += "\n\nReconstruire ces fichiers ?"
                answer_1  = messagebox.askokcancel(ask_title, ask_text)
                if answer_1:
                    _add_otp_try()
                else:
                    info_title = "- Information -"
                    info_text  = "Les fichiers pour l'attribution des OTPs "
                    info_text += f"de l'année {year_select} dejà disponibles sont conservés."
                    messagebox.showinfo(info_title, info_text)
        else:
            os.mkdir(otp_path)
            _add_otp_try()
    else:
        info_title = "- Information -"
        info_text = "La création des fichiers pour l'attribution des OTPs "
        info_text += f"de l'année {year_select} est annulée."
        messagebox.showinfo(info_title, info_text)


def _launch_pub_list_conso_try(institute,
                               org_tup,
                               bibliometer_path,
                               datatype,
                               otp_path,
                               pub_list_path,
                               pub_list_file_path,
                               otp_file_base_alias,
                               pub_list_file_alias,
                               year_missing_aliases,
                               bdd_multi_annuelle_folder_alias,
                               years_list,
                               year_select):
    """
    """

    def _consolidate_pub_list():
        if os.path.isdir(otp_path) and os.listdir(otp_path):
            end_message, split_ratio, if_database_complete = consolidate_pub_list(institute, org_tup,
                                                                                  bibliometer_path, datatype,
                                                                                  otp_path, pub_list_path,
                                                                                  pub_list_file_path, otp_file_base_alias,
                                                                                  year_select)
            print(end_message)
            end_message = concatenate_pub_lists(institute, org_tup, bibliometer_path, years_list)
            print('\n',end_message)
            info_title = "- Information -"
            info_text  = f"La liste consolidée des publications de l'année {year_select} "
            info_text += f"a été créée dans le dossier :\n\n '{pub_list_path}' "
            info_text += f"\n\nsous le nom :   '{pub_list_file_alias}'."
            info_text += "\n\nLes IFs disponibles ont été automatiquement attribués."
            if if_database_complete:
                info_text += "\n\nLa base de données des facteurs d'impact étant complète, "
                info_text += "les listes des journaux avec IFs ou ISSNs inconnus sont vides."
            else:
                info_text += "\n\nAttention, les listes des journaux avec IFs ou ISSNs inconnus "
                info_text += "ont été créées dans le même dossier sous les noms :"
                info_text += f"\n\n '{year_missing_aliases[0]}' "
                info_text += f"\n\n '{year_missing_aliases[1]}' "
                info_text += "\n\n Ces fichiers peuvent être modifiés pour compléter la base de donnée des IFs :"
                info_text += "\n\n1- Ouvrez chacun de ces fichiers ;"
                info_text += "\n2- Complétez manuellement les IFs inconnus ou les ISSNs et IFs inconnus, selon le fichier - "
                info_text += "\n       Attention : VIRGULE pour le séparateur décimal des IFS ;"
                info_text += "\n3- Puis sauvegardez les fichiers sous le même nom ;"
                info_text += "\n4- Pour prendre en compte ces compléments, allez à la page de mise à jour des IFs."
            info_text += f"\n\nPar ailleurs, la liste consolidée des publications a été décomposée à {split_ratio} % "
            info_text += "en trois fichiers disponibles dans le même dossier correspondant aux différentes "
            info_text += "classes de documents (les classes n'étant pas exhaustives, la décomposition peut être partielle)."
            info_text += "\n\nEnfin, la concaténation des listes consolidées des publications "
            info_text += f"disponibles, a été créée dans le dossier :\n\n '{bdd_multi_annuelle_folder_alias}' "
            info_text += "\n\nsous un nom vous identifiant ainsi que la liste des années prises en compte "
            info_text += "et caractérisé par la date et l'heure de la création."
            messagebox.showinfo(info_title, info_text)

        else:
            warning_title = "!!! ATTENTION : fichiers manquants !!!"
            warning_text  = "Les fichiers d'attribution des OTPs "
            warning_text += f"de l'année {year_select} ne sont pas disponibles."
            warning_text += "\n1- Effectuez l'attribution des OTPs pour cette année."
            warning_text += "\n2- Relancez la consolidation de la liste des publications pour cette année."
            messagebox.showwarning(warning_title, warning_text)

    ask_title = "- Confirmation de l'étape de consolidation de la liste des publications -"
    ask_text  = "La création du fichier de la liste consolidée des publications "
    ask_text += f"a été lancée pour l'année {year_select}."
    ask_text += "\n\nContinuer ?"
    answer    = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        pub_list_status = os.path.exists(pub_list_file_path)
        if not pub_list_status:
            _consolidate_pub_list()
        else:
            ask_title = "- Reconstruction de la liste consolidée des publications -"
            ask_text  = "Le fichier de la liste consolidée des publications "
            ask_text += "de l'année {year_select} est déjà disponible."
            ask_text += "\n\nReconstruire ce fichier ?"
            answer_1  = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:
                _consolidate_pub_list()
            else:
                info_title = "- Information -"
                info_text  = "Le fichier de la liste consolidée des publications "
                info_text += f"de l'année {year_select} dejà disponible est conservé."
                messagebox.showinfo(info_title, info_text)
    else:
        info_title = "- Information -"
        info_text = "La création du fichier de la liste consolidée des publications "
        info_text += f"de l'année {year_select} est annulée."
        messagebox.showinfo(info_title, info_text)


def create_consolidate_corpus(self, master, page_name, institute, bibliometer_path, datatype):

    """
    Description : function working as a bridge between the BiblioMeter
    App and the functionalities needed for the use of the app

    Uses the following globals :
    - DIC_OUT_PARSING
    - FOLDER_NAMES

    Args: takes only self and bibliometer_path as arguments.
    self is the intense in which PageThree will be created
    bibliometer_path is a type Path, and is the path to where the folders
    organised in a very specific way are stored

    Returns:

    """

    # Internal functions
    def _etape_frame(self, num):
        '''The local function `_etape_frame` sets the 'etape' and place in the page
        using the global 'ETAPE_LABEL_TEXT_LIST' and the local variables 'etape_label_format',
        'etape_label_font', 'etape_underline', 'etape_label_pos_x' and 'etape_label_pos_y_list'.

        Args:
            num (int): The order of the 'etape' in 'ETAPE_LABEL_TEXT_LIST'.
        '''
        etape = tk.Label(self,
                         text      = gg.ETAPE_LABEL_TEXT_LIST[num],
                         justify   = etape_label_format,
                         font      = etape_label_font,
                         underline = etape_underline)
        etape.place(x = etape_label_pos_x,
                    y = etape_label_pos_y_list[num])
        return etape

    # ********************* Function start

    # Setting useful local variables for positions modification
    # numbers are reference values in mm for reference screen
    eff_etape_font_size      = font_size(gg.REF_ETAPE_FONT_SIZE,   master.width_sf_min)           #14
    eff_launch_font_size     = font_size(gg.REF_ETAPE_FONT_SIZE-1, master.width_sf_min)
    eff_select_font_size     = font_size(gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)
    eff_buttons_font_size    = font_size(gg.REF_ETAPE_FONT_SIZE-3, master.width_sf_min)

    etape_label_pos_x        = mm_to_px(gg.REF_ETAPE_POS_X_MM * master.width_sf_mm, gg.PPI)        #10
    etape_label_pos_y_list   = [mm_to_px( y * master.height_sf_mm, gg.PPI)
                                for y in gg.REF_ETAPE_POS_Y_MM_LIST]  #[40, 74, 101, 129]
    etape_button_dx          = mm_to_px(gg.REF_ETAPE_BUT_DX_MM * master.width_sf_mm, gg.PPI)       #10
    etape_button_dy          = mm_to_px(gg.REF_ETAPE_BUT_DY_MM * master.height_sf_mm, gg.PPI)      #5

    year_button_x_pos        = mm_to_px(gg.REF_YEAR_BUT_POS_X_MM * master.width_sf_mm,  gg.PPI)    #10
    year_button_y_pos        = mm_to_px(gg.REF_YEAR_BUT_POS_Y_MM * master.height_sf_mm, gg.PPI)    #26
    dy_year                  = -6

    # Setting useful aliases
    bdd_multi_annuelle_folder_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    bdd_mensuelle_alias             = pg.ARCHI_YEAR["bdd mensuelle"]
    homonymes_path_alias            = pg.ARCHI_YEAR["homonymes folder"]
    homonymes_file_base_alias       = pg.ARCHI_YEAR["homonymes file name base"]
    otp_path_alias                  = pg.ARCHI_YEAR["OTP folder"]
    otp_file_base_alias             = pg.ARCHI_YEAR["OTP file name base"]
    pub_list_path_alias             = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias        = pg.ARCHI_YEAR["pub list file name base"]
    submit_alias                    = pg.ARCHI_YEAR["submit file name"]
    orphan_alias                    = pg.ARCHI_YEAR["orphan file name"]
    year_missing_if_base_alias      = pg.ARCHI_IF["missing_if_base"]
    year_missing_issn_base_alias    = pg.ARCHI_IF["missing_issn_base"]
    listing_alias                   = eg.EMPLOYEES_ARCHI["root"]
    effectifs_folder_name_alias     = eg.EMPLOYEES_ARCHI["all_years_employees"]
    effectifs_file_name_alias       = eg.EMPLOYEES_ARCHI["employees_file_name"]
    maj_effectifs_folder_name_alias = eg.EMPLOYEES_ARCHI["complementary_employees"]

    # Setting useful paths independent from corpus year
    effectifs_root_path       = bibliometer_path / Path(listing_alias)
    effectifs_folder_path     = effectifs_root_path / Path(effectifs_folder_name_alias)
    maj_effectifs_folder_path = effectifs_root_path / Path(maj_effectifs_folder_name_alias)
    all_effectifs_path        = effectifs_folder_path / Path(effectifs_file_name_alias)

    # Getting institute parameters
    org_tup = set_org_params(institute, bibliometer_path)

    # Creating and setting widgets for page title and exit button
    set_page_title(self, master, page_name, institute)
    set_exit_button(self, master)

    # - Etapes labels
    etape_label_font   = tkFont.Font(family = gg.FONT_NAME,
                                     size = eff_etape_font_size,
                                     weight = 'bold')
    etapes_number      = len(gg.ETAPE_LABEL_TEXT_LIST)
    etape_label_format = 'left'
    etape_underline    = -1
    etapes             = [_etape_frame(self, etape_num) for etape_num in range(etapes_number)]

    ### Choix de l'année
    default_year = master.years_list[-1]
    variable_years = tk.StringVar(self)
    variable_years.set(default_year)

        # Création de l'option button des années
    self.font_OptionButton_years = tkFont.Font(family = gg.FONT_NAME,
                                               size = eff_buttons_font_size)
    self.OptionButton_years = tk.OptionMenu(self,
                                            variable_years,
                                            *master.years_list)
    self.OptionButton_years.config(font = self.font_OptionButton_years)

        # Création du label
    self.font_Label_years = tkFont.Font(family = gg.FONT_NAME,
                                        size = eff_select_font_size,
                                        weight = 'bold')
    self.Label_years = tk.Label(self,
                                text = gg.TEXT_YEAR_PI,
                                font = self.font_Label_years)
    self.Label_years.place(x = year_button_x_pos, y = year_button_y_pos)

    place_after(self.Label_years, self.OptionButton_years, dy = dy_year)

    # *********************** Etape 1 : Croisement auteurs-effectifs
    def _launch_recursive_year_search():
        """ Fonction executée par le bouton 'button_croisement'.
        """

        # Getting year selection
        year_select =  variable_years.get()

        # Setting paths dependent on year_select
        corpus_year_path = bibliometer_path / Path(year_select)
        bdd_mensuelle_path =  corpus_year_path / Path(bdd_mensuelle_alias)
        submit_path = corpus_year_path / Path(bdd_mensuelle_alias) / Path(submit_alias)

        # Getting check_effectif_status
        check_effectif_status = check_effectif_var.get()

        # Updating employees file
        employees_update_status = _launch_update_employees(bibliometer_path,
                                                           year_select,
                                                           maj_effectifs_folder_path,
                                                           effectifs_file_name_alias,
                                                           effectifs_folder_path,
                                                           check_effectif_status,
                                                           )

        if not employees_update_status :
            check_effectif_var.set(0)
            check_effectif_status = check_effectif_var.get()

        # Trying launch of recursive search for authors in employees file
        _launch_recursive_year_search_try(year_select,
                                          eg.SEARCH_DEPTH,
                                          institute,
                                          org_tup,
                                          bibliometer_path,
                                          bdd_mensuelle_path,
                                          submit_path,
                                          all_effectifs_path,
                                          employees_update_status,
                                          orphan_alias,
                                         )

    ### Définition du  bouton 'button_croisement'
    font_croisement = tkFont.Font(family = gg.FONT_NAME,
                                  size   = eff_launch_font_size)
    button_croisement = tk.Button(self,
                                  text = gg.TEXT_CROISEMENT,
                                  font = font_croisement,
                                  command = lambda: _launch_recursive_year_search())

    check_effectif_var = tk.IntVar()
    check_effectif_box = tk.Checkbutton(self,
                                        text = gg.TEXT_MAJ_EFFECTIFS,
                                        variable = check_effectif_var,
                                        onvalue = 1,
                                        offvalue = 0)

    etape_1 = etapes[0]
    place_bellow(etape_1,
                 check_effectif_box,
                 dx = etape_button_dx,
                 dy = etape_button_dy / 2)
    place_bellow(check_effectif_box,
                 button_croisement,
                 dy = etape_button_dy / 2)

    # ******************* Etape 2 : Résolution des homonymies
    def _launch_resolution_homonymies():
        """Fonction executée par le bouton 'button_homonymes'.
        """

        # Renewing year selection
        year_select = variable_years.get()

        # Setting paths and aliases dependent pn year_select
        homonymes_file_alias =  homonymes_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path = bibliometer_path / Path(year_select)
        submit_path = corpus_year_path / Path(bdd_mensuelle_alias) / Path(submit_alias)
        homonymes_path = corpus_year_path / Path(homonymes_path_alias)
        homonymes_file_path = homonymes_path / Path(homonymes_file_alias)

        # Trying launch creation of file for homonymies resolution
        _launch_resolution_homonymies_try(institute,
                                          org_tup,
                                          bibliometer_path,
                                          submit_path,
                                          homonymes_path,
                                          homonymes_file_path,
                                          homonymes_file_alias,
                                          year_select)

    ### Définition du bouton "button_homonymes"
    font_homonymes = tkFont.Font(family = gg.FONT_NAME,
                                 size   = eff_launch_font_size)
    button_homonymes = tk.Button(self,
                                     text = gg.TEXT_HOMONYMES,
                                     font = font_homonymes,
                                     command = lambda: _launch_resolution_homonymies())
    etape_2 = etapes[1]
    place_bellow(etape_2,
                 button_homonymes,
                 dx = etape_button_dx,
                 dy = etape_button_dy)

    # ******************* Etape 3 : Attribution des OTPs
    def _launch_add_otp():
        """Fonction executée par le bouton 'button_otp'.
        """

        # Renewing year selection
        year_select = variable_years.get()

        # Setting paths and aliases dependent on year_select
        homonymes_file_alias = homonymes_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path     = bibliometer_path / Path(year_select)
        homonymes_path       = corpus_year_path / Path(homonymes_path_alias)
        homonymes_file_path  = homonymes_path / Path(homonymes_file_alias)
        otp_path             = corpus_year_path / Path(otp_path_alias)

        # Trying launch creation of files for OTP attribution
        _launch_add_otp_try(institute,
                            org_tup,
                            bibliometer_path,
                            homonymes_file_path,
                            otp_path,
                            otp_file_base_alias,
                            year_select)

    ### Définition du bouton "button_OTP"
    font_otp = tkFont.Font(family = gg.FONT_NAME,
                           size   = eff_launch_font_size)
    button_otp = tk.Button(self,
                           text = gg.TEXT_OTP,
                           font = font_otp,
                           command = lambda: _launch_add_otp())
    etape_3 = etapes[2]
    place_bellow(etape_3,
                 button_otp,
                 dx = etape_button_dx,
                 dy = etape_button_dy)

    # ****************** Etape 4 : Liste consolidée des publications
    def _launch_pub_list_conso():
        """Fonction executée par le bouton 'button_finale'.
        """

        # Renewing year selection and years
        year_select = variable_years.get()

        # Setting year_select dependent paths and aliases
        year_missing_if_alias   = year_select + year_missing_if_base_alias
        year_missing_issn_alias = year_select + year_missing_issn_base_alias
        year_missing_aliases    = (year_missing_if_alias, year_missing_issn_alias)
        pub_list_file_alias     = pub_list_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path        = bibliometer_path / Path(year_select)
        otp_path                = corpus_year_path / Path(otp_path_alias)
        pub_list_path           = corpus_year_path / Path(pub_list_path_alias)
        pub_list_file_path      = pub_list_path / Path(pub_list_file_alias)

        # Trying launch creation of consolidated publications lists
        _launch_pub_list_conso_try(institute,
                                   org_tup,
                                   bibliometer_path,
                                   datatype,
                                   otp_path,
                                   pub_list_path,
                                   pub_list_file_path,
                                   otp_file_base_alias,
                                   pub_list_file_alias,
                                   year_missing_aliases,
                                   bdd_multi_annuelle_folder_alias,
                                   master.years_list,
                                   year_select)

    # Définition du bouton de création de la liste consolidée des publications
    font_finale = tkFont.Font(family = gg.FONT_NAME,
                              size   = eff_launch_font_size)
    button_finale = tk.Button(self,
                              text = gg.TEXT_PUB_CONSO,
                              font = font_finale,
                              command = lambda: _launch_pub_list_conso())

    etape_4 = etapes[3]

    place_bellow(etape_4,
                 button_finale,
                 dx = etape_button_dx,
                 dy = etape_button_dy / 2)
