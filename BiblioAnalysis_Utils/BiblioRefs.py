'''This module permits to build the two files required for the categories identification of the corpus articles
using the scopus database. Beforehand one should download an .xls file as indicated in "scopus_journals_issn_cat"
function.
'''
__all__ = ['create_scopus_cat_codes','scopus_journals_issn_cat']

SCOPUS_JOURNAL_LIST = 'scopus-journal-list-download.xlsx'
SCOPUS_XLS_SHEET_NAME = 'Scopus Sources October 2020'


def create_scopus_cat_codes():
    
    # 3rd party imports
    import requests 
    import pandas as pd
    from bs4 import BeautifulSoup 
    
    URL =  'https://service.elsevier.com/app/answers/detail/a_id/15181/supporthub/scopus/related/1/session/'
    URL += 'L2F2LzEvdGltZS8xNjE5MzMwNzQyL2dlbi8xNjE5MzMwNzQyL3NpZC9mVWt2WEdTNmNDdVIwZU5Da2dVU3JNOFNmbHA4NVUlN0Vxaj'
    URL += 'hoWHpqUWsxY2pBSlVZWUFoRmxOUWhBNUZpOVFMbVZuU2JNMEF0Q2w3NzB2cHg0aWxCdEJoaFZEWCU3RUVxNDNaRXdvSnVvX2dLRTd3'
    URL += 'a3l6RE9aajdKQ3pnJTIxJTIx/'

    page = requests.get(URL).text

    soup = BeautifulSoup(page,'lxml')
    rep = [p.text for p in soup.find(class_="order-table table-bordered table-hover table-striped").find_all('p')]
    df_code = pd.DataFrame(zip( rep[1::3], rep[::3]),columns=['Field','Code'])
    
    return df_code

def scopus_journals_issn_cat(root):
    
    '''
    Download the file SCOPUS_JOURNAL_LIST (default: "scopus-journal-list-download.xlsx") from the url "URL" 
    '''
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    URL = 'https://www.scopusjournals.com/p/redirect.html?&url=https:'
    URL +=  '//www.internauka.org/sites/default/files/scopus/' + SCOPUS_JOURNAL_LIST
        
    df = pd.read_excel(root / Path('Downloads') / Path(SCOPUS_JOURNAL_LIST),
                       sheet_name= SCOPUS_XLS_SHEET_NAME,
                       usecols = 'B,C,X')

    return df