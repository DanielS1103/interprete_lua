# Intérprete de Lua 5.4

Intérprete de **Lua 5.4** desarrollado en **Python 3** utilizando **ANTLR4** (patrón *Visitor*).

## Requisitos
* Python 3.8 o superior.

## Instalación

1. **Crear y activar el entorno virtual:**
   * **Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```


2. **Instalar dependencias:**
   ```bash
   pip install antlr4-python3-runtime
   ```
   *(También se puede usar `pip install -r requirements.txt`)*.

## Ejecución

* **Ejecutar un archivo específico:**
  ```bash
  python main.py tests/01.in
  ```

* **Ejecutar mediante entrada estándar (`stdin`):**
  ```bash
  python main.py < tests/01.in
  ```

* **Ejecutar todos los casos de prueba (`01.in` a `06.in`):**
  ```bash
  python main.py
  ```