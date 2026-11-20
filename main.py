import os
import sys
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)  # usa el runtime de ANTLR incluido en ./antlr4
sys.path.append(os.path.join(BASE_DIR, "grammar"))

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from LuaLexer import LuaLexer
from LuaParser import LuaParser
from interpreter import LuaInterpreter
from runtime.exceptions import LuaError
from runtime.stdlib import lua_tostring, write_err
from runtime.values import LuaTable


class _CollectErrors(ErrorListener):
    def __init__(self):
        self.messages = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.messages.append(f"input:{line}:{column}: {msg}")


def run_source(source):
    """Analiza y ejecuta un programa Lua (el texto usa un carácter por byte, latin-1).

    La entrada se garantiza sintácticamente correcta; si ANTLR reporta algo, se avisa por
    stderr pero se intenta ejecutar igualmente el árbol recuperado.
    """
    errors = _CollectErrors()
    lexer = LuaLexer(InputStream(source))
    lexer.removeErrorListeners()
    lexer.addErrorListener(errors)
    parser = LuaParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(errors)
    tree = parser.start_()
    for m in errors.messages:
        write_err(f"lua: {m}\n")
    LuaInterpreter().visit(tree.chunk())


def read_file(path):
    with open(path, "rb") as f:
        return f.read().decode("latin-1")


def error_text(err):
    obj = err.lua_obj
    if isinstance(obj, LuaTable):
        mm = obj.metatable.rawget("__tostring") if isinstance(obj.metatable, LuaTable) else None
        if mm is None:
            return "(error object is a table value)"
    if obj is None:
        return "nil"
    return lua_tostring(obj)


def run_guarded(source, name=None):
    """Ejecuta y devuelve el código de salida (0 ok, 1 error)."""
    try:
        run_source(source)
        return 0
    except LuaError as e:
        sys.stdout.flush()
        write_err(f"lua: {error_text(e)}\n")
    except RecursionError:
        sys.stdout.flush()
        write_err("lua: stack overflow\n")
    except Exception as e:  # error interno (p. ej. árbol de sintaxis incompleto)
        sys.stdout.flush()
        write_err(f"lua: {type(e).__name__}: {e}\n")
    return 1


def main():
    sources = []
    if len(sys.argv) > 1:
        sources = [read_file(p) for p in sys.argv[1:]]
    elif not sys.stdin.isatty():
        sources = [sys.stdin.buffer.read().decode("latin-1")]
    else:
        for i in range(1, 7):
            print(f"\n==================== tests/0{i}.in ====================")
            sys.stdout.flush()
            sources.append(read_file(os.path.join(BASE_DIR, "tests", f"0{i}.in")))

    code = 0
    for src in sources:
        code = run_guarded(src) or code
    sys.stdout.flush()
    return code


def start():
    """Ejecuta main() en un hilo con pila grande para soportar recursión profunda de Lua."""
    result = {"code": 1}

    def target():
        result["code"] = main()

    started = False
    for stack_mb in (512, 256, 64, 16):
        try:
            threading.stack_size(stack_mb * 1024 * 1024)
            sys.setrecursionlimit(220_000)
            t = threading.Thread(target=target)
            t.start()
            started = True
            break
        except (ValueError, RuntimeError, MemoryError):
            continue
    if started:
        threading.stack_size(16 * 1024 * 1024)  # hilos de corrutinas
        t.join()
    else:
        threading.stack_size(0)
        sys.setrecursionlimit(5000)
        target()
    sys.stdout.flush()
    return result["code"]


if __name__ == "__main__":
    sys.exit(start())
