# get a real network

import pickle
import real_networks_citenet as rn

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

def get_network_pickle(pat,pno,depth,threshold,trait):
    results = rn.walk_down_graph(pno,depth,threshold,trait)
    print(pat)
    print('nodes: '+ str(len(results[0])) + ' edges: ' + str(len(results[2])))
    print('\n')

    if threshold == 1:
        thresh = 'full'
    else: 
        thresh = str(threshold)

    f_name = '_'.join([pat,'network',str(depth),thresh])
    f_name = f_name + '.p'
    f = open(f_name,'wb')
    pickle.dump(results,f)


def all_pickles(pats,trait):
    for pat in pats:
        #pat = 'nonwovenwebs'
        pno = pats[pat]['pno']
        depth = 5
        threshold = 0 # pats[pat]['threshold']

        get_network_pickle(pat,pno,depth,threshold,trait)

#get_network_pickle('bowflex',4620704,5,1,'top_tf-idf')

all_pickles(pats,'doc_vec')

"""
some_pats = ['stents','zeolites','pcr','nonwovenwebs']
some_pats = ['bubblejet']
for pat in some_pats:
    pat = pat
    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    threshold -= 10
    get_network_pickle(pat,pno,depth,threshold,trait)

    threshold += 20
    get_network_pickle(pat,pno,depth,threshold,trait)
"""