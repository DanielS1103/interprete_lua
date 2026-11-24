# Intérprete de Lua 5.4 en Python

Trabajo de **Intérprete/Traductor de Lua** (asignación en UNCode). Se entrega un **intérprete** de Lua 5.4
escrito en **Python 3**: el análisis léxico y sintáctico lo hace un parser generado con **ANTLR 4.13.2**
(gramática en [grammar/](grammar/)) y la ejecución es un recorrido del árbol con el patrón *Visitor*
([interpreter.py](interpreter.py)).

## Integrantes

| Nombre | Correo / usuario |
|---|---|
| _Daniel Alejandro Acosta Avila_ | _dacostaav@unal.edu.co_ |
| _<nombre 2>_ | _<correo>_ |
| _<nombre 3>_ | _<correo>_ |

> Completar antes de la entrega. Recordar que **solo una persona** del grupo realiza los envíos.

## Requisitos y ejecución

* **Python 3.8 o superior** (probado con 3.12). No hace falta instalar nada: el runtime de ANTLR (Python puro) viene incluido
  en la carpeta [antlr4/](antlr4/) (licencia BSD en [antlr4/LICENSE.txt](antlr4/LICENSE.txt)).

```bash
# Entrada estándar (como en UNCode)
python main.py < tests/01.in

# Un archivo (o varios)
python main.py tests/01.in

# Sin argumentos y sin stdin redirigido: ejecuta tests/01.in ... tests/06.in
python main.py
```

El programa lee el código Lua completo por la entrada estándar, lo ejecuta y escribe la salida en la salida
estándar. Si el programa Lua termina con un error no capturado, escribe `lua: <mensaje>` en stderr y
devuelve el código de salida 1.

### Versión de un solo archivo

Si la plataforma solo admite un archivo, `python tools/bundle.py` genera `submit/main.py` (≈ 260 KB),
que contiene todo el intérprete (incluido ANTLR) y se usa igual: `python submit/main.py < tests/01.in`.

### Pruebas

```bash
python tools/run_tests.py            # ejecuta tests/01.in..06.in y compara con tests/expected/*.out
python tools/run_tests.py submit/main.py   # lo mismo con la versión de un solo archivo
```

## Estructura

| Ruta | Contenido |
|---|---|
| [main.py](main.py) | Punto de entrada: lee stdin/archivos, ejecuta en un hilo con pila grande, reporta errores. |
| [interpreter.py](interpreter.py) | `LuaInterpreter` (visitor del árbol ANTLR): sentencias, expresiones, funciones, metamétodos, `goto`, `<close>`… |
| [runtime/values.py](runtime/values.py) | `LuaTable` (tablas con llaves débiles/valores débiles, longitud tipo `luaH_getn`), `MultiRes` (valores múltiples). |
| [runtime/environment.py](runtime/environment.py) | Ámbitos léxicos, variables `<const>` y `<close>`, resolución de globales a través de `_ENV`. |
| [runtime/luacheck.py](runtime/luacheck.py) | Verificador estático (léxico, sintáctico y semántico) que replica `llex.c`/`lparser.c` para dar los mismos mensajes de error de compilación que Lua. |
| [runtime/stdlib.py](runtime/stdlib.py) | Librería estándar: base, `string`, `table`, `math`, `os`, `io`, `coroutine`. |
| [runtime/lpattern.py](runtime/lpattern.py) | Patrones de Lua (`find`, `match`, `gmatch`, `gsub`), portados de `lstrlib.c`. |
| [grammar/](grammar/) | Gramática ANTLR (`.g4`) y parser/lexer generados. |
| [antlr4/](antlr4/) | Runtime de ANTLR 4.13.2 (Python puro) incluido para no depender de `pip`. |
| [tests/](tests/) | Los 6 casos de prueba (`*.in`) y sus salidas esperadas (`expected/*.out`). |
| [tools/](tools/) | `run_tests.py` (pruebas) y `bundle.py` (genera la versión de un solo archivo). |

## Características cubiertas

Todo lo que ejercitan los 6 casos de prueba, y más:

* **Tipos y valores**: `nil`, booleanos, enteros de 64 bits (con *wrap-around*) y floats, strings (como
  secuencias de bytes), tablas, funciones, corrutinas y *userdata* (`io.stdin`). Formato de números igual a
  Lua (`%.14g`, `1e+100`, `10/2 → 5.0`, `inf`, `-nan`).
* **Léxico**: comentarios cortos/largos, strings con todas las secuencias de escape (`\n`, `\x41`, `\066`,
  `\u{2603}`, `\z`, continuación de línea), strings largos `[==[ ]==]`, enteros/hex/floats/hex-floats.
* **Variables y ámbitos**: locales, globales (a través de `_ENV`/`_G`), `local _ENV = t`, parámetros
  `_ENV` y asignación `_ENV = t` (§2.2), *closures* y *upvalues* por iteración de bucle, asignación múltiple
  con evaluación estricta de índices, `<const>` y `<close>` (se cierran al salir del bloque, del chunk o por
  error; un valor sin `__close` da `variable 'x' got a non-closable value`).
* **Control de flujo**: `if/elseif/else`, `while`, `repeat…until`, `for` numérico (entero y float) y
  genérico, `break`, `goto` y etiquetas.
* **Operadores** con la precedencia y asociatividad de Lua: aritméticos (`+ - * / // % ^`, división entera y
  módulo hacia −∞), bit a bit (`& | ~ << >> ~`), relacionales, lógicos con cortocircuito, concatenación y
  longitud `#`; coerción string↔número.
* **Funciones**: variádicas (`...`), valores de retorno múltiples y su ajuste (paréntesis, truncamiento,
  expansión al final), llamadas con string/tabla literal, métodos `obj:m()` y `function a.b:m()`,
  recursión profunda (decenas de miles de niveles) y **llamadas de cola propias** (`return f(x)` no
  consume pila, §3.4.10).
* **Metatablas**: `__index`, `__newindex`, `__call`, `__tostring`, `__len`, `__eq`, `__lt`, `__le`, `__concat`,
  todos los aritméticos y bit a bit, `__unm`, `__bnot`, `__close`, `__metatable`, `__pairs`, `__name`,
  `__mode` (tablas débiles) y `__gc` (finalizadores: se ejecutan en `collectgarbage()` y al terminar el
  programa, en orden inverso al de marcado, como `lua_close`).
* **Errores**: `error`, `pcall`, `xpcall` (con objetos de error arbitrarios), `assert`; los mensajes de
  error de ejecución imitan los de Lua, con posición y nombre de variable
  (`input:7: attempt to index a nil value (field 'x')`).
* **Corrutinas**: `create`, `resume`, `yield`, `status`, `wrap`, `isyieldable`, `running`, `close`
  (implementadas con hilos).
* **`load`** con cadenas (y funciones), con entorno opcional. Los errores de compilación se devuelven con
  los mensajes de Lua (`[string "x = "]:1: unexpected symbol near <eof>`, `'end' expected (to close
  'function' at line 1) near <eof>`, `attempt to assign to const variable 'x'`, `no visible label 'l' for
  <goto> at line 1`, `break outside a loop at line 1`…).
* **Librería estándar**: `print`, `type`, `tostring`, `tonumber`, `select`, `pairs`, `ipairs`, `next`,
  `rawget/rawset/rawequal/rawlen`, `getmetatable/setmetatable`, `collectgarbage`; `string.*` (incluye
  `format`, `find`, `match`, `gmatch`, `gsub`, `rep`, `sub`, `byte`, `char`…, también como métodos
  `("x"):upper()`, y `pack`/`unpack`/`packsize`), `table.*` (`insert`, `remove`, `concat`, `sort`, `unpack`,
  `pack`, `move`), `math.*` (incluye `deg`, `rad`, `ult`, `tointeger` y `random` con el generador xoshiro256**
  de Lua), `utf8.*` (`char`, `len`, `codepoint`, `codes`, `offset`, `charpattern`), `collectgarbage` con todas
  sus opciones, `os.time/clock/date/getenv/exit`, `io.write/read/lines`, `io.stdout:write`.

## Detalles de implementación

* **Strings como bytes**: la entrada se lee en bytes y cada byte se modela como un carácter (`latin-1`), igual
  que Lua; así `#"ñ" == 2` y la salida reproduce exactamente los bytes UTF-8 del programa, sin depender de la
  codificación de la consola de la plataforma.
* **Recursión**: el intérprete se ejecuta en un hilo con pila grande y las llamadas Lua no pasan por `__call__`
  (Python 3.12 limita la recursión de C), por lo que se soportan unos 30 000 niveles de recursión normal; la
  recursión infinita produce `input:N: stack overflow` capturable con `pcall`. Las llamadas de cola se
  ejecutan en un bucle dentro de `LuaFunction.call` (excepción de control `LuaTailCall`), sin límite.
* **Errores de compilación**: si ANTLR rechaza el programa, [luacheck.py](runtime/luacheck.py) produce el
  mensaje exacto de Lua y no se ejecuta nada (como el `lua` oficial). En `load` se usa siempre, porque también
  detecta los errores semánticos que Lua comprueba al compilar.
* **`table.sort`** usa el mismo quicksort que `ltablib.c` (mismas comparaciones e intercambios), así que el
  orden de los elementos "empatados" coincide con el de Lua; `math.random` usa xoshiro256** como `lmathlib.c`.
* **Rendimiento**: la clasificación de cada nodo del árbol se calcula una sola vez y se cachea, las
  operaciones numéricas más comunes tienen un camino rápido, las expresiones se despachan directamente (sin
  el `accept` genérico de ANTLR) y los bucles reutilizan el ámbito de cada iteración cuando su cuerpo no crea
  *closures*.
* **Precedencia**: la gramática original (grammars-v4) ponía los operadores bit a bit con la menor
  precedencia; se corrigió en [LuaParser.g4](grammar/LuaParser.g4) (`or < and < comparación < | < ~ < & <
  << >> < .. < + - < * / // % < unarios < ^`) y se regeneró el parser con ANTLR 4.13.2.

## Marco teórico: relación con el curso de Procesadores de Lenguaje

El trabajo corresponde a la fase de **análisis semántico** del esquema clásico de un compilador (léxico →
sintáctico → semántico → código intermedio → optimización → código objeto). Aquí se implementó la variante de
**intérprete**: el árbol sintáctico se recorre y se *ejecuta* directamente, por lo que **no se genera código
intermedio** (la clase sobre código intermedio se usa abajo como contraste). Correspondencia entre los conceptos
vistos en clase y el código:

### Análisis léxico y sintáctico: ANTLR

* [LuaLexer.g4](grammar/LuaLexer.g4) define los *tokens* (la fase léxica) y [LuaParser.g4](grammar/LuaParser.g4)
  la gramática libre de contexto; ANTLR genera un analizador **descendente recursivo** (una función por regla)
  con predicción ALL(*).
* En clase, una gramática con recursividad por la izquierda (`E → E op T`) hay que transformarla para un ASDR
  (`E → T E'`, `E' → op T E' | ε`). ANTLR 4 **reescribe automáticamente la recursividad directa por la
  izquierda** de la regla `exp`, por eso la gramática se puede escribir como `exp ('+'|'-') exp`.
* La **precedencia** se define por el *orden* de las alternativas de `exp` (las primeras ligan más fuerte) y la
  **asociatividad por la derecha** de `^` y `..` con `<assoc = right>`. Escribir mal ese orden es un error de
  diseño de la gramática, no de la semántica: eso fue lo que se corrigió con los operadores bit a bit.
* [runtime/luacheck.py](runtime/luacheck.py) es además un **ASDR escrito a mano**, igual al de la clase: un
  analizador léxico (`Lexer.next_token`, como `llex.c`) y una función por no terminal (`statement`, `expr`,
  `suffixedexp`, `funcargs`…, como `lparser.c`). La recursividad por la izquierda de las expresiones se resuelve
  con el bucle de `expr` y una tabla de prioridades (izquierda/derecha) por operador. Su única tarea es
  **detectar y describir errores** con el texto de Lua (`'then' expected near 'print'`, `unexpected symbol
  near <eof>`…): el árbol que se ejecuta sigue siendo el de ANTLR.

### Gramática de atributos, DDS y ETDS

* **Árbol decorado en dos pasadas.** De las dos formas de implementar un traductor vistas en clase, este
  intérprete usa la primera: el *parser* construye el árbol (primera pasada) y luego `LuaInterpreter`, un
  *visitor* ([interpreter.py](interpreter.py)), lo recorre calculando los atributos (segunda pasada). No se
  traduce/ejecuta "al vuelo" durante el análisis (una sola pasada) porque un mismo subárbol se ejecuta muchas
  veces (cuerpos de bucles y de funciones) y porque un `goto` puede saltar a una etiqueta posterior.
* **Atributos sintetizados** = lo que devuelve cada método `visitXxx`: `visitExp` devuelve el valor de la
  expresión; `visitTableconstructor`, la tabla; una llamada, un valor o un `MultiRes` (lista de valores, el
  atributo "traducción" de las llamadas con varios resultados).
* **Atributos heredados** = el contexto que baja desde el padre: el ámbito actual (`self.current_env`) y la línea
  actual (`self.cur_line`). En un ETDS con ASDR serían parámetros de la función del no terminal (como `L(th)` de
  la clase); aquí viven en el estado del intérprete porque el recorrido es el que fija el orden.
* **El orden de las acciones importa** (es lo que distingue un ETDS de una DDS). Ejemplo real en los tests: en
  `i, t[i] = i + 1, 20` primero se evalúan los *lvalues* (`t[i]` con `i = 1`) y después las expresiones de la
  derecha, así que el resultado es `i = 2, t[1] = 20`, no `t[2]`. Está en `_resolve_lvalue` y en la rama
  `assign` de `visitStat`.
* **Atributos cacheados en el árbol.** `_exp_info`, `_stat_info`, `_node_kind` y `_eval_args` calculan una sola
  vez la "decoración" de cada nodo (tipo de expresión, operador, literal ya convertido) y la guardan en el propio
  nodo; es la idea del árbol decorado, usada aquí como optimización.

### Tabla de símbolos y ámbitos anidados

* [runtime/environment.py](runtime/environment.py) implementa la **pila de tablas de símbolos**: cada
  `Environment` tiene su diccionario `vars` y una referencia al padre (`parent`); `get`/`assign` buscan en la
  tabla actual y, si no está, recursivamente en la del ámbito padre (la segunda alternativa de implementación
  vista en clase). `visitBlock` abre un ámbito al entrar a un bloque y lo "olvida" al salir, igual que el ETDS de
  gestión de ámbitos (`tsActual = new TablaSimbolos(tsActual)` / `tsActual.pop()`).
* `define_local` equivale a `nuevoSimbolo` / `anadirTS` de la DDS de declaraciones (`local a, b = ...` es el
  análogo de `D → T id L`), y `get` a `buscarSimbolo`. Como el nombre se resuelve **en tiempo de ejecución**,
  aquí no existe el "error semántico por variable no declarada": una variable no declarada es una **global**
  (se busca en la tabla `_ENV`) y vale `nil`.
* Los *atributos de variable* `<const>` y `<close>` son campos extra del símbolo (`consts`, `to_close`);
  asignar a una `<const>` es un **error semántico de compilación**: `luacheck.py` mantiene su propia tabla de
  símbolos (locales activos por función y por bloque, con su atributo) y lo detecta antes de ejecutar, igual
  que las etiquetas de `goto` no visibles, `break` fuera de un bucle o `...` fuera de una función variádica.
* Los *closures* funcionan porque cada función guarda la referencia a su `Environment` de definición
  (`closure_env`), no una copia; por eso, si el cuerpo de un bucle crea funciones, cada iteración usa un ámbito
  nuevo con su propia variable (si no las crea, el ámbito se reutiliza: ningún closure puede notarlo).
* `_ENV` es un nombre más de la tabla de símbolos: un `local _ENV` o un parámetro `_ENV` cambia la tabla en la
  que se buscan los globales de su ámbito; si no hay ninguno, se usa el `_ENV` del chunk.

### Sistema de tipos y expresiones

* Lua es de **tipado dinámico**: no se calcula `E.tipo` durante el análisis (como en el ETDS de enteros/reales
  de la clase), sino que cada operador comprueba y convierte los tipos **al ejecutarse**. `_arith` es el
  análogo de la tabla de conversiones de la clase: `int op int → int`, cualquier otra combinación numérica `→
  float` (equivale a insertar `conv.r8`/`ITOR`), y los strings se convierten a número antes de operar
  (`"10" + 5 → 15`). El error semántico "no se puede mezclar esos tipos" pasa a ser un error en ejecución:
  `attempt to perform arithmetic on a nil value`.
* Ejemplo de la clase, `a = 2.3 + 3*4.5 - 7.2*(3*4.5)`: en Lua `3*4.5` ya es `float` (13.5) y el resultado es
  `-81.4`; mientras que `3*3` sigue siendo `integer`. El compilador estático de la clase habría emitido
  `ITOR`/`conv.r8` para el `3`; el intérprete lo hace dentro de `_arith`.
* **Operadores booleanos.** En C todo valor distinto de 0 es verdadero y en Pascal solo existen `true`/`false`;
  Lua es un tercer caso: **solo `nil` y `false` son falsos** (`0` y `""` son verdaderos). `and` y `or` usan
  **evaluación en cortocircuito** (la opción 2 de la clase: `A and B → if A then B`) y devuelven *uno de sus
  operandos*, no un booleano (`nil or "x" → "x"`); está en la rama `and`/`or` de `visitExp`, que no evalúa el
  segundo operando si no hace falta.
* **Operadores relacionales.** En CIL solo existen `ceq`, `cgt`, `clt`, y `>=` se obtiene negando `clt`
  (`not(v1 < v2)`). Esa equivalencia **no es válida con `NaN`**: `not (0/0 < 0/0)` es `true`, pero
  `0/0 >= 0/0` debe ser `false`. Por eso `_lua_compare` compara directamente (y, para metamétodos, Lua define
  `a > b` como `b < a`, y `a >= b` como `b <= a`, con `__lt`/`__le`).

### Instrucciones de control de flujo (comparación con el código intermedio)

En el código intermedio de la clase las estructuras de control se traducen a saltos con etiquetas (`beq L1`,
`br L2`). Un intérprete de árbol no tiene "saltos" sino recursión y excepciones de control (definidas en
[runtime/exceptions.py](runtime/exceptions.py)):

| Instrucción | En código intermedio (clase) | En este intérprete |
|---|---|---|
| `if / elseif / else` | `ldc.i4 0; beq L1 … br L2` | se evalúan las condiciones en orden y se ejecuta el primer bloque verdadero |
| `while` | `L1: cond; beq L2; cuerpo; br L1; L2:` | bucle `while` de Python; `break` lanza `LuaBreak` |
| `repeat … until` | cuerpo; condición; salto atrás | igual, pero la condición **ve las locales del cuerpo** (mismo ámbito) |
| `for` numérico | `Expr1; L1: Expr2; beq L2; Instr; Expr3; br L1` (el `for` de C del ejercicio) | el inicio, límite y paso se evalúan **una vez**; cada iteración crea un ámbito nuevo con la variable de control |
| `goto` / etiqueta | `br Etiqueta` | `goto` lanza `LuaGoto`; `visitBlock` la atrapa y continúa desde el índice de la etiqueta |
| asignación | `Expr.cod; stloc pos` | `Environment.assign`; las tablas pasan por `_table_set` (metamétodo `__newindex`) |
| `print` / entrada | `Console.Write` / `ReadLine` | `print` → `write_out`; `io.read` lee de `stdin` |
