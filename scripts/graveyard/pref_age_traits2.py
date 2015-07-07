# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 19:30:33 2014

@author: zodcomp
"""


from random import random, randint
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
        self.define_patents_and_citations()
        self.define_citation_count()
        self.define_weights()       
        
    def define_patents(self):       
        self.patents = [i for i in range(self.number_of_patents)]
    
    def define_patents_and_citations(self):
        # Form the first patent manually!      
        self.patents_and_citations = [(0, ())]

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
            
            citations = citation_sampler.weighted_sampling()
            self.patents_and_citations.append((self.now_forming, citations))
            
            self.citation_count = citation_sampler.sample_count
            self.counts.append(list(self.citation_count))
                
            if self.now_forming % 1000 == 0:
                print "Now forming patent_%i" % self.now_forming
                
        return self.patents_and_citations

#==============================================================================
# Save output
#           
#    -patents_and_citations
#    -final count for each patent        

    def write_patents_and_citations(self):
        file = open('patents_and_citations.txt', 'w')
            
        for tuple in self.patents_and_citations:
            patent, citations = zip(tuple)
            patent_and_citations = str((patent, citations[0]))
            patent_and_citations = "%s\n" % patent_and_citations
            file.write(patent_and_citations)
        
        file.close()
    
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
            
            citations = citation_sampler.unweighted_sampling()
            self.patents_and_citations.append((self.now_forming, citations))
            
            self.citation_count = citation_sampler.sample_count
            self.counts.append(list(self.citation_count)) 
                           
            if self.now_forming % 1000 == 0:
                print "Now forming patent_%i" % self.now_forming
    
        return self.patents_and_citations
        
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

    def __init__(self, patents_and_citations_file, keywords_per_patent=5, avg=True, min_keywords_per_patent=0):
        self.number_of_patents = number_of_patents        
        self.keywords_per_patent = keywords_per_patent
        if avg:
            self.min_keyword_per_patent = min_keywords_per_patent                                    
            self.max_keywords_per_patent = (self.keywords_per_patent - self.min_keywords_per_patent) * 2
        else:
            self.min_keywords_per_patent = self.keywords_per_patent
            self.max_keywords_per_patent = self.keywords_per_patent

    def define_keywords(self):
        self.patents = [i for i in range(self.number_of_keywords)]
    
    def define_patents_and_keywords(self):
        self.patents_and_keywords = []
        
    def patents_and_citations(self):
        self.patents_and_citations = []
        with open(self.patents_and_citations_file, newline='') as inputfile:
            for row in csv.reader(inputfile):
                self.patents_and_citations.append(row)
        
        self.number_of_patents = len(self.patents_and_citations)
    
    def define_weights(self):
        self.weights = []
        
    def assign_keywords(self):
        keyword_sampler = Sampler(self, self.min_keywords_per_patent, self.max_keywords_per_patent, 0) 
        
        for i in range(self.number_of_patents):
            assigned_keywords = keyword_sampler.unweighted_keywords()
            self.patents_and_keywords.append(assigned_keywords)

    def unweighted_keywords(self):
        samples = {}
        for i in range(randint(self.min, self.max)):
            a_sample = randint(0, 100)
            if not a_sample in samples:           
                samples |= a_sample
        
        return samples
        
    def count_first_degree_chains(self):       
        keywords_inherited = [0 for i in range(len(self.patents_and_citations))]
        for child, parents in zip(*self.patents_and_citations):
            for parent in parents:
                intersection = self.patents_and_keywords[parent].update(self.patents_and_keywords[child])                 
                if intersection:
                   keywords_inherited[parent] += len(intersection)
                
    def follow_chain(self, parent, children):
        for child in children:
           intersection = self.patents_and_keywords[parent].update(self.patents_and_keywords[child])              
           if intersection: 
                pass                            
         
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
    
    def simple_r_citation_matrix(self, patents_and_citations):
        file = open('citation_network.txt', 'w')
        column_headers = "parent child\n"
        file.write(column_headers)
        
        # Citations are parents, patents are children
        for p_and_cs in patents_and_citations:
            for citation in p_and_cs[1]:
                line = "%i %i\n" % (citation, p_and_cs[0])               
                file.write(line)
       
        file.close()



                
class Testing(object):
    
    def lets_cite(self):              
        self.some_patents = Aging(number_of_patents=20000, citations_per_patent=5, avg=False, 
                 min_citations_per_patent=0, initial_weight = 1)
        self.some_patents.form_patents()
        
        #self.some_patents.write_patents_and_citations()
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
        my_network.simple_r_citation_matrix(self.some_patents.patents_and_citations)

    def lets_keyword(self):
        self.key_up = Keywords(number_of_patents=, keywords_per_patent=5, avg=False, min_keywords_per_patent=0)

start_time = time.time()

test = Testing()
test.lets_plot()
#test.lets_cite()
#test.lets_prep_lines()
#test.lets_network()

elapsed_time = time.time() - start_time  
print elapsed_time  
