__all__ = ['create_update_ifs']

# Nom de module et nom de fonctions à revoir !!!

def create_update_ifs(self, bibliometer_path, parent):
    
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
    import shutil
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    import tkinter as tk
    from tkinter import font as tkFont
    from tkinter import filedialog
    from tkinter import messagebox
    
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioGui import _mm_to_px
    
    # Local functions imports
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import update_if_multi
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import find_missing_if
    from BiblioMeter_GUI.Coordinates import root_properties
    from BiblioMeter_GUI.Useful_Classes import LabelEntry_toFile    
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import place_bellow
    from BiblioMeter_GUI.Useful_Functions import encadre_RL
    from BiblioMeter_GUI.Useful_Functions import encadre_UD
    
    # Globals imports
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_BACKUP 
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_IF
    from BiblioMeter_GUI.Coordinates import FONT_NAME
    from BiblioMeter_GUI.Coordinates import HELP_ETAPE_5
    from BiblioMeter_GUI.Coordinates import HELP_ETAPE_6
    from BiblioMeter_GUI.Coordinates import HELP_ETAPE_7
    from BiblioMeter_GUI.Coordinates import REF_ENTRY_NB_CHAR
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_5
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_6
    from BiblioMeter_GUI.Coordinates import TEXT_ETAPE_7
    from BiblioMeter_GUI.Coordinates import TEXT_MAJ_IF
    from BiblioMeter_GUI.Coordinates import TEXT_MISSING_IF
    from BiblioMeter_GUI.Coordinates import TEXT_PAUSE    
    from BiblioMeter_GUI.GUI_Globals import PPI
    
    # Internal functions

    def _get_if_info():
        if_df = pd.read_excel(all_if_path, sheet_name = None)
        if_years_list = ', '.join(list(if_df.keys()))
        if_most_recent_year = list(if_df.keys())[-1]
        return if_years_list, if_most_recent_year
    
    def _update_if_try(file_to_update_path):
        try:
            end_message = update_if_multi(file_to_update_path, file_to_update_path, all_if_path)
            print('\n',end_message)
            info_title = '- Information -'
            info_text  = "Les IFs ont été mis à jour."
            messagebox.showinfo(info_title, info_text)
        except KeyError:
            warning_title = "!!! ATTENTION : fichier incorrect !!!"
            warning_text = f"Le fichier excel des IFs présente un problème."
            warning_text += f"\n 1- Vérifiez le fichier  '{if_file_name_alias}' ;"
            warning_text += f"\n 2- Puis relancez la mise à jour des IFs."
            messagebox.showwarning(warning_title, warning_text)
        except Exception as e:
            #messagebox.showinfo('Information', f"Vous n'avez pas sélectionné de fichier à mettre à jour.")
            print(e)
            return
        
    def _launch_if_update():
        
        '''
        '''
        
        # Getting the file path to update with IFs
        file_to_update_path = file_select_entry.get()
        
        # Cheking availability of IF all years file
        all_if_status = os.path.exists(all_if_path)
        if all_if_status:
            if_years_list, _ = _get_if_info()
            info_title = '- Information -'
            info_text  = f"Les IFs des publications du fichier : \n '{file_to_update_path}' "
            info_text += f"\n\nvont être mis à jour avec les IFs des années : \n\n '{if_years_list}' "
            info_text += f"\n\ndu fichier :   '{if_file_name_alias}'."
            messagebox.showinfo(info_title, info_text)            
            _update_if_try(file_to_update_path)

        else:
            ask_title = "- Régénération du fichier des IFs -"
            ask_text  = f"Le fichier des IFs n'est pas disponible à l'emplacement attendu. "
            ask_text += f"\nL'utilisation de la dernière sauvegarde de secours est possible "
            ask_text += f"pour effectuer la mise à jour des IFs."
            ask_text += f"\nConfirmer cette utilisation ?"
            answer_2  = messagebox.askokcancel(ask_title, ask_text)
            if answer_2:
                # Alors comme c'est oui, il faut aller chercher le fichier et le copier au bon endroit
                filePath = shutil.copy(backup_if_file_path, all_if_path)
                if_years_list, _ = _get_if_info() 
                info_title = '- Information -'
                info_text  = f"Les IFs des publications du fichier : \n '{file_to_update_path}' "
                info_text += f"vont être mis à jour avec les IFs des années : \n\n '{if_years_list}' "
                info_text += f"\n\ndu fichier : '{if_file_name_alias}'."
                messagebox.showinfo(info_title, info_text) 
                _update_if_try(file_to_update_path)

            else:
                # Arrêt de la procédure
                info_title = '- Information -'
                info_text  = "La mise à jour des IFs a été abandonnée."
                messagebox.showinfo(info_title, info_text)
                return
            
    def _launch_missing_if():
        try:
            # Getting the file path to update with IFs
            file_to_update_path = file_select_entry.get()
            
            _, if_most_recent_year = _get_if_info()
            end_message = find_missing_if(bibliometer_path, file_to_update_path, if_most_recent_year)
            print('\n',end_message)
            info_title = '- Information -'
            info_text  = f"La liste des journaux dont l'IF est manquant a été construite."
            info_text += f"\nElle est disponible dans le dossier : \n '{if_root_folder_path}'"
            info_text += f"\n\nsous le nom de fichier :   '{if_manquants_file_alias}'."
            info_text += f"\n\nCette liste peut-être utilisée pour rechercher les IFs manquants sur la toile "
            info_text += f"\n\net compléter manuellement le fichier :  '{if_file_name_alias}'."
            messagebox.showinfo(info_title, info_text)
        except KeyError:
            warning_title = "!!! ATTENTION : fichier incorrect !!!"
            warning_text  = f"Le fichier à mettre à jour présente un problème."
            warning_text += f"\n 1- Vérifiez le fichier sélectionné pour la mise à jour des IFs ;"
            warning_text += f"\n 2- Puis relancez la recherche des IFs manquants."                         
            messagebox.showwarning(warning_title, warning_text)            
        except Exception as e:
            warning_title = "!!! ATTENTION : pas d'identification de fichier !!!"
            warning_text  = f"Le fichier à mettre à jour n'est pas défini."
            warning_text += f"\n 1- Vérifiez le fichier sélectionné pour la mise à jour des IFs ;"
            warning_text += f"\n 2- Puis relancez la recherche des IFs manquants."                         
            messagebox.showwarning(warning_title, warning_text)            
            print(e)    
            
    def _launch_exit():
        message =  "Vous allez fermer BiblioMeter. "
        message += "\nRien ne sera perdu et vous pourrez reprendre le traitement plus tard."
        message += "\n\nSouhaitez-vous faire une pause dans le traitement ?"
        answer_1 = messagebox.askokcancel('Information', message)
        if answer_1:
            parent.destroy()
            
    # Getting useful window sizes and scale factors depending on displays properties
    sizes_tuple   = root_properties(self)
    win_width_px  = sizes_tuple[0]    # unused here
    win_height_px = sizes_tuple[1]    # unused here
    width_sf_px   = sizes_tuple[2] 
    height_sf_px  = sizes_tuple[3]    # unused here
    width_sf_mm   = sizes_tuple[4]
    height_sf_mm  = sizes_tuple[5]
    width_sf_min  = min(width_sf_mm, width_sf_px)
    
    # Setting effective font sizes and positions (numbers are reference values)
    eff_etape_font_size      = font_size(14, width_sf_min)
    eff_launch_font_size     = font_size(13, width_sf_min)
    eff_entry_font_size      = font_size(12, width_sf_min)
    eff_help_font_size       = font_size(12, width_sf_min)
    eff_buttons_font_size    = font_size(11, width_sf_min)
    file_select_label_x_pos_px = _mm_to_px(10 * width_sf_mm, PPI)
    file_select_label_y_pos_px = _mm_to_px(25 * height_sf_mm, PPI)
    entry_x_pos_px             = _mm_to_px(25 * width_sf_mm, PPI)  
    entry_y_pos_px             = _mm_to_px(35 * height_sf_mm, PPI) 
    if_update_label_dx_px      = _mm_to_px( 0 * width_sf_mm, PPI)  
    if_update_label_dy_px      = _mm_to_px(20 * height_sf_mm, PPI) 
    missing_if_label_dx_px     = _mm_to_px( 0 * width_sf_mm, PPI)  
    missing_if_label_dy_px     = _mm_to_px(30 * height_sf_mm, PPI) 
    if_update_x_pos_px       = _mm_to_px(10 * width_sf_mm, PPI)    
    if_update_y_pos_px       = _mm_to_px(25 * height_sf_mm, PPI)   
    entry_dx_px              = _mm_to_px( 5 * width_sf_mm, PPI)    
    entry_dy_px              = _mm_to_px( 5 * height_sf_mm, PPI)   
    launch_dx_px             = _mm_to_px( 0 * width_sf_mm, PPI)    
    launch_dy_px             = _mm_to_px( 5 * height_sf_mm, PPI)   
    exit_button_x_pos_px     = _mm_to_px(193 * width_sf_mm, PPI)    
    exit_button_y_pos_px     = _mm_to_px(145 * height_sf_mm, PPI)  
    
    # Setting common attributs
    etape_label_format = 'left'
    etape_underline    = -1 
    
    # Setting number-of-characters reference for width in LabelEntry call    
    ref_entry_nb_char = REF_ENTRY_NB_CHAR                #90 -> 80                                     
    
    # Setting useful aliases
    backup_folder_name_alias  = ARCHI_BACKUP["root"]    
    if_root_folder_path_alias = ARCHI_IF["root"]
    if_file_name_alias        = ARCHI_IF["all IF"]
    if_manquants_file_alias   = ARCHI_IF["missing"]
    
    # Setting useful paths
    if_root_folder_path = bibliometer_path / Path(if_root_folder_path_alias)
    all_if_path = if_root_folder_path / Path(if_file_name_alias)
    backup_if_file_path = bibliometer_path / Path(backup_folder_name_alias) / Path (if_file_name_alias)
    
    ################## Sélection de la liste consolidée de publications
    
    ### Titre
    file_select_label_font = tkFont.Font(family = FONT_NAME, 
                                         size = eff_etape_font_size,
                                         weight = 'bold')
    file_select_label = tk.Label(self,
                               text = TEXT_ETAPE_5,
                               justify = etape_label_format,
                               font = file_select_label_font,
                               underline = etape_underline)
    file_select_label.place(x = file_select_label_x_pos_px, 
                            y = file_select_label_y_pos_px)
    
    ### Entrée nom de fichier pour la mise à jour    
    entry_label_font = tkFont.Font(family = FONT_NAME,
                                   size = eff_entry_font_size)
    entry_button_font = tkFont.Font(family = FONT_NAME,
                                    size = eff_entry_font_size)
        # le label du bouton est défini en dur dans la class LabelEntry_toFile à "Choix du fichier"
    file_select_entry = LabelEntry_toFile(self, 
                                          text_label = f"", 
                                          font_label = entry_label_font, 
                                          font_button = entry_button_font, 
                                          width = int(ref_entry_nb_char * width_sf_min))
    file_select_entry.place(x = entry_x_pos_px,
                            y = entry_y_pos_px) 
    
    
    ################## Mise à jour les IFs

    ### Titre
    if_update_font = tkFont.Font(family = FONT_NAME, 
                                 size = eff_etape_font_size,
                                 weight = 'bold')
    if_update_label = tk.Label(self,
                               text = TEXT_ETAPE_6,
                               justify = etape_label_format,
                               font = if_update_font,
                               underline = etape_underline)
    place_bellow(file_select_label, 
                 if_update_label, 
                 dx = if_update_label_dx_px, 
                 dy = if_update_label_dy_px)    
    
    ### Explication
    help_label_font = tkFont.Font(family = FONT_NAME, 
                                  size = eff_help_font_size)
    help_label = tk.Label(self, 
                          text = HELP_ETAPE_6, 
                          justify = "left", 
                          font = help_label_font)
    place_bellow(if_update_label, 
                 help_label)     
                                         
    ### Bouton pour lancer l'étape 
    if_update_launch_font = tkFont.Font(family = FONT_NAME, 
                                        size = eff_launch_font_size)
    if_update_launch_button = tk.Button(self,
                                        text = TEXT_MAJ_IF,
                                        font = if_update_launch_font,
                                        command = lambda: _launch_if_update())    
    place_bellow(help_label, 
                 if_update_launch_button, 
                 dx = launch_dx_px, 
                 dy = launch_dy_px)
    
    ################## Identification des IFs manquants
    
    ### Titre 
    missing_if_label_font = tkFont.Font(family = FONT_NAME, 
                                        size = eff_etape_font_size,
                                        weight = 'bold')
    missing_if_label = tk.Label(self, 
                                text = TEXT_ETAPE_7, 
                                justify = "left", 
                                font = missing_if_label_font)
    place_bellow(if_update_label, 
                 missing_if_label, 
                 dx = missing_if_label_dx_px, 
                 dy = missing_if_label_dy_px)
    
    ### Explication de l'étape
    help_label_font = tkFont.Font(family = FONT_NAME,
                               size = eff_help_font_size)
    help_label = tk.Label(self, 
                          text = HELP_ETAPE_7, 
                          justify = "left", 
                          font = help_label_font)
    place_bellow(missing_if_label, 
                 help_label) 
    
    ### Bouton pour lancer l'identification des IFs manquants
    button_missing_if_font = tkFont.Font(family = FONT_NAME, 
                                         size = eff_launch_font_size)
    button_missing_if = tk.Button(self, 
                                  text = TEXT_MISSING_IF, 
                                  font = button_missing_if_font, 
                                  command = lambda: _launch_missing_if())    
    place_bellow(help_label, 
                 button_missing_if, 
                 dx = launch_dx_px, 
                 dy = launch_dy_px)
    
    
    ################## Bouton pour sortir de la page
    font_button_quit = tkFont.Font(family = FONT_NAME, 
                                   size   = eff_buttons_font_size)
    button_quit = tk.Button(self, 
                            text = TEXT_PAUSE, 
                            font = font_button_quit, 
                            command = lambda: _launch_exit()).place(x = exit_button_x_pos_px, 
                                                                    y = exit_button_y_pos_px, 
                                                                    anchor = 'n')