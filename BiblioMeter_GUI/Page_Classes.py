__all__ = ['app_main']

# Standard library imports
import tkinter as tk 
 
class app_main(tk.Tk):
    '''The class app_main inherite the attributes and methods of "tk.Tk" 
    that is the "master" window.
    "bmf" stands for BiblioMeter_Files.
    ''' 
    
    ############################### Class init - start ###############################
    def __init__(master):
        # Setting the link with "tk.Tk"
        tk.Tk.__init__(master)
        
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
        
        # Internal functions - start        
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
                                          size   = eff_button_font_size)                
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
                                            size   = eff_button_font_size)
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
            
        ############################## Internal functions - end ##############################                   
        
        ######################################## Main ########################################
  
        # Identifying tk window of init class   
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
        app_main.height_sf_px  = sizes_tuple[3]     # unused here
        app_main.width_sf_mm   = sizes_tuple[4]
        app_main.height_sf_mm  = sizes_tuple[5]
        app_main.width_sf_min  = min(app_main.width_sf_mm, app_main.width_sf_px)
        
        # Setting common parameters for widgets
        add_space_mm = gg.ADD_SPACE_MM
        eff_button_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)
        
        ####################### Institute-selection widgets parameters ########################
        # Setting institut selection widgets parameters
        eff_buttons_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)
        eff_select_font_size  = font_size(gg.REF_SUB_TITLE_FONT_SIZE, app_main.width_sf_min)
        inst_button_x_pos     = mm_to_px(gg.REF_INST_POS_X_MM * app_main.width_sf_mm,  gg.PPI)  
        inst_button_y_pos     = mm_to_px(gg.REF_INST_POS_Y_MM * app_main.height_sf_mm, gg.PPI)     
        dy_inst               = -10
        
        ##################### Working-folder selection widgets parameters ######################
        # Setting effective value for bmf entry width
        eff_bmf_width = int(gg.REF_ENTRY_NB_CHAR * app_main.width_sf_min)

        # Setting font size for bmf
        eff_bmf_font_size = font_size(gg.REF_SUB_TITLE_FONT_SIZE, app_main.width_sf_min)       

        # Setting reference positions in mm and effective ones in pixels for bmf 
        eff_bmf_pos_x_px = mm_to_px(gg.REF_BMF_POS_X_MM * app_main.height_sf_mm, gg.PPI)  
        eff_bmf_pos_y_px = mm_to_px(gg.REF_BMF_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        
        # Setting reference relative positions in mm and effective relative 
        # Y positions in pixels for bmf change button
        eff_button_dy_px = mm_to_px(gg.REF_BUTTON_DY_MM * app_main.height_sf_mm, gg.PPI) 
        
        ##################### Corpuses-list-display widgets parameters ######################                
        # Setting effective value for corpi setting width        
        eff_list_width = int(gg.REF_ENTRY_NB_CHAR * app_main.width_sf_min)

        # Setting font size for corpi
        eff_corpi_font_size  = font_size(gg.REF_SUB_TITLE_FONT_SIZE, app_main.width_sf_min)

        # Setting reference positions in mm and effective ones in pixels for corpuses      
        eff_corpi_pos_x_px = mm_to_px(gg.REF_CORPI_POS_X_MM * app_main.height_sf_mm, gg.PPI)
        eff_corpi_pos_y_px = mm_to_px(gg.REF_CORPI_POS_Y_MM * app_main.height_sf_mm, gg.PPI)         
         
        ############################# Launch button parameters ############################## 
        # Setting font size for launch button
        eff_launch_font_size = font_size(gg.REF_LAUNCH_FONT_SIZE, app_main.width_sf_min) 

        # Setting x and y position in pixels for launch button
        launch_but_pos_x_px = app_main.win_width_px  * 0.5
        launch_but_pos_y_px = app_main.win_height_px * 0.8
        
        # Setting default values
        institutes_list = ig.INSTITUTES_LIST   
        default_institute = "   "  
        
        ######################################## Title and copyright                       
        PageTitle(master)
        AuthorCopyright(master)
                
        ######################################## Selection de l'Institut   
        institute_val = tk.StringVar(master)
        institute_val.set(default_institute)

        # Création de l'option button des instituts    
        master.font_OptionButton_inst = tkFont.Font(family = gg.FONT_NAME, 
                                                  size = eff_buttons_font_size)
        master.OptionButton_inst = tk.OptionMenu(master, 
                                               institute_val, 
                                               *institutes_list)
        master.OptionButton_inst.config(font = master.font_OptionButton_inst)

        # Création du label
        master.font_Label_inst = tkFont.Font(family = gg.FONT_NAME, 
                                           size = eff_select_font_size,
                                           weight = 'bold') 
        master.Label_inst = tk.Label(master, 
                                   text = gg.TEXT_INSTITUTE, 
                                   font = master.font_Label_inst)
        master.Label_inst.place(x = inst_button_x_pos, y = inst_button_y_pos)
        place_after(master.Label_inst, master.OptionButton_inst, dy = dy_inst)
        
        # Suivi de la sélection
        institute_val.trace('w', partial(_update_page, widget = institute_val))                
        
    ################################ Class init - end ################################
        
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
            container_button = tk.Frame(master, 
                                        height = gg.CONTAINER_BUTTON_HEIGHT_PX, 
                                        bg = 'red')
            container_button.pack(side = "top", 
                                  fill = "both", 
                                  expand = False)

            container_frame = tk.Frame(master)
            container_frame.pack(side="top", 
                                 fill="both", 
                                 expand=True)
            container_frame.grid_rowconfigure(0, 
                                              weight = 1)
            container_frame.grid_columnconfigure(0, 
                                                 weight = 1)

            self.frames = {}
            for page in app_main.pages:
                page_name = page.__name__
                frame = page(container_frame, master, container_button, institute, bibliometer_path)
                self.frames[page_name] = frame

                # put all of the pages in the same location;
                # the one on the top of the stacking order
                # will be the one that is visible.
                frame.grid(row = 0, 
                           column = 0, 
                           sticky = "nsew")
            master.frames = self.frames


class PageTitle(tk.Tk):
    
    def __init__(self, parent):
        # Standard library imports
        from tkinter import font as tkFont
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_GUI.Useful_Functions as guf
        
        ####################### Title and copyright widgets parameters ########################
        # Setting font size for page title and copyright
        eff_page_title_font_size = guf.font_size(gg.REF_PAGE_TITLE_FONT_SIZE, app_main.width_sf_min)     
        
        # Setting reference Y position in mm and effective Y position in pixels for page label 
        eff_page_title_pos_y_px = guf.mm_to_px(gg.REF_PAGE_TITLE_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page title 
        mid_page_pos_x_px = app_main.win_width_px  * 0.5
        page_title = tk.Label(parent, 
                              text = gg.TEXT_TITLE, 
                              font = (gg.FONT_NAME, eff_page_title_font_size), 
                              justify = "center")
        page_title.place(x = mid_page_pos_x_px, 
                         y = eff_page_title_pos_y_px, 
                         anchor = "center")

class AuthorCopyright(tk.Frame):
        
    def __init__(self, parent):
        # Standard library imports
        from tkinter import font as tkFont
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_GUI.Useful_Functions as guf
        
        # Setting font size for copyright
        ref_copyright_font_size = gg.REF_COPYRIGHT_FONT_SIZE       
        eff_copyright_font_size = guf.font_size(ref_copyright_font_size, app_main.width_sf_min)
        
        # Setting X and Y positions reference in mm for copyright
        ref_copyright_x_mm = gg.REF_COPYRIGHT_X_MM              #5
        eff_copyright_x_px = guf.mm_to_px(ref_copyright_x_mm * app_main.width_sf_mm, gg.PPI)
        ref_copyright_y_mm = gg.REF_COPYRIGHT_Y_MM              #170
        eff_copyright_y_px = guf.mm_to_px(ref_copyright_y_mm * app_main.height_sf_mm, gg.PPI)
        
        # Setting font size for version
        ref_version_font_size = gg.REF_VERSION_FONT_SIZE         #12
        eff_version_font_size = guf.font_size(ref_version_font_size,app_main.width_sf_min)
        
        # Setting X and Y positions reference in mm for version
        ref_version_x_mm = gg.REF_VERSION_X_MM                   #185
        ref_version_y_mm = gg.REF_COPYRIGHT_Y_MM                 #170
        eff_version_y_px = guf.mm_to_px(ref_version_y_mm * app_main.height_sf_mm, gg.PPI)
        eff_version_x_px = guf.mm_to_px(ref_version_x_mm * app_main.width_sf_mm, gg.PPI)
           
    
        Auteurs_font_label = tkFont.Font(family = gg.FONT_NAME, 
                                             size   = eff_copyright_font_size,)
        Auteurs_label = tk.Label(parent, 
                                 text = gg.TEXT_COPYRIGHT, 
                                 font = Auteurs_font_label,
                                 justify = "left")
        Auteurs_label.place(x = eff_copyright_x_px, 
                            y = eff_copyright_y_px, 
                            anchor = "sw")
      
        version_font_label = tkFont.Font(family = gg.FONT_NAME, 
                                         size = eff_version_font_size,
                                         weight = 'bold')
        version_label = tk.Label(parent, 
                                 text = gg.TEXT_VERSION, 
                                 font = version_font_label,
                                 justify = "right")
        version_label.place(x = eff_version_x_px, 
                            y = eff_version_y_px, 
                            anchor = "sw")


class Page_ParseCorpus(tk.Frame):
    '''PAGE 1 'Analyse élémentaire des corpus'.
    '''             
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from tkinter import font as tkFont        

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        from BiblioMeter_GUI.Page_ParseCorpus import create_parsing_concat
        from BiblioMeter_GUI.Useful_Functions import font_size 
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        from BiblioMeter_GUI.Useful_Functions import show_frame
        
        # Setting specific texts
        page_name  = self.__class__.__name__
        page_num   = app_main.pages_ordered_list.index(page_name)
        label_text = gg.PAGES_LABELS[page_name]
        page_title = label_text + " du " + institute         
        
        # Setting font size for page label and button
        eff_label_font_size  = font_size(gg.REF_LABEL_FONT_SIZE, app_main.width_sf_min)
        eff_button_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px   = mm_to_px(gg.REF_LABEL_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = app_main.win_width_px / 2
        
        # Creation of the class object Page 1
        create_parsing_concat(self, institute, bibliometer_path, controller)
        
        label_font = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_label_font_size)
        label = tk.Label(self, 
                         text = page_title, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px,
                    anchor = "center")       
        button_font = tkFont.Font(family = gg.FONT_NAME, 
                                  size   = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font,
                           command = lambda: show_frame(controller, page_name))
        button.grid(row = 0, column = page_num)


class Page_ConsolidateCorpus(tk.Frame):
    '''PAGE 2 'Consolidation annuelle des corpus'. 
    '''        
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # Standard library imports
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        from BiblioMeter_GUI.Page_ConsolidateCorpus import create_consolidate_corpus
        from BiblioMeter_GUI.Useful_Functions import existing_corpuses
        from BiblioMeter_GUI.Useful_Functions import font_size 
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        from BiblioMeter_GUI.Useful_Functions import show_frame  
        
        # Internal functions
        def _launch_consolidate_corpus():
       
            # Getting years of available corpuses from files status       
            files_status = existing_corpuses(bibliometer_path)    
            corpus_years_list = files_status[0]
            Liste_2 = corpus_years_list
            
            if self.Liste_1 != Liste_2:                
                self.Liste_1 = Liste_2                
                create_consolidate_corpus(self, institute, bibliometer_path, controller)                
                label_font = tkFont.Font(family = gg.FONT_NAME, 
                                         size   = eff_label_font_size)
                label = tk.Label(self, 
                                 text = page_title, 
                                 font = label_font)
                label.place(x = mid_page_pos_x_px, 
                            y = eff_label_pos_y_px, 
                            anchor = "center")                
                button_font = tkFont.Font(family = gg.FONT_NAME, 
                                          size   = eff_button_font_size)
                button = tk.Button(container_button, 
                                   text = label_text, 
                                   font = button_font, 
                                   command = lambda: _launch_consolidate_corpus())
                button.grid(row = 0, column = 1)        
            show_frame(controller, page_name)
                
        # Setting specific texts
        page_name  = self.__class__.__name__
        page_num   = app_main.pages_ordered_list.index(page_name)
        label_text = gg.PAGES_LABELS[page_name]
        page_title = label_text + " du " + institute

        # Setting font size for page label and button
        eff_label_font_size  = font_size(gg.REF_LABEL_FONT_SIZE, app_main.width_sf_min)
        eff_button_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px = mm_to_px(gg.REF_LABEL_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = app_main.win_width_px / 2
        
        # Getting years of available corpuses from files status       
        files_status = existing_corpuses(bibliometer_path)    
        corpus_years_list = files_status[0]
        self.Liste_1 = corpus_years_list        
        
        # Creating the class object Page 2
        create_consolidate_corpus(self, institute, bibliometer_path, controller)        
        label_font = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_label_font_size)
        label = tk.Label(self, 
                         text = page_title, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px, 
                    anchor = "center")        
        button_font = tkFont.Font(family = gg.FONT_NAME, 
                                  size   = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font, 
                           command = lambda: _launch_consolidate_corpus())
        button.grid(row = 0, column = page_num)

            
############################ ############################

class Page_UpdateIFs(tk.Frame):
    '''PAGE 3 'Mise à jour des IF'. 
    '''    
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg  
        from BiblioMeter_GUI.Page_UpdateIFs import create_update_ifs
        from BiblioMeter_GUI.Useful_Functions import font_size 
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        from BiblioMeter_GUI.Useful_Functions import show_frame  
        
        # Setting specific texts
        page_name  = self.__class__.__name__
        page_num   = app_main.pages_ordered_list.index(page_name) 
        label_text = gg.PAGES_LABELS[page_name]
        page_title = label_text + " du " + institute
        
        # Setting font size for page label and button
        eff_label_font_size  = font_size(gg.REF_LABEL_FONT_SIZE, app_main.width_sf_min)
        eff_button_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px = mm_to_px(gg.REF_LABEL_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = app_main.win_width_px / 2
        
        # Creation of the class object Page 3
        create_update_ifs(self, institute, bibliometer_path, controller)
        label_font = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_label_font_size)
        label = tk.Label(self, 
                         text = page_title, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px, 
                    anchor = "center")        
        button_font = tkFont.Font(family = gg.FONT_NAME, 
                                  size   = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font, 
                           command = lambda: show_frame(controller, page_name))
        button.grid(row = 0, column = page_num)


class Page_Analysis(tk.Frame):
    '''PAGE 4 'Analyse des corpus'.
    '''
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg   
        from BiblioMeter_GUI.Page_Analysis import create_analysis
        from BiblioMeter_GUI.Useful_Functions import font_size 
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        from BiblioMeter_GUI.Useful_Functions import show_frame 
        
        # Setting specific texts 
        page_name  = self.__class__.__name__
        page_num   = app_main.pages_ordered_list.index(page_name)
        label_text = gg.PAGES_LABELS[page_name]
        page_title = label_text + " du " + institute
        
        # Setting font size for page label and button
        eff_label_font_size  = font_size(gg.REF_LABEL_FONT_SIZE, app_main.width_sf_min)
        eff_button_font_size = font_size(gg.REF_BUTTON_FONT_SIZE, app_main.width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px = mm_to_px(gg.REF_LABEL_POS_Y_MM * app_main.height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = app_main.win_width_px / 2
        
        # Creation of the class object Page 4
        create_analysis(self, institute, bibliometer_path, controller)
        label_font = tkFont.Font(family = gg.FONT_NAME, 
                                 size   = eff_label_font_size)
        label = tk.Label(self, 
                         text = page_title, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px, 
                    anchor = "center")        
        button_font = tkFont.Font(family = gg.FONT_NAME, 
                                  size   = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font, 
                           command = lambda: show_frame(controller, page_name))
        button.grid(row = 0, column = page_num)        