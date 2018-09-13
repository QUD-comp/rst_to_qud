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
    """
    
    def __init__(self, edu=None, edu_num=None, multi_nuc_relation=None):
        self.edu = edu
        self.edu_num = edu_num

        self.children = ([], multi_nuc_relation)
        self.satellites_left = []
        self.satellites_right = []

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

    def get_text(self):
        """
        Get combined EDUs dominated by by this node.
        """
        text = ""
        
        for sat in self.satellites_left:
            text += " " + sat[0].get_text()

        if not self.edu is None:
            text += " " + self.edu

        for child in self.children[0]:
            text += " " + child.get_text()

        for sat in self.satellites_right:
            text += " " + sat[0].get_text()

        return text
        

                    
        
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





        

        
