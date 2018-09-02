
class Qud_Node:
    """
    Class representing a QUD tree.

    Attributes
    ----------
    edu : String
        elemental discourse unit represented by this node
    qud : String
        Question under discussion. Is None for leaf nodes.
    children : [Qud_Node]
        children of this node
    """

    def __init__(self, edu=None, qud=None):
        self.edu = edu
        self.qud = qud

        self.children = []

    def add_child(self, child):
        """Add child to node."""
        if not isinstance(child, Qud_Node):
            raise TypeError("child must be a Qud_Node")

        self.children.append(child)

    def print_tree(self, indent=0):
        """
        Print this tree.

        Parameters
        ----------
        indent : int
            level of node in tree
        """

        if self.children == []:
            out_str = indent * ">" + str(self.edu)
        else:
            out_str = indent * ">" + str(self.qud)

        print(out_str)

        for child in self.children:
            child.print_tree(indent+1)
