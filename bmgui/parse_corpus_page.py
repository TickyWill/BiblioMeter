""" `parse_corpus_page` module allows to parse the rawdata extracted 
from the external databases and then the concatenation 
and the deduplication of the parsings."""

__all__ = ['create_parsing_concat']


# Standard library imports
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import ttk

# 3rd party imports
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as pg
import bmgui.gui_globals as gg
from bmfuncts.config_utils import set_org_params
from bmfuncts.config_utils import set_user_config
from bmfuncts.useful_functs import read_parsing_dict
from bmfuncts.useful_functs import save_fails_dict
from bmfuncts.useful_functs import save_parsing_dict
from bmgui.gui_utils import disable_buttons
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import existing_corpuses
from bmgui.gui_utils import font_size
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_exit_button
from bmgui.gui_utils import set_page_title


class CheckBoxCorpuses:
    """Displays status of parsing files through Checkbutton tkinter widgets.

    Args:
        year (str): Corpus year defined by 4 digits.
        wos_r (bool): Status of WoS raw-data file.
        wos_p (bool): Status of WoS parsing files.
        scopus_r (bool): Status of Scopus raw-data file.
        scopus_p (bool): Status of Scopus parsing files.
        concat (bool) : Status of concatenation and deduplication files.
    """

    def __init__(self, parent, master, year, wos_r, wos_p,
                 scopus_r, scopus_p, concat):

        self.check_boxes_sep_space = mm_to_px(gg.REF_CHECK_BOXES_SEP_SPACE * master.width_sf_mm,
                                              gg.PPI)
        font = tkFont.Font(family=gg.FONT_NAME, size=font_size(11, master.width_sf_min))
        self.lab = tk.Label(parent,
                            text='Année ' + year,
                            font=font)

        self.wos_r = tk.Checkbutton(parent)
        if wos_r:
            self.wos_r.select()
        self.wos_p = tk.Checkbutton(parent)
        if wos_p:
            self.wos_p.select()
        self.scopus_r = tk.Checkbutton(parent)
        if scopus_r:
            self.scopus_r.select()
        self.scopus_p = tk.Checkbutton(parent)
        if scopus_p:
            self.scopus_p.select()
        self.concat = tk.Checkbutton(parent)
        if concat:
            self.concat.select()

    def place(self, x, y):
        a = self.lab.winfo_reqwidth()
        self.lab.place(x=x-a, y=y, anchor='center')
        self.wos_r.place(x=x+self.check_boxes_sep_space, y=y, anchor='center')
        self.wos_r.config(state='disabled')
        self.wos_p.place(x=x+2*self.check_boxes_sep_space, y=y, anchor='center')
        self.wos_p.config(state='disabled')
        self.scopus_r.place(x=x+3*self.check_boxes_sep_space, y=y, anchor='center')
        self.scopus_r.config(state='disabled')
        self.scopus_p.place(x=x+4*self.check_boxes_sep_space, y=y, anchor='center')
        self.scopus_p.config(state='disabled')
        self.concat.place(x=x+5*self.check_boxes_sep_space, y=y, anchor='center')
        self.concat.config(state='disabled')

    def efface(self):
        for x in (self.lab, self.wos_r, self.wos_p, self.scopus_r, self.scopus_p, self.concat):
            x.place_forget()


def _create_table(self, master, pos_x_init):
    """Creates the column names of the table displaying which files 
    of the parsing step are available in the working folder.

    The positions of the table items are set using the argument 'pos_x_init', 
    and the general properties of tkinter window as 'master' class variables.

    Args:
        pos_x_init (int): The initial horizontal position in pixels to be used \
        for widgets location on the parsing page.
    Note:
        The functions 'font_size' and 'mm_to_px' are imported 
        from the module 'gui_utils' of the package 'bmgui'.        
        The globals 'FONT_NAME' and 'PPI' are imported from the module 'gui_globals'
        of the package 'bmgui'.
    """

    # Internal functions
    def _set_table_item(item_text, item_pos_x):
        item_case = tk.Label(self,
                             text=item_text,
                             font=header_font)
        item_case.place(x=item_pos_x, y=pos_y_ref, anchor='center')
        self.TABLE.append(item_case)

    # Setting specific font properties
    ref_font_size = 11
    local_font_size = font_size(ref_font_size, master.width_sf_min)
    header_font = tkFont.Font(family=gg.FONT_NAME,
                              size=local_font_size)

    # Setting useful x position shift and y position reference in pixels
    pos_x_shift = mm_to_px(25 * master.width_sf_mm, gg.PPI)
    pos_y_ref = mm_to_px(30 * master.height_sf_mm, gg.PPI)

    # Initializing x position in pixels
    pos_x = pos_x_init

    # Mise en page tableau
    item_text = 'Wos\nDonnées brutes'
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)

    item_text = 'Wos\nParsing'
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)

    item_text = 'Scopus\nDonnées brutes'
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)

    item_text = 'Scopus\nParsing'
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)

    item_text = 'Synthèse du\nparsing des BDD'
    pos_x += pos_x_shift
    _set_table_item(item_text, pos_x)


def _update(self, master, bibliometer_path, pos_tup):
    """Refreshes the current state of the files in the 
    working folder using the `_create_table` internal function.

    It also updates the OptionMenu buttons used to select the year.

    Args:
        bibliometer_path (path): The path leading to the working folder.
        pos_tup (tup): (x position (int) for widgets location, \
        y position (int) for widgets location, space value (int) \
        for widgets spacing).
    Note:
        The function 'mm_to_px' is imported from the module 'gui_utils'
        of the package 'bmgui'.
        The functions 'existing_corpuses', 'font_size' and 'place_after'
        are imported from the module 'gui_utils' of the package 'bmgui'.
        The globals FONT_NAME and PPI are imported from the module 'gui_globals'
        of the package 'bmgui'.
    """
    # Setting parameters from args
    pos_x, pos_y, esp_ligne = pos_tup

    # Setting existing corpuses status
    files_status = existing_corpuses(bibliometer_path)
    master.list_corpus_year = files_status[0]
    master.list_wos_rawdata = files_status[1]
    master.list_wos_parsing = files_status[2]
    master.list_scopus_rawdata = files_status[3]
    master.list_scopus_parsing = files_status[4]
    master.list_dedup = files_status[5]

    # ????
    for i, check in enumerate(self.CHECK):
        check.efface()

    for i, annee in enumerate(master.list_corpus_year):
        tmp = CheckBoxCorpuses(self,
                               master,
                               annee,
                               master.list_wos_rawdata[i],
                               master.list_wos_parsing[i],
                               master.list_scopus_rawdata[i],
                               master.list_scopus_parsing[i],
                               master.list_dedup[i])
        tmp.place(x=pos_x,
                  y=i * esp_ligne + pos_y)
        self.CHECK.append(tmp)

    _create_table(self, master, pos_x)


def _launch_parsing(master, corpus_year, database_type,
                    paths_tup, progress_callback):
    """Launches parsing of raw-data of 'database_type' database.

    This is done through `biblio_parser` function imported from 
    3rd party package imported as bp after check of database name 
    and database raw-data availability.

    It saves the resulting parsing files using paths set through 
    `set_user_config` function imported from `bmfuncts.config_utils` 
    module.

    It updates the files status using the internal function `_update`.

    Args:
        corpus_year (str): Corpus year defined by 4 digits.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        paths_tup (tup): (full path to working folder, 
        full path to institute-affiliations file, \
        full path to institutions-types file).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """

    # Internal functions
    def _corpus_parsing(rawdata_path, parsing_path,
                        database_type, progress_callback):
        progress_callback(20)
        if not os.path.exists(parsing_path):
            os.mkdir(parsing_path)
        parsing_tup = bp.biblio_parser(rawdata_path, database_type,
                                       inst_filter_list=None,
                                       country_affiliations_file_path=institute_affil_file_path,
                                       inst_types_file_path=inst_types_file_path)
        parsing_dict, dic_failed = parsing_tup
        progress_callback(80)
        save_parsing_dict(parsing_dict, parsing_path,
                          item_filename_dict, parsing_save_extent)
        progress_callback(90)
        save_fails_dict(dic_failed, parsing_path)
        progress_callback(100)

        articles_number = dic_failed["number of article"]
        info_title = "Information"
        info_text = (f"'Parsing' de '{database_type}' effectué pour l'année {corpus_year}."
                     f"\n\n  Nombre d'articles du corpus : {articles_number}")
        messagebox.showinfo(info_title, info_text)

    # Setting parameters from args
    bibliometer_path, institute_affil_file_path, inst_types_file_path = paths_tup

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, corpus_year, pg.BDD_LIST)
    rawdata_path_dict = config_tup[0]
    parsing_path_dict = config_tup[1]
    item_filename_dict = config_tup[2]

    # Setting useful paths for database 'database_type'
    rawdata_path = rawdata_path_dict[database_type]
    parsing_path = parsing_path_dict[database_type]

    # Setting parsing files extension for saving
    parsing_save_extent = pg.TSV_SAVE_EXTENT
    progress_callback(10)

    # Getting files status for corpus parsing
    if database_type in pg.BDD_LIST:
        rawdata_status = False
        parsing_status = False
        if database_type==bp.WOS:
            rawdata_status = master.list_wos_rawdata[master.list_corpus_year.index(corpus_year)]
            parsing_status = master.list_wos_parsing[master.list_corpus_year.index(corpus_year)]
        if database_type==bp.SCOPUS:
            rawdata_status = master.list_scopus_rawdata[master.list_corpus_year.index(corpus_year)]
            parsing_status = master.list_scopus_parsing[master.list_corpus_year.index(corpus_year)]

        # Asking for confirmation of corpus year to parse
        ask_title = "Confirmation de l'année de traitement"
        ask_text = (f"Une procédure de 'parsing' de '{database_type}' "
                    f"pour l'année {corpus_year} a été lancée."
                    "\n\n Confirmer ce choix ?")
        answer_1 = messagebox.askokcancel(ask_title, ask_text)
        if answer_1:
            if rawdata_status is False:
                progress_callback(100)
                warning_title = "Attention ! Fichier manquant"
                warning_text = (f"Le fichier brut d'extraction de '{database_type}' "
                                f"de l'année {corpus_year} n'est pas disponible."
                                "\nLe 'parsing' correspondant ne peut être construit !"
                                "\n\nAjoutez le fichier à l'emplacement attendu "
                                "et relancez le 'parsing'.")
                messagebox.showwarning(warning_title, warning_text)
            else:
                if not os.path.exists(parsing_path):
                    os.mkdir(parsing_path)
                if parsing_status==1:
                    # Ask to carry on with parsing if already done
                    ask_title = "Confirmation de traitement"
                    ask_text = (f"Le 'parsing' du corpus '{database_type}' "
                                f"de l'année {corpus_year} est déjà disponible."
                                "\n\nReconstruire le 'parsing' ?")
                    answer_2 = messagebox.askokcancel(ask_title, ask_text)
                    if answer_2:
                        # Parse when already parsed and ok for reconstructing parsing
                        _corpus_parsing(rawdata_path, parsing_path,
                                        database_type, progress_callback)
                    else:
                        # Cancel parsing reconstruction
                        progress_callback(100)
                        info_title = "Information"
                        info_text = (f"Le 'parsing' existant du corpus '{database_type}' "
                                     f"de l'année {corpus_year} a été conservé.")
                        messagebox.showinfo(info_title, info_text)
                else:
                    # Parse when not parsed yet
                    _corpus_parsing(rawdata_path, parsing_path,
                                    database_type, progress_callback)
        else:
            progress_callback(100)
            info_title = "Information"
            info_text = "Modifiez vos choix et relancez le 'parsing'."
            messagebox.showinfo(info_title, info_text)

    else:
        progress_callback(100)
        warning_title = "Attention : Erreur sur type de BDD"
        warning_text = (f"Le type de BDD {database_type}"
                        " n'est pas encore pris en compte."
                        "\nLe 'parsing' correspondant ne peut être construit !"
                        "\n\nModifiez le type de BDD sélectionné et relancez le 'parsing'.")
        messagebox.showwarning(warning_title, warning_text)


def _launch_synthese(master, corpus_year, org_tup, datatype,
                     paths_tup, progress_callback):
    """Concatenates and deduplicates the parsing from wos or scopus databases.

    This is done through the functions `concatenate_parsing` 
    and `deduplicate_parsing` imported from 3rd party package 
    imported as bp.

    It checks if all useful files are available in the working folder.

    It saves the resulting parsing files using paths set through 
    `set_user_config` function imported from `bmfuncts.config_utils` 
    module.

    It updates the files status using the internal function `_update`.

    Args:
        corpus_year (str): Corpus year defined by 4 digits.
        org_tup (tup): Contains Institute parameters.
        datatype (str): Data combination type from corpuses databases.
        paths_tup (tup): (full path to working folder, \
        full path to institute-affiliations file, \
        full path to institutions-types file).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """

    # Internal functions
    def _deduplicate_corpus_parsing(progress_callback):
        if not os.path.exists(concat_root_folder):
            os.mkdir(concat_root_folder)
        if not os.path.exists(concat_parsing_path):
            os.mkdir(concat_parsing_path)
        if not os.path.exists(dedup_root_folder):
            os.mkdir(dedup_root_folder)
        if not os.path.exists(dedup_parsing_path):
            os.mkdir(dedup_parsing_path)

        progress_callback(15)

        scopus_parsing_dict = read_parsing_dict(scopus_parsing_path, item_filename_dict,
                                                parsing_save_extent)
        wos_parsing_dict = read_parsing_dict(wos_parsing_path, item_filename_dict,
                                             parsing_save_extent)
        progress_callback(30)
        concat_parsing_dict = bp.concatenate_parsing(scopus_parsing_dict, wos_parsing_dict,
                                                     inst_filter_list=institutions_filter_list)
        progress_callback(50)
        save_parsing_dict(concat_parsing_dict, concat_parsing_path,
                          item_filename_dict, parsing_save_extent)
        progress_callback(60)
        file_path_0 = inst_types_file_path
        file_path_1 = institute_affil_file_path
        dedup_parsing_dict = bp.deduplicate_parsing(concat_parsing_dict,
                                                    norm_inst_status=False,
                                                    inst_types_file_path=file_path_0,
                                                    country_affiliations_file_path=file_path_1)

        synthese_articles_nb = len(dedup_parsing_dict["articles"])
        progress_callback(90)
        save_parsing_dict(dedup_parsing_dict, dedup_parsing_path,
                          item_filename_dict, parsing_save_extent,
                          dedup_infos=(bibliometer_path, datatype, corpus_year))

        progress_callback(100)
        return synthese_articles_nb

    # Setting parameters from args
    bibliometer_path, institute_affil_file_path, inst_types_file_path = paths_tup

    # Setting Institute parameters
    institutions_filter_list = org_tup[3]

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, corpus_year, pg.BDD_LIST)
    parsing_path_dict, item_filename_dict = config_tup[1], config_tup[2]

    # Setting useful paths for database 'database_type'
    scopus_parsing_path = parsing_path_dict["scopus"]
    wos_parsing_path = parsing_path_dict["wos"]
    concat_root_folder = parsing_path_dict["concat_root"]
    concat_parsing_path = parsing_path_dict["concat"]
    dedup_root_folder = parsing_path_dict["dedup_root"]
    dedup_parsing_path = parsing_path_dict["dedup"]

    # Setting parsing files extension for saving
    parsing_save_extent = pg.TSV_SAVE_EXTENT

    # Getting files status for corpus concatenation and deduplication
    wos_parsing_status = master.list_wos_parsing[master.list_corpus_year.index(corpus_year)]
    scopus_parsing_status = master.list_scopus_parsing[master.list_corpus_year.index(corpus_year)]
    dedup_parsing_status = master.list_dedup[master.list_corpus_year.index(corpus_year)]
    progress_callback(10)

    # Asking for confirmation of corpus year to concatenate and deduplicate
    ask_title = "Confirmation de l'année de traitement"
    ask_text = (f"La synthèse pour l'année {corpus_year} a été lancée."
                "\n\nConfirmer ce choix ?")
    answer_1 = messagebox.askokcancel(ask_title, ask_text)
    if answer_1:

        # Checking availability of parsing files
        if not wos_parsing_status:
            progress_callback(100)
            warning_title = "Attention ! Fichiers manquants"
            warning_text = ("Le 'parsing' de 'wos' "
                            f"de l'année {corpus_year} n'est pas disponible."
                            "\nLa synthèse correspondante ne peut pas encore être construite !"
                            "\n\n-1 Lancez le 'parsing' manquant;"
                            "\n-2 Relancez la synthèse.")
            messagebox.showwarning(warning_title, warning_text)

        if not scopus_parsing_status:
            progress_callback(100)
            warning_title = "Attention ! Fichiers manquants"
            warning_text = ("Le 'parsing' de 'scopus' "
                            f"de l'année {corpus_year} n'est pas disponible."
                            "\nLa synthèse correspondante ne peut pas encore être construite !"
                            "\n\n-1 Lancez le 'parsing' manquant;"
                            "\n-2 Relancez la synthèse.")
            messagebox.showwarning(warning_title, warning_text)

        if wos_parsing_status and scopus_parsing_status:
            if dedup_parsing_status:
                # Ask to carry on with concatenation and deduplication if already available
                ask_title = "Reconstruction de la synthèse"
                ask_text = (f"La synthèse pour l'année {corpus_year} est déjà disponible."
                            "\n\nReconstruire la synthèse ?")
                answer_2 = messagebox.askokcancel(ask_title, ask_text)
                if answer_2:
                    synthese_articles_nb = _deduplicate_corpus_parsing(progress_callback)
                    info_title = "Information"
                    info_text = (f"La synthèse pour l'année {corpus_year} a été reconstruite."
                                 f"\n\nNombre d'articles de synthèse : {synthese_articles_nb}.")
                    messagebox.showinfo(info_title, info_text)
                else:
                    progress_callback(100)
                    info_title = "Information"
                    info_text = "La synthèse dejà disponible est conservée."
                    messagebox.showinfo(info_title, info_text)
            else:
                _deduplicate_corpus_parsing(progress_callback)
                info_title = "Information"
                info_text = ("La construction de la synthèse pour "
                             f"l'année {corpus_year} est terminée.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "Information"
        info_text = f"La synthèse pour l'année {corpus_year} est annulée."
        messagebox.showinfo(info_title, info_text)


def create_parsing_concat(self, master, page_name, institute, bibliometer_path, datatype):
    """Manages creation and use of widgets for corpus parsing.

    This is done through the internal functions  `_launch_parsing`, 
    `_launch_synthese` and `_update`.

    Args:
        page_name (str): Name of parsing page.
        institute (str): Institute name.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """
    # Internal functions
    def _launch_parsing_try(progress_callback):
        paths_tup = (bibliometer_path,
                     institute_affil_file_path,
                     inst_types_file_path)
        parsing_year = self.var_year_pc_1.get()
        parsing_bdd = var_bdd_pc_1.get()
        _launch_parsing(master, parsing_year, parsing_bdd,
                        paths_tup, progress_callback)
        progress_bar.place_forget()

    def _launch_synthese_try(progress_callback):
        synthese_year = self.var_year_pc_2.get()
        _launch_synthese(master, synthese_year,
                         org_tup, datatype,
                         paths_tup, progress_callback)
        progress_bar.place_forget()

    def _update_progress(value):
        progress_var.set(value)
        progress_bar.update_idletasks()
        if value>=100:
            enable_buttons(parse_buttons_list)

    def _start_launch_parsing_try():
        disable_buttons(parse_buttons_list)
        place_bellow(parsing_launch_button,
                     progress_bar, dx=-80, dy=15)
        progress_var.set(0)
        threading.Thread(target=_launch_parsing_try,
                         args=(_update_progress,)).start()
        # update files status
        _update(self, master, bibliometer_path, pos_tup)

    def _start_launch_synthese_try():
        disable_buttons(parse_buttons_list)
        place_after(synthese_launch_button,
                    progress_bar, dx=40, dy=0)
        progress_var.set(0)
        threading.Thread(target=_launch_synthese_try,
                         args=(_update_progress,)).start()
        # update files status
        _update(self, master, bibliometer_path, pos_tup)


    # Setting useful local variables for positions modification (globals to create ??)
    # numbers are reference values in mm for reference screen
    w_sf_mm = master.width_sf_mm
    h_sf_mm = master.height_sf_mm
    w_sf_min = master.width_sf_min
    position_selon_x_check = mm_to_px(70 * w_sf_mm, gg.PPI)
    position_selon_y_check = mm_to_px(40 * h_sf_mm, gg.PPI)
    espace_entre_ligne_check = mm_to_px(10 * h_sf_mm, gg.PPI)
    labels_x_pos = mm_to_px(10 * w_sf_mm, gg.PPI)
    labels_y_space = mm_to_px(10 * h_sf_mm, gg.PPI)
    status_label_y_pos = mm_to_px(25 * h_sf_mm, gg.PPI)
    parsing_label_y_pos = mm_to_px(107 * h_sf_mm, gg.PPI)
    synthese_label_y_pos = mm_to_px(135 * h_sf_mm, gg.PPI)
    status_button_x_pos = mm_to_px(148 * w_sf_mm, gg.PPI)
    status_button_y_pos = mm_to_px(98 * h_sf_mm, gg.PPI)
    dx_year_select = mm_to_px(1 * w_sf_mm, gg.PPI)
    dy_year_select = mm_to_px(1 * h_sf_mm, gg.PPI)
    dx_bdd_select = mm_to_px(12 * w_sf_mm, gg.PPI)
    dy_bdd_select = mm_to_px(1 * h_sf_mm, gg.PPI)
    dx_launch = mm_to_px(15 * w_sf_mm, gg.PPI)
    dy_launch = mm_to_px(0.2 * h_sf_mm, gg.PPI)
    progress_bar_length_px = mm_to_px(50 * w_sf_mm, gg.PPI)
    eff_labels_font_size = font_size(14, w_sf_min)
    eff_select_font_size = font_size(12, w_sf_min)
    eff_buttons_font_size = font_size(11, w_sf_min)

    year_x_pos = labels_x_pos
    parsing_year_y_pos = parsing_label_y_pos + labels_y_space
    synthese_year_y_pos = synthese_label_y_pos + labels_y_space
    pos_tup = (position_selon_x_check,
               position_selon_y_check,
               espace_entre_ligne_check)

    # Setting useful local variables for default selection items in selection lists
    default_year = master.list_corpus_year[-1]
    default_bdd = pg.BDD_LIST[0]

    # Getting institute parameters
    org_tup = set_org_params(institute, bibliometer_path)

    # Setting useful aliases
    institutions_folder_alias = pg.ARCHI_INSTITUTIONS["root"]
    inst_aff_file_base_alias = pg.ARCHI_INSTITUTIONS["institute_affil_base"]
    inst_types_file_base_alias = pg.ARCHI_INSTITUTIONS["inst_types_base"]

    # Setting useful file names and paths for Institute affiliations
    institute_affil_file = institute + "_" + inst_aff_file_base_alias
    inst_types_file = institute + "_" + inst_types_file_base_alias
    institutions_folder_path = bibliometer_path / Path(institutions_folder_alias)
    institute_affil_file_path = institutions_folder_path / Path(institute_affil_file)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file)
    paths_tup = (bibliometer_path,
                 institute_affil_file_path,
                 inst_types_file_path)

    # Creating and setting widgets for page title and exit button
    set_page_title(self, master, page_name, institute, datatype)
    set_exit_button(self, master)

    # Initializing progress bar widget
    progress_var = tk.IntVar()  # Variable to keep track of the progress bar value
    progress_bar = ttk.Progressbar(self,
                                   orient="horizontal",
                                   length=progress_bar_length_px,
                                   mode="determinate",
                                   variable=progress_var)

    # **************** Zone Statut des fichiers de "parsing"
    # Liste des checkbox des corpuses
    self.CHECK = []
    self.TABLE = []

    font_statut = tkFont.Font(family=gg.FONT_NAME,
                              size=eff_labels_font_size,
                              weight='bold')
    label_statut = tk.Label(self,
                            text=gg.TEXT_STATUT,
                            font=font_statut)
    label_statut.place(x=labels_x_pos,
                       y=status_label_y_pos,
                       anchor="nw")

    # **************** Bouton pour actualiser la zone de stockage
    font_exist_button = tkFont.Font(family=gg.FONT_NAME,
                                    size=eff_buttons_font_size)
    exist_button = tk.Button(self,
                             text=gg.TEXT_UPDATE_STATUS,
                             font=font_exist_button,
                             command=lambda: _update(self,
                                                     master,
                                                     bibliometer_path,
                                                     pos_tup))
    gg.GUI_BUTTONS.append(exist_button)
    exist_button.place(x=status_button_x_pos,
                       y=status_button_y_pos,
                       anchor='n')

    # **************** Zone Construction des fichiers de "parsing" par BDD
    font_parsing = tkFont.Font(family=gg.FONT_NAME,
                               size=eff_labels_font_size,
                               weight='bold')
    label_parsing = tk.Label(self,
                             text=gg.TEXT_PARSING,
                             font=font_parsing)
    label_parsing.place(x=labels_x_pos,
                        y=parsing_label_y_pos, anchor="nw")

    # Choix de l'année
    font_year_pc_1 = tkFont.Font(family=gg.FONT_NAME,
                                 size=eff_select_font_size)
    self.label_year_pc_1 = tk.Label(self,
                                    text=gg.TEXT_YEAR_PC,
                                    font=font_year_pc_1)
    self.label_year_pc_1.place(x=year_x_pos,
                               y=parsing_year_y_pos,
                               anchor="nw")

    self.var_year_pc_1 = tk.StringVar(self)
    self.var_year_pc_1.set(default_year)
    self.om_year_pc_1 = tk.OptionMenu(self,
                                      self.var_year_pc_1,
                                      *master.list_corpus_year)
    font_year_pc_1 = tkFont.Font(family=gg.FONT_NAME,
                                 size=eff_buttons_font_size)
    self.om_year_pc_1.config(font=font_year_pc_1)
    gg.GUI_BUTTONS.append(self.om_year_pc_1)
    place_after(self.label_year_pc_1,
                self.om_year_pc_1,
                dx=+ dx_year_select,
                dy=- dy_year_select)

    # Choix de la BDD
    font_bdd_pc_1 = tkFont.Font(family=gg.FONT_NAME,
                                size=eff_select_font_size)
    label_bdd_pc_1 = tk.Label(self,
                              text=gg.TEXT_BDD_PC,
                              font =font_bdd_pc_1)
    place_after(self.om_year_pc_1,
                label_bdd_pc_1,
                dx=dx_bdd_select,
                dy=dy_bdd_select)

    var_bdd_pc_1 = tk.StringVar(self)
    var_bdd_pc_1.set(default_bdd)
    om_bdd_pc_1 = tk.OptionMenu(self,
                                var_bdd_pc_1,
                                *pg.BDD_LIST)
    font_bdd_pc_1 = tkFont.Font(family=gg.FONT_NAME,
                                size=eff_buttons_font_size)
    om_bdd_pc_1.config(font=font_bdd_pc_1)
    place_after(label_bdd_pc_1,
                om_bdd_pc_1,
                dx=+ dx_year_select,
                dy=- dy_year_select)

    # Lancement du parsing
    parsing_launch_font = tkFont.Font(family=gg.FONT_NAME,
                                      size=eff_buttons_font_size)
    parsing_launch_button = tk.Button(self,
                                      text=gg.TEXT_LAUNCH_PARSING,
                                      font=parsing_launch_font,
                                      command=_start_launch_parsing_try)
    gg.GUI_BUTTONS.append(parsing_launch_button)
    place_after(om_bdd_pc_1,
                parsing_launch_button,
                dx=dx_launch,
                dy=dy_launch)

    # **************** Zone Synthèse des fichiers de parsing de toutes les BDD
    font_synthese = tkFont.Font(family=gg.FONT_NAME,
                                size=eff_labels_font_size,
                                weight='bold')
    label_synthese = tk.Label(self,
                              text =gg.TEXT_SYNTHESE,
                              font=font_synthese)
    label_synthese.place(x=labels_x_pos,
                         y=synthese_label_y_pos,
                         anchor="nw")

    # Choix de l'année
    font_year_pc_2 = tkFont.Font(family=gg.FONT_NAME,
                                 size=eff_select_font_size)
    self.label_year_pc_2 = tk.Label(self,
                                    text=gg.TEXT_YEAR_PC,
                                    font=font_year_pc_2)
    self.label_year_pc_2.place(x=year_x_pos,
                               y=synthese_year_y_pos,
                               anchor="nw")

    self.var_year_pc_2 = tk.StringVar(self)
    self.var_year_pc_2.set(master.list_corpus_year[-1])
    self.om_year_pc_2 = tk.OptionMenu(self,
                                      self.var_year_pc_2,
                                      *master.list_corpus_year)
    font_year_pc_2 = tkFont.Font(family=gg.FONT_NAME,
                                 size=eff_buttons_font_size)
    self.om_year_pc_2.config(font=font_year_pc_2)
    gg.GUI_BUTTONS.append(self.om_year_pc_2)
    place_after(self.label_year_pc_2,
                self.om_year_pc_2,
                dx=+ dx_year_select,
                dy=- dy_year_select)

    # Lancement de la synthèse
    synthese_launch_font = tkFont.Font(family=gg.FONT_NAME,
                                       size=eff_buttons_font_size)
    synthese_launch_button = tk.Button(self,
                                     text=gg.TEXT_LAUNCH_SYNTHESE,
                                     font=synthese_launch_font,
                                     command=_start_launch_synthese_try)
    gg.GUI_BUTTONS.append(synthese_launch_button)
    place_after(self.om_year_pc_2,
                synthese_launch_button,
                dx=dx_launch,
                dy=dy_launch)

    # **************** Placement de CHECKBOXCORPUSES :
    _update(self, master, bibliometer_path, pos_tup)

    # Setting buttons list for status change
    parse_buttons_list = [exist_button,
                          self.om_year_pc_1,
                          om_bdd_pc_1,
                          self.om_year_pc_2,
                          parsing_launch_button,
                          synthese_launch_button]
