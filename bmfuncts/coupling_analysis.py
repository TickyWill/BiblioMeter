"""Module of functions for publications-list analysis of the Institute 
in terms of authors' geographical location and of authors' affiliations.

The statistical analysis is performed through the functions of 
the `build_affiliations_stat` module.
"""

__all__ = ['coupling_analysis']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import pandas as pd
from bpfuncts import build_norm_and_raw_affils as bp_build_norm_and_raw_affils

# Local imports
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
from bmfuncts.build_geo_stat import build_and_save_geo_stat
from bmfuncts.build_affiliations_stat import build_and_save_affiliations_stat
from bmfuncts.build_pub_addresses import build_institute_addresses_df
from bmfuncts.correct_dedup import correct_dedup
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.read_final_results import build_pub_ids_dict
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import remove_file


def _set_co_cols_dic(institute, org_tup):
    """Builds a dict setting selected columns names for the process 
    of coupling analysis.

    This is done through the `set_final_col_names` function imported 
    from the `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains parameters of Institute's organization.
    Returns:
        (dict): The built dict.
    """
    final_col_dic, _ = set_final_col_names(institute, org_tup)

    co_cols_dic = {'hash_id_col'      : bm_pg.COL_HASH['hash_id'],
                   'pub_id_col'       : bm_pg.COL_NAMES['pub_id'],
                   'doi_col'          : bm_pg.COL_NAMES['articles'][6],
                   'address_col'      : bm_pg.COL_NAMES['address'][2],
                   'address_id_col'   : bm_pg.COL_NAMES['institution'][1],
                   'affiliations_col' : bm_pg.COL_NAMES['institution'][2],
                   'countries_col'    : bm_pg.COL_NAMES['country'][2],
                   'raw_affil_col'    : "Raw affiliations",
                   'final_pub_id_col' : final_col_dic['pub_id'],
                   'final_doctype_col': final_col_dic['doc_type'],
                  }
    return co_cols_dic


def _clean_unkept_affil(raw_affiliations_df, country_unkept_affil_file_path, cols_list):
    """Removes the affiliation items given in the file pointed by 'country_unkept_affil_file_path' 
    path from the raw-affiliationns data.

    Args:
        raw_affiliations_df (dataframe): The initial data of raw affiliations.
        country_unkept_affil_file_path (path): The full path to the data of raw \
        affiliations that should be dropped from the initial data of raw affiliations.
        cols_list (list): The names of useful columns.
    Returns:
        (dataframe): The cleaned data of raw affiliations.
    """
    countries_col, raw_affil_col, affiliation_col = cols_list
    unkept_affiliations_dict = pd.read_excel(country_unkept_affil_file_path, sheet_name=None)
    unkept_country_list = list(unkept_affiliations_dict.keys())

    new_raw_affiliations_df = pd.DataFrame()
    for country, country_raw_affil_df in raw_affiliations_df.groupby(countries_col):
        if country in unkept_country_list:
            unkept_affiliations_list = unkept_affiliations_dict[country][raw_affil_col].to_list()
            unkept_affiliations_list_mod = [affiliation.translate(bm_pg.SYMB_CHANGE).strip()
                                            for affiliation in unkept_affiliations_list]
            for idx_row, affil_row in country_raw_affil_df.iterrows():
                affil_row_list = [x.strip() for x in affil_row[affiliation_col].split(";")]
                affil_row_list_mod = [x.translate(bm_pg.SYMB_CHANGE).lower() for x in affil_row_list]
                for unkept_affil in unkept_affiliations_list_mod:
                    if unkept_affil.lower() in affil_row_list_mod:
                        affil_idx = affil_row_list_mod.index(unkept_affil.lower())
                        del affil_row_list_mod[affil_idx]
                        del affil_row_list[affil_idx]
                        if len(affil_row_list)>1:
                            country_raw_affil_df.loc[idx_row, affiliation_col] = "; ".join(affil_row_list)
                        elif len(affil_row_list)==1:
                            country_raw_affil_df.loc[idx_row, affiliation_col] = affil_row_list[0]
                        else:
                            country_raw_affil_df.loc[idx_row, affiliation_col] = bm_pg.EMPTY
        new_raw_affiliations_df = concat_dfs([new_raw_affiliations_df, country_raw_affil_df])
    return new_raw_affiliations_df


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


def _enhance_raw_affiliations_data(init_raw_addr_df, ids_dicts_list, co_cols_dic):
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
                'countries_col', 'address_col', 'affiliations_col']
    (hash_id_col, pub_id_col, doi_col, address_id_col, countries_col,
     address_col, affiliations_col) = [co_cols_dic[key] for key in col_keys]

    init_ordered_columns = [pub_id_col, address_id_col, countries_col, address_col,
                            affiliations_col]
    final_ordered_columns = [hash_id_col, pub_id_col, doi_col, address_id_col, countries_col,
                             address_col, affiliations_col]

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


def _build_norm_raw_affil_data(raw_addr_dfs_list, affil_params_dics_list, co_cols_dic,
                               ids_dicts_list, print_params, progress_param=None):
    if progress_param:
        progress_callback, _init_progress, _final_progress = progress_param

    # Setting useful column names
    col_keys = ['address_col', 'address_id_col', 'affiliations_col',
                'countries_col', 'final_pub_id_col', 'raw_affil_col']
    (address_col, address_id_col, affiliations_col, countries_col,
     final_pub_id_col, raw_affil_col) = [co_cols_dic[key] for key in col_keys]

    # Setting parameters values from args
    institute_pub_raw_addr_df, empty_raw_addr_df, keep_norm_affil_df = raw_addr_dfs_list
    dedup_affil_params_dic, co_affil_params_dic = affil_params_dics_list
    country_unkept_affil_file_path = co_affil_params_dic['unkept_affils_file_path']

    # Building countries, normalized affiliations and remaining raw-addresses data
    return_tup = bp_build_norm_and_raw_affils(institute_pub_raw_addr_df, affil_params_dic=dedup_affil_params_dic,
                                              progress_param=progress_param)
    sub_countries_df, sub_norm_affil_df, sub_raw_addr_df, wrong_affil_types_dict = return_tup

    # Initializing returned parameters
    norm_affil_df, raw_addr_df = keep_norm_affil_df, empty_raw_addr_df
    raw_addr_status = False
    if not wrong_affil_types_dict:
        if progress_param:
            inter_progress_1 = _init_progress + (_final_progress - _init_progress) * 0.75
            progress_callback(inter_progress_1)
        step_str = ("      - Data of countries, of normalized affiliations and of remaining raw-affiliations\n"
                    "        built for addresses with previously remaining raw-affiliations")
        print_step_text(step_str, print_params)

        # Adding countries column to normalized affiliations and remaining raw-addresses data
        norm_cols_list = [final_pub_id_col, address_id_col, countries_col, affiliations_col]
        sub_norm_affil_df = _copy_dg_col_to_df(sub_norm_affil_df, sub_countries_df, norm_cols_list, countries_col)

        raw_cols_list = [final_pub_id_col, address_id_col, countries_col, address_col, affiliations_col]
        sub_raw_addr_df = _copy_dg_col_to_df(sub_raw_addr_df, sub_countries_df, raw_cols_list, countries_col)
        if progress_param:
            inter_progress_2 =  _init_progress + (_final_progress - _init_progress) * 0.9
            progress_callback(inter_progress_2)
        step_str = ("      - Countries column added to the data of normalized affiliations\n"
                    "        and to the data of remaing raw-affiliations")
        print_step_text(step_str, print_params)

        # Removing unkept affiliations from remaining raw-addresses data
        cols_list = [countries_col, raw_affil_col, affiliations_col]
        sub_raw_addr_df = _clean_unkept_affil(sub_raw_addr_df, country_unkept_affil_file_path, cols_list)
        print_step_text("      - Unkept addresses-parts removed from the data of remaining raw-affiliations",
                        print_params)
        sub_raw_addr_df = _enhance_raw_affiliations_data(sub_raw_addr_df, ids_dicts_list, co_cols_dic)
        print_step_text("      - Data of the remaining raw-affiliations enhanced with complementary info",
                        print_params)

        raw_addr_df = sub_raw_addr_df.copy()
        if not empty_raw_addr_df.empty:
            empty_raw_addr_df = empty_raw_addr_df[sub_raw_addr_df.columns]
            raw_addr_df = concat_dfs([empty_raw_addr_df, sub_raw_addr_df])
        raw_addr_df = raw_addr_df.sort_values(by=[final_pub_id_col, address_id_col])
        raw_addr_status = raw_addr_df[raw_addr_df[affiliations_col]!=bm_pg.EMPTY].empty
        print_step_text("      - Existing data of raw-affiliations updated", print_params)

        norm_affil_df = sub_norm_affil_df.copy()
        if not keep_norm_affil_df.empty:
            norm_affil_df = concat_dfs([keep_norm_affil_df, sub_norm_affil_df])
        norm_affil_df = norm_affil_df.sort_values(by=[final_pub_id_col, address_id_col])
        print_step_text("      - Existing data of normalized affiliations updated", print_params)
    if progress_param:
        progress_callback(_final_progress)
    return norm_affil_df, raw_addr_df, wrong_affil_types_dict, raw_addr_status


def _build_addresses_to_normalize(addr_params, co_cols_dic, addr_paths,
                                  verbose=False, progress_param=None):

    # Setting useful column names
    col_keys = ['pub_id_col', 'address_id_col', 'affiliations_col',
                'countries_col', 'final_pub_id_col']
    (pub_id_col, address_id_col, affiliations_col, countries_col,
     final_pub_id_col) = [co_cols_dic[key] for key in col_keys]
    norm_cols_list = [final_pub_id_col, address_id_col, countries_col, affiliations_col]

    # Setting parameters valu from 'addr_params'
    (corpus_year, print_params, institute, org_tup, wf_path,
     parsing_filenames_dict) = addr_params
    final_results_path, norm_affil_file_path, raw_affil_file_path = addr_paths

    # Building data of all addresses of Institute's publications from parsing addresses data
    print_step_text("  - Building data of all addresses of Institute's publications...", print_params)
    sub_addr_params = [corpus_year, institute, org_tup, wf_path,
                       parsing_filenames_dict, final_results_path]
    return_tup = build_institute_addresses_df(sub_addr_params, verbose=verbose,
                                              progress_param=progress_param)
    institute_pub_raw_addr_df = return_tup[2]
    print_step_text("      - Data of all addresses of Institute's publications selected", print_params)

    sub_institute_pub_raw_addr_df = institute_pub_raw_addr_df.copy()
    empty_raw_addr_df = pd.DataFrame()
    keep_norm_affil_df = pd.DataFrame(columns=norm_cols_list)
    if raw_affil_file_path.is_file():
        print_step_text("  - Selecting data of addresses with affiliations remaining to be normalized...", print_params)
        # Reading the previously built data of remaining raw-addresses
        init_raw_addr_df = pd.read_excel(raw_affil_file_path)

        empty_raw_addr_df = init_raw_addr_df[init_raw_addr_df[affiliations_col]==bm_pg.EMPTY]
        empty_pub_ids = empty_raw_addr_df[pub_id_col].to_list()
        empty_address_ids = empty_raw_addr_df[address_id_col].to_list()
        empty_pub_addr_tups = list(tuple(zip(empty_pub_ids, empty_address_ids)))

        empty_rows = []
        for idx, row in institute_pub_raw_addr_df.iterrows():
            pub_addr_tup = (row[pub_id_col], row[address_id_col])
            if pub_addr_tup in empty_pub_addr_tups:
                empty_rows.append(idx)
        sub_institute_pub_raw_addr_df = institute_pub_raw_addr_df.drop(empty_rows)
        print_step_text("      - Data of addresses with affiliations remaining to be normalized selected",
                        print_params)

        if norm_affil_file_path.is_file():
            # Reading the previously built data of normalized affiliations
            init_norm_affil_df = pd.read_excel(norm_affil_file_path)

            other_raw_addr_df = init_raw_addr_df[init_raw_addr_df[affiliations_col]!=bm_pg.EMPTY]
            other_pub_ids = other_raw_addr_df[pub_id_col].to_list()
            other_address_ids = other_raw_addr_df[address_id_col].to_list()
            other_pub_addr_tups = list(tuple(zip(other_pub_ids, other_address_ids)))

            other_rows = []
            for idx, row in init_norm_affil_df.iterrows():
                pub_addr_tup = (row[pub_id_col], row[address_id_col])
                if pub_addr_tup in other_pub_addr_tups:
                    other_rows.append(idx)
            keep_norm_affil_df = init_norm_affil_df.drop(other_rows)
            print_step_text("      - Data of normalized affiliations to be kept selected",
                            print_params)
    addr_dfs_list = [sub_institute_pub_raw_addr_df, empty_raw_addr_df, keep_norm_affil_df]

    return addr_dfs_list


def _set_co_files_params(wf_path, corpus_year, final_results_path):
    """Sets files, folders and full paths for the process of coupling analysis
    for a given corpus.

    Args:
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
    affils_analysis_folder_alias = bm_pg.ARCHI_YEAR["institutions analysis"]
    norm_affils_file_base_alias = bm_pg.ARCHI_YEAR["norm inst file name"]
    raw_affils_file_base_alias = bm_pg.ARCHI_YEAR["raw inst file name"]

    # Setting useful file names
    hash_id_file = f'{corpus_year} {bm_pg.ARCHI_YEAR["hash_id file name"]}'
    norm_affils_file = norm_affils_file_base_alias + '.xlsx'
    raw_affils_file = raw_affils_file_base_alias + '.xlsx'

    # Setting useful paths
    year_folder_path = wf_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    affils_analysis_folder_path = analysis_folder_path / Path(affils_analysis_folder_alias)
    addresses_to_correct_path = affils_analysis_folder_path / Path(addresses_to_correct_file_alias)

    year_final_results_path = final_results_path / Path(corpus_year)
    hash_ids_path = year_final_results_path / Path(hash_id_folder_alias) / Path(hash_id_file)
    final_affils_analysis_folder_path = year_final_results_path / Path(affils_analysis_folder_alias)
    norm_affil_file_path = final_affils_analysis_folder_path / Path(norm_affils_file)
    raw_affil_file_path = final_affils_analysis_folder_path / Path(raw_affils_file)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(affils_analysis_folder_path):
        os.makedirs(affils_analysis_folder_path)
    if not os.path.exists(final_affils_analysis_folder_path):
        os.makedirs(final_affils_analysis_folder_path)

    files_list = [norm_affils_file, raw_affils_file]
    folders_list = [analysis_folder_alias, affils_analysis_folder_alias]
    paths_list = [analysis_folder_path, affils_analysis_folder_path, hash_ids_path,
                  addresses_to_correct_path, norm_affil_file_path, raw_affil_file_path]
    return files_list, folders_list, paths_list


def _built_co_pub_identifiers_data(ids_params, hash_ids_path, identifiers_cols):
    """Builds data of publications identifiers specific to a given deduplicated corpus parsing.

    Args:
        ids_params (list): Composed of the 4 digits year of the corpus, \
        of the dict giving the name of the parsing file for each parsed item \
        and of the full path to the folder where final results are saved.
        hash_ids_path (path): The full path to the hash-IDs file.
        identifiers_cols (list): The column names of the publications identifiers.
    Returns:
        (list): The list composed of the data (dict) of database ID per publication ID \
        and the data (dict) of the DOI per publication ID.
    """
    # Setting parameters values from args
    hash_id_col, pub_id_col, doi_col = identifiers_cols

    # Building the data of hash-ID per publication-ID
    hash_ids_df = pd.read_excel(hash_ids_path)
    hash_ids_dict = dict(zip(hash_ids_df[pub_id_col], hash_ids_df[hash_id_col]))

    # Building the data of DOI per publication-ID
    dedup_read_params = ids_params
    dedup_parsing_dict = read_final_dedup(dedup_read_params)
    pub_parsing_key = bm_pg.PARSING_KEYS_DIC['parsing_pub']
    parsing_pub_df = dedup_parsing_dict[pub_parsing_key]
    dois_dict = dict(zip(parsing_pub_df[pub_id_col], parsing_pub_df[doi_col]))
    ids_dicts_list = [hash_ids_dict, dois_dict]
    return ids_dicts_list


def coupling_analysis(params_list, progress_callback=None, verbose=False):
    """Performs the analysis of countries and authors affiliations of Institute publications 
    of a corpus.

    This is done through the following steps:

    1. Builds the addresses remaining to be normalized among only the addresses related to the \
    publications of the Institute through the `_build_addresses_to_normalize` internal function.
    2. Builds the data of normalized affiliations, of raw affiliations and of the wrong \
    affiliations types through the `_build_norm_raw_affil_data` internal function.
    3. Saves the data of normalized affiliations and the data of raw affiliations through the \
    `save_formatted_df_to_xlsx` function imported from the `bmfuncts.format_files` module.
    4. If no wrong affiliations type is found and no raw addresses remains:

        - Builds the publications statistics data per affiliations through the \
        `_build_and_save_affiliations_stat` internal function after setting the list of \
        Institute's publications IDs through the `build_pub_ids_dict` function \
        imported from  the `bmfuncts.read_final_results` module.

        - Builds the publications statistics data per country and per continent through \
        the `_build_and_save_geo_stat` internal function.

        - Saves the results of this analysis for the case 'datatype' through the \
        `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        params_list (list): The list composed of the 4 digits year of the corpus (str), \
        of the print parameters (list), of the Institute's name (str), \
        of the org_tup (tup) that contains parameters of Institute's organization, \
        of the full path to working folder (path), \
        of the data combination type of corpuses databases (str), \
        of the dict giving the name of the parsing file for each parsed item, \
        of the dict giving the full paths to the Institute's files to use for \
        authors' affiliations parsing at parsing deduplication step \
        and of the dict giving the full paths to the Institute's complementary files \
        to use for authors' affiliations parsing at coupling analysis step.
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
    Note:
        TO DO: Split in sub-functions.
    """
    # Setting parameters values from params_list
    (corpus_year, print_params, institute, org_tup, wf_path, datatype, parsing_filenames_dict,
     dedup_affil_params_dic, co_affil_params_dic) = params_list

    # Setting useful files parameters
    final_results_path = set_results_folder_path(wf_path, datatype)
    files_list, folders_list, paths_list = _set_co_files_params(wf_path, corpus_year,
                                                                final_results_path)
    norm_affil_file, raw_addr_file = files_list
    (analysis_folder_path, affils_analysis_folder_path, hash_ids_path,
     addresses_to_correct_path, norm_affil_file_path, raw_affil_file_path) = paths_list

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
    ids_params = [corpus_year, parsing_filenames_dict, final_results_path]
    identifiers_cols = [hash_id_col, pub_id_col, doi_col]
    ids_dicts_list = _built_co_pub_identifiers_data(ids_params, hash_ids_path, identifiers_cols)

    # Correcting false addresses in deduplication-parsing data as indicated by the user
    print_step_text("\nCorrecting false addresses...", print_params)
    dedup_params = [corpus_year, print_params, wf_path, parsing_filenames_dict,
                    dedup_affil_params_dic, final_results_path, addresses_to_correct_path]
    correct_status = correct_dedup(dedup_params, ids_dicts_list)
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
    print_step_text("\nBuilding data of affiliations remaining to be normalized...",
                    print_params)
    addr_params = [corpus_year, print_params, institute, org_tup, wf_path,
                   parsing_filenames_dict]
    addr_paths = [final_results_path, norm_affil_file_path, raw_affil_file_path]
    addr_dfs_list = _build_addresses_to_normalize(addr_params, co_cols_dic, addr_paths,
                                                  verbose=verbose, progress_param=progress_param)
    institute_pub_raw_addr_df, empty_raw_addr_df, keep_norm_affil_df = addr_dfs_list
    print_step_text("  - Data of affiliations remaining to be normalized built",
                    print_params)
    if institute_pub_raw_addr_df.empty:
        print_step_text("  - No affiliation remains to be normalized", print_params)
    else:
        print_step_text("  - Affiliations remain to be normalized", print_params)
    if progress_callback:
        progress_callback(inter_progress_2)
        inter_progress_3 = init_progress + (final_progress - init_progress) * 0.8
        progress_param = (progress_callback, inter_progress_2, inter_progress_3)

    print_step_text("\nTrying to built affiliations stat and geographical stat...", print_params)
    if not institute_pub_raw_addr_df.empty:
        print_step_text("  - Building normalized-affiliations data and remaining raw-affiliations data...",
                        print_params)
        affil_params_dics_list = [dedup_affil_params_dic, co_affil_params_dic]
        return_tup = _build_norm_raw_affil_data(addr_dfs_list, affil_params_dics_list, co_cols_dic,
                                                ids_dicts_list, print_params, progress_param=progress_param)
        norm_affil_df, raw_addr_df, wrong_affil_types_dict, raw_addr_status = return_tup
        print_step_text("      - Normalized-affiliations data and remaining raw-affiliations built",
                        print_params)
    else:
        raw_addr_status = True
        wrong_affil_types_dict = {}
        norm_affil_df = keep_norm_affil_df.copy()
        raw_addr_df = empty_raw_addr_df.copy()
        print_step_text("  - Normalized-affiliations data unchanged...", print_params)
    countries_df = norm_affil_df[[final_pub_id_col, address_id_col, countries_col]]

    # Saving formatted df of normalized and raw affiliations
    affils_df_title = bm_pg.DF_TITLES_LIST[9]
    sheet_name = 'Norm ' + corpus_year
    save_formatted_df_to_xlsx(affils_analysis_folder_path, norm_affil_file,
                              norm_affil_df, affils_df_title, sheet_name)
    affils_df_title = bm_pg.DF_TITLES_LIST[16]
    sheet_name = 'Raw ' + corpus_year
    save_formatted_df_to_xlsx(affils_analysis_folder_path, raw_addr_file,
                              raw_addr_df, affils_df_title, sheet_name)
    step_text = "      - Normalized-affiliations data and of raw-affiliations data saved "
    if raw_addr_status:
        step_text += "with no raw-affiliations"
        remove_file(addresses_to_correct_path)
        step_text += "\n      - File for correcting addresses by the user delated"
    else:
        step_text += "with remaining raw-affiliations"
        step_text += "\n      - File for correcting addresses by the user available"
    print_step_text(step_text, print_params)

    if not wrong_affil_types_dict and raw_addr_status:
        # Building and saving affiliations stat data
        if progress_callback:
            inter_progress_4 = init_progress + (final_progress - init_progress) * 0.9
            progress_param = (progress_callback, inter_progress_3, inter_progress_4)
        pub_doctype_cols_list = [final_pub_id_col, final_doctype_col]
        pub_ids_dict = build_pub_ids_dict(final_results_path, corpus_year, pub_doctype_cols_list)
        affil_types_file_path = dedup_affil_params_dic['affil_types_file_path']
        sub_paths_list = [final_results_path, affils_analysis_folder_path, affil_types_file_path]
        affils_stat_params = [institute, corpus_year, print_params]
        build_and_save_affiliations_stat(norm_affil_df, sub_paths_list, pub_ids_dict,
                                         affils_stat_params, progress_param=progress_param)

        # Building and saving geo stat data
        geo_stat_params = [corpus_year, print_params, institute]
        geo_analysis_folder_name = build_and_save_geo_stat(geo_stat_params, countries_df,
                                                           norm_affil_df, analysis_folder_path)
        if progress_callback:
            inter_progress_5 = init_progress + (final_progress - init_progress) * 0.98
            progress_callback(inter_progress_5)

        # Saving coupling analysis as final result
        status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
        results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
        save_keys_list = ["countries", "continents", "affiliations", "institute_country"]
        for key in save_keys_list:
            results_to_save_dict[key] = True
        save_params_list = [corpus_year, institute, org_tup, wf_path, datatype]
        _institute_country = bm_ig.INSTITUTES_COUNTRY_DICT[institute]
        save_final_results(save_params_list, results_to_save_dict,
                           institute_country=_institute_country)
    else:
        geo_analysis_folder_name = ""

    return_folders_list = folders_list + [geo_analysis_folder_name]
    return_paths_list = [addresses_to_correct_path, raw_affil_file_path]
    return_tup = (wrong_affil_types_dict, raw_addr_status, return_folders_list, return_paths_list)
    if progress_callback:
        progress_callback(final_progress)
    return return_tup
