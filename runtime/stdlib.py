import gc
import sys
import math
import threading
from antlr4 import InputStream, CommonTokenStream
from grammar.LuaLexer import LuaLexer
from grammar.LuaParser import LuaParser
from runtime.values import LuaTable, MultiRes, unwrap_one
from runtime.environment import Environment
from runtime.exceptions import LuaError

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
    if isinstance(val, LuaTable) and interp is not None:
        mm = interp._get_metamethod(val, "__tostring")
        if mm is not None:
            return str(unwrap_one(interp._call_callable(mm, [val])))
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float):
        if math.isnan(val):
            return "-nan"
        if val.is_integer():
            return f"{val:.1f}"
        return str(val)
    if isinstance(val, LuaTable):
        return f"table: {hex(id(val))}"
    if isinstance(val, LuaCoroutine):
        return f"thread: {hex(id(val))}"
    if callable(val):
        return f"function: {hex(id(val))}"
    return str(val)

class LuaCoroutine:
    _active_stack = []

    def __init__(self, fn, interp):
        self.fn = fn
        self.interp = interp
        self.status = "suspended"
        self.cond = threading.Condition()
        self.transfer_vals = []
        self.error_obj = None
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
                self.error_obj = e.lua_obj
                self.cond.notify_all()
        except Exception as e:
            with self.cond:
                self.status = "dead"
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

            if self.error_obj is not None:
                return MultiRes([False, self.error_obj])
            return MultiRes([True] + list(self.transfer_vals))

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

def build_global_env(interp):
    env = LuaTable()
    env.rawset("_G", env)
    env.rawset("_ENV", env)

    def _print(*args):
        print("\t".join(lua_tostring(a, interp) for a in args))

    def _error(msg=None, level=1):
        raise LuaError(msg)

    def _pcall(fn, *args):
        try:
            res = interp._call_callable(fn, list(args))
            if isinstance(res, MultiRes):
                return MultiRes([True] + list(res))
            return MultiRes([True, res])
        except LuaError as e:
            return MultiRes([False, e.lua_obj])
        except Exception as e:
            return MultiRes([False, str(e)])

    def _xpcall(fn, msgh, *args):
        try:
            res = interp._call_callable(fn, list(args))
            if isinstance(res, MultiRes):
                return MultiRes([True] + list(res))
            return MultiRes([True, res])
        except LuaError as e:
            handled = unwrap_one(interp._call_callable(msgh, [e.lua_obj]))
            return MultiRes([False, handled])
        except Exception as e:
            handled = unwrap_one(interp._call_callable(msgh, [str(e)]))
            return MultiRes([False, handled])

    def _load(chunk_str, chunkname="=(load)", mode="bt", custom_env=None):
        from interpreter import LuaFunction
        input_stream = InputStream(str(chunk_str))
        lexer = LuaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = LuaParser(token_stream)
        tree = parser.chunk()
        if parser.getNumberOfSyntaxErrors() > 0:
            return MultiRes([None, "syntax error in loaded chunk"])
        target_env_tbl = custom_env if custom_env is not None else env
        chunk_env = Environment(parent=None, env_table=target_env_tbl)
        return LuaFunction([], True, tree.block(), chunk_env, interp)

    def _setmetatable(t, mt):
        if not isinstance(t, LuaTable):
            raise LuaError("bad argument #1 to 'setmetatable' (table expected)")
        t.metatable = mt
        return t

    def _getmetatable(obj):
        if isinstance(obj, LuaTable):
            return obj.metatable
        return None

    def _rawset(t, k, v):
        t.rawset(k, v)
        return t

    def _rawget(t, k):
        return t.rawget(k)

    def _ipairs_iter(t, i):
        i = i + 1
        v = interp._table_get(t, i)
        if v is None:
            return None
        return MultiRes([i, v])

    def _ipairs(t):
        return MultiRes([_ipairs_iter, t, 0])

    def _next(t, k=None):
        keys = t.keys()
        if not keys:
            return None
        if k is None:
            first_k = keys[0]
            return MultiRes([first_k, t.rawget(first_k)])
        for idx, curr_k in enumerate(keys):
            if curr_k == k or curr_k is k:
                if idx + 1 < len(keys):
                    nk = keys[idx + 1]
                    return MultiRes([nk, t.rawget(nk)])
                return None
        return None

    def _pairs(t):
        return MultiRes([_next, t, None])

    # Librería table
    table_lib = LuaTable()
    def _table_pack(*args):
        res = LuaTable()
        for idx, val in enumerate(args, start=1):
            res.rawset(idx, val)
        res.rawset("n", len(args))
        return res

    def _table_unpack(t, i=1, j=None):
        if j is None:
            j = interp._table_len(t)
        return MultiRes([interp._table_get(t, idx) for idx in range(int(i), int(j) + 1)])

    table_lib.rawset("pack", _table_pack)
    table_lib.rawset("unpack", _table_unpack)

    # Librería coroutine
    coro_lib = LuaTable()
    coro_lib.rawset("create", lambda fn: LuaCoroutine(fn, interp))
    coro_lib.rawset("resume", lambda co, *args: co.resume(*args))
    coro_lib.rawset("yield", lambda *args: LuaCoroutine.yield_current(*args))
    coro_lib.rawset("status", lambda co: co.status)

    # Librería math e io básicas
    math_lib = LuaTable()
    math_lib.rawset("pi", math.pi)
    math_lib.rawset("floor", lambda x: math.floor(x))

    io_lib = LuaTable()
    class _Userdata:
        _is_userdata = True
    io_lib.rawset("stdin", _Userdata())
    io_lib.rawset("write", lambda *args: sys.stdout.write("".join(lua_tostring(a, interp) for a in args)))

    env.rawset("print", _print)
    env.rawset("type", lua_type)
    env.rawset("tostring", lambda v: lua_tostring(v, interp))
    env.rawset("error", _error)
    env.rawset("pcall", _pcall)
    env.rawset("xpcall", _xpcall)
    env.rawset("load", _load)
    env.rawset("setmetatable", _setmetatable)
    env.rawset("getmetatable", _getmetatable)
    env.rawset("rawset", _rawset)
    env.rawset("rawget", _rawget)
    env.rawset("ipairs", _ipairs)
    env.rawset("pairs", _pairs)
    env.rawset("next", _next)
    env.rawset("table", table_lib)
    env.rawset("coroutine", coro_lib)
    env.rawset("math", math_lib)
    env.rawset("io", io_lib)
    env.rawset("collectgarbage", lambda *args: gc.collect())

    return env