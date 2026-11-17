"""
Simulacion del nulo para fijar la tolerancia del criterio de recuperacion
(respuesta de Diego del 12/11).

Genera datos con el nivel declarado del caso base y la maquinaria del modulo
tal cual (correr_replica y filas_recuperacion, el mismo camino que la corrida
oficial), promedia 20 replicas y lo repite N veces. Informa, por parametro y
para el agregado del dominio (el que evalua predictions.criterio_recuperacion),
el corrimiento del DeltaR2 parcial promedio respecto del nivel declarado, su
desvio y sus percentiles, y la proporcion de repeticiones que pasarian con
cada tolerancia candidata.

Las semillas son 20261019 + 100000 + 20 k + r (repeticion k, replica r): no se
cruzan con las de la corrida oficial (20261019 + r) ni con las de los tests.
La tolerancia se fija con este resultado, una vez y ANTES de ver la corrida
oficial; nunca despues.

Uso (parado en la raiz del proyecto):
    python scripts/simular_nulo.py --repeticiones 200
"""

import argparse
import json
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ)]
import anima_spine  # noqa: E402
from anima_spine import predictions  # noqa: E402
from tfc_voz.cohorte import leer_cohorte  # noqa: E402
from tfc_voz.genotipo import SEMILLA  # noqa: E402
from tfc_voz.parametros import NIVELES  # noqa: E402
from tfc_voz.recuperacion import NIVEL_CON_CRITERIO, barrido_recuperacion  # noqa: E402

SEMILLA_NULO = SEMILLA + 100_000
TOLERANCIAS_CANDIDATAS = (0.015, 0.020, 0.025)
LINEA_BASE = NIVELES.criterio_recuperacion["linea_base"]


def semilla_base(k):
    return SEMILLA_NULO + predictions.REPLICAS * k


def una_repeticion(k, ruta_cohorte):
    """Promedio de las 20 replicas de la repeticion k, por rasgo y linea base."""
    cohorte = leer_cohorte(ruta_cohorte)
    filas = pd.DataFrame(barrido_recuperacion(cohorte, NIVEL_CON_CRITERIO, semilla_base=semilla_base(k)))
    promedio = (filas.groupby(["rasgo", "linea_base"])
                .agg(nivel_declarado=("nivel_declarado", "first"),
                     parcial_promedio=("delta_r2_parcial", "mean"),
                     total_promedio=("delta_r2_total", "mean"))
                .reset_index())
    return promedio.assign(repeticion=k, semilla_base=semilla_base(k))


def resumir(datos, linea_base=LINEA_BASE, tolerancias=TOLERANCIAS_CANDIDATAS):
    """Corrimiento por rasgo y del agregado, y tasas de aprobacion por tolerancia."""
    d = datos[datos["linea_base"] == linea_base].assign(
        corrimiento=lambda x: x["parcial_promedio"] - x["nivel_declarado"])
    por_rasgo = {
        rasgo: {
            "nivel_declarado": float(g["nivel_declarado"].iloc[0]),
            "corrimiento_medio": float(g["corrimiento"].mean()),
            "desvio": float(g["corrimiento"].std(ddof=1)),
            "p2_5": float(g["corrimiento"].quantile(0.025)),
            "p97_5": float(g["corrimiento"].quantile(0.975)),
        }
        for rasgo, g in d.groupby("rasgo")
    }
    ancho = d.pivot(index="repeticion", columns="rasgo", values="corrimiento")
    agregado = ancho.mean(axis=1)
    peor = ancho.abs().max(axis=1)
    tasas = {
        f"{t:.3f}": {
            "pasa_cada_rasgo": {r: float((ancho[r].abs() <= t).mean()) for r in ancho.columns},
            "pasan_los_8_juntos": float((peor <= t).mean()),
            "pasa_el_agregado": float((agregado.abs() <= t).mean()),
        }
        for t in tolerancias
    }
    return {
        "linea_base": linea_base,
        "repeticiones": int(len(ancho)),
        "por_rasgo": por_rasgo,
        "agregado": {
            "corrimiento_medio": float(agregado.mean()),
            "desvio": float(agregado.std(ddof=1)),
            "p2_5": float(agregado.quantile(0.025)),
            "p97_5": float(agregado.quantile(0.975)),
        },
        "tasas_de_aprobacion": tasas,
    }


def main():
    ap = argparse.ArgumentParser(description="Simulacion del nulo del criterio de recuperacion")
    ap.add_argument("--repeticiones", type=int, default=200)
    ap.add_argument("--procesos", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--cohorte", type=Path, default=RAIZ / "cohorte_anima.csv")
    ap.add_argument("--salida", type=Path, default=RAIZ / "informes" / "simulacion_nulo_voz.csv")
    args = ap.parse_args()

    inicio = time.time()
    partes = []
    with ProcessPoolExecutor(max_workers=args.procesos) as ejecutor:
        futuros = [ejecutor.submit(una_repeticion, k, args.cohorte) for k in range(args.repeticiones)]
        for hechos, futuro in enumerate(as_completed(futuros), 1):
            partes.append(futuro.result())
            if hechos % 10 == 0 or hechos == args.repeticiones:
                print(f"{hechos}/{args.repeticiones} repeticiones ({time.time() - inicio:.0f} s)", flush=True)
    datos = (pd.concat(partes, ignore_index=True)
             .sort_values(["repeticion", "rasgo", "linea_base"])
             [["repeticion", "semilla_base", "rasgo", "linea_base", "nivel_declarado",
               "parcial_promedio", "total_promedio"]])
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(args.salida, index=False, lineterminator="\n")
    meta = {
        "archivo": args.salida.name,
        "generado": date.today().isoformat(),
        "repeticiones": args.repeticiones,
        "replicas_por_repeticion": predictions.REPLICAS,
        "semillas": f"{SEMILLA_NULO} + {predictions.REPLICAS} * repeticion + replica",
        "nivel": NIVEL_CON_CRITERIO,
        "niveles_declarados": {"version": NIVELES.version, "fijado": NIVELES.fijado},
        "versiones": {"anima_spine": anima_spine.__version__, "numpy": np.__version__,
                      "pandas": pd.__version__, "python": platform.python_version()},
        "duracion_s": round(time.time() - inicio),
        "resumen": resumir(datos),
    }
    ruta_meta = args.salida.with_name(args.salida.stem + ".meta.json")
    ruta_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{args.salida}: {len(datos)} filas; resumen en {ruta_meta.name}")


if __name__ == "__main__":
    main()
