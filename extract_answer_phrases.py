from nltk.parse import stanford
from nltk.tokenize import sent_tokenize, word_tokenize
import jpype
import rst_tree

#Tregex patterns from (Heilman, 2011)
#marking unmovable phrases
tregex_patterns = ["VP < (S=unmv $,, /,/)",
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

    print(rst)
    if not rst.edu is None:
        text = rst.edu
        question_content_list = extract_answer_phrases(text)
        question_content = " ".join(question_content_list)
        return question_content

    if len(rst.children[0]) > 1:
        #multinuc
        text = _find_text(rst.children[0])
        question_content_list = extract_answer_phrases(text)
        question_content = " ".join(question_content_list)
        return question_content

    if len(rst.children) == 0:
        raise Error("RST node is neither EDU nor does it have children.")

    #span
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
    print(rsts)
    for rst in rsts:
        print(rst)
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


def extract_answer_phrases(text):
    
    classpath = "/home/johann/Studium/QMD/stanford-tregex-2018-02-27/stanford-tregex-3.9.1.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-javadoc.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-models.jar"

    
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
    

    #tree_str = jpype.java.lang.String("(VBD (VBD studied) (VBD studied) )")
    #Tree = jpype.JPackage("edu").stanford.nlp.trees.Tree
    #tree = Tree.valueOf(tree_str)

    phrases = get_all_phrases(tree)

    TregexPattern = jpype.JPackage("edu").stanford.nlp.trees.tregex.TregexPattern

    for i, pattern_string in enumerate(tregex_patterns):
        pattern = TregexPattern.compile(pattern_string)
        phrases = remove_unmvs(tree, pattern, phrases)
        
    max_answer_phrase = find_longest(phrases)
    max_answer_phrase = list(map(str, max_answer_phrase))

    
    if max_answer_phrase is None:
        return text
    
    return max_answer_phrase


def find_longest(phrases):
    longest = None
    length = 0

    for phrase in phrases:
        if len(phrase) > length:
            longest = phrase
            length = len(phrase)

    return longest
    

def get_all_phrases(tree):

    phrases = []
    
    if len(tree.children()) != 1:
        phrases.append(tree.getLeaves())
    
    for child in tree.children():
        if not child.isLeaf():
            phrases += get_all_phrases(child)

    return phrases


def find_subphrases(phrase):
    subphrases = []

    for i in range(len(phrase)):
        phrase_i = list(phrase)

        while len(phrase_i) >= i:
            subphrase = phrase_i[:i+1]
            phrase_i = phrase_i[1:]
            subphrases.append(subphrase)

    return subphrases
    

def remove_unmvs(tree, pattern, phrases):
    matcher = pattern.matcher(tree)

    while matcher.find():
        unmv = matcher.getNode("unmv")
        if unmv is None:
            continue
        unmv_phrase = unmv.getLeaves()
        if unmv_phrase in phrases:
            phrases.remove(unmv_phrase)


    return phrases
    
    

