class LuaControlFlow(BaseException):
    pass

class LuaReturn(LuaControlFlow):
    def __init__(self, values):
        self.values = values  # Lista de valores retornados

class LuaBreak(LuaControlFlow):
    pass

class LuaGoto(LuaControlFlow):
    def __init__(self, label):
        self.label = label

class LuaError(Exception):
    def __init__(self, message):
        self.lua_obj = message  # En Lua error() puede recibir strings o tablas (ej. xpcall en 01.in)
        super().__init__(str(message))

class LuaTailCall(LuaControlFlow):
    """'return f(args)': la llamada se hace desde LuaFunction.call reutilizando el marco
    (llamada de cola propia, §3.4.10), así la recursión de cola no tiene límite."""
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args


def make_lua_error(msg):
    """Crea un LuaError sin ejecutar código Python (útil cuando la pila está agotada)."""
    e = LuaError.__new__(LuaError)
    e.lua_obj = msg
    e.args = (msg,)
    return e
