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
from runtime.stdlib import lua_tostring, lua_type, write_err
from runtime.values import LuaTable
from runtime import luacheck


class _CollectErrors(ErrorListener):
    def __init__(self):
        self.messages = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.messages.append(f"input:{line}:{column}: {msg}")


def run_source(source, interp=None):
    """Analiza y ejecuta un programa Lua (el texto usa un carácter por byte, latin-1).

    Si el programa tiene errores de sintaxis, Lua no ejecuta nada: se informa el error con el
    mismo mensaje que el compilador oficial (runtime/luacheck.py) y se termina con código 1.
    Si solo ANTLR se queja (el verificador lo acepta), se ejecuta el árbol recuperado.
    """
    if source.startswith("#"):
        source = "--" + source[1:]  # como lua.c: se ignora una primera línea '#!...'
    errors = _CollectErrors()
    lexer = LuaLexer(InputStream(source))
    lexer.removeErrorListeners()
    lexer.addErrorListener(errors)
    parser = LuaParser(CommonTokenStream(lexer))
    parser.removeErrorListeners()
    parser.addErrorListener(errors)
    tree = parser.start_()
    if errors.messages:
        problem = luacheck.check(source, "input")
        if problem is not None:
            raise LuaError(problem[0])
        for m in errors.messages:
            write_err("lua: " + m + chr(10))
    (interp or LuaInterpreter()).visit(tree.chunk())


def read_file(path):
    with open(path, "rb") as f:
        return f.read().decode("latin-1")


def error_text(err):
    """Mensaje como el 'msghandler' de lua.c para errores no capturados."""
    obj = err.lua_obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        return lua_tostring(obj)
    if isinstance(obj, LuaTable):
        mm = obj.metatable.rawget("__tostring") if isinstance(obj.metatable, LuaTable) else None
        if mm is not None:
            return lua_tostring(obj, _CURRENT[0])
    return "(error object is a %s value)" % lua_type(obj)


_CURRENT = [None]


def run_guarded(source, name=None):
    """Ejecuta y devuelve el código de salida (0 ok, 1 error).

    Al final (con o sin error) se cierra el estado: se llaman los finalizadores '__gc'
    pendientes, igual que lua_close en el intérprete oficial.
    """
    interp = LuaInterpreter()
    _CURRENT[0] = interp
    try:
        run_source(source, interp)
        return 0
    except LuaError as e:
        sys.stdout.flush()
        write_err("lua: " + error_text(e) + chr(10))
    except RecursionError:
        sys.stdout.flush()
        write_err("lua: stack overflow" + chr(10))
    except Exception as e:  # error interno (p. ej. árbol de sintaxis incompleto)
        sys.stdout.flush()
        write_err("lua: %s: %s" % (type(e).__name__, e) + chr(10))
    finally:
        try:
            interp.close_state()
        except BaseException:
            pass
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
            sys.setrecursionlimit(400_000 if sys.version_info >= (3, 11) else 220_000)
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
