"""Module of functions for correcting parsing data of a given database type
using corrected addresses by the user in the case of unknown country.

ToDo: Deep update of docstrings.
"""

__all__ = ['build_and_save_unknown_country_data',
           'correct_parsing',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import pandas as pd
from bpfuncts import standardize_address as bp_standardize_address

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.correct_parsing_utils import build_pub_correct_authaddr_data
from bmfuncts.format_files import format_page
from bmfuncts.useful_functs import build_list_from_str
from bmfuncts.useful_functs import build_string_from_list
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import drop_multiple_item
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import print_temp_text


def _set_parse_cols_params():
    """Builds a dict setting selected columns names and a dict setting useful lists of columns names 
    for the process of correcting the addresses with unknown-country in parsings data.

    Returns:
        (tup): The built dicts.
    """
    parse_cols_dic = {'bp_pub_id_col'      : bm_pg.COL_NAMES['pub_id'],
                      'bp_doi_col'         : bm_pg.COL_NAMES['articles'][6],
                      'bp_address_id_col'  : bm_pg.COL_NAMES['address'][1],
                      'bp_address_col'     : bm_pg.COL_NAMES['address'][2],
                      'bp_country_col'     : bm_pg.COL_NAMES['country'][2],
                      'bp_author_id_col'   : bm_pg.COL_NAMES['auth_inst'][1],
                      'bp_norm_affils_col' : bm_pg.COL_NAMES['auth_inst'][4],
                      'bp_raw_affils_col'  : bm_pg.COL_NAMES['auth_inst'][5],
                      'bp_author_col'      : bm_pg.COL_NAMES['authors'][2],
                      'author_ids_col'     : 'Author IDs',
                      'authors_col'        : 'Author names',
                      'correct_address_col': "Correct address",
                     }

    select_pub_data_keys = ['bp_pub_id_col', 'bp_author_id_col', 'bp_author_col']
    set_authors_keys = ['bp_author_id_col', 'bp_address_col']
    parse_cols_lists_dic = {'select_pub_data': [parse_cols_dic[key] for key in select_pub_data_keys],
                            'set_author': [parse_cols_dic[key] for key in set_authors_keys],
                           }
    return parse_cols_dic, parse_cols_lists_dic


def _built_db_pub_identifiers_data(parsing_dict, db_ids_path, identifiers_cols):
    """Builds data of publications identifiers specific to a given corpus database.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_KEYS_DIC' global.
        db_ids_path (path): The full path to database-IDs file.
        identifiers_cols (list): The column names of the publications identifiers.
    Returns:
        (list): The list composed of the data (dict) of database ID per publication ID \
        and the data (dict) of the DOI per publication ID.
    """
    # Setting column names from args
    database_id_col, pub_id_col, doi_col = identifiers_cols

    # Getting ID of each publication with associated main metadata
    parsing_pub_key = bm_pg.PARSING_KEYS_DIC['parsing_pub']
    parsing_pub_df = parsing_dict[parsing_pub_key]

    # Building the data of DOI per publication-ID
    dois_dict = dict(zip(parsing_pub_df[pub_id_col], parsing_pub_df[doi_col]))

    # Building the data of database-ID per publication-ID
    db_ids_df = pd.read_excel(db_ids_path)
    db_ids_dict = dict(zip(db_ids_df[pub_id_col], db_ids_df[database_id_col]))

    ids_dicts_list = [db_ids_dict, dois_dict]
    return ids_dicts_list


def _set_correct_parsing_paths(parsing_path, database, correct_parsing_filenames,
                               test_txt=""):
    """Builds a list of useful paths and file-names for the process of correcting the addresses 
    with unknown-country in parsings data using the corrected addresses by the user.

    Args:
        parsing_path (path): Full path to the folder of the parsing results.
        database (str): Database name (ex: 'wos' or 'scopus').
        correct_parsing_filenames (list): if not empty the useful \
        full paths to the parsing are added to built paths-list.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default: "").
    Returns:
        (tuple): (The list of the built paths, the list of the built file-names).
    """
    # Internal functions
    def _set_db_file_name(name_base):
        db_file_name = f"{database.capitalize()}{name_base}"
        return db_file_name

    def _set_parsing_item_path(_item_filename):
        parsing_item_file = test_txt + _item_filename + parsing_extent
        parsing_item_path = parsing_path / Path(parsing_item_file)
        return parsing_item_path

    # Setting parameters from globals
    parsing_extent = f".{bm_pg.TSV_SAVE_EXTENT}"

    # Setting full path to file of data of addresses with unknown-country to be corrected
    addresses_to_correct_file = _set_db_file_name(bm_pg.ARCHI_YEAR["addresses_to_correct_file_base"])
    addresses_to_correct_path = parsing_path / Path(addresses_to_correct_file)

    # Setting full path to file of data of corrected addresses with unknown-country
    corrected_addresses_file = _set_db_file_name(bm_pg.ARCHI_YEAR["corrected_addresses_file_base"])
    corrected_addresses_path = parsing_path / Path(corrected_addresses_file)

    # Setting full path to database-IDs file
    db_ids_file = _set_db_file_name(bm_pg.IDS_FILE_BASE)
    db_ids_path = parsing_path / Path(db_ids_file)

    # Building returned lists
    files_list = [addresses_to_correct_file, corrected_addresses_file]
    paths_list = [addresses_to_correct_path, corrected_addresses_path, db_ids_path]
    compl_paths_list = []
    if correct_parsing_filenames:
        # Setting list of full paths to the parsing data to be corrected
        compl_paths_list = [_set_parsing_item_path(item_filename)
                            for item_filename in correct_parsing_filenames]
    paths_list = paths_list + compl_paths_list
    return paths_list, files_list


def _remove_unknown_country(input_addr_str, sep_str, unknown_country):
    """Removes unknown-country key from an address.

    The unknown-country key is potentially added when 
    the address is standardized.
    The split of the address and the join of the items uses 
    the specified separator.

    Args:
        input_addr_str (str): The list of string items to be joined.
        sep_str (str): The separator to be used for the split and join \
        including space if required.
        unknown_country (str): Key word for unknown country.
    Returns:
        (str): The built final address.
    """
    output_addr_list = build_list_from_str(input_addr_str, sep_str)
    output_addr_list = drop_multiple_item(output_addr_list, unknown_country)
    output_addr_str = build_string_from_list(output_addr_list, sep_str)
    return output_addr_str


def _set_addr_first_auth_id(addr_auth_ids):
    # Ensuring type of 'addr_auth_ids' as string
    auth_ids_str = str(addr_auth_ids)

    if ";" in auth_ids_str:
        # Keeping only the first item as integer
        # assuming author's IDs are sorted
        auth_ids_list = auth_ids_str.split('; ')
        addr_first_auth_id = int(auth_ids_list[0])
    else:
        # Setting type of 'addr_first_auth_id' as integer
        # assuming only one author ID
        addr_first_auth_id = int(auth_ids_str)
    return addr_first_auth_id


def _save_addresses_to_correct_data(addresses_to_correct_df, addresses_to_correct_path,
                                    database, corpus_year, sorting_cols, file_clear=False):
    """Saves the data of addresses with unknown-country for the process of correcting the parsing data.

    Args:
        addresses_to_correct_df (dataframe): The data of addresses with unknown-country.
        addresses_to_correct_path (path): Full file path for saving the data.
        database (str): Database name (ex: 'wos' or 'scopus').
        corpus_year (str): Corpus year defined by 4 digits.
        sorting_cols (list): Columns names for sorting the data to save.
        file_clear (bool): Optional parameter for saving empty data (default: False).
    """
    if file_clear:
        # Building empty data to save with col names and 10 empty rows
        empty_df_cols = addresses_to_correct_df.columns
        cols_nb = len(empty_df_cols)
        data_row = [""] * cols_nb
        data = sum([], [data_row]*10)
        save_addresses_to_correct_df = pd.DataFrame(data, columns=empty_df_cols)
    else:
        # Setting actual sorting columns to use authors' IDs as int
        author_ids_col = sorting_cols[1]
        temp_col = 'sorting_auth_id'
        sorting_cols[1] = temp_col

        # Building temporary column of integer author's IDs
        save_addresses_to_correct_df = addresses_to_correct_df.assign(temp=addresses_to_correct_df[author_ids_col])
        save_addresses_to_correct_df = save_addresses_to_correct_df.rename({"temp": temp_col}, axis=1)
        save_addresses_to_correct_df[temp_col] = save_addresses_to_correct_df[temp_col].apply(_set_addr_first_auth_id)

        # Saving data of corrected addresses of addresses with initial unknown-countries
        save_addresses_to_correct_df = save_addresses_to_correct_df.sort_values(by=sorting_cols, axis=0)
        save_addresses_to_correct_df = save_addresses_to_correct_df.drop(columns=temp_col)

    df_title = 'false_addr'
    wb, ws = format_page(save_addresses_to_correct_df, df_title)
    ws.title = database + " " + corpus_year
    wb.save(addresses_to_correct_path)


def _build_db_id_corrected_addr_hist(db_id, dfs_list, cols_lists, merge_cols_rename_dic):
    """Required for using updated addresses identifiers that may be not 
    the same as in the available saved history of correction by the user.
    """
    addresses_to_correct_cols, merge_on_cols, merge_cols_to_drop, update_cols = cols_lists
    address_id_col, country_col, correct_address_col = update_cols
    corrected_addresses_hist_df, init_addresses_to_correct_df = dfs_list

    corrected_db_id_df = corrected_addresses_hist_df[corrected_addresses_hist_df[db_id_col]==db_id]

    # Mapping the history of corrected addresses to the authors IDs
    # while keeping the addresses IDs of the parsing results to be corrected
    db_id_addresses_to_correct_df = init_addresses_to_correct_df[init_addresses_to_correct_df[db_id_col]==db_id]
    new_corrected_db_id_df = pd.merge(db_id_addresses_to_correct_df, corrected_db_id_df, how='inner', on=merge_on_cols)
    new_corrected_db_id_df.drop(columns=merge_cols_to_drop, inplace=True)
    new_corrected_db_id_df.rename(columns=merge_cols_rename_dic, inplace=True)
    new_corrected_db_id_df = new_corrected_db_id_df[addresses_to_correct_cols]

    correct_countries_dict = dict(zip(new_corrected_db_id_df[address_id_col], new_corrected_db_id_df[country_col]))
    correct_addresses_dict = dict(zip(new_corrected_db_id_df[address_id_col], new_corrected_db_id_df[correct_address_col]))
    return correct_countries_dict, correct_addresses_dict


def _build_db_id_data_to_correct(db_id_df, correct_countries_dict, correct_addresses_dict, db_id_use_cols):
    pub_id_col, doi_col, address_id_col, address_col, author_ids_col, authors_col = db_id_use_cols
    db_id_data = []
    for _, row in db_id_df.iterrows():
        pub_id = row[pub_id_col]
        doi = row[doi_col]
        address_id = row[address_id_col]
        country = correct_countries_dict[address_id]
        address = row[address_col]
        correct_address = correct_addresses_dict[address_id]
        author_ids = row[author_ids_col]
        author_names = row[authors_col]
        db_id_data.append([db_id, pub_id, doi, address_id, country, address, correct_address,
                           author_ids, author_names])
    return db_id_data


def _use_corrected_addresses(init_addresses_to_correct_df, corrected_addresses_path, unknown_country):
    """Uses the history of the corrected-addresses data to pre-correct the data of addresses 
    with unknown-country before completion by the user.

    The status of the corrected addresses is set to True if all the addresses are corrected \
    using the history.

    Args:
        init_addresses_to_correct_df (dataframe): Addresses with unknown-country data before \
        the pre-correction using the history of corrected addresses.
        corrected_addresses_path (path): The full path to the file of the addresses \
        correction history.
        unknown_country (str): Key word for unknown-country.
    Returns:
        (tuple): (The pre-corrected data (dataframe) of the addresses with unknown-country, \
        the status of the corrected addesses (bool))
    """
    # Setting useful columns names
    addresses_to_correct_cols = init_addresses_to_correct_df.columns
    (db_id_col, pub_id_col, doi_col, address_id_col, country_col,
     address_col, correct_address_col, author_ids_col, authors_col) = addresses_to_correct_cols

    # Setting cols' list for updating addresses identifiers in history of corrected addresses
    update_cols = [address_id_col, country_col, correct_address_col]

    # Setting cols' list for merge of history of addresses' correction into data of addresses to correct
    merge_on_cols = [db_id_col, doi_col, address_col, author_ids_col, authors_col]

    # Setting cols' list to drop after merge
    unknown_cols_to_drop = [country_col + "_x", correct_address_col + "_x"]
    hist_cols_to_drop = [pub_id_col + "_y", address_id_col + "_y"]
    merge_cols_to_drop = unknown_cols_to_drop + hist_cols_to_drop

    # Setting dict for rename of kept cols after merge by removing added suffixes by merge
    merge_cols_rename_dic = {pub_id_col + "_x"         : pub_id_col,
                             address_id_col + "_x"     : address_id_col,
                             country_col + "_y"        : country_col,
                             correct_address_col + "_y": correct_address_col,
                             }

    # Setting useful shared parameters within loops
    cols_lists = [addresses_to_correct_cols, merge_on_cols, merge_cols_to_drop, update_cols]
    corrected_addresses_hist_df, init_addresses_to_correct_df = dfs_list

    # Getting the data of addresses' correction history
    corrected_addresses_hist_df = pd.read_excel(corrected_addresses_path, converters={author_ids_col:str})

    # Setting the list of database IDs of publications for which addresses have to be corrected
    corrected_db_ids = corrected_addresses_hist_df[db_id_col].to_list()

    new_addresses_to_correct_df = pd.DataFrame()
    for db_id, db_id_df in init_addresses_to_correct_df.groupby(db_id_col):
        new_db_id_df = db_id_df.copy()
        if db_id in corrected_db_ids:
            return_tup = _build_db_id_corrected_addr_hist(db_id, dfs_list, cols_lists, merge_cols_rename_dic)
            correct_countries_dict, correct_addresses_dict = return_tup

            db_id_data = _build_db_id_data_to_correct(db_id, db_id_df, correct_countries_dict,
                                                      correct_addresses_dict, db_id_use_cols)
            new_db_id_df = pd.DataFrame(db_id_data, columns=addresses_to_correct_cols)

        new_addresses_to_correct_df = concat_dfs([new_addresses_to_correct_df, new_db_id_df])
        new_addresses_to_correct_df.sort_values(by=[pub_id_col, address_id_col, address_col], inplace=True)
    all_addresses_corrected = False
    if unknown_country not in new_addresses_to_correct_df[country_col].to_list():
        all_addresses_corrected = True
    return new_addresses_to_correct_df, all_countries_corrected


def _select_country_pub_data(pub_id, data_dfs, select_pub_data_cols):
    """Selects the data specific to a publication from parsing data.

    Args:
        pub_id (str): The index of publication which data are selected.
        data_dfs (list): The list composed of the parsing full data \
        of addresses, of authors with affiliations and of authors names.
        select_pub_data_cols (list): The list is composed of column names \
        of the publications indices, the authors indices and the authors names.
    Returns:
        (tup): (Selected data (dataframe) from authors with affiliations parsing results, \
        Selected data (dataframe) from addresses parsing results, The data (dict) \
        keyed by author index and valued by author name selected from authors parsing results).
    """
    # Setting parameters value from args
    addresses_df, authaddr_df, authors_df = data_dfs
    pub_id_col, author_id_col, author_name_col = select_pub_data_cols

    pub_addresses_df = addresses_df[addresses_df[pub_id_col]==pub_id]
    pub_authaddr_df = authaddr_df[authaddr_df[pub_id_col]==pub_id]
    pub_authors_df = authors_df[authors_df[pub_id_col]==pub_id]

    pub_authors_dict = dict(zip(pub_authors_df[author_id_col].to_list(),
                                pub_authors_df[author_name_col].to_list()))
    return pub_addresses_df, pub_authaddr_df, pub_authors_dict


def _build_author_addresses_list(author_addresses_str, unknown_country):
    """Builds the list of standardized addresses of an author after remove 
    of the keyword of unknown-country in all the addresses.

    Args:
        author_addresses_str (str): Composed of the addresses of the author \
        separated by semicolon.
        unknown_country (str): The keyword for unknown country.
    Returns:
        (list): The list of standardized addresses of the author.
    """
    # Building the author's addresses list (standardized without add of unknown country)
    author_addresses_list = build_list_from_str(author_addresses_str, "; ")
    author_addresses_list = [bp_standardize_address(x, add_unknown_country=False)
                             for x in author_addresses_list]
    author_addresses_list = [_remove_unknown_country(x, ", ", unknown_country)
                             for x in author_addresses_list]
    return author_addresses_list


def _build_auth_ids_names_lists(std_false_address, pub_authaddr_df, pub_authors_dict,
                                set_authors_cols, unknown_country):
    """Builds the data specific to a publication from parsing data.

    Args:
        std_false_address (str): Standardized address with unknown country \
        to be searched in the author's addresses list.
        pub_authaddr_df (dataframe): Publication data selected from authors \
        with affiliations parsing results.
        pub_authors_dict (dict): Publication data keyed by author index \
        and valued by author name as selected from authors parsing results.
        set_authors_cols (list):
        unknown_country (str): The keyword for unknown country.
    Returns:
        (list): The list of standardized addresses of the author.
    """
    author_id_col, address_col = set_authors_cols
    # Building the IDs list and names list of authors
    # that have the false address in their affiliations list
    false_address_auth_ids_list = []
    false_address_auth_names_list = []
    for _, row in pub_authaddr_df.iterrows():
        author_id = row[author_id_col]
        author_name = pub_authors_dict[author_id]

        # Building the author's addresses list (standardized without add of unknown country)
        author_addresses_list = _build_author_addresses_list(row[address_col], unknown_country)

        # Searching for false address in the author's addresses list to append author's ID
        if std_false_address in author_addresses_list:
            false_address_auth_ids_list.append(str(author_id))
            false_address_auth_names_list.append(str(author_name))

    # Building a string from the built IDs list of authors
    false_address_auth_ids = build_string_from_list(false_address_auth_ids_list, "; ")
    false_address_auth_names = build_string_from_list(false_address_auth_names_list, "; ")
    return false_address_auth_ids, false_address_auth_names


def _build_pub_id_data_to_correct(pub_id, data_to_correct, dfs_list, parse_cols_lists_dic,
                                  address_id_col, unknown_country):
    # Setting data from 'dfs_list' args useful for building the data to correct
    pub_unknown_country_df, addresses_df, authaddr_df, authors_df = dfs_list

    # Setting the identifiers of the publication
    database_id, doi = db_ids_dict[pub_id], dois_dict[pub_id]

    # Selecting the data of the publication
    return_tup = _select_country_pub_data(pub_id, dfs_list[1:], parse_cols_lists_dic['select_pub_data'])
    pub_addresses_df, pub_authaddr_df, pub_authors_dict = return_tup

    # Building data for each address with unknown-country
    false_address_ids_list = pub_unknown_country_df[address_id_col].to_list()
    for false_address_id in false_address_ids_list:
        # setting the false address with standardization without add of unknown country
        address_id_df = pub_addresses_df[pub_addresses_df[address_id_col]==false_address_id]
        raw_false_address = address_id_df[address_col].to_list()[0]
        std_false_address = bp_standardize_address(raw_false_address, add_unknown_country=False)

        # Building the IDs list and names list of authors
        # that have the false address in their affiliations list
        return_tup = _build_auth_ids_names_lists(std_false_address, pub_authaddr_df, pub_authors_dict,
                                                 parse_cols_lists_dic['set_authors'], unknown_country)
        false_address_auth_ids, false_address_auth_names = return_tup

        data_to_correct.append([database_id, pub_id, doi, false_address_id, unknown_country,
                                std_false_address, "", false_address_auth_ids, false_address_auth_names])
    return data_to_correct



def _check_unknown_country_data(init_addresses_to_correct_df, corrected_addresses_path,
                                unknown_country, print_params):
    """Checks the status of the data of the addresses with unknown-country 
    and use the history of the addresses correction.

    Args:
        init_addresses_to_correct_df (dataframe): The data of addresses with unknown \
        country before use of the addresses correction history.
        corrected_addresses_path (path): The full path to the file of the addresses \
        correction history.
        unknown_country (str): The keyword for unknown country.
        print_params (list): Parameters for the `print_step_text` function \
        imported from the `bmfuncts.useful_functs` module.
    Returns:
        (tup): (The data (dataframe) of addresses with unknown after use of \
        the addresses correction history, the addresses-to-correct status (bool) \
        which is True if data are empty, The corrected-addresses status (bool) \
        which is True if all the addresses are already corrected).
    """
    addresses_to_correct_empty = init_addresses_to_correct_df.empty
    addresses_to_correct_df = init_addresses_to_correct_df.copy()
    all_addresses_corrected = False
    if addresses_to_correct_empty:
        all_addresses_corrected = True
        step_txt = f"{bm_pg.TAB}- No addresses with unknown-country found"
    elif corrected_addresses_path.is_file():
        return_tup = _use_corrected_addresses(init_addresses_to_correct_df, corrected_addresses_path,
                                              unknown_country)
        addresses_to_correct_df, all_addresses_corrected = return_tup
        step_txt = f"{bm_pg.TAB}- History of corrected addresses with unknown-country used"
        if all_addresses_corrected:
            step_txt += f"\n{bm_pg.TAB}- Correction is available for all addresses with unknown-country"
        else:
            step_txt += f"\n{bm_pg.TAB}- Addresses with unknown-country remain to be corrected"
    else:
        step_txt = (f"{bm_pg.TAB}- Addresses with unknown-country found"
                    f"\n{bm_pg.TAB}- No history of correction for these addresses is available")
    return addresses_to_correct_df, addresses_to_correct_empty, all_addresses_corrected, step_txt


def build_and_save_unknown_country_data(parsing_dict, parsing_path, unknown_country, correct_params):
    """Builds data of addresses with unknown-country and saves these data 
    as an Openpyxl workbook for correction by the user.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the data (dataframes) of parsing results.
        parsing_path (path): Full path to the folder of the parsing results.
        unknown_country (str): Key word for unknown country.
        correct_params (list): Composed of the type (str) of data ('wos' or 'scopus'), \
        of the corpus year (str) defined by 4 digits, of the parameters for \
        the `print_step_text` function imported from the `bmfuncts.useful_functs` module \
        and of the keys (list) of parsing items for building data of addresses with \
        unknown-country.
    Returns:
        (tup): (The status (bool) of search result of unknown country, the status (bool) \
        of addresses correction, the list of the file names of the parsing data corrected).
    """
    database, corpus_year, print_params = correct_params
    print_step_text("\nBuilding the data of addresses with unknown-country...", print_params)
    # Setting useful paths for the process of the correction
    empty_list = []
    return_tup = _set_correct_parsing_paths(parsing_path, database, empty_list)
    correct_paths_list, correct_files_list = return_tup
    (addresses_to_correct_path, corrected_addresses_path,
     db_ids_path) = [correct_paths_list[idx] for idx in range(3)]

    # Setting useful parsing data
    (addresses_df, authors_df, authaddr_df,
     countries_df) = [parsing_dict[key] for key in bm_pg.PARSING_KEYS_DIC['unknown_country']]

    # Setting list of useful parsing data for building data to correct
    parsing_dfs_list = [addresses_df, authaddr_df, authors_df]

    # Setting useful column names
    parse_cols_dic, parse_cols_lists_dic = _set_parse_cols_params()
    cols_keys = ['bp_pub_id_col', 'bp_doi_col', 'bp_address_id_col', 'bp_country_col', 'bp_address_col',
                 'correct_address_col', 'bp_author_id_col', 'bp_author_col', 'author_ids_col', 'authors_col']
    (pub_id_col, doi_col, address_id_col, country_col, address_col, correct_address_col, author_id_col,
     author_name_col, author_ids_col, authors_col) = [parse_cols_dic[key] for key in cols_keys]
    database_id_col = bm_pg.DB_ID_COLS[database]

    # Setting columns list of the data to correct
    unknown_countries_cols = [database_id_col, pub_id_col, doi_col, address_id_col, country_col,
                              address_col, correct_address_col, author_ids_col, authors_col]

    # Setting publications' identifiers
    identifiers_cols = [database_id_col, pub_id_col, doi_col]
    db_ids_dict, dois_dict = _built_db_pub_identifiers_data(parsing_dict, db_ids_path, identifiers_cols)

    pub_to_check_nb = len(list(set(countries_df[pub_id_col])))
    pub_num = 0
    data_to_correct = []
    for pub_id, pub_id_df in countries_df.groupby(pub_id_col):
        pub_num += 1
        txt_len = print_temp_text(f"{bm_pg.TAB}Publications number: {pub_num} / {pub_to_check_nb}", txt_end=True)
        # Setting the list of countries from the countries data of the publication
        countries = pub_id_df[country_col].to_list()

        if unknown_country in countries:
            # Selecting the data of the unknown-country in the countries data of the publication
            pub_unknown_country_df = pub_id_df[pub_id_df[country_col]==unknown_country]

            # Building 
            dfs_list = [pub_unknown_country_df] + parsing_dfs_list
            data_to_correct = _build_pub_id_data_to_correct(pub_id, data_to_correct, dfs_list, parse_cols_lists_dic,
                                                            address_id_col, unknown_country)
    init_addresses_to_correct_df = pd.DataFrame(data_to_correct, columns=unknown_countries_cols)

    # Checking addresses with unknown-country data and use correction history
    return_tup = _check_unknown_country_data(init_addresses_to_correct_df, corrected_addresses_path,
                                             unknown_country, print_params)
    addresses_to_correct_df, addresses_to_correct_empty, all_addresses_corrected, step_txt = return_tup
    print_step_text(step_txt, print_params, prev_txt_len=txt_len)

    # Saving data of addresses with unknown-country
    sorting_cols = [database_id_col, author_ids_col]
    _save_addresses_to_correct_data(addresses_to_correct_df, addresses_to_correct_path,
                                    database, corpus_year, sorting_cols)
    if not all_addresses_corrected:
        print_step_text(f"{bm_pg.TAB}- Data for correction of addresses with unknown-country saved",
                        print_params)
    return addresses_to_correct_empty, all_addresses_corrected, correct_files_list


def _update_corrected_addresses_history(user_addresses_to_correct_df, corrected_addresses_path,
                                        db_ids_path, database, corpus_year, dedup_cols):
    """Updates the history of the corrected-addresses data and saves them.

    Args:
        user_addresses_to_correct_df (dataframe): Data of addresses with \
        unknown-country completely corrected by the user after pre-correction \
        using the correction history.
        corrected_addresses_path (path): Full path to the existing history \
        of corrected addresses with unknown-country before update.
        database (str): Database name (ex: 'wos' or 'scopus').
        corpus_year (str): Corpus year defined by 4 digits.
        dedup_cols (list): Columns names for deduplicating rows in the updated data.
    Returns:
        (dataframe): The updated data of history of the corrected addresses.
    """
    addresses_correction_df = user_addresses_to_correct_df.copy()
    new_corrected_addresses_hist_df = user_addresses_to_correct_df.copy()
    # Getting the history of corrected addresses with unknown-country before update
    if corrected_addresses_path.is_file():
        # Getting database IDs list
        db_ids_df = pd.read_excel(db_ids_path)
        database_id_col = dedup_cols[0]
        db_ids_list = db_ids_df[database_id_col].to_list()

        # Getting existing history of corrected addresses
        saved_corrected_addresses_hist_df = pd.read_excel(corrected_addresses_path)
        user_ids_list = user_addresses_to_correct_df[database_id_col].to_list()
        init_data_df = (saved_corrected_addresses_hist_df[saved_corrected_addresses_hist_df[database_id_col]
                        .isin(user_ids_list)])
        final_data_df = init_data_df[init_data_df[database_id_col].isin(db_ids_list)]
        clean_corrected_addresses_hist_df = final_data_df.copy()

        # Concatenating the existing history of corrected data with the user's corrected ones
        addresses_correction_df = concat_dfs([clean_corrected_addresses_hist_df,
                                              user_addresses_to_correct_df],
                                             dedup_cols=dedup_cols, keep='last')
        new_corrected_addresses_hist_df = concat_dfs([saved_corrected_addresses_hist_df,
                                                      new_corrected_addresses_hist_df],
                                                     dedup_cols=dedup_cols, keep='last')

    # Saving data of addresses with unknown-country
    new_corrected_addresses_hist_df.sort_values(by=dedup_cols, axis=0, inplace=True)
    df_title = 'false_addr'
    wb, ws = format_page(new_corrected_addresses_hist_df, df_title)
    ws.title = database + " " + corpus_year
    wb.save(corrected_addresses_path)
    return addresses_correction_df


def _correct_item(correct_address_id, address_id_col, item_col, pub_id_item_df,
                  pub_id_correct_item_dict):
    for num_row, row in pub_id_item_df.iterrows():
        false_address_id = row[address_id_col]
        if correct_address_id==false_address_id:
            correct_item = pub_id_correct_item_dict[correct_address_id]
            pub_id_item_df.loc[num_row, item_col] = correct_item
    return pub_id_item_df


def _build_pub_id_correct_addr_and_countries_data(pub_id_dfs, cols_list):
    # Setting column names from args
    address_id_col, country_col, address_col, correct_address_col = cols_list

    # Setting input-data from args
    pub_id_addresses_to_correct_df, pub_id_addresses_df, pub_id_countries_df = pub_id_dfs

    # Setting addresses IDs, correct addresses and correct countries of addresses to correct
    pub_id_correct_address_ids_list = pub_id_addresses_to_correct_df[address_id_col].to_list()
    pub_id_correct_addresses_list = pub_id_addresses_to_correct_df[correct_address_col].to_list()
    pub_id_correct_countries_list = pub_id_addresses_to_correct_df[country_col].to_list()

    # Building data dicts of correct addresses and correct countries per IDs of addresses to correct
    pub_id_correct_addresses_dict = dict(zip(pub_id_correct_address_ids_list, pub_id_correct_addresses_list))
    pub_id_correct_countries_dict = dict(zip(pub_id_correct_address_ids_list, pub_id_correct_countries_list))

    # Cycling on IDs of addresses to correct for correction of addresses and countries
    # using the above built dicts
    for correct_address_id in pub_id_correct_address_ids_list:
        # Correcting address for correct_address_id
        pub_id_addresses_df = _correct_item(correct_address_id, address_id_col, address_col,
                                            pub_id_addresses_df, pub_id_correct_addresses_dict)
        # Correcting country for correct_address_id
        pub_id_countries_df = _correct_item(correct_address_id, address_id_col, country_col,
                                            pub_id_countries_df, pub_id_correct_countries_dict)

    # Cleaning data from duplicate addresses for pub_id
    pub_id_addresses_df = pub_id_addresses_df.drop_duplicates(address_col)
    pub_id_addresses_ids_list = pub_id_addresses_df[address_id_col]
    pub_id_countries_df = pub_id_countries_df[pub_id_countries_df[address_id_col].isin(pub_id_addresses_ids_list)]
    return pub_id_addresses_df, pub_id_countries_df


def _correct_parsing_addresses_and_countries(addresses_correct_dfs, parse_cols_dic,
                                             parsing_addresses_path, parsing_countries_path):
    """Corrects the parsing data of addresses and countries using the data of addresses 
    with unknown-country corrected by the user.

    Args:
        addresses_correct_dfs (list): Composed of the parsing data of addresses (dataframe), \
        of the parsing data of countries (dataframe) and of the user's correction of the addresses \
        with unknown-country (dataframe).
        parse_cols_dic (dict): The dict giving the columns names for the \
        process of correcting parsing data.
    Returns:
        (tup): The corrected parsing data (dataframe) of addresses and of countries.
    """
    # Setting useful col names from 'parse_cols_dic' arg
    pub_id_col = parse_cols_dic['bp_pub_id_col']
    cols_keys = ['bp_address_id_col', 'bp_country_col', 'bp_address_col', 'correct_address_col']
    cols_list = [parse_cols_dic[key] for key in cols_keys]

    # Setting data for parsing correction from 'addresses_correct_dfs' arg
    addresses_df, countries_df, addresses_to_correct_df = addresses_correct_dfs
    correct_pub_ids_list = addresses_to_correct_df[pub_id_col].to_list()

    new_addresses_df = pd.DataFrame(columns=addresses_df.columns)
    new_countries_df = pd.DataFrame(columns=countries_df.columns)
    for pub_id, pub_id_df in addresses_df.groupby(pub_id_col):
        pub_id_addresses_df = pub_id_df.copy()
        pub_id_countries_df = countries_df[countries_df[pub_id_col]==pub_id]
        if pub_id in correct_pub_ids_list:
            # Selecting addresses-to-correct data for pub_id
            pub_id_addresses_to_correct_df = addresses_to_correct_df[addresses_to_correct_df[pub_id_col]==pub_id]

            # Correcting addresses and countries data for pub_id
            pub_id_dfs = [pub_id_addresses_to_correct_df, pub_id_addresses_df, pub_id_countries_df]
            return_tup = _build_pub_id_correct_addr_and_countries_data(pub_id_dfs, cols_list)
            pub_id_addresses_df, pub_id_countries_df = return_tup

        # Adding the kept or corrected data for pub_id to the data to return
        new_addresses_df = concat_dfs([new_addresses_df, pub_id_addresses_df])
        new_countries_df = concat_dfs([new_countries_df, pub_id_countries_df])
    new_addresses_df.to_csv(parsing_addresses_path, index=False, sep='\t')
    new_countries_df.to_csv(parsing_countries_path, index=False, sep='\t')


def _correct_parsing_authaddr(authaddr_correct_dfs, parse_cols_dic, parsing_authaddr_path,
                              parse_affil_params_dic, unknown_country):
    """Corrects the parsing data of authors-affiliations using the data 
    of addresses with unknown-country corrected by the user.

    In addition, the normalized and raw affiliations are defined for 
    the corrected addresses of authors using the `bp_build_addr_affils_tup` 
    function imported from the `biblioparsing` package. 
    This function requires data per country for normalizing the authors affiliations, 
    the data of affiliations types and the data of towns per country.

    Args:
        authaddr_correct_dfs (list): Composed of the parsing data (dataframe) of \
        authors-affiliations and of the user's correction data (dataframe) of \
        the addresses with unknown-country.
        parse_cols_dic (dict): The dict giving the columns names for the process \
        of correcting parsing data.
        parse_affil_params_dic (dict): 
        unknown_country (str): Key word for unknown country.
    Returns:
        (dataframe): The corrected parsing data of authors with addresses.
    """
    # Setting useful col names from 'parse_cols_dic' arg
    cols_keys = ['bp_country_col', 'bp_address_col', 'correct_address_col', 'bp_author_id_col',
                 'author_ids_col', 'bp_norm_affils_col', 'bp_raw_affils_col']
    cols_list = [parse_cols_dic[key] for key in cols_keys]
    pub_id_col = parse_cols_dic['bp_pub_id_col']

    # Setting data for parsing correction from 'authaddr_correct_dfs' arg
    authaddr_df, addresses_to_correct_df = authaddr_correct_dfs
    correct_pub_ids_list = addresses_to_correct_df[pub_id_col].to_list()

    new_authaddr_df = pd.DataFrame(columns=authaddr_df.columns)
    for pub_id, pub_id_df in authaddr_df.groupby(pub_id_col):
        pub_id_authaddr_df = pub_id_df.copy()
        if pub_id in correct_pub_ids_list:
            # Selecting addresses-to-correct data for pub_id
            pub_id_addresses_to_correct_df = addresses_to_correct_df[addresses_to_correct_df[pub_id_col]==pub_id]

            # Correcting authors-with-addresses data for pub_id
            pub_id_dfs = [pub_id_addresses_to_correct_df, pub_id_authaddr_df]
            pub_id_authaddr_df = build_pub_correct_authaddr_data(pub_id_dfs, cols_list, parse_affil_params_dic,
                                                                 unknown_country)

        # Updating authors-with-addresses data with the kept or corrected data for pub_id
        new_authaddr_df = concat_dfs([new_authaddr_df, pub_id_authaddr_df])
    new_authaddr_df.to_csv(parsing_authaddr_path, index=False, sep='\t')


def _correct_parsing_data(addresses_to_correct_df, parsing_dict, data_params_list, parse_cols_dic, correction_paths):
    # Setting params from args
    (database, corpus_year, print_params, parse_affil_params_dic) = data_params_list
    (addresses_to_correct_path, corrected_addresses_path, db_ids_path, parsing_addresses_path,
     parsing_authaddr_path, parsing_countries_path) = correction_paths

    # Setting useful column names
    database_id_col = bm_pg.DB_ID_COLS[database]
    address_id_col = parse_cols_dic['bp_address_id_col']

    # Updating history of corrected addresses by the user
    drop_dedup_cols = [database_id_col, address_id_col]
    addresses_to_correct_df = _update_corrected_addresses_history(addresses_to_correct_df, corrected_addresses_path,
                                                                  db_ids_path, database, corpus_year, drop_dedup_cols)
    print_step_text(f"{bm_pg.TAB}- History of corrected addresses with unknown-country updated", print_params)

    # Getting parsing data to be corrected
    addresses_df, authaddr_df, countries_df = [parsing_dict[key] for key in bm_pg.PARSING_KEYS_DIC['correct_parsing']]

    print_step_text(f"{bm_pg.TAB}- Correcting addresses in parsing data...", print_params)

    # Correcting the addresses and countries parsing data
    # using the user's correction of the addresses with unknown-country
    addresses_correct_dfs = [addresses_df, countries_df, addresses_to_correct_df]
    _correct_parsing_addresses_and_countries(addresses_correct_dfs, parse_cols_dic, parsing_addresses_path,
                                             parsing_countries_path)
    print_step_text(f"{bm_pg.TAB*2}- Addresses and countries parsing corrected", print_params)

    # Correcting the authors-affiliations parsing data
    # using the user's correction of addresses with unknown-country
    txt_len = print_temp_text(f"{bm_pg.TAB}- Correcting authors-with-affiliations parsing...", txt_end=True)
    authaddr_correct_dfs = [authaddr_df, addresses_to_correct_df]
    new_authaddr_df = _correct_parsing_authaddr(authaddr_correct_dfs, parse_cols_dic, parsing_authaddr_path,
                                                parse_affil_params_dic, unknown_country)
    print_step_text(f"{bm_pg.TAB*2}- Authors-with-affiliations parsing corrected", print_params)

    # Clear data of addresses with unknown-country to be corrected
    sorting_cols = [database_id_col, address_id_col]
    _save_addresses_to_correct_data(addresses_to_correct_df, addresses_to_correct_path,
                                    database, corpus_year, sorting_cols, file_clear=True)
    print_step_text(f"{bm_pg.TAB}- Data for correction of addresses with unknown-country cleaned",
                    print_params, prev_txt_len=txt_len)


def correct_parsing(db_params_list, parsing_path, parsing_dict, unknown_country, test_txt=""):
    """Corrects the parsing data of countries, addresses and authors-affiliations 
    using the data of addresses with unknown-country corrected by the user.

    This is done through the `_correct_parsing_addresses_and_countries` and 
    `_correct_parsing_authaddr` internal functions. 
    For this last function, it builds 3 dicts through the `build_norm_dicts` function 
    imported from the `bmfuncts.config_utils` module, for the normalization of affiliations.

    Args:
        db_params_list (list): The list composed of the name of the rawdata-database, \
        of the 4 digits year of the corpus (str), of the print parameters (list), \
        of the dict giving the full paths to the Institute's files to use for \
        affiliations parsing of Institute's authors at rawdata-parsing step, \
        and of the dict giving the name of the parsing file for each parsed item.
        parsing_path (path): Full path to the folder of the parsing results \
        in the corpus folder.
        parsing_dict (dict): Parsing results keyed by parsing items and valued by \
        the data (dataframes) of parsing results.
        unknown_country (str): Key word for unknown country.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default="").
    Returns:
        (bool): True if the parsing data have been corrected.
    Note:
        The 'PARSING_KEYS_DIC' global is imported from the `bmfuncts.pub_globals` package.
    """
    # Setting parameters from 'db_params_list'
    (database, corpus_year, print_params, parse_affil_params_dic, parsing_filenames_dict) = db_params_list

    print_step_text(f"\nCorrecting addresses with unknown countries for {database}...", print_params)

    # Setting useful paths to files for parsing data correction
    correct_parsing_filenames = [parsing_filenames_dict[key]
                                 for key in bm_pg.PARSING_KEYS_DIC['correct_parsing']]
    correction_paths, _ = _set_correct_parsing_paths(parsing_path, database, correct_parsing_filenames, test_txt)

    # Setting useful column names
    parse_cols_dic, _ = _set_parse_cols_params()
    country_col = parse_cols_dic['bp_country_col']

    # Getting data of the user's correction of the addresses with unknown-country
    addresses_to_correct_path = correction_paths[0]
    addresses_to_correct_df = pd.read_excel(addresses_to_correct_path)
    addresses_to_correct_df = addresses_to_correct_df[addresses_to_correct_df[country_col]!=unknown_country]
    countries_corrected_list = addresses_to_correct_df[country_col].to_list()

    correct_status = False
    if not addresses_to_correct_df.empty:
        # If data of the user's correction of the addresses with unknown-country not empty,
        # proceeding with correction of parsing data

        data_params_list = [database, corpus_year, print_params, parse_affil_params_dic]
        _correct_parsing_data(correct_parsing_dfs, corrected_addresses_df, data_params_list,
                              parse_cols_dic, correction_paths)

        correct_status = True
    return correct_status
