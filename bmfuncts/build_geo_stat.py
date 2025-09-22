"""Module of functions for geographical collaborations analysis.

"""

__all__ = ['build_and_save_geo_stat']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmfuncts.institute_globals as bm_ig
from bmfuncts.format_files import save_formatted_df_to_xlsx


def _set_geo_stat_cols():
    """Builds a dict setting selected columns names for the process 
    of building geographical statistics.

    Returns:
        (dict): The built dict.
    """
    geo_stat_cols_dic = {'pub_id_col'       : bp.COL_NAMES['pub_id'],
                         'country_col'      : bp.COL_NAMES['country'][2],
                         'continent_col'    : bm_pg.COL_NAMES_BONUS['continent'],
                         'final_country_col': bm_pg.COL_NAMES_BONUS['country'],
                         'weight_col'       : bm_pg.COL_NAMES_BONUS['pub number'],
                         'pub_ids_col'      : bm_pg.COL_NAMES_BONUS["pub_ids list"],
                        }

    return geo_stat_cols_dic


def _build_countries_stat(countries_df):
    """Builds the statistics of publications per country from the analysis 
    of the dataframe of countries.

    Each row of this dataframe contains:

    - A publication IDs; 
    - The index of an address of the publication addresses; 
    - The country of the given address.

    Args:
        countries_df (dataframe): Data of countries per publications.
    Returns:
        (dataframe): Countries statistics where each row gives the country name, \
        the Institute-publications number with address from the country \
        and a string listing the concerned publications IDs separated by semicolon.
    """
    # Setting col names
    geo_stat_cols_dic = _set_geo_stat_cols()
    col_keys = ['pub_id_col', 'country_col', 'final_country_col', 'weight_col', 'pub_ids_col']
    (pub_id_col, country_col, final_country_col,
     weight_col, pub_ids_col) = [geo_stat_cols_dic[key] for key in col_keys]

    by_country_df = pd.DataFrame(columns=[final_country_col, weight_col, pub_ids_col])
    idx_country = 0
    for country, pub_id_dg in countries_df.groupby(country_col):
        pub_id_dg = pub_id_dg.drop_duplicates([pub_id_col, country_col])
        pub_ids_list = pub_id_dg[pub_id_col].tolist()
        pub_ids_nb = len(pub_ids_list)
        by_country_df.loc[idx_country, final_country_col] = country
        by_country_df.loc[idx_country, weight_col] = pub_ids_nb
        if country!=bm_ig.INSTITUTE_GEO['country']:
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_country_df.loc[idx_country, pub_ids_col] = pud_ids_txt
        idx_country += 1

    return by_country_df


def _build_continents_stat(countries_df):
    """Builds the statistics of publications per continents from the analysis 
    of the dataframe of countries.

    Each row of this dataframe contains:

    - A publication IDs; 
    - The index of an address of the publication addresses; 
    - The country of the given address.

    Args:
        countries_df (dataframe): Data of countries per publications.
    Returns:
        (dataframe): Continents statistics where each row gives the continent name, \
        the Institute-publications number with address from the continent \
        and a string listing the concerned publications IDs separated by semicolon.
    """
    # Setting col names
    geo_stat_cols_dic = _set_geo_stat_cols()
    col_keys = ['pub_id_col', 'country_col', 'continent_col', 'weight_col', 'pub_ids_col']
    (pub_id_col, country_col, continent_col,
     weight_col, pub_ids_col) = [geo_stat_cols_dic[key] for key in col_keys]

    # Getting continent information by country from COUNTRIES_CONTINENT, a BiblioParsing global
    country_conti_dict = bp.COUNTRIES_CONTINENT

    # Replacing country by its continent in a copy of 'by_country_df'
    continents_df = countries_df.copy()
    continents_df[country_col] = continents_df[country_col].map(lambda x: country_conti_dict[x])

    # Renaming the column 'country_col' to 'continent_col'
    continents_df = continents_df.rename(columns={country_col: continent_col})

    by_continent_df = pd.DataFrame(columns=[continent_col, weight_col, pub_ids_col])
    idx_continent = 0
    for continent, pub_id_dg in continents_df.groupby(continent_col):
        pub_id_dg = pub_id_dg.drop_duplicates([pub_id_col, continent_col])
        pub_ids_list = pub_id_dg[pub_id_col].tolist()
        pub_ids_nb = len(pub_ids_list)
        by_continent_df.loc[idx_continent, continent_col] = continent
        by_continent_df.loc[idx_continent, weight_col] = pub_ids_nb
        if continent!=bm_ig.INSTITUTE_GEO['continent']:
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_continent_df.loc[idx_continent, pub_ids_col] = pud_ids_txt
        idx_continent += 1

    return by_continent_df


def _set_geo_files_params(analysis_folder_path):
    """Sets specific file names, folder names and folder paths for geographical-analysis. 

    Args:
        analysis_folder_path (path): The full path to the folder where analysis data are saved.
    Returns:
        (tup): (The list composed of the File names (str) for saving computed statistics \
        of countries and continents, The folder parameters (list) composed of the folder \
        name (str) and the full path (path) for saving the computed data).
    """
    # Setting local parameters
    xlsx_extent = ".xlsx"

    # Setting aliases from globals
    geo_analysis_folder_alias = bm_pg.ARCHI_YEAR["countries analysis"]
    country_weight_filename_alias = bm_pg.ARCHI_YEAR["country weight file name"] + xlsx_extent
    continent_weight_filename_alias = bm_pg.ARCHI_YEAR["continent weight file name"] + xlsx_extent

    # Setting useful paths
    geo_analysis_folder_path = analysis_folder_path / Path(geo_analysis_folder_alias)

    # Creating the required output folder
    if not os.path.exists(geo_analysis_folder_path):
        os.makedirs(geo_analysis_folder_path)

    filenames_list = [country_weight_filename_alias, continent_weight_filename_alias]
    folder_params = [geo_analysis_folder_alias, geo_analysis_folder_path]
    return filenames_list, folder_params


def build_and_save_geo_stat(countries_df, analysis_folder_path, year):
    """Builds the publications statistics dataframes per country and per continent.
    
    First, it builds the statistics dataframes through the `_build_countries_stat` 
    and the `_build_continents_stat` internal functions.
    Then, it saves the statistics dataframes through the `_save_formatted_df_to_xlsx` 
    internal function.

    Args:
        countries_df (dataframe): Data of countries per publications.
        analysis_folder_path (path): The full path to the folder where analysis data are saved.
        year (str): 4 digits-year of the analyzed corpus.
    returns:
        (path): The full path to the folder where the results of the geographical analysis \
        are saved.
    """
    print("    Computing geographical statistics...")

    # Setting files params
    filenames_list, folder_params = _set_geo_files_params(analysis_folder_path)
    country_weight_filename, continent_weight_filename = filenames_list
    geo_analysis_folder, geo_analysis_folder_path = folder_params

    # Building stat dataframes
    by_country_df = _build_countries_stat(countries_df)
    by_continent_df = _build_continents_stat(countries_df)

    # Saving formatted stat dataframes
    geo_df_title = bm_pg.DF_TITLES_LIST[8]
    sheet_name = 'Pays ' + year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, country_weight_filename,
                              by_country_df, geo_df_title, sheet_name)
    sheet_name = 'Continent ' + year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, continent_weight_filename,
                              by_continent_df, geo_df_title, sheet_name)

    return geo_analysis_folder
