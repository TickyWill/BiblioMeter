__all__ = ['CONFIG_JSON_FILES_DICT',
           'DPT_LABEL_KEY',
           'DPT_OTP_KEY',
           'INSTITUTES_LIST',
           'INVALIDE',
           'WORKING_FOLDERS_DICT',
          ]


# Setting institute names list
INSTITUTES_LIST = ["Liten", "Leti"]

# Setting default working folder of each institute
WORKING_FOLDERS_DICT = {}
WORKING_FOLDERS_DICT["Liten"]  = "S:\\130-LITEN\\130.1-Direction\\130.1.2-Direction Scientifique\\"
WORKING_FOLDERS_DICT["Liten"] += "130.1.2.2-Infos communes\\BiblioMeter\\BiblioMeter_Files"
WORKING_FOLDERS_DICT["Leti"]   = "S:\\120-LETI\\120.38-BiblioMeter\\"
WORKING_FOLDERS_DICT["Leti"]  += "BiblioMeter_Files"

CONFIG_JSON_FILES_DICT = {}
for institute in INSTITUTES_LIST:
    CONFIG_JSON_FILES_DICT[institute] = institute + 'Org_config.json'

# Setting organization parameters of all institutes
DPT_LABEL_KEY = 'dpt_label'
DPT_OTP_KEY   = 'dpt_otp'
INVALIDE      = 'Invalide'



