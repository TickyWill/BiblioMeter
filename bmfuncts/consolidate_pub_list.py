"""Module of functions for the consolidation of the publications-list 
in terms of:

- effective affiliation of the authors to the Institute;
- attributing department affiliation to the Institute authors;
- reduction of homonyms among the Institute authors;
- attributing OTPs to each publication;
- attributing impact factor (IF) to each publication.

"""

__all__ = ['add_if',
           'built_final_pub_list',
           'concatenate_pub_lists',
           'get_if_db',
           'solving_homonyms',
           'split_pub_list_by_doc_type',
          ]


# Standard library imports
import os
from datetime import datetime
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl.worksheet.datavalidation import DataValidation \
    as openpyxl_DataValidation
from openpyxl.utils import get_column_letter \
    as openpyxl_get_column_letter

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.institute_globals as ig
import bmfuncts.pub_globals as pg
from bmfuncts.format_files import format_page
from bmfuncts.format_files import set_base_keys_list
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.rename_cols import set_homonym_col_names
from bmfuncts.rename_cols import set_otp_col_names
from bmfuncts.rename_cols import set_if_col_names
from bmfuncts.use_homonyms import solving_homonyms
from bmfuncts.use_otps import save_otps
from bmfuncts.save_final_results import save_final_results


def _create_if_column(issn_column, if_dict, if_empty_word):
    """Builds a dataframe column 'if_column' using the column 'issn_column' 
    of this dataframe and the dict 'if_dict'.

    The dict 'if_dict' make the link between ISSNs ('if_dict' keys) and 
    IFs ('if_dict' values). 
    The 'nan' values in the column 'if_column' are replaced by 'empty_word'.

    Args:
        issn_column (pandas serie): The column of the dataframe of interest \
        that contains the ISSNs values.
        if_dict (dict): The dict which keys are ISSNs and values are IFs.
        if_empty_word (str): The word that will replace nan values in \
        the returned column.
    Returns:
        (pandas serie): The column of the dataframe of interest \
        that contains the IFs values.
    """
    if_column = issn_column.map(if_dict)
    if_column = if_column.fillna(if_empty_word)
    return if_column


def _build_inst_issn_df(if_db_df, use_col_list):
    """Builds a dataframe of 'use_col_list' columns composed of journal name, 
    ISSN and eISSN.

    First, a subset dataframe is built from the hierarchical dataframe 'if_db_df' 
    using 'use_col_list' columns for each year (key of 'if_db_df'). 
    Then, a single dataframe results from concatenation of these dataframes. 
    Finally, duplicates are dropped after setting unique ISSN and eISSN values 
    for each journal name.

    Args:
        if_db_df (dataframe): Hierarchical dataframe of impact-factors database \
        keyyed by years.
        use_col_list (list): List of subset columns names \
        of 'if_db_df[<year>]' dataframes.
    Returns:
        (dataframe): Dataframe with 'use_col_list' columns.
    """

    # Setting useful aliases
    journal_col_alias = use_col_list[0]
    issn_col_alias = use_col_list[1]
    eissn_col_alias = use_col_list[2]
    unknown_alias = bp.UNKNOWN

    years_list = list(if_db_df.keys())

    init_inst_issn_df = pd.DataFrame(columns=use_col_list)

    for year in years_list:
        year_sub_df = if_db_df[year][use_col_list].copy()
        init_inst_issn_df = pd.concat([init_inst_issn_df, year_sub_df])
    init_inst_issn_df[journal_col_alias] = init_inst_issn_df.apply(lambda row:
                                                                   (row[journal_col_alias].upper()),
                                                                    axis=1)

    inst_issn_df = pd.DataFrame()
    for _ , dg in init_inst_issn_df.groupby(journal_col_alias):

        issn_list = list(set(dg[issn_col_alias].to_list()) - {unknown_alias})
        if not issn_list:
            issn_list = [unknown_alias]
        dg[issn_col_alias] = issn_list[0]

        eissn_list = list(set(dg[eissn_col_alias].to_list()) - {unknown_alias})
        if not eissn_list:
            eissn_list = [unknown_alias]
        dg[eissn_col_alias] = eissn_list[0]

        inst_issn_df = pd.concat([inst_issn_df,dg.iloc[:1]])

    inst_issn_df.sort_values(by=[journal_col_alias], inplace=True)
    inst_issn_df.drop_duplicates(inplace=True)

    return inst_issn_df


def _fullfill_issn(corpus_df, issn_df, unknown, col_tup):
    """Fills the unknown values in the 'issn_col' column 
    in the 'corpus_df' dataframe.

    For that it uses the ISSN or eISSN' available in the 'issn_df' dataframe.

    Args:
        corpus_df (dataframe): Corpus of publications to be updated.
        issn_df (dataframe): Data of journals with their ISSN and eISSN.
        unknown (str): Value of unknown ISSN or eISSN.
        col_tup (tup): Tuple of columns names = (journal name, ISSN, eISSN).
    Returns:
        (dataframe): Updated dataframe.
    """

    # Setting parameters from args
    journal_col, issn_col, eissn_col = col_tup

    for corpus_idx, corpus_row in corpus_df.iterrows():
        if corpus_row[issn_col]!=unknown:
            continue
        corpus_journal = corpus_row[journal_col].upper()
        for _, issn_row in issn_df.iterrows():
            issn_journal = issn_row[journal_col].upper()
            if corpus_journal!=issn_journal:
                continue
            if issn_row[issn_col]!=unknown:
                corpus_df.loc[corpus_idx, issn_col] = issn_row[issn_col]
            elif issn_row[eissn_col]!=unknown:
                corpus_df.loc[corpus_idx, issn_col] = issn_row[eissn_col]
            else:
                pass
    return corpus_df


def _build_if_dict(if_df, if_year, args_tup):
    """Builds a dict keyyed by ISSN or eISSN values and valued 
    by impact factors.

    Args:
        if_df (dataframe): Database of impact-factors.
        if_year (str): 4 digits-year key for using values from the database \
        of impact-factors.
        args_tup (tup): Tuple = (value of unknown ISSN or eISSN, \
        ISSN-column name, eISSN-column name, impact-factors-column name).
    Returns:
        (dict): dict keyyed by ISSN (str) or eISSN (str) values \
        and valued by impact factors (float).
    """

    # Setting parameters from args
    unknown, issn_col, eissn_col, if_col = args_tup

    issn_if_dict = dict(zip(if_df[if_year][issn_col],
                            if_df[if_year][if_col]))
    if unknown in issn_if_dict:
        del issn_if_dict[unknown]
    eissn_if_dict = {}
    if eissn_col in list(if_df[if_year].columns):
        eissn_if_dict = dict(zip(if_df[if_year][eissn_col],
                                 if_df[if_year][if_col]))
        if unknown in eissn_if_dict.keys():
            del eissn_if_dict[unknown]
    if_dict = {**issn_if_dict, **eissn_if_dict}
    return if_dict


def _get_id(issn_df, journal_name, journal_col, id_col, unknown):
    """Sets a unique journal name for the ISSN value at 'journal_name' 
    key in 'issn_df' dataframe.

    Args:
        issn_df (dataframe): Data of journals with their ISSN and eISSN.
        journal_name (str): Name of journal for which the unique name will be defined.
        journal_col (str): Name of the journal-names column in the 'issn_df' dataframe.
        id_col (str): Name of the ISSN or eISSN column to be used in the 'issn_df' dataframe.
    Returns:
        (str): Unified journal name.
    """

    # Setting parameters from args
    id_lower_df = issn_df[issn_df[journal_col]==journal_name.lower()][id_col]
    id_lower = unknown
    if not id_lower_df.empty:
        id_lower = id_lower_df.to_list()[0]
    id_upper_df = issn_df[issn_df[journal_col]==journal_name.upper()][id_col]
    id_upper = unknown
    if not id_upper_df.empty:
        id_upper = id_upper_df.to_list()[0]
    journal_id = list(set([id_lower,id_upper]) - set([unknown]))[0]
    return journal_id


def _format_missing_df(results_df, common_args_tup, unknown, add_cols):
    """Formats the 'results_df' dataframe with final column names.

    Args:
        results_df (dataframe): Corpus of publications to be updated.
        common_args_tup (tup): Tuple of columns name (str) = (year (4 digits), \
        corpus-year impact-factor, impact-factors most-recent year, journal-name, \
        ISSN, eISNN, number of publications, impact-factors year, ISSN in \
        'result_df' dataframe).
        unknown (str): Value of unknown ISSN or eISSN in 'results_df' dataframe.
        add_cols (bool): True if suplementary columns for ISSN and eISSN are to be \
        filled with unknown values.
    Returns:
        (dataframe): Formatted dataframe.
    """
    (year_col, corpus_year_if_col,
     most_recent_year_if_col,
     journal_col, issn_col, eissn_col,
     pub_id_nb_col, year_db_if_col,
     corpus_issn_col) = common_args_tup

    # Setting final year column
    final_year_col = year_col[0:5]

    # Setting the ordered final columns
    final_order_col_list = [final_year_col, journal_col,
                            issn_col, eissn_col,
                            most_recent_year_if_col,
                            year_db_if_col,
                            pub_id_nb_col,
                            corpus_issn_col]

    # Formatting 'results_df'
    results_df.rename(columns={year_col: final_year_col,
                               corpus_year_if_col: year_db_if_col},
                      inplace=True)
    if add_cols:
        results_df.rename(columns={issn_col: corpus_issn_col},
                          inplace=True)
        results_df[issn_col]  = unknown
        results_df[eissn_col] = unknown
        results_df = results_df[final_order_col_list]
    else:
        if results_df.empty:
            results_df[eissn_col] = unknown
        results_df = results_df[final_order_col_list[:-1]]
    sorted_results_df = results_df.sort_values(by=[journal_col])
    return sorted_results_df


def get_if_db(institute, org_tup, bibliometer_path):
    """Builds a dataframe of impact-factors of the Institute.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
    Returns:
        (tup): (impact-factors (dataframe), \
        available-years of impact-factors in the dataframe (list), \
        most-recent year of available impact-factors (4-digits str)).
    """

    ## Setting institute parameters
    if_db_status = org_tup[5]

    # Setting useful aliases
    if_root_folder_alias = pg.ARCHI_IF["root"]
    if_filename_alias = pg.ARCHI_IF["all IF"]
    inst_if_filename_alias = institute + pg.ARCHI_IF["institute_if_all_years"]

    if if_db_status:
        if_filename_alias = inst_if_filename_alias

    # Setting useful paths
    if_root_folder_path = bibliometer_path / Path(if_root_folder_alias)
    if_path = if_root_folder_path / Path(if_filename_alias)

    # Getting the df of the IFs database
    if_df = pd.read_excel(if_path, sheet_name=None)

    # Setting list of years for which IF are available
    if_available_years_list = list(if_df.keys())

    # Setting the most recent year for which IF are available
    if_most_recent_year = if_available_years_list[-1]

    return if_df, if_available_years_list, if_most_recent_year


def add_if(institute, org_tup, bibliometer_path, paths_tup, corpus_year):

    """Adds two new columns containing impact factors to the corpus 
    dataframe 'corpus_df' got from a file which full path is 'in_file_path'.

    The two columns are named through 'corpus_year_if_col_alias' 
    and 'most_recent_year_if_col'. 
    The impact factors are got using `get_if_db` function that returns 
    in particular the dataframe 'if_df' of impact-factors database. 
    The column 'corpus_year_if_col_alias' is filled with the impact-factors 
    values of the corpus year 'corpus_year' if available in the dataframe 'if_df', 
    otherwise the values are set to 'not_available_if_alias' value. 
    The column 'most_recent_year_if_col' is filled with the impact-factors 
    values of the most recent year available in the dataframe 'if_df'. 
    In these columns, the NaN values of impact-factors are replaced 
    by 'unknown_if_fill_alias'. 
    The results are saved as openpyxl workbook formatted through the `format_page`
    function imported from the `bmfuncts.format_files` module after 
    setting the attrubutes keys list through the `set_base_keys_list` function 
    imported from the same module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        paths_tup (tup): Tuple = (full path to get the corpus dataframe 'corpus_df', \
        full path to save the missing impact-factors information, \
        full path to save the missing ISSNs information, \
        year (4 digits str) of the corpus to be appended with the two \
        new impact-factors columns).
    Returns:
        (tup): (message indicating which file has been mofified and how, \
        completion status of the impact-factors database).
    """

    #Setting parameters from args
    (in_file_path, out_file_path,
     missing_if_path, missing_issn_path) = paths_tup

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    base_col_list = list(final_col_dic.values())
    if_maj_col_dic = set_if_col_names(institute, org_tup)

    # Setting useful column aliases
    pub_id_col_alias = final_col_dic['pub_id']
    year_col_alias = final_col_dic['corpus_year']
    journal_col_alias = final_col_dic['journal']
    doctype_col_alias = final_col_dic['doc_type']
    issn_col_alias = final_col_dic['issn']
    otp_col_alias = final_col_dic['otp']
    current_if_col_alias = if_maj_col_dic['current_if']
    corpus_year_if_col_alias = if_maj_col_dic['pub_year_if']
    corpus_issn_col_alias = pg.COL_NAMES_BONUS["database ISSN"]
    database_if_col_alias = pg.COL_NAMES_BONUS['IF clarivate']
    eissn_col_alias = pg.COL_NAMES_BONUS['e-ISSN']
    otp_col_new_alias = pg.COL_NAMES_BONUS['final OTP']
    pub_id_nb_col_alias = pg.COL_NAMES_BONUS['pub number']

    # Setting globals aliases
    doc_type_dict_alias = pg.DOC_TYPE_DICT
    not_available_if_alias = pg.NOT_AVAILABLE_IF
    unknown_if_fill_alias = pg.FILL_EMPTY_KEY_WORD
    unknown_alias = pg.FILL_EMPTY_KEY_WORD
    outside_if_analysis_alias = pg.OUTSIDE_ANALYSIS

    # Setting tuples for passing args
    col_tup = (journal_col_alias, issn_col_alias, eissn_col_alias)
    aliases_tup = (unknown_alias, issn_col_alias, eissn_col_alias, database_if_col_alias)

    # Setting institute parameters
    if_db_status = org_tup[5]
    no_if_doctype_keys_list = org_tup[6]

    # Setting list of document types to drop
    no_if_doctype = sum([doc_type_dict_alias[x] for x in no_if_doctype_keys_list] , [])
    doctype_to_drop_list_alias = [x.upper() for x in no_if_doctype]

    # Getting the df of the IFs database
    if_df, if_available_years_list, if_most_recent_year = get_if_db(institute, org_tup,
                                                                    bibliometer_path)

    # Taking care all IF column names in if_df are set to database_if_col_alias
    if if_db_status:
        for year in if_available_years_list:
            year_database_if_col_alias = database_if_col_alias + " " + year
            if_df[year].rename(columns={year_database_if_col_alias: database_if_col_alias},
                               inplace=True)

    # Replacing NAN in if_df
    values_dict = {issn_col_alias: unknown_alias,
                   eissn_col_alias: unknown_alias,
                   database_if_col_alias: not_available_if_alias}
    for year in if_available_years_list:
        if_df[year].fillna(value=values_dict, inplace=True)

    # Building the IF dict keyed by issn or e-issn of journals for the most recent year
    most_recent_year_if_dict = _build_if_dict(if_df, if_most_recent_year, aliases_tup)

    # Setting local column names
    most_recent_year_if_col = current_if_col_alias + ', ' + if_most_recent_year
    year_db_if_col = database_if_col_alias + ' ' + corpus_year
    journal_upper_col = journal_col_alias + '_Upper'

    # Getting the df where to add IFs
    corpus_df = pd.read_excel(in_file_path)

    # Recasting column names
    new_base_col_list = list(
        map(lambda x: x.replace(otp_col_alias, otp_col_new_alias),
            base_col_list)
    )
    if otp_col_alias in corpus_df.columns:
        corpus_df.rename(columns={otp_col_alias : otp_col_new_alias},
                         inplace =True)

    # Setting type of values in 'year_col_alias' as string
    corpus_df = corpus_df.astype({year_col_alias: str})

    # Initializing 'corpus_df_bis' as copy of 'corpus_df'
    corpus_df_bis = corpus_df[new_base_col_list].copy()

    # Getting the df of ISSN and eISSN database of the institut
    use_col_list = [journal_col_alias, issn_col_alias, eissn_col_alias]
    inst_issn_df = _build_inst_issn_df(if_df, use_col_list)

    # Filling unknown ISSN in 'corpus_df_bis' using 'inst_issn_df'
    # through _fullfill_issn function
    corpus_df_bis = _fullfill_issn(corpus_df_bis, inst_issn_df, unknown_alias, col_tup)

    # Adding 'most_recent_year_if_col' column to 'corpus_df_bis'
    # with values defined by internal function '_create_if_column'
    corpus_df_bis[most_recent_year_if_col] = _create_if_column(corpus_df_bis[issn_col_alias],
                                                               most_recent_year_if_dict,
                                                               unknown_if_fill_alias)

    # Adding 'corpus_year_if_col_alias' column to 'corpus_df_bis'
    if corpus_year in if_available_years_list:
        # with values defined by internal function '_create_if_column'
        # Building the IF dict keyed by issn or e-issn of journals for the corpus year
        current_year_if_dict = _build_if_dict(if_df, corpus_year, aliases_tup)
        corpus_df_bis[corpus_year_if_col_alias] = _create_if_column(corpus_df_bis[issn_col_alias],
                                                                    current_year_if_dict,
                                                                    unknown_if_fill_alias)
    else:
        # with 'not_available_if_alias' value
        corpus_df_bis[corpus_year_if_col_alias] = not_available_if_alias

    # Sorting 'corpus_df_bis' pub_id values
    corpus_df_bis.sort_values(by = [pub_id_col_alias], inplace=True)

    # Building 'year_pub_if_df' with subset of 'corpus_df_bis' columns
    subsetcols = [pub_id_col_alias,
                  year_col_alias,
                  journal_col_alias,
                  doctype_col_alias,
                  issn_col_alias,
                  most_recent_year_if_col,
                  corpus_year_if_col_alias,]
    year_pub_if_df = corpus_df_bis[subsetcols].copy()

    # Building 'year_article_if_df' by keeping only rows which doc type has usually an IF
    # then droping the doc type column
    year_article_if_df = pd.DataFrame(columns=year_pub_if_df.columns)
    for doc_type, doc_type_df in year_pub_if_df.groupby(doctype_col_alias):
        if doc_type.upper() not in doctype_to_drop_list_alias:
            year_article_if_df = pd.concat([year_article_if_df, doc_type_df])
    year_article_if_df.drop(doctype_col_alias, axis=1, inplace=True)

    # Building 'year_if_df' by keeping one row for each issn
    # adding a column with number of related articles
    # then droping "Pub_id" column
    year_if_df = pd.DataFrame(columns=year_article_if_df.columns.to_list() [1:] \
                                      + [pub_id_nb_col_alias])
    for _, issn_df in year_article_if_df.groupby(issn_col_alias):
        pub_id_nb = len(issn_df)
        issn_df[pub_id_nb_col_alias] = pub_id_nb
        issn_df.drop(pub_id_col_alias, axis=1, inplace=True)
        issn_df[journal_upper_col] = issn_df[journal_col_alias].astype(str).str.upper()
        issn_df.drop_duplicates(subset=[journal_upper_col], keep='first', inplace=True)
        issn_df.drop([journal_upper_col], axis=1, inplace=True)
        year_if_df = pd.concat([year_if_df, issn_df])

    # Removing from 'year_if_df' the rows which ISSN value is not in IF database
    # and keeping them in 'year_missing_issn_df'
    year_missing_issn_df = pd.DataFrame(columns = year_if_df.columns)
    year_missing_if_df = pd.DataFrame(columns = year_if_df.columns)
    inst_issn_list = inst_issn_df[issn_col_alias].to_list()
    inst_eissn_list = inst_issn_df[eissn_col_alias].to_list()
    for _, row in year_if_df.iterrows():
        row_issn = row[issn_col_alias]
        row_most_recent_year_if = row[most_recent_year_if_col]
        row_corpus_year_if = row[corpus_year_if_col_alias]
        if row_issn not in inst_issn_list and row_issn not in inst_eissn_list:
            year_missing_issn_df = pd.concat([year_missing_issn_df, row.to_frame().T])
        elif unknown_alias in [row_most_recent_year_if, row_corpus_year_if]:
            row_journal = row[journal_col_alias]
            row[issn_col_alias] = _get_id(inst_issn_df, row_journal,
                                          journal_col_alias, issn_col_alias,
                                          unknown_alias)
            row[eissn_col_alias] = _get_id(inst_issn_df, row_journal,
                                           journal_col_alias, eissn_col_alias,
                                           unknown_alias)
            year_missing_if_df = pd.concat([year_missing_if_df, row.to_frame().T])

    if_database_complete = True
    if not year_missing_issn_df.empty or not year_missing_if_df.empty:
        if_database_complete = False
    else:
        # replace remaining unknown IF values by 'not_available_if_alias' value
        corpus_df_bis.replace({most_recent_year_if_col: unknown_if_fill_alias,
                               corpus_year_if_col_alias: unknown_if_fill_alias,
                              }, outside_if_analysis_alias, inplace=True)

    # Setting common args list for '_format_missing_df' function
    common_args_tup = (year_col_alias, corpus_year_if_col_alias,
                       most_recent_year_if_col,
                       journal_col_alias, issn_col_alias, eissn_col_alias,
                       pub_id_nb_col_alias, year_db_if_col,
                       corpus_issn_col_alias)

    # Formatting 'year_missing_issn_df' and 'year_missing_if_df'
    sorted_year_missing_issn_df = _format_missing_df(
        year_missing_issn_df, common_args_tup, unknown_alias, add_cols=True)
    sorted_year_missing_if_df   = _format_missing_df(
        year_missing_if_df, common_args_tup, unknown_alias, add_cols=False)

    # Setting useful parameters for use of 'format_page' function
    common_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)
    
    # Formatting and saving 'corpus_df_bis' as openpyxl file at full path 'out_file_path'
    wb, _ = format_page(corpus_df_bis, common_df_title,
                        attr_keys_list=format_cols_list)    
    wb.save(out_file_path)

    # Saving 'year_missing_issn_df' as openpyxl file at full path 'missing_issn_path'
    wb, _ = format_page(sorted_year_missing_issn_df, common_df_title,
                        attr_keys_list=format_cols_list)   
    wb.save(missing_issn_path)

    # Saving 'year_missing_if_df' as openpyxl file at full path 'missing_if_path'
    wb, _ = format_page(sorted_year_missing_if_df, common_df_title,
                        attr_keys_list=format_cols_list)  
    wb.save(missing_if_path)

    end_message = f"IFs added for year {year} in file : \n  '{out_file_path}'"
    return end_message, if_database_complete


def split_pub_list_by_doc_type(institute, org_tup, bibliometer_path, corpus_year):
    """Splits the dataframe of the publications final list into dataframes 
    corresponding to different documents types.

    This is done for the 'corpus_year' corpus. 
    These dataframes are saved through the `format_page` function 
    imported from `bmfuncts.format_files` module after setting 
    the attrubutes keys list through the `set_base_keys_list` 
    function imported from the same module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (int): Split ratio in % of the publications final list.
    """
    # Setting useful parameters for use of 'format_page' function
    common_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)

    # Setting useful aliases
    pub_list_path_alias = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    year_pub_list_file_alias = pub_list_file_base_alias + " " + corpus_year
    pub_list_file_alias = year_pub_list_file_alias + ".xlsx"
    other_dg_file_alias = year_pub_list_file_alias + "_" + pg.OTHER_DOCTYPE + ".xlsx"
    corpus_year_path = bibliometer_path / Path(corpus_year)
    pub_list_path = corpus_year_path / Path(pub_list_path_alias)
    pub_list_file_path = pub_list_path / Path(pub_list_file_alias)
    other_dg_path = pub_list_path / Path(other_dg_file_alias)

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    pub_id_col_alias = final_col_dic['pub_id']
    doc_type_alias = final_col_dic['doc_type']

    full_pub_list_df = pd.read_excel(pub_list_file_path)
    other_dg = full_pub_list_df.copy()
    pub_nb = len(full_pub_list_df)
    key_pub_nb = 0
    for key, doctype_list in pg.DOCTYPE_TO_SAVE_DICT.items():
        doctype_list = [x.upper() for x in  doctype_list]
        key_dg = pd.DataFrame(columns=full_pub_list_df.columns)

        for doc_type, dg in full_pub_list_df.groupby(doc_type_alias):
            if doc_type.upper() in doctype_list:
                key_dg = pd.concat([key_dg, dg])
                other_dg = other_dg.drop(dg.index)

        key_pub_nb += len(key_dg)
        key_dg_file_alias = year_pub_list_file_alias + "_" + key + ".xlsx"
        key_dg_path = pub_list_path / Path(key_dg_file_alias)

        key_dg.sort_values(by=[pub_id_col_alias], inplace=True)
        wb, _ = format_page(key_dg, common_df_title,
                            attr_keys_list=format_cols_list)
        wb.save(key_dg_path)

    other_dg.sort_values(by=[pub_id_col_alias], inplace=True)
    wb, _ = format_page(other_dg, common_df_title,
                        attr_keys_list=format_cols_list)
    wb.save(other_dg_path)

    split_ratio = 100
    if pub_nb != 0:
        split_ratio = round(key_pub_nb / pub_nb*100)
    return split_ratio


def _set_dpt_otp_df(dpt_label, in_file_base, in_path):
    """Gets the publications list of the a department 
    from the EXCEL files where the user has set the OTPs.

    The name of the file is build using the file-name base 
    and the department label. This name is added '_ok' if 
    this file exists in the folder of files. 
    Then the file is read as a multisheet EXCEL file. 
    The final publication list of the department results from 
    the concatenation of the containt of all the existing sheets.  

    Args:
        dpt_label (str): Label of the department.
        in_file_base (str): Base of OTPs files names.
        in_path (path): Full path to folder of files where OTPs \
        have been attributed.
    Returns:
        (dataframe): The concatenated publications list with OTPs.        
    """
    otp_file_name_dpt = in_file_base + '_' + dpt_label
    otp_file_name_dpt_ok = otp_file_name_dpt + '_ok'
    dpt_otp_path = in_path / Path(otp_file_name_dpt_ok + '.xlsx')
    if not os.path.exists(dpt_otp_path):
        dpt_otp_path = in_path / Path(otp_file_name_dpt + '.xlsx')
    dpt_otp_dict = pd.read_excel(dpt_otp_path, sheet_name=None)
    dpt_otp_df = pd.DataFrame()
    for _, lab_df in dpt_otp_dict.items():
        dpt_otp_df = pd.concat([dpt_otp_df, lab_df])    
    return dpt_otp_df


def _concat_dept_otps_dfs(org_tup, in_file_base, in_path):
    """Concatenates the publications list of the Institute departments 
    after getting them through the `_set_dpt_otp_df` internal function.

    Args:
        org_tup (tup): Contains Institute parameters.
        in_file_base (str): Base of OTPs files names.
        in_path (path): Full path to folder of files where OTPs \
        have been attributed.
    Returns:
        (dataframe): The concatenated publications list with OTPs.        
    """
    # Setting institute parameters
    dpt_label_dict = org_tup[1]
    dpt_label_list = list(dpt_label_dict.keys())

    # Concatenating publications list with OTPs of the Institute departments
    otp_df_init_status = True
    for dpt_label in dpt_label_list:
        # Getting department publications list with OTPs
        dpt_otp_df = _set_dpt_otp_df(dpt_label, in_file_base, in_path)

        # Appending department publications list with OTPs
        # to the full publication list to be returned   
        if otp_df_init_status:
            otp_df = dpt_otp_df.copy()
            otp_df_init_status = False
        else:
            otp_df = pd.concat([otp_df, dpt_otp_df])
    return otp_df


def built_final_pub_list(institute, org_tup, bibliometer_path, datatype,
                         in_path, out_path, in_file_base, corpus_year):
    """Builds the dataframe of the publications final list 
    of the 'corpus_year' corpus.

    This is done through the following steps:

    1. A 'consolidate_pub_list_df' dataframe is built through \
    the concatenation of the dataframes got from the files of \
    OTPs attribution to publications of each of the Institute \
    departments through the `_concat_dept_otps_dfs` internal function.
    2. Meanwhile, the set OTPS are saved through the `save_otps` \
    function imported from `bmfuncts.use_pub_attributes` module. 
    3. The publications attributed with 'INVALIDE' OTP value, \
    (imported from `bmfuncts.institute_globals` module) are dropped \
    in the 'consolidate_pub_list_df' dataframe and kept in \
    the 'invalids_df' dedicated dataframe.
    4. These two dataframes are then saved respectively as EXCEL file \
    and openpyxl file through the `format_page` function imported \
    from `bmfuncts.format_files` module after setting the attrubutes \
    keys list through the `set_base_keys_list` function imported \
    from the same module.
    5. The file saved from the 'consolidate_pub_list_df' dataframe \
    is added with impact factors values through the `add_if` function \
    of the present module.
    6. This dataframe is split by documents type through the \
    `split_pub_list_by_doc_type` function of the present module.
    7. A copy of all the created files is made in a folder specific to \
    the combination type of data specified by 'datatype' arg \
    through the `save_final_results` function imported from \
    the `bmfuncts.save_final_results` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        in_path (path): Full path to folder of files where OTPs \
        have been attributed.
        out_path (path): Full path to folder where file of publications \
        final list and associated files are saved.
        in_file_base (str): Base of OTPs files names.
        corpus_year (str): 4 digits year of the corpus.
    Returns :
        (tup): (end message recalling the full path to the saved file \
        of the publication final list, split ratio in % of the publications \
        final list, completion status of the impact-factors database).
    """

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    final_col_list = list(final_col_dic.values())

    # Setting useful aliases
    pub_list_filename_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    missing_if_filename_base_alias = pg.ARCHI_IF["missing_if_base"]
    missing_issn_filename_base_alias = pg.ARCHI_IF["missing_issn_base"]
    invalid_pub_filename_base_alias = pg.ARCHI_YEAR["invalid file name base"]
    pub_id_alias = final_col_dic['pub_id']
    otp_alias = final_col_dic['otp'] # Choix de l'OTP
    otp_col_new_alias = pg.COL_NAMES_BONUS['final OTP'] # OTP

    # Setting useful paths
    pub_list_file_path = out_path / Path(pub_list_filename_base_alias
                                         + " " + corpus_year + ".xlsx")
    missing_if_path = out_path / Path(corpus_year + missing_if_filename_base_alias)
    missing_issn_path = out_path / Path(corpus_year + missing_issn_filename_base_alias)
    invalids_file_path = out_path / Path(invalid_pub_filename_base_alias
                                        + " " + corpus_year + ".xlsx")

    # Getting dept OTPs df and concatenating them
    otp_df = _concat_dept_otps_dfs(org_tup, in_file_base, in_path)

    # Deduplicating rows on Pub_id
    otp_df.drop_duplicates(subset=[pub_id_alias], inplace=True)

    # Selecting useful columns using final_col_list
    consolidate_pub_list_df = otp_df[final_col_list].copy()

    # Saving df to EXCEL file
    consolidate_pub_list_df.to_excel(pub_list_file_path, index=False)

    # Saving set OTPs
    otp_message = save_otps(institute, org_tup, bibliometer_path, corpus_year)

    # Setting pub ID as index for unique identification of rows
    consolidate_pub_list_df.set_index(pub_id_alias, inplace=True)

    # Droping invalid publications by pub Id as index
    invalids_idx_list = consolidate_pub_list_df[consolidate_pub_list_df[otp_alias]\
                                                !=ig.INVALIDE].index
    invalids_df = consolidate_pub_list_df.drop(index=invalids_idx_list)
    valids_idx_list = consolidate_pub_list_df[consolidate_pub_list_df[otp_alias]\
                                                         ==ig.INVALIDE].index
    consolidate_pub_list_df.drop(index=valids_idx_list, inplace=True)

    # Resetting pub ID as a standard column
    consolidate_pub_list_df.reset_index(inplace=True)
    invalids_df.reset_index(inplace=True)

    # Re_saving df to EXCEL file
    consolidate_pub_list_df.to_excel(pub_list_file_path, index=False)
    
    # Formatting and saving 'invalids_df' as openpyxl file
    # at full path 'invalids_file_path'
    invalids_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)
    invalids_df.rename(columns={otp_alias: otp_col_new_alias}, inplace=True)
    wb, _ = format_page(invalids_df, invalids_df_title,
                        attr_keys_list=format_cols_list)
    wb.save(invalids_file_path)

    # Adding Impact Factors and saving new consolidate_pub_list_df
    # this also for saving results files to complete IFs database
    paths_tup = (pub_list_file_path, pub_list_file_path,
                 missing_if_path, missing_issn_path)
    _, if_database_complete = add_if(institute, org_tup, bibliometer_path,
                                     paths_tup, corpus_year)

    # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
    split_ratio = split_pub_list_by_doc_type(institute, org_tup,
                                             bibliometer_path, corpus_year)

    # Saving pub list as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["pub_lists"] = True
    if_analysis_name = None
    final_save_message = save_final_results(institute, org_tup, bibliometer_path,
                                            datatype, corpus_year, if_analysis_name,
                                            results_to_save_dict, verbose=False)

    end_message  = (f"\n{otp_message}"
                    f"\nOTPs identification integrated in file: \n  '{pub_list_file_path}'"
                    f"\n\nPublications list for year {corpus_year} "
                    f"has been {split_ratio} % split "
                    "in several files by group of document types. \n"
                    f"{final_save_message}")

    return end_message, split_ratio, if_database_complete


def concatenate_pub_lists(institute, org_tup, bibliometer_path, years_list):
    """Builds the concatenated dataframe of the publications lists 
    of the corpuses listed in 'years_list'.

    The dataframe is saved through the `format_page` function 
    imported from `bmfuncts.format_files` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        years_list (list): List of 4 digits years of the available \
        publications lists.
    Returns :
        (str): End message recalling folder and file name where file is saved.
    """

    # Setting useful aliases
    pub_list_path_alias = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    bdd_multi_annuelle_folder_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    bdd_multi_annuelle_file_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["concat file name base"]

    # Building the concatenated dataframe of available publications lists
    concat_df = pd.DataFrame()
    available_liste_conso = ""
    for year in years_list:
        try:
            corpus_folder_path = bibliometer_path / Path(year)
            pub_list_folder_path = corpus_folder_path / Path(pub_list_path_alias)
            pub_list_file_name = f"{pub_list_file_base_alias} {year}.xlsx"
            pub_list_path = pub_list_folder_path / Path(pub_list_file_name)
            inter_df  = pd.read_excel(pub_list_path)
            concat_df = pd.concat([concat_df, inter_df])
            available_liste_conso += f" {year}"

        except FileNotFoundError:
            pass

    # Formatting and saving the concatenated dataframe in an EXCEL file
    date = str(datetime.now())[:16].replace(':', 'h')
    out_file = (f"{date} {bdd_multi_annuelle_file_alias} "
                f"{os.getlogin()}_{available_liste_conso}.xlsx")
    out_path = bibliometer_path / Path(bdd_multi_annuelle_folder_alias)
    out_file_path = out_path / Path(out_file)
    concat_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)
    wb, _ = format_page(concat_df, concat_df_title,
                        attr_keys_list=format_cols_list)
    wb.save(out_file_path)

    end_message  = f"Concatenation of consolidated pub lists saved in folder: \n  '{out_path}'"
    end_message += f"\n\n under filename: \n  '{out_file}'."
    return end_message
