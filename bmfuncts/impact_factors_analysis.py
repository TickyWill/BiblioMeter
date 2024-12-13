"""Module of functions for publications-list analysis
in terms of impact factors.

"""

__all__ = ['if_analysis']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import numpy as np
import pandas as pd
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_user_config
from bmfuncts.format_files import format_page
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.update_impact_factors import journal_capwords
from bmfuncts.useful_functs import read_parsing_dict


def update_kpi_database(institute, org_tup, bibliometer_path, datatype, corpus_year,
                        kpi_dict, if_key, verbose=False):
    """Updates database of the key performance indicators (KPIs) with values of 'kpi_dict' 
    hierarchical dict for the Institute and each of the its departments with the KPIs data 
    of 'corpus_year' corpus.

    These updated databases are saved as openpyxl workbooks using the `format_page` function \
    imported from the `bmfuncts.format_files` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        kpi_dict (dict): Hierarchical dict keyyed by departments of the Institute \
        including itself and valued with KPIs dict of these keys.
        if_key (str): Column name of the analyzed impact factors (either those of \
        the publication year or the most available ones).
        verbose (bool): Status of prints (default = False).
    Returns:
        (dataframe): Institute KPIs database.
    """

    # Setting aliases for updating KPIs database
    results_root_alias = pg.ARCHI_RESULTS["root"]
    results_folder_alias = pg.ARCHI_RESULTS[datatype]
    results_sub_folder_alias = pg.ARCHI_RESULTS["kpis"]
    kpi_file_base_alias = pg.ARCHI_RESULTS["kpis file name base"]

    # Setting paths for saving results
    results_root_path = bibliometer_path / Path(results_root_alias)
    results_folder_path = results_root_path / Path(results_folder_alias)
    results_kpis_folder_path = results_folder_path / Path(results_sub_folder_alias)

    # Checking availability of required results folder
    if not os.path.exists(results_kpis_folder_path):
        os.makedirs(results_kpis_folder_path)

    # Setting useful column names aliases
    _, depts_col_list = set_final_col_names(institute, org_tup)
    corpus_year_row_alias = pg.KPI_KEYS_ORDER_DICT[0]

    # Initializing return dataframe
    institute_kpi_df = pd.DataFrame()

    # Building as a dataframe the column of KPIs of each 'dept'
    for dept in [institute] + depts_col_list:

        # Building sub dict of KPIs dict for 'dept'
        dept_kpi_dict = dict(kpi_dict[dept].items())

        # Building sub dict of publications KPIs of 'dept' in keys order specified by 'ordered_keys'
        ordered_keys = [v for k, v in pg.KPI_KEYS_ORDER_DICT.items() if k in range(1, 14)]

        dept_pub_dict = {k: dept_kpi_dict[k] for k in ordered_keys}

        # Building 'dept_pub_df' using keys of 'dept_pub_dict' as indexes
        # and setting the name of the values column to 'corpus_year'
        dept_pub_df = pd.DataFrame.from_dict(dept_pub_dict, orient="index",
                                             columns=[corpus_year])

        # Renaming the index column of 'dept_pub_df' as 'corpus_year_row_alias'
        dept_pub_df.reset_index(inplace=True)
        dept_pub_df.rename_axis("idx", axis=1, inplace=True)
        dept_pub_df.rename(columns={"index": corpus_year_row_alias}, inplace=True)

        # Building sub dict of IFs KPIs of 'dept' in keys order specified by 'ordered_keys'
        part_dept_if_dict = dict(dept_kpi_dict[if_key].items())
        dept_if_dict = dict({pg.KPI_KEYS_ORDER_DICT[14]: if_key}, **part_dept_if_dict)

        # Building 'dept_if_df' using keys of 'dept_if_dict' as indexes
        # and setting the name of the values column to 'corpus_year'
        dept_if_df = pd.DataFrame.from_dict(dept_if_dict, orient="index",
                                            columns=[corpus_year])

        # Renaming the index column with 'corpus_year_row_alias'
        dept_if_df.reset_index(inplace=True)
        dept_if_df.rename_axis("idx", axis=1, inplace=True)
        dept_if_df.rename(columns={"index": corpus_year_row_alias}, inplace=True)

        # Combining the two dataframes through rows concatenation
        dept_kpi_df = pd.concat([dept_pub_df, dept_if_df], axis=0)

        # Reading as the dataframe the KPI file of 'dept' if it exists else creating it
        filename = dept + "_" + kpi_file_base_alias + ".xlsx"
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
        kpi_df_title = pg.DF_TITLES_LIST[6]
        wb, ws = format_page(db_dept_kpi_df, kpi_df_title)
        ws.title = dept + ' KPIs '
        wb.save(file_path)

        if dept == institute:
            institute_kpi_df = db_dept_kpi_df.copy()

    message = f"\n    Kpi database updated and saved in folder: \n {file_path}"
    if verbose:
        print(message)

    return institute_kpi_df


# *********************************
# * Basic-KPIs analysis functions *
# *********************************


def _build_analysis_books_kpi(books_df, params_tup):
    """Computes the key performance indicators (KPIs) of books document 
    types for each department of the Institute including itself.

    Args:
        books_df (dataframe): Publications list of books document-type. 
        params_tup (tup): Tuple = (Institute name (str), \
        list of departments (list), column name of journals (str)).
    Returns:
        (dict): Hierarchical dict keyyed by departments and valued \
        at each key by KPIs of the department.
    """

    # Setting useful parameters from args
    institute, depts_col_list, journal_col = params_tup

    # Setting new col names and related parameters
    chapters_nb_col_alias = pg.COL_NAMES_IF_ANALYSIS['articles_nb']

    # Building the books KPIs dict covering all departments
    books_kpi_dict = {}
    for dept in [institute] + depts_col_list:

        # Building the books dataframe for "dept"
        if dept != institute:
            dept_books_df = books_df[books_df[dept] == 1].copy()
        else:
            dept_books_df = books_df.copy()

        # Adding a column with number of articles per journal then droping duplicate rows
        count_books_df = dept_books_df[journal_col].value_counts().to_frame()
        count_books_df.rename(columns={"count": chapters_nb_col_alias}, inplace=True)
        count_books_df.reset_index(inplace=True)
        dept_books_df = dept_books_df.drop_duplicates([journal_col])
        dept_books_df = count_books_df.merge(dept_books_df, how="outer", on=journal_col)

        # Computing KPI for department'dept'
        # Number of items by doctype
        nb_books = round(len(dept_books_df))

        # Number of documents by doctype
        nb_chapters = round(dept_books_df[chapters_nb_col_alias].sum())

        # Ratio of chapters per book
        chapters_per_book = 0
        chapters_per_book_max = 0
        if nb_books:
            chapters_per_book = round(nb_chapters / nb_books, 1)
            chapters_per_book_max = round(dept_books_df[chapters_nb_col_alias].max())

        # Building the dict of books KPIs of department 'dept'
        dept_kpi_dict = {
            pg.KPI_KEYS_ORDER_DICT[2]: nb_books,
            pg.KPI_KEYS_ORDER_DICT[3]: nb_chapters,
            pg.KPI_KEYS_ORDER_DICT[4]: chapters_per_book,
            pg.KPI_KEYS_ORDER_DICT[5]: chapters_per_book_max,
        }

        # Updating KPI dict with KPIs of department 'dept'
        books_kpi_dict[dept] = dept_kpi_dict

    return books_kpi_dict


def _build_basic_kpi_dict(dept_analysis_df, dept_books_kpi_dict, cols_tup):
    """Computes the key performance indicators (KPIs) of all document types 
    for each department of the Institute including itself.

    This is done through the following steps:

    1. Adds a column with number of articles per journal to the \
    'dept_analysis_df' dataframe then drops duplicate rows on journal ISSN values;
    2. Builds the 'dept_articles_df' dataframe by keeping only articles \
    of journal (not proceedings) and drops 'doctype_col' column;
    3. Computes the basic KPIs independent of specific analysis \
    (such as impact factors, coupling anf keywords analysis);
    4. Builds the KPIs dict.

    Args:
        dept_analysis_df (dataframe): 
        dept_books_kpi_dict (dept_books_kpi_dict): KPIs of books document-type. 
        params_tup (tup): (Institute name (str), \
        list of departments (list), column name of journals (str)).
    Returns:
        (tup): (the built articles dataframe for the department, \
        KPIs dict keyyed by KPI_KEYS_ORDER_DICT global -imported from \
        the globals module imported as pg- and valued by KPIs values \
        of the department).
    """

    # Setting useful parameters from args
    doctype_col, issn_col, articles_nb_col = cols_tup

    # Setting useful aliases
    doctype_article_alias = pg.DOC_TYPE_DICT['Articles']

    # Adding a column with number of articles per journal then droping duplicate rows
    count_journal_df = dept_analysis_df[issn_col].value_counts().to_frame()
    count_journal_df.rename(columns={'count': articles_nb_col}, inplace=True)
    count_journal_df.reset_index(inplace=True)
    dept_analysis_df = dept_analysis_df.drop_duplicates([issn_col])
    dept_analysis_df = count_journal_df.merge(dept_analysis_df, how="outer",
                                              on=issn_col)

    # Keeping only articles of journal (not proceedings)
    # and dropping 'doctype_col' column
    inter_df = dept_analysis_df[dept_analysis_df[doctype_col].isin(doctype_article_alias)]
    dept_articles_df = inter_df
    dept_articles_df = dept_articles_df.drop(columns=[doctype_col])

    # Computing KPIs independent of IF

    # * Total number of publications
    nb_chapters = dept_books_kpi_dict[pg.KPI_KEYS_ORDER_DICT[3]]
    nb_articles_communications = round(dept_analysis_df[articles_nb_col].sum())
    nb_publications = round(nb_chapters + nb_articles_communications)

    # * Number of items by doctype
    nb_journals_proceedings = round(len(dept_analysis_df))
    nb_journals = round(len(dept_articles_df))

    # * Number of documents by doctype
    nb_articles = round(dept_articles_df[articles_nb_col].sum())
    nb_communications = round(nb_articles_communications - nb_articles)
    communications_ratio = 0
    if nb_articles_communications:
        communications_ratio = round(nb_communications / nb_articles_communications * 100)

    # * Ratio of articles per journal
    articles_per_journal = 0
    articles_per_journal_max = 0
    if nb_journals:
        articles_per_journal = round(nb_articles / nb_journals, 1)
        articles_per_journal_max = round(dept_articles_df[articles_nb_col].max())

    # Completing the KPIs dict with IF independent KPIs
    dept_kpi_dict = dict(dept_books_kpi_dict.items())
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[1]] = nb_publications
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[6]] = nb_journals_proceedings
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[7]] = nb_journals
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[8]] = nb_articles_communications
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[9]] = nb_communications
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[10]] = communications_ratio
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[11]] = nb_articles
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[12]] = articles_per_journal
    dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[13]] = articles_per_journal_max

    return dept_articles_df, dept_kpi_dict


# ***********************************
# * IFs analysis specific functions *
# ***********************************


def _build_analysis_if_data(institute, org_tup, analysis_df,
                            if_analysis_col, if_analysis_year,
                            if_analysis_folder_path, books_list_file_path,
                            verbose=False):
    """Builds the data of each department of the Institute including itself 
    for impact-factors (IFs) analysis.

    This is done through the following steps:

    1. Builds the 'dept_analysis_df' dataframe of publications list of the department \
    selected from the 'analysis_df' dataframe.
    2. Initializes the 'dept_kpi_dict' dict with the basic key performance indicators (KPIs) \
    of the department using the 'dept_analysis_df' through the `_build_basic_kpi_dict` internal \
    function which returns also 'dept_articles_df' dataframe with only articles as document types.
    3. Builds the 'dept_if_df' dataframe from 'dept_articles_df' dataframe selecting \
    useful columns for IF-KPIs computation and cleans it.
    4. Computes the IF-KPIs of the department using the data of the 'dept_if_df' dataframe.
    5. Builds the 'dept_if_kpi_dict' dict using the IF_KPIs computed.
    6. Sets the value of the 'dept_kpi_dict' dict at key given by 'if_analysis_col_new' \
    aqual to 'dept_if_kpi_dict' dict; by that the 'dept_kpi_dict' dict becomes a hierarchical dict.  
    7. Sets the value of the 'kpi_dict' hierarchical dict at key 'dept' (name of the department) \
    equal to the 'dept_kpi_dict' hierarchical dict.
    8. Saves the 'dept_if_df' dataframe as openpyxl workbook using the `format_page` function \
    imported from the `bmfuncts.format_files` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        analysis_df (dataframe): Publications list to be analyzed.
        if_analysis_col (str): Column name of the IFs values to be used for \
        the analysis in the 'analysis_df' dataframe.
        if_analysis_year (str): 4 digits year of the IFs values used for the analysis.
        if_analysis_folder_path (path): Full path to the folder for saving results.
        books_list_file_path (path): Full path to the file of book list to be analyzed.
        kpi_dict (dict): Dict keyyed by departments of the Institute including itself \
        and valued with KPIs of the 'corpus_year' corpus.
        if_key (str): Column name of the analyzed impact factors (either those of \
        the publication year or the most available ones).
        verbose (bool): Status of prints (default = False).
    Returns:
        (tup): (hierarchical dict keyyed by departments of the Institute including \
        itself and valued with KPIs dict of each department, key of IF-KPIs in the \
        hierarchical dict of each department and also column name of IFs values in the saved files).
    """

    # Setting useful column names aliases
    final_col_dic, depts_col_list = set_final_col_names(institute, org_tup)
    journal_col_alias = final_col_dic['journal']
    doctype_col_alias = final_col_dic['doc_type']
    issn_col_alias = final_col_dic['issn']
    articles_nb_col_alias = pg.COL_NAMES_IF_ANALYSIS['articles_nb']

    # Setting useful tuple args
    params_tup = (institute, depts_col_list, journal_col_alias)
    cols_tup = (doctype_col_alias, issn_col_alias, articles_nb_col_alias)

    # Building the dataframe of the books list
    usecols = [journal_col_alias, doctype_col_alias] + depts_col_list
    books_df = pd.read_excel(books_list_file_path,
                             usecols=usecols)

    # Building KPIs dict for book doctypes
    books_kpi_dict = _build_analysis_books_kpi(books_df, params_tup)

    # Building the full KPIs dict covering all departments
    kpi_dict = {}
    for dept in [institute] + depts_col_list:

        # Building the IFs analysis dataframe for "dept"
        if dept != institute:
            dept_analysis_df = analysis_df[analysis_df[dept] == 1].copy()
        else:
            dept_analysis_df = analysis_df.copy()
        dept_analysis_df.drop(columns=depts_col_list, inplace=True)

        # Computing basic KPIs of department 'dept'
        dept_articles_df, dept_kpi_dict = _build_basic_kpi_dict(dept_analysis_df,
                                                                books_kpi_dict[dept],
                                                                cols_tup)

        # Building the 'dept_if_df' dataframe for computing IF KPIs
        # * Selecting useful columns from 'dept_articles_df' dataframe
        dept_if_df = dept_articles_df[[journal_col_alias, articles_nb_col_alias, if_analysis_col]]

        # * Cleaning the 'dept_if_df' dataframe
        dept_if_df = dept_if_df.sort_values(by=[if_analysis_col, journal_col_alias],
                                            ascending=True)
        if_analysis_col_new = "IF " + if_analysis_year
        dept_if_df.rename(columns={if_analysis_col: if_analysis_col_new}, inplace=True)
        dept_if_df = dept_if_df.reset_index().drop(columns=["index"])

        # Computing IF KPIs values
        nb_articles = dept_kpi_dict[pg.KPI_KEYS_ORDER_DICT[11]]
        if_moyen = 0
        if nb_articles:
            if_moyen = sum(x[0]*x[1] for x in zip(dept_if_df[if_analysis_col_new],
                                                  dept_if_df[articles_nb_col_alias]))/nb_articles
        if_max = np.max(dept_if_df[if_analysis_col_new])
        if_min = np.min(dept_if_df[if_analysis_col_new])
        dept_if_sub_df = dept_if_df[dept_if_df[if_analysis_col_new] == 0]
        nb_art_wo_if = dept_if_sub_df[articles_nb_col_alias].sum()
        wo_if_ratio = 0
        if nb_articles:
            wo_if_ratio = nb_art_wo_if / nb_articles * 100

        # Completing the KPIs dict with IF KPIs values
        dept_if_kpi_dict = {
            pg.KPI_KEYS_ORDER_DICT[15]: round(if_max, 1),
            pg.KPI_KEYS_ORDER_DICT[16]: round(if_min, 1),
            pg.KPI_KEYS_ORDER_DICT[17]: round(if_moyen, 1),
            pg.KPI_KEYS_ORDER_DICT[18]: round(nb_art_wo_if),
            pg.KPI_KEYS_ORDER_DICT[19]: round(wo_if_ratio)
        }
        dept_kpi_dict[if_analysis_col_new] = dept_if_kpi_dict

        # Updating KPI dict with KPIs of department 'dept'
        kpi_dict[dept] = dept_kpi_dict

        # Saving after formatting the updated dataframe as EXCEL file
        file_name = f'{if_analysis_col_new}-{dept}'
        dept_xlsx_file_path = Path(if_analysis_folder_path) / Path(file_name + '.xlsx')
        if_anal_df_title = pg.DF_TITLES_LIST[10]
        wb, ws = format_page(dept_if_df, if_anal_df_title)
        ws.title = dept + ' IFs '
        wb.save(dept_xlsx_file_path)

        message = (
            f"\n    EXCEL file of {if_analysis_col_new} for {dept} department "
            f"saved in : \n {if_analysis_folder_path}"
        )
        if verbose:
            print(message, "\n")

    return kpi_dict, if_analysis_col_new


def if_analysis(institute, org_tup, bibliometer_path, datatype,
                corpus_year, if_most_recent_year,
                progress_callback=None, verbose=False):
    """ Performs the analysis of journal impact_factors (IFs) of the 'corpus_year' corpus.

    This is done through the following steps:

    1. Gets deduplication results of the parsing step trough the `read_parsing_dict` \
    function imported from `bmfuncts.useful_functs` module.
    2. Builds the dataframe of publications list to be analyzed using \
    normalized journal names available in the deduplicated list of publications \
    resulting from the parsing step. 
    3. Builds the IFs data resulting from IFs analysis of this dataframe \
     through the `_build_analysis_if_data` internal function and saves them as xlsx files.
    4. Updates database of key performance indicators (KPIs) of the Institute \
    with the results of this analysis through the `update_kpi_database` function.
    5. Saves the results of this analysis for the 'datatype' case through the \
    `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        if_most_recent_year (str): Most recent year of impact factors.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).
    Returns:
        (tup): (full path to the folder where results of impact-factors \
        analysis are saved, dataframe of Institute KPIs database, dict of Institute KPIs).
    """

    # internal functions
    def _unique_journal_name(init_analysis_df):
        """Sets a unique journal name by ISSN value.
        """
        analysis_df = pd.DataFrame(columns=init_analysis_df.columns)
        for _, df in init_analysis_df.groupby(by=[issn_col_alias]):
            issn_df = df.copy()
            issn = issn_df[issn_col_alias].to_list()[0]
            journal_names_list = issn_df[journal_col_alias].to_list()
            if len(journal_names_list) > 1:
                if issn != unknown_alias:
                    journal_length_list = [len(journal) for journal in journal_names_list]
                    journal_names_dict = dict(zip(journal_length_list, journal_names_list))
                    length_min = min(journal_length_list)
                    issn_df[journal_col_alias] = journal_names_dict[length_min]
                else:
                    journal_names_list = list(set(issn_df[journal_col_alias].to_list()))
                    journal_issn_list = [issn + str(num) for num in range(len(journal_names_list))]
                    journal_names_dict = dict(zip(journal_names_list, journal_issn_list))
                    issn_df[issn_col_alias] = issn_df[journal_col_alias].copy()
                    issn_df[issn_col_alias] = issn_df[issn_col_alias].map(journal_names_dict)
            analysis_df = pd.concat([analysis_df, issn_df], ignore_index=True)
        return analysis_df

    def _capwords_journal_col(journal_col):
        return lambda row: journal_capwords(row[journal_col])

    def _replace_no_if(no_if1, no_if2):
        return lambda x: x if x not in (no_if1, no_if2) else 0

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN
    articles_item_alias = bp.PARSING_ITEMS_LIST[0]
    pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    if_analysis_folder_alias = pg.ARCHI_YEAR["if analysis"]
    pub_list_filename_base = pg.ARCHI_YEAR["pub list file name base"]
    papers_doctype_alias = list(pg.DOCTYPE_TO_SAVE_DICT.keys())[0]
    books_doctype_alias = list(pg.DOCTYPE_TO_SAVE_DICT.keys())[1]

    # Setting useful xlsx file names for results saving
    year_pub_list_filename = pub_list_filename_base + " " + corpus_year
    papers_list_filename = year_pub_list_filename + "_" + papers_doctype_alias + ".xlsx"
    books_list_filename = year_pub_list_filename + "_" + books_doctype_alias + ".xlsx"

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(corpus_year)
    pub_list_folder_path = year_folder_path / Path(pub_list_folder_alias)
    papers_list_file_path = pub_list_folder_path / Path(papers_list_filename)
    books_list_file_path = pub_list_folder_path / Path(books_list_filename)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    if_analysis_folder_path = analysis_folder_path / Path(if_analysis_folder_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(if_analysis_folder_path):
        os.makedirs(if_analysis_folder_path)
    if progress_callback:
        progress_callback(10)

    # Setting useful column names aliases
    final_col_dic, depts_col_list = set_final_col_names(institute, org_tup)
    journal_col_alias = final_col_dic['journal']
    doctype_col_alias = final_col_dic['doc_type']
    issn_col_alias = final_col_dic['issn']
    journal_norm_col_alias = bp.COL_NAMES['temp_col'][1]
    most_recent_year_if_col_base_alias = pg.COL_NAMES_BONUS["IF en cours"]
    corpus_year_if_col = pg.COL_NAMES_BONUS['IF année publi']
    most_recent_year_if_col_alias = most_recent_year_if_col_base_alias + \
                                    ", " + if_most_recent_year
    if progress_callback:
        progress_callback(15)

    # Building the dataframe of publications list to be analyzed

    # * Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, corpus_year, pg.BDD_LIST)
    parsing_path_dict, item_filename_dict = config_tup[1], config_tup[2]

    # * Setting parsing files extension of saved results
    parsing_save_extent = pg.TSV_SAVE_EXTENT

    # * Setting path of deduplicated parsings
    dedup_parsing_path = parsing_path_dict['dedup']

    # * Getting the dict of deduplication results
    dedup_parsing_dict = read_parsing_dict(dedup_parsing_path, item_filename_dict,
                                           parsing_save_extent)
    if progress_callback:
        progress_callback(30)

    # * Building the dict {journal name : normalized journal name,}
    articles_df = dedup_parsing_dict[articles_item_alias]
    journal_norm_dict = dict(zip(articles_df[journal_col_alias],
                                 articles_df[journal_norm_col_alias]))
    if progress_callback:
        progress_callback(50)

    # * Setting the IF columns dict
    if_col_dict = {most_recent_year_if_col_alias: if_most_recent_year,
                   corpus_year_if_col: corpus_year}

    # * Setting the IF analysis year and column
    if if_most_recent_year >= corpus_year:
        if_analysis_col = pg.ANALYSIS_IF
        if_analysis_year = if_col_dict[pg.ANALYSIS_IF]
    else:
        if_analysis_col = most_recent_year_if_col_alias
        if_analysis_year = if_most_recent_year

    # * Initializing the dataframe to be analysed
    if_col_list = list(if_col_dict.keys())
    usecols = [journal_col_alias, doctype_col_alias, issn_col_alias] + \
              depts_col_list + if_col_list
    init_analysis_df = pd.read_excel(papers_list_file_path,
                                     usecols=usecols)
    if progress_callback:
        progress_callback(55)

    # * Setting final dataframe to be analyzed
    analysis_df = _unique_journal_name(init_analysis_df)
    analysis_df[journal_norm_col_alias] = analysis_df[journal_col_alias]
    analysis_df[journal_norm_col_alias] = analysis_df[journal_norm_col_alias].map(journal_norm_dict)
    analysis_df[journal_col_alias] = analysis_df. \
        apply(_capwords_journal_col(journal_col_alias), axis=1)
    for if_col, _ in if_col_dict.items():
        analysis_df[if_col] = analysis_df[if_col]. \
            apply(_replace_no_if(unknown_alias, pg.NOT_AVAILABLE_IF))
    if progress_callback:
        progress_callback(60)

    # Building the data resulting from IFs analysis of the final dataframe
    # and saving them as xlsx files
    kpi_dict, if_analysis_col_new = _build_analysis_if_data(institute, org_tup,
                                                            analysis_df, if_analysis_col,
                                                            if_analysis_year,
                                                            if_analysis_folder_path,
                                                            books_list_file_path,
                                                            verbose=verbose)
    if progress_callback:
        progress_callback(75)

    # Updating the KPIs database
    institute_kpi_df = update_kpi_database(institute, org_tup, bibliometer_path,
                                           datatype, corpus_year, kpi_dict,
                                           if_analysis_col_new, verbose=verbose)
    if progress_callback:
        progress_callback(90)

    # Saving IFs analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["ifs"] = True
    if_analysis_name = if_analysis_col_new
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype, corpus_year,
                           if_analysis_name, results_to_save_dict, verbose=False)
    if progress_callback:
        progress_callback(100)

    return if_analysis_folder_path, institute_kpi_df, kpi_dict
