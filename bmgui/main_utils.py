"""Module of useful functions for GUI main management."""

__all__ = ['set_corpuses_widgets_param',
           'set_datatype_widgets_param',
           'set_common_params',
           'set_displays_widths',
           'set_institute_widgets',
           'set_labels_pos',
           'set_wf_widget_param',
           'update_app_page',
          ]


# Standard library imports
import os
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import messagebox
from tkinter import font as tkFont

# Local imports
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu
from bmfuncts.useful_functs import create_archi
from bmgui.pages_classes import SetLaunchButton


def set_common_params(self, master):
    """Sets common parameters for widgets of main page.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
    """
    self.select_font_size_tup = bm_gu.set_font_size_tup(master,
                                                        bm_gg.MAIN_FONT_SIZE_DICT['main_select'],
                                                        ['label', 'button'])
    self.disp_font_size_tup = bm_gu.set_font_size_tup(master,
                                                      bm_gg.MAIN_FONT_SIZE_DICT['main_disp'],
                                                      ['label', 'button'])
    self.val_disp_dx = bm_gu.set_item_pos(master, bm_gg.VAL_DISPLAY_DX, 0)
    self.buttons_dy = bm_gu.set_item_pos(master, bm_gg.MAIN_BUT_DPOS_TUP[1], 1)
    self.opt_but_dy = bm_gu.set_item_pos(master, bm_gg.MAIN_OPT_BUT_DPOS_TUP[1], 1)


def set_labels_pos(self, master):
    """Sets widget label positions in main page.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
    """
    self.inst_label_pos_tup = bm_gu.set_pos_tup_px(master,
                                                   bm_gg.MAIN_SELECT_LABEL_POS_DICT['institute'])
    self.datatype_label_pos_tup = bm_gu.set_pos_tup_px(master,
                                                       bm_gg.MAIN_SELECT_LABEL_POS_DICT['datatype'])
    self.wf_pos_tup = bm_gu.set_pos_tup_px(master,
                                           bm_gg.MAIN_DISP_LABEL_POS_DICT['work_folder'])
    self.corpuses_pos_tup = bm_gu.set_pos_tup_px(master,
                                                 bm_gg.MAIN_DISP_LABEL_POS_DICT['corpus_list'])


def set_displays_widths(self, master):
    """Sets widths for displayed information in main page.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
    """
    self.datatype_width =  bm_gu.set_display_width(master, 'datatype')
    self.wf_width = bm_gu.set_display_width(master, 'work_folder')
    self.corpuses_width = bm_gu.set_display_width(master, 'corpus_list')


def set_institute_widgets(self, institute_val):
    """Sets widget parameters for institute selection through 'tk.OptionMenu'.

    Args:
        self (instance): Instance of the calling page.
        institute_val (tk.StringVar): For tracking value in 'tk.OptionMenu'.
    """
    # Setting label widget for institute selection
    self.inst_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                       size=self.select_font_size_tup[0],
                                       weight='bold')
    self.inst_label = tk.Label(self,
                               text=bm_gg.MAIN_SELECT_LABEL_DICT['institute'],
                               font=self.inst_label_font)
    self.inst_label.place(x=self.inst_label_pos_tup[0],
                          y=self.inst_label_pos_tup[1])

    # Setting button for institute selection
    self.inst_optionbutton_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                              size=self.select_font_size_tup[1])
    self.inst_optionbutton = tk.OptionMenu(self, institute_val,
                                           *bm_ig.INSTITUTES_LIST)
    self.inst_optionbutton.config(font=self.inst_optionbutton_font)

    # Placing widgets for Institute selection
    bm_gu.place_after(self.inst_label, self.inst_optionbutton, dy=self.opt_but_dy)


def set_datatype_widgets_param(self, datatype_val):
    """Sets widget parameters for datatype selection through 'tk.OptionMenu'.

    Args:
        self (instance): Instance of the calling page.
        datatype_val (tk.StringVar): For tracking value in 'tk.OptionMenu'.
    """
    # Setting label widget for datatype selection
    self.datatype_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                           size=self.select_font_size_tup[0],
                                           weight='bold')
    self.datatype_label = tk.Label(self,
                                   text=bm_gg.MAIN_SELECT_LABEL_DICT['datatype'],
                                   font=self.datatype_label_font)
    self.datatype_label.place(x=self.datatype_label_pos_tup[0],
                              y=self.datatype_label_pos_tup[1])

    # Setting button widget for datatype selection
    self.datatype_optionbutton_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                                  size=self.select_font_size_tup[1])
    self.datatype_optionbutton = tk.OptionMenu(self, datatype_val,
                                               *bm_pg.DATATYPE_LIST)
    self.datatype_optionbutton.config(font=self.datatype_optionbutton_font,
                                      width=self.datatype_width)
    bm_gu.place_after(self.datatype_label, self.datatype_optionbutton, dy=self.opt_but_dy)


def _display_path(inst_wf):
    """Shortens wf path for easy display.

    Args:
        inst_wf (str): Full path as string to the working folder.
    Returns:
        (str): The shortened path to the working folder to be displayed.
    """
    p = Path(inst_wf)
    if len(p.parts)<=4:
        p_disp = p
    else:
        part_start = p.parts[0:2]
        part_end = p.parts[-3:]
        p_disp = ('/'.join(part_start)) / Path("...") / ('/'.join(part_end))
    return p_disp


def _get_file(self, institute_select, datatype_select):
    """Gets full path of working folder through 'tk.filedialog.askdirectory'. 
    Updates 'wf' widgets parameters and values accordingly to the working 
    folder got and sets launch button of corpuses analysis.

    Args:
        self (instance): Instance of the calling page.
        institute_select (str): Selected Institute name.
        datatype_select (str): Selected datatype.
    """
    # Getting new working directory
    dialog_title = "Choisir un nouveau dossier de travail"
    wf_str = tk.filedialog.askdirectory(title=dialog_title)
    if wf_str=='':
        warning_title = "!!! Attention !!!"
        warning_text = "Chemin non renseigné."
        messagebox.showwarning(warning_title, warning_text)

    # Updating wf values using new working directory
    set_wf_widget_param(self, institute_select, wf_str, datatype_select)
    _update_corpuses(self, wf_str)
    wf_path = Path(wf_str)
    SetLaunchButton(self, institute_select, wf_path, datatype_select)


def set_wf_widget_param(self, institute_select, inst_wf, datatype_select):
    """Sets 'wf' widgets parameters and values 
    according to the selected Institute.

    Args:
        self (instance): Instance of the calling page.
        institute_select (str): Selected Institute name.
        inst_wf (str): Full path as string to the working folder.
        datatype_select (str): Selected datatype.
    """
    # Setting wf label widget
    wf_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                size=self.disp_font_size_tup[0],
                                weight='bold')
    wf_label = tk.Label(self,
                        text=bm_gg.MAIN_DISP_LABEL_DICT['wf'],
                        font=wf_label_font)
    wf_label.place(x=self.wf_pos_tup[0], y=self.wf_pos_tup[1])

    # Setting wf value widget
    wf_val = tk.StringVar(self)
    wf_val.set(inst_wf)

    # Setting wf displayed value widget
    wf_val_disp = tk.StringVar(self)
    wf_entry = tk.Entry(self, textvariable=wf_val_disp, width=self.wf_width)
    bm_gu.place_after(wf_label, wf_entry, dx=self.val_disp_dx)
    wf_val_disp.set(_display_path(inst_wf))

    # Setting button for changing Wf
    wf_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                 size=self.disp_font_size_tup[1])
    wf_button = tk.Button(self,
                          text=bm_gg.MAIN_BUT_LABEL_DICT['wf_change'],
                          font=wf_button_font,
                          command=lambda: _get_file(self, institute_select,
                                                    datatype_select))
    bm_gu.place_bellow(wf_entry, wf_button, dy=self.buttons_dy)


def _try_wf_access(wf_path):
    """Returns status of the default working folder as boolean: True, if exists 
    and access is authorized to the user; False, otherwise.

    Args:
        wf_path (path): Full path to the working folder.
    Returns:
        (bool): Status of the access to the working folder.
    """
    wf_access_status = False
    if os.access(wf_path, os.F_OK | os.R_OK | os.W_OK):
        wf_access_status = True
    else:
        warning_title = "!!! ATTENTION : Accés au dossier impossible !!!"
        warning_text = (f"Accès non autorisé ou absence du dossier \n   {wf_path}."
                        "\n\nChoisissez un autre dossier de travail.")
        messagebox.showwarning(warning_title, warning_text)
    return wf_access_status


def _create_corpus(self, inst_wf):
    """Creates a new corpus folder in the working folder through `create_archi` 
    function imported from `bmfuncts.useful_functs` module.             
    Then, updates 'corpuses' widget value with new list of available corpuses.

    Args:
        self (instance): Instance of the calling page.
        inst_wf (str): Full path as string to the working folder.
    """
    corpuses_val = set_corpuses_widgets_param(self, inst_wf)
    wf_path = Path(inst_wf)
    wf_access_status = _try_wf_access(wf_path)
    if wf_access_status:
        # Setting new corpus year folder name
        corpuses_list = bm_gu.last_available_years(wf_path, bm_gg.CORPUSES_NUMBER)
        last_corpus_year = corpuses_list[-1]
        new_corpus_year_folder = str(int(last_corpus_year) + 1)

        # Creating required folders for new corpus year
        message = create_archi(wf_path, new_corpus_year_folder, verbose=False)
        print("\n",message)

        # Getting updated corpuses list
        corpuses_list = bm_gu.last_available_years(wf_path, bm_gg.CORPUSES_NUMBER)

        # Setting corpuses_val value to corpuses list
        corpuses_val_to_set = str(corpuses_list)
        corpuses_val.set(corpuses_val_to_set)

        # Displaying info
        extractions_folder_alias = bm_pg.ARCHI_EXTRACT['root']
        info_title = "- Information -"
        info_text = (f"L'architecture du dossier pour l'année {new_corpus_year_folder} "
                     "a été créée dans le dossier de travail."
                     "\n\nAvant de lancer l'analyse, mettez les extractions "
                     f"correspondantes dans le dossier :\n\n  '{extractions_folder_alias}'.")
        messagebox.showinfo(info_title, info_text)
    else:
        corpuses_val.set("")


def set_corpuses_widgets_param(self, inst_wf):
    """Sets 'corpuses' widgets parameters and values accordingly 
    to the working folder and returns tkinter 'corpuses' parameter 
    that is used to set for displaying the available corpuses list.

    Args:
        self (instance): Instance of the calling page.
        inst_wf (str): Full path as string to the working folder.
    """

    # Setting corpuses label widget
    corpuses_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                size=self.disp_font_size_tup[0],
                                weight='bold')
    corpuses_label = tk.Label(self,
                              text=bm_gg.MAIN_DISP_LABEL_DICT['corpuses'],
                              font=corpuses_font)
    corpuses_label.place(x=self.corpuses_pos_tup[0],
                         y=self.corpuses_pos_tup[1])

    # Setting corpuses widgets parameters
    corpuses_val = tk.StringVar(self)
    corpuses_entry = tk.Entry(self, textvariable=corpuses_val,
                              width=self.corpuses_width)
    bm_gu.place_after(corpuses_label, corpuses_entry, dx=self.val_disp_dx)

    # Setting button for corpus creation
    corpuses_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                    size=self.disp_font_size_tup[1])
    corpuses_button = tk.Button(self,
                             text=bm_gg.MAIN_BUT_LABEL_DICT['corpus_add'],
                             font=corpuses_button_font,
                             command=lambda: _create_corpus(self, inst_wf))
    bm_gu.place_bellow(corpuses_entry, corpuses_button, dy=self.buttons_dy)
    return corpuses_val


def _update_corpuses(self, inst_wf):
    """Updates tkinter 'corpuses' parameter with the available corpuses list
    accordingly to working folder.

    Args:
        self (instance): Instance of the calling page.
        inst_wf (str): Full path as string to the working folder.
    """

    corpuses_val = set_corpuses_widgets_param(self, inst_wf)
    corpuses_val_to_set = ""
    wf_path = Path(inst_wf)
    wf_access_status = _try_wf_access(wf_path)
    if wf_access_status:
        # Getting updated corpuses list
        corpuses_list = bm_gu.last_available_years(wf_path, bm_gg.CORPUSES_NUMBER)

        # Setting corpuses_val value to corpuses list
        corpuses_val_to_set = str(corpuses_list)
    corpuses_val.set(corpuses_val_to_set)


def _update_datatype(self, *args, datatype_widget=None):
    """Gets selected data-type and sets, accordingly, 'wf' widgets parameters, 
    'corpuses' widgets parameters and sets launch button of corpuses analysis.

    Args:
        self (instance): Instance of the calling page.
        datatype_widget (tk.StringVar): For tracking value of datatype selection.
    """

    datatype_select = datatype_widget.get()
    self.datatype_optionbutton.configure(state = 'disabled')

    # Managing working folder
    institute_select = args[0]
    inst_default_wf = bm_ig.WORKING_FOLDERS_DICT[institute_select] + "-" + bm_gg.VERSION
    set_wf_widget_param(self, institute_select, inst_default_wf, datatype_select)

    # Managing corpus list
    corpuses_val = set_corpuses_widgets_param(self, inst_default_wf)

    # Setting and displaying corpuses list initial values
    corpuses_val_to_set = ""
    default_wf_path = Path(inst_default_wf)
    info_title = "- Information -"
    info_text = ("Le test de l'accès au dossier de travail défini "
                 "par défaut peut prendre un peu de temps."
                 "\n\nMerci de patienter.")
    messagebox.showinfo(info_title, info_text)
    wf_access_status = _try_wf_access(default_wf_path)
    if wf_access_status:
        info_title = "- Information -"
        info_text = ("L'accès au dossier de travail défini "
                     "par défaut est autorisé mais vous pouvez "
                     "en choisir un autre.")
        messagebox.showinfo(info_title, info_text)
        init_corpuses_list = bm_gu.last_available_years(default_wf_path, bm_gg.CORPUSES_NUMBER)
        corpuses_val_to_set = str(init_corpuses_list)
    corpuses_val.set(corpuses_val_to_set)

    # Managing analysis launch button
    SetLaunchButton(self, institute_select, default_wf_path, datatype_select)


def update_app_page(self, *args, institute_widget=None):
    """Gets the selected Institute and 'datatype' widgets parameters.
    Then, trace change in datatype selection to update page parameters.

    Args:
        self (instance): Instance of the calling page.
        institute_widget (tk.StringVar): For tracking value of Institute selection.
    """
    institute_select = institute_widget.get()

    # Setting default values for datatype selection
    default_datatype = " "
    datatype_val = tk.StringVar(self)
    datatype_val.set(default_datatype)

    # Creating widgets for datatype selection
    set_datatype_widgets_param(self, datatype_val)

    # Tracing data type selection
    datatype_val.trace('w',
                       partial(_update_datatype, self, institute_select,
                               datatype_widget=datatype_val))
