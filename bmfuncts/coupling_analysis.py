"""Module of functions for publications-list analysis
in terms of geographical collaborations and inctitutions collaborations.

To do: Analysis of co-publication with other institutions and 
publications per OTPs.
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
from bmfuncts.config_utils import set_user_config
from bmfuncts.format_files import format_page
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
#        new_raw_institutions_df = pd.concat([new_raw_institutions_df, country_raw_inst_df])
    return new_raw_institutions_df


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
    through the `build_norm_raw_institutions` function imported from the package imported as bp, \
    using 'inst_pub_addresses_df' dataframe and specific files for this function; in these \
    datraframes, each row contains:

        - A publication IDs
        - The index of an address of the publication addresses 
        - The country of the given address
        - For the institutions dataframes, the list of normalized institutions or the list of raw \
        institutions for the given address.  

    4. Completes the normalized institutions and raw institutions dataframes with country \
    information by `_copy_dg_col_to_df` local function.
    5. Modifyes the publication_IDs by `_year_pub_id` local function in the 3 dataframes.
    6. Saves the normalized institutions and raw institutions dataframes through the \
    `_save_formatted_df_to_xlsx` local function.
    7. Builds the publications statistics dataframes per country and per continent using \
    the `_build_countries_stat` and `_build_continents_stat` internal functions.
    8. Saves the statistics dataframes through the `_save_formatted_df_to_xlsx` \
    local function.
    9. Saves the results of this analysis for the 'datatype' case through the \
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
        (path): Full path to the folder where results of keywords analysis are saved.
    """


    # Internal functions
    def _copy_dg_col_to_df(df, dg, col_alias):
        df[col_alias] = dg[col_alias]
        cols_list = [final_pub_id_alias, idx_address_alias, countries_col_alias, institutions_alias]
        df = df[cols_list]
        return df

    def _year_pub_id(df, year, pub_id_alias):
        """Transforms the column 'Pub_id' of the df
        by adding "yyyy_" to the value of the row.

        Args:
            df (pandas.DataFrame()): pandas.DataFrame() that we want to modify.
            year (str): 4 digits year of the corpus.
        Returns:
            (dataframe): the df with its changed column.
        """

        def _rename_pub_id(old_pub_id, year):
            pub_id_str = str(int(old_pub_id))
            while len(pub_id_str) < 3:
                pub_id_str = "0" + pub_id_str
            new_pub_id = str(int(year)) + '_' + pub_id_str
            return new_pub_id

        df[pub_id_alias] = df[pub_id_alias].apply(lambda x: _rename_pub_id(x, year))

    def _save_formatted_df_to_xlsx(results_path, item_filename, item_df,
                                   item_df_title, sheet_name, year):
        """Formats the 'item_df' dataframe through `format_page` function imported 
        from the `bmfuncts.format_files` module and saves it as xlsx workbook.
        """
        item_xlsx_file = item_filename + xlsx_extent
        item_xlsx_path = results_path / Path(item_xlsx_file)
        wb, ws = format_page(item_df, item_df_title)
        ws.title = sheet_name + year
        wb.save(item_xlsx_path)

    # Setting useful local aliases
    dedup_folder = "dedup"
    xlsx_extent = ".xlsx"

    # Setting aliases from globals
    tsv_extent_alias = "." + pg.TSV_SAVE_EXTENT
    addresses_item_alias = bp.PARSING_ITEMS_LIST[2]
    pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    geo_analysis_folder_alias = pg.ARCHI_YEAR["countries analysis"]
    inst_analysis_folder_alias = pg.ARCHI_YEAR["institutions analysis"]
    pub_list_filename_base = pg.ARCHI_YEAR["pub list file name base"]
    country_weight_filename_alias = pg.ARCHI_YEAR["country weight file name"]
    continent_weight_filename_alias = pg.ARCHI_YEAR["continent weight file name"]
    norm_inst_filename_alias = pg.ARCHI_YEAR["norm inst file name"]
    raw_inst_filename_alias = pg.ARCHI_YEAR["raw inst file name"]
    institutions_folder_alias = pg.ARCHI_INSTITUTIONS["root"]
    inst_types_file_base_alias = pg.ARCHI_INSTITUTIONS["inst_types_base"]
    country_affiliations_file_base_alias = pg.ARCHI_INSTITUTIONS["affiliations_base"]
    country_towns_file_base_alias = pg.ARCHI_INSTITUTIONS["country_towns_base"]
    country_unkept_inst_file_base_alias = pg.ARCHI_INSTITUTIONS["unkept_affil_base"]

    # Setting useful file names
    pub_list_filename = pub_list_filename_base + " " + str(year) + xlsx_extent
    inst_types_file_alias = institute + "_" + inst_types_file_base_alias
    country_affil_file_alias = institute + "_" + country_affiliations_file_base_alias
    country_towns_file_alias = institute + "_" + country_towns_file_base_alias
    country_unkept_affil_file_alias = institute + "_" + country_unkept_inst_file_base_alias

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(str(year))
    pub_list_folder_path = year_folder_path / Path(pub_list_folder_alias)
    pub_list_file_path = pub_list_folder_path / Path(pub_list_filename)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    geo_analysis_folder_path = analysis_folder_path / Path(geo_analysis_folder_alias)
    inst_analysis_folder_path = analysis_folder_path / Path(inst_analysis_folder_alias)
    institutions_folder_path = bibliometer_path / Path(institutions_folder_alias)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file_alias)
    country_affil_file_path = institutions_folder_path / Path(country_affil_file_alias)
    country_unkept_affil_file_path = institutions_folder_path / Path(country_unkept_affil_file_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(geo_analysis_folder_path):
        os.makedirs(geo_analysis_folder_path)
    if not os.path.exists(inst_analysis_folder_path):
        os.makedirs(inst_analysis_folder_path)
    if progress_callback:
        progress_callback(10)

    # Setting useful column names aliases
    final_col_dic, depts_col_list = set_final_col_names(institute, org_tup)
    final_pub_id_alias = final_col_dic['pub_id']
    parsing_pub_id_alias = bp.COL_NAMES['pub_id']
    idx_address_alias = bp.COL_NAMES['institution'][1]
    institutions_alias = bp.COL_NAMES['institution'][2]
    countries_col_alias = bp.COL_NAMES['country'][2]

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
#            inst_pub_addresses_df = pd.concat([inst_pub_addresses_df, dg])
    if progress_callback:
        progress_callback(20)

    # Building countries, normalized institutions and still not normalized ones
    file_path_0 = inst_types_file_path
    file_path_1 = country_affil_file_path
    file_path_2 = country_towns_file_alias
    file_path_3 = institutions_folder_path
    return_tup = bp.build_norm_raw_institutions(inst_pub_addresses_df,
                                                inst_types_file_path=file_path_0,
                                                country_affiliations_file_path=file_path_1,
                                                country_towns_file=file_path_2,
                                                country_towns_folder_path=file_path_3,
                                                verbose=verbose)
    countries_df, norm_institutions_df, raw_institutions_df = return_tup
    if progress_callback:
        progress_callback(60)

    # Adding countries column to 'norm_institutions_df' and 'raw_institutions_df'
    norm_institutions_df = _copy_dg_col_to_df(norm_institutions_df, countries_df,
                                              countries_col_alias)
    raw_institutions_df = _copy_dg_col_to_df(raw_institutions_df, countries_df,
                                             countries_col_alias)
    if progress_callback:
        progress_callback(65)

    # Building pub IDs with year information
    _year_pub_id(countries_df, year, parsing_pub_id_alias)
    _year_pub_id(norm_institutions_df, year, parsing_pub_id_alias)
    _year_pub_id(raw_institutions_df, year, parsing_pub_id_alias)
    if progress_callback:
        progress_callback(70)

    # Removing unkept institutions from 'raw_institutions_df'
    raw_affil_col = 'Raw affiliations'
    cols_tup = (countries_col_alias, raw_affil_col, institutions_alias)
    raw_institutions_df = _clean_unkept_affil(raw_institutions_df,
                                              country_unkept_affil_file_path,
                                              cols_tup)
    if progress_callback:
        progress_callback(75)

    # Saving formatted df of normalized and raw institutions
    inst_df_title = pg.DF_TITLES_LIST[9]
    _save_formatted_df_to_xlsx(inst_analysis_folder_path, norm_inst_filename_alias,
                               norm_institutions_df, inst_df_title, 'Norm Inst ', year)
    _save_formatted_df_to_xlsx(inst_analysis_folder_path, raw_inst_filename_alias,
                               raw_institutions_df, inst_df_title, 'Raw Inst ', year)
    if progress_callback:
        progress_callback(80)

    # Building stat dataframes
    by_country_df = _build_countries_stat(countries_df)
    by_continent_df = _build_continents_stat(countries_df)

    # Saving formatted stat dataframes
    geo_df_title = pg.DF_TITLES_LIST[8]
    _save_formatted_df_to_xlsx(geo_analysis_folder_path, country_weight_filename_alias,
                               by_country_df, geo_df_title, 'Pays', year)
    _save_formatted_df_to_xlsx(geo_analysis_folder_path, continent_weight_filename_alias,
                               by_continent_df, geo_df_title, 'Continent', year)
    if progress_callback:
        progress_callback(90)

    # Saving coupling analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["countries"] = True
    results_to_save_dict["continents"] = True
    if_analysis_name = None
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype, year,
                           if_analysis_name, results_to_save_dict, verbose=False)
    if progress_callback:
        progress_callback(100)

    return analysis_folder_alias, geo_analysis_folder_alias, inst_analysis_folder_alias
