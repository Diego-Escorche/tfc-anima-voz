"""
Tests de cohorte.py: VZ-06 y rechazo de archivos mal formados.
"""

import json
import shutil
from pathlib import Path

import pytest

from tfc_voz.cohorte import COLUMNAS, generar_cohorte, leer_cohorte

COHORTE_REAL = Path(__file__).resolve().parents[1] / "cohorte_anima.csv"
HUELLA_2_0 = "8203824aff641fb8a7e54a09d902a887407c81f70b000846b37b9f296609abb6"
TAMANIOS = {"entrenamiento": 1000, "calibracion": 500, "prueba": 500}


def comprobar_vz06(cohorte):
    """Particiones disjuntas, que cubren a todos y con los tamanios 1.000 / 500 / 500."""
    assert cohorte["individuo_id"].is_unique
    ids = {p: set(cohorte.loc[cohorte["particion"] == p, "individuo_id"]) for p in TAMANIOS}
    assert not ids["entrenamiento"] & ids["calibracion"]
    assert not ids["entrenamiento"] & ids["prueba"]
    assert not ids["calibracion"] & ids["prueba"]
    assert set().union(*ids.values()) == set(cohorte["individuo_id"])
    assert {p: len(v) for p, v in ids.items()} == TAMANIOS


@pytest.fixture(scope="module")
def cohorte_real():
    if not COHORTE_REAL.exists():
        pytest.skip("cohorte_anima.csv no esta en el repo: copiarla del paquete anima_spine 2.2 (cohorte 2.0)")
    return leer_cohorte(COHORTE_REAL)


def test_vz06_particiones_cohorte_generada():
    """VZ-06: particiones disjuntas y con los tamanios correctos (cohorte generada)."""
    comprobar_vz06(generar_cohorte())


def test_vz06_particiones_cohorte_real(cohorte_real):
    """VZ-06: particiones disjuntas y con los tamanios correctos (cohorte_anima.csv)."""
    comprobar_vz06(cohorte_real)


def test_leer_cohorte_devuelve_el_esquema(cohorte_real):
    assert list(cohorte_real.columns) == COLUMNAS
    assert len(cohorte_real) == 2000
    assert set(cohorte_real["sexo"]) == {0, 1}


def test_la_cohorte_del_repo_es_la_2_0(cohorte_real):
    """La 2.0 congelada (entrega del 9/11): 503 personas reales de 1000 Genomes, 253 / 125 / 125."""
    meta = json.loads(COHORTE_REAL.with_suffix(".meta.json").read_text(encoding="utf-8"))
    assert meta["version"] == "2.0" and meta["sha256_csv"] == HUELLA_2_0
    reales = cohorte_real[cohorte_real["origen"] == "1000g"]
    assert len(reales) == 503 and reales["muestra_1000g"].is_unique
    assert reales["particion"].value_counts().to_dict() == {"entrenamiento": 253, "calibracion": 125,
                                                            "prueba": 125}


def test_generar_cohorte_misma_semilla_mismo_resultado():
    assert generar_cohorte().equals(generar_cohorte())


# --- Archivos mal formados: el error del paquete pasa tal cual -----------------

def copia_modificada(tmp_path, cambiar, con_meta):
    """Copia cohorte_anima.csv a tmp_path aplicando `cambiar` a sus lineas."""
    if not COHORTE_REAL.exists():
        pytest.skip("cohorte_anima.csv no esta en el repo")
    lineas = COHORTE_REAL.read_text(encoding="utf-8").splitlines(keepends=True)
    ruta = tmp_path / "cohorte_anima.csv"
    ruta.write_text("".join(cambiar(lineas)), encoding="utf-8", newline="")
    if con_meta:
        shutil.copy(COHORTE_REAL.with_suffix(".meta.json"), tmp_path / "cohorte_anima.meta.json")
    return ruta


def test_rechaza_archivo_que_no_coincide_con_la_huella(tmp_path):
    # Cambia la edad del individuo 1 sin tocar los metadatos.
    ruta = copia_modificada(tmp_path, lambda l: [l[0], l[1].replace(",64,", ",65,")] + l[2:],
                            con_meta=True)
    with pytest.raises(AssertionError, match="huella"):
        leer_cohorte(ruta)


def test_rechaza_ids_repetidos(tmp_path):
    ruta = copia_modificada(tmp_path, lambda l: l[:-1] + [l[1]], con_meta=False)
    with pytest.raises(AssertionError, match="individuo_id"):
        leer_cohorte(ruta)


def test_rechaza_sexo_fuera_de_codificacion(tmp_path):
    ruta = copia_modificada(tmp_path, lambda l: [l[0], l[1].replace("CEU,0,", "CEU,2,")] + l[2:],
                            con_meta=False)
    with pytest.raises(AssertionError, match="sexo"):
        leer_cohorte(ruta)


def test_rechaza_columna_faltante(tmp_path):
    def sin_edad(lineas):
        return [",".join(c for i, c in enumerate(ln.rstrip("\n").split(",")) if i != 3) + "\n"
                for ln in lineas]
    ruta = copia_modificada(tmp_path, sin_edad, con_meta=False)
    with pytest.raises(KeyError):
        leer_cohorte(ruta)
