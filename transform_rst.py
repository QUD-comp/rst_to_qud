import rst_tree
import relations
import extract_answer_phrases as eap
import qud_tree

def transform(rst_node, root=False):
    """
    Transform an rst tree recursively into a qud tree.

    Parameter
    ---------
    rst_node : Rst_Node
        tree to be transformed
    root : Boolean
        indicates if this node is the root of the overall tree

    Returns
    -------
    qud_node : Qud_Node
        transformed tree
    """

    if root:
        qud_node = qud_tree.Qud_Node(qud="What is the way things are?")
        print(rst_node.children[0][0].satellites_right)
        for child in transform(rst_node):
            qud_node.add_child(child)
        #qud_node.add_child(transform(rst_node)[0])

        return qud_node
        
        
    
    
    if len(rst_node.satellites_left) > 0:
        print("left")
        sats = rst_node.satellites_left
        sat, rel = sats[(len(sats)-1)]
        rst_node_copy = rst_node
        rst_node_copy.satellites_left = sats[:len(sats)-1]
        rst_node.print_tree()
        qud = find_qud(rel, sat, right = False)
        qud_node = qud_tree.Qud_Node(qud=qud)

        nuc_children = transform(rst_node_copy)
        sat_children = transform(sat)

        for child in nuc_children:
            qud_node.add_child(child)
        for child in sat_children:
            qud_node.add_child(child)

        return [qud_node]
    
    if len(rst_node.satellites_right) > 0:
        print("right")
        sats = rst_node.satellites_right
        sat, rel = sats[(len(sats)-1)]
        rst_node_copy = rst_node
        rst_node_copy.satellites_right = sats[:len(sats)-1]

        qud = find_qud(rel, rst_node_copy, right = True)

        qud_node = qud_tree.Qud_Node(qud=qud)

        nuc_children = transform(rst_node_copy)

        sat_children_lists = transform(sat)
        sat_children = []
        for sublist in sat_children_lists:
            for child in sublist:
                sat_children.append(child)
        
        print(sat_children)
        for child in nuc_children:
            qud_node.add_child(child)
        for child in sat_children:
            print(child)
            print(type(child))
            qud_node.add_child(child)

        return [qud_node]

    children, multi_nuc_type = rst_node.children

    if multi_nuc_type is None and children != []:
        #span node
        print("span")
        return transform(children[0])

    if multi_nuc_type is None and children == []:
        #leaf
        print("leaf")
        edu = rst_node.edu

        qud_node = qud_tree.Qud_Node(edu=edu)

        return [qud_node]

    
    if multi_nuc_type != "restatement_mn":
        print("multinuc")
        #it's a multi-nuc, not a span
        transformed = []
        for child in children:
            transformed.append(transform(child))

        return transformed
    else:
        transformed = []

        transformed.append(children[0])

        for i, child in enumerate(children[1:]):
            qud = find_qud("restatement", children[i], right=True)

            qud_node = qud_tree.Qud_Node(qud=qud)
            qud_node.children += transform(child)

            transformed.append(child)

        return transformed
    
            
def find_qud(relation, subtree, right):
    """
    Find QUD of a certain node from the relation and the subtree to the left of the node.

    Parameters
    ----------
    relation : String
        RST relation between node to be transformed and the satellite.
    subtree : Rst_Node
        Left-hand subtree in the relation, either nucleus or satellite.
    right : Boolean
        Is true if satellite is to the right of the nucleus in the relation.
    """

    text = subtree.get_text()

    question_content = eap.extract_answer_phrases(text)

    if right:
        part1 = question_frame_right[relation][0]
        part2 = question_frame_right[relation][1]
    else:
        part1 = question_frame_left[relation][0]
        part2 = question_frame_left[relation][1]


    qud = part1 + text + part2

    return qud





question_frame_right = {
    "antithesis" : ("Does anything speak against ", "?"),
    "background" : ("What is the background to ", "?"),
    #"circumstance" : (
    "concession" : ("Is it always true that ", "?"),
    "condition" : ("What is necessary for ", "?"),
    "elaboration" : ("What about ", "?"),
    "e-elaboration" : ("What about ", "?"),
    "enablement" : ("How can we do ", "?"),
    "evaluation-s" : ("Is ", " good?"),
    "evidence" : ("Is there proof that ", "?"),
    "interpretation" : ("How can ", "be interpreted?"),
    "justify" : ("Is there a justification for ", "?"),
    "means" : ("How can ", " be done?"),
    "motivation" : ("Why should one ", "?"),
    "cause" : ("Why does ", " happen?"),
    "result" : ("What happens because of ", "?"),
    "otherwise" : ("What can't happen if ", "?"),
    #"preparation" -> can't happen with satellite on the right-hand side
    "purpose" : ("What does ", " achieve?"),
    #"restatement"
    "solutionhood" : ("What problem does ", " solve?"),
    "summary" : ("How can ", " be summed up?"),
    "unconditional" : ("What could affect ", ", but doesn't?"),
    "unless" : ("What would prevent ", " from happening?"),
    "unstated-relation" : ("What about ", "?"),
    #"evaluation-n" : ("
    "reason" : ("What could make one think that ", "?")
    }


question_frame_left = {
    "antithesis" : ("What does speak against ", "?"),
    "background" : ("What is ", " the background to?"),
    #"circumstance" : (
    "concession" : ("To what is ", " a concession?"),
    "condition" : ("For what is ", " a condition?"),
    #"elaboration" : ("What about ", "?"),
    #"e-elaboration" : ("What about ", "?"),
    #"enablement" : ("How can we do ", "?"),
    #"evaluation-s" : ("Is ", " good?"),
    "evidence" : ("What does ", " proof?"),
    "interpretation" : ("What is ", " an interpretation for?"),
    "justify" : ("Is there a justification for ", "?"),
    "means" : ("What can one do with ", "?"),
    "motivation" : ("What should one do because of ", "?"),
    "cause" : ("What happens ", " because of?"),
    "result" : ("Why does ", " happen?"),
    #"otherwise" : ("What can't happen if ", "?"),
    "preparation" : ("What is ", " a preparation for?"),
    "purpose" : ("How can ", " be achieved?"),
    #"restatement"
    "solutionhood" : ("How can ", " be solved?"),
    "summary" : ("What is ", " a summary for?"),
    "unconditional" : ("What does ", " not have an effect on?"),
    "unless" : ("What would be prevented from happening by ", "?"),
    "unstated-relation" : ("What about ", "?"),
    "evaluation-n" : ("Is ", " good?"),
    "reason" : ("What could ", " make one think?")
    }
    

def print_qud_tree(tree, indent=0):
    """
    Print qud tree

    Parameters
    ----------
    tree : Qud_Node
        Tree to be printed.
    indent : int
        level of node in tree
    """
    
    if tree.children == []:
        out_str = indent * ">" + tree.edu
    else:
        out_str = indent * ">" + tree.qud

    print(out_str)

    for child in tree.children:
        print_qud_tree(child, indent+1)




    
