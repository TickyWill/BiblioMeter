"""Module of functions for creating an ID for each publication 
that is independent of the extraction from the external databases.

"""

__all__ = ['create_hash_id']


# Standard Library imports
from pathlib import Path

# 3rd party imports
import pandas as pd
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import reorder_df


def _my_hash(text:str):
    """Builds hash given the string 'text' 
    with a fixed prime numbers to mix up the bits.

    Args:
        text (str): The text for which the Hash ID is built.
    Returns:
        (int): The built Hash ID.
    """
    my_hash = 0
    facts = (257,961) # prime numbers to mix up the bits
    minus_one = 0xFFFFFFFF # "-1" hex code
    for ch in text:
        my_hash = (my_hash*facts[0] ^ ord(ch)*facts[1]) & minus_one
    return my_hash


def _clean_hash_id_df(dfs_tup, cols_tup):
    """Cleans data from publications with same hash ID.

    Args:
        dfs_tup (tup): 3 dataframes = (data of publications list with one row \
        per institute author and attributes as employee, data \
        of publications list with one row per author not found \
        in the employees database, data of Hash IDs with related publication IDs).
        cols_tup (tup): The name of useful columns.
    Returns:
        (tup): 3 dataframes = (The cleaned data of publications list with one row \
        per institute author and attributes as employee, \
        The cleaned data of publications list with one row per author not found \
        in the employees database, The cleaned data of Hash IDs with related publication IDs).
    """
    # Setting parameters from args
    submit_df, orphan_df, hash_id_df = dfs_tup
    pub_id_col, hash_id_col = cols_tup

    # Setting publications IDs list
    submit_pub_id_list = list(submit_df[pub_id_col])
    orphan_pub_id_list = list(orphan_df[pub_id_col])

    new_hash_id_df = pd.DataFrame()
    new_submit_df = submit_df.copy()
    new_orphan_df = orphan_df.copy()
    for _, hash_id_dg in hash_id_df.groupby(hash_id_col):
        add_hash_id_dg = hash_id_dg.copy()
        if len(hash_id_dg)>1:
            pub_id_list = list(hash_id_dg[pub_id_col])
            pub_id_to_keep = pub_id_list[0]
            pub_id_to_drop_list = pub_id_list[1:]
            for pub_id_to_drop in pub_id_to_drop_list:
                if pub_id_to_drop in submit_pub_id_list:
                    new_submit_df = new_submit_df[new_submit_df[pub_id_col]!=pub_id_to_drop]
                if pub_id_to_drop in orphan_pub_id_list:
                    new_orphan_df = new_orphan_df[new_orphan_df[pub_id_col]!=pub_id_to_drop]
            add_hash_id_dg = hash_id_dg[hash_id_dg[pub_id_col]==pub_id_to_keep].copy()
        new_hash_id_df = concat_dfs([new_hash_id_df, add_hash_id_dg])

    # Adding column of Hash-IDs and reordering columns in new_submit_df
    new_submit_df = new_submit_df.merge(new_hash_id_df,
                                        how="inner",
                                        on=pub_id_col)
    col_dict = {hash_id_col: 0}
    new_submit_df = reorder_df(new_submit_df, col_dict)

    # Adding column of Hash-IDs and reordering columns in new_orphan_df
    new_orphan_df = new_orphan_df.merge(new_hash_id_df,
                                        how="inner",
                                        on=pub_id_col)
    col_dict = {hash_id_col: 0,
                pub_id_col : 1}
    new_orphan_df = reorder_df(new_orphan_df, col_dict)

    return new_submit_df, new_orphan_df, new_hash_id_df


def create_hash_id(institute, org_tup, files_paths):
    """Creates a dataframe which columns are given by 'hash_id_alias' and 'pub_id_alias'.

    The content of these columns is as follows:

    - The 'hash_id_alias' column contains the unique hash ID built for each publication \
    through the `_my_hash` internal function on the basis of the values of 'year_alias', \
    'first_auth_alias', 'title_alias', 'issn_alias' and 'doi_alias' columns.
    - The 'pub_id_alias' column contains the publication order number in the publications list.

    Finally, the data are cleaned from the publications that have same hash ID through \
    the `_clean_hash_id_df` internal function and the dataframes are saved as Excel files.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        files_paths (list): Full paths (path) to (1) the publications list \
        with one row per Institute authorthat has been identified \
        as Institute employee, (2) the publications list with one row per author that has not \
        been identified as Institute employee and (3) for saving the created Hash-IDs data.
    Returns:
        (str): End message recalling path to the saved file.        
    """
    # Setting paths from args
    submit_path, orphan_path, hash_id_path = files_paths

    # Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    submit_col_rename_dic = col_rename_tup[1]
    pub_id_col = submit_col_rename_dic[bp.COL_NAMES["pub_id"]]
    year_col = submit_col_rename_dic[bp.COL_NAMES['articles'][2]]
    first_auth_col = submit_col_rename_dic[bp.COL_NAMES['articles'][1]]
    doi_col = submit_col_rename_dic[bp.COL_NAMES['articles'][6]]
    title_col = submit_col_rename_dic[bp.COL_NAMES['articles'][9]]
    issn_col = submit_col_rename_dic[bp.COL_NAMES['articles'][10]]

    # Setting useful aliases    
    hash_id_alias = bm_pg.COL_HASH['hash_id']

    # Setting useful columns list
    useful_cols = [pub_id_col, year_col, first_auth_col,
                   title_col, issn_col, doi_col]

    # Getting dataframes to hash
    submit_df = pd.read_excel(submit_path)
    orphan_df = pd.read_excel(orphan_path)

    # Concatenate de dataframes to hash
    submit_to_hash = submit_df[useful_cols].copy()
    orphan_to_hash = orphan_df[useful_cols].copy()
    dg_to_hash = concat_dfs([submit_to_hash, orphan_to_hash],
                            dedup_cols=[pub_id_col], drop_ignore_index=True)

    hash_id_df = pd.DataFrame()
    for idx in range(len(dg_to_hash)):
        pub_id = dg_to_hash.loc[idx, pub_id_col]
        text   = (f"{str(dg_to_hash.loc[idx, year_col])}"
                  f"{str(dg_to_hash.loc[idx, first_auth_col])}"
                  f"{str(dg_to_hash.loc[idx, title_col])}"
                  f"{str(dg_to_hash.loc[idx, issn_col])}"
                  f"{str(dg_to_hash.loc[idx, doi_col])}")
        hash_id = _my_hash(text)
        hash_id_df.loc[idx, hash_id_alias] = str(hash_id)
        hash_id_df.loc[idx, pub_id_col] = pub_id

    # Cleaning dataframe from publications with same hash ID
    dfs_tup = (submit_df, orphan_df, hash_id_df)
    cols_tup = (pub_id_col, hash_id_alias)
    new_submit_df, new_orphan_df, new_hash_id_df = _clean_hash_id_df(dfs_tup, cols_tup)

    # Saving the data
    new_submit_df.to_excel(submit_path, index=False)
    new_orphan_df.to_excel(orphan_path, index=False)
    new_hash_id_df.to_excel(hash_id_path, index=False)
    hash_id_nb = len(new_hash_id_df)
    print(f"{hash_id_nb} hash IDs of publications created")
    message = (f"{hash_id_nb} hash IDs of publications created and saved in file: ",
               f"\n  {hash_id_path}")
    return message
