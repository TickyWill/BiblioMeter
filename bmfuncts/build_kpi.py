"""Module of functions for building key performance indicators (KPIs) 
including impact-factors KPIs.
"""
__all__ = ['if_analysis']


# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import numpy as np
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.doctype_analysis import doctype_analysis
from bmfuncts.format_files import format_page
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import print_step_text


def _set_build_kpi_cols(institute, org_tup, if_analysis_col, if_analysis_year):
    """Builds a dict setting selected columns names for the process 
    of building KPIs data.

    This is done through the `set_final_col_names` function imported from the 
    `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute's name.
        org_tup (tup): Contains parameters of Institute's organization.
        if_analysis_col (str): Name of the column of IFs in the IFs analysis results.
        if_analysis_year (str): 4 digits-year of IFs analysis.
    Returns:
        (dict): The built dict.
    """
    final_cols_tup = set_final_col_names(institute, org_tup)
    final_col_dic, depts_col_list = final_cols_tup

    build_kpi_cols_dic = {'depts_col_list' : depts_col_list,
                          'journal_col'    : final_col_dic['journal'],
                          'issn_col'       : final_col_dic['issn'],
                          'articles_nb_col': bm_pg.COL_NAMES_DOCTYPE_ANALYSIS["articles"]['weight_col'],
                          'items_nb_col'   : bm_pg.COL_NAMES_IF_ANALYSIS['articles_nb'],
                          'init_if_col'    : if_analysis_col,
                          'new_if_col'     : 'IF ' + if_analysis_year,
                         }
    return build_kpi_cols_dic


def _build_dept_doctype_df(init_dept_doctype_df, cols_tup):
    """Builds the document-type data of a department of the Institute 
    with the number of publications per the document-type values.

    Args:
        init_dept_doctype_df (dataframe): Data of the department \
        publications list of a document-type.
        cols_tup (tup): (document-type values col name (str), col name \
        of publications number (str))
    Returns:
        (dataframe): The built data.
    """
    # setting parameters from args
    journal_col, items_nb_col = cols_tup

    # Adding a column with number of articles per journal
    # then dropping duplicate rows
    count_doctype_df = init_dept_doctype_df[journal_col].value_counts().to_frame()
    count_doctype_df = count_doctype_df.rename(columns={"count": items_nb_col})
    count_doctype_df = count_doctype_df.reset_index()
    dept_doctype_df = init_dept_doctype_df.drop_duplicates([journal_col])
    dept_doctype_df = count_doctype_df.merge(dept_doctype_df, how="outer",
                                             on=journal_col)
    return dept_doctype_df


def _build_dept_doctype_kpi(doctype, dept_doctype_df, items_nb_col):
    """Builds the key performance indicators (KPIs) of a given document-type 
    for a department of the Institute.

    Args:
        doctype (str): The document-type label.
        dept_doctype_df (dataframe): Data of the given document-type with \
        the number of publications per document-type values.
        items_nb_col (str): The col name of publications number.
    Returns:
        (dict): The dict keyed by KPIs labels and valued by their values.
    """
    # Number of items by doctype
    nb_doctypes = round(len(dept_doctype_df))

    # Number of documents by doctype
    nb_items = round(dept_doctype_df[items_nb_col].sum())

    # Ratio of items per doctype
    items_per_doctype = 0
    items_per_doctype_max = 0
    if nb_doctypes:
        items_per_doctype = round(nb_items / nb_doctypes, 1)
        items_per_doctype_max = round(dept_doctype_df[items_nb_col].max())

    # Building the dict of doctype KPIs (ToDo: import from pg)
    keys_list = bm_pg.KPI_KEYS_DICT[doctype]
    dept_doctype_kpi_dict = {
        bm_pg.KPI_KEYS_ORDER_DICT[keys_list[0]]: nb_doctypes,
        bm_pg.KPI_KEYS_ORDER_DICT[keys_list[1]]: nb_items,
        bm_pg.KPI_KEYS_ORDER_DICT[keys_list[2]]: items_per_doctype,
        bm_pg.KPI_KEYS_ORDER_DICT[keys_list[3]]: items_per_doctype_max,
    }
    return dept_doctype_kpi_dict


def _build_doctype_kpi(doctype, doctype_df, institute, build_kpi_cols_dic):
    """Builds the key performance indicators (KPIs) dict of a given 
    document-type for each department of the Institute including itself.

    The doctype KPIs dict is built by cycling on each department label, 
    including the Institute's name, through the following steps:

    1. Sets the publications list of the given document type for the department.
    2. Builds the document-type data of a department of the Institute 
    with the number of publications per the document-type values through \
    the `_build_dept_doctype_df` internal function. 
    3. Builds the doctype KPIs dict at the department-label key through the \
    `_build_dept_doctype_kpi` internal function.

    Args:
        doctype (str): The document-type label.
        doctype_df (dataframe): Publications list of the given document-type.
        institute (str): The name of the institute.
        build_kpi_cols_dic (dict): The selected columns names for the process \
        of building KPIs data
    Returns:
        (dict): Hierarchical dict keyed by departments and valued at each \
        key by KPIs dict of the department for the given document type.
    """
    # Setting parameters values from 'build_kpi_cols_dic'
    col_keys = ['depts_col_list', 'journal_col', 'items_nb_col']
    depts_col_list, journal_col, items_nb_col = [build_kpi_cols_dic[key] for key in col_keys]

    # Setting useful col names tup
    cols_tup = (journal_col, items_nb_col)

    # Building the doctype KPIs dict covering all departments
    doctype_kpi_dict = {}
    for dept in [institute] + depts_col_list:
        # Setting the doctype data for "dept"
        if dept!=institute:
            dept_doctype_df = doctype_df[doctype_df[dept]==1].copy()
        else:
            dept_doctype_df = doctype_df.copy()

        # Building the books dataframe for "dept"
        dept_doctype_df = _build_dept_doctype_df(dept_doctype_df, cols_tup)

        # Computing KPI for department 'dept'
        doctype_kpi_dict[dept] = _build_dept_doctype_kpi(doctype, dept_doctype_df, items_nb_col)
    return doctype_kpi_dict


def _build_basic_kpi(institute, pub_df_dict, build_kpi_cols_dic):
    """Builds the basic key performance indicators (KPIs) 
    data of each department of the Institute including itself.

    First, an initial hierarchical dict keyed by doctypes 
    and valued by KPIs dict built through the `_build_doctype_kpi` 
    internal function. 
    Then, a final hierarchical dict is built by cycling on each 
    department label, including the Institute's name, through 
    the following steps:

    1. Building the hierarchical dict at the department_label key \
    and at each-doctype key.
    2. Computing complementary KPIs for the department.
    3. Completing hierarchical dict at the department_label key \
    and at 'complements' key with the computed complementary KPIs.

    The final hierarchical dict is keyed by the departments and valued 
    by a dict keyed by doctypes including complements' key and valued 
    by KPIs extracted from the initial hierarchical dict and 
    the complementary computed ones.

    Args:
        institute (str): Institute's name.
        pub_df_dict (dataframe): Articles data to be analyzed.
        build_kpi_cols_dic (dict): The selected columns names for the process \
        of building KPIs data.
    Returns:
        (hierarchical dict): The dict keyed by departments of \
        the Institute including itself and valued with basic-KPIs \
        dict of each department.
    """
    # Setting useful columns infos
    depts_col_list = build_kpi_cols_dic['depts_col_list']

    # Setting useful KPI dict keys
    pub_nb_key = bm_pg.KPI_KEYS_ORDER_DICT[1]
    art_proc_nb_key = bm_pg.KPI_KEYS_ORDER_DICT[2]
    proc_ratio_key = bm_pg.KPI_KEYS_ORDER_DICT[15]
    chapt_ratio_key = bm_pg.KPI_KEYS_ORDER_DICT[16]

    # Initializing useful dicts
    init_kpi_dict = {}
    items_nb_key_dict = {}

    # Building KPIs dict for all doctypes
    doctypes_list = list(pub_df_dict.keys())
    for doctype in doctypes_list:
        doctype_kpi_dict = _build_doctype_kpi(doctype, pub_df_dict[doctype],
                                              institute, build_kpi_cols_dic)
        init_kpi_dict[doctype] = doctype_kpi_dict
        items_nb_key_dict[doctype] = bm_pg.KPI_KEYS_ORDER_DICT[bm_pg.KPI_KEYS_DICT[doctype][1]]

    # Building the full KPIs dict covering all departments and all doctypes
    kpi_dict = {}
    for dept in [institute] + depts_col_list:
        # Setting KPI dict for department 'dept' and each doctype
        kpi_dict[dept] = {}
        doctype_nb_dict = {}
        for doctype in doctypes_list:
            kpi_dict[dept][doctype] = init_kpi_dict[doctype][dept]
            doctype_nb_dict[doctype] = init_kpi_dict[doctype][dept][items_nb_key_dict[doctype]]

        # Computing complementary KPIs
        art_proc_nb = doctype_nb_dict['articles'] + doctype_nb_dict['proceedings']
        pub_nb = art_proc_nb + doctype_nb_dict['books']
        proc_ratio = 0
        chapt_ratio = 0
        if art_proc_nb:
            proc_ratio = round(doctype_nb_dict['proceedings'] / art_proc_nb * 100)
        if pub_nb:
            chapt_ratio = round(doctype_nb_dict['books'] / pub_nb * 100)

        # Completing KPI dict for department 'dept'
        kpi_dict[dept]['complements'] = {}
        kpi_dict[dept]['complements'][pub_nb_key] = pub_nb
        kpi_dict[dept]['complements'][art_proc_nb_key] = art_proc_nb
        kpi_dict[dept]['complements'][proc_ratio_key] = proc_ratio
        kpi_dict[dept]['complements'][chapt_ratio_key] = chapt_ratio
    return kpi_dict


def _build_dept_if_df(dept_by_journal_df, cols_list):
    """Builds the IFs data for a department.
    Args:
        dept_by_journal_df (dataframe): The statistics by journals \
        data for the department.
        cols_list (list): Useful column names.
    Returns:
        (dataframe): The built IFs data of a department.
    """
    # Setting parameters from 'cols_list'
    journal_col, init_if_col, new_if_col = cols_list[0], cols_list[3], cols_list[4]

    # Selecting useful columns from 'dept_articles_df' dataframe
    dept_if_df = dept_by_journal_df[cols_list[0:4]]

    # Cleaning the 'dept_if_df' dataframe
    dept_if_df = dept_if_df.rename(columns={init_if_col: new_if_col})
    dept_if_df[new_if_col] = dept_if_df[new_if_col].replace(bm_pg.NOT_AVAILABLE, 0)
    dept_if_df = dept_if_df.sort_values(by=[new_if_col, journal_col],
                                        ascending=False)
    dept_if_df = dept_if_df.reset_index().drop(columns=["index"])
    return dept_if_df


def _build_articles_if_kpi(institute, by_journal_dict, if_analysis_folder_path,
                           kpi_dict, build_kpi_cols_dic, verbose=False):
    """Builds the key performance indicators (KPIs) data specific to 
    the impact factors (IFs) for each department of the Institute 
    including itself.

    This is done through the following steps by cycling on the department:

    1. The IFs data for the department is set through the `_build_dept_if_df` \
    internal function. 
    2. The IF KPIs data are computed for the department and the KPIs dict is \
    filled with the computed values at the key corresponding to the label of \
    the department.
    3. The IFs data for the department are saved as openpyxl workbook through \
    `format_page` function imported  from the `bmfuncts.format_files` module.

    Args:
        institute (str): Institute's name.
        by_journal_dict (dict): Dict keyed by department labels (str) of \
        the Institute and valued by data (dataframe) of statistics per journal.
        if_analysis_folder_path (path): Full path to the folder where IFs analysis \
        final results are saved.
        kpi_dict (dict): Hierarchical dict keyed by departments of the Institute \
        including itself and valued with KPIs dict of these keys.
        build_kpi_cols_dic (dict): The selected columns names for the process \
        of building KPIs data.
        verbose (bool): Status of prints (default: False).
    Returns:
        (tup): (KPIs updated data with IFs data (hierarchical dict), name of the column \
        of IFs in the IFs analysis results).
    """
    # Setting useful columns info from args
    col_keys = ['depts_col_list', 'journal_col', 'issn_col', 'articles_nb_col',
                'init_if_col', 'new_if_col']
    (depts_col_list, journal_col, issn_col, articles_nb_col,
     init_if_col, new_if_col) = [build_kpi_cols_dic[key] for key in col_keys]

    # Setting useful columns list
    cols_list = [journal_col, issn_col, articles_nb_col,
                 init_if_col, new_if_col]

    for dept in [institute] + depts_col_list:
        # Setting the statistics by journals data for 'dept'
        dept_by_journal_df = by_journal_dict[dept]

        # Building the 'dept_if_df' dataframe for computing IF KPIs
        dept_if_df= _build_dept_if_df(dept_by_journal_df, cols_list)

        # Computing IF KPIs values for 'dept'
        dept_kpi_dict = kpi_dict[dept]
        nb_articles = dept_kpi_dict['articles'][bm_pg.KPI_KEYS_ORDER_DICT[3]]
        dept_if_sub_df = dept_if_df[dept_if_df[new_if_col]!=0]
        if_moyen = 0
        if nb_articles:
            if_moyen = sum(x[0]*x[1] for x in zip(dept_if_sub_df[new_if_col],
                                                  dept_if_sub_df[articles_nb_col]))/nb_articles
        if_max = np.max(dept_if_sub_df[new_if_col])
        if_min = np.min(dept_if_sub_df[new_if_col])
        dept_if_nul_df = dept_if_df[dept_if_df[new_if_col]==0]
        nb_art_wo_if = dept_if_nul_df[articles_nb_col].sum()
        wo_if_ratio = 0
        if nb_articles:
            wo_if_ratio = nb_art_wo_if / nb_articles * 100

        # Completing the KPIs dict with IF KPIs values
        dept_if_kpi_dict = {
            bm_pg.KPI_KEYS_ORDER_DICT[18]: round(if_max, 1),
            bm_pg.KPI_KEYS_ORDER_DICT[19]: round(if_min, 1),
            bm_pg.KPI_KEYS_ORDER_DICT[20]: round(if_moyen, 1),
            bm_pg.KPI_KEYS_ORDER_DICT[21]: round(nb_art_wo_if),
            bm_pg.KPI_KEYS_ORDER_DICT[22]: round(wo_if_ratio)
        }
        dept_kpi_dict[new_if_col] = dept_if_kpi_dict

        # Updating KPI dict with KPIs of department 'dept'
        kpi_dict[dept] = dept_kpi_dict

        # Saving after formatting the updated dataframe as openpyxl workbook
        file_name = f'{new_if_col}-{dept}'
        dept_xlsx_file_path = Path(if_analysis_folder_path) / Path(file_name + '.xlsx')
        if_anal_df_title = bm_pg.DF_TITLES_LIST[10]
        wb, ws = format_page(dept_if_df, if_anal_df_title)
        ws.title = dept + ' IFs '
        wb.save(dept_xlsx_file_path)

        if verbose:
            message = (f"\n    EXCEL file of {new_if_col} "
                       f"for {dept} department "
                       f"saved in : \n {if_analysis_folder_path}")
            print(message, "\n")
    return kpi_dict, new_if_col


def _build_dept_kpi_data(dept, kpi_dict, if_key, ordered_keys, corpus_year, corpus_year_row):
    """Builds the key performance indicators (KPIs) data for a given department.

    Args:
        dept (str): The department label.
        kpi_dict (dict): Hierarchical dict keyed by departments of the Institute \
        including itself and valued with KPIs dict of these keys. 
        if_key (str): Column name of the analyzed impact factors (either those of \
        the publication year or the last available ones). 
        ordered_keys (list): Ordered list of keys (str) to set the order of the KPIs \
        in the database.
        corpus_year (str): 4 digits year of the corpus.
        corpus_year_row (str): The first column name in the KPIs database and \
        that corresponds to the label of the first row.
    Returns:
        (dataframe): Department KPIs data.
    """
    dept_kpi_dict = kpi_dict[dept]
    new_dept_kpi_dict = {}
    for _, doctype_kpi_dict in dept_kpi_dict.items():
        new_dept_kpi_dict = dict(new_dept_kpi_dict, **doctype_kpi_dict)

    # Building sub dict of publications KPIs of 'dept' in keys order
    # specified by 'ordered_keys'
    dept_basic_kpi_dict = {k: new_dept_kpi_dict[k] for k in ordered_keys[1:17]}
    part_dept_if_kpi_dict = {k: new_dept_kpi_dict[k] for k in ordered_keys[18:23]}
    dept_if_kpi_dict = dict({bm_pg.KPI_KEYS_ORDER_DICT[17]: if_key}, **part_dept_if_kpi_dict)

    # Building 'dept_pub_df' using keys of 'dept_pub_dict' as indexes
    # and setting the name of the values column to 'corpus_year'
    dept_pub_df = pd.DataFrame.from_dict(dept_basic_kpi_dict, orient="index",
                                         columns=[corpus_year])

    # Renaming the index column of 'dept_pub_df' as 'corpus_year_row'
    dept_pub_df = dept_pub_df.reset_index()
    dept_pub_df = dept_pub_df.rename_axis("idx", axis=1)
    dept_pub_df = dept_pub_df.rename(columns={"index": corpus_year_row})

    # Building 'dept_if_df' using keys of 'dept_if_dict' as indexes
    # and setting the name of the values column to 'corpus_year'
    dept_if_df = pd.DataFrame.from_dict(dept_if_kpi_dict, orient="index",
                                        columns=[corpus_year])

    # Renaming the index column of ''dept_if_df as 'corpus_year_row'
    dept_if_df = dept_if_df.reset_index()
    dept_if_df = dept_if_df.rename_axis("idx", axis=1)
    dept_if_df = dept_if_df.rename(columns={"index": corpus_year_row})

    # Combining the two dataframes through rows concatenation
    dept_kpi_df = concat_dfs([dept_pub_df, dept_if_df], dedup=False)
    return dept_kpi_df


def _set_kpi_files_params(final_results_path):
    """Sets IFs specific file and folder.

    Args:
        final_results_path (path): Full path to the folder \
        where final results are saved.
    Returns:
        (tup): publications-lists folder name, \
        base for building names of publications-list files, \
        base for building names of missing-IFs files, \
        name for building names of missing-ISSNs files.
    """
    # Setting aliases for updating KPIs database
    results_sub_folder_alias = bm_pg.ARCHI_RESULTS["kpis"]
    kpi_file_base_alias = bm_pg.ARCHI_RESULTS["kpis file name base"]

    # Setting paths for saving results
    results_kpis_folder_path = final_results_path / Path(results_sub_folder_alias)

    # Checking availability of required results folder
    if not os.path.exists(results_kpis_folder_path):
        os.makedirs(results_kpis_folder_path)
    return kpi_file_base_alias, results_kpis_folder_path


def update_kpi_database(kpi_params, kpi_dict, if_key, depts_col_list, verbose=False):
    """Updates the database of the key performance indicators (KPIs) with the KPIs data 
    of the given corpus.

    The KPIs data for each department are set through the `_build_dept_kpi_data` internal 
    function. 
    These updated databases are saved as openpyxl workbooks using the `format_page` function 
    imported from the `bmfuncts.format_files` module.

    Args:
        kpi_params (list): A list composed of the name of the institute (str), \
        the full path to the folder where final results are saved (path) and \
        the 4 digits year of the corpus (str).
        kpi_dict (dict): Hierarchical dict keyed by departments of the Institute \
        including itself and valued with KPIs dict of these keys.
        if_key (str): Column name of the analyzed impact factors (either those of \
        the publication year or the last available ones).
        depts_col_list (list): The list of the Institute's departments.
        verbose (bool): Status of prints (default = False).
    Returns:
        (dataframe): Institute's KPIs data.
    """
    # Setting parameters values from kpi_params
    institute, final_results_path, corpus_year = kpi_params

    # Setting file name and path for saving results
    kpi_file_base, results_kpis_folder_path = _set_kpi_files_params(final_results_path)

    # Setting useful column names aliases
    corpus_year_row_alias = bm_pg.KPI_KEYS_ORDER_DICT[0]
    ordered_keys = list(bm_pg.KPI_KEYS_ORDER_DICT.values())

    # Initializing return dataframe
    institute_kpi_df = pd.DataFrame()

    # Building as a dataframe the column of KPIs of each 'dept'
    for dept in [institute] + depts_col_list:
        # Building 'dept_kpi_df' using keys of 'kpi_dict' as indexes
        dept_kpi_df = _build_dept_kpi_data(dept, kpi_dict, if_key, ordered_keys,
                                           corpus_year, corpus_year_row_alias)

        # Reading as a dataframe the KPI file of 'dept' if it exists else creating it
        filename = dept + "_" + kpi_file_base + ".xlsx"
        file_path = results_kpis_folder_path / Path(filename)
        if os.path.isfile(file_path):
            db_dept_kpi_df = pd.read_excel(file_path)
            # Updating the dataframe with the column to append
            if corpus_year in db_dept_kpi_df.columns:
                db_dept_kpi_df = db_dept_kpi_df.drop(columns=[corpus_year])
            db_dept_kpi_df = db_dept_kpi_df.merge(dept_kpi_df, how="outer",
                                                  on=corpus_year_row_alias)
        else:
            db_dept_kpi_df = dept_kpi_df

        # Saving after formatting the updated dataframe
        kpi_df_title = bm_pg.DF_TITLES_LIST[6]
        wb, ws = format_page(db_dept_kpi_df, kpi_df_title)
        ws.title = dept + ' KPIs '
        wb.save(file_path)

        if dept==institute:
            institute_kpi_df = db_dept_kpi_df.copy()
        if verbose:
            message = f"    - {dept} KPIs database updated and saved in folder: \n {file_path}"
            print(message)

    return institute_kpi_df


def _set_if_files_params(wf_path, corpus_year):
    """Sets IFs specific file and folder.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): publications-lists folder name, \
        base for building names of publications-list files, \
        base for building names of missing-IFs files, \
        name for building names of missing-ISSNs files.
    """
    # Setting useful aliases
    analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    if_analysis_folder_alias = bm_pg.ARCHI_YEAR["if analysis"]

    # Setting analysis-results paths
    year_folder_path = wf_path / Path(corpus_year)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    if_analysis_folder_path = analysis_folder_path / Path(if_analysis_folder_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(if_analysis_folder_path):
        os.makedirs(if_analysis_folder_path)
    return if_analysis_folder_path


def if_analysis(params_list, if_most_recent_year, progress_callback=None, verbose=False):
    """Performs the analysis per document types together with 
    the analysis of the journals impact-factors (IFs) and update 
    the key performance indicators (KPIs).

    This is done through the following steps:

    1. Performs the analysis per doctypes through the `doctype_analysis` \
    function imported from `bmfuncts.doctype_analysis` module. 
    2. Initializes the KPIs dict with the basic KPIs data through the \
    `_build_basic_kpi` internal function.
    3. Adds to the KPIs dict, the IFs KPIs computed through the \
    `_build_articles_if_kpi` internal function.
    4. Updates the data of the Institute with KPIs dict through \
    the `update_kpi_database` function of the same module.
    5. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        params_list (list): The list composed of the Institute's name (str), \
        the org_tup (tup) that contains parameters of Institute's organization, \
        the full path to working folder (path), the data combination type \
        of corpuses databases (str) and the 4 digits year of the corpus (str).
        if_most_recent_year (str): Most recent year of impact factors.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).
    Returns:
        (tup): (full path to the folder where results of analysis per doctypes are saved,\
        full path to the folder where results of impact-factors analysis are saved, \
        Institute's KPIs data (dataframe), KPIs data (hierarchical dict keyed by \
        departments of the Institute including itself and valued with KPIs dict \
        of these keys)).
    """
    # Setting params values from params_list
    (corpus_year, print_params, institute, org_tup, wf_path,
     datatype, parsing_filenames_dict) = params_list

    # Setting input-data path
    final_results_path = set_results_folder_path(wf_path, datatype)

    # Setting useful folder path
    if_analysis_folder_path =  _set_if_files_params(wf_path, corpus_year)
    if progress_callback:
        progress_callback(5)

    print_step_text("\nAnalysing publications per document types...", print_params)

    # Building analysis dicts
    print("  - Building data per document types...", end="\r")
    doc_params_list = [corpus_year, institute, org_tup, wf_path, datatype,
                       parsing_filenames_dict, final_results_path]
    return_tup = doctype_analysis(doc_params_list, if_most_recent_year,
                                  progress_callback=progress_callback)
    (pub_df_dict, by_journal_dict, if_analysis_col,
     if_analysis_year, doctypes_analysis_folder_path) = return_tup
    print_step_text("  - Data of doctype analysis saved as final results", print_params)
    if progress_callback:
        progress_callback(55)

    # Setting useful columns info
    build_kpi_cols_dic = _set_build_kpi_cols(institute, org_tup, if_analysis_col,
                                             if_analysis_year)
    if progress_callback:
        progress_callback(60)

    # Building the basic KPIs
    print("  - Building basic KPIs...", end="\r")
    kpi_dict = _build_basic_kpi(institute, pub_df_dict, build_kpi_cols_dic)
    print_step_text("  - Basic KPIs built      ", print_params)
    if progress_callback:
        progress_callback(70)

    print_step_text("\nAnalysing journals IFs of publications...", print_params)

    # Building the IFs KPIs
    print("  - Building IFs KPIs...", end="\r")
    return_tup = _build_articles_if_kpi(institute, by_journal_dict,
                                        if_analysis_folder_path, kpi_dict,
                                        build_kpi_cols_dic)
    kpi_dict, new_if_analysis_col = return_tup
    print_step_text("  - IFs KPIs built      ", print_params)
    if progress_callback:
        progress_callback(75)

    print_step_text("\nUpdating KPIs data per Institute's department...", print_params)

    # Updating the KPIs data
    print("  - Building full KPIs data...", end="\r")
    depts_col_list = build_kpi_cols_dic['depts_col_list']
    kpi_params = [institute, final_results_path, corpus_year]
    institute_kpi_df = update_kpi_database(kpi_params, kpi_dict, new_if_analysis_col,
                                           depts_col_list, verbose=verbose)
    print_step_text("  - Full KPIs built for each Institute's department", print_params)
    if progress_callback:
        progress_callback(90)

    # Saving IFs analysis as final result
    status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["ifs"] = True
    save_params_list = [corpus_year, institute, org_tup, wf_path, datatype]
    _ = save_final_results(save_params_list, results_to_save_dict,
                           if_analysis_name=new_if_analysis_col)
    print_step_text("  - KPIs data saved as final results", print_params)
    if progress_callback:
        progress_callback(100)
    return doctypes_analysis_folder_path, if_analysis_folder_path, institute_kpi_df, kpi_dict
