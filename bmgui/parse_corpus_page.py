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
from bmgui.gui_utils import set_page_title


class CheckBoxCorpuses:
    """Displays status of parsing files through Checkbutton tkinter widgets.

    Args:
        year (str): Corpus year defined by 4 digits.
        wos_r_ (bool): Status of WoS raw-data file.
        wos_p (bool): Status of WoS parsing files.
        scopus_r (bool): Status of Scopus raw-data file.
        scopus_p (bool): Status of Scopus parsing files.
        concat (bool) : Status of concatenation and deduplication files.
    """

    def __init__(self, parent, master, year, items_status):
        
        def _set_item_status(self, item):
            self.boxes_dict[item] = tk.Checkbutton(parent)
            if items_status[item]:
                self.boxes_dict[item].select()
            
        # Setting useful local variables for positions setting in px
        w_sf_mm = master.width_sf_mm
        w_sf_min = master.width_sf_min

        self.check_boxes_sep_space = mm_to_px(bm_gg.REF_CHECK_BOXES_SEP_SPACE * w_sf_mm,
                                              bm_gg.PPI)
        header_font_size = font_size(bm_gg.STEP_FONT_SIZE_REF - 3, w_sf_min) # 11
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
            self.boxes_dict[item].place(x=box_x_pos, y=box_y_pos, anchor='center')
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
        The globals 'FONT_NAME' and 'PPI' are imported from the module 'gui_globals'
        of the package 'bmgui'.
    """
    # Internal functions
    def _set_table_item(item_text, item_x_pos):
        item_box = tk.Label(self,
                            text=item_text,
                            font=table_header_font)
        item_box.place(x=item_x_pos, y=y_pos_ref, anchor='center')
        self.TABLE.append(item_box)

    # Setting useful local variables for positions setting in px
    w_sf_mm = master.width_sf_mm
    h_sf_mm = master.height_sf_mm
    w_sf_min = master.width_sf_min

    # Setting specific font properties
    header_font_size = font_size(bm_gg.STEP_FONT_SIZE_REF - 3, w_sf_min) # 11
    table_header_font = tkFont.Font(family=bm_gg.FONT_NAME,
                              size=header_font_size)

    # Setting useful x position shift and y position reference in pixels
    x_pos_shift = mm_to_px(25 * w_sf_mm, bm_gg.PPI)
    y_pos_ref = mm_to_px(30 * h_sf_mm, bm_gg.PPI)

    # Initializing x position in pixels
    x_pos = x_pos_init

    # Setting table items
    for _, item_text in bm_gg.BOX_TABLE_COLS.items():
        x_pos += x_pos_shift
        _set_table_item(item_text, x_pos)


def _update(self, master, wf_path, box_pos_tup):
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
    # Setting parameters from args
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
    It updates the files status using the internal function `_update`.

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
        if not os.path.exists(parsing_path):
            os.mkdir(parsing_path)
        progress_callback(20)
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
        progress_callback(10)

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
    It updates the files status using the internal function `_update`.

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
        if not os.path.exists(concat_root_path):
            os.mkdir(concat_root_path)
        if not os.path.exists(concat_path):
            os.mkdir(concat_path)
        if not os.path.exists(dedup_root_path):
            os.mkdir(dedup_root_path)
        if not os.path.exists(dedup_path):
            os.mkdir(dedup_path)
        progress_callback(15)

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
    `_launch_dedup` and `_update`.

    Args:
        page_name (str): Name of parsing page.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """
    # Internal functions
    def _set_item_select_widgets(self, item, step_name):
        """Sets in the page the label and place of the year-selection 
        label widget and the button and place of the year-selection button.
        """
        # Setting item selection label
        item_label = tk.Label(self,
                              text=bm_gg.OPTION_SELECT[item],
                              font=label_select_font)
        place_bellow(step_label_widget_dict[step_name], item_label,
                     dx=select_label_dx[item], dy=select_label_dy[item])

        # Setting option button for item selection
        item_variable = tk.StringVar(self)
        item_variable.set(select_default[item])
        item_opt_but = tk.OptionMenu(self, item_variable,
                                     *select_list[item])
        item_opt_but.config(font=but_select_font)
        place_after(item_label, item_opt_but, dx=select_button_dx,
                    dy=select_button_dy)
        bm_gg.GUI_BUTTONS.append(item_opt_but)
        return item_variable, item_opt_but

    def _set_step_label(self, step_name):
        """Sets the label and place of step-label widget in the page.

        Args:
            step_name (str): The name of the step in 'bm_gg.STEP_KEYS_LIST' \
            global.
        """
        step_label = tk.Label(self,
                              text=bm_gg.PARSING_LABELS[step_name],
                              justify=step_label_format,
                              font=step_label_font)
        step_label.place(x=step_label_x_pos,
                         y=step_label_y_pos_dict[step_name],
                         anchor="nw")
        return step_label

    def _set_step_launch_button(self, step_name, step_start_funct,
                                pos_params):
        step_launch_button = tk.Button(self,
                                       text=bm_gg.PARSING_LAUNCH[step_name],
                                       font=step_launch_font,
                                       command=step_start_funct)
        pos_type, widget_ref, x_pos, y_pos, dx, dy = pos_params
        if pos_type=='bellow':
            place_bellow(widget_ref, step_launch_button,
                         dy=dy)
        elif pos_type=='after':
            place_after(widget_ref, step_launch_button,
                        dx=dx, dy=dy)
        else:    
            step_launch_button.place(x=x_pos, y=y_pos,
                                     anchor='n')
        bm_gg.GUI_BUTTONS.append(step_launch_button)
        return step_launch_button
    def _update_progress(value):
        progress_var.set(value)
        progress_bar.update_idletasks()
        if value>=100:
            enable_buttons(parse_buttons_list)

    # Setting useful local variables for positions setting in px
    w_sf_mm = master.width_sf_mm
    h_sf_mm = master.height_sf_mm
    w_sf_min = master.width_sf_min

    # ****************************** STATUS **********************************************
    # ************************************************************************************
    # Setting check box positions
    box_x_pos_px = mm_to_px(bm_gg.BOX_POS_MM_LIST[0] * w_sf_mm, bm_gg.PPI)    #70
    box_y_pos_px = mm_to_px(bm_gg.BOX_POS_MM_LIST[1] * h_sf_mm, bm_gg.PPI)    #40
    box_line_dy_px = mm_to_px(bm_gg.BOX_POS_MM_LIST[2] * h_sf_mm, bm_gg.PPI)  #10
    box_pos_tup = (box_x_pos_px, box_y_pos_px, box_line_dy_px)

    # Setting positions in px for status update
    status_launch_x_pos = mm_to_px(148 * w_sf_mm, bm_gg.PPI)
    status_launch_y_pos = mm_to_px(98 * h_sf_mm, bm_gg.PPI)
    
    # ****************************** STEP LABEL ******************************************
    # ************************************************************************************
    # Setting labels positions in px
    step_label_x_pos = mm_to_px(bm_gg.STEP_POS_X_MM_REF * w_sf_mm, #10
                                bm_gg.PPI)
    step_label_y_pos_list = [mm_to_px( y * master.height_sf_mm, bm_gg.PPI)
                             for y in bm_gg.LABELS_POS_Y_MM_REF.values()]     #[25, 107, 135]
    step_label_y_pos_dict = dict(zip(bm_gg.LABELS_POS_Y_MM_REF.keys(),
                                     step_label_y_pos_list))

    # Setting step-label font
    step_font_size = font_size(bm_gg.STEP_FONT_SIZE_REF + 2, master.width_sf_min)   #16
    step_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=step_font_size,
                                  weight='bold')

    # Setting step-label widgets parameters
    step_label_format = 'left'
    step_names_list = bm_gg.STEP_KEYS_LIST
    step_label_widget_list = [_set_step_label(self, step_name)
                              for step_name in step_names_list]    
    step_label_widget_dict = dict(zip(step_names_list, step_label_widget_list))


    # ****************************** ITEM SELECT *****************************************
    # ************************************************************************************
    # Setting position parameters for items selection
    select_label_dx = {'year': 0,
                       'data': mm_to_px(70 * w_sf_mm, bm_gg.PPI)}
    select_label_dy = {'year': mm_to_px(2 * h_sf_mm, bm_gg.PPI),
                       'data': mm_to_px(2 * h_sf_mm, bm_gg.PPI)}
    select_button_dx = mm_to_px(1 * w_sf_mm, bm_gg.PPI)
    select_button_dy = mm_to_px(-2 * h_sf_mm, bm_gg.PPI)

    # Setting lists and default values for items selection
    select_list = {'year': master.years_list,
                   'data': bm_pg.BDD_LIST}

    select_default = {'year': master.years_list[-1],
                      'data': bm_pg.BDD_LIST[0]}
    
    # Setting select-item label font
    select_font_size = font_size(bm_gg.STEP_FONT_SIZE_REF - 2, master.width_sf_min) #14
    label_select_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                    size=select_font_size)
    # Setting select-item button font
    button_font_size = font_size(bm_gg.STEP_FONT_SIZE_REF - 3, master.width_sf_min) #11
    but_select_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=button_font_size)

    # ****************************** STEP LAUNCH *****************************************
    # ************************************************************************************
    # Setting buttons positions in px
    launch_but_dx = mm_to_px(bm_gg.LAUNCH_DPOS_MM_LIST[0] * w_sf_mm, bm_gg.PPI)    #15
    launch_but_dy = mm_to_px(bm_gg.LAUNCH_DPOS_MM_LIST[1] * h_sf_mm, bm_gg.PPI)    #0.2

    # Setting step-launch font
    launch_font_size = font_size(bm_gg.STEP_FONT_SIZE_REF - 2, master.width_sf_min) #12
    step_launch_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                   size=launch_font_size)

    # ****************************** PROGRESS BAR *********************************************
    # ************************************************************************************
    # Setting progress_bar parameters in px
    progress_bar_len_px = mm_to_px(bm_gg.PROGRESS_BAR_LEN_MM['parse']\
                                   * w_sf_mm, bm_gg.PPI)  # 50
    progress_bar_parse_dx = bm_gg.PROGRESS_BAR_DX_PX['parse'] # -80
    progress_bar_parse_dy = bm_gg.PROGRESS_BAR_DY_PX['parse'] # 15
    progress_bar_synth_dx = bm_gg.PROGRESS_BAR_DX_PX['synth'] # 40
    progress_bar_synth_dy = bm_gg.PROGRESS_BAR_DY_PX['synth'] # 0

    # ****************************** GENERAL *********************************************
    # ************************************************************************************
    # Getting institute parameters
    wf_root_path = wf_path.parent
    org_tup = set_org_params(institute, wf_root_path)

    # Setting institutions files paths
    inst_paths_tup = _set_parse_inst_params(institute, wf_path)

    # Initializing progress bar widget
    progress_var = tk.IntVar()  # Variable to keep track of the progress bar value
    progress_bar = ttk.Progressbar(self,
                                   orient="horizontal",
                                   length=progress_bar_len_px,
                                   mode="determinate",
                                   variable=progress_var)

    # Creating and setting widgets for page title and exit button
    page_label = bm_gg.PAGES_LABELS[page_name]
    set_page_title(self, master, page_label, institute, datatype)
    set_exit_button(self, master)

    # **************** DISPLAY PARSING-FILES STATUS
    def _launch_update_try():
        # update files status
        _update(self, master, wf_path, box_pos_tup)

    # Initializing checkbox parameters as lists
    # filled in _create_table and _update internal functions
    self.CHECK = []
    self.TABLE = []

    # Setting widgets of button for update of parsing-files status
    pos_params = ('place', None, status_launch_x_pos, status_launch_y_pos,
                  None, None)
    status_button = _set_step_launch_button(self, 'status',
                                            _launch_update_try,
                                            pos_params)

    # **************** LAUNCH PARSING    
    def _launch_parsing_try(progress_callback):
        parsing_year = parse_year_var.get()
        parsing_data = parse_data_var.get()
        _launch_parsing(master, parsing_year, parsing_data,
                        wf_path, inst_paths_tup, progress_callback)
        progress_bar.place_forget()

    def _start_launch_parsing_try():
        disable_buttons(parse_buttons_list)
        place_bellow(parsing_button, progress_bar,
                     dx=progress_bar_parse_dx,
                     dy=progress_bar_parse_dy)
        progress_var.set(0)
        threading.Thread(target=_launch_parsing_try,
                         args=(_update_progress,)).start()
        # update files status
        _update(self, master, wf_path, box_pos_tup)

    # Setting widgets for corpus year selection for parsing
    return_tup = _set_item_select_widgets(self, 'year', 'parsing')
    parse_year_var, parse_year_opt_but = return_tup

    # Setting widgets for database-type selection
    return_tup = _set_item_select_widgets(self, 'data', 'parsing')
    parse_data_var, parse_data_opt_but = return_tup

    # Setting widgets for launch parsing button
    pos_params = ('after', parse_data_opt_but, None, None,
                  launch_but_dx, launch_but_dy)
    parsing_button = _set_step_launch_button(self, 'parsing',
                                             _start_launch_parsing_try,
                                             pos_params)

    # **************** LAUNCH PARSING DEDUPLICATION
    def _launch_dedup_try(progress_callback):
        dedup_year = dedup_year_var.get()
        _launch_dedup(master, dedup_year,
                      org_tup, wf_path, datatype,
                      inst_paths_tup, progress_callback)
        progress_bar.place_forget()

    def _start_launch_dedup_try():
        disable_buttons(parse_buttons_list)
        place_after(dedup_button, progress_bar,
                    dx=progress_bar_synth_dx,
                    dy=progress_bar_synth_dy)
        progress_var.set(0)
        threading.Thread(target=_launch_dedup_try,
                         args=(_update_progress,)).start()
        # update files status
        _update(self, master, wf_path, box_pos_tup)

    # Setting widgets for corpus year selection for parsing
    return_tup = _set_item_select_widgets(self, 'year', 'dedup')
    dedup_year_var, dedup_year_opt_but = return_tup

    # Setting widgets for launch deduplication button
    pos_params = ('after', dedup_year_opt_but, None, None,
                  launch_but_dx, launch_but_dy)
    dedup_button = _set_step_launch_button(self, 'dedup',
                                           _start_launch_dedup_try,
                                           pos_params)

    # **************** UPDATE CHECK BOXES :
    _update(self, master, wf_path, box_pos_tup)

    # Setting buttons list for status change
    parse_buttons_list = [status_button,
                          parse_year_opt_but,
                          parse_data_opt_but,
                          dedup_year_opt_but,
                          parsing_button,
                          dedup_button]
