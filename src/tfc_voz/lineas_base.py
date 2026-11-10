"""
Las dos lineas base y el modelo completo de cada parametro (Etapa 3 del
brief del prototipo), ajustados con modelo.py:

  Modelo               Columnas de X_mu                               Columnas de X_sigma
  solo intercepto      1                                              1
  ancestria sexo edad  1, sexo, edad_c, sexo*edad_c, tramo60,         1, sexo, edad_c
                       sexo*tramo60, dummies de subpoblacion (ref. CEU)
  completo             lo anterior + g, g*sexo, g*edad_c              1, sexo, edad_c

Las interacciones de g con sexo y edad hacen falta porque el efecto genetico
se escala con s, que depende de sexo y edad. Con los efectos reales c = 0, asi
que g*edad_c tiene que dar cerca de 0; se deja para que el modelo siga
sirviendo si c deja de ser 0 (ajustes del 29/10).

edad_c y tramo60 son las de fenotipo.py, sin redefinirlas: si las dos
definiciones se separan, la linea base deja de poder representar la media del
generador. Los nombres de las lineas base son los del paquete comun.

Se ajusta un modelo por parametro, solo con la particion de entrenamiento.
Si el optimizador no converge, el error nombra el parametro y el modelo.
"""

import numpy as np
import pandas as pd

from anima_spine import predictions
from tfc_voz.fenotipo import edad_centrada, tramo60
from tfc_voz.modelo import ErrorConvergencia, ajustar, predecir
from tfc_voz.poblacion import SUBPOBLACIONES

SOLO_INTERCEPTO, ANCESTRIA_SEXO_EDAD = predictions.LINEAS_BASE
COMPLETO = "completo"
MODELOS = (SOLO_INTERCEPTO, ANCESTRIA_SEXO_EDAD, COMPLETO)
REFERENCIA = "CEU"
PARTICION_AJUSTE = "entrenamiento"


def _dummies(subpoblacion):
    subpoblacion = np.asarray(subpoblacion)
    desconocidas = set(subpoblacion) - set(SUBPOBLACIONES)
    if desconocidas:
        raise ValueError(f"subpoblaciones desconocidas: {sorted(desconocidas)}")
    return np.column_stack([(subpoblacion == s).astype(float) for s in SUBPOBLACIONES if s != REFERENCIA])


def matrices(modelo, cohorte, g=None):
    """X_mu y X_sigma de un modelo para las filas de `cohorte` (y su puntaje g, en el mismo orden)."""
    n = len(cohorte)
    uno = np.ones((n, 1))
    if modelo == SOLO_INTERCEPTO:
        return uno, uno
    if modelo not in MODELOS:
        raise ValueError(f"modelo {modelo!r} desconocido: {MODELOS}")
    sexo = cohorte["sexo"].to_numpy(dtype=float)
    ec, tr = edad_centrada(cohorte["edad"]), tramo60(cohorte["edad"])
    X_mu = np.column_stack([uno, sexo, ec, sexo * ec, tr, sexo * tr, _dummies(cohorte["subpoblacion"])])
    X_sigma = np.column_stack([uno, sexo, ec])
    if modelo == COMPLETO:
        if g is None:
            raise ValueError("el modelo completo necesita el puntaje genetico g")
        g = np.asarray(g, dtype=float)
        if len(g) != n:
            raise ValueError(f"g tiene {len(g)} valores y la cohorte {n} filas")
        X_mu = np.column_stack([X_mu, g, g * sexo, g * ec])
    return X_mu, X_sigma


def ajustar_parametro(cohorte, y, g, parametro):
    """{modelo: Ajuste} de los tres modelos de un parametro, sobre todas las filas recibidas."""
    ajustes = {}
    for modelo in MODELOS:
        X_mu, X_sigma = matrices(modelo, cohorte, g)
        try:
            ajustes[modelo] = ajustar(X_mu, X_sigma, y)
        except ErrorConvergencia as e:
            raise ErrorConvergencia(f"parametro {parametro}, modelo {modelo!r}: {e}") from e
    return ajustes


def columnas_de(fenotipos, rasgo, cohorte, columnas):
    """Columnas de un rasgo de los fenotipos, en el orden de las filas de `cohorte`."""
    f = fenotipos.loc[fenotipos["rasgo"] == rasgo].set_index("individuo_id")
    ids = cohorte["individuo_id"].to_numpy()
    faltan = pd.Index(ids).difference(f.index)
    if len(faltan):
        raise ValueError(f"{rasgo}: faltan fenotipos de {len(faltan)} personas")
    return [f.loc[ids, c].to_numpy() for c in columnas]


def ajustar_modelos(cohorte, fenotipos, parametros, columna_g="g"):
    """{rasgo: {modelo: Ajuste}}, ajustados solo con la particion de entrenamiento.

    columna_g: la columna de fenotipos que recibe el modelo completo como
    puntaje genetico (la g completa, o la parte conocida en el segundo nivel).
    """
    entrenamiento = cohorte[cohorte["particion"] == PARTICION_AJUSTE]
    if entrenamiento.empty:
        raise ValueError(f"la cohorte no tiene personas de {PARTICION_AJUSTE}")
    ajustes = {}
    for p in parametros:
        y, g = columnas_de(fenotipos, p.nombre, entrenamiento, ["y", columna_g])
        ajustes[p.nombre] = ajustar_parametro(entrenamiento, y, g, p.nombre)
    return ajustes


def predecir_modelos(ajustes_rasgo, cohorte, g):
    """{modelo: (mu, sigma)} de un rasgo para las filas de `cohorte`."""
    return {modelo: predecir(*ajuste, *matrices(modelo, cohorte, g)) for modelo, ajuste in ajustes_rasgo.items()}
