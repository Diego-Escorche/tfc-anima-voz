"""
Tests de scripts/exportar_para_calibracion.py (datos de Voz para la capa de
calibracion de Tomas).
"""

import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from tfc_voz.cohorte import leer_cohorte
from tfc_voz.fenotipo import generar_fenotipos
from tfc_voz.genotipo import SEMILLA
from tfc_voz.parametros import PARAMETROS
from tfc_voz.poblacion import EFECTOS

RAIZ = Path(__file__).resolve().parents[1]
# SHA-256 de informes/voz_para_calibracion.csv tal como se le mando a Tomas
# (commit 333940a). Se fija aca para que no dependa de la copia del repo.
HUELLA_ENVIADA = "22fb376eff0eeafb53b672480cc8539ffb90e1431c273b16747cf69f9bcb1dc6"
_spec = importlib.util.spec_from_file_location("exportar_para_calibracion",
                                               RAIZ / "scripts" / "exportar_para_calibracion.py")
exportar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exportar)


@pytest.fixture(scope="module")
def cohorte():
    if not (RAIZ / "cohorte_anima.csv").exists():
        pytest.skip("cohorte_anima.csv no esta en el repo")
    return leer_cohorte(RAIZ / "cohorte_anima.csv")


@pytest.fixture(scope="module")
def datos(cohorte):
    return exportar.armar_datos(cohorte)


def test_pasa_la_validacion(datos, cohorte):
    exportar.validar(datos, cohorte)


def test_forma_del_archivo(datos):
    assert list(datos.columns) == exportar.COLUMNAS
    assert len(datos) == 8000
    assert set(datos["particion"]) == {"calibracion", "prueba"}
    assert datos.groupby("rasgo").size().to_dict() == {p.nombre: 1000 for p in PARAMETROS}


def test_y_real_es_el_fenotipo_de_la_replica_0(datos, cohorte):
    fen = generar_fenotipos(cohorte, PARAMETROS, EFECTOS, SEMILLA)
    unido = datos.merge(fen, on=["individuo_id", "rasgo"])
    assert len(unido) == len(datos)
    assert np.array_equal(unido["y_real"].to_numpy(), unido["y"].to_numpy())


def test_el_csv_regenerado_es_identico_al_enviado(datos, tmp_path):
    """Con el oraculo calculado en fenotipo.py, el archivo no cambia ni un byte."""
    ruta = tmp_path / "voz_para_calibracion.csv"
    exportar.escribir(datos, ruta)
    assert hashlib.sha256(ruta.read_bytes()).hexdigest() == HUELLA_ENVIADA


def test_el_oraculo_esta_calibrado(datos):
    """(y_real - mu_oraculo) / sigma_oraculo es normal estandar: e / sqrt(1 - h2)."""
    z = (datos["y_real"] - datos["mu_oraculo"]) / datos["sigma_oraculo"]
    assert abs(z.mean()) < 0.05
    assert abs(z.std() - 1) < 0.05


# --- La validacion rechaza archivos mal armados ------------------------------

def test_rechaza_fila_duplicada(datos, cohorte):
    malo = datos.copy()
    malo.loc[1, ["individuo_id", "particion"]] = malo.loc[0, ["individuo_id", "particion"]].to_numpy()
    with pytest.raises(AssertionError, match="mas de una fila"):
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
