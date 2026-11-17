"""
Metricas del modulo (Etapa 5 del brief, adelantada al punto 8 de la entrega
del 9/11): R2, DeltaR2 total y parcial, CRPS de la normal y bootstrap pareado.

No hay funcion de cobertura (respuesta del 12/11): la cuenta el paquete
comun, con predictions.fila_barrido y predictions.cobertura_promedio, y una
segunda funcion pondria la misma cantidad en dos lugares. Por la misma razon,
R2 y DeltaR2 son los de anima_spine.compare: este modulo solo los expone con
la firma del brief.

Todas se calculan sobre la particion de prueba; eso lo decide quien las llama.
"""

import numpy as np
from scipy.stats import norm

from anima_spine import compare
from tfc_voz.genotipo import SEMILLA


def r2(y, mu):
    """1 - suma de residuos al cuadrado / suma de cuadrados alrededor de la media de y."""
    return compare._r2(np.asarray(y, dtype=float), np.asarray(mu, dtype=float))


def delta_r2(y, mu_base, mu_completo):
    """(DeltaR2 total, DeltaR2 parcial) del modelo completo sobre una linea base.

    parcial = (R2 completo - R2 base) / (1 - R2 base). Es compare.delta_r2.
    """
    return compare.delta_r2(np.asarray(y, dtype=float), np.asarray(mu_completo, dtype=float),
                            np.asarray(mu_base, dtype=float))


def crps_normal(y, mu, sigma):
    """CRPS de una prediccion normal, por persona (formula cerrada).

    CRPS = sigma * [z (2 Phi(z) - 1) + 2 phi(z) - 1 / sqrt(pi)], z = (y - mu) / sigma.
    """
    y, mu, sigma = (np.asarray(a, dtype=float) for a in (y, mu, sigma))
    if np.any(sigma <= 0):
        raise ValueError("sigma tiene que ser positivo")
    z = (y - mu) / sigma
    return sigma * (z * (2.0 * norm.cdf(z) - 1.0) + 2.0 * norm.pdf(z) - 1.0 / np.sqrt(np.pi))


def bootstrap_pareado(estadistico, *arrays, n_rep=2000, semilla=SEMILLA, nivel=0.95):
    """Estimacion e IC por percentiles, remuestreando personas con reposicion.

    estadistico(*arrays) -> float. En cada remuestreo se usan los MISMOS
    indices en todos los arrays, asi los dos modelos se comparan sobre las
    mismas personas. Devuelve (estimacion, limite inferior, limite superior).
    """
    arrays = [np.asarray(a) for a in arrays]
    n = len(arrays[0])
    if any(len(a) != n for a in arrays):
        raise ValueError("los arrays tienen que tener la misma cantidad de personas")
    rng = np.random.default_rng(semilla)
    replicas = np.empty(n_rep)
    for k in range(n_rep):
        idx = rng.integers(0, n, n)
        replicas[k] = estadistico(*(a[idx] for a in arrays))
    alfa = (1.0 - nivel) / 2.0
    lo, hi = np.quantile(replicas, [alfa, 1.0 - alfa])
    return float(estadistico(*arrays)), float(lo), float(hi)
