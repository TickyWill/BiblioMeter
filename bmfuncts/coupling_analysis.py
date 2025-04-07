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
import bmfuncts.pub_globals as pg
from bmfuncts.build_geo_stat import build_and_save_geo_stat
from bmfuncts.build_institutions_stat import build_and_save_institutions_stat
from bmfuncts.build_pub_addresses import build_institute_addresses_df
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import set_saved_results_path

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
            unkept_institutions_list_mod = [institution.translate(bp.SYMB_CHANGE)
                                            for institution in unkept_institutions_list]
            for idx_row, inst_row in country_raw_inst_df.iterrows():
                inst_row_list = [x.strip() for x in inst_row[institution_col].split(";")]
                for unkept_inst in unkept_institutions_list_mod:
                    if unkept_inst in inst_row_list:
                        inst_row_list.remove(unkept_inst)
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


def _build_and_save_norm_raw_dfs(institute, inst_pub_addresses_df,
                                 inst_analysis_folder_path, year,
                                 final_pub_id, paths_tup,
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
        institute (str): Institute name.
        inst_pub_addresses_df (dataframe): Data of addresses related only to publications \
        of the Institute.
        inst_analysis_folder_path (path): The full path to the folder wher the build data \
        are saved.
        year (str): 4 digits year of the corpus.
        final_pub_id (str): Final name of publication ID columns. 
        paths_tup (tup): (the full path to the folder where useful institutions info \
        are stored, the full path to the file of institutions types definition).
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
        verbose (bool): Status of prints (default = False).
    Returns:
        (tup): (Data with one row per country for each publication ID, Data with one row \
        per address with attached institutions list  for each publication ID, \
        The full path (path) to the file of countries-affiliations data, \
        The dict keyed by countries and valued by the list of normalyzed affiliation types \
        to be corrected).
    """
    print("    Building normalized and raw affiliations data...")

    # Setting local parameters
    xlsx_extent = ".xlsx"

    # Setting parameters from args
    institutions_folder_path, inst_types_file_path = paths_tup

    # Setting useful column names aliases
    pub_id_alias = bp.COL_NAMES['pub_id']
    address_alias = bp.COL_NAMES['address'][2]
    idx_address_alias = bp.COL_NAMES['institution'][1]
    institutions_alias = bp.COL_NAMES['institution'][2]
    countries_alias = bp.COL_NAMES['country'][2]

    # Setting aliases from globals
    norm_inst_filename_alias = pg.ARCHI_YEAR["norm inst file name"] + xlsx_extent
    raw_inst_filename_alias = pg.ARCHI_YEAR["raw inst file name"] + xlsx_extent
    country_affiliations_file_base_alias = pg.ARCHI_INSTITUTIONS["affiliations_base"]
    country_towns_file_base_alias = pg.ARCHI_INSTITUTIONS["country_towns_base"]
    country_unkept_inst_file_base_alias = pg.ARCHI_INSTITUTIONS["unkept_affil_base"]

    # Setting useful file names
    country_affil_file_alias = institute + "_" + country_affiliations_file_base_alias
    country_towns_file_alias = institute + "_" + country_towns_file_base_alias
    country_unkept_affil_file_alias = institute + "_" + country_unkept_inst_file_base_alias

    # Setting useful paths
    country_affil_file_path = institutions_folder_path / Path(country_affil_file_alias)
    country_unkept_affil_file_path = institutions_folder_path / Path(country_unkept_affil_file_alias)

    # Setting parameters from optional arg
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        inter_progress_1 = init_progress + (final_progress - init_progress) * 0.90
        progress_callback(init_progress)

    # Building countries, normalized institutions and not normalized institutions data
    file_path_0 = inst_types_file_path
    file_path_1 = country_affil_file_path
    file_path_2 = country_towns_file_alias
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
    if not wrong_affil_types_dict:
        if progress_param:
            progress_callback(inter_progress_1)
        if verbose:
            print("      countries, normalized institutions and not-yet-normalized "
                  "institutions data built")

        # Adding countries column to normalized institutions and not normalized institutions data
        norm_cols_list = [final_pub_id, idx_address_alias, countries_alias, institutions_alias]
        norm_institutions_df = _copy_dg_col_to_df(norm_institutions_df, countries_df,
                                                  norm_cols_list, countries_alias)
        raw_cols_list = [final_pub_id, idx_address_alias, countries_alias,
                         address_alias, institutions_alias]
        raw_institutions_df = _copy_dg_col_to_df(raw_institutions_df, countries_df,
                                                 raw_cols_list, countries_alias)
        if verbose:
            print("      Countries column added to normalized institutions "
                  "and not-yet-normalized institutions data")
        if progress_param:
            inter_progress_2 = inter_progress_1 + (final_progress - inter_progress_1) * 0.25
            progress_callback(inter_progress_2)

        # Removing unkept institutions from 'raw_institutions_df'
        raw_affil_col = 'Raw affiliations'
        cols_list = [countries_alias, raw_affil_col, institutions_alias]
        raw_institutions_df = _clean_unkept_affil(raw_institutions_df,
                                                  country_unkept_affil_file_path,
                                                  cols_list)
        raw_institutions_df = raw_institutions_df.sort_values(by=[pub_id_alias,
                                                                  idx_address_alias])
        if verbose:
            print("      Unkept institutions removed from not-yet-normalized "
                  "institutions data")
        if progress_param:
            inter_progress_3 = inter_progress_1 + (final_progress - inter_progress_1) * 0.75
            progress_callback(inter_progress_3)

        # Saving formatted df of normalized and raw institutions
        inst_df_title = pg.DF_TITLES_LIST[9]
        sheet_name = 'Norm Inst ' + year
        save_formatted_df_to_xlsx(inst_analysis_folder_path, norm_inst_filename_alias,
                                  norm_institutions_df, inst_df_title, sheet_name)
        inst_df_title = pg.DF_TITLES_LIST[16]
        sheet_name = 'Raw Inst ' + year
        save_formatted_df_to_xlsx(inst_analysis_folder_path, raw_inst_filename_alias,
                                  raw_institutions_df, inst_df_title, sheet_name)
        if verbose:
            print("      Normalized institutions and not-yet-normalized "
                  "institutions data saved")
        if progress_param:
            progress_callback(final_progress)
    return countries_df, norm_institutions_df, country_affil_file_path, wrong_affil_types_dict


def coupling_analysis(institute, org_tup, bibliometer_path,
                      datatype, year, progress_callback=None, verbose=False):
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
    `_build_and_save_institutions_stat` internal function.
    5. Builds the publications statistics dataframes per country and per continent through \
    the `_build_and_save_geo_stat` internal function.
    6. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year (str): 4 digits year of the corpus.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).
    Returns:
        (tup): (The full path (path) to the folder where results of coupling analysis are saved, \
        The full path (path) to folder where the results of the geographical analysis are saved, \
        The full path (path) to folder where the results of the collaborations analysis are saved, \
        The full path (path) to the file of countries-affiliations data, \
        The dict keyed by countries and valued by the list of normalyzed affiliation types \
        to be corrected).
    """
    # Setting input-data path
    saved_results_path = set_saved_results_path(bibliometer_path, datatype)

    # Setting aliases from globals
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    inst_analysis_folder_alias = pg.ARCHI_YEAR["institutions analysis"]
    institutions_folder_alias = pg.ARCHI_INSTITUTIONS["root"]
    inst_types_file_base_alias = pg.ARCHI_INSTITUTIONS["inst_types_base"]

    # Setting useful file names
    inst_types_file_alias = institute + "_" + inst_types_file_base_alias

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(str(year))
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    inst_analysis_folder_path = analysis_folder_path / Path(inst_analysis_folder_alias)
    institutions_folder_path = bibliometer_path / Path(institutions_folder_alias)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(inst_analysis_folder_path):
        os.makedirs(inst_analysis_folder_path)

    # Setting useful column names aliases
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    final_pub_id_alias = final_col_dic['pub_id']

    # Building only addresses of Institute publications
    progress_param = None
    if progress_callback:
        init_progress = 5
        inter_progress_1 = 15
        progress_param = (progress_callback, init_progress, inter_progress_1)
        progress_callback(init_progress)

    inst_pub_addresses_df = build_institute_addresses_df(institute, org_tup, bibliometer_path,
                                                         saved_results_path, year, verbose=False,
                                                         progress_param=progress_param)
    if verbose:
        print("    Addresses of Institute publications selected.")
    if progress_callback:
        progress_callback(inter_progress_1)
        inter_progress_2 = 83
        progress_param = (progress_callback, inter_progress_1, inter_progress_2)
    paths_tup = (institutions_folder_path, inst_types_file_path)
    return_tup = _build_and_save_norm_raw_dfs(institute, inst_pub_addresses_df,
                                              inst_analysis_folder_path, year,
                                              final_pub_id_alias, paths_tup,
                                              progress_param=progress_param,
                                              verbose=verbose)
    (countries_df, norm_institutions_df,
     country_affil_file_path, wrong_affil_types_dict) = return_tup
    if not wrong_affil_types_dict:
        if verbose:
            print("    normalized and raw institutions built and saved.")

        # Building and saving inst stat dataframe
        if progress_callback:
            progress_callback(inter_progress_2)
            inter_progress_3 = 93
            progress_param = (progress_callback, inter_progress_2, inter_progress_3)
        build_and_save_institutions_stat(institute, norm_institutions_df,
                                         inst_types_file_path,
                                         inst_analysis_folder_path, year,
                                         progress_param=progress_param)
        if verbose:
            print("    Distributed institutions and institutions stat built and saved.")

        # Building and saving geo stat dataframes
        geo_analysis_folder_alias = build_and_save_geo_stat(countries_df, analysis_folder_path,
                                                            year)
        if verbose:
            print("    Geo stat built and saved.")
        if progress_callback:
            progress_callback(98)

        # Saving coupling analysis as final result
        status_values = len(pg.RESULTS_TO_SAVE) * [False]
        results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
        results_to_save_dict["countries"] = True
        results_to_save_dict["continents"] = True
        results_to_save_dict["institutions"] = True
        if_analysis_name = None
        _ = save_final_results(institute, org_tup, bibliometer_path, datatype, year,
                               if_analysis_name, results_to_save_dict, verbose=False)
    else:
        analysis_folder_alias, geo_analysis_folder_alias, inst_analysis_folder_alias = ("", "", "")
    if progress_callback:
        progress_callback(100)
    return_tup = (analysis_folder_alias, geo_analysis_folder_alias, inst_analysis_folder_alias,
                  country_affil_file_path, wrong_affil_types_dict)
    return return_tup
