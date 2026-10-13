"""
Chequeo de entorno -- Fase 1, paso 1.

Corre esto DESPUES de instalar requirements.txt:
    python tests/test_setup.py

Si pyworld falla en el paso de analisis/sintesis (no solo en el import),
es un problema de compilacion del binding en C++, no un typo en el codigo.
En Windows sin Build Tools de Visual Studio es el punto de falla mas comun.
"""

import sys


def check(nombre, fn):
    try:
        fn()
        print(f"[OK] {nombre}")
    except Exception as e:
        print(f"[FALLA] {nombre}: {e}")
        sys.exit(1)


def check_parselmouth():
    import parselmouth
    print(f"    version: {parselmouth.__version__}")


def check_flask():
    import importlib.metadata
    import flask  # noqa: F401
    print(f"    version: {importlib.metadata.version('flask')}")


def check_numpy_scipy():
    import numpy as np
    import scipy
    print(f"    numpy {np.__version__}, scipy {scipy.__version__}")


def check_pyworld_roundtrip():
    """No alcanza con importar pyworld -- hay que probar que el binding en
    C++ realmente compilo y corre, analizando y resintetizando una onda simple."""
    import numpy as np
    import pyworld as pw

    fs = 16000
    t = np.arange(0, 0.5, 1.0 / fs)
    x = (0.5 * np.sin(2 * np.pi * 150 * t)).astype(np.float64)

    f0, sp, ap = pw.wav2world(x, fs)
    y = pw.synthesize(f0, sp, ap, fs)

    assert len(y) > 0, "la sintesis devolvio una senal vacia"
    print(f"    analisis+sintesis OK -- {len(f0)} frames de F0 estimados")


if __name__ == "__main__":
    check("parselmouth (import)", check_parselmouth)
    check("flask (import)", check_flask)
    check("numpy + scipy (import)", check_numpy_scipy)
    check("pyworld (analisis + sintesis real, no solo import)", check_pyworld_roundtrip)
    print("\nEntorno listo para la Fase 1.")
