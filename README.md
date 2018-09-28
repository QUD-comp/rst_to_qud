# rst_to_qud
Project for the Questions and Models of Discourse course

## Requirements
* Python (tested with version 3.6.4)
* nltk (tested with version 3.2.5)
* jpype (tested with version 0.6.3)
* pattern.en (tested with version 2.6)
* the Stanford Parser (tested with version 3.9.1)
* the Stanford Tregex tool (tested with version 3.9.1)

## Transformation
Use transform_rst in transform_rst.py. It currently uses the relations from the arg-microtexts-multilayer corpus (https://github.com/peldszus/arg-microtexts-multilayer). Use read_rst.py to read an RST tree from the corpus.

##Tests
execute_tests.py acts as a wrapper for test.py. It takes a folder with RST trees from the arg-microtexts and a folder with QUD trees for the same texts.