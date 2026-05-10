"""Module of useful classes for GUI main management."""

__all__ = ['AnalyzeCorpusPage',
           'ConsolidateCorpusPage',
           'PageButton',
           'ParseCorpusPage',
           'SetAuthorCopyright',
           'SetLaunchButton',
           'SetMasterTitle',
           'UpdateIfPage',
           ]


# Standard library imports
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import font as tkFont

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu
import bmgui.pages_utils as bm_pu
from bmfuncts.config_utils import set_affil_params
from bmfuncts.config_utils import set_org_params
from bmfuncts.config_utils import set_parsing_items_params
from bmfuncts.parse_data import set_rawdata
from bmfuncts.useful_functs import print_to_console
from bmfuncts.useful_functs import print_to_log
from bmgui.analyze_corpus_page import create_analysis
from bmgui.consolidate_corpus_page import create_consolidate_corpus
from bmgui.parse_corpus_page import create_parsing_concat
from bmgui.update_if_page import create_update_ifs


class SetMasterTitle:
    """Displays title in main page."""

    def __init__(self, master):

        # Setting widget parameters for page title
        page_title_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.MAIN_FONT_SIZE_DICT,
                                                           ['main_title'])
        page_title_pos_tup = bm_gu.set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['main_title'])

        # Creating widget for page title
        page_title = tk.Label(master,
                              text= master.main_page_title,
                              font=(bm_gg.FONT_NAME, page_title_font_size_tup[0]),
                              justify="center")

        # Placing widget for page title
        page_title.place(x=page_title_pos_tup[0],
                         y=page_title_pos_tup[1],
                         anchor="center")


class SetAuthorCopyright:
    """Displays authors and copyright in main page."""

    def __init__(self, master):
        # Setting widgets parameters for copyright
        au_cop_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.MAIN_FONT_SIZE_DICT,
                                                       ['copyright', 'version'])
        copyright_pos_tup = bm_gu.set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['copyright'])
        version_pos_tup = bm_gu.set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['version'])

        # Creating widgets for copyright
        auteurs_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=au_cop_font_size_tup[0])
        auteurs_label = tk.Label(master,
                                 text=master.app_copyright,
                                 font=auteurs_font_label,
                                 justify="left")
        version_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=au_cop_font_size_tup[1],
                                         weight='bold')
        version_label = tk.Label(master,
                                 text=f"\nVersion {master.app_version}",
                                 font=version_font_label,
                                 justify="right")

        # Placing widgets for copyright
        auteurs_label.place(x=copyright_pos_tup[0],
                            y=copyright_pos_tup[1],
                            anchor="sw")
        version_label.place(x=version_pos_tup[0],
                            y=version_pos_tup[1],
                            anchor="sw")


class SetLaunchButton:
    """Displays corpuses analysis launch button in main window.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        institute (str): The name of the selected Institute.
        wf_path (path): The full path to the selected working folder.
        datatype (str): The selected type of Data combination of corpuses databases.
        set_inst_param (bool): Parameter for getting rid of setting \
        Institute parameters if False.
    """

    def __init__(self, master, institute, wf_path, datatype, set_inst_param):
        # setting common general parameters common to all pages
        bm_pu.set_general_params(master, institute, wf_path, datatype, set_inst_param)

        # Setting font size for launch button
        launch_but_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.MAIN_FONT_SIZE_DICT,
                                                           ['main_launch'])

        # Setting x and y position in pixels for launch button
        launch_but_pos_tup = bm_gu.set_pos_tup_px(master, bm_gg.MAIN_BUT_POS_TUP)

        # Setting launch button
        launch_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=launch_but_font_size_tup[0],
                                  weight='bold')
        launch_button = tk.Button(master,
                                  text=bm_gg.MAIN_BUT_LABEL_DICT['launch'],
                                  font=launch_font,
                                  command=lambda: self._generate_pages(master,))
        # Placing launch button
        launch_button.place(x=launch_but_pos_tup[0],
                            y=launch_but_pos_tup[1],
                            anchor="s")

    def _generate_pages(self, master,):
        """Generates pages after working folder setting.

        Args:
            master (class): `bmgui.main_page.AppMain` class.
        """
        # Setting run info
        run_date_time = str(datetime.now())[:16]
        run_date, run_time = run_date_time.split(" ")
        master.log_file = f"{run_date}_{run_time.replace(':', '-')}_{bm_pg.LOG_FILE}"
        log_title = f"BM ANALYSIS FOR {master.institute}"
        print_txt = (f"\n\n    Date            : {run_date} {run_time}")

        if not master.datatype:
            print_txt += ("\n    Data combination type not yet selected"
                          "\n    Log file not yet created")
            print_to_console(log_title, print_txt)
            warning_title = "!!! ATTENTION !!!"
            warning_text = ("Type de données non selectionné."
                            "\nL'application ne peut pas être lancée."
                            "\nVeuillez le sélectionner avant de lancer l'application.")
            messagebox.showwarning(warning_title, warning_text)
        else:
            print_txt += (f"\n    Data combination: {master.datatype}")

        if not master.wf_path:
            print_txt += ("\n    Working folder not yet defined"
                          "\n    Log file not yet created")
            print_to_console(log_title, print_txt)
            warning_title = "!!! ATTENTION !!!"
            warning_text = ("Chemin non renseigné."
                            "\nL'application ne peut pas être lancée."
                            "\nVeuillez le définir avant de lancer l'application.")
            messagebox.showwarning(warning_title, warning_text)
        else:
            master.wf_root_path = master.wf_path.parent
            if master.set_inst_param:
                # Getting Institute parameters
                master.org_tup = set_org_params(master.institute, master.wf_root_path)

            # Setting years list
            master.years_list = bm_gu.last_available_years(master.wf_path,
                                                           bm_gg.CORPUSES_NUMBER)

            # Printing run info to console and log file
            master.print_params = [master.log_file, bm_pg.LOG_FOLDER, master.wf_path]
            print_txt += (f"\n    Working folder  : {master.wf_path}"
                          f"\n    Corpus list     : {master.years_list}")

            print_to_console(log_title, print_txt)
            print_to_log(log_title, print_txt, master.print_params)

            # Setting affiliations parsing data
            return_tup = set_affil_params(master.institute, master.wf_path)
            (master.parse_affil_params_dic, master.dedup_affil_params_dic,
             master.co_affil_params_dic) = return_tup

            # Setting parsing items parameters
            master.parsing_filenames_dict = set_parsing_items_params()

            # Setting rawdata for datatype
            set_rawdata_params = [master.print_params, master.wf_path,
                                  master.datatype, master.years_list]
            missing_rawdata_dic, rawdata_status = set_rawdata(set_rawdata_params)

            if not rawdata_status:
                warning_title = "!!! ATTENTION : Données indisponibles !!!"
                warning_text = "Des extractions de bases de données sont manquantes.\n"
                for db, db_info in missing_rawdata_dic.items():
                    warning_text += (f"\n - {db_info[1]} manquent dans le dossier de {db}:\n"
                                     f"    {db_info[0]}\n")
                warning_text += ("\nL'application ne peut pas être lancée."
                                 "\nVeuillez ajouter ces données avant de relancer l'application.")
                messagebox.showwarning(warning_title, warning_text)
            else:
                # Setting existing corpuses status
                files_status = bm_gu.existing_corpuses(master.wf_path)
                master.list_corpus_year = files_status[0]
                master.list_wos_rawdata = files_status[1]
                master.list_wos_parsing = files_status[2]
                master.list_scopus_rawdata = files_status[3]
                master.list_scopus_parsing = files_status[4]
                master.list_dedup = files_status[5]

                # Creating two frames in the tk window
                pagebutton_height = bm_gu.set_item_pos(master, bm_gg.PAGE_BUTTON_HEIGHT, 1)
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
                    frame = page(master, pagebutton_frame, page_frame)
                    self.frames[page_name] = frame

                    # Putting all the pages in the same location
                    # The one visible is the one on the top of the stacking order
                    frame.grid(row=0, column=0, sticky="nsew")
                master.frames = self.frames


class PageButton(tk.Frame):
    """Sets button of 'page_name' page.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        page_name (str): Page name.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
    """

    def __init__(self, master, page_name, pagebutton_frame):
        super().__init__(pagebutton_frame)
        self.controller = master

        # Setting page num
        page_num = master.pages_ordered_list.index(page_name)

        # Setting widgets parameters for page button
        button_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.MAIN_FONT_SIZE_DICT,
                                                       ['page_button'])

        # Creating widgets for page button
        button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=button_font_size_tup[0])
        button = tk.Button(pagebutton_frame,
                           text=master.pages_labels[page_name],
                           font=button_font,
                           command=lambda: bm_gu.show_frame(master, page_name))

        # Placing widgets for page button
        button.grid(row=0, column=page_num)


class ParseCorpusPage(tk.Frame):
    """Sets parsing page widgets through `create_parsing_concat` function 
    imported from `bmgui.parse_corpus_page` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
        page_frame (tk.Frame): Frame of master page.
    """

    def __init__(self, master, pagebutton_frame, page_frame):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_parsing_concat(self, master, page_name)


class ConsolidateCorpusPage(tk.Frame):
    """Sets corpuses-consolidation page widgets through `create_consolidate_corpus` function 
    imported from `bmgui.consolidate_corpus_page` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
        page_frame (tk.Frame): Frame of master page.
    """

    def __init__(self, master, pagebutton_frame, page_frame):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_consolidate_corpus(self, master, page_name)


class UpdateIfPage(tk.Frame):
    """Sets impact-factors-update page widgets through `create_update_ifs` function 
    imported from `bmgui.update_if_page` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
        page_frame (tk.Frame): Frame of master page.
    """

    def __init__(self, master, pagebutton_frame, page_frame):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_update_ifs(self, master, page_name)


class AnalyzeCorpusPage(tk.Frame):
    """Sets corpuses-analysis page widgets through `create_analysis` function 
    imported from `bmgui.analyze_corpus_page` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
        page_frame (tk.Frame): Frame of master page.
    """

    def __init__(self, master, pagebutton_frame, page_frame):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_analysis(self, master, page_name)
