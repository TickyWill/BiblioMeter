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
import bmfuncts.pub_globals as pg
import bmgui.gui_globals as gg
from bmfuncts.config_utils import set_org_params
from bmfuncts.consolidate_pub_list import get_if_db
from bmfuncts.authors_analysis import authors_analysis
from bmfuncts.coupling_analysis import coupling_analysis
from bmfuncts.impact_factors_analysis import if_analysis
from bmfuncts.keywords_analysis import keywords_analysis
from bmgui.gui_globals import GUI_BUTTONS
from bmgui.gui_utils import disable_buttons
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import font_size
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_exit_button
from bmgui.gui_utils import set_page_title


def _launch_au_analysis(institute, org_tup, bibliometer_path, datatype,
                        year_select, progress_callback):
    """Launches authors production analysis through `authors_analysis` 
    function imported from `bmfuncts.authors_analysis` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """
    auth_analysis_folder_path = authors_analysis(institute,
                                                 org_tup,
                                                 bibliometer_path,
                                                 datatype,
                                                 year_select,
                                                 progress_callback,
                                                 verbose=False)

    info_title = "- Information -"
    info_text = (f"L'analyse de la production par auteur a été effectuée "
                 "pour l'année {year_select}."
                 "\nLes fichiers obtenus ont été créés dans le dossier :"
                 f"\n\n'{auth_analysis_folder_path}' ")
    messagebox.showinfo(info_title, info_text)


def _launch_kw_analysis(institute, org_tup, bibliometer_path,
                        datatype, year_select, progress_callback):
    """Launches keywords analysis through `keywords_analysis` function 
    imported from `bmfuncts.pub_analysis` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.   
    """
    kw_analysis_folder_path = keywords_analysis(institute,
                                                org_tup,
                                                bibliometer_path,
                                                datatype,
                                                year_select,
                                                progress_callback,
                                                verbose=False)

    info_title = "- Information -"
    info_text = (f"L'analyse des mots clefs a été effectuée pour l'année {year_select}."
                 "\nLes fichiers obtenus ont été créés dans le dossier :"
                 f"\n\n'{kw_analysis_folder_path}' ")
    messagebox.showinfo(info_title, info_text)


def _launch_coupling_analysis(institute, org_tup, bibliometer_path, datatype,
                              year_select, results_folder_path, progress_callback):
    """Launches coupling analysis through `coupling_analysis` function 
    imported from `bmfuncts.pub_analysis` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        results_folder_path (path): Full path where coupling results \
        will be saved in the futur (not yet used).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.    
    """
    # TO DO: use 'results_folder_path' in info_text

    return_tup = coupling_analysis(institute,
                                   org_tup,
                                   bibliometer_path,
                                   datatype,
                                   year_select,
                                   progress_callback,
                                   verbose=False)
    analysis_folder_alias, geo_analysis_folder_alias, inst_analysis_folder_alias = return_tup

    info_title = "- Information -"
    info_text = ("L'analyse géographique et des collaborations "
                 f"a été effectuée pour l'année {year_select}."
                 "\n\nLes fichiers obtenus ont été créés dans les dossiers :"
                 f"\n\n    '{analysis_folder_alias}/{geo_analysis_folder_alias}'"
                 f"\n\n    '{analysis_folder_alias}/{inst_analysis_folder_alias}'")
    # info_text += ("\n\nLa base de donnée des indicateurs respective de l'Institut "
    #            "et de chaque département a été mise à jour "
    #            "avec les résultats de cette analyse et se trouve dans le dossier :"
    #            f"\n\n'{results_folder_path}'.")
    messagebox.showinfo(info_title, info_text)


def _launch_if_analysis(institute, org_tup, bibliometer_path, datatype,
                        year_select, results_folder_path, progress_callback):
    """Launches impact-factors analysis through `if_analysis` function 
    imported from `bmfuncts.pub_analysis` module after 
    getting year of most-recent impact factors.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year_select (str): Corpus year defined by 4 digits.
        results_folder_path (path): Full path where coupling results \
        will be saved in the futur (not yet used).
        progress_callback (function): Function for updating \
        ProgressBar tkinter widget status.  
    """

    # Getting year of most recent IFs
    _, _, if_most_recent_year = get_if_db(institute, org_tup, bibliometer_path)

    analysis_if = "IF " + if_most_recent_year
    if pg.ANALYSIS_IF == pg.COL_NAMES_BONUS['IF année publi']:
        if if_most_recent_year >= year_select:
            analysis_if = "IF " + year_select

    if_analysis_folder_path, _, _ = if_analysis(institute,
                                                org_tup,
                                                bibliometer_path,
                                                datatype,
                                                year_select,
                                                if_most_recent_year,
                                                progress_callback,
                                                verbose=False)

    info_title = "- Information -"
    info_text = (f"L'analyse des IFs a été effectuée pour l'année {year_select} "
                 f"avec les valeurs {analysis_if}. "
                 "\n\nLes fichiers obtenus ont été créés dans le dossier :"
                 f"\n\n'{if_analysis_folder_path}'."
                 "\n\nLa base de données des indicateurs respective de l'Institut "
                 "et de chaque département a été mise à jour "
                 "avec les résultats de cette analyse et se trouve dans le dossier :"
                 f"\n\n'{results_folder_path}'.")
    messagebox.showinfo(info_title, info_text)


def create_analysis(self, master, page_name, institute, bibliometer_path, datatype):
    """Manages creation and use of widgets for corpus analysis through internal 
    functions  `_launch_if_analysis`, `_launch_au_analysis`, `_launch_coupling_analysis` 
    and `_launch_kw_analysis`.

    Args:
        self (instense): Instense where analysis page will be created.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of analysis page (`AnalyzeCorpusPage` class \
        of bmgui.main_page module).
        institute (str): Institute name.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """

    # Internal functions
    def _launch_if_analysis_try(progress_callback):
        # Getting year selection
        year_select = variable_years.get()

        print(f"\nIFs analysis launched for year {year_select}")
        _launch_if_analysis(institute, org_tup, bibliometer_path, datatype,
                            year_select, results_folder_path, progress_callback)
        progress_bar.place_forget()

    def _launch_au_analysis_try(progress_callback):
        # Getting year selection
        year_select = variable_years.get()

        print(f"\nAuthors analysis launched for year {year_select}")
        _launch_au_analysis(institute, org_tup, bibliometer_path, datatype,
                            year_select, progress_callback)
        progress_bar.place_forget()

    def _launch_coupling_analysis_try(progress_callback):
        # Getting year selection
        year_select = variable_years.get()

        ask_title = "- Confirmation de l'analyse des collaborations -"
        ask_text  = ("L'analyse des collaborations a été lancée "
                     f"pour l'année {year_select}."
                     "\nCette opération peut prendre quelques minutes."
                     "\n\nContinuer ?")
        answer    = messagebox.askokcancel(ask_title, ask_text)
        if answer:
            print(f"Coupling analysis launched for year {year_select}")
            _launch_coupling_analysis(institute, org_tup, bibliometer_path, datatype,
                                      year_select, results_folder_path, progress_callback)
        else:
            progress_callback(100)
            info_title = "- Information -"
            info_text = ("L'analyse des collaborations "
                         f"de l'année {year_select} est annulée.")
            messagebox.showinfo(info_title, info_text)
        progress_bar.place_forget()

    def _launch_kw_analysis_try(progress_callback):
        # Getting year selection
        year_select = variable_years.get()

        print(f"Keywords analysis launched for year {year_select}")
        _launch_kw_analysis(institute, org_tup, bibliometer_path, datatype,
                            year_select, progress_callback)
        progress_bar.place_forget()

    def _update_progress(value):
        progress_var.set(value)
        progress_bar.update_idletasks()
        if value >= 100:
            enable_buttons(analysis_buttons_list)

    def _start_launch_if_analysis_try():
        disable_buttons(analysis_buttons_list)
        place_after(if_analysis_launch_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_if_analysis_try, args=(_update_progress,)).start()

    def _start_launch_au_analysis_try():
        disable_buttons(analysis_buttons_list)
        place_after(au_analysis_launch_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_au_analysis_try, args=(_update_progress,)).start()

    def _start_launch_coupling_analysis_try():
        disable_buttons(analysis_buttons_list)
        place_after(co_analysis_launch_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_coupling_analysis_try, args=(_update_progress,)).start()

    def _start_launch_kw_analysis_try():
        disable_buttons(analysis_buttons_list)
        place_after(kw_analysis_launch_button,
                    progress_bar, dx = progress_bar_dx, dy = 0)
        progress_var.set(0)
        threading.Thread(target=_launch_kw_analysis_try, args=(_update_progress,)).start()

    def _edit_help(help_text):
        disable_buttons(analysis_buttons_list)
        info_title = "- DESCRIPTION -"
        info_text = help_text
        messagebox.showinfo(info_title, info_text)
        enable_buttons(analysis_buttons_list)


    # Setting effective font sizes and positions (numbers are reference values)
    eff_etape_font_size = font_size(gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)           # 14
    eff_launch_font_size = font_size(gg.REF_ETAPE_FONT_SIZE-1, master.width_sf_min)
    eff_help_font_size = font_size(gg.REF_ETAPE_FONT_SIZE-2, master.width_sf_min)
    eff_select_font_size = font_size(gg.REF_ETAPE_FONT_SIZE, master.width_sf_min)
    eff_buttons_font_size = font_size(gg.REF_ETAPE_FONT_SIZE-3, master.width_sf_min)
    progress_bar_length_px = mm_to_px(100 * master.width_sf_mm, gg.PPI)
    progress_bar_dx = 50
    if_analysis_x_pos_px = mm_to_px(10 * master.width_sf_mm, gg.PPI)
    if_analysis_y_pos_px = mm_to_px(40 * master.height_sf_mm, gg.PPI)
    title_dy = 20
    au_analysis_label_dx_px = mm_to_px(0 * master.width_sf_mm, gg.PPI)
    au_analysis_label_dy_px = mm_to_px(title_dy * master.height_sf_mm, gg.PPI)
    co_analysis_label_dx_px = mm_to_px(0 * master.width_sf_mm, gg.PPI)
    co_analysis_label_dy_px = mm_to_px(title_dy * master.height_sf_mm, gg.PPI)
    kw_analysis_label_dx_px = mm_to_px(0 * master.width_sf_mm, gg.PPI)
    kw_analysis_label_dy_px = mm_to_px(title_dy * master.height_sf_mm, gg.PPI)

    launch_dx_px = mm_to_px(10 * master.width_sf_mm, gg.PPI)
    launch_dy_px = mm_to_px(2 * master.height_sf_mm, gg.PPI)
    year_button_x_pos = mm_to_px(gg.REF_YEAR_BUT_POS_X_MM * master.width_sf_mm, gg.PPI)     # 10
    year_button_y_pos = mm_to_px(gg.REF_YEAR_BUT_POS_Y_MM * master.height_sf_mm, gg.PPI)    # 26
    year_dy = -6
    help_dx = mm_to_px(100 * master.width_sf_mm, gg.PPI)
    help_dy = mm_to_px(0 * master.width_sf_mm, gg.PPI)

    # Setting common attributes
    etape_label_format = 'left'
    etape_underline = -1

    # Setting aliases for saving results independent of corpus year
    results_root_alias = pg.ARCHI_RESULTS["root"]
    results_folder_alias = pg.ARCHI_RESULTS[datatype]

    # Setting paths for saving results independent of corpus year
    results_root_path = bibliometer_path / Path(results_root_alias)
    results_folder_path = results_root_path / Path(results_folder_alias)

    # Getting institute parameters
    org_tup = set_org_params(institute, bibliometer_path)

    # Creating and setting widgets for page title and exit button
    set_page_title(self, master, page_name, institute, datatype)
    set_exit_button(self, master)

    # Creating and setting year selection widgets
    default_year = master.years_list[-1]
    variable_years = tk.StringVar(self)
    variable_years.set(default_year)

    # - Creating years button option
    self.font_OptionButton_years = tkFont.Font(family=gg.FONT_NAME,
                                               size=eff_buttons_font_size)
    self.OptionButton_years = tk.OptionMenu(self,
                                            variable_years,
                                            *master.years_list)
    self.OptionButton_years.config(font=self.font_OptionButton_years)
    GUI_BUTTONS.append(self.OptionButton_years)

    # - Creating year selection label
    self.font_Label_years = tkFont.Font(family=gg.FONT_NAME,
                                        size=eff_select_font_size,
                                        weight='bold')
    self.Label_years = tk.Label(self,
                                text=gg.TEXT_YEAR_PI,
                                font=self.font_Label_years)
    self.Label_years.place(x=year_button_x_pos, y=year_button_y_pos)

    place_after(self.Label_years, self.OptionButton_years, dy=year_dy)

    # Creating help button
    help_text = (f" - {gg.ANALYSIS_TEXT_DICT['if'][1]}\n\n"
                 f" - {gg.ANALYSIS_TEXT_DICT['au'][1]}\n\n"
                 f" - {gg.ANALYSIS_TEXT_DICT['co'][1]}\n\n"
                 f" - {gg.ANALYSIS_TEXT_DICT['kw'][1]}\n\n"
                )
    help_label_font = tkFont.Font(family=gg.FONT_NAME,
                                  size=eff_help_font_size)
    help_button = tk.Button(self,
                            text='Description',
                            font=help_label_font,
                            command=partial(_edit_help, help_text))
    place_after(self.OptionButton_years, help_button, dx=help_dx, dy = help_dy)

    # Initializing progress bar widget
    progress_var = tk.IntVar()  # Variable to keep track of the progress bar value
    progress_bar = ttk.Progressbar(self,
                                   orient="horizontal",
                                   length=progress_bar_length_px,
                                   mode="determinate",
                                   variable=progress_var)

    # Creating and setting impact-factors analysis widgets
    title = gg.ANALYSIS_TEXT_DICT["if"][0]
    launch_text = gg.ANALYSIS_TEXT_DICT["if"][2]

    # - Setting title
    if_analysis_font = tkFont.Font(family=gg.FONT_NAME,
                                   size=eff_etape_font_size,
                                   weight='bold')
    if_analysis_label = tk.Label(self,
                                 text=title,
                                 justify=etape_label_format,
                                 font=if_analysis_font,
                                 underline=etape_underline)

    if_analysis_label.place(x=if_analysis_x_pos_px,
                            y=if_analysis_y_pos_px)

    # - Setting launch button
    if_analysis_launch_font = tkFont.Font(family=gg.FONT_NAME,
                                          size=eff_launch_font_size)
    if_analysis_launch_button = tk.Button(self,
                                          text=launch_text,
                                          font=if_analysis_launch_font,
                                          command= _start_launch_if_analysis_try)
    GUI_BUTTONS.append(if_analysis_launch_button)
    place_bellow(if_analysis_label,
                 if_analysis_launch_button,
                 dx=launch_dx_px,
                 dy=launch_dy_px)

    # Creating and setting authors analysis widgets
    title = gg.ANALYSIS_TEXT_DICT["au"][0]
    launch_text = gg.ANALYSIS_TEXT_DICT["au"][2]

    # - Setting title
    au_analysis_font = tkFont.Font(family=gg.FONT_NAME,
                                   size=eff_etape_font_size,
                                   weight='bold')
    au_analysis_label = tk.Label(self,
                                 text=title,
                                 justify=etape_label_format,
                                 font=au_analysis_font,
                                 underline=etape_underline)
    place_bellow(if_analysis_label,
                 au_analysis_label,
                 dx=au_analysis_label_dx_px,
                 dy=au_analysis_label_dy_px)

    # - Setting launch button
    au_analysis_launch_font = tkFont.Font(family=gg.FONT_NAME,
                                          size=eff_launch_font_size)
    au_analysis_launch_button = tk.Button(self,
                                          text=launch_text,
                                          font=au_analysis_launch_font,
                                          command= _start_launch_au_analysis_try)
    place_bellow(au_analysis_label,
                 au_analysis_launch_button,
                 dx=launch_dx_px,
                 dy=launch_dy_px)

    # Creating and setting coupling analysis widgets
    title = gg.ANALYSIS_TEXT_DICT["co"][0]
    launch_text = gg.ANALYSIS_TEXT_DICT["co"][2]

    # - Setting title
    co_analysis_label_font = tkFont.Font(family=gg.FONT_NAME,
                                         size=eff_etape_font_size,
                                         weight='bold')
    co_analysis_label = tk.Label(self,
                                 text=title,
                                 justify="left",
                                 font=co_analysis_label_font)
    place_bellow(au_analysis_label,
                 co_analysis_label,
                 dx=co_analysis_label_dx_px,
                 dy=co_analysis_label_dy_px)

    # - Setting launch button
    co_analysis_launch_font = tkFont.Font(family=gg.FONT_NAME,
                                          size=eff_launch_font_size)
    co_analysis_launch_button = tk.Button(self,
                                          text = launch_text,
                                          font = co_analysis_launch_font,
                                          command = _start_launch_coupling_analysis_try)
    GUI_BUTTONS.append(co_analysis_launch_button)
    place_bellow(co_analysis_label,
                 co_analysis_launch_button,
                 dx=launch_dx_px,
                 dy=launch_dy_px)

    # Creating and setting keywords analysis widgets
    title = gg.ANALYSIS_TEXT_DICT["kw"][0]
    launch_text = gg.ANALYSIS_TEXT_DICT["kw"][2]

    # - Setting title
    kw_analysis_label_font = tkFont.Font(family = gg.FONT_NAME,
                                         size = eff_etape_font_size,
                                         weight = 'bold')
    kw_analysis_label = tk.Label(self,
                                 text=title,
                                 justify="left",
                                 font=kw_analysis_label_font)
    place_bellow(co_analysis_label,
                 kw_analysis_label,
                 dx=kw_analysis_label_dx_px,
                 dy=kw_analysis_label_dy_px)

    # - Setting launch button
    kw_analysis_launch_font = tkFont.Font(family=gg.FONT_NAME,
                                          size=eff_launch_font_size)
    kw_analysis_launch_button = tk.Button(self,
                                          text=launch_text,
                                          font=kw_analysis_launch_font,
                                          command= _start_launch_kw_analysis_try)
    GUI_BUTTONS.append(kw_analysis_launch_button)
    place_bellow(kw_analysis_label,
                 kw_analysis_launch_button,
                 dx=launch_dx_px,
                 dy=launch_dy_px)

    # Setting buttons list for status change
    analysis_buttons_list = [self.OptionButton_years,
                             if_analysis_launch_button,
                             au_analysis_launch_button,
                             co_analysis_launch_button,
                             kw_analysis_launch_button]
