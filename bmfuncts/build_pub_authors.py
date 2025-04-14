"""Module of functions for building the Institute publications list 
with one row per author taking care of:

- Potential discrepancy between author-name spelling and employee-name spelling;
- Complementary database to the Institute employees database \
with young researchers affiliated to the Institute;
- Inappropriate affiliation to the Institute of external collaborators.

"""

__all__ = ['build_institute_pubs_authors']

# Standard Library imports
import warnings
from pathlib import Path

# 3rd party imports
import pandas as pd
import BiblioParsing as bp

# Local imports
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_user_config
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import reorder_df
from bmfuncts.useful_functs import get_final_dedup
from bmfuncts.useful_functs import save_final_dedup
from bmfuncts.useful_functs import set_saved_results_path
from bmfuncts.useful_functs import standardize_firstname_initials
from bmfuncts.useful_functs import standardize_full_name_order
from bmfuncts.useful_functs import standardize_txt


def _get_hal_added_dois(bibliometer_path, corpus_year):
    """Gets the list of the added DOIS from HAL database.
    Args:
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): Contains the corpus year defined by 4 digits.
    Returns:
        (list): The list of added DOIs.
    """
    doi_col = bp.COL_NAMES['articles'][6]
    extract_root_alias = pg.ARCHI_EXTRACT["root"]
    scopus_extract_root_alias = pg.ARCHI_EXTRACT[bp.SCOPUS]["root"]
    added_dois_file_base_alias = pg.ARCHI_EXTRACT[bp.SCOPUS]["added_dois_file"]
    added_dois_file = corpus_year + added_dois_file_base_alias
    extract_root_path = bibliometer_path / Path(extract_root_alias)
    scopus_extract_path = extract_root_path / Path(scopus_extract_root_alias)
    added_dois_path = Path(scopus_extract_path) / Path(corpus_year) / Path(added_dois_file)
    hal_added_dois_df = pd.read_excel(added_dois_path)
    hal_added_dois_list = hal_added_dois_df[doi_col].to_list()
    return hal_added_dois_list


def _get_doi_pub_id(articles_df, dois_list):
    """Gets data of the publications ID per DOI in the given list of DOIs.

    Args:
        articles_df (dataframe): The data of publications list resulting \
        from the parsing step.
        dois_list (list): The DOIs (str) list for which publications IDs are got.
    Returns:
        (dataframe): The data of the publications ID per DOI.
    """
    pub_id_col = bp.COL_NAMES['articles'][0]
    doi_col = bp.COL_NAMES['articles'][6]
    usecols = [pub_id_col, doi_col]
    dois_df_init = articles_df[usecols]
    dois_pub_id_df = pd.DataFrame(columns=usecols)
    for doi in dois_list:
        doi_df = dois_df_init[dois_df_init['DOI']==doi]
        dois_pub_id_df = concat_dfs([dois_pub_id_df, doi_df])
    return dois_pub_id_df


def _check_added_dois_affil(institute, org_tup, bibliometer_path, corpus_year, dfs_tup):
    """Checks if normalized affiliation attribution is correct for the added DOIs 
    from HAL database and save the corrected files of parsing.

    Args:
        institute (str): The institute name.
        org_tup (tup): Contains parameters of the institute.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): Contains the corpus year defined by 4 digits.
        dfs_tup (tup): (The publications data (dataframe), \
        The addresses data (dataframe), \
        The authors with affiliations data (dataframe)).
    Returns:
         (tup): (The corrected data of addresses (dataframe), \
         The corrected data of authors with affiliations (dataframe)).
    """
    articles_df, addresses_df, authorsinst_df = dfs_tup
    pub_id_col = bp.COL_NAMES['auth_inst'][0]
    address_col = bp.COL_NAMES['auth_inst'][2]
    norm_inst_col = bp.COL_NAMES['auth_inst'][4]
    institute_norm = org_tup[3][0][0]
    inst_col_list = org_tup[4]
    main_inst_idx = org_tup[7]

    # Setting test parameters to include institute in address
    top_inst = 'CEA'.lower()
    town = 'Grenoble'.lower()
    other_inst = ['LITEN', 'LETI', 'IRIG', 'IBS']

    hal_added_dois_list = _get_hal_added_dois(bibliometer_path, corpus_year)
    hal_added_pub_id_df = _get_doi_pub_id(articles_df, hal_added_dois_list)
    hal_added_pub_id_list = hal_added_pub_id_df[pub_id_col].to_list()

    new_authorsinst_df = pd.DataFrame(columns=authorsinst_df.columns)
    for pub_id, pub_df in authorsinst_df.groupby(pub_id_col):
        if pub_id in hal_added_pub_id_list:
            new_pub_df = pd.DataFrame(columns=pub_df.columns)
            for addrs, addr_df in pub_df.groupby(address_col):
                addrs_list = addrs.split("; ")
                new_addrs_list = []
                for addr in addrs_list:
                    addr_lw = addr.lower()
                    exclude_test = any(ext.lower() in addr_lw for ext in other_inst)
                    include_test = top_inst in addr_lw and town in addr_lw and not exclude_test
                    new_addr = addr
                    new_norm_inst = addr_df[norm_inst_col]
                    new_main_inst_idx = addr_df[inst_col_list[main_inst_idx]]
                    if include_test:
                        new_addr = institute + ', ' + addr
                        new_norm_inst = institute_norm
                        new_main_inst_idx = 1
                    new_addrs_list.append(new_addr)
                    new_addrs = "; ".join(new_addrs_list)
                    addr_df[address_col] = new_addrs
                    addr_df[norm_inst_col] = new_norm_inst
                    addr_df[inst_col_list[main_inst_idx]] = new_main_inst_idx
                new_pub_df = concat_dfs([new_pub_df, addr_df])
            new_authorsinst_df = concat_dfs([new_authorsinst_df, new_pub_df])
        else:
            new_authorsinst_df = concat_dfs([new_authorsinst_df, pub_df])

    new_addresses_df = pd.DataFrame(columns=addresses_df.columns)
    for pub_id, pub_df in addresses_df.groupby(pub_id_col):
        if pub_id in hal_added_pub_id_list:
            new_pub_df = pd.DataFrame(columns=pub_df.columns)
            for addr, addr_df in pub_df.groupby(address_col):
                addr_lw = addr.lower()
                exclude_test = any(ext.lower() in addr_lw for ext in other_inst)
                include_test = top_inst in addr_lw and town in addr_lw and not exclude_test
                if include_test:
                    addr_df[address_col] = institute + ', ' + addr
                new_pub_df = concat_dfs([new_pub_df, addr_df])
            new_addresses_df = concat_dfs([new_addresses_df, new_pub_df])
        else:
            new_addresses_df = concat_dfs([new_addresses_df, pub_df])

    return new_addresses_df, new_authorsinst_df


def _retain_firstname_initials(txt):
    """Removes '-' from the initials of the author's 
    first name.

    Args:
        txt (str): The raw initials of the author's \
        first name.
    returns:
        (str): The modifyed initials.
    """
    txt = txt.replace('-',' ')
    initials = ''.join(txt.split(' '))
    return initials


def _split_lastname_firstname(txt, digits_min=4):
    """Sets the lambda function for extracting last_name 
    and first-name initials from the author's name.

    It uses the `_retain_firstname_initials` internal function 
    and the `standardize_txt` function imported from the \
    `bmfuncts.useful_functs` module.

    Args:
        txt (str): The txt from which last name and first-name initials \
        of the author are extracted.
        digits_min (int): The minimum length of the names that contains '-' \
        symbol to be kept in author's last name.
    returns:
        tup): (The extracted last name, the extracted first-name initials).
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


def _build_filt_authors_inst(authorsinst_authors_df, inst_col_list, main_status, main_inst_idx):
    """Builds the `filt_authors_inst_` filter to select the authors by their institution.

    Args:
        authorsinst_authors_df (dataframe): Data of combined name of author to author ID \
        with affiliation by publication ID.
        inst_col_list (list): List of column names (str) that contains \
        affiliation status to the Institute.
        main_status (bool): Status of the combination of 'inst_col_list' columns \
        to identify affiliation to the Institute. 
        main_inst_idx (int): Index of the unique column name in 'inst_col_list' list \
        to be used for the Institute affiliation status for 'main_status' set to False.                    
    Returns:
        (Pandas Series): A filter on specified columns depending on the status \
        of the combination of 'inst_col_list' columns of the 'authorsinst_authors_df' \
        dataframe that sets:

        - True if any in these columns is equal to 1 for the author;
        - False otherwise.
    """
    main_inst_col = inst_col_list[main_inst_idx]
    if main_status:
        filt_authors_inst_ = authorsinst_authors_df[main_inst_col]==1
    else:
        first_inst_col = inst_col_list[0]
        filt_authors_inst_ = authorsinst_authors_df[first_inst_col]==1
        for inst_idx, inst_col in enumerate(inst_col_list):
            if inst_idx!=0:
                filt_authors_inst_ = filt_authors_inst_ | \
                                     (authorsinst_authors_df[inst_col]==1)
    return filt_authors_inst_


def _check_names_spelling(bibliometer_path, init_df, cols_list):
    """Replace author names in 'init_df' dataframe by the employee name.

    This is done when a name-spelling discrepancy is given in the dedicated 
    Excel file named 'orthograph_file_name' and located in the 'orphan_treat_root' 
    folder of the working folder.
    Beforehand, the full name given by this file is standardized through the 
    `standardize_txt` function imported from `bmfuncts.useful_functs` module.

    Args:
        bibliometer_path (path): Full path to working folder.
        init_df (dataframe): Publications list with one row per author \
        where author names should be corrected.
        cols_list (list): Useful column names in 'init_df' dataframe \
        = [full name, last name, first name].
    Returns:
        (dataframe): Publications list with one row per author where \
        spelling of author names have been corrected.
    """

    # Setting parameters from args
    col0, col1, col2 = cols_list
    pub_fullname_col = col0
    pub_last_name_col = col1
    pub_first_name_col = col2

    # Setting useful aliases
    orphan_treat_root = pg.ARCHI_ORPHAN["root"]
    orthograph_file_name = pg.ARCHI_ORPHAN["orthograph file"]
    ortho_lastname_init = pg.COL_NAMES_ORTHO['last name init']
    ortho_initials_init = pg.COL_NAMES_ORTHO['initials init']
    ortho_lastname_new = pg.COL_NAMES_ORTHO['last name new']
    ortho_initials_new = pg.COL_NAMES_ORTHO['initials new']

    # Setting useful path
    ortho_path = bibliometer_path / Path(orphan_treat_root) / Path(orthograph_file_name)

    # Reading data file targeted by 'ortho_path'
    ortho_col_list = list(pg.COL_NAMES_ORTHO.values())
    warnings.simplefilter(action='ignore', category=UserWarning)
    ortho_df = pd.read_excel(ortho_path,
                             usecols=ortho_col_list,
                             keep_default_na=False)
    ortho_df[ortho_lastname_init] = ortho_df[ortho_lastname_init].\
        apply(standardize_txt)
    ortho_df[ortho_lastname_new] = ortho_df[ortho_lastname_new].\
        apply(standardize_txt)
    ortho_df[ortho_initials_init] = ortho_df[ortho_initials_init].\
        apply(standardize_firstname_initials)
    ortho_df[ortho_initials_new] = ortho_df[ortho_initials_new].\
        apply(standardize_firstname_initials)

    new_df = init_df.copy()
    new_df = new_df.reset_index(drop=True)
    for pub_row_num, _ in new_df.iterrows():
        lastname_init = init_df.loc[pub_row_num, pub_last_name_col]
        initials_init = init_df.loc[pub_row_num, pub_first_name_col]
        for ortho_row_num, _ in ortho_df.iterrows():
            lastname_pub_ortho = ortho_df.loc[ortho_row_num, ortho_lastname_init]
            initials_pub_ortho = ortho_df.loc[ortho_row_num, ortho_initials_init]

            if lastname_init==lastname_pub_ortho and initials_init==initials_pub_ortho:
                lastname_eff_ortho = ortho_df.loc[ortho_row_num, ortho_lastname_new]
                initials_eff_ortho = ortho_df.loc[ortho_row_num, ortho_initials_new]
                new_df.loc[pub_row_num, pub_last_name_col] = lastname_eff_ortho
                new_df.loc[pub_row_num, pub_first_name_col] = initials_eff_ortho
                new_df.loc[pub_row_num, pub_fullname_col] = lastname_eff_ortho + \
                                                            ' ' + initials_eff_ortho

    print("    Misspelling of author names corrected")
    return new_df


def _check_names_to_replace(bibliometer_path, year, init_df, cols_list):
    """Replace author names in 'init_df' dataframe by the correct author name.

    This is done when metadata error is reported in the dedicated Excel file named 
    'complements_file_name' at sheet 'compl_to_replace_sheet' and located 
    in the 'orphan_treat_root' folder of the working folder.

    Args:
        bibliometer_path (path): Full path to working folder.
        year (str): Corpus year of publications list.
        init_df (dataframe): Publications list with one row per author \
        where author names should be corrected.
        cols_list (list): Useful column names in 'init_df' dataframe \
        = [full name, last name, first name].
    Returns:
        (dataframe): Publications list with one row per author where \
        author names have been corrected.
    """

    # Setting parameters from args
    col0, col1, col2 = cols_list
    pub_fullname_col = col0
    pub_last_name_col = col1
    pub_first_name_col = col2

    # Setting useful aliases
    orphan_treat_root = pg.ARCHI_ORPHAN["root"]
    complements_file_name = pg.ARCHI_ORPHAN["complementary file"]
    compl_to_replace_sheet = pg.SHEET_NAMES_ORPHAN['to replace']
    compl_lastname_init = pg.COL_NAMES_COMPL['last name init']
    compl_initials_init = pg.COL_NAMES_COMPL['initials init']
    compl_lastname_new = pg.COL_NAMES_COMPL['last name new']
    compl_initials_new = pg.COL_NAMES_COMPL['initials new']
    compl_year_pub = pg.COL_NAMES_COMPL['publication year']

    # Setting useful path
    complements_path = bibliometer_path / Path(orphan_treat_root) / Path(complements_file_name)

    # Getting the information of the year in the complementary file
    compl_col_list = list(pg.COL_NAMES_COMPL.values())
    warnings.simplefilter(action='ignore', category=UserWarning)
    compl_df = pd.read_excel(complements_path,
                             sheet_name=compl_to_replace_sheet,
                             usecols=compl_col_list,
                             keep_default_na=False)
    compl_df[compl_lastname_init] = compl_df[compl_lastname_init].\
        apply(standardize_txt)
    compl_df[compl_lastname_new] = compl_df[compl_lastname_new].\
        apply(standardize_txt)
    compl_df[compl_initials_init] = compl_df[compl_initials_init].\
        apply(standardize_firstname_initials)
    compl_df[compl_initials_new] = compl_df[compl_initials_new].\
        apply(standardize_firstname_initials)
    year_compl_df = compl_df[compl_df[compl_year_pub]==int(year)]
    year_compl_df = year_compl_df.reset_index()

    new_df = init_df.copy()
    for pub_row_num, _ in new_df.iterrows():
        lastname_init = init_df.loc[pub_row_num, pub_last_name_col]
        initials_init = init_df.loc[pub_row_num, pub_first_name_col]
        for compl_row_num, _ in year_compl_df.iterrows():
            lastname_pub_compl = year_compl_df.loc[compl_row_num, compl_lastname_init]
            initials_pub_compl = year_compl_df.loc[compl_row_num, compl_initials_init]
            if lastname_init==lastname_pub_compl and initials_init==initials_pub_compl:

                lastname_eff_compl = year_compl_df.loc[compl_row_num, compl_lastname_new]
                initials_eff_compl = year_compl_df.loc[compl_row_num, compl_initials_new]
                new_df.loc[pub_row_num, pub_last_name_col] = lastname_eff_compl
                new_df.loc[pub_row_num, pub_first_name_col] = initials_eff_compl
                new_df.loc[pub_row_num, pub_fullname_col] = lastname_eff_compl \
                + ' ' + initials_eff_compl

    print("    False author names replaced")
    return new_df


def _check_authors_to_remove(institute, bibliometer_path, pub_df, cols_list):
    """Drops rows of authors to be removed in the 'pub-df' dataframe.

    The authors to remove are reported in the dedicated xlsx 
    file named 'outliers_file_name' at sheet 'outliers_sheet' 
    and located in the 'orphan_treat_root' folder of the working folder.

    Args:
        institute (str): The institute name.
        bibliometer_path (path): Full path to working folder.
        pub_df (dataframe): Publications list with one row per author \
        where rows should be dropped.
        cols_list (list): Useful column names in 'pub_df' dataframe \
        = [last name, first name].
    Returns:
        (dataframe): Publications list with one row per author where \
        rows of authors to be removed have been dropped.
    """

    # Setting parameters from args
    pub_last_col, pub_initials_col = cols_list

    # Setting useful aliases
    orphan_treat_root = pg.ARCHI_ORPHAN["root"]
    outliers_file_name = pg.ARCHI_ORPHAN["complementary file"]
    outliers_sheet = pg.SHEET_NAMES_ORPHAN["to remove"] + institute
    outliers_lastname_col = pg.COL_NAMES_EXT['last name']
    outliers_initials_col = pg.COL_NAMES_EXT['initials']

    # Setting useful path
    outliers_path = bibliometer_path / Path(orphan_treat_root) / Path(outliers_file_name)

    # Reading the file giving the outliers
    warnings.simplefilter(action='ignore', category=UserWarning)
    outliers_df = pd.read_excel(outliers_path,
                                sheet_name=outliers_sheet,
                                usecols=[outliers_lastname_col,
                                         outliers_initials_col],
                                keep_default_na=False)
    outliers_df[outliers_lastname_col] = outliers_df[outliers_lastname_col].\
        apply(standardize_txt)
    outliers_df[outliers_initials_col] = outliers_df[outliers_initials_col].\
        apply(standardize_firstname_initials)

    # Initializing the dataframe that will contain the rows to drop
    # with the same columns names as the dataframe to update
    drop_df = pd.DataFrame(columns=list(pub_df.columns))

    # Searching for the outliers in the dataframe to update by lastname and initials
    for pub_row_num, _ in pub_df.iterrows():
        pub_lastname = pub_df.loc[pub_row_num, pub_last_col]
        pub_initials = pub_df.loc[pub_row_num, pub_initials_col]
        for outliers_row_num, _ in outliers_df.iterrows():
            outliers_lastname = outliers_df.loc[outliers_row_num, outliers_lastname_col]
            outliers_initials = outliers_df.loc[outliers_row_num, outliers_initials_col]
            if pub_lastname==outliers_lastname and pub_initials==outliers_initials:
                # Setting the row to drop as a dataframe
                row_to_drop_df = pub_df.loc[pub_row_num].to_frame().T
                # Appending the row to drop to the dataframe that will contain all the rows to drop
                drop_df = concat_dfs([drop_df, row_to_drop_df], concat_ignore_index=True)

    # Removing the rows to drop from the dataframe to update
    new_pub_df = concat_dfs([pub_df, drop_df], keep=False)

    print("    External authors removed")
    return new_pub_df


def _read_useful_parsing_data(bibliometer_path, saved_results_path,
                              corpus_year, items_list):
    """Reads the saved data of publications, addresses, authors 
    and authors with affiliations resulting from 
    the parsing step.

    It uses the `get_final_dedup` function of 
    the `bmfuncts.useful_functs` module.

    Args:
        bibliometer_path (path): Full path to working folder.
        saved_results_path (path): Full path to the folder \
        where final results are saved.
        corpus_year (str): 4 digits year of the corpus.
        items_list (list): List of items (str) to be read.
    Returns:
        (tup): (The publications data (dataframe), \
         The addresses data (dataframe), \
         The authors data (dataframe), \
         The authors with affiliations data (dataframe)).
    """
    # Setting useful parameters from args
    (articles_item,
     addresses_item,
     authors_item,
     auth_inst_item) = items_list

    # Getting the dict of deduplication results
    dedup_parsing_dict = get_final_dedup(bibliometer_path,
                                         saved_results_path,
                                         corpus_year)

    # Getting ID of each publication with complementary info
    articles_df = dedup_parsing_dict[articles_item]

    # Getting ID of each address with address info
    addresses_df = dedup_parsing_dict[addresses_item]

    # Getting ID of each author with author name
    authors_df = dedup_parsing_dict[authors_item]

    # Getting ID of each author with institution by publication ID
    authorsinst_df = dedup_parsing_dict[auth_inst_item]

    return articles_df, addresses_df, authors_df, authorsinst_df


def _get_input_data(institute, org_tup, bibliometer_path, datatype, corpus_year):
    """Gets the input data through the `_read_useful_parsing_data` internal function 
    and corrects incomplete affiliations for the added DOIs info from HAL database through 
    the `_check_added_dois_affil` internal function.

    Args:
        institute (str): The institute name.
        org_tup (tup): Contains parameters of the institute .
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        corpus_year (str): Contains the corpus year defined by 4 digits.
    Returns:
        (tup): (The built data of articles, The built data of authors, \
        The built data of authors with affiliations).
    """
    # Setting useful aliases
    articles_item_alias = bp.PARSING_ITEMS_LIST[0]
    addresses_item_alias = bp.PARSING_ITEMS_LIST[2]
    authors_item_alias = bp.PARSING_ITEMS_LIST[1]
    auth_inst_item_alias = bp.PARSING_ITEMS_LIST[5]

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, corpus_year, pg.BDD_LIST)
    item_filename_dict = config_tup[2]

    # Setting input-data paths
    saved_results_path = set_saved_results_path(bibliometer_path, datatype)

    # Getting the useful parsing results
    items_list = [articles_item_alias,
                  addresses_item_alias,
                  authors_item_alias,
                  auth_inst_item_alias]
    return_tup = _read_useful_parsing_data(bibliometer_path, saved_results_path,
                                           corpus_year, items_list)
    articles_df, addresses_df, authors_df, authorsinst_df = return_tup

    if datatype=="Scopus-HAL & WoS":
        # Checking affiliations for added DOIs from HAL
        dfs_tup = articles_df, addresses_df, authorsinst_df
        return_tup = _check_added_dois_affil(institute, org_tup, bibliometer_path,
                                             corpus_year, dfs_tup)
        addresses_df, authorsinst_df = return_tup

        # Saving checked parsing data
        dedup_infos = bibliometer_path, datatype, corpus_year
        addresses_file_name_base = item_filename_dict[addresses_item_alias]
        auth_inst_file_name_base = item_filename_dict[auth_inst_item_alias]
        save_final_dedup(addresses_df, addresses_file_name_base,
                         pg.TSV_SAVE_EXTENT, dedup_infos)
        save_final_dedup(authorsinst_df, auth_inst_file_name_base,
                         pg.TSV_SAVE_EXTENT, dedup_infos)

    return articles_df, authors_df, authorsinst_df


def _recasting_authors_df(authors_df, bm_cols_list):
    """Recasts the data with one row per Institute author 
    for each publication by formatting the authors full names and their 
    redistribution into last names and firsnames initials.

    Args:
        authors_df (dataframe): Data of publication IDs list \
        with one row per author resulting from the parsing step. 
        bm_cols_list (list): Useful column names.
    Returns:
        (dataframe): The recast data.
    """
    # Setting useful alias
    bp_co_auth_alias = bp.COL_NAMES['authors'][2]
    bm_fullname_alias, bm_lastname_alias, bm_firstname_alias = bm_cols_list

    # Transforming to uppercase the Institute author name
    # which is in column COL_NAMES['co_author']
    col = bp_co_auth_alias
    authors_df[col] = authors_df[col].str.upper()

    # Splitting the Institute author name to firstname initials and lastname
    # and putting them as a tuple in column COL_NAMES_BM['Full_name']
    col_in, col_out = bp_co_auth_alias, bm_fullname_alias
    authors_df[col_out] = authors_df.apply(lambda row:
                                           _split_lastname_firstname(row[col_in]),
                                           axis=1)

    # Splitting tuples of column COL_NAMES_BM['Full_name']
    # into the two columns COL_NAMES_BM['Last_name'] and COL_NAMES_BM['First_name']
    col_in = bm_fullname_alias # Last_name + firstname initials
    col1_out, col2_out = bm_lastname_alias, bm_firstname_alias
    authors_df[[col1_out, col2_out]] = pd.DataFrame(authors_df[col_in].tolist())

    # Recasting tuples (NAME, INITIALS) into a single string 'NAME INITIALS'
    col_in = bm_fullname_alias # Last_name + firstname initials
    authors_df[col_in] = authors_df[col_in].apply(lambda x: ' '.join(x))  # pylint: disable=unnecessary-lambda
    print("    Author name recast to last name and first-name initials")
    return authors_df


def _build_authors_full_list(authors_df, cols_list):
    """Builds the data of authors full-list per publications.

    Args:
        authors_df (dataframe): Data of publication IDs list \
        with one row per author resulting from the parsing step. 
        cols_list (list): Useful column names.
    Returns:
        (dataframe): The built data.
    """
    bp_pub_id_col, bp_authors_col, fullname_col, authors_list_col = cols_list
    authors_col = bp_authors_col
    if pg.AUTHORS_FULL_LIST_NAME_CORRECTION:
        authors_col = fullname_col
    data = []
    for pub_id, pub_id_authors_df in authors_df.groupby(bp_pub_id_col):
        init_authors_list = pub_id_authors_df[authors_col].to_list()
        authors_list = []
        for author in init_authors_list:
            new_author = standardize_full_name_order(author)
            authors_list.append(new_author)
        authors_str = ", ".join(authors_list)
        data.append([pub_id, authors_str])
    pub_authors_df = pd.DataFrame(data, columns=[bp_pub_id_col, authors_list_col])
    print("    Full list of authors per publication built")
    return pub_authors_df


def _reorder_cols(inst_merged_df, reorder_cols_list):
    """Reorders the columns of the data with one row per Institute's author 
    for each publication.

    The columns of full name, last name and first-name initials are set 
    at the end of the data. The column of full-authors list is set just 
    before the first author of the publication in place of the initial 
    position of the full-name column. It uses the `reorder_df` function 
    imported from `bmfuncts.useful_functs` module.

    Args:
        inst_merged_df (dataframe): Data of publication IDs list \
        with one row per author where authors full name has been \
        formatted and split into last name and firstname initials \
        and the misspelled names have been corrected. 
        reorder_cols_list (list): The names of the columns to be reordered.
    Returns:
        (dataframe): The data with reordered columns.
    """
    fullname_col, lastname_col, firstname_col, authors_list_col = reorder_cols_list
    init_cols_list = list(inst_merged_df.columns)
    fullname_init_idx = init_cols_list.index(fullname_col)

    col_dict = {authors_list_col : fullname_init_idx,
                fullname_col     : -3,
                lastname_col     : -2,
                firstname_col    : -1,
               }
    new_inst_merged_df = reorder_df(inst_merged_df, col_dict)
    return new_inst_merged_df


def build_institute_pubs_authors(institute, org_tup, bibliometer_path, datatype, year):
    """Builds the publications list dataframe with one row per Institute author 
    for each publication from the results of the corpus parsing.

    This is done through the following steps:
    
    1. The parsing results are got through the `_get_input_data` internal function.
    2. The authors data resulting from the parsing step are recast to split \
    authors full name into last name and firstname initials through \
    the `_recasting_inst_merged_df` internal function.
    3. The misspelling of authors name in the recast authors data are corrrected \
    through the `_check_names_spelling` internal function. 
    4. The data of full list of authors per publications are built through the \
    `_build_authors_full_list` internal function.
    5. The data of full list of authors per publications are merged to the data \
    of the list of publications resulting from the parsing step.
    6. A publications list data with one row per author affiliated to the Institute \
    is built using the 'filt_authors_inst' filter got through \
    the `_build_filt_authors_inst` internal function.
    7. Finally, the publications list data are cleaned as follows:
    - Errors on author names resulting from publication metadata errors \
    are corrected through the `_check_names_to_replace` internal function.
    - The row of authors mistakenly affiliated to the Institute are dropped \
    through the `_check_authors_to_remove` internal function.
    - The columns are reordered through the `_reorder_cols` internal function.

    Args:
        institute (str): The institute name.
        org_tup (tup): Contains parameters of the institute .
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year (str): Contains the corpus year defined by 4 digits.
    Returns:
        (dataframe): Publications list with one row per author with correction \
        of author-names and drop of authors with inappropriate affiliation \
        to the Institute.
    """
    # Setting useful col aliases
    bp_pub_id_alias = bp.COL_NAMES['authors'][0]
    bp_auth_idx_alias = bp.COL_NAMES['authors'][1]
    bp_authors_alias = bp.COL_NAMES['authors'][2]
    fullname_alias = pg.COL_NAMES_BM['Full_name']
    lastname_alias = pg.COL_NAMES_BM['Last_name']
    firstname_alias = pg.COL_NAMES_BM['First_name']
    corpus_year_col_alias = pg.COL_NAMES_BONUS['corpus_year']
    authors_list_alias = pg.COL_NAMES_BONUS['liste auteurs']

    # Setting useful cols list
    names_cols_list = [fullname_alias, lastname_alias, firstname_alias]
    full_authors_cols_list = [bp_pub_id_alias, bp_authors_alias, fullname_alias, authors_list_alias]
    reorder_cols_list = names_cols_list + [authors_list_alias]

    # Getting input-data from parsing ones
    return_tup = _get_input_data(institute, org_tup, bibliometer_path,
                                 datatype, year)
    articles_df, authors_df, authorsinst_df = return_tup

    # Adding new column with year of initial publication which is the corpus year
    articles_df[corpus_year_col_alias] = year

    # Recasting the authors data
    authors_df = _recasting_authors_df(authors_df, names_cols_list)

    # Checking authors name spelling and correct them
    authors_df = _check_names_spelling(bibliometer_path, authors_df, names_cols_list)

    # Adding column of full authors list
    pub_authors_df = _build_authors_full_list(authors_df, full_authors_cols_list)
    new_articles_df =  articles_df.merge(pub_authors_df,
                                         how='right',
                                         on=bp_pub_id_alias)

    # Combining name of author to author ID with affiliation by publication ID
    authorsinst_authors_df = authorsinst_df.merge(authors_df,
                                                  how='inner',
                                                  left_on=[bp_pub_id_alias, bp_auth_idx_alias],
                                                  right_on=[bp_pub_id_alias, bp_auth_idx_alias])

    # Building the authors filter of the institution INSTITUTE
    inst_col_list = org_tup[4]
    main_inst_idx = org_tup[7]
    main_status = org_tup[8]
    filt_authors_inst = _build_filt_authors_inst(authorsinst_authors_df,
                                                 inst_col_list,
                                                 main_status, main_inst_idx)

    # Associating each publication (including its complementary info)
    # with each of its INSTITUTE authors
    # The resulting dataframe contains a row for each INSTITUTE author
    # with the corresponding publication info
    inst_merged_df = authorsinst_authors_df[filt_authors_inst].merge(new_articles_df,
                                                                     how='left',
                                                                     left_on=[bp_pub_id_alias],
                                                                     right_on=[bp_pub_id_alias])

    # Replacing author names resulting from publication metadata errors
    # Then searching for authors external to Institute but tagged as affiliated to it
    # and dropping their row in the returned dataframe
    inst_merged_df = _check_names_to_replace(bibliometer_path, year,
                                             inst_merged_df, names_cols_list)
    inst_merged_df = _check_authors_to_remove(institute, bibliometer_path,
                                              inst_merged_df, names_cols_list[1:])

    # Setting columns order
    inst_merged_df = _reorder_cols(inst_merged_df, reorder_cols_list)
    return inst_merged_df
