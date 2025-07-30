""" The `main_page` module sets the `AppMain` class, its attributes and related secondary classes.
"""
__all__ = ['AppMain']

# Standard library imports
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
import bmfuncts.pub_globals as bm_pg
from bmgui.pages_classes import AnalyzeCorpusPage
from bmgui.pages_classes import UpdateIfPage
from bmgui.pages_classes import ConsolidateCorpusPage
from bmgui.pages_classes import ParseCorpusPage
from bmgui.gui_utils import change_tup_value
from bmgui.gui_utils import enable_buttons
from bmgui.gui_utils import general_properties
from bmgui.gui_utils import set_display_width
from bmgui.gui_utils import set_font_size_tup
from bmgui.gui_utils import set_item_pos
from bmgui.gui_utils import set_pos_tup_px
from bmgui.main_utils import set_institute_widgets
from bmgui.main_utils import update_app_page


class AppMain(tk.Tk):
    """Main class of the application.

    Traces changes in institute selection to update page parameters. 
    'wf' stands for working folder.
    """
    def __init__(self):

        # Internal function
        def _except_hook(args):
            messagebox.showerror("Error", args)
            messagebox.showerror("Exception", traceback.format_exc())
            enable_buttons(bm_gg.GUI_BUTTONS)

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

        # Setting common parameters for widgets of main page
        self.select_font_size_tup = set_font_size_tup(AppMain,
                                                      bm_gg.MAIN_FONT_SIZE_DICT['main_select'],
                                                      ['label', 'button'])
        self.disp_font_size_tup = set_font_size_tup(AppMain,
                                                    bm_gg.MAIN_FONT_SIZE_DICT['main_disp'],
                                                    ['label', 'button'])
        self.val_disp_dx = set_item_pos(AppMain, bm_gg.VAL_DISPLAY_DX, 0)
        self.buttons_dy = set_item_pos(AppMain, bm_gg.MAIN_BUT_DPOS_TUP[1], 1)
        self.opt_but_dy = set_item_pos(AppMain, bm_gg.MAIN_OPT_BUT_DPOS_TUP[1], 1)

        # Setting widget label positions in main page
        self.inst_label_pos_tup = set_pos_tup_px(AppMain,
                                                 bm_gg.MAIN_SELECT_LABEL_POS_DICT['institute'])
        self.datatype_label_pos_tup = set_pos_tup_px(AppMain,
                                                     bm_gg.MAIN_SELECT_LABEL_POS_DICT['datatype'])
        self.wf_pos_tup = set_pos_tup_px(AppMain,
                                         bm_gg.MAIN_DISP_LABEL_POS_DICT['work_folder'])
        self.corpuses_pos_tup = set_pos_tup_px(AppMain,
                                               bm_gg.MAIN_DISP_LABEL_POS_DICT['corpus_list'])

        # Setting widths for displayed information
        self.datatype_width =  set_display_width(AppMain, 'datatype')
        self.wf_width = set_display_width(AppMain, 'work_folder')
        self.corpuses_width = set_display_width(AppMain, 'corpus_list')

        # Setting and placing widgets for title and copyright
        SetMasterTitle(self)
        SetAuthorCopyright(self)

        # Setting default values for Institute selection
        default_institute = "   "
        institute_val = tk.StringVar(self)
        institute_val.set(default_institute)
        set_institute_widgets(self, institute_val)

        # Tracing Institute selection
        institute_val.trace('w', partial(update_app_page, self,
                                         institute_widget=institute_val))

        # Handling exception
        threading.excepthook = _except_hook

class SetMasterTitle():
    """Displays title in main page."""

    def __init__(self, master):

        # Setting widget parameters for page title
        page_title_font_size_tup = set_font_size_tup(master, bm_gg.MAIN_FONT_SIZE_DICT,
                                                     ['main_title'])
        page_title_pos_tup = set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['main_title'])
        if not page_title_pos_tup[0]:
            page_title_pos_tup = change_tup_value(page_title_pos_tup, 0, master.mid_x_pos)

        # Creating widget for page title
        page_title = tk.Label(master,
                              text=bm_gg.MAIN_PAGE_TITLE,
                              font=(bm_gg.FONT_NAME, page_title_font_size_tup[0]),
                              justify="center")

        # Placing widget for page title
        page_title.place(x=page_title_pos_tup[0],
                         y=page_title_pos_tup[1],
                         anchor="center")


class SetAuthorCopyright():
    """Displays authors and copyright in main page."""

    def __init__(self, master):
        # Setting widgets parameters for copyright
        au_cop_font_size_tup = set_font_size_tup(master, bm_gg.MAIN_FONT_SIZE_DICT,
                                                ['copyright', 'version'])        
        copyright_pos_tup = set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['copyright'])
        version_pos_tup = set_pos_tup_px(master, bm_gg.MAIN_INFO_POS_DICT['version'])

        # Creating widgets for copyright
        auteurs_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=au_cop_font_size_tup[0])
        auteurs_label = tk.Label(master,
                                 text=bm_gg.APP_COPYRIGHT,
                                 font=auteurs_font_label,
                                 justify="left")
        version_font_label = tkFont.Font(family=bm_gg.FONT_NAME,
                                         size=au_cop_font_size_tup[1],
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
