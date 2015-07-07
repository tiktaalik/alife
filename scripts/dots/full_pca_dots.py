# pca for all the patents in all of the geneologies we've chosen
# look at the geologies
# see how homogeneous they are

# do over for all of the graphs with pref traits

# do over with emp freqs but not pref traits


import pickle
import trait_matrix as tm
import extract_traits as et
import dots

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



full_dict = {}
# the index for the sparse matrix
for pat in pats:
    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    f_name = '_'.join([pat,'network',str(depth),str(threshold)])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    network = pickle.load(f)

    trait_dict = network[3]
    
    full_dict = merge_two_dicts(full_dict,trait_dict)



    
# output the dots!
for pat in pats:
    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    f_name = '_'.join([pat,'network',str(depth),str(threshold)])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    network = pickle.load(f)

    network = list(network)
    network[3] = full_dict



    num_traits = 10
    rank_length = 15
    file_name = pat + "_network_pca_full"
    focus = 'both' # 'nodes','edges',both
    sharing = dots.pca_coloring
    coloring = None
    colors = 'red' #['indigo','forestgreen','gold','red']
    traits = None

    dots.write_dot(network,num_traits,rank_length,file_name,focus,sharing,coloring,colors,traits)




              
            