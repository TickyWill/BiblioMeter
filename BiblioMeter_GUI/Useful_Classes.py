__all__= ['LabelEntry',
          'CheckBoxCorpuses',
          'LabelEntry_toFile',
          'LabelEntry_toValue',
         ]

class LabelEntry:
    
    """
    Petit automat permettant d'afficher sur la même ligne :
    - un texte d'info
    - une entrée
    - un boutton
    
    Fonctionnalités :
        - l'opt "align" sur la méthode <place> permet d'alligner sur l'entrée plutot que sur le texte.
        - surcharge des méthode get() et set() : pointeur vers le tk.StringVar()
          (permet de garder la continuité des appels sur l'objet Entry créé)
        - permet de masquer/afficher la ligne (<.efface()> / <.place()>) (inutile pour le moment)
        - autorise le replacement (~déplacement) // méthode self.place(x=<float>, y=<float>)
    """

    def __init__(self, parent, text_label, font_label, text_button, font_button, *args, **kargs):
        
        # 3rd party imports
        import tkinter as tk
        
        self.lab = tk.Label(parent, text = text_label, font = font_label)
        self.val = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.val2 = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.entree = tk.Entry(parent, textvariable = self.val)
        self.entree2 = tk.Entry(parent, textvariable = self.val2, *args, **kargs)
        self.but = tk.Button(parent, text = text_button, font = font_button, command = self.get_file)

    def place(self, x, y, but_pos_dx, but_pos_dy, align = True):
        a,b = self.lab.winfo_reqwidth(),0
        if not align:
            a,b = b,a
        self.lab.place(x = x - a, y = y, anchor = "w")
        self.entree2.place(x = x + b, y = y, anchor = "w")
        self.but.place(x = x + b + self.entree2.winfo_reqwidth() + but_pos_dx, y = y + but_pos_dy, anchor = "w")
        
    def get(self):
        return self.val.get()
    
    def set(self, value):
        self.val.set(value)
        
    def set2(self, value):
        # Standard library imports
        from pathlib import Path
        
        p = Path(value)
        self.val2.set(('/'.join(p.parts[0:2])) / Path("...") / ('/'.join(p.parts[-3:])))
        
    def get_file(self):
        
        # Standard library imports
        from pathlib import Path
        
        # 3rd party imports
        import tkinter as tk
        from tkinter import filedialog

        # Local variables
        dialog_title = "Choisir un nouveau dossier de travail"
        warning_title = "!!! Attention !!!"
        warning_text = "Chemin non renseigné."
        
        fic = tk.filedialog.askdirectory(title = dialog_title)
        if fic == '':
            return tk.messagebox.showwarning(warning_title, warning_ext)
        self.val.set(fic)
        
        p = Path(fic)
        self.val2.set(('/'.join(p.parts[0:2])) / Path("...") / ('/'.join(p.parts[-3:])))
        
    def efface(self):
        for x in (self.lab, self.entree):
            x.place_forget()


class CheckBoxCorpuses:
    
    """ 
    Petit automat permettant d'afficher sur la même ligne :
        - L'annee du corpus
        - Wos rawdata/parsing dispo
        - Scopus rawdata/parsing dispo
    """
    
    def __init__(self, parent, year, wos_r, wos_p, scopus_r, scopus_p, concat, *agrs, **kargs):
        
        # 3rd library imports
        import tkinter as tk
        from tkinter import font as tkFont
        
        # BiblioAnalysis_Utils package imports
        from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
        
        # Local library imports
        from BiblioMeter_GUI.GUI_Globals import root_properties        
        from BiblioMeter_GUI.Useful_Functions import font_size
        
        # Local globals imports
        from BiblioMeter_GUI.GUI_Globals import FONT_NAME
        from BiblioMeter_GUI.GUI_Globals import PPI
        from BiblioMeter_GUI.GUI_Globals import REF_CHECK_BOXES_SEP_SPACE        
        from BiblioMeter_GUI.GUI_Globals import ROOT_PATH        
        
        # Getting useful window sizes and scale factors depending on displays properties
        sizes_tuple   = root_properties(parent)
        win_width_px  = sizes_tuple[0]    # unused here
        win_height_px = sizes_tuple[1]    # unused here
        width_sf_px   = sizes_tuple[2]    # unused here
        height_sf_px  = sizes_tuple[3]    # unused here
        width_sf_mm   = sizes_tuple[4]
        height_sf_mm  = sizes_tuple[5]
        width_sf_min  = min(width_sf_mm, width_sf_px)
        
        self.check_boxes_sep_space = _mm_to_px(REF_CHECK_BOXES_SEP_SPACE * width_sf_mm, PPI)
        font = tkFont.Font(family = FONT_NAME, size = font_size(11, width_sf_min))
        self.lab = tk.Label(parent, 
                            text = 'Année ' + year, 
                            font = font)
        
        self.wos_r = tk.Checkbutton(parent)
        if wos_r == True:
            self.wos_r.select()
        self.wos_p = tk.Checkbutton(parent)
        if wos_p == True:
            self.wos_p.select()
        self.scopus_r = tk.Checkbutton(parent)
        if scopus_r == True:
            self.scopus_r.select()
        self.scopus_p = tk.Checkbutton(parent)
        if scopus_p == True:
            self.scopus_p.select()
        self.concat = tk.Checkbutton(parent)
        if concat == True:
            self.concat.select()
    
    def place(self, x, y):
        a = self.lab.winfo_reqwidth()
        self.lab.place(x = x-a, y = y, anchor = 'center')
        self.wos_r.place(x = x+self.check_boxes_sep_space, y = y, anchor = 'center')
        self.wos_r.config(state = 'disabled')
        self.wos_p.place(x = x+2*self.check_boxes_sep_space, y = y, anchor = 'center')
        self.wos_p.config(state = 'disabled')
        self.scopus_r.place(x = x+3*self.check_boxes_sep_space, y = y, anchor = 'center')
        self.scopus_r.config(state = 'disabled')
        self.scopus_p.place(x = x+4*self.check_boxes_sep_space, y = y, anchor = 'center')
        self.scopus_p.config(state = 'disabled')
        self.concat.place(x = x+5*self.check_boxes_sep_space, y = y, anchor = 'center')
        self.concat.config(state = 'disabled')
        
    def efface(self):
        for x in (self.lab, self.wos_r, self.wos_p, self.scopus_r, self.scopus_p, self.concat):
            x.place_forget()
            

class ColumnFilter:
    
    """
    """
    
    def __init__(self, parent, text_label, df, *arg, **kargs):
        
        # 3rd party imports
        import tkinter as tk
        
        # Local variables
        button_label1 = 'Choix filtre inter colonne'
        
        self.check_var_1 = tk.IntVar()
        self.check_column = tk.Checkbutton(parent, variable = self.check_var_1, command = lambda : self.ables_disables_1())

        self.check_var_2 = tk.IntVar()
        self.check_value = tk.Checkbutton(parent, variable = self.check_var_2, command = lambda : self.ables_disables_2(), state = 'disable')

        self.column_name = tk.Label(parent, text = text_label + ' : ', state = 'disable')
        
        self.drop_down = tk.Button(parent, text = button_label1, command = lambda : self.open_list_box_create_filter(df, text_label, parent))
        self.drop_down.configure(state = 'disable')
        
        self.val = tk.StringVar(parent)
        self.val.set(text_label)
        self.real_column_name = tk.Entry(parent, textvariable = self.val)        
        
    def place(self, y):
        self.check_column.grid(row = y, column = 0)
        self.column_name.grid(row = y, column = 1)
        self.drop_down.grid(row = y, column = 3)
        self.check_value.grid(row = y, column = 2)
    
    def efface(self):
        pass
    
    def get_check_1(self):
        return self.check_var_1.get()
    
    def get_label(self):
        return self.real_column_name.get()
    
    def ables_disables_1(self):
        if self.check_var_1.get() == 1:
            self.column_name.configure(state = 'normal')
            self.check_value.configure(state = 'normal')
        else:
            self.column_name.configure(state = 'disable')
            self.check_value.configure(state = 'disable')
            self.drop_down.configure(state = 'disable')
            self.check_var_2.set(0)
            
    def ables_disables_2(self):
        if self.check_var_2.get() == 1:
            self.drop_down.configure(state = 'normal')
        else:
            self.drop_down.configure(state = 'disable')
            
    def open_list_box_create_filter(self, df, column, parent):
        
        # 3rd party imports
        import tkinter as tk
        from tkinter import Toplevel
        
        # Local variables
        newWindow_title_label = 'Selection des filtres inter colonnes'
        button_label2 = "Valider la sélection"
        
        def _access_values(df, column):
            values = df[column].unique().tolist()
            #values.sort()
            return values
        
        newWindow = tk.Toplevel(parent)
        newWindow.title(newWindow_title_label)

        newWindow.geometry(f"600x600+{parent.winfo_rootx()}+{parent.winfo_rooty()}")

        yscrollbar = tk.Scrollbar(newWindow)
        yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        my_listbox = tk.Listbox(newWindow, 
                                selectmode = tk.MULTIPLE, 
                                yscrollcommand = yscrollbar.set)
        my_listbox.place(anchor = 'center', width = 400, height = 400, relx = 0.5, rely = 0.5)

        x = _access_values(df, column)
        for idx, item in enumerate(x):
            my_listbox.insert(idx, item)
            my_listbox.itemconfig(idx,
                                  bg = "white" if idx % 2 == 0 else "white")
            
        button = tk.Button(newWindow, text = button_label2)
        button.place(anchor = 'n', relx = 0.5, rely = 0.9)
        
class LabelEntry_toFile:
    
    """
    Petit automat permettant d'afficher sur la même ligne :
    - un texte d'info
    - une entrée
    - un boutton
    
    Fonctionnalités :
        - l'opt "align" sur la méthode <place> permet d'alligner sur l'entrée plutot que sur le texte.
        - surcharge des méthode get() et set() : pointeur vers le tk.StringVar()
          (permet de garder la continuité des appels sur l'objet Entry créé)
        - permet de masquer/afficher la ligne (<.efface()> / <.place()>) (inutile pour le moment)
        - autorise le replacement (~déplacement) // méthode self.place(x=<float>, y=<float>)
    """

    def __init__(self, parent, text_label, font_label, font_button, *args, **kargs):
        
        # 3rd party imports
        import tkinter as tk
        
        # Local variables
        button_label = "Choix du fichier"
        
        self.lab = tk.Label(parent, text = text_label, font = font_label)
        self.val = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.val2 = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.entree = tk.Entry(parent, textvariable=self.val)
        self.entree2 = tk.Entry(parent, textvariable = self.val2, *args, **kargs)
        self.but = tk.Button(parent, text = button_label, font = font_button, command = self.get_file)

    def place(self,x,y,align=True):
        a,b = self.lab.winfo_reqwidth(),0
        if not align:
            a,b = b,a
        self.lab.place(x=x-a,y=y)
        self.entree2.place(x = x + b, y = y)
        self.but.place(x=x+b+self.entree2.winfo_reqwidth()+10,y=y-2)
        
    def get(self):
        return self.val.get()
    
    def set(self, value):
        self.val.set(value)
        
    def set2(self, value):
        from pathlib import Path
        p = Path(value)
        self.val2.set(p.name)
        
    def get_file(self):
        # Standard library imports
        from pathlib import Path
        
        # 3rd party imports
        import tkinter as tk
        from tkinter import filedialog
        
        # Local variables
        dialog_title = 'Choisir un fichier petit pingouin des Alpes'
        warning_title = "Attention"
        warning_text = "Chemin non renseigné"
        
        fic = tk.filedialog.askopenfilename(title = dialog_title)
        if fic == '':
            return tk.messagebox.showwarning(warning_title, warning_text)
        self.val.set(fic)
        
        p = Path(fic)
        self.val2.set(p.name)
        
    def efface(self):
        for x in (self.lab, self.entree):
            x.place_forget()

            
class LabelEntry_toValue:
    
    """
    Petit automat permettant d'afficher sur la même ligne :
    - un texte d'info
    - une entrée
    - un boutton
    
    Fonctionnalités :
        - l'opt "align" sur la méthode <place> permet d'alligner sur l'entrée plutot que sur le texte.
        - surcharge des méthode get() et set() : pointeur vers le tk.StringVar()
          (permet de garder la continuité des appels sur l'objet Entry créé)
        - permet de masquer/afficher la ligne (<.efface()> / <.place()>) (inutile pour le moment)
        - autorise le replacement (~déplacement) // méthode self.place(x=<float>, y=<float>)
    """

    def __init__(self, parent, text_label, font_label):
        
        # 3rd party imports
        import tkinter as tk
        self.lab = tk.Label(parent, text = text_label, font = font_label)
        self.val = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.entree = tk.Entry(parent, textvariable=self.val)
        self.val2 = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.entree2 = tk.Entry(parent, textvariable = self.val2)

    def place(self,x,y,align=True):
        a,b = self.lab.winfo_reqwidth(),0
        if not align:
            a,b = b,a
        self.lab.place(x=x-a,y=y)
        self.entree2.place(x = x + b, y = y)
        
    def get(self):
        return self.val.get()
    
    def set(self, value):
        self.val.set(value)
        
    def set2(self, value):
        from pathlib import Path
        p = Path(value)
        self.val2.set(p.name)
        
    def efface(self):
        for x in (self.lab, self.entree):
            x.place_forget()            