__all__ = ['create_ParsingConcat']

def _data_parsing(self, corpus_year, database_type, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK, bibliometer_path):

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

    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
        
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
                messagebox.showwarning('Fichiers manquants', f"Attention : le fichier rawdata de {database_type} de l'année {corpus_year} n'est pas disponible")
                return
            else:
                path_rawdata = Path(bibliometer_path) / Path(corpus_year) / Path(wos_path_alias) / Path(rawdata_path_alias) 
                path_parsing = Path(bibliometer_path) / Path(corpus_year) / Path(wos_path_alias) / Path(parsing_path_alias)
                parser_done = list_wos_parsing[list_corpus_year.index(corpus_year)]
        else:

            if list_scopus_rawdata[list_corpus_year.index(corpus_year)] == False:
                messagebox.showwarning('Fichiers manquants', f"Attention : le fichier rawdata de {database_type} de l'année {corpus_year} n'est pas disponible")
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
                messagebox.showinfo('Information', f"Le parsing n'a pas été fait.")
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
    
    _update(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK)
    
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
    
    from BiblioMeter_GUI.Coordinates import root_properties
    
    from BiblioMeter_GUI.Globals_GUI import GUI_DISP
    from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
    from BiblioMeter_GUI.Globals_GUI import PPI    

    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    
    # 3rd party imports
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import font as tkFont
    
    win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(self)
    
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
        
    # Mise en page tableau
    font_1 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    wos_rawdata = tk.Label(self, 
                           text = 'Wos\nDonnées brutes', 
                           font = font_1)
    wos_rawdata.place(x = POSITION_SELON_X_CHECK + mm_to_px(25, PPI) * SFW, y = mm_to_px(35, PPI) * SFH, anchor = 'center')
    self.TABLE.append(wos_rawdata)

    font_2 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    wos_parsing = tk.Label(self, 
                           text = 'Wos\nParsing', 
                           font = font_2)
    wos_parsing.place(x = POSITION_SELON_X_CHECK + 2 * mm_to_px(25, PPI) * SFW, y = mm_to_px(35, PPI) * SFH, anchor = 'center')
    self.TABLE.append(wos_parsing)

    font_3 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    scopus_rawdata = tk.Label(self, 
                              text = 'Scopus\nDonnées brutes', 
                              font = font_3)
    scopus_rawdata.place(x = POSITION_SELON_X_CHECK + 3 * mm_to_px(25, PPI) * SFW, y = mm_to_px(35, PPI) * SFH, anchor = 'center')
    self.TABLE.append(scopus_rawdata)

    font_4 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    scopus_parsing = tk.Label(self, 
                              text = 'Scopus\nParsing', 
                              font = font_4)
    scopus_parsing.place(x = POSITION_SELON_X_CHECK + 4 * mm_to_px(25, PPI) * SFW, y = mm_to_px(35, PPI) * SFH, anchor = 'center')
    self.TABLE.append(scopus_parsing)

    font_5 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    concat = tk.Label(self, 
                      text = "Synthèse du\nparsing des BDD", 
                      font = font_5)
    concat.place(x = POSITION_SELON_X_CHECK + 5 * mm_to_px(25, PPI) * SFW, y = mm_to_px(35, PPI) * SFH, anchor = 'center')
    self.TABLE.append(concat)
    
def _reset_year_and_launch_parsing_concat_dedup(self, corpus_year, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK, bibliometer_path):
    
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

    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    
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

    list_corpus_year = results[0]
    list_wos_rawdata = results[1]
    list_wos_parsing = results[2]
    list_scopus_rawdata = results[3]
    list_scopus_parsing = results[4]
    list_concatenation = results[5]
    #################################################################################
    
    answer_1 = messagebox.askokcancel('Information', f"Une procédure de synthèse a été lancée, continuer la procédure ?")
    if answer_1: # Alors on lance la synthèse
        
        # Vérification de la présence des fichiers
        if list_wos_parsing[list_corpus_year.index(corpus_year)] == False:
            messagebox.showwarning('Fichiers manquants', f"Warning : le fichier articles.dat de wos de l'année {corpus_year} n'est pas disponible. Veuillez effectuer le parsing pour cette année.")
            return

        if list_scopus_parsing[list_corpus_year.index(corpus_year)] == False:
            messagebox.showwarning('Fichiers manquants', f"Warning : le fichier articles.dat de scopus de l'année {corpus_year} n'est pas disponible. Veuillez effectuer le parsing pour cette année.")
            return
        if list_concatenation[list_corpus_year.index(corpus_year)]:

            answer_2 = messagebox.askokcancel('Information', f"La synthèse pour l'année {corpus_year} est déjà disponible, voulez-vous quand même l'effectuer ?")
            if answer_2: # Alors on effectue la synthèse
                # Setting the useful paths
                path_scopus_parsing = bibliometer_path / Path(corpus_year) / Path(scopus_path_alias) / Path(parsing_path_alias)
                path_scopus_rawdata = bibliometer_path / Path(corpus_year) / Path(scopus_path_alias) / Path(rawdata_path_alias) 
                path_wos_parsing = bibliometer_path / Path(corpus_year) / Path(wos_path_alias) / Path(parsing_path_alias)
                path_wos_rawdata = bibliometer_path / Path(corpus_year) / Path(wos_path_alias) / Path(rawdata_path_alias) 
                path_concat = bibliometer_path / Path(corpus_year) / Path(concat_path_alias)
                path_concat_parsing = path_concat / Path(parsing_path_alias)

                if not os.path.exists(path_concat_parsing):
                    if not os.path.exists(path_concat): os.mkdir(path_concat)
                    os.mkdir(path_concat_parsing)

                path_rational = bibliometer_path / Path(corpus_year) / Path(dedupli_path_alias)
                path_rational_parsing = path_rational / Path(parsing_path_alias)

                print(path_rational)
                print(path_rational_parsing)

                if not os.path.exists(path_rational_parsing):
                    if not os.path.exists(path_rational): os.mkdir(path_rational)
                    os.mkdir(path_rational_parsing)

                useful_path_list = [path_scopus_parsing, path_wos_parsing, path_concat_parsing, path_rational_parsing]    

                bau.parsing_concatenate_deduplicate(useful_path_list)

                path_to_folder = bibliometer_path / Path(corpus_year) / Path(FOLDER_NAMES['corpus']) / Path(FOLDER_NAMES['dedup']) / Path(FOLDER_NAMES['parsing'])
                bau.extend_author_institutions(path_to_folder, [('INES', 'France'), ('LITEN', 'France')])

                _update(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK)

                messagebox.showinfo('Information', f"La synthèse est terminée.")
            else:
                messagebox.showinfo('Information', f"La synthèse n'a pas été faite.")
        else:
            # Setting the useful paths
            path_scopus_parsing = bibliometer_path / Path(corpus_year) / Path(scopus_path_alias) / Path(parsing_path_alias)
            path_scopus_rawdata = bibliometer_path / Path(corpus_year) / Path(scopus_path_alias) / Path(rawdata_path_alias) 
            path_wos_parsing = bibliometer_path / Path(corpus_year) / Path(wos_path_alias) / Path(parsing_path_alias)
            path_wos_rawdata = bibliometer_path / Path(corpus_year) / Path(wos_path_alias) / Path(rawdata_path_alias) 
            path_concat = bibliometer_path / Path(corpus_year) / Path(concat_path_alias)
            path_concat_parsing = path_concat / Path(parsing_path_alias)

            if not os.path.exists(path_concat_parsing):
                if not os.path.exists(path_concat): os.mkdir(path_concat)
                os.mkdir(path_concat_parsing)

            path_rational = bibliometer_path / Path(corpus_year) / Path(dedupli_path_alias)
            path_rational_parsing = path_rational / Path(parsing_path_alias)

            print(path_rational)
            print(path_rational_parsing)

            if not os.path.exists(path_rational_parsing):
                if not os.path.exists(path_rational): os.mkdir(path_rational)
                os.mkdir(path_rational_parsing)

            useful_path_list = [path_scopus_parsing, path_wos_parsing, path_concat_parsing, path_rational_parsing]    

            bau.parsing_concatenate_deduplicate(useful_path_list)

            path_to_folder = bibliometer_path / Path(corpus_year) / Path(FOLDER_NAMES['corpus']) / Path(FOLDER_NAMES['dedup']) / Path(FOLDER_NAMES['parsing'])
            bau.extend_author_institutions(path_to_folder, [('INES', 'France'), ('LITEN', 'France')])

            _update(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK)

            messagebox.showinfo('Information', f"La synthèse est terminée.")

def _update(self, bibliometer_path, pos_x, pos_y, esp_ligne):

    """
    Description : 

    Uses the following globals :

    Args :

    Returns :

    """
    # 3rd party imports
    import tkinter as tk
    from tkinter import font as tkFont
    
    # Local imports
    from BiblioMeter_GUI.Useful_Classes import CheckBoxCorpuses
    
    from BiblioMeter_GUI.Coordinates import root_properties
    #from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PC

    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    
    from BiblioMeter_GUI.Globals_GUI import PPI
    
    win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(self)
    
    for i in range(len(self.CHECK)):
        self.CHECK[i].efface()

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
        tmp.place(x = pos_x, y = i*esp_ligne+pos_y)
        self.CHECK.append(tmp)

    _create_table(self, bibliometer_path, pos_x, pos_y, esp_ligne)
    
    self.OM_year_pc_1.destroy()
    

    #font_year_pc_1 = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    #label_year_pc_1 = tk.Label(self, text = TEXT_YEAR_PC, font = font_year_pc_1)#
    #label_year_pc_1.place(x = mm_to_px(10, PPI)*SFW, y = y_constru + mm_to_px(10, PPI)*SFH, anchor = "nw")
    
    var_year_pc_1 = tk.StringVar(self)
    var_year_pc_1.set(list_annee[-1])
    self.OM_year_pc_1 = tk.OptionMenu(self, var_year_pc_1, *list_annee)
    font_year_pc_1 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    self.OM_year_pc_1.config(font = font_year_pc_1)
    place_after(self.label_year_pc_1, self.OM_year_pc_1, dx = mm_to_px(1, PPI)*SFW, dy = -mm_to_px(1, PPI)*SFH)
    
    self.OM_year_pc_2.destroy()
    
    #font_year_pc_2 = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    #label_year_pc_2 = tk.Label(self, text = TEXT_YEAR_PC, font = font_year_pc_2)
    #label_year_pc_2.place(x = mm_to_px(10, PPI)*SFW, y = y_constru + mm_to_px(10, PPI)*SFH, anchor = "nw")
    
    var_year_pc_2 = tk.StringVar(self)
    var_year_pc_2.set(list_annee[-1])
    self.OM_year_pc_2 = tk.OptionMenu(self, var_year_pc_2, *list_annee)
    font_year_pc_2 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    self.OM_year_pc_2.config(font = font_year_pc_2)
    place_after(self.label_year_pc_2, self.OM_year_pc_2, dx = mm_to_px(1, PPI)*SFW, dy = -mm_to_px(1, PPI)*SFH)


def create_ParsingConcat(self, bibliometer_path, parent):

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
    from tkinter import font as tkFont

    # Local imports
    import BiblioAnalysis_Utils as bau
    
    from BiblioMeter_GUI.Coordinates import root_properties
        
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import str_size_mm
    
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    from BiblioMeter_GUI.Globals_GUI import GUI_DISP
    from BiblioMeter_GUI.Globals_GUI import ROOT_PATH
    from BiblioMeter_GUI.Globals_GUI import PPI
    
    win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(self)
    
    ### On récupère la présence ou non des fichiers #################################        
    results = existing_corpuses(bibliometer_path)

    list_annee = results[0]
    list_wos_rawdata = results[1]
    list_wos_parsing = results[2]
    list_scopus_rawdata = results[3]
    list_scopus_parsing = results[4]
    list_concatenation = results[5]
    #################################################################################
    
    # Zone Statut des fichiers de "parsing"
    
    # Liste des checkbox des corpuses
    self.CHECK = []
    self.TABLE = []
    
    from BiblioMeter_GUI.Coordinates import TEXT_STATUT
    font_statut = tkFont.Font(family = "Helvetica", size = font_size(14, min(SFW, SFWP)))
    label_statut = tk.Label(self, text = TEXT_STATUT, font = font_statut)
    label_statut.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(30, PPI)*SFH, anchor = "nw")
    
    ### Zone Construction des fichiers de "parsing" par BDD
    from BiblioMeter_GUI.Coordinates import TEXT_CONSTRU
    font_constru = tkFont.Font(family = "Helvetica", size = font_size(14, min(SFW, SFWP)))
    label_constru = tk.Label(self, text = TEXT_CONSTRU, font = font_constru)
    y_constru = mm_to_px(102, PPI)*SFH
    label_constru.place(x = mm_to_px(10, PPI)*SFW, y = y_constru, anchor = "nw")

    # Choix de l'année
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PC
    font_year_pc_1 = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    self.label_year_pc_1 = tk.Label(self, text = TEXT_YEAR_PC, font = font_year_pc_1)
    self.label_year_pc_1.place(x = mm_to_px(10, PPI)*SFW, y = y_constru + mm_to_px(10, PPI)*SFH, anchor = "nw")
    
    var_year_pc_1 = tk.StringVar(self)
    var_year_pc_1.set(list_annee[-1])
    self.OM_year_pc_1 = tk.OptionMenu(self, var_year_pc_1, *list_annee)
    font_year_pc_1 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    self.OM_year_pc_1.config(font = font_year_pc_1)
    place_after(self.label_year_pc_1, self.OM_year_pc_1, dx = mm_to_px(1, PPI)*SFW, dy = -mm_to_px(1, PPI)*SFH)
    
    # Choix de la BDD
    from BiblioMeter_GUI.Coordinates import TEXT_BDD_PC
    font_bdd_pc_1 = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    label_bdd_pc_1 = tk.Label(self, text = TEXT_BDD_PC, font = font_bdd_pc_1)
    place_after(self.OM_year_pc_1, label_bdd_pc_1, dx = mm_to_px(15, PPI)*SFW, dy = mm_to_px(1, PPI)*SFH)
    
    var_bdd_pc_1 = tk.StringVar(self)
    var_bdd_pc_1.set('wos')
    OM_bdd_pc_1 = tk.OptionMenu(self, var_bdd_pc_1, *['wos','scopus'])
    font_bdd_pc_1 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    OM_bdd_pc_1.config(font = font_bdd_pc_1)
    place_after(label_bdd_pc_1, OM_bdd_pc_1, dx = mm_to_px(1, PPI)*SFW, dy = -mm_to_px(1, PPI)*SFH)
    
    # Lancement du parsing
    from BiblioMeter_GUI.Coordinates import TEXT_LAUNCH_PARSING
    font_launch_parsing = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    button_launch_parsing = tk.Button(self, 
                                      text = TEXT_LAUNCH_PARSING, 
                                      font = font_launch_parsing, 
                                      command = lambda: _data_parsing(self, 
                                                                      var_year_pc_1.get(), 
                                                                      var_bdd_pc_1.get(), 
                                                                      POSITION_SELON_X_CHECK, 
                                                                      POSITION_SELON_Y_CHECK, 
                                                                      ESPACE_ENTRE_LIGNE_CHECK, 
                                                                      bibliometer_path))
    place_after(OM_bdd_pc_1, button_launch_parsing, dx = mm_to_px(25, PPI)*SFW, dy = mm_to_px(0.2, PPI)*SFH)
    
    ### Zone Synthèse des fichiers de parsing de toutes les BDD
    from BiblioMeter_GUI.Coordinates import TEXT_SYNTHESE
    font_synthese = tkFont.Font(family = "Helvetica", size = font_size(14, min(SFW, SFWP)))
    label_synthese = tk.Label(self, text = TEXT_SYNTHESE, font = font_synthese)
    y_synthese = mm_to_px(130, PPI)*SFH
    label_synthese.place(x = mm_to_px(10, PPI)*SFW, y = y_synthese, anchor = "nw")
    
    # Choix de l'année
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PC
    font_year_pc_2 = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    self.label_year_pc_2 = tk.Label(self, text = TEXT_YEAR_PC, font = font_year_pc_2)
    self.label_year_pc_2.place(x = mm_to_px(10, PPI)*SFW, y = y_synthese + mm_to_px(10, PPI)*SFH, anchor = "nw")
    
    var_year_pc_2 = tk.StringVar(self)
    var_year_pc_2.set(list_annee[-1])
    self.OM_year_pc_2 = tk.OptionMenu(self, var_year_pc_2, *list_annee)
    font_year_pc_2 = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    self.OM_year_pc_2.config(font = font_year_pc_2)
    place_after(self.label_year_pc_2, self.OM_year_pc_2, dx = mm_to_px(1, PPI)*SFW, dy = -mm_to_px(1, PPI)*SFH)
        
    # Lancement de la concatenation
    from BiblioMeter_GUI.Coordinates import TEXT_LAUNCH_SYNTHESE
    font_launch_concat = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    button_launch_concat = tk.Button(self, 
                                     text = TEXT_LAUNCH_SYNTHESE, 
                                     font = font_launch_concat, 
                                     command = lambda: _reset_year_and_launch_parsing_concat_dedup(self, 
                                                                                                   var_year_pc_2.get(), 
                                                                                                   POSITION_SELON_X_CHECK, 
                                                                                                   POSITION_SELON_Y_CHECK, 
                                                                                                   ESPACE_ENTRE_LIGNE_CHECK, 
                                                                                                   bibliometer_path))
    place_after(self.OM_year_pc_2, button_launch_concat, dx = mm_to_px(25, PPI)*SFW, dy = mm_to_px(0.2, PPI)*SFH)
    
    # Bouton pour actualiser la zone de stockage
    font_exist_button = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    exist_button = tk.Button(self, 
                             text = "Mettre à jour le statut des fichiers", 
                             font = font_exist_button, 
                             command = lambda: _update(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK))
    exist_button.place(x = mm_to_px(40, PPI)*SFW, y = mm_to_px(92, PPI)*SFH, anchor = 'n')
    
    # Placement de CHECKBOXCORPUSES :
    POSITION_SELON_X_CHECK = mm_to_px(70, PPI) * SFW
    POSITION_SELON_Y_CHECK = mm_to_px(45, PPI) * SFH
    ESPACE_ENTRE_LIGNE_CHECK = mm_to_px(10, PPI) * SFH
    _update(self, bibliometer_path, POSITION_SELON_X_CHECK, POSITION_SELON_Y_CHECK, ESPACE_ENTRE_LIGNE_CHECK)
    
    def _launch_exit():
        answer_1 = messagebox.askokcancel('Information', f"Vous allez fermer BiblioMeter, rien ne sera perdu et vous pourrez reprendre votre travail plus tard, souhaitez-vous fermer BiblioMeter ?")
        if answer_1:
            parent.destroy()
        
    # Boutou pour sortir de la page
    font_button_quit = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    button_quit = tk.Button(self, 
                            text = "Mettre en pause", 
                            font = font_button_quit, 
                            command = lambda: _launch_exit()).place(x = mm_to_px(193, PPI)*SFW, y = mm_to_px(145, PPI)*SFH, anchor = 'n')