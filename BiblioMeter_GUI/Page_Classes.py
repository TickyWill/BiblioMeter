__all__ = ['App_Test']

# To Do: Check the classes arg based on tkinter
# Pourquoi la fonction 'Page_ParsingInstitution' est structurée comme elle est avec répétition des même instructions. 
# Je n'ai pas osé modifier du fait de la programmation orientée objet que je ne maîtrise pas. 

import tkinter as tk

class App_Test(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        # Standard library imports
        from screeninfo import get_monitors
        
        # 3rd party imports
        import tkinter as tk
        from tkinter import font as tkFont
        from tkinter import messagebox
        
        # Local imports
        from BiblioMeter_GUI.Coordinates import general_properties
        
        from BiblioMeter_GUI.Useful_Classes import LabelEntry
        
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        from BiblioMeter_GUI.Useful_Functions import str_size_mm
        
        from BiblioMeter_GUI.Coordinates import FONT_NAME
        from BiblioMeter_GUI.Coordinates import REF_COPYRIGHT_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_COPYRIGHT_X_MM
        from BiblioMeter_GUI.Coordinates import REF_COPYRIGHT_Y_MM
        from BiblioMeter_GUI.Coordinates import REF_ENTRY_NB_CHAR        
        from BiblioMeter_GUI.Coordinates import REF_LAUNCH_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_LE_BMF_POS_Y_MM
        from BiblioMeter_GUI.Coordinates import REF_LE_BUTTON_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_LE_LABEL_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_PAGE_TITLE_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_PAGE_TITLE_POS_Y_MM
        from BiblioMeter_GUI.Coordinates import TEXT_BOUTON_LANCEMENT
        from BiblioMeter_GUI.Coordinates import TEXT_COPYRIGHT
        from BiblioMeter_GUI.Coordinates import TEXT_LE_BMF
        from BiblioMeter_GUI.Coordinates import TEXT_TITLE
        
        from BiblioMeter_GUI.Globals_GUI import PPI
        from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
                
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
        
        # Setting number-of-characters reference for width in LabelEntry call
        ref_entry_nb_char = REF_ENTRY_NB_CHAR                #80
        
        # Setting font size for pages label, button and copyright
        ref_page_title_font_size = REF_PAGE_TITLE_FONT_SIZE      #30
        eff_page_title_font_size = font_size(ref_page_title_font_size, width_sf_min)
        ref_launch_font_size     = REF_LAUNCH_FONT_SIZE          #25
        eff_launch_font_size     = font_size(ref_launch_font_size, width_sf_min)
        ref_le_label_font_size   = REF_LE_LABEL_FONT_SIZE        #15
        eff_le_label_font_size   = font_size(ref_le_label_font_size, width_sf_min)
        ref_le_button_font_size  = REF_LE_BUTTON_FONT_SIZE       #10
        eff_le_button_font_size  = font_size(ref_le_button_font_size, width_sf_min)       
        ref_copyright_font_size  = REF_COPYRIGHT_FONT_SIZE       #10
        eff_copyright_font_size  = font_size(ref_copyright_font_size, width_sf_min)
        
        # Setting Y position reference in mm for page label
        ref_page_title_pos_y_mm = REF_PAGE_TITLE_POS_Y_MM    #20 
        eff_page_title_pos_y_px = mm_to_px(ref_page_title_pos_y_mm * height_sf_mm, PPI)
        
        # Setting Y position reference in mm for le_bmf 
        ref_le_bmf_pos_y_mm = REF_LE_BMF_POS_Y_MM            #45
        eff_le_bmf_pos_y_px = mm_to_px(ref_le_bmf_pos_y_mm * height_sf_mm, PPI)
        
        # Setting X and Y positions reference in mm for copyright
        ref_copyright_x_mm = REF_COPYRIGHT_X_MM              #5
        eff_copyright_x_px = mm_to_px(ref_copyright_x_mm * width_sf_mm, PPI)
        ref_copyright_y_mm = REF_COPYRIGHT_Y_MM              #170
        eff_copyright_y_px = mm_to_px(ref_copyright_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        mid_page_pos_y_px = win_height_px / 2
        
        # Main page
        page_title = tk.Label(self, 
                              text = TEXT_TITLE, 
                              font = (FONT_NAME, eff_page_title_font_size), 
                              justify = "center")
        page_title.place(x = mid_page_pos_x_px, 
                         y = eff_page_title_pos_y_px, 
                         anchor = "center")
        
        self.REP = list()
        
        le_label_font = tkFont.Font(family = FONT_NAME, 
                                    size = eff_le_label_font_size)
        le_button_font = tkFont.Font(family = FONT_NAME, 
                                     size = eff_le_button_font_size)
        # !  width en nombre de caractères
        le_bmf = LabelEntry(self, 
                            text_label = TEXT_LE_BMF, 
                            font_label = le_label_font, 
                            font_button = le_button_font, 
                            width = int(ref_entry_nb_char * width_sf_min)) 
        le_bmf.set(ROOT_PATH)
        le_bmf.set2(ROOT_PATH)
        text_width_mm, _ = str_size_mm(TEXT_LE_BMF, 
                                       le_label_font, 
                                       PPI)
        eff_le_bmf_pos_x_px = mm_to_px(text_width_mm + 5, PPI)
        #! check the value 5 added in the original code
        le_bmf.place(x = eff_le_bmf_pos_x_px,
                     y = eff_le_bmf_pos_y_px,  
                     align = True)
        
        launch_font = tkFont.Font(family = FONT_NAME,
                                  size = eff_launch_font_size)
        launch_button = tk.Button(self,
                                  text = TEXT_BOUTON_LANCEMENT,
                                  font = launch_font,
                                  command = lambda: self._generate_pages(le_bmf.get()))

        launch_button.place(x = mid_page_pos_x_px,
                            y = mid_page_pos_y_px,
                            anchor = "s")        
        
        # Auteurs et versions
        Auteurs_font_label = tkFont.Font(family = FONT_NAME, 
                                         size = eff_copyright_font_size)
        Auteurs_label = tk.Label(self, 
                                 text = TEXT_COPYRIGHT, 
                                 font = Auteurs_font_label,
                                 justify = "left")
        Auteurs_label.place(x = eff_copyright_x_px, 
                            y = eff_copyright_y_px, 
                            anchor = "sw")
                
    def _generate_pages(self, bibliometer_path):
        
        '''Permet la génération des pages après spécification du chemin 
        vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, 
        sinon redemande de renseigner un chemin.
        '''       
        
        from BiblioMeter_GUI.Coordinates import CONTAINER_BUTTON_HEIGHT_PX
        
        # Setting container button height in pixels
        container_button_height_px  = CONTAINER_BUTTON_HEIGHT_PX    #50
            
        if bibliometer_path == '':
            warning_title = "!!! Attention !!!"
            warning_text =  """Chemin non renseigné.""" 
            warning_text += """\nL'application ne peut pas être lancée."""
            warning_text += """\nVeuillez le définir."""
            messagebox.showwarning(warning_title, warning_text)

        else:
            # Creating buttons pointing on classes listed in pages
            pages = (Page_MultiAnnuelle,
                     Page_ParsingInstitution,
                     Page_ParsingConcat)

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

class Page_ParsingConcat(tk.Frame): 
    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        from tkinter import font as tkFont

        # Local imports
        from BiblioMeter_GUI.Coordinates import root_properties
        from BiblioMeter_GUI.Page_ParsingConcat import create_ParsingConcat        
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        
        from BiblioMeter_GUI.Coordinates import FONT_NAME
        from BiblioMeter_GUI.Coordinates import REF_LABEL_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_BUTTON_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_LABEL_POS_Y_MM
        from BiblioMeter_GUI.Globals_GUI import PAGES_LABELS
        from BiblioMeter_GUI.Globals_GUI import PAGES_NAMES
        from BiblioMeter_GUI.Globals_GUI import PPI
        
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
        eff_label_pos_y_px   = mm_to_px(ref_label_pos_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Creation of the class object PageOne
        create_ParsingConcat(self, bibliometer_path, controller)
        
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

class Page_ParsingInstitution(tk.Frame):
    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        from tkinter import font as tkFont

        # Local imports
        from BiblioMeter_GUI.Coordinates import root_properties
        from BiblioMeter_GUI.Page_ParsingInstitution import create_ParsingInstitution
        from BiblioMeter_GUI.Useful_Functions import existing_corpuses
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        
        from BiblioMeter_GUI.Coordinates import FONT_NAME
        from BiblioMeter_GUI.Coordinates import REF_LABEL_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_BUTTON_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_LABEL_POS_Y_MM
        from BiblioMeter_GUI.Globals_GUI import PAGES_LABELS
        from BiblioMeter_GUI.Globals_GUI import PAGES_NAMES
        from BiblioMeter_GUI.Globals_GUI import PPI
        
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
        eff_label_pos_y_px = mm_to_px(ref_label_pos_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Getting years of available corpuses from files status       
        files_status = existing_corpuses(bibliometer_path)    
        corpus_years_list = files_status[0]
        self.Liste_1 = corpus_years_list        
        
        # Creating the class object PageTwo
        create_ParsingInstitution(self, bibliometer_path, controller)
        
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
                           command = lambda: _launch_ParsingInstitution())
        button.grid(row = 0, column = 1)
        
        def _launch_ParsingInstitution():
       
            # Getting years of available corpuses from files status       
            files_status = existing_corpuses(bibliometer_path)    
            corpus_years_list = files_status[0]
            Liste_2 = corpus_years_list
            
            if self.Liste_1 != Liste_2:
                
                self.Liste_1 = Liste_2
                
                create_ParsingInstitution(self, bibliometer_path, controller)
                
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
                                   command = lambda: _launch_ParsingInstitution())
                button.grid(row = 0, column = 1)
            
            controller._show_frame(page_name)

            
############################ PAGE 3 'Mise à jour des IF' ############################

class Page_MultiAnnuelle(tk.Frame):
    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # 3rd party imports
        from tkinter import font as tkFont

        # Local imports
        from BiblioMeter_GUI.Coordinates import root_properties
        from BiblioMeter_GUI.Page_MultiAnnuelle import create_MultiAnnuelle        
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        
        from BiblioMeter_GUI.Coordinates import FONT_NAME
        from BiblioMeter_GUI.Coordinates import REF_LABEL_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_BUTTON_FONT_SIZE
        from BiblioMeter_GUI.Coordinates import REF_LABEL_POS_Y_MM
        from BiblioMeter_GUI.Globals_GUI import PAGES_LABELS
        from BiblioMeter_GUI.Globals_GUI import PAGES_NAMES
        from BiblioMeter_GUI.Globals_GUI import PPI

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
        eff_label_pos_y_px = mm_to_px(ref_label_pos_y_mm * height_sf_mm, PPI)
        
        # Setting x position in pixels for page label 
        mid_page_pos_x_px = win_width_px / 2
        
        # Creation of the class object PageFour
        create_MultiAnnuelle(self, bibliometer_path, controller)

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