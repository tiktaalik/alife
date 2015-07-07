# tools for extracting traits from real networks output by real_networks.py

def flatten_text(D, keylabel = "key"):
    arr = []
    
    for elem in D:
        # just copies the dict entry in an array
        newElem = D[elem]
        newElem[keylabel] = elem
        arr.append(newElem)

    return arr

def trim_sorted_text(recs,n):
    """sorted_text = top n tf-idf words"""
    for k in recs:
        n_traits = top_n_words(recs[k],n)
        recs[k]['traits'] = n_traits

    return recs


def top_n_words(rec,n):
    # given a record returns the top n tf-idf words
    traits = []
    try: 
        bow = rec['sorted_text']

    except KeyError:
        try:
            bow = flatten_text(rec['text'],'word')
            sorted_text = sorted(bow, key=lambda w: w[u'tf-idf'], reverse = True)
        # may not have tf-idf
        except KeyError:
            return None


    for word in bow[0:n]:
        traits.append(word['word'])

    return traits

def recs_by_pno(recs):
    rec_dict = {}
    for rec in recs:
        rec_dict[rec['pno']] = rec
    recs = rec_dict

    return recs


def parents_by_child(links):
    p_by_c = {}

    for parent,child in links:
        try:
            p_by_c[child].append(parent)
        # not yet in dict
        except KeyError:
            p_by_c[child] = [parent]

    return p_by_c