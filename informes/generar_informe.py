"""
Genera el informe de estado del modulo de Voz en PDF.

Uso (parado en la raiz del proyecto):
    .venv\\Scripts\\python.exe informes\\generar_informe.py
    .venv\\Scripts\\python.exe informes\\generar_informe.py --fecha 2026-10-13

Sale en informes/informe-estado-AAAA-MM-DD.pdf. Requiere instalar ademas
requirements-informes.txt (reportlab + matplotlib).

Que se actualiza solo y que hay que editar en cada informe nuevo:
  - El avance por fase (grafico de cronograma, tabla de fases y porcentaje de
    la fase en curso) se lee de seguimiento-modulo-voz.md. Alcanza con tener
    los [x] al dia; las subtareas indentadas no cuentan.
  - Todo lo que esta en la seccion CONTENIDO (KPIs, resumen, resultados,
    hallazgos, proximos pasos) es el texto de ESTE informe: editarlo antes de
    generar el siguiente. Los informes anteriores quedan en git y en los PDF
    de esta carpeta.
"""

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from tfc_voz.extraccion import RANGO_F0  # noqa: E402  (rangos reales, no copiados)

SEGUIMIENTO = RAIZ / "seguimiento-modulo-voz.md"
SALIDA_DIR = RAIZ / "informes"

# Paleta de referencia (validada: CVD y contraste). El aqua queda bajo 3:1
# sobre blanco, por eso toda barra lleva su valor escrito.
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA2, TINTA3 = "#0b0b0b", "#52514e", "#8a8984"
GRIS_BAND, GRIS_GRID, LINEA_TABLA = "#e6e5e1", "#ecebe7", "#dddcd7"

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"]


# =====================================================================
# Lectura del seguimiento
# =====================================================================

# El proyecto va de sep 2026 a feb 2027: los meses de julio en adelante son
# de 2026 y los anteriores de 2027. Cambiar si el cronograma se corre.
ANIO_INICIO = 2026

RE_FASE = re.compile(r"^## Fase (\d+) — (.+?) \((.+?)\)\s*$")
RE_TAREA = re.compile(r"^- \[([ xX])\]")


@dataclass
class Fase:
    numero: int
    nombre: str
    inicio: date
    fin: date
    hechas: int = 0
    total: int = 0


def _fecha(txt, mes_por_defecto=None):
    partes = txt.strip().split()
    dia = int(partes[0])
    mes = MESES.index(partes[1][:3].lower()) + 1 if len(partes) > 1 else mes_por_defecto
    return date(ANIO_INICIO if mes >= 7 else ANIO_INICIO + 1, mes, dia)


def leer_fases(ruta=SEGUIMIENTO):
    fases, actual = [], None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = RE_FASE.match(linea)
        if m:
            ini_txt, fin_txt = re.split(r"\s*[–-]\s*", m.group(3))
            fin = _fecha(fin_txt)
            actual = Fase(int(m.group(1)), m.group(2).strip(), _fecha(ini_txt, fin.month), fin)
            fases.append(actual)
        elif linea.startswith("## "):
            actual = None  # otra seccion (p. ej. pendientes puntuales)
        elif actual and RE_TAREA.match(linea):
            actual.total += 1
            actual.hechas += RE_TAREA.match(linea).group(1) != " "
    if not fases:
        raise SystemExit(f"no se encontraron fases en {ruta}")
    return fases


def estado(f, hoy):
    if f.total and f.hechas == f.total:
        return "hecha"
    if hoy < f.inicio:
        return "adelantada" if f.hechas else "pendiente"
    return "curso" if hoy <= f.fin else "atrasada"


def ventana_consumida(f, hoy):
    return max(0.0, min(1.0, (hoy - f.inicio).days / (f.fin - f.inicio).days))


def fecha_corta(d):
    return f"{d.day} {MESES[d.month - 1]}"


def fecha_larga(d):
    return f"{d.day} de {MESES_LARGOS[d.month - 1]} de {d.year}"


def n(v, d=1):
    """Numero con coma decimal y sin separador de miles."""
    return f"{v:.{d}f}".replace(".", ",")


# =====================================================================
# CONTENIDO DEL INFORME -- editar en cada informe nuevo
# =====================================================================

AUTOR = "Diego Escorche"

# Fecha real de cierre de fases terminadas fuera de su ventana. Se usa para
# dibujar el atraso en el cronograma y en la tabla de fases.
CIERRES_REALES = {1: date(2026, 10, 12)}

# Prueba de humo del 12 oct 2026 (VCTK 0.92, frase _001, mic1).
# id, sexo, edad, acento, f0, f0_var, jitter, hnr, f1, f2, f3, vtl
PRUEBA_HUMO = [
    ("p225", "F", 23, "Southern England", 197.848, 29.283, 0.018, 12.750, 415.388, 1617.044, 2632.530, 17.972),
    ("p228", "F", 22, "Southern England", 222.846, 27.226, 0.019, 14.007, 470.119, 1762.768, 2809.133, 16.359),
    ("p229", "F", 23, "Southern England", 194.609, 19.767, 0.010, 14.516, 476.954, 1695.579, 3125.580, 15.941),
    ("p230", "F", 22, "Stockton-on-Tees", 209.420, 20.022, 0.027, 15.187, 590.389, 1576.018, 2899.443, 15.522),
    ("p231", "F", 23, "Southern England", 200.424, 35.644, 0.027, 11.065, 435.932, 1391.015, 3027.163, 17.799),
    ("p226", "M", 22, "Surrey", 124.234, 22.259, 0.032, 9.643, 377.394, 1387.642, 2722.942, 19.390),
    ("p227", "M", 38, "Cumbria", 121.634, 19.210, 0.015, 10.415, 526.693, 1221.464, 2748.930, 18.006),
    ("p232", "M", 23, "Southern England", 114.645, 20.983, 0.023, 10.083, 488.890, 1265.461, 2796.926, 18.094),
    ("p237", "M", 22, "Scottish (Fife)", 80.632, 9.756, 0.024, 9.449, 393.159, 1154.489, 2476.063, 20.887),
    ("p241", "M", 21, "Scottish (Perth)", 123.782, 11.793, 0.022, 11.600, 500.775, 1248.972, 2562.186, 18.522),
]
CASO_A_REVISAR = "p237"

# VTL estimado desde F1, F2, F3 y promedio (lo que reporta extraccion.py).
VTL_DESGLOSE = {"Mujeres": (18.583, 16.427, 15.146, 16.719),
                "Hombres": (19.485, 20.981, 16.474, 18.980)}
# Banda orientativa de VTL en adultos (aproximada, sin cita todavia).
VTL_REFERENCIA = {"Mujeres": (14, 15), "Hombres": (16.5, 17.5)}


def contenido(ctx):
    """Arma la lista de flowables del informe. ctx trae fases, hoy y helpers."""
    P, bullets, tabla, kpis, figura = ctx["P"], ctx["bullets"], ctx["tabla"], ctx["kpis"], ctx["figura"]
    fases, hoy, figs = ctx["fases"], ctx["hoy"], ctx["figs"]
    en_curso = next((f for f in fases if estado(f, hoy) == "curso"), None)
    pct = round(100 * ventana_consumida(en_curso, hoy)) if en_curso else None

    story = [
        P("Módulo de Voz — Informe de estado", "titulo"), Spacer(1, 4),
        P(f"Proyecto Anima · Trabajo Final de Carrera, Universidad de Belgrano · {AUTOR} · "
          f"{fecha_larga(hoy)}", "sub"),
        Spacer(1, 14),
        kpis([
            ("Completada", "Fase 1, cerrada el 12 oct<br/>(vencía el 1 oct: 11 días de atraso)"),
            ("10 / 10", "archivos de VCTK extraídos sin errores ni advertencias"),
            (f"{pct} %" if pct is not None else "—",
             f"de la ventana de la Fase {en_curso.numero} ya consumida, con {en_curso.hechas} de "
             f"{en_curso.total} tareas cerradas" if en_curso else "sin fase en curso"),
            ("1 hallazgo", "a resolver antes de la Fase 2: VTL ~2 cm sobreestimado"),
        ]),
        Spacer(1, 10),
        P("Resumen", "h1"),
    ]
    story += bullets([
        "<b>La Fase 1 está cerrada.</b> El entorno está instalado y verificado, el corpus VCTK descargado "
        "y la extracción de los 8 parámetros funciona sobre audio real <b>sin modificar el código</b>.",
        "<b>La prueba de humo salió limpia:</b> 10 hablantes (5 mujeres y 5 hombres), 0 errores, 0 advertencias "
        "de plausibilidad. El problema que preocupaba de la señal sintética (un formante espurio que corre la "
        "numeración) no apareció.",
        "<b>Hay un hallazgo a resolver en la Fase 2:</b> el largo del tracto vocal (VTL) da unos 2 cm más que "
        "los valores habituales en adultos. Viene del modelo de tubo uniforme, no de un error de medición, y "
        "hay que decidir cómo tratarlo antes de reescalar la cohorte sintética.",
        f"<b>El cronograma sigue siendo el riesgo principal.</b> La Fase 2 arranca con el {pct} % de su ventana "
        "consumida. Para cerrarla el 1 de noviembre hacen falta unas 25 hs/semana en vez de las 16 planificadas.",
    ])

    story += [P("1. Cómo va el proyecto", "h1"),
              figura(figs["cronograma"], 17, 3.3 / 7.2),
              P(f"Figura 1. Avance por fase al {fecha_corta(hoy)}, leído de seguimiento-modulo-voz.md. El número "
                "a la derecha indica tareas cerradas sobre el total. Una fase “adelantada” tiene tareas cerradas "
                "antes de que empiece su ventana.", "cap"),
              tabla_fases(fases, hoy, tabla),
              P("Cronograma y riesgo", "h2")]
    story += bullets([
        "En volumen total el proyecto sigue siendo viable (~190 hs en 18 semanas, unas 11 hs/semana de promedio), "
        "gracias a que la redacción del documento individual va adelantada.",
        "El riesgo es el <b>efecto dominó hacia diciembre</b>, el mes con menos margen: cada semana de atraso de la "
        "Fase 2 empuja Calibración, Reconstrucción e Integración con el equipo.",
        "<b>Decisión pendiente si no se recupera el atraso:</b> recortar alcance en la Fase 2 (menos parámetros o una "
        "cohorte sintética más chica) antes que correr las fechas.",
    ])

    story += [P("2. Qué se hizo en este cierre de Fase 1", "h1"), tabla([
        ["Tarea", "Resultado"],
        ["Entorno virtual", "Python 3.12.4 en .venv/. Los 4 chequeos de tests/test_setup.py pasan, incluido el "
         "análisis y la síntesis reales con pyworld."],
        ["Dependencias", "parselmouth 0.4.7 · pyworld 0.3.5 · flask 3.1.3 · numpy 2.5.4 · scipy 1.18.1. pyworld ya "
         "trae paquete precompilado para 3.12: no hizo falta compilador de C++."],
        ["Módulos existentes", "parametros.py y genotipo.py corren sin cambios; la cohorte es reproducible con la "
         "semilla 42."],
        ["Corpus VCTK 0.92", "10,94 GB descargados y descomprimidos en data/VCTK-Corpus-0.92/: 110 hablantes "
         "(63 mujeres y 47 hombres). El audio viene en FLAC y parselmouth lo lee directo."],
        ["Prueba de humo", "10 archivos, 0 errores, 0 advertencias (sección 3)."],
        ["Repositorio y documentación", "Git inicializado (.venv/ y data/ excluidos). SETUP.md reescrito según la "
         "instalación real; informe-fase1.md y seguimiento-modulo-voz.md actualizados."],
    ], [4 * cm, 13 * cm])]

    story += [P("3. Resultados de la prueba de humo", "h1"),
              P("Se tomaron los primeros 5 hablantes de cada sexo de <i>speaker-info.txt</i>, con la frase "
                "<i>_001</i> y el micrófono 1. La frase es la misma para todos (<i>“Please call Stella.”</i>, "
                "de 2 a 3,4 s), así que las diferencias entre hablantes no vienen del texto. La extracción usó "
                "<i>extraer_parametros()</i> con sus valores por defecto: el rango de F0 depende del sexo y el "
                "techo de formantes es 5000 Hz (hombres) o 5500 Hz (mujeres).")]
    cab = ["Hablante", "Sexo", "Edad", "F0 (Hz)", "F0 var.", "Jitter %", "HNR (dB)", "F1", "F2", "F3", "VTL (cm)"]
    filas = [cab] + [[f[0], f[1], f[2], n(f[4]), n(f[5]), n(f[6] * 100), n(f[7]), n(f[8], 0), n(f[9], 0),
                      n(f[10], 0), n(f[11], 2)] for f in PRUEBA_HUMO]
    t = tabla(filas, [1.6 * cm, 1.0 * cm, 1.0 * cm, 1.6 * cm, 1.5 * cm, 1.5 * cm, 1.6 * cm, 1.4 * cm,
                      1.5 * cm, 1.5 * cm, 1.7 * cm])
    fila_caso = 1 + [f[0] for f in PRUEBA_HUMO].index(CASO_A_REVISAR)
    t.setStyle(TableStyle([("ALIGN", (3, 0), (-1, -1), "RIGHT"),
                           ("BACKGROUND", (0, fila_caso), (-1, fila_caso), colors.HexColor("#fdf3ec"))]))
    story += [t, P(f"Tabla 1. Parámetros por archivo. Formantes F1–F3 en Hz. La fila resaltada ({CASO_A_REVISAR}) "
                   "es el caso a revisar de la sección 4.3.", "cap")]

    medias = [["Parámetro", "Mujeres", "Hombres", "Lectura"],
              ["F0 medio", "205,0 Hz", "113,0 Hz", "Separa bien por sexo"],
              ["Variabilidad de F0", "26,4 Hz", "16,8 Hz", "Esperable"],
              ["Jitter", "2,0 %", "2,3 %", "Alto para vocal sostenida, normal en habla leída (4.2)"],
              ["HNR", "13,5 dB", "10,2 dB", "Más alto en mujeres, patrón habitual"],
              ["F1 / F2 / F3", "478 / 1608 / 2899 Hz", "457 / 1256 / 2661 Hz",
               "En orden y en rango; F2 y F3 más altos en mujeres"],
              ["VTL", "16,7 cm", "19,0 cm", "~2 cm por encima de lo esperable (4.1)"]]
    story += [KeepTogether([P("Medias por sexo", "h2"),
                            tabla(medias, [3.2 * cm, 3.6 * cm, 3.6 * cm, 6.6 * cm])])]
    story += [KeepTogether([
        Spacer(1, 8),
        figura(figs["f0"], 17, 1.9 / 7.2),
        P("Figura 2. F0 medio por hablante sobre el rango de búsqueda de F0 de cada sexo. Todos los valores quedan "
          "dentro del rango y sin señales de que el algoritmo haya leído la mitad o el doble del pitch real, salvo "
          f"el caso a revisar de {CASO_A_REVISAR}.", "cap")])]

    story += [P("4. Hallazgos a resolver en la Fase 2", "h1"),
              P("4.1 VTL sobreestimado", "h2"),
              P("El largo del tracto vocal da 16,7 cm de media en mujeres y 19,0 cm en hombres, unos 2 cm por encima "
                "de los valores habituales en adultos (del orden de 14–15 cm y 17 cm). La diferencia entre sexos se "
                "mantiene, y ningún archivo sale del rango plausible de 10 a 21 cm, así que <b>el control de "
                "calidad automático no lo detecta</b>."),
              figura(figs["vtl"], 17, 2.9 / 7.2),
              P("Figura 3. VTL que da cada formante por separado (L = (2n−1)·c / 4F<sub>n</sub>) y el promedio de "
                "los tres, que es lo que reporta extraccion.py. La banda gris es una referencia aproximada en "
                "adultos, solo orientativa; conviene fijar la exacta con Lammert &amp; Narayanan (2015).", "cap"),
              P("Desglosando por formante, la estimación desde <b>F3 es la más estable</b> y la más cercana a lo "
                "esperable. <b>F1 en mujeres y F2 en hombres inflan el promedio.</b> El modelo de tubo uniforme "
                "supone una vocal neutra, pero acá se aplica sobre la mediana de los formantes de una frase entera. "
                "Esas medianas quedan bajas y se traducen en un tracto más largo. La docstring de "
                "<i>_vtl_desde_formantes</i> ya advierte que es una aproximación."),
              P("<b>Decisión a tomar</b> antes de reescalar la cohorte sintética: (a) cambiar la estimación, por "
                "ejemplo con Lammert &amp; Narayanan (2015), que ya está en la bibliografía, o (b) mantenerla y "
                "declarar el sesgo en la memoria. Como VTL es el único parámetro con h² derivada (0,13, convertida "
                "desde gemelos), conviene que su medición sea la más defendible del espacio."),
              P("4.2 Jitter alto", "h2"),
              P("El jitter medio (2,0–2,3 %) supera el umbral de referencia de Praat para vocales sostenidas "
                "(1,04 %). Es esperable en habla leída continua de 2 a 3 segundos, donde las transiciones entre "
                "sonidos agregan perturbación. No indica una falla, pero hay que tenerlo en cuenta al comparar con "
                "la literatura, que suele medir sobre vocales sostenidas."),
              P(f"4.3 Caso a revisar: {CASO_A_REVISAR}", "h2"),
              P("Es un hombre escocés de 22 años con F0 = 80,6 Hz (unos 33 Hz debajo de la media masculina) y la "
                "menor variabilidad de F0 de la muestra. Puede ser una voz genuinamente grave, pero también es el "
                "patrón típico de un error en que el algoritmo lee la mitad del pitch real. Se verifica con varias "
                "frases del mismo hablante al procesar el corpus completo.")]

    story += [P("5. Limitaciones de esta prueba", "h1")]
    story += bullets([
        "Es una prueba de humo, no una validación estadística: 10 de 110 hablantes, una frase de unos 2 s cada uno.",
        "No hay valores de referencia por hablante. “Plausible” significa dentro de los rangos de "
        "RANGOS_PLAUSIBLES, no correcto.",
        "La muestra es casi toda de acento del sur de Inglaterra, por el orden de speaker-info.txt. Alcanza para "
        "validar el pipeline: ampliar idiomas o acentos está fuera de alcance.",
    ])

    story += [P("6. Próximos pasos", "h1"), tabla([
        ["#", "Paso", "Por qué"],
        ["1", "Extraer los 8 parámetros de todo VCTK y contar las advertencias",
         "Da los rangos y correlaciones reales. El README pide el conteo antes de ajustar maximum_formant."],
        ["2", "Decidir el tratamiento de VTL (4.1)", "Bloquea el reescalado de la cohorte a unidades reales."],
        ["3", f"Revisar {CASO_A_REVISAR} con varias frases (4.3)",
         "Descarta que el algoritmo esté leyendo la mitad del pitch."],
        ["4", "Reescalar la cohorte sintética y ajustar el modelo heterocedástico",
         "Cierra la Fase 2 y habilita la calibración conformal (Fase 3)."],
        ["5", "Si no se recupera el ritmo: recortar alcance de la Fase 2", "Evita el efecto dominó hacia diciembre."],
    ], [0.7 * cm, 7.3 * cm, 9 * cm])]

    story += [P("Pendientes menores", "h2")]
    story += bullets([
        "Actualizar la tabla de estado del README.md (§3 y §8): todavía figuran VCTK y la validación con audio real "
        "como pendientes, y solo Python 3.11 como verificado.",
        "decisiones-fase1.md cita factores-no-geneticos-voz.md, que no está en el repo.",
        "Buscar si apareció algún estudio posterior a 2024 con h²-SNP directo para jitter y HNR.",
    ])
    story += [Spacer(1, 10),
              P("Recordatorio de encuadre: lo que se defiende es la cuantificación de la incertidumbre, no la "
                "precisión de la reconstrucción. Un ΔR² chico (y prácticamente nulo en jitter y HNR) es el "
                "resultado esperado dado que la h² de la voz es del 5 al 17 %.", "cap")]
    return story


# =====================================================================
# Figuras
# =====================================================================

def configurar_fuentes():
    """Arial en Windows; si no esta, DejaVu Sans (viene con matplotlib).
    Hace falta una TTF con griegos: la Helvetica de reportlab no tiene Δ ni −."""
    win = Path("C:/Windows/Fonts")
    if (win / "arial.ttf").exists():
        archivos = {"normal": win / "arial.ttf", "bold": win / "arialbd.ttf", "italic": win / "ariali.ttf"}
        familia_mpl = "Arial"
    else:
        ttf = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        archivos = {"normal": ttf / "DejaVuSans.ttf", "bold": ttf / "DejaVuSans-Bold.ttf",
                    "italic": ttf / "DejaVuSans-Oblique.ttf"}
        familia_mpl = "DejaVu Sans"
    for clave, nombre in [("normal", "Base"), ("bold", "Base-Bold"), ("italic", "Base-Italic")]:
        pdfmetrics.registerFont(TTFont(nombre, str(archivos[clave])))
    pdfmetrics.registerFontFamily("Base", normal="Base", bold="Base-Bold", italic="Base-Italic",
                                  boldItalic="Base-Bold")
    if familia_mpl == "Arial":
        for f in archivos.values():
            font_manager.fontManager.addfont(str(f))
    plt.rcParams.update({
        "font.family": familia_mpl, "font.size": 9, "axes.edgecolor": TINTA3,
        "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })


def fig_cronograma(ruta, fases, hoy):
    fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=220)
    ys = list(range(len(fases)))[::-1]
    for y, f in zip(ys, fases):
        ini, fin = mdates.date2num(f.inicio), mdates.date2num(f.fin)
        est = estado(f, hoy)
        ax.barh(y, fin - ini, left=ini, height=0.55, color=GRIS_BAND, edgecolor="none")
        x_etiqueta = fin
        if est == "hecha":
            cierre = mdates.date2num(CIERRES_REALES.get(f.numero, f.fin))
            ax.barh(y, cierre - ini, left=ini, height=0.55, color=AZUL, edgecolor="none")
            x_etiqueta = max(fin, cierre)
        elif est in ("curso", "atrasada"):
            hasta = min(mdates.date2num(hoy), fin)
            ax.barh(y, hasta - ini, left=ini, height=0.55, color=NARANJA, edgecolor="none")
        elif est == "adelantada":
            ax.barh(y, (fin - ini) * f.hechas / f.total, left=ini, height=0.55, color=AZUL,
                    edgecolor="none", alpha=0.45)
        sufijo = {"adelantada": "  (adelantada)", "atrasada": "  (atrasada)"}.get(est, "")
        ax.text(x_etiqueta + 2, y, f"{f.hechas}/{f.total}{sufijo}", va="center", fontsize=7.5, color=TINTA2)
    x_hoy = mdates.date2num(hoy)
    ax.axvline(x_hoy, color=TINTA, lw=1, ls=(0, (3, 2)))
    ax.text(x_hoy, len(fases) - 0.35, f" hoy, {fecha_corta(hoy)}", fontsize=7.5, color=TINTA, va="bottom")
    ax.set_yticks(ys, [f"Fase {f.numero} · {f.nombre}" for f in fases], fontsize=7.5)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: MESES[mdates.num2date(x).month - 1]))
    ax.grid(axis="x", color=GRIS_GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlim(mdates.date2num(min(f.inicio for f in fases)) - 5,
                mdates.date2num(max(f.fin for f in fases)) + 22)
    ax.set_ylim(-0.6, len(fases) - 0.1)
    ax.legend(handles=[Patch(color=AZUL, label="Ejecutado"),
                       Patch(color=NARANJA, label="En curso (ventana consumida)"),
                       Patch(color=GRIS_BAND, label="Ventana planificada")],
              loc="upper center", bbox_to_anchor=(0.45, -0.1), ncol=3, frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def fig_f0(ruta):
    fig, ax = plt.subplots(figsize=(7.2, 1.9), dpi=220)
    for sexo, y in (("F", 1), ("M", 0)):
        lo, hi = RANGO_F0[sexo]
        ax.barh(y, hi - lo, left=lo, height=0.5, color=GRIS_BAND, edgecolor="none")
        xs = [f[4] for f in PRUEBA_HUMO if f[1] == sexo]
        ax.scatter(xs, [y] * len(xs), s=34, color=AZUL, edgecolor="white", linewidth=1.2, zorder=3)
        ax.text(lo + 2, y + 0.3, f"rango de búsqueda {lo:.0f}–{hi:.0f} Hz", fontsize=7, color=TINTA2,
                va="bottom")
    caso = next(f for f in PRUEBA_HUMO if f[0] == CASO_A_REVISAR)
    y_caso = 1 if caso[1] == "F" else 0
    ax.annotate(f"{caso[0]} · {n(caso[4])} Hz", (caso[4], y_caso), xytext=(caso[4], y_caso - 0.62),
                fontsize=7.5, color=TINTA, ha="center",
                arrowprops=dict(arrowstyle="-", color=TINTA3, lw=0.8))
    ax.set_yticks([1, 0], ["Mujeres", "Hombres"], fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("F0 medio (Hz)", fontsize=8)
    ax.set_xlim(50, 310)
    ax.set_ylim(-0.95, 1.6)
    ax.grid(axis="x", color=GRIS_GRID, lw=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def fig_vtl(ruta):
    fig, ax = plt.subplots(figsize=(7.2, 2.9), dpi=220)
    ancho, gap = 0.18, 0.02
    series = [("Estimado desde F1", AZUL), ("Desde F2", NARANJA), ("Desde F3", AQUA),
              ("Promedio: VTL que reporta extraccion.py", TINTA2)]
    for gi, (grupo, vals) in enumerate(VTL_DESGLOSE.items()):
        lo, hi = VTL_REFERENCIA[grupo]
        ax.fill_between([gi - 0.48, gi + 0.48], lo, hi, color=GRIS_BAND, lw=0, zorder=0)
        for si, (etiqueta, color) in enumerate(series):
            x = gi + (si - 1.5) * (ancho + gap)
            ax.bar(x, vals[si], width=ancho, color=color, edgecolor="none", zorder=2,
                   label=etiqueta if gi == 0 else None)
            ax.text(x, vals[si] + 0.3, n(vals[si]), ha="center", fontsize=7.5, color=TINTA,
                    fontweight="bold" if si == 3 else "normal")
    ax.set_xticks(range(len(VTL_DESGLOSE)), list(VTL_DESGLOSE), fontsize=8.5)
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Largo del tracto vocal (cm)", fontsize=8)
    ax.set_ylim(0, 24)
    ax.set_xlim(-0.6, 1.6)
    ax.grid(axis="y", color=GRIS_GRID, lw=0.8)
    ax.set_axisbelow(True)
    h, l = ax.get_legend_handles_labels()
    h.append(Patch(color=GRIS_BAND))
    l.append("Referencia aproximada en adultos")
    ax.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


# =====================================================================
# Maquetado
# =====================================================================

def estilos():
    base = ParagraphStyle("base", fontName="Base", fontSize=9.5, leading=13.5, textColor=colors.HexColor(TINTA))

    def e(nombre, **kw):
        return ParagraphStyle(nombre, parent=base, **kw)

    return {
        "titulo": e("titulo", fontName="Base-Bold", fontSize=20, leading=24),
        "sub": e("sub", fontSize=10, textColor=colors.HexColor(TINTA2)),
        "h1": e("h1", fontName="Base-Bold", fontSize=13, leading=17, spaceBefore=12, spaceAfter=5),
        "h2": e("h2", fontName="Base-Bold", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3),
        "p": e("p", spaceAfter=5),
        "bul": e("bul", leftIndent=12, bulletIndent=2, spaceAfter=3),
        "cap": e("cap", fontSize=8, leading=11, textColor=colors.HexColor(TINTA2), spaceAfter=8),
        "cel": e("cel", fontSize=8, leading=10),
        "celb": e("celb", fontName="Base-Bold", fontSize=8, leading=10),
        "kpi_v": e("kpi_v", fontName="Base-Bold", fontSize=16, leading=19),
        "kpi_l": e("kpi_l", fontSize=8, leading=10.5, textColor=colors.HexColor(TINTA2)),
    }


def helpers(S):
    def P(texto, estilo="p"):
        return Paragraph(texto, S[estilo])

    def bullets(items):
        return [Paragraph(t, S["bul"], bulletText="•") for t in items]

    def tabla(datos, anchos):
        filas = [[c if hasattr(c, "wrap") else Paragraph(str(c), S["celb" if i == 0 else "cel"]) for c in fila]
                 for i, fila in enumerate(datos)]
        t = Table(filas, colWidths=anchos, repeatRows=1)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor(LINEA_TABLA)),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f1ee")),
            ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor(TINTA3)),
        ]))
        return t

    def kpis(items):
        interno = [("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                   ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
        celdas = [Table([[Paragraph(v, S["kpi_v"])], [Paragraph(l, S["kpi_l"])]], colWidths=[3.95 * cm],
                        style=interno) for v, l in items]
        t = Table([celdas], colWidths=[4.25 * cm] * len(celdas))
        t.setStyle(TableStyle(
            [("BOX", (i, 0), (i, 0), 0.6, colors.HexColor(LINEA_TABLA)) for i in range(len(celdas))] + [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
        return t

    def figura(ruta, ancho_cm, proporcion):
        return Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * proporcion)

    return {"P": P, "bullets": bullets, "tabla": tabla, "kpis": kpis, "figura": figura}


def tabla_fases(fases, hoy, tabla):
    filas = [["Fase", "Ventana", "Tareas", "Estado"]]
    for f in fases:
        est = estado(f, hoy)
        if est == "hecha":
            cierre = CIERRES_REALES.get(f.numero)
            if cierre and cierre > f.fin:
                texto = f"Completada el {fecha_corta(cierre)} ({(cierre - f.fin).days} días tarde)"
            else:
                texto = "Completada"
        elif est == "curso":
            texto = f"En curso; {round(100 * ventana_consumida(f, hoy))} % de la ventana consumida"
        elif est == "atrasada":
            texto = f"Atrasada: la ventana cerró el {fecha_corta(f.fin)}"
        elif est == "adelantada":
            texto = "Adelantada"
        else:
            texto = "Pendiente"
        filas.append([f"{f.numero} · {f.nombre}", f"{fecha_corta(f.inicio)} – {fecha_corta(f.fin)}",
                      f"{f.hechas} / {f.total}", texto])
    return tabla(filas, [6.4 * cm, 2.9 * cm, 1.5 * cm, 6.2 * cm])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--fecha", type=date.fromisoformat, default=date.today(),
                    help="fecha del informe, AAAA-MM-DD (por defecto, hoy)")
    ap.add_argument("--salida", type=Path, help="ruta del PDF (por defecto, informes/informe-estado-<fecha>.pdf)")
    args = ap.parse_args()
    hoy = args.fecha
    salida = args.salida or SALIDA_DIR / f"informe-estado-{hoy.isoformat()}.pdf"

    configurar_fuentes()
    fases = leer_fases()
    S = estilos()
    h = helpers(S)

    with tempfile.TemporaryDirectory() as tmp:
        figs = {"cronograma": Path(tmp) / "cronograma.png", "f0": Path(tmp) / "f0.png",
                "vtl": Path(tmp) / "vtl.png"}
        fig_cronograma(figs["cronograma"], fases, hoy)
        fig_f0(figs["f0"])
        fig_vtl(figs["vtl"])
        story = contenido({**h, "fases": fases, "hoy": hoy, "figs": figs})

        def pie(canvas, doc):
            canvas.saveState()
            canvas.setFont("Base", 7.5)
            canvas.setFillColor(colors.HexColor(TINTA3))
            canvas.drawString(2 * cm, 1.2 * cm,
                              f"Proyecto Anima · Módulo de Voz · Informe de estado, {fecha_corta(hoy)} {hoy.year}")
            canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
            canvas.restoreState()

        doc = SimpleDocTemplate(str(salida), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                                topMargin=1.8 * cm, bottomMargin=2 * cm,
                                title="Módulo de Voz — Informe de estado", author=AUTOR,
                                subject=f"Proyecto Anima · estado al {hoy.isoformat()}")
        doc.build(story, onFirstPage=pie, onLaterPages=pie)
    print(f"Informe generado: {salida}")


if __name__ == "__main__":
    main()
