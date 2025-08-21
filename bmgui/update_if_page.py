"""`update_if_page` module allows to update the impact-factors database 
and the publications final lists."""

__all__ = ['create_update_ifs']

# Standard library imports
import os
import threading
from pathlib import Path
from tkinter import messagebox

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu
import bmgui.pages_utils as bm_pu
from bmfuncts.add_ifs import add_if
from bmfuncts.config_utils import set_org_params
from bmfuncts.consolidate_pub_list import concatenate_pub_lists
from bmfuncts.consolidate_pub_list import split_pub_list_by_doc_type
from bmfuncts.save_final_results import save_final_results
from bmfuncts.update_impact_factors import update_inst_if_database


def _set_if_files_params(institute, org_tup, wf_path):
    """Sets IFs specific file and folder 
    
    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
    Returns:
        (tup): publications-lists folder name, \
        base for building names of publications-list files, \
        base for building names of missing-IFs files, \
        name for building names of missing-ISSNs files.
    """
    # Setting useful aliases
    all_years_folder_alias = bm_pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    pub_list_folder_alias = bm_pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    backup_folder_name_alias = bm_pg.ARCHI_BACKUP["root"]
    if_root_path_alias = bm_pg.ARCHI_IF["root"]
    if_file_name_alias = bm_pg.ARCHI_IF["all IF"]
    missing_if_base_alias = bm_pg.ARCHI_IF["missing_if_base"]
    missing_issn_base_alias = bm_pg.ARCHI_IF["missing_issn_base"]
    inst_if_file_name_alias = bm_pg.ARCHI_IF["institute_if_all_years"]

    if_file_name = if_file_name_alias
    if_db_status = org_tup[5]
    if if_db_status:
        if_file_name = institute + inst_if_file_name_alias

    # Setting useful paths
    backup_if_folder_path = wf_path / Path(backup_folder_name_alias)
    if_root_path = wf_path / Path(if_root_path_alias)
    if_db_path = if_root_path / Path(if_file_name)

    files_list = [if_file_name,
                  pub_list_file_base_alias,
                  missing_if_base_alias,
                  missing_issn_base_alias]
    folders_list = [pub_list_folder_alias, all_years_folder_alias]
    files_paths_list = [if_db_path]
    folders_paths_list = [backup_if_folder_path, if_root_path]
    return files_list, folders_list, files_paths_list, folders_paths_list


def _launch_update_if_db(institute, org_tup, wf_path,
                         corpus_years_list,
                         progress_callback):
    """Launches updating impact-factors database of the Institute.

    This is done through the `update_inst_if_database` function 
    imported from `bmfuncts.update_impact_factors` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        corpus_years_list (list): List of available corpus years \
        (each item defined by a string of 4 digits).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    Returns:
        (bool): Status of impact-factors database.    
    """
    # Setting files parameters
    return_tup = _set_if_files_params(institute, org_tup, wf_path)
    files_list, folders_list, files_paths_list, folders_paths_list = return_tup
    if_file_name = files_list[0]
    pub_list_folder = folders_list[0]
    if_db_path = files_paths_list[0]
    backup_if_folder_path, if_root_path = folders_paths_list

    # Checking availability of IFs database file
    if_db_file_status = os.path.exists(if_db_path)
    if if_db_file_status:
        progress_callback(10)
        # Lancement de la fonction de MAJ base de données des IFs
        ask_title = "- Confirmation de la mise à jour de la base de données des IFs -"
        ask_text = ("La base de données des IFs va être mise à jour "
                    "avec les nouvelles données disponibles dans les dossiers :"
                    f"\n\n '{pub_list_folder}' "
                    f"\n\n des corpus des années \n\n  {corpus_years_list} ."
                    "\n\nCette opération peut prendre quelques secondes."
                    "\nDans l'attente, ne pas fermer l'application."
                    " \n\nEffectuer la mise à jour ?")
        answer = messagebox.askokcancel(ask_title, ask_text)
        if answer:
            progress_callback(15)
            # Mise à jour de la base de données des IFs
            _, if_years_list = update_inst_if_database(institute, org_tup,
                                                       wf_path,
                                                       corpus_years_list,
                                                       progress_callback)
            print("IFs database updated")
            progress_callback(100)
            info_title = "- Information -"
            info_text = ("La mise à jour de la base de données des IFs a été effectuée "
                         f"pour les années  {if_years_list}."
                         "\n\nLa consolidation des corpus des années "
                         f"\n {corpus_years_list} "
                         "\npeut être lancée.")
            messagebox.showinfo(info_title, info_text)
            update_status = True
        else:
            progress_callback(100)
            print("IFs database update cancelled")
            # Arrêt de la procédure
            info_title = "- Information -"
            info_text = "La mise à jour de la base de données des IFs est abandonnée."
            messagebox.showwarning(info_title, info_text)
            update_status = False
    else:
        progress_callback(100)
        warning_title = "!!! ATTENTION : fichier absent !!!"
        warning_text = (f"Le fichier {if_file_name} de la base de données des IFs "
                        "\nn'est pas disponible à l'emplacement attendu. "
                        "\nL'utilisation de la dernière sauvegarde de secours du dossier "
                        f"\n {backup_if_folder_path} "
                        "\nest possible : "
                        "\n1- Copier le fichier de secours dans le dossier : "
                        f"\n {if_root_path} ;"
                        "\n2- Puis relancez la mise à jour de la base de données des IFs.")
        messagebox.showwarning(warning_title, warning_text)
        update_status = False
        print("Update of IFs database aborted because of IFs database file missing")
    return update_status


def _missing_pub_file_year_check(wf_path, corpus_years_list, if_tup,
                                 all_years_list_folder, progress_callback):
    """Launches updating impact-factors database of the Institute.

    This is done through the `update_inst_if_database` function 
    imported from `bmfuncts.update_impact_factors` module.

    Args:
        wf_path (path): Full path to working folder.
        corpus_years_list (list): List of available corpus years \
        (each item defined by a string of 4 digits).
        if_tup (tup): (year of the missing publications list (str),\
        status of IFs database (bool), unused parameter).
        all_years_list_folder (str): The folder name where \
        concatenation of all-years publications lists is saved.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    Returns:
        (bool): Status of impact-factors database.    
    """
    missing_pub_file_year, if_database_complete, _ = if_tup
    if not missing_pub_file_year:
        print("IFs updated in all consolidated lists of publications")
        if bm_pg.LISTES_CONCAT:
            _ = concatenate_pub_lists(wf_path, corpus_years_list)
            print("Consolidated lists of publications concatenated after IFs update")
        progress_callback(100)
        info_title = '- Information -'
        info_text = ("La mise à jour des IFs dans les listes consolidées "
                     "des publications des corpus :"
                     f"\n\n   {corpus_years_list}"
                     "\n\na été effectuée avec une base de données des IFs ")
        if if_database_complete:
            info_text += "complète."
        else:
            info_text += "incomplète."
        info_text += ("\n\nDe plus, chaque liste consolidée des publications "
                      "a été décomposée en trois fichiers disponibles "
                      "dans le même dossier correspondant "
                      "aux différentes classes de documents "
                      "(les classes n'étant pas exhaustives, "
                      "la décomposition peut être partielle).")           
        if bm_pg.LISTES_CONCAT:
            info_text += ("\n\nEnfin, la concaténation des listes consolidées "
                          "de publications disponibles, à été créée dans le dossier :"
                          f"\n\n '{all_years_list_folder}' "
                          "\n\nsous un nom vous identifiant "
                          "et caractérisé par la date et l'heure de sa création "
                          "ainsi que la liste des années prises en compte.")
        messagebox.showinfo(info_title, info_text)

    else:
        progress_callback(100)
        print("IFs updated in some consolidated lists of publications"
              "but interrupted because of missing of a consolidated list file")
        info_title = '- Information -'
        info_text = ("La mise à jour des IFs a été effectuée dans une partie des listes "
                     "consolidées existantes mais a été interrompue par l'absence "
                     "de la liste consolidée des publications du corpus :"
                     f" {missing_pub_file_year}")
        messagebox.showinfo(info_title, info_text)


def _set_year_files_params(wf_path, corpus_year, names_tup):
    # Setting files parameters from args
    (pub_list_folder,
     pub_list_file_base,
     missing_if_base,
     missing_issn_base) = names_tup

    # Setting corpus dependant paths
    pub_list_file = pub_list_file_base + " " + corpus_year + ".xlsx"
    year_pub_list_folder_path = wf_path / Path(corpus_year) / pub_list_folder
    pub_list_file_path = year_pub_list_folder_path / Path(pub_list_file)
    missing_if_path = year_pub_list_folder_path / Path(corpus_year + missing_if_base)
    missing_issn_path = year_pub_list_folder_path / Path(corpus_year + missing_issn_base)
    paths_tup = (year_pub_list_folder_path, pub_list_file_path, missing_if_path, missing_issn_path)
    return paths_tup


def _update_pub_if(institute, org_tup, wf_path, datatype,
                   corpus_years_list, progress_callback):
    """Updates impact factors of publications final list of the corpuses years.

    This is done through the `add_if` function imported from 
    `bmfuncts.consolidate_pub_list` module after check of availability 
    of the corresponding file of the publications list.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_years_list (list): List of available corpus years \
        (each item defined by a string of 4 digits).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    Returns:
        (bool): Status of impact-factors database. 
    """
    # Setting files parameters
    return_tup = _set_if_files_params(institute, org_tup, wf_path)
    files_list, folders_list, _, _ = return_tup
    [_,
     pub_list_file_base,
     missing_if_base,
     missing_issn_base] = files_list
    pub_list_folder = folders_list[0]
    all_years_list_folder = folders_list[1]
    names_tup = (pub_list_folder, pub_list_file_base,
                 missing_if_base, missing_issn_base)
    progress_callback(5)
    progress_bar_state = 5
    progress_bar_loop_progression = 70 // len(corpus_years_list)

    if_database_complete = None
    missing_pub_file_year = None
    for corpus_year in corpus_years_list:
        # Setting corpus dependant paths
        return_tup = _set_year_files_params(wf_path, corpus_year, names_tup)
        (year_pub_list_folder_path, pub_list_file_path,
         missing_if_path, missing_issn_path) = return_tup

        # Checking availability of publications-list file of the year
        out_file_status = os.path.exists(pub_list_file_path)
        if out_file_status:

            # Updating Impact Factors and saving new consolidated list of publications
            # this also for saving results files to complete IFs database
            paths_tup = (pub_list_file_path, pub_list_file_path,
                         missing_if_path, missing_issn_path)
            _, if_database_complete = add_if(institute, org_tup, wf_path,
                                             paths_tup, corpus_year)

            # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
            split_pub_list_by_doc_type(institute, org_tup, wf_path, corpus_year)

            # Saving pub list as final result
            status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
            results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
            results_to_save_dict["pub_lists"] = True
            if_analysis_name = None
            _ = save_final_results(institute, org_tup, wf_path, datatype, corpus_year,
                                   if_analysis_name, results_to_save_dict, verbose=False)
            # Updating progress bar state
            progress_bar_state += progress_bar_loop_progression
            progress_callback(progress_bar_state)

            if not if_database_complete:
                info_title = "- Information -"
                info_text = ("La base de données des facteurs d'impact étant incomplète, "
                             "les listes des journaux avec IFs ou ISSNs inconnus "
                             f"ont été créées dans le dossier \n\n '{year_pub_list_folder_path}' "
                             "\n\nsous les noms :"
                             f"\n\n '{missing_if_path}' "
                             f"\n\n '{missing_issn_path}' "
                             "\n\n Ces fichiers peuvent être modifiés pour compléter "
                             "la base de donnée des IFs :"
                             "\n\n1- Ouvrez chacun de ces fichiers, "
                             "\n2- Complétez manuellement les IFs inconnus ou les ISSNs "
                             "et IFs inconnus, selon le fichier,"
                             "\n3- Puis sauvegardez les fichiers sous le même nom."
                             "\n\nChaque fois que ces compléments sont apportés, "
                             "la base de données des IFs doit être mise à jour, "
                             "ainsi que toutes les listes consolidées des publications existantes."
                             "\n\nCependant, la mise à jour va être poursuivie avec la base "
                             "de données des IFs incomplète.")
                messagebox.showinfo(info_title, info_text)
        else:
            progress_bar_state = 100
            warning_title = "!!! ATTENTION : fichier absent !!!"
            warning_text = ("La liste consolidée des publications du corpus "
                            f"de l'année {corpus_year} "
                            "\nn'est pas disponible à l'emplacement attendu. "
                            "\n1- Relancer la consolidation annuelle pour ce corpus ;"
                            "\n2- Puis relancez la mise à jour des IFs des listes consolidées.")
            messagebox.showwarning(warning_title, warning_text)
            missing_pub_file_year = corpus_year
        progress_callback(progress_bar_state)
    if_tup = missing_pub_file_year, if_database_complete, progress_bar_state
    _missing_pub_file_year_check(wf_path, corpus_years_list, if_tup,
                                 all_years_list_folder, progress_callback)


def _launch_update_pub_if(institute, org_tup, wf_path, datatype, if_db_update_status,
                          corpus_years_list, progress_callback):
    """Launches updating impact factors of publications final list of the corpuses years.

    This is done through the `_update_pub_if` internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        if_db_update_status (bool) : True if IFs database has been \
        updated.
        corpus_years_list (list): List of available corpus years \
        (each item defined by a string of 4 digits).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.  
    """
    if if_db_update_status:
        _update_pub_if(institute, org_tup, wf_path, datatype,
                       corpus_years_list, progress_callback)
        progress_callback(100)
    else:
        # Confirmation du lancement de la fonction de MAJ des IFs
        # dans les listes consolidées sans MAJ de la base de données des IFs
        ask_title = ("- Confirmation de la mise à jour des IFs "
                     "dans les listes consolidées des publications -")
        ask_text = ("La base de données des IFs n'a pas été préalablement mise à jour."
                    "\n\nLa mise à jour des IFs dans les listes consolidées "
                    f"des corpus des années \n\n  {corpus_years_list} "
                    "\n\nva être effectuée avec la version de la base de données "
                    "des IFs qui est disponible."
                    "\n\nCette opération peut prendre quelques secondes."
                    "\nDans l'attente, ne pas fermer l'application."
                    " \n\nEffectuer la mise à jour ?")
        answer = messagebox.askokcancel(ask_title, ask_text)
        if answer:
            _update_pub_if(institute, org_tup, wf_path, datatype,
                           corpus_years_list, progress_callback)
            progress_callback(100)
        else:
            progress_callback(100)
            print("IFs update in consolidated lists of publications cancelled")
            info_title = '- Information -'
            info_text = ("La mise à jour des listes consolidées "
                         "des publications est abandonnée.")
            messagebox.showinfo(info_title, info_text)


def create_update_ifs(self, master, page_name, institute, wf_path, datatype):
    """Manages creation and use of widgets for impact factors update.

    This is done through the internal functions `_launch_update_if_db` 
    and `_launch_update_pub_if`.

    Args:
        self (instance): Instance of the calling page.
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
            bm_gu.enable_buttons(self.page_buttons_list)


    # ****************************** GENERAL SETTNGS

    # Initializing update status of IFs database
    self.if_db_update_status = False

    # Creating and setting widgets for page title and exit button
    page_label = bm_gg.PAGES_LABELS[page_name]
    bm_gu.set_page_title(self, master, page_label, institute, datatype)
    bm_gu.set_exit_button(self, master)

    # Getting institute parameters
    wf_root_path = wf_path.parent
    org_tup = set_org_params(institute, wf_root_path)

    # Setting short_name for page key to use in globals
    self.page_key = bm_gg.KEY_IF

    # Setting progress bars parameters
    bm_pu.set_progress_bar_params(self, master)

    # Setting steps widgets parameters
    bm_pu.set_steps_widgets_param(self, master)

    # *********************** STEP 0: UPDATE IF DATABASE
    def _launch_update_if_db_try(progress_callback):
        """Command of the 'if_db_update_launch_button' button.        
        """
        print("\nUpdating IFs database...")
        if not self.if_db_update_status:
            self.if_db_update_status = _launch_update_if_db(institute, org_tup,
                                                            wf_path,
                                                            master.years_list,
                                                            progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_update_if_db_try():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_bellow(if_db_update_button, self.progress_bar,
                           dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_update_if_db_try,
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for IF-database update
    step_num = 0
    if_db_help_button = bm_pu.set_step_help_button(self, step_num)
    if_db_update_button = bm_pu.set_step_launch_button(self, step_num,
                                                       _start_launch_update_if_db_try,
                                                       'bellow')

    # *********************** STEP 1: UPDATE IF IN CONSOLIDATED LISTS OF PUBLICATIONS

    def _launch_update_pub_if_try(progress_callback):
        print("\nUpdating IFs in consolidated lists of publications...")
        _launch_update_pub_if(institute, org_tup, wf_path, datatype,
                              self.if_db_update_status, master.years_list,
                              progress_callback)

        # Re-initializing status of IFs database update
        self.if_db_update_status = False
        self.progress_bar.place_forget()

    def _start_launch_update_pub_if_try():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_bellow(pub_if_update_button, self.progress_bar,
                           dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_update_pub_if_try,#
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for IF_update in publications lists
    step_num = 1
    pub_if_help_button = bm_pu.set_step_help_button(self, step_num)
    pub_if_update_button = bm_pu.set_step_launch_button(self, step_num,
                                                        _start_launch_update_pub_if_try,
                                                        'bellow')
    # Setting buttons list for status change
    self.page_buttons_list = [if_db_help_button,
                              if_db_update_button,
                              pub_if_help_button,
                              pub_if_update_button]
