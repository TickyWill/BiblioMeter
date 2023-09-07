__all__ = ['create_consolidate_corpus']


def _launch_update_employees(bibliometer_path, 
                             year_select, 
                             maj_effectifs_folder_path,
                             effectifs_file_name_alias,
                             effectifs_folder_path,
                             check_effectif_status,
                             ):
    """
    """
    
    # 3rd party imports    
    from tkinter import messagebox
    
    # Local library imports     
    from BiblioMeter_FUNCTS.BM_UpdateEmployees import update_employees
    
    if check_effectif_status:
        # Lancement de la fonction MAJ Effectif
        ask_title = "- Confirmation de la mise à jour des effectifs -"
        ask_text  = f"Le fichier des effectifs LITEN va être mis à jour "
        ask_text += f"avec les nouvelles données disponibles dans le dossier :"
        ask_text += f"\n\n '{maj_effectifs_folder_path}'."
        ask_text += f"\n\nCette opération peut prendre quelques minutes."
        ask_text += f"\nDans l'attente, ne pas fermer 'BiblioMeter'."
        ask_text += f"\n\nAvant de poursuivre le croisement auteurs-effectifs, "
        ask_text += f"confirmez la mise à jour ?"            
        answer_1  = messagebox.askokcancel(ask_title, ask_text)
        if answer_1:
            (employees_year, 
             files_number_error,
             sheet_name_error, 
             column_error, 
             years2add_error,
             all_years_file_error) = update_employees(bibliometer_path)
            if not any((files_number_error,sheet_name_error, column_error, years2add_error, all_years_file_error)):
                info_title = "- Information -"
                info_text  = f"La mise à jour des effectifs a été effectuée pour l'année {employees_year}."
                info_text += f"\nLe croisement pour l'année {year_select} va être poursuivi."
                messagebox.showinfo(info_title, info_text)
                update_status = True
                return update_status
            elif all_years_file_error:
                info_title = "- Information -"
                info_text  = f"La mise à jour des effectifs a été effectuée pour l'année {employees_year}."
                info_text += f"\nMais le fichier des effectifs consolidés '{effectifs_file_name_alias}' " 
                info_text += f"non disponible a été créé dans le dossier :"
                info_text += f"\n '{effectifs_folder_path}'.\n"
                info_text += f"\nErreur précise retournée :"
                info_text += f"\n '{all_years_file_error}'.\n" 
                info_text += f"\nLe croisement pour l'année {year_select} va être poursuivi."
                messagebox.showinfo(info_title, info_text)
                update_status = True
                return update_status
            else:
                warning_title = "!!! ATTENTION : Erreurs dans les fichiers des effectifs !!!"
                if files_number_error:
                    warning_text  = f"Absence de fichier ou plus d'un fichier présent dans le dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'."
                    warning_text += f"\n\nNe conservez que le fichier utile et relancer la mise à jour,"
                    warning_text += f"\n\nou bien relancez le traitement sans mise à jour des effectifs."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                    return update_status
                if sheet_name_error:
                    warning_text  = f"Un nom de feuille du fichier des effectifs additionnels est de format incorrect "
                    warning_text += f"dans le fichier des effectifs additionnels du dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'.\n"
                    warning_text += f"\nErreur précise retournée :\n"
                    warning_text += f"\n '{sheet_name_error}'.\n"
                    warning_text += f"\n 1- Ouvrez le fichier;"
                    warning_text += f"\n 2- Vérifiez et corrigez les noms des feuilles dans ce fichier;" 
                    warning_text += f"\n 3- Sauvegardez le ficher;"
                    warning_text += f"\n 4- Relancez la mise à jour des effectifs (via le croisement auteurs-effectifs)."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                    return update_status
                if column_error:
                    warning_text  = f"Une colonne est manquante ou mal nommée dans une feuille "
                    warning_text += f"dans le fichier des effectifs additionnels du dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'.\n"
                    warning_text += f"\nErreur précise retournée :\n"
                    warning_text += f"\n '{column_error}'.\n"
                    warning_text += f"\n 1- Ouvrez le fichier;"
                    warning_text += f"\n 2- Vérifiez et corrigez les noms des colonnes des feuilles dans ce fichier;" 
                    warning_text += f"\n 3- Sauvegardez le ficher."
                    warning_text += f"\n 4- Relancez la mise à jour des effectifs (via le croisement auteurs-effectifs)."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                    return update_status
                if years2add_error:
                    warning_text  = f"Le fichier des effectifs additionnels couvre plusieurs années "
                    warning_text += f"dans le fichier des effectifs additionnels du dossier :"
                    warning_text += f"\n\n '{maj_effectifs_folder_path}'.\n"
                    warning_text += f"\n 1- Séparez les feuilles d'années différentes en fichiers d'effectifs additionnels différents;"
                    warning_text += f"\n 2- Relancer la mise à jour des effectifs (via le croisement auteurs-effectifs) " 
                    warning_text += f"\n    pour chacun des fichiers créés en les positionant seul dans le dossier successivement."
                    messagebox.showwarning(warning_title, warning_text)
                    update_status = False
                    return update_status
        else:
            # Arrêt de la procédure
            info_title    = "- Information -"
            warning_text  = f"La mise à jour des effectifs est abandonnée."
            warning_text += f"\n\nSi le croisement auteurs-effectifs pour l'année {year_select} "
            warning_text += f"est confirmé, il se fera sans cette mise à jour."            
            messagebox.showwarning(warning_title, warning_text)          
            update_status = False
            return update_status 

            
def _launch_recursive_year_search_try(year_select, 
                                      search_depth,
                                      bibliometer_path,
                                      bdd_mensuelle_path,
                                      submit_path,
                                      all_effectifs_path,
                                      employees_update_status,
                                      orphan_alias,
                                     ):
    '''       
    '''

    # Local library imports
    from BiblioMeter_FUNCTS.BM_MergePubEmployees import recursive_year_search    
    
    # Standard library imports
    import os
    
    # 3rd party imports
    from tkinter import messagebox

    def _recursive_year_search_try():
        try:            
            end_message, orphan_status = recursive_year_search(bdd_mensuelle_path, 
                                                               all_effectifs_path,
                                                               bibliometer_path,
                                                               year_select, 
                                                               search_depth)
            print('\n',end_message)
            info_title = '- Information -'
            info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} a été effectué." 
            if orphan_status: 
                info_text += f"\n\nTous les auteurs LITEN ont été identifiés dans les effectifs." 
                info_text += f"\n\nLa résolution des homonymes peut être lancée." 
            else:
                info_text += f"\n\nMais, des auteurs LITEN n'ont pas été identifiés dans les effectifs." 
                info_text += f"\n1- Ouvrez le fichier {orphan_alias} du dossier :\n  {bdd_mensuelle_path} ;"
                info_text += f"\n\n2- Suivez le mode opératoire disponible pour son utilisation ;"
                info_text += f"\n3- Puis relancez le croisement pour cette année."
                info_text += f"\n\nNéanmoins, la résolution des homonymes peut être lancée sans cette opération, "
                info_text += f"mais la liste consolidée des publications sera incomplète."
            messagebox.showinfo(info_title, info_text)
            return 'ok'

        except FileNotFoundError:
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = f"La synthèse de l'année {year_select} n'est pas disponible."
            warning_text += f"\n1- Revenez à l'onglet 'Analyse élémentaire des corpus' ;"
            warning_text += f"\n2- Effectuez la synthèse pour cette année ;"
            warning_text += f"\n3- Puis relancez le croisement pour cette année."                         
            messagebox.showwarning(warning_title, warning_text)
            return None  
        
    # Adapting search depth to available years for search                                                                         
    annees_disponibles = _annee_croisement(year_select, all_effectifs_path, search_depth)
    if annees_disponibles == None:
        return
    else:
        search_depth = min(int(search_depth), len(annees_disponibles))
        
    if employees_update_status: 
        status = "avec"
    else:
        status = "sans"

    ask_title = "- Confirmation du croisement auteurs-effectifs -"
    ask_text  = f"Le croisement avec les effectifs des années "
    ask_text += f"{', '.join([str(i) for i in annees_disponibles])} "
    ask_text += f"a été lancé pour l'année {year_select}."
    ask_text += f"\nCe croisement se fera {status} la mise à jour "
    ask_text += f"du fichier des effectifs."
    ask_text += f"\n\nCette opération peut prendre quelques minutes."
    ask_text += f"\nDans l'attente, ne pas fermer 'BiblioMeter'."
    ask_text += f"\n\nContinuer ?"
    answer    = messagebox.askokcancel(ask_title, ask_text)
    if answer:
        submit_status = os.path.exists(submit_path)                             
        if not submit_status:
            _recursive_year_search_try()
        else: 
            ask_title = "- Reconstruction du croisement auteurs-effectifs -"
            ask_text  = f"Le croisement pour l'année {year_select} est déjà disponible."
            ask_text += f"\n\nReconstruire le croisement ?"
            answer_4  = messagebox.askokcancel(ask_title, ask_text)                         
            if answer_4:
                _recursive_year_search_try()
            else:
                info_title = "- Information -"
                info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} "
                info_text += f"dejà disponible est conservé."                   
                messagebox.showinfo(info_title, info_text)                     
    else:
        info_title = "- Information -"
        info_text  = f"Le croisement auteurs-effectifs de l'année {year_select} "
        info_text += f"est annulé."            
        messagebox.showinfo(info_title, info_text)
        return            


def _annee_croisement(corpus_year, all_effectifs_path, search_depth):
    
    # 3rd party imports    
    import pandas as pd
    from tkinter import messagebox
    
    all_effectifs_df = pd.read_excel(all_effectifs_path, sheet_name = None)
    annees_dispo = [int(x) for x in list(all_effectifs_df.keys())]
    annees_a_verifier = [int(corpus_year) - int(search_depth) + (i+1) for i in range(int(search_depth))]
    annees_verifiees = list()
    for i in annees_a_verifier:
        if i in annees_dispo: annees_verifiees.append(i)
    if len(annees_verifiees) > 0:
        return annees_verifiees
    else:
        warning_title = "!!! Attention !!!"
        warning_text  = f"Le nombre d'années disponibles est insuffisant "
        warning_text += f"dans le fichier des effectifs du LITEN."
        warning_text += f"\nLe croisement auteurs-effectifs ne peut être effectué !"
        warning_text += f"\n1- Complétez le fichier des effectifs du LITEN ;"
        warning_text += f"\n2- Puis relancer le croisement auteurs-effectifs."                    
        messagebox.showwarning(warning_title, warning_text)                         
        return None


def _launch_resolution_homonymies_try(bibliometer_path, 
                                      submit_path, 
                                      homonymes_path, 
                                      homonymes_file_path, 
                                      homonymes_file_alias, 
                                      year_select):
    """
    """
    
    # Standard library imports
    import os
    
    # 3rd party imports    
    from tkinter import messagebox
    
    # Local library imports
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import solving_homonyms
    from BiblioMeter_FUNCTS.BM_UsePubAttributes import set_saved_homonyms
    
    def _resolution_homonymies_try():
        try:
            end_message, actual_homonym_status = solving_homonyms(submit_path, homonymes_file_path)
            print(end_message)
            print('\n Actual homonyms status before setting saved homonyms:', actual_homonym_status)
            if actual_homonym_status: 
                end_message, actual_homonym_status = set_saved_homonyms(bibliometer_path, year_select, actual_homonym_status)
            print('\n',end_message)
            print('\n Actual homonyms status after setting saved homonyms:', actual_homonym_status)
            info_title = "- Information -"            
            info_text  = f"Le fichier pour la résolution des homonymies de l'année {year_select} a été créé "
            info_text += f"dans le dossier :\n\n  '{homonymes_path}' "
            info_text += f"\n\nsous le nom :  '{homonymes_file_alias}'."
            if actual_homonym_status:
                info_text += f"\n\nDes homonymes existent parmi les auteurs dans les effectifs."
                info_text += f"\n\n1- Ouvrez ce fichier, "
                info_text += f"\n2- Supprimez manuellement les lignes des homonymes non-auteurs, "
                info_text += f"\n3- Puis sauvegardez le fichier sous le même nom."
                info_text += f"\n\nDès que le fichier est traité, "                
                info_text += f"\nl'affectation des OTPs peut être lancée."   
            else:
                info_text += f"\n\nAucun homonyme n'est trouvé parmi les auteurs dans les effectifs." 
                info_text += f"\n\nL'affectation des OTPs peut être lancée."   
            messagebox.showinfo(info_title, info_text)
            return 'ok'

        except FileNotFoundError:
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = f"Le fichier contenant le croisement auteurs-effectifs "
            warning_text += f"de l'année {year_select} n'est pas disponible."
            warning_text += f"\n1- Effectuez d'abord le croisement pour cette année."
            warning_text += f"\n2- Puis relancez la résolution des homonymies pour cette année."                         
            messagebox.showwarning(warning_title, warning_text)
            return None 

        except:
            warning_title = "!!! ATTENTION : erreur inconnue !!!"
            warning_text  = f"Contactez les auteurs de l'application."                        
            messagebox.showwarning(warning_title, warning_text)
            return None

    ask_title = "- Confirmation de l'étape de résolution des homonymies -"
    ask_text  = f"La création du fichier pour cette résolution "
    ask_text += f"a été lancée pour l'année {year_select}."
    ask_text += f"\n\nContinuer ?"
    answer    = messagebox.askokcancel(ask_title, ask_text)        
    if answer:
        homonymes_status = os.path.exists(homonymes_file_path)                           
        if not homonymes_status:
            _resolution_homonymies_try()
        else: 
            ask_title = "- Reconstruction de la résolution des homonymes -"
            ask_text  = f"Le fichier pour la résolution des homonymies "
            ask_text += f"de l'année {year_select} est déjà disponible."
            ask_text += f"\n\nReconstruire ce fichier ?"
            answer_1  = messagebox.askokcancel(ask_title, ask_text)                         
            if answer_1:
                _resolution_homonymies_try()
            else:
                info_title = "- Information -"
                info_text  = f"Le fichier pour la résolution des homonymies "
                info_text += f"de l'année {year_select} dejà disponible est conservé."                   
                messagebox.showinfo(info_title, info_text)                     
    else:
        info_title = "- Information -"
        info_text = f"La création du fichier pour la résolution "
        info_text += f"des homonymies de l'année {year_select} est annulée."            
        messagebox.showinfo(info_title, info_text)
    return    


def _launch_add_OTP_try(bibliometer_path,
                        homonymes_path, 
                        homonymes_file_path, 
                        OTP_path, 
                        OTP_file_base_alias,
                        dpt_label_list,
                        year_select):
    """
    """
    
    # Standard library imports
    import os
    from pathlib import Path
    
    # 3rd party imports    
    from tkinter import messagebox
    
    # Local library imports
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import add_OTP
    from BiblioMeter_FUNCTS.BM_UsePubAttributes import save_homonyms
    from BiblioMeter_FUNCTS.BM_UsePubAttributes import set_saved_otps

    def _add_OTP_try():
        try:
            end_message = save_homonyms(bibliometer_path, year_select)
            print('\n',end_message)
            end_message = add_OTP(homonymes_file_path, OTP_path, OTP_file_base_alias)
            print(end_message)
            end_message = set_saved_otps(bibliometer_path, year_select)
            print(end_message)                
            info_title = "- Information -"
            info_text  = f"Les fichiers de l'année {year_select} pour l'attribution des OTPs "
            info_text += f"ont été créés dans le dossier : \n\n'{OTP_path}' "
            info_text += f"\n\n1- Ouvrez le fichier du département ad-hoc, "
            info_text += f"\n2- Attribuez manuellement à chacune des publications un OTP, "
            info_text += f"\n3- Sauvegardez le fichier en ajoutant à son nom '_ok'."
            info_text += f"\n\nDès que les fichiers de tous les départements sont traités, "
            info_text += f"\nla liste consolidée des publications de l'année {year_select} peut être créée."          
            messagebox.showinfo(info_title, info_text)
            return 'ok'

        except FileNotFoundError:
            warning_title = "!!! ATTENTION : fichier manquant !!!"
            warning_text  = f"Le fichier contenant la résolution des homonymies "
            warning_text += f"de l'année {year_select} n'est pas disponible."
            warning_text += f"\n1- Effectuez la résolution des homonymies pour cette année."
            warning_text += f"\n2- Relancez l'attribution des OTPs pour cette année."                         
            messagebox.showwarning(warning_title, warning_text)
            return None 

        except:
            warning_title = "!!! ATTENTION : erreur inconnue !!!"
            warning_text  = f"Contactez les auteurs de l'application."                        
            messagebox.showwarning(warning_title, warning_text)                
            return None

    ask_title = "- Confirmation de l'étape d'attribution des OTPs -"
    ask_text  = f"La création des fichiers pour cette attribution "
    ask_text += f"a été lancée pour l'année {year_select}."
    ask_text += f"\n\nContinuer ?"
    answer    = messagebox.askokcancel(ask_title, ask_text)        
    if answer:
        OTP_path_status = os.path.exists(OTP_path)
        if OTP_path_status:
            OTP_files_status_list = []
            for dpt_label in dpt_label_list:
                dpt_OTP_file_name = OTP_file_base_alias + '_' + dpt_label + '.xlsx'
                dpt_OTP_file_path = OTP_path / Path(dpt_OTP_file_name)
                OTP_files_status_list.append(not(dpt_OTP_file_path.is_file()))
            if any(OTP_files_status_list):
                _add_OTP_try()
            else: 
                ask_title = "- Reconstruction de l'attribution des OTPs -"
                ask_text  = f"Les fichiers pour l'attribution des OTPs "
                ask_text += f"de l'année {year_select} sont déjà disponibles."
                ask_text += f"\n\nReconstruire ces fichiers ?"
                answer_1  = messagebox.askokcancel(ask_title, ask_text)                         
                if answer_1:
                    _add_OTP_try()
                else:
                    info_title = "- Information -"
                    info_text  = f"Les fichiers pour l'attribution des OTPs "
                    info_text += f"de l'année {year_select} dejà disponibles sont conservés."                   
                    messagebox.showinfo(info_title, info_text)
        else:
            os.mkdir(OTP_path)
            _add_OTP_try()
    else:
        info_title = "- Information -"
        info_text = f"La création des fichiers pour l'attribution des OTPs "
        info_text += f"de l'année {year_select} est annulée."            
        messagebox.showinfo(info_title, info_text)
    return   


def _launch_update_if_db(bibliometer_path,
                         corpi_year_list,
                         year_select,
                         pub_list_path,
                         check_if_status,
                        ):
    """
    """
    
    # 3rd party imports    
    from tkinter import messagebox
    
    # Local library imports     
    from BiblioMeter_FUNCTS.BM_UpdateImpactFactors import update_inst_if_database
    
    if check_if_status:
        # Lancement de la fonction MAJ Effectif
        ask_title = "- Confirmation de la mise à jour des IFs -"
        ask_text  = f"La base de données des IFs va être mise à jour "
        ask_text += f"avec les nouvelles données disponibles dans les dossiers :"
        ask_text += f"\n\n '{pub_list_path}' "
        ask_text += f"\n des corpus des années {corpi_year_list} ."
        ask_text += f"\n\nCette opération peut prendre quelques secondes."
        ask_text += f"\nDans l'attente, ne pas fermer 'BiblioMeter'."
        ask_text += f"\n\nAvant de poursuivre la consolidation, "
        ask_text += f"confirmez la mise à jour ?"            
        answer_1  = messagebox.askokcancel(ask_title, ask_text)
        if answer_1:
            _, if_years_list = update_inst_if_database(bibliometer_path, corpi_year_list)
            info_title = "- Information -"
            info_text  = f"La mise à jour de la base de données des IFs a été effectuée "
            info_text += f"pour les années  {if_years_list}."
            info_text += f"\nLa consolidation pour l'année {year_select} va être poursuivie."
            messagebox.showinfo(info_title, info_text)
            update_status = True
            return update_status
        else:
            # Arrêt de la procédure
            info_title    = "- Information -"
            warning_text  = f"La mise à jour des effectifs est abandonnée."
            warning_text += f"\n\nSi la consolidation pour l'année {year_select} "
            warning_text += f"est confirmée, elle se fera sans cette mise à jour."            
            messagebox.showwarning(warning_title, warning_text)          
            update_status = False
            return update_status 


def _launch_pub_list_conso_try(bibliometer_path, 
                               OTP_path,
                               pub_list_path,
                               pub_list_file_path, 
                               OTP_file_base_alias,
                               pub_list_file_alias,
                               year_inst_if_alias,
                               bdd_multi_annuelle_folder_alias,
                               years_list,
                               year_select):
    """
    """
    
    # Standard library imports
    import os
    
    # 3rd party imports    
    from tkinter import messagebox
    
    # Local library imports
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import concatenate_pub_lists
    from BiblioMeter_FUNCTS.BM_ConsolidatePubList import consolidate_pub_list
    from BiblioMeter_FUNCTS.BM_UsePubAttributes import save_otps
    
    def _consolidate_pub_list():
        try:
            end_message, split_ratio = consolidate_pub_list(bibliometer_path, OTP_path, pub_list_path, 
                                                            pub_list_file_path, OTP_file_base_alias, 
                                                            year_select)
            print(end_message)
            end_message = save_otps(bibliometer_path, year_select)
            print('\n',end_message)
            end_message = concatenate_pub_lists(bibliometer_path, years_list)
            print('\n',end_message)
            info_title = "- Information -"
            info_text  = f"La liste consolidée des publications de l'année {year_select} "
            info_text += f"a été créée dans le dossier :\n\n '{pub_list_path}' "
            info_text += f"\n\nsous le nom :   '{pub_list_file_alias}'."
            info_text += f"\n\nLes IFs disponibles ont été automatiquement attribués." 
            info_text += f"\n\nDe plus, la liste des journaux avec ISSNs et IFs connus ou inconnus "
            info_text += f"a été créée dans le même dossier sous le nom : \n\n '{year_inst_if_alias}' "
            info_text += f"\n\n Ce fichier peut être modifié pour compléter la base de donnée des IFs :"
            info_text += f"\n\n1- Ouvrez ce fichier, "
            info_text += f"\n2- Complétez manuellement les IFs inconnus, "
            info_text += f"\n3- Puis sauvegardez le fichier sous le même nom."
            info_text += f"\n\nChaque fois que ces compléments sont apportés, "
            info_text += f"la base de données des IFs doit être mise à jour, "
            info_text += f"ainsi que les listes consolidées des publications existantes."
            info_text += f"\n\nDe plus, la liste consolidée des publications a été décomposée à {split_ratio} % "
            info_text += f"en trois fichiers disponibles dans le même dossier correspondant aux différentes "
            info_text += f"classes de documents (les classes n'étant pas exhaustives, la décomposition peut être partielle)."            
            info_text += f"\n\nEnfin, la concaténation des listes consolidées des publications "
            info_text += f"disponibles, à été créée dans le dossier :\n\n '{bdd_multi_annuelle_folder_alias}' "
            info_text += f"\n\nsous un nom vous identifiant ainsi que la liste des années prises en compte "
            info_text += f"et caractérisé par la date et l'heure de la création."
                           
            messagebox.showinfo(info_title, info_text)
            return 'ok'

        except FileNotFoundError:
            warning_title = "!!! ATTENTION : fichiers manquants !!!"
            warning_text  = f"Les fichiers d'attribution des OTPs "
            warning_text += f"de l'année {year_select} ne sont pas tous disponibles."
            warning_text += f"\n1- Effectuez l'attribution des OTPs pour cette année."
            warning_text += f"\n2- Relancez la consolidation de la liste des publications pour cette année."                         
            messagebox.showwarning(warning_title, warning_text)
            return None 

        except:
            warning_title = "!!! ATTENTION : erreur inconnue !!!"
            warning_text  = f"Contactez les auteurs de l'application."                        
            messagebox.showwarning(warning_title, warning_text)                
            return None

    ask_title = "- Confirmation de l'étape de consolidation de la liste des publications -"
    ask_text  = f"La création du fichier de la liste consolidée des publications "
    ask_text += f"a été lancée pour l'année {year_select}."
    ask_text += f"\n\nContinuer ?"
    answer    = messagebox.askokcancel(ask_title, ask_text)        
    if answer:
        pub_list_status = os.path.exists(pub_list_file_path)                           
        if not pub_list_status:
            _consolidate_pub_list()
        else: 
            ask_title = "- Reconstruction de la liste consolidée des publications -"
            ask_text  = f"Le fichier de la liste consolidée des publications "
            ask_text += f"de l'année {year_select} est déjà disponible."
            ask_text += f"\n\nReconstruire ce fichier ?"
            answer_1  = messagebox.askokcancel(ask_title, ask_text)                         
            if answer_1:
                _consolidate_pub_list()
            else:
                info_title = "- Information -"
                info_text  = f"Le fichier de la liste consolidée des publications "
                info_text += f"de l'année {year_select} dejà disponible est conservé."                   
                messagebox.showinfo(info_title, info_text)                     
    else:
        info_title = "- Information -"
        info_text = f"La création du fichier de la liste consolidée des publications "
        info_text += f"de l'année {year_select} est annulée."            
        messagebox.showinfo(info_title, info_text)
    return     


def create_consolidate_corpus(self, bibliometer_path, parent):
    
    """
    Description : function working as a bridge between the BiblioMeter 
    App and the functionalities needed for the use of the app
    
    Uses the following globals : 
    - DIC_OUT_PARSING
    - FOLDER_NAMES
    
    Args : takes only self and bibliometer_path as arguments. 
    self is the intense in which PageThree will be created
    bibliometer_path is a type Path, and is the path to where the folders
    organised in a very specific way are stored
    
    Returns : 
    
    Note:
        The function '_mm_to_px' is imported from the module 'BiblioGui' 
        of the package 'BiblioAnalysis_Utils'.
    """

    # Standard library imports
    import os
    from pathlib import Path

    # 3rd party imports    
    import pandas as pd
    import tkinter as tk
    from datetime import date
    from tkinter import font as tkFont
    from tkinter import filedialog
    from tkinter import messagebox
    
    # BiblioAnalysis_Utils library imports
    from BiblioAnalysis_Utils.BiblioGui import _mm_to_px        
    
    # Local library imports         
    from BiblioMeter_GUI.Coordinates import root_properties
    from BiblioMeter_GUI.Useful_Functions import encadre_RL
    from BiblioMeter_GUI.Useful_Functions import last_available_years
    from BiblioMeter_GUI.Useful_Functions import font_size
    from BiblioMeter_GUI.Useful_Functions import place_after
    from BiblioMeter_GUI.Useful_Functions import place_bellow
    
    # Local globals imports
    from BiblioMeter_FUNCTS.BM_EmployeesGlobals import EMPLOYEES_ARCHI
    from BiblioMeter_FUNCTS.BM_EmployeesGlobals import SEARCH_DEPTH
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_BACKUP 
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_BDD_MULTI_ANNUELLE
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_IF
    from BiblioMeter_FUNCTS.BM_PubGlobals import ARCHI_YEAR
    from BiblioMeter_FUNCTS.BM_PubGlobals import DPT_LABEL_DICT
    
    from BiblioMeter_GUI.Coordinates import ETAPE_LABEL_TEXT_LIST
    from BiblioMeter_GUI.Coordinates import FONT_NAME    
    from BiblioMeter_GUI.Coordinates import TEXT_CROISEMENT
    from BiblioMeter_GUI.Coordinates import TEXT_HOMONYMES
    from BiblioMeter_GUI.Coordinates import TEXT_MAJ_EFFECTIFS
    from BiblioMeter_GUI.Coordinates import TEXT_MAJ_DB_IF
    from BiblioMeter_GUI.Coordinates import TEXT_OTP
    from BiblioMeter_GUI.Coordinates import TEXT_PAUSE
    from BiblioMeter_GUI.Coordinates import TEXT_PUB_CONSO
    from BiblioMeter_GUI.Coordinates import TEXT_YEAR_PI    
    from BiblioMeter_GUI.GUI_Globals import CORPUSES_NUMBER
    from BiblioMeter_GUI.GUI_Globals import PPI

    # Defining internal functions

    def _etape_frame(self, num):
        '''The local function `_etape_frame` sets the 'etape' and place in the page
        using the global 'ETAPE_LABEL_TEXT_LIST' and the local variables 'etape_label_format', 
        'etape_label_font', 'etape_underline', 'etape_label_pos_x' and 'etape_label_pos_y_list'.
        
        Args:
            num (int): The order of the 'etape' in 'ETAPE_LABEL_TEXT_LIST'.
        '''
        etape = tk.Label(self, 
                         text      = ETAPE_LABEL_TEXT_LIST[num], 
                         justify   = etape_label_format, 
                         font      = etape_label_font, 
                         underline = etape_underline)
        etape.place(x = etape_label_pos_x, 
                    y = etape_label_pos_y_list[num])
        return etape
       
    def _launch_exit():
        ask_title = "Arrêt de BiblioMeter"
        ask_text =  "Après la fermeture des fenêtres, "
        ask_text += "les traitements effectués sont sauvegardés."
        ask_text += "\nLe traitement peut être repris ultérieurement."
        ask_text += "\nConfirmez la mise en pause ?"
        exit_answer = messagebox.askokcancel(ask_title, ask_text)
        if exit_answer:
            parent.destroy()
    
    ########################## Function start
    
    # Getting useful window sizes and scale factors depending on displays properties
    sizes_tuple   = root_properties(self)
    win_width_px  = sizes_tuple[0]    # unused here
    win_height_px = sizes_tuple[1]    # unused here
    width_sf_px   = sizes_tuple[2] 
    height_sf_px  = sizes_tuple[3]    # unused here
    width_sf_mm   = sizes_tuple[4]
    height_sf_mm  = sizes_tuple[5]
    width_sf_min  = min(width_sf_mm, width_sf_px)
    
    # Setting useful local variables for positions modification (globals to create ??)
    # numbers are reference values in mm for reference screen
    eff_etape_font_size      = font_size(14, width_sf_min)
    eff_launch_font_size     = font_size(13, width_sf_min)
    eff_answer_font_size     = font_size(13, width_sf_min)
    eff_select_font_size     = font_size(12, width_sf_min)
    eff_buttons_font_size    = font_size(11, width_sf_min)                                         

    etape_label_pos_x        = _mm_to_px( 10 * width_sf_mm, PPI)
    etape_label_pos_y_list   = [_mm_to_px( y * height_sf_mm, PPI) for y in [40, 74, 101, 129]]
    etape_button_dx          = _mm_to_px( 10 * width_sf_mm, PPI)
    etape_button_dy          = _mm_to_px(  5 * height_sf_mm, PPI)
    etape_check_dy           = _mm_to_px( -8 * height_sf_mm, PPI)

    exit_button_x_pos        = _mm_to_px(193 * width_sf_mm,  PPI) 
    exit_button_y_pos        = _mm_to_px(145 * height_sf_mm, PPI)

    year_button_x_pos        = _mm_to_px( 10 * width_sf_mm,  PPI) 
    year_button_y_pos        = _mm_to_px( 26 * height_sf_mm, PPI)    
    dy_year                  = -6
    ds_year                  = 5

    # Setting useful aliases
    bdd_multi_annuelle_folder_alias = ARCHI_BDD_MULTI_ANNUELLE["root"]
    bdd_mensuelle_alias             = ARCHI_YEAR["bdd mensuelle"] 
    homonymes_path_alias            = ARCHI_YEAR["homonymes folder"]
    homonymes_file_base_alias       = ARCHI_YEAR["homonymes file name base"]
    OTP_path_alias                  = ARCHI_YEAR["OTP folder"]
    OTP_file_base_alias             = ARCHI_YEAR["OTP file name base"]
    pub_list_path_alias             = ARCHI_YEAR["pub list folder"]
    pub_list_file_base_alias        = ARCHI_YEAR["pub list file name base"]
    corpus_alias                    = ARCHI_YEAR['corpus']
    dedup_alias                     = ARCHI_YEAR['dedup']
    parsing_alias                   = ARCHI_YEAR['parsing']
    submit_alias                    = ARCHI_YEAR["submit file name"]
    orphan_alias                    = ARCHI_YEAR["orphan file name"]
    listing_alias                   = EMPLOYEES_ARCHI["root"]
    effectifs_folder_name_alias     = EMPLOYEES_ARCHI["all_years_employees"]
    effectifs_file_name_alias       = EMPLOYEES_ARCHI["employees_file_name"]
    maj_effectifs_folder_name_alias = EMPLOYEES_ARCHI["complementary_employees"] 
    year_inst_if_base_alias         = ARCHI_IF["institute_if_base"]

    # Setting useful paths independent from corpus year
    effectifs_root_path       = bibliometer_path / Path(listing_alias)
    effectifs_folder_path     = effectifs_root_path / Path(effectifs_folder_name_alias)
    maj_effectifs_folder_path = effectifs_root_path / Path(maj_effectifs_folder_name_alias)    
    all_effectifs_path        = effectifs_folder_path / Path(effectifs_file_name_alias)

    # Getting departments label list
    dpt_label_list = list(DPT_LABEL_DICT.keys()) 
    
    ### Décoration de la page
    # - Canvas
    fond = tk.Canvas(self, 
                     width = win_width_px, 
                     height = win_height_px)
    fond.place(x = 0, y = 0)
    
    # - Etapes labels
    etape_label_font   = tkFont.Font(family = FONT_NAME, 
                                     size = eff_etape_font_size,
                                     weight = 'bold')
    etapes_number      = len(ETAPE_LABEL_TEXT_LIST)
    etape_label_format = 'left'
    etape_underline    = -1
    etapes             = [_etape_frame(self, etape_num) for etape_num in range(etapes_number)]    
    
    ### Choix de l'année 
    years_list = last_available_years(bibliometer_path, CORPUSES_NUMBER)
    default_year = years_list[-1]  
    variable_years = tk.StringVar(self)
    variable_years.set(default_year)
    
    # Création de l'option button des années    
    self.font_OptionButton_years = tkFont.Font(family = FONT_NAME, 
                                               size = eff_buttons_font_size)
    self.OptionButton_years = tk.OptionMenu(self, 
                                            variable_years, 
                                            *years_list)
    self.OptionButton_years.config(font = self.font_OptionButton_years)
    
        # Création du label
    self.font_Label_years = tkFont.Font(family = FONT_NAME, 
                                        size = eff_select_font_size)
    self.Label_years = tk.Label(self, 
                                text = TEXT_YEAR_PI, 
                                font = self.font_Label_years)
    self.Label_years.place(x = year_button_x_pos, y = year_button_y_pos)
    
    place_after(self.Label_years, self.OptionButton_years, dy = dy_year)
    encadre_RL(fond, self.Label_years, self.OptionButton_years, ds = ds_year)

    ################## Etape 1 : Croisement auteurs-effectifs 
    def _launch_recursive_year_search():
        ''' Fonction executée par le bouton 'button_croisement'.      
        '''

        # 3rd party imports    
        from pathlib import Path                                         
        
        # Getting year selection
        year_select =  variable_years.get()
        
        # Setting paths dependent on year_select
        corpus_year_path = bibliometer_path / Path(year_select)                 
        parsing_path = corpus_year_path / Path(corpus_alias) / Path(dedup_alias) / Path(parsing_alias)   # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        bdd_mensuelle_path =  corpus_year_path / Path(bdd_mensuelle_alias)
        submit_path = corpus_year_path / Path(bdd_mensuelle_alias) / Path(submit_alias) 
        
        # Getting search depth selection
        search_depth = go_back_years.get()
        
        # Getting check_effectif_status
        check_effectif_status = check_effectif_var.get()
        
        # Updating employees file
        employees_update_status = _launch_update_employees(bibliometer_path, 
                                                           year_select, 
                                                           maj_effectifs_folder_path,
                                                           effectifs_file_name_alias,
                                                           effectifs_folder_path,
                                                           check_effectif_status,
                                                           )
        
        if not employees_update_status : 
            check_effectif_var.set(0)
            check_effectif_status = check_effectif_var.get()
            
        # Trying launch of recursive search for authors in employees file        
        _launch_recursive_year_search_try(year_select, 
                                          search_depth,
                                          bibliometer_path,
                                          bdd_mensuelle_path,
                                          submit_path,
                                          all_effectifs_path,
                                          employees_update_status,
                                          orphan_alias,
                                         )

    ### Définition ou choix de la profondeur de recherche
    # Fixe la profondeur de recherche à SEARCH_DEPTH dans l'historique des effectifs
    go_back_years_list = [i for i in range(1,date.today().year-2009)]
    go_back_years = tk.StringVar(self)
    go_back_years.set(go_back_years_list[SEARCH_DEPTH-1])
    
    ### Définition du  bouton 'button_croisement' 
    font_croisement = tkFont.Font(family = FONT_NAME, 
                                  size   = eff_launch_font_size)
    button_croisement = tk.Button(self, 
                                  text = TEXT_CROISEMENT,
                                  font = font_croisement, 
                                  command = lambda: _launch_recursive_year_search())
    
    check_effectif_var = tk.IntVar()
    check_effectif_box = tk.Checkbutton(self, 
                                        text = TEXT_MAJ_EFFECTIFS, 
                                        variable = check_effectif_var, 
                                        onvalue = 1, 
                                        offvalue = 0)
    
    font_check = tkFont.Font(family = FONT_NAME, 
                             size = eff_answer_font_size)

    etape_1 = etapes[0]
    place_bellow(etape_1, 
                 check_effectif_box, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy / 2)
    place_bellow(check_effectif_box, 
                 button_croisement, 
                 dy = etape_button_dy / 2)  
                                             
    ################## Etape 2 : Résolution des homonymies
    def _launch_resolution_homonymies():
        '''Fonction executée par le bouton 'button_homonymes'.        
        '''
        # 3rd party imports    
        from pathlib import Path 
        
        # Renewing year selection
        year_select = variable_years.get()
        
        # Setting paths and aliases dependent pn year_select  
        homonymes_file_alias =  homonymes_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path = bibliometer_path / Path(year_select)                 
        submit_path = corpus_year_path / Path(bdd_mensuelle_alias) / Path(submit_alias) 
        homonymes_path = corpus_year_path / Path(homonymes_path_alias)
        homonymes_file_path = homonymes_path / Path(homonymes_file_alias)
        
        # Trying launch creation of file for homonymies resolution
        _launch_resolution_homonymies_try(bibliometer_path, 
                                          submit_path, 
                                          homonymes_path, 
                                          homonymes_file_path, 
                                          homonymes_file_alias, 
                                          year_select)
    
    ### Définition du bouton "button_homonymes"
    font_homonymes = tkFont.Font(family = FONT_NAME, 
                                 size   = eff_launch_font_size)
    button_homonymes = tk.Button(self, 
                                     text = TEXT_HOMONYMES, 
                                     font = font_homonymes, 
                                     command = lambda: _launch_resolution_homonymies())
    etape_2 = etapes[1]
    place_bellow(etape_2, 
                 button_homonymes, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy)
    
    ################## Etape 3 : Attribution des OTPs
    def _launch_add_OTP():
        '''Fonction executée par le bouton 'button_OTP'.        
        '''
        # 3rd party imports    
        from pathlib import Path 
      
        # Renewing year selection
        year_select = variable_years.get()
        
        # Setting paths and aliases dependent on year_select  
        homonymes_file_alias =  homonymes_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path     = bibliometer_path / Path(year_select)
        homonymes_path       = corpus_year_path / Path(homonymes_path_alias)
        homonymes_file_path  = homonymes_path / Path(homonymes_file_alias) 
        OTP_path             = corpus_year_path / Path(OTP_path_alias)        
        
        # Trying launch creation of files for OTP attribution
        _launch_add_OTP_try(bibliometer_path, 
                            homonymes_path, 
                            homonymes_file_path, 
                            OTP_path, 
                            OTP_file_base_alias,
                            dpt_label_list,
                            year_select)

    ### Définition du bouton "button_OTP"
    font_OTP = tkFont.Font(family = FONT_NAME, 
                           size   = eff_launch_font_size)
    button_OTP = tk.Button(self, 
                           text = TEXT_OTP, 
                           font = font_OTP,  
                           command = lambda: _launch_add_OTP())
    etape_3 = etapes[2]
    place_bellow(etape_3, 
                 button_OTP, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy)
    
    ################## Etape 4 : Liste consolidée des publications
    def _launch_pub_list_conso():
        '''Fonction executée par le bouton 'button_finale'.        
        '''
        # 3rd party imports    
        from pathlib import Path     
            
        # Renewing year selection and years 
        year_select = variable_years.get()
        
        # Setting year_select dependent paths and aliases
        year_inst_if_alias = year_select + year_inst_if_base_alias
        pub_list_file_alias = pub_list_file_base_alias + f' {year_select}.xlsx'
        corpus_year_path = bibliometer_path / Path(year_select)                  
        OTP_path = corpus_year_path / Path(OTP_path_alias)
        pub_list_path = corpus_year_path / Path(pub_list_path_alias)
        pub_list_file_path = pub_list_path / Path(pub_list_file_alias)             
        
        # Getting check_if_status
        check_if_status = check_if_var.get()
        
        # Updating IF database
        if_db_update_status = _launch_update_if_db(bibliometer_path,
                                                   years_list,
                                                   year_select,
                                                   pub_list_path,
                                                   check_if_status,
                                                   )       
        if not if_db_update_status : 
            check_if_var.set(0)
            check_if_status = check_if_var.get()
        
        # Trying launch creation of consolidated publications lists
        _launch_pub_list_conso_try(bibliometer_path, 
                                   OTP_path,
                                   pub_list_path,
                                   pub_list_file_path, 
                                   OTP_file_base_alias,
                                   pub_list_file_alias,
                                   year_inst_if_alias,
                                   bdd_multi_annuelle_folder_alias,
                                   years_list,
                                   year_select)

    # Définition du bouton de création de la liste consolidée des publications
    font_finale = tkFont.Font(family = FONT_NAME, 
                              size   = eff_launch_font_size)
    button_finale = tk.Button(self, 
                              text = TEXT_PUB_CONSO, 
                              font = font_finale, 
                              command = lambda: _launch_pub_list_conso())
    
    check_if_var = tk.IntVar()
    check_if_box = tk.Checkbutton(self, 
                                  text = TEXT_MAJ_DB_IF, 
                                  variable = check_if_var, 
                                  onvalue = 1, 
                                  offvalue = 0)
    
    font_check = tkFont.Font(family = FONT_NAME, 
                             size = eff_answer_font_size)

    etape_4 = etapes[3]
    place_bellow(etape_4, 
                 check_if_box, 
                 dx = etape_button_dx, 
                 dy = etape_button_dy / 2)
    place_bellow(check_if_box, 
                 button_finale, 
                 dy = etape_button_dy / 2)  
    
    #etape_4 = etapes[3]
    #
    #place_bellow(etape_4, 
    #             button_finale, 
    #             dx = etape_button_dx, 
    #             dy = etape_button_dy)
                  
    ################## Bouton pour sortir de la page
    font_button_quit = tkFont.Font(family = FONT_NAME, 
                                   size   = eff_buttons_font_size)
    button_quit = tk.Button(self, 
                            text = TEXT_PAUSE, 
                            font = font_button_quit, 
                            command = lambda: _launch_exit()).place(x = exit_button_x_pos, 
                                                                    y = exit_button_y_pos, 
                                                                    anchor = 'n')