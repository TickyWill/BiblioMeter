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
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.useful_functs import concat_dfs


def _set_inst_stat_cols():
    """Builds a dict setting selected columns names for the process 
    of building institutions statistics.

    Returns:
        (dict): The built dict.
    """
    inst_stat_cols_dic = {'pub_id_col'       : bp.COL_NAMES['pub_id'],
                          'country_col'      : bp.COL_NAMES['country'][2],
                          'final_country_col': bm_pg.COL_NAMES_BONUS['country'],
                          'inst_col'         : bm_pg.COL_NAMES_BONUS['institution'],
                          'pub_nb_col'       : bm_pg.COL_NAMES_BONUS["pub number"],
                          'pub_ids_col'      : bm_pg.COL_NAMES_BONUS["pub_ids list"],
                          'inst_nb_col'      : bm_pg.COL_NAMES_BONUS["inst number"],
                          'inst_list_col'    : bm_pg.COL_NAMES_BONUS["inst list"],
                          'journal_nb_col'   : bm_pg.COL_NAMES_BONUS['journal_pub_nb'],
                          'proc_nb_col'      : bm_pg.COL_NAMES_BONUS['proceedings_pub_nb'],
                          'book_nb_col'      : bm_pg.COL_NAMES_BONUS['book_pub_nb'],
                        }

    return inst_stat_cols_dic


def _build_distributed_inst_df(norm_institutions_df, institutions_col, inst_types_list,
                               progress_param=None):
    """Distributes the column that contains the list of the normalized institutions 
    of a publication and an author address into a column for each institution type.

    ex: "Institution" col value = UGA Univ; USMB Univ; CNRS Nro; G-INP Sch; IMEP-LaHC Lab
        => "Univ" col value = "['UGA Univ', 'USMB Univ']"
        => "Nro" col value = "['CNRS Nro']"
        => "Sch" col value = "['G-INP Sch']"
        => "Lab" col value = "['IMEP-LaHC Lab']"
        => Other type col value = "[]"

    Args:
        norm_institutions_df (dataframe): Data of the normalized institutions per publication.
        institutions_col (str): Column name of the normalized institutions list in \
        the 'norm-institution_df' dataframe.
        inst_types_list (list): Institution types that are used as column names in the built data.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    Returns:
        (dataframe): The built data with distributed normalized institutions per institution \
        type and per publication.
    """
    if progress_param:
        step_nb = len(norm_institutions_df) * len(inst_types_list)
        progress_callback, progress_init, progress_final = progress_param
        progress_step = (progress_final - progress_init) / step_nb
        progress_status = progress_init
        progress_callback(progress_status)

    set_words_template = Template(r'[\s]$word$$')
    distrib_institutions_df = pd.DataFrame()
    for _, row in norm_institutions_df.iterrows():
        inst_list = row[institutions_col].split("; ")
        for inst_type in inst_types_list:
            re_search_words = re.compile(set_words_template.substitute({"word":inst_type}))
            row[inst_type] = [inst for inst in inst_list if re.search(re_search_words, inst)]
            if progress_param:
                progress_status += progress_step
                progress_callback(progress_status)
        row_df = row.to_frame().T.astype(str)
        distrib_institutions_df = concat_dfs([distrib_institutions_df, row_df])
    distrib_institutions_df = distrib_institutions_df.astype(str)
    return distrib_institutions_df


def _set_inst_names_list(inst_names):
    """Converts the string containing a list of institutions into a list.

    ex: "['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']" 
        => ['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']

    Args:
        inst_names (str): Contains the list of institutions.
    Returns:
        (list): The list of institutions names (str).
    """
    inst_names = inst_names[1:len(inst_names)-1]
    inst_names_list = inst_names.split(", ")
    final_inst_names_list = [x[1:len(x)-1] for x in inst_names_list]
    return final_inst_names_list


def _build_pub_id_inst_type_df(institute, distrib_institutions_df,
                               institute_pub_ids_list, cols_list):
    """Builds the data with one row per institution name and its country 
    for each publication for a given type of institutions.

    Args:
        institute (str): Institute name.
        distrib_institutions_df (dataframe): data with distributed normalized \
        institutions per institution type and per publication.
        institute_pub_ids_list (list): All publication IDs (str) of the institute.
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data. 
    """
    # Setting useful column names
    pub_id_col, country_col, inst_type_col = cols_list

    # Setting out of stat institutions
    out_inst = institute.upper() + " Rto"

    # Building the dataframe with one row per list of institutions of type
    # 'inst_type' set through 'inst_type_col' per country for each publication
    full_inst_list = []
    data_cols = cols_list
    pub_id_inst_type_df = pd.DataFrame(columns=data_cols)
    for pub_id, pub_id_df in distrib_institutions_df.groupby(pub_id_col):
        if pub_id in institute_pub_ids_list:
            data = []
            for country, country_df in pub_id_df.groupby(country_col):
                pub_id_inst_list = []
                for _, row in country_df.iterrows():
                    inst_names = row[inst_type_col]
                    if inst_names!="[]":
                        inst_names_list = _set_inst_names_list(inst_names)
                        pub_id_inst_list += inst_names_list
                pub_id_inst_list = list(set(pub_id_inst_list))
                full_inst_list += pub_id_inst_list
                data.append([pub_id, country, str(pub_id_inst_list)])
            pub_inst_df = pd.DataFrame(data, columns=data_cols)
            pub_id_inst_type_df = concat_dfs([pub_id_inst_type_df, pub_inst_df])
    full_inst_list = list(set(full_inst_list))
    corrected_inst_list = [x for x in full_inst_list if x!=out_inst]

    # Building the dataframe with one row per institution name and country
    # for each publication
    final_pub_id_inst_type_df = pd.DataFrame(columns=data_cols)
    for inst_name in corrected_inst_list:
        for _, row in pub_id_inst_type_df.iterrows():
            inst_names = row[inst_type_col]
            pub_id = row[pub_id_col]
            if inst_names!="[]":
                inst_names_list = _set_inst_names_list(inst_names)
                data = []
                if inst_name in inst_names_list:
                    pub_id = row[pub_id_col]
                    country = row[country_col]
                    data.append([pub_id, country, inst_name])
                if data:
                    pub_id_inst_name_df = pd.DataFrame(data, columns=data_cols)
                    final_pub_id_inst_type_df = concat_dfs([final_pub_id_inst_type_df,
                                                            pub_id_inst_name_df])
    return final_pub_id_inst_type_df


def _build_inst_type_inst_df(final_pub_id_inst_type_df, sub_pub_ids_lists, cols_list):
    """Builds data with one row per institution and attached country, 
    number of publications and list of publications IDs for a given type 
    of institutions.

    Args:
        final_pub_id_inst_type_df (dataframe): The data with one row \
        per institution name and its country for each publication \
        for a given type of institutions.
        sub_pub_ids_lists (tuple): (list of the IDs (str) of publications \
        in journals, list of the IDs (str) of publications in conference \
        proceedings, list of the IDs (str) of publications in books).
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting pub_ids lists
    journal_pub_ids_list, proceedings_pub_ids_list, books_pub_ids_list = sub_pub_ids_lists

    # Setting col names from 'inst_type_inst_cols'
    (pub_id_col, country_col, final_country_col, inst_col, journal_nb_col, proc_nb_col,
     book_nb_col, pub_nb_col, pub_ids_col, inst_type_col) = cols_list

    # Building the dataframe with the statistics data per institution
    # for a given type of institutions
    data_cols = [inst_col, final_country_col, journal_nb_col,
                 proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    inst_type_inst_df = pd.DataFrame(columns=data_cols)
    for inst_name, inst_name_df in final_pub_id_inst_type_df.groupby(inst_type_col):
        countries_list = sorted(inst_name_df[country_col].to_list())
        for idx_row, row in inst_name_df.iterrows():
            country = row[country_col]
            if country==bp.UNKNOWN:
                inst_name_df.loc[idx_row, country_col] = countries_list[0]
        data = []
        for country, country_df in inst_name_df.groupby(country_col):
            pub_ids_list = country_df[pub_id_col].to_list()
            pub_nb = len(pub_ids_list)
            journal_pub_nb = len([x for x in pub_ids_list if x in journal_pub_ids_list])
            proceedings_pub_nb = len([x for x in pub_ids_list if x in proceedings_pub_ids_list])
            book_pub_nb = len([x for x in pub_ids_list if x in books_pub_ids_list])
            pub_ids_txt = "; ".join(pub_ids_list)
            data.append([inst_name, country, journal_pub_nb,
                         proceedings_pub_nb, book_pub_nb, pub_nb, pub_ids_txt])
            country_inst_name_df = pd.DataFrame(data, columns=data_cols)
            inst_type_inst_df = concat_dfs([inst_type_inst_df, country_inst_name_df])
    inst_type_inst_df = inst_type_inst_df.drop_duplicates()

    # Sorting the built dataframe by publications number for each country
    sorted_inst_type_inst_df = pd.DataFrame(columns=data_cols)
    for country, country_df in inst_type_inst_df.groupby(final_country_col):
        country_df = country_df.sort_values(by=[pub_nb_col], ascending=False)
        sorted_inst_type_inst_df = concat_dfs([sorted_inst_type_inst_df, country_df])
    return sorted_inst_type_inst_df


def _build_inst_type_pub_id_df(final_pub_id_inst_type_df, cols_list):
    """Builds data with one row per publication and country with attached 
    number of institutions and list of institutions for a given type of 
    institutions.

    Args:
        final_pub_id_inst_type_df (dataframe): The data with one row \
        per institution name and its country for each publication \
        for a given type of institutions.
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting col names from 'cols_list'
    (pub_id_col, country_col, final_country_col,
     inst_nb_col, inst_list_col, inst_type_col) = cols_list

    # Building stat per country for given inst_type
    data_cols = [pub_id_col, final_country_col,
                 inst_nb_col, inst_list_col]
    data = []
    for pub_id, pub_id_df in final_pub_id_inst_type_df.groupby(pub_id_col):
        for country, country_df in pub_id_df.groupby(country_col):
            institutions_list = list(set(country_df[inst_type_col].to_list()))
            institutions_nb = len(institutions_list)
            institutions_list_str = "; ".join(institutions_list)
            data.append([pub_id, country, institutions_nb, institutions_list_str])
    pub_country_inst_df = pd.DataFrame(data, columns=data_cols)

    # Sorting the built dataframe by pub_id_col and by country
    pub_country_inst_df = pub_country_inst_df.sort_values(by=[pub_id_col,
                                                              final_country_col])
    return pub_country_inst_df


def _build_inst_type_country_df(pub_country_inst_df, sub_pub_ids_lists, cols_list):
    """Builds data with one row per country with attached number of 
    publications and list of publications IDs for a given type of institutions.

    Args:
        pub_country_inst_df (dataframe): The data with one row per publication \
        and country with attached number of institutions and list of institutions \
        as built through the `_build_inst_type_pub_id_df` internal function \
        for the given type of institutions.
        sub_pub_ids_lists (tuple): (list of the IDs (str) of publications in journals, \
        list of the IDs (str) of publications in conference proceedings, \
        list of the IDs (str) of publications in books).
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting pub_ids lists
    journal_pub_ids_list, proceedings_pub_ids_list, books_pub_ids_list = sub_pub_ids_lists

    # Setting col names from 'cols_list'
    (pub_id_col, country_col, inst_nb_col, inst_list_col, journal_nb_col, proc_nb_col,
     book_nb_col, pub_nb_col, pub_ids_col) = cols_list

    # Building stat per country for given inst_type
    data_cols = [country_col, inst_nb_col, inst_list_col, journal_nb_col,
                 proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    data = []
    for country, country_df in pub_country_inst_df.groupby(country_col):
        pub_ids_list = list(set(country_df[pub_id_col].to_list()))
        pub_ids_nb = len(pub_ids_list)
        journal_pub_nb = len([x for x in pub_ids_list if x in journal_pub_ids_list])
        proceedings_pub_nb = len([x for x in pub_ids_list if x in proceedings_pub_ids_list])
        book_pub_nb = len([x for x in pub_ids_list if x in books_pub_ids_list])

        pub_ids_list_str = "; ".join(pub_ids_list)

        init_inst_list = country_df[inst_list_col].to_list()
        full_inst_list = sum([x.split("; ") for x in init_inst_list], [])
        institutions_list = list(set(full_inst_list))
        institutions_nb = len(institutions_list)
        institutions_list_str = "; ".join(institutions_list)

        data.append([country, institutions_nb, institutions_list_str,
                     journal_pub_nb, proceedings_pub_nb, book_pub_nb,
                     pub_ids_nb, pub_ids_list_str])
    country_inst_pub_df = pd.DataFrame(data, columns=data_cols)
    return country_inst_pub_df


def _build_useful_cols_lists(inst_stat_cols_dic):

    # Setting col names from 'inst_stat_cols_dic'
    col_keys = ['pub_id_col', 'country_col', 'final_country_col',
                'inst_col', 'inst_nb_col', 'inst_list_col', 
                'journal_nb_col', 'proc_nb_col', 'book_nb_col',
                'pub_nb_col', 'pub_ids_col']
    (pub_id_col, country_col, final_country_col,
     inst_col, inst_nb_col, inst_list_col,
     journal_nb_col, proc_nb_col, book_nb_col,
     pub_nb_col, pub_ids_col) = [inst_stat_cols_dic[key] for key in col_keys]

    # Setting col lists
    cols_list_1 = [pub_id_col, country_col]
    cols_list_2 = [pub_id_col, country_col, final_country_col, inst_col,
                   journal_nb_col, proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    cols_list_3 = [pub_id_col, country_col, final_country_col, inst_nb_col, inst_list_col]
    cols_list_4 = [pub_id_col, final_country_col, inst_nb_col, inst_list_col,
                   journal_nb_col, proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]

    return cols_list_1, cols_list_2, cols_list_3, cols_list_4


def _build_inst_stat_data(institute, distrib_institutions_df, pub_ids_lists, inst_stat_cols_dic):
    """Builds 3 dataframes of institutions statistics for each institution type.

    This done through the cycling on the list of the institutions type 
    defined by the 'STAT_FILE_DICT' global. The cycled steps are as follows:

    1. Building the data with one row per institution name and its \
    country for each publication for the type of institutions through \
    the `_build_pub_id_inst_type_df` internal function.
    2. Building the 3 sets of statistical data for the type of institutions \
    through the `_build_inst_type_inst_df`, `_build_inst_type_pub_id_df` \
    and `_build_inst_type_country_df` internal functions.

    Args:
        institute (str): Institute name.
        distrib_institutions_df (dataframe): data with distributed normalized \
        institutions per institution type and per publication.
        common_cols_list (list): The  names (str) list of the common columns \
        used to build the data.
        stat_cols_list (list): The names (str) list of the specific columns \
        that will contain the statistics results in the built data.
        pub_ids_lists (tuple): (list of all publication IDs (str) of the institute, \
        list of the IDs (str) of publications in journals, \
        list of the IDs (str) of publications in conference proceedings, \
        list of the IDs (str) of publications in books).
    Returns:
        (Hierarchical dict): The dict keyed by institutions types and valued \
        by dicts keyed by the statistical keys (str) given by the 'STAT_FILE_DICT' \
        global and valued by the built data (dataframe) of the statistical results.
    """
    # Setting useful columns list
    lists_tup = _build_useful_cols_lists(inst_stat_cols_dic)
    (base_cols_list, inst_type_inst_cols, inst_type_pub_id_cols, inst_type_country_cols) = lists_tup

    stat_keys = list(bm_pg.STAT_FILE_DICT.keys())
    inst_type_data_dict = {}
    for inst_type in bm_pg.STAT_INST_TYPES_LIST:
        inst_type_data_dict[inst_type] = {}

        # Building data for inst_type stat computing
        final_pub_id_inst_type_df = _build_pub_id_inst_type_df(institute, distrib_institutions_df,
                                                               pub_ids_lists[0], base_cols_list + [inst_type])
        inst_type_inst_df = _build_inst_type_inst_df(final_pub_id_inst_type_df, pub_ids_lists[1:],
                                                     inst_type_inst_cols + [inst_type])
        pub_country_inst_df = _build_inst_type_pub_id_df(final_pub_id_inst_type_df,
                                                         inst_type_pub_id_cols + [inst_type])
        country_inst_pub_df = _build_inst_type_country_df(pub_country_inst_df, pub_ids_lists[1:],
                                                          inst_type_country_cols)

        # Setting 'inst_type_dict' at 'inst_type' key
        inst_type_data_dict[inst_type][stat_keys[0]] = inst_type_inst_df
        inst_type_data_dict[inst_type][stat_keys[1]] = pub_country_inst_df
        inst_type_data_dict[inst_type][stat_keys[2]] = country_inst_pub_df
    return inst_type_data_dict


def _save_inst_stat_data(inst_type_data_dict, inst_stat_path):
    """Saves the data of the institutions statistics into multisheet 
    openpyxl workbooks with a sheet per institution type.

    This done by cycling on institution type with the following steps:

    1. A dataframe is selected in the institutions statistics dict.
    2. A sheet is added to the openpyxl workbook containing the data 
    of the dataframe through the `format_wb_sheet` function 
    imported from the `bmfuncts.format_files` module.

    Args:
        inst_type_data_dict (hierarchical dict): The institutions statistics \
        dict keyed by institutions type (str) and valued by dicts keyed by \
        statistical keys (str) and valued by data (dataframe) of statistical results.
        inst_stat_path (path): The full path to the folder where the statistical \
        results are saved.
    """
    inst_types_list = inst_type_data_dict.keys()
    for stat_key, value_tup in bm_pg.STAT_FILE_DICT.items():
        stat_file, df_title_idx = value_tup
        # Initialize parameters for saving results as multisheet workbook
        first = True
        wb = openpyxl_Workbook()

        inst_stat_xlsx_path = inst_stat_path / Path(stat_file + ".xlsx")
        for inst_type in inst_types_list:
            inst_type_stat_df = inst_type_data_dict[inst_type][stat_key]

            inst_sheet_name = inst_type
            inst_stat_title = bm_pg.DF_TITLES_LIST[df_title_idx]
            wb = format_wb_sheet(inst_sheet_name, inst_type_stat_df,
                                 inst_stat_title, wb, first)
            first = False
        # Saving workbook
        wb.save(inst_stat_xlsx_path)


def build_and_save_institutions_stat(institute, norm_institutions_df,
                                     inst_types_file_path,
                                     inst_analysis_folder_path, year,
                                     pub_ids_lists,
                                     progress_param=None):
    """Builds and saves the institutions statistics from the publications data 
    with normalized institutions.

    This is done through the following steps:

    1. Builds a dataframe from the publications data with normalized institutions \
    by distributing the institutions list of each address by institution type \
    through the `_build_distributed_inst_df` internal function.  
    2. Saves the built dataframe through `save_formatted_df_to_xlsx` function \
    imported from the `bmfuncts.format_files` module.
    3. Builds and saves the institutions statistics through the \
    `_build_and_save_inst_stat_data` internal function.

    Args:
        institute (str): Institute name.
        norm_institutions_df (dataframe): Data of the normalized institutions \
        per publication.
        inst_types_file_path (path): The full path to the institutions-types file.
        inst_analysis_folder_path (path); The full path to the folder \
        where the results of the institutions analysis are saved.
        year (str): 4 digits-year of the analyzed corpus.
        pub_ids_lists (tuple): (list of all publication IDs (str) of the institute, \
        list of the IDs (str) of publications in journals, \
        list of the IDs (str) of publications in conference proceedings, \
        list of the IDs (str) of publications in books).
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    """
    print("    Computing institutions statistics")

    inst_stat_cols_dic = _set_inst_stat_cols()
    institutions_col = inst_stat_cols_dic['inst_col']

    # Setting local parameters
    xlsx_extent = ".xlsx"

    # Setting optional values
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_inter = init_progress + (final_progress - init_progress) * 0.85
        progress_callback(init_progress)

    # Setting useful column names aliases
    inst_type_abbr_col = bp.INST_TYPES_USECOLS[1]
    institutions_col = bm_pg.COL_NAMES_BONUS['institution']

    # Setting folder and file names aliases
    distrib_inst_filename_alias = bm_pg.ARCHI_YEAR["institutions distribution file name"] + xlsx_extent

    # Getting institutions types data
    inst_types_df = pd.read_excel(inst_types_file_path, usecols = bp.INST_TYPES_USECOLS)
    inst_types_list = inst_types_df[inst_type_abbr_col].to_list()

    # Building distributed info of normalized institutions per type and per address
    inter_progress_param = None
    if progress_param:
        inter_progress_param = (progress_callback, init_progress, progress_inter)
    distrib_institutions_df = _build_distributed_inst_df(norm_institutions_df, institutions_col, inst_types_list,
                                                         progress_param=inter_progress_param)

    # Saving formatted df of distributed institutions
    distrib_inst_df_title = bm_pg.DF_TITLES_LIST[11]
    sheet_name = 'Distributed Inst ' + year
    save_formatted_df_to_xlsx(inst_analysis_folder_path, distrib_inst_filename_alias,
                              distrib_institutions_df, distrib_inst_df_title,
                              sheet_name)

    # Building and saving as multisheet openpyxl files the data of institutions statistics
    inst_type_data_dict = _build_inst_stat_data(institute, distrib_institutions_df,
                                                pub_ids_lists, inst_stat_cols_dic)
    _save_inst_stat_data(inst_type_data_dict, inst_analysis_folder_path)
    if progress_param:
        progress_callback(final_progress)
