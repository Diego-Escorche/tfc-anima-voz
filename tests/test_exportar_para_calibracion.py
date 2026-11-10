"""
Tests de scripts/exportar_para_calibracion.py (datos de Voz para la capa de
calibracion de Tomas): cohorte 2.0, 20 replicas, 160.000 filas.
"""

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from tfc_voz.cohorte import leer_cohorte
from tfc_voz.fenotipo import generar_fenotipos
from tfc_voz.genotipo import SEMILLA
from tfc_voz.parametros import NIVELES, PARAMETROS
from tfc_voz.poblacion import EFECTOS

RAIZ = Path(__file__).resolve().parents[1]
COHORTE = RAIZ / "cohorte_anima.csv"
_spec = importlib.util.spec_from_file_location("exportar_para_calibracion",
                                               RAIZ / "scripts" / "exportar_para_calibracion.py")
exportar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exportar)


@pytest.fixture(scope="module")
def cohorte():
    if not COHORTE.exists():
        pytest.skip("cohorte_anima.csv no esta en el repo")
    return leer_cohorte(COHORTE)


@pytest.fixture(scope="module")
def datos(cohorte):
    return exportar.armar_datos(cohorte)


def test_pasa_la_validacion(datos, cohorte):
    exportar.validar(datos, cohorte)


def test_forma_del_archivo(datos):
    assert list(datos.columns) == exportar.COLUMNAS
    assert exportar.COLUMNAS[:4] == ["replica", "semilla", "dominio", "sexo"]
    assert len(datos) == 160_000
    assert set(datos["particion"]) == {"calibracion", "prueba"}
    assert datos.groupby("rasgo").size().to_dict() == {p.nombre: 20_000 for p in PARAMETROS}
    assert datos.groupby("replica").size().to_dict() == {r: 8_000 for r in range(20)}
    assert (datos["semilla"] == SEMILLA + datos["replica"]).all()


@pytest.mark.parametrize("replica", [0, 7, 19])
def test_y_real_es_el_fenotipo_de_cada_replica(datos, cohorte, replica):
    fen = generar_fenotipos(cohorte, PARAMETROS, EFECTOS, SEMILLA + replica)
    unido = datos[datos["replica"] == replica].merge(fen, on=["individuo_id", "rasgo"])
    assert len(unido) == 8_000
    assert np.array_equal(unido["y_real"].to_numpy(), unido["y"].to_numpy())


def test_las_replicas_son_distintas(datos):
    a = datos.loc[datos["replica"] == 0, "y_real"].to_numpy()
    b = datos.loc[datos["replica"] == 1, "y_real"].to_numpy()
    assert not np.allclose(a, b)


def test_sexo_es_el_de_la_cohorte(datos, cohorte):
    unido = datos.merge(cohorte[["individuo_id", "sexo"]], on="individuo_id", suffixes=("", "_cohorte"))
    assert (unido["sexo"] == unido["sexo_cohorte"]).all()


def test_el_oraculo_esta_calibrado(datos):
    """(y_real - mu_oraculo) / sigma_oraculo es normal estandar: e / sqrt(1 - h2)."""
    z = (datos["y_real"] - datos["mu_oraculo"]) / datos["sigma_oraculo"]
    assert abs(z.mean()) < 0.05  # nivel-literal-ok: tolerancia sobre z, no la h2 de jitter/hnr
    assert abs(z.std() - 1) < 0.05  # nivel-literal-ok: tolerancia sobre z, no la h2 de jitter/hnr


def test_escribe_csv_y_meta(datos, tmp_path):
    ruta = tmp_path / "voz_para_calibracion.csv"
    ruta_meta = exportar.escribir(datos, ruta, COHORTE)
    meta = json.loads(ruta_meta.read_text(encoding="utf-8"))
    assert ruta_meta.name == "voz_para_calibracion.meta.json"
    assert meta["sha256"] == hashlib.sha256(ruta.read_bytes()).hexdigest()
    assert meta["filas"] == 160_000 and meta["replicas"] == list(range(20))
    assert meta["cohorte"]["version"] == "2.0"
    assert meta["semilla_base"] == SEMILLA
    assert meta["versiones"]["anima_spine"] == "2.2" and meta["versiones"]["numpy"] == np.__version__
    assert meta["nivel_declarado"]["nivel"] == "caso_base"
    assert meta["nivel_declarado"]["valores"] == NIVELES.de("caso_base")
    assert meta["nivel_declarado"]["version"] == NIVELES.version
    assert meta["nivel_declarado"]["fijado"] == NIVELES.fijado
    assert "g_conocida" in meta["puntaje_genetico"] and "b6f8d2d8" in meta["puntaje_genetico"]
    assert "\r\n" not in ruta.read_text(encoding="utf-8")[:2000]


# --- La validacion rechaza archivos mal armados ------------------------------

def test_rechaza_fila_duplicada(datos, cohorte):
    malo = datos.copy()
    malo.loc[1, ["individuo_id", "particion", "sexo"]] = malo.loc[0, ["individuo_id", "particion", "sexo"]].to_numpy()
    with pytest.raises(AssertionError, match="mas de una fila"):
        exportar.validar(malo, cohorte)


def test_rechaza_replica_faltante(datos, cohorte):
    with pytest.raises(AssertionError, match="replicas"):
        exportar.validar(datos[datos["replica"] != 19].reset_index(drop=True), cohorte)


def test_rechaza_semilla_equivocada(datos, cohorte):
    malo = datos.copy()
    malo.loc[malo["replica"] == 3, "semilla"] = SEMILLA
    with pytest.raises(AssertionError, match="semilla"):
        exportar.validar(malo, cohorte)


def test_rechaza_dominio_equivocado(datos, cohorte):
    malo = datos.copy()
    malo.loc[0, "dominio"] = "rostro"
    with pytest.raises(AssertionError, match="dominio"):
        exportar.validar(malo, cohorte)


def test_rechaza_sexo_cambiado(datos, cohorte):
    malo = datos.copy()
    malo.loc[0, "sexo"] = 1 - malo.loc[0, "sexo"]
    with pytest.raises(AssertionError, match="sexo"):
        exportar.validar(malo, cohorte)


def test_rechaza_particion_cambiada(datos, cohorte):
    malo = datos.copy()
    malo.loc[0, "particion"] = "prueba" if malo.loc[0, "particion"] == "calibracion" else "calibracion"
    with pytest.raises(AssertionError, match="particiones"):
        exportar.validar(malo, cohorte)


def test_rechaza_individuo_faltante(datos, cohorte):
    with pytest.raises(AssertionError, match="ids"):
        exportar.validar(datos.drop(index=0).reset_index(drop=True), cohorte)


def test_rechaza_valor_no_finito(datos, cohorte):
    malo = datos.copy()
    malo.loc[0, "mu_oraculo"] = np.nan
    with pytest.raises(AssertionError, match="no finitos"):
        exportar.validar(malo, cohorte)


def test_rechaza_sigma_no_positivo(datos, cohorte):
    malo = datos.copy()
    malo.loc[0, "sigma_oraculo"] = 0.0
    with pytest.raises(AssertionError, match="sigma_oraculo"):
        exportar.validar(malo, cohorte)


def test_rechaza_columnas_en_otro_orden(datos, cohorte):
    with pytest.raises(AssertionError, match="columnas"):
        exportar.validar(datos[exportar.COLUMNAS[::-1]], cohorte)
