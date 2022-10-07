__all__ = ['create_MultiAnnuelle']

def create_MultiAnnuelle(self, bibliometer_path):
    
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
    etape_5.place(x = mm_to_px(10, PPI)*min(SFW, SFWP), y = mm_to_px(25, PPI)*min(SFH, SFHP))

    #sous_text_etape_5 = tk.Label(self, text = SOUS_TEXT_ETAPE_5, justify = FORMAT_TEXT_ETAPE_5, font = FONT_SOUS_ETAPE_5)
    #place_after(etape_5, sous_text_etape_5, dx = 2, dy = 4)
    

    # QUATRIEME PARTIE : CONCATENER LES 5 DERNIERS ANNEES
    font_Button_concat = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_concat = tk.Button(self, 
                              text = TEXT_FINALE, 
                              font = font_Button_concat, 
                              command = lambda: _concat_filtre_depar())
    
    place_bellow(etape_5, Button_concat, dy = mm_to_px(5, PPI)*min(SFH, SFHP))
    #encadre_UD(fond, etape_5, Button_concat, "black", dn = 2, de = 5000, ds = 5000, dw = 5000)
    
    #Button_concat.place(anchor = 'center', relx = 0.5, rely = 0.75)
    
    def _concat_filtre_depar():
        
        '''
        '''
        
        df_concat = pd.DataFrame()
    
        for i in range(len(years_list)):
            path = Path(bibliometer_path) / Path(years_list[i]) / Path(R_path_alias) / Path(f'Liste finale publication {years_list[i]}.xlsx')
            df_inter = pd.read_excel(path)
            df_concat = df_concat.append(df_inter)
            
        date = str(datetime.now())[:16].replace(':', '')
        df_concat.to_excel(Path(bibliometer_path) / Path(bdd_annuelle_alias) / Path(f'{date}_concat_dep_{os.getlogin()}.xlsx'))
        
        messagebox.showinfo('Information', f"La concatenation des documents finaux des dernières années disponibles a été faite, vous pouvez la retrouver dans BDD Multi-annuelle")
        
    font_MAJ_IF = tkFont.Font(family = "Helvetica", size = font_size(13, min(SFW, SFWP)))
    Button_MAJ_IF = tk.Button(self, 
                              text = TEXT_MAJ_IF, 
                              font = font_MAJ_IF, 
                              command = lambda: _launch_maj_if())
    
    place_after(Button_concat, Button_MAJ_IF, dx = mm_to_px(65, PPI)*min(SFW, SFWP), dy = -mm_to_px(0.5, PPI)*min(SFH, SFHP))

    LE_font_label = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
    LE_font_button = tkFont.Font(family = "Helvetica", size = font_size(12, min(SFW, SFWP)))
        
    LabelEntry_MAJ_IF = LabelEntry_toFile(self, 
                                          text_label = f"Fichier dont les IF\nsont à mettre à jour", font_label = LE_font_label, font_button = LE_font_button, 
                                          width = int(20*min(SFW, SFWP)))
    LabelEntry_MAJ_IF.set("")
    place_bellow(Button_MAJ_IF, LabelEntry_MAJ_IF, dx = mm_to_px(15, PPI)*min(SFW, SFWP))
    
        
    def _launch_maj_if():
        
        '''
        '''
        
    #try:
        ajout_IF(LabelEntry_MAJ_IF.get(), LabelEntry_MAJ_IF.get(), bibliometer_path / Path(STOCKAGE_ARBORESCENCE['general'][7] / Path('IF all years.xlsx')), None)
        messagebox.showinfo('Information', f"Les IF ont été mis à jour.")
    #except:
        messagebox.showinfo('Information', f"Vous n'avez pas sélectionné de fichier à mettre à jour.")
        