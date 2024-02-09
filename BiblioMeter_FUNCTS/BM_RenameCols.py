__all__ = ['set_homonym_col_names',
           'set_otp_col_names',
           'set_final_col_names',
           'set_if_col_names',
           'set_col_attr',
          ]

def set_homonym_col_names():
    """
    
    """
    # 3rd party imports
    import BiblioParsing as bp

    # local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg  

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

    col_homonyms = [pg.BM_COL_RENAME_DIC[col_homonyms_dic[idx]] for idx in col_homonyms_dic.keys()]
    return col_homonyms


def set_otp_col_names():
    '''
    '''
    # 3rd party imports
    import BiblioParsing as bp

    # local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    # Setting useful column names
    col_otp_dic = {0  : bp.COL_NAMES['pub_id'],
                   1  : pg.COL_NAMES_BONUS['corpus_year'],
                   2  : bp.COL_NAMES['articles'][2],
                   3  : bp.COL_NAMES['articles'][1],
                   4  : pg.COL_NAMES_BONUS['nom prénom liste'],
                   5  : bp.COL_NAMES['articles'][9],
                   6  : bp.COL_NAMES['articles'][3],
                   7  : bp.COL_NAMES['articles'][7],
                   8  : bp.COL_NAMES['articles'][6],
                   9  : pg.COL_NAMES_BONUS['liste biblio'],
                   10 : bp.COL_NAMES['articles'][10],
                   11 : eg.EMPLOYEES_USEFUL_COLS['matricule'],
                   12 : pg.COL_NAMES_BONUS['nom prénom'],
                   13 : eg.EMPLOYEES_USEFUL_COLS['dpt'],
                   14 : eg.EMPLOYEES_USEFUL_COLS['serv'],
                   15 : eg.EMPLOYEES_USEFUL_COLS['lab'],
                   16 : ig.COL_NAMES_DPT['DTNM'],
                   17 : ig.COL_NAMES_DPT['DTCH'],
                   18 : ig.COL_NAMES_DPT['DEHT'],
                   19 : ig.COL_NAMES_DPT['DTS'],
                   20 : ig.COL_NAMES_DPT['DIR'],
                   21 : pg.COL_NAMES_BONUS['list OTP'],
                  }

    col_otp = [pg.BM_COL_RENAME_DIC[col_otp_dic[idx]] for idx in col_otp_dic.keys()]
    return col_otp


def set_final_col_names():
    '''
    '''
    # 3rd party imports
    import BiblioParsing as bp

    # Local imports
    import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg 
    
    col_final_dic = {0  : bp.COL_NAMES['pub_id'],
                     1  : pg.COL_NAMES_BONUS['corpus_year'],
                     2  : bp.COL_NAMES['articles'][2],              # 'Year'
                     3  : bp.COL_NAMES['articles'][1],              # 'Authors'
                     4  : pg.COL_NAMES_BONUS['nom prénom liste'],
                     5  : bp.COL_NAMES['articles'][9],              # 'Title'
                     6  : bp.COL_NAMES['articles'][3],              # 'Journal'
                     7  : bp.COL_NAMES['articles'][7],              # 'Document_type'
                     8  : bp.COL_NAMES['articles'][6],              # 'DOI'
                     9  : pg.COL_NAMES_BONUS['liste biblio'],
                     10 : bp.COL_NAMES['articles'][10],             # 'ISSN'
                     11 : ig.COL_NAMES_DPT['DTNM'],
                     12 : ig.COL_NAMES_DPT['DTCH'],
                     13 : ig.COL_NAMES_DPT['DEHT'],
                     14 : ig.COL_NAMES_DPT['DTS'],
                     15 : ig.COL_NAMES_DPT['DIR'],
                     16 : pg.COL_NAMES_BONUS['list OTP'],
                     }
    
    col_final = [pg.BM_COL_RENAME_DIC[col_final_dic[idx]] for idx in col_final_dic.keys()]
    
    return col_final

def set_if_col_names():
    '''
    
    Note:
        The function 'set_final_col_names' is used from 'BM_RenameCols' module
        of the 'BiblioMeter_Functs' package.
    '''
    # local imports
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    col_base_if = set_final_col_names()
    
    col_spec_if = [pg.COL_NAMES_BONUS['IF en cours'],                 
                   pg.COL_NAMES_BONUS['IF année publi'], 
                  ]
    
    col_maj_if = col_base_if + col_spec_if
    
    return (col_base_if, col_maj_if)


def set_col_attr():
    '''
    '''
    # 3rd party imports
    import BiblioParsing as bp

    # local imports
    import BiblioMeter_FUNCTS.BM_EmployeesGlobals as eg
    import BiblioMeter_FUNCTS.BM_InstituteGlobals as ig
    import BiblioMeter_FUNCTS.BM_PubGlobals as pg
    
    init_col_attr   = {bp.COL_NAMES['pub_id']              : [15, "center"],
                       pg.COL_NAMES_BONUS['nom prénom liste'] : [40, "left"],
                       bp.COL_NAMES['authors'][1]          : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['matricule']  : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['name']       : [20, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['first_name'] : [20, "center"],
                       bp.COL_NAMES['articles'][9]         : [40, "left"],
                       bp.COL_NAMES['articles'][1]         : [20, "center"],
                       pg.COL_NAMES_BONUS['IF en cours']      : [15, "center"],
                       pg.COL_NAMES_BONUS['IF année publi']   : [15, "center"],
                       bp.COL_NAMES['articles'][6]         : [20, "left"],
                       bp.COL_NAMES['articles'][10]        : [15, "center"],
                       bp.COL_NAMES['articles'][2]         : [15, "center"],
                       bp.COL_NAMES['articles'][3]         : [40, "left"],
                       bp.COL_NAMES['articles'][7]         : [20, "center"],
                       pg.COL_NAMES_BONUS['corpus_year']      : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['dpt']        : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['serv']       : [15, "center"],
                       eg.EMPLOYEES_USEFUL_COLS['lab']        : [15, "center"],
                       pg.COL_NAMES_BONUS['liste biblio']     : [55, 'left'],
                       pg.COL_NAMES_BONUS['homonym']          : [20, "center"], 
                       pg.COL_NAMES_BONUS['list OTP']         : [75, "center"],
                       ig.COL_NAMES_DPT['DTNM']            : [10, "center"],
                       ig.COL_NAMES_DPT['DTCH']            : [10, "center"],
                       ig.COL_NAMES_DPT['DEHT']            : [10, "center"],
                       ig.COL_NAMES_DPT['DTS']             : [10, "center"],
                       ig.COL_NAMES_DPT['DIR']             : [10, "center"],                       
                      }
    
    final_col_list = [pg.BM_COL_RENAME_DIC[key] for key in list(init_col_attr.keys())]
    col_attr_list = list(init_col_attr.values())
    
    final_col_attr = dict(zip(final_col_list,col_attr_list))
    final_col_attr['else'] = [15, "center"]
    return (final_col_attr, final_col_list)