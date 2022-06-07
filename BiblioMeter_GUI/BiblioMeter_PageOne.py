__all__ = ['create_PageOne']

def _data_parsing(corpus_year, database_type, bibliometer_path):

    """
    Description : Parses corpuses from wos or scopus (depending on the arg database_type
    using the function biblio_parser from BiblioAnalysis_Utils. 

    Uses the following globals :
    - DIC_OUTIR_PARSING
    - FOLDER_NAMES

    Args :
    - corpus_year : The year of the extracted corpuses
    - database_type : Either wos or scopus depending from where comes the corpuses
    - results : A list of list of zeros and ones displaying available or not
    rawdata and parsing where documents are stocked by year.
    [[2018, 2019, 2020, 2021, 2022],   #Years
     [0, 0, 0, 0, 0],                  #Wos Rawdata
     [0, 0, 0, 0, 0],                  #Scopus Rawdata
     [0, 0, 0, 0, 0],                  #Wos Parsing
     [0, 0, 0, 0, 0],                  #Scopus Parsing
     [0, 0, 0, 0, 0]]                  #Concatenation & Deduplication
    - second_inst : For the time being it is a binary value, 1 meaning that secondary institutions 
    should be parsed, 0 meaning it shouldn't. Secondary institutions can (for the time being) be
    found in the inst_filter_dic variable inside of data_parsing

    Returns :
    Display the number of articles parsed, and via the function biblio_parser, create a set of
    documents (.dat) which are results of the parsing of the treated corpuses.

    """

    # Standard library imports
    import os
    import json
    from pathlib import Path

    # 3rd party imports
    import tkinter as tk
    from tkinter import messagebox

    # Local imports
    import BiblioAnalysis_Utils as bau

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES

    from BiblioMeter_GUI.BiblioMeter_AllPagesFunctions import existing_corpuses
        
    ### On récupère la présence ou non des fichiers #################################        
    results = existing_corpuses(bibliometer_path)

    list_corpus_year = results[0]
    list_wos_rawdata = results[1]
    list_wos_parsing = results[2]
    list_scopus_rawdata = results[3]
    list_scopus_parsing = results[4]
    list_concatenation = results[5]
    #################################################################################
    
    # Création des alias pour simplifier les accès
    wos_alias = FOLDER_NAMES['wos']
    scopus_alias = FOLDER_NAMES['scopus']
    corpus_path_alias = FOLDER_NAMES['corpus']

    scopus_path_alias = Path(corpus_path_alias) / Path(scopus_alias)
    wos_path_alias = Path(corpus_path_alias) / Path(wos_alias)

    parsing_path_alias = FOLDER_NAMES['parsing']
    rawdata_path_alias = FOLDER_NAMES['rawdata']

    concat_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['concat']
    dedupli_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['dedup']

    article_path_alias = DIC_OUTDIR_PARSING['A']

    expert = False

    answer_1 = messagebox.askokcancel('Information', f"Une procédure de parsing a été lancée, continuer à parser ?")
    if answer_1:
        # Creation of path_rawdata, path_parsing, rep_utils and parser_done
        if database_type == 'wos':
            if list_wos_rawdata[list_corpus_year.index(corpus_year)] == False:
                messagebox.showwarning('Fichiers manquants', f"Warning : le fichier rawdata de {database_type} de l'année {corpus_year} n'est pas disponible")
                return
            else:
                path_rawdata = Path(bibliometer_path) / Path(corpus_year) / Path(wos_path_alias) / Path(rawdata_path_alias) 
                path_parsing = Path(bibliometer_path) / Path(corpus_year) / Path(wos_path_alias) / Path(parsing_path_alias)
                parser_done = list_wos_parsing[list_corpus_year.index(corpus_year)]
        else:

            if list_scopus_rawdata[list_corpus_year.index(corpus_year)] == False:
                messagebox.showwarning('Missing files', f"Warning : le fichier rawdata de {database_type} de l'année {corpus_year} n'est pas disponible")
                return
            else:
                path_rawdata = Path(bibliometer_path) / Path(corpus_year) / Path(scopus_path_alias) / Path(rawdata_path_alias)
                path_parsing = Path(bibliometer_path) / Path(corpus_year) / Path(scopus_path_alias) / Path(parsing_path_alias)
                parser_done = list_scopus_parsing[list_corpus_year.index(corpus_year)]

        if not os.path.exists(path_parsing):
            os.mkdir(path_parsing)

        if parser_done == 1:
            # Ask to carry on with parsing if already done
            answer_2 = messagebox.askokcancel('Information', f"Le parsing pour le corpus {database_type} de l'année {corpus_year} est déjà disponible, continuer à parser ?")
            if answer_2:
                bau.biblio_parser(path_rawdata, path_parsing, database_type, expert) 
                with open(Path(path_parsing) / Path('failed.json'), 'r') as failed_json:
                    data_failed=failed_json.read()
                dic_failed = json.loads(data_failed)

                articles_number = dic_failed["number of article"]

                messagebox.showinfo('Information', f"Parsing effectué \nParsing processed on full corpus \nNumber of articles in the corpus : {articles_number}")
            else:
                messagebox.showinfo('Information', f"Parsing annulé car déjà présent")
                return
        else:
            # Parse immediately when not parsed yet
            bau.biblio_parser(path_rawdata, path_parsing, database_type, expert) 
            with open(Path(path_parsing) / Path('failed.json'), 'r') as failed_json:
                data_failed=failed_json.read()
            dic_failed = json.loads(data_failed)

            articles_number = dic_failed["number of article"]

            messagebox.showinfo('Information', f"Parsing effectué \nParsing processed on full corpus \nNumber of articles in the corpus : {articles_number}")
    else:
        return
    
    # Ajouter _update() si pas trop la flemme

def _create_table(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK):
        
    """
    Description : 

    Uses the following globals :

    Args :

    Returns :

    """
    
    # Standard library imports
    from pathlib import Path
    import os
    
    # Local imports
    import BiblioAnalysis_Utils as bau
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioMeter_GUI.BiblioMeter_AllPagesFunctions import existing_corpuses
    
    # 3rd party imports
    import tkinter as tk
    from tkinter import messagebox
    
    # Création des alias pour simplifier les accès
    wos_alias = FOLDER_NAMES['wos']
    scopus_alias = FOLDER_NAMES['scopus']
    corpus_path_alias = FOLDER_NAMES['corpus']

    scopus_path_alias = Path(corpus_path_alias) / Path(scopus_alias)
    wos_path_alias = Path(corpus_path_alias) / Path(wos_alias)

    parsing_path_alias = FOLDER_NAMES['parsing']
    rawdata_path_alias = FOLDER_NAMES['rawdata']

    concat_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['concat']
    dedupli_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['dedup']

    article_path_alias = DIC_OUTDIR_PARSING['A']
    
    ### On récupère la présence ou non des fichiers #################################        
    results = existing_corpuses(bibliometer_path)

    list_annee = results[0]
    list_wos_rawdata = results[1]
    list_wos_parsing = results[2]
    list_scopus_rawdata = results[3]
    list_scopus_parsing = results[4]
    list_concatenation = results[5]
    #################################################################################
    
    for i in range(len(self.TABLE)):
        self.TABLE[i].destroy()
        
    # Mise en page tableau
    wos_rawdata = tk.Label(self, text = 'Wos Rawdata')
    wos_rawdata.place(x = POSITION_SELON_X_CHECK + 100, y = 215, anchor = 'center')
    self.TABLE.append(wos_rawdata)

    wos_parsing = tk.Label(self, text = 'Wos Parsing')
    wos_parsing.place(x = POSITION_SELON_X_CHECK + 200, y = 215, anchor = 'center')
    self.TABLE.append(wos_parsing)

    scopus_rawdata = tk.Label(self, text = 'Scopus Rawdata')
    scopus_rawdata.place(x = POSITION_SELON_X_CHECK + 300, y = 215, anchor = 'center')
    self.TABLE.append(scopus_rawdata)

    scopus_parsing = tk.Label(self, text = 'Scopus Parsing')
    scopus_parsing.place(x = POSITION_SELON_X_CHECK + 400, y = 215, anchor = 'center')
    self.TABLE.append(scopus_parsing)

    concat = tk.Label(self, text = 'Concatenation \n and dédoublonnage')
    concat.place(x = POSITION_SELON_X_CHECK + 500, y = 215, anchor = 'center')
    self.TABLE.append(concat)

    # TITRE ZONE PARSING et CONCATENATION
    label = tk.Label(self, text="Parsing et concatenation", font = ("Helvetica", 14))
    label.place(anchor = 'center', relx = 0.5, y = (len(list_annee)+1)*ESPACE_ENTRE_LIGNE_CHECK+POSITION_SELON_Y_CHECK-15)
    self.TABLE.append(label)

    # CHOIX DE L'ANNEE POUR LE PARSING
    variable_1 = tk.StringVar(self)
    variable_1.set(list_annee[0])
    YearOptionButton = tk.OptionMenu(self, variable_1, *list_annee)
    YearOptionButton.place(anchor = 'center', relx = 0.25, y = (len(list_annee)+2)*ESPACE_ENTRE_LIGNE_CHECK+POSITION_SELON_Y_CHECK)
    self.TABLE.append(YearOptionButton)

    # CHOIX DU TYPE DE DOCUMENT POUR LE PARSING WOS/SCOPUS
    variable_2 = tk.StringVar(self)
    variable_2.set('wos')
    SourceOptionButton = tk.OptionMenu(self, variable_2, *['wos','scopus'])
    SourceOptionButton.place(anchor = 'center', relx = 0.5, y = (len(list_annee)+2)*ESPACE_ENTRE_LIGNE_CHECK+POSITION_SELON_Y_CHECK)
    self.TABLE.append(SourceOptionButton)

    # BOUTON POUR LANCER LE PARSING
    launch_button_parsing = tk.Button(self, text = 'Lancement du parsing', command = lambda: _data_parsing(variable_1.get(), 
                                                                                                           variable_2.get(), 
                                                                                                           bibliometer_path))
    launch_button_parsing.place(anchor = 'center', relx = 0.75, y = (len(list_annee)+2)*ESPACE_ENTRE_LIGNE_CHECK+POSITION_SELON_Y_CHECK)
    self.TABLE.append(launch_button_parsing)

    # CHOIX DE L'ANNEE POUR LA CONCATENATION
    variable_3 = tk.StringVar(self)
    variable_3.set(list_annee[0])
    YearOptionButton = tk.OptionMenu(self, variable_3, *list_annee)
    YearOptionButton.place(anchor = 'center', relx = 0.33, y = (len(list_annee)+4.5)*ESPACE_ENTRE_LIGNE_CHECK+POSITION_SELON_Y_CHECK-15)
    self.TABLE.append(YearOptionButton)

    # CONCATENATION DE WOS ET SCOPUS D'UNE ou PLUSIEURS ANNEESl
    concat_button = tk.Button(self, text="Lancement de la concatenation", command = lambda: _reset_year_and_launch_parsing_concat_dedup())
    concat_button.place(anchor = 'center', relx = 0.66, y = (len(list_annee)+4.5)*ESPACE_ENTRE_LIGNE_CHECK+POSITION_SELON_Y_CHECK-15)
    self.TABLE.append(concat_button)
    
    def _reset_year_and_launch_parsing_concat_dedup():
        
        ### On récupère la présence ou non des fichiers #################################        
        results = existing_corpuses(bibliometer_path)

        list_corpus_year = results[0]
        list_wos_rawdata = results[1]
        list_wos_parsing = results[2]
        list_scopus_rawdata = results[3]
        list_scopus_parsing = results[4]
        list_concatenation = results[5]
        #################################################################################
        
        if list_wos_parsing[list_corpus_year.index(variable_3.get())] == False:
            messagebox.showwarning('Fichiers manquants', f"Warning : le fichier articles.dat de wos de l'année {variable_3.get()} n'est pas disponible")
            return
        
        if list_scopus_parsing[list_corpus_year.index(variable_3.get())] == False:
            messagebox.showwarning('Fichiers manquants', f"Warning : le fichier articles.dat de scopus de l'année {variable_3.get()} n'est pas disponible")
            return
            
        # Setting the useful paths
        path_scopus_parsing = bibliometer_path / Path(variable_3.get()) / Path(scopus_path_alias) / Path(parsing_path_alias)
        path_scopus_rawdata = bibliometer_path / Path(variable_3.get()) / Path(scopus_path_alias) / Path(rawdata_path_alias) 
        path_wos_parsing = bibliometer_path / Path(variable_3.get()) / Path(wos_path_alias) / Path(parsing_path_alias)
        path_wos_rawdata = bibliometer_path / Path(variable_3.get()) / Path(wos_path_alias) / Path(rawdata_path_alias) 
        path_concat = bibliometer_path / Path(variable_3.get()) / Path(concat_path_alias)
        path_concat_parsing = path_concat / Path(parsing_path_alias)
        
        if not os.path.exists(path_concat_parsing):
            if not os.path.exists(path_concat): os.mkdir(path_concat)
            os.mkdir(path_concat_parsing)
            
        path_rational = bibliometer_path / Path(variable_3.get()) / Path(dedupli_path_alias)
        path_rational_parsing = path_rational / Path(parsing_path_alias)
        
        print(path_rational)
        print(path_rational_parsing)
        
        if not os.path.exists(path_rational_parsing):
            if not os.path.exists(path_rational): os.mkdir(path_rational)
            os.mkdir(path_rational_parsing)
            
        useful_path_list = [path_scopus_parsing, path_wos_parsing, path_concat_parsing, path_rational_parsing]    
        
        bau.parsing_concatenate_deduplicate(useful_path_list)
        
        messagebox.showinfo('Information', f"La concatenation et le dédoublement \n sont terminés")

def create_PageOne(self, bibliometer_path):

    """
    Description : 
    
    Uses the following globals :
    
    Args :
    
    Returns :
    
    """

    # Standard library imports
    import os
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

    # Liste des checkbox des corpuses
    self.CHECK = []
    self.TABLE = []

    # Placement de CHECKBOXCORPUSES : TO DO
    POSITION_SELON_X_CHECK = 245
    POSITION_SELON_Y_CHECK = 250
    ESPACE_ENTRE_LIGNE_CHECK = 35
    
    ### On récupère la présence ou non des fichiers #################################        
    results = existing_corpuses(bibliometer_path)

    list_annee = results[0]
    list_wos_rawdata = results[1]
    list_wos_parsing = results[2]
    list_scopus_rawdata = results[3]
    list_scopus_parsing = results[4]
    list_concatenation = results[5]
    #################################################################################
    
    # Bouton pour actualiser la zone de stockage
    exist_button = tk.Button(self, 
                             text = '''Mettre à jour l'état des fichiers''', 
                             command = lambda: _update())
    exist_button.place(relx = 0.5, y = 150, anchor = 'center')
    
    def _update():
        
        """
        Description : 

        Uses the following globals :

        Args :

        Returns :

        """
        # Local imports
        from BiblioMeter_GUI.BiblioMeter_UsefulClasses import CheckBoxCorpuses
        
        ### On récupère la présence ou non des fichiers #################################        
        results = existing_corpuses(bibliometer_path)

        list_annee = results[0]
        list_wos_rawdata = results[1]
        list_wos_parsing = results[2]
        list_scopus_rawdata = results[3]
        list_scopus_parsing = results[4]
        list_concatenation = results[5]
        #################################################################################

        for i, annee in enumerate(list_annee):
            tmp = CheckBoxCorpuses(self, annee, list_wos_rawdata[i], list_wos_parsing[i], list_scopus_rawdata[i], list_scopus_parsing[i], list_concatenation[i])
            tmp.place(x=POSITION_SELON_X_CHECK, y=i*ESPACE_ENTRE_LIGNE_CHECK+POSITION_SELON_Y_CHECK)
            self.CHECK.append(tmp)
        
        _create_table(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK)
    
    _create_table(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK)