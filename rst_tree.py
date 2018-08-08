class Rst_Node:
    """Class representing an RST tree.

    Attributes
    ----------
    edu : String
        elemental discourse unit corresponding to this node, provided it is a leave node
    children : ([Rst_Node], String)
        Tuple of list of child nodes and relation type for multinuclear relation.
        If self is a span node, wich is above a mononuclear relation, the list just 
        contains the nucleus of that relation. The relation type is None in that case.
        If self is the nucleus of a mononuclear relation, the list is empty 
        and the relation type is None.
    satellites: [(Rst_Node, String)]
        List of tuples representing the satellites in a mononuclear relation.
        The first element of the tuple is a satellite, the second one is the relation type.
    """
    
    def __init__(self, edu=None, multi_nuc_relation=None):
        self.edu = edu

        self.children = ([], multi_nuc_relation)
        self.satellites = []

    def add_child(child):
        """Add an Rst_Node to self.children."""
        if not isinstance(child, Rst_Node):
            raise TypeError("child must be an Rst_Node")
        
        child_nodes, rel_type = children
        child_nodes.append(child)
        self.children = (child_nodes, rel_type)

    def add_satellite(satellite, rel_type):
        """Add an Rst_Node as satellite with relation type rel_type."""
        if not isinstance(satellite,Rst_Node):
            raise TypeError("satellite must be an Rst_Node")

        self.satellites.append((satellite, rel_type))

    
