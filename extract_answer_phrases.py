from nltk.parse import stanford
from nltk.tokenize import sent_tokenize, word_tokenize
import jpype
#from nltk.parse.corenlp import StanforCoreNLPParser

def extract_answer_phrases(text):
    #parser = StanforCoreNLPParser()
    parser = stanford.StanfordParser()

    sentences = sent_tokenize(text)

    classpath = "/home/johann/Studium/QMD/stanford-tregex-2018-02-27/stanford-tregex-3.9.1.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-javadoc.jar" + ":" + "/home/johann/Studium/QMD/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-models.jar"
    jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=%s" % classpath)

    #get tree from text
    #text_java =jpype.java.lang.String(text)
    #text_list = jpype.java.util.ArrayList()
    #text_list.add(text_java)
    words = word_tokenize(text)

    text_list = jpype.java.util.ArrayList()
    for word in words:
        Word = jpype.JPackage("edu").stanford.nlp.ling.Word(word)
        Word.setWord(word)
        text_list.add(Word)
        
    StanfordParser = jpype.JPackage("edu").stanford.nlp.parser.lexparser.LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    tree = StanfordParser.parse(text_list)
    
    TregexPattern = jpype.JPackage("edu").stanford.nlp.trees.tregex.TregexPattern
    print(tree)
    pattern = TregexPattern.compile("SBAR < WHADVP << S|NP|ADJP|VP|ADVP|PP=unmv")

    matcher = pattern.matcher(tree)
    print(matcher.getMatch())
    
    #jpype.java.lang.System.out.println(text)
    jpype.shutdownJVM()
    
    #print(list(list(parser.raw_parse_sents(sentences))[0]))

    #tregex_dir = "/home/johann/Studium/QMD/stanford-tregex-2018-02-27/"
    #op = Popen(["java", "-mx900m", "-cp", "stanford-tregex.jar:", "edu.stanford.nlp.trees.tregex.TregexPattern", "NP"],
    #           cwd = tregex_dir,
    #           stdout = PIPE,
    #           stdin = PIPE,
    #           stderr = STDOUT)
    #res = op.communicate(input=text)[0]
    #print(res)
    
    #print(list(list(parser.raw_parse_sents(sentences))[1]))

extract_answer_phrases("Darwin studied how species evolve.")
