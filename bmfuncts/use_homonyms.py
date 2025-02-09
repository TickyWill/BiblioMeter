"""Module of functions for using publications attributes
such as homonyms and OTPs.

"""

__all__ = ['save_homonyms',
           'set_saved_homonyms',
           'solving_homonyms',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd
from openpyxl import Workbook as openpyxl_Workbook
from openpyxl.utils.dataframe import dataframe_to_rows \
    as openpyxl_dataframe_to_rows
from openpyxl.styles import PatternFill as openpyxl_PatternFill

# Local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg
from bmfuncts.rename_cols import build_col_conversion_dic
from bmfuncts.rename_cols import set_homonym_col_names
from bmfuncts.useful_functs import concat_dfs


def _save_shaped_homonyms_file(homonyms_df, out_path):
    """Saves as openpyxl workbook the dataframe for resolving 
    homonymies by the user.

    Args:
        homonyms_df (dtaframe): Data for resolving homonymies.
        out_path (path): Full path for saving the created workbook.
    """
    # Setting useful column names
    col_homonyms = list(homonyms_df.columns)

    # Useful aliases of renamed columns names
    name_alias = col_homonyms[12]
    firstname_alias = col_homonyms[13]
    homonym_alias = col_homonyms[18]

    wb = openpyxl_Workbook()
    ws = wb.active
    ws.title = 'Consolidation Homonymes'
    yellow_ft = openpyxl_PatternFill(fgColor=pg.ROW_COLORS['highlight'],
                                     fill_type="solid")

    for indice, r in enumerate(openpyxl_dataframe_to_rows(homonyms_df,
                                                          index=False, header=True)):
        ws.append(r)
        last_row = ws[ws.max_row]
        if r[col_homonyms.index(homonym_alias)]==pg.HOMONYM_FLAG and indice>0:
            cell = last_row[col_homonyms.index(name_alias)]
            cell.fill = yellow_ft
            cell = last_row[col_homonyms.index(firstname_alias)]
            cell.fill = yellow_ft

    wb.save(out_path)


def solving_homonyms(institute, org_tup, in_path, out_path):
    """Creates the file for homonyms solving by the user.

    First, a dataframe is built from specific columns 
    of the list of publications merged with employees database 
    given by the file pointed by 'in_path' path. 
    In this dataframe the homonyms are tagged by 'HOMONYM_FLAG' 
    global imported from `bmfuncts.pub_globals` module. 
    Then this dataframe is saved as Excel file pointed 
    by 'out_path' path through `_save_shaped_homonyms_file` 
    internal function.

    Args:
        institute (str): The Intitute name.
        org_tup (tup): The tuple of the organization structure of the Institute \
        used here to set column names for homonyms.
        in_path (path): The full path to the input file of list of publications \
        merged with employees database.
        out_path (path): The full path to the output file of homonyms solving \
        by the user.
    Returns:
        (tup): The tuple composed of end message (str) \
        and homonyms status (bool; True if homonyms are found).
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
    _save_shaped_homonyms_file(df_homonyms, out_path)

    end_message = f"File for solving homonymies saved in folder: \n  '{out_path}'"
    return end_message, homonyms_status


def save_homonyms(institute, org_tup, bibliometer_path, corpus_year):
    """Saves the history of the resolved homonyms by the user.

    First, builds the dataframe to save with the following columns:

        - Hash-ID of the publication for which homonyms have been solved.
        - The personal number of the kept author among the homonyms.

    Finally, saves the dataframe as Excel file.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
    Returns:
        (str): End message.
    """

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    submit_col_rename_dic = col_rename_tup[1]
    pub_id_col_alias = submit_col_rename_dic[bp.COL_NAMES["pub_id"]]
    author_idx_col_alias = submit_col_rename_dic[bp.COL_NAMES["authors"][1]]
    homonyms_col_alias = submit_col_rename_dic[pg.COL_NAMES_BONUS['homonym']]
    matricule_col_alias = submit_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['matricule']]

    # Setting useful folder and file aliases
    bdd_mensuelle_alias = pg.ARCHI_YEAR["bdd mensuelle"]
    homonyms_folder_alias = pg.ARCHI_YEAR["homonymes folder"]
    homonyms_file_base_alias = pg.ARCHI_YEAR["homonymes file name base"]
    history_folder_alias = pg.ARCHI_YEAR["history folder"]
    kept_homonyms_file_alias = pg.ARCHI_YEAR["kept homonyms file name"]
    hash_id_file_alias = pg.ARCHI_YEAR["hash_id file name"]
    homonyms_file_alias = homonyms_file_base_alias + ' ' + corpus_year + ".xlsx"

    # Setting useful paths
    corpus_year_path = bibliometer_path / Path(corpus_year)
    bdd_mensuelle_path = corpus_year_path / Path(bdd_mensuelle_alias)
    hash_id_file_path = bdd_mensuelle_path / Path(hash_id_file_alias)
    homonyms_folder_path = corpus_year_path / Path(homonyms_folder_alias)
    homonyms_file_path = homonyms_folder_path / Path(homonyms_file_alias)
    history_folder_path = corpus_year_path / Path(history_folder_alias)
    kept_homonyms_file_path = history_folder_path / Path(kept_homonyms_file_alias)

    # Getting the hash_id dataframe
    hash_id_df = pd.read_excel(hash_id_file_path)

    # Getting the dataframe of homonyms to solve
    pub_df = pd.read_excel(homonyms_file_path)

    # Building dataframe of pub_id and kept personal numbers for solved homonyms
    temp_df = pub_df[pub_df[homonyms_col_alias]==pg.HOMONYM_FLAG]
    homonyms_df = pd.DataFrame(columns=temp_df.columns)
    for _, pub_id_df in temp_df.groupby(pub_id_col_alias):
        for _, author_df in pub_id_df.groupby(author_idx_col_alias):
            if len(author_df)==1:
                homonyms_df = concat_dfs([homonyms_df, author_df])
    kept_matricules_df = homonyms_df[[pub_id_col_alias, matricule_col_alias]]

    # Building hash_id and kept matricules df
    homonyms_history_df = pd.merge(hash_id_df,
                                   kept_matricules_df,
                                   how='inner',
                                   on=pub_id_col_alias)
    homonyms_history_df = homonyms_history_df.drop(columns=[pub_id_col_alias])
    homonyms_history_df = homonyms_history_df.astype(str)

    # Concatenating with the dataframe of already saved solved homonyms
    if kept_homonyms_file_path.is_file():
        existing_homonyms_history_df = pd.read_excel(kept_homonyms_file_path)
        homonyms_history_df = concat_dfs([existing_homonyms_history_df, homonyms_history_df])
    homonyms_history_df = homonyms_history_df.astype('str')
    homonyms_history_df = homonyms_history_df.drop_duplicates()

    # Saving the concatenated dataframe
    homonyms_history_df.to_excel(kept_homonyms_file_path, index=False)

    message = "History of homonyms resolution saved"
    return message


def set_saved_homonyms(institute, org_tup, bibliometer_path,
                       corpus_year, actual_homonym_status):
    """Resolves the homonyms from the history of the resolved homonyms 
    before submiting the file for resolving remaining homonyms to the user.

    First, builds the dataframe with solved homonyms and homonyms remaining \
    to be solved.

    Finally, saves the dataframe through the `_save_shaped_homonyms_file` \
    internal function.

    Args:
        institute (str): Institute name.
        org_tup (tup): Contains Institute parameters.
        bibliometer_path (path): Full path to working folder.
        corpus_year (str): 4 digits year of the corpus.
        actual_homonym_status (bool): True if homonyms exists.
    Returns:
        (tup): Tuple = (End message (str), actualized homonyms \
        status (bool).
    """

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    submit_col_rename_dic = col_rename_tup[1]
    pub_id_col_alias = submit_col_rename_dic[bp.COL_NAMES["pub_id"]]
    author_idx_col_alias = submit_col_rename_dic[bp.COL_NAMES["authors"][1]]
    homonyms_col_alias = submit_col_rename_dic[pg.COL_NAMES_BONUS['homonym']]
    matricule_col_alias = submit_col_rename_dic[eg.EMPLOYEES_USEFUL_COLS['matricule']]
    hash_id_col_alias = pg.COL_HASH['hash_id']

    # Setting useful folder and file aliases
    bdd_mensuelle_alias = pg.ARCHI_YEAR["bdd mensuelle"]
    homonyms_folder_alias = pg.ARCHI_YEAR["homonymes folder"]
    homonyms_file_base_alias = pg.ARCHI_YEAR["homonymes file name base"]
    history_folder_alias = pg.ARCHI_YEAR["history folder"]
    kept_homonyms_file_alias = pg.ARCHI_YEAR["kept homonyms file name"]
    hash_id_file_alias = pg.ARCHI_YEAR["hash_id file name"]
    homonyms_file_alias = homonyms_file_base_alias + ' ' + corpus_year + ".xlsx"

    # Setting useful paths
    corpus_year_path = bibliometer_path / Path(corpus_year)
    bdd_mensuelle_path = corpus_year_path / Path(bdd_mensuelle_alias)
    hash_id_file_path = bdd_mensuelle_path / Path(hash_id_file_alias)
    homonyms_folder_path = corpus_year_path / Path(homonyms_folder_alias)
    homonyms_file_path = homonyms_folder_path / Path(homonyms_file_alias)
    history_folder_path = corpus_year_path / Path(history_folder_alias)
    kept_homonyms_file_path = history_folder_path / Path(kept_homonyms_file_alias)

    if kept_homonyms_file_path.is_file():

        # Getting the kept homonyms dataframe
        homonyms_history_df = pd.read_excel(kept_homonyms_file_path)

        # Getting the hash_id dataframe
        hash_id_df = pd.read_excel(hash_id_file_path)

        # Building dataframe of pub_id and personal number to keep related to hash_id
        mats_to_keep_df = pd.merge(hash_id_df,
                                   homonyms_history_df,
                                   how='inner',
                                   on=hash_id_col_alias,)
        mats_to_keep_df = mats_to_keep_df.astype(str)
        mats_to_keep_df = mats_to_keep_df.drop(columns=[hash_id_col_alias])

        # Getting the resolved homonyms dataframe to be updated
        homonyms_df = pd.read_excel(homonyms_file_path)
        homonyms_df[matricule_col_alias] = homonyms_df[matricule_col_alias].astype(str)

        # Building the updated homonyms dataframe
        homonyms_df_new = pd.DataFrame(columns=homonyms_df.columns)

        for pub_id, pub_id_homonyms_df in homonyms_df.groupby(pub_id_col_alias):
            for _, author_df in pub_id_homonyms_df.groupby(author_idx_col_alias):
                if len(author_df)==1:
                    # Keeping row of authors without homonyms
                    homonyms_df_new = concat_dfs([homonyms_df_new, author_df])
                else:
                    pub_id_mats_to_keep_df = mats_to_keep_df[mats_to_keep_df[pub_id_col_alias]\
                                                             ==pub_id]
                    pub_id_mats_to_keep_list = list(pub_id_mats_to_keep_df[matricule_col_alias])
                    mats_to_check_list = list(author_df[matricule_col_alias])
                    mats_to_keep_list = [x for x in mats_to_check_list\
                                         if x in pub_id_mats_to_keep_list]

                    if mats_to_keep_list:
                        # Keeping only row of matricule to keep when homonymies have been resolved
                        mat_to_keep = mats_to_keep_list[0]
                        new_author_df = author_df[author_df[matricule_col_alias]\
                                                  ==mat_to_keep].copy()
                        new_author_df[homonyms_col_alias] = "_"
                        homonyms_df_new = concat_dfs([homonyms_df_new, new_author_df])
                    else:
                        # Keeping all rows when homonymies have not been resolved
                        homonyms_df_new = concat_dfs([homonyms_df_new, author_df])

        # Setting actual homonyms status
        actual_homonym_status = False
        if pg.HOMONYM_FLAG in homonyms_df_new[homonyms_col_alias].to_list():
            actual_homonym_status = True
        # Saving updated homonyms_df
        _save_shaped_homonyms_file(homonyms_df_new, homonyms_file_path)
        message = "Already resolved homonyms used"
    else:
        message = "No already resolved homonyms available"
    return message, actual_homonym_status
