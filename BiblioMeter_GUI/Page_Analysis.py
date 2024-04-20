__all__ = ['create_analysis']


def _launch_kw_analysis(institute, org_tup, bibliometer_path, year_select):
    """
    """

    # Standard library imports
    from tkinter import messagebox
    
    # Local imports
    from BiblioMeter_FUNCTS.BM_PubAnalysis import keywords_analysis

    kw_analysis_folder_path = keywords_analysis(institute, org_tup, bibliometer_path, 
                                                year_select, verbose = False)
    
    info_title = "- Information -"
    info_text  = f"L'analyse des mots clefs a été effectuée pour l'année {year_select}."
    info_text += f"\nLes fichiers obtenus ont été créés dans le dossier :"
    info_text += f"\n\n'{kw_analysis_folder_path}' "       
    messagebox.showinfo(info_title, info_text)        
    


def _launch_if_analysis(institute, org_tup, bibliometer_path, 
                        year_select, bdd_multi_annuelle_folder_alias):
    """
    """
    
    # Standard library imports
    from tkinter import messagebox
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import get_if_db
    from BiblioMeter_FUNCTS.BM_PubAnalysis import if_analysis

    # Getting year of most recent IFs 
    _,_,if_most_recent_year = get_if_db(institute, org_tup, bibliometer_path)

    analysis_if  = "IF " + if_most_recent_year
    if pg.ANALYSIS_IF == pg.COL_NAMES_BONUS['IF année publi'] and if_most_recent_year >= year_select:
        analysis_if  = "IF " + year_select            

    if_analysis_folder_path,_,_ = if_analysis(institute, org_tup, bibliometer_path, 
                                              year_select, if_most_recent_year, verbose = False) 
    
    info_title = "- Information -"
    info_text  = f"L'analyse des IFs a été effectuée pour l'année {year_select} "
    info_text += f"avec les valeurs {analysis_if}. "
    info_text += f"\n\nLes fichiers obtenus ont été créés dans le dossier :"
    info_text += f"\n\n'{if_analysis_folder_path}'."
    info_text += f"\n\nLa base de donnée des indicateurs respective de l'Institut "
    info_text += f"et de chaque département a été mise à jour "
    info_text += f"avec les résultats de cette analyse et se trouve dans le dossier :" 
    info_text += f"\n\n'{bdd_multi_annuelle_folder_alias}'."
    messagebox.showinfo(info_title, info_text)       
    

def create_analysis(self, institute, bibliometer_path, parent):
    
    """
    Description : function working as a bridge between the BiblioMeter 
    App and the functionalities needed for the use of the app
    
    Uses the following globals : 
    - DIC_OUT_PARSING
    - FOLDER_NAMES
    
    Args: takes only self and bibliometer_path as arguments. 
    self is the instense in which PageThree will be created
    bibliometer_path is a type Path, and is the path to where the folders
    organised in a very specific way are stored
    
    Returns : nothing, it create the page in self
    """
    
    # Standard library imports
    import os
    import shutil
    import tkinter as tk
    from tkinter import font as tkFont
    from tkinter import filedialog
    from tkinter import messagebox
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    import BiblioMeter_GUI.GUI_Globals as gg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_GUI.Page_Classes import app_main
    from BiblioMeter_GUI.Useful_Functions import encadre_RL
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import last_available_years
    from BiblioMeter_GUI.Useful_Functions import mm_to_px
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import place_bellow   
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_org_params  
   
    # Internal functions    
    def _launch_if_analysis_try():        
        # Getting year selection
        year_select =  variable_years.get()
        
        print(f"\nIFs analysis launched for year {year_select}")
        _launch_if_analysis(institute, org_tup, bibliometer_path, 
                            year_select, bdd_multi_annuelle_folder_alias)
        return
    
    def _launch_kw_analysis_try():
        # Getting year selection
        year_select =  variable_years.get()
        
        print(f"Keywords analysis launched for year {year_select}")
        _launch_kw_analysis(institute, org_tup, bibliometer_path, year_select)
        return   
            
    def _launch_exit():
        message =  "Vous allez fermer BiblioMeter. "
        message += "\nRien ne sera perdu et vous pourrez reprendre le traitement plus tard."
        message += "\n\nSouhaitez-vous faire une pause dans le traitement ?"
        answer_1 = messagebox.askokcancel('Information', message)
        if answer_1:
            parent.destroy()   
    
    # Setting effective font sizes and positions (numbers are reference values)
    eff_etape_font_size      = font_size(gg.REF_ETAPE_FONT_SIZE,   app_main.width_sf_min)           #14
    eff_launch_font_size     = font_size(gg.REF_ETAPE_FONT_SIZE-1, app_main.width_sf_min)
    eff_help_font_size       = font_size(gg.REF_ETAPE_FONT_SIZE-2, app_main.width_sf_min)
    eff_select_font_size     = font_size(gg.REF_ETAPE_FONT_SIZE-2, app_main.width_sf_min)
    eff_buttons_font_size    = font_size(gg.REF_ETAPE_FONT_SIZE-3, app_main.width_sf_min)  
    
    if_analysis_x_pos_px     = mm_to_px(10 * app_main.width_sf_mm,  gg.PPI)
    if_analysis_y_pos_px     = mm_to_px(40 * app_main.height_sf_mm, gg.PPI)     
    kw_analysis_label_dx_px  = mm_to_px( 0 * app_main.width_sf_mm,  gg.PPI)  
    kw_analysis_label_dy_px  = mm_to_px(15 * app_main.height_sf_mm, gg.PPI)   
    launch_dx_px             = mm_to_px( 0 * app_main.width_sf_mm,  gg.PPI)    
    launch_dy_px             = mm_to_px( 5 * app_main.height_sf_mm, gg.PPI)   

    year_button_x_pos        = mm_to_px(gg.REF_YEAR_BUT_POS_X_MM * app_main.width_sf_mm,  gg.PPI)    #10  
    year_button_y_pos        = mm_to_px(gg.REF_YEAR_BUT_POS_Y_MM * app_main.height_sf_mm, gg.PPI)    #26     
    dy_year                  = -6
    ds_year                  = 5
    
    exit_button_x_pos_px     = mm_to_px(gg.REF_EXIT_BUT_POS_X_MM * app_main.width_sf_mm,  gg.PPI)    #193 
    exit_button_y_pos_px     = mm_to_px(gg.REF_EXIT_BUT_POS_Y_MM * app_main.height_sf_mm, gg.PPI)    #145 
    
    # Setting common attributs
    etape_label_format = 'left'
    etape_underline    = -1                              

    # Setting useful paths independent from corpus year
    bdd_multi_annuelle_folder_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    
    # Getting institute parameters
    org_tup = set_org_params(institute, bibliometer_path)    
    
    # Décoration de la page
    # - Canvas
    fond = tk.Canvas(self, 
                     width  = app_main.win_width_px, 
                     height = app_main.win_height_px)
    fond.place(x = 0, y = 0)

    
    ### Choix de l'année 
    years_list = last_available_years(bibliometer_path, gg.CORPUSES_NUMBER)
    default_year = years_list[-1]  
    variable_years = tk.StringVar(self)
    variable_years.set(default_year)
    
    # Création de l'option button des années    
    self.font_OptionButton_years = tkFont.Font(family = gg.FONT_NAME, 
                                               size = eff_buttons_font_size)
    self.OptionButton_years = tk.OptionMenu(self, 
                                            variable_years, 
                                            *years_list)
    self.OptionButton_years.config(font = self.font_OptionButton_years)
    
        # Création du label
    self.font_Label_years = tkFont.Font(family = gg.FONT_NAME, 
                                        size = eff_select_font_size)
    self.Label_years = tk.Label(self, 
                                text = gg.TEXT_YEAR_PI, 
                                font = self.font_Label_years)
    self.Label_years.place(x = year_button_x_pos, y = year_button_y_pos)
    
    place_after(self.Label_years, self.OptionButton_years, dy = dy_year)
    encadre_RL(fond, self.Label_years, self.OptionButton_years, ds = ds_year)    
    
    ################## Analyse des IFs

    ### Titre
    if_analysis_font = tkFont.Font(family = gg.FONT_NAME, 
                                   size = eff_etape_font_size,
                                   weight = 'bold')
    if_analysis_label = tk.Label(self,
                                 text = gg.TEXT_ETAPE_7,
                                 justify = etape_label_format,
                                 font = if_analysis_font,
                                 underline = etape_underline)
    
    if_analysis_label.place(x = if_analysis_x_pos_px, 
                            y = if_analysis_y_pos_px)
    
    ### Explication
    help_label_font = tkFont.Font(family = gg.FONT_NAME, 
                                  size = eff_help_font_size)
    help_label = tk.Label(self, 
                          text = gg.HELP_ETAPE_7, 
                          justify = "left", 
                          font = help_label_font)
    place_bellow(if_analysis_label, 
                 help_label)     
                                         
    ### Bouton pour lancer l'analyse des IFs
    if_analysis_launch_font = tkFont.Font(family = gg.FONT_NAME, 
                                          size = eff_launch_font_size)
    if_analysis_launch_button = tk.Button(self,
                                          text = gg.TEXT_IF_ANALYSIS,
                                          font = if_analysis_launch_font,
                                          command = lambda: _launch_if_analysis_try())
    place_bellow(help_label, 
                 if_analysis_launch_button, 
                 dx = launch_dx_px, 
                 dy = launch_dy_px)
    
    ################## Analyse des mots clefs
    
    ### Titre 
    kw_analysis_label_font = tkFont.Font(family = gg.FONT_NAME, 
                                        size = eff_etape_font_size,
                                        weight = 'bold')
    kw_analysis_label = tk.Label(self, 
                               text = gg.TEXT_ETAPE_8, 
                               justify = "left", 
                               font = kw_analysis_label_font)
    place_bellow(if_analysis_launch_button, 
                 kw_analysis_label, 
                 dx = kw_analysis_label_dx_px, 
                 dy = kw_analysis_label_dy_px)
    
    ### Explication de l'étape
    help_label_font = tkFont.Font(family = gg.FONT_NAME,
                               size = eff_help_font_size)
    help_label = tk.Label(self, 
                          text = gg.HELP_ETAPE_8, 
                          justify = "left", 
                          font = help_label_font)
    place_bellow(kw_analysis_label, 
                 help_label) 
    
    ### Bouton pour lancer l'analyse des mots clefs
    kw_analysis_launch_font = tkFont.Font(family = gg.FONT_NAME, 
                                         size = eff_launch_font_size)
    kw_analysis_button = tk.Button(self, 
                                  text = gg.TEXT_KW_ANALYSIS, 
                                  font = kw_analysis_launch_font, 
                                  command = lambda: _launch_kw_analysis_try())  
    place_bellow(help_label, 
                 kw_analysis_button, 
                 dx = launch_dx_px, 
                 dy = launch_dy_px)
    
    
    ################## Bouton pour sortir de la page
    quit_font = tkFont.Font(family = gg.FONT_NAME, 
                            size   = eff_buttons_font_size)
    quit_button = tk.Button(self, 
                            text = gg.TEXT_PAUSE, 
                            font = quit_font, 
                            command = lambda: _launch_exit()).place(x = exit_button_x_pos_px, 
                                                                    y = exit_button_y_pos_px, 
                                                                    anchor = 'n')