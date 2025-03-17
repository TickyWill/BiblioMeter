"""Module of functions for collaborating institutions analysis.

"""

__all__ = ['build_and_save_institutions_stat']

# Standard Library imports
import re
from pathlib import Path
from string import Template

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl import Workbook as openpyxl_Workbook

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.useful_functs import concat_dfs


def _build_distributed_inst_df(norm_institutions_df, institutions_col, inst_types_list):
    """Distributes the column that contains the list of the normalized institutions 
    of a publication and an author address into a column for each institution type.
    
    ex: "Institution" col value = UGA Univ; USMB Univ; CNRS Nro; G-INP Sch; IMEP-LaHC Lab
        => "Univ" col value = "['UGA Univ', 'USMB Univ']"
        => "Nro" col value = "['CNRS Nro']"
        => "Sch" col value = "['G-INP Sch']"
        => "Lab" col value = "['IMEP-LaHC Lab']"
        => Other type col value = "[]"
    """
    set_words_template = Template(r'[\s]$word$$')
    distrib_institutions_df = pd.DataFrame()
    for _, row in norm_institutions_df.iterrows():
        inst_list = row[institutions_col].split("; ")
        for inst_type in inst_types_list:
            re_search_words = re.compile(set_words_template.substitute({"word":inst_type}))
            row[inst_type] = [inst for inst in inst_list if re.search(re_search_words, inst)]
        row_df = row.to_frame().T.astype(str)
        distrib_institutions_df = concat_dfs([distrib_institutions_df, row_df])
    distrib_institutions_df = distrib_institutions_df.astype(str)
    return distrib_institutions_df


def _set_inst_names_list(inst_names):
    """Converts the string containing a list of institutions into a list.
    
    ex: "['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']" 
        => ['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']
    """
    inst_names = inst_names[1:len(inst_names)-1]
    inst_names_list = inst_names.split(", ")
    final_inst_names_list = [x[1:len(x)-1] for x in inst_names_list]
    return final_inst_names_list


def _build_pub_id_inst_type_df(distrib_institutions_df, cols_list):
    """Builds the data with one row per institution name and its country 
    for each publication for a given type of institutions.
    """
    # Setting useful column names
    pub_id_col, bp_country_col, inst_type_col = cols_list

    # Building tha dataframe with one row per list of institutions of type 
    # 'inst_type' set through 'inst_type_col' per country for each publication
    full_inst_list = []
    pub_id_inst_type_df = pd.DataFrame(columns=cols_list)
    for pub_id, pub_id_df in distrib_institutions_df.groupby(pub_id_col):
        data = []
        for country, country_df in pub_id_df.groupby(bp_country_col):
            pub_id_inst_list = []
            for _, row in country_df.iterrows():
                inst_names = row[inst_type_col]
                if inst_names!="[]":
                    inst_names_list = _set_inst_names_list(inst_names)
                    pub_id_inst_list += inst_names_list
            pub_id_inst_list = list(set(pub_id_inst_list))
            full_inst_list += pub_id_inst_list
            data.append([pub_id, country, str(pub_id_inst_list)])
        pub_inst_df = pd.DataFrame(data, columns=cols_list)
        pub_id_inst_type_df = concat_dfs([pub_id_inst_type_df, pub_inst_df])
    full_inst_list = list(set(full_inst_list))
    corrected_inst_list = [x for x in full_inst_list if x!="LITEN Rto"]

    # Building the dataframe with one row per institution name and country
    # for each publication
    final_pub_id_inst_type_df = pd.DataFrame(columns=cols_list)
    for inst_name in corrected_inst_list:
        for _, row in pub_id_inst_type_df.iterrows():
            inst_names = row[inst_type_col]
            pub_id = row[pub_id_col]
            if inst_names!="[]":
                inst_names_list = _set_inst_names_list(inst_names)
                data = []
                if inst_name in inst_names_list:
                    pub_id = row[pub_id_col]
                    country = row[bp_country_col]
                    data.append([pub_id, country, inst_name])
                if data:
                    pub_id_inst_name_df = pd.DataFrame(data, columns=cols_list)
                    final_pub_id_inst_type_df = concat_dfs([final_pub_id_inst_type_df,
                                                            pub_id_inst_name_df])
    return final_pub_id_inst_type_df


def _build_inst_type_inst_df(final_pub_id_inst_type_df,
                             input_cols_list, stat_cols_list):
    """Builds the statistics data for a given type of institutions.
    """
    # Setting col names from args
    pub_id_col, bp_country_col, inst_type_col = input_cols_list
    pg_country_col, inst_col, _, _, pub_nb_col, pub_ids_col = stat_cols_list

    # Building the dataframe with the statistics data per institution
    # for a given type of institutions
    data_cols = [inst_col, pg_country_col, pub_nb_col, pub_ids_col]
    inst_type_inst_df = pd.DataFrame(columns=data_cols)
    for inst_name, inst_name_df in final_pub_id_inst_type_df.groupby(inst_type_col):
        countries_list = sorted(inst_name_df[bp_country_col].to_list())
        for idx_row, row in inst_name_df.iterrows():
            country = row[bp_country_col]
            if country==bp.UNKNOWN:
                inst_name_df.loc[idx_row, bp_country_col] = countries_list[0]
        data = []
        for country, country_df in inst_name_df.groupby(bp_country_col):
            pub_nb = len(country_df[pub_id_col])
            pub_list = "; ".join(country_df[pub_id_col].to_list())
            data.append([inst_name, country, pub_nb, pub_list])
            country_inst_name_df = pd.DataFrame(data, columns=data_cols)
            inst_type_inst_df = concat_dfs([inst_type_inst_df, country_inst_name_df])
    inst_type_inst_df = inst_type_inst_df.drop_duplicates()

    # Sorting the built dataframe by publications number for each counrtry
    sorted_inst_type_inst_df = pd.DataFrame(columns=data_cols)
    for country, country_df in inst_type_inst_df.groupby(pg_country_col):
        country_df = country_df.sort_values(by=[pub_nb_col], ascending=False)
        sorted_inst_type_inst_df = concat_dfs([sorted_inst_type_inst_df, country_df])
    return sorted_inst_type_inst_df


def _build_inst_type_pub_id_df(final_pub_id_inst_type_df, input_cols_list,
                               stat_cols_list):
    """Builds, for a given type of institutions, data with, on the one hand, 
    one row per publication with attached countries number and countries list 
    and, on the other hand, one row per publication and country with attached 
    number of institutions and list of institutions."""
    # Setting col names from args
    pub_id_col, bp_country_col, inst_type_col = input_cols_list
    pg_country_col, _, inst_nb_col, inst_list_col, _, _ = stat_cols_list

    # Building stat per country for given inst_type
    institutions_cols_list = [pub_id_col, pg_country_col,
                              inst_nb_col, inst_list_col]
    pub_country_inst_df = pd.DataFrame(columns=institutions_cols_list)

    institutions_data = []
    for pub_id, pub_id_df in final_pub_id_inst_type_df.groupby(pub_id_col):
        for country, country_df in pub_id_df.groupby(bp_country_col):
            institutions_list = list(set(country_df[inst_type_col].to_list()))
            institutions_nb = len(institutions_list)
            institutions_list_str = "; ".join(institutions_list)
            institutions_data.append([pub_id, country, institutions_nb,
                                      institutions_list_str])
    pub_country_inst_df = pd.DataFrame(institutions_data,
                                       columns=institutions_cols_list)

    # Sorting the built dataframe by pub_id_col and by counrtry
    pub_country_inst_df = pub_country_inst_df.sort_values(by=[pub_id_col,
                                                              pg_country_col])        
    return pub_country_inst_df


def _build_inst_type_country_df(pub_country_inst_df, input_cols_list, stat_cols_list):
    """Builds data with one row per country with attached number 
    of publications and list of publications for a given type of institutions."""

    # Setting col names from args
    pub_id_col, _, inst_type = input_cols_list
    country_col, _, inst_nb_col, inst_list_col, pub_nb_col, pub_ids_col = stat_cols_list

    # Building stat per country for given inst_type
    data_cols_list = [country_col, inst_nb_col, inst_list_col,
                      pub_nb_col, pub_ids_col]
    country_inst_pub_df = pd.DataFrame(columns=data_cols_list)
    pub_data = []
    inst_data = []
    data = []
    for country, country_df in pub_country_inst_df.groupby(country_col):
        pub_ids_list = list(set(country_df[pub_id_col].to_list()))
        pub_ids_nb = len(pub_ids_list)
        pub_ids_list_str = "; ".join(pub_ids_list)

        init_inst_list = country_df[inst_list_col].to_list()
        full_inst_list = sum([x.split("; ") for x in init_inst_list], [])
        institutions_list = list(set(full_inst_list))
        institutions_nb = len(institutions_list)
        institutions_list_str = "; ".join(institutions_list)
        
        data.append([country, institutions_nb, institutions_list_str,
                     pub_ids_nb, pub_ids_list_str])
    country_inst_pub_df = pd.DataFrame(data, columns=data_cols_list)
    return country_inst_pub_df


def _build_inst_stat_data(distrib_institutions_df, common_cols_list, stat_cols_list):
    """Builds 3 dataframes of institutions statistics for each inst_type.
    
    This is done through the use of the `_build_pub_id_inst_type_df`,
    `_build_inst_type_inst_df`, `_build_inst_type_pub_id_df` and 
    `_build_inst_type_country_df` internal functions."""
    stat_keys_alias = list(pg.STAT_FILE_DICT.keys())
    inst_type_data_dict = {}
    for inst_type in pg.STAT_INST_TYPES_LIST:
        inst_type_data_dict[inst_type] = {}
        
        # Setting useful columns list
        input_cols_list = common_cols_list + [inst_type]

        # Building data for inst_type stat computing
        final_pub_id_inst_type_df = _build_pub_id_inst_type_df(distrib_institutions_df,
                                                               input_cols_list)        
        inst_type_inst_df = _build_inst_type_inst_df(final_pub_id_inst_type_df,
                                                     input_cols_list, stat_cols_list)
        pub_country_inst_df = _build_inst_type_pub_id_df(final_pub_id_inst_type_df,
                                                         input_cols_list, stat_cols_list)
        country_inst_pub_df = _build_inst_type_country_df(pub_country_inst_df,
                                                           input_cols_list, stat_cols_list)

        # Setting 'inst_type_dict' at 'inst_type' key
        inst_type_data_dict[inst_type][stat_keys_alias[0]] = inst_type_inst_df
        inst_type_data_dict[inst_type][stat_keys_alias[1]] = pub_country_inst_df
        inst_type_data_dict[inst_type][stat_keys_alias[2]] = country_inst_pub_df
    return inst_type_data_dict


def _save_inst_stat_data(inst_type_data_dict, inst_stat_path):
    """Saves the data of the institutions statistics into multisheet 
    openpyxl workbooks with a sheet per institution type.

    This done by cycling on institution type with the following steps:

    1. A dataframe is selected in the institutions statistics dict.
    2. A sheet is added to the openpyxl workbook containing the data 
    of the dataframe through the `format_wb_sheet` function 
    imported from the `bmfuncts.format_files` module. 
    """
    inst_types_list = inst_type_data_dict.keys()
    for stat_key, value_tup in pg.STAT_FILE_DICT.items():
        stat_file, df_title_idx = value_tup  
        # Initialize parameters for saving results as multisheet workbook
        first = True
        wb = openpyxl_Workbook()

        inst_stat_xlsx_path = inst_stat_path / Path(stat_file + ".xlsx")
        for inst_type in inst_types_list:
            inst_type_stat_df = inst_type_data_dict[inst_type][stat_key]

            inst_sheet_name = inst_type
            inst_stat_title = pg.DF_TITLES_LIST[df_title_idx]
            wb = format_wb_sheet(inst_sheet_name, inst_type_stat_df,
                                 inst_stat_title, wb, first)
            first = False
        # Saving workbook
        wb.save(inst_stat_xlsx_path)


def _build_and_save_inst_stat_data(distrib_institutions_df,
                                   inst_analysis_folder_path):
    """Builds and saves data of institutions statistics into  
    multisheet openpyxl workbooks with a sheet per institution type.

    This done through the following steps:

    1. For each inst_type, 3 dataframes of institutions statistics 
    are built through the `_build_inst_stat_data` internal function.
    2. The data are saved as multisheet openpyxl workbooks through 
    the `_save_inst_stat_data` internal function.
    """
    # Setting useful column alias
    pub_id_col_alias = bp.COL_NAMES['pub_id']
    bp_country_col_alias = bp.COL_NAMES['address_inst'][3]
    pg_country_col_alias = pg.COL_NAMES_BONUS['country']
    inst_col_alias = pg.COL_NAMES_BONUS['institution']
    pub_nb_col_alias = pg.COL_NAMES_BONUS["pub number"]
    pub_ids_col_alias = pg.COL_NAMES_BONUS["pub_ids list"]
    inst_nb_col_alias = pg.COL_NAMES_BONUS["inst number"]
    inst_list_col_alias = pg.COL_NAMES_BONUS["inst list"]

    # Setting useful columns list
    common_cols_list = [pub_id_col_alias, bp_country_col_alias]
    stat_cols_list = [pg_country_col_alias, inst_col_alias,
                      inst_nb_col_alias, inst_list_col_alias, 
                      pub_nb_col_alias, pub_ids_col_alias]

    inst_type_data_dict = _build_inst_stat_data(distrib_institutions_df,
                                                common_cols_list,
                                                stat_cols_list)
    _save_inst_stat_data(inst_type_data_dict, inst_analysis_folder_path)


def build_and_save_institutions_stat(norm_institutions_df, inst_types_file_path,
                                     inst_analysis_folder_path, year):
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
    # Setting local parameters
    xlsx_extent = ".xlsx"

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
    inst_stat_xlsx_path = inst_analysis_folder_path / Path(inst_stat_filename_alias)

    # Getting institutions types data
    inst_types_df = pd.read_excel(inst_types_file_path, usecols = bp.INST_TYPES_USECOLS)
    inst_types_list = inst_types_df[inst_type_abbr_col].to_list()

    # Building distributed info of normalized institutions per type and per address
    distrib_institutions_df = _build_distributed_inst_df(norm_institutions_df, institutions_col,
                                                         inst_types_list)

    # Saving formatted df of distributed institutions
    distrib_inst_df_title = pg.DF_TITLES_LIST[11]
    sheet_name = 'Distributed Inst ' + year
    save_formatted_df_to_xlsx(inst_analysis_folder_path, distrib_inst_filename_alias,
                              distrib_institutions_df, distrib_inst_df_title,
                              sheet_name)

    # Building and saving as multisheet openpyxl files the data of institutions statistics 
    _build_and_save_inst_stat_data(distrib_institutions_df, inst_analysis_folder_path)
