__all__ = ['create_PageFour']

def create_PageFour(self, bibliometer_path):

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

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES

    Button_DTNM = tk.Button(self, text = 'DTNM', 
                                    font = ("Helvetica", 18))
    Button_DTNM.place(anchor = 'center', relx = 0.25, rely = 0.25)

    Button_DTBH = tk.Button(self, text = 'DTBM', 
                            font = ("Helvetica", 18))
    Button_DTBH.place(anchor = 'center', relx = 0.75, rely = 0.25)

    Button_DTS = tk.Button(self, text = 'DTS', 
                           font = ("Helvetica", 18))
    Button_DTS.place(anchor = 'center', relx = 0.25, rely = 0.75)

    Button_DEHT = tk.Button(self, text = 'DEHT', 
                            font = ("Helvetica", 18))
    Button_DEHT.place(anchor = 'center', relx = 0.75, rely = 0.75)