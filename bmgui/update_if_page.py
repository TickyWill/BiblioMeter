"""`update_if_page` module allows to update the impact-factors database 
and the publications final lists."""

__all__ = ['create_update_ifs']

# Standard library imports
import os
import threading
import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path

# Local imports
import bmgui.gui_globals as gg
import bmfuncts.pub_globals as pg
from bmgui.gui_utils import disable_buttons, enable_buttons
from bmgui.gui_utils import font_size
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_exit_button
from bmgui.gui_utils import set_page_title
from bmfuncts.config_utils import set_org_params
from bmfuncts.consolidate_pub_list import add_if
from bmfuncts.consolidate_pub_list import concatenate_pub_lists
from bmfuncts.consolidate_pub_list import split_pub_list_by_doc_type
from bmfuncts.save_final_results import save_final_results
from bmfuncts.update_impact_factors import update_inst_if_database


def _launch_update_if_db(institute, org_tup, bibliometer_path,
                         pub_list_folder_alias, corpus_years_list,
                         progress_callback):
    """Launches updating impact-factors database of the Institute.

    This is done through the `update_inst_if_database` function 
    imported from `bmfuncts.update_impact_factors` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        pub_list_folder_alias (str): Publications-lists folder name.
        corpus_years_list (list): List of available corpus years \
        (each item defined by a string of 4 digits).
        progress_callback (function): Function for updating \ProgressBar tkinter widget status. 
    Returns:
        (bool): Status of impact-factors database.    
    """

    # Lancement de la fonction de MAJ base de données des IFs
    ask_title = "- Confirmation de la mise à jour de la base de données des IFs -"
    ask_text  = ("La base de données des IFs va être mise à jour "
                 "avec les nouvelles données disponibles dans les dossiers :"
                 f"\n\n '{pub_list_folder_alias}' "
                 f"\n\n des corpus des années \n\n  {corpus_years_list} ."
                 "\n\nCette opération peut prendre quelques secondes."
                 "\nDans l'attente, ne pas fermer 'BiblioMeter'."
                 " \n\nEffectuer la mise à jour ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        progress_callback(15)
        # Mise à jour de la base de données des IFs
        _, if_years_list = update_inst_if_database(institute, org_tup,
                                                   bibliometer_path,
                                                   corpus_years_list,
                                                   progress_callback)
        print("IFs database updated")
        info_title = "- Information -"
        info_text  = ("La mise à jour de la base de données des IFs a été effectuée "
                      f"pour les années  {if_years_list}."
                      "\n\nLa consolidation des corpus des années "
                      f"\n {corpus_years_list} "
                      "\npeut être lancée.")
        messagebox.showinfo(info_title, info_text)
        update_status = True
    else:
        progress_callback(100)
        print("IFs database update dropped")
        # Arrêt de la procédure
        info_title = "- Information -"
        info_text  = "La mise à jour de la base de données des IFs est abandonnée."
        messagebox.showwarning(info_title, info_text)
        update_status = False
    return update_status

def _launch_update_pub_if(institute, org_tup, bibliometer_path, datatype,
                          aliases_tup, corpus_years_list, progress_callback):
    """Launches updating impact factors of publications final list of the year.

    This is done through the `add_if` function imported from 
    `bmfuncts.consolidate_pub_list` module after check of availability 
    of the corresponding file of the publications list.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        aliases_tup (tup): (publications-lists folder name, \
        base for building names of publications-list files, \
        base for building names of missing-IFs files, \
        name for building names of missing-ISSNs files).
        corpus_years_list (list): List of available corpus years \
        (each item defined by a string of 4 digits).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status. 
    Returns:
        (tup): (year of missing publications file (string of 4 digits), \
        completion status of impact-factors database (bool), \
        progress-bar status (int)).    
    """

    # Setting parameters from args
    (pub_list_folder_alias,
     pub_list_file_base_alias,
     missing_if_base_alias,
     missing_issn_base_alias) = aliases_tup
    
    progress_callback(5)
    progress_bar_state = 5
    progress_bar_loop_progression = 70 // len(corpus_years_list)    
    if_database_complete = None
    missing_pub_file_year = None
    for corpus_year in corpus_years_list:

        # Setting corpus dependant paths
        pub_list_file = pub_list_file_base_alias + " " + corpus_year + ".xlsx"
        year_pub_list_folder_path = bibliometer_path / Path(corpus_year) / pub_list_folder_alias
        out_file_path     = year_pub_list_folder_path / Path(pub_list_file)
        missing_if_path   = year_pub_list_folder_path / Path(corpus_year + missing_if_base_alias)
        missing_issn_path = year_pub_list_folder_path / Path(corpus_year + missing_issn_base_alias)

        # Checking availability of publications-list file of the year
        out_file_status = os.path.exists(out_file_path)
        if out_file_status:

            # Updating Impact Factors and saving new consolidated list of publications
            # this also for saving results files to complete IFs database
            paths_tup = (out_file_path, out_file_path,
                         missing_if_path, missing_issn_path)
            _, if_database_complete = add_if(institute, org_tup, bibliometer_path,
                                             paths_tup, corpus_year)

            # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
            split_pub_list_by_doc_type(institute, org_tup, bibliometer_path, corpus_year)

            # Saving pub list as final result
            status_values = len(pg.RESULTS_TO_SAVE) * [False]
            results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
            results_to_save_dict["pub_lists"] = True
            if_analysis_name = None
            _ = save_final_results(institute, org_tup, bibliometer_path, datatype, corpus_year,
                                   if_analysis_name, results_to_save_dict, verbose = False)
            # Updating progress bar state
            progress_bar_state += progress_bar_loop_progression
            if not if_database_complete:
                info_title = "- Information -"
                info_text  = ("La base de données des facteurs d'impact étant incomplète, "
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
            warning_text  = ("La liste consolidée des publications du corpus "
                             f"de l'année {corpus_year} "
                             "\nn'est pas disponible à l'emplacement attendu. "
                             "\n1- Relancer la consolidation annuelle pour ce corpus ;"
                             "\n2- Puis relancez la mise à jour des IFs des listes consolidées.")
            messagebox.showwarning(warning_title, warning_text)
            missing_pub_file_year = corpus_year
        progress_callback(progress_bar_state)
    return missing_pub_file_year, if_database_complete, progress_bar_state


def create_update_ifs(self, master, page_name, institute, bibliometer_path, datatype):
    """Manages creation and use of widgets for impact factors update.

    This is done through the internal functions `_launch_update_if_db` 
    and `_launch_update_pub_if`.

    Args:
        self (instense): Instense where consolidation page will be created.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of consolidation page.
        institute (str): Institute name.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """

    # Internal functions
    def _launch_update_if_db_try(progress_callback):
        print("\nUpdate of IFs database launched")
        new_if_db_update_status = if_db_update_status
        if not if_db_update_status:
            # Checking availability of IFs database file
            if_db_file_status = os.path.exists(if_db_path)
            if if_db_file_status:
                progress_callback(10)
                new_if_db_update_status = _launch_update_if_db(institute,
                                                               org_tup,
                                                               bibliometer_path,
                                                               pub_list_folder_alias,
                                                               master.years_list,
                                                               progress_callback)
            else:
                progress_callback(100)
                warning_title = "!!! ATTENTION : fichier absent !!!"
                warning_text  = (f"Le fichier {if_file_name_alias} de la base de données des IFs "
                                 "\nn'est pas disponible à l'emplacement attendu. "
                                 "\nL'utilisation de la dernière sauvegarde de secours du dossier "
                                 f"\n {backup_if_folder_path} "
                                 "\nest possible : "
                                 "\n1- Copier le fichier de secours dans le dossier : "
                                 f"\n {if_root_path} ;"
                                 "\n2- Puis relancez la mise à jour de la base de données des IFs.")
                messagebox.showwarning(warning_title, warning_text)
                new_if_db_update_status = False
                print("Update of IFs database aborted because of IFs database file missing")

        # Setting status of IFs database update
        globals()['if_db_update_status'] = new_if_db_update_status
        progress_bar.place_forget()

    def _missing_pub_file_year_check(progress_callback):
        aliases_tup = (pub_list_folder_alias, pub_list_file_base_alias,
                       missing_if_base_alias, missing_issn_base_alias)                                       
        if_tup = _launch_update_pub_if(institute, org_tup, bibliometer_path, datatype,
                                       aliases_tup, master.years_list, progress_callback)
        missing_pub_file_year, if_database_complete, progress_bar_state = if_tup
        if not missing_pub_file_year:
            print("IFs updated in all consolidated lists of publications")
            concatenate_pub_lists(institute, org_tup, bibliometer_path, master.years_list)
            print("Consolidated lists of publications concatenated after IFs update")
            progress_callback(100)
            info_title = '- Information -'
            info_text  = ("La mise à jour des IFs dans les listes consolidées "
                          "des publications des corpus :"
                          f"\n\n   {master.years_list}"
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
                          "la décomposition peut être partielle)."
                          "\n\nEnfin, la concaténation des listes consolidées "
                          "de publications disponibles, à été créée dans le dossier :"
                          f"\n\n '{bdd_multi_annuelle_folder_alias}' "
                          "\n\nsous un nom vous identifiant "
                          "et caractérisé par la date et l'heure de sa création "
                          "ainsi que la liste des années prises en compte.")
            messagebox.showinfo(info_title, info_text)

        else:
            progress_callback(100)
            print("IFs updated in some consolidated lists of publications"
                  "but interrupted because of missing of a consolidated list file")
            info_title = '- Information -'
            info_text  = ("La mise à jour des IFs a été effectuée dans une partie des listes "
                          "consolidées existantes mais a été interrompue par l'absence "
                          "de la liste consolidée des publications du corpus :"
                          f" {missing_pub_file_year}")
            messagebox.showinfo(info_title, info_text)

    def _launch_update_pub_if_try(progress_callback):
        print("\nUpdate of IFs in consolidated lists of publications launched")
        if if_db_update_status:
            _missing_pub_file_year_check(progress_callback)
        else:
            # Confirmation du lancement de la fonction de MAJ des IFs
            # dans les listes consolidées sans MAJ de la base de données des IFs
            ask_title = ("- Confirmation de la mise à jour des IFs "
                         "dans les listes consolidées des publications -")
            ask_text  = ("La base de données des IFs n'a pas été préalablement mise à jour."
                         "\n\nLa mise à jour des IFs dans les listes consolidées "
                         f"des corpus des années \n\n  {master.years_list} "
                         "\n\nva être effectuée avec la version de la base de données "
                         "des IFs qui est disponible."
                         "\n\nCette opération peut prendre quelques secondes."
                         "\nDans l'attente, ne pas fermer 'BiblioMeter'."
                         " \n\nEffectuer la mise à jour ?")
            answer    = messagebox.askokcancel(ask_title, ask_text)
            if answer:
                _missing_pub_file_year_check(progress_callback)
            else:
                progress_callback(100)
                print("IFs update in consolidated lists of publications dropped")
                info_title = '- Information -'
                info_text  = ("La mise à jour des listes consolidées "
                              "des publications est abandonnée.")
                messagebox.showinfo(info_title, info_text)
        # Re-initializing status of IFs database update
        globals()['if_db_update_status'] = False
        progress_bar.place_forget()               

    def _update_progress(value):
        progress_var.set(value)
        progress_bar.update_idletasks()
        if value >= 100:
            enable_buttons(update_if_buttons_list)

    def _except_hook(args):
        messagebox.showwarning("Error", args)
        progress_var.set(0)
        enable_buttons(update_if_buttons_list)

    def _start_launch_update_if_db_try():
        disable_buttons(update_if_buttons_list)
        place_after(if_db_update_launch_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_update_if_db_try,
                         args=(_update_progress,)).start()

    def _start_launch_update_pub_if_try():
        disable_buttons(update_if_buttons_list)
        place_after(pub_if_update_launch_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_update_pub_if_try,
                         args=(_update_progress,)).start()


    # Setting effective font sizes and positions (numbers are reference values in mm)
    eff_etape_font_size   = font_size(gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)           #14
    eff_launch_font_size  = font_size(gg.REF_ETAPE_FONT_SIZE-1, master.width_sf_min)
    eff_help_font_size    = font_size(gg.REF_ETAPE_FONT_SIZE-2, master.width_sf_min)

    if_db_update_x_pos_px = mm_to_px(10 * master.width_sf_mm,  gg.PPI)
    if_db_update_y_pos_px = mm_to_px(35 * master.height_sf_mm, gg.PPI)
    update_if_label_dx_px = mm_to_px( 0 * master.width_sf_mm,  gg.PPI)
    update_if_label_dy_px = mm_to_px(15 * master.height_sf_mm, gg.PPI)
    launch_dx_px = mm_to_px( 0 * master.width_sf_mm,  gg.PPI)
    launch_dy_px = mm_to_px( 5 * master.height_sf_mm, gg.PPI)    
    progress_bar_length_px = mm_to_px(75 * master.width_sf_mm, gg.PPI)
    progress_bar_dx = 40

    # Setting common attributs
    etape_label_format = 'left'
    etape_underline    = -1

    # Setting useful aliases
    bdd_multi_annuelle_folder_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    pub_list_folder_alias           = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias        = pg.ARCHI_YEAR["pub list file name base"]
    backup_folder_name_alias        = pg.ARCHI_BACKUP["root"]
    if_root_path_alias              = pg.ARCHI_IF["root"]
    if_file_name_alias              = pg.ARCHI_IF["all IF"]
    missing_if_base_alias           = pg.ARCHI_IF["missing_if_base"]
    missing_issn_base_alias         = pg.ARCHI_IF["missing_issn_base"]
    inst_if_file_name_alias         = pg.ARCHI_IF["institute_if_all_years"]

    # Gettting institute parameters
    org_tup = set_org_params(institute, bibliometer_path)
    if_db_status = org_tup[5]
    if if_db_status:
        if_file_name_alias = institute + inst_if_file_name_alias

    # Creating and setting widgets for page title and exit button
    set_page_title(self, master, page_name, institute, datatype)
    set_exit_button(self, master)
    
    # Handling exception
    threading.excepthook = _except_hook

    # Initializing progress bar widget
    progress_var = tk.IntVar()  # Variable to keep track of the progress bar value
    progress_bar = ttk.Progressbar(self,
                                   orient="horizontal",
                                   length=progress_bar_length_px,
                                   mode="determinate",
                                   variable=progress_var)

    # Setting useful paths
    if_root_path = bibliometer_path / Path(if_root_path_alias)
    if_db_path   = if_root_path / Path(if_file_name_alias)
    backup_if_folder_path = bibliometer_path / Path(backup_folder_name_alias)

    # Initializing status of IFs database update
    if_db_update_status = False

    # **************** Mise à jour de la base de données des IFs

    # ** Titre
    if_db_update_font = tkFont.Font(family = gg.FONT_NAME,
                                 size = eff_etape_font_size,
                                 weight = 'bold')
    if_db_update_label = tk.Label(self,
                                  text = gg.TEXT_ETAPE_5,
                                  justify = etape_label_format,
                                  font = if_db_update_font,
                                  underline = etape_underline)

    if_db_update_label.place(x = if_db_update_x_pos_px,
                             y = if_db_update_y_pos_px)

    # ** Explication
    help_label_font = tkFont.Font(family = gg.FONT_NAME,
                                  size = eff_help_font_size)
    help_label = tk.Label(self,
                          text = gg.HELP_ETAPE_5,
                          justify = "left",
                          font = help_label_font)
    place_bellow(if_db_update_label,
                 help_label)

    # ** Bouton pour lancer l'étape
    if_db_update_launch_font = tkFont.Font(family = gg.FONT_NAME,
                                           size = eff_launch_font_size)
    if_db_update_launch_button = tk.Button(self,
                                           text = gg.TEXT_MAJ_BDD_IF,
                                           font = if_db_update_launch_font,
                                           command = _start_launch_update_if_db_try)
    place_bellow(help_label,
                 if_db_update_launch_button,
                 dx = launch_dx_px,
                 dy = launch_dy_px)

    # **************** Mise à jour des Ifs dans les listes consolidées

    # ** Titre
    update_if_label_font = tkFont.Font(family = gg.FONT_NAME,
                                       size = eff_etape_font_size,
                                       weight = 'bold')
    update_if_label = tk.Label(self,
                               text = gg.TEXT_ETAPE_6,
                               justify = "left",
                               font = update_if_label_font)
    place_bellow(if_db_update_launch_button,
                 update_if_label,
                 dx = update_if_label_dx_px,
                 dy = update_if_label_dy_px)

    # ** Explication de l'étape
    help_label_font = tkFont.Font(family = gg.FONT_NAME,
                                  size = eff_help_font_size)
    help_label = tk.Label(self,
                          text = gg.HELP_ETAPE_6,
                          justify = "left",
                          font = help_label_font)
    place_bellow(update_if_label,
                 help_label)

    # ** Bouton pour lancer la mise à jour des IFs dans les listes consolidées existantes
    pub_if_update_launch_button_font = tkFont.Font(family = gg.FONT_NAME,
                                                   size = eff_launch_font_size)
    pub_if_update_launch_button = tk.Button(self,
                                 text = gg.TEXT_MAJ_PUB_IF,
                                 font = pub_if_update_launch_button_font,
                                 command = _start_launch_update_pub_if_try)
    place_bellow(help_label,
                 pub_if_update_launch_button,
                 dx = launch_dx_px,
                 dy = launch_dy_px)
    
    # Setting buttons list for status change
    update_if_buttons_list = [if_db_update_launch_button,
                              pub_if_update_launch_button]
