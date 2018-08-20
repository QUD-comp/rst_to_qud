from treelib import Node, Tree

class Rst_Node:
    """Class representing an RST tree.

    Attributes
    ----------
    edu : String
        elemental discourse unit corresponding to this node, provided it is a leave node
    edu_num : int
        position of edu in text (1, 2, 3, ...)
    children : ([Rst_Node], String)
        Tuple of list of child nodes and relation type for multinuclear relation.
        If self is a span node, wich is above a mononuclear relation, the list just 
        contains the nucleus of that relation. The relation type is None in that case.
        If self is the nucleus of a mononuclear relation, the list is empty 
        and the relation type is None.
    satellites_left: [(Rst_Node, String)]
        List of tuples representing the satellites to the left of the nucleus 
        in a mononuclear relation.
        The first element of the tuple is a satellite, the second one is the relation type.
    satellites_right: [(Rst_Node, String)]
        List of tuples representing the satellites to the right of the nucleus 
        in a mononuclear relation.
        The first element of the tuple is a satellite, the second one is the relation type.
    __address : [int]
        tree-structured address in tree
    """
    
    def __init__(self, edu=None, edu_num=None, multi_nuc_relation=None):
        self.edu = edu
        self.edu_num = edu_num

        self.children = ([], multi_nuc_relation)
        self.satellites_left = []
        self.satellites_right = []
        self.address = []

    def add_child(self, child):
        """Add an Rst_Node to self.children."""
        if not isinstance(child, Rst_Node):
            raise TypeError("child must be an Rst_Node")
        
        child_nodes, relname = self.children
        child_nodes.append(child)
        self.children = (child_nodes, relname)

    def add_satellite_left(self, satellite, relname):
        """Add an Rst_Node as satellite with relation relname."""
        if not isinstance(satellite,Rst_Node):
            raise TypeError("satellite must be an Rst_Node")

        self.satellites_left.append((satellite, relname))

    def add_satellite_right(self, satellite, relname):
        """Add an Rst_Node as satellite with relation relname."""
        if not isinstance(satellite,Rst_Node):
            raise TypeError("satellite must be an Rst_Node")

        self.satellites_right.append((satellite, relname))


    #def get_leaves(self):
    #    """Return nodes of tree that have no children (but may have satellites)."""
    #    leaves = []
    #    for satellite in self.satellites_left:
    #        leaves += satellite[0].get_leaves()
    #    for satellite in self.satellites_right:
    #        leaves += satellite[0].get_leaves()

    #    if self.children[0] == []:
    #        leaves.append(self)
    #    else:
    #        for child in self.children[0]:
    #            leaves += child.get_leaves()

    #    return leaves

    #def equals(self, tree):
    #    if self.edu != tree.edu:
    #        return False

    #    if len(self.satellites_left) != len(tree.satellites_left):
    #        return False
    #        
    #    for s1, s2 in zip(self.satellites_left, tree.satellites_left):
    #        if not s1.equals(s2):
    #            return False

    #    if len(self.satellites_right) != len(tree.satellites_right):
    #        return False
    #        
    #    for s1, s2 in zip(self.satellites_right, tree.satellites_right):
    #        if not s1.equals(s2):
    #            return False

    #    if len(self.children) != len(tree.children):
    #        return False
    #        
    #    for s1, s2 in zip(self.children, tree.children):
    #        if not s1.equals(s2):
    #            return False

    #    return True


    #        
    #
    #def find_connections(self, tree, leaves):
    #    connections = []

    #    if tree.edu_num is None:
    #        tree.edu_num = find_edu_num(tree)
    #    
    #    for leaf in leaves:
    #        #if leaf, _ in tree.satellites_left:
    #        for node, rel in tree.satellites_left:
    #            if leaf.equals(node):
    #                connections.append((tree.edu_num, leaf.edu_num, rel))
    #        for node, rel in tree.satellites_right:
    #            if leaf.equals(node):
    #                connections.append((tree.edu_num, leaf.edu_num, rel))

    #        for child in tree.children[0]:
    #            if leaf.equals(child):
    #                connections.append((tree.edu_num, leaf.edu_num, tree.children[1]))

    #    return connections
                    
        
    def print_tree(self):
        """
        Print this tree.

        Print this tree as a simplified structure without 
        differentiating between satellites and children in multinuclear relations.
        """
        simplified = Tree()

        queue = [(self, None, None)]

        node_id = 0

        for subtree, rel, parent in queue:
            tag = str(rel)
            if not subtree.edu is None:
               tag += " " + str(subtree.edu_num+1)

            simplified.create_node(tag, node_id, parent)

            for sat, rel in subtree.satellites_left:
                queue.append((sat, rel, node_id))

            for child in subtree.children[0]:
                rel = subtree.children[1]
                queue.append((child, rel, node_id))

            for sat, rel in subtree.satellites_right:
                queue.append((sat, rel, node_id))

            node_id += 1

        simplified.show()





        
        #tree_copy = self
        #leaves = tree_copy.get_leaves()
        #edu_nums = list(range(len(leaves)))
        ##print(leaves)
        #while leaves != []:
        #    #print_row(leaves)
        #    edu_num = lambda n : n.edu_num
        #    string1 = ""
        #    string2 = ""
        #    for leaf in sorted(leaves, key=edu_num):
        #        string1 += str(leaf.edu_num) + "     "
        #        string2 += "_     "
        #    print(string1)
        #    print(string2)
        #    conn = find_connections(tree_copy, leaves)
        #    fst = lambda x : x[0]
        #    
        #    for edu_num in edu_nums:
        #        if 
        #    #sat_conn = find_satellite_connections(tree_copy, leaves)
        #    #mult_conn = find_mult_nuc_connections(tree_copy, leaves)
        #    
        #    
        #    #print connections

        
