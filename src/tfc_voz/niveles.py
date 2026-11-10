"""
Cargador de los niveles declarados del modulo (config/niveles_declarados.json).

Es el UNICO lugar de donde salen las h2: ningun .py las escribe a mano
(tests/test_niveles.py lo controla). Hay dos niveles declarados:

  caso_base      h2-SNP por parametro (Gisladottir 2023, S6; jitter y hnr,
                 cota superior declarada). Con estos se generan siempre los
                 fenotipos.
  segundo_nivel  lo que explican las tres variantes publicadas (S8):
                 V = suma_s w_s * 2 * p_s * (1 - p_s) * beta^2, con p_s la
                 frecuencia de la subpoblacion (la misma que centra
                 g_conocida) y w_s la composicion de la cohorte.

Los dos niveles son ENTRADA: el cargador no recalcula nada (respuesta de
Diego del 9/11, tercera vuelta). El segundo nivel se calculo una vez con
scripts/calcular_segundo_nivel.py para la composicion de la cohorte 2.0, que
queda registrada en el JSON. Al cargar se VERIFICA que la cohorte tenga esa
composicion: si no, error, porque el nivel declarado no puede moverse en
silencio. Si cohorte_anima.csv no esta, se carga igual y la verificacion
queda como no hecha, para que el reporte lo diga.

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
# Las fracciones por subpoblacion se comparan exactas, salvo error de redondeo.
TOLERANCIA_COMPOSICION = 1e-12


@dataclass(frozen=True)
class Variante:
    rs: str
    parametro: str
    alelo_efecto: str
    beta: float
    frecuencias: dict  # frecuencia del alelo de efecto por subpoblacion

    def varianza(self, composicion):
        """Suma sobre subpoblaciones de w_s * 2 * p_s * (1 - p_s) * beta^2.

        Solo la usa scripts/calcular_segundo_nivel.py y su test: el cargador no recalcula.
        """
        if set(composicion) != set(self.frecuencias):
            raise ValueError(f"{self.rs}: subpoblaciones {sorted(self.frecuencias)}, "
                             f"la composicion tiene {sorted(composicion)}")
        return sum(w * 2.0 * self.frecuencias[s] * (1.0 - self.frecuencias[s]) * self.beta ** 2
                   for s, w in composicion.items())


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
    composicion_cohorte: dict  # version, sha256_csv, n y conteos de la cohorte de referencia
    verificacion_cohorte: str  # que paso con la verificacion de la composicion
    ruta: Path

    @property
    def parametros(self):
        return list(self.niveles["caso_base"])

    @property
    def composicion(self):
        """{subpoblacion: fraccion} de la cohorte con la que se fijaron los niveles."""
        c = self.composicion_cohorte
        return {s: k / c["n"] for s, k in c["conteos"].items()}

    def de(self, nivel):
        """{parametro: valor} de un nivel declarado."""
        if nivel not in self.niveles:
            raise KeyError(f"nivel {nivel!r} desconocido: {list(self.niveles)}")
        return dict(self.niveles[nivel])

    def agregado(self, nivel):
        valores = self.niveles[nivel].values()
        return sum(valores) / len(valores)

    def describir(self, nivel):
        """Renglones para el reporte: nivel, archivo, version, fecha y verificacion de la cohorte."""
        return (f"Nivel declarado: {nivel} (agregado {100 * self.agregado(nivel):.3f} %), "
                f"de {self.ruta.name}, version {self.version}, fijado el {self.fijado}. "
                f"Fuente: {self.fuentes[nivel]}. Composicion de la cohorte: {self.verificacion_cohorte}.")


def composicion_de(cohorte):
    """{subpoblacion: fraccion} de una cohorte."""
    conteo = cohorte["subpoblacion"].value_counts()
    return {s: float(k) / len(cohorte) for s, k in sorted(conteo.items())}


def verificar_composicion(registrada, cohorte):
    """Levanta ValueError, nombrando la subpoblacion, si la cohorte no tiene la composicion registrada."""
    _validar_conteos(registrada)
    esperada = {s: k / registrada["n"] for s, k in registrada["conteos"].items()}
    obtenida = composicion_de(cohorte)
    for s in sorted(set(esperada) | set(obtenida)):
        w_esperada, w_obtenida = esperada.get(s, 0.0), obtenida.get(s, 0.0)
        if abs(w_esperada - w_obtenida) > TOLERANCIA_COMPOSICION:
            raise ValueError(
                f"subpoblacion {s}: la cohorte tiene {100 * w_obtenida:.2f} % y los niveles declarados "
                f"se fijaron para la cohorte {registrada['version']}, con {100 * w_esperada:.2f} %. "
                "Cambiar la composicion exige recalcular el segundo nivel "
                "(scripts/calcular_segundo_nivel.py) y volver a declararlo.")


def cargar(ruta=RUTA, cohorte=None, ruta_cohorte=RUTA_COHORTE):
    """Lee y valida el archivo de niveles declarados. Levanta ValueError si no cierra.

    cohorte: DataFrame cuya composicion se verifica; por defecto, la de
    ruta_cohorte si existe. Si no hay cohorte, carga igual y deja la
    verificacion como no hecha.
    """
    ruta, ruta_cohorte = Path(ruta), Path(ruta_cohorte)
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    registrada = datos["composicion_cohorte"]
    if cohorte is None and ruta_cohorte.exists():
        cohorte = leer_cohorte(ruta_cohorte)
    if cohorte is None:
        verificacion = f"NO VERIFICADA: falta {ruta_cohorte.name}"
    else:
        verificar_composicion(registrada, cohorte)
        verificacion = f"verificada contra la cohorte {registrada['version']} ({registrada['n']} personas)"
    nd = NivelesDeclarados(
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
        composicion_cohorte=registrada,
        verificacion_cohorte=verificacion,
        ruta=ruta,
    )
    _validar(nd)
    return nd


def _validar_conteos(c):
    if sum(c["conteos"].values()) != c["n"]:
        raise ValueError(f"composicion_cohorte: los conteos suman {sum(c['conteos'].values())}, n = {c['n']}")


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
    c = nd.composicion_cohorte
    _validar_conteos(c)
    for var in nd.variantes:
        if var.parametro not in nombres:
            raise ValueError(f"{var.rs}: parametro {var.parametro!r} desconocido")
        if set(var.frecuencias) != set(c["conteos"]):
            raise ValueError(f"{var.rs}: sus subpoblaciones no son las de composicion_cohorte")
        if not all(0.0 <= f <= 1.0 for f in var.frecuencias.values()):
            raise ValueError(f"{var.rs}: frecuencia fuera de [0, 1]")
    caso_base, segundo = nd.de("caso_base"), nd.de("segundo_nivel")
    con_variante = {var.parametro for var in nd.variantes}
    for nombre in nombres:
        if segundo[nombre] > caso_base[nombre]:
            raise ValueError(f"{nombre}: el segundo nivel ({segundo[nombre]}) supera la h2 del caso base "
                             f"({caso_base[nombre]})")
        if (segundo[nombre] > 0) != (nombre in con_variante):
            raise ValueError(f"{nombre}: el segundo nivel es distinto de cero si y solo si hay una variante")
