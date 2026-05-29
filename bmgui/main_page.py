""" The `main_page` module sets the `AppMain` class, its attributes and related secondary classes.
"""
__all__ = ['AppMain']

# Standard library imports
import threading
import tkinter as tk
from functools import partial
from pathlib import Path

# 3rd party imports
from screeninfo import get_monitors

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmgui.gui_globals as bm_gg
import bmgui.gui_utils as bm_gu
import bmgui.main_utils as bm_mu
from bmgui.pages_classes import AnalyzeCorpusPage
from bmgui.pages_classes import ConsolidateCorpusPage
from bmgui.pages_classes import ParseCorpusPage
from bmgui.pages_classes import UpdateIfPage
from bmgui.pages_classes import SetAuthorCopyright
from bmgui.pages_classes import SetMasterTitle


class AppMain(tk.Tk):
    """Main class of the application.

    Traces changes in institute selection to update page parameters. 
    'wf' stands for working folder.
    """
    def __init__(self):

        # Setting the link between "self" and "tk.Tk"
        tk.Tk.__init__(self)

        # Setting useful paths
        app_functs_path = Path(__file__).parent.parent / Path('bmfuncts')
        config_path = app_functs_path / Path(bm_pg.CONFIG_FOLDER)
        icon_path = config_path / Path('BM-logo.ico')

        # Setting class attributes and methods (mandatory)
        _ = get_monitors()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes,'-topmost', False)
        self.iconbitmap(icon_path)

        # Initializing AppMain attributes set after working folder definition
        (AppMain.years_list, AppMain.list_corpus_year,
         AppMain.list_wos_rawdata, AppMain.list_wos_parsing,
         AppMain.list_scopus_rawdata, AppMain.list_scopus_parsing,
         AppMain.list_dedup) = ([0],) * 7

        # Setting pages classes, pages list and pages labels
        AppMain.pages = (AnalyzeCorpusPage,
                         UpdateIfPage,
                         ConsolidateCorpusPage,
                         ParseCorpusPage,)
        AppMain.pages_ordered_list = [x.__name__ for x in AppMain.pages][::-1]
        AppMain.pages_labels = bm_gg.PAGES_LABELS

        # Getting useful screen sizes and scale factors depending on displays properties
        (AppMain.win_width_px, AppMain.win_height_px, AppMain.width_sf_px, AppMain.height_sf_px,
         AppMain.width_sf_mm, AppMain.height_sf_mm) = bm_gu.general_properties(self,
                                                                               bm_gg.APP_WIN_TITLE)
        AppMain.width_sf_min = min(AppMain.width_sf_mm, AppMain.width_sf_px)
        AppMain.mid_x_pos = int(AppMain.win_width_px * 0.5)
        AppMain.sf_mm_tup = (AppMain.width_sf_mm, AppMain.height_sf_mm)

        # Setting common parameters for widgets of main page
        bm_mu.set_common_params(self, AppMain)

        # Setting widget label positions in main page
        bm_mu.set_labels_pos(self, AppMain)

        # Setting widths for displayed information
        bm_mu.set_displays_widths(self, AppMain)

        # Setting and placing widgets for title and copyright
        AppMain.main_page_title = bm_gg.MAIN_PAGE_TITLE
        AppMain.app_copyright = bm_gg.APP_COPYRIGHT
        AppMain.app_version = bm_gg.VERSION
        SetMasterTitle(self)
        SetAuthorCopyright(self)

        # Setting default values for Institute selection
        default_institute = "   "
        institute_val = tk.StringVar(self)
        institute_val.set(default_institute)
        bm_mu.set_institute_widgets(self, institute_val)

        # Tracing Institute selection
        institute_val.trace('w', partial(bm_mu.update_app_page, self,
                                         institute_val))

        # Handling exception
        threading.excepthook = bm_mu.except_hook
