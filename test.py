import re
import os
from nltk import word_tokenize
import collections as col

import qud_tree
import read_rst as rr
import transform_rst as tr
import read_qud as rq






def evaluate_transform(rst_path, gold_qud_path, transformed_path, result_filename, relations_filename):
    """
    Evaluate the transform function by transforming RST trees
    and comparing them to human-annotated QUD trees.

    Parameters
    ----------
    rst_path : str
        Path of the folder of the RST trees.
    gold_qud_path : str
        Path of the folder containing the human-annotated QUD trees.
    transformed_path : str
        Path to write the transformed trees to.
    result_filename : str
        Path of the file to write the evaluation results to.
    relations_filename : str
        Path to the file to write the results for the relations to.
    """

    def get_code(qud_name):
        regex = "([a-z][0-9]{3})"
        match = re.search(regex, qud_name)
        if match:
            return match.group(1)
        
    def get_rst_path(code):
        filename = "micro_" + code + ".rs3"

        no_sameunit_path = os.path.join(rst_path, "../rst-without-sameunit")
        no_sameunit_path = os.path.join(no_sameunit_path, filename)
        if os.path.isfile(no_sameunit_path):
            #some RST trees in the microtexts corpus include the sameunit tag
            #read_rst can't deal with that, so we need to use the
            #corresponding files not using the sameunit tag
            return no_sameunit_path
        
        path = os.path.join(rst_path, filename)
        return path


    gold_filenames = os.listdir(gold_qud_path)

    codes = list(set(map(get_code, gold_filenames)))

    rst_file_paths = list(map(get_rst_path, codes))

    relations_total = col.defaultdict(float)
    relations_spans = col.defaultdict(float)

    for rst_path, code in zip(rst_file_paths, codes):
        try:
            rst_tree = rr.read_rst_from_microtexts(rst_path)
        except Exception as ex:
            with open("error_log", "a") as error_file:
                error_file.write(code)
                error_file.write("\n")
                error_file.write(str(ex))
                error_file.write("\n")
            continue
            
        qud_transformed = tr.transform_rst(rst_tree)

        transformed_filename = code + ".txt"
        transformed_filename = os.path.join(transformed_path, transformed_filename)

        qud_transformed.write_tree(transformed_filename)


        curr_gold_filenames = []
        for name in gold_filenames:
            match = re.search(code, name)
            if match:
                curr_gold_filenames.append(name)

        for name in curr_gold_filenames:
            try:
                gold_path = os.path.join(gold_qud_path, name)
                gold_qud = rq.read_qud_from_microtexts(gold_path)

                kappa, curr_rel_total, curr_rel_spans = calculate_kappa(qud_transformed, gold_qud)


                for key in curr_rel_total.keys():
                    relations_total[key] += curr_rel_total[key]
                    relations_spans[key] += curr_rel_spans[key]


                transformed_depth = qud_transformed.get_depth()
                gold_depth = gold_qud.get_depth()
                depth_diff = transformed_depth - gold_depth

                with open(result_filename, "a") as result_file:
                    line = code + " | " + name + " | " + str(kappa) + " | " + str(transformed_depth) + " | " + str(gold_depth) + " | " + str(depth_diff) + "\n"
                    result_file.write(line)
            except Exception as ex:
                if str(ex) == "float division by zero":
                    raise ex
                #write errors to file in order to be able to deal with them by hand
                with open("error_log", "a") as error_file:
                    error_file.write(name)
                    error_file.write("\n")
                    error_file.write(str(ex))
                    error_file.write("\n")

        with open(relations_filename, "w") as rel_file:
            for rel in relations_total.keys():
                #if relations_total[key] == 0:
                #    percentage = 0
                #else:
                percentage = relations_spans[rel] / relations_total[rel]
                line = str(rel) + " | " + str(relations_total[rel]) + " | " + str(relations_spans[rel]) + " | " + str(percentage) + "\n"
                rel_file.write(line)









def calculate_kappa(tree1, tree2):
    """
    Calculate kappa value, comparing the structural similarity of two QUD trees.
    For each relation, used to build tree1, calculate how often it was used to form a question
    such that a question with the same span exists in tree2.

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
    relations_all : dict
        dictionary with relations as keys and floats as values
        the float is the proportion of how often this relation was translated into 
        a question in tree1 such that a question with the same span exists in tree2 
    """

    edus1 = get_edus(tree1)
    edus2 = get_edus(tree2)

    boundary_segments = find_boundary_segments(edus1, edus2)

    edus1 = enumerate_edus(edus1, boundary_segments)
    edus2 = enumerate_edus(edus2, boundary_segments)

    
    matrix1 = build_matrix(tree1, edus1)
    matrix2 = build_matrix(tree2, edus2)
    
    relations_all = col.defaultdict(float)
    relations_spans = col.defaultdict(float)
    
    num_cells = len(matrix1.keys())

    num_agreed = 0
    for key in matrix1.keys():
        
        if matrix1[key][0]:
            rel = matrix1[key][1]
            relations_all[rel] += 1
            if matrix2[key][0]:
                relations_spans[rel] += 1

        if matrix1[key][0] == matrix2[key][0]:
            num_agreed += 1

            

    observed = num_agreed / num_cells

    num_true = lambda matrix : len([entry for entry in matrix.items() if entry[1][0]])
    num_false = lambda matrix : len([entry for entry in matrix.items() if not entry[1][0]])

    nt1 = num_true(matrix1)
    nt2 = num_true(matrix2)
    nf1 = num_false(matrix1)
    nf2 = num_false(matrix2)


    expected = 1/(num_cells * num_cells) * (nt1 * nt2 + nf1 * nf2)

    kappa = (observed - expected) / (1 - expected)

    return kappa, relations_all, relations_spans


def find_boundary_segments(edus1, edus2):
    """
    Find EDU boundaries according to the trees.
    Presupposes that edus1 and edus2 contain the same text.

    Parameters
    ----------
    edus1 : [str]
        EDUs from first tree
    edus2 : [str]
        EDUs from second tree

    Return
    ------
    boundary_segments : [(int, str)]
        enumerated list of smaller segments given by boundaries from edus1 and edus2
    """
    
    
    boundary_segments = []
    
    while edus1 != [] and edus2 != []:
        edu1 = edus1[0].strip()
        edus1 = edus1[1:]
        edu2 = edus2[0].strip()
        edus2 = edus2[1:]

        if edu1 == edu2:
            boundary_segments.append(edu1)
        elif edu1.startswith(edu2):
            boundary_segments.append(edu2)
            edu1 = edu1[len(edu2):]
            edus1 = [edu1] + edus1
        else:
            boundary_segments.append(edu1)
            edu2 = edu2[len(edu1):]
            edus2 = [edu2] + edus2
            

    #simply append remaining EDUs
    boundary_segments += edus1
    boundary_segments += edus2

    return list(enumerate(boundary_segments))
            




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
        if matrix[(x,y)] == (True, _), there is a qud spanning from edu x to edu y in the tree
        the second element in the pair is the relation presumably used to 
        build the QUD spanning x and y
    """

    matrix = dict()

    #build matrix
    num_edus = edus[-1][0][-1] + 1
    for i in range(num_edus):
        for j in range(num_edus):
            if i <= j:
                matrix[(i,j)] = (False, None)
    
    #fill matrix

    edu_pairs, _, _ = get_spans(tree, edus)

    for edu1, edu2, rel in edu_pairs:
        matrix[(edu1, edu2)] = (True, rel)

    return matrix


def get_spans(tree, edus, right_num=-1):
    """
    Get tuples of EDUs spanned by the QUDs in the tree.

    Parameters
    ----------
    tree : Qud_Node
        tree of which to get spans
    edus : [([int], str)]
        list of EDUs annotated with their numbers
    right_num : int
        number of last EDU found in left-to-right depth-first-search of tree

    Return
    ------
    spans : [(int, int, relation)]
        list of spans with relations that were used to form the QUD during transformation
        relation is None if it can't be determined 
        (which should usually be the case when the tree wasn't transformed from an RST tree)
    edus : [([int], str)]
        list of EDUs not yet found in the left-to-right depth-first-search of tree
    right_num : int
        number of last EDU found in left-to-right depth-first-search of tree
    """

    spans = []
    leftmost_edu = edus[0]

    if tree.children == []:
        right_num = edus[0][0][-1]
        edus = edus[1:]
        return spans, edus, right_num

    left = None
    if not tree.edu is None:
        #If there is an explicit QUD, it's the leftmost edu in the span.
        left = edus[0][0][0]
        right_num = edus[0][0][-1]
        edus = edus[1:]

    for child in tree.children:
        new_spans, edus, right_num = get_spans(child, edus, right_num)
        spans += new_spans

    if left is None:
        left = leftmost_edu[0][0]
    right = right_num

    relation = find_relation(tree.qud)
    
    spans.append((left,right, relation))

    return spans, edus, right_num


def find_relation(qud):
    """
    Find relation from which a QUD was produced.

    Find the relation by matching the question_frames from transform_rst to the QUD.
    This is a crude method, since sometimes different relations have the same question frames.
    For example, "elaboration", "e-elaboration", and "unstated-relation" will be 
    matched to "elaboration"; 
    also "evaluation-n" and "evaluation-s" cannot be told apart from each other,
    neither can "result" and "cause".

    Parameter
    ---------
    qud : str
        QUD in question
    
    Return
    ------
    rel : str
        relation that was identified as being the one used to make the QUD
    """
    for rel, frame in tr.question_frame_right.items():
        reg1 = re.escape(frame[0])
        match1 = re.search(reg1, qud)

        reg2 = re.escape(frame[1])
        match2 = re.search(reg2, qud)

        if match1 and match2:
            return rel

    for rel, frame in tr.question_frame_left.items():
        reg1 = re.escape(frame[0])
        match1 = re.search(reg1, qud)

        reg2 = re.escape(frame[1])
        match2 = re.search(reg2, qud)

        if match1 and match2:
            return rel

    return None
        

            
    
    



def enumerate_edus(edus1, boundary_segments):
    """
    Annotate edus1 with the numbers of the corresponding segments in boundary_segments.

    This is necessary because in some cases, edus were combined in the qud annotations of the Potsdam microtexts corpus.

    Parameter
    ---------
    edus1 : [str]
        EDUs to annotate with the numbers.
    boundary_segments : [(int, str)]
        enumerated segments

    Return
    ------
    ret_edus : [([int], str)]
        edus1 annotated with the edu numbers
    """

    ret_edus = []

    for combined_edu in edus1:
        combined_list = word_tokenize(combined_edu.strip(",. ").lower())
        num, edu = boundary_segments[0]
        boundary_segments = boundary_segments[1:]
        single_list = word_tokenize(edu.strip(",. ").lower())
        num_list = [num]
        
        while len(combined_list) > len(single_list):
            num, edu = boundary_segments[0]
            boundary_segments = boundary_segments[1:]
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



