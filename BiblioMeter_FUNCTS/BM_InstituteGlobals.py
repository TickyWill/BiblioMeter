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


# Setting institute name
#INSTITUTE = "Liten"
INSTITUTE = "Leti"

print("Institute:", INSTITUTE)

# Institute organization # 
DPT_LABEL_KEY = 'dpt_label'
DPT_OTP_KEY   = 'dpt_otp'
INVALIDE      = 'Invalide'

def _set_inst_org(institute, dpt_label_key, dpt_otp_key):
    # Standard library imports
    import ast
    import json
    from pathlib import Path
    
    if institute == 'Liten':
        config_json_file_name = 'LitenOrg_config.json'
    elif institute == 'Leti':
        config_json_file_name = 'LetiOrg_config.json'
    else:
        print("Institute should be 'Liten' or 'Leti'.")
    
    # Reads the Institute json_file_name config file
    config_file_path = Path(__file__).parent / Path('ConfigFiles') / Path(config_json_file_name)

    with open(config_file_path) as file:
        inst_org_dict = json.load(file)    
        
    root_path           = inst_org_dict["ROOT_PATH"]
    col_names_dpt       = inst_org_dict["COL_NAMES_DPT"]
    dpt_label_dict      = inst_org_dict["DPT_LABEL_DICT"]
    dpt_otp_dict        = inst_org_dict["DPT_OTP_DICT"]
    dpt_attributs_dict  = {}
    for dpt in list(col_names_dpt.keys())[:-1]:
        dpt_attributs_dict[dpt] = {}
        dpt_attributs_dict[dpt][dpt_label_key] = dpt_label_dict[dpt]
        dpt_attributs_dict[dpt][dpt_otp_key]   = dpt_otp_dict[dpt]    
        
    inst_filter_list    = inst_org_dict["INST_FILTER_LIST"]
    institute_inst_list = inst_org_dict["INSTITUTE_INST_LIST"]
    inst_if_status      = inst_org_dict["INST_IF_STATUS"]
    
    return_tup = (root_path, col_names_dpt, dpt_label_dict, dpt_attributs_dict, 
                  inst_filter_list, institute_inst_list, inst_if_status) 
    return return_tup

org_tup = _set_inst_org(INSTITUTE, DPT_LABEL_KEY, DPT_OTP_KEY)
ROOT_PATH           = org_tup[0]
COL_NAMES_DPT       = org_tup[1]
DPT_LABEL_DICT      = org_tup[2]
DPT_ATTRIBUTS_DICT  = org_tup[3]
INST_FILTER_LIST    = [tuple(x) for x in org_tup[4]]
INSTITUTE_INST_LIST = [tuple(x) for x in org_tup[5]]
INST_IF_STATUS      = org_tup[6]

DPT_ATTRIBUTS_DICT['DIR'] = {DPT_LABEL_KEY: ['(' + INSTITUTE.upper() + ')'],
                             DPT_OTP_KEY  : list(set(sum([DPT_ATTRIBUTS_DICT[dpt_label][DPT_OTP_KEY] 
                                                         for dpt_label in DPT_ATTRIBUTS_DICT.keys()],[]))),}
for dpt in list(COL_NAMES_DPT.keys()): DPT_ATTRIBUTS_DICT[dpt][DPT_OTP_KEY] += [INVALIDE]



