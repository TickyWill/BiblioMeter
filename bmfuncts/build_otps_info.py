"""Module of functions for building a dictionary of OTPs list 
per laboratory of the Institute.
"""
__all__ = ['set_lab_otps',
          ]


# Standard library imports
from pathlib import Path

# 3rd party imports
import BiblioParsing as bp
import pandas as pd

# local imports
import bmfuncts.employees_globals as bm_eg
import bmfuncts.institute_globals as bm_ig


def _try_init_dict(dic, init_key, set_key):
    """Initializes 'dic' dict at key 'init_key' if init_key not an empty 
    string then returns 'init_key', else returns 'set_key'.

    Args:
        dic (dict): the dict to initialize at 'init_key' if 'init_key' \
        is not an empty string.
        init_key (str): the key at which the dict should be initialized.
        set_key (str): the key to be used for the existing dict.
    Returns:
        (tup): (the final key to be used for the dict, the potentially \
        updated dict).
    """
    key = init_key
    if key:
        dic[key] = {}
    else:
        key = set_key
    return key, dic


def _set_sorted_list1(lists):
    """Sets sorted list from list of lists.

    Args:
        lists (list): List of lists to be summed and sorted.
    Returns:
        (list): Sorted list of summed lists.
    """
    init_list = sum(lists, [])
    sorted_list = sorted(list(set(init_list)))
    return sorted_list


def _set_sorted_list2(df, col):
    """Sets sorted list from column of df.

    Args:
        df (dataframe): Dataframe from which the list is built.
        col (str): Name of the column from which the list is built.
    Returns:
        (list): Sorted list of the column values of the dataframe.
    """
    init_lists = [list(df[col])]
    sorted_list =_set_sorted_list1(init_lists)
    return sorted_list


def _set_dir(div):
    """Sets name of division direction.

    Args:
        div (str): Name of the division.
    Returns:
        (str): Name of the division direction.
    """
    div_dir = "(" + div + ")"
    return div_dir


def _set_full(div):
    """Sets new name of division that will be attributed 
    full list of OTPs.

    Args:
        div (str): Name of the division.
    Returns:
        (str): Modified name of the division .
    """
    full_div = _set_dir("full-" + div)
    return full_div


def _add_invalide(new_lab_otps_dict):
    """Adds 'INVALIDE' global, imported from 
    'bmfuncts.institute_globals' module, to OTPs list 
    of values of 'new_lab_otps_dict'.

    Args:
        new_lab_otps_dict (hierarchical dict): Keyed by departments \
        and valued by dicts each one keyed by lab of department 
        and valued OTPs values list.
    Returns:
        (hierarchical dict): with same structure as 'new_lab_otps_dict' \
        but the OTPs values lists are added with 'INVALIDE' global.
    """
    final_lab_otps_dict = {}
    for dept, dept_dict in new_lab_otps_dict.items():
        final_lab_otps_dict[dept] = {}
        for k,v in dept_dict.items():
            final_lab_otps_dict[dept][k] = v + [bm_ig.INVALIDE]
    return final_lab_otps_dict


def _set_final_otps_dict(institute, lab_otps_dict):
    """ Sets the final dict of OTPs specifically for 
    the 'Leti' institute taking care of the effective 
    structure of the Institute.

    In addition, it adds a specific OTP value for tagging 
    publications as invalide through the `_add_invalide` 
    internal function.

    Args:
        institute (str): Institute's name.
        lab_otps_dict (dict): OTPs hierarchical dict \
        keyed by departments and valued by dicts keyed \
        by labs and valued by OTPs lists.
    Returns:
        (dict): Final OTPs hierarchical dict keyed by \
        departments of effective Institute's structure and \
        valued by dicts keyed by labs and valued \
        by OTPs lists.
    """
    # Internal functions
    def _fill_full_div(div1, div2):
        """Sets full list of OTPs of 'div2' division as OTPs of 'div1' division 
        when 'div1' division is not defined in source file of OTPs.
        """
        new_lab_otps_dict[div1] = {}
        full_otps = new_lab_otps_dict[div2][_set_full(div2)]
        new_lab_otps_dict[div1][_set_full(div1)] = full_otps

    # Setting final dict of OTPs
    new_lab_otps_dict = lab_otps_dict
    if institute=="Leti":
        new_lab_otps_dict = {}
        dtis_lab_list = []
        dtis_otps_lists = []
        for dept, dept_v in lab_otps_dict.items():
            if dept in ["CLINATEC", "DTBS"]:
                dtis_lab_list = dtis_lab_list + list(dept_v.keys())
                dtis_otps_lists = dtis_otps_lists + list(dept_v.values())
            else:
                new_lab_otps_dict[dept] = lab_otps_dict[dept]
        new_lab_otps_dict["DTIS"] = dict(zip(dtis_lab_list, dtis_otps_lists))
        new_lab_otps_dict["DTIS"][_set_full("DTIS")] = _set_sorted_list1(dtis_otps_lists)
        _fill_full_div("DACLE", "DSYS")
        _fill_full_div("DEXT", "DCOS")
    final_lab_otps_dict = _add_invalide(new_lab_otps_dict)
    return final_lab_otps_dict


def _set_lab_otps_dict(dept_otps_dict, institute_dir):
    """Set the reorganized dict of OTPs by removing services keys.

    It also builds the final dict of OTPs specifically for the \
    'Leti' institute taking care of the effective structure \
    of the Institute through the `_set_final_otps_dict` \
    internal function.

    Args:
        dept_otps_dict (dict): The OTPs hierarchical dict \
        keyed by departments and valued by dicts keyed by \
        services and valued by dicts keyed by labs and valued \
        by OTPs lists.
        institute_dir (str): The department label to be used for \
        the Institute's direction (ex: for "Leti" Institute, \
        it may be "(LETI)").
    Returns:
        (dict): OTPs hierarchical dict keyed by \
        departments and valued by dicts keyed \
        by labs and valued by OTPs lists.
    """
    # Reorganizing dict of OTPs by removing services keys
    lab_otps_dict = {}
    for dept, dept_v in dept_otps_dict.items():
        dept_lab_list = []
        dept_otps_lists = []
        for _, serv_v in dept_v.items():
            dept_lab_list = dept_lab_list + list(serv_v.keys())
            dept_otps_lists = dept_otps_lists + list(serv_v.values())
        lab_otps_dict[dept] = dict(zip(dept_lab_list, dept_otps_lists))
        full_otps_list = _set_sorted_list1(dept_otps_lists)
        if dept=="DIR":
            lab_otps_dict[dept][_set_full(institute_dir)] = full_otps_list
        else:
            lab_otps_dict[dept][_set_full(dept)] = full_otps_list
    return lab_otps_dict


def _set_otps_dict(dept_otps_dict, dept, serv, lb, otps_list, srv="", dpt=""):
    """Updates of the OTPs data for the given lab of the given service 
    of the given department.

    It uses the `-try_init_dict` internal function to initialize the OTPs data
    at the right key value depending on the status of the optional args.

    Args:
        dept_otps_dict (dict): The hierarchical dict of OTPs data to be updated.
        dept (str): The label of the department.
        serv (str): The label of the service of the department.
        lb (str): The label of the laboratory of the service of the department.
        otps_list (list): The list of OTPs values.
        srv (str): The optional label of the service to be used as key \
        (default: "").
        dpt (str): The optional label of the department to be used as key \
        (default: "").
    Returns:
        (dict): The updated data as a hierarchical dict keyed by the department label \
        and valued by a dict keyed by the service label and valued by a dict keyed \
        by laboratory label and valued by the OTPs list. 
    """
    dpt, dept_otps_dict = _try_init_dict(dept_otps_dict, dpt, dept)
    srv, dept_otps_dict[dpt] = _try_init_dict(dept_otps_dict[dpt], srv, serv)
    dept_otps_dict[dpt][srv][lb] = otps_list
    return dept_otps_dict


def _build_lab_otps_dict(otps_serv_df, otps_serv, otps_dept,
                         build_otps_cols_dic, dept_otps_dict,
                         serv_otps_list, unknown):
    """Updates the OTPs dict for each laboratory of a given service of a given 
    department different from the department direction.

    Args:
        otps_serv_df (dataframe): The OTPs info got from the OTPs database \
        for the given service of the given department.
        otps_serv (str): The service label to be used for OTPs selection.
        otps_dept (str): The department label to be used for OTPs selection.
        build_otps_cols_dic (dict): The dict giving the columns names \
        of the OTPs data.
        dept_otps_dict (dict): The hierarchical dict to be updated.
        serv_otps_list (list): The list of OTPs to be used for the service.
        unknown (str): The string used to represent unknown values.
    Returns:
        (dict): The updated hierarchical dict of OTPs of the department \
        keyed by services and valued by a dict keyed by laboratories and \
        valued by OTPs list.
    """
    # Setting useful col names of the OTPs source file
    otps_otp_col = build_otps_cols_dic['otps_otp_col']
    otps_lab_col = build_otps_cols_dic['otps_lab_col']

    dept_otps_dict[otps_dept][otps_serv] = {}
    labs_list = _set_sorted_list2(otps_serv_df, otps_lab_col)
    if labs_list==[unknown]:
        lab = _set_dir(otps_serv)
        dept_otps_dict = _set_otps_dict(dept_otps_dict, otps_dept,
                                        otps_serv, lab, serv_otps_list,
                                        srv="", dpt="")
    else:
        for otps_lab, otps_lab_df in otps_serv_df.groupby(otps_lab_col):
            lab_otps_list = _set_sorted_list2(otps_lab_df, otps_otp_col)
            if otps_lab==unknown or "DIR" in otps_lab:
                lab = _set_dir(otps_serv)
            else:
                lab = otps_lab
            dept_otps_dict = _set_otps_dict(dept_otps_dict, otps_dept,
                                            otps_serv, lab, lab_otps_list,
                                            srv="", dpt="")
    return dept_otps_dict


def _build_dept_otps_dict(otps_dept, otps_dept_df, build_otps_cols_dic,
                          dept_otps_dict, unknown):
    """Updates the OTPs dict for each lab of each service of a department 
     different from the Institute and different from 'CLINATEC'.

    It uses the `_build_lab_otps_dict` internal function for seek of clarity.

    Args:
        otps_dept (str): The department label to be used for OTPs selection.
        otps_dept_df (dataframe): The OTPs info got from the OTPs database \
        for the given department.
        build_otps_cols_dic (dict): The dict giving the columns names \
        of the OTPs data
        dept_otps_dict (dict): The hierarchical dict to be updated.
        unknown (str): The string used to represent unknown values.
    Returns:
        (dict): The updated hierarchical dict of OTPs of the department \
        keyed by services and valued by a dict keyed by laboratories and \
        valued by OTPs list.
    """
    # Setting useful col names of the OTPs source file
    otps_otp_col = build_otps_cols_dic['otps_otp_col']
    otps_serv_col = build_otps_cols_dic['otps_serv_col']

    dept_otps_dict[otps_dept] = {}
    for otps_serv, otps_serv_df in otps_dept_df.groupby(otps_serv_col):
        serv_otps_list = _set_sorted_list2(otps_serv_df, otps_otp_col)

        if "DIR" in otps_serv:
            serv = _set_dir(otps_dept)
            lab = _set_dir(serv)
            dept_otps_dict = _set_otps_dict(dept_otps_dict, otps_dept,
                                            serv, lab, serv_otps_list,
                                            srv=serv, dpt=otps_dept)
        elif otps_serv==unknown:
            serv = _set_dir(otps_dept)
            lab = _set_dir(serv)
            otps_lists = [dept_otps_dict[otps_dept][serv][lab], serv_otps_list]
            new_serv_otps_list = _set_sorted_list1(otps_lists)
            dept_otps_dict = _set_otps_dict(dept_otps_dict, otps_dept,
                                            serv, lab, new_serv_otps_list,
                                            srv=serv, dpt="")
        else:
            dept_otps_dict = _build_lab_otps_dict(otps_serv_df, otps_serv, otps_dept,
                                                  build_otps_cols_dic, dept_otps_dict,
                                                  serv_otps_list, unknown)
    return dept_otps_dict


def _build_special_depts_labels(otps_data_df, otps_dept_col, institute_dir):
    """Builds a dict keyed by special labels of OTPS departments and 
    valued for each key by a tuple composed of the department label 
    and service label to be used for the OTPs attribution.

    The label 'CLINATEC' is considered as a possible special department 
    label in the OTPs data, and it is attributed the tuple value 
    '("CLINATEC", "SCLIN")'. 
    In addition to the 'institute_dir' label, the labels containing the string 
    'DIR' are considered as special departments labels that are attributed 
    the tuple value '("DIR", institute_dir)'.

    Args:
        otps_data_df (dataframe): The data of OTPS got through \
        the `_read_otps_data` internal function.
        otps_dept_col (str): The name of the column of departments \
        in the data of OTPS.
        institute_dir (str): The label used for the part of the \
        Institute external to all the Institute's departments.
    Returns:
        (dict): The built dict.
    """
    # Setting the list of departments in the OTPs data
    otps_depts_list = list(otps_data_df[otps_dept_col])

    # Setting list of departments with "DIR" in their label
    sub_otps_depts_list = [otps_dept for otps_dept in otps_depts_list if "DIR" in otps_dept]
    dir_nb = len(sub_otps_depts_list)

    # Setting the list of keys and values of the dict to build
    special_otps_depts_keys = ["CLINATEC"] + [institute_dir] + sub_otps_depts_list
    special_otps_depts_values = [("CLINATEC", "SCLIN")] + [("DIR", institute_dir)] * (dir_nb + 1)

    # Building the dict
    special_otps_depts_attr_dic = dict(zip(special_otps_depts_keys, special_otps_depts_values))
    return special_otps_depts_attr_dic


def _set_build_otps_cols(otps_cols):
    """Build a dict setting selected columns names for the process 
    of building OTPs information.

    Args:
        otps_cols (list):  The list of columns names of OTPs data \
        as given by the parameters tuple of Institute's organization.
    Returns:
        (dict): The built dict.
    """
    build_otps_cols_dic = {'otps_dept_col': otps_cols[0],
                           'otps_otp_col' : otps_cols[1],
                           'otps_serv_col': otps_cols[2],
                           'otps_lab_col' : otps_cols[3]
                          }
    return build_otps_cols_dic


def _read_otps_data(org_tup, wf_root_path, unknown_kw):
    """Reads the file of data of OTPs using the parameters 
    of the Institute's organization.

    Args:
        org_tup (tuple): Contains parameters of Institute's organization.
        wf_root_path (path): The full path to the root folder \
        of the working folder where the OTPs data should be available.
        unknown_kw (str): The word for replacing NaN values \
        in the OTPs data.
    Returns:
        (tuple): (The OTPs data (dataframe), The dict giving the columns \
        names of the OTPs data (dict) as built by the `_set_build_otps_cols` \
        internal function).
    """
    # Setting useful Institute's config-parameters for OTPs
    otps_data_file, otps_sheet, otps_header, otps_cols = org_tup[12:16]

    # Building the dict giving the columns names of the OTPs data
    build_otps_cols_dic = _set_build_otps_cols(otps_cols)

    # Setting useful aliases for OTPs source file
    config_root_alias = bm_eg.EMPLOYEES_ARCHI["root"]

    # Setting useful paths for OTPs source file
    config_root_path = wf_root_path / Path(config_root_alias)
    otps_data_path = config_root_path / Path(otps_data_file)

    # Getting the OTPs infos from OTPs source file
    otps_data_df = pd.read_excel(otps_data_path, sheet_name=otps_sheet,
                                 header=otps_header, usecols=otps_cols)
    otps_data_df = otps_data_df.fillna(unknown_kw)

    return otps_data_df, build_otps_cols_dic


def set_lab_otps(set_otp_params_list):
    """Builds the dict that gives the OTPs list to be used for each lab 
    of each department of the Institute.

    First, it gets the OTPs infos from the OTPs source file. \
    Then, it fills an initial OTPs dict with infos provided by \
    the OTPs source file. Then, it reorganizes dict of OTPs 
    by removing services keys through the `_set_lab_otps_dict` \
    internal function. It also builds the final dict of OTPs \
    specifically for the 'Leti' institute taking care of \
    the effective structure of the Institute through the \
    `_set_final_otps_dict` internal function. For seek of code clarity, \
    it uses several other internal functions that are: `_try_init_dict`, \
    `_set_sorted_list1`, `_set_sorted_list2`, `_set_dir`, `_set_full` \
    and `_build_dept_otps_dict`.

    Args:
        set_otp_params_list (list): The list composed of the Institute's name (str), \
        the org_tup that contains parameters of Institute's organization (tup), \
        and of the full path (path) to the root folder of the working folder \
        where the OTPs data should be available.
    Returns:
        (dict): OTPs hierarchical dict keyed by departments \
        and valued by dicts keyed by labs and valued by OTPs lists.
    """
    # Setting params values from set_otp_params_list
    institute, org_tup, wf_path = set_otp_params_list

    # Setting folder of the Institute's parameters
    wf_root_path = wf_path.parent

    # Setting the label used for the part of the Institute
    # external to all the Institute's departments
    institute_dir = _set_dir(institute.upper())

    # Setting useful aliases
    unknown_alias = bp.UNKNOWN

    # Getting the OTPs infos from OTPs source file
    otps_data_df, build_otps_cols_dic = _read_otps_data(org_tup, wf_root_path,
                                                        unknown_alias)

    # Setting useful col names
    otps_dept_col = build_otps_cols_dic['otps_dept_col']
    otps_otp_col = build_otps_cols_dic['otps_otp_col']

    # Setting special departments labels
    special_otps_depts_attr_dic = _build_special_depts_labels(otps_data_df,
                                                              otps_dept_col, institute_dir)

    # Filling initial OTPs dict with infos provided by OTPs source file
    # The dict is a hierarchical dict keyed by department, services and labs
    # They are set from the source file but not from the Institute's configuration file.
    dept_otps_dict = {}
    for otps_dept, otps_dept_df in otps_data_df.groupby(otps_dept_col):
        dept_otps_list = _set_sorted_list2(otps_dept_df, otps_otp_col)

        if not otps_dept in special_otps_depts_attr_dic.keys():
            dept_otps_dict = _build_dept_otps_dict(otps_dept, otps_dept_df,
                                                   build_otps_cols_dic, dept_otps_dict,
                                                   unknown_alias)
        else:
            dept, serv = special_otps_depts_attr_dic[otps_dept]
            lab = _set_dir(serv)
            dept_otps_dict = _set_otps_dict(dept_otps_dict, otps_dept,
                                            serv, lab, dept_otps_list,
                                            srv=serv, dpt=dept)

    # Reorganizing dict of OTPs by removing services keys
    lab_otps_dict = _set_lab_otps_dict(dept_otps_dict, institute_dir)

    # Setting final dict of OTPs
    final_lab_otps_dict = _set_final_otps_dict(institute, lab_otps_dict)
    return final_lab_otps_dict
