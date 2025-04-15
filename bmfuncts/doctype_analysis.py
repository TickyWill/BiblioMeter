"""Module of functions for building statistics per doctype.

"""

__all__ = ['build_doctype_analysis_data',
           'doctype_analysis',
          ]


# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import pandas as pd
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.format_files import save_formatted_df_to_xlsx
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.useful_functs import set_capwords_lambda
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import get_final_dedup
from bmfuncts.useful_functs import read_final_pub_list_data
from bmfuncts.useful_functs import set_saved_results_path


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
            if issn!=bp.UNKNOWN:
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


def _read_articles_data(bibliometer_path, saved_results_path, corpus_year):
    """Reads saved data of publications list resulting from the parsing step.

    It uses the `get_final_dedup` function imported from the 
    the `bmfuncts.useful_functs` module.

    Args:
        bibliometer_path (path): Full path to working folder.
        saved_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The data of the publications list.
    """
    # Setting useful aliases
    articles_item_alias = bp.PARSING_ITEMS_LIST[0]

    # Getting the dict of deduplication results
    dedup_parsing_dict = get_final_dedup(bibliometer_path,
                                         saved_results_path,
                                         corpus_year)

    # Getting ID of each author with author name
    articles_df = dedup_parsing_dict[articles_item_alias]
    return articles_df


def build_doctype_analysis_data(bibliometer_path, datatype, corpus_year,
                                final_cols_tup, if_col_list=None):
    """Builds the data of publications list to be analyzed for each documents types.

    The list of documents-types items is ['articles', 'proceedings', 'books']. 
    The data are built through the following steps:

    1. A dict keyed by documents-type values and valued by normalized documents-type \
    values is built through the use of parsing results returned by the \
    `_read_articles_data` internal function.
    2. The data of the final publication list is got through the `read_final_pub_list_data` \
    function imported from the `bmfuncts.useful_functs` module.
    3. The journal names are normalized using the dict built at step 1.
    4. THe words of the values of journal columns and documents types are capitalized through \
    the `set_capwords_lambda` lambda function imported from the `bmfuncts.useful_functs` module.
    5. The data thus obtained are split into data of each documents-types items.

    Args:
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        final_cols_tup (tup): (final columns names dict, departments columns list).
        if_col_list (list): Optional list of column names of impact-factors.
    Returns:
        (dict): The dict keyed per documents-types items (str) and valued \
        by the data (dataframe) built for each documents type.
    """
    # Setting input-data path
    saved_results_path = set_saved_results_path(bibliometer_path, datatype)

    # Setting useful aliases
    journal_norm_col_alias = bp.COL_NAMES['temp_col'][1]

    # Setting useful column names
    final_col_dic, depts_col_list = final_cols_tup
    pub_id_col = final_col_dic['pub_id']
    journal_col = final_col_dic['journal']
    doctype_col = final_col_dic['doc_type']
    issn_col = final_col_dic['issn']

    # Getting articles data resulting from deduplication parsing
    parsing_articles_df = _read_articles_data(bibliometer_path,
                                              saved_results_path, corpus_year)

    # Building the dict {journal name : normalized journal name,}
    # from the deduplication results
    journal_norm_dict = dict(zip(parsing_articles_df[journal_col],
                                 parsing_articles_df[journal_norm_col_alias]))

    # Initializing the dataframe to be analysed
    cols_list = [pub_id_col, journal_col, doctype_col, issn_col] + \
                depts_col_list
    if if_col_list:
        cols_list += if_col_list
    pub_df = read_final_pub_list_data(saved_results_path,
                                      corpus_year, cols_list)

    # Setting final dataframe to be analyzed
    analysis_df = _unique_journal_name(pub_df, journal_col, issn_col)
    analysis_df[journal_norm_col_alias] = analysis_df[journal_col]
    analysis_df[journal_norm_col_alias] = analysis_df[journal_norm_col_alias].map(journal_norm_dict)
    analysis_df[journal_norm_col_alias] = analysis_df.apply(set_capwords_lambda(journal_norm_col_alias),
                                                            axis=1)
    analysis_df[journal_col] = analysis_df.apply(set_capwords_lambda(journal_col), axis=1)
    analysis_df[doctype_col] = analysis_df.apply(set_capwords_lambda(doctype_col), axis=1)

    # Setting articles dataframe to be analyzed
    articles_df = analysis_df[analysis_df[doctype_col].isin(pg.DOC_TYPE_DICT['Articles'])]

    # Setting proceedings dataframe to be analyzed
    proceedings_df = analysis_df[analysis_df[doctype_col].isin(pg.DOC_TYPE_DICT['Proceedings'])]

    # Setting books dataframe to be analyzed
    books_df = analysis_df[analysis_df[doctype_col].isin(pg.DOC_TYPE_DICT['Books'])]

    # Setting pub_df_dict
    pub_df_dict = {'articles': articles_df, 'proceedings': proceedings_df, 'books': books_df}
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
        drop_dup_cols (list): The list of columns names (str) for droping \
        duplicates in 'dg' data.
        journal_col (str): The column name of documents-types values.
        norm_doc (str): The normalized name of the document-type value \
        for the given ISSN value.
    Returns:
        (dataframe): The data where the statistics have been set.
    """
    # Setting useful col names
    cols_list = by_doc_df.columns
    final_doctype_col = cols_list[0]
    issn_col = cols_list[1]
    weight_col = cols_list[2]
    pub_ids_col = cols_list[3]
    if_analysis_col = cols_list[4]
    pub_id_col = drop_dup_cols[0]

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
    ifs_new_list = [x for x in ifs_list if x!=bp.UNKNOWN]
    if_value = "Not available"
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


def _build_doctype_stat(doctype, doctype_df, if_analysis_col, final_col_dic):
    """Builds the statistics data of a given document type with one row 
    per document-type value with attached number of publications and 
    list of publications IDs.

    To do that, it uses the `_set_by_issn_df` internal function.

    Args:
        doctype (str): The documents type label.
        doctype_df (dataframe): The data of publications list \
        of the documents type to be analyzed.
        if_analysis_col(str): Name of the column of IFs in the \
        analysis results.
        final_col_dic (dict): The dict keyed by columns labels \
        and valued by final columns names of the statistics data.
    Returns:
        (tup): (The built data (dataframe), The maximum index \
        to wrap the list of publications IDs when saving data as \
        formatted files).
    """
    # Setting useful column names
    pub_id_col = final_col_dic['pub_id']
    journal_col = final_col_dic['journal']
    issn_col = final_col_dic['issn']

    # Setting useful local aliases
    journal_norm_col_alias = bp.COL_NAMES['temp_col'][1]
    pub_ids_alias = pg.COL_NAMES_BONUS["pub_ids list"]  # "Liste des Pub_ids"
    final_doctype_alias = pg.COL_NAMES_DOCTYPE_ANALYSIS[doctype]
    weight_alias = pg.COL_NAMES_DOCTYPE_ANALYSIS["articles_nb"]
    if doctype=="books":
        weight_alias = pg.COL_NAMES_DOCTYPE_ANALYSIS["chapters_nb"]

    # Setting useful cols tup
    cols_list = [final_doctype_alias, issn_col, weight_alias,
                 pub_ids_alias, if_analysis_col]

    by_doc_df = pd.DataFrame(columns=cols_list)
    idx_doc = 0
    for issn, issn_dg in doctype_df.groupby(issn_col):
        if bp.UNKNOWN in issn:
            issn = "Not available"
            for doc, doc_dg in issn_dg.groupby(journal_norm_col_alias):
                norm_doc = doc
                drop_dup_cols = [pub_id_col, journal_norm_col_alias]
                by_doc_df = _set_by_issn_df(by_doc_df, idx_doc, issn, doc_dg,
                                            drop_dup_cols, journal_col, norm_doc)
        else:
            norm_doc = issn_dg[journal_norm_col_alias].to_list()[0]
            drop_dup_cols = [pub_id_col, issn_col]
            by_doc_df = _set_by_issn_df(by_doc_df, idx_doc, issn, issn_dg,
                                        drop_dup_cols, journal_col, norm_doc)
        idx_doc += 1
    by_doc_df = by_doc_df.sort_values(by=[weight_alias], ascending=False)

    # Setting max index of rows where text should be wrapped
    wrap_df = by_doc_df[by_doc_df[weight_alias]>10]
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


def _build_and_save_doctype_stat(institute, bibliometer_path, pub_df_dict,
                                 corpus_year, if_analysis_col, final_cols_tup):
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
        institute (str): Institute name.
        bibliometer_path (path): Full path to working folder.
        pub_df_dict (dict): The dict keyed by documents types and valued \
        by the publications list data of each documents type.
        corpus_year (str): 4 digits year of the corpus.
        if_analysis_col (str): Name of the column of IFs in the IFs \
        analysis results.
        final_cols_tup (tup): The columns info as returned by \
        the `set_final_col_names` function imported from the \
        `bmfuncts.rename_cols` module.
    Returns:
        (tup): (Dict keyed by department labels (str) of the Institute \
        and valued by data (dataframe) of statistics per journal, full path \
        to the folder where the results of the anqlysis per documents types \
        are saved).
    """
    # Setting parameters from args
    final_col_dic, depts_col_list = final_cols_tup

    # Setting local parameters
    xlsx_extent = ".xlsx"

    # Setting useful aliases
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    doctypes_analysis_folder_alias = pg.ARCHI_YEAR["doctype analysis"]
    journal_weight_filename_alias = pg.ARCHI_YEAR["journal weight file name"] + xlsx_extent
    proc_weight_filename_alias = pg.ARCHI_YEAR["proceedings weight file name"] + xlsx_extent
    book_weight_filename_alias = pg.ARCHI_YEAR["book weight file name"] + xlsx_extent

    # Setting out-data paths
    year_folder_path = bibliometer_path / Path(str(corpus_year))
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    doctypes_analysis_folder_path = analysis_folder_path / Path(doctypes_analysis_folder_alias)
    sub_folder_path = Path("Departements")

    # Setting useful parameters
    doctypes_list = list(pub_df_dict.keys())
    filenames_list = [journal_weight_filename_alias,
                      proc_weight_filename_alias,
                      book_weight_filename_alias]
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

    by_journal_dict = {}
    for dept in [institute] + depts_col_list:
        # Building stat dataframes for department 'dept'
        for doctype, doctype_file in doctype_filenames_dict.items():
            doctype_df = pub_df_dict[doctype]

            # Building the doctype data for "dept"
            dept_doctype_df = _build_dept_df(institute, dept, doctype_df)
            dept_doctype_df = dept_doctype_df.drop(columns=depts_col_list)

            # Building statistic data by document of doctype
            by_doc_dept_df, idx_wrap = _build_doctype_stat(doctype, dept_doctype_df,
                                                           if_analysis_col, final_col_dic)

            # Keeping the articles data for IF analysis
            if doctype=="articles":
                by_journal_dict[dept] = by_doc_dept_df

            # Saving formatted stat data
            doctype_stat_title = pg.DF_TITLES_LIST[13]
            sheet_name = pg.COL_NAMES_DOCTYPE_ANALYSIS[doctype] + " " + corpus_year
            dept_doctype_file = dept + "-" + doctype_file
            doctype_folder = doctype_folders_dict[doctype] / sub_folder_path
            if dept==institute:
                doctype_folder = doctype_folders_dict[doctype]
            save_formatted_df_to_xlsx(doctype_folder, dept_doctype_file,
                                      by_doc_dept_df, doctype_stat_title,
                                      sheet_name, idx_wrap=idx_wrap)
    return by_journal_dict, doctypes_analysis_folder_path


def _set_analysis_if_cols_list(corpus_year, if_most_recent_year):
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
    most_recent_year_if_col_base_alias = pg.COL_NAMES_BONUS["IF en cours"]
    corpus_year_if_col_alias = pg.COL_NAMES_BONUS['IF année publi']

    # Setting IFs column names info
    most_recent_year_if_col = most_recent_year_if_col_base_alias + \
                              ", " + if_most_recent_year
    if_col_dict = {most_recent_year_if_col: if_most_recent_year,
                   corpus_year_if_col_alias: corpus_year}
    if if_most_recent_year>=corpus_year:
        if_analysis_col = pg.ANALYSIS_IF
        if_analysis_year = if_col_dict[pg.ANALYSIS_IF]
    else:
        if_analysis_col = most_recent_year_if_col
        if_analysis_year = if_most_recent_year
    analysis_if_col_list = list(if_col_dict.keys())
    return analysis_if_col_list, if_analysis_col, if_analysis_year


def doctype_analysis(institute, org_tup, bibliometer_path, datatype,
                     corpus_year, if_most_recent_year,
                     progress_callback=None):
    """Performs the analysis per documents-types of the Institute 
    publications of the 'year' corpus.

    This is done through the following steps:

    1. The specific columns names for the impact-factors analysis \
    are set through the `_set_analysis_if_cols_lis` internal function. 
    2. The data of the publications list per documents-types to be \
    analyzed are built through the `build_doctype_analysis_data` \
    function of the same module. 
    3. The statistic data are built for each documents type through \
    the function `_build_and_save_doctype_stat` internal function. 
    4. The results of this analysis for the 'datatype' case are saved \
    through the `save_final_results` function imported from \
    `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
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
    print(f"\n    Doctype analysis launched for year {corpus_year}...")

    # Setting useful columns info
    final_cols_tup = set_final_col_names(institute, org_tup)

    # Setting col list of IFs
    return_tup = _set_analysis_if_cols_list(corpus_year, if_most_recent_year)
    analysis_if_col_list, if_analysis_col, if_analysis_year = return_tup

    # Building the dataframe of publications data to be analyzed
    pub_df_dict = build_doctype_analysis_data(bibliometer_path, datatype,
                                              corpus_year, final_cols_tup,
                                              if_col_list=analysis_if_col_list)
    if progress_callback:
        progress_callback(20)

    # Building and saving statistics for each doctype
    return_tup = _build_and_save_doctype_stat(institute, bibliometer_path,
                                               pub_df_dict, corpus_year,
                                               if_analysis_col, final_cols_tup)
    by_journal_dict, doctypes_analysis_folder_path = return_tup

    # Saving stat analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["doctypes"] = True
    if_analysis_name = None
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype,
                           corpus_year, if_analysis_name, results_to_save_dict,
                           verbose=False)
    if progress_callback:
        progress_callback(50)

    final_return_tup = (pub_df_dict, by_journal_dict, if_analysis_col,
                        if_analysis_year, doctypes_analysis_folder_path)
    return final_return_tup
