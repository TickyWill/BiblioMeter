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
import bmfuncts.pub_globals as pg
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import concat_dfs


def _my_hash(text:str):
    """Builts hash given the string 'text' 
    with a fixed prime numbers to mix up the bits."""

    my_hash = 0
    facts = (257,961) # prime numbers to mix up the bits
    minus_one = 0xFFFFFFFF # "-1" hex code
    for ch in text:
        my_hash = (my_hash*facts[0] ^ ord(ch)*facts[1]) & minus_one
    return my_hash


def _clean_hash_id_df(dfs_tup, cols_tup):
    """Cleans data from publications with same hash ID."""
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
    return new_submit_df, new_orphan_df, new_hash_id_df


def create_hash_id(institute, org_tup, working_folder_path, file_names_tup):
    """Creates a dataframe which columns are given by 'hash_id_col_alias' and 'pub_id_alias'.

    The containt of these columns is as follows:

    - The 'hash_id_col_alias' column contains the unique hash ID built for each publication \
    through the `_my_hash` internal function on the basis of the values of 'year_alias', \
    'first_auth_alias', 'title_alias', 'issn_alias' and 'doi_alias' columns.
    - The 'pub_id_alias' column contains the publication order number in the publications list.

    Finally, the data are cleaned from the publications that have same hash ID through \
    the `_clean_hash_id_df` internal function and the dataframes are saved as Excel files.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        working_folder_path (path): Full path to working folder.
        submit_file_name (str): File name of the Excel file of the publications list \
        with one row per Institute author with one row per author \
        that has been identified as Institute employee.
        orphan_file_name (str): File name of the Excel file of the publications list \
        with one row per author that has not been identified as Institute employee.
    Returns:
        (str): End message recalling path to the saved file.        
    """
    # Setting parameters from args
    submit_file_name, orphan_file_name = file_names_tup

    # Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    submit_col_rename_dic = col_rename_tup[1]

    # Setting useful aliases
    hash_id_file_alias = pg.ARCHI_YEAR["hash_id file name"]
    hash_id_col_alias = pg.COL_HASH['hash_id']
    pub_id_alias = submit_col_rename_dic[bp.COL_NAMES["pub_id"]]
    year_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][2]]
    first_auth_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][1]]
    doi_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][6]]
    title_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][9]]
    issn_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][10]]

    # Setting useful paths
    submit_file_path = working_folder_path / Path(submit_file_name)
    orphan_file_path = working_folder_path / Path(orphan_file_name)
    hash_id_file_path = working_folder_path / Path(hash_id_file_alias)

    # Setting useful columns list
    useful_cols = [pub_id_alias, year_alias, first_auth_alias,
                   title_alias, issn_alias, doi_alias]

    # Getting dataframes to hash
    submit_df = pd.read_excel(submit_file_path)
    orphan_df = pd.read_excel(orphan_file_path)

    # Concatenate de dataframes to hash
    submit_to_hash = submit_df[useful_cols].copy()
    orphan_to_hash = orphan_df[useful_cols].copy()
    dg_to_hash = concat_dfs([submit_to_hash, orphan_to_hash],
                            dedup_cols=[pub_id_alias], drop_ignore_index=True)

    hash_id_df = pd.DataFrame()
    for idx in range(len(dg_to_hash)):
        pub_id = dg_to_hash.loc[idx, pub_id_alias]
        text   = (f"{str(dg_to_hash.loc[idx, year_alias])}"
                  f"{str(dg_to_hash.loc[idx, first_auth_alias])}"
                  f"{str(dg_to_hash.loc[idx, title_alias])}"
                  f"{str(dg_to_hash.loc[idx, issn_alias])}"
                  f"{str(dg_to_hash.loc[idx, doi_alias])}")
        hash_id = _my_hash(text)
        hash_id_df.loc[idx, hash_id_col_alias] = str(hash_id)
        hash_id_df.loc[idx, pub_id_alias] = pub_id

    # Cleaning dataframe from publications with same hash ID
    dfs_tup = (submit_df, orphan_df, hash_id_df)
    cols_tup = (pub_id_alias, hash_id_col_alias)
    new_submit_df, new_orphan_df, new_hash_id_df = _clean_hash_id_df(dfs_tup, cols_tup)

    # Saving the data
    new_submit_df.to_excel(submit_file_path, index=False)
    new_orphan_df.to_excel(orphan_file_path, index=False)
    new_hash_id_df.to_excel(hash_id_file_path, index=False)
    hash_id_nb = len(new_hash_id_df)
    print(f"{hash_id_nb} hash IDs of publications created")
    message = f"{hash_id_nb} hash IDs of publications created and saved in file: \n  {hash_id_file_path}"
    return message
