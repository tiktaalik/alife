# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 00:00:55 2014

@author: zodcomp

Features: 
User sets total number of patents
Weighted citation
Unweighted citation
"""

from random import random, randint
import matplotlib.pyplot as plt
import collections




class Patents(object):
    
    def __init__(self, number_of_patents=100, citations_per_patent=5, initial_weight = 1):
        self.number_of_patents = number_of_patents
        self.citations_per_patent = citations_per_patent
        self.initial_weight = initial_weight 
        self.define_patents()
        self.define_weights()
        self.define_citation_count()
    
    def define_patents(self):       
        self.patents = []
        
        for item in range(self.number_of_patents):
            self.patents.append(item)
            
        return self.patents.reverse()
        
    def form_patents(self):   
        self.patents_and_citations = []
        self.number_not_formed = self.number_of_patents - 1
        
        for self.now_forming in self.patents[0:self.number_of_patents - 5]:
            print "forming_patent: %r" % self.now_forming
            # Remove from the sum the weight of the currently forming patent
            # as it is not eligible for citing            
            del self.weights[self.now_forming]

            citations = self.weighted_citing()          
            self.patents_and_citations.append((self.now_forming, citations))
            self.number_not_formed -= 1
            
            self.counts.append(list(self.citation_count))
    
        return self.patents_and_citations
    
    def unweighted_citing(self):
        citations = [randint(self.number_of_patents - 1 - self.number_not_formed, self.number_of_patents - 1) for i in range(5)]
        return citations
        
    def weighted_citing(self):             
        self.update_weights()
        self.dummy_weights = list(self.weights)    
        self.dummy_summed_weights = self.summed_weights
        
        citations = ()
        for i in range(5):
            a_citation = self.random_weighted_citation()
            citations += (a_citation, )
            self.update_dummy_weights(a_citation)
            self.update_count(a_citation)
        
        return citations
    
    def update_weights(self):
        # probability(k) ~ (k^w)(d^a) where k is the patent, B is the weight, 
        # d is the age (t - i), and a is the aging attachment factor
        self.weights = [float(1 + (2 * self.citation_count[i]) * ((self.now_forming - i) ** -1.1))  for i in range(len(self.weights))]
        
        #for i, v in enumerate(self.weights):            
        #    self.weights[i] = float(1 + (2 * self.citation_count[i]) * ((self.now_forming - i) ** -1.1))        
        
        self.summed_weights = sum(self.weights)
    
    def update_dummy_weights(self, patent):        
        self.dummy_summed_weights -= self.dummy_weights[patent]           
        self.dummy_weights[patent] = 0
        
    def update_count(self, patent):
        self.citation_count[patent] += 1
        
    def define_citation_count(self):
        self.citation_count = [0 for item in self.patents]
        self.counts = []
    
    def define_weights(self):
        self.weights = [self.initial_weight for key in self.patents]
        self.summed_weights = self.initial_weight * (self.number_of_patents)

    def random_weighted_citation(self):      
        rnd = random() * self.dummy_summed_weights

        for i, w in enumerate(self.dummy_weights):                  
            rnd -= w
            if rnd < 0:              
                return i

    def write_patents_and_citations(self):
        file = open('patents_and_cititions.txt', 'w')
            
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
        
    
    def plot_counts(self):
        # Empty lists for each patent
        counts_by_patent = []        
        for i in range(self.number_of_patents):
            counts_by_patent.append([])
        
        patents_and_counts = []
        # 100 most cited patents
        for patent, count in enumerate(self.citation_count):        
            tuple = (count, patent)            
            patents_and_counts.append(tuple)        
        
        ordered_ps_and_cs = sorted(patents_and_counts)
        reversed_ps_and_cs = ordered_ps_and_cs[::-1]     
        most_cited_ps_and_cs = reversed_ps_and_cs[0:100]
        print most_cited_ps_and_cs
        
        most_cited = []
        for tuple in most_cited_ps_and_cs:
            most_cited.append(tuple[1])
        
        # Counts vs time for 100 most cited patents
        counts_at_t = self.counts[::-1]        
        for counts in counts_at_t:
            
            for patent, count in enumerate(counts):
                    this_list = counts_by_patent[patent]
                    this_list.append(count)
        
        counts_by_most_cited = []        
        for patent in most_cited:
            patent_counts = counts_by_patent[patent]
            counts_by_most_cited.append(patent_counts[::-1])
        
            
        
        for i, v in enumerate(counts_by_most_cited):
            plt.plot(v)
            plt.ylabel("Number of Citations")
            plt.xlabel("Time")
            print "List %r done" % i
        
        plt.show()
        
               
some_patents = Patents(10000)
the_ps = some_patents.define_patents()
the_ps_and_cs = some_patents.form_patents()

some_patents.plot_counts()




print "OKAY"