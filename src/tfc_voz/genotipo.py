"""
Generador de genotipo sintetico -- Opcion A (polygenic score simple).

Para cada parametro acustico, el efecto genetico se resume en un solo
polygenic score (PGS) con varianza igual a su heredabilidad SNP (h2).
El resto de la varianza fenotipica se atribuye a un termino ambiental.

    score_genetico   ~ N(0, h2)
    score_ambiental  ~ N(0, 1 - h2)
    score_total = score_genetico + score_ambiental   (varianza total = 1)

El score_total queda estandarizado (media 0, varianza 1); se reescala a
las unidades reales de cada parametro recien al construir la cohorte
completa con medias y desvios poblacionales (eso es trabajo de la Fase 2,
no de este archivo).
"""

from dataclasses import dataclass, field

import numpy as np

try:  # funciona importado como paquete (from tfc_voz.genotipo import ...)
    from .parametros import PARAMETROS
except ImportError:  # y tambien corriendo el archivo directo (python genotipo.py)
    from parametros import PARAMETROS


@dataclass
class IndividuoSintetico:
    id: int
    scores_geneticos: dict = field(default_factory=dict)
    scores_ambientales: dict = field(default_factory=dict)

    def score_total(self, parametro: str) -> float:
        return self.scores_geneticos[parametro] + self.scores_ambientales[parametro]


def generar_cohorte_sintetica(n_individuos: int, semilla: int = 42) -> list[IndividuoSintetico]:
    """Genera una cohorte de individuos sinteticos siguiendo la Opcion A."""
    rng = np.random.default_rng(semilla)
    cohorte = []

    for i in range(n_individuos):
        ind = IndividuoSintetico(id=i)
        for p in PARAMETROS:
            ind.scores_geneticos[p.nombre] = rng.normal(0, np.sqrt(p.heredabilidad))
            ind.scores_ambientales[p.nombre] = rng.normal(0, np.sqrt(1 - p.heredabilidad))
        cohorte.append(ind)

    return cohorte


if __name__ == "__main__":
    cohorte = generar_cohorte_sintetica(5)
    for ind in cohorte:
        print(f"Individuo {ind.id}: F0 score total = {ind.score_total('f0_medio'):+.3f}   "
              f"VTL score total = {ind.score_total('vtl'):+.3f}")
