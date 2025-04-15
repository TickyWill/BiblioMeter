"""Module of functions for the merge of employees information with the publications list 
of the Institute for a year corpus.

"""

__all__ = ['build_submit_df']

# Standard Library imports
import os
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg
from bmfuncts.useful_functs import concat_dfs
from bmfuncts.useful_functs import keep_initials


def _test_full_match(empl_pub_match_df, pub_lastname):
    """Prints the info of the test for 'Full match' test case.

    Args:
        empl_pub_match_df (dataframe): The concatenated rows of the 'empl_df' dataframe 
        corresponding to each of the found similarities by orphan reduction.
        pub_lastname (str): The last name of the author for which similarity \
        has been found.
    """
    if len(empl_pub_match_df)!=0:
        print('\nMatch found for author lastname:', pub_lastname)
        print(' Nb of matches:', len(empl_pub_match_df))
        print(' Employee matricule:',
              empl_pub_match_df[eg.EMPLOYEES_USEFUL_COLS['matricule']].to_list()[0])
        print(' Employee lastname:',
              empl_pub_match_df[eg.EMPLOYEES_USEFUL_COLS['name']].to_list()[0])
    else:
        print('\nNo match for author lastname:', pub_lastname)
        print('  Nb first matches:', len(empl_pub_match_df))


def _test_similarity(empl_pub_match_df, pub_lastname,
                     lastname_match_list, flag_lastname_match):
    """Prints the info of the test for 'Similarity' test case.

    Args:
        empl_pub_match_df (dataframe): The concatenated rows of the 'empl_df' dataframe 
        corresponding to each of the found similarities by orphan reduction.
        pub_lastname (str): The last name of the author for which similarity \
        has been found.
        lastname_match_list (list): The list of employees last-names (str) \
        that matches the author last_name.
        flag_lastname_match (bool): The status of last name match.
    """
    print('\nSimilarities by orphan reduction for author lastname:', pub_lastname)
    print('  Lastname flag match:', flag_lastname_match)
    print('  Nb similarities by orphan reduction:', len(lastname_match_list))
    print('  List of lastnames with similarities:', lastname_match_list)
    print('  Employee matricules:',
          empl_pub_match_df[eg.EMPLOYEES_USEFUL_COLS['matricule']].to_list())
    print('  Employee lastnames:',
          empl_pub_match_df[eg.EMPLOYEES_USEFUL_COLS['name']].to_list())
    print('  Employee firstnames:',
          empl_pub_match_df[eg.EMPLOYEES_USEFUL_COLS['first_name']].to_list())
    print('  Employee fullnames:',
          empl_pub_match_df[eg.EMPLOYEES_ADD_COLS['employee_full_name']].to_list())


def _test_no_similarity(pub_df_row, pub_lastname, lastname_match_list,
                        flag_lastname_match):
    """Prints the info of the test for 'No similarity' test case.

    Args:
        pub_df_row (pandas series): The data related to a given publication \
        when several matches on firstname initials are found.
        pub_lastname (str): The last name of the author for which no similarity \
        has been found.
        lastname_match_list (list): The list of employees last-names (str) \
        that matches the author last_name.
        flag_lastname_match (bool): The status of last name match.
    """
    print('\nNo similarity by orphan reduction for author lastname:', pub_lastname)
    print('  Lastname flag match:', flag_lastname_match)
    print('  Nb similarities by orphan reduction:', len(lastname_match_list))
    print('  Orphan full author name:', pub_df_row[bp.COL_NAMES['authors'][2]])
    print('  Orphan author lastname:', pub_df_row[pg.COL_NAMES_BM['Last_name']])
    print('  Orphan author firstname initials:',
          pub_df_row[pg.COL_NAMES_BM['First_name']])


def _test_match_of_firstname_initials(pub_df_row, pub_lastname, pub_firstname,
                                      eff_firstnames, list_idx, eff_lastnames_spec):
    print('\nInitials for author lastname:', pub_lastname)
    print('  Author fullname:', pub_df_row[bp.COL_NAMES['authors'][2]])
    print('  Author firstname initials:', pub_firstname)
    print('\nInitials of matching employees for author lastname:', pub_lastname)
    print('  Employees firstname initials list:', eff_firstnames)
    print('\nChecking initials matching for author lastname:', pub_lastname)
    print('  Nb of matching initials:', len(list_idx))
    print('  Index list of matching initials:', list_idx)
    print('  Employees lastnames list:', eff_lastnames_spec)


def _set_match_test_info(bibliometer_path, test_case):
    """Sets the info for the test of the matching results.

    Args: 
        bibliometer_path (path): Full path to working folder.
        test_case (str): The case for the test selected \
        among the keys of the test dict.
    Returns:
        (tup): (The value of the test dict art 'test_case' key (list), \
        The full path to the folder where test results will be saved).
    """
    test_dict = {'Full match'            : [True, True, True, True, True],
                 'Lower value similarity': [False, True, True, True, True],
                 'Upper value similarity': [False, True, True, True, True],
                 'No similarity'         : [False, False, True, True, True],
                 'No test'               : [False, False, False, False, False]
                 }
    test_states = test_dict[test_case]
    checks_path = Path(bibliometer_path) / Path('Temp_checks')
    if test_states[4]:
        # Creating temporary output folder
        if not os.path.exists(checks_path):
            os.makedirs(checks_path)
    return test_states, checks_path


def _save_spec_dfs(temp_df, empl_pub_match_df, test_name, checks_path):
    """Saves specific data for the control of the matching results.

    Args:
        temp_df (dataframe): Data related to a given publication \
        when several matches on firstname initials are found.
        empl_pub_match_df (dataframe): The concatenated rows of the 'empl_df' dataframe 
        corresponding to each of the found similarities by orphan reduction.
        test_name (str): The author's last-name for the test.
        checks_path (path): The full path for saving the the testing data.
    """
    name_suffix = test_name + '.xlsx'
    temp_df.to_excel(checks_path / Path('temp_df_' + name_suffix),
                     index=False)
    empl_pub_match_df.to_excel(checks_path / Path('empl_pub_match_df_' + name_suffix),
                              index=False)


def _reduce_orphan_df(orphan_lastname, eff_lastname):
    """Finds the list of employees last-names that matches \
    with the author's last name.

    Args:
        orphan_lastname (str): The author last-name.
        eff_lastname (list): The list of employees last-names (str).
    Returns:
        (list): The list of employees last-names (str) that matches \
        the author last_name.
    """
    orphan_lastname = ' ' + orphan_lastname + ' '
    lastname_match_list = []
    for eff_name in eff_lastname:
        if (orphan_lastname in eff_name) or (eff_name in orphan_lastname):
            lastname_match_list.append(eff_name.strip())
    return lastname_match_list


def build_submit_df(empl_df, pub_df, bibliometer_path, test_case="No test", test_name="No name"):
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
    module imported as pg.

    Args:
        empl_df (dataframe): Employees database of a given year.
        pub_df (dataframe): Institute publications list with one row per author. 
        bibliometer_path (path): Full path to working folder.
        test_case (str): Optional test case for testing the function (default = "No test").
        test_name (str): Optional author's last-name for testing the function \
        (default = "No name").
    Returns:
        (tup): (dataframe of merged employees information with \
        the publications list with one row per Institute author with \
        identified homonyms, dataframe of publications list with \
        one row per author that has not been identified as Institute employee).
    Note:
        Care is taken to keep 'NA' value for the first name initiales \
        (that are set to NaN otherwise) through the `keep_initials` function \
        imported from `bmfuncts.useful_functs` module.
    """
    # Replace in "pub_df" NaN values "NA" in first name initials
    pub_df = keep_initials(pub_df, pg.COL_NAMES_BM['First_name'])

    # Initializing a Data frame that will contain all matches
    # between 'pub_df' author-name and 'empl_df' emmployee-name
    submit_df = pd.DataFrame()

    # Initializing a Data frame that will contain all 'pub_df' author-names
    # which do not match with any of the 'empl_df' emmployee-names
    orphan_df = pd.DataFrame(columns=list(pub_df.columns))

    # Building the set of lastnames (without duplicates) of the dataframe 'empl_df'
    eff_lastnames = set(empl_df[eg.EMPLOYEES_USEFUL_COLS['name']].to_list())
    eff_lastnames = [' ' + x + ' ' for x in eff_lastnames]

    # Setting the useful info for testing the function
    # Setting a dict keyed by type of test with values for test states and
    # test name from column [COL_NAMES_BM['Last_name']] of the dataframe 'pub_df'
    test_states, checks_path = _set_match_test_info(bibliometer_path, test_case)

    # Building submit_df and orphan_df dataframes
    for _, pub_df_row in pub_df.iterrows():

        # Building a dataframe 'empl_pub_match_df' with rows of 'empl_df'
        # where name in column COL_NAMES_BM['Last_name'] of the dataframe 'pub_df'
        # matches with name in column EMPLOYEES_USEFUL_COLS['name'] of the dataframe 'empl_df'

        # Initializing the flag 'flag_lastname_match' as True by default
        flag_lastname_match = True

        # Getting the lastname from pub_df_row row of the dataframe pub_df
        pub_lastname = pub_df_row[pg.COL_NAMES_BM['Last_name']]

        # Building the dataframe 'empl_pub_match_df' with rows of dataframe empl_df
        # where item at EMPLOYEES_USEFUL_COLS['name'] matches author lastname 'pub_lastname'
        empl_pub_match_df = empl_df[empl_df[eg.EMPLOYEES_USEFUL_COLS['name']]==pub_lastname].copy()

        # Test of lastname full match
        if pub_lastname==test_name and test_states[0]:
            _test_full_match(empl_pub_match_df, pub_lastname)

        if len(empl_pub_match_df)==0: # No match found
            flag_lastname_match = False
            # Checking for a similarity
            lastname_match_list = _reduce_orphan_df(pub_lastname, eff_lastnames)

            if lastname_match_list:
                # Concatenating in the dataframe 'empl_pub_match_df',
                # the rows of the dataframe 'empl_df'
                # corresponding to each of the found similarities by orphan reduction
                frames = []
                for lastname_match in lastname_match_list:
                    temp_df = empl_df[empl_df[eg.EMPLOYEES_USEFUL_COLS['name']]\
                                      ==lastname_match].copy()
                    # Replacing the employee last name by the publication last name
                    # for 'pub_emp_join_df' building
                    temp_df[eg.EMPLOYEES_ADD_COLS['employee_full_name']]=\
                        pub_lastname + ' ' + temp_df[pg.COL_NAMES_BM['First_name']]
                    frames.append(temp_df)

                empl_pub_match_df = concat_dfs(frames, concat_ignore_index=True)
                flag_lastname_match = True

                # Test of lastnames similarity found by '_reduce_orphan_df' function
                if pub_lastname==test_name and test_states[1]:
                    _test_similarity(empl_pub_match_df, pub_lastname,
                                     lastname_match_list, flag_lastname_match)

            else:
                # Appending to dataframe orphan_df the row 'pub_df_row'
                # as effective orphan after orphan reduction
                orphan_df = concat_dfs([orphan_df, pub_df_row.to_frame().T])
                flag_lastname_match = False

                # Test of lastnames no-similarity by '_reduce_orphan_df' function
                if pub_lastname==test_name and test_states[2]:
                    _test_no_similarity(pub_df_row, pub_lastname, lastname_match_list,
                                        flag_lastname_match)

        # Checking match for a given lastname between the publication first-name
        # and the employee first-name
        if flag_lastname_match:

            # Finding the author name initials for the current publication
            pub_firstname = pub_df_row[pg.COL_NAMES_BM['First_name']]

            # List of firstnames initials of a given name in the employees data
            eff_firstnames = empl_pub_match_df[pg.COL_NAMES_BM['First_name']].to_list()
            eff_lastnames_spec = empl_pub_match_df[eg.EMPLOYEES_USEFUL_COLS['name']].to_list()

            # Building the list of index of first names initials
            list_idx = []
            for idx, eff_firstname in enumerate(eff_firstnames):

                if pub_firstname==eff_firstname:
                    list_idx.append(idx)

            # Test of match of firstname initials for lastname match or similarity
            if pub_lastname==test_name and test_states[3]:
                _test_match_of_firstname_initials(pub_df_row, pub_lastname, pub_firstname,
                                                  eff_firstnames, list_idx, eff_lastnames_spec)

            if list_idx:
                # Building a dataframe 'temp_df' with the row 'pub_df_row'
                # related to a given publication
                # and adding the item value HOMONYM_FLAG
                # at column COL_NAMES_BM['Homonym']
                # when several matches on firstname initials are found
                temp_df = pub_df_row.to_frame().T
                temp_df[pg.COL_NAMES_BM['Homonym']]=\
                    pg.HOMONYM_FLAG if len(list_idx) > 1 else '_'

                # Saving specific dataframes 'temp_df' and 'empl_pub_match_df' for function testing
                if pub_lastname==test_name and test_states[4]:
                    _save_spec_dfs(temp_df, empl_pub_match_df, test_name, checks_path)

                # Merging the dataframe 'empl_pub_match_df' to the dataframe 'temp_df'
                # by matching column '[COL_NAMES_BM['Last_name']]' of the dataframe 'temp_df'
                # to the column 'EMPLOYEES_ADD_COLS['employee_full_name']'
                # of the dataframe 'empl_pub_match_df'
                pub_emp_join_df = pd.merge(temp_df,
                                           empl_pub_match_df,
                                           how='left',
                                           left_on=[pg.COL_NAMES_BM['Full_name']],
                                           right_on=[eg.EMPLOYEES_ADD_COLS['employee_full_name']])

                # Appending to the dataframe 'submit_df' the dataframe 'pub_emp_join_df'
                # which is specific to a given publication
                submit_df = concat_dfs([submit_df, pub_emp_join_df], concat_ignore_index=True)
            else:
                # Appending to the dataframe orphan_df the row 'pub_df_row' as effective orphan
                # after complementary checking of match via first name initials
                orphan_df = concat_dfs([orphan_df, pub_df_row.to_frame().T], concat_ignore_index=True)

    # Dropping duplicate rows in both dataframes (mandatory)
    submit_df = submit_df.drop_duplicates()
    orphan_df = orphan_df.drop_duplicates()

    return submit_df, orphan_df
