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


def get_if_db(institute, org_tup, bibliometer_path):
    """Builds a dict keyyed by years and valued by a dataframe 
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
        results_df[issn_col] = unknown
        results_df[eissn_col] = unknown
        results_df = results_df[final_order_col_list]
    else:
        if results_df.empty:
            results_df[eissn_col] = unknown
        results_df = results_df[final_order_col_list[:-1]]
    sorted_results_df = results_df.sort_values(by=[journal_col])
    return sorted_results_df


def _build_only_if_doctype_df(pub_df, doctype_col, doctype_to_drop_list):
    """Builds a dataframe by keeping only rows which doc type has usually 
    an IF then droping the doc type column.
    """
    articles_df = pd.DataFrame(columns=pub_df.columns)
    for doc_type, doc_type_df in pub_df.groupby(doctype_col):
        if doc_type.upper() not in doctype_to_drop_list:
            articles_df = pd.concat([articles_df, doc_type_df])
    articles_df.drop(doctype_col, axis=1, inplace=True)
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
        issn_df.drop(pub_id_col, axis=1, inplace=True)
        issn_df[journal_upper_col] = issn_df[journal_col].astype(str).str.upper()
        issn_df.drop_duplicates(subset=[journal_upper_col], keep='first', inplace=True)
        issn_df.drop([journal_upper_col], axis=1, inplace=True)
        if_df = pd.concat([if_df, issn_df])
    return if_df


def _build_missing_issn_and_if_df(if_df, inst_issn_df, cols_tup, unknown):
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
            missing_issn_df = pd.concat([missing_issn_df, row.to_frame().T])
        elif unknown in [row_most_recent_year_if, row_corpus_year_if]:
            row_journal = row[journal_col]
            row[issn_col] = _get_id(inst_issn_df, row_journal,
                                          journal_col, issn_col,
                                          unknown)
            row[eissn_col] = _get_id(inst_issn_df, row_journal,
                                           journal_col, eissn_col,
                                           unknown)
            missing_if_df = pd.concat([missing_if_df, row.to_frame().T])
    return missing_if_df, missing_issn_df


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
    if_dict, if_available_years_list, if_most_recent_year = get_if_db(institute, org_tup,
                                                                      bibliometer_path)

    # Taking care all IF column names in if_dict are set to database_if_col_alias
    if if_db_status:
        for year in if_available_years_list:
            year_database_if_col_alias = database_if_col_alias + " " + year
            if_dict[year].rename(columns={year_database_if_col_alias: database_if_col_alias},
                                 inplace=True)

    # Replacing NAN in if_dict
    values_dict = {issn_col_alias: unknown_alias,
                   eissn_col_alias: unknown_alias,
                   database_if_col_alias: not_available_if_alias}
    for year in if_available_years_list:
        if_dict[year].fillna(value=values_dict, inplace=True)

    # Building the IF dict keyed by issn or e-issn of journals for the most recent year
    most_recent_year_if_dict = _build_if_dict(if_dict, if_most_recent_year, aliases_tup)

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
    inst_issn_df = _build_inst_issn_df(if_dict, use_col_list)

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
        current_year_if_dict = _build_if_dict(if_dict, corpus_year, aliases_tup)
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
    year_article_if_df = _build_only_if_doctype_df(year_pub_if_df, doctype_col_alias,
                                                   doctype_to_drop_list_alias)

    # Building 'year_if_df' by keeping one row for each issn
    # adding a column with number of related articles
    # then droping "Pub_id" column
    cols_tup = (pub_id_col_alias, journal_col_alias, journal_upper_col,
                pub_id_nb_col_alias, issn_col_alias)
    year_if_df = _build_issn_df(year_article_if_df, cols_tup)

    # Removing from 'year_if_df' the rows which ISSN value is not in IF database
    # and keeping them in 'year_missing_issn_df'
    cols_tup = (issn_col_alias, eissn_col_alias, most_recent_year_if_col,
                corpus_year_if_col_alias, journal_col_alias)
    return_tup = _build_missing_issn_and_if_df(year_if_df, inst_issn_df, cols_tup, unknown_alias)
    year_missing_if_df, year_missing_issn_df = return_tup

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
