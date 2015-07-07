from pymongo import MongoClient
from pprint import pprint
import pickle
import extract_traits as et
import trait_matrix as tm




c = MongoClient()

collection = c.patents.patns

def walk_down_graph(pno,depth,threshold,trait=None):
    p = collection.find_one({'pno':pno},{'pno':1, 'citedby':1, 'sorted_text':1})
    gens = [[p]]
    just_nodes = [p['pno']]
    node_gens = [[p['pno']]]
    links = []
    
    for i in range(1,depth):
        parents = gens[i-1]
        next_gen = []
        new_nodes = []

        for par in parents:
            children_pnos = par['citedby']
            children = collection.find({'pno': {"$in":children_pnos}}, {'pno':1, 'citedby':1, 'sorted_text':1, 'text':1})
            
            for child in list(children):
                if len(child['citedby']) >= threshold:
                    links.append((par['pno'],child['pno']))
                    # add only previously unseen nodes
                    if child['pno'] not in just_nodes:
                        next_gen.append(child)
                        new_nodes.append(child['pno'])
                        just_nodes.append(child['pno'])

        gens.append(next_gen)
        node_gens.append(new_nodes)

    recs = []
    for gen in gens:
        recs += gen

    # get the trait dict
    recs = et.recs_by_pno(recs)
    recs = et.trim_sorted_text(recs,10)

    sparse = tm.sparse_matrix(just_nodes,recs,'traits')

    trait_dict = {}
    for i,pno in enumerate(just_nodes):
        trait_dict[pno] = sparse[i]


    return (just_nodes,node_gens,links,trait_dict)
