""" `gui_utils` module contains useful functions for gui management."""

__all__ = ['change_tup_value',
           'disable_buttons',
           'enable_buttons',
           'existing_corpuses',
           'font_size',
           'general_properties',
           'last_available_years',
           'mm_to_px',
           'place_after',
           'place_bellow',
           'set_display_width',
           'set_exit_button',
           'set_font_size_tup',
           'set_item_pos',
           'set_page_title',
           'set_pos_tup_px',
           'set_pos_tup_px_list',
           'set_progress_bar_pos_tup',
           'show_frame',
           ]


# Standard library imports
import os
import math
import tkinter as tk
from pathlib import Path
from tkinter import font as tkFont
from tkinter import messagebox

# 3rd party imports
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
from bmfuncts.config_utils import set_user_config


def change_tup_value(init_tup, chg_idx, new_value):
    tup_to_list = list(init_tup)
    tup_to_list[chg_idx] = new_value
    new_tup = tuple(tup_to_list)
    return new_tup


def disable_buttons(buttons_list):
    """Disables use of tkinter widgets listed in 'buttons_list'."""
    for button in buttons_list:
        button.config(state=tk.DISABLED)

def enable_buttons(buttons_list):
    """Enables use of tkinter widgets listed in 'buttons_list'."""
    for button in buttons_list:
        button.config(state=tk.NORMAL)


def show_frame(self, page_name):
    """Show a frame for the 'page_name' page."""
    frame = self.frames[page_name]
    frame.tkraise()


def set_pos_tup_px(master, pos_tup):
    idx_list = [0,1]
    if pos_tup[0]=="mid_page":
        pos_px_tup = (None, mm_to_px(pos_tup[1] * master.sf_mm_tup[1], bm_gg.PPI))
    else:
        pos_px_tup = tuple([mm_to_px(pos_tup[idx] * master.sf_mm_tup[idx],
                                     bm_gg.PPI) for idx in [0,1]])
    return pos_px_tup


def set_pos_tup_px_list(master, pos_tup_list):
    pos_px_tup_list = [set_pos_tup_px(master, pos_tup)
                       for pos_tup in pos_tup_list]
    return pos_px_tup_list


def set_font_size_tup(master, font_dict, items):
    font_size_list = [font_size(font_dict[item], master.width_sf_min)
                      for item in items]
    return tuple(font_size_list)

        
def set_item_pos(master, value_mm, fact_idx):
    item_pos = mm_to_px(value_mm * master.sf_mm_tup[fact_idx], bm_gg.PPI)
    return item_pos

       
def set_display_width(master, item):
    item_width = int(bm_gg.MAIN_CHAR_NB_DICT[item] * master.width_sf_min)
    return item_width


def set_progress_bar_pos_tup(master, page_key):
    # Setting progress_bar parameters in px
    bar_len = mm_to_px(bm_gg.PROGRESS_BAR_LEN_DICT[page_key]\
                       * master.width_sf_mm, bm_gg.PPI)

    bar_dx = mm_to_px(bm_gg.PROGRESS_BAR_DPOS_DICT[page_key][0]\
                      * master.width_sf_mm, bm_gg.PPI)

    bar_dy = mm_to_px(bm_gg.PROGRESS_BAR_DPOS_DICT[page_key][1]\
                      * master.width_sf_mm, bm_gg.PPI)
    return bar_len, bar_dx, bar_dy


def set_page_title(self, master, page_label, institute, datatype=None):
    """Sets the page title of the 'page_name' page.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of 'page_name' page.
        institute (str): Institute name.
        datatype (str): Optional data combination type from corpuses \
        (default = None).        
    """
    # internal functions
    def _set_title_widgets(item):        
        title_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                       size=title_font_size[item])
        self.label = tk.Label(self,
                              text=page_title[item],
                              font=title_label_font)
        self.label.place(x=title_x_pos,
                         y=title_y_pos[item],
                         anchor="center")

    sub_title_add = ""
    if datatype:
        sub_title_add = f" - {datatype}"
    
    # Setting page titles
    page_title = {'page_title'     : f"{page_label}",
                  'page_sub_title' : f"{institute}{sub_title_add}"}

    # Setting short names for window factors for positions setting in px
    h_sf_mm = master.height_sf_mm
    w_sf_min = master.width_sf_min

    # Setting font size for page titles
    title_font_size = {'page_title'    : font_size(bm_gg.PAGE_FONT_SIZE_DICT['page_title'],
                                                   w_sf_min),
                       'page_sub_title': font_size(bm_gg.PAGE_FONT_SIZE_DICT['page_sub_title'],
                                                   w_sf_min),}
    title_x_pos = master.mid_x_pos
    title_y_pos = {'page_title'    : mm_to_px(bm_gg.PAGE_TITLE_POS_DICT['page_title'][1]\
                                              * h_sf_mm, bm_gg.PPI),
                   'page_sub_title': mm_to_px(bm_gg.PAGE_TITLE_POS_DICT['page_sub_title'][1]\
                                              * h_sf_mm, bm_gg.PPI),}

    # Creating title widget
    _set_title_widgets('page_title')

    # Creating sub-title widget
    _set_title_widgets('page_sub_title')


def set_exit_button(self, master):
    """Sets exit button on any page of 'master'.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
    """
    # Internal functions
    def _launch_exit():
        ask_title = "Arrêt de l'application"
        ask_text = ("Les traitements intermédiaires effectués sont sauvegardés."
                    "\n\nConfirmez la mise en pause ?")
        exit_answer = messagebox.askokcancel(ask_title, ask_text)
        if exit_answer:
            master.destroy()

    # Setting useful local variables for positions modification (globals to create ??)
    # numbers are reference values in mm for reference screen
    exit_font_size = font_size(bm_gg.PAGE_FONT_SIZE_DICT['exit_button'],
                               master.width_sf_min)
    exit_x_pos = mm_to_px(bm_gg.EXIT_BUT_POS_TUP[0]\
                          * master.width_sf_mm, bm_gg.PPI)
    exit_y_pos = mm_to_px(bm_gg.EXIT_BUT_POS_TUP[1]\
                          * master.height_sf_mm, bm_gg.PPI)

    # Setting widget for exit button
    button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                              size=exit_font_size)
    button_label = tk.Button(self,
                             text=bm_gg.EXIT_LABEL,
                             font=button_font,
                             command=_launch_exit)
    button_label.place(x=exit_x_pos,
                       y=exit_y_pos,
                       anchor='n')


def last_available_years(wf_path, year_number):
    """Returns a list of up to 'year_number' number 
    of the most-recent years of available corpuses 
    in the working folder targetted by 'wf_path'.

    Args:
        wf_path (path): Full path to working folder.
        year_number (int): Data combination type from corpuses databases.
    Returns:
        (list): List of 'year_number' length of available corpuses \
        as strings of 4 digits.    
    """
    # Setting warning parameters
    warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
    warning_text = (f"L'accès au dossier {wf_path} est impossible."
                    "\nChoisissez un autre dossier de travail.")

    # Get list of available corpuses
    try:
        list_dir = sorted(os.listdir(wf_path))
        years_full_list = []

        for year in list_dir:
            if len(year)==4:
                years_full_list.append(year)

        years_list = years_full_list[-year_number:]

    except FileNotFoundError:
        warning_title = "!!! ATTENTION : Dossier de travail non disponible !!!"
        warning_text = (f"Le dossier {wf_path} est introuvable."
                        "\nChoisissez un autre dossier de travail.")
        messagebox.showwarning(warning_title, warning_text)
        years_list = []

    except OSError:
        warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
        warning_text = (f"L'accès au dossier {wf_path} est impossible."
                        "\nChoisissez un autre dossier de travail.")
        messagebox.showwarning(warning_title, warning_text)
        years_list = []

    return years_list


def existing_corpuses(wf_path, corpuses_number=None):
    """Returns a list of lists of booleans displaying True
    if rawdata and parsing results are available, and False otherwise.

    This is done for each of the available corpuses.        
        ex: If only 2023 files are not present, the returned tuple of lists contains

        - Years list                          = ["2018", "2019", "2020", "2021", "2022", "2023"]
        - WoS raw-data boolean list           = [ True,   True,   True,   True,   True,   False]
        - WoS parsing boolean list            = [ True,   True,   True,   True,   True,   False]
        - Scopus raw-data boolean list        = [ True,   True,   True,   True,   True,   False]
        - Scopus parsing boolean list         = [ True,   True,   True,   True,   True,   False]
        - Deduplication parsing boolean list  = [ True,   True,   True,   True,   True,   False]

    Args:
        wf_path (path):  Full path to working folder.
        corpuses_number (int): The number of corpuses to be checked \
        (default: CORPUSES_NUMBER global).
    Returns:
        (tup of lists): (Years list, WoS raw-data boolean list, \
        WoS parsing boolean list, Scopus raw-data boolean list, \
        Scopus parsing boolean list, Deduplication parsing boolean list).
    """

    # internal functions
    def _get_rawdata_file_path(rawdata_path, rawdata_extent):
        """Returns the name of the rawdata file with 'rawdata_extent' extention
        pointed by the full path 'rawdata_path'.
        """

        filenames_list = []
        for _, _, files in os.walk(rawdata_path):
            filenames_list.extend(file for file in files if file.endswith("." + rawdata_extent))
        if not filenames_list:
            return Path(f'{database_type} rawdata file not Found')
        return rawdata_path / Path(filenames_list[0])

    def _get_parsing_file_paths(parsing_path):
        """Returns the full path to the file named 'articles_item_alias' 
        given the full path to the parsing folder 'parsing_path' 
        and the extension 'parsing_save_extent' of the file.
        """
        file_name = articles_item_alias + "." + parsing_save_extent
        parsing_file_path = parsing_path / Path(file_name)
        return parsing_file_path

    # Getting the last available corpus years
    if not corpuses_number:
        corpuses_number = bm_gg.CORPUSES_NUMBER
    years_folder_list = last_available_years(wf_path, corpuses_number)

    # Setting the files type of raw data and saved parsing results
    parsing_save_extent = bm_pg.TSV_SAVE_EXTENT
    wos_rawdata_extent = bp.WOS_RAWDATA_EXTENT
    scopus_rawdata_extent = bp.SCOPUS_RAWDATA_EXTENT

    # Setting articles item alias for checking availability of parsing
    articles_item_alias = bp.PARSING_ITEMS_LIST[0]

    # Initialization of lists
    years_list = []
    wos_rawdata_list = []
    wos_parsing_list = []
    scopus_rawdata_list = []
    scopus_parsing_list = []
    dedup_parsing_list = []

    for year in years_folder_list:

        # Getting the full paths of the working folder architecture for the corpus "year"
        config_tup = set_user_config(wf_path, year, bm_pg.BDD_LIST)
        rawdata_path_dict, parsing_path_dict = config_tup[0], config_tup[1]

        # Setting useful paths for database 'database_type'
        scopus_rawdata_path = rawdata_path_dict["scopus"]
        wos_rawdata_path = rawdata_path_dict["wos"]
        scopus_parsing_path = parsing_path_dict["scopus"]
        wos_parsing_path = parsing_path_dict["wos"]
        dedup_parsing_path = parsing_path_dict["dedup"]

        years_list.append(year)

        # Wos
        database_type = bp.WOS
        wos_rawdata_file_path = _get_rawdata_file_path(wos_rawdata_path,
                                                       wos_rawdata_extent)
        wos_parsing_articles_path = _get_parsing_file_paths(wos_parsing_path)
        wos_rawdata_list.append(wos_rawdata_file_path.is_file())
        wos_parsing_list.append(wos_parsing_articles_path.is_file())

        # Scopus
        database_type = bp.SCOPUS
        scopus_rawdata_file_path = _get_rawdata_file_path(scopus_rawdata_path,
                                                          scopus_rawdata_extent)
        scopus_parsing_articles_path = _get_parsing_file_paths(scopus_parsing_path)
        scopus_rawdata_list.append(scopus_rawdata_file_path.is_file())
        scopus_parsing_list.append(scopus_parsing_articles_path.is_file())

        # Concatenation and deduplication
        dedup_parsing_articles_path = _get_parsing_file_paths(dedup_parsing_path)
        dedup_parsing_list.append(dedup_parsing_articles_path.is_file())

    return (years_list, wos_rawdata_list, wos_parsing_list,
            scopus_rawdata_list, scopus_parsing_list, dedup_parsing_list)


def place_after(gauche, droite, dx=5, dy=0):
    """Places widget 'droite' after widget 'gauche' 
    by dx shift in pixels on x axis without shift on y axis.
    """
    gauche_info = gauche.place_info()
    x = int(gauche_info['x']) + gauche.winfo_reqwidth() + dx
    y = int(gauche_info['y']) + dy
    droite.place(x=x, y=y)


def place_bellow(haut, bas, dx=0, dy=5):
    """Places widget 'bas' after widget 'haut' 
    by dy shift in pixels on y axis without shift on x axis.
    """
    haut_info = haut.place_info()
    x = int(haut_info['x']) + dx
    y = int(haut_info['y']) + haut.winfo_reqheight() + dy
    bas.place(x=x, y=y)


def font_size(size, scale_factor):
    """Sets the font-size based on scale_factor.
    
    If the font-size is less than minimum_size, 
    it is set to the minimum size.
    """
    fontsize = int(size * scale_factor)
    fontsize = max(fontsize, 8)
    return fontsize


def mm_to_px(size_mm, ppi, fact=1.0):
    """The `mm_to_px` function converts a value in mm to a value in pixels
    using the display resolution and a factor fact to adjust the result if needed.

    Args:
        size_mm (float): The value in mm to be converted.
        ppi (float): The display resolution in pixels per inch.
        fact (float): Adjusting factor (default= 1).
    Returns:
        (int): Upper integer value of the conversion to pixels.
    """
    size_px = math.ceil((size_mm * fact / bm_gg.IN_TO_MM) * ppi)
    return size_px


def _window_properties(screen_width_px, screen_height_px):
    """Computes useful values for adapting tkinter windows 
    and widgets positions to the display resolution using reference 
    values given as globals in module imported as bm_gg.

    Args:
        screen_width_px (int): The display screen width in pixel.
        screen_height_px (int): The display screen height in pixel.
    Returns:
        (tup): (width of reference window converted to px, \
        height of reference window converted to px, \
        scale factor on width in px, \
        scale factor on height in px, \
        scale factor on width in mm, \
        scale factor on height in mm).
    """

    # Getting number of pixels per inch screen resolution from imported global DISPLAYS
    ppi = bm_gg.DISPLAYS[bm_gg.BM_GUI_DISP]["ppi"]

    # Setting screen effective sizes in mm from imported global DISPLAYS
    screen_width_mm = bm_gg.DISPLAYS[bm_gg.BM_GUI_DISP]["width_mm"]
    screen_height_mm = bm_gg.DISPLAYS[bm_gg.BM_GUI_DISP]["height_mm"]

    # Setting screen reference sizes in pixels and mm
    ref_width_px = bm_gg.TK_SIZES_REF['display_px'][0]
    ref_height_px = bm_gg.TK_SIZES_REF['display_px'][1]
    ref_width_mm = bm_gg.TK_SIZES_REF['display_mm'][0]
    ref_height_mm = bm_gg.TK_SIZES_REF['display_mm'][1]

    # Setting secondary window reference sizes in mm
    ref_window_width_mm = bm_gg.TK_SIZES_REF['window_mm'][0]
    ref_window_height_mm = bm_gg.TK_SIZES_REF['window_mm'][1]

    # Computing ratii of effective screen sizes to screen reference sizes in pixels
    scale_factor_width_px  = screen_width_px / ref_width_px
    scale_factor_height_px = screen_height_px / ref_height_px

    # Computing ratii of effective screen sizes to screen reference sizes in mm
    scale_factor_width_mm = screen_width_mm / ref_width_mm
    scale_factor_height_mm = screen_height_mm / ref_height_mm

    # Computing secondary window sizes in pixels depending on scale factors
    win_width_px = mm_to_px(ref_window_width_mm * scale_factor_width_mm, ppi)
    win_height_px = mm_to_px(ref_window_height_mm * scale_factor_height_mm, ppi)

    sizes_tuple = (win_width_px, win_height_px,
                   scale_factor_width_px, scale_factor_height_px,
                   scale_factor_width_mm, scale_factor_height_mm)
    return sizes_tuple


def general_properties(self):
    """The function `general_properties` calculate the window sizes
    and useful scale factors for the application launch window through
    `_window_properties` internal function.

    The window title is set through the global "APPLICATION_TITLE". 
    These globals are defined locally in the module imported as bm_gg.

    Args:
        self (instense): Instense where application launch window is created.
    Returns:
        (tup): (width of reference window converted to px, \
        height of reference window converted to px, \
        scale factor on width in px, \
        scale factor on height in px, \
        scale factor on width in mm, \
        scale factor on height in mm).
    """

    # Getting screen effective sizes in pixels for window "root" (not woring for Darwin platform)
    screen_width_px  = self.winfo_screenwidth()
    screen_height_px = self.winfo_screenheight()

    sizes_tuple = _window_properties(screen_width_px, screen_height_px)
    win_width_px = sizes_tuple[0]
    win_height_px = sizes_tuple[1]

    # Setting window size depending on scale factor
    self.geometry(f"{win_width_px}x{win_height_px}")
    self.resizable(False, False)

    # Setting title window
    self.title(bm_gg.APP_WIN_TITLE)
    return sizes_tuple
