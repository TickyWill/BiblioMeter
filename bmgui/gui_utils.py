""" `gui_functions` module contains useful functions for gui management."""

__all__ = ['disable_buttons',
           'enable_buttons',
           'existing_corpuses',
           'font_size',
           'general_properties',
           'last_available_years',
           'mm_to_px',
           'place_after',
           'place_bellow',
           'str_size_mm',
           'set_exit_button',
           'set_page_title',
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
import bmfuncts.pub_globals as pg
import bmgui.gui_globals as gg
from bmfuncts.config_utils import set_user_config


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


def set_page_title(self, master, page_name, institute, datatype = None):
    """Sets the page title of the 'page_name' page.

    Args:
        self (instense): Instense where is located 'page_name' page.
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Name of 'page_name' page.
        institute (str): Institute name.
        datatype (str): Data combination type from corpuses databases (default = None). 

    Returns:
        None.
        
    """

    # Setting page title
    label_text = gg.PAGES_LABELS[page_name]
    page_title = label_text + " du " + institute

    # Setting font size for page label and button
    eff_label_font_size = font_size(gg.REF_LABEL_FONT_SIZE, master.width_sf_min)
    eff_label_pos_y_px  = mm_to_px(gg.REF_LABEL_POS_Y_MM * master.height_sf_mm, gg.PPI)
    eff_dy_px           = mm_to_px(gg.REF_LABEL_DX_Y_MM * master.height_sf_mm, gg.PPI)
    mid_page_pos_x_px   = master.win_width_px * 0.5

    # Creating title widget
    label_font = tkFont.Font(family = gg.FONT_NAME,
                             size   = eff_label_font_size)
    self.label = tk.Label(self,
                          text = page_title,
                          font = label_font)
    self.label.place(x = mid_page_pos_x_px,
                     y = eff_label_pos_y_px,
                     anchor = "center")

    if datatype:
        page_sub_title = f"Données {datatype}"

        # Creating title widget
        label_font = tkFont.Font(family = gg.FONT_NAME,
                                 size   = int(eff_label_font_size * 0.7))
        self.label = tk.Label(self,
                              text = page_sub_title,
                              font = label_font)
        self.label.place(x = mid_page_pos_x_px,
                         y = eff_label_pos_y_px + eff_dy_px,
                         anchor = "center")


def set_exit_button(self, master):
    """Sets exit button on any page of 'master'.

    Args:
        self (instense): Instense where is located 'master'.
        master (class): `bmgui.main_page.AppMain` class.

    Returns:
        None.
        
    """
    # Internal functions
    def _launch_exit():
        ask_title = 'Arrêt de BiblioMeter'
        ask_text =  ("Après la fermeture des fenêtres, "
                     "les traitements intermédiaires effectués sont sauvegardés."
                     "\n\n     !!! Attention !!!"
                     "\nSi le type de données est modifié à la reprise "
                     "\ndu traitement, ces traitements seront écrasés."
                     "\nConfirmez la mise en pause ?")
        exit_answer = messagebox.askokcancel(ask_title, ask_text)
        if exit_answer:
            master.destroy()

    # Setting useful local variables for positions modification (globals to create ??)
    # numbers are reference values in mm for reference screen
    exit_button_x_pos     = mm_to_px(gg.REF_EXIT_BUT_POS_X_MM * master.width_sf_mm,  gg.PPI)
    exit_button_y_pos     = mm_to_px(gg.REF_EXIT_BUT_POS_Y_MM * master.height_sf_mm, gg.PPI)
    eff_buttons_font_size = font_size(11, master.width_sf_min)

    # Setting widget for exit button
    font_button_quit = tkFont.Font(family = gg.FONT_NAME,
                                   size   = eff_buttons_font_size)
    button_quit = tk.Button(self,
                            text = gg.TEXT_PAUSE,
                            font = font_button_quit,
                            command = _launch_exit)
    button_quit.place(x = exit_button_x_pos,
                      y = exit_button_y_pos,
                      anchor = 'n')


def last_available_years(bibliometer_path, year_number):
    """Returns a list of up to 'year_number' number 
    of the most-recent years of available corpuses 
    in the working folder targetted by 'bibliometer_path'.

    Args:
        bibliometer_path (path): Full path to working folder.
        year_number (int): Data combination type from corpuses databases.

    Returns:
        (list): List of 'year_number' length of available corpuses as strings of 4 digits.    
    """

    # Récupérer les corpus disponibles TO DO : consolider le choix des années
    try:
        list_dir = os.listdir(bibliometer_path)
        years_full_list = []

        for year in list_dir:
            if len(year) == 4:
                years_full_list.append(year)

        years_list = years_full_list[-year_number:]

    except FileNotFoundError:
        warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
        warning_text  = (f"L'accès au dossier {bibliometer_path} est impossible."
                         "\nChoisissez un autre dossier de travail.")
        messagebox.showwarning(warning_title, warning_text)
        years_list = []

    except OSError:
        warning_title = "!!! ATTENTION : Erreur lors de l'accès au dossier de travail !!!"
        warning_text = (f"L'accès au dossier {bibliometer_path} a échoué (erreur interne)"
                        "\nVeuillez réessayer d'accéder à votre répertoire de travail avec "
                        "l'option \"Changer de dossier de travail\"")
        messagebox.showwarning(warning_title, warning_text)
        years_list = []

    return years_list


def existing_corpuses(bibliometer_path, corpuses_number = None):
    """Returns a list of lists of booleans displaying True
    if rawdata and parsing results are available, and False otherwise.
    This is done for each of the available corpuses.
    ex:
    If only 2023 files are not present, the returned tuple of lists is the following:
    (["2018", "2019", "2020", "2021", "2022", "2023"],   # Years
     [True,True,True,True,True,False],                   # WoS raw-data
     [True,True,True,True,True,False],                   # Scopus raw-data
     [True,True,True,True,True,False],                   # WoS parsing
     [True,True,True,True,True,False],                   # Scopus parsing
     [True,True,True,True,True,False])                   # Deduplication parsing.

    Args:
        bibliometer_path (path):  Full path to working folder.
        corpuses_number (int): The number of corpuses to be checked 
                               (default: CORPUSES_NUMBER global).

    Returns:
        (tup of lists): Tuple = (years list, 
                                 WoS raw-data boolean list,
                                 WoS parsing boolean list,
                                 Scopus raw-data boolean list,
                                 Scopus parsing boolean list,
                                 Deduplication parsing boolean list).
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
        corpuses_number = gg.CORPUSES_NUMBER
    years_folder_list = last_available_years(bibliometer_path, corpuses_number)

    # Setting the files type of raw data and saved parsing results
    parsing_save_extent   = pg.TSV_SAVE_EXTENT
    wos_rawdata_extent    = bp.WOS_RAWDATA_EXTENT
    scopus_rawdata_extent = bp.SCOPUS_RAWDATA_EXTENT

    # Setting articles item alias for checking availability of parsing
    articles_item_alias = bp.PARSING_ITEMS_LIST[0]

    # Initialization of lists
    years_list          = []
    wos_rawdata_list    = []
    wos_parsing_list    = []
    scopus_rawdata_list = []
    scopus_parsing_list = []
    dedup_parsing_list  = []

    for year in years_folder_list:

        # Getting the full paths of the working folder architecture for the corpus "year"
        config_tup = set_user_config(bibliometer_path, year, pg.BDD_LIST)
        rawdata_path_dict, parsing_path_dict = config_tup[0], config_tup[1]

        # Setting useful paths for database 'database_type'
        scopus_rawdata_path = rawdata_path_dict["scopus"]
        wos_rawdata_path    = rawdata_path_dict["wos"]
        scopus_parsing_path = parsing_path_dict["scopus"]
        wos_parsing_path    = parsing_path_dict["wos"]
        dedup_parsing_path  = parsing_path_dict["dedup"]

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


def place_after(gauche, droite, dx = 5, dy = 0):
    """Places widget 'droite' after widget 'gauche' 
    by dx shift in pixels on x axis without shift on y axis.
    """
    gauche_info = gauche.place_info()
    x = int(gauche_info['x']) + gauche.winfo_reqwidth() + dx
    y = int(gauche_info['y']) + dy
    droite.place(x = x, y = y)


def place_bellow(haut, bas, dx = 0, dy = 5):
    """Places widget 'bas' after widget 'haut' 
    by dy shift in pixels on y axis without shift on x axis.
    """
    haut_info = haut.place_info()
    x = int(haut_info['x']) + dx
    y = int(haut_info['y']) + haut.winfo_reqheight() + dy
    bas.place(x = x, y = y)


def font_size(size, scale_factor):
    """Sets the font-size based on scale_factor.
    If the font-size is less than minimum_size,
    it is set to the minimum size.
    """
    fontsize = int(size * scale_factor)
    fontsize = max(fontsize, 8)
    return fontsize


def str_size_mm(text, font, ppi):
    """The function `str_size_mm` computes the sizes in mm of a string
    given the font name and the resolution of the display.

    Args:
        text (str): The text of which we compute the size in mm.
        font (tk.font): The font for displaying the string 'text'.
        ppi (int): The display resolution in pixels per inch.

    Returns:
        (tup): Tuple = (width in mm (float), height in mm (float)).

    Note:
        The use of this function requires a tkinter window availability
        since it is based on a tkinter font definition.
    """
    w_px, h_px = font.measure(text), font.metrics("linespace")
    w_mm = w_px * gg.IN_TO_MM / ppi
    h_mm = h_px * gg.IN_TO_MM / ppi
    return w_mm, h_mm


def mm_to_px(size_mm, ppi, fact = 1.0):
    """The `mm_to_px` function converts a value in mm to a value in pixels
    using the display resolution and a factor fact to adjust the result if needed.

    Args:
        size_mm (float): The value in mm to be converted.
        ppi (float): The display resolution in pixels per inch.
        fact (float): Adjusting factor (default= 1).

    Returns:
        (int): Upper integer value of the conversion to pixels.
    """
    size_px = math.ceil((size_mm * fact / gg.IN_TO_MM) * ppi)
    return size_px


def _window_properties(screen_width_px, screen_height_px):
    """Computes useful values for adapting tkinter windows 
    and widgets positions to the display resolution using reference 
    values given as globals in module imported as gg.

    Args:
        screen_width_px (int): The display screen width in pixel.
        screen_height_px (int): The display screen height in pixel.

    Returns:
        (tup): Tuple = (width of reference window converted to px,
                        height of reference window converted to px,
                        scale factor on width in px,
                        scale factor on height in px,
                        scale factor on width in mm,
                        scale factor on height in mm).
    """

    # Getting number of pixels per inch screen resolution from imported global DISPLAYS
    ppi = gg.DISPLAYS[gg.BM_GUI_DISP]["ppi"]

    # Setting screen effective sizes in mm from imported global DISPLAYS
    screen_width_mm  = gg.DISPLAYS[gg.BM_GUI_DISP]["width_mm"]
    screen_height_mm = gg.DISPLAYS[gg.BM_GUI_DISP]["height_mm"]

    # Setting screen reference sizes in pixels and mm
    ref_width_px  = gg.REF_SCREEN_WIDTH_PX
    ref_height_px = gg.REF_SCREEN_HEIGHT_PX
    ref_width_mm  = gg.REF_SCREEN_WIDTH_MM
    ref_height_mm = gg.REF_SCREEN_HEIGHT_MM

    # Setting secondary window reference sizes in mm
    ref_window_width_mm  = gg.REF_WINDOW_WIDTH_MM
    ref_window_height_mm = gg.REF_WINDOW_HEIGHT_MM

    # Computing ratii of effective screen sizes to screen reference sizes in pixels
    scale_factor_width_px  = screen_width_px / ref_width_px
    scale_factor_height_px = screen_height_px / ref_height_px

    # Computing ratii of effective screen sizes to screen reference sizes in mm
    scale_factor_width_mm  = screen_width_mm / ref_width_mm
    scale_factor_height_mm = screen_height_mm / ref_height_mm

    # Computing secondary window sizes in pixels depending on scale factors
    win_width_px  = mm_to_px(ref_window_width_mm * scale_factor_width_mm, ppi)
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
    These globals are defined locally in the module imported as gg.

    Args:
        self (instense): Instense where application launch window is created.

    Returns:
        (tup): Tuple = (width of reference window converted to px,
                        height of reference window converted to px,
                        scale factor on width in px,
                        scale factor on height in px,
                        scale factor on width in mm,
                        scale factor on height in mm).
    """

    # Getting screen effective sizes in pixels for window "root" (not woring for Darwin platform)
    screen_width_px  = self.winfo_screenwidth()
    screen_height_px = self.winfo_screenheight()

    sizes_tuple = _window_properties(screen_width_px, screen_height_px)
    win_width_px  = sizes_tuple[0]
    win_height_px = sizes_tuple[1]

    # Setting window size depending on scale factor
    self.geometry(f"{win_width_px}x{win_height_px}")
    self.resizable(False, False)

    # Setting title window
    self.title(gg.APPLICATION_WINDOW_TITLE)
    return sizes_tuple
