import sys

from parser.lexer import *
from shell import *

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as file:
                code = file.read()
            shell_ = Shell()
            shell_.runProgram(filename, code)
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        shell_ = Shell()
        shell_.run()
    

if __name__ == '__main__':
    main()
