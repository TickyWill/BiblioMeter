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



