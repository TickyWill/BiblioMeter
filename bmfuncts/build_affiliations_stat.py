"""Module of functions for statistical analysis of Institute collaborations
through publications.
"""

__all__ = ['build_and_save_affiliations_stat']

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


def _set_affils_stat_cols():
    """Builds a dict setting selected columns names for the process 
    of building statistics of affiliations.

    Returns:
        (dict): The built dict.
    """
    affils_stat_cols_dic = {'pub_id_col'        : bp.COL_NAMES['pub_id'],
                            'country_col'       : bp.COL_NAMES['country'][2],
                            'final_country_col' : bm_pg.COL_NAMES_BONUS['country'],
                            'affils_col'        : bm_pg.COL_NAMES_BONUS['institution'],
                            'pub_nb_col'        : bm_pg.COL_NAMES_BONUS["pub number"],
                            'pub_ids_col'       : bm_pg.COL_NAMES_BONUS["pub_ids list"],
                            'affils_nb_col'     : bm_pg.COL_NAMES_BONUS["inst number"],
                            'affils_list_col'   : bm_pg.COL_NAMES_BONUS["inst list"],
                            'co_auth_affils_col': bm_pg.COL_NAMES_BONUS['co-auth inst'],
                            'journal_nb_col'    : bm_pg.COL_NAMES_BONUS['journal_pub_nb'],
                            'proc_nb_col'       : bm_pg.COL_NAMES_BONUS['proceedings_pub_nb'],
                            'book_nb_col'       : bm_pg.COL_NAMES_BONUS['book_pub_nb'],
                           }

    return affils_stat_cols_dic


def _build_distrib_affils_data(norm_affiliations_df, affiliations_col, affil_types_file_path,
                               progress_param=None):
    """Distributes the column that contains the list of the normalized affiliations 
    of a publication and an author address into a column for each affiliation type.

    ex: affiliationq col value = UGA Univ; USMB Univ; CNRS Nro; G-INP Sch; IMEP-LaHC Lab
        => "Univ" col value = "['UGA Univ', 'USMB Univ']"
        => "Nro" col value = "['CNRS Nro']"
        => "Sch" col value = "['G-INP Sch']"
        => "Lab" col value = "['IMEP-LaHC Lab']"
        => Other type col value = "[]"

    Args:
        norm_affiliations_df (dataframe): Data of the normalized affiliations per publication.
        affiliations_col (str): Column name of the normalized affiliations list in \
        the 'norm_affiliations_df' dataframe.
        affil_types_file_path (path): The full path to the data giving affiliation types \
        that are used as column names in the built data.
        progress_param (tup): (Function for updating ProgressBar tkinter widget status, \
        The initial progress status (int), The final progress status (int)) \
        (optional, default = None)
    Returns:
        (dataframe): The built data with distributed normalized affiliations per affiliation \
        type and per publication.
    """
    # Getting affiliations types data
    affil_types_df = pd.read_excel(affil_types_file_path, usecols=bp.AFFIL_TYPES_USECOLS)
    full_affil_types_list = affil_types_df[bp.AFFIL_TYPES_USECOLS[1]].to_list()

    progress_status, progress_step, progress_callback = [None] * 3
    if progress_param:
        step_nb = len(norm_affiliations_df) * len(full_affil_types_list)
        progress_callback, progress_init, progress_final = progress_param
        progress_step = (progress_final - progress_init) / step_nb
        progress_status = progress_init
        progress_callback(progress_status)

    norm_affils_nb, norm_affil_num = len(norm_affiliations_df), 0
    set_words_template = Template(r'[\s]$word$$')
    distrib_affiliations_df = pd.DataFrame()
    norm_affil_num = 0
    for _, row in norm_affiliations_df.iterrows():
        norm_affil_num += 1
        txt = f"              Number of distributed affiliations:   {norm_affil_num} / {norm_affils_nb}"
        print(txt, end="\r")
        affil_list = row[affiliations_col].split("; ")
        for affil_type in full_affil_types_list:
            re_search_words = re.compile(set_words_template.substitute({"word":affil_type}))
            row[affil_type] = [affil for affil in affil_list if re.search(re_search_words, affil)]
            if progress_param:
                progress_status += progress_step
                progress_callback(progress_status)
        row_df = row.to_frame().T.astype(str)
        distrib_affiliations_df = concat_dfs([distrib_affiliations_df, row_df])
    distrib_affiliations_df = distrib_affiliations_df.astype(str)
    print(" " * len(txt), end="\r")
    return distrib_affiliations_df


def _save_distrib_affils_data(distrib_affiliations_df, corpus_year, distrib_affils_file_path):
    # Saving formatted data of distributed affiliations
    distrib_affils_df_title = bm_pg.DF_TITLES_LIST[11]
    sheet_name = 'Distributed Affils ' + corpus_year
    wb, ws = format_page(distrib_affiliations_df, distrib_affils_df_title)
    ws.title = sheet_name
    wb.save(distrib_affils_file_path)


def _set_affil_names_list(affil_names):
    """Converts the string containing a list of affiliations into a list.

    ex: "['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']"
        => ['Sorbonne Univ', 'Paris-Sud Univ', 'UPMC Univ']

    Args:
        affil_names (str): Contains the list of affiliations.
    Returns:
        (list): The list of affiliations names (str).
    """
    affil_names = affil_names[1:len(affil_names)-1]
    affil_names_list = affil_names.split(", ")
    final_affil_names_list = [x[1:len(x)-1] for x in affil_names_list]
    return final_affil_names_list


def _build_pub_id_affil_types_data(institute, distrib_affiliations_df,
                                   institute_pub_ids_list, cols_list):
    """Builds the data with one row per affiliation name and its country 
    for each publication for a given type of affiliations.

    Args:
        institute (str): Institute's name.
        distrib_affiliations_df (dataframe): data with distributed normalized \
        affiliations per affiliation type and per publication.
        institute_pub_ids_list (list): All publication IDs (str) of the Institute.
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting useful column names
    pub_id_col, country_col, affil_type_col = cols_list

    # Setting out-of-stat affiliations
    out_affils = bm_ig.INSTITUTES_NORM_NAME_DICT[institute]

    # Building the data with one row per list of affiliations of type
    # 'affil_type' set through 'affil_type_col' per country for each publication
    full_affils_list = []
    data_cols = cols_list
    full_data = []
    for pub_id, pub_id_df in distrib_affiliations_df.groupby(pub_id_col):
        pub_id_data = []
        if pub_id in institute_pub_ids_list:
            for country, country_df in pub_id_df.groupby(country_col):
                pub_id_affils_list = []
                for _, row in country_df.iterrows():
                    affil_names = str(row[affil_type_col])
                    if affil_names!="[]":
                        affil_names_list = _set_affil_names_list(affil_names)
                        pub_id_affils_list += affil_names_list
                pub_id_affils_list = list(set(pub_id_affils_list))
                full_affils_list += pub_id_affils_list
                pub_id_data.append([pub_id, country, str(pub_id_affils_list)])
        full_data = full_data + pub_id_data
    pub_id_affil_types_df = pd.DataFrame(full_data, columns=data_cols)
    full_affils_list = list(set(full_affils_list))
    corrected_affils_list = [x for x in full_affils_list if x!=out_affils]

    # Building the data with one row per affiliation name and country
    # for each publication
    final_data = []
    for affil_name in corrected_affils_list:
        for _, row in pub_id_affil_types_df.iterrows():
            affil_names = str(row[affil_type_col])
            affil_name_data = []
            if affil_names!="[]":
                affil_names_list = _set_affil_names_list(affil_names)
                if affil_name in affil_names_list:
                    pub_id, country = str(row[pub_id_col]), str(row[country_col])
                    affil_name_data.append([pub_id, country, affil_name])
            final_data = final_data + affil_name_data
    final_pub_id_affil_types_df = pd.DataFrame(final_data, columns=data_cols)
    return final_pub_id_affil_types_df


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


def _build_affil_type_affils_data(final_pub_id_affil_types_df, pub_ids_dict, cols_list):
    """Builds data with one row per affiliation and attached country, 
    number of publications and list of publications IDs for a given type 
    of affiliations.

    Args:
        final_pub_id_affil_types_df (dataframe): The data with one row \
        per affiliation name and its country for each publication \
        for a given type of affiliations.
        pub_ids_dict (dict): The dict as built through the `build_pub_ids_dict` \
        function imported from the `bmfuncts.read_final_results` module.
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting col names from 'cols_list'
    (pub_id_col, country_col, final_country_col, affils_col, journal_nb_col, proc_nb_col,
     book_nb_col, pub_nb_col, pub_ids_col, affil_type_col) = cols_list

    # Building the dataframe with the statistics data per affiliation
    # for a given type of affiliations
    data_cols = [affils_col, final_country_col, journal_nb_col,
                 proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    full_data = []
    for affil_name, init_affil_name_df in final_pub_id_affil_types_df.groupby(affil_type_col):
        affil_name_df = _set_clean_country_col_values(init_affil_name_df, country_col)
        affil_name_data = []
        for country, country_df in affil_name_df.groupby(country_col):
            country_pub_ids_list = country_df[pub_id_col].to_list()
            stat_data = _build_pub_stat_values(country_pub_ids_list, pub_ids_dict)
            affil_name_data.append([affil_name, country] + stat_data)
        full_data = full_data + affil_name_data
    affil_types_affils_df = pd.DataFrame(full_data, columns=data_cols)
    affil_types_affils_df = affil_types_affils_df.drop_duplicates()

    # Sorting the built dataframe by publications number for each country
    sorted_affil_types_affils_df = pd.DataFrame(columns=data_cols)
    for country, country_df in affil_types_affils_df.groupby(final_country_col):
        country_df = country_df.sort_values(by=[pub_nb_col], ascending=False)
        sorted_affil_types_affils_df = concat_dfs([sorted_affil_types_affils_df, country_df])
    return affil_types_affils_df


def _build_affiliations_stat_values(full_affils_list):
    """Builds the statistics data in terms of affiliations numbers and affiliations list.

    Args:
        full_affils_list (list): Full list of affiliations (str).
    Returns:
        (list): The built statistics data.
    """
    affiliations_list = list(set(full_affils_list))
    affiliations_nb = len(affiliations_list)
    affiliations_list_str = "; ".join(affiliations_list)
    affils_stat_data = [affiliations_nb, affiliations_list_str]
    return affils_stat_data


def _build_affil_type_pub_id_data(final_pub_id_affil_types_df, cols_list):
    """Builds data with one row per publication and country with attached 
    number of affiliations and list of affiliations for a given type of 
    affiliations.

    Args:
        final_pub_id_affil_types_df (dataframe): The data with one row \
        per affiliation name and its country for each publication \
        for a given type of affiliations.
        cols_list (list): The columns names (str) list used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting col names from 'cols_list'
    (pub_id_col, country_col, final_country_col,
     affils_nb_col, affils_list_col, affil_type_col) = cols_list

    # Building stat per country for given affil_type
    data_cols = [pub_id_col, final_country_col,
                 affils_nb_col, affils_list_col]
    data = []
    for pub_id, pub_id_df in final_pub_id_affil_types_df.groupby(pub_id_col):
        for country, country_df in pub_id_df.groupby(country_col):
            full_affils_list = country_df[affil_type_col].to_list()
            affils_stat_data = _build_affiliations_stat_values(full_affils_list)
            data.append([pub_id, country] + affils_stat_data)
    pub_country_affil_df = pd.DataFrame(data, columns=data_cols)

    # Sorting the built dataframe by pub_id_col and by country
    pub_country_affil_df = pub_country_affil_df.sort_values(by=[pub_id_col,
                                                              final_country_col])
    return pub_country_affil_df


def _build_affil_type_country_data(pub_country_affil_df, pub_ids_dict, cols_list):
    """Builds data with one row per country with attached number of 
    publications and list of publications IDs for a given type of affiliations.

    Args:
        pub_country_affil_df (dataframe): The data with one row per publication \
        and country with attached number of affiliations and list of affiliations \
        as built through the `_build_affil_type_pub_id_data` internal function \
        for the given type of affiliations.
        pub_ids_dict (dict): The dict as built through the `build_pub_ids_dict` \
        function imported from the `bmfuncts.read_final_results` module.
        cols_list (list): The columns names (str) used to build the data.
    Returns:
        (dataframe): The built data.
    """
    # Setting col names from 'cols_list'
    (pub_id_col, country_col, affils_nb_col, affils_list_col, journal_nb_col, proc_nb_col,
     book_nb_col, pub_nb_col, pub_ids_col) = cols_list

    # Building stat per country for given affil_type
    data_cols = [country_col, affils_nb_col, affils_list_col, journal_nb_col,
                 proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    data = []
    for country, country_df in pub_country_affil_df.groupby(country_col):
        country_pub_ids_list = list(set(country_df[pub_id_col].to_list()))
        doctype_stat_data = _build_pub_stat_values(country_pub_ids_list, pub_ids_dict)

        init_affils_list = country_df[affils_list_col].to_list()
        full_affils_list = sum([x.split("; ") for x in init_affils_list], [])
        affils_stat_data = _build_affiliations_stat_values(full_affils_list)

        data.append([country] + affils_stat_data + doctype_stat_data)
    country_affil_pub_df = pd.DataFrame(data, columns=data_cols)
    return country_affil_pub_df


def _build_useful_cols_lists(affils_stat_cols_dic):
    """Builds useful lists of columns used in several functions of the module.

    Args:
        affils_stat_cols_dic (dict): The selected columns names for the process \
        of building statistics of affiliations.
    Returns:
        (tup): Tuple of 4 lists of columns names.
    """
    # Setting col names from 'affils_stat_cols_dic'
    col_keys = ['pub_id_col', 'country_col', 'final_country_col',
                'affils_col', 'affils_nb_col', 'affils_list_col',
                'journal_nb_col', 'proc_nb_col', 'book_nb_col',
                'pub_nb_col', 'pub_ids_col']
    (pub_id_col, country_col, final_country_col,
     affils_col, affils_nb_col, affils_list_col,
     journal_nb_col, proc_nb_col, book_nb_col,
     pub_nb_col, pub_ids_col) = [affils_stat_cols_dic[key] for key in col_keys]

    # Setting col lists
    cols_list_1 = [pub_id_col, country_col]
    cols_list_2 = [pub_id_col, country_col, final_country_col, affils_col,
                   journal_nb_col, proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]
    cols_list_3 = [pub_id_col, country_col, final_country_col, affils_nb_col, affils_list_col]
    cols_list_4 = [pub_id_col, final_country_col, affils_nb_col, affils_list_col,
                   journal_nb_col, proc_nb_col, book_nb_col, pub_nb_col, pub_ids_col]

    return cols_list_1, cols_list_2, cols_list_3, cols_list_4


def _build_affils_stat_data(institute, distrib_affiliations_df, pub_ids_dict, affils_stat_cols_dic):
    """Builds 3 dataframes of affiliations statistics for each affiliation type.

    This done through the cycling on the list of the affiliations type 
    defined by the 'STAT_FILE_DICT' global. The cycled steps are as follows:

    1. Building the data with one row per affiliation name and its \
    country for each publication for the type of affiliations through \
    the `_build_pub_id_affil_types_data` internal function.
    2. Building the 3 sets of statistical data for the type of affiliations \
    through the `_build_affil_type_affils_data`, `_build_affil_type_pub_id_data` \
    and `_build_affil_type_country_data` internal functions.

    Args:
        institute (str): Institute name.
        distrib_affiliations_df (dataframe): data with distributed normalized \
        affiliations per affiliation type and per publication.
        pub_ids_dict (dict): (list of all publication IDs (str) of the institute, \
        list of the IDs (str) of publications in journals, \
        list of the IDs (str) of publications in conference proceedings, \
        list of the IDs (str) of publications in books).
        affils_stat_cols_dic (dict): The selected columns names for the process \
        of building statistics of affiliations.
    Returns:
        (Hierarchical dict): The dict keyed by affiliations types and valued \
        by dicts keyed by the statistical keys (str) given by the 'STAT_FILE_DICT' \
        global and valued by the built data (dataframe) of the statistical results.
    """
    # Setting pub_ids lists
    all_pub_ids_list = pub_ids_dict['all']

    # Setting useful columns list
    lists_tup = _build_useful_cols_lists(affils_stat_cols_dic)
    (base_cols_list, affil_type_affils_cols, affil_type_pub_ids_cols,
     affil_type_countries_cols) = lists_tup

    affil_types_nb, affil_type_num = len(bm_pg.STAT_INST_TYPES_LIST), 0
    stat_keys = list(bm_pg.STAT_FILE_DICT.keys())
    affil_type_data_dict = {}
    for affil_type in bm_pg.STAT_INST_TYPES_LIST:
        affil_type_num += 1
        txt = f"              Number of analyzed affiliations type:   {affil_type_num} / {affil_types_nb}"
        print(txt, end="\r")
        affil_type_data_dict[affil_type] = {}

        # Building the data with one row per affiliation name and its country
        # for each publication for a given type of affiliations
        cols_list = base_cols_list + [affil_type]
        final_pub_id_affil_types_df = _build_pub_id_affil_types_data(institute, distrib_affiliations_df,
                                                                     all_pub_ids_list, cols_list)

        # Building data with one row per affiliation and attached country, number of publications
        # and list of publications IDs for a given type of affiliations
        cols_list = affil_type_affils_cols + [affil_type]
        affil_type_affils_df = _build_affil_type_affils_data(final_pub_id_affil_types_df, pub_ids_dict,
                                                             cols_list)

        # Building data with one row per publication and country with attached number of affiliations
        # and list of affiliations for a given type of affiliations
        cols_list = affil_type_pub_ids_cols + [affil_type]
        pub_country_affil_df = _build_affil_type_pub_id_data(final_pub_id_affil_types_df, cols_list)

        # Building data with one row per country with attached number of publications
        # and list of publications IDs for a given type of affiliations.
        country_affil_pub_df = _build_affil_type_country_data(pub_country_affil_df, pub_ids_dict,
                                                              affil_type_countries_cols)

        # Setting 'affil_type_data_dict' values at 'affil_type' key
        affil_type_data_dict[affil_type][stat_keys[0]] = affil_type_affils_df
        affil_type_data_dict[affil_type][stat_keys[1]] = pub_country_affil_df
        affil_type_data_dict[affil_type][stat_keys[2]] = country_affil_pub_df
    print(" " * len(txt), end="\r")
    return affil_type_data_dict


def _save_affils_stat_data(affil_type_data_dict, affils_stat_path):
    """Saves the data of the affiliations statistics into multisheet 
    openpyxl workbooks with a sheet per affiliation type.

    This done by cycling on affiliation type with the following steps:

    1. A dataframe is selected in the affiliations statistics dict.
    2. A sheet is added to the openpyxl workbook containing the data 
    of the dataframe through the `format_wb_sheet` function 
    imported from the `bmfuncts.format_files` module.

    Args:
        affil_type_data_dict (hierarchical dict): The affiliations statistics \
        dict keyed by affiliations type (str) and valued by dicts keyed by \
        statistical keys (str) and valued by data (dataframe) of statistical results.
        affils_stat_path (path): The full path to the folder where the statistical \
        results are saved.
    """
    stat_affil_types_list = affil_type_data_dict.keys()
    for stat_key, value_tup in bm_pg.STAT_FILE_DICT.items():
        stat_file, df_title_idx = value_tup
        # Initialize parameters for saving results as multisheet workbook
        first = True
        wb = openpyxl_Workbook()

        affils_stat_xlsx_path = affils_stat_path / Path(stat_file + ".xlsx")
        for affil_type in stat_affil_types_list:
            affil_type_stat_df = affil_type_data_dict[affil_type][stat_key]

            affils_sheet_name = affil_type
            affils_stat_title = bm_pg.DF_TITLES_LIST[df_title_idx]
            wb = format_wb_sheet(affils_sheet_name, affil_type_stat_df,
                                 affils_stat_title, wb, first)
            first = False
        # Saving workbook
        wb.save(affils_stat_xlsx_path)


def _build_stat_files_paths(corpus_year, final_results_path, affils_analysis_folder_path):
    # Setting aliases to folder and file names
    pub_lists_folder_alias = bm_pg.ARCHI_RESULTS["pub-lists"]
    full_pub_list_file_base_alias = bm_pg.ARCHI_YEAR["pub list file name base"]
    distrib_affils_file_alias = bm_pg.ARCHI_YEAR["institutions distribution file name"]

    # Setting file names
    full_pub_list_file = f"{full_pub_list_file_base_alias} {corpus_year}.xlsx"
    collab_pub_list_file = f"{full_pub_list_file_base_alias} {corpus_year}_Collaborations.xlsx"
    distrib_affils_file = f"{distrib_affils_file_alias}.xlsx"

    # Setting paths
    year_final_results_path = final_results_path / Path(corpus_year)
    pub_lists_folder_path = year_final_results_path / Path(pub_lists_folder_alias)
    full_pub_list_file_path = pub_lists_folder_path / Path(full_pub_list_file)
    collab_pub_list_path = pub_lists_folder_path / Path(collab_pub_list_file)
    distrib_affils_file_path = affils_analysis_folder_path / Path(distrib_affils_file)

    return full_pub_list_file_path, collab_pub_list_path, distrib_affils_file_path


def _build_collab_pub_list_data(full_pub_list_file_path, affil_type_data_dict, affils_stat_cols_dic):
    # Setting useful column names
    col_keys = ['pub_id_col', 'final_country_col', 'affils_list_col']
    pub_id_col, country_col, affils_list_col = [affils_stat_cols_dic[key] for key in col_keys]

    # Getting the full publications list
    full_pub_list_df = pd.read_excel(full_pub_list_file_path)

    # Selecting the statistics results to use
    stat_type = list(bm_pg.STAT_FILE_DICT.keys())[1]

    sep_str = "; "
    affil_types_list = list(affil_type_data_dict.keys())
    affil_types_nb = len(affil_types_list)
    pub_nb, pub_num = len(full_pub_list_df), 0
    data = []
    for _, full_pub_list_row in full_pub_list_df.iterrows():
        pub_num += 1
        print(f"              Number of analyzed publications:   {pub_num} / {pub_nb}", end="\r")
        full_pub_list_pub_id = full_pub_list_row[pub_id_col]
        full_pub_list_row_list = full_pub_list_row.to_frame().T.values.tolist()[0]
        collab_list = []
        for affil_type in affil_types_list:
            stat_pub_affil_df = affil_type_data_dict[affil_type][stat_type]
            pub_id_affil_country_list = []
            for _, stat_row in stat_pub_affil_df.iterrows():
                stat_pub_id = stat_row[pub_id_col]
                if stat_pub_id==full_pub_list_pub_id:
                    country = stat_row[country_col]
                    country_pub_id_affils_list = build_list_from_str(str(stat_row[affils_list_col]), sep_str)
                    pub_id_affil_country_list += [f"{x}_{country}" for x in country_pub_id_affils_list]
            pub_id_affil_country_str = ""
            if pub_id_affil_country_list:
                pub_id_affil_country_str = build_string_from_list(pub_id_affil_country_list, sep_str)
            collab_list.append(pub_id_affil_country_str)
        data.append(full_pub_list_row_list + collab_list)
    pub_lists_cols = full_pub_list_df.columns.to_list() + affil_types_list
    collab_pub_list_df = pd.DataFrame(data, columns=pub_lists_cols)
    return collab_pub_list_df, affil_types_nb


def _save_collab_pub_list_data(collab_pub_list_df, collab_pub_list_path, affil_types_nb, corpus_year):
    df_title = bm_pg.DF_TITLES_LIST[20]
    wb, ws = format_page(collab_pub_list_df, df_title, add_cols_nb=affil_types_nb)
    ws.title = f"Collaborations {corpus_year}"
    # Saving workbook
    wb.save(collab_pub_list_path)


def build_and_save_affiliations_stat(norm_affiliations_df, sub_paths_list, pub_ids_dict,
                                     affils_stat_params, progress_param=None):
    """Builds and saves the affiliations statistics from the publications data 
    with normalized affiliations.

    This is done through the following steps:

    1. Builds data from the publications data with normalized affiliations \
    by distributing the affiliations list of each address by affiliation type \
    through the `_build_distrib_affils_data` internal function.
    2. Saves the built data through `_save_distrib_affils_data` internal function.
    3. Computes the affiliations statistics through the `_build_affils_stat_data` \
    internal function.
    4. Saves the built data through `_save_affils_stat_data` internal function.
    5. Builds lists of publications per affiliation type through the \
    `_build_collab_pub_list_data` internal function.
    6. Saves the built data through `_save_collab_pub_list_data` internal function.

    Args:
        norm_affiliations_df (dataframe): Data of the normalized affiliations \
        per publication.
        sub_paths_list (list): Composed of the full path (path) to folder where final \
        results are saved, of the full path (path) to the folder where the results of \
        the affiliations analysis are saved and of the full path (path) to the \
        affiliations-types file.
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
    # setting parameters value from 'affils_stat_params'
    institute, corpus_year, print_params = affils_stat_params

    # Setting useful col names
    affils_stat_cols_dic = _set_affils_stat_cols()
    affiliations_col = affils_stat_cols_dic['affils_col']

    # Setting files paths
    final_results_path, affils_analysis_folder_path, affil_types_file_path = sub_paths_list
    paths_tup = _build_stat_files_paths(corpus_year, final_results_path, affils_analysis_folder_path)
    full_pub_list_file_path, collab_pub_list_path, distrib_affils_file_path = paths_tup

    # Setting optional values
    progress_callback, init_progress, final_progress, progress_inter = [None] * 4
    if progress_param:
        progress_callback, init_progress, final_progress = progress_param
        progress_inter = init_progress + (final_progress - init_progress) * 0.50
        progress_callback(init_progress)

    # Building distributed info of normalized affiliations per type and per address
    inter_progress_param = None
    if progress_param:
        inter_progress_param = (progress_callback, init_progress, progress_inter)
    print_step_text("  - Distributing normalized affiliations per address and publications...",
                    print_params)
    distrib_affiliations_df = _build_distrib_affils_data(norm_affiliations_df, affiliations_col,
                                                         affil_types_file_path,
                                                         progress_param=inter_progress_param)
    print_step_text("      - Distributed normalized affiliations built", print_params)
    print("      - Saving the built distribution...", end="\r")
    _save_distrib_affils_data(distrib_affiliations_df, corpus_year,distrib_affils_file_path)
    print_step_text("      - Distributed normalized affiliations saved", print_params)

    # Building and saving as multisheet openpyxl files the data of affiliations statistics
    print_step_text("  - Computing affiliations statistics...", print_params)
    affil_type_data_dict = _build_affils_stat_data(institute, distrib_affiliations_df,
                                                   pub_ids_dict, affils_stat_cols_dic)
    _save_affils_stat_data(affil_type_data_dict, affils_analysis_folder_path)
    print_step_text("      - Affiliations statistics built and saved", print_params)

    # Building and saving as multisheet openpyxl files the data of affiliations publications list
    print_step_text("  - Building publications lists with co-author affiliations per organization type...",
                    print_params)
    collab_pub_list_df, affil_types_nb = _build_collab_pub_list_data(full_pub_list_file_path, affil_type_data_dict,
                                                                     affils_stat_cols_dic)
    _save_collab_pub_list_data(collab_pub_list_df, collab_pub_list_path, affil_types_nb, corpus_year)
    print_step_text("      - Publications lists with co-author affiliations per organization type built and saved",
                    print_params)
    if progress_param:
        progress_callback(final_progress)
