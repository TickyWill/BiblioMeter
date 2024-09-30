"""Module of functions for publications-list analysis
in terms of impact factors, key words and collaborations."""

__all__ = ['if_analysis',
           'keywords_analysis',
           'coupling_analysis']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import numpy as np
import pandas as pd

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_user_config
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.update_impact_factors import journal_capwords
from bmfuncts.useful_functs import format_df_for_excel
from bmfuncts.useful_functs import read_parsing_dict


def _update_kpi_database(institute, org_tup, bibliometer_path, datatype, corpus_year,
                         kpi_dict, if_key, verbose=False):
    """Updates database of the key performance indicators (KPIs) with values of 'kpi_dict' 
    hierarchical dict for the Institute and each of the its departments with the KPIs data 
    of 'corpus_year' corpus.
    Then, these updated databases are saved as Excel workbooks using the `format_df_for_excel` 
    function imported from the `bmfuncts.useful_functs` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        kpi_dict (dict): Hierarchical dict keyyed by departments of the Institute 
                         including itself and valued with KPIs dict of these keys.
        if_key (str): Column name of the analyzed impact factors (either those of 
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
        first_col_width = 35
        wb, ws = format_df_for_excel(db_dept_kpi_df, first_col_width)
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
        params_tup (tup): Tuple = (Institute name (str), 
                          list of departments (list), 
                          column name of journals (str)).

    Returns:
        (dict): Hierarchical dict keyyed by departments and valued 
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
    To do that:
        - First, adds a column with number of articles per journal to the 
        'dept_analysis_df' dataframe then drops duplicate rows on journal ISSN values; 
        - Then, builds the 'dept_articles_df' dataframe by keeping only articles 
        of journal (not proceedings) and drops 'doctype_col' column; 
        - Then, computes the basic KPIs independent of specific analysis 
        (such as impact factors, coupling anf keywords analysis);
        - Finally, builds the KPIs dict.

    Args:
        dept_analysis_df (dataframe): 
        dept_books_kpi_dict (dept_books_kpi_dict): KPIs of books document-type. 
        params_tup (tup): Tuple = (Institute name (str), 
                          list of departments (list), 
                          column name of journals (str)).

    Returns:
        (tup): Tuple = (the built articles dataframe for the department, 
               KPIs dict keyyed by KPI_KEYS_ORDER_DICT global -imported from 
               the globals module imported as pg- and valued by KPIs values 
               of the department.
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
    To do that:
        - First, builds the 'dept_analysis_df' dataframe of publications list of the department 
        selected from the 'analysis_df' dataframe.
  
        - Then, initializes the 'dept_kpi_dict' dict with the basic key performance indicators (KPIs) 
        of the department using the 'dept_analysis_df' through the `_build_basic_kpi_dict` 
        internal function which returns also 'dept_articles_df' dataframe with only articles 
        as document types.
  
        - Then, builds the 'dept_if_df' dataframe from 'dept_articles_df' dataframe selecting 
        useful columns for IF-KPIs computation and cleans it.
  
        - Then, computes the IF-KPIs of the department using the data of the 'dept_if_df' dataframe.
  
        - Then, builds the 'dept_if_kpi_dict' dict using the IF_KPIs computed.
  
        _ Then, sets the value of the 'dept_kpi_dict' dict at key given by 'if_analysis_col_new' 
        aqual to 'dept_if_kpi_dict' dict; by that the 'dept_kpi_dict' dict becomes a hierarchical dict.
  
        - Then, sets the value of the 'kpi_dict' hierarchical dict at key 'dept' (name of the department) 
        equal to the 'dept_kpi_dict' hierarchical dict.
  
        - Finally, saves the 'dept_if_df' dataframe as Excel workbook using the `format_df_for_excel` 
        function imported from the `bmfuncts.useful_functs` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        analysis_df (dataframe): Publications list to be analyzed.
        if_analysis_col (str): Column name of the IFs values to be used for 
                               the analysis in the 'analysis_df' dataframe.
        if_analysis_year (str): 4 digits year of the IFs values used for the analysis.
        if_analysis_folder_path (path): Full path to the folder for saving results.
        books_list_file_path (path): Full path to the file of book list to be analyzed.
        kpi_dict (dict): Dict keyyed by departments of the Institute including itself 
                         and valued with KPIs of the 'corpus_year' corpus.
        if_key (str): Column name of the analyzed impact factors (either those of 
                      the publication year or the most available ones).
        verbose (bool): Status of prints (default = False).

    Returns:
        (tup): Tuple = (hierarchical dict keyyed by departments of the Institute including itself 
               and valued with KPIs dict of each department, 
               key of IF-KPIs in the hierarchical dict of each department 
               and also column name of IFs values in the saved files).
    """

    # Setting useful aliases
    doctype_article_alias = pg.DOC_TYPE_DICT['Articles']

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
        first_col_width = 50
        wb, ws = format_df_for_excel(dept_if_df, first_col_width)
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
    To do that:
        - First, gets deduplication results of the parsing step trough the `read_parsing_dict` 
        function imported from `bmfuncts.useful_functs` module.

        - Then, builds the dataframe of publications list to be analyzed using 
        normalized journal names available in the deduplicated list of publications 
        resulting from the parsing step.
 
        - Then, builds the IFs data resulting from IFs analysis of this dataframe 
         through the `_build_analysis_if_data` internal function and saves them as xlsx files.
  
        - Then, updates database of key performance indicators (KPIs) of the Institute 
        with the results of this analysis through the `_update_kpi_database` internal function.
  
        - Finally, saves the results of this analysis for the 'datatype' case through the 
        `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): 4 digits year of the corpus.
        if_most_recent_year (str): Most recent year of impact factors.
        progress_callback (function): Function for updating ProgressBar 
                                      tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).

    Returns:
        (tup): Tuple = (full path to the folder where results 
                        of impact-factors analysis are saved, 
                        dataframe of Institute KPIs database,
                        dict of Institute KPIs).
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

    # Building the data resulting from IFs analysis of the final dataframe and saving them as xlsx files
    kpi_dict, if_analysis_col_new = _build_analysis_if_data(institute, org_tup,
                                                            analysis_df, if_analysis_col,
                                                            if_analysis_year,
                                                            if_analysis_folder_path,
                                                            books_list_file_path,
                                                            verbose=verbose)
    if progress_callback:
        progress_callback(75)

    # Updating the KPIs database
    institute_kpi_df = _update_kpi_database(institute, org_tup, bibliometer_path,
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


# ****************************************
# * Keywords analysis specific functions *
# ****************************************


def _create_kw_analysis_data(institute, year, analysis_df, kw_type, kw_df, cols_tup,
                             kw_analysis_folder_path, verbose=False):
    """Creates publications-keywords (KW) data for the 'kw_type' KW type 
    for each department of the Institute including itself. 
    To do that:
        - First, builds the list of publication IDs of the department 
        extracted from the 'analysis_df' dataframe;
        - Then, builds the list of KWs for the 'kw_type' KW type extracted 
        from the 'kw_df' dataframe using the built list of publication IDs 
        of the department;
        - Then, builds the 'dept_kw_df' dataframe by computing the number 
        of occurences of each KW in the built list of KWs;
        - Finally, saves the 'dept_kw_df' dataframe as Excel workbook using the 
        `format_df_for_excel` function imported from the `bmfuncts.useful_functs` 
        module.

    Args:
        institute (str): Institute name.
        year (str): 4 digits year of the corpus.
        analysis_df (dataframe): Publications list to be analyzed.
        kw_type (str): Type of keyword to be analyzed.
        kw_df (dataframe): Keywords list of 'kw_type' type to be analyzed.
        cols_tup (tup): Tuple = (list of column name for each department of the Institute, 
                                 publication-IDs column name in 'analysis_df' dataframe, 
                                 publication-IDs column name in 'kw_df' dataframe, 
                                 keywords column name, keyword-weight column name).
        kw_analysis_folder_path (path): Full path to the folder for saving results.
        verbose (bool): Status of prints (default = False).

    Returns:
        None.
    """

    # Setting useful column names aliases
    depts_col_list, final_pub_id_col, parsing_pub_id_col, keywords_col, weight_col = cols_tup

    # Analyzing the keywords for each of the department in 'depts_col_list'
    for dept in [institute] + depts_col_list:
        # Collecting and normalizing all the Pub_ids of the department 'dept'
        # by removing the 4 first characters corresponding to the corpus "year"
        # in order to make them comparable to 'parsing_pub_id_col' values
        if dept != institute:
            raw_pub_id_list = analysis_df[analysis_df[dept] == 1][final_pub_id_col].tolist()
            dept_pub_id_list = [int(x[5:8]) for x in raw_pub_id_list]
        else:
            dept_pub_id_list = [int(x[5:8]) for x in analysis_df[final_pub_id_col].tolist()]

        # Building the list of keywords for the keywords type 'kw_type' and the department 'dept'
        dept_kw_list = []
        for _, row in kw_df.iterrows():
            pub_id = row[parsing_pub_id_col]
            keyword = row[keywords_col]
            if pub_id in dept_pub_id_list:
                pub_kw_list = [word.strip() for word in keyword.split(";")]
                dept_kw_list = dept_kw_list + pub_kw_list

        # Building a dataframe with the keywords and their weight for the keywords type 'kw_type'
        # and the department 'dept'
        dept_kw_df = pd.DataFrame(columns=[keywords_col, weight_col])
        dept_kw_set_to_list = sorted(list(set(dept_kw_list)))
        kw_drop = 0
        for idx, keyword in enumerate(dept_kw_set_to_list):
            if len(keyword) > 1:
                dept_kw_df.loc[idx, keywords_col] = keyword
                dept_kw_df.loc[idx, weight_col] = dept_kw_list.count(keyword)
            else:
                kw_drop += 1
        if kw_drop and dept == institute:
            print(f"    WARNING: {kw_drop} dropped keywords of 1 character "
                  f"among {len(dept_kw_set_to_list)} {kw_type} ones of {institute}")

        # Saving the keywords dataframe as EXCEL file
        dept_xlsx_file_path = Path(kw_analysis_folder_path) / Path(f'{dept} {year}-{kw_type}.xlsx')
        first_col_width = 50
        wb, ws = format_df_for_excel(dept_kw_df, first_col_width)
        ws.title = dept + ' ' + kw_type
        wb.save(dept_xlsx_file_path)

    message = ("\n    Keywords of all types and all departments "
               f"saved in : \n {kw_analysis_folder_path}")
    if verbose:
        print(message, "\n")


def keywords_analysis(institute, org_tup, bibliometer_path, datatype,
                      year, progress_callback=None, verbose=False):
    """ Performs the analysis of publications keywords (KWs) of the 'year' corpus. 
    To do that:
        - First, gets deduplication results of the parsing step trough the 
        `read_parsing_dict` function imported from `bmfuncts.useful_functs` module.
        - Then, builds the dataframe of publications list to be analyzed specifying 
        the useful columns;
        - Then, loops on KW type among author KW (AK), indexed KW (IK) and title KW (TK) for:
            - building the dataframe of KW list to be analyzed given by the deduplication 
            results of the parsing step;
            - creating KW analysis data through the `_create_kw_analysis_data` internal function;
        - Finally, saves the results of this analysis for the 'datatype' case through the 
        `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year (str): 4 digits year of the corpus.
        progress_callback (function): Function for updating ProgressBar 
                                      tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).

    Returns:
        (path): Full path to the folder where results of keywords analysis are saved.
    """

    # Setting useful aliases
    auth_kw_item_alias = bp.PARSING_ITEMS_LIST[6]
    index_kw_item_alias = bp.PARSING_ITEMS_LIST[7]
    title_kw_item_alias = bp.PARSING_ITEMS_LIST[8]
    pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    kw_analysis_folder_alias = pg.ARCHI_YEAR["keywords analysis"]
    pub_list_filename_base = pg.ARCHI_YEAR["pub list file name base"]
    doctype_alias = list(pg.DOCTYPE_TO_SAVE_DICT.keys())[0]

    # Setting useful file names
    pub_list_filename = pub_list_filename_base + " " + str(year) + "_" + doctype_alias + ".xlsx"

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(str(year))
    pub_list_folder_path = year_folder_path / Path(pub_list_folder_alias)
    pub_list_file_path = pub_list_folder_path / Path(pub_list_filename)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    kw_analysis_folder_path = analysis_folder_path / Path(kw_analysis_folder_alias)
    if progress_callback:
        progress_callback(5)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(kw_analysis_folder_path):
        os.makedirs(kw_analysis_folder_path)
    if progress_callback:
        progress_callback(10)

    # Setting useful column names aliases
    final_col_dic, depts_col_list = set_final_col_names(institute, org_tup)
    final_pub_id_col_alias = final_col_dic['pub_id']
    parsing_pub_id_col_alias = bp.COL_NAMES['pub_id']
    keywords_col_alias = bp.COL_NAMES['keywords'][1]
    weight_col_alias = pg.COL_NAMES_BONUS['weight']
    if progress_callback:
        progress_callback(15)

    # Getting the full paths of the working folder architecture for the corpus "year"
    config_tup = set_user_config(bibliometer_path, year, pg.BDD_LIST)
    parsing_path_dict, item_filename_dict = config_tup[1], config_tup[2]

    # Setting parsing files extension of saved results
    parsing_save_extent = pg.TSV_SAVE_EXTENT
    if progress_callback:
        progress_callback(20)

    # Setting path of deduplicated parsings
    dedup_parsing_path = parsing_path_dict['dedup']

    # Getting the dict of deduplication results
    dedup_parsing_dict = read_parsing_dict(dedup_parsing_path, item_filename_dict,
                                           parsing_save_extent)
    if progress_callback:
        progress_callback(25)

    # Setting useful filenames dict
    kw_item_alias_dict = {'AK': auth_kw_item_alias,
                          'IK': index_kw_item_alias,
                          'TK': title_kw_item_alias,
                          }
    if progress_callback:
        progress_callback(25)

    # Building the dataframe to be analysed from the file which full path is 'pub_list_file_path'
    analysis_df = pd.read_excel(pub_list_file_path,
                                usecols=[final_pub_id_col_alias] + depts_col_list)
    if progress_callback:
        progress_callback(30)

    # Plotting the words-cloud of the different kinds of keywords
    if progress_callback:
        progress_bar_state = 30
        progress_bar_loop_progression = 50 // len(kw_item_alias_dict.keys())
    for kw_type, kw_item_alias in kw_item_alias_dict.items():
        # Building the keywords dataframe for the keywords type 'kw_type'
        # from 'dedup_parsing_dict' dict at 'kw_item_alias' key
        kw_df = dedup_parsing_dict[kw_item_alias]
        kw_df[keywords_col_alias] = kw_df[keywords_col_alias]. \
            apply(lambda x: x.replace(' ', '_').replace('-', '_'))
        kw_df[keywords_col_alias] = kw_df[keywords_col_alias]. \
            apply(lambda x: x.replace('_(', ';').replace(')', ''))
        kw_df[keywords_col_alias] = kw_df[keywords_col_alias].apply(lambda x: x.lower())

        # Creating keywords-analysis data and saving them as xlsx files
        cols_tup = (depts_col_list, final_pub_id_col_alias, parsing_pub_id_col_alias,
                    keywords_col_alias, weight_col_alias)
        _create_kw_analysis_data(institute, year, analysis_df, kw_type, kw_df, cols_tup,
                                 kw_analysis_folder_path, verbose=verbose)

        # Updating progress bar state
        if progress_callback:
            progress_bar_state += progress_bar_loop_progression
            progress_callback(progress_bar_state)

    # Saving keywords analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["kws"] = True
    if_analysis_name = None
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype, year,
                           if_analysis_name, results_to_save_dict, verbose=False)
    if progress_callback:
        progress_callback(100)
    return kw_analysis_folder_path


# ****************************************
# * Coupling analysis specific functions *
# ****************************************


def _build_countries_stat(countries_df):
    """Builds the statistics of publications per country from the analysis 
    of the dataframe of countries where each row contains:
        - a publication IDs; 
        - the index of an address of the publication addresses; 
        - the country of the given address.

    Args:
        countries_df (dataframe): Data of countries per publications.

    Returns:
        (dataframe): Countries statistics where each row gives the country name, 
                     the Institute-publications number with address from the country 
                     and a string listing the concerned publications IDs separated by semicolon.
    """

    # Setting useful local aliases
    pub_id_alias = bp.COL_NAMES['pub_id']  # "Pub_id"
    country_alias = bp.COL_NAMES['country'][2]  # "Country"
    final_country_alias = pg.COL_NAMES_BONUS['country']  # "Pays"
    weight_alias = pg.COL_NAMES_BONUS['pub number']  # "Nombre de publications"
    pub_ids_alias = pg.COL_NAMES_BONUS["pub_ids list"]  # "Liste des Pub_ids"

    by_country_df = pd.DataFrame(columns=[final_country_alias, weight_alias, pub_ids_alias])
    idx_country = 0
    for country, pub_id_dg in countries_df.groupby(country_alias):
        pub_id_dg = pub_id_dg.drop_duplicates([pub_id_alias, country_alias])
        pub_ids_list = pub_id_dg[pub_id_alias].tolist()
        pub_ids_nb = len(pub_ids_list)
        by_country_df.loc[idx_country, final_country_alias] = country
        by_country_df.loc[idx_country, weight_alias] = pub_ids_nb
        if country != "France":
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_country_df.loc[idx_country, pub_ids_alias] = pud_ids_txt
        idx_country += 1

    return by_country_df


def _build_continents_stat(countries_df):
    """Builds the statistics of publications per continents from the analysis 
    of the dataframe of countries where each row contains:
        - a publication IDs; 
        - the index of an address of the publication addresses; 
        - the country of the given address.

    Args:
        countries_df (dataframe): Data of countries per publications.

    Returns:
        (dataframe): Continents statistics where each row gives the continent name, 
                     the Institute-publications number with address from the continent 
                     and a string listing the concerned publications IDs separated by semicolon.
    """

    # Setting useful local aliases
    pub_id_alias = bp.COL_NAMES['pub_id']  # "Pub_id"
    country_alias = bp.COL_NAMES['country'][2]  # "Country"
    weight_alias = pg.COL_NAMES_BONUS['pub number']  # "Nombre de publications"
    pub_ids_alias = pg.COL_NAMES_BONUS["pub_ids list"]  # "Liste des Pub_ids"
    continent_alias = pg.COL_NAMES_BONUS['continent']  # "Continent"

    # Getting continent information by country from COUNTRIES_CONTINENT, a BiblioParsing global
    country_conti_dict = bp.COUNTRIES_CONTINENT

    # Replacing country by its continent in a copy of 'by_country_df'
    continents_df = countries_df.copy()
    continents_df[country_alias] = continents_df[country_alias].map(lambda x: country_conti_dict[x])

    # Renaming the column 'country_alias' to 'continent_alias'
    continents_df.rename(columns={country_alias: continent_alias}, inplace=True)

    by_continent_df = pd.DataFrame(columns=[continent_alias, weight_alias, pub_ids_alias])
    idx_continent = 0
    for continent, pub_id_dg in continents_df.groupby(continent_alias):
        pub_id_dg = pub_id_dg.drop_duplicates([pub_id_alias, continent_alias])
        pub_ids_list = pub_id_dg[pub_id_alias].tolist()
        pub_ids_nb = len(pub_ids_list)
        by_continent_df.loc[idx_continent, continent_alias] = continent
        by_continent_df.loc[idx_continent, weight_alias] = pub_ids_nb
        if continent != "Europe":
            pud_ids_txt = "; ".join(pub_ids_list)
        else:
            pud_ids_txt = pub_ids_list[0] + "..." + pub_ids_list[pub_ids_nb - 1]
        by_continent_df.loc[idx_continent, pub_ids_alias] = pud_ids_txt
        idx_continent += 1

    return by_continent_df


def coupling_analysis(institute, org_tup, bibliometer_path,
                      datatype, year, progress_callback=None, verbose=False):
    """ Performs the analysis of countries and authors affiliations of Institute publications 
    of the 'year' corpus. 
    To do that:
        - First, gets the 'all_address_df' dataframe of authors addresses from the file which full path 
        is given by 'addresses_item_path' and that is a deduplication results of the parsing step
        of the corpus.

        - Then, builds the 'inst_pub_addresses_df' dataframe by selecting in 'all_address_df' dataframe 
        only addresses related to publications of the Institute.

        - Then, builds the dataframes of countries, normalized institutions and raw institutions 
        through the `build_norm_raw_institutions` function imported from the package imported as bp, 
        using 'inst_pub_addresses_df' dataframe and specific files for this function; in these datraframes,  
        each row contains:
            - a publication IDs
            - the index of an address of the publication addresses 
            - the country of the given address
            - and for the institutions dataframes, the list of normalized institutions or the list of raw 
            institutions for the given address.  

        - Then, completes the normalized institutions and raw institutions dataframes with country 
        information by `_copy_dg_col_to_df` local function.

        - Then, modifyes the publication_IDs by `_year_pub_id` local function in the 3 dataframes.

        - Then, saves the normalized institutions and raw institutions dataframes through the 
        `_save_formatted_df_to_xlsx` local function.

        - Then, builds the publications statistics dataframes per country and per continent using 
        the `_build_countries_stat` and `_build_continents_stat` internal functions.

        - Then, saves the statistics dataframes through the `_save_formatted_df_to_xlsx` 
        local function.

        - Finally, saves the results of this analysis for the 'datatype' case through the 
        `save_final_results` function imported from `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year (str): 4 digits year of the corpus.
        progress_callback (function): Function for updating ProgressBar 
                                      tkinter widget status (default = None).
        verbose (bool): Status of prints (default = False).

    Returns:
        (path): Full path to the folder where results of keywords analysis are saved.
    """


    # Internal functions
    def _copy_dg_col_to_df(df, dg, col_alias):
        df[col_alias] = dg[col_alias]
        cols_list = [final_pub_id_alias, idx_address_alias, countries_col_alias, institutions_alias]
        df = df[cols_list]
        return df

    def _year_pub_id(df, year, pub_id_alias):
        '''The local function `_unique_pub_id` transforms the column 'Pub_id' of the df
        by adding "yyyy_" to the value of the row.

        Args:
            df (pandas.DataFrame()): pandas.DataFrame() that we want to modify.
            year (str):

        Returns:
            (pandas.DataFrame()): the df with its changed column.
        '''

        def _rename_pub_id(old_pub_id, year):
            pub_id_str = str(int(old_pub_id))
            while len(pub_id_str) < 3:
                pub_id_str = "0" + pub_id_str
            new_pub_id = str(int(year)) + '_' + pub_id_str
            return new_pub_id

        df[pub_id_alias] = df[pub_id_alias].apply(lambda x: _rename_pub_id(x, year))

    def _save_formatted_df_to_xlsx(results_path, item_filename, item_df,
                                   sheet_name, year, first_col_width, last_col_width):
        """Formats the 'item_df' dataframe through `format_df_for_excel` function 
        imported from `bmfuncts.useful_functs import` module and saves it as Excel workbook."""
        item_xlsx_file = item_filename + xlsx_extent_alias
        item_xlsx_path = results_path / Path(item_xlsx_file)
        wb, ws = format_df_for_excel(item_df, first_col_width, last_col_width)
        ws.title = sheet_name + year
        wb.save(item_xlsx_path)

    # Setting useful local aliases
    dedup_folder_alias = "dedup"
    xlsx_extent_alias = ".xlsx"

    # Setting aliases from globals
    tsv_extent_alias = "." + pg.TSV_SAVE_EXTENT
    addresses_item_alias = bp.PARSING_ITEMS_LIST[2]
    pub_list_folder_alias = pg.ARCHI_YEAR["pub list folder"]
    analysis_folder_alias = pg.ARCHI_YEAR["analyses"]
    geo_analysis_folder_alias = pg.ARCHI_YEAR["countries analysis"]
    inst_analysis_folder_alias = pg.ARCHI_YEAR["institutions analysis"]
    pub_list_filename_base = pg.ARCHI_YEAR["pub list file name base"]
    country_weight_filename_alias = pg.ARCHI_YEAR["country weight file name"]
    continent_weight_filename_alias = pg.ARCHI_YEAR["continent weight file name"]
    norm_inst_filename_alias = pg.ARCHI_YEAR["norm inst file name"]
    raw_inst_filename_alias = pg.ARCHI_YEAR["raw inst file name"]
    institutions_folder_alias = pg.ARCHI_INSTITUTIONS["root"]
    inst_types_file_base_alias = pg.ARCHI_INSTITUTIONS["inst_types_base"]
    country_affiliations_file_base_alias = pg.ARCHI_INSTITUTIONS["affiliations_base"]
    country_towns_file_base_alias        = pg.ARCHI_INSTITUTIONS["country_towns_base"]

    # Setting useful file names
    pub_list_filename = pub_list_filename_base + " " + str(year) + xlsx_extent_alias
    inst_types_file_alias = institute + "_" + inst_types_file_base_alias
    country_affil_file_alias = institute + "_" + country_affiliations_file_base_alias
    country_towns_file_alias = institute + "_" + country_towns_file_base_alias

    # Setting useful paths
    year_folder_path = bibliometer_path / Path(str(year))
    pub_list_folder_path = year_folder_path / Path(pub_list_folder_alias)
    pub_list_file_path = pub_list_folder_path / Path(pub_list_filename)
    analysis_folder_path = year_folder_path / Path(analysis_folder_alias)
    geo_analysis_folder_path = analysis_folder_path / Path(geo_analysis_folder_alias)
    inst_analysis_folder_path = analysis_folder_path / Path(inst_analysis_folder_alias)
    institutions_folder_path = bibliometer_path / Path(institutions_folder_alias)
    inst_types_file_path = institutions_folder_path / Path(inst_types_file_alias)
    country_affil_file_path = institutions_folder_path / Path(country_affil_file_alias)

    # Creating required output folders
    if not os.path.exists(analysis_folder_path):
        os.makedirs(analysis_folder_path)
    if not os.path.exists(geo_analysis_folder_path):
        os.makedirs(geo_analysis_folder_path)
    if not os.path.exists(inst_analysis_folder_path):
        os.makedirs(inst_analysis_folder_path)
    if progress_callback:
        progress_callback(10)

    # Setting useful column names aliases
    final_col_dic, depts_col_list = set_final_col_names(institute, org_tup)
    final_pub_id_alias = final_col_dic['pub_id']
    parsing_pub_id_alias = bp.COL_NAMES['pub_id']
    idx_address_alias = bp.COL_NAMES['institution'][1]
    institutions_alias = bp.COL_NAMES['institution'][2]
    countries_col_alias = bp.COL_NAMES['country'][2]

    # Getting the full paths of the working folder architecture for the corpus "year"
    config_tup = set_user_config(bibliometer_path, year, pg.BDD_LIST)
    parsing_path_dict = config_tup[1]
    item_filename_dict = config_tup[2]

    # Reading the full file of addresses
    addresses_item_file = item_filename_dict[addresses_item_alias] + tsv_extent_alias
    addresses_item_path = parsing_path_dict[dedup_folder_alias] / Path(addresses_item_file)
    all_address_df = pd.read_csv(addresses_item_path, sep='\t')
    if progress_callback:
        progress_callback(15)

    # Selecting only addresses of Institute publications
    pub_df = pd.read_excel(pub_list_file_path,
                           usecols=[final_pub_id_alias] + depts_col_list)
    pub_num_list = [int(x.split("_")[1]) for x in pub_df[final_pub_id_alias].tolist()]
    inst_pub_addresses_df = pd.DataFrame()
    for pub_id, dg in all_address_df.groupby(parsing_pub_id_alias):
        if pub_id in pub_num_list:
            inst_pub_addresses_df = pd.concat([inst_pub_addresses_df, dg])
    if progress_callback:
        progress_callback(20)

    # Building countries, normalized institutions and still unormalized ones
    return_tup = bp.build_norm_raw_institutions(inst_pub_addresses_df,
                                                inst_types_file_path = inst_types_file_path,
                                                country_affiliations_file_path = country_affil_file_path,
                                                country_towns_file = country_towns_file_alias,
                                                country_towns_folder_path = institutions_folder_path,
                                                verbose=verbose)
    countries_df, norm_institutions_df, raw_institutions_df = return_tup
    if progress_callback:
        progress_callback(60)

    # Adding countries column to 'norm_institutions_df' and 'raw_institutions_df'
    norm_institutions_df = _copy_dg_col_to_df(norm_institutions_df, countries_df,
                                              countries_col_alias)
    raw_institutions_df = _copy_dg_col_to_df(raw_institutions_df, countries_df,
                                             countries_col_alias)
    if progress_callback:
        progress_callback(65)

    # Building pub IDs with year information
    _year_pub_id(countries_df, year, parsing_pub_id_alias)
    _year_pub_id(norm_institutions_df, year, parsing_pub_id_alias)
    _year_pub_id(raw_institutions_df, year, parsing_pub_id_alias)
    if progress_callback:
        progress_callback(70)

    # Saving formatted df of normalized and raw institutions
    first_col_width = 12
    last_col_width = 80
    _save_formatted_df_to_xlsx(inst_analysis_folder_path, norm_inst_filename_alias,
                               norm_institutions_df, 'Norm Inst', year,
                               first_col_width, last_col_width)
    _save_formatted_df_to_xlsx(inst_analysis_folder_path, raw_inst_filename_alias,
                               raw_institutions_df, 'Raw Inst', year,
                               first_col_width, last_col_width)
    if progress_callback:
        progress_callback(80)

    # Building stat dataframes
    by_country_df = _build_countries_stat(countries_df)
    by_continent_df = _build_continents_stat(countries_df)

    # Saving formatted stat dataframes
    first_col_width = 32
    last_col_width = 80
    _save_formatted_df_to_xlsx(geo_analysis_folder_path, country_weight_filename_alias,
                               by_country_df, 'Pays', year,
                               first_col_width, last_col_width)
    _save_formatted_df_to_xlsx(geo_analysis_folder_path, continent_weight_filename_alias,
                               by_continent_df, 'Continent', year,
                               first_col_width, last_col_width)
    if progress_callback:
        progress_callback(90)

    # Saving coupling analysis as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["countries"] = True
    results_to_save_dict["continents"] = True
    if_analysis_name = None
    _ = save_final_results(institute, org_tup, bibliometer_path, datatype, year,
                           if_analysis_name, results_to_save_dict, verbose=False)
    if progress_callback:
        progress_callback(100)

    return analysis_folder_alias, geo_analysis_folder_alias, inst_analysis_folder_alias
