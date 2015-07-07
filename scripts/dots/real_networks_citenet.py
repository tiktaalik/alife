from pymongo import MongoClient
import trait_matrix as tm
import extract_traits as et


c = MongoClient()

collection = c.patents.traits

def walk_down_graph(pno,depth,threshold,trait='top_tf-idf'):
    count = 0
    p = collection.find_one({'_id':pno},{'_id':1, 'citedby':1, trait:1})
    gens = [[p]]
    just_nodes = [p['_id']]
    node_gens = [[p['_id']]]
    links = []
    
    for i in range(1,depth):
        parents = gens[i-1]
        next_gen = []
        new_nodes = []

        for par in parents:
            children_pnos = par['citedby']
            children = collection.find({'_id': {"$in":children_pnos}}, {'_id':1, 'citedby':1, trait:1})
            
            for child in list(children):
                if 'citedby' not in child.keys():
                    count += 1
                elif len(child['citedby']) >= threshold:
                    links.append((par['_id'],child['_id']))
                    # add only previously unseen nodes
                    if child['_id'] not in just_nodes:
                        next_gen.append(child)
                        new_nodes.append(child['_id'])
                        just_nodes.append(child['_id'])

        gens.append(next_gen)
        node_gens.append(new_nodes)
    print(count, 'without citedby')
    # get rid of the gens, just a list of records
    recs = []
    count = 0
    for gen in gens:
        recs += gen

    for rec in recs:
        # rename '_id' to 'pno' 
        rec['pno'] = rec.pop('_id')
        # rename trait to 'traits'
        if trait in rec.keys():
            rec['traits'] = rec.pop(trait)
        else:
            count += 1
            rec['traits'] = []

    count = round(float(count)/float(len(just_nodes)) * 100)
    print('%d%% without traits' % count)
    recs = et.recs_by_pno(recs)

    sparse = tm.sparse_matrix(just_nodes,recs,'traits')

    trait_dict = {}
    for i,pno in enumerate(just_nodes):
        trait_dict[pno] = sparse[i]



    return (just_nodes,node_gens,links,trait_dict)