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




class Patents(object):
    
    def __init__(self, number_of_patents=100, citations_per_patent=5, avg=True, 
                 min_citations_per_patent=0, initial_weight = 1):
        self.number_of_patents = number_of_patents
        self.citations_per_patent = citations_per_patent
        
        # set min and max so that number of citations averages citations_per_patent
        if avg:
            self.min_citations_per_patent = min_citations_per_patent                                    
            self.max_citations_per_patent = (self.citations_per_patent - self.min_citations_per_patent) * 2
        else:
            self.min_citations_per_patent = self.citations_per_patent
            self.max_citations_per_patent = self.citations_per_patent

        self.initial_weight = initial_weight
        self.define_prior_to_forming()
    
#==============================================================================   
    def define_prior_to_forming(self):
        self.define_patents()
        self.define_lineages()
        self.define_citation_count()
        self.define_weights()
        
    def define_patents(self):       
        self.patents = [i for i in range(self.number_of_patents)]
    
    def define_lineages(self):
        # Form the first patent manually!      
        self.lineages = [()]

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
            
            children = citation_sampler.weighted_sampling()
            self.lineages.append(children)
            
            self.citation_count = citation_sampler.sample_count
            self.counts.append(list(self.citation_count))
                
            if self.now_forming % 1000 == 0:
                print "Now forming patent_%i" % self.now_forming

#==============================================================================
# Save output
#           
#    -lineages
#    -final count for each patent        

    def write_lineages(self):
        with open("lineages.csv", "wb") as file:
            writer = csv.writer(file)
            writer.writerows(self.lineages)
            
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
            
            children = citation_sampler.unweighted_sampling()
            self.lineages.append(children)
            
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

    def __init__(self, lineages_file, keywords_per_patent=5, avg=True, min_keywords_per_patent=0):
        self.lineages_file = lineages_file       
        self.keywords_per_patent = keywords_per_patent
        if avg:
            self.min_keywords_per_patent = min_keywords_per_patent                                    
            self.max_keywords_per_patent = (self.keywords_per_patent - self.min_keywords_per_patent) * 2
        else:
            self.min_keywords_per_patent = self.keywords_per_patent
            self.max_keywords_per_patent = self.keywords_per_patent
            
        self.define_prior_to_assignment()

    def define_prior_to_assignment(self):
        self.define_keywords()
        self.define_weights()
        self.define_traits_by_patent()
        self.define_lineages()

    def define_keywords(self):
        #self.keywords = [i for i in range(100)]
        pass
    
    def define_weights(self):
        self.weights = []
            
    def define_traits_by_patent(self):
        self.traits_by_patent = []
        
    def define_lineages(self):
        self.lineages = []
        with open(self.lineages_file) as inputfile:
            for row in csv.reader(inputfile, delimiter=","):
                self.lineages.append(row)
        
        # convert lists of strings to lists of ints
        self.lineages = [map(int, parents) for parents in self.lineages]
        
        self.number_of_patents = len(self.lineages)
    
    def assign_keywords(self):        
        for i in range(self.number_of_patents):
            traits = self.unweighted_keywords()
            self.traits_by_patent.append(traits)

    def unweighted_keywords(self):
        traits = set()
        for i in range(randint(self.min_keywords_per_patent, self.max_keywords_per_patent)):
            sample = randint(0, 100)
            if not sample in traits:           
                traits.add(sample)
        
        return frozenset(traits)
        
    def count_first_degree_chains(self):       
        self.inheritance_count = [0 for i in range(len(self.lineages))]        
        self.inheritance_interactions = [[] for i in range(len(self.lineages))]       
        
        for child, parents in enumerate(self.lineages):

            for parent in parents:
                #dummy_traits_of_parent = set(self.traits_by_patent[parent])
                intersection = self.traits_by_patent[parent].intersection(self.traits_by_patent[child])                
                if intersection:
                    self.inheritance_count[parent] += len(intersection)                 
                    self.inheritance_interactions[parent].append(child*len(intersection))
                    
                
    def follow_chain(self, parent, children):
        for child in children:
           intersection = self.lineages[parent].update(self.lineages[child])              
           if intersection: 
                pass                            
         
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
        for child, parents in enumerate(self.lineages):
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
                        row = "%i -> %i [color=red weight=%i]\n" % (parent, child, weight)
                    else:
                        row = "%i -> %i [color=grey weight=%i]\n" % (parent, child, initial_weight)
                    edges.append(row)
            
        edges.sort()
       
        file = open('dot_for_hiver.dot', 'w')    
        
        file.write("graph inheritance {\n")       
        for n in range(len(self.lineages)):           
            file.write('%d;\n' % n)
        for row in edges:            
            file.write(row)
        file.write('}\n')        
        file.close()       
    
    def dot_for_graphviz(self):                 
        # In command line: dot -Kfdp -n -Textension -o out_name.extension in_name.dot
        # e.g., dot -Kfdp -n -Tps -o sample.ps  dot_for_graphviz.dot (prints paths which can be opened in Illustrator)
        # layerselect has not been working. Instead commment out
        # e.g., "/*top*/" -> "/*top"
        
        edges = []
        for child, parents in enumerate(self.lineages):
            if not parents:
                pass                
                row = "%i;\n" % child
                edges.append(row)
            else:
                for parent in parents:
                    
                    if child in self.inheritance_interactions[parent]:

                        if self.inheritance_interactions[parent].count(child) > 1:
                            style = "solid"
                        else:
                            style = "bold"
                        
                        row = "/*top*/ %i -> %i [color=red, layer=\"inherited\", style=\"%s\"];\n" % (parent, child, style)
                    else:
                        row = "/*bottom*/ %i -> %i [color=black, layer=\"normal\", style=\"solid\"];\n" % (parent, child)
                    edges.append(row)
            
        edges.sort()
       
        file = open('dot_for_graphviz.dot', 'w')    
        
        # general attributes         
        file.write(
"""digraph inheritance {     
center=true;
node [shape=point];
splines=line;
edge [arrowhead=none];
layers="normal:inherited";
overlap="true";

"""
)
#        # node position grid
#        xmax = float(30)        
#        ymax = float(30)
#         
#        y = 0
#        # number of inches / (number of rows - 1)        
#        yincr = ymax/9
#         
#        
#        x = 0       
#        for n in range(1000):
#            # max inches across
#            xincr = xmax/99
#            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
#            x += xincr
#             
#            # new row: reset x and increment y            
#            if (n + 1) % 100 == 0:
#               x = 0
#               y += yincr
        
        # node position house
        xmax = float(30)        
        ymax = float(30)
         
        y = 0
        yprime = 0
        # number of inches / (number of rows - 1)        
        yincr = ymax/14 
        
        file.write('0 [pos="%f, %f!"];\n' % (xmax/2, y))

        
        yprime += yincr
        y += yincr
        row_width = (yprime*xmax)/(yincr*6) # outermost nodes are on the lines from the origin to the outermost nodes on the first line of xmax (a'b/a = b')
        x = xmax/2 - row_width/2
        for n in range(1,3):
            xincr = row_width
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
        
        yprime += yincr
        y += yincr
        row_width = (yprime*xmax)/(yincr*6)        
        x = xmax/2 - row_width/2
        for n in range(3,13):
            xincr = row_width/9
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
        
        yprime += yincr
        y += yincr
        row_width = (yprime*xmax)/(yincr*6)        
        x = xmax/2 - row_width/2
        for n in range(13,33):
            xincr = row_width/19
 
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
        
        yprime += yincr
        y += yincr
        row_width = (yprime*xmax)/(yincr*6)        
        x = xmax/2 - row_width/2
        for n in range(33,63):
            # 3 inches across
            xincr = row_width/29
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
 
        y += yincr
        row_width = (yprime*xmax/2)/(yincr*6) 
        x = xmax/2 - row_width/2    
        for n in range(63,101):
            # 4 inches across
            xincr = row_width/39
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
        
        y += yincr
        x = 0       
        for n in range(101,1000):
            # max inches across
            xincr = xmax/99 
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
             
            # new row: reset x and increment y            
            if n % 100 == 0:
               x = 0
               y += yincr      
        
        # edges        
        for row in edges:            
            file.write(row)
        file.write('}\n')        
        file.close()
           
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
                
        # 100 most cited patents
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
    
    def simple_r_citation_matrix(self, lineages):
        file = open('citation_network.txt', 'w')
        column_headers = "parent child\n"
        file.write(column_headers)
        
        # Citations are parents, patents are children
        for child_and_parents in enumerate(lineages):
            for parent in child_and_parents[1]:
                line = "%i %i\n" % (parent, child_and_parents[0])               
                file.write(line)
       
        file.close()



                
class Testing(object):
    
    def lets_cite(self):              
        self.some_patents = Aging(number_of_patents=1000, citations_per_patent=5, avg=False, 
                 min_citations_per_patent=0, initial_weight = 1)
        self.some_patents.form_patents()
        
        self.some_patents.write_lineages()
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
        my_network.simple_r_citation_matrix(self.some_patents.lineages)

    def lets_keyword(self):
        self.key_up = Keywords("lineages.csv", keywords_per_patent=5, avg=False, min_keywords_per_patent=0)
        self.key_up.assign_keywords()
        self.key_up.write_traits_by_patent()        
        
        self.key_up.count_first_degree_chains() 
        self.key_up.write_inheritance_count()
        
        self.key_up.dot_for_graphviz()

start_time = time.time()

test = Testing()
#test.lets_plot()
test.lets_cite()
#test.lets_prep_lines()
#test.lets_network()
test.lets_keyword()

elapsed_time = time.time() - start_time  
print elapsed_time  