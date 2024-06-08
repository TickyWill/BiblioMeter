"""`update_if_page` module allows to update the impact-factors database 
and the consolidated publications lists. """

__all__ = ['create_update_ifs']


# Standard library imports
import os
import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox
from pathlib import Path

# Local imports
import bmgui.gui_globals as gg
import bmfuncts.pub_globals as pg
from bmgui.gui_utils import font_size
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_exit_button
from bmgui.gui_utils import set_page_title
from bmfuncts.config_utils import set_org_params
from bmfuncts.consolidate_pub_list import add_if
from bmfuncts.consolidate_pub_list import concatenate_pub_lists
from bmfuncts.consolidate_pub_list import split_pub_list_by_doc_type
from bmfuncts.save_final_results import save_final_results
from bmfuncts.update_impact_factors import update_inst_if_database


def _launch_update_if_db(institute,
                         org_tup,
                         bibliometer_path,
                         corpus_years_list,
                         pub_list_folder_path):
    """
    """

    # Lancement de la fonction de MAJ base de données des IFs
    ask_title = "- Confirmation de la mise à jour de la base de données des IFs -"
    ask_text  = ("La base de données des IFs va être mise à jour "
                 "avec les nouvelles données disponibles dans les dossiers :"
                 f"\n\n '{pub_list_folder_path}' "
                 f"\n\n des corpus des années \n\n  {corpus_years_list} ."
                 "\n\nCette opération peut prendre quelques secondes."
                 "\nDans l'attente, ne pas fermer 'BiblioMeter'."
                 " \n\nEffectuer la mise à jour ?")
    answer    = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        # Mise à jour de la base de données des IFs
        _, if_years_list = update_inst_if_database(institute, org_tup,
                                                   bibliometer_path, corpus_years_list)
        info_title = "- Information -"
        info_text  = ("La mise à jour de la base de données des IFs a été effectuée "
                      f"pour les années  {if_years_list}."
                      "\n\nLa consolidation des corpus des années "
                      f"\n {corpus_years_list} "
                      "\npeut être lancée.")
        messagebox.showinfo(info_title, info_text)
        update_status = True
    else:
        # Arrêt de la procédure
        info_title = "- Information -"
        info_text  = "La mise à jour de la base de données des IFs est abandonnée."
        messagebox.showwarning(info_title, info_text)
        update_status = False
    return update_status

def _launch_update_pub_if(institute,
                          org_tup,
                          bibliometer_path,
                          datatype,
                          corpus_years_list,
                          pub_list_folder_alias,
                          pub_list_file_base_alias,
                          missing_if_base_alias,
                          missing_issn_base_alias):
    """
    """

    if_database_complete = None
    missing_pub_file_year = None
    for corpus_year in corpus_years_list:
        # Setting corpus dependant paths
        pub_list_file = pub_list_file_base_alias + " " + corpus_year + ".xlsx"
        year_pub_list_folder_path = bibliometer_path / Path(corpus_year) / pub_list_folder_alias
        out_file_path     = year_pub_list_folder_path / Path(pub_list_file)
        missing_if_path   = year_pub_list_folder_path / Path(corpus_year + missing_if_base_alias)
        missing_issn_path = year_pub_list_folder_path / Path(corpus_year + missing_issn_base_alias)

        # Cheking availability of pub_list file of the year
        out_file_status = os.path.exists(out_file_path)
        if out_file_status:
            # Updating Impact Factors and saving new consolidated list of publications
            # this also for saving results files to complete IFs database
            _, if_database_complete = add_if(institute,
                                             org_tup,
                                             bibliometer_path,
                                             out_file_path,
                                             out_file_path,
                                             missing_if_path,
                                             missing_issn_path,
                                             corpus_year)

            # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
            split_pub_list_by_doc_type(institute, org_tup, bibliometer_path, corpus_year)

            # Saving pub list as final result
            status_values = len(pg.RESULTS_TO_SAVE) * [False]
            results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
            results_to_save_dict["pub_lists"] = True
            if_analysis_name = None
            _ = save_final_results(institute, org_tup, bibliometer_path, datatype, corpus_year,
                                   if_analysis_name, results_to_save_dict, verbose = False)

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
            warning_title = "!!! ATTENTION : fichier absent !!!"
            warning_text  = ("La liste consolidée des publications du corpus "
                             f"de l'année {corpus_year} "
                             "\nn'est pas disponible à l'emplacement attendu. "
                             "\n1- Relancer la consolidation annuelle pour ce corpus ;"
                             "\n2- Puis relancez la mise à jour des IFs des listes consolidées.")
            messagebox.showwarning(warning_title, warning_text)
            missing_pub_file_year = corpus_year
            return missing_pub_file_year, if_database_complete
    return missing_pub_file_year, if_database_complete


def create_update_ifs(self, master, page_name, institute, bibliometer_path, datatype):

    """
    Description : function working as a bridge between the BiblioMeter
    App and the functionalities needed for the use of the app

    Uses the following globals :
    - DIC_OUT_PARSING
    - FOLDER_NAMES

    Args : takes only self and bibliometer_path as arguments.
    self is the intense in which PageThree will be created
    bibliometer_path is a type Path, and is the path to where the folders
    organised in a very specific way are stored

    Returns : nothing, it create the page in self
    """

    # Internal functions
    def _launch_update_if_db_try(if_db_update_status):
        if not if_db_update_status:
            # Checking availability of IFs database file
            if_db_file_status = os.path.exists(if_db_path)
            if if_db_file_status:
                print("Update of IFs database launched")
                if_db_update_status = _launch_update_if_db(institute,
                                                           org_tup,
                                                           bibliometer_path,
                                                           master.years_list,
                                                           pub_list_folder_path)
            else:
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
                if_db_update_status = False
        else:
            print("IFs database already updated")

    def _missing_pub_file_year_check():
        if_tup = _launch_update_pub_if(institute,
                                       org_tup,
                                       bibliometer_path,
                                       datatype,
                                       master.years_list,
                                       pub_list_folder_alias,
                                       pub_list_file_base_alias,
                                       missing_if_base_alias,
                                       missing_issn_base_alias)
        missing_pub_file_year, if_database_complete = if_tup[0], if_tup[1]
        if not missing_pub_file_year:
            concatenate_pub_lists(institute, org_tup, bibliometer_path, master.years_list)
            print("Consolidated lists of publications concatenated after IFs update")
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
            info_title = '- Information -'
            info_text  = ("La mise à jour des IFs dans les listes consolidées "
                          "a été interrompue par l'absence "
                          "de la liste consolidée des publications du corpus :"
                          f" {missing_pub_file_year}")
            messagebox.showinfo(info_title, info_text)

    def _launch_update_pub_if_try(if_db_update_status):
        if if_db_update_status:
            print("Update of IFs in consolidated lists of publications launched")
            _missing_pub_file_year_check()
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
                _missing_pub_file_year_check()
            else:
                info_title = '- Information -'
                info_text  = ("La lmise à jour des listes consolidées "
                             "des publications est abandonnée.")
                messagebox.showinfo(info_title, info_text)

    # Setting effective font sizes and positions (numbers are reference values in mm)
    eff_etape_font_size   = font_size(gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)           #14
    eff_launch_font_size  = font_size(gg.REF_ETAPE_FONT_SIZE-1, master.width_sf_min)
    eff_help_font_size    = font_size(gg.REF_ETAPE_FONT_SIZE-2, master.width_sf_min)

    if_db_update_x_pos_px = mm_to_px(10 * master.width_sf_mm,  gg.PPI)
    if_db_update_y_pos_px = mm_to_px(35 * master.height_sf_mm, gg.PPI)
    update_if_label_dx_px = mm_to_px( 0 * master.width_sf_mm,  gg.PPI)
    update_if_label_dy_px = mm_to_px(15 * master.height_sf_mm, gg.PPI)
    launch_dx_px          = mm_to_px( 0 * master.width_sf_mm,  gg.PPI)
    launch_dy_px          = mm_to_px( 5 * master.height_sf_mm, gg.PPI)

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

    # Setting useful paths
    if_root_path = bibliometer_path / Path(if_root_path_alias)
    if_db_path   = if_root_path / Path(if_file_name_alias)
    backup_if_folder_path = bibliometer_path / Path(backup_folder_name_alias)
    pub_list_folder_path  =  bibliometer_path / Path(pub_list_folder_alias)

    # Initializing status of IFs database update
    if_db_update_status = False

    ################## Mise à jour de la base de données des IFs

    ### Titre
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

    ### Explication
    help_label_font = tkFont.Font(family = gg.FONT_NAME,
                                  size = eff_help_font_size)
    help_label = tk.Label(self,
                          text = gg.HELP_ETAPE_5,
                          justify = "left",
                          font = help_label_font)
    place_bellow(if_db_update_label,
                 help_label)

    ### Bouton pour lancer l'étape
    if_db_update_launch_font = tkFont.Font(family = gg.FONT_NAME,
                                           size = eff_launch_font_size)
    if_db_update_launch_button = tk.Button(self,
                                           text = gg.TEXT_MAJ_BDD_IF,
                                           font = if_db_update_launch_font,
                                           command = lambda :
                                           (_launch_update_if_db_try(if_db_update_status)))
    place_bellow(help_label,
                 if_db_update_launch_button,
                 dx = launch_dx_px,
                 dy = launch_dy_px)

    ################## Mise à jour des Ifs dans les listes consolidées

    ### Titre
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

    ### Explication de l'étape
    help_label_font = tkFont.Font(family = gg.FONT_NAME,
                                  size = eff_help_font_size)
    help_label = tk.Label(self,
                          text = gg.HELP_ETAPE_6,
                          justify = "left",
                          font = help_label_font)
    place_bellow(update_if_label,
                 help_label)

    # ** Bouton pour lancer la mise à jour des IFs dans les listes consolidées existantes
    button_update_if_font = tkFont.Font(family = gg.FONT_NAME,
                                        size = eff_launch_font_size)
    button_update_if = tk.Button(self,
                                 text = gg.TEXT_MAJ_PUB_IF,
                                 font = button_update_if_font,
                                 command = lambda :
                                 (_launch_update_pub_if_try(if_db_update_status)))
    place_bellow(help_label,
                 button_update_if,
                 dx = launch_dx_px,
                 dy = launch_dy_px)
