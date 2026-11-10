"""
Cargador de los niveles declarados del modulo (config/niveles_declarados.json).

Es el UNICO lugar de donde salen las h2: ningun .py las escribe a mano
(tests/test_niveles.py lo controla). Hay dos niveles declarados:

  caso_base      h2-SNP por parametro (Gisladottir 2023, S6). Con estos se
                 generan siempre los fenotipos.
  segundo_nivel  lo que explican las tres variantes publicadas (S8),
                 2pq * beta^2 por parametro; cero en los cinco sin variante.

Los niveles se fijan antes de la primera corrida y no se eligen mirando
resultados. Para cambiarlos se cambia el archivo, que lleva version y fecha.
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path

RUTA = Path(__file__).resolve().parents[2] / "config" / "niveles_declarados.json"
NOMBRES_NIVEL = ("caso_base", "segundo_nivel")
# El JSON redondea los agregados y el segundo nivel a 6 decimales.
TOLERANCIA_REDONDEO = 1e-6


@dataclass(frozen=True)
class Variante:
    rs: str
    parametro: str
    alelo_efecto: str
    beta: float
    frecuencias: dict  # frecuencia del alelo de efecto por subpoblacion

    @property
    def frecuencia_europea(self):
        """Promedio simple de las cinco subpoblaciones."""
        return sum(self.frecuencias.values()) / len(self.frecuencias)

    @property
    def varianza(self):
        """2pq * beta^2 con la frecuencia europea promedio."""
        p = self.frecuencia_europea
        return 2.0 * p * (1.0 - p) * self.beta ** 2


@dataclass(frozen=True)
class NivelesDeclarados:
    version: str
    fijado: str
    nota: str
    fuentes: dict
    salvedades: dict
    niveles: dict             # {nivel: {parametro: valor}}
    agregados_esperados: dict
    variantes: tuple
    ruta: Path

    @property
    def parametros(self):
        return list(self.niveles["caso_base"])

    def de(self, nivel):
        """{parametro: valor} de un nivel declarado."""
        if nivel not in self.niveles:
            raise KeyError(f"nivel {nivel!r} desconocido: {list(self.niveles)}")
        return dict(self.niveles[nivel])

    def agregado(self, nivel):
        valores = self.niveles[nivel].values()
        return sum(valores) / len(valores)

    def varianza_conocida(self):
        """V por parametro: suma de 2pq * beta^2 de sus variantes (0 si no tiene)."""
        v = {nombre: 0.0 for nombre in self.parametros}
        for var in self.variantes:
            v[var.parametro] += var.varianza
        return v

    def describir(self, nivel):
        """Renglon para el reporte: que nivel se uso, de que archivo, version y fecha."""
        return (f"Nivel declarado: {nivel} (agregado {100 * self.agregado(nivel):.3f} %), "
                f"de {self.ruta.name}, version {self.version}, fijado el {self.fijado}. "
                f"Fuente: {self.fuentes[nivel]}.")


def cargar(ruta=RUTA):
    """Lee y valida el archivo de niveles declarados. Levanta ValueError si no cierra."""
    ruta = Path(ruta)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    niveles = NivelesDeclarados(
        version=datos["version"],
        fijado=datos["fijado"],
        nota=datos.get("nota", ""),
        fuentes=datos["fuentes"],
        salvedades=datos.get("salvedades", {}),
        niveles={n: {k: float(v) for k, v in datos["niveles"][n].items()} for n in datos["niveles"]},
        agregados_esperados={k: float(v) for k, v in datos["agregados_esperados"].items()},
        variantes=tuple(Variante(v["rs"], v["parametro"], v["alelo_efecto"], float(v["beta"]),
                                 {k: float(f) for k, f in v["frecuencias"].items()})
                        for v in datos["variantes"]),
        ruta=ruta,
    )
    _validar(niveles)
    return niveles


def _validar(nd):
    if tuple(nd.niveles) != NOMBRES_NIVEL:
        raise ValueError(f"niveles {list(nd.niveles)}, se esperaba {list(NOMBRES_NIVEL)}")
    nombres = nd.parametros
    for nivel, valores in nd.niveles.items():
        if list(valores) != nombres:
            raise ValueError(f"{nivel}: parametros {list(valores)}, se esperaba {nombres}")
        for nombre, valor in valores.items():
            if not (math.isfinite(valor) and 0.0 <= valor < 1.0):
                raise ValueError(f"{nivel}, {nombre}: {valor} fuera de [0, 1)")
        if nivel not in nd.fuentes:
            raise ValueError(f"{nivel}: falta su fuente")
        esperado = nd.agregados_esperados[nivel]
        if abs(nd.agregado(nivel) - esperado) > TOLERANCIA_REDONDEO:
            raise ValueError(f"{nivel}: el agregado da {nd.agregado(nivel):.6f}, se esperaba {esperado}")
    for var in nd.variantes:
        if var.parametro not in nombres:
            raise ValueError(f"{var.rs}: parametro {var.parametro!r} desconocido")
        if not all(0.0 <= f <= 1.0 for f in var.frecuencias.values()):
            raise ValueError(f"{var.rs}: frecuencia fuera de [0, 1]")
    # El segundo nivel es la varianza de la parte conocida: si la cuenta no da, hay un error.
    caso_base, segundo = nd.de("caso_base"), nd.de("segundo_nivel")
    for nombre, v in nd.varianza_conocida().items():
        if abs(v - segundo[nombre]) > TOLERANCIA_REDONDEO:
            raise ValueError(f"{nombre}: 2pq * beta^2 da {v:.6f} y el segundo nivel dice {segundo[nombre]}")
        if v > caso_base[nombre]:
            raise ValueError(f"{nombre}: la varianza conocida ({v:.6f}) supera la h2 del caso base "
                             f"({caso_base[nombre]})")
