__all__ = ['CONFIG_JSON_FILES_DICT',
           'DPT_LABEL_KEY',
           'DPT_OTP_KEY',
           'INSTITUTES_LIST',
           'INVALIDE',
          ]


# Setting institute names list
INSTITUTES_LIST = ["Liten", "Leti"]

CONFIG_JSON_FILES_DICT = {}
for institute in INSTITUTES_LIST:
    CONFIG_JSON_FILES_DICT[institute] = institute + 'Org_config.json'

# Institute organization # 
DPT_LABEL_KEY = 'dpt_label'
DPT_OTP_KEY   = 'dpt_otp'
INVALIDE      = 'Invalide'

#def set_inst_org(config_json_file_name, dpt_label_key = None, dpt_otp_key = None):
#    # Standard library imports
#    import ast
#    import json
#    from pathlib import Path
#    
#    # Reads the Institute json_file_name config file
#    config_file_path = Path(__file__).parent / Path('ConfigFiles') / Path(config_json_file_name)
#
#    with open(config_file_path) as file:
#        inst_org_dict = json.load(file)    
#        
#    root_path = inst_org_dict["ROOT_PATH"]
#    
#    if dpt_label_key or dpt_otp_key:
#        col_names_dpt       = inst_org_dict["COL_NAMES_DPT"]
#        dpt_label_dict      = inst_org_dict["DPT_LABEL_DICT"]
#        dpt_otp_dict        = inst_org_dict["DPT_OTP_DICT"]
#        dpt_attributs_dict  = {}
#        for dpt in list(col_names_dpt.keys())[:-1]:
#            dpt_attributs_dict[dpt] = {}
#            dpt_attributs_dict[dpt][dpt_label_key] = dpt_label_dict[dpt]
#            dpt_attributs_dict[dpt][dpt_otp_key]   = dpt_otp_dict[dpt]    
#
#        inst_filter_list    = inst_org_dict["INST_FILTER_LIST"]
#        institute_inst_list = inst_org_dict["INSTITUTE_INST_LIST"]
#        inst_if_status      = inst_org_dict["INST_IF_STATUS"]
#
#        return_tup = (root_path, col_names_dpt, dpt_label_dict, dpt_attributs_dict, 
#                      inst_filter_list, institute_inst_list, inst_if_status)
#    else:
#        return_tup = (root_path)
#    return return_tup



