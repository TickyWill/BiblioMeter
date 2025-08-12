"""The `consolidate_corpus_page` module allows to built consolidated publication lists 
for the Institute selected and the data type selected.

It performs the merge of the publications list with the employees database of the Institute. 
Then it provides xlsx files to the user for:

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
from functools import partial
from pathlib import Path
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import ttk

# Local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
from bmfuncts.add_otps import add_otp
from bmfuncts.config_utils import set_org_params
from bmfuncts.consolidate_pub_list import built_final_pub_list
from bmfuncts.consolidate_pub_list import concatenate_pub_lists
from bmfuncts.merge_pub_employees import recursive_year_search
from bmfuncts.update_employees import set_employees_data
from bmfuncts.update_employees import update_employees
from bmfuncts.use_homonyms import save_homonyms
from bmfuncts.use_homonyms import set_saved_homonyms
from bmfuncts.use_homonyms import solving_homonyms
from bmfuncts.use_otps import set_saved_otps
from bmfuncts.useful_functs import check_dedup_parsing_available
from bmgui.gui_utils import disable_buttons
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import font_size
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_exit_button
from bmgui.gui_utils import set_font_size_tup
from bmgui.gui_utils import set_page_title
from bmgui.gui_utils import set_pos_tup_px
from bmgui.gui_utils import set_pos_tup_px_list
from bmgui.gui_utils import set_progress_bar_pos_tup
from bmgui.pages_utils import set_progress_bar_params
from bmgui.pages_utils import set_step_help_button 
from bmgui.pages_utils import set_step_label 
from bmgui.pages_utils import set_step_launch_button 
from bmgui.pages_utils import set_year_select_widgets
from bmgui.pages_utils import set_steps_widgets_param


def _set_empl_files_params(wf_path):
    """Sets useful folders and files parameters (path and file name) 
    for employees data management and update.

    Args:
        wf_path (path): Full path to working folder.
    Returns:
        (tup): (The folder (path) of full employees data of all available years,\
        The folder (path) of employees data used for the update of the full data, \
        The file (path) of full employees data of all available years, \
        The file name (str) of full employees data of all available years).
    """
    # Setting folder of the Institute parameters
    wf_root_path = wf_path.parent
    
    # Setting useful aliases
    empl_root_alias = bm_eg.EMPLOYEES_ARCHI["root"]
    empl_folder_alias = bm_eg.EMPLOYEES_ARCHI["all_years_employees"]
    empl_file_alias = bm_eg.EMPLOYEES_ARCHI["employees_file_name"]
    empl_upd_folder_alias = bm_eg.EMPLOYEES_ARCHI["complementary_employees"]

    # Setting useful paths independent from corpus year
    empl_root_path = wf_root_path / Path(empl_root_alias)
    empl_folder_path = empl_root_path / Path(empl_folder_alias)
    empl_upd_folder_path = empl_root_path / Path(empl_upd_folder_alias)
    empl_file_path = empl_folder_path / Path(empl_file_alias)
    
    return empl_folder_path, empl_upd_folder_path, empl_file_path, empl_file_alias


def _launch_update_employees_try(wf_path, progress_callback):
    """Launches update of Intitute employees database.

    This is done through the `update_employees` function imported from 
    `bmfuncts.update_employees` module after check of available 
    files for update (should be single) and check of Institute 
    employees database file. 
    Useful path are set through the `_set_empl_files_params` internal 
    function.

    Args:
        wf_path (path): Full path to working folder.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """
    # Setting useful file parameters for employees data
    return_tup = _set_empl_files_params(wf_path)
    empl_folder_path, empl_upd_folder_path, _, _ = return_tup
    if progress_callback:
        progress_bar_state_init = 10
        progress_callback(progress_bar_state_init)

    # Setting dialogs and checking answers
    # for ad-hoc use of 'update_employees' function
    update_status = False
    # Launch employees database update
    ask_title = "- Confirmation de la mise à jour des effectifs -"
    ask_text = ("Le fichier des effectifs de l'Institut va être mis à jour "
                "avec les nouvelles données disponibles dans le dossier :"
                f"\n\n '{empl_upd_folder_path}'."
                "\n\nCette opération peut prendre quelques minutes."
                "\nDans l'attente, ne pas fermer l'application."
                "\n\nAvant de lancer les traitements annuels, "
                "confirmez la mise à jour ?")
    answer_1 = messagebox.askokcancel(ask_title, ask_text)
    if answer_1:
        (employees_year,
         files_number_error,
         sheet_name_error,
         column_error,
         years2add_error,
         all_years_file_error) = update_employees(wf_path, progress_callback,
                                                  progress_bar_state_init)
        progress_callback(100)
        if not any([files_number_error, sheet_name_error, column_error,
                    years2add_error, all_years_file_error]):
            info_title = "- Information -"
            info_text = ("La mise à jour des effectifs a été effectuée "
                         f"pour l'année {employees_year}.")
            messagebox.showinfo(info_title, info_text)
            update_status = True
        elif all_years_file_error:
            info_title = "- Information -"
            info_text = ("La mise à jour des effectifs a été effectuée "
                         f"pour l'année {employees_year}."
                         "\nMais le fichier des effectifs consolidés "
                         f"'{effectifs_file_name}' "
                         "non disponible a été créé dans le dossier :"
                         f"\n '{empl_folder_path}'.\n"
                         f"\nErreur précise retournée :\n '{all_years_file_error}'.")
            messagebox.showinfo(info_title, info_text)
            update_status = True
        else:
            warning_title = "!!! ATTENTION : Erreurs dans les fichiers des effectifs !!!"
            if files_number_error:
                warning_text = ("Absence de fichier ou plus d'un fichier "
                                "présent dans le dossier :"
                                f"\n\n '{empl_upd_folder_path}'."
                                "\n\nNe conservez que le fichier utile "
                                "et relancez la mise à jour,"
                                "\n\nou bien lancez les traitements "
                                "annuel sans mise à jour des effectifs.")
                messagebox.showwarning(warning_title, warning_text)
                update_status = False
            if sheet_name_error:
                warning_text = ("Un nom de feuille est de format incorrect "
                                "dans le fichier des effectifs additionnels du dossier :"
                                f"\n\n '{empl_upd_folder_path}'.\n"
                                "\nErreur précise retournée :\n"
                                f"\n '{sheet_name_error}'.\n"
                                "\n 1- Ouvrez le fichier;"
                                "\n 2- Vérifiez et corrigez les noms des feuilles "
                                "dans ce fichier;"
                                "\n 3- Sauvegardez le ficher;"
                                "\n 4- Relancez la mise à jour des effectifs.")
                messagebox.showwarning(warning_title, warning_text)
                update_status = False
            if column_error:
                warning_text = ("Une colonne est manquante ou mal nommée dans une feuille "
                                "dans le fichier des effectifs additionnels du dossier :"
                                f"\n\n '{empl_upd_folder_path}'.\n"
                                "\nErreur précise retournée :\n"
                                f"\n '{column_error}'.\n"
                                "\n 1- Ouvrez le fichier;"
                                "\n 2- Vérifiez et corrigez les noms des colonnes "
                                "des feuilles dans ce fichier;"
                                "\n 3- Sauvegardez le ficher."
                                "\n 4- Relancez la mise à jour des effectifs.")
                messagebox.showwarning(warning_title, warning_text)
                update_status = False
            if years2add_error:
                warning_text = ("Le fichier des effectifs additionnels "
                                "couvre plusieurs années "
                                "dans le fichier des effectifs additionnels du dossier :"
                                f"\n\n '{empl_upd_folder_path}'.\n"
                                "\n 1- Séparez les feuilles d'années différentes "
                                "en fichiers d'effectifs additionnels différents;"
                                "\n 2- Relancer la mise à jour des effectifs "
                                "\n    pour chacun des fichiers créés en les positionant seul "
                                "dans le dossier successivement.")
                messagebox.showwarning(warning_title, warning_text)
                update_status = False
    else:
        progress_callback(100)
        # Cancel employees database update
        warning_title = "- Information -"
        warning_text = ("La mise à jour des effectifs est abandonnée."
                        f"\n\nLes croisement auteurs-effectifs de chaque l'année"
                        "se fera avec le fichier des effectifs sans sa mise à jour.")
        messagebox.showwarning(warning_title, warning_text)
        update_status = False
    return update_status


def _set_conso_year_files_params(wf_path, year_select):
    """Sets useful folders and files parameters (path and file name) depending 
    on the selected corpus year for the consolidation of the publications list.

    Args:
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
    Returns:
        (tup): (The list of set file names (str), \
        The list of the built folders paths, The list of the \
        the built files paths).
    """
    # Setting useful aliases
    merge_data_folder_alias = bm_pg.ARCHI_YEAR["bdd mensuelle"]
    submit_alias = bm_pg.ARCHI_YEAR["submit file name"]
    orphan_alias = bm_pg.ARCHI_YEAR["orphan file name"]
    homonyms_folder_alias = bm_pg.ARCHI_YEAR["homonymes folder"]
    homonyms_file_base_alias = bm_pg.ARCHI_YEAR["homonymes file name base"]
    otp_folder_alias = bm_pg.ARCHI_YEAR["OTP folder"]
    otp_file_base_alias = bm_pg.ARCHI_YEAR["OTP file name base"]
    pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    missing_if_base_alias = bm_pg.ARCHI_IF["missing_if_base"]
    missing_issn_base_alias = bm_pg.ARCHI_IF["missing_issn_base"]

    # Setting useful files names dependant on year select
    homonyms_file = homonyms_file_base_alias + f' {year_select}.xlsx'
    pub_list_file = pub_list_file_base_alias + f' {year_select}.xlsx'
    missing_if_file = f'{year_select}_' + missing_if_base_alias + ".xlsx"
    missing_issn_file = f'{year_select}_' + missing_issn_base_alias + ".xlsx"
    
    # Setting useful folders paths dependant on year select    
    corpus_year_path = wf_path / Path(year_select)
    merge_data_folder_path = corpus_year_path / Path(merge_data_folder_alias)
    homonyms_folder_path = corpus_year_path / Path(homonyms_folder_alias)
    otp_folder_path = corpus_year_path / Path(otp_folder_alias)
    pub_list_folder_path = corpus_year_path / Path(pub_list_folder_alias)

    # Setting useful files paths dependant on year select
    submit_path = merge_data_folder_path / Path(submit_alias)
    orphan_path = merge_data_folder_path / Path(orphan_alias)
    homonyms_file_path = homonyms_folder_path / Path(homonyms_file)
    pub_list_file_path = pub_list_folder_path / Path(pub_list_file)
    
    # Setting returned lists
    files_list = [submit_alias, orphan_alias, homonyms_file, otp_file_base_alias,
                  pub_list_file, missing_if_file, missing_issn_file]
    folders_paths_list = [merge_data_folder_path, homonyms_folder_path,
                          otp_folder_path, pub_list_folder_path]
    files_paths_list = [submit_path, orphan_path, homonyms_file_path, pub_list_file_path]
    return files_list, folders_paths_list, files_paths_list


def _launch_recursive_year_search_try(institute, org_tup,
                                      wf_path, datatype,
                                      year_select, search_depth_init,
                                      employees_update_status,
                                      progress_callback):
    """Launches merge of publications list with Institute employees.

    This is done through the `recursive_year_search` function imported from 
    `bmfuncts.merge_pub_employees` module after:
    - setting employees data through `_set_employees_data` function 
    - check of status of parsing step through `check_dedup_parsing_available` \
    function imported from `bmfuncts.useful_functs` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        search_depth_init (int): Initial search depth that will be adapted \
        depending on available years in Institute employees database.
        employees_update_status (bool): Equal to 'True' if employees data \
        have been updated; otherwise, equal to 'False'.
        progress_callback (function): Function for updating ProgressBar tkinter \
        widget status.
    """

    def _recursive_year_search_try(progress_callback, progress_bar_state):
        dedup_parsing_status = check_dedup_parsing_available(wf_path, year_select)
        if dedup_parsing_status:
            end_message, orphan_status = recursive_year_search(merge_data_folder_path,
                                                               employees_df, institute,
                                                               org_tup, wf_path, datatype,
                                                               year_select, search_depth,
                                                               progress_callback,
                                                               progress_bar_state)
            print('\n',end_message)
            progress_callback(100)
            info_title = '- Information -'
            info_text = f"Le croisement auteurs-effectifs de l'année {year_select} a été effectué."
            if orphan_status:
                info_text += ("\n\nTous les auteurs de l'Institut ont été "
                              "identifiés dans les effectifs."
                              "\n\nLa résolution des homonymes peut être lancée.")
            else:
                info_text += ("\n\nMais, des auteurs affiiés à l'Institut "
                              "n'ont pas été identifiés dans les effectifs."
                              f"\n1- Ouvrez le fichier {orphan_file} "
                              f"du dossier :\n  {merge_data_folder_path} ;"
                              "\n\n2- Suivez le mode opératoire disponible pour son utilisation ;"
                              "\n3- Puis relancez le croisement pour cette année."
                              "\n\nNéanmoins, la résolution des homonymes "
                              "peut être lancée sans cette opération, "
                              "mais la liste consolidée des publications sera incomplète.")
            messagebox.showinfo(info_title, info_text)

        else:
            progress_callback(100)
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text = (f"La synthèse de l'année {year_select} n'est pas disponible."
                            "\n1- Revenez à l'onglet 'Analyse élémentaire des corpus' ;"
                            "\n2- Effectuez la synthèse pour cette année ;"
                            "\n3- Puis relancez le croisement pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting files parameters independant from year selection
    return_tup = _set_empl_files_params(wf_path)
    _, _, empl_file_path, _ = return_tup

    # Setting files parameters dependent on year selection
    return_tup = _set_conso_year_files_params(wf_path, year_select)
    files_list, folders_paths_list, files_paths_list = return_tup
    orphan_file = files_list[1]
    submit_path = files_paths_list[0]
    merge_data_folder_path = folders_paths_list[0]

    if progress_callback:
        progress_bar_state_init = 10
        progress_callback(progress_bar_state_init)

    # Setting dialogs and checking answers
    # for ad-hoc use of '_recursive_year_search_try' internal function
    # after adapting search depth to available years for search
    tup = set_employees_data(year_select, empl_file_path, search_depth_init)
    employees_df, search_depth, available_empl_years = tup[0], tup[1], tup[2]
    if available_empl_years:
        status = "sans"
        if employees_update_status:
            status = "avec"
        ask_title = "- Confirmation du croisement auteurs-effectifs -"
        ask_text = ("Le croisement avec les effectifs des années "
                    f"{', '.join([str(i) for i in available_empl_years])} "
                    f"a été lancé pour l'année {year_select}."
                    f"\nCe croisement se fera {status} la mise à jour "
                    "du fichier des effectifs."
                    "\n\nCette opération peut prendre quelques minutes."
                    "\nDans l'attente, ne pas fermer l'application."
                    "\n\nContinuer ?")
        answer = messagebox.askokcancel(ask_title, ask_text)
        if answer:
            submit_status = os.path.exists(submit_path)
            if not submit_status:
                _recursive_year_search_try(progress_callback, progress_bar_state_init)
            else:
                ask_title = "- Reconstruction du croisement auteurs-effectifs -"
                ask_text = (f"Le croisement pour l'année {year_select} est déjà disponible."
                            "\n\nReconstruire le croisement ?")
                answer_4 = messagebox.askokcancel(ask_title, ask_text)
                if answer_4:
                    _recursive_year_search_try(progress_callback, progress_bar_state_init)
                else:
                    progress_callback(100)
                    info_title = "- Information -"
                    info_text = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                                 "dejà disponible est conservé.")
                    messagebox.showinfo(info_title, info_text)
        else:
            progress_callback(100)
            info_title = "- Information -"
            info_text = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                         "est annulé.")
            messagebox.showinfo(info_title, info_text)


def _launch_resolution_homonymies_try(institute, org_tup,
                                      wf_path, year_select,
                                      progress_callback):
    """Launches file creation for resolving homonyms. 

    This is done through the `solving_homonyms` function imported from 
    `bmfuncts.consolidate_pub_list` module after check of status of 
    publications-employees merge step. 
    The Created file is filled with previously resolved homonyms 
    through `set_saved_homonyms` function imported from 
    `bmfuncts.use_pub_attributes` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """

    def _resolution_homonymies_try(progress_callback):
        if os.path.isfile(submit_path):
            progress_callback(20)
            return_tup = solving_homonyms(institute, org_tup,
                                          submit_path, homonyms_file_path)
            end_message, actual_homonym_status = return_tup
            print(end_message)
            print('\n Actual homonyms status before setting saved homonyms:',
                  actual_homonym_status)
            progress_callback(80)
            if actual_homonym_status:
                return_tup = set_saved_homonyms(institute, org_tup,
                                                wf_path, year_select,
                                                actual_homonym_status)
                end_message, actual_homonym_status = return_tup
            print('\n',end_message)
            print('\n Actual homonyms status after setting saved homonyms:',
                  actual_homonym_status)
            progress_callback(100)
            info_title = "- Information -"
            info_text = ("Le fichier pour la résolution des homonymies "
                         f"de l'année {year_select} a été créé "
                         f"dans le dossier :\n\n  '{homonyms_folder_path}' "
                         f"\n\nsous le nom :  '{homonyms_file}'.")
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
            progress_callback(100)
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text = ("Le fichier contenant le croisement auteurs-effectifs "
                            f"de l'année {year_select} n'est pas disponible."
                            "\n1- Effectuez d'abord le croisement pour cette année."
                            "\n2- Puis relancez la résolution des homonymies pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting files parameters dependent on year selection
    return_tup = _set_conso_year_files_params(wf_path, year_select)
    files_list, folders_paths_list, files_paths_list = return_tup
    homonyms_file = files_list[2]
    submit_path = files_paths_list[0]
    homonyms_file_path = files_paths_list[2]
    homonyms_folder_path = folders_paths_list[1]

    if progress_callback:
        progress_bar_state_init = 10
        progress_callback(progress_bar_state_init)

    # Setting dialogs and checking answers
    # for ad-hoc use of '_resolution_homonymies_try' internal function
    ask_title = "- Confirmation de l'étape de résolution des homonymies -"
    ask_text = ("La création du fichier pour cette résolution "
                f"a été lancée pour l'année {year_select}."
                "\n\nContinuer ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        progress_callback(10)
        homonymes_status = os.path.exists(homonyms_file_path)
        if not homonymes_status:
            _resolution_homonymies_try(progress_callback)
        else:
            ask_title = "- Reconstruction de la résolution des homonymes -"
            ask_text = ("Le fichier pour la résolution des homonymies "
                        f"de l'année {year_select} est déjà disponible."
                        "\n\nReconstruire ce fichier ?")
            answer_1 = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:
                _resolution_homonymies_try(progress_callback)
            else:
                progress_callback(100)
                info_title = "- Information -"
                info_text = ("Le fichier pour la résolution des homonymies "
                             f"de l'année {year_select} dejà disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("La création du fichier pour la résolution "
                     f"des homonymies de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def _launch_add_otp_try(institute, org_tup,
                        wf_path, year_select,
                        progress_callback):
    """Launches files creation for adding OTP attribute to publications.

    This is done through the `add_otp` function imported from 
    `bmfuncts.add_otps` module after:

    - check of status of homonyms resolution step 
    - saving the resolved homonyms through `save_homonyms` function \
    imported from `bmfuncts.use_pub_attributes` module.

    The created files are filled with previously set OTPs through 
    `set_saved_otps` function imported from `bmfuncts.use_otps` 
    module. 

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """

    def _add_otp_try(progress_callback):
        if os.path.isfile(homonyms_file_path):
            progress_callback(15)
            end_message = save_homonyms(institute, org_tup, wf_path, year_select)
            print('\n',end_message)
            progress_callback(20)
            end_message = add_otp(institute, org_tup, wf_path,
                                  homonyms_file_path, otp_folder_path, otp_file_base)
            print(end_message)
            progress_callback(80)
            end_message = set_saved_otps(institute, org_tup, wf_path, year_select)
            print(end_message)
            progress_callback(100)
            info_title = "- Information -"
            info_text = (f"Les fichiers de l'année {year_select} pour l'attribution des OTPs "
                         f"ont été créés dans le dossier : \n\n'{otp_folder_path}' "
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
            warning_text = ("Le fichier contenant la résolution des homonymies "
                            f"de l'année {year_select} n'est pas disponible."
                            "\n1- Effectuez la résolution des homonymies pour cette année."
                            "\n2- Relancez l'attribution des OTPs pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting files parameters dependent on year selection
    return_tup = _set_conso_year_files_params(wf_path, year_select)
    files_list, folders_paths_list, files_paths_list = return_tup
    otp_file_base = files_list[3]
    homonyms_file_path = files_paths_list[2]
    otp_folder_path = folders_paths_list[2]

    if progress_callback:
        progress_bar_state_init = 10
        progress_callback(progress_bar_state_init)

    # Getting institute parameters
    dpt_label_list = list(org_tup[1].keys())

    # Setting dialogs and checking answers
    # for ad-hoc use of '_add_otp_try' internal function
    ask_title = "- Confirmation de l'étape d'attribution des OTPs -"
    ask_text = ("La création des fichiers pour cette attribution "
                f"a été lancée pour l'année {year_select}."
                "\n\nContinuer ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        progress_callback(10)
        otp_path_status = os.path.exists(otp_folder_path)
        if otp_path_status:
            otp_files_status_list = []
            for dpt_label in dpt_label_list:
                dpt_otp_file_name = otp_file_base + f'_{dpt_label}.xlsx'
                dpt_otp_file_path = otp_folder_path / Path(dpt_otp_file_name)
                otp_files_status_list.append(not dpt_otp_file_path.is_file())
            if any(otp_files_status_list):
                _add_otp_try(progress_callback)
            else:
                ask_title = "- Reconstruction de l'attribution des OTPs -"
                ask_text = ("Les fichiers pour l'attribution des OTPs "
                            f"de l'année {year_select} sont déjà disponibles."
                            "\n\nReconstruire ces fichiers ?")
                answer_1 = messagebox.askokcancel(ask_title, ask_text)
                if answer_1:
                    _add_otp_try(progress_callback)
                else:
                    progress_callback(100)
                    info_title = "- Information -"
                    info_text = ("Les fichiers pour l'attribution des OTPs "
                                 f"de l'année {year_select} dejà disponibles sont conservés.")
                    messagebox.showinfo(info_title, info_text)
        else:
            os.mkdir(otp_folder_path)
            _add_otp_try(progress_callback)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("La création des fichiers pour l'attribution des OTPs "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def _launch_pub_list_conso_try(institute, org_tup,
                               wf_path, datatype,
                               year_select, years_list,
                               progress_callback):
    """Launches building of publications final list.

    This is done through the `built_final_pub_list` 
    function imported from `bmfuncts.consolidate_pub_list` 
    module after check of status of OTPs adding step.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        years_list (list): List of available corpus years \
        (each item defined by a string of 4 digits).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.  
    """

    def _consolidate_pub_list(progress_callback):
        if os.path.isdir(otp_folder_path) and os.listdir(otp_folder_path):
            progress_callback(20)
            conso_tup = built_final_pub_list(institute, org_tup,
                                             wf_path, datatype,
                                             otp_folder_path, pub_list_folder_path,
                                             otp_file_base, year_select)
            end_message, pub_nb, split_ratio, if_database_complete = conso_tup
            print(end_message)
            progress_callback(70)
            if bm_pg.LISTES_CONCAT:
                end_message = concatenate_pub_lists(wf_path, years_list)
                print('\n',end_message)
            progress_callback(100)
            info_title = "- Information -"
            info_text = (f"Une liste consolidée de {pub_nb} publications a été créée "
                         f"pour l'année {year_select} dans le dossier :\n\n '{pub_list_file_path}' "
                         f"\n\nsous le nom :   '{pub_list_file}'."
                         "\n\nLes IFs disponibles ont été automatiquement attribués.")
            if if_database_complete:
                info_text += ("\n\nLa base de données des facteurs d'impact étant complète, "
                              "les listes des journaux avec IFs ou ISSNs inconnus sont vides.")
            else:
                info_text += ("\n\nAttention, les listes des journaux avec IFs ou ISSNs inconnus "
                              "ont été créées dans le même dossier sous les noms :"
                              f"\n\n '{missing_if_file}' "
                              f"\n\n '{missing_issn_file}' "
                              "\n\n Ces fichiers peuvent être modifiés pour compléter "
                              "la base de donnée des IFs :"
                              "\n\n1- Ouvrez chacun de ces fichiers ;"
                              "\n2- Complétez manuellement les IFs inconnus ou les ISSNs "
                              "et IFs inconnus, selon le fichier - "
                              "\n       Attention : VIRGULE pour le séparateur décimal des IFS ;"
                              "\n3- Puis sauvegardez les fichiers sous le même nom ;"
                              "\n4- Pour prendre en compte ces compléments, allez à la page "
                              "de mise à jour des IFs.")
            info_text += ("\n\nPar ailleurs, cette liste consolidée des publications "
                          f"a été décomposée à {split_ratio} % "
                          "en trois fichiers disponibles dans le même dossier "
                          "correspondant aux différentes "
                          "classes de documents (les classes n'étant pas exhaustives, "
                          "la décomposition peut être partielle)."
                          "\n\nLa liste des publications invalides a été créée "
                          "dans le même dossier.")
            if bm_pg.LISTES_CONCAT:
                all_years_data_folder = bm_pg.ARCHI_BDD_MULTI_ANNUELLE
                info_text += ("\n\nEnfin, la concaténation des listes consolidées des publications "
                              "disponibles, a été créée dans le dossier :"
                              f"\n\n '{all_years_data_folder}' "
                              "\n\nsous un nom vous identifiant ainsi que la liste des années "
                              "prises en compte et caractérisé par la date et l'heure de la création.")
            messagebox.showinfo(info_title, info_text)

        else:
            progress_callback(100)
            warning_title = "!!! ATTENTION : fichiers manquants !!!"
            warning_text = ("Les fichiers d'attribution des OTPs "
                            f"de l'année {year_select} ne sont pas disponibles."
                            "\n1- Relancez la création des fichiers d'attribution des OTPs "
                            "pour cette année."
                            "\n2- Relancez la consolidation de la liste des publications "
                            "pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    # Setting files parameters dependent on year selection
    return_tup = _set_conso_year_files_params(wf_path, year_select)
    files_list, folders_paths_list, files_paths_list = return_tup
    otp_file_base = files_list[3]
    pub_list_file, missing_if_file, missing_issn_file = files_list[4:7]
    pub_list_file_path = files_paths_list[3]
    otp_folder_path = folders_paths_list[2]
    pub_list_folder_path = folders_paths_list[3]

    # Setting dialogs and checking answers
    # for ad-hoc use of '_consolidate_pub_list' internal function
    ask_title = "- Confirmation de l'étape de consolidation de la liste des publications -"
    ask_text = ("La création du fichier de la liste consolidée des publications "
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
            ask_text = ("Le fichier de la liste consolidée des publications "
                        f"de l'année {year_select} est déjà disponible."
                        "\n\nReconstruire ce fichier ?")
            answer_1 = messagebox.askokcancel(ask_title, ask_text)
            if answer_1:
                _consolidate_pub_list(progress_callback)
            else:
                progress_callback(100)
                info_title = "- Information -"
                info_text = ("Le fichier de la liste consolidée des publications "
                             f"de l'année {year_select} dejà disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("La création du fichier de la liste consolidée des publications "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)

    
def create_consolidate_corpus(self, master, page_name, institute, wf_path, datatype):
    """Manages creation and use of widgets for corpus consolidation 
    through merge with Institute employees database.

    Args:
        self (instense): Instense where consolidation page will be created.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of consolidation page.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """
    # Internal functions

    def _update_progress(value):
        self.progress_var.set(value)
        self.progress_bar.update_idletasks()
        if value>=100:
            enable_buttons(self.page_buttons_list)


    # ****************************** GENERAL SETTNGS
    
    # initializing update status of employees data
    empl_update_status = False

    # Getting institute parameters
    wf_root_path = wf_path.parent
    org_tup = set_org_params(institute, wf_root_path)

    # Creating and setting widgets for page title and exit button
    page_label = bm_gg.PAGES_LABELS[page_name]
    set_page_title(self, master, page_label, institute, datatype)
    set_exit_button(self, master)

    # Setting short_name for page key and year key to use in globals
    self.page_key = bm_gg.KEY_CONSO
    self.year_key = bm_gg.KEY_CONSO_YEAR
    
    # Setting progress bars parameters
    set_progress_bar_params(self, master)

    # Setting steps widgets parameters
    set_steps_widgets_param(self, master)

    # *********************** STEP 0: UPDATE EMPLOYEES DATA
    def _launch_update_employees(progress_callback):
        """Command of the 'empl_update_button' button.        
        """
        # Trying launch of update of employees file
        employees_update_status = _launch_update_employees_try(wf_path,
                                                               progress_callback)
        self.progress_bar.place_forget()

    def _start_update_employees():
        disable_buttons(self.page_buttons_list)
        place_after(empl_update_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_update_employees,
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for employees-update
    step_num = 0
    empl_help_button = set_step_help_button(self, step_num)
    empl_update_button = set_step_launch_button(self, step_num,
                                                _start_update_employees,
                                                'bellow')


    # ****************************** YEAR SELECTION

    default_year = master.years_list[-1]
    self.variable_years = tk.StringVar(self)
    self.variable_years.set(default_year)
    set_year_select_widgets(self, master)


    # *********************** STEP 1: MERGE AUTHORS-EMPLOYEES
    def _launch_recursive_year_search(progress_callback):
        """Command of the 'merge_button' button.        
        """
        # Getting year selection
        year_select = self.variable_years.get()

        # Trying launch of recursive search for authors in employees file
        _launch_recursive_year_search_try(institute, org_tup,
                                          wf_path, datatype,
                                          year_select, bm_eg.SEARCH_DEPTH,
                                          empl_update_status,
                                          progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_recursive_year_search():
        disable_buttons(self.page_buttons_list)
        place_after(merge_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_recursive_year_search,
                         args=(_update_progress,)).start()

    # Setting widgets for authors-employees-merge button
    step_num = 1
    merge_help_button = set_step_help_button(self, step_num)     
    merge_button = set_step_launch_button(self, step_num,
                                          _start_launch_recursive_year_search,
                                          'bellow')


    # ******************* STEP 2: HOMONYMS RESOLUTION
    def _launch_resolution_homonymies(progress_callback):
        """Command of the 'homonyms_button' button.
        """
        # Renewing year selection
        year_select = self.variable_years.get()

        # Trying launch creation of file for homonymies resolution
        _launch_resolution_homonymies_try(institute, org_tup,
                                          wf_path, year_select,
                                          progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_resolution_homonymies():
        disable_buttons(self.page_buttons_list)
        place_after(homonyms_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_resolution_homonymies,
                         args=(_update_progress,)).start()

    # Setting widgets for homonyms-resolution button
    step_num = 2
    homonyms_help_button = set_step_help_button(self, step_num)    
    homonyms_button = set_step_launch_button(self, step_num,
                                             _start_launch_resolution_homonymies,
                                             'bellow')

    # ******************* STEP 3: OTPs ATTRIBUTION
    def _launch_add_otp(progress_callback):
        """Command of the 'otp_button' button.        
        """

        # Renewing year selection
        year_select = self.variable_years.get()

        # Trying launch creation of files for OTP attribution
        _launch_add_otp_try(institute, org_tup,
                            wf_path,
                            year_select,
                            progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_add_otp():
        disable_buttons(self.page_buttons_list)
        place_after(otp_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_add_otp,
                         args=(_update_progress,)).start()

    # Setting widgets for OTPs attribution button
    step_num = 3
    otp_help_button = set_step_help_button(self, step_num)      
    otp_button = set_step_launch_button(self, step_num,
                                        _start_launch_add_otp,
                                        'bellow')

    # ****************** STEP 4: PUBLICATIONS-LIST CONSOLIDATION
    def _launch_pub_list_conso(progress_callback):
        """Command of the 'conso_button' button.
        """
        # Renewing year selection and years
        year_select = self.variable_years.get()

        # Trying launch creation of consolidated publications lists
        _launch_pub_list_conso_try(institute, org_tup,
                                   wf_path, datatype,
                                   year_select, master.years_list,
                                   progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_pub_list_conso():
        disable_buttons(self.page_buttons_list)
        place_after(conso_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_pub_list_conso,
                         args=(_update_progress,)).start()

    # Setting widgets for consolidation of publications list
    step_num = 4
    conso_help_button = set_step_help_button(self, step_num)      
    conso_button = set_step_launch_button(self, step_num,
                                          _start_launch_pub_list_conso,
                                          'bellow')

    # Setting buttons list for status change
    self.page_buttons_list = [self.years_opt_but,
                              empl_update_button,
                              merge_button,
                              homonyms_button,
                              otp_button,
                              conso_button]
