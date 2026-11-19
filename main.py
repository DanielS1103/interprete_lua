import os
import sys
from antlr4 import FileStream, InputStream, CommonTokenStream

sys.path.append(os.path.join(os.path.dirname(__file__), "grammar"))

from LuaLexer import LuaLexer
from LuaParser import LuaParser
from interpreter import LuaInterpreter

def run_stream(input_stream):
    lexer = LuaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = LuaParser(token_stream)
    tree = parser.chunk()
    if parser.getNumberOfSyntaxErrors() > 0:
        raise SyntaxError("Errores sintácticos en el código Lua")
    LuaInterpreter().visit(tree)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for filepath in sys.argv[1:]:
            run_stream(FileStream(filepath, encoding="utf-8"))
    elif not sys.stdin.isatty():
        run_stream(InputStream(sys.stdin.read()))
    else:
        for i in range(1, 7):
            print(f"\n==================== tests/0{i}.in ====================")
            run_stream(FileStream(f"tests/0{i}.in", encoding="utf-8"))