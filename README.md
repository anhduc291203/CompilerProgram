# Compiler

# Lexical Analyzer

## Introduction

This is a lexical analyzer for a subset of C language (VC) implemented using Python 3. The lexical analyzer is able to recognize tokens, comments and throw errors for invalid tokens. 

## **Prerequisites**

- ≥ Python 3.8 ( In my project i test version 3.8 and 3.12 and it work so you can you this version)
- You should also install some other libraries before running by pip: json, argparse.
- A data file containing information about the Deterministic finite automata (DFA) used in the lexical analyzer, the format of the file is defined in dfa.json file.
- Source code can detect for the VC compiler file.

## **Data File**

- The data file is in json format but the extension is *.json*, there's a json data file in the root directory of this project. The data file contains the following fields:
    - `primitive_types`: a list of primitive_types in target the language.
    - `special_literals`: a list of special literals used in target the language.
    - `end_type`: a list of types of tokens in target the language.
    - `nodes`: a list of nodes in the DFA, this includes:
        - the key of each node is the name of the node.
        - `children` is a list of children of the node, each child is a map from a list of characters to the name of the child node
        - if the node is the starting node, it will include a field `start` with value *true*.
        - if the node is end, it will include a field `end` with value *true* and a field `end_type` with the type of the token from `end_type` , else it will have a field `end` with value *false*.
- There is also a simple C program for you to use to test in the root directory of this project.
    
    ## **Run**
    
- To run the lexical analyzer, run the following command in the terminal (default value for `data_file` is *dfa.json*):

```
python lexer.py <source_code_file> [data_file]
```

- To see more information about the command, run the following command in the terminal:

```
python lexer.py -h
```

- You can add flag -n to not show out the comment.

```
python lexer.py <source_code_file> [data_file] -n
```