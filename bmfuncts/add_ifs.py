"""Module of functions for the consolidation of the publications-list 
in terms of attributing impact factors to each publication.

"""

__all__ = ['add_if',
           'get_if_db',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.format_files import format_page
from bmfuncts.format_files import set_base_keys_list
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.rename_cols import set_if_col_names
from bmfuncts.useful_functs import concat_dfs


def _create_if_column(issn_column, if_dict, if_empty_kw):
    """Builds a dataframe column 'if_column' using the column 'issn_column' 
    of this dataframe and the dict 'if_dict'.

    The dict 'if_dict' make the link between ISSNs ('if_dict' keys) and 
    IFs ('if_dict' values). 
    The 'nan' values in the column 'if_column' are replaced by 'empty_word'.

    Args:
        issn_column (pandas serie): The column of the dataframe of interest \
        that contains the ISSNs values.
        if_dict (dict): The dict which keys are ISSNs and values are IFs.
        if_empty_kw (str): The word that will replace nan values in \
        the returned column.
    Returns:
        (pandas serie): The column of the dataframe of interest \
        that contains the IFs values.
    """
    if_column = issn_column.map(if_dict)
    if_column = if_column.fillna(if_empty_kw)
    return if_column


def _build_if_dict(if_df, if_year, args_tup):
    """Builds a dict keyed by ISSN or eISSN values and valued 
    by impact factors.

    Args:
        if_df (dataframe): Database of impact-factors.
        if_year (str): 4 digits-year key for using values from the database \
        of impact-factors.
        args_tup (tup): Tuple = (value of unknown ISSN or eISSN, \
        ISSN-column name, eISSN-column name, impact-factors-column name).
    Returns:
        (dict): dict keyed by ISSN (str) or eISSN (str) values \
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


def _build_inst_issn_df(if_db_df, cols_tup):
    """Builds a dataframe of 'use_col_list' columns composed of journal name, 
    ISSN and eISSN.

    First, a subset dataframe is built from the hierarchical dataframe 'if_db_df' 
    using 'use_col_list' columns for each year (key of 'if_db_df'). 
    Then, a single dataframe results from concatenation of these dataframes. 
    Finally, duplicates are dropped after setting unique ISSN and eISSN values 
    for each journal name.

    Args:
        if_db_df (dataframe): Hierarchical dataframe of impact-factors database \
        keyed by years.
        cols_tup (tup): Tuple of subset columns names \
        of 'if_db_df[<year>]' dataframes.
    Returns:
        (dataframe): Dataframe with 'use_col_list' columns.
    """

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN
    journal_col, issn_col, eissn_col = cols_tup

    # Setting parameters for args
    use_col_list = list(cols_tup)
    years_list = list(if_db_df.keys())

    # Initializing 'inst_issn_df'
    init_inst_issn_df = pd.DataFrame(columns=use_col_list)

    for year in years_list:
        year_sub_df = if_db_df[year][use_col_list].copy()
        init_inst_issn_df = concat_dfs([init_inst_issn_df, year_sub_df])
#                                                                          init_inst_issn_df = pd.concat([init_inst_issn_df, year_sub_df])
    init_inst_issn_df[journal_col] = init_inst_issn_df.apply(lambda row:
                                                             (row[journal_col].upper()),
                                                             axis=1)

    inst_issn_df = pd.DataFrame()
    for _ , dg in init_inst_issn_df.groupby(journal_col):

        issn_list = list(set(dg[issn_col].to_list()) - {unknown_alias})
        if not issn_list:
            issn_list = [unknown_alias]
        dg[issn_col] = issn_list[0]

        eissn_list = list(set(dg[eissn_col].to_list()) - {unknown_alias})
        if not eissn_list:
            eissn_list = [unknown_alias]
        dg[eissn_col] = eissn_list[0]

        inst_issn_df = concat_dfs([inst_issn_df, dg.iloc[:1]])
#                                                                            inst_issn_df = pd.concat([inst_issn_df, dg.iloc[:1]])

    inst_issn_df = inst_issn_df.sort_values(by=[journal_col])
    inst_issn_df = inst_issn_df.drop_duplicates()

    return inst_issn_df


def get_if_db(institute, org_tup, bibliometer_path):
    """Builds a dict keyed by years and valued by a dataframe 
    of impact-factor per journal for the Institute.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
    Returns:
        (tup): (impact-factors (dict), \
        available-years of impact-factors in the dict (list), \
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
    if_dict = pd.read_excel(if_path, sheet_name=None)

    # Setting list of years for which IF are available
    if_available_years_list = list(if_dict.keys())

    # Setting the most recent year for which IF are available
    if_most_recent_year = if_available_years_list[-1]

    return if_dict, if_available_years_list, if_most_recent_year


def _fullfill_issn(corpus_df, issn_df, empty_kw, col_tup):
    """Fills the empty values in the 'issn_col' column 
    in the 'corpus_df' dataframe.

    For that it uses the ISSN or eISSN' available in the 'issn_df' dataframe.

    Args:
        corpus_df (dataframe): Corpus of publications to be updated.
        issn_df (dataframe): Data of journals with their ISSN and eISSN.
        empty_kw (str): Value of empty ISSN or eISSN.
        col_tup (tup): Tuple of columns names = (journal name, ISSN, eISSN).
    Returns:
        (dataframe): Updated dataframe.
    """

    # Setting parameters from args
    journal_col, issn_col, eissn_col = col_tup

    for corpus_idx, corpus_row in corpus_df.iterrows():
        if corpus_row[issn_col]!=empty_kw:
            continue
        corpus_journal = corpus_row[journal_col].upper()
        for _, issn_row in issn_df.iterrows():
            issn_journal = issn_row[journal_col].upper()
            if corpus_journal!=issn_journal:
                continue
            if issn_row[issn_col]!=empty_kw:
                corpus_df.loc[corpus_idx, issn_col] = issn_row[issn_col]
            elif issn_row[eissn_col]!=empty_kw:
                corpus_df.loc[corpus_idx, issn_col] = issn_row[eissn_col]
    return corpus_df


def _get_id(issn_df, journal_name, journal_col, id_col, empty_kw):
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
    id_lower = empty_kw
    if not id_lower_df.empty:
        id_lower = id_lower_df.to_list()[0]
    id_upper_df = issn_df[issn_df[journal_col]==journal_name.upper()][id_col]
    id_upper = empty_kw
    if not id_upper_df.empty:
        id_upper = id_upper_df.to_list()[0]
    journal_id = list(set([id_lower,id_upper]) - set([empty_kw]))[0]
    return journal_id


def _format_missing_df(results_df, common_args_tup, empty_kw, add_cols):
    """Formats the 'results_df' dataframe with final column names.

    Args:
        results_df (dataframe): Corpus of publications to be updated.
        common_args_tup (tup): Tuple of columns name (str) = (year (4 digits), \
        corpus-year impact-factor, impact-factors most-recent year, journal-name, \
        ISSN, eISNN, number of publications, impact-factors year, ISSN in \
        'result_df' dataframe).
        empty_kw (str): Value of empty ISSN or eISSN in 'results_df' dataframe.
        add_cols (bool): True if suplementary columns for ISSN and eISSN are to be \
        filled with empty_kw values.
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
    results_df = results_df.rename(columns={year_col: final_year_col,
                                            corpus_year_if_col: year_db_if_col})
    if add_cols:
        results_df = results_df.rename(columns={issn_col: corpus_issn_col})
        results_df[issn_col] = empty_kw
        results_df[eissn_col] = empty_kw
        results_df = results_df[final_order_col_list]
    else:
        if results_df.empty:
            results_df[eissn_col] = empty_kw
        results_df = results_df[final_order_col_list[:-1]]
    sorted_results_df = results_df.sort_values(by=[journal_col])
    return sorted_results_df


def _build_only_if_doctype_df(org_tup, pub_df, doctype_col):
    """Builds a dataframe by keeping only rows which doc type has usually 
    an IF then droping the doc type column.
    """
    # Setting global aliase
    doc_type_dict_alias = pg.DOC_TYPE_DICT

    # Setting list of document types to drop (usually no IF attributed)
    no_if_doctype_keys_list = org_tup[6]
    no_if_doctype = sum([doc_type_dict_alias[x] for x in no_if_doctype_keys_list] , [])

    # Building 'year_article_if_df' by keeping only rows which doc type has usually an IF
    # then droping the doc type column
    doctype_to_drop_list = [x.upper() for x in no_if_doctype]

    articles_df = pd.DataFrame(columns=pub_df.columns)
    for doc_type, doc_type_df in pub_df.groupby(doctype_col):
        if doc_type.upper() not in doctype_to_drop_list:
            articles_df = concat_dfs([articles_df, doc_type_df])
#                                                                articles_df = pd.concat([articles_df, doc_type_df])
    articles_df = articles_df.drop(doctype_col, axis=1)
    return articles_df


def _build_issn_df(article_df, cols_tup):
    """Builds a dataframe by keeping one row for each issn adding a column 
    with number of related articles then droping "Pub_id" column.
    """
    pub_id_col, journal_col, journal_upper_col, pub_id_nb_col, issn_col = cols_tup
    if_df = pd.DataFrame(columns=article_df.columns.to_list() [1:] \
                         + [pub_id_nb_col])
    for _, issn_df in article_df.groupby(issn_col):
        pub_id_nb = len(issn_df)
        issn_df[pub_id_nb_col] = pub_id_nb
        issn_df = issn_df.drop(pub_id_col, axis=1)
        issn_df[journal_upper_col] = issn_df[journal_col].astype(str).str.upper()
        issn_df = issn_df.drop_duplicates(subset=[journal_upper_col], keep='first')
        issn_df = issn_df.drop([journal_upper_col], axis=1)
        if_df = concat_dfs([if_df, issn_df])
#                                                                    if_df = pd.concat([if_df, issn_df])
    return if_df


def _build_missing_issn_and_if_df(if_df, inst_issn_df, cols_tup, empty_kw):
    """Builds a dataframe 'missing_if_df' by removing from 'if_df' the rows 
    which ISSN value is not in IF database and keeping them in the dataframe 
    'missing_issn_df'."""
    (issn_col, eissn_col, most_recent_year_if_col,
     corpus_year_if_col, journal_col) = cols_tup
    missing_issn_df = pd.DataFrame(columns=if_df.columns)
    missing_if_df = pd.DataFrame(columns=if_df.columns)
    inst_issn_list = inst_issn_df[issn_col].to_list()
    inst_eissn_list = inst_issn_df[eissn_col].to_list()
    for _, row in if_df.iterrows():
        row_issn = row[issn_col]
        row_most_recent_year_if = row[most_recent_year_if_col]
        row_corpus_year_if = row[corpus_year_if_col]
        if row_issn not in inst_issn_list and row_issn not in inst_eissn_list:
            missing_issn_df = concat_dfs([missing_issn_df, row.to_frame().T])
#                                                                           missing_issn_df = pd.concat([missing_issn_df, row.to_frame().T])
        elif empty_kw in [row_most_recent_year_if, row_corpus_year_if]:
            row_journal = row[journal_col]
            row[issn_col] = _get_id(inst_issn_df, row_journal,
                                    journal_col, issn_col,
                                    empty_kw)
            row[eissn_col] = _get_id(inst_issn_df, row_journal,
                                     journal_col, eissn_col,
                                     empty_kw)
            missing_if_df = concat_dfs([missing_if_df, row.to_frame().T])
#                                                                        missing_if_df = pd.concat([missing_if_df, row.to_frame().T])
    return missing_if_df, missing_issn_df


def _format_and_save_add_if_dfs(institute, org_tup, dfs_tup, out_cols_tup,
                                empty_kw, out_paths_tup):
    # Setting parameters from args
    corpus_df, year_missing_issn_df, year_missing_if_df = dfs_tup
    out_file_path, missing_issn_path, missing_if_path = out_paths_tup

    # Formatting 'year_missing_issn_df' and 'year_missing_if_df'
    sorted_year_missing_issn_df = _format_missing_df(
        year_missing_issn_df, out_cols_tup, empty_kw, add_cols=True)
    sorted_year_missing_if_df = _format_missing_df(
        year_missing_if_df, out_cols_tup, empty_kw, add_cols=False)

    # Setting useful parameters for use of 'format_page' function
    common_df_title = pg.DF_TITLES_LIST[0]
    format_cols_list = set_base_keys_list(institute, org_tup)

    # Formatting and saving 'corpus_df' as openpyxl file at full path 'out_file_path'
    wb, _ = format_page(corpus_df, common_df_title,
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


def _clean_if_dict(institute, org_tup, bibliometer_path, aliases_tup):
    # Setting parameters from args
    if_db_status = org_tup[5]
    (empty_kw, issn_col, eissn_col,
     database_if_col, not_available_if) = aliases_tup

    # Getting the df of the IFs database
    if_dict, if_available_years_list, if_most_recent_year = get_if_db(institute, org_tup,
                                                                      bibliometer_path)

    # Taking care all IF column names in if_dict are set to database_if_col
    if if_db_status:
        for year in if_available_years_list:
            year_database_if_col = database_if_col + " " + year
            if_dict[year] = if_dict[year].rename(columns={year_database_if_col: database_if_col})

    # Replacing NAN in if_dict
    values_dict = {issn_col: empty_kw,
                   eissn_col: empty_kw,
                   database_if_col: not_available_if}
    for year in if_available_years_list:
        if_dict[year] = if_dict[year].fillna(value=values_dict)

    return if_dict, if_available_years_list, if_most_recent_year


def _clean_corpus_df(in_file_path, if_dict, cols_tup, recast_cols_tup, empty_kw):
    # Setting parameters from args
    base_col_list, otp_col, otp_col_new, year_col_alias = recast_cols_tup

    # Getting the df where to add IFs
    corpus_df = pd.read_excel(in_file_path)

    # Recasting column names
    new_base_col_list = list(
        map(lambda x: x.replace(otp_col, otp_col_new),
            base_col_list)
    )
    if otp_col in corpus_df.columns:
        corpus_df = corpus_df.rename(columns={otp_col : otp_col_new})

    # Setting type of values in 'year_col_alias' as string
    corpus_df = corpus_df.astype({year_col_alias: str})

    # Initializing 'corpus_df_bis' as copy of 'corpus_df'
    corpus_df_bis = corpus_df[new_base_col_list].copy()

    # Getting the df of ISSN and eISSN database of the institut
    inst_issn_df = _build_inst_issn_df(if_dict, cols_tup)

    # Filling unknown ISSN in 'corpus_df_bis' using 'inst_issn_df'
    # through _fullfill_issn function
    corpus_df_bis = _fullfill_issn(corpus_df_bis, inst_issn_df, empty_kw, cols_tup)
    return corpus_df_bis, inst_issn_df


def _add_if_cols(corpus_df, if_dict, if_cols_tup, aliases_tup,
                 most_recent_year_if_dict, empty_kws_tup, years_tup):
    # Setting parameters from args
    not_available_if, if_empty_kw = empty_kws_tup
    if_available_years_list, corpus_year = years_tup
    most_recent_year_if_col, corpus_year_if_col, issn_col = if_cols_tup

    # Adding 'most_recent_year_if_col' column to 'corpus_df'
    # with values defined by internal function '_create_if_column'
    corpus_df[most_recent_year_if_col] = _create_if_column(corpus_df[issn_col],
                                                           most_recent_year_if_dict,
                                                           if_empty_kw)

    # Adding 'corpus_year_if_col' column to 'corpus_df'
    if corpus_year in if_available_years_list:
        # with values defined by internal function '_create_if_column'
        # Building the IF dict keyed by issn or e-issn of journals for the corpus year
        current_year_if_dict = _build_if_dict(if_dict, corpus_year, aliases_tup)
        corpus_df[corpus_year_if_col] = _create_if_column(corpus_df[issn_col],
                                                          current_year_if_dict,
                                                          if_empty_kw)
    else:
        # with 'not_available_if' value
        corpus_df[corpus_year_if_col] = not_available_if
    return corpus_df


def add_if(institute, org_tup, bibliometer_path, paths_tup, corpus_year):

    """Adds two new columns containing impact factors to the corpus 
    dataframe 'corpus_df' got from a file which full path is 'in_file_path'.

    First, useful column names are got through the `set_final_col_names` 
    and `set_if_col_names` functions imported from the `bmfuncts.rename_cols` 
    module. 
    The two added columns are named through 'corpus_year_if_col_alias' 
    and 'most_recent_year_if_col'. 
    The impact factors are got using `get_if_db` function that returns 
    in particular the dict 'if_dict' of impact-factors database. 
    The column 'corpus_year_if_col_alias' is filled with the impact-factors 
    values of the corpus year 'corpus_year' if available in the 'if_dict' dict, 
    otherwise the values are set to 'not_available_if_alias' value. 
    The column 'most_recent_year_if_col' is filled with the impact-factors 
    values of the most recent year available in the 'if_dict' dict. 
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
        paths_tup (tup): Tuple = (full path to get the corpus data, \
        full path to save the corpus data with the impact-factors information added, \
        full path to save the missing impact-factors information, \
        full path to save the missing ISSNs information).
        corpus_year (str): Year (4 digits) of the corpus to be appended with the two \
        new impact-factors columns.
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
    not_available_if_alias = pg.NOT_AVAILABLE_IF
    if_empty_kw_alias = pg.FILL_EMPTY_KEY_WORD
    empty_kw_alias = pg.FILL_EMPTY_KEY_WORD
    outside_if_analysis_alias = pg.OUTSIDE_ANALYSIS

    # Setting tuples for passing args
    cols_tup = (journal_col_alias, issn_col_alias, eissn_col_alias)
    aliases_tup = (empty_kw_alias, issn_col_alias, eissn_col_alias, database_if_col_alias)
    more_aliases_tup = aliases_tup + (not_available_if_alias,)

    return_tup = _clean_if_dict(institute, org_tup, bibliometer_path, more_aliases_tup)
    if_dict, if_available_years_list, if_most_recent_year = return_tup

    # Building the IF dict keyed by issn or e-issn of journals for the most recent year
    most_recent_year_if_dict = _build_if_dict(if_dict, if_most_recent_year, aliases_tup)

    # Setting local column names
    most_recent_year_if_col = current_if_col_alias + ', ' + if_most_recent_year
    year_db_if_col = database_if_col_alias + ' ' + corpus_year
    journal_upper_col = journal_col_alias + '_Upper'

    # Cleaning corpus data
    recast_cols_tup = (base_col_list, otp_col_alias, otp_col_new_alias, year_col_alias)
    corpus_df, inst_issn_df = _clean_corpus_df(in_file_path, if_dict, cols_tup,
                                               recast_cols_tup, empty_kw_alias)

    # Adding Ifs cols to 'corpus_df'
    if_cols_tup = (most_recent_year_if_col, corpus_year_if_col_alias, issn_col_alias)
    empty_kws_tup = (not_available_if_alias, if_empty_kw_alias)
    years_tup = (if_available_years_list, corpus_year)
    corpus_df = _add_if_cols(corpus_df, if_dict, if_cols_tup, aliases_tup,
                             most_recent_year_if_dict, empty_kws_tup, years_tup)

    # Sorting 'corpus_df' pub_id values
    corpus_df = corpus_df.sort_values(by=[pub_id_col_alias])

    # Building 'year_pub_if_df' with subset of 'corpus_df' columns
    subsetcols = [pub_id_col_alias,
                  year_col_alias,
                  journal_col_alias,
                  doctype_col_alias,
                  issn_col_alias,
                  most_recent_year_if_col,
                  corpus_year_if_col_alias,]
    year_pub_if_df = corpus_df[subsetcols].copy()

    # Building 'year_article_if_df' by keeping only rows which doc type has usually an IF
    # then droping the doc type column
    year_article_if_df = _build_only_if_doctype_df(org_tup, year_pub_if_df, doctype_col_alias)

    # Building 'year_if_df' by keeping one row for each issn
    # adding a column with number of related articles
    # then droping "Pub_id" column
    year_if_cols_tup = (pub_id_col_alias, journal_col_alias, journal_upper_col,
                        pub_id_nb_col_alias, issn_col_alias)
    year_if_df = _build_issn_df(year_article_if_df, year_if_cols_tup)

    # Removing from 'year_if_df' the rows which ISSN value is not in IF database
    # and keeping them in 'year_missing_issn_df'
    missing_infos_cols_tup = (issn_col_alias, eissn_col_alias, most_recent_year_if_col,
                              corpus_year_if_col_alias, journal_col_alias)
    return_tup = _build_missing_issn_and_if_df(year_if_df, inst_issn_df,
                                               missing_infos_cols_tup, empty_kw_alias)
    year_missing_if_df, year_missing_issn_df = return_tup

    if_database_complete = True
    if not year_missing_issn_df.empty or not year_missing_if_df.empty:
        if_database_complete = False
    else:
        # replace remaining unknown IF values by 'not_available_if_alias' value
        corpus_df = corpus_df.replace({most_recent_year_if_col: if_empty_kw_alias,
                                       corpus_year_if_col_alias: if_empty_kw_alias},
                                      outside_if_analysis_alias)

    # Setting args tups for '_format_and_save_add_if_dfs' function
    dfs_tup = (corpus_df, year_missing_issn_df, year_missing_if_df)
    out_cols_tup = (year_col_alias, corpus_year_if_col_alias,
                    most_recent_year_if_col,
                    journal_col_alias, issn_col_alias, eissn_col_alias,
                    pub_id_nb_col_alias, year_db_if_col,
                    corpus_issn_col_alias)
    out_paths_tup = (out_file_path, missing_issn_path, missing_if_path)

    # Formatting and saving the built dataframes as openpyxl workbooks
    _format_and_save_add_if_dfs(institute, org_tup, dfs_tup, out_cols_tup,
                                empty_kw_alias, out_paths_tup)

    end_message = f"IFs added for year {corpus_year} in file : \n  '{out_file_path}'"
    return end_message, if_database_complete
