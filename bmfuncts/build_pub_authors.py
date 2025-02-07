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
from bmfuncts.useful_functs import read_parsing_dict
from bmfuncts.useful_functs import standardize_firstname_initials
from bmfuncts.useful_functs import standardize_txt


def _get_hal_added_dois(bibliometer_path, corpus_year):
    """Gets the list of the added DOIS from HAL database."""
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
    """Gets the publications ID per DOI as a dataframe."""
    pub_id_col = bp.COL_NAMES['articles'][0]
    doi_col = bp.COL_NAMES['articles'][6]
    usecols = [pub_id_col, doi_col]
    dois_df_init = articles_df[usecols]
    dois_pub_id_df = pd.DataFrame(columns=usecols)
    for doi in dois_list:
        doi_df = dois_df_init[dois_df_init['DOI']==doi]
        dois_pub_id_df = concat_dfs([dois_pub_id_df, doi_df])
#        dois_pub_id_df = pd.concat([dois_pub_id_df, doi_df])
    return dois_pub_id_df


def _check_added_dois_affil(institute, org_tup, bibliometer_path, corpus_year, dfs_tup):
    """Checks if normalized affiliation attribution is correct 
    for the added DOIS from HAL database."""
    articles_df, authorsinst_authors_df = dfs_tup
    pub_id_col = bp.COL_NAMES['auth_inst'][0]
    address_col = bp.COL_NAMES['auth_inst'][2]
    morm_inst_col = bp.COL_NAMES['auth_inst'][4]
    institute_norm = org_tup[3][0][0]
    inst_col_list = org_tup[4]
    main_inst_idx = org_tup[7]
    top_inst = 'CEA'

    hal_added_dois_list = _get_hal_added_dois(bibliometer_path, corpus_year)
    hal_added_pub_id_df = _get_doi_pub_id(articles_df, hal_added_dois_list)
    hal_added_pub_id_list = hal_added_pub_id_df[pub_id_col].to_list()
    new_authorsinst_authors_df = pd.DataFrame(columns=authorsinst_authors_df.columns)
    for pub_id, pub_df in authorsinst_authors_df.groupby(pub_id_col):
        if pub_id in hal_added_pub_id_list:
            new_pub_df = pd.DataFrame(columns=pub_df.columns)
            for addr, addr_df in pub_df.groupby(address_col):
                if top_inst in addr and (institute.lower() not in addr.lower()):
                    addr_df[address_col] = institute + ', ' + addr
                    addr_df[morm_inst_col] = institute_norm
                    addr_df[inst_col_list[main_inst_idx]] = 1
                new_pub_df = concat_dfs([new_pub_df, addr_df])
#                new_pub_df = pd.concat([new_pub_df, addr_df])
            new_authorsinst_authors_df = concat_dfs([new_authorsinst_authors_df, new_pub_df])
#            new_authorsinst_authors_df = pd.concat([new_authorsinst_authors_df, new_pub_df])
        else:
            new_authorsinst_authors_df = concat_dfs([new_authorsinst_authors_df, pub_df])
#            new_authorsinst_authors_df = pd.concat([new_authorsinst_authors_df, pub_df])
    return new_authorsinst_authors_df


def _retain_firstname_initials(row):
    row = row.replace('-',' ')
    initials = ''.join(row.split(' '))
    return initials


def _split_lastname_firstname(row, digits_min=4):
    names_list = row.split()
    first_names_list = names_list[-1:]
    last_names_list = names_list[:-1]
    for name_idx, name in enumerate(last_names_list):

        if len(name)<digits_min and ('-' in name):
            first_names_list.append(name)
            first_names_list = first_names_list[::-1]
            last_names_list = last_names_list[:name_idx] + last_names_list[(name_idx + 1):]

    first_name_initials = _retain_firstname_initials((' ').join(first_names_list))
    last_name = standardize_txt((' ').join(last_names_list))
    return (last_name, first_name_initials)


def _build_filt_authors_inst(authorsinst_authors_df, inst_col_list, main_status, main_inst_idx):
    """Builds the `filt_authors_inst_` filter to select the authors by their institution.

    Args:
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


def _check_names_spelling(bibliometer_path, init_df, cols_tup):
    """Replace author names in 'init_df' dataframe by the employee name.

    This is done when a name-spelling discrepency is given in the dedicated 
    Excel file named 'orthograph_file_name' and located in the 'orphan_treat_root' 
    folder of the working folder.
    Beforehand, the full name given by this file is standardized through the 
    `standardize_txt` function imported from `bmfuncts.useful_functs` module.

    Args:
        bibliometer_path (path): Full path to working folder.
        init_df (dataframe): Publications list with one row per author \
        where author names should be corrected.
        cols_tup (tup): Tuple of useful column names in 'init_df' dataframe \
        = (full name, last name, first name).
    Returns:
        (dataframe): Publications list with one row per author where \
        spelling of author names have been corrected.
    """

    # Setting parameters from args
    col0, col1, col2 = cols_tup
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

    print("Mispelling of author names corrected")
    return new_df


def _check_names_to_replace(bibliometer_path, year, init_df, cols_tup):
    """Replace author names in 'init_df' dataframe by the correct author name.

    This is done when metadata error is reported in the dedicated Excel file named 
    'complements_file_name' at sheet 'compl_to_replace_sheet' and located 
    in the 'orphan_treat_root' folder of the working folder.

    Args:
        bibliometer_path (path): Full path to working folder.
        year (str): Corpus year of publications list.
        init_df (dataframe): Publications list with one row per author \
        where author names should be corrected.
        cols_tup (tup): Tuple of useful column names in 'init_df' dataframe \
        = (full name, last name, first name).
    Returns:
        (dataframe): Publications list with one row per author where \
        author names have been corrected.
    """

    # Setting parameters from args
    col0, col1, col2 = cols_tup
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

    print("False author names replaced")
    return new_df


def _check_authors_to_remove(institute, bibliometer_path, pub_df, cols_tup):
    """Drops rows of authors to be removed in the 'pub-df' dataframe.

    The authors to remove are reported in the dedicated Excel 
    file named 'outliers_file_name' at sheet 'outliers_sheet' 
    and located in the 'orphan_treat_root' folder of the working folder.

    Args:
        institute (str): Institute name.
        bibliometer_path (path): Full path to working folder.
        pub_df (dataframe): Publications list with one row per author \
        where rows should be dropped.
        cols_tup (tup): Tuple of useful column names in 'pub_df' dataframe \
        = (last name, first name).
    Returns:
        (dataframe): Publications list with one row per author where \
        rows of authors to be removed have been dropped.
    """

    # Setting parameters from args
    pub_last_col, pub_initials_col = cols_tup

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
#                drop_df = pd.concat([drop_df, row_to_drop_df], ignore_index=True)

    # Removing the rows to drop from the dataframe to update
    new_pub_df = concat_dfs([pub_df, drop_df], keep=False)
#    new_pub_df = pd.concat([pub_df, drop_df]).drop_duplicates(keep=False)

    print("External authors removed")
    return new_pub_df


def build_institute_pubs_authors(institute, org_tup, bibliometer_path, datatype, year):
    """Builds the publications list dataframe with one row per Institute author 
    for each publication from the results of the corpus parsing.

    First, the parsing results are got through the `read_parsing_dict` function 
    imported from `bmfuncts.useful_functs` module. 
    After that, a publications list dataframe with one row per author affiliated 
    to the Institute is built using the 'filt_authors_inst_' filter. 
    Then, the dataframe is complemented with useful new columns 
    of full name, last name and first name of authors after standardization of 
    last name through the `standardize_txt` function. imported from 
    `bmfuncts.useful_functs` module. 
    Finally, the dataframe is cleaned as follows:

    - Author-name spelling is corrected through the `_check_names_spelling` \
    internal function;
    - Errors on author names resulting from publication metadata errors \
    are corrected through the `_check_names_to_replace` internal function.
    - The row of authors mistakenly affiliated to the Institute are dropped \
    through the `_check_authors_to_remove` internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        datatype (str): Data combination type from corpuses databases.
        year (str): Contains the corpus year defined by 4 digits.
    Returns:
        (dataframe): Publications list with one row per author with correction \
        of author-names and drop of authors with inappropriate affiliation \
        to the Institute.

    """

    # Setting useful col list
    bp_auth_col_list = bp.COL_NAMES['authors']
    bp_pub_id_alias = bp_auth_col_list[0]
    bp_auth_idx_alias = bp_auth_col_list[1]
    bp_co_auth_alias = bp_auth_col_list[2]

    # Setting useful aliases
    articles_item_alias = bp.PARSING_ITEMS_LIST[0]
    authors_item_alias = bp.PARSING_ITEMS_LIST[1]
    auth_inst_item_alias = bp.PARSING_ITEMS_LIST[5]
    bm_colnames_alias = pg.COL_NAMES_BM
    corpus_year_col_alias = pg.COL_NAMES_BONUS['corpus_year']

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    config_tup = set_user_config(bibliometer_path, year, pg.BDD_LIST)
    parsing_path_dict, item_filename_dict = config_tup[1], config_tup[2]

    # Setting parsing files extension of saved results
    parsing_save_extent = pg.TSV_SAVE_EXTENT

    # Setting path of deduplicated parsings
    dedup_parsing_path = parsing_path_dict['dedup']

    # Getting the dict of deduplication results
    dedup_parsing_dict = read_parsing_dict(dedup_parsing_path, item_filename_dict,
                                           parsing_save_extent)

    # Getting ID of each author with institution by publication ID
    authorsinst_df = dedup_parsing_dict[auth_inst_item_alias]

    # Getting ID of each author with author name
    authors_df = dedup_parsing_dict[authors_item_alias]

    # Getting ID of each publication with complementary info
    articles_df = dedup_parsing_dict[articles_item_alias]

    # Adding new column with year of initial publication which is the corpus year
    articles_df[corpus_year_col_alias] = year

    # Combining name of author to author ID with institution by publication ID
    authorsinst_authors_df = pd.merge(authorsinst_df,
                                      authors_df,
                                      how='inner',
                                      left_on=[bp_pub_id_alias, bp_auth_idx_alias],
                                      right_on=[bp_pub_id_alias, bp_auth_idx_alias])
    if datatype=="Scopus-HAL & WoS":
        # Checkking affiliations for added DOIs from HAL
        dfs_tup = (articles_df, authorsinst_authors_df)
        authorsinst_authors_df = _check_added_dois_affil(institute, org_tup, bibliometer_path,
                                                         year, dfs_tup)

    # Building the authors filter of the institution INSTITUTE
    inst_col_list = org_tup[4]
    main_inst_idx = org_tup[7]
    main_status = org_tup[8]
    filt_authors_inst = _build_filt_authors_inst(authorsinst_authors_df, inst_col_list,
                                                 main_status, main_inst_idx)

    # Associating each publication (including its complementary info)
    # whith each of its INSTITUTE authors
    # The resulting dataframe contains a row for each INSTITUTE author
    # with the corresponding publication info
    inst_merged_df = pd.merge(authorsinst_authors_df[filt_authors_inst],
                              articles_df,
                              how='left',
                              left_on=[bp_pub_id_alias],
                              right_on=[bp_pub_id_alias])

    # Transforming to uppercase the Institute author name
    # which is in column COL_NAMES['co_author']
    col = bp_co_auth_alias
    inst_merged_df[col] = inst_merged_df[col].str.upper()

    # Splitting the Institute author name to firstname initials and lastname
    # and putting them as a tuple in column COL_NAMES_BM['Full_name']
    col_in, col_out = bp_co_auth_alias, bm_colnames_alias['Full_name']
    inst_merged_df[col_out] = inst_merged_df.apply(lambda row:
                                                   _split_lastname_firstname(row[col_in]),
                                                   axis=1)

    # Splitting tuples of column COL_NAMES_BM['Full_name']
    # into the two columns COL_NAMES_BM['Last_name'] and COL_NAMES_BM['First_name']
    col_in = bm_colnames_alias['Full_name'] # Last_name + firstname initials
    col1_out, col2_out = bm_colnames_alias['Last_name'], bm_colnames_alias['First_name']
    inst_merged_df[[col1_out, col2_out]] = pd.DataFrame(inst_merged_df[col_in].tolist())

    # Recasting tuples (NAME, INITIALS) into a single string 'NAME INITIALS'
    col_in = bm_colnames_alias['Full_name'] # Last_name + firstname initials
    inst_merged_df[col_in] = inst_merged_df[col_in].apply(lambda x: ' '.join(x))  # pylint: disable=unnecessary-lambda


    # Checking author name spelling and correct it then replacing author names
    # resulting from publication metadata errors
    # finally Searching for authors external to Institute but tagged as affiliated to it
    # and dropping their row in the returned dataframe
    names_cols_tup = (bm_colnames_alias['Last_name'],
                      bm_colnames_alias['First_name'])
    cols_tup = (bm_colnames_alias['Full_name'],) + names_cols_tup
    inst_merged_df = _check_names_spelling(bibliometer_path, inst_merged_df, cols_tup)
    inst_merged_df = _check_names_to_replace(bibliometer_path, year,
                                             inst_merged_df, cols_tup)
    inst_merged_df = _check_authors_to_remove(institute, bibliometer_path,
                                              inst_merged_df, names_cols_tup)

    return inst_merged_df
