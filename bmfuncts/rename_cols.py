__all__ = ['build_col_conversion_dic',
           'set_homonym_col_names',
           'set_otp_col_names',
           'set_final_col_names',
           'set_if_col_names',
           'set_col_attr',
          ]


def build_col_conversion_dic(institute, org_tup):
    """
    """

    # 3rd party imports
    import BiblioParsing as bp

    # Local imports
    import bmfuncts.employees_globals as eg
    import bmfuncts.institute_globals as ig
    import bmfuncts.pub_globals as pg

    # Setting institute parameters
    col_names_dpt  = org_tup[0]
    dpt_label_dict = org_tup[1]
    dpt_col_list   = list(col_names_dpt.values())
    inst_col_list  = org_tup[4]

    init_orphan_col_list = sum([bp.COL_NAMES['auth_inst'][:5],
                                inst_col_list,
                                [bp.COL_NAMES['authors'][2]],
                                bp.COL_NAMES['articles'][1:11],
                                [pg.COL_NAMES_BONUS['corpus_year']],
                                [pg.COL_NAMES_BM['Full_name'],
                                 pg.COL_NAMES_BM['Last_name'],
                                 pg.COL_NAMES_BM['First_name']],
                               ],
                               [],
                              )

    init_submit_col_list = sum([init_orphan_col_list,
                                [pg.COL_NAMES_BONUS['homonym']],
                                list(eg.EMPLOYEES_USEFUL_COLS.values()),
                                list(eg.EMPLOYEES_ADD_COLS.values()),
                                [pg.COL_NAMES_BONUS['author_type'],
                                 pg.COL_NAMES_BONUS['liste biblio']],
                               ],
                               [],
                              )

    init_bm_col_list = sum([init_submit_col_list,
                           [pg.COL_NAMES_BONUS['nom prénom liste'] + institute,
                            pg.COL_NAMES_BONUS['nom prénom'] + institute,
                             ],
                            dpt_col_list,
                           [pg.COL_NAMES_BONUS['list OTP'],
                            pg.COL_NAMES_BONUS['IF en cours'],
                            pg.COL_NAMES_BONUS['IF année publi'],
                           ]
                          ],
                          [],
                         )

    final_bm_col_list = sum([["Pub_id",
                              "Auteur_id",
                              "Adresse",
                              "Pays",
                              "Institutions",
                             ],
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
                             "Année de première publication",
                             ],
                             [pg.COL_NAMES_BM['Full_name'],
                              pg.COL_NAMES_BM['Last_name'],
                              pg.COL_NAMES_BM['First_name'],
                             ],
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
                              "Tranche d'age (5 ans)",
                             ],
                             list(eg.EMPLOYEES_ADD_COLS.values()),
                             [pg.COL_NAMES_BONUS['author_type'],
                              pg.COL_NAMES_BONUS['liste biblio'],
                              pg.COL_NAMES_BONUS['nom prénom liste'] + institute,
                              pg.COL_NAMES_BONUS['nom prénom'] + institute,
                             ],
                              dpt_col_list,
                             [pg.COL_NAMES_BONUS['list OTP'],
                              pg.COL_NAMES_BONUS['IF en cours'],
                              pg.COL_NAMES_BONUS['IF année publi'],
                             ]
                            ],
                            [],
                           )

    all_col_rename_dic     = dict(zip(init_bm_col_list, final_bm_col_list))

    final_submit_col_list  = [all_col_rename_dic[col] for col in init_submit_col_list]
    submit_col_rename_dic  = dict(zip(init_submit_col_list, final_submit_col_list))

    final_orphan_col_list  = [all_col_rename_dic[col] for col in init_orphan_col_list]
    orphan_col_rename_dic  = dict(zip(init_orphan_col_list, final_orphan_col_list))

    return (orphan_col_rename_dic, submit_col_rename_dic, all_col_rename_dic)


def set_homonym_col_names(institute, org_tup):
    """
    """
    # 3rd party imports
    import BiblioParsing as bp

    # local imports
    import bmfuncts.employees_globals as eg
    import bmfuncts.pub_globals as pg
    from bmfuncts.rename_cols import build_col_conversion_dic

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    bm_col_rename_dic = col_rename_tup[2]

    col_homonyms_dic = {0 : bp.COL_NAMES['pub_id'],
                        1 : pg.COL_NAMES_BONUS['corpus_year'],
                        2 : bp.COL_NAMES['articles'][2],
                        3 : bp.COL_NAMES['articles'][1],
                        4 : bp.COL_NAMES['articles'][9],
                        5 : bp.COL_NAMES['articles'][3],
                        6 : bp.COL_NAMES['articles'][7],
                        7 : bp.COL_NAMES['articles'][6],
                        8 : pg.COL_NAMES_BONUS['liste biblio'],
                        9 : bp.COL_NAMES['articles'][10],
                        10: bp.COL_NAMES['auth_inst'][1],
                        11: eg.EMPLOYEES_USEFUL_COLS['matricule'],
                        12: eg.EMPLOYEES_USEFUL_COLS['name'],
                        13: eg.EMPLOYEES_USEFUL_COLS['first_name'],
                        14: pg.COL_NAMES_BONUS['author_type'],
                        15: eg.EMPLOYEES_USEFUL_COLS['dpt'],
                        16: eg.EMPLOYEES_USEFUL_COLS['serv'],
                        17: eg.EMPLOYEES_USEFUL_COLS['lab'],
                        18: pg.COL_NAMES_BONUS['homonym'],
                        }

    col_homonyms = [bm_col_rename_dic[col_homonyms_dic[idx]] for idx in col_homonyms_dic.keys()]
    return col_homonyms


def set_otp_col_names(institute, org_tup):
    '''
    '''
    # 3rd party imports
    import BiblioParsing as bp

    # local imports
    import bmfuncts.employees_globals as eg
    import bmfuncts.institute_globals as ig
    import bmfuncts.pub_globals as pg
    from bmfuncts.rename_cols import build_col_conversion_dic

    # Setting institute parameters
    col_names_dpt = org_tup[0]

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    bm_col_rename_dic = col_rename_tup[2]

    # Setting useful column names
    col_OTP_dic = {0  : bp.COL_NAMES['pub_id'],
                   1  : pg.COL_NAMES_BONUS['corpus_year'],
                   2  : bp.COL_NAMES['articles'][2],
                   3  : bp.COL_NAMES['articles'][1],
                   4  : pg.COL_NAMES_BONUS['nom prénom liste'] + institute,
                   5  : bp.COL_NAMES['articles'][9],
                   6  : bp.COL_NAMES['articles'][3],
                   7  : bp.COL_NAMES['articles'][7],
                   8  : bp.COL_NAMES['articles'][6],
                   9  : pg.COL_NAMES_BONUS['liste biblio'],
                   10 : bp.COL_NAMES['articles'][10],
                   11 : eg.EMPLOYEES_USEFUL_COLS['matricule'],
                   12 : pg.COL_NAMES_BONUS['nom prénom'] + institute,
                   13 : eg.EMPLOYEES_USEFUL_COLS['dpt'],
                   14 : eg.EMPLOYEES_USEFUL_COLS['serv'],
                   15 : eg.EMPLOYEES_USEFUL_COLS['lab'],
                  }
    last_num = len(col_OTP_dic)
    for _,dpt_col_name in col_names_dpt.items():
        col_OTP_dic[last_num] = col_names_dpt[dpt_col_name]
        last_num += 1
    col_OTP_dic[last_num] = pg.COL_NAMES_BONUS['list OTP']

    col_OTP = [bm_col_rename_dic[col_OTP_dic[idx]] for idx in col_OTP_dic.keys()]
    return col_OTP


def set_final_col_names(institute, org_tup):
    '''
    '''
    # 3rd party imports
    import BiblioParsing as bp

    # Local imports
    import bmfuncts.institute_globals as ig
    import bmfuncts.pub_globals as pg
    from bmfuncts.rename_cols import build_col_conversion_dic

    # Setting institute parameters
    col_names_dpt = org_tup[0]

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    bm_col_rename_dic = col_rename_tup[2]

    col_final_dic = {0  : bp.COL_NAMES['pub_id'],
                     1  : pg.COL_NAMES_BONUS['corpus_year'],
                     2  : bp.COL_NAMES['articles'][2],                         # 'Year'
                     3  : bp.COL_NAMES['articles'][1],                         # 'Authors'
                     4  : pg.COL_NAMES_BONUS['nom prénom liste'] + institute,
                     5  : bp.COL_NAMES['articles'][9],                         # 'Title'
                     6  : bp.COL_NAMES['articles'][3],                         # 'Journal'
                     7  : bp.COL_NAMES['articles'][7],                         # 'Document_type'
                     8  : bp.COL_NAMES['articles'][6],                         # 'DOI'
                     9  : pg.COL_NAMES_BONUS['liste biblio'],
                     10 : bp.COL_NAMES['articles'][10],                        # 'ISSN'
                    }
    last_num = len(col_final_dic)
    for _,dpt_col_name in col_names_dpt.items():
        col_final_dic[last_num] = col_names_dpt[dpt_col_name]
        last_num += 1
    col_final_dic[last_num] = pg.COL_NAMES_BONUS['list OTP']

    col_final = [bm_col_rename_dic[col_final_dic[idx]] for idx in col_final_dic.keys()]

    return col_final


def set_if_col_names(institute, org_tup):
    '''

    Note:
        The function 'set_final_col_names' is used from 'rename_cols' module
        of the 'bmfuncts' package.
    '''
    # local imports
    import bmfuncts.pub_globals as pg
    from bmfuncts.rename_cols import set_final_col_names

    col_base_if = set_final_col_names(institute, org_tup)

    col_spec_if = [pg.COL_NAMES_BONUS['IF en cours'],
                   pg.COL_NAMES_BONUS['IF année publi'],
                  ]

    col_maj_if = col_base_if + col_spec_if

    return (col_base_if, col_maj_if)


def set_col_attr(institute, org_tup):
    '''
    '''
    # 3rd party imports
    import BiblioParsing as bp

    # local imports
    import bmfuncts.employees_globals as eg
    import bmfuncts.institute_globals as ig
    import bmfuncts.pub_globals as pg
    from bmfuncts.rename_cols import build_col_conversion_dic

    # Setting institute parameters
    col_names_dpt = org_tup[0]

    #  Setting useful col names
    col_rename_tup = build_col_conversion_dic(institute, org_tup)
    bm_col_rename_dic = col_rename_tup[2]

    init_col_attr   = {bp.COL_NAMES['pub_id']                             : [15, "center"],
                       pg.COL_NAMES_BONUS['nom prénom liste'] + institute : [40, "left"],
                       bp.COL_NAMES['authors'][1]                         : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['matricule']              : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['name']                   : [20, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['first_name']             : [20, "center"],
                       bp.COL_NAMES['articles'][9]                        : [40, "left"],
                       bp.COL_NAMES['articles'][1]                        : [20, "center"],
                       pg.COL_NAMES_BONUS['IF en cours']                  : [15, "center"],
                       pg.COL_NAMES_BONUS['IF année publi']               : [15, "center"],
                       bp.COL_NAMES['articles'][6]                        : [20, "left"],
                       bp.COL_NAMES['articles'][10]                       : [15, "center"],
                       bp.COL_NAMES['articles'][2]                        : [15, "center"],
                       bp.COL_NAMES['articles'][3]                        : [40, "left"],
                       bp.COL_NAMES['articles'][7]                        : [20, "center"],
                       pg.COL_NAMES_BONUS['corpus_year']                  : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['dpt']                    : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['serv']                   : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['lab']                    : [15, "center"],
                       pg.COL_NAMES_BONUS['liste biblio']                 : [55, 'left'],
                       pg.COL_NAMES_BONUS['homonym']                      : [20, "center"],
                       pg.COL_NAMES_BONUS['list OTP']                     : [75, "center"],
                      }
    for _,dpt_col_name in col_names_dpt.items():
        init_col_attr[col_names_dpt[dpt_col_name]] = [10, "center"]

    final_col_list = [bm_col_rename_dic[key] for key in list(init_col_attr.keys())]
    col_attr_list = list(init_col_attr.values())

    final_col_attr = dict(zip(final_col_list,col_attr_list))
    final_col_attr['else'] = [15, "center"]
    return (final_col_attr, final_col_list)