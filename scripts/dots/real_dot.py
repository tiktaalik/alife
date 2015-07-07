import pickle
import trait_matrix as tm
import extract_traits as et
import dots


pats = {'rsa':{'pno':4405829,'threshold':400},
        'pcr':{'pno':4683202,'threshold':150},
        'zeolites':{'pno':4061724,'threshold':60},
        'semiconductors':{'pno':4064521,'threshold':125},
        'stents':{'pno':4655771,'threshold':350},
        'browser':{'pno':5572643,'threshold':250},
        'bubblejet':{'pno':4723129,'threshold':75},
        'nonwovenwebs':{'pno':4340563,'threshold':100},
        'microarrays':{'pno':5143854,'threshold':175},
        'cellphone':{'pno':5103459,'threshold':225},
        'bowflex':{'pno':4620704,'threshold':'full'}
        }

for pat in ['bowflex']:
    #pat = 'nonwovenwebs'
    pno = pats[pat]['pno']
    depth = 5
    threshold = pats[pat]['threshold']
    trait='top_tf-idf'

    f_name = '_'.join([pat,'network',str(depth),str(threshold)])
    f_name = f_name + '.p'



    f = open(f_name, 'rb')
    network = pickle.load(f)
    network = list(network)
    n = 10

    just_nodes = network[0]
    node_gens = network[1]
    links = network[2]
    trait_dict = network[3]

    num_traits = 10
    rank_length = 15
    file_name= pat +'_network'
    focus = 'both' # 'nodes','edges',both
    sharing = dots.parents
    coloring = dots.single
    colors = 'red' #['indigo','forestgreen','gold','red']
    traits = None #[chamber, droplet, heat, jet, liquid, orific, outlet, passageway, portion, thermal]

    dots.write_dot(network,num_traits,rank_length,file_name,focus,sharing,coloring,colors,traits)