# March 05 2015
# Zackary Dunivin
#
# Assigns traits to pre-generated patent citation network 
# recorded in a CSV.
#
# Returns a CSV comprising a sparse matrix wherein the rows represent 
# a patent index and the columns represent the index of a trait type.
#
#

import csv
import os
import numpy as np
import rwg
from random import randint
import pickle
import dots.trait_matrix as tm
from pprint import pprint




class Traits(object):

    def __init__(self, traits_pickle = None, real_network = None, real_traits=None, num_records=1000, traits_per_patent=5, avg=True, min_traits=0, num_traits=100, gen_len=100, dist = 'flat'):
        # traits pickle is a dictionary of where k is trait and v is trait frequency
        # real_network is a dictionary where keys are pnos and values are parents
        # real_traits is be a tuple where:
        # tup[0] = traits for the first patent,
        # tup[1] = dict where k is pno and v is traits
        #
        self.traits_pickle = traits_pickle
        self.real_network = real_network
        self.real_traits = real_traits 
        self.num_records = num_records
        self.traits_per_patent = traits_per_patent
        self.num_traits = num_traits
        self.gen_len = gen_len
        self.dist = dist

        if avg:
            self.min_traits = min_traits
            self.max_traits = (self.traits_per_patent - self.min_traits) * 2
        else:
            self.min_traits = self.traits_per_patent
            self.max_traits = self.traits_per_patent
        
        if 'emp' in self.dist:  
            self.extract_empirical()

        self.define_prior_to_assignment()

    def define_prior_to_assignment(self):
        """Calls the requisite procedures for trait assignment"""
        self.define_weights()
        self.define_phenomes()
        self.define_traits()


    def define_weights(self):
        """Reads probabilities from a csv for which each row corresponds
         to a trait and the column (only one) represents the probability
         that it will be cited."""
        # probabilities
        summed_weights = sum(self.weights)
        self.probs = [weight/float(summed_weights) for weight in self.weights]

    def define_phenomes(self):
        self.phenomes = []
    
    def define_traits(self):
        """traits become traits when assigned. By default, they are flat.
        However, they may be derived from empirical traits. If so, the number 
        of traits needs to reflect the number of empirical trait types."""
        if self.dist == 'flat':
            return

    def open_files(self):
        """Opens the csv to which the phenomes will be written"""
        self.p_file = open('phenomes.csv', 'wb')
        self.p_writer = csv.writer(self.p_file)
        
    def close_file(self, f):
        """Dumps all remaining data into a file and then closes it"""
        f.flush()
        os.fsync(f.fileno())
        f.close()
        
    def cleanup(self):
        """Securely closes all open files"""
        self.close_file(self.p_file)
    
#==============================================================================
# csv    
#==============================================================================
    def write_phenomes(self):
        """Writes the phenomes (assigned triats) to a csv for which each
         row corresponds to a patent and each column a trait which has
         been assigned to that patent."""
        with open('phenomes.csv', 'w') as f:
            writer = csv.writer(f)
            list_of_lists = [list(i) for i in self.phenomes]
            writer.writerows(list_of_lists)
            
#==============================================================================
# assignment
#==============================================================================
    def assign_traits(self):
        """Assigns traits to each patent"""
        self.new_pool()
        for i in range(self.num_records):
            
            if self.pool < self.traits_per_patent*5:
                self.new_pool()            
            traits = set()
            while len(traits) < randint(self.min_traits, self.max_traits):
                trait = self.pool.pop(0)
                traits.add(trait)
            
            self.phenomes.append(frozenset(traits))
            
            if i % self.gen_len == 0:
                self.new_pool()   
                
    def new_pool(self):
        """Generates the pool of traits from which traits will be
         assigned"""
        if self.traits_pickle:
            n = self.gen_len * self.traits_per_patent * 2
            self.pool = rwg.generate(n, self.probs)
        else:
            n = self.traits_per_patent * 1000 * 2
            self.pool = list(np.random.randint(0, self.num_traits, n))


class Real_traits(Traits):
    def define_prior_to_assignment(self):
        self.get_real_network()
        self.get_real_traits()
        super(Real_traits,self).define_prior_to_assignment()


    def get_real_network(self):
        # network is k = child, v = parents
        self.network = self.real_network

        # we need a list of patents by age (pno) so we assign traits to the oldest patents first
        self.patents = self.network.keys()
        self.patents = sorted(self.patents)

        self.num_records = len(self.patents)

    def get_real_traits(self):
        self.initial_traits = self.real_traits[0]
        
        # dict where k = pno and v = traits
        self.traits_by_patent = self.real_traits[1]
        # get an s_matrix ordered by pno
        s_matrix = []
        for pno in self.patents:
            traits = self.traits_by_patent[pno]
            s_matrix.append(traits)

        trait_freqs = tm.trait_freqs(s_matrix)

        self.traits_index = trait_freqs
        self.traits_index = sorted(self.traits_index)

        # get the weights
        alpha_trait_freqs = []
        for trait in self.traits_index:
            alpha_trait_freqs.append(trait_freqs[trait])

        self.weights = alpha_trait_freqs


    def assign_traits(self):
        # first patent
        self.phenomes.append(self.initial_traits)

        self.new_pool()
        for patent in self.patents[1::]:
    
            traits = set()
            while len(traits) < randint(self.min_traits, self.max_traits):
                # assign parental traits
                parents = self.network[patent]
                for parent in parents:
                    p_traits = self.traits_by_patent[parent]  
                    
                    # some patents may not have traits
                    # if not stop looking at this parent
                    if not p_traits:
                        continue 
                    
                    # shares two traits with each parent on average
                    x = np.random.randint(0,len(p_traits))
                    for i in range(x):
                        y = np.random.randint(0,len(p_traits))
                        trait = p_traits.pop(y)
                        # convert to index
                        trait = self.traits_index.index(trait)
                        traits.add(trait)

                # assign whatever's left
                trait = self.pool.pop(0)
                traits.add(trait)
                if self.pool == None:
                    self.new_pool()

            self.phenomes.append(frozenset(traits))
    

    def assign_traits(self):
        # first patent
        self.phenomes.append(self.initial_traits)

        self.new_pool()
        for patent in self.patents[1::]:
    
            traits = set()
            while len(traits) < randint(self.min_traits, self.max_traits):
                trait = self.pool.pop(0)
                traits.add(trait)
                if self.pool == None:
                    self.new_pool()

            self.phenomes.append(frozenset(traits))
