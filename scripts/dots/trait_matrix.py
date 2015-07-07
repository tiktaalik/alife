def sparse_matrix(nodes,recs,key="traits"):
    """Outputs a sparse matrix where rows are patents and columns are traits.
    Input is a dictionary of pnos where the values are a diction where one of 
    the keys is the traits you want to extract"""
    # construct sparse matrix
    matrix = []
    for pno in nodes:
        data = recs[pno]
        traits = data[key]
        if traits == None:
            traits = []
        matrix.append(traits)

    return matrix


def dense_matrix(matrix):
    tokens = flatten_s_matrix(matrix)

    types = list(set(tokens))

    # dense matrix with all 0s
    d_matrix = [[0]*len(types) for i in range(len(matrix))]
    
    for i,arr in enumerate(matrix):
        if arr:
            for trait in arr:
                # get the trait id
                t_id = types.index(trait)
                d_matrix[i][t_id] += 1

    return d_matrix


def flatten_s_matrix(s_matrix):
    tokens = []
    for i,patent_traits in enumerate(s_matrix):
        tokens += patent_traits

    return tokens


def traits_by_pno(nodes,s_matrix):
    traits_dict = {}
    for node in nodes:
        traits_dict[node] = s_matrix.pop(0)

    return traits_dict


def trait_freqs(s_matrix):
    tokens = flatten_s_matrix(s_matrix)

    types = list(set(tokens))
    freqs = {trait:0 for trait in types}

    for token in tokens:
        freqs[token] += 1

    return freqs

