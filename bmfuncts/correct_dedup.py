"""Module of functions for correcting parsing data
for instence in the case of unknown countries.
"""

__all__ = ['correct_dedup',
           'initialize_addresses_to_correct_file',
          ]


# Standard Library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.config_utils import set_org_params
from bmfuncts.config_utils import set_parse_inst_params
from bmfuncts.format_files import format_page
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import build_list_from_str
from bmfuncts.useful_functs import build_string_from_list
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import drop_multiple_item
from bmfuncts.useful_functs import read_parsing_dict
from bmfuncts.useful_functs import set_year_pub_id


def _set_dedup_cols_dic():
    """Builds a dict setting selected columns names for the process 
    of getting list of unknown countries per address and per publication.

    Returns:
        (dict): The built dict.
    """
    dedup_cols_dic = {'bm_hash_id_col'     : bm_pg.COL_HASH['hash_id'],
                      'bp_pub_id_col'      : bp.COL_NAMES['pub_id'],
                      'bp_doi_col'         : bp.COL_NAMES['articles'][6],
                      'bp_address_id_col'  : bp.COL_NAMES['address'][1],
                      'bp_address_col'     : bp.COL_NAMES['address'][2],
                      'bp_country_col'     : bp.COL_NAMES['country'][2],
                      'bp_author_id_col'   : bp.COL_NAMES['auth_inst'][1],
                      'bp_norm_inst_col'   : bp.COL_NAMES['auth_inst'][4],
                      'author_ids_col'     : "Author IDs",
                      'correct_address_col': "Correct address",
                     }
    return dedup_cols_dic


def _set_correct_dedup_paths(final_results_path, corpus_year, item_filename_dict="", test_txt=""):
    # Internal functions
    def _set_parsing_item_path(item):
        parsing_item_file = test_txt + item_filename_dict[item] + parsing_extent
        parsing_item_path = dedup_parsing_path / Path(parsing_item_file)
        return parsing_item_path

    # Setting useful aliases
    parsing_extent = "." + bm_pg.TSV_SAVE_EXTENT
    saved_dedup_parsing_folder_alias = bm_pg.ARCHI_RESULTS["dedup_parsing"]
    addresses_to_correct_file_alias = bm_pg.ARCHI_RESULTS["false_addresses_file"]
    corrected_addresses_history_file_alias = bm_pg.ARCHI_RESULTS["corrected_addresses_file"]

    # Setting path of deduplicated parsings
    year_final_results_path = final_results_path / Path(corpus_year)
    dedup_parsing_path = year_final_results_path / Path(saved_dedup_parsing_folder_alias)

    # Setting paths for addresses correction
    addresses_to_correct_path = dedup_parsing_path / Path(addresses_to_correct_file_alias)
    corrected_addresses_path = dedup_parsing_path / Path(corrected_addresses_history_file_alias)
    
    paths_list = []
    paths_list.append(addresses_to_correct_path)
    paths_list.append(corrected_addresses_path)
    if item_filename_dict:
        for item in ['countries', 'addresses', 'authors_institutions']:
            paths_list.append(_set_parsing_item_path(item))
    return paths_list


def initialize_addresses_to_correct_file(addresses_to_correct_path, corpus_year, file_clean=False):
    # internal functions
    def _save_empty_file():
        cols_nb = len(correct_addresses_cols)
        data_row = [""] * cols_nb
        data = sum([], [data_row]*10)
        correct_addresses_df = pd.DataFrame(data, columns=correct_addresses_cols)

        # Saving false-addresses empty data
        df_title = bm_pg.DF_TITLES_LIST[19]
        wb, ws = format_page(correct_addresses_df, df_title) 
        ws.title = "False addr " + corpus_year
        wb.save(addresses_to_correct_path)

    # Setting useful column names    
    dedup_cols_dic = _set_dedup_cols_dic()
    cols_keys = ['bm_hash_id_col', 'bp_pub_id_col', 'bp_doi_col',
                 'bp_address_id_col', 'bp_country_col', 'bp_address_col',
                 'correct_address_col']   
    correct_addresses_cols = [dedup_cols_dic[key] for key in cols_keys]

    # Creating or cleaning the false-addresses file
    if addresses_to_correct_path.is_file() and not file_clean:
        message = ("    - File for correcting false addresses already exist")
    else:
        _save_empty_file()
        if file_clean:
            message = ("    - File for correction of false addresses by the user cleaned")
        else:
            message = ("    - Empty file for correction of false addresses created")
    return message


def _add_auth_ids_to_false_address_data(all_correct_dfs, dedup_cols_dic, ids_dicts_list):
    """Builds data of unknown countries in authors addresses and saves these data 
    as an Openpyxl workbook for correction by the user.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the data (dataframes) of parsing results.
        parsing_path (path): Full path to the folder of the parsing results.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        corpus_year (str): Corpus year defined by 4 digits.
    Returns:
        (bool): True if no unknown country is found.
    """
    # Setting data from 'all_correct_dfs'
    (countries_df, auth_inst_df, correct_addresses_df) = all_correct_dfs

    # Setting useful column names    
    dedup_cols_dic = _set_dedup_cols_dic()
    cols_keys = ['bm_hash_id_col', 'bp_pub_id_col', 'bp_doi_col', 'bp_address_id_col', 'bp_country_col',
                 'bp_address_col', 'correct_address_col', 'author_ids_col', 'bp_author_id_col']   
    (hash_id, pub_id_col, doi_col, address_id_col, country_col, address_col, correct_address_col,
     author_ids_col, author_id_col) = [dedup_cols_dic[key] for key in cols_keys]

    # Setting hash-ID and DOI per publication data from args
    hash_ids_dict, dois_dict = ids_dicts_list

    correct_addresses_cols = [hash_id, pub_id_col, doi_col, address_id_col, country_col,
                              address_col, correct_address_col, author_ids_col]
    data = []
    for _, corr_row in correct_addresses_df.iterrows():
        pub_id_str = corr_row[pub_id_col]
        address_id = corr_row[address_id_col]
        false_address = corr_row[address_col]
        correct_address = corr_row[correct_address_col]
        country = corr_row[country_col]
        hash_id = hash_ids_dict[pub_id_str]
        pub_id_int = int(pub_id_str[5:])
        doi = dois_dict[pub_id_int]
        pub_id_auth_inst_df = auth_inst_df[auth_inst_df[pub_id_col]==pub_id_int]

        false_address_auth_ids_list = []
        for _, auth_inst_row in pub_id_auth_inst_df.iterrows():
            author_id = auth_inst_row[author_id_col]

            # Building author's addresses-list 
            author_addresses_str = auth_inst_row[address_col]
            author_addresses_list = build_list_from_str(author_addresses_str, "; ")
            author_addresses_list = [bp.standardize_address(x) for x in author_addresses_list]

            # Searching for false address in the author's adresses-list to append author's ID
            std_false_address = bp.standardize_address(false_address)

            if std_false_address in author_addresses_list:
                false_address_auth_ids_list.append(str(author_id))

        # Building a string from the built IDs list of authors
        false_address_auth_ids = build_string_from_list(false_address_auth_ids_list, "; ")
        data.append([hash_id, pub_id_str, doi, address_id, country, false_address,
                     correct_address, false_address_auth_ids])
    new_correct_addresses_df = pd.DataFrame(data, columns=correct_addresses_cols)
    return new_correct_addresses_df


def _update_corrected_addresses_history(addresses_to_correct_df, corrected_addresses_path,
                                        corpus_year, dedup_cols):
    """Updates the history of the corrected-addresses data and saves them.

    Args:
        addresses_to_correct_df (dataframe): False-addresses data corrected by the user \
        and enhanced with publications' hash-IDs, DOIs and list of authors' IDs of which \
        address is false.
        corrected_addresses_path (path): Full path to the existing history of corrected \
        addresses data before update.
        corpus_year (str): Corpus year defined by 4 digits.
        dedup_cols (list): Columns names for deduplicating rows in updated data.
    Returns:
        (dataframe): The updated data of history of the corrected-addresses.
    """
    new_corrected_addresses_hist_df = addresses_to_correct_df.copy()
    # Getting the history of corrected countries before umpdate
    if corrected_addresses_path.is_file():
        init_corrected_addresses_hist_df = pd.read_excel(corrected_addresses_path)

        # Concatenating the existing history of corrected countries data with the user's corrected ones
        new_corrected_addresses_hist_df = concat_dfs([init_corrected_addresses_hist_df,
                                                      addresses_to_correct_df],
                                                     dedup_cols=dedup_cols)    
        message = ("    - History of corrected addresses updated")
    else:
        message = ("    - History of corrected addresses created")

    # Saving unknown-countries data
    df_title = bm_pg.DF_TITLES_LIST[19]
    wb, ws = format_page(new_corrected_addresses_hist_df, df_title) 
    ws.title = 'Correct addresses ' + corpus_year
    wb.save(corrected_addresses_path)
    
    print(message)
    return new_corrected_addresses_hist_df


def _correct_dedup_countries(countries_correct_dfs, parse_cols_dic, parsing_countries_path, corpus_year):
    """Corrects the parsing data of countries using the data of unknown countries corrected by the user.

    Args:
        countries_correct_dfs (list): Composed of the parsing data of countries (dataframe) \
        and of the user's correction of the unkown countries (dataframe).
        parse_cols_dic (dict): The dict giving the columns names for the \
        process of correcting parsing data.
        parsing_countries_path (path): The full path for saving the corrected parsing data of countries.
    Returns:
        (str): Final message.
    """
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_country_col']   
    pub_id_col, address_id_col, country_col = [parse_cols_dic[key] for key in cols_keys]

    countries_df, correct_addresses_df = countries_correct_dfs
    correct_pub_ids_list = correct_addresses_df[pub_id_col].to_list()
    
    new_countries_df = pd.DataFrame(columns=countries_df.columns)
    for pub_id, pub_id_df in countries_df.groupby(pub_id_col):
        pub_id_countries_df = pub_id_df.copy()
        mod_pub_id_df = set_year_pub_id(pub_id_df, corpus_year, pub_id_col)
        pub_id_str = mod_pub_id_df[pub_id_col].to_list()[0]
        if pub_id_str in correct_pub_ids_list:
            pub_id_correct_address_df = correct_addresses_df[correct_addresses_df[pub_id_col]==pub_id_str]

            # Building a dict keyyed by address ID and valued by correct country
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
    message = ("    - Countries parsing data corrected")
    print(message)
    return new_countries_df


def _correct_dedup_addresses(addresses_correct_dfs, parse_cols_dic, parsing_addresses_path, corpus_year):
    """Corrects the parsing data of countries using the data of unknown countries corrected by the user.

    Args:
        addresses_correct_dfs (list): Composed of the parsing data of addresses (dataframe) \
        and of the user's correction of the unkown countries (dataframe).
        parse_cols_dic (dict): The dict giving the columns names for the \
        process of correcting parsing data.
        parsing_addresses_path (path): The full path for saving the corrected parsing data of addresses.
    Returns:
        (str): Final message.
    """
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_address_col',
                 'bp_country_col', 'correct_address_col']   
    (pub_id_col, address_id_col, address_col, country_col,
     correct_address_col) = [parse_cols_dic[key] for key in cols_keys]

    addresses_df, correct_addresses_df = addresses_correct_dfs
    correct_pub_ids_list = correct_addresses_df[pub_id_col].to_list()

    new_addresses_df = pd.DataFrame(columns=addresses_df.columns)
    for pub_id, pub_id_df in addresses_df.groupby(pub_id_col):
        pub_id_addressess_df = pub_id_df.copy()
        mod_pub_id_df = set_year_pub_id(pub_id_df, corpus_year, pub_id_col)
        pub_id_str = mod_pub_id_df[pub_id_col].to_list()[0]
        if pub_id_str in correct_pub_ids_list:
            pub_id_correct_address_df = correct_addresses_df[correct_addresses_df[pub_id_col]==pub_id_str]

            # Building a dict keyyed by address ID and valued by correct address
            pub_id_corr_addr_ids_list = pub_id_correct_address_df[address_id_col].to_list()
            pub_id_corr_addr_list = pub_id_correct_address_df[correct_address_col].to_list()
            pub_id_corr_addr_dict = dict(zip(pub_id_corr_addr_ids_list, pub_id_corr_addr_list))

            # Searching for each address ID of correct-addresses data in initial addresses of 'pub_id' data
            # Then replacing false addresses by correct addresses
            for correct_address_id in pub_id_corr_addr_ids_list:
                for num_row, row in pub_id_addressess_df.iterrows():
                    false_address_id = row[address_id_col]
                    if correct_address_id==false_address_id:
                        correct_address = pub_id_corr_addr_dict[correct_address_id]
                        pub_id_addressess_df.loc[num_row, address_col] = correct_address
        new_addresses_df = concat_dfs([new_addresses_df, pub_id_addressess_df])
    new_addresses_df.to_csv(parsing_addresses_path, index=False, sep='\t')
    message = ("    - Addresses parsing data corrected")
    print(message)
    return new_addresses_df


def _correct_dedup_authsinst(authsinst_correct_dfs, parse_cols_dic,
                             parsing_authsinst_path, norm_dicts, corpus_year):
    """Corrects the parsing data of authors-institutions using the data 
    of unknown countries corrected by the user.

    In addition, the normalized and raw affiliations are defined for 
    the corrected addresses of authors using the `address_inst_full_list` 
    function imported from the `BiblioParsing` package itself imported as bp. 
    This function requires data per country for normalizing the authors affiliations, 
    the data of affiliations types and the data of towns per country.

    Args:
        authsinst_correct_dfs (list): Composed of the parsing data (dataframe) of \
        authors-institutions and of the user's correction of the unkown countries (dataframe).
        parse_cols_dic (dict): The dict giving the columns names for the process \
        of correcting parsing data.
        parsing_authsinst_path (path): The full path for saving the corrected parsing data \
        of authors-institutions.
        norm_dicts (list): Composed of the data per country for normalizing the authors' \
        affiliations (dict), the data (dict) of affiliations types and the data (dict) \
        of towns per country.
    Returns:
        (str): Final message.
    """
    cols_keys = ['bp_pub_id_col', 'bp_address_col', 'bp_country_col', 'bp_author_id_col',
                 'author_ids_col', 'bp_norm_inst_col', 'correct_address_col']   
    (pub_id_col, address_col, country_col, author_id_col, author_ids_col,
     norm_inst_col, correct_address_col) = [parse_cols_dic[key] for key in cols_keys]

    norm_raw_aff_dict, aff_type_dict, towns_dict = norm_dicts

    auth_inst_df, correct_addresses_df = authsinst_correct_dfs
    correct_pub_ids_list = correct_addresses_df[pub_id_col].to_list()

    new_auth_inst_df = pd.DataFrame(columns=auth_inst_df.columns)
    for pub_id, pub_id_df in auth_inst_df.groupby(pub_id_col):
        pub_id_auths_inst_df = pub_id_df.copy()
        mod_pub_id_df = set_year_pub_id(pub_id_df, corpus_year, pub_id_col)
        pub_id_str = mod_pub_id_df[pub_id_col].to_list()[0]
        if pub_id_str in correct_pub_ids_list:
            pub_id_correct_address_df = correct_addresses_df[correct_addresses_df[pub_id_col]==pub_id_str]
            for _, correct_address_row in pub_id_correct_address_df.iterrows():
                false_address = correct_address_row[address_col]
                correct_address = correct_address_row[correct_address_col]
                correct_country = correct_address_row[country_col]
                auth_ids_str = str(correct_address_row[author_ids_col])
                auth_ids_list = build_list_from_str(auth_ids_str, "; ")
                auth_ids_list = [int(x) for x in auth_ids_list]
                for row_num, auths_inst_row in pub_id_auths_inst_df.iterrows():
                    author_id = auths_inst_row[author_id_col]
                    if author_id in auth_ids_list:
                        raw_author_addresses_str = str(auths_inst_row[address_col])
                        raw_author_addresses_list = build_list_from_str(raw_author_addresses_str, "; ")
                        author_addresses_list = []
                        for address in raw_author_addresses_list:
                            std_address_str = bp.standardize_address(address)
                            author_addresses_list.append(std_address_str)

                        # Finding index of false address in 'author_addresses_list'
                        false_addr_idx = author_addresses_list.index(false_address)
                        author_addresses_list[false_addr_idx] = correct_address

                        author_addresses_str = build_string_from_list(author_addresses_list, "; ")
                        pub_id_auths_inst_df.loc[row_num, address_col] = author_addresses_str
                        pub_id_auths_inst_df.loc[row_num, country_col] = correct_country

                        # Correcting normalized affiliations
                        addr_norm_inst_list = []
                        for auth_address in author_addresses_list:
                            author_addr_aff_tup = bp.address_inst_full_list(auth_address, norm_raw_aff_dict,
                                                                            aff_type_dict, towns_dict,
                                                                            drop_status=False)
                            auth_addr_norm_inst_list = author_addr_aff_tup.norm_inst_list
                            addr_norm_inst_list.append(auth_addr_norm_inst_list)

                        addr_norm_inst_list = drop_multiple_item(addr_norm_inst_list, bp.EMPTY)
                        norm_inst_str = build_string_from_list(addr_norm_inst_list, ";")

                        pub_id_auths_inst_df.loc[row_num, norm_inst_col] = norm_inst_str

        new_auth_inst_df = concat_dfs([new_auth_inst_df, pub_id_auths_inst_df])
    new_auth_inst_df.to_csv(parsing_authsinst_path, index=False, sep='\t')
    message = ("    - Authors-institutions parsing data corrected")
    print(message)
    return new_auth_inst_df


def correct_dedup(params_list, final_results_path, item_filename_dict, ids_dicts_list, test_txt=""):
    """Corrects the parsing data of countries, addresses and authors-institutions 
    using the data of unknown countries corrected by the user.

    This is done through the `_correct_parsing_countries`, `_correct_parsing_addresses` 
    and `_correct_parsing_authsinst` internal functions.
    For this last function, it builts 3 dicts:
    - The data per country for normalizing the authors affiliations \
    through the `build_norm_raw_affiliations_dict` function;
    - The data of affiliations types through the `read_inst_types` function; 
    - The data of towns per country through the `read_towns_per_country` function.
    These 3 functions are imported from the BiblioParsing package itself imported as bp. 

    Args:
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        parsing_path (path): Full path to the folder of the parsing results.
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the data (dataframes) of parsing results.
        item_filename_dict (dict): Dict keyed by the parsing items \
        and valued by the file names for saving the parsing results.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default="").
    Returns:
        (bool): True if the parsing data have been corrected.
    """
    # Internal functions
    def _build_corrected_addresses_data():
        addresses_to_correct_df = init_addresses_to_correct_df.copy()
        if not init_addresses_to_correct_df.empty:
            # Adding authors IDs with false addresses to correct addresses data
            all_correct_dfs = [countries_df, auth_inst_df, init_addresses_to_correct_df] 
            addresses_to_correct_df = _add_auth_ids_to_false_address_data(all_correct_dfs, dedup_cols_dic,
                                                                          ids_dicts_list)
            
        corrected_addresses_df = _update_corrected_addresses_history(addresses_to_correct_df,
                                                                     corrected_addresses_path,
                                                                     corpus_year, dedup_cols)
        return corrected_addresses_df

    # Setting useful column names
    dedup_cols_dic = _set_dedup_cols_dic()
    cols_keys = ['bm_hash_id_col', 'bp_address_id_col'] 
    dedup_cols = [dedup_cols_dic[key] for key in cols_keys]
    
    # Setting params from "params_list"
    institute, wf_path, datatype, corpus_year = params_list

    # Setting useful paths to files for parsing data correction
    correct_paths_list = _set_correct_dedup_paths(final_results_path, corpus_year,
                                                  item_filename_dict, test_txt)
    (addresses_to_correct_path, corrected_addresses_path, parsing_countries_path,
     parsing_addresses_path, parsing_authsinst_path) = correct_paths_list
    
    # Setting parsing data for the correction process
    parsing_dict = read_final_dedup(wf_path, final_results_path, corpus_year)
    addresses_df = parsing_dict['addresses']
    countries_df = parsing_dict['countries']
    auth_inst_df = parsing_dict['authors_institutions']

    # Initializing status
    correct_status = False
    addresses_to_correct_status = addresses_to_correct_path.is_file()
    corrected_addresses_status = corrected_addresses_path.is_file()
        
    if not addresses_to_correct_status:
        print("\n    Initializing file of addresses to correct by the user...")
        message = initialize_addresses_to_correct_file(addresses_to_correct_path, corpus_year)
        print(message)

    # Getting data of the user's correction of the unknown countries
    print("\n    Building data for addresses correction...")
    init_addresses_to_correct_df = pd.read_excel(addresses_to_correct_path)    
    corrected_addresses_df = _build_corrected_addresses_data()
        
    if not corrected_addresses_df.empty:
        print("\n    Correcting addresses in deduplication-parsing data...")
        
        # Correcting the countries parsing data using the user's correction of the addresses
        countries_correct_dfs = [countries_df, corrected_addresses_df]
        _ = _correct_dedup_countries(countries_correct_dfs, dedup_cols_dic,
                                     parsing_countries_path, corpus_year)

        # Correcting the addresses parsing data using the user's correction of the addresses
        addresses_correct_dfs = [addresses_df, corrected_addresses_df]
        _ = _correct_dedup_addresses(addresses_correct_dfs, dedup_cols_dic,
                                     parsing_addresses_path, corpus_year)

        # Getting intitutions normalization data for correction authors-institutions parsing data
        inst_country_towns_file, inst_paths_list = set_parse_inst_params(institute, wf_path)
        norm_raw_aff_dict = bp.build_norm_raw_affiliations_dict(
            country_affiliations_file_path=inst_paths_list[0])
        aff_type_dict = bp.read_inst_types(inst_types_file_path=inst_paths_list[1],
                                           inst_types_usecols=None)
        towns_dict = bp.read_towns_per_country(country_towns_file=inst_country_towns_file,
                                               country_towns_folder_path=inst_paths_list[2])
        norm_dicts = [norm_raw_aff_dict, aff_type_dict, towns_dict]

        # Correcting the authors-institutions parsing data using the user's correction of the addresses
        authsinst_correct_dfs = [auth_inst_df, corrected_addresses_df]
        _ = _correct_dedup_authsinst(authsinst_correct_dfs, dedup_cols_dic, parsing_authsinst_path,
                                     norm_dicts, corpus_year)
        correct_status = True
        print("\n    Cleaning file of addresses to correct by the user")
        message = initialize_addresses_to_correct_file(addresses_to_correct_path, corpus_year, file_clean=True)
        print(message)
    return addresses_to_correct_path, correct_status
