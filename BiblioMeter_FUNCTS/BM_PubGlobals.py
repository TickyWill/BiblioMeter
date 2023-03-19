__all__ = ['ARCHI_BACKUP',
           'ARCHI_BDD_MULTI_ANNUELLE',
           'ARCHI_IF',
           'ARCHI_YEAR',
           'BM_COL_RENAME_DIC',
           'COL_NAMES_BM',
           'COL_NAMES_BONUS', 
           'COL_NAMES_DPT',
           'DPT_ATTRIBUTS_DICT',
           'DPT_LABEL_DICT', 
           'FILL_EMPTY_KEY_WORD',
           'HOMONYM_FLAG',
           'LITEN_INST_LIST',
           'NOT_AVAILABLE_IF',
           'ROW_COLORS',
           'SUBMIT_COL_RENAME_DIC',
          ]


ARCHI_BACKUP = {"root" : "Sauvegarde de secours"}


ARCHI_BDD_MULTI_ANNUELLE = {"root"                 : "BDD multi annuelle",
                            "concat file name base": "Concaténation par",}


ARCHI_IF = {"root"    : "Impact Factor",
            "all IF"  : "IF all years.xlsx",
            "missing" : "ISSN_manquants.xlsx"}


ARCHI_YEAR = {"bdd mensuelle"                  : "0 - BDD multi mensuelle", 
              "submit file name"               : "submit.xlsx", 
              "orphan file name"               : "orphan.xlsx",            
              "homonymes folder"               : "1 - Consolidation Homonymes", 
              "homonymes file name base"       : "Fichier Consolidation",            
              "OTP folder"                     : "2 - OTP", 
              "OTP file name base"             : "fichier_ajout_OTP",            
              "pub list folder"                : "3 - Résultats Finaux", 
              "pub list file name base"        : "Liste consolidée",              
              "corpus"                         : "Corpus", 
              "concat"                         : "concatenation", 
              "dedup"                          : "deduplication", 
              "scopus"                         : "scopus", 
              "wos"                            : "wos", 
              "parsing"                        : "parsing", 
              "rawdata"                        : "rawdata",
             }


DPT_LABEL_DICT = {'DEHT': ['DEHT'],
                  'DTCH': ['DTCH', 'DTBH'],
                  'DTNM': ['DTNM'],
                  'DTS' : ['DTS']
                 }


DPT_ATTRIBUTS_DICT = {'DEHT': {'dpt_label': ['DEHT'],
                               'dpt_otp'  : ['MSBAT', 'INDIB', 'COBH2', 'STSH2', 
                                             'EMEPE', 'SYS2E','SYSIE', 'TEENV'],
                              },
                      'DTCH': {'dpt_label': ['DTCH', 'DTBH'],
                               'dpt_otp'  : ['PROH2', 'STSH2', 'ASMAT', 'SECSY', 
                                             'INREL', 'MATEP', 'ESQVE', 'MATNA', 
                                             'TECNA', 'IDNES', 'COTHE', 'SYS2E', 
                                             'SYSIE', 'CHECC'],
                              },
                      'DTNM': {'dpt_label': ['DTNM'],
                               'dpt_otp'  : ['PROH2', 'COTHE', 'ASMAT', 'FAB3D', 
                                             'INDIB', 'STSH2', 'INNAN', 'TEENV', 
                                             'CHECC', 'NRBCT', 'ELORG'],
                              },
                      'DTS' : {'dpt_label': ['DTS'],
                               'dpt_otp'  : ['MACPV', 'HETPV', 'MSYPV', 'TEENV', 
                                             'MSBAT', 'EMEPE', 'SYS2E', 'SYSIE'],
                              },
                     }


DPT_ATTRIBUTS_DICT['DIR'] = {'dpt_label': ['(LITEN)'],
                             'dpt_otp'  : list(set(sum([DPT_ATTRIBUTS_DICT[dpt_label]['dpt_otp'] 
                                                        for dpt_label in DPT_ATTRIBUTS_DICT.keys()],[]))),
                            }


# Colors for row background in EXCEL files
ROW_COLORS = {'odd'      : '0000FFFF',
              'even'     : '00CCFFCC',
              'highlight': '00FFFF00',
             }


# BiblioMeter globals imports
from BiblioMeter_FUNCTS.BM_EmployeesGlobals import EMPLOYEES_ADD_COLS 

LITEN_INST_LIST = [('INES',  'France'), 
                   ('LITEN', 'France'),
                  ]


FILL_EMPTY_KEY_WORD = 'unknown' 


NOT_AVAILABLE_IF    = 'Not available'


HOMONYM_FLAG = "HOMONYM"


COL_NAMES_BONUS = {'nom prénom'       : "Nom, Prénom de l'auteur Liten", 
                   'nom prénom liste' : 'Liste ordonnée des auteurs Liten', 
                   'liste biblio'     : 'Référence bibliographique complète', 
                   'author_type'      : "Type de l'auteur Liten",
                   'homonym'          : 'Homonymes',
                   'list OTP'         : "Choix de l'OTP",
                   'corpus_year'      : 'Année de première publication',
                   'IF en cours'      : "IF en cours", 
                   'IF année publi'   : "IF de l'année de première publication",
                   'IF clarivate'     : 'IF',
                   'EISSN'            : 'EISSN',
                  }


COL_NAMES_DPT = {'DTNM': 'DTNM',
                 'DTCH': 'DTCH',
                 'DEHT': 'DEHT',
                 'DTS' : 'DTS',
                 'DIR' : 'DIR',
                }


COL_NAMES_BM = {'Dpts'      : EMPLOYEES_ADD_COLS['dpts_list'], 
                'Servs'     : EMPLOYEES_ADD_COLS['servs_list'],
                'First_name': EMPLOYEES_ADD_COLS['first_name_initials'],
                'Last_name' : 'Co_author_joined',  # 'Co_author_joined' DOE J --> DOE
                'Full_name' : 'Full_name', # DOE J
                'Homonym'   : COL_NAMES_BONUS['homonym'],
               }


def _build_col_conversion_dic():
    """
    """
    
    # BiblioAnalysis_Utils package globals imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # Local globals imports
    from BiblioMeter_FUNCTS.BM_EmployeesGlobals import EMPLOYEES_ADD_COLS
    from BiblioMeter_FUNCTS.BM_EmployeesGlobals import EMPLOYEES_USEFUL_COLS
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BM
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_DPT
    from BiblioMeter_FUNCTS.BM_PubGlobals import LITEN_INST_LIST

    liten_col_list  = [tup[0] + '_' + tup[1] for tup in LITEN_INST_LIST]

    init_submit_col_list = sum([COL_NAMES['auth_inst'][:5],
                           liten_col_list,
                           [COL_NAMES['authors'][2] ], 
                           COL_NAMES['articles'][1:11],
                           [COL_NAMES_BONUS['corpus_year'], ],
                           [COL_NAMES_BM['Full_name'], COL_NAMES_BM['Last_name'], COL_NAMES_BM['First_name'], ],
                           [COL_NAMES_BONUS['homonym']],
                           list(EMPLOYEES_USEFUL_COLS.values()),
                           list(EMPLOYEES_ADD_COLS.values()),
                           [COL_NAMES_BONUS['author_type'], COL_NAMES_BONUS['liste biblio'], ],
                          ],
                          [],
                         )

    init_bm_col_list = sum([init_submit_col_list,
                           [COL_NAMES_BONUS['nom prénom liste'],
                            COL_NAMES_BONUS['nom prénom'],
                            COL_NAMES_DPT['DTNM'],
                            COL_NAMES_DPT['DTCH'],
                            COL_NAMES_DPT['DEHT'],
                            COL_NAMES_DPT['DTS'],
                            COL_NAMES_DPT['DIR'],
                            COL_NAMES_BONUS['list OTP'],
                            COL_NAMES_BONUS['IF en cours'],
                            COL_NAMES_BONUS['IF année publi'],
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
                             liten_col_list,
                             ["Co_auteur Liten",
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
                             [COL_NAMES_BM['Full_name'],
                              COL_NAMES_BM['Last_name'],
                              COL_NAMES_BM['First_name'],
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
                             list(EMPLOYEES_ADD_COLS.values()),
                             [COL_NAMES_BONUS['author_type'], 
                              COL_NAMES_BONUS['liste biblio'],
                              COL_NAMES_BONUS['nom prénom liste'],
                              COL_NAMES_BONUS['nom prénom'],
                              COL_NAMES_DPT['DTNM'],
                              COL_NAMES_DPT['DTCH'],
                              COL_NAMES_DPT['DEHT'],
                              COL_NAMES_DPT['DTS'],
                              COL_NAMES_DPT['DIR'],
                              COL_NAMES_BONUS['list OTP'],
                              COL_NAMES_BONUS['IF en cours'],
                              COL_NAMES_BONUS['IF année publi'],
                             ]
                            ],
                            [],
                           )
    
    all_col_rename_dic     = dict(zip(init_bm_col_list,final_bm_col_list))
    
    final__submit_col_list = [all_col_rename_dic[col] for col in init_submit_col_list]
    submit_col_rename_dic  = dict(zip(init_submit_col_list,final__submit_col_list))
    
    return (submit_col_rename_dic, all_col_rename_dic)

SUBMIT_COL_RENAME_DIC, BM_COL_RENAME_DIC = _build_col_conversion_dic()


