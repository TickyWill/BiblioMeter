__all__ = ['recursive_year_search']
            
def _build_df_submit(df_eff, df_pub, bibliometer_path, test_case='No test'):

    """
    Description à venir
    """

    #Standard Library imports
    import os
    from pathlib import Path

    # 3rd party import
    import numpy as np
    import pandas as pd

    # Local library imports
    import BiblioMeter_FUNCTS as bmf

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioMeter_GUI.Globals_GUI import COL_NAMES_BM
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_RH
    from BiblioMeter_FUNCTS.BiblioMeterGlobalsVariables import COL_NAMES_BONUS

    # Création chemin vers résultats pour effectuer des checks étapes
    PATH_OF_CHECKS = Path(bibliometer_path) / Path('Results')

    def _orphan_reduction(orphan_lastname,eff_lastname):
        # A bug with "if ' TRAN ' in ' TUAN TRAN ':"
        orphan_lastname = ' ' + orphan_lastname + ' '
        lastname_match_list = []
        for eff_name in eff_lastname:
            if (orphan_lastname in eff_name) or (eff_name in orphan_lastname):
                lastname_match_list.append(eff_name.strip())
        return lastname_match_list

    def _test_full_match():
        if len(df_eff_pub_match)!=0:
            print('\nMatch found for author lastname:',pub_lastname)
            print(' Nb of matches:',len(df_eff_pub_match))
            print(' Employee matricule:',df_eff_pub_match[COL_NAMES_RH['ID']].to_list()[0])
            print(' Employee lastname:',df_eff_pub_match[COL_NAMES_RH['nom']].to_list()[0])
        else:
            print('\nNo match for author lastname:',pub_lastname)
            print('  Nb first matches:',len(df_eff_pub_match))

    def _test_similarity():
        print('\nSimilarities by orphan reduction for author lastname:',pub_lastname)
        print('  Lastname flag match:', flag_lastname_match)
        print('  Nb similarities by orphan reduction:',len(lastname_match_list))
        print('  List of lastnames with similarities:', lastname_match_list)
        print('  Employee matricules:',df_eff_pub_match[COL_NAMES_RH['ID']].to_list())
        print('  Employee lastnames:',df_eff_pub_match[COL_NAMES_RH['nom']].to_list())
        print('  Employee firstnames:',df_eff_pub_match[COL_NAMES_RH['prénom']].to_list())
        print('  Employee fullnames:',df_eff_pub_match[COL_NAMES_RH['Full_name']].to_list())    

    def _test_no_similarity():
        print('\nNo similarity by orphan reduction for author lastname:',pub_lastname)
        print('  Lastname flag match:', flag_lastname_match)
        print('  Nb similarities by orphan reduction:',len(lastname_match_list))
        print('  Orphan full author name:',df_pub_row[COL_NAMES['authors'][2]])
        print('  Orphan author lastname:',df_pub_row[COL_NAMES_BM['Last_name']])
        print('  Orphan author firstname initiales:',df_pub_row[COL_NAMES_BM['First_name']])

    def _test_match_of_firstname_initiales():
        print('\nInitiales for author lastname:',pub_lastname)
        print('  Author fullname:', df_pub_row[COL_NAMES['authors'][2]]) 
        print('  Author firstname initiales:',pub_firstname)
        print('\nInitiales of matching employees for author lastname:',pub_lastname)
        print('  Employees firstname initiales list:',eff_firstnames)                              
        print('\nChecking initiales matching for author lastname:',pub_lastname)
        print('  Nb of matching initiales:', len(list_idx))
        print('  Index list of matching initiales:',list_idx)
        print('  Employees lastnames list:',eff_lastnames_spec)

    def _save_spec_dfs():                       
        df_temp.to_excel(PATH_OF_CHECKS / Path('df_temp_' + test_name + '.xlsx'))
        df_eff_pub_match.to_excel(PATH_OF_CHECKS / Path('df_eff_pub_match_' + test_name + '.xlsx'))     

    # Initializing a Data frame that will contains all matches 
    # between 'df_pub' author-name and 'df_eff' emmployee-name
    df_submit = pd.DataFrame() 

    # Initializing a Data frame that will contains all 'df_pub' author-names 
    # which do not match with any of the 'df_eff' emmployee-names
    df_orphan = pd.DataFrame()

    # Building the set of lastnames (without duplicates) of the dataframe 'df_eff' 
    eff_lastnames = set(df_eff[COL_NAMES_RH['nom']].to_list())
    eff_lastnames = [' ' + x + ' ' for x in eff_lastnames]

    # Setting the useful info for testing the function if verbose = True
    # Setting a dict keyyed by type of test with values for test states and 
    # test name from column [COL_NAMES_BM['Last_name']] of the dataframe 'df_pub'
    # for testing this function for year 2021
    test_dict = {'Full match'            : [True, True, True,True,True,'SIMONATO'],
                 'Lower value similarity': [False,True, True,True,True,'SILVA' ],
                 'Upper value similarity': [False,True, True,True,True,'TUAN TRAN'],
                 'No similarity'         : [False,False,True,True,True,'LUIS GABRIEL'],
                 'No test'               : [False,False,False,False,False,'None']
                 }

    test_nb = len(test_dict[test_case])-1
    test_name = test_dict[test_case][test_nb]
    test_states = test_dict[test_case][0:test_nb]    

    # Building df_submit and df_orphan dataframes
    for _,df_pub_row in df_pub.iterrows(): 

        # Building a dataframe 'df_match_eff_publi' with rows of 'df_eff'
        # where name in column COL_NAMES_BM['Last_name'] of the dataframe 'df_pub' 
        # matches with name in column COL_NAMES_RH['Nom'] of the dataframe 'df_eff'

        # Initializing 'df_eff_pub_match' as dataframe
        df_eff_pub_match = pd.DataFrame()

        # Initializing the flag 'flag_lastname_match' as True by default
        flag_lastname_match = True

        # Getting the lastname from df_pub_row row of the dataframe df_pub
        pub_lastname = df_pub_row[COL_NAMES_BM['Last_name']]

        # Building the dataframe 'df_eff_pub_match' with rows of dataframe df_eff 
        # where item at COL_NAMES_RH['Nom'] matches author lastname 'pub_lastname'
        df_eff_pub_match = df_eff[df_eff[COL_NAMES_RH['nom']] == pub_lastname].copy()

        # Adding column COL_NAMES_BM['Full_name'] + '_eff' by combination of 
        # df_eff_pub_match[COL_NAMES_RH['Nom']] and df_eff_pub_match[COL_NAMES_BM['First_name']]
        #new_col = COL_NAMES_BM['Full_name']
        #df_eff_pub_match[new_col] =  df_eff_pub_match[COL_NAMES_RH['Nom']] + ' ' + df_eff_pub_match[COL_NAMES_BM['First_name']] #------------------------------------------

        # Test of lastname full match
        if pub_lastname == test_name and test_states[0]: _test_full_match()          

        if len(df_eff_pub_match) == 0: # No match found
            flag_lastname_match = False
            lastname_match_list = _orphan_reduction(pub_lastname,eff_lastnames) # check for a similarity

            if lastname_match_list: 
                # Concatenating in the dataframe 'df_eff_pub_match', the rows of the dataframe 'df_eff'
                # corresponding to each of the found similarities by orphan reduction
                col = COL_NAMES_RH['nom']
                frames = []
                for lastname_match in lastname_match_list:
                    df_temp = df_eff[df_eff[COL_NAMES_RH['nom']] == lastname_match].copy()
                    # Replacing the employee last name by the publication last name
                    # for df_pub_rh_join building
                    df_temp[COL_NAMES_RH['Full_name']] = pub_lastname + ' ' + df_temp[COL_NAMES_BM['First_name']] #------------------------------------------
                    frames.append(df_temp )

                df_eff_pub_match = pd.concat(frames, ignore_index=True)
                flag_lastname_match = True

                # Test of lastnames similarity found by '_orphan_reduction' function
                if pub_lastname == test_name and test_states[1]: _test_similarity()

            else: 
                # Appending to dataframe df_orphan the row 'df_pub_row'  as effective orphan after orphan reduction
                df_orphan = df_orphan.append(df_pub_row)
                flag_lastname_match = False

                # Test of lastnames no-similarity by '_orphan_reduction' function
                if pub_lastname == test_name and test_states[2]: _test_no_similarity             

        # Checking match for a given lastname between the publication first-name and the employee first-name
        if flag_lastname_match:

            # Finding the author name initiales for the current publication
            pub_firstname = df_pub_row[COL_NAMES_BM['First_name']]

            # List of firstnames initiales of a given name in the rh effectif
            eff_firstnames = df_eff_pub_match[COL_NAMES_BM['First_name']].to_list()
            eff_lastnames_spec = df_eff_pub_match[COL_NAMES_RH['nom']].to_list()

            #if pub_lastname == 'MARTIN': 
                #print(eff_firstnames)

            # Building the list of index of firsnames initiales 
            list_idx = []
            for idx,eff_firstname in enumerate(eff_firstnames):
                #if pub_lastname == 'MARTIN': 
                    #print()
                    #print('pub_lastname',pub_lastname, 'pub_firstname',pub_firstname)
                    #print('eff_firstnames',eff_firstnames,'eff_firstname',eff_firstname)

                if (pub_firstname == eff_firstname):
                    list_idx.append(idx)

                elif (pub_firstname == eff_firstname):
                    # Replacing the employee first name initials by the publication first name initials
                    # for df_pub_rh_join building
                    df_eff_pub_match[COL_NAMES_RH['Full_name']].iloc[idx] = pub_lastname + ' ' + pub_firstname
                    list_idx.append(idx)

                #if pub_lastname == 'MARTIN': 
                    #print(list_idx)
                    #print()

            # Test of match of firstname initiales for lastname match or similarity
            if pub_lastname == test_name and test_states[3]: _test_match_of_firstname_initiales()

            if list_idx: 
                # Building a dataframe df_temp with the row 'df_pub_row'related to a given publication 
                # and adding the item value 'HOMONYM' at column COL_NAMES_BM['Homonym'] 
                # when several matches on firstname initiales are found
                df_temp = df_pub_row.to_frame().T            
                df_temp[COL_NAMES_BM['Homonym']] = 'HOMONYM' if len(list_idx)>1 else ''

                # Saving specific dataframes 'df_temp' and 'df_eff_pub_match' for function testing
                if pub_lastname == test_name and test_states[4]: _save_spec_dfs()                       

                # Merging the dataframe 'df_eff_pub_match' to the dataframe 'df_temp' 
                # by matching column '[COL_NAMES_BM['Last_name']]' of the dataframe 'df_temp'
                # to the column '[COL_NAMES_RH['Nom']]' of the dataframe 'df_eff_pub_match'
                df_pub_rh_join = pd.merge(df_temp,
                                          df_eff_pub_match, 
                                          how = 'left',
                                          left_on = [COL_NAMES_BM['Full_name']],
                                          right_on = [COL_NAMES_RH['Full_name']])

                # Appending to the dataframe 'df_submit' the dataframe 'df_pub_rh_join'
                # which is specific to a given publication
                df_submit = df_submit.append(df_pub_rh_join, ignore_index = True)
            else:
                # Appending to the dataframe df_orphan the row 'df_pub_row' as effective orphan 
                # after complementary checking of match via firsname initiales
                df_orphan = df_orphan.append(df_pub_row)

    return df_submit, df_orphan

def _build_pubs_authors_Liten(year, bibliometer_path):

    """ 
    Description : 

    Uses the following globals :
    - PATH_DAT_DEDUPLICATED
    - LIST_INSTITUTIONS

    Args : 

    Returns : 

    """

    #Standard Library imports
    import os
    from pathlib import Path

    # 3rd party import
    import pandas as pd

    # Local library imports
    import BiblioMeter_FUNCTS as bmf

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Globals_GUI import COL_NAMES_BM
    from BiblioMeter_GUI.Globals_GUI import COL_NAMES_ORPHAN

    # Création des alias pour simplifier les accès
    corpus_path_alias = FOLDER_NAMES['corpus']
    wos_alias = FOLDER_NAMES['wos']
    scopus_alias = FOLDER_NAMES['scopus']

    scopus_path_alias = Path(corpus_path_alias) / Path(scopus_alias)
    wos_path_alias = Path(corpus_path_alias) / Path(wos_alias)

    parsing_path_alias = FOLDER_NAMES['parsing']
    rawdata_path_alias = FOLDER_NAMES['rawdata']

    concat_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['concat']
    dedupli_path_alias = Path(corpus_path_alias) / FOLDER_NAMES['dedup']

    article_path_alias = DIC_OUTDIR_PARSING['A']
    index_alias = COL_NAMES['address'][0]

    # Building useful paths
    PATH_DAT_DEDUPLICATED = Path(bibliometer_path) / Path(year) / Path(dedupli_path_alias) / Path(parsing_path_alias)

    def _retain_firstname_initiales(row):
        row = row.replace('-',' ')
        initiales = ''.join(row.split(' '))
        return initiales 

    def _split_lastname_firstname(row,digits_min=4):
        names_list = row.split()
        last_names_list = names_list[:-1]
        first_names_list = names_list[-1:]

        for name_idx,name in enumerate(last_names_list):

            if len(name)<digits_min and ('-' in name):
                first_names_list.append(name)
                first_names_list = first_names_list[::-1]
                last_names_list = last_names_list[:name_idx] + last_names_list[name_idx+1:]

        first_name_initiales = _retain_firstname_initiales((' ').join(first_names_list))
        last_name = (' ').join(last_names_list)

        return (last_name, first_name_initiales)

    def _build_filt_authors_inst():

        '''The function `_build_filt_authors_inst` builds the `filt_authors_inst` filter
        to select the authors by their institution.
        Returns a filter, as a Pandas Serie, with:
                - true if any institution in the institution list is equal to the author institution;
                - false elsewhere.
        '''

        filt_authors_inst = (df_authorsinst_authors['LITEN_France']==1) | (df_authorsinst_authors['INES_France']==1) # TO DO : faire en sorte qu'on construise en fonction de ce l'on souhaite chercher

        return filt_authors_inst

    # Getting ID of each author with institution by publication ID
    df_authorsinst = pd.read_csv(PATH_DAT_DEDUPLICATED / Path(DIC_OUTDIR_PARSING['I2']), 
                                 sep="\t")

    # Getting ID of each author with author name  
    df_authors = pd.read_csv(PATH_DAT_DEDUPLICATED / Path(DIC_OUTDIR_PARSING['AU']), 
                             sep="\t")

    # Getting ID of each publication with complementary info 
    df_articles = pd.read_csv(PATH_DAT_DEDUPLICATED / Path(DIC_OUTDIR_PARSING['A']), 
                              sep="\t")

    # Combining name of author to author ID with institution by publication ID
    df_authorsinst_authors = pd.merge(df_authorsinst, 
                                      df_authors, 
                                      how = 'inner', 
                                      left_on = [COL_NAMES['authors'][0],COL_NAMES['authors'][1]], 
                                      right_on = [COL_NAMES['authors'][0],COL_NAMES['authors'][1]])

    # Building the LITEN authors filter
    filt_authors_LITEN = _build_filt_authors_inst() 

    # Associating each publication (with its complementary info) with each of its LITEN authors
    # The resulting dataframe contents on a row for each LITEN author with the corresponding publication info 
    merged_df_Liten = pd.merge(df_authorsinst_authors[filt_authors_LITEN], 
                               df_articles, 
                               how = 'left', 
                               left_on = [COL_NAMES['authors'][0]], 
                               right_on = [COL_NAMES['authors'][0]])

    # Transforming to uppercase the LITEN author name which is in column COL_NAMES_BAU['co_author']
    col = COL_NAMES['authors'][2]
    merged_df_Liten[col] = merged_df_Liten[col].str.upper()

    # Spliting the LITEN author name to firstname initiales and lastname
    # and putting them as a tupple in column COL_NAMES_BM['Full_name']
    col_in, col_out = COL_NAMES['authors'][2], COL_NAMES_BM['Full_name'] #COL_NAMES_BM['Full_name'] 
    merged_df_Liten[col_out] = merged_df_Liten.apply(lambda row: 
                                                     _split_lastname_firstname(row[col_in]),
                                                     axis=1)

    # Spliting tuples of column COL_NAMES_BM['Full_name']
    # into the two columns COL_NAMES_BM['Last_name'] and COL_NAMES_BM['First_name']
    col_in = COL_NAMES_BM['Full_name'] #Last_name + firstname initials
    col1_out, col2_out = COL_NAMES_BM['Last_name'], COL_NAMES_BM['First_name']
    merged_df_Liten[[col1_out, col2_out]] = pd.DataFrame(merged_df_Liten[col_in].tolist())

    # Recasting tuples (NAME, INITIALS) into a single string 'NAME INITIALS'
    col_in = COL_NAMES_BM['Full_name'] #Last_name + firstname initials
    merged_df_Liten[col_in] = merged_df_Liten[col_in].apply(lambda x : ' '.join(x))

    return  merged_df_Liten

def recursive_year_search(path_in, path_out, path_eff_1, bibliometer_path, corpus_year, go_back_years):

    """
    Description à venir
    """

    # Standard library imports
    from pathlib import Path

    # 3rd party import
    import pandas as pd
    from datetime import date

    # Local library imports
    import BiblioMeter_FUNCTS as bmf

    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import FOLDER_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    from BiblioMeter_GUI.Globals_GUI import STOCKAGE_ARBORESCENCE
    from BiblioMeter_GUI.Globals_GUI import COL_NAMES_BM
    from BiblioMeter_GUI.Globals_GUI import COL_NAMES_ORPHAN
    from BiblioMeter_GUI.Globals_GUI import SUBMIT_FILE_NAME
    from BiblioMeter_GUI.Globals_GUI import ORPHAN_FILE_NAME
    
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import add_biblio_list
    from BiblioMeter_FUNCTS.BiblioMeterFonctions import ajout_IF

    ###################################
    # Building the articles dataframe #
    ###################################

    df_pub = _build_pubs_authors_Liten(corpus_year, bibliometer_path)

    ##########################################################
    # Building the search time extension of Liten co-authors #
    ##########################################################

    today_year = int(date.today().year)
    start_year = int(corpus_year)
    time_line_history = int(go_back_years)
    years = [str(i) for i in range(start_year - time_line_history + 1, start_year + 1)]
    years = years[::-1]

    #################################################################################################
    # Building recursively the `df_submit` and `df_orphan` dataframes using `df_eff` files of years #
    #################################################################################################

    # Initializing the dataframes to be built
    df_submit = pd.DataFrame() # Data frame containing all match between publi author name name and rh name name
    df_orphan = pd.DataFrame() # No match found between article LITEN author and rh names

    # Setting the test case
    test_list = ['Full match',            
                 'Lower value similarity',
                 'Upper value similarity',
                 'No similarity',
                 'No test'
                ]

    test_case = 'Upper value similarity'
    
    # Read the sheet `year` of `EFFECTIFS_FILE` file
    effectifs_path = path_eff_1 # Récupère ALL_Effectifs.xlsx
    
    df_eff = pd.read_excel(effectifs_path, sheet_name = None)

    # Building the initial dataframes
    df_submit, df_orphan =  _build_df_submit(df_eff[years[0]], df_pub, bibliometer_path, test_case = test_case)
    
    for step, year in enumerate(years):
    
        # Updating the dataframes 
        df_submit_add, df_orphan =  _build_df_submit(df_eff[year], df_orphan, bibliometer_path, test_case)

        # Updating df_submit 
        df_submit = df_submit.append(df_submit_add)
        
        year_submit_file_name = year + '_' + SUBMIT_FILE_NAME
        year_orphan_file_name = year + '_' + ORPHAN_FILE_NAME

        df_submit.to_excel(path_out / Path(year_submit_file_name), index = False)
        df_orphan.to_excel(path_out / Path(year_orphan_file_name), index = False) 

    #####################################################################
    # Saving results in `SUBMIT_FILE_NAME` and `ORPHAN_FILE_NAME` files #
    #####################################################################
    
    ### Normalisation des titres de journaux
    #df_submit['Journal'] = df_submit['Journal'].apply(lambda x : x.title())
    
    
    def _unique_pub_id(df):

        '''The `_unique_pub_id`transforms the column 'Pub_id' of the df by adding _yyyy to the value of the row.

        Args: 
            df (pandas.DataFrame()): pandas.DataFrame() that we want to modify.

        Returns:
            (pandas.DataFrame()): the df with its changed column.
        '''

        # Local libray imports
        from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

        # 3rd party library imports
        import pandas as pd

        # Useful alias
        year_alias = COL_NAMES['articles'][2]
        pub_id_alias = COL_NAMES['pub_id']

        annee = df[year_alias].iloc[0]
        
        def _rename_pub_id(old, annee):
            return f"{int(old)}_{annee}"

        df[pub_id_alias] = df[pub_id_alias].apply(lambda x: _rename_pub_id(x, f"{annee}"))
        
        return df
    
    # Changing Pub_id columns to a unique Pub_id depending on the year
    df_submit = _unique_pub_id(df_submit)

    df_submit.to_excel(path_out / Path(SUBMIT_FILE_NAME), index = False)

    
    ### Adding biblio
    add_biblio_list(path_out / Path(SUBMIT_FILE_NAME), path_out / Path(SUBMIT_FILE_NAME))
    
    ### Adding Impact Factor
    ajout_IF(path_out / Path(SUBMIT_FILE_NAME), path_out / Path(SUBMIT_FILE_NAME), bibliometer_path / Path(STOCKAGE_ARBORESCENCE['general'][7] / Path('IF all years.xlsx')), corpus_year)
       
    # df_orphan = df_orphan.reindex(columns = COL_NAMES_ORPHAN)
    
    df_orphan.to_excel(path_out / Path(ORPHAN_FILE_NAME), index = False)
    
    print('Results saved')