__all__ = ['create_ParsingInstitution']

def create_ParsingInstitution(self, bibliometer_path, parent):
    
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
    # New imports to sort
    
    from BiblioMeter_GUI.Coordinates import root_properties
    
    from tkinter import font as tkFont

    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px

    from BiblioMeter_GUI.Globals_GUI import DISPLAYS
    from BiblioMeter_GUI.Globals_GUI import GUI_DISP
    from BiblioMeter_GUI.Globals_GUI import PPI
    
    win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(self)

    # Standard library imports
    import os
    from pathlib import Path
    from datetime import datetime

    # 3rd party imports
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox
    import pandas as pd
    from datetime import date

    # Local imports
    import BiblioAnalysis_Utils as bau
    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME

    from BiblioMeter_FUNCTS.BiblioMeter_MergeEffectif import recursive_year_search
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import filtrer_par_departement
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import consolidation_homonyme
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ajout_OTP
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ajout_IF
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import concat_listes_consolidees
    
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import place_bellow
    from BiblioMeter_GUI.Useful_Functions import encadre_RL
    from BiblioMeter_GUI.Useful_Functions import encadre_UD

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PI
    from BiblioMeter_GUI.Coordinates import X_YEAR_PI
    from BiblioMeter_GUI.Coordinates import Y_YEAR_PI

    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_1
    from BiblioMeter_GUI.Coordinates import SOUS_TEXT_ETAPE_1
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_1
    from BiblioMeter_GUI.Coordinates import FONT_SOUS_ETAPE_1
    from BiblioMeter_GUI.Coordinates import X_ETAPE_1
    from BiblioMeter_GUI.Coordinates import Y_ETAPE_1
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_1
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_1
    
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_2
    from BiblioMeter_GUI.Coordinates import SOUS_TEXT_ETAPE_2
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_2
    from BiblioMeter_GUI.Coordinates import FONT_SOUS_ETAPE_2
    from BiblioMeter_GUI.Coordinates import X_ETAPE_2
    from BiblioMeter_GUI.Coordinates import Y_ETAPE_2
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_2
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_2
    
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_3
    from BiblioMeter_GUI.Coordinates import SOUS_TEXT_ETAPE_3
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_3
    from BiblioMeter_GUI.Coordinates import FONT_SOUS_ETAPE_3
    from BiblioMeter_GUI.Coordinates import X_ETAPE_3
    from BiblioMeter_GUI.Coordinates import Y_ETAPE_3
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_3
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_3
    
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_4
    from BiblioMeter_GUI.Coordinates import SOUS_TEXT_ETAPE_4
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_4
    from BiblioMeter_GUI.Coordinates import FONT_SOUS_ETAPE_4
    from BiblioMeter_GUI.Coordinates import X_ETAPE_4
    from BiblioMeter_GUI.Coordinates import Y_ETAPE_4
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_4
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_4
    
    from BiblioMeter_GUI.Coordinates import TEXT_AFFI
    from BiblioMeter_GUI.Coordinates import X_AFFI
    from BiblioMeter_GUI.Coordinates import Y_AFFI
    
    from BiblioMeter_GUI.Coordinates import TEXT_CROISEMENT
    from BiblioMeter_GUI.Coordinates import FONT_CROISEMENT
    from BiblioMeter_GUI.Coordinates import X_CROISEMENT
    from BiblioMeter_GUI.Coordinates import Y_CROISEMENT

    from BiblioMeter_GUI.Coordinates import TEXT_CROISEMENT_L
    from BiblioMeter_GUI.Coordinates import FONT_CROISEMENT_L
    from BiblioMeter_GUI.Coordinates import FORMAT_CROISEMENT_L

    from BiblioMeter_GUI.Coordinates import FONT_GOBACK
    
    from BiblioMeter_GUI.Coordinates import TEXT_CONSOLIDATION
    from BiblioMeter_GUI.Coordinates import FONT_CONSOLIDATION
    from BiblioMeter_GUI.Coordinates import X_CONSOLIDATION
    from BiblioMeter_GUI.Coordinates import Y_CONSOLIDATION
    
    from BiblioMeter_GUI.Coordinates import TEXT_OTP
    from BiblioMeter_GUI.Coordinates import FONT_OTP

    from BiblioMeter_GUI.Coordinates import TEXT_FINALE
    from BiblioMeter_GUI.Coordinates import FONT_FINALE

    from BiblioMeter_GUI.Coordinates import FONT_CONCAT
    
    from BiblioMeter_GUI.Coordinates import TEXT_MAJ_IF
    from BiblioMeter_GUI.Coordinates import FONT_MAJ_IF

    ### DECORATION DE LA PAGE
    # - Canvas
    fond = tk.Canvas(self, width = win_width, height = win_height)
    fond.place(x = 0, y = 0)
    
    # - Labels
    font_etape = tkFont.Font(family = "Helvetica", size = font_size(14, min(SFW, SFWP)))
    etape_1 = tk.Label(self, 
                       text = TEXT_ETAPE_1, 
                       justify = FORMAT_TEXT_ETAPE_1, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_1)
    etape_1.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(40, PPI)*SFH)
    
    #sous_text_etape_1 = tk.Label(self, text = SOUS_TEXT_ETAPE_1, justify = FORMAT_TEXT_ETAPE_1, font = FONT_SOUS_ETAPE_1)
    #place_after(etape_1, sous_text_etape_1, dx = 2, dy = 2)
    
    etape_2 = tk.Label(self, 
                       text = TEXT_ETAPE_2, 
                       justify = FORMAT_TEXT_ETAPE_2, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_2)
    etape_2.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(74, PPI)*SFH)
    
    #sous_text_etape_2 = tk.Label(self, text = SOUS_TEXT_ETAPE_2, justify = FORMAT_TEXT_ETAPE_2, font = FONT_SOUS_ETAPE_2)
    #place_after(etape_2, sous_text_etape_2, dx = 2, dy = 4)
    
    etape_3 = tk.Label(self, 
                       text = TEXT_ETAPE_3, 
                       justify = FORMAT_TEXT_ETAPE_3, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_3)
    etape_3.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(101, PPI)*SFH)

    #sous_text_etape_3 = tk.Label(self, text = SOUS_TEXT_ETAPE_3, justify = FORMAT_TEXT_ETAPE_3, font = FONT_SOUS_ETAPE_3)
    #place_after(etape_3, sous_text_etape_3, dx = 2, dy = 4)
    
    etape_4 = tk.Label(self, 
                       text = TEXT_ETAPE_4, 
                       justify = FORMAT_TEXT_ETAPE_4, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_4)
    etape_4.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(129, PPI)*SFH)

    #sous_text_etape_4 = tk.Label(self, text = SOUS_TEXT_ETAPE_4, justify = FORMAT_TEXT_ETAPE_4, font = FONT_SOUS_ETAPE_4)
    #place_after(etape_4, sous_text_etape_4, dx = 2, dy = 4)
    
    ### Choose which year you want to be working with #############################################################################################################
    years_list = five_last_available_years(bibliometer_path)
    variable_years = tk.StringVar(self)
    variable_years.set(years_list[0])
    
        # Création de l'option button des années
    font_OptionButton_years = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    OptionButton_years = tk.OptionMenu(self, variable_years, *years_list)
    OptionButton_years.config(font = font_OptionButton_years)
    
        # Création du label
    font_Label_years = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    Label_years = tk.Label(self, 
                           text = TEXT_YEAR_PI, 
                           font = font_Label_years)
    Label_years.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(26, PPI)*SFH)
    
    place_after(Label_years, OptionButton_years, dy = -6)
    encadre_RL(fond, Label_years, OptionButton_years, ds = 5)
    ###############################################################################################################################################################
    
    
    ### Bouton qui va permettre d'utiliser seeting_secondary_inst_filter sur un corpus concatené ##################################################################
    #Button_affi = tk.Button(self, text = TEXT_AFFI, command = lambda: _setting_extend())
    #place_after(Label_years, Button_affi, dx = 400, dy = -6)
    #Button_affi.place(x = X_AFFI, y = Y_AFFI)
    ###############################################################################################################################################################
    
    def _setting_extend():

        """
        Description :

        Uses the following globals :

        Args :

        Returns :
        """

        # Setting path_to_folder
        path_to_folder = bibliometer_path / Path(variable_years.get()) / Path(FOLDER_NAMES['corpus']) / Path(FOLDER_NAMES['dedup']) / Path(FOLDER_NAMES['parsing'])
        
        ### On récupère la présence ou non des fichiers #################################        
        results = existing_corpuses(bibliometer_path)

        list_corpus_year = results[0]
        list_wos_rawdata = results[1]
        list_wos_parsing = results[2]
        list_scopus_rawdata = results[3]
        list_scopus_parsing = results[4]
        list_concatenation = results[5]
        #################################################################################
        
        if list_wos_parsing[list_corpus_year.index(variable_years.get())] == False:
            messagebox.showwarning('Fichiers manquants', f"Warning : le fichier authorsinst.dat de wos de l'année {variable_years.get()} n'est pas disponible.\nVeuillez effectuer le parsing avant de parser les instituts")
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

        label = tk.Label(newWindow, text="Selectionner les\ninstitutions", font = ("Helvetica", 20))
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
            
        # TO DO : Nommer la variable_years dans la commande
        
        button = tk.Button(newWindow, text ="Lancer le parsing des institutions", 
                           command = lambda: launch())
        button.place(anchor = 'n', relx = 0.5, rely = 0.9)
    
        def launch():
                        
            bau.extend_author_institutions(path_to_folder, [(x.split(':')[1].strip(),x.split(':')[0].strip()) for x in [my_listbox.get(i) for i in my_listbox.curselection()]])
            
            messagebox.showinfo('Information', f"Le parsing des institutions sélectionnées a été efectué.")
            
            newWindow.destroy()
            
    ### Choix du nombre d'année du recursive_year_search
    font_croisement = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Label_croisement = tk.Label(self, 
                     text = TEXT_CROISEMENT_L, 
                     font = font_croisement, 
                     justify = FORMAT_CROISEMENT_L)
    
    place_bellow(etape_1, Label_croisement, dy = mm_to_px(5, PPI)*SFH)

    
    go_back_years_list_rh = [i for i in range(1,date.today().year-2009)]
    go_back_years = tk.StringVar(self)
    go_back_years.set(go_back_years_list_rh[4])
    
        # Création de l'option button des années
    OptionButton_goback = tk.OptionMenu(self, go_back_years, *go_back_years_list_rh)
    OptionButton_goback.configure(font = font_croisement)
    
    #place_after(Label_croisement, OptionButton_goback, dy = -mm_to_px(1, PPI)*SFH)
    
    ### Bouton qui va permettre d'utiliser recursive_year_search sur un corpus concatené ##################################################################
    Button_croisement = tk.Button(self, 
                       text = TEXT_CROISEMENT,
                       font = font_croisement, 
                       command = lambda: _launch_recursive_year_search())
    
    place_bellow(Label_croisement, Button_croisement, dx = mm_to_px(10, PPI)*SFW, dy = mm_to_px(-5, PPI)*SFH)
    #Button_croisement.place(x = X_CROISEMENT, y = Y_CROISEMENT)
    
    Label_croisement.destroy()
    
    def _launch_recursive_year_search():
        
        answer_1 = messagebox.askokcancel('Information', f"Une procédure de croisement des publications avec les effectifs LITEN a été lancée, continuer ?\nAttention cette opération peut prendre plusieurs minutes, ne pas fermer BiblioMeter pendant ce temps.")
        if answer_1:  
            if os.path.exists(Path(bibliometer_path) / Path(variable_years.get()) / Path(STOCKAGE_ARBORESCENCE['general'][0]) / Path(SUBMIT_FILE_NAME)):
                if messagebox.askokcancel('Information', f"Le croisement pour l'année {variable_years.get()} est déjà disponible, voulez-vous quand même l'effectuer ?"):
                    try:
                        recursive_year_search(Path(bibliometer_path) / 
                                              Path(variable_years.get()) / 
                                              Path(FOLDER_NAMES['corpus']) / 
                                              Path(FOLDER_NAMES['dedup']) / 
                                              Path(FOLDER_NAMES['parsing']),
                                              Path(bibliometer_path) / 
                                              Path(variable_years.get()) / 
                                              Path(STOCKAGE_ARBORESCENCE['general'][0]), 
                                              Path(bibliometer_path) / 
                                              Path(STOCKAGE_ARBORESCENCE['effectif'][0]) / 
                                              Path(STOCKAGE_ARBORESCENCE['effectif'][1]),
                                              Path(bibliometer_path) / 
                                              Path(STOCKAGE_ARBORESCENCE['effectif'][0]) / 
                                              Path(STOCKAGE_ARBORESCENCE['effectif'][2]),
                                              Path(bibliometer_path),
                                              variable_years.get(), 
                                              go_back_years.get())

                        messagebox.showinfo('Information', f"Le croisement est terminé, vous pouvez maintenant passer aux étapes suivantes en les effectuant dans l'ordre.")
                    except FileNotFoundError:
                        messagebox.showwarning('Fichier manquant', f"Le croisement des publications n'a pas pu être effectué. La synthèse de l'année {variable_years.get()} n'est pas disponible. Veuillez revenir à l'onglet précédent pour le faire.")
                    #except:
                        #messagebox.showwarning('Erreur inconnue', f"Une erreur inconnue est survenue, veuillez consulter la console et/ou contacter une personne capable de résoudre le problème.")
                else:
                    messagebox.showinfo('Information', f"Le croisement n'a pas été effectué.")
            else:
                try:
                    recursive_year_search(Path(bibliometer_path) / 
                                          Path(variable_years.get()) / 
                                          Path(FOLDER_NAMES['corpus']) / 
                                          Path(FOLDER_NAMES['dedup']) / 
                                          Path(FOLDER_NAMES['parsing']),
                                          Path(bibliometer_path) / 
                                          Path(variable_years.get()) / 
                                          Path(STOCKAGE_ARBORESCENCE['general'][0]), 
                                          Path(bibliometer_path) / 
                                          Path(STOCKAGE_ARBORESCENCE['effectif'][0]) / 
                                          Path(STOCKAGE_ARBORESCENCE['effectif'][1]),
                                          Path(bibliometer_path) / 
                                          Path(STOCKAGE_ARBORESCENCE['effectif'][0]) / 
                                          Path(STOCKAGE_ARBORESCENCE['effectif'][2]),
                                          Path(bibliometer_path),
                                          variable_years.get(), 
                                          go_back_years.get())

                    messagebox.showinfo('Information', f"Le croisement est terminé, vous pouvez maintenant passer aux étapes suivantes en les effectuant dans l'ordre.")
                except FileNotFoundError:
                    messagebox.showwarning('Fichier manquant', f"Le croisement des publications n'a pas pu être effectué. La synthèse de l'année {variable_years.get()} n'est pas disponible. Veuillez revenir à l'onglet précédent pour le faire.")
                #except:
                    #messagebox.showwarning('Erreur inconnue', f"Une erreur inconnue est survenue, veuillez consulter la console et/ou contacter une personne capable de résoudre le problème.")
        else:
            messagebox.showinfo('Information', f"Le croisement n'a pas été effectué.")
    
    ###########################################################################################################################################################
    
    # Useful alias
    bdd_mensuelle_alias = STOCKAGE_ARBORESCENCE['general'][0]
    bdd_annuelle_alias = STOCKAGE_ARBORESCENCE['general'][1]
    OTP_path_alias = STOCKAGE_ARBORESCENCE['general'][3]
    Homonyme_path_alias = STOCKAGE_ARBORESCENCE['general'][4]
    R_path_alias = STOCKAGE_ARBORESCENCE['general'][5]
    submit_alias = SUBMIT_FILE_NAME
    
    # PREMIERE PARTIE : CONSOLIDATION  
    font_consolidation = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_mise_en_forme = tk.Button(self, 
                                     text = TEXT_CONSOLIDATION, 
                                     font = font_consolidation, 
                                     command = lambda: _launch_consolidation_homonyme())
    
    # Button_mise_en_forme.place(x = X_CONSOLIDATION, y = Y_CONSOLIDATION)
    place_bellow(etape_2, Button_mise_en_forme, dx = mm_to_px(10, PPI)*SFW, dy = mm_to_px(5, PPI)*SFH)

    
    def _launch_consolidation_homonyme():
        answer_1 = messagebox.askokcancel('Information', f"Une procédure de création du fichier résolution des homonymies a été lancée, continuer ?")
        if answer_1:
            if os.path.exists(Path(bibliometer_path) / Path(variable_years.get()) / Path(Homonyme_path_alias) / Path(f'Fichier Consolidation {variable_years.get()}.xlsx')):
                if messagebox.askokcancel('Information', f"Le fichier de consolidation pour l'année {variable_years.get()} est déjà disponible, voulez-vous quand même l'effectuer ?"):
                    try:
                        consolidation_homonyme(Path(bibliometer_path) / 
                                              Path(variable_years.get()) / 
                                              Path(bdd_mensuelle_alias) / 
                                              Path(submit_alias), 
                                              Path(bibliometer_path) / 
                                              Path(variable_years.get()) / 
                                              Path(Homonyme_path_alias) / 
                                              Path(f'Fichier Consolidation {variable_years.get()}.xlsx'))

                        messagebox.showinfo('Information', f"""La procédure est terminée. Vous pouvez vous rendre dans\n"1 - Consolidations Homonymes", supprimer les homonymes et enregistrer le fichier sous le même nom.""")
                    except FileNotFoundError:
                        messagebox.showwarning('Fichier manquant', f"La procédure n'a pas pu être effectué. Le croisement des publications de l'année {variable_years.get()} n'est pas disponible. Veuillez revenir à l'étape précédente pour le faire.")
                    except:
                        messagebox.showwarning('Erreur inconnue', f"Une erreur inconnue est survenue, veuillez consulter la console et/ou contacter une personne capable de résoudre le problème.")
                else:
                    messagebox.showinfo('Information', f"La procédure n'a pas été effectuée.")
            else:
                try:
                    consolidation_homonyme(Path(bibliometer_path) / 
                                          Path(variable_years.get()) / 
                                          Path(bdd_mensuelle_alias) / 
                                          Path(submit_alias), 
                                          Path(bibliometer_path) / 
                                          Path(variable_years.get()) / 
                                          Path(Homonyme_path_alias) / 
                                          Path(f'Fichier Consolidation {variable_years.get()}.xlsx'))

                    messagebox.showinfo('Information', f"""La procédure est terminée. Vous pouvez vous rendre dans\n"1 - Consolidations Homonymes", supprimer les homonymes et enregistrer le fichier sous le même nom.""")
                except FileNotFoundError:
                    messagebox.showwarning('Fichier manquant', f"La procédure n'a pas pu être effectué. Le croisement des publications de l'année {variable_years.get()} n'est pas disponible. Veuillez revenir à l'étape précédente pour le faire.")
                except:
                    messagebox.showwarning('Erreur inconnue', f"Une erreur inconnue est survenue, veuillez consulter la console et/ou contacter une personne capable de résoudre le problème.")
        else:
            messagebox.showinfo('Information', f"La procédure n'a pas été effectuée.")
    
    # DEUXIEME PARTIE : DEFINITION DE L'OTP
    font_OTP = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_OTP = tk.Button(self, 
                           text = TEXT_OTP, 
                           font = font_OTP,  
                           command = lambda: _launch_ajout_OTP())
    
    place_bellow(etape_3, Button_OTP, dx = mm_to_px(10, PPI)*SFW, dy = mm_to_px(5, PPI)*SFH)
    #encadre_UD(fond, etape_3, Button_OTP, "black", dn = 5, de = 5000, ds = -22, dw = 5000)
    
    def _launch_ajout_OTP():
        answer_1 = messagebox.askokcancel('Information', f"Une procédure de création des quatre fichiers permettant l'ajout des OTP a été lancée, continuer ?")
        if answer_1:
            try:
                ajout_OTP(Path(bibliometer_path) / 
                          Path(variable_years.get()) / 
                          Path(Homonyme_path_alias) / 
                          Path(f'Fichier Consolidation {variable_years.get()}.xlsx'), 
                          Path(bibliometer_path) / 
                          Path(variable_years.get()) / 
                          Path(OTP_path_alias))

                messagebox.showinfo('Information', f"""Les fichiers OTP ont été créés dans "2 - OTP". Vous pouvez vous y rendre pour les remplir en indiquant le bon OTP. Veuillez enregistrer le document sous le nom fichier_ajout_OTP_XXXX_ok une fois chose faite.""")
            except FileNotFoundError:
                messagebox.showwarning('Fichier manquant', f"La procédure n'a pas pu être effectué. Le fichier résolution des homonymies de l'année {variable_years.get()} n'est pas disponible. Veuillez revenir à l'étape précédente pour le faire.")
            except:
                messagebox.showwarning('Erreur inconnue', f"Une erreur inconnue est survenue, veuillez consulter la console et/ou contacter une personne capable de résoudre le problème.")
    
    # TROISIEME PARTIE : CONSTRUCTION DU FICHIER FINAL  
    # Buton pour creer fichier excel d'une filtre par département
    font_finale = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_finale = tk.Button(self, 
                              text = "Lancer la création du fichier de la liste consolidée des publications", 
                              font = font_finale, 
                              command = lambda: _launch_filtrer_par_departement())
    
    place_bellow(etape_4, Button_finale, dx = mm_to_px(10, PPI)*SFW, dy = mm_to_px(5, PPI)*SFH)

    def _launch_filtrer_par_departement():
        answer_1 = messagebox.askokcancel('Information', f"Une procédure de création du fichier de la liste consolidée des publications a été lancée, continuer ?")
        if answer_1:
            try:
                from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import FILE_NAMES

                a = filtrer_par_departement(Path(bibliometer_path) / 
                                            Path(variable_years.get()) / 
                                            Path(OTP_path_alias), 
                                            Path(bibliometer_path) / 
                                            Path(variable_years.get()) / 
                                            Path(R_path_alias) / 
                                            Path(f"""{FILE_NAMES['liste conso']} {variable_years.get()}.xlsx"""))
        
                if a:
                    messagebox.showinfo('Information', f"""La liste consolidée a été créé, vous pouvez la retrouver dans "3 - Résultats finaux".""")
                    
                    # Concaténer avec les années disponibles
                    concat_listes_consolidees(bibliometer_path, years_list, R_path_alias, bdd_annuelle_alias)
                    
                    messagebox.showinfo('Information', f"""De plus, une concatenation des listes consolidées des différentes années disponibles a été faite. Vous pouvez retrouver le document dans "BDD multi annuelle".""")
                    
                else:
                    messagebox.showwarning('Fichier manquant', f"""La création de la liste consolidée n'a pas pu être faite, il manque un fichier OTP. Vérifiez bien que les fichiers soient au bon emplacement (2 - OTP) et sous le bon nom "fichier_ajout_OTP_XXXX_ok". Veuillez revenir à l'étape précédente pour les créer si besoin.""")
                        
            except FileNotFoundError:
                messagebox.showwarning('Fichier manquant', f"""La création de la liste consolidée n'a pas pu être faite, il manque un fichier OTP. Vérifiez bien que les fichiers soient au bon emplacement (2 - OTP) et sous le bon nom "fichier_ajout_OTP_XXXX_ok". Veuillez revenir à l'étape précédente pour les créer si besoin.""")
            except:
                messagebox.showwarning('Erreur inconnue', f"Une erreur inconnue est survenue, veuillez consulter la console et/ou contacter une personne capable de résoudre le problème.")
                

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