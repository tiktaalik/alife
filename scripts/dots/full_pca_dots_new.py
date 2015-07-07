n# pca for all the patents in all of the geneologies we've chosen
# look at the geologies
# see how homogeneous they are

# do over for all of the graphs with pref traits

# do over with emp freqs but not pref traits


import pickle
import trait_matrix as tm
import extract_traits as et
import dots
import time


def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z


pats = {'rsa':{'pno':4405829,'threshold':400},
        'pcr':{'pno':4683202,'threshold':150},
        'zeolites':{'pno':4061724,'threshold':60},
        'semiconductors':{'pno':4064521,'threshold':125},
        'stents':{'pno':4655771,'threshold':350},
        'browser':{'pno':5572643,'threshold':250},
        'bubblejet':{'pno':4723129,'threshold':75},
        'nonwovenwebs':{'pno':4340563,'threshold':100},
        'microarrays':{'pno':5143854,'threshold':175},
        'cellphone':{'pno':5103459,'threshold':225}
        }
"""
# the index for the sparse matrix
for pat in {'bubblejet':{'pno':4723129,'threshold':75}}:
    if pat in ['zeolites','stents']:
        continue

    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    f_name = '_'.join([pat,'network',str(depth),'full'])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    network = pickle.load(f)

    trait_dict = network[3]
    
    #full_dict = merge_two_dicts(full_dict,trait_dict)
    full_dict = trait_dict

    pca_patents = full_dict.keys()
    pca_patents = sorted(pca_patents)

    # get rid of the pnos
    sparse = []
    for pno in pca_patents:
        sparse.append(full_dict[pno])
    start = time.time()
    colors = dots.get_pca_colors(sparse,pca_patents)
    print((time.time()-start)/60)

    f_name = pat + '_pca_dict.p'
    f = open(f_name, 'wb')
    pickle.dump(colors,f)
"""
"""
full_dict = {}
for pat in pats:
    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    f_name = '_'.join([pat,'network',str(depth),'full'])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    network = pickle.load(f)

    trait_dict = network[3]
    
    full_dict = merge_two_dicts(full_dict,trait_dict)

    all_pats = full_dict.keys()

    print(len(all_pats))
"""

def get_full_dict(pats):
    full_dict = {}
    for pat in pats:
        pno = pats[pat]['pno']
        depth = 5
        threshold = pats[pat]['threshold']
        trait='top_tf-idf'

        trait_dict = get_dict(pat,depth,threshold)
        
        full_dict = merge_two_dicts(full_dict,trait_dict)

    return full_dict

def get_dict(pat,depth,threshold):
    f_name = '_'.join([pat,'network',str(depth),str(threshold)])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    network = pickle.load(f)

    trait_dict = network[3]

    return trait_dict

"""
dicts = {}
for pat in pats:
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'
    d = get_dict(pat,depth,threshold)
    nodes = d.keys()
    dicts[pat] = frozenset(nodes)
    

for pat1 in dicts:
    d1 = dicts[pat1]
    print(pat1)
    for pat2 in dicts:
        d2 = dicts[pat2]
        print(pat2,len(d1.intersection(d2)))

"""



# output the dots!
for pat in ['zeolites']:
    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    # get the pca pickle
    f_name = pat + '_pca_dict.p'
    f = open(f_name, 'rb')
    pca_dict = pickle.load(f)

    f_name = '_'.join([pat,'network',str(depth),str(threshold)])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    network = pickle.load(f)

    network = list(network)
    #network[3] = full_dict



    num_traits = 10
    rank_length = 15
    file_name = pat + "_network_pca_full"
    focus = 'both' # 'nodes','edges',both
    sharing = dots.pca_coloring
    coloring = None
    colors = 'red' #['indigo','forestgreen','gold','red']
    traits = None

    dots.write_dot(network,num_traits,rank_length,file_name,focus,sharing,coloring,colors,traits,pca_dict)



              
            