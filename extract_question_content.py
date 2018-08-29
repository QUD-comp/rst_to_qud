from nltk.tokenize import sent_tokenize, word_tokenize
import jpype
import rst_tree
from pattern.en import conjugate, PROGRESSIVE
import os

#Tregex patterns from (Heilman, 2011)
#marking unmovable phrases
heilman_patterns = ["VP < (S=unmv $,, /,/)",
                   "S < PP|ADJP|ADVP|S|SBAR=unmv > ROOT",
                   "/\\.*/ < CC << NP|ADJP|VP|ADVP|PP=unmv",
                   "SBAR < (IN|DT < /[ˆthat]/) << NP|PP=unmv",
                   "SBAR < /ˆWH.*P$/ << NP|ADJP|VP|ADVP|PP=unmv",
                   "SBAR <, IN|DT < (S < (NP=unmv !$,, VP))",
                   "S < (VP <+(VP) (VB|VBD|VBN|VBZ < be|being|been|is|are|was|were|am) <+(VP) (S << NP|ADJP|VP|ADVP|PP=unmv))",
                   "NP << (PP=unmv !< (IN < of|about))",
                   "PP << PP=unmv",
                   "NP $ VP << PP=unmv",
                   "SBAR=unmv [ !> VP | $-- /,/ | < RB ]",
                   "SBAR=unmv !< WHNP < (/ˆ[ˆS].*/ !<< that|whether|how)",
                   "NP=unmv < EX",
                   "/ˆS/ < ‘‘ << NP|ADJP|VP|ADVP|PP=unmv",
                   "PP=unmv !< NP",
                   "NP=unmv $ @NP",
                   "NP|PP|ADJP|ADVP << NP|ADJP|VP|ADVP|PP=unmv",
                   "@UNMV << NP|ADJP|VP|ADVP|PP=unmv"]

def find_question_content(rst):
    """
    Extract the answer phrase from the leaves of an rst tree, to use in a qud.

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
        print("nuc")
        text = rst.edu
        question_content_list = extract_from_text(text, single=True)
        question_content = " ".join(question_content_list)
        return question_content

    if len(rst.children[0]) > 1:
        print("multi")
        #multinuc
        text = _find_text(rst.children[0])
        question_content_list = extract_from_text(text, single=False)
        question_content = " ".join(question_content_list)
        return question_content

    if len(rst.children) == 0:
        raise Error("RST node is neither EDU nor does it have children.")

    #span
    print("span")
    question_content = find_question_content(rst.children[0][0])

    return question_content


def _find_text(rsts):
    """
    Find EDUs dominated by a list of nodes.

    Parameter
    ---------
    rsts : [Rst_Node]
        list of nodes of which the EDUs have to be found
    
    Return
    ------
    text : String
        combined EDUs
    """

    text = ""
    for rst in rsts:
        text += _find_text_single(rst) + " "

    text = text[:-1]
        
    return text

def _find_text_single(rst):
    text = ""
    if not rst.edu is None:
        text += rst.edu
    for sat, _ in rst.satellites_left:
        text += " " + _find_text_single(sat)
    for child in rst.children[0]:
        text += " " + _find_text_single(child)
    for sat, _ in rst.satellites_right:
        text += " " + _find_text_single(sat)
    return text


def extract_from_text(text, single=True):

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

    if single:
        return extract_from_single(tree)
    return ["that"]#extract_from_multinuc(tree)


def extract_from_multinuc(tree):#, TregexPattern):
    TregexPattern = jpype.JPackage("edu").stanford.nlp.trees.tregex.TregexPattern

    subtrees = tree.subTreeList()

    for i, pattern_string in enumerate(heilman_patterns):
        pattern = TregexPattern.compile(pattern_string)
        trees = remove_unmvs(subtrees, pattern)

    snd_longest = second_longest(trees)
    print("snd_longest")
    print(list(map(str, snd_longest.getLeaves())))
    siblings = snd_longest.siblings(tree)

    if siblings.isEmpty():
        return ingify(snd_longest)

    subject = extract_subject(siblings)
    rest = ingify(snd_longest)
    print("subject")
    print(subject)
    print("rest")
    print(rest)

    question_content = subject + rest

    return question_content

def remove_unmvs(subtrees, pattern):
    not_match = []
    for tree in subtrees:
        matcher = pattern.matcher(tree)
        if not matcher.matches():
            not_match.append(tree)

    return not_match

def second_longest(trees):
    tuples = []
    for tree in trees:
        tuples.append((len(tree.getLeaves()), tree))
    fst = lambda x: x[0]
    tuples = sorted(tuples, key=fst, reverse=True)
    
    len_longest = tuples[0][0]

    for length, tree in tuples:
        if length < len_longest:
            return tree
    
    return tuples[0][1]


def extract_from_single(tree, gerund=True):#, TregexPattern):
    pattern_string = "NP=nounp .. VP=verbp"
    TregexPattern = jpype.JPackage("edu").stanford.nlp.trees.tregex.TregexPattern
    pattern = TregexPattern.compile(pattern_string)
    matcher = pattern.matcher(tree)

    print(tree)

    if matcher.find():
        np_tree = matcher.getNode("nounp")
        vp_tree = matcher.getNode("verbp")

        subject = extract_subject([np_tree])
        if gerund:
            rest = ingify(vp_tree)
        else:
            rest = list(map(str, vp_tree.getLeaves()))

        print("subject")
        print(subject)
        print("rest")
        print(rest)

        question_content = subject + rest
        return question_content

    print("gnurgl")
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
