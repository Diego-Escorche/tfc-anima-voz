"""
Tests de replicas.py (tabla predictiva y replicas) y de recuperacion.py.

Todos usan semillas fuera de las 20 de la corrida oficial (20261019 + r): la
tolerancia del criterio se fija antes de ver esa corrida (respuesta del 12/11).
"""

import dataclasses
from pathlib import Path

import numpy as np
import pytest

from anima_spine import predictions
from tfc_voz.cohorte import leer_cohorte
from tfc_voz.fenotipo import generar_fenotipos, oraculo
from tfc_voz.genotipo import SEMILLA
from tfc_voz.metricas import delta_r2
from tfc_voz.parametros import NIVELES, PARAMETROS
from tfc_voz.poblacion import EFECTOS
from tfc_voz.recuperacion import (ToleranciaSinFijar, barrido_recuperacion, escribir_recuperacion,
                                  evaluar_criterio, filas_recuperacion)
from tfc_voz.replicas import COLUMNAS_TABLA, correr_replica

SEMILLA_TESTS = SEMILLA + 900  # fuera de las semillas de la corrida oficial
RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cohorte():
    ruta = RAIZ / "cohorte_anima.csv"
    if not ruta.exists():
        pytest.skip("cohorte_anima.csv no esta en el repo")
    return leer_cohorte(ruta)


@pytest.fixture(scope="module")
def tabla(cohorte):
    return correr_replica(cohorte, 3, semilla_base=SEMILLA_TESTS)


@pytest.fixture(scope="module")
def barrido(cohorte):
    return barrido_recuperacion(cohorte, semilla_base=SEMILLA_TESTS)


# --- Tabla predictiva ---------------------------------------------------------

def test_forma_de_la_tabla(tabla, cohorte):
    assert list(tabla.columns) == COLUMNAS_TABLA
    assert len(tabla) == 16_000
    assert set(tabla["dominio"]) == {"voz"}
    assert set(tabla["linea_base"]) == set(predictions.LINEAS_BASE)
    sub = cohorte[cohorte["particion"].isin(["calibracion", "prueba"])]
    esperado = set(zip(sub["individuo_id"], sub["particion"]))
    for (rasgo, base), grupo in tabla.groupby(["rasgo", "linea_base"]):
        assert set(zip(grupo["individuo_id"], grupo["particion"])) == esperado, (rasgo, base)
    assert (tabla[["sigma", "sigma_base", "sigma_oraculo"]] > 0).all().all()


def test_mu_y_sigma_del_completo_iguales_en_las_dos_lineas_base(tabla):
    a, b = (tabla[tabla["linea_base"] == base].sort_values(["rasgo", "individuo_id"]).reset_index(drop=True)
            for base in predictions.LINEAS_BASE)
    assert np.array_equal(a[["mu", "sigma"]].to_numpy(), b[["mu", "sigma"]].to_numpy())
    assert not np.array_equal(a["mu_base"].to_numpy(), b["mu_base"].to_numpy())


def test_y_real_y_oraculo_son_los_de_fenotipo(tabla, cohorte):
    """y real de la semilla base + r, y el oraculo de fenotipo.oraculo (reusado, no duplicado)."""
    fen = generar_fenotipos(cohorte, PARAMETROS, EFECTOS, SEMILLA_TESTS + 3)
    orac = oraculo(cohorte, fen, PARAMETROS, EFECTOS)
    unido = (tabla.merge(fen[["individuo_id", "rasgo", "y"]], on=["individuo_id", "rasgo"])
             .merge(orac, on=["individuo_id", "rasgo"], suffixes=("", "_fenotipo")))
    assert len(unido) == len(tabla)
    assert np.array_equal(unido["y_real"], unido["y"])
    assert np.array_equal(unido["mu_oraculo"], unido["mu_oraculo_fenotipo"])
    assert np.array_equal(unido["sigma_oraculo"], unido["sigma_oraculo_fenotipo"])


def test_correr_replica_es_determinista(tabla, cohorte):
    assert tabla.equals(correr_replica(cohorte, 3, semilla_base=SEMILLA_TESTS))
    otra = correr_replica(cohorte, 4, semilla_base=SEMILLA_TESTS)
    assert not np.array_equal(tabla["y_real"], otra["y_real"])


# --- Recuperacion -------------------------------------------------------------

def test_filas_de_una_replica(tabla):
    declarado = NIVELES.de("caso_base")
    filas = filas_recuperacion(tabla, 3, SEMILLA_TESTS + 3, declarado)
    assert len(filas) == 16 and all(list(f) == list(predictions.CAMPOS_RECUPERACION) for f in filas)
    prueba = tabla[tabla["particion"] == "prueba"]
    for f in filas:
        g = prueba[(prueba["rasgo"] == f["rasgo"]) & (prueba["linea_base"] == f["linea_base"])]
        assert len(g) == 500
        assert (f["delta_r2_total"], f["delta_r2_parcial"]) == pytest.approx(
            delta_r2(g["y_real"], g["mu_base"], g["mu"]))
        assert f["nivel_declarado"] == declarado[f["rasgo"]]


def test_barrido_de_20_replicas_pasa_la_validacion_del_paquete(barrido, tmp_path):
    assert len(barrido) == predictions.REPLICAS * 8 * 2
    assert {f["semilla"] - f["replica"] for f in barrido} == {SEMILLA_TESTS}
    ruta = escribir_recuperacion(barrido, tmp_path)
    assert ruta.name == "recuperacion_voz.csv"
    assert len(predictions.cargar_recuperacion(ruta)) == 320


def test_sin_tolerancia_fijada_no_hay_veredicto(barrido):
    assert NIVELES.criterio_recuperacion["tolerancia"] is None
    with pytest.raises(ToleranciaSinFijar, match="simulacion del nulo"):
        evaluar_criterio(barrido)


def test_con_tolerancia_fijada_usa_la_de_la_configuracion(barrido):
    criterio = {**NIVELES.criterio_recuperacion, "tolerancia": 0.123}
    resultado = evaluar_criterio(barrido, dataclasses.replace(NIVELES, criterio_recuperacion=criterio))
    assert resultado["tolerancia"] == 0.123 and resultado["linea_base"] == "ancestria sexo edad"
    assert set(resultado["por_rasgo"]) == {p.nombre for p in PARAMETROS}


def test_el_segundo_nivel_no_lleva_criterio(cohorte):
    filas = barrido_recuperacion(cohorte, nivel="segundo_nivel", columna_g="g_conocida",
                                 semilla_base=SEMILLA_TESTS, replicas=1)
    assert {f["rasgo"]: f["nivel_declarado"] for f in filas} == NIVELES.de("segundo_nivel")
    criterio = {**NIVELES.criterio_recuperacion, "tolerancia": 0.123}
    with pytest.raises(ValueError, match="sin criterio"):
        evaluar_criterio(filas, dataclasses.replace(NIVELES, criterio_recuperacion=criterio))


def test_rechaza_un_archivo_con_19_replicas(barrido, tmp_path):
    with pytest.raises(AssertionError, match="réplicas"):
        escribir_recuperacion([f for f in barrido if f["replica"] != 19], tmp_path)
