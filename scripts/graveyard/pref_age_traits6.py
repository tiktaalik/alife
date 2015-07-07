# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 19:30:33 2014

@author: zodcomp
"""


from random import random, randint, shuffle
import matplotlib.pyplot as plt
from operator import itemgetter
import cPickle
import time
import csv
import os




class Patents(object):
    
    def __init__(self, number_of_patents=100, citations_per_patent=5, avg=True, 
                 min_citations_per_patent=0, initial_weight = 1):
        self.number_of_patents = number_of_patents
        self.citations_per_patent = citations_per_patent
        
        # set min and max so that number of citations averages citations_per_patent
        if avg:
            self.min_citations_per_patent = min_citations_per_patent                                    
            self.max_citations_per_patent = self.citations_per_patent * 2 - self.min_citations_per_patent
        else:
            self.min_citations_per_patent = self.citations_per_patent
            self.max_citations_per_patent = self.citations_per_patent

        self.initial_weight = initial_weight
        self.define_prior_to_forming()
    
#==============================================================================   
    def define_prior_to_forming(self):
        self.define_patents()
        self.define_parentage()
        self.define_citation_count()
        self.define_weights()
        
    def define_patents(self):       
        self.patents = [i for i in range(self.number_of_patents)]
    
    def define_parentage(self):
        # Form the first patent manually!      
        self.parentage = [()]

    def define_citation_count(self):
        self.citation_count = [0 for i in range(self.number_of_patents)]
        self.counts = []
    
    def define_weights(self):
        self.weights = []
   
#==============================================================================
    def form_patents(self):
        for self.now_forming in self.patents[1:self.number_of_patents]:
            self.update_weights()            
            citation_sampler = Sampler(self, self.min_citations_per_patent, self.max_citations_per_patent, self.citation_count) 
            
            parents = citation_sampler.weighted_sampling()
            self.parentage.append(parents)
            
            self.citation_count = citation_sampler.sample_count
            self.counts.append(list(self.citation_count))
                
            if self.now_forming % 1000 == 0:
                print "Now forming patent_%i" % self.now_forming

#==============================================================================
# Save output
#           
#    -parentage
#    -final count for each patent        

    def write_parentage(self):
        with open("parentage.csv", "wb") as file:
            writer = csv.writer(file)
            writer.writerows(self.parentage)
            
    def write_count(self):
        file = open('counts.txt', 'w')

        counts = self.citation_count
        for v in counts:
            count =  v
            count = str(count)
            count = "%s\n" % count   
            file.write(count)
        file.close()

class Uniform(Patents):

    def form_patents(self):
        for self.now_forming in self.patents[1:self.number_of_patents]:          
            citation_sampler = Sampler(self, self.min_citations_per_patent, self.max_citations_per_patent, self.citation_count) 
            
            parents = citation_sampler.unweighted_sampling()
            self.parentage.append(parents)
            
            self.citation_count = citation_sampler.sample_count
            self.counts.append(list(self.citation_count)) 
                           
            if self.now_forming % 1000 == 0:
                print "Now forming patent_%i" % self.now_forming
        
class Preferential(Patents):
     
    def update_weights(self):        
         self.weights = [1 + (self.citation_count[i] * 2) for i in range(self.now_forming)]
 
         self.summed_weights = sum(self.weights)          

class Aging(Patents):
    
    def define_prior_to_forming(self):
        super(Aging, self).define_prior_to_forming()
        self.define_aging_coefficients()
            
    def define_aging_coefficients(self):
        self.aging_coefficients = []        
        for i in range(self.citations_per_patent):
            self.aging_coefficients.append((self.citations_per_patent + 1 - i) ** -1.45)            
 
    def update_weights(self):
        self.update_aging_coefficients()        
        # probability(k) ~ 1 + (k ^ w)(d^a) where k is the patent, w is the weight, 
        # d is the age (t - i), and a is the aging attachment factor
        self.weights = [1 + (self.citation_count[i] ** 2) * self.aging_coefficients[i] for i in range(self.now_forming)]

        self.summed_weights = sum(self.weights)
        
    def update_aging_coefficients(self):
        self.aging_coefficients.insert(0, self.now_forming ** -1.45)      
     
     
class Keywords(object):

    def __init__(self, parentage_file, keywords_per_patent=5, avg=True, min_keywords_per_patent=0, num_keywords=100):
        self.parentage_file = parentage_file       
        self.keywords_per_patent = keywords_per_patent
        self.num_keywords = num_keywords
        if avg:
            self.min_keywords_per_patent = min_keywords_per_patent                                    
            self.max_keywords_per_patent = (self.keywords_per_patent - self.min_keywords_per_patent) * 2
        else:
            self.min_keywords_per_patent = self.keywords_per_patent
            self.max_keywords_per_patent = self.keywords_per_patent
            
        self.define_prior_to_assignment()

    def define_prior_to_assignment(self):
        self.define_keywords()
        self.define_keyword_count()
        self.define_weights()
        self.define_traits_by_patent()
        self.define_parentage()
        self.get_phylogenies()

    def define_keywords(self):
        #self.keywords = [i for i in range(100)]
        pass

    def define_keyword_count(self):
        self.keyword_count = [0 for i in range(self.num_keywords)]
    
    def define_weights(self):
        self.weights = []
            
    def define_traits_by_patent(self):
        self.traits_by_patent = []
        
    def define_parentage(self):
        self.parentage = []
        with open(self.parentage_file) as inputfile:
            for row in csv.reader(inputfile, delimiter=","):
                self.parentage.append(row)
        
        # convert lists of strings to lists of ints
        self.parentage = [map(int, parents) for parents in self.parentage]
        
        self.number_of_patents = len(self.parentage)
    
    def assign_keywords(self):        
        for i in range(self.number_of_patents):
            traits = self.unweighted_keywords()
            self.traits_by_patent.append(traits)

    def unweighted_keywords(self):
        traits = set()
        for i in range(randint(self.min_keywords_per_patent, self.max_keywords_per_patent)):
            sample = randint(0, self.num_keywords - 1)
            if not sample in traits:           
                traits.add(sample)
        
        return frozenset(traits)
        
    def first_degree_chains(self):       
        self.inheritance_count = [0 for i in range(len(self.parentage))]        
        self.inheritance_interactions = [[] for i in range(len(self.parentage))]
        self.inheritance_interactions_colored = [[] for i in range(len(self.parentage))]
        
        for child, parents in enumerate(self.parentage):

            for parent in parents:
                intersection = self.traits_by_patent[parent].intersection(self.traits_by_patent[child])                
                if intersection:
                    self.inheritance_count[parent] += len(intersection)
                    for keyword in intersection:
                        child_and_keyword = (child, keyword)
                        self.update_keyword_count(keyword)
                        
                    self.inheritance_interactions_colored[parent].append(child_and_keyword)
                    self.inheritance_interactions[parent].append(child*len(intersection))
    
    
    def follow_chain(self, parent, children):
        for child in children:
           intersection = self.parentage[parent].update(self.parentage[child])              
           if intersection:
                pass
               
    def update_keyword_count(self, keyword):
        self.keyword_count[keyword] += 1

    def measure_inheritance(self):
        num_citations = 0
        for parents in self.parentage:
            num_citations += len(parents)
        
        expected = float(self.keywords_per_patent ** 2) / (self.num_keywords)      
        actual = float(sum(self.keyword_count)) / num_citations 
        
        expected *= 100
        actual *= 100
        print ("expected: %d%%" % expected)
        print ("actual: %d%%" % actual)
    
    def write_traits_by_patent(self):
        file = open('traits_by_patent.txt', 'w')    
        for traits in self.traits_by_patent:
            traits = str(traits)
            traits = "%s\n" % traits
            file.write(traits)
        
        file.close()
    
    def write_inheritance_count(self):
        file = open('inheritance_count.txt', 'w')
        summed_counts = "sum: " + str(sum(self.inheritance_count)) + '\n'           
        file.write(summed_counts)
        for trait_count in self.inheritance_count:
            trait_count = str(trait_count)
            trait_count = "%s\n" % trait_count
            file.write(trait_count)
        
        file.close()
             
    def dot_for_hiver(self):               
        edges = []
        for child, parents in enumerate(self.parentage):
            if not parents:
                pass                
                row = "%i;\n" % child
                edges.append(row)
            else:
                for parent in parents:
                    initial_weight = 1             

                    if child in self.inheritance_interactions[parent]:
                        initial_weight = 1                    
                        weight = initial_weight + self.inheritance_interactions[parent].count(child)*initial_weight
                        row = "%i -> %i [color=red]\n" % (parent, child)
#                    else:
#                        row = "/*bottom*/ %i -> %i [color=grey]\n" % (parent, child)
                    edges.append(row)
            
        edges.sort()
       
        file = open('dot_for_hiver.dot', 'w')    
        
        file.write("graph inheritance {\n")       
        for n in range(len(self.parentage)):           
            file.write('%d;\n' % n)
        for row in edges:   
            file.write(row)
        file.write('}\n')
        file.close()     
    
    def get_top_keywords(self, range):
        # most cited patents
        ordered_keywords_and_counts = sorted(enumerate(self.keyword_count), key=itemgetter(1))        
        reversed_ks_and_cs = ordered_keywords_and_counts[::-1]     
        most_cited_ks_and_cs = reversed_ks_and_cs[0:range]
        
        return most_cited_ks_and_cs
        
    def get_phylogenies(self):
        parentage_sets = [frozenset(parents) for parents in self.parentage]
        ancestors = [frozenset() for i in range(len(self.parentage))]
        descendents = [frozenset() for i in range(len(self.parentage))]
        
        for child, parents in enumerate(parentage_sets):
            ancestors[child] = parents            
            for parent in parents:
                ancestors[child] = ancestors[child].union(ancestors[parent])
     
        enum_parentage = [(child, parents) for child, parents in enumerate(parentage_sets)]
        reversed_e_p = enum_parentage[::-1]
        for child, parents in reversed_e_p:            
            for parent in parents:
                descendents[parent] = descendents[parent].union(descendents[child])
        
        self.ancestors = ancestors
        self.descendents = descendents                      
 
    def colors_for_graphviz(self, palette="rainbow"):
        # For multi-colored inheritance layers. Greys, black and white removed. 
        # Shuffle into random order       
        rainbow = ["red", "yellow", "orange", "green", "blue", "purple"]
        svg = ["aliceblue", "antiquewhite", "aqua", "aquamarine", "beige", "blue", "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue", "firebrick", "forestgreen", "fuchsia", "gainsboro", "gold", "goldenrod", "gray", "green", "greenyellow", "hotpink", "indianred", "indigo", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue", "purple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "springgreen", "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "whitesmoke", "yellow", "yellowgreen"]
        x11 = ["aliceblue", "antiquewhite", "antiquewhite1", "antiquewhite2", "antiquewhite3", "antiquewhite4", "aquamarine", "aquamarine1", "aquamarine2", "aquamarine3", "aquamarine4", "azure", "azure1", "azure2", "azure3", "azure4", "beige", "bisque", "bisque1", "bisque2", "bisque3", "bisque4", "blanchedalmond", "blue", "blue1", "blue2", "blue3", "blue4", "blueviolet", "brown", "brown1", "brown2", "brown3", "brown4", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "cadetblue", "cadetblue1", "cadetblue2", "cadetblue3", "cadetblue4", "chartreuse", "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4", "chocolate", "chocolate1", "chocolate2", "chocolate3", "chocolate4", "coral", "coral1", "coral2", "coral3", "coral4", "cornflowerblue", "cornsilk", "cornsilk1", "cornsilk2", "cornsilk3", "cornsilk4", "crimson", "cyan", "cyan1", "cyan2", "cyan3", "cyan4", "darkgoldenrod", "darkgoldenrod1", "darkgoldenrod2", "darkgoldenrod3", "darkgoldenrod4", "darkgreen", "darkkhaki", "darkolivegreen", "darkolivegreen1", "darkolivegreen2", "darkolivegreen3", "darkolivegreen4", "darkorange", "darkorange1", "darkorange2", "darkorange3", "darkorange4", "darkorchid", "darkorchid1", "darkorchid2", "darkorchid3", "darkorchid4", "darksalmon", "darkseagreen", "darkseagreen1", "darkseagreen2", "darkseagreen3", "darkseagreen4", "darkslateblue", "darkslategray", "darkslategray1", "darkslategray2", "darkslategray3", "darkslategray4", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deeppink1", "deeppink2", "deeppink3", "deeppink4", "deepskyblue", "deepskyblue1", "deepskyblue2", "deepskyblue3", "deepskyblue4", "dimgray", "dimgrey", "dodgerblue", "dodgerblue1", "dodgerblue2", "dodgerblue3", "dodgerblue4", "firebrick", "firebrick1", "firebrick2", "firebrick3", "firebrick4", "floralwhite", "forestgreen", "gainsboro", "ghostwhite", "gold", "gold1", "gold2", "gold3", "gold4", "goldenrod", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4", "honeydew", "honeydew1", "honeydew2", "honeydew3", "honeydew4", "hotpink", "hotpink1", "hotpink2", "hotpink3", "hotpink4", "indianred", "indianred1", "indianred2", "indianred3", "indianred4", "indigo", "invis", "ivory", "ivory1", "ivory2", "ivory3", "ivory4", "khaki", "khaki1", "khaki2", "khaki3", "khaki4", "lavender", "lavenderblush", "lavenderblush1", "lavenderblush2", "lavenderblush3", "lavenderblush4", "lawngreen", "lemonchiffon", "lemonchiffon1", "lemonchiffon2", "lemonchiffon3", "lemonchiffon4", "lightblue", "lightblue1", "lightblue2", "lightblue3", "lightblue4", "lightcoral", "lightcyan", "lightcyan1", "lightcyan2", "lightcyan3", "lightcyan4", "lightgoldenrod", "lightgoldenrod1", "lightgoldenrod2", "lightgoldenrod3", "lightgoldenrod4", "lightgoldenrodyellow", "lightgray", "lightgrey", "lightpink", "lightpink1", "lightpink2", "lightpink3", "lightpink4", "lightsalmon", "lightsalmon1", "lightsalmon2", "lightsalmon3", "lightsalmon4", "lightseagreen", "lightskyblue", "lightskyblue1", "lightskyblue2", "lightskyblue3", "lightskyblue4", "lightslateblue", "lightslategray", "lightslategrey", "lightsteelblue", "lightsteelblue1", "lightsteelblue2", "lightsteelblue3", "lightsteelblue4", "lightyellow", "lightyellow1", "lightyellow2", "lightyellow3", "lightyellow4", "limegreen", "linen", "magenta", "magenta1", "magenta2", "magenta3", "magenta4", "maroon", "maroon1", "maroon2", "maroon3", "maroon4", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumorchid1", "mediumorchid2", "mediumorchid3", "mediumorchid4", "mediumpurple", "mediumpurple1", "mediumpurple2", "mediumpurple3", "mediumpurple4", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "mistyrose1", "mistyrose2", "mistyrose3", "mistyrose4", "moccasin", "navajowhite", "navajowhite1", "navajowhite2", "navajowhite3", "navajowhite4", "navy", "navyblue", "none", "oldlace", "olivedrab", "olivedrab1", "olivedrab2", "olivedrab3", "olivedrab4", "orange", "orange1", "orange2", "orange3", "orange4", "orangered", "orangered1", "orangered2", "orangered3", "orangered4", "orchid", "orchid1", "orchid2", "orchid3", "orchid4", "palegoldenrod", "palegreen", "palegreen1", "palegreen2", "palegreen3", "palegreen4", "paleturquoise", "paleturquoise1", "paleturquoise2", "paleturquoise3", "paleturquoise4", "palevioletred", "palevioletred1", "palevioletred2", "palevioletred3", "palevioletred4", "papayawhip", "peachpuff", "peachpuff1", "peachpuff2", "peachpuff3", "peachpuff4", "peru", "pink", "pink1", "pink2", "pink3", "pink4", "plum", "plum1", "plum2", "plum3", "plum4", "powderblue", "purple", "purple1", "purple2", "purple3", "purple4", "red", "red1", "red2", "red3", "red4", "rosybrown", "rosybrown1", "rosybrown2", "rosybrown3", "rosybrown4", "royalblue", "royalblue1", "royalblue2", "royalblue3", "royalblue4", "saddlebrown", "salmon", "salmon1", "salmon2", "salmon3", "salmon4", "sandybrown", "seagreen", "seagreen1", "seagreen2", "seagreen3", "seagreen4", "seashell", "seashell1", "seashell2", "seashell3", "seashell4", "sienna", "sienna1", "sienna2", "sienna3", "sienna4", "skyblue", "skyblue1", "skyblue2", "skyblue3", "skyblue4", "slateblue", "slateblue1", "slateblue2", "slateblue3", "slateblue4", "slategray", "slategray1", "slategray2", "slategray3", "slategray4", "slategrey", "snow", "snow1", "snow2", "snow3", "snow4", "springgreen", "springgreen1", "springgreen2", "springgreen3", "springgreen4", "steelblue", "steelblue1", "steelblue2", "steelblue3", "steelblue4", "tan", "tan1", "tan2", "tan3", "tan4", "thistle", "thistle1", "thistle2", "thistle3", "thistle4", "tomato", "tomato1", "tomato2", "tomato3", "tomato4", "transparent", "turquoise", "turquoise1", "turquoise2", "turquoise3", "turquoise4", "violet", "violetred", "violetred1", "violetred2", "violetred3", "violetred4", "wheat", "wheat1", "wheat2", "wheat3", "wheat", "whitesmoke", "yellow", "yellow1", "yellow2", "yellow3", "yellow4", "yellowgreen"]
        
        
        if not hasattr(self, 'keyword_colors'):        
            shuffle(x11)            
            self.keyword_colors = x11
        
        # if need colors randomized independently of keyword colors
        if palette == "x11": 
            colors = x11
        elif palette == "svg":
            colors = svg
        else:
            colors = rainbow
            
        shuffle(colors)
        return colors

    def grid(self, starting_node, ending_node, nodes_per_gen, xmax, ymax, starting_y, num_rows, file):         
        xmax = float(xmax)
        ymax = float(ymax)
         
        y = starting_y
        num_nodes = ending_node - starting_node
        if not num_rows:
            num_rows = (num_nodes/nodes_per_gen)

        # number of inches / (number of rows - 1)        
        yincr = ymax / (num_rows - 1)
         
        x = 0      
        for n in range(starting_node, ending_node):
            # max inches across
            xincr = xmax/ (nodes_per_gen - 1)
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
             
            # new row: reset x and increment y            
            if (n + 1) % nodes_per_gen == 0:
               x = 0
               y -= yincr
    
    def pyramid(self, limits, xmax, ymax, num_rows, file):
        # num_rows should include both pyramid AND rectangular grid in order
        # that each "generation" be equal        
        
        xmax = float(xmax)        
        ymax = float(ymax)
         
        y = ymax
        yprime = 0
        # number of inches / (number of rows - 1)        
        yincr = ymax/(num_rows - 1)
        
        file.write('0 [pos="%f, %f!"];\n' % (xmax/2, y))
        
        for a_range in limits:
            range_min = a_range[0]
            range_max = a_range[1]
            
            yprime += yincr
            y -= yincr
            # outermost nodes are on the lines from the origin to the outermost 
            # nodes of the first generation of the rectangular grid (a'b/a = b')            
            row_width = (yprime*xmax)/(yincr*(len(limits)+1))
            x = xmax/2 - row_width/2
            for n in range(range_min, range_max):
                xincr = row_width / (range_max - range_min - 1)
                file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
                x += xincr
        
        # starting position for grid        
        y -= yincr
        return y
        
    def dot_for_graphviz(self, selected_layer, focus):                 
        # In command line: dot -Kfdp -n -Textension -o out_name.extension in_name.dot
        # e.g., dot -Kfdp -n -Tps -o sample.ps  dot_for_graphviz.dot (prints paths which can be opened in Illustrator)
        
        phylo_prefix = "phylo_"
        keyword_prefix = "keyword_"
        both_prefix = "both_"
        
        phylo_colors = self.colors_for_graphviz("rainbow")        
        
        edges = []
        for child, parents in enumerate(self.parentage):
            if parents:
                for parent in parents:
                    row = "/*bottom*/ %d -> %d [color=black, layer=\"bottom\", style=\"solid\"];\n" % (parent, child)        
                    
                    if 'phylo' in focus:               
                       if (selected_layer in self.ancestors[parent]) or (parent == selected_layer):
                            # write rows                      
                            row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"bold\"];\n" 
                                   % (parent, child, phylo_colors[0]))
                     
                    elif selected_layer == "all":
                        pass
                    
                    else:
                        if child in self.inheritance_interactions[parent] and (selected_layer == "top" or type(selected_layer) is int):                                                                                                   
                             for citation, keyword in self.inheritance_interactions_colored[parent]:
                                    if child == citation:
        
                                        if self.inheritance_interactions[parent].count(child) <= 1:
                                            style = "solid"
                                        else:
                                            style = "bold"
                                        
                            
                                        if focus == "both":
                                            # phylo edges                            
                                            if selected_layer in self.ancestors[child]:
                                                    # write rows                                    
                                                    row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"%s\"];\n" 
                                                           % (parent, child, phylo_colors[0], style))     
                                        else:            
                                            if type(selected_layer) == int:
                                                if keyword == selected_layer:                                    
                                                    row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"%s\"];\n" 
                                                           % (parent, child, self.keyword_colors[keyword % len(self.keyword_colors)], style))
                                            elif selected_layer == "top":
                                                row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"%s\"];\n" 
                                                           % (parent, child, self.keyword_colors[keyword % len(self.keyword_colors)], style))
                   
                    edges.append(row)
                
        edges.sort()
       
        # get the path
        full_path = os.path.realpath(__file__)        
        start_path = os.path.dirname(full_path)               
        
        if 'phylo' in focus:        
            output_file = phylo_prefix + str(selected_layer) + ".dot"
        elif 'key' in focus:
            output_file = keyword_prefix + str(selected_layer) + ".dot"
        elif 'both' in focus:
            output_file = both_prefix + str(selected_layer) + ".dot"
            
        final_path = os.path.join(start_path, 'network', 'to_file', output_file)
        file = open(final_path, 'w')     
        
        if not selected_layer in ("all", "bottom"):
            selected_layer = "top"
            
        # general attributes     
        file.write(
"""digraph inheritance {
center=true;
node [shape=point]
node [layer=all];
splines=line;
edge [arrowhead=none];
layers="bottom:top";
layerselect="%s";
overlap="true";

""" % selected_layer
)               
        # nodes (house plot)         
        xmax = float(30)        
        ymax = float(30)
        num_rows = 15
        
        limits = [(1, 3), (3, 13), (13, 33), (33, 63), (63, 100)]
        starting_y = self.pyramid(limits, xmax, ymax, num_rows, file)
        self.grid(100, 1000, 20, xmax, 5, starting_y, num_rows, file) 
         
        
        # edges        
        for row in edges:            
            file.write(row)
        file.write('}\n')        
        file.close()


#        final_path = os.path.join(start_path, 'network', 'to_file', 'ancestors.txt')
#        file = open(final_path, 'w')     
#        for patent, ancestors in enumerate(self.ancestors):
#            file.write('%s, %s\n' % (patent, ancestors))
           
class Sampler(object):  
    
    def __init__(self, pool, min, max, count):
        self.pool = pool
        self.min = min
        self.max = max
        # list of the number of times each sample has been previously sampled        
        self.sample_count = count
        
    def unweighted_sampling(self):
        samples = ()
        for i in range(randint(self.min, self.max)):
            a_sample = randint(0, self.pool.now_forming - 1)
            if not a_sample in samples:           
                samples += (a_sample, )
                self.update_count(a_sample)
        
        return samples
    
    def weighted_sampling(self):        
        self.dummy_weights = list(self.pool.weights)    
        self.dummy_summed_weights = self.pool.summed_weights
        
        samples = ()
        for i in range(randint(self.min, self.max)):
            rwg = RandomWeightedGenerator()            
            a_sample = rwg.generate(self.dummy_weights, self.dummy_summed_weights)
            if a_sample is not None:       
                samples += (a_sample, )
                self.update_dummy_weights(a_sample)
                self.update_count(a_sample)
        
        return samples
    
    def update_dummy_weights(self, sample):
        self.dummy_summed_weights -= self.dummy_weights[sample]           
        self.dummy_weights[sample] = 0
        
    def update_count(self, sample):
        self.sample_count[sample] += 1

        
class RandomWeightedGenerator(object):

    def generate(self, weights, sum):      
        rnd = random() * sum
        for i, w in enumerate(weights):                  
            rnd -= w
            if rnd < 0:
                return i

        
class LineGraph(object):

    def prep_counts(self, citation_count, counts):
        counts_to_plot = 1000        
        
        # Empty lists for each patent        
        self.counts_by_patent = [[] for i in range(counts_to_plot)]
                
        # most cited patents
        ordered_patents_and_counts = sorted(enumerate(citation_count), key=itemgetter(1))        
        reversed_ps_and_cs = ordered_patents_and_counts[::-1]     
        most_cited_ps_and_cs = reversed_ps_and_cs[0:counts_to_plot]
        
        most_cited = []
        for tuple in most_cited_ps_and_cs:
            most_cited.append(tuple[0])

        # Counts vs time for 100 most cited patents
        for i, patent in enumerate(most_cited):
            for count_at_t in counts:
                this_list = self.counts_by_patent[i]
                this_list.append(count_at_t[patent])
                
        return self.counts_by_patent
    
    def plot_counts(self, to_plot):
        
        for i, v in enumerate(to_plot):
            plt.plot(v)
            #plt.xlim(0, 5000) 
            plt.ylabel("Number of Citations")
            plt.xlabel("Time")
            print "List %r done" % i
        
        plt.show()                   
               

class Network(object):
    
    def simple_r_citation_matrix(self, parentage):
        file = open('citation_network.txt', 'w')
        column_headers = "parent child\n"
        file.write(column_headers)
        
        # Citations are parents, patents are children
        for child_and_parents in enumerate(parentage):
            for parent in child_and_parents[1]:
                line = "%i %i\n" % (parent, child_and_parents[0])             
                file.write(line)
       
        file.close()



                
class Testing(object):
    
    def lets_cite(self):              
        self.some_patents = Uniform(number_of_patents=1000, citations_per_patent=3, avg=False, 
                 min_citations_per_patent=0, initial_weight = 1)
        self.some_patents.form_patents()
        
        self.some_patents.write_parentage()
        self.some_patents.write_count()
        
    def lets_prep_lines(self):    
        self.my_lines = LineGraph()
        counts_by_patent = self.my_lines.prep_counts(self.some_patents.citation_count, 
                                               self.some_patents.counts)        
                                               
        file = open('counts_by_patent', 'w')
        cPickle.dump(counts_by_patent, file)
        file.close()
    
    def lets_plot(self):
        file = open('counts_by_patent')
        to_plot = cPickle.load(file)
        my_plot = LineGraph()
        my_plot.plot_counts(to_plot)
        file.close()       
    
    def lets_network(self):
        my_network = Network()
        my_network.simple_r_citation_matrix(self.some_patents.parentage)

    def lets_keyword(self):
        self.key_up = Keywords("parentage.csv", keywords_per_patent=10, avg=False, 
                               min_keywords_per_patent=0, num_keywords=100)
        self.key_up.assign_keywords()
        self.key_up.write_traits_by_patent()        
        
        self.key_up.first_degree_chains()
        self.key_up.write_inheritance_count()
        
        self.key_up.colors_for_graphviz("rainbow")        

        layers = ['all', 'bottom', 'top']        
        for layer in layers:        
            self.key_up.dot_for_graphviz(layer, "keyword")
        
        top_keywords = self.key_up.get_top_keywords(10)
        print(self.key_up.get_top_keywords(100))
        for keyword, count in top_keywords:
            self.key_up.dot_for_graphviz(keyword, "keyword")
         
        some_ancestors = [210, 550, 840] 
        for ancestor in some_ancestors:
            self.key_up.dot_for_graphviz(ancestor, "phylo")
            
        self.key_up.measure_inheritance()
            
start_time = time.time()

test = Testing()
#test.lets_plot()
test.lets_cite()
#test.lets_prep_lines()
#test.lets_network()
test.lets_keyword()

elapsed_time = time.time() - start_time  
print elapsed_time  