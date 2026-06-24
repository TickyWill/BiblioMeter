"""Module of functions for building statistics per doctype.
"""

__all__ = ['doctype_analysis',
          ]


# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.read_final_results import read_final_pub_list_data
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import set_capwords_lambda
from bmfuncts.useful_functs import concat_dfs


def _set_doctype_files_params(wf_path, corpus_year):
    """Sets doctype analysis specific files and folder paths.

    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (tup): (Dict keyed by document type (str) and valued by full path (path) \
        to file for out data, Dict keyed by doctype (str) and valued \
        by full path (path) to folder for out data, full path to the folder \
        where the results of the analysis per documents types are saved).
    """
    # Setting local parameters
    xlsx_extent = ".xlsx"

    # Setting useful aliases
    analysis_folder_alias = bm_pg.ARCHI_YEAR["analyses"]
    doctypes_analysis_folder_alias = bm_pg.ARCHI_YEAR["doctype analysis"]
    journal_weight_filename_alias = bm_pg.ARCHI_YEAR["journal weight file name"] + xlsx_extent
    proc_weight_filename_alias = bm_pg.ARCHI_YEAR["proceedings weight file name"] + xlsx_extent
    book_weight_filename_alias = bm_pg.ARCHI_YEAR["book weight file name"] + xlsx_extent

    # Setting out-data paths
    year_folder_path = wf_path / Path(str(corpus_year))
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    doctypes_analysis_folder_path = analysis_folder_path / Path(doctypes_analysis_folder_alias)
    sub_folder_path = Path("Departements")

    # Setting useful parameters
    doctypes_list = list(bm_pg.DOC_TYPE_DICT.keys())
    filenames_list = [journal_weight_filename_alias,
                      book_weight_filename_alias,
                      proc_weight_filename_alias,]
    doctype_filenames_dict = dict(zip(doctypes_list, filenames_list))
    folders_paths_list = [doctypes_analysis_folder_path / Path(doctype.capitalize()) \
                          for doctype in doctype_filenames_dict.keys()]
    doctype_folders_dict = dict(zip(doctypes_list, folders_paths_list))

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(doctypes_analysis_folder_path):
        os.makedirs(doctypes_analysis_folder_path)
    for doctype in doctype_filenames_dict.keys():
        if not os.path.exists(doctype_folders_dict[doctype]):
            os.makedirs(doctype_folders_dict[doctype])
        if not os.path.exists(doctype_folders_dict[doctype] / sub_folder_path):
            os.makedirs(doctype_folders_dict[doctype] / sub_folder_path)

    file_params = (doctype_filenames_dict, doctype_folders_dict,
                  doctypes_analysis_folder_path, sub_folder_path)
    return file_params


def _set_analysis_if_cols_info(corpus_year, if_most_recent_year):
    """Sets the specific columns names for the impact-factors analysis.

    Args:
        corpus_year (str): 4 digits year of the corpus.
        if_most_recent_year (str): Most recent year of impact factors.
    Returns:
        (tup): (List of the columns names (str) to be used for \
        the IF analysis, Name (str) of the column of IFs in the IFs \
        analysis results, 4 digits-year (str) of IFs analysis).
    """
    # Setting useful aliases
    most_recent_year_if_col_base_alias = bm_pg.COL_NAMES_BONUS["IF en cours"]
    corpus_year_if_col_alias = bm_pg.COL_NAMES_BONUS['IF année publi']

    # Setting IFs column names info
    most_recent_year_if_col = f'{most_recent_year_if_col_base_alias}, {if_most_recent_year}'
    if_col_dict = {most_recent_year_if_col : if_most_recent_year,
                   corpus_year_if_col_alias: corpus_year}

    if if_most_recent_year>=corpus_year:
        if_analysis_col = bm_pg.ANALYSIS_IF
        if_analysis_year = if_col_dict[bm_pg.ANALYSIS_IF]
    else:
        if_analysis_col = most_recent_year_if_col
        if_analysis_year = if_most_recent_year
    analysis_if_col_list = [most_recent_year_if_col, corpus_year_if_col_alias]
    return analysis_if_col_list, if_analysis_col, if_analysis_year


def _set_full_doctype_cols_dic(init_doctype_cols_dic):
    """Adds the specific columns to document types to the initialized columns dict."""
    doctype_cols_dic = init_doctype_cols_dic.copy()
    doctypes_list = list(bm_pg.COL_NAMES_DOCTYPE_ANALYSIS.keys())
    doctype_cols_keys_dic = {}
    for doctype in doctypes_list:
        col_names_dic = bm_pg.COL_NAMES_DOCTYPE_ANALYSIS[doctype]
        final_doctype_col_key = f'{doctype}_doctype_col'
        weight_col_key = f'{doctype}_weight_col'
        doctype_cols_keys_dic[doctype] = (final_doctype_col_key, weight_col_key)
        doctype_cols_dic[final_doctype_col_key] = col_names_dic['doctype_col']
        doctype_cols_dic[weight_col_key] = col_names_dic['weight_col']
    return doctype_cols_dic, doctype_cols_keys_dic


def _set_doctype_cols_dic(institute, org_tup, corpus_year, if_most_recent_year):
    """Builds a dict setting selected columns names for the process 
    of data for the document-types analysis.

    The specific columns names for the impact-factors analysis are built 
    through the `_set_analysis_if_cols_info` internal function.

    Args:
        institute (str): The Institute name.
        org_tup (tup): Contains parameters of Institute organization.
        corpus_year (str): 4 digits year of the corpus.
        if_most_recent_year (str): Most recent year of impact factors.
    Returns:
        (tuple) : (The selected columns names for the process \
        of document-types analysis (dict), the list of Institute's \
        departments (list), the set IF year for the analysis)
    """
    # Setting useful column names from final column names of the publications list data
    final_cols_tup = set_final_col_names(institute, org_tup)
    final_col_dic, depts_col_list = final_cols_tup

    # Setting specific columns names for the impact-factors analysis
    return_tup = _set_analysis_if_cols_info(corpus_year, if_most_recent_year)
    analysis_if_col_list, if_analysis_col, if_analysis_year = return_tup
    most_recent_year_if_col, corpus_year_if_col = analysis_if_col_list

    # Initializing the columns dict
    init_doctype_cols_dic = {'pub_id_col'             : final_col_dic['pub_id'],
                             'journal_col'            : final_col_dic['journal'],
                             'issn_col'               : final_col_dic['issn'],
                             'doctype_col'            : final_col_dic['doc_type'],
                             'journal_norm_col'       : bm_pg.COL_NAMES['temp_col'][1],
                             'pub_ids_col'            : bm_pg.COL_NAMES_BONUS["pub_ids list"],
                             'most_recent_year_if_col': most_recent_year_if_col,
                             'corpus_year_if_col'     : corpus_year_if_col,
                             'if_analysis_col'        : if_analysis_col
                            }

    # Complementing the columns dict with columns specific to document types
    doctype_cols_dic, doctype_cols_keys_dic = _set_full_doctype_cols_dic(init_doctype_cols_dic)

    return doctype_cols_dic, doctype_cols_keys_dic, depts_col_list, if_analysis_year


def _unique_journal_name(init_analysis_df, journal_col, issn_col):
    """Sets a unique journal name by ISSN value.

    Args:
        init_analysis_df (dataframe): The initial data to be modified.
        journal_col (str): The name of the column of the journal names.
        issn_col (str) The name of the column of the ISSNs.
    Returns:
        (dataframe): The modified data.
    """
    analysis_df = pd.DataFrame(columns=init_analysis_df.columns)
    for _, df in init_analysis_df.groupby(by=[issn_col]):
        issn_df = df.copy()
        issn = issn_df[issn_col].to_list()[0]
        journal_names_list = issn_df[journal_col].to_list()
        if len(journal_names_list)>1:
            if issn!=bm_pg.UNKNOWN:
                journal_length_list = [len(journal) for journal in journal_names_list]
                journal_names_dict = dict(zip(journal_length_list, journal_names_list))
                length_min = min(journal_length_list)
                issn_df[journal_col] = journal_names_dict[length_min]
            else:
                journal_names_list = list(set(issn_df[journal_col].to_list()))
                journal_issn_list = [issn + str(num) for num in range(len(journal_names_list))]
                journal_names_dict = dict(zip(journal_names_list, journal_issn_list))
                issn_df[issn_col] = issn_df[journal_col].copy()
                issn_df[issn_col] = issn_df[issn_col].map(journal_names_dict)
        analysis_df = concat_dfs([analysis_df, issn_df], dedup=False, concat_ignore_index=True)
    return analysis_df


def _read_parsing_pub_data(dedup_read_params):
    """Reads saved data of publications list resulting from the parsing step.

    It uses the `read_final_dedup` function imported from 
    the `bmfuncts.read_final_results` module.

    Args:
        dedup_read_params (list): Composed of the 4 digits year of the corpus, \
        of the full path to working folder, of the dict giving the name of \
        the parsing file for each parsed item and of the full path to the folder \
        where final results are saved.
    Returns:
        (dataframe): The data of the publications list.
    """
    # Getting the dict of deduplication results
    dedup_parsing_dict = read_final_dedup(dedup_read_params)

    # Getting ID of each publication with associated main metadata
    parsing_pub_key = bm_pg.PARSING_KEYS_DIC['parsing_pub']
    parsing_pub_df = dedup_parsing_dict[parsing_pub_key]
    return parsing_pub_df


def _build_doctype_analysis_data(data_params_list, doctype_cols_tup):
    """Builds the data of publications list to be analyzed for each document types.

    The list of documents-types items is given by the 'DOC_TYPE_DICT' global 
    imported from the `bmfuncts.pub_globals` module. 
    The data are built through the following steps:

    1. A dict keyed by documents-type values and valued by normalized documents-type \
    values is built through the use of parsing results returned by the \
    `_read_articles_data` internal function.
    2. The data of the final publication list is got through the `read_final_pub_list_data` \
    function imported from the `bmfuncts.useful_functs` module.
    3. The journal names are normalized using the dict built at step 1.
    4. The words of the values of journal columns and documents types are capitalized through \
    the `set_capwords_lambda` lambda function imported from the `bmfuncts.useful_functs` module.
    5. The data thus obtained are split into data of each documents-types items.

    Args:
        data_params_list (list): The list composed of the full path \
        to working folder (path), the data-combination type (str) of corpus \
        databases and the 4 digits year of the corpus (str).
        doctype_cols_tup (tup): (The selected columns names for the process \
        of document-types analysis (dict), the departments (list) of the Institute).
    Returns:
        (dict): The dict keyed per documents-types items (str) and valued \
        by the data (dataframe) built for each document type.
    """
    # Setting parameters values from data_params_list
    (corpus_year, wf_path, datatype, parsing_filenames_dict,
     final_results_path) = data_params_list

    # Setting input-data path
    final_results_path = set_results_folder_path(wf_path, datatype)

    # Setting useful column names list
    doctype_cols_dic, depts_cols_list = doctype_cols_tup
    col_keys = ['pub_id_col', 'journal_col', 'doctype_col', 'issn_col', 'journal_norm_col']
    sub_cols_list = [doctype_cols_dic[col_key] for col_key in col_keys]
    col_keys = ['most_recent_year_if_col', 'corpus_year_if_col']
    if_cols_list = [doctype_cols_dic[key] for key in col_keys]
    full_cols_list = sub_cols_list[:-1] + depts_cols_list + if_cols_list

    # Setting used column names
    journal_col, doctype_col, issn_col, journal_norm_col = sub_cols_list[1:]

    # Getting articles data resulting from deduplication parsing
    dedup_read_params = [corpus_year, parsing_filenames_dict, final_results_path]
    parsing_pub_df = _read_parsing_pub_data(dedup_read_params)

    # Building the dict {journal name : normalized journal name,}
    # from the deduplication results
    journal_norm_dict = dict(zip(parsing_pub_df[journal_col],
                                 parsing_pub_df[journal_norm_col]))

    # Initializing the data to be analyzed
    pub_df = read_final_pub_list_data(final_results_path,
                                      corpus_year, full_cols_list)

    # Setting final data to be analyzed
    analysis_df = _unique_journal_name(pub_df, journal_col, issn_col)
    analysis_df[journal_norm_col] = analysis_df[journal_col]
    analysis_df[journal_norm_col] = analysis_df[journal_norm_col].map(journal_norm_dict)
    analysis_df[journal_norm_col] = analysis_df.apply(set_capwords_lambda(journal_norm_col),
                                                      axis=1)
    analysis_df[journal_col] = analysis_df.apply(set_capwords_lambda(journal_col), axis=1)
    analysis_df[doctype_col] = analysis_df.apply(set_capwords_lambda(doctype_col), axis=1)

    # Building the dict of data to be analyzed
    pub_df_dict = {}
    for doctype, docname_list in bm_pg.DOC_TYPE_DICT.items():
        pub_df_dict[doctype] = analysis_df[analysis_df[doctype_col].isin(docname_list)]
    return pub_df_dict


def _set_by_issn_df(by_doc_df, idx_doc, issn, dg, drop_dup_cols,
                    journal_col, norm_doc):
    """Computes the statistics data of a given ISSN with attached 
    number of publications and list of publications IDs.

    Args:
        by_doc_df (dataframe): The data where the statistics will be set.
        idx_doc (int): The index at which the statistics will be set.
        issn (str): The given ISSN value for which the statistics data \
        are computed.
        dg (dataframe): The data of publications list for the given \
        ISSN value.
        drop_dup_cols (list): The list of columns names (str) for dropping \
        duplicates in 'dg' data.
        journal_col (str): The column name of documents-types values.
        norm_doc (str): The normalized name of the document-type value \
        for the given ISSN value.
    Returns:
        (dataframe): The data where the statistics have been set.
    """
    # Setting useful col names
    pub_id_col = drop_dup_cols[0]
    cols_list = by_doc_df.columns
    (final_doctype_col, issn_col, weight_col,
     pub_ids_col, if_analysis_col) = cols_list

    dg = dg.drop_duplicates(drop_dup_cols)
    by_doc_df.loc[idx_doc, issn_col] = issn

    # Setting unique doc_name
    doc_names_list = list(set(dg[journal_col].tolist()))
    doc_name = doc_names_list[0]
    if len(doc_names_list)>1:
        doc_name = norm_doc
    by_doc_df.loc[idx_doc, final_doctype_col] = doc_name

    # Managing unknown IF
    ifs_list = list(set(dg[if_analysis_col].tolist()))
    ifs_new_list = [x for x in ifs_list if x!=bm_pg.UNKNOWN]
    if_value = bm_pg.NOT_AVAILABLE
    if ifs_new_list:
        if_value = ifs_new_list[0]
    by_doc_df.loc[idx_doc, if_analysis_col] = if_value

    # Setting stat values
    pub_ids_list = dg[pub_id_col].tolist()
    pub_ids_nb = len(pub_ids_list)
    by_doc_df.loc[idx_doc, weight_col] = pub_ids_nb
    pud_ids_txt = "; ".join(pub_ids_list)
    by_doc_df.loc[idx_doc, pub_ids_col] = pud_ids_txt
    return by_doc_df


def _build_doctype_stat(doctype_df, doctype_col_keys_tup, doctype_cols_dic):
    """Builds the statistics data of a given document type with one row 
    per document-type value with attached number of publications and 
    list of publications IDs.

    To do that, it uses the `_set_by_issn_df` internal function.

    Args:
        doctype_df (dataframe): The data of publications list \
        of the documents type to be analyzed.
        doctype_cols_dic (dict): The dict giving the columns names for the \
        process of building document_types analysis data.
    Returns:
        (tup): (The built data (dataframe), The maximum index \
        to wrap the list of publications IDs when saving data as \
        formatted files).
    """
    # Setting column names from 'doctype_cols_dic'
    final_doctype_col_key, weight_col_key = doctype_col_keys_tup
    col_keys = ['pub_id_col', 'journal_col', 'issn_col', 'journal_norm_col',
                'pub_ids_col', final_doctype_col_key, weight_col_key, 'if_analysis_col']
    all_cols_list = [doctype_cols_dic[key] for key in col_keys]
    (pub_id_col, journal_col, issn_col, journal_norm_col, pub_ids_col,
     final_doctype_col, weight_col, if_analysis_col) = all_cols_list

    # Setting useful cols list
    cols_list = [final_doctype_col, issn_col, weight_col,
                 pub_ids_col, if_analysis_col]

    by_doc_df = pd.DataFrame(columns=cols_list)
    idx_doc = 0
    for issn, issn_dg in doctype_df.groupby(issn_col):
        if bm_pg.UNKNOWN in issn:
            issn = bm_pg.NOT_AVAILABLE
            for doc, doc_dg in issn_dg.groupby(journal_norm_col):
                norm_doc = doc
                drop_dup_cols = [pub_id_col, journal_norm_col]
                by_doc_df = _set_by_issn_df(by_doc_df, idx_doc, issn, doc_dg,
                                            drop_dup_cols, journal_col, norm_doc)
        else:
            norm_doc = issn_dg[journal_norm_col].to_list()[0]
            drop_dup_cols = [pub_id_col, issn_col]
            by_doc_df = _set_by_issn_df(by_doc_df, idx_doc, issn, issn_dg,
                                        drop_dup_cols, journal_col, norm_doc)
        idx_doc += 1
    by_doc_df = by_doc_df.sort_values(by=[weight_col], ascending=False)

    # Setting max index of rows where text should be wrapped
    wrap_df = by_doc_df[by_doc_df[weight_col]>10]
    idx_wrap = len(wrap_df)
    return by_doc_df, idx_wrap


def _build_dept_df(institute, dept, df):
    """Builds the publications list data for a given department by selecting 
    them in the full publications list data.

    Args:
        institute (str): The institute name.
        dept (str): The department label.
        df (dataframe): The full publications-list data.
    Returns:
        (dataframe): The publications-list data of the given department.
    """
    if dept!=institute:
        dept_df = df[df[dept]==1].copy()
    else:
        dept_df = df.copy()
    return dept_df


def _build_and_save_doctype_stat(stat_params_list, pub_df_dict,
                                 doctype_cols_tup, doctype_cols_keys_dic):
    """Builds the statistics data of publications per documents types for each 
    department of the Institute including itself.

    First, it sets the full path to the files of publications list for each 
    document type. 
    Then, it builds the statistics data by cycling on department and 
    on documents types, the following steps:

    1. The publications list of the given document type for the given \
    department are built through the `_build_dept_df` internal function.
    2. The statistics data of the given document type for the given \
    department are built through the `_build_doctype_stat` internal \
    function.
    3. These statistics data of the given document type for the given \
    department are saved through the `save_formatted_df_to_xlsx` \
    function imported from `bmfuncts.format_files` module.

    Args:
        stat_params_list (list): The list composed of the Institute name (str), \
        the full path to working folder (path), and the 4 digits year \
        of the corpus (str).
        pub_df_dict (dict): The dict keyed by documents types and valued \
        by the publications list data of each documents type.
        doctype_cols_tup (tup): The columns info as returned by \
        the `_set_doctype_cols_dic` internal function.
    Returns:
        (tup): (Dict keyed by department labels (str) of the Institute \
        and valued by data (dataframe) of statistics per journal, full path \
        to the folder where the results of the analysis per document types \
        are saved).
    """
    # Setting parameters values from 'stat_params_list'
    institute, wf_path, corpus_year = stat_params_list

    # Setting parameters values from 'doctype_cols_tup'
    doctype_cols_dic, depts_col_list = doctype_cols_tup

    # Setting files and their folder parameters
    files_params = _set_doctype_files_params(wf_path, corpus_year)
    (doctype_filenames_dict, doctype_folders_dict,
     doctypes_analysis_folder_path, sub_folder_path) = files_params

    by_journal_dict = {}
    for dept in [institute] + depts_col_list:
        # Building stat dataframes for department 'dept'
        for doctype, doctype_file in doctype_filenames_dict.items():
            doctype_df = pub_df_dict[doctype]
            doctype_col_keys_tup = doctype_cols_keys_dic[doctype]

            # Building the doctype data for "dept"
            dept_doctype_df = _build_dept_df(institute, dept, doctype_df)
            dept_doctype_df = dept_doctype_df.drop(columns=depts_col_list)

            # Building statistic data by document of doctype
            return_tup = _build_doctype_stat(dept_doctype_df, doctype_col_keys_tup,
                                             doctype_cols_dic)
            by_doc_dept_df, idx_wrap = return_tup

            # Keeping the articles data for IF analysis
            if doctype=="articles":
                by_journal_dict[dept] = by_doc_dept_df

            # Saving formatted stat data
            doctype_stat_title = bm_pg.DF_TITLES_LIST[13]
            sheet_name_base = f"{bm_pg.COL_NAMES_DOCTYPE_ANALYSIS[doctype]['doctype_col']}"
            sheet_name = f'{sheet_name_base} {corpus_year}'
            dept_doctype_file = f'{dept}-{doctype_file}'
            doctype_folder = doctype_folders_dict[doctype] / sub_folder_path
            if dept==institute:
                doctype_folder = doctype_folders_dict[doctype]
            save_formatted_df_to_xlsx(doctype_folder, dept_doctype_file,
                                      by_doc_dept_df, doctype_stat_title,
                                      sheet_name, idx_wrap=idx_wrap)
    return by_journal_dict, doctypes_analysis_folder_path


def doctype_analysis(doc_params_list, if_most_recent_year, progress_callback=None):
    """Performs the analysis per documents-types of the Institute 
    publications of the 'year' corpus.

    This is done through the following steps:

    1. The specific columns names for the impact-factors analysis \
    are set through the `_set_analysis_if_cols_lis` internal function.
    2. The data of the publications list per documents-types to be \
    analyzed are built through the `_build_doctype_analysis_data` \
    internal function.
    3. The statistic data are built for each documents type through \
    the function `_build_and_save_doctype_stat` internal function.
    4. The results of this analysis for the 'datatype' case are saved \
    through the `save_final_results` function imported from \
    `bmfuncts.save_final_results` module.

    Args:
        doc_params_list (list):  The list composed of the Institute name (str), \
        the org_tup (tup) that contains parameters of Institute organization, \
        the full path to working folder (path), the data combination type \
        of corpuses databases (str) and the 4 digits year of the corpus (str).
        if_most_recent_year (str): Most recent year of impact factors.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
    Returns:
        (tup): (Dict keyed by document-types labels (str) and valued by \
        the publications lists (dataframe) of each document-type, \
        Dict keyed by department labels (str) of the Institute \
        and valued by data (dataframe) of statistics per journal, \
        Name (str) of the column of IFs in the IFs analysis results, \
        4 digits-year (str) of IFs analysis, Full path to the folder \
        where IFs analysis final results are saved).
    """
    # Setting params values from doc_params_list
    (corpus_year, institute, org_tup, wf_path, datatype,
     parsing_filenames_dict, final_results_path) = doc_params_list

    # Setting useful columns info
    return_tup = _set_doctype_cols_dic(institute, org_tup, corpus_year, if_most_recent_year)
    doctype_cols_dic, doctype_cols_keys_dic, depts_col_list, if_analysis_year = return_tup
    if_analysis_col = doctype_cols_dic['if_analysis_col']
    doctype_cols_tup = (doctype_cols_dic, depts_col_list)

    # Building the dataframe of publications data to be analyzed
    data_params_list = [corpus_year, wf_path, datatype, parsing_filenames_dict, final_results_path]
    pub_df_dict = _build_doctype_analysis_data(data_params_list, doctype_cols_tup)
    if progress_callback:
        progress_callback(20)

    # Building and saving statistics for each doctype
    stat_params_list = [institute, wf_path, corpus_year]
    return_tup = _build_and_save_doctype_stat(stat_params_list, pub_df_dict,
                                              doctype_cols_tup, doctype_cols_keys_dic)
    by_journal_dict, doctypes_analysis_folder_path = return_tup

    # Saving stat analysis as final result
    status_values = len(bm_pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(bm_pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["doctypes"] = True
    save_params_list = [corpus_year, institute, org_tup, wf_path, datatype]
    save_final_results(save_params_list, results_to_save_dict)
    if progress_callback:
        progress_callback(50)
    final_return_tup = (pub_df_dict, by_journal_dict, if_analysis_col,
                        if_analysis_year, doctypes_analysis_folder_path)
    return final_return_tup
