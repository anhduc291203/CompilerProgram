import argparse
import json
import time

WHITESPACES = " \t\n\r\f"
NEWLINE = "\r\n"
EXCLUDE = "EXCLUDE"

NAME = "python3 lexer.py"
DESCRIPTION = "this is a lexer for the VC programming language."

def read_file(path: str):
    with open(path, "r") as file:
        return file.read()

def check_match(match: str, char: str):
    """
    Parameters
    ----------
    match : str
        a string of characters to match
    char : str
        the character to check

    Returns
    -------
    bool
        True if the match contains the character, False otherwise
    """
    global EXCLUDE

    if match.startswith(EXCLUDE):
        return char not in match[len(EXCLUDE):]
    return char in match


def lexer(source: str, nodes: dict, primitive_types: list, special_literals: list, no_comments: bool = False):
    """
    Parameters
    ----------
    source : str
        the source code to parse
    nodes : dict
        the nodes in the DFA
    primitive_types : list
        the list of primitive_types
    special_literals : list
        the list of special literals
    no_comments : bool, optional
        whether to ignore comments or not, by default False

    Returns
    -------
    list
        a list of tokens
    """
    global WHITESPACES, NEWLINE

    # Initialize the starting state
    STARTING_STATE = "0"
    for id in nodes:
        if nodes[id]["start"]:
            STARTING_STATE = id
            break

    tokens = []
    token = ""
    state = STARTING_STATE
    line = 1
    new_line_stack = ""
    position = 0
    start = position
    index = 0

    while index < len(source):
        char = source[index]
        index += 1
        position += 1
        
        # Skip whitespaces if the state is the starting state
        if state == STARTING_STATE and char in WHITESPACES:
            if char not in NEWLINE:
                new_line_stack = ""
            else:
                new_line_stack += char
                line += 1
                position = 0
            if new_line_stack.endswith(NEWLINE):
                new_line_stack = ""
                line -= 1
            continue
        
        # Check if current character matches any of the children
        children = nodes[state]["children"]
        found = False
        for match in children.keys():
            if check_match(match, char):
                state = children[match]
                if len(token) == 0:
                    start = position
                token += char
                found = True
                break
        
        # If no match is found, check if the current state is a end state
        if not found:
            index -= 1
            position -= 1

            # If the current state is a end state, add the token to the list of tokens
            if nodes[state]["end"] :
                if token in primitive_types:
                    tokens.append({"token": token, "type": "PRIMITIVE_TYPES", "line": line, "start": start, "end": position})
                elif token in special_literals:
                    tokens.append({"token": token, "type": "SPECIAL_LITERAL", "line": line, "start": start, "end": position})
                else:
                    tokens.append({"token": token, "type": nodes[state]["end_type"], "line": line, "start": start, "end": position})
                if token.endswith("\n"):
                    line += 1
                    position = 0
                token = ""
                state = STARTING_STATE

            # If the current state is not a end state, print an error message
            else:
                error_msg = f"Error while parsing '{token}': invalid character at line {line}({position}): '{char}', "
                expecting = list(nodes[state]['children'].keys())
                for i in range(len(expecting)):
                    if expecting[i].startswith(EXCLUDE):
                        expecting[i] = "everything except '" + expecting[i][len(EXCLUDE):] + "'"
                    elif len(expecting[i]) == 1:
                        expecting[i] = "'" + expecting[i] + "'"
                    else:
                        expecting[i] = "one of {'" + "', '".join(expecting[i]) + "'}"
                expecting = sorted(expecting, key=lambda x: x.startswith("everything except"))
                error_msg += f"expected: {' or '.join(expecting)}"
                error_msg = error_msg.encode("unicode_escape").decode("utf-8")
                error_msg = error_msg.replace("\\\\", "\\")
                print(error_msg)
                token = ""
                state = STARTING_STATE

    # Add the last token to the list of tokens
    if token:
        if nodes[state]["end"]:
            if token in primitive_types:
                tokens.append({"token": token, "type": "PRIMITIVE_TYPES", "line": line, "start": start, "end": position})
            elif token in special_literals:
                tokens.append({"token": token, "type": "SPECIAL_LITERAL", "line": line, "start": start, "end": position})
            else:
                tokens.append({"token": token, "type": nodes[state]["end_type"], "line": line, "start": start, "end": position})
    
    if no_comments:
        tokens = [token for token in tokens if token["type"] != "COMMENT"]

    return tokens

def run_lexer(filename, datafile, no_comments):
    """
    Parameters
    ----------
    filename : str
        the name of the file to parse
    datafile : str
        the name of the file containing the DFA
    no_comments : bool
        whether to ignore comments or not

    Returns
    -------
    list
        a list of tokens
    """

    # Read the source code and data file containing the DFA
    source = read_file(filename)
    with open(datafile, "r") as file:
        data = json.load(file)
        PRIMITIVE_TYPES = data["primitive_types"]
        SPECIAL_LITERALS = data["special_literals"]
        TOKEN_TYPES = data["end_type"]
        nodes = data["nodes"]

    # Parse the source code
    print("Parsing file: " + filename)
    start = time.time()
    if no_comments:
        # Remove comments if the user specified the -n or --no-comments option
        result = lexer(source, nodes, PRIMITIVE_TYPES, SPECIAL_LITERALS, True)
    else:
        result = lexer(source, nodes, PRIMITIVE_TYPES, SPECIAL_LITERALS)
    end = time.time()
    print(f"Done in {end-start:.3f} seconds.")

    # Export the tokens
    verbose = "VC compiler output"
    for token in result:
        verbose += f"\nKind = {TOKEN_TYPES.index(token['type'])} [{token['type']}]"
        verbose += f", spelling = \"{token['token']}\""
        verbose += f", position = {token['line']}({token['start']})..{token['line']}({token['end']})"

    output = ""
    for token in result:
        output += token["token"]
        output += "\n"

    # Remove extension from filename
    filename = filename.split(".")
    filename = ".".join(filename[:-1])

    verbose_filename = filename + ".verbose.vctok"
    with open(verbose_filename, "w+") as file:
        file.write(verbose)

    output_filename = filename + ".vctok"
    with open(output_filename, "w+") as file:
        file.write(output)

    print("Exported tokens to: " + output_filename)
    print("Exported verbose tokens to: " + verbose_filename)

    return result

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=DESCRIPTION
    )
    parser.add_argument("filename")
    parser.add_argument("datafile", nargs="?", default="dfa.json")
    parser.add_argument("-n", "--no-comments", action="store_true", help="remove comments tokens from the output")
    args = parser.parse_args()

    filename = args.filename
    datafile = args.datafile
    no_comments = args.no_comments

    run_lexer(filename, datafile, no_comments)