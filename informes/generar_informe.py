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
  - Las h2 (figura y textos) se leen de parametros.py, y los casos VZ-01 a
    VZ-05 se recalculan con el generador al armar el informe.
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
import numpy as np
from matplotlib import font_manager
from matplotlib.lines import Line2D
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
from tfc_voz.genotipo import SEMILLA, generar_cohorte_sintetica  # noqa: E402
from tfc_voz.parametros import H2_MAXIMOS, PARAMETROS  # noqa: E402  (valores reales, no copiados)

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
CIERRES_REALES = {}

# Techo facial declarado por el modulo Rostro, para comparar con la h2 media de Voz.
H2_ROSTRO = 0.079

# VZ-01 a VZ-05 se recalculan al generar el informe, igual que en
# tests/test_generador.py (cohorte propia de 100.000, ~4 s).
N_COHORTE_VZ = 100_000

# VZ-07 (20 semillas) no se recalcula: tarda ~45 s. Valores de la ultima
# corrida de pytest.
VZ07_ERROR_MAXIMO = 0.0043
TESTS_EN_VERDE = (51, 51)


def calcular_vz():
    """VZ-01 a VZ-05 sobre el generador, con el mismo criterio que los tests."""
    cohorte = generar_cohorte_sintetica(N_COHORTE_VZ, semilla=SEMILLA)
    filas, max_perm = [], 0.0
    for p in PARAMETROS:
        g = np.array([ind.scores_geneticos[p.nombre] for ind in cohorte])
        total = np.array([ind.score_total(p.nombre) for ind in cohorte])
        filas.append((p, float(np.corrcoef(g, total)[0, 1] ** 2)))
        g_mezclado = np.random.default_rng(SEMILLA).permutation(g)
        max_perm = max(max_perm, float(np.corrcoef(g_mezclado, total)[0, 1] ** 2))
    return {"filas": filas, "max_perm": max_perm}


def contenido(ctx):
    """Arma la lista de flowables del informe. ctx trae fases, hoy, helpers y casos VZ."""
    P, bullets, tabla, kpis, figura = ctx["P"], ctx["bullets"], ctx["tabla"], ctx["kpis"], ctx["figura"]
    fases, hoy, figs, vz = ctx["fases"], ctx["hoy"], ctx["figs"], ctx["vz"]
    en_curso = next((f for f in fases if estado(f, hoy) == "curso"), None)
    pct = round(100 * ventana_consumida(en_curso, hoy)) if en_curso else None
    h2s = [p.heredabilidad for p in PARAMETROS]
    promedio = sum(h2s) / len(h2s)
    error_max = max(abs(r2 - p.heredabilidad) for p, r2 in vz["filas"])

    story = [
        P("Módulo de Voz — Informe de estado", "titulo"), Spacer(1, 4),
        P(f"Proyecto Anima · Trabajo Final de Carrera, Universidad de Belgrano · {AUTOR} · "
          f"{fecha_larga(hoy)}", "sub"),
        Spacer(1, 14),
        kpis([
            (f"{en_curso.hechas} / {en_curso.total}" if en_curso else "—",
             f"tareas de la Fase {en_curso.numero} cerradas, con el {pct} % de su ventana consumida"
             if en_curso else "sin fase en curso"),
            (f"{n(100 * promedio)} %", "h² media de Voz con la regla agregada (antes, 10,4 %)"),
            (f"{TESTS_EN_VERDE[0]} / {TESTS_EN_VERDE[1]}", "tests en verde, incluidos VZ-01 a VZ-05 y VZ-07"),
            ("3", "decisiones del grupo que bloquean (sección 5)"),
        ]),
        Spacer(1, 10),
        P("Resumen", "h1"),
    ]
    story += bullets([
        "<b>El alcance se acotó el 19 de octubre.</b> Salieron la síntesis de audio, la validación contra audio "
        "real y la interfaz web. El cronograma pasó a 150 horas en 17 semanas, y los resultados de Voz cierran el "
        "21 de diciembre.",
        f"<b>Las heredabilidades se recargaron con la regla agregada de cinco vocales</b> de la tabla S6 de "
        f"Gisladóttir et al. (2023). La h² media de Voz bajó de 10,4 % a {n(100 * promedio)} %: los valores "
        "anteriores eran el máximo de cada medida, no un valor típico.",
        "<b>El VTL estaba sobreestimado al doble.</b> Pasó de 0,13 (h² de gemelos dividido por dos) a 0,0606, el "
        "valor directo de la S6. El cociente real entre las dos escalas es 0,23, no 0,5.",
        "<b>El código volvió a arrancar.</b> Entorno verificado en un venv limpio, valores contrastados contra el "
        "CSV de la S6 y los primeros casos de prueba en verde.",
        f"<b>Consecuencia para el grupo:</b> la h² media de Voz queda a {n(100 * (H2_ROSTRO - promedio))} puntos "
        f"del techo facial declarado ({n(100 * H2_ROSTRO)} %). El orden original del gradiente se sostiene, pero "
        "por un margen que no alcanza para afirmarlo.",
    ])

    story += [P("1. Cómo va el proyecto", "h1"),
              figura(figs["cronograma"], 17, 3.3 / 7.2),
              P(f"Figura 1. Avance por fase al {fecha_corta(hoy)}, leído de seguimiento-modulo-voz.md. El número "
                "a la derecha indica tareas cerradas sobre el total.", "cap"),
              tabla_fases(fases, hoy, tabla),
              P("Cronograma y riesgo", "h2")]
    story += bullets([
        "150 horas en 17 semanas, unas 10 h por semana. Las dos semanas de fiestas (22 dic – 4 ene) quedan sin "
        "compromisos.",
        "<b>Los resultados de Voz cierran el 21 de diciembre</b>, con predicciones_voz.csv definitivo. Enero queda "
        "para el prototipo y las 30 horas de redacción, el bloque más grande del plan.",
        "<b>Riesgo principal: que el código no arranque.</b> No había avance desde fines de septiembre. La semana 1 "
        "se diseñó como el hito más barato, sin decisiones de diseño nuevas, y sus tareas de código están cerradas.",
        "Falta superponer el calendario de entregas de la cátedra posterior a la Práctica 10: las semanas que "
        "coincidan bajan a la mitad.",
    ])

    story += [P("2. Qué se hizo esta semana", "h1"), tabla([
        ["Tarea", "Resultado"],
        ["Alcance", "El corpus de audio (~12 GB), el script de extracción por lote, pyworld y Flask salieron del "
         "disco y del entorno. Lo hecho con audio real quedó documentado en historico-vctk.md."],
        ["Entorno", "Python 3.12.4. tests/test_setup.py pasa en un venv nuevo instalado sólo con requirements.txt; "
         "parselmouth estima 150,0 Hz sobre una onda de 150 Hz."],
        ["Heredabilidades", "parametros.py con los valores exactos de la S6, su IC95 % y su fila. Los máximos "
         "anteriores quedan aparte, sólo para un análisis de sensibilidad. La S6 está versionada en referencias/."],
        ["Casos de prueba", "VZ-01 a VZ-05 y VZ-07 en pytest, sobre una cohorte propia de 100.000 personas "
         "(sección 4). Semilla 20261019, la misma de la cohorte compartida."],
        ["Documentación", "README, SETUP, decisiones-fase1 y el seguimiento actualizados al alcance del 19/10 y al "
         "cronograma de 17 semanas."],
    ], [4 * cm, 13 * cm])]

    story += [P("3. El dato bibliográfico", "h1"),
              P("Gisladóttir et al. (2023) informa 72 medidas acústicas y 41 quedan por debajo del 5 %. Los valores "
                "cargados hasta ahora eran el máximo de cada rasgo entre todas las tareas y vocales: una envolvente "
                "superior. La regla adoptada toma, para cada rasgo, la medida agregada de las cinco vocales del "
                "estudio. Es la única que existe para todos, porque los formantes no se midieron en lectura."),
              figura(figs["h2"], 17, 3.4 / 7.2),
              P("Figura 2. h²-SNP por parámetro con la regla agregada (punto e IC95 %) y el máximo que estaba cargado "
                "antes (anillo). En f2 coinciden. Jitter y HNR no están en la S6 y llevan un valor conservador de "
                "0,05, sin intervalo. Las líneas punteadas marcan la media de Voz y el techo facial declarado.",
                "cap"),
              tabla([
                  ["Regla de lectura", "VTL", "h² media de Voz"],
                  ["Máximo por rasgo", "0,13 (gemelos ÷ 2)", "10,4 %"],
                  ["Máximo por rasgo", "0,0606 (S6)", "9,6 %"],
                  ["<b>Agregada de cinco vocales</b>", "<b>0,0606 (S6)</b>", f"<b>{n(100 * promedio)} %</b>"],
              ], [6 * cm, 5.5 * cm, 5.5 * cm]),
              P("Qué cambia para la hipótesis", "h2")]
    story += bullets([
        "<b>Las h² ya están por encima de la línea base.</b> Gisladóttir ajustó cada rasgo por edad, IMC, altura y "
        "micrófono dentro de cada sexo antes de estimarlas. La afirmación de que la línea base ya captura casi toda "
        "la señal heredable de la voz es falsa y hay que sacarla del documento individual.",
        f"<b>El escalón Rostro–Voz es de {n(100 * (H2_ROSTRO - promedio))} puntos.</b> No alcanza para afirmar el "
        "orden. Recomendación: formular la hipótesis en dos niveles, decidido antes de ver resultados.",
        "<b>Cuatro intervalos cruzan el cero</b> (f0_variabilidad, f1, f3 y vtl). Los cinco máximos anteriores lo "
        "excluían todos; con la regla agregada, tres de esos cinco pasan a cruzarlo.",
        "<b>Queda abierto</b> si la h² es fracción de la varianza residual y no de la total. Si lo es, el techo del "
        "ΔR² sobre una línea base con sexo y edad es h² × (1 − R² de la línea base), más bajo todavía, y aplica "
        "igual a Rostro.",
    ])

    filas_vz = [["Parámetro", "h² pedida", "h² recuperada", "Error", "Estado"]]
    for p, r2 in vz["filas"]:
        error = abs(r2 - p.heredabilidad)
        filas_vz.append([p.nombre, n(p.heredabilidad, 4), n(r2, 4), n(error, 4),
                         "Pasó" if error < 0.01 else "Falló"])
    t_vz = tabla(filas_vz, [4.4 * cm, 3 * cm, 3.2 * cm, 3 * cm, 3.4 * cm])
    t_vz.setStyle(TableStyle([("ALIGN", (1, 0), (3, -1), "RIGHT")]))
    story += [P("4. Casos de prueba sobre el generador", "h1"),
              P(f"Se usa una cohorte propia de {N_COHORTE_VZ:,} personas, no cohorte_anima.csv: con 2.000 personas "
                "el ruido de muestreo supera la tolerancia de 0,01 la mitad de las veces en f2. Estos casos validan "
                "el generador, no el modelo.".replace(",", ".")),
              KeepTogether([t_vz, P("Tabla 1. VZ-01 a VZ-04: R² del puntaje total explicado por el puntaje "
                                    "genético, recalculado al generar este informe (semilla 20261019).", "cap")]),
              tabla([
                  ["ID", "Qué verifica", "Resultado", "Estado"],
                  ["VZ-01 a VZ-04", "La h² pedida se recupera con error menor a 0,01",
                   f"Error máximo {n(error_max, 4)} en los 8 parámetros", "Pasó"],
                  ["VZ-05", "Con el puntaje genético mezclado, el R² cae por debajo de 0,005",
                   f"R² máximo {n(vz['max_perm'], 5)}", "Pasó"],
                  ["VZ-06", "Particiones de entrenamiento y calibración disjuntas", "Requiere cohorte_anima.csv",
                   "Pendiente (27 oct)"],
                  ["VZ-07", "VZ-01 a VZ-04 con 20 semillas (20261019 + 0…19)",
                   f"Error máximo {n(VZ07_ERROR_MAXIMO, 4)} entre todas", "Pasó"],
                  ["VZ-08, VZ-09", "Síntesis de audio y validación contra audio real", "Fuera del alcance desde el "
                   "19/10", "Retirados"],
                  ["VZ-10 a VZ-12", "Cobertura y ΔR² contra las dos líneas base", "Requieren el modelo y la "
                   "calibración", "Pendiente (dic)"],
                  ["VZ-13", "Tabla de orden de los 8 parámetros por ΔR²", "Requiere los ΔR²", "Pendiente (dic)"],
              ], [2.6 * cm, 6.4 * cm, 5 * cm, 3 * cm])]

    story += [P("5. Dependencias y decisiones pendientes", "h1"), tabla([
        ["Qué espera Voz", "De quién", "Para cuándo", "Plan alternativo"],
        ["cohorte_anima.csv v1.0 congelada", "Grupo", "27 oct", "Ya existe; el pedido es que no cambie"],
        ["Línea base heterocedástica (OE2)", "Grupo", "24-30 nov", "Una sola línea base, declarada"],
        ["Capa de calibración conformal (OE4)", "Tomás", "1-7 dic", "La escribe Diego (~6 h)"],
        ["ΔR² de Rostro y Temperamento sobre la misma cohorte", "Audrey y Tomás", "26 ene",
         "El documento individual se sostiene con el ΔR² de Voz y su IC"],
    ], [5.4 * cm, 2.6 * cm, 2.2 * cm, 6.8 * cm]),
              P("Decisiones del grupo que bloquean", "h2")]
    story += bullets([
        "<b>Con qué criterio se eligen las h² en los tres módulos.</b> Si Voz usa la regla agregada y los otros "
        "máximos, el contraste entre dominios queda sesgado por cómo leyó la bibliografía cada uno.",
        "<b>Cómo queda formulada la hipótesis:</b> tres niveles, dos niveles o reordenada.",
        "<b>Qué afirma el TFC:</b> un gradiente entre dominios, o que la maquinaria de cuantificación de "
        "incertidumbre funciona y cómo responde a la heredabilidad.",
    ])

    story += [P("6. Próximos pasos", "h1"), tabla([
        ["#", "Paso", "Por qué"],
        ["1", "Entregar el dato bibliográfico con su regla de lectura a Audrey, Tomás y Brest",
         "Es la tarea que falta de la semana 1 y condiciona cómo se formula la hipótesis."],
        ["2", "Migrar a cohorte_anima.csv con sus particiones (27 oct – 2 nov)",
         "Sin la cohorte compartida no hay contraste pareado entre dominios."],
        ["3", "Primer predicciones_voz.csv que pase las pruebas de contrato",
         "Detecta temprano cualquier desacuerdo con el formato común."],
        ["4", "Acordar el criterio de h² de los tres módulos", "Ver sección 5."],
        ["5", "Verificar la elegibilidad para la defensa de febrero", "Es el único riesgo que no se arregla con horas."],
    ], [0.7 * cm, 7.3 * cm, 9 * cm])]

    story += [Spacer(1, 10),
              P("Recordatorio de encuadre: lo que se defiende es la cuantificación de la incertidumbre, no la "
                "precisión de la reconstrucción. Un ΔR² chico (y prácticamente nulo en jitter y HNR) es el "
                f"resultado esperado: la h² de la voz va del {n(100 * min(h2s))} al {n(100 * max(h2s))} % por "
                f"parámetro, con una media de {n(100 * promedio)} %.", "cap")]
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


def fig_h2(ruta):
    """h2 por parametro: regla agregada con IC95% y el maximo que estaba cargado antes."""
    ps = sorted(PARAMETROS, key=lambda p: p.heredabilidad)
    promedio = 100 * sum(p.heredabilidad for p in PARAMETROS) / len(PARAMETROS)
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=220)
    ys = range(len(ps))
    for y, p in zip(ys, ps):
        if p.fila_s6:
            ax.plot([100 * p.ic95_inf, 100 * p.ic95_sup], [y, y], color=AZUL, lw=2,
                    solid_capstyle="round", zorder=2)
        maximo = H2_MAXIMOS.get(p.nombre)
        if maximo is not None and maximo != p.heredabilidad:
            ax.scatter(100 * maximo, y, s=46, facecolor="white", edgecolor=NARANJA, linewidth=1.6, zorder=3)
        ax.scatter(100 * p.heredabilidad, y, s=46, color=AZUL, edgecolor="white", linewidth=1.2, zorder=4)
        # valores en una columna fija: pegados a cada punto chocaban con las lineas de referencia
        ax.text(26.5, y, f"{n(100 * p.heredabilidad)} %", va="center", ha="right", fontsize=7.5, color=TINTA)
    ax.axvline(0, color=TINTA3, lw=0.8)
    ax.axvline(promedio, color=AZUL, lw=1, ls=(0, (3, 2)), zorder=1)
    ax.axvline(100 * H2_ROSTRO, color=TINTA3, lw=1, ls=(0, (3, 2)), zorder=1)
    y_tope = len(ps) - 0.35
    ax.text(promedio - 0.3, y_tope, f"media Voz {n(promedio)} %", fontsize=7, color=TINTA2, ha="right", va="bottom")
    ax.text(100 * H2_ROSTRO + 0.3, y_tope, f"techo Rostro {n(100 * H2_ROSTRO)} %", fontsize=7, color=TINTA2,
            ha="left", va="bottom")
    etiquetas = [p.nombre if p.fila_s6 else f"{p.nombre} (sin S6)" for p in ps]
    ax.set_yticks(list(ys), etiquetas, fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("h²-SNP (%)", fontsize=8)
    ax.set_xlim(-6, 27)
    ax.set_xticks(range(-5, 25, 5))
    ax.set_ylim(-0.6, len(ps) + 0.2)
    ax.grid(axis="x", color=GRIS_GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(handles=[Line2D([], [], color=AZUL, lw=2, marker="o", markersize=6, markeredgecolor="white",
                              label="Regla agregada (punto e IC95 %)"),
                       Line2D([], [], lw=0, marker="o", markersize=6, markerfacecolor="white",
                              markeredgecolor=NARANJA, markeredgewidth=1.6, label="Máximo cargado antes")],
              loc="upper center", bbox_to_anchor=(0.45, -0.16), ncol=2, frameon=False, fontsize=7.5)
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
        figs = {"cronograma": Path(tmp) / "cronograma.png", "h2": Path(tmp) / "h2.png"}
        fig_cronograma(figs["cronograma"], fases, hoy)
        fig_h2(figs["h2"])
        story = contenido({**h, "fases": fases, "hoy": hoy, "figs": figs, "vz": calcular_vz()})

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
