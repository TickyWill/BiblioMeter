__all__ = ['COL_NAMES_DPT',
           'DPT_ATTRIBUTS_DICT',
           'DPT_LABEL_DICT',
           'DPT_LABEL_KEY',
           'DPT_OTP_KEY',
           'INST_FILTER_LIST',
           'INSTITUTE',
           'INST_IF_STATUS',
           'INSTITUTE_INST_LIST',
           'INVALIDE',
           'ROOT_PATH',
          ]



# Setting the default value for the working directory
ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.2-Infos communes\BiblioMeter\BiblioMeter_Files"

# Setting institute name
#INSTITUTE = "Liten"
INSTITUTE = "Leti"

# Institute organization # 
DPT_LABEL_KEY = 'dpt_label'
DPT_OTP_KEY   = 'dpt_otp'
INVALIDE      = 'Invalide'

if INSTITUTE == "Liten":
    
    # Setting the default value for the working directory
    ROOT_PATH = r"S:\130-LITEN\130.1-Direction\130.1.2-Direction Scientifique\130.1.2.2-Infos communes\BiblioMeter\BiblioMeter_Files"
    
    COL_NAMES_DPT = {'DEHT': 'DEHT',
                     'DTCH': 'DTCH',
                     'DTNM': 'DTNM',
                     'DTS' : 'DTS',
                     'DIR' : 'DIR',
                    }


    DPT_LABEL_DICT = {'DEHT': ['DEHT'],
                      'DTCH': ['DTCH', 'DTBH'],
                      'DTNM': ['DTNM'],
                      'DTS' : ['DTS'],
                      'DIR' : ['(' + INSTITUTE.upper() + ')']
                     }

    DPT_ATTRIBUTS_DICT = {'DEHT': {DPT_LABEL_KEY: DPT_LABEL_DICT['DEHT'],
                                   DPT_OTP_KEY  : ['MSBAT', 'INDIB', 'COBH2', 'STSH2', 
                                                   'EMEPE', 'SYS2E','SYSIE', 'TEENV',
                                                   INVALIDE],
                                  },
                          'DTCH': {DPT_LABEL_KEY: DPT_LABEL_DICT['DTCH'],
                                   DPT_OTP_KEY  : ['PROH2', 'STSH2', 'ASMAT', 'SECSY', 
                                                   'INREL', 'MATEP', 'ESQVE', 'MATNA', 
                                                   'TECNA', 'IDNES', 'COTHE', 'SYS2E', 
                                                   'SYSIE', 'CHECC', INVALIDE],
                                  },
                          'DTNM': {DPT_LABEL_KEY: DPT_LABEL_DICT['DTNM'],
                                   DPT_OTP_KEY  : ['PROH2', 'COTHE', 'ASMAT', 'FAB3D', 
                                                   'INDIB', 'STSH2', 'INNAN', 'TEENV', 
                                                   'CHECC', 'NRBCT', 'ELORG', INVALIDE],
                                  },
                          'DTS' : {DPT_LABEL_KEY: DPT_LABEL_DICT['DTS'],
                                   DPT_OTP_KEY  : ['MACPV', 'HETPV', 'MSYPV', 'TEENV', 
                                                   'MSBAT', 'EMEPE', 'SYS2E', 'SYSIE', INVALIDE],
                                  },
                         }

    DPT_ATTRIBUTS_DICT['DIR'] = {DPT_LABEL_KEY: ['(' + INSTITUTE.upper() + ')'],
                                 DPT_OTP_KEY  : list(set(sum([DPT_ATTRIBUTS_DICT[dpt_label][DPT_OTP_KEY] 
                                                              for dpt_label in DPT_ATTRIBUTS_DICT.keys()],[]))),
                                }  

    INST_FILTER_LIST = [(INSTITUTE.upper(),'France'),('INES','France')]

    INSTITUTE_INST_LIST = [('INES',  'France'), 
                           (INSTITUTE.upper(), 'France'),
                          ]
    INST_IF_STATUS = True
    
    
elif INSTITUTE == "Leti":
        
    # Setting the default value for the working directory
    ROOT_PATH = r"C:\Users\AC265100\Documents\BiblioMeter_App\LETI\BiblioMeter_Files"
    
    COL_NAMES_DPT = {'DCOS': 'DCOS',
                     'DOPT': 'DOPT',
                     'DSYS': 'DSYS',
                     'DTBS': 'DTBS',
                     'DPFT': 'DPFT',
                     'DIR' : 'DIR',
                    }
    
    DPT_LABEL_DICT = {'DCOS': ['DCOS'],
                      'DOPT': ['DOPT'],
                      'DPFT': ['DPFT', 'DTSI'],
                      'DSYS': ['DSYS'],
                      'DTBS': ['DTBS'],
                      'DIR' : ['(' + INSTITUTE.upper() + ')']
                     }

    DPT_ATTRIBUTS_DICT = {'DCOS': {DPT_LABEL_KEY: DPT_LABEL_DICT['DCOS'],
                                   DPT_OTP_KEY  : ['aaaa', 'bbbb', 'cccc', 'dddd', 
                                                   'eeee', 'ffff', 'gggg', 'hhhh',
                                                   INVALIDE],
                                  },
                          'DOPT': {DPT_LABEL_KEY: DPT_LABEL_DICT['DOPT'],
                                   DPT_OTP_KEY  : ['aaaa', 'bbbb', 'cccc', 'dddd', 
                                                   'eeee', 'ffff', 'gggg', 'hhhh',
                                                   INVALIDE],
                                  },
                          'DPFT': {DPT_LABEL_KEY: DPT_LABEL_DICT['DPFT'],
                                   DPT_OTP_KEY  : ['aaaa', 'bbbb', 'cccc', 'dddd', 
                                                   'eeee', 'ffff', 'gggg', 'hhhh',
                                                   INVALIDE],
                                  },
                          'DSYS': {DPT_LABEL_KEY: DPT_LABEL_DICT['DSYS'],
                                   DPT_OTP_KEY  : ['aaaa', 'bbbb', 'cccc', 'dddd', 
                                                   'eeee', 'ffff', 'gggg', 'hhhh',
                                                   INVALIDE],
                                  },
                          'DTBS': {DPT_LABEL_KEY: DPT_LABEL_DICT['DTBS'],
                                   DPT_OTP_KEY  : ['aaaa', 'bbbb', 'cccc', 'dddd', 
                                                   'eeee', 'ffff', 'gggg', 'hhhh',
                                                   INVALIDE],
                                  },
                         }

    DPT_ATTRIBUTS_DICT['DIR'] = {DPT_LABEL_KEY: ['(' + INSTITUTE.upper() + ')'],
                                 DPT_OTP_KEY  : list(set(sum([DPT_ATTRIBUTS_DICT[dpt_label][DPT_OTP_KEY] 
                                                              for dpt_label in DPT_ATTRIBUTS_DICT.keys()],[]))),
                                }

    INST_FILTER_LIST = [(INSTITUTE.upper(),'France')]

    INSTITUTE_INST_LIST = [(INSTITUTE.upper(), 'France'),
                          ]

    INST_IF_STATUS = False
