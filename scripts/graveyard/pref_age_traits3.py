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
        
    def dot_for_graphvis(self):                 

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
                            style = "bold"
                        else:
                            style = "bold"
                        
                        row = "/*top*/ %i -> %i [color=red, layer=\"inherited\", style=\"%s\"];\n" % (parent, child, style)
                    else:
                        row = "/*bottom*/ %i -> %i [color=grey, layer=\"normal\", style=\"solid\"];\n" % (parent, child)
                    edges.append(row)
            
        edges.sort()
       
        file = open('dot_for_graphviz.dot', 'w')    
        
        # general attributes         
        file.write(
"""digraph inheritance {     
center=true;
ratio="2,3";
nodesep=0.02;
node [shape=point];
splines=line;
edge [arrowhead=none];
layers="normal:inherited"; 

"""
)
        # node position 100 count
        xmax = float(10)        
        ymax = float(10)
         
        y = 0
        # number of inches / (number of rows - 1)        
        yincr = ymax/9
         
        
        x = 0       
        for n in range(1000):
            # max inches across
            xincr = xmax/99
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
             
            # new row: reset x and increment y            
            if (n + 1) % 100 == 0:
               x = 0
               y += yincr      
        
        
        # node position
        xmax = float(5)        
        ymax = float(5)
         
        y = 0
        # number of inches / (number of rows - 1)        
        yincr = ymax/14
         
        
        file.write('0 [pos="%f, %f!"];\n' % (xmax/2, y))
         
        y += yincr
        # 1 inch across      
        file.write('1 [pos="%f, %f!"];\n' % (xmax-0.5, y))
        file.write('2 [pos="%f, %f!"];\n' % (xmax+0.5, y))
        
        y += yincr
        x = xmax/2 - 2/2
        for n in range(3,13):
            # 2 inches across
            xincr = 2.000/9
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
        
        y += yincr
        x = xmax/2 - 2.5/2
        for n in range(13,33):
            # 2.5 inches across
            xincr = 2.5/19
 
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
 
        y += yincr
        x = xmax/2 - 3/2
        for n in range(33,63):
            # 3 inches across
            xincr = 3.000/29
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr
 
        y += yincr
        x = xmax/2 - 4/2      
        for n in range(63,101):
            # 4 inches across
            xincr = 4.000/29
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

        file.write(
"""        
{ "rank=same" 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
{ "rank=same" 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32}
{ "rank=same" 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62};
{ "rank=same" 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100};
{ "rank=same" 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200};
{ "rank=same" 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300};
{ "rank=same" 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400};
{ "rank=same" 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500};
{ "rank=same" 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600};
{ "rank=same" 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700};
{ "rank=same" 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800};
{ "rank=same" 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900};
{ "rank=same" 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999};
"""
        )
        
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
        self.some_patents = Preferential(number_of_patents=1000, citations_per_patent=5, avg=False, 
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
        
        self.key_up.dot_for_graphvis()

start_time = time.time()

test = Testing()
#test.lets_plot()
test.lets_cite()
#test.lets_prep_lines()
#test.lets_network()
test.lets_keyword()

elapsed_time = time.time() - start_time  
print elapsed_time  