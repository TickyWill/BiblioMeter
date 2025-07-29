""" `gui_utils` module contains useful functions for gui management."""

__all__ = ['set_data_select_widgets',
           'set_step_help_button',
           'set_step_label',
           'set_step_launch_button',
           'set_year_select_widgets',
          ]


# Standard library imports
import tkinter as tk
from functools import partial
from tkinter import font as tkFont
from tkinter import messagebox

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
from bmgui.gui_utils import disable_buttons
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow


def set_year_select_widgets(self, master, year_select_params):
    """Sets in the page the label and place of the year-selection 
    label widget and the button and place of the year-selection button.
    """
    # Setting parameters from args
    [year_font_size_tup, year_label_pos_tup,
     year_button_dpos_tup] = year_select_params

    # Setting year selection label
    self.Label_years_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                        size=year_font_size_tup[0],              # year_font_size
                                        weight='bold')
    self.Label_years = tk.Label(self,
                                text=bm_gg.PAGE_SELECT_LABEL_DICT['year'],
                                font=self.Label_years_font)
    self.Label_years.place(x=year_label_pos_tup[0], y=year_label_pos_tup[1])     #year_label_x_pos, y=year_label_y_pos)

    # Setting option button for year selection
    self.years_opt_but_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                          size=year_font_size_tup[1])            # button_font_size
    self.years_opt_but = tk.OptionMenu(self,
                                       self.variable_years,
                                       *master.years_list)
    self.years_opt_but.config(font=self.years_opt_but_font)
    place_after(self.Label_years, self.years_opt_but, dy=year_button_dpos_tup[1])
    bm_gg.GUI_BUTTONS.append(self.years_opt_but)


def set_data_select_widgets(self, data_select_params):
    """Sets in the page the label and place of the data-selection 
    label widget and the button and place of the data-selection button.
    """
    # Setting parameters from args
    (data_font_size_tup, data_label_dpos_tup,
     data_button_dpos_tup, widget_ref) = data_select_params

    # Setting data selection label
    data_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=data_font_size_tup[0])      # select_font_size
    data_label = tk.Label(self,
                          text=bm_gg.PAGE_SELECT_LABEL_DICT['data'],
                          font=data_label_font)
    place_bellow(widget_ref, data_label,                                 # step_label_widget[step_num]
                 dx=data_label_dpos_tup[0],                              # select_label_dx[item]
                 dy=data_label_dpos_tup[1])                              # select_label_dy[item]

    # Setting option button for data selection
    data_variable = tk.StringVar(self)
    data_variable.set(bm_pg.BDD_LIST[0])                                 # select_default[item]
    data_opt_but_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                    size=data_font_size_tup[1])   # button_font_size
    data_opt_but = tk.OptionMenu(self, data_variable,
                                 *bm_pg.BDD_LIST)
    data_opt_but.config(font=data_opt_but_font)
    place_after(data_label, data_opt_but,
                dx=data_button_dpos_tup[0],                              # select_button_dx
                dy=data_button_dpos_tup[1])                              # select_button_dy
    bm_gg.GUI_BUTTONS.append(data_opt_but)
    return data_variable, data_opt_but


def set_step_label(self, step_num, step_label_params):
    """Sets the label and place of step-label widget in the page.

    Args:
        step_num (int): The order of the step in 'STEPS_LABELS_DICT' global \
        at 'page_key' key.
    Returns:
        (tk widget): The widget of the step label.
    """
    # Setting parameters from args
    step_font_size_tup, step_label_pos_tup_list = step_label_params

    # Setting label of step-label widget
    step_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=step_font_size_tup[0],             # built with ['step_label', 'step_launch']
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


def _edit_help(self, step_num):
    disable_buttons(self.page_buttons_list)
    info_title = (f"{bm_gg.STEPS_LABELS_DICT[self.page_key][step_num].split(' - ')[0]}"
                  f" - {bm_gg.HELP_LABEL}")
    info_text = bm_gg.STEPS_HELPS_DICT[self.page_key][step_num]
    messagebox.showinfo(info_title, info_text)
    enable_buttons(self.page_buttons_list)


def set_step_help_button(self, step_num,
                         help_button_params, step_label_params):
    # Setting parameters from args
    step_font_size_tup, help_dpos_ref_tup = help_button_params
    step_label_widget, step_label_pos_tup_list = step_label_params

    # Setting label widget for help button
    help_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                   size=step_font_size_tup[2])
    help_button = tk.Button(self,
                            text=bm_gg.HELP_LABEL,
                            font=help_button_font,
                            command=partial(_edit_help, self, step_num))

    # Placing help button after step label widget
    step_label = step_label_widget[step_num]
    step_x_pos, _ = step_label_pos_tup_list[step_num]
    step_help_dx = help_dpos_ref_tup[0] - step_label.winfo_reqwidth() - step_x_pos
    step_help_dy = help_dpos_ref_tup[1]
    place_after(step_label, help_button,
                dx=step_help_dx, dy=step_help_dy)


def set_step_launch_button(self, step_num,
                           launch_button_params, launch_pos_params):
    """Sets launch button for a given step"""
    # Setting parameters from args
    step_font_size_tup, step_start_funct = launch_button_params
    pos_type, widget_ref, pos_tup, dpos_tup = launch_pos_params

    # Setting label widget for launch button
    step_launch_font = tkFont.Font(family=bm_gg.FONT_NAME,    # line  to be integrated in function of launch button
                                   size=step_font_size_tup[1])
    step_launch_button = tk.Button(self,
                                   text=bm_gg.STEPS_LAUNCHES_DICT[self.page_key][step_num],
                                   font=step_launch_font,
                                   command=step_start_funct)

    # Placing launch button relatively to 'widget_ref' depending on 'pos_type'
    if pos_type=='bellow':
        place_bellow(widget_ref, step_launch_button,
                     dx=dpos_tup[0], dy=dpos_tup[1])                           # step_button_dx, step_button_dy
    elif pos_type=='after':
        place_after(widget_ref, step_launch_button,
                    dx=dpos_tup[0], dy=dpos_tup[1])
    else:    
        step_launch_button.place(x=pos_tup[0], y=pos_tup[1])
    bm_gg.GUI_BUTTONS.append(step_launch_button)
    return step_launch_button
