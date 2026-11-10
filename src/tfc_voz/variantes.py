"""
Parte conocida del puntaje genetico: las tres variantes publicadas de la
tabla S8 de Gisladottir 2023 (punto 7 de la entrega del 9/11).

    g = g_conocida + g_resto

  g_conocida  solo en los parametros con variante: suma de
              beta * (copias - 2 * p_s), con p_s la frecuencia del alelo de
              efecto en la subpoblacion de la persona (la de la
              configuracion, unica fuente de p; respuesta del 9/11).
              - Personas reales de 1000 Genomes: copias del archivo de genotipos.
              - Personas simuladas: copias ~ Binomial(2, p_s).
              El centrado por subpoblacion deja a g_conocida ortogonal a la
              subpoblacion: la diferencia de frecuencias entre poblaciones es
              ancestria, no efecto del genotipo.
  g_resto     normal con varianza h2 - V (fenotipo.py), con V el segundo
              nivel declarado. Asi Var(g) = h2.

Los genotipos los paso Diego como archivo (datos/genotipos_voz_1000g.csv);
no se descarga nada. Se verifican contra la huella de su .meta.json, y la
frecuencia observada contra la configurada: si se aparta mas de 10 puntos en
alguna subpoblacion, el alelo puede estar invertido y se levanta un error
sin corregir nada.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RUTA_GENOTIPOS = RAIZ / "datos" / "genotipos_voz_1000g.csv"
TOLERANCIA_ALINEACION = 0.10
COPIAS_VALIDAS = {0, 1, 2}


def reales(cohorte):
    """Mascara de las personas reales de 1000 Genomes."""
    if "origen" not in cohorte:
        return np.zeros(len(cohorte), dtype=bool)
    return (cohorte["origen"] == "1000g").to_numpy()


def cargar_genotipos(variantes, ruta=RUTA_GENOTIPOS):
    """Copias del alelo de efecto por muestra de 1000 Genomes: DataFrame indexado por muestra_1000g.

    Verifica la huella del .meta.json, las columnas (una por variante) y que
    las copias sean 0, 1 o 2.
    """
    ruta = Path(ruta)
    meta = json.loads(ruta.with_name(ruta.stem + ".meta.json").read_text(encoding="utf-8"))
    huella = hashlib.sha256(ruta.read_bytes()).hexdigest()
    if huella != meta["sha256"]:
        raise ValueError(f"{ruta.name}: la huella {huella[:12]}... no coincide con la de su .meta.json "
                         f"({meta['sha256'][:12]}...)")
    genotipos = pd.read_csv(ruta, dtype={"muestra_1000g": str})
    esperadas = ["muestra_1000g"] + [v.rs for v in variantes]
    if list(genotipos.columns) != esperadas:
        raise ValueError(f"{ruta.name}: columnas {list(genotipos.columns)}, se esperaba {esperadas}")
    if not genotipos["muestra_1000g"].is_unique:
        raise ValueError(f"{ruta.name}: muestras repetidas")
    for v in variantes:
        if not set(genotipos[v.rs]) <= COPIAS_VALIDAS:
            raise ValueError(f"{ruta.name}: {v.rs} tiene copias fuera de 0, 1 y 2")
    return genotipos.set_index("muestra_1000g")


def copias_de_reales(cohorte, genotipos, rs):
    """Copias de una variante para las personas reales de la cohorte, en su orden."""
    muestras = cohorte.loc[reales(cohorte), "muestra_1000g"].astype(str)
    faltan = sorted(set(muestras) - set(genotipos.index))
    if faltan:
        raise ValueError(f"faltan genotipos de {len(faltan)} personas reales, por ejemplo {faltan[0]}")
    return genotipos.loc[muestras, rs].to_numpy()


def verificar_alineacion(cohorte, genotipos, variantes):
    """Frecuencia observada en las personas reales contra la configurada, por subpoblacion.

    Devuelve el mayor desvio. Si alguno supera TOLERANCIA_ALINEACION, el alelo
    puede estar invertido: ValueError con la variante, sin corregir nada.
    """
    mascara = reales(cohorte)
    subpob = cohorte.loc[mascara, "subpoblacion"].to_numpy()
    mayor = 0.0
    for v in variantes:
        copias = copias_de_reales(cohorte, genotipos, v.rs)
        for s, p in v.frecuencias.items():
            de_s = subpob == s
            if not de_s.any():
                continue
            observada = copias[de_s].mean() / 2.0
            desvio = abs(observada - p)
            if desvio > TOLERANCIA_ALINEACION:
                raise ValueError(f"{v.rs} ({v.parametro}), subpoblacion {s}: frecuencia observada "
                                 f"{observada:.3f} y configurada {p:.3f}. El alelo de efecto puede estar "
                                 "invertido: no se corrige, hay que revisarlo con Diego")
            mayor = max(mayor, desvio)
    return mayor


def frecuencias_de(cohorte, variante):
    """p de la subpoblacion de cada persona, para una variante."""
    desconocidas = set(cohorte["subpoblacion"]) - set(variante.frecuencias)
    if desconocidas:
        raise ValueError(f"{variante.rs}: sin frecuencia para {sorted(desconocidas)}")
    return cohorte["subpoblacion"].map(variante.frecuencias).to_numpy(dtype=float)


def copias(cohorte, variante, genotipos, rng):
    """Copias del alelo de efecto de cada persona: del archivo las reales, sorteadas las simuladas.

    Se sortea para todas (asi el consumo del generador no depende de cuantas
    reales haya) y despues se reemplazan las reales por las del archivo.
    """
    p = frecuencias_de(cohorte, variante)
    resultado = rng.binomial(2, p).astype(float)
    mascara = reales(cohorte)
    if mascara.any():
        if genotipos is None:
            raise ValueError("la cohorte tiene personas reales y no se pasaron sus genotipos")
        resultado[mascara] = copias_de_reales(cohorte, genotipos, variante.rs)
    return resultado


def puntaje_conocido(cohorte, variantes, genotipos, rng):
    """g_conocida: suma sobre las variantes de beta * (copias - 2 * p_s). Cero si no hay variantes."""
    g = np.zeros(len(cohorte))
    for v in variantes:
        g += v.beta * (copias(cohorte, v, genotipos, rng) - 2.0 * frecuencias_de(cohorte, v))
    return g
