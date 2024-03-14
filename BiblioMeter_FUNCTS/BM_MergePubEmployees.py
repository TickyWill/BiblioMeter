__all__ = ['recursive_year_search']

def _build_df_submit(df_eff, df_pub, bibliometer_path, test_case = 'No test', verbose = False):

    """
    
    """

    #Standard Library imports
    import os
    from pathlib import Path

    # 3rd party import
    import numpy as np
    import pandas as pd
    import BiblioParsing as bp
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg

    def _orphan_reduction(orphan_lastname, eff_lastname):
        # A bug with "if ' TRAN ' in ' TUAN TRAN ':"
        orphan_lastname = ' ' + orphan_lastname + ' '
        lastname_match_list = []
        for eff_name in eff_lastname:
            if (orphan_lastname in eff_name) or (eff_name in orphan_lastname):
                lastname_match_list.append(eff_name.strip())
        return lastname_match_list

    def _test_full_match():
        if verbose:
            if len(df_eff_pub_match) != 0:
                print('\nMatch found for author lastname:', pub_lastname)
                print(' Nb of matches:', len(df_eff_pub_match))
                print(' Employee matricule:', df_eff_pub_match[emp_useful_cols_alias['matricule']].to_list()[0])
                print(' Employee lastname:', df_eff_pub_match[emp_useful_cols_alias['name']].to_list()[0])
            else:
                print('\nNo match for author lastname:', pub_lastname)
                print('  Nb first matches:', len(df_eff_pub_match))

    def _test_similarity():
        if verbose:
            print('\nSimilarities by orphan reduction for author lastname:', pub_lastname)
            print('  Lastname flag match:', flag_lastname_match)
            print('  Nb similarities by orphan reduction:', len(lastname_match_list))
            print('  List of lastnames with similarities:', lastname_match_list)
            print('  Employee matricules:', df_eff_pub_match[emp_useful_cols_alias['matricule']].to_list())
            print('  Employee lastnames:',  df_eff_pub_match[emp_useful_cols_alias['name']].to_list())
            print('  Employee firstnames:', df_eff_pub_match[emp_useful_cols_alias['first_name']].to_list())
            print('  Employee fullnames:',  df_eff_pub_match[emp_add_cols_alias['employee_full_name']].to_list())    

    def _test_no_similarity():
        if verbose:
            print('\nNo similarity by orphan reduction for author lastname:', pub_lastname)
            print('  Lastname flag match:', flag_lastname_match)
            print('  Nb similarities by orphan reduction:', len(lastname_match_list))
            print('  Orphan full author name:', df_pub_row[bp_colnames_alias['authors'][2]])
            print('  Orphan author lastname:',  df_pub_row[bm_colnames_alias['Last_name']])
            print('  Orphan author firstname initiales:', df_pub_row[bm_colnames_alias['First_name']])

    def _test_match_of_firstname_initiales():
        if verbose:
            print('\nInitiales for author lastname:', pub_lastname)
            print('  Author fullname:', df_pub_row[bp_colnames_alias['authors'][2]]) 
            print('  Author firstname initiales:', pub_firstname)
            print('\nInitiales of matching employees for author lastname:', pub_lastname)
            print('  Employees firstname initiales list:', eff_firstnames)                              
            print('\nChecking initiales matching for author lastname:', pub_lastname)
            print('  Nb of matching initiales:', len(list_idx))
            print('  Index list of matching initiales:', list_idx)
            print('  Employees lastnames list:', eff_lastnames_spec)

    def _save_spec_dfs():                       
        df_temp.to_excel(PATH_OF_CHECKS / Path('df_temp_' + test_name + '.xlsx'), index = False)
        df_eff_pub_match.to_excel(PATH_OF_CHECKS / Path('df_eff_pub_match_' + test_name + '.xlsx'), index = False)     
    
    # Creating path for saving test files
    PATH_OF_CHECKS = Path(bibliometer_path) / Path('Results')
    
    # Setting useful aliases
    bp_colnames_alias     = bp.COL_NAMES
    bm_colnames_alias     = pg.COL_NAMES_BM
    emp_useful_cols_alias = eg.EMPLOYEES_USEFUL_COLS
    emp_add_cols_alias    = eg.EMPLOYEES_ADD_COLS
            
    # Initializing a Data frame that will contains all matches 
    # between 'df_pub' author-name and 'df_eff' emmployee-name
    df_submit = pd.DataFrame() 

    # Initializing a Data frame that will contains all 'df_pub' author-names 
    # which do not match with any of the 'df_eff' emmployee-names
    df_orphan = pd.DataFrame(columns = list(df_pub.columns)) 

    # Building the set of lastnames (without duplicates) of the dataframe 'df_eff' 
    eff_lastnames = set(df_eff[emp_useful_cols_alias['name']].to_list())
    eff_lastnames = [' ' + x + ' ' for x in eff_lastnames]

    # Setting the useful info for testing the function if verbose = True
    # Setting a dict keyyed by type of test with values for test states and 
    # test name from column [COL_NAMES_BM['Last_name']] of the dataframe 'df_pub'
    # for testing this function for year 2021
    test_dict   = {'Full match'            : [True, True, True,True,True,'SIMONATO'],
                   'Lower value similarity': [False,True, True,True,True,'SILVA' ],
                   'Upper value similarity': [False,True, True,True,True,'TUAN TRAN'],
                   'No similarity'         : [False,False,True,True,True,'LUIS GABRIEL'],
                   'No test'               : [False,False,False,False,False,'None']
                   }

    test_nb     = len(test_dict[test_case])-1
    test_name   = test_dict[test_case][test_nb]
    test_states = test_dict[test_case][0:test_nb]    

    # Building df_submit and df_orphan dataframes
    for row_idx, df_pub_row in df_pub.iterrows(): 

        # Building a dataframe 'df_match_eff_publi' with rows of 'df_eff'
        # where name in column COL_NAMES_BM['Last_name'] of the dataframe 'df_pub' 
        # matches with name in column EMPLOYEES_USEFUL_COLS['name'] of the dataframe 'df_eff'

        # Initializing 'df_eff_pub_match' as dataframe
        df_eff_pub_match = pd.DataFrame()

        # Initializing the flag 'flag_lastname_match' as True by default
        flag_lastname_match = True

        # Getting the lastname from df_pub_row row of the dataframe df_pub
        pub_lastname = df_pub_row[bm_colnames_alias['Last_name']]

        # Building the dataframe 'df_eff_pub_match' with rows of dataframe df_eff 
        # where item at EMPLOYEES_USEFUL_COLS['name'] matches author lastname 'pub_lastname'
        df_eff_pub_match = df_eff[df_eff[emp_useful_cols_alias['name']] == pub_lastname].copy()

        # Test of lastname full match
        if pub_lastname == test_name and test_states[0]: _test_full_match()          

        if len(df_eff_pub_match) == 0: # No match found
            flag_lastname_match = False
            lastname_match_list = _orphan_reduction(pub_lastname, eff_lastnames) # check for a similarity

            if lastname_match_list: 
                # Concatenating in the dataframe 'df_eff_pub_match', the rows of the dataframe 'df_eff'
                # corresponding to each of the found similarities by orphan reduction
                col = emp_useful_cols_alias['name']
                frames = []
                for lastname_match in lastname_match_list:
                    df_temp = df_eff[df_eff[emp_useful_cols_alias['name']] == lastname_match].copy()
                    # Replacing the employee last name by the publication last name
                    # for df_pub_emp_join building
                    df_temp[emp_add_cols_alias['employee_full_name']] = pub_lastname + ' ' + df_temp[bm_colnames_alias['First_name']] 
                    frames.append(df_temp )

                df_eff_pub_match = pd.concat(frames, ignore_index = True)
                flag_lastname_match = True

                # Test of lastnames similarity found by '_orphan_reduction' function
                if pub_lastname == test_name and test_states[1]: _test_similarity()

            else:                    
                # Appending to dataframe df_orphan the row 'df_pub_row'  as effective orphan after orphan reduction
                df_orphan = pd.concat([df_orphan, df_pub_row.to_frame().T])
                #df_orphan = df_orphan.append(df_pub_row)
                flag_lastname_match = False

                # Test of lastnames no-similarity by '_orphan_reduction' function
                if pub_lastname == test_name and test_states[2]: _test_no_similarity             

        # Checking match for a given lastname between the publication first-name and the employee first-name
        if flag_lastname_match:

            # Finding the author name initiales for the current publication
            pub_firstname = df_pub_row[bm_colnames_alias['First_name']]

            # List of firstnames initiales of a given name in the employees data
            eff_firstnames = df_eff_pub_match[bm_colnames_alias['First_name']].to_list()
            eff_lastnames_spec = df_eff_pub_match[emp_useful_cols_alias['name']].to_list()

            # Building the list of index of firsnames initiales 
            list_idx = []
            for idx,eff_firstname in enumerate(eff_firstnames):

                if (pub_firstname == eff_firstname):
                    list_idx.append(idx)

                elif (pub_firstname == eff_firstname):
                    # Replacing the employee first name initials by the publication first name initials
                    # for df_pub_emp_join building
                    df_eff_pub_match[emp_add_cols_alias['employee_full_name']].iloc[idx] = pub_lastname + ' ' + pub_firstname
                    list_idx.append(idx)

            # Test of match of firstname initiales for lastname match or similarity
            if pub_lastname == test_name and test_states[3]: _test_match_of_firstname_initiales()

            if list_idx: 
                # Building a dataframe df_temp with the row 'df_pub_row' related to a given publication 
                # and adding the item value HOMONYM_FLAG at column COL_NAMES_BM['Homonym'] 
                # when several matches on firstname initiales are found
                df_temp = df_pub_row.to_frame().T            
                df_temp[bm_colnames_alias['Homonym']] = pg.HOMONYM_FLAG if len(list_idx) > 1 else '_'

                # Saving specific dataframes 'df_temp' and 'df_eff_pub_match' for function testing
                if pub_lastname == test_name and test_states[4]: _save_spec_dfs()                       

                # Merging the dataframe 'df_eff_pub_match' to the dataframe 'df_temp' 
                # by matching column '[COL_NAMES_BM['Last_name']]' of the dataframe 'df_temp'
                # to the column 'EMPLOYEES_ADD_COLS['employee_full_name']' of the dataframe 'df_eff_pub_match'
                df_pub_emp_join = pd.merge(df_temp,
                                           df_eff_pub_match, 
                                           how = 'left',
                                           left_on  = [bm_colnames_alias['Full_name']],
                                           right_on = [emp_add_cols_alias['employee_full_name']])

                # Appending to the dataframe 'df_submit' the dataframe 'df_pub_emp_join'
                # which is specific to a given publication
                df_submit = pd.concat([df_submit, df_pub_emp_join], ignore_index = True)
            else:
                # Appending to the dataframe df_orphan the row 'df_pub_row' as effective orphan 
                # after complementary checking of match via firsname initiales
                df_orphan = pd.concat([df_orphan, df_pub_row.to_frame().T], ignore_index = True)
    
    # Droping duplicate rows if both dataframes (mandatory)
    df_submit = df_submit.drop_duplicates()
    df_orphan = df_orphan.drop_duplicates()

    return df_submit, df_orphan


def _check_names_orthograph(bibliometer_path, init_df, col0, col1, col2):
    '''
    '''
    # Standard Library imports
    from pathlib import Path
    
    # 3rd party import
    import pandas as pd
    import warnings
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    # Setting useful aliases
    orphan_treat_alias    = pg.ARCHI_ORPHAN["root"]
    orthograph_file_alias = pg.ARCHI_ORPHAN["orthograph file"]
    ortho_lastname_init   = pg.COL_NAMES_ORTHO['last name init']
    ortho_initials_init   = pg.COL_NAMES_ORTHO['initials init']
    ortho_lastname_new    = pg.COL_NAMES_ORTHO['last name new']
    ortho_initials_new    = pg.COL_NAMES_ORTHO['initials new']
    
    # Setting useful path
    ortho_path = bibliometer_path / Path(orphan_treat_alias) / Path(orthograph_file_alias)
    
    # Reading data file targetted by 'ortho_path'
    ortho_col_list = list(pg.COL_NAMES_ORTHO.values())
    warnings.simplefilter(action = 'ignore', category = UserWarning)
    ortho_df = pd.read_excel(ortho_path, usecols = ortho_col_list)
    
    new_df = init_df.copy()
    for pub_row_num in range(len(init_df)):
        lastname_init = init_df[col1][pub_row_num]
        initiales_init = init_df[col2][pub_row_num]
        for ortho_row_num in range(len(ortho_df)):
            lastname_pub_ortho = ortho_df[ortho_lastname_init ][ortho_row_num]
            initials_pub_ortho = ortho_df[ortho_initials_init][ortho_row_num]

            if lastname_init == lastname_pub_ortho and initiales_init == initials_pub_ortho:
                lastname_eff_ortho = ortho_df[ortho_lastname_new][ortho_row_num]
                initials_eff_ortho = ortho_df[ortho_initials_new][ortho_row_num]
                new_df .loc[pub_row_num,col1] = lastname_eff_ortho
                new_df .loc[pub_row_num,col2] = initials_eff_ortho 
                new_df .loc[pub_row_num,col0] = lastname_eff_ortho + ' ' + initials_eff_ortho
   
    return new_df


def _check_names_to_replace(bibliometer_path, year, init_df, col0, col1, col2):
    '''
    '''
    # Standard Library imports
    from pathlib import Path
    
    # 3rd party import
    import pandas as pd
    import warnings
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg

    # Setting useful aliases
    orphan_treat_alias     = pg.ARCHI_ORPHAN["root"]
    complements_file_alias = pg.ARCHI_ORPHAN["complementary file"]            
    compl_to_replace_sheet = pg.SHEET_NAMES_ORPHAN['to replace']
    compl_lastname_init    = pg.COL_NAMES_COMPL['last name init']
    compl_initials_init    = pg.COL_NAMES_COMPL['initials init']
    compl_matricule        = pg.COL_NAMES_COMPL['matricule']
    compl_lastname_new     = pg.COL_NAMES_COMPL['last name new']
    compl_initials_new     = pg.COL_NAMES_COMPL['initials new']
    compl_year_pub         = pg.COL_NAMES_COMPL['publication year']
    compl_hash_id          = pg.COL_NAMES_COMPL['hash id']
    
    # Setting useful path
    complements_path = bibliometer_path / Path(orphan_treat_alias) / Path(complements_file_alias)
    
    # Getting the information of the year in the complementary file 
    compl_col_list = list(pg.COL_NAMES_COMPL.values())
    warnings.simplefilter(action = 'ignore', category = UserWarning)
    compl_df = pd.read_excel(complements_path, sheet_name = compl_to_replace_sheet, usecols = compl_col_list)
    year_compl_df = compl_df[compl_df[compl_year_pub] == int(year)]
    year_compl_df.reset_index(inplace = True)

    new_df = init_df.copy()
    for pub_row_num in range(len(init_df)):
        lastname_init = init_df[col1][pub_row_num]
        initiales_init = init_df[col2][pub_row_num]
        for compl_row_num in range(len(year_compl_df)):
            lastname_pub_compl = year_compl_df[compl_lastname_init][compl_row_num]
            initials_pub_compl = year_compl_df[compl_initials_init][compl_row_num]
            if lastname_init == lastname_pub_compl and initiales_init == initials_pub_compl:
                
                lastname_eff_compl = year_compl_df[compl_lastname_new][compl_row_num]
                initials_eff_compl = year_compl_df[compl_initials_new][compl_row_num]
                new_df .loc[pub_row_num,col1] = lastname_eff_compl
                new_df .loc[pub_row_num,col2] = initials_eff_compl 
                new_df .loc[pub_row_num,col0] = lastname_eff_compl + ' ' + initials_eff_compl
   
    return new_df


def _check_authors_to_remove(institute, bibliometer_path, pub_df, pub_last_col, pub_initials_col):
    '''
    '''
    # Standard Library imports
    from pathlib import Path
    
    # 3rd party import
    import pandas as pd
    import warnings
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    # Setting useful aliases
    orphan_treat_alias          = pg.ARCHI_ORPHAN["root"]
    outliers_file_alias         = pg.ARCHI_ORPHAN["complementary file"]
    outliers_sheet_alias        = pg.SHEET_NAMES_ORPHAN["to remove"] + institute
    outliers_lastname_col_alias = pg.COL_NAMES_EXT['last name']
    outliers_initials_col_alias = pg.COL_NAMES_EXT['initials']
    
    # Setting useful path
    outliers_path = bibliometer_path / Path(orphan_treat_alias) / Path(outliers_file_alias)

    # Reading the file giving the outliers
    warnings.simplefilter(action='ignore', category = UserWarning)
    outliers_df = pd.read_excel(outliers_path, 
                                sheet_name = outliers_sheet_alias,
                                usecols = [outliers_lastname_col_alias, 
                                           outliers_initials_col_alias])
    # Initializing the dataframe that will contain the rows to drop
    # with the same columns names as the dataframe to update
    drop_df = pd.DataFrame(columns = list(pub_df.columns))
    
    # Searching for the outliers in the dataframe to update by lastname and initiales
    for pub_row_num in range(len(pub_df)):
        pub_lastname  = pub_df[pub_last_col][pub_row_num]
        pub_initiales = pub_df[pub_initials_col][pub_row_num]
        for outliers_row_num in range(len(outliers_df)):
            outliers_lastname = outliers_df[outliers_lastname_col_alias][outliers_row_num]
            outliers_initials = outliers_df[outliers_initials_col_alias][outliers_row_num]
            if pub_lastname == outliers_lastname and pub_initiales == outliers_initials:
                # Setting the row to drop as a dataframe
                row_to_drop_df = pub_df.loc[pub_row_num].to_frame().T
                # Appending the row to drop to the dataframe that will contain all the rows to drop
                drop_df = pd.concat([drop_df, row_to_drop_df], ignore_index = True)              
    
    # Removing the rows to drop from the dataframe to update             
    new_pub_df = pd.concat([pub_df, drop_df]).drop_duplicates(keep = False)
   
    return new_pub_df


def _build_institute_pubs_authors(institute, year, bibliometer_path):

    """ 
    Uses following local functions of the module "BM_MergePubEmployees.py":
        - `_check_names_orthograph`
        - `_check_names_to_replace`.
    
    Args:
        year (str): Contains the corpus year defined by 4 digits.
        bibliometer_path (path): Full path of BiblioMeter files folder.

    Returns:
        (dataframe): Resulting from merging of publications list 
                     and employees of a specified institution.

    """

    #Standard Library imports
    import os
    from pathlib import Path

    # 3rd party import
    import pandas as pd
    import BiblioParsing as bp

    # Local imports
    import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_inst_org
    from BiblioMeter_FUNCTS.BM_ConfigUtils import set_user_config
    from BiblioMeter_FUNCTS.BM_UsefulFuncts import read_parsing_dict

    # Internal functions
    def _retain_firstname_initiales(row):
        row = row.replace('-',' ')
        initiales = ''.join(row.split(' '))
        return initiales 

    def _split_lastname_firstname(row, digits_min = 4):
        names_list = row.split()
        first_names_list = names_list[-1:]
        last_names_list  = names_list[:-1]
        for name_idx,name in enumerate(last_names_list):

            if len(name)<digits_min and ('-' in name):
                first_names_list.append(name)
                first_names_list = first_names_list[::-1]
                last_names_list  = last_names_list[:name_idx] + last_names_list[(name_idx + 1):]

        first_name_initiales = _retain_firstname_initiales((' ').join(first_names_list))
        last_name = (' ').join(last_names_list)
        return (last_name, first_name_initiales)

    def _build_filt_authors_inst(inst_col_list):       
        '''The function `_build_filt_authors_inst` builds the `filt_authors_inst` filter
        to select the authors by their institution.
        Returns a filter, as a Pandas Serie, with:
                - true if any institution in the institution list is equal to the author institution;
                - false elsewhere.
        '''
        
        for inst_idx, inst_col in enumerate(inst_col_list):
            if inst_idx==0: 
                filt_authors_inst = (df_authorsinst_authors[inst_col] == 1)
            else:
                filt_authors_inst = filt_authors_inst | (df_authorsinst_authors[inst_col] == 1)
        return filt_authors_inst
    
    # Setting useful col list
    bp_auth_col_list  = bp.COL_NAMES['authors']
    bp_pub_id_alias   = bp_auth_col_list[0]
    bp_auth_idx_alias = bp_auth_col_list[1]
    bp_co_auth_alias  = bp_auth_col_list[2]
    
    # Setting usefull aliases
    articles_item_alias   = bp.PARSING_ITEMS_LIST[0]
    authors_item_alias    = bp.PARSING_ITEMS_LIST[1]
    auth_inst_item_alias  = bp.PARSING_ITEMS_LIST[5]
    bm_colnames_alias     = pg.COL_NAMES_BM    
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
    df_authorsinst = dedup_parsing_dict[auth_inst_item_alias]

    # Getting ID of each author with author name  
    df_authors = dedup_parsing_dict[authors_item_alias]

    # Getting ID of each publication with complementary info 
    df_articles = dedup_parsing_dict[articles_item_alias]
    
    # Adding new column with year of initial publication which is the corpus year
    df_articles[corpus_year_col_alias] = year 

    # Combining name of author to author ID with institution by publication ID
    df_authorsinst_authors = pd.merge(df_authorsinst, 
                                      df_authors, 
                                      how = 'inner', 
                                      left_on  = [bp_pub_id_alias, bp_auth_idx_alias], 
                                      right_on = [bp_pub_id_alias, bp_auth_idx_alias])

    # Building the authors filter of the institution INSTITUTE
    org_tup = set_inst_org(ig.CONFIG_JSON_FILES_DICT[institute], 
                           dpt_label_key = ig.DPT_LABEL_KEY, 
                           dpt_otp_key = ig.DPT_OTP_KEY)
    institute_inst_list = [tuple(x) for x in org_tup[5]]
    institute_col_list  = [tup[0] + '_' + tup[1] for tup in institute_inst_list]
    filt_authors_inst = _build_filt_authors_inst(institute_col_list) 

    # Associating each publication (with its complementary info) whith each of its INSTITUTE authors
    # The resulting dataframe contains a row for each INSTITUTE author with the corresponding publication info 
    inst_merged_df = pd.merge(df_authorsinst_authors[filt_authors_inst], 
                              df_articles, 
                              how = 'left', 
                              left_on  = [bp_pub_id_alias], 
                              right_on = [bp_pub_id_alias])    

    # Transforming to uppercase the Institute author name which is in column COL_NAMES['co_author']
    col = bp_co_auth_alias
    inst_merged_df[col] = inst_merged_df[col].str.upper()
    

    # Spliting the Institute author name to firstname initiales and lastname
    # and putting them as a tupple in column COL_NAMES_BM['Full_name']
    col_in, col_out = bp_co_auth_alias, bm_colnames_alias['Full_name']  
    inst_merged_df[col_out] = inst_merged_df.apply(lambda row: 
                                                   _split_lastname_firstname(row[col_in]),
                                                   axis = 1)

    # Spliting tuples of column COL_NAMES_BM['Full_name']
    # into the two columns COL_NAMES_BM['Last_name'] and COL_NAMES_BM['First_name']
    col_in = bm_colnames_alias['Full_name'] #Last_name + firstname initials
    col1_out, col2_out = bm_colnames_alias['Last_name'], bm_colnames_alias['First_name']
    inst_merged_df[[col1_out, col2_out]] = pd.DataFrame(inst_merged_df[col_in].tolist())
    
    # Recasting tuples (NAME, INITIALS) into a single string 'NAME INITIALS'
    col_in = bm_colnames_alias['Full_name'] #Last_name + firstname initials
    inst_merged_df[col_in] = inst_merged_df[col_in].apply(lambda x : ' '.join(x))
    
    # Checking author name spelling and correct it then replacing author names resulting from publication metadata errors
    # finally Searching for authors external to Institute but tagged as affiliated to it 
    # and droping their row in the returned dataframe 
    col_full, col_last, col_initials = bm_colnames_alias['Full_name'], bm_colnames_alias['Last_name'], bm_colnames_alias['First_name']
    inst_merged_df = _check_names_orthograph(bibliometer_path, inst_merged_df, col_full, col_last, col_initials) 
    inst_merged_df = _check_names_to_replace(bibliometer_path, year, inst_merged_df, col_full, col_last, col_initials)
    inst_merged_df = _check_authors_to_remove(institute, bibliometer_path, inst_merged_df, col_last, col_initials)

    return  inst_merged_df


def _add_author_job_type(in_path, out_path):
    """The function `_add_author_job_type` adds a new column containing the job type for each author
    of each publication listed in an EXCEL file and saves it.
    The job type is get from the employee information available in 3 particular columns wich names 
    are defined by the global 'EMPLOYEES_USEFUL_COLS' at keys 'category', 'status' and 'qualification'.
    The name of the new column is defined by the global the 'COL_NAMES_BONUS' at key 'author_type'.
    
    Args:
        in_path (path): Full path of the working EXCEL file. 
        out_path (path): Full path of the file with the new column.
    
    Returns:
        (str): Message of completed run.
    
    Notes:
        The globals 'EMPLOYEES_CONVERTERS_DIC' and 'EMPLOYEES_USEFUL_COLS' are imported 
        from the module 'BM_EmployeesGlobals' of the package 'BiblioMeter_FUNCTS'. 
        The global 'COL_NAMES_BONUS'is imported from the module 'BM_PubGlobals' 
        of the package 'BiblioMeter_FUNCTS'.             
    """
    # 3rd party imports
    import pandas as pd 
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    # internal functions:    
    def _get_author_type(row):
        for col_name, dic in author_types_dic.items(): 
            for key,values_list in dic.items():
                values_status = [True for value in values_list if value in row[col_name]]
                if any(values_status): return key
        return '-'

    # Setting useful aliases
    category_col_alias      = eg.EMPLOYEES_USEFUL_COLS['category']
    status_col_alias        = eg.EMPLOYEES_USEFUL_COLS['status']
    qualification_col_alias = eg.EMPLOYEES_USEFUL_COLS['qualification']     
    author_type_col_alias   = pg.COL_NAMES_BONUS['author_type']
    
    author_types_dic = {category_col_alias      : eg.CATEGORIES_DIC, 
                        status_col_alias        : eg.STATUS_DIC, 
                        qualification_col_alias : eg.QUALIFICATION_DIC}

    # Read of the excel file with dates convertion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(in_path, converters = eg.EMPLOYEES_CONVERTERS_DIC)
    
    submit_df[author_type_col_alias] = submit_df.apply(_get_author_type, axis=1)
    
    submit_df.to_excel(out_path, index = False)
    
    end_message = f"Column with author job type added in file: \n  '{out_path}'"
    return end_message 


def _set_full_ref(title, first_author, journal_name, pub_year, doi):
    """ The function `_set_full_ref` built the full reference of an article.
    
    Args:
        title (str): Title of the article.
        first_author (str): First author of the article formated as 'NAME IJ'
                            with 'NAME' the lastname and 'IJ' the initials 
                            of the firstname of the author. 
        journal_name (str): Name of the journal where the article is published.
        pub_year (str): Publication year defined by 4 digits.
        doi (str): Digital identification of the article.
        
    Returns:
        (str): Full reference of the article.

    """
    full_ref  = f'{title}, '                     # add the reference's title
    full_ref += f'{first_author}. et al., '      # add the reference's first author
    full_ref += f'{journal_name.capitalize()}, ' # add the reference's journal name
    full_ref += f'{pub_year}, '                  # add the reference's publication year
    full_ref += f'{doi}'                         # add the reference's DOI
    return full_ref


def _add_biblio_list(in_path, out_path):
    """The function `_add_biblio_list` adds a new column containing the full reference 
    of each publication listed in an EXCEL file and saves it.
    The full reference is built by concatenating the folowing items: title, first author, year, journal, DOI.
    These items sould be available in the initial EXCEL file with columns names 
    defined by the global 'COL_NAMES' with the keys 'pub_id' and 'articles'.
    The name of the new column is defined by the global 'COL_NAMES_BONUS' at key 'liste biblio'.
    
    Args:
        in_path (path): Full path of the working EXCEL file. 
        out_path (path): Full path of the file with the new column.
    
    Returns:
        (str): Message of completed run.
    
    Notes:
        The local function `_set_full_ref` of the module 'BM_MergePubEmployees' 
        of the package 'BiblioMeter_FUNCTS'is used.
        The global 'COL_NAMES' is imported from the module 'BiblioSpecificGlobals'  
        of the package 'BiblioParsing'.
        The global 'EMPLOYEES_CONVERTERS_DIC' is imported from the module 'BM_EmployeesGlobals' 
        of the package 'BiblioMeter_FUNCTS'. 
        The global 'COL_NAMES_BONUS'is imported from the module 'BM_PubGlobals' 
        of the package 'BiblioMeter_FUNCTS'.             
    """
    # 3rd party imports
    import pandas as pd
    import BiblioParsing as bp
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg

    # Setting useful aliases
    pub_id_alias           = bp.COL_NAMES['pub_id']
    pub_first_author_alias = bp.COL_NAMES['articles'][1]
    pub_year_alias         = bp.COL_NAMES['articles'][2]
    pub_journal_alias      = bp.COL_NAMES['articles'][3]
    pub_doi_alias          = bp.COL_NAMES['articles'][6]
    pub_title_alias        = bp.COL_NAMES['articles'][9]   
    pub_full_ref_alias     = pg.COL_NAMES_BONUS['liste biblio']

    # Read of the excel file with dates convertion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(in_path, converters = eg.EMPLOYEES_CONVERTERS_DIC)

    articles_plus_full_ref_df = pd.DataFrame()
    for pub_id, pub_id_df in submit_df.groupby(pub_id_alias): # Split the frame into subframes with same Pub_id
        
        pub_id_first_row = pub_id_df.iloc[0]                  # Select the first row and build the full reference        
        title        = str(pub_id_first_row[pub_title_alias])
        first_author = str(pub_id_first_row[pub_first_author_alias])
        journal_name = str(pub_id_first_row[pub_journal_alias])
        pub_year     = str(pub_id_first_row[pub_year_alias])
        doi          = str(pub_id_first_row[pub_doi_alias])
        pub_id_df[pub_full_ref_alias] = _set_full_ref(title, first_author, journal_name, pub_year, doi)
        articles_plus_full_ref_df = pd.concat([articles_plus_full_ref_df, pub_id_df])

    articles_plus_full_ref_df.to_excel(out_path, index = False)
    
    end_message = f"Column with full reference of publication added in file: \n  '{out_path}'"
    return end_message


def _add_ext_docs(submit_path, orphan_path, ext_docs_path):
    """The function `_add_ext_docs` adds to the file pointed by the path 'submit_path' 
    new rows containing the informations of authors of the file pointed by the path 'orphan_path' 
    that are PhD students of the institution but not as employees of the institution.
    The list of these PhD students with the required information must be available in an EXCEL file
    which full path is 'ext_docs_path'.
    
    Args:
        submit_path (path): Full path of the EXCEL file to be completed 
        and initially created by the main function `recursive_year_search`. 
        orphan_path (path): Full path of the EXCEL file containing the list of authors affiliated 
        to the institution but not found in the employees database with articles information 
        and initially created by the main function `recursive_year_search`.
        ext_docs_path (path): Full path of the EXCEL file of the PHD students external to the institution.
    
    Returns:
        (str): Message of completed run.
    
    Notes:
        The global 'COL_NAMES' is imported from the module 'BiblioSpecificGlobals'  
        of the package 'BiblioParsing'.
        The globals 'COL_NAMES_BM', 'COL_NAMES_BONUS' and 'EXT_DOCS_COL_ADDS_LIST' 
        are imported from the module 'BM_PubGlobals' of the package 'BiblioMeter_FUNCTS'. 
        The globals 'EMPLOYEES_ADD_COLS', 'EMPLOYEES_CONVERTERS_DIC', 'EMPLOYEES_USEFUL_COLS' 
        and 'EXT_DOCS_USEFUL_COL_LIST',  are imported from the module 'BM_EmployeesGlobals' 
        of the package 'BiblioMeter_FUNCTS'. 
    
    """
    # 3rd party import
    import BiblioParsing as bp
    import pandas as pd
    import warnings

    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg

    # Setting aliases for useful column names
    pub_id_alias                      = bp.COL_NAMES['authors'][0]
    author_id_alias                   = bp.COL_NAMES['authors'][1]
    converters_alias                  = eg.EMPLOYEES_CONVERTERS_DIC      
    firstname_initials_col_base_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']    
    ext_docs_full_name_alias          = eg.EMPLOYEES_ADD_COLS['employee_full_name']
    ext_docs_last_name_alias          = eg.EMPLOYEES_USEFUL_COLS['name']
    ext_docs_useful_col_list_alias    = eg.EXT_DOCS_USEFUL_COL_LIST   
    ext_docs_pub_last_name_alias      = pg.COL_NAMES_PUB_NAMES['last name']
    ext_docs_pub_initials_alias       = pg.COL_NAMES_PUB_NAMES['initials']
    ext_docs_sheet_name_alias         = pg.SHEET_NAMES_ORPHAN["docs to add"]
    ext_docs_col_adds_list_alias      = pg.EXT_DOCS_COL_ADDS_LIST
    orphan_full_name_alias            = pg.COL_NAMES_BM['Full_name']
    orphan_last_name_alias            = pg.COL_NAMES_BM['Last_name']    
    
    # Reading of the existing submit excel file of the corpus year 
    # with dates conversion through converters_alias
    init_submit_df = pd.read_excel(submit_path, converters = converters_alias)
    init_orphan_df = pd.read_excel(orphan_path, converters = converters_alias)

    # Initializing new_submit_df with same column names as init_submit_df 
    new_submit_df = pd.DataFrame(columns = list(init_submit_df.columns))

    # Initializing the dataframe to be concatenated to init_submit_df in new_submit_df
    # with same column names as init_submit_df 
    new_submit_adds_df = pd.DataFrame(columns = list(init_submit_df.columns))
    
    # Aligning column names between init_submit_df and init_orphan_df 
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {firstname_initials_col_base_alias : firstname_initials_col_base_alias + "_x"}
    init_orphan_df.rename(columns = col_rename_dic, inplace = True)
    orphan_initials_alias = col_rename_dic[firstname_initials_col_base_alias]
    
    # Initializing new_orphan_df as copy of init_orphan_df
    #new_orphan_df = init_orphan_df.copy()
    new_orphan_df = pd.DataFrame(columns = list(init_orphan_df.columns))
    
    # Initializing the dataframe to be droped from init_orphan_df 
    # with same column names as init_orphan_df 
    orphan_drop_df = pd.DataFrame(columns = list(init_orphan_df.columns))

    # Reading of the external phd students excel file 
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    ext_docs_usecols = sum([[ext_docs_pub_last_name_alias, ext_docs_pub_initials_alias],
                            ext_docs_col_adds_list_alias,
                            ext_docs_useful_col_list_alias,],
                           [])
    warnings.simplefilter(action = 'ignore', category = UserWarning)
    ext_docs_df = pd.read_excel(ext_docs_path, 
                                sheet_name = ext_docs_sheet_name_alias,
                                usecols    = ext_docs_usecols,
                                converters = converters_alias)
    ext_docs_df.dropna(how ='all', inplace = True)

    # Searching for last names of init_orphan_df in ext_docs_df 
    # to update submit and orphan files using new_submit_adds_df and new_orphan_drop_df
    for orphan_row_num in range(len(init_orphan_df)):
        author_last_name = init_orphan_df[orphan_last_name_alias][orphan_row_num]
        author_initials  = init_orphan_df[orphan_initials_alias][orphan_row_num] 
        for ext_docs_row_num in range(len(ext_docs_df)):
            ext_docs_pub_last_name = ext_docs_df[ext_docs_pub_last_name_alias][ext_docs_row_num]
            ext_docs_pub_initials  = ext_docs_df[ext_docs_pub_initials_alias][ext_docs_row_num]
            if ext_docs_pub_last_name == author_last_name and ext_docs_pub_initials == author_initials:
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = init_orphan_df.loc[orphan_row_num].to_frame().T

                # Setting the row to copy from ext_docs_df as a dataframe
                row_to_copy_df = ext_docs_df.loc[ext_docs_row_num].to_frame().T
                
                # Droping the columns of row_to_copy_df that should not be present in row_to_add_df  
                row_to_copy_df.drop([ext_docs_pub_last_name_alias, ext_docs_pub_initials_alias], axis = 1, inplace = True)

                # Merging the two dataframes on respective full name column  
                row_to_add_df = pd.merge(row_to_move_df, 
                                         row_to_copy_df, 
                                         left_on  = [orphan_full_name_alias],
                                         right_on = [ext_docs_full_name_alias], 
                                         how = 'left')

                # Appending the merged df to new_submit_adds_df
                new_submit_adds_df = pd.concat([new_submit_adds_df, row_to_add_df], ignore_index = True)

                # Appending row_to_move_df to  orphan_drop_df
                orphan_drop_df = pd.concat([orphan_drop_df, row_to_move_df], ignore_index = True)

    # Concatenating init_submit_df and new_submit_adds_df            
    new_submit_df = pd.concat([init_submit_df, new_submit_adds_df])
    new_submit_df.sort_values([pub_id_alias, author_id_alias], inplace = True)
    
    # Droping orphan_drop_df rows from init_orphan_df
    new_orphan_df = pd.concat([init_orphan_df, orphan_drop_df]).drop_duplicates(keep = False)
    
    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {firstname_initials_col_base_alias + "_x" : firstname_initials_col_base_alias}
    new_orphan_df.rename(columns = col_invert_rename_dic, inplace = True)
    
    # Saving new_submit_df and new_orphan_df replacing init_submit_df and init_submit_df
    new_submit_df.to_excel(submit_path, index = False)
    new_orphan_df.to_excel(orphan_path, index = False)
    
    return (new_submit_df, new_orphan_df)


def _add_other_ext(submit_path, orphan_path, others_path):
    """The function `_add_other_ext` adds to the file pointed by the path 'submit_path' 
    new rows containing the informations of authors of the file pointed by the path 'orphan_path' 
    that are under external hiring contract in the institution.
    The list of these employees with the required information must be available in an EXCEL file
    which full path is 'others_path'.
    
    Args:
        submit_path (path): Full path of the EXCEL file to be completed 
        and initially created by the main function `recursive_year_search`. 
        orphan_path (path): Full path of the EXCEL file containing the list of authors affiliated 
        to the institution but not found in the employees database with articles information 
        and initially created by the main function `recursive_year_search`.
        others_path (path): Full path of the EXCEL file of the author to add while external to the institution.
    
    Returns:
        (str): Message of completed run.
    
    Notes:
        The global 'COL_NAMES' is imported from the module 'BiblioSpecificGlobals'  
        of the package 'BiblioParsing'.
        The globals 'COL_NAMES_BM', 'COL_NAMES_BONUS' and 'EXT_DOCS_COL_ADDS_LIST' 
        are imported from the module 'BM_PubGlobals' of the package 'BiblioMeter_FUNCTS'. 
        The globals 'EMPLOYEES_ADD_COLS', 'EMPLOYEES_CONVERTERS_DIC', 'EMPLOYEES_USEFUL_COLS' 
        and 'EXT_DOCS_USEFUL_COL_LIST',  are imported from the module 'BM_EmployeesGlobals' 
        of the package 'BiblioMeter_FUNCTS'. 
    
    """
    # 3rd party import
    import pandas as pd
    import warnings
    import BiblioParsing as bp

    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg

    # Setting aliases for useful column names 
    pub_id_alias                      = bp.COL_NAMES['authors'][0]
    author_id_alias                   = bp.COL_NAMES['authors'][1]
    converters_alias                  = eg.EMPLOYEES_CONVERTERS_DIC
    firstname_initials_col_base_alias = eg.EMPLOYEES_ADD_COLS['first_name_initials']
    others_full_name_alias            = eg.EMPLOYEES_ADD_COLS['employee_full_name']
    others_last_name_alias            = eg.EMPLOYEES_USEFUL_COLS['name']
    ext_docs_useful_col_list_alias    = eg.EXT_DOCS_USEFUL_COL_LIST
    others_pub_last_name_alias        = pg.COL_NAMES_PUB_NAMES['last name']
    others_pub_initials_alias         = pg.COL_NAMES_PUB_NAMES['initials']
    others_sheet_name_alias           = pg.SHEET_NAMES_ORPHAN["others to add"]
    ext_docs_col_adds_list_alias      = pg.EXT_DOCS_COL_ADDS_LIST
    orphan_full_name_alias            = pg.COL_NAMES_BM['Full_name']
    orphan_last_name_alias            = pg.COL_NAMES_BM['Last_name']        
    
    # Reading of the existing submit excel file of the corpus year 
    # with dates conversion through converters_alias 
    init_submit_df = pd.read_excel(submit_path, converters = converters_alias)
    init_orphan_df = pd.read_excel(orphan_path, converters = converters_alias)

    # Initializing new_submit_df with same column names as init_submit_df 
    new_submit_df = pd.DataFrame(columns = list(init_submit_df.columns))

    # Initializing the dataframe to be concatenated to init_submit_df in new_submit_df
    # with same column names as init_submit_df 
    new_submit_adds_df = pd.DataFrame(columns = list(init_submit_df.columns))
    
    # Aligning column names between init_submit_df and init_orphan_df 
    # to feed new_submit_adds_df with same column names as init_submit_df
    col_rename_dic = {firstname_initials_col_base_alias : firstname_initials_col_base_alias + "_x"}
    init_orphan_df.rename(columns = col_rename_dic, inplace = True)
    orphan_initials_alias = col_rename_dic[firstname_initials_col_base_alias]
    
    # Initializing new_orphan_df as copy of init_orphan_df
    #new_orphan_df = init_orphan_df.copy()
    new_orphan_df = pd.DataFrame(columns = list(init_orphan_df.columns))
    
    # Initializing the dataframe to be droped from init_orphan_df 
    # with same column names as init_orphan_df 
    orphan_drop_df = pd.DataFrame(columns = list(init_orphan_df.columns))

    # Reading of the external phd students excel file 
    # using the same useful columns as init_submit_df defined by EXT_DOCS_USEFUL_COL_LIST
    # with dates conversion through converters_alias
    # and drop of empty rows
    others_usecols   = sum([[others_pub_last_name_alias, others_pub_initials_alias],
                            ext_docs_col_adds_list_alias,
                            ext_docs_useful_col_list_alias,],
                           [])
    warnings.simplefilter(action='ignore', category=UserWarning)
    others_df   = pd.read_excel(others_path, 
                                sheet_name = others_sheet_name_alias,
                                usecols   = others_usecols,
                                converters = converters_alias)
    others_df.dropna(how='all', inplace=True)

    # Searching for last names of init_orphan_df in others_df 
    # to update submit and orphan files using new_submit_adds_df and new_orphan_drop_df
    for orphan_row_num in range(len(init_orphan_df)):
        author_last_name = init_orphan_df[orphan_last_name_alias][orphan_row_num]
        author_initials  = init_orphan_df[orphan_initials_alias][orphan_row_num] 
        for others_row_num in range(len(others_df)):
            others_pub_last_name = others_df[others_pub_last_name_alias][others_row_num]
            others_pub_initials  = others_df[others_pub_initials_alias][others_row_num]
            if others_pub_last_name == author_last_name and others_pub_initials == author_initials:
                # Setting the row to move from init_orphan_df as a dataframe
                row_to_move_df = init_orphan_df.loc[orphan_row_num].to_frame().T

                # Setting the row to copy from others_df as a dataframe
                row_to_copy_df = others_df.loc[others_row_num].to_frame().T
                
                # Droping the columns of row_to_copy_df that should not be present in row_to_add_df  
                row_to_copy_df.drop([others_pub_last_name_alias, others_pub_initials_alias], axis=1, inplace = True)

                # Merging the two dataframes on respective full name column  
                row_to_add_df = pd.merge(row_to_move_df, 
                                         row_to_copy_df, 
                                         left_on  = [orphan_full_name_alias],
                                         right_on = [others_full_name_alias], 
                                         how = 'left')

                # Appending the merged df to new_submit_adds_df
                new_submit_adds_df = pd.concat([new_submit_adds_df, row_to_add_df], ignore_index = True)
                #new_submit_adds_df = new_submit_adds_df.append(row_to_add_df, ignore_index = True, sort = False) 

                # Appending row_to_move_df to  orphan_drop_df
                orphan_drop_df = pd.concat([orphan_drop_df, row_to_move_df], ignore_index = True)
                #orphan_drop_df = orphan_drop_df.append(row_to_move_df, ignore_index = True, sort = False)
                
    # Concatenating init_submit_df and new_submit_adds_df            
    new_submit_df = pd.concat([init_submit_df, new_submit_adds_df])
    new_submit_df.sort_values([pub_id_alias, author_id_alias], inplace = True)
    
    # Droping orphan_drop_df rows from init_orphan_df
    new_orphan_df = pd.concat([init_orphan_df, orphan_drop_df]).drop_duplicates(keep=False)
    
    # Recovering the initial column names of init_orphan_df
    col_invert_rename_dic = {firstname_initials_col_base_alias + "_x" : firstname_initials_col_base_alias}
    new_orphan_df.rename(columns = col_invert_rename_dic, inplace = True)
    
    # Saving new_submit_df and new_orphan_df replacing init_submit_df and init_submit_df
    new_submit_df.to_excel(submit_path, index = False)
    new_orphan_df.to_excel(orphan_path, index = False)
    
    return (new_submit_df, new_orphan_df)


def _change_col_names(institute, submit_path, orphan_path):
    """
    
    """

    # Standard library imports
    from pathlib import Path

    # 3rd party imports
    import pandas as pd    
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_RenameCols import build_col_conversion_dic
    
    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute)
    orphan_col_rename_dic = col_rename_tup[0]
    submit_col_rename_dic = col_rename_tup[1]
    
    # Read of the 'submit' file with dates convertion through EMPLOYEES_CONVERTERS_DIC
    submit_df = pd.read_excel(submit_path, converters = eg.EMPLOYEES_CONVERTERS_DIC)    
    submit_df.rename(columns = submit_col_rename_dic, inplace = True)

    # Resaving df_submit
    submit_df.to_excel(submit_path, index = False)
    
    # Read of the 'orphan' file 
    orphan_df = pd.read_excel(orphan_path)    
    orphan_df.rename(columns = orphan_col_rename_dic, inplace = True)

    # Resaving df_submit
    orphan_df.to_excel(orphan_path, index = False)
    
    end_message = f"Column renamed in files: \n  '{submit_path}' \n  '{orphan_path}' "
    return end_message


def _myHash(text:str):
    my_hash = 0
    facts = (257,961) # prime numbers to mix up the bits
    minus_one = 0xFFFFFFFF # "-1" hex code
    for ch in text:
        my_hash = (my_hash*facts[0] ^ ord(ch)*facts[1]) & minus_one
    #my_hash_hex = hex(my_hash)[2:].upper().zfill(8)  # to return hex value of hash
    return my_hash


def _creating_hash_id(institute, bibliometer_path, corpus_year):
    """
    """
    # Standard library imports
    from pathlib import Path
    
    # 3rd library imports
    import pandas as pd    
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    from BiblioMeter_FUNCTS.BM_RenameCols import build_col_conversion_dic
    
    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute)
    submit_col_rename_dic = col_rename_tup[1]
  
    # Setting useful aliases
    bdd_mensuelle_alias  = pg.ARCHI_YEAR["bdd mensuelle"]
    submit_file_alias    = pg.ARCHI_YEAR["submit file name"]
    orphan_file_alias    = pg.ARCHI_YEAR["orphan file name"]
    hash_id_file_alias   = pg.ARCHI_YEAR["hash_id file name"]
    hash_id_col_alias    = pg.COL_HASH['hash_id']
    pub_id_alias         = submit_col_rename_dic['Pub_id']
    year_alias           = submit_col_rename_dic['Year']
    first_auth           = submit_col_rename_dic['Authors']
    title_alias          = submit_col_rename_dic['Title']
    ISSN_alias           = submit_col_rename_dic['ISSN']
    doi_alias            = submit_col_rename_dic['DOI']     
       
    # Setting useful paths
    corpus_year_path   = bibliometer_path / Path(corpus_year)
    bdd_mensuelle_path = corpus_year_path / Path(bdd_mensuelle_alias)
    submit_file_path   = bdd_mensuelle_path / Path(submit_file_alias)
    orphan_file_path   = bdd_mensuelle_path / Path(orphan_file_alias)
    hash_id_file_path  = bdd_mensuelle_path / Path(hash_id_file_alias)
    
    # Setting useful columns list
    useful_cols = [pub_id_alias, year_alias, first_auth, title_alias, ISSN_alias, doi_alias ]
        
    # Getting dataframes to hash
    submit_to_hash = pd.read_excel(submit_file_path, usecols = useful_cols)
    orphan_to_hash = pd.read_excel(orphan_file_path, usecols = useful_cols)
    
    # Concatenate de dataframes to hash
    dg_to_hash = pd.concat([submit_to_hash, orphan_to_hash])
    
    # Droping rows of same pub_id_alias and reindexing the rows using ignore_index
    dg_to_hash.drop_duplicates(subset = [pub_id_alias], inplace = True, ignore_index = True)
    
    hash_id_df = pd.DataFrame()    
    for idx in range(len(dg_to_hash)):
        pub_id = dg_to_hash.loc[idx, pub_id_alias]                
        text   = str(dg_to_hash.loc[idx, year_alias])
        text  += str(dg_to_hash.loc[idx, first_auth])
        text  += str(dg_to_hash.loc[idx, title_alias])
        text  += str(dg_to_hash.loc[idx, ISSN_alias])
        text  += str(dg_to_hash.loc[idx, doi_alias])
        hash_id = _myHash(text)
        hash_id_df.loc[idx, hash_id_col_alias] = str(hash_id)
        hash_id_df.loc[idx, pub_id_alias] = pub_id

    hash_id_df.to_excel(hash_id_file_path, index = False)    
    
    message = f"Hash id of publications created"
    return message


def recursive_year_search(path_out, effectifs_path, institute, bibliometer_path, corpus_year, go_back_years):
    """
    Uses following local functions of the module "BM_MergePubEmployees.py":
    - `_build_institute_pubs_authors`
    - `_build_df_submit`
    - `_add_ext_docs`
    - `_add_other_ext`
    - `_add_author_job_type`
    - `_add_biblio_list`
    - `_change_col_names`   
    - `_creating_hash_id`
    """

    # Standard library imports
    from pathlib import Path

    # 3rd party imports
    import pandas as pd
    import BiblioParsing as bp
    
    # Local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    # Internal functions
    def _unique_pub_id(df):

        '''The local function `_unique_pub_id` transforms the column 'Pub_id' of the df 
        by adding "yyyy_" to the value of the row.

        Args: 
            df (pandas.DataFrame()): pandas.DataFrame() that we want to modify.

        Returns:
            (pandas.DataFrame()): the df with its changed column.
        '''
        df_year = df[year_col_alias].iloc[0]
        
        def _rename_pub_id(old_pub_id, year):
            pub_id_str = str(int(old_pub_id))
            while len(pub_id_str)<3: pub_id_str = "0" + pub_id_str
            new_pub_id = str(int(year)) + '_' + pub_id_str
            return new_pub_id

        df[pub_id_alias] = df[pub_id_alias].apply(lambda x: _rename_pub_id(x, df_year))
        return df  
    
    # Setting useful aliases
    unknown_alias          = bp.UNKNOWN
    year_col_alias         = bp.COL_NAMES['articles'][2]
    pub_id_alias           = bp.COL_NAMES['pub_id']    
    submit_file_name_alias = pg.ARCHI_YEAR["submit file name"]
    orphan_file_name_alias = pg.ARCHI_YEAR["orphan file name"]
    orphan_treat_alias     = pg.ARCHI_ORPHAN["root"]
    adds_file_name_alias   = pg.ARCHI_ORPHAN["employees adds file"]
    
    # Setting useful paths
    submit_path   = path_out / Path(submit_file_name_alias)
    orphan_path   = path_out / Path(orphan_file_name_alias)
    ext_docs_path = bibliometer_path / Path(orphan_treat_alias) / Path(adds_file_name_alias)
    others_path   = bibliometer_path / Path(orphan_treat_alias) / Path(adds_file_name_alias)
        
    # Getting the employees dataframe with the useful columns only
    useful_col_list = list(eg.EMPLOYEES_USEFUL_COLS.values()) + list(eg.EMPLOYEES_ADD_COLS.values())
    df_eff = pd.read_excel(effectifs_path, 
                           sheet_name = None, 
                           dtype = eg.EMPLOYEES_COL_TYPES, 
                           usecols = useful_col_list)
    eff_available_years = list(df_eff.keys())        
    corpus_year_status = corpus_year in eff_available_years 
    
    # Building the articles dataframe 
    df_pub = _build_institute_pubs_authors(institute, corpus_year, bibliometer_path)

    # Building the search time depth of Institute co-authors among the employees dataframe
    year_start = int(corpus_year)
    if not corpus_year_status : year_start = int(corpus_year)-1    
    time_line_history = int(go_back_years)
    year_stop = year_start - (time_line_history - 1)
    years = [str(i) for i in range(year_start, year_stop-1,-1)]

    #################################################################################################
    # Building recursively the `df_submit` and `df_orphan` dataframes using `df_eff` files of years #
    #################################################################################################

    # Initializing the dataframes to be built
    # a Data frame containing all matches between article Institute authors and employee names
    df_submit = pd.DataFrame()
    # a Data frame containing containing article Institute authors not matching with any employee name
    df_orphan = pd.DataFrame()

    # Setting the test case
    test_list = ['Full match',            
                 'Lower value similarity',
                 'Upper value similarity',
                 'No similarity',
                 'No test'
                ]

    test_case = 'Upper value similarity'
    
    # Building the initial dataframes
    df_submit, df_orphan = _build_df_submit(df_eff[years[0]], 
                                            df_pub, bibliometer_path, 
                                            test_case = test_case)
    
    # Saving initial files of df_submit and df_orphan
    df_submit.to_excel(submit_path, index = False)
    df_orphan.to_excel(orphan_path, index = False)

    # Adding authors from list of external_phd students and saving new df_submit and df_orphan
    df_submit, df_orphan = _add_ext_docs(submit_path, orphan_path, ext_docs_path)
    
    # Adding authors from list of external employees under other hiring contract and saving new df_submit and df_orphan
    df_submit, df_orphan = _add_other_ext(submit_path, orphan_path, others_path)
    
    for step, year in enumerate(years):   
        # Updating the dataframes df_submit_add and df_orphan
        df_submit_add, df_orphan =  _build_df_submit(df_eff[year], 
                                                     df_orphan, 
                                                     bibliometer_path, 
                                                     test_case) 

        # Updating df_submit and df_orphan
        df_submit = pd.concat([df_submit, df_submit_add])
        #df_submit = df_submit.append(df_submit_add)

    #####################################################################################
    # Saving results in 'submit_file_name_alias' file and 'orphan_file_name_alias' file #
    #####################################################################################
    
    # Replace NaN values by UNKNOWN string
    df_submit.fillna(unknown_alias, inplace=True)
    df_orphan.fillna(unknown_alias, inplace=True)
    orphan_status = df_orphan.empty

    # Changing Pub_id columns to a unique Pub_id depending on the year
    df_submit = _unique_pub_id(df_submit)
    if not orphan_status : df_orphan = _unique_pub_id(df_orphan)
    
    # Saving df_orphan
    df_orphan.to_excel(orphan_path, index = False)
    
    # Saving df_submit
    df_submit.to_excel(submit_path, index = False)
    
    # Adding author job type and saving new df_submit
    _add_author_job_type(submit_path, submit_path)
    
    # Adding full article reference and saving new df_submit
    _add_biblio_list(submit_path, submit_path)

    # Renaming column names using submit_col_rename_dic and orphan_col_rename_dic
    _change_col_names(institute, submit_path, orphan_path)
    
    # Creating universal identification of articles independant from database extraction
    _creating_hash_id(institute, bibliometer_path, corpus_year)    
    
    end_message = f"Results of search of authors in employees list saved in folder: \n  {path_out}" 
    return (end_message, orphan_status) 