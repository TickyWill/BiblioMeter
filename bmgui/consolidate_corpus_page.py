"""The `consolidate_corpus_page` module allows to built consolidated publication lists 
for the Institute selected and the data type selected. It performs the merge 
of the publications list with the employees database of the Institute. 
Then it provides xlsx files to the user for :
- Authors metadata correction when not found in the employees database;
- Homonymies resolution;
- Publications OTPs setting;
- Completion of impact-factors database.
Finally it saves the consolidated publications list in a dedicated directory.
"""
__all__ = ['create_consolidate_corpus']


# Standard library imports
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import ttk

# 3rd party imports
import pandas as pd

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg
import bmgui.gui_globals as gg
from bmfuncts.config_utils import set_org_params
from bmfuncts.consolidate_pub_list import add_otp
from bmfuncts.consolidate_pub_list import built_final_pub_list
from bmfuncts.consolidate_pub_list import concatenate_pub_lists
from bmfuncts.consolidate_pub_list import solving_homonyms
from bmfuncts.merge_pub_employees import recursive_year_search
from bmfuncts.update_employees import update_employees
from bmfuncts.use_pub_attributes import save_homonyms
from bmfuncts.use_pub_attributes import set_saved_homonyms
from bmfuncts.use_pub_attributes import set_saved_otps
from bmfuncts.useful_functs import check_dedup_parsing_available
from bmgui.gui_utils import disable_buttons
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import font_size
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_exit_button
from bmgui.gui_utils import set_page_title


def _set_employees_data(corpus_year, all_effectifs_path, search_depth):
    """Sets Intitute employees data   
    through `update_employees` function imported from 
    `bmfuncts.update_employees` module after check 
    of available files for update (should be single) 
    and check of Institute employees database file.

    Args:
        all_effectifs_path (path): Full path to file of Institute employees database.
        corpus_year (str): Corpus year defined by 4 digits.
        search_depth (int): Initial search depth.
        progress_callback (function): Function for updating 
                                      ProgressBar tkinter widget status.

    Returns:
        (tup): Tuple = (employees data (df), adapted search depth (int), 
                        list of available years of employees data).    
    """

    # Getting employees df
    useful_col_list = list(eg.EMPLOYEES_USEFUL_COLS.values()) + list(eg.EMPLOYEES_ADD_COLS.values())
    all_effectifs_df = pd.read_excel(all_effectifs_path,
                                     sheet_name = None,
                                     dtype = eg.EMPLOYEES_COL_TYPES,
                                     usecols = useful_col_list)

    # Identifying available years in employees df
    annees_dispo = [int(x) for x in list(all_effectifs_df.keys())]
    annees_a_verifier = [int(corpus_year) - int(search_depth)
                         + (i+1) for i in range(int(search_depth))]
    annees_verifiees = []
    for i in annees_a_verifier:
        if i in annees_dispo:
            annees_verifiees.append(i)

    if len(annees_verifiees) > 0:
        search_depth = min(int(search_depth), len(annees_verifiees))
    else:
        search_depth = 0
        warning_title = "!!! Attention !!!"
        warning_text  = ("Le nombre d'années disponibles est insuffisant "
                         "dans le fichier des effectifs de l'Institut."
                         "\nLe croisement auteurs-effectifs ne peut être effectué !"
                         "\n1- Complétez le fichier des effectifs de l'Institut ;"
                         "\n2- Puis relancer le croisement auteurs-effectifs.")
        messagebox.showwarning(warning_title, warning_text)
    return (all_effectifs_df, search_depth, annees_verifiees)


def _launch_update_employees(bibliometer_path,
                             paths_tup,
                             effectifs_file_name,
                             year_select,
                             check_effectif_status,
                             progress_callback):
    """Launches update of Intitute employees database   
    through `update_employees` function imported from 
    `bmfuncts.update_employees` module after check 
    of available files for update (should be single) 
    and check of Institute employees database file.

    Args:
        bibliometer_path (path): Full path to working folder.
        paths_tup (tup): Tuple = (full path to folder where file for update 
                                  of Institute employeees database,
                                  full path to file of Institute employees database).
        effectifs_file_name (str): Name of file of Institute employees database.
        year_select (str): Corpus year defined by 4 digits.
        check_effectif_status (int): Value for updating 
                                     Institute employees database '0: no update; 1: update'.
        progress_callback (function): Function for updating 
                                      ProgressBar tkinter widget status.

    Returns:
        None.    
    """

    # Setting parameters from args
    maj_effectifs_folder_path, effectifs_folder_path = paths_tup

    # Setting dialogs and checking answers
    # for ad-hoc use of 'update_employees' function    
    update_status = False
    if check_effectif_status:
        # Launch employees database update
        ask_title = "- Confirmation de la mise à jour des effectifs -"
        ask_text  = ("Le fichier des effectifs de l'Institut va être mis à jour "
                     "avec les nouvelles données disponibles dans le dossier :"
                     f"\n\n '{maj_effectifs_folder_path}'."
                     "\n\nCette opération peut prendre quelques minutes."
                     "\nDans l'attente, ne pas fermer 'BiblioMeter'."
                     "\n\nAvant de poursuivre le croisement auteurs-effectifs, "
                     "confirmez la mise à jour ?")
        answer_1  = messagebox.askokcancel(ask_title, ask_text)
        if answer_1:
            (employees_year,
             files_number_error,
             sheet_name_error,
             column_error,
             years2add_error,
             all_years_file_error) = update_employees(bibliometer_path, progress_callback)
            if not any([files_number_error, sheet_name_error, column_error,
                        years2add_error, all_years_file_error]):
                info_title = "- Information -"
                info_text  = ("La mise à jour des effectifs a été effectuée "
                              f"pour l'année {employees_year}."
                              f"\nLe croisement pour l'année {year_select} "
                              "va être poursuivi.")
                messagebox.showinfo(info_title, info_text)
                update_status = True
            elif all_years_file_error:
                info_title = "- Information -"
                info_text  = ("La mise à jour des effectifs a été effectuée "
                              f"pour l'année {employees_year}."
                              "\nMais le fichier des effectifs consolidés "
                              f"'{effectifs_file_name}' "
                              "non disponible a été créé dans le dossier :"
                              f"\n '{effectifs_folder_path}'.\n"
                              f"\nErreur précise retournée :\n '{all_years_file_error}'.\n"
                              f"\nLe croisement pour l'année {year_select} "
                              "va être poursuivi.")
                messagebox.showinfo(info_title, info_text)
                update_status = True
            else:
                warning_title = "!!! ATTENTION : Erreurs dans les fichiers des effectifs !!!"
                if files_number_error:
                    warning_text  = ("Absence de fichier ou plus d'un fichier "
                                     "présent dans le dossier :"
                                     f"\n\n '{maj_effectifs_folder_path}'."
                                     "\n\nNe conservez que le fichier utile "
                                     "et relancez la mise à jour,"
                                     "\n\nou bien relancez le traitement "
                                     "sans mise à jour des effectifs.")
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                if sheet_name_error:
                    warning_text  = ("Un nom de feuille est de format incorrect "
                                     "dans le fichier des effectifs additionnels du dossier :"
                                     f"\n\n '{maj_effectifs_folder_path}'.\n"
                                     "\nErreur précise retournée :\n"
                                     f"\n '{sheet_name_error}'.\n"
                                     "\n 1- Ouvrez le fichier;"
                                     "\n 2- Vérifiez et corrigez les noms des feuilles "
                                     "dans ce fichier;"
                                     "\n 3- Sauvegardez le ficher;"
                                     "\n 4- Relancez la mise à jour des effectifs "
                                     "(via le croisement auteurs-effectifs).")
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                if column_error:
                    warning_text  = ("Une colonne est manquante ou mal nommée dans une feuille "
                                     "dans le fichier des effectifs additionnels du dossier :"
                                     f"\n\n '{maj_effectifs_folder_path}'.\n"
                                     "\nErreur précise retournée :\n"
                                     f"\n '{column_error}'.\n"
                                     "\n 1- Ouvrez le fichier;"
                                     "\n 2- Vérifiez et corrigez les noms des colonnes "
                                     "des feuilles dans ce fichier;"
                                     "\n 3- Sauvegardez le ficher."
                                     "\n 4- Relancez la mise à jour des effectifs "
                                     "(via le croisement auteurs-effectifs).")
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                if years2add_error:
                    warning_text  = ("Le fichier des effectifs additionnels "
                                     "couvre plusieurs années "
                                     "dans le fichier des effectifs additionnels du dossier :"
                                     f"\n\n '{maj_effectifs_folder_path}'.\n"
                                     "\n 1- Séparez les feuilles d'années différentes "
                                     "en fichiers d'effectifs additionnels différents;"
                                     "\n 2- Relancer la mise à jour des effectifs "
                                     "(via le croisement auteurs-effectifs) "
                                     "\n    pour chacun des fichiers créés en les positionant seul "
                                     "dans le dossier successivement.")
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
        else:
            # Cancel employees database update
            warning_title = "- Information -"
            warning_text  = ("La mise à jour des effectifs est abandonnée."
                             f"\n\nSi le croisement auteurs-effectifs pour l'année {year_select} "
                             "est confirmé, il se fera sans cette mise à jour.")
            messagebox.showwarning(warning_title, warning_text)
            update_status = False
    return update_status


def _launch_recursive_year_search_try(institute, org_tup,
                                      bibliometer_path,
                                      paths_tup,
                                      files_tup,
                                      year_select,
                                      search_depth_init,
                                      employees_update_status,
                                      progress_callback,
                                      progress_bar_state):
    """Launches merge of publications list with Institute employees  
    through `recursive_year_search` function imported from 
    `bmfuncts.merge_pub_employees` module after setting employees data 
    through `_set_employees_data` function and check of status of parsing step 
    through `check_dedup_parsing_available` function imported from 
    `bmfuncts.useful_functs` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        paths_tup (tup): Tuple = (full path to folder where publications  
                         merged with Institute employees and associated 
                         files are saved, full path to file of Institute 
                         employees database).
        files_tup (tup): Tuple = (name of file of publications merged 
                         with Institut employees, name of file of publications
                         with authors not found in Institute employees database).
        year_select (str): Corpus year defined by 4 digits.
        search_depth_init (int): Initial search depth that will be adapted depending 
                                 on available years in Institute employees database.
        progress_callback (function): Function for updating 
                                      ProgressBar tkinter widget status.
        progress_bar_state (int): Initial status of ProgressBar tkinter widget.

    Returns:
        None.    
    """

    def _recursive_year_search_try(progress_callback):
        dedup_parsing_status = check_dedup_parsing_available(bibliometer_path, year_select)
        if dedup_parsing_status:
            end_message, orphan_status = recursive_year_search(bdd_mensuelle_path,
                                                               all_effectifs_df,
                                                               institute,
                                                               org_tup,
                                                               bibliometer_path,
                                                               year_select,
                                                               search_depth,
                                                               progress_callback,
                                                               progress_bar_state)
            print('\n',end_message)
            info_title = '- Information -'
            info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} a été effectué."
            if orphan_status:
                info_text += ("\n\nTous les auteurs de l'Institut ont été "
                              "identifiés dans les effectifs."
                              "\n\nLa résolution des homonymes peut être lancée.")
            else:
                info_text += ("\n\nMais, des auteurs affiiés à l'Institut "
                              "n'ont pas été identifiés dans les effectifs."
                              f"\n1- Ouvrez le fichier {orphan_file} "
                              f"du dossier :\n  {bdd_mensuelle_path} ;"
                              "\n\n2- Suivez le mode opératoire disponible pour son utilisation ;"
                              "\n3- Puis relancez le croisement pour cette année."
                              "\n\nNéanmoins, la résolution des homonymes "
                              "peut être lancée sans cette opération, "
                              "mais la liste consolidée des publications sera incomplète.")
            messagebox.showinfo(info_title, info_text)

        else:
            progress_callback(100)
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = (f"La synthèse de l'année {year_select} n'est pas disponible."
                             "\n1- Revenez à l'onglet 'Analyse élémentaire des corpus' ;"
                             "\n2- Effectuez la synthèse pour cette année ;"
                             "\n3- Puis relancez le croisement pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting parameters from args
    bdd_mensuelle_path, all_effectifs_path = paths_tup
    submit_file, orphan_file = files_tup
    submit_path = bdd_mensuelle_path / Path(submit_file)

    # Setting dialogs and checking answers
    # for ad-hoc use of '_recursive_year_search_try' internal function    
    # after adapting search depth to available years for search
    tup = _set_employees_data(year_select, all_effectifs_path, search_depth_init)
    all_effectifs_df, search_depth, annees_disponibles = tup[0], tup[1], tup[2]
    if annees_disponibles:
        status = "sans"
        if employees_update_status:
            status = "avec"
        ask_title = "- Confirmation du croisement auteurs-effectifs -"
        ask_text  = ("Le croisement avec les effectifs des années "
                     f"{', '.join([str(i) for i in annees_disponibles])} "
                     f"a été lancé pour l'année {year_select}."
                     f"\nCe croisement se fera {status} la mise à jour "
                     "du fichier des effectifs."
                     "\n\nCette opération peut prendre quelques minutes."
                     "\nDans l'attente, ne pas fermer 'BiblioMeter'."
                     "\n\nContinuer ?")
        answer = messagebox.askokcancel(ask_title, ask_text)
        if answer:
            submit_status = os.path.exists(submit_path)
            if not submit_status:
                _recursive_year_search_try(progress_callback)
            else:
                ask_title = "- Reconstruction du croisement auteurs-effectifs -"
                ask_text  = (f"Le croisement pour l'année {year_select} est déjà disponible."
                             "\n\nReconstruire le croisement ?")
                answer_4  = messagebox.askokcancel(ask_title, ask_text)
                if answer_4:
                    _recursive_year_search_try(progress_callback)
                else:
                    progress_callback(100)
                    info_title = "- Information -"
                    info_text  = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                                  "dejà disponible est conservé.")
                    messagebox.showinfo(info_title, info_text)
        else:
            progress_callback(100)
            info_title = "- Information -"
            info_text  = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                          "est annulé.")
            messagebox.showinfo(info_title, info_text)


def _launch_resolution_homonymies_try(institute, org_tup,
                                      bibliometer_path,
                                      paths_tup,
                                      homonymes_file,
                                      year_select,
                                      progress_callback):
    """Launches file creation for resolving homonyms 
    through `solving_homonyms` function imported from 
    `bmfuncts.consolidate_pub_list` module after check 
    of status of publications-employees merge step.
    Created file is filled with previously resolved homonyms 
    through `set_saved_homonyms` function imported from 
    `bmfuncts.use_pub_attributes` module. 

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        paths_tup (tup): Tuple = (full path to file where publications  
                         have been merged with Institute employees,  
                         full path to folder where file for resolving 
                         homonyms is saved).
        homonymes_file (str): Name of file created for resolving homonyms.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating 
                                      ProgressBar tkinter widget status.

    Returns:
        None.    
    """

    def _resolution_homonymies_try(progress_callback):
        if os.path.isfile(submit_path):
            progress_callback(20)
            return_tup = solving_homonyms(institute, org_tup,
                                          submit_path, homonymes_file_path)
            end_message, actual_homonym_status = return_tup
            print(end_message)
            print('\n Actual homonyms status before setting saved homonyms:',
                  actual_homonym_status)
            progress_callback(80)
            if actual_homonym_status:
                end_message, actual_homonym_status = set_saved_homonyms(institute, org_tup,
                                                                        bibliometer_path,
                                                                        year_select,
                                                                        actual_homonym_status)
            print('\n',end_message)
            print('\n Actual homonyms status after setting saved homonyms:',
                  actual_homonym_status)
            progress_callback(100)
            info_title = "- Information -"
            info_text  = ("Le fichier pour la résolution des homonymies "
                          f"de l'année {year_select} a été créé "
                          f"dans le dossier :\n\n  '{homonymes_path}' "
                          f"\n\nsous le nom :  '{homonymes_file}'.")
            if actual_homonym_status:
                info_text += ("\n\nDes homonymes existent parmi "
                              "les auteurs dans les effectifs."
                              "\n\n1- Ouvrez ce fichier, "
                              "\n2- Supprimez manuellement les lignes "
                              "des homonymes non-auteurs, "
                              "\n3- Puis sauvegardez le fichier sous le même nom."
                              "\n\nDès que le fichier est traité, "
                              "\nl'affectation des OTPs peut être lancée.")
            else:
                info_text += ("\n\nAucun homonyme n'est trouvé parmi "
                              "les auteurs dans les effectifs."
                              "\n\nL'affectation des OTPs peut être lancée.")
            messagebox.showinfo(info_title, info_text)

        else:
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = ("Le fichier contenant le croisement auteurs-effectifs "
                             f"de l'année {year_select} n'est pas disponible."
                             "\n1- Effectuez d'abord le croisement pour cette année."
                             "\n2- Puis relancez la résolution des homonymies pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting parameters from args
    submit_path, homonymes_path = paths_tup
    homonymes_file_path = homonymes_path / Path(homonymes_file)

    # Setting dialogs and checking answers
    # for ad-hoc use of '_resolution_homonymies_try' internal function
    ask_title = "- Confirmation de l'étape de résolution des homonymies -"
    ask_text  = ("La création du fichier pour cette résolution "
                 f"a été lancée pour l'année {year_select}."
                 "\n\nContinuer ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        progress_callback(10)
        homonymes_status = os.path.exists(homonymes_file_path)
        if not homonymes_status:
            _resolution_homonymies_try(progress_callback)
        else:
            ask_title = "- Reconstruction de la résolution des homonymes -"
            ask_text  = ("Le fichier pour la résolution des homonymies "
                         f"de l'année {year_select} est déjà disponible."
                         "\n\nReconstruire ce fichier ?")
            answer_1  = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:
                _resolution_homonymies_try(progress_callback)
            else:
                progress_callback(100)
                info_title = "- Information -"
                info_text  = ("Le fichier pour la résolution des homonymies "
                              f"de l'année {year_select} dejà disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("La création du fichier pour la résolution "
                     f"des homonymies de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def _launch_add_otp_try(institute, org_tup,
                        bibliometer_path,
                        paths_tup,
                        files_tup,
                        year_select,
                        progress_callback):
    """Launches files creation for adding OTP attribute to publications 
    through `add_otp` function imported from `bmfuncts.consolidate_pub_list` 
    module after check of status of homonyms resolution step 
    and saving the resolved homonyms through `save_homonyms` function 
    imported from `bmfuncts.use_pub_attributes` module.
    Created files are filled with previously set OTPs through `set_saved_otps` 
    function imported from `bmfuncts.use_pub_attributes` module. 

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        homonymes_file_path (path): Full path to file where homonyms 
                                    have been resolved.
        otp_path (path): Full path to folder where created files are saved.
        otp_file_base (str): Base for building created-files names.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating 
                                      ProgressBar tkinter widget status. 

    Returns:
        None.    
    """

    def _add_otp_try(progress_callback):
        if os.path.isfile(homonymes_file_path):
            progress_callback(15)
            end_message = save_homonyms(institute, org_tup, bibliometer_path, year_select)
            print('\n',end_message)
            progress_callback(20)
            end_message = add_otp(institute, org_tup, homonymes_file_path,
                                  otp_path, otp_file_base)
            print(end_message)
            progress_callback(80)
            end_message = set_saved_otps(institute, org_tup, bibliometer_path, year_select)
            print(end_message)
            progress_callback(100)
            info_title = "- Information -"
            info_text  = (f"Les fichiers de l'année {year_select} pour l'attribution des OTPs "
                          f"ont été créés dans le dossier : \n\n'{otp_path}' "
                          "\n\n1- Ouvrez le fichier du département ad-hoc, "
                          "\n2- Attribuez manuellement à chacune des publications un OTP, "
                          "\n3- Sauvegardez le fichier en ajoutant à son nom '_ok'."
                          "\n\nDès que les fichiers de tous les départements "
                          "sont traités, la liste consolidée des publications "
                          f"de l'année {year_select} peut être créée.")
            messagebox.showinfo(info_title, info_text)
        else:
            progress_callback(100)
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = ("Le fichier contenant la résolution des homonymies "
                             f"de l'année {year_select} n'est pas disponible."
                             "\n1- Effectuez la résolution des homonymies pour cette année."
                             "\n2- Relancez l'attribution des OTPs pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting parameters from args
    homonymes_path, otp_path = paths_tup
    homonymes_file, otp_file_base = files_tup
    homonymes_file_path = homonymes_path / Path(homonymes_file)

    # Getting institute parameters
    dpt_label_list = list(org_tup[1].keys())

    # Setting dialogs and checking answers
    # for ad-hoc use of '_add_otp_try' internal function
    ask_title = "- Confirmation de l'étape d'attribution des OTPs -"
    ask_text  = ("La création des fichiers pour cette attribution "
                 f"a été lancée pour l'année {year_select}."
                 "\n\nContinuer ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        progress_callback(10)
        otp_path_status = os.path.exists(otp_path)
        if otp_path_status:
            otp_files_status_list = []
            for dpt_label in dpt_label_list:
                dpt_otp_file_name = otp_file_base + '_' + dpt_label + '.xlsx'
                dpt_otp_file_path = otp_path / Path(dpt_otp_file_name)
                otp_files_status_list.append(not dpt_otp_file_path.is_file())
            if any(otp_files_status_list):
                _add_otp_try(progress_callback)
            else:
                ask_title = "- Reconstruction de l'attribution des OTPs -"
                ask_text  = ("Les fichiers pour l'attribution des OTPs "
                             f"de l'année {year_select} sont déjà disponibles."
                             "\n\nReconstruire ces fichiers ?")
                answer_1  = messagebox.askokcancel(ask_title, ask_text)
                if answer_1:
                    _add_otp_try(progress_callback)
                else:
                    progress_callback(100)
                    info_title = "- Information -"
                    info_text  = ("Les fichiers pour l'attribution des OTPs "
                                  f"de l'année {year_select} dejà disponibles sont conservés.")
                    messagebox.showinfo(info_title, info_text)
        else:
            os.mkdir(otp_path)
            _add_otp_try(progress_callback)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("La création des fichiers pour l'attribution des OTPs "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def _launch_pub_list_conso_try(institute, org_tup,
                               bibliometer_path, datatype,
                               paths_tup, aliases_tup,
                               year_select, years_list,
                               progress_callback):
    """Launches building of publications final list through `built_final_pub_list` 
    function imported from `bmfuncts.consolidate_pub_list` module 
    after check of status of OTPs adding step.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        paths_tup (tup): Tuple = (full path to folder of files where OTPs 
                         have been attributed, full path to folder where 
                         file of publications final list and associated files are saved).
        aliases_tup (tup): Tuple = (base for building names of OTPs files, 
                           publications-list file name,
                           [name of missing-IFs file, name of missing-ISSNs file], 
                           name of folder where concatenated list of available 
                           publications lists are saved).
        year_select (str): Corpus year defined by 4 digits.
        years_list (list): List of available corpus years 
                           (each item defined by a string of 4 digits).
        progress_callback (function): Function for updating 
                                      ProgressBar tkinter widget status. 

    Returns:
        None.    
    """

    def _consolidate_pub_list(progress_callback):
        if os.path.isdir(otp_path) and os.listdir(otp_path):
            progress_callback(20)
            conso_tup = built_final_pub_list(institute, org_tup,
                                             bibliometer_path, datatype,
                                             otp_path, pub_list_path,
                                             pub_list_file_path, otp_file_base,
                                             year_select)
            end_message, split_ratio, if_database_complete = (conso_tup[0], conso_tup[1],
                                                              conso_tup[2])
            print(end_message)
            progress_callback(50)
            end_message = concatenate_pub_lists(institute, org_tup, bibliometer_path, years_list)
            print('\n',end_message)
            progress_callback(100)
            info_title = "- Information -"
            info_text  = (f"La liste consolidée des publications de l'année {year_select} "
                          f"a été créée dans le dossier :\n\n '{pub_list_path}' "
                          f"\n\nsous le nom :   '{pub_list_file}'."
                          "\n\nLes IFs disponibles ont été automatiquement attribués.")
            if if_database_complete:
                info_text += ("\n\nLa base de données des facteurs d'impact étant complète, "
                              "les listes des journaux avec IFs ou ISSNs inconnus sont vides.")
            else:
                info_text += ("\n\nAttention, les listes des journaux avec IFs ou ISSNs inconnus "
                              "ont été créées dans le même dossier sous les noms :"
                              f"\n\n '{year_missing_aliases[0]}' "
                              f"\n\n '{year_missing_aliases[1]}' "
                              "\n\n Ces fichiers peuvent être modifiés pour compléter "
                              "la base de donnée des IFs :"
                              "\n\n1- Ouvrez chacun de ces fichiers ;"
                              "\n2- Complétez manuellement les IFs inconnus ou les ISSNs "
                              "et IFs inconnus, selon le fichier - "
                              "\n       Attention : VIRGULE pour le séparateur décimal des IFS ;"
                              "\n3- Puis sauvegardez les fichiers sous le même nom ;"
                              "\n4- Pour prendre en compte ces compléments, allez à la page "
                              "de mise à jour des IFs.")
            info_text += ("\n\nPar ailleurs, la liste consolidée des publications "
                          f"a été décomposée à {split_ratio} % "
                          "en trois fichiers disponibles dans le même dossier "
                          "correspondant aux différentes "
                          "classes de documents (les classes n'étant pas exhaustives, "
                          "la décomposition peut être partielle)."
                          "\n\nLa liste des publications invalides a été créée dans le même dossier."
                          "\n\nEnfin, la concaténation des listes consolidées des publications "
                          "disponibles, a été créée dans le dossier :"
                          f"\n\n '{bdd_multi_annuelle_folder}' "
                          "\n\nsous un nom vous identifiant ainsi que la liste des années "
                          "prises en compte et caractérisé par la date et l'heure de la création.")
            messagebox.showinfo(info_title, info_text)

        else:
            progress_callback(100)
            warning_title = "!!! ATTENTION : fichiers manquants !!!"
            warning_text  = ("Les fichiers d'attribution des OTPs "
                             f"de l'année {year_select} ne sont pas disponibles."
                             "\n1- Effectuez l'attribution des OTPs pour cette année."
                             "\n2- Relancez la consolidation de la liste des publications "
                             "pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting parameters from args
    otp_path, pub_list_path = paths_tup
    (otp_file_base, pub_list_file,
     year_missing_aliases, bdd_multi_annuelle_folder) = aliases_tup
    pub_list_file_path = pub_list_path / Path(pub_list_file)
    
    # Setting dialogs and checking answers
    # for ad-hoc use of '_consolidate_pub_list' internal function
    ask_title = "- Confirmation de l'étape de consolidation de la liste des publications -"
    ask_text  = ("La création du fichier de la liste consolidée des publications "
                 f"a été lancée pour l'année {year_select}."
                 "\n\nContinuer ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        progress_callback(10)
        pub_list_status = os.path.exists(pub_list_file_path)
        if not pub_list_status:
            _consolidate_pub_list(progress_callback)
        else:
            ask_title = "- Reconstruction de la liste consolidée des publications -"
            ask_text  = ("Le fichier de la liste consolidée des publications "
                         f"de l'année {year_select} est déjà disponible."
                         "\n\nReconstruire ce fichier ?")
            answer_1 = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:
                _consolidate_pub_list(progress_callback)
            else:
                progress_callback(100)
                info_title = "- Information -"
                info_text  = ("Le fichier de la liste consolidée des publications "
                              f"de l'année {year_select} dejà disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("La création du fichier de la liste consolidée des publications "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def create_consolidate_corpus(self, master, page_name, institute, bibliometer_path, datatype):
    """Manages creation and use of widgets for corpus consolidation 
    through merge with Institute employees database.

    Args:
        self (instense): Instense where consolidation page will be created.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of consolidation page.
        institute (str): Institute name.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases. 

    Returns:
        None.
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

    def _update_progress(value):
        progress_var.set(value)
        progress_bar.update_idletasks()
        if value >= 100:
            enable_buttons(consolidate_corpus_buttons_list)

    def _except_hook(args):
        messagebox.showwarning("Error", args)
        progress_var.set(0)
        enable_buttons(consolidate_corpus_buttons_list)

    # ********************* Function start

    # Setting useful local variables for positions modification
    # numbers are reference values in mm for reference screen
    eff_etape_font_size = font_size(gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)
    eff_launch_font_size = font_size(gg.REF_ETAPE_FONT_SIZE-1, master.width_sf_min)
    eff_select_font_size = font_size(gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)
    eff_buttons_font_size = font_size(gg.REF_ETAPE_FONT_SIZE-3, master.width_sf_min)    
    progress_bar_length_px = mm_to_px(100 * master.width_sf_mm, gg.PPI)
    progress_bar_dx = 40
    etape_label_pos_x = mm_to_px(gg.REF_ETAPE_POS_X_MM * master.width_sf_mm,
                                 gg.PPI)
    etape_label_pos_y_list = [mm_to_px( y * master.height_sf_mm, gg.PPI)
                              for y in gg.REF_ETAPE_POS_Y_MM_LIST]
    etape_button_dx = mm_to_px(gg.REF_ETAPE_BUT_DX_MM * master.width_sf_mm,
                               gg.PPI)
    etape_button_dy = mm_to_px(gg.REF_ETAPE_BUT_DY_MM * master.height_sf_mm,
                               gg.PPI)
    year_button_x_pos = mm_to_px(gg.REF_YEAR_BUT_POS_X_MM * master.width_sf_mm,
                                 gg.PPI)
    year_button_y_pos = mm_to_px(gg.REF_YEAR_BUT_POS_Y_MM * master.height_sf_mm,
                                 gg.PPI)
    dy_year = -6

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
    set_page_title(self, master, page_name, institute, datatype)
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
    
    # Handling exception
    threading.excepthook = _except_hook

    # Initializing progress bar widget
    progress_var = tk.IntVar()  # Variable to keep track of the progress bar value
    progress_bar = ttk.Progressbar(self,
                                   orient="horizontal",
                                   length=progress_bar_length_px,
                                   mode="determinate",
                                   variable=progress_var)

    # *********************** Etape 1 : Croisement auteurs-effectifs
    def _launch_recursive_year_search(progress_callback):
        """ Fonction executée par le bouton 'merge_button'.
        """

        # Getting year selection
        year_select = variable_years.get()

        # Setting paths dependent on year_select
        corpus_year_path = bibliometer_path / Path(year_select)
        bdd_mensuelle_path = corpus_year_path / Path(bdd_mensuelle_alias)
        submit_path = bdd_mensuelle_path / Path(submit_alias)

        # Getting check_effectif_status
        check_effectif_status = check_effectif_var.get()
        progress_callback(10)

        # Updating employees file
        paths_tup = maj_effectifs_folder_path, effectifs_folder_path
        employees_update_status = _launch_update_employees(bibliometer_path,
                                                           paths_tup,
                                                           effectifs_file_name_alias,
                                                           year_select,
                                                           check_effectif_status,
                                                           progress_callback)
        if not employees_update_status:
            check_effectif_var.set(0)
            check_effectif_status = check_effectif_var.get()
        progress_callback(30)
        progress_bar_state = 30

        # Trying launch of recursive search for authors in employees file
        paths_tup = (bdd_mensuelle_path, all_effectifs_path)
        files_tup = (submit_alias, orphan_alias)
        _launch_recursive_year_search_try(institute, org_tup,
                                          bibliometer_path,
                                          paths_tup,
                                          files_tup,
                                          year_select,
                                          eg.SEARCH_DEPTH,
                                          employees_update_status,
                                          progress_callback,
                                          progress_bar_state)
        progress_bar.place_forget()


    def _start_launch_recursive_year_search():
        disable_buttons(consolidate_corpus_buttons_list)
        place_after(merge_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_recursive_year_search, args=(_update_progress,)).start()

    ### Définition du bouton 'merge_button'
    merge_font = tkFont.Font(family = gg.FONT_NAME,
                             size   = eff_launch_font_size)
    merge_button = tk.Button(self,
                             text = gg.TEXT_CROISEMENT,
                             font = merge_font,
                             command = _start_launch_recursive_year_search)

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
                 merge_button,
                 dy = etape_button_dy / 2)

    # ******************* Etape 2 : Résolution des homonymies
    def _launch_resolution_homonymies(progress_callback):
        """Fonction executée par le bouton 'button_homonymes'.
        """

        # Renewing year selection
        year_select = variable_years.get()

        # Setting paths and aliases dependent pn year_select
        homonymes_file_alias =  homonymes_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path = bibliometer_path / Path(year_select)
        bdd_mensuelle_path = corpus_year_path / Path(bdd_mensuelle_alias)
        submit_path = bdd_mensuelle_path / Path(submit_alias)
        homonymes_path = corpus_year_path / Path(homonymes_path_alias)
        homonymes_file_path = homonymes_path / Path(homonymes_file_alias)

        # Trying launch creation of file for homonymies resolution
        paths_tup = (submit_path, homonymes_path)
        _launch_resolution_homonymies_try(institute,
                                          org_tup,
                                          bibliometer_path,
                                          paths_tup,
                                          homonymes_file_alias,
                                          year_select,
                                          progress_callback)        
        progress_bar.place_forget()


    def _start_launch_resolution_homonymies():
        disable_buttons(consolidate_corpus_buttons_list)
        place_after(homonyms_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_resolution_homonymies, args=(_update_progress,)).start()

    ### Définition du bouton "homonyms_button"
    homonyms_font = tkFont.Font(family = gg.FONT_NAME,
                                size   = eff_launch_font_size)
    homonyms_button = tk.Button(self,
                                text = gg.TEXT_HOMONYMES,
                                font = homonyms_font,
                                command = _start_launch_resolution_homonymies)
    etape_2 = etapes[1]
    place_bellow(etape_2,
                 homonyms_button,
                 dx = etape_button_dx,
                 dy = etape_button_dy)

    # ******************* Etape 3 : Attribution des OTPs
    def _launch_add_otp(progress_callback):
        """Fonction executée par le bouton 'otp_button'.
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
        paths_tup = (homonymes_path, otp_path)
        files_tup = (homonymes_file_alias, otp_file_base_alias)
        _launch_add_otp_try(institute, org_tup,
                            bibliometer_path,
                            paths_tup,
                            files_tup,
                            year_select,
                            progress_callback)        
        progress_bar.place_forget()


    def _start_launch_add_otp():
        disable_buttons(consolidate_corpus_buttons_list)
        place_after(otp_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_add_otp, args=(_update_progress,)).start()

    ### Définition du bouton "otp_button"
    otp_font = tkFont.Font(family = gg.FONT_NAME,
                           size   = eff_launch_font_size)
    otp_button = tk.Button(self,
                           text = gg.TEXT_OTP,
                           font = otp_font,
                           command = _start_launch_add_otp)
    etape_3 = etapes[2]
    place_bellow(etape_3,
                 otp_button,
                 dx = etape_button_dx,
                 dy = etape_button_dy)

    # ****************** Etape 4 : Liste consolidée des publications
    def _launch_pub_list_conso(progress_callback):
        """Fonction executée par le bouton 'final_button'.
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
        paths_tup = (otp_path, pub_list_path)
        aliases_tup = (otp_file_base_alias,
                       pub_list_file_alias,
                       year_missing_aliases,
                       bdd_multi_annuelle_folder_alias)
        _launch_pub_list_conso_try(institute, org_tup,
                                   bibliometer_path, datatype,
                                   paths_tup, aliases_tup,
                                   year_select, master.years_list,
                                   progress_callback)        
        progress_bar.place_forget()


    def _start_launch_pub_list_conso():
        disable_buttons(consolidate_corpus_buttons_list)
        place_after(conso_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_pub_list_conso, args=(_update_progress,)).start()

    # Définition du bouton de création de la liste consolidée des publications
    conso_font = tkFont.Font(family = gg.FONT_NAME,
                             size   = eff_launch_font_size)
    conso_button = tk.Button(self,
                             text = gg.TEXT_PUB_CONSO,
                             font = conso_font,
                             command = _start_launch_pub_list_conso)

    etape_4 = etapes[3]

    place_bellow(etape_4,
                 conso_button,
                 dx = etape_button_dx,
                 dy = etape_button_dy / 2)
    
    # Setting buttons list for status change
    consolidate_corpus_buttons_list = [self.OptionButton_years,
                                       merge_button,
                                       homonyms_button,
                                       otp_button,
                                       conso_button]
