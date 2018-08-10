from rst_tree import Rst_Node
import xml.etree.ElementTree as ET
import relations


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

    xml_tree = ET.parse(filename)
    xml_root = xml_tree.getroot()
    xml_body = xml_root.find("body")
    segments = xml_body.findall("segment")
    groups = xml_body.findall("group")
    nodes = segments + groups

    root = list(filter(lambda x : not 'parent' in x.attrib.keys(), nodes))[0]
    
    ret_tree = build_tree(nodes, root=root)

    return ret_tree

def build_tree(nodes, root):
    """
    Build rst tree recursively.

    Parameters
    ----------
    nodes : [xml.etree.ElementTree.Element]
        nodes of the rst tree represented as xml elements
    root : xml.etree.ElementTree.Element
        element of nodes, that becomes root node of returned tree

    Returns
    -------
    tree : Rst_Node
        root node, with attributes sattelites and children 
        containing the subtrees attached to the root node
    """

    attributes=root.attrib
    if attributes["type"] == "multinuc":
        children = find_children(nodes, root)
        multi_nuc_relation = children[0].attrib["relname"]
    else:
        children = []
        multi_nuc_relation = None
    
    node = Rst_Node(edu=root.text, multi_nuc_relation=multi_nuc_relations)

    child_trees = []
    for child in children:
        child_tree = build_tree(nodes, child)
        node.add_child(child_tree)
        #child_trees.append(child_tree)

    satellites = find_satellites(nodes, root)

    for satellite in satellites:
        relname = satellite.attrib["relname"]
        satellite_tree = build_tree(nodes, satellite)
        node.add_satellite(satellite_tree, relname)
        
    
    return node

def find_children(nodes, parent):
    """
    Find children in multinuclear relation.
 
    Parameters
    ----------
    nodes : [xml.etree.ElementTree.Element]
        nodes of the rst tree represented as xml elements
    root : xml.etree.ElementTree.Element
        node whose children (in multinuclear relations) are to be returned

    Returns
    -------
    children : [xml.etree.ElementTree.Element]
        child nodes in the multinuclear relation
    """
    parent_id = parent.attrib[id]

    parent_filter = lambda n : n.attrib["parent"] == parent_id
    relname_filter = lambda n : n.attrib["relname"] in relations.multi_nuc
    
    children_and_sattelites = filter(parent_filter, nodes)
    children = list(filter(relname_filter, children_and_sattelites))

    return children


def find_satellites(nodes, nucleus):
    """
    Find satellites in mononuclear relation.
 
    Parameters
    ----------
    nodes : [xml.etree.ElementTree.Element]
        nodes of the rst tree represented as xml elements
    nucleus : xml.etree.ElementTree.Element
        node whose satellites are to be returned

    Returns
    -------
    satellites : [xml.etree.ElementTree.Element]
        satellites of nucleus
    """
    nucleus_id = parent.attrib[id]

    parent_filter = lambda n : n.attrib["parent"] == nucleus_id
    relname_filter = lambda n : n.attrib["relname"] in relations.mono_nuc
    
    satellites_and_children = filter(parent_filter, nodes)
    satellites = list(filter(relname_filter, satellites_and_children))

    return satellites
