"""The `consolidate_corpus_page` module allows to built consolidated publication lists 
for the Institute selected and the data type selected.

It performs the merge of the publications list with the employees database of the Institute. 
Then it provides xlsx files to the user for:

- Authors metadata correction when not found in the employees database;
- Homonymies resolution;
- Publications OTPs setting;
- Completion of impact-factors database.

Finally, it saves the consolidated publications list in a dedicated directory.
"""
__all__ = ['create_consolidate_corpus']


# Standard library imports
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

# Local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu
import bmgui.pages_utils as bm_pu
from bmfuncts.add_otps import add_otp
from bmfuncts.consolidate_pub_list import built_final_pub_list
from bmfuncts.consolidate_pub_list import check_dedup_parsing_available
from bmfuncts.consolidate_pub_list import concatenate_pub_lists
from bmfuncts.merge_pub_employees import recursive_year_search
from bmfuncts.update_employees import set_employees_data
from bmfuncts.update_employees import update_employees
from bmfuncts.use_homonyms import set_saved_homonyms
from bmfuncts.use_homonyms import solve_homonyms
from bmfuncts.use_otps import set_saved_otps
from bmfuncts.useful_functs import set_bold_txt


def _set_empl_files_params(root_path):
    """Sets useful folders and files parameters (path and file name) 
    for employees data management and update.

    Args:
        root_path (path): The full path to the folder where the folder \
        of Institute parameters are saved.
    Returns:
        (tup): (The folder (path) of full employees data of all available years,\
        The folder (path) of employees data used for the update of the full data, \
        The file (path) of full employees data of all available years, \
        The file name (str) of full employees data of all available years).
    """
    # Setting useful aliases
    empl_root_alias = bm_eg.EMPLOYEES_ARCHI["root"]
    empl_folder_alias = bm_eg.EMPLOYEES_ARCHI["all_years_employees"]
    empl_file_alias = bm_eg.EMPLOYEES_ARCHI["employees_file_name"]
    empl_upd_folder_alias = bm_eg.EMPLOYEES_ARCHI["complementary_employees"]

    # Setting useful paths independent of corpus year
    empl_root_path = root_path / Path(empl_root_alias)
    empl_folder_path = empl_root_path / Path(empl_folder_alias)
    empl_upd_folder_path = empl_root_path / Path(empl_upd_folder_alias)
    empl_file_path = empl_folder_path / Path(empl_file_alias)

    return empl_folder_path, empl_upd_folder_path, empl_file_path, empl_file_alias


def _launch_update_employees_try(self, wf_path, progress_callback):
    """Launches update of Institute employees database.

    This is done through the `update_employees` function imported from 
    `bmfuncts.update_employees` module after check of available 
    files for update (should be single) and check of Institute 
    employees database file.

    Args:
        self (instance): Instance of the calling page.
        wf_path (path): Full path to working folder.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    Returns:
        (bool): Update status of the employees' data.
    """
    progress_bar_state_init = None
    if progress_callback:
        progress_bar_state_init = 10
        progress_callback(progress_bar_state_init)

    # Setting dialogs and checking answers
    # for ad-hoc use of 'update_employees' function
    # Launch employees database update
    ask_title = "- Confirmation de la mise à jour des effectifs -"
    ask_text = ("Le fichier des effectifs de l'Institut va être mis à jour "
                "avec les nouvelles données disponibles dans le dossier :"
                f"\n\n '{self.empl_upd_folder_path}'."
                "\n\nCette opération peut prendre quelques minutes."
                "\nDans l'attente, ne pas fermer l'application."
                "\n\nAvant de lancer les traitements annuels, "
                "confirmez la mise à jour ?")
    answer_1 = messagebox.askokcancel(ask_title, ask_text)
    if answer_1:
        log_title = "UPDATE OF EMPLOYEES DATABASE"
        print(f"\n\n{set_bold_txt(log_title)}")

        (employees_year, files_number_error, sheet_name_error,
         column_error, years2add_error,
         all_years_file_error) = update_employees(wf_path, progress_callback,
                                                  progress_bar_state_init)
        progress_callback(100)
        if not any([files_number_error, sheet_name_error, column_error,
                    years2add_error, all_years_file_error]):
            update_status = True
            print("File of employees-data updated")

            # Displaying the status of the update of employees data
            info_title = "- Information -"
            info_text = ("La mise à jour des effectifs a été effectuée "
                         f"pour l'année {employees_year}.")
            messagebox.showinfo(info_title, info_text)
        elif all_years_file_error:
            update_status = True
            print("File of employees data created")

            # Displaying the status of the update of employees data
            info_title = "- Information -"
            info_text = ("La mise à jour des effectifs a été effectuée "
                         f"pour l'année {employees_year}."
                         "\nMais le fichier des effectifs consolidés "
                         f"'{self.empl_file_name}' "
                         "non disponible a été créé dans le dossier :"
                         f"\n '{self.empl_folder_path}'.\n"
                         f"\nErreur précise retournée :\n '{all_years_file_error}'.")
            messagebox.showinfo(info_title, info_text)
        else:
            update_status = False
            print("Update of employees data aborted (error in the provided file for update)")

            # Displaying the status of the update of employees data
            warning_title = "!!! ATTENTION : Erreurs dans les fichiers des effectifs !!!"
            if files_number_error:
                warning_text = ("Absence de fichier ou plus d'un fichier "
                                "présent dans le dossier :"
                                f"\n\n '{self.empl_upd_folder_path}'."
                                "\n\nNe conservez que le fichier utile "
                                "et relancez la mise à jour,"
                                "\n\nou bien lancez les traitements "
                                "annuel sans mise à jour des effectifs.")
                messagebox.showwarning(warning_title, warning_text)
            if sheet_name_error:
                warning_text = ("Un nom de feuille est de format incorrect "
                                "dans le fichier des effectifs additionnels du dossier :"
                                f"\n\n '{self.empl_upd_folder_path}'.\n"
                                "\nErreur précise retournée :\n"
                                f"\n '{sheet_name_error}'.\n"
                                "\n 1- Ouvrez le fichier;"
                                "\n 2- Vérifiez et corrigez les noms des feuilles "
                                "dans ce fichier;"
                                "\n 3- Sauvegardez le fichier;"
                                "\n 4- Relancez la mise à jour des effectifs.")
                messagebox.showwarning(warning_title, warning_text)
            if column_error:
                warning_text = ("Une colonne est manquante ou mal nommée dans une feuille "
                                "dans le fichier des effectifs additionnels du dossier :"
                                f"\n\n '{self.empl_upd_folder_path}'.\n"
                                "\nErreur précise retournée :\n"
                                f"\n '{column_error}'.\n"
                                "\n 1- Ouvrez le fichier;"
                                "\n 2- Vérifiez et corrigez les noms des colonnes "
                                "des feuilles dans ce fichier;"
                                "\n 3- Sauvegardez le fichier."
                                "\n 4- Relancez la mise à jour des effectifs.")
                messagebox.showwarning(warning_title, warning_text)
            if years2add_error:
                warning_text = ("Le fichier des effectifs additionnels "
                                "couvre plusieurs années "
                                "dans le fichier des effectifs additionnels du dossier :"
                                f"\n\n '{self.empl_upd_folder_path}'.\n"
                                "\n 1- Séparez les feuilles d'années différentes "
                                "en fichiers d'effectifs additionnels différents;"
                                "\n 2- Relancer la mise à jour des effectifs pour "
                                "chacun des fichiers créés en le positionnant seul "
                                "dans le dossier.")
                messagebox.showwarning(warning_title, warning_text)
    else:
        progress_callback(100)
        update_status = False
        print("Update of employees data canceled")

        # Displaying the status of the update of employees data
        warning_title = "- Information -"
        warning_text = ("La mise à jour des effectifs est abandonnée."
                        "\n\nLes croisement auteurs-effectifs de chaque l'année"
                        "se fera avec le fichier des effectifs sans sa mise à jour.")
        messagebox.showwarning(warning_title, warning_text)
    return update_status


def _set_merge_year_files_param(wf_path, year_select):
    """Sets useful folders and files parameters (path and file name) 
    depending on the selected corpus year for the step of the merge 
    of employees data into the publications list.

    Args:
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
    Returns:
        (tup): (The file name of the list of publications with \
        one row per author that is missing in the employees data (str), \
        The full path to the file of the list of publications with \
        one row per author found in the employees data, The full path \
        to the folder where the results of the merge are saved).
    """
    # Setting useful aliases
    merge_folder_alias = bm_pg.ARCHI_YEAR["bdd mensuelle"]
    submit_alias = bm_pg.ARCHI_YEAR["submit file name"]
    orphan_alias = bm_pg.ARCHI_YEAR["orphan file name"]
    hash_id_alias = bm_pg.ARCHI_YEAR["hash_id file name"]

    # Setting useful folders paths dependent on year select
    corpus_year_path = wf_path / Path(year_select)
    merge_folder_path = corpus_year_path / Path(merge_folder_alias)

    # Setting useful files paths dependant on year select
    submit_path = merge_folder_path / Path(submit_alias)
    orphan_path = merge_folder_path / Path(orphan_alias)
    hash_id_path = merge_folder_path / Path(hash_id_alias)

    merge_files = [submit_alias, orphan_alias]
    merge_paths = [merge_folder_path, submit_path, orphan_path, hash_id_path]

    return merge_files, merge_paths


def _launch_recursive_year_search_try(self, master, year_select, progress_callback):
    """Launches merge of publications list with Institute employees.

    This is done through the `recursive_year_search` function imported from 
    `bmfuncts.merge_pub_employees` module after:
    - setting employees data through `set_employees_data` function imported \
    from `bmfuncts.update_employees` module.
    - check of status of parsing step through `check_dedup_parsing_available` \
    function imported from `bmfuncts.useful_functs` module.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """
    def _recursive_year_search_try(_progress_callback, progress_bar_state):
        dedup_parsing_status = check_dedup_parsing_available(master.wf_path, year_select)
        if dedup_parsing_status:
            # Setting the list of useful params values selected by the user
            params_list = [master.institute, master.org_tup, master.wf_path,
                           master.datatype, year_select]

            # Searching recursively the authors in the employees data
            orphan_status = recursive_year_search(orphan_file=orphan_file,
                                                  merge_paths=merge_paths,
                                                  empl_dict=employees_dict,
                                                  params_list=params_list,
                                                  search_depth=search_depth,
                                                  progress_callback=_progress_callback,
                                                  progress_bar_state=progress_bar_state)
            _progress_callback(100)

            # Displaying the status of the recursive search of authors
            _info_title = '- Information -'
            _info_text = f"Le croisement auteurs-effectifs de l'année {year_select} a été effectué."
            if orphan_status:
                _info_text += ("\n\nTous les auteurs de l'Institut ont été "
                              "identifiés dans les effectifs."
                              "\n\nLa résolution des homonymes peut être lancée.")
            else:
                _info_text += ("\n\nMais, des auteurs affiiés à l'Institut "
                              "n'ont pas été identifiés dans les effectifs."
                              f"\n1- Ouvrez le fichier {orphan_file} "
                              f"du dossier :\n  {merge_folder_path} ;"
                              "\n\n2- Suivez le mode opératoire disponible pour son utilisation ;"
                              "\n3- Puis relancez le croisement pour cette année."
                              "\n\nNéanmoins, la résolution des homonymes "
                              "peut être lancée sans cette opération, "
                              "mais la liste consolidée des publications sera incomplète.")
            messagebox.showinfo(_info_title, _info_text)

        else:
            _progress_callback(100)

            # Displaying the status of the recursive search of authors
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text = (f"La synthèse de l'année {year_select} n'est pas disponible."
                            "\n1- Revenez à l'onglet 'Analyse élémentaire des corpus' ;"
                            "\n2- Effectuez la synthèse pour cette année ;"
                            "\n3- Puis relancez le croisement pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    log_title = f"ENHANCEMENT OF PUBLICATIONS LIST WITH EMPLOYEES DATA FOR {year_select}"
    print(f"\n\n{set_bold_txt(log_title)}")

    # Setting files parameters dependent on year selection
    merge_files, merge_paths = _set_merge_year_files_param(master.wf_path, year_select)
    orphan_file = merge_files[1]
    merge_folder_path, submit_path = merge_paths[:2]

    progress_bar_state_init = None
    if progress_callback:
        progress_bar_state_init = 10
        progress_callback(progress_bar_state_init)

    # Setting dialogs and checking answers
    # for ad-hoc use of '_recursive_year_search_try' internal function
    # after adapting search depth to available years for search
    tup = set_employees_data(year_select, self.empl_file_path, bm_eg.SEARCH_DEPTH)
    employees_dict, search_depth, available_empl_years = tup[0], tup[1], tup[2]
    if available_empl_years:
        status = "sans"
        if self.empl_update_status:
            # Employees data previously updated
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

                    # Displaying the status of the recursive search of authors
                    info_title = "- Information -"
                    info_text = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                                 "dejà disponible est conservé.")
                    messagebox.showinfo(info_title, info_text)
        else:
            progress_callback(100)

            # Displaying the status of the recursive search of authors
            info_title = "- Information -"
            info_text = (f"Le croisement auteurs-effectifs de l'année {year_select} "
                         "est annulé.")
            messagebox.showinfo(info_title, info_text)


def _set_homonymies_year_files_param(wf_path, year_select):
    """Sets useful folders and files parameters (path and file name) 
    depending on the selected corpus year for homonymies-resolution step.

    Args:
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
    Returns:
        (tup): (The full path to the file of the list of publications with \
        one row per author found in the employees data, The full path to the \
        file of data for homonymies resolution, The full path to the folder \
        of data for homonymies resolution, The file name of data for \
        homonymies resolution).
    """
    # Setting useful aliases
    merge_data_folder_alias = bm_pg.ARCHI_YEAR["bdd mensuelle"]
    submit_alias = bm_pg.ARCHI_YEAR["submit file name"]
    homonyms_folder_alias = bm_pg.ARCHI_YEAR["homonymes folder"]
    homonyms_file_base_alias = bm_pg.ARCHI_YEAR["homonymes file name base"]

    # Setting useful files names dependent on year select
    homonyms_file = homonyms_file_base_alias + f' {year_select}.xlsx'

    # Setting useful folders paths dependent on year select
    corpus_year_path = wf_path / Path(year_select)
    merge_data_folder_path = corpus_year_path / Path(merge_data_folder_alias)
    homonyms_folder_path = corpus_year_path / Path(homonyms_folder_alias)

    # Setting useful files paths dependant on year select
    submit_path = merge_data_folder_path / Path(submit_alias)
    homonyms_file_path = homonyms_folder_path / Path(homonyms_file)

    return submit_path, homonyms_file_path, homonyms_folder_path, homonyms_file


def _launch_resolution_homonymies_try(master, year_select, progress_callback):
    """Launches file creation for resolving homonyms. 

    This is done through the `solve_homonyms` function imported from 
    `bmfuncts.use_homonyms` module after check of status of 
    publications-employees merge step. 
    The created file is filled with previously resolved homonyms 
    through `set_saved_homonyms` function imported from 
    `bmfuncts.use_homonyms` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """
    def _resolution_homonymies_try(_progress_callback):
        if os.path.isfile(submit_path):
            _progress_callback(20)

            # Creating the files for homonyms resolution by the user
            homonyms_status = solve_homonyms(master.institute, master.org_tup,
                                             submit_path, homonyms_file_path)
            _progress_callback(80)
            if homonyms_status:
                # Setting the list of useful params values selected by the user
                sub_params_list = [master.institute, master.org_tup,
                                   master.wf_path, year_select]

                # Using the available history of homonyms resolution by the user
                # in the files for homonyms resolution
                homonyms_status = set_saved_homonyms(sub_params_list,
                                                     homonyms_status)
            _progress_callback(100)

            # Displaying the status of the homonyms step
            _info_title = "- Information -"
            _info_text = ("Le fichier pour la résolution des homonymies "
                         f"de l'année {year_select} a été créé "
                         f"dans le dossier :\n\n  '{homonyms_folder_path}' "
                         f"\n\nsous le nom :  '{homonyms_file}'.")
            if homonyms_status:
                _info_text += ("\n\nDes homonymes existent parmi "
                              "les auteurs dans les effectifs."
                              "\n\n1- Ouvrez ce fichier, "
                              "\n2- Supprimez manuellement les lignes "
                              "des homonymes non-auteurs, "
                              "\n3- Puis sauvegardez le fichier sous le même nom."
                              "\n\nDès que le fichier est traité, "
                              "\nl'attribution des OTPs peut être lancée.")
            else:
                _info_text += ("\n\nAucun homonyme n'est trouvé parmi "
                              "les auteurs dans les effectifs."
                              "\n\nL'attribution des OTPs peut être lancée.")
            messagebox.showinfo(_info_title, _info_text)

        else:
            _progress_callback(100)

            # Displaying the status of the homonyms step
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text = ("Le fichier contenant le croisement auteurs-effectifs "
                            f"de l'année {year_select} n'est pas disponible."
                            "\n1- Effectuez d'abord le croisement pour cette année."
                            "\n2- Puis relancez la résolution des homonymies pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    log_title = f"BUILD OF DATA FOR HOMONYMS RESOLUTION FOR {year_select}"
    print(f"\n\n{set_bold_txt(log_title)}")

    # Setting files parameters dependent on year selection
    return_tup = _set_homonymies_year_files_param(master.wf_path, year_select)
    submit_path, homonyms_file_path, homonyms_folder_path, homonyms_file = return_tup

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

                # Displaying the status of the homonyms step
                info_title = "- Information -"
                info_text = ("Le fichier pour la résolution des homonymies "
                             f"de l'année {year_select} dejà disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)

        # Displaying the status of the homonyms step
        info_title = "- Information -"
        info_text = ("La création du fichier pour la résolution "
                     f"des homonymies de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def _set_otp_year_files_param(wf_path, year_select):
    """Sets useful folders and files parameters (path and file name) 
    depending on the selected corpus year for the OTPs attribution step.

    Args:
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
    Returns:
        (tup): (The full path to the file of data of homonymies resolution, \
        The full path to the folder of data for OTPs attribution, \
        The file-name base of data for OTPs attribution).
    """
    # Setting useful aliases
    homonyms_folder_alias = bm_pg.ARCHI_YEAR["homonymes folder"]
    homonyms_file_base_alias = bm_pg.ARCHI_YEAR["homonymes file name base"]
    otp_folder_alias = bm_pg.ARCHI_YEAR["OTP folder"]
    otp_file_base_alias = bm_pg.ARCHI_YEAR["OTP file name base"]

    # Setting useful files names dependent on year select
    homonyms_file = homonyms_file_base_alias + f' {year_select}.xlsx'

    # Setting useful folders paths dependent on year select
    corpus_year_path = wf_path / Path(year_select)
    homonyms_folder_path = corpus_year_path / Path(homonyms_folder_alias)
    otp_folder_path = corpus_year_path / Path(otp_folder_alias)

    # Setting useful files paths dependant on year select
    homonyms_file_path = homonyms_folder_path / Path(homonyms_file)

    return homonyms_file_path, otp_folder_path, otp_file_base_alias


def _launch_add_otp_try(master, year_select, progress_callback):
    """Launches files creation for adding OTP attribute to publications.

    This is done through the `add_otp` function imported from 
    `bmfuncts.add_otps` module after checking of status of 
    homonyms resolution step. 
    The created files are filled with previously set OTPs through 
    `set_saved_otps` function imported from `bmfuncts.use_otps` 
    module. 

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """

    def _add_otp_try(_progress_callback):
        if os.path.isfile(homonyms_file_path):
            # Setting the list of useful params values selected by the user
            sub_params_list = [master.institute, master.org_tup,
                               master.wf_path, year_select]
            _progress_callback(20)

            # Creating the files for OTPs attribution by the user
            _ = add_otp(sub_params_list, homonyms_file_path,
                        otp_folder_path, otp_file_base)
            _progress_callback(80)

            # Using the available history of OTPs attribution by the user
            # in the created files for that
            _ = set_saved_otps(sub_params_list)
            _progress_callback(100)

            # Displaying the status of the OTPs step
            _info_title = "- Information -"
            _info_text = (f"Les fichiers de l'année {year_select} pour l'attribution des OTPs "
                         f"ont été créés dans le dossier : \n\n'{otp_folder_path}' "
                         "\n\n1- Ouvrez le fichier du département ad-hoc, "
                         "\n2- Attribuez manuellement à chacune des publications un OTP, "
                         "\n3- Sauvegardez le fichier en ajoutant à son nom '_ok'."
                         "\n\nDès que les fichiers de tous les départements "
                         "sont traités, la liste consolidée des publications "
                         f"de l'année {year_select} peut être créée.")
            messagebox.showinfo(_info_title, _info_text)
        else:
            _progress_callback(100)

            # Displaying up the status of the OTPs step
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text = ("Le fichier contenant la résolution des homonymies "
                            f"de l'année {year_select} n'est pas disponible."
                            "\n1- Effectuez la résolution des homonymies pour cette année."
                            "\n2- Relancez l'attribution des OTPs pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    log_title = f"BUILD OF DATA FOR OTP ATTRIBUTION FOR {year_select}"
    print(f"\n\n{set_bold_txt(log_title)}")

    # Setting files parameters dependent on year selection
    return_tup = _set_otp_year_files_param(master.wf_path, year_select)
    homonyms_file_path, otp_folder_path, otp_file_base = return_tup

    if progress_callback:
        progress_bar_state_init = 10
        progress_callback(progress_bar_state_init)

    # Getting institute parameters
    dpt_label_list = list(master.org_tup[1].keys())

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

                    # Displaying up the status of the OTPs step
                    info_title = "- Information -"
                    info_text = ("Les fichiers pour l'attribution des OTPs "
                                 f"de l'année {year_select} dejà disponibles sont conservés.")
                    messagebox.showinfo(info_title, info_text)
        else:
            os.mkdir(otp_folder_path)
            _add_otp_try(progress_callback)
    else:
        progress_callback(100)

        # Displaying up the status of the OTPs step
        info_title = "- Information -"
        info_text = ("La création des fichiers pour l'attribution des OTPs "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def _set_conso_year_files_params(wf_path, year_select):
    """Sets useful folders and files parameters (path and file name) depending 
    on the selected corpus year for the consolidation of the publications list.

    Args:
        wf_path (path): Full path to working folder.
        year_select (str): Corpus year defined by 4 digits.
    Returns:
        (tup): (The list of set file names (str), \
        The list of the built paths).
    """
    # Setting useful aliases
    otp_folder_alias = bm_pg.ARCHI_YEAR["OTP folder"]
    pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    missing_if_base_alias = bm_pg.ARCHI_IF["missing_if_base"]
    missing_issn_base_alias = bm_pg.ARCHI_IF["missing_issn_base"]

    # Setting useful files names dependent on year select
    pub_list_file =  f'{pub_list_file_base_alias} {year_select}.xlsx'
    missing_if_file = f'{year_select}{missing_if_base_alias}'
    missing_issn_file = f'{year_select}{missing_issn_base_alias}'

    # Setting useful folders paths dependent on year select
    corpus_year_path = wf_path / Path(year_select)
    otp_folder_path = corpus_year_path / Path(otp_folder_alias)
    pub_list_folder_path = corpus_year_path / Path(pub_list_folder_alias)

    # Setting useful files paths dependant on year select
    pub_list_file_path = pub_list_folder_path / Path(pub_list_file)

    # Setting returned lists
    files_list = [pub_list_file, missing_if_file, missing_issn_file]
    paths_list = [otp_folder_path, pub_list_folder_path, pub_list_file_path]

    return files_list, paths_list


def _launch_pub_list_conso_try(master, year_select, progress_callback):
    """Launches building of publications final list.

    This is done through the `built_final_pub_list` 
    function imported from `bmfuncts.consolidate_pub_list` 
    module after check of status of OTPs adding step.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.  
    """

    def _consolidate_pub_list(_progress_callback):
        if os.path.isdir(otp_folder_path) and os.listdir(otp_folder_path):
            _progress_callback(20)
            # Setting the list of useful params values selected by the user
            params_list = [master.institute, master.org_tup, master.wf_path,
                           master.datatype, year_select]

            # Consolidating publications list
            conso_tup = built_final_pub_list(params_list)
            (pub_nb, invalids_nb, split_ratio, if_database_complete) = conso_tup
            _progress_callback(70)
            if bm_pg.LISTES_CONCAT:
                # Concatenating all available publications lists
                _ = concatenate_pub_lists(master.wf_path, master.years_list)
            _progress_callback(100)

            # Displaying the status of the consolidation step of the publications list
            _info_title = "- Information -"
            _info_text = (f"Une liste consolidée de {pub_nb} publications a été créée "
                         f"pour l'année {year_select} dans le dossier :\n\n '{pub_list_folder_path}' "
                         f"\n\nsous le nom :   '{pub_list_file}'."
                         f"\n\nUne liste de {invalids_nb} publications invalides "
                          "a également été créée dans le même dossier."
                         "\n\nLes IFs disponibles ont été automatiquement attribués.")
            if if_database_complete:
                _info_text += ("\n\nLa base de données des facteurs d'impact étant complète, "
                              "les listes des journaux avec IFs ou ISSNs inconnus sont vides.")
            else:
                _info_text += ("\n\nAttention, les listes des journaux avec IFs ou ISSNs inconnus "
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
            _info_text += ("\n\nPar ailleurs, cette liste consolidée des publications "
                          f"a été décomposée à {split_ratio} % "
                          "en trois fichiers disponibles dans le même dossier "
                          "correspondant aux différentes "
                          "classes de documents (les classes n'étant pas exhaustives, "
                          "la décomposition peut être partielle)."
                          "\n\nLa liste des publications invalides a été créée "
                          "dans le même dossier.")
            if bm_pg.LISTES_CONCAT:
                all_years_data_folder = bm_pg.ARCHI_BDD_MULTI_ANNUELLE
                _info_text += ("\n\nEnfin, la concaténation des listes consolidées des publications "
                              "disponibles, a été créée dans le dossier :"
                              f"\n\n '{all_years_data_folder}' "
                              "\n\nsous un nom vous identifiant ainsi que la liste des années "
                              "prises en compte et caractérisé par la date et l'heure de la création.")
            messagebox.showinfo(_info_title, _info_text)

        else:
            _progress_callback(100)

            # Displaying the status of the consolidation step of the publications list
            warning_title = "!!! ATTENTION : fichiers manquants !!!"
            warning_text = ("Les fichiers d'attribution des OTPs "
                            f"de l'année {year_select} ne sont pas disponibles."
                            "\n1- Relancez la création des fichiers d'attribution des OTPs "
                            "pour cette année."
                            "\n2- Relancez la consolidation de la liste des publications "
                            "pour cette année.")
            messagebox.showwarning(warning_title, warning_text)

    log_title = f"BUILD FINAL LIST OF PUBLICATIONS FOR {year_select}"
    print(f"\n\n{set_bold_txt(log_title)}")

    # Setting files parameters dependent on year selection
    files_list, paths_list = _set_conso_year_files_params(master.wf_path, year_select)
    (pub_list_file, missing_if_file, missing_issn_file) = files_list
    otp_folder_path, pub_list_folder_path, pub_list_file_path = paths_list

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

                # Displaying the status of the consolidation step of the publications list
                info_title = "- Information -"
                info_text = ("Le fichier de la liste consolidée des publications "
                             f"de l'année {year_select} dejà disponible est conservé.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)

        # Displaying the status of the consolidation step of the publications list
        info_title = "- Information -"
        info_text = ("La création du fichier de la liste consolidée des publications "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def create_consolidate_corpus(self, master, page_name):
    """Manages creation and use of widgets for corpus consolidation 
    through merge with Institute employees database.

    Useful files parameters are set through the `_set_empl_files_params`
    internal function.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of consolidation page.
    """
    # Internal functions

    def _update_progress(value):
        self.progress_var.set(value)
        self.progress_bar.update_idletasks()
        if value>=100:
            bm_gu.enable_buttons(self.page_buttons_list)


    # ****************************** GENERAL SETTNGS

    # initializing update status of employees data
    self.empl_update_status = False

    # Setting files parameters for employees data
    # independent of year selection
    return_tup = _set_empl_files_params(master.wf_root_path)
    (self.empl_folder_path, self.empl_upd_folder_path,
     self.empl_file_path, self.empl_file_name) = return_tup

    # Creating and setting widgets for page title and exit button
    page_label = bm_gg.PAGES_LABELS[page_name]
    bm_gu.set_page_title(self, master, page_label)
    bm_gu.set_exit_button(self, master)

    # Setting short_name for page key and year key to use in globals
    self.page_key = bm_gg.KEY_CONSO
    self.year_key = bm_gg.KEY_CONSO_YEAR

    # Setting progress bars parameters
    bm_pu.set_progress_bar_params(self, master)

    # Setting steps widgets parameters
    bm_pu.set_steps_widgets_param(self, master)

    # *********************** STEP 0: UPDATE EMPLOYEES DATA
    def _launch_update_employees(progress_callback):
        """Command of the 'empl_update_button' button.        
        """
        # Trying launch of update of employees file
        self.empl_update_status = _launch_update_employees_try(self, master.wf_path,
                                                               progress_callback)
        self.progress_bar.place_forget()

    def _start_update_employees():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_after(empl_update_button, self.progress_bar,
                          dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_update_employees,
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for employees-update
    step_num = 0
    empl_help_button = bm_pu.set_step_help_button(self, step_num)
    empl_update_button = bm_pu.set_step_launch_button(self, step_num,
                                                      _start_update_employees,
                                                      'bellow')


    # ****************************** YEAR SELECTION

    default_year = master.years_list[-1]
    self.variable_years = tk.StringVar(self)
    self.variable_years.set(default_year)
    bm_pu.set_year_select_widgets(self, master)


    # *********************** STEP 1: MERGE AUTHORS-EMPLOYEES
    def _launch_recursive_year_search(progress_callback):
        """Command of the 'merge_button' button.        
        """
        # Getting year selection
        year_select = self.variable_years.get()

        # Trying launch of recursive search for authors in employees file
        _launch_recursive_year_search_try(self, master, year_select, progress_callback)
        self.empl_update_status = False
        self.progress_bar.place_forget()

    def _start_launch_recursive_year_search():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_after(merge_button, self.progress_bar,
                          dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_recursive_year_search,
                         args=(_update_progress,)).start()

    # Setting widgets for authors-employees-merge button
    step_num = 1
    merge_help_button = bm_pu.set_step_help_button(self, step_num)
    merge_button = bm_pu.set_step_launch_button(self, step_num,
                                                _start_launch_recursive_year_search,
                                                'bellow')


    # ******************* STEP 2: HOMONYMS RESOLUTION
    def _launch_resolution_homonymies(progress_callback):
        """Command of the 'homonyms_button' button.
        """
        # Renewing year selection
        year_select = self.variable_years.get()

        # Trying launch creation of file for homonymies resolution
        _launch_resolution_homonymies_try(master, year_select, progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_resolution_homonymies():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_after(homonyms_button, self.progress_bar,
                          dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_resolution_homonymies,
                         args=(_update_progress,)).start()

    # Setting widgets for homonyms-resolution button
    step_num = 2
    homonyms_help_button = bm_pu.set_step_help_button(self, step_num)
    homonyms_button = bm_pu.set_step_launch_button(self, step_num,
                                                   _start_launch_resolution_homonymies,
                                                   'bellow')

    # ******************* STEP 3: OTPs ATTRIBUTION
    def _launch_add_otp(progress_callback):
        """Command of the 'otp_button' button.        
        """

        # Renewing year selection
        year_select = self.variable_years.get()

        # Trying launch creation of files for OTP attribution
        _launch_add_otp_try(master, year_select, progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_add_otp():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_after(otp_button, self.progress_bar,
                          dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_add_otp,
                         args=(_update_progress,)).start()

    # Setting widgets for OTPs attribution button
    step_num = 3
    otp_help_button = bm_pu.set_step_help_button(self, step_num)
    otp_button = bm_pu.set_step_launch_button(self, step_num,
                                              _start_launch_add_otp,
                                              'bellow')

    # ****************** STEP 4: PUBLICATIONS-LIST CONSOLIDATION
    def _launch_pub_list_conso(progress_callback):
        """Command of the 'conso_button' button.
        """
        # Renewing year selection and years
        year_select = self.variable_years.get()

        # Trying launch creation of consolidated publications lists
        _launch_pub_list_conso_try(master, year_select, progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_pub_list_conso():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_after(conso_button, self.progress_bar,
                          dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_pub_list_conso,
                         args=(_update_progress,)).start()

    # Setting widgets for consolidation of publications list
    step_num = 4
    conso_help_button = bm_pu.set_step_help_button(self, step_num)
    conso_button = bm_pu.set_step_launch_button(self, step_num,
                                                _start_launch_pub_list_conso,
                                                'bellow')

    # Setting buttons list for status change
    self.page_buttons_list = [self.years_opt_but,
                              empl_help_button,
                              empl_update_button,
                              merge_help_button,
                              merge_button,
                              homonyms_help_button,
                              homonyms_button,
                              otp_help_button,
                              otp_button,
                              conso_help_button,
                              conso_button]
