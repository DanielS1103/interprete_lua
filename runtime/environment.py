from runtime.exceptions import LuaError

class Environment:
    def __init__(self, parent=None, env_table=None):
        self.parent = parent
        self.vars = {}
        self.consts = set()
        self.to_close = []
        self.env_table = env_table  # Referencia a _ENV global

    def define_local(self, name, value, attrib=None):
        self.vars[name] = value
        if attrib == "const":
            self.consts.add(name)
        elif attrib == "close":
            self.consts.add(name)
            if value is not None:
                self.to_close.append((name, value))

    def get(self, name, lookup_table_fn):
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.get(name, lookup_table_fn)
        # Si no es local ni upvalue, busca en _ENV (variables globales)
        return lookup_table_fn(self.env_table, name)

    def assign(self, name, value, assign_table_fn):
        if name in self.vars:
            if name in self.consts:
                raise LuaError(f"attempt to assign to const variable '{name}'")
            self.vars[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value, assign_table_fn)
            return
        assign_table_fn(self.env_table, name, value)

    def close_scope(self, call_metamethod_fn, err=None):
        """Ejecuta __close en orden LIFO al salir de un bloque o tras un error."""
        while self.to_close:
            _, obj = self.to_close.pop()
            call_metamethod_fn(obj, "__close", [obj, err])