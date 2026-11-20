import re
import math
from grammar.LuaParserVisitor import LuaParserVisitor
from runtime.values import LuaTable, MultiRes, unwrap_one, expand_args
from runtime.environment import Environment
from runtime.exceptions import LuaReturn, LuaBreak, LuaGoto, LuaError
from runtime.stdlib import (build_global_env, lua_tostring, lua_type, str2number,
                            wrap_int64, is_number, LuaFile, MAXINT, MININT)

class LuaFunction:
    __slots__ = ("params", "is_vararg", "block_ctx", "closure_env", "interp", "chunkname", "__weakref__")

    def __init__(self, params, is_vararg, block_ctx, closure_env, interp, chunkname=None):
        self.params = params
        self.is_vararg = is_vararg
        self.block_ctx = block_ctx
        self.closure_env = closure_env
        self.interp = interp
        self.chunkname = chunkname if chunkname is not None else interp.chunkname

    def __call__(self, *args):
        return self.call(args)

    def call(self, args):
        """Invoca la función Lua (se usa en vez de __call__ para no consumir recursión de C)."""
        interp = self.interp
        fn_env = Environment(parent=self.closure_env, env_table=self.closure_env.env_table)
        fn_env.is_func = True
        params = self.params
        nargs = len(args)
        vars_ = fn_env.vars
        for i, p_name in enumerate(params):
            vars_[p_name] = args[i] if i < nargs else None
        if self.is_vararg:
            vars_["..."] = MultiRes(args[len(params):])

        prev_env = interp.current_env
        prev_line = interp.cur_line
        prev_chunk = interp.chunkname
        interp.chunkname = self.chunkname
        interp.call_lines.append(prev_line)
        interp.current_env = fn_env
        err = None
        try:
            interp.visitBlock(self.block_ctx, create_scope=False)
            return MultiRes()
        except LuaReturn as ret:
            vals = ret.values
            if len(vals) == 1:
                return vals[0]
            return MultiRes(vals)
        except LuaError as e:
            err = e.lua_obj
            raise
        finally:
            try:
                if fn_env.to_close:
                    fn_env.close_scope(interp._call_metamethod, err)
            finally:
                interp.current_env = prev_env
                if interp.call_lines:
                    interp.call_lines.pop()
                interp.cur_line = prev_line
                interp.chunkname = prev_chunk

class LuaInterpreter(LuaParserVisitor):
    def __init__(self):
        self.global_table = build_global_env(self)
        self.current_env = Environment(parent=None, env_table=self.global_table)
        self.current_env.vars["..."] = MultiRes([])
        self.chunkname = "input"
        self.cur_line = 0
        self.call_lines = []

    def rt_error(self, msg, level=1):
        """Crea un LuaError con prefijo 'chunk:línea:' como lo hace Lua para errores de ejecución."""
        line = self.cur_line
        if level >= 2:
            idx = len(self.call_lines) - (level - 1)
            line = self.call_lines[idx] if 0 <= idx < len(self.call_lines) else None
        if line is None or level <= 0:
            return LuaError(msg)
        return LuaError(f"{self.chunkname}:{line}: {msg}")

    # --- Helpers de semántica Lua ---
    def _is_truthy(self, val):
        return val is not None and val is not False

    def _to_number(self, val):
        if isinstance(val, bool):
            return None
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            return str2number(val)
        return None

    def _to_int64(self, val, ctx=None):
        if isinstance(val, int) and not isinstance(val, bool):
            return wrap_int64(val)
        if isinstance(val, float) and not math.isnan(val) and not math.isinf(val) and val.is_integer():
            return wrap_int64(int(val))
        if isinstance(val, float):
            raise self.rt_error("number has no integer representation")
        suffix = self._desc_suffix(self._exp_desc(ctx)) if ctx is not None else ""
        raise self.rt_error(f"attempt to perform bitwise operation on a {lua_type(val)} value{suffix}")

    def _wrap_int64(self, n):
        return wrap_int64(n)

    def _get_metamethod(self, obj, event):
        if isinstance(obj, LuaTable) and isinstance(obj.metatable, LuaTable):
            return obj.metatable.rawget(event)
        return None

    def _call_metamethod(self, obj, event, args):
        mm = self._get_metamethod(obj, event)
        if mm is not None:
            return self._call_callable(mm, args)
        return None

    def _call_callable(self, fn, args, desc=None):
        if type(fn) is LuaFunction:
            return fn.call(args)
        if callable(fn):
            return fn(*args)
        if isinstance(fn, LuaTable):
            mm = self._get_metamethod(fn, "__call")
            if mm is not None:
                return self._call_callable(mm, [fn] + args)
        raise self.rt_error(f"attempt to call a {lua_type(fn)} value{self._desc_suffix(desc)}")

    def _table_get(self, t, key, depth=0):
        if depth > 2000:
            raise self.rt_error("'__index' chain too long; possible loop")
        if isinstance(t, LuaTable):
            val = t.rawget(key)
            if val is not None:
                return val
            mm = self._get_metamethod(t, "__index")
            if mm is None:
                return None
            if callable(mm):
                return unwrap_one(self._call_callable(mm, [t, key]))
            return self._table_get(mm, key, depth + 1)
        if isinstance(t, str):
            return self.string_lib.rawget(key)
        if isinstance(t, LuaFile):
            return t.methods.get(key) if isinstance(key, str) else None
        raise self.rt_error(f"attempt to index a {lua_type(t)} value")

    def _table_set(self, t, key, val, depth=0):
        if depth > 2000:
            raise self.rt_error("'__newindex' chain too long; possible loop")
        if isinstance(t, LuaTable):
            if key is None:
                raise self.rt_error("table index is nil")
            if key.__class__ is float and key != key:
                raise self.rt_error("table index is NaN")
            existing = t.rawget(key)
            if existing is None:
                mm = self._get_metamethod(t, "__newindex")
                if mm is not None:
                    if callable(mm):
                        self._call_callable(mm, [t, key, val])
                        return
                    self._table_set(mm, key, val, depth + 1)
                    return
            t.rawset(key, val)
            return
        raise self.rt_error(f"attempt to index a {lua_type(t)} value")

    def _table_len(self, obj, desc=None):
        if isinstance(obj, str):
            return len(obj)
        if isinstance(obj, LuaTable):
            mm = self._get_metamethod(obj, "__len")
            if mm is not None:
                return unwrap_one(self._call_callable(mm, [obj]))
            return obj.length()
        raise self.rt_error(f"attempt to get length of a {lua_type(obj)} value{self._desc_suffix(desc)}")

    # --- Parseo de literales ---
    def _parse_number(self, text):
        val = str2number(text)
        return 0 if val is None else val

    @staticmethod
    def _utf8_encode(cp):
        """Codifica un punto de código (hasta 2^31) en bytes UTF-8 (como str latin-1)."""
        if cp < 0x80:
            return chr(cp)
        limits = [(0x800, 2), (0x10000, 3), (0x200000, 4), (0x4000000, 5), (0x80000000, 6)]
        for limit, n in limits:
            if cp < limit:
                break
        else:
            raise LuaError("UTF-8 value too large")
        out = []
        for _ in range(n - 1):
            out.append(0x80 | (cp & 0x3F))
            cp >>= 6
        first_mask = (0xFF << (8 - n)) & 0xFF
        out.append(first_mask | cp)
        return "".join(chr(b) for b in reversed(out))

    def _parse_string(self, text):
        if text.startswith("["):
            match = re.match(r"^\[(=*)\[(.*)\]\1\]$", text, re.DOTALL)
            body = match.group(2) if match else text
            body = body.replace("\r\n", "\n").replace("\n\r", "\n").replace("\r", "\n")
            return body[1:] if body.startswith("\n") else body
        inner = text[1:-1]
        out = []
        i = 0
        n = len(inner)
        escapes = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v",
                   "\\": "\\", '"': '"', "'": "'"}
        while i < n:
            ch = inner[i]
            if ch != "\\":
                out.append(ch)
                i += 1
                continue
            i += 1
            if i >= n:
                break
            esc = inner[i]
            if esc in escapes:
                out.append(escapes[esc])
                i += 1
            elif esc == "\n" or esc == "\r":
                out.append("\n")
                i += 1
                if i < n and inner[i] in "\r\n" and inner[i] != esc:
                    i += 1
            elif esc == "z":
                i += 1
                while i < n and inner[i] in " \t\r\n\f\v":
                    i += 1
            elif esc == "x":
                out.append(chr(int(inner[i + 1:i + 3], 16)))
                i += 3
            elif esc == "u":
                end_brace = inner.index("}", i + 2)
                out.append(self._utf8_encode(int(inner[i + 2:end_brace], 16)))
                i = end_brace + 1
            elif esc.isdigit():
                j = i
                while j < n and j < i + 3 and inner[j].isdigit():
                    j += 1
                out.append(chr(int(inner[i:j]) & 0xFF))
                i = j
            else:
                out.append(esc)
                i += 1
        return "".join(out)

    # --- Reglas de bloques y sentencias ---
    def visitChunk(self, ctx):
        try:
            self.visitBlock(ctx.block(), create_scope=False)
        except LuaReturn as ret:
            return MultiRes(ret.values) if len(ret.values) > 1 else (ret.values[0] if ret.values else None)
        return None

    def visitBlock(self, ctx, create_scope=True):
        if create_scope:
            self.current_env = Environment(parent=self.current_env, env_table=self.current_env.env_table)

        info = ctx.__dict__.get("_binfo")
        if info is None:
            stats = ctx.stat()
            labels = {}
            for idx, st in enumerate(stats):
                if st.label():
                    labels[st.label().NAME().getText()] = idx
            info = ctx._binfo = (stats, labels, ctx.retstat())
        stats, labels, retstat = info

        idx = 0
        nstats = len(stats)
        caught_err = None
        try:
            while idx < nstats:
                try:
                    while idx < nstats:
                        self.visitStat(stats[idx])
                        idx += 1
                except LuaGoto as g:
                    if g.label in labels:
                        idx = labels[g.label] + 1
                    else:
                        raise
            if retstat is not None:
                self.visitRetstat(retstat)
        except LuaError as e:
            caught_err = e.lua_obj
            raise
        finally:
            if create_scope:
                closing_env = self.current_env
                self.current_env = closing_env.parent
                if closing_env.to_close:
                    closing_env.close_scope(self._call_metamethod, caught_err)

    def visitRetstat(self, ctx):
        self.cur_line = ctx.start.line
        exps = ctx.__dict__.get("_exps")
        if exps is None:
            exps = ctx._exps = ctx.explist().exp() if ctx.explist() else []
        if len(exps) == 1:
            val = self.visit(exps[0])
            raise LuaReturn(list(val) if isinstance(val, MultiRes) else [val])
        raise LuaReturn(expand_args([self.visit(e) for e in exps]))

    def _resolve_lvalue(self, var_ctx):
        children = list(var_ctx.children)
        if len(children) == 1:
            return ("var", children[0].getText())
        if children[-1].getChildCount() == 0 and children[-1].getText() == "]":
            target, desc = self._eval_chain(children[:-3])
            key = unwrap_one(self.visit(children[-2]))
            return ("table", unwrap_one(target), key, desc)
        # Caso prefix '.' NAME
        target, desc = self._eval_chain(children[:-2])
        key = children[-1].getText()
        return ("table", unwrap_one(target), key, desc)

    def _stat_info(self, ctx):
        """Clasifica una sentencia una sola vez y guarda sus sub-contextos (el árbol es inmutable)."""
        if ctx.varlist():
            return ("assign", ctx.varlist().var(), ctx.explist().exp())
        if ctx.functioncall():
            return ("call", ctx.functioncall())
        child0 = ctx.getChild(0)
        first = child0.getText() if child0.getChildCount() == 0 else ""
        if first == "break":
            return ("break",)
        if first == "goto":
            return ("goto", ctx.NAME().getText())
        if first == "do":
            return ("do", ctx.block(0))
        if first == "while":
            return ("while", ctx.exp(0), ctx.block(0))
        if first == "repeat":
            return ("repeat", ctx.block(0), ctx.exp(0))
        if first == "if":
            return ("if", ctx.exp(), ctx.block())
        if first == "for":
            if ctx.namelist() is None:
                return ("fornum", ctx.NAME().getText(), ctx.exp(), ctx.block(0))
            return ("forgen", [n.getText() for n in ctx.namelist().NAME()], ctx.explist().exp(), ctx.block(0))
        if first == "function":
            fn_ctx = ctx.funcname()
            names = [n.getText() for n in fn_ctx.NAME()]
            return ("function", names, ":" in fn_ctx.getText(), ctx.funcbody())
        if first == "local":
            if ctx.funcbody() is not None:
                return ("localfunc", ctx.NAME().getText(), ctx.funcbody())
            att_items = []
            attlist = ctx.attnamelist()
            for i, name_node in enumerate(attlist.NAME()):
                attrib_node = attlist.attrib(i)
                attr = attrib_node.NAME().getText() if attrib_node and attrib_node.NAME() else None
                att_items.append((name_node.getText(), attr))
            exps = ctx.explist().exp() if ctx.explist() else []
            return ("local", att_items, exps)
        return ("nop",)

    def visitStat(self, ctx):
        self.cur_line = ctx.start.line
        k = ctx.__dict__.get("_k")
        if k is None:
            k = ctx._k = self._stat_info(ctx)
        kind = k[0]

        if kind == "assign":
            lvars, exps = k[1], k[2]
            if len(lvars) == 1 and len(exps) == 1:
                # caso frecuente: una variable = una expresión
                lv = self._resolve_lvalue(lvars[0])
                val = unwrap_one(self.visit(exps[0]))
                rvalues = None
                lvalues = (lv,)
                rvalues = (val,)
            else:
                lvalues = [self._resolve_lvalue(v) for v in lvars]
                rvalues = expand_args([self.visit(e) for e in exps])
            nr = len(rvalues)
            for idx, lv in enumerate(lvalues):
                val = rvalues[idx] if idx < nr else None
                if lv[0] == "var":
                    self.current_env.assign(lv[1], val, self._table_set)
                else:
                    if not isinstance(lv[1], LuaTable):
                        raise self.rt_error(f"attempt to index a {lua_type(lv[1])} value{self._desc_suffix(lv[3])}")
                    self._table_set(lv[1], lv[2], val)
            return None

        if kind == "call":
            self.visit(k[1])
            return None

        if kind == "local":
            att_items, exps = k[1], k[2]
            if len(att_items) == 1 and len(exps) == 1:
                vname, attr = att_items[0]
                self.current_env.define_local(vname, unwrap_one(self.visit(exps[0])), attrib=attr)
                return None
            rvalues = expand_args([self.visit(e) for e in exps]) if exps else []
            nr = len(rvalues)
            for idx, (vname, attr) in enumerate(att_items):
                self.current_env.define_local(vname, rvalues[idx] if idx < nr else None, attrib=attr)
            return None

        if kind == "if":
            exps, blocks = k[1], k[2]
            for i, cond_exp in enumerate(exps):
                v = self.visit(cond_exp)
                if v.__class__ is MultiRes:
                    v = unwrap_one(v)
                if v is not None and v is not False:
                    self.visitBlock(blocks[i], create_scope=True)
                    return None
            if len(blocks) > len(exps):
                self.visitBlock(blocks[-1], create_scope=True)
            return None

        if kind == "nop":
            return None

        if kind == "break":
            raise LuaBreak()

        if kind == "goto":
            raise LuaGoto(k[1])

        if kind == "do":
            self.visitBlock(k[1], create_scope=True)
            return None

        if kind == "while":
            cond_ctx, body = k[1], k[2]
            while self._is_truthy(unwrap_one(self.visit(cond_ctx))):
                try:
                    self.visitBlock(body, create_scope=True)
                except LuaBreak:
                    break
            return None

        if kind == "repeat":
            body, cond_ctx = k[1], k[2]
            while True:
                loop_env = Environment(parent=self.current_env, env_table=self.current_env.env_table)
                self.current_env = loop_env
                try:
                    self.visitBlock(body, create_scope=False)
                    cond = self._is_truthy(unwrap_one(self.visit(cond_ctx)))
                    if cond:
                        break
                except LuaBreak:
                    break
                finally:
                    self.current_env = loop_env.parent
                    loop_env.close_scope(self._call_metamethod)
            return None

        if kind == "fornum":
            # for NAME '=' exp ',' exp (',' exp)? 'do' block 'end'
            var_name, exps, body = k[1], k[2], k[3]
            start = unwrap_one(self.visit(exps[0]))
            limit = unwrap_one(self.visit(exps[1]))
            step = unwrap_one(self.visit(exps[2])) if len(exps) > 2 else 1
            for what, v in (("initial value", start), ("limit", limit), ("step", step)):
                if not is_number(v):
                    raise self.rt_error(f"'for' {what} must be a number")
            if step == 0:
                raise self.rt_error("'for' step is zero")
            if isinstance(start, float) or isinstance(step, float):
                start, step, limit = float(start), float(step), float(limit)
            elif isinstance(limit, float):
                # límite float con inicio/paso enteros: se recorta al entero equivalente
                if math.isnan(limit):
                    return None
                if limit >= 2 ** 63:
                    limit = MAXINT
                elif limit <= -2 ** 63:
                    limit = MININT
                else:
                    limit = math.floor(limit) if step > 0 else math.ceil(limit)
            curr = start
            while (step > 0 and curr <= limit) or (step < 0 and curr >= limit):
                loop_env = Environment(parent=self.current_env, env_table=self.current_env.env_table)
                loop_env.vars[var_name] = curr
                self.current_env = loop_env
                try:
                    self.visitBlock(body, create_scope=False)
                except LuaBreak:
                    break
                finally:
                    self.current_env = loop_env.parent
                    if loop_env.to_close:
                        loop_env.close_scope(self._call_metamethod)
                curr += step
                if isinstance(curr, int) and not (MININT <= curr <= MAXINT):
                    break
            return None

        if kind == "forgen":
            # for namelist 'in' explist 'do' block 'end'
            names, exps, body = k[1], k[2], k[3]
            it_vals = expand_args([self.visit(e) for e in exps])
            iter_fn = it_vals[0] if len(it_vals) > 0 else None
            state = it_vals[1] if len(it_vals) > 1 else None
            ctrl = it_vals[2] if len(it_vals) > 2 else None
            while True:
                res = self._call_callable(iter_fn, [state, ctrl])
                row = list(res) if isinstance(res, MultiRes) else [res]
                if not row or row[0] is None:
                    break
                ctrl = row[0]
                loop_env = Environment(parent=self.current_env, env_table=self.current_env.env_table)
                for idx, n in enumerate(names):
                    loop_env.vars[n] = row[idx] if idx < len(row) else None
                self.current_env = loop_env
                try:
                    self.visitBlock(body, create_scope=False)
                except LuaBreak:
                    break
                finally:
                    self.current_env = loop_env.parent
                    if loop_env.to_close:
                        loop_env.close_scope(self._call_metamethod)
            return None

        if kind == "function":
            names, has_colon, funcbody = k[1], k[2], k[3]
            fn_obj = self._build_function(funcbody, inject_self=has_colon)
            if len(names) == 1:
                self.current_env.assign(names[0], fn_obj, self._table_set)
            else:
                target = self.current_env.get(names[0], self._table_get)
                for part in names[1:-1]:
                    target = self._table_get(target, part)
                self._table_set(target, names[-1], fn_obj)
            return None

        if kind == "localfunc":
            fn_name = k[1]
            self.current_env.define_local(fn_name, None)
            fn_obj = self._build_function(k[2], inject_self=False)
            self.current_env.vars[fn_name] = fn_obj
            return None

        return None

    # --- Funciones y llamadas ---
    def _build_function(self, funcbody_ctx, inject_self=False):
        params = ["self"] if inject_self else []
        is_vararg = False
        plist = funcbody_ctx.parlist()
        if plist:
            if plist.namelist():
                params.extend(n.getText() for n in plist.namelist().NAME())
            if "..." in plist.getText():
                is_vararg = True
        return LuaFunction(params, is_vararg, funcbody_ctx.block(), self.current_env, self)

    def visitFunctiondef(self, ctx):
        return self._build_function(ctx.funcbody(), inject_self=False)

    def _eval_args(self, args_ctx):
        info = args_ctx.__dict__.get("_ai")
        if info is None:
            if args_ctx.explist():
                info = ("exps", args_ctx.explist().exp())
            elif args_ctx.tableconstructor():
                info = ("table", args_ctx.tableconstructor())
            elif args_ctx.string():
                info = ("str", self._parse_string(args_ctx.string().getText()))
            else:
                info = ("none", None)
            args_ctx._ai = info
        kind, payload = info
        if kind == "exps":
            if len(payload) == 1:
                v = payload[0].accept(self)
                return list(v) if v.__class__ is MultiRes else [v]
            return expand_args([e.accept(self) for e in payload])
        if kind == "table":
            return [self.visit(payload)]
        if kind == "str":
            return [payload]
        return []

    # --- Descripción de variables para mensajes de error (como Lua: "(local 'x')") ---
    def _name_kind(self, name):
        env = self.current_env
        crossed = False
        while env is not None:
            if name in env.vars:
                return "upvalue" if crossed else "local"
            if env.is_func:
                crossed = True
            env = env.parent
        return "global"

    def _desc_suffix(self, desc):
        if desc is None:
            return ""
        kind, name = desc
        if kind == "name":
            kind = self._name_kind(name)
        return f" ({kind} '{name}')"

    def _exp_desc(self, exp_ctx):
        """Descripción sintáctica de una expresión (variable, campo, constante) o None."""
        try:
            if exp_ctx.string() is not None:
                return ("constant", self._parse_string(exp_ctx.string().getText()))
            pe = exp_ctx.prefixexp()
            if pe is None:
                return None
            ch = list(pe.children)
            if len(ch) == 1:
                return ("name", ch[0].getText())
            if len(ch) >= 2 and ch[-2].getText() == ".":
                return ("field", ch[-1].getText())
            if len(ch) >= 3 and ch[-3].getText() == "[" and ch[-2].string() is not None:
                return ("field", self._parse_string(ch[-2].string().getText()))
            if len(ch) >= 3 and ch[-1].getText() == "]":
                return ("field", "?")
        except AttributeError:
            pass
        return None

    @staticmethod
    def _node_kind(node):
        """Clasifica (una sola vez) un nodo de una cadena prefijo: sub-regla, args o token."""
        k = node.__dict__.get("_ck")
        if k is None:
            if node.getChildCount() > 0 and not hasattr(node, "explist"):
                k = ("sub", None)
            elif hasattr(node, "explist"):
                k = ("args", None)
            else:
                k = ("tok", node.symbol.text)
            node._ck = k
        return k

    def _eval_chain(self, nodes):
        """Evalúa una cadena prefijo (NAME, '.', '[', ':', args...). Devuelve (valor, descripción)."""
        curr = None
        desc = None
        i = 0
        n = len(nodes)
        node_kind = self._node_kind
        while i < n:
            node = nodes[i]
            kind, text = node_kind(node)
            if kind == "sub":
                curr, desc = self._eval_chain(node.children)
                i += 1
                continue
            if kind == "args":
                call_args = self._eval_args(node)
                curr = self._call_callable(unwrap_one(curr), call_args, desc)
                desc = None
                i += 1
                continue
            if text == "(":
                curr = unwrap_one(self.visit(nodes[i + 1]))
                desc = None
                i += 3  # salta '(', exp, ')'
            elif text == "[":
                key_ctx = nodes[i + 1]
                key = unwrap_one(self.visit(key_ctx))
                target = unwrap_one(curr)
                if target.__class__ is LuaTable:
                    curr = self._table_get(target, key)
                elif isinstance(target, (str, LuaFile)):
                    curr = self._table_get(target, key)
                else:
                    raise self.rt_error(f"attempt to index a {lua_type(target)} value{self._desc_suffix(desc)}")
                desc = ("field", key if isinstance(key, str) and key_ctx.string() is not None else "?")
                i += 3  # salta '[', exp, ']'
            elif text == ".":
                key = node_kind(nodes[i + 1])[1]
                target = unwrap_one(curr)
                if target.__class__ is LuaTable:
                    curr = self._table_get(target, key)
                elif isinstance(target, (str, LuaFile)):
                    curr = self._table_get(target, key)
                else:
                    raise self.rt_error(f"attempt to index a {lua_type(target)} value{self._desc_suffix(desc)}")
                desc = ("field", key)
                i += 2  # salta '.', NAME
            elif text == ":":
                method_name = node_kind(nodes[i + 1])[1]
                target = unwrap_one(curr)
                if not isinstance(target, (LuaTable, str, LuaFile)):
                    raise self.rt_error(f"attempt to index a {lua_type(target)} value{self._desc_suffix(desc)}")
                fn = self._table_get(target, method_name)
                call_args = self._eval_args(nodes[i + 2])
                curr = self._call_callable(fn, [target] + call_args, ("method", method_name))
                desc = None
                i += 3  # salta ':', NAME, args
            else:
                # Token NAME inicial
                curr = self.current_env.get(text, self._table_get)
                desc = ("name", text)
                i += 1
        return curr, desc

    def _eval_chain_nodes(self, nodes):
        return self._eval_chain(nodes)[0]

    def visitVar(self, ctx):
        return self._eval_chain_nodes(list(ctx.children))

    def visitPrefixexp(self, ctx):
        return self._eval_chain_nodes(list(ctx.children))

    def visitFunctioncall(self, ctx):
        return self._eval_chain_nodes(list(ctx.children))

    # --- Tablas ---
    def visitTableconstructor(self, ctx):
        tbl = LuaTable()
        flist = ctx.fieldlist()
        if not flist:
            return tbl
        fields = flist.field()
        array_idx = 1
        for idx, f in enumerate(fields):
            is_last = (idx == len(fields) - 1)
            c0 = f.getChild(0)
            if c0.getChildCount() == 0 and c0.getText() == "[":
                k = unwrap_one(self.visit(f.exp(0)))
                v = unwrap_one(self.visit(f.exp(1)))
                if k is None:
                    raise self.rt_error("table index is nil")
                if k.__class__ is float and k != k:
                    raise self.rt_error("table index is NaN")
                tbl.rawset(k, v)
            elif f.NAME() is not None:
                k = f.NAME().getText()
                v = unwrap_one(self.visit(f.exp(0)))
                tbl.rawset(k, v)
            else:
                val = self.visit(f.exp(0))
                if is_last and isinstance(val, MultiRes):
                    for item in val:
                        tbl.rawset(array_idx, item)
                        array_idx += 1
                else:
                    tbl.rawset(array_idx, unwrap_one(val))
                    array_idx += 1
        tbl.asize = array_idx - 1
        return tbl

    # --- Expresiones y operadores ---
    def _exp_info(self, ctx):
        """Clasifica una expresión una sola vez (el árbol es inmutable) y cachea literales."""
        n = ctx.getChildCount()
        if n == 1:
            c = ctx.getChild(0)
            if c.getChildCount() == 0:
                t = c.getText()
                if t == "nil":
                    return ("const", None)
                if t == "false":
                    return ("const", False)
                if t == "true":
                    return ("const", True)
                if t == "...":
                    return ("vararg",)
            if ctx.number():
                return ("const", self._parse_number(ctx.number().getText()))
            if ctx.string():
                return ("const", self._parse_string(ctx.string().getText()))
            sub = ctx.functiondef() or ctx.prefixexp() or ctx.tableconstructor()
            if sub is not None:
                return ("sub", sub)
        exps = ctx.exp()
        if len(exps) == 1:
            return ("unary", ctx.getChild(0).getText(), exps)
        if len(exps) == 2:
            return ("binary", ctx.getChild(1).getText(), exps)
        return ("none",)

    def visitExp(self, ctx):
        info = ctx.__dict__.get("_info")
        if info is None:
            info = ctx._info = self._exp_info(ctx)
        kind = info[0]
        if kind == "const":
            return info[1]
        if kind == "sub":
            return info[1].accept(self)
        if kind == "binary":
            op, exps = info[1], info[2]
            if op == "and":
                left = exps[0].accept(self)
                if left.__class__ is MultiRes:
                    left = left[0] if left else None
                if left is None or left is False:
                    return left
                return unwrap_one(exps[1].accept(self))
            if op == "or":
                left = exps[0].accept(self)
                if left.__class__ is MultiRes:
                    left = left[0] if left else None
                if left is not None and left is not False:
                    return left
                return unwrap_one(exps[1].accept(self))
            left = exps[0].accept(self)
            if left.__class__ is MultiRes:
                left = left[0] if left else None
            right = exps[1].accept(self)
            if right.__class__ is MultiRes:
                right = right[0] if right else None
            tl = left.__class__
            tr = right.__class__
            if (tl is int or tl is float) and (tr is int or tr is float):
                # camino rápido numérico
                if op == "+":
                    r = left + right
                elif op == "-":
                    r = left - right
                elif op == "*":
                    r = left * right
                elif op == "<":
                    return left < right
                elif op == "<=":
                    return left <= right
                elif op == ">":
                    return left > right
                elif op == ">=":
                    return left >= right
                elif op == "==":
                    return left == right
                elif op == "~=":
                    return left != right
                else:
                    return self._binary_op(op, left, right, exps)
                if tl is int and tr is int and not (MININT <= r <= MAXINT):
                    r = wrap_int64(r)
                return r
            return self._binary_op(op, left, right, exps)
        if kind == "vararg":
            return self.current_env.get("...", self._table_get)
        if kind == "unary":
            return self._unary_op(info[1], info[2])
        return None

    def _unary_op(self, op, exps):
        val = unwrap_one(exps[0].accept(self))
        if op == "not":
            return val is None or val is False
        if op == "#":
            return self._table_len(val, self._exp_desc(exps[0]) if not isinstance(val, (str, LuaTable)) else None)
        if op == "-":
            mm = self._get_metamethod(val, "__unm")
            if mm is not None:
                return unwrap_one(self._call_callable(mm, [val]))
            num = self._to_number(val)
            if num is None:
                if isinstance(val, str):
                    raise self.rt_error("attempt to unm a 'string' with a 'string'")
                raise self.rt_error(f"attempt to perform arithmetic on a {lua_type(val)} value{self._desc_suffix(self._exp_desc(exps[0]))}")
            return wrap_int64(-num) if isinstance(num, int) else -num
        if op == "~":
            mm = self._get_metamethod(val, "__bnot")
            if mm is not None:
                return unwrap_one(self._call_callable(mm, [val]))
            return self._wrap_int64(~self._to_int64(val, exps[0]))
        return None

    _BITWISE_MM = {"&": "__band", "|": "__bor", "~": "__bxor", "<<": "__shl", ">>": "__shr"}
    _ARITH_MM = {"+": "__add", "-": "__sub", "*": "__mul", "/": "__div", "//": "__idiv", "%": "__mod", "^": "__pow"}
    _ARITH_NAMES = {"+": "add", "-": "sub", "*": "mul", "/": "div", "//": "idiv", "%": "mod", "^": "pow"}

    def _binary_op(self, op, left, right, exps):
        # Concatenación
        if op == "..":
            lt, rt = left.__class__, right.__class__
            if (lt is str or lt is int or lt is float) and (rt is str or rt is int or rt is float):
                return (left if lt is str else lua_tostring(left)) + (right if rt is str else lua_tostring(right))
            mm = self._get_metamethod(left, "__concat") or self._get_metamethod(right, "__concat")
            if mm is not None:
                return unwrap_one(self._call_callable(mm, [left, right]))
            left_ok = lt is str or lt is int or lt is float
            bad = right if left_ok else left
            bad_ctx = exps[1] if left_ok else exps[0]
            raise self.rt_error(f"attempt to concatenate a {lua_type(bad)} value{self._desc_suffix(self._exp_desc(bad_ctx))}")

        # Igualdad y orden
        if op == "==":
            return self._lua_equal(left, right)
        if op == "~=":
            return not self._lua_equal(left, right)
        if op in ("<", "<=", ">", ">="):
            return self._lua_compare(op, left, right)

        # Bitwise
        if op in self._BITWISE_MM:
            mm = self._get_metamethod(left, self._BITWISE_MM[op]) or self._get_metamethod(right, self._BITWISE_MM[op])
            if mm is not None:
                return unwrap_one(self._call_callable(mm, [left, right]))
            a = self._to_int64(left, exps[0])
            b = self._to_int64(right, exps[1])
            if op == "&":
                return self._wrap_int64(a & b)
            if op == "|":
                return self._wrap_int64(a | b)
            if op == "~":
                return self._wrap_int64(a ^ b)
            if op == "<<":
                return self._bit_shift(a, b)
            return self._bit_shift(a, -b)

        # Aritméticos
        if op in self._ARITH_MM:
            mm = self._get_metamethod(left, self._ARITH_MM[op]) or self._get_metamethod(right, self._ARITH_MM[op])
            if mm is not None:
                return unwrap_one(self._call_callable(mm, [left, right]))
            a = self._to_number(left)
            b = self._to_number(right)
            if a is None or b is None:
                if isinstance(left, str) or isinstance(right, str):
                    raise self.rt_error(f"attempt to {self._ARITH_NAMES[op]} a '{lua_type(left)}' with a '{lua_type(right)}'")
                bad = right if a is not None else left
                bad_ctx = exps[1] if a is not None else exps[0]
                raise self.rt_error(f"attempt to perform arithmetic on a {lua_type(bad)} value{self._desc_suffix(self._exp_desc(bad_ctx))}")
            return self._arith(op, a, b)
        return None

    def _arith(self, op, a, b):
        both_int = isinstance(a, int) and isinstance(b, int)
        if op == "+":
            return wrap_int64(a + b) if both_int else a + b
        if op == "-":
            return wrap_int64(a - b) if both_int else a - b
        if op == "*":
            return wrap_int64(a * b) if both_int else a * b
        if op == "/":
            a, b = float(a), float(b)
            if b == 0:
                if a == 0 or a != a:
                    return math.copysign(float("nan"), -1)
                return math.copysign(math.inf, a) * math.copysign(1.0, b)
            return a / b
        if op == "//":
            if both_int:
                if b == 0:
                    raise self.rt_error("attempt to divide by zero")
                return wrap_int64(a // b)
            a, b = float(a), float(b)
            if b == 0:
                if a == 0 or a != a:
                    return math.copysign(float("nan"), -1)
                return math.copysign(math.inf, a) * math.copysign(1.0, b)
            q = a / b
            return float(math.floor(q)) if math.isfinite(q) else q
        if op == "%":
            if both_int:
                if b == 0:
                    raise self.rt_error("attempt to perform 'n%%0'".replace("%%", "%"))
                return a % b
            a, b = float(a), float(b)
            if b == 0 or math.isinf(a) or a != a or b != b:
                return math.copysign(float("nan"), -1)
            if math.isinf(b):
                return a if (a >= 0) == (b > 0) or a == 0 else b
            return a % b
        if op == "^":
            try:
                return math.pow(a, b)
            except OverflowError:
                return math.inf
            except ValueError:
                return math.copysign(float("nan"), -1)
        raise self.rt_error(f"unknown arithmetic operator {op}")

    def _bit_shift(self, a, shift):
        if shift >= 64 or shift <= -64:
            return 0
        ua = a & 0xFFFFFFFFFFFFFFFF
        if shift >= 0:
            return self._wrap_int64(ua << shift)
        return self._wrap_int64(ua >> (-shift))

    def _lua_equal(self, a, b):
        if isinstance(a, (int, float)) and not isinstance(a, bool) and \
           isinstance(b, (int, float)) and not isinstance(b, bool):
            return a == b
        if a is b:
            return True
        if type(a) is not type(b):
            return False
        if isinstance(a, LuaTable):
            mm = self._get_metamethod(a, "__eq") or self._get_metamethod(b, "__eq")
            if mm is not None:
                return self._is_truthy(unwrap_one(self._call_callable(mm, [a, b])))
        return a == b

    def _lua_compare(self, op, a, b):
        if isinstance(a, (int, float)) and not isinstance(a, bool) and \
           isinstance(b, (int, float)) and not isinstance(b, bool):
            if op == "<": return a < b
            if op == "<=": return a <= b
            if op == ">": return a > b
            if op == ">=": return a >= b
        if isinstance(a, str) and isinstance(b, str):
            if op == "<": return a < b
            if op == "<=": return a <= b
            if op == ">": return a > b
            if op == ">=": return a >= b
        if op in ("<", ">"):
            x, y = (a, b) if op == "<" else (b, a)
            mm = self._get_metamethod(x, "__lt") or self._get_metamethod(y, "__lt")
            if mm is not None:
                return self._is_truthy(unwrap_one(self._call_callable(mm, [x, y])))
        if op in ("<=", ">="):
            x, y = (a, b) if op == "<=" else (b, a)
            mm = self._get_metamethod(x, "__le") or self._get_metamethod(y, "__le")
            if mm is not None:
                return self._is_truthy(unwrap_one(self._call_callable(mm, [x, y])))
        ta, tb = lua_type(a), lua_type(b)
        if ta == tb:
            raise self.rt_error(f"attempt to compare two {ta} values")
        raise self.rt_error(f"attempt to compare {ta} with {tb}")