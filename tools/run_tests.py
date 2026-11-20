"""Ejecuta los casos de prueba con main.py y compara con las salidas esperadas.

Suites:
  tests/*.in            -> tests/expected/*.out         (los 6 casos del taller)
  tests/extra/*.lua     -> tests/extra/expected/*.out   (pruebas adicionales de robustez)

Uso:
    python tools/run_tests.py            # compara
    python tools/run_tests.py --update   # regenera las salidas esperadas (revisarlas antes de aceptar)
    python tools/run_tests.py submit/main.py   # usa otro punto de entrada (versión de un solo archivo)

Las salidas esperadas se contrastaron con Lua 5.4 real; las únicas diferencias son cosméticas
(nombre de chunk "input" en los mensajes de error, nombres de función en algunos 'bad argument',
signo de nan en 1.0%0).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, "tests")
CRLF = b"\r\n"
LF = b"\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    update = "--update" in sys.argv
    entry = os.path.join(ROOT, args[0]) if args else os.path.join(ROOT, "main.py")
    suites = [
        (TESTS, ".in", os.path.join(TESTS, "expected")),
        (os.path.join(TESTS, "extra"), ".lua", os.path.join(TESTS, "extra", "expected")),
    ]
    failures = 0
    for folder, ext, exp_dir in suites:
        if not os.path.isdir(folder):
            continue
        os.makedirs(exp_dir, exist_ok=True)
        for name in sorted(f for f in os.listdir(folder) if f.endswith(ext)):
            case = name[: -len(ext)]
            with open(os.path.join(folder, name), "rb") as f:
                source = f.read()
            proc = subprocess.run([sys.executable, entry], input=source, capture_output=True, timeout=300)
            out = proc.stdout.replace(CRLF, LF)
            exp_path = os.path.join(exp_dir, case + ".out")
            if update:
                with open(exp_path, "wb") as f:
                    f.write(out)
                print(f"[actualizado] {case}")
                continue
            with open(exp_path, "rb") as f:
                expected = f.read().replace(CRLF, LF)
            if proc.returncode == 0 and out == expected:
                print(f"[ok]     {case}")
            else:
                failures += 1
                print(f"[FALLA]  {case} (código {proc.returncode})")
                if proc.stderr:
                    print("   stderr:", proc.stderr.decode("utf-8", "replace")[:300])
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
