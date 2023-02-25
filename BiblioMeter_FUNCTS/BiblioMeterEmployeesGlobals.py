__all__ = ['BACKUP_ARCHI',                 # <= ARCHI_SECOURS
           'CATEGORIES_DIC',
           'EMPLOYEES_ADD_COLS',
           'EMPLOYEES_ARCHI',              # <= ARCHI_RH
           'EMPLOYEES_COL_TYPES',          # <= COL_TYPES_RH
           'EMPLOYEES_CONVERTERS_DIC',     # <= EFF_CONVERTERS_DIC
           'EMPLOYEES_FULL_COLS',          # <= COL_NAMES_RH
           'EMPLOYEES_USEFUL_COLS',
           'QUALIFICATION_DIC',
           'STATUS_DIC',]

# To Be moved from Globals_GUI.py because specific to employees files and dict keys changed  <= ARCHI_RH
EMPLOYEES_ARCHI = {"root"                        : "Listing RH",
                   "all_years_employees"         : "Effectifs consolidés",
                   "one_year_employees"          : "Effectifs annuels",
                   "employees_file_name"         : "All_effectifs.xlsx",
                   "one_year_employees_filebase" : "_Effectifs.xlsx",
                   "complementary_employees"     : "Effectifs additionnels",}

BACKUP_ARCHI = {"root" : "Sauvegarde de secours"}  


# Moved from BiblioMeterGlobalsVariables.py because specific to employees files      <= COL_NAMES_RH 
# This is only the full list of employees file columns available to be add to EMPLOYEES_USEFUL_COLS global
EMPLOYEES_FULL_COLS = {'matricule'           : 'Matricule',                       #
                       'name'                : 'Nom',                             #
                       'first_name'          : 'Prénom',                          #
                       'gender'              : 'Sexe(lib)',                       #
                       'nationality'         : 'Nationalité (lib)',               #
                       'category'            : 'Catégorie de salarié (lib)',      #
                       'status'              : 'Statut de salarié (lib)',         #
                       'ranking_channel'     : 'Filière classement (lib)',
                       'qualification'       : 'Qualification classement (lib)',  #
                       'specility'           : 'Spécialité poste (lib)',
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

EMPLOYEES_USEFUL_COLS ={}
for key in employees_useful_cols_keys_list: EMPLOYEES_USEFUL_COLS[key] = EMPLOYEES_FULL_COLS[key]

# Types dict used when reading all-years employees file
EMPLOYEES_COL_TYPES = {} 
for col_name in list(EMPLOYEES_USEFUL_COLS.keys()): EMPLOYEES_COL_TYPES[col_name] = str

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

employees_col_convert_list = [EMPLOYEES_USEFUL_COLS[col_key] for col_key in _employees_col_convert_key]

EMPLOYEES_CONVERTERS_DIC = {}    # <= EFF_CONVERTERS_DIC
for col_convert in employees_col_convert_list: 
    EMPLOYEES_CONVERTERS_DIC[col_convert] = lambda x: _get_str_date(str(x))


# The name of the 6 columns added by the function  _build_year_month_dpt
EMPLOYEES_ADD_COLS = {'dpts_list'          : 'Dpts',
                      'servs_list'         : 'Servs',
                      'months_list'        : 'Months',
                      'years_list'         : 'Years',
                      'first_name_initials': 'Firstname_initials',
                      'employee_full_name' : 'Employee_full_name',
                     }

CATEGORIES_DIC   = {'CDI'      : ['CDI'],
                    'CDD'      : ['CDD'],
                    'CSc'      : ['Conseiller Scient.'],
                    'Stg'      : ['Stagiaire'],
                   }    

STATUS_DIC       = {'Doc'      : ['Thésard'],
                    'Postdoc'  : ['Post doc'],
                    'CSc'      : ['Conseiller Scient.NR'],
                    'Stg'      : ['Stagiaire'],
                   }

QUALIFICATION_DIC = {'Doc'     : ['THESARD', 'THESE'],
                     'Postdoc' : ['POST-DOC'],
                     'CSc'     : ['CONSEILLER SCIENTIFIQUE'],
                     'Stg'     : ['STAGIAIRE'],
                    }