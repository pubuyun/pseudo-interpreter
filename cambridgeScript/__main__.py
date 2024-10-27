import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # cli()
    from cambridgeScript.parser.lexer import parse_tokens
    from parser.parser import Parser
    from interpreter.variables import VariableState
    from interpreter.interpreter import Interpreter

    tokens = parse_tokens(open("cambridgeScript/input.txt", 'r').read())
    for token in tokens:
        print(token)
    parsed = Parser.parse_program(tokens)
    print(parsed)
    interpreter = Interpreter(VariableState())
    interpreter.visit(parsed)
