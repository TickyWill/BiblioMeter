"""Module of functions for collaborating institutions analysis.

"""

__all__ = ['build_and_save_institutions_stat']

# Standard Library imports
from pathlib import Path

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
    distrib_institutions_df = pd.DataFrame()
    for _, row in norm_institutions_df.iterrows():
        inst_list = row[institutions_col].split("; ")
        for inst_type in inst_types_list:
            inst_type_check_str = " " + inst_type
            row[inst_type] = [inst for inst in inst_list if inst_type_check_str in inst]
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
            inst_names = row[inst_type]
            pub_id = row[pub_id_col]
            if inst_names!="[]":
                inst_names_list = _set_inst_names_list(inst_names)
                data = []
                if inst_name in inst_names_list:
                    pub_id = row[pub_id_col]
                    country = row[bp_country_col_alias]
                    data.append([pub_id, country, inst_name])
                if data:
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
        inst_stat_title = pg.DF_TITLES_LIST[12]
        wb = format_wb_sheet(inst_sheet_name, inst_type_stat_df, inst_stat_title, wb, first)
        first = False

    # Saving workbook
    wb.save(inst_stat_xlsx_path)


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

    # Building and saving as multisheet openpyxl file the institutions statistics per institution type
    _build_and_save_inst_stat_df(distrib_institutions_df, inst_types_list,
                                 stat_cols_list, pub_id_col, inst_stat_xlsx_path)
