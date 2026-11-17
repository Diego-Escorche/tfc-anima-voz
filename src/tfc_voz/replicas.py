"""
Tabla predictiva y replicas (ajustes del 29/10 de la Etapa 3; adelantado al
punto 8 de la entrega del 9/11). lineas_base.py arma los modelos; este archivo
orquesta fenotipos, ajuste y tabla.

tabla_predictiva: una fila por persona de calibracion y de prueba x parametro
x linea base (16.000 filas), con las columnas del contrato v2 de la capa de
calibracion. mu y sigma son los del modelo completo, iguales en las dos filas
de una misma persona y parametro. El oraculo es fenotipo.oraculo, el mismo del
archivo para la capa de calibracion.

correr_replica: fenotipos con la semilla base + r, los tres modelos de cada
parametro ajustados solo con entrenamiento, y la tabla predictiva. Es
determinista. La replica 0 de la semilla 20261019 es la corrida principal.
"""

import pandas as pd

from anima_spine import predictions
from tfc_voz.fenotipo import generar_fenotipos, oraculo
from tfc_voz.genotipo import SEMILLA
from tfc_voz.lineas_base import COMPLETO, ajustar_modelos, columnas_de, predecir_modelos
from tfc_voz.parametros import PARAMETROS
from tfc_voz.poblacion import EFECTOS

DOMINIO = "voz"
PARTICIONES_TABLA = ("calibracion", "prueba")
COLUMNAS_TABLA = ["individuo_id", "dominio", "particion", "rasgo", "y_real", "mu", "sigma",
                  "linea_base", "mu_base", "sigma_base", "mu_oraculo", "sigma_oraculo"]


def tabla_predictiva(cohorte, fenotipos, ajustes, parametros=PARAMETROS, efectos=EFECTOS, columna_g="g"):
    """DataFrame largo con las columnas del contrato v2, para calibracion y prueba.

    ajustes: {rasgo: {modelo: Ajuste}} de lineas_base.ajustar_modelos.
    columna_g: el puntaje que recibe el modelo completo (el mismo con el que se ajusto).
    El oraculo usa siempre la g completa: es la verdad, no una prediccion.
    """
    parametros = [p for p in parametros if p.nombre in ajustes]
    sub = cohorte[cohorte["particion"].isin(PARTICIONES_TABLA)]
    orac = oraculo(cohorte, fenotipos, parametros, efectos).set_index(["individuo_id", "rasgo"])
    ids = sub["individuo_id"].to_numpy()
    bloques = []
    for p in parametros:
        y, g = columnas_de(fenotipos, p.nombre, sub, ["y", columna_g])
        pred = predecir_modelos(ajustes[p.nombre], sub, g)
        mu, sigma = pred[COMPLETO]
        o = orac.loc[[(i, p.nombre) for i in ids]]
        for base in predictions.LINEAS_BASE:
            mu_base, sigma_base = pred[base]
            bloques.append(pd.DataFrame({
                "individuo_id": ids, "dominio": DOMINIO, "particion": sub["particion"].to_numpy(),
                "rasgo": p.nombre, "y_real": y, "mu": mu, "sigma": sigma, "linea_base": base,
                "mu_base": mu_base, "sigma_base": sigma_base,
                "mu_oraculo": o["mu_oraculo"].to_numpy(), "sigma_oraculo": o["sigma_oraculo"].to_numpy(),
            }))
    return pd.concat(bloques, ignore_index=True)[COLUMNAS_TABLA]


def correr_replica(cohorte, r, parametros=PARAMETROS, efectos=EFECTOS, columna_g="g", semilla_base=SEMILLA):
    """Tabla predictiva de la replica r: semilla semilla_base + r, ajuste solo con entrenamiento."""
    fenotipos = generar_fenotipos(cohorte, parametros, efectos, semilla_base + r)
    ajustes = ajustar_modelos(cohorte, fenotipos, parametros, columna_g=columna_g)
    return tabla_predictiva(cohorte, fenotipos, ajustes, parametros, efectos, columna_g)
