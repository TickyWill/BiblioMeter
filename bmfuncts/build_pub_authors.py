"""Module of functions for building the Institute's publications-list 
with one row per author taking care of:

- Potential discrepancy between author-name spelling and employee-name spelling;
- Complementary database to the Institute's employees-database \
with young researchers affiliated to the Institute;
- Inappropriate affiliation to the Institute of external collaborators.

"""

__all__ = ['build_institute_pubs_authors_data',
          ]

# Standard Library imports
import warnings
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import bmfuncts.pub_globals as bm_pg
import bmfuncts.institute_globals as bm_ig
from bmfuncts.read_final_results import read_final_dedup
from bmfuncts.save_final_results import save_final_dedup
from bmfuncts.save_final_results import set_results_folder_path
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import print_temp_text
from bmfuncts.useful_functs import reorder_df
from bmfuncts.useful_functs import standardize_full_name_order
from bmfuncts.useful_functs import standardize_txt


def _set_useful_bp_cols():
    """Sets the list of useful columns' names.

    The globals set from globals of `bmfuncts.pub_globals` 
    module imported as bm_pg, have values set in the `bpfuncts` package.

    Returns:
        (list): The built list of columns' names (str).
    """
    pub_id_alias = bm_pg.COL_NAMES['pub_id']
    auth_idx_alias = bm_pg.COL_NAMES['authors'][1]
    co_auth_alias = bm_pg.COL_NAMES['authors'][2]
    doi_alias = bm_pg.COL_NAMES['articles'][6]
    address_alias = bm_pg.COL_NAMES['auth_inst'][2]
    norm_affil_alias = bm_pg.COL_NAMES['auth_inst'][4]

    bp_cols_list = [pub_id_alias, auth_idx_alias,
                    co_auth_alias, doi_alias,
                    address_alias, norm_affil_alias]
    return bp_cols_list


def _set_useful_bm_cols():
    """Sets useful lists of columns' names from globals 
    of `bmfuncts.pub_globals` module imported as bm_pg.

    Returns:
        (tup): Composed of the built lists of columns' names.
    """
    corpus_year_alias = bm_pg.COL_NAMES_ADD['corpus_year']
    authors_list_alias = bm_pg.COL_NAMES_ADD['liste auteurs']
    bm_bonus_cols_list = [corpus_year_alias, authors_list_alias]

    fullname_alias = bm_pg.COL_NAMES_ADD['full_name']
    lastname_alias = bm_pg.COL_NAMES_ADD['last_name']
    firstname_alias = bm_pg.COL_NAMES_ADD['first_name']
    bm_auth_names_list = [fullname_alias, lastname_alias, firstname_alias]

    ortho_lastname_init_alias = bm_pg.COL_NAMES_ORTHO['last name init']
    ortho_initials_init_alias = bm_pg.COL_NAMES_ORTHO['initials init']
    ortho_lastname_new_alias = bm_pg.COL_NAMES_ORTHO['last name new']
    ortho_initials_new_alias = bm_pg.COL_NAMES_ORTHO['initials new']
    bm_ortho_cols_list = [ortho_lastname_init_alias, ortho_initials_init_alias,
                          ortho_lastname_new_alias, ortho_initials_new_alias]

    compl_lastname_init_alias = bm_pg.COL_NAMES_COMPL['last name init']
    compl_initials_init_alias = bm_pg.COL_NAMES_COMPL['initials init']
    compl_lastname_new_alias = bm_pg.COL_NAMES_COMPL['last name new']
    compl_initials_new_alias = bm_pg.COL_NAMES_COMPL['initials new']
    compl_year_pub_alias = bm_pg.COL_NAMES_COMPL['publication year']
    bm_compl_cols_list = [compl_lastname_init_alias, compl_initials_init_alias,
                          compl_lastname_new_alias, compl_initials_new_alias,
                          compl_year_pub_alias]

    outliers_lastname_col_alias = bm_pg.COL_NAMES_EXT['last name']
    outliers_initials_col_alias = bm_pg.COL_NAMES_EXT['initials']
    bm_outliers_cols_list = [outliers_lastname_col_alias, outliers_initials_col_alias]

    return_tup = (bm_bonus_cols_list, bm_auth_names_list, bm_ortho_cols_list,
                  bm_compl_cols_list, bm_outliers_cols_list)
    return return_tup


def _get_hal_added_dois(wf_path, corpus_year, doi_col):
    """Gets the list of the added DOIS from HAL database.
    Args:
        wf_path (path): Full path to working folder.
        corpus_year (str): Contains the corpus year defined by 4 digits.
        doi_col (str):  The column name of DOIs.
    Returns:
        (list): The list of added DOIs.
    """
    extract_root_alias = bm_pg.ARCHI_EXTRACT["root"]
    scopus_extract_root_alias = bm_pg.ARCHI_EXTRACT[bm_pg.SCOPUS]["root"]
    added_dois_file_base_alias = bm_pg.ARCHI_EXTRACT[bm_pg.SCOPUS]["added_dois_file"]
    added_dois_file = corpus_year + added_dois_file_base_alias
    extract_root_path = wf_path / Path(extract_root_alias)
    scopus_extract_path = extract_root_path / Path(scopus_extract_root_alias)
    added_dois_path = Path(scopus_extract_path) / Path(corpus_year) / Path(added_dois_file)
    hal_added_dois_df = pd.read_excel(added_dois_path)
    hal_added_dois_list = hal_added_dois_df[doi_col].to_list()
    return hal_added_dois_list


def _get_doi_pub_id(articles_df, dois_list, pub_id_col, doi_col):
    """Gets data of the publications ID per DOI in the given list of DOIs.

    Args:
        articles_df (dataframe): The data of publications list resulting \
        from the parsing step.
        dois_list (list): The DOIs (str) list for which publications IDs are got.
        pub_id_col (str): The column name of publications IDs.
        doi_col (str):  The column name of DOIs.
    Returns:
        (dataframe): The data of the publications ID per DOI.
    """
    usecols = [pub_id_col, doi_col]
    dois_df_init = articles_df[usecols]
    dois_pub_id_df = pd.DataFrame(columns=usecols)
    for doi in dois_list:
        doi_df = dois_df_init[dois_df_init[doi_col]==doi]
        dois_pub_id_df = concat_dfs([dois_pub_id_df, doi_df])
    return dois_pub_id_df


def _correct_addr(addr, correct_params, norm_affil=None, institute_main_val=None):
    """Corrects the given address if it contains the top affiliation and the town 
    of the Institute, and it doesn't contain any of the specified excluding items.

    Args:
        addr (str): The address to be checked and corrected if required.
        correct_params (list): Parameters set through the `_set_addr_correction_params` \
        internal function.
        norm_affil (str): Optional (default=None), initial normalized affiliation.
        institute_main_val (int): Optional (default=None), initial value of the status \
        of the affiliation of the author to the Institute.
    Returns:
        (tup): Composed of the possibly corrected items (address, normalized affiliation \
        and the value of the status of the affiliation of the author to the Institute).
    """
    (institute, _, institute_norm, top_affil,
     town, excluding_items) = correct_params
    correct_addr, correct_norm_affil, correct_institute_main_val = addr, norm_affil, institute_main_val

    addr_lw = addr.lower()
    exclude_test = any(ext.lower() in addr_lw for ext in excluding_items)
    correct_test = top_affil in addr_lw and town in addr_lw and not exclude_test
    if correct_test:
        correct_addr = institute + ', ' + addr
        correct_norm_affil = institute_norm
        correct_institute_main_val= 1
    return correct_addr, correct_norm_affil, correct_institute_main_val


def _build_corrected_authaddr_data(authaddr_df, hal_added_pub_id_list, bp_cols_list, correct_params):
    """Corrects the authors-with-addresses parsing data for the publications added from HAL 
    through the `_correct_addr` internal function.

    Args:
        authaddr_df (dataframe): The initial data of authors with addresses.
        hal_added_pub_id_list (list): The publication IDs added from HAL.
        bp_cols_list (list): The list of useful col names as set by \
        the `_set_useful_bp_cols` internal function.
        correct_params (list): Parameters set through the `_set_addr_correction_params` \
        internal function.
    Returns:
        (dataframe): The corrected data of authors with addresses.
    """
    pub_id_col, address_col, norm_affil_col = bp_cols_list[0], bp_cols_list[4], bp_cols_list[5]

    institute_col = correct_params[1]

    new_authaddr_df = pd.DataFrame(columns=authaddr_df.columns)
    for pub_id, pub_df in authaddr_df.groupby(pub_id_col):
        if pub_id in hal_added_pub_id_list:
            new_pub_df = pd.DataFrame(columns=pub_df.columns)
            for addrs, addr_df in pub_df.groupby(address_col):
                addrs_list = addrs.split("; ")
                new_addrs_list = []
                for addr in addrs_list:
                    return_tup = _correct_addr(addr, correct_params, norm_affil=addr_df[norm_affil_col],
                                               institute_main_val=addr_df[institute_col])
                    correct_addr, correct_norm_affil, correct_institute_main_val = return_tup
                    new_addrs_list.append(correct_addr)
                    new_addrs = "; ".join(new_addrs_list)
                    addr_df[address_col] = new_addrs
                    addr_df[norm_affil_col] = correct_norm_affil
                    addr_df[institute_col] = correct_institute_main_val
                new_pub_df = concat_dfs([new_pub_df, addr_df])
            new_authaddr_df = concat_dfs([new_authaddr_df, new_pub_df])
        else:
            new_authaddr_df = concat_dfs([new_authaddr_df, pub_df])
    return new_authaddr_df


def _build_corrected_addr_data(addresses_df, hal_added_pub_id_list, bp_cols_list, correct_params):
    """Corrects the addresses parsing data for the publications added from HAL 
    through the `_correct_addr` internal function.

    Args:
        addresses_df (dataframe): The initial data of addresses.
        hal_added_pub_id_list (list): The publication IDs added from HAL.
        bp_cols_list (list): The list of useful col names as set by \
        the `_set_useful_bp_cols` internal function.
        correct_params (list): Parameters set through the `_set_addr_correction_params` \
        internal function.
    Returns:
        (dataframe): The corrected data of addresses.
    """
    pub_id_col, address_col = bp_cols_list[0], bp_cols_list[4]

    new_addresses_df = pd.DataFrame(columns=addresses_df.columns)
    for pub_id, pub_df in addresses_df.groupby(pub_id_col):
        if pub_id in hal_added_pub_id_list:
            new_pub_df = pd.DataFrame(columns=pub_df.columns)
            for addr, addr_df in pub_df.groupby(address_col):
                correct_addr, _, _ = _correct_addr(addr, correct_params)
                addr_df[address_col] = correct_addr
                new_pub_df = concat_dfs([new_pub_df, addr_df])
            new_addresses_df = concat_dfs([new_addresses_df, new_pub_df])
        else:
            new_addresses_df = concat_dfs([new_addresses_df, pub_df])
    return new_addresses_df


def _set_addr_correction_params(institute, org_tup):
    """Sets test parameters to include Institute's name in address from values 
    defined in the `bmfuncts.institute_globals` module.

    Args:
        institute (str): The Institute's name.
        org_tup (tup): Contains parameters of Institute's organization.
    Return:
        (list): Composed of the Institute's name (str), \
        of the column name (str) that contains '1' value if the address \
        belongs to the Institute, of the top affiliation (str) for the Institute, \
        of the normalized affiliation name (str) of the Institute, \
        of the town (str) of the Institute, the items (list of str) \
        that exclude the address correction.
    """
    institute_col_list = org_tup[4]
    institute_main_idx = org_tup[7]
    institute_col = institute_col_list[institute_main_idx]
    institute_norm = bm_ig.INSTITUTES_NORM_NAME_DICT[institute]
    top_affil = bm_ig.INSTITUTES_TOP_AFFIL_DICT[institute].lower()
    town = bm_ig.INSTITUTES_TOWN_DICT[institute].lower()
    excluding_items = bm_ig.EXCLUDE_ADDR_ITEMS_LIST
    correct_params = [institute, institute_col, institute_norm, top_affil, town, excluding_items]
    return correct_params


def _check_added_dois_affil(params_list, select_items_dict, bp_cols_list):
    """Checks if normalized-affiliation attribution is correct for the added DOIs 
    from HAL database and builds the corrected files of parsing.

    Args:
        params_list (list):  Composed of the 4 digits year of the corpus (str), \
        of the Institute's name (str), of the org_tup (tup) that contains parameters of \
        Institute's organization and of the full path to the working folder (path).
        select_items_dict (dict): !!!!Composed of the publications data (dataframe), \
        of the addresses data (dataframe) and \
        of the authors with addresses data (dataframe)!!!.
        bp_cols_list (list): The list of useful col names as set by \
        the `_set_useful_bp_cols` internal function.
    Returns:
         (dataframe): The corrected data of authors with addresses.
    """
    # Setting parameters values from args
    (corpus_year, print_params, institute, org_tup, wf_path, datatype,
     parsing_filenames_dict) = params_list
    pub_id_col, doi_col = bp_cols_list[0], bp_cols_list[3]
    articles_df, addresses_df, _, authaddr_df = list(select_items_dict.values())

    txt_len = print_temp_text(f"{bm_pg.TAB*2}- Checking affiliations of HAL added "
                              "DOIs in deduplication's parsing results...", txt_end=True)

    # Setting test parameters to include Institute's name in address
    correct_params = _set_addr_correction_params(institute, org_tup)

    # Building the list of publications IDs for the publications added from HAL
    hal_added_dois_list = _get_hal_added_dois(wf_path, corpus_year, doi_col)
    hal_added_pub_id_df = _get_doi_pub_id(articles_df, hal_added_dois_list,
                                          pub_id_col, doi_col)
    hal_added_pub_id_list = hal_added_pub_id_df[pub_id_col].to_list()

    # Correcting the authors-with-addresses data for the publications added from HAL
    new_authaddr_df = _build_corrected_authaddr_data(authaddr_df, hal_added_pub_id_list,
                                                     bp_cols_list, correct_params)

    # Correcting the addresses data for the publications added from HAL
    new_addresses_df = _build_corrected_addr_data(addresses_df, hal_added_pub_id_list,
                                                  bp_cols_list, correct_params)

    # Saving checked parsing data
    dedup_infos = [wf_path, datatype, corpus_year]
    _, addresses_key, _, authaddr_key = list(select_items_dict.keys())
    addresses_file_name_base = parsing_filenames_dict[addresses_key]
    authaddr_file_name_base = parsing_filenames_dict[authaddr_key]
    save_final_dedup(new_addresses_df, addresses_file_name_base, bm_pg.TSV_SAVE_EXTENT, dedup_infos)
    save_final_dedup(new_authaddr_df, authaddr_file_name_base, bm_pg.TSV_SAVE_EXTENT, dedup_infos)

    print_step_text(f"{bm_pg.TAB*2}- Affiliations of HAL added DOIs in parsing data"
                    "checked and saved as final deduplication's results",
                    print_params, prev_txt_len=txt_len)
    return new_authaddr_df


def _retain_firstname_initials(txt):
    """Removes '-' from the initials of the author's firstname.

    Args:
        txt (str): The raw initials of the author's firstname.
    Returns:
        (str): The modified initials.
    """
    txt = txt.replace('-',' ')
    initials = ''.join(txt.split(' '))
    return initials


def _split_lastname_firstname(txt, digits_min=4):
    """Sets the lambda function for extracting last_name and first-name initials from the author's name.

    It uses the `_retain_firstname_initials` internal function  and the `standardize_txt` function 
    imported from the `bmfuncts.useful_functs` module.

    Args:
        txt (str): The txt from which lastname and first-name initials of the author are extracted.
        digits_min (int): The minimum length of the names that contains '-' symbol to be kept \
        in author's lastname.
    Returns:
        (tup): (The extracted lastname, the extracted first-name initials).
    """
    names_list = txt.split()
    first_names_list = names_list[-1:]
    last_names_list = names_list[:-1]
    for name_idx, name in enumerate(last_names_list):
        if len(name)<digits_min and ('-' in name):
            first_names_list.append(name)
            first_names_list = first_names_list[::-1]
            last_names_list = last_names_list[:name_idx] + last_names_list[(name_idx + 1):]
    first_name_initials = _retain_firstname_initials(' '.join(first_names_list))
    last_name = standardize_txt(' '.join(last_names_list))
    return last_name, first_name_initials


def _build_filt_auth_affil(authaddr_auth_df, org_tup):
    """Builds the filter to select the authors by their affiliation to the Institute.

    The filter returns True if any of the specified columns contains 1 for the author, 
    otherwise it returns False.
    To do that, the function needs the following parameters of the Institute's organization:
    1- The list of columns' names that contains the status of the author's affiliation to the Institute;
    2- The index in this list of the column name that contains the status of the author's affiliation \
    via the main Institute's affiliation name.
    3- The checking mode given for the Institute for either using only the main-affiliation status \
    or using the status of all the possible names of the Institute's affiliation.

    Args:
        authaddr_auth_df (dataframe): Data of combined name of author to author ID \
        with affiliation by publication ID.
        org_tup (tup): Contains parameters of Institute's organization.
    Returns:
        (Pandas Series): The built filter.
    """
    # Setting parameters' values of Institute's organization from 'org_tup' tuple
    # 1- List of column names (str) the status of the author's affiliation
    # to the Institute
    # 2- Index in this list of the column name that contains the status of the author's affiliation
    # via the main Institute's affiliation name
    # 3- checking mode given for the Institute for either using only the main-affiliation status
    # or using the status of all the possible names of the Institute's affiliation
    institute_col_list, institute_main_idx, main_status = org_tup[4], org_tup[7], org_tup[8]

    # Building the filter
    main_institute_col = institute_col_list[institute_main_idx]
    if main_status:
        # Setting the identification of affiliation to the Institute only from the column
        # of the status in the main-affiliation's column
        filt_auth_affil_ = authaddr_auth_df[main_institute_col]==1
    else:
        # Setting the identification of affiliation to the Institute from the status in all
        # the possible columns of the Institute's affiliations
        first_institute_col = institute_col_list[0]
        filt_auth_affil_ = authaddr_auth_df[first_institute_col]==1
        for institute_col_idx, institute_col in enumerate(institute_col_list):
            if institute_col_idx!=0:
                filt_auth_affil_ = filt_auth_affil_ | (authaddr_auth_df[institute_col]==1)
    return filt_auth_affil_


def _set_correction_file_params(corpus_year, institute, wf_path):
    """Sets the files paths and sheet names for authors names correction.

    It builds a list of full paths composed of:
    - The path to the file for saving the main data of the dropped publications;
    - The path to the file for saving the authors-with-affiliations data of the dropped publications;
    - The path to the file for correction of authors' names mispelling;
    - The path to the file for replacing and removing authors'.
    It also sets the list of sheets'names in this last file.

    Args:
        corpus_year (str): The 4 digits year of the corpus.
        institute (str): The institute's name.
        wf_path (path): Full path to working folder.
    Returns:
        (tup): Composed of the built list of full paths and of the list of sheets' names.
    """
    # Setting useful aliases
    drop_articles_folder = bm_pg.ARCHI_YEAR["merge folder name"]
    drop_articles_file = bm_pg.ARCHI_YEAR["drop articles file name"]
    drop_authaddr_file = bm_pg.ARCHI_YEAR["drop authaffils file name"]
    orphan_treat_root = bm_pg.ARCHI_ORPHAN["root"]
    orthograph_file_name = bm_pg.ARCHI_ORPHAN["orthograph file"]
    complements_file_name = bm_pg.ARCHI_ORPHAN["complementary file"]
    replace_sheet = bm_pg.SHEET_NAMES_ORPHAN['to replace']
    remove_sheet = bm_pg.SHEET_NAMES_ORPHAN["to remove"] + institute

    # Setting useful path
    year_drop_articles_folder = Path(corpus_year) / Path(drop_articles_folder)
    drop_articles_path = wf_path / Path(year_drop_articles_folder) / Path(drop_articles_file)
    drop_authaddr_path = wf_path / Path(year_drop_articles_folder) / Path(drop_authaddr_file)
    ortho_path = wf_path / Path(orphan_treat_root) / Path(orthograph_file_name)
    complements_path = wf_path / Path(orphan_treat_root) / Path(complements_file_name)

    paths_list = [drop_articles_path, drop_authaddr_path, ortho_path, complements_path]
    sheets_list = [replace_sheet, remove_sheet]

    return paths_list, sheets_list


def _read_useful_parsing_data(dedup_read_params):
    """Reads the saved data of publications, addresses, authors and authors 
    with affiliations resulting from the parsing step.

    It uses the `read_final_dedup` function of the `bmfuncts.useful_functs` module.

    Args:
        dedup_read_params (list): Composed of the 4 digits year of the corpus, \
        of the dict giving the name of the parsing file for each parsed item \
        and of the full path to the folder where final results are saved.
    Returns:
        (dict): Keyed by the selected items-keys (str) and valued by the corresponding \
        parsing data (dataframe).
    """
    # Getting the dict of deduplication results
    dedup_parsing_dict = read_final_dedup(dedup_read_params)

    select_items_dict = {key:dedup_parsing_dict[key] for key in bm_pg.PARSING_KEYS_DIC['merge']}
    return select_items_dict


def _get_parsing_data(params_list, bp_cols_list):
    """Gets the publications' main data, the authors' data and the authors-with-affiliations' data 
    resulting from the parsing process.

    The parsing data are read through the `_read_useful_parsing_data` internal function. 
    For the case of added publications' data from HAL database, the partial affiliations 
    are corrected through the `_check_added_dois_affil` internal function.

    Args:
        params_list (list): Composed of the 4 digits year of the corpus (str), \
        of the print parameters (list), of the Institute's name (str), \
        of the org_tup (tup) that contains parameters of Institute's organization, \
        of the full path to working folder (path), of the data combination \
        type of corpuses databases (str) and of the dict giving the name of the parsing file \
        for each parsed item.
        bp_cols_list (list): the list of useful col names as set through the `_set_useful_bp_cols` \
        internal function.
    Returns:
        (list): Composed of the publications' main data (dataframe), of the authors' data (dataframe), \
        and of the authors-with-affiliations' data (dataframe).
    """
    # Setting parameters values from params_list
    (corpus_year, print_params, _, _, wf_path, datatype,
     parsing_filenames_dict) = params_list

    txt_len = print_temp_text(f"{bm_pg.TAB*2}- Reading useful parsing data...", txt_end=True)

    # Setting input-data paths
    final_results_path = set_results_folder_path(wf_path, datatype)

    # Getting the useful parsing results
    dedup_read_params = [corpus_year, parsing_filenames_dict, final_results_path]
    select_items_dict = _read_useful_parsing_data(dedup_read_params)
    articles_df, _, authors_df, authaddr_df = list(select_items_dict.values())

    print_step_text(f"{bm_pg.TAB*2}- Publications' main data, authors's data and "
                    "authors-with-affiliations got from parsing results",
                    print_params, prev_txt_len=txt_len)

    if datatype=="Scopus-HAL & WoS":
        # Checking affiliations for added DOIs from HAL
        authaddr_df = _check_added_dois_affil(params_list, select_items_dict, bp_cols_list)
    parsing_dfs_list = [articles_df, authors_df, authaddr_df]
    return parsing_dfs_list


def _recasting_authors_data(authors_df, recast_cols_list, print_params):
    """Recasts the data with one row per Institute's author for each publication 
    by formatting the authors fullnames and their redistribution into lastnames 
    and firstnames' initials.

    Args:
        authors_df (dataframe): Data of publication IDs list with one row per author \
        resulting from the parsing step.
        recast_cols_list (list): The names (str) of the columns to be used for authors' \
        names recast (fullname, lastname, firstname, co-author name).
        print_params (list): The parameters for the prints to the log file and to the console.
    Returns:
        (dataframe): The recast data.
    """
    txt_len = print_temp_text(f"{bm_pg.TAB*3}- Recasting authors' names in authors' data "
                              "of parsing results...", txt_end=True)
    # Setting useful alias
    fullname_col, lastname_col, firstname_col, co_auth_col = recast_cols_list

    # Transforming to uppercase the co-author's name
    authors_df[co_auth_col] = authors_df[co_auth_col].str.upper()

    # Splitting the Ico-author's name to firstname initials and lastname
    # and putting them as a tuple in column 'fullname_col'
    col_in, col_out = co_auth_col, fullname_col
    authors_df[col_out] = authors_df.apply(lambda row: _split_lastname_firstname(row[col_in]), axis=1)

    # Splitting tuples of column 'fullname_col' into the two columns 'lastname_col' and 'firstname_col'
    col_in = fullname_col
    col1_out, col2_out = lastname_col, firstname_col
    authors_df[[col1_out, col2_out]] = pd.DataFrame(authors_df[col_in].tolist())

    # Recasting tuples (NAME, INITIALS) into a single string 'NAME INITIALS'
    col_in = fullname_col
    authors_df[col_in] = authors_df[col_in].apply(lambda x: ' '.join(x))  # pylint: disable=unnecessary-lambda
    print_step_text(f"{bm_pg.TAB*3}- Author's name recast to lastname and first-name initials "
                    "in authors' data of parsing results", print_params, prev_txt_len=txt_len)
    return authors_df


def _check_names_spelling(init_df, ortho_path, enhance_cols_list, print_params, progress_params):
    """Replace author names in 'init_df' dataframe by the employee's name.

    This is done when a name-spelling discrepancy is given in the dedicated XLSX file. 
    Beforehand, the fullname given by this file is standardized through the `standardize_txt` 
    function imported from `bmfuncts.useful_functs` module.

    Args:
        init_df (dataframe): Publications list with one row per author \
        where author names should be corrected.
        ortho_path (path): The full path to the file of the misspelled names.
        enhance_cols_list (list): Two lists of column names as set in the `_enhance_input_data` \
        internal function.
        print_params (list): The parameters for the prints to the log file and to the console.
        progress_params (list): # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!.
    Returns:
        (dataframe): Publications list with one row per author where \
        spelling of author names have been corrected.
    """
    # Setting parameters from args
    bm_auth_names_list, bm_ortho_cols_list = enhance_cols_list
    (pub_fullname_col, pub_last_name_col, pub_first_name_col) = bm_auth_names_list
    (ortho_lastname_init, ortho_initials_init, ortho_lastname_new, ortho_initials_new) = bm_ortho_cols_list

    # Reading the file giving the misspelled names
    ortho_col_list = list(bm_pg.COL_NAMES_ORTHO.values())
    warnings.simplefilter(action='ignore', category=UserWarning)
    ortho_df = pd.read_excel(ortho_path, usecols=ortho_col_list,
                             keep_default_na=False)

    # Standardizing the names
    for col in bm_ortho_cols_list:
        ortho_df[col] = ortho_df[col]. apply(standardize_txt)

    txt_len, full_names_nb, names_nb, progress_step = 0, len(init_df), 0, 0
    progress_callback, init_progress_state, final_progress_state = progress_params
    if progress_callback:
        progress_step = (final_progress_state - init_progress_state) / full_names_nb

    new_df = pd.DataFrame()
    for _, pub_row in init_df.iterrows():
        names_nb += 1
        txt_len = print_temp_text(f"{bm_pg.TAB*3}- Correcting misspelling of authors' names:"
                                  f"{bm_pg.TAB}{names_nb} / {full_names_nb}", txt_end=True)
        lastname_init = str(pub_row[pub_last_name_col])
        initials_init = str(pub_row[pub_first_name_col])
        new_pub_row = pub_row.copy()
        for _, ortho_df_row in ortho_df.iterrows():
            lastname_pub_ortho = str(ortho_df_row[ortho_lastname_init])
            initials_pub_ortho = str(ortho_df_row[ortho_initials_init])
            if lastname_init==lastname_pub_ortho and initials_init==initials_pub_ortho:
                lastname_eff_ortho = str(ortho_df_row[ortho_lastname_new])
                initials_eff_ortho = str(ortho_df_row[ortho_initials_new])
                new_pub_row[pub_last_name_col] = lastname_eff_ortho
                new_pub_row[pub_first_name_col] = initials_eff_ortho
                new_pub_row[pub_fullname_col] = lastname_eff_ortho + ' ' + initials_eff_ortho
        new_df = concat_dfs([new_df, new_pub_row.to_frame().T], concat_ignore_index=True)
        if progress_callback:
            progress_callback(init_progress_state + progress_step * names_nb)
    print_step_text(f"{bm_pg.TAB*3}- Misspelling of authors' names corrected",
                    print_params, prev_txt_len=txt_len)
    return new_df


def _build_authors_full_list(authors_df, full_authors_cols_list, print_params):
    """Builds the data of authors full-list per publications.

    Args:
        authors_df (dataframe): Data of publication IDs list with one row per author \
        resulting from the parsing step.
        full_authors_cols_list (list): Column names as set in the `_enhance_input_data` \
        internal function.
        print_params (list): The parameters for the prints to the log file and to the console.
    Returns:
        (dataframe): The built data.
    """
    txt_len = print_temp_text(f"{bm_pg.TAB*3}- Building Full list of authors per publication...",
                              txt_end=True)
    (pub_id_col, co_auth_col, fullname_col,
     authors_list_col) = full_authors_cols_list
    if bm_pg.AUTHORS_FULL_LIST_NAME_CORRECTION:
        co_auth_col = fullname_col
    data = []
    for pub_id, pub_id_authors_df in authors_df.groupby(pub_id_col):
        init_authors_list = pub_id_authors_df[co_auth_col].to_list()
        authors_list = []
        for author in init_authors_list:
            new_author = standardize_full_name_order(author)
            authors_list.append(new_author)
        authors_str = ", ".join(authors_list)
        data.append([pub_id, authors_str])
    pub_authors_df = pd.DataFrame(data, columns=[pub_id_col, authors_list_col])
    print_step_text(f"{bm_pg.TAB*3}- Full list of authors per publication built",
                    print_params, prev_txt_len=txt_len)
    return pub_authors_df


def _enhance_input_data(parsing_dfs_list, enhance_params,
                        enhance_cols, enhance_cols_list, ortho_path, progress_params):
    """Enhances the publications' main data, the authors' data and the authors-with-affiliations' data 
    resulting from the parsing process.

    This is done through the following steps:
    1. A column with the corpus year is added to the publication's main data.
    2. In the authors' data, the authors' fullnames are split into lastname and \
    firstname initials through the `_recasting_authors_data` internal function.
    3. The misspelling of authors' names in the recast authors' data are corrected \
    through the `_check_names_spelling` internal function.
    4. The data of full list of authors per publications are built through the \
    `_build_authors_full_list` internal function and merged into the publications' main data.
    5. Finally, the authors' data are merged into the authors-with-affiliations' data.

    Args:
        parsing_dfs_list (list): Composed of the publications' main data (dataframe), \
        of the authors' data (dataframe), and of the authors-with-affiliations' data (dataframe).
        enhance_params (list): Composed of the 4 digits year of the corpus (str) and of the print parameters (list).
        enhance_cols (list): Column names as set in the `build_institute_pubs_authors_data` \
        main function of this module through the `_set_useful_bp_cols` internal function.
        enhance_cols_list (list): Lists of column names as set in the `build_institute_pubs_authors_data` \
        main function of this module through the `_set_useful_bm_cols` internal function.
        ortho_path (path): The full path to the file for correction of misspelled author names.
        progress_params (list): # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!.
    Returns:
        (list): Composed of the enhanced publications' main data (dataframe) and of \
        the merged data (dataframe) of the authors' data into the authors-with-affiliations' data.
    """
    progress_callback, init_progress_state, final_progress_state = [None] * 3
    if progress_params:
        progress_callback, init_progress_state, final_progress_state = progress_params

    # Setting parameters values from args
    articles_df, authors_df, authaddr_df = parsing_dfs_list
    corpus_year, print_params = enhance_params
    pub_id_col, auth_idx_col, co_auth_col, corpus_year_col, authors_list_col = enhance_cols
    bm_auth_names_list = enhance_cols_list[0]

    print_step_text(f"{bm_pg.TAB*2}- Enhancing parsing data...", print_params)

    # Adding new column with year of initial publication which is the corpus year
    articles_df[corpus_year_col] = corpus_year

    # Recasting the authors data
    recast_cols_list = bm_auth_names_list + [co_auth_col]
    authors_df = _recasting_authors_data(authors_df, recast_cols_list, print_params)
    inter_progress_params = [None] * 3
    if progress_params:
        inter_progress_state = (final_progress_state - init_progress_state) / 3
        inter_progress_params = [progress_callback, inter_progress_state, final_progress_state]
        progress_callback(inter_progress_state)

    # Checking authors name spelling and correct them
    authors_df = _check_names_spelling(authors_df, ortho_path, enhance_cols_list, print_params,
                                       inter_progress_params)

    # Adding column of full authors list
    fullname_col = bm_auth_names_list[0]
    full_authors_cols_list = [pub_id_col, co_auth_col, fullname_col, authors_list_col]
    pub_authors_df = _build_authors_full_list(authors_df, full_authors_cols_list, print_params)
    enhanced_articles_df =  articles_df.merge(pub_authors_df, how='right', on=pub_id_col)
    if progress_params:
        progress_callback(final_progress_state)

    # Combining name of author to author ID with affiliation by publication ID
    merge_cols = [pub_id_col, auth_idx_col]
    authaddr_auth_df = authaddr_df.merge(authors_df, how='inner', left_on=merge_cols,
                                         right_on=merge_cols)
    enhanced_dfs_list = [enhanced_articles_df, authaddr_auth_df]
    if progress_params:
        progress_callback(final_progress_state)
    return enhanced_dfs_list


def _check_names_to_replace(corpus_year, init_df, complements_path, replace_sheet,
                            bm_auth_names_list, bm_compl_cols_list, print_params):
    """Replace author names in 'init_df' dataframe by the correct author name.

    This is done when metadata error is reported for specified publications in the dedicated XLSX file.

    Args:
        corpus_year (str): Corpus year of publications list.
        init_df (dataframe): Publications list with one row per author where author names \
        should be corrected.
        complements_path (path): The full path to the file where the metadata errors are reported.
        replace_sheet (str): The name of the sheet where the metadata errors are reported.
        bm_auth_names_list (list): Useful column names in 'init_df' data (fullname, lastname, firstname).
        bm_compl_cols_list (list): Useful column names in the complementary (publication lastname, \
        publication firstname, employee lastname, employee firstname, corpus year).
        print_params (list): The parameters for the prints to the log file and to the console.
    Returns:
        (dataframe): Publications list with one row per author where author names have been \
        corrected for specific publications.
    """
    # Setting parameters from args
    (pub_fullname_col, pub_last_name_col, pub_first_name_col) = bm_auth_names_list
    (compl_lastname_init, compl_initials_init, compl_lastname_new,
     compl_initials_new, compl_year_pub) = bm_compl_cols_list

    # Reading the file reporting metadata errors
    compl_col_list = list(bm_pg.COL_NAMES_COMPL.values())
    warnings.simplefilter(action='ignore', category=UserWarning)
    compl_df = pd.read_excel(complements_path, sheet_name=replace_sheet,
                             usecols=compl_col_list, keep_default_na=False)

    # Standardizing the names
    for col in bm_compl_cols_list[:-1]:
        compl_df[col] = compl_df[col].apply(standardize_txt)

    # Getting the information of the year in the complementary file
    year_compl_df = compl_df[compl_df[compl_year_pub]==int(corpus_year)]
    year_compl_df = year_compl_df.reset_index()

    txt_len = 0
    full_names_nb, names_nb = len(init_df), 0
    new_df = pd.DataFrame()
    for _, pub_row in init_df.iterrows():
        names_nb += 1
        txt_len = print_temp_text(f"{bm_pg.TAB*3}- Checking authors' to replace:"
                                  f"{bm_pg.TAB}{names_nb} / {full_names_nb}", txt_end=True)
        lastname_init = str(pub_row[pub_last_name_col])
        initials_init = str(pub_row[pub_first_name_col])
        new_pub_row = pub_row.copy()
        for _, year_compl_row in year_compl_df.iterrows():
            lastname_pub_compl = str(year_compl_row[compl_lastname_init])
            initials_pub_compl = str(year_compl_row[compl_initials_init])
            if lastname_init==lastname_pub_compl and initials_init==initials_pub_compl:
                lastname_eff_compl = str(year_compl_row[compl_lastname_new])
                initials_eff_compl = str(year_compl_row[compl_initials_new])
                new_pub_row[pub_last_name_col] = lastname_eff_compl
                new_pub_row[pub_first_name_col] = initials_eff_compl
                new_pub_row[pub_fullname_col] = lastname_eff_compl + ' ' + initials_eff_compl
        new_df = concat_dfs([new_df, new_pub_row.to_frame().T], concat_ignore_index=True)
    print_step_text(f"{bm_pg.TAB*3}- False authors' names replaced", print_params,
                    prev_txt_len=txt_len)
    return new_df


def _check_authors_to_remove(pub_df, outliers_path, outliers_sheet, bm_auth_names_list,
                             bm_outliers_cols_list, print_params):
    """Drops rows of authors to be removed in the publications' data.

    The authors to remove are reported in the dedicated xlsx file.

    Args:
        pub_df (dataframe): Publications' list with one row per author where rows should be dropped.
        outliers_path (path): The full path to the file where the authors to remove are reported.
        outliers_sheet (str): The name of the sheet where the authors to remove are reported.
        bm_auth_names_list (list): Useful column names in 'pub_df' data (lastname col, firstname col).
        bm_outliers_cols_list (list): Useful column names in the outliers (lastname col, firstname-initials col).
        print_params (list): The parameters for the prints to the log file and to the console.
    Returns:
        (dataframe): Publications' list with one row per author where rows of authors to be removed have been dropped.
    """
    # Setting parameters from args
    pub_last_col, pub_initials_col = bm_auth_names_list[1:]
    outliers_lastname_col, outliers_initials_col = bm_outliers_cols_list

    # Reading the file giving the outliers
    warnings.simplefilter(action='ignore', category=UserWarning)
    outliers_df = pd.read_excel(outliers_path, sheet_name=outliers_sheet,
                                usecols=bm_outliers_cols_list, keep_default_na=False)

    # Standardizing the names
    for col in bm_outliers_cols_list:
        outliers_df[col] = outliers_df[col].apply(standardize_txt)

    # Searching for the outliers in the data to update by lastname and initials
    txt_len = 0
    full_names_nb, names_nb = len(pub_df), 0
    drop_df = pd.DataFrame(columns=list(pub_df.columns))
    for _, pub_row in pub_df.iterrows():
        names_nb += 1
        txt_len = print_temp_text(f"{bm_pg.TAB*2}- Checking authors' to remove..."
                                  f"{bm_pg.TAB}{names_nb} / {full_names_nb}", txt_end=True)
        pub_lastname = str(pub_row[pub_last_col])
        pub_initials = str(pub_row[pub_initials_col])
        for _, outliers_row in outliers_df.iterrows():
            outliers_lastname = str(outliers_row[outliers_lastname_col])
            outliers_initials = str(outliers_row[outliers_initials_col])
            if pub_lastname==outliers_lastname and pub_initials==outliers_initials:
                # Setting the row to drop as a dataframe
                row_to_drop_df = pub_row.to_frame().T
                # Appending the row to drop to the datathat will contain all the rows to drop
                drop_df = concat_dfs([drop_df, row_to_drop_df], concat_ignore_index=True)

    # Removing the rows to drop from the dataframe to update
    new_pub_df = concat_dfs([pub_df, drop_df], keep="False")
    print_step_text(f"{bm_pg.TAB*3}- External authors removed", print_params,
                    prev_txt_len=txt_len)
    return new_pub_df


def _reorder_cols(institute_merged_df, reorder_cols_list, print_params):
    """Reorders the columns of the data with one row per Institute's author for each publication.

    The columns of fullname, lastname and firstname initials are set at the end of the data. 
    The column of full-authors list is set just before the first author of the publication in place 
    of the initial position of the full-name column. It uses the `reorder_df` function imported 
    from `bmfuncts.useful_functs` module.

    Args:
        institute_merged_df (dataframe): Data of publication IDs list with one row per author where \
        authors fullname has been formatted and split into lastname and firstname initials \
        and the misspelled names have been corrected.
        reorder_cols_list (list): The names of the columns to be reordered as set in the \
        `_select_institute_auth_pub_data` internal function.
        print_params (list): The parameters for the prints to the log file and to the console.
    Returns:
        (dataframe): The data with reordered columns.
    """
    txt_len = print_temp_text(f"{bm_pg.TAB*2}- Reordering columns...", txt_end=True)
    # Setting parameters from args
    fullname_col, lastname_col, firstname_col, authors_list_col = reorder_cols_list
    init_cols_list = list(institute_merged_df.columns)
    fullname_init_idx = init_cols_list.index(fullname_col)

    col_dict = {authors_list_col : fullname_init_idx,
                fullname_col     : -3,
                lastname_col     : -2,
                firstname_col    : -1,
               }
    new_institute_merged_df = reorder_df(institute_merged_df, col_dict)
    print_step_text(f"{bm_pg.TAB*2}- Columns reordered", print_params, prev_txt_len=txt_len)
    return new_institute_merged_df


def _select_institute_auth_pub_data(enhanced_dfs_list, merge_params, merge_cols, merge_cols_lists,
                                    sheets_list, complements_path):
    """Builds the data of publications' list with one row per Institute's author cleaned through 
    the correction of metadata errors on authors' names and through the drop of authors with 
    inappropriate affiliation to the Institute.

    This is done through the following steps:
    1. A publications list data with one row per author affiliated to the Institute is built using \
    the 'filt_auth_affil' filter got through the `_build_filt_auth_affil` internal function.
    2. Errors on author names resulting from publication metadata errors are corrected through \
    the `_check_names_to_replace` internal function.
    3. The row of authors mistakenly affiliated to the Institute are dropped through \
    the `_check_authors_to_remove` internal function.
    4. Finally, the columns are reordered through the `_reorder_cols` internal function.

    Args:
        enhanced_dfs_list (list): 
        merge_params (list): The list composed of the 4 digits year of the corpus (str), \
        of the print parameters (list) and of the org_tup (tup) that contains parameters \
        of Institute's organization.
        merge_cols (list): Useful column names as set 
        merge_cols_lists
        sheets_list
        complements_path
    Returns:
        (dataframe): The built and cleaned data.
    """
    # Setting parameters from args
    corpus_year, print_params, org_tup = merge_params
    pub_id_col, authors_list_col = merge_cols
    bm_auth_names_list, bm_compl_cols_list, bm_outliers_cols_list = merge_cols_lists
    replace_sheet, remove_sheet = sheets_list
    enhanced_articles_df, authaddr_auth_df = enhanced_dfs_list

    txt_len = print_temp_text(f"{bm_pg.TAB*2}- Selecting publication's data for Institute's authors...",
                              txt_end=True)
    # Building the authors filter of the institution INSTITUTE
    filt_auth_affil = _build_filt_auth_affil(authaddr_auth_df, org_tup)

    # Associating each publication (including its complementary info) with each of its Institute's authors
    # The resulting data contains a row for each Institute's author with the corresponding publication info
    institute_merged_df = authaddr_auth_df[filt_auth_affil].merge(enhanced_articles_df, how='left',
                                                                  left_on=[pub_id_col], right_on=[pub_id_col])
    print_step_text(f"{bm_pg.TAB*2}- Publication's data selected for Institute's authors",
                    print_params, prev_txt_len=txt_len)

    print_step_text(f"{bm_pg.TAB*2}- Cleaning selected publication's data...", print_params)
    # Replacing author names resulting from publication metadata errors
    # Then searching for authors external to Institute but tagged as affiliated to it
    # and dropping their row in the returned dataframe
    institute_merged_df = _check_names_to_replace(corpus_year, institute_merged_df, complements_path,
                                                  replace_sheet, bm_auth_names_list, bm_compl_cols_list,
                                                  print_params)
    institute_merged_df = _check_authors_to_remove(institute_merged_df, complements_path, remove_sheet,
                                                   bm_auth_names_list, bm_outliers_cols_list, print_params)

    # Setting columns order
    reorder_cols_list = bm_auth_names_list + [authors_list_col]
    institute_merged_df = _reorder_cols(institute_merged_df, reorder_cols_list, print_params)
    return institute_merged_df


def _build_and_save_dropped_pub_data(pub_id_col, pub_drop_dfs, pub_drop_paths, print_params):
    """Builds and saves the data of the dropped publications in terms of publications' main data 
    and authors_with_affiliations data for further control.

    Args:
        pub_id_col (str): The name of the columns of publication's identifiers.
        pub_drop_dfs (list): !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!.
        pub_drop_paths (list): Composed of the full paths to the files for saving \
        the main data and the authors_with_affiliations data of the dropped publications.
        print_params (list): The parameters for the prints to the log file and to the console.
    """
    txt_len = print_temp_text(f"{bm_pg.TAB*2}- Building data of dropped publications...", txt_end=True)

    # Setting parameters' values from args
    articles_df, authaddr_df, institute_merged_df = pub_drop_dfs
    drop_articles_path, drop_authaddr_path = pub_drop_paths

    final_pub_ids_list = list(set(institute_merged_df[pub_id_col].to_list()))
    drop_articles_df = articles_df[~articles_df[pub_id_col].isin(final_pub_ids_list)]
    drop_authaddr_df = authaddr_df[~authaddr_df[pub_id_col].isin(final_pub_ids_list)]
    drop_articles_df.to_excel(drop_articles_path, index=False)
    drop_authaddr_df.to_excel(drop_authaddr_path, index=False)
    print_step_text(f"{bm_pg.TAB*2}- Data of dropped publications saved",
                    print_params, prev_txt_len=txt_len)


def build_institute_pubs_authors_data(params_list, progress_params):
    """Builds the publications' data with one row per Institute's author for each publication 
    from the results of the corpus parsing.

    This is done through the following steps:
    1. The parsing results are got through the `_get_parsing_data` internal function.
    2. The parsing results are enhanced through the `_enhance_input_data` internal function.
    3. The data of publications' list with one row per Institute's author with correction \
    of authors' names and drop of authors with inappropriate affiliation to the Institute \
    through the `_select_institute_auth_pub_data` internal function.
    4. Finally, the data of the dropped publications in terms of publications' main data \
    and authors-with-affiliations data are built and saved through \
    the `_build_and_save_dropped_pub_data` internal function.

    Args:
        params_list (list): Composed of the 4 digits year of the corpus (str), of the parameters (list) \
        for the `print_step_text` function imported from the `bmfuncts.useful_functs` module, \
        of the Institute's name (str), of the org_tup (tup) that contains parameters of Institute's \
        organization, of the full path to working folder (path), of the data combination type \
        of corpuses databases (str), and of the dict giving the name of the parsing file for each parsed item.
        progress_params (list): Composed of the function for updating the status of the ProgressBar tkinter widget, \
        of its initial status and of its final status (optional, default: None).
    Returns:
        (dataframe): Publications' list with one row per author with correction of authors' names \
        and drop of authors with inappropriate affiliation to the Institute.
    """
    # Setting parameters values from params_list
    corpus_year, print_params, institute, org_tup, wf_path = params_list[0:5]
    print_step_text(f"{bm_pg.TAB}- Building publications list with authors affiliated "
                    "to the Institute...", print_params)

    # Setting useful cols lists
    bp_cols_list = _set_useful_bp_cols()
    (bm_bonus_cols_list, bm_auth_names_list, bm_ortho_cols_list,
     bm_compl_cols_list, bm_outliers_cols_list) = _set_useful_bm_cols()

    # Setting useful col names
    pub_id_col, auth_idx_col, co_auth_col = bp_cols_list[0:3]
    corpus_year_col, authors_list_col = bm_bonus_cols_list

    # Setting files parameters for authors names correction
    paths_list, sheets_list = _set_correction_file_params(corpus_year, institute, wf_path)

    # Getting input-data from parsing ones
    parsing_dfs_list = _get_parsing_data(params_list, bp_cols_list)

    # Enhancing input_data ( parameters to be defined)
    enhance_params = [corpus_year, print_params]
    enhance_cols = [pub_id_col, auth_idx_col, co_auth_col, corpus_year_col, authors_list_col]
    enhance_cols_list = [bm_auth_names_list, bm_ortho_cols_list]
    ortho_path = paths_list[2]
    enhanced_dfs_list = _enhance_input_data(parsing_dfs_list, enhance_params, enhance_cols,
                                            enhance_cols_list, ortho_path, progress_params)

    # Building publications' data with one row for each Institute's author
    merge_params = [corpus_year, print_params, org_tup]
    merge_cols = [pub_id_col, authors_list_col]
    merge_cols_lists = [bm_auth_names_list, bm_compl_cols_list, bm_outliers_cols_list]
    complements_path = paths_list[3]
    institute_merged_df = _select_institute_auth_pub_data(enhanced_dfs_list, merge_params, merge_cols,
                                                          merge_cols_lists, sheets_list, complements_path)

    # Building and save data of dropped publications
    pub_drop_dfs = parsing_dfs_list[0:2] + [institute_merged_df]
    pub_drop_paths = paths_list[0:2]
    _build_and_save_dropped_pub_data(pub_id_col, pub_drop_dfs, pub_drop_paths, print_params)
    return institute_merged_df
