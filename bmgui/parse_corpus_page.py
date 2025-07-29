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
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
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
from bmgui.gui_utils import set_font_size_tup
from bmgui.gui_utils import set_page_title
from bmgui.gui_utils import set_pos_tup_px
from bmgui.gui_utils import set_pos_tup_px_list
from bmgui.gui_utils import set_progress_bar_pos_tup
from bmgui.pages_utils import set_data_select_widgets
from bmgui.pages_utils import set_step_label
from bmgui.pages_utils import set_step_launch_button
from bmgui.pages_utils import set_year_select_widgets


class CheckBoxCorpuses:
    """Displays status of parsing files through Checkbutton tkinter widgets.

    Args:
        year (str): Corpus year defined by 4 digits.
        items_status (dict): Availability of raw data, parsing data \
        and deduplicated data (keys: type of data (str); values: status (bool)).
    """

    def __init__(self, parent, master, year, items_status):
        
        def _set_item_status(self, item):
            self.boxes_dict[item] = tk.Checkbutton(parent)
            if items_status[item]:
                self.boxes_dict[item].select()

        self.check_boxes_sep_space = mm_to_px(bm_gg.BOX_SEP_SPACE\
                                              * master.width_sf_mm, bm_gg.PPI)
        header_font_size = font_size(bm_gg.PAGE_FONT_SIZE_DICT['box_header'],
                                     master.width_sf_min)
        table_header_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                        size=header_font_size)
        self.lab = tk.Label(parent, text=year, font=table_header_font)
        self.boxes_dict = {}
        for item in items_status.keys():
            _set_item_status(self, item)

    def boxes_place(self, box_x_pos_init, box_y_pos, items_status):
        box_x_pos = box_x_pos_init
        a = self.lab.winfo_reqwidth()
        self.lab.place(x=box_x_pos-a, y=box_y_pos, anchor='center')
        for item in items_status.keys():
            box_x_pos += self.check_boxes_sep_space
            self.boxes_dict[item].place(x=box_x_pos, y=box_y_pos,
                                        anchor='center')
            self.boxes_dict[item].config(state='disabled')

    def efface(self):
        self.lab.place_forget()
        for item in self.boxes_dict.keys():
            self.boxes_dict[item].place_forget()


def _create_table(self, master, x_pos_init):
    """Creates the column names of the table displaying which files 
    of the parsing step are available in the working folder.

    The positions of the table items are set using the argument 'x_pos_init', 
    and the general properties of tkinter window as 'master' class variables.

    Args:
        x_pos_init (int): The horizontal position in pixels to be used \
        for the first widget location on the parsing page.
    Note:
        The functions 'font_size' and 'mm_to_px' are imported 
        from the module 'gui_utils' of the package 'bmgui'.
    """
    # Internal functions
    def _set_table_item(item_text, item_x_pos):
        item_box = tk.Label(self,
                            text=item_text,
                            font=table_header_font)
        item_box.place(x=item_x_pos, y=y_pos, anchor='center')
        self.TABLE.append(item_box)

    # Setting specific font properties
    header_font_size = font_size(bm_gg.PAGE_FONT_SIZE_DICT['box_header'],
                                 master.width_sf_min)
    table_header_font = tkFont.Font(family=bm_gg.FONT_NAME,
                              size=header_font_size)

    # Setting useful x position shift and y position reference
    x_shift = mm_to_px(bm_gg.BOX_TABLE_POS_DICT['x_shift']\
                       * master.width_sf_mm, bm_gg.PPI)
    y_pos = mm_to_px(bm_gg.BOX_TABLE_POS_DICT['y_pos']\
                     * master.height_sf_mm, bm_gg.PPI)

    # Initializing x position in pixels
    x_pos = x_pos_init

    # Setting table items
    for _, item_text in bm_gg.BOX_TABLE_COLS_DICT.items():
        x_pos += x_shift
        _set_table_item(item_text, x_pos)


def _set_box_pos_tup(master):
    # Setting check box positions
    box_x_pos = mm_to_px(bm_gg.BOX_POS_TUP[0] * master.width_sf_mm, bm_gg.PPI)
    box_y_pos = mm_to_px(bm_gg.BOX_POS_TUP[1] * master.height_sf_mm, bm_gg.PPI)
    box_line_dy = mm_to_px(bm_gg.BOX_Y_DPOS * master.height_sf_mm, bm_gg.PPI)
    box_pos_tup = (box_x_pos, box_y_pos, box_line_dy)
    return box_pos_tup


def _update_status(self, master, wf_path, box_pos_tup):
    """Refreshes the current state of the files in the 
    working folder using the `_create_table` internal function.

    It also updates the OptionMenu buttons used to select the year.

    Args:
        wf_path (path): The path leading to the working folder.
        box_pos_tup (tup): (x position (int) for first widget location, \
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
    # Setting check box positions
    x_pos_init, y_pos_init, esp_ligne = box_pos_tup
    box_x_pos_init = x_pos_init

    # Clearing all check boxes
    for _, check in enumerate(self.CHECK):
        check.efface()

    for year_idx, year in enumerate(master.list_corpus_year):
        items_status = {'wos_r'   : master.list_wos_rawdata[year_idx],
                        'wos_p'   : master.list_wos_parsing[year_idx],
                        'scopus_r': master.list_scopus_rawdata[year_idx],
                        'scopus_p': master.list_scopus_parsing[year_idx],
                        'dedup'   : master.list_dedup[year_idx]
                       }
        tmp = CheckBoxCorpuses(self,
                               master,
                               year,
                               items_status)
        box_y_pos = y_pos_init + year_idx * esp_ligne
        tmp.boxes_place(box_x_pos_init, box_y_pos, items_status)
        self.CHECK.append(tmp)

    _create_table(self, master, x_pos_init)


def _set_parse_year_files_params(wf_path, year_select):
    """Sets useful folders and files parameters (path and file name) depending 
    on the selected corpus year for the parsing of the publications extractions
    from external databases.

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


def _launch_parsing(master, corpus_year, database_type, wf_path,
                    inst_paths_tup, progress_callback):
    """Launches parsing of raw-data of 'database_type' database.

    This is done through `biblio_parser` function imported from 
    3rd party package imported as bp after check of database name 
    and database raw-data availability. 
    It saves the resulting parsing files using paths set through 
    `set_user_config` function imported from `bmfuncts.config_utils` 
    module.

    Args:
        corpus_year (str): Corpus year defined by 4 digits.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        wf_path (path): Full path to working folder.
        inst_paths_tup (tup): (full path to institute-affiliations \
        file, full path to institutions-types file).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """
    # Internal functions
    def _corpus_parsing(rawdata_path, parsing_path,
                        database_type, progress_callback):
        parsing_tup = bp.biblio_parser(rawdata_path, database_type,
                                       inst_filter_list=None,
                                       country_affiliations_file_path=inst_paths_tup[0],
                                       inst_types_file_path=inst_paths_tup[1])
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

    # Setting dialog for parsing corpus
    if database_type in bm_pg.BDD_LIST:
        # Getting the full paths of the working folder architecture for the corpus "corpus_year"
        config_tup = set_user_config(wf_path, corpus_year, bm_pg.BDD_LIST)
        rawdata_path_dict, parsing_path_dict, item_filename_dict = config_tup[0:3]

        # Setting useful paths for database 'database_type'
        rawdata_path = rawdata_path_dict[database_type]
        parsing_path = parsing_path_dict[database_type]

        # Getting files status for corpus parsing
        rawdata_status, parsing_status = _get_parse_data_status(master, database_type,
                                                                corpus_year)
    
        # Setting parsing files extension for saving
        parsing_save_extent = bm_pg.TSV_SAVE_EXTENT
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

        
def _launch_dedup(master, corpus_year, org_tup, wf_path, datatype,
                     inst_paths_tup, progress_callback):
    """Concatenates and deduplicates the parsing from wos or scopus databases.

    This is done through the functions `concatenate_parsing` 
    and `deduplicate_parsing` imported from 3rd party package 
    imported as bp.

    It checks if all useful files are available in the working folder. 
    It saves the resulting parsing files using paths set through 
    `set_user_config` function imported from `bmfuncts.config_utils` 
    module.

    Args:
        corpus_year (str): Corpus year defined by 4 digits.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        inst_paths_tup (tup): (full path to institute-affiliations file, \
        full path to institutions-types file).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.
    """
    # Internal functions
    def _deduplicate_corpus_parsing(progress_callback):
        scopus_parsing_dict = read_parsing_dict(scopus_parse_path, item_filename_dict,
                                                parsing_save_extent)
        wos_parsing_dict = read_parsing_dict(wos_parse_path, item_filename_dict,
                                             parsing_save_extent)
        progress_callback(30)
        concat_parsing_dict = bp.concatenate_parsing(scopus_parsing_dict, wos_parsing_dict,
                                                     inst_filter_list=org_tup[3])
        progress_callback(50)
        save_parsing_dict(concat_parsing_dict, concat_path,
                          item_filename_dict, parsing_save_extent)
        progress_callback(60)
        dedup_parsing_dict = bp.deduplicate_parsing(concat_parsing_dict,
                                                    norm_inst_status=False,
                                                    inst_types_file_path=inst_paths_tup[0],
                                                    country_affiliations_file_path=inst_paths_tup[1])
        dedup_articles_nb = len(dedup_parsing_dict["articles"])
        progress_callback(90)
        save_parsing_dict(dedup_parsing_dict, dedup_path,
                          item_filename_dict, parsing_save_extent,
                          dedup_infos=(wf_path, datatype, corpus_year))
        progress_callback(100)
        return dedup_articles_nb

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(wf_path, corpus_year, bm_pg.BDD_LIST)
    parsing_path_dict, item_filename_dict = config_tup[1], config_tup[2]

    # Setting useful paths for corpus deduplication
    scopus_parse_path, wos_parse_path = parsing_path_dict["scopus"], parsing_path_dict["wos"]
    concat_root_path, concat_path = parsing_path_dict["concat_root"], parsing_path_dict["concat"]
    dedup_root_path, dedup_path = parsing_path_dict["dedup_root"], parsing_path_dict["dedup"]

    # Getting files status for corpus concatenation and deduplication
    dedup_status_tup = _get_dedup_data_status(master, corpus_year)
    wos_parse_status, scopus_parse_status, dedup_parse_status = dedup_status_tup

    # Setting parsing files extension for saving
    parsing_save_extent = bm_pg.TSV_SAVE_EXTENT
    progress_callback(15)

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
                    dedup_articles_nb = _deduplicate_corpus_parsing(progress_callback)
                    info_title = "Information"
                    info_text = (f"La synthèse pour l'année {corpus_year} a été reconstruite."
                                 f"\n\nNombre d'articles de synthèse : {dedup_articles_nb}.")
                    messagebox.showinfo(info_title, info_text)
                else:
                    progress_callback(100)
                    info_title = "Information"
                    info_text = "La synthèse dejà disponible est conservée."
                    messagebox.showinfo(info_title, info_text)
            else:
                dedup_articles_nb = _deduplicate_corpus_parsing(progress_callback)
                info_title = "Information"
                info_text = (f"La synthèse pour l'année {corpus_year} a été construite."
                             f"\n\nNombre d'articles de synthèse : {dedup_articles_nb}.")
                messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "Information"
        info_text = f"La synthèse pour l'année {corpus_year} est abandonnée."
        messagebox.showinfo(info_title, info_text)


def _set_parse_inst_params(institute, wf_path):
    """Sets files paths to institutions data.

    Args:
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
    Returns:
        (tup): (full path to institute-affiliations file, \
        full path to institutions-types file).
    """
    # Setting useful aliases
    institutions_folder_alias = bm_pg.ARCHI_INSTITUTIONS["root"]
    inst_aff_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["institute_affil_base"]
    inst_types_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["inst_types_base"]

    # Setting useful file names and paths for Institute affiliations
    institute_affil_file = institute + "_" + inst_aff_file_base_alias
    inst_types_file = institute + "_" + inst_types_file_base_alias
    institutions_folder_path = wf_path / Path(institutions_folder_alias)
    institute_affil_file_path = institutions_folder_path / Path(institute_affil_file)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file)

    # Setting return tup
    inst_paths_tup = (institute_affil_file_path, inst_types_file_path)
    return inst_paths_tup


def create_parsing_concat(self, master, page_name, institute, wf_path, datatype):
    """Manages creation and use of widgets for corpus parsing.

    This is done through the internal functions  `_launch_parsing`, 
    `_launch_dedup` and `_update_status`.

    Args:
        page_name (str): Name of parsing page.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """
    # Internal functions
    
    def _update_progress(value):
        progress_var.set(value)
        progress_bar.update_idletasks()
        if value>=100:
            enable_buttons(self.page_buttons_list)


    # ****************************** GENERAL SETTNGS

    # Getting institute parameters
    wf_root_path = wf_path.parent
    org_tup = set_org_params(institute, wf_root_path)

    # Setting institutions files paths
    inst_paths_tup = _set_parse_inst_params(institute, wf_path)

    # Setting page key and page year
    self.page_key = bm_gg.KEY_PARSE
    year_key = bm_gg.KEY_PARSE_YEAR
    parse_key = bm_gg.KEY_PARSE
    dedup_key = bm_gg.KEY_DEDUP

    # Setting size and relative positions of widget of progress bars
    return_tup = set_progress_bar_pos_tup(master, self.page_key)
    progress_bar_len, progress_bar_dx, progress_bar_dy = return_tup

    # Setting variable to keep track of the progress bar value
    progress_var = tk.IntVar()  
    progress_bar = ttk.Progressbar(self,
                                   orient="horizontal",
                                   length=progress_bar_len,
                                   mode="determinate",
                                   variable=progress_var)

    # Creating and setting widgets for page title and exit button
    page_label = bm_gg.PAGES_LABELS[page_name]
    set_page_title(self, master, page_label, institute, datatype)
    set_exit_button(self, master)

    # Setting all step-label widgets parameters
    step_label_pos_tup_list = set_pos_tup_px_list(master, bm_gg.STEP_POS_TUPS_DICT[self.page_key])    
    step_font_size_tup = set_font_size_tup(master, bm_gg.PAGE_FONT_SIZE_DICT,
                                           ['step_label', 'step_launch'])
    step_label_params = (step_font_size_tup, step_label_pos_tup_list)                   
    steps_number = bm_gg.STEPS_NB_DICT[self.page_key]
    step_label_widgets_list = [set_step_label(self, step_num, step_label_params)
                               for step_num in range(steps_number)]
    step_label_widgets_params = (step_label_widgets_list, step_label_pos_tup_list)

    # ****************************** DISPLAY PARSING-FILES STATUS

    def _launch_update_status_try():
        # update files status
        _update_status(self, master, wf_path, box_pos_tup)

    step_num = 0
    # Initializing checkbox parameters as lists
    # filled in _create_table and _update_status internal functions
    self.CHECK = []
    self.TABLE = []
    
    # Setting check box positions
    box_pos_tup = _set_box_pos_tup(master)
    
    # Setting widgets of button for update of parsing-files status 
    status_button_pos_tup = set_pos_tup_px(master, bm_gg.STATUS_BUT_POS_TUP)     
    status_button_params = (step_font_size_tup, _launch_update_status_try)
    status_pos_params = ('place', None, status_button_pos_tup, None)    
    status_button = set_step_launch_button(self, step_num,
                                           status_button_params,
                                           status_pos_params)

    # Updating check boxes
    _update_status(self, master, wf_path, box_pos_tup)


    # ****************************** YEAR SELECTION

    default_year = master.years_list[-1]
    self.variable_years = tk.StringVar(self)
    self.variable_years.set(default_year)

    # Setting widgets for year selection
    year_font_size_tup = set_font_size_tup(master, bm_gg.PAGE_FONT_SIZE_DICT['year_select'],
                                           ['label', 'button'])
    year_label_pos_tup = set_pos_tup_px(master, bm_gg.PAGE_SELECT_LABEL_POS_DICT[year_key])
    year_button_dpos_tup = set_pos_tup_px(master, bm_gg.PAGE_SELECT_BUT_DPOS_DICT[self.page_key])
    year_select_params = [year_font_size_tup, year_label_pos_tup, year_button_dpos_tup]
    set_year_select_widgets(self, master, year_select_params)


    # ****************************** LAUNCH PARSING    

    def _launch_parsing_try(progress_callback):
        
        # Getting year selection and database selection 
        year_select = self.variable_years.get()
        parsing_data = parse_data_var.get()

        _launch_parsing(master, year_select, parsing_data,
                        wf_path, inst_paths_tup, progress_callback)
        progress_bar.place_forget()

    def _start_launch_parsing_try():
        disable_buttons(self.page_buttons_list)
        place_after(parsing_button, progress_bar,
                    dx=progress_bar_dx,
                    dy=progress_bar_dy)
        progress_var.set(0)
        threading.Thread(target=_launch_parsing_try,
                         args=(_update_progress,)).start()
        # update files status
        _update_status(self, master, wf_path, box_pos_tup)

    step_num = 1
    # Setting widgets for database selection for parsing
    data_font_size_tup = set_font_size_tup(master, bm_gg.PAGE_FONT_SIZE_DICT['step_select'],
                                           ['label', 'button'])
    data_label_dpos_tup = set_pos_tup_px(master, bm_gg.PAGE_SELECT_LABEL_DPOS_DICT[self.page_key])
    data_button_dpos_tup = set_pos_tup_px(master, bm_gg.PAGE_SELECT_BUT_DPOS_DICT[self.page_key])
    data_select_params = (data_font_size_tup, data_label_dpos_tup,
                          data_button_dpos_tup, step_label_widgets_list[step_num])
    parse_data_var, parse_data_opt_but = set_data_select_widgets(self, data_select_params)

    # Setting widgets for launch parsing button
    parse_button_dpos_tup = set_pos_tup_px(master, bm_gg.STEP_BUT_DPOS_DICT[parse_key])     
    parse_launch_button_params = (step_font_size_tup, _start_launch_parsing_try)
    parse_launch_pos_params = ('after', parse_data_opt_but,
                               None, parse_button_dpos_tup)    
    parsing_button = set_step_launch_button(self, step_num,
                                            parse_launch_button_params,
                                            parse_launch_pos_params)


    # ****************************** LAUNCH PARSING DEDUPLICATION

    def _launch_dedup_try(progress_callback):
        # Getting year selection
        year_select = self.variable_years.get()
        _launch_dedup(master, year_select,
                      org_tup, wf_path, datatype,
                      inst_paths_tup, progress_callback)
        progress_bar.place_forget()

    def _start_launch_dedup_try():
        disable_buttons(self.page_buttons_list)
        place_after(dedup_button, progress_bar,
                    dx=progress_bar_dx,
                    dy=progress_bar_dy)
        progress_var.set(0)
        threading.Thread(target=_launch_dedup_try,
                         args=(_update_progress,)).start()
        # update files status
        _update_status(self, master, wf_path, box_pos_tup)

    step_num = 2
    # Setting widgets for launch deduplication button   
    dedup_button_dpos_tup = set_pos_tup_px(master, bm_gg.STEP_BUT_DPOS_DICT[dedup_key])     
    dedup_launch_button_params = (step_font_size_tup, _start_launch_dedup_try)
    dedup_launch_pos_params = ('bellow', step_label_widgets_list[step_num],
                               None, dedup_button_dpos_tup)    
    dedup_button = set_step_launch_button(self, step_num,
                                          dedup_launch_button_params,
                                          dedup_launch_pos_params)


    # ****************************** Setting buttons list for status change
    self.page_buttons_list = [self.years_opt_but,
                              status_button,
                              parse_data_opt_but,
                              parsing_button,
                              dedup_button]
