import gc
import os
import re
import sys
import math
import time
import threading
import functools
from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from grammar.LuaLexer import LuaLexer
from grammar.LuaParser import LuaParser
from runtime.values import LuaTable, MultiRes, unwrap_one
from runtime.environment import Environment
from runtime.exceptions import LuaError
from runtime import lpattern, luacheck

MAXINT = 0x7FFFFFFFFFFFFFFF
MININT = -0x8000000000000000


# ---------------------------------------------------------------------------
# Salida / entrada: los strings de Lua se modelan como bytes (str latin-1)
# ---------------------------------------------------------------------------
def write_out(s):
    sys.stdout.buffer.write(s.encode("latin-1", "replace"))


def write_err(s):
    sys.stderr.buffer.write(s.encode("latin-1", "replace"))


# ---------------------------------------------------------------------------
# Números
# ---------------------------------------------------------------------------
def wrap_int64(n):
    n &= 0xFFFFFFFFFFFFFFFF
    return n - 0x10000000000000000 if n & 0x8000000000000000 else n


def fmt_float(x):
    """Formato de Lua 5.4 para floats ("%.14g" y '.0' si parece entero)."""
    if x != x:
        return "-nan" if math.copysign(1.0, x) < 0 else "nan"
    if x == math.inf:
        return "inf"
    if x == -math.inf:
        return "-inf"
    s = "%.14g" % x
    if "." not in s and "e" not in s and "n" not in s:
        s += ".0"
    return s


_DEC_RE = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$")
_DEC_INT_RE = re.compile(r"^[+-]?\d+$")
_HEX_RE = re.compile(r"^([+-]?)0[xX]([0-9a-fA-F]*)(?:\.([0-9a-fA-F]*))?(?:[pP]([+-]?\d+))?$")


def str2number(text):
    """Convierte un string a número como lo hace Lua; devuelve None si no es válido."""
    s = text.strip(" \t\n\r\f\v")
    if not s:
        return None
    if _DEC_INT_RE.match(s):
        n = int(s)
        return n if MININT <= n <= MAXINT else float(n)
    if _DEC_RE.match(s):
        try:
            return float(s)
        except ValueError:
            return None
    m = _HEX_RE.match(s)
    if m:
        sign, ip, fp, ex = m.groups()
        if not ip and not fp:
            return None
        if fp is None and ex is None:
            n = wrap_int64(int(ip, 16))
            return -n if sign == "-" and n != MININT else (wrap_int64(-n) if sign == "-" else n)
        try:
            val = float.fromhex("0x" + (ip or "0") + "." + (fp or "0") + "p" + (ex or "0"))
        except (ValueError, OverflowError):
            return None
        return -val if sign == "-" else val
    return None


def chunkid(source):
    """Nombre de un chunk para los mensajes, como luaO_chunkid (LUA_IDSIZE = 60)."""
    idsize = 60
    if source.startswith("="):
        return source[1:idsize]
    if source.startswith("@"):
        if len(source) <= idsize:
            return source[1:]
        return "..." + source[len(source) - (idsize - 4):]
    nl = source.find("\n")
    bufflen = idsize - len('[string "..."]') - 1
    if len(source) < bufflen and nl < 0:
        return '[string "' + source + '"]'
    s = source if nl < 0 else source[:nl]
    return '[string "' + s[:bufflen] + '..."]'


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ---------------------------------------------------------------------------
# type / tostring
# ---------------------------------------------------------------------------
def lua_type(val):
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "boolean"
    if isinstance(val, (int, float)):
        return "number"
    if isinstance(val, str):
        return "string"
    if isinstance(val, LuaTable):
        return "table"
    if isinstance(val, LuaCoroutine):
        return "thread"
    if hasattr(val, "_is_userdata"):
        return "userdata"
    if callable(val):
        return "function"
    return "userdata"


def lua_tostring(val, interp=None):
    if isinstance(val, LuaTable):
        if interp is not None:
            mm = interp._get_metamethod(val, "__tostring")
            if mm is not None:
                res = unwrap_one(interp._call_callable(mm, [val]))
                if not isinstance(res, str):
                    if is_number(res):
                        return lua_tostring(res)
                    raise LuaError("'__tostring' must return a string")
                return res
            name = interp._get_metamethod(val, "__name")
            if isinstance(name, str):
                return f"{name}: 0x{id(val):012x}"
        return f"table: 0x{id(val):012x}"
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return fmt_float(val)
    if isinstance(val, str):
        return val
    if isinstance(val, LuaCoroutine):
        return f"thread: 0x{id(val):012x}"
    if isinstance(val, LuaFile):
        return f"file (0x{id(val):012x})"
    if callable(val):
        return f"function: 0x{id(val):012x}"
    return str(val)


# ---------------------------------------------------------------------------
# Archivos (io)
# ---------------------------------------------------------------------------
class LuaFile:
    _is_userdata = True

    def __init__(self, kind, interp):
        self.kind = kind  # "stdin" | "stdout" | "stderr"
        self.interp = interp
        self.closed = False
        self.methods = {}

    def write(self, *args):
        for a in args:
            if isinstance(a, str):
                s = a
            elif isinstance(a, float) and math.isfinite(a):
                s = "%.14g" % a  # io.write de Lua 5.4 usa LUA_NUMBER_FMT sin el ".0"
            elif is_number(a):
                s = lua_tostring(a)
            else:
                raise self.interp.rt_error(f"bad argument #1 to 'write' (string expected, got {lua_type(a)})")
            if self.kind == "stderr":
                write_err(s)
            else:
                write_out(s)
        return self

    def _readline(self, keep_nl):
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        s = line.decode("latin-1")
        if not keep_nl and s.endswith("\n"):
            s = s[:-1]
        return s

    def _read_number(self):
        buf = sys.stdin.buffer
        while True:  # salta espacios en blanco
            c = buf.peek(1)[:1]
            if not c or c not in b" \t\n\r\f\v":
                break
            buf.read(1)
        tok = bytearray()
        while len(tok) < 200:
            c = buf.peek(1)[:1]
            if not c or c not in b"0123456789+-.xXaAbBcCdDeEfFpP":
                break
            tok += buf.read(1)
        return str2number(tok.decode("latin-1")) if tok else None

    def read_one(self, fmt):
        if isinstance(fmt, int) and not isinstance(fmt, bool):
            data = sys.stdin.buffer.read(fmt)
            if not data and fmt > 0:
                return None
            return data.decode("latin-1")
        f = str(fmt).lstrip("*")[:1]
        if f == "l":
            return self._readline(False)
        if f == "L":
            return self._readline(True)
        if f == "a":
            return sys.stdin.buffer.read().decode("latin-1")
        if f == "n":
            return self._read_number()
        raise LuaError("bad argument #1 to 'read' (invalid format)")

    def read(self, *fmts):
        if not fmts:
            return self.read_one("l")
        out = []
        for f in fmts:
            v = self.read_one(f)
            out.append(v)
            if v is None:
                break
        return MultiRes(out)


# ---------------------------------------------------------------------------
# Corrutinas (basadas en hilos)
# ---------------------------------------------------------------------------
class LuaCoroutine:
    _active_stack = []

    def __init__(self, fn, interp):
        self.fn = fn
        self.interp = interp
        self.status = "suspended"
        self.cond = threading.Condition()
        self.transfer_vals = []
        self.error_obj = None
        self.has_error = False
        self.saved_env = None
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.started = False

    def _run(self):
        with self.cond:
            while self.status != "running":
                self.cond.wait()
            init_args = list(self.transfer_vals)

        try:
            res = self.interp._call_callable(self.fn, init_args)
            out = list(res) if isinstance(res, MultiRes) else ([] if res is None else [res])
            with self.cond:
                self.status = "dead"
                self.transfer_vals = out
                self.cond.notify_all()
        except LuaError as e:
            with self.cond:
                self.status = "dead"
                self.has_error = True
                self.error_obj = e.lua_obj
                self.cond.notify_all()
        except RecursionError:
            with self.cond:
                self.status = "dead"
                self.has_error = True
                self.error_obj = "stack overflow"
                self.cond.notify_all()
        except BaseException as e:
            with self.cond:
                self.status = "dead"
                self.has_error = True
                self.error_obj = str(e)
                self.cond.notify_all()

    def resume(self, *args):
        with self.cond:
            if self.status == "dead":
                return MultiRes([False, "cannot resume dead coroutine"])
            if self.status == "running":
                return MultiRes([False, "cannot resume non-suspended coroutine"])

            caller_env = self.interp.current_env
            if self.saved_env is not None:
                self.interp.current_env = self.saved_env

            self.transfer_vals = list(args)
            self.status = "running"
            LuaCoroutine._active_stack.append(self)

            if not self.started:
                self.started = True
                self.thread.start()
            self.cond.notify_all()

            while self.status == "running":
                self.cond.wait()

            LuaCoroutine._active_stack.pop()
            self.interp.current_env = caller_env

            if self.has_error:
                return MultiRes([False, self.error_obj])
            return MultiRes([True] + list(self.transfer_vals))

    def real_status(self):
        if self.status == "running" and LuaCoroutine._active_stack and LuaCoroutine._active_stack[-1] is not self:
            return "normal"
        return self.status

    @classmethod
    def yield_current(cls, *args):
        if not cls._active_stack:
            raise LuaError("attempt to yield from outside a coroutine")
        co = cls._active_stack[-1]
        with co.cond:
            co.saved_env = co.interp.current_env
            co.transfer_vals = list(args)
            co.status = "suspended"
            co.cond.notify_all()

            while co.status == "suspended":
                co.cond.wait()
            return MultiRes(list(co.transfer_vals))


# ---------------------------------------------------------------------------
# Construcción del entorno global
# ---------------------------------------------------------------------------
def build_global_env(interp):
    env = LuaTable()
    env.rawset("_G", env)
    env.rawset("_VERSION", "Lua 5.4")

    # ---- helpers de validación ----
    def tname(v, n):
        """Tipo de un argumento para mensajes 'bad argument' ("no value" si no se pasó)."""
        if v is None and n > getattr(interp, "nargs", 0):
            return "no value"
        return lua_type(v)

    def arg_error(n, fname, msg):
        raise interp.rt_error(f"bad argument #{n} to '{fname}' ({msg})")

    def check_table(v, n, fname):
        if not isinstance(v, LuaTable):
            arg_error(n, fname, f"table expected, got {tname(v, n)}")
        return v

    def check_int(v, n, fname, default=None):
        if v is None and default is not None:
            return default
        if isinstance(v, bool):
            arg_error(n, fname, f"number expected, got boolean")
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            if v.is_integer():
                return int(v)
            arg_error(n, fname, "number has no integer representation")
        if isinstance(v, str):
            num = str2number(v)
            if num is not None:
                return check_int(num, n, fname)
        arg_error(n, fname, f"number expected, got {tname(v, n)}")

    def check_num(v, n, fname, default=None):
        if v is None and default is not None:
            return default
        if is_number(v):
            return v
        if isinstance(v, str):
            num = str2number(v)
            if num is not None:
                return num
        arg_error(n, fname, f"number expected, got {tname(v, n)}")

    def check_str(v, n, fname, default=None):
        if v is None and default is not None:
            return default
        if isinstance(v, str):
            return v
        if is_number(v):
            return lua_tostring(v)
        arg_error(n, fname, f"string expected, got {tname(v, n)}")

    def tostr(v):
        return lua_tostring(v, interp)

    # ---- funciones base ----
    def _print(*args):
        write_out("\t".join(tostr(a) for a in args) + "\n")
        return MultiRes()

    def _type(*args):
        if not args:
            arg_error(1, "type", "value expected")
        return lua_type(args[0])

    def _error(msg=None, level=1):
        if isinstance(msg, str) and isinstance(level, int) and level > 0:
            raise interp.rt_error(msg, level)
        raise LuaError(msg)

    def _call_protected(fn, args):
        saved_line = interp.cur_line
        interp.cur_line = None  # la función se invoca desde un builtin: sin línea para 'error(msg, 2)'
        try:
            res = interp._call_callable(fn, list(args))
            if isinstance(res, MultiRes):
                return MultiRes([True] + list(res))
            return MultiRes([True, res])
        except LuaError as e:
            return MultiRes([False, e.lua_obj])
        except RecursionError:
            return MultiRes([False, "stack overflow"])
        except Exception as e:  # error interno del intérprete: se informa como error Lua
            return MultiRes([False, f"{type(e).__name__}: {e}"])
        finally:
            interp.cur_line = saved_line

    def _pcall(fn=None, *args):
        if fn is None:
            arg_error(1, "pcall", "value expected")
        return _call_protected(fn, args)

    def _xpcall(fn, msgh, *args):
        try:
            res = interp._call_callable(fn, list(args))
            if isinstance(res, MultiRes):
                return MultiRes([True] + list(res))
            return MultiRes([True, res])
        except LuaError as e:
            handled = interp._call_callable(msgh, [e.lua_obj])
            return MultiRes([False] + (list(handled) if isinstance(handled, MultiRes) else [handled]))
        except RecursionError:
            handled = interp._call_callable(msgh, ["stack overflow"])
            return MultiRes([False] + (list(handled) if isinstance(handled, MultiRes) else [handled]))

    class _SyntaxCollector(ErrorListener):
        def __init__(self):
            self.errors = []

        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            tok = "<eof>"
            if offendingSymbol is not None and offendingSymbol.type != -1:
                tok = "'" + offendingSymbol.text + "'"
            self.errors.append((line, tok))

    def _load(chunk=None, chunkname=None, mode="bt", custom_env=None):
        has_env = interp.nargs >= 4  # load(s, n, m, nil) fija _ENV = nil
        if callable(chunk) and not isinstance(chunk, str):
            parts = []
            while True:
                piece = unwrap_one(interp._call_callable(chunk, []))
                if piece is None or piece == "":
                    break
                parts.append(piece)
            chunk = "".join(parts)
            default_name = "=(load)"
        elif isinstance(chunk, str):
            default_name = chunk
        else:
            arg_error(1, "load", f"function expected, got {tname(chunk, 1)}")
        name = chunkname if isinstance(chunkname, str) else default_name
        display = chunkid(name)
        if isinstance(mode, str) and "t" not in mode:
            return MultiRes([None, f"attempt to load a text chunk (mode is '{mode}')"])
        from interpreter import LuaFunction
        # Errores de compilación con los mensajes de Lua (léxicos, sintácticos y semánticos)
        problem = luacheck.check(chunk, display)
        if problem is not None:
            return MultiRes([None, problem[0]])
        collector = _SyntaxCollector()
        lexer = LuaLexer(InputStream(chunk))
        lexer.removeErrorListeners()
        lexer.addErrorListener(collector)
        parser = LuaParser(CommonTokenStream(lexer))
        parser.removeErrorListeners()
        parser.addErrorListener(collector)
        tree = parser.start_()
        if collector.errors:
            line, tok = collector.errors[0]
            return MultiRes([None, f"{display}:{line}: syntax error near {tok}"])
        target_env_tbl = custom_env if (custom_env is not None or has_env) else env
        chunk_env = Environment(parent=None, env_table=target_env_tbl)
        return LuaFunction([], True, tree.chunk().block(), chunk_env, interp, display)

    def _setmetatable(t=None, mt=None):
        if not isinstance(t, LuaTable):
            arg_error(1, "setmetatable", f"table expected, got {tname(t, 1)}")
        if mt is not None and not isinstance(mt, LuaTable):
            arg_error(2, "setmetatable", f"nil or table expected, got {lua_type(mt)}")
        if isinstance(t.metatable, LuaTable) and t.metatable.rawget("__metatable") is not None:
            raise interp.rt_error("cannot change a protected metatable")
        t.metatable = mt
        if mt is not None and mt.rawget("__gc") is not None:
            interp.mark_for_gc(t)
        return t

    def _getmetatable(obj=None):
        if isinstance(obj, LuaTable):
            mt = obj.metatable
        elif isinstance(obj, str):
            mt = string_meta
        else:
            return None
        if isinstance(mt, LuaTable):
            protected = mt.rawget("__metatable")
            if protected is not None:
                return protected
        return mt

    def _rawset(t, k, v):
        check_table(t, 1, "rawset")
        t.rawset(k, v)
        return t

    def _rawget(t, k):
        check_table(t, 1, "rawget")
        return t.rawget(k)

    def _rawequal(a, b):
        if is_number(a) and is_number(b):
            return a == b
        return a is b or (type(a) is type(b) and not isinstance(a, LuaTable) and a == b)

    def _rawlen(v):
        if isinstance(v, LuaTable):
            return v.length()
        if isinstance(v, str):
            return len(v)
        raise interp.rt_error("table or string expected")

    def _ipairs_iter(t, i):
        i = i + 1
        v = interp._table_get(t, i)
        if v is None:
            return None
        return MultiRes([i, v])

    def _ipairs(t=None):
        if t is None:
            arg_error(1, "ipairs", "table expected, got nil")
        return MultiRes([_ipairs_iter, t, 0])

    def _next(t, k=None):
        check_table(t, 1, "next")
        keys = t.keys()
        if not keys:
            if k is not None:
                raise interp.rt_error("invalid key to 'next'")
            return None
        if k is None:
            first_k = keys[0]
            return MultiRes([first_k, t.rawget(first_k)])
        for idx, curr_k in enumerate(keys):
            if curr_k is k or (type(curr_k) is type(k) and curr_k == k) or \
               (is_number(curr_k) and is_number(k) and curr_k == k):
                if idx + 1 < len(keys):
                    nk = keys[idx + 1]
                    return MultiRes([nk, t.rawget(nk)])
                return None
        raise interp.rt_error("invalid key to 'next'")

    def _pairs(t=None):
        mm = interp._get_metamethod(t, "__pairs")
        if mm is not None:
            res = interp._call_callable(mm, [t])
            vals = list(res) if isinstance(res, MultiRes) else [res]
            return MultiRes((vals + [None, None, None])[:3])
        check_table(t, 1, "pairs")
        # Iterador con estado: primero la parte secuencial 1..n y luego el resto en orden de inserción
        keys = t.keys()
        seq = []
        i = 1
        while t.rawget(i) is not None:
            seq.append(i)
            i += 1
        seqset = set(seq)
        rest = [k for k in keys if not (is_number(k) and not isinstance(k, bool) and k in seqset)]
        order = seq + rest
        state = {"i": 0}

        def _iter(_t=None, _k=None):
            while state["i"] < len(order):
                k = order[state["i"]]
                state["i"] += 1
                v = t.rawget(k)
                if v is not None:
                    return MultiRes([k, v])
            return None

        return MultiRes([_iter, t, None])

    def _tonumber(v=None, base=None):
        if base is None:
            if is_number(v):
                return v
            if isinstance(v, str):
                return str2number(v)
            return None
        base = check_int(base, 2, "tonumber")
        s = check_str(v, 1, "tonumber").strip(" \t\n\r\f\v").lower()
        neg = s.startswith("-")
        if neg:
            s = s[1:]
        if not s or not all(c.isalnum() and c.isascii() for c in s):
            return None
        try:
            n = int(s, base)
        except ValueError:
            return None
        return wrap_int64(-n if neg else n)

    def _select(n, *args):
        if n == "#":
            return len(args)
        n = check_int(n, 1, "select")
        if n < 0:
            n = len(args) + n
            if n < 0:
                arg_error(1, "select", "index out of range")
            return MultiRes(list(args[n:]))
        if n == 0:
            arg_error(1, "select", "index out of range")
        return MultiRes(list(args[n - 1:]))

    def _assert(*args):
        if not args:
            arg_error(1, "assert", "value expected")
        if args[0] is None or args[0] is False:
            msg = args[1] if len(args) > 1 else "assertion failed!"
            if isinstance(msg, str):
                raise interp.rt_error(msg)
            raise LuaError(msg)
        return MultiRes(list(args))

    gc_state = {"running": True, "mode": "incremental", "setpause": 200, "setstepmul": 100}

    def _collectgarbage(*args):
        opt = args[0] if args and args[0] is not None else "collect"
        if not isinstance(opt, str):
            arg_error(1, "collectgarbage", f"string expected, got {tname(opt, 1)}")
        if opt == "collect":
            interp.full_gc()
            return 0
        if opt == "count":
            return float(len(gc.get_objects())) / 10.0
        if opt == "step":
            interp.full_gc()
            return True
        if opt in ("stop", "restart"):
            gc_state["running"] = opt == "restart"
            return 0
        if opt == "isrunning":
            return gc_state["running"]
        if opt in ("setpause", "setstepmul"):
            prev = gc_state[opt]
            gc_state[opt] = check_int(args[1] if len(args) > 1 else None, 2, "collectgarbage", 0)
            return prev
        if opt in ("incremental", "generational"):
            prev = gc_state["mode"]
            gc_state["mode"] = opt
            return prev
        arg_error(1, "collectgarbage", f"invalid option '{opt}'")

    # ---- table ----
    table_lib = LuaTable()

    def _table_pack(*args):
        res = LuaTable()
        for idx, val in enumerate(args, start=1):
            res.rawset(idx, val)
        res.asize = len(args)
        res.rawset("n", len(args))
        return res

    def _table_unpack(t, i=1, j=None):
        i = check_int(i, 2, "unpack", 1)
        if j is None:
            j = interp._table_len(t)
        j = check_int(j, 3, "unpack")
        if j - i >= 10_000_000:
            raise interp.rt_error("too many results to unpack")
        return MultiRes([interp._table_get(t, idx) for idx in range(i, j + 1)])

    def _table_insert(t=None, *args):
        check_table(t, 1, "insert")
        n = interp._table_len(t)
        if len(args) == 1:
            t.rawset(n + 1, args[0])
        elif len(args) == 2:
            pos = check_int(args[0], 2, "insert")
            if pos < 1 or pos > n + 1:
                arg_error(2, "insert", "position out of bounds")
            for k in range(n, pos - 1, -1):
                t.rawset(k + 1, t.rawget(k))
            t.rawset(pos, args[1])
        else:
            raise interp.rt_error("wrong number of arguments to 'insert'")
        return MultiRes()

    def _table_remove(t=None, pos=None):
        check_table(t, 1, "remove")
        n = interp._table_len(t)
        if pos is None:
            pos = n
        else:
            pos = check_int(pos, 2, "remove")
            if n + 1 == pos:
                v = t.rawget(pos)
                t.rawset(pos, None)
                return v
            if n == 0 and pos == 0:
                return t.rawget(pos)
            if pos < 1 or pos > n + 1:
                arg_error(2, "remove", "position out of bounds")
        v = t.rawget(pos)
        for k in range(pos, n):
            t.rawset(k, t.rawget(k + 1))
        if pos <= n:
            t.rawset(n, None)
        return v

    def _table_concat(t=None, sep="", i=1, j=None):
        check_table(t, 1, "concat")
        sep = check_str(sep, 2, "concat", "")
        i = check_int(i, 3, "concat", 1)
        j = interp._table_len(t) if j is None else check_int(j, 4, "concat")
        parts = []
        for k in range(i, j + 1):
            v = interp._table_get(t, k)
            if isinstance(v, str):
                parts.append(v)
            elif is_number(v):
                parts.append(lua_tostring(v))
            else:
                raise interp.rt_error(f"invalid value ({lua_type(v)}) at index {k} in table for 'concat'")
        return sep.join(parts)

    def _table_sort(t=None, comp=None):
        """Quicksort de ltablib.c (Lua 5.4): mismo orden de comparaciones e intercambios,
        así que el resultado coincide con Lua incluso con elementos 'empatados'."""
        check_table(t, 1, "sort")
        n = interp._table_len(t)
        if n <= 1:
            return MultiRes()
        if comp is not None and not (callable(comp) and not isinstance(comp, LuaTable)):
            arg_error(2, "sort", f"function expected, got {tname(comp, 2)}")
        a = [None] + [interp._table_get(t, k) for k in range(1, n + 1)]
        if comp is not None:
            def lt(x, y):
                r = interp._call_callable(comp, [x, y])
                if r.__class__ is MultiRes:
                    r = r[0] if r else None
                return r is not None and r is not False
        else:
            def lt(x, y):
                return interp._lua_compare("<", x, y)

        def bad_order():
            # luaL_error: lleva la posición del llamador de 'sort' (si es código Lua)
            msg = "invalid order function for sorting"
            if saved_line is not None:
                msg = f"{interp.chunkname}:{saved_line}: {msg}"
            raise LuaError(msg)

        def auxsort(lo, up):
            while lo < up:
                if lt(a[up], a[lo]):
                    a[lo], a[up] = a[up], a[lo]
                if up - lo == 1:
                    break
                p = (lo + up) // 2
                if lt(a[p], a[lo]):
                    a[p], a[lo] = a[lo], a[p]
                elif lt(a[up], a[p]):
                    a[p], a[up] = a[up], a[p]
                if up - lo == 2:
                    break
                pivot = a[p]
                a[p], a[up - 1] = a[up - 1], pivot
                i, j = lo, up - 1
                while True:
                    i += 1
                    while lt(a[i], pivot):
                        if i == up - 1:
                            bad_order()
                        i += 1
                    j -= 1
                    while lt(pivot, a[j]):
                        if j < i:
                            bad_order()
                        j -= 1
                    if j < i:
                        a[up - 1] = a[i]
                        a[i] = pivot
                        break
                    a[i], a[j] = a[j], a[i]
                p = i
                if p - lo < up - p:
                    auxsort(lo, p - 1)
                    lo = p + 1
                else:
                    auxsort(p + 1, up)
                    up = p - 1

        saved_line = interp.cur_line
        interp.cur_line = None  # los errores de comparación ocurren dentro de 'sort' (función C): sin posición
        try:
            auxsort(1, n)
        finally:
            interp.cur_line = saved_line
        for k in range(1, n + 1):
            interp._table_set(t, k, a[k])
        return MultiRes()

    def _table_move(a1, f, e, tpos, a2=None):
        a2 = a1 if a2 is None else a2
        f = check_int(f, 2, "move")
        e = check_int(e, 3, "move")
        tpos = check_int(tpos, 4, "move")
        if e >= f:
            if tpos > e or tpos <= f or a1 is not a2:
                for k in range(0, e - f + 1):
                    interp._table_set(a2, tpos + k, interp._table_get(a1, f + k))
            else:
                for k in range(e - f, -1, -1):
                    interp._table_set(a2, tpos + k, interp._table_get(a1, f + k))
        return a2

    for name, fn in (("pack", _table_pack), ("unpack", _table_unpack), ("insert", _table_insert),
                     ("remove", _table_remove), ("concat", _table_concat), ("sort", _table_sort),
                     ("move", _table_move)):
        table_lib.rawset(name, fn)

    # ---- coroutine ----
    coro_lib = LuaTable()
    main_co = LuaCoroutine(None, interp)
    main_co.status = "running"

    def _co_create(fn=None):
        if not callable(fn) or isinstance(fn, LuaTable):
            arg_error(1, "create", f"function expected, got {tname(fn, 1)}")
        return LuaCoroutine(fn, interp)

    def _co_resume(co=None, *args):
        if not isinstance(co, LuaCoroutine):
            arg_error(1, "resume", f"coroutine expected, got {tname(co, 1)}")
        return co.resume(*args)

    def _co_wrap(fn=None):
        if not callable(fn) or isinstance(fn, LuaTable):
            arg_error(1, "wrap", f"function expected, got {tname(fn, 1)}")
        co = LuaCoroutine(fn, interp)

        def wrapped(*args):
            res = co.resume(*args)
            if res[0] is True:
                return MultiRes(list(res[1:]))
            if isinstance(res[1], str):
                raise interp.rt_error(res[1])  # como auxwrap: antepone la posición del llamador
            raise LuaError(res[1])

        return wrapped

    def _co_status(co=None):
        if not isinstance(co, LuaCoroutine):
            arg_error(1, "status", f"coroutine expected, got {tname(co, 1)}")
        return co.real_status()

    def _co_running():
        if LuaCoroutine._active_stack:
            return MultiRes([LuaCoroutine._active_stack[-1], False])
        return MultiRes([main_co, True])

    def _co_close(co=None):
        if not isinstance(co, LuaCoroutine):
            arg_error(1, "close", f"coroutine expected, got {tname(co, 1)}")
        if co.status in ("suspended", "dead"):
            co.status = "dead"
            if co.has_error:
                co.has_error = False
                return MultiRes([False, co.error_obj])
            return True
        raise interp.rt_error(f"cannot close a {co.real_status()} coroutine")

    coro_lib.rawset("create", _co_create)
    coro_lib.rawset("resume", _co_resume)
    coro_lib.rawset("yield", lambda *args: LuaCoroutine.yield_current(*args))
    coro_lib.rawset("status", _co_status)
    coro_lib.rawset("wrap", _co_wrap)
    coro_lib.rawset("running", _co_running)
    coro_lib.rawset("isyieldable", lambda *a: bool(LuaCoroutine._active_stack))
    coro_lib.rawset("close", _co_close)

    # ---- math ----
    math_lib = LuaTable()
    math_lib.rawset("pi", math.pi)
    math_lib.rawset("huge", math.inf)
    math_lib.rawset("maxinteger", MAXINT)
    math_lib.rawset("mininteger", MININT)

    def _floor(x=None):
        x = check_num(x, 1, "floor")
        if isinstance(x, int):
            return x
        if math.isnan(x) or math.isinf(x):
            return x
        r = math.floor(x)
        return r if MININT <= r <= MAXINT else float(r)

    def _ceil(x=None):
        x = check_num(x, 1, "ceil")
        if isinstance(x, int):
            return x
        if math.isnan(x) or math.isinf(x):
            return x
        r = math.ceil(x)
        return r if MININT <= r <= MAXINT else float(r)

    def _abs(x=None):
        x = check_num(x, 1, "abs")
        return wrap_int64(abs(x)) if isinstance(x, int) else abs(x)

    def _max(*args):
        if not args:
            arg_error(1, "max", "number expected, got no value")
        best = check_num(args[0], 1, "max")
        for i, a in enumerate(args[1:], start=2):
            a = check_num(a, i, "max")
            if best < a:
                best = a
        return best

    def _min(*args):
        if not args:
            arg_error(1, "min", "number expected, got no value")
        best = check_num(args[0], 1, "min")
        for i, a in enumerate(args[1:], start=2):
            a = check_num(a, i, "min")
            if a < best:
                best = a
        return best

    def _sqrt(x=None):
        x = float(check_num(x, 1, "sqrt"))
        if x != x:
            return x
        return math.sqrt(x) if x >= 0 else math.copysign(float("nan"), -1)

    def _wrap_float(fn, name):
        def f(x=None):
            x = float(check_num(x, 1, name))
            try:
                return fn(x)
            except ValueError:
                return math.copysign(float("nan"), -1)
            except OverflowError:
                return math.inf
        return f

    def _log(x=None, base=None):
        x = float(check_num(x, 1, "log"))
        try:
            if base is None:
                return math.log(x)
            base = float(check_num(base, 2, "log"))
            if base == 2.0:
                return math.log2(x)
            if base == 10.0:
                return math.log10(x)
            return math.log(x) / math.log(base)
        except ValueError:
            return -math.inf if x == 0 else math.copysign(float("nan"), -1)

    def _fmod(a=None, b=None):
        a = check_num(a, 1, "fmod")
        b = check_num(b, 2, "fmod")
        if isinstance(a, int) and isinstance(b, int):
            if b == 0:
                arg_error(2, "fmod", "zero")
            return int(math.fmod(a, b)) if abs(a) < 2 ** 53 and abs(b) < 2 ** 53 else a - b * int(a / b)
        try:
            return math.fmod(a, b)
        except ValueError:
            return math.copysign(float("nan"), -1)

    def _modf(x=None):
        x = check_num(x, 1, "modf")
        if isinstance(x, int):
            return MultiRes([x, 0.0])
        x = float(x)
        if math.isinf(x):
            return MultiRes([x, 0.0])
        fp, ip = math.modf(x)
        return MultiRes([float(ip), fp])

    def _tointeger(x=None):
        if isinstance(x, bool):
            return None
        if isinstance(x, int):
            return x
        if isinstance(x, float) and x.is_integer() and MININT <= x <= MAXINT:
            return int(x)
        if isinstance(x, str):
            n = str2number(x)
            return _tointeger(n) if n is not None else None
        return None

    def _mtype(*args):
        if not args:
            arg_error(1, "type", "value expected")
        x = args[0]
        if isinstance(x, bool):
            return None
        if isinstance(x, int):
            return "integer"
        if isinstance(x, float):
            return "float"
        return None

    # Generador xoshiro256** de lmathlib.c (Lua 5.4): con la misma semilla produce los mismos números
    _M64 = 0xFFFFFFFFFFFFFFFF
    _rstate = [0, 0, 0, 0]

    def _rotl(x, n):
        return ((x << n) | (x >> (64 - n))) & _M64

    def _nextrand():
        s0, s1, s2, s3 = _rstate
        res = (_rotl((s1 * 5) & _M64, 7) * 9) & _M64
        t = (s1 << 17) & _M64
        s2 ^= s0
        s3 ^= s1
        s1 ^= s2
        s0 ^= s3
        s2 ^= t
        s3 = _rotl(s3, 45)
        _rstate[:] = [s0, s1, s2, s3]
        return res

    def _setseed(n1, n2):
        _rstate[:] = [n1 & _M64, 0xFF, n2 & _M64, 0]
        for _ in range(16):
            _nextrand()

    _setseed(int(time.time()) ^ id(_rstate), id(interp))

    def _project(ran, n):
        if n & (n + 1) == 0:
            return ran & n
        lim = n
        for sh in (1, 2, 4, 8, 16, 32):
            lim |= lim >> sh
        ran &= lim
        while ran > n:
            ran = _nextrand() & lim
        return ran

    def _random_fn(*args):
        rv = _nextrand()
        if not args:
            return (rv >> 11) * (0.5 ** 53)
        if len(args) == 1:
            low = 1
            up = check_int(args[0], 1, "random")
            if up == 0:
                return wrap_int64(rv)
        elif len(args) == 2:
            low = check_int(args[0], 1, "random")
            up = check_int(args[1], 2, "random")
        else:
            raise interp.rt_error("wrong number of arguments")
        if low > up:
            arg_error(len(args), "random", "interval is empty")
        p = _project(rv, (up - low) & _M64)
        return wrap_int64(p + low)

    def _randomseed(*args):
        if not args:
            n1, n2 = int(time.time() * 1000) & _M64, id(args)
        else:
            n1 = check_int(args[0], 1, "randomseed") if not (isinstance(args[0], float) and not args[0].is_integer()) else int(args[0])
            n2 = check_int(args[1], 2, "randomseed", 0) if len(args) > 1 else 0
        _setseed(n1, n2)
        return MultiRes([wrap_int64(n1), wrap_int64(n2)])

    def _ult(a, b):
        return (a & 0xFFFFFFFFFFFFFFFF) < (b & 0xFFFFFFFFFFFFFFFF)

    for name, fn in (("floor", _floor), ("ceil", _ceil), ("abs", _abs), ("max", _max), ("min", _min),
                     ("sqrt", _sqrt), ("sin", _wrap_float(math.sin, "sin")), ("cos", _wrap_float(math.cos, "cos")),
                     ("tan", _wrap_float(math.tan, "tan")), ("asin", _wrap_float(math.asin, "asin")),
                     ("acos", _wrap_float(math.acos, "acos")), ("exp", _wrap_float(math.exp, "exp")),
                     ("atan", lambda y=None, x=1.0: math.atan2(float(check_num(y, 1, "atan")), float(check_num(x, 2, "atan", 1.0)))),
                     ("log", _log), ("fmod", _fmod), ("modf", _modf), ("tointeger", _tointeger), ("type", _mtype),
                     ("random", _random_fn), ("randomseed", _randomseed), ("ult", _ult),
                     ("deg", lambda x=None: float(check_num(x, 1, "deg")) * (180.0 / math.pi)),
                     ("rad", lambda x=None: float(check_num(x, 1, "rad")) * (math.pi / 180.0))):
        math_lib.rawset(name, fn)

    # ---- string ----
    string_lib = LuaTable()
    string_meta = LuaTable()
    string_meta.rawset("__index", string_lib)
    interp.string_lib = string_lib

    def posrelat_start(pos, length):
        if pos > 0:
            return pos
        if pos == 0:
            return 1
        if pos < -length:
            return 1
        return length + pos + 1

    def posrelat_end(pos, length):
        if pos > length:
            return length
        if pos >= 0:
            return pos
        if pos < -length:
            return 0
        return length + pos + 1

    def _s_len(s=None):
        return len(check_str(s, 1, "len"))

    def _s_sub(s=None, i=1, j=-1):
        s = check_str(s, 1, "sub")
        l = len(s)
        start = posrelat_start(check_int(i, 2, "sub", 1), l)
        end = posrelat_end(check_int(j, 3, "sub", -1), l)
        return s[start - 1:end] if start <= end else ""

    _UP = {i: i - 32 for i in range(ord("a"), ord("z") + 1)}
    _LOW = {i: i + 32 for i in range(ord("A"), ord("Z") + 1)}

    def _s_upper(s=None):
        return check_str(s, 1, "upper").translate(_UP)

    def _s_lower(s=None):
        return check_str(s, 1, "lower").translate(_LOW)

    def _s_rep(s=None, n=None, sep=""):
        s = check_str(s, 1, "rep")
        n = check_int(n, 2, "rep")
        sep = check_str(sep, 3, "rep", "")
        if n <= 0:
            return ""
        if (len(s) + len(sep)) * n > 1 << 31:
            raise interp.rt_error("resulting string too large")
        return sep.join([s] * n) if sep else s * n

    def _s_reverse(s=None):
        return check_str(s, 1, "reverse")[::-1]

    def _s_byte(s=None, i=1, j=None):
        s = check_str(s, 1, "byte")
        i = check_int(i, 2, "byte", 1)
        start = posrelat_start(i, len(s))
        end = posrelat_end(check_int(j, 3, "byte") if j is not None else start, len(s))
        if start > end:
            return MultiRes([])
        return MultiRes([ord(c) for c in s[start - 1:end]])

    def _s_char(*args):
        out = []
        for k, a in enumerate(args, start=1):
            c = check_int(a, k, "char")
            if not 0 <= c <= 255:
                arg_error(k, "char", "value out of range")
            out.append(chr(c))
        return "".join(out)

    def _hexfloat(v):
        """Equivalente a printf("%a") de C (sin ceros finales en la mantisa)."""
        if math.isnan(v):
            return "-nan" if math.copysign(1.0, v) < 0 else "nan"
        if math.isinf(v):
            return "inf" if v > 0 else "-inf"
        mant, exp = float.hex(v).split("p")
        if "." in mant:
            mant = mant.rstrip("0").rstrip(".")
        return mant + "p" + exp

    def _format_q(v):
        if isinstance(v, str):
            out = ['"']
            for k, c in enumerate(v):
                if c in '"\\':
                    out.append("\\" + c)
                elif c == "\n":
                    out.append("\\\n")
                elif c == "\r":
                    out.append("\\r")
                elif c == "\0":
                    nxt = v[k + 1] if k + 1 < len(v) else ""
                    out.append("\\000" if nxt.isdigit() else "\\0")
                elif ord(c) < 32 or ord(c) == 127:
                    nxt = v[k + 1] if k + 1 < len(v) else ""
                    out.append("\\%03d" % ord(c) if nxt.isdigit() else "\\%d" % ord(c))
                else:
                    out.append(c)
            out.append('"')
            return "".join(out)
        if isinstance(v, float):
            if math.isnan(v):
                return "(0/0)"
            if math.isinf(v):
                return "1e9999" if v > 0 else "-1e9999"
            return _hexfloat(v)
        if v == MININT:
            return "0x8000000000000000"
        if is_number(v) or v is None or isinstance(v, bool):
            return lua_tostring(v)
        arg_error(2, "format", "value has no literal form")

    _FMT_RE = re.compile(r"%([-+ #0]*)(\d*)(?:\.(\d*))?([a-zA-Z%])")

    def _s_format(fmt=None, *args):
        fmt = check_str(fmt, 1, "format")
        out = []
        pos = 0
        argi = 0
        n = len(fmt)
        while pos < n:
            k = fmt.find("%", pos)
            if k < 0:
                out.append(fmt[pos:])
                break
            out.append(fmt[pos:k])
            m = _FMT_RE.match(fmt, k)
            if not m:
                raise interp.rt_error(f"invalid conversion '{fmt[k:k + 2]}' to 'format'")
            flags, width, prec, conv = m.groups()
            pos = m.end()
            if conv == "%":
                out.append("%")
                continue
            if argi >= len(args):
                arg_error(argi + 2, "format", "no value")
            arg = args[argi]
            argi += 1
            spec = "%" + flags + width + ("." + prec if prec is not None else "")
            if conv in "di":
                v = arg
                if isinstance(v, str):
                    v = str2number(v)
                if isinstance(v, float):
                    if not v.is_integer():
                        arg_error(argi + 1, "format", "number has no integer representation")
                    v = int(v)
                if not isinstance(v, int) or isinstance(v, bool):
                    arg_error(argi + 1, "format", f"number expected, got {lua_type(arg)}")
                out.append((spec + "d") % v)
            elif conv in "uoxXc":
                v = arg
                if isinstance(v, str):
                    v = str2number(v)
                if isinstance(v, float) and v.is_integer():
                    v = int(v)
                if not isinstance(v, int) or isinstance(v, bool):
                    arg_error(argi + 1, "format", f"number expected, got {lua_type(arg)}")
                if conv == "c":
                    out.append((spec.replace(".", "") + "s") % chr(v & 0xFF))
                elif conv == "u":
                    out.append((spec + "d") % (v & 0xFFFFFFFFFFFFFFFF))
                else:
                    out.append((spec + conv) % (v & 0xFFFFFFFFFFFFFFFF if v < 0 else v))
            elif conv in "eEfFgG":
                v = arg
                if isinstance(v, str):
                    v = str2number(v)
                if not is_number(v):
                    arg_error(argi + 1, "format", f"number expected, got {lua_type(arg)}")
                v = float(v)
                if math.isinf(v) or math.isnan(v):
                    txt = "inf" if v > 0 else "-inf" if v < 0 else ("-nan" if math.copysign(1, v) < 0 else "nan")
                    if conv.isupper():
                        txt = txt.upper()
                    out.append(("%" + flags.replace("0", "") + width + "s") % txt)
                else:
                    out.append((spec + conv) % v)
            elif conv in "aA":
                v = float(check_num(arg, argi + 1, "format"))
                h = _hexfloat(v)
                out.append((("%" + flags.replace("0", "") + width + "s") % (h.upper() if conv == "A" else h)))
            elif conv == "s":
                out.append((spec + "s") % tostr(arg))
            elif conv == "q":
                out.append(_format_q(arg))
            elif conv == "p":
                out.append(("%" + flags + width + "s") % (f"0x{id(arg):012x}" if isinstance(arg, (LuaTable, LuaCoroutine)) or callable(arg) else "(null)"))
            else:
                raise interp.rt_error(f"invalid conversion '%{conv}' to 'format'")
        return "".join(out)

    def _find_aux(s, pat, init, plain, find, fname):
        s = check_str(s, 1, fname)
        pat = check_str(pat, 2, fname)
        ls = len(s)
        init = posrelat_start(check_int(init, 3, fname, 1), ls)
        if init > ls + 1:
            return None
        if find and ((plain is not None and plain is not False) or not lpattern.has_specials(pat)):
            idx = s.find(pat, init - 1)
            if idx < 0:
                return None
            return MultiRes([idx + 1, idx + len(pat)])
        ms = lpattern.MatchState(s, pat)
        anchor = pat.startswith("^")
        p = 1 if anchor else 0
        s1 = init - 1
        while True:
            ms.reprep()
            e = ms.match(s1, p)
            if e != -1:
                if find:
                    return MultiRes([s1 + 1, e] + ms.get_captures(s1, e, whole_if_none=False))
                caps = ms.get_captures(s1, e)
                return MultiRes(caps)
            s1 += 1
            if anchor or s1 > ls:
                break
        return None

    def _s_find(s=None, pat=None, init=None, plain=None):
        return _find_aux(s, pat, init, plain, True, "find")

    def _s_match(s=None, pat=None, init=None):
        return _find_aux(s, pat, init, None, False, "match")

    def _s_gmatch(s=None, pat=None, init=None):
        s = check_str(s, 1, "gmatch")
        pat = check_str(pat, 2, "gmatch")
        ls = len(s)
        start = posrelat_start(check_int(init, 3, "gmatch", 1), ls) - 1
        if start > ls:
            start = ls + 1
        state = {"src": start, "last": -1}
        ms = lpattern.MatchState(s, pat)

        def it(*_):
            while state["src"] <= ls:
                ms.reprep()
                e = ms.match(state["src"], 0)
                if e != -1 and e != state["last"]:
                    st = state["src"]
                    state["src"] = state["last"] = e
                    return MultiRes(ms.get_captures(st, e))
                state["src"] += 1
            return None

        return it

    def _s_gsub(s=None, pat=None, repl=None, max_n=None):
        s = check_str(s, 1, "gsub")
        pat = check_str(pat, 2, "gsub")
        if not (isinstance(repl, (str, LuaTable)) or is_number(repl) or callable(repl)):
            arg_error(3, "gsub", f"string/function/table expected, got {tname(repl, 3)}")
        ls = len(s)
        max_s = check_int(max_n, 4, "gsub") if max_n is not None else ls + 1
        anchor = pat.startswith("^")
        p = 1 if anchor else 0
        ms = lpattern.MatchState(s, pat)
        src = 0
        last = -1
        n = 0
        out = []
        if is_number(repl):
            repl = lua_tostring(repl)
        while n < max_s:
            ms.reprep()
            e = ms.match(src, p)
            if e != -1 and e != last:
                n += 1
                whole = s[src:e]
                if isinstance(repl, str):
                    i = 0
                    buf = []
                    while i < len(repl):
                        c = repl[i]
                        if c == "%":
                            i += 1
                            if i >= len(repl):
                                raise interp.rt_error("invalid use of '%' in replacement string")
                            d = repl[i]
                            if d == "%":
                                buf.append("%")
                            elif d.isdigit():
                                if d == "0":
                                    buf.append(whole)
                                else:
                                    v = ms.get_onecapture(int(d) - 1, src, e)
                                    buf.append(lua_tostring(v))
                            else:
                                raise interp.rt_error("invalid use of '%' in replacement string")
                        else:
                            buf.append(c)
                        i += 1
                    out.append("".join(buf))
                else:
                    cap0 = ms.get_onecapture(0, src, e)
                    if isinstance(repl, LuaTable):
                        v = interp._table_get(repl, cap0)
                    else:
                        v = unwrap_one(interp._call_callable(repl, ms.get_captures(src, e)))
                    if v is None or v is False:
                        out.append(whole)
                    elif isinstance(v, str) or is_number(v):
                        out.append(lua_tostring(v))
                    else:
                        raise interp.rt_error(f"invalid replacement value (a {lua_type(v)})")
                src = last = e
            elif src < ls:
                out.append(s[src])
                src += 1
            else:
                break
            if anchor:
                break
        out.append(s[src:])
        return MultiRes(["".join(out), n])

    # ---- string.pack / string.unpack / string.packsize (§6.4.2, como lstrlib.c) ----
    import struct as _struct
    _MAXINTSIZE = 16
    _NATIVE_ALIGN = 8

    class _PackState:
        def __init__(self, fmt, fname):
            self.fmt = fmt
            self.pos = 0
            self.little = True
            self.maxalign = 1
            self.fname = fname

        def getnum(self, default):
            fmt = self.fmt
            if self.pos >= len(fmt) or not fmt[self.pos].isdigit():
                return default
            a = 0
            while self.pos < len(fmt) and fmt[self.pos].isdigit() and a <= (2 ** 31 - 10) // 10:
                a = a * 10 + int(fmt[self.pos])
                self.pos += 1
            return a

        def getnumlimit(self, default):
            sz = self.getnum(default)
            if sz > _MAXINTSIZE or sz <= 0:
                raise interp.rt_error(f"integral size ({sz}) out of limits [1,{_MAXINTSIZE}]")
            return sz

        def getoption(self):
            """Devuelve (opción, tamaño). Opciones: int, uint, float, double, number, char,
            string, zstr, padding, paddalign, nop."""
            c = self.fmt[self.pos]
            self.pos += 1
            if c == "b":
                return "int", 1
            if c == "B":
                return "uint", 1
            if c == "h":
                return "int", 2
            if c == "H":
                return "uint", 2
            if c in "lj":
                return "int", 8
            if c in "LJT":
                return "uint", 8
            if c == "f":
                return "float", 4
            if c in "nd":
                return "double", 8
            if c == "i":
                return "int", self.getnumlimit(4)
            if c == "I":
                return "uint", self.getnumlimit(4)
            if c == "s":
                return "string", self.getnumlimit(8)
            if c == "c":
                sz = self.getnum(-1)
                if sz == -1:
                    raise interp.rt_error("missing size for format option 'c'")
                return "char", sz
            if c == "z":
                return "zstr", 0
            if c == "x":
                return "padding", 1
            if c == "X":
                return "paddalign", 0
            if c == " ":
                return "nop", 0
            if c in "<=":
                self.little = True
                return "nop", 0
            if c == ">":
                self.little = False
                return "nop", 0
            if c == "!":
                self.maxalign = self.getnumlimit(_NATIVE_ALIGN)
                return "nop", 0
            raise interp.rt_error(f"invalid format option '{c}'")

        def getdetails(self, totalsize):
            opt, size = self.getoption()
            align = size
            if opt == "paddalign":
                if self.pos >= len(self.fmt):
                    arg_error(1, self.fname, "invalid next option for option 'X'")
                opt2, align = self.getoption()
                if opt2 == "char" or align == 0:
                    arg_error(1, self.fname, "invalid next option for option 'X'")
            ntoalign = 0
            if align > 1 and opt in ("int", "uint", "float", "double", "paddalign"):
                align = min(align, self.maxalign)
                if align & (align - 1):
                    arg_error(1, self.fname, "format asks for alignment not power of 2")
                ntoalign = (align - (totalsize & (align - 1))) & (align - 1)
            return opt, size, ntoalign

    def _packint(n, little, size, neg):
        n &= (1 << (8 * size)) - 1 if size <= 8 else (1 << 64) - 1
        out = bytearray(size)
        for i in range(min(size, 8)):
            out[i] = n & 0xFF
            n >>= 8
        if neg and size > 8:
            for i in range(8, size):
                out[i] = 0xFF
        if not little:
            out.reverse()
        return out.decode("latin-1")

    def _s_pack(fmt=None, *args):
        fmt = check_str(fmt, 1, "pack")
        st = _PackState(fmt, "pack")
        out = []
        total = 0
        argi = 0
        while st.pos < len(fmt):
            opt, size, ntoalign = st.getdetails(total)
            total += ntoalign + size
            out.append("\0" * ntoalign)
            if opt in ("int", "uint"):
                argn = argi + 2
                v = check_int(args[argi] if argi < len(args) else None, argn, "pack")
                argi += 1
                if size < 8:
                    if opt == "int":
                        lim = 1 << (size * 8 - 1)
                        if not (-lim <= v < lim):
                            arg_error(argn, "pack", "integer overflow")
                    elif not (0 <= (v & 0xFFFFFFFFFFFFFFFF) < (1 << (size * 8))):
                        arg_error(argn, "pack", "unsigned overflow")
                out.append(_packint(v, st.little, size, v < 0))
            elif opt in ("float", "double"):
                v = float(check_num(args[argi] if argi < len(args) else None, argi + 2, "pack"))
                argi += 1
                code = ("<" if st.little else ">") + ("f" if opt == "float" else "d")
                try:
                    out.append(_struct.pack(code, v).decode("latin-1"))
                except OverflowError:
                    out.append(_struct.pack(code, math.copysign(math.inf, v)).decode("latin-1"))
            elif opt == "char":
                s = check_str(args[argi] if argi < len(args) else None, argi + 2, "pack")
                if len(s) > size:
                    arg_error(argi + 2, "pack", "string longer than given size")
                argi += 1
                out.append(s + "\0" * (size - len(s)))
            elif opt == "string":
                s = check_str(args[argi] if argi < len(args) else None, argi + 2, "pack")
                if size < 8 and len(s) >= (1 << (size * 8)):
                    arg_error(argi + 2, "pack", "string length does not fit in given size")
                argi += 1
                out.append(_packint(len(s), st.little, size, False))
                out.append(s)
                total += len(s)
            elif opt == "zstr":
                s = check_str(args[argi] if argi < len(args) else None, argi + 2, "pack")
                if "\0" in s:
                    arg_error(argi + 2, "pack", "string contains zeros")
                argi += 1
                out.append(s + "\0")
                total += len(s) + 1
            elif opt == "padding":
                out.append("\0")
        return "".join(out)

    def _s_packsize(fmt=None):
        fmt = check_str(fmt, 1, "packsize")
        st = _PackState(fmt, "packsize")
        total = 0
        while st.pos < len(fmt):
            opt, size, ntoalign = st.getdetails(total)
            if opt in ("string", "zstr"):
                arg_error(1, "packsize", "variable-length format")
            total += ntoalign + size
        return total

    def _unpackint(s, little, size, signed):
        b = s.encode("latin-1")
        if not little:
            b = b[::-1]
        res = 0
        for i in range(min(size, 8) - 1, -1, -1):
            res = (res << 8) | b[i]
        if size < 8:
            if signed:
                mask = 1 << (size * 8 - 1)
                res = (res ^ mask) - mask
        elif size > 8:
            mask = 0xFF if (signed and res >> 63) else 0
            for i in range(8, size):
                if b[i] != mask:
                    raise interp.rt_error(f"{size}-byte integer does not fit into Lua Integer")
        return wrap_int64(res)

    def _s_unpack(fmt=None, data=None, init=None):
        fmt = check_str(fmt, 1, "unpack")
        data = check_str(data, 2, "unpack")
        ld = len(data)
        pos = posrelat_start(check_int(init, 3, "unpack", 1), ld) - 1
        if not (0 <= pos <= ld):
            arg_error(3, "unpack", "initial position out of string")
        st = _PackState(fmt, "unpack")
        out = []
        while st.pos < len(fmt):
            opt, size, ntoalign = st.getdetails(pos)
            if ntoalign + size > ld - pos:
                arg_error(2, "unpack", "data string too short")
            pos += ntoalign
            if opt in ("int", "uint"):
                out.append(_unpackint(data[pos:pos + size], st.little, size, opt == "int"))
            elif opt in ("float", "double"):
                code = ("<" if st.little else ">") + ("f" if opt == "float" else "d")
                out.append(_struct.unpack(code, data[pos:pos + size].encode("latin-1"))[0])
            elif opt == "char":
                out.append(data[pos:pos + size])
            elif opt == "string":
                ln = _unpackint(data[pos:pos + size], st.little, size, False)
                if ln < 0 or ln > ld - pos - size:
                    arg_error(2, "unpack", "data string too short")
                out.append(data[pos + size:pos + size + ln])
                pos += ln
            elif opt == "zstr":
                end = data.find("\0", pos)
                if end < 0:
                    arg_error(2, "unpack", "unfinished string for format 'z'")
                out.append(data[pos:end])
                pos = end + 1 - size
            pos += size
        out.append(pos + 1)
        return MultiRes(out)

    for name, fn in (("len", _s_len), ("sub", _s_sub), ("upper", _s_upper), ("lower", _s_lower), ("rep", _s_rep),
                     ("reverse", _s_reverse), ("byte", _s_byte), ("char", _s_char), ("format", _s_format),
                     ("find", _s_find), ("match", _s_match), ("gmatch", _s_gmatch), ("gsub", _s_gsub),
                     ("pack", _s_pack), ("unpack", _s_unpack), ("packsize", _s_packsize)):
        string_lib.rawset(name, fn)

    # ---- os ----
    os_lib = LuaTable()

    def _os_time(t=None):
        if t is None:
            return int(time.time())
        check_table(t, 1, "time")

        def field(name, default=None):
            v = t.rawget(name)
            if v is None:
                if default is None:
                    raise interp.rt_error(f"field '{name}' missing in date table")
                return default
            return check_int(v, 1, "time")

        tup = (field("year"), field("month"), field("day"), field("hour", 12), field("min", 0), field("sec", 0), 0, 0, -1)
        return int(time.mktime(tup))

    def _os_date(fmt="%c", t=None):
        fmt = check_str(fmt, 1, "date", "%c")
        t = time.time() if t is None else check_num(t, 2, "date")
        utc = fmt.startswith("!")
        if utc:
            fmt = fmt[1:]
        st = time.gmtime(t) if utc else time.localtime(t)
        if fmt.startswith("*t"):
            res = LuaTable()
            for k, v in (("year", st.tm_year), ("month", st.tm_mon), ("day", st.tm_mday), ("hour", st.tm_hour),
                         ("min", st.tm_min), ("sec", st.tm_sec), ("wday", (st.tm_wday + 1) % 7 + 1),
                         ("yday", st.tm_yday), ("isdst", bool(st.tm_isdst > 0))):
                res.rawset(k, v)
            return res
        return time.strftime(fmt, st)

    def _os_exit(code=None, close=None):
        sys.stdout.flush()
        sys.stderr.flush()
        if code is None or code is True:
            rc = 0
        elif code is False:
            rc = 1
        else:
            rc = int(code)
        os._exit(rc)

    os_lib.rawset("time", _os_time)
    os_lib.rawset("clock", lambda: time.process_time())
    os_lib.rawset("date", _os_date)
    os_lib.rawset("getenv", lambda name=None: os.environ.get(str(name)))
    os_lib.rawset("exit", _os_exit)
    os_lib.rawset("difftime", lambda a, b=0: float(a - b))

    # ---- io ----
    io_lib = LuaTable()
    stdin_f = LuaFile("stdin", interp)
    stdout_f = LuaFile("stdout", interp)
    stderr_f = LuaFile("stderr", interp)
    for f in (stdin_f, stdout_f, stderr_f):
        f.methods = {
            "write": lambda self, *a: self.write(*a),
            "read": lambda self, *a: self.read(*a),
            "close": lambda self, *a: True,
            "flush": lambda self, *a: self,
            "setvbuf": lambda self, *a: True,
            "lines": lambda self, *a: (lambda *_: self.read_one("l")),
        }
    io_lib.rawset("stdin", stdin_f)
    io_lib.rawset("stdout", stdout_f)
    io_lib.rawset("stderr", stderr_f)
    io_lib.rawset("write", lambda *args: stdout_f.write(*args))
    io_lib.rawset("read", lambda *fmts: stdin_f.read(*fmts))
    io_lib.rawset("lines", lambda *a: (lambda *_: stdin_f.read_one("l")))

    # ---- debug (mínimo) ----
    debug_lib = LuaTable()

    def _traceback(msg=None, *rest):
        if msg is not None and not isinstance(msg, str) and not is_number(msg):
            return msg
        text = "" if msg is None else lua_tostring(msg) + "\n"
        return text + "stack traceback:\n\t[C]: in ?"

    def _getinfo(*args):
        info = LuaTable()
        info.rawset("currentline", interp.cur_line if interp.cur_line is not None else -1)
        info.rawset("short_src", interp.chunkname)
        info.rawset("source", "@" + interp.chunkname)
        info.rawset("what", "Lua")
        return info

    debug_lib.rawset("traceback", _traceback)
    debug_lib.rawset("getinfo", _getinfo)
    debug_lib.rawset("sethook", lambda *a: None)
    debug_lib.rawset("gethook", lambda *a: None)
    debug_lib.rawset("getmetatable", lambda v=None: v.metatable if isinstance(v, LuaTable) else (string_meta if isinstance(v, str) else None))
    debug_lib.rawset("setmetatable", lambda v=None, mt=None: (setattr(v, "metatable", mt), v)[1] if isinstance(v, LuaTable) else v)

    # ---- utf8 (mínimo) ----
    utf8_lib = LuaTable()

    def _utf8_char(*cps):
        return "".join(interp._utf8_encode(check_int(c, i, "char")) for i, c in enumerate(cps, start=1))

    def _utf8_decode(s, i):
        """Decodifica un carácter UTF-8 en s[i] (índice base 0). Devuelve (codepoint, longitud) o None."""
        c = ord(s[i])
        if c < 0x80:
            return c, 1
        if c < 0xC0:
            return None
        n = 2 if c < 0xE0 else 3 if c < 0xF0 else 4 if c < 0xF8 else 5 if c < 0xFC else 6
        if i + n > len(s):
            return None
        cp = c & (0x7F >> n)
        for k in range(1, n):
            cc = ord(s[i + k])
            if cc & 0xC0 != 0x80:
                return None
            cp = (cp << 6) | (cc & 0x3F)
        return cp, n

    def _utf8_len(s=None, i=1, j=-1):
        s = check_str(s, 1, "len")
        start = posrelat_start(check_int(i, 2, "len", 1), len(s)) - 1
        end = posrelat_end(check_int(j, 3, "len", -1), len(s))
        count = 0
        while start < end:
            dec = _utf8_decode(s, start)
            if dec is None:
                return MultiRes([None, start + 1])
            start += dec[1]
            count += 1
        return count

    def _utf8_codepoint(s=None, i=1, j=None):
        s = check_str(s, 1, "codepoint")
        start = posrelat_start(check_int(i, 2, "codepoint", 1), len(s)) - 1
        end = posrelat_end(check_int(j, 3, "codepoint") if j is not None else start + 1, len(s))
        out = []
        while start < end:
            dec = _utf8_decode(s, start)
            if dec is None:
                raise interp.rt_error("invalid UTF-8 code")
            out.append(dec[0])
            start += dec[1]
        return MultiRes(out)

    def _iscont(s, i):
        return i < len(s) and (ord(s[i]) & 0xC0) == 0x80

    def _utf8_codes(s=None, lax=None):
        s = check_str(s, 1, "codes")
        if _iscont(s, 0):
            arg_error(1, "codes", "invalid UTF-8 code")

        def _codes_iter(_s=None, ctrl=0):
            n = ctrl if isinstance(ctrl, int) else 0
            ls = len(s)
            if 0 <= n < ls:
                while _iscont(s, n):
                    n += 1
            if n >= ls or n < 0:
                return None
            dec = _utf8_decode(s, n)
            if dec is None or _iscont(s, n + dec[1]):
                raise interp.rt_error("invalid UTF-8 code")
            return MultiRes([n + 1, dec[0]])

        return MultiRes([_codes_iter, s, 0])

    def _utf8_offset(s=None, n=None, i=None):
        s = check_str(s, 1, "offset")
        n = check_int(n, 2, "offset")
        ls = len(s)
        posi = check_int(i, 3, "offset") if i is not None else (1 if n >= 0 else ls + 1)
        if posi < 0:
            posi = 0 if -posi > ls else ls + posi + 1
        if not (1 <= posi and posi - 1 <= ls):
            arg_error(3, "offset", "position out of bounds")
        posi -= 1
        if n == 0:
            while posi > 0 and _iscont(s, posi):
                posi -= 1
            return posi + 1
        if _iscont(s, posi):
            raise interp.rt_error("initial position is a continuation byte")
        if n < 0:
            while n < 0 and posi > 0:
                posi -= 1
                while posi > 0 and _iscont(s, posi):
                    posi -= 1
                n += 1
        else:
            n -= 1
            while n > 0 and posi < ls:
                posi += 1
                while _iscont(s, posi):
                    posi += 1
                n -= 1
        return posi + 1 if n == 0 else None

    utf8_lib.rawset("char", _utf8_char)
    utf8_lib.rawset("len", _utf8_len)
    utf8_lib.rawset("codepoint", _utf8_codepoint)
    utf8_lib.rawset("codes", _utf8_codes)
    utf8_lib.rawset("offset", _utf8_offset)
    utf8_lib.rawset("charpattern", "[\x00-\x7F\xC2-\xFD][\x80-\xBF]*")

    # ---- registro en _G ----
    env.rawset("print", _print)
    env.rawset("type", _type)
    env.rawset("tostring", lambda v=None: lua_tostring(v, interp))
    env.rawset("tonumber", _tonumber)
    env.rawset("error", _error)
    env.rawset("pcall", _pcall)
    env.rawset("xpcall", _xpcall)
    env.rawset("load", _load)
    env.rawset("setmetatable", _setmetatable)
    env.rawset("getmetatable", _getmetatable)
    env.rawset("rawset", _rawset)
    env.rawset("rawget", _rawget)
    env.rawset("rawequal", _rawequal)
    env.rawset("rawlen", _rawlen)
    env.rawset("ipairs", _ipairs)
    env.rawset("pairs", _pairs)
    env.rawset("next", _next)
    env.rawset("select", _select)
    env.rawset("assert", _assert)
    env.rawset("table", table_lib)
    env.rawset("coroutine", coro_lib)
    env.rawset("math", math_lib)
    env.rawset("string", string_lib)
    env.rawset("os", os_lib)
    env.rawset("debug", debug_lib)
    env.rawset("utf8", utf8_lib)
    env.rawset("io", io_lib)
    env.rawset("collectgarbage", _collectgarbage)

    return env
