"""
Tests de metricas.py (Etapa 5 del brief, adelantada al punto 8).

Los que ajustan modelos usan semillas de fenotipos distintas de las de la
corrida oficial (20261019 + r, r de 0 a 19): la tolerancia del criterio de
recuperacion se fija antes de ver esa corrida.
"""

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.stats import norm

from anima_spine import compare
from tfc_voz.cohorte import generar_cohorte
from tfc_voz.fenotipo import generar_fenotipos
from tfc_voz.genotipo import SEMILLA
from tfc_voz.lineas_base import (ANCESTRIA_SEXO_EDAD, COMPLETO, ajustar_modelos, columnas_de,
                                 predecir_modelos)
from tfc_voz.metricas import bootstrap_pareado, crps_normal, delta_r2, r2
from tfc_voz.parametros import PARAMETROS
from tfc_voz.poblacion import EFECTOS, configuracion_neutra

SEMILLA_TESTS = SEMILLA + 900  # fuera de las 20 semillas de la corrida oficial


def test_crps_con_y_igual_a_mu():
    """Con y = mu, CRPS = sigma * (2 phi(0) - 1/sqrt(pi)) = 0,2337 sigma."""
    sigma = np.array([0.5, 1.0, 2.0])
    assert np.allclose(crps_normal(np.zeros(3), np.zeros(3), sigma), 0.2337 * sigma, atol=1e-4)


@pytest.mark.parametrize("y, mu, sigma", [(0.3, -0.2, 0.7), (-1.5, 0.4, 1.3), (2.0, 2.0, 0.1)])
def test_crps_coincide_con_la_integral(y, mu, sigma):
    """CRPS = integral de (F(x) - 1{x >= y})^2 dx, calculada numericamente."""
    antes, _ = quad(lambda x: norm.cdf(x, mu, sigma) ** 2, -np.inf, y)
    despues, _ = quad(lambda x: (1 - norm.cdf(x, mu, sigma)) ** 2, y, np.inf)
    assert crps_normal(y, mu, sigma) == pytest.approx(antes + despues, abs=1e-7)


def test_crps_rechaza_sigma_no_positivo():
    with pytest.raises(ValueError, match="positivo"):
        crps_normal([0.0], [0.0], [0.0])


def test_r2_y_delta_r2_son_los_del_paquete():
    rng = np.random.default_rng(SEMILLA_TESTS)
    y, mu, base = rng.normal(size=500), rng.normal(size=500), rng.normal(size=500)
    assert r2(y, mu) == pytest.approx(1 - np.sum((y - mu) ** 2) / np.sum((y - y.mean()) ** 2))
    assert delta_r2(y, base, mu) == compare.delta_r2(y, mu, base)
    total, parcial = delta_r2(y, base, mu)
    assert total == pytest.approx(r2(y, mu) - r2(y, base))
    assert parcial == pytest.approx(total / (1 - r2(y, base)))


def test_bootstrap_usa_los_mismos_indices_en_todos_los_arrays():
    """Si los dos arrays son iguales, la diferencia es 0 en todos los remuestreos."""
    a = np.random.default_rng(SEMILLA_TESTS).normal(size=300)
    assert bootstrap_pareado(lambda x, y: float(np.mean(x - y)), a, a.copy(), n_rep=200) == (0.0, 0.0, 0.0)


def test_bootstrap_es_determinista_y_cubre_la_estimacion():
    a = np.random.default_rng(SEMILLA_TESTS).normal(1.0, 1.0, size=400)
    primero = bootstrap_pareado(np.mean, a, n_rep=500)
    assert primero == bootstrap_pareado(np.mean, a, n_rep=500)
    estimacion, lo, hi = primero
    assert lo < estimacion < hi


def ajustar_y_predecir(cohorte, fen, parametros, columna_g="g"):
    """mu del modelo completo y de la linea base 2, y el y real, en la particion de prueba."""
    ajustes = ajustar_modelos(cohorte, fen, parametros, columna_g=columna_g)
    prueba = cohorte[cohorte["particion"] == "prueba"]
    salida = {}
    for p in parametros:
        y, g = columnas_de(fen, p.nombre, prueba, ["y", columna_g])
        pred = predecir_modelos(ajustes[p.nombre], prueba, g)
        salida[p.nombre] = (y, pred[ANCESTRIA_SEXO_EDAD][0], pred[COMPLETO][0])
    return salida


def test_con_el_puntaje_permutado_el_ic_del_delta_r2_incluye_el_cero():
    cohorte = generar_cohorte()
    fen = generar_fenotipos(cohorte, PARAMETROS, EFECTOS, SEMILLA_TESTS)
    fen["g_permutado"] = np.random.default_rng(SEMILLA_TESTS).permutation(fen["g"].to_numpy())
    for nombre, (y, mu_base, mu) in ajustar_y_predecir(cohorte, fen, PARAMETROS, "g_permutado").items():
        _, lo, hi = bootstrap_pareado(lambda a, b, c: delta_r2(a, b, c)[1], y, mu_base, mu, n_rep=1000)
        assert lo <= 0 <= hi, nombre


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_con_100000_personas_y_efectos_neutros_el_delta_r2_da_la_h2(p, recuperado_100000):
    """Contra la linea base de ancestria, sexo y edad, a menos de 0,01 de la h2."""
    y, mu_base, mu = recuperado_100000[p.nombre]
    _, parcial = delta_r2(y, mu_base, mu)
    assert abs(parcial - p.heredabilidad) < 0.01


@pytest.fixture(scope="module")
def recuperado_100000():
    cohorte = generar_cohorte(n=100_000)
    fen = generar_fenotipos(cohorte, PARAMETROS, configuracion_neutra(), SEMILLA_TESTS)
    return ajustar_y_predecir(cohorte, fen, PARAMETROS)
