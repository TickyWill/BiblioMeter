__all__ = ['create_MultiAnnuelle']

def create_MultiAnnuelle(self, bibliometer_path, parent):
    
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

    from BiblioMeter_GUI.Coordinates import root_properties
    
    from tkinter import font as tkFont
    import tkinter as tk
    
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ajout_IF
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ISSN_manquant

    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import mm_to_px

    from BiblioMeter_GUI.Globals_GUI import DISPLAYS
    from BiblioMeter_GUI.Globals_GUI import GUI_DISP
    from BiblioMeter_GUI.Globals_GUI import PPI
    
    win_width, win_height, SFW, SFH, SFWP, SFHP = root_properties(self)
    
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import place_bellow
    from BiblioMeter_GUI.Useful_Functions import encadre_RL
    from BiblioMeter_GUI.Useful_Functions import encadre_UD
    
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_5
    from BiblioMeter_GUI.Coordinates import SOUS_TEXT_ETAPE_5
    from BiblioMeter_GUI.Coordinates import FONT_ETAPE_5
    from BiblioMeter_GUI.Coordinates import FONT_SOUS_ETAPE_5
    from BiblioMeter_GUI.Coordinates import X_ETAPE_5
    from BiblioMeter_GUI.Coordinates import Y_ETAPE_5
    from BiblioMeter_GUI.Coordinates import FORMAT_TEXT_ETAPE_5
    from BiblioMeter_GUI.Coordinates import UNDERLINE_ETAPE_5
    from BiblioMeter_GUI.Coordinates import HELP_ETAPE_5
    
    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years
    from BiblioMeter_GUI.Useful_Functions import existing_corpuses
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME
    
    from BiblioMeter_GUI.Coordinates import TEXT_FINALE
    from BiblioMeter_GUI.Coordinates import FONT_CONCAT
    
    from BiblioMeter_GUI.Coordinates import TEXT_MAJ_IF
    from BiblioMeter_GUI.Coordinates import FONT_MAJ_IF
    
    from BiblioMeter_GUI.Useful_Classes import LabelEntry_toFile
    
    from BiblioMeter_GUI.Useful_Functions import five_last_available_years

    from pathlib import Path
    
    import pandas as pd
    
    from tkinter import filedialog
    from tkinter import messagebox
    
    # Useful alias
    bdd_mensuelle_alias = STOCKAGE_ARBORESCENCE['general'][0]
    bdd_annuelle_alias = STOCKAGE_ARBORESCENCE['general'][1]
    OTP_path_alias = STOCKAGE_ARBORESCENCE['general'][3]
    Homonyme_path_alias = STOCKAGE_ARBORESCENCE['general'][4]
    R_path_alias = STOCKAGE_ARBORESCENCE['general'][5]
    submit_alias = SUBMIT_FILE_NAME
    
    years_list = five_last_available_years(bibliometer_path)
    
    font_etape = tkFont.Font(family = "Helvetica", size = font_size(14, min(SFW, SFWP)))
    etape_5 = tk.Label(self, 
                       text = TEXT_ETAPE_5, 
                       justify = FORMAT_TEXT_ETAPE_5, 
                       font = font_etape, 
                       underline = UNDERLINE_ETAPE_5)
    etape_5.place(x = mm_to_px(10, PPI)*SFW, y = mm_to_px(25, PPI)*SFH)
    
    

    #sous_text_etape_5 = tk.Label(self, text = SOUS_TEXT_ETAPE_5, justify = FORMAT_TEXT_ETAPE_5, font = FONT_SOUS_ETAPE_5)
    #place_after(etape_5, sous_text_etape_5, dx = 2, dy = 4)
    
    help_font_label = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    help_label = tk.Label(self, 
                          text = HELP_ETAPE_5, 
                          justify = "left", 
                          font = help_font_label)
    place_bellow(etape_5, help_label)
    

    # QUATRIEME PARTIE : CONCATENER LES 5 DERNIERS ANNEES
    font_Button_concat = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_concat = tk.Button(self, 
                              text = TEXT_FINALE, 
                              font = font_Button_concat, 
                              command = lambda: _concat_filtre_depar())
    
    #place_bellow(etape_5, Button_concat, dy = mm_to_px(5, PPI)*min(SFH, SFHP))
    #encadre_UD(fond, etape_5, Button_concat, "black", dn = 2, de = 5000, ds = 5000, dw = 5000)
    
    #Button_concat.place(anchor = 'center', relx = 0.5, rely = 0.75)
    
    def _concat_filtre_depar():
        
        '''
        '''
        
        from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import FILE_NAMES
        
        df_concat = pd.DataFrame()
    
        for i in range(len(years_list)):
            path = Path(bibliometer_path) / Path(years_list[i]) / Path(R_path_alias) / Path(f"""{FILE_NAMES['liste conso']} {years_list[i]}.xlsx""")
            df_inter = pd.read_excel(path)
            df_concat = df_concat.append(df_inter)
            
        date = str(datetime.now())[:16].replace(':', '')
        df_concat.to_excel(Path(bibliometer_path) / Path(bdd_annuelle_alias) / Path(f'{date}_concat_dep_{os.getlogin()}.xlsx'))
        
        messagebox.showinfo('Information', f"La concatenation des documents finaux des dernières années disponibles a été faite, vous pouvez la retrouver dans BDD Multi-annuelle")
        

    
    #place_after(Button_concat, Button_MAJ_IF, dx = mm_to_px(65, PPI)*min(SFW, SFWP), dy = -mm_to_px(0.5, PPI)*SFH)

    LE_font_label = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    LE_font_button = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    
    LabelEntry_MAJ_IF = LabelEntry_toFile(self, 
                                          text_label = f"", font_label = LE_font_label, font_button = LE_font_button, 
                                          width = int(90*min(SFW, SFWP)))
    #LabelEntry_MAJ_IF.set2("Selectionner un fichier ---->")
    
    place_bellow(help_label, LabelEntry_MAJ_IF, dx = mm_to_px(5, PPI)*SFW, dy = mm_to_px(5, PPI)*SFH)
    
    font_MAJ_IF = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_MAJ_IF = tk.Button(self, 
                              text = TEXT_MAJ_IF, 
                              font = font_MAJ_IF, 
                              command = lambda: _launch_maj_if())
    
    place_bellow(help_label, Button_MAJ_IF, dx = mm_to_px(0, PPI)*SFW, dy = mm_to_px(20, PPI)*SFH)
    
    def _launch_maj_if():
        
        '''
        '''
        # Import et alias important
        import os
        import shutil
        import pandas
        
        path_all_IF = Path(bibliometer_path) / Path(STOCKAGE_ARBORESCENCE['general'][7]) / Path(STOCKAGE_ARBORESCENCE['all IF'])
        
        # Vérifier que le fichier IF all years est là
        if os.path.exists(path_all_IF):
            df_IF = pd.read_excel(path_all_IF, sheet_name = None)
            messagebox.showinfo('Information', f"Les IF des publications des années {', '.join(list(df_IF.keys()))} vont être mis à jour avec les informations disponibles dans le fichier {STOCKAGE_ARBORESCENCE['all IF']}.")
            try:
                ajout_IF(LabelEntry_MAJ_IF.get(), LabelEntry_MAJ_IF.get(), path_all_IF, None)
                messagebox.showinfo('Information', f"Les IF ont été mis à jour.")
            except Exception as e:
                messagebox.showinfo('Information', f"Vous n'avez pas sélectionné de fichier à mettre à jour.")
                print(e)
                return
        else:
            answer_2 = messagebox.askokcancel('Fichier manquant', f"""Le fichier {STOCKAGE_ARBORESCENCE['all IF']} n'est pas présent à l'emplacement attribué. Voulez-vous effectuer une copie de la dernière sauvegarde en l'état du fichier, et continuer avec la procédure ?""")
            if answer_2:
                # Alors comme c'est oui, il faut aller chercher le fichier et le copier au bon endroit
                filePath = shutil.copy(bibliometer_path / Path(STOCKAGE_ARBORESCENCE['general'][8]) / Path (STOCKAGE_ARBORESCENCE['all IF']), path_all_IF)
                
                df_IF = pd.read_excel(path_all_IF, sheet_name = None)
                messagebox.showinfo('Information', f"Les IF des publications des années {', '.join(list(df_IF.keys()))} vont être mis à jour avec les informations disponibles dans le fichier {STOCKAGE_ARBORESCENCE['all IF']}.")
                try:
                    ajout_IF(LabelEntry_MAJ_IF.get(), LabelEntry_MAJ_IF.get(), path_all_IF, None)
                    messagebox.showinfo('Information', f"Les IF ont été mis à jour.")
                except Exception as e:
                    messagebox.showinfo('Information', f"Vous n'avez pas sélectionné de fichier à mettre à jour.")
                    print(e)
                    return
            else:
                # Arrêt de la procédure
                messagebox.showinfo('Information', f"La mise à jour n'a pas été faite.")
                return
            
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
    
    # RETROUVER LES ISSN MANQUANTS
    missing_ISSN_font_label = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    missing_ISSN_label = tk.Label(self, 
                                  text = """Dans cette partie, vous pouvez générer un fichier excel qui recherche les ISSN dont l'IF est inconnu.\nLe fichier sera nommé "ISSN_manquants", et sera disponible dans le dossier "Impact Factor".\nLa recherche se fera dans le document sélectionné au dessus.\nCe fichier peut-être utilisé pour remplir manuellement le fichier qui répertorie les IF année par année.""", 
                                  justify = "left", 
                                  font = missing_ISSN_font_label)
    place_bellow(Button_MAJ_IF, missing_ISSN_label, dx = mm_to_px(0, PPI)*SFW, dy = mm_to_px(20, PPI)*SFH)
    
    font_Button_missing_ISSN = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_missing_ISSN = tk.Button(self, 
                                    text = "Lancer la recherche des ISSN dont l'IF est manquant", 
                                    font = font_Button_missing_ISSN, 
                                    command = lambda: _launch_ISSN_manquant())
    
    place_bellow(missing_ISSN_label, Button_missing_ISSN, dx = mm_to_px(0, PPI)*SFW, dy = mm_to_px(5, PPI)*SFH)
    
    def _launch_ISSN_manquant():
        try:
            ISSN_manquant(bibliometer_path, LabelEntry_MAJ_IF.get())
            messagebox.showinfo('Information', f"""Les ISSN manquants ont été trouvés et mis dans un fichier excel dans le dossier "Impact Factor".""")
        except Exception as e:
            messagebox.showinfo('Information', f"Vous n'avez pas sélectionné de fichier.")
            print(e)#