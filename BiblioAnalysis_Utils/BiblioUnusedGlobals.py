__all__ = ['SCOPUS_TAGS',
           'WOS_TAGS','WOS_TAGS_DICT',
           ]

# WOS_TAGS unused
WOS_TAGS = '''FN,VR,PT,AU,AF,BA,BF,CA,GP,BE,TI,SO,SE,BS,LA,DT,CT,CY,CL,
              SP,HO,DE,ID,AB,C1,RP,EM,RI,OI,FU,FX,CR,NR,TC,Z9,U1,U2,PU,
              PI,PA,SN,EI,BN,J9,JI,PD,PY,VL,IS,SI,PN,SU,MA,BP,EP,AR,DI,
              D2,EA,EY,PG,P2,WC,SC,GA,PM,UT,OA,HP,ES,HC,DA,ER,EF'''

#  WOS_TAGS_VALUES unused
WOS_TAGS_VALUES ='''File Name,Version Number,Publication Type (J=Journal; B=Book; S=Series;P=Patent),
Authors,Author Full Name,Book Authors,Book Authors Full Name,
Group Authors,Book Group Authors,Editors,Document Title,Publication Name,
Book Series Title,Book Series Subtitle,Language,Document Type,
Conference Title,Conference Date,Conference Location,Conference Sponsors,
Conference Host,Author Keywords,Keywords Plus,Abstract,Author Address,Reprint Address,
E-mail Address,ResearcherID Number,ORCID Identifier (Open Researcher and Contributor ID),
Funding Agency and Grant Number,Funding Text,Cited References,Cited Reference Count,
Web of Science Core Collection Times Cited Count,Total Times Cited Count 
(Web of Science Core Collection; BIOSIS Citation Index; Chinese Science Citation Database;
Data Citation Index; Russian Science Citation Index; SciELO Citation Index),
Usage Count (Last 180 Days),Usage Count (Since 2013),Publisher,Publisher City,Publisher Address,
International Standard Serial Number (ISSN),Electronic International Standard Serial Number (eISSN),
International Standard Book Number (ISBN),29-Character Source Abbreviation,
ISO Source Abbreviation,Publication Date,Year Published,Volume,Issue,Special Issue,Part Number,
Supplement,Meeting Abstract,Beginning Page,Ending Page,Article Number,Digital Object Identifier (DOI),
Book Digital Object Identifier (DOI),Early access date,Early access year,Page Count,
Chapter Count (Book Citation Index),Web of Science Categories,Research Areas,Document Delivery Number,
PubMed ID,Accession Number,Open Access Indicator,ESI Hot Paper. Note that this field is valued only for subscribers.,
ESI Highly Cited Paper. Note that this field is valued only for ESI subscribers.,
Date this report was generated.,End of Record,End of File'''
# WOS_TAGS_DICT unused
WOS_TAGS_DICT = dict(zip([x.strip() for x in WOS_TAGS.split(',')],
                         [x.strip() for x in WOS_TAGS_VALUES.split(',')]))

# SCOPUS_TAGS unused
SCOPUS_TAGS = '''Authors,Title,Year,Source title,Volume,Issue,Art. No.,
Page start,Page end,Page count,Cited by,DOI,Link,Affiliations,
Authors with affiliations,Abstract,Author Keywords,Index Keywords,References,
ISSN,ISBN,CODEN,Language of Original Document,Abbreviated Source Title,
Document Type,Source,EID'''
SCOPUS_TAGS = [x.strip() for x in SCOPUS_TAGS.split(',')]



   