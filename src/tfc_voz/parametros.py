"""
Definicion del espacio de parametros acusticos del modulo de Voz (Anima).

Cada parametro lleva su heredabilidad de referencia (h2) y el nivel de
evidencia que la respalda:

  "directa"  -> h2-SNP reportado explicitamente para ESE parametro acustico
                (Gisladottir et al. 2023, tabla S6). Es la escala en la que
                trabaja el modelo.
  "derivada" -> el valor publicado existe pero esta en OTRA escala y hubo
                que convertirlo. Hoy ningun parametro esta en este nivel.
  "debil"    -> la literatura existe pero es de muestra chica, resultados
                contradictorios o no significativos; el valor es conservador.

REGLA DE LECTURA DE LA S6 (aprobada por Diego el 20/10/2026): regla
agregada de cinco vocales. Para cada parametro se toma la fila de la S6
medida sobre el conjunto de las vocales [i, a, o, u, e] (columna Measure
terminada en _MeasureVowels, o la fila VTL), no el maximo entre tareas ni
entre vocales sueltas. Los maximos que se usaban antes quedan en
H2_MAXIMOS, solo para un analisis de sensibilidad. tests/test_parametros.py
contrasta las h2 contra referencias/tabla-s6-heredabilidades.csv.

LAS h2 NO SE ESCRIBEN ACA: salen del nivel "caso_base" de
config/niveles_declarados.json, a traves de niveles.py (entrega del 9/11).
Ningun .py las escribe a mano; tests/test_niveles.py lo controla.

Cuatro parametros (f0_variabilidad, f1, f3, vtl) tienen un IC95% que cruza
el cero. Es lo que reporta la S6, no un error de carga.

ESCALA: Gisladottir log-transformo cada rasgo y lo ajusto por edad, IMC,
altura y microfono, por separado dentro de cada sexo, ANTES de estimar h2.
Las h2-SNP de este archivo estan entonces por encima de sexo, edad y
altura, no incluidas en ellas. Queda abierto si son fraccion de la varianza
residual (despues del ajuste) y no de la total; si es asi, el techo del
DeltaR2 sobre una linea base con sexo y edad es h2 * (1 - R2 de la linea
base). Se declara como limitacion.

IMPORTANTE (para la memoria y la defensa): h2 de gemelos y h2-SNP NO son
lo mismo. El h2 de gemelos captura toda la varianza genetica aditiva; el
h2-SNP solo la que explican las variantes comunes genotipadas, y suele ser
bastante menor. Mezclar ambos sin aclararlo inflaria artificialmente el
aporte genetico de los parametros medidos en gemelos.
"""

from dataclasses import dataclass

from tfc_voz.niveles import cargar

NIVELES = cargar()
_H2 = NIVELES.de("caso_base")


@dataclass(frozen=True)
class ParametroAcustico:
    nombre: str
    unidad: str
    heredabilidad: float  # fraccion de varianza fenotipica, escala h2-SNP
    evidencia: str        # "directa" | "derivada" | "debil"
    fuente: str
    ic95_inf: float | None = None  # IC95% de la S6; None si no hay fila
    ic95_sup: float | None = None
    fila_s6: str | None = None     # columna Measure de la tabla S6


PARAMETROS = [
    ParametroAcustico(
        "f0_medio", "Hz", _H2["f0_medio"], "directa",
        "Gisladottir et al. 2023, Science Advances, tabla S6, fila "
        "MedianF0_MeasureVowels: h2-SNP 10.27% (IC95% 3.4-17.2%)",
        0.033512, 0.171888, "MedianF0_MeasureVowels",
    ),
    ParametroAcustico(
        "f0_variabilidad", "Hz (SD)", _H2["f0_variabilidad"], "directa",
        "Gisladottir et al. 2023, tabla S6, fila StdF0_MeasureVowels: "
        "h2-SNP 4.10% (IC95% -3.0-11.2%)",
        -0.030344, 0.112344, "StdF0_MeasureVowels",
    ),
    ParametroAcustico(
        "jitter", "%", _H2["jitter"], "debil",
        "No esta en la S6. Van Lierde et al. 2005 (J Voice) NO obtuvo "
        "correlacion significativa para jitter en gemelos monocigoticos; "
        "Lima et al. 2024 (gemelas brasileras) reporta ICC intra-par MZ debil "
        "de 0.374 (IC95% 0.11-0.59). Evidencia contradictoria y de muestra "
        "chica -> valor conservador. Coherente con Gisladottir: 41 de 72 "
        "medidas acusticas tienen h2-SNP < 5%",
    ),
    ParametroAcustico(
        "hnr", "dB", _H2["hnr"], "debil",
        "No esta en la S6. Lima et al. 2024 reporta ICC intra-par MZ debil "
        "de 0.366 (IC95% 0.10-0.59) para HNR; sin estimacion de h2-SNP "
        "publicada. Valor conservador, mismo criterio que jitter",
    ),
    ParametroAcustico(
        "f1", "Hz", _H2["f1"], "directa",
        "Gisladottir et al. 2023, tabla S6, fila MedianF1_MeasureVowels: "
        "h2-SNP 6.19% (IC95% -0.9-13.3%)",
        -0.009052, 0.132852, "MedianF1_MeasureVowels",
    ),
    ParametroAcustico(
        "f2", "Hz", _H2["f2"], "directa",
        "Gisladottir et al. 2023, tabla S6, fila MedianF2_MeasureVowels: "
        "h2-SNP 13.53% (IC95% 6.6-20.5%)",
        0.065524, 0.205076, "MedianF2_MeasureVowels",
    ),
    ParametroAcustico(
        "f3", "Hz", _H2["f3"], "directa",
        "Gisladottir et al. 2023, tabla S6, fila MedianF3_MeasureVowels: "
        "h2-SNP 6.44% (IC95% -0.1-13.0%)",
        -0.000868, 0.129668, "MedianF3_MeasureVowels",
    ),
    ParametroAcustico(
        "vtl", "cm", _H2["vtl"], "directa",
        "Gisladottir et al. 2023, tabla S6, fila VTL (medida agregada de "
        "F1-F4 sobre las cinco vocales): h2-SNP 6.06% (IC95% -0.9-13.0%). "
        "Reemplaza el 0.13 anterior, que salia de deflacionar a la mitad el "
        "h2 de gemelos de Dediu et al. 2022 (0.26)",
        -0.00898, 0.13018, "VTL",
    ),
]

if [p.nombre for p in PARAMETROS] != NIVELES.parametros:
    raise ValueError(f"los parametros de {NIVELES.ruta.name} no coinciden con PARAMETROS")

# Maximos de la S6 que se usaban antes de adoptar la regla agregada.
# El modelo NO los usa; quedan para un analisis de sensibilidad posterior.
# VTL no tiene maximo: su valor anterior (0.13) venia de gemelos, otra escala.
H2_MAXIMOS = {
    "f0_medio": 0.1675,         # MedianF0_MeasureReading
    "f0_variabilidad": 0.1276,  # StdF0_MeasureReading
    "f1": 0.0872,               # MedianF1_MeasureA
    "f2": _H2["f2"],            # MedianF2_MeasureVowels (coincide con la regla)
    "f3": 0.0815,               # MedianF3_MeasureO
}


def por_evidencia(nivel: str):
    return [p for p in PARAMETROS if p.evidencia == nivel]


if __name__ == "__main__":
    for nivel, titulo in [
        ("directa", "Ancla directa (h2-SNP publicado para el parametro)"),
        ("derivada", "Derivada (publicada en otra escala, convertida)"),
        ("debil", "Evidencia debil (valor conservador)"),
    ]:
        ps = por_evidencia(nivel)
        if not ps:
            continue
        print(f"\n{titulo}:")
        for p in ps:
            ic = (f"IC95% [{p.ic95_inf:+.4f}, {p.ic95_sup:+.4f}]  S6: {p.fila_s6}"
                  if p.fila_s6 else "sin IC (no esta en la S6)")
            print(f"  {p.nombre:16s} h2={p.heredabilidad:.4f}  [{p.unidad}]  {ic}")

    promedio = sum(p.heredabilidad for p in PARAMETROS) / len(PARAMETROS)
    print(f"\nPromedio de las {len(PARAMETROS)} h2: {promedio:.4f}")
