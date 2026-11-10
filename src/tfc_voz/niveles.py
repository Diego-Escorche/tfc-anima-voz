"""
Cargador de los niveles declarados del modulo (config/niveles_declarados.json).

Es el UNICO lugar de donde salen las h2: ningun .py las escribe a mano
(tests/test_niveles.py lo controla). Hay dos niveles declarados:

  caso_base      h2-SNP por parametro (Gisladottir 2023, S6; jitter y hnr,
                 valor conservador declarado). Con estos se generan siempre
                 los fenotipos.
  segundo_nivel  lo que explican las tres variantes publicadas (S8). Es
                 DERIVADO, no configurado (respuesta de Diego del 9/11):

                     V = suma_s  w_s * 2 * p_s * (1 - p_s) * beta^2

                 con p_s la frecuencia de la subpoblacion (la misma que centra
                 g_conocida) y w_s la fraccion de la cohorte en cada
                 subpoblacion. Los valores escritos en el JSON son control:
                 si V difiere en mas de la tolerancia, el cargador falla.

Los niveles se fijan antes de la primera corrida y no se eligen mirando
resultados. Para cambiarlos se cambia el archivo, que lleva version y fecha.
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path

from tfc_voz.cohorte import leer_cohorte

RAIZ = Path(__file__).resolve().parents[2]
RUTA = RAIZ / "config" / "niveles_declarados.json"
RUTA_COHORTE = RAIZ / "cohorte_anima.csv"
NOMBRES_NIVEL = ("caso_base", "segundo_nivel")
# El JSON redondea los agregados a 6 decimales.
TOLERANCIA_REDONDEO = 1e-6


@dataclass(frozen=True)
class Variante:
    rs: str
    parametro: str
    alelo_efecto: str
    beta: float
    frecuencias: dict  # frecuencia del alelo de efecto por subpoblacion

    def varianza(self, composicion):
        """Suma sobre subpoblaciones de w_s * 2 * p_s * (1 - p_s) * beta^2."""
        if set(composicion) != set(self.frecuencias):
            raise ValueError(f"{self.rs}: subpoblaciones {sorted(self.frecuencias)}, "
                             f"la cohorte tiene {sorted(composicion)}")
        return sum(w * 2.0 * self.frecuencias[s] * (1.0 - self.frecuencias[s]) * self.beta ** 2
                   for s, w in composicion.items())


@dataclass(frozen=True)
class NivelesDeclarados:
    version: str
    fijado: str
    nota: str
    fuentes: dict
    salvedades: dict
    niveles: dict             # {nivel: {parametro: valor}}; el segundo, derivado
    escrito_segundo_nivel: dict  # los valores del JSON, que son control
    tolerancia_control: float
    agregados_esperados: dict
    variantes: tuple
    composicion: dict         # {subpoblacion: fraccion de la cohorte}
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

    def describir(self, nivel):
        """Renglon para el reporte: que nivel se uso, de que archivo, version y fecha."""
        return (f"Nivel declarado: {nivel} (agregado {100 * self.agregado(nivel):.3f} %), "
                f"de {self.ruta.name}, version {self.version}, fijado el {self.fijado}. "
                f"Fuente: {self.fuentes[nivel]}.")


def composicion_de(cohorte):
    """Fraccion de la cohorte en cada subpoblacion."""
    conteo = cohorte["subpoblacion"].value_counts()
    return {s: float(c) / len(cohorte) for s, c in sorted(conteo.items())}


def _varianza_conocida(variantes, nombres, composicion):
    v = {nombre: 0.0 for nombre in nombres}
    for var in variantes:
        if var.parametro not in v:
            raise ValueError(f"{var.rs}: parametro {var.parametro!r} desconocido")
        v[var.parametro] += var.varianza(composicion)
    return v


def cargar(ruta=RUTA, cohorte=None):
    """Lee y valida el archivo de niveles declarados. Levanta ValueError si no cierra.

    cohorte: DataFrame de la cohorte de la que sale la composicion por
    subpoblacion; por defecto, cohorte_anima.csv.
    """
    ruta = Path(ruta)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if cohorte is None:
        cohorte = leer_cohorte(RUTA_COHORTE)
    composicion = composicion_de(cohorte)
    niveles = {n: {k: float(v) for k, v in datos["niveles"][n].items()} for n in datos["niveles"]}
    if tuple(niveles) != NOMBRES_NIVEL:
        raise ValueError(f"niveles {list(niveles)}, se esperaba {list(NOMBRES_NIVEL)}")
    variantes = tuple(Variante(v["rs"], v["parametro"], v["alelo_efecto"], float(v["beta"]),
                               {k: float(f) for k, f in v["frecuencias"].items()})
                      for v in datos["variantes"])
    escrito = niveles["segundo_nivel"]
    if list(escrito) != list(niveles["caso_base"]):
        raise ValueError(f"segundo_nivel: parametros {list(escrito)}, se esperaba {list(niveles['caso_base'])}")
    niveles["segundo_nivel"] = _varianza_conocida(variantes, list(niveles["caso_base"]), composicion)
    nd = NivelesDeclarados(
        version=datos["version"],
        fijado=datos["fijado"],
        nota=datos.get("nota", ""),
        fuentes=datos["fuentes"],
        salvedades=datos.get("salvedades", {}),
        niveles=niveles,
        escrito_segundo_nivel=escrito,
        tolerancia_control=float(datos["tolerancia_control_segundo_nivel"]),
        agregados_esperados={k: float(v) for k, v in datos["agregados_esperados"].items()},
        variantes=variantes,
        composicion=composicion,
        ruta=ruta,
    )
    _validar(nd)
    return nd


def _validar(nd):
    nombres = nd.parametros
    caso_base = nd.de("caso_base")
    for nombre, valor in list(caso_base.items()) + list(nd.escrito_segundo_nivel.items()):
        if not (math.isfinite(valor) and 0.0 <= valor < 1.0):
            raise ValueError(f"{nombre}: {valor} fuera de [0, 1)")
    for nivel in NOMBRES_NIVEL:
        if nivel not in nd.fuentes:
            raise ValueError(f"{nivel}: falta su fuente")
    # Agregados de lo escrito: el del caso base y el del control del segundo nivel.
    for nivel, valores in (("caso_base", caso_base), ("segundo_nivel", nd.escrito_segundo_nivel)):
        agregado = sum(valores.values()) / len(valores)
        esperado = nd.agregados_esperados[nivel]
        if abs(agregado - esperado) > TOLERANCIA_REDONDEO:
            raise ValueError(f"{nivel}: el agregado da {agregado:.6f}, se esperaba {esperado}")
    for var in nd.variantes:
        if not all(0.0 <= f <= 1.0 for f in var.frecuencias.values()):
            raise ValueError(f"{var.rs}: frecuencia fuera de [0, 1]")
    # El segundo nivel derivado contra su control escrito, y contra la h2.
    for nombre in nombres:
        v = nd.niveles["segundo_nivel"][nombre]
        if abs(v - nd.escrito_segundo_nivel[nombre]) > nd.tolerancia_control:
            raise ValueError(f"{nombre}: V por subpoblacion da {v:.6f} y el control escrito dice "
                             f"{nd.escrito_segundo_nivel[nombre]} (tolerancia {nd.tolerancia_control})")
        if v > caso_base[nombre]:
            raise ValueError(f"{nombre}: la varianza conocida ({v:.6f}) supera la h2 del caso base "
                             f"({caso_base[nombre]})")
