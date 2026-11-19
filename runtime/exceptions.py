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