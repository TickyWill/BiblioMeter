__all__ = ['deduplicate_parsing',
           'convert_parsing_keys_to_bm',
           'rawdata_parsing',
           'revers_parsing_keys_to_bp',
          ]

# 3rd party imports
import BiblioParsing as bp

# local imports
import bmfuncts.pub_globals as bm_pg
from bmfuncts.config_utils import set_rawdata_and_parsing_paths
from bmfuncts.correct_parsing import build_and_save_unknown_country_data
from bmfuncts.correct_parsing import correct_parsing
from bmfuncts.save_final_results import save_db_ids_data
from bmfuncts.save_final_results import save_fails_dict
from bmfuncts.save_final_results import save_parsing_dict
from bmfuncts.save_final_results import save_rawdata_correction
from bmfuncts.useful_functs import build_and_save_dedup_db_ids
from bmfuncts.useful_functs import compute_dedup_pub_number
from bmfuncts.useful_functs import print_step_text
from bmfuncts.useful_functs import print_step_title
from bmfuncts.useful_functs import read_parsing_dict


def convert_parsing_keys_to_bm(bp_parsing_dict):
    parsing_dict = {key: bp_parsing_dict[bm_pg.PARSING_KEYS_CONVERT_DIC[key]]
                    for key in bm_pg.PARSING_KEYS_DIC['all']
                    if bm_pg.PARSING_KEYS_CONVERT_DIC[key] in bp_parsing_dict.keys()}
    return parsing_dict


def revers_parsing_keys_to_bp(parsing_dict):
    bp_parsing_dict = {key: parsing_dict[bm_pg.PARSING_KEYS_REVERT_DIC[key]]
                       for key in bp.PARSING_ITEMS_LIST
                       if bm_pg.PARSING_KEYS_REVERT_DIC[key] in parsing_dict.keys()}
    return bp_parsing_dict


def rawdata_parsing(rawparse_params, rawdata_path, parsing_path,
                    database, progress_callback=None):

    # Setting parameters values from params_list
    (corpus_year, print_params, datatype,
     parse_affil_params_dic, parsing_filenames_dict) = rawparse_params

    print_step_title(f"PARSING OF {database.upper()} DATA FOR {corpus_year}",
                     print_params)

    print_step_text("\nParsing...", print_params)
    parsing_tup = bp.biblio_parser(rawdata_path, database, affil_filter_list=None,
                                   affil_params_dic=parse_affil_params_dic)
    bp_parsing_dict, fails_dict, db_ids_df = parsing_tup[0:3]
    parsing_dict = convert_parsing_keys_to_bm(bp_parsing_dict)
    if len(parsing_tup)>3:
        correction_dict = dict(zip(list(bm_pg.RAWDATA_CORRECT.keys()), parsing_tup[3:]))
        save_rawdata_correction(correction_dict, rawdata_path, database)
        print_step_text("  - Data of correction in rawdata of authors and addresses saved for control",
                        print_params)
    pubs_nb = fails_dict["number of article"]
    if progress_callback:
        progress_callback(80)

    save_parsing_dict(parsing_dict, parsing_path, parsing_filenames_dict, bm_pg.TSV_SAVE_EXTENT)
    if progress_callback:
        progress_callback(90)

    save_fails_dict(fails_dict, parsing_path)
    save_db_ids_data(db_ids_df, parsing_path, database)
    print_step_text(f"  - Parsing results built and saved for {pubs_nb} publications",
                    print_params)
    if progress_callback:
        progress_callback(95)

    # Building the data for addresses correction by the user
    unknown_countries_empty, all_countries_corrected, correct_files_list = True, True, []
    if database.lower() in datatype.lower():
        correct_params = [database, corpus_year, print_params]
        return_tup = build_and_save_unknown_country_data(parsing_dict, parsing_path,
                                                         bp.UNKNOWN_COUNTRY, correct_params)
        unknown_countries_empty, all_countries_corrected, correct_files_list = return_tup
    raw_parse_tup = (pubs_nb, unknown_countries_empty, all_countries_corrected, correct_files_list)
    return raw_parse_tup


def deduplicate_parsing(dedup_params_list, progress_callback=None):
    (corpus_year, print_params, institute, org_tup, wf_path, datatype,
     dedup_affil_params_dic, parsing_filenames_dict) = dedup_params_list
    base_params_list = [corpus_year, print_params, institute, wf_path,
                        dedup_affil_params_dic, parsing_filenames_dict]

    print_step_title(f"DEDUPLICATION OF PARSINGS FOR {corpus_year}", print_params)

    # Getting the full paths of the working folder architecture for the corpus "corpus_year"
    _, parsing_path_dict = set_rawdata_and_parsing_paths(wf_path, corpus_year, bm_pg.BDD_LIST)

    # Setting useful paths for corpus deduplication
    scopus_parse_path, wos_parse_path = parsing_path_dict[bp.SCOPUS], parsing_path_dict[bp.WOS]
    concat_path, dedup_path = parsing_path_dict["concat"], parsing_path_dict["dedup"]

    # Setting and correcting the Scopus parsing results
    scopus_parsing_dict = read_parsing_dict(scopus_parse_path, parsing_filenames_dict,
                                            bm_pg.TSV_SAVE_EXTENT)

    if bp.SCOPUS.lower() in datatype.lower():
        scopus_params_list = [bp.SCOPUS] + base_params_list
        correct_status = correct_parsing(scopus_params_list, scopus_parse_path,
                                         scopus_parsing_dict, bp.UNKNOWN_COUNTRY)
        if correct_status:
            scopus_parsing_dict = read_parsing_dict(scopus_parse_path, parsing_filenames_dict,
                                                    bm_pg.TSV_SAVE_EXTENT)

    # Setting and correcting the WoS parsing results
    wos_parsing_dict = read_parsing_dict(wos_parse_path, parsing_filenames_dict,
                                         bm_pg.TSV_SAVE_EXTENT)


    if bp.WOS.lower() in datatype.lower():
        wos_params_list = [bp.WOS] + base_params_list
        correct_status = correct_parsing(wos_params_list, wos_parse_path,
                                         wos_parsing_dict, bp.UNKNOWN_COUNTRY)
        if correct_status:
            wos_parsing_dict = read_parsing_dict(wos_parse_path, parsing_filenames_dict,
                                                 bm_pg.TSV_SAVE_EXTENT)
    if progress_callback:
        progress_callback(15)

    print_step_text("\nConcatenating parsing data...", print_params)
    bp_scopus_parsing_dict = revers_parsing_keys_to_bp(scopus_parsing_dict)
    bp_wos_parsing_dict = revers_parsing_keys_to_bp(wos_parsing_dict)
    if bm_pg.FIRST_BDD==bp.SCOPUS:
        bp_concat_parsing_dict = bp.concatenate_parsing(bp_scopus_parsing_dict, bp_wos_parsing_dict,
                                                        affil_filter_list=org_tup[3])
    else:
        bp_concat_parsing_dict = bp.concatenate_parsing(bp_wos_parsing_dict, bp_scopus_parsing_dict,
                                                        affil_filter_list=org_tup[3])
    concat_parsing_dict = convert_parsing_keys_to_bm(bp_concat_parsing_dict)
    if progress_callback:
        progress_callback(25)

    save_parsing_dict(concat_parsing_dict, concat_path,
                      parsing_filenames_dict, bm_pg.TSV_SAVE_EXTENT)
    print_step_text("  - Parsing data concatenated and saved", print_params)
    if progress_callback:
        progress_callback(30)

    print_step_text("\nDeduplicating parsing data...", print_params)
    bp_dedup_parsing_dict = bp.deduplicate_parsing(bp_concat_parsing_dict, norm_affil_status=False,
                                                   affil_params_dic=dedup_affil_params_dic)
    dedup_parsing_dict = convert_parsing_keys_to_bm(bp_dedup_parsing_dict)
    dedup_pub_nb, dedup_institute_pub_nb = compute_dedup_pub_number(org_tup, dedup_parsing_dict)
    _dedup_infos=(wf_path, datatype, corpus_year)
    pubs_df = dedup_parsing_dict['pub']
    ids_nb_dict = build_and_save_dedup_db_ids(pubs_df, parsing_path_dict, _dedup_infos)
    if progress_callback:
        progress_callback(90)

    save_parsing_dict(dedup_parsing_dict, dedup_path, parsing_filenames_dict, bm_pg.TSV_SAVE_EXTENT,
                      dedup_infos=_dedup_infos)
    step_txt = ("  - All parsing results deduplicated and saved as final results "
                f"for {dedup_pub_nb} publications "
                f"including {dedup_institute_pub_nb} of {institute}"
                "\n  - After deduplication, the number of kept publications from each database are:")
    for db_type, db_nb in ids_nb_dict.items():
        step_txt += f"\n      - {db_nb} for {db_type}"
    print_step_text(step_txt, print_params)
    return dedup_pub_nb, dedup_institute_pub_nb, ids_nb_dict