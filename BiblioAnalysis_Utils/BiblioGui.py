__all__ = ['cooc_selection',
           'coupling_attr_selection',
           'filters_selection',
           'filter_item_selection',
           'item_selection',
           'merge_database_gui',           
           'SAVE_CONFIG_FILTERS',
           'select_folder_gui',
           'select_folder_gui_new',
           'Select_multi_items',
           'treemap_item_selection',]

# To Do: change 'Select_multi_items' to 'select_multi_items'

# Globals used from BiblioAnalysis_Utils.BiblioSys: DISPLAYS
# Globals used from BiblioAnalysis_Utils.BiblioGeneralGlobals: IN_TO_MM

from BiblioAnalysis_Utils.BiblioSpecificGlobals import (DIC_OUTDIR_PARSING,
                                                        LABEL_MEANING,
                                                        COOC_AUTHORIZED_ITEMS_DICT)

ACRONYME_MEANING = dict(zip(LABEL_MEANING.values(),LABEL_MEANING.keys()))

TREE_MAP_ITEM = [
    ("years", 1),
    ("languages", 2),
    ("doctypes", 3),
    ("countries", 4),
    ("institutions", 5),
    ("journals", 6),
    ("references", 7),
    ("refjournals", 8),
    ("subjects", 9),
    ("subjects2", 10),
    ("journalkeywords", 11),
    ("titlekeywords", 12),
    ("authorskeywords", 13),
    ("authors",14)
]

TREE_MAP_ITEM_HELP_TEXT = '''Select the item you want to deal with.

With MACOS, to exit you have to kill manually the menu window.''' 

GEOMETRY_ITEM_SELECTION = '350x520+50+50'

COOC_SELECTION_HELP_TEXT = '''In a cooccurrence graph two authors, keywords, sujects 
or more generally two 'items' are linked by an edge, if two
authors have coothered an article, if two keywords
names belong to the same article...

To build a cooccurrence graph, you have to select:
                                 - the item used to build cooccurrences graph (default='Authors')
                                 - the minimum size of the node (integer, default=1)
                                 
The node size is the total number of occurences of an author, keyword name,... in the corpus.

With macOS, to exit you have to kill manually the menu window.''' 

GEOMETRY_COOC_SELECTION = '410x350+50+50'
GEOMETRY_COUPLING_SELECTION = '470x350+50+50'

MERGE_DATABASE_HELP_TEXT = '''Merge several databases (wos/scopus) in one database.
You have to choose:
    the database type (wos/scopus)
    the name of the merged database (without extension)
    the input dfolder where the databases are stored
    the output folder where the merged database will be stored.
    
With macOS, to exit you have to kill manually the menu window.''' 

GEOMETRY_MERGE_GUI = '500x550+50+50'

FILTERS_ITEMS_DICT = {'Authors':'AU',
                      'Years':'Y',
                      'Institutions':'I',
                      'Document types':'DT',
                      'Journals':'J',
                      'References journals':'RJ',
                      'Full references':'R',
                      'Authors keywords':'AK',
                      'Title keywords':'TK',
                      'Journal keywords':'IK',
                      'Countries':'CU',
                      'Subjects':'S',
                      'Sub-subjects':'S2',
                        }

FILTERS_SELECTION_HELP_TEXT = '''To be done'''

GEOMETRY_FILTERS_SELECTION = '500x580+50+50' 

SAVE_CONFIG_FILTERS = 'save_config_filters.json'

DEFAULT_SAVE_CONFIG_FILTER = {'description': 'items to be combined in union or intersection for filtering the corpus',
 'COMBINE': 'union',
 'EXCLUSION': False,
 'AU': {'description': 'Selected authors',
  'mode': False,
  'list': []},
 'Y': {'description': 'Selected time period', 'mode': False, 'list': []},
 'CU': {'description': 'Selected countries',
  'mode': False,
  'list': []},
 'I': {'description': 'Selected institutions',
  'mode': False,
  'list': []},
 'DT': {'description': 'Selected document types',
  'mode': False,
  'list': []},
 'J': {'description': 'Selected journals',
  'mode': False,
  'list': []},
 'LA': {'description': 'Selected languages',
  'mode': False,
  'list': []},
 'S': {'description': 'Selected subject categories',
  'mode': False,
  'list': []},
 'S2': {'description': 'Selected subject subcategories',
  'mode': False,
  'list': []},
 'RJ': {'description': 'Selected journals of cited publications',
  'mode': False,
  'list': []},
 'R': {'description': 'Selected full references of cited publications',
  'mode': False,
  'list': []},
 'IK': {'description': 'Selected keywords',
  'mode': False,
  'list': []},
 'TK': {'description': 'Selected title words',
  'mode': False,
  'list': []},
 'AK': {'description': 'Selected authors keywords',
  'mode': False,
  'list': []}}

def item_selection(fact=3, win_widthmm=80, win_heightmm=130, font_size=16) :
    
    '''
    Selection of items for treemaps
    
    Arguments: none
    
    Returns:
        selected_item (string): choosen item

    '''
    
    # Standard library imports
    import os
    import tkinter as tk
    import tkinter.font as TkFont    
    from tkinter import ttk
    from tkinter import messagebox
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
    
    global selected_item
    
    def _choice(text, v):
        global selected_item
        selected_item = text
    
    def _help():
        messagebox.showinfo("Item selection info", TREE_MAP_ITEM_HELP_TEXT)

    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title    
    title = 'Treemap GUI'
    
    # Creating the gui window
    tk_root = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))

    #win_widthpx = 350
    #win_heightpx = 520
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50)

    tk_root.attributes("-topmost", True)
    tk_root.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    tk_root.title(title) 
    item_choice = ttk.LabelFrame(tk_root, text=' Label selection ')
    item_choice.grid(column=0, row=0, padx=8, pady=4)
    
    menu = ttk.LabelFrame(tk_root, text=' Menu ')
    menu.grid(column=1, row=0, padx=8, pady=4)
        
    selected_item = "subjects"
       
    # choice of the item for treemap
    #
    varitem = tk.IntVar()
    varitem.set(TREE_MAP_ITEM[0][1])

    tk.Label(item_choice, text='Choose the item for treemap :').grid(column=0, row=1, padx=8, pady=4)
    
    idx_row = 2
    for txt, val in TREE_MAP_ITEM:
        tk.Radiobutton(item_choice, text = txt, variable = varitem, value=val,
            command=lambda t = txt, v = varitem: _choice(t, v)).grid(column=0, row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        idx_row += 1

    help_button = ttk.Button(menu, text="HELP", command=_help)
    help_button.grid(column=0, row=0)
    
    if os.name == 'nt':
        tk.Button(menu, text="EXIT", command=tk_root.destroy).grid(column=0, row=1, padx=8, pady=4)
    tk_root.mainloop()
    
    return selected_item


def treemap_item_selection(fact=2, win_widthmm=70, win_heightmm=105, font_size=16):
    
    '''
    Selection of items for treemaps
    
    Arguments: none
    
    Returns:
        selected_item (string): choosen item

    '''
    
    # Standard library imports
    import os
    import tkinter as tk
    import tkinter.font as TkFont    
    from tkinter import ttk
    from tkinter import messagebox
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
    
    global selected_item
    
    def _choice(text, v):
        global selected_item
        selected_item = text
    
    def _help():
        messagebox.showinfo("Item selection info", TREE_MAP_ITEM_HELP_TEXT)

    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title    
    title = 'Treemap GUI'
    
    # Creating the gui window
    tk_root = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))

    #win_widthpx = 350
    #win_heightpx = 520
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50)

    tk_root.attributes("-topmost", True)
    tk_root.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    tk_root.title(title) 
    item_choice = ttk.LabelFrame(tk_root, text=' Label selection ')
    item_choice.grid(column=0, row=0, padx=8, pady=4)
    
    menu = ttk.LabelFrame(tk_root, text=' Menu ')
    menu.grid(column=1, row=0, padx=8, pady=4)
        
    selected_item = "subjects"
       
    # choice of the item for treemap
    #
    varitem = tk.IntVar()
    varitem.set(TREE_MAP_ITEM[0][1])

    tk.Label(item_choice, text='Choose the item for treemap :').grid(column=0, row=1, padx=8, pady=4)
    
    idx_row = 2
    for txt, val in TREE_MAP_ITEM:
        tk.Radiobutton(item_choice, text = txt, variable = varitem, value=val,
            command=lambda t = txt, v = varitem: _choice(t, v)).grid(column=0, row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        idx_row += 1

    help_button = ttk.Button(menu, text="HELP", command=_help)
    help_button.grid(column=0, row=0)
    
    if os.name == 'nt':
        tk.Button(menu, text="EXIT", command=tk_root.destroy).grid(column=0, row=1, padx=8, pady=4)
    tk_root.mainloop()
    
    return selected_item


def cooc_selection(fact=3, win_widthmm=80, win_heightmm=100, font_size=16) :
    
    '''
    Selection of items for cooccurrences graph treatment
    
    Arguments: none
    
    Returns:
        selected_item(string): item acronyme
        minimum_size_node (int): minimum size of the nodes


    '''
    # Standard library imports
    import os
    import tkinter as tk
    import tkinter.font as TkFont     
    from tkinter import ttk
    from tkinter import messagebox
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
      
    global selected_item, minimum_size_node
    
    def _choice(text, v):
        global selected_item
        selected_item = COOC_AUTHORIZED_ITEMS_DICT[text]
    

    def _submit(): 
        global minimum_size_node
        minimum_size_node = size_entered.get()
    
    def _help():
        messagebox.showinfo("cooc selection info", COOC_SELECTION_HELP_TEXT)
    
    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title    
    title = 'Cooccurrence graph GUI'
    
    # Creating the gui window
    tk_root = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))
    #win_widthpx = 410
    #win_heightpx = 350
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50) 

    tk_root.attributes("-topmost", True)
    tk_root.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    tk_root.title(title) 
    
    item_choice = ttk.LabelFrame(tk_root, text=' Label selection ')
    item_choice.grid(column=0, row=0, padx=8, pady=4)
    
    size_choice = ttk.LabelFrame(tk_root, text=' Size choice ')
    size_choice.grid(column=1, row=0, padx=8, pady=4)
    
    selected_item = 'AU'  # Default value
    minimum_size_node = 1 # Default value        
        
    #                               Choice of the item for the cooccurrence graph
    # -------------------------------------------------------------------------------------------
    item = [(x,i) for i,x in enumerate(COOC_AUTHORIZED_ITEMS_DICT.keys())]
    varitem = tk.IntVar()
    #varitem.set(item[0][1])

    ttk.Label(item_choice , 
             text='Choose an item\nfor the co-occurrence graph:').grid(column=0, row=1, padx=8, pady=4)
    
    idx_row = 2
    for txt, val in item:
        tk.Radiobutton(item_choice, text=txt, variable=varitem, value=val,
            command=lambda t = txt, v=varitem: _choice(t, v)).grid(column=0, \
                                    row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        idx_row += 1
     
    #                                Minmum node size selection
    # -------------------------------------------------------------------------------------------
    name = tk.StringVar()
    ttk.Label(size_choice , 
             text='Choose the minimum\nsize of the nodes:').grid(column=0, row=0, padx=8, pady=4)
    size_entered = ttk.Entry(size_choice, width=5, textvariable=name)
    size_entered.grid(column=0, row=1, padx=8, pady=4) #sticky=tk.W) 
    

    submit_button = ttk.Button(size_choice, text="Submit", command=_submit)   
    submit_button.grid(column=0, row=2, padx=8, pady=4) 
    help_button = ttk.Button(size_choice, text="HELP", command=_help)
    help_button.grid(column=0, row=3, padx=8, pady=4)
    
    if os.name == 'nt':
        tk.Button(size_choice, text="EXIT", command=tk_root.destroy).grid(column=0, row=4, padx=8, pady=4)
    
    tk_root.mainloop()
    
    try:
        minimum_size_node = int(minimum_size_node)
    except: # Takes a default value
        minimum_size_node = 1
     
    return selected_item,minimum_size_node
    
def merge_database_gui(fact=3, win_widthmm=80, win_heightmm=100, font_size=16):
    
    '''
    Selection of database files to be merged
    
    Arguments: none
    
    Returns:
        database (str): database type (scopus or wos)
        filename (str): name of the merged database
        in_dir (str): name of the folder where the databases to be merged are stored
        out_dir (str): name of the folder where the merged database will be stored

    '''
    # Standard library imports
    import os
    import tkinter as tk
    import tkinter.font as TkFont 
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    from pathlib import Path
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
    
    global database_type, database_filename, in_dir, out_dir
    
    def _choice(text, v):
        global database_type
        database_type = text
        
    def _submit(): 
        global database_filename
        database_filename = size_entered.get()
        if database_type == "wos":
            database_filename = database_filename + '.txt'
        else:
            database_filename = database_filename + '.csv'
    
    def _indir_folder_choice():
        global in_dir
        in_dir = filedialog.askdirectory(initialdir=str(Path.home()), title="Select in_dir folder")                             
    
    def _outdir_folder_choice():
        global out_dir
        out_dir = filedialog.askdirectory(initialdir=str(Path.home()), title="Select out_dir folder")   
    
    def _help():
        messagebox.showinfo("Merge database info", MERGE_DATABASE_HELP_TEXT)
                    
    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title
    title = 'Database merge GUI'
    
    # Creating the gui window
    tk_root = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))
    #win_widthpx = 500
    #win_heightpx = 550
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50) 

    tk_root.attributes("-topmost", True)
    tk_root.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    tk_root.title(title) 
    
    item_choice = ttk.LabelFrame(tk_root, text=' Database selection ')
    item_choice.grid(column=0, row=0, padx=8, pady=4)
    
    folder_choice = ttk.LabelFrame(tk_root, text=' Folders selection ')
    folder_choice.grid(column=1, row=0, padx=8, pady=4)
    
    database_type = 'wos'  # Default value    
    database_filename = "test" # Default value

    #                               Choice of a database
    # -------------------------------------------------------------------------------------------
    item = ["wos", 'scopus']
    varitem = tk.IntVar()
    varitem.set(item[0][1])

    ttk.Label(item_choice , 
             text='Choose a database type:').grid(column=0, row=1, padx=8, pady=4)
    
    idx_row = 2
    for  val, txt,  in enumerate(item):
        tk.Radiobutton(item_choice, text = txt, variable = varitem, value=val,
            command=lambda t = txt, v = varitem: _choice(t, v)).grid(column=0, row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        idx_row += 1
     
    #                   File name, in_dir,  out_dir selection
    # -------------------------------------------------------------------------------------------
    name = tk.StringVar()
    ttk.Label(folder_choice , 
             text='File name of the merged database:').grid(column=0, row=0, padx=8, pady=4)
    size_entered = ttk.Entry(folder_choice, width=30, textvariable=name)
    size_entered.grid(column=0, row=1, sticky=tk.W) 
    

    submit_button = ttk.Button(folder_choice, text="Submit", command=_submit)   
    submit_button.grid(column=1, row=1, padx=8, pady=4)
    
    indir_button = ttk.Button(folder_choice, text="In-dir folder", command=_indir_folder_choice)
    indir_button.grid(column=0, row=2, padx=8, pady=4)
    
    outdir_button = ttk.Button(folder_choice, text="Out-dir folder", command=_outdir_folder_choice)
    outdir_button.grid(column=0, row=3, padx=8, pady=4)
    
    help_button = ttk.Button(folder_choice, text="HELP", command=_help)
    help_button.grid(column=0, row=5, padx=8, pady=4)
    
    
    if os.name == 'nt': # Work with nt not macos
        tk.Button(folder_choice, text="EXIT", command=tk_root.destroy).grid(column=0, row=6, padx=8, pady=4)
    
    tk_root.mainloop()
    
    return database_type, database_filename, in_dir, out_dir
    
def _read_item_state(item,parsing_dir):
    '''
    item: 
    parsing_dir:
    '''

    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    if item in ['AU','CU','I']:
        df = pd.read_csv(parsing_dir / Path(DIC_OUTDIR_PARSING[item]),
                     sep='\t',
                     engine='python',
                     header=None)
        df.columns = ['pub_id','idx','attribute']
        dg = df['attribute'].tolist()
    
    elif item in ['IK','TK','AK','S','S2']:
        df = pd.read_csv(parsing_dir / Path(DIC_OUTDIR_PARSING[item]),
                     sep='\t',
                     engine='python',
                     header=None)
        df.columns = ['pub_id','attribute']
        dg = df['attribute'].tolist()
        
    elif item in ['Y','DT','J','LA']:
        df = pd.read_csv(parsing_dir / Path(DIC_OUTDIR_PARSING['A']),
                     sep='\t',
                     engine='python',
                     header=None).astype(str)
        df.columns = ['pub_id','authors','Y','J','vol', 'page','DOI', 'DT','LA','title','ISSN']
        if item == 'Y':
            dg = df['Y'].tolist()
        if item == 'DT':
            dg = df['DT'].tolist()       
        if item == 'J':
            dg = df['J'].tolist()            
        if item == 'LA':
            dg = df['LA'].tolist()
            
    elif item in ['R','RJ']:
        df = pd.read_csv(parsing_dir / Path(DIC_OUTDIR_PARSING['R']),
                     sep='\t',
                     engine='python',
                     header=None).astype(str)
        df.columns = ['pub_id','first_author','year','journal','volume','page']
        if item == 'R':
            table = df.T.apply(lambda row : ", ".join(row[1:] )) # Builds ref: "author, year, journal, volume, page"
                                                                 # ex:"Gordon P, 2004, SCIENCE, 306, 496"
            dg = table.tolist()
        if item == 'RJ':
            dg = df['journal'].tolist()              

    return dg

def _select_item_attributes(dg, item_tag, config_filter, 
                            win_widthmm=80, win_heightmm=100):

    """interactive selection of items among the list list-item
    
    Args:
        list_item (list): list of items used for the selection
        
    Returns:
        list (list): list of selected items without duplicate
        
    """
    # Standard library imports
    import collections
    import os
    import re
    import tkinter as tk 
   
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
    
    global val
 
    def selected_item():
        global val
        val = [re.split(re_split, listbox.get(i))[0] for i in listbox.curselection()]
        config_filter[item_tag]['list'] = val
        if os.name == 'nt':
            top.destroy()
    
    re_split = re.compile('\s\(\d{1,5}\)')
    
    val = list_default = config_filter[item_tag]['list']
    dg = sorted([ (token,nbr_occurrence_token) for token,nbr_occurrence_token in collections.Counter(dg).items()],
                   key=lambda tup: tup[1], reverse=True)

    list_item = [token+ f' ({int(nbr_occurrence_token)})' for token,nbr_occurrence_token 
                  in dg
                  if nbr_occurrence_token>2]
    
    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Creating the gui window
    top = tk.Toplevel()
    
    # Setting the window geometry parameters
    win_widthpx = str(_mm_to_px(win_widthmm,ppi))
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))
    #win_widthpx = 500
    #win_heightpx = 580
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 100)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 100) 

    top.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    top.attributes("-topmost", True)
    yscrollbar = tk.Scrollbar(top)
    yscrollbar.pack(side = tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(top, width=40, height=10, selectmode=tk.MULTIPLE,
                         yscrollcommand=yscrollbar.set)

    x = list_item

    for idx,item in enumerate(x):
        listbox.insert(idx, item)
        listbox.itemconfig(idx,
                 bg = "white" if idx % 2 == 0 else "white")
    
    for default_value in list_default:
        idx = [dg.index(tupl) for tupl in dg if tupl[0] == default_value]
        if idx != []:
            listbox.selection_set(idx)

    btn = tk.Button(top, text='OK', command=selected_item)

    btn.pack(side='bottom')

    listbox.pack(padx = 10, pady = 10,
              expand = tk.YES, fill = "both")
    yscrollbar.config(command = listbox.yview)
    
    top.mainloop()
    
    return val
    
def _function_help():
    # Standard library imports
    import tkinter as tk
    
    top = tk.Toplevel()
    top.geometry(GEOMETRY_FILTERS_SELECTION)
    top.attributes("-topmost", True)
    
    T = tk.Text(top)
    T.pack(expand = True, fill = tk.BOTH)
    T.insert("end",FILTERS_SELECTION_HELP_TEXT)
    
    top.mainloop()

def filters_selection(filters_filename, save_filename, parsing_dir, 
                      fact=3, win_widthmm=80, win_heightmm=130, font_size=16) :
    
    ''' The 'filters_selection' function allows an interactive setting of the configuration
    for the corpus filtering. 
    
    Arguments: 
        filters_filename (path): path of the json file of the filtering configuration.
        save_filename (path): path for saving the json file of the filtering configuration.
        parsing_dir (path) : path of the parsing folder ofthe corpus.
        fact (float):
        win_widthmm (float):
        win_heightmm (float):
        font_size (int): font size of the window title (default=16).
        
    Returns:


    '''
    # Standard library imports
    import functools
    import json
    import os
    import tkinter as tk
    import tkinter.font as TkFont
    from tkinter import ttk
    from tkinter import messagebox
    from pathlib import Path
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
    
    global number_of_call    
                
    def spy_state(*args):
        global number_of_call
        number_of_call += 1
        nbr_select = sum([x.get() for x in varitem] )
        if (nbr_select<2) & (number_of_call>=len(items)):
            button_union["state"] = "disable"
            button_inter["state"] = "disable"
            button_union.deselect()
            button_inter.deselect()
            
            #messagebox.showwarning('you must select at least two items to use \n union/intersection set operation')
            
        else:
            button_union["state"] = "normal"
            button_inter["state"] = "normal"
            if config_filter['COMBINE'] == 'union':
                button_union.select()
            else:
                button_inter.select()            
        
    def action_varitem():
        for idx in range(len(LABEL_MEANING)):
            if varitem[idx].get():
                list_button[idx]['state'] = 'normal'
                item_label = [tupl[0] for i, tupl in enumerate(items) if tupl[1] == idx][0]
                item_acronyme = ACRONYME_MEANING[item_label]
                config_filter[item_acronyme]['mode'] = True
            else:
                list_button[idx]['state'] = 'disabled'
                item_label = [tupl[0] for i, tupl in enumerate(items) if tupl[1] == idx][0]
                item_acronyme = ACRONYME_MEANING[item_label]
                config_filter[item_acronyme]['mode'] = False
            
    def func(item_acronyme):
        dg = _read_item_state(item_acronyme,parsing_dir)
        _select_item_attributes(dg,item_acronyme,config_filter)
        
    def ModeSelected():
        choice  = var_union_inter.get()
        if choice == 1:
           config_filter['COMBINE'] = "union"

        elif choice == 2:
           config_filter['COMBINE'] = "intersection"
        
    def action_exlusion():
        choice  = var_exclusion.get()
        if choice:
            config_filter['EXCLUSION'] = True
        else:
            config_filter['EXCLUSION'] = False
    
    def func_help():
        _function_help()
    
    # Read the filters configuration file
    try:
        with open(filters_filename, "r") as read_file:
            config_filter = json.load(read_file)
    except:
        config_filter = DEFAULT_SAVE_CONFIG_FILTER
    
    # To Do : explain this line
    number_of_call = 0
    
    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title
    title = 'Filters configuration GUI'
    
    # Creating the gui window
    tk_root = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50)
    
    tk_root.attributes("-topmost", True)
    tk_root.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    tk_root.title(title)
    tk_root.columnconfigure(0,weight=1)
    tk_root.columnconfigure(1,weight=1)
    item_choice = ttk.LabelFrame(tk_root, text=' ')
    item_choice.grid(column=0, row=0, padx=8, pady=4,sticky=tk.W+tk.E)
    
    combine_exit = ttk.LabelFrame(tk_root, text=' ')
    combine_exit.grid(column=1, row=0, padx=8, pady=4,sticky=tk.W+tk.E)
    
    combine_choice = ttk.LabelFrame(combine_exit, text=' ')
    combine_choice.grid(column=0, row=0, padx=8, pady=4,sticky=tk.W+tk.E)

    exit_choice = ttk.LabelFrame(combine_exit, text='  ')
    exit_choice.grid(column=0, row=1, padx=8, pady=4)
    
   
    items = [(x,i) for i,x in enumerate(LABEL_MEANING.values())]

    ttk.Label(item_choice , 
             text='Choose the items for filtering').grid(column=0, row=1, padx=8, pady=4)
    
    var_union_inter = tk.IntVar()
    var_exclusion = tk.IntVar()
    tk.Label(combine_choice, text='Choose a combination mode\n between at least 2 items :'
            ).grid(column=0, row=1, padx=8, pady=4)
    
    button_union = tk.Radiobutton(combine_choice,
                                  text = 'Union',
                                  variable = var_union_inter,
                                  value=1,
                                  command=ModeSelected,
                                  state="normal")
    button_union.grid(column=0, row=2, padx=8, pady=4,sticky=tk.W)
    button_inter = tk.Radiobutton(combine_choice,
                                  text = 'Intersection',
                                  variable = var_union_inter,
                                  value=2,
                                  command=ModeSelected,
                                  state="normal")
    button_inter.grid(column=0, row=3, padx=8, pady=4,sticky=tk.W)
    
    if config_filter['COMBINE'] == 'union':
        button_union.select()
    else:
        button_inter.select()
        
    tk.Checkbutton(combine_choice, 
                       text = 'Exclusion', 
                       variable = var_exclusion,command=action_exlusion
                      ).grid(column=0, row=5, padx=8, pady=4,sticky=tk.W)
    
    if config_filter['EXCLUSION']:
        var_exclusion.set(True)
        
    button_help = tk.Button(exit_choice, 
                            text='HELP', 
                            command=func_help)
    button_help.grid(column=0, row=0, padx=8, pady=4,sticky=tk.E+tk.W)
    if os.name == 'nt':
        exit = tk.Button(exit_choice, text="EXIT", command=tk_root.destroy)
        exit.grid(column=0, row=1, padx=8, pady=4)
    
    idx_row = 2
    list_button = []
    varitem = []
    for  txt, val in items:
        check_state = tk.BooleanVar()    
        check_state.trace('w',spy_state) 
        varitem.append(check_state)
        if config_filter[ACRONYME_MEANING[txt]]['mode']:
            state = 'normal'
            varitem[val].set(True)
        else:
            state = 'disabled'
            varitem[val].set(False)
        button = tk.Button(item_choice, 
                               text='SELECT', 
                               command=functools.partial(func,ACRONYME_MEANING[txt]),
                               state = state)
        button.grid(column=1, row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        list_button.append(button)
            
        tk.Checkbutton(item_choice, 
                       text = txt, 
                       variable = varitem[idx_row-2],command=action_varitem
                       ).grid(column=0, row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        idx_row += 1 
    
    tk_root.mainloop()
    
    with open(save_filename, "w") as write_file:
        jsonString = json.dumps(config_filter, indent=4)
        write_file.write(jsonString)
        
    return
    
def coupling_attr_selection(fact=2, win_widthmm=80, win_heightmm=60, font_size=16):
    
    '''
    Selection of items for coupling graph treatment
    
    Arguments: none
    
    Returns:
        selected_item (string): item acronyme
        m_max_attrs (int): maximum added attributes

    '''
    # Standard library imports
    import os
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    import tkinter.font as TkFont
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP    
    
    global selected_item, m_max_attrs
    
    def choice(text, v):
        global selected_item
        selected_item = COOC_AUTHORIZED_ITEMS_DICT[text]
    
    m_max_attrs = 2 # Default value
    def submit(): 
        global m_max_attrs
        m_max_attrs = size_entered.get()
    
    def help():
        messagebox.showinfo("coupling selection info", COOC_SELECTION_HELP_TEXT)    
    
    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title
    title = 'Coupling graph GUI'
    
    # Setting the selected_item default value
    selected_item = 'S'
    
    # Creating the gui window
    tk_root = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))      
    #win_widthpx = '470'
    #win_heightpx = '350'
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50)
         
    tk_root.attributes("-topmost", True)
    tk_root.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    tk_root.title(title) 
    
    item_choice = ttk.LabelFrame(tk_root, text=' Item selection ')
    item_choice.grid(column=0, row=0, padx=8, pady=4)
    
    size_choice = ttk.LabelFrame(tk_root, text=' Number of item values ')
    size_choice.grid(column=1, row=0, padx=8, pady=4)
            
    #           Choice of the item for the coupling graph completion
    # -------------------------------------------------------------------------------------------
    item = [(x,i) for i,x in enumerate(COOC_AUTHORIZED_ITEMS_DICT.keys())]
    varitem = tk.IntVar()

    ttk.Label(item_choice , 
             text='Choose an item\nfor the coupling graph node attribute:').grid(column=0, row=1, padx=8, pady=4)
    
    idx_row = 2
    for txt, val in item:
        tk.Radiobutton(item_choice, text=txt, variable=varitem, value=val,
            command=lambda t = txt, v=varitem: choice(t, v)).grid(column=0, row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        idx_row += 1
     
    #                 Selection of the maximum number of item values
    # -------------------------------------------------------------------------------------------
    name = tk.StringVar()
    ttk.Label(size_choice , 
             text='Choose the maximum \n number of item values:').grid(column=0,
                                                                       row=0,
                                                                       padx=8,
                                                                       pady=4)
    size_entered = ttk.Entry(size_choice, width=5, textvariable=name)
    size_entered.grid(column=0, row=1, padx=10, pady=4)
    

    submit_button = ttk.Button(size_choice, text="Submit", command=submit)   
    submit_button.grid(column=0, row=2, padx=8, pady=4) 
    help_button = ttk.Button(size_choice, text="HELP", command=help)
    help_button.grid(column=0, row=3, padx=8, pady=4)
    
    if os.name == 'nt':
        tk.Button(size_choice, text="EXIT", command=tk_root.destroy).grid(column=0, row=4, padx=8, pady=4)
    
    tk_root.mainloop()
    
    try:
        m_max_attrs = int(m_max_attrs)
    except: # Takes a default value
        m_max_attrs = 2
    
    return selected_item, m_max_attrs

def Select_multi_items(list_item,mode='multiple', fact=2, win_widthmm=80, win_heightmm=100, font_size=16): 

    """interactive selection of items among the list list_item
    
    Args:
        list_item (list): list of items used for the selection
        
    Returns:
        val (list): list of selected items without duplicate
        
    """
    # Standard library imports
    import os
    import tkinter as tk
    import tkinter.font as TkFont
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
    
    global val
    
    def selected_item():
        global val
        val = [listbox.get(i) for i in listbox.curselection()]
        if os.name == 'nt': window.destroy()
    
    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title
    if mode == 'single': 
        title = 'Single item selection'
    else:
        title = 'Multiple items selection'
    
    # Creating the gui window 
    window = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))     
    #win_heightpx = '500'
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50)
    
    window.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    window.attributes("-topmost", True)
    window.title(title)

    yscrollbar = tk.Scrollbar(window)
    yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
    selectmode = tk.MULTIPLE
    if mode == 'single':selectmode = tk.SINGLE
    listbox = tk.Listbox(window, width=40, height=10, selectmode=selectmode,
                     yscrollcommand = yscrollbar.set)

    x = list_item
    for idx,item in enumerate(x):
        listbox.insert(idx, item)
        listbox.itemconfig(idx,
                           bg = "white" if idx % 2 == 0 else "white")

    btn = tk.Button(window, text='OK', command=selected_item)
    btn.pack(side='bottom')

    listbox.pack(padx = 10, pady = 10,expand = tk.YES, fill = "both")
    yscrollbar.config(command = listbox.yview)
    
    window.mainloop()
    
    return val

def filter_item_selection(fact=2, win_widthmm=80, win_heightmm=100, font_size=16):
    
    '''
    Selection of item to be modifyed in the filter configuration
    
    Arguments: none
    
    Returns:
        selected_item (string): acronyme of the selected item.


    '''
    # Standard library imports
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    import tkinter.font as TkFont
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS,GUI_DISP
    
    global selected_item

    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[GUI_DISP]['ppi']
    
    # Setting the window title    
    title = 'Filter-item selection GUI'
    
    # Creating the gui window 
    tk_root = tk.Tk()
    
    # Setting the window geometry parameters
    font_title = TkFont.Font(family='arial', size=font_size, weight='bold')
    title_widthmm,_ = _str_size_mm(title, font_title, ppi)
    win_widthmm = max(title_widthmm*fact,win_widthmm)
    win_widthpx = str(_mm_to_px(win_widthmm,ppi)) 
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))     
    #win_heightpx = '500'
    #win_heightpx = '520'
    win_xpx = str(int(DISPLAYS[GUI_DISP]['x']) + 50)
    win_ypx = str(int(DISPLAYS[GUI_DISP]['y']) + 50)

    tk_root.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')
    tk_root.title(title) 
    tk_root.attributes("-topmost", True)
    
    item_choice = ttk.LabelFrame(tk_root, text=' Item selection ')
    item_choice.grid(column=0, row=0, padx=8, pady=4)
       
    selected_item = 'AK'  # Default value
    def _choice(text, v):
        global selected_item
        selected_item = FILTERS_ITEMS_DICT[text]
    
    def _help():
        messagebox.showinfo("coupling selection info", COOC_SELECTION_HELP_TEXT)
        
        
    #           Choice of the item for the coupling graph completion
    # -------------------------------------------------------------------------------------------
    item = [(x,i) for i,x in enumerate(FILTERS_ITEMS_DICT.keys())]
    varitem = tk.IntVar()

    ttk.Label(item_choice, 
              text='Choose an item to be modifyed in the filter configuration:').grid(column=0, row=1, padx=8, pady=4)
    
    idx_row = 2
    for txt, val in item:
        tk.Radiobutton(item_choice, text=txt, variable=varitem, value=val,
            command=lambda t = txt, v=varitem: choice(t, v)).grid(column=0, row=idx_row+2, padx=8, pady=4,sticky=tk.W)
        idx_row += 1
     
    tk_root.mainloop()

    return selected_item

def select_folder_gui(in_dir,title):
    
    '''
    Interactive selection of a folder.
    
    Args: 
        in_dir (str): name of the initial folder.
        title (str): title of the tk window. 
    
    Returns:
        `(str)`: name of the selected folder

    '''
    # Standard library imports
    import os
    import re
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    
    global out_dir
    
    # set the tk window geometry 
    width = 10 * len(title + 5 * ' ')
    height = "210"
    
    win = tk.Tk()
    win.attributes("-topmost", True)
    win.geometry(str(width) + 'x' + str(height) )
    win.title('Folder selection window') 
    
    folder_select = tk.LabelFrame(win, text=title, font=('Aerial 18 bold'))
    folder_select.grid(column=0, row=0, padx=30, pady=4)
    
    folder_choice = tk.LabelFrame(win, text='Selected folder', font=('Aerial 18 bold'))
    folder_choice.grid(column=0, row=1, padx=30, pady=4)
    
    help_choice = tk.LabelFrame(win)
    help_choice.grid(column=0, row=2, padx=30, pady=4)
    
    def outdir_folder_choice():
        global out_dir
        out_dir = filedialog.askdirectory(initialdir=in_dir,title=title)
        thr = 0.6 * len(title + 5 * ' ')
        pos_list = [m.start() for m in re.finditer(r'[\\/]', out_dir)]
        for i in range(len(pos_list)):
            if pos_list[-i] >= thr : mid_pos = i
        out_dir1 = str(out_dir)[0:pos_list[-mid_pos]]
        out_dir2 = str(out_dir)[pos_list[-mid_pos]:]
        folder_label1 = ttk.Label(folder_choice, text=out_dir1, font=13)
        folder_label1.grid(column=0, row=1, padx=8, pady=4)
        out_dir2 = str(out_dir)[pos_list[-mid_pos]:]
        folder_label2 = ttk.Label(folder_choice, text=out_dir2, font=13)
        folder_label2.grid(column=0, row=2, padx=8, pady=4)
    
    def help():
        messagebox.showinfo('Folder selection info', '')
    
    outdir_button = ttk.Button(folder_select,text='Select',command=outdir_folder_choice)
    outdir_button.grid(column=0, row=1, padx=40, pady=4)

    help_button = ttk.Button(help_choice, text="HELP", command=help)
    help_button.grid(column=0, row=1, padx=20, pady=4)
    
    
    if os.name == 'nt': # Work with Windows not MacOS
        tk.Button(folder_choice, text="EXIT", command=win.destroy).grid(column=1, row=1, padx=8, pady=4)
    
    win.mainloop()
    
    return out_dir


############## New GUIs #######################################################################


def _str_size_mm(text, font, ppi):
    '''The function `_str_size_mm` computes the sizes in mm of a string.

    Args:
        text (str): the text of which we compute the size in mm.
        font (tk.font): the font of the text.
        ppi (int): pixels per inch of the display.

    Returns:
        `(tuple)`: width in mm `(float)`, height in mm `(float)`.

    Note:
        The use of this function requires a tkinter window availability 
        since it is based on a tkinter font definition.

    '''

    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM
       
    (w_px,h_px) = (font.measure(text),font.metrics("linespace"))
    w_mm = w_px * IN_TO_MM / ppi
    h_mm = h_px * IN_TO_MM / ppi

    return (w_mm,h_mm )


def _str_max_len_mm(list_strs,font,ppi): 
    '''The `_str_max_len_mm`function gets the maximum length in mm of a list of strings 
       given the font and the ppi of the used display and using the `_str_size_mm` function .
       
    Args:
        list_strs (list): list of strings to be sized to get their maximum length.
        font (tk.font): the font used for the strings size evaluation in mm.
        ppi (int): pixels per inch of the display.
        
    Returns:
        `(float)`: maximum length in mm of the strings in `list_strs`.
    '''                   
    
    max_length_mm = max([_str_size_mm(value, font, ppi)[0] 
                         for value in list_strs])
    return max_length_mm


def _mm_to_px(size_mm,ppi,fact=1.0):
    '''The `_mm_to_px' function converts a value in mm to a value in pixels
    using the ppi of the used display and a factor fact.
    
    Args:
        size_mm (float): value in mm to be converted.
        ppi ( float): pixels per inch of the display.
        fact (float): factor (default= 1).
        
    Returns:
        `(int)`: upper integer value of the conversion to pixels
        
    '''
    
    # Standard library imports 
    import math
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM

    size_px = math.ceil((size_mm * fact / IN_TO_MM) * ppi)
    
    return size_px


def _split_path2str(in_str,sep,max_px,font,ppi):
    '''The `_split_path2str` function splits the `in_str` string 
    in substrings of pixels sizes lower than `max_px` using the separator `sep` .

    Args:
        in_str (str): the full path of a folder.
        sep (str): the character to be find in `in_str`.
        max_px (int): the maximum size in pixels for the substrings 
                      that should result from the split of `in-dir`.
        font (tk.font): the font used for the substrings size evaluation in mm.
        ppi (float): pixels per inch of the display.

    Returns:
        `(tuple)`: tuple of the substrings resulting from the split of `in-dir`.

    Note:
        The use of this function requires a tkinter window availability 
        since it is based on a tkinter font definition.

    '''        

    # Standard library imports 
    import numpy as np
    import re

    len_in_str,_ = _str_size_mm(in_str, font, ppi)
    if _mm_to_px(len_in_str,ppi)>int(max_px):
        pos_list = np.array([m.start() for m in re.finditer(r'[\\' + sep + ']', in_str)])
        list_len = [_mm_to_px(_str_size_mm(in_str[0:pos_slash], font, ppi)[0],ppi)
                    for pos_slash in pos_list ]
        try:
            pos_mid = pos_list[np.min(np.where(np.array(list_len) >= int(max_px))) - 1]
        except:
            pos_mid = pos_list[-1]
        out_str1 = str(in_str)[0:pos_mid]
        out_str2 = str(in_str)[pos_mid:]

    else:
        out_str1 = str(in_str)
        out_str2 = ''

    return (out_str1,out_str2)


def _gui_params(titles, buttons_labels, fonts, mm_size_corr, 
                gui_disp, widget_ratio, 
                button_ratio, max_lines_nb):
    
    '''The function `_gui_params` define the geometry parameters in pixels for a gui window.
    
    Args: 
        titles (dict): titles of the window.
        buttons_labels(list): list of button labels as strings.
        gui_disp (int): number identifying the used display.
        mm_size_corr (int): value in mm for the correction of the sizes in milimeters
                            before use for computing the widgets horizontal positions in pixels
                            (correction still to be understood).
        widget_ratio (float): base ratio for defining the different widget ratio.
        button_ratio (float): buttons-height to the label-height ratio 
                              to vertically center the label in the button.
        max_lines_nb (int): maximum lines number for editing the selected folder name.                    
    
    Returns:
        `(named tupple)`: display ppi and sizes and positions of the window widgets in pixels.
        
    Note:
        Uses the globals: `IN_TO_MM`, `DISPLAYS`.
        Based on two frames in the main window and two buttons in the top frame.
    
    '''

    # standard library imports
    from collections import namedtuple
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM
    
    ############# Local parameters setting ############# 

    # Getting the ppi of the selected prime display.
    ppi = DISPLAYS[gui_disp]['ppi']
    
    # Checking the number of frames and buttons.
    frames_nb = len(titles) - 1 
    buttons_nb = len(buttons_labels)
    if frames_nb!=1 or buttons_nb!=2:
        print('Number of titles:', len(titles) )
        print('Number of buttons:', len(button_labels) )
        print('The number of titles should be 2 \
               and the number of buttons should be 2.\
               Please define ad hoc number of widgets.')             
    
    # Setting the ratio of frames-width to the titles-max-width.
    frame_ratio = widget_ratio
    
    # Setting the ratio of window-width to the frame-width.
    win_ratio = widget_ratio 
    
    # Setting a potential ratio for correcting the conversion from mm to px for the buttons sizes.
    # Todo: adapt these ratios to correct the discrepancy between the set mm sizes 
    # and the effective mm sizes on the screen for MacOs 
    # (correction still to be understood).
    buttonsize_mmtopx_ratios = (1,1,1)

    # Computing the maximum size in mm of the list of titles.
    titles_mm_max = _str_max_len_mm(titles.values(), fonts['frame'], ppi)
    
    # Computing button sizes in mm and pixels using button label sizes and button_ratio.
    # Buttons width is the button heigth added to the labels width 
    # to horizontally center the label in the button. 
    labels_widthmm = [_str_size_mm(buttons_labels[i],fonts['button'], ppi)[0] for i in range(buttons_nb)]
    label_heightmm = _str_size_mm(buttons_labels[0],fonts['button'], ppi)[1]
    button_heightmm =  label_heightmm * button_ratio
    buttons_widthmm = (labels_widthmm[0] + button_heightmm, labels_widthmm[1] + button_heightmm)
    buttons_widthpx = (_mm_to_px(buttons_widthmm[0],ppi,buttonsize_mmtopx_ratios[0]), 
                       _mm_to_px(buttons_widthmm[1],ppi,buttonsize_mmtopx_ratios[1]))
    button_heigthpx = _mm_to_px(button_heightmm,ppi,buttonsize_mmtopx_ratios[2])

    # Computing the frame width in pixels from titles maximum size in mm using frame_ratio.
    frame_widthmm = titles_mm_max * frame_ratio    
    frame_widthpx = str(_mm_to_px(frame_widthmm,ppi))

    # Computing the window width in pixels from the frame width and buttons width using win_ratio.
    win_widthmm = max(frame_widthmm,sum(buttons_widthmm)) * win_ratio 
    win_widthpx = str(_mm_to_px(win_widthmm,ppi))

     # Computing the buttons horizontal positions in pixels 
     # assuming 2 buttons and with correction of size in mm by mm_size_corr value.
    padx_ratio = buttons_nb * 2  
    pad_xmm = (win_widthmm - min(frame_widthmm,sum(buttons_widthmm))) / padx_ratio
    buttons_xmm = (pad_xmm, buttons_widthmm[0] + 3 * pad_xmm)
    buttons_xpx = (_mm_to_px(buttons_xmm[0] - mm_size_corr,ppi), _mm_to_px(buttons_xmm[1] - mm_size_corr,ppi))

    # Computing the frames heigth unit.
    _, text_heigthmm = _str_size_mm('Users/',fonts['text'], ppi)
    frame_unit_heightmm = min(button_heightmm,text_heigthmm) 
    frame_unit_heightpx = _mm_to_px(frame_unit_heightmm,ppi)

    # Computing the buttons vertical position in pixels.
    button_ymm = frame_unit_heightmm 
    button_ypx = _mm_to_px(button_ymm,ppi)

    # Computing the frame heigth in mm and in pixels.
    pads_nb = 4  # 2 frame units above and 2 frame units under the edited text. 
    max_frame_unit_nb = pads_nb + max_lines_nb  
    frame_heightmm = frame_unit_heightmm * max_frame_unit_nb
    frame_heightpx = str(_mm_to_px(frame_heightmm,ppi))

    # Computing the frame positions in pixels.
    frame_xmm = (win_widthmm - frame_widthmm) / 2
    frame_ymm = button_ymm + button_heightmm + 2 * frame_unit_heightmm
    frame_xpx, frame_ypx = _mm_to_px(frame_xmm,ppi), _mm_to_px(frame_ymm,ppi)

    # Computing the window heigth in mm and in pixels .
    # with frame_unit_heightmm separating vertically the widgets.
    win_heightmm = button_ymm + button_heightmm + frame_heightmm + 3 * frame_unit_heightmm
    win_heightpx = str(_mm_to_px(win_heightmm,ppi))

    # Setting the window geometry.
    win_xpx = str(int(DISPLAYS[gui_disp]['x']) + 50)
    win_ypx = str(int(DISPLAYS[gui_disp]['y']) + 50)
    
    # Defining the named tuple template for the results returned
    named_tup_button = namedtuple('button', ['buttons_widthpx', 'button_heigthpx', 'buttons_xpx', 'button_ypx'])
    named_tup_frame = namedtuple('frame', ['frame_widthmm', 'frame_unit_heightpx', 'frame_widthpx', 'frame_heightpx', 'frame_xpx', 'frame_ypx'])
    named_tup_win = namedtuple('win', ['win_widthpx', 'win_heightpx', 'win_xpx', 'win_ypx'])   
    named_tup_results = namedtuple('results', ['ppi','button_params', 'frame_params', 'win_params',])
    
    # Setting the named tuple for the results returned
    button_params = named_tup_button(buttons_widthpx, button_heigthpx, buttons_xpx, button_ypx,)
    frame_params = named_tup_frame(frame_widthmm, frame_unit_heightpx, frame_widthpx, frame_heightpx, frame_xpx, frame_ypx,)
    win_params = named_tup_win(win_widthpx, win_heightpx, win_xpx, win_ypx,)
    gui_params = named_tup_results(ppi,button_params, frame_params, win_params,)
    
    return  gui_params


def select_folder_gui_new(in_dir, titles, buttons_labels, 
                          gui_disp=0, widget_ratio=None, 
                          button_ratio=None, max_lines_nb=None):

    
    ''' The function `select_folder_gui_new` allows the interactive selection of a folder.
    Args: 
        in_dir (str): name of the initial folder.
        titles (dict): title of the tk window.
        buttons_labels(list): list of button labels as strings.
        gui_disp (int): number identifying the used display (default: 0).
        widget_ratio (float): base ratio for defining the different widget ratii
                              (default: `GUI_WIDGET_RATIO` global).
        button_ratio (float): buttons-height to the label-height ratio 
                              to vertically center the label in the button
                              (default: `GUI_BUTTON_RATIO` global).
        max_lines_nb (int): maximum lines number for editing the selected folder name
                            (default: `GUI_TEXT_MAX_LINES_NB` global).
    
    Returns:
        `(str)`: name of the selected folder.
        
    Note:
        Uses the globals: `IN_TO_MM`, `DISPLAYS`, `FOLDER_SELECTION_HELP_TEXT`,
                          `GUI_BUTTON_RATIO`, `GUI_TEXT_MAX_LINES_NB` and `GUI_WIDGET_RATIO`.
        Based on two frames in the main window and two buttons in the top frame.
    
    '''

    # Standard library imports 
    import math
    import re
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import filedialog
    import tkinter.font as TkFont
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSys import DISPLAYS
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_SELECTION_HELP_TEXT
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import GUI_BUTTON_RATIO, GUI_TEXT_MAX_LINES_NB, GUI_WIDGET_RATIO
    
    global out_dir
 
    ############# Definition of local functions #############    

    def _outdir_folder_choice():
        '''The function `_outdir_folder_choice' allows the interactive choice of a folder, 
        puts it in the `out_dir` global variable and prints the result in the `folder_choice` frame.

        '''
        # Standard library imports
        import numpy as np

        global out_dir
        
        # Setting the value in mm for the correction of the sizes in milimeters 
        # before use for computing the widgets horizontal positions in pixels 
        # (correction still to be understood).
        mm_size_corr = 1

        out_dir = filedialog.askdirectory(initialdir=in_dir,title=titles['main'])
        
        out_dir_split = [out_dir]
        while out_dir_split[len(out_dir_split)-1]!='':
            out_dir1,out_dir2 = _split_path2str(out_dir_split[len(out_dir_split)-1], 
                                               '/', frame_widthpx, fonts['text'], ppi)
            out_dir_split[len(out_dir_split)-1] = out_dir1
            out_dir_split.append(out_dir2)

         # Creating the folder-result frame and set its geometry. 
        folder_result = tk.LabelFrame(master=win,              
                        text=titles['result'],
                        font= fonts['frame'])
        folder_result.place(x=frame_xpx,
                            y=frame_ypx,
                            width=frame_widthpx,
                            height=frame_heightpx)

         # Editing the selected folder.       
        text_max_widthmm = _str_max_len_mm(out_dir_split, fonts['text'], ppi)
        text_xmm = (frame_widthmm - text_max_widthmm) / 2
        text_xpx = _mm_to_px(text_xmm - mm_size_corr,ppi)
        text_ypx = frame_unit_heightpx       
        text = '\n'.join(out_dir_split)
        folder_label = tk.Label(folder_result, text=text, font=fonts['text'])
        folder_label.place(x=text_xpx,
                           y=text_ypx)
    
    def _help():
        messagebox.showinfo('Folder selection info', FOLDER_SELECTION_HELP_TEXT)
        
    # Setting the value in mm for the correction of the sizes in milimeters 
    # before use for computing the widgets horizontal positions in pixels 
    # (correction still to be understood).
    mm_size_corr = 1
    
        # Setting geometry parameters of gui widgets
    if widget_ratio==None: widget_ratio = GUI_WIDGET_RATIO
    if button_ratio==None: button_ratio = GUI_BUTTON_RATIO
    if max_lines_nb==None: max_lines_nb = GUI_TEXT_MAX_LINES_NB  
   
    ############# Tkinter window management #############
    
     # Creating the tk window.
    win = tk.Tk()
    win.attributes("-topmost", True)
    win.title(titles['main']) 
    
     # Setting the fonts to be used.
    fonts = {}
    fonts = {'frame': TkFont.Font(family='arial', size=16, weight='bold'),
             'text':  TkFont.Font(family='arial', size=12, weight='normal'),
             'button':TkFont.Font(family='arial', size=12, weight='normal'),}
    
     # Get the gui geometry parameters
    gui_params = _gui_params(titles, buttons_labels, fonts, mm_size_corr, 
                             gui_disp, widget_ratio = widget_ratio, 
                             button_ratio = button_ratio, max_lines_nb = max_lines_nb)
    
    ppi = gui_params.ppi
    
    buttons_widthpx = gui_params.button_params.buttons_widthpx
    button_heigthpx = gui_params.button_params.button_heigthpx
    buttons_xpx = gui_params.button_params.buttons_xpx
    button_ypx = gui_params.button_params.button_ypx
    
    frame_widthmm = gui_params.frame_params.frame_widthmm
    frame_unit_heightpx = gui_params.frame_params.frame_unit_heightpx
    frame_widthpx = gui_params.frame_params.frame_widthpx
    frame_heightpx = gui_params.frame_params.frame_heightpx
    frame_xpx = gui_params.frame_params.frame_xpx
    frame_ypx = gui_params.frame_params.frame_ypx
    
    win_widthpx = gui_params.win_params.win_widthpx
    win_heightpx = gui_params.win_params.win_heightpx
    win_xpx = gui_params.win_params.win_xpx
    win_ypx = gui_params.win_params.win_ypx    

     # Setting the window geometry.
    win.geometry(f'{win_widthpx}x{win_heightpx}+{win_xpx}+{win_ypx}')

     # Creates the folder result frame and set its geometry. 
    folder_result = tk.LabelFrame(master=win,              
                text=titles['result'],
                font=fonts['frame'])
    folder_result.place(x=frame_xpx,
                    y=frame_ypx,
                    width=frame_widthpx,
                    height=frame_heightpx)

     # Creating the button for folder selection.
    select_button = tk.Button(win,
                          text=buttons_labels[0],
                          font=fonts['button'],
                          command=_outdir_folder_choice)
    select_button.place(x=buttons_xpx[0], 
                    y=button_ypx, 
                    width=buttons_widthpx[0], 
                    height=button_heigthpx)

     # Creating the help button.
    help_button = tk.Button(win,
                        text=buttons_labels[1],
                        font=fonts['button'],
                        command=_help)
    help_button.place(x=buttons_xpx[1], 
                  y=button_ypx, 
                  width=buttons_widthpx[1], 
                  height=button_heigthpx)

    win.mainloop()
    
    return out_dir

