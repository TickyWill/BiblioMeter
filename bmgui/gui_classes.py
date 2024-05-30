""" `gui_classes` module contains useful classes for gui management."""

__all__= ['LabelEntry',
          'CheckBoxCorpuses',
          'LabelEntryToFile',
          'LabelEntryToValue',
         ]


# Standard library imports
import tkinter as tk
from tkinter import font as tkFont
from pathlib import Path

# Local imports
import bmgui.gui_globals as gg
from bmgui.gui_functions import font_size
from bmgui.gui_functions import mm_to_px


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

        self.lab = tk.Label(parent, text = text_label, font = font_label)
        self.val = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.val2 = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.entree = tk.Entry(parent, textvariable = self.val)
        self.entree2 = tk.Entry(parent, textvariable = self.val2, *args, **kargs)
        self.but = tk.Button(parent, text = text_button, font = font_button, command = lambda: self.get_file)

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
        p = Path(value)
        self.val2.set(('/'.join(p.parts[0:2])) / Path("...") / ('/'.join(p.parts[-3:])))

    def get_file(self):
        dialog_title = "Choisir un nouveau dossier de travail"
        fic = tk.filedialog.askdirectory(title = dialog_title)
        if fic == '':
            warning_title = "!!! Attention !!!"
            warning_text = "Chemin non renseigné."
            tk.messagebox.showwarning(warning_title, warning_text)
        else:
            self.val.set(fic)
            p = Path(fic)
            if len(p.parts) <= 4:
                p_disp = p
            else:
                part_start = p.parts[0:2]
                part_end = p.parts[-3:]
                p_disp = ('/'.join(part_start)) / Path("...") / ('/'.join(part_end))
            self.val2.set(p_disp)

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

    def __init__(self, parent, master, year, wos_r, wos_p, scopus_r, scopus_p, concat, *agrs, **kargs):

        self.check_boxes_sep_space = mm_to_px(gg.REF_CHECK_BOXES_SEP_SPACE * master.width_sf_mm, gg.PPI)
        font = tkFont.Font(family = gg.FONT_NAME, size = font_size(11, master.width_sf_min))
        self.lab = tk.Label(parent,
                            text = 'Année ' + year,
                            font = font)

        self.wos_r = tk.Checkbutton(parent)
        if wos_r:
            self.wos_r.select()
        self.wos_p = tk.Checkbutton(parent)
        if wos_p:
            self.wos_p.select()
        self.scopus_r = tk.Checkbutton(parent)
        if scopus_r:
            self.scopus_r.select()
        self.scopus_p = tk.Checkbutton(parent)
        if scopus_p:
            self.scopus_p.select()
        self.concat = tk.Checkbutton(parent)
        if concat:
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

        # Local variables
        new_window_title_label = 'Selection des filtres inter colonnes'
        button_label2 = "Valider la sélection"

        def _access_values(df, column):
            values = df[column].unique().tolist()
            return values

        new_window = tk.Toplevel(parent)
        new_window.title(new_window_title_label)

        new_window.geometry(f"600x600+{parent.winfo_rootx()}+{parent.winfo_rooty()}")

        yscrollbar = tk.Scrollbar(new_window)
        yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        my_listbox = tk.Listbox(new_window,
                                selectmode = tk.MULTIPLE,
                                yscrollcommand = yscrollbar.set)
        my_listbox.place(anchor = 'center', width = 400, height = 400, relx = 0.5, rely = 0.5)

        x = _access_values(df, column)
        for idx, item in enumerate(x):
            my_listbox.insert(idx, item)
            my_listbox.itemconfig(idx,
                                  bg = "white" if idx % 2 == 0 else "white")

        button = tk.Button(new_window, text = button_label2)
        button.place(anchor = 'n', relx = 0.5, rely = 0.9)

class LabelEntryToFile:
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
        # Local variables
        button_label = "Choix du fichier"

        self.lab = tk.Label(parent, text = text_label, font = font_label)
        self.val = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.val2 = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.entree = tk.Entry(parent, textvariable=self.val)
        self.entree2 = tk.Entry(parent, textvariable = self.val2, *args, **kargs)
        self.but = tk.Button(parent, text = button_label, font = font_button, command = lambda: self.get_file)

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
        p = Path(value)
        self.val2.set(p.name)

    def get_file(self):
        dialog_title = 'Choisir un fichier petit pingouin des Alpes'
        fic = tk.filedialog.askopenfilename(title = dialog_title)
        if fic == '':
            warning_title = "Attention"
            warning_text = "Chemin non renseigné"
            tk.messagebox.showwarning(warning_title, warning_text)
        else:
            self.val.set(fic)
            p = Path(fic)
            self.val2.set(p.name)

    def efface(self):
        for x in (self.lab, self.entree):
            x.place_forget()


class LabelEntryToValue:
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
        p = Path(value)
        self.val2.set(p.name)

    def efface(self):
        for x in (self.lab, self.entree):
            x.place_forget()
