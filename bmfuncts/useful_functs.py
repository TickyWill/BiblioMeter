"""Module of useful functions used by several modules of package `bmfuncts`.
"""

__all__ = ['build_list_from_str',
           'build_string_from_list',
           'concat_dfs',
           'create_archi',
           'create_folder',
           'drop_multiple_item',
           'get_sheet_names',
           'keep_initials',
           'name_capwords',
           'print_step_text',
           'print_step_title',
           'print_to_console',
           'print_to_log',
           'reorder_df',
           'save_xlsx_file',
           'set_bold_txt',
           'set_capwords_lambda',
           'set_print_same_len',
           'set_year_pub_id',
           'standardize_firstname_initials',
           'standardize_full_name_order',
           'standardize_txt',
           'try_save_excel_data',
          ]


# Standard library imports
import numpy as np
import os
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# 3rd party imports
import pandas as pd
from bpfuncts import remove_special_symbol as bp_remove_special_symbol

# local imports
import bmfuncts.pub_globals as bm_pg


def print_step_title(step_title, print_params):
    """Prints to console and to log file the step title

    Args:
        step_title (str)= The title to print.
        print_params (list): Composed of the name of the TXT log file \
        to which ".txt" extension is added, of the name of the log folder \
        where the TXT log file is saved and of the full path to the working \
        folder where the log folder is saved.
    """
    print_txt = ""
    print_to_console(step_title, print_txt)
    print_to_log(step_title, print_txt, print_params, log_init=False)


def print_step_text(step_txt, print_params):
    """Prints to console and to log file the step text.

    Args:
        step_txt (str)= The text to print.
        print_params (list): Composed of the name of the TXT log file \
        to which ".txt" extension is added, of the name of the log folder \
        where the TXT log file is saved and of the full path to the working \
        folder where the log folder is saved.
    """
    print_title = ""
    print_to_console(print_title, step_txt)
    print_to_log(print_title, step_txt, print_params, log_init=False)


def print_to_console(title, print_txt):
    """Sends prints to console.

    The title format and the other prints color are set through \
    the `set_bold_txt` function of the same module.

    Args:
        title (str): Title of the prints.
        print_txt (str): Corps of the prints.
    """
    if title and print_txt:
        full_print_txt = f"\n\n{set_bold_txt(title)}" + print_txt
    elif title:
        full_print_txt = f"\n\n{set_bold_txt(title)}"
    else:
        full_print_txt = print_txt
    print(full_print_txt)


def print_to_log(title, print_txt, print_params, log_init=True):
    """Sends prints to a TXT log file.

    Args:
        title (str): Title of the prints.
        print_txt (str): Corps of the prints.
        print_params (list): Composed of the name of the TXT log file \
        to which ".txt" extension is added, of the name of the log folder \
        where the TXT log file is saved and of the full path to the working \
        folder where the log folder is saved.
        log_init (bool): Optional (default: true), if True, the title is surrounded by \
        "*" lines and it is headed by "* " and ended by " *", "otherwise, \
        the title is only headed by '# '.
    """
    log_file, log_folder, wf_path = print_params
    txt_log_file = log_file +'.txt'
    log_files_path = Path(wf_path) / Path(log_folder)
    txt_log_file_path = log_files_path / Path(txt_log_file)
    if not os.path.exists(log_files_path):
        os.makedirs(log_files_path)
    os.chdir(log_files_path)

    full_print_txt = print_txt
    if log_init:
        full_title_len = len(title) + 4
        title_line = "".join(["*"] * full_title_len)
        title_sup_line = "\n" + title_line + "\n* "
        title_inf_line = " *\n" + title_line
        full_print_txt = f"\n{title_sup_line}{title}{title_inf_line}{print_txt}"
    else:
        if title:
            title_start = "# "
            full_print_txt = f"\n{title_start}{title}"
        if print_txt:
            full_print_txt = print_txt

    if log_init or not txt_log_file_path.is_file():
        with open(txt_log_file, 'w', encoding='utf-8') as f:
            print(full_print_txt, file=f)
    else:
        with open(txt_log_file, 'a', encoding='utf-8') as f:
            print(full_print_txt, file=f)
    os.chdir(wf_path)


def try_save_excel_data(df, file_path):
    """Saves data as XLSX file by making sure the file is closed in case it already exists.

    Args:
        df (dataframe): The data to save.
        file_path (path): The full path to the file where data will be saved.
    """
    closed = False
    rep = "N"
    while not closed:
        print("Trying to save data...", end="\r")
        try:
            df.to_excel(file_path, index=False)
            print(f"Data saved in the file:\n        {file_path}")
            closed = True
        except PermissionError:
            while rep!="Y":
                rep = input("    !!!-Permission denied-!!! Close all opened XLSX files (Y/N)?")
            os.system('TASKKILL /F /IM excel.exe')


def get_sheet_names(file_path):
    """Gets the sheet names of an multisheet XLSX file whithout loading it.

    Args:
        file_path (path): The full path to the file.
    Returns:
        (list): Composed of the sheet names(str).
    """
    search_str = ".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"
    with zipfile.ZipFile(file_path, "r") as z:
        xml_content = z.read("xl/workbook.xml")
        root = ET.fromstring(xml_content)
        sheet_names = [sheet.attrib["name"] for sheet in root.findall(search_str)]
        return sheet_names


def set_bold_txt(txt):
    """Builds a bold text using a dict from globals 
    imported from `bmfuncts.pub_globals` module.

    Args:
        txt (str): The string to be formatted to bold characters.
    Returns:
        (str): The bold text.
    """
    bold_txt = f"{bm_pg.PRINT_DICT['end']}{bm_pg.PRINT_DICT['bold']}{txt}{bm_pg.PRINT_DICT['blue']}"
    return bold_txt


def set_print_same_len(txts_list):
    """Builds strings of same lengths by addition of spaces for prints.

    The function builds a dict keyed by the initial string and valued by 
    the same string added with spaces to reach the same length as 
    the maximum string length of the passed list of strings.

    Args:
        txts_list (list): The strings to be added with spaces \
        for reaching the maximum string length.
    Returns:
        (dict): The built dict.
    """
    max_len = np.max([len(x) for x in txts_list])
    print_txts_list = [x + ' ' * (max_len - len(x)) for x in txts_list]
    print_txts_dict = dict(zip(txts_list, print_txts_list))
    return print_txts_dict


def build_list_from_str(input_str, sep_str):
    """Builds a list of strings by split of the input string using 
    the specified separator.

    Args:
        input_str (str): The string to be split.
        sep_str (str): The separator to be used for the split \
        including space if required.
    Returns:
        (list): The built list of strings.
    """
    if sep_str in input_str:
        txts_list = input_str.split(sep_str)
        output_list = [x.strip() for x in txts_list]
    else:
        output_list = [input_str.strip()]
    return output_list


def build_string_from_list(input_list, sep_str):
    """Builds a string by joining the items of the input list using 
    the specified separator.

    Args:
        input_list (list): The list of string items to be joined.
        sep_str (str): The separator to be used for the join \
        including space if required.
    Returns:
        (str): The built string.
    """
    items_nb = len(input_list)
    if items_nb>1:
        output_str = sep_str.join(input_list)
    elif items_nb==1:
        output_str = str(input_list[0])
    else:
        output_str = ""
    return output_str


def drop_multiple_item(init_list, item):
    """Keeps only one occurrence of an item value in a list.

    Args:
        init_list (list): The list of string items to be modified.
        item (str): The item value to be kept only once.
    Returns:
        (list): The modified list.
    """
    final_list = init_list
    while item in final_list and len(final_list)>1:
        item_idx = final_list.index(item)
        del final_list[item_idx]
    return final_list


def reorder_df(df, col_dict):
    """Reorders data by modifying the order of the columns using 
    the given index for each column to be moved.

    A positive index gives the effective position of the column in 
    the reordered list of the columns. 
    A negative index means that the column is to be added at the end 
    of the reordered list of the columns. The lowest negative index 
    corresponds to the first added column among the columns to be added 
    at the end.

    Args:
        df (dataframe): The data to be reordered.
        col_dict (dict); Dict keyed by the names (str) of the column \
        to be moved and valued by the indices (int) of the columns \
        in the reordered list of columns.
    Returns:
        (dataframe): The reordered data.
    """
    df = df.reset_index()
    if "index" in df.columns:
        df = df.drop(columns="index")
    init_cols = list(df.columns)
    new_cols = init_cols.copy()
    append_cols_dict = {}
    for col, col_idx in col_dict.items():
        if col_idx>=0:
            init_col_idx = init_cols.index(col)
            new_cols.remove(col)
            new_cols.insert(col_idx, init_cols[init_col_idx])
        if col_idx<0:
            append_cols_dict[col] = col_idx
    while append_cols_dict:
        col_idx_min = min(append_cols_dict.values())
        reverse_cols_dict = dict(map(reversed, append_cols_dict.items()))
        col_min = reverse_cols_dict[col_idx_min]
        new_cols.remove(col_min)
        new_cols.append(col_min)
        del append_cols_dict[col_min]
    df = df[new_cols]
    return df


def name_capwords(text):
    """Capitalizes words in full names of authors getting 
    rid of particular separators and keeping firstname initials.

    Args:
        text (str): Full name to be capitalized by words.
    Returns:
        (str): Full name capitalized by words.
    """
    sep_list = ["-", "'"]
    sub_text_list = text.split()[:-1]
    text_split_list = []
    for sub_text in sub_text_list:
        for sep in sep_list:
            if sep in sub_text:
                words_list = [x.capitalize() for x in sub_text.split(sep)]
                sub_text = sep.join(words_list)
            else:
                sub_text = sub_text.capitalize()
        text_split_list.append(sub_text)
    text_split_list.append(text.split()[-1])
    text = " ".join(text_split_list)
    return text


def standardize_full_name_order(author):
    """Sets the first-name initials before the last name in a full name.

    It appends "." after each initial and takes care of keeping '-'
    between the parts of composed first names.

    Args:
        author (str): Full name to transform (expected shape 'NAME IJ', \
        where 'NAME' is the last name and 'IJ' the first name initials).
    Returns:
        (str): The transformed full name (ex: I. J. Name).
        """
    author_parts_list = author.split(" ")
    author_initials = author_parts_list[-1]
    if "-" in author_initials:
        author_initials_list = author_initials.split("-")
        new_author_initial_list = []
        for author_initial in author_initials_list:
            new_author_initial = author_initial + "."
            new_author_initial_list.append(new_author_initial)
        new_author_initials = "-".join(new_author_initial_list) + " "
    else:
        new_author_initial_list = [x + ". " for x in author_initials]
        new_author_initials = "".join(new_author_initial_list)
    last_name_parts_list = [x.capitalize() for x in author_parts_list[:-1]]
    last_name = " ".join(last_name_parts_list)
    new_author = "".join([new_author_initials] + [last_name])
    return new_author


def _set_capwords(text):
    """Capitalizes words in text except those given 
    by the 'BM_LOW_WORDS_LIST' global import from globals 
    module imported as bm_pg.

    Args:
        text (str): Text to be capitalized by words.
    Returns:
        (str): Text capitalized by main words.
    """
    text_list = []
    for sub_text in text.split("; "):
        space_split_list = []
        for x in sub_text.split():
            if x.lower() in bm_pg.BM_LOW_WORDS_LIST:
                x = x.lower()
            else:
                x = x.capitalize()
            space_split_list.append(x)
        sub_text = " ".join(space_split_list)
        text_list.append(sub_text)
    text = "; ".join(text_list)
    return text


def set_capwords_lambda(col):
    """Build lambda function based on `_set_capwords` 
    internal function.

    Args:
        col (str): Name of the column to be modified.
    Return:
        (lambda function): Function to be applied by rows.
    """
    return lambda row: _set_capwords(row[col])


def keep_initials(df, initials_col_base, missing_fill=None):
    """Keeps the first-name initials avoiding setting them to NaN 
    when they are equal to 'NA'.

    Args:
        df (dataframe): Data where the first-name initials are kept.
        initials_col_base (str): Base of the column names \
        of first_name initials.
        missing_fill (str): Optional value for replacing NaN \
        in the other columns (default = None).
    Returns:
        (dataframe): The modified dataframe.
    """
    df_cols = list(df.columns)
    df_initials_cols = [x for x in df_cols if initials_col_base in x]
    for col in df_initials_cols:
        df[col] = df[col].fillna("NA")
    if missing_fill:
        df_fill_na_cols = list(set(df_cols) - set(df_initials_cols))
        for col in df_fill_na_cols:
            df[col] = df[col].fillna(missing_fill)
    return df


def save_xlsx_file(root_path, df, file_name):
    """Saves data as an xlsx file that is one sheet and not formatted.

    Args:
        root_path (path): The path to the folder where the Excel file is saved.
        df (dataframe): The data to save.
        file_name (str): The name of the file including '.xlsx' extent.
    """
    file_path = root_path / Path(file_name)
    df.to_excel(file_path, index=False)


def set_year_pub_id(df, year, pub_id_col):
    """Transforms the pub-ID column of 'df' data by adding "yyyy_" 
    (year in 4 digits) to the values.

    Args:
        df (pandas.DataFrame): The data we want to modify.
        year (str): The 4 digits year to add as "yyyy".
        pub_id_col (str): The name of the pub-ID column to transform.
    Returns:
        (pandas.DataFrame): The data with its changed column.
    """
    new_df = df.copy()
    def _rename_pub_id(old_pub_id, _year):
        pub_id_str = str(int(old_pub_id))
        while len(pub_id_str)<3:
            pub_id_str = "0" + pub_id_str
        new_pub_id = str(int(_year)) + '_' + pub_id_str
        return new_pub_id
    new_df[pub_id_col] = new_df[pub_id_col].apply(lambda x: _rename_pub_id(x, year))
    return new_df


def concat_dfs(dfs_list, dedup=True, dedup_cols=None, keep='first', axis=0,
               concat_ignore_index=False, drop_ignore_index=False):
    """Allows to avoid warnings when using pandas concat of a list of dataframes 
    with empty dataframe in it and drops duplicates in the concatenated dataframe.

    Args:
        dfs_list (list): The list of pandas dataframes to concatenate.
        dedup (bool): If true, deduplication is applied, optional, default:True.
        dedup_cols (list): Same as 'subset' parameter of 'drop_duplicates' method \
        of 'pandas.DataFrame' method, optional, default:None.
        keep (str): Same as 'keep' parameter of 'drop_duplicates' method \
        of 'pandas.DataFrame' method, optional, default:'first'.
        axis (int): Same as 'axis' parameter of 'concat' method of 'pandas.DataFrame' \
        method, optional, default:0.
        concat_ignore_index (bool): Same as 'ignore_index' parameter of concat \
        method of 'pandas.DataFrame' method, optional, default:False.
        drop_ignore_index (bool): Same as 'ignore_index' parameter of drop_duplicates \
        method of 'pandas.DataFrame' method, optional, default:False.
    Returns:
        (dataframe): Result of the concatenation.
    """

    # Setting list of not empty dataframes
    dfs_clean_list = []
    for df in dfs_list:
        if not df.empty:
            dfs_clean_list.append(df)
    dfs_clean_nb = len(dfs_clean_list)

    # Concatenating dataframes
    if dfs_clean_nb==0:
        concat_df = dfs_list[0].copy()
    elif dfs_clean_nb==1:
        concat_df = dfs_clean_list[0].copy()
    else:
        concat_df = pd.concat(dfs_clean_list, axis=axis, ignore_index=concat_ignore_index)

    if dedup:
        keep_type = keep
        if keep=='False':
            keep_type = False
        # Removing duplicates
        full_col_list = list(concat_df.columns)
        if dedup_cols and all(i in full_col_list for i in dedup_cols):
            concat_df = concat_df.drop_duplicates(subset=dedup_cols, keep=keep_type,
                                                  ignore_index=drop_ignore_index)
        else:
            concat_df = concat_df.drop_duplicates(keep=keep_type,
                                                  ignore_index=drop_ignore_index)
    return concat_df


def standardize_firstname_initials(initials_init):
    """Standardizes the initials of a firstname by removing minus symbol 
    between initials.

    For example, changes "P-Y" into "PY"

    Args:
        initials_init (str): String containing raw firstname initials 
        to be standardized.
    Returns:
        (str): The standardized string."""
    initials_init = initials_init.replace('-',' ')
    initials = ''.join(initials_init.split(' '))
    return initials


def standardize_txt(text):
    """Standardizes text by keeping only ASCII characters
    and replacing minus symbol between words by space.

    Args:
        text (str): String to be standardized.
    Returns:
        (str): The standardized string."""
    # Removing accentuated characters
    new_text = bp_remove_special_symbol(text, only_ascii=True, strip=True)

    # Remove minus
    new_text = new_text.replace("-", " ").strip()
    return new_text


def create_folder(root_path, folder, verbose=False):
    """Creates a folder checking first if it already exists.

    Args:
        root_path (path): Full path to the folder where \
        the new folder is created.
        folder (str): Name of the folder to be created.
        verbose (bool): Optional status of prints (default = False).
    Returns:
        (path): Full path to the created folder.
    """

    folder_path = root_path / Path(folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        message = f"{folder_path} created"
    else:
        message = f"{folder_path} already exists"

    if verbose:
        print(message)
    return folder_path


def create_archi(wf_path, corpus_year_folder, create_archi_param=True, verbose=False):
    """Creates a corpus folder with optionally the required internal architecture.

    It uses the global "ARCHI_YEAR" for the names of the sub_folders 
    and the `create_folder` function of the same module.

    Args:
        wf_path (path): The full path of the working folder.
        corpus_year_folder (str): The name of the folder of the corpus.
        create_archi_param (bool): If true, a full corpus folder architecture \
        is built otherwise only the root corpus folder is created (default: True).
        verbose (bool): Optional status of prints (default:  False).
    Returns:
        (str): End message recalling the corpus-year architecture created.
    """
    # Creating folder for corpus-year working-folder
    corpus_year_folder_path = create_folder(wf_path, corpus_year_folder, verbose=verbose)
    if create_archi_param:
        # Setting useful alias
        archi_alias = bm_pg.ARCHI_YEAR
        extract_folder_alias = bm_pg.ARCHI_EXTRACT["root"]
        archiv_folder_alias = bm_pg.ARCHI_EXTRACT["archiv"]

        # Creating folders for corpus extractions from databases for the corpus year
        extract_folder_path = wf_path / Path(extract_folder_alias)
        for bdd in bm_pg.BDD_LIST:
            bdd_extract_folder_alias = bm_pg.ARCHI_EXTRACT[bdd]["root"]
            bdd_extract_folder_path = extract_folder_path / Path(bdd_extract_folder_alias)
            year_bdd_extract_folder_path = create_folder(bdd_extract_folder_path,
                                                         corpus_year_folder, verbose=verbose)
            _ = create_folder(year_bdd_extract_folder_path, archiv_folder_alias, verbose=verbose)

        # Creating architecture for corpus-year working-folder
        _ = create_folder(corpus_year_folder_path, archi_alias["bdd mensuelle"], verbose=verbose)
        _ = create_folder(corpus_year_folder_path, archi_alias["homonymes folder"], verbose=verbose)
        _ = create_folder(corpus_year_folder_path, archi_alias["OTP folder"], verbose=verbose)
        _ = create_folder(corpus_year_folder_path, archi_alias["pub list folder"], verbose=verbose)
        _ = create_folder(corpus_year_folder_path, archi_alias["history folder"], verbose=verbose)

        analysis_folder = create_folder(corpus_year_folder_path, archi_alias["analyses"],
                                        verbose=verbose)
        _ = create_folder(analysis_folder, archi_alias["if analysis"], verbose=verbose)
        _ = create_folder(analysis_folder, archi_alias["keywords analysis"], verbose=verbose)
        _ = create_folder(analysis_folder, archi_alias["subjects analysis"], verbose=verbose)
        _ = create_folder(analysis_folder, archi_alias["countries analysis"], verbose=verbose)
        _ = create_folder(analysis_folder, archi_alias["institutions analysis"], verbose=verbose)

        corpus_folder = create_folder(corpus_year_folder_path, archi_alias["corpus"], verbose=verbose)

        concat_folder = create_folder(corpus_folder, archi_alias["concat"], verbose=verbose)
        _ = create_folder(concat_folder, archi_alias["parsing"], verbose=verbose)

        dedup_folder = create_folder(corpus_folder, archi_alias["dedup"], verbose=verbose)
        _ = create_folder(dedup_folder, archi_alias["parsing"], verbose=verbose)

        scopus_folder = create_folder(corpus_folder, archi_alias["scopus"], verbose=verbose)
        _ = create_folder(scopus_folder, archi_alias["parsing"], verbose=verbose)
        _ = create_folder(scopus_folder, archi_alias["rawdata"], verbose=verbose)

        wos_folder = create_folder(corpus_folder, archi_alias["wos"], verbose=verbose)
        _ = create_folder(wos_folder, archi_alias["parsing"], verbose=verbose)
        _ = create_folder(wos_folder, archi_alias["rawdata"], verbose=verbose)

        message = f"Architecture created for {corpus_year_folder} folder"
    else:
        message = f"{corpus_year_folder} folder created"
    return message
