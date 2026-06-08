"""Module of functions for cleaning authors' addresses of Institute's publications.
"""

__all__ = ['build_institute_addresses_df']

# Standard Library imports
from pathlib import Path

# 3rd party imports
import pandas as pd
from bpfuncts import standardize_address as bp_standardize_address

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.read_final_results import keep_only_final_pub_data
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.read_final_results import read_final_submit_data
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import save_xlsx_file
from bmfuncts.useful_functs import set_year_pub_id


def _set_pub_addresses_cols_dic(institute, org_tup):
    """Builds a dict setting selected columns names for the process 
    of building addresses data per publication.

    This is done through the `build_col_conversion_dic` function imported from the 
    `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains parameters of Institute organization.
    Returns:
        (dict): The built dict.
    """
    _, submit_col_rename_dic, _ = build_col_conversion_dic(institute, org_tup)

    pub_addresses_cols_dic = {'bp_pub_id_col'    : bm_pg.COL_NAMES['address'][0],
                              'bp_address_id_col': bm_pg.COL_NAMES['address'][1],
                              'bp_address_col'   : bm_pg.COL_NAMES['address'][2],
                              'bp_author_id_col' : bm_pg.COL_NAMES['auth_inst'][1],
                              'bm_pub_id_col'    : submit_col_rename_dic[bm_pg.COL_NAMES['authors'][0]],
                              'bm_address_id_col': bm_pg.COL_NAMES_BONUS['address ID'],
                              'bm_address_col'   : submit_col_rename_dic[bm_pg.COL_NAMES['address'][2]],
                              'bm_author_id_col' : submit_col_rename_dic[bm_pg.COL_NAMES['authors'][1]],
                              'bm_doctype_col'   : submit_col_rename_dic[bm_pg.COL_NAMES['articles'][7]],
                             }

    return pub_addresses_cols_dic


def _set_col_lists_infos(pub_addresses_cols_dic):
    """Builds a dict giving useful col lists and a dict for renaming col names.

    The col names set at the parsing step are renamed with the col names
    set within the step of the consolidation of the publications list.

    Args:
        pub_addresses_cols_dic (dict): The dict giving selected columns names \
        as built through the `_set_pub_addresses_cols_dic` internal function.
    Returns:
        (tuple): (The dict giving the final col list and the full col list, \
        The dict for renaming the columns).
    """
    col_keys = ['bp_pub_id_col', 'bp_address_id_col', 'bp_address_col']
    bp_init_cols_list = [pub_addresses_cols_dic[key] for key in col_keys]

    col_keys = ['bm_pub_id_col', 'bm_address_id_col', 'bm_address_col']
    bm_final_cols_list = [pub_addresses_cols_dic[key] for key in col_keys]

    col_keys = ['bm_pub_id_col', 'bm_address_id_col', 'bm_author_id_col', 'bm_address_col']
    bm_full_cols_list = [pub_addresses_cols_dic[key] for key in col_keys]

    col_lists_dic = {'bm_final_cols_list': bm_final_cols_list,
                     'bm_full_cols_list' : bm_full_cols_list,
                    }

    bp2bm_rename_cols_dict = dict(zip(bp_init_cols_list, bm_final_cols_list))
    return col_lists_dic, bp2bm_rename_cols_dict


def _set_steps_save_params_dic():
    """Sets dict giving the file name base for saving
    intermediate results.

    The dict is keyed by the step index and valued name (str) of the data
    to be saved.

    Returns:
        (dict): the built dict.
    """
    steps_save_params_dic = {1: 'institute_pub_addresses_init_df',
                             2: 'institute_author_addresses_df',
                             3: 'pubid_addid_authid_addresse_df',
                             4: 'corr_pubid_addid_authid_addresse_df',
                             5: 'institute_pub_addresses_df',
                            }
    return steps_save_params_dic


def _initializing_save_params_dic(wf_path, corpus_year, verbose):
    """Initialize the parameters dict for saving intermediate results.

    At key 'save_num', the value of the index of the already-saved
    results is set to 0.
    At key 'save_folder_path', the full path to the folder where
    intermediate results are saved is defined through
    the `_set_save_folder_path` internal function.
    At key 'steps_save_params_dic', the dict giving useful file information
    for saving intermediate results is set through
    the `_set_steps_save_params_dic` internal function.

    Args:
        wf_path (path): The full path to the working folder.
        corpus_year (str): The 4 digits year of the corpus.
    Returns:
        (dict): The built dict.
    """
    # Initializing the index of already-saved intermediate results
    save_num = 0
    save_folder_path = ""
    steps_save_params_dic = {}

    if verbose:
        # Setting the folder for saving intermediate results
        save_folder_path = _set_save_folder_path(wf_path, corpus_year)
        # Building the dict giving information for saving intermediate results
        steps_save_params_dic = _set_steps_save_params_dic()

    save_params_dic = {'save_num'             : save_num,
                       'save_folder_path'     : save_folder_path,
                       'steps_save_params_dic': steps_save_params_dic,
                       }
    return save_params_dic


def _save_step_df(save_params_dic, step_df):
    """Saves intermediate results.

    Args:
        save_params_dic (dict): The parameters dict for saving \
        intermediate results and initialized through \
        the `_initializing_save_params_dic` internal function.
        step_df (dataframe): The intermediate results to be saved.
    Returns:
        (int): the incremented index of the already-saved \
        intermediate results.
    """
    # Setting parameters value from 'save_params_dic'
    keys = ['save_num', 'save_folder_path', 'steps_save_params_dic']
    (save_num, save_folder_path,
     steps_save_params_dic) = [save_params_dic[key] for key in keys]

    # Updating step parameters value
    save_num += 1
    save_params_dic['save_num'] = save_num
    step_value = steps_save_params_dic[save_num]
    step_file = f'{str(save_num)}-{step_value}.xlsx'

    if step_df.empty:
        # Printing message
        print(f"    {step_value} empty dataframe\n"
              f"    at step number: {save_params_dic['save_num']}"
              f"    unsaved to    : {step_file} \n")
    else:
        # saving intermediate results
        save_xlsx_file(save_folder_path, step_df, step_file)

        # Printing message
        print(f"    {step_value} \n"
              f"    at step number: {save_params_dic['save_num']}"
              f"    saved to      : {step_file} \n")

    return save_num


def _build_pubid_addid_authid_addresse_df(clean_dfs, bm_full_cols_list):
    """Builds the data of addresses per author ID, per address ID and per 
    publication ID.

    Author_id is set to "_" for authors not affiliated to the institute. 
    The input data are built through the `_build_init_institute_addresses_df` 
    internal function.

    Args:
        clean_dfs (list): Composed of the initial data (dataframe) of addresses \
        per publications of the institute and of the data (dataframe) of addresses \
        per publication and author of the institute.
        bm_full_cols_list (list): All useful column names (str) set within \
        the application.
    Returns:
        (dataframe): The built data.
    """
    # Setting parameters value from 'clean_dfs'
    institute_pub_addresses_init_df, institute_author_addresses_df = clean_dfs

    bm_pub_id_col, bm_address_id_col, bm_author_id_col, bm_address_col = bm_full_cols_list
    pubid_addid_authid_addresse_df = pd.DataFrame(columns=bm_full_cols_list)
    for pub_id, pub_id_df1 in institute_pub_addresses_init_df.groupby(bm_pub_id_col):
        # Setting all addresses list for 'pub_id' in a dict
        df1_address_ids_list = pub_id_df1[bm_address_id_col].to_list()
        df1_addresses_list = pub_id_df1[bm_address_col].to_list()
        df1_address_dict = dict(zip(df1_addresses_list, df1_address_ids_list))

        # Setting institute-authors addresses for 'pub_id'
        pub_id_df2 = institute_author_addresses_df[institute_author_addresses_df[bm_pub_id_col]==pub_id]

        # Setting list of other-authors addresses for 'pub_id'
        df2_addresses_list = pub_id_df2[bm_address_col].to_list()
        df1_out_df2_addresses_list = list(set(df1_addresses_list) - set(df2_addresses_list))

        # Building partial 'pubid_addid_authid_addresse_df' for 'pub_id' as 'pub_id_out_df'
        pub_id_data = []
        others_data = []
        for address in df1_out_df2_addresses_list:
            # Setting data for other authors than authors of the institute
            address_id = df1_address_dict[address]
            author_id = "_"
            others_data.append([pub_id, address_id, author_id, address])
        pub_id_data = pub_id_data + others_data

        for df2_address, df2_addresses_df in pub_id_df2.groupby(bm_address_col):
            # Setting data for authors of the institute
            df2_author_ids_list = df2_addresses_df[bm_author_id_col].to_list()
            df1_address_id = df1_address_dict[df2_address]
            institute_data = []
            for author_id in df2_author_ids_list:
                institute_data.append([pub_id, df1_address_id, author_id, df2_address])
            pub_id_data = pub_id_data + institute_data
        pub_id_out_df = pd.DataFrame(pub_id_data, columns=bm_full_cols_list)
        pub_id_out_df = pub_id_out_df.drop_duplicates()
        pub_id_out_df = pub_id_out_df.sort_values(by=[bm_address_id_col])

        # Updating the full pubid_addid_authid_addresse_df by concatenation with 'pub_id_out_df'
        pubid_addid_authid_addresse_df = concat_dfs([pubid_addid_authid_addresse_df, pub_id_out_df])
    return pubid_addid_authid_addresse_df


def _correct_institute_address(pubid_addid_authid_addresse_df, bm_full_cols_list):
    """Corrects addresses of the authors of LITEN institute by replacing
    'INES' by "CEA, LITEN, INES".

    No correction is performed for the other Institutes.

    Args:
        pubid_addid_authid_addresse_df (dataframe): The data of addresses \
        per author ID, per address ID and per publication ID.
        bm_full_cols_list (list): All useful column names (str) set within \
        the application.
    Returns:
        (dataframe): The corrected data.
    """
    bm_pub_id_col, bm_address_id_col, bm_author_id_col, bm_address_col = bm_full_cols_list
    out_df = pd.DataFrame()
    for pub_id, pub_id_df in pubid_addid_authid_addresse_df.groupby(bm_pub_id_col):
        new_pub_id_df = pd.DataFrame()
        for author_id, author_id_df in pub_id_df.groupby(bm_author_id_col):
            if author_id!="_":
                address_ids_list = author_id_df[bm_address_id_col].to_list()
                addresses_list = author_id_df[bm_address_col].to_list()
                addresses_str = str(addresses_list).lower()
                new_author_id_df = pd.DataFrame()
                if "INES".lower() in addresses_str:
                    ines_rpl_str = "CEA, LITEN, INES"
                    unknown_rpl_str = "France"
                    # Correcting Liten-Institute addresse when "CEA" and "LITEN" are missing
                    # before replacing "INESCEA" by "ines_rpl-str" to avoid replacing "INES" in "ines_rpl-str"
                    new_addresses_list = [address.replace("INES", ines_rpl_str) for address in addresses_list]
                    # Correcting Liten-Institute addresse when affiliation is "INESCEA" and "LITEN" is missing
                    new_addresses_list = [address.replace("INESCEA", ines_rpl_str) for address in addresses_list]
                    new_addresses_list = [address.replace(bm_pg.UNKNOWN, unknown_rpl_str)
                                          for address in new_addresses_list]
                    addresses_dict = dict(zip(new_addresses_list, address_ids_list))
                    data = []
                    for address in new_addresses_list:
                        data.append([pub_id, addresses_dict[address], author_id, address])
                    addresses_df = pd.DataFrame(data, columns=bm_full_cols_list)
                    new_author_id_df = pd.concat([new_author_id_df, addresses_df])
                else:
                    new_author_id_df = author_id_df.copy()
                new_pub_id_df = concat_dfs([new_pub_id_df, new_author_id_df])
            else:
                new_pub_id_df = concat_dfs([new_pub_id_df, author_id_df])
        new_pub_id_df = new_pub_id_df.sort_values(by=[bm_address_id_col])
        out_df = pd.concat([out_df, new_pub_id_df])
    corr_pubid_addid_authid_addresse_df = out_df.copy()
    return corr_pubid_addid_authid_addresse_df


def _build_final_institute_addresses_df(corr_pubid_addid_authid_addresse_df, bm_final_cols_list):
    """Builds the final data of addresses with one row per address 
    and per publication ID corrected for addresses of the institute.

    Args:
        corr_pubid_addid_authid_addresse_df (dataframe): The data of addresses \
        per author ID, per address ID and per publication ID with corrected \
        addresses of the authors of the institute.
        bm_final_cols_list (list): Final column names (str) set within \
        the application.
    Returns:
        (dataframe): The data of addresses with one row per address and per \
        publication ID.
    """
    # Setting col names from 'bm_full_cols_list'
    bm_pub_id_col, bm_address_id_col, bm_address_col = bm_final_cols_list

    # Building the final data
    data_cols = bm_final_cols_list
    in_df = corr_pubid_addid_authid_addresse_df.copy()
    full_data = []
    for pub_id, pub_id_df in in_df.groupby(bm_pub_id_col):
        pub_id_data = []
        for addr_id, addr_id_df in pub_id_df.groupby(bm_address_id_col):
            addresses_list = list(set(addr_id_df[bm_address_col].to_list()))
            address = ", ".join(addresses_list)
            pub_id_data.append([pub_id, addr_id, address])
        full_data = full_data + pub_id_data
    out_df = pd.DataFrame(full_data, columns=data_cols)
    out_df = out_df.drop_duplicates()
    institute_pub_addresses_df = out_df.copy()
    return institute_pub_addresses_df


def _clean_institute_addresses_data(institute, clean_dfs, col_lists_dic,
                                    verbose, save_params_dic, progress_param=None):
    """Cleans the data of addresses per publication ID depending on the institute.

    It uses the `_build_pubid_addid_authid_addresse_df`, `_correct_institute_address` 
    and `_build_final_institute_addresses_df` internal functions to do that. 
    The resulting data may be saved for control through the `save_xlsx_file` 
    function imported from `bmfuncts.useful_functs` and the use of 'verbose' arg.

    Args:
        institute (str): The institute name.
        clean_dfs (list): Composed of the initial data (dataframe) of addresses \
        per publications of the institute and of the data (dataframe) of addresses \
        per publication and author of the institute.
        col_lists_dic (dict): The dict giving the final col list and the full \
        col list as built through the `_set_col_lists_infos` internal function.
        verbose (bool): Status of prints and saving intermediate results.
        save_params_dic (dict): The parameters dict for saving intermediate \
        results and initialized through the `_initializing_save_params_dic` \
        internal function.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    Returns:
        (tup): (The cleaned data, the updated index of the already-saved \
        intermediate results).
    """
    # Setting parameters values from 'bm_full_cols_list'
    bm_full_cols_list = col_lists_dic['bm_full_cols_list']
    bm_final_cols_list = col_lists_dic['bm_final_cols_list']

    # Setting parameters from optional arg
    progress_callback, init_progress, final_progress, progress_step, progress_status = [None] * 5
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_step = (final_progress - init_progress) * 0.30
        progress_status = init_progress
        progress_callback(progress_status)

    if institute.upper()=="LITEN":
        # Building "pubid_addid_authid_addresse_df"
        return_df = _build_pubid_addid_authid_addresse_df(clean_dfs, bm_full_cols_list)
        pubid_addid_authid_addresse_df = return_df
        if progress_param:
            progress_status += progress_step
            progress_callback(progress_status)

        # Building corrected "pubid_addid_authid_addresse_df"
        corr_pubid_addid_authid_addresse_df = _correct_institute_address(pubid_addid_authid_addresse_df,
                                                                         bm_full_cols_list)
        if progress_param:
            progress_status += progress_step
            progress_callback(progress_status)

        # Building final_institute_addresses_df
        institute_pub_addresses_df = _build_final_institute_addresses_df(corr_pubid_addid_authid_addresse_df,
                                                                         bm_final_cols_list)
    else:
        pubid_addid_authid_addresse_df = pd.DataFrame()
        corr_pubid_addid_authid_addresse_df = pd.DataFrame()

        # Setting the cleaned data to the initial Institute's data of addresses per publications
        institute_pub_addresses_df = clean_dfs[0].copy()

    if verbose:
        save_params_dic['save_num'] = _save_step_df(save_params_dic,
                                                    pubid_addid_authid_addresse_df)
        save_params_dic['save_num'] = _save_step_df(save_params_dic,
                                                    corr_pubid_addid_authid_addresse_df)
    if progress_param:
        progress_callback(final_progress)
    return institute_pub_addresses_df, save_params_dic['save_num']


def _set_save_folder_path(wf_path, corpus_year):
    """ Sets the full path to the folder where intermediate results are saved.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (path): The set full path.
    """
    # Setting useful aliases
    analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    affils_analysis_folder_alias = bm_pg.ARCHI_YEAR["institutions analysis"]

    # Setting root for saving intermediate results
    year_folder_path = wf_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    save_folder_path = analysis_folder_path / Path(affils_analysis_folder_alias)
    return save_folder_path


def _read_final_data(dedup_read_params):
    """Reads saved data of addresses and authors with affiliations resulting 
    from the parsing step and the publications list with one row per Institute's
    author enhanced by employees data.

    It uses the `read_final_dedup` function imported from 
    the `bmfuncts.read_final_results` module.

    Args:
        dedup_read_params (list): Composed of the 4 digits year of the corpus, \
        of the full path to working folder, of the dict giving the name of \
        the parsing file for each parsed item and of the full path to the folder \
        where final results are saved.
    Returns:
        (tup): The 3 read data (dataframe).
    """
    # Setting parameters values from 'read_data_params'
    corpus_year, final_results_path = dedup_read_params[0], dedup_read_params[3]

    # Getting the dict of deduplication results
    dedup_parsing_dict = read_final_dedup(dedup_read_params)

    # Getting useful parsing results
    addresses_df, authaddr_df = [dedup_parsing_dict[key]
                                 for key in bm_pg.PARSING_KEYS_DIC['build_addresses']]

    # Getting useful results of merge with employees data
    submit_df = read_final_submit_data(final_results_path, corpus_year)
    return addresses_df, authaddr_df, submit_df


def _build_institute_authors_addresses(corpus_year, input_dfs, pub_addresses_cols_dic):
    """Builds data of addresses per publication and author of the institute.

    Args:
        corpus_year (str): The 4 digits year of the corpus.
        input_dfs (list): The list composed of the data (dataframe) of \
        publications-list merge with employees data and of the deduplication \
        results of the parsing of authors with affiliations.
        pub_addresses_cols_dic (dict): The dict giving selected columns names \
        as built through the `_set_pub_addresses_cols_dic` internal function.
    Returns:
        (tup): (Data of addresses per publication and author of the institute \
        (dataframe), Publications IDs (str) of the institute (list)).
    """
    # Setting parameters value from 'input_dfs'
    submit_df, authaddr_df = input_dfs

    # Setting useful column names from 'pub_addresses_cols_dic'
    col_keys = ['bp_pub_id_col', 'bp_author_id_col', 'bp_address_col',
                'bm_pub_id_col', 'bm_author_id_col', 'bm_address_col']
    (bp_pub_id_col, bp_author_id_col, bp_address_col, bm_pub_id_col, bm_author_id_col,
     bm_address_col) = [pub_addresses_cols_dic[key] for key in col_keys]

    # Getting the data of consolidated Institute's authors
    bm_cols = [bm_pub_id_col, bm_author_id_col, bm_address_col]
    sub_submit_df = submit_df[bm_cols]

    # building {pub_id, institute_auth_ids_list} dict
    institute_auth_dict = {}
    for pub_id, pub_id_df in sub_submit_df.groupby(bm_pub_id_col):
        auth_ids_list = pub_id_df[bm_author_id_col].to_list()
        institute_auth_dict[pub_id] = auth_ids_list
    institute_pub_ids_list = list(institute_auth_dict.keys())

    # Getting the data of all authors with their addresses corrected
    bp_cols = [bp_pub_id_col, bp_author_id_col, bp_address_col]
    sub_authaddr_df = authaddr_df[bp_cols]
    sub_authaddr_df = set_year_pub_id(sub_authaddr_df, corpus_year, bp_pub_id_col)

    # Building the dict of institute-authors IDs per publications
    full_data = []
    for _, sub_authaddr_row in sub_authaddr_df.iterrows():
        pub_id = sub_authaddr_row[bp_pub_id_col]
        if pub_id in institute_pub_ids_list:
            dedup_author_idx = sub_authaddr_row[bp_author_id_col]
            if dedup_author_idx in institute_auth_dict[pub_id]:
                auth_addresses_list = sub_authaddr_row[bp_address_col].split("; ")
                data = []
                for auth_address in auth_addresses_list:
                    data.append([pub_id, dedup_author_idx, auth_address])
                full_data = full_data + data
    institute_author_addresses_df = pd.DataFrame(full_data, columns=bm_cols)
    return institute_author_addresses_df


def _build_init_institute_addresses_df(build_addr_params, pub_addresses_cols_dic,
                                       progress_param=None):
    """Selects from the addresses data obtained at the parsing step the ones 
    that corresponds to the consolidated publications list of the institute.

    This is performed through the following steps:

    1. Builds the data of standardized addresses per publication and author \
    of the institute through the `_build_institute_authors_addresses` internal function.
    2. Builds the dict for renaming parsing columns into consolidation ones.
    3. Sets the standardized addresses data from the deduplication results \
    of the parsing step through the `_read_addresses_data` internal function \
    and the `set_year_pub_id` function imported from the `bmfuncts.useful_functs` \
    module.
    4. Selects only addresses of the publications of the institute.

    All addresses are standardized through the `standardize_address` function \
    imported from the `biblioparsing` package.

    Args:
        build_addr_params (list): Composed of the 4 digits year of the corpus, \
        of the full path to working folder, of the dict giving the name of \
        the parsing file for each parsed item and of the full path to the folder \
        where final results are saved.
        pub_addresses_cols_dic (dict): The dict giving selected columns names \
        as built through the `_set_pub_addresses_cols_dic` internal function.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    Returns:
        (tup): (Data of addresses of the institute per publications (dataframe), \
        Data of addresses per publication and author of the institute (dataframe), \
        All useful column names (str) specific to 'BiblioMeter' (list), \
        Info for renaming parsing columns into consolidation ones (dict)).
    """
    # Setting parameters values from 'build_addr_params'
    corpus_year, final_results_path = build_addr_params[0], build_addr_params[3]

    # Setting parameters from optional arg
    progress_callback, init_progress, final_progress = [None] * 3
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_callback(init_progress)

    # Setting useful column names from 'pub_addresses_cols_dic'
    col_keys = ['bp_pub_id_col', 'bp_address_col', 'bm_pub_id_col', 'bm_address_col', 'bm_doctype_col']
    (bp_pub_id_col, bp_address_col, bm_pub_id_col, bm_address_col,
     bm_doctype_col) = [pub_addresses_cols_dic[key] for key in col_keys]

    # Setting useful cols lists
    col_lists_dic, bp2bm_rename_cols_dict = _set_col_lists_infos(pub_addresses_cols_dic)
    if progress_param:
        progress_callback(init_progress + (final_progress - init_progress) * 0.05)

    # Getting useful final data
    all_addresses_df, authaddr_df, submit_df = _read_final_data(build_addr_params)

    # Getting the institute-authors IDs per publications of the institute
    input_dfs = [submit_df, authaddr_df]
    return_df = _build_institute_authors_addresses(corpus_year, input_dfs, pub_addresses_cols_dic)
    return_df[bm_address_col] = return_df[bm_address_col].apply(bp_standardize_address)
    all_institute_author_addresses_df = return_df.copy()
    if progress_param:
        progress_callback(init_progress + (final_progress - init_progress) * 0.50)

    # Setting the addresses data from the deduplication results of the parsing step
    all_addresses_df = set_year_pub_id(all_addresses_df, corpus_year, bp_pub_id_col)
    all_addresses_df[bp_address_col] = all_addresses_df[bp_address_col].apply(bp_standardize_address)
    all_addresses_df.rename(columns=bp2bm_rename_cols_dict, inplace=True)
    if progress_param:
        progress_callback(init_progress + (final_progress - init_progress) * 0.80)

    # Selecting only data related to the consolidated publications list
    cols_list = [bm_pub_id_col, bm_doctype_col]
    institute_pub_addresses_init_df = keep_only_final_pub_data(all_addresses_df, final_results_path,
                                                               corpus_year, cols_list)
    institute_author_addresses_df = keep_only_final_pub_data(all_institute_author_addresses_df,
                                                             final_results_path, corpus_year, cols_list)
    if progress_param:
        progress_callback(final_progress)

    return_tup = (institute_pub_addresses_init_df, institute_author_addresses_df,
                  col_lists_dic, bp2bm_rename_cols_dict)
    return return_tup


def build_institute_addresses_df(institute_addr_params, verbose=False, progress_param=None):
    """Builds the data of addresses with one row per address 
    and per publication ID for the institute.

    For that, it uses the `_build_init_institute_addresses_df` and 
    `_clean_institute_addresses_data` internal functions. 
    The resulting data may be saved for control through the `save_xlsx_file` 
    function imported from `bmfuncts.useful_functs` and the use of 'verbose' arg.

    Args:
        addresses_params (list): The institute name (str), \
        the full path to the working folder (path), \
        4 digits year of the corpus (str).
        verbose (bool): Status of prints (optional, default = False).
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    Returns:
        (dataframe): The built data.
    """
    # Setting parameters values from "addresses_params"
    (corpus_year, institute, org_tup, wf_path, parsing_filenames_dict,
     final_results_path) = institute_addr_params

    # Setting dict giving column names
    pub_addresses_cols_dic = _set_pub_addresses_cols_dic(institute, org_tup)

    # Setting parameters from optional args
    (progress_callback, init_progress, final_progress,
     inter_progress_1, inter_progress_2) = [None] * 5
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_callback(init_progress)

    # Initializing the parameters dict for saving intermediate results
    save_params_dic = _initializing_save_params_dic(wf_path, corpus_year, verbose)

    # Building "institute_pub_addresses_init_df", "institute_author_addresses_df"
    inter_progress_param_1 = None
    if progress_param:
        inter_progress_1 = init_progress + (final_progress - init_progress) * 0.20
        inter_progress_param_1 = (progress_callback, init_progress, inter_progress_1)
    build_addr_params = [corpus_year, wf_path, parsing_filenames_dict, final_results_path]
    return_tup = _build_init_institute_addresses_df(build_addr_params, pub_addresses_cols_dic,
                                                    progress_param=inter_progress_param_1)
    (institute_pub_addresses_init_df, institute_author_addresses_df,
     col_lists_dic, bp2bm_rename_cols_dict) = return_tup
    if progress_param:
        progress_callback(inter_progress_1)

    if verbose:
        print("    col_lists_dic built")
        for step_df in [institute_pub_addresses_init_df, institute_author_addresses_df]:
            save_params_dic['save_num'] = _save_step_df(save_params_dic, step_df)

    inter_progress_param_2 = None
    if progress_param:
        inter_progress_2 = init_progress + (final_progress - init_progress) * 0.80
        inter_progress_param_2 = (progress_callback, inter_progress_1, inter_progress_2)
    clean_dfs = [institute_pub_addresses_init_df, institute_author_addresses_df]
    return_tup = _clean_institute_addresses_data(institute, clean_dfs, col_lists_dic,
                                                 verbose, save_params_dic,
                                                 progress_param=inter_progress_param_2)
    institute_pub_addresses_df, save_params_dic['save_num'] = return_tup
    if progress_param:
        progress_callback(inter_progress_2)

    # Renaming columns for building normalized and raw affiliations
    bm2bp_rename_cols_dict = {v: k for k, v in bp2bm_rename_cols_dict.items()}
    institute_pub_addresses_df.rename(columns=bm2bp_rename_cols_dict, inplace=True)
    if progress_param:
        progress_callback(final_progress)

    if verbose:
        _ = _save_step_df(save_params_dic, institute_pub_addresses_df)

    final_return_tup = (institute_pub_addresses_init_df, institute_author_addresses_df,
                        institute_pub_addresses_df)
    return final_return_tup
