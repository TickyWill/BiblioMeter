"""The `BiblioDescription` module is a set of functions useful for a bibliographic corpus description.
   More specifically, the frequency occurence of the item values is computed for each of the parsing items.
         
"""

__all__ = ['describe_corpus', 
           'plot_graph', 
           'plot_counts', 
           'plot_histo',
           'treemap_item']

# Globals used from BiblioAnalysis_Utils.BiblioSpecificGlobals: COOC_NETWORKS_FILE, DIC_OUTDIR_PARSING, 
#                                                               DIC_OUTDIR_DESCRIPTION, DISTRIBS_ITEM_FILE,
#                                                               LABEL_MEANING, NAME_MEANING, NMAX_NODES,
#                                                               VALID_LABEL_GRAPH


def _frequency_analysis(df,corpus_size):

    '''The '_frequency_analysis' function builds the dataframe "df_freq" and the arrays "q_item" and "p_item" from the dataframe "df".
    The dataframe "df" consists in two columns named "pub_id" and "item":

     ex_a:              pub_id   item
                    0     0     item_a
                    1     0     item_b
                    2     1     item_c
                    3     2     item_a

    The dataframe "df_freq" consists in three columns named "pub_id" "item" and "f" as (for ex_a):

                        item   count    f
                    0  item_a    2      50
                    1  item_b    1      25
                    2  item_c    1      25

    where : "count" is the total number of occurrence of the item (ex_a: count=2 for item_a )
            "f" is the frequency occurrence (100*count/total number of items) (ex_a: f=50% for item_a )

    "q_item" is array of two arrays: [array1,array2] where:
        array1 = [list of possible number of items per articles] = [#item1, #item2,..]
        array2 = [number of articles with a number of items #item1,
                  number of articles with a number of items #item2,...]
    for ex_a we have: [[1,2],[2,1]]

    "p_item" is an array of two arrays: [array1,array2] where:
        array1 = [list of possible number of occurrences of an item in the articles corpus ] = [#1, #2,..]
        array2 = [number of articles with a number of items #1, #2,...]
    for ex_a we have: [[1,2],[4,2]]

    '''
    # Standard library imports
    import itertools
    import operator
    
    #df_freq = df.groupby('item').count().reset_index()
    df_freq = df.drop_duplicates().groupby('item').count().reset_index()   #!!!!!!!!!!!!!
    df_freq.sort_values(by=['pub_id'],ascending=False,inplace=True)
    #df_freq['f'] = df_freq['pub_id']/len(df)*100 # old fashion of freq calculation
    df_freq['f'] = df_freq['pub_id']/corpus_size*100
    df_freq.columns = ['item','count','f']
    
    df_freq_stat = df.drop_duplicates().\
                      groupby('pub_id').count().reset_index().\
                      groupby('item').count().reset_index()
    q_item = [df_freq_stat['item'] .astype(int).to_list(),df_freq_stat['pub_id'].to_list()]

    df_freq_stat = df.drop_duplicates().\
                      groupby('item').count().reset_index().\
                      groupby('pub_id').count().reset_index()
    
    freq_item = df_freq_stat['item'].to_list()
    p_item = [df_freq_stat['pub_id'].to_list(),
             [k for k in itertools.accumulate([sum(freq_item)]+freq_item,operator.isub)][:-1]]
    
    del df_freq_stat
    return df_freq, q_item, p_item


def _generate_cooc(df,item):

    '''Builds a cooccurence undirected graph (N,V) where:
            - the set N of nodes is the set of the NMAX_NODES prominent items in term of occurrence
       frequency (by default NMAX_NODES=100)
            - the set of edges connecting two items sitting in the the same article

        As input we use the dataframe "df" which consists in two columns named "pub_id" and "item":

     ex_a:              pub_id   item
                    0     0     item_a
                    1     0     item_b
                    2     1     item_c
                    3     2     item_a

       Args:

    '''

    # Standard library imports
    from collections import defaultdict
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import NMAX_NODES

    #                           Builds nodes
    #----------------------------------------------------------------------------
    liste_node = []
    dict_node={}
    dg = df.groupby('item').count()\
                      .reset_index()\
                      .sort_values(by='pub_id',ascending=False)\
                      .iloc[:NMAX_NODES,:] # Selects the n most prominent items
                                           # in term of rate occurrence

    for node,x in enumerate(dg.iterrows()):
        dict_node[x[1]['item']] = node
        liste_node.append({'type':item,
                           'name':node,
                           'item':x[1]['item'],
                           'size':x[1]['pub_id']})

    #                           Builds edges
    #----------------------------------------------------------------------------
    dic_item_to_keep = {}
    comm = defaultdict(int)

    item_to_keep = set(dg['item'].to_list()) # Buils the n-top list of the n items
                                             # with the higher occurrence rate

    for x in df.groupby('pub_id')['item']:   # For each article, keeps items in the n-top list
        item_publi = set(x[1].to_list())
        item_publi_to_keep = item_publi.intersection(item_to_keep)
        if len(item_publi_to_keep):
            dic_item_to_keep[x[0]] = item_publi_to_keep


    for item_to_keep in dic_item_to_keep.values() : # Builds a edge between two items if
                                                    # there are are in the same article item list
        for source in item_to_keep:
            for target in [x for x in item_to_keep if x > source]:
                comm[source,target] += 1

    liste_edge = []
    for edge,weight in comm.items():
        liste_edge.append({'type':item,
                           'source':dict_node[edge[0]],
                           'target':dict_node[edge[1]],
                           'Ncooc':weight})
    
    del dict_node, dg, dic_item_to_keep
    return liste_node, liste_edge


def _describe_item(df,item,dic_distrib_item,list_cooc_nodes,list_cooc_edges ,freq_filename):

    '''Builds the dataframe "df_freq" and the arrays "q_item" and "p_item for :
    item = 'AU','AK','CU', 'DT', 'I', 'J', 'IK', 'LA', 'R', 'RJ', 'S', 'S2', 'TK', 'Y'
       Builds the coocurence undirected graph
    item = 'AU', 'CU', 'S', 'S2', 'K', 'R', 'RJ', 'I', 'AK', 'TK'
    '''
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import VALID_LABEL_GRAPH
    
    # Deal with .csv files
    corpus_size = dic_distrib_item['N']  #Retrieve the corpus size from the json dict
    df.columns = ['pub_id','item']
    df_freq, q_item, p_item = _frequency_analysis(df,corpus_size)
    df_freq.to_csv(freq_filename,sep=',', index = False)
     
    # Upgrades the json dict used to build DISTRIBS_itemuse.json file
    dic_distrib_item['q'+item.capitalize()] = q_item
    dic_distrib_item['p'+item.capitalize()] = p_item

    # Upgrades the list of nodes and edges of the coocurrence graph
    if item in VALID_LABEL_GRAPH:
        liste_node, liste_edge = _generate_cooc(df,item)

        list_cooc_nodes.extend(liste_node)
        list_cooc_edges.extend(liste_edge)
    
    del df_freq, q_item, p_item

    
def _process_article(in_dir, out_dir, usecols, dic_distrib_item, list_cooc_nodes, list_cooc_edges):
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_DESCRIPTION
    
    try:
        df_articles = pd.read_csv(in_dir/Path(DIC_OUTDIR_PARSING['A']),
                                  sep='\t',
                                  usecols=usecols)

        dic_distrib_item['N'] = len(df_articles)

        item = 'Y'                       # Deals with years
        _describe_item(df_articles[[usecols[0],usecols[1]]],
                       item,
                       dic_distrib_item,
                       list_cooc_nodes,
                       list_cooc_edges,
                       out_dir/Path(DIC_OUTDIR_DESCRIPTION[item]))

        item = 'J'                     # Deals with journals title (ex: PHYSICAL REVIEW B)
        _describe_item(df_articles[[usecols[0],usecols[2]]],
                      item,
                      dic_distrib_item,
                      list_cooc_nodes,
                      list_cooc_edges,
                      out_dir/Path(DIC_OUTDIR_DESCRIPTION[item]))

        item = 'DT'                    # Deal with doc type (ex: article, review)
        _describe_item(df_articles[[usecols[0],usecols[3]]],
                      item,
                      dic_distrib_item,
                      list_cooc_nodes,
                      list_cooc_edges,
                      out_dir/Path(DIC_OUTDIR_DESCRIPTION[item]))

        item = 'LA'                   # Deal with language
        _describe_item(df_articles[[usecols[0],usecols[4]]],
                      item,
                      dic_distrib_item,
                      list_cooc_nodes,
                      list_cooc_edges,
                      out_dir/Path(DIC_OUTDIR_DESCRIPTION[item]))
        del df_articles
    except pd.errors.EmptyDataError:
        print(f'Note: file {DIC_OUTDIR_PARSING["A"]} was empty. Skipping')
            
        
def _process_references(in_dir, out_dir, usecols, dic_distrib_item, list_cooc_nodes, list_cooc_edges):
    
    # Standard library imports
    import re
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_DESCRIPTION
    
    try:
        item ='R'
        find_0 = re.compile(r',\s?0')
        df = pd.read_csv(in_dir / Path(DIC_OUTDIR_PARSING[item]),
                         sep='\t',
                         usecols=usecols).astype(str)
        

        df['ref'] = df.apply(lambda row:re.sub(find_0,'', ', '.join(row[1:-1]))
                                     ,axis=1)
                         
        _describe_item(df[[usecols[0],'ref']],
                      item,
                      dic_distrib_item,
                      list_cooc_nodes,
                      list_cooc_edges,
                      out_dir/Path(DIC_OUTDIR_DESCRIPTION[item]))
                         
        item = 'RJ'
        _describe_item(df[[usecols[0],usecols[3]]],
                      item,
                      dic_distrib_item,
                      list_cooc_nodes,
                      list_cooc_edges,
                      out_dir/Path(DIC_OUTDIR_DESCRIPTION[item]))

        del df    
    
    except pd.errors.EmptyDataError:
        print(f'Note: file {DIC_OUTDIR_PARSING["R"]} was empty. Skipping')
  

def _process_item(in_dir, out_dir, item, usecols, dic_distrib_item, list_cooc_nodes, list_cooc_edges):
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_DESCRIPTION
    
    try:
        df = pd.read_csv(in_dir / Path(DIC_OUTDIR_PARSING[item]),
                         sep='\t',
                         usecols=usecols)
        _describe_item(df,
                      item,
                      dic_distrib_item,
                      list_cooc_nodes,
                      list_cooc_edges,
                      out_dir/Path(DIC_OUTDIR_DESCRIPTION[item]))
        del df
        
    except pd.errors.EmptyDataError:
        print(f'Note: file {DIC_OUTDIR_PARSING[item]} was empty. Skipping') 

        
def describe_corpus(in_dir, out_dir, database_type, verbose):

    '''Using the files xxxx.dat generated by the parsing function biblio_parser and stored in
    the folder parsing, the function describe_corpus generates the files freq_xxxx.dat and
    two .json files. These new files are stored in the folder freq.
    home path//BiblioAnalysis Data/
    |-- myprojectname/
    |   |-- freq/
    |   |   |-- COOC_NETWORKS_FILE, DISTRIBS_ITEM_FILE 
    |   |   |-- freq_authors.dat, freq_authorskeywords.dat, freq_countries.dat
    |   |   |-- freq_doctypes.dat, freq_institutions.dat, freq_journals.dat
    |   |   |-- freq_keywords.dat, freq_languages.dat, freq_references.dat
    |   |   |-- freq_refjournals.dat, freq_subjects.dat, freq_subjects2.dat
    |   |   |-- freq_titlewords.dat, freq_years.dat
    |   |-- parsing/
    |   |   |-- addresses.dat, articles.dat, authors.dat, countries.dat, database.dat
    |   |   |-- institutions.dat, keywords.dat, references.dat, subjects.dat, subjects2.dat
    
    the json file coocnetworks.json is structured as follow:

        {
        "nodes":[
            {"type":"AU","name":0,"item":"Abanades S","size":8},
            ...................................................
        ],
        "links":[
            {"type":"AU","source":0,"target":8,"Ncooc":5},
            ..............................................
        ]
        }

    where type = "AU", "S", "I", "CU", "S2", "IK", "AK", "TK", "R", "RJ"

    '''

    # Standard library imports
    import json
    from pathlib import Path
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COOC_NETWORKS_FILE
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DISTRIBS_ITEM_FILE
    
    dic_distrib_item = {}
    list_cooc_nodes = []   # Only one .json file is used to describe all the graph
    list_cooc_edges = []   # these list are extended at each call of _describe_item function

    #with open(in_dir/Path('database.dat' ), 'r') as file:  # read the database type wos/scopus  
        #dic_distrib_item['database'] = file.read().strip('\n')
    dic_distrib_item['database'] = database_type  

    # Deals with years, journals title, doc type and language
    usecols = [COL_NAMES['articles'][i] for i in [0,2,3,7,8]]
    _process_article(in_dir, out_dir, usecols, dic_distrib_item, list_cooc_nodes, list_cooc_edges)
    corpus_size = dic_distrib_item['N']
        
    item = 'AU'                   # Deals with authors
    usecols = [COL_NAMES['authors'][0],COL_NAMES['authors'][2]] #ex: ['pub_id','co_author']
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)
    
    usecols = [COL_NAMES['keywords'][0],COL_NAMES['keywords'][1]] #ex: ['pub_id','keyword']
    item = 'AK'                   # Deals with authors keywords
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)
    item = 'IK'                   # Deals journal keywords
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)
    item = 'TK'                   # Deals with title keywords
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)
   
    item = 'CU'                   # Deals with countries
    usecols = [COL_NAMES['country'][0],COL_NAMES['country'][2]] #ex: ['pub_id','country']
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)
    
    item = 'I'                    # Deals with institutions
    usecols = [COL_NAMES['institution'][0],COL_NAMES['institution'][2]] #ex: ['pub_id','institution']
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)

    item = 'S'                    # Deals with subjects
    usecols = [COL_NAMES['subject'][0],COL_NAMES['subject'][1]] #ex: ['pub_id','subject']
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)

    item = 'S2'                   # Deals with subject2
    usecols = [COL_NAMES['sub_subject'][0],COL_NAMES['sub_subject'][1]] #ex: ['pub_id','sub_subject']
    _process_item(in_dir, out_dir,item,usecols,dic_distrib_item,list_cooc_nodes,list_cooc_edges)

    # Deals with references
    usecols = [COL_NAMES['references'][i] for i in range(0,6)]
    _process_references(in_dir, out_dir, usecols, dic_distrib_item, list_cooc_nodes, list_cooc_edges)
    
    #                    creates two json files
    #---------------------------------------------------------------------
    with open(out_dir / Path(DISTRIBS_ITEM_FILE),'w') as file:
        json.dump(dic_distrib_item,file,indent=4)

    dic_cooc = {}
    dic_cooc['nodes'] = list_cooc_nodes
    dic_cooc['links'] = list_cooc_edges
    with open(out_dir / Path(COOC_NETWORKS_FILE),'w') as file:
        json.dump(dic_cooc,file,indent=4)

        
def plot_graph(in_dir,item):

    '''plot the communities graph which nodes and edges are extracted from
    the json file coocnetworks.json built by the function describe_corpus:

        {
        "nodes":[
            {"type":"AU","name":0,"item":"Abanades S","size":8},
            ...................................................
        ],
        "links":[
            {"type":"AU","source":0,"target":8,"Ncooc":5},
            ..............................................
        ]
        }

    where type = "AU", "S", "I", "CU", "S2", "IK", "AK", "TK", "R", "RJ"
    
    Returns the graph G.
    '''

    # Standard library imports
    import json
    import pprint
    from pathlib import Path
    
    # 3rd party imports
    import community as community_louvain
    import matplotlib.cm as cm
    import matplotlib.pyplot as plt
    import networkx as nx
    import numpy as np
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import LABEL_MEANING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import VALID_LABEL_GRAPH


    assert (item in VALID_LABEL_GRAPH),\
            f'unknown type {TYPE}: should be {", ".join(VALID_LABEL_GRAPH)}'

    # Extract nodes and edgesSets the graph  from the json coocnetworks.json
    # for type=TYPE
    # -----------------------------------------------------------
    file_coocnetworks = in_dir / Path('coocnetworks.json')
    with open(file_coocnetworks, 'r') as read_file:
                cooc = json.load(read_file)

    df = pd.DataFrame( cooc['links']).query('type==@item')
    G = nx.from_pandas_edgelist(df,source='source',target='target' )
    dg = pd.DataFrame(cooc['nodes']).query('type==@item')
    G.add_nodes_from(dg['name'])
    for index, row in dg.iterrows():
        src_attr_dict = {k: row.to_dict()[k] for k in ['item','size']}
        G.nodes[row['name']].update(src_attr_dict)

    # compute the best partition
    partition = community_louvain.best_partition(G)
    nx.set_node_attributes(G,partition,'community_id')

    # draw the graph
    pos = nx.spring_layout(G)
    node_size = np.array(list(nx.get_node_attributes(G,'size').values()))*70
    cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
    fig = plt.figure(figsize=(15,15))
    nx.draw_networkx_nodes(G, pos, partition.keys(), node_size=node_size,
                           cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_edges(G, pos, alpha=0.9,width=1.5, edge_color='k', style='solid',)

    labels = nx.draw_networkx_labels(G,pos=pos,font_size=8,
                                   font_color='w')

    plt.title(f'Graph partition using the {LABEL_MEANING[item]} and the Louvain algorithm')
    plt.show()

    node = nx.get_node_attributes(G,'item')
    pprint.pprint(node)

    df = pd.DataFrame({node_id:[num_partition, node[node_id] ]
                       for node_id,num_partition in partition.items()}).T

    for g in df.groupby([0]):
        print(f'N° partition:{g[0]}, items: {g[1][1].to_list()}')
    
    del df, dg, src_attr_dict, partition, labels, node
    
    return G


def plot_counts(item_counts, file_name_counts):

    '''Plots a distribution curve from the frequency analysis .
    The data are extracted from the freq_xxxx.dat files 
    built by the funtion describe_corpus
    '''
    
    # 3rd party imports
    import matplotlib.pyplot as plt
    import pandas as pd
    
    df = pd.read_csv(file_name_counts, sep= ',')

    #        Scatter plot 
    #------------------------------------------------------
    fig = plt.figure(figsize=(15,7))
    plt.scatter(df['item'], df['count'] )
    plt.xticks([])
    plt.show()

    
def plot_histo(item_label, file_distrib_item):

    '''Plots the histograms of the p and q statistics (see _frequency_analysis function for more details).
    The data are extracted from the json file DISTRIBS_itemuse.json
    built by the funtion describe_corpus
    '''

    # Standard library imports
    import json
    
    # 3rd party imports
    import matplotlib.pyplot as plt
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import LABEL_MEANING
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import NAME_MEANING

    #file_distrib_item = in_dir / Path('DISTRIBS_itemuse.json')
    with open(file_distrib_item, 'r') as read_file:
                    distrib_item = json.load(read_file)
    
    # Convert item label in acronyme using the global dictionary ACRONYME_MEANING
    item = NAME_MEANING[item_label]
    
    #        Plots the q histogram
    #------------------------------------------------------
    q = distrib_item['q' + item.capitalize()]
    print('q',q)
    xmin=q[0][0]-0.5
    xmax= q[0][len(q[0])-1]+0.5
    fig = plt.figure(figsize=(15,7))
    plt.subplot(1,2,1)
    _ =plt.bar(q[0], q[1] , width=0.8, bottom=None)
    plt.xlim(xmin,xmax)
    plt.xlabel(f'Number of {LABEL_MEANING[item]} / Article')
    plt.ylabel(f'Number of articles')
    plt.title(f'{LABEL_MEANING[item]} histogram')

    #        Plots the p histogram
    #------------------------------------------------------
    p = distrib_item['p' + item.capitalize()]
    print('p',p)
    xmin=p[0][0]-0.5
    xmax= p[0][len(p[0])-1]+0.5
    plt.subplot(1,2,2)
    _ = plt.bar(p[0], p[1] , width=0.8, bottom=None)
    plt.xlim(xmin,xmax)
    plt.xlabel(f'Number of articles / {LABEL_MEANING[item]}')
    plt.ylabel(f'Number of {LABEL_MEANING[item]}')
    plt.title(f'{LABEL_MEANING[item]} histogram')
    plt.show()

    
def treemap_item(item_treemap, file_name_treemap):

    # 3rd party imports
    import matplotlib.pyplot as plt
    import pandas as pd
    import squarify    # algorithm for treemap
    from matplotlib import cm
    from matplotlib import colors
        
    df = pd.read_csv(file_name_treemap, sep= ',')
    all_labels = list(df['item'])
    all_sizes = list(df['count'])
    all_freqs = list(df['f'])
    total_size = len(all_sizes)
    if total_size != 0 : 
        
        request = "Enter the number of items to be used for the treemap " + \
                  "(min = 1, max = " + str(total_size) + "): "
        size_limit = int(input(request))      
        labels = all_labels[0:size_limit]
        sizes = all_sizes[0:size_limit]
        freqs = all_freqs[0:size_limit]
        all_alias = [str(i) for i in range(len(labels))]
        alias = all_alias[0:size_limit]
    
        fig = plt.gcf()
        ax = fig.add_subplot()
        fig.set_size_inches(10, 8)
        norm = colors.Normalize(vmin=min(sizes), vmax=max(sizes))
        colors = [cm.viridis(norm(value)) for value in sizes]
        squarify.plot(sizes=sizes, label=alias, alpha=1, color = colors)
        plt.axis('off')
        plt.title('Frequences for the top '+ str(size_limit) + ' ' + item_treemap + ' out of ' + \
                   str(total_size),fontsize=23,fontweight='bold')
        plt.show()
    
        print(f'{"alias":<6}{item_treemap:<60}{"counts":<8}{"freq"}')
        for i in range(0, len(alias)):
            print(f'{alias[i]:<6}{labels[i]:<60}{sizes[i]:<8}{round(freqs[i],3)}')
        
        del sizes, all_labels, labels, all_alias, alias
    else:
        print('The selected item is empty')

    del df, all_sizes, 