from rst_tree import Rst_Node
import xml.etree.ElementTree as ET

def read_rst_from_microtexts(filename):
    """
    Read rst tree from microtexts corpus
    
    Parameter
    ---------
    filename : String
        Filename/filepath of xml file containing the rst tree.

    Returns
    -------
    Rst_Node
        Same rst tree represented as Rst_Node.
    """

    tree = ET.parse(filename)
    root = tree.getroot()
    #while root.tag != "body":
    segments = root.iter(tag="segment")
    print(list(segments))
