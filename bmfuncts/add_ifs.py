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
import bmfuncts.pub_globals as bm_pg
from bmfuncts.format_files import format_page
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.rename_cols import set_if_col_names
from bmfuncts.useful_functs import concat_dfs


def _set_add_ifs_col_dic(institute, org_tup, corpus_year):
    """Builds a dict setting selected columns names for the process
    of IFs attribution.

    This is done through the combination of column names resulting 
    from the `set_final_col_names` and `set_if_col_names` functions 
    imported from the `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        corpus_year (str): 4 digits-year of the corpus.
    Returns:
        (tup): The built dict and the full list of final column names \
        got from the `set_final_col_names` function.
    """
    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    if_maj_col_dic = set_if_col_names(institute, org_tup)

    add_ifs_col_dic = {'year_col'          : final_col_dic['corpus_year'],
                       'pub_id_col'        : final_col_dic['pub_id'],
                       'doctype_col'       : final_col_dic['doc_type'],
                       'pub_id_nb_col'     : bm_pg.COL_NAMES_BONUS['pub number'],
                       'journal_col'       : final_col_dic['journal'],
                       'issn_col'          : final_col_dic['issn'],
                       'eissn_col'         : bm_pg.COL_NAMES_BONUS['e-ISSN'],
                       'corpus_issn_col'   : bm_pg.COL_NAMES_BONUS["database ISSN"],
                       'current_if_col'    : if_maj_col_dic['current_if'],
                       'corpus_year_if_col': if_maj_col_dic['pub_year_if'],
                       'database_if_col'   : bm_pg.COL_NAMES_BONUS['IF clarivate'],
                       'otp_col'           : final_col_dic['otp'],
                       'new_otp_col'       : bm_pg.COL_NAMES_BONUS['final OTP'],
                      }
    add_ifs_col_dic['final_year_col'] = add_ifs_col_dic['year_col'][0:5]
    add_ifs_col_dic['journal_upper_col'] = f"{add_ifs_col_dic['journal_col']}_Upper"
    add_ifs_col_dic['year_db_if_col'] = f"{add_ifs_col_dic['database_if_col']} {corpus_year}"

    base_col_list = list(final_col_dic.values())
    return add_ifs_col_dic, base_col_list


def get_if_db(institute, org_tup, wf_path):
    """Builds a dict keyed by years and valued by a dataframe 
    of impact-factor per journal for the Institute.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
    Returns:
        (tup): (impact-factors (dict), available-years of impact-factors \
        in the dict (list), most-recent year (4-digits str) of available \
        impact-factors).
    """
    ## Setting institute parameters
    if_db_status = org_tup[5]

    # Setting useful aliases
    if_root_folder_alias = bm_pg.ARCHI_IF["root"]
    if_filename_alias = bm_pg.ARCHI_IF["all IF"]

    # Setting institute value for IFs file name
    if if_db_status:
        if_filename = institute + bm_pg.ARCHI_IF["institute_if_all_years"]
    else:
        if_filename = if_filename_alias

    # Setting useful paths
    if_root_folder_path = wf_path / Path(if_root_folder_alias)
    if_path = if_root_folder_path / Path(if_filename)

    # Getting the df of the IFs database
    if_dict = pd.read_excel(if_path, sheet_name=None)

    # Setting list of years for which IF are available
    if_available_years_list = list(if_dict.keys())

    # Setting the most recent year for which IF are available
    if_most_recent_year = if_available_years_list[-1]

    return if_dict, if_available_years_list, if_most_recent_year


def _clean_if_dict(institute, org_tup, wf_path, add_ifs_col_dic, empty_kws_list):
    """Recast the IFs data by checking the names of IFs columns and completing 
    empty values in ISSNs, eISSNs and IFs columns with ad-hoc words.

    The starting IFs data are got through the `get_if_db` function of this module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        wf_path (path): Full path to working folder.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
        empty_kws_list (list): Composed of the 'UNKNOWN' global imported \
        from the `BiblioParsing` package and of the 'NOT_AVAILABLE' global \
        imported from the `bmfuncts.pub_globals` module.
    returns:
        (tup): (The recast IFs data (dict keyed by years and valued \
        by dataframes),  the list of available years (4-digits strings) \
        of IFs data, the most recent year (4-digits string) of IFs data).
    """
    # Setting institute parameters from args
    if_db_status = org_tup[5]

    # Setting parameters value from args
    col_keys = ['database_if_col', 'issn_col', 'eissn_col']
    database_if_col, issn_col, eissn_col = [add_ifs_col_dic[key] for key in col_keys]
    unknown_kw, not_available_kw = empty_kws_list

    # Getting the df of the IFs database
    ifs_return_tup = get_if_db(institute, org_tup, wf_path)
    if_dict, if_available_years_list, if_most_recent_year = ifs_return_tup

    # Taking care all IF column names in if_dict are set to database_if_col
    if if_db_status:
        for year in if_available_years_list:
            year_database_if_col = database_if_col + " " + year
            if_dict[year] = if_dict[year].rename(columns={year_database_if_col: database_if_col})

    # Replacing NAN in if_dict
    values_dict = {issn_col: unknown_kw,
                   eissn_col: unknown_kw,
                   database_if_col: not_available_kw}
    for year in if_available_years_list:
        if_dict[year] = if_dict[year].fillna(value=values_dict)

    return if_dict, if_available_years_list, if_most_recent_year


def _build_if_dict(if_dict, if_year, add_ifs_col_dic, unknown_kw):
    """Builds a dict keyed by ISSN or eISSN values and valued 
    by impact factors.

    Args:
        if_dict (dict): Database of impact-factors.
        if_year (str): 4 digits-year key for using values from \
        the database of impact-factors.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
        unknown_kw (str): The word to identifie unknown values.
    Returns:
        (dict): Dict keyed by ISSN (str) or eISSN (str) values \
        and valued by impact factors (float).
    """
    # Setting parameters value from args
    col_keys = ['database_if_col', 'issn_col', 'eissn_col']
    if_col, issn_col, eissn_col = [add_ifs_col_dic[key] for key in col_keys]

    issn_if_dict = dict(zip(if_dict[if_year][issn_col],
                            if_dict[if_year][if_col]))
    if unknown_kw in issn_if_dict:
        del issn_if_dict[unknown_kw]
    eissn_if_dict = {}
    if eissn_col in list(if_dict[if_year].columns):
        eissn_if_dict = dict(zip(if_dict[if_year][eissn_col],
                                 if_dict[if_year][if_col]))
        if unknown_kw in eissn_if_dict:
            del eissn_if_dict[unknown_kw]
    year_if_dict = {**issn_if_dict, **eissn_if_dict}
    return year_if_dict


def _build_institute_issn_df(if_dict, journal_id_cols_list, unknown_kw):
    """Builds data making the link between journal names and ISSNs and 
    eISSNs.

    First, a subset dataframe is built from the dict 'if_dict' 
    using 'journal_id_cols_list' columns for each year (key of 'if_dict'). 
    Then, a single dataframe results from concatenation of these dataframes. 
    Finally, duplicates are dropped after setting unique ISSN and eISSN values 
    for each journal name.

    Args:
        if_dict (dict): Impact-factors data (dataframes) keyed by years.
        journal_id_cols_list (list): Subset columns names composed \
        of journal names, ISSNs and eISSNs.
        unknown_kw (str): The word to identify unknown values.
    Returns:
        (dataframe): Data of journals names (str) with their ISSN \
        and eISSN IDs (str).
    """
    # Setting parameters from args
    journal_col, issn_col, eissn_col = journal_id_cols_list
    if_available_years_list = list(if_dict.keys())

    # Initializing 'institute_issn_df'
    init_institute_issn_df = pd.DataFrame(columns=journal_id_cols_list)

    for year in if_available_years_list:
        year_sub_df = if_dict[year][journal_id_cols_list].copy()
        init_institute_issn_df = concat_dfs([init_institute_issn_df, year_sub_df])
    init_institute_issn_df[journal_col] = init_institute_issn_df.apply(lambda row:
                                                                       (row[journal_col].upper()),
                                                                       axis=1)
    institute_issn_df = pd.DataFrame()
    for _, dg in init_institute_issn_df.groupby(journal_col):

        issn_list = list(set(dg[issn_col].to_list()) - {unknown_kw})
        if not issn_list:
            issn_list = [unknown_kw]
        dg[issn_col] = issn_list[0]

        eissn_list = list(set(dg[eissn_col].to_list()) - {unknown_kw})
        if not eissn_list:
            eissn_list = [unknown_kw]
        dg[eissn_col] = eissn_list[0]

        institute_issn_df = concat_dfs([institute_issn_df, dg.iloc[:1]])

    institute_issn_df = institute_issn_df.sort_values(by=[journal_col])
    institute_issn_df = institute_issn_df.drop_duplicates()
    return institute_issn_df


def _fullfill_issn(corpus_df, issn_df, journal_id_cols_list, unknown_kw):
    """Fills the empty values in the 'issn_col' column in the 'corpus_df' 
    dataframe.

    For that it uses the ISSN or eISSN' available in the 'issn_df' dataframe.

    Args:
        corpus_df (dataframe): Corpus of publications to be updated.
        issn_df (dataframe): Data of journals with their ISSN and eISSN.
        journal_id_cols_list (list): Subset columns names composed \
        of journal names, ISSNs and eISSNs.
        unknown_kw (str): The word to identify unknown values.
    Returns:
        (dataframe): The updated dataframe.
    """
    # Setting parameters from args
    journal_col, issn_col, eissn_col = journal_id_cols_list

    for corpus_idx, corpus_row in corpus_df.iterrows():
        if corpus_row[issn_col]!=unknown_kw:
            continue
        corpus_journal = corpus_row[journal_col].upper()
        for _, issn_row in issn_df.iterrows():
            issn_journal = issn_row[journal_col].upper()
            if corpus_journal!=issn_journal:
                continue
            if issn_row[issn_col]!=unknown_kw:
                corpus_df.loc[corpus_idx, issn_col] = issn_row[issn_col]
            elif issn_row[eissn_col]!=unknown_kw:
                corpus_df.loc[corpus_idx, issn_col] = issn_row[eissn_col]
    return corpus_df


def _clean_corpus_df(in_file_path, if_dict, add_ifs_col_tup, unknown_kw):
    """Recast the corpus data by renaming OTPs column and completing 
    empty values in ISSN column.

    The ISSNs completion is donne through the `_fullfill_issn` internal function 
    using the ISSN provided by the `_build_institute_issn_df` internal function.

    Args:
        in_file_path (path): The full path to get the corpus data.
        if_dict (dict): Impact-factors data (dataframes) keyed by years.
        add_ifs_col_tup (tup): (Useful columns names (dict) for the IFs-attribution process \
        as set through the `_set_add_ifs_col_dic` internal function, the full list (list) of \
        final column names got from the `set_final_col_names` function imported from \
        the `bmfuncts.rename_cols` module).
        unknown_kw (str): The word to identify unknown values.
    Returns:
        (tup): (Recast corpus data (dataframe), Data (dataframe) of \
        journals with their ISSN and eISSN IDs).
    """
    # Setting parameters value from args
    add_ifs_col_dic, base_col_list = add_ifs_col_tup
    col_keys = ['journal_col', 'issn_col', 'eissn_col']
    journal_id_cols_list = [add_ifs_col_dic[key] for key in col_keys]

    # Getting the df where to add IFs
    corpus_df = pd.read_excel(in_file_path)

    # Setting type of values in 'year_col' as string
    year_col = add_ifs_col_dic['year_col']
    corpus_df = corpus_df.astype({year_col: str})

    # Recasting column names
    otp_col, new_otp_col = add_ifs_col_dic['otp_col'], add_ifs_col_dic['new_otp_col']
    new_base_col_list = [x.replace(otp_col, new_otp_col) for x in base_col_list]
    if otp_col in corpus_df.columns:
        corpus_df = corpus_df.rename(columns={otp_col: new_otp_col})

    # Initializing 'corpus_df_bis' as copy of 'corpus_df'
    corpus_df_bis = corpus_df[new_base_col_list].copy()

    # Getting the df of ISSN and eISSN database of the institute
    institute_issn_df = _build_institute_issn_df(if_dict, journal_id_cols_list, unknown_kw)

    # Filling unknown ISSN in 'corpus_df_bis' using 'institute_issn_df'
    # through _fullfill_issn function
    corpus_df_bis = _fullfill_issn(corpus_df_bis, institute_issn_df, journal_id_cols_list,
                                   unknown_kw)
    return corpus_df_bis, institute_issn_df


def _create_if_column(issn_column, year_if_dict, unknown_kw):
    """Builds a dataframe column 'if_column' using the column 'issn_column' 
    of this dataframe and the dict 'year_if_dict'.

    The dict 'year_if_dict' make the link between ISSNs ('year_if_dict' keys) and 
    IFs ('year_if_dict' values) of a year. 
    The 'nan' values in the column 'if_column' are replaced by the 'unknown_kw' word .

    Args:
        issn_column (pandas series): The column of the dataframe of interest \
        that contains the ISSNs values.
        year_if_dict (dict): The dict which keys are ISSNs and values are IFs of a year.
        unknown_kw (str): The word that will replace nan values in \
        the returned column.
    Returns:
        (pandas series): The column of the dataframe of interest \
        that contains the IFs values.
    """
    if_column = issn_column.map(year_if_dict)
    if_column = if_column.fillna(unknown_kw)
    return if_column


def _add_if_cols(corpus_df, if_dicts_list, corpus_year, add_ifs_col_dic, empty_kws_list):
    """Adds two IF columns to the corpus data through the `_create_if_column` 
    internal function.

    The names of the new columns are given by the 'add_ifs_col_dic' dict 
    at keys 'most_recent_year_if_col' and 'corpus_year_if_col'.

    Args:
        corpus_df (dataframe): The corpus data as built through \
        the `_clean_corpus_df` internal function.
        if_dicts_list (list): Composed of the IFs data built through \
        the `_clean_if_dict` internal function and of the IFs data \
        built through the `_build_if_dict` internal function.
        corpus_year (str): The 4-digits year of the corpus.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
        empty_kws_list (list): Composed of the 'UNKNOWN' global imported \
        from the `BiblioParsing` package and of the 'NOT_AVAILABLE' global \
        imported from the `bmfuncts.pub_globals` module.
    Returns:
        (dataframe): The corpus data added with the two IF columns.
    """
    # Setting parameters value from args
    if_dict, most_recent_year_if_dict = if_dicts_list
    if_available_years_list = list(if_dict.keys())
    col_keys = ['most_recent_year_if_col', 'corpus_year_if_col', 'issn_col']
    (most_recent_year_if_col,
     corpus_year_if_col, issn_col) = [add_ifs_col_dic[key] for key in col_keys]
    unknown_kw, not_available_kw = empty_kws_list

    # Adding 'most_recent_year_if_col' column to 'corpus_df'
    # with values defined by internal function '_create_if_column'
    corpus_df[most_recent_year_if_col] = _create_if_column(corpus_df[issn_col],
                                                           most_recent_year_if_dict,
                                                           unknown_kw)

    # Adding 'corpus_year_if_col' column to 'corpus_df'
    if corpus_year in if_available_years_list:
        # with values defined by internal function '_create_if_column'
        # Building the IF dict keyed by issn or e-issn of journals for the corpus year
        current_year_if_dict = _build_if_dict(if_dict, corpus_year, add_ifs_col_dic,
                                              unknown_kw)
        corpus_df[corpus_year_if_col] = _create_if_column(corpus_df[issn_col],
                                                          current_year_if_dict,
                                                          unknown_kw)
    else:
        # with 'not_available_kw' value
        corpus_df[corpus_year_if_col] = not_available_kw
    return corpus_df


def _build_only_if_doctype_df(org_tup, corpus_df, add_ifs_col_dic):
    """Builds data by keeping only rows which document type has usually 
    an IF then dropping the doc type column.

    The document type that may be attributed an IF are given through the 
    `DOC_TYPE_DICT` global imported from the `bmfunct.pub_globals` module.

    Args:
        org_tup (tup): Contains Institute parameters.
        corpus_df (dataframe): The corpus data as updated through \
        the `_add_if_cols` internal function.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
    Returns:
        (dataframe): The corpus data with only the documents \
        that may be attributed impact_factors. 
    """
    # Setting parameters value from args
    col_keys = ['pub_id_col', 'year_col', 'journal_col', 'doctype_col', 'issn_col',
                'most_recent_year_if_col', 'corpus_year_if_col']
    subsetcols = [add_ifs_col_dic[key] for key in col_keys]
    doctype_col = add_ifs_col_dic['doctype_col']

    # Building 'year_pub_if_df' with subset of 'corpus_df' columns
    year_pub_if_df = corpus_df[subsetcols].copy()

    # Setting global alias
    doc_type_dict_alias = bm_pg.DOC_TYPE_DICT

    # Setting list of document types to drop (usually no IF attributed)
    no_if_doctype_keys_list = [x.upper() for x in org_tup[6]]
    no_if_doctype = sum([doc_type_dict_alias[x.lower()] for x in no_if_doctype_keys_list], [])

    # Building 'year_article_if_df' by keeping only rows which doc type has usually an IF
    # then dropping the doc type column
    doctype_to_drop_list = [x.upper() for x in no_if_doctype]

    articles_df = pd.DataFrame(columns=subsetcols)
    for doc_type, doc_type_df in year_pub_if_df.groupby(doctype_col):
        if doc_type.upper() not in doctype_to_drop_list:
            articles_df = concat_dfs([articles_df, doc_type_df])
    articles_df = articles_df.drop(doctype_col, axis=1)
    return articles_df


def _build_issn_df(article_df, add_ifs_col_dic):
    """Builds data by keeping one row for each issn adding a column 
    with number of related articles then dropping "Pub_id" column.

    Args:
        article_df (dataframe): The corpus data with only the documents \
        that may be attributed impact_factors.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
    Returns:
        (dataframe): The built data.
    """
    # Setting parameters value from args
    col_keys = ['pub_id_col', 'journal_col', 'journal_upper_col',
                'pub_id_nb_col', 'issn_col']
    (pub_id_col, journal_col, journal_upper_col,
     pub_id_nb_col, issn_col) = [add_ifs_col_dic[key] for key in col_keys]

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
    return if_df


def _get_id(issn_df, journal_name, journal_col, id_col, unknown_kw):
    """Sets a unique journal name for the ISSN value at 'journal_name' 
    key in 'issn_df' dataframe.

    Args:
        issn_df (dataframe): Data of journals with their ISSN and eISSN.
        journal_name (str): Name of journal for which the unique name will be defined.
        journal_col (str): Name of the journal-names column in the 'issn_df' dataframe.
        id_col (str): Name of the ISSN or eISSN column to be used in the 'issn_df' dataframe.
        unknown_kw (str): The word to identify unknown values.
    Returns:
        (str): Unified journal name.
    """
    # Setting parameters from args
    id_lower_df = issn_df[issn_df[journal_col]==journal_name.lower()][id_col]
    id_lower = unknown_kw
    if not id_lower_df.empty:
        id_lower = id_lower_df.to_list()[0]
    id_upper_df = issn_df[issn_df[journal_col]==journal_name.upper()][id_col]
    id_upper = unknown_kw
    if not id_upper_df.empty:
        id_upper = id_upper_df.to_list()[0]
    id_journal = list({id_lower, id_upper} - {unknown_kw})[0]
    return id_journal


def _build_missing_issn_and_if_df(if_df, institute_issn_df, add_ifs_col_dic, unknown_kw):
    """Builds a dataframe 'missing_if_df' by removing from 'if_df' the rows 
    which ISSN value is not in IF database and keeping them in the dataframe 
    'missing_issn_df'.

    The unknown values are identified by the 'unknown_kw' word.

    Args:
        if_df (dataframe): The built data through the `_build_issn_df` \
        internal function.
        institute_issn_df (dataframe): The built data through the \
        `_clean_corpus_df` internal function.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
        unknown_kw (str): The word to identify unknown values.
    Returns:
        (tup): (Data (dataframe) of missing ISSNs in corpus data, Data (dataframe) \
        of missing IFs in corpus data).
    """
    # Setting parameters value from args
    col_keys = ['journal_col', 'issn_col', 'eissn_col',
                'most_recent_year_if_col', 'corpus_year_if_col']
    (journal_col, issn_col, eissn_col, most_recent_year_if_col,
     corpus_year_if_col) = [add_ifs_col_dic[key] for key in col_keys]

    missing_issn_df = pd.DataFrame(columns=if_df.columns)
    missing_if_df = pd.DataFrame(columns=if_df.columns)
    institute_issn_list = institute_issn_df[issn_col].to_list()
    institute_eissn_list = institute_issn_df[eissn_col].to_list()
    for _, row in if_df.iterrows():
        row_issn = row[issn_col]
        row_most_recent_year_if = row[most_recent_year_if_col]
        row_corpus_year_if = row[corpus_year_if_col]
        if row_issn in institute_issn_list or row_issn in institute_eissn_list:
            if unknown_kw in [row_most_recent_year_if, row_corpus_year_if]:
                row_journal = row[journal_col]
                row[issn_col] = _get_id(institute_issn_df, row_journal,
                                        journal_col, issn_col,
                                        unknown_kw)
                row[eissn_col] = _get_id(institute_issn_df, row_journal,
                                         journal_col, eissn_col,
                                         unknown_kw)
                missing_if_df = concat_dfs([missing_if_df, row.to_frame().T])
        else:
            missing_issn_df = concat_dfs([missing_issn_df, row.to_frame().T])
    return missing_issn_df, missing_if_df


def _format_missing_df(results_df, add_ifs_col_dic, unknown_kw, add_cols):
    """Formats the 'results_df' dataframe with final column names.

    Args:
        results_df (dataframe): Corpus of publications to be updated.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
        unknown_kw (str): The word for setting unknown values.
        add_cols (bool): True if supplementary columns for ISSN and eISSN are to be \
        filled with value of unknown_kw.
    Returns:
        (dataframe): The formatted data.
    """
    # Setting col names from args
    init_col_keys = ['year_col', 'final_year_col', 'journal_col',
                'issn_col', 'eissn_col','corpus_issn_col',
                'year_db_if_col', 'corpus_year_if_col']
    (year_col, final_year_col, journal_col,
     issn_col, eissn_col, corpus_issn_col,
     year_db_if_col, corpus_year_if_col) = [add_ifs_col_dic[key] for key in init_col_keys]

    # Setting the ordered final columns
    final_col_keys = ['final_year_col', 'journal_col', 'issn_col', 'eissn_col',
                      'most_recent_year_if_col', 'year_db_if_col', 'pub_id_nb_col',
                      'corpus_issn_col']
    final_col_list = [add_ifs_col_dic[key] for key in final_col_keys]

    # Formatting 'results_df'
    results_df = results_df.rename(columns={year_col: final_year_col,
                                            corpus_year_if_col: year_db_if_col})
    if add_cols:
        results_df = results_df.rename(columns={issn_col: corpus_issn_col})
        results_df[issn_col] = unknown_kw
        results_df[eissn_col] = unknown_kw
        results_df = results_df[final_col_list]
    else:
        if results_df.empty:
            results_df[eissn_col] = unknown_kw
        results_df = results_df[final_col_list[:-1]]
    sorted_results_df = results_df.sort_values(by=[journal_col])
    return sorted_results_df


def _format_and_save_add_if_dfs(dfs_list, out_paths_list, corpus_year,
                                add_ifs_col_dic, unknown_kw):
    """Formats with final column names the missing-ISSNs data 
    and the missing-IFs data and saves them.

    The data are formated through the `_format_missing_df` 
    internal function. 
    They are saved through the `format_page` function imported 
    from the `bmfuncts.format_files` module.

    Args:
        dfs_list (list): Composed of the corpus data (dataframe), of the \
        missing-ISSNs data (dataframe) and of the missing-IFs data (dataframe).
        out_paths_list (list): Composed of the full paths to the files where \
        the corpus data, the missing_ISSNs data and of the  missing_IFs data are saved.
        corpus_year (str): The 4-digits year of the corpus.
        add_ifs_col_dic (dict): Useful columns names for the IFs-attribution \
        process as set through the `_set_add_ifs_col_dic` internal function.
        unknown_kw (str): The word for setting unknown values.
    """
    # Setting parameters from args
    corpus_df, year_missing_issn_df, year_missing_if_df = dfs_list
    out_file_path, missing_issn_path, missing_if_path = out_paths_list

    # Formatting 'year_missing_issn_df' and 'year_missing_if_df'
    sorted_year_missing_issn_df = _format_missing_df(year_missing_issn_df, add_ifs_col_dic,
                                                     unknown_kw, add_cols=True)
    sorted_year_missing_if_df = _format_missing_df(year_missing_if_df, add_ifs_col_dic,
                                                   unknown_kw, add_cols=False)

    # Formatting and saving 'corpus_df' as openpyxl file at full path 'out_file_path'
    corpus_df_title = bm_pg.DF_TITLES_LIST[0]
    wb, ws = format_page(corpus_df, corpus_df_title)
    ws.title = "Publications " +  corpus_year
    wb.save(out_file_path)

    # Saving 'year_missing_issn_df' as openpyxl file at full path 'missing_issn_path'
    missing_issn_df_title = bm_pg.DF_TITLES_LIST[18]
    wb, ws = format_page(sorted_year_missing_issn_df, missing_issn_df_title)
    ws.title = "ISSNs manquants " +  corpus_year
    wb.save(missing_issn_path)

    # Saving 'year_missing_if_df' as openpyxl file at full path 'missing_if_path'
    missing_if_df_title = bm_pg.DF_TITLES_LIST[18]
    wb, ws = format_page(sorted_year_missing_if_df, missing_if_df_title)
    ws.title = "IFs manquants " +  corpus_year
    wb.save(missing_if_path)


def add_if(add_if_params_list, paths_list):
    """Adds two new columns containing impact factors to the corpus 
    dataframe 'corpus_df' got from a file which full path is 'in_file_path'.

    First, useful column names are got through the `set_final_col_names` 
    and `set_if_col_names` functions imported from the `bmfuncts.rename_cols` 
    module. 
    The two added columns are named through 'corpus_year_if_col' 
    and 'most_recent_year_if_col'. 
    The impact factors are got using `get_if_db` function that returns 
    in particular the dict 'if_dict' of impact-factors database. 
    The column 'corpus_year_if_col' is filled with the impact-factors 
    values of the corpus year 'corpus_year' if available in the 'if_dict' dict, 
    otherwise the values are set to the 'NOT_AVAILABLE' global value imported 
    from the `bmfuncts.pub_globals` module. 
    The column 'most_recent_year_if_col' is filled with the impact-factors 
    values of the most recent year available in the 'if_dict' dict. 
    In these columns, the NaN values of impact-factors are replaced 
    by 'UNKNOWN' global value imported from the `BiblioParsing` package. 
    The results are saved as openpyxl workbook formatted through the 
    `_format_and_save_add_if_dfs` internal function.

    Args:
        add_if_params_list (list): The list composed of the 4 digits year of the corpus (str), \
        of the Institute's name (str), of the org_tup (tup) that contains parameters of \
        the Institute's organization and of the full path to working folder (path).
        paths_list (list): The list composed of the full path to get the corpus data, \
        the full path to save the corpus data with the impact-factors information added, \
        the full path to save the missing ISSNs information and \
        the full path to save the missing impact-factors information.
    Returns:
        (bool):  Completion status of the impact-factors data (True if complete).
    """
    # Setting parameters values from fct_params_list
    corpus_year, institute, org_tup, wf_path = add_if_params_list

    # Setting parameters from args
    in_file_path = paths_list[0]

    # Setting useful column names
    add_ifs_col_tup = _set_add_ifs_col_dic(institute, org_tup, corpus_year)
    add_ifs_col_dic = add_ifs_col_tup[0]

    # Setting col names from args
    init_col_keys = ['pub_id_col', 'current_if_col', 'corpus_year_if_col']
    (pub_id_col, current_if_col,
     corpus_year_if_col) = [add_ifs_col_dic[key] for key in init_col_keys]

    # Setting particular words list for empty values
    empty_kws_list = [bp.UNKNOWN, bm_pg.NOT_AVAILABLE]

    # Cleaning IFs data
    return_tup = _clean_if_dict(institute, org_tup, wf_path, add_ifs_col_dic,
                                empty_kws_list)
    if_dict, _, if_most_recent_year = return_tup
    add_ifs_col_dic['most_recent_year_if_col'] = (f"{current_if_col}, "
                                                  f"{if_most_recent_year}")
    most_recent_year_if_col = add_ifs_col_dic['most_recent_year_if_col']

    # Building the IF dict keyed by issn or e-issn of journals for the most recent year
    most_recent_year_if_dict = _build_if_dict(if_dict, if_most_recent_year,
                                              add_ifs_col_dic, bp.UNKNOWN)

    # Cleaning corpus data
    corpus_df, institute_issn_df = _clean_corpus_df(in_file_path, if_dict, add_ifs_col_tup,
                                                    bp.UNKNOWN)

    # Adding IFs cols to 'corpus_df'
    if_dicts_list = [if_dict, most_recent_year_if_dict]
    corpus_df = _add_if_cols(corpus_df, if_dicts_list, corpus_year, add_ifs_col_dic,
                             empty_kws_list)

    # Sorting 'corpus_df' pub_id values
    corpus_df = corpus_df.sort_values(by=[pub_id_col])

    # Building 'year_article_if_df' by keeping only rows which doc type has usually an IF
    # then dropping the doc type column
    year_article_if_df = _build_only_if_doctype_df(org_tup, corpus_df, add_ifs_col_dic)

    # Building 'year_if_df' by keeping one row for each issn
    # adding a column with number of related articles
    # then dropping "Pub_id" column
    year_if_df = _build_issn_df(year_article_if_df, add_ifs_col_dic)

    # Removing from 'year_if_df' the rows which ISSN value is not in IF database
    # and keeping them in 'year_missing_issn_df'
    return_tup = _build_missing_issn_and_if_df(year_if_df, institute_issn_df,
                                               add_ifs_col_dic, bp.UNKNOWN)
    year_missing_issn_df, year_missing_if_df = return_tup

    if_database_complete = True
    if not year_missing_issn_df.empty or not year_missing_if_df.empty:
        if_database_complete = False
    else:
        # replace remaining unknown IF values by 'bm_pg.OUTSIDE_ANALYSIS' value
        corpus_df = corpus_df.replace({most_recent_year_if_col: bp.UNKNOWN,
                                       corpus_year_if_col: bp.UNKNOWN},
                                      bm_pg.OUTSIDE_ANALYSIS)

    # Formatting and saving the built dataframes as openpyxl workbooks
    dfs_list = [corpus_df, year_missing_issn_df, year_missing_if_df]
    _format_and_save_add_if_dfs(dfs_list, paths_list[1:], corpus_year, add_ifs_col_dic,
                                bp.UNKNOWN)
    return if_database_complete
