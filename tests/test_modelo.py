"""
Tests de modelo.py (Etapa 3) con datos simulados de respuesta conocida.
"""

import numpy as np
import pytest
from scipy.optimize import check_grad

from tfc_voz.genotipo import SEMILLA
from tfc_voz.modelo import (Ajuste, ErrorConvergencia, _menos_log_verosimilitud, ajustar,
                            predecir, punto_de_partida)

N = 20_000
TOLERANCIA = 0.05
BETA = np.array([0.5, -1.0, 0.3])  # constante, binaria, continua


@pytest.fixture(scope="module")
def simulados():
    """Una variable binaria lleva sigma de 1,0 a 1,5; la media depende de la binaria y de una continua."""
    rng = np.random.default_rng(SEMILLA)
    binaria = rng.integers(0, 2, N).astype(float)
    continua = rng.normal(size=N)
    X_mu = np.column_stack([np.ones(N), binaria, continua])
    X_sigma = np.column_stack([np.ones(N), binaria])
    sigma = np.where(binaria == 1, 1.5, 1.0)
    y = X_mu @ BETA + sigma * rng.normal(size=N)
    return X_mu, X_sigma, y


@pytest.fixture(scope="module")
def ajuste(simulados):
    return ajustar(*simulados)


def test_alfa_de_la_binaria_da_log_1_5(ajuste):
    assert ajuste.alfa[0] == pytest.approx(0.0, abs=TOLERANCIA)
    assert ajuste.alfa[1] == pytest.approx(np.log(1.5), abs=TOLERANCIA)


def test_beta_recupera_los_verdaderos(ajuste):
    assert np.all(np.abs(ajuste.beta - BETA) < TOLERANCIA)


def test_se_desempaqueta_como_beta_y_alfa(ajuste):
    beta, alfa = ajuste
    assert beta is ajuste.beta and alfa is ajuste.alfa
    assert isinstance(ajuste, Ajuste) and ajuste.iteraciones > 0


def test_predecir(ajuste, simulados):
    X_mu, X_sigma, _ = simulados
    mu, sigma = predecir(*ajuste, X_mu, X_sigma)
    assert np.allclose(mu, X_mu @ ajuste.beta)
    assert np.allclose(sigma, np.exp(X_sigma @ ajuste.alfa))
    assert np.all(sigma > 0)


def test_gradiente_analitico_coincide_con_el_numerico(simulados):
    X_mu, X_sigma, y = simulados
    theta = np.array([0.4, -0.8, 0.2, 0.1, 0.3])
    error = check_grad(lambda t: _menos_log_verosimilitud(t, X_mu, X_sigma, y)[0],
                       lambda t: _menos_log_verosimilitud(t, X_mu, X_sigma, y)[1], theta)
    assert error < 1e-5


def test_punto_de_partida(simulados):
    X_mu, X_sigma, y = simulados
    beta0, alfa0 = punto_de_partida(X_mu, X_sigma, y)
    assert np.allclose(beta0, np.linalg.lstsq(X_mu, y, rcond=None)[0])
    assert alfa0[0] == pytest.approx(np.log(np.std(y - X_mu @ beta0)))
    assert np.all(alfa0[1:] == 0)


def test_maxima_verosimilitud_mejora_al_punto_de_partida(ajuste, simulados):
    X_mu, X_sigma, y = simulados
    inicio = np.concatenate(punto_de_partida(X_mu, X_sigma, y))
    final = np.concatenate([ajuste.beta, ajuste.alfa])
    assert _menos_log_verosimilitud(final, X_mu, X_sigma, y)[0] < _menos_log_verosimilitud(inicio, X_mu, X_sigma, y)[0]


def test_sin_convergencia_levanta_error_con_el_mensaje_del_optimizador(simulados):
    with pytest.raises(ErrorConvergencia, match="no convergio en 1 iteraciones: .+"):
        ajustar(*simulados, max_iteraciones=1)


def test_rechaza_x_sigma_sin_constante(simulados):
    X_mu, X_sigma, y = simulados
    with pytest.raises(ValueError, match="constante"):
        ajustar(X_mu, X_sigma[:, ::-1], y)


def test_rechaza_dimensiones_incompatibles(simulados):
    X_mu, X_sigma, y = simulados
    with pytest.raises(ValueError, match="dimensiones"):
        ajustar(X_mu, X_sigma, y[:-1])
