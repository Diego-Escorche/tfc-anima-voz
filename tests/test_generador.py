"""
Casos de prueba de la Practica 10 que dependen solo del generador
(genotipo.py). No usan cohorte_anima.csv ni el modelo.
"""

import numpy as np
import pytest

from tfc_voz.genotipo import SEMILLA, generar_cohorte_sintetica
from tfc_voz.parametros import PARAMETROS

# Estos tests generan su propia cohorte de 100.000 personas y NO usan
# cohorte_anima.csv (2.000). Una tolerancia de 0,01 sobre la h2 es mas chica
# que el ruido de muestreo con 2.000 personas: simulado con 300 repeticiones,
# para h2 = 0,135 (f2) el error supera 0,01 el 50% de las veces con 2.000
# personas, el 2% con 20.000 y nunca con 100.000. El generador es barato
# (~4 s para 100.000), asi que se usa el tamano grande.
N_COHORTE = 100_000
TOLERANCIA_H2 = 0.01


def scores(cohorte, parametro):
    """(score_genetico, score_total) de un parametro, como arrays."""
    g = np.array([ind.scores_geneticos[parametro] for ind in cohorte])
    total = np.array([ind.score_total(parametro) for ind in cohorte])
    return g, total


def r2(x, y):
    """R2 de la regresion lineal simple de y sobre x (con intercepto)."""
    return float(np.corrcoef(x, y)[0, 1] ** 2)


@pytest.fixture(scope="module")
def cohorte():
    return generar_cohorte_sintetica(N_COHORTE, semilla=SEMILLA)


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_vz01_04_recupera_h2_pedida(cohorte, p):
    """VZ-01 a VZ-04: la h2 empirica recupera la pedida con error menor a 0,01."""
    g, total = scores(cohorte, p.nombre)
    assert abs(r2(g, total) - p.heredabilidad) < TOLERANCIA_H2


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_vz05_permutacion_anula_la_senal(cohorte, p):
    """VZ-05: con score_genetico mezclado al azar entre individuos, el R2
    cae por debajo de 0,005."""
    g, total = scores(cohorte, p.nombre)
    g_mezclado = np.random.default_rng(SEMILLA).permutation(g)
    assert r2(g_mezclado, total) < 0.005


@pytest.mark.lento
@pytest.mark.parametrize("semilla", [SEMILLA + i for i in range(20)])
def test_vz07_estabilidad_entre_semillas(semilla):
    """VZ-07: VZ-01 a VZ-04 pasan para los 8 parametros con las 20 semillas
    20261019 + 0..19."""
    cohorte = generar_cohorte_sintetica(N_COHORTE, semilla=semilla)
    for p in PARAMETROS:
        g, total = scores(cohorte, p.nombre)
        assert abs(r2(g, total) - p.heredabilidad) < TOLERANCIA_H2, p.nombre
