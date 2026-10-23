"""
Contrasta las h2 cargadas en parametros.py contra la tabla S6 de
Gisladottir et al. 2023, para que no se puedan desincronizar del CSV.
"""

from pathlib import Path

import pandas as pd
import pytest

from tfc_voz.parametros import H2_MAXIMOS, PARAMETROS

CSV_S6 = Path(__file__).resolve().parents[1] / "referencias" / "tabla-s6-heredabilidades.csv"

# Fila de la S6 de la que sale cada maximo de H2_MAXIMOS.
FILAS_MAXIMOS = {
    "f0_medio": "MedianF0_MeasureReading",
    "f0_variabilidad": "StdF0_MeasureReading",
    "f1": "MedianF1_MeasureA",
    "f2": "MedianF2_MeasureVowels",
    "f3": "MedianF3_MeasureO",
}


@pytest.fixture(scope="module")
def s6():
    return pd.read_csv(CSV_S6).set_index("Measure")


@pytest.mark.parametrize("p", [p for p in PARAMETROS if p.fila_s6], ids=lambda p: p.nombre)
def test_h2_e_ic_coinciden_con_s6(s6, p):
    fila = s6.loc[p.fila_s6]
    assert p.heredabilidad == pytest.approx(fila["H2"], abs=1e-9)
    assert p.ic95_inf == pytest.approx(fila["LowerCI"], abs=1e-9)
    assert p.ic95_sup == pytest.approx(fila["UpperCI"], abs=1e-9)


def test_regla_agregada_de_cinco_vocales():
    filas = {p.nombre: p.fila_s6 for p in PARAMETROS if p.fila_s6}
    for nombre, fila in filas.items():
        assert fila == "VTL" or fila.endswith("_MeasureVowels"), nombre


def test_parametros_sin_s6_no_tienen_ic():
    for p in PARAMETROS:
        if p.fila_s6 is None:
            assert p.ic95_inf is None and p.ic95_sup is None, p.nombre


def test_promedio_h2():
    promedio = sum(p.heredabilidad for p in PARAMETROS) / len(PARAMETROS)
    assert round(promedio, 4) == 0.0707


@pytest.mark.parametrize("nombre", list(FILAS_MAXIMOS))
def test_maximos_coinciden_con_s6(s6, nombre):
    assert H2_MAXIMOS[nombre] == pytest.approx(s6.loc[FILAS_MAXIMOS[nombre], "H2"], abs=1e-9)


def test_el_modelo_no_usa_los_maximos():
    for p in PARAMETROS:
        if p.nombre in H2_MAXIMOS and p.nombre != "f2":  # en f2 coinciden
            assert p.heredabilidad != H2_MAXIMOS[p.nombre], p.nombre
