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



# the index for the sparse matrix
for pat in pats:
    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    # open subnetwork

    f_name = '_'.join([pat,'network',str(depth),str(threshold)])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    subnetwork = pickle.load(f)
    sub_dict = subnetwork[3]

    # open full network
    f_name = '_'.join([pat,'network',str(depth),'full'])
    f_name = f_name + '.p'

    f = open(f_name, 'rb')
    network = pickle.load(f)
    network = list(network)
    full_dict = network[3]
    
    full_dict = merge_two_dicts(full_dict,sub_dict)

    network[3] = full_dict

    f_name = '_'.join([pat,'network',str(depth),'full'])
    f_name = f_name + '.p'
    f = open(f_name, 'wb')
    network = pickle.dump(network,f)