__all__ = ['create_PageThree']

def create_PageThree(self, bibliometer_path):
    
    """
    Description : function working as a bridge between the BiblioMeter 
    App and the functionalities needed for the use of the app
    
    Uses the following globals : 
    - DIC_OUT_PARSING
    - FOLDER_NAMES
    
    Args : takes only self and bibliometer_path as arguments. 
    self is the intense in which PageThree will be created
    bibliometer_path is a type Path, and is the path to where the folders
    organised in a very specific way are stored
    
    Returns : nothing, it create the page in self
    """
    
    # Standard library imports
    from pathlib import Path

    # 3rd party imports
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox

    # Local imports
    import BiblioAnalysis_Utils as bau
    from BiblioMeter_GUI.BiblioMeter_AllPagesFunctions import five_last_available_years
    from BiblioMeter_GUI.BiblioMeter_AllPagesFunctions import existing_corpuses


    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    
    ### Choose which year you want to be working with #############################################################################################################
    years_list = five_last_available_years(bibliometer_path)
    variable = tk.StringVar(self)
    variable.set(years_list[0])
    
        # Création de l'optionbutton des années
    OptionButton = tk.OptionMenu(self, variable, *years_list)
    OptionButton.place(anchor = 'center', relx = 0.40, rely = 0.20)
    
        # Création du label
    Label = tk.Label(self, text = '''Choisir l'année de travail :''')
    Label.place(anchor = 'center', relx = 0.20, rely = 0.20)
    ###############################################################################################################################################################
    
    
    ### Bouton qui va permettre d'utiliser seeting_secondary_inst_filter sur un corpus concatené ##################################################################
    Button = tk.Button(self, 
                       text = 'Choisir les affiliations', 
                       command = lambda: _setting_extend())
    Button.place(anchor = 'center', relx = 0.70, rely = 0.2)
    ###############################################################################################################################################################
    
    def _setting_extend():

        """
        Description :

        Uses the following globals :

        Args :

        Returns :
        """

        # Setting path_to_folder
        path_to_folder = bibliometer_path / Path(variable.get()) / Path(FOLDER_NAMES['corpus']) / Path(FOLDER_NAMES['dedup']) / Path(FOLDER_NAMES['parsing'])
        
        ### On récupère la présence ou non des fichiers #################################        
        results = existing_corpuses(bibliometer_path)

        list_corpus_year = results[0]
        list_wos_rawdata = results[1]
        list_wos_parsing = results[2]
        list_scopus_rawdata = results[3]
        list_scopus_parsing = results[4]
        list_concatenation = results[5]
        #################################################################################
        
        if list_wos_parsing[list_corpus_year.index(variable.get())] == False:
            messagebox.showwarning('Fichiers manquants', f"Warning : le fichier authorsinst.dat de wos de l'année {variable.get()} n'est pas disponible. \nVeuillez effectuer le parsing avant de parser les instituts")
            return
        
        full_list = bau.getting_secondary_inst_list(path_to_folder)

        _open_list_box_filter(self, full_list, path_to_folder)

    def _open_list_box_filter(self, full_list, path_to_folder):

        """
        Description :

        Uses the following globals :

        Args :

        Returns :
        """

        newWindow = tk.Toplevel(self)
        newWindow.grab_set()
        newWindow.title('Selection des institutions à parser')

        newWindow.geometry(f"600x600+{self.winfo_rootx()}+{self.winfo_rooty()}")

        label = tk.Label(newWindow, text="Selectionner les \n institutions", font = ("Helvetica", 20))
        label.place(anchor = 'n', relx = 0.5, rely = 0.025)

        yscrollbar = tk.Scrollbar(newWindow)
        yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        my_listbox = tk.Listbox(newWindow, 
                                selectmode = tk.MULTIPLE, 
                                yscrollcommand = yscrollbar.set)
        my_listbox.place(anchor = 'center', width = 400, height = 400, relx = 0.5, rely = 0.5)

        # TO DO : Ajouter une présélection

        x = full_list
        for idx, item in enumerate(x):
            my_listbox.insert(idx, item)
            my_listbox.itemconfig(idx,
                                  bg = "white" if idx % 2 == 0 else "white")
        # TO DO : Utiliser la global INST_FILTER_LIST quand feu vert de Amal et François
        n = x.index('France:LITEN')
        my_listbox.selection_set(first = n)
        n = x.index('France:INES')
        my_listbox.selection_set(first = n)
            
        # TO DO : Nommer la variable dans la commande
        
        button = tk.Button(newWindow, text ="Lancer le parsing des institutions", 
                           command = lambda: launch())
        button.place(anchor = 'n', relx = 0.5, rely = 0.9)
    
        def launch():
            
            bau.extend_author_institutions(path_to_folder, [(x.split(':')[1].strip(),x.split(':')[0].strip()) for x in [my_listbox.get(i) for i in my_listbox.curselection()]])
            
            messagebox.showinfo('Information', f"Le parsing des institutions sélectionnées a été efectué.")
            
            newWindow.destroy()
            
            