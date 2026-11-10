"""
Calculo del segundo nivel declarado: se corre UNA vez, cuando cambian las
variantes o la composicion de la cohorte, y sus numeros se copian a
config/niveles_declarados.json (segundo_nivel, agregados_esperados y
composicion_cohorte), con una version nueva del archivo.

    V = suma_s  w_s * 2 * p_s * (1 - p_s) * beta^2

con p_s la frecuencia del alelo de efecto en la subpoblacion (la misma que
centra g_conocida) y w_s la fraccion de la cohorte en cada subpoblacion.

El cargador (niveles.py) no recalcula: verifica que la cohorte tenga la
composicion registrada (respuesta de Diego del 9/11, tercera vuelta).

Uso (parado en la raiz del proyecto):
    python scripts/calcular_segundo_nivel.py
"""

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ)]
from tfc_voz.cohorte import leer_cohorte  # noqa: E402
from tfc_voz.niveles import RUTA, cargar, composicion_de  # noqa: E402


def segundo_nivel(niveles, composicion):
    """{parametro: V} para una composicion; cero en los parametros sin variante."""
    v = {nombre: 0.0 for nombre in niveles.parametros}
    for var in niveles.variantes:
        v[var.parametro] += var.varianza(composicion)
    return v


def main():
    ap = argparse.ArgumentParser(description="Calcula el segundo nivel declarado para una cohorte")
    ap.add_argument("--cohorte", type=Path, default=RAIZ / "cohorte_anima.csv")
    args = ap.parse_args()

    cohorte = leer_cohorte(args.cohorte)
    niveles = cargar(RUTA)  # la configuracion vigente, verificada contra la cohorte del repo
    v = segundo_nivel(niveles, composicion_de(cohorte))
    escrito = niveles.de("segundo_nivel")
    print(f"Cohorte: {args.cohorte.name}, {len(cohorte)} personas")
    print(json.dumps({"conteos": cohorte["subpoblacion"].value_counts().sort_index().to_dict()}))
    print(f"{'parametro':16s} {'V calculado':>12s} {'escrito':>10s}")
    for nombre in niveles.parametros:
        print(f"{nombre:16s} {v[nombre]:12.6f} {escrito[nombre]:10.6f}")
    print(f"{'agregado':16s} {sum(v.values()) / len(v):12.6f} {niveles.agregado('segundo_nivel'):10.6f}")


if __name__ == "__main__":
    main()
