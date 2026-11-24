import math
import weakref
from runtime.exceptions import LuaError

class MultiRes(list):
    """Representa múltiples valores retornados por una función o '...'."""
    pass

def unwrap_one(val):
    """Ajusta una expresión a 1 solo valor (para paréntesis o argumentos intermedios)."""
    if isinstance(val, MultiRes):
        return val[0] if len(val) > 0 else None
    return val

def expand_args(raw_list):
    """Expande MultiRes solo si está en la última posición de una lista de expresiones."""
    if not raw_list:
        return []
    result = [unwrap_one(v) for v in raw_list[:-1]]
    last = raw_list[-1]
    if isinstance(last, MultiRes):
        result.extend(last)
    else:
        result.append(last)
    return result

class _RefKey:
    """Envuelve objetos mutables (tablas, funciones) para usarlos como llaves por identidad."""
    def __init__(self, obj):
        self.obj = obj
    def __hash__(self):
        return object.__hash__(self.obj)
    def __eq__(self, other):
        if isinstance(other, _RefKey):
            return self.obj is other.obj
        if isinstance(other, weakref.ref):
            return other() is self.obj
        return False

class _BoolKey:
    """Centinela para llaves booleanas (en Python True == 1 y False == 0)."""
    def __init__(self, value):
        self.value = value

_TRUE_KEY = _BoolKey(True)
_FALSE_KEY = _BoolKey(False)

class LuaTable:
    def __init__(self):
        self._data = {}
        self.metatable = None
        self.asize = 0  # tamaño de la parte "array" fijado por el constructor (emula luaH_getn)
        self.hint = 0   # último border calculado (evita recorrer la secuencia en cada '#')

    def _normalize_key(self, key):
        if key is None:
            raise LuaError("table index is nil")
        if key is True:
            return _TRUE_KEY
        if key is False:
            return _FALSE_KEY
        if isinstance(key, float):
            if math.isnan(key):
                raise LuaError("table index is NaN")
            if key.is_integer():
                return int(key)
        if isinstance(key, (LuaTable, dict, list)) or callable(key):
            return _RefKey(key)
        return key

    def _get_mode(self):
        if isinstance(self.metatable, LuaTable):
            mode = self.metatable.rawget("__mode")
            if isinstance(mode, str):
                return mode
        return ""

    def rawget(self, key):
        tk = type(key)
        if tk is str or tk is int:  # camino rápido (los más frecuentes)
            val = self._data.get(key)
            if val.__class__ is weakref.ref:
                return val()
            return val
        try:
            nk = self._normalize_key(key)
        except LuaError:
            return None
        val = self._data.get(nk, None)
        if isinstance(val, weakref.ref):
            return val()
        return val

    def rawset(self, key, value):
        tk = type(key)
        if (tk is str or tk is int) and self.metatable is None:  # camino rápido
            if value is None:
                self._data.pop(key, None)
            else:
                self._data[key] = value
            return
        nk = self._normalize_key(key)
        if value is None:
            self._data.pop(nk, None)
            return
        mode = self._get_mode()
        if "k" in mode and isinstance(nk, _RefKey):
            # Si la llave débil es recolectada por el GC, se elimina la entrada automáticamente
            nk = weakref.ref(nk.obj, lambda ref: self._data.pop(ref, None))
        if "v" in mode and isinstance(value, (LuaTable, dict, list)):
            value = weakref.ref(value, lambda ref, k=nk: self._data.pop(k, None))
        self._data[nk] = value

    def keys(self):
        valid_keys = []
        for k, v in list(self._data.items()):
            real_k = k() if isinstance(k, weakref.ref) else k
            real_v = v() if isinstance(v, weakref.ref) else v
            if real_k is None or real_v is None:
                self._data.pop(k, None)
                continue
            if isinstance(real_k, _RefKey):
                real_k = real_k.obj
            elif isinstance(real_k, _BoolKey):
                real_k = real_k.value
            valid_keys.append(real_k)
        return valid_keys

    def length(self):
        """Longitud 'border' como luaH_getn de Lua 5.4 (considera el tamaño del array del constructor)."""
        n = self.asize
        if n > 0 and self.rawget(n) is None:
            # el último elemento del array es nil: búsqueda binaria de un border en [0, n]
            i, j = 0, n
            while j - i > 1:
                m = (i + j) // 2
                if self.rawget(m) is None:
                    j = m
                else:
                    i = m
            return i
        h = self.hint
        if h < n:
            h = n
        while h > n and self.rawget(h) is None:  # la tabla se redujo: bajar hasta un border válido
            h -= 1
        while self.rawget(h + 1) is not None:
            h += 1
        self.hint = h
        return h

# ---------------------------------------------------------------------------
# Finalizadores (__gc): una tabla cuya metatabla tiene '__gc' al llamar a setmetatable
# pasa a ser LuaTableGC. Cuando Python detecta que es inalcanzable llama a __del__, que la
# "resucita" en GC_READY; el finalizador Lua se ejecuta en el siguiente collectgarbage()
# o al terminar el programa (como lua_close).
# ---------------------------------------------------------------------------
GC_READY = []
GC_CLOSED = [False]


class LuaTableGC(LuaTable):
    def __del__(self):
        if not GC_CLOSED[0] and not getattr(self, "_gc_done", False):
            GC_READY.append(self)
