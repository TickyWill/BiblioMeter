"""Module setting globals specific to employees database management.

"""

__all__ = [
           'CATEGORIES_DIC',
           'EMPLOYEES_ADD_COLS',
           'EMPLOYEES_ARCHI',
           'EMPLOYEES_COL_TYPES',
           'EMPLOYEES_CONVERTERS_DIC',
           'EMPLOYEES_FULL_COLS',
           'EMPLOYEES_USEFUL_COLS',
           'EXT_DOCS_USEFUL_COL_LIST',
           'QUALIFICATION_DIC',
           'STATUS_DIC',
           'SEARCH_DEPTH',
          ]

SEARCH_DEPTH = 10

EMPLOYEES_ARCHI = {"root"                        : "Parametres Institut",
                   "all_years_employees"         : "Effectifs consolidés",
                   "one_year_employees"          : "Effectifs annuels",
                   "employees_file_name"         : "All_effectifs.xlsx",
                   "one_year_employees_filebase" : "_Effectifs.xlsx",
                   "complementary_employees"     : "Effectifs de consolidation",}


# This is only the full list of employees file columns available
# to be add to EMPLOYEES_USEFUL_COLS global
EMPLOYEES_FULL_COLS = {'matricule'           : 'Matricule',                       #
                       'name'                : 'Nom',                             #
                       'first_name'          : 'Prénom',                          #
                       'gender'              : 'Sexe(lib)',                       #
                       'nationality'         : 'Nationalité (lib)',               #
                       'category'            : 'Catégorie de salarié (lib)',      #
                       'status'              : 'Statut de salarié (lib)',         #
                       'ranking_channel'     : 'Filière classement (lib)',
                       'qualification'       : 'Qualification classement (lib)',  #
                       'speciality'          : 'Spécialité poste (lib)',
                       'contract_nature'     : 'Nature de contrat (lib)',
                       'link_annex'          : 'Annexe classement',
                       'ranking_date'        : "Date d'effet classement",
                       'hiring_date'         : 'Date début contrat',              #
                       'last_entry_date'     : 'Date dernière entrée',            #
                       'departure_date'      : 'Date de fin de contrat',          #
                       'dpt'                 : 'Dpt/DOB (lib court)',             #
                       'serv'                : 'Service (lib court)',             #
                       'lab'                 : 'Laboratoire (lib court)',         #
                       'full_affiliation'    : 'Laboratoire (lib long)',          #
                       'budget_item'         : 'N° id du poste budgétaire',
                       'structure_unit'      : 'Unité structurelle',
                       'structure_unit_code' : 'Unité structurelle (code R3)',
                       'expenses_kind'       : 'Nature de dépenses',
                       'activity_ratio'      : 'TA',
                       'activity_percent'    : "Taux d'Activité",
                       'working_time'        : 'Règle de plan de roulement (lib)',
                       'working_time_label'  : 'Regpt PR niveau 1(lib)',
                       'birth_date'          : 'Date de naissance',                #
                       'year'                : 'Année',
                       'age'                 : 'Age',
                       'age_range'           : "Tranche d'age (5 ans)",
                      }



# New globals
employees_useful_cols_keys_list = ['matricule',
                                   'name',
                                   'first_name',
                                   'gender',
                                   'nationality',
                                   'category',
                                   'status',
                                   'qualification',
                                   'hiring_date',
                                   'last_entry_date',
                                   'departure_date',
                                   'dpt',
                                   'serv',
                                   'lab',
                                   'full_affiliation',
                                   'birth_date',
                                   'age_range',]

EMPLOYEES_USEFUL_COLS = {}
for key in employees_useful_cols_keys_list:
    EMPLOYEES_USEFUL_COLS[key] = EMPLOYEES_FULL_COLS[key]

# Types dict used when reading all-years employees file
EMPLOYEES_COL_TYPES = {}
for col_name in list(EMPLOYEES_USEFUL_COLS.keys()):
    EMPLOYEES_COL_TYPES[col_name] = str


# The name of the 6 columns added by the function _build_year_month_dpt
EMPLOYEES_ADD_COLS = {'dpts_list'          : 'Dpts',
                      'servs_list'         : 'Servs',
                      'months_list'        : 'Months',
                      'years_list'         : 'Years',
                      'first_name_initials': 'Firstname_initials',
                      'employee_full_name' : 'Employee_full_name',
                     }


# Column names when reading external phd students list
EXT_DOCS_USEFUL_COL_LIST = [EMPLOYEES_USEFUL_COLS['matricule'],
                            EMPLOYEES_USEFUL_COLS['name'],
                            EMPLOYEES_USEFUL_COLS['first_name'],
                            EMPLOYEES_USEFUL_COLS['gender'],
                            EMPLOYEES_USEFUL_COLS['nationality'],
                            EMPLOYEES_USEFUL_COLS['category'],
                            EMPLOYEES_USEFUL_COLS['status'],
                            EMPLOYEES_USEFUL_COLS['qualification'],
                            EMPLOYEES_USEFUL_COLS['hiring_date'],
                            EMPLOYEES_USEFUL_COLS['last_entry_date'],
                            EMPLOYEES_USEFUL_COLS['departure_date'],
                            EMPLOYEES_USEFUL_COLS['dpt'],
                            EMPLOYEES_USEFUL_COLS['serv'],
                            EMPLOYEES_USEFUL_COLS['lab'],
                            EMPLOYEES_USEFUL_COLS['full_affiliation'],
                            EMPLOYEES_USEFUL_COLS['birth_date'],
                            EMPLOYEES_USEFUL_COLS['age_range'],
                            EMPLOYEES_ADD_COLS['dpts_list'],
                            EMPLOYEES_ADD_COLS['servs_list'],
                            EMPLOYEES_ADD_COLS['months_list'],
                            EMPLOYEES_ADD_COLS['years_list'],
                            EMPLOYEES_ADD_COLS['first_name_initials'] + "_y",
                            EMPLOYEES_ADD_COLS['employee_full_name'],]

# Converters of datetime columns for all-years employees file
def _get_str_date(date_value):
    text_to_remove = '[numpy.datetime64('
    if text_to_remove in date_value:
        start = len(text_to_remove) + 1
    else:
        start = 0
    return date_value[start: start + 10]

_employees_col_convert_key = ['hiring_date',
                              'last_entry_date',
                              'departure_date',
                              'birth_date',
                             ]

employees_col_convert_list = [EMPLOYEES_USEFUL_COLS[col_key]
                              for col_key in _employees_col_convert_key]

EMPLOYEES_CONVERTERS_DIC = {}
for col_convert in employees_col_convert_list:
    EMPLOYEES_CONVERTERS_DIC[col_convert] = lambda x: _get_str_date(str(x))


CATEGORIES_DIC   = {'CDI'      : ['CDI', 'Retraite'],
                    'CDD'      : ['CDD'],
                    'CSc'      : ['Conseiller Scient.'],
                    'Stg'      : ['Stagiaire'],
                    'MaD-Dtch' : ['Mis à disposition', "Détaché hors CEA"],
                    'FIN'      : ["Fin de lien"],
                   }

STATUS_DIC       = {'Doc'      : ['Thésard', 'Doctorant', 'Thèse', 'thèse', 'THESARD'],
                    'Postdoc'  : ['Post doc', 'Post-doctorant'],
                    'CSc'      : ['Conseiller Scient.NR'],
                    'Stg'      : ['Stagiaire', "Apprentis."],
                    'Intrm'    : ['Intérimaire']
                   }

QUALIFICATION_DIC = {'Doc'     : ['THESARD', 'THESE', 'Doc'],
                     'Postdoc' : ['POST-DOC', 'Postdoc'],
                     'CSc'     : ['CONSEILLER SCIENTIFIQUE'],
                     'Stg'     : ['STAGIAIRE', 'Stg', "PROFESSIONNALISATION"],
                     'Coll'    : ['Coll', 'externe']
                    }
