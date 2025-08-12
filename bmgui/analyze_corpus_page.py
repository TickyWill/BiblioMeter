"""The `analysis_corpus_page` module allows to perform 
impact factors, keywords and coupling analysis.
"""

__all__ = ['create_analysis']

# Standard library imports
import threading
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import ttk

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
from bmfuncts.add_ifs import get_if_db
from bmfuncts.authors_analysis import authors_analysis
from bmfuncts.build_kpi import if_analysis
from bmfuncts.config_utils import set_org_params
from bmfuncts.coupling_analysis import coupling_analysis
from bmfuncts.keywords_analysis import keywords_analysis
from bmfuncts.save_final_results import set_result_folder_path
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
from bmgui.pages_utils import set_data_select_widgets
from bmgui.pages_utils import set_progress_bar_params
from bmgui.pages_utils import set_step_help_button
from bmgui.pages_utils import set_step_label
from bmgui.pages_utils import set_step_launch_button
from bmgui.pages_utils import set_steps_widgets_param
from bmgui.pages_utils import set_year_select_widgets


def _launch_au_analysis(institute, org_tup, wf_path, datatype,
                        year_select, progress_callback):
    """Launches authors production analysis through `authors_analysis` 
    function imported from `bmfuncts.authors_analysis` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """
    auth_analysis_folder_path = authors_analysis(institute, org_tup,
                                                 wf_path,
                                                 datatype, year_select,
                                                 progress_callback)

    info_title = "- Information -"
    info_text = (f"L'analyse de la production par auteur a été effectuée "
                 f"pour l'année {year_select}."
                 "\nLes fichiers obtenus ont été créés dans le dossier :"
                 f"\n\n'{auth_analysis_folder_path}' ")
    messagebox.showinfo(info_title, info_text)


def _launch_kw_analysis(institute, org_tup, wf_path,
                        datatype, year_select, progress_callback):
    """Launches keywords analysis through `keywords_analysis` function 
    imported from `bmfuncts.pub_analysis` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """
    kw_analysis_folder_path = keywords_analysis(institute, org_tup,
                                                wf_path,
                                                datatype, year_select,
                                                progress_callback,
                                                verbose=False)

    info_title = "- Information -"
    info_text = (f"L'analyse des mots clefs a été effectuée pour l'année {year_select}."
                 "\nLes fichiers obtenus ont été créés dans le dossier :"
                 f"\n\n'{kw_analysis_folder_path}' ")
    messagebox.showinfo(info_title, info_text)


def _launch_coupling_analysis(institute, org_tup, wf_path, datatype,
                              year_select, progress_callback):
    """Launches coupling analysis through `coupling_analysis` function 
    imported from `bmfuncts.pub_analysis` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.    
    """

    ask_title = "- Confirmation de l'analyse des collaborations -"
    ask_text = ("L'analyse des collaborations a été lancée "
                f"pour l'année {year_select}."
                "\nCette opération peut prendre quelques minutes."
                "\n\nContinuer ?")
    answer = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        return_tup = coupling_analysis(institute, org_tup,
                                       wf_path,
                                       datatype, year_select,
                                       progress_callback,
                                       verbose=True)
        (analysis_folder, geo_analysis_folder, inst_analysis_folder,
         country_affil_file_path, wrong_affil_types_dict) = return_tup

        if not wrong_affil_types_dict:
            info_title = "- Information -"
            info_text = ("L'analyse géographique et l'analyse des collaborations "
                         f"a été effectuée pour l'année {year_select}."
                         "\n\nLes fichiers obtenus ont été créés dans les dossiers :"
                         f"\n\n    '{analysis_folder}/{geo_analysis_folder}'"
                         f"\n\n    '{analysis_folder}/{inst_analysis_folder}'")
        else:
            info_title = "- Attention -"
            info_text = ("L'analyse géographique et l'analyse des collaborations "
                         f"a été abandonnée pour l'année {year_select}."
                         "\n\nDes types d'affiliations erronés ont été rencontrés dans le fichier "
                         f"suivant : \n    '{country_affil_file_path}"
                         f"\n\n1- Corriger dans ce fichier les types d'affiliation suivants:")
            for k,v in wrong_affil_types_dict.items():
                info_text += f"\n        {k}: {v}"
            info_text +="\n\n2- Relancer l'analyse des collaborations"
        messagebox.showinfo(info_title, info_text)
    else:
        progress_callback(100)
        info_title = "- Information -"
        info_text = ("L'analyse des collaborations "
                     f"de l'année {year_select} est annulée.")
        messagebox.showinfo(info_title, info_text)


def _launch_if_analysis(institute, org_tup, wf_path, datatype,
                        year_select, progress_callback):
    """Launches impact-factors analysis through `if_analysis` function 
    imported from `bmfuncts.pub_analysis` module after 
    getting year of most-recent impact factors.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.  
    """
    # Setting path for saving results
    results_folder_path = set_result_folder_path(wf_path, datatype)
    
    # Getting year of most recent IFs
    _, _, if_most_recent_year = get_if_db(institute, org_tup, wf_path)

    analysis_if = "IF " + if_most_recent_year
    if bm_pg.ANALYSIS_IF==bm_pg.COL_NAMES_BONUS['IF année publi']:
        if if_most_recent_year>=year_select:
            analysis_if = "IF " + year_select

    return_tup = if_analysis(institute, org_tup, wf_path,
                             datatype, year_select, if_most_recent_year,
                             progress_callback, verbose=False)
    doctypes_analysis_folder_path, if_analysis_folder_path, _, _ = return_tup
    info_title = "- Information -"
    info_text = ("L'analyse par type de documents et l'analyse des IFs "
                 f"ont été effectuées pour l'année {year_select} "
                 f"avec les valeurs {analysis_if}. "
                 "\n\nPour les types de documents, les fichiers obtenus "
                 "ont été créés dans le dossier :"
                 f"\n\n'{doctypes_analysis_folder_path}'."
                 "\n\nPour les IFs, les fichiers obtenus ont été créés "
                 f"dans le dossier :\n\n'{if_analysis_folder_path}'."
                 "\n\nLa base de données des indicateurs respective de l'Institut "
                 "et de chaque département a été mise à jour "
                 "avec les résultats de cette analyse et se trouve dans le dossier :"
                 f"\n\n'{results_folder_path}'.")
    messagebox.showinfo(info_title, info_text)


def create_analysis(self, master, page_name, institute, wf_path, datatype):
    """Manages creation and use of widgets for corpus analysis through internal 
    functions  `_launch_if_analysis`, `_launch_au_analysis`, `_launch_coupling_analysis` 
    and `_launch_kw_analysis`.

    Args:
        self (instense): Instense where analysis page will be created.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of analysis page (`AnalyzeCorpusPage` class \
        of bmgui.main_page module).
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

    # Creating and setting widgets for page title and exit button
    page_label = bm_gg.PAGES_LABELS[page_name]
    set_page_title(self, master, page_label, institute, datatype)
    set_exit_button(self, master)

    # Getting institute parameters
    wf_root_path = wf_path.parent
    org_tup = set_org_params(institute, wf_root_path)

    # Setting short_name for page key and year key to use in globals
    self.page_key = bm_gg.KEY_ANALYS
    self.year_key = bm_gg.KEY_ANALYS_YEAR
    
    # Setting progress bars parameters
    set_progress_bar_params(self, master)

    # Setting steps widgets parameters
    set_steps_widgets_param(self, master)
  
    # *********************** YEAR SELECTION

    default_year = master.years_list[-1]
    self.variable_years = tk.StringVar(self)
    self.variable_years.set(default_year)

    # Setting widgets for year selection
    set_year_select_widgets(self, master)

    # *********************** STEP 0: IMPACT-FACTORS ANALYSIS
    def _launch_if_analysis_try(progress_callback):
        # Getting year selection
        year_select = self.variable_years.get()

        print(f"\nIFs analysis launched for year {year_select}")
        _launch_if_analysis(institute, org_tup, wf_path, datatype,
                            year_select, progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_if_analysis_try():
        disable_buttons(self.page_buttons_list)
        place_after(if_analysis_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_if_analysis_try,
                         args=(_update_progress,)).start()

    # Setting widgets of button for IF analysis
    step_num = 0
    if_analysis_help_button = set_step_help_button(self, step_num)     
    if_analysis_button = set_step_launch_button(self, step_num,
                                                _start_launch_if_analysis_try,
                                                'bellow')

    # *********************** STEP 1: AUTHORS-PRODUCTION ANALYSIS
    def _launch_au_analysis_try(progress_callback):
        # Getting year selection
        year_select = self.variable_years.get()

        print(f"\nAuthors analysis launched for year {year_select}")
        _launch_au_analysis(institute, org_tup, wf_path, datatype,
                            year_select, progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_au_analysis_try():
        disable_buttons(self.page_buttons_list)
        place_after(au_analysis_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_au_analysis_try,
                         args=(_update_progress,)).start()

    # Setting widgets of button for IF analysis
    step_num = 1
    au_analysis_help_button = set_step_help_button(self, step_num)    
    au_analysis_button = set_step_launch_button(self, step_num,
                                                _start_launch_au_analysis_try,
                                                'bellow')

    # *********************** STEP 2: COUPLING ANALYSIS
    def _launch_coupling_analysis_try(progress_callback):
        # Getting year selection
        year_select = self.variable_years.get()

        print(f"\nCoupling analysis launched for year {year_select}")
        _launch_coupling_analysis(institute, org_tup,
                                  wf_path,
                                  datatype, year_select,
                                  progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_coupling_analysis_try():
        disable_buttons(self.page_buttons_list)
        place_after(co_analysis_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_coupling_analysis_try,
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for IF analysis
    step_num = 2
    co_analysis_help_button = set_step_help_button(self, step_num)
    co_analysis_button = set_step_launch_button(self, step_num,
                                                _start_launch_coupling_analysis_try,
                                                'bellow')

    # *********************** STEP 3: KEYWORDS ANALYSIS
    def _launch_kw_analysis_try(progress_callback):
        # Getting year selection
        year_select = self.variable_years.get()

        print(f"\nKeywords analysis launched for year {year_select}")
        _launch_kw_analysis(institute, org_tup, wf_path, datatype,
                            year_select, progress_callback)
        self.progress_bar.place_forget()

    def _start_launch_kw_analysis_try():
        disable_buttons(self.page_buttons_list)
        place_after(kw_analysis_button, self.progress_bar,
                    dx=self.progress_bar_dx, dy=self.progress_bar_dy)
        self.progress_var.set(0)
        threading.Thread(target=_launch_kw_analysis_try,
                         args=(_update_progress,)).start()

    # Setting widgets of buttons for IF analysis
    step_num = 3
    kw_analysis_help_button = set_step_help_button(self, step_num)    
    kw_analysis_button = set_step_launch_button(self, step_num,
                                                _start_launch_kw_analysis_try,
                                                'bellow')

    # Setting buttons list for status change
    self.page_buttons_list = [self.years_opt_but,
                              if_analysis_button,
                              au_analysis_button,
                              co_analysis_button,
                              kw_analysis_button]
