"""
Definicion del espacio de parametros acusticos del modulo de Voz (Anima).

Cada parametro lleva su heredabilidad de referencia (h2) y el nivel de
evidencia que la respalda:

  "directa"  -> h2-SNP reportado explicitamente para ESE parametro acustico
                (Gisladottir et al. 2023). Es la escala en la que trabaja
                el modelo.
  "derivada" -> el valor publicado existe pero esta en OTRA escala (h2 de
                gemelos, que incluye toda la varianza genetica aditiva, no
                solo la de variantes comunes) y hubo que convertirlo.
  "debil"    -> la literatura existe pero es de muestra chica, resultados
                contradictorios o no significativos; el valor es conservador.

IMPORTANTE (para la memoria y la defensa): h2 de gemelos y h2-SNP NO son
lo mismo. El h2 de gemelos captura toda la varianza genetica aditiva; el
h2-SNP solo la que explican las variantes comunes genotipadas, y suele ser
bastante menor. Mezclar ambos sin aclararlo inflaria artificialmente el
aporte genetico de los parametros medidos en gemelos.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ParametroAcustico:
    nombre: str
    unidad: str
    heredabilidad: float  # fraccion de varianza fenotipica, escala h2-SNP
    evidencia: str        # "directa" | "derivada" | "debil"
    fuente: str


PARAMETROS = [
    ParametroAcustico(
        "f0_medio", "Hz", 0.17, "directa",
        "Gisladottir et al. 2023, Science Advances -- h2-SNP 17% en lectura "
        "(IC95% 9-24%), el mas alto de las 72 medidas del estudio",
    ),
    ParametroAcustico(
        "f0_variabilidad", "Hz (SD)", 0.13, "directa",
        "Gisladottir et al. 2023 -- h2-SNP 13% para variabilidad del pitch",
    ),
    ParametroAcustico(
        "jitter", "%", 0.05, "debil",
        "Van Lierde et al. 2005 (J Voice) NO obtuvo correlacion significativa "
        "para jitter en gemelos monocigoticos; Lima et al. 2024 (gemelas "
        "brasileras) reporta ICC intra-par MZ debil de 0.374 (IC95% 0.11-0.59). "
        "Evidencia contradictoria y de muestra chica -> valor conservador. "
        "Coherente con Gisladottir: 41 de 72 medidas acusticas tienen h2-SNP < 5%",
    ),
    ParametroAcustico(
        "hnr", "dB", 0.05, "debil",
        "Lima et al. 2024 reporta ICC intra-par MZ debil de 0.366 "
        "(IC95% 0.10-0.59) para HNR; sin estimacion de h2-SNP publicada. "
        "Valor conservador, mismo criterio que jitter",
    ),
    ParametroAcustico(
        "f1", "Hz", 0.09, "directa",
        "Gisladottir et al. 2023 -- h2-SNP hasta 9% para F1",
    ),
    ParametroAcustico(
        "f2", "Hz", 0.14, "directa",
        "Gisladottir et al. 2023 -- h2-SNP hasta 14% para F2",
    ),
    ParametroAcustico(
        "f3", "Hz", 0.08, "directa",
        "Gisladottir et al. 2023 -- h2-SNP hasta 8% para F3",
    ),
    ParametroAcustico(
        "vtl", "cm", 0.13, "derivada",
        "Dediu et al. 2022 (Human Genetics), Tabla 2: SVTh = largo del tracto "
        "vocal supralaringeo horizontal, h2 de gemelos = 0.26 (IC95% 0.03-0.62), "
        "clase II; SVTv (vertical) = 0.24 (IC95% 0.00-0.74), clase IV. "
        "Ese 0.26 es h2 de GEMELOS, no h2-SNP: se deflaciona a la mitad (0.13) "
        "para ponerlo en la misma escala que el resto del espacio. El factor 1/2 "
        "es un supuesto explicito del proyecto, no un valor publicado",
    ),
]


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
            print(f"  {p.nombre:18s} h2={p.heredabilidad:.2f}  [{p.unidad}]")
