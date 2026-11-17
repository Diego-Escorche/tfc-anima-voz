"""
Datos de Voz para la capa de calibracion comun (la de Tomas).

Genera los fenotipos sobre cohorte_anima.csv (cohorte 2.0) en las 20
replicas del barrido, con la semilla 20261019 + replica, y escribe
informes/voz_para_calibracion.csv: las personas de calibracion y de prueba,
por los 8 parametros y las 20 replicas (160.000 filas). Al lado escribe
voz_para_calibracion.meta.json, con la huella del CSV, el nivel declarado
usado y la nota sobre el puntaje genetico.

mu_oraculo y sigma_oraculo son la media y el desvio VERDADEROS de cada persona,
conocidos por diseno: mu_oraculo = m + s * g y sigma_oraculo = s * sqrt(1 - h2).
No son predicciones de ningun modelo. Sirven para que la capa de calibracion
pruebe con datos que tienen la forma real de Voz antes de que exista el modelo.
El calculo es fenotipo.oraculo, el mismo que usa la tabla predictiva.

Nivel declarado: el caso base. El puntaje genetico es g = g_conocida +
g_resto (punto 7 de la entrega del 9/11): en f0_medio, f1 y f2, la parte
conocida sale de las variantes publicadas, con los genotipos del archivo en
las 503 personas reales y sorteados en las simuladas. La version anterior
del archivo (huella b6f8d2d8..., commit 577a0e5) tenia g enteramente
simulado; esta tiene las mismas columnas y la misma distribucion.

Columnas (respuesta de Diego del 9/11): replica, semilla, dominio y sexo
primero, en el orden que pidio el responsable de la capa, y despues las que
ya tenia el archivo. Si el contrato congelado usa otros nombres, se renombran
en COLUMNAS, sin tocar la logica.

Uso (parado en la raiz del proyecto):
    python scripts/exportar_para_calibracion.py
"""

import argparse
import hashlib
import json
import platform
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ)]
import anima_spine  # noqa: E402
from anima_spine import predictions  # noqa: E402
from tfc_voz.cohorte import leer_cohorte  # noqa: E402
from tfc_voz.fenotipo import generar_fenotipos, oraculo  # noqa: E402
from tfc_voz.genotipo import SEMILLA  # noqa: E402
from tfc_voz.parametros import NIVELES, PARAMETROS  # noqa: E402
from tfc_voz.poblacion import EFECTOS  # noqa: E402

COLUMNAS = ["replica", "semilla", "dominio", "sexo",
            "individuo_id", "particion", "rasgo", "y_real", "mu_oraculo", "sigma_oraculo"]
PARTICIONES = ("calibracion", "prueba")
DOMINIO = "voz"
NIVEL = "caso_base"
NOTA_PUNTAJE = ("g = g_conocida + g_resto. En f0_medio, f1 y f2, g_conocida sale de las tres variantes "
                "publicadas (Gisladottir 2023, S8): copias del archivo datos/genotipos_voz_1000g.csv en las "
                "503 personas reales de 1000 Genomes y sorteadas en las simuladas, centradas por la "
                "frecuencia de la subpoblacion; g_resto es simulado. En los otros cinco, g es enteramente "
                "simulado. Reemplaza a la version con g enteramente simulado (huella b6f8d2d8...).")

SORTEO_GENOTIPOS = ("Asimetria declarada (confirmada por Diego el 12/11): las 503 personas reales de 1000 Genomes "
                    "aportan un genotipo fijo, el del archivo, igual en las 20 replicas; las 1.497 simuladas "
                    "reciben un sorteo nuevo de sus copias en cada replica, con la semilla de la replica. La "
                    "cohorte fija a la persona (id, subpoblacion, sexo, edad y particion); el genotipo de las "
                    "simuladas es parte de la simulacion del modulo, como g_resto, y promediar sobre su sorteo "
                    "hace que el promedio de las 20 replicas converja al nivel declarado.")


def armar_replica(cohorte, replica, parametros=PARAMETROS, efectos=EFECTOS):
    """Filas de calibracion y prueba de una replica, con y real, media y desvio oraculo."""
    semilla = SEMILLA + replica
    fenotipos = generar_fenotipos(cohorte, parametros, efectos, semilla)
    datos = (oraculo(cohorte, fenotipos, parametros, efectos)
             .merge(fenotipos[["individuo_id", "rasgo", "y"]], on=["individuo_id", "rasgo"])
             .merge(cohorte[["individuo_id", "particion", "sexo"]], on="individuo_id")
             .rename(columns={"y": "y_real"})
             .assign(replica=replica, semilla=semilla, dominio=DOMINIO))
    return datos[datos["particion"].isin(PARTICIONES)].reset_index(drop=True)[COLUMNAS]


def armar_datos(cohorte, parametros=PARAMETROS, efectos=EFECTOS, replicas=predictions.REPLICAS):
    """Las replicas 0 a replicas - 1, una debajo de la otra."""
    return pd.concat([armar_replica(cohorte, r, parametros, efectos) for r in range(replicas)],
                     ignore_index=True)


def validar(datos, cohorte, parametros=PARAMETROS, replicas=predictions.REPLICAS):
    """Levanta AssertionError si el archivo no cumple lo que espera la capa de calibracion."""
    if list(datos.columns) != COLUMNAS:
        raise AssertionError(f"columnas {list(datos.columns)}, se esperaba {COLUMNAS}")
    if datos.duplicated(["individuo_id", "rasgo", "replica"]).any():
        raise AssertionError("hay mas de una fila por (individuo_id, rasgo, replica)")
    if set(datos["replica"]) != set(range(replicas)):
        raise AssertionError(f"replicas {sorted(set(datos['replica']))}, se esperaban 0 a {replicas - 1}")
    if not (datos["semilla"] == SEMILLA + datos["replica"]).all():
        raise AssertionError(f"hay filas cuya semilla no es {SEMILLA} + replica")
    if not (datos["dominio"] == DOMINIO).all():
        raise AssertionError(f"hay filas con dominio distinto de {DOMINIO!r}")
    rasgos = {p.nombre for p in parametros}
    if set(datos["rasgo"]) != rasgos:
        raise AssertionError(f"rasgos {sorted(set(datos['rasgo']))}, se esperaba {sorted(rasgos)}")
    esperado = cohorte.loc[cohorte["particion"].isin(PARTICIONES), ["individuo_id", "particion", "sexo"]]
    esperado = set(esperado.itertuples(index=False, name=None))
    for (replica, rasgo), grupo in datos.groupby(["replica", "rasgo"]):
        obtenido = set(grupo[["individuo_id", "particion", "sexo"]].itertuples(index=False, name=None))
        if obtenido != esperado:
            raise AssertionError(f"replica {replica}, rasgo {rasgo}: los ids, las particiones o el sexo "
                                 "no coinciden con la cohorte")
    numericos = datos[["y_real", "mu_oraculo", "sigma_oraculo"]].to_numpy()
    if not np.isfinite(numericos).all():
        raise AssertionError("hay valores no finitos")
    if not (datos["sigma_oraculo"] > 0).all():
        raise AssertionError("hay sigma_oraculo no positivo")


def escribir(datos, ruta, ruta_cohorte):
    """Escribe el CSV (finales de linea LF) y su .meta.json. Devuelve la ruta del meta."""
    ruta = Path(ruta)
    datos.to_csv(ruta, index=False, lineterminator="\n")
    cohorte_meta = json.loads(Path(ruta_cohorte).with_suffix(".meta.json").read_text(encoding="utf-8"))
    meta = {
        "archivo": ruta.name,
        "generado": date.today().isoformat(),
        "sha256": hashlib.sha256(ruta.read_bytes()).hexdigest(),
        "filas": len(datos),
        "columnas": COLUMNAS,
        "cohorte": {"version": cohorte_meta["version"], "sha256_csv": cohorte_meta["sha256_csv"]},
        "particiones": list(PARTICIONES),
        "replicas": sorted(int(r) for r in datos["replica"].unique()),
        "semilla_base": SEMILLA,
        "semillas": f"{SEMILLA} + replica",
        "versiones": {"anima_spine": anima_spine.__version__, "numpy": np.__version__,
                      "pandas": pd.__version__, "python": platform.python_version()},
        "nivel_declarado": {
            "nivel": NIVEL,
            "descripcion": NIVELES.describir(NIVEL),
            "archivo": f"config/{NIVELES.ruta.name}",
            "version": NIVELES.version,
            "fijado": NIVELES.fijado,
            "valores": NIVELES.de(NIVEL),
        },
        "puntaje_genetico": NOTA_PUNTAJE,
        "sorteo_genotipos": SORTEO_GENOTIPOS,
        "oraculo": "mu_oraculo = m + s * g y sigma_oraculo = s * sqrt(1 - h2): media y desvio verdaderos, "
                   "conocidos por diseno. No son predicciones de ningun modelo.",
    }
    ruta_meta = ruta.with_name(ruta.stem + ".meta.json")
    ruta_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta_meta


def main():
    ap = argparse.ArgumentParser(description="Datos de Voz para la capa de calibracion comun")
    ap.add_argument("--cohorte", type=Path, default=RAIZ / "cohorte_anima.csv")
    ap.add_argument("--salida", type=Path, default=RAIZ / "informes" / "voz_para_calibracion.csv")
    args = ap.parse_args()

    cohorte = leer_cohorte(args.cohorte)
    datos = armar_datos(cohorte)
    validar(datos, cohorte)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_meta = escribir(datos, args.salida, args.cohorte)
    print(f"{args.salida}: {len(datos)} filas, validacion OK")
    print(f"{ruta_meta}")
    print(NIVELES.describir(NIVEL))
    print(datos.groupby(["rasgo", "particion"]).size().unstack().to_string())


if __name__ == "__main__":
    main()
