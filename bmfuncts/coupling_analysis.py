"""Module of functions for publications-list analysis
in terms of geographical collaborations and institutions collaborations.

"""

__all__ = ['coupling_analysis']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
from bmfuncts.build_geo_stat import build_and_save_geo_stat
from bmfuncts.build_institutions_stat import build_and_save_institutions_stat
from bmfuncts.build_pub_addresses import build_institute_addresses_df
from bmfuncts.config_utils import set_user_config
from bmfuncts.correct_dedup import correct_dedup
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.read_final_results import build_pub_ids_dict
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import print_step_text


def _set_co_cols_dic(institute, org_tup):
    """Builds a dict setting selected columns names for the process 
    of coupling analysis.

    This is done through the `set_final_col_names` function imported 
    from the `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains parameters of Institute organization.
    Returns:
        (dict): The built dict.
    """
    final_col_dic, _ = set_final_col_names(institute, org_tup)

    co_cols_dic = {'hash_id_col'      : bm_pg.COL_HASH['hash_id'],
                   'pub_id_col'       : bp.COL_NAMES['pub_id'],
                   'doi_col'          : bp.COL_NAMES['articles'][6],
                   'address_col'      : bp.COL_NAMES['address'][2],
                   'address_id_col'   : bp.COL_NAMES['institution'][1],
                   'institutions_col' : bp.COL_NAMES['institution'][2],
                   'countries_col'    : bp.COL_NAMES['country'][2],
                   'raw_affil_col'    : "Raw affiliations",
                   'final_pub_id_col' : final_col_dic['pub_id'],
                   'final_doctype_col': final_col_dic['doc_type'],
                  }
    return co_cols_dic


def _clean_unkept_affil(raw_institutions_df, country_unkept_affil_file_path, cols_list):
    """Removes the affiliation items given in the file pointed by 'country_unkept_affil_file_path' 
    path from the raw-institutions data.

    Args:
        raw_institutions_df (dataframe): The initial data of raw institutions.
        country_unkept_affil_file_path (path): The full path to the data of raw \
        institutions that should be dropped from the initial data of raw institutions.
        cols_list (list): The names of useful columns.
    Returns:
        (dataframe): The cleaned data of raw institutions.
    """
    countries_col, raw_affil_col, institution_col = cols_list
    unkept_institutions_dict = pd.read_excel(country_unkept_affil_file_path, sheet_name=None)
    unkept_country_list = list(unkept_institutions_dict.keys())

    new_raw_institutions_df = pd.DataFrame()
    for country, country_raw_inst_df in raw_institutions_df.groupby(countries_col):
        if country in unkept_country_list:
            unkept_institutions_list = unkept_institutions_dict[country][raw_affil_col].to_list()
            unkept_institutions_list_mod = [institution.translate(bp.SYMB_CHANGE).strip()
                                            for institution in unkept_institutions_list]
            for idx_row, inst_row in country_raw_inst_df.iterrows():
                inst_row_list = [x.strip() for x in inst_row[institution_col].split(";")]
                inst_row_list_mod = [x.translate(bp.SYMB_CHANGE).lower() for x in inst_row_list]
                for unkept_inst in unkept_institutions_list_mod:
                    if unkept_inst.lower() in inst_row_list_mod:
                        inst_idx = inst_row_list_mod.index(unkept_inst.lower())
                        del inst_row_list_mod[inst_idx]
                        del inst_row_list[inst_idx]
                        if len(inst_row_list)>1:
                            country_raw_inst_df.loc[idx_row, institution_col] = "; ".join(inst_row_list)
                        elif len(inst_row_list)==1:
                            country_raw_inst_df.loc[idx_row, institution_col] = inst_row_list[0]
                        else:
                            country_raw_inst_df.loc[idx_row, institution_col] = bp.EMPTY
        new_raw_institutions_df = concat_dfs([new_raw_institutions_df, country_raw_inst_df])
    return new_raw_institutions_df


def _copy_dg_col_to_df(df, dg, cols_list, copy_col):
    """Copies a column of 'dg' data in initial 'df' data.

    Args:
         df (dataframe): The initial data.
         dg (dataframe): The data from which the column is copied
         cols_list (list): The names of useful columns.
         copy_col (str): The name of the column that is copied.
    Returns:
        (dataframe): The modified data.
    """
    df[copy_col] = dg[copy_col]
    df = df[cols_list]
    return df


def _enhance_raw_institutions_data(init_raw_addr_df, ids_dicts_list, co_cols_dic):
    """Adds hash-IDs and DOIs identifiers to help the user in the reduction 
    of the authors' affiliations not yet normalized and to identify the addresses 
    that need to be corrected.

    Args:
        init_raw_addr_df (dataframe): Initial data of raw affiliations of the corpus.
        ids_dicts_list (list): The list composed of the data (dict) of database ID \
        per publication ID and the data (dict) of the DOI per publication ID.
        co_cols_dic (dict): The dict giving the col names for coupling analysis process.
    Returns:
        (dataframe): The updated data of raw affiliations of the corpus.
    """
    # Setting useful column names aliases
    col_keys = ['hash_id_col','pub_id_col', 'doi_col', 'address_id_col',
                'countries_col', 'address_col', 'institutions_col']
    (hash_id_col, pub_id_col, doi_col, address_id_col, countries_col,
     address_col, institutions_col) = [co_cols_dic[key] for key in col_keys]

    init_ordered_columns = [pub_id_col, address_id_col, countries_col, address_col,
                            institutions_col]
    final_ordered_columns = [hash_id_col, pub_id_col, doi_col, address_id_col, countries_col,
                             address_col, institutions_col]

    # Setting hash-ID and DOI per publication data from args
    hash_ids_dict, dois_dict = ids_dicts_list

    raw_addr_df = pd.DataFrame(columns=final_ordered_columns)
    if not init_raw_addr_df.empty:
        init_raw_addr_df = init_raw_addr_df[init_ordered_columns]
        init_raw_addr_df = init_raw_addr_df.sort_values(by=[pub_id_col, address_id_col])
        data = []
        for _, row in init_raw_addr_df.iterrows():
            init_values_list = row.T.to_list()
            pub_id_str = row[pub_id_col]
            hash_id = hash_ids_dict[pub_id_str]
            pub_id_int = int(pub_id_str[5:])
            doi = dois_dict[pub_id_int]
            data.append([hash_id, pub_id_str, doi] + init_values_list[1:])
        raw_addr_df = pd.DataFrame(data, columns=final_ordered_columns)
    return raw_addr_df


def _build_norm_raw_affil_data(raw_addr_dfs_list, norm_paths_list, country_towns_file, co_cols_dic,
                               ids_dicts_list, print_params, progress_param=None):
    if progress_param:
        progress_callback, _init_progress, _final_progress = progress_param

    # Setting useful column names
    col_keys = ['address_col', 'address_id_col', 'institutions_col',
                'countries_col', 'final_pub_id_col', 'raw_affil_col']
    (address_col, address_id_col, institutions_col, countries_col,
     final_pub_id_col, raw_affil_col) = [co_cols_dic[key] for key in col_keys]

    # Setting parameters values from args
    inst_pub_raw_addr_df, empty_raw_addr_df, keep_norm_affil_df = raw_addr_dfs_list
    [institutions_folder_path, inst_types_file_path, country_affil_file_path,
     country_unkept_affil_file_path] = norm_paths_list

    # Building countries, normalized affiliations and remaining raw-addresses data
    return_tup = bp.build_norm_raw_institutions(inst_pub_raw_addr_df,
                                                inst_types_file_path=inst_types_file_path,
                                                country_affiliations_file_path=country_affil_file_path,
                                                country_towns_file=country_towns_file,
                                                country_towns_folder_path=institutions_folder_path,
                                                progress_param=progress_param)
    sub_countries_df, sub_norm_affil_df, sub_raw_addr_df, wrong_affil_types_dict = return_tup

    # Initializing returned parameters
    norm_affil_df, raw_addr_df = keep_norm_affil_df, empty_raw_addr_df
    raw_addr_status = False
    if not wrong_affil_types_dict:
        if progress_param:
            inter_progress_1 = _init_progress + (_final_progress - _init_progress) * 0.75
            progress_callback(inter_progress_1)
        step_str = ("      - Data of countries, of normalized affiliations and of remaining raw-addresses "
                    "for previously not-normalized addresses built")
        print_step_text(step_str, print_params)

        # Adding countries column to normalized institutions and remaining raw-addresses data
        norm_cols_list = [final_pub_id_col, address_id_col, countries_col, institutions_col]
        sub_norm_affil_df = _copy_dg_col_to_df(sub_norm_affil_df, sub_countries_df, norm_cols_list, countries_col)

        raw_cols_list = [final_pub_id_col, address_id_col, countries_col, address_col, institutions_col]
        sub_raw_addr_df = _copy_dg_col_to_df(sub_raw_addr_df, sub_countries_df, raw_cols_list, countries_col)
        if progress_param:
            inter_progress_2 =  _init_progress + (_final_progress - _init_progress) * 0.9
            progress_callback(inter_progress_2)
        step_str = ("      - Countries column added to the data of normalized affiliations and to the data "
                    "of remaing raw-addresses")
        print_step_text(step_str, print_params)

        # Removing unkept institutions from remaining raw-addresses data
        cols_list = [countries_col, raw_affil_col, institutions_col]
        sub_raw_addr_df = _clean_unkept_affil(sub_raw_addr_df, country_unkept_affil_file_path, cols_list)
        print_step_text("      - Unkept addresses-parts removed from the data of remaining raw-addresses", print_params)
        sub_raw_addr_df = _enhance_raw_institutions_data(sub_raw_addr_df, ids_dicts_list, co_cols_dic)
        print_step_text("      - Data of the remaining raw-addresses enhanced with complementary info", print_params)

        raw_addr_df = sub_raw_addr_df.copy()
        if not empty_raw_addr_df.empty:
            empty_raw_addr_df = empty_raw_addr_df[sub_raw_addr_df.columns]
            raw_addr_df = concat_dfs([empty_raw_addr_df, sub_raw_addr_df])
        raw_addr_df = raw_addr_df.sort_values(by=[final_pub_id_col, address_id_col])
        raw_addr_status = raw_addr_df[raw_addr_df[institutions_col]!=bp.EMPTY].empty
        print_step_text("      - Existing data of raw-addresses updated", print_params)

        norm_affil_df = sub_norm_affil_df.copy()
        if not keep_norm_affil_df.empty:
            norm_affil_df = concat_dfs([keep_norm_affil_df, sub_norm_affil_df])
        norm_affil_df = norm_affil_df.sort_values(by=[final_pub_id_col, address_id_col])
        print_step_text("      - Existing data of normalized affiliations updated", print_params)
    if progress_param:
        progress_callback(_final_progress)
    return norm_affil_df, raw_addr_df, wrong_affil_types_dict, raw_addr_status


def _build_addresses_to_normalize(addr_params, co_cols_dic, print_params, verbose=False, progress_param=None):

    # Setting useful column names
    col_keys = ['pub_id_col', 'address_col', 'address_id_col', 'institutions_col',
                'countries_col', 'final_pub_id_col', 'raw_affil_col']
    (pub_id_col, address_col, address_id_col, institutions_col, countries_col,
     final_pub_id_col, raw_affil_col) = [co_cols_dic[key] for key in col_keys]
    norm_cols_list = [final_pub_id_col, address_id_col, countries_col, institutions_col]


    # Building data of all addresses of Institute's publications from parsing addresses data
    print_step_text("  - Building data of all addresses of Institute's publications...", print_params)
    sub_addresses_param = addr_params[0:5]
    return_tup = build_institute_addresses_df(sub_addresses_param, verbose=verbose,
                                              progress_param=progress_param)
    inst_pub_raw_addr_df = return_tup[2]
    print_step_text("      - Data of all addresses of Institute's publications selected", print_params)

    sub_inst_pub_raw_addr_df = inst_pub_raw_addr_df.copy()
    empty_raw_addr_df = pd.DataFrame()
    keep_norm_affil_df = pd.DataFrame(columns=norm_cols_list)
    norm_affil_file_path, raw_addr_file_path = addr_params[5], addr_params[6]
    if raw_addr_file_path.is_file():
        print_step_text("  - Selecting data of addresses remaining to be normalized...", print_params)
        # Reading the previously built data of remaining raw-addresses
        init_raw_addr_df = pd.read_excel(raw_addr_file_path)

        empty_raw_addr_df = init_raw_addr_df[init_raw_addr_df[institutions_col]==bp.EMPTY]
        empty_pub_ids = empty_raw_addr_df[pub_id_col].to_list()
        empty_address_ids = empty_raw_addr_df[address_id_col].to_list()
        empty_pub_addr_tups = list(tuple(zip(empty_pub_ids, empty_address_ids)))

        empty_rows = []
        for idx, row in inst_pub_raw_addr_df.iterrows():
            pub_addr_tup = (row[pub_id_col], row[address_id_col])
            if pub_addr_tup in empty_pub_addr_tups:
                empty_rows.append(idx)
        sub_inst_pub_raw_addr_df = inst_pub_raw_addr_df.drop(empty_rows)
        print_step_text("      - Data of addresses remaining to be normalized selected", print_params)

        if norm_affil_file_path.is_file():
            # Reading the previously built data of normalized affiliations
            init_norm_affil_df = pd.read_excel(norm_affil_file_path)

            other_raw_addr_df = init_raw_addr_df[init_raw_addr_df[institutions_col]!=bp.EMPTY]
            other_pub_ids = other_raw_addr_df[pub_id_col].to_list()
            other_address_ids = other_raw_addr_df[address_id_col].to_list()
            other_pub_addr_tups = list(tuple(zip(other_pub_ids, other_address_ids)))

            other_rows = []
            for idx, row in init_norm_affil_df.iterrows():
                pub_addr_tup = (row[pub_id_col], row[address_id_col])
                if pub_addr_tup in other_pub_addr_tups:
                    other_rows.append(idx)
            keep_norm_affil_df = init_norm_affil_df.drop(other_rows)
            print_step_text("      - Data of normalized affiliations to be kept selected", print_params)
    addr_dfs_list = [sub_inst_pub_raw_addr_df, empty_raw_addr_df, keep_norm_affil_df]

    return addr_dfs_list


def _set_co_files_params(institute, wf_path, corpus_year, final_results_path):
    """Sets IFs specific file and folder.

    Args:
        institute (str): Institute name.
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): (the list of useful file names, \
        the list of useful folder names, the list of useful paths).
    """
    # Setting aliases from globals
    hash_id_folder_alias = bm_pg.ARCHI_RESULTS["hash_id"]
    addresses_to_correct_file_alias = bm_pg.ARCHI_RESULTS["false_addresses_file"]
    analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    inst_analysis_folder_alias = bm_pg.ARCHI_YEAR["institutions analysis"]
    norm_inst_file_base_alias = bm_pg.ARCHI_YEAR["norm inst file name"]
    raw_inst_file_base_alias = bm_pg.ARCHI_YEAR["raw inst file name"]
    institutions_folder_alias = bm_pg.ARCHI_INSTITUTIONS["root"]
    inst_types_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["inst_types_base"]
    country_affiliations_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["affiliations_base"]
    country_towns_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["country_towns_base"]
    country_unkept_inst_file_base_alias = bm_pg.ARCHI_INSTITUTIONS["unkept_affil_base"]

    # Setting useful file names
    hash_id_file = f'{corpus_year} {bm_pg.ARCHI_YEAR["hash_id file name"]}'
    norm_inst_file = norm_inst_file_base_alias + '.xlsx'
    raw_inst_file = raw_inst_file_base_alias + '.xlsx'
    inst_types_file = institute + "_" + inst_types_file_base_alias
    country_affil_file = institute + "_" + country_affiliations_file_base_alias
    country_towns_file = institute + "_" + country_towns_file_base_alias
    country_unkept_affil_file = institute + "_" + country_unkept_inst_file_base_alias

    # Setting useful paths
    year_folder_path = wf_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    inst_analysis_folder_path = analysis_folder_path / Path(inst_analysis_folder_alias)
    institutions_folder_path = wf_path / Path(institutions_folder_alias)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file)
    country_affil_file_path = institutions_folder_path / Path(country_affil_file)
    country_unkept_affil_file_path = institutions_folder_path / Path(country_unkept_affil_file)
    year_final_results_path = final_results_path / Path(corpus_year)
    hash_ids_path = year_final_results_path / Path(hash_id_folder_alias) / Path(hash_id_file)
    inst_addresses_to_correct_path = inst_analysis_folder_path / Path(addresses_to_correct_file_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(inst_analysis_folder_path):
        os.makedirs(inst_analysis_folder_path)

    files_list = [country_towns_file, norm_inst_file, raw_inst_file]
    folders_list = [analysis_folder_alias, inst_analysis_folder_alias]
    paths_list = [analysis_folder_path, institutions_folder_path,
                  inst_analysis_folder_path, inst_types_file_path,
                  country_affil_file_path, country_unkept_affil_file_path, hash_ids_path,
                  inst_addresses_to_correct_path]
    return files_list, folders_list, paths_list


def _built_co_pub_identifiers_data(ids_params, hash_ids_path, identifiers_cols):
    """Builds data of publications identifiers specific to a given deduplicated corpus parsing.

    Args:
        ids_params (list): The list composed of the full path to the working folder (path), \
        of the 4 digits year of the corpus (str) and of the full path to the folder \
        where the final results of parsings deduplication are saved.
        hash_ids_path (path): The full path to the hash-IDs file.
        identifiers_cols (list): The column names of the publications identifiers.
    Returns:
        (list): The list composed of the data (dict) of database ID per publication ID \
        and the data (dict) of the DOI per publication ID.
    """
    # Setting parameters values from args
    wf_path, corpus_year, final_results_path = ids_params
    hash_id_col, pub_id_col, doi_col = identifiers_cols

    # Building the data of hash-ID per publication-ID
    hash_ids_df = pd.read_excel(hash_ids_path)
    hash_ids_dict = dict(zip(hash_ids_df[pub_id_col], hash_ids_df[hash_id_col]))

    # Building the data of DOI per publication-ID
    parsing_dict = read_final_dedup(wf_path, final_results_path, corpus_year)
    articles_df = parsing_dict['articles']
    dois_dict = dict(zip(articles_df[pub_id_col], articles_df[doi_col]))
    ids_dicts_list = [hash_ids_dict, dois_dict]
    return ids_dicts_list


def coupling_analysis(params_list, progress_callback=None, verbose=False):
    """Performs the analysis of countries and authors affiliations of Institute publications 
    of a corpus.

    This is done through the following steps:

    1. Gets the 'all_address_df' dataframe of authors addresses from the file which full path \
    is given by 'addresses_item_path' and that is a deduplication results of the parsing step \
    of the corpus.
    2. Builds the 'inst_pub_addresses_df' dataframe by selecting in 'all_address_df' dataframe \
    only addresses related to publications of the Institute.
    3. Builds the dataframes of countries, normalized institutions and raw institutions \
    through the `_build_and_save_norm_raw_dfs` internal function.
    4. Builds the publications statistics dataframes per institutions through the \
    `_build_and_save_institutions_stat` internal function after setting the Institute publications \
    IDs list through the `build_pub_ids_dict` function imported from the `bmfuncts.read_final_results` \
    module.
    5. Builds the publications statistics dataframes per country and per continent through \
    the `_build_and_save_geo_stat` internal function.
    6. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        params_list (list):  The list composed of the Institute name (str), \
        of the org_tup (tup) that contains parameters of Institute organization, \
        of the full path to working folder (path), of the data combination type \
        of corpuses databases (str) and of the 4 digits year of the corpus (str).
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default: None).
        verbose (bool): Status of prints (default: False).
    Returns:
        (tup): (The full path (path) to the folder where results of coupling analysis are saved, \
        The full path (path) to folder where the results of the geographical analysis are saved, \
        The full path (path) to folder where the results of the collaborations analysis are saved, \
        The full path (path) to the file of countries-affiliations data, \
        The dict keyed by countries and valued by the list of the normalized affiliation types \
        to be corrected).
    """
    # Setting parameters values from params_list
    institute, org_tup, wf_path, datatype, print_params, corpus_year = params_list

    # Getting item_filename_dict
    config_tup = set_user_config(wf_path, corpus_year, bm_pg.BDD_LIST)
    item_filename_dict = config_tup[2]

    # Setting useful files parameters
    final_results_path = set_results_folder_path(wf_path, datatype)
    files_list, folders_list, paths_list = _set_co_files_params(institute, wf_path,
                                                                corpus_year, final_results_path)
    (analysis_folder_path, institutions_folder_path, inst_analysis_folder_path, inst_types_file_path,
     country_affil_file_path, country_unkept_affil_file_path, hash_ids_path, inst_addresses_to_correct_path) = paths_list
    country_towns_file, norm_affil_file, raw_addr_file = files_list
    norm_affil_file_path = inst_analysis_folder_path / Path(norm_affil_file)
    raw_addr_file_path = inst_analysis_folder_path / Path(raw_addr_file)

    # Setting useful parameters lists
    ids_params = [wf_path, corpus_year, final_results_path]
    dedup_params = [institute, wf_path, print_params, corpus_year, final_results_path, inst_addresses_to_correct_path]
    addr_params = [institute, org_tup, wf_path, corpus_year, final_results_path,
                   norm_affil_file_path, raw_addr_file_path]

    # Setting useful column names
    co_cols_dic = _set_co_cols_dic(institute, org_tup)
    col_keys = ['hash_id_col', 'pub_id_col', 'doi_col', 'final_pub_id_col', 'final_doctype_col',
                'address_id_col', 'countries_col']
    (hash_id_col, pub_id_col, doi_col, final_pub_id_col, final_doctype_col,
     address_id_col, countries_col) = [co_cols_dic[key] for key in col_keys]

    # Setting parameters from optional arg
    progress_param, init_progress, final_progress= [None] * 3
    if progress_callback:
        init_progress, final_progress = 5, 100
        progress_callback(init_progress)

    # Building data of hash-ID and DOI per publication
    identifiers_cols = [hash_id_col, pub_id_col, doi_col]
    ids_dicts_list = _built_co_pub_identifiers_data(ids_params, hash_ids_path, identifiers_cols)

    # Correcting false addresses in deduplication-parsing data as indicated by the user
    print_step_text("\nCorrecting false addresses...", print_params)
    addresses_to_correct_path, correct_status = correct_dedup(dedup_params, item_filename_dict,
                                                              ids_dicts_list)
    if correct_status:
        print_step_text("  - False addresses in deduplication-parsing data corrected", print_params)
    else:
        print_step_text("  - No correction of false addresses in deduplication-parsing data", print_params)

    if progress_callback:
        inter_progress_1 = init_progress + (final_progress - init_progress) * 0.20
        inter_progress_2 = init_progress + (final_progress - init_progress) * 0.50
        progress_param = (progress_callback, inter_progress_1, inter_progress_2)
        progress_callback(inter_progress_1)

    # Selecting addresses of Institute's publications remaining to be normalized
    print_step_text("\nBuilding data of addresses of Institute's publications remaining to be normalized...",
                    print_params)
    addr_dfs_list = _build_addresses_to_normalize(addr_params, co_cols_dic, print_params,
                                                  verbose=verbose, progress_param=progress_param)
    inst_pub_raw_addr_df, empty_raw_addr_df, keep_norm_affil_df = addr_dfs_list
    print_step_text("  - Data of addresses of Institute's publications remaining to be normalized built",
                    print_params)
    if inst_pub_raw_addr_df.empty:
        print_step_text("  - No address remains to be normalized", print_params)
    else:
        print_step_text("  - Addresses remain to be normalized", print_params)
    if progress_callback:
        progress_callback(inter_progress_2)
        inter_progress_3 = init_progress + (final_progress - init_progress) * 0.8
        progress_param = (progress_callback, inter_progress_2, inter_progress_3)

    print_step_text("\nTrying to built affiliations stat and geographical stat...", print_params)
    if not inst_pub_raw_addr_df.empty:
        norm_paths_list = [institutions_folder_path, inst_types_file_path, country_affil_file_path,
                           country_unkept_affil_file_path]
        print_step_text("  - Building normalized affiliations data and remaining raw-addresses...", print_params)
        return_tup = _build_norm_raw_affil_data(addr_dfs_list, norm_paths_list, country_towns_file, co_cols_dic,
                                                ids_dicts_list, print_params, progress_param=progress_param)
        norm_affil_df, raw_addr_df, wrong_affil_types_dict, raw_addr_status = return_tup
        print_step_text("      - Normalized affiliations data and remaining raw-addresses built", print_params)
    else:
        raw_addr_status = True
        wrong_affil_types_dict = {}
        norm_affil_df = keep_norm_affil_df.copy()
        raw_addr_df = empty_raw_addr_df.copy()
        print_step_text("  - Normalized affiliations data unchanged...", print_params)
    countries_df = norm_affil_df[[final_pub_id_col, address_id_col, countries_col]]

    # Saving formatted df of normalized and raw institutions
    inst_df_title = bm_pg.DF_TITLES_LIST[9]
    sheet_name = 'Norm ' + corpus_year
    save_formatted_df_to_xlsx(inst_analysis_folder_path, norm_affil_file,
                              norm_affil_df, inst_df_title, sheet_name)
    inst_df_title = bm_pg.DF_TITLES_LIST[16]
    sheet_name = 'Raw ' + corpus_year
    save_formatted_df_to_xlsx(inst_analysis_folder_path, raw_addr_file,
                              raw_addr_df, inst_df_title, sheet_name)
    step_text = "      - Data of normalized affiliations and of raw-affiliations saved "
    if raw_addr_status:
        step_text += "with empty raw-affiliations"
    else:
        step_text += "with remaining raw-affiliation"
    print_step_text(step_text, print_params)

    if not wrong_affil_types_dict and raw_addr_status:
        # Building and saving inst stat dataframe
        if progress_callback:
            inter_progress_4 = init_progress + (final_progress - init_progress) * 0.9
            progress_param = (progress_callback, inter_progress_3, inter_progress_4)
        pub_doctype_cols_list = [final_pub_id_col, final_doctype_col]
        pub_ids_dict = build_pub_ids_dict(final_results_path, corpus_year, pub_doctype_cols_list)
        sub_paths_list = [final_results_path, inst_analysis_folder_path, inst_types_file_path]
        inst_stat_params = [institute, corpus_year, print_params]
        build_and_save_institutions_stat(norm_affil_df, sub_paths_list, pub_ids_dict,
                                         inst_stat_params, progress_param=progress_param)

        # Setting Institute's geo
        institute_geo_dict = {'country'  : bm_ig.INSTITUTES_COUNTRY_DICT[institute],
                              'continent': bm_ig.INSTITUTES_CONTINENT_DICT[institute],
                              'norm_name': bm_ig.INSTITUTES_NORM_NAME_DICT[institute],
                             }

        # Building and saving geo stat dataframes
        geo_analysis_folder_name = build_and_save_geo_stat(countries_df, norm_affil_df,
                                                           institute_geo_dict, analysis_folder_path,
                                                           corpus_year, print_params)
        if progress_callback:
            inter_progress_5 = init_progress + (final_progress - init_progress) * 0.98
            progress_callback(inter_progress_5)

        # Saving coupling analysis as final result
        status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
        results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
        save_keys_list = ["countries", "continents", "institutions", "institute_country"]
        for key in save_keys_list:
            results_to_save_dict[key] = True
        _ = save_final_results(params_list, results_to_save_dict,
                               institute_country=institute_geo_dict['country'])
    else:
        geo_analysis_folder_name = ""

    return_folders_list = [folders_list[0], folders_list[1], geo_analysis_folder_name]
    return_paths_list = [country_affil_file_path, addresses_to_correct_path]
    return_tup = (wrong_affil_types_dict, raw_addr_status, return_folders_list, return_paths_list)
    if progress_callback:
        progress_callback(final_progress)
    return return_tup
