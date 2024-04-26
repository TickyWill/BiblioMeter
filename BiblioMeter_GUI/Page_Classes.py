__all__ = ['app_main']

# Standard library imports
import tkinter as tk 
 
class app_main(tk.Tk):
    '''The class app_main inherite the attributes and methods of "tk.Tk" 
    that is the "master" window.
    "bmf" stands for BiblioMeter_Files.
    ''' 

    def __init__(master):
        
        # Standard library imports
        from tkinter import filedialog
        from tkinter import messagebox
        from tkinter import font as tkFont
        from functools import partial
        from pathlib import Path
        
        # 3rd party imports
        from screeninfo import get_monitors
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
        from BiblioMeter_FUNCTS.BM_UsefulFuncts import create_archi 
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import general_properties
        from BiblioMeter_GUI.Useful_Functions import last_available_years
        from BiblioMeter_GUI.Useful_Functions import mm_to_px 
        from BiblioMeter_GUI.Useful_Functions import place_after
        from BiblioMeter_GUI.Useful_Functions import str_size_mm
        
        # Internal functions        
        def _display_path(inst_bmf):
            """Shortening bmf path for easy display""" 
            p = Path(inst_bmf)
            p_disp = ('/'.join(p.parts[0:2])) / Path("...") / ('/'.join(p.parts[-3:]))
            return p_disp
               
        def _get_file(institute_select):
            # Getting new working directory
            dialog_title = "Choisir un nouveau dossier de travail"
            bmf_str = tk.filedialog.askdirectory(title = dialog_title)
            if bmf_str == '':
                warning_title = "!!! Attention !!!"
                warning_text = "Chemin non renseigné."
                return messagebox.showwarning(warning_title, warning_text)  
            
            # Updating bmf values using new working directory
            _set_bmf_widget_param(institute_select, bmf_str)            
            _update_corpi(bmf_str)
            SetLaunchButton(master, institute_select, bmf_str)            
        
        def _set_bmf_widget_param(institute_select, inst_bmf):
            # Setting bmf widgets parameters
            bmf_font = tkFont.Font(family = gg.FONT_NAME, 
                                   size   = eff_bmf_font_size,
                                   weight = 'bold')
            bmf_label       = tk.Label(master, 
                                       text = gg.TEXT_BMF,  
                                       font = bmf_font,)
            bmf_val         = tk.StringVar(master) 
            bmf_val2        = tk.StringVar(master)
            bmf_entree      = tk.Entry(master, textvariable = bmf_val)
            bmf_entree2     = tk.Entry(master, textvariable = bmf_val2, width = eff_bmf_width)
            bmf_button_font = tkFont.Font(family = gg.FONT_NAME,
                                          size   = eff_buttons_font_size)                
            bmf_button      = tk.Button(master, 
                                        text = gg.TEXT_BMF_CHANGE, 
                                        font = bmf_button_font, 
                                        command = lambda: _get_file(institute_select))
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
            bmf_val2.set((_display_path(inst_bmf))) 
        
        def _create_corpus(inst_bmf):
            corpi_val = _set_corpi_widgets_param(inst_bmf)
            bmf_path = Path(inst_bmf)
            try: 
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
                corpi_val.set(str(corpuses_list))
                
            except FileNotFoundError:
                warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
                warning_text  = f"L'accès au dossier {bmf_path} est impossible."
                warning_text += f"\nChoisissez un autre dossier de travail."                       
                messagebox.showwarning(warning_title, warning_text)
                
                # Setting corpi_val value to empty string
                corpi_val.set("")                                           
                
        def _set_corpi_widgets_param(inst_bmf):           
            # Setting corpuses widgets parameters 
            corpi_font   = tkFont.Font(family = gg.FONT_NAME, 
                                       size   = eff_corpi_font_size,
                                       weight = 'bold')
            corpi_val    = tk.StringVar(master)        
            corpi_entry  = tk.Entry(master, textvariable = corpi_val, width = eff_list_width) 
            corpi_button_font = tkFont.Font(family = gg.FONT_NAME,
                                            size   = eff_buttons_font_size)
            corpi_label  = tk.Label(master, 
                                    text = gg.TEXT_CORPUSES,  
                                    font = corpi_font,)                          
            corpi_button = tk.Button(master, 
                                     text = gg.TEXT_BOUTON_CREATION_CORPUS, 
                                     font = corpi_button_font, 
                                     command = lambda: _create_corpus(inst_bmf))
                        # Placing corpuses widgets        
            corpi_label.place(x = eff_corpi_pos_x_px,
                              y = eff_corpi_pos_y_px,)

            text_width_mm, _ = str_size_mm(gg.TEXT_CORPUSES, corpi_font, gg.PPI)
            eff_list_pos_x_px = mm_to_px(text_width_mm + add_space_mm, gg.PPI)                
            corpi_entry.place(x = eff_list_pos_x_px ,
                              y = eff_corpi_pos_y_px,)

            corpi_button.place(x = eff_list_pos_x_px, 
                               y = eff_corpi_pos_y_px + eff_button_dy_px,)
            return corpi_val
            
        def _update_corpi(inst_bmf):
            corpi_val = _set_corpi_widgets_param(inst_bmf)
            bmf_path = Path(inst_bmf)
            try: 
                # Getting updated corpuses list
                corpuses_list = last_available_years(bmf_path, gg.CORPUSES_NUMBER)
                
                # Setting corpi_val value to corpuses list
                corpi_val.set(str(corpuses_list))
                
            except FileNotFoundError:
                warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
                warning_text  = f"L'accès au dossier {bmf_path} est impossible."
                warning_text += f"\nChoisissez un autre dossier de travail."                       
                messagebox.showwarning(warning_title, warning_text)
                
                # Setting corpi_val value to empty string
                corpi_val.set("")                                       
                
        def _update_page(*args, widget = None):
            institute_select = widget.get()
            inst_default_bmf = ig.WORKING_FOLDERS_DICT[institute_select] 
            
            # Managing working folder (bmf stands for "BiblioMeter_Files") 
            _set_bmf_widget_param(institute_select, inst_default_bmf)
            
            # Managing corpus list
            corpi_val = _set_corpi_widgets_param(inst_default_bmf)            
                # Setting and displating corpuses list initial values
            try:
                init_corpuses_list = last_available_years(inst_default_bmf, gg.CORPUSES_NUMBER)
                corpi_val.set(str(init_corpuses_list))
            except FileNotFoundError:
                warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
                warning_text  = f"L'accès au dossier {inst_default_bmf} est impossible."
                warning_text += f"\nChoisissez un autre dossier de travail."                       
                messagebox.showwarning(warning_title, warning_text)
                # Setting corpuses list value to empty string
                corpi_val.set("")              
            
            # Managing analysis launch button 
            SetLaunchButton(master, institute_select, inst_default_bmf)
        
        # Setting the link between "master" and "tk.Tk"
        tk.Tk.__init__(master)
  
        # Setting master attributes and methods  
        _ = get_monitors() # OBLIGATOIRE        
        #master.lift()
        master.attributes("-topmost", True)
        #master.after_idle(master.attributes,'-topmost',False)
        #master.REP = list()  
        
        # Defining pages classes and pages list
        app_main.pages = (Page_Analysis,
                          Page_UpdateIFs,
                          Page_ConsolidateCorpus,
                          Page_ParseCorpus,                     
                         )
        app_main.pages_ordered_list = [x.__name__ for x in app_main.pages][::-1]
        
        # Getting useful screen sizes and scale factors depending on displays properties
        sizes_tuple = general_properties(master)
        app_main.win_width_px  = sizes_tuple[0]
        app_main.win_height_px = sizes_tuple[1]
        app_main.width_sf_px   = sizes_tuple[2] 
        app_main.height_sf_px  = sizes_tuple[3]     
        app_main.width_sf_mm   = sizes_tuple[4]
        app_main.height_sf_mm  = sizes_tuple[5]
        app_main.width_sf_min  = min(app_main.width_sf_mm, app_main.width_sf_px)

        # Setting common parameters for widgets
        add_space_mm = gg.ADD_SPACE_MM
        eff_buttons_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)        
        
        # Setting widgets parameters for institut selection 
        eff_select_font_size = font_size(gg.REF_SUB_TITLE_FONT_SIZE, app_main.width_sf_min)
        inst_button_x_pos    = mm_to_px(gg.REF_INST_POS_X_MM * app_main.width_sf_mm,  gg.PPI)  
        inst_button_y_pos    = mm_to_px(gg.REF_INST_POS_Y_MM * app_main.height_sf_mm, gg.PPI)     
        dy_inst              = -10
        
        # Setting widgets parameters for Working-folder selection 
        eff_bmf_width = int(gg.REF_ENTRY_NB_CHAR * app_main.width_sf_min)
        eff_bmf_font_size = font_size(gg.REF_SUB_TITLE_FONT_SIZE, app_main.width_sf_min)
        eff_bmf_pos_x_px  = mm_to_px(gg.REF_BMF_POS_X_MM * app_main.height_sf_mm, gg.PPI)  
        eff_bmf_pos_y_px  = mm_to_px(gg.REF_BMF_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        eff_button_dy_px  = mm_to_px(gg.REF_BUTTON_DY_MM * app_main.height_sf_mm, gg.PPI) 
        
        # Setting widgets parameters for corpuses display        
        eff_list_width = int(gg.REF_ENTRY_NB_CHAR * app_main.width_sf_min)
        eff_corpi_font_size = font_size(gg.REF_SUB_TITLE_FONT_SIZE, app_main.width_sf_min)      
        eff_corpi_pos_x_px  = mm_to_px(gg.REF_CORPI_POS_X_MM * app_main.height_sf_mm, gg.PPI)
        eff_corpi_pos_y_px  = mm_to_px(gg.REF_CORPI_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        
        # Setting and placing widgets for title and copyright                       
        SetMasterTitle(master)
        SetAuthorCopyright(master)
                
        # Setting default values for Institute selection
        institutes_list = ig.INSTITUTES_LIST   
        default_institute = "   "  
        institute_val = tk.StringVar(master)
        institute_val.set(default_institute)

        # Creating widgets for Institute selection    
        master.font_OptionButton_inst = tkFont.Font(family = gg.FONT_NAME, 
                                                    size = eff_buttons_font_size)
        master.OptionButton_inst = tk.OptionMenu(master, 
                                                 institute_val, 
                                                 *institutes_list)
        master.OptionButton_inst.config(font = master.font_OptionButton_inst)
        master.font_Label_inst = tkFont.Font(family = gg.FONT_NAME, 
                                             size = eff_select_font_size,
                                             weight = 'bold') 
        master.Label_inst = tk.Label(master, 
                                     text = gg.TEXT_INSTITUTE, 
                                     font = master.font_Label_inst)
        
        # Placing widgets for Institute selection
        master.Label_inst.place(x = inst_button_x_pos, y = inst_button_y_pos)
        place_after(master.Label_inst, master.OptionButton_inst, dy = dy_inst)
        
        # Tracing Institute selection
        institute_val.trace('w', partial(_update_page, widget = institute_val))

class SetMasterTitle(tk.Tk):
    
    def __init__(self, master):
        # Standard library imports
        from tkinter import font as tkFont
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg 
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px 
        
        # Setting widget parameters for page title
        eff_page_title_font_size = font_size(gg.REF_PAGE_TITLE_FONT_SIZE, app_main.width_sf_min)
        eff_page_title_pos_y_px  = mm_to_px(gg.REF_PAGE_TITLE_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        mid_page_pos_x_px = app_main.win_width_px  * 0.5
        
        # Creating widget for page title 
        page_title = tk.Label(master, 
                              text = gg.TEXT_TITLE, 
                              font = (gg.FONT_NAME, eff_page_title_font_size), 
                              justify = "center")
        
        # Placing widget for page title
        page_title.place(x = mid_page_pos_x_px, 
                         y = eff_page_title_pos_y_px, 
                         anchor = "center")
        
class SetAuthorCopyright(tk.Tk):
        
    def __init__(self, master):
        # Standard library imports
        from tkinter import font as tkFont
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        from BiblioMeter_GUI.Useful_Functions import font_size 
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        
        # Setting widgets parameters for copyright      
        eff_copyright_font_size = font_size(gg.REF_COPYRIGHT_FONT_SIZE, app_main.width_sf_min)
        eff_version_font_size   = font_size(gg.REF_VERSION_FONT_SIZE, app_main.width_sf_min)
        eff_copyright_x_px = mm_to_px(gg.REF_COPYRIGHT_X_MM * app_main.width_sf_mm, gg.PPI)
        eff_copyright_y_px = mm_to_px(gg.REF_COPYRIGHT_Y_MM * app_main.height_sf_mm, gg.PPI)
        eff_version_x_px = mm_to_px(gg.REF_VERSION_X_MM * app_main.width_sf_mm, gg.PPI)
        eff_version_y_px = mm_to_px(gg.REF_COPYRIGHT_Y_MM * app_main.height_sf_mm, gg.PPI)
           
        # Creating widgets for copyright
        Auteurs_font_label = tkFont.Font(family = gg.FONT_NAME, 
                                         size   = eff_copyright_font_size,)
        Auteurs_label = tk.Label(master, 
                                 text = gg.TEXT_COPYRIGHT, 
                                 font = Auteurs_font_label,
                                 justify = "left")      
        version_font_label = tkFont.Font(family = gg.FONT_NAME, 
                                         size = eff_version_font_size,
                                         weight = 'bold')
        version_label = tk.Label(master, 
                                 text = gg.TEXT_VERSION, 
                                 font = version_font_label,
                                 justify = "right")
        
        # Placing widgets for copyright 
        Auteurs_label.place(x = eff_copyright_x_px, 
                            y = eff_copyright_y_px, 
                            anchor = "sw")        
        version_label.place(x = eff_version_x_px, 
                            y = eff_version_y_px, 
                            anchor = "sw")
        
class SetLaunchButton(tk.Tk):

    def __init__(self, master, institute, bibliometer_path):        
        # Standard library imports
        from tkinter import font as tkFont
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg 
        from BiblioMeter_GUI.Useful_Functions import font_size
        
        tk.Frame.__init__(self)
        
        # Setting font size for launch button
        eff_launch_font_size = font_size(gg.REF_LAUNCH_FONT_SIZE, app_main.width_sf_min)
        
        # Setting x and y position in pixels for launch button
        launch_but_pos_x_px = app_main.win_width_px  * 0.5
        launch_but_pos_y_px = app_main.win_height_px * 0.8
        
        # Setting launch button
        launch_font = tkFont.Font(family = gg.FONT_NAME,
                                  size   = eff_launch_font_size,
                                  weight = 'bold')
        launch_button = tk.Button(master,
                                  text = gg.TEXT_BOUTON_LANCEMENT,
                                  font = launch_font,
                                  command = lambda: self._generate_pages(master, 
                                                                         institute, 
                                                                         bibliometer_path)) 
        # Placing launch button    
        launch_button.place(x = launch_but_pos_x_px,
                            y = launch_but_pos_y_px,
                            anchor = "s")  

    def _generate_pages(self, master, institute, bibliometer_path):
        
        '''Permet la génération des pages après spécification du chemin 
        vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, 
        sinon redemande de renseigner un chemin.
        ''' 
        # Standard library imports
        from tkinter import messagebox
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        
        if bibliometer_path == '':
            warning_title = "!!! Attention !!!"
            warning_text =  "Chemin non renseigné." 
            warning_text += "\nL'application ne peut pas être lancée."
            warning_text += "\nVeuillez le définir."
            messagebox.showwarning(warning_title, warning_text)

        else:
            # Creating two frames in the tk window
            pagebutton_frame = tk.Frame(master, bg = 'red',
                                        height = gg.PAGEBUTTON_HEIGHT_PX)
            pagebutton_frame.pack(side = "top", fill = "both", expand = False)

            page_frame = tk.Frame(master)
            page_frame.pack(side = "top", fill = "both", expand = True)
            page_frame.grid_rowconfigure(0, weight = 1)
            page_frame.grid_columnconfigure(0, weight = 1)

            self.frames = {}
            for page in app_main.pages:
                page_name = page.__name__
                frame = page(master, pagebutton_frame, page_frame, institute, bibliometer_path)
                self.frames[page_name] = frame

                # Putting all of the pages in the same location
                # The one visible is the one on the top of the stacking order
                frame.grid(row = 0, column = 0, sticky = "nsew")
            master.frames = self.frames

class PageButton(tk.Frame):
    
    def __init__(self, master, page_name, pagebutton_frame):
        
        # Standard library imports
        from tkinter import font as tkFont
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        from BiblioMeter_GUI.Useful_Functions import font_size 
        from BiblioMeter_GUI.Useful_Functions import mm_to_px 
        from BiblioMeter_GUI.Useful_Functions import show_frame           
        
        # Setting page num
        label_text = gg.PAGES_LABELS[page_name]
        page_num = app_main.pages_ordered_list.index(page_name)
        
        # Setting widgets parameters for page button
        eff_button_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)
        
        # Creating widgets for page button                 
        button_font = tkFont.Font(family = gg.FONT_NAME, 
                                  size   = eff_button_font_size)
        button = tk.Button(pagebutton_frame, 
                           text = label_text, 
                           font = button_font,
                           command = lambda: show_frame(master, page_name))
        
        # Placing widgets for page button
        button.grid(row = 0, column = page_num)

class Page_ParseCorpus(tk.Frame):
    '''PAGE 1 'Analyse élémentaire des corpus'.
    '''             
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path):
        super().__init__(page_frame)
        self.controller = master      

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        from BiblioMeter_GUI.Page_ParseCorpus import create_parsing_concat      
        
        # Setting page name
        page_name = self.__class__.__name__
        
        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)

        # Creating and setting widgets for page frame
        create_parsing_concat(self, master, page_name, institute, bibliometer_path)
        
class Page_ConsolidateCorpus(tk.Frame):
    '''PAGE 2 'Consolidation annuelle des corpus'. 
    '''        
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path):
        super().__init__(page_frame)
        self.controller = master

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        from BiblioMeter_GUI.Page_ConsolidateCorpus import create_consolidate_corpus      
        
        # Setting page name
        page_name = self.__class__.__name__
        
        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)
        
        # Creating and setting widgets for page frame 
        create_consolidate_corpus(self, master, page_name, institute, bibliometer_path)        


class Page_UpdateIFs(tk.Frame):
    '''PAGE 3 'Mise à jour des IF'. 
    '''    
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path):
        super().__init__(page_frame)
        self.controller = master

        # Standard library imports
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg  
        from BiblioMeter_GUI.Page_UpdateIFs import create_update_ifs      
        
        # Setting page name
        page_name = self.__class__.__name__
        
        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)
        
        # Creating and setting widgets for page frame
        create_update_ifs(self, master, page_name, institute, bibliometer_path)


class Page_Analysis(tk.Frame):
    '''PAGE 4 'Analyse des corpus'.
    '''
    def __init__(self, master, pagebutton_frame, page_frame, institute, bibliometer_path):
        super().__init__(page_frame)
        self.controller = master

        # Standard library imports
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg   
        from BiblioMeter_GUI.Page_Analysis import create_analysis      
        
        # Setting page name
        page_name = self.__class__.__name__
        
        # Creating and setting widgets for page button
        PageButton(master, page_name, pagebutton_frame)
        
        # Creating and setting widgets for page frame
        create_analysis(self, master, page_name, institute, bibliometer_path)
