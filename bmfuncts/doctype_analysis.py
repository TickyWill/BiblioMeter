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
    """Reads saved articles data resulting from the parsing step.

    It uses the `get_final_dedup` function of 
    the `bmfuncts.useful_functs` module.

    Args:
        bibliometer_path (path): Full path to working folder.
        saved_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (dataframe): The dataframe of the authors data.
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


def build_doctype_analysis_data(institute, org_tup, bibliometer_path, datatype, corpus_year,
                                final_cols_tup, if_col_list=None):
    """To update: Builds the dataframe of publications list to be analyzed.

    This is done through the following steps:

    1. Gets deduplication results of the parsing step trough the `read_parsing_dict` \
    function imported from `bmfuncts.useful_functs` module.
    2. Builds the dataframe of publications list to be analyzed using \
    normalized journal names available in the deduplicated list of publications \
    resulting from the parsing step.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        final_cols_tup (tup) : (final columns names dict, departments columns list) .
        if_col_list (list): Optional list of column names of impact-factors.
    Returns:
        (dataframe): 
    """
    # Building pub_df_dict dict
    # keyyed by doctypes: ['articles', 'proceedings', 'books']
    # valued by a dataframe for each doctype
    #    colunms: ['Journal', 'Type du document', 'ISSN', 'DACLE', 'DCOS', 'DOPT', 'DPFT',
    #              'DSYS', 'DTIS', 'DEXT', 'DIR', 'IF en cours, 2023',
    #              "IF de l'année de première publication", 'Dedup_Same_Journal']
    #    pub_df_dict['articles'] = articles_df
    #    pub_df_dict['proceedings'] = proceedings_df
    #    pub_df_dict['books'] = books_df
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

    # Getting articles data reuslting from deduplication parsing
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
    pub_df_dict = {}
    pub_df_dict['articles'] = articles_df
    pub_df_dict['proceedings'] = proceedings_df
    pub_df_dict['books'] = books_df
    return pub_df_dict


def _set_by_issn_df(by_doc_df, idx_doc, issn, dg, drop_dup_cols,
                    journal_col, norm_doc):
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
    if dept!=institute:
        dept_df = df[df[dept]==1].copy()
    else:
        dept_df = df.copy()
    return dept_df


def _build_and_save_doctype_stat(institute, bibliometer_path, pub_df_dict,
                                 corpus_year, if_analysis_col, final_cols_tup):
    """Builds the publications statistics dataframes per country and per continent.
    
    First, it builds the statistics dataframes through the `_build_countries_stat` 
    and the `_build_continents_stat` internal functions.
    Then, it saves the statistics dataframes through the `save_formatted_df_to_xlsx` 
    function imported from `bmfuncts.format_files` module.
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
    return by_journal_dict


def _set_analysis_if_cols_list(corpus_year, if_most_recent_year):
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
                     corpus_year, if_most_recent_year, progress_callback=None):
    """ 
    """
    # Setting useful columns info
    final_cols_tup = set_final_col_names(institute, org_tup)

    # Setting col list of IFs
    return_tup = _set_analysis_if_cols_list(corpus_year, if_most_recent_year)
    analysis_if_col_list, if_analysis_col, if_analysis_year = return_tup

    # Building the dataframe of publications data to be analyzed
    pub_df_dict = build_doctype_analysis_data(institute, org_tup, bibliometer_path,
                                              datatype, corpus_year, final_cols_tup,
                                              if_col_list=analysis_if_col_list)
    if progress_callback:
        progress_callback(20)

    # Building and saving statistics for each doctype    
    by_journal_dict = _build_and_save_doctype_stat(institute, bibliometer_path,
                                                   pub_df_dict, corpus_year,
                                                   if_analysis_col, final_cols_tup)

    # Saving stat analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["doctypes"] = True
    if_analysis_name = None
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype, corpus_year,
                           if_analysis_name, results_to_save_dict, verbose=False)
    if progress_callback:
        progress_callback(50)
    return pub_df_dict, by_journal_dict, if_analysis_col, if_analysis_year
