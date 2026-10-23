"""
Cohorte del prototipo: envoltorio del paquete comun anima_spine.

La validacion del esquema y de la huella SHA-256 la hace el paquete
(spine.cargar y spine.verificar); aca no se duplica. Si el paquete rechaza
el archivo, su error pasa tal cual.

REEMPLAZABLE: es la unica pieza del modulo que sabe de donde salen los
individuos. Si cambia la columna vertebral, se toca solo este archivo.
"""

import pandas as pd

from anima_spine import spine

COLUMNAS = list(spine.CAMPOS)  # individuo_id, subpoblacion, sexo, edad, particion


def _a_dataframe(cohorte):
    return pd.DataFrame(cohorte.filas, columns=COLUMNAS)


def leer_cohorte(ruta="cohorte_anima.csv"):
    """Lee y verifica cohorte_anima.csv. Es la cohorte del analisis."""
    cohorte = spine.cargar(ruta)
    spine.verificar(cohorte)
    return _a_dataframe(cohorte)


def generar_cohorte(semilla=spine.SEMILLA, n=2000):
    """Genera una cohorte con el esquema del paquete.

    Solo para tests y para --generar-cohorte: el analisis se hace siempre
    sobre cohorte_anima.csv, que es la fuente de verdad (el generador de
    numpy puede cambiar entre versiones).
    """
    cohorte = spine.generar(n=n, semilla=semilla)
    spine.verificar(cohorte)
    return _a_dataframe(cohorte)
