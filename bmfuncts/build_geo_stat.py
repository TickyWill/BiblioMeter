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


def _build_countries_stat(countries_df, institute_country):
    """Builds the statistics of publications per country from the analysis 
    of the dataframe of countries.

    Each row of this dataframe contains:

    - A publication IDs; 
    - The index of an address of the publication addresses; 
    - The country of the given address.

    Args:
        countries_df (dataframe): Data of countries per publications.
        institute_country (str): The country of the institute
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
        if country!=institute_country:
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_country_df.loc[idx_country, pub_ids_col] = pud_ids_txt
        idx_country += 1

    return by_country_df


def _build_continents_stat(countries_df, institute_continent):
    """Builds the statistics of publications per continents from the analysis 
    of the dataframe of countries.

    Each row of this dataframe contains:

    - A publication IDs; 
    - The index of an address of the publication addresses; 
    - The country of the given address.

    Args:
        institute (str): Institute's name.
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
        if continent!=institute_continent:
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_continent_df.loc[idx_continent, pub_ids_col] = pud_ids_txt
        idx_continent += 1

    return by_continent_df


def _set_institute_country_stat_df_params():
    """Builds a dict setting selected columns names for the process 
    of building statistics within Institute country .

    Returns:
        (dict): The built dict.
    """
    inst_country_stat_cols_dic = {'pub_id_col'      : bp.COL_NAMES['pub_id'],
                                  'address_id_col'  : bp.COL_NAMES['institution'][1],
                                  'institutions_col': bp.COL_NAMES['institution'][2],
                                  'countries_col'   : bp.COL_NAMES['country'][2],
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


def _build_institute_country_stat(norm_institutions_df, institute_country, institute_norm):
    inst_country_stat_cols_dic, inst_country_stat_rows_dic = _set_institute_country_stat_df_params()
    col_keys = ['pub_id_col', 'address_id_col', 'countries_col', 'institutions_col',
                'pub_kind_col', 'weight_col', 'pub_ids_col']
    (pub_id_col, address_id_col, countries_col, institutions_col,
     pub_kind_col, weight_col, pub_ids_col) = [inst_country_stat_cols_dic[key] for key in col_keys]

    row_keys = ['all_key', 'institute_only_key', 'country_only_key', 'country_at_least_key', 'out_of_country_only_key']
    (all_key, institute_only_key, country_only_key,
     country_at_least_key, out_of_country_only_key) = [inst_country_stat_rows_dic[key] for key in row_keys]

    inst_country_stat_dic = {}
    raw_institute_only_pub_ids_list = []
    raw_country_only_pub_ids_list = []
    raw_country_at_least_pub_ids_list = []
    raw_out_of_country_only_pub_ids_list = []

    for pub_id, pub_id_df in norm_institutions_df.groupby(pub_id_col):
        countries_list = list(set(pub_id_df[countries_col].to_list()))
        if len(countries_list)==1:
            addr_idxs = pub_id_df[address_id_col].to_list()
            institutions = pub_id_df[institutions_col].to_list()
            addr_inst_dic = dict(zip(addr_idxs, institutions))
            only_institute = True
            for _, addr_institution in addr_inst_dic.items():
                institutions_list = str(addr_institution).split("; ")
                if not institute_norm in institutions_list:
                    only_institute = False
                    break
            if only_institute:
                raw_institute_only_pub_ids_list.append(pub_id)
            else:
                raw_country_only_pub_ids_list.append(pub_id)
        else:
            institute_country_df = pub_id_df[pub_id_df[countries_col]==institute_country]
            addr_idxs = institute_country_df[address_id_col].to_list()
            institutions = institute_country_df[institutions_col].to_list()
            addr_inst_dic = dict(zip(addr_idxs, institutions))
            country_at_least = False
            for _, addr_institution in addr_inst_dic.items():
                institutions_list = str(addr_institution).split("; ")
                if not institute_norm in institutions_list:
                    country_at_least = True
                    break
            if country_at_least:
                raw_country_at_least_pub_ids_list.append(pub_id)
            else:
                raw_out_of_country_only_pub_ids_list.append(pub_id)

    raw_pub_ids_list = norm_institutions_df[pub_id_col].to_list()
    all_pub_ids_list = sorted(list(set(raw_pub_ids_list)))
    all_nb = len(all_pub_ids_list)
    all_pub_ids_str = "; ... ; ".join([all_pub_ids_list[0], all_pub_ids_list[all_nb-1]])
    inst_country_stat_dic[all_key] = [all_nb, all_pub_ids_str]

    institute_only_pub_ids_list = sorted(list(set(raw_institute_only_pub_ids_list)))
    institute_only_nb = len(institute_only_pub_ids_list)
    institute_only_pub_ids_str = "; ".join(institute_only_pub_ids_list)
    inst_country_stat_dic[institute_only_key] = [institute_only_nb,
                                                 institute_only_pub_ids_str]

    country_only_pub_ids_list = sorted(list(set(raw_country_only_pub_ids_list)))
    country_only_nb = len(country_only_pub_ids_list)
    country_only_pub_ids_str = "; ".join(country_only_pub_ids_list)
    inst_country_stat_dic[country_only_key] = [country_only_nb, country_only_pub_ids_str]

    country_at_least_pub_ids_list = sorted(list(set(raw_country_at_least_pub_ids_list)))
    country_at_least_nb = len(country_at_least_pub_ids_list)
    country_at_least_pub_ids_str = "; ".join(country_at_least_pub_ids_list)
    inst_country_stat_dic[country_at_least_key] = [country_at_least_nb, country_at_least_pub_ids_str]

    out_of_country_only_pub_ids_list = sorted(list(set(raw_out_of_country_only_pub_ids_list)))
    out_of_country_only_nb = len(out_of_country_only_pub_ids_list)
    out_of_country_only_pub_ids_str = "; ".join(out_of_country_only_pub_ids_list)
    inst_country_stat_dic[out_of_country_only_key] = [out_of_country_only_nb, out_of_country_only_pub_ids_str]

    data_cols = [pub_kind_col, weight_col, pub_ids_col]
    data = []
    for k, v in inst_country_stat_dic.items():
        data.append([k,v[0],v[1]])
    inst_country_stat_df = pd.DataFrame(data, columns=data_cols)

    return inst_country_stat_df


#def _build_institute_country_stat_old(norm_institutions_df, institute_country, institute_norm):
#    inst_country_stat_cols_dic, inst_country_stat_rows_dic = _set_institute_country_stat_df_params()
#    col_keys = ['pub_id_col', 'address_id_col', 'countries_col', 'institutions_col',
#                'pub_kind_col', 'weight_col', 'pub_ids_col']
#    (pub_id_col, address_id_col, countries_col, institutions_col,
#     pub_kind_col, weight_col, pub_ids_col) = [inst_country_stat_cols_dic[key] for key in col_keys]
#
#    row_keys = ['all_key', 'institute_only_key', 'w_others_key', 'wo_others_key']
#    (all_key, institute_only_key, w_others_key,
#     wo_others_key) = [inst_country_stat_rows_dic[key] for key in row_keys]
#
#    inst_country_stat_dic = {}
#    raw_institute_only_pub_ids_list = []
#    raw_w_others_pub_ids_list = []
#
#    for pub_id, pub_id_df in norm_institutions_df.groupby(pub_id_col):
#        countries_list = list(set(pub_id_df[countries_col].to_list()))
#        if len(countries_list)==1:
#            if countries_list[0]==institute_country:
#                addr_idxs = pub_id_df[address_id_col].to_list()
#                institutions = pub_id_df[institutions_col].to_list()
#                addr_inst_dic = dict(zip(addr_idxs, institutions))
#                only_institute = True
#                for addr_idx, addr_institution in addr_inst_dic.items():
#                    institutions_list = str(addr_institution).split("; ")
#                    if not institute_norm in institutions_list:
#                        only_institute = False
#                if only_institute:
#                    raw_institute_only_pub_ids_list.append(pub_id)
#
#    for pub_id, pub_id_df in norm_institutions_df.groupby(pub_id_col):
#        for country, country_df in pub_id_df.groupby(countries_col):
#            if country==institute_country:
#                addr_idxs = country_df[address_id_col].to_list()
#                institutions = country_df[institutions_col].to_list()
#                addr_inst_dic = dict(zip(addr_idxs, institutions))
#                for addr_idx, addr_institution in addr_inst_dic.items():
#                    institutions_list = str(addr_institution).split("; ")
#                    if not institute_norm in institutions_list:
#                        raw_w_others_pub_ids_list.append(pub_id)
#
#    raw_pub_ids_list = norm_institutions_df[pub_id_col].to_list()
#    all_pub_ids_list = sorted(list(set(raw_pub_ids_list)))
#    all_nb = len(all_pub_ids_list)
#    all_pub_ids_str = "; ... ; ".join([all_pub_ids_list[0], all_pub_ids_list[all_nb-1]])
#    inst_country_stat_dic[all_key] = [all_nb, all_pub_ids_str]
#
#    institute_only_pub_ids_list = sorted(list(set(raw_institute_only_pub_ids_list)))
#    institute_only_nb = len(institute_only_pub_ids_list)
#    institute_only_pub_ids_str = "; ".join(institute_only_pub_ids_list)
#    inst_country_stat_dic[institute_only_key] = [institute_only_nb,
#                                                 institute_only_pub_ids_str]
#
#    w_others_pub_ids_list = sorted(list(set(raw_w_others_pub_ids_list)))
#    w_others_nb = len(w_others_pub_ids_list)
#    w_others_pub_ids_str = "; ".join(w_others_pub_ids_list)
#    inst_country_stat_dic[w_others_key] = [w_others_nb, w_others_pub_ids_str]
#
#    raw_wo_others_pub_ids_set = set(raw_pub_ids_list) - set(raw_w_others_pub_ids_list)
#    wo_others_pub_ids_list = sorted(list(raw_wo_others_pub_ids_set))
#    wo_others_nb = all_nb - w_others_nb
#    wo_others_pub_ids_str = "; ".join(wo_others_pub_ids_list)
#    inst_country_stat_dic[wo_others_key] = [wo_others_nb, wo_others_pub_ids_str]
#
#    data_cols = [pub_kind_col, weight_col, pub_ids_col]
#    data = []
#    for k, v in inst_country_stat_dic.items():
#        data.append([k,v[0],v[1]])
#    inst_country_stat_df = pd.DataFrame(data, columns=data_cols)
#
#    return inst_country_stat_df


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

    filenames_list = [country_weight_file_name, continent_weight_file_name, institute_country_weight_file_name]
    folder_params = [geo_analysis_folder_alias, geo_analysis_folder_path]
    return filenames_list, folder_params


def build_and_save_geo_stat(countries_df, norm_institutions_df,
                            institute_geo_dict, analysis_folder_path, year):
    """Builds the publications statistics dataframes per country and per continent
    including for the Institute country.
    
    First, it builds the statistics dataframes through the `_build_countries_stat` 
    and the `_build_continents_stat` internal functions.
    Then, it saves the statistics dataframes through the `_save_formatted_df_to_xlsx` 
    internal function.

    Args:
        countries_df (dataframe): Data of countries per publications.
        norm_institutions_df (dataframe): Data of the normalized institutions per publication.
        institute_geo_dict (dict): Geographic data of the institute (keys: 'country', 'continent' \
        and 'norm_name'; values: country, continent and normalized name of Institute).
        analysis_folder_path (path): The full path to the folder where analysis data are saved.
        year (str): 4 digits-year of the analyzed corpus.
    returns:
        (path): The full path to the folder where the results of the geographical analysis \
        are saved.
    """
    print("    Computing geographical statistics...")
    # Setting Institute's country and continent
    institute_country = institute_geo_dict['country']
    institute_continent = institute_geo_dict['continent']
    institute_norm = institute_geo_dict['norm_name']

    # Building stat dataframes
    by_country_df = _build_countries_stat(countries_df, institute_country)
    by_continent_df = _build_continents_stat(countries_df, institute_continent)
    inst_country_stat_df = _build_institute_country_stat(norm_institutions_df,
                                                         institute_country, institute_norm)

    # Setting files params
    filenames_list, folder_params = _set_geo_files_params(analysis_folder_path, institute_country)
    (country_weight_filename, continent_weight_filename,
     institute_country_weight_filename) = filenames_list
    geo_analysis_folder, geo_analysis_folder_path = folder_params

    # Saving formatted stat dataframes
    geo_df_title = bm_pg.DF_TITLES_LIST[8]
    sheet_name = 'Pays ' + year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, country_weight_filename,
                              by_country_df, geo_df_title, sheet_name)
    sheet_name = 'Continent ' + year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, continent_weight_filename,
                              by_continent_df, geo_df_title, sheet_name)
    sheet_name = institute_country + " " + year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, institute_country_weight_filename,
                              inst_country_stat_df, geo_df_title, sheet_name)

    return geo_analysis_folder
