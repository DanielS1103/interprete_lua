"""Motor de patrones de Lua 5.4 (port de la lógica de match de lstrlib.c).

Trabaja sobre `str` donde cada carácter representa un byte (latin-1).
"""
from runtime.exceptions import LuaError

L_ESC = "%"
SPECIALS = "^$*+?.([%-"
CAP_UNFINISHED = -1
CAP_POSITION = -2
MAXCCALLS = 200
LUA_MAXCAPTURES = 32


def _isalpha(c): return ("a" <= c <= "z") or ("A" <= c <= "Z")
def _isdigit(c): return "0" <= c <= "9"
def _islower(c): return "a" <= c <= "z"
def _isupper(c): return "A" <= c <= "Z"
def _isspace(c): return c in " \t\n\r\f\v"
def _iscntrl(c): return ord(c) < 32 or ord(c) == 127
def _isgraph(c): return 32 < ord(c) < 127
def _ispunct(c): return _isgraph(c) and not (_isalpha(c) or _isdigit(c))
def _isalnum(c): return _isalpha(c) or _isdigit(c)
def _isxdigit(c): return _isdigit(c) or ("a" <= c <= "f") or ("A" <= c <= "F")


def match_class(c, cl):
    low = cl.lower()
    if low == "a": res = _isalpha(c)
    elif low == "c": res = _iscntrl(c)
    elif low == "d": res = _isdigit(c)
    elif low == "g": res = _isgraph(c)
    elif low == "l": res = _islower(c)
    elif low == "p": res = _ispunct(c)
    elif low == "s": res = _isspace(c)
    elif low == "u": res = _isupper(c)
    elif low == "w": res = _isalnum(c)
    elif low == "x": res = _isxdigit(c)
    else:
        return cl == c
    if _isupper(cl):
        res = not res
    return res


class MatchState:
    def __init__(self, src, pat):
        self.src = src
        self.pat = pat
        self.slen = len(src)
        self.plen = len(pat)
        self.level = 0
        self.capture = [[0, 0] for _ in range(LUA_MAXCAPTURES)]
        self.matchdepth = MAXCCALLS

    def reprep(self):
        self.level = 0
        self.matchdepth = MAXCCALLS

    # ---- utilidades de patrón ----
    def class_end(self, p):
        pat, plen = self.pat, self.plen
        if p >= plen:
            raise LuaError("malformed pattern (ends with '%')")
        c = pat[p]
        p += 1
        if c == L_ESC:
            if p >= plen:
                raise LuaError("malformed pattern (ends with '%')")
            return p + 1
        if c == "[":
            if p < plen and pat[p] == "^":
                p += 1
            while True:  # busca el ']'
                if p >= plen:
                    raise LuaError("malformed pattern (missing ']')")
                cc = pat[p]
                p += 1
                if cc == L_ESC and p < plen:
                    p += 1
                if p < plen and pat[p] == "]":
                    break
            return p + 1
        return p

    def match_bracket_class(self, c, p, ec):
        pat = self.pat
        sig = True
        if pat[p + 1] == "^":
            sig = False
            p += 1
        p += 1
        while p < ec:
            ch = pat[p]
            if ch == L_ESC:
                p += 1
                if match_class(c, pat[p]):
                    return sig
            elif p + 2 < ec and pat[p + 1] == "-":
                p += 2
                if pat[p - 2] <= c <= pat[p]:
                    return sig
            elif ch == c:
                return sig
            p += 1
        return not sig

    def single_match(self, s, p, ep):
        if s >= self.slen:
            return False
        c = self.src[s]
        pc = self.pat[p]
        if pc == ".":
            return True
        if pc == L_ESC:
            return match_class(c, self.pat[p + 1])
        if pc == "[":
            return self.match_bracket_class(c, p, ep - 1)
        return pc == c

    def match_balance(self, s, p):
        if p + 1 >= self.plen:
            raise LuaError("malformed pattern (missing arguments to '%b')")
        if s >= self.slen or self.src[s] != self.pat[p]:
            return -1
        b, e = self.pat[p], self.pat[p + 1]
        cont = 1
        s += 1
        while s < self.slen:
            c = self.src[s]
            if c == e:
                cont -= 1
                if cont == 0:
                    return s + 1
            elif c == b:
                cont += 1
            s += 1
        return -1

    def max_expand(self, s, p, ep):
        i = 0
        while self.single_match(s + i, p, ep):
            i += 1
        while i >= 0:
            res = self.match(s + i, ep + 1)
            if res != -1:
                return res
            i -= 1
        return -1

    def min_expand(self, s, p, ep):
        while True:
            res = self.match(s, ep + 1)
            if res != -1:
                return res
            if self.single_match(s, p, ep):
                s += 1
            else:
                return -1

    def start_capture(self, s, p, what):
        if self.level >= LUA_MAXCAPTURES:
            raise LuaError("too many captures")
        self.capture[self.level][0] = s
        self.capture[self.level][1] = what
        self.level += 1
        res = self.match(s, p)
        if res == -1:
            self.level -= 1
        return res

    def end_capture(self, s, p):
        l = self.capture_to_close()
        self.capture[l][1] = s - self.capture[l][0]
        res = self.match(s, p)
        if res == -1:
            self.capture[l][1] = CAP_UNFINISHED
        return res

    def capture_to_close(self):
        level = self.level - 1
        while level >= 0:
            if self.capture[level][1] == CAP_UNFINISHED:
                return level
            level -= 1
        raise LuaError("invalid pattern capture")

    def check_capture(self, ch):
        l = int(ch) - 1
        if l < 0 or l >= self.level or self.capture[l][1] == CAP_UNFINISHED:
            raise LuaError(f"invalid capture index %{l + 1}")
        return l

    def match_capture(self, s, ch):
        l = self.check_capture(ch)
        init, length = self.capture[l]
        if self.slen - s >= length and self.src[init:init + length] == self.src[s:s + length]:
            return s + length
        return -1

    # ---- núcleo ----
    def match(self, s, p):
        self.matchdepth -= 1
        if self.matchdepth == 0:
            raise LuaError("pattern too complex")
        try:
            pat, plen = self.pat, self.plen
            while True:
                if p >= plen:
                    return s
                c = pat[p]
                if c == "(":
                    if p + 1 < plen and pat[p + 1] == ")":
                        return self.start_capture(s, p + 2, CAP_POSITION)
                    return self.start_capture(s, p + 1, CAP_UNFINISHED)
                if c == ")":
                    return self.end_capture(s, p + 1)
                if c == "$" and p + 1 == plen:
                    return s if s == self.slen else -1
                if c == L_ESC and p + 1 < plen:
                    nc = pat[p + 1]
                    if nc == "b":
                        s = self.match_balance(s, p + 2)
                        if s != -1:
                            p += 4
                            continue
                        return -1
                    if nc == "f":
                        p += 2
                        if p >= plen or pat[p] != "[":
                            raise LuaError("missing '[' after '%f' in pattern")
                        ep = self.class_end(p)
                        prev = self.src[s - 1] if s > 0 else "\0"
                        cur = self.src[s] if s < self.slen else "\0"
                        if (not self.match_bracket_class(prev, p, ep - 1)) and self.match_bracket_class(cur, p, ep - 1):
                            p = ep
                            continue
                        return -1
                    if _isdigit(nc):
                        s = self.match_capture(s, nc)
                        if s != -1:
                            p += 2
                            continue
                        return -1
                # caso por defecto
                ep = self.class_end(p)
                epc = pat[ep] if ep < plen else ""
                if epc == "?":
                    if self.single_match(s, p, ep):
                        res = self.match(s + 1, ep + 1)
                        if res != -1:
                            return res
                    p = ep + 1
                    continue
                if epc == "+":
                    return self.max_expand(s + 1, p, ep) if self.single_match(s, p, ep) else -1
                if epc == "*":
                    return self.max_expand(s, p, ep)
                if epc == "-":
                    return self.min_expand(s, p, ep)
                if self.single_match(s, p, ep):
                    s += 1
                    p = ep
                    continue
                return -1
        finally:
            self.matchdepth += 1

    # ---- capturas ----
    def get_onecapture(self, i, s, e):
        if i >= self.level:
            if i != 0:
                raise LuaError(f"invalid capture index %{i + 1}")
            return self.src[s:e]
        init, l = self.capture[i]
        if l == CAP_UNFINISHED:
            raise LuaError("unfinished capture")
        if l == CAP_POSITION:
            return init + 1
        return self.src[init:init + l]

    def get_captures(self, s, e, whole_if_none=True):
        n = self.level if (self.level != 0 or not whole_if_none) else 1
        return [self.get_onecapture(i, s, e) for i in range(n)]


def has_specials(pat):
    return any(c in SPECIALS for c in pat)
