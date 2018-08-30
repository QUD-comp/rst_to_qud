from nltk.tokenize import sent_tokenize, word_tokenize
import jpype
import rst_tree
from pattern.en import conjugate, PROGRESSIVE
import os


def find_question_content(rst, gerund=True):
    """
    Extract the question content from the leaves of an rst tree, to use in a qud.

    Parameter
    ---------
    rst : Rst_Node
        tree from which the phrase is to be extracted
    
    Return
    ------
    question_content : String
        extracted phrase
    """

    if not rst.edu is None:
        text = rst.edu
        question_content_list = extract_from_text(text, gerund=gerund)
        question_content = " ".join(question_content_list)
        question_content = strip_content(question_content)
        return question_content

    if len(rst.children[0]) > 1:
        #multinuc
        #text = _find_text(rst.children[0])
        #question_content_list = extract_from_text(text, single=False)
        #question_content = " ".join(question_content_list)
        return "that"

    if len(rst.children) == 0:
        raise Error("RST node is neither EDU nor does it have children.")

    #span
    question_content = find_question_content(rst.children[0][0])

    return question_content


def strip_content(text):
    text = text.strip("., ")
    text = text[0].lower() + text[1:]
    return text


def extract_from_text(text, gerund=True):

    classpath = os.environ['CLASSPATH']
    if classpath is None:
        raise Error("Java classpath not set")
    if not jpype.isJVMStarted():
        jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)

    
    words = word_tokenize(text)

    text_list = jpype.java.util.ArrayList()
    for word in words:
        Word = jpype.JPackage("edu").stanford.nlp.ling.Word(word)
        Word.setWord(word)
        text_list.add(Word)

    StanfordParser = jpype.JPackage("edu").stanford.nlp.parser.lexparser.LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    tree = StanfordParser.parse(text_list)

    return extract_from_single(tree, gerund=gerund)


def extract_from_single(tree, gerund=True):
    pattern_string = "NP=nounp .. VP=verbp"
    TregexPattern = jpype.JPackage("edu").stanford.nlp.trees.tregex.TregexPattern
    pattern = TregexPattern.compile(pattern_string)
    matcher = pattern.matcher(tree)

    if matcher.find():
        np_tree = matcher.getNode("nounp")
        vp_tree = matcher.getNode("verbp")

        subject = extract_subject([np_tree])
        if gerund:
            rest = ingify(vp_tree)
        else:
            rest = list(map(str, vp_tree.getLeaves()))

        question_content = subject + rest
        return question_content

    text = list(map(str, tree.getLeaves()))

    return text

        
def extract_subject(trees):
    TregexPattern = jpype.JPackage("edu").stanford.nlp.trees.tregex.TregexPattern
    pattern = TregexPattern.compile("NP")

    for tree in trees:
        matcher = pattern.matcher(tree)
        if matcher.find():
            np_tree = matcher.getMatch()
            words = list(map(str, np_tree.getLeaves()))
            return words

    return []


def ingify(tree):

    children = tree.getChildrenAsList()
    
    vp_label = str(tree.label()) == "VP"
    not_no_children = not children.isEmpty()
    first_child_verb = not_no_children and str(children[0].label()) == "VBP"
    
    if not vp_label or not first_child_verb:
        leaves = tree.getLeaves()
        words = list(map(str, leaves))
        return words

    verb = str(children[0].getChildrenAsList()[0].label())

    verb_progressive = conjugate(verb, aspect=PROGRESSIVE)

    leaves = tree.getLeaves()
    words = list(map(str, leaves))
    words = words[1:]
    words = [verb_progressive] + words
    
    return words
