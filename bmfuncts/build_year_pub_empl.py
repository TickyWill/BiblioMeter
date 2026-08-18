"""Module of functions for the merge of employees information with the publications list 
of the Institute for a year corpus.

"""

__all__ = ['build_pub_empl_data']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import pandas as pd

# Local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.pub_globals as bm_pg
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import keep_initials
from bmfuncts.useful_functs import print_step_text


def _set_test_cols_dic():
    """Builds a dict setting selected columns names for the process 
    of testing match between employees data and publications data.

    Returns:
        (dict): The built dict.
    """
    test_cols_dic = {'pub_firstname_col' : bm_pg.COL_NAMES_BM['First_name'],
                     'pub_lastname_col'  : bm_pg.COL_NAMES_BM['Last_name'],
                     'pub_fullname_col'  : bm_pg.COL_NAMES['authors'][2],
                     'empl_mat_col'      : bm_eg.EMPLOYEES_USEFUL_COLS['matricule'],
                     'empl_lastname_col' : bm_eg.EMPLOYEES_USEFUL_COLS['name'],
                     'empl_firstname_col': bm_eg.EMPLOYEES_USEFUL_COLS['first_name'],
                     'empl_fullname_col' : bm_eg.EMPLOYEES_ADD_COLS['employee_full_name'],
                    }
    return test_cols_dic


def _test_full_match(empl_pub_match_df, pub_lastname, test_cols_dic):
    """Prints the info of the test for 'Full match' test case.

    Args:
        empl_pub_match_df (dataframe): The concatenated rows of the 'empl_df' dataframe 
        corresponding to each of the found similarities by orphan reduction.
        pub_lastname (str): The last name of the author for which similarity \
        has been found.
        test_cols_dic (dict): The selected columns names for the process \
        of testing match between employees data and publications data.
    """
    # Setting col names
    empl_mat_col = test_cols_dic['empl_mat_col']
    empl_lastname_col = test_cols_dic['empl_lastname_col']

    if not empl_pub_match_df.empty:
        print('\nMatch found for author lastname:', pub_lastname)
        print(' Nb of matches:', len(empl_pub_match_df))
        print(' Employee matricule:',
              empl_pub_match_df[empl_mat_col].to_list()[0])
        print(' Employee lastname:',
              empl_pub_match_df[empl_lastname_col].to_list()[0])
    else:
        print('\nNo match for author lastname:', pub_lastname)
        print('  Nb first matches:', len(empl_pub_match_df))


def _test_similarity(empl_pub_match_df, pub_lastname, lastname_match_list,
                     flag_lastname_match, test_cols_dic):
    """Prints the info of the test for 'Similarity' test case.

    Args:
        empl_pub_match_df (dataframe): The concatenated rows of the 'empl_df' dataframe 
        corresponding to each of the found similarities by orphan reduction.
        pub_lastname (str): The last name of the author for which similarity \
        has been found.
        lastname_match_list (list): The list of employees last-names (str) \
        that matches the author last_name.
        flag_lastname_match (bool): The status of last name match.
        test_cols_dic (dict): The selected columns names for the process \
        of testing match between employees data and publications data.
    """
    # Setting col names
    empl_mat_col = test_cols_dic['empl_mat_col']
    empl_lastname_col = test_cols_dic['empl_lastname_col']
    empl_firstname_col = test_cols_dic['empl_firstname_col']
    empl_fullname_col = test_cols_dic['empl_fullname_col']

    print('\nSimilarities by orphan reduction for author lastname:', pub_lastname)
    print('  Lastname flag match:', flag_lastname_match)
    print('  Nb similarities by orphan reduction:', len(lastname_match_list))
    print('  List of lastnames with similarities:', lastname_match_list)
    print('  Employee matricules:',
          empl_pub_match_df[empl_mat_col].to_list())
    print('  Employee lastnames:',
          empl_pub_match_df[empl_lastname_col].to_list())
    print('  Employee firstnames:',
          empl_pub_match_df[empl_firstname_col].to_list())
    print('  Employee fullnames:',
          empl_pub_match_df[empl_fullname_col].to_list())


def _test_no_similarity(pub_df_row, pub_lastname, lastname_match_list,
                        flag_lastname_match, test_cols_dic):
    """Prints the info of the test for 'No similarity' test case.

    Args:
        pub_df_row (pandas series): The data related to a given publication \
        when several matches on firstname initials are found.
        pub_lastname (str): The last name of the author for which no similarity \
        has been found.
        lastname_match_list (list): The list of employees last-names (str) \
        that matches the author last_name.
        flag_lastname_match (bool): The status of last name match.
        test_cols_dic (dict): The selected columns names for the process \
        of testing match between employees data and publications data.
    """
    # Setting col names
    pub_fullname_col = test_cols_dic['pub_fullname_col']
    pub_lastname_col = test_cols_dic['pub_lastname_col']
    pub_firstname_col = test_cols_dic['pub_firstname_col']

    print('\nNo similarity by orphan reduction for author lastname:', pub_lastname)
    print('  Lastname flag match:', flag_lastname_match)
    print('  Nb similarities by orphan reduction:', len(lastname_match_list))
    print('  Orphan full author name:', pub_df_row[pub_fullname_col])
    print('  Orphan author lastname:', pub_df_row[pub_lastname_col])
    print('  Orphan author firstname initials:',
          pub_df_row[pub_firstname_col])


def _test_match_of_firstname_initials(pub_df_row, pub_lastname, pub_firstname,
                                      empl_firstnames, list_idx, empl_lastnames_spec,
                                      test_cols_dic):
    """Prints the info of the test on first name initials for all test cases.

    Args:
        pub_df_row (pandas series): The data related to a given publication \
        when several matches on firstname initials are found.
        pub_lastname (str): The last name of the author for which matches of \
        firstname initials has been found.
        pub_firstname (str): The first name initials of the author matches of \
        firstname initials has been found.
        empl_firstnames (list): The list of first name initials of the employees \
        that matches the firstname initials of the author.
        list_idx (list): Indices (int) of matching initials.
        empl_lastnames_spec (list): The list of last names of the employees \
        that matches the firstname initials of the author.
        test_cols_dic (dict): The selected columns names for the process \
        of testing match between employees data and publications data.
    """
    # Setting col names
    pub_fullname_col = test_cols_dic['pub_fullname_col']

    print('\nInitials for author lastname:', pub_lastname)
    print('  Author fullname:', pub_df_row[pub_fullname_col])
    print('  Author firstname initials:', pub_firstname)
    print('\nInitials of matching employees for author lastname:', pub_lastname)
    print('  Employees firstname initials list:', empl_firstnames)
    print('\nChecking initials matching for author lastname:', pub_lastname)
    print('  Nb of matching initials:', len(list_idx))
    print('  Index list of matching initials:', list_idx)
    print('  Employees lastnames list:', empl_lastnames_spec)


def _set_match_test_info(wf_path, test_case, test_name):
    """Sets the info for the test of the matching results.

    Args:
        wf_path (path): Full path to working folder.
        test_case (str): The case for the test selected \
        among the keys of the test dict.
        test_name (str): The author's lastname for which tests are performed.
    Returns:
        (dict): keyed by ['cols', 'lastname', 'states', 'filespath'] and valued \
        by the useful colums names (dict), the author's lastname (str), \
        the value of the test dict at 'test_case' key (list), \
        The full path to the folder where test results will be saved.
    """
    # Setting col names for test results prints
    test_cols_dic = _set_test_cols_dic()

    # Setting test states info
    test_dict = {'Full match'            : [True, True, True, True, True],
                 'Lower value similarity': [False, True, True, True, True],
                 'Upper value similarity': [False, True, True, True, True],
                 'No similarity'         : [False, False, True, True, True],
                 'No test'               : [False, False, False, False, False]
                 }
    test_states = test_dict[test_case]

    # Setting path for saving results of test
    checks_path = Path(wf_path) / Path('Temp_checks')
    if test_states[4]:
        # Creating temporary output folder
        if not os.path.exists(checks_path):
            os.makedirs(checks_path)
    test_info_dic = {'cols'     : test_cols_dic,
                     'lastname' : test_name,
                     'states'   : test_states,
                     'filespath': checks_path,
                    }
    return test_info_dic


def _save_spec_dfs(temp_df, empl_pub_match_df, test_name, checks_path):
    """Saves specific data for the control of the matching results.

    Args:
        temp_df (dataframe): Data related to a given publication \
        when several matches on firstname initials are found.
        empl_pub_match_df (dataframe): The concatenated rows of the 'empl_df' dataframe 
        corresponding to each of the found similarities by orphan reduction.
        test_name (str): The author's last-name for the test.
        checks_path (path): The full path for saving the testing data.
    """
    name_suffix = test_name + '.xlsx'
    temp_df.to_excel(checks_path / Path('temp_df_' + name_suffix),
                     index=False)
    empl_pub_match_df.to_excel(checks_path / Path('empl_pub_match_df_' + name_suffix),
                              index=False)


def _reduce_orphan_df(orphan_lastname, empl_lastnames):
    """Finds the list of employees lastnames that matches \
    with the author's lastname.

    Args:
        orphan_lastname (str): The author lastname.
        empl_lastnames (list): The list of employees lastnames (str).
    Returns:
        (list): The list of employees lastnames (str) that matches \
        the author lastname.
    """
    orphan_lastname = ' ' + orphan_lastname + ' '
    lastname_match_list = []
    for empl_name in empl_lastnames:
        if (orphan_lastname in empl_name) or (empl_name in orphan_lastname):
            lastname_match_list.append(empl_name.strip())
    return lastname_match_list


def _set_merge_cols_dic():
    merge_cols_dic = {'pub_firstname_col': bm_pg.COL_NAMES_BM['First_name'],
                      'pub_lastname_col' : bm_pg.COL_NAMES_BM['Last_name'],
                      'pub_fullname_col' : bm_pg.COL_NAMES_BM['Full_name'],
                      'empl_lastname_col': bm_eg.EMPLOYEES_USEFUL_COLS['name'],
                      'empl_fullname_col': bm_eg.EMPLOYEES_ADD_COLS['employee_full_name'],
                      'homonyms_col'     : bm_pg.COL_NAMES_BM['Homonym'],
                     }
    return merge_cols_dic


def _check_last_name_similarity(pub_lastname, empl_lastnames, empl_df, orphan_df, pub_author_row,
                                empl_lastname_col, empl_fullname_col, pub_firstname_col,
                                test_info_dic):
    """Checks similarity of author's lastname and employees' lastnames when full-match not found."""

    test_keys = ['cols', 'lastname', 'states']
    test_cols_dic, test_name, test_states = [test_info_dic[key] for key in test_keys]

    # Checking for a similarity
    lastname_match_list = _reduce_orphan_df(pub_lastname, empl_lastnames)

    if lastname_match_list:
        # Concatenating in the dataframe 'empl_pub_match_df',
        # the rows of the dataframe 'empl_df'
        # corresponding to each of the found similarities by orphan reduction
        frames = []
        for lastname_match in lastname_match_list:
            temp_df = empl_df[empl_df[empl_lastname_col]==lastname_match].copy()
            # Replacing the employee last name by the publication last name
            # for 'empl_pub_match_df' building
            temp_df[empl_fullname_col]= pub_lastname + ' ' + temp_df[pub_firstname_col]
            frames.append(temp_df)

        empl_pub_match_df = concat_dfs(frames, concat_ignore_index=True)
        flag_lastname_match = True

        # Test of lastnames similarity found by '_reduce_orphan_df' function
        if pub_lastname==test_name and test_states[1]:
            _test_similarity(empl_pub_match_df, pub_lastname, lastname_match_list,
                             flag_lastname_match, test_cols_dic)
    else:
        empl_pub_match_df = pd.DataFrame()
        # Appending to dataframe orphan_df the row 'pub_author_row'
        # as actual orphan after orphan reduction
        orphan_df = concat_dfs([orphan_df, pub_author_row.to_frame().T])
        flag_lastname_match = False

        # Test of lastnames no-similarity by '_reduce_orphan_df' function
        if pub_lastname==test_name and test_states[2]:
            _test_no_similarity(pub_author_row, pub_lastname, lastname_match_list,
                                flag_lastname_match, test_cols_dic)
    return flag_lastname_match, empl_pub_match_df, orphan_df


def _check_lastname_match(empl_df, orphan_df, pub_author_row, empl_lastnames,
                          pub_lastname_col, pub_firstname_col, empl_lastname_col, empl_fullname_col,
                          test_info_dic):
    test_keys = ['cols', 'lastname', 'states']
    test_cols_dic, test_name, test_states = [test_info_dic[key] for key in test_keys]

    # Initializing the flag 'flag_lastname_match' as True by default
    flag_lastname_match = True

    # Getting the author's lastname
    pub_lastname = pub_author_row[pub_lastname_col]

    # Building the dataframe 'empl_pub_match_df' with rows of dataframe empl_df
    # where item at EMPLOYEES_USEFUL_COLS['name'] matches author lastname 'pub_lastname'
    empl_pub_match_df = empl_df[empl_df[empl_lastname_col]==pub_lastname].copy()

    # Test of lastname full match
    if pub_lastname==test_name and test_states[0]:
        _test_full_match(empl_pub_match_df, pub_lastname, test_cols_dic)

    if empl_pub_match_df.empty:
        # No match found

        # Checking for similarity between author's lastname and employees' lastnames
        return_tup = _check_last_name_similarity(pub_lastname, empl_lastnames, empl_df, orphan_df, pub_author_row,
                                                 empl_lastname_col, empl_fullname_col, pub_firstname_col,
                                                 test_info_dic)
        flag_lastname_match, empl_pub_match_df, orphan_df = return_tup
    return flag_lastname_match, empl_pub_match_df, orphan_df


def _check_firstname_initiales_match(empl_pub_match_df, pub_author_row,
                                     pub_lastname_col, pub_firstname_col, empl_lastname_col,
                                     test_info_dic):
    # Checking match between the author's firstname and the employees' firstnames
    # for the matching lastname either (by full match or similarity)

    test_keys = ['cols', 'lastname', 'states']
    test_cols_dic, test_name, test_states = [test_info_dic[key] for key in test_keys]

    # Getting the author's lastname and firstname initials
    pub_lastname = pub_author_row[pub_lastname_col]
    pub_firstname = pub_author_row[pub_firstname_col]

    # Building the list of firstnames initials of a given name in the employees data
    empl_firstnames = empl_pub_match_df[pub_firstname_col].to_list()
    empl_lastnames_spec = empl_pub_match_df[empl_lastname_col].to_list()

    # Building the list of index of firstnames initials that match
    initials_match_idx_list = []
    for idx, empl_firstname in enumerate(empl_firstnames):
        if pub_firstname==empl_firstname:
            initials_match_idx_list.append(idx)

    # Test of match of firstname initials for lastname match or similarity
    if pub_lastname==test_name and test_states[3]:
        _test_match_of_firstname_initials(pub_author_row, pub_lastname, pub_firstname,
                                          empl_firstnames, initials_match_idx_list, empl_lastnames_spec,
                                          test_cols_dic)
    return initials_match_idx_list


def _update_pub_empl_data(merge_df, pub_author_row, empl_pub_match_df, initials_match_idx_list,
                          pub_lastname_col, pub_fullname_col, empl_fullname_col, homonyms_col,
                          test_info_dic):

    test_keys = ['lastname', 'states', 'filespath']
    test_name, test_states, checks_path = [test_info_dic[key] for key in test_keys]

    # Building a 'pub_author_df' data with the 'pub_author_row' row
    # related to a given author's last name.
    # Then adding the item value HOMONYM_FLAG global at 'homonyms_col' column
    # when several matches on firstname initials are found.
    pub_author_df = pub_author_row.to_frame().T
    pub_author_df[homonyms_col]= bm_pg.HOMONYM_FLAG if len(initials_match_idx_list)>1 else '_'

    # Getting the author's lastname and firstname initials
    pub_lastname = pub_author_row[pub_lastname_col]

    # Saving specific dataframes 'pub_author_df' and 'empl_pub_match_df' for function testing
    if pub_lastname==test_name and test_states[4]:
        _save_spec_dfs(pub_author_df, empl_pub_match_df, test_name, checks_path)

    # Merging the 'empl_pub_match_df' data to the 'pub_author_df' data.
    # The pub_lastname_col column of the 'pub_author_df' data
    # is matched to the empl_fullname_col column of the 'empl_pub_match_df' data.
    pub_auth_emp_join_df = pd.merge(pub_author_df,
                                    empl_pub_match_df,
                                    how='left',
                                    left_on=[pub_fullname_col],
                                    right_on=[empl_fullname_col])

    # Appending to the dataframe 'merge_df' the dataframe 'pub_auth_emp_join_df'
    # which is specific to a given publication
    merge_df = concat_dfs([merge_df, pub_auth_emp_join_df], concat_ignore_index=True)
    return merge_df


def build_pub_empl_data(empl_df, pub_df, wf_path, print_params,
                        test_case="No test", test_name="No name", init_status=False):
    """Builds a dataframe of the merged employees information with the publications 
    list with one row per author.

    The merge is based on test of similarities between last names and first names 
    of employees and authors. 
    The 'test_case' arg allows to print and save the results of the similarity 
    test for a given author name defined by the 'test_name' arg. The test parameters 
    are set through the `_set_match_test_info` internal function. The values of the test 
    parameters are printed through the `_test_full_match`, `_test_similarity` and 
    `_test_no_similarity` internal functions. The results are saved through the 
    `_save_spec_dfs` internal function.
    Found homonyms are tagged by 'HOMONYM_FLAG' global imported from globals 
    module imported as bm_pg.

    Args:
        empl_df (dataframe): Employees database of a given year.
        pub_df (dataframe): Institute's publications-list with one row per author.
        wf_path (path): Full path to working folder.
        test_case (str): Optional test case for testing the function (default: "No test").
        test_name (str): Optional author's last-name for testing the function \
        (default: "No name").
        init_status (bool): Optional, status of initial search (default: False)
    Returns:
        (tup): (dataframe of merged employees information with \
        the publications list with one row per Institute's author with \
        identified homonyms, dataframe of publications list with \
        one row per author that has not been identified as Institute's employee).
    Note:
        Care is taken to keep 'NA' value for the first name initials \
        (that are set to NaN otherwise) through the `keep_initials` function \
        imported from `bmfuncts.useful_functs` module.
    """
    # Setting useful col names for building merged data
    merge_cols_dic = _set_merge_cols_dic()
    col_keys = merge_cols_dic.keys()
    (pub_firstname_col, pub_lastname_col, pub_fullname_col, empl_lastname_col,
     empl_fullname_col, homonyms_col) = [merge_cols_dic[key] for key in col_keys]

    # Initializing the Data that will contain all matches
    # between 'pub_df' author-name and 'empl_df' employee-name
    merge_df = pd.DataFrame()

    # Initializing the Data that will contain all 'pub_df' author-names
    # which do not match with any of the 'empl_df' employee-names
    orphan_df = pd.DataFrame(columns=list(pub_df.columns))

    # Building the set of lastnames (without duplicates) of the 'empl_df' data
    empl_lastnames = set(empl_df[empl_lastname_col].to_list())
    empl_lastnames = [' ' + x + ' ' for x in empl_lastnames]

    # Setting the useful info for testing the function
    test_info_dic = _set_match_test_info(wf_path, test_case, test_name)

    # Building 'merge_df' and 'orphan_df' data
    if init_status:
        print_step_text("      - Searching of authors among employees data...", print_params)
        full_names_nb, names_nb = len(pub_df), 0
    for _, pub_author_row in pub_df.iterrows():
        if init_status:
            names_nb += 1
            print(f"              Number of searched authors:   {names_nb} / {full_names_nb}", end="\r")
        # Building an 'empl_pub_match_df' data with rows of 'empl_df' data
        # The rows where the value in COL_NAMES_BM['Last_name'] column of the 'pub_df' data
        # matches with the value in EMPLOYEES_USEFUL_COLS['name'] column of the 'empl_df' data

        return_tup = _check_lastname_match(empl_df, orphan_df, pub_author_row, empl_lastnames,
                                           pub_lastname_col, pub_firstname_col, empl_lastname_col, empl_fullname_col,
                                           test_info_dic)
        flag_lastname_match, empl_pub_match_df, orphan_df = return_tup

        if flag_lastname_match:
            # Checking match between the author's firstname and the employees' firstnames
            # for the matching lastname either (by full match or similarity)
            initials_match_idx_list = _check_firstname_initiales_match(empl_pub_match_df, pub_author_row,
                                                                       pub_lastname_col, pub_firstname_col, empl_lastname_col,
                                                                       test_info_dic)

            if initials_match_idx_list:
                # Updating merged data of publications and employees
                merge_df = _update_pub_empl_data(merge_df, pub_author_row, empl_pub_match_df, initials_match_idx_list,
                                                 pub_lastname_col, pub_fullname_col, empl_fullname_col, homonyms_col,
                                                 test_info_dic)
            else:
                # Appending to the dataframe orphan_df the row 'pub_author_row' as actual orphan
                # after the complementary checking of match via firstname initials
                orphan_df = concat_dfs([orphan_df, pub_author_row.to_frame().T], concat_ignore_index=True)

    # Dropping duplicate rows in both dataframes (mandatory)
    merge_df = merge_df.drop_duplicates()
    orphan_df = orphan_df.drop_duplicates()

    if init_status:
        step_txt = ("      - Data of authors found as employees "
                    "and data of authors not found amond employees built")
        print_step_text(step_txt, print_params)
    return merge_df, orphan_df
