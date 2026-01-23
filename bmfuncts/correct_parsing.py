"""Module of functions for correcting parsing data of a given database type
using corrected addresses by the user in the case of unknown country.
"""

__all__ = ['build_and_save_unknown_country_data',
           'correct_parsing',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.config_utils import build_norm_dicts
from bmfuncts.format_files import format_page
from bmfuncts.useful_functs import build_list_from_str
from bmfuncts.useful_functs import build_string_from_list
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import drop_multiple_item


def _set_parse_cols_dic():
    """Builds a dict setting selected columns names for the process 
    of correcting the addresses with unknown-country in parsings data 
    using the corrected addresses by the user.

    Returns:
        (dict): The built dict.
    """
    parse_cols_dic = {'bp_pub_id_col'      : bp.COL_NAMES['pub_id'],
                      'bp_doi_col'         : bp.COL_NAMES['articles'][6],
                      'bp_address_id_col'  : bp.COL_NAMES['address'][1],
                      'bp_address_col'     : bp.COL_NAMES['address'][2],
                      'bp_country_col'     : bp.COL_NAMES['country'][2],
                      'bp_author_id_col'   : bp.COL_NAMES['auth_inst'][1],
                      'bp_norm_inst_col'   : bp.COL_NAMES['auth_inst'][4],
                      'bp_raw_inst_col'    : bp.COL_NAMES['auth_inst'][5],
                      'bp_author_col'      : bp.COL_NAMES['authors'][2],
                      'author_ids_col'     : 'Author IDs',
                      'authors_col'        : 'Author names',
                      'correct_address_col': "Correct address",
                     }
    return parse_cols_dic


def _set_db_id_cols_dict():
    """Builds a dict setting columns names for the database-IDs for the process 
    of correcting the addresses with unknown-country in parsings data using 
    the corrected addresses by the user.

    Returns:
        (dict): The built dict.
    """
    db_id_cols_dic = {bp.WOS   : bp.COL_NAMES['wos_id'][0],
                      bp.SCOPUS: bp.COL_NAMES['scopus_id'][0],
                     }
    return db_id_cols_dic


def _built_db_pub_identifiers_data(parsing_dict, db_ids_path, identifiers_cols):
    """Builds data of publications identifiers specific to a given corpus database.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the data (dataframes) of parsing results.
        db_ids_path (path): The full path to database-IDs file.
        identifiers_cols (list): The column names of the publications identifiers.
    Returns:
        (list): The list composed of the data (dict) of database ID per publication ID \
        and the data (dict) of the DOI per publication ID.
    """
    # Setting column names from args
    database_id_col, pub_id_col, doi_col = identifiers_cols

    # Building the data of DOI per publication-ID
    articles_df = parsing_dict['articles']
    dois_dict = dict(zip(articles_df[pub_id_col], articles_df[doi_col]))

    # Building the data of database-ID per publication-ID
    db_ids_df = pd.read_excel(db_ids_path)
    db_ids_dict = dict(zip(db_ids_df[pub_id_col], db_ids_df[database_id_col]))

    ids_dicts_list = [db_ids_dict, dois_dict]
    return ids_dicts_list


def _set_correct_parsing_paths(parsing_path, database_type, item_filename_dict,
                               items_parsing_status=False, test_txt=""):
    """Builds a list of useful paths and file-names for the process of correcting the addresses 
    with unknown-country in parsings data using the corrected addresses by the user.

    Args:
        parsing_path (path): Full path to the folder of the parsing results.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        item_filename_dict (dict): The full paths to the parsing.
        items_parsing_status (bool): Optional (default: False), if True the useful \
        full paths to the parsing are added to built paths list.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default: "").
    Returns:
        (tuple): (The list of the built paths, the list of the built file-names).
    """
    # Internal functions
    def _set_db_file_name(name_base):
        db_file_name = f"{database_type.capitalize()}{name_base}"
        return db_file_name

    def _set_parsing_item_path(_item):
        parsing_item_file = test_txt + item_filename_dict[_item] + parsing_extent
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
    if items_parsing_status:
        # Setting list of full paths to the parsing data to be corrected
        use_items_list = ['countries', 'addresses', 'authors_institutions']
        compl_paths_list = [_set_parsing_item_path(item) for item in use_items_list]
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


def _save_addresses_to_correct_data(addresses_to_correct_df, addresses_to_correct_path,
                                    database_type, corpus_year, file_clear=False):
    """Saves the data of addresses with unknown-country for the process of correcting the parsing data.

    Args:
        addresses_to_correct_df (dataframe): The data of addresses with unknown-country.
        addresses_to_correct_path (path): Full file path for saving the data.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        corpus_year (str): Corpus year defined by 4 digits.
        file_clear (bool): Optional parameter for saving empty data (default: False).
    """
    save_addresses_to_correct_df = addresses_to_correct_df.copy()
    if file_clear:
        empty_df_cols = save_addresses_to_correct_df.columns
        cols_nb = len(empty_df_cols)
        data_row = [""] * cols_nb
        data = sum([], [data_row]*10)
        save_addresses_to_correct_df = pd.DataFrame(data, columns=empty_df_cols)

    # Saving data of corrected addresses with unknown-countries
    df_title = bm_pg.DF_TITLES_LIST[19]
    wb, ws = format_page(save_addresses_to_correct_df, df_title)
    ws.title = database_type + " " + corpus_year
    wb.save(addresses_to_correct_path)


def _use_corrected_addresses(init_addresses_to_correct_df, corrected_addresses_hist_df, unknown_country):
    """Uses the history of the corrected-addresses data to pre-correct the data of addresses 
    with unknown-country before completion by the user.

    The status of the corrected addresses is set to True if all the addresses are corrected \
    using the history.

    Args:
        init_addresses_to_correct_df (dataframe): Addresses with unknown-country data before \
        the pre-correction using the history of corrected addresses.
        corrected_addresses_hist_df (dataframe): History of corrected data of addresses \
        with unknown-country.
        unknown_country (str): Key word for unknown-country.
    Returns:
        (tuple): (The pre-corrected data (dataframe) of the addresses with unknown-country, \
        the status of the corrected addesses (bool))
    """
    unknown_countries_cols = init_addresses_to_correct_df.columns
    (database_id_col, pub_id_col, doi_col, address_id_col, country_col,
     address_col, correct_address_col, author_ids_col, authors_col) = unknown_countries_cols

    corrected_db_ids = corrected_addresses_hist_df[database_id_col].to_list()

    unknown_countries_df = pd.DataFrame(columns=unknown_countries_cols)
    for db_id, db_id_df in init_addresses_to_correct_df.groupby(database_id_col):
        if db_id in corrected_db_ids:
            corrected_db_id_df = corrected_addresses_hist_df[corrected_addresses_hist_df[database_id_col]==db_id]
            correct_countries_dict = dict(zip(corrected_db_id_df[address_id_col],
                                              corrected_db_id_df[country_col]))
            correct_addresses_dict = dict(zip(corrected_db_id_df[address_id_col],
                                              corrected_db_id_df[correct_address_col]))
            data = []
            for _, row in db_id_df.iterrows():
                pub_id = row[pub_id_col]
                doi = row[doi_col]
                address_id = row[address_id_col]
                country = correct_countries_dict[address_id]
                address = row[address_col]
                correct_address = correct_addresses_dict[address_id]
                author_ids = row[author_ids_col]
                author_names = row[authors_col]
                data.append([db_id, pub_id, doi, address_id, country, address, correct_address,
                             author_ids, author_names])
            new_db_id_df = pd.DataFrame(data, columns=unknown_countries_cols)
        else:
            new_db_id_df = db_id_df.copy()
        unknown_countries_df = concat_dfs([unknown_countries_df, new_db_id_df])
        unknown_countries_df.sort_values(by=[pub_id_col], inplace=True)
    all_countries_corrected = False
    if unknown_country not in unknown_countries_df[country_col].to_list():
        all_countries_corrected = True
    return unknown_countries_df, all_countries_corrected


def _select_country_pub_data(pub_id, data_dfs, select_pub_data_cols):
    """Selects the data specific to a publication from parsing data.

    Args:
        pub_id (str): The index of publication which data are selected.
        data_dfs (list): The list composed of the parsing full data \
        of authors with affiliations, addresses and authors names.
        select_pub_data_cols (list): The list is composed of column names \
        of the publications indices, the authors indices and the authors names.
    Returns:
        (tup): (Selected data (dataframe) from authors with affiliations parsing results, \
        Selected data (dataframe) from addresses parsing results, The data (dict) \
        keyed by author index and valued by author name selected from authors parsing results).
    """
    # Setting parameters value from args
    auth_inst_df, addresses_df, authors_df = data_dfs
    pub_id_col, author_id_col, author_name_col = select_pub_data_cols

    pub_auth_inst_df = auth_inst_df[auth_inst_df[pub_id_col]==pub_id]
    pub_addresses_df = addresses_df[addresses_df[pub_id_col]==pub_id]
    pub_authors_df = authors_df[authors_df[pub_id_col]==pub_id]
    pub_authors_dict = dict(zip(pub_authors_df[author_id_col].to_list(),
                                pub_authors_df[author_name_col].to_list()))
    return pub_auth_inst_df, pub_addresses_df, pub_authors_dict


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
    author_addresses_list = [bp.standardize_address(x, add_unknown_country=False)
                             for x in author_addresses_list]
    author_addresses_list = [_remove_unknown_country(x, ", ", unknown_country)
                             for x in author_addresses_list]
    return author_addresses_list


def _build_auth_ids_names_lists(std_false_address, pub_auth_inst_df, pub_authors_dict,
                                set_authors_cols, unknown_country):
    """Builds the data specific to a publication from parsing data.

    Args:
        std_false_address (str): Standardized address with unknown country \
        to be searched in the author's addresses list.
        pub_auth_inst_df (dataframe): Publication data selected from authors \
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
    for _, row in pub_auth_inst_df.iterrows():
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


def _check_unknown_country_data(init_addresses_to_correct_df, corrected_addresses_path,
                                unknown_country):
    """Checks the status of the data of the addresses with unknown-country 
    and use the history of the addresses correction.

    Args:
        init_addresses_to_correct_df (dataframe): The data of addresses with unknown \
        country before use of the addresses correction history.
        corrected_addresses_path (path): The full path to the file of the addresses \
        correction history.
        unknown_country (str): The keyword for unknown country.
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
        message = "  - No addresses with unknown-country found"
    elif corrected_addresses_path.is_file():
        corrected_addresses_hist_df = pd.read_excel(corrected_addresses_path)
        return_tup = _use_corrected_addresses(init_addresses_to_correct_df, corrected_addresses_hist_df,
                                              unknown_country)
        addresses_to_correct_df, all_addresses_corrected = return_tup
        message = "  - History of corrected addresses with unknown-country used"
        if all_addresses_corrected:
            message = "    and correction is available for all addresses with unknown-country"
        else:
            message = "    and addresses with unknown-country remain to be corrected"
    else:
        message = ("  - Addresses with unknown-country need to be corrected"
                   "\n    and no history of correction for addresses "
                   "    with unknown-country is available")
    print(message)
    return addresses_to_correct_df, addresses_to_correct_empty, all_addresses_corrected


def build_and_save_unknown_country_data(parsing_dict, parsing_path, unknown_country,
                                        database_type, corpus_year):
    """Builds data of addresses with unknown-country and saves these data 
    as an Openpyxl workbook for correction by the user.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the data (dataframes) of parsing results.
        parsing_path (path): Full path to the folder of the parsing results.
        unknown_country (str): Key word for unknown country.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        corpus_year (str): Corpus year defined by 4 digits.
    Returns:
        (tup): True if no unknown country is found.
    """
    # Setting useful paths for the process of the correction
    empty_dict = {}
    return_tup = _set_correct_parsing_paths(parsing_path, database_type, empty_dict)
    correct_paths_list, correct_files_list = return_tup
    (addresses_to_correct_path, corrected_addresses_path,
     db_ids_path) = [correct_paths_list[idx] for idx in range(3)]

    # Setting useful parsing data
    addresses_df = parsing_dict['addresses']
    auth_inst_df = parsing_dict['authors_institutions']
    authors_df = parsing_dict['authors']
    countries_df = parsing_dict['countries']

    # Setting useful list of data
    data_dfs = [auth_inst_df, addresses_df, authors_df]

    # Setting useful column names
    parse_cols_dic = _set_parse_cols_dic()
    cols_keys = ['bp_pub_id_col', 'bp_doi_col', 'bp_address_id_col', 'bp_country_col',
                 'bp_address_col', 'correct_address_col', 'bp_author_id_col', 'bp_author_col',
                 'author_ids_col', 'authors_col']
    (pub_id_col, doi_col, address_id_col, country_col, address_col, correct_address_col, author_id_col,
     author_name_col, author_ids_col, authors_col) = [parse_cols_dic[key] for key in cols_keys]
    db_id_cols_dic = _set_db_id_cols_dict()
    database_id_col = db_id_cols_dic[database_type]

    # Setting useful columns list
    select_pub_data_cols = [pub_id_col, author_id_col, author_name_col]
    set_authors_cols = [author_id_col, address_col]

    # Setting publications identifiers
    identifiers_cols = [database_id_col, pub_id_col, doi_col]
    db_ids_dict, dois_dict = _built_db_pub_identifiers_data(parsing_dict, db_ids_path, identifiers_cols)

    unknown_countries_cols = [database_id_col, pub_id_col, doi_col, address_id_col, country_col,
                              address_col, correct_address_col, author_ids_col, authors_col]
    data = []
    for pub_id, pub_id_df in countries_df.groupby(pub_id_col):
        # Setting the list of countries from the countries data of the publication
        countries = pub_id_df[country_col].to_list()

        if unknown_country in countries:
            # Setting the publication identifiers
            database_id, doi = db_ids_dict[pub_id], dois_dict[pub_id]

            # Selecting the data of the publication
            return_tup = _select_country_pub_data(pub_id, data_dfs, select_pub_data_cols)
            pub_auth_inst_df, pub_addresses_df, pub_authors_dict = return_tup

            # Selecting the data of the unknown-country in the countries data of the publication
            pub_unknown_country_df = pub_id_df[pub_id_df[country_col]==unknown_country]

            # Building data for each address with unknown-country
            false_address_ids_list = pub_unknown_country_df[address_id_col].to_list()
            for false_address_id in false_address_ids_list:
                # setting the false address with standardization without add of unknown country
                address_id_df = pub_addresses_df[pub_addresses_df[address_id_col]==false_address_id]
                raw_false_address = address_id_df[address_col].to_list()[0]
                std_false_address = bp.standardize_address(raw_false_address, add_unknown_country=False)

                # Building the IDs list and names list of authors
                # that have the false address in their affiliations list
                return_tup = _build_auth_ids_names_lists(std_false_address, pub_auth_inst_df, pub_authors_dict,
                                                         set_authors_cols, unknown_country)
                false_address_auth_ids, false_address_auth_names = return_tup

                data.append([database_id, pub_id, doi, false_address_id, unknown_country,
                             std_false_address, "", false_address_auth_ids, false_address_auth_names])
    init_addresses_to_correct_df = pd.DataFrame(data, columns=unknown_countries_cols)

    # Checking addresses with unknown-country data and use correction history
    return_tup = _check_unknown_country_data(init_addresses_to_correct_df,
                                             corrected_addresses_path, unknown_country)
    addresses_to_correct_df, addresses_to_correct_empty, all_addresses_corrected = return_tup

    # Saving data of addresses with unknown-country
    _save_addresses_to_correct_data(addresses_to_correct_df, addresses_to_correct_path,
                                    database_type, corpus_year)
    if not all_addresses_corrected:
        message = "  - Data for correction of addresses with unknown-country saved"
        print(message)
    return addresses_to_correct_empty, all_addresses_corrected, correct_files_list


def _update_corrected_addresses_history(user_addresses_to_correct_df, corrected_addresses_path,
                                        database_type, corpus_year, dedup_cols):
    """Updates the history of the corrected-addresses data and saves them.

    Args:
        user_addresses_to_correct_df (dataframe): Data of addresses with \
        unknown-country completely corrected by the user after pre-correction \
        using the correction history.
        corrected_addresses_path (path): Full path to the existing history \
        of corrected addresses with unknown-country before update.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        corpus_year (str): Corpus year defined by 4 digits.
        dedup_cols (list): Columns names for deduplicating rows in the updated data.
    Returns:
        (dataframe): The updated data of history of the corrected addresses.
    """
    new_corrected_addresses_hist_df = user_addresses_to_correct_df.copy()
    # Getting the history of corrected addresses with unknown-country before update
    if corrected_addresses_path.is_file():
        init_corrected_addresses_hist_df = pd.read_excel(corrected_addresses_path)

        # Concatenating the existing history of corrected data with the user's corrected ones
        new_corrected_addresses_hist_df = concat_dfs([init_corrected_addresses_hist_df,
                                                      user_addresses_to_correct_df],
                                                     dedup_cols=dedup_cols, keep='last', )

    # Saving data of addresses with unknown-country
    df_title = bm_pg.DF_TITLES_LIST[19]
    wb, ws = format_page(new_corrected_addresses_hist_df, df_title)
    ws.title = database_type + " " + corpus_year
    wb.save(corrected_addresses_path)
    return new_corrected_addresses_hist_df


def _correct_parsing_countries(countries_correct_dfs, parse_cols_dic):
    """Corrects the parsing data of countries using the data of addresses with unknown-country 
    corrected by the user.

    Args:
        countries_correct_dfs (list): Composed of the parsing data of countries (dataframe) \
        and of the user's correction of the addresses with unknown-country (dataframe).
        parse_cols_dic (dict): The dict giving the columns names for the \
        process of correcting parsing data.
    Returns:
        (str): Final message.
    """
    # Setting useful col names from 'parse_cols_dic' arg
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_country_col']
    pub_id_col, address_id_col, country_col = [parse_cols_dic[key] for key in cols_keys]

    # Setting data to correct from 'countries_correct_dfs' arg
    countries_df, addresses_to_correct_df = countries_correct_dfs
    correct_pub_ids_list = addresses_to_correct_df[pub_id_col].to_list()

    new_countries_df = pd.DataFrame(columns=countries_df.columns)
    for pub_id, pub_id_df in countries_df.groupby(pub_id_col):
        pub_id_countries_df = pub_id_df.copy()
        if pub_id in correct_pub_ids_list:
            pub_id_addresses_to_correct_df = addresses_to_correct_df[addresses_to_correct_df[pub_id_col]==pub_id]
            pub_id_correct_address_ids_list = pub_id_addresses_to_correct_df[address_id_col].to_list()
            pub_id_correct_countries_list = pub_id_addresses_to_correct_df[country_col].to_list()
            pub_id_correct_countries_dict = dict(zip(pub_id_correct_address_ids_list,
                                                     pub_id_correct_countries_list))
            for correct_address_id in pub_id_correct_address_ids_list:
                for num_row, row in pub_id_countries_df.iterrows():
                    false_address_id = row[address_id_col]
                    if correct_address_id==false_address_id:
                        correct_country = pub_id_correct_countries_dict[correct_address_id]
                        pub_id_countries_df.loc[num_row, country_col] = correct_country
        new_countries_df = concat_dfs([new_countries_df, pub_id_countries_df])
    message = "  - Countries parsing corrected"
    print(message)
    return new_countries_df


def _correct_parsing_addresses(addresses_correct_dfs, parse_cols_dic):
    """Corrects the parsing data of countries using the data of addresses with unknown-country 
    corrected by the user.

    Args:
        addresses_correct_dfs (list): Composed of the parsing data of addresses (dataframe) \
        and of the user's correction of the addresses with unknown-country (dataframe).
        parse_cols_dic (dict): The dict giving the columns names for the \
        process of correcting parsing data.
    Returns:
        (str): Final message.
    """
    # Setting useful col names from 'parse_cols_dic' arg
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_address_col', 'correct_address_col']
    (pub_id_col, address_id_col, address_col, correct_address_col ) = [parse_cols_dic[key] for key in cols_keys]

    # Setting data for parsing correction from 'addresses_correct_dfs' arg
    addresses_df, addresses_to_correct_df = addresses_correct_dfs
    correct_pub_ids_list = addresses_to_correct_df[pub_id_col].to_list()

    new_addresses_df = pd.DataFrame(columns=addresses_df.columns)
    for pub_id, pub_id_df in addresses_df.groupby(pub_id_col):
        pub_id_addresses_df = pub_id_df.copy()
        if pub_id in correct_pub_ids_list:
            pub_id_addresses_to_correct_df = addresses_to_correct_df[addresses_to_correct_df[pub_id_col]==pub_id]
            pub_id_correct_address_ids_list = pub_id_addresses_to_correct_df[address_id_col].to_list()
            pub_id_correct_addresses_list = pub_id_addresses_to_correct_df[correct_address_col].to_list()
            pub_id_correct_addresses_dict = dict(zip(pub_id_correct_address_ids_list,
                                                     pub_id_correct_addresses_list))
            for correct_address_id in pub_id_correct_address_ids_list:
                for num_row, row in pub_id_addresses_df.iterrows():
                    false_address_id = row[address_id_col]
                    if correct_address_id==false_address_id:
                        correct_address = pub_id_correct_addresses_dict[correct_address_id]
                        pub_id_addresses_df.loc[num_row, address_col] = correct_address
        new_addresses_df = concat_dfs([new_addresses_df, pub_id_addresses_df])
    message = "  - Addresses parsing corrected"
    print(message)
    return new_addresses_df


def _correct_parsing_authsinst(authsinst_correct_dfs, parse_cols_dic,
                               norm_dicts, unknown_country):
    """Corrects the parsing data of authors-institutions using the data 
    of addresses with unknown-country corrected by the user.

    In addition, the normalized and raw affiliations are defined for 
    the corrected addresses of authors using the `address_inst_full_list` 
    function imported from the `BiblioParsing` package itself imported as bp. 
    This function requires data per country for normalizing the authors affiliations, 
    the data of affiliations types and the data of towns per country.

    Args:
        authsinst_correct_dfs (list): Composed of the parsing data (dataframe) of \
        authors-institutions and of the user's correction data (dataframe) of \
        the addresses with unknown-country.
        parse_cols_dic (dict): The dict giving the columns names for the process \
        of correcting parsing data.
        norm_dicts (list): Composed of the data (dict) per country for normalizing the authors' \
        affiliations, the data (dict) of affiliations types and the data (dict) of towns \
        per country.
        unknown_country (str): Key word for unknown country.
    Returns:
        (str): Final message.
    """
    # Setting useful col names from 'parse_cols_dic' arg
    cols_keys = ['bp_pub_id_col', 'bp_country_col', 'bp_address_col', 'correct_address_col', 'bp_author_id_col',
                 'author_ids_col', 'bp_norm_inst_col', 'bp_raw_inst_col']   
    (pub_id_col, country_col, address_col, correct_address_col, author_id_col, author_ids_col,
     norm_inst_col, raw_inst_col) = [parse_cols_dic[key] for key in cols_keys]

    # Setting data for affiliations normalization from 'norm_dicts' arg
    norm_raw_aff_dict, aff_type_dict, towns_dict = norm_dicts

    # Setting data for parsing correction from 'authsinst_correct_dfs' arg
    auth_inst_df, addresses_to_correct_df = authsinst_correct_dfs
    correct_pub_ids_list = addresses_to_correct_df[pub_id_col].to_list()

    new_auth_inst_df = pd.DataFrame(columns=auth_inst_df.columns)
    for pub_id, pub_id_df in auth_inst_df.groupby(pub_id_col):
        pub_id_auths_inst_df = pub_id_df.copy()
        if pub_id in correct_pub_ids_list:
            pub_id_addresses_to_correct_df = addresses_to_correct_df[addresses_to_correct_df[pub_id_col]==pub_id]
            for _, addresses_to_correct_row in pub_id_addresses_to_correct_df.iterrows():
                correct_country = addresses_to_correct_row[country_col]
                false_address = addresses_to_correct_row[address_col]
                correct_address = addresses_to_correct_row[correct_address_col]
                auth_ids_str = str(addresses_to_correct_row[author_ids_col])
                auth_ids_list = build_list_from_str(auth_ids_str, "; ")
                auth_ids_list = [int(x) for x in auth_ids_list]

                for row_num, auths_inst_row in pub_id_auths_inst_df.iterrows():
                    author_id = int(auths_inst_row[author_id_col])
                    if author_id in auth_ids_list:
                        raw_author_addresses_str = str(auths_inst_row[address_col])
                        raw_author_addresses_list = build_list_from_str(raw_author_addresses_str, "; ")
                        author_addresses_list = []
                        for address in raw_author_addresses_list:
                            std_address_str = bp.standardize_address(address, add_unknown_country=False)
                            address_str = _remove_unknown_country(std_address_str, ", ", unknown_country)
                            author_addresses_list.append(address_str)

                        # Finding index of false address in 'author_addresses_list'
                        false_addr_idx = author_addresses_list.index(false_address)
                        author_addresses_list[false_addr_idx] = correct_address

                        author_addresses_str = build_string_from_list(author_addresses_list, "; ")
                        pub_id_auths_inst_df.loc[row_num, address_col] = author_addresses_str
                        pub_id_auths_inst_df.loc[row_num, country_col] = correct_country

                        # Correcting normalized affiliations
                        addr_norm_inst_list = []
                        full_raw_inst_list = []
                        for auth_address in author_addresses_list:
                            author_addr_aff_tup = bp.address_inst_full_list(auth_address, norm_raw_aff_dict,
                                                                            aff_type_dict, towns_dict,
                                                                            drop_status=False)
                            auth_addr_norm_inst_list = author_addr_aff_tup.norm_inst_list
                            addr_norm_inst_list.append(auth_addr_norm_inst_list)
                            auth_addr_raw_inst_list = author_addr_aff_tup.raw_inst_list
                            full_raw_inst_list.append(auth_addr_raw_inst_list)

                        addr_norm_inst_list = drop_multiple_item(addr_norm_inst_list, bp.EMPTY)
                        norm_inst_str = build_string_from_list(addr_norm_inst_list, ";")
                        full_raw_inst_list = drop_multiple_item(full_raw_inst_list, bp.EMPTY)
                        raw_inst_str = build_string_from_list(full_raw_inst_list, ";")

                        pub_id_auths_inst_df.loc[row_num, norm_inst_col] = norm_inst_str
                        pub_id_auths_inst_df.loc[row_num, raw_inst_col] = raw_inst_str

        new_auth_inst_df = concat_dfs([new_auth_inst_df, pub_id_auths_inst_df])
    message = "  - Authors-with-affiliations parsing corrected"
    print(message)
    return new_auth_inst_df


def correct_parsing(params_list, parsing_path, parsing_dict,
                    item_filename_dict, unknown_country, test_txt=""):
    """Corrects the parsing data of countries, addresses and authors-institutions 
    using the data of addresses with unknown-country corrected by the user.

    This is done through the `_correct_parsing_countries`, `_correct_parsing_addresses` 
    and `_correct_parsing_authsinst` internal functions. 
    For this last function, it builds 3 dicts through the `build_norm_dicts` function 
    imported from the `bmfuncts.config_utils` module, for the normalization of affiliations.

    Args:
        params_list (list)/ The list composed of the Institute name (str), \
        the full path to working folder (path), the database name (ex: 'wos' or 'scopus') \
        and the corpus year defined by 4 digits (str).
        parsing_path (path): Full path to the folder of the parsing results in the corpus folder.
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the `BiblioParsing` package \
        imported as 'bp' and valued by the data (dataframes) of parsing results.
        item_filename_dict (dict): Dict keyed by the parsing items \
        and valued by the file names used to save the parsing results.
        unknown_country (str): Key word for unknown country.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default="").
    Returns:
        (bool): True if the parsing data have been corrected.
    """
    # Setting parameters from 'params_list'
    institute, wf_path, database_type, corpus_year = params_list

    # Setting useful paths to files for parsing data correction
    items_parsing_status = True
    correct_paths_list, _ = _set_correct_parsing_paths(parsing_path, database_type, item_filename_dict,
                                                       items_parsing_status, test_txt)
    (addresses_to_correct_path, corrected_addresses_path, _, parsing_countries_path,
     parsing_addresses_path, parsing_authsinst_path) = [correct_paths_list[idx] for idx in range(6)]

    # Getting data of the user's correction of the addresses with unknown-country
    addresses_to_correct_df = pd.read_excel(addresses_to_correct_path)

    correct_status = False
    if not addresses_to_correct_df.empty:
        # If data of the user's correction of the addresses with unknown-country not empty,
        # proceeding with parsing data correction

        # Setting useful column names
        parse_cols_dic = _set_parse_cols_dic()
        address_id_col = parse_cols_dic["bp_address_id_col"]
        db_id_cols_dic = _set_db_id_cols_dict()
        database_id_col = db_id_cols_dic[database_type]

        # Updating history of corrected addresses by the user
        dedup_cols = [database_id_col, address_id_col]
        addresses_to_correct_df = _update_corrected_addresses_history(addresses_to_correct_df,
                                                                      corrected_addresses_path,
                                                                      database_type, corpus_year,
                                                                      dedup_cols)
        message = "  - History of corrected addresses with unknown-country updated"
        print(message)

        # Getting parsing data to be corrected
        addresses_df = parsing_dict['addresses']
        countries_df = parsing_dict['countries']
        auth_inst_df = parsing_dict['authors_institutions']

        # Correcting the countries parsing data using the user's correction of the addresses with unknown-country
        countries_correct_dfs = [countries_df, addresses_to_correct_df]
        new_countries_df = _correct_parsing_countries(countries_correct_dfs, parse_cols_dic)
        new_countries_df.to_csv(parsing_countries_path, index=False, sep='\t')

        # Correcting the addresses parsing data using the user's correction of the addresses with unknown-country
        addresses_correct_dfs = [addresses_df, addresses_to_correct_df]
        new_addresses_df = _correct_parsing_addresses(addresses_correct_dfs, parse_cols_dic)
        new_addresses_df.to_csv(parsing_addresses_path, index=False, sep='\t')

        # Getting affiliations normalization data for correction of authors-institutions parsing data
        norm_dicts = build_norm_dicts(institute, wf_path)

        # Correcting the authors-institutions parsing data
        # using the user's correction of addresses with unknown-country
        authsinst_correct_dfs = [auth_inst_df, addresses_to_correct_df]
        new_auth_inst_df = _correct_parsing_authsinst(authsinst_correct_dfs, parse_cols_dic,
                                                      norm_dicts, unknown_country)
        new_auth_inst_df.to_csv(parsing_authsinst_path, index=False, sep='\t')
        correct_status = True

        # Clear data of addresses with unknown-country to be corrected
        _save_addresses_to_correct_data(addresses_to_correct_df, addresses_to_correct_path,
                                        database_type, corpus_year, file_clear=True)
        print("  - Data for correction of addresses with unknown-country cleaned")
    return correct_status
