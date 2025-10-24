"""Module of useful functions used by several modules of package `bmfuncts`.

ToDo:
    - import `standardize_address` from BiblioParsing package.
"""

__all__ = ['concat_dfs',
           'create_archi',
           'create_folder',
           'keep_initials',
           'name_capwords',
           'read_parsing_dict',
           'reorder_df',
           'save_xlsx_file',
           'set_capwords_lambda',
           'set_rawdata',
           'set_year_pub_id',
           'standardize_firstname_initials',
           'standardize_full_name_order',
           'standardize_txt',
          ]


# Standard library imports
import csv
import os
import shutil
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.config_utils import set_user_config


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
    rid of particular separators and keeping firstname initiales.

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
        of first_name initiales. 
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
    def _rename_pub_id(old_pub_id, _year):
        pub_id_str = str(int(old_pub_id))
        while len(pub_id_str)<3:
            pub_id_str = "0" + pub_id_str
        new_pub_id = str(int(_year)) + '_' + pub_id_str
        return new_pub_id
    df[pub_id_col] = df[pub_id_col].apply(lambda x: _rename_pub_id(x, year))
    return df


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
        concat_df = pd.concat(dfs_clean_list, axis=axis,
                              ignore_index=concat_ignore_index)

    if dedup:
        keep_type = keep
        if keep=='False':
            keep_type = False
        # Removing duplicates
        full_col_list = list(concat_df.columns)
        if dedup_cols and all(i in full_col_list for i in dedup_cols):
            concat_df = concat_df.drop_duplicates(subset=dedup_cols,
                                                  keep=keep_type,
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
    new_text = bp.remove_special_symbol(text, only_ascii=True, strip=True)

    # Remove minus
    new_text = new_text.replace("-", " ").strip()
    return new_text


def _get_database_file_path(database_folder_path, database_file_end):
    """Selects the most recent file ending with 'database_file_end'.

    This is done through the following steps:

    1. Lists all the files with this ending present in the \
    folder targeted by "database_folder_path".
    2. Selects the most recent one in this list using date \
    of last modification.

    Args:
        database_folder_path (path): The path to the folder where files \
        with names ending with 'database_file_end' will be searched.
        database_file_end (str): Ending of the names of the files \
        to be searched.
    Returns:
        (path): Path targeting the file found and selected.
    """
    list_data_base = []
    for file in os.listdir(database_folder_path):
        if file.endswith(database_file_end):
            list_data_base.append(file)
    if list_data_base:
        database_file_path = database_folder_path / Path(list_data_base[0])
    else:
        database_file_path = None
    return database_file_path


def _set_database_extract_info(wf_path, datatype, database):
    """Builds the path to database extractions and the file 
    names ending that are specific to the data type 'datatype'.

    It also sets the folder name of the empty files required for 
    specific data types (ex: using only "WoS" datatype requires 
    empty files for Scopus extractions). 
    To do that, it uses the global 'ARCHI_EXTRACT' defined 
    in the module imported as bm_pg.

    Args:
        wf_path (path): The path to the working folder.
        datatype (str): The data type of data combination type \
        from databases.
        database (str): The database selected for the analysis.
    Returns:
        (tup): (path to database extractions (path), \
        file name ending (str), \
        path to the folder of empty files (path)).
    """

    # Setting useful aliases
    extraction_folder = bm_pg.ARCHI_EXTRACT["root"]
    empty_file_folder = bm_pg.ARCHI_EXTRACT["empty-file folder"]
    database_folder = bm_pg.ARCHI_EXTRACT[database]["root"]
    database_file_base = bm_pg.ARCHI_EXTRACT[database][datatype]
    database_file_extent = bm_pg.ARCHI_EXTRACT[database]["file_extent"]
    database_file_end = database_file_base + database_file_extent

    # Setting useful paths
    extraction_folder_path = wf_path / Path(extraction_folder)
    database_folder_path = extraction_folder_path / Path(database_folder)

    return database_folder_path, database_file_end, empty_file_folder


def _correct_authors(init_au_txt):
    init_au_txt = bp.remove_special_symbol(init_au_txt,
                                           only_ascii=True, strip=True)
    init_au_list = init_au_txt.split("; ")
    corr_au_list = []
    for init_au in init_au_list:
        new_au = init_au
        au_parts_list = init_au.split(", ")
        new_au_parts_list = []
        for au_part in au_parts_list:
            if not "." in au_part:
                new_au_parts_list.append(au_part)
            else:
                end_au_part = au_part
        new_au_parts_list.append(end_au_part)
        if len(new_au_parts_list)<=2: 
            new_au = " ".join(new_au_parts_list)
        else:
            new_au = f'{new_au_parts_list[0]} {new_au_parts_list[-1]}'
        corr_au_list.append(new_au)
    new_au_txt = "; ".join(corr_au_list)
    return new_au_txt


def set_rawdata(wf_path, datatype, years_list, database):
    """Sets the rawdata to be used for the data type 'datatype' analysis.

    It copies the files ending with 'database_file_end' from database folder 
    targeted by the path 'database_folder_path' to the rawdata folder 
    targeted by the path 'rawdata_path'. 
    To do that it uses the `_set_database_extract_info` internal function. 
    When the database is Scopus and the data type to be analysed is restricted to WoS, 
    empty files ending with 'database_file_end' are used as Scopus rawdata.

    Args:
        wf_path (path): The path to the working folder.
        datatype (str): The data type of data combination type \
        from databases.
        years_list (list): List of corpus years (4 digits str).
        database (str): The database selected for the analysis.
    Returns:
        (str): End message recalling the database and data type used.
    """
    # Getting database extractions info
    return_tup = _set_database_extract_info(wf_path, datatype, database)
    database_folder_path, database_file_end, empty_file_folder = return_tup

    # Setting specific parameters for Scopus-HAL data
    last_year_database_file_end = database_file_end
    if datatype==bm_pg.DATATYPE_LIST[1] and database==bp.SCOPUS:
        last_year_datatype = bm_pg.DATATYPE_LIST[0]
        return_tup = _set_database_extract_info(wf_path, last_year_datatype,
                                                database)
        _, last_year_database_file_end, _ = return_tup

    # Cycling on year
    for year in years_list:
        if database==bp.SCOPUS and datatype==bm_pg.DATATYPE_LIST[2]:
            year_database_folder_path = database_folder_path / Path(empty_file_folder)
            year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                              database_file_end)
        else:
            year_database_folder_path = database_folder_path / Path(year)
            year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                              database_file_end)
            if not year_database_file_path:
                year_database_file_path = _get_database_file_path(year_database_folder_path,
                                                                  last_year_database_file_end)
        
        rawdata_path_dict, _, _ = set_user_config(wf_path, year, bm_pg.BDD_LIST)
        rawdata_path = rawdata_path_dict[database]
        if os.path.exists(rawdata_path):
            shutil.rmtree(rawdata_path)
        os.makedirs(rawdata_path)
        shutil.copy2(year_database_file_path, rawdata_path)

    message = f"\n{database} rawdata set for {datatype} data type."
    return message


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
    """Creates a corpus folder with the required architecture.

    It uses the global "ARCHI_YEAR" for the names of the sub_folders 
    and the `create_folder` function of the same module.

    Args:
        wf_path (path): The full path of the working folder.
        corpus_year_folder (str): The name of the folder of the corpus.
        verbose (bool): Optional status of prints (default = False).
    Returns:
        (str): End message recalling the corpus-year architecture created.
    """
    if not create_archi_param:
        # Creating folder for corpus-year working-folder
        corpus_year_folder_path = create_folder(wf_path, corpus_year_folder, verbose=verbose)
        message = f"{corpus_year_folder} folder created"
    else:
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
        corpus_year_folder_path = create_folder(wf_path, corpus_year_folder, verbose=verbose)
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
    return message


def read_parsing_dict(parsing_path, item_filename_dict, save_extent):
    """Reads the dataframes of the parsing results from files of a specified type.

    Args:
        parsing_path (path): Full path to the folder where the parsing \
        results are located.
        item_filename_dict (dict): Dict keyed by the parsing items and valued \
        by the file names of the parsing results.
        save_extent (str): File type given by file extension without the dot separator \
        (ex: "xlsx" for Excel file type).
    Returns:
        (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from \
        the package imported as bp and valued by the dataframes \
        of parsing results.
    """
    parsing_dict = {}
    # Cycling on parsing items
    for item in bp.PARSING_ITEMS_LIST:
        item_df = None
        if save_extent == "xlsx":
            item_xlsx_file = item_filename_dict[item] + ".xlsx"
            item_xlsx_path = parsing_path / Path(item_xlsx_file)
            if item_xlsx_path.is_file():
                try:
                    item_df = pd.read_excel(item_xlsx_path)
                except pd.errors.EmptyDataError:
                    item_df = pd.DataFrame()
        elif save_extent=="dat":
            item_tsv_file = item_filename_dict[item] + ".dat"
            item_tsv_path = parsing_path / Path(item_tsv_file)
            if item_tsv_path.is_file():
                try:
                    item_df = pd.read_csv(item_tsv_path, sep = "\t")
                except pd.errors.EmptyDataError:
                    item_df = pd.DataFrame()

        if item_df is not None:
            parsing_dict[item] = item_df
    return parsing_dict
