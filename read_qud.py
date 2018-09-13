import rst_tree
import xml.etree.ElementTree as ET
import qud_tree
import re

def read_qud_from_microtexts(filename):
    """
    Read a QUD tree from the microtexts corpus.

    Paramaters
    ----------
    filename : String
        Name of the file containing the tree.

    Result
    ------
    qud_tree : Qud_Tree
        QUD tree read from file.
    """

    with open(filename) as f:
        lines = [line.strip() for line in f]

    lines = [line for line in lines if line != '']

    edus = get_edus(filename)

    qud_tree = get_subtree(lines, edus)

    return qud_tree


def get_edus(filename):
    """
    Get EDUs of text.

    Parameter
    ---------
    filename : String
        name of file containing the qud tree

    Returns
    -------
    edus : [String]
        EDUs of the text
    """
    regex = r"([a-z][0-9]{3})"
    match = re.search(regex, filename)

    if match is None:
        raise "Could not find micro_**** filename"

    xml_filename = "../arg-microtexts-multilayer/corpus/arg/micro_" + match.group(0) + ".xml"

    xml_tree = ET.parse(xml_filename)
    edus = xml_tree.findall("edu")
    edus = [edu.text for edu in edus]

    return edus




def get_subtree(lines, edus):
    """
    Recursively get subtree represented by lines in a file.

    Parameter
    ---------
    lines : [String]
        lines from the file
    edus : [String]
        EDUs of text

    Returns
    -------
    qud_tree : Qud_Tree
        tree represented by the lines
    """

    root_line = lines[0]

    match = re.match(r"(>*)(.*)", root_line)
    indent = len(match.group(1))
    children_lists = get_child_lines(lines[1:], indent)

    root_text = match.group(2).strip()

    if not is_edu(root_text, edus):
        #It's an implicit QUD.
        qud = qud_tree.Qud_Node(qud=root_text)
    elif children_lists != []:
        #It's an explicit question.
        qud = qud_tree.Qud_Node(qud=root_text, edu=root_text)
    else:
        #It's a leaf.
        qud = qud_tree.Qud_Node(edu=root_text)

    for child_list in children_lists:
        child_tree = get_subtree(child_list, edus)
        qud.add_child(child_tree)

    return qud


def is_edu(text, edus):
    """Check if text matches any of the edus in the list."""
    for edu in edus:
        match = re.match(edu.strip(), text)
        if match:
            return True
    return False


def get_child_lines(lines, root_indent):
    """
    Get lines which represent descendants of a node in the tree, 
    according to the indentation with ">".

    Parameters
    ----------
    lines : [str]
        lines from which to find the descendants
    root_indent : int
        number indicating how far the root of this subtree was indented
        descendants are all lines until one with the same indentation occurs
        (representing a sibling of the root, rather than descendant)

    Return
    ------
    children_lists : [[str]]
        For each child of the root of the current subtree,
        children_lists contains a list of the strings 
        representing the child and its descendants.
    """
    children_lists = []
    child_list = []
    for line in lines:
        match = re.match(r"(>*)(.*)", line.strip())
        curr_indent = len(match.group(1))
        if curr_indent == root_indent + 1:
            #child of root node of this specific tree
            if child_list != []:
                children_lists.append(child_list)
                child_list = []
            child_list.append(line)
        elif curr_indent > root_indent +1 :
            #indirect descendant of root
            child_list.append(line)
        else:
            #sibling of root of this subtree or sibling of parent of root
            if child_list != []:
                children_lists.append(child_list)
                child_list = []
            return children_lists

    if child_list != []:
        children_lists.append(child_list)

    return children_lists

