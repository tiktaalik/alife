# dots.py
# takes a pickle as input
# pickle is a tuple of two entities
# 0: gens: list of lists of patents by generation
# 1: traits: a sparse vector of the traits for each patent, except each vector 
#            is the value of a dictionary entry where the key is the pno

# real_dots.py
# produces dots from the real networks retrieved from the patns collection
# using real_networks.py
#
# Zackary Dunivin, Center for Advanced Computation, Reed College
# June 16 2015

import numpy as np
from pprint import pprint
from random import random, shuffle
from sys import exit
from operator import mul
import pca_to_rgb
import trait_matrix as tm

def ranks(file,n,just_nodes):
    node_gens = gens_by_pno(just_nodes,n)
    
    # guide rank
    file.write('/*guide*/ { node [color=invis, fillcolor = invis]; edge [style=invis]; ')
    for i in range(len(node_gens)-1):
        s = ('gen_',str(i),' -> ')
        s = ''.join(s)      
        file.write(s)
    s = ('gen_',str(len(node_gens)-1))
    s = ''.join(s) 
    file.write(s)
    file.write(';}\n')

    #
    # patent ranks
    #
    # generation
    for i in range(len(node_gens)):
        s = ('{ rank = same; gen_',str(i),'; ')            
        s = ''.join(s)
        file.write(s)
        # patent nodes            
        for pno in node_gens[i]:
            # genealogy                
            
            s = (str(pno),'; ')
            s = ''.join(s)           
            file.write(s)
                    
        # close subgraph
        file.write('}\n')


def pca_coloring(file,links,trait_dict,node_gens,focus,coloring,colors='red',traits = None):
    just_nodes = []
    for gen in node_gens:
        just_nodes += gen

    if focus == 'nodes' or focus == 'both':
        for pno in just_nodes:
            color = colors[pno]
            string = color_nodes(pno,color)
            file.write(string)


    for tup in links:    
        if focus == 'nodes':
            string = color_edges(tup,"grey")
            file.write(string)

        if focus == 'edges' or focus == 'both':
            color = colors[tup[1]]
            string = color_edges(tup,color)
            file.write(string)


def specified_traits(file,links,trait_dict,node_gens,focus,coloring,colors='red',traits = None):
    node_list = []
    edge_list = []
    base_edges = []

    # the primogenitor will always be the first parent in links
    primo = links[0][0]
    traits = set(traits)
    for tup in links:
        # color the child red
        child_traits = set(trait_dict[tup[1]])
        shared = list(child_traits.intersection(set(traits)))
        if shared:
            # select a random trait
            i = np.random.randint(len(shared))
            trait = shared[i]
            
            # color the node
            if focus == 'nodes' or focus == 'both':
                string = coloring(tup,trait,colors,'nodes')
                node_list.append(string)
            
            # don't color the edge  
            if focus == 'nodes':
                string = color_edges(tup,'grey')
                edge_list.append(string)
            
            # also color the edge
            if focus == 'edges' or focus == 'both':
                string = coloring(tup,trait,colors,'edges')
                edge_list.append(string)

        # base edge
        else:
            string = color_edges(tup,'grey')
            base_edges.append(string)

    write_nedges(file,node_list,base_edges,edge_list)

def primogenitor(file,links,trait_dict,node_gens,focus,coloring,colors='red',traits = None):
    primo = links[0][0]
    traits = trait_dict[primo]

    specified_traits(file,links,trait_dict,node_gens,focus,coloring,colors,traits)

def primo_depth(file,links,trait_dict,node_gens,focus,coloring,colors=['indigo','forestgreen','gold','red'],traits = None):
    node_list = []
    edge_list = []
    base_edges = []

    # make sure we have colors for all of the generations except the last
    if len(node_gens) != len(colors) + 1:
        print(colors)
        raise ValueError('Your have the wrong number of colors for primo_depth. Number of colors should equal number of generations - 1.')

    # coloring should always be color nodes
        if coloring != color_nodes:
            print('Coloring for primo_depth should always be nodes_or_edges. Set to nodes_or_edges.')
            coloring = nodes_or_edges

    # the primogenitor will always be the first parent in links
    primo = links[0][0]

    # count backwards, so that earlier connections will overwrite later ones
    #
    # no trait necessary
    trait = None
    
    for tup in links[::-1]:
        shared = shared_traits(primo,tup[1],trait_dict)
        if shared:
            gen = get_gen(tup[0],node_gens)
            color = colors[gen]
            
            # color the node
            if focus == 'nodes' or focus == 'both':
                string = coloring(tup,trait,color,'nodes')
                node_list.append(string)
            
            # don't color the edge  
            if focus == 'nodes':
                string = color_edges(tup,'grey')
                edge_list.append(string)
            
            # also color the edge
            if focus == 'edges' or focus == 'both':
                string = coloring(tup,trait,color,'edges')
                edge_list.append(string)

        # base edge
        else:
            string = color_edges(tup,'grey')
            base_edges.append(string)

    write_nedges(file,node_list,base_edges,edge_list)


def parents(file,links,trait_dict,node_gens,focus,coloring,colors='red',traits = None):
    node_list = []
    edge_list = []
    base_edges = []

    for tup in links:
        # color the child red
        shared = shared_traits(tup[0],tup[1],trait_dict)
        if shared:
            # select a random trait
            i = np.random.randint(len(shared))
            trait = shared[i]
            
            # color the node
            if focus == 'nodes' or focus == 'both':
                string = coloring(tup,trait,colors,'nodes')
                node_list.append(string)
            
            # don't color the edge  
            if focus == 'nodes':
                string = color_edges(tup,'grey')
                edge_list.append(string)
            
            # also color the edge
            if focus == 'edges' or focus == 'both':
                string = coloring(tup,trait,colors,'edges')
                edge_list.append(string)

        # base edge
        else:
            string = color_edges(tup,'grey')
            base_edges.append(string)

    write_nedges(file,node_list,base_edges,edge_list)


def randomized(file,links,trait_dict,node_gens,focus,coloring, colors='red',traits = None):
    node_list = []
    edge_list = []

    for tup in links:
        x = random()
        if x <= .12:
            if isinstance(colors,dict):
                # random color
                color_keys = colors.keys()
                i = np.randint(len(color_keys))
                trait = color_keys[i]
            else:
                trait = None

            if focus == 'nodes' or focus == 'both':
                string = coloring(tup,trait,colors,'nodes')
                node_list.append(string)
           
            # don't color the edge  
            if focus == 'nodes':
                string = color_edges(tup,'grey')
                edge_list.append(string)
            
            # also color the edge
            if focus == 'edges' or focus == 'both':
                string = coloring(tup,trait,colors,'edges')
                edge_list.append(string)

        # base edge
        else:
            string = color_edges(tup,'grey')
            edge_list.append(string)

    write_nedges(file,node_list,edge_list)


def color_nodes(node,color):
    return '%d [fillcolor = "%s"]\n' % (node,color)


def color_edges(nodes,color):
    return '%d -> %d [color="%s", style="solid"];\n' % (nodes[0],nodes[1],color)


def nodes_or_edges(nodes,colors,focus):
    if focus == "nodes":
        return color_nodes(nodes[1],colors)
    else:
        return color_edges(nodes,colors)


def single(nodes,trait,color,focus):
    return nodes_or_edges(nodes,color,focus)


def trait_color(nodes,trait,colors,focus):
    color = colors[trait]
    return nodes_or_edges(nodes,color,focus)


def write_nedges(file,node_list,base_edges,edge_list):
    for node in node_list:
        file.write(node)
    
    for edge in base_edges:
        file.write(edge)

    for edge in edge_list:
        file.write(edge)


def get_trait_colors(traits):
    """Returns a dictionary where keys are traits and values are colors"""
    if len(traits) <= 20:
        colors = ['red', 'gold', 'forestgreen', 'plum', 'blue','maroon','cyan','greenyellow','deeppink','orange', 'orangered','olivedrab','midnightblue','brown','aqua','purple','indigo','lightsalmon','palegoldenrod','magenta']
    else:
        colors = colors_for_graphviz(svg)
    
    color_dict = {}
    for i,trait in enumerate(traits):
        color_dict[trait] = colors[i%len(colors)]
    pprint(color_dict)
    return color_dict

def get_gen(pno,node_gens):
    for i,gen in enumerate(node_gens):
        if pno in gen:
            return i
    
    return 0

def shared_traits(p1,p2,trait_dict):
    try:
        p1set = set(trait_dict[p1])
        p2set = set(trait_dict[p2])

        # color the child red
        interset = p1set.intersection(p2set) 
        return list(interset)
    
    except TypeError, IndexError:
        print('1 with no traits')    
    
    return list()


def gens_by_pno(just_nodes,width):
    nodes = sorted(just_nodes)
    # first generation is the progenitor patent
    new_gens = [[nodes.pop(0)]]

    while len(nodes) > width:
        gen = []
        for i in range(width):
            gen.append(nodes.pop(0))

        new_gens.append(gen)

    # remaining patents make their own generation
    last_gen = []
    while len(nodes) > 0:
        last_gen.append(nodes.pop(0))

    new_gens.append(last_gen)

    return new_gens


def colors_for_graphviz(palette="rainbow"):
    # For multi-colored inheritance layers. Greys, black and white removed.
    # Shuffle into random order
    rainbow = ["red", "yellow", "orange", "green", "blue", "purple"]
    svg = ["aliceblue", "aqua", "aquamarine", "beige", "blue", "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue", "firebrick", "forestgreen", "fuchsia", "gainsboro", "gold", "goldenrod", "gray", "green", "greenyellow", "hotpink", "indianred", "indigo", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue", "purple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "springgreen", "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "whitesmoke", "yellow", "yellowgreen"]
    x11 = ["aliceblue", "aquamarine", "aquamarine1", "aquamarine2", "aquamarine3", "aquamarine4", "azure", "azure1", "azure2", "azure3", "azure4", "beige", "bisque", "bisque1", "bisque2", "bisque3", "bisque4", "blanchedalmond", "blue", "blue1", "blue2", "blue3", "blue4", "blueviolet", "brown", "brown1", "brown2", "brown3", "brown4", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "cadetblue", "cadetblue1", "cadetblue2", "cadetblue3", "cadetblue4", "chartreuse", "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4", "chocolate", "chocolate1", "chocolate2", "chocolate3", "chocolate4", "coral", "coral1", "coral2", "coral3", "coral4", "cornflowerblue", "cornsilk", "cornsilk1", "cornsilk2", "cornsilk3", "cornsilk4", "crimson", "cyan", "cyan1", "cyan2", "cyan3", "cyan4", "darkgoldenrod", "darkgoldenrod1", "darkgoldenrod2", "darkgoldenrod3", "darkgoldenrod4", "darkgreen", "darkkhaki", "darkolivegreen", "darkolivegreen1", "darkolivegreen2", "darkolivegreen3", "darkolivegreen4", "darkorange", "darkorange1", "darkorange2", "darkorange3", "darkorange4", "darkorchid", "darkorchid1", "darkorchid2", "darkorchid3", "darkorchid4", "darksalmon", "darkseagreen", "darkseagreen1", "darkseagreen2", "darkseagreen3", "darkseagreen4", "darkslateblue", "darkslategray", "darkslategray1", "darkslategray2", "darkslategray3", "darkslategray4", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deeppink1", "deeppink2", "deeppink3", "deeppink4", "deepskyblue", "deepskyblue1", "deepskyblue2", "deepskyblue3", "deepskyblue4", "dimgray", "dimgrey", "dodgerblue", "dodgerblue1", "dodgerblue2", "dodgerblue3", "dodgerblue4", "firebrick", "firebrick1", "firebrick2", "firebrick3", "firebrick4", "floralwhite", "forestgreen", "gainsboro", "ghostwhite", "gold", "gold1", "gold2", "gold3", "gold4", "goldenrod", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4", "honeydew", "honeydew1", "honeydew2", "honeydew3", "honeydew4", "hotpink", "hotpink1", "hotpink2", "hotpink3", "hotpink4", "indianred", "indianred1", "indianred2", "indianred3", "indianred4", "indigo", "invis", "ivory", "ivory1", "ivory2", "ivory3", "ivory4", "khaki", "khaki1", "khaki2", "khaki3", "khaki4", "lavender", "lavenderblush", "lavenderblush1", "lavenderblush2", "lavenderblush3", "lavenderblush4", "lawngreen", "lemonchiffon", "lemonchiffon1", "lemonchiffon2", "lemonchiffon3", "lemonchiffon4", "lightblue", "lightblue1", "lightblue2", "lightblue3", "lightblue4", "lightcoral", "lightcyan", "lightcyan1", "lightcyan2", "lightcyan3", "lightcyan4", "lightgoldenrod", "lightgoldenrod1", "lightgoldenrod2", "lightgoldenrod3", "lightgoldenrod4", "lightgoldenrodyellow", "lightgray", "lightgrey", "lightpink", "lightpink1", "lightpink2", "lightpink3", "lightpink4", "lightsalmon", "lightsalmon1", "lightsalmon2", "lightsalmon3", "lightsalmon4", "lightseagreen", "lightskyblue", "lightskyblue1", "lightskyblue2", "lightskyblue3", "lightskyblue4", "lightslateblue", "lightslategray", "lightslategrey", "lightsteelblue", "lightsteelblue1", "lightsteelblue2", "lightsteelblue3", "lightsteelblue4", "lightyellow", "lightyellow1", "lightyellow2", "lightyellow3", "lightyellow4", "limegreen", "linen", "magenta", "magenta1", "magenta2", "magenta3", "magenta4", "maroon", "maroon1", "maroon2", "maroon3", "maroon4", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumorchid1", "mediumorchid2", "mediumorchid3", "mediumorchid4", "mediumpurple", "mediumpurple1", "mediumpurple2", "mediumpurple3", "mediumpurple4", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "mistyrose1", "mistyrose2", "mistyrose3", "mistyrose4", "moccasin", "navajowhite", "navajowhite1", "navajowhite2", "navajowhite3", "navajowhite4", "navy", "navyblue", "none", "oldlace", "olivedrab", "olivedrab1", "olivedrab2", "olivedrab3", "olivedrab4", "orange", "orange1", "orange2", "orange3", "orange4", "orangered", "orangered1", "orangered2", "orangered3", "orangered4", "orchid", "orchid1", "orchid2", "orchid3", "orchid4", "palegoldenrod", "palegreen", "palegreen1", "palegreen2", "palegreen3", "palegreen4", "paleturquoise", "paleturquoise1", "paleturquoise2", "paleturquoise3", "paleturquoise4", "palevioletred", "palevioletred1", "palevioletred2", "palevioletred3", "palevioletred4", "papayawhip", "peachpuff", "peachpuff1", "peachpuff2", "peachpuff3", "peachpuff4", "peru", "pink", "pink1", "pink2", "pink3", "pink4", "plum", "plum1", "plum2", "plum3", "plum4", "powderblue", "purple", "purple1", "purple2", "purple3", "purple4", "red", "red1", "red2", "red3", "red4", "rosybrown", "rosybrown1", "rosybrown2", "rosybrown3", "rosybrown4", "royalblue", "royalblue1", "royalblue2", "royalblue3", "royalblue4", "saddlebrown", "salmon", "salmon1", "salmon2", "salmon3", "salmon4", "sandybrown", "seagreen", "seagreen1", "seagreen2", "seagreen3", "seagreen4", "seashell", "seashell1", "seashell2", "seashell3", "seashell4", "sienna", "sienna1", "sienna2", "sienna3", "sienna4", "skyblue", "skyblue1", "skyblue2", "skyblue3", "skyblue4", "slateblue", "slateblue1", "slateblue2", "slateblue3", "slateblue4", "slategray", "slategray1", "slategray2", "slategray3", "slategray4", "slategrey", "snow", "snow1", "snow2", "snow3", "snow4", "springgreen", "springgreen1", "springgreen2", "springgreen3", "springgreen4", "steelblue", "steelblue1", "steelblue2", "steelblue3", "steelblue4", "tan", "tan1", "tan2", "tan3", "tan4", "thistle", "thistle1", "thistle2", "thistle3", "thistle4", "tomato", "tomato1", "tomato2", "tomato3", "tomato4", "transparent", "turquoise", "turquoise1", "turquoise2", "turquoise3", "turquoise4", "violet", "violetred", "violetred1", "violetred2", "violetred3", "violetred4", "wheat", "wheat1", "wheat2", "wheat3", "wheat", "whitesmoke", "yellow", "yellow1", "yellow2", "yellow3", "yellow4", "yellowgreen"]

    # if need colors randomized independently of keyword colors
    if palette == "x11":
        colors = x11
    elif palette == "svg":
        colors = svg
    else:
        colors = rainbow

    shuffle(colors)
    return colors    


def get_pca_colors(s_matrix,just_nodes):
    matrix = tm.dense_matrix(s_matrix)

    z = pca_to_rgb.main(matrix)
    z = [arr.tolist() for arr in z]
    return dec_to_hex(z,just_nodes)
    
def dec_to_hex(z,just_nodes):
    pca = []
    for arr in z:
        # multiply by 255
        arr = map(mul,arr,[255]*3)
        # round
        arr = map(round,arr)
        # int
        arr = map(int,arr)
        string = rgb_to_hex(arr)
        #string = '%r %r %r' % arr
        pca.append(string)

    pca_dict = {pno:pca[i] for i,pno in enumerate(just_nodes)}


    return pca_dict 


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (rgb[0],rgb[1],rgb[2])


def write_dot(network,num_traits,rank_length,file_name="network",focus='nodes',sharing=parents,coloring=color_nodes,colors='red',traits=None,pca_dict=None):
    # n is number of traits to look at
    # the results of real_networks.py produces a 4-tuple
    # 0: just_nodes: the pno of every node in the network
    # 1: node_gens: the pno of every node in the network separated into 
    #               lists by generation
    # 2: links: a tuple of parent pno and child pno for every edge in 
    #           the network
    # 3: gens: a dictionary containing the pno, citedby and sorted_text 
    #          for every node in the network the pno of every node in the
    #          network separated into lists by generation

    just_nodes = network[0]
    node_gens = network[1]
    links = network[2]
    trait_dict = network[3]

    primo_traits = trait_dict[just_nodes[0]]
    
    # get colors
    if coloring == trait_color:
        colors = get_trait_colors(primo_traits)
    elif pca_dict and sharing == pca_coloring:
        colors = pca_dict
    elif sharing == pca_coloring:
        pca_patents = trait_dict.keys()
        pca_patents = sorted(pca_patents)
        
        # get rid of the pnos
        sparse = []
        for pno in pca_patents:
            sparse.append(trait_dict[pno])
        colors = get_pca_colors(sparse,pca_patents)

    file = open(file_name + '.dot', 'w')
    file.write(
"""digraph inheritance {
center=true;
ratio = .77
size = 5
node [shape=square, style = filled, fixedsize=false, height = 4.7, width= 4.7, color = white, fillcolor = black, label = ""]
edge [arrowhead=none, color=lightgrey];
"""
)
    # orders the patents by issue number with rank_length patents per rank
    ranks(file,rank_length,just_nodes)

    # nodes
    # color the progenitor node
    if isinstance(colors, basestring):
        color = colors
    else:
        color = "black"

    string = '%d [fillcolor = %s]\n' % (just_nodes[0],color)
    file.write(string)

    sharing(file,links,trait_dict,node_gens,focus,coloring,colors) 
    

    # end of file
    #
    file.write('}\n')
    file.close()