"""Module setting globals specific to Institutes.

"""

__all__ = ['CONFIG_JSON_FILES_DICT',
           'DPT_LABEL_KEY',
           'DPT_OTP_KEY',
           'EXCLUDE_ADDR_ITEMS_LIST',
           'INSTITUTES_CONTINENT_DICT',
           'INSTITUTES_COUNTRY_DICT',
           'INSTITUTES_LIST',
           'INSTITUTES_NORM_NAME_DICT',
           'INSTITUTES_TOP_AFFIL_DICT',
           'INSTITUTES_TOWN_DICT',
           'INVALIDE',
           'ROOT_FOLDERS_DICT',
           'WORKING_FOLDERS_DICT',
          ]


# Setting institute names list
INSTITUTES_LIST = ["Liten", "Leti"]

# Setting Institutes towns, countries, continents, affiliation normalized names and top affiliation
INSTITUTES_TOWNS_LIST = ['Grenoble', 'Grenoble']
INSTITUTES_COUNTRIES_LIST = ['France', 'France']
INSTITUTES_CONTINENTS_LIST = ['Europe', 'Europe']
INSTITUTES_AFFIL_TYPES_LIST = ['Rto', 'Rto']
INSTITUTES_NORM_NAMES_LIST = [x.upper() + " " + INSTITUTES_AFFIL_TYPES_LIST[idx]
                              for idx, x in enumerate(INSTITUTES_LIST)]
INSTITUTES_TOP_AFFILS_LIST = ['CEA', 'CEA']

INSTITUTES_TOWN_DICT = dict(zip(INSTITUTES_LIST, INSTITUTES_TOWNS_LIST))
INSTITUTES_COUNTRY_DICT = dict(zip(INSTITUTES_LIST, INSTITUTES_COUNTRIES_LIST))
INSTITUTES_CONTINENT_DICT = dict(zip(INSTITUTES_LIST, INSTITUTES_CONTINENTS_LIST))
INSTITUTES_NORM_NAME_DICT = dict(zip(INSTITUTES_LIST, INSTITUTES_NORM_NAMES_LIST))
INSTITUTES_TOP_AFFIL_DICT = dict(zip(INSTITUTES_LIST, INSTITUTES_TOP_AFFILS_LIST))

# Setting list of address items that exlude affiliation correction of added data from HAL database
EXCLUDE_ADDR_ITEMS_LIST = ['LITEN', 'LETI', 'IRIG', 'IBS']

# Setting default working folder of each institute
FILES_FOLDER = "BiblioMeter_Files"
ROOT_FOLDERS_LIST = [("S:\\130-LITEN\\130.1-Direction\\130.1.2-Direction Scientifique\\"
                      "130.1.2.2-Infos communes\\BiblioMeter\\Bibliometry"),
                     "S:\\120-LETI\\120.38-BiblioMeter\\Bibliometry",
                    ]
ROOT_FOLDERS_DICT =  dict(zip(INSTITUTES_LIST, ROOT_FOLDERS_LIST))

WORKING_FOLDERS_DICT = dict(zip(INSTITUTES_LIST, [ROOT_FOLDERS_DICT[inst] + "\\" + FILES_FOLDER
                                                  for inst in INSTITUTES_LIST]))

# Setting file names of institutes' organization description
CONFIG_JSON_FILES_LIST = [x + 'Org_config.json' for x in INSTITUTES_LIST]
CONFIG_JSON_FILES_DICT = dict(zip(INSTITUTES_LIST, CONFIG_JSON_FILES_LIST))

# Setting organization parameters of all institutes
DPT_LABEL_KEY = 'dpt_label'
DPT_OTP_KEY   = 'dpt_otp'
INVALIDE      = 'Invalide'
