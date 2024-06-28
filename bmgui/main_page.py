""" The `...` module sets the `AppMain` class, its attributes and related secondary classes.
"""
__all__ = ['AppMain']

# Standard library imports
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont
from functools import partial
from pathlib import Path

# 3rd party imports
from screeninfo import get_monitors

# Local imports
import bmgui.gui_globals as gg
import bmfuncts.institute_globals as ig
import bmfuncts.pub_globals as pg
from bmgui.analyze_corpus_page import create_analysis
from bmgui.consolidate_corpus_page import create_consolidate_corpus
from bmgui.parse_corpus_page import create_parsing_concat
from bmgui.update_if_page import create_update_ifs
from bmgui.gui_utils import existing_corpuses
from bmgui.gui_utils import font_size
from bmgui.gui_utils import general_properties
from bmgui.gui_utils import last_available_years
from bmgui.gui_utils import mm_to_px
from bmgui.gui_utils import place_after
from bmgui.gui_utils import show_frame
from bmgui.gui_utils import str_size_mm
from bmfuncts.useful_functs import create_archi
from bmfuncts.useful_functs import set_rawdata

class AppMain(tk.Tk):
    """The class AppMain inherit the attributes and methods of tk.Tk.
    'bmf' stands for BiblioMeter_Files usual working directory name.
    """
    def __init__(self):

        # Internal functions
        def _set_datatype_widgets_param(datatype_val, datatype_list):
            # Setting widgets parameters for datatype selection
            self.datatype_optionbutton_font = tkFont.Font(family = gg.FONT_NAME,
                                                          size = eff_buttons_font_size)
            self.datatype_optionbutton = tk.OptionMenu(self,
                                                       datatype_val,
                                                       *datatype_list)
            self.datatype_optionbutton.config(font = self.datatype_optionbutton_font,
                                              width = eff_menu_width)
            self.datatype_label_font = tkFont.Font(family = gg.FONT_NAME,
                                                   size = eff_select_font_size,
                                                   weight = 'bold')
            self.datatype_label = tk.Label(self,
                                           text = gg.TEXT_DATATYPE,
                                           font = self.datatype_label_font)

            # Placing widgets for datatype selection
            self.datatype_label.place(x = datatype_button_x_pos, y = datatype_button_y_pos)
            place_after(self.datatype_label, self.datatype_optionbutton, dy = dy_datatype)

        def _display_path(inst_bmf):
            """Shortening bmf path for easy display"""
            p = Path(inst_bmf)
            if len(p.parts) <= 4:
                p_disp = p
            else:
                part_start = p.parts[0:2]
                part_end = p.parts[-3:]
                p_disp = ('/'.join(part_start)) / Path("...") / ('/'.join(part_end))
            return p_disp

        def _get_file(institute_select, datatype_select):
            # Getting new working directory
            dialog_title = "Choisir un nouveau dossier de travail"
            bmf_str = tk.filedialog.askdirectory(title = dialog_title)
            if bmf_str == '':
                warning_title = "!!! Attention !!!"
                warning_text = "Chemin non renseigné."
                messagebox.showwarning(warning_title, warning_text)

            # Updating bmf values using new working directory
            _set_bmf_widget_param(institute_select, bmf_str, datatype_select)
            _update_corpi(bmf_str)
            SetLaunchButton(self, institute_select, bmf_str, datatype_select)

        def _set_bmf_widget_param(institute_select, inst_bmf, datatype_select):
            # Setting bmf widgets parameters
            bmf_font        = tkFont.Font(family = gg.FONT_NAME,
                                          size   = eff_bmf_font_size,
                                          weight = 'bold')
            bmf_label       = tk.Label(self,
                                       text = gg.TEXT_BMF,
                                       font = bmf_font,)
            bmf_val         = tk.StringVar(self)
            bmf_val2        = tk.StringVar(self)
            #bmf_entree      = tk.Entry(self, textvariable = bmf_val)
            bmf_entree2     = tk.Entry(self, textvariable = bmf_val2, width = eff_bmf_width)
            bmf_button_font = tkFont.Font(family = gg.FONT_NAME,
                                          size   = eff_buttons_font_size)
            bmf_button      = tk.Button(self,
                                        text = gg.TEXT_BMF_CHANGE,
                                        font = bmf_button_font,
                                        command = lambda: _get_file(institute_select,
                                                                    datatype_select))
            # Placing bmf widgets
            bmf_label.place(x = eff_bmf_pos_x_px,
                            y = eff_bmf_pos_y_px,)

            text_width_mm, _ = str_size_mm(gg.TEXT_BMF, bmf_font, gg.PPI)
            eff_path_pos_x_px = mm_to_px(text_width_mm + add_space_mm, gg.PPI)
            bmf_entree2.place(x = eff_path_pos_x_px,
                              y = eff_bmf_pos_y_px,)

            bmf_button.place(x = eff_path_pos_x_px,
                             y = eff_bmf_pos_y_px + eff_button_dy_px,)
            bmf_val.set(inst_bmf)
            bmf_val2.set(_display_path(inst_bmf))
        def _try_bmf_access(bmf_path):
            bmf_access_status = False
            if os.access(bmf_path, os.F_OK | os.R_OK | os.W_OK):
                bmf_access_status = True
            else:
                warning_title = "!!! ATTENTION : Accés au dossier impossible !!!"
                warning_text  = (f"Accès non autorisé ou absence du dossier \n   {bmf_path}."
                                 "\n\nChoisissez un autre dossier de travail.")
                messagebox.showwarning(warning_title, warning_text)
            return bmf_access_status

        def _create_corpus(inst_bmf):
            corpi_val = _set_corpi_widgets_param(inst_bmf)
            corpi_val_to_set = ""
            bmf_path = Path(inst_bmf)
            bmf_access_status = _try_bmf_access(bmf_path)
            if bmf_access_status:
                # Setting new corpus year folder name
                corpuses_list    = last_available_years(bmf_path, gg.CORPUSES_NUMBER)
                last_corpus_year = corpuses_list[-1]
                new_corpus_year_folder = str(int(last_corpus_year) + 1)

                # Creating required folders for new corpus year
                message = create_archi(bmf_path, new_corpus_year_folder, verbose = False)
                print("\n",message)

                # Getting updated corpuses list
                corpuses_list = last_available_years(bmf_path, gg.CORPUSES_NUMBER)

                # Setting corpi_val value to corpuses list
                corpi_val_to_set = str(corpuses_list)
            corpi_val.set(corpi_val_to_set)

        def _set_corpi_widgets_param(inst_bmf):
            # Setting corpuses widgets parameters
            corpi_font   = tkFont.Font(family = gg.FONT_NAME,
                                       size   = eff_corpi_font_size,
                                       weight = 'bold')
            corpi_val    = tk.StringVar(self)
            corpi_entry  = tk.Entry(self, textvariable = corpi_val, width = eff_list_width)
            corpi_button_font = tkFont.Font(family = gg.FONT_NAME,
                                            size   = eff_buttons_font_size)
            corpi_label  = tk.Label(self,
                                    text = gg.TEXT_CORPUSES,
                                    font = corpi_font,)
            corpi_button = tk.Button(self,
                                     text = gg.TEXT_BOUTON_CREATION_CORPUS,
                                     font = corpi_button_font,
                                     command = lambda: _create_corpus(inst_bmf))

            # Placing corpuses widgets
            corpi_label.place(x = eff_corpi_pos_x_px,
                              y = eff_corpi_pos_y_px,)

            text_width_mm, _ = str_size_mm(gg.TEXT_CORPUSES, corpi_font, gg.PPI)
            eff_list_pos_x_px = mm_to_px(text_width_mm + add_space_mm, gg.PPI)
            corpi_entry.place(x = eff_list_pos_x_px,
                              y = eff_corpi_pos_y_px,)

            corpi_button.place(x = eff_list_pos_x_px,
                               y = eff_corpi_pos_y_px + eff_button_dy_px,)
            return corpi_val

        def _update_corpi(inst_bmf):
            corpi_val = _set_corpi_widgets_param(inst_bmf)
            corpi_val_to_set = ""
            bmf_path = Path(inst_bmf)
            bmf_access_status = _try_bmf_access(bmf_path)
            if bmf_access_status:
                # Getting updated corpuses list
                corpuses_list = last_available_years(bmf_path, gg.CORPUSES_NUMBER)

                # Setting corpi_val value to corpuses list
                corpi_val_to_set = str(corpuses_list)
            corpi_val.set(corpi_val_to_set)

        def _update_datatype(*args, datatype_widget = None):
            datatype_select = datatype_widget.get()
            self.datatype_optionbutton.configure(state = 'disabled')

            # Managing working folder (bmf stands for "BiblioMeter_Files")
            institute_select = args[0]
            inst_default_bmf = ig.WORKING_FOLDERS_DICT[institute_select]
            _set_bmf_widget_param(institute_select, inst_default_bmf, datatype_select)

            # Managing corpus list
            corpi_val = _set_corpi_widgets_param(inst_default_bmf)

            # Setting and displaying corpuses list initial values
            corpi_val_to_set = ""
            default_bmf_path = Path(inst_default_bmf)
            info_title = "- Information -"
            info_text = ("Le test de l'accès au dossier de travail défini "
                         "par défaut peut prendre un peu de temps."
                         "\n\nMerci de patienter.")
            messagebox.showinfo(info_title, info_text)
            bmf_access_status = _try_bmf_access(default_bmf_path)
            if bmf_access_status:
                info_title = "- Information -"
                info_text = ("L'accès au dossier de travail défini "
                             "par défaut est autorisé mais vous pouvez "
                             "en choisir un autre.")
                messagebox.showinfo(info_title, info_text)
                init_corpuses_list = last_available_years(default_bmf_path, gg.CORPUSES_NUMBER)
                corpi_val_to_set = str(init_corpuses_list)
            corpi_val.set(corpi_val_to_set)

            # Managing analysis launch button
            SetLaunchButton(self, institute_select, inst_default_bmf, datatype_select)

        def _update_page(*args, institute_widget = None):
            _ = args
            institute_select = institute_widget.get()

            # Setting default values for datatype selection
            datatype_list = pg.DATATYPE_LIST
            default_datatype = " "
            datatype_val = tk.StringVar(self)
            datatype_val.set(default_datatype)

            # Creating widgets for datatype selection
            _set_datatype_widgets_param(datatype_val, datatype_list)

            # Tracing data type selection
            datatype_val.trace('w',
                               partial(_update_datatype, institute_select,
                                       datatype_widget = datatype_val))

        # Setting the link between "self" and "tk.Tk"
        tk.Tk.__init__(self)

        # Setting class attributes and methods
        _ = get_monitors() # Mandatory
        #self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes,'-topmost', False)
        icon_path = Path(__file__).parent.parent / Path('bmfuncts') / Path(pg.CONFIG_FOLDER)
        icon_path = icon_path / Path('BM-logo.ico')
        self.iconbitmap(icon_path)
        #self.REP = list()

        # Initializing AppMain attributes set after working folder definition
        AppMain.years_list          = []
        AppMain.list_corpus_year    = []
        AppMain.list_wos_rawdata    = []
        AppMain.list_wos_parsing    = []
        AppMain.list_scopus_rawdata = []
        AppMain.list_scopus_parsing = []
        AppMain.list_dedup          = []

        # Setting pages classes and pages list
        AppMain.pages = (AnalyzeCorpusPage,
                         UpdateIfPage,
                         ConsolidateCorpusPage,
                         ParseCorpusPage,)
        AppMain.pages_ordered_list = [x.__name__ for x in AppMain.pages][::-1]

        # Getting useful screen sizes and scale factors depending on displays properties
        sizes_tuple = general_properties(self)
        AppMain.win_width_px  = sizes_tuple[0]
        AppMain.win_height_px = sizes_tuple[1]
        AppMain.width_sf_px   = sizes_tuple[2]
        AppMain.height_sf_px  = sizes_tuple[3]
        AppMain.width_sf_mm   = sizes_tuple[4]
        AppMain.height_sf_mm  = sizes_tuple[5]
        AppMain.width_sf_min  = min(AppMain.width_sf_mm, AppMain.width_sf_px)

        # Setting common parameters for widgets
        add_space_mm = gg.ADD_SPACE_MM
        eff_buttons_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, AppMain.width_sf_min)

        # Setting widgets parameters for institute selection
        eff_select_font_size = font_size(gg.REF_SUB_TITLE_FONT_SIZE, AppMain.width_sf_min)
        inst_button_x_pos    = mm_to_px(gg.REF_INST_POS_X_MM * AppMain.width_sf_mm,  gg.PPI)
        inst_button_y_pos    = mm_to_px(gg.REF_INST_POS_Y_MM * AppMain.height_sf_mm, gg.PPI)
        dy_inst              = -10

        # Setting widgets parameters for Working-folder selection
        eff_bmf_width = int(gg.REF_ENTRY_NB_CHAR * AppMain.width_sf_min)
        eff_bmf_font_size = font_size(gg.REF_SUB_TITLE_FONT_SIZE, AppMain.width_sf_min)
        eff_bmf_pos_x_px  = mm_to_px(gg.REF_BMF_POS_X_MM * AppMain.height_sf_mm, gg.PPI)
        eff_bmf_pos_y_px  = mm_to_px(gg.REF_BMF_POS_Y_MM * AppMain.height_sf_mm, gg.PPI)
        eff_button_dy_px  = mm_to_px(gg.REF_BUTTON_DY_MM * AppMain.height_sf_mm, gg.PPI)

        # Setting widgets parameters for corpuses display
        eff_list_width = int(gg.REF_ENTRY_NB_CHAR * AppMain.width_sf_min)
        eff_corpi_font_size = font_size(gg.REF_SUB_TITLE_FONT_SIZE, AppMain.width_sf_min)
        eff_corpi_pos_x_px  = mm_to_px(gg.REF_CORPI_POS_X_MM * AppMain.height_sf_mm, gg.PPI)
        eff_corpi_pos_y_px  = mm_to_px(gg.REF_CORPI_POS_Y_MM * AppMain.height_sf_mm, gg.PPI)

        # Setting widgets parameters for datatype selection
        eff_menu_width = int(30 * AppMain.width_sf_min)     # gg.REF_MENU_NB_CHAR
        eff_select_font_size  = font_size(gg.REF_SUB_TITLE_FONT_SIZE,
                                          AppMain.width_sf_min)
        datatype_button_x_pos = mm_to_px(gg.REF_DATATYPE_POS_X_MM * AppMain.width_sf_mm, gg.PPI)
        datatype_button_y_pos = mm_to_px(gg.REF_DATATYPE_POS_Y_MM * AppMain.height_sf_mm, gg.PPI)
        dy_datatype           = -10

        # Setting and placing widgets for title and copyright
        SetMasterTitle(self)
        SetAuthorCopyright(self)

        # Setting default values for Institute selection
        institutes_list = ig.INSTITUTES_LIST
        default_institute = "   "
        institute_val = tk.StringVar(self)
        institute_val.set(default_institute)

        # Creating widgets for Institute selection
        self.inst_optionbutton_font = tkFont.Font(family = gg.FONT_NAME,
                                                  size = eff_buttons_font_size)
        self.inst_optionbutton = tk.OptionMenu(self,
                                               institute_val,
                                               *institutes_list)
        self.inst_optionbutton.config(font = self.inst_optionbutton_font)
        self.inst_label_font = tkFont.Font(family = gg.FONT_NAME,
                                           size = eff_select_font_size,
                                           weight = 'bold')
        self.inst_label = tk.Label(self,
                                   text = gg.TEXT_INSTITUTE,
                                   font = self.inst_label_font)

        # Placing widgets for Institute selection
        self.inst_label.place(x = inst_button_x_pos, y = inst_button_y_pos)
        place_after(self.inst_label, self.inst_optionbutton, dy = dy_inst)

        # Tracing Institute selection
        institute_val.trace('w', partial(_update_page, institute_widget = institute_val))

class SetMasterTitle():
    """

    """
    def __init__(self, master):

        # Setting widget parameters for page title
        eff_page_title_font_size = font_size(gg.REF_PAGE_TITLE_FONT_SIZE, master.width_sf_min)
        eff_page_title_pos_y_px  = mm_to_px(gg.REF_PAGE_TITLE_POS_Y_MM * master.height_sf_mm,
                                            gg.PPI)
        mid_page_pos_x_px = master.win_width_px * 0.5

        # Creating widget for page title
        page_title = tk.Label(master,
                              text = gg.TEXT_TITLE,
                              font = (gg.FONT_NAME, eff_page_title_font_size),
                              justify = "center")

        # Placing widget for page title
        page_title.place(x = mid_page_pos_x_px,
                         y = eff_page_title_pos_y_px,
                         anchor = "center")

class SetAuthorCopyright():
    """

    """
    def __init__(self, master):

        # Setting widgets parameters for copyright
        eff_copyright_font_size = font_size(gg.REF_COPYRIGHT_FONT_SIZE, master.width_sf_min)
        eff_version_font_size   = font_size(gg.REF_VERSION_FONT_SIZE, master.width_sf_min)
        eff_copyright_x_px = mm_to_px(gg.REF_COPYRIGHT_X_MM * master.width_sf_mm, gg.PPI)
        eff_copyright_y_px = mm_to_px(gg.REF_COPYRIGHT_Y_MM * master.height_sf_mm, gg.PPI)
        eff_version_x_px = mm_to_px(gg.REF_VERSION_X_MM * master.width_sf_mm, gg.PPI)
        eff_version_y_px = mm_to_px(gg.REF_COPYRIGHT_Y_MM * master.height_sf_mm, gg.PPI)

        # Creating widgets for copyright
        auteurs_font_label = tkFont.Font(family = gg.FONT_NAME,
                                         size   = eff_copyright_font_size,)
        auteurs_label = tk.Label(master,
                                 text = gg.TEXT_COPYRIGHT,
                                 font = auteurs_font_label,
                                 justify = "left")
        version_font_label = tkFont.Font(family = gg.FONT_NAME,
                                         size = eff_version_font_size,
                                         weight = 'bold')
        version_label = tk.Label(master,
                                 text = gg.TEXT_VERSION,
                                 font = version_font_label,
                                 justify = "right")

        # Placing widgets for copyright
        auteurs_label.place(x = eff_copyright_x_px,
                            y = eff_copyright_y_px,
                            anchor = "sw")
        version_label.place(x = eff_version_x_px,
                            y = eff_version_y_px,
                            anchor = "sw")

class SetLaunchButton(tk.Tk):
    """

    """
    def __init__(self, master, institute, bibliometer_path, datatype):

        tk.Frame.__init__(self)

        # Setting font size for launch button
        eff_launch_font_size = font_size(gg.REF_LAUNCH_FONT_SIZE, master.width_sf_min)

        # Setting x and y position in pixels for launch button
        launch_but_pos_x_px = master.win_width_px  * 0.5
        launch_but_pos_y_px = master.win_height_px * 0.8

        # Setting launch button
        launch_font = tkFont.Font(family = gg.FONT_NAME,
                                  size   = eff_launch_font_size,
                                  weight = 'bold')
        launch_button = tk.Button(master,
                                  text = gg.TEXT_BOUTON_LANCEMENT,
                                  font = launch_font,
                                  command = lambda: self._generate_pages(master,
                                                                         institute,
                                                                         bibliometer_path,
                                                                         datatype))
        # Placing launch button
        launch_button.place(x = launch_but_pos_x_px,
                            y = launch_but_pos_y_px,
                            anchor = "s")

    def _generate_pages(self, master, institute, bibliometer_path, datatype):
        """Permet la génération des pages après spécification du chemin
        vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant,
        sinon redemande de renseigner un chemin.
        """

        if bibliometer_path == '':
            warning_title = "!!! Attention !!!"
            warning_text =  "Chemin non renseigné."
            warning_text += "\nL'application ne peut pas être lancée."
            warning_text += "\nVeuillez le définir."
            messagebox.showwarning(warning_title, warning_text)

        else:
            # Setting years list
            master.years_list = last_available_years(bibliometer_path,
                                                       gg.CORPUSES_NUMBER)

            # Setting rawdata for datatype
            for database in pg.BDD_LIST:
                _ = set_rawdata(bibliometer_path, datatype,
                                master.years_list, database)

            # Setting existing corpuses status
            files_status = existing_corpuses(bibliometer_path)
            master.list_corpus_year    = files_status[0]
            master.list_wos_rawdata    = files_status[1]
            master.list_wos_parsing    = files_status[2]
            master.list_scopus_rawdata = files_status[3]
            master.list_scopus_parsing = files_status[4]
            master.list_dedup          = files_status[5]

            # Creating two frames in the tk window
            pagebutton_frame = tk.Frame(master, bg = 'red',
                                        height = gg.PAGEBUTTON_HEIGHT_PX)
            pagebutton_frame.pack(side = "top", fill = "both", expand = False)

            page_frame = tk.Frame(master)
            page_frame.pack(side = "top", fill = "both", expand = True)
            page_frame.grid_rowconfigure(0, weight = 1)
            page_frame.grid_columnconfigure(0, weight = 1)

            self.frames = {}
            for page in master.pages:
                page_name = page.__name__
                frame = page(master, pagebutton_frame, page_frame,
                             institute, bibliometer_path, datatype)
                self.frames[page_name] = frame

                # Putting all of the pages in the same location
                # The one visible is the one on the top of the stacking order
                frame.grid(row = 0, column = 0, sticky = "nsew")
            master.frames = self.frames

class PageButton(tk.Frame):
    """
    """
    def __init__(self, master, page_name, pagebutton_frame):

        # Setting page num
        label_text = gg.PAGES_LABELS[page_name]
        page_num = master.pages_ordered_list.index(page_name)

        # Setting widgets parameters for page button
        eff_button_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, master.width_sf_min)

        # Creating widgets for page button
        button_font = tkFont.Font(family = gg.FONT_NAME,
                                  size   = eff_button_font_size)
        button = tk.Button(pagebutton_frame,
                           text = label_text,
                           font = button_font,
                           command = lambda: show_frame(master, page_name))

        # Placing widgets for page button
        button.grid(row = 0, column = page_num)


class ParseCorpusPage(tk.Frame):
    """PAGE 1 'Analyse élémentaire des corpus'.
    """
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_parsing_concat(self, master, page_name, institute, bibliometer_path, datatype)

class ConsolidateCorpusPage(tk.Frame):
    """PAGE 2 'Consolidation annuelle des corpus'.
    """
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_consolidate_corpus(self, master, page_name, institute, bibliometer_path, datatype)


class UpdateIfPage(tk.Frame):
    """PAGE 3 'Mise à jour des IF'.
    """
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_update_ifs(self, master, page_name, institute, bibliometer_path, datatype)


class AnalyzeCorpusPage(tk.Frame):
    """PAGE 4 'Analyse des corpus'.
    """
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_analysis(self, master, page_name, institute, bibliometer_path, datatype)
