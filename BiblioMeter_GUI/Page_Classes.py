__all__ = ['app_main']

import tkinter as tk 
 
class app_main(tk.Tk):
    '''PAGE de lancement.
    bmf stands for BiblioMeter_Files.
    '''               
    ############################### Class init - start ###############################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Standard library imports
        from functools import partial
        from screeninfo import get_monitors
        from pathlib import Path
        
        # 3rd party imports
        import tkinter as tk
        from tkinter import filedialog
        from tkinter import messagebox
        from tkinter import font as tkFont
        
        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_GUI.Useful_Functions as guf
        import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
        from BiblioMeter_FUNCTS.BM_UsefulFuncts import create_archi 
        
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
            _set_launch_button(institute_select, bmf_str)
            
        
        def _set_bmf_widget_param(institute_select, inst_bmf):
            # Setting bmf widgets parameters
            bmf_font = tkFont.Font(family = gg.FONT_NAME, 
                                   size   = eff_bmf_font_size,
                                   weight = 'bold')
            bmf_label       = tk.Label(self, 
                                       text = gg.TEXT_BMF,  
                                       font = bmf_font,)
            bmf_val         = tk.StringVar(self) 
            bmf_val2        = tk.StringVar(self)
            bmf_entree      = tk.Entry(self, textvariable = bmf_val)
            bmf_entree2     = tk.Entry(self, textvariable = bmf_val2, width = eff_bmf_width)
            bmf_button_font = tkFont.Font(family = gg.FONT_NAME,
                                          size   = eff_button_font_size)                
            bmf_button      = tk.Button(self, 
                                        text = gg.TEXT_BMF_CHANGE, 
                                        font = bmf_button_font, 
                                        command = lambda: _get_file(institute_select))
            # Placing bmf widgets
            bmf_label.place(x = eff_bmf_pos_x_px,
                            y = eff_bmf_pos_y_px,)

            text_width_mm, _ = guf.str_size_mm(gg.TEXT_BMF,
                                               bmf_font,
                                               gg.PPI)
            eff_path_pos_x_px = guf.mm_to_px(text_width_mm + add_space_mm, gg.PPI)                
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
                corpuses_list    = guf.last_available_years(bmf_path, gg.CORPUSES_NUMBER)
                last_corpus_year = corpuses_list[-1]
                new_corpus_year_folder = str(int(last_corpus_year) + 1)
                
                # Creating required folders for new corpus year
                message = create_archi(bmf_path, new_corpus_year_folder, verbose = False)
                print("\n",message)

                # Getting updated corpuses list
                corpuses_list = guf.last_available_years(bmf_path, gg.CORPUSES_NUMBER)
                
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
            corpi_val    = tk.StringVar(self)        
            corpi_entry  = tk.Entry(self, textvariable = corpi_val, width = eff_list_width) 
            corpi_button_font = tkFont.Font(family = gg.FONT_NAME,
                                            size   = eff_button_font_size)
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

            text_width_mm, _ = guf.str_size_mm(gg.TEXT_CORPUSES,
                                               corpi_font,
                                               gg.PPI)
            eff_list_pos_x_px = guf.mm_to_px(text_width_mm + add_space_mm, gg.PPI)                
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
                corpuses_list = guf.last_available_years(bmf_path, gg.CORPUSES_NUMBER)
                
                # Setting corpi_val value to corpuses list
                corpi_val.set(str(corpuses_list))
                
            except FileNotFoundError:
                warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
                warning_text  = f"L'accès au dossier {bmf_path} est impossible."
                warning_text += f"\nChoisissez un autre dossier de travail."                       
                messagebox.showwarning(warning_title, warning_text)
                
                # Setting corpi_val value to empty string
                corpi_val.set("")            

                
        def _set_launch_button(institute, inst_bmf):
            # Setting launch button
            launch_font = tkFont.Font(family = gg.FONT_NAME,
                                      size   = eff_launch_font_size,
                                      weight = 'bold')
            launch_button = tk.Button(self,
                                      text = gg.TEXT_BOUTON_LANCEMENT,
                                      font = launch_font,
                                      command = lambda: self._generate_pages(institute, inst_bmf))                            
            # Plqcing launch button    
            launch_button.place(x = launch_but_pos_x_px,
                                y = launch_but_pos_y_px,
                                anchor = "s") 
                            
                
        def _update_page(*args, widget = None):
            institute_select = widget.get()
            inst_default_bmf = ig.WORKING_FOLDERS_DICT[institute_select] 
            
            # Managing working folder (bmf stands for "BiblioMeter_Files") 
            _set_bmf_widget_param(institute_select, inst_default_bmf)
            
            # Managing corpus list
            corpi_val = _set_corpi_widgets_param(inst_default_bmf)            
                # Setting and displating corpuses list initial values
            try:
                init_corpuses_list = guf.last_available_years(inst_default_bmf, gg.CORPUSES_NUMBER)
                corpi_val.set(str(init_corpuses_list))
            except FileNotFoundError:
                warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
                warning_text  = f"L'accès au dossier {inst_default_bmf} est impossible."
                warning_text += f"\nChoisissez un autre dossier de travail."                       
                messagebox.showwarning(warning_title, warning_text)
                # Setting corpuses list value to empty string
                corpi_val.set("")              
            
            # Managing analysis launch button             
            _set_launch_button(institute_select, inst_default_bmf)                            
        ############################## Internal functions - end ##############################                   
        
        ######################################## Main ########################################
  
        # Identifying tk window of init class   
        _ = get_monitors() # OBLIGATOIRE        
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes,'-topmost',False)
        self.REP = list()                    
        
        # Getting useful screen sizes and scale factors depending on displays properties
        self, sizes_tuple = guf.general_properties(self)
        win_width_px  = sizes_tuple[0]
        win_height_px = sizes_tuple[1]
        width_sf_px   = sizes_tuple[2] 
        height_sf_px  = sizes_tuple[3]     # unused here
        width_sf_mm   = sizes_tuple[4]
        height_sf_mm  = sizes_tuple[5]
        width_sf_min  = min(width_sf_mm, width_sf_px)
        
        # Setting common parameters for widgets
        add_space_mm = gg.ADD_SPACE_MM
        
        ####################### Title and copyright widgets parameters ########################
        # Setting font size for page title and copyright
        eff_page_title_font_size = guf.font_size(gg.REF_PAGE_TITLE_FONT_SIZE, width_sf_min)     
       
        # Setting reference Y position in mm and effective Y position in pixels for page label 
        eff_page_title_pos_y_px = guf.mm_to_px(gg.REF_PAGE_TITLE_POS_Y_MM * height_sf_mm, gg.PPI)
       
        # Setting x position in pixels for page title 
        mid_page_pos_x_px = win_width_px  * 0.5 
        
        # Setting font size for copyright
        ref_copyright_font_size = gg.REF_COPYRIGHT_FONT_SIZE       
        eff_copyright_font_size = guf.font_size(ref_copyright_font_size, width_sf_min)
        
        # Setting X and Y positions reference in mm for copyright
        ref_copyright_x_mm = gg.REF_COPYRIGHT_X_MM              #5
        eff_copyright_x_px = guf.mm_to_px(ref_copyright_x_mm * width_sf_mm, gg.PPI)
        ref_copyright_y_mm = gg.REF_COPYRIGHT_Y_MM              #170
        eff_copyright_y_px = guf.mm_to_px(ref_copyright_y_mm * height_sf_mm, gg.PPI)
        
        # Setting font size for version
        ref_version_font_size = gg.REF_VERSION_FONT_SIZE         #12
        eff_version_font_size = guf.font_size(ref_version_font_size, width_sf_min)
        
        # Setting X and Y positions reference in mm for version
        ref_version_x_mm = gg.REF_VERSION_X_MM                   #185
        eff_version_x_px = guf.mm_to_px(ref_version_x_mm * width_sf_mm, gg.PPI)
        ref_version_y_mm = gg.REF_COPYRIGHT_Y_MM                 #170
        eff_version_y_px = guf.mm_to_px(ref_version_y_mm * height_sf_mm, gg.PPI)
        
        ####################### Institute-selection widgets parameters ########################
        # Setting institut selection widgets parameters
        eff_buttons_font_size = guf.font_size(gg.REF_BUTTON_FONT_SIZE, width_sf_min)
        eff_select_font_size  = guf.font_size(gg.REF_SUB_TITLE_FONT_SIZE, width_sf_min)
        inst_button_x_pos     = guf.mm_to_px(gg.REF_INST_POS_X_MM * width_sf_mm,  gg.PPI)  
        inst_button_y_pos     = guf.mm_to_px(gg.REF_INST_POS_Y_MM * height_sf_mm, gg.PPI)     
        dy_inst               = -10
        
        ##################### Working-folder selection widgets parameters ######################
        # Setting effective value for bmf entry width
        eff_bmf_width = int(gg.REF_ENTRY_NB_CHAR * width_sf_min)

        # Setting font size for bmf
        eff_bmf_font_size    = guf.font_size(gg.REF_SUB_TITLE_FONT_SIZE, width_sf_min)
        eff_button_font_size = guf.font_size(gg.REF_BUTTON_FONT_SIZE, width_sf_min)

        # Setting reference positions in mm and effective ones in pixels for bmf 
        eff_bmf_pos_x_px = guf.mm_to_px(gg.REF_BMF_POS_X_MM * height_sf_mm, gg.PPI)  
        eff_bmf_pos_y_px = guf.mm_to_px(gg.REF_BMF_POS_Y_MM * height_sf_mm, gg.PPI)         

        # Setting reference relative positions in mm and effective relative 
        # X,Y positions in pixels for bmf change button
        eff_button_dx_px = guf.mm_to_px(gg.REF_BUTTON_DX_MM * width_sf_mm,  gg.PPI)
        eff_button_dy_px = guf.mm_to_px(gg.REF_BUTTON_DY_MM * height_sf_mm, gg.PPI) 
        
        ##################### Corpuses-list-display widgets parameters ######################                
        # Setting effective value for corpi setting width        
        eff_list_width = int(gg.REF_ENTRY_NB_CHAR * width_sf_min)

        # Setting font size for corpi
        eff_corpi_font_size  = guf.font_size(gg.REF_SUB_TITLE_FONT_SIZE, width_sf_min)
        eff_button_font_size = guf.font_size(gg.REF_BUTTON_FONT_SIZE, width_sf_min)

        # Setting reference positions in mm and effective ones in pixels for corpuses 
        ref_corpi_pos_x_mm = gg.REF_CORPI_POS_X_MM           #5       
        eff_corpi_pos_x_px = guf.mm_to_px(ref_corpi_pos_x_mm * height_sf_mm, gg.PPI)       
        ref_corpi_pos_y_mm = gg.REF_CORPI_POS_Y_MM          #75
        eff_corpi_pos_y_px = guf.mm_to_px(ref_corpi_pos_y_mm * height_sf_mm, gg.PPI)

        # Setting reference relative positions in mm and effective relative 
        # Y positions in pixels for bmf change button
        eff_button_dy_px = guf.mm_to_px(gg.REF_BUTTON_DY_MM * height_sf_mm, gg.PPI)         
         
        ############################# Launch button parameters ############################## 
        # Setting font size for launch button
        ref_launch_font_size = gg.REF_LAUNCH_FONT_SIZE          #25
        eff_launch_font_size = guf.font_size(ref_launch_font_size, width_sf_min) 

        # Setting x and y position in pixels for launch button
        launch_but_pos_x_px = win_width_px  * 0.5
        launch_but_pos_y_px = win_height_px * 0.8         
        
        # Setting default values
        institutes_list = ig.INSTITUTES_LIST
        #default_institute = institutes_list[0]    
        default_institute = "   "  
        
        ######################################## Title - start                       
        page_title = tk.Label(self, 
                              text = gg.TEXT_TITLE, 
                              font = (gg.FONT_NAME, eff_page_title_font_size), 
                              justify = "center")
        page_title.place(x = mid_page_pos_x_px, 
                         y = eff_page_title_pos_y_px, 
                         anchor = "center")
        ######################################## Title - end        
                
        ######################################## Selection de l'Institut   
        institute_val = tk.StringVar(self)
        institute_val.set(default_institute)

        # Création de l'option button des instituts    
        self.font_OptionButton_inst = tkFont.Font(family = gg.FONT_NAME, 
                                                  size = eff_buttons_font_size)
        self.OptionButton_inst = tk.OptionMenu(self, 
                                               institute_val, 
                                               *institutes_list)
        self.OptionButton_inst.config(font = self.font_OptionButton_inst)

        # Création du label
        self.font_Label_inst = tkFont.Font(family = gg.FONT_NAME, 
                                           size = eff_select_font_size,
                                           weight = 'bold') 
        self.Label_inst = tk.Label(self, 
                                   text = gg.TEXT_INSTITUTE, 
                                   font = self.font_Label_inst)
        self.Label_inst.place(x = inst_button_x_pos, y = inst_button_y_pos)
        guf.place_after(self.Label_inst, self.OptionButton_inst, dy = dy_inst)
        
        # Suivi de la sélection
        institute_val.trace('w', partial(_update_page, widget = institute_val))                

        
        ######################################## Auteurs et versions         
        Auteurs_font_label = tkFont.Font(family = gg.FONT_NAME, 
                                         size   = eff_copyright_font_size,)
        Auteurs_label = tk.Label(self, 
                                 text = gg.TEXT_COPYRIGHT, 
                                 font = Auteurs_font_label,
                                 justify = "left")
        Auteurs_label.place(x = eff_copyright_x_px, 
                            y = eff_copyright_y_px, 
                            anchor = "sw")
      
        version_font_label = tkFont.Font(family = gg.FONT_NAME, 
                                         size = eff_version_font_size,
                                         weight = 'bold')
        version_label = tk.Label(self, 
                                 text = gg.TEXT_VERSION, 
                                 font = version_font_label,
                                 justify = "right")
        version_label.place(x = eff_version_x_px, 
                            y = eff_version_y_px, 
                            anchor = "sw") 
        
    ################################ Class init - end ################################
  
    ######################## Class internal functions - start ########################   
    def _generate_pages(self, institute, bibliometer_path):
        
        '''Permet la génération des pages après spécification du chemin 
        vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, 
        sinon redemande de renseigner un chemin.
        ''' 
        # 3rd party imports
        import tkinter as tk
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
            # Creating buttons pointing on classes listed in pages
            pages = (Page_Analysis,
                     Page_UpdateIFs,
                     Page_ConsolidateCorpus,
                     Page_ParseCorpus,                     
                    )

            # Création de mes deux containers
            container_button = tk.Frame(self, 
                                        height = gg.CONTAINER_BUTTON_HEIGHT_PX, 
                                        bg = 'red')
            container_button.pack(side = "top", 
                                  fill = "both", 
                                  expand = False)

            container_frame = tk.Frame(self)
            container_frame.pack(side="top", 
                                 fill="both", 
                                 expand=True)
            container_frame.grid_rowconfigure(0, 
                                              weight = 1)
            container_frame.grid_columnconfigure(0, 
                                                 weight = 1)

            self.frames = {}
            for page in pages:
                page_name = page.__name__
                frame = page(parent           = container_frame, 
                             controller       = self, 
                             container_button = container_button,
                             institute        = institute,
                             bibliometer_path = bibliometer_path)
                self.frames[page_name] = frame

                # put all of the pages in the same location;
                # the one on the top of the stacking order
                # will be the one that is visible.
                frame.grid(row = 0, 
                           column = 0, 
                           sticky = "nsew")
        
    def _show_frame(self, page_name):        
        '''Show a frame for the given page name'''        
        frame = self.frames[page_name]
        frame.tkraise()


class Page_ParseCorpus(tk.Frame):
    '''PAGE 1 'Analyse élémentaire des corpus'.
    '''             
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # 3rd party imports
        import tkinter as tk
        from tkinter import font as tkFont        

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_GUI.Useful_Functions as guf
        from BiblioMeter_GUI.Page_ParseCorpus import create_parsing_concat    
        
        
        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = guf.root_properties(controller)
        win_width_px  = sizes_tuple[0]
        win_height_px = sizes_tuple[1]    # unused here
        width_sf_px   = sizes_tuple[2] 
        height_sf_px  = sizes_tuple[3]    # unused here
        width_sf_mm   = sizes_tuple[4]
        height_sf_mm  = sizes_tuple[5]
        width_sf_min  = min(width_sf_mm, width_sf_px)
        
        # Setting page identifier
        page = 'first'
        
        # Setting specific texts 
        label_text = gg.PAGES_LABELS[page]
        page_title = label_text + " du " + institute
        page_name  = gg.PAGES_NAMES[page]  
        
        # Setting font size for page label and button
        eff_label_font_size  = guf.font_size(gg.REF_LABEL_FONT_SIZE, width_sf_min)
        eff_button_font_size = guf.font_size(gg.REF_BUTTON_FONT_SIZE, width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px   = guf.mm_to_px(gg.REF_LABEL_POS_Y_MM * height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
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
                           command = lambda: controller._show_frame(page_name))
        button.grid(row = 0, column = 0)


class Page_ConsolidateCorpus(tk.Frame):
    '''PAGE 2 'Consolidation annuelle des corpus'. 
    '''        
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        import tkinter as tk 
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_GUI.Useful_Functions as guf
        from BiblioMeter_GUI.Page_ConsolidateCorpus import create_consolidate_corpus
        
        # Internal functions
        def _launch_consolidate_corpus():
       
            # Getting years of available corpuses from files status       
            files_status = guf.existing_corpuses(bibliometer_path)    
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
            controller._show_frame(page_name)
        
        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = guf.root_properties(controller)
        win_width_px  = sizes_tuple[0]
        win_height_px = sizes_tuple[1]    # unused here
        width_sf_px   = sizes_tuple[2] 
        height_sf_px  = sizes_tuple[3]    # unused here
        width_sf_mm   = sizes_tuple[4]
        height_sf_mm  = sizes_tuple[5]
        width_sf_min  = min(width_sf_mm, width_sf_px)
        
        # Setting page identifier
        page = 'second'
                
        # Setting specific texts
        label_text = gg.PAGES_LABELS[page]
        page_title = label_text + " du " + institute
        page_name  = gg.PAGES_NAMES[page]  

        # Setting font size for page label and button
        eff_label_font_size  = guf.font_size(gg.REF_LABEL_FONT_SIZE, width_sf_min)
        eff_button_font_size = guf.font_size(gg.REF_BUTTON_FONT_SIZE, width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px = guf.mm_to_px(gg.REF_LABEL_POS_Y_MM * height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Getting years of available corpuses from files status       
        files_status = guf.existing_corpuses(bibliometer_path)    
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
        button.grid(row = 0, column = 1)

            
############################ ############################

class Page_UpdateIFs(tk.Frame):
    '''PAGE 3 'Mise à jour des IF'. 
    '''    
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # 3rd party imports
        import tkinter as tk 
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_GUI.Useful_Functions as guf   
        from BiblioMeter_GUI.Page_UpdateIFs import create_update_ifs
        
        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = guf.root_properties(controller)
        win_width_px  = sizes_tuple[0]
        win_height_px = sizes_tuple[1]    # unused here
        width_sf_px   = sizes_tuple[2] 
        height_sf_px  = sizes_tuple[3]    # unused here
        width_sf_mm   = sizes_tuple[4]
        height_sf_mm  = sizes_tuple[5]
        width_sf_min  = min(width_sf_mm, width_sf_px)
        
        # Setting page identifier
        page = 'third'
        
        # Setting specific texts 
        label_text = gg.PAGES_LABELS[page]
        page_title = label_text + " du " + institute
        page_name  = gg.PAGES_NAMES[page]  
        
        # Setting font size for page label and button
        eff_label_font_size  = guf.font_size(gg.REF_LABEL_FONT_SIZE, width_sf_min)
        eff_button_font_size = guf.font_size(gg.REF_BUTTON_FONT_SIZE, width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px = guf.mm_to_px(gg.REF_LABEL_POS_Y_MM * height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
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
                           command = lambda: controller._show_frame(page_name))
        button.grid(row = 0, column = 2)


class Page_Analysis(tk.Frame):
    '''PAGE 4 'Analyse des corpus'.
    '''
    def __init__(self, parent, controller, container_button, institute, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # 3rd party imports
        import tkinter as tk 
        from tkinter import font as tkFont

        # Local imports
        import BiblioMeter_GUI.GUI_Globals as gg
        import BiblioMeter_GUI.Useful_Functions as guf   
        from BiblioMeter_GUI.Page_Analysis import create_analysis

        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = guf.root_properties(controller)
        win_width_px  = sizes_tuple[0]
        win_height_px = sizes_tuple[1]    # unused here
        width_sf_px   = sizes_tuple[2] 
        height_sf_px  = sizes_tuple[3]    # unused here
        width_sf_mm   = sizes_tuple[4]
        height_sf_mm  = sizes_tuple[5]
        width_sf_min  = min(width_sf_mm, width_sf_px)
        
        # Setting page identifier
        page = 'fourth'
        
        # Setting specific texts 
        label_text = gg.PAGES_LABELS[page]
        page_title = label_text + " du " + institute
        page_name  = gg.PAGES_NAMES[page]  
        
        # Setting font size for page label and button
        eff_label_font_size  = guf.font_size(gg.REF_LABEL_FONT_SIZE, width_sf_min)
        eff_button_font_size = guf.font_size(gg.REF_BUTTON_FONT_SIZE, width_sf_min)
        
        # Setting y_position in px for page label
        eff_label_pos_y_px = guf.mm_to_px(gg.REF_LABEL_POS_Y_MM * height_sf_mm, gg.PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
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
                           command = lambda: controller._show_frame(page_name))
        button.grid(row = 0, column = 3)        