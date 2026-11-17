"""
Tests de variantes.py y de g = g_conocida + g_resto en fenotipo.py (punto 7
de la entrega del 9/11): VZ-14, VZ-15 y las guardas.
"""

import csv
import dataclasses
import shutil
from pathlib import Path

import numpy as np
import pytest

from tfc_voz import variantes
from tfc_voz.cohorte import generar_cohorte, leer_cohorte
from tfc_voz.fenotipo import generar_fenotipos
from tfc_voz.genotipo import SEMILLA
from tfc_voz.parametros import NIVELES, PARAMETROS
from tfc_voz.poblacion import EFECTOS, configuracion_neutra

RAIZ = Path(__file__).resolve().parents[1]
N = 200_000
TOLERANCIA_FRECUENCIA = 0.01  # VZ-14, parte 2
TOLERANCIA_H2 = 0.01          # VZ-14, parte 3: la misma de VZ-01 a VZ-04
# VZ-15: la referencia es el segundo nivel declarado de f0_medio, 0,006086 (el
# valor exacto con el centrado por subpoblacion; actualizacion del 10/11), y
# nada mas. Que se parezca al 0,61 % de Di et al. (2024) es solo un control de
# orden de magnitud: aquella cifra es el desempeno fuera de muestra de un
# puntaje construido con todos los estadisticos resumen, no la varianza de una
# variante (respuesta del 12/11).
VZ15_REFERENCIA = NIVELES.de("segundo_nivel")["f0_medio"]
VZ15_FACTOR = 2.0
CON_VARIANTE = {v.parametro: v for v in NIVELES.variantes}
SIN_VARIANTE = [p.nombre for p in PARAMETROS if p.nombre not in CON_VARIANTE]


@pytest.fixture(scope="module")
def cohorte_real():
    ruta = RAIZ / "cohorte_anima.csv"
    if not ruta.exists():
        pytest.skip("cohorte_anima.csv no esta en el repo")
    return leer_cohorte(ruta)


@pytest.fixture(scope="module")
def fen_real(cohorte_real):
    return generar_fenotipos(cohorte_real, PARAMETROS, EFECTOS, SEMILLA)


@pytest.fixture(scope="module")
def cohorte_grande():
    return generar_cohorte(n=N)


@pytest.fixture(scope="module")
def fen_grande(cohorte_grande):
    return generar_fenotipos(cohorte_grande, PARAMETROS, configuracion_neutra(), SEMILLA)


@pytest.fixture(scope="module")
def genotipos_a_mano():
    """El archivo de genotipos leido con csv, sin pasar por variantes.py."""
    with (RAIZ / "datos" / "genotipos_voz_1000g.csv").open(encoding="utf-8") as fh:
        return {fila["muestra_1000g"]: fila for fila in csv.DictReader(fh)}


def columna(fen, rasgo, campo):
    return fen.loc[fen["rasgo"] == rasgo, campo].to_numpy()


# --- VZ-14 ------------------------------------------------------------------

@pytest.mark.parametrize("replica", [0, 7])
@pytest.mark.parametrize("rasgo", list(CON_VARIANTE))
def test_vz14_1_reales_coinciden_con_la_suma_a_mano(cohorte_real, genotipos_a_mano, rasgo, replica):
    """En las 503 reales, g_conocida = beta * (copias - 2 * p de su subpoblacion), persona por persona."""
    fen = generar_fenotipos(cohorte_real, PARAMETROS, EFECTOS, SEMILLA + replica)
    v = CON_VARIANTE[rasgo]
    reales = cohorte_real["origen"] == "1000g"
    assert reales.sum() == 503
    obtenido = columna(fen, rasgo, "g_conocida")[reales.to_numpy()]
    esperado = [v.beta * (int(genotipos_a_mano[m][v.rs]) - 2 * v.frecuencias[s])
                for m, s in zip(cohorte_real.loc[reales, "muestra_1000g"], cohorte_real.loc[reales, "subpoblacion"])]
    assert np.array_equal(obtenido, np.array(esperado))


@pytest.mark.parametrize("rasgo", list(CON_VARIANTE))
def test_vz14_2_frecuencia_recuperada_en_las_simuladas(cohorte_grande, fen_grande, rasgo):
    """Con 200.000 personas, la frecuencia de las simuladas por subpoblacion, a menos de 0,01."""
    v = CON_VARIANTE[rasgo]
    simuladas = (cohorte_grande["origen"] == "simulada").to_numpy()
    p = cohorte_grande["subpoblacion"].map(v.frecuencias).to_numpy()
    copias = np.rint(columna(fen_grande, rasgo, "g_conocida") / v.beta + 2 * p)
    assert set(np.unique(copias)) <= {0, 1, 2}
    for s, p_s in v.frecuencias.items():
        de_s = simuladas & (cohorte_grande["subpoblacion"] == s).to_numpy()
        assert abs(copias[de_s].mean() / 2 - p_s) < TOLERANCIA_FRECUENCIA, s


@pytest.mark.parametrize("rasgo", SIN_VARIANTE)
def test_vz14_3_g_conocida_es_cero_sin_variante(fen_grande, rasgo):
    assert np.all(columna(fen_grande, rasgo, "g_conocida") == 0)


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_vz14_3_la_varianza_de_g_sigue_siendo_h2(fen_grande, p):
    assert abs(columna(fen_grande, p.nombre, "g").var() - p.heredabilidad) < TOLERANCIA_H2


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_vz14_3_la_varianza_esperada_cierra_exacto(p):
    """V (por subpoblacion, con la composicion registrada) + (h2 - V declarado) = h2."""
    v = CON_VARIANTE[p.nombre].varianza(NIVELES.composicion) if p.nombre in CON_VARIANTE else 0.0
    resto = p.heredabilidad - NIVELES.de("segundo_nivel")[p.nombre]
    assert v + resto == pytest.approx(p.heredabilidad, abs=1e-6)


def test_g_resto_tiene_varianza_h2_menos_v(fen_grande):
    for p in PARAMETROS:
        g_resto = columna(fen_grande, p.nombre, "g") - columna(fen_grande, p.nombre, "g_conocida")
        objetivo = p.heredabilidad - NIVELES.de("segundo_nivel")[p.nombre]
        assert abs(g_resto.var() - objetivo) < TOLERANCIA_H2, p.nombre


# --- VZ-15 ------------------------------------------------------------------

@pytest.mark.parametrize("cual", ["cohorte 2.0", "200.000"])
def test_vz15_varianza_conocida_de_f0_medio(fen_real, fen_grande, cual):
    """Var(g_conocida) de f0_medio alrededor de 0,0062: si se va por mas de un factor de dos, parar."""
    fen = fen_real if cual == "cohorte 2.0" else fen_grande
    v = columna(fen, "f0_medio", "g_conocida").var()
    assert VZ15_REFERENCIA / VZ15_FACTOR < v < VZ15_REFERENCIA * VZ15_FACTOR, v


# --- Replicas -----------------------------------------------------------------

def test_reales_fijas_y_simuladas_sorteadas_en_cada_replica(cohorte_real):
    a = generar_fenotipos(cohorte_real, PARAMETROS, EFECTOS, SEMILLA)
    b = generar_fenotipos(cohorte_real, PARAMETROS, EFECTOS, SEMILLA + 1)
    reales = (cohorte_real["origen"] == "1000g").to_numpy()
    for rasgo in CON_VARIANTE:
        ga, gb = columna(a, rasgo, "g_conocida"), columna(b, rasgo, "g_conocida")
        assert np.array_equal(ga[reales], gb[reales])
        assert not np.array_equal(ga[~reales], gb[~reales])


# --- Guardas ------------------------------------------------------------------

def test_alineacion_pasa_con_el_archivo_entregado(cohorte_real):
    genotipos = variantes.cargar_genotipos(NIVELES.variantes)
    assert variantes.verificar_alineacion(cohorte_real, genotipos, NIVELES.variantes) < 0.005


def test_alelo_invertido_es_un_error(cohorte_real):
    genotipos = variantes.cargar_genotipos(NIVELES.variantes)
    genotipos["rs369031872"] = 2 - genotipos["rs369031872"]
    with pytest.raises(ValueError, match="rs369031872.*invertido"):
        variantes.verificar_alineacion(cohorte_real, genotipos, NIVELES.variantes)


def test_rechaza_archivo_que_no_coincide_con_su_huella(tmp_path):
    origen = RAIZ / "datos" / "genotipos_voz_1000g.csv"
    shutil.copy(origen.with_name("genotipos_voz_1000g.meta.json"), tmp_path)
    lineas = origen.read_text(encoding="utf-8").splitlines(keepends=True)
    lineas[1] = lineas[1].replace(",0,", ",2,", 1)
    (tmp_path / origen.name).write_text("".join(lineas), encoding="utf-8", newline="")
    with pytest.raises(ValueError, match="huella"):
        variantes.cargar_genotipos(NIVELES.variantes, tmp_path / origen.name)


def test_persona_real_sin_genotipo_es_un_error(cohorte_real):
    genotipos = variantes.cargar_genotipos(NIVELES.variantes).iloc[1:]
    with pytest.raises(ValueError, match="faltan genotipos"):
        generar_fenotipos(cohorte_real, PARAMETROS, EFECTOS, SEMILLA, genotipos=genotipos)


def test_varianza_conocida_mayor_que_h2_es_un_error():
    chica = dataclasses.replace(PARAMETROS[0], heredabilidad=0.001)
    with pytest.raises(ValueError, match="supera la h2"):
        generar_fenotipos(generar_cohorte(), [chica], configuracion_neutra(), SEMILLA)
