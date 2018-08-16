from nltk.parse import stanford
from nltk.tokenize import sent_tokenize, word_tokenize
import jpype

def extract_answer_phrases(text):
    
    classpath = "/home/johann/Studium/QMD/stanford-tregex-2018-02-27/stanford-tregex-3.9.1.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-javadoc.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-models.jar"
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
    #pattern = TregexPattern.compile("SBAR < WHADVP << WRB|S|NP|ADJP|VP|ADVP|PP=unmv")
    pattern = TregexPattern.compile("S=unmv")

    potential_phrases = remove_unmvs(tree, pattern, phrases)
    max_answer_phrase = find_longest(potential_phrases)
    max_answer_phrase = list(map(str, max_answer_phrase))
    
    jpype.shutdownJVM()


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


    

def remove_unmvs(tree, pattern, phrases):
    matcher = pattern.matcher(tree)

    if matcher.matches():
        unmv = matcher.getNode("unmv")
        unmv_phrase = unmv.getLeaves()
        phrases.remove(unmv_phrase)

    children = tree.children()

    for child in children:
        phrases = remove_unmvs(child, pattern, phrases)

    return phrases
    
    

print(extract_answer_phrases("Darwin studied how species evolve."))
