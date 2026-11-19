import re
import math
from grammar.LuaParserVisitor import LuaParserVisitor
from runtime.values import LuaTable, MultiRes, unwrap_one, expand_args
from runtime.environment import Environment
from runtime.exceptions import LuaReturn, LuaBreak, LuaGoto, LuaError
from runtime.stdlib import build_global_env, lua_tostring

class LuaFunction:
    def __init__(self, params, is_vararg, block_ctx, closure_env, interp):
        self.params = params
        self.is_vararg = is_vararg
        self.block_ctx = block_ctx
        self.closure_env = closure_env
        self.interp = interp

    def __call__(self, *args):
        fn_env = Environment(parent=self.closure_env, env_table=self.closure_env.env_table)
        arg_list = list(args)
        for i, p_name in enumerate(self.params):
            fn_env.define_local(p_name, arg_list[i] if i < len(arg_list) else None)
        if self.is_vararg:
            fn_env.vars["..."] = MultiRes(arg_list[len(self.params):])

        prev_env = self.interp.current_env
        self.interp.current_env = fn_env
        try:
            self.interp.visitBlock(self.block_ctx, create_scope=False)
            return None
        except LuaReturn as ret:
            if len(ret.values) == 0:
                return None
            if len(ret.values) == 1:
                return ret.values[0]
            return MultiRes(ret.values)
        finally:
            try:
                fn_env.close_scope(self.interp._call_metamethod)
            finally:
                self.interp.current_env = prev_env

class LuaInterpreter(LuaParserVisitor):
    def __init__(self):
        self.global_table = build_global_env(self)
        self.current_env = Environment(parent=None, env_table=self.global_table)
        self.current_env.vars["..."] = MultiRes([])

    # --- Helpers de semántica Lua ---
    def _is_truthy(self, val):
        return val is not None and val is not False

    def _to_number(self, val):
        if isinstance(val, bool):
            return None
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return None
            try:
                if s.lower().startswith(("0x", "-0x", "+0x")):
                    if "." in s or "p" in s.lower():
                        return float.fromhex(s)
                    return int(s, 16)
                return int(s)
            except ValueError:
                try:
                    return float(s)
                except ValueError:
                    return None
        return None

    def _to_int64(self, val):
        if isinstance(val, int) and not isinstance(val, bool):
            return self._wrap_int64(val)
        if isinstance(val, float) and not math.isnan(val) and not math.isinf(val) and val.is_integer():
            return self._wrap_int64(int(val))
        raise LuaError("number has no integer representation")

    def _wrap_int64(self, n):
        n &= 0xFFFFFFFFFFFFFFFF
        return n - 0x10000000000000000 if n & 0x8000000000000000 else n

    def _get_metamethod(self, obj, event):
        if isinstance(obj, LuaTable) and isinstance(obj.metatable, LuaTable):
            return obj.metatable.rawget(event)
        return None

    def _call_metamethod(self, obj, event, args):
        mm = self._get_metamethod(obj, event)
        if mm is not None:
            return self._call_callable(mm, args)
        return None

    def _call_callable(self, fn, args):
        if callable(fn):
            return fn(*args)
        if isinstance(fn, LuaTable):
            mm = self._get_metamethod(fn, "__call")
            if mm is not None:
                return self._call_callable(mm, [fn] + args)
        raise LuaError(f"attempt to call a {type(fn).__name__} value")

    def _table_get(self, t, key, depth=0):
        if depth > 2000:
            raise LuaError("'__index' chain too long; possible loop")
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
        raise LuaError("attempt to index a non-table value")

    def _table_set(self, t, key, val, depth=0):
        if depth > 2000:
            raise LuaError("'__newindex' chain too long; possible loop")
        if isinstance(t, LuaTable):
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
        raise LuaError("attempt to index a non-table value")

    def _table_len(self, obj):
        if isinstance(obj, str):
            return len(obj)
        if isinstance(obj, LuaTable):
            mm = self._get_metamethod(obj, "__len")
            if mm is not None:
                return unwrap_one(self._call_callable(mm, [obj]))
            i = 0
            while obj.rawget(i + 1) is not None:
                i += 1
            return i
        raise LuaError("attempt to get length of a non-sequence value")

    # --- Parseo de literales ---
    def _parse_number(self, text):
        if text.lower().startswith("0x"):
            if "." in text or "p" in text.lower():
                return float.fromhex(text)
            return int(text, 16)
        if "." in text or "e" in text.lower():
            return float(text)
        return int(text)

    def _parse_string(self, text):
        if text.startswith("["):
            match = re.match(r"^\[(=*)\[\r?\n?(.*)\]\1\]$", text, re.DOTALL)
            return match.group(2) if match else text
        inner = text[1:-1]
        out = []
        i = 0
        escapes = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\", '"': '"', "'": "'"}
        while i < len(inner):
            ch = inner[i]
            if ch != "\\":
                out.append(ch)
                i += 1
                continue
            i += 1
            if i >= len(inner):
                break
            esc = inner[i]
            if esc in escapes:
                out.append(escapes[esc])
                i += 1
            elif esc == "z":
                i += 1
                while i < len(inner) and inner[i] in " \t\r\n\f\v":
                    i += 1
            elif esc == "x":
                out.append(chr(int(inner[i + 1:i + 3], 16)))
                i += 3
            elif esc == "u":
                end_brace = inner.index("}", i + 2)
                codepoint = int(inner[i + 2:end_brace], 16)
                out.append(chr(codepoint))
                i = end_brace + 1
            elif esc.isdigit():
                digits = inner[i:i + 3]
                num_str = "".join(c for c in digits if c.isdigit())
                out.append(chr(int(num_str)))
                i += len(num_str)
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

        stats = ctx.stat()
        labels = {}
        for idx, st in enumerate(stats):
            if st.label():
                labels[st.label().NAME().getText()] = idx

        idx = 0
        caught_err = None
        try:
            while idx < len(stats):
                try:
                    self.visit(stats[idx])
                    idx += 1
                except LuaGoto as g:
                    if g.label in labels:
                        idx = labels[g.label] + 1
                    else:
                        raise
            if ctx.retstat():
                self.visit(ctx.retstat())
        except LuaError as e:
            caught_err = e.lua_obj
            raise
        finally:
            if create_scope:
                closing_env = self.current_env
                self.current_env = closing_env.parent
                closing_env.close_scope(self._call_metamethod, caught_err)

    def visitRetstat(self, ctx):
        vals = expand_args([self.visit(e) for e in ctx.explist().exp()]) if ctx.explist() else []
        raise LuaReturn(vals)

    def _resolve_lvalue(self, var_ctx):
        children = list(var_ctx.children)
        if len(children) == 1:
            return ("var", children[0].getText())
        if children[-1].getText() == "]":
            target = self._eval_chain_nodes(children[:-3])
            key = unwrap_one(self.visit(children[-2]))
            return ("table", target, key)
        # Caso prefix '.' NAME
        target = self._eval_chain_nodes(children[:-2])
        key = children[-1].getText()
        return ("table", target, key)

    def visitStat(self, ctx):
        first = ctx.getChild(0).getText()

        # Asignación múltiple estricta: varlist '=' explist
        if ctx.varlist():
            lvalues = [self._resolve_lvalue(v) for v in ctx.varlist().var()]
            rvalues = expand_args([self.visit(e) for e in ctx.explist().exp()])
            for idx, lv in enumerate(lvalues):
                val = rvalues[idx] if idx < len(rvalues) else None
                if lv[0] == "var":
                    self.current_env.assign(lv[1], val, self._table_set)
                else:
                    self._table_set(lv[1], lv[2], val)
            return None

        if ctx.functioncall():
            self.visit(ctx.functioncall())
            return None

        if first == "break":
            raise LuaBreak()

        if first == "goto":
            raise LuaGoto(ctx.NAME().getText())

        if first == "do":
            self.visitBlock(ctx.block(0), create_scope=True)
            return None

        if first == "while":
            while self._is_truthy(unwrap_one(self.visit(ctx.exp(0)))):
                try:
                    self.visitBlock(ctx.block(0), create_scope=True)
                except LuaBreak:
                    break
            return None

        if first == "repeat":
            while True:
                loop_env = Environment(parent=self.current_env, env_table=self.current_env.env_table)
                self.current_env = loop_env
                try:
                    self.visitBlock(ctx.block(0), create_scope=False)
                    cond = self._is_truthy(unwrap_one(self.visit(ctx.exp(0))))
                    if cond:
                        break
                except LuaBreak:
                    break
                finally:
                    self.current_env = loop_env.parent
                    loop_env.close_scope(self._call_metamethod)
            return None

        if first == "if":
            exps = ctx.exp()
            blocks = ctx.block()
            for i, cond_exp in enumerate(exps):
                if self._is_truthy(unwrap_one(self.visit(cond_exp))):
                    self.visitBlock(blocks[i], create_scope=True)
                    return None
            if len(blocks) > len(exps):
                self.visitBlock(blocks[-1], create_scope=True)
            return None

        if first == "for":
            # For numérico: for NAME '=' exp ',' exp (',' exp)? 'do' block 'end'
            if ctx.namelist() is None:
                var_name = ctx.NAME().getText()
                start = self._to_number(unwrap_one(self.visit(ctx.exp(0))))
                limit = self._to_number(unwrap_one(self.visit(ctx.exp(1))))
                step = self._to_number(unwrap_one(self.visit(ctx.exp(2)))) if len(ctx.exp()) > 2 else 1
                curr = start
                while (step > 0 and curr <= limit) or (step < 0 and curr >= limit):
                    loop_env = Environment(parent=self.current_env, env_table=self.current_env.env_table)
                    loop_env.define_local(var_name, curr)
                    self.current_env = loop_env
                    try:
                        self.visitBlock(ctx.block(0), create_scope=False)
                    except LuaBreak:
                        break
                    finally:
                        self.current_env = loop_env.parent
                        loop_env.close_scope(self._call_metamethod)
                    curr += step
                return None

            # For genérico: for namelist 'in' explist 'do' block 'end'
            names = [n.getText() for n in ctx.namelist().NAME()]
            it_vals = expand_args([self.visit(e) for e in ctx.explist().exp()])
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
                    loop_env.define_local(n, row[idx] if idx < len(row) else None)
                self.current_env = loop_env
                try:
                    self.visitBlock(ctx.block(0), create_scope=False)
                except LuaBreak:
                    break
                finally:
                    self.current_env = loop_env.parent
                    loop_env.close_scope(self._call_metamethod)
            return None

        if first == "function":
            fn_ctx = ctx.funcname()
            names = [n.getText() for n in fn_ctx.NAME()]
            has_colon = ":" in fn_ctx.getText()
            fn_obj = self._build_function(ctx.funcbody(), inject_self=has_colon)
            if len(names) == 1:
                self.current_env.assign(names[0], fn_obj, self._table_set)
            else:
                target = self.current_env.get(names[0], self._table_get)
                for part in names[1:-1]:
                    target = self._table_get(target, part)
                self._table_set(target, names[-1], fn_obj)
            return None

        if first == "local":
            if ctx.funcbody() is not None:
                fn_name = ctx.NAME().getText()
                self.current_env.define_local(fn_name, None)
                fn_obj = self._build_function(ctx.funcbody(), inject_self=False)
                self.current_env.vars[fn_name] = fn_obj
                return None

            att_items = []
            attlist = ctx.attnamelist()
            for i, name_node in enumerate(attlist.NAME()):
                attrib_node = attlist.attrib(i)
                attr = attrib_node.NAME().getText() if attrib_node and attrib_node.NAME() else None
                att_items.append((name_node.getText(), attr))

            rvalues = expand_args([self.visit(e) for e in ctx.explist().exp()]) if ctx.explist() else []
            for idx, (vname, attr) in enumerate(att_items):
                val = rvalues[idx] if idx < len(rvalues) else None
                self.current_env.define_local(vname, val, attrib=attr)
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
        if args_ctx.explist():
            return expand_args([self.visit(e) for e in args_ctx.explist().exp()])
        if args_ctx.tableconstructor():
            return [self.visit(args_ctx.tableconstructor())]
        if args_ctx.string():
            return [self._parse_string(args_ctx.string().getText())]
        return []

    def _eval_chain_nodes(self, nodes):
        curr = None
        i = 0
        while i < len(nodes):
            node = nodes[i]
            text = node.getText()

            if hasattr(node, "children") and node.children is not None and not hasattr(node, "explist"):
                # Subregla recursiva (VarContext, FunctioncallContext, PrefixexpContext)
                curr = self._eval_chain_nodes(list(node.children))
                i += 1
            elif text == "(":
                curr = unwrap_one(self.visit(nodes[i + 1]))
                i += 3  # salta '(', exp, ')'
            elif text == "[":
                key = unwrap_one(self.visit(nodes[i + 1]))
                curr = self._table_get(unwrap_one(curr), key)
                i += 3  # salta '[', exp, ']'
            elif text == ".":
                key = nodes[i + 1].getText()
                curr = self._table_get(unwrap_one(curr), key)
                i += 2  # salta '.', NAME
            elif text == ":":
                method_name = nodes[i + 1].getText()
                call_args = self._eval_args(nodes[i + 2])
                target = unwrap_one(curr)
                fn = self._table_get(target, method_name)
                curr = self._call_callable(fn, [target] + call_args)
                i += 3  # salta ':', NAME, args
            elif hasattr(node, "explist"):
                # Nodo ArgsContext directo
                call_args = self._eval_args(node)
                curr = self._call_callable(unwrap_one(curr), call_args)
                i += 1
            else:
                # Token NAME inicial
                curr = self.current_env.get(text, self._table_get)
                i += 1
        return curr

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
            if f.getChild(0).getText() == "[":
                k = unwrap_one(self.visit(f.exp(0)))
                v = unwrap_one(self.visit(f.exp(1)))
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
        return tbl

    # --- Expresiones y operadores ---
    def visitExp(self, ctx):
        first_text = ctx.getChild(0).getText()
        if first_text == "nil":
            return None
        if first_text == "false":
            return False
        if first_text == "true":
            return True
        if first_text == "...":
            return self.current_env.get("...", self._table_get)
        if ctx.number():
            return self._parse_number(ctx.number().getText())
        if ctx.string():
            return self._parse_string(ctx.string().getText())
        if ctx.functiondef():
            return self.visit(ctx.functiondef())
        if ctx.prefixexp():
            return self.visit(ctx.prefixexp())
        if ctx.tableconstructor():
            return self.visit(ctx.tableconstructor())

        exps = ctx.exp()
        # Operadores unarios
        if len(exps) == 1:
            op = ctx.getChild(0).getText()
            val = unwrap_one(self.visit(exps[0]))
            if op == "not":
                return not self._is_truthy(val)
            if op == "#":
                return self._table_len(val)
            if op == "-":
                mm = self._get_metamethod(val, "__unm")
                if mm is not None:
                    return unwrap_one(self._call_callable(mm, [val]))
                num = self._to_number(val)
                if num is None:
                    raise LuaError("attempt to perform arithmetic on a non-number")
                return -num
            if op == "~":
                mm = self._get_metamethod(val, "__bnot")
                if mm is not None:
                    return unwrap_one(self._call_callable(mm, [val]))
                return self._wrap_int64(~self._to_int64(val))

        # Operadores binarios
        if len(exps) == 2:
            op = ctx.getChild(1).getText()
            left = unwrap_one(self.visit(exps[0]))

            # Cortocircuito lógico
            if op == "and":
                return unwrap_one(self.visit(exps[1])) if self._is_truthy(left) else left
            if op == "or":
                return left if self._is_truthy(left) else unwrap_one(self.visit(exps[1]))

            right = unwrap_one(self.visit(exps[1]))

            # Concatenación
            if op == "..":
                mm = self._get_metamethod(left, "__concat") or self._get_metamethod(right, "__concat")
                if mm is not None:
                    return unwrap_one(self._call_callable(mm, [left, right]))
                if isinstance(left, (str, int, float)) and not isinstance(left, bool) and \
                   isinstance(right, (str, int, float)) and not isinstance(right, bool):
                    return lua_tostring(left, self) + lua_tostring(right, self)
                raise LuaError("attempt to concatenate non-string/number values")

            # Igualdad y orden
            if op in ("==", "~="):
                eq = self._lua_equal(left, right)
                return eq if op == "==" else not eq
            if op in ("<", "<=", ">", ">="):
                return self._lua_compare(op, left, right)

            # Bitwise
            bitwise_mm = {"&": "__band", "|": "__bor", "~": "__bxor", "<<": "__shl", ">>": "__shr"}
            if op in bitwise_mm:
                mm = self._get_metamethod(left, bitwise_mm[op]) or self._get_metamethod(right, bitwise_mm[op])
                if mm is not None:
                    return unwrap_one(self._call_callable(mm, [left, right]))
                a = self._to_int64(left)
                b = self._to_int64(right)
                if op == "&":
                    return self._wrap_int64(a & b)
                if op == "|":
                    return self._wrap_int64(a | b)
                if op == "~":
                    return self._wrap_int64(a ^ b)
                if op == "<<":
                    return self._bit_shift(a, b)
                if op == ">>":
                    return self._bit_shift(a, -b)

            # Aritméticos
            arith_mm = {"+": "__add", "-": "__sub", "*": "__mul", "/": "__div", "//": "__idiv", "%": "__mod", "^": "__pow"}
            if op in arith_mm:
                mm = self._get_metamethod(left, arith_mm[op]) or self._get_metamethod(right, arith_mm[op])
                if mm is not None:
                    return unwrap_one(self._call_callable(mm, [left, right]))
                a = self._to_number(left)
                b = self._to_number(right)
                if a is None or b is None:
                    raise LuaError("attempt to perform arithmetic on a non-number")
                if op == "+":
                    return a + b
                if op == "-":
                    return a - b
                if op == "*":
                    return a * b
                if op == "/":
                    if b == 0:
                        if a == 0:
                            return float("nan")
                        return float("inf") if a > 0 else float("-inf")
                    return float(a) / float(b)
                if op == "//":
                    if b == 0:
                        if isinstance(a, int) and isinstance(b, int):
                            raise LuaError("attempt to divide by zero")
                        if a == 0:
                            return float("nan")
                        return float("inf") if a > 0 else float("-inf")
                    res = math.floor(a / b)
                    return int(res) if isinstance(a, int) and isinstance(b, int) else float(res)
                if op == "%":
                    if b == 0:
                        if isinstance(a, int) and isinstance(b, int):
                            raise LuaError("attempt to perform 'n%0'")
                        return float("nan")
                    res = a % b
                    return int(res) if isinstance(a, int) and isinstance(b, int) else float(res)
                if op == "^":
                    return float(a ** b)

        return None

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
        raise LuaError(f"attempt to compare {type(a).__name__} with {type(b).__name__}")