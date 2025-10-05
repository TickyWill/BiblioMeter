"""Module of functions for building information on collaborating institutions with the Institute.

"""

__all__ = ['build_institute_addresses_df']

# Standard Library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import get_final_dedup
from bmfuncts.useful_functs import read_final_submit_data
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

    pub_addresses_cols_dic = {'bp_pub_id_col'    : bp.COL_NAMES['address'][0],
                              'bp_address_id_col': bp.COL_NAMES['address'][1],
                              'bp_address_col'   : bp.COL_NAMES['address'][2],
                              'bm_pub_id_col'    : submit_col_rename_dic[bp.COL_NAMES['authors'][0]],
                              'bm_address_id_col': bm_pg.COL_NAMES_BONUS['address ID'],
                              'bm_address_col'   : submit_col_rename_dic[bp.COL_NAMES['address'][2]],
                              'bm_author_id_col' : submit_col_rename_dic[bp.COL_NAMES['authors'][1]],
                             }

    return pub_addresses_cols_dic


def _set_col_lists_infos(pub_addresses_cols_dic):
    """Builds a dict giving useful col lists and a dict for renaming col names.

    The col names set by the `BiblioParsing` package are renamed with the col names
    set within the `bmfuncts` package.

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

    The dict is keyyed by the step index and valued name (str) of the data
    to be saved.

    Returns:
        (dict): the built dict.
    """
    steps_save_params_dic = {1: 'inst_pub_addresses_init_df',
                             2: 'institute_author_addresses_df',
                             3: 'pubid_addid_authid_addresse_df',
                             4: 'corr_pubid_addid_authid_addresse_df',
                             5: 'inst_pub_addresses_df',
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
    save_params_dic = {'save_num': save_num,}

    if verbose:
        # Setting the folder for saving intermediate results
        save_folder_path = _set_save_folder_path(wf_path, corpus_year)
        save_params_dic['save_folder_path'] = save_folder_path
        # Building the dict giving information for saving intermediate results
        steps_save_params_dic = _set_steps_save_params_dic()
        save_params_dic['steps_save_params_dic'] = steps_save_params_dic
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
    # Setting parameters values from 'save_params_dic'
    keys = ['save_num', 'save_folder_path', 'steps_save_params_dic']
    (save_num, save_folder_path,
     steps_save_params_dic) = [save_params_dic[key] for key in keys]

    # saving intermediate results
    save_num += 1
    step_value = steps_save_params_dic[save_num]
    step_file = f'{str(save_num)}-{step_value}.xlsx'
    save_xlsx_file(save_folder_path, step_df, step_file)

    # Printing message
    print(f'    {step_value} built')

    return save_num


def _build_pubid_addid_authid_addresse_df(inst_pub_addresses_init_df,
                                          institute_author_addresses_df,
                                          bm_full_cols_list):
    """Builds the data of addresses per author ID, per address ID and per 
    publication ID.

    Author_id is set to "_" for authors not affiliated to the institute. 
    The input data are built through the `_build_init_institute_addresses_df` 
    internal function.

    Args:
        inst_pub_addresses_init_df (dataframe): The data of addresses \
        per publications of the institute .
        institute_author_addresses_df (dataframe): The Data of addresses per \
        publication and author of the institute. 
        bm_full_cols_list (list): All useful column names (str) set within \
        the application.
    Returns:
        (dataframe): The built data.
    """
    bm_pub_id_col, bm_address_id_col, bm_author_id_col, bm_address_col = bm_full_cols_list
    pubid_addid_authid_addresse_df = pd.DataFrame()
    for pub_id, pub_id_df1 in inst_pub_addresses_init_df.groupby(bm_pub_id_col):
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
        pub_id_out_df = pd.DataFrame()
        data = []
        for address in df1_out_df2_addresses_list:
            # Setting data for other authors than authors of the institute
            address_id = df1_address_dict[address]
            author_id = "_"
            data.append([pub_id, address_id, author_id, address])
            address_df = pd.DataFrame(data,
                                      columns=bm_full_cols_list)
            pub_id_out_df = concat_dfs([pub_id_out_df, address_df])

        for df2_address, df2_address_df in pub_id_df2.groupby(bm_address_col):
            # Setting data for authors of the institute
            df2_author_ids_list = df2_address_df[bm_author_id_col].to_list()
            df1_address_id = df1_address_dict[df2_address]
            data = []
            for author_id in df2_author_ids_list:
                data.append([pub_id, df1_address_id, author_id, df2_address])
            address_df = pd.DataFrame(data, columns=bm_full_cols_list)
            pub_id_out_df = concat_dfs([pub_id_out_df, address_df])
        pub_id_out_df = pub_id_out_df.drop_duplicates()
        pub_id_out_df = pub_id_out_df.sort_values(by=[bm_address_id_col])

        # Updating the full pubid_addid_authid_addresse_df by concatenation with 'pub_id_out_df'
        pubid_addid_authid_addresse_df = concat_dfs([pubid_addid_authid_addresse_df, pub_id_out_df])
    return pubid_addid_authid_addresse_df


def _correct_inst_address(pubid_addid_authid_addresse_df, bm_full_cols_list):
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
                    new_addresses_list = [address.replace("INES", ines_rpl_str) for address in addresses_list]
                    new_addresses_list = [address.replace(bp.UNKNOWN, unknown_rpl_str)
                                          for address in new_addresses_list]
                    addresses_dict = dict(zip(new_addresses_list, address_ids_list))
                    data = []
                    for address in new_addresses_list:
                        data.append([pub_id, addresses_dict[address], author_id, address])
                    address_df = pd.DataFrame(data, columns=bm_full_cols_list)
                    new_author_id_df = pd.concat([new_author_id_df, address_df])
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
        corr_pubid_addid_authid_addresse_df (dtaframe): The data of addresses \
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
    out_df = pd.DataFrame()
    for pub_id, pub_id_df in in_df.groupby(bm_pub_id_col):
        data = []
        for addr_id, addr_id_df in pub_id_df.groupby(bm_address_id_col):
            addresses_list = list(set(addr_id_df[bm_address_col].to_list()))
            address = ", ".join(addresses_list)
            data.append([pub_id, addr_id, address])
            addr_df = pd.DataFrame(data, columns=data_cols)
            out_df = concat_dfs([out_df, addr_df])
    out_df = out_df.drop_duplicates()
    inst_pub_addresses_df = out_df.copy()
    return inst_pub_addresses_df


def _clean_institute_addresses_data(institute, inst_pub_addresses_init_df,
                                    institute_author_addresses_df, col_lists_dic,
                                    verbose, save_params_dic, progress_param=None):
    """Cleans the data of addresses per publication ID depending on the institute.
    
    It uses the `_build_pubid_addid_authid_addresse_df`, `_correct_inst_address` 
    and `_build_final_institute_addresses_df` internal functions to do that. 
    The resulting data may be saved for control through the `save_xlsx_file` 
    function imported from `bmfuncts.useful_functs` and the use of 'verbose' arg.

    Args:
        institute (str): The institute name.
        inst_pub_addresses_init_df (dataframe): The initial data of addresses \
        per publications of the institute.
        institute_author_addresses_df (dataframe): The Data of addresses per \
        publication and author of the institute. 
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
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_step = (final_progress - init_progress) * 0.30
        progress_status = init_progress
        progress_callback(progress_status)

    if institute.upper()=="LITEN":
        # Building "pubid_addid_authid_addresse_df"
        return_df = _build_pubid_addid_authid_addresse_df(inst_pub_addresses_init_df,
                                                          institute_author_addresses_df,
                                                          bm_full_cols_list)
        pubid_addid_authid_addresse_df = return_df
        if progress_param:
            progress_status += progress_step
            progress_callback(progress_status)
        if verbose:
            save_params_dic['save_num'] = _save_step_df(save_params_dic,
                                                        pubid_addid_authid_addresse_df)

        # Building corrected "pubid_addid_authid_addresse_df"
        corr_pubid_addid_authid_addresse_df = _correct_inst_address(pubid_addid_authid_addresse_df,
                                                                    bm_full_cols_list)
        if progress_param:
            progress_status += progress_step
            progress_callback(progress_status)
        if verbose:
            save_params_dic['save_num'] = _save_step_df(save_params_dic,
                                                        corr_pubid_addid_authid_addresse_df)

        # Building final_institute_addresses_df
        inst_pub_addresses_df = _build_final_institute_addresses_df(corr_pubid_addid_authid_addresse_df,
                                                                    bm_final_cols_list)
    else:
        inst_pub_addresses_df = inst_pub_addresses_init_df.copy()
    if progress_param:
        progress_callback(final_progress)
    return inst_pub_addresses_df, save_params_dic['save_num']


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
    inst_analysis_folder_alias = bm_pg.ARCHI_YEAR["institutions analysis"]

    # Setting root for saving intermediate results
    year_folder_path = wf_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    save_folder_path = analysis_folder_path / Path(inst_analysis_folder_alias)
    return save_folder_path


def _read_addresses_data(input_data_params):
    """Reads saved data of addresses resulting from the parsing step.

    It uses the `get_final_dedup` function imported from 
    the `bmfuncts.useful_functs` module.

    Args:
        input_data_params (list): The list composed of the full path (path) \
        to the working folder, of the 4 digits year (str) of the corpus \
        and of the Full path to the folder where final results are saved.
    Returns:
        (dataframe): The data of addresses.
    """
    # Setting parameters values from 'input_data_params'
    wf_path, corpus_year, saved_results_path = input_data_params

    # Setting useful aliases
    addresses_item_alias = bp.PARSING_ITEMS_LIST[2]

    # Getting the dict of deduplication results
    dedup_parsing_dict = get_final_dedup(wf_path,
                                         saved_results_path,
                                         corpus_year)

    # Getting ID of each author with author name
    addresses_df = dedup_parsing_dict[addresses_item_alias]
    return addresses_df


def _build_institute_authors_addresses(input_data_params, pub_addresses_cols_dic):
    """Builds data of addresses per publication and author of the institute.

    Args:
        input_data_params (list): The list composed of the 4 digits year (str) \
        of the corpus and of the Full path to the folder where final results are saved.
        pub_addresses_cols_dic (dict): The dict giving selected columns names \
        as built through the `_set_pub_addresses_cols_dic` internal function.
    Returns:
        (tup): (Data of addresses per publication and author of the institute \
        (dataframe), Publications IDs (str) of the institute (list)).
    """
    # Setting parameters values from 'input_data_params'
    corpus_year, saved_results_path = input_data_params

    # Setting useful column names from 'pub_addresses_cols_dic'
    col_keys = ['bm_pub_id_col', 'bm_author_id_col', 'bm_address_col']
    (bm_pub_id_col, bm_author_id_col,
     bm_address_col) = [pub_addresses_cols_dic[key] for key in col_keys]

    # Setting useful col list
    data_cols = [bm_pub_id_col, bm_author_id_col, bm_address_col]

    # Building the dict of institute-authors IDs per publications
    submit_df = read_final_submit_data(saved_results_path, corpus_year)
    sub_submit_df = submit_df[data_cols]

    institute_author_addresses_df = pd.DataFrame()
    for _, submit_row in sub_submit_df.iterrows():
        pub_id = submit_row[bm_pub_id_col]
        author_idx = submit_row[bm_author_id_col]
        auth_addresses_list = submit_row[bm_address_col].split("; ")
        data = []
        for auth_address in auth_addresses_list:
            data.append([pub_id, author_idx, auth_address])
            author_addresse_df = pd.DataFrame(data, columns=data_cols)
            dfs_list = [institute_author_addresses_df, author_addresse_df]
            institute_author_addresses_df = concat_dfs(dfs_list)
    inst_pud_ids_list = list(set(institute_author_addresses_df[bm_pub_id_col].to_list()))
    return institute_author_addresses_df, inst_pud_ids_list


def _build_init_institute_addresses_df(sub_addresses_params, pub_addresses_cols_dic,
                                       progress_param=None):
    """Selects from the addresses data obtained at the parsing step the ones 
    that corresponds to the consolidated publications list of the institute.

    This is performed through the following steps:

    1. Builds the data of standardized addresses per publication and author \
    of the institute through the `_build_institute_authors_addresses` internal function.
    2. Builds the dict for renaming 'BiblioParsing' columns into 'BiblioMeter' ones.
    3. Sets the standardized addresses data from the deduplication results \
    of the parsing step through the `_read_addresses_data` internal function \
    and the `set_year_pub_id` function imported from the `bmfuncts.useful_functs` \
    module.
    4. Selects only addresses of the publications of the institute.

    All addresses are standardized through the `standardize_address` function \
    imported from the `BiblioParsing` package.

    Args:
        sub_addresses_params (list): Composed of of the full path (path) to \
        the working folder, of the 4 digits year (str) of the corpus and of \
        the full path to the folder where final results are saved (path).
        pub_addresses_cols_dic (dict): The dict giving selected columns names \
        as built through the `_set_pub_addresses_cols_dic` internal function.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    Returns:
        (tup): (Data of addresses of the institute per publications (dataframe), \
        Data of addresses per publication and author of the institute (dataframe), \
        All useful column names (str) specific to 'BiblioMeter' (list), \
        Info for renaming 'BiblioParsing' columns into 'BiblioMeter' ones (dict)).
    """
    # Setting parameters values from 'sub_addresses_params'
    corpus_year = sub_addresses_params[1]

    # Setting parameters from optional arg
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_callback(init_progress)

    # Setting useful column names from 'pub_addresses_cols_dic'
    col_keys = ['bp_pub_id_col', 'bp_address_col', 'bm_pub_id_col', 'bm_address_col']
    (bp_pub_id_col, bp_address_col,
     bm_pub_id_col, bm_address_col) = [pub_addresses_cols_dic[key] for key in col_keys]

    # Setting useful cols lists
    col_lists_dic, bp2bm_rename_cols_dict = _set_col_lists_infos(pub_addresses_cols_dic)

    # Setting the addresses data from the deduplication results of the parsing step
    all_address_df = _read_addresses_data(sub_addresses_params)
    all_address_df = set_year_pub_id(all_address_df, corpus_year, bp_pub_id_col)
    all_address_df[bp_address_col] = all_address_df[bp_address_col].apply(bp.standardize_address)
    all_address_df.rename(columns=bp2bm_rename_cols_dict, inplace=True)
    if progress_param:
        progress_callback(init_progress + (final_progress - init_progress) * 0.20)

    # Getting the institute-authors IDs per publications of the institute
    return_tup = _build_institute_authors_addresses(sub_addresses_params[1:],
                                                    pub_addresses_cols_dic)
    return_df, inst_pud_ids_list = return_tup
    return_df[bm_address_col] = return_df[bm_address_col].apply(bp.standardize_address)
    institute_author_addresses_df = return_df.copy()
    if progress_param:
        progress_callback(init_progress + (final_progress - init_progress) * 0.70)

    # Selecting only addresses of the publications of the institute
    inst_pub_addresses_init_df = pd.DataFrame()
    for pub_id, dg in all_address_df.groupby(bm_pub_id_col):
        if pub_id in inst_pud_ids_list:
            inst_pub_addresses_init_df = concat_dfs([inst_pub_addresses_init_df, dg])
    if progress_param:
        progress_callback(final_progress)

    return_tup = (inst_pub_addresses_init_df, institute_author_addresses_df,
                  col_lists_dic, bp2bm_rename_cols_dict)
    return return_tup


def build_institute_addresses_df(addresses_params, verbose=False,
                                 progress_param=None):
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
    institute, org_tup, wf_path, corpus_year = addresses_params[:-1]
    sub_adresses_params = addresses_params[2:]

    # Setting dict giving column names
    pub_addresses_cols_dic = _set_pub_addresses_cols_dic(institute, org_tup)

    # Setting parameters from optional arg
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_callback(init_progress)

    # Initializing the parameters dict for saving intermediate results
    save_params_dic = _initializing_save_params_dic(wf_path, corpus_year, verbose)

    # Building "inst_pub_addresses_init_df", "institute_author_addresses_df"
    inter_progress_param_1 = None
    if progress_param:
        inter_progress_1 = init_progress + (final_progress - init_progress) * 0.20
        inter_progress_param_1 = (progress_callback, init_progress, inter_progress_1)
    return_tup = _build_init_institute_addresses_df(sub_adresses_params, pub_addresses_cols_dic,
                                                    progress_param=inter_progress_param_1)
    (inst_pub_addresses_init_df, institute_author_addresses_df,
     col_lists_dic, bp2bm_rename_cols_dict) = return_tup
    if progress_param:
        progress_callback(inter_progress_1)

    if verbose:
        print("    col_lists_dic built")
        for step_df in [inst_pub_addresses_init_df, institute_author_addresses_df]:
            save_params_dic['save_num'] = _save_step_df(save_params_dic, step_df)

    inter_progress_param_2 = None
    if progress_param:
        inter_progress_2 = init_progress + (final_progress - init_progress) * 0.80
        inter_progress_param_2 = (progress_callback, inter_progress_1, inter_progress_2)
    return_tup = _clean_institute_addresses_data(institute, inst_pub_addresses_init_df,
                                                 institute_author_addresses_df, col_lists_dic,
                                                 verbose, save_params_dic,
                                                 progress_param=inter_progress_param_2)
    inst_pub_addresses_df, save_params_dic['save_num'] = return_tup
    if progress_param:
        progress_callback(inter_progress_2)

    if verbose:
        _ = _save_step_df(save_params_dic, inst_pub_addresses_df)

    # Renaming columns for building normalized and raw institutions through BiblioParsing package
    bm2bp_rename_cols_dict = {v: k for k, v in bp2bm_rename_cols_dict.items()}
    inst_pub_addresses_df.rename(columns=bm2bp_rename_cols_dict, inplace=True)
    if progress_param:
        progress_callback(final_progress)
    return inst_pub_addresses_df
