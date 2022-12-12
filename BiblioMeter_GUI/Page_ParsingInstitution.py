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

    # Standard library imports
    import os
    from pathlib import Path
    from datetime import datetime

    # 3rd party imports
    from datetime import date
    import pandas as pd
    import tkinter as tk
    from tkinter import font as tkFont
    from tkinter import filedialog
    from tkinter import messagebox
    
    # Local imports
    import BiblioAnalysis_Utils as bau
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    
    from BiblioMeter_FUNCTS.BiblioMeter_MergeEffectif import recursive_year_search
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ajout_OTP
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ajout_IF
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import concat_listes_consolidees
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import consolidation_homonyme
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import filtrer_par_departement
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import maj_rh
    
    from BiblioMeter_GUI.Coordinates import root_properties
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PC
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PI
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_1
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_1
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_1
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_1
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_2
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_2
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_2
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_2
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_3
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_3
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_3
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_3
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_4
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_4
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_4
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_4
    from BiblioMeter_GUI.Coordinates import TEXT_CROISEMENT
    from BiblioMeter_GUI.Coordinates import FONT_CROISEMENT
    from BiblioMeter_GUI.Coordinates import TEXT_CROISEMENT_L
    from BiblioMeter_GUI.Coordinates import FORMAT_CROISEMENT_L
    from BiblioMeter_GUI.Coordinates import TEXT_CONSOLIDATION
    from BiblioMeter_GUI.Coordinates import TEXT_OTP
    from BiblioMeter_GUI.Coordinates import FONT_OTP
    from BiblioMeter_GUI.Coordinates import FONT_CONCAT

    from BiblioMeter_GUI.Globals_GUI import ARCHI_BDD_MULTI_ANNUELLE
    from BiblioMeter_GUI.Globals_GUI import ARCHI_RH
    from BiblioMeter_GUI.Globals_GUI import ARCHI_SECOURS
    from BiblioMeter_GUI.Globals_GUI import ARCHI_YEAR
    from BiblioMeter_GUI.Globals_GUI import PPI
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME
    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Useful_Functions import encadre_RL
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import place_bellow

    
    win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(self)
    
    # Useful alias
    bdd_mensuelle_alias = ARCHI_YEAR["bdd mensuelle"]
    bdd_annuelle_alias = ARCHI_BDD_MULTI_ANNUELLE["root"]
    OTP_path_alias = ARCHI_YEAR["OTP"]
    Homonyme_path_alias = ARCHI_YEAR["consolidation"]
    R_path_alias = ARCHI_YEAR["resultats"]
    corpus_alias = ARCHI_YEAR['corpus']
    dedup_alias = ARCHI_YEAR['dedup']
    parsing_alias = ARCHI_YEAR['parsing']
    submit_alias = ARCHI_YEAR["submit file name"]
    listing_alias = ARCHI_RH["root"]
    effectif_folder_name_alias = ARCHI_RH["effectifs"]
    effectif_file_name_alias = ARCHI_RH["effectifs file name"]
    secours_alias = ARCHI_SECOURS["root"]
    
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
    
    etape_2 = tk.Label(self, 
                       text = TEXT_ETAPE_2, 
                       justify = FORMAT_TEXT_ETAPE_2, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_2)
    etape_2.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(74, PPI)*SFH)
    
    etape_3 = tk.Label(self, 
                       text = TEXT_ETAPE_3, 
                       justify = FORMAT_TEXT_ETAPE_3, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_3)
    etape_3.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(101, PPI)*SFH)
    
    etape_4 = tk.Label(self, 
                       text = TEXT_ETAPE_4, 
                       justify = FORMAT_TEXT_ETAPE_4, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_4)
    etape_4.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(129, PPI)*SFH)
    
    ### Choose which year you want to be working with #############################################################################################################
    years_list = five_last_available_years(bibliometer_path)
    variable_years = tk.StringVar(self)
    variable_years.set(years_list[-1])
    
        # Création de l'option button des années
    self.font_OptionButton_years = tkFont.Font(family = "Helvetica", size = font_size(11, min(SFW, SFWP)))
    self.OptionButton_years = tk.OptionMenu(self, variable_years, *years_list)
    self.OptionButton_years.config(font = self.font_OptionButton_years)
    
        # Création du label
    self.font_Label_years = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    self.Label_years = tk.Label(self, 
                           text = TEXT_YEAR_PI, 
                           font = self.font_Label_years)
    self.Label_years.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(26, PPI)*SFH)
    
    place_after(self.Label_years, self.OptionButton_years, dy = -6)
    encadre_RL(fond, self.Label_years, self.OptionButton_years, ds = 5)
    ###############################################################################################################################################################
    
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
    
    ### Bouton qui va permettre d'utiliser recursive_year_search sur un corpus concatené ##################################################################
    Button_croisement = tk.Button(self, 
                       text = TEXT_CROISEMENT,
                       font = font_croisement, 
                       command = lambda: _launch_recursive_year_search())
    
    check_effectif_var = tk.IntVar()
    check_effectif_box = tk.Checkbutton(self, text = "Oui (coché) / Non (non coché)", variable = check_effectif_var, onvalue = 1, offvalue = 0)
    
    font_check = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Label_check = tk.Label(self, text = "Mettre à jour le fichier RH avant le croisement ?", font = font_check, justify = 'left')

    place_bellow(Label_croisement, Label_check, dx = mm_to_px(10, PPI)*SFW, dy = mm_to_px(-8, PPI)*SFH)
    place_bellow(Label_check, Button_croisement, dy = mm_to_px(5, PPI)*SFH)
    place_after(Label_check, check_effectif_box)
    
    Label_croisement.destroy() # car on ne l'autorise plus pour le moment
    
    def _launch_recursive_year_search():
        
        # Import et alias important
        import os
        import shutil
        import pandas
        
        if check_effectif_var.get():
            # Lancement de la fonction MAJ Effectif
            answer = messagebox.askokcancel('Information', f"Le fichier des effectifs LITEN va être mis à jour. Après cette mise à jour, la procédure normale reprendra et il vous faudra répondre aux messages pop-up comme quand vous ne faites pas la mise à jour des effectifs LITEN.")
            if answer:
                maj_rh(bibliometer_path)
                messagebox.showinfo('Information', f"La mise à jour a été effectuée. La procédure normale de croisement va reprendre.")
            else:
            # Arrêt de la procédure
                messagebox.showinfo('Information', f"La mise à jour n'a pas été effectuée, et la procédure de croisement non plus.")
                return
    
        path_all_effectifs = Path(bibliometer_path) / Path(listing_alias) / Path(effectif_folder_name_alias) / Path(effectif_file_name_alias)
        
        def _annee_croisement(corpus_year):
    
            in_path = path_all_effectifs
            df = pandas.read_excel(in_path, sheet_name = None)

            annees_dispo = [int(x) for x in list(df.keys())]

            annees_a_verifier = [int(corpus_year) - int(go_back_years.get()) + i + 1 for i in range(int(go_back_years.get()))]
            annees_verifiees = list()

            for i in annees_a_verifier:
                if i in annees_dispo:
                    annees_verifiees.append(i)

            if len(annees_verifiees) > 0:
                return annees_verifiees
            else:
                return None
                
        # Dans l'ordre, je vérifie l'existence du fichier All_effectifs.xlsx
        if os.path.exists(path_all_effectifs):
            # Si disponible, il faut afficher les années disponibles
            df_effectifs = pd.read_excel(path_all_effectifs, sheet_name = None)
            # Vérifier les années disponibles
            annees_disponibles = _annee_croisement(variable_years.get())
            if annees_disponibles == None:
                messagebox.showwarning('Information', f"Il n'y a pas suffisament d'années disponibles dans le fichier effectifs LITEN pour effectuer le croisement. Procédure annulée.")
                return
        else:
            answer_2 = messagebox.askokcancel('Fichier manquant', f"""Le fichier {effectif_file_name_alias} n'est pas présent à l'emplacement attribué. Voulez-vous effectuer une copie de la dernière sauvegarde en l'état du fichier, et continuer avec la procédure ?""")
            if answer_2:
                # Alors comme c'est oui, il faut aller chercher le fichier et le copier au bon endroit
                filePath = shutil.copy(bibliometer_path / Path(secours_alias) / Path (effectif_file_name_alias), path_all_effectifs)
                
                df_effectifs = pd.read_excel(path_all_effectifs, sheet_name = None)
                # Vérifier les années disponibles
                annees_disponibles = _annee_croisement(variable_years.get())
                if annees_disponibles == None: # Si pas assez d'année disponible, alors arrêter la procédure
                    messagebox.showwarning('Information', f"Il n'y a pas suffisament d'années disponibles dans le fichier effectifs LITEN pour effectuer le croisement. Procédure annulée.")
                    return
            else:
                # Arrêt de la procédure
                messagebox.showinfo('Information', f"Le croisement n'a pas été effectué.")
                return
        # On passe directement ici si le document est disponible
        answer_1 = messagebox.askokcancel('Information', f"Une procédure de croisement des publications avec les effectifs LITEN des années : {', '.join([str(i) for i in annees_disponibles])} a été lancée, continuer ?\nAttention cette opération peut prendre plusieurs minutes, ne pas fermer BiblioMeter pendant ce temps.")
        if answer_1:  
            if os.path.exists(Path(bibliometer_path) / Path(variable_years.get()) / Path(bdd_mensuelle_alias) / Path(submit_alias)):
                if messagebox.askokcancel('Information', f"Le croisement pour l'année {variable_years.get()} est déjà disponible, voulez-vous quand même l'effectuer ?"):
                    try:
                        recursive_year_search(Path(bibliometer_path) / 
                                              Path(variable_years.get()) / 
                                              Path(corpus_alias) / 
                                              Path(dedup_alias) / 
                                              Path(parsing_alias),
                                              Path(bibliometer_path) / 
                                              Path(variable_years.get()) / 
                                              Path(bdd_mensuelle_alias), 
                                              path_all_effectifs,
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
                                          Path(corpus_alias) / 
                                          Path(dedup_alias) / 
                                          Path(parsing_alias),
                                          Path(bibliometer_path) / 
                                          Path(variable_years.get()) / 
                                          Path(bdd_mensuelle_alias), 
                                          path_all_effectifs, 
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
    
    # PREMIERE PARTIE : CONSOLIDATION  
    font_consolidation = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_mise_en_forme = tk.Button(self, 
                                     text = TEXT_CONSOLIDATION, 
                                     font = font_consolidation, 
                                     command = lambda: _launch_consolidation_homonyme())
    
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

                        messagebox.showwarning('Information', f"""La procédure est terminée. Veuillez vous rendre dans\n"1 - Consolidations Homonymes", supprimer les homonymes et enregistrer le fichier sous le même nom.\n\nVeuillez retirer le mauvais homonyme du fichier Excel en supprimant entièrement la ligne dans le fichier Excel. Les lignes à potentiellement surpprimer sont surlignées en jaune.""")
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