"""Verificador estático de un chunk Lua 5.4 (análisis léxico, sintáctico y semántico).

ANTLR construye el árbol que ejecuta el intérprete, pero sus mensajes de error no son los de
Lua. Este módulo replica la estructura de llex.c y lparser.c (analizador descendente
recursivo) solo para *detectar* errores de compilación y reportarlos con el mismo texto que
el compilador oficial, por ejemplo:

    [string "return 1 +"]:1: unexpected symbol near <eof>
    input:3: 'end' expected (to close 'function' at line 1) near <eof>
    input:2: attempt to assign to const variable 'x'
    input:5: no visible label 'fin' for <goto> at line 2

Además de la sintaxis hace las comprobaciones semánticas que Lua hace al compilar: asignación a
variables <const>/<close>, atributos desconocidos, '...' fuera de una función variádica,
etiquetas repetidas, 'goto' sin etiqueta visible o que entra en el ámbito de un local y
'break' fuera de un bucle.

Uso: check(source, chunkname) -> None si el chunk es válido, o (mensaje, es_semantico).
"""

RESERVED = {
    "and", "break", "do", "else", "elseif", "end", "false", "for", "function", "goto", "if",
    "in", "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while",
}

# tokens de "valor": su texto en los mensajes es el propio lexema
NAME, STRING, NUMBER, EOS = "<name>", "<string>", "<number>", "<eof>"

UNARY_OPS = {"not", "-", "~", "#"}
UNARY_PRIORITY = 12
BINARY_PRIORITY = {
    "+": (10, 10), "-": (10, 10), "*": (11, 11), "%": (11, 11), "^": (14, 13),
    "/": (11, 11), "//": (11, 11), "&": (6, 6), "|": (4, 4), "~": (5, 5),
    "<<": (7, 7), ">>": (7, 7), "..": (9, 8),
    "==": (3, 3), "<": (3, 3), "<=": (3, 3), "~=": (3, 3), ">": (3, 3), ">=": (3, 3),
    "and": (2, 2), "or": (1, 1),
}

HEX = "0123456789abcdefABCDEF"
DIGITS = "0123456789"
ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
ALNUM = ALPHA + DIGITS
_SIMPLE_ESC = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v",
               "\\": "\\", '"': '"', "'": "'"}


class LuaSyntaxError(Exception):
    def __init__(self, msg, semantic=False):
        super().__init__(msg)
        self.msg = msg
        self.semantic = semantic


def _utf8(cp):
    """Bytes UTF-8 (extendido hasta 2^31, como luaO_utf8esc) como str latin-1."""
    if cp < 0x80:
        return chr(cp)
    out = []
    mfb = 0x3F
    while cp > mfb:
        out.append(0x80 | (cp & 0x3F))
        cp >>= 6
        mfb >>= 1
    out.append(((~mfb << 1) & 0xFF) | cp)
    return "".join(chr(b) for b in reversed(out))


def _str2number_ok(text):
    """¿Es 'text' un numeral válido de Lua? (equivalente a luaO_str2num != 0)."""
    from runtime.stdlib import str2number
    return str2number(text) is not None


# ---------------------------------------------------------------------------
# Analizador léxico (llex.c)
# ---------------------------------------------------------------------------
class Token:
    __slots__ = ("kind", "text", "line")

    def __init__(self, kind, text, line):
        self.kind = kind  # símbolo/palabra reservada, o NAME/STRING/NUMBER/EOS
        self.text = text  # lexema (para mensajes "near ...")
        self.line = line  # línea en la que termina el token (ls->linenumber)


class Lexer:
    def __init__(self, src, chunkname):
        self.src = src
        self.n = len(src)
        self.pos = 0
        self.line = 1
        self.chunkname = chunkname

    def cur(self):
        return self.src[self.pos] if self.pos < self.n else None

    def error(self, msg, near):
        text = f"{self.chunkname}:{self.line}: {msg}"
        if near is not None:
            text += f" near {near}"
        raise LuaSyntaxError(text)

    def _inclinenumber(self):
        old = self.cur()
        self.pos += 1
        c = self.cur()
        if c in ("\n", "\r") and c != old:
            self.pos += 1  # '\n\r' o '\r\n' cuentan como un solo salto
        self.line += 1

    def _skip_sep(self):
        """Lee '[' '='* '[' (o ']' '='* ']'). Devuelve nº de '=' + 2 si es un separador
        válido, 1 si era solo el corchete, 0 si había '=' sin segundo corchete."""
        s = self.cur()
        self.pos += 1
        count = 0
        while self.cur() == "=":
            self.pos += 1
            count += 1
        if self.cur() == s:
            return count + 2
        return 1 if count == 0 else 0

    def _read_long_string(self, sep, is_comment, start_line):
        self.pos += 1  # salta el segundo '['
        if self.cur() in ("\n", "\r"):
            self._inclinenumber()
        while True:
            c = self.cur()
            if c is None:
                what = "comment" if is_comment else "string"
                self.error(f"unfinished long {what} (starting at line {start_line})", EOS)
            if c == "]":
                save = self.pos
                if self._skip_sep() == sep:
                    self.pos += 1  # salta el segundo ']'
                    return
                self.pos = save + 1
            elif c in ("\n", "\r"):
                self._inclinenumber()
            else:
                self.pos += 1

    def _read_string(self, delim):
        buf = [delim]
        self.pos += 1
        while True:
            c = self.cur()
            if c is None:
                self.error("unfinished string", EOS)
            if c in ("\n", "\r"):
                self.error("unfinished string", "'" + "".join(buf) + "'")
            if c == delim:
                self.pos += 1
                buf.append(delim)
                return "".join(buf)
            if c != "\\":
                buf.append(c)
                self.pos += 1
                continue
            # secuencia de escape
            buf.append("\\")
            self.pos += 1
            c = self.cur()

            def escerror(msg):
                if self.cur() is not None:
                    buf.append(self.cur())
                    self.pos += 1
                self.error(msg, "'" + "".join(buf) + "'")

            if c is None:
                continue  # se informará como 'unfinished string'
            # el buffer guarda el carácter ya procesado (como llex.c), salvo en los errores
            if c in _SIMPLE_ESC:
                buf[-1] = _SIMPLE_ESC[c]
                self.pos += 1
            elif c in ("\n", "\r"):
                self._inclinenumber()
                buf[-1] = "\n"
            elif c == "x":
                buf.append(c)
                self.pos += 1
                r = 0
                for _ in range(2):
                    if self.cur() is None or self.cur() not in HEX:
                        escerror("hexadecimal digit expected")
                    r = r * 16 + int(self.cur(), 16)
                    buf.append(self.cur())
                    self.pos += 1
                del buf[-4:]
                buf.append(chr(r))
            elif c == "z":
                self.pos += 1
                buf.pop()
                while self.cur() is not None and self.cur() in " \t\f\v\n\r":
                    if self.cur() in "\n\r":
                        self._inclinenumber()
                    else:
                        self.pos += 1
            elif c == "u":
                buf.append(c)
                self.pos += 1
                if self.cur() != "{":
                    escerror("missing '{' in \\u{xxxx}")
                buf.append("{")
                self.pos += 1
                if self.cur() is None or self.cur() not in HEX:
                    escerror("hexadecimal digit expected")
                r = 0
                while self.cur() is not None and self.cur() in HEX:
                    r = r * 16 + int(self.cur(), 16)
                    if r > 0x7FFFFFFF:
                        escerror("UTF-8 value too large")
                    buf.append(self.cur())
                    self.pos += 1
                if self.cur() != "}":
                    escerror("missing '}' in \\u{xxxx}")
                self.pos += 1
                while buf[-1] != "\\":
                    buf.pop()
                buf.pop()
                buf.append(_utf8(r))
            elif c in DIGITS:
                r = 0
                nd = 0
                for _ in range(3):
                    if self.cur() is None or self.cur() not in DIGITS:
                        break
                    r = r * 10 + int(self.cur())
                    buf.append(self.cur())
                    self.pos += 1
                    nd += 1
                if r > 255:
                    escerror("decimal escape too large")
                del buf[-(nd + 1):]
                buf.append(chr(r))
            else:
                escerror("invalid escape sequence")

    def _read_numeral(self):
        start = self.pos
        first = self.cur()
        self.pos += 1
        expo = "Ee"
        if first == "0" and self.cur() in ("x", "X"):
            self.pos += 1
            expo = "Pp"
        while True:
            c = self.cur()
            if c is not None and c in expo:
                self.pos += 1
                if self.cur() in ("+", "-"):
                    self.pos += 1
            elif c is not None and (c in HEX or c == "."):
                self.pos += 1
            else:
                break
        c = self.cur()
        if c is not None and c in ALPHA:
            self.pos += 1  # numeral pegado a una letra: fuerza el error
        text = self.src[start:self.pos]
        if not _str2number_ok(text):
            self.error("malformed number", "'" + text + "'")
        return text

    def next_token(self):
        while True:
            c = self.cur()
            if c is None:
                return Token(EOS, EOS, self.line)
            if c in ("\n", "\r"):
                self._inclinenumber()
                continue
            if c in " \t\f\v":
                self.pos += 1
                continue
            if c == "-":
                if self.src.startswith("--", self.pos):
                    self.pos += 2
                    if self.cur() == "[":
                        start_line = self.line
                        sep = self._skip_sep()
                        if sep >= 2:
                            self._read_long_string(sep, True, start_line)
                            continue
                    while self.cur() is not None and self.cur() not in "\n\r":
                        self.pos += 1
                    continue
                self.pos += 1
                return Token("-", "-", self.line)
            if c == "[":
                start = self.pos
                start_line = self.line
                sep = self._skip_sep()
                if sep >= 2:
                    self._read_long_string(sep, False, start_line)
                    return Token(STRING, self.src[start:self.pos], self.line)
                if sep == 0:
                    self.error("invalid long string delimiter", "'" + self.src[start:self.pos] + "'")
                return Token("[", "[", self.line)
            if c in "\"'":
                text = self._read_string(c)
                return Token(STRING, text, self.line)
            if c == ".":
                if self.src.startswith("...", self.pos):
                    self.pos += 3
                    return Token("...", "...", self.line)
                if self.src.startswith("..", self.pos):
                    self.pos += 2
                    return Token("..", "..", self.line)
                nxt = self.src[self.pos + 1] if self.pos + 1 < self.n else ""
                if nxt and nxt in DIGITS:
                    return Token(NUMBER, self._read_numeral(), self.line)
                self.pos += 1
                return Token(".", ".", self.line)
            if c in DIGITS:
                return Token(NUMBER, self._read_numeral(), self.line)
            if c in ALPHA:
                start = self.pos
                while self.cur() is not None and self.cur() in ALNUM:
                    self.pos += 1
                word = self.src[start:self.pos]
                if word in RESERVED:
                    return Token(word, word, self.line)
                return Token(NAME, word, self.line)
            for op in ("==", "<=", ">=", "~=", "<<", ">>", "//", "::"):
                if self.src.startswith(op, self.pos):
                    self.pos += 2
                    return Token(op, op, self.line)
            self.pos += 1
            return Token(c, c, self.line)


def token2str(kind):
    """luaX_token2str: cómo se nombra un tipo de token en los mensajes."""
    if kind in (NAME, STRING, NUMBER, EOS):
        return kind
    if len(kind) == 1 and not (32 <= ord(kind) < 127):
        return f"'<\\{ord(kind)}>'"
    return f"'{kind}'"


# ---------------------------------------------------------------------------
# Analizador sintáctico + comprobaciones semánticas (lparser.c)
# ---------------------------------------------------------------------------
class Block:
    __slots__ = ("nactvar", "firstlabel", "firstgoto", "isloop")

    def __init__(self, nactvar, firstlabel, firstgoto, isloop):
        self.nactvar = nactvar
        self.firstlabel = firstlabel
        self.firstgoto = firstgoto
        self.isloop = isloop


class FuncState:
    def __init__(self, prev, is_vararg):
        self.prev = prev
        self.is_vararg = is_vararg
        self.actvar = []   # locales activos: [nombre, tipo] (tipo: 'reg', 'const', 'close')
        self.labels = []   # [nombre, línea, nactvar]
        self.gotos = []    # [nombre, línea, nactvar]
        self.blocks = []


class Parser:
    def __init__(self, src, chunkname):
        self.lex = Lexer(src, chunkname)
        self.chunkname = chunkname
        self.t = self.lex.next_token()
        self.ahead = None
        self.fs = None

    # ---- utilidades de tokens ----
    @property
    def linenumber(self):
        return self.ahead.line if self.ahead is not None else self.t.line

    def next(self):
        if self.ahead is not None:
            self.t, self.ahead = self.ahead, None
        else:
            self.t = self.lex.next_token()

    def lookahead(self):
        if self.ahead is None:
            self.ahead = self.lex.next_token()
        return self.ahead.kind

    def near(self):
        k = self.t.kind
        if k in (NAME, STRING, NUMBER):
            return "'" + self.t.text + "'"
        return token2str(k)

    def syntax_error(self, msg):
        raise LuaSyntaxError(f"{self.chunkname}:{self.linenumber}: {msg} near {self.near()}")

    def sem_error(self, msg):
        raise LuaSyntaxError(f"{self.chunkname}:{self.linenumber}: {msg}", semantic=True)

    def error_expected(self, kind):
        self.syntax_error(f"{token2str(kind)} expected")

    def check(self, kind):
        if self.t.kind != kind:
            self.error_expected(kind)

    def checknext(self, kind):
        self.check(kind)
        self.next()

    def testnext(self, kind):
        if self.t.kind == kind:
            self.next()
            return True
        return False

    def check_match(self, what, who, where):
        if not self.testnext(what):
            if where == self.linenumber:
                self.error_expected(what)
            self.syntax_error(f"{token2str(what)} expected (to close {token2str(who)} at line {where})")

    def str_checkname(self):
        self.check(NAME)
        name = self.t.text
        self.next()
        return name

    def block_follow(self, withuntil):
        k = self.t.kind
        return k in ("else", "elseif", "end", EOS) or (k == "until" and withuntil)

    # ---- funciones, bloques, variables ----
    def open_func(self, is_vararg):
        self.fs = FuncState(self.fs, is_vararg)
        self.enterblock(False)

    def close_func(self):
        self.leaveblock()
        self.fs = self.fs.prev

    def enterblock(self, isloop):
        fs = self.fs
        fs.blocks.append(Block(len(fs.actvar), len(fs.labels), len(fs.gotos), isloop))

    def leaveblock(self):
        fs = self.fs
        bl = fs.blocks.pop()
        del fs.actvar[bl.nactvar:]  # quita los locales del bloque
        if bl.isloop:
            self.createlabel("break", 0, False, bl)
        del fs.labels[bl.firstlabel:]
        if fs.blocks:  # bloque anidado: los goto pendientes pasan al bloque exterior
            for g in fs.gotos[bl.firstgoto:]:
                if g[2] > bl.nactvar:
                    g[2] = bl.nactvar
        elif len(fs.gotos) > bl.firstgoto:
            name, line, _ = fs.gotos[bl.firstgoto]
            if name == "break":
                self.sem_error(f"break outside a loop at line {line}")
            self.sem_error(f"no visible label '{name}' for <goto> at line {line}")

    def new_localvar(self, name, kind="reg"):
        return [name, kind]

    def adjustlocalvars(self, vars_):
        self.fs.actvar.extend(vars_)

    def findlabel(self, name):
        for lb in self.fs.labels:
            if lb[0] == name:
                return lb
        return None

    def createlabel(self, name, line, last, bl=None):
        fs = self.fs
        bl = bl or fs.blocks[-1]
        nact = bl.nactvar if last else len(fs.actvar)
        lb = [name, line, nact]
        fs.labels.append(lb)
        # resuelve los goto pendientes del bloque actual con ese nombre
        i = bl.firstgoto
        while i < len(fs.gotos):
            g = fs.gotos[i]
            if g[0] == name:
                if g[2] < nact:
                    varname = fs.actvar[g[2]][0] if g[2] < len(fs.actvar) else "?"
                    self.sem_error(f"<goto {g[0]}> at line {g[1]} jumps into the scope of local '{varname}'")
                del fs.gotos[i]
            else:
                i += 1

    def singlevar_kind(self, name):
        """Tipo de la variable 'name' (local, upvalue) o None si es global."""
        fs = self.fs
        while fs is not None:
            for v in reversed(fs.actvar):
                if v[0] == name:
                    return v[1]
            fs = fs.prev
        return None

    # ---- reglas de la gramática ----
    def mainfunc(self):
        self.open_func(True)
        self.statlist()
        self.check(EOS)
        self.close_func()

    def statlist(self):
        while not self.block_follow(True):
            if self.t.kind == "return":
                self.statement()
                return
            self.statement()

    def block(self):
        self.enterblock(False)
        self.statlist()
        self.leaveblock()

    def statement(self):
        line = self.linenumber
        k = self.t.kind
        if k == ";":
            self.next()
        elif k == "if":
            self.ifstat(line)
        elif k == "while":
            self.next()
            self.expr()
            self.enterblock(True)
            self.checknext("do")
            self.block()
            self.check_match("end", "while", line)
            self.leaveblock()
        elif k == "do":
            self.next()
            self.block()
            self.check_match("end", "do", line)
        elif k == "for":
            self.forstat(line)
        elif k == "repeat":
            self.next()
            self.enterblock(True)
            self.enterblock(False)
            self.statlist()
            self.check_match("until", "repeat", line)
            self.expr()
            self.leaveblock()
            self.leaveblock()
        elif k == "function":
            self.next()
            name = self.str_checkname()
            simple = True
            while self.t.kind == ".":
                self.next()
                self.str_checkname()
                simple = False
            ismethod = False
            if self.t.kind == ":":
                self.next()
                self.str_checkname()
                ismethod = True
                simple = False
            self.body(ismethod, line)
            if simple and self.singlevar_kind(name) in ("const", "close"):
                self.sem_error(f"attempt to assign to const variable '{name}'")
        elif k == "local":
            self.next()
            if self.testnext("function"):
                name = self.str_checkname()
                self.adjustlocalvars([self.new_localvar(name)])
                self.body(False, self.linenumber)
            else:
                self.localstat()
        elif k == "::":
            self.next()
            name = self.str_checkname()
            self.checknext("::")
            while self.t.kind in (";", "::"):
                self.statement()
            if self.findlabel(name) is not None:
                self.sem_error(f"label '{name}' already defined on line {self.findlabel(name)[1]}")
            self.createlabel(name, line, self.block_follow(False))
        elif k == "return":
            self.next()
            if not (self.block_follow(True) or self.t.kind == ";"):
                self.explist()
            self.testnext(";")
        elif k == "break":
            self.next()
            self.fs.gotos.append(["break", line, len(self.fs.actvar)])
        elif k == "goto":
            self.next()
            line = self.linenumber
            name = self.str_checkname()
            if self.findlabel(name) is None:  # salto hacia adelante: se resuelve al ver la etiqueta
                self.fs.gotos.append([name, line, len(self.fs.actvar)])
        else:
            self.exprstat()

    def ifstat(self, line):
        self.test_then_block()
        while self.t.kind == "elseif":
            self.test_then_block()
        if self.testnext("else"):
            self.block()
        self.check_match("end", "if", line)

    def test_then_block(self):
        self.next()
        self.expr()
        self.checknext("then")
        self.block()

    def forstat(self, line):
        self.enterblock(True)
        self.next()
        varname = self.str_checkname()
        if self.t.kind == "=":
            self.next()
            self.expr()
            self.checknext(",")
            self.expr()
            if self.testnext(","):
                self.expr()
            internals = [self.new_localvar("(for state)") for _ in range(3)]
            names = [varname]
        elif self.t.kind in (",", "in"):
            names = [varname]
            while self.testnext(","):
                names.append(self.str_checkname())
            self.checknext("in")
            self.explist()
            internals = [self.new_localvar("(for state)") for _ in range(4)]
        else:
            self.syntax_error("'=' or 'in' expected")
        self.adjustlocalvars(internals)
        self.checknext("do")
        self.enterblock(False)
        self.adjustlocalvars([self.new_localvar(n) for n in names])
        self.block()
        self.leaveblock()
        self.check_match("end", "for", line)
        self.leaveblock()

    def localstat(self):
        vars_ = []
        has_close = False
        while True:
            name = self.str_checkname()
            kind = "reg"
            if self.testnext("<"):
                attr = self.str_checkname()
                self.checknext(">")
                if attr == "const":
                    kind = "const"
                elif attr == "close":
                    kind = "close"
                    if has_close:
                        self.sem_error("multiple to-be-closed variables in local list")
                    has_close = True
                else:
                    self.sem_error(f"unknown attribute '{attr}'")
            vars_.append(self.new_localvar(name, kind))
            if not self.testnext(","):
                break
        if self.testnext("="):
            self.explist()
        self.adjustlocalvars(vars_)

    def body(self, ismethod, line):
        self.open_func(False)
        if ismethod:
            self.adjustlocalvars([self.new_localvar("self")])
        self.checknext("(")
        params = []
        if self.t.kind != ")":
            while True:
                if self.t.kind == NAME:
                    params.append(self.new_localvar(self.str_checkname()))
                elif self.t.kind == "...":
                    self.next()
                    self.fs.is_vararg = True
                else:
                    self.syntax_error("<name> expected")
                if self.fs.is_vararg or not self.testnext(","):
                    break
        self.adjustlocalvars(params)
        self.checknext(")")
        self.statlist()
        self.check_match("end", "function", line)
        self.close_func()

    def exprstat(self):
        kind, name = self.suffixedexp()
        if self.t.kind in ("=", ","):
            self.restassign(kind, name)
        elif kind != "call":
            self.syntax_error("syntax error")

    def restassign(self, kind, name):
        if kind not in ("local", "index"):
            self.syntax_error("syntax error")
        if name is not None and self.singlevar_kind(name) in ("const", "close"):
            self.sem_error(f"attempt to assign to const variable '{name}'")
        if self.testnext(","):
            k2, n2 = self.suffixedexp()
            self.restassign(k2, n2)
        else:
            self.checknext("=")
            self.explist()

    def explist(self):
        self.expr()
        while self.testnext(","):
            self.expr()

    def expr(self, limit=0):
        if self.t.kind in UNARY_OPS:
            self.next()
            self.expr(UNARY_PRIORITY)
        else:
            self.simpleexp()
        op = self.t.kind
        while op in BINARY_PRIORITY and BINARY_PRIORITY[op][0] > limit:
            self.next()
            op = self.expr(BINARY_PRIORITY[op][1])
        return self.t.kind if self.t.kind in BINARY_PRIORITY else None

    def simpleexp(self):
        k = self.t.kind
        if k in (NUMBER, STRING, "nil", "true", "false"):
            self.next()
        elif k == "...":
            if not self.fs.is_vararg:
                self.syntax_error("cannot use '...' outside a vararg function")
            self.next()
        elif k == "{":
            self.constructor()
        elif k == "function":
            self.next()
            self.body(False, self.linenumber)
        else:
            self.suffixedexp()

    def primaryexp(self):
        k = self.t.kind
        if k == NAME:
            return "local", self.str_checkname()
        if k == "(":
            line = self.linenumber
            self.next()
            self.expr()
            self.check_match(")", "(", line)
            return "paren", None
        self.syntax_error("unexpected symbol")

    def suffixedexp(self):
        """Devuelve (tipo, nombre): tipo 'local' (nombre simple), 'index', 'call' o 'paren'."""
        line = self.linenumber
        kind, name = self.primaryexp()
        while True:
            k = self.t.kind
            if k == ".":
                self.next()
                self.str_checkname()
                kind, name = "index", None
            elif k == "[":
                self.next()
                self.expr()
                self.checknext("]")
                kind, name = "index", None
            elif k == ":":
                self.next()
                self.str_checkname()
                self.funcargs(line)
                kind, name = "call", None
            elif k in ("(", STRING, "{"):
                self.funcargs(line)
                kind, name = "call", None
            else:
                return kind, name

    def funcargs(self, line):
        k = self.t.kind
        if k == "(":
            self.next()
            if self.t.kind != ")":
                self.explist()
            self.check_match(")", "(", line)
        elif k == "{":
            self.constructor()
        elif k == STRING:
            self.next()
        else:
            self.syntax_error("function arguments expected")

    def constructor(self):
        line = self.linenumber
        self.checknext("{")
        while True:
            if self.t.kind == "}":
                break
            self.field()
            if not (self.testnext(",") or self.testnext(";")):
                break
        self.check_match("}", "{", line)

    def field(self):
        k = self.t.kind
        if k == NAME:
            if self.lookahead() != "=":
                self.expr()
            else:
                self.next()
                self.checknext("=")
                self.expr()
        elif k == "[":
            self.next()
            self.expr()
            self.checknext("]")
            self.checknext("=")
            self.expr()
        else:
            self.expr()


def check(source, chunkname="input", skip_shebang=False):
    """Devuelve None si el chunk compila, o (mensaje, es_error_semantico)."""
    if skip_shebang and source.startswith("#"):
        source = "--" + source[1:]  # como luaL_loadfile: se ignora una primera línea '#...'
    try:
        Parser(source, chunkname).mainfunc()
    except LuaSyntaxError as e:
        return e.msg, e.semantic
    except RecursionError:
        return chunkname + ": chunk has too many syntax levels", False
    return None
