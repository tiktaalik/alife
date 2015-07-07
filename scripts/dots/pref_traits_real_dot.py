# input is a real subnetwork to which traits are assigned with 
#       preferential attachment
# outputs a python pickle that can be input to dots
# 
# Zackary Dunivin, Reed College Center for Advanced Computing
# June 26 2015

"""
# make sure to look above to find package if not in current dir
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
"""

import traits_emp
import pickle
import extract_traits as et
import trait_matrix as tm
import ..dots


f = open('zeolites_network_5_60.p', 'rb')
network = pickle.load(f)
n = 10

just_nodes = network[0]
node_gens = network[1]
links = network[2]
recs = network[3]
primo = just_nodes[0]


recs = et.recs_by_pno(recs)
recs = et.trim_sorted_text(recs,n)

p_by_c = et.parents_by_child(links)
# first patent doesn't have any parents! we need to add it manually
p_by_c[primo] = []

# get the primogenitors traits
primo_traits = recs[primo]['words']

# the matrix is ordered by the order of pnos in just_nodes
s_matrix = tm.sparse_matrix(just_nodes,recs,'words')
traits_by_pno = tm.traits_by_pno(just_nodes,s_matrix)


real_network = p_by_c
real_traits = [primo_traits,traits_by_pno]
traits_per_patent = n

assigner = traits_emp.Real_traits(real_network = real_network,real_traits = real_traits, traits_per_patent = traits_per_patent)
assigner.assign_traits()

# new traits are ordered by pno
just_nodes = sorted(just_nodes)
# sparse matrix with new traits
new_traits = assigner.phenomes


traits_by_pno = tm.traits_by_pno(just_nodes,new_traits)

network = [just_nodes,node_gens,links,traits_by_pno]


num_traits = 10
rank_length = 15
file_name="zeolites_network"
focus = 'both' # 'nodes','edges',both
sharing = dots.pca_coloring
coloring = dots.single
colors = 'red' #['indigo','forestgreen','gold','red']
traits = None #[chamber, droplet, heat, jet, liquid, orific, outlet, passageway, portion, thermal]

dots.write_dot(network,num_traits,rank_length,file_name,focus,sharing,coloring,colors,traits)





