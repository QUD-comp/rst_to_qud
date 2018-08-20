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
    segments_numbered = zip(segments, list(range(len(segments))))
    groups = xml_body.findall("group")
    groups_numbered = zip(groups, [None] * len(groups))

    #print(list(segments_numbered))
    #print(list(range(len(segments))))
    #for node in segments_numbered:
    #    print("Hallo")
    #    print(node.text)

    nodes = list(segments_numbered) + list(groups_numbered)

    
    root = list(filter(lambda x : not 'parent' in x[0].attrib.keys(), nodes))[0]
    
    ret_tree = build_tree(nodes, root=root)

    return ret_tree

def build_tree(nodes, root):
    """
    Build rst tree recursively.

    Parameters
    ----------
    nodes : [(xml.etree.ElementTree.Element,int)]
        tuples of nodes of the rst tree represented as xml element
        and ints giving the position of the corresponding EDUs in text
        int is None if the node doesn't contain text
    root : xml.etree.ElementTree.Element
        element of nodes, that becomes root node of returned tree

    Returns
    -------
    tree : Rst_Node
        root node, with attributes sattelites and children 
        containing the subtrees attached to the root node
    """
    
    attributes=root[0].attrib
    if not "type" in attributes.keys():
        children = []
        multi_nuc_relation = None
    elif attributes["type"] == "multinuc":
        children = find_children(nodes, root)#, debug=True)
        multi_nuc_relation = children[0][0].attrib["relname"]
    elif attributes["type"] == "span":
        children = find_span_children(nodes,root)
        multi_nuc_relation = None
    else:
        children = []
        multi_nuc_relation = None
    
    node = Rst_Node(edu=root[0].text, edu_num=root[1], multi_nuc_relation=multi_nuc_relation)

    for child in children:
        child_tree = build_tree(nodes, child)
        node.add_child(child_tree)

    satellites_left, satellites_right = find_satellites(nodes, root)

    for satellite in satellites_left:
        relname = satellite[0].attrib["relname"]
        satellite_tree = build_tree(nodes, satellite)
        node.add_satellite_left(satellite_tree, relname)
    for satellite in satellites_right:
        relname = satellite[0].attrib["relname"]
        satellite_tree = build_tree(nodes, satellite)
        node.add_satellite_right(satellite_tree, relname)
        
    return node


def find_children(nodes, parent, debug=False):
    """
    Find children in multinuclear relation.
 
    Parameters
    ----------
    nodes : [(xml.etree.ElementTree.Element, int)]
        tuples of nodes of the rst tree represented as xml element
        and ints giving the position of the corresponding EDUs in text
        int is None if the node doesn't contain text
    parent : (xml.etree.ElementTree.Element, int)
        element of nodes whose children (in multinuclear relations) are to be returned

    Returns
    -------
    children : [(xml.etree.ElementTree.Element, int)]
        child nodes in the multinuclear relation
    """
    parent_id = parent[0].attrib["id"]

    def parent_filter(n):
        if not "parent" in n[0].attrib.keys():
            return False
        else:
            return n[0].attrib["parent"] == parent_id
    
    def relname_filter(n):
        if not "relname" in n[0].attrib.keys():
            return False
        else:
            return n[0].attrib["relname"] in relations.multi_nuc

    if debug:
        print("nodes")
        print(nodes)
    children_and_satellites = filter(parent_filter, nodes)
    if debug:
        print("children_and_satellites")
        print(children_and_satellites)
    children = list(filter(relname_filter, children_and_satellites))
    if debug:
        print("children")
        print(children)

    children = reorder_children(children, nodes)
        
    return children


def reorder_children(children, nodes):
    """
    Reorder xml representations of children or satellites of one node according to the edus dominated by them.

    Parameters
    ----------
    children : [(xml.etree.ElementTree.Element, int)]
        list to be reordered
    nodes : [(xml.etree.ElementTree.Element, int)]
        list of all nodes in tree
    
    Returns
    -------
    reordered : [(xml.etree.ElementTree.Element, int)]
        reordered list
    """
    

    def find_edu_number(node):
        if not node[1] is None:
            return node
        parent_id = node[0].attrib["id"]
        edu_number = 0
        for n in nodes:
            attribs = n[0].attrib
            if "parent" in attribs.keys():
                if attribs["parent"] == parent_id and attribs["relname"] in relations.multi_nuc:
                    edu_number = find_edu_number(n)[1]

        return (node[0], edu_number)
    
    children = list(map(find_edu_number, children))
    snd = lambda x : x[1]
    return sorted(children, key=snd)

    


def find_satellites(nodes, nucleus):
    """
    Find satellites in mononuclear relation.
 
    Parameters
    ----------
    nodes : [(xml.etree.ElementTree.Element, int)]
        tuples of nodes of the rst tree represented as xml element
        and ints giving the position of the corresponding EDUs in text
        int is None if the node doesn't contain text
    nucleus : (xml.etree.ElementTree.Element, int)
        element of nodes whose satellites are to be returned

    Returns
    -------
    satellites_left : [(xml.etree.ElementTree.Element, int)]
        satellites to the left of nucleus
    satellites_right : [(xml.etree.ElementTree.Element, int)]
        satellites to the right of nucleus
    """

    nucleus_id = nucleus[0].attrib["id"]

    def parent_filter(n):
        if not "parent" in n[0].attrib.keys():
            return False
        else:
            return n[0].attrib["parent"] == nucleus_id
    
    def relname_filter(n):
        if not "relname" in n[0].attrib.keys():
            return False
        else:
            #print(n[0].attrib["relname"])
            return n[0].attrib["relname"] in relations.mono_nuc
        
    
    satellites_and_children = filter(parent_filter, nodes)
    satellites = list(filter(relname_filter, satellites_and_children))
    satellites_left, satellites_right = reorder_satellites(satellites, nodes, nucleus)
    
    return satellites_left, satellites_right


def reorder_satellites(satellites, nodes, nucleus):
    """
    Reorder xml representations of satellites of one node according to the edus dominated by them
    and order them into lists according to their position relative to the nucleus.

    Parameters
    ----------
    satellites : [(xml.etree.ElementTree.Element, int)]
        list to be reordered
    nodes : [(xml.etree.ElementTree.Element, int)]
        list of all nodes in tree
    nucleus : 
    
    Returns
    -------
    satellites_left : [(xml.etree.ElementTree.Element, int)]
        reordered list of satellites to the left of the nucleus
    satellites_right : [(xml.etree.ElementTree.Element, int)]
        reordered list of satellites to the right of the nucleus
    """
    #print(satellites)
    #print(nucleus)
    #for node in nodes:
    #    print(node[0].text)
    #    print(node[1])
    #for node in satellites:
    #    print(node[0].text)
    #    print(node[1])

    def find_edu_number(node):
        if not node[1] is None:
            #print("Hallo")
            #print(node[0].text)
            #print(node[1])
            return node
        parent_id = node[0].attrib["id"]
        edu_number = 0
        for n in nodes:
            attribs = n[0].attrib
            if "parent" in attribs.keys():
                if attribs["parent"] == parent_id:# and attribs["relname"] in relations.multi_nuc:
                    edu_number = find_edu_number(n)[1]

        return (node[0], edu_number)

    satellites = list(map(find_edu_number, satellites))
    #print(satellites)
    nucleus_pos = find_edu_number(nucleus)
    #print("nucleus_pos")
    #print(nucleus_pos)

    snd = lambda x : x[1]
    left = lambda x : x[1] < nucleus_pos[1]
    right = lambda x : x[1] > nucleus_pos[1]

    satellites_left = sorted(filter(left, satellites), key=snd)
    satellites_right = sorted(filter(right, satellites), key=snd)
    
    return satellites_left, satellites_right


def find_span_children(nodes, parent):
    """
    Find children of a span node.
 
    Parameters
    ----------
    nodes : [(xml.etree.ElementTree.Element, int)]
        tuples of nodes of the rst tree represented as xml element
        and ints giving the position of the corresponding EDUs in text
        int is None if the node doesn't contain text
    parent : (xml.etree.ElementTree.Element, int)
        element of nodes whose children (in multinuclear relations) are to be returned

    Returns
    -------
    children : [(xml.etree.ElementTree.Element, int)]
        child nodes in the multinuclear relation
    """
    parent_id = parent[0].attrib["id"]

    def parent_filter(n):
        if not "parent" in n[0].attrib.keys():
            return False
        else:
            return n[0].attrib["parent"] == parent_id
    
    def relname_filter(n):
        if not "relname" in n[0].attrib.keys():
            return False
        else:
            return n[0].attrib["relname"] == "span"

    
    children_and_sattelites = filter(parent_filter, nodes)
    children = list(filter(relname_filter, children_and_sattelites))

    return children


