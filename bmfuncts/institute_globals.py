"""Module setting globals specific to Institutes.

"""

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
FILES_FOLDER = "BiblioMeter_Files"

ROOT_FOLDERS_DICT = {'Liten': ("S:\\130-LITEN\\130.1-Direction\\130.1.2-Direction Scientifique\\"
                                  "130.1.2.2-Infos communes\\BiblioMeter\\Bibliometry"),
                     'Leti' : "S:\\120-LETI\\120.38-BiblioMeter\\Bibliometry",
                    }

WORKING_FOLDERS_DICT = dict(zip(INSTITUTES_LIST, [ROOT_FOLDERS_DICT[inst] + "\\" + FILES_FOLDER 
                                                  for inst in INSTITUTES_LIST]))

CONFIG_JSON_FILES_DICT = {}
for institute in INSTITUTES_LIST:
    CONFIG_JSON_FILES_DICT[institute] = institute + 'Org_config.json'

# Setting organization parameters of all institutes
DPT_LABEL_KEY = 'dpt_label'
DPT_OTP_KEY   = 'dpt_otp'
INVALIDE      = 'Invalide'
