"""
Modelo generativo de los fenotipos vocales (brief del prototipo, "Decisiones
ya tomadas"):

    y = m(sexo, edad, subpob) + s(sexo, edad) * (g + e)
    g ~ N(0, h2)      e ~ N(0, 1 - h2)

con m y s armados con los efectos de poblacion.py. La h2 es la proporcion
genetica dentro de lo que sexo, edad y ancestria no explican (heredabilidad
residual). Escala: desvios del logaritmo en mujeres (hnr: desvios de dB).

Cada parametro usa su propio generador, default_rng([semilla, indice]), con
un indice FIJO por nombre: agregar o reordenar parametros no cambia los
valores de los demas (decision de Diego, 23/10).
"""

import numpy as np
import pandas as pd

# Indice de cada parametro para su generador. Un parametro nuevo recibe el
# numero siguiente; nunca se renumera.
INDICE_SEMILLA = {
    "f0_medio": 0,
    "f0_variabilidad": 1,
    "jitter": 2,
    "hnr": 3,
    "f1": 4,
    "f2": 5,
    "f3": 6,
    "vtl": 7,
}


def edad_centrada(edad):
    """edad_c = (edad - 49) / 10: decadas desde los 49 anios."""
    return (np.asarray(edad, dtype=float) - 49.0) / 10.0


def tramo60(edad):
    """tramo60 = max(0, edad - 60) / 10: decadas despues de los 60."""
    return np.maximum(0.0, np.asarray(edad, dtype=float) - 60.0) / 10.0


def media_y_escala(efecto, sexo, edad, subpoblacion):
    """m y s de un parametro para cada persona."""
    sexo = np.asarray(sexo, dtype=float)
    mujer = 1.0 - sexo
    ec, tr = edad_centrada(edad), tramo60(edad)
    a = np.array([efecto.a[s] for s in subpoblacion], dtype=float)
    m = (efecto.d * sexo
         + (efecto.b_mujer * mujer + efecto.b_hombre * sexo) * ec
         + (efecto.q_mujer * mujer + efecto.q_hombre * sexo) * tr
         + a)
    s = efecto.r ** sexo * np.exp(efecto.c * ec)
    return m, s


def generar_fenotipos(cohorte, parametros, efectos, semilla):
    """g, e e y por persona y parametro, en formato largo.

    cohorte: DataFrame de cohorte.py (individuo_id, subpoblacion, sexo, edad, ...).
    parametros: lista de ParametroAcustico (nombre y heredabilidad).
    efectos: {nombre: EfectosPoblacionales}.
    Devuelve un DataFrame con individuo_id, rasgo, g, e e y.
    """
    n = len(cohorte)
    bloques = []
    for p in parametros:
        if p.nombre not in INDICE_SEMILLA:
            raise KeyError(f"{p.nombre} no tiene indice de semilla: agregarlo a INDICE_SEMILLA")
        rng = np.random.default_rng([semilla, INDICE_SEMILLA[p.nombre]])
        g = rng.normal(0.0, np.sqrt(p.heredabilidad), n)
        e = rng.normal(0.0, np.sqrt(1.0 - p.heredabilidad), n)
        m, s = media_y_escala(efectos[p.nombre], cohorte["sexo"].to_numpy(),
                              cohorte["edad"].to_numpy(), cohorte["subpoblacion"].to_numpy())
        bloques.append(pd.DataFrame({
            "individuo_id": cohorte["individuo_id"].to_numpy(),
            "rasgo": p.nombre,
            "g": g,
            "e": e,
            "y": m + s * (g + e),
        }))
    return pd.concat(bloques, ignore_index=True)
