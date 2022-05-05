"""The `BiblioCoupling` module is a set of functions useful for articles coupling analysis
   in a bibliographic corpus.
   More specifically, a coupling graph `G(nodes, edges)` is generated where:
       - the nodes are the articles of the corpus with predefined attributes 
         and interactively defined attributes;
       - the edges connect two articles when they share at least a minimum number of refererences.
         The edge attributes are the number of shared references and the Kessler similarity.
         
"""

__all__ = ['build_coupling_graph',
           'build_louvain_partition',
           'plot_coupling_graph',
           'save_communities_xls',
           'save_graph_gexf',
           'add_item_attribute',]

# Globals used from BiblioAnalysis_Utils.BiblioSpecificGlobals: COUPL_AUTHORIZED_ITEMS,
#                                                               COUPL_FILENAME_GEXF,
#                                                               COUPL_FILENAME_XLSX, 
#                                                               COUPL_GLOBAL_VALUES,
#                                                               DIC_OUTDIR_DESCRIPTION,
#                                                               DIC_OUTDIR_PARSING 


def build_coupling_graph(in_dir):
    
    '''The "build_coupling_graph" function builds a corpus coupling graph G(N,E) where:
            - N is the set of nodes with two attributes: article ID and number of references
            - E is the set of edges. An edge links two articles if and only if:
                   (i)   they share at least "BCTHR" references
                   (ii)  each article has at least "NRTHR" references
                   (iii) their Kessler similarity w_ij is >= "WTHR"
              An edge has two attributes: number of shared references 
                                          and the Kessler similarity     
       The Kessler similarity is defined as: 
                       
                  # of common references between pub_id_i and pub_id_j
         w_ij = ---------------------------------------------------------
                sqrt(# references of pub_id_i * # references of pub_id_j)
                                 
       Args:
           in_dir (Path): folder path of the corpus parsed files generated 
                          by the BiblioParsingWos module or the BiblioParsingScopus module.
       
       Returns:
           G (networkx object): corpus coupling graph.
        
    '''
     
    # Standard library import
    from collections import defaultdict
    from more_itertools import distinct_combinations
    from pathlib import Path
    
    # 3rd party import
    import math
    import networkx as nx
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COUPL_GLOBAL_VALUES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
        
    BCTHR = COUPL_GLOBAL_VALUES['BCTHR']
    RTUTHR = COUPL_GLOBAL_VALUES['RTUTHR']
    WTHR = COUPL_GLOBAL_VALUES['WTHR']
    NRTHR = COUPL_GLOBAL_VALUES['NRTHR']
    
    pub_id_alias = COL_NAMES['articles'][0]
    author_alias = COL_NAMES['articles'][1]
    year_alias = COL_NAMES['articles'][2]
    journal_alias = COL_NAMES['articles'][3]
    author_ref_alias = COL_NAMES['references'][1]
    
    # The references and their ids are extracted from the file articles.dat (tsv format)
    # ---------------------------------------------------------------------------------------

    # TO DO: set columns by names
    usecols = [COL_NAMES['articles'][i] for i in [0,1,2,3,4,5]]
    df_article = pd.read_csv(in_dir / Path(DIC_OUTDIR_PARSING['A']),
                 sep='\t',
                 usecols=usecols).fillna(0).astype(str)

    table_art = df_article.apply(lambda row : ', '.join(row[1:]),axis=1) # Builds article: "pub_id, author, year, journal, volume, page"
                                                                         # ex:"6354, Name S., 2004, SCIENCE, 306, 496"
    table_art = [x.replace(', 0','') for x in table_art] # takes care of the unknown volume and/or page number
                                                         # ex: "6354, Name S., 2010, THESIS"
    df_article['label_article'] = table_art

    df_article[pub_id_alias] = pd.to_numeric(df_article[pub_id_alias])



    # 1- Creates the dict named ref_table = {ref A: [list of article id (pub_id) citing ref A]}
    # ex : ref_table = {'Bellouard Q, 2017, INT. J. HYDROG. ENERGY, 42, 13486': [0, 50],...}
    # 2- creates the dict named nR = {pub_id: number of references of pub_id}
    # ---------------------------------------------------------------------------------------

    usecols = [COL_NAMES['references'][i] for i in [0,1,2,3,4,5]]
    df_reference = pd.read_csv(in_dir / Path(DIC_OUTDIR_PARSING['R']),
                               sep='\t',
                               usecols=usecols,
                               na_filter=False).astype(str)
    #df_reference.columns = ['pub_id','first_author','year','journal','volume','page']

    table = df_reference.apply(lambda row : ", ".join(row[1:]), axis=1) # Builds ref: "pub_id, author, year, journal, volume, page"
                                                                         # ex:"6354, Name S., 2004, SCIENCE, 306, 496"
    table = [x.replace(', 0','') for x in table] # takes care of the unknown volume and/or page number
                                                 # ex: "6354, Name S., 2010, THESIS"
    df_reference['label_ref'] = table

    df_reference[pub_id_alias] = pd.to_numeric(df_reference[pub_id_alias])

    nR = df_reference.groupby(pub_id_alias).count().to_dict()[author_ref_alias]

    ref_table = {x[0]:x[1].tolist() for x in df_reference.groupby('label_ref')[pub_id_alias]}


    # Builds the dict of dicts BC_table such as:
    #   BC_table = {pub_id_i:{pub_id_j: number of common references of pub_id_i and pub_id_j,...},...}
    # ex : BC_table = {0: {50: 8, 55: 2, 121: 2, 10: 2},...}
    #   pub_id 0 has 8 common references with pub_id 50; pub_id 0 has 2 common references with pub_id 55
    #----------------------------------------------------------------------------------------------

    BC_table = {}
    for reference in ref_table:
        if len(ref_table[reference]) >= RTUTHR:  # The reference is cited more than RTUTHR-1 times
            for pub_id_i,pub_id_j  in distinct_combinations(ref_table[reference], 2):
                if pub_id_i not in BC_table:
                    BC_table[pub_id_i] = dict()
                if pub_id_j not in BC_table[pub_id_i]:
                    BC_table[pub_id_i][pub_id_j] = 0
                BC_table[pub_id_i][pub_id_j] += 1   
                
    # Builds the graph netwokx objet G with edge atributes:
    #    1-   the Kessler similarity  w_ij
    #    2-   the number of common references between pub_id_i and pub_id_j                                 
    #----------------------------------------------------------------------------------------------

    G = nx.Graph()
    for pub_id_i in BC_table:
        for pub_id_j in BC_table[pub_id_i]:
            w_ij = (1.0 * BC_table[pub_id_i][pub_id_j]) \
                   / math.sqrt(nR[pub_id_i] * nR[pub_id_j]) # Kessler similarity
            if (
                (BC_table[pub_id_i][pub_id_j] >= BCTHR) # Number of common references 
                                                        #   between id_i and id_j>=BCTHR
                and (nR[pub_id_i] >= NRTHR)             # Number of references of id_i>=NRTHR (default=1)
                and (nR[pub_id_j] >= NRTHR)             # Number of references of id_j>=NRTHR (default=1)
                and (w_ij >= WTHR)                      # Kessler similarity >=WTHR (default=0)
            ):
                G.add_edge(pub_id_i, pub_id_j, weight=w_ij, nc=BC_table[pub_id_i][pub_id_j])
    
    nx.set_node_attributes(G,nR,'nbr_references')
    
    node_label = {x:df_article.loc[df_article[pub_id_alias] == x,'label_article'].tolist()[0] for x in G.nodes}
    nx.set_node_attributes(G,node_label,'label')
    
    node_first_author = {x:df_article.loc[df_article[pub_id_alias] == x,author_alias].tolist()[0] for x in G.nodes}
    nx.set_node_attributes(G,node_first_author,'first_author')
    
    node_year = {x:df_article.loc[df_article[pub_id_alias] == x,year_alias].tolist()[0] for x in G.nodes}
    nx.set_node_attributes(G,node_year,'year')
    
    node_journal = {x:df_article.loc[df_article[pub_id_alias] == x,journal_alias].tolist()[0] for x in G.nodes}
    nx.set_node_attributes(G,node_journal,'journal')

    return G


def build_louvain_partition(G):
    
    '''The "build_louvain_partition" function computes corpus-coupling-graph G partition
       into communities using the Louvain algorithm, 
       (see https://buildmedia.readthedocs.org/media/pdf/python-louvain/latest/python-louvain.pdf).
       The attribute community is added to the nodes of the graph G.
       
       Args:
           G (networkx object): initial corpus coupling graph.
       
       Returns:
           louvain_part (namedtuple): 
               louvain_part.G (networkx object): corpus coupling graph with community ID
                                                 as supplementary node attribute;
               louvain_part.partition (dict): Louvain partition of the corpus coupling graph G 
                                              where dict keys are the pub IDs 
                                              and the dict values are the community IDs. 
       
    '''
    # standard library imports
    from collections import namedtuple
    
    # 3rd party import
    import community as community_louvain
    import networkx as nx
    
    named_tup_results = namedtuple('results', ['G','partition',])
    
    # Compute the best partition : {pub_id:community_id}
    partition = community_louvain.best_partition(G)
    
    nx.set_node_attributes(G,partition,'community_id')
    
    louvain_part = named_tup_results(G, partition,)   
    return louvain_part


def add_item_attribute(G, item, m_max_attrs,
                       in_dir_freq, in_dir_parsing):
    
    '''The 'add_item_attribute' function adds node attributes to the corpus coupling graph G.
       The number of these attributes is limited to m_max_attrs.
       
       The attributes correspond to an item selected in COUPL_AUTHORIZED_ITEMS 
       defined in BiblioGlobals module.
       
       The attributes are labelled item_<i> with i=0,...,m_max_attrs-1.
        
       For a given node, labelled article id, the node item_<i> attribute values are 
       the m_max_attrs topmost itemvalues of the item, in term of frequency, of this node. 
       The  m_max_attrs attributes are ranked by decreasing frequency values. 
       The frequency is attached to the itemvalue.
                    
       Example: 
       
       with m_max_attrs=2 and item= 'S2'
    
                id            S2_0                          S2_1
                
                125 | Behavioral Sciences(3.90) | Psychology, Biological(1.74)
                
                126 | Behavioral Sciences(3.90) | Psychology, Developmental(0.62)
                
                109 | Behavioral Sciences(3.90) | unknown
                
                238 | Behavioral Sciences(3.90) | Psychology, Multidisciplinary(1.33)
                
                470 | Zoology(1.95)             | Psychology, Biological(1.74)
                
    
       Args:
           G (networkx object): corpus coupling graph.
           item (str): the item choosen as attribute.
           m_max_attrs (int): maximum number of added node attributes 
                              corresponding to the choosen item.
           in_dir_freq (Path): folder path of the corpus description results.
           in_dir_parsing (Path): folder path of the corpus parsing results.
        
       Returns:
           G (networkx object): corpus coupling graph with the added attributes.
        
    '''

    # Standard library imports
    import inspect
    from pathlib import Path

    # 3rd party imports
    import networkx as nx
    import pandas as pd

    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COUPL_AUTHORIZED_ITEMS
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_DESCRIPTION
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
    
    # Check valid input arguments
    add_item_attribute.__annotations__ = {'G': nx.Graph, 'item': str, 'm_max_attrs': int,
                       'in_dir_freq': Path, 'in_dir_parsing': Path, 'return':nx.Graph}
    assert item in COUPL_AUTHORIZED_ITEMS, f"unknown item {item}"
    args = inspect.getfullargspec(add_item_attribute).args
    annotations = inspect.getfullargspec(add_item_attribute).annotations
    for arg in args:
        assert isinstance(locals()[arg],annotations[arg]), \
                f"type {locals()[arg]} should be: {annotations[arg]}"

    # Reads the list of "itemvalues" and their respective frequencies in the folder freq
    freq_file: Path = in_dir_freq / Path(DIC_OUTDIR_DESCRIPTION[item])
    df: pd.DataFame = pd.read_csv(freq_file,
                                  sep=',',
                                  usecols=['item', 'f']) # choose article id,item frequency
    dic_freq = dict(zip(df['item'],
                        df['f']))  # Builds dic_freq {itemvalue:frequency,...}

    # Reads the list of articles id and their respective itemvalues in the folder parsing
    parsing_file: Path = in_dir_parsing / Path(DIC_OUTDIR_PARSING[item])     
    usecols = [0, 1]
    if item == 'CU' or item == 'AU' or item == 'I':
        usecols = [0, 2]  # Takes care of countries.dat,
                          # authors.dat and institutions.dat with 3 columns
    df: pd.DataFame = pd.read_csv(parsing_file,
                                  sep='\t',
                                  usecols=usecols)
    df.columns = ['article_id', 'item_value'] # Normalization of the columns names for all items

    dic_freq_node: dict = {}
    for x in df.groupby('article_id'):  # Loop for article_id in corpus
        list_item_values = list(set(
            x[1]['item_value'].tolist()))  # Creates the list of itemvalues
                                           # of an article without duplicates

        # Creates the dic {article_id:[(itemvalue1,frequency1),(itemvalue2,frequency2)...],...}
        # ordered with frequency1 >= frequency2 >= ... >= frequency<m_max_attrs>
        dic_freq_node[x[0]] = sorted([(item_value, dic_freq[item_value])
                                      for item_value in list_item_values],
                                     key=lambda tup: tup[1],
                                     reverse=True)[0:m_max_attrs]

    # Takes care of the nodes with no itemvalues
    nodes = set(G.nodes)
    unaffected_nodes = nodes - set(dic_freq_node.keys())
    for node in unaffected_nodes:
        dic_freq_node[node] = [('unknown', 0)] * m_max_attrs

    # Adds m_max_attrs node attributes to the graph G
    dic_freq_node_attr = {}
    for i in range(m_max_attrs):
        for x, y in dic_freq_node.items():
            try:
                if y[i][0] != 'unknown':
                    dic_freq_node_attr[x] = f'{y[i][0]}({y[i][1]:.2f})'
                else:
                    dic_freq_node_attr[x] = 'unknown'
            except:
                dic_freq_node_attr[x] = 'unknown'
        nx.set_node_attributes(G, dic_freq_node_attr, f"{item}_{i}")

    return G


def plot_coupling_graph(G,partition,nodes_number_max=1):
    
    '''The "plot_coupling_graph" function plots corpus coupling graph G 
       coloring each node according to its community using networkx package.
       The layout is fixed to "spring_layout".
       
       Args:
           G (networkx object): corpus coupling graph with community ID 
                                as supplementary node attribute.
           partition (dict): Louvain partition of the corpus coupling graph G 
                             where dict keys are the pub IDs 
                             and the dict values are the community IDs.
           nodes_number_max (int): minimum number of nodes in a community 
                                   to keep the community on the plot (default = 1).
       
    '''
    
    # 3rd party import
    import matplotlib.cm as cm
    import matplotlib.pyplot as plt
    import networkx as nx
    import pandas as pd
       
    # Suppress communities with a number of nodes less than nodes_number_max
    df = pd.DataFrame(list(partition.items()),columns = ['pub_id','community_id']) 
    dg = df.groupby('community_id').count().reset_index()
    community_to_discard = list(dg[dg['pub_id']<nodes_number_max ] ['community_id'])
    nodes_to_dicard = list(df.query('community_id in @community_to_discard')['pub_id'])
    partition_number = max(partition.values()) - len(community_to_discard)
    G.remove_nodes_from(nodes_to_dicard)
    new_partition = {key:value for key,value in partition.items()
                 if value not in community_to_discard}
    
    # Draw the graph
    pos = nx.spring_layout(G)
    cmap = cm.get_cmap('viridis',partition_number + 1)
    fig = plt.figure(figsize=(15,15))
        # color the nodes according to their partition
    nx.draw_networkx_nodes(G, pos, new_partition.keys(), node_size=250,
                           cmap=cmap, node_color=list(new_partition.values()))
    nx.draw_networkx_edges(G, pos, alpha=0.9,width=1.5, edge_color='k', style='solid',)
    labels = nx.draw_networkx_labels(G,pos=pos,font_size=8,
                                     font_color='w')                                 
    node_degree = dict(G.degree).values()
    
    # Compute usefull information for the plot title
    mean_degree = sum(node_degree) * 1.0 / len(node_degree)
    mean_weight = 2*sum([d[-1]['weight'] for d in G.edges(data=True)])/(len(G.nodes()) * (len(G.nodes()) - 1))                    
    plt.title(f'Coupling graph \nAverage degree: {mean_degree:.2f}\
                Average weight: {mean_weight:.5f}',fontsize=23,fontweight="bold")
    plt.show()
    

def save_communities_xls(partition,in_dir,out_dir):
    
    '''The "save_communities_xls" function saves the "articles.dat" file as an EXCEL file 
       adding a column that contains the community ID of each article of the corpus.
       The filename is defined by COUPL_FILENAME_XLSX global in BiblioGlobals module.
       
       Args:
           partition (dict): Louvain partition of the corpus coupling graph G 
                             where dict keys are the pub IDs 
                             and the dict values are the community IDs.
           in_dir (Path): folder path of the corpus parsed files generated 
                          by the BiblioParsingWos module or the BiblioParsingScopus module.
           out_dir (Path): folder path where the EXEL file COUPL_FILENAME_XLSX is saved.
       
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party import
    import pandas as pd
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COL_NAMES
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COUPL_FILENAME_XLSX
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import DIC_OUTDIR_PARSING
  
    pub_id_alias = COL_NAMES['articles'][0]
    
    df_articles = pd.read_csv(in_dir / Path(DIC_OUTDIR_PARSING['A']),sep="\t")

    df_articles['communnity_id'] = df_articles[pub_id_alias].map(partition) # Adds column community_id
    df_articles.sort_values(by=['communnity_id',pub_id_alias],inplace=True)
    df_articles.to_excel(out_dir / Path(COUPL_FILENAME_XLSX))

    
def save_graph_gexf(G,save_dir):
    
    '''The "save_graph_gexf" function saves graph "G" in Gephy  format (.gexf).
       The filename is defined by COUPL_FILENAME_GEXF global in BiblioGlobals module.
       
       Args:
           G (networkx object): corpus coupling graph.
           save_dir (Path): folder path where the Gephy file COUPL_FILENAME_GEXF is saved.
       
    '''
    
    # Standard library imports
    from pathlib import Path
    
    # 3rd party imports
    import networkx as nx
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COUPL_FILENAME_GEXF
    
    nx.write_gexf(G,save_dir / Path(COUPL_FILENAME_GEXF))
    

def _runpythonlouvain(G): # unused function 
    
    '''The "_runpythonlouvain" function  is used to analyse a corpus 
       at level "len(foo_dendrogram) - 1)" of the corpus coupling graph G dendrogram, 
       (see https://buildmedia.readthedocs.org/media/pdf/python-louvain/latest/python-louvain.pdf).
       Author: Sebastian Grauwin (http://sebastian-grauwin.com/bibliomaps/)
    
       Args:
           G (networkx object): corpus coupling graph.
        
       Returns:
           results (tuple): [dendrogram, partition, modularity,] where
               dendrogram [list of dict]: a list of partitions, ie dictionnaries 
                                          where keys of the i+1 dict are the values of the i dict;
               partition (dict): Louvain partition of the corpus coupling graph G 
                                 where dict keys are the pub IDs 
                                 and the dict values are the community IDs;
               modularity [float]: modularity.
    
    '''
    # standard library imports
    from collections import namedtuple
    
    # 3rd party import
    import community as community_louvain
    
    # TO DO: move NRUNS in COUPL_GLOBAL_VALUES if _runpythonlouvain is used.
    NRUNS = 1 # number of time the louvain algorithm is run for a given network,
              # the best partition being kept.
    
    named_tup_results = namedtuple('results', ['dendrogram','partition','modularity',])
    
    max_modularity = -1
    for run in range(NRUNS):
        if NRUNS > 1:
            print(f'......run {run + 1}/{NRUNS}')
        foo_dendrogram = community_louvain.generate_dendrogram(G, part_init=None)
        partition_foo = community_louvain.partition_at_level(foo_dendrogram, len(foo_dendrogram) - 1)
        modularity = community_louvain.modularity(partition_foo, G)
        if modularity > max_modularity:
            max_modularity = modularity
            partition = partition_foo.copy()
            dendrogram = foo_dendrogram.copy()
    
    louvain_part = named_tup_results(dendrogram, partition, modularity,) 
    return louvain_part


def _graph_community(G): # unused function
        
    '''The 'graph_community' function is used to analyse a corpus at 
       two levels of the dendrogram of the corpus coupling graph G 
       in a way that the size of all the communities are <= SIZECUT.
       Author: Sebastian Grauwin (http://sebastian-grauwin.com/bibliomaps/)
    
       Args:
           G (networkx object): corpus coupling graph.
        
       Returns:
           louvain_partition (dict): partition of the corpus coupling graph G. 
    
    '''

    # 3rd party import    
    import community as community_louvain
    
    # TO DO: move SIZECUT in COUPL_GLOBAL_VALUES if _graph_community is used
    SIZECUT = 10 # Upper limit of size communities

    dendrogram, part, max_mod = _runpythonlouvain(G)
    part2 = part.copy()
    to_update = {}

    communities_id,nodes_id =set(part.values()), list(part.keys())
    for community_id in communities_id:
        list_nodes = [nodes for nodes in part.keys() if part[nodes] == community_id]

        if len(list_nodes) > SIZECUT: # split clusters of size > SIZECUT
            H = G.subgraph(list_nodes).copy()
            [dendo2, partfoo, mod] = _runpythonlouvain(H)
            dendo2 = community_louvain.generate_dendrogram(H, part_init=None)
            partfoo = community_louvain.partition_at_level(dendo2, len(dendo2) - 1)
            # add prefix code
            for aaa in partfoo.keys():
                partfoo[aaa] = (community_id + 1) * 1000 + partfoo[aaa]
            nb_comm = len(set(partfoo.values()))
            # "community_id" cluster ("len(list_nodes)" records) is split in nb_comm sub-clusters
            part2.update(partfoo)
        else:  # for communities of less than SIZECUT nodes, shift the com label as well
            for n in list_nodes:
                to_update[n] = ""
    for n in to_update:
        part2[n] += 1

    # ... save partitions
    louvain_partition = dict()
    for lev in range(len(dendrogram)):
        louvain_partition[lev] = community_louvain.partition_at_level(dendrogram, lev)
    # .. set communtity labels starting from 1 instead of 0 for top level
    for k in louvain_partition[len(dendrogram) - 1].keys():
        louvain_partition[len(dendrogram) - 1][k] += 1
    louvain_partition[len(dendrogram)] = part2
    
    return louvain_partition
