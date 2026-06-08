"""Module of functions for geographical collaborations analysis.
"""

__all__ = ['build_and_save_geo_stat']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.useful_functs import print_step_text


def _set_geo_stat_cols():
    """Builds a dict setting selected columns names for the process 
    of building geographical statistics.

    Returns:
        (dict): The built dict.
    """
    geo_stat_cols_dic = {'pub_id_col'       : bm_pg.COL_NAMES['pub_id'],
                         'country_col'      : bm_pg.COL_NAMES['country'][2],
                         'continent_col'    : bm_pg.COL_NAMES_BONUS['continent'],
                         'final_country_col': bm_pg.COL_NAMES_BONUS['country'],
                         'weight_col'       : bm_pg.COL_NAMES_BONUS['pub number'],
                         'pub_ids_col'      : bm_pg.COL_NAMES_BONUS["pub_ids list"],
                        }

    return geo_stat_cols_dic


def _build_items_stat(items_df, institute_item, items_cols, stat_cols):
    """Builds the statistics of publications per item, item being 
    for instance country or continent.

    Args:
        items_df (dataframe): Item data used to compute the statistics.
        institute_item (str): Value of the Institute's item.
        items_cols (list): The two column names of the item data useful \
        to compute de statistics, i.e. publications IDs and publications items.
        stat_cols (list): The column names of the data of the built statisctics.
    Returns:
        (dataframe): The data of the built statisctics.
    """
    [pub_id_col, item_col] = items_cols
    data = []
    for item, pub_id_dg in items_df.groupby(item_col):
        pub_id_dg = pub_id_dg.drop_duplicates([pub_id_col, item_col])
        pub_ids_list = pub_id_dg[pub_id_col].tolist()
        pub_ids_nb = len(pub_ids_list)
        if item!=institute_item:
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        data.append([item, pub_ids_nb, pud_ids_txt])
    by_item_df = pd.DataFrame(data, columns=stat_cols)
    return by_item_df


def _build_countries_stat(countries_df, institute_country):
    """Builds the statistics of publications per country from the analysis 
    of the dataframe of countries.

    Each row of this dataframe contains:

    - A publication IDs;
    - The index of an address of the publication addresses;
    - The country of the given address.

    Args:
        countries_df (dataframe): Data of countries per publications.
        institute_country (str): The country of the institute.
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

    # Computing the statistics per countries
    countries_cols = [pub_id_col, country_col]
    stat_cols = [final_country_col, weight_col, pub_ids_col]
    by_country_df = _build_items_stat(countries_df, institute_country, countries_cols, stat_cols)
    return by_country_df


def _build_continents_stat(countries_df, institute_continent):
    """Builds the statistics of publications per continents from the analysis 
    of the dataframe of countries.

    Each row of this dataframe contains:

    - A publication IDs;
    - The index of an address of the publication addresses;
    - The country of the given address.

    Args:
        countries_df (dataframe): Data of countries per publications.
        institute_continent (str): The continent of the institute
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

    # Getting continent information by country from COUNTRIES_CONTINENT global
    country_conti_dict = bm_pg.COUNTRIES_CONTINENT

    # Replacing country by its continent in a copy of 'by_country_df'
    continents_df = countries_df.copy()
    continents_df[country_col] = continents_df[country_col].map(lambda x: country_conti_dict[x])

    # Renaming the column 'country_col' to 'continent_col'
    continents_df = continents_df.rename(columns={country_col: continent_col})

    # Computing the statistics per continents
    continents_cols = [pub_id_col, continent_col]
    stat_cols = [continent_col, weight_col, pub_ids_col]
    by_continent_df = _build_items_stat(continents_df, institute_continent, continents_cols, stat_cols)
    return by_continent_df


def _set_institute_country_stat_df_params():
    """Builds a dict setting selected columns names for the process 
    of building statistics within Institute country .

    Returns:
        (dict): The built dict.
    """
    inst_country_stat_cols_dic = {'pub_id_col'      : bm_pg.COL_NAMES['pub_id'],
                                  'address_id_col'  : bm_pg.COL_NAMES['institution'][1],
                                  'institutions_col': bm_pg.COL_NAMES['institution'][2],
                                  'countries_col'   : bm_pg.COL_NAMES['country'][2],
                                  'pub_kind_col'    : bm_pg.COL_NAMES_BONUS['pub_type'],
                                  'weight_col'      : bm_pg.COL_NAMES_BONUS['pub number'],
                                  'pub_ids_col'     : bm_pg.COL_NAMES_BONUS["pub_ids list"],
                                 }

    inst_country_stat_rows_dic = {'all_key'                : bm_pg.STAT_ROW_NAMES['all'],
                                  'institute_only_key'     : bm_pg.STAT_ROW_NAMES['institute_only'],
                                  'country_only_key'       : bm_pg.STAT_ROW_NAMES['country_only'],
                                  'country_at_least_key'   : bm_pg.STAT_ROW_NAMES['country_at_least'],
                                  'out_of_country_only_key': bm_pg.STAT_ROW_NAMES['out_of_country_only'],
                                 }

    return inst_country_stat_cols_dic, inst_country_stat_rows_dic


def _update_pub_ids_lists(pub_id, df, institute_norm, institutions_col, init_raw_item_lists):
    """Updates two lists of publications IDs with the passed publication ID 
    depending on the Institute's normalized name occurrence in the analyzed data.

    The kind of the publications IDs lists are explained in 
    the `_build_institute_country_stat` internal calling function.

    Args:
        pub_id (str): The publication ID tagged with the corpus year value.
        df (dataframe): The data to be analyzed.
        institute_norm (str): The Institute's normalized name.
        institutions_col (list): The name of the column that contains \
        the normalized affiliations in the data to be analyzed.
        init_raw_item_lists (list): The list of the publications IDs lists to be updated.
    Returns:
        (tup): The two updated lists of the publications IDs.
    """
    raw_item_at_least, raw_out_of_item_only = init_raw_item_lists
    item_at_least = []
    all_affiliations = [str(x) for x in df[institutions_col].to_list()]
    for affils_idx, affils_str in enumerate(all_affiliations):
        item_at_least.append(False)
        affils_list = affils_str.split("; ")
        if institute_norm not in affils_list:
            item_at_least[affils_idx] = True
            break
    new_raw_item_at_least = raw_item_at_least.copy()
    new_raw_out_of_item_only = raw_out_of_item_only.copy()
    if not any(item_at_least):
        new_raw_item_at_least.append(pub_id)
    else:
        new_raw_out_of_item_only.append(pub_id)
    return new_raw_item_at_least, new_raw_out_of_item_only


def _set_stat_value(raw_pub_ids_list, all_status=False):
    """Formats the statistics data of the Institute's country.

    The list of publications IDs are built through the 
    `_build_institute_country_stat` internal calling function. 
    The statistics data computed are:
        - The number of publications;
        - The publications-IDs string composed of the publications \
        IDs separated by semicolon.

    Args:
        raw_pub_ids_list (list) : The list of publications IDs \
        to be used for computing the statistics data.
        all_status (bool): Optional (default: False), if True the length \
        of the publications-IDs string is limited.
    Returns:
        (list): The formated statistics data.
    """
    pub_ids_list = sorted(set(raw_pub_ids_list))
    pub_ids_nb = len(pub_ids_list)
    pub_ids_str = "; ".join(pub_ids_list)
    if all_status:
        pub_ids_str = "; ... ; ".join([pub_ids_list[0], pub_ids_list[pub_ids_nb-1]])
    value_list = [pub_ids_nb, pub_ids_str]
    return value_list


def _build_institute_country_stat(norm_affil_df, institute_country, institute_norm):
    """Builds the statistics of publications per combination types of co-authors countries 
    from the analysis of the data of the normalized institutions per publication.

    Each row of the built data contains:

    - A type of co-authors:
        - all types of co-authors,
        - no co-authors,
        - only co-authors of the country of the Institute,
        - co-authors from the Institute country together with co-authors from other countries,
        - only co-authors from other countries;
    - The number of publications;
    - The list of publication IDs.

    Args:
        norm_affil_df (dataframe): Data of the normalized institutions per publication.
        institute_country (str): The country of the institute
    Returns:
        (dataframe): Institute's country statistics where each row gives the co-authors type, \
        the Institute-publications number related to the co-authors type \
        and a string listing the concerned publications IDs separated by semicolon.
    """
    inst_country_stat_cols_dic, inst_country_stat_rows_dic = _set_institute_country_stat_df_params()
    col_keys = ['pub_id_col', 'countries_col', 'institutions_col', 'pub_kind_col',
                'weight_col', 'pub_ids_col']
    (pub_id_col, countries_col, institutions_col, pub_kind_col,
     weight_col, pub_ids_col) = [inst_country_stat_cols_dic[key] for key in col_keys]

    row_keys = ['all_key', 'institute_only_key', 'country_only_key',
                'country_at_least_key', 'out_of_country_only_key']
    (all_key, institute_only_key, country_only_key, country_at_least_key,
     out_of_country_only_key) = [inst_country_stat_rows_dic[key] for key in row_keys]

    (raw_institute_only, raw_country_only,
     raw_country_at_least, raw_out_of_country_only) = [[]] * 4

    raw_all_pub_ids_list = norm_affil_df[pub_id_col].to_list()
    for pub_id, pub_id_df in norm_affil_df.groupby(pub_id_col):
        countries_list = list(set(pub_id_df[countries_col].to_list()))
        if len(countries_list)==1:
            init_country_raw_item_lists = [raw_institute_only.copy(), raw_country_only.copy()]
            return_tup = _update_pub_ids_lists(pub_id, pub_id_df, institute_norm,
                                              institutions_col, init_country_raw_item_lists)
            raw_institute_only, raw_country_only = return_tup
        else:
            institute_country_df = pub_id_df[pub_id_df[countries_col]==institute_country]
            init_raw_item_lists = [raw_country_at_least.copy(), raw_out_of_country_only.copy()]
            return_tup = _update_pub_ids_lists(pub_id, institute_country_df, institute_norm,
                                               institutions_col, init_raw_item_lists)
            raw_country_at_least, raw_out_of_country_only = return_tup

    inst_country_stat_dic = {all_key                : _set_stat_value(raw_all_pub_ids_list, all_status=True),
                             institute_only_key     : _set_stat_value(raw_institute_only),
                             country_only_key       : _set_stat_value(raw_country_only),
                             country_at_least_key   : _set_stat_value(raw_country_at_least),
                             out_of_country_only_key: _set_stat_value(raw_out_of_country_only),
                             }

    data_cols = [pub_kind_col, weight_col, pub_ids_col]
    data = []
    for k, v in inst_country_stat_dic.items():
        data.append([k, v[0], v[1]])
    inst_country_stat_df = pd.DataFrame(data, columns=data_cols)

    return inst_country_stat_df


def _set_geo_files_params(analysis_folder_path, institute_country):
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
    country_weight_file_base_alias = bm_pg.ARCHI_YEAR["country weight file name"]
    continent_weight_file_base_alias = bm_pg.ARCHI_YEAR["continent weight file name"]
    institute_country_weight_file_base_alias = bm_pg.ARCHI_YEAR["institute-country weight file base"]

    # Setting specific file name
    country_weight_file_name = f'{country_weight_file_base_alias}{xlsx_extent}'
    continent_weight_file_name = f'{continent_weight_file_base_alias}{xlsx_extent}'
    institute_country_weight_file_name = (f'{institute_country_weight_file_base_alias}'
                                          f'{institute_country}{xlsx_extent}')

    # Setting useful paths
    geo_analysis_folder_path = analysis_folder_path / Path(geo_analysis_folder_alias)

    # Creating the required output folder
    if not os.path.exists(geo_analysis_folder_path):
        os.makedirs(geo_analysis_folder_path)

    filenames_list = [country_weight_file_name, continent_weight_file_name,
                      institute_country_weight_file_name]
    folder_params = [geo_analysis_folder_alias, geo_analysis_folder_path]
    return filenames_list, folder_params


def build_and_save_geo_stat(geo_stat_params, countries_df, norm_affiliations_df,
                            analysis_folder_path):
    """Builds the publications statistics dataframes per country and per continent
    including for the Institute country.

    First, it builds the statistics dataframes through the `_build_countries_stat` 
    and the `_build_continents_stat` internal functions.
    Then, it saves the statistics dataframes through the `save_formatted_df_to_xlsx` 
    function imported from the `bmfuncts.format_files` module.

    Args:
        geo_stat_params (list): Composed of the 4 digits-year of the analyzed corpus, \
        of the print parameters (list) and of the Institute's name (str).
        countries_df (dataframe): Data of countries per publications.
        norm_affiliations_df (dataframe): Data of the normalized affiliations per publication.
        analysis_folder_path (path): The full path to the folder where analysis data are saved.
    returns:
        (path): The full path to the folder where the results of the geographical analysis \
        are saved.
    """
    # Setting parameters value from 'geo_stat_params'
    corpus_year, print_params, institute = geo_stat_params

    # Setting Institute's country and continent
    institute_country = bm_ig.INSTITUTES_COUNTRY_DICT[institute]
    institute_continent = bm_ig.INSTITUTES_CONTINENT_DICT[institute]
    institute_norm = bm_ig.INSTITUTES_NORM_NAME_DICT[institute]

    # Building stat dataframes
    print("  - Computing geographical statistics...", end="\r")
    by_country_df = _build_countries_stat(countries_df, institute_country)
    by_continent_df = _build_continents_stat(countries_df, institute_continent)
    inst_country_stat_df = _build_institute_country_stat(norm_affiliations_df,
                                                         institute_country, institute_norm)

    # Setting files params
    filenames_list, folder_params = _set_geo_files_params(analysis_folder_path, institute_country)
    (country_weight_filename, continent_weight_filename,
     institute_country_weight_filename) = filenames_list
    geo_analysis_folder, geo_analysis_folder_path = folder_params

    # Saving formatted stat dataframes
    geo_df_title = bm_pg.DF_TITLES_LIST[8]
    sheet_name = 'Pays ' + corpus_year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, country_weight_filename,
                              by_country_df, geo_df_title, sheet_name)
    sheet_name = 'Continent ' + corpus_year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, continent_weight_filename,
                              by_continent_df, geo_df_title, sheet_name)
    sheet_name = institute_country + " " + corpus_year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, institute_country_weight_filename,
                              inst_country_stat_df, geo_df_title, sheet_name)
    print_step_text("  - Geo statistics built and saved      ", print_params)
    return geo_analysis_folder
