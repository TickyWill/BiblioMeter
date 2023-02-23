__all__ = ['COL_NAMES_BONUS', 
           'COL_NAMES_DPT', 
           'COL_CONSOLIDATION', 
           'COL_NAMES_FINALE', 
           'COL_SIZES',
           'FILE_NAMES', 
           'COL_MAJ_IF',
           'LITEN_INST_LIST',
           'FILL_EMPTY_KEY_WORD',
           'NOT_AVAILABLE_IF',
           'DPT_ATTRIBUTS_DICT',
           'ROW_COLORS',
          ]

from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
from BiblioMeter_FUNCTS.BiblioMeterEmployeesGlobals import EMPLOYEES_USEFUL_COLS


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


COL_NAMES_BONUS = {'nom prénom'       : 'Nom Prénom du premier auteur Liten', 
                   'nom prénom liste' : 'Liste des auteurs Liten participant à la publication', 
                   'liste biblio'     : 'Référence bibliographique complète', 
                   'homonym'          : 'HOMONYM',
                   'list OTP'         : "Choix de l'OTP", 
                   'IF en cours'      : "IF de l'année en cours", 
                   'IF année publi'   : "IF de l'année de publication",
                   'IF clarivate'     : 'IF', 
                   'EISSN'            : 'EISSN',
                  }


FILL_EMPTY_KEY_WORD = 'unknown'   # 'unknow'


NOT_AVAILABLE_IF = 'Not available'


FILE_NAMES = {'liste conso'  : 'Liste consolidée', 
              'liste consoS' : 'listes consolidées',
             }


COL_NAMES_FINALE = {'Authors'                   : 'Premier auteur de la publication', 
                    'Document_type'             : 'Type du document', 
                    COL_NAMES_BONUS['list OTP'] : 'OTP',
                   }

COL_NAMES_DPT = {'DTNM': 'DTNM',
                 'DTCH': 'DTCH',
                 'DEHT': 'DEHT',
                 'DTS' : 'DTS',
                 'DIR' : 'DIR',
                }


COL_CONSOLIDATION = [COL_NAMES['pub_id'],                # 'Pub_id', 
                     COL_NAMES['authors'][1],            # 'Idx_Author',
                     EMPLOYEES_USEFUL_COLS['matricule'], # 'Matricule', 
                     EMPLOYEES_USEFUL_COLS['name'],      # 'Nom', 
                     EMPLOYEES_USEFUL_COLS['first_name'],# 'Prénom',                      
                     COL_NAMES['articles'][9],           # 'Title', 
                     COL_NAMES['articles'][1],           # 'Authors',
                     COL_NAMES['articles'][3],           # 'Journal',
                     COL_NAMES_BONUS['IF en cours'],     # 'IF en cours', 
                     COL_NAMES_BONUS['IF année publi'],  # 'IF année de la publi',
                     COL_NAMES['articles'][6],           # 'DOI', 
                     COL_NAMES['articles'][10],          # 'ISSN', 
                     COL_NAMES['articles'][7],           # 'Document_type', 
                     COL_NAMES['articles'][2],           # 'Year',                      
                     EMPLOYEES_USEFUL_COLS['dpt'],       # 'Dpt/DOB  (lib court)',
                     EMPLOYEES_USEFUL_COLS['serv'],      # 'Service (lib court)', 
                     EMPLOYEES_USEFUL_COLS['lab'],       # 'Laboratoire (lib court)',
                     COL_NAMES_BONUS['liste biblio'],
                     COL_NAMES_BONUS['homonym'],
                     ]


COL_OTP = [COL_NAMES['pub_id'],                          # 'Pub_id', 
           EMPLOYEES_USEFUL_COLS['matricule'],           # 'Matricule',            
           COL_NAMES_BONUS['nom prénom'],                # 'Nom prénom',
           EMPLOYEES_USEFUL_COLS['dpt'],                 # 'Dpt/DOB  (lib court)',
           EMPLOYEES_USEFUL_COLS['serv'],                # 'Service (lib court)', 
           EMPLOYEES_USEFUL_COLS['lab'],                 # 'Laboratoire (lib court)',           
           COL_NAMES_BONUS['nom prénom liste'],          # 'Liste des auteurs'
           COL_NAMES_BONUS['liste biblio'], 
           COL_NAMES['articles'][9],                     # 'Title', 
           COL_NAMES['articles'][1],                     # 'Authors',
           COL_NAMES['articles'][3],                     # 'Journal',
           COL_NAMES_BONUS['IF en cours'],               # 'IF en cours', 
           COL_NAMES_BONUS['IF année publi'],            # 'IF année de la publi'
           COL_NAMES['articles'][6],                     # 'DOI', 
           COL_NAMES['articles'][10],                    # 'ISSN', 
           COL_NAMES['articles'][7], 
          #COL_NAMES_FINALE['Document_type'],            # 'Document_type', 
           COL_NAMES['articles'][2],                     # 'Year',           
           COL_NAMES_DPT['DTNM'],
           COL_NAMES_DPT['DTCH'],
           COL_NAMES_DPT['DEHT'],
           COL_NAMES_DPT['DTS'],
           COL_NAMES_DPT['DIR'],
           COL_NAMES_BONUS['list OTP'],
          ]


COL_MAJ_IF = [COL_NAMES['pub_id'],                       # 'Pub_id', 
              EMPLOYEES_USEFUL_COLS['matricule'],        # 'Matricule',               
              COL_NAMES_BONUS['nom prénom'],             # 'Nom prénom',
              EMPLOYEES_USEFUL_COLS['dpt'],              # 'Dpt/DOB (lib court)'
              EMPLOYEES_USEFUL_COLS['serv'],             # 'Service (lib court)', 
              EMPLOYEES_USEFUL_COLS['lab'],              # 'Laboratoire (lib court)',             
              COL_NAMES_BONUS['nom prénom liste'],       # 'Liste des auteurs',
              COL_NAMES_BONUS['liste biblio'],                 
              COL_NAMES['articles'][9],                  # 'Title', 
              COL_NAMES_FINALE['Authors'],               # 'Authors',
              COL_NAMES['articles'][3],                  # 'Journal',
              COL_NAMES_BONUS['IF en cours'],            # 'IF en cours', 
              COL_NAMES_BONUS['IF année publi'],         # 'IF année de la publi',
              COL_NAMES['articles'][6],                  # 'DOI', 
              COL_NAMES['articles'][10],                 # 'ISSN', 
              COL_NAMES_FINALE['Document_type'],         # 'Document_type', 
              COL_NAMES['articles'][2],                  # 'Year',              
              COL_NAMES_DPT['DTNM'],
              COL_NAMES_DPT['DTCH'],
              COL_NAMES_DPT['DEHT'],
              COL_NAMES_DPT['DTS'],
              COL_NAMES_FINALE[COL_NAMES_BONUS['list OTP']], 
             ]

COL_SIZES = {COL_NAMES['pub_id']                 : 15,
             COL_NAMES['authors'][1]             : 15,
             EMPLOYEES_USEFUL_COLS['matricule']  : 15,
             EMPLOYEES_USEFUL_COLS['name']       : 15,
             EMPLOYEES_USEFUL_COLS['first_name'] : 15,
             COL_NAMES['articles'][9]            : 35,
             COL_NAMES['articles'][1]            : 15,
             COL_NAMES_BONUS['IF en cours']      : 21,
             COL_NAMES_BONUS['IF année publi']   : 26,
             COL_NAMES['articles'][6]            : 15,
             COL_NAMES['articles'][10]           : 15,
             COL_NAMES['articles'][2]            : 15,
             EMPLOYEES_USEFUL_COLS['dpt']        : 15,
             EMPLOYEES_USEFUL_COLS['serv']       : 15,
             EMPLOYEES_USEFUL_COLS['lab']        : 15,
             COL_NAMES_BONUS['liste biblio']     : 55,
             COL_NAMES_BONUS['homonym']          : 20, 
             COL_NAMES_BONUS['list OTP']         : 75,
            }


# Colors for row background in EXCEL files
ROW_COLORS = {'odd'      : '0000FFFF',
              'even'     : '00CCFFCC',
              'highlight': '00FFFF00',
             }


LITEN_INST_LIST = [('INES',  'France'), 
                   ('LITEN', 'France'),
                  ]