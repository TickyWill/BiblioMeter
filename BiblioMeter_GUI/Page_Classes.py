__all__ = ['app_main']


import tkinter as tk 

################################# PAGE de lancement #################################
 
class app_main(tk.Tk):
    
    ############################### Class init - start ###############################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        # Standard library imports
        from screeninfo import get_monitors
        
        # 3rd party imports
        import tkinter as tk
        from tkinter import font as tkFont
        from tkinter import messagebox
        
        # BiblioAnalysis_Utils package imports
        from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
        from BiblioAnalysis_Utils.BiblioGui import _str_size_mm

        # Local library imports
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.GUI_Globals import general_properties
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import FONT_NAME              
        from BiblioMeter_GUI.GUI_Globals import PPI 
        
        _ = get_monitors() # OBLIGATOIRE
        
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes,'-topmost',False)
        
        # Getting useful screen sizes and scale factors depending on displays properties
        self, sizes_tuple = general_properties(self)
        win_width_px  = sizes_tuple[0]
        win_height_px = sizes_tuple[1]
        width_sf_px   = sizes_tuple[2] 
        height_sf_px  = sizes_tuple[3]     # unused here
        width_sf_mm   = sizes_tuple[4]
        height_sf_mm  = sizes_tuple[5]
        width_sf_min  = min(width_sf_mm, width_sf_px) 
        
        ######################################## Title - start 
        # Local globals imports       
        from BiblioMeter_GUI.GUI_Globals import REF_PAGE_TITLE_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_PAGE_TITLE_POS_Y_MM
        from BiblioMeter_GUI.GUI_Globals import TEXT_TITLE      
        
        # Setting font size for page title and copyright
        ref_page_title_font_size = REF_PAGE_TITLE_FONT_SIZE      #30
        eff_page_title_font_size = font_size(ref_page_title_font_size, width_sf_min)     
       
        # Setting reference Y position in mm and effective Y position in pixels for page label 
        ref_page_title_pos_y_mm = REF_PAGE_TITLE_POS_Y_MM    #20 
        eff_page_title_pos_y_px = _mm_to_px(ref_page_title_pos_y_mm * height_sf_mm, PPI)
       
        # Setting x position in pixels for page title 
        mid_page_pos_x_px = win_width_px  * 0.5 
                
        page_title = tk.Label(self, 
                              text = TEXT_TITLE, 
                              font = (FONT_NAME, eff_page_title_font_size), 
                              justify = "center")
        page_title.place(x = mid_page_pos_x_px, 
                         y = eff_page_title_pos_y_px, 
                         anchor = "center")
        ######################################## Title - end        
        
        self.REP = list()
        
        ######################################## Gestion du dossier de travail - start
        # BiblioAnalysis_Utils package imports
        from BiblioAnalysis_Utils.BiblioGui import _str_size_mm
        
        # Local library imports
        from BiblioMeter_GUI.Useful_Functions import last_available_years
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import ADD_SPACE_MM
        from BiblioMeter_GUI.GUI_Globals import CORPUSES_NUMBER
        from BiblioMeter_GUI.GUI_Globals import REF_BMF_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_BMF_POS_X_MM
        from BiblioMeter_GUI.GUI_Globals import REF_BMF_POS_Y_MM    
        from BiblioMeter_GUI.GUI_Globals import REF_BUTTON_DX_MM
        from BiblioMeter_GUI.GUI_Globals import REF_BUTTON_DY_MM
        from BiblioMeter_GUI.GUI_Globals import REF_BUTTON_FONT_SIZE        
        from BiblioMeter_GUI.GUI_Globals import REF_CORPI_POS_X_MM
        from BiblioMeter_GUI.GUI_Globals import REF_CORPI_POS_Y_MM
        from BiblioMeter_GUI.GUI_Globals import REF_ENTRY_NB_CHAR
        from BiblioMeter_GUI.GUI_Globals import ROOT_PATH 
        from BiblioMeter_GUI.GUI_Globals import TEXT_BMF
        from BiblioMeter_GUI.GUI_Globals import TEXT_BMF_CHANGE
        from BiblioMeter_GUI.GUI_Globals import TEXT_BOUTON_CREATION_CORPUS
        from BiblioMeter_GUI.GUI_Globals import TEXT_CORPUSES         
        
        # Internal functions

        def _display_path(bmf_str):
            """Shortening bmf path for easy display""" 
            # Standard library imports
            from pathlib import Path
            
            p = Path(bmf_str)
            p_disp = ('/'.join(p.parts[0:2])) / Path("...") / ('/'.join(p.parts[-3:]))
            return p_disp
            
        def _update_corpi(bmf_str):
            # Standard library imports
            from pathlib import Path

            # 3rd party imports
            from tkinter import messagebox

            # Local library imports
            from BiblioMeter_GUI.Useful_Functions import last_available_years

            # Local globals imports
            from BiblioMeter_GUI.GUI_Globals import CORPUSES_NUMBER
            
            bmf_path = Path(bmf_str)

            try: 
                # Getting updated corpuses list
                corpuses_list = last_available_years(bmf_path, CORPUSES_NUMBER)

                # Setting bmf val3 value to corpuses list
                bmf_val3.set(str(corpuses_list))

            except FileNotFoundError:
                warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
                warning_text  = f"L'accès au dossier {bmf_path} est impossible."
                warning_text += f"\nChoisissez un autre dossier de travail."                       
                messagebox.showwarning(warning_title, warning_text)
                # Setting bmf val3 value to empty string
                bmf_val3.set("")
                

        def _get_file():
            # 3rd party imports
            import tkinter as tk
            from tkinter import filedialog

            # Getting new working directory
            dialog_title = "Choisir un nouveau dossier de travail"
            bmf_str = tk.filedialog.askdirectory(title = dialog_title)
            if bmf_str == '':
                warning_title = "!!! Attention !!!"
                warning_text = "Chemin non renseigné."
                return tk.messagebox.showwarning(warning_title, warning_text)  
            
            # Updating bmf 3 values using new working directory 
            bmf_val.set(bmf_str)
            bmf_val2.set(_display_path(bmf_str))             
            _update_corpi(bmf_str)
            
            
        def _create_corpus(bmf_str):
            # Standard library imports
            from pathlib import Path
            
            # 3rd party imports
            from tkinter import messagebox

            # Local library imports   
            from BiblioMeter_FUNCTS.BM_UsefulFuncts import create_archi
            from BiblioMeter_GUI.Useful_Functions import last_available_years
            
            # Local globals imports
            from BiblioMeter_GUI.GUI_Globals import CORPUSES_NUMBER
            
            bmf_path = Path(bmf_str)

            try: 
                # Setting new corpus year folder name
                corpuses_list    = last_available_years(bmf_path, CORPUSES_NUMBER)
                last_corpus_year = corpuses_list[-1] 
                new_corpus_year_folder = str(int(last_corpus_year) + 1)

                # Creating required folders for new corpus year
                message = create_archi(bmf_path, new_corpus_year_folder, verbose = False)
                print("\n",message)

                # Getting updated corpuses list
                corpuses_list = last_available_years(bmf_path, CORPUSES_NUMBER)
                
                # Setting bmf val3 value to corpuses list 
                bmf_val3.set(str(corpuses_list))
                
            except FileNotFoundError:
                warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
                warning_text  = f"L'accès au dossier {bmf_path} est impossible."
                warning_text += f"\nChoisissez un autre dossier de travail."                       
                messagebox.showwarning(warning_title, warning_text)
                # Setting bmf val3 value to empty string
                bmf_val3.set("")
                
        
        # Setting number-of-characters reference and effective value for entry width
        ref_entry_nb_char = REF_ENTRY_NB_CHAR             #100
        eff_bmf_width     = int(ref_entry_nb_char * width_sf_min)
        eff_list_width    = eff_bmf_width

        # Setting font size for bmf
        ref_bmf_font_size    = REF_BMF_FONT_SIZE          #15
        eff_bmf_font_size    = font_size(ref_bmf_font_size, width_sf_min)        
        ref_button_font_size = REF_BUTTON_FONT_SIZE       #12
        eff_button_font_size = font_size(ref_button_font_size, width_sf_min)

        # Setting reference Y position in mm and effective Y position in pixels for bmf 
        ref_bmf_pos_x_mm   = REF_BMF_POS_X_MM             #5
        eff_bmf_pos_x_px   = _mm_to_px(ref_bmf_pos_x_mm * height_sf_mm, PPI)
        ref_bmf_pos_y_mm   = REF_BMF_POS_Y_MM             #45  
        eff_bmf_pos_y_px   = _mm_to_px(ref_bmf_pos_y_mm * height_sf_mm, PPI)
        ref_corpi_pos_x_mm = REF_CORPI_POS_X_MM           #5       
        eff_corpi_pos_x_px = _mm_to_px(ref_corpi_pos_x_mm * height_sf_mm, PPI)       
        ref_corpi_pos_y_mm =  REF_CORPI_POS_Y_MM          #75
        eff_corpi_pos_y_px = _mm_to_px(ref_corpi_pos_y_mm * height_sf_mm, PPI)
        add_space_mm       = ADD_SPACE_MM                 #10

        # Setting reference relative X,Y positions in mm and effective relative 
        # X,Y positions in pixels for bmf change button
        ref_button_dx_mm = REF_BUTTON_DX_MM               #-147
        eff_button_dx_px = _mm_to_px(ref_button_dx_mm * width_sf_mm, PPI)
        ref_button_dy_mm = REF_BUTTON_DY_MM               #10
        eff_button_dy_px = _mm_to_px(ref_button_dy_mm * height_sf_mm, PPI)       

        # Setting corpi widgets
        bmf_font        = tkFont.Font(family = FONT_NAME, 
                                      size   = eff_bmf_font_size,
                                      weight = 'bold') 
        bmf_label1      = tk.Label(self, 
                                   text = TEXT_BMF,  
                                   font = bmf_font,)        
        bmf_label2      = tk.Label(self, 
                                   text = TEXT_CORPUSES,  
                                   font = bmf_font,)
        bmf_val         = tk.StringVar(self) 
        bmf_val2        = tk.StringVar(self)
        bmf_val3        = tk.StringVar(self)
        bmf_entree      = tk.Entry(self, textvariable = bmf_val)
        bmf_entree2     = tk.Entry(self, textvariable = bmf_val2, width = eff_bmf_width)
        bmf_entree3     = tk.Entry(self, textvariable = bmf_val3, width = eff_list_width)
        bmf_button_font = tkFont.Font(family = FONT_NAME,
                                      size   = eff_button_font_size)                
        bmf_button      = tk.Button(self, 
                                    text = TEXT_BMF_CHANGE, 
                                    font = bmf_button_font, 
                                    command = lambda: _get_file()) 
                       
        corpi_button      = tk.Button(self, 
                                      text = TEXT_BOUTON_CREATION_CORPUS, 
                                      font = bmf_button_font, 
                                      command = lambda: _create_corpus(bmf_val.get())) 

        # Setting bmf initiales values
        bmf_val.set(ROOT_PATH)
        bmf_val2.set((_display_path(ROOT_PATH)))

        # Placing bmf widgets
        bmf_label1.place(x = eff_bmf_pos_x_px,
                         y = eff_bmf_pos_y_px,)

        text_width_mm, _ = _str_size_mm(TEXT_BMF, 
                                        bmf_font, 
                                        PPI)
        eff_path_pos_x_px = _mm_to_px(text_width_mm + add_space_mm, PPI)                
        bmf_entree2.place(x = eff_path_pos_x_px ,
                          y = eff_bmf_pos_y_px,)

        bmf_button.place(x = eff_path_pos_x_px, 
                         y = eff_bmf_pos_y_px + eff_button_dy_px,) 
        
        # Setting corpi initiales values# Setting bmf initiales values
        try:
            init_corpuses_list = last_available_years(ROOT_PATH, CORPUSES_NUMBER)
            bmf_val3.set(str(init_corpuses_list))
        except FileNotFoundError:
            warning_title = "!!! ATTENTION : Dossier de travail inaccessible !!!"
            warning_text  = f"L'accès au dossier {ROOT_PATH} est impossible."
            warning_text += f"\nChoisissez un autre dossier de travail."                       
            messagebox.showwarning(warning_title, warning_text)
            # Setting bmf val3 value to empty string
            bm_val3.set("")              
        
        # Placing corpi widgets
        
        bmf_label2.place(x = eff_corpi_pos_x_px,
                         y = eff_corpi_pos_y_px,)

        text_width_mm, _ = _str_size_mm(TEXT_CORPUSES, 
                                        bmf_font, 
                                        PPI)
        eff_list_pos_x_px = _mm_to_px(text_width_mm + add_space_mm, PPI)                
        bmf_entree3.place(x = eff_list_pos_x_px ,
                          y = eff_corpi_pos_y_px,)
                      
        corpi_button.place(x = eff_list_pos_x_px, 
                           y = eff_corpi_pos_y_px + eff_button_dy_px,)             

        
        ######################################## Bouton lancement - start
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import REF_LAUNCH_FONT_SIZE        
        from BiblioMeter_GUI.GUI_Globals import TEXT_BOUTON_LANCEMENT
        
        # Setting font size for launch button
        ref_launch_font_size = REF_LAUNCH_FONT_SIZE          #25
        eff_launch_font_size = font_size(ref_launch_font_size, width_sf_min) 
        
        # Setting x and y position in pixels for launch button
        launch_but_pos_x_px = win_width_px  * 0.5
        launch_but_pos_y_px = win_height_px * 0.7         
        
        # Setting launch button
        launch_font = tkFont.Font(family = FONT_NAME,
                                  size = eff_launch_font_size,
                                  weight = 'bold')
        launch_button = tk.Button(self,
                                  text = TEXT_BOUTON_LANCEMENT,
                                  font = launch_font,
                                  command = lambda: self._generate_pages(bmf_val.get()))    
        launch_button.place(x = launch_but_pos_x_px,
                            y = launch_but_pos_y_px,
                            anchor = "s") 

        
        ######################################## Auteurs et versions - start
        # Local globals imports      
        from BiblioMeter_GUI.GUI_Globals import REF_COPYRIGHT_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_COPYRIGHT_X_MM
        from BiblioMeter_GUI.GUI_Globals import REF_COPYRIGHT_Y_MM
        from BiblioMeter_GUI.GUI_Globals import REF_VERSION_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_VERSION_X_MM
        from BiblioMeter_GUI.GUI_Globals import TEXT_COPYRIGHT
        from BiblioMeter_GUI.GUI_Globals import TEXT_VERSION

        # Setting font size for copyright
        ref_copyright_font_size = 12 # REF_COPYRIGHT_FONT_SIZE       #10
        eff_copyright_font_size = font_size(ref_copyright_font_size, width_sf_min)
        
        # Setting X and Y positions reference in mm for copyright
        ref_copyright_x_mm = REF_COPYRIGHT_X_MM              #5
        eff_copyright_x_px = _mm_to_px(ref_copyright_x_mm * width_sf_mm, PPI)
        ref_copyright_y_mm = REF_COPYRIGHT_Y_MM              #170
        eff_copyright_y_px = _mm_to_px(ref_copyright_y_mm * height_sf_mm, PPI)
        
        
        Auteurs_font_label = tkFont.Font(family = FONT_NAME, 
                                         size = eff_copyright_font_size,)
        Auteurs_label = tk.Label(self, 
                                 text = TEXT_COPYRIGHT, 
                                 font = Auteurs_font_label,
                                 justify = "left")
        Auteurs_label.place(x = eff_copyright_x_px, 
                            y = eff_copyright_y_px, 
                            anchor = "sw")
        
        # Setting font size for copyright
        ref_version_font_size = REF_VERSION_FONT_SIZE         #12
        eff_version_font_size = font_size(ref_version_font_size, width_sf_min)
        
        # Setting X and Y positions reference in mm for version
        ref_version_x_mm = REF_VERSION_X_MM                   #185
        eff_version_x_px = _mm_to_px(ref_version_x_mm * width_sf_mm, PPI)
        ref_version_y_mm = REF_COPYRIGHT_Y_MM                 #170
        eff_version_y_px = _mm_to_px(ref_version_y_mm * height_sf_mm, PPI)
        
        
        version_font_label = tkFont.Font(family = FONT_NAME, 
                                         size = eff_version_font_size,
                                         weight = 'bold')

        version_label = tk.Label(self, 
                                 text = TEXT_VERSION, 
                                 font = version_font_label,
                                 justify = "right")
        version_label.place(x = eff_version_x_px, 
                            y = eff_version_y_px, 
                            anchor = "sw")       
    
    ################################ Class init - end ################################
    
    ######################## Class internal functions - start ########################   
    def _generate_pages(self, bibliometer_path):
        
        '''Permet la génération des pages après spécification du chemin 
        vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, 
        sinon redemande de renseigner un chemin.
        '''       
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import CONTAINER_BUTTON_HEIGHT_PX
        
        # Setting container button height in pixels
        container_button_height_px  = CONTAINER_BUTTON_HEIGHT_PX    #50
            
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
                                        height = container_button_height_px, 
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
                frame = page(parent = container_frame, 
                             controller = self, 
                             container_button = container_button, 
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

        
############################ PAGE 1 'Analyse élémentaire des corpus' ############################

class Page_ParseCorpus(tk.Frame): 
    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        from tkinter import font as tkFont
        
        # BiblioAnalysis_Utils package imports
        from BiblioAnalysis_Utils.BiblioGui import _mm_to_px

        # Local library imports
        from BiblioMeter_GUI.GUI_Globals import root_properties
        from BiblioMeter_GUI.Page_ParseCorpus import create_parsing_concat        
        from BiblioMeter_GUI.Useful_Functions import font_size
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import FONT_NAME
        from BiblioMeter_GUI.GUI_Globals import PAGES_LABELS
        from BiblioMeter_GUI.GUI_Globals import PAGES_NAMES
        from BiblioMeter_GUI.GUI_Globals import PPI
        from BiblioMeter_GUI.GUI_Globals import REF_BUTTON_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_POS_Y_MM
        
        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = root_properties(controller)
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
        label_text = PAGES_LABELS[page]
        page_name  = PAGES_NAMES[page]  
        
        # Setting font size for page label and button
        ref_label_font_size  = REF_LABEL_FONT_SIZE   #25
        eff_label_font_size  = font_size(ref_label_font_size, width_sf_min)
        ref_button_font_size = REF_BUTTON_FONT_SIZE #10
        eff_button_font_size = font_size(ref_button_font_size, width_sf_min)
        
        # Setting y_position in px for page label
        ref_label_pos_y_mm   = REF_LABEL_POS_Y_MM    #15
        eff_label_pos_y_px   = _mm_to_px(ref_label_pos_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Creation of the class object Page 1
        create_parsing_concat(self, bibliometer_path, controller)
        
        label_font = tkFont.Font(family = FONT_NAME, 
                                 size = eff_label_font_size)
        label = tk.Label(self, 
                         text = label_text, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px,
                    anchor = "center")

        
        button_font = tkFont.Font(family = FONT_NAME, 
                                  size = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font, 
                           command = lambda: controller._show_frame(page_name))
        button.grid(row = 0, column = 0)

        
############################ PAGE 2 'Consolidation annuelle des corpus' ############################

class Page_ConsolidateCorpus(tk.Frame):
    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        from tkinter import font as tkFont
        
        # BiblioAnalysis_Utils package imports
        from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
        
        # Local library imports
        from BiblioMeter_GUI.GUI_Globals import root_properties
        from BiblioMeter_GUI.Page_ConsolidateCorpus import create_consolidate_corpus
        from BiblioMeter_GUI.Useful_Functions import existing_corpuses
        from BiblioMeter_GUI.Useful_Functions import font_size
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import FONT_NAME
        from BiblioMeter_GUI.GUI_Globals import PAGES_LABELS
        from BiblioMeter_GUI.GUI_Globals import PAGES_NAMES
        from BiblioMeter_GUI.GUI_Globals import PPI 
        from BiblioMeter_GUI.GUI_Globals import REF_BUTTON_FONT_SIZE        
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_POS_Y_MM
        
        # Internal functions
        def _launch_consolidate_corpus():
       
            # Getting years of available corpuses from files status       
            files_status = existing_corpuses(bibliometer_path)    
            corpus_years_list = files_status[0]
            Liste_2 = corpus_years_list
            
            if self.Liste_1 != Liste_2:                
                self.Liste_1 = Liste_2                
                create_consolidate_corpus(self, bibliometer_path, controller)                
                label_font = tkFont.Font(family = FONT_NAME, 
                                         size = eff_label_font_size)
                label = tk.Label(self, 
                                 text = label_text, 
                                 font = label_font)
                label.place(x = mid_page_pos_x_px, 
                            y = eff_label_pos_y_px, 
                            anchor = "center")                
                button_font = tkFont.Font(family = FONT_NAME, 
                                          size = eff_button_font_size)
                button = tk.Button(container_button, 
                                   text = label_text, 
                                   font = button_font, 
                                   command = lambda: _launch_consolidate_corpus())
                button.grid(row = 0, column = 1)        
            controller._show_frame(page_name)
        
        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = root_properties(controller)
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
        label_text = PAGES_LABELS[page]
        page_name  = PAGES_NAMES[page]  

        # Setting font size for page label and button
        ref_label_font_size  = REF_LABEL_FONT_SIZE   #25
        eff_label_font_size  = font_size(ref_label_font_size, width_sf_min)
        ref_button_font_size = REF_BUTTON_FONT_SIZE  #10
        eff_button_font_size = font_size(ref_button_font_size, width_sf_min)
        
        # Setting y_position in px for page label
        ref_label_pos_y_mm = REF_LABEL_POS_Y_MM      #15
        eff_label_pos_y_px = _mm_to_px(ref_label_pos_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Getting years of available corpuses from files status       
        files_status = existing_corpuses(bibliometer_path)    
        corpus_years_list = files_status[0]
        self.Liste_1 = corpus_years_list        
        
        # Creating the class object Page 2
        create_consolidate_corpus(self, bibliometer_path, controller)        
        label_font = tkFont.Font(family = FONT_NAME, 
                                 size = eff_label_font_size)
        label = tk.Label(self, 
                         text = label_text, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px, 
                    anchor = "center")        
        button_font = tkFont.Font(family = FONT_NAME, 
                                  size = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font, 
                           command = lambda: _launch_consolidate_corpus())
        button.grid(row = 0, column = 1)

            
############################ PAGE 3 'Mise à jour des IF' ############################

class Page_UpdateIFs(tk.Frame):
    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        from tkinter import font as tkFont

        # BiblioAnalysis_Utils package imports
        from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
        
        # Local library imports
        from BiblioMeter_GUI.GUI_Globals import root_properties
        from BiblioMeter_GUI.Page_UpdateIFs import create_update_ifs        
        from BiblioMeter_GUI.Useful_Functions import font_size
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import FONT_NAME
        from BiblioMeter_GUI.GUI_Globals import PAGES_LABELS
        from BiblioMeter_GUI.GUI_Globals import PAGES_NAMES
        from BiblioMeter_GUI.GUI_Globals import PPI 
        from BiblioMeter_GUI.GUI_Globals import REF_BUTTON_FONT_SIZE        
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_POS_Y_MM

        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = root_properties(controller)
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
        label_text = PAGES_LABELS[page]
        page_name  = PAGES_NAMES[page]  
        
        # Setting font size for page label and button
        ref_label_font_size  = REF_LABEL_FONT_SIZE   #25
        eff_label_font_size  = font_size(ref_label_font_size, width_sf_min)
        ref_button_font_size = REF_BUTTON_FONT_SIZE  #10
        eff_button_font_size = font_size(ref_button_font_size, width_sf_min)
        
        # Setting y_position in px for page label
        ref_label_pos_y_mm = REF_LABEL_POS_Y_MM     #15
        eff_label_pos_y_px = _mm_to_px(ref_label_pos_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Creation of the class object Page 3
        create_update_ifs(self, bibliometer_path, controller)
        label_font = tkFont.Font(family = FONT_NAME, 
                                 size = eff_label_font_size)
        label = tk.Label(self, 
                         text = label_text, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px, 
                    anchor = "center")        
        button_font = tkFont.Font(family = FONT_NAME, 
                                  size = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font, 
                           command = lambda: controller._show_frame(page_name))
        button.grid(row = 0, column = 2)
        
        
############################ PAGE 4 'Analyse des corpus' ############################

class Page_Analysis(tk.Frame):
    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        from tkinter import font as tkFont

        # BiblioAnalysis_Utils package imports
        from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
        
        # Local library imports
        from BiblioMeter_GUI.GUI_Globals import root_properties
        from BiblioMeter_GUI.Page_Analysis import create_analysis        
        from BiblioMeter_GUI.Useful_Functions import font_size
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import FONT_NAME
        from BiblioMeter_GUI.GUI_Globals import PAGES_LABELS
        from BiblioMeter_GUI.GUI_Globals import PAGES_NAMES
        from BiblioMeter_GUI.GUI_Globals import PPI 
        from BiblioMeter_GUI.GUI_Globals import REF_BUTTON_FONT_SIZE        
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_FONT_SIZE
        from BiblioMeter_GUI.GUI_Globals import REF_LABEL_POS_Y_MM

        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = root_properties(controller)
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
        label_text = PAGES_LABELS[page]
        page_name  = PAGES_NAMES[page]  
        
        # Setting font size for page label and button
        ref_label_font_size  = REF_LABEL_FONT_SIZE   #25
        eff_label_font_size  = font_size(ref_label_font_size, width_sf_min)
        ref_button_font_size = REF_BUTTON_FONT_SIZE  #10
        eff_button_font_size = font_size(ref_button_font_size, width_sf_min)
        
        # Setting y_position in px for page label
        ref_label_pos_y_mm = REF_LABEL_POS_Y_MM     #15
        eff_label_pos_y_px = _mm_to_px(ref_label_pos_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Creation of the class object Page 4
        create_analysis(self, bibliometer_path, controller)
        label_font = tkFont.Font(family = FONT_NAME, 
                                 size = eff_label_font_size)
        label = tk.Label(self, 
                         text = label_text, 
                         font = label_font)
        label.place(x = mid_page_pos_x_px, 
                    y = eff_label_pos_y_px, 
                    anchor = "center")        
        button_font = tkFont.Font(family = FONT_NAME, 
                                  size = eff_button_font_size)
        button = tk.Button(container_button, 
                           text = label_text, 
                           font = button_font, 
                           command = lambda: controller._show_frame(page_name))
        button.grid(row = 0, column = 3)        