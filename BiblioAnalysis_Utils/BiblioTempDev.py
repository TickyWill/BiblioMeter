__all__ = ['temporaldev_itemvalues_freq','read_config_temporaldev','write_config_temporaldev','temporaldev_result_toxlsx']

#Globals imported from BiblioAnalysis_Utils.BiblioSpecificGlobals: DIC_OUTDIR_DESCRIPTION

def temporaldev_itemvalues_freq(keyword_filters ,items, years, corpuses_folder):
    
    '''
    Make a list of named tuple [('item','keyword','data_frame','freq','year','mode'),...]
    with:
        'item' in the list "items". Ex: items=['IK','AK',TK]
        'keyword' in the list keyword_filters.values where:
            keyword_filters is a dict {mode:[keyword1,keyword2,...],...} with mode='is_in'or 'is_equal'
        'data_frame' the dataframe of the frequency occurrences of keywords
        containing (or equal) to 'keyword')
    '''
    # Standard library imports
    import re
    from collections import namedtuple
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_DESCRIPTION

    def _filter(df,keyword_filter,mode):
        
        '''Builds the dataframe dg out of the dataframe df by selecting 
        the df rows such that the "item" column :
            - contains the keyword "keyword_filter" if mode="is_in"
            - is equal to "keyword_filter" elsewhere 
        '''

        if mode == 'is_in':
            dg = df[df['item'].str.contains(keyword_filter)]
        else:
            dg = df.loc[df['item']==keyword_filter]
        return dg

    keyword_filter_tuple = namedtuple('keyword_filter_list',['item','keyword','data_frame','freq','year','mode'] )
    keyword_filter_list = []
    for file_year in years:
        year = int(re.findall('\d{4}', file_year )[0])
        for item in items:
            file_kw = DIC_OUTDIR_DESCRIPTION[item]
            file = corpuses_folder / Path(file_year) / Path('freq') / Path(file_kw)
            try:
                df = pd.read_csv(file)
            except:
                print(f"Warning no such file {file}")
                pass
            for mode,keyword_filter_all in keyword_filters.items():
                for keyword_filter in keyword_filter_all:
                    df_filter = _filter(df,keyword_filter,mode)
                    keyword_filter_list.append(keyword_filter_tuple(item=item,
                                                                   keyword=keyword_filter,
                                                                   data_frame=df_filter,
                                                                   freq=sum(df_filter['f']),
                                                                   year=year,
                                                                   mode=mode))
    return keyword_filter_list

def read_config_temporaldev(file_config):
    """
    Parse json file to build the keywords configuration for temporal analysis of corpuses
    
    Args:
        file_config (Path): absolute path of the configuration file
       
    Returns:
        items (list of strings): selected items for the analysis among ['IK', 'AK', 'TK', 'S', 'S2']
        keywords (dict): {"is_in": list of selected strings,
                          "is_equal": list of keywords}
    """
    # Standard library imports
    import json
    from collections import defaultdict

    keywords = defaultdict(list)

    with open(file_config, "r") as read_file:
            config_temporal = json.load(read_file)

    items = config_temporal ["items"]

    for key, value in config_temporal.items():
        keywords[key] = value

    return items,keywords

def write_config_temporaldev(file_config,items,keywords):
    """
    Store the keywords configuration for temporal analysis of corpuses in ajson file
    
    Args:
        file_config (path): absolute path of the configuration file
        keyword_filters (dict): { "is_in": list of selected strings,
                                  "is_equal": list of keywords}
        items (list of strings): selected items for the analysis among ['IK', 'AK', 'TK', 'S', 'S2']

    """
    # Standard library imports
    import json

    config_temporal = {}
    config_temporal ["items"] = items
    for key, value in keywords.items(): 
        config_temporal [key] = value
    
    with open(file_config,'w') as write_file:
            config_temporal = json.dump(config_temporal,write_file,indent = 4)
            
def temporaldev_result_toxlsx(keyword_filter_list,store_file):
    # Standard library imports
    import numpy as np

    # 3rd party imports
    import pandas as pd

    # Building a dict from each tupple of the keyword_filter_list list 
    # to append the dataframe dg with the dict
    res={}
    flag = True
    for i in range(0,len(keyword_filter_list)):
        res['Corpus year']=keyword_filter_list[i].year
        res['Item'] = keyword_filter_list[i].item
        res['Search word'] = keyword_filter_list[i].keyword
        res['Weight'] = (round(keyword_filter_list[i].freq,3))
        res['Search mode'] = keyword_filter_list[i].mode
        df = keyword_filter_list[i].data_frame
        res['Item-values list'] = [np.array(df['item']).flatten()]

        # flush dict into a data frame 
        if flag: # first round we create a new data frame
            flag = False
            dg = pd.DataFrame.from_dict(res, orient='columns') 
        else: # we append to the existing data frame
            dg = dg.append(pd.DataFrame.from_dict(res),ignore_index=True)

    # flush the built dataframe dg into an excel file
    writer = pd.ExcelWriter(store_file, engine='openpyxl')
    dg.to_excel(writer, sheet_name = 'Results')
    writer.save()
    writer.close()
