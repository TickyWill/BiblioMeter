"""Module of functions for correcting parsing data
for instence in the case of unknown countries.
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
from bmfuncts.config_utils import set_parse_inst_params
from bmfuncts.format_files import format_page
from bmfuncts.useful_functs import build_list_from_str
from bmfuncts.useful_functs import build_string_from_list
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import drop_multiple_item


def _set_parse_cols_dic():
    """Builds a dict setting selected columns names for the process 
    of getting list of unknown countries per address and per publication.

    Returns:
        (dict): The built dict.
    """
    parse_cols_dic = {'bp_pub_id_col'    : bp.COL_NAMES['pub_id'],
                      'bp_address_id_col': bp.COL_NAMES['address'][1],
                      'bp_address_col'   : bp.COL_NAMES['address'][2],
                      'bp_country_col'   : bp.COL_NAMES['country'][2],
                      'bp_author_id_col' : bp.COL_NAMES['auth_inst'][1],
                      'bp_norm_inst_col' : bp.COL_NAMES['auth_inst'][4],
                      'bp_raw_inst_col'  : bp.COL_NAMES['auth_inst'][5],
                      'author_ids_col'   : 'Author IDs',
                     }
    return parse_cols_dic


def _set_correct_parsing_paths(parsing_path, item_filename_dict="", test_txt=""):
    # Internal functions
    def _set_parsing_item_path(item):
        parsing_item_file = test_txt + item_filename_dict[item] + parsing_extent
        parsing_item_path = parsing_path / Path(parsing_item_file)
        return parsing_item_path

    # Setting useful aliases
    parsing_extent = "." + bm_pg.TSV_SAVE_EXTENT
    unknown_country_file_alias = bm_pg.ARCHI_YEAR["unknown_country_file"]
    
    paths_list = []
    unknown_countries_path = parsing_path / Path(unknown_country_file_alias)
    paths_list.append(unknown_countries_path)
    if item_filename_dict:
        for item in ['countries', 'addresses', 'authors_institutions']:
            paths_list.append(_set_parsing_item_path(item))
    return paths_list


def _remove_unknown_country(input_addr_str, sep_str, unknown_country):
    """Removes unknown-country key from an address.

    The unknown-country key is potentially added when  
    the address is stadardized. 
    The split of the address and the join of the items uses  
    the specified separator.

    Args:
        input_addr_str (str): The list of string items to be joined.
        sep_str (str): The separator to be used for the split and join \
        including space if required.
        unknown_country (str): Key word for unknown countries.
    Returns:
        (str): The built final address.
    """
    output_addr_list = build_list_from_str(input_addr_str, sep_str)
    while output_addr_list[-1]==unknown_country:
        output_addr_list = output_addr_list[:-1]
    output_addr_str = build_string_from_list(output_addr_list, sep_str)
    return output_addr_str


def build_and_save_unknown_country_data(parsing_dict, parsing_path, unknown_country,
                                        database_type, corpus_year):
    """Builds data of unknown countries in authors addresses and saves these data 
    as an Openpyxl workbook for correction by the user.

    Args:
        parsing_dict (dict): Parsing results keyed by parsing items \
        given by 'PARSING_ITEMS_LIST' global imported from the package \
        imported as bp and valued by the data (dataframes) of parsing results.
        parsing_path (path): Full path to the folder of the parsing results.
        unknown_country (str): Key word for unknown countries.
        database_type (str): Database name (ex: 'wos' or 'scopus').
        corpus_year (str): Corpus year defined by 4 digits.
    Returns:
        (bool): True if no unknown country is found.
    """
    # Setting useful paths for the process of the unknown-countries correction 
    correct_paths_list = _set_correct_parsing_paths(parsing_path)
    unknown_countries_path = correct_paths_list[0]

    # Setting parsing data to be corrected
    addresses_df = parsing_dict['addresses']
    countries_df = parsing_dict['countries']
    auth_inst_df = parsing_dict['authors_institutions']

    # Setting useful column names    
    parse_cols_dic = _set_parse_cols_dic()
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_address_col',
                 'bp_country_col', 'bp_author_id_col', 'author_ids_col',
                ]   
    (pub_id_col, address_id_col, address_col, country_col,
     author_id_col, author_ids_col) = [parse_cols_dic[key] for key in cols_keys]

    unknown_countries_cols = [pub_id_col, address_id_col, address_col,
                              country_col, author_ids_col]
    data = []
    for pub_id, pub_id_df in countries_df.groupby(pub_id_col):
        countries = pub_id_df[country_col].to_list()
        if unknown_country in countries:
            pub_id_auth_inst_df = auth_inst_df[auth_inst_df[pub_id_col]==pub_id]
            pub_id_addresses_df = addresses_df[addresses_df[pub_id_col]==pub_id]
            unknown_country_df = pub_id_df[pub_id_df[country_col]==unknown_country]
            false_address_ids_list = unknown_country_df[address_id_col].to_list()
            for false_address_id in false_address_ids_list:
                # setting the false address with stadardization and remove of unknown country
                address_id_df = pub_id_addresses_df[pub_id_addresses_df[address_id_col]==false_address_id]
                raw_false_address = address_id_df[address_col].to_list()[0]
                std_false_address = bp.standardize_address(raw_false_address)
                false_address = _remove_unknown_country(std_false_address, ", ", unknown_country)

                # Building the IDs list of authors that have the false address in their affiliations list
                false_address_auth_ids_list = []
                for _, row in pub_id_auth_inst_df.iterrows():
                    author_id = row[author_id_col]

                    # Building the author's addresses list (standardized and unknown countryremoved)
                    author_addresses_str = row[address_col]
                    author_addresses_list = build_list_from_str(author_addresses_str, "; ")
                    author_addresses_list = [bp.standardize_address(x) for x in author_addresses_list]
                    author_addresses_list = [_remove_unknown_country(x, ", ", unknown_country)
                                             for x in author_addresses_list]

                    # Searching for false address in the author's adresses list to append author's ID
                    if false_address in author_addresses_list:
                        false_address_auth_ids_list.append(str(author_id))

                # Building a string from the built IDs list of authors
                false_address_auth_ids = build_string_from_list(false_address_auth_ids_list, "; ")

                data.append([pub_id, false_address_id, false_address, unknown_country, false_address_auth_ids])
    unkown_countries_df = pd.DataFrame(data, columns=unknown_countries_cols)
    unkown_countries_empty = unkown_countries_df.empty

    # Saving false-addresses data
    df_title = bm_pg.DF_TITLES_LIST[19]
    wb, ws = format_page(unkown_countries_df, df_title) 
    ws.title = database_type + " " + corpus_year
    wb.save(unknown_countries_path)

    message = ("\nData for correction of unknown countries in addresses saved in the file:"
               f"\n{unknown_countries_path}")
    print(message)
    return unkown_countries_empty


def _correct_parsing_countries(countries_correct_dfs, parse_cols_dic, parsing_countries_path):
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
    # Setting useful col names from 'parse_cols_dic' arg
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_country_col']   
    pub_id_col, address_id_col, country_col = [parse_cols_dic[key] for key in cols_keys]

    # Setting data to correct from 'countries_correct_dfs' arg
    countries_df, correct_countries_df = countries_correct_dfs
    correct_pub_ids_list = correct_countries_df[pub_id_col].to_list()
    
    new_countries_df = pd.DataFrame(columns=countries_df.columns)
    for pub_id, pub_id_df in countries_df.groupby(pub_id_col):
        pub_id_countries_df = pub_id_df.copy()
        if pub_id in correct_pub_ids_list:
            pub_id_correct_countries_df = correct_countries_df[correct_countries_df[pub_id_col]==pub_id]
            pub_id_correct_address_ids_list = pub_id_correct_countries_df[address_id_col].to_list()
            pub_id_correct_countries_list = pub_id_correct_countries_df[country_col].to_list()
            pub_id_correct_countries_dict = dict(zip(pub_id_correct_address_ids_list,
                                              pub_id_correct_countries_list))
            for correct_address_id in pub_id_correct_address_ids_list:
                for num_row, row in pub_id_countries_df.iterrows():
                    false_address_id = row[address_id_col]
                    if correct_address_id==false_address_id:
                        correct_country = pub_id_correct_countries_dict[correct_address_id]
                        pub_id_countries_df.loc[num_row, country_col] = correct_country
        new_countries_df = concat_dfs([new_countries_df, pub_id_countries_df])
    new_countries_df.to_csv(parsing_countries_path, index=False, sep='\t')
    message = ("\nCorrected parsing countries saved in the file:"
               f"\n{parsing_countries_path}")
    return message


def _correct_parsing_addresses(addresses_correct_dfs, parse_cols_dic, parsing_addresses_path):
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
    # Setting useful col names from 'parse_cols_dic' arg
    cols_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_address_col',
                 'bp_country_col']   
    (pub_id_col, address_id_col, address_col,
     country_col) = [parse_cols_dic[key] for key in cols_keys]

    # Setting data for parsing correction from 'addresses_correct_dfs' arg
    addresses_df, correct_countries_df = addresses_correct_dfs
    correct_pub_ids_list = correct_countries_df[pub_id_col].to_list()

    new_addresses_df = pd.DataFrame(columns=addresses_df.columns)
    for pub_id, pub_id_df in addresses_df.groupby(pub_id_col):
        pub_id_addresses_df = pub_id_df.copy()
        pub_id_addresses_df[address_col] = pub_id_addresses_df[address_col].apply(bp.standardize_address)
        if pub_id in correct_pub_ids_list:
            pub_id_correct_countries_df = correct_countries_df[correct_countries_df[pub_id_col]==pub_id]
            pub_id_correct_address_ids_list = pub_id_correct_countries_df[address_id_col].to_list()
            pub_id_correct_addresses_list = pub_id_correct_countries_df[address_col].to_list()
            pub_id_correct_countries_list = pub_id_correct_countries_df[country_col].to_list()
            pub_id_correct_addresses_dict = dict(zip(pub_id_correct_address_ids_list,
                                              pub_id_correct_addresses_list))
            pub_id_correct_countries_dict = dict(zip(pub_id_correct_address_ids_list,
                                              pub_id_correct_countries_list))
            for correct_address_id in pub_id_correct_address_ids_list:
                for num_row, row in pub_id_addresses_df.iterrows():
                    false_address_id = row[address_id_col]
                    if correct_address_id==false_address_id:
                        init_address = pub_id_correct_addresses_dict[correct_address_id]
                        correct_country = pub_id_correct_countries_dict[correct_address_id]
                        correct_address = init_address + ", " + correct_country
                        pub_id_addresses_df.loc[num_row, address_col] = correct_address
        new_addresses_df = concat_dfs([new_addresses_df, pub_id_addresses_df])
    new_addresses_df.to_csv(parsing_addresses_path, index=False, sep='\t')
    message = ("\nCorrected parsing addresses saved in the file:"
               f"\n{parsing_addresses_path}")
    return message 


def _correct_parsing_authsinst(authsinst_correct_dfs, parse_cols_dic,
                               parsing_authsinst_path, norm_dicts, unknown_country):
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
        unknown_country (str): Key word for unknown countries.
    Returns:
        (str): Final message.
    """
    # Setting useful col names from 'parse_cols_dic' arg
    cols_keys = ['bp_pub_id_col', 'bp_address_col', 'bp_country_col', 'bp_author_id_col',
                 'author_ids_col', 'bp_norm_inst_col', 'bp_raw_inst_col']   
    (pub_id_col, address_col, country_col, author_id_col, author_ids_col,
     norm_inst_col, raw_inst_col) = [parse_cols_dic[key] for key in cols_keys]

    # Setting data for affiliations normalization from 'norm_dicts' arg
    norm_raw_aff_dict, aff_type_dict, towns_dict = norm_dicts

    # Setting data for parsing correction from 'authsinst_correct_dfs' arg
    auth_inst_df, correct_countries_df = authsinst_correct_dfs
    correct_pub_ids_list = correct_countries_df[pub_id_col].to_list()

    new_auth_inst_df = pd.DataFrame(columns=auth_inst_df.columns)
    for pub_id, pub_id_df in auth_inst_df.groupby(pub_id_col):
        pub_id_auths_inst_df = pub_id_df.copy()
        if pub_id in correct_pub_ids_list:
            pub_id_correct_countries_df = correct_countries_df[correct_countries_df[pub_id_col]==pub_id]
            for _, pub_id_correct_countries_row in pub_id_correct_countries_df.iterrows():
                false_address = pub_id_correct_countries_row[address_col]
                correct_country = pub_id_correct_countries_row[country_col]
                correct_address = false_address + ", " + correct_country
                auth_ids_str = str(pub_id_correct_countries_row[author_ids_col])
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
    new_auth_inst_df.to_csv(parsing_authsinst_path, index=False, sep='\t')
    message = ("\nCorrected parsing authors-institutions saved in the file:"
               f"\n{parsing_authsinst_path}")
    return message


def set_parse_inst_params(institute, wf_path):
    """Sets files paths to institutions data.

    Args:
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
    Returns:
        (tup): (full path to institute-affiliations file, \
        full path to institutions-types file).
    """
    # Setting useful aliases
    institutions_folder_alias = bm_pg.ARCHI_INSTITUTIONS["root"]
    inst_aff_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["institute_affil_base"]
    inst_types_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["inst_types_base"]
    country_towns_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["country_towns_base"]

    # Setting useful file names and paths for Institute affiliations
    inst_country_towns_file = institute + "_" + country_towns_file_base_alias
    institute_affil_file = institute + "_" + inst_aff_file_base_alias
    inst_types_file = institute + "_" + inst_types_file_base_alias
    institutions_folder_path = wf_path / Path(institutions_folder_alias)
    institute_affil_file_path = institutions_folder_path / Path(institute_affil_file)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file)

    # Setting return tup
    inst_paths_list = [institute_affil_file_path, inst_types_file_path,
                       institutions_folder_path]
    return inst_country_towns_file, inst_paths_list


def correct_parsing(institute, wf_path, parsing_path, parsing_dict,
                    item_filename_dict, unknown_country, test_txt=""):
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
        unknown_country (str): Key word for unknown countries.
        test_txt (str): For optional modification of the file names \
        for saving the corrected parsing data during code test (default="").
    Returns:
        (bool): True if the parsing data have been corrected.
    """
    # Setting useful paths to files for parsing data correction
    correct_paths_list = _set_correct_parsing_paths(parsing_path, item_filename_dict, test_txt)
    (correct_countries_path, parsing_countries_path,
     parsing_addresses_path, parsing_authsinst_path) = correct_paths_list

    # Getting data of the user's correction of the unknown countries
    correct_countries_df = pd.read_excel(correct_countries_path)
    correct_status = False
    if not correct_countries_df.empty:
        # If data of the user's correction of the unknown countries not empty,
        # proceeding with parsing data correction

        # Getting parsing data to be corrected
        addresses_df = parsing_dict['addresses']
        countries_df = parsing_dict['countries']
        auth_inst_df = parsing_dict['authors_institutions']

        # Setting useful column names
        parse_cols_dic = _set_parse_cols_dic()

        # Correcting the countries parsing data using the user's correction of the unknown countries
        countries_correct_dfs = [countries_df, correct_countries_df]
        _ = _correct_parsing_countries(countries_correct_dfs, parse_cols_dic, parsing_countries_path)

        # Correcting the addresses parsing data using the user's correction of the unknown countries
        addresses_correct_dfs = [addresses_df, correct_countries_df]
        _ = _correct_parsing_addresses(addresses_correct_dfs, parse_cols_dic, parsing_addresses_path)

        # Getting intitutions normalization data for correction authors-institutions parsing data
        inst_country_towns_file, inst_paths_list = set_parse_inst_params(institute, wf_path)
        norm_raw_aff_dict = bp.build_norm_raw_affiliations_dict(
            country_affiliations_file_path=inst_paths_list[0])
        aff_type_dict = bp.read_inst_types(inst_types_file_path=inst_paths_list[1],
                                           inst_types_usecols=None)
        towns_dict = bp.read_towns_per_country(country_towns_file=inst_country_towns_file,
                                               country_towns_folder_path=inst_paths_list[2])
        norm_dicts = [norm_raw_aff_dict, aff_type_dict, towns_dict]

        # Correcting the authors-institutions parsing data using the user's correction of the unknown countries
        authsinst_correct_dfs = [auth_inst_df, correct_countries_df]
        _ = _correct_parsing_authsinst(authsinst_correct_dfs, parse_cols_dic, parsing_authsinst_path,
                                       norm_dicts, unknown_country)
        correct_status = True
        empty_addresses_df = pd.DataFrame(columns=correct_countries_df.columns)
        empty_addresses_df.to_excel(correct_countries_path, index=False)
    return correct_status
