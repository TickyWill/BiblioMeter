__all__ = ['cooc_graph_html_plot',
           'coupling_graph_html_nwplt',
           'coupling_graph_html_plot',]

# Globals imported from BiblioAnalysis_Utils.BiblioSpecificGlobals: COOC_HTML_PARAM, COUPL_HTML_PARAM

def cooc_graph_html_plot(G,html_file,heading, cooc_html_param=None):
    
    # 3rd party import
    import networkx as nx
    from pyvis.network import Network
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COOC_HTML_PARAM
    
    if cooc_html_param==None: cooc_html_param=COOC_HTML_PARAM
    algo = COOC_HTML_PARAM['algo']
    height = COOC_HTML_PARAM['height']
    width = COOC_HTML_PARAM['width']
    bgcolor = COOC_HTML_PARAM['bgcolor']
    font_color = COOC_HTML_PARAM['algo']
    
    def map_algs(g,alg='barnes'):
        if alg == 'barnes':
            g.barnes_hut()
        if alg == 'forced':
            g.force_atlas_2based()
        if alg == 'hr':
            g.hrepulsion()
    
    dic_tot_edges ={node:G.degree(node,'nbr_edges') for node in G.nodes}
    
    nt = Network(height=height, width=width, 
                 bgcolor=bgcolor, 
                 font_color=font_color,notebook=False,heading = heading)

    # populates the nodes and edges data structures
    nt.from_nx(G)
    dic_node_label = {str(node['id']):str(node['node_size'])+ '-'\
                      + node['label'] for node in nt.nodes}
    map_algs(nt,alg='barnes')
    
    for edge in nt.edges:
        edge['title'] = edge['nbr_edges']
        edge['value'] = edge['nbr_edges']
    
    for node in nt.nodes:     
        node['title'] = node['label']
        node['size'] = node['node_size']
        node['tot_edges'] = dic_tot_edges[node['id']]
        node['nbr_edges_to'] = {}
        for edge in nt.edges:
            if edge['from'] == node['id']:
                node_to_label = dic_node_label[str(edge['to'])]
                node['nbr_edges_to'][node_to_label] = edge['nbr_edges']
            if edge['to'] == node['id']:
                node_from_label = dic_node_label[str(edge['from'])]
                node['nbr_edges_to'][node_from_label]=edge['nbr_edges']

    neighbor_map = nt.get_adj_list()
    
    dic_label_main = {node['id']: str(node['node_size']) + '-' \
                                 + node['label'] + ' (' \
                                 + str(node['tot_edges']) + ')' for node in nt.nodes}
    dic_label_neighbors = {}
    for node in nt.nodes:
        id = node['id']
        dic_label_neighbors[id] = []
        for key in node['nbr_edges_to'].keys():
            dic_label_neighbors[id].append(key + ' (' + str(node['nbr_edges_to'][key]) + ')')
        # Sorting neighbors size
        neighbors_size = [int(dic_label_neighbors[id][i][:dic_label_neighbors[id][i].find('-')]) \
                   for i in range(len(dic_label_neighbors[id]))]
        sizes_tup = list(zip(neighbors_size,dic_label_neighbors[id])) 
        sizes_tup = sorted(sizes_tup, key=lambda sizes_tup: sizes_tup[0], reverse=True)
        dic_label_neighbors[id] = [tup[1] for tup in sizes_tup]                   
    
    # add neighbor data to node hover data
    for node in nt.nodes:
        idd = node['id'] 
        title = '<b>'+dic_label_main[idd] + '</b>'+ '<br>' +'<br>'\
                .join([dic_label_neighbors[idd][i] for i in range(len(dic_label_neighbors[idd]))])
        node['title'] = title

    nt.show_buttons(filter_=['physics'])
    nt.show(html_file)
    

def coupling_graph_html_nwplt(G,html_file,community_id,attr_dic,colored_attr,
                                colored_values,shaped_attr,heading,coupl_html_param=None):
    
    # 3rd party import
    import networkx as nx
    from pyvis.network import Network
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioSpecificGlobals import COUPL_HTML_PARAM

    if coupl_html_param==None: coupl_html_param=COUPL_HTML_PARAM        
    background_color = COUPL_HTML_PARAM['background_color']
    font_color = COUPL_HTML_PARAM['font_color']
    edges_color = COUPL_HTML_PARAM['edges_color']
    nodes_colors = COUPL_HTML_PARAM['nodes_colors']

    SG = G.__class__()
    if community_id != 'all':
        # Builds a sub-graph from G limited to the community 'community_id'
        selected_nodes = {n:d['community_id'] for n,d in G.nodes().items() \
                          if d['community_id'] == int(community_id)}
        nodes_list = list(selected_nodes.keys())
        SG.add_nodes_from((n, G.nodes[n]) for n in nodes_list)
        SG.add_edges_from((n, nbr, d)
                for n, nbrs in G.adj.items() if n in nodes_list
                for nbr, d in nbrs.items() if nbr in nodes_list)
        SG.graph.update(G.graph)
    else:
        SG = G
    dic_tot_edges ={node:SG.degree(node,'nc') for node in SG.nodes}
    
    # sets colored attributes keys  
    attr_nbr = attr_dic[colored_attr]
    attr_keys = [colored_attr + '_' + str(i) for i in range(attr_nbr)]
     
    def map_algs(g,alg='barnes'):
        if alg == 'barnes':
            g.barnes_hut()
        if alg == 'forced':
            g.force_atlas_2based()
        if alg == 'hr':
            g.hrepulsion()

    
    nt = Network(height=1000, width=1000, 
                 bgcolor=background_color, 
                 font_color=font_color,notebook=False, heading= heading)        

    # populates the nodes data structures
    nt.from_nx(SG)
    map_algs(nt,alg='barnes')

    for node in nt.nodes:
        node['size'] = node['nbr_references']
        node['title'] = 'community_id: ' + str(node['community_id'])+ '<br>'
        node['title'] += 'pub_id:'+ str(node['id'])+ '<br>'
        node['title'] += 'refs number:'+ str(node['size'])+ '<br>'
        node['title'] += 'shared refs:'+ str(dic_tot_edges[node['id']])+ '<br>'
        node['title'] += '<br>'.join([key + ': ' + str(node[key]) 
                                    for key in node.keys()
                                    if 'CU_' in key
                                    or 'TK_' in key
                                    or 'IK_' in key
                                    or 'AK_' in key
                                    or 'S_' in key
                                    or 'S2_' in key])
        
        node['label'] = str(node['id'])

        attr_labels = [node[attr_keys[i]][:node[attr_keys[i]].find('(')] for i in range(attr_nbr)]
        if attr_labels[0] in colored_values.keys():
            node['color'] = nodes_colors[int(colored_values[attr_labels[0]])]
        else:
            node['color'] = nodes_colors['uncolor']
        
        if shaped_attr in attr_labels :
            node['shape'] = 'triangle'
        else:
            node['shape'] = 'dot'
    
    for edge in nt.edges:
        edge['title'] = edge['nc']
        edge['color'] = edges_color
        edge['value'] = edge['nc']
    
    nt.show_buttons(filter_=['physics'])
    nt.show(html_file)
    

def coupling_graph_html_plot(G,html_file,community_id,attr_dic,colored_attr,
                             colored_values,shaped_attr,nodes_colors,edges_color,
                             background_color,font_color,heading):
    
    # 3rd party import
    import networkx as nx
    from pyvis.network import Network
    
    SG = G.__class__()
    if community_id != 'all':
        # Builds a sub-graph from G limited to the community 'community_id'
        selected_nodes = {n:d['community_id'] for n,d in G.nodes().items() \
                          if d['community_id'] == int(community_id)}
        nodes_list = list(selected_nodes.keys())
        SG.add_nodes_from((n, G.nodes[n]) for n in nodes_list)
        SG.add_edges_from((n, nbr, d)
                for n, nbrs in G.adj.items() if n in nodes_list
                for nbr, d in nbrs.items() if nbr in nodes_list)
        SG.graph.update(G.graph)
    else:
        SG = G
    dic_tot_edges ={node:SG.degree(node,'nc') for node in SG.nodes}
    
    # sets colored attributes keys  
    attr_nbr = attr_dic[colored_attr]
    attr_keys = [colored_attr + '_' + str(i) for i in range(attr_nbr)]
     
    def map_algs(g,alg='barnes'):
        if alg == 'barnes':
            g.barnes_hut()
        if alg == 'forced':
            g.force_atlas_2based()
        if alg == 'hr':
            g.hrepulsion()
   
    nt = Network(height=1000, width=1000, 
                 bgcolor=background_color, 
                 font_color=font_color,notebook=False, heading= heading)        

    # populates the nodes data structures
    nt.from_nx(SG)
    map_algs(nt,alg='barnes')

    for node in nt.nodes:
        node['size'] = node['nbr_references']
        node['title'] = 'community_id: ' + str(node['community_id'])+ '<br>'
        node['title'] += 'pub_id:'+ str(node['id'])+ '<br>'
        node['title'] += 'refs number:'+ str(node['size'])+ '<br>'
        node['title'] += 'shared refs:'+ str(dic_tot_edges[node['id']])+ '<br>'
        node['title'] += '<br>'.join([key + ': ' + str(node[key]) 
                                    for key in node.keys()
                                    if 'CU_' in key
                                    or 'TK_' in key
                                    or 'IK_' in key
                                    or 'AK_' in key
                                    or 'S_' in key
                                    or 'S2_' in key])
        
        node['label'] = str(node['id'])

        attr_labels = [node[attr_keys[i]][:node[attr_keys[i]].find('(')] for i in range(attr_nbr)]
        if attr_labels[0] in colored_values.keys():
            node['color'] = nodes_colors[int(colored_values[attr_labels[0]])]
        else:
            node['color'] = nodes_colors['uncolor']
        
        if shaped_attr in attr_labels :
            node['shape'] = 'triangle'
        else:
            node['shape'] = 'dot'
    
    for edge in nt.edges:
        edge['title'] = edge['nc']
        edge['color'] = edges_color
        edge['value'] = edge['nc']
    
    nt.show_buttons(filter_=['physics'])
    nt.show(html_file)