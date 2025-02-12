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
from openpyxl import Workbook as openpyxl_Workbook

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_user_config
from bmfuncts.format_files import format_page
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.useful_functs import concat_dfs


def _clean_unkept_affil(raw_institutions_df, country_unkept_affil_file_path, cols_tup):
    """Removes the affiliation items given in the file pointed by 'country_unkept_affil_file_path' 
    path from the raw-institutions data."""
    countries_col, raw_affil_col, institution_col = cols_tup
    unkept_institutions_dict = pd.read_excel(country_unkept_affil_file_path, sheet_name=None)
    unkept_country_list = list(unkept_institutions_dict.keys())

    new_raw_institutions_df = pd.DataFrame()
    for country, country_raw_inst_df in raw_institutions_df.groupby(countries_col):
        if country in unkept_country_list:
            unkept_institutions_list = unkept_institutions_dict[country][raw_affil_col].to_list()
            for idx_row, inst_row in country_raw_inst_df.iterrows():
                inst_row_list = [x.strip() for x in inst_row[institution_col].split(";")]
                for unkept_inst in unkept_institutions_list:
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
    df[copy_col] = dg[copy_col]
    df = df[cols_list]
    return df


def _year_pub_id(df, year, pub_id_col):
    """Transforms the column 'Pub_id' of the df
    by adding "yyyy_" to the value of the row.

    Args:
        df (pandas.DataFrame()): pandas.DataFrame() to be modified.
        year (str): 4 digits year of the corpus.
        pub_id_col (str): Name of the column of publications ID.
    Returns:
        (dataframe): the df with its changed column.
    """
    def _rename_pub_id(old_pub_id, year):
        pub_id_str = str(int(old_pub_id))
        while len(pub_id_str) < 3:
            pub_id_str = "0" + pub_id_str
        new_pub_id = str(int(year)) + '_' + pub_id_str
        return new_pub_id
    df[pub_id_col] = df[pub_id_col].apply(lambda x: _rename_pub_id(x, year))
    return df


def _build_and_save_norm_raw_dfs(institute, inst_pub_addresses_df,
                                 inst_analysis_folder_path, year,
                                 xlsx_extent, cols_tup, paths_tup,
                                 progress_callback, verbose=False):
    """Builds the data of countries, normalized institutions and raw institutions.

    This is done through the following steps:

    1. Builds dataframes of countries, normalized institutions and raw institutions \
    through the `build_norm_raw_institutions` function imported from the `BiblioParsing \
    package` imported as bp, using 'inst_pub_addresses_df' dataframe and specific files \
    for this function; in these datraframes, each row contains:

        - A publication IDs
        - The index of an address of the publication addresses 
        - The country of the given address
        - The list of the normalized institutions or the list of the raw institutions \
        for the given address, depending on the built dataframe.  

    2. Completes the normalized institutions and raw institutions dataframes with country \
    information by `_copy_dg_col_to_df` internal function.
    3. Modifyes the publication_IDs by `_year_pub_id` internal function in the 3 dataframes.
    4. Removes the institutions not to be considered through the `_clean_unkept_affil` \
    internal function.
    5. Saves the normalized institutions and raw institutions dataframes through the \
    `save_formatted_df_to_xlsx` function imported from the `bmfuncts.format_files` module.
    """
    # Setting parameters from args
    final_pub_id, parsing_pub_id = cols_tup
    institutions_folder_path, inst_types_file_path = paths_tup
    
    # Setting useful column names aliases
    idx_address_alias = bp.COL_NAMES['institution'][1]
    institutions_alias = bp.COL_NAMES['institution'][2]
    countries_col_alias = bp.COL_NAMES['country'][2]
    
    # Setting aliases from globals
    norm_inst_filename_alias = pg.ARCHI_YEAR["norm inst file name"] + xlsx_extent
    raw_inst_filename_alias = pg.ARCHI_YEAR["raw inst file name"] + xlsx_extent
    institutions_folder_alias = pg.ARCHI_INSTITUTIONS["root"]
    inst_types_file_base_alias = pg.ARCHI_INSTITUTIONS["inst_types_base"]
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
    
    # Building countries, normalized institutions and not normalized institutions data
    if verbose:
        print("Building of normalized and raw institutions on going...")
    file_path_0 = inst_types_file_path
    file_path_1 = country_affil_file_path
    file_path_2 = country_towns_file_alias
    file_path_3 = institutions_folder_path
    return_tup = bp.build_norm_raw_institutions(inst_pub_addresses_df,
                                                inst_types_file_path=file_path_0,
                                                country_affiliations_file_path=file_path_1,
                                                country_towns_file=file_path_2,
                                                country_towns_folder_path=file_path_3)
    countries_df, norm_institutions_df, raw_institutions_df = return_tup
    if verbose:
        print("countries, normalized institutions and not normalized institutions data built")
    if progress_callback:
        progress_callback(60)

    # Adding countries column to normalized institutions and not normalized institutions data    
    cols_list = [final_pub_id, idx_address_alias, countries_col_alias, institutions_alias]
    norm_institutions_df = _copy_dg_col_to_df(norm_institutions_df, countries_df,
                                              cols_list, countries_col_alias)
    raw_institutions_df = _copy_dg_col_to_df(raw_institutions_df, countries_df,
                                             cols_list, countries_col_alias)
    if verbose:
        print("Countries column added to normalized institutions and not normalized institutions data")
    if progress_callback:
        progress_callback(65)

    # Building pub IDs with year information
    _year_pub_id(countries_df, year, parsing_pub_id)
    _year_pub_id(norm_institutions_df, year, parsing_pub_id)
    _year_pub_id(raw_institutions_df, year, parsing_pub_id)
    if verbose:
        print("Publications IDs built with year information")
    if progress_callback:
        progress_callback(70)

    # Removing unkept institutions from 'raw_institutions_df'
    raw_affil_col = 'Raw affiliations'
    cols_tup = (countries_col_alias, raw_affil_col, institutions_alias)
    raw_institutions_df = _clean_unkept_affil(raw_institutions_df,
                                              country_unkept_affil_file_path,
                                              cols_tup)
    if verbose:
        print("Unkept institutions removed from not normalized institutions data")
    if progress_callback:
        progress_callback(75)

    # Saving formatted df of normalized and raw institutions
    inst_df_title = pg.DF_TITLES_LIST[9]
    sheet_name = 'Norm Inst ' + year
    save_formatted_df_to_xlsx(inst_analysis_folder_path, norm_inst_filename_alias,
                              norm_institutions_df, inst_df_title, sheet_name)
    sheet_name = 'Raw Inst ' + year
    save_formatted_df_to_xlsx(inst_analysis_folder_path, raw_inst_filename_alias,
                              raw_institutions_df, inst_df_title, sheet_name)
    if verbose:
        print("Normalized institutions and not normalized institutions data saved as openpyxl files")    
    return countries_df, norm_institutions_df, raw_institutions_df


def _build_distributed_inst_df(norm_institutions_df, institutions_col, inst_types_list):
    """Distributes the column that contains the list of the normalized institutions 
    of a publication and an author address into a column for each institution type.
    
    ex: "Institution" col value = UGA Univ; USMB Univ; CNRS Nro; G-INP Sch; IMEP-LaHC Lab
        -> "Univ" col value = "['UGA Univ', 'USMB Univ']"
        -> "Nro" col value = "['CNRS Nro']"
        -> "Sch" col value = "['G-INP Sch']"
        -> "Lab" col value = "['IMEP-LaHC Lab']"
        -> Other type col value = "[]"
    """    
    distrib_institutions_df = pd.DataFrame()
    for row_idx, row in norm_institutions_df.iterrows():
        inst_list = row[institutions_col].split("; ")
        for inst_type in inst_types_list:
            row[inst_type] = [inst for inst in inst_list if inst_type in inst]
        row_df = row.to_frame().T.astype(str)
        distrib_institutions_df = concat_dfs([distrib_institutions_df, row_df])
    distrib_institutions_df = distrib_institutions_df.astype(str)
    return distrib_institutions_df


def _set_inst_names_list(inst_names):
    """Converts the string containing a list of institutions into a list.
    
    ex: "['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']" 
        -> ['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']
    """
    inst_names = inst_names[1:len(inst_names)-1]
    inst_names_list = inst_names.split(", ")
    final_inst_names_list = [x[1:len(x)-1] for x in inst_names_list]
    return final_inst_names_list


def _build_pub_id_inst_type_df(distrib_institutions_df, inst_type,
                               pub_cols_list, pub_id_col):
    """Builds the data of institution per country per publication 
    for a given type of institutions.
    """
    # Setting useful column names
    bp_country_col_alias = pub_cols_list[1]

    # Building tha dataframe with one row per list of institutions of type 'inst_type' 
    # per country for each publication 
    full_inst_list = []
    pub_id_inst_type_df = pd.DataFrame(columns=pub_cols_list)
    for pub_id, pub_id_df in distrib_institutions_df.groupby(pub_id_col):
        data = []
        for country, country_df in pub_id_df.groupby(bp_country_col_alias):
            pub_id_inst_list = []
            for _, row in country_df.iterrows():
                inst_names = row[inst_type]
                if inst_names!="[]":
                    inst_names_list = _set_inst_names_list(inst_names)
                    pub_id_inst_list += inst_names_list
            pub_id_inst_list = list(set(pub_id_inst_list))
            full_inst_list += pub_id_inst_list
            data.append([pub_id, country, str(pub_id_inst_list)])
        pub_inst_df = pd.DataFrame(data, columns=pub_cols_list)
        pub_id_inst_type_df = concat_dfs([pub_id_inst_type_df, pub_inst_df])
    full_inst_list = list(set(full_inst_list))

    # Building the dataframe with one row per institution name and country
    # for each publication
    final_pub_id_inst_type_df = pd.DataFrame(columns=pub_cols_list)
    for inst_name in full_inst_list:
        for _, row in pub_id_inst_type_df.iterrows():
            inst_names_list = row[inst_type]
            data = []
            if " " + inst_name in inst_names_list:
                pub_id = row[pub_id_col]
                country = row[bp_country_col_alias]
                data.append([pub_id, country, inst_name])
            if data!=[]:
                pub_id_inst_name_df = pd.DataFrame(data, columns=pub_cols_list)
                final_pub_id_inst_type_df = concat_dfs([final_pub_id_inst_type_df,
                                                        pub_id_inst_name_df])
    return final_pub_id_inst_type_df


def _build_inst_type_stat_df(distrib_institutions_df, inst_type,
                             stat_cols_list, pub_id_col):
    """Builds the statistics data for a given type of institutions.

    It uses the `_build_pub_id_inst_type_df` internal function to build
    the dataframe with one row per list of institutions of type 'inst_type'
    per country for each publication.
    """
    # Setting useful column names
    bp_country_col_alias = bp.COL_NAMES['address_inst'][3]
    pg_country_col = stat_cols_list[1]
    pub_nb_col = stat_cols_list[2]
    pub_cols_list = [pub_id_col, bp_country_col_alias, inst_type]
    
    # Building the dataframe with one row per list of institutions of type 'inst_type'
    # per country for each publication
    pub_id_inst_type_df = _build_pub_id_inst_type_df(distrib_institutions_df, inst_type,
                                                     pub_cols_list, pub_id_col)
    
    # Building the dataframe with the statistics data per institution
    # for a given type of institutions
    inst_type_stat_df = pd.DataFrame(columns=stat_cols_list)
    for inst_name, inst_name_df in pub_id_inst_type_df.groupby(inst_type):
        countries_list = sorted(inst_name_df[bp_country_col_alias].to_list())
        for idx_row, row in inst_name_df.iterrows():
            country = row[bp_country_col_alias]
            if country==bp.UNKNOWN:
                inst_name_df.loc[idx_row, bp_country_col_alias] = countries_list[0]
        data = []
        for country, country_df in inst_name_df.groupby(bp_country_col_alias):
            pub_nb = len(country_df[pub_id_col])
            pub_list = "; ".join(country_df[pub_id_col].to_list())
            data.append([inst_name, country, pub_nb, pub_list])
            country_inst_name_df = pd.DataFrame(data, columns=stat_cols_list)
            inst_type_stat_df = concat_dfs([inst_type_stat_df, country_inst_name_df])
    inst_type_stat_df = inst_type_stat_df.drop_duplicates()

    # Sorting the built dataframe by publications number for each counrtry
    sorted_inst_type_stat_df = pd.DataFrame(columns=stat_cols_list)
    for country, country_df in inst_type_stat_df.groupby(pg_country_col):
        country_df = country_df.sort_values(by=[pub_nb_col], ascending=False)
        sorted_inst_type_stat_df = concat_dfs([sorted_inst_type_stat_df, country_df])
    return sorted_inst_type_stat_df


def _build_and_save_inst_stat_df(distrib_institutions_df, inst_types_list,
                                 stat_cols_list, pub_id_col, inst_stat_xlsx_path):
    """Builds and saves the institutions statistics into a multisheet openpyxl 
    workbook with a sheet per institution type.

    This done by cycling on institution type with the following steps:

    1. A dataframe of institutions statistics is built through the 
    `_build_inst_type_stat_df` internal function.
    2. A sheet is added to the openpyxl workbook containing the data 
    of the built dataframe through the `format_wb_sheet` function 
    imported from the `bmfuncts.format_files` module. 
    """
    # Initialize parameters for saving results as multisheet workbook
    first = True
    wb = openpyxl_Workbook()
    
    for inst_type in inst_types_list:
        inst_type_stat_df = _build_inst_type_stat_df(distrib_institutions_df, inst_type,
                                                     stat_cols_list, pub_id_col)        
        inst_sheet_name = inst_type
        inst_df_title = pg.DF_TITLES_LIST[12]
        wb = format_wb_sheet(inst_sheet_name, inst_type_stat_df, inst_df_title, wb, first)
        first = False

    # Saving workbook
    wb.save(inst_stat_xlsx_path)


def _build_and_save_institutions_stat(norm_institutions_df, inst_types_file_path,
                                      inst_analysis_folder_path, year, xlsx_extent):
    """Builds and saves the institutions statistics from the publications data 
    with normalized institutions.

    This is done through the following steps:

    1. Builds a dataframe from the publications data with normalized institutions \
    by distributing the institutions list of each address by institution type \
    through the `_build_distributed_inst_df` internal function.  
    2. Saves the built dataframe through `save_formatted_df_to_xlsx` function \
    imported from the `bmfuncts.format_files` module.
    3. Builds and saves the institutions statistics through the \
    `_build_and_save_inst_stat_df` internal function.
    """
    # Setting useful column names aliases
    inst_type_abbr_col = bp.INST_TYPES_USECOLS[1]
    pub_id_col = bp.COL_NAMES['pub_id']
    country_col = pg.COL_NAMES_BONUS['country']
    institutions_col = pg.COL_NAMES_BONUS['institution']
    pub_nb_col = pg.COL_NAMES_BONUS["pub number"]
    pub_ids_col = pg.COL_NAMES_BONUS["pub_ids list"]
    
    # Setting useful columns list
    stat_cols_list = [institutions_col, country_col, pub_nb_col, pub_ids_col]

    # Setting folder and file names aliases
    distrib_inst_filename_alias = pg.ARCHI_YEAR["institutions distribution file name"] + xlsx_extent
    inst_stat_filename_alias = pg.ARCHI_YEAR["institution weight file name"] + xlsx_extent

    # Setting useful paths
    distrib_inst_file_path = inst_analysis_folder_path / Path(distrib_inst_filename_alias)
    inst_stat_xlsx_path = inst_analysis_folder_path / Path(inst_stat_filename_alias)

    # Getting institutions types data
    inst_types_df = pd.read_excel(inst_types_file_path, usecols = bp.INST_TYPES_USECOLS)
    inst_types_list = inst_types_df[inst_type_abbr_col].to_list()

    # Building distributed info of normalized institutions per type and per address
    distrib_institutions_df = _build_distributed_inst_df(norm_institutions_df, institutions_col,
                                                         inst_types_list)
    
    # Saving formatted df of distributed institutions
    distrib_inst_df_title = pg.DF_TITLES_LIST[11]
    sheet_name = 'Dirstibuted Inst ' + year
    save_formatted_df_to_xlsx(inst_analysis_folder_path, distrib_inst_filename_alias,
                              distrib_institutions_df, distrib_inst_df_title,
                              sheet_name)

    # Building and saving as multisheet openpyxl file the institutions statistics per institution type
    _build_and_save_inst_stat_df(distrib_institutions_df, inst_types_list,
                                 stat_cols_list, pub_id_col, inst_stat_xlsx_path)


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

    # Setting useful local aliases
    pub_id_alias = bp.COL_NAMES['pub_id']  # "Pub_id"
    country_alias = bp.COL_NAMES['country'][2]  # "Country"
    final_country_alias = pg.COL_NAMES_BONUS['country']  # "Pays"
    weight_alias = pg.COL_NAMES_BONUS['pub number']  # "Nombre de publications"
    pub_ids_alias = pg.COL_NAMES_BONUS["pub_ids list"]  # "Liste des Pub_ids"

    by_country_df = pd.DataFrame(columns=[final_country_alias, weight_alias, pub_ids_alias])
    idx_country = 0
    for country, pub_id_dg in countries_df.groupby(country_alias):
        pub_id_dg = pub_id_dg.drop_duplicates([pub_id_alias, country_alias])
        pub_ids_list = pub_id_dg[pub_id_alias].tolist()
        pub_ids_nb = len(pub_ids_list)
        by_country_df.loc[idx_country, final_country_alias] = country
        by_country_df.loc[idx_country, weight_alias] = pub_ids_nb
        if country != "France":
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_country_df.loc[idx_country, pub_ids_alias] = pud_ids_txt
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

    # Setting useful local aliases
    pub_id_alias = bp.COL_NAMES['pub_id']  # "Pub_id"
    country_alias = bp.COL_NAMES['country'][2]  # "Country"
    weight_alias = pg.COL_NAMES_BONUS['pub number']  # "Nombre de publications"
    pub_ids_alias = pg.COL_NAMES_BONUS["pub_ids list"]  # "Liste des Pub_ids"
    continent_alias = pg.COL_NAMES_BONUS['continent']  # "Continent"

    # Getting continent information by country from COUNTRIES_CONTINENT, a BiblioParsing global
    country_conti_dict = bp.COUNTRIES_CONTINENT

    # Replacing country by its continent in a copy of 'by_country_df'
    continents_df = countries_df.copy()
    continents_df[country_alias] = continents_df[country_alias].map(lambda x: country_conti_dict[x])

    # Renaming the column 'country_alias' to 'continent_alias'
    continents_df = continents_df.rename(columns={country_alias: continent_alias})

    by_continent_df = pd.DataFrame(columns=[continent_alias, weight_alias, pub_ids_alias])
    idx_continent = 0
    for continent, pub_id_dg in continents_df.groupby(continent_alias):
        pub_id_dg = pub_id_dg.drop_duplicates([pub_id_alias, continent_alias])
        pub_ids_list = pub_id_dg[pub_id_alias].tolist()
        pub_ids_nb = len(pub_ids_list)
        by_continent_df.loc[idx_continent, continent_alias] = continent
        by_continent_df.loc[idx_continent, weight_alias] = pub_ids_nb
        if continent != "Europe":
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_continent_df.loc[idx_continent, pub_ids_alias] = pud_ids_txt
        idx_continent += 1

    return by_continent_df


def _build_and_save_geo_stat(countries_df, analysis_folder_path, year, xlsx_extent):
    """Builds the publications statistics dataframes per country and per continent.
    
    First, it builds the statistics dataframes through the `_build_countries_stat` 
    and the `_build_continents_stat` internal functions.
    Then, it saves the statistics dataframes through the `_save_formatted_df_to_xlsx` 
    internal function.
    """
    # Setting aliases from globals
    geo_analysis_folder_alias = pg.ARCHI_YEAR["countries analysis"]
    country_weight_filename_alias = pg.ARCHI_YEAR["country weight file name"] + xlsx_extent
    continent_weight_filename_alias = pg.ARCHI_YEAR["continent weight file name"] + xlsx_extent

    # Setting useful paths
    geo_analysis_folder_path = analysis_folder_path / Path(geo_analysis_folder_alias)

    # Creating the required output folder
    if not os.path.exists(geo_analysis_folder_path):
        os.makedirs(geo_analysis_folder_path)

    # Building stat dataframes
    by_country_df = _build_countries_stat(countries_df)
    by_continent_df = _build_continents_stat(countries_df)

    # Saving formatted stat dataframes
    geo_df_title = pg.DF_TITLES_LIST[8]
    sheet_name = 'Pays ' + year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, country_weight_filename_alias,
                              by_country_df, geo_df_title, sheet_name)
    sheet_name = 'Continent ' + year
    save_formatted_df_to_xlsx(geo_analysis_folder_path, continent_weight_filename_alias,
                              by_continent_df, geo_df_title, sheet_name)

    return geo_analysis_folder_alias


def coupling_analysis(institute, org_tup, bibliometer_path,
                      datatype, year, progress_callback=None, verbose=False):
    """ Performs the analysis of countries and authors affiliations of Institute publications 
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
        (path): Full path to the folder where results of coupling analysis are saved.
    """

    # Setting useful local aliases
    dedup_folder = "dedup"
    xlsx_extent = ".xlsx"

    # Setting aliases from globals
    tsv_extent_alias = "." + pg.TSV_SAVE_EXTENT
    addresses_item_alias = bp.PARSING_ITEMS_LIST[2]
    pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    inst_analysis_folder_alias = pg.ARCHI_YEAR["institutions analysis"]
    pub_list_filename_base = pg.ARCHI_YEAR["pub list file name base"]
    institutions_folder_alias = pg.ARCHI_INSTITUTIONS["root"]
    inst_types_file_base_alias = pg.ARCHI_INSTITUTIONS["inst_types_base"]

    # Setting useful file names
    pub_list_filename = pub_list_filename_base + " " + str(year) + xlsx_extent
    inst_types_file_alias = institute + "_" + inst_types_file_base_alias

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(str(year))
    pub_list_folder_path = year_folder_path / Path(pub_list_folder_alias)
    pub_list_file_path = pub_list_folder_path / Path(pub_list_filename)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    inst_analysis_folder_path = analysis_folder_path / Path(inst_analysis_folder_alias)
    institutions_folder_path = bibliometer_path / Path(institutions_folder_alias)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(inst_analysis_folder_path):
        os.makedirs(inst_analysis_folder_path)
    if progress_callback:
        progress_callback(10)

    # Setting useful column names aliases
    final_col_dic, depts_col_list = set_final_col_names(institute, org_tup)
    final_pub_id_alias = final_col_dic['pub_id']
    parsing_pub_id_alias = bp.COL_NAMES['pub_id']

    # Getting the full paths of the working folder architecture for the corpus "year"
    config_tup = set_user_config(bibliometer_path, year, pg.BDD_LIST)
    parsing_path_dict = config_tup[1]
    item_filename_dict = config_tup[2]

    # Reading the full file of addresses
    addresses_item_file = item_filename_dict[addresses_item_alias] + tsv_extent_alias
    addresses_item_path = parsing_path_dict[dedup_folder] / Path(addresses_item_file)
    all_address_df = pd.read_csv(addresses_item_path, sep='\t')
    if progress_callback:
        progress_callback(15)

    # Selecting only addresses of Institute publications
    pub_df = pd.read_excel(pub_list_file_path,
                           usecols=[final_pub_id_alias] + depts_col_list)
    pub_num_list = [int(x.split("_")[1]) for x in pub_df[final_pub_id_alias].tolist()]
    inst_pub_addresses_df = pd.DataFrame()
    for pub_id, dg in all_address_df.groupby(parsing_pub_id_alias):
        if pub_id in pub_num_list:
            inst_pub_addresses_df = concat_dfs([inst_pub_addresses_df, dg])
    if verbose:
        print("Addresses of Institute publications selected.")
    if progress_callback:
        progress_callback(20)

    cols_tup = (final_pub_id_alias, parsing_pub_id_alias)
    paths_tup = (institutions_folder_path, inst_types_file_path)
    return_tup = _build_and_save_norm_raw_dfs(institute, inst_pub_addresses_df,
                                              inst_analysis_folder_path, year,
                                              xlsx_extent, cols_tup, paths_tup,
                                              progress_callback, verbose=verbose)
    countries_df, norm_institutions_df, raw_institutions_df = return_tup
    if verbose:
        print("normalized and raw institutions built and saved.")
    if progress_callback:
        progress_callback(80)

    # Building and saving inst stat dataframe
    _build_and_save_institutions_stat(norm_institutions_df, inst_types_file_path,
                                      inst_analysis_folder_path, year, xlsx_extent)
    if verbose:
        print("Distributed institutions and institutions stat built and saved.")
    if progress_callback:
        progress_callback(85)

    # Building and saving geo stat dataframes
    geo_analysis_folder_alias = _build_and_save_geo_stat(countries_df, analysis_folder_path,
                                                         year, xlsx_extent)
    if verbose:
        print("Geo stat built and saved.")
    if progress_callback:
        progress_callback(90)

    # Saving coupling analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["countries"] = True
    results_to_save_dict["continents"] = True
    results_to_save_dict["institutions"] = True
    if_analysis_name = None
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype, year,
                           if_analysis_name, results_to_save_dict, verbose=False)
    if progress_callback:
        progress_callback(100)

    return analysis_folder_alias, geo_analysis_folder_alias, inst_analysis_folder_alias
