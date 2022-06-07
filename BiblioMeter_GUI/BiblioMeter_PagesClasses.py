__all__ = ['App_Test']

import tkinter as tk

class App_Test(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Standard library imports
        import os
        
        # 3rd library imports
        import tkinter as tk
        from tkinter import messagebox
        
        # Local library imports
        from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
        from BiblioMeter_GUI.BiblioMeter_UsefulClasses import LabelEntry
        
        # To do :
        global screen_width
        screen_width = self.winfo_screenwidth()
        global screen_height
        screen_height = self.winfo_screenheight()
        
        global window_width
        window_width = 700
        global window_heigth
        window_height = 900
        
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
                       text="Page de lancement de BiblioMeter", 
                       font = ("Helvetica", 35))
        tmp.place(anchor = 'n', relx = 0.5, rely = 0.05)
        self.REP.append(tmp)
            
        # Placement de LABEL ENTRY TO DO
        self.LONGUEUR_ENTRY_FICHIER = 100
        self.POSITION_SELON_X = 200 # Droite/Gauche
        self.POSITION_SELON_Y = 150 # Haut/Bas
        self.ESPACE_ENTRE_LIGNE = 30
            
        tmp = LabelEntry(self, text_label='Emplacement de BiblioMeter :', width=self.LONGUEUR_ENTRY_FICHIER)
        tmp.set(ROOT_PATH)
        tmp.place(x=self.POSITION_SELON_X, 
                  y=self.ESPACE_ENTRE_LIGNE+self.POSITION_SELON_Y, 
                  align=True)
        self.REP.append(tmp)
        
        tmp = tk.Button(self, 
                        text = "Lancer l'application", 
                        font = ("Helvetica", 25), 
                        command = lambda: self._generate_pages(self.REP[1].get()))
        tmp.place(anchor = 'n', relx = 0.5, rely = 0.4)
        self.REP.append(tmp)
        
    def _generate_pages(self, bibliometer_path):
        
        """
        Permet la génération des pages après spécification du chemin vers la zone de stockage.
        Vérifie qu'un chemin a été renseigné et continue le cas échant, sinon redemande de renseigner un chemin.
        """
        if bibliometer_path == '':
            messagebox.showwarning("Attention","Chemin non renseigné, l'application ne peut pas être lancée. \nVeuillez le faire.")

        else:
            # Bouton création des autres pages
            Pages = (PageOne,
                     PageThree,
                     PageTwo, 
                     PageFour)

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

class PageOne(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # Standard library imports
        from pathlib import Path
        
        # Local library imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.BiblioMeter_PageOne import create_PageOne
        
        # Creation of the class object PageOne
        create_PageOne(self, bibliometer_path)
        
        label = tk.Label(self, 
                         text="Parser les corpus", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.1)
        
        button = tk.Button(container_button, text = 'Parsing des corpus', command = lambda: controller.show_frame("PageOne"))
        button.grid(row = 0, column = 0)
        

####################################################################### DEUXIEME PAGE #######################################################################
class PageTwo(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # Local imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.BiblioMeter_PageTwo import create_PageTwo
        
        # Creation of the class object PageTwo
        create_PageTwo(self, bibliometer_path)
        
        label = tk.Label(self, 
                         text="Analyse multi mensuelle", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.1)
        
        button = tk.Button(container_button, text = 'Analyse multi mensuelle', command = lambda: controller.show_frame("PageTwo"))
        button.grid(row = 0, column = 2)

####################################################################### TROISIEME PAGE #######################################################################
class PageThree(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller
        
        # Standard library imports
        from pathlib import Path
        
        # Local imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.BiblioMeter_PageThree import create_PageThree
        
        # Creation of the class object PageThree
        create_PageThree(self, bibliometer_path)       
        
        label = tk.Label(self, 
                         text="Travailler sur les fichiers parsés", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0.1)
        
        button = tk.Button(container_button, text = 'Travailler sur les fichiers parsés', command = lambda: controller.show_frame("PageThree"))
        button.grid(row = 0, column = 1)

####################################################################### QUATRIEME PAGE #######################################################################
class PageFour(tk.Frame):    
    def __init__(self, parent, controller, container_button, bibliometer_path):
        super().__init__(parent)
        self.controller = controller

        # Standard library imports
        from pathlib import Path
        
        # Local imports
        import BiblioAnalysis_Utils as bau
        from BiblioMeter_GUI.BiblioMeter_PageFour import create_PageFour
        
        # Creation of the class object PageFour
        create_PageFour(self, bibliometer_path)    
        
        label = tk.Label(self, 
                         text="Filtrer le fichier submit", 
                         font = ("Helvetica", 25))
        label.place(anchor = 'n', relx = 0.5, rely = 0)
        
        button = tk.Button(container_button, text = 'Filtre sur Submit', command = lambda: controller.show_frame("PageFour"))
        button.grid(row = 0, column = 4)