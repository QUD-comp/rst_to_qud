import qud_tree
import copy
from nltk import word_tokenize

def kappa(tree1, tree2):
    """
    Calculate kappa value, comparing the structural similarity of two QUD trees.

    For each tree, build a matrix whose entries give for each pair of EDUs (edu1, edu2), 
    if there is a span in the tree from edu1 to edu2. 
    Calculate a kappa value based on these two matrices.

    Parameters
    ----------
    tree1 : Qud_Node
        First of the two trees to be compared.
    tree2 : Qud_Node
        Second of the two trees to be compared.

    Return
    ------
    kappa : float
        kappa value measuring structural similarity of the trees
    """

    edus1 = get_edus(tree1)
    edus2 = get_edus(tree2)

    listify_fst = lambda tup : ([tup[0]],tup[1])
    
    if len(edus1) > len(edus2):
        edus1 = list(enumerate(edus1))
        edus2 = enumerate_edus(edus2, edus1)
        edus1 = list(map(listify_fst, edus1))
    else:
        edus2 = list(enumerate(edus2))
        edus1 = enumerate_edus(edus1, edus2)
        edus2 = list(map(listify_fst, edus2))

    matrix1 = build_matrix(tree1, edus1)
    matrix2 = build_matrix(tree2, edus2)

    num_cells = len(matrix1.keys())

    num_agreed = 0
    for key in matrix1.keys():
        if matrix1[key] == matrix2[key]:
            num_agreed += 1

    observed = num_agreed / num_cells

    num_true = lambda matrix : len([entry for entry in matrix.items() if entry[1]])
    num_false = lambda matrix : len([entry for entry in matrix.items() if not entry[1]])

    nt1 = num_true(matrix1)
    nt2 = num_true(matrix2)
    nf1 = num_false(matrix1)
    nf2 = num_false(matrix2)

    print(nt1, nt2, nf1, nf2)
    
    expected = 1/num_cells * (nt1 * nt2 + nf1 * nf2)

    kappa = (observed - expected) / (1 - expected)

    return kappa

    


def build_matrix(tree, edus):
    """
    Build a matrix whose entries give for each pair of EDUs (edu1, edu2), 
    if there is a span in the tree from edu1 to edu2.

    Parameter
    ---------
    tree : Qud_Node
        Tree for which to build the matrix
    edus : [([int], str)]
        EDUs annotated with numbers.

    Return
    ------
    matrix : dict
        dict with pairs of ints as keys booleans as value
        if matrix[(x,y)] == True, there is a qud spanning from edu x to edu y in the tree
    """

    matrix = dict()

    #build matrix
    num_edus = edus[-1][0][-1] + 1
    for i in range(num_edus):
        for j in range(num_edus):
            if i <= j:
                matrix[(i,j)] = False
    
    #fill matrix
    edu_pairs = get_spans(tree, edus)

    for pair in edu_pairs:
        matrix[pair] = True

    return matrix


def get_spans(tree, edus):
    spans = []

    if tree.children == []:
        num_list = edus[0][0]
        spans += get_spans_from_list(num_list)
        return spans

    left = None
    if not tree.edu is None:
        #If there is an explicit QUD, it's the leftmost edu in the span.
        left = edus[0][0][0]
        edus = edus[1:]

    for child in tree.children:
        spans += get_spans(child, edus)
        rightmost_thus_far = spans[-1][1]
        edu_num = edus[0][0][0]
        while edu_num <= rightmost_thus_far:
            edus = edus[1:]
            if edus == []:
                break
            edu_num = edus[0][0][0]

    if left is None:
        left = spans[0][0]
    right = spans[-1][1]

    spans.append((left,right))

    return spans
            
                    

def get_spans_from_list(num_list):
    spans = []
    for num in num_list:
        for num2 in num_list:
            if num <= num2:
                spans.append((num, num2))
    return spans
            
    
    



def enumerate_edus(edus1, edus2):
    """
    Annotate edus1 with the numbers of the corresponding edus in edus2.

    This is necessary because in some cases, edus were combined in the qud annotations of the Potsdam microtexts corpus.

    Parameter
    ---------
    edus1 : [str]
        EDUs to annotate with the numbers.
    edus2 : [(int, str)]
        EDUs already enumerated.

    Return
    ------
    ret_edus : [([int], str)]
        edus1 annotated with the edu numbers
    """

    ret_edus = []

    for combined_edu in edus1:
        combined_list = word_tokenize(combined_edu.strip(",. ").lower())
        num, edu = edus2[0]
        edus2 = edus2[1:]
        single_list = word_tokenize(edu.strip(",. ").lower())
        num_list = [num]
        
        while len(combined_list) > len(single_list):
            num, edu = edus2[0]
            edus2 = edus2[1:]
            single_list += word_tokenize(edu)
            num_list.append(num)

        ret_edus.append((num_list, combined_edu))

    return ret_edus
            
        
        

    


def get_edus(tree):
    """
    Get EDUs of a tree.

    Parameter
    ---------
    tree : Qud_Node
        Tree from which to get the EDUs.

    Return
    ------
    edus : [str]
        EDUs of the tree.
    """

    edus = []
    
    if not tree.edu is None:
        edus.append(tree.edu)

    for child in tree.children:
        edus += get_edus(child)

    return edus
