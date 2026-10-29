"""
Tests de salida.py con filas sinteticas armadas aca, sobre los ids de prueba
de la cohorte real. No usan el modelo: prueban el formato y la validacion.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from anima_spine import predictions
from tfc_voz.cohorte import leer_cohorte
from tfc_voz.genotipo import SEMILLA
from tfc_voz.parametros import PARAMETROS
from tfc_voz.salida import escribir_barrido, escribir_intervalos, escribir_predicciones

RAIZ = Path(__file__).resolve().parents[1]
RASGOS = [p.nombre for p in PARAMETROS]


@pytest.fixture(scope="module")
def cohorte():
    if not (RAIZ / "cohorte_anima.csv").exists():
        pytest.skip("cohorte_anima.csv no esta en el repo")
    return leer_cohorte(RAIZ / "cohorte_anima.csv")


@pytest.fixture(scope="module")
def sinteticos(cohorte):
    """Predicciones, intervalos y barrido coherentes entre si, armados a mano."""
    rng = np.random.default_rng(SEMILLA)
    ids = cohorte.loc[cohorte["particion"] == "prueba", "individuo_id"].to_numpy()
    filas_pred, filas_int, filas_bar = [], [], []
    for rasgo in RASGOS:
        n = len(ids)
        y, mu = rng.normal(size=n), rng.normal(size=n)
        sigma = rng.uniform(0.5, 1.5, n)
        intervalos = {nivel: (mu - norm.ppf((1 + nivel) / 2) * sigma, mu + norm.ppf((1 + nivel) / 2) * sigma)
                      for nivel in predictions.NIVELES}
        lo90, hi90 = intervalos[predictions.NIVEL_PRINCIPAL]
        for base in predictions.LINEAS_BASE:
            filas_pred.append(pd.DataFrame({
                "individuo_id": ids, "dominio": "voz", "rasgo": rasgo, "y_real": y, "mu": mu,
                "sigma": sigma, "lo": lo90, "hi": hi90, "mu_base": rng.normal(size=n),
                "sigma_base": rng.uniform(0.8, 2.0, n), "linea_base": base}))
        for nivel, (lo, hi) in intervalos.items():
            filas_int.append(pd.DataFrame({"individuo_id": ids, "dominio": "voz", "rasgo": rasgo,
                                           "nivel": nivel, "lo": lo, "hi": hi}))
            for replica in range(predictions.REPLICAS):
                filas_bar.append(predictions.fila_barrido(replica, SEMILLA + replica, "voz", rasgo,
                                                          nivel, y, lo, hi))
    return (pd.concat(filas_pred, ignore_index=True)[list(predictions.CAMPOS)],
            pd.concat(filas_int, ignore_index=True)[list(predictions.CAMPOS_INTERVALOS)],
            pd.DataFrame(filas_bar)[list(predictions.CAMPOS_BARRIDO)])


def test_los_tres_archivos_pasan_y_se_escriben(sinteticos, cohorte, tmp_path):
    pred, inter, barrido = sinteticos
    ruta_pred = escribir_predicciones(pred, cohorte, tmp_path, rasgos=RASGOS)
    ruta_int = escribir_intervalos(inter, pred, cohorte, tmp_path)
    ruta_bar = escribir_barrido(barrido, inter, pred, cohorte, tmp_path)
    assert ruta_pred.name == "predicciones_voz.csv" and len(predictions.cargar(ruta_pred)) == 8000
    assert ruta_int.name == "intervalos_voz.csv"
    assert len(predictions.cargar_intervalos(ruta_int)) == 500 * 8 * len(predictions.NIVELES)
    assert ruta_bar.name == "barrido_voz.csv"
    assert len(predictions.cargar_barrido(ruta_bar)) == predictions.REPLICAS * 8 * len(predictions.NIVELES)


def test_rechaza_fila_duplicada(sinteticos, cohorte, tmp_path):
    pred = sinteticos[0]
    malo = pd.concat([pred, pred.iloc[[0]]], ignore_index=True)
    with pytest.raises(AssertionError, match="repetido"):
        escribir_predicciones(malo, cohorte, tmp_path)
    assert not (tmp_path / "predicciones_voz.csv").exists()


def test_rechaza_nivel_faltante(sinteticos, cohorte, tmp_path):
    pred, inter, _ = sinteticos
    malo = inter[inter["nivel"] != 0.95].reset_index(drop=True)
    with pytest.raises(AssertionError, match="niveles"):
        escribir_intervalos(malo, pred, cohorte, tmp_path)
    assert not (tmp_path / "intervalos_voz.csv").exists()


def test_rechaza_19_replicas(sinteticos, cohorte, tmp_path):
    pred, inter, barrido = sinteticos
    malo = barrido[barrido["replica"] != predictions.REPLICAS - 1].reset_index(drop=True)
    with pytest.raises(AssertionError, match="réplicas"):
        escribir_barrido(malo, inter, pred, cohorte, tmp_path)
    assert not (tmp_path / "barrido_voz.csv").exists()


def test_rechaza_una_linea_base_faltante(sinteticos, cohorte, tmp_path):
    pred = sinteticos[0]
    malo = pred[~((pred["rasgo"] == "f1") & (pred["linea_base"] == "solo intercepto"))]
    with pytest.raises(AssertionError, match="dos lineas base"):
        escribir_predicciones(malo.reset_index(drop=True), cohorte, tmp_path)


def test_rechaza_ids_fuera_de_prueba(sinteticos, cohorte, tmp_path):
    pred = sinteticos[0].copy()
    pred.loc[0, "individuo_id"] = int(cohorte.loc[cohorte["particion"] == "entrenamiento", "individuo_id"].iloc[0])
    with pytest.raises(AssertionError, match="partición de\\s+prueba"):
        escribir_predicciones(pred, cohorte, tmp_path)


def test_rechaza_columnas_fuera_de_orden(sinteticos, cohorte, tmp_path):
    pred = sinteticos[0]
    with pytest.raises(AssertionError, match="columnas"):
        escribir_predicciones(pred[list(predictions.CAMPOS)[::-1]], cohorte, tmp_path)


def test_rechaza_rasgos_distintos_de_los_pedidos(sinteticos, cohorte, tmp_path):
    pred = sinteticos[0]
    with pytest.raises(AssertionError, match="rasgos"):
        escribir_predicciones(pred[pred["rasgo"] != "vtl"].reset_index(drop=True), cohorte, tmp_path,
                              rasgos=RASGOS)
