"""
Datos de Voz para la capa de calibracion comun (la de Tomas).

Genera los fenotipos sobre cohorte_anima.csv con la semilla 20261019 (la de
la replica 0 del prototipo) y escribe informes/voz_para_calibracion.csv: las
personas de calibracion y de prueba, por los 8 parametros (8.000 filas).

mu_oraculo y sigma_oraculo son la media y el desvio VERDADEROS de cada persona,
conocidos por diseno: mu_oraculo = m + s * g y sigma_oraculo = s * sqrt(1 - h2).
No son predicciones de ningun modelo. Sirven para que la capa de calibracion
pruebe con datos que tienen la forma real de Voz antes de que exista el modelo.
El calculo es fenotipo.oraculo, el mismo que usa la tabla predictiva.

Las columnas siguen la propuesta que Diego le mando a Tomas el 26/10. Si el
contrato congelado usa otros nombres, se renombran en COLUMNAS, sin tocar la
logica.

Uso (parado en la raiz del proyecto):
    python scripts/exportar_para_calibracion.py
"""

import argparse
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ)]
from tfc_voz.cohorte import leer_cohorte  # noqa: E402
from tfc_voz.fenotipo import generar_fenotipos, oraculo  # noqa: E402
from tfc_voz.genotipo import SEMILLA  # noqa: E402
from tfc_voz.parametros import PARAMETROS  # noqa: E402
from tfc_voz.poblacion import EFECTOS  # noqa: E402

COLUMNAS = ["individuo_id", "particion", "rasgo", "y_real", "mu_oraculo", "sigma_oraculo"]
PARTICIONES = ("calibracion", "prueba")


def armar_datos(cohorte, parametros=PARAMETROS, efectos=EFECTOS, semilla=SEMILLA):
    """Filas de calibracion y prueba con y real, media y desvio oraculo."""
    fenotipos = generar_fenotipos(cohorte, parametros, efectos, semilla)
    datos = (oraculo(cohorte, fenotipos, parametros, efectos)
             .merge(fenotipos[["individuo_id", "rasgo", "y"]], on=["individuo_id", "rasgo"])
             .merge(cohorte[["individuo_id", "particion"]], on="individuo_id")
             .rename(columns={"y": "y_real"}))
    return datos[datos["particion"].isin(PARTICIONES)].reset_index(drop=True)[COLUMNAS]


def escribir(datos, ruta):
    """Escribe el CSV con finales de linea LF, igual en cualquier sistema."""
    datos.to_csv(ruta, index=False, lineterminator="\n")


def validar(datos, cohorte, parametros=PARAMETROS):
    """Levanta AssertionError si el archivo no cumple lo que espera la capa de calibracion."""
    if list(datos.columns) != COLUMNAS:
        raise AssertionError(f"columnas {list(datos.columns)}, se esperaba {COLUMNAS}")
    if datos.duplicated(["individuo_id", "rasgo"]).any():
        raise AssertionError("hay mas de una fila por (individuo_id, rasgo)")
    rasgos = {p.nombre for p in parametros}
    if set(datos["rasgo"]) != rasgos:
        raise AssertionError(f"rasgos {sorted(set(datos['rasgo']))}, se esperaba {sorted(rasgos)}")
    esperado = cohorte.loc[cohorte["particion"].isin(PARTICIONES), ["individuo_id", "particion"]]
    esperado = dict(zip(esperado["individuo_id"], esperado["particion"]))
    for rasgo, grupo in datos.groupby("rasgo"):
        obtenido = dict(zip(grupo["individuo_id"], grupo["particion"]))
        if obtenido != esperado:
            raise AssertionError(f"rasgo {rasgo}: los ids o las particiones no coinciden con la cohorte")
    numericos = datos[["y_real", "mu_oraculo", "sigma_oraculo"]].to_numpy()
    if not np.isfinite(numericos).all():
        raise AssertionError("hay valores no finitos")
    if not (datos["sigma_oraculo"] > 0).all():
        raise AssertionError("hay sigma_oraculo no positivo")


def main():
    ap = argparse.ArgumentParser(description="Datos de Voz para la capa de calibracion comun")
    ap.add_argument("--cohorte", type=Path, default=RAIZ / "cohorte_anima.csv")
    ap.add_argument("--salida", type=Path, default=RAIZ / "informes" / "voz_para_calibracion.csv")
    args = ap.parse_args()

    cohorte = leer_cohorte(args.cohorte)
    datos = armar_datos(cohorte)
    validar(datos, cohorte)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    escribir(datos, args.salida)
    print(f"{args.salida}: {len(datos)} filas, validacion OK")
    print(datos.groupby(["rasgo", "particion"]).size().unstack().to_string())


if __name__ == "__main__":
    main()
