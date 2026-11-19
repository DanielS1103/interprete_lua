import os
import sys
from antlr4 import FileStream, CommonTokenStream

sys.path.append(os.path.join(os.path.dirname(__file__), "grammar"))

from LuaLexer import LuaLexer
from LuaParser import LuaParser
from interpreter import LuaInterpreter

def run_file(filepath):
    input_stream = FileStream(filepath, encoding="utf-8")
    lexer = LuaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = LuaParser(token_stream)
    tree = parser.chunk()

    if parser.getNumberOfSyntaxErrors() > 0:
        raise SyntaxError(f"Errores sintácticos en {filepath}")

    interp = LuaInterpreter()
    interp.visit(tree)

if __name__ == "__main__":
    archivos = sys.argv[1:] if len(sys.argv) > 1 else [f"tests/0{i}.in" for i in range(1, 7)]
    for archivo in archivos:
        print(f"\n==================== {archivo} ====================")
        run_file(archivo)