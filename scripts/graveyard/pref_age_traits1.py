# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 19:30:33 2014

@author: zodcomp
"""


from random import random, randint
import matplotlib.pyplot as plt
from operator import itemgetter
import cPickle




class Patents(object):
    
    def __init__(self, number_of_patents=100, citations_per_patent=5, avg=True, 
                 min_citations_per_patent=0, initial_weight = 1):
        self.number_of_patents = number_of_patents
        self.citations_per_patent = citations_per_patent
        
        # set min and max so number of citations averages citations_per_patent
        if avg:
            self.min_citations_per_patent = min_citations_per_patent                                    
            self.max_citations_per_patent = (self.citations_per_patent - self.min_citations_per_patent) * 2 - 1 # subtract 1 for use in randint() (endpoints are included)
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
        self.define_aging_coefficients()
        
    def define_patents(self):       
        self.patents = []
        
        for item in range(self.number_of_patents):
            self.patents.append(item)
            
        return self.patents
    
    def define_patents_and_citations(self):
        # Form the first patent manually!      
        self.patents_and_citations = [(0, ())]

    def define_citation_count(self):
        self.citation_count = [0 for i in range(self.number_of_patents)]
        self.counts = []
    
    def define_weights(self):
        # 0 until update prior to assignment of citations 
        self.weights = [0 for i in range(self.citations_per_patent)]   
   
    def define_aging_coefficients(self):
        self.aging_coefficients = []        
        for i in range(self.citations_per_patent):
            self.aging_coefficients.append((self.citations_per_patent + 1 - i) ** -1.45)            

#==============================================================================
    def form_patents(self):
        for self.now_forming in self.patents[1:self.number_of_patents]:
            self.update_weights()            
            citation_sampler = Sampler(self, self.min_citations_per_patent, self.max_citations_per_patent, self.citation_count) 
            
            citations = citation_sampler.weighted_sampling()
            self.patents_and_citations.append((self.now_forming, citations))
            
            self.citation_count = citation_sampler.sample_count
            self.counts.append(list(self.citation_count))
    
        return self.patents_and_citations

#==============================================================================    
    def unweighted_citing(self):
        citations = [randint(0, self.now_forming - 1) for i in range(randint(self.min_citations_per_patent, self.max_citations_per_patent))]
        return citations

#==============================================================================       
    
    def update_weights(self):
        self.update_aging_coefficients()        
        # probability(k) ~ 1 + (k * w)(d^a) where k is the patent, w is the weight, 
        # d is the age (t - i), and a is the aging attachment factor
        self.weights = [1 + (self.citation_count[i] ** 2) * self.aging_coefficients[i] for i in range(self.now_forming)]

        self.summed_weights = sum(self.weights)
            
    def update_aging_coefficients(self):
        self.aging_coefficients.insert(0, self.now_forming ** -1.45)

#==============================================================================
    def write_patents_and_citations(self):
        file = open('patents_and_citations.txt', 'w')
            
        for tuple in self.patents_and_citations:
            patent, citations = zip(tuple)   
            patent = "patent_%d" % patent 
            patent_and_citations = str((patent, citations[0]))
            patent_and_citations = "%s\n" % patent_and_citations
            file.write(patent_and_citations)
        
        file.close()
    
    def write_counts(self):
        file = open('counts.txt', 'w')

        counts = self.counts[::-1]
        for v in counts:
            count =  v
            count = str(count)
            count = "[%s],\n" % count   
            file.write(count)
        file.close()
#==============================================================================
            
class Sampler(object):    
    
    def __init__(self, pool, min, max, count):
        self.pool = pool
        self.min = min
        self.max = max
        # list of the number of times each sample has been previously sampled        
        self.sample_count = count
        
    def weighted_sampling(self):        
        self.dummy_weights = list(self.pool.weights)    
        self.dummy_summed_weights = self.pool.summed_weights
        
        samples = ()
        for i in range(randint(self.min, self.max)):
            a_sample = self.random_weighted_generator()
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
        
    def random_weighted_generator(self):      
        rnd = random() * self.dummy_summed_weights
        for i, w in enumerate(self.dummy_weights):                  
            rnd -= w
            if rnd < 0:
                return i

        
class LineGraph(object):

    def __init__(self):
        pass
    
    def prep_counts(self, citation_count, counts):
        # Empty lists for each patent
        self.counts_by_patent = []        
        for i in range(100):
            self.counts_by_patent.append([])
                
        # 100 most cited patents
        ordered_patents_and_counts = sorted(enumerate(citation_count), key=itemgetter(1))        
        reversed_ps_and_cs = ordered_patents_and_counts[::-1]     
        most_cited_ps_and_cs = reversed_ps_and_cs[0:100]
        
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
        self.some_patents = Patents(100, 5)
        self.some_patents.form_patents()
        
        self.some_patents.write_patents_and_citations()
        print sum(self.some_patents.citation_count)
        
    def lets_prep_lines(self):    
        self.my_lines = LineGraph()
        counts_by_patent = self.my_plot.prep_counts(self.some_patents.citation_count, 
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
    
test = Testing()
#test.lets_plot()
test.lets_cite()
test.lets_network()