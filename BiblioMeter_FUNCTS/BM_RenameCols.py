__all__ = ['set_homonym_col_names',
           'set_otp_col_names',
           'set_final_col_names',
           'set_if_col_names',
           'set_col_attr',
          ]

def set_homonym_col_names():
    """
    
    """
    # BiblioAnalysis_Utils package globals imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # Local globals imports
    from BiblioMeter_FUNCTS.BM_EmployeesGlobals import EMPLOYEES_USEFUL_COLS
    from BiblioMeter_FUNCTS.BM_PubGlobals import BM_COL_RENAME_DIC
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BONUS   

    col_homonyms_dic = {0 : COL_NAMES['pub_id'],
                        1 : COL_NAMES_BONUS['corpus_year'],
                        2 : COL_NAMES['articles'][2],
                        3 : COL_NAMES['articles'][1],
                        4 : COL_NAMES['articles'][9],
                        5 : COL_NAMES['articles'][3],
                        6 : COL_NAMES['articles'][7],
                        7 : COL_NAMES['articles'][6],
                        8 : COL_NAMES_BONUS['liste biblio'],
                        9 : COL_NAMES['articles'][10],
                        10: COL_NAMES['auth_inst'][1],	
                        11: EMPLOYEES_USEFUL_COLS['matricule'],	
                        12: EMPLOYEES_USEFUL_COLS['name'],
                        13: EMPLOYEES_USEFUL_COLS['first_name'],	
                        14: COL_NAMES_BONUS['author_type'],	
                        15: EMPLOYEES_USEFUL_COLS['dpt'],
                        16: EMPLOYEES_USEFUL_COLS['serv'],
                        17: EMPLOYEES_USEFUL_COLS['lab'],	
                        18: COL_NAMES_BONUS['homonym'],    	
                        }

    col_homonyms = [BM_COL_RENAME_DIC[col_homonyms_dic[idx]] for idx in col_homonyms_dic.keys()]
    return col_homonyms


def set_otp_col_names():
    '''
    '''
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # local globals imports
    from BiblioMeter_FUNCTS.BM_EmployeesGlobals import EMPLOYEES_USEFUL_COLS
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_DPT
    from BiblioMeter_FUNCTS.BM_PubGlobals import BM_COL_RENAME_DIC
    
    # Setting useful column names
    col_otp_dic = {0  : COL_NAMES['pub_id'],
                   1  : COL_NAMES_BONUS['corpus_year'],
                   2  : COL_NAMES['articles'][2],
                   3  : COL_NAMES['articles'][1],
                   4  : COL_NAMES_BONUS['nom prénom liste'],
                   5  : COL_NAMES['articles'][9],
                   6  : COL_NAMES['articles'][3],
                   7  : COL_NAMES['articles'][7],
                   8  : COL_NAMES['articles'][6],
                   9  : COL_NAMES_BONUS['liste biblio'],
                   10 : COL_NAMES['articles'][10],
                   11 : EMPLOYEES_USEFUL_COLS['matricule'],
                   12 : COL_NAMES_BONUS['nom prénom'],
                   13 : EMPLOYEES_USEFUL_COLS['dpt'],
                   14 : EMPLOYEES_USEFUL_COLS['serv'],
                   15 : EMPLOYEES_USEFUL_COLS['lab'],
                   16 : COL_NAMES_DPT['DTNM'],
                   17 : COL_NAMES_DPT['DTCH'],
                   18 : COL_NAMES_DPT['DEHT'],
                   19 : COL_NAMES_DPT['DTS'],
                   20 : COL_NAMES_DPT['DIR'],
                   21 : COL_NAMES_BONUS['list OTP'],
                  }

    col_otp = [BM_COL_RENAME_DIC[col_otp_dic[idx]] for idx in col_otp_dic.keys()]
    return col_otp


def set_final_col_names():
    '''
    '''
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # local globals imports
    from BiblioMeter_FUNCTS.BM_PubGlobals import BM_COL_RENAME_DIC
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_DPT    
    
    col_final_dic = {0  : COL_NAMES['pub_id'],
                     1  : COL_NAMES_BONUS['corpus_year'],
                     2  : COL_NAMES['articles'][2],
                     3  : COL_NAMES['articles'][1],
                     4  : COL_NAMES_BONUS['nom prénom liste'],
                     5  : COL_NAMES['articles'][9],
                     6  : COL_NAMES['articles'][3],
                     7  : COL_NAMES['articles'][7],
                     8  : COL_NAMES['articles'][6],
                     9  : COL_NAMES_BONUS['liste biblio'],
                     10 : COL_NAMES['articles'][10],
                     11 : COL_NAMES_DPT['DTNM'],
                     12 : COL_NAMES_DPT['DTCH'],
                     13 : COL_NAMES_DPT['DEHT'],
                     14 : COL_NAMES_DPT['DTS'],
                     15 : COL_NAMES_DPT['DIR'],
                     16 : COL_NAMES_BONUS['list OTP'],
                     }
    
    col_final = [BM_COL_RENAME_DIC[col_final_dic[idx]] for idx in col_final_dic.keys()]
    
    return col_final

def set_if_col_names():
    '''
    
    Note:
        The function 'set_final_col_names' is used from 'BM_RenameCols' module
        of the 'BiblioMeter_Functs' package.
    '''
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # local globals imports
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_DPT
    from BiblioMeter_FUNCTS.BM_PubGlobals import BM_COL_RENAME_DIC
    
    col_base_if = set_final_col_names()
    
    col_spec_if = [COL_NAMES_BONUS['IF en cours'],                 
                   COL_NAMES_BONUS['IF année publi'], 
                  ]
    
    col_maj_if = col_base_if + col_spec_if
    
    return (col_base_if, col_maj_if)


def set_col_attr():
    '''
    '''
    # BiblioAnalysis_Utils package imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES

    # local globals imports
    from BiblioMeter_FUNCTS.BM_EmployeesGlobals import EMPLOYEES_USEFUL_COLS
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_BONUS
    from BiblioMeter_FUNCTS.BM_PubGlobals import BM_COL_RENAME_DIC
    from BiblioMeter_FUNCTS.BM_PubGlobals import COL_NAMES_DPT
    
    init_col_attr   = {COL_NAMES['pub_id']                 : [15, "center"],
                       COL_NAMES_BONUS['nom prénom liste'] : [40, "left"],
                       COL_NAMES['authors'][1]             : [15, "center"],
                       EMPLOYEES_USEFUL_COLS['matricule']  : [15, "center"],
                       EMPLOYEES_USEFUL_COLS['name']       : [20, "center"],
                       EMPLOYEES_USEFUL_COLS['first_name'] : [20, "center"],
                       COL_NAMES['articles'][9]            : [40, "left"],
                       COL_NAMES['articles'][1]            : [20, "center"],
                       COL_NAMES_BONUS['IF en cours']      : [15, "center"],
                       COL_NAMES_BONUS['IF année publi']   : [15, "center"],
                       COL_NAMES['articles'][6]            : [20, "left"],
                       COL_NAMES['articles'][10]           : [15, "center"],
                       COL_NAMES['articles'][2]            : [15, "center"],
                       COL_NAMES['articles'][3]            : [40, "left"],
                       COL_NAMES['articles'][7]            : [20, "center"],
                       COL_NAMES_BONUS['corpus_year']      : [15, "center"],
                       EMPLOYEES_USEFUL_COLS['dpt']        : [15, "center"],
                       EMPLOYEES_USEFUL_COLS['serv']       : [15, "center"],
                       EMPLOYEES_USEFUL_COLS['lab']        : [15, "center"],
                       COL_NAMES_BONUS['liste biblio']     : [55, 'left'],
                       COL_NAMES_BONUS['homonym']          : [20, "center"], 
                       COL_NAMES_BONUS['list OTP']         : [75, "center"],
                       COL_NAMES_DPT['DTNM']               : [10, "center"],
                       COL_NAMES_DPT['DTCH']               : [10, "center"],
                       COL_NAMES_DPT['DEHT']               : [10, "center"],
                       COL_NAMES_DPT['DTS']                : [10, "center"],
                       COL_NAMES_DPT['DIR']                : [10, "center"],                       
                      }
    
    final_col_list = [BM_COL_RENAME_DIC[key] for key in list(init_col_attr.keys())]
    col_attr_list = list(init_col_attr.values())
    
    final_col_attr = dict(zip(final_col_list,col_attr_list))
    final_col_attr['else'] = [15, "center"]
    return (final_col_attr, final_col_list)