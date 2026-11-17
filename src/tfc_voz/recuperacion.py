"""
Criterio de recuperacion del nivel declarado (punto 8 de la entrega del 9/11).

Por replica, rasgo y linea base, el DeltaR2 total y parcial del modelo
completo en la particion de prueba, con el nivel declarado del rasgo sacado de
la configuracion. Las filas son las de predictions.fila_recuperacion y el
archivo, recuperacion_voz.csv, se valida con predictions.verificar_recuperacion
antes de escribirlo.

El criterio (predictions.criterio_recuperacion) se evalua sobre el promedio de
las 20 replicas, contra la linea base de ancestria, sexo y edad, y solo en el
caso base: el segundo nivel se informa sin criterio. La tolerancia sale de la
configuracion, no de este codigo (respuesta del 12/11), y se fija con la
simulacion del nulo ANTES de ver la corrida real (scripts/simular_nulo.py).
Mientras no este fijada, no hay veredicto.
"""

from anima_spine import predictions
from tfc_voz.genotipo import SEMILLA
from tfc_voz.metricas import delta_r2
from tfc_voz.parametros import NIVELES, PARAMETROS
from tfc_voz.poblacion import EFECTOS
from tfc_voz.replicas import DOMINIO, correr_replica

NIVEL_CON_CRITERIO = "caso_base"


class ToleranciaSinFijar(RuntimeError):
    """La tolerancia del criterio todavia no se fijo con la simulacion del nulo."""


def filas_recuperacion(tabla, replica, semilla, nivel_declarado):
    """Filas de recuperacion de una replica, desde su tabla predictiva (solo la particion de prueba).

    nivel_declarado: {rasgo: valor}, de la configuracion.
    """
    prueba = tabla[tabla["particion"] == "prueba"]
    filas = []
    for (rasgo, base), grupo in prueba.groupby(["rasgo", "linea_base"], sort=True):
        total, parcial = delta_r2(grupo["y_real"].to_numpy(), grupo["mu_base"].to_numpy(),
                                  grupo["mu"].to_numpy())
        filas.append(predictions.fila_recuperacion(replica, semilla, DOMINIO, rasgo, base,
                                                   nivel_declarado[rasgo], total, parcial))
    return filas


def barrido_recuperacion(cohorte, nivel=NIVEL_CON_CRITERIO, columna_g="g", semilla_base=SEMILLA,
                         replicas=predictions.REPLICAS, parametros=PARAMETROS, efectos=EFECTOS):
    """Filas de recuperacion de las replicas 0 a replicas - 1 (semilla semilla_base + r).

    En el caso base el modelo completo recibe la g completa; en el segundo
    nivel, columna_g = "g_conocida". Los fenotipos son siempre los mismos.
    """
    declarado = NIVELES.de(nivel)
    filas = []
    for r in range(replicas):
        tabla = correr_replica(cohorte, r, parametros, efectos, columna_g, semilla_base)
        filas += filas_recuperacion(tabla, r, semilla_base + r, declarado)
    return filas


def escribir_recuperacion(filas, directorio):
    """Valida con el paquete y escribe recuperacion_voz.csv. Devuelve la ruta."""
    predictions.verificar_recuperacion(filas, DOMINIO)
    return predictions.exportar_recuperacion(filas, DOMINIO, directorio)


def evaluar_criterio(filas, niveles=NIVELES):
    """Veredicto del criterio de recuperacion, con la tolerancia de la configuracion.

    Levanta ToleranciaSinFijar si la tolerancia no esta fijada, y ValueError si
    las filas no son del caso base (el segundo nivel no lleva criterio).
    """
    criterio = niveles.criterio_recuperacion
    if criterio["tolerancia"] is None:
        raise ToleranciaSinFijar(f"la tolerancia del criterio no esta fijada: {criterio['estado']}")
    caso_base = niveles.de(criterio["nivel"])
    if any(abs(f["nivel_declarado"] - caso_base[f["rasgo"]]) > 0 for f in filas):
        raise ValueError(f"el criterio se evalua solo sobre el {criterio['nivel']}: "
                         "el segundo nivel se informa sin criterio")
    return predictions.criterio_recuperacion(filas, linea_base=criterio["linea_base"],
                                             tolerancia=criterio["tolerancia"])

