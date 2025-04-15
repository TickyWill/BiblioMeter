"""Module of useful functions for setting columns names of dataframes.
"""

__all__ = ['build_col_conversion_dic',
           'set_homonym_col_names',
           'set_otp_col_names',
           'set_final_col_names',
           'set_if_col_names',
           'set_col_attr',
          ]


# 3rd party imports
import BiblioParsing as bp

# local imports
import bmfuncts.employees_globals as eg
import bmfuncts.pub_globals as pg

def build_col_conversion_dic(institute, org_tup):
    """Builds a dict for setting the final column names 
    given the initial column names of 3 dataframes.

    Args:
        institute (str): The Intitute name.
        org_tup (tup): The tuple of the organization structure \
        of the Institute.
    Returns:
        (tup): (dict for renaming the specific columns of the dataframe \
        of publications list with one row per author that has not been \
        identified as Institute employee, \
        dict for renaming the specific columns of the dataframe of merged \
        employees information with the publications list with one \
        row per Institute author, \
        dict for renaming the columns of all the results dataframes).
    """

    # Setting institute parameters
    col_names_dpt  = org_tup[0]
    dpt_col_list   = list(col_names_dpt.values())
    inst_col_list  = org_tup[4]

    init_orphan_col_list = sum([[pg.COL_HASH['hash_id']],
                                bp.COL_NAMES['auth_inst'][:5],
                                inst_col_list,
                                [bp.COL_NAMES['authors'][2]],
                                bp.COL_NAMES['articles'][1:11],
                                [pg.COL_NAMES_BONUS['corpus_year']],
                                [pg.COL_NAMES_BM['Full_name'],
                                 pg.COL_NAMES_BM['Last_name'],
                                 pg.COL_NAMES_BM['First_name']]], [])

    init_submit_col_list = sum([init_orphan_col_list,
                                [pg.COL_NAMES_BONUS['homonym']],
                                list(eg.EMPLOYEES_USEFUL_COLS.values()),
                                list(eg.EMPLOYEES_ADD_COLS.values()),
                                [pg.COL_NAMES_BONUS['author_type'],
                                 pg.COL_NAMES_BONUS['liste biblio']]], [])

    init_bm_col_list = sum([init_submit_col_list,
                            [pg.COL_NAMES_BONUS['nom prénom liste'],
                             pg.COL_NAMES_BONUS['liste auteurs'],
                             pg.COL_NAMES_BONUS['nom prénom'] + institute],
                            [pg.COL_NAMES_BONUS['list OTP'],
                             pg.COL_NAMES_BONUS['IF en cours'],
                             pg.COL_NAMES_BONUS['IF année publi']],
                            dpt_col_list], [])

    final_bm_col_list = sum([["Hash_id",
                              "Pub_id",
                              "Auteur_id",
                              "Adresse",
                              "Pays",
                              "Institutions"],
                             inst_col_list,
                             ["Co_auteur " + institute,
                              "Premier auteur",
                              "Année de publication finale",
                              "Journal",
                              "Volume",
                              "Page",
                              "DOI",
                              "Type du document",
                              "Langue",
                              "Titre",
                              "ISSN",
                              "Année de première publication"],
                             [pg.COL_NAMES_BM['Full_name'],
                              pg.COL_NAMES_BM['Last_name'],
                              pg.COL_NAMES_BM['First_name']],
                             ["Homonymes",
                              "Matricule",
                              "Nom",
                              "Prénom",
                              "Genre",
                              "Nationalité",
                              "Catégorie de salarié",
                              "Statut de salarié",
                              "Qualification classement",
                              "Date début contrat",
                              "Date dernière entrée",
                              "Date de fin de contrat",
                              "Dept",
                              "Serv",
                              "Labo",
                              "Affiliation",
                              "Date de naissance",
                              "Tranche d'age (5 ans)"],
                             list(eg.EMPLOYEES_ADD_COLS.values()),
                             [pg.COL_NAMES_BONUS['author_type'],
                              pg.COL_NAMES_BONUS['liste biblio'],
                              pg.COL_NAMES_BONUS['nom prénom liste'],
                              pg.COL_NAMES_BONUS['liste auteurs'],
                              pg.COL_NAMES_BONUS['nom prénom'] + institute],
                             [pg.COL_NAMES_BONUS['list OTP'],
                              pg.COL_NAMES_BONUS['IF en cours'],
                              pg.COL_NAMES_BONUS['IF année publi']],
                             dpt_col_list], [])

    all_col_rename_dic    = dict(zip(init_bm_col_list, final_bm_col_list))
    final_submit_col_list = [all_col_rename_dic[col] for col in init_submit_col_list]
    submit_col_rename_dic = dict(zip(init_submit_col_list, final_submit_col_list))
    final_orphan_col_list = [all_col_rename_dic[col] for col in init_orphan_col_list]
    orphan_col_rename_dic = dict(zip(init_orphan_col_list, final_orphan_col_list))

    return orphan_col_rename_dic, submit_col_rename_dic, all_col_rename_dic


def set_homonym_col_names(institute, org_tup):
    """Sets the dict for setting the final column names to be used for building 
    the dataframe for homonyms solving by the user.

    This is done through the `build_col_conversion_dic` function of 
    the same module.

    Args:
        institute (str): The Intitute name.
        org_tup (tup): The tuple of the organization structure \
        of the Institute.
    Returns:
        (dict): To be used for setting the final column names \
        of the dataframe built for homonyms solving by the user.
    """
    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    all_col_rename_dic = col_rename_tup[2]

    homonyms_col_dic_init = {'hash_id'       : pg.COL_HASH['hash_id'],
                             'pub_id'        : bp.COL_NAMES['pub_id'],
                             'corpus_year'   : pg.COL_NAMES_BONUS['corpus_year'],
                             'final_year'    : bp.COL_NAMES['articles'][2],
                             'inst_author'   : bp.COL_NAMES['authors'][2],
                             "all_authors"   : pg.COL_NAMES_BONUS['liste auteurs'],
                             'first_author'  : bp.COL_NAMES['articles'][1],
                             'title'         : bp.COL_NAMES['articles'][9],
                             'journal'       : bp.COL_NAMES['articles'][3],
                             'doc_type'      : bp.COL_NAMES['articles'][7],
                             'doi'           : bp.COL_NAMES['articles'][6],
                             'full_ref'      : pg.COL_NAMES_BONUS['liste biblio'],
                             'issn'          : bp.COL_NAMES['articles'][10],
                             'author_id'     : bp.COL_NAMES['auth_inst'][1],
                             'matricul'      : eg.EMPLOYEES_USEFUL_COLS['matricule'],
                             'last_name'     : eg.EMPLOYEES_USEFUL_COLS['name'],
                             'first_name'    : eg.EMPLOYEES_USEFUL_COLS['first_name'],
                             'author_type'   : pg.COL_NAMES_BONUS['author_type'],
                             'dpt'           : eg.EMPLOYEES_USEFUL_COLS['dpt'],
                             'serv'          : eg.EMPLOYEES_USEFUL_COLS['serv'],
                             'lab'           : eg.EMPLOYEES_USEFUL_COLS['lab'],
                             'empl_full_name': eg.EMPLOYEES_ADD_COLS['employee_full_name'],
                             'homonym'       : pg.COL_NAMES_BONUS['homonym'],
                             }

    homonyms_col_list = [all_col_rename_dic[name] for _, name in homonyms_col_dic_init.items()]
    homonyms_col_dic = dict(zip(homonyms_col_dic_init.keys(), homonyms_col_list))
    return homonyms_col_dic


def set_otp_col_names(institute, org_tup):
    """Sets the dict for setting the final column names to be used for building 
    the dataframes for OTPs attribution by the user.

    This is done through the `build_col_conversion_dic` function of 
    the same module.

    Args:
        institute (str): The Intitute name.
        org_tup (tup): The tuple of the organization structure \
        of the Institute.
    Returns:
        (dict): To be used for setting the final column names of the \
        dataframes built for OTPs attribution by the user.
    """
    # Setting institute parameters
    dpt_col_names = org_tup[0]

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    all_col_rename_dic = col_rename_tup[2]

    otp_col_dic_init = {'hash_id'           : pg.COL_HASH['hash_id'],
                        'pub_id'            : bp.COL_NAMES['pub_id'],
                        'corpus_year'       : pg.COL_NAMES_BONUS['corpus_year'],
                        'final_year'        : bp.COL_NAMES['articles'][2],
                        'first_author'      : bp.COL_NAMES['articles'][1],
                        "institute_authors" : pg.COL_NAMES_BONUS['nom prénom liste'],
                        "all_authors"       : pg.COL_NAMES_BONUS['liste auteurs'],
                        'title'             : bp.COL_NAMES['articles'][9],
                        'journal'           : bp.COL_NAMES['articles'][3],
                        'doc_type'          : bp.COL_NAMES['articles'][7],
                        'doi'               : bp.COL_NAMES['articles'][6],
                        'full_ref'          : pg.COL_NAMES_BONUS['liste biblio'],
                        'issn'              : bp.COL_NAMES['articles'][10],
                        'author_id'         : bp.COL_NAMES['auth_inst'][1],
                        'matricul'          : eg.EMPLOYEES_USEFUL_COLS['matricule'],
                        'institute_author'  : pg.COL_NAMES_BONUS['nom prénom'] + institute,
                        'dpt'               : eg.EMPLOYEES_USEFUL_COLS['dpt'],
                        'serv'              : eg.EMPLOYEES_USEFUL_COLS['serv'],
                        'lab'               : eg.EMPLOYEES_USEFUL_COLS['lab'],
                       }
    otp_col_list = [all_col_rename_dic[name] for _, name in otp_col_dic_init.items()]
    otp_col_dic = dict(zip(otp_col_dic_init.keys(), otp_col_list))
    for _,dpt_col_name in dpt_col_names.items():
        otp_col_dic[dpt_col_name] = dpt_col_names[dpt_col_name]
    otp_col_dic['otp_list'] = pg.COL_NAMES_BONUS['list OTP']

    return otp_col_dic


def set_final_col_names(institute, org_tup):
    """Sets the dict for setting the final column names to be used for building 
    the final publications-list dataframe.

    This is done through the `build_col_conversion_dic` function 
    of the same module.

    Args:
        institute (str): The Intitute name.
        org_tup (tup): The tuple of the organization structure \
        of the Institute.
    Returns:
        (tup): (dict to be used for setting the final \
        column names of the final publications-list dataframe, \
        list of the final column names of the departments).
    """
    # Setting institute parameters
    dpt_col_names = org_tup[0]

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    all_col_rename_dic = col_rename_tup[2]

    final_col_dic_init = {'hash_id'           : pg.COL_HASH['hash_id'],
                          'pub_id'            : bp.COL_NAMES['pub_id'],
                          'corpus_year'       : pg.COL_NAMES_BONUS['corpus_year'],
                          'final_year'        : bp.COL_NAMES['articles'][2],
                          'first_author'      : bp.COL_NAMES['articles'][1],
                          'institute_authors' : pg.COL_NAMES_BONUS['nom prénom liste'],
                          "all_authors"       : pg.COL_NAMES_BONUS['liste auteurs'],
                          'title'             : bp.COL_NAMES['articles'][9],
                          'journal'           : bp.COL_NAMES['articles'][3],
                          'doc_type'          : bp.COL_NAMES['articles'][7],
                          'doi'               : bp.COL_NAMES['articles'][6],
                          'full_ref'          : pg.COL_NAMES_BONUS['liste biblio'],
                          'issn'              : bp.COL_NAMES['articles'][10],
                         }

    final_col_list = [all_col_rename_dic[name] for _, name in final_col_dic_init.items()]
    final_col_dic = dict(zip(final_col_dic_init.keys(), final_col_list))
    for _,dpt_col_name in dpt_col_names.items():
        final_col_dic[dpt_col_name] = dpt_col_names[dpt_col_name]
    final_col_dic['otp'] = pg.COL_NAMES_BONUS['list OTP']

    # Setting the final dept column names in case of getting changed
    # in this function from initial 'dpt_col_names' list
    final_depts_col_list = [final_col_dic[dpt_col_name]
                            for dpt_col_name in dpt_col_names]

    return final_col_dic, final_depts_col_list


def set_if_col_names(institute, org_tup):
    """Sets the dict for setting the final column names, including 
    columns specific to impact-factors, to be used for updating the 
    final publications-list dataframe with impact factors values.

    This is done through the `set_final_col_names` function of 
    the same module.

    Args:
        institute (str): The Intitute name.
        org_tup (tup): The tuple of the organization structure \
        of the Institute.
    Returns:
        (dict): To to be used for updating the final publications-list \
        dataframe with impact factors values.
    """

    if_maj_col_dic, _ = set_final_col_names(institute, org_tup)
    if_maj_col_dic['current_if']  = pg.COL_NAMES_BONUS['IF en cours']
    if_maj_col_dic['pub_year_if'] = pg.COL_NAMES_BONUS['IF année publi']

    return if_maj_col_dic


def set_col_attr(institute, org_tup, columns_list):
    """Sets the dict for setting the final column attributes 
    in terms of width and alignment to be used for formating 
    dataframes before openpyxl save.

    The final column names are got through the 
    `build_col_conversion_dic` internal function.

    Args:
        institute (str): The Institute name.
        org_tup (tup): The tuple of the organization structure \
        of the Institute.
        columns_list (): The full list of column names (str) \
        to be used as keys in the dict to be returned.
    Returns:
        (tup): (dict to be used for setting the final column \
        attributes for formating dataframes before openpyxl save, \
        list of the final column names that have attributes).
    """

    # Setting institute parameters
    col_names_dpt = org_tup[0]

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    all_col_rename_dic = col_rename_tup[2]

    init_col_attr   = {pg.COL_HASH['hash_id']                 : [25, "center"],
                       bp.COL_NAMES['pub_id']                 : [20, "center"],
                       pg.COL_NAMES_BONUS['nom prénom liste'] : [40, "left"],
                       pg.COL_NAMES_BONUS['liste auteurs']    : [40, "left"],
                       bp.COL_NAMES['authors'][1]             : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['matricule']  : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['name']       : [20, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['first_name'] : [20, "center"],
                       bp.COL_NAMES['articles'][9]            : [40, "left"],
                       bp.COL_NAMES['articles'][1]            : [20, "center"],
                       pg.COL_NAMES_BONUS['IF en cours']      : [15, "center"],
                       pg.COL_NAMES_BONUS['IF année publi']   : [15, "center"],
                       bp.COL_NAMES['articles'][6]            : [20, "left"],
                       bp.COL_NAMES['articles'][10]           : [15, "center"],
                       bp.COL_NAMES['articles'][2]            : [15, "center"],
                       bp.COL_NAMES['articles'][3]            : [40, "left"],
                       bp.COL_NAMES['articles'][7]            : [20, "center"],
                       pg.COL_NAMES_BONUS['corpus_year']      : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['dpt']        : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['serv']       : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['lab']        : [15, "center"],
                       pg.COL_NAMES_BONUS['liste biblio']     : [55, 'left'],
                       pg.COL_NAMES_BONUS['homonym']          : [20, "center"],
                       pg.COL_NAMES_BONUS['list OTP']         : [75, "center"],
                      }
    for _,dpt_col_name in col_names_dpt.items():
        init_col_attr[col_names_dpt[dpt_col_name]] = [10, "center"]

    set_col_list = [all_col_rename_dic[key] for key in list(init_col_attr.keys())]
    col_attr_list = list(init_col_attr.values())
    final_col_attr_dict = dict(zip(set_col_list, col_attr_list))

    # Managing not-yet set columns
    for col in columns_list:
        if col in set_col_list:
            continue
        final_col_attr_dict[col] = [15, "center"]

    return final_col_attr_dict
