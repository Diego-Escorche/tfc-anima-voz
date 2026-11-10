"""
Ajuste generico de media y log-desvio por maxima verosimilitud normal
(Etapa 3 del brief del prototipo). No sabe nada de voz: recibe matrices.

    mu = X_mu @ beta        log sigma = X_sigma @ alfa

Minimiza la log-verosimilitud normal negativa con scipy.optimize.minimize
(L-BFGS-B, gradiente analitico). Punto de partida: beta por minimos
cuadrados, alfa_0 igual al logaritmo del desvio de los residuos y el resto
de alfa en cero (la primera columna de X_sigma tiene que ser la constante).

Nunca devuelve un ajuste sin convergencia: si el optimizador no converge,
levanta ErrorConvergencia con su mensaje. lineas_base.py lo vuelve a levantar
nombrando el parametro y el modelo (decision del 29/10).
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize


class ErrorConvergencia(RuntimeError):
    """El optimizador no convergio."""


@dataclass(frozen=True)
class Ajuste:
    """beta y alfa ajustados, y cuantas iteraciones hizo el optimizador.

    Se desempaqueta como (beta, alfa): beta, alfa = ajustar(...).
    """
    beta: np.ndarray
    alfa: np.ndarray
    iteraciones: int

    def __iter__(self):
        return iter((self.beta, self.alfa))


def _menos_log_verosimilitud(theta, X_mu, X_sigma, y):
    """Log-verosimilitud normal negativa promedio (sin la constante) y su gradiente."""
    k = X_mu.shape[1]
    beta, alfa = theta[:k], theta[k:]
    residuo = y - X_mu @ beta
    log_sigma = X_sigma @ alfa
    w = np.exp(-2.0 * log_sigma)            # 1 / sigma^2
    n = len(y)
    valor = np.sum(log_sigma + 0.5 * w * residuo ** 2) / n
    grad_beta = -(X_mu.T @ (w * residuo)) / n
    grad_alfa = (X_sigma.T @ (1.0 - w * residuo ** 2)) / n
    return valor, np.concatenate([grad_beta, grad_alfa])


def punto_de_partida(X_mu, X_sigma, y):
    """beta por minimos cuadrados; alfa_0 = log del desvio de los residuos, el resto en cero."""
    beta0, *_ = np.linalg.lstsq(X_mu, y, rcond=None)
    alfa0 = np.zeros(X_sigma.shape[1])
    alfa0[0] = np.log(np.std(y - X_mu @ beta0))
    return beta0, alfa0


def ajustar(X_mu, X_sigma, y, max_iteraciones=15000):
    """beta y alfa de maxima verosimilitud. Levanta ErrorConvergencia si no converge."""
    X_mu = np.asarray(X_mu, dtype=float)
    X_sigma = np.asarray(X_sigma, dtype=float)
    y = np.asarray(y, dtype=float)
    if not (X_mu.ndim == X_sigma.ndim == 2 and len(X_mu) == len(X_sigma) == len(y)):
        raise ValueError(f"dimensiones incompatibles: X_mu {X_mu.shape}, X_sigma {X_sigma.shape}, "
                         f"y {y.shape}")
    if not np.allclose(X_sigma[:, 0], 1.0):
        raise ValueError("la primera columna de X_sigma tiene que ser la constante")
    beta0, alfa0 = punto_de_partida(X_mu, X_sigma, y)
    res = minimize(_menos_log_verosimilitud, np.concatenate([beta0, alfa0]), args=(X_mu, X_sigma, y),
                   jac=True, method="L-BFGS-B", options={"maxiter": max_iteraciones})
    if not res.success:
        raise ErrorConvergencia(f"L-BFGS-B no convergio en {res.nit} iteraciones: {res.message}")
    k = X_mu.shape[1]
    return Ajuste(beta=res.x[:k], alfa=res.x[k:], iteraciones=int(res.nit))


def predecir(beta, alfa, X_mu, X_sigma):
    """mu y sigma para cada fila."""
    return np.asarray(X_mu, dtype=float) @ beta, np.exp(np.asarray(X_sigma, dtype=float) @ alfa)
