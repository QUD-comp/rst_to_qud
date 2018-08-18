
class Qud_Node:
    """
    Class representing a QUD tree.

    Attributes
    ----------
    edu : String
        elemental discourse unit represented by this node
        In the current implementation, edu is always None for non-leaf nodes,
        but it could be extended to include explicit questions as quds.
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
