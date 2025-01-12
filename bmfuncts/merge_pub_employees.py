"""Module of functions for the merge of employees information with the publications list 
of the Institute taking care of:

- Potential discrepancy between author-name spelling and employee-name spelling;
- Complementary database to the Institute employees database \
with young researchers affiliated to the Institute;
- Inappropriate affiliation to the Institute of external collaborators;
- Creation of list of Institute authors with selected attributes;
- Creation of full reference for each publication.

"""

__all__ = ['recursive_year_search']

# Standard Library imports
import os
import warnings
from pathlib import Path

# 3rd party imports
import pandas as pd
import BiblioParsing as bp

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg
from bmfuncts.config_utils import set_user_config
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.useful_functs import read_parsing_dict
from bmfuncts.useful_functs import standardize_txt

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
    warnings.simplefilter(action = 'ignore', category = UserWarning)
    ortho_df = pd.read_excel(ortho_path, usecols = ortho_col_list)
    ortho_df[ortho_lastname_init] = ortho_df[ortho_lastname_init].\
        apply(standardize_txt)
    ortho_df[ortho_lastname_new] = ortho_df[ortho_lastname_new].\
        apply(standardize_txt)

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
    compl_df = pd.read_excel(complements_path, sheet_name=compl_to_replace_sheet,
                             usecols=compl_col_list)
    compl_df[compl_lastname_init] = compl_df[compl_lastname_init].\
        apply(standardize_txt)
    compl_df[compl_lastname_new] = compl_df[compl_lastname_new].\
        apply(standardize_txt)
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
    warnings.simplefilter(action='ignore', category = UserWarning)
    outliers_df = pd.read_excel(outliers_path,
                                sheet_name = outliers_sheet,
                                usecols = [outliers_lastname_col,
                                           outliers_initials_col])

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
                drop_df = pd.concat([drop_df, row_to_drop_df], ignore_index=True)

    # Removing the rows to drop from the dataframe to update
    new_pub_df = pd.concat([pub_df, drop_df]).drop_duplicates(keep=False)

    print("External authors removed")
    return new_pub_df


def _build_institute_pubs_authors(institute, org_tup, bibliometer_path, year):
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
        year (str): Contains the corpus year defined by 4 digits.
    Returns:
        (dataframe): Publications list with one row per author with correction \
        of author-names and drop of authors with inappropriate affiliation \
        to the Institute.

    """

    # Internal functions

    def _retain_firstname_initials(row):
        row = row.replace('-',' ')
        initials = ''.join(row.split(' '))
        return initials

    def _split_lastname_firstname(row, digits_min = 4):
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

    def _build_filt_authors_inst(inst_col_list, main_status, main_inst_idx):
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

    # Building the authors filter of the institution INSTITUTE
    inst_col_list = org_tup[4]
    main_inst_idx = org_tup[7]
    main_status = org_tup[8]
    filt_authors_inst = _build_filt_authors_inst(inst_col_list, main_status, main_inst_idx)

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


def _build_submit_df(empl_df, pub_df, bibliometer_path, test_case = 'No test', verbose = False):
    """Builds a dataframe of the merged employees information with the publication 
    list with one row per author.

    The merge is based on test of similarities between last names and first names 
    of employees and authors. 
    Found homonyms are tagged by 'HOMONYM_FLAG' global imported from globals 
    module imported as pg.

    Args:
        empl_df (dataframe): Employees database of a given year.
        pub_df (dataframe): Institute publications list with one row per author. 
        bibliometer_path (path): Full path to working folder.
        test_case (str): Optional test case for testing the function (default = 'No test').
        verbose (bool): Optional status of prints (default = False).
    Returns:
        (tup): (dataframe of merged employees information with \
        the publications list with one row per Institute author with \
        identified homonyms, dataframe of publications list with \
        one row per author that has not been identified as Institute employee).
    """

    def _orphan_reduction(orphan_lastname, eff_lastname):
        # A bug with "if ' TRAN ' in ' TUAN TRAN ':"
        orphan_lastname = ' ' + orphan_lastname + ' '
        lastname_match_list = []
        for eff_name in eff_lastname:
            if (orphan_lastname in eff_name) or (eff_name in orphan_lastname):
                lastname_match_list.append(eff_name.strip())
        return lastname_match_list

    def _test_full_match(empl_pub_match_df, pub_lastname, emp_useful_cols_alias):
        if verbose:
            if len(empl_pub_match_df)!=0:
                print('\nMatch found for author lastname:', pub_lastname)
                print(' Nb of matches:', len(empl_pub_match_df))
                print(' Employee matricule:',
                      empl_pub_match_df[emp_useful_cols_alias['matricule']].to_list()[0])
                print(' Employee lastname:',
                      empl_pub_match_df[emp_useful_cols_alias['name']].to_list()[0])
            else:
                print('\nNo match for author lastname:', pub_lastname)
                print('  Nb first matches:', len(empl_pub_match_df))

    def _test_similarity(empl_pub_match_df, pub_lastname, emp_useful_cols_alias,
                         lastname_match_list, flag_lastname_match):
        if verbose:
            print('\nSimilarities by orphan reduction for author lastname:', pub_lastname)
            print('  Lastname flag match:', flag_lastname_match)
            print('  Nb similarities by orphan reduction:', len(lastname_match_list))
            print('  List of lastnames with similarities:', lastname_match_list)
            print('  Employee matricules:',
                  empl_pub_match_df[emp_useful_cols_alias['matricule']].to_list())
            print('  Employee lastnames:',
                  empl_pub_match_df[emp_useful_cols_alias['name']].to_list())
            print('  Employee firstnames:',
                  empl_pub_match_df[emp_useful_cols_alias['first_name']].to_list())
            print('  Employee fullnames:',
                  empl_pub_match_df[emp_add_cols_alias['employee_full_name']].to_list())

    def _test_no_similarity(pub_df_row, pub_lastname, bp_colnames_alias, bm_colnames_alias,
                            lastname_match_list, flag_lastname_match):
        if verbose:
            print('\nNo similarity by orphan reduction for author lastname:', pub_lastname)
            print('  Lastname flag match:', flag_lastname_match)
            print('  Nb similarities by orphan reduction:', len(lastname_match_list))
            print('  Orphan full author name:', pub_df_row[bp_colnames_alias['authors'][2]])
            print('  Orphan author lastname:', pub_df_row[bm_colnames_alias['Last_name']])
            print('  Orphan author firstname initials:',
                  pub_df_row[bm_colnames_alias['First_name']])

    def _test_match_of_firstname_initials(pub_df_row, pub_lastname, pub_firstname, eff_firstnames,
                                          bp_colnames_alias, list_idx, eff_lastnames_spec):
        if verbose:
            print('\nInitials for author lastname:', pub_lastname)
            print('  Author fullname:', pub_df_row[bp_colnames_alias['authors'][2]])
            print('  Author firstname initials:', pub_firstname)
            print('\nInitials of matching employees for author lastname:', pub_lastname)
            print('  Employees firstname initials list:', eff_firstnames)
            print('\nChecking initials matching for author lastname:', pub_lastname)
            print('  Nb of matching initials:', len(list_idx))
            print('  Index list of matching initials:', list_idx)
            print('  Employees lastnames list:', eff_lastnames_spec)

    def _save_spec_dfs(temp_df):
        name_suffix = test_name + '.xlsx'
        temp_df.to_excel(checks_path / Path('temp_df_' + name_suffix),
                         index=False)
        empl_pub_match_df.to_excel(checks_path / Path('empl_pub_match_df_' + name_suffix),
                                  index=False)

    # Setting useful aliases
    bp_colnames_alias = bp.COL_NAMES
    bm_colnames_alias = pg.COL_NAMES_BM
    emp_useful_cols_alias = eg.EMPLOYEES_USEFUL_COLS
    emp_add_cols_alias = eg.EMPLOYEES_ADD_COLS

    # Initializing a Data frame that will contains all matches
    # between 'pub_df' author-name and 'empl_df' emmployee-name
    submit_df = pd.DataFrame()

    # Initializing a Data frame that will contains all 'pub_df' author-names
    # which do not match with any of the 'empl_df' emmployee-names
    orphan_df = pd.DataFrame(columns=list(pub_df.columns))

    # Building the set of lastnames (without duplicates) of the dataframe 'empl_df'
    eff_lastnames = set(empl_df[emp_useful_cols_alias['name']].to_list())
    eff_lastnames = [' ' + x + ' ' for x in eff_lastnames]

    # Setting the useful info for testing the function if verbose = True
    # Setting a dict keyed by type of test with values for test states and
    # test name from column [COL_NAMES_BM['Last_name']] of the dataframe 'pub_df'
    # for testing this function for year 2021
    test_dict   = {'Full match'            : [True, True, True,True,True,'SIMONATO'],
                   'Lower value similarity': [False,True, True,True,True,'SILVA' ],
                   'Upper value similarity': [False,True, True,True,True,'TUAN TRAN'],
                   'No similarity'         : [False,False,True,True,True,'LUIS GABRIEL'],
                   'No test'               : [False,False,False,False,False,'None']
                   }
    test_nb = len(test_dict[test_case])-1
    test_name = test_dict[test_case][test_nb]
    test_states = test_dict[test_case][0:test_nb]
    checks_path = Path(bibliometer_path) / Path('Temp_checks')

    # Building submit_df and orphan_df dataframes
    for _, pub_df_row in pub_df.iterrows():

        # Building a dataframe 'empl_pub_match_df' with rows of 'empl_df'
        # where name in column COL_NAMES_BM['Last_name'] of the dataframe 'pub_df'
        # matches with name in column EMPLOYEES_USEFUL_COLS['name'] of the dataframe 'empl_df'

        # Initializing 'empl_pub_match_df' as dataframe
        empl_pub_match_df = pd.DataFrame()

        # Initializing the flag 'flag_lastname_match' as True by default
        flag_lastname_match = True

        # Getting the lastname from pub_df_row row of the dataframe pub_df
        pub_lastname = pub_df_row[bm_colnames_alias['Last_name']]

        # Building the dataframe 'empl_pub_match_df' with rows of dataframe empl_df
        # where item at EMPLOYEES_USEFUL_COLS['name'] matches author lastname 'pub_lastname'
        empl_pub_match_df = empl_df[empl_df[emp_useful_cols_alias['name']]==pub_lastname].copy()

        # Test of lastname full match
        if pub_lastname==test_name and test_states[0]:
            _test_full_match(empl_pub_match_df, pub_lastname, emp_useful_cols_alias)

        if len(empl_pub_match_df)==0: # No match found
            flag_lastname_match = False
            # Checking for a similarity
            lastname_match_list = _orphan_reduction(pub_lastname, eff_lastnames)

            if lastname_match_list:
                # Concatenating in the dataframe 'empl_pub_match_df',
                # the rows of the dataframe 'empl_df'
                # corresponding to each of the found similarities by orphan reduction
                frames = []
                for lastname_match in lastname_match_list:
                    temp_df = empl_df[empl_df[emp_useful_cols_alias['name']]\
                                      ==lastname_match].copy()
                    # Replacing the employee last name by the publication last name
                    # for 'pub_emp_join_df' building
                    temp_df[emp_add_cols_alias['employee_full_name']]=\
                        pub_lastname + ' ' + temp_df[bm_colnames_alias['First_name']]
                    frames.append(temp_df)

                empl_pub_match_df = pd.concat(frames, ignore_index=True)
                flag_lastname_match = True

                # Test of lastnames similarity found by '_orphan_reduction' function
                if pub_lastname==test_name and test_states[1]:
                    _test_similarity(empl_pub_match_df, pub_lastname, emp_useful_cols_alias,
                                     lastname_match_list, flag_lastname_match)

            else:
                # Appending to dataframe orphan_df the row 'pub_df_row'
                # as effective orphan after orphan reduction
                orphan_df = pd.concat([orphan_df, pub_df_row.to_frame().T])
                flag_lastname_match = False

                # Test of lastnames no-similarity by '_orphan_reduction' function
                if pub_lastname==test_name and test_states[2]:
                    _test_no_similarity(pub_df_row, pub_lastname, bp_colnames_alias,
                                        bm_colnames_alias, lastname_match_list,
                                        flag_lastname_match)

        # Checking match for a given lastname between the publication first-name
        # and the employee first-name
        if flag_lastname_match:

            # Finding the author name initials for the current publication
            pub_firstname = pub_df_row[bm_colnames_alias['First_name']]

            # List of firstnames initials of a given name in the employees data
            eff_firstnames = empl_pub_match_df[bm_colnames_alias['First_name']].to_list()
            eff_lastnames_spec = empl_pub_match_df[emp_useful_cols_alias['name']].to_list()

            # Building the list of index of firs names initials
            list_idx = []
            for idx,eff_firstname in enumerate(eff_firstnames):

                if pub_firstname==eff_firstname:
                    list_idx.append(idx)

                elif pub_firstname==eff_firstname:
                    # Replacing the employee first name initials
                    # by the publication first name initials
                    # for 'pub_emp_join_df' building
                    empl_pub_match_df[emp_add_cols_alias['employee_full_name']].iloc[idx]=\
                        pub_lastname + ' ' + pub_firstname
                    list_idx.append(idx)

            # Test of match of firstname initials for lastname match or similarity
            if pub_lastname==test_name and test_states[3]:
                _test_match_of_firstname_initials(pub_df_row, pub_lastname, pub_firstname,
                                                  eff_firstnames, bp_colnames_alias,
                                                  list_idx, eff_lastnames_spec)

            if list_idx:
                # Building a dataframe 'temp_df' with the row 'pub_df_row'
                # related to a given publication
                # and adding the item value HOMONYM_FLAG
                # at column COL_NAMES_BM['Homonym']
                # when several matches on firstname initials are found
                temp_df = pub_df_row.to_frame().T
                temp_df[bm_colnames_alias['Homonym']]=\
                    pg.HOMONYM_FLAG if len(list_idx) > 1 else '_'

                # Saving specific dataframes 'temp_df' and 'empl_pub_match_df' for function testing
                if pub_lastname==test_name and test_states[4]:
                    # Creating path for saving test files
                    if not os.path.isdir(checks_path):
                        os.makedirs(checks_path)
                    _save_spec_dfs(temp_df)

                # Merging the dataframe 'empl_pub_match_df' to the dataframe 'temp_df'
                # by matching column '[COL_NAMES_BM['Last_name']]' of the dataframe 'temp_df'
                # to the column 'EMPLOYEES_ADD_COLS['employee_full_name']'
                # of the dataframe 'empl_pub_match_df'
                pub_emp_join_df = pd.merge(temp_df,
                                           empl_pub_match_df,
                                           how='left',
                                           left_on=[bm_colnames_alias['Full_name']],
                                           right_on=[emp_add_cols_alias['employee_full_name']])

                # Appending to the dataframe 'submit_df' the dataframe 'pub_emp_join_df'
                # which is specific to a given publication
                submit_df = pd.concat([submit_df, pub_emp_join_df], ignore_index=True)
            else:
                # Appending to the dataframe orphan_df the row 'pub_df_row' as effective orphan
                # after complementary checking of match via first name initials
                orphan_df = pd.concat([orphan_df, pub_df_row.to_frame().T], ignore_index=True)

    # Dropping duplicate rows if both dataframes (mandatory)
    submit_df = submit_df.drop_duplicates()
    orphan_df = orphan_df.drop_duplicates()

    return submit_df, orphan_df


def _add_author_job_type(in_path, out_path):
    """Adds a new column containing the job type for each author 
    of the publications list with one row per author.

    The job type is got from the employee information available 
    in 3 columns which names are given by 'category_col_alias', 
    'status_col_alias' and 'qualification_col_alias'. 
    The name of the new column is given by 'author_type_col_alias'. 
    The updated publications list is saved as Excel file.

    Args:
        in_path (path):  Full path to the Excel file of the publications list \
        with one row per author with attributes as Institute employee.
        out_path (path): Full path for saving the modified publications list.
    Returns:
        (str): End message recalling the full path to the saved file of \
        the modified publications list.
    """

    # internal functions:
    def _get_author_type(row):
        author_type = '-'
        for col_name, dic in author_types_dic.items():
            for key,values_list in dic.items():
                values_status = [True for value in values_list if value in row[col_name]]
                if any(values_status):
                    author_type = key
        return author_type

    # Setting useful aliases
    category_col_alias = eg.EMPLOYEES_USEFUL_COLS['category']
    status_col_alias = eg.EMPLOYEES_USEFUL_COLS['status']
    qualification_col_alias = eg.EMPLOYEES_USEFUL_COLS['qualification']
    author_type_col_alias = pg.COL_NAMES_BONUS['author_type']

    author_types_dic = {category_col_alias      : eg.CATEGORIES_DIC,
                        status_col_alias        : eg.STATUS_DIC,
                        qualification_col_alias : eg.QUALIFICATION_DIC}

    # Read of the excel file with dates conversion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(in_path, converters=eg.EMPLOYEES_CONVERTERS_DIC)

    submit_df[author_type_col_alias] = submit_df.apply(_get_author_type, axis=1)

    submit_df.to_excel(out_path, index=False)

    end_message = f"Column with author job type added in file: \n  '{out_path}'"
    return end_message


def _set_full_ref(title, first_author, journal_name, pub_year, doi):
    """Builds the full reference of a publication.

    Args:
        title (str): Title of the publication.
        first_author (str): First author of the publication formated as 'NAME IJ' \
        with 'NAME' the lastname and 'IJ' the initials of the firstname of the author.
        journal_name (str): Name of the journal where the publication is published.
        pub_year (str): Publication year defined by 4 digits.
        doi (str): Digital identification of the publication.
    Returns:
        (str): Full reference of the publication.
    """
    full_ref  = f'{title}, '                     # add the reference's title
    full_ref += f'{first_author}. et al., '      # add the reference's first author
    full_ref += f'{journal_name.capitalize()}, ' # add the reference's journal name
    full_ref += f'{pub_year}, '                  # add the reference's publication year
    full_ref += f'{doi}'                         # add the reference's DOI
    return full_ref


def _add_biblio_list(in_path, out_path):
    """Adds a new column containing the full reference of each publication 
    of the publications list with one row per author.

    The full reference is built by concatenating the folowing items: 
    title, first author, year, journal, DOI. 
    These items are got from the columns which names are given by 
    'pub_title_alias', 'pub_first_author_alias', 'pub_year_alias', 
    'pub_journal_alias' and 'pub_doi_alias', respectively. 
    The name of the new column is given by 'pub_full_ref_alias'. 
    The updated publications list is saved as Excel file.

    Args:
        in_path (path): Full path to the Excel file of the publications list.
        out_path (path): Full path for saving the modified publications list.
    Returns:
        (str): End message recalling the full path to the saved file \
        of the modified publications list.
    """

    # Setting useful aliases
    pub_id_alias = bp.COL_NAMES['pub_id']
    pub_first_author_alias = bp.COL_NAMES['articles'][1]
    pub_year_alias = bp.COL_NAMES['articles'][2]
    pub_journal_alias = bp.COL_NAMES['articles'][3]
    pub_doi_alias = bp.COL_NAMES['articles'][6]
    pub_title_alias = bp.COL_NAMES['articles'][9]
    pub_full_ref_alias = pg.COL_NAMES_BONUS['liste biblio']

    # Read of the excel file with dates convertion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(in_path, converters=eg.EMPLOYEES_CONVERTERS_DIC)

    articles_plus_full_ref_df = pd.DataFrame()
    # Splitting the frame into subframes with same Pub_id
    for _, pub_id_df in submit_df.groupby(pub_id_alias):
        # Select the first row and build the full reference
        pub_id_first_row = pub_id_df.iloc[0]
        title = str(pub_id_first_row[pub_title_alias])
        first_author = str(pub_id_first_row[pub_first_author_alias])
        journal_name = str(pub_id_first_row[pub_journal_alias])
        pub_year = str(pub_id_first_row[pub_year_alias])
        doi = str(pub_id_first_row[pub_doi_alias])
        pub_id_df[pub_full_ref_alias] = _set_full_ref(title, first_author,
                                                      journal_name, pub_year, doi)
        articles_plus_full_ref_df = pd.concat([articles_plus_full_ref_df, pub_id_df])

    articles_plus_full_ref_df.to_excel(out_path, index=False)

    end_message = f"Column with full reference of publication added in file: \n  '{out_path}'"
    return end_message


def _add_ext_docs(submit_path, orphan_path, ext_docs_path):
    """Adds to the publications-list dataframe with one row per author 
    new rows containing the information of specific authors.

    The specific authors are PhD students at the Institute but not as employees of it. 
    The list of these PhD students with the required information is got from 
    the excel file which full path is given by 'ext_docs_path' in sheet which 
    name is given by 'ext_docs_sheet_name_alias'. 
    The row of the added PhD students is dropped in the publications list 
    with one row per author that has not been identified as Institute employee. 
    The new publications lists are saved as Excel files.

    Args:
        submit_path (path): Full path to the Excel file of the publications list \
        with one row per author with attributes as Institute employee.
        orphan_path (path): Full path to the Excel file of the publications list \
        with one row per author that has not been identified as Institute employee.
        ext_docs_path (path): Full path to the Excel file giving the PhD students \
        at the Institute but not employees of it.
    Returns:
        (tup): (updated dataframe of the publications list with one row \
        per Institute author including external PhD students, updated dataframe \
        of publications list with one row per author that has not been identified \
        as Institute employee).
    """

    # Setting aliases for useful column names
    pub_id_alias = bp.COL_NAMES['authors'][0]
    author_id_alias = bp.COL_NAMES['authors'][1]
    converters_alias = eg.EMPLOYEES_CONVERTERS_DIC
    firstname_initials_col_base_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    ext_docs_full_name_alias = eg.EMPLOYEES_ADD_COLS['employee_full_name']
    ext_docs_useful_col_list_alias = eg.EXT_DOCS_USEFUL_COL_LIST
    ext_docs_pub_last_name_alias = pg.COL_NAMES_PUB_NAMES['last name']
    ext_docs_pub_initials_alias = pg.COL_NAMES_PUB_NAMES['initials']
    ext_docs_sheet_name_alias = pg.SHEET_NAMES_ORPHAN["docs to add"]
    ext_docs_col_adds_list_alias = pg.EXT_DOCS_COL_ADDS_LIST
    orphan_full_name_alias = pg.COL_NAMES_BM['Full_name']
    orphan_last_name_alias = pg.COL_NAMES_BM['Last_name']

    # Reading of the existing submit excel file of the corpus year
    # with dates conversion through converters_alias
    init_submit_df = pd.read_excel(submit_path, converters=converters_alias)
    init_orphan_df = pd.read_excel(orphan_path, converters=converters_alias)

    # Initializing new_submit_df with same column names as init_submit_df
    new_submit_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Initializing the dataframe to be concatenated to init_submit_df in new_submit_df
    # with same column names as init_submit_df
    new_submit_adds_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Aligning column names between init_submit_df and init_orphan_df
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {firstname_initials_col_base_alias : firstname_initials_col_base_alias + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_initials_alias = col_rename_dic[firstname_initials_col_base_alias]

    # Initializing new_orphan_df as copy of init_orphan_df
    #new_orphan_df = init_orphan_df.copy()
    new_orphan_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external phd students excel file
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    ext_docs_usecols = sum([[ext_docs_pub_last_name_alias, ext_docs_pub_initials_alias],
                            ext_docs_col_adds_list_alias,
                            ext_docs_useful_col_list_alias,],
                           [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    ext_docs_df = pd.read_excel(ext_docs_path,
                                sheet_name=ext_docs_sheet_name_alias,
                                usecols=ext_docs_usecols,
                                converters=converters_alias)
    ext_docs_df = ext_docs_df.dropna(how='any')

    # Searching for last names of init_orphan_df in ext_docs_df
    # to update submit and orphan files using new_submit_adds_df and new_orphan_drop_df
    for orphan_row_num, _ in init_orphan_df.iterrows():
        author_last_name = init_orphan_df.loc[orphan_row_num, orphan_last_name_alias]
        author_last_name = standardize_txt(author_last_name)
        author_initials = init_orphan_df.loc[orphan_row_num, orphan_initials_alias]
        for ext_docs_row_num, _ in ext_docs_df.iterrows():
            ext_docs_pub_last_name = ext_docs_df.loc[ext_docs_row_num, ext_docs_pub_last_name_alias]
            ext_docs_pub_last_name = standardize_txt(ext_docs_pub_last_name)
            ext_docs_pub_initials = ext_docs_df.loc[ext_docs_row_num, ext_docs_pub_initials_alias]
            if (ext_docs_pub_last_name==author_last_name
                    and ext_docs_pub_initials==author_initials):
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = init_orphan_df.loc[orphan_row_num].to_frame().T

                # Setting the row to copy from ext_docs_df as a dataframe
                row_to_copy_df = ext_docs_df.loc[ext_docs_row_num].to_frame().T

                # Dropping the columns of row_to_copy_df that should not be present in row_to_add_df
                row_to_copy_df = row_to_copy_df.drop([ext_docs_pub_last_name_alias, ext_docs_pub_initials_alias],
                                                     axis = 1)

                # Merging the two dataframes on respective full name column
                row_to_add_df = pd.merge(row_to_move_df,
                                         row_to_copy_df,
                                         left_on=[orphan_full_name_alias],
                                         right_on=[ext_docs_full_name_alias],
                                         how='left')

                # Appending the merged df to new_submit_adds_df
                new_submit_adds_df = pd.concat([new_submit_adds_df, row_to_add_df],
                                               ignore_index=True)

                # Appending row_to_move_df to  orphan_drop_df
                orphan_drop_df = pd.concat([orphan_drop_df, row_to_move_df],
                                           ignore_index=True)

    # Concatenating init_submit_df and new_submit_adds_df
    new_submit_df = pd.concat([init_submit_df, new_submit_adds_df])
    new_submit_df = new_submit_df.sort_values([pub_id_alias, author_id_alias])

    # Droping orphan_drop_df rows from init_orphan_df
    new_orphan_df = pd.concat([init_orphan_df, orphan_drop_df]).drop_duplicates(keep=False)

    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {firstname_initials_col_base_alias + "_x": \
                                 firstname_initials_col_base_alias}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    # Saving new_submit_df and new_orphan_df replacing init_submit_df and init_submit_df
    new_submit_df.to_excel(submit_path, index=False)
    new_orphan_df.to_excel(orphan_path, index=False)

    print("External PhD students added")
    return (new_submit_df, new_orphan_df)


def _add_other_ext(submit_path, orphan_path, others_path):
    """Adds to the publications-list dataframe with one row per author 
    new rows containing the information of specific authors.

    The specific authors are under external hiring contract at the Institute. 
    The list of these employees with the required information is got from 
    the excel file which full path is given by 'others_path' in sheet which 
    name is given by 'others_sheet_name_alias'. 
    The row of the added employees is dropped in the publications list 
    with one row per author that has not been identified as Institute employee. 
    The new publications lists are saved as Excel files.

    Args:
        submit_path (path): Full path to the Excel file of the publications list \
        with one row per author with attributes as Institute employee.
        orphan_path (path): Full path to the Excel file of the publications list \
        with one row per author that has not been identified as Institute employee.
        ext_docs_path (path): Full path to the Excel file giving the employees \
        under external hiring contract at the Institute.
    Returns:
        (tup): (updated dataframe of the publications list with one row \
        per Institute author including employees under external hiring contract \
        at the Institute, updated dataframe of publications list with one row \
        per author that has not been identified as Institute employee).
    """

    # Setting aliases for useful column names
    pub_id_alias = bp.COL_NAMES['authors'][0]
    author_id_alias = bp.COL_NAMES['authors'][1]
    converters_alias = eg.EMPLOYEES_CONVERTERS_DIC
    firstname_initials_col_base_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    others_full_name_alias = eg.EMPLOYEES_ADD_COLS['employee_full_name']
    ext_docs_useful_col_list_alias = eg.EXT_DOCS_USEFUL_COL_LIST
    others_pub_last_name_alias = pg.COL_NAMES_PUB_NAMES['last name']
    others_pub_initials_alias = pg.COL_NAMES_PUB_NAMES['initials']
    others_sheet_name_alias = pg.SHEET_NAMES_ORPHAN["others to add"]
    ext_docs_col_adds_list_alias = pg.EXT_DOCS_COL_ADDS_LIST
    orphan_full_name_alias = pg.COL_NAMES_BM['Full_name']
    orphan_last_name_alias = pg.COL_NAMES_BM['Last_name']

    # Reading of the existing submit excel file of the corpus year
    # with dates conversion through converters_alias
    init_submit_df = pd.read_excel(submit_path, converters=converters_alias)
    init_orphan_df = pd.read_excel(orphan_path, converters=converters_alias)

    # Initializing new_submit_df with same column names as init_submit_df
    new_submit_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Initializing the dataframe to be concatenated to init_submit_df in new_submit_df
    # with same column names as init_submit_df
    new_submit_adds_df = pd.DataFrame(columns=list(init_submit_df.columns))

    # Aligning column names between init_submit_df and init_orphan_df
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {firstname_initials_col_base_alias : firstname_initials_col_base_alias + "_x"}
    init_orphan_df = init_orphan_df.rename(columns=col_rename_dic)
    orphan_initials_alias = col_rename_dic[firstname_initials_col_base_alias]

    # Initializing new_orphan_df as copy of init_orphan_df
    #new_orphan_df = init_orphan_df.copy()
    new_orphan_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Initializing the dataframe to be droped from init_orphan_df
    # with same column names as init_orphan_df
    orphan_drop_df = pd.DataFrame(columns=list(init_orphan_df.columns))

    # Reading of the external phd students excel file
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    others_usecols = sum([[others_pub_last_name_alias, others_pub_initials_alias],
                          ext_docs_col_adds_list_alias,
                          ext_docs_useful_col_list_alias,],
                         [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    others_df = pd.read_excel(others_path,
                              sheet_name=others_sheet_name_alias,
                              usecols=others_usecols,
                              converters=converters_alias)
    others_df = others_df.dropna(how='any')

    # Searching for last names of init_orphan_df in others_df
    # to update submit and orphan files using new_submit_adds_df and new_orphan_drop_df
    for orphan_row_num, _ in init_orphan_df.iterrows():
        author_last_name = init_orphan_df.loc[orphan_row_num, orphan_last_name_alias]
        author_last_name = standardize_txt(author_last_name)
        author_initials = init_orphan_df.loc[orphan_row_num, orphan_initials_alias]
        for others_row_num, _ in others_df.iterrows():
            others_pub_last_name = others_df.loc[others_row_num, others_pub_last_name_alias]
            others_pub_last_name = standardize_txt(others_pub_last_name)
            others_pub_initials = others_df.loc[others_row_num, others_pub_initials_alias]
            if others_pub_last_name==author_last_name and others_pub_initials==author_initials:
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = init_orphan_df.loc[orphan_row_num].to_frame().T

                # Setting the row to copy from others_df as a dataframe
                row_to_copy_df = others_df.loc[others_row_num].to_frame().T

                # Droping the columns of row_to_copy_df that should not be present in row_to_add_df
                row_to_copy_df = row_to_copy_df.drop([others_pub_last_name_alias, others_pub_initials_alias],
                                                     axis=1)

                # Merging the two dataframes on respective full name column
                row_to_add_df = pd.merge(row_to_move_df,
                                         row_to_copy_df,
                                         left_on=[orphan_full_name_alias],
                                         right_on=[others_full_name_alias],
                                         how='left')

                # Appending the merged df to new_submit_adds_df
                new_submit_adds_df = pd.concat([new_submit_adds_df, row_to_add_df],
                                               ignore_index=True)

                # Appending row_to_move_df to  orphan_drop_df
                orphan_drop_df = pd.concat([orphan_drop_df, row_to_move_df],
                                           ignore_index=True)

    # Concatenating init_submit_df and new_submit_adds_df
    new_submit_df = pd.concat([init_submit_df, new_submit_adds_df])
    new_submit_df = new_submit_df.sort_values([pub_id_alias, author_id_alias])

    # Dropping orphan_drop_df rows from init_orphan_df
    new_orphan_df = pd.concat([init_orphan_df, orphan_drop_df]).drop_duplicates(keep=False)

    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {firstname_initials_col_base_alias + "_x": \
                                 firstname_initials_col_base_alias}
    new_orphan_df = new_orphan_df.rename(columns=col_invert_rename_dic)

    # Saving new_submit_df and new_orphan_df replacing init_submit_df and init_submit_df
    new_submit_df.to_excel(submit_path, index=False)
    new_orphan_df.to_excel(orphan_path, index=False)

    print("Other external collaborators added")
    return (new_submit_df, new_orphan_df)


def _change_col_names(institute, org_tup, submit_path, orphan_path):
    """Sets new column names to the files pointed by 'submit_path' 
    and 'orphan_path' paths.

    For that it uses the `build_col_conversion_dic` function 
    imported from `bmfuncts.rename_cols` module.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        submit_path (path): Full path to the Excel file of the publications list \
        with one row per author with attributes as Institute employee.
        orphan_path (path): Full path to the Excel file of the publications list \
        with one row per author that has not been identified as Institute employee.
    Returns:
        (str): End message recalling the full paths to the modified files.        
    """

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    orphan_col_rename_dic = col_rename_tup[0]
    submit_col_rename_dic = col_rename_tup[1]

    # Read of the 'submit' file with dates convertion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(submit_path, converters=eg.EMPLOYEES_CONVERTERS_DIC,
                              keep_default_na=False)
    submit_df = submit_df.rename(columns=submit_col_rename_dic)

    # Resaving submit_df
    submit_df.to_excel(submit_path, index=False)

    # Read of the 'orphan' file
    orphan_df = pd.read_excel(orphan_path, keep_default_na=False)
    orphan_df = orphan_df.rename(columns=orphan_col_rename_dic)

    # Resaving orphan_df
    orphan_df.to_excel(orphan_path, index=False)

    end_message = f"Column renamed in files: \n  '{submit_path}' \n  '{orphan_path}' "
    return end_message


def _split_orphan(org_tup, working_folder_path, orphan_file_name, verbose=False):
    """Splits the publications list with one row per author that has not been identified 
    as Institute employees.

    The split is in separate lists of publications depending on values in columns 
    given by 'inst_col_list' list that is specific to the Institute. 
    These lists are then saved as Excel files in the folder which full path 
    is given by 'orphan_path'.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        working_folder_path (path): Full path to working folder.
        orphan_file_name (str): File name of the Excel file of the publications list \
        with one row per author that has not been identified as Institute employee.
        verbose (bool): Status of prints (default = False).       
    """

    # Internal function
    def _save_inst_col_df(inst_col, df_to_save):
        if inst_col=="all_undrop":
            file_path = orphan_path
        else:
            file_name = inst_col + "_" + orphan_file_name
            file_path = working_folder_path / Path(file_name)
        df_to_save.to_excel(file_path, index=False)
        message = f"Excel file of orphan authors created for Institute subdivision: {inst_col}"
        if verbose:
            print(message)

    # Setting useful aliases
    converters_alias = eg.EMPLOYEES_CONVERTERS_DIC

    # Setting useful column names list and droping status
    inst_col_list = org_tup[4]
    orphan_drop_dict = org_tup[10]

    # Reading of the existing orphan excel file
    # with dates conversion through converters_alias
    orphan_path = working_folder_path / Path(orphan_file_name)
    orphan_df = pd.read_excel(orphan_path, converters=converters_alias, keep_default_na=False)

    # Creating, and saving as Excel file, orphan authors for each Institute subdivision
    institute_df = orphan_df.copy()
    new_orphan_df = orphan_df.copy()
    droped_indexes = set()
    for inst_col in inst_col_list[1:]:
        inst_col_df = orphan_df[orphan_df[inst_col]==1]
        _save_inst_col_df(inst_col, inst_col_df)
        indexes_to_drop = list(set(inst_col_df.index) - droped_indexes)
        institute_df = institute_df.drop(indexes_to_drop)
        droped_indexes = set(inst_col_df.index)
        if orphan_drop_dict[inst_col]:
            new_orphan_df = new_orphan_df.drop(inst_col_df.index)
    _save_inst_col_df(inst_col_list[0], institute_df)
    _save_inst_col_df("all_undrop", new_orphan_df)


def _my_hash(text:str):
    """Builts hash given the string 'text' 
    with a fixed prime numbers to mix up the bits."""

    my_hash = 0
    facts = (257,961) # prime numbers to mix up the bits
    minus_one = 0xFFFFFFFF # "-1" hex code
    for ch in text:
        my_hash = (my_hash*facts[0] ^ ord(ch)*facts[1]) & minus_one
    return my_hash


def _creating_hash_id(institute, org_tup, working_folder_path, submit_file_name, orphan_file_name):
    """Creates a dataframe which columns are given by 'hash_id_col_alias' and 'pub_id_alias'.

    The containt of these columns is as follows:

    - The 'hash_id_col_alias' column contains the unique hash ID built for each publication \
    through the `_my_hash` internal function on the basis of the values of 'year_alias', \
    'first_auth_alias', 'title_alias', 'issn_alias' and 'doi_alias' columns.
    - The 'pub_id_alias' column contains the publication order number in the publications list.

    The dataframe is saved as Excel file which full path is given by 'hash_id_file_path'.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        working_folder_path (path): Full path to working folder.
        submit_file_name (str): File name of the Excel file of the publications list \
        with one row per Institute author with one row per author \
        that has been identified as Institute employee.
        orphan_file_name (str): File name of the Excel file of the publications list \
        with one row per author that has not been identified as Institute employee.
    Returns:
        (str): End message recalling path to the saved file.        
    """

    # Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    submit_col_rename_dic = col_rename_tup[1]

    # Setting useful aliases
    hash_id_file_alias = pg.ARCHI_YEAR["hash_id file name"]
    hash_id_col_alias = pg.COL_HASH['hash_id']
    pub_id_alias = submit_col_rename_dic[bp.COL_NAMES["pub_id"]]
    year_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][2]]
    first_auth_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][1]]
    doi_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][6]]
    title_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][9]]
    issn_alias = submit_col_rename_dic[bp.COL_NAMES['articles'][10]]

    # Setting useful paths
    submit_file_path = working_folder_path / Path(submit_file_name)
    orphan_file_path = working_folder_path / Path(orphan_file_name)
    hash_id_file_path = working_folder_path / Path(hash_id_file_alias)

    # Setting useful columns list
    useful_cols = [pub_id_alias, year_alias, first_auth_alias,
                   title_alias, issn_alias, doi_alias]

    # Getting dataframes to hash
    submit_to_hash = pd.read_excel(submit_file_path, usecols=useful_cols)
    orphan_to_hash = pd.read_excel(orphan_file_path, usecols=useful_cols)

    # Concatenate de dataframes to hash
    dg_to_hash = pd.concat([submit_to_hash, orphan_to_hash])

    # Dropping rows of same pub_id_alias and reindexing the rows using ignore_index
    dg_to_hash = dg_to_hash.drop_duplicates(subset=[pub_id_alias], ignore_index=True)

    hash_id_df = pd.DataFrame()
    for idx in range(len(dg_to_hash)):
        pub_id = dg_to_hash.loc[idx, pub_id_alias]
        text   = (f"{str(dg_to_hash.loc[idx, year_alias])}"
                  f"{str(dg_to_hash.loc[idx, first_auth_alias])}"
                  f"{str(dg_to_hash.loc[idx, title_alias])}"
                  f"{str(dg_to_hash.loc[idx, issn_alias])}"
                  f"{str(dg_to_hash.loc[idx, doi_alias])}")
        hash_id = _my_hash(text)
        hash_id_df.loc[idx, hash_id_col_alias] = str(hash_id)
        hash_id_df.loc[idx, pub_id_alias] = pub_id

    hash_id_df.to_excel(hash_id_file_path, index=False)

    message = f"Hash IDs of publications created and saved in file: \n  {hash_id_file_path}"
    return message


def recursive_year_search(out_path, empl_df, institute, org_tup,
                          bibliometer_path, corpus_year, search_depth,
                          progress_callback=None, progress_bar_state=None):
    """Searches in the employees database of the Institute the information for the authors 
    of the publications of a corpus.

    This is done through the following steps:

    1. The publications list dataframe with one row per Institute author for each \
    publication is built from the results of the corpus parsing through \
    the `_build_institute_pubs_authors` internal function.
    2. The 'submit_df' dataframe of the publications list containing all matches \
    between Institute authors and employee names is initialized using the most recent year \
    of the employees database through the `_build_submit_df` internal function; \
    this is done together with the initialization of 'orphan_df' dataframe of the publications \
    list with authors not found in the employees database; these two dataframes contains \
    one row per author of each publication.
    3. New rows containing the information of authors that are PhD students \
    at the Institute but not as employees of it are added through the `_add_ext_docs` \
    internal function updating 'submit_df' and 'orphan_df' dataframes.
    4. New rows containing the information of authors that are under external hiring \
    contract at the Institute are added through the `_add_other_ext` internal function \
    updating 'submit_df' and 'orphan_df' dataframes.
    5. The 'submit_df' and 'orphan_df' dataframes are updated by search in the employees \
    database through the `_build_submit_df` internal function using recusively items from \
    'years' list for the search year; the dataframes are saved as Excel files which full \
    paths are given by 'submit_path' and 'orphan_path', respectively.
    6. A new column containing the job type for each author is added in the file which \
    full path is given by 'submit_path' through the `_add_author_job_type` internal function.
    7. A new column containing the full reference of each publication is added \
    in the file which full path is given by 'submit_path' through the `_add_biblio_list` \
    internal function.
    8. Column names are changed in the two files which full path are given by respectively, \
    'submit_path' and 'orphan_path' through the `_change_col_names` internal function.    
    9. An Excel file containing the unique hash ID built for each publication \
    is created through the `_creating_hash_id` internal function.

    Args:
        out_path (path): Full path to the folder for saving built dataframes. 
        empl_df (dataframe): Hierarchical employees database keyed by 'years' list.
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): Contains the corpus year defined by 4 digits.
        search_depth (int): Depth for search in 'empl_df' using 'years' list.
        progress_callback (function): Function for updating ProgressBar \
        tkinter widget status (default = None).
        progress_bar_state (int): Initial status of ProgressBar tkinter widget \
        (default = None).        
    Returns:
        (tup): (end_message (str), empty status (bool) of the publications \
        list with authors not found in the employees database)
    """

    # Internal functions
    def _set_unknown(df, cols, initials_cols):
        fill_na_cols = list(set(cols) - set(initials_cols))
        for col in fill_na_cols:
            df[col] = df[col].fillna(unknown_alias)
        for col in initials_cols:
            df[col] = df[col].fillna("NA")

    def _unique_pub_id(df):
        """Transforms the column 'Pub_id' of df y adding "yyyy_" 
        (year in 4 digits) to the values.

        Args:
            df (pandas.DataFrame): data that we want to modify.
        Returns:
            (pandas.DataFrame): df with its changed column.
        """
        year_df = df[year_col_alias].iloc[0]

        def _rename_pub_id(old_pub_id, year):
            pub_id_str = str(int(old_pub_id))
            while len(pub_id_str)<3:
                pub_id_str = "0" + pub_id_str
            new_pub_id = str(int(year)) + '_' + pub_id_str
            return new_pub_id

        df[pub_id_alias] = df[pub_id_alias].apply(lambda x: _rename_pub_id(x, year_df))
        return df

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN
    year_col_alias = bp.COL_NAMES['articles'][2]
    pub_id_alias = bp.COL_NAMES['pub_id']
    initials_col_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    submit_file_name_alias = pg.ARCHI_YEAR["submit file name"]
    orphan_file_name_alias = pg.ARCHI_YEAR["orphan file name"]
    orphan_treat_alias = pg.ARCHI_ORPHAN["root"]
    adds_file_name_alias = pg.ARCHI_ORPHAN["employees adds file"]

    # Setting local parameters
    orphan_split_status = org_tup[9]

    # Setting useful paths
    submit_path = out_path / Path(submit_file_name_alias)
    orphan_path = out_path / Path(orphan_file_name_alias)
    ext_docs_path = bibliometer_path / Path(orphan_treat_alias) / Path(adds_file_name_alias)
    others_path = bibliometer_path / Path(orphan_treat_alias) / Path(adds_file_name_alias)
    if progress_callback:
        step = (100 - progress_bar_state) / 100
        progress_callback(progress_bar_state + step * 2)

    # Building the articles dataframe
    pub_df = _build_institute_pubs_authors(institute, org_tup, bibliometer_path, corpus_year)
    if progress_callback:
        progress_callback(progress_bar_state + step * 5)

    # Building the search time depth of Institute co-authors among the employees dataframe
    eff_available_years = list(empl_df.keys())
    corpus_year_status = corpus_year in eff_available_years
    year_start = int(corpus_year)
    if not corpus_year_status:
        year_start = int(corpus_year)-1
    year_stop = year_start - (search_depth - 1)
    years = [str(i) for i in range(year_start, year_stop-1,-1)]
    if progress_callback:
        progress_callback(progress_bar_state + step * 10)

    # *******************************************************************
    # * Building recursively the `submit_df` and `orphan_df` dataframes *
    # *                 using `empl_df` files of years                   *
    # *******************************************************************

    # Initializing the dataframes to be built
    # a Data frame containing all matches between article Institute authors and employee names
    submit_df = pd.DataFrame()
    # a Data frame containing containing article Institute authors
    # not matching with any employee name
    orphan_df = pd.DataFrame()

    # Setting the test case selected within the following list
    # ['Full match',
    #  'Lower value similarity',
    #  'Upper value similarity',
    #  'No similarity',
    #  'No test']
    test_case = 'Upper value similarity'

    # Building the initial dataframes
    submit_df, orphan_df = _build_submit_df(empl_df[years[0]],
                                            pub_df, bibliometer_path,
                                            test_case=test_case)

    # Saving initial files of submit_df and orphan_df
    submit_df.to_excel(submit_path, index=False)
    orphan_df.to_excel(orphan_path, index=False)
    if progress_callback:
        progress_callback(progress_bar_state + step * 20)

    # Adding authors from list of external_phd students and saving new submit_df and orphan_df
    submit_df, orphan_df = _add_ext_docs(submit_path, orphan_path, ext_docs_path)
    if progress_callback:
        progress_callback(progress_bar_state + step * 25)

    # Adding authors from list of external employees under other hiring contract
    # and saving new submit_df and orphan_df
    submit_df, orphan_df = _add_other_ext(submit_path, orphan_path, others_path)
    if progress_callback:
        new_progress_bar_state = progress_bar_state + step * 30
        progress_callback(new_progress_bar_state)
        progress_bar_loop_progression = step * 50 // len(years)

    for _, year in enumerate(years):
        # Updating the dataframes submit_df_add and orphan_df
        submit_df_add, orphan_df = _build_submit_df(empl_df[year],
                                                    orphan_df,
                                                    bibliometer_path,
                                                    test_case)

        # Updating submit_df and orphan_df
        submit_df = pd.concat([submit_df, submit_df_add])

        # Updating progress bar state
        if progress_callback:
            new_progress_bar_state += progress_bar_loop_progression
            progress_callback(new_progress_bar_state)

    # *************************************************************************************
    # * Saving results in 'submit_file_name_alias' file and 'orphan_file_name_alias' file *
    # *************************************************************************************

    # Replace NaN values by UNKNOWN string except in first name initials
    submit_cols = list(submit_df.columns)
    submit_initials_cols = [x for x in list(submit_df.columns) if initials_col_alias in x]
    _set_unknown(submit_df, submit_cols, submit_initials_cols)
    orphan_cols = list(orphan_df.columns)
    orphan_initials_cols = [initials_col_alias]
    _set_unknown(orphan_df, orphan_cols, orphan_initials_cols)
    orphan_status = orphan_df.empty

    # Changing Pub_id columns to a unique Pub_id depending on the year
    submit_df = _unique_pub_id(submit_df)
    if not orphan_status:
        orphan_df = _unique_pub_id(orphan_df)

    # Saving orphan_df
    orphan_df.to_excel(orphan_path, index=False)

    # Saving submit_df
    submit_df.to_excel(submit_path, index=False)

    # Adding author job type and saving new submit_df
    _add_author_job_type(submit_path, submit_path)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 5)

    # Adding full article reference and saving new submit_df
    _add_biblio_list(submit_path, submit_path)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 10)

    # Renaming column names using submit_col_rename_dic and orphan_col_rename_dic
    _change_col_names(institute, org_tup, submit_path, orphan_path)

    # Splitting orphan file in subdivisions of Institute
    if orphan_split_status:
        _split_orphan(org_tup, out_path, orphan_file_name_alias)
    if progress_callback:
        progress_callback(new_progress_bar_state + step * 15)

    # Creating universal identification of articles independent of database extraction
    _creating_hash_id(institute, org_tup, out_path,
                      submit_file_name_alias, orphan_file_name_alias)
    if progress_callback:
        progress_callback(100)

    end_message = ("Results of search of authors in employees list "
                   f"saved in folder: \n  {out_path}")
    return end_message, orphan_status
