"""Module of useful classes for GUI main management."""

__all__ = ['SetLaunchButton',
           'PageButton',
          ]


# Standard library imports
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu
from bmfuncts.useful_functs import set_rawdata
from bmgui.analyze_corpus_page import create_analysis
from bmgui.consolidate_corpus_page import create_consolidate_corpus
from bmgui.parse_corpus_page import create_parsing_concat
from bmgui.update_if_page import create_update_ifs


class SetLaunchButton(tk.Tk):
    """Displays corpuses analysis launch button in main window.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """

    def __init__(self, master, institute, wf_path, datatype):

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
                                  command=lambda: self._generate_pages(master,
                                                                       institute,
                                                                       wf_path,
                                                                       datatype))
        # Placing launch button
        launch_button.place(x=launch_but_pos_tup[0],
                            y=launch_but_pos_tup[1],
                            anchor="s")

    def _generate_pages(self, master, institute, wf_path, datatype):
        """Generates pages after working folder setting.

        Args:
            master (class): `bmgui.main_page.AppMain` class.
            institute (str): Institute name.
            wf_path (path): Full path to working folder.
            datatype (str): Data combination type from corpuses databases.
        """

        if wf_path=='':
            warning_title = "!!! Attention !!!"
            warning_text =  ("Chemin non renseigné."
                             "\nL'application ne peut pas être lancée."
                             "\nVeuillez le définir.")
            messagebox.showwarning(warning_title, warning_text)

        else:
            # Setting years list
            master.years_list = bm_gu.last_available_years(wf_path,
                                                           bm_gg.CORPUSES_NUMBER)

            if datatype:
                # Setting rawdata for datatype
                for database in bm_pg.BDD_LIST:
                    _ = set_rawdata(wf_path, datatype,
                                    master.years_list, database)

                # Setting existing corpuses status
                files_status = bm_gu.existing_corpuses(wf_path)
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
                if datatype:
                    frame = page(master, pagebutton_frame, page_frame,
                                 institute, wf_path, datatype)
                else:
                    frame = page(master, pagebutton_frame, page_frame,
                                 institute, wf_path)
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

        # Setting page num
        label_text = bm_gg.PAGES_LABELS[page_name]
        page_num = master.pages_ordered_list.index(page_name)

        # Setting widgets parameters for page button
        button_font_size_tup = bm_gu.set_font_size_tup(master, bm_gg.MAIN_FONT_SIZE_DICT,
                                                       ['page_button'])

        # Creating widgets for page button
        button_font = tkFont.Font(family=bm_gg.FONT_NAME,
                                  size=button_font_size_tup[0])
        button = tk.Button(pagebutton_frame,
                           text=label_text,
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
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """

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
    imported from `bmgui.consolidate_corpus_page` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
        page_frame (tk.Frame): Frame of master page.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """

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
    imported from `bmgui.update_if_page` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
        page_frame (tk.Frame): Frame of master page.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """

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
    imported from `bmgui.analyze_corpus_page` module.

    Args:
        master (class): `bmgui.main_page.AppMain` class.
        pagebutton_frame (tk.Frame): Frame of pages buttons.
        page_frame (tk.Frame): Frame of master page.
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
    """

    def __init__(self, master, pagebutton_frame, page_frame, institute, wf_path, datatype):
        super().__init__(page_frame)
        self.controller = master

        # Setting page name
        page_name = self.__class__.__name__

        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_analysis(self, master, page_name, institute, wf_path, datatype)
