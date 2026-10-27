"""
Efectos poblacionales de sexo, edad y subpoblacion sobre cada parametro.

Son los coeficientes del modelo generativo (brief del prototipo, "Decisiones
ya tomadas"):

    m = d*sexo + [b_mujer*(1-sexo) + b_hombre*sexo]*edad_c
               + [q_mujer*(1-sexo) + q_hombre*sexo]*tramo60 + a[subpob]
    s = r**sexo * exp(c*edad_c)
    edad_c = (edad - 49) / 10      tramo60 = max(0, edad - 60) / 10

Escala: desvios del logaritmo natural del valor acustico en mujeres. hnr ya
esta en dB (escala logaritmica), asi que va en desvios de dB en mujeres.
Las pendientes son por decada. Sexo: 0 = mujer (referencia), 1 = hombre.

Cada valor lleva su fuente, que empieza con uno de cuatro tipos:
  "dato"        -> sale de una celda o una frase de la fuente citada, a lo
                   sumo convertido a la escala del modulo;
  "derivado"    -> combina varios valores de la fuente (promedio de vocales,
                   diferencia entre grupos de edad, pendientes de F1 a F4);
  "0 declarado" -> no hay datos: queda en 0 y se declara;
  "PENDIENTE"   -> falta el dato; queda en 0 y el reporte lo lista.

media_ref y desvio_ref son la media y el desvio del logaritmo (o de los dB)
en mujeres. Sirven para volver a unidades fisicas: valor = exp(media_ref +
desvio_ref * y), o media_ref + desvio_ref * y en hnr. La conversion no se
implementa todavia. Las fuentes informan la media y el DE en unidades fisicas
(REFERENCIA_FISICA); se pasan a logaritmo por momentos lognormales:
desvio_ref = sqrt(ln(1 + (DE / media)^2)) y media_ref = ln(media) - desvio_ref^2 / 2.
hnr ya esta en dB y no se convierte (verificado contra las tablas el 26/10).
"""

from dataclasses import dataclass

from anima_spine import spine

TIPOS_FUENTE = ("dato", "derivado", "0 declarado", "PENDIENTE")

CAMPOS_CON_FUENTE = ("d", "r", "b_mujer", "b_hombre", "q_mujer", "q_hombre", "c", "a",
                     "media_ref", "desvio_ref")

SUBPOBLACIONES = tuple(spine.SUBPOBLACIONES)  # CEU es la referencia


@dataclass(frozen=True)
class EfectosPoblacionales:
    nombre: str
    d: float           # diferencia hombre - mujer en la media, a edad fija
    r: float           # cociente de desvios hombre / mujer, a edad fija
    b_mujer: float     # pendiente por decada, mujeres
    b_hombre: float    # pendiente por decada, hombres
    q_mujer: float     # cambio de pendiente desde los 60, mujeres
    q_hombre: float    # cambio de pendiente desde los 60, hombres
    c: float           # cambio del log-desvio por decada
    a: dict            # efecto de cada subpoblacion
    media_ref: float
    desvio_ref: float
    escala: str        # "log" | "dB"
    fuente: dict       # campo -> "tipo: texto", un texto por valor


def tipo_de_fuente(texto):
    """El tipo con el que empieza una fuente ("dato", "derivado", ...)."""
    for tipo in TIPOS_FUENTE:
        if texto.startswith(tipo + ":"):
            return tipo
    raise ValueError(f"fuente sin tipo reconocido: {texto!r}")


def _sin_subpoblacion():
    return {s: 0.0 for s in SUBPOBLACIONES}


# Textos repetidos entre parametros.
_C_SIN_DATO = "0 declarado: no hay datos del cambio de la dispersion con la edad"
_A_SIN_DATO = "0 declarado: no hay datos del efecto de la subpoblacion"
_SIN_QUIEBRE = "0 declarado: el quiebre a los 60 solo se modela en f0_medio"
_C_GOY = ("0 declarado: Goy et al. 2013 muestra que la dispersion crece con la edad "
          "(0,01 a 0,06 por decada en log del desvio), pero el modelo tiene un solo c "
          "para ambos sexos")
_EDAD_GOY = ("derivado: Goy et al. 2013, Tablas 2 y 3, diferencia entre jovenes (~19 anios) "
             "y mayores (~72 anios); no significativa con Bonferroni, se usa la estimacion puntual")


# Media y DE de las mujeres en unidades fisicas, tal como las informa la fuente.
# nombre: (fila de la fuente, media, DE, unidad)
REFERENCIA_FISICA = {
    "f0_medio": ("Gisladottir et al. 2023, tabla S2 (S2_Means), Vowels.MedianF0", 198.3467, 23.79237, "Hz"),
    "f0_variabilidad": ("Gisladottir et al. 2023, tabla S2 (S2_Means), Vowels.StdF0", 9.801441, 6.397369, "Hz"),
    "f1": ("Gisladottir et al. 2023, tabla S2 (S2_Means), Vowels.MedianF1", 542.6445, 48.37267, "Hz"),
    "f2": ("Gisladottir et al. 2023, tabla S2 (S2_Means), Vowels.MedianF2", 1559.675, 89.84026, "Hz"),
    "f3": ("Gisladottir et al. 2023, tabla S2 (S2_Means), Vowels.MedianF3", 2948.821, 141.7478, "Hz"),
    "vtl": ("Gisladottir et al. 2023, tabla S2 (S2_Means), VTL.F1to4", 14.87063, 0.614681, "cm"),
    "jitter": ("Goy et al. 2013, tabla 3, grupo joven", 0.37, 0.25, "%"),
    "hnr": ("Goy et al. 2013, tabla 3, grupo joven", 25.3, 3.1, "dB"),
}

_MOMENTOS = ("momentos lognormales: desvio_ref = sqrt(ln(1 + (DE/media)^2)), "
             "media_ref = ln(media) - desvio_ref^2 / 2")


def _fuente_referencia(nombre):
    """Fuente de media_ref y desvio_ref: fila, media y DE fisicos, y la conversion."""
    fila, media, de, unidad = REFERENCIA_FISICA[nombre]
    valores = f"{fila}, mujeres: media {media} {unidad}, DE {de} {unidad}"
    if unidad == "dB":
        return f"dato: {valores}; sin conversion (hnr ya esta en dB)"
    return f"derivado: {valores}; {_MOMENTOS}"


def _fuentes_gisladottir(nombre, fila_s2, edad_b_mujer, edad_b_hombre, quiebre=None):
    quiebre = quiebre or {"q_mujer": _SIN_QUIEBRE, "q_hombre": _SIN_QUIEBRE}
    return {
        "d": f"dato: Gisladottir et al. 2023, tabla S2, {fila_s2}",
        "r": f"dato: Gisladottir et al. 2023, tabla S2, {fila_s2}",
        "b_mujer": edad_b_mujer,
        "b_hombre": edad_b_hombre,
        **quiebre,
        "c": _C_SIN_DATO,
        "a": _A_SIN_DATO,
        "media_ref": _fuente_referencia(nombre),
        "desvio_ref": _fuente_referencia(nombre),
    }


def _fuentes_goy(nombre):
    return {
        "d": "dato: Goy et al. 2013, Tablas 2 y 3, grupo joven",
        "r": "dato: Goy et al. 2013, Tablas 2 y 3, grupo joven",
        "b_mujer": _EDAD_GOY,
        "b_hombre": _EDAD_GOY,
        "q_mujer": _SIN_QUIEBRE,
        "q_hombre": _SIN_QUIEBRE,
        "c": _C_GOY,
        "a": _A_SIN_DATO,
        "media_ref": _fuente_referencia(nombre),
        "desvio_ref": _fuente_referencia(nombre),
    }


_S4_VOCALES = "derivado: Gisladottir et al. 2023, tabla S4, promedio de las 5 vocales"

EFECTOS = {
    "f0_medio": EfectosPoblacionales(
        "f0_medio", d=-4.03, r=1.41, b_mujer=-0.32, b_hombre=0.0, q_mujer=0.32, q_hombre=0.40,
        c=0.0, a=_sin_subpoblacion(), media_ref=5.2829, desvio_ref=0.1195, escala="log",
        fuente=_fuentes_gisladottir(
            "f0_medio", "Vowels.MedianF0",
            edad_b_mujer="dato: texto de Gisladottir et al. 2023, mujeres -0,8 Hz por anio hasta los 60",
            edad_b_hombre="derivado: lectura de Gisladottir et al. 2023: el cambio de F0 en "
                          "hombres empieza a los 60, asi que antes de los 60 la pendiente es 0",
            quiebre={
                "q_mujer": "derivado: lectura de Gisladottir et al. 2023: la caida de F0 en "
                           "mujeres termina a los 60, asi que desde los 60 se anula su pendiente",
                "q_hombre": "dato: texto de Gisladottir et al. 2023, hombres +0,6 Hz por anio "
                            "desde los 60",
            })),
    "f0_variabilidad": EfectosPoblacionales(
        "f0_variabilidad", d=-0.75, r=1.02, b_mujer=0.0, b_hombre=0.0, q_mujer=0.0, q_hombre=0.0,
        c=0.0, a=_sin_subpoblacion(), media_ref=2.1051, desvio_ref=0.5957, escala="log",
        fuente=_fuentes_gisladottir(
            "f0_variabilidad", "Vowels.StdF0",
            edad_b_mujer="0 declarado: sin dato del efecto de la edad",
            edad_b_hombre="0 declarado: sin dato del efecto de la edad")),
    "jitter": EfectosPoblacionales(
        "jitter", d=0.26, r=0.54, b_mujer=0.07, b_hombre=0.06, q_mujer=0.0, q_hombre=0.0,
        c=0.0, a=_sin_subpoblacion(), media_ref=-1.1825, desvio_ref=0.6135, escala="log",
        fuente=_fuentes_goy("jitter")),
    "hnr": EfectosPoblacionales(
        "hnr", d=-0.77, r=0.87, b_mujer=0.0, b_hombre=-0.06, q_mujer=0.0, q_hombre=0.0,
        c=0.0, a=_sin_subpoblacion(), media_ref=25.3, desvio_ref=3.1, escala="dB",
        fuente=_fuentes_goy("hnr")),
    "f1": EfectosPoblacionales(
        "f1", d=-1.91, r=0.94, b_mujer=-0.10, b_hombre=0.02, q_mujer=0.0, q_hombre=0.0,
        c=0.0, a=_sin_subpoblacion(), media_ref=6.2925, desvio_ref=0.0890, escala="log",
        fuente=_fuentes_gisladottir("f1", "Vowels.MedianF1", _S4_VOCALES, _S4_VOCALES)),
    "f2": EfectosPoblacionales(
        "f2", d=-2.53, r=1.02, b_mujer=-0.14, b_hombre=-0.03, q_mujer=0.0, q_hombre=0.0,
        c=0.0, a=_sin_subpoblacion(), media_ref=7.3506, desvio_ref=0.0576, escala="log",
        fuente=_fuentes_gisladottir("f2", "Vowels.MedianF2", _S4_VOCALES, _S4_VOCALES)),
    "f3": EfectosPoblacionales(
        "f3", d=-2.45, r=0.99, b_mujer=0.02, b_hombre=-0.03, q_mujer=0.0, q_hombre=0.0,
        c=0.0, a=_sin_subpoblacion(), media_ref=7.9880, desvio_ref=0.0480, escala="log",
        fuente=_fuentes_gisladottir("f3", "Vowels.MedianF3", _S4_VOCALES, _S4_VOCALES)),
    "vtl": EfectosPoblacionales(
        "vtl", d=3.38, r=1.06, b_mujer=0.04, b_hombre=-0.02, q_mujer=0.0, q_hombre=0.0,
        c=0.0, a=_sin_subpoblacion(), media_ref=2.6985, desvio_ref=0.0413, escala="log",
        fuente=_fuentes_gisladottir(
            "vtl", "VTL.F1to4",
            "derivado: Gisladottir et al. 2023, tabla S4, pendientes de F1 a F4",
            "derivado: Gisladottir et al. 2023, tabla S4, pendientes de F1 a F4")),
}


def pendientes(efectos=None):
    """Valores que siguen PENDIENTE, como (parametro, campo, fuente). El reporte los lista."""
    efectos = EFECTOS if efectos is None else efectos
    return [(nombre, campo, ef.fuente[campo])
            for nombre, ef in efectos.items()
            for campo in CAMPOS_CON_FUENTE
            if tipo_de_fuente(ef.fuente[campo]) == "PENDIENTE"]


def configuracion_neutra(nombres=None):
    """Efectos nulos (todo en 0, r = 1). SOLO PARA TESTS: con ella, y = g + e."""
    nombres = list(EFECTOS) if nombres is None else nombres
    texto = "0 declarado: configuracion neutra, solo para tests"
    return {n: EfectosPoblacionales(
        n, d=0.0, r=1.0, b_mujer=0.0, b_hombre=0.0, q_mujer=0.0, q_hombre=0.0, c=0.0,
        a=_sin_subpoblacion(), media_ref=0.0, desvio_ref=1.0, escala="log",
        fuente={campo: texto for campo in CAMPOS_CON_FUENTE}) for n in nombres}
