""" `parse_corpus_page` module allows to parse the rawdata extracted 
from the external databases and then the concatenation 
and the deduplication of the parsings."""

__all__ = ['create_parsing_concat']


# Standard library imports
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

# 3rd party imports
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu
import bmgui.pages_utils as bm_pu
from bmfuncts.config_utils import set_user_config
from bmfuncts.correct_parsing import build_and_save_unknown_country_data
from bmfuncts.correct_parsing import correct_parsing
from bmfuncts.correct_parsing import set_parse_inst_params
from bmfuncts.save_final_results import save_fails_dict
from bmfuncts.save_final_results import save_parsing_dict
from bmfuncts.useful_functs import compute_dedup_articles_number
from bmfuncts.useful_functs import read_parsing_dict


class CheckBoxCorpuses:
    """Displays status of parsing files through Checkbutton tkinter widgets.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        year (str): Corpus year defined by 4 digits.
        items_status (dict): Availability of raw data, parsing data \
        and deduplicated data (keys: type of data (str); values: status (bool)).
        col_space (int): The space value (int) for boxes columns spacing. 
    """

    def __init__(self, parent, master, year, items_status, col_space):

        def _set_item_status(_self, _item):
            _self.boxes_dict[_item] = tk.Checkbutton(parent)
            if items_status[_item]:
                _self.boxes_dict[_item].select()

        self.check_boxes_sep_space = col_space
        table_header_font = bm_gu.set_table_header_font(master)
        self.lab = tk.Label(parent, text=year, font=table_header_font)
        self.boxes_dict = {}
        for item in items_status.keys():
            _set_item_status(self, item)

    def boxes_place(self, box_x_pos_init, box_y_pos, items_status):
        """Places the checkboxes for displaying files status."""
        box_x_pos = box_x_pos_init
        a = self.lab.winfo_reqwidth()
        self.lab.place(x=box_x_pos-a, y=box_y_pos, anchor='center')
        for item in items_status.keys():
            box_x_pos += self.check_boxes_sep_space
            self.boxes_dict[item].place(x=box_x_pos, y=box_y_pos,
                                        anchor='center')
            self.boxes_dict[item].config(state='disabled')

    def efface(self):
        """Erases the checkboxes of the files status."""
        self.lab.place_forget()
        for value in self.boxes_dict.values():
            value.place_forget()


def _create_table(self, master, x_pos_init):
    """Creates the column names of the table displaying which files 
    of the parsing step are available in the working folder.

    The positions of the table items are set using the argument 'x_pos_init', 
    and the general properties of tkinter window as 'master' class variables.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
        x_pos_init (int): The horizontal position in pixels to be used \
        for the first widget location on the parsing page.
    Note:
        The functions 'set_table_header_font' and 'set_item_pos' are imported 
        from the module 'gui_utils' of the package 'bmgui'.
    """
    # Internal functions
    def _set_table_item(_item_text, item_x_pos):
        item_box = tk.Label(self,
                            text=_item_text,
                            font=table_header_font)
        item_box.place(x=item_x_pos, y=y_pos, anchor='center')
        self.TABLE.append(item_box)

    # Setting specific font properties
    table_header_font = bm_gu.set_table_header_font(master)

    # Setting useful x position shift and y position reference
    x_shift = bm_gu.set_item_pos(master, bm_gg.BOX_TABLE_POS_DICT['x_shift'], 0)
    y_pos = bm_gu.set_item_pos(master, bm_gg.BOX_TABLE_POS_DICT['y_pos'], 1)

    # Initializing x position in pixels
    x_pos = x_pos_init

    # Setting table items
    for _, item_text in bm_gg.BOX_TABLE_COLS_DICT.items():
        x_pos += x_shift
        _set_table_item(item_text, x_pos)


def _set_box_pos_params(master):
    """Sets the x-axis and y-axis positions of top boxes and separation 
    of boxes lines in pixels.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
    Returns:
        (tuple): ((x-axis position (int) for top-boxes location, \
        y-axis position (int) for boxes location), \
        (space value (int) for boxes columns spacing, space value (int) \
        for boxes lines spacing)).
    """
    # Setting check box positions
    box_pos_tup = bm_gu.set_pos_tup_px(master, bm_gg.BOX_POS_TUP)
    box_dpos_tup = bm_gu.set_pos_tup_px(master, bm_gg.BOX_DPOS_TUP)
    return box_pos_tup, box_dpos_tup


def _update_status(self, master, box_pos_params):
    """Refreshes the current state of the files in the 
    working folder using the `_create_table` internal function.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
        box_pos_params (tup): ((x-axis position (int) for top-boxes location, \
        y-axis position (int) for boxes location), \
        (space value (int) for boxes columns spacing, space value (int) \
        for boxes lines spacing)).
    """
    # Setting check box positions
    box_pos_tup, box_dpos_tup = box_pos_params
    x_pos_init, y_pos_init = box_pos_tup
    col_space, line_space = box_dpos_tup
    box_x_pos_init = x_pos_init

    # Clearing all check boxes
    for _, check in enumerate(self.CHECK):
        check.efface()

    # Setting existing corpuses status
    files_status = bm_gu.existing_corpuses(master.wf_path)
    master.list_corpus_year = files_status[0]
    master.list_wos_rawdata = files_status[1]
    master.list_wos_parsing = files_status[2]
    master.list_scopus_rawdata = files_status[3]
    master.list_scopus_parsing = files_status[4]
    master.list_dedup = files_status[5]

    for year_idx, year in enumerate(master.list_corpus_year):
        items_status = {'wos_r'   : master.list_wos_rawdata[year_idx],
                        'wos_p'   : master.list_wos_parsing[year_idx],
                        'scopus_r': master.list_scopus_rawdata[year_idx],
                        'scopus_p': master.list_scopus_parsing[year_idx],
                        'dedup'   : master.list_dedup[year_idx]
                       }
        tmp = CheckBoxCorpuses(self, master, year, items_status, col_space)
        box_y_pos = y_pos_init + year_idx * line_space
        tmp.boxes_place(box_x_pos_init, box_y_pos, items_status)
        self.CHECK.append(tmp)

    _create_table(self, master, x_pos_init)


def _get_parse_data_status(master, database_type, corpus_year):
    rawdata_status = False
    parsing_status = False
    if database_type==bp.WOS:
        rawdata_status = master.list_wos_rawdata[master.list_corpus_year.index(corpus_year)]
        parsing_status = master.list_wos_parsing[master.list_corpus_year.index(corpus_year)]
    if database_type==bp.SCOPUS:
        rawdata_status = master.list_scopus_rawdata[master.list_corpus_year.index(corpus_year)]
        parsing_status = master.list_scopus_parsing[master.list_corpus_year.index(corpus_year)]
    return rawdata_status, parsing_status


def _get_dedup_data_status(master, corpus_year):
    wos_parse_status = _get_parse_data_status(master, bp.WOS, corpus_year)[1]
    scopus_parse_status = _get_parse_data_status(master, bp.SCOPUS, corpus_year)[1]
    dedup_parse_status = master.list_dedup[master.list_corpus_year.index(corpus_year)]
    dedup_status_tup = (wos_parse_status, scopus_parse_status, dedup_parse_status)
    return dedup_status_tup


def _launch_parsing(master, corpus_year, database_type,
                    inst_paths_list, progress_callback):
    """Launches parsing of raw-data of 'database_type' database.

    This is done through `biblio_parser` function imported from 
    3rd party package imported as bp after check of database name 
    and database raw-data availability. 
    It saves the resulting parsing files using paths set through 
    `set_user_config` function imported from `bmfuncts.config_utils` 
    module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        corpus_year (str): Corpus year defined by 4 digits.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        inst_paths_list (list): Composed of the full path to institute-affiliations \
        file and of the full path to institutions-types file.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """
    # Internal functions
    def _corpus_parsing(raw_data_path, _parsing_path,
                        _database_type, _progress_callback):
        parsing_tup = bp.biblio_parser(raw_data_path, _database_type,
                                       inst_filter_list=None,
                                       country_affiliations_file_path=inst_paths_list[0],
                                       inst_types_file_path=inst_paths_list[1])
        parsing_dict, dic_failed = parsing_tup
        _progress_callback(80)
        save_parsing_dict(parsing_dict, _parsing_path,
                          item_filename_dict, parsing_save_extent)
        _progress_callback(90)
        save_fails_dict(dic_failed, _parsing_path)
        _progress_callback(95)

        # Building the data for unknown country correction by the user
        unkown_countries_empty = build_and_save_unknown_country_data(parsing_dict,
                                                                     _parsing_path,
                                                                     bp.UNKNOWN_COUNTRY,
                                                                    _database_type,
                                                                     corpus_year)
        _progress_callback(100)

        articles_number = dic_failed["number of article"]
        _info_title = "Information"
        _info_text = (f"'Parsing' de '{_database_type}' effectué pour l'année {corpus_year}."
                      f"\n\n  Nombre d'articles du corpus : {articles_number}")
        if not unkown_countries_empty:
            _info_text += ("\n\nATTENTION : Des adresses d'auteurs ne comportent pas de pays."
                           "\nPour les définir :"
                           f"\n\n - Ouvrez le fichier :     {bm_pg.ARCHI_YEAR['unknown countries file']}"
                           f"\n  qui a été créé dans le dossier :"
                           f"\n    {_parsing_path}"
                           "\n\n - Indiquez le pays correct dans la colonne nommée 'Country' ;"
                           "\n - Sauvegardez le fichier ;"
                           "\n - Puis, poursuivez vos traitements sans aucune autre action.")
        messagebox.showinfo(_info_title, _info_text)

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(master.wf_path, corpus_year, bm_pg.BDD_LIST)
    rawdata_path_dict, parsing_path_dict, item_filename_dict = config_tup[0:3]

    # Setting parsing files extension for saving
    parsing_save_extent = bm_pg.TSV_SAVE_EXTENT

    # Setting dialog for parsing corpus
    if database_type in bm_pg.BDD_LIST:

        # Setting useful paths for database 'database_type'
        rawdata_path = rawdata_path_dict[database_type]
        parsing_path = parsing_path_dict[database_type]

        # Getting files status for corpus parsing
        rawdata_status, parsing_status = _get_parse_data_status(master, database_type,
                                                                corpus_year)
        progress_callback(20)

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


def _launch_dedup(master, corpus_year, inst_paths_list, progress_callback):
    """Concatenates and deduplicates the parsing from wos or scopus databases.

    This is done through the functions `concatenate_parsing` 
    and `deduplicate_parsing` imported from 3rd party package 
    imported as bp.

    It checks if all useful files are available in the working folder. 
    It saves the resulting parsing files using paths set through 
    `set_user_config` function imported from `bmfuncts.config_utils` 
    module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        corpus_year (str): Corpus year defined by 4 digits.
        inst_paths_list (list): Composed of the full path to institute-affiliations \
        file and of the full path to institutions-types file.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """
    # Internal functions
        
    def _deduplicate_corpus_parsing(_progress_callback):
        scopus_parsing_dict = read_parsing_dict(scopus_parse_path, item_filename_dict,
                                                parsing_save_extent)
        correct_status = correct_parsing(master.institute, master.wf_path, scopus_parse_path,
                                         scopus_parsing_dict, item_filename_dict, bp.UNKNOWN_COUNTRY)
        if correct_status:
            scopus_parsing_dict = read_parsing_dict(scopus_parse_path, item_filename_dict,
                                                    parsing_save_extent)
        wos_parsing_dict = read_parsing_dict(wos_parse_path, item_filename_dict,
                                             parsing_save_extent)
        correct_status = correct_parsing(master.institute, master.wf_path, wos_parse_path,
                                         wos_parsing_dict, item_filename_dict, bp.UNKNOWN_COUNTRY)
        if correct_status:
            wos_parsing_dict = read_parsing_dict(wos_parse_path, item_filename_dict,
                                                 parsing_save_extent)
        _progress_callback(15)
        if bm_pg.FIRST_BDD==bp.SCOPUS:
            concat_parsing_dict = bp.concatenate_parsing(scopus_parsing_dict, wos_parsing_dict,
                                                         inst_filter_list=master.org_tup[3])
        else:
            concat_parsing_dict = bp.concatenate_parsing(wos_parsing_dict, scopus_parsing_dict,
                                                         inst_filter_list=master.org_tup[3])
        _progress_callback(25)
        save_parsing_dict(concat_parsing_dict, concat_path,
                          item_filename_dict, parsing_save_extent)
        _progress_callback(30)
        dedup_parsing_dict = bp.deduplicate_parsing(concat_parsing_dict,
                                                    norm_inst_status=False,
                                                    inst_types_file_path=inst_paths_list[0],
                                                    country_affiliations_file_path=inst_paths_list[1])
        _dedup_articles_nb_tup = compute_dedup_articles_number(master.org_tup, dedup_parsing_dict)
        _progress_callback(90)
        save_parsing_dict(dedup_parsing_dict, dedup_path,
                          item_filename_dict, parsing_save_extent,
                          dedup_infos=(master.wf_path, master.datatype, corpus_year))
        _progress_callback(100)
        return _dedup_articles_nb_tup

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(master.wf_path, corpus_year, bm_pg.BDD_LIST)
    parsing_path_dict, item_filename_dict = config_tup[1], config_tup[2]

    # Setting useful paths for corpus deduplication
    scopus_parse_path, wos_parse_path = parsing_path_dict["scopus"], parsing_path_dict["wos"]
    concat_path, dedup_path = parsing_path_dict["concat"], parsing_path_dict["dedup"]

    # Getting files status for corpus concatenation and deduplication
    dedup_status_tup = _get_dedup_data_status(master, corpus_year)
    wos_parse_status, scopus_parse_status, dedup_parse_status = dedup_status_tup

    # Setting parsing files extension for saving
    parsing_save_extent = bm_pg.TSV_SAVE_EXTENT
    progress_callback(10)

    # Asking for confirmation of corpus year to concatenate and deduplicate
    ask_title = "Confirmation de l'année de traitement"
    ask_text = (f"La synthèse pour l'année {corpus_year} a été lancée."
                "\n\nConfirmer ce choix ?")
    answer_1 = messagebox.askokcancel(ask_title, ask_text)
    if answer_1:
        # Checking availability of parsing files
        if not wos_parse_status:
            progress_callback(100)
            warning_title = "Attention ! Fichiers manquants"
            warning_text = ("Le 'parsing' de 'wos' "
                            f"de l'année {corpus_year} n'est pas disponible."
                            "\nLa synthèse correspondante ne peut pas encore être construite !"
                            "\n\n-1 Lancez le 'parsing' manquant ;"
                            "\n-2 Relancez la synthèse.")
            messagebox.showwarning(warning_title, warning_text)

        if not scopus_parse_status:
            progress_callback(100)
            warning_title = "Attention ! Fichiers manquants"
            warning_text = ("Le 'parsing' de 'scopus' "
                            f"de l'année {corpus_year} n'est pas disponible."
                            "\nLa synthèse correspondante ne peut pas encore être construite !"
                            "\n\n-1 Lancez le 'parsing' manquant ;"
                            "\n-2 Relancez la synthèse.")
            messagebox.showwarning(warning_title, warning_text)

        if wos_parse_status and scopus_parse_status:
            if dedup_parse_status:
                # Ask to carry on with concatenation and deduplication if already available
                ask_title = "Reconstruction de la synthèse"
                ask_text = (f"La synthèse pour l'année {corpus_year} est déjà disponible."
                            "\n\nReconstruire la synthèse ?")
                answer_2 = messagebox.askokcancel(ask_title, ask_text)
                if answer_2:
                    return_tup = _deduplicate_corpus_parsing(progress_callback)
                    dedup_articles_nb, dedup_institute_articles_nb = return_tup
                    info_title = "Information"
                    info_text = (f"La synthèse pour l'année {corpus_year} a été reconstruite."
                                 f"\n\nNombre d'articles de synthèse : {dedup_articles_nb}."
                                 f"\n\ndont {dedup_institute_articles_nb} du {master.institute}.")
                    messagebox.showinfo(info_title, info_text)
                else:
                    progress_callback(100)
                    info_title = "Information"
                    info_text = "La synthèse dejà disponible est conservée."
                    messagebox.showinfo(info_title, info_text)
            else:
                return_tup = _deduplicate_corpus_parsing(progress_callback)
                dedup_articles_nb, dedup_institute_articles_nb = return_tup
                info_title = "Information"
                info_text = (f"La synthèse pour l'année {corpus_year} a été construite."
                             f"\n\nNombre d'articles de synthèse : {dedup_articles_nb}."
                             f"\n\ndont {dedup_institute_articles_nb} du {master.institute}.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "Information"
        info_text = f"La synthèse pour l'année {corpus_year} est abandonnée."
        messagebox.showinfo(info_title, info_text)


def create_parsing_concat(self, master, page_name):
    """Manages creation and use of widgets for corpus parsing.

    This is done through the internal functions  `_launch_parsing`, 
    `_launch_dedup` and `_update_status`.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of parsing page.
    """
    # Internal functions

    def _update_progress(value):
        self.progress_var.set(value)
        self.progress_bar.update_idletasks()
        if value>=100:
            bm_gu.enable_buttons(self.page_buttons_list)


    # ****************************** GENERAL SETTNGS

    # Setting institutions files paths
    _, full_inst_paths_list = set_parse_inst_params(master.institute, master.wf_path)
    inst_paths_list = full_inst_paths_list[0:2]

    # Creating and setting widgets for page title and exit button
    page_label = bm_gg.PAGES_LABELS[page_name]
    bm_gu.set_page_title(self, master, page_label)
    bm_gu.set_exit_button(self, master)

    # Setting page key and page year
    self.page_key = bm_gg.KEY_PARSE
    self.parse_key = bm_gg.KEY_PARSE
    self.dedup_key = bm_gg.KEY_DEDUP
    self.year_key = bm_gg.KEY_PARSE_YEAR

    # Setting progress bars parameters
    bm_pu.set_progress_bar_params(self, master)

    # Setting steps widgets parameters
    bm_pu.set_steps_widgets_param(self, master, parse=True)

    # Initializing checkbox parameters as lists
    # filled in _create_table and _update_status internal functions
    self.CHECK, self.TABLE = [], []

    # Setting check box positions
    box_pos_params = _set_box_pos_params(master)

    # ****************************** DISPLAY PARSING-FILES STATUS

    def _launch_update_status_try():
        # update files status
        _update_status(self, master, box_pos_params)

    # Setting widgets of button for update of parsing-files status
    step_num = 0
    status_help_button = bm_pu.set_step_help_button(self, step_num, pos_type='bellow')
    status_button = bm_pu.set_step_launch_button(self, step_num,
                                                 _launch_update_status_try,
                                                 'place', parse=True)

    # Updating check boxes
    _update_status(self, master, box_pos_params)


    # ****************************** YEAR SELECTION

    default_year = master.years_list[-1]
    self.variable_years = tk.StringVar(self)
    self.variable_years.set(default_year)

    # Setting widgets for year selection
    bm_pu.set_year_select_widgets(self, master)


    # ****************************** LAUNCH PARSING

    def _launch_parsing_try(progress_callback):

        # Getting year selection and database selection
        year_select = self.variable_years.get()
        parsing_data = parse_data_var.get()

        _launch_parsing(master, year_select, parsing_data,
                        inst_paths_list, progress_callback)
        # update files status
        _update_status(self, master, box_pos_params)
        self.progress_bar.place_forget()

    def _start_launch_parsing_try():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_after(parsing_button, self.progress_bar,
                          dx=self.progress_bar_dx,
                          dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_parsing_try,
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for parsing
    step_num = 1
    parse_help_button = bm_pu.set_step_help_button(self, step_num)

    # Setting widgets for database selection for parsing
    parse_data_var, parse_data_opt_but = bm_pu.set_data_select_widgets(self, step_num)

    # Setting widgets of buttons for parsing launch button
    parsing_button = bm_pu.set_step_launch_button(self, step_num,
                                                  _start_launch_parsing_try,
                                                  'after', parse=True,
                                                  widget_ref=parse_data_opt_but)


    # ****************************** LAUNCH PARSING DEDUPLICATION

    def _launch_dedup_try(progress_callback):
        # Getting year selection
        year_select = self.variable_years.get()
        _launch_dedup(master, year_select, inst_paths_list, progress_callback)
        # update files status
        _update_status(self, master, box_pos_params)
        self.progress_bar.place_forget()

    def _start_launch_dedup_try():
        bm_gu.disable_buttons(self.page_buttons_list)
        bm_gu.place_after(dedup_button, self.progress_bar,
                          dx=self.progress_bar_dx,
                          dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_dedup_try,
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for deduplication
    step_num = 2
    dedup_help_button = bm_pu.set_step_help_button(self, step_num)
    dedup_button = bm_pu.set_step_launch_button(self, step_num,
                                                _start_launch_dedup_try,
                                                'bellow', parse=True)


    # ****************************** Setting buttons list for status change
    self.page_buttons_list = [self.years_opt_but,
                              status_help_button,
                              status_button,
                              parse_help_button,
                              parse_data_opt_but,
                              parsing_button,
                              dedup_help_button,
                              dedup_button]
