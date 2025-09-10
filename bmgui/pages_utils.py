"""Module of useful functions for GUI pages management."""

__all__ = ['set_data_select_widgets',
           'set_general_params',
           'set_progress_bar_params',
           'set_step_help_button',
           'set_step_label',
           'set_step_launch_button',
           'set_steps_widgets_param',
           'set_year_select_widgets',
          ]


# Standard library imports
import tkinter as tk
from functools import partial
from tkinter import font as tkFont
from tkinter import messagebox
from tkinter import ttk

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu

from bmgui.gui_utils import disable_buttons
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import set_font_size_tup
from bmgui.gui_utils import set_pos_tup_px
from bmgui.gui_utils import set_pos_tup_px_list
from bmgui.gui_utils import set_progress_bar_pos_tup


def set_general_params(master, institute, wf_path, datatype):
    master.institute = institute
    master.wf_path = wf_path
    master.datatype = datatype


def set_step_label(self, step_num, step_label_params):
    """Sets the label and place of step-label widget in the page.

    Args:
        self (instance): Instance of the calling page.
        step_num (int): The order of the step in 'STEPS_LABELS_DICT' global \
        at 'page_key' key.
        step_label_params (tup): (fonts of step widgets (tup), \
        x-axis and y-axis positions of step widgets (list of tup)).
    Returns:
        (tk widget): The widget of the step label.
    """
    # Setting parameters from args
    step_font_size_tup, step_label_pos_tup_list = step_label_params

    # Setting label of step-label widget
    step_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=step_font_size_tup[0],
                                  weight='bold')
    step_label = tk.Label(self,
                          text=bm_gg.STEPS_LABELS_DICT[self.page_key][step_num],
                          font=step_label_font,
                          justify='left',
                          underline=-1)

    # Placing step-label widget
    step_label.place(x=step_label_pos_tup_list[step_num][0],
                     y=step_label_pos_tup_list[step_num][1])
    return step_label


def set_progress_bar_params(self, master):
    """Sets size and relative positions of widget of progress bar in page 
    and variable to keep track of the progress bar value.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
    """
    # Setting size and relative positions of widget of progress bar
    return_tup = set_progress_bar_pos_tup(master, self.page_key)
    progress_bar_len, self.progress_bar_dx, self.progress_bar_dy = return_tup

    # Setting variable to keep track of the progress bar value
    self.progress_var = tk.IntVar()
    self.progress_bar = ttk.Progressbar(self,
                                        orient="horizontal",
                                        length=progress_bar_len,
                                        mode="determinate",
                                        variable=self.progress_var)


def set_steps_widgets_param(self, master, parse=False):
    """Sets label widgets and help buttons parameters for all page steps.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
        parse (bool): Optional, specify if the calling page \
        is the parsing page (default=False).
    """
    # Setting label widgets parameters for all page steps
    step_label_pos_tup_list = bm_gu.set_pos_tup_px_list(master, bm_gg.STEP_POS_TUPS_DICT[self.page_key])
    self.step_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.PAGE_FONT_SIZE_DICT,
                                                      ['step_label', 'step_launch', 'step_help'])
    step_label_params = (self.step_font_size_tup, step_label_pos_tup_list)
    steps_number = bm_gg.STEPS_NB_DICT[self.page_key]
    self.step_label_widgets_list = [set_step_label(self, step_num, step_label_params)
                                    for step_num in range(steps_number)]
    self.step_label_widgets_params = (self.step_label_widgets_list, step_label_pos_tup_list)
    if parse:
        self.step_button_pos_tup = bm_gu.set_pos_tup_px(master, bm_gg.STATUS_BUT_POS_TUP)
        self.step_button_dpos_tup_list = [bm_gu.set_pos_tup_px(master, bm_gg.STEP_BUT_DPOS_DICT[key])
                                          for key in [self.parse_key, self.dedup_key]]

        data_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.PAGE_FONT_SIZE_DICT['step_select'],
                                                     ['label', 'button'])
        data_label_dpos_tup = bm_gu.set_pos_tup_px(master, bm_gg.PAGE_SELECT_LABEL_DPOS_DICT[self.page_key])
        data_button_dpos_tup = bm_gu.set_pos_tup_px(master, bm_gg.PAGE_SELECT_BUT_DPOS_DICT[self.page_key])
        self.data_select_params = (data_font_size_tup, data_label_dpos_tup,
                                   data_button_dpos_tup)

        # Setting parameters of help buttons for all page steps
        help_dpos_ref_tup_list = [bm_gu.set_pos_tup_px(master, bm_gg.HELP_BUT_DPOS_TUP[key])
                                  for key in ['status', 'other', 'other']]
    else:
        self.step_button_dpos_tup = bm_gu.set_pos_tup_px(master, bm_gg.STEP_BUT_DPOS_DICT[self.page_key])
        # Setting parameters of help buttons for all page steps
        dpos_ref_tup = bm_gu.set_pos_tup_px(master, bm_gg.HELP_BUT_DPOS_TUP['other'])
        help_dpos_ref_tup_list = sum([[dpos_ref_tup] * steps_number], [])
    self.help_button_params = (self.step_font_size_tup, help_dpos_ref_tup_list)


def set_year_select_widgets(self, master):
    """Sets in the page the label and place of the year-selection 
    label widget and the button and place of the year-selection button.

    Args:
        self (instance): Instance of the calling page.
        master (class): `bmgui.main_page.AppMain` class.
    """
    # Setting parameters
    year_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.PAGE_FONT_SIZE_DICT['year_select'],
                                                 ['label', 'button'])
    year_label_pos_tup = bm_gu.set_pos_tup_px(master,
                                              bm_gg.PAGE_SELECT_LABEL_POS_DICT[self.year_key])
    year_button_dpos_tup = bm_gu.set_pos_tup_px(master,
                                                bm_gg.PAGE_SELECT_BUT_DPOS_DICT[self.page_key])

    # Setting year selection label
    self.Label_years_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                        size=year_font_size_tup[0],
                                        weight='bold')
    self.Label_years = tk.Label(self,
                                text=bm_gg.PAGE_SELECT_LABEL_DICT['year'],
                                font=self.Label_years_font)
    self.Label_years.place(x=year_label_pos_tup[0], y=year_label_pos_tup[1])

    # Setting option button for year selection
    self.years_opt_but_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                          size=year_font_size_tup[1])
    self.years_opt_but = tk.OptionMenu(self,
                                       self.variable_years,
                                       *master.years_list)
    self.years_opt_but.config(font=self.years_opt_but_font)
    bm_gu.place_after(self.Label_years, self.years_opt_but, dy=year_button_dpos_tup[1])
    bm_gg.GUI_BUTTONS.append(self.years_opt_but)


def set_data_select_widgets(self, step_num):
    """Sets in the page the label and place of the data-selection 
    label widget and the button and place of the data-selection button.

    Args:
        self (instance): Instance of the calling page.
        step_num (int): Index of the step.
    Returns:
        (tup): (variable (tk.StringVar) for tracking value of selected data, \
        data selection button (tk.OptionMenu)).
    """
    # Setting parameters from args
    (data_font_size_tup, data_label_dpos_tup,
     data_button_dpos_tup) = self.data_select_params
    widget_ref = self.step_label_widgets_list[step_num]

    # Setting data selection label
    data_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=data_font_size_tup[0])
    data_label = tk.Label(self,
                          text=bm_gg.PAGE_SELECT_LABEL_DICT['data'],
                          font=data_label_font)
    bm_gu.place_bellow(widget_ref, data_label,
                       dx=data_label_dpos_tup[0],
                       dy=data_label_dpos_tup[1])

    # Setting option button for data selection
    data_variable = tk.StringVar(self)
    data_variable.set(bm_pg.BDD_LIST[0])
    data_opt_but_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                    size=data_font_size_tup[1])
    data_opt_but = tk.OptionMenu(self, data_variable,
                                 *bm_pg.BDD_LIST)
    data_opt_but.config(font=data_opt_but_font)
    bm_gu.place_after(data_label, data_opt_but,
                      dx=data_button_dpos_tup[0],
                      dy=data_button_dpos_tup[1])
    bm_gg.GUI_BUTTONS.append(data_opt_but)
    return data_variable, data_opt_but


def _edit_help(self, step_num):
    """Edits help menu.

    Args:
        self (instance): Instance of the calling page.
        step_num (int): Index of the step.
    """
    bm_gu.disable_buttons(self.page_buttons_list)
    info_title = (f"{bm_gg.STEPS_LABELS_DICT[self.page_key][step_num].split(' - ')[0]}"
                  f" - {bm_gg.HELP_LABEL}")
    info_text = bm_gg.STEPS_HELPS_DICT[self.page_key][step_num]
    messagebox.showinfo(info_title, info_text)
    bm_gu.enable_buttons(self.page_buttons_list)


def set_step_help_button(self, step_num, pos_type=None):
    """Sets widget parameters and place for help button of a given step.

    Args:
        self (instance): Instance of the calling page.
        step_num (int): Index of the step.
        pos_type (str): Optional, if set to 'bellow' \
        the button is placed bellow the step label, \
        else it is placed after on the same line (default=None).
    Returns:
        (tk.Button): The set button for editing help message.
    """
    # Setting parameters from args
    step_font_size_tup, help_dpos_ref_tup_list = self.help_button_params
    step_label_widget, step_label_pos_tup_list = self.step_label_widgets_params

    # Setting label widget for help button
    help_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                   size=step_font_size_tup[2])
    help_button = tk.Button(self,
                            text=bm_gg.HELP_LABEL,
                            font=help_button_font,
                            command=partial(_edit_help, self, step_num))

    # Placing help button after step label widget
    step_label = step_label_widget[step_num]
    if pos_type=='bellow':
        step_help_dx = help_dpos_ref_tup_list[step_num][0]
        step_help_dy = help_dpos_ref_tup_list[step_num][1]
        bm_gu.place_bellow(step_label, help_button,
                           dx=step_help_dx, dy=step_help_dy)
    else:
        step_x_pos, _ = step_label_pos_tup_list[step_num]
        step_help_dx = help_dpos_ref_tup_list[step_num][0] - step_label.winfo_reqwidth() - step_x_pos
        step_help_dy = help_dpos_ref_tup_list[step_num][1]
        bm_gu.place_after(step_label, help_button,
                          dx=step_help_dx, dy=step_help_dy)
    return help_button


def set_step_launch_button(self, step_num, step_start_funct, pos_type,
                           parse=False, widget_ref=None):
    """Sets launch button for a given step

    Args:
        self (instance): Instance of the calling page.
        step_num (int): Index of the step.
        step_start_funct (str): Name of the function \
        to be used for the button command.
        pos_type (str): {'place', 'bellow', 'after'}, \
        'place' = button placed at absolute position, \
        'bellow' = button is placed bellow the step label, \
        'after' = button is placed after a specifyed reference widget.
        parse (bool): Optional, specify if the calling page \
        is the parsing page (default=False).
        widget_ref (tk widget): Optional, specify the reference \
        widget when posètype is set to 'after'.
    Returns:
        (tk.Button): The set button for launching the step.
    """
    # Setting label widget for launch button
    step_launch_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                   size=self.step_font_size_tup[1])
    step_launch_button = tk.Button(self,
                                   text=bm_gg.STEPS_LAUNCHES_DICT[self.page_key][step_num],
                                   font=step_launch_font,
                                   command=step_start_funct)

    # Placing launch button depending on 'pos_type'
    if pos_type=='place':
        # Absolute position
        pos_tup = self.step_button_pos_tup
        step_launch_button.place(x=pos_tup[0], y=pos_tup[1])
    else:
        if parse:
            dpos_tup = self.step_button_dpos_tup_list[step_num-1]
        else:
            dpos_tup = self.step_button_dpos_tup
        if pos_type=='bellow':
            # Bellow the step label
            bm_gu.place_bellow(self.step_label_widgets_list[step_num], step_launch_button,
                               dx=dpos_tup[0], dy=dpos_tup[1])
        elif pos_type=='after':
            # On the same line, after the specified widget as reference
            bm_gu.place_after(widget_ref, step_launch_button,
                              dx=dpos_tup[0], dy=dpos_tup[1])
    bm_gg.GUI_BUTTONS.append(step_launch_button)
    return step_launch_button
