__all__ = ['OTP_LIST',      # To be removed
           'OTP_STRING',    # To be removed
           'COL_NAMES_RH', 
           'COL_NAMES_BONUS', 
           'COL_NAMES_DPT', 
           'COL_CONSOLIDATION', 
           'COL_NAMES_FINALE', 
           'COL_SIZES',
           'COL_TYPES_RH',
           'FILE_NAMES', 
           'COL_MAJ_IF',
           'LITEN_INST_LIST',
           'EFF_CONVERTERS_DIC',
           'FILL_EMPTY_KEY_WORD',
           'NOT_AVAILABLE_IF',
           'DPT_ATTRIBUTS_DICT',
           'ROW_COLORS',
          ]

from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
#from BiblioMeter_GUI.Globals_GUI import COL_NAMES_BM


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

OTP_LIST = {
            'STB'    : ['MSBAT', 'INDIB', 'TEENV'],
            'SAMA'   : ['MSBAT', 'INDIB', 'COBH2', 'STSH2', 
                        'EMEPE', 'SYS2E', 'SYSIE'],
            'STP'    : ['COBH2', 'STSH2', 'TEENV'],
            'STH2'   : ['PROH2'],
            'SCPC'   : ['STSH2', 'ASMAT', 'SECSY', 'INREL', 
                        'MATEP', 'ESQVE', 'MATNA', 'TECNA', 
                        'IDNES'],
            'SSETI'  : ['COTHE', 'SYS2E', 'SYSIE', 'CHECC'],
            'SA3D'   : ['PROH2', 'COTHE', 'ASMAT', 'FAB3D'],
            'STDC'   : ['INDIB', 'PROH2', 'STSH2', 'ASMAT', 
                        'INNAN', 'TEENV', 'CHECC', 'NRBCT'],
            'SCSF'   : ['PROH2', 'ELORG'],
            'SCPV'   : ['MACPV', 'HETPV'],
            'SMSP'   : ['MSYPV', 'TEENV'],
            'SIRE'   : ['MSBAT', 'EMEPE', 'SYS2E', 'SYSIE'],
                
            'DEHT'   : DPT_ATTRIBUTS_DICT['DEHT']['dpt_otp'],   
            'DTBH'   : DPT_ATTRIBUTS_DICT['DTCH']['dpt_otp'],
            'DTCH'   : DPT_ATTRIBUTS_DICT['DTCH']['dpt_otp'],
            'DTNM'   : DPT_ATTRIBUTS_DICT['DTNM']['dpt_otp'],
            'DTS'    : DPT_ATTRIBUTS_DICT['DTS']['dpt_otp'],        
            '(LITEN)': DPT_ATTRIBUTS_DICT['DIR']['dpt_otp'],
    
            'STHB': ['Vieille appellation'],
            'S2CE': ['Vieille appellation'],
            'S3E' : ['Vieille appellation'],
            'SBST': ['Vieille appellation'],
            'SCTR': ['Vieille appellation'],
            'SMCP': ['Vieille appellation'],
            'SBST': ['Vieille appellation'],
            'SMPV': ['Vieille appellation'],
            ''    : ['unknown']
}

OTP_STRING = {
        'STB': "MSBAT, INDIB, TEENV",
        'SAMA': "MSBAT, INDIB, COBH2, STSH2, EMEPE, SYS2E, SYSIE",
        'STP': "COBH2, STSH2, TEENV",

        'STH2': "PROH2",
        'SCPC': "STSH2, ASMAT, SECSY, INREL, MATEP, ESQVE, MATNA, TECNA, IDNES",
        'SSETI': "COTHE, SYS2E, SYSIE, CHECC",

        'SA3D': "PROH2, COTHE, ASMAT, FAB3D",
        'STDC': "INDIB, PROH2, STSH2, ASMAT, INNAN, TEENV, CHECC, NRBCT",
        'SCSF': "PROH2, ELORG",

        'SCPV': "MACPV, HETPV",
        'SMSP': "MSYPV, TEENV",
        'SIRE': "MSBAT, EMEPE, SYS2E, SYSIE",

        'DEHT': "MSBAT, INDIB, COBH2, STSH2, EMEPE, SYS2E, SYSIE, TEENV",
        'DTBH': "PROH2, STSH2, ASMAT, SECSY, INREL, MATEP, ESQVE, MATNA, TECNA, IDNES, COTHE, SYS2E, SYSIE, CHECC",
        'DTCH': "PROH2, STSH2, ASMAT, SECSY, INREL, MATEP, ESQVE, MATNA, TECNA, IDNES, COTHE, SYS2E, SYSIE, CHECC",
        'DTNM': "PROH2, COTHE, ASMAT, FAB3D, INDIB, STSH2, INNAN, TEENV, CHECC, NRBCT, ELORG",
        'DTS' : "MACPV, HETPV, MSYPV, TEENV, MSBAT, EMEPE, SYS2E, SYSIE",
    
        '(LITEN)': "A rajouter",
    
        'STHB': "Vieille appellation",
        'S2CE': "Vieille appellation",
        'S3E' : "Vieille appellation",
        'SBST': "Vieille appellation",
        'SCTR': "Vieille appellation",
        'SMCP': "Vieille appellation",
        'SBST': "Vieille appellation",
        'SMPV': "Vieille appellation",
        '' : 'unknown'
}

COL_NAMES_RH = {'ID'                       : 'Matricule',
                'nom'                      : 'Nom',
                'prénom'                   : 'Prénom',
                'sexe'                     : 'Sexe(lib)',
                'nation'                   : 'Nationalité (lib)',
                'catégorie'                : 'Catégorie de salarié (lib)',
                'statut'                   : 'Statut de salarié (lib)',
                'filière classemet'        : 'Filière classement (lib)',
                'qualification classement' : 'Qualification classement (lib)',
                'spé poste'                : 'Spécialité poste (lib)',
                'nat contrat'              : 'Nature de contrat (lib)',
                'annexe classement'        : 'Annexe classement',
                'date effet classement'    : "Date d'effet classement",
                'date debut contrat'       : 'Date début contrat',
                'date dernière entrée'     : 'Date dernière entrée',
                'date de fin de contrat'   : 'Date de fin de contrat',
                'dpt'                      : 'Dpt/DOB (lib court)',
                'service'                  : 'Service (lib court)',
                'labo'                     : 'Laboratoire (lib court)',
                'affiliation complete'     : 'Laboratoire (lib long)',
                'id poste budgetaire'      : 'N° id du poste budgétaire',
                'unité structure'          : 'Unité structurelle',
                'unité structure R3'       : 'Unité structurelle (code R3)',
                'nat dépenses'             : 'Nature de dépenses',
                'TA'                       : 'TA',
                'taux activité'            : "Taux d'Activité",
                'règle plan roulement'     : 'Règle de plan de roulement (lib)',
                'regpt PR lvl 1'           : 'Regpt PR niveau 1(lib)',
                'date naissance'           : 'Date de naissance',
                'année'                    : 'Année', 
                'Full_name'                : 'Full_name_eff',
               }

# Types dict used when reading 'All_Effectifs' file
COL_TYPES_RH = {}
for col_name in list(COL_NAMES_RH.keys()): COL_TYPES_RH[col_name] = str

# Converters of datetime columns for 'All_Effectifs' file

def _get_str_date(date_value):
    text_to_remove = '[numpy.datetime64('
    if text_to_remove in date_value:
        start = len(text_to_remove) + 1
    else:
        start = 0
    return date_value[start: start + 10]

_col_convert_keys_rh = ['date effet classement',
                        'date debut contrat',
                        'date dernière entrée',
                        'date de fin de contrat',
                        'date naissance',
                       ]

_col_convert_rh_list = [COL_NAMES_RH[col_key] for col_key in _col_convert_keys_rh]

EFF_CONVERTERS_DIC = {}
for col_convert in _col_convert_rh_list: 
    EFF_CONVERTERS_DIC[col_convert] = lambda x: _get_str_date(str(x))


COL_NAMES_BONUS = {'nom prénom'       : 'Nom Prénom du premier auteur Liten', 
                   'nom prénom liste' : 'Liste des auteurs Liten participant à la publication', 
                   'liste biblio'     : 'Référence bibliographique complète', 
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
                     COL_NAMES_RH['ID'],                 # 'Matricule', 
                     COL_NAMES_RH['nom'],                # 'Nom', 
                     COL_NAMES_RH['prénom'],             # 'Prénom',                      
                     COL_NAMES['articles'][9],           # 'Title', 
                     COL_NAMES['articles'][1],           # 'Authors',
                     COL_NAMES['articles'][3],           # 'Journal',
                     COL_NAMES_BONUS['IF en cours'],     # 'IF en cours', 
                     COL_NAMES_BONUS['IF année publi'],  # 'IF année de la publi',
                     COL_NAMES['articles'][6],           # 'DOI', 
                     COL_NAMES['articles'][10],          # 'ISSN', 
                     COL_NAMES['articles'][7],           # 'Document_type', 
                     COL_NAMES['articles'][2],           # 'Year',                      
                     COL_NAMES_RH['dpt'], 
                     COL_NAMES_RH['service'],            # 'Service (lib court)', 
                     COL_NAMES_RH['labo'],               # 'Laboratoire (lib court)',
                     COL_NAMES_BONUS['liste biblio'],
                     'HOMONYM',
                     ]

COL_OTP = [COL_NAMES['pub_id'],                          # 'Pub_id', 
           COL_NAMES_RH['ID'],                           # 'Matricule',            
           COL_NAMES_BONUS['nom prénom'],                # 'Nom prénom',
           COL_NAMES_RH['dpt'], 
           COL_NAMES_RH['service'],                      # 'Service (lib court)', 
           COL_NAMES_RH['labo'],                         # 'Laboratoire (lib court)',           
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
              COL_NAMES_RH['ID'],                        # 'Matricule',               
              COL_NAMES_BONUS['nom prénom'],             # 'Nom prénom',
              COL_NAMES_RH['dpt'], 
              COL_NAMES_RH['service'],                   # 'Service (lib court)', 
              COL_NAMES_RH['labo'],                      # 'Laboratoire (lib court)',             
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

COL_SIZES = {
             'Pub_id'                            : 15,
             'Idx_authors'                       : 15,
             'Matricule'                         : 15,
             'Nom'                               : 15,
             'Prénom'                            : 15,
             'Title'                             : 35,
             'Authors'                           : 15,
             "IF de l'année en cours"            : 21,
             "IF de l'année de publication"      : 26,
             'DOI'                               : 15,
             'ISSN'                              : 15,
             'Year'                              : 15,
             'Dpt/DOB (lib court)'               : 15,
             'Service (lib court)'               : 15,
             'Laboratoire (lib court)'           : 15,
             'Référence bibliographique complète': 55,
             'HOMONYM'                           : 20, 
             "Choix de l'OTP"                    : 75,
            }


# Colors for row background in EXCEL files
ROW_COLORS = {'odd'      : '0000FFFF',
              'even'     : '00CCFFCC',
              'highlight': '00FFFF00',
             }


LITEN_INST_LIST = [('INES',  'France'), 
                   ('LITEN', 'France'),
                  ]