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

class LuaTable:
    def __init__(self):
        self._data = {}
        self.metatable = None

    def _normalize_key(self, key):
        if key is None:
            raise LuaError("table index is nil")
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
        try:
            nk = self._normalize_key(key)
        except LuaError:
            return None
        val = self._data.get(nk, None)
        if isinstance(val, weakref.ref):
            return val()
        return val

    def rawset(self, key, value):
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
            valid_keys.append(real_k.obj if isinstance(real_k, _RefKey) else real_k)
        return valid_keys