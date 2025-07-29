""" The `main_page` module sets the `AppMain` class, its attributes and related secondary classes.
"""
__all__ = ['AppMain']

# Standard library imports
import os
import threading
import tkinter as tk
import traceback
from functools import partial
from pathlib import Path
from tkinter import messagebox
from tkinter import font as tkFont

# 3rd party imports
from screeninfo import get_monitors

# Local imports
import bmgui.gui_globals as bm_gg
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
from bmfuncts.useful_functs import create_archi
from bmfuncts.useful_functs import set_rawdata
from bmgui.analyze_corpus_page import create_analysis
from bmgui.consolidate_corpus_page import create_consolidate_corpus
from bmgui.parse_corpus_page import create_parsing_concat
from bmgui.update_if_page import create_update_ifs
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import existing_corpuses
from bmgui.gui_utils import font_size
from bmgui.gui_utils import general_properties
from bmgui.gui_utils import last_available_years
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import place_bellow
from bmgui.gui_utils import show_frame
from bmgui.gui_utils import set_pos_tup_px
from bmgui.gui_utils import set_font_size_tup


class AppMain(tk.Tk):
    """Main class of the BiblioMeter application.

    Traces changes in institute selection to update page parameters. 
    'wf' stands for working folder.
    """
    def __init__(self):
        self.inst_label_font = None
        self.inst_label = None
        self.inst_optionbutton_font = None
        self.inst_optionbutton = None
        self.datatype_label_font = None
        self.datatype_label = None
        self.datatype_optionbutton_font = None
        self.datatype_optionbutton = None

        # Internal functions
        def _set_institute_widgets(institute_val):
            """Sets widget parameters for institute selection through 'tk.OptionMenu'."""
            # Setting label widget for institute selection
            self.inst_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                               size=select_font_size_tup[0],
                                               weight='bold')
            self.inst_label = tk.Label(self,
                                       text=bm_gg.MAIN_SELECT_LABEL_DICT['institute'],
                                       font=self.inst_label_font)

            # Setting button for institute selection
            self.inst_optionbutton_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                                      size=select_font_size_tup[1])
            self.inst_optionbutton = tk.OptionMenu(self, institute_val,
                                                   *bm_ig.INSTITUTES_LIST)
            self.inst_optionbutton.config(font=self.inst_optionbutton_font)

            # Placing widgets for Institute selection
            self.inst_label.place(x=inst_label_pos_tup[0], y=inst_label_pos_tup[1])
            place_after(self.inst_label, self.inst_optionbutton, dy=opt_but_dy)

        def _set_datatype_widgets_param(datatype_val):
            """Sets widget parameters for datatype selection through 'tk.OptionMenu'."""
            # Setting label widget for datatype selection
            self.datatype_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                                   size=select_font_size_tup[0],
                                                   weight='bold')
            self.datatype_label = tk.Label(self,
                                           text=bm_gg.MAIN_SELECT_LABEL_DICT['datatype'],
                                           font=self.datatype_label_font)
            self.datatype_label.place(x=datatype_label_pos_tup[0], y=datatype_label_pos_tup[1])

            # Setting button widget for datatype selection
            self.datatype_optionbutton_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                                          size=select_font_size_tup[1])
            self.datatype_optionbutton = tk.OptionMenu(self, datatype_val,
                                                       *bm_pg.DATATYPE_LIST)
            self.datatype_optionbutton.config(font=self.datatype_optionbutton_font,
                                              width=datatype_width)
            place_after(self.datatype_label, self.datatype_optionbutton, dy=opt_but_dy)

        def _display_path(inst_wf):
            """Shortens wf path for easy display."""

            p = Path(inst_wf)
            if len(p.parts)<=4:
                p_disp = p
            else:
                part_start = p.parts[0:2]
                part_end = p.parts[-3:]
                p_disp = ('/'.join(part_start)) / Path("...") / ('/'.join(part_end))
            return p_disp

        def _get_file(institute_select, datatype_select):
            """Gets full path of working folder through 'tk.filedialog.askdirectory'. 
            Updates 'wf' widgets parameters and values accordingly to the working 
            folder got and sets launch button of corpuses analysis."""

            # Getting new working directory
            dialog_title = "Choisir un nouveau dossier de travail"
            wf_str = tk.filedialog.askdirectory(title=dialog_title)
            if wf_str=='':
                warning_title = "!!! Attention !!!"
                warning_text = "Chemin non renseigné."
                messagebox.showwarning(warning_title, warning_text)

            # Updating wf values using new working directory
            _set_wf_widget_param(institute_select, wf_str, datatype_select)
            _update_corpuses(wf_str)
            wf_path = Path(wf_str)
            SetLaunchButton(self, institute_select, wf_path, datatype_select)

        def _set_wf_widget_param(institute_select, inst_wf, datatype_select):
            """Sets 'wf' widgets parameters and values 
            according to the selected Institute."""
            # Setting wf label widget
            wf_label_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                        size=disp_font_size_tup[0],
                                        weight='bold')
            wf_label = tk.Label(self,
                                text=bm_gg.MAIN_DISP_LABEL_DICT['wf'],
                                font=wf_label_font)
            wf_label.place(x=wf_pos_tup[0], y=wf_pos_tup[1])
            
            # Setting wf value widget
            wf_val = tk.StringVar(self)
            wf_val.set(inst_wf)
            
            # Setting wf displayed value widget
            wf_val_disp = tk.StringVar(self)
            wf_entry = tk.Entry(self, textvariable=wf_val_disp, width=wf_width)
            place_after(wf_label, wf_entry, dx=val_disp_dx)
            wf_val_disp.set(_display_path(inst_wf))
            
            # Setting button for changing Wf
            wf_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=disp_font_size_tup[1])
            wf_button = tk.Button(self,
                                  text=bm_gg.MAIN_BUT_LABEL_DICT['wf_change'],
                                  font=wf_button_font,
                                  command=lambda: _get_file(institute_select,
                                                            datatype_select))
            place_bellow(wf_entry, wf_button, dy=buttons_dy)

        def _try_wf_access(wf_path):
            """Returns status of the default working folder as boolean: True, if exists 
            and access is authorized to the user; False, otherwise."""

            wf_access_status = False
            if os.access(wf_path, os.F_OK | os.R_OK | os.W_OK):
                wf_access_status = True
            else:
                warning_title = "!!! ATTENTION : Accés au dossier impossible !!!"
                warning_text = (f"Accès non autorisé ou absence du dossier \n   {wf_path}."
                                "\n\nChoisissez un autre dossier de travail.")
                messagebox.showwarning(warning_title, warning_text)
            return wf_access_status

        def _create_corpus(inst_wf):
            """Creates a new corpus folder in the working folder through `create_archi` 
            function imported from `bmfuncts.useful_functs` module.             
            Then, updates 'corpuses' widget value with new list of available corpuses."""

            corpuses_val = _set_corpuses_widgets_param(inst_wf)
            wf_path = Path(inst_wf)
            wf_access_status = _try_wf_access(wf_path)
            if wf_access_status:
                # Setting new corpus year folder name
                corpuses_list = last_available_years(wf_path, corpuses_nb_alias)
                last_corpus_year = corpuses_list[-1]
                new_corpus_year_folder = str(int(last_corpus_year) + 1)

                # Creating required folders for new corpus year
                message = create_archi(wf_path, new_corpus_year_folder, verbose=False)
                print("\n",message)

                # Getting updated corpuses list
                corpuses_list = last_available_years(wf_path, corpuses_nb_alias)

                # Setting corpuses_val value to corpuses list
                corpuses_val_to_set = str(corpuses_list)
                corpuses_val.set(corpuses_val_to_set)

                # Dispaying info
                extractions_folder_alias = bm_pg.ARCHI_EXTRACT['root']
                info_title = "- Information -"
                info_text = (f"L'architecture du dossier pour l'année {new_corpus_year_folder} "
                             "a été créée dans le dossier de travail."
                             "\n\nAvant de lancer l'analyse, mettez les extractions "
                             f"correspondantes dans le dossier :\n\n  '{extractions_folder_alias}'.")
                messagebox.showinfo(info_title, info_text)
            else:
                corpuses_val.set("")

        def _set_corpuses_widgets_param(inst_wf):
            """Sets 'corpuses' widgets parameters and values accordingly 
            to the working folder and returns tkinter 'corpuses' parameter 
            that is used to set for displaying the available corpuses list."""

            # Setting corpuses label widget
            corpuses_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                     size=disp_font_size_tup[0],
                                     weight='bold')
            corpuses_label = tk.Label(self,
                                   text=bm_gg.MAIN_DISP_LABEL_DICT['corpuses'],
                                   font=corpuses_font)
            corpuses_label.place(x=corpuses_pos_tup[0],
                                 y=corpuses_pos_tup[1])
            
            # Setting corpuses widgets parameters
            corpuses_val = tk.StringVar(self)
            corpuses_entry = tk.Entry(self, textvariable=corpuses_val, width=corpuses_width)
            place_after(corpuses_label, corpuses_entry, dx=val_disp_dx)

            # Setting button for corpus creation
            corpuses_button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                            size=disp_font_size_tup[1])
            corpuses_button = tk.Button(self,
                                     text=bm_gg.MAIN_BUT_LABEL_DICT['corpus_add'],
                                     font=corpuses_button_font,
                                     command=lambda: _create_corpus(inst_wf))
            place_bellow(corpuses_entry, corpuses_button, dy=buttons_dy)
            return corpuses_val

        def _update_corpuses(inst_wf):
            """Updates tkinter 'corpuses' parameter with the available corpuses list 
            accordingly to working folder."""

            corpuses_val = _set_corpuses_widgets_param(inst_wf)
            corpuses_val_to_set = ""
            wf_path = Path(inst_wf)
            wf_access_status = _try_wf_access(wf_path)
            if wf_access_status:
                # Getting updated corpuses list
                corpuses_list = last_available_years(wf_path, corpuses_nb_alias)

                # Setting corpuses_val value to corpuses list
                corpuses_val_to_set = str(corpuses_list)
            corpuses_val.set(corpuses_val_to_set)

        def _update_datatype(*args, datatype_widget=None):
            """Gets selected data-type and sets, accordingly, 'wf' widgets parameters, 
            'corpuses' widgets parameters and sets launch button of corpuses analysis."""

            datatype_select = datatype_widget.get()
            self.datatype_optionbutton.configure(state = 'disabled')

            # Managing working folder
            institute_select = args[0]
            inst_default_wf = bm_ig.WORKING_FOLDERS_DICT[institute_select] + "-" + bm_gg.VERSION
            _set_wf_widget_param(institute_select, inst_default_wf, datatype_select)

            # Managing corpus list
            corpuses_val = _set_corpuses_widgets_param(inst_default_wf)

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
                init_corpuses_list = last_available_years(default_wf_path, corpuses_nb_alias)
                corpuses_val_to_set = str(init_corpuses_list)
            corpuses_val.set(corpuses_val_to_set)

            # Managing analysis launch button
            SetLaunchButton(self, institute_select, default_wf_path, datatype_select)

        def _update_bm_page(*args, institute_widget=None):
            """Gets the selected Institute and 'datatype' widgets parameters.
            Then, trace change in datatype selection to update page parameters."""
            _ = args
            institute_select = institute_widget.get()

            # Setting default values for datatype selection
            default_datatype = " "
            datatype_val = tk.StringVar(self)
            datatype_val.set(default_datatype)

            # Creating widgets for datatype selection
            _set_datatype_widgets_param(datatype_val)

            # Tracing data type selection
            datatype_val.trace('w',
                               partial(_update_datatype, institute_select,
                                       datatype_widget=datatype_val))

        def _except_hook(args):
            messagebox.showerror("Error", args)
            messagebox.showerror("Exception", traceback.format_exc())
            enable_buttons(bm_gg.GUI_BUTTONS)

        # Setting the link between "self" and "tk.Tk"
        tk.Tk.__init__(self)

        # Setting class attributes and methods
        _ = get_monitors() # Mandatory
        self.attributes("-topmost", True)
        self.after_idle(self.attributes,'-topmost', False)
        icon_path = Path(__file__).parent.parent / Path('bmfuncts') / Path(bm_pg.CONFIG_FOLDER)
        icon_path = icon_path / Path('BM-logo.ico')
        self.iconbitmap(icon_path)

        # Initializing AppMain attributes set after working folder definition
        (AppMain.years_list, AppMain.list_corpus_year,
         AppMain.list_wos_rawdata, AppMain.list_wos_parsing,
         AppMain.list_scopus_rawdata, AppMain.list_scopus_parsing,
         AppMain.list_dedup) = ([0],) * 7

        # Setting pages classes and pages list
        AppMain.pages = (AnalyzeCorpusPage,
                         UpdateIfPage,
                         ConsolidateCorpusPage,
                         ParseCorpusPage,)
        AppMain.pages_ordered_list = [x.__name__ for x in AppMain.pages][::-1]

        # Getting useful screen sizes and scale factors depending on displays properties
        (AppMain.win_width_px, AppMain.win_height_px,
         AppMain.width_sf_px, AppMain.height_sf_px,
         AppMain.width_sf_mm, AppMain.height_sf_mm) = general_properties(self)
        AppMain.width_sf_min = min(AppMain.width_sf_mm, AppMain.width_sf_px)
        AppMain.mid_x_pos = int(AppMain.win_width_px * 0.5)
        AppMain.sf_mm_tup = (AppMain.width_sf_mm, AppMain.height_sf_mm)
        
        # Setting short names for window factors for positions setting in px
        w_sf_mm = AppMain.width_sf_mm
        h_sf_mm = AppMain.height_sf_mm
        w_sf_min = AppMain.width_sf_min
        fact_tup = (w_sf_mm, h_sf_mm)

        # Setting common parameters for widgets
        corpuses_nb_alias = bm_gg.CORPUSES_NUMBER
        select_font_size_tup = set_font_size_tup(AppMain,
                                                 bm_gg.MAIN_FONT_SIZE_DICT['main_select'],
                                                 ['label', 'button'])
        disp_font_size_tup = set_font_size_tup(AppMain,
                                               bm_gg.MAIN_FONT_SIZE_DICT['main_disp'],
                                               ['label', 'button'])
        buttons_dy = mm_to_px(bm_gg.MAIN_BUT_DPOS_TUP[1] * h_sf_mm, bm_gg.PPI)
        val_disp_dx = mm_to_px(bm_gg.VAL_DISPLAY_DX * h_sf_mm, bm_gg.PPI)
        opt_but_dy = mm_to_px(bm_gg.MAIN_OPT_BUT_DPOS_TUP[1] * h_sf_mm, bm_gg.PPI)

        # Setting widget label positions
        inst_label_pos_tup = set_pos_tup_px(AppMain, bm_gg.MAIN_SELECT_LABEL_POS_DICT['institute'])
        datatype_label_pos_tup = set_pos_tup_px(AppMain, bm_gg.MAIN_SELECT_LABEL_POS_DICT['datatype'])
        wf_pos_tup = set_pos_tup_px(AppMain, bm_gg.MAIN_DISP_LABEL_POS_DICT['work_folder'])
        corpuses_pos_tup = set_pos_tup_px(AppMain, bm_gg.MAIN_DISP_LABEL_POS_DICT['corpus_list'])

        # Setting widths for displayed information
        datatype_width = int(bm_gg.MAIN_CHAR_NB_DICT['datatype'] * w_sf_min)
        wf_width = int(bm_gg.MAIN_CHAR_NB_DICT['work_folder'] * w_sf_min)
        corpuses_width = int(bm_gg.MAIN_CHAR_NB_DICT['corpus_list'] * w_sf_min)

        # Setting and placing widgets for title and copyright
        SetMasterTitle(self)
        SetAuthorCopyright(self)

        # Setting default values for Institute selection
        default_institute = "   "
        institute_val = tk.StringVar(self)
        institute_val.set(default_institute)
        _set_institute_widgets(institute_val)

        # Tracing Institute selection
        institute_val.trace('w', partial(_update_bm_page, institute_widget=institute_val))

        # Handling exception
        threading.excepthook = _except_hook

class SetMasterTitle():
    """Displays title in main window."""

    def __init__(self, master):

        # Setting widget parameters for page title
        page_title_font_size = font_size(bm_gg.MAIN_FONT_SIZE_DICT['main_title'],
                                         master.width_sf_min)
        page_title_x_pos = master.mid_x_pos
        page_title_y_pos = mm_to_px(bm_gg.MAIN_INFO_POS_DICT['main_title'][1]\
                                    * master.height_sf_mm, bm_gg.PPI)

        # Creating widget for page title
        page_title = tk.Label(master,
                              text=bm_gg.MAIN_PAGE_TITLE,
                              font=(bm_gg.FONT_NAME, page_title_font_size),
                              justify="center")

        # Placing widget for page title
        page_title.place(x=page_title_x_pos,
                         y=page_title_y_pos,
                         anchor="center")

class SetAuthorCopyright():
    """Displays authors and copyright in main window."""

    def __init__(self, master):
        # Setting short names for window factors  for positions setting in px
        w_sf_mm = master.width_sf_mm
        h_sf_mm = master.height_sf_mm
        w_sf_min = master.width_sf_min
        fact_tup = (w_sf_mm, h_sf_mm)

        # Setting widgets parameters for copyright
        copyright_font_size = font_size(bm_gg.MAIN_FONT_SIZE_DICT['copyright'], w_sf_min)
        version_font_size = font_size(bm_gg.MAIN_FONT_SIZE_DICT['version'], w_sf_min)        
        copyright_pos_tup = set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['copyright'])
        version_pos_tup = set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['version'])

        # Creating widgets for copyright
        auteurs_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=copyright_font_size,)
        auteurs_label = tk.Label(master,
                                 text=bm_gg.APP_COPYRIGHT,
                                 font=auteurs_font_label,
                                 justify="left")
        version_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=version_font_size,
                                         weight='bold')
        version_label = tk.Label(master,
                                 text=f"\nVersion {bm_gg.VERSION}",
                                 font=version_font_label,
                                 justify="right")

        # Placing widgets for copyright
        auteurs_label.place(x=copyright_pos_tup[0],
                            y=copyright_pos_tup[1],
                            anchor="sw")
        version_label.place(x=version_pos_tup[0],
                            y=version_pos_tup[1],
                            anchor="sw")

class SetLaunchButton(tk.Tk):
    """Displays corpuses analysis launch button in main window."""

    def __init__(self, master, institute, wf_path, datatype):

        # Setting font size for launch button
        launch_font_size = font_size(bm_gg.MAIN_FONT_SIZE_DICT['main_launch'],
                                     master.width_sf_min)

        # Setting x and y position in pixels for launch button
        launch_but_x_pos = master.mid_x_pos
        launch_but_y_pos = mm_to_px(bm_gg.MAIN_BUT_POS_TUP[1]\
                                    * master.height_sf_mm, bm_gg.PPI)

        # Setting launch button
        launch_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=launch_font_size,
                                  weight='bold')
        launch_button = tk.Button(master,
                                  text=bm_gg.MAIN_BUT_LABEL_DICT['launch'],
                                  font=launch_font,
                                  command=lambda: self._generate_pages(master,
                                                                       institute,
                                                                       wf_path,
                                                                       datatype))
        # Placing launch button
        launch_button.place(x=launch_but_x_pos,
                            y=launch_but_y_pos,
                            anchor="s")

    def _generate_pages(self, master, institute, wf_path, datatype):
        """Generates pages after working folder setting."""

        if wf_path=='':
            warning_title = "!!! Attention !!!"
            warning_text =  "Chemin non renseigné."
            warning_text += "\nL'application ne peut pas être lancée."
            warning_text += "\nVeuillez le définir."
            messagebox.showwarning(warning_title, warning_text)

        else:
            # Setting years list
            master.years_list = last_available_years(wf_path,
                                                     bm_gg.CORPUSES_NUMBER)

            if datatype:
                # Setting rawdata for datatype
                for database in bm_pg.BDD_LIST:
                    _ = set_rawdata(wf_path, datatype,
                                    master.years_list, database)

                # Setting existing corpuses status
                files_status = existing_corpuses(wf_path)
                master.list_corpus_year = files_status[0]
                master.list_wos_rawdata = files_status[1]
                master.list_wos_parsing = files_status[2]
                master.list_scopus_rawdata = files_status[3]
                master.list_scopus_parsing = files_status[4]
                master.list_dedup = files_status[5]

            # Creating two frames in the tk window
            pagebutton_height = mm_to_px(bm_gg.PAGE_BUTTON_HEIGHT\
                                         * master.height_sf_mm, bm_gg.PPI)
            pagebutton_frame = tk.Frame(master, bg='red',
                                        height=pagebutton_height)
            pagebutton_frame.pack(side="top", fill="both", expand=False)

            page_frame = tk.Frame(master)
            page_frame.pack(side="top", fill="both", expand=True)
            page_frame.grid_rowconfigure(0, weight=1)
            page_frame.grid_columnconfigure(0, weight=1)

            self.frames = {}
            for page in master.pages:
                page_name = page.__name__
                if datatype:
                    frame = page(master, pagebutton_frame, page_frame,
                                 institute, wf_path, datatype)
                else:
                    frame = page(master, pagebutton_frame, page_frame,
                                 institute, wf_path)
                self.frames[page_name] = frame

                # Putting all of the pages in the same location
                # The one visible is the one on the top of the stacking order
                frame.grid(row=0, column=0, sticky="nsew")
            master.frames = self.frames


class PageButton(tk.Frame):
    """Sets button of 'page_name' page."""

    def __init__(self, master, page_name, pagebutton_frame):

        # Setting page num
        label_text = bm_gg.PAGES_LABELS[page_name]
        page_num = master.pages_ordered_list.index(page_name)

        # Setting widgets parameters for page button
        button_font_size = font_size(bm_gg.MAIN_FONT_SIZE_DICT['page_button'],
                                     master.width_sf_min)

        # Creating widgets for page button
        button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=button_font_size)
        button = tk.Button(pagebutton_frame,
                           text=label_text,
                           font=button_font,
                           command=lambda: show_frame(master, page_name))

        # Placing widgets for page button
        button.grid(row=0, column=page_num)


class ParseCorpusPage(tk.Frame):
    """Sets parsing page widgets through `create_parsing_concat` function 
    imported from `bmgui.parse_corpus_page` module."""

    def __init__(self, master, pagebutton_frame, page_frame, institute, wf_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_parsing_concat(self, master, page_name, institute, wf_path, datatype)


class ConsolidateCorpusPage(tk.Frame):
    """Sets corpuses-consolidation page widgets through `create_consolidate_corpus` function 
    imported from `bmgui.consolidate_corpus_page` module."""

    def __init__(self, master, pagebutton_frame, page_frame, institute, wf_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_consolidate_corpus(self, master, page_name, institute, wf_path, datatype)


class UpdateIfPage(tk.Frame):
    """Sets impact-factors-update page widgets through `create_update_ifs` function 
    imported from `bmgui.update_if_page` module."""

    def __init__(self, master, pagebutton_frame, page_frame, institute, wf_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_update_ifs(self, master, page_name, institute, wf_path, datatype)


class AnalyzeCorpusPage(tk.Frame):
    """Sets corpuses-analysis page widgets through `create_analysis` function 
    imported from `bmgui.analyze_corpus_page` module."""

    def __init__(self, master, pagebutton_frame, page_frame, institute, wf_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_analysis(self, master, page_name, institute, wf_path, datatype)
