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
from bmfuncts.correct_dedup import initialize_addresses_to_correct_file
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.read_final_results import build_pub_ids_lists
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import concat_dfs


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
        institutions that should be droped from the initial data of raw institutions.
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


def _enhance_raw_institutions_data(init_raw_institutions_df, ids_dicts_list, co_cols_dic):
    
    # Setting useful column names aliases
    col_keys = ['hash_id_col','pub_id_col', 'doi_col', 'address_id_col',
                'countries_col', 'address_col', 'institutions_col']
    (hash_id_col, pub_id_col, doi_col, address_id_col, countries_col,
     address_col, institutions_col) = [co_cols_dic[key] for key in col_keys]
    
    init_ordered_columns = [pub_id_col, address_id_col, countries_col, address_col,
                            institutions_col] 
    init_raw_institutions_df = init_raw_institutions_df[init_ordered_columns]
    final_ordered_columns = [hash_id_col, pub_id_col, doi_col, address_id_col, countries_col,
                             address_col, institutions_col]

    # Setting hash-ID and DOI per publication data from args
    hash_ids_dict, dois_dict = ids_dicts_list
    
    data = []
    for _, row in init_raw_institutions_df.iterrows():
        init_values_list = row.T.to_list()
        pub_id_str = row[pub_id_col]
        hash_id = hash_ids_dict[pub_id_str]
        pub_id_int = int(pub_id_str[5:])
        doi = dois_dict[pub_id_int]
        data.append([hash_id, pub_id_str, doi] + init_values_list[1:])
    raw_institutions_df = pd.DataFrame(data, columns=final_ordered_columns)
    return raw_institutions_df


def _build_and_save_norm_raw_dfs(corpus_year, inst_pub_addresses_df,
                                 co_cols_dic, files_list, sub_paths_list, ids_dicts_list,
                                 progress_param=None, verbose=False):
    """Builds the data of countries, normalized institutions and raw institutions.

    This is done through the following steps:

    1. Builds dataframes of countries, normalized institutions and raw institutions \
    through the `build_norm_raw_institutions` function imported from the `BiblioParsing \
    package` imported as bp, using 'inst_pub_addresses_df' dataframe and specific files \
    for this function; in these dataframes, each row contains:

        - A publication IDs
        - The index of an address of the publication addresses 
        - The country of the given address
        - The list of the normalized institutions or the list of the raw institutions \
        for the given address, depending on the built dataframe.  

    2. Completes the normalized institutions and raw institutions dataframes with country \
    information by `_copy_dg_col_to_df` internal function.
    3. Modifyes the publications IDs by `set_year_pub_id` function imported from \
    `bmfuncts.useful_functs` in the 3 dataframes.
    4. Removes the institutions not to be considered through the `_clean_unkept_affil` \
    internal function.
    5. Saves the normalized institutions and raw institutions dataframes through the \
    `save_formatted_df_to_xlsx` function imported from the `bmfuncts.format_files` module.

    Args:
        corpus_year (str): 4 digits year of the corpus.
        inst_pub_addresses_df (dataframe): Data of addresses related only to publications \
        of the Institute.
        co_cols_dic (dict): The dict giving the col names for coupling analysis process.
        files_list (list): The list of file names as built by the `_set_co_files_params` \
        internal function.
        sub_paths_list (list): The list of paths as built by the `_set_co_files_params` \
        internal function except the first item of the bulit list.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
        verbose (bool): Status of prints (default = False).
    Returns:
        (tup): (Data with one row per country for each publication ID, Data with one row \
        per address with attached institutions list  for each publication ID, \
        The full path (path) to the file of countries-affiliations data, \
        The dict keyed by countries and valued by the list of normalised affiliation types \
        to be corrected, The status (bool) of the raw-affiliations data \
        (True if no remaining raw-affiliations)).
    """
    print("    Building normalized and raw affiliations data...")

    # Setting useful column names
    col_keys = ['pub_id_col', 'address_col', 'address_id_col', 'institutions_col',
                'countries_col', 'final_pub_id_col', 'raw_affil_col']
    (pub_id_col, address_col, address_id_col, institutions_col,
     countries_col, final_pub_id_col, raw_affil_col) = [co_cols_dic[key] for key in col_keys]

    # Setting parameters values from 'files_list' and 'sub_paths_list'
    country_towns_file, norm_inst_file, raw_inst_file = files_list
    (institutions_folder_path, inst_analysis_folder_path, inst_types_file_path,
     country_affil_file_path, country_unkept_affil_file_path) = sub_paths_list

    # Setting parameters from optional arg
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        inter_progress_1 = init_progress + (final_progress - init_progress) * 0.90
        progress_callback(init_progress)

    # Building countries, normalized institutions and not normalized institutions data
    file_path_0 = inst_types_file_path
    file_path_1 = country_affil_file_path
    file_path_2 = country_towns_file
    file_path_3 = institutions_folder_path
    inter_progress_param = None
    if progress_param:
        inter_progress_param = (progress_callback, init_progress, inter_progress_1)
    return_tup = bp.build_norm_raw_institutions(inst_pub_addresses_df,
                                                inst_types_file_path=file_path_0,
                                                country_affiliations_file_path=file_path_1,
                                                country_towns_file=file_path_2,
                                                country_towns_folder_path=file_path_3,
                                                verbose=False,
                                                progress_param=inter_progress_param)
    countries_df, norm_institutions_df, raw_institutions_df, wrong_affil_types_dict = return_tup
    raw_institutions_status = False
    if not wrong_affil_types_dict:
        if progress_param:
            progress_callback(inter_progress_1)
        print("      - Data of countries, of normalized affiliations "
              "and of raw affiliations built")

        # Adding countries column to normalized institutions and not normalized institutions data
        norm_cols_list = [final_pub_id_col, address_id_col, countries_col, institutions_col]
        norm_institutions_df = _copy_dg_col_to_df(norm_institutions_df, countries_df,
                                                  norm_cols_list, countries_col)
        raw_cols_list = [final_pub_id_col, address_id_col, countries_col,
                         address_col, institutions_col]
        raw_institutions_df = _copy_dg_col_to_df(raw_institutions_df, countries_df,
                                                 raw_cols_list, countries_col)
        print("      - Countries column added to data of normalized affiliations "
              "and to data of raw affiliations")
        if progress_param:
            inter_progress_2 = inter_progress_1 + (final_progress - inter_progress_1) * 0.25
            progress_callback(inter_progress_2)

        # Removing unkept institutions from 'raw_institutions_df'
        cols_list = [countries_col, raw_affil_col, institutions_col]
        raw_institutions_df = _clean_unkept_affil(raw_institutions_df,
                                                  country_unkept_affil_file_path,
                                                  cols_list)
        raw_institutions_df = raw_institutions_df.sort_values(by=[pub_id_col,
                                                                  address_id_col])
        raw_institutions_df = _enhance_raw_institutions_data(raw_institutions_df, ids_dicts_list, co_cols_dic)
        temp_sub_df = raw_institutions_df[raw_institutions_df[institutions_col]!=bp.EMPTY]
        raw_institutions_status = temp_sub_df.empty
        print("      - Unkept addresses-parts removed from data of raw affiliations")
        if progress_param:
            inter_progress_3 = inter_progress_1 + (final_progress - inter_progress_1) * 0.75
            progress_callback(inter_progress_3)

        # Saving formatted df of normalized and raw institutions
        inst_df_title = bm_pg.DF_TITLES_LIST[9]
        sheet_name = 'Norm Inst ' + corpus_year
        save_formatted_df_to_xlsx(inst_analysis_folder_path, norm_inst_file,
                                  norm_institutions_df, inst_df_title, sheet_name)
        inst_df_title = bm_pg.DF_TITLES_LIST[16]
        sheet_name = 'Raw Inst ' + corpus_year
        save_formatted_df_to_xlsx(inst_analysis_folder_path, raw_inst_file,
                                  raw_institutions_df, inst_df_title, sheet_name)
        print_text = ("      - Data of normalized affiliations and of "
                      "raw-affiliations saved ")
        if raw_institutions_status:
            print_text += "with empty raw-affiliations"
        else:
            print_text += "with remaining raw-affiliation"
        print(print_text)
        if progress_param:
            progress_callback(final_progress)
    return countries_df, norm_institutions_df, wrong_affil_types_dict, raw_institutions_status


def _set_co_files_params(institute, wf_path, corpus_year, final_results_path):
    """Sets IFs specific file and folder 
    
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

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(inst_analysis_folder_path):
        os.makedirs(inst_analysis_folder_path)

    files_list = [country_towns_file, norm_inst_file, raw_inst_file]
    folders_list = [analysis_folder_alias, inst_analysis_folder_alias]
    paths_list = [analysis_folder_path, institutions_folder_path,
                  inst_analysis_folder_path, inst_types_file_path,
                  country_affil_file_path, country_unkept_affil_file_path, hash_ids_path]
    return files_list, folders_list, paths_list


def _built_pub_identifiers_data(wf_path, corpus_year, final_results_path, hash_ids_path, co_cols_dic):
    # Setting useful column names aliases
    col_keys = ['hash_id_col', 'pub_id_col', 'doi_col']
    (hash_id_col, pub_id_col, doi_col) = [co_cols_dic[key] for key in col_keys]

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
    of the 'year' corpus.

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
    IDs list through the `build_pub_ids_lists` function imported from the `bmfuncts.useful_functs` \
    module.
    5. Builds the publications statistics dataframes per country and per continent through \
    the `_build_and_save_geo_stat` internal function.
    6. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        params_list (list):  The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path), the data combination type \
        of corpuses databases (str) and the 4 digits year of the corpus (str).
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).
    Returns:
        (tup): (The full path (path) to the folder where results of coupling analysis are saved, \
        The full path (path) to folder where the results of the geographical analysis are saved, \
        The full path (path) to folder where the results of the collaborations analysis are saved, \
        The full path (path) to the file of countries-affiliations data, \
        The dict keyed by countries and valued by the list of normalised affiliation types \
        to be corrected).
    """
    # Setting parameters values from params_list
    institute, org_tup, wf_path, datatype, corpus_year = params_list

    # Setting input-data path
    final_results_path = set_results_folder_path(wf_path, datatype)

    # Setting useful parameters lists
    dedup_params = [institute, wf_path, datatype, corpus_year]
    addresses_params = [institute, org_tup, wf_path, corpus_year, final_results_path]

    # Getting item_filename_dict
    config_tup = set_user_config(wf_path, corpus_year, bm_pg.BDD_LIST)
    item_filename_dict = config_tup[2]

    # Setting useful paths
    files_list, folders_list, paths_list = _set_co_files_params(institute, wf_path,
                                                                corpus_year, final_results_path)
    analysis_folder_name, inst_analysis_folder_name = folders_list
    analysis_folder_path = paths_list[0]
    (inst_analysis_folder_path, inst_types_file_path,
     country_affil_file_path) = paths_list[2:5]
    hash_ids_path = paths_list[-1]

    # Setting useful column names
    co_cols_dic = _set_co_cols_dic(institute, org_tup)
    final_pub_id_col = co_cols_dic['final_pub_id_col']
    final_doctype_col = co_cols_dic['final_doctype_col']

    # Building data of hash-ID and DOI per publication
    ids_dicts_list = _built_pub_identifiers_data(wf_path, corpus_year, final_results_path,
                                                 hash_ids_path, co_cols_dic)

    # Correcting false addresses in deduplication-parsing data as indicated by the user
    print(f"\nCorrecting false addresses...")
    addresses_to_correct_path, correct_status = correct_dedup(dedup_params, final_results_path,
                                                              item_filename_dict, ids_dicts_list)
    if correct_status:
        print("\n    False addresses in deduplication-parsing data corrected")
    else:
        print("\n    No correction of false addresses in deduplication-parsing data")
    progress_param = None
    if progress_callback:
        init_progress = 5
        inter_progress_1 = 15
        progress_param = (progress_callback, init_progress, inter_progress_1)
        progress_callback(init_progress)

    # Selecting addresses of Institute's publications only from parsing addresses data
    print(f"\nBuilding data of addresses of Institute's publications...")
    inst_pub_addresses_df = build_institute_addresses_df(addresses_params, verbose=False,
                                                         progress_param=progress_param)
    print("  - Addresses of Institute's publications selected")
    if progress_callback:
        progress_callback(inter_progress_1)
        inter_progress_2 = 83
        progress_param = (progress_callback, inter_progress_1, inter_progress_2)

    print(f"\nTrying to built affiliations and geographical statistics...")
    sub_paths_list = paths_list[1:6]
    return_tup = _build_and_save_norm_raw_dfs(corpus_year, inst_pub_addresses_df, co_cols_dic,
                                              files_list, sub_paths_list, ids_dicts_list,
                                              progress_param=progress_param,
                                              verbose=verbose)
    (countries_df, norm_institutions_df,
     wrong_affil_types_dict, raw_institutions_status) = return_tup
    if not wrong_affil_types_dict and raw_institutions_status:
        # Building and saving inst stat dataframe
        if progress_callback:
            progress_callback(inter_progress_2)
            inter_progress_3 = 93
            progress_param = (progress_callback, inter_progress_2, inter_progress_3)
        pub_doctype_cols_list = [final_pub_id_col, final_doctype_col]
        pub_ids_lists = build_pub_ids_lists(final_results_path, corpus_year, pub_doctype_cols_list)
        build_and_save_institutions_stat(institute, norm_institutions_df,
                                         inst_types_file_path,
                                         inst_analysis_folder_path, corpus_year,
                                         pub_ids_lists,
                                         progress_param=progress_param)
        print("    Affiliations statistics built and saved")

        # Setting Institute's geo
        institute_geo_dict = {'country'  : bm_ig.INSTITUTES_COUNTRY_DICT[institute],
                              'continent': bm_ig.INSTITUTES_CONTINENT_DICT[institute],
                              'norm_name': institute.upper() + " Rto",
                             }

        # Building and saving geo stat dataframes
        return_tup = build_and_save_geo_stat(countries_df, norm_institutions_df,
                                             institute_geo_dict, analysis_folder_path,
                                             corpus_year)
        geo_analysis_folder_name = return_tup
        if verbose:
            print("        Geo statistics built and saved")
        if progress_callback:
            progress_callback(98)

        # Saving coupling analysis as final result
        status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
        results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
        save_keys_list = ["countries", "continents", "institutions", "institute_country"]
        for key in save_keys_list:
            results_to_save_dict[key] = True
        _ = save_final_results(params_list, results_to_save_dict,
                               institute_country=institute_geo_dict['country'])
    else:
        analysis_folder_name, geo_analysis_folder_name, inst_analysis_folder_name = ("", "", "")
        message = initialize_addresses_to_correct_file(addresses_to_correct_path, corpus_year)
        print(message)

    if progress_callback:
        progress_callback(100)
    return_tup = (analysis_folder_name, geo_analysis_folder_name, inst_analysis_folder_name,
                  country_affil_file_path, wrong_affil_types_dict, raw_institutions_status,
                  addresses_to_correct_path)
    return return_tup
