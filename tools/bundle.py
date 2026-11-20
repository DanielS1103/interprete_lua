"""Genera submit/main.py: un único archivo autocontenido con todo el intérprete.

Sirve para plataformas que solo aceptan un archivo (p. ej. UNCode). El archivo contiene el
proyecto (main.py, interpreter.py, runtime/, grammar/*.py y el runtime de ANTLR) comprimido en
base64; al ejecutarse lo extrae a un directorio temporal y arranca el intérprete.

    python tools/bundle.py
    python submit/main.py < tests/01.in
"""
import base64
import os
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "submit")

INCLUDE_DIRS = ["antlr4", "runtime", "grammar"]
INCLUDE_FILES = {"interpreter.py": "interpreter.py", "main.py": "luamain.py"}

TEMPLATE = '''# Archivo generado por tools/bundle.py -- no editar a mano.
import base64, os, sys, tempfile, zlib

_FILES = {files!r}


def _extract():
    root = tempfile.mkdtemp(prefix="lua_interp_")
    for rel, data in _FILES.items():
        path = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(zlib.decompress(base64.b64decode(data)))
    return root


if __name__ == "__main__":
    _root = _extract()
    sys.path.insert(0, _root)
    import luamain
    sys.exit(luamain.start())
'''


def collect():
    files = {}
    for d in INCLUDE_DIRS:
        for base, _dirs, names in os.walk(os.path.join(ROOT, d)):
            if "__pycache__" in base:
                continue
            for n in names:
                if not n.endswith((".py", ".txt")):
                    continue
                full = os.path.join(base, n)
                rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
                files[rel] = full
    for src, dst in INCLUDE_FILES.items():
        files[dst] = os.path.join(ROOT, src)
    return files


def main():
    packed = {}
    for rel, full in sorted(collect().items()):
        with open(full, "rb") as f:
            packed[rel] = base64.b64encode(zlib.compress(f.read(), 9)).decode("ascii")
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "main.py")
    with open(out, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(files=packed))
    print(f"Generado {out} ({os.path.getsize(out) // 1024} KB, {len(packed)} archivos)")


if __name__ == "__main__":
    main()
