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
import bmfuncts.institute_globals as bm_ig
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import format_page
from bmfuncts.format_files import format_wb_sheet
from bmfuncts.useful_functs import build_list_from_str
from bmfuncts.useful_functs import build_string_from_list
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import print_step_text


def _set_inst_stat_cols():
    """Builds a dict setting selected columns names for the process 
    of building statistics of institutions.

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
                          'co_auth_inst_col' : bm_pg.COL_NAMES_BONUS['co-auth inst'],
                          'journal_nb_col'   : bm_pg.COL_NAMES_BONUS['journal_pub_nb'],
                          'proc_nb_col'      : bm_pg.COL_NAMES_BONUS['proceedings_pub_nb'],
                          'book_nb_col'      : bm_pg.COL_NAMES_BONUS['book_pub_nb'],
                        }

    return inst_stat_cols_dic


def _build_distributed_inst_data(norm_institutions_df, institutions_col, inst_types_file_path,
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
        inst_types_file_path (path): The full path to the data giving institution types \
        that are used as column names in the built data.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    Returns:
        (dataframe): The built data with distributed normalized institutions per institution \
        type and per publication.
    """
    # Getting institutions types data
    inst_types_df = pd.read_excel(inst_types_file_path, usecols=bp.INST_TYPES_USECOLS)
    full_inst_types_list = inst_types_df[bp.INST_TYPES_USECOLS[1]].to_list()

    progress_status, progress_step, progress_callback = [None] * 3
    if progress_param:
        step_nb = len(norm_institutions_df) * len(full_inst_types_list)
        progress_callback, progress_init, progress_final = progress_param
        progress_step = (progress_final - progress_init) / step_nb
        progress_status = progress_init
        progress_callback(progress_status)

    norm_inst_nb, norm_inst_num = len(norm_institutions_df), 0
    set_words_template = Template(r'[\s]$word$$')
    distrib_institutions_df = pd.DataFrame()
    norm_inst_num = 0
    for _, row in norm_institutions_df.iterrows():
        norm_inst_num += 1
        txt = f"              Number of distributed affiliations:   {norm_inst_num} / {norm_inst_nb}"
        print(txt, end="\r")
        inst_list = row[institutions_col].split("; ")
        for inst_type in full_inst_types_list:
            re_search_words = re.compile(set_words_template.substitute({"word":inst_type}))
            row[inst_type] = [inst for inst in inst_list if re.search(re_search_words, inst)]
            if progress_param:
                progress_status += progress_step
                progress_callback(progress_status)
        row_df = row.to_frame().T.astype(str)
        distrib_institutions_df = concat_dfs([distrib_institutions_df, row_df])
    distrib_institutions_df = distrib_institutions_df.astype(str)
    print(" " * len(txt), end="\r")
    return distrib_institutions_df


def _save_distrib_inst_data(distrib_institutions_df, corpus_year, distrib_inst_file_path):
    # Saving formatted data of distributed institutions
    distrib_inst_df_title = bm_pg.DF_TITLES_LIST[11]
    sheet_name = 'Distributed Inst ' + corpus_year
    wb, ws = format_page(distrib_institutions_df, distrib_inst_df_title)
    ws.title = sheet_name
    wb.save(distrib_inst_file_path)


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
    out_inst = bm_ig.INSTITUTES_NORM_NAME_DICT[institute]

    # Building the data with one row per list of institutions of type
    # 'inst_type' set through 'inst_type_col' per country for each publication
    full_inst_list = []
    data_cols = cols_list
    full_data = []
    for pub_id, pub_id_df in distrib_institutions_df.groupby(pub_id_col):
        pub_id_data = []
        if pub_id in institute_pub_ids_list:
            for country, country_df in pub_id_df.groupby(country_col):
                pub_id_inst_list = []
                for _, row in country_df.iterrows():
                    inst_names = str(row[inst_type_col])
                    if inst_names!="[]":
                        inst_names_list = _set_inst_names_list(inst_names)
                        pub_id_inst_list += inst_names_list
                pub_id_inst_list = list(set(pub_id_inst_list))
                full_inst_list += pub_id_inst_list
                pub_id_data.append([pub_id, country, str(pub_id_inst_list)])
        full_data = full_data + pub_id_data
    pub_id_inst_type_df = pd.DataFrame(full_data, columns=data_cols)
    full_inst_list = list(set(full_inst_list))
    corrected_inst_list = [x for x in full_inst_list if x!=out_inst]

    # Building the data with one row per institution name and country
    # for each publication
    final_data = []
    for inst_name in corrected_inst_list:
        for _, row in pub_id_inst_type_df.iterrows():
            inst_names = str(row[inst_type_col])
            inst_name_data = []
            if inst_names!="[]":
                inst_names_list = _set_inst_names_list(inst_names)
                if inst_name in inst_names_list:
                    pub_id, country = str(row[pub_id_col]), str(row[country_col])
                    inst_name_data.append([pub_id, country, inst_name])
            final_data = final_data + inst_name_data
    final_pub_id_inst_type_df = pd.DataFrame(final_data, columns=data_cols)
    return final_pub_id_inst_type_df


def _set_clean_country_col_values(init_df, country_col):
    """Sets the same country as the first item of the sorted countries list 
    when the country value is unknown.

    Args:
        init_df (dataframe): The data to clean.
        country_col (str): The column to clean in the data.
    Returns:
        (dataframe): The cleaned data.
    """
    countries_list = sorted([str(x) for x in init_df[country_col].to_list()])
    country_to_set = countries_list[0]
    clean_df = init_df.copy()
    clean_df[country_col] = init_df[country_col].apply(lambda x: country_to_set
                                                       if x==bp.UNKNOWN_COUNTRY else x)
    return clean_df


def _set_item_pub_nb(full_pub_ids_list, item_pub_ids_list):
    """Sets the number of publications which IDs are in a select list of IDs for an item.

    Args:
        full_pub_ids_list (list): Full list of publications IDs (str).
        item_pub_ids_list (list): Selected list of publications IDs (str) for an item.
    Returns:
        (int): The computed number of publications.
    """
    item_pub_nb = len([x for x in full_pub_ids_list if x in item_pub_ids_list])
    return item_pub_nb


def _build_pub_stat_values(full_pub_ids_list, pub_ids_dict):
    """Builds the statistics data in terms of publications numbers and publications-IDs list.

    The publications numbers are computed through the `_set_item_pub_nb` internal function 
    for the following items: journals, proceedings and books.

    Args:
        full_pub_ids_list (list): Full list of publications IDs (str).
        pub_ids_dict (dict): The dict as built through the `build_pub_ids_dict` function \
        imported from the `bmfuncts.read_final_results` module.
    Returns:
        (list): The built statistics data.
    """
    journal_pub_nb = _set_item_pub_nb(full_pub_ids_list, pub_ids_dict['journals'])
    proceedings_pub_nb = _set_item_pub_nb(full_pub_ids_list, pub_ids_dict['proceedings'])
    book_pub_nb = _set_item_pub_nb(full_pub_ids_list, pub_ids_dict['books'])
    full_pub_nb = len(full_pub_ids_list)
    pub_ids_str = "; ".join(full_pub_ids_list)

    stat_data = [journal_pub_nb, proceedings_pub_nb, book_pub_nb, full_pub_nb, pub_ids_str]
    return stat_data


def _build_inst_type_inst_df(final_pub_id_inst_type_df, pub_ids_dict, cols_list):
    """Builds data with one row per institution and attached country, 
    number of publications and list of publications IDs for a given type 
    of institutions.

    Args:
        final_pub_id_inst_type_df (dataframe): The data with one row \
        per institution name and its country for each publication \
        for a given type of institutions.
        pub_ids_dict (dict): The dict as built through the `build_pub_ids_dict` \
        function imported from the `bmfuncts.read_final_results` module.
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting col names from 'inst_type_inst_cols'
    (pub_id_col, country_col, final_country_col, inst_col, journal_nb_col, proc_nb_col,
     book_nb_col, pub_nb_col, pub_ids_col, inst_type_col) = cols_list

    # Building the dataframe with the statistics data per institution
    # for a given type of institutions
    data_cols = [inst_col, final_country_col, journal_nb_col,
                 proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    full_data = []
    for inst_name, init_inst_name_df in final_pub_id_inst_type_df.groupby(inst_type_col):
        inst_name_df = _set_clean_country_col_values(init_inst_name_df, country_col)
        inst_name_data = []
        for country, country_df in inst_name_df.groupby(country_col):
            country_pub_ids_list = country_df[pub_id_col].to_list()
            stat_data = _build_pub_stat_values(country_pub_ids_list, pub_ids_dict)
            inst_name_data.append([inst_name, country] + stat_data)
        full_data = full_data + inst_name_data
    inst_type_inst_df = pd.DataFrame(full_data, columns=data_cols)
    inst_type_inst_df = inst_type_inst_df.drop_duplicates()

    # Sorting the built dataframe by publications number for each country
    sorted_inst_type_inst_df = pd.DataFrame(columns=data_cols)
    for country, country_df in inst_type_inst_df.groupby(final_country_col):
        country_df = country_df.sort_values(by=[pub_nb_col], ascending=False)
        sorted_inst_type_inst_df = concat_dfs([sorted_inst_type_inst_df, country_df])
    return sorted_inst_type_inst_df


def _build_institutions_stat_values(full_inst_list):
    """Builds the statistics data in terms of institutions numbers and institutions list.

    Args:
        full_inst_list (list): Full list of institutions (str).
    Returns:
        (list): The built statistics data.
    """
    institutions_list = list(set(full_inst_list))
    institutions_nb = len(institutions_list)
    institutions_list_str = "; ".join(institutions_list)
    inst_stat_data = [institutions_nb, institutions_list_str]
    return inst_stat_data


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
            full_inst_list = country_df[inst_type_col].to_list()
            inst_stat_data = _build_institutions_stat_values(full_inst_list)
            data.append([pub_id, country] + inst_stat_data)
    pub_country_inst_df = pd.DataFrame(data, columns=data_cols)

    # Sorting the built dataframe by pub_id_col and by country
    pub_country_inst_df = pub_country_inst_df.sort_values(by=[pub_id_col,
                                                              final_country_col])
    return pub_country_inst_df


def _build_inst_type_country_df(pub_country_inst_df, pub_ids_dict, cols_list):
    """Builds data with one row per country with attached number of 
    publications and list of publications IDs for a given type of institutions.

    Args:
        pub_country_inst_df (dataframe): The data with one row per publication \
        and country with attached number of institutions and list of institutions \
        as built through the `_build_inst_type_pub_id_df` internal function \
        for the given type of institutions.
        pub_ids_dict (dict): The dict as built through the `build_pub_ids_dict` \
        function imported from the `bmfuncts.read_final_results` module.
        cols_list (list): The columns names (str) used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting col names from 'cols_list'
    (pub_id_col, country_col, inst_nb_col, inst_list_col, journal_nb_col, proc_nb_col,
     book_nb_col, pub_nb_col, pub_ids_col) = cols_list

    # Building stat per country for given inst_type
    data_cols = [country_col, inst_nb_col, inst_list_col, journal_nb_col,
                 proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    data = []
    for country, country_df in pub_country_inst_df.groupby(country_col):
        country_pub_ids_list = list(set(country_df[pub_id_col].to_list()))
        doctype_stat_data = _build_pub_stat_values(country_pub_ids_list, pub_ids_dict)

        init_inst_list = country_df[inst_list_col].to_list()
        full_inst_list = sum([x.split("; ") for x in init_inst_list], [])
        inst_stat_data = _build_institutions_stat_values(full_inst_list)

        data.append([country] + inst_stat_data + doctype_stat_data)
    country_inst_pub_df = pd.DataFrame(data, columns=data_cols)
    return country_inst_pub_df


def _build_useful_cols_lists(inst_stat_cols_dic):
    """Builds useful lists of columns used in several functions of the module.

    Args:
        inst_stat_cols_dic (dict): The selected columns names for the process \
        of building statistics of institutions.
    Returns:
        (tup): Tuple of 4 lists of columns names.
    """
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


def _build_inst_stat_data(institute, distrib_institutions_df, pub_ids_dict, inst_stat_cols_dic):
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
        pub_ids_dict (dict): (list of all publication IDs (str) of the institute, \
        list of the IDs (str) of publications in journals, \
        list of the IDs (str) of publications in conference proceedings, \
        list of the IDs (str) of publications in books).
        inst_stat_cols_dic (dict): The selected columns names for the process \
        of building statistics of institutions.
    Returns:
        (Hierarchical dict): The dict keyed by institutions types and valued \
        by dicts keyed by the statistical keys (str) given by the 'STAT_FILE_DICT' \
        global and valued by the built data (dataframe) of the statistical results.
    """
    # Setting pub_ids lists
    all_pub_ids_list = pub_ids_dict['all']

    # Setting useful columns list
    lists_tup = _build_useful_cols_lists(inst_stat_cols_dic)
    (base_cols_list, inst_type_inst_cols, inst_type_pub_id_cols,
     inst_type_country_cols) = lists_tup

    inst_types_nb, inst_type_num = len(bm_pg.STAT_INST_TYPES_LIST), 0
    stat_keys = list(bm_pg.STAT_FILE_DICT.keys())
    inst_type_data_dict = {}
    for inst_type in bm_pg.STAT_INST_TYPES_LIST:
        inst_type_num += 1
        txt = f"              Number of analyzed affiliations type:   {inst_type_num} / {inst_types_nb}"
        print(txt, end="\r")
        inst_type_data_dict[inst_type] = {}

        # Building the data with one row per institution name and its country
        # for each publication for a given type of institutions
        cols_list = base_cols_list + [inst_type]
        final_pub_id_inst_type_df = _build_pub_id_inst_type_df(institute, distrib_institutions_df,
                                                               all_pub_ids_list, cols_list)

        # Building data with one row per institution and attached country, number of publications
        # and list of publications IDs for a given type of institutions
        cols_list = inst_type_inst_cols + [inst_type]
        inst_type_inst_df = _build_inst_type_inst_df(final_pub_id_inst_type_df, pub_ids_dict, cols_list)

        # Building data with one row per publication and country with attached number of institutions
        # and list of institutions for a given type of institutions
        cols_list = inst_type_pub_id_cols + [inst_type]
        pub_country_inst_df = _build_inst_type_pub_id_df(final_pub_id_inst_type_df, cols_list)

        # Building data with one row per country with attached number of publications
        # and list of publications IDs for a given type of institutions.
        country_inst_pub_df = _build_inst_type_country_df(pub_country_inst_df, pub_ids_dict,
                                                          inst_type_country_cols)

        # Setting 'inst_type_dict' values at 'inst_type' key
        inst_type_data_dict[inst_type][stat_keys[0]] = inst_type_inst_df
        inst_type_data_dict[inst_type][stat_keys[1]] = pub_country_inst_df
        inst_type_data_dict[inst_type][stat_keys[2]] = country_inst_pub_df
    print(" " * len(txt), end="\r")
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
    stat_inst_types_list = inst_type_data_dict.keys()
    for stat_key, value_tup in bm_pg.STAT_FILE_DICT.items():
        stat_file, df_title_idx = value_tup
        # Initialize parameters for saving results as multisheet workbook
        first = True
        wb = openpyxl_Workbook()

        inst_stat_xlsx_path = inst_stat_path / Path(stat_file + ".xlsx")
        for inst_type in stat_inst_types_list:
            inst_type_stat_df = inst_type_data_dict[inst_type][stat_key]

            inst_sheet_name = inst_type
            inst_stat_title = bm_pg.DF_TITLES_LIST[df_title_idx]
            wb = format_wb_sheet(inst_sheet_name, inst_type_stat_df,
                                 inst_stat_title, wb, first)
            first = False
        # Saving workbook
        wb.save(inst_stat_xlsx_path)


def _build_stat_files_paths(corpus_year, final_results_path, inst_analysis_folder_path):
    # Setting aliases to folder and file names
    pub_lists_folder_alias = bm_pg.ARCHI_RESULTS["pub-lists"]
    full_pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    distrib_inst_file_alias = bm_pg.ARCHI_YEAR["institutions distribution file name"]

    # Setting file names
    full_pub_list_file = f"{full_pub_list_file_base_alias} {corpus_year}.xlsx"
    collab_pub_list_file = f"{full_pub_list_file_base_alias} {corpus_year}_Collaborations.xlsx"
    distrib_inst_file = f"{distrib_inst_file_alias}.xlsx"

    # Setting paths
    year_final_results_path = final_results_path / Path(corpus_year)
    pub_lists_folder_path = year_final_results_path / Path(pub_lists_folder_alias)
    full_pub_list_file_path = pub_lists_folder_path / Path(full_pub_list_file)
    collab_pub_list_path = pub_lists_folder_path / Path(collab_pub_list_file)
    distrib_inst_file_path = inst_analysis_folder_path / Path(distrib_inst_file)

    return full_pub_list_file_path, collab_pub_list_path, distrib_inst_file_path


def _build_collab_pub_list_data(full_pub_list_file_path, inst_type_data_dict, inst_stat_cols_dic):
    # Setting useful column names
    col_keys = ['pub_id_col', 'final_country_col', 'inst_list_col']
    pub_id_col, country_col, inst_list_col = [inst_stat_cols_dic[key] for key in col_keys]

    # Getting the full publications list
    full_pub_list_df = pd.read_excel(full_pub_list_file_path)

    # Selecting the statistics results to use
    stat_type = list(bm_pg.STAT_FILE_DICT.keys())[1]

    sep_str = "; "
    inst_types_list = list(inst_type_data_dict.keys())
    inst_types_nb = len(inst_types_list)
    pub_nb, pub_num = len(full_pub_list_df), 0
    data = []
    for _, full_pub_list_row in full_pub_list_df.iterrows():
        pub_num += 1
        print(f"              Number of analyzed publications:   {pub_num} / {pub_nb}", end="\r")
        full_pub_list_pub_id = full_pub_list_row[pub_id_col]
        full_pub_list_row_list = full_pub_list_row.to_frame().T.values.tolist()[0]
        collab_list = []
        for inst_type in inst_types_list:
            stat_pub_inst_df = inst_type_data_dict[inst_type][stat_type]
            pub_id_inst_country_list = []
            for _, stat_row in stat_pub_inst_df.iterrows():
                stat_pub_id = stat_row[pub_id_col]
                if stat_pub_id==full_pub_list_pub_id:
                    country = stat_row[country_col]
                    country_pub_id_inst_list = build_list_from_str(str(stat_row[inst_list_col]), sep_str)
                    pub_id_inst_country_list += [f"{x}_{country}" for x in country_pub_id_inst_list]
            pub_id_inst_country_str = ""
            if pub_id_inst_country_list:
                pub_id_inst_country_str = build_string_from_list(pub_id_inst_country_list, sep_str)
            collab_list.append(pub_id_inst_country_str)
        data.append(full_pub_list_row_list + collab_list)
    pub_lists_cols = full_pub_list_df.columns.to_list() + inst_types_list
    collab_pub_list_df = pd.DataFrame(data, columns=pub_lists_cols)
    return collab_pub_list_df, inst_types_nb


def _save_collab_pub_list_data(collab_pub_list_df, collab_pub_list_path, inst_types_nb, corpus_year):

    df_title = bm_pg.DF_TITLES_LIST[20]
    wb, ws = format_page(collab_pub_list_df, df_title, add_cols_nb=inst_types_nb)
    ws.title = f"Collaborations {corpus_year}"
    # Saving workbook
    wb.save(collab_pub_list_path)


def build_and_save_institutions_stat(norm_institutions_df, sub_paths_list, pub_ids_dict,
                                     inst_stat_params, progress_param=None):
    """Builds and saves the institutions statistics from the publications data 
    with normalized institutions.

    This is done through the following steps:

    1. Builds data from the publications data with normalized institutions \
    by distributing the institutions list of each address by institution type \
    through the `_build_distributed_inst_data` internal function.
    2. Saves the built data through `_save_distrib_inst_data` internal function.
    3. Computes the institutions statistics through the `_build_inst_stat_data` \
    internal function.
    4. Saves the built data through `_save_inst_stat_data` internal function.
    5. Builds lists of publications per institution type through the \
    `_build_inst_pub_list_data` internal function.
    6. Saves the built data through `_save_pub_lists_data` internal function.

    Args:
        norm_institutions_df (dataframe): Data of the normalized institutions \
        per publication.
        sub_paths_list (list): Composed of the full path (path) to folder where final \
        results are saved, of the full path (path) to the folder where the results of \
        the institutions analysis are saved and of the full path (path) to the \
        institutions-types file.
        pub_ids_dict (tuple): (list of all publication IDs (str) of the institute, \
        list of the IDs (str) of publications in journals, \
        list of the IDs (str) of publications in conference proceedings, \
        list of the IDs (str) of publications in books).
        institute (str): Institute name.
        corpus_year (str): 4 digits-year of the analyzed corpus.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default: None)
    """
    # setting parameters value from 'inst_stat_params'
    institute, corpus_year, print_params = inst_stat_params

    # Setting useful col names
    inst_stat_cols_dic = _set_inst_stat_cols()
    institutions_col = inst_stat_cols_dic['inst_col']

    # Setting files paths
    final_results_path, inst_analysis_folder_path, inst_types_file_path = sub_paths_list
    paths_tup = _build_stat_files_paths(corpus_year, final_results_path, inst_analysis_folder_path)
    full_pub_list_file_path, collab_pub_list_path, distrib_inst_file_path = paths_tup

    # Setting optional values
    progress_callback, init_progress, final_progress, progress_inter = [None] * 4
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_inter = init_progress + (final_progress - init_progress) * 0.50
        progress_callback(init_progress)

    # Building distributed info of normalized institutions per type and per address
    inter_progress_param = None
    if progress_param:
        inter_progress_param = (progress_callback, init_progress, progress_inter)
    print_step_text("  - Distributing normalized affiliations per address and publications...",
                    print_params)
    distrib_institutions_df = _build_distributed_inst_data(norm_institutions_df, institutions_col,
                                                           inst_types_file_path, progress_param=inter_progress_param)
    print_step_text("      - Distributed normalized affiliations built", print_params)
    print("      - Saving the built distribution...", end="\r")
    _save_distrib_inst_data(distrib_institutions_df, corpus_year, distrib_inst_file_path)
    print_step_text("      - Distributed normalized affiliations saved", print_params)

    # Building and saving as multisheet openpyxl files the data of institutions statistics
    print_step_text("  - Computing affiliations statistics...", print_params)
    inst_type_data_dict = _build_inst_stat_data(institute, distrib_institutions_df,
                                                pub_ids_dict, inst_stat_cols_dic)
    _save_inst_stat_data(inst_type_data_dict, inst_analysis_folder_path)
    print_step_text("      - Affiliations statistics built and saved", print_params)

    # Building and saving as multisheet openpyxl files the data of institutions publications list
    print_step_text("  - Building publications lists with co-author affiliations per organization type...",
                    print_params)
    collab_pub_list_df, inst_types_nb = _build_collab_pub_list_data(full_pub_list_file_path, inst_type_data_dict,
                                                                    inst_stat_cols_dic)
    _save_collab_pub_list_data(collab_pub_list_df, collab_pub_list_path, inst_types_nb, corpus_year)
    print_step_text("      - Publications lists with co-author affiliations per organization type built and saved",
                    print_params)
    if progress_param:
        progress_callback(final_progress)
