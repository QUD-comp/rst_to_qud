import copy

import rst_tree
import relations
import extract_question_content as eqc
import qud_tree

def transform_rst(rst_tree):
    """wrapper function for transform()"""
    return transform(rst_tree)[0]

def transform(rst_node, root=True):
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
    qud_nodes : [Qud_Node]
        transformed tree
    """

    if root:
        qud_node = qud_tree.Qud_Node(qud="What is the way things are?")
        for child in transform(rst_node, root=False):
            qud_node.add_child(child)

        return [qud_node]




    if len(rst_node.satellites_left) > 0:
        sats = rst_node.satellites_left
        sat, rel = sats[(len(sats)-1)]
        rst_node_copy = copy.copy(rst_node)
        rst_node_copy.satellites_left = sats[:len(sats)-1]

        qud = find_qud(rel, sat, right = False)
        qud_node = qud_tree.Qud_Node(qud=qud)


        sat_children = transform(sat, root=False)

        nuc_children = transform(rst_node_copy, root=False)
        for child in nuc_children:
            qud_node.add_child(child)

        return sat_children + [qud_node]

    if len(rst_node.satellites_right) > 0:
        sats = rst_node.satellites_right

        sat, rel = sats[(len(sats)-1)]

        rst_node_copy = copy.copy(rst_node)
        rst_node_copy.satellites_right = sats[:len(sats)-1]

        qud = find_qud(rel, rst_node_copy, right = True)

        qud_node = qud_tree.Qud_Node(qud=qud)

        nuc_children = transform(rst_node_copy, root=False)

        sat_children = transform(sat, root=False)

        for child in sat_children:
            qud_node.add_child(child)

        return nuc_children + [qud_node]

    children, multi_nuc_type = rst_node.children

    if multi_nuc_type is None and children != []:
        #span node
        return transform(children[0], root=False)

    if multi_nuc_type is None and children == []:
        #leaf
        edu = rst_node.edu

        qud_node = qud_tree.Qud_Node(edu=edu)

        return [qud_node]

    
    if multi_nuc_type != "restatement_mn":
        #it's a multi-nuc, not a span
        transformed = []
        for child in children:
            for element in transform(child, root=False):
                transformed.append(element)

        return transformed
    else:
        transformed = []

        transformed.append(transform(children[0], root=False))

        for i, child in enumerate(children[1:]):
            qud = find_qud("restatement", children[i], right=True)

            qud_node = qud_tree.Qud_Node(qud=qud)
            qud_node.children += transform(child, root=False)

            transformed.append(qud_node)

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

    if right:
        use_gerund = relation in use_gerund_relations_right
    else:
        use_gerund = relation in use_gerund_relations_left

    question_content = eqc.find_question_content(subtree, gerund=use_gerund)

    if right:
        part1 = question_frame_right[relation][0]
        part2 = question_frame_right[relation][1]
    else:
        part1 = question_frame_left[relation][0]
        part2 = question_frame_left[relation][1]



    qud = part1 + question_content + part2

    return qud


use_gerund_relations_right = [
    "antithesis",
    "background",
    "circumstance",
    "elaboration",
    "e-elaboration",
    "evaluation-s",
    "interpretation",
    "justify",
    "means",
    "result",
    "purpose",
    "solutionhood",
    "unconditional",
    "unless",
    "unstated-relation",
    "evaluation-n"
    ]
    



question_frame_right = {
    "antithesis" : ("Does anything speak against ", "?"),
    "background" : ("What is the background to ", "?"),
    "circumstance" : ("What are the circumstances around ", "?"),
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
    "restatement" : ("What is another way to say ", "?"),
    "solutionhood" : ("What problem does ", " solve?"),
    "summary" : ("How can ", " be summed up?"),
    "unconditional" : ("What could affect ", ", but doesn't?"),
    "unless" : ("What would prevent ", " from happening?"),
    "unstated-relation" : ("What about ", "?"),
    "evaluation-n" : ("How do you evaluate ", "?"),
    "reason" : ("What could make one think that ", "?")
    }


use_gerund_relations_left = [
    "antithesis",
    "background",
    "condition",
    "enablement",
    "evaluation-s",
    "evidence",
    "justify",
    "motivation",
    "cause",
    "purpose",
    "solutionhood",
    "unconditional",
    "unless",
    "unstated-relation",
    "evaluation-n",
    "reason"
    ]


question_frame_left = {
    "antithesis" : ("What does speak against ", "?"),
    "background" : ("What is ", " the background to?"),
    "circumstance" : ("What happens under the circumstance that ", "?"),
    "concession" : ("To what is ", " a concession?"),
    "condition" : ("For what is ", " a condition?"),
    #"elaboration" : ("What about ", "?"), -> can't happen with satellite on the left-hand side
    #"e-elaboration" : ("What about ", "?"), -> can't happen with satellite on the left-hand side
    "enablement" : ("What can we do because of ", "?"),
    "evaluation-s" : ("What is ", " an evaluation of?"),
    "evidence" : ("What does ", " proof?"),
    "interpretation" : ("What is ", " an interpretation for?"),
    "justify" : ("Is there a justification for ", "?"),
    "means" : ("What can one do with ", "?"),
    "motivation" : ("What should one do because of ", "?"),
    "cause" : ("What happens because of ", "?"),
    "result" : ("Why does ", " happen?"),
    "otherwise" : ("What can't happen if ", "?"),
    "preparation" : ("What is ", " a preparation for?"),
    "purpose" : ("How can ", " be achieved?"),
    "restatement" : ("What is another way to say " "?"),
    "solutionhood" : ("How can ", " be solved?"),
    "summary" : ("What is ", " a summary for?"),
    "unconditional" : ("What does ", " not have an effect on?"),
    "unless" : ("What would be prevented from happening by ", "?"),
    "unstated-relation" : ("What about ", "?"),
    "evaluation-n" : ("Is ", " good?"),
    "reason" : ("What could ", " make one think?")
    }
    





    
