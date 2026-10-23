"""
Chequeo de entorno.

Corre esto DESPUES de instalar requirements.txt:
    python tests/test_setup.py

Para parselmouth no alcanza con el import: se estima el pitch de una onda
sintetica de 150 Hz y se verifica que el resultado tenga sentido.
"""

import sys


def check(nombre, fn):
    try:
        fn()
        print(f"[OK] {nombre}")
    except Exception as e:
        print(f"[FALLA] {nombre}: {e}")
        sys.exit(1)


def check_numpy_scipy():
    import numpy as np
    import scipy
    print(f"    numpy {np.__version__}, scipy {scipy.__version__}")


def check_pandas():
    import pandas as pd
    print(f"    version: {pd.__version__}")


def check_pytest():
    import pytest
    print(f"    version: {pytest.__version__}")


def check_parselmouth_pitch():
    """Estima el pitch de una onda de 150 Hz y exige que caiga entre 145 y 155 Hz."""
    import numpy as np
    import parselmouth

    print(f"    version: {parselmouth.__version__}")

    fs = 16000
    t = np.arange(0, 0.5, 1.0 / fs)
    x = 0.5 * np.sin(2 * np.pi * 150 * t)

    sonido = parselmouth.Sound(x, sampling_frequency=fs)
    f0 = sonido.to_pitch().selected_array["frequency"]
    f0 = f0[f0 > 0]  # frames sordos devuelven 0

    assert len(f0) > 0, "no se detecto ningun frame sonoro"
    mediana = float(np.median(f0))
    assert 145 <= mediana <= 155, f"pitch estimado {mediana:.1f} Hz, se esperaba ~150 Hz"
    print(f"    pitch estimado: {mediana:.1f} Hz sobre {len(f0)} frames sonoros")


if __name__ == "__main__":
    check("numpy + scipy (import)", check_numpy_scipy)
    check("pandas (import)", check_pandas)
    check("pytest (import)", check_pytest)
    check("parselmouth (pitch real de una onda de 150 Hz, no solo import)", check_parselmouth_pitch)
    print("\nEntorno listo.")
