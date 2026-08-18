"""Module of functions for correcting final data of deduplicated parsings
using corrected addresses by the user.
"""

__all__ = ['correct_dedup',
           'initialize_addresses_to_correct_file',
          ]


# Standard Library imports
from pathlib import Path

# 3rd party imports
import pandas as pd
from bpfuncts import standardize_address as bp_standardize_address
from bpfuncts import build_addr_affils_tup as bp_build_addr_affils_tup

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import format_page
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.useful_functs import build_list_from_str
from bmfuncts.useful_functs import build_string_from_list
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import drop_multiple_item
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import set_year_pub_id


def _set_dedup_cols_dic():
    """Builds a dict setting selected columns names for the process 
    of correcting the data of parsings deduplication from corrected 
    addresses by the user.

    Returns:
        (dict): The built dict.
    """
    dedup_cols_dic = {'bm_hash_id_col'     : bm_pg.COL_HASH['hash_id'],
                      'bp_pub_id_col'      : bm_pg.COL_NAMES['pub_id'],
                      'bp_doi_col'         : bm_pg.COL_NAMES['articles'][6],
                      'bp_address_id_col'  : bm_pg.COL_NAMES['address'][1],
                      'bp_address_col'     : bm_pg.COL_NAMES['address'][2],
                      'bp_country_col'     : bm_pg.COL_NAMES['country'][2],
                      'bp_author_id_col'   : bm_pg.COL_NAMES['auth_inst'][1],
                      'bp_norm_affils_col' : bm_pg.COL_NAMES['auth_inst'][4],
                      'author_ids_col'     : "Author IDs",
                      'correct_address_col': "Correct address",
                     }
    return dedup_cols_dic


def _set_correct_dedup_paths(final_results_path, corpus_year, correction_item_filenames,
                             test_txt=""):
    """Builds a list of useful paths for the process of correcting the data 
    of parsings deduplication using corrected addresses by the user.

    Args:
        final_results_path (path): Full path to the folder where the final \
        results of parsings deduplication are saved.
        corpus_year (str): Corpus year defined by 4 digits.
        correction_item_filenames (list): The file names (str) of the parsing items \
        to be corrected.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default: "").
    Returns:
        (list): The built list of paths.
    """
    # Internal functions
    def _set_parsing_item_path(_item_filename):
        parsing_item_file = test_txt + _item_filename + parsing_extent
        parsing_item_path = dedup_parsing_path / Path(parsing_item_file)
        return parsing_item_path

    # Setting useful aliases
    parsing_extent = "." + bm_pg.TSV_SAVE_EXTENT
    saved_dedup_parsing_folder_alias = bm_pg.ARCHI_RESULTS["dedup_parsing"]
    corrected_addresses_history_file_alias = bm_pg.ARCHI_RESULTS["corrected_addresses_file"]

    # Setting path of deduplicated parsings
    year_final_results_path = final_results_path / Path(corpus_year)
    dedup_parsing_path = year_final_results_path / Path(saved_dedup_parsing_folder_alias)

    # Setting paths for addresses correction
    corrected_addresses_path = dedup_parsing_path / Path(corrected_addresses_history_file_alias)

    paths_list = [corrected_addresses_path]
    # Setting list of full paths to the parsing data to be corrected
    compl_paths_list = [_set_parsing_item_path(item_filename)
                        for item_filename in correction_item_filenames]
    paths_list = paths_list + compl_paths_list
    return paths_list


def initialize_addresses_to_correct_file(addresses_to_correct_path, corrected_addresses_path,
                                         corpus_year, print_params, file_clean=False):
    """Manages the initialization of the file for correcting 
    false addresses identified by the user.

    Args:
        addresses_to_correct_path (path): The full path to the file \
        for correcting false addresses.
        corrected_addresses_path (path): The full path to the file \
        of history of false addresses correction.
        corpus_year (str): Corpus year defined by 4 digits.
        print_params (list): The print parameters.
        file_clean 'bool): Optional, if True the existing file is \
        replaced by a formated empty file (default: False).
    """
    # internal functions
    def _save_file(_addresses_to_correct_df):
        # Saving false-addresses data
        df_title = bm_pg.DF_TITLES_LIST[19]
        wb, ws = format_page(_addresses_to_correct_df, df_title)
        ws.title = "False addr " + corpus_year
        wb.save(addresses_to_correct_path)

    def _save_empty_file():
        # Setting false-addresses empty data
        cols_nb = len(addresses_to_correct_cols)
        empty_data_row = [""] * cols_nb
        empty_data = sum([], [empty_data_row]*10)
        addresses_to_correct_df = pd.DataFrame(empty_data, columns=addresses_to_correct_cols)
        _save_file(addresses_to_correct_df)

    # Setting useful column names
    dedup_cols_dic = _set_dedup_cols_dic()
    cols_keys = ['bm_hash_id_col', 'bp_pub_id_col', 'bp_doi_col', 'bp_address_id_col',
                 'bp_country_col', 'bp_address_col', 'correct_address_col']
    addresses_to_correct_cols = [dedup_cols_dic[key] for key in cols_keys]

    # Setting status of data for addresses correction
    corrected_addresses_isfile = corrected_addresses_path.is_file()
    addresses_to_correct_isfile = addresses_to_correct_path.is_file()

    step_txt = "    - File for correction of false addresses by the user unchanged"
    if file_clean:
        _save_empty_file()
        step_txt = "    - File for correction of false addresses by the user cleaned"
    else:
        if not corrected_addresses_isfile and not addresses_to_correct_isfile:
            _save_empty_file()
            step_txt = "    - Empty file for correction of false addresses by the user created"
        elif corrected_addresses_isfile:
            # Using the history of corrected addresses
            corrected_addresses_hist_df = pd.read_excel(corrected_addresses_path)
            addresses_to_correct_hist_df = corrected_addresses_hist_df[addresses_to_correct_cols]
            addresses_to_correct_df = addresses_to_correct_hist_df.copy()

            if addresses_to_correct_isfile:
                user_addresses_to_correct_df = pd.read_excel(addresses_to_correct_path)
                addresses_to_correct_df = concat_dfs([addresses_to_correct_hist_df, user_addresses_to_correct_df])
                step_txt = ("    - File for correction of false addresses by the user updated "
                            "with history of corrected addresses")
            else:
                step_txt = ("    - File for correction of false addresses by the user created "
                            "with history of corrected addresses")
            _save_file(addresses_to_correct_df)
    print_step_text(step_txt, print_params)


def _add_auth_ids_to_false_address_data(init_correct_dfs, dedup_cols_dic, ids_dicts_list):
    """Adds to each address to correct, the IDs of the authors of wich affiliations 
    contain the false address.

    Args:
        init_correct_dfs (list): The list composed of the data (dataframe) \
        of authors with affiliations and of the initial data (dataframe) \
        of the addresses to correct.
        dedup_cols_dic (dict): The selected columns names for the process \
        of correcting the data of parsings deduplication.
        ids_dicts_list (list): The list composed of the data (dict) of hash ID \
        per publication ID and the data (dict) of DOI per publication ID.
    Returns:
        (bool): True if no false address is found.
    """
    # Setting data from 'all_correct_dfs'
    authaddr_df, addresses_to_correct_df = init_correct_dfs

    # Setting useful column names
    cols_keys = ['bm_hash_id_col', 'bp_pub_id_col', 'bp_doi_col', 'bp_address_id_col', 'bp_country_col',
                 'bp_address_col', 'correct_address_col', 'author_ids_col', 'bp_author_id_col']
    (hash_id, pub_id_col, doi_col, address_id_col, country_col, address_col, correct_address_col,
     author_ids_col, author_id_col) = [dedup_cols_dic[key] for key in cols_keys]

    # Setting hash-ID and DOI per publication data from args
    hash_ids_dict, dois_dict = ids_dicts_list

    correct_addresses_cols = [hash_id, pub_id_col, doi_col, address_id_col, country_col,
                              address_col, correct_address_col, author_ids_col]
    data = []
    for _, corr_row in addresses_to_correct_df.iterrows():
        pub_id_str = corr_row[pub_id_col]
        address_id = corr_row[address_id_col]
        false_address = corr_row[address_col]
        correct_address = corr_row[correct_address_col]
        country = corr_row[country_col]
        hash_id = hash_ids_dict[pub_id_str]
        pub_id_int = int(pub_id_str[5:])
        doi = dois_dict[pub_id_int]
        pub_id_authaddr_df = authaddr_df[authaddr_df[pub_id_col]==pub_id_int]

        false_address_auth_ids_list = []
        for _, authaddr_row in pub_id_authaddr_df.iterrows():
            author_id = authaddr_row[author_id_col]

            # Building author's addresses-list
            author_addresses_str = authaddr_row[address_col]
            author_addresses_list = build_list_from_str(author_addresses_str, "; ")
            author_addresses_list = [bp_standardize_address(x) for x in author_addresses_list]

            # Searching for false address in the author's addresses-list to append author's ID
            std_false_address = bp_standardize_address(false_address, add_unknown_country=False)

            if std_false_address in author_addresses_list:
                false_address_auth_ids_list.append(str(author_id))

        # Building a string from the built IDs list of authors
        false_address_auth_ids = build_string_from_list(false_address_auth_ids_list, "; ")
        data.append([hash_id, pub_id_str, doi, address_id, country, false_address,
                     correct_address, false_address_auth_ids])
    corrected_addresses_df = pd.DataFrame(data, columns=correct_addresses_cols)
    return corrected_addresses_df


def _update_corrected_addresses_history(addresses_to_correct_df, corrected_addresses_path,
                                        corpus_year, dedup_cols, print_params):
    """Updates the history of the corrected-addresses data and saves them.

    Args:
        addresses_to_correct_df (dataframe): False-addresses data corrected by the user \
        and enhanced with publications' hash-IDs, DOIs and list of authors' IDs of which \
        address is false.
        corrected_addresses_path (path): Full path to the existing history of corrected \
        addresses data before update.
        corpus_year (str): Corpus year defined by 4 digits.
        dedup_cols (list): Columns names for deduplicating rows in updated data.
    """
    new_corrected_addresses_hist_df = addresses_to_correct_df.copy()
    # Getting the history of corrected addresses before update
    if corrected_addresses_path.is_file():
        corrected_addresses_hist_df = pd.read_excel(corrected_addresses_path)

        # Concatenating the existing history of corrected countries data with the user's corrected ones
        new_corrected_addresses_hist_df = concat_dfs([corrected_addresses_hist_df, addresses_to_correct_df],
                                                     dedup_cols=dedup_cols)
        step_txt = "    - History of corrected addresses updated"
    else:
        step_txt = "    - History of corrected addresses created"
    print_step_text(step_txt, print_params)

    # Saving false addresses data
    df_title = bm_pg.DF_TITLES_LIST[19]
    wb, ws = format_page(new_corrected_addresses_hist_df, df_title)
    ws.title = 'Correct addresses ' + corpus_year
    wb.save(corrected_addresses_path)
    return new_corrected_addresses_hist_df


def _correct_dedup_countries(countries_correct_dfs, dedup_cols_dic, parsing_countries_path, corpus_year):
    """Corrects the parsing data of countries using the data of addresses corrected by the user.

    Args:
        countries_correct_dfs (list): Composed of the parsing data of countries (dataframe) \
        and of the user's correction of the false addresses (dataframe).
        dedup_cols_dic (dict): The selected columns names for the process \
        of correcting the data of parsings deduplication.
        parsing_countries_path (path): The full path for saving the corrected parsing data of countries.
        corpus_year (str): Corpus year defined by 4 digits.
    """
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_country_col']
    pub_id_col, address_id_col, country_col = [dedup_cols_dic[key] for key in cols_keys]

    countries_df, corrected_addresses_df = countries_correct_dfs
    correct_pub_ids_list = corrected_addresses_df[pub_id_col].to_list()

    new_countries_df = pd.DataFrame(columns=countries_df.columns)
    for _, pub_id_df in countries_df.groupby(pub_id_col):
        pub_id_countries_df = pub_id_df.copy()
        mod_pub_id_df = set_year_pub_id(pub_id_df, corpus_year, pub_id_col)
        pub_id_str = mod_pub_id_df[pub_id_col].to_list()[0]
        if pub_id_str in correct_pub_ids_list:
            pub_id_correct_address_df = corrected_addresses_df[corrected_addresses_df[pub_id_col]==pub_id_str]

            # Building a dict keyed by address ID and valued by correct country
            correct_address_ids_list = pub_id_correct_address_df[address_id_col].to_list()
            correct_countries_list = pub_id_correct_address_df[country_col].to_list()
            correct_countries_dict = dict(zip(correct_address_ids_list, correct_countries_list))

            # Searching for each address ID of correct-addresses data in initial countries of 'pub_id' data
            # Then replacing false countries by correct countries
            for correct_address_id in correct_address_ids_list:
                for num_row, row in pub_id_countries_df.iterrows():
                    false_address_id = row[address_id_col]
                    if correct_address_id==false_address_id:
                        correct_country = correct_countries_dict[correct_address_id]
                        pub_id_countries_df.loc[num_row, country_col] = correct_country
        new_countries_df = concat_dfs([new_countries_df, pub_id_countries_df])
    new_countries_df.to_csv(parsing_countries_path, index=False, sep='\t')


def _correct_dedup_addresses(addresses_correct_dfs, dedup_cols_dic, parsing_addresses_path, corpus_year):
    """Corrects the parsing data of countries using the data of addresses corrected by the user.

    Args:
        addresses_correct_dfs (list): Composed of the parsing data of addresses (dataframe) \
        and of the user's correction of the false addresses (dataframe).
        dedup_cols_dic (dict): The selected columns names for the process \
        of correcting the data of parsings deduplication.
        parsing_addresses_path (path): The full path for saving the corrected parsing data of addresses.
        corpus_year (str): Corpus year defined by 4 digits.
    """
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_address_col',
                 'correct_address_col']
    (pub_id_col, address_id_col, address_col,
     correct_address_col) = [dedup_cols_dic[key] for key in cols_keys]

    addresses_df, corrected_addresses_df = addresses_correct_dfs
    correct_pub_ids_list = corrected_addresses_df[pub_id_col].to_list()

    new_addresses_df = pd.DataFrame(columns=addresses_df.columns)
    for _, pub_id_df in addresses_df.groupby(pub_id_col):
        pub_id_addresses_df = pub_id_df.copy()
        mod_pub_id_df = set_year_pub_id(pub_id_df, corpus_year, pub_id_col)
        pub_id_str = mod_pub_id_df[pub_id_col].to_list()[0]
        if pub_id_str in correct_pub_ids_list:
            pub_id_correct_address_df = corrected_addresses_df[corrected_addresses_df[pub_id_col]==pub_id_str]

            # Building a dict keyed by address ID and valued by correct address
            pub_id_corr_addr_ids_list = pub_id_correct_address_df[address_id_col].to_list()
            pub_id_corr_addr_list = pub_id_correct_address_df[correct_address_col].to_list()
            pub_id_corr_addr_dict = dict(zip(pub_id_corr_addr_ids_list, pub_id_corr_addr_list))

            # Searching for each address ID of correct-addresses data in initial addresses of 'pub_id' data
            # Then replacing false addresses by correct addresses
            for correct_address_id in pub_id_corr_addr_ids_list:
                for num_row, row in pub_id_addresses_df.iterrows():
                    false_address_id = row[address_id_col]
                    if correct_address_id==false_address_id:
                        correct_address = pub_id_corr_addr_dict[correct_address_id]
                        pub_id_addresses_df.loc[num_row, address_col] = correct_address
        new_addresses_df = concat_dfs([new_addresses_df, pub_id_addresses_df])
    new_addresses_df.to_csv(parsing_addresses_path, index=False, sep='\t')


def _correct_dedup_authaddr(authaddr_correct_dfs, dedup_cols_dic, parsing_authaddr_path,
                            dedup_affil_params_dic, corpus_year):
    """Corrects the parsing data of authors-addresses using the data 
    of addresses corrected by the user.

    In addition, the normalized and raw affiliations are defined for 
    the corrected addresses of authors using the `bo_build_addr_affils_tup` 
    function imported from the `biblioparsing` package. 
    This function requires data per country for normalizing the authors affiliations, 
    the data of affiliations types and the data of towns per country.

    Args:
        authaddr_correct_dfs (list): Composed of the parsing data (dataframe) of \
        authors-addresses and of the user's correction of the false addresses (dataframe).
        dedup_cols_dic (dict): The selected columns names for the process \
        of correcting the data of parsings deduplication.
        parsing_authaddr_path (path): The full path for saving the corrected parsing data \
        of authors-addresses.
        dedup_affil_params_dic (dict): Gives the full paths to the Institute's files to use for \
        authors' affiliations parsing at parsing deduplication step.
        corpus_year (str): Corpus year defined by 4 digits.
    """
    cols_keys = ['bp_pub_id_col', 'bp_address_col', 'bp_country_col', 'bp_author_id_col',
                 'author_ids_col', 'bp_norm_affils_col', 'correct_address_col']
    (pub_id_col, address_col, country_col, author_id_col, author_ids_col,
     norm_affils_col, correct_address_col) = [dedup_cols_dic[key] for key in cols_keys]

    authaddr_df, corrected_addresses_df = authaddr_correct_dfs
    correct_pub_ids_list = corrected_addresses_df[pub_id_col].to_list()

    new_authaddr_df = pd.DataFrame(columns=authaddr_df.columns)
    for _, pub_id_df in authaddr_df.groupby(pub_id_col):
        pub_id_authaddr_df = pub_id_df.copy()
        mod_pub_id_df = set_year_pub_id(pub_id_df, corpus_year, pub_id_col)
        pub_id_str = mod_pub_id_df[pub_id_col].to_list()[0]
        if pub_id_str in correct_pub_ids_list:
            pub_id_correct_address_df = corrected_addresses_df[corrected_addresses_df[pub_id_col]==pub_id_str]
            for _, correct_address_row in pub_id_correct_address_df.iterrows():
                false_address = correct_address_row[address_col]
                correct_address = correct_address_row[correct_address_col]
                correct_country = correct_address_row[country_col]
                auth_ids_str = str(correct_address_row[author_ids_col])
                auth_ids_list = build_list_from_str(auth_ids_str, "; ")
                auth_ids_list = [int(x) for x in auth_ids_list]
                for row_num, authaddr_row in pub_id_authaddr_df.iterrows():
                    author_id = authaddr_row[author_id_col]
                    if author_id in auth_ids_list:
                        raw_author_addresses_str = str(authaddr_row[address_col])
                        raw_author_addresses_list = build_list_from_str(raw_author_addresses_str, "; ")
                        author_addresses_list = []
                        for address in raw_author_addresses_list:
                            std_address_str = bp_standardize_address(address)
                            author_addresses_list.append(std_address_str)

                        # Finding index of false address in 'author_addresses_list'
                        if false_address in author_addresses_list:
                            false_addr_idx = author_addresses_list.index(false_address)
                            author_addresses_list[false_addr_idx] = correct_address

                        author_addresses_str = build_string_from_list(author_addresses_list, "; ")
                        pub_id_authaddr_df.loc[row_num, address_col] = author_addresses_str
                        pub_id_authaddr_df.loc[row_num, country_col] = correct_country

                        # Correcting normalized affiliations
                        addr_norm_affils_list = []
                        for auth_address in author_addresses_list:
                            author_addr_aff_tup = bp_build_addr_affils_tup(auth_address, dedup_affil_params_dic,
                                                                           drop_status=False)
                            auth_addr_norm_affils_list = author_addr_aff_tup.norm_affils_list
                            addr_norm_affils_list.append(auth_addr_norm_affils_list)

                        addr_norm_affils_list = drop_multiple_item(addr_norm_affils_list, bm_pg.EMPTY)
                        norm_affils_str = build_string_from_list(addr_norm_affils_list, ";")

                        pub_id_authaddr_df.loc[row_num, norm_affils_col] = norm_affils_str

        new_authaddr_df = concat_dfs([new_authaddr_df, pub_id_authaddr_df])
    new_authaddr_df.to_csv(parsing_authaddr_path, index=False, sep='\t')


def correct_dedup(dedup_params_list, ids_dicts_list, test_txt=""):
    """Corrects the parsing data of countries, addresses and authors-addresses 
    using the data of addresses corrected by the user.

    This is done through the `_correct_dedup_countries`, `_correct_dedup_addresses` 
    and `_correct_dedup_authaddr` internal functions.

    Args:
        dedup_params_list (list): The list composed of the 4 digits year of the corpus (str), \
        of the print parameters (list), of the full path to working folder (path), \
        of the dict giving the name of the parsing file for each parsed item, \
        of the dict giving the full paths to the Institute's files to use for \
        authors' affiliations parsing at parsing deduplication step, of the full path to \
        the folder where the final results of parsings-deduplication are saved, and of \
        the full path to the file for correcting false addresses.
        ids_dicts_list (list): The list composed of the data (dict) of hash ID \
        per publication ID and the data (dict) of DOI per publication ID.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default: "").
    Returns:
        (bool): True if the parsing data have been corrected.
    """
    # Internal functions
    def _build_corrected_addresses_data():
        addresses_to_correct_df = pd.read_excel(addresses_to_correct_path)
        new_corrected_addresses_df = addresses_to_correct_df.copy()
        if not addresses_to_correct_df.empty:
            # Adding authors IDs with false addresses to correct addresses data
            init_correct_dfs = [authaddr_df, addresses_to_correct_df]
            new_corrected_addresses_df = _add_auth_ids_to_false_address_data(init_correct_dfs, dedup_cols_dic,
                                                                             ids_dicts_list)

        _corrected_addresses_df = _update_corrected_addresses_history(new_corrected_addresses_df,
                                                                      corrected_addresses_path, corpus_year,
                                                                      dedup_cols, print_params)
        return _corrected_addresses_df

    # Setting useful column names
    dedup_cols_dic = _set_dedup_cols_dic()
    cols_keys = ['bm_hash_id_col', 'bp_address_id_col']
    dedup_cols = [dedup_cols_dic[key] for key in cols_keys]

    # Setting params from "dedup_params_list"
    (corpus_year, print_params, wf_path, parsing_filenames_dict,
     dedup_affil_params_dic, final_results_path, addresses_to_correct_path) = dedup_params_list

    # Setting keys for getting parsing-deduplication results
    correct_dedup_keys = bm_pg.PARSING_KEYS_DIC['correct_parsing']

    # Setting useful paths to files for parsing data correction
    correction_item_filenames = [parsing_filenames_dict[key] for key in correct_dedup_keys]
    correct_paths_list = _set_correct_dedup_paths(final_results_path, corpus_year,
                                                  correction_item_filenames, test_txt)
    (corrected_addresses_path, parsing_addresses_path,
     parsing_authaddr_path, parsing_countries_path) = correct_paths_list

    # Setting parsing data for the correction process
    dedup_read_params = [corpus_year, parsing_filenames_dict, final_results_path]
    parsing_dict = read_final_dedup(dedup_read_params)
    addresses_df, authaddr_df, countries_df = [parsing_dict[key] for key in correct_dedup_keys]

    # Initializing status of addresses to correct
    correct_status = False
    print_step_text("  - Initializing file of addresses to correct by the user...", print_params)
    initialize_addresses_to_correct_file(addresses_to_correct_path, corrected_addresses_path,
                                         corpus_year, print_params)

    # Getting data of the user's correction of the addresses to correct
    print_step_text("  - Building data for addresses correction...", print_params)
    corrected_addresses_df = _build_corrected_addresses_data()

    if not corrected_addresses_df.empty:
        print_step_text("  - Correcting addresses in deduplication-parsing data...", print_params)

        # Correcting the countries parsing data using the user's correction of the addresses
        countries_correct_dfs = [countries_df, corrected_addresses_df]
        _correct_dedup_countries(countries_correct_dfs, dedup_cols_dic, parsing_countries_path, corpus_year)
        print_step_text("    - Countries parsing data corrected", print_params)

        # Correcting the addresses parsing data using the user's correction of the addresses
        addresses_correct_dfs = [addresses_df, corrected_addresses_df]
        _correct_dedup_addresses(addresses_correct_dfs, dedup_cols_dic, parsing_addresses_path, corpus_year)
        print_step_text("    - Addresses parsing data corrected", print_params)

        # Correcting the authors-addresses parsing data using the user's correction of the addresses
        print_step_text("    - Correcting authors-addresses parsing data...", print_params)
        authaddr_correct_dfs = [authaddr_df, corrected_addresses_df]
        _correct_dedup_authaddr(authaddr_correct_dfs, dedup_cols_dic, parsing_authaddr_path,
                                dedup_affil_params_dic, corpus_year)
        print_step_text("    - Authors-addresses parsing data corrected", print_params)

        correct_status = True
        print_step_text("  - Cleaning file of addresses to correct by the user...", print_params)
        initialize_addresses_to_correct_file(addresses_to_correct_path, corrected_addresses_path,
                                             corpus_year, print_params, file_clean=True)
    return correct_status
