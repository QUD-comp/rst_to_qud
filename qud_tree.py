
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

    def _get_tree_str(self, indent=0):
        """
        Return a string representing this tree.
        Used as helper function for print_tree and write_tree.

        Parameter
        ---------
        indent : int
            level of node in tree
        """
        if self.children == []:
            tree_str = indent * ">" + str(self.edu) + "\n"
        else:
            tree_str = indent * ">" + str(self.qud) + "\n"

        for child in self.children:
            tree_str += child._get_tree_str(indent+1)

        return tree_str

    def print_tree(self):
        """
        Print this tree.
        """
        print(self._get_tree_str())

    def write_tree(self, filename):
        """
        Write this tree to a file.

        Parameters
        ----------
        filename : str
            name of the file to write the tree to
        """

        tree_str = self._get_tree_str(indent = 0)

        with open(filename, "w") as out_file:
            out_file.write(tree_str)
        
