from runtime.exceptions import LuaError


class Environment:
    """Ámbito léxico (tabla de símbolos) con referencia al ámbito padre.

    Los nombres que no son locales ni upvalues son globales: se buscan en la tabla '_ENV'
    visible en ese punto. Normalmente es la del chunk ('env_table'), pero un 'local _ENV = t'
    o un parámetro llamado '_ENV' la reemplazan dentro de su ámbito (manual §2.2).
    """

    # Se activa la primera vez que se declara un local/parámetro '_ENV'; mientras sea False,
    # la búsqueda de globales no necesita recorrer la cadena buscando ese nombre.
    env_shadowed = False

    # Valores por defecto compartidos (la mayoría de los ámbitos no tiene <const>/<close>):
    # se crean por instancia solo cuando hacen falta, para que crear un ámbito sea barato.
    consts = frozenset()
    to_close = ()
    is_func = False  # True para el entorno raíz de una llamada a función (para 'local' vs 'upvalue')

    def __init__(self, parent=None, env_table=None):
        self.parent = parent
        self.vars = {}
        self.env_table = env_table  # _ENV del chunk (upvalue)

    def define_local(self, name, value, attrib=None):
        self.vars[name] = value
        if name == "_ENV":
            Environment.env_shadowed = True
        if attrib is None:
            if name in self.consts:  # redeclaración normal de un nombre que era <const>
                self.consts = self.consts - {name}
            return
        if attrib == "const" or attrib == "close":
            if not isinstance(self.consts, set):
                self.consts = set()
            self.consts.add(name)
        if attrib == "close" and value is not None:
            if not isinstance(self.to_close, list):
                self.to_close = []
            self.to_close.append((name, value))

    def reset_for_iteration(self):
        """Deja el ámbito vacío para reutilizarlo en la siguiente iteración de un bucle."""
        self.vars.clear()
        if self.consts:
            self.consts = frozenset()

    def current_env_table(self):
        """Valor de '_ENV' visible desde este ámbito (local/parámetro '_ENV' o el del chunk)."""
        env = self
        shadowed = Environment.env_shadowed
        while True:
            if shadowed and "_ENV" in env.vars:
                return env.vars["_ENV"]
            if env.parent is None:
                return env.env_table  # ámbito raíz = chunk: su env_table es el upvalue _ENV
            env = env.parent

    def get(self, name, lookup_table_fn):
        env = self
        while True:
            vars_ = env.vars
            if name in vars_:
                return vars_[name]
            parent = env.parent
            if parent is None:
                break
            env = parent
        # No es local ni upvalue: es un global, se busca en _ENV
        tab = self.current_env_table() if Environment.env_shadowed else env.env_table
        if name == "_ENV":
            return tab
        return lookup_table_fn(tab, name)

    def assign(self, name, value, assign_table_fn):
        env = self
        while True:
            vars_ = env.vars
            if name in vars_:
                if name in env.consts:
                    raise LuaError(f"attempt to assign to const variable '{name}'")
                vars_[name] = value
                return
            parent = env.parent
            if parent is None:
                break
            env = parent
        if name == "_ENV":
            env.env_table = value  # asigna el upvalue _ENV del chunk (afecta a todo el chunk)
            return
        tab = self.current_env_table() if Environment.env_shadowed else env.env_table
        assign_table_fn(tab, name, value)

    def close_scope(self, call_metamethod_fn, err=None):
        """Ejecuta __close en orden LIFO al salir de un bloque o tras un error."""
        while self.to_close:
            _, obj = self.to_close.pop()
            call_metamethod_fn(obj, "__close", [obj, err])
