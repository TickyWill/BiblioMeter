"""Module of functions for the consolidation of the publications-list 
in terms of:
- effective affiliation of the authors to the Institute;
- attributing department affiliation to the Institute authors;
- reduction of homonyms among the Institute authors;
- attributing OTPs to each publication;
- attributing impact factor (IF) to each publication.
"""

__all__ = ['add_if',
           'add_otp',
           'concatenate_pub_lists',
           'built_final_pub_list',
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
from bmfuncts.rename_cols import set_homonym_col_names
from bmfuncts.rename_cols import set_otp_col_names
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.rename_cols import set_final_col_names
from bmfuncts.rename_cols import set_if_col_names
from bmfuncts.save_final_results import save_final_results
from bmfuncts.useful_functs import mise_en_page
from bmfuncts.use_pub_attributes import save_otps
from bmfuncts.use_pub_attributes import save_shaped_homonyms_file


def solving_homonyms(institute, org_tup, in_path, out_path):
    """
    
    Args:
        institute (str): The Intitute name.
        org_tup (tup): The tuple of the organization structure of the Institute 
                       used here to set column names for homonyms.
        in_path (path): The full path to the input file where the homonyms are solved.
        out_path (path): The full path to the output file where the solved homonyms 
                         will be kept.

    Returns:
        (tup): The tuple composed of end message (str) and homonyms status (bool).
    """

    # Setting useful column names
    homonyms_col_dic = set_homonym_col_names(institute, org_tup)
    homonyms_col_list = list(homonyms_col_dic.values())
    homonym_col_alias = homonyms_col_dic['homonym']

    # Reading the submit file #
    df_submit = pd.read_excel(in_path)

    # Getting rid of the columns we don't want #
    df_homonyms = df_submit[homonyms_col_list].copy()

    # Setting homonyms status
    homonyms_status = False
    if pg.HOMONYM_FLAG in df_homonyms[homonym_col_alias].to_list():
        homonyms_status = True

    # Saving shaped df_homonyms
    save_shaped_homonyms_file(df_homonyms, out_path)

    end_message = f"File for solving homonymies saved in folder: \n  '{out_path}'"
    return (end_message, homonyms_status)


def _add_authors_name_list(institute, org_tup, in_path, out_path):
    """ The function ` _add_authors_name_list` adds two columns to the dataframe get
    from the Excel file pointed by 'in_path'.
    The columns contain respectively the full name of each author as "NAME, Firstname"
    and the institute co-authors list with attributes of each author as follows:
    "NAME1, Firstame1 (matricule,job type,department affiliation,service affiliation);
     NAME2, Firstame2 (matricule,job type,department affiliation,service affiliation);
     ...".

    Args:
        in_path (path): Fullpath of the excel file of the publications list
                        with a row per Institute author and their attributes columns.
        out_path (path): Fullpath of the processed dataframe as an Excel file
                         saved after going through its treatment.

    Returns:
        (str): end message recalling out_path.

    Notes:
        The global 'COL_NAMES' is imported from 'BiblioSpecificGlobals' module
        of 'BiblioParsing' package.
        The global 'EMPLOYEES_USEFUL_COLS' is imported from 'employees_globals'
        module of 'bmfuncts' package.
        The global 'COL_NAMES_BONUS' is imported from 'pub_globals'
        module of 'bmfuncts' package.
    """

    # Internal functions
    def _get_dpt_key(dpt_raw):
        return_key = None
        for key, values in dpt_label_dict.items():
            if dpt_raw in values:
                return_key = key
        return return_key


    # Setting institute parameters
    dpt_label_dict = org_tup[1]

    # Setting useful column names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    bm_col_rename_dic = col_rename_tup[2]

    # Setting useful aliases
    pub_id_alias         = bm_col_rename_dic[bp.COL_NAMES['pub_id']]
    idx_authors_alias    = bm_col_rename_dic[bp.COL_NAMES['authors'][1]]
    nom_alias            = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['name']]
    prenom_alias         = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['first_name']]
    matricule_alias      = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['matricule']]
    full_name_alias      = bm_col_rename_dic[pg.COL_NAMES_BONUS['nom prénom'] + institute]
    author_type_alias    = bm_col_rename_dic[pg.COL_NAMES_BONUS['author_type']]
    full_name_list_alias = bm_col_rename_dic[pg.COL_NAMES_BONUS['nom prénom liste'] + institute]
    dept_alias           = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['dpt']]
    serv_alias           = bm_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['serv']]

    # Reading the excel file
    df_in = pd.read_excel(in_path)

    # Adding the column 'Nom Prénom' that will be used to create the authors fullname list
    df_in[prenom_alias]    = df_in[prenom_alias].apply(lambda x: x.capitalize())
    df_in[full_name_alias] = df_in[nom_alias] + ', ' + df_in[prenom_alias]

    df_out = pd.DataFrame()
    for _, pub_id_df in df_in.groupby(pub_id_alias):

        authors_tup_list = sorted(list(set(zip(pub_id_df[idx_authors_alias],
                                               pub_id_df[full_name_alias],
                                               pub_id_df[matricule_alias],
                                               pub_id_df[author_type_alias],
                                               pub_id_df[dept_alias],
                                               pub_id_df[serv_alias]))))

        authors_str_list = [(f'{x[1]} ({x[2]},'
                             f'{x[3]},{_get_dpt_key(x[4])},{x[5]})')
                            for x in authors_tup_list]
        authors_full_str = "; ".join(authors_str_list)
        pub_id_df[full_name_list_alias] = authors_full_str
        df_out = pd.concat([df_out, pub_id_df])

    # Saving 'df_out' in an excel file 'out_path'
    df_out.to_excel(out_path, index = False)

    end_message = f"Column with co-authors list is added to the file: \n  '{out_path}'"
    return end_message


def _save_dpt_otp_file(institute, org_tup, dpt, df_dpt, dpt_otp_list,
                       otp_alias, excel_dpt_path, otp_col_list):
    """ Create and store an Excel file under 'excel_dpt_path' for the department labelled 'dpt'.
    The OPTs of the choosen department are added in a new column named 'otp_alias'.
    A list data validation rules is added to each celles of the column
    'otp_alias'. The data frame column are renamed using 'otp_col_list'. The Excel frame is
    configurated by the `mise_en_page` function.
    """

    # Building validation list of OTPs for 'dpt' department
    validation_list = '"'+','.join(dpt_otp_list) + '"'
    data_val = openpyxl_DataValidation(type = "list",
                                       formula1 = validation_list,
                                       showErrorMessage = False)

    # Adding a column containing OTPs of 'dpt' department
    df_dpt[otp_alias] = validation_list

    # Renaming the columns
    df_dpt = df_dpt.reindex(columns = otp_col_list)

    # Formatting the EXCEL file
    wb, ws = mise_en_page(institute, org_tup, df_dpt)
    ws.title = pg.OTP_SHEET_NAME_BASE + " " +  dpt

    # Setting num of first col and first row in EXCEL files
    excel_first_col_num = 1
    excel_first_row_num = 2

    # Getting the column letter for the OTPs column
    otp_alias_df_index = list(df_dpt.columns).index(otp_alias)
    otp_alias_excel_index = otp_alias_df_index + excel_first_col_num
    otp_alias_column_letter = openpyxl_get_column_letter(otp_alias_excel_index)

    # Activating the validation data list in all cells of the OTPs column
    if len(df_dpt):
        # Adding a validation data list
        ws.add_data_validation(data_val)
        for df_index_row in range(len(df_dpt)):
            otp_cell_alias = otp_alias_column_letter + str(df_index_row + excel_first_row_num)
            data_val.add(ws[otp_cell_alias])

    wb.save(excel_dpt_path)


def add_otp(institute, org_tup, in_path, out_path, out_file_base):
    """
    Args:
        in_path (path): fullpath of the working excel file.
        out_path (path): fullpath of the saved prosseced file

    Returns:
        None.

    Notes:
        The global 'COL_NAMES' is imported from the module 'BiblioSpecificGlobals'
        of the package 'BiblioParsing'.
        The function `_add_authors_name_list` is imported
        from the module 'BiblioMeterFonctions' of the package 'bmfuncts'.
        The global 'EMPLOYEES_USEFUL_COLS' is imported from the module 'employees_globals'
        of the package 'bmfuncts'.
        The globals 'COL_NAMES_BONUS' and 'DPT_ATTRIBUTS_DICT' are imported
        from the module 'pub_globals' of the package 'bmfuncts'.
    """
    # Internal functions
    def _set_dpt(dpt_label_list):
        return lambda x: 1 if x in dpt_label_list else 0

    # Setting institute parameters
    dpt_attributs_dict = org_tup[2]

    # Setting useful column names
    otp_col_dic = set_otp_col_names(institute, org_tup)
    otp_col_list = list(otp_col_dic.values())

    # Setting useful aliases
    pub_id_alias     = otp_col_dic['pub_id']
    idx_author_alias = otp_col_dic['author_id']
    dpt_alias        = otp_col_dic['dpt']
    otp_alias        = otp_col_dic['otp_list']
    dpt_label_alias  = ig.DPT_LABEL_KEY
    dpt_otp_alias    = ig.DPT_OTP_KEY

    # Adding a column with a list of the authors in the file where homonymies
    # have been solved and pointed by in_path
    end_message = _add_authors_name_list(institute, org_tup, in_path, in_path)
    print('\n ',end_message)

    solved_homonymies_df = pd.read_excel(in_path)
    solved_homonymies_df.fillna('', inplace = True)

    dpt_list = list(dpt_attributs_dict.keys())

    # For each department adding a column containing 1 or 0
    # depending on if the author belongs or not to the department
    for dpt in dpt_list:
        dpt_label_list = dpt_attributs_dict[dpt][dpt_label_alias]
        solved_homonymies_df[dpt] = solved_homonymies_df[dpt_alias]
        solved_homonymies_df[dpt] = solved_homonymies_df[dpt].apply(_set_dpt(dpt_label_list))

    # Building 'df_out' out of 'solved_homonymies_df' with a row per pub_id
    # 1 or 0 is assigned to each department column depending
    # on if at least one co-author is a member of this department,
    # the detailed information is related to the first author only
    df_out = pd.DataFrame()
    for _, dg in solved_homonymies_df.groupby(pub_id_alias):
        dg = dg.sort_values(by = [idx_author_alias])
        for dpt in dpt_list:
            x = dg[dpt].any().astype(int)
            dg[dpt] = x
        df_out = pd.concat([df_out, dg.iloc[:1]])

    # Configuring an Excel file per department with the list of OTPs
    for dpt in sorted(dpt_list):
        # Setting df_dpt with only pub_ids for which the first author
        # is from the 'dpt' department
        filtre_dpt = False
        for dpt_value in dpt_attributs_dict[dpt][dpt_label_alias]:
            filtre_dpt = filtre_dpt | (df_out[dpt_alias] == dpt_value)
        df_dpt = df_out[filtre_dpt].copy()

        # Setting the list of OTPs for the 'dpt' department
        dpt_otp_list = dpt_attributs_dict[dpt][dpt_otp_alias]

        # Setting the full path of the EXCEl file for the 'dpt' department
        otp_file_name_dpt = f'{out_file_base}_{dpt}.xlsx'
        excel_dpt_path    = out_path / Path(otp_file_name_dpt)

        # Adding a column with validation list for OTPs and saving the file
        _save_dpt_otp_file(institute, org_tup, dpt, df_dpt, dpt_otp_list,
                           otp_alias, excel_dpt_path, otp_col_list)

    end_message  = ("Files for setting publication OTPs per department "
                    f"saved in folder: \n  '{out_path}'")
    return end_message


def _create_if_column(issn_column, if_dict, if_empty_word):
    """ The function `_create_if_column` builds a dataframe column 'if_column'
    using the column 'issn_column' of this dataframe and the dict 'if_dict'
    that make the link between ISSNs ('if_dict' keys) and IFs ('if_dict' values).
    The 'nan' values in the column 'if_column' are replaced by 'empty_word'.

    Args:
        issn_column (pandas serie): The column of the dataframe of interest
                                    that contains the ISSNs values.
        if_dict (dict): The dict which keys are ISSNs and values are IFs.
        if_empty_word (str): The word that will replace nan values in column the returned column.

    Returns:
        (pandas serie): The column of the dataframe of interest
                        that contains the IFs values.
    """
    if_column = issn_column.map(if_dict)
    if_column = if_column.fillna(if_empty_word)
    return if_column


def _build_inst_issn_df(if_db_df, use_col_list):
    """

    """

    # Setting useful aliases
    journal_col_alias = use_col_list[0]
    issn_col_alias    = use_col_list[1]
    eissn_col_alias   = use_col_list[2]
    unknown_alias     = bp.UNKNOWN

    years_list = list(if_db_df.keys())

    init_inst_issn_df = pd.DataFrame(columns = use_col_list)

    for year in years_list:
        year_sub_df = if_db_df[year][use_col_list].copy()
        init_inst_issn_df = pd.concat([init_inst_issn_df, year_sub_df])
    init_inst_issn_df[journal_col_alias] = init_inst_issn_df.apply(lambda row:
                                                                   (row[journal_col_alias].upper()),
                                                                   axis = 1)

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

    inst_issn_df.sort_values(by = [journal_col_alias], inplace = True)
    inst_issn_df.drop_duplicates(inplace = True)

    return inst_issn_df


def _fullfill_issn(corpus_df_bis, inst_issn_df, unknown,
                   journal_col, issn_col, eissn_col):
    """
    TODO Complete the docstring
    """
    for corpus_idx, corpus_row in corpus_df_bis.iterrows():
        if corpus_row[issn_col] != unknown:
            continue
        corpus_journal = corpus_row[journal_col].upper()
        for _, inst_row in inst_issn_df.iterrows():
            inst_journal = inst_row[journal_col].upper()
            if corpus_journal != inst_journal:
                continue
            if inst_row[issn_col] != unknown:
                corpus_df_bis.loc[corpus_idx, issn_col] = inst_row[issn_col]
            elif inst_row[eissn_col] != unknown:
                corpus_df_bis.loc[corpus_idx, issn_col] = inst_row[eissn_col]
            else:
                pass
    return corpus_df_bis


def _build_if_dict(if_df, if_year, unknown, issn_col, eissn_col, if_col):
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


def _get_id(inst_issn_df, journal_name, journal_col, id_col, unknown):
    id_lower_df = inst_issn_df[inst_issn_df[journal_col] == journal_name.lower()][id_col]
    id_lower = unknown
    if not id_lower_df.empty:
        id_lower = id_lower_df.to_list()[0]
    id_upper_df = inst_issn_df[inst_issn_df[journal_col] == journal_name.upper()][id_col]
    id_upper = unknown
    if not id_upper_df.empty:
        id_upper = id_upper_df.to_list()[0]
    journal_id = list(set([id_lower,id_upper]) - set([unknown]))[0]
    return journal_id


def _format_missing_df(results_df, common_args_tup, add_cols):
    (year_col, corpus_year_if_col,
     most_recent_year_if_col,
     journal_col, issn_col, eissn_col,
     pub_id_nb_col, year_db_if_col,
     corpus_issn_col, unknown) = common_args_tup

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
    results_df.rename(columns = {year_col           : final_year_col,
                                 corpus_year_if_col : year_db_if_col},
                      inplace = True)
    if add_cols:
        results_df.rename(columns = {issn_col : corpus_issn_col},
                          inplace = True)
        results_df[issn_col]  = unknown
        results_df[eissn_col] = unknown
        results_df = results_df[final_order_col_list]
    else:
        if results_df.empty:
            results_df[eissn_col] = unknown
        results_df = results_df[final_order_col_list[:-1]]
    sorted_results_df = results_df.sort_values(by = [journal_col])
    return sorted_results_df


def get_if_db(institute, org_tup, bibliometer_path):
    """

    """
    ## Setting institute parameters
    if_db_status = org_tup[5]

    # Setting useful aliases
    if_root_folder_alias   = pg.ARCHI_IF["root"]
    if_filename_alias      = pg.ARCHI_IF["all IF"]
    inst_if_filename_alias = institute + pg.ARCHI_IF["institute_if_all_years"]

    if if_db_status:
        if_filename_alias = inst_if_filename_alias

    # Setting useful paths
    if_root_folder_path = bibliometer_path / Path(if_root_folder_alias)
    if_path             = if_root_folder_path / Path(if_filename_alias)

    # Getting the df of the IFs database
    if_df = pd.read_excel(if_path, sheet_name = None)

    # Setting list of years for which IF are available
    if_available_years_list  = list(if_df.keys())

    # Setting the most recent year for which IF are available
    if_most_recent_year = if_available_years_list[-1]

    return if_df, if_available_years_list, if_most_recent_year


def add_if(institute, org_tup, bibliometer_path, in_file_path, out_file_path,
           missing_if_path, missing_issn_path, corpus_year):

    """ The function `add_if` adds two new columns containing impact factors
    to the corpus dataframe 'corpus_df' got from a file which full path is 'in_file_path'.
    The two columns are named through 'corpus_year_if_col_alias' and 'most_recent_year_if_col'.
    The impact factors are got using `get_if_db` function that returns
    in particular the dataframe 'if_df'.
    The column 'corpus_year_if_col_alias' is filled with the IFs values
    of the corpus year 'corpus_year' if available in the dataframe 'if_df',
    else the values are set to 'not_available_if_alias'.
    The column 'most_recent_year_if_col' is filled with the IFs values
    of the most recent year available in the dataframe 'if_df'.
    In these columns, the NaN values of IFs are replaced by 'unknown_if_fill_alias'.

    Args:
        in_file_path (path): The full path to get the corpus dataframe 'corpus_df'.
        out_file_path (path): The full path to save the new corpus dataframe with the two columns.
        missing_if_path (path): The full path to save the missing IFs information
        missing_issn_path (path): The full path to save the missing ISSNs information.
        corpus_year (int): The year of the corpus to be appended with the two new IF columns.

    Returns:
        (str): Message indicating which file has been mofified and how.

    Notes:
        The globals 'COL_NAMES_BONUS', 'FILL_EMPTY_KEY_WORD' and 'NOT_AVAILABLE_IF'
        are imported from the module 'pub_globals'
        of the package 'bmfuncts'.
    """

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    base_col_list    = list(final_col_dic.values())
    if_maj_col_dic   = set_if_col_names(institute, org_tup)

    # Setting useful column aliases
    pub_id_col_alias         = final_col_dic['pub_id']
    year_col_alias           = final_col_dic['corpus_year']
    journal_col_alias        = final_col_dic['journal']
    doctype_col_alias        = final_col_dic['doc_type']
    issn_col_alias           = final_col_dic['issn']
    otp_col_alias            = final_col_dic['otp']
    current_if_col_alias     = if_maj_col_dic['current_if']
    corpus_year_if_col_alias = if_maj_col_dic['pub_year_if']
    corpus_issn_col_alias    = pg.COL_NAMES_BONUS["database ISSN"]
    database_if_col_alias    = pg.COL_NAMES_BONUS['IF clarivate']
    eissn_col_alias          = pg.COL_NAMES_BONUS['e-ISSN']
    otp_col_new_alias        = pg.COL_NAMES_BONUS['final OTP']
    pub_id_nb_col_alias      = pg.COL_NAMES_BONUS['pub number']

    # Setting globals aliases
    doc_type_dict_alias       = pg.DOC_TYPE_DICT
    not_available_if_alias    = pg.NOT_AVAILABLE_IF
    unknown_if_fill_alias     = pg.FILL_EMPTY_KEY_WORD
    unknown_alias             = pg.FILL_EMPTY_KEY_WORD
    outside_if_analysis_alias = pg.OUTSIDE_ANALYSIS

    # Setting institute parameters
    if_db_status            = org_tup[5]
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
            if_df[year].rename(columns = {year_database_if_col_alias: database_if_col_alias},
                               inplace = True)

    # Replacing NAN in if_df
    values_dict = {issn_col_alias       : unknown_alias,
                   eissn_col_alias      : unknown_alias,
                   database_if_col_alias: not_available_if_alias}
    for year in if_available_years_list:
        if_df[year].fillna(value = values_dict, inplace = True)

    # Building the IF dict keyed by issn or e-issn of journals for the most recent year
    most_recent_year_if_dict = _build_if_dict(if_df, if_most_recent_year, unknown_alias,
                                              issn_col_alias, eissn_col_alias,
                                              database_if_col_alias)

    # Setting local column names
    most_recent_year_if_col = current_if_col_alias + ', ' + if_most_recent_year
    year_db_if_col          = database_if_col_alias + ' ' + corpus_year
    #final_year_col          = year_col_alias[0:5]
    journal_upper_col       = journal_col_alias + '_Upper'

    # Getting the df where to add IFs
    corpus_df = pd.read_excel(in_file_path)

    # Recasting column names
    new_base_col_list = list(
        map(lambda x: x.replace(otp_col_alias, otp_col_new_alias),
            base_col_list)
    )
    if otp_col_alias in corpus_df.columns:
        corpus_df.rename(columns = {otp_col_alias : otp_col_new_alias},
                         inplace = True)

    # Setting type of values in 'year_col_alias' as string
    corpus_df = corpus_df.astype({year_col_alias : str})

    # Initializing 'corpus_df_bis' as copy of 'corpus_df'
    corpus_df_bis = corpus_df[new_base_col_list].copy()

    # Getting the df of ISSN and eISSN database of the institut
    use_col_list = [journal_col_alias, issn_col_alias, eissn_col_alias]
    inst_issn_df = _build_inst_issn_df(if_df, use_col_list)

    # Filling unknown ISSN in 'corpus_df_bis' using 'inst_issn_df'
    # through _fullfill_issn function
    corpus_df_bis = _fullfill_issn(corpus_df_bis, inst_issn_df, unknown_alias,
                                   journal_col_alias, issn_col_alias, eissn_col_alias)

    # Adding 'most_recent_year_if_col' column to 'corpus_df_bis'
    # with values defined by internal function '_create_if_column'
    corpus_df_bis[most_recent_year_if_col] = _create_if_column(corpus_df_bis[issn_col_alias],
                                                               most_recent_year_if_dict,
                                                               unknown_if_fill_alias)

    # Adding 'corpus_year_if_col_alias' column to 'corpus_df_bis'
    if corpus_year in if_available_years_list:
        # with values defined by internal function '_create_if_column'
        # Building the IF dict keyed by issn or e-issn of journals for the corpus year
        current_year_if_dict = _build_if_dict(if_df, corpus_year, unknown_alias,
                                              issn_col_alias, eissn_col_alias,
                                              database_if_col_alias)
        corpus_df_bis[corpus_year_if_col_alias] = _create_if_column(corpus_df_bis[issn_col_alias],
                                                                   current_year_if_dict,
                                                                   unknown_if_fill_alias)
    else:
        # with 'not_available_if_alias' value
        corpus_df_bis[corpus_year_if_col_alias] = not_available_if_alias

    # Sorting 'corpus_df_bis' pub_id values
    corpus_df_bis.sort_values(by = [pub_id_col_alias], inplace = True)

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
    year_article_if_df = pd.DataFrame(columns = year_pub_if_df.columns)
    for doc_type, doc_type_df in year_pub_if_df.groupby(doctype_col_alias):
        if doc_type.upper() not in doctype_to_drop_list_alias:
            year_article_if_df = pd.concat([year_article_if_df, doc_type_df])
    year_article_if_df.drop(doctype_col_alias, axis = 1, inplace = True)

    # Building 'year_if_df' by keeping one row for each issn
    # adding a column with number of related articles
    # then droping "Pub_id" column
    year_if_df = pd.DataFrame(columns = year_article_if_df.columns.to_list() [1:] \
                                        + [pub_id_nb_col_alias])
    for _, issn_df in year_article_if_df.groupby(issn_col_alias):
        pub_id_nb = len(issn_df)
        issn_df[pub_id_nb_col_alias] = pub_id_nb
        issn_df.drop(pub_id_col_alias, axis = 1, inplace = True)
        issn_df[journal_upper_col] = issn_df[journal_col_alias].astype(str).str.upper()
        issn_df.drop_duplicates(subset=[journal_upper_col], keep='first', inplace = True)
        issn_df.drop([journal_upper_col], axis = 1, inplace = True)
        year_if_df = pd.concat([year_if_df, issn_df])

    # Removing from 'year_if_df' the rows which ISSN value is not in IF database
    # and keeping them in 'year_missing_issn_df'
    year_missing_issn_df = pd.DataFrame(columns = year_if_df.columns)
    year_missing_if_df   = pd.DataFrame(columns = year_if_df.columns)
    inst_issn_list  = inst_issn_df[issn_col_alias].to_list()
    inst_eissn_list = inst_issn_df[eissn_col_alias].to_list()
    for _, row in year_if_df.iterrows():
        row_issn = row[issn_col_alias]
        row_most_recent_year_if = row[most_recent_year_if_col]
        row_corpus_year_if      = row[corpus_year_if_col_alias]
        if row_issn not in inst_issn_list and row_issn not in inst_eissn_list:
            year_missing_issn_df = pd.concat([year_missing_issn_df, row.to_frame().T])
        elif unknown_alias in [row_most_recent_year_if, row_corpus_year_if]:
            row_journal = row[journal_col_alias]
            row[issn_col_alias]  = _get_id(inst_issn_df, row_journal,
                                           journal_col_alias, issn_col_alias,
                                           unknown_alias)
            row[eissn_col_alias] = _get_id(inst_issn_df, row_journal,
                                           journal_col_alias, eissn_col_alias,
                                           unknown_alias)
            year_missing_if_df   = pd.concat([year_missing_if_df, row.to_frame().T])

    if_database_complete = True
    if not year_missing_issn_df.empty or not year_missing_if_df.empty:
        if_database_complete = False
    else:
        # replace remaining unknown IF values by 'not_available_if_alias' value
        corpus_df_bis.replace({most_recent_year_if_col: unknown_if_fill_alias,
                               corpus_year_if_col_alias    : unknown_if_fill_alias,
                              }, outside_if_analysis_alias, inplace = True)

    # Formatting and saving 'corpus_df_bis' as EXCEL file at full path 'out_file_path'
    wb, _ = mise_en_page(institute, org_tup, corpus_df_bis)
    wb.save(out_file_path)

    # Setting common args list for '_format_missing_df' function
    common_args_tup = (year_col_alias, corpus_year_if_col_alias,
                       most_recent_year_if_col,
                       journal_col_alias, issn_col_alias, eissn_col_alias,
                       pub_id_nb_col_alias, year_db_if_col,
                       corpus_issn_col_alias, unknown_alias)

    # Formatting 'year_missing_issn_df' and 'year_missing_if_df'
    sorted_year_missing_issn_df = _format_missing_df(
        year_missing_issn_df, common_args_tup, add_cols = True)
    sorted_year_missing_if_df   = _format_missing_df(
        year_missing_if_df, common_args_tup, add_cols = False)

    # Saving 'year_missing_issn_df' as EXCEL file at full path 'missing_issn_path'
    wb, _ = mise_en_page(institute, org_tup, sorted_year_missing_issn_df)
    wb.save(missing_issn_path)

    # Saving 'year_missing_if_df' as EXCEL file at full path 'missing_if_path'
    wb, _ = mise_en_page(institute, org_tup, sorted_year_missing_if_df)
    wb.save(missing_if_path)

    end_message = f"IFs added for year {year} in file : \n  '{out_file_path}'"
    return end_message, if_database_complete


def split_pub_list_by_doc_type(institute, org_tup, bibliometer_path, corpus_year):
    """

    """

    # Setting useful aliases
    pub_list_path_alias      = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    year_pub_list_file_alias = pub_list_file_base_alias + " " + corpus_year
    pub_list_file_alias      = year_pub_list_file_alias + ".xlsx"
    other_dg_file_alias      = year_pub_list_file_alias + "_" + pg.OTHER_DOCTYPE + ".xlsx"
    corpus_year_path         = bibliometer_path / Path(corpus_year)
    pub_list_path            = corpus_year_path / Path(pub_list_path_alias)
    pub_list_file_path       = pub_list_path / Path(pub_list_file_alias)
    other_dg_path            = pub_list_path / Path(other_dg_file_alias)

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    pub_id_col_alias = final_col_dic['pub_id']
    doc_type_alias   = final_col_dic['doc_type']

    full_pub_list_df = pd.read_excel(pub_list_file_path)
    other_dg = full_pub_list_df.copy()
    pub_nb = len(full_pub_list_df)
    key_pub_nb = 0
    for key, doctype_list in pg.DOCTYPE_TO_SAVE_DICT.items():
        doctype_list = [x.upper() for x in  doctype_list]
        key_dg = pd.DataFrame(columns = full_pub_list_df.columns)

        for doc_type, dg in full_pub_list_df.groupby(doc_type_alias):
            if doc_type.upper() in doctype_list:
                key_dg = pd.concat([key_dg, dg])
                other_dg = other_dg.drop(dg.index)

        key_pub_nb += len(key_dg)

        key_dg_file_alias = year_pub_list_file_alias + "_" + key + ".xlsx"
        key_dg_path = pub_list_path / Path(key_dg_file_alias)

        key_dg.sort_values(by=[pub_id_col_alias], inplace = True)
        wb, _ = mise_en_page(institute, org_tup, key_dg)
        wb.save(key_dg_path)

    other_dg.sort_values(by = [pub_id_col_alias], inplace = True)
    wb, _ = mise_en_page(institute, org_tup, other_dg)
    wb.save(other_dg_path)

    split_ratio = 100
    if pub_nb != 0:
        split_ratio = round(key_pub_nb / pub_nb*100)
    return split_ratio


def built_final_pub_list(institute, org_tup, bibliometer_path, datatype,
                         in_path, out_path, out_file_path, in_file_base, corpus_year):
    """
    Args :
        in_path
        out_file_path
        in_file_base

    Returns :
        un fichier excel
    """

    # internal functions
    def _set_df_otp_dpt(dpt_label):
        otp_file_name_dpt_ok = in_file_base + '_' + dpt_label + '_ok.xlsx'

        dpt_path = in_path / Path(otp_file_name_dpt_ok)
        if not os.path.exists(dpt_path):
            otp_file_name_dpt = in_file_base + '_' + dpt_label + '.xlsx'
            dpt_path = in_path / Path(otp_file_name_dpt)
        dpt_df = pd.read_excel(dpt_path)
        return dpt_df

    # Setting useful column names
    final_col_dic, _ = set_final_col_names(institute, org_tup)
    final_col_list   = list(final_col_dic.values())

    # Setting useful aliases
    missing_if_filename_base_alias   = pg.ARCHI_IF["missing_if_base"]
    missing_issn_filename_base_alias = pg.ARCHI_IF["missing_issn_base"]
    invalid_pub_filename_base_alias  = pg.ARCHI_YEAR["invalid file name base"]
    pub_id_alias                     = final_col_dic['pub_id']
    otp_alias                        = final_col_dic['otp']   # Choix de l'OTP

    # Setting useful paths
    missing_if_path   = out_path / Path(corpus_year + missing_if_filename_base_alias)
    missing_issn_path = out_path / Path(corpus_year + missing_issn_filename_base_alias)
    invalid_file_path = out_path / Path(invalid_pub_filename_base_alias
                                        + " " + corpus_year + ".xlsx")

    # Setting institute parameters
    dpt_label_dict = org_tup[1]

    # Getting dept OTPs df and concatenating them
    dpt_label_list = list(dpt_label_dict.keys())
    otp_df_init_status = True
    for dpt_label in dpt_label_list:
        dpt_df = _set_df_otp_dpt(dpt_label)
        if otp_df_init_status:
            otp_df = dpt_df.copy()
        else:
            otp_df = pd.concat([otp_df, dpt_df])
        otp_df_init_status = False

    # Deduplicating rows on Pub_id
    otp_df.drop_duplicates(subset = [pub_id_alias], inplace = True)

    # Selecting useful columns using final_col_list
    consolidate_pub_list_df = otp_df[final_col_list].copy()

    # Saving df to EXCEL file
    consolidate_pub_list_df.to_excel(out_file_path, index = False)

    # Saving set OTPs
    otp_message = save_otps(institute, org_tup, bibliometer_path, corpus_year)

    # Setting pub ID as index for unique identification of rows
    consolidate_pub_list_df.set_index(pub_id_alias, inplace = True)

    # Droping invalide publications by pub Id as index
    invalid_pub_list_df = consolidate_pub_list_df.drop(
        consolidate_pub_list_df[consolidate_pub_list_df[otp_alias] \
                                != ig.INVALIDE].index)
    consolidate_pub_list_df.drop(consolidate_pub_list_df[consolidate_pub_list_df[otp_alias] \
                                                         == ig.INVALIDE].index,
                                 inplace = True)

    # Resetting pub ID as a standard column
    consolidate_pub_list_df.reset_index(inplace = True)

    # Re_saving df to EXCEL file
    consolidate_pub_list_df.to_excel(out_file_path, index = False)
    invalid_pub_list_df.to_excel(invalid_file_path, index = False)

    # Adding Impact Factors and saving new consolidate_pub_list_df
    # this also for saving results files to complete IFs database
    _, if_database_complete = add_if(institute,
                                     org_tup,
                                     bibliometer_path,
                                     out_file_path,
                                     out_file_path,
                                     missing_if_path,
                                     missing_issn_path,
                                     corpus_year)

    # Splitting saved file by documents types (ARTICLES, BOOKS and PROCEEDINGS)
    split_ratio = split_pub_list_by_doc_type(institute, org_tup, bibliometer_path, corpus_year)

    # Saving pub list as final result
    status_values = len(pg.RESULTS_TO_SAVE) * [False]
    results_to_save_dict = dict(zip(pg.RESULTS_TO_SAVE, status_values))
    results_to_save_dict["pub_lists"] = True
    if_analysis_name = None
    final_save_message = save_final_results(institute, org_tup, bibliometer_path,
                                            datatype, corpus_year, if_analysis_name,
                                            results_to_save_dict, verbose = False)

    end_message  = (f"\n{otp_message}"
                    f"\nOTPs identification integrated in file: \n  '{out_file_path}'"
                    f"\n\nPublications list for year {corpus_year} "
                    f"has been {split_ratio} % split "
                    "in several files by group of document types. \n"
                    f"{final_save_message}")

    return end_message, split_ratio, if_database_complete


def concatenate_pub_lists(institute, org_tup, bibliometer_path, years_list):
    """

    """
    # Setting useful aliases
    pub_list_path_alias      = pg.ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias = pg.ARCHI_YEAR["pub list file name base"]
    bdd_multi_annuelle_folder_alias = pg.ARCHI_BDD_MULTI_ANNUELLE["root"]
    bdd_multi_annuelle_file_alias   = pg.ARCHI_BDD_MULTI_ANNUELLE["concat file name base"]

    # Building the concatenated dataframe of available publications lists
    df_concat = pd.DataFrame()
    available_liste_conso = ""
    for year in years_list:
        try:
            corpus_folder_path = bibliometer_path / Path(year)
            pub_list_folder_path = corpus_folder_path / Path(pub_list_path_alias)
            pub_list_file_name = f"{pub_list_file_base_alias} {year}.xlsx"
            pub_list_path = pub_list_folder_path / Path(pub_list_file_name)
            df_inter  = pd.read_excel(pub_list_path)
            df_concat = pd.concat([df_concat, df_inter])
            available_liste_conso += f" {year}"

        except FileNotFoundError:
            pass

    # Formatting and saving the concatenated dataframe in an EXCEL file
    date = str(datetime.now())[:16].replace(':', 'h')
    out_file = (f"{date} {bdd_multi_annuelle_file_alias} "
                f"{os.getlogin()}_{available_liste_conso}.xlsx")
    out_path = bibliometer_path / Path(bdd_multi_annuelle_folder_alias)
    out_file_path = out_path / Path(out_file)

    wb, _ = mise_en_page(institute, org_tup, df_concat)
    wb.save(out_file_path)

    end_message  = f"Concatenation of consolidated pub lists saved in folder: \n  '{out_path}'"
    end_message += f"\n\n under filename: \n  '{out_file}'."
    return end_message
