__all__ = ['App_Test']

import tkinter as tk

class App_Test(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Standard library imports
        from pathlib import Path
        import os
        
        # 3rd library imports
        from datetime import date
        import pandas as pd
        import tkinter as tk
        from tkinter import messagebox
        
        # Local library imports
        from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
        from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
        from BiblioMeter_GUI.Useful_Classes import LabelEntry
        from BiblioMeter_FUNCTS.BiblioMeterFonctions import maj_listing_RH
        
        from BiblioMeter_GUI.Coordinates import WINDOW_HEIGHT
        from BiblioMeter_GUI.Coordinates import WINDOW_WIDTH
        
        # To do :
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_height = WINDOW_HEIGHT
        window_width = WINDOW_WIDTH
        
        global center_x 
        center_x = int(screen_width/2 - window_width)
        global center_y 
        center_y = int(screen_height/2 - window_height/3)
        
        self.geometry(f"{window_height}x{window_width}+{center_x}+{center_y}")
        self.title('BiblioMeter Beta Test')
        self.resizable(False, False)
        
        self.REP = list()
        
        # TITRE DE LA PAGE
        tmp = tk.Label(self, 
                       text="Page de lancement de BiblioMeter Files", 
                       font = ("Helvetica", 35))
        tmp.place(anchor = 'n', relx = 0.5, rely = 0.05)
        self.REP.append(tmp)
            
        # Placement de LABEL ENTRY TO DO
        self.LONGUEUR_ENTRY_FICHIER = 100
        self.POSITION_SELON_X = 200 # Droite/Gauche
        self.POSITION_SELON_Y = 150 # Haut/Bas
        self.ESPACE_ENTRE_LIGNE = 30
            
        tmp = LabelEntry(self, text_label='Emplacement de BiblioMeter Files :', width=self.LONGUEUR_ENTRY_FICHIER)
        tmp.set(ROOT_PATH)
        tmp.place(x=self.POSITION_SELON_X, 
                  y=self.ESPACE_ENTRE_LIGNE+self.POSITION_SELON_Y, 
                  align=True)
        self.REP.append(tmp)
        
        tmp = tk.Button(self, 
                        text = "Lancer l'application", 
                        font = ("Helvetica", 25), 
                        command = lambda: self._generate_pages(self.REP[1].get(), tmp_var_check.get()))
        tmp.place(anchor = 'n', relx = 0.5, rely = 0.4)
        self.REP.append(tmp)
        
        # TO DO : METTRE CHEMIN EN GLOBAL
        listing_alias = STOCKAGE_ARBORESCENCE['effectif'][0]
        maj_alias = STOCKAGE_ARBORESCENCE['effectif'][3]
        
        path = Path(ROOT_PATH) / Path(listing_alias) / Path(maj_alias)
        #path = "S:/130-LITEN/130.1-Direction/130.1.2-Direction Scientifique/130.1.2.1-Dossiers en cours/110-Alternants/2021-22 Ludovic Desmeuzes/BiblioMeter_Files/Listing RH/MAJ.txt"
        f = open(path,'r')
        last_MAJ = f.readline()
        f.close()

        # Mise à jour du fichier RH
        tmp = tk.Label(self, text = f"Date de la dernière mise à jour des effectifs Liten : {last_MAJ}")
        tmp.place(anchor = 'w', relx = 0.15, rely = 0.7)
        
        tmp = tk.Label(self, text = f"Mettre à jour le fichier ? (COCHER UNIQUEMENT SI le document 'Effectifs_2010_2022.xlsx' n'a pas été mis à jour ce mois ci)")
        tmp.place(anchor = 'w', relx = 0.15, rely = 0.75)
        
        tmp_var_check = tk.IntVar()
        tmp_check = tk.Checkbutton(self, variable = tmp_var_check)
        tmp_check.place(anchor = 'center', relx = 0.85, rely = 0.75)
        
    def _generate_pages(self, bibliometer_path, check_MAJ):
        
        """
        Permet la génération des pages après spécification du chemin vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, sinon redemande de renseigner un chemin.
        """
        
        # 3rd library imports
        from datetime import date
        from BiblioMeter_FUNCTS.BiblioMeterFonctions import maj_listing_RH
        
        # Met à jour le fichier RH, si demandé
        if check_MAJ == 1:
            # TO DO : METTRE CHEMIN EN GLOBAL
            
            maj_listing_RH()
            
            path = r'S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.1-Dossiers en cours\111- Ludovic Desmeuzes\BiblioMeter_Files\Listing RH\MAJ.txt'
            f = open(path,'w')
            nouvelle_date = f'{date.today().month}{date.today().year}'
            if len(nouvelle_date) == 5:
                nouvelle_date = '0' + nouvelle_date
            f.writelines(nouvelle_date)
            f.close()
            
        if bibliometer_path == '':
            messagebox.showwarning("Attention","Chemin non renseigné, l'application ne peut pas être lancée. \nVeuillez le faire.")

        else:
            # Bouton création des autres pages
            Pages = (Page_ParsingInstitution,
                     Page_Allyears,
                     Page_ParsingConcat)

            # Création de mes deux containers
            container_button = tk.Frame(self, height = 50, bg = 'red')
            container_button.pack(side="top", fill="both", expand=False)

            container_frame = tk.Frame(self)
            container_frame.pack(side="top", fill="both", expand=True)
            container_frame.grid_rowconfigure(0, weight=1)
            container_frame.grid_columnconfigure(0, weight=1)

            self.frames = {}
            for F in Pages:
                page_name = F.__name__
                frame = F(parent = container_frame, controller = self, container_button = container_button, bibliometer_path = bibliometer_path)
                self.frames[page_name] = frame

                # put all of the pages in the same location;
                # the one on the top of the stacking order
                # will be the one that is visible.
                frame.grid(row=0, column=0, sticky="nsew")
        
    def show_frame(self, page_name):
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
        
        # Local library imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.Page_ParsingConcat import create_ParsingConcat
        
        # Creation of the class object PageOne
        create_ParsingConcat(self, bibliometer_path)
        
        label = tk.Label(self, 
                         text="Parser les corpus", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.05)
        
        button = tk.Button(container_button, text = 'Parsing des corpus', command = lambda: controller.show_frame("Page_ParsingConcat"))
        button.grid(row = 0, column = 0)
        

####################################################################### DEUXIEME PAGE #######################################################################
class Page_MergeEffectif(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # Local imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.Page_MergeEffectif import create_MergeEffectif
        
        # Creation of the class object PageTwo
        create_MergeEffectif(self, bibliometer_path)
        
        label = tk.Label(self, 
                         text="Analyse multi mensuelle", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.1)
        
        button = tk.Button(container_button, text = 'Analyse multi mensuelle', command = lambda: controller.show_frame("Page_MergeEffectif"))
        button.grid(row = 0, column = 2)

####################################################################### TROISIEME PAGE #######################################################################
class Page_ParsingInstitution(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # Standard library imports
        from pathlib import Path
        
        # Local imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.Page_ParsingInstitution import create_ParsingInstitution
        
        # Creation of the class object PageThree
        create_ParsingInstitution(self, bibliometer_path)       
        
        label = tk.Label(self, 
                         text="Travailler sur les fichiers parsés", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.05)
        
        button = tk.Button(container_button, text = 'Travailler sur les fichiers parsés', command = lambda: controller.show_frame("Page_ParsingInstitution"))
        button.grid(row = 0, column = 1)

####################################################################### QUATRIEME PAGE #######################################################################
class Page_WorkSubmit(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # Local imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.Page_WorkSubmit import create_WorkSubmit
        
        # Creation of the class object PageFour
        create_WorkSubmit(self, bibliometer_path)    
        
        label = tk.Label(self, 
                         text="Filtrer le fichier submit", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.05)
        
        button = tk.Button(container_button, text = 'Filtre sur Submit', command = lambda: controller.show_frame("Page_WorkSubmit"))
        button.grid(row = 0, column = 4)

####################################################################### CINQUIEME PAGE #######################################################################
class Page_Allyears(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # Local imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.Page_Allyears import create_Allyears
        
        # Creation of the class object PageFour
        create_Allyears(self, bibliometer_path)    
        
        label = tk.Label(self, 
                         text="Extraire sur les 5 ans", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.05)
        
        button = tk.Button(container_button, text = 'Extraire sur les 5 ans', command = lambda: controller.show_frame("Page_Allyears"))
        button.grid(row = 0, column = 3)