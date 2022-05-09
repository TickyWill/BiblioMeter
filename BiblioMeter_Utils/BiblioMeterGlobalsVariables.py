__all__ = ['PATH_SCOPUS_PARSING',
           'PATH_WOS_PARSING',
           'PATH_DAT_CONCATENATED',
           'PATH_DAT_DEDUPLICATED',
           'PATH_JP',
           'PATH_TO_EFFECTIFS',
           'OTP_LIST',
           'OTP_STRING']

# Usefull path to documents
PATH_SCOPUS_PARSING = 'C:/Users/ld259969/Documents/PyVenv/BiblioMeterDraft/Liten_Corpuses/2021_scopus/parsing/'
PATH_WOS_PARSING = 'C:/Users/ld259969/Documents/PyVenv/BiblioMeterDraft/Liten_Corpuses/2021_wos/parsing/'
PATH_DAT_CONCATENATED = 'C:/Users/ld259969/Documents/PyVenv/BiblioMeterDraft/Concatenated_Deduplicated_Parsing/concatenated/'
PATH_DAT_DEDUPLICATED = 'C:/Users/ld259969/Documents/PyVenv/BiblioMeterDraft/Concatenated_Deduplicated_Parsing/deduplicated/'
PATH_JP = 'C:/Users/ld259969/Documents/PyVenv/BiblioMeterDraft/Concatenated_Deduplicated_Parsing/JP/'
PATH_TO_EFFECTIFS = 'C:/Users/ld259969/Documents/PyVenv/BiblioMeterDraft/Liten_Effectifs/Effectifs.xlsx'


# Dictionary of the OTPs
OTP_LIST = {
        'STB': ['MSBAT', 'INDIB', 'TEENV'],
        'SAMA': ['MSBAT', 'INDIB', 'COBH2', 'STSH2', 'EMEPE', 'SYS2E', 'SYSIE'],
        'STP': ['COBH2', 'STSH2', 'TEENV'],
        'STH2': ['PROH2'],
        'SCPC': ['STSH2', 'ASMAT', 'SECSY', 'INREL', 'MATEP', 'ESQVE', 'MATNA', 'TECNA', 'IDNES'],
        'SSETI': ['COTHE', 'SYS2E', 'SYSIE', 'CHECC'],
        'SA3D': ['PROH2', 'COTHE', 'ASMAT', 'FAB3D'],
        'STDC': ['INDIB', 'PROH2', 'STSH2', 'ASMAT', 'INNAN', 'TEENV', 'CHECC', 'NRBCT'],
        'SCSF': ['PROH2', 'ELORG'],
        'SCPV': ['MACPV', 'HETPV'],
        'SMSP': ['MSYPV', 'TEENV'],
        'SIRE': ['MSBAT', 'EMEPE', 'SYS2E', 'SYSIE'],
    
        'STHB': ['Vielle appelation'],
    
        'DEHT': ['MSBAT', 'INDIB', 'COBH2', 'STSH2', 'EMEPE', 'SYS2E', 'SYSIE', 'TEENV'], # OK
        'DTBH': ['PROH2', 'STSH2', 'ASMAT', 'SECSY', 'INREL', 'MATEP', 'ESQVE', 'MATNA', 'TECNA', 'IDNES', 'COTHE', 'SYS2E', 'SYSIE', 'CHECC'], # OK
        'DTCH': ['PROH2', 'STSH2', 'ASMAT', 'SECSY', 'INREL', 'MATEP', 'ESQVE', 'MATNA', 'TECNA', 'IDNES', 'COTHE', 'SYS2E', 'SYSIE', 'CHECC'], # OK
        'DTNM': ['PROH2', 'COTHE', 'ASMAT', 'FAB3D', 'INDIB', 'STSH2', 'INNAN', 'TEENV', 'CHECC', 'NRBCT', 'ELORG'], # OK
        'DTS' : ['MACPV', 'HETPV', 'MSYPV', 'TEENV', 'MSBAT', 'EMEPE', 'SYS2E', 'SYSIE'], # OK
        
        '(LITEN)' : ['A rajouter'],


        'S2CE': ['Vieille appellation'],
        'S3E' : ['Vieille appellation'],
        'SBST': ['Vieille appellation'],
        'SCTR': ['Vieille appellation'],
        'SMCP': ['Vieille appellation'],
        'SBST': ['Vieille appellation'],
        'SMPV': ['Vieille appellation']    
}

OTP_STRING = {
        'STB': "MSBAT, INDIB, TEENV",
        'SAMA': "MSBAT, INDIB, COBH2, STSH2, EMEPE, SYS2E, SYSIE",
        'STP': "COBH2, STSH2, TEENV",

        'STH2': "PROH2",
        'SCPC': "STSH2, ASMAT, SECSY, INREL, MATEP, ESQVE, MATNA, TECNA, IDNES",
        'SSETI': "COTHE, SYS2E, SYSIE, CHECC",

        'SA3D': "PROH2, COTHE, ASMAT, FAB3D",
        'STDC': "INDIB, PROH2, STSH2, ASMAT, INNAN, TEENV, CHECC, NRBCT",
        'SCSF': "PROH2, ELORG",

        'SCPV': "MACPV, HETPV",
        'SMSP': "MSYPV, TEENV",
        'SIRE': "MSBAT, EMEPE, SYS2E, SYSIE",

        'DEHT': "MSBAT, INDIB, COBH2, STSH2, EMEPE, SYS2E, SYSIE, TEENV",
        'DTBH': "PROH2, STSH2, ASMAT, SECSY, INREL, MATEP, ESQVE, MATNA, TECNA, IDNES, COTHE, SYS2E, SYSIE, CHECC",
        'DTCH': "PROH2, STSH2, ASMAT, SECSY, INREL, MATEP, ESQVE, MATNA, TECNA, IDNES, COTHE, SYS2E, SYSIE, CHECC",
        'DTNM': "PROH2, COTHE, ASMAT, FAB3D, INDIB, STSH2, INNAN, TEENV, CHECC, NRBCT, ELORG",
        'DTS' : "MACPV, HETPV, MSYPV, TEENV, MSBAT, EMEPE, SYS2E, SYSIE",
    
        '(LITEN)': "A rajouter",
    
        'STHB': "Vieille appellation",
        'S2CE': "Vieille appellation",
        'S3E' : "Vieille appellation",
        'SBST': "Vieille appellation",
        'SCTR': "Vieille appellation",
        'SMCP': "Vieille appellation",
        'SBST': "Vieille appellation",
        'SMPV': "Vieille appellation"    
}

