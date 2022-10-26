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
        from BiblioMeter_GUI.Globals_GUI import GUI_DISP
        from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
        from BiblioMeter_GUI.Globals_GUI import PPI
        
        get_monitors() # OBLIGATOIRE
        self, win_width, win_height, SFW, SFH, SFWP, SFHP = general_properties(self)
        
        # TITRE DE LA PAGE
        Page_Title = tk.Label(self, 
                              text = TEXT_TITLE, 
                              font = ("Helvetica", font_size(30, min(SFW, SFWP))), 
                              justify = "center")
        Page_Title.place(x = (win_width/2), y = (mm_to_px(20, PPI))*min(SFH, SFHP), anchor = "center")
        
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
                     y = (mm_to_px(45, PPI))*min(SFH, SFHP),  
                     align = True)
        
        Lancement_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
        Bouton_Lancement = tk.Button(self, 
                                     text = TEXT_BOUTON_LANCEMENT, 
                                     font = Lancement_font, 
                                     command = lambda: self._generate_pages(LE_BMF.get()))
        Bouton_Lancement.place(x = (win_width/2), y = (win_height/2) + 20*min(SFH, SFHP), anchor = "s")
        
        ## TO DO : METTRE CHEMIN EN GLOBAL
        #listing_alias = STOCKAGE_ARBORESCENCE['effectif'][0]
        #maj_alias = STOCKAGE_ARBORESCENCE['effectif'][3]
        
        #path = Path(ROOT_PATH) / Path(listing_alias) / Path(maj_alias)
        ##path = "S:/130-LITEN/130.1-Direction/130.1.2-Direction Scientifique/130.1.2.1-Dossiers en cours/110-Alternants/2021-22 Ludovic Desmeuzes/BiblioMeter_Files/Listing RH/MAJ.txt"
        #f = open(path,'r')
        #last_MAJ = f.readline()
        #f.close()

        ## Mise à jour du fichier RH
        #tmp = tk.Label(self, text = f"Date de la dernière mise à jour des effectifs Liten : {last_MAJ}")
        #tmp.place(anchor = 'w', relx = 0.15, rely = 0.7)
        
        #tmp = tk.Label(self, text = f"Mettre à jour le fichier ? (COCHER UNIQUEMENT SI le document 'Effectifs_2010_2022.xlsx' a pas été mis à jour ce mois ci)")
        #tmp.place(anchor = 'w', relx = 0.15, rely = 0.75)
        
        #tmp_var_check = tk.IntVar()
        #tmp_check = tk.Checkbutton(self, variable = tmp_var_check)
        #tmp_check.place(anchor = 'center', relx = 0.85, rely = 0.75)
        
    def _generate_pages(self, bibliometer_path):
        
        """
        Permet la génération des pages après spécification du chemin vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, sinon redemande de renseigner un chemin.
        """
        
        # 3rd library imports
        #from datetime import date
        #from BiblioMeter_FUNCTS.BiblioMeterFonctions import maj_listing_RH
        
        ## Met à jour le fichier RH, si demandé
        #if check_MAJ == 1:
            ## TO DO : METTRE CHEMIN EN GLOBAL
            
            #maj_listing_RH()
            
            #path = r'S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.1-Dossiers en cours\111- Ludovic Desmeuzes\BiblioMeter_Files\Listing RH\MAJ.txt'
            #f = open(path,'w')
            #nouvelle_date = f'{date.today().month}{date.today().year}'
            #if len(nouvelle_date) == 5:
                #nouvelle_date = '0' + nouvelle_date
            #f.writelines(nouvelle_date)
            #f.close()
            
        if bibliometer_path == '':
            messagebox.showwarning("Attention","Chemin non renseigné, l'application ne peut pas être lancée. \nVeuillez le faire.")

        else:
            # Bouton création des autres pages
            Pages = (Page_ParsingInstitution,
                     #Page_Allyears,
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
        label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*min(SFH, SFHP), anchor = "center")
        
        button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        button = tk.Button(container_button, 
                           text = "Analyse élémentaire des corpus", 
                           font = button_font, 
                           command = lambda: controller._show_frame("Page_ParsingConcat"))
        button.grid(row = 0, column = 0)
        

####################################################################### DEUXIEME PAGE #######################################################################
class Page_MergeEffectif(tk.Frame):    
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
        
        # Creation of the class object PageTwo
        create_MergeEffectif(self, bibliometer_path, controller)
        
        label_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
        label = tk.Label(self, 
                         text="Consolidation annuelle des corpus", 
                         font = label_font)
        label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*min(SFH, SFHP), anchor = "center")
        
        button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        button = tk.Button(container_button, 
                           text = "Consolidation annuelle des corpus", 
                           font = button_font, 
                           command = lambda: controller._show_frame("Page_MergeEffectif"))
        button.grid(row = 0, column = 2)

####################################################################### TROISIEME PAGE #######################################################################
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
        
        win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(controller)
        
        # Creation of the class object PageTwo
        create_ParsingInstitution(self, bibliometer_path, controller)
        
        label_font = tkFont.Font(family = "Helvetica", size = font_size(25, min(SFW, SFWP)))
        label = tk.Label(self, 
                         text="Consolidation annuelle des corpus", 
                         font = label_font)
        label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*min(SFH, SFHP), anchor = "center")
        
        button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        button = tk.Button(container_button, 
                           text = "Consolidation annuelle des corpus", 
                           font = button_font, 
                           command = lambda: controller._show_frame("Page_ParsingInstitution"))
        button.grid(row = 0, column = 1)

####################################################################### QUATRIEME PAGE #######################################################################
class Page_WorkSubmit(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # Local imports
        from BiblioMeter_GUI.Page_WorkSubmit import create_WorkSubmit
        
        # Creation of the class object PageFour
        create_WorkSubmit(self, bibliometer_path, controller)    
        
        label = tk.Label(self, 
                         text="Filtrer le fichier submit", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.05)
        
        button = tk.Button(container_button, text = 'Filtre sur Submit', command = lambda: controller._show_frame("Page_WorkSubmit"))
        button.grid(row = 0, column = 4)

####################################################################### CINQUIEME PAGE #######################################################################
class Page_Allyears(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # Local imports
        from BiblioMeter_GUI.Page_Allyears import create_Allyears
        
        # Creation of the class object PageFour
        create_Allyears(self, bibliometer_path, controller)    
        
        label = tk.Label(self, 
                         text="Extraire sur les 5 ans", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.05)
        
        button = tk.Button(container_button, text = 'Extraire sur les 5 ans', command = lambda: controller._show_frame("Page_Allyears"))
        button.grid(row = 0, column = 3)
        

####################################################################### CINQUIEME PAGE #######################################################################
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
        label.place(x = (win_width/2), y = (mm_to_px(15, PPI))*min(SFH, SFHP), anchor = "center")
        
        button_font = tkFont.Font(family = "Helvetica", size = font_size(10, min(SFW, SFWP)))
        button = tk.Button(container_button, 
                           text = "Mise à jour des IF", 
                           font = button_font, 
                           command = lambda: controller._show_frame("Page_MultiAnnuelle"))
        button.grid(row = 0, column = 3)