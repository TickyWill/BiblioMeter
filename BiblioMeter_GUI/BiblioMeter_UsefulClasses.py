__all__=['LabelEntry', 
         'CheckBoxCorpuses']

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

    def __init__(self, parent, text_label, *args, **kargs):
        
        # 3rd party imports
        import tkinter as tk
        
        self.lab = tk.Label(parent, text=text_label)
        self.val = tk.StringVar(parent) # réel associé à la variable "fenetre".
        self.entree = tk.Entry(parent, textvariable=self.val, *args, **kargs)
        self.but = tk.Button(parent, text='...',command = self.get_file)

    def place(self,x,y,align=True):
        a,b = self.lab.winfo_reqwidth(),0
        if not align:
            a,b = b,a
        self.lab.place(x=x-a,y=y)
        self.entree.place(x=x+b,y=y)
        self.but.place(x=x+b+self.entree.winfo_reqwidth()+6,y=y-2)
        
    def get(self):
        return self.val.get()
    
    def set(self, value):
        self.val.set(value)
        
    def get_file(self):
        
        # 3rd party imports
        import tkinter as tk
        
        fic = tk.filedialog.askdirectory(title='Choisir un fichier petit pingouin des Alpes')
        if fic == '':
            return tk.messagebox.showwarning("Attention","Chemin non renseigné")
        self.val.set(fic)
        
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
        
        self.ESPACE_ENTRE_BOX_CHECK = 100
        self.lab = tk.Label(parent, text = 'Année ' + year)
        
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
        self.wos_r.place(x = x+self.ESPACE_ENTRE_BOX_CHECK, y = y, anchor = 'center')
        self.wos_r.config(state = 'disabled')
        self.wos_p.place(x = x+2*self.ESPACE_ENTRE_BOX_CHECK, y = y, anchor = 'center')
        self.wos_p.config(state = 'disabled')
        self.scopus_r.place(x = x+3*self.ESPACE_ENTRE_BOX_CHECK, y = y, anchor = 'center')
        self.scopus_r.config(state = 'disabled')
        self.scopus_p.place(x = x+4*self.ESPACE_ENTRE_BOX_CHECK, y = y, anchor = 'center')
        self.scopus_p.config(state = 'disabled')
        self.concat.place(x = x+5*self.ESPACE_ENTRE_BOX_CHECK, y = y, anchor = 'center')
        self.concat.config(state = 'disabled')
        
    def efface(self):
        for x in (self.lab, self.wos_r, self.wos_p, self.scopus_r, self.scopus_p, self.concat):
            x.place_forget()