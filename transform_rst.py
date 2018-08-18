import rst_tree
import relations
import extract_answer_phrases
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
        qud_node.add_children(transform(rst_node))

        return qud_node
        
        
        
    
    if len(rst_node.satellites_left) > 0:
        sats = rst_node.satellites_left
        sat, rel = sats[len(sats)-1)]
        rst_node_copy = rst_node
        rst_node_copy.satellites_left = sats[:len(sats)-1]

        qud = find_qud(rel, sat, right = False)

        qud_node = qud_tree.Qud_Node(qud=qud)

        nuc_children = transform(rst_node_copy)
        sat_children = transform(sat)

        for child in nuc_children:
            qud_node.add_child(nuc_child)
        for child in sat_children:
            qud_node.add_child(sat_child)

        return [qud_node]
    
    if len(rst_node.satellites_right) > 0:
        sats = rst_node.satellites_right
        sat, rel = sats[len(sats)-1)]
        rst_node_copy = rst_node
        rst_node_copy.satellites_right = sats[:len(sats)-1]

        qud = find_qud(rel, rst_node_copy, right = True)

        qud_node = qud_tree.Qud_Node(qud=qud)

        nuc_children = transform(rst_node_copy)
        sat_children = transform(sat)

        for child in nuc_children:
            qud_node.add_child(nuc_child)
        for child in sat_children:
            qud_node.add_child(sat_child)

        return [qud_node]

    children, multi_nuc_type = rst_node.children

    if multi_nuc_type is None and children != []:
        #span node
        return transform(children[0])

    if multi_nuc_type is None and children == []:
        #leaf
        edu = rst_node.edu

        qud_node = qud_tree.Qud_Node(edu=edu)

        return [qud_node]

    
    if multi_nuc_type != "restatement_mn":
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
    
            
