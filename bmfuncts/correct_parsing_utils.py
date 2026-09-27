"""Module of useful functions shared for correcting parsing and deduplication data 
using corrected addresses by the user.
"""

__all__ = ['build_pub_correct_authaddr_data',
          ]


# 3rd party imports
from bpfuncts import standardize_address as bp_standardize_address
from bpfuncts import build_addr_affils_tup as bp_build_addr_affils_tup

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.useful_functs import build_list_from_str
from bmfuncts.useful_functs import build_string_from_list
from bmfuncts.useful_functs import drop_multiple_item


def _correct_auth_addresses(authaddr_row, address_col, false_address, correct_address,
                            unknown_country):
    raw_author_addresses_str = str(authaddr_row[address_col])
    raw_author_addresses_list = build_list_from_str(raw_author_addresses_str, "; ")
    author_addresses_list = []
    for address in raw_author_addresses_list:
        std_address_str = bp_standardize_address(address, add_unknown_country=False)
        if unknown_country:
            std_address_str = _remove_unknown_country(std_address_str, ", ", unknown_country)
        author_addresses_list.append(std_address_str)

    # Finding index of false address in 'author_addresses_list'
    if false_address in author_addresses_list:
        false_addr_idx = author_addresses_list.index(false_address)
        author_addresses_list[false_addr_idx] = correct_address
    author_addresses_str = build_string_from_list(author_addresses_list, "; ")
    return author_addresses_list, author_addresses_str


def _correct_auth_norm_raw_affils(author_addresses_list, affil_params_dic):
    # Correcting normalized affiliations
    full_norm_affils_list, full_raw_affils_list = [], []
    for auth_address in author_addresses_list:
        author_addr_aff_tup = bp_build_addr_affils_tup(auth_address, affil_params_dic,
                                                       drop_status=False)
        auth_addr_norm_affils_list = author_addr_aff_tup.norm_affils_list
        full_norm_affils_list.append(auth_addr_norm_affils_list)
        auth_addr_raw_affils_list = author_addr_aff_tup.raw_affils_list
        full_raw_affils_list.append(auth_addr_raw_affils_list)

    norm_affils_list = drop_multiple_item(full_norm_affils_list, bm_pg.EMPTY)
    norm_affils_str = build_string_from_list(norm_affils_list, ";")
    raw_affils_list = drop_multiple_item(full_raw_affils_list, bm_pg.EMPTY)
    raw_affils_str = build_string_from_list(raw_affils_list, ";")
    return norm_affils_str, raw_affils_str


def _correct_auth_pub_id_authaddr(authaddr_row, address_col, false_address, correct_address,
                                  affil_params_dic, unknown_country):
    # Correcting author's addresses
    return_tup = _correct_auth_addresses(authaddr_row, address_col, false_address,
                                         correct_address, unknown_country)
    author_addresses_list, author_addresses_str = return_tup

    # Correcting normalized affiliations of author
    norm_affils_str, raw_affils_str = _correct_auth_norm_raw_affils(author_addresses_list,
                                                                    affil_params_dic)
    return author_addresses_str, norm_affils_str, raw_affils_str


def build_pub_correct_authaddr_data(pub_id_dfs, cols_list, affil_params_dic, unknown_country=None):
    """Builds the correct author-with-addresses data for a given publication.
    """
    # Setting column names from args
    (country_col, address_col, correct_address_col, author_id_col, author_ids_col,
     norm_affils_col, raw_affils_col) = cols_list

    # Setting input-data from args
    pub_id_addr_correction_df, pub_id_authaddr_df = pub_id_dfs

    for _, correct_address_row in pub_id_addr_correction_df.iterrows():
        # Setting values for correction of authors-with-addresses data
        correct_country = correct_address_row[country_col]
        false_address = correct_address_row[address_col]
        correct_address = correct_address_row[correct_address_col]
        auth_ids_str = str(correct_address_row[author_ids_col])
        auth_ids_list = build_list_from_str(auth_ids_str, "; ")
        auth_ids_list = [int(x) for x in auth_ids_list]

        for row_num, authaddr_row in pub_id_authaddr_df.iterrows():
            author_id = int(authaddr_row[author_id_col])
            if author_id in auth_ids_list:
                # Building the correct author-with-addresses data for the author
                return_tup = _correct_auth_pub_id_authaddr(authaddr_row, address_col, false_address,
                                                           correct_address, affil_params_dic, unknown_country)
                author_addresses_str, norm_affils_str, raw_affils_str = return_tup

                # Updating author-with-addresses data of the author with corrected data
                pub_id_authaddr_df.loc[row_num, address_col] = author_addresses_str
                pub_id_authaddr_df.loc[row_num, country_col] = correct_country
                pub_id_authaddr_df.loc[row_num, norm_affils_col] = norm_affils_str
                pub_id_authaddr_df.loc[row_num, raw_affils_col] = raw_affils_str
    return pub_id_authaddr_df
