from pymongo import MongoClient
import trait_matrix as tm
import extract_traits as et


c = MongoClient()

collection = c.patents.traits

def get_all_traits(trait='doc_vec'):
    all_traits = {}
    pats = collection.find({},{'_id':1,'doc_vec':1})
    for pat in list(pats):
        pno = pat['_id']
        vec = pat['doc_vec']

        all_traits[pno] = vec


    return all_traits



all_traits = get_all_traits()
c.close()

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

f_name = pat + 'full_pca_dict.p'
f = open(f_name, 'wb')
pickle.dump(colors,f)
