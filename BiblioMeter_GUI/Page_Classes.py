__all__ = ['App_Test']

import tkinter as tk

class App_Test(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        # Standard library imports
        import os
        from pathlib import Path
        from screeninfo import get_monitors
        
        # 3rd library imports
        from datetime import date
        import pandas as pd
        import tkinter as tk
        from tkinter import font as tkFont
        from tkinter import messagebox
        
        # Local library imports
        from BiblioMeter_GUI.Coordinates import general_properties
        from BiblioMeter_GUI.Useful_Classes import LabelEntry
        
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        from BiblioMeter_GUI.Useful_Functions import str_size_mm
        
        from BiblioMeter_GUI.Coordinates import TEXT_BOUTON_LANCEMENT
        from BiblioMeter_GUI.Coordinates import TEXT_LE_BMF
        from BiblioMeter_GUI.Coordinates import TEXT_TITLE
        from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
        from BiblioMeter_GUI.Globals_GUI import PPI
        
        a = get_monitors() # OBLIGATOIRE
        
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes,'-topmost',False)
        
        self, win_width, win_height, SFW, SFH, SFWP, SFHP = general_properties(self)
        
        # TITRE DE LA PAGE
        Page_Title = tk.Label(self, 
                              text = TEXT_TITLE, 
                              font = ("Helvetica", font_size(30, min(SFW, SFWP))), 
                              justify = "center")
        Page_Title.place(x = (win_width/2), y = (mm_to_px(20, PPI))*SFH, anchor = "center")
        
        self.REP = list()
        
        LE_font_label = tkFont.Font(family = "Helvetica", size = font_size(15, min(SFW, SFWP)))
        LE_font_button = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        LE_BMF = LabelEntry(self, 
                            text_label = TEXT_LE_BMF, 
                            font_label = LE_font_label, 
                            font_button = LE_font_button, 
                            width = int(80*min(SFW, SFWP))) # Ici width est en nombre de caractères
        LE_BMF.set(ROOT_PATH)
        LE_BMF.set2(ROOT_PATH)
        LE_BMF.place(x = (mm_to_px(str_size_mm(TEXT_LE_BMF, LE_font_label, PPI)[0] + 5, PPI)), 
                     y = (mm_to_px(45, PPI))*SFH,  
                     align = True)
        
        Lancement_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
        Bouton_Lancement = tk.Button(self, 
                                     text = TEXT_BOUTON_LANCEMENT, 
                                     font = Lancement_font, 
                                     command = lambda: self._generate_pages(LE_BMF.get()))
        Bouton_Lancement.place(x = (win_width/2), y = (win_height/2) + 20*SFH, anchor = "s")
                
    def _generate_pages(self, bibliometer_path):
        
        """
        Permet la génération des pages après spécification du chemin vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, sinon redemande de renseigner un chemin.
        """
            
        if bibliometer_path == '':
            messagebox.showwarning("Attention","Chemin non renseigné, l'application ne peut pas être lancée. \nVeuillez le faire.")

        else:
            # Bouton création des autres pages
            Pages = (Page_ParsingInstitution,
                     Page_MultiAnnuelle,
                     Page_ParsingConcat)

            # Création de mes deux containers
            container_button = tk.Frame(self, height = 50, bg = 'red')
            container_button.pack(side = "top", fill = "both", expand = False)

            container_frame = tk.Frame(self)
            container_frame.pack(side="top", fill="both", expand=True)
            container_frame.grid_rowconfigure(0, weight = 1)
            container_frame.grid_columnconfigure(0, weight = 1)

            self.frames = {}
            for F in Pages:
                page_name = F.__name__
                frame = F(parent = container_frame, controller = self, container_button = container_button, bibliometer_path = bibliometer_path)
                self.frames[page_name] = frame

                # put all of the pages in the same location;
                # the one on the top of the stacking order
                # will be the one that is visible.
                frame.grid(row = 0, column = 0, sticky = "nsew")
        
    def _show_frame(self, page_name):
        
        '''Show a frame for the given page name'''
        
        frame = self.frames[page_name]
        frame.tkraise()

####################################################################### PREMIERE PAGE #######################################################################

class Page_ParsingConcat(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # Standard library imports
        from pathlib import Path
        
        # 3rd library imports
        from tkinter import font as tkFont

        # Local library imports
        from BiblioMeter_GUI.Coordinates import root_properties
        from BiblioMeter_GUI.Page_ParsingConcat import create_ParsingConcat
        
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        
        from BiblioMeter_GUI.Globals_GUI import PPI
        
        win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(controller)
        
        # Creation of the class object PageOne
        create_ParsingConcat(self, bibliometer_path, controller)
        
        label_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
        label = tk.Label(self, 
                         text="Analyse élémentaire des corpus", 
                         font = label_font)
        label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*SFH, anchor = "center")
        
        button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        button = tk.Button(container_button, 
                           text = "Analyse élémentaire des corpus", 
                           font = button_font, 
                           command = lambda: controller._show_frame("Page_ParsingConcat"))
        button.grid(row = 0, column = 0)
        
####################################################################### DEUXIEME PAGE #######################################################################
class Page_ParsingInstitution(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # 3rd library imports
        from tkinter import font as tkFont

        # Local library imports
        from BiblioMeter_GUI.Coordinates import root_properties
        from BiblioMeter_GUI.Page_ParsingInstitution import create_ParsingInstitution
        
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        
        from BiblioMeter_GUI.Globals_GUI import PPI
    
        from BiblioMeter_GUI.Useful_Functions import existing_corpuses
        
        win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(controller)
        
        # Garder en mémoire la liste des années
        
        ### On récupère la présence ou non des fichiers #################################        
        results = existing_corpuses(bibliometer_path)

        self.Liste_1 = results[0]
        #################################################################################
        
        
        # Creation of the class object PageTwo
        create_ParsingInstitution(self, bibliometer_path, controller)
        
        label_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
        label = tk.Label(self, 
                         text="Consolidation annuelle des corpus", 
                         font = label_font)
        label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*SFH, anchor = "center")
        
        button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        button = tk.Button(container_button, 
                           text = "Consolidation annuelle des corpus", 
                           font = button_font, 
                           command = lambda: _launch_ParsingInstitution())
        button.grid(row = 0, column = 1)
        
        def _launch_ParsingInstitution():
            
            ### On récupère la présence ou non des fichiers #################################        
            results = existing_corpuses(bibliometer_path)

            Liste_2 = results[0]
            #################################################################################
            
            if self.Liste_1 != Liste_2:
                
                self.Liste_1 = Liste_2
                
                create_ParsingInstitution(self, bibliometer_path, controller)
                
                label_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
                label = tk.Label(self, 
                                 text="Consolidation annuelle des corpus", 
                                 font = label_font)
                label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*SFH, anchor = "center")

                button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
                button = tk.Button(container_button, 
                                   text = "Consolidation annuelle des corpus", 
                                   font = button_font, 
                                   command = lambda: _launch_ParsingInstitution())
                button.grid(row = 0, column = 1)
            
            controller._show_frame("Page_ParsingInstitution")

####################################################################### TROISIEME PAGE #######################################################################
class Page_MultiAnnuelle(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # 3rd library imports
        from tkinter import font as tkFont

        # Local library imports
        from BiblioMeter_GUI.Coordinates import root_properties
        from BiblioMeter_GUI.Page_MultiAnnuelle import create_MultiAnnuelle
        
        from BiblioMeter_GUI.Useful_Functions import font_size
        from BiblioMeter_GUI.Useful_Functions import mm_to_px
        
        from BiblioMeter_GUI.Globals_GUI import PPI
        
        win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(controller)
        
        # Creation of the class object PageFour
        create_MultiAnnuelle(self, bibliometer_path, controller)

        label_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
        label = tk.Label(self, 
                         text="Mise à jour des IF", 
                         font = label_font)
        label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*SFH, anchor = "center")
        
        button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        button = tk.Button(container_button, 
                           text = "Mise à jour des IF", 
                           font = button_font, 
                           command = lambda: controller._show_frame("Page_MultiAnnuelle"))
        button.grid(row = 0, column = 3)