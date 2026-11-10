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

El puntaje genetico es g = g_conocida + g_resto (punto 7 de la entrega del
9/11; ver variantes.py): g_conocida sale de las variantes publicadas en los
parametros que tienen una, y g_resto ~ N(0, h2 - V), con V el segundo nivel
declarado, asi Var(g) = h2. En los parametros sin variante V = 0 y g es la
de siempre. Del generador de cada parametro salen, en este orden, g_resto, e
y las copias sorteadas de las personas simuladas: e no depende de V.
En cada replica se sortean de nuevo las copias de las personas simuladas;
las de las reales son siempre las del archivo de genotipos.
"""

import numpy as np
import pandas as pd

from tfc_voz import variantes as _variantes

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


def generar_fenotipos(cohorte, parametros, efectos, semilla, niveles=None, genotipos=None):
    """g (y su parte conocida), e e y por persona y parametro, en formato largo.

    cohorte: DataFrame de cohorte.py (individuo_id, subpoblacion, sexo, edad, ...).
    parametros: lista de ParametroAcustico (nombre y heredabilidad).
    efectos: {nombre: EfectosPoblacionales}.
    niveles: NivelesDeclarados con las variantes y el segundo nivel (V); por
    defecto, los de la configuracion.
    genotipos: copias de las personas reales (variantes.cargar_genotipos); por
    defecto se leen de datos/ si hacen falta, verificando la alineacion.
    Devuelve un DataFrame con individuo_id, rasgo, g, g_conocida, e e y.
    """
    if niveles is None:
        from tfc_voz.parametros import NIVELES as niveles
    segundo = niveles.de("segundo_nivel")
    con_variante = [v for v in niveles.variantes if v.parametro in {p.nombre for p in parametros}]
    if genotipos is None and con_variante and _variantes.reales(cohorte).any():
        genotipos = _variantes.cargar_genotipos(niveles.variantes)
        _variantes.verificar_alineacion(cohorte, genotipos, con_variante)
    n = len(cohorte)
    bloques = []
    for p in parametros:
        if p.nombre not in INDICE_SEMILLA:
            raise KeyError(f"{p.nombre} no tiene indice de semilla: agregarlo a INDICE_SEMILLA")
        v_conocida = segundo.get(p.nombre, 0.0)
        if v_conocida > p.heredabilidad:
            raise ValueError(f"{p.nombre}: la varianza conocida ({v_conocida}) supera la h2 "
                             f"({p.heredabilidad}); no se usa una varianza negativa")
        rng = np.random.default_rng([semilla, INDICE_SEMILLA[p.nombre]])
        g_resto = rng.normal(0.0, np.sqrt(p.heredabilidad - v_conocida), n)
        e = rng.normal(0.0, np.sqrt(1.0 - p.heredabilidad), n)
        g_conocida = _variantes.puntaje_conocido(
            cohorte, [v for v in con_variante if v.parametro == p.nombre], genotipos, rng)
        g = g_conocida + g_resto
        m, s = media_y_escala(efectos[p.nombre], cohorte["sexo"].to_numpy(),
                              cohorte["edad"].to_numpy(), cohorte["subpoblacion"].to_numpy())
        bloques.append(pd.DataFrame({
            "individuo_id": cohorte["individuo_id"].to_numpy(),
            "rasgo": p.nombre,
            "g": g,
            "g_conocida": g_conocida,
            "e": e,
            "y": m + s * (g + e),
        }))
    return pd.concat(bloques, ignore_index=True)


def oraculo(cohorte, fenotipos, parametros, efectos):
    """Media y desvio VERDADEROS de cada persona y parametro, conocidos por diseno.

    mu_oraculo = m + s * g y sigma_oraculo = s * sqrt(1 - h2): la distribucion de
    y dado todo lo que la genera salvo e. No son predicciones de ningun modelo.
    fenotipos: la salida de generar_fenotipos sobre la misma cohorte.
    Devuelve un DataFrame con individuo_id, rasgo, mu_oraculo y sigma_oraculo,
    en el orden de la cohorte dentro de cada rasgo.
    """
    ids = cohorte["individuo_id"].to_numpy()
    sexo, edad = cohorte["sexo"].to_numpy(), cohorte["edad"].to_numpy()
    subpob = cohorte["subpoblacion"].to_numpy()
    bloques = []
    for p in parametros:
        f = fenotipos[fenotipos["rasgo"] == p.nombre]
        if not np.array_equal(f["individuo_id"].to_numpy(), ids):
            raise ValueError(f"{p.nombre}: los fenotipos no estan en el orden de la cohorte")
        m, s = media_y_escala(efectos[p.nombre], sexo, edad, subpob)
        bloques.append(pd.DataFrame({
            "individuo_id": ids,
            "rasgo": p.nombre,
            "mu_oraculo": m + s * f["g"].to_numpy(),
            "sigma_oraculo": s * np.sqrt(1.0 - p.heredabilidad),
        }))
    return pd.concat(bloques, ignore_index=True)
