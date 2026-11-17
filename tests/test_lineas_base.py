"""
Tests de lineas_base.py (Etapa 3 del brief, con los ajustes del 29/10).

Los de recuperacion usan los valores de prueba de la Etapa 2 y 200.000
personas, ajustando sobre toda la muestra con ajustar_parametro. La semilla
es fija: si un test falla con ella, se diagnostica, no se cambia la semilla.
"""

import dataclasses

import numpy as np
import pytest

from tfc_voz import fenotipo, lineas_base
from tfc_voz.cohorte import generar_cohorte, leer_cohorte
from tfc_voz.fenotipo import generar_fenotipos
from tfc_voz.genotipo import SEMILLA
from tfc_voz.lineas_base import (ANCESTRIA_SEXO_EDAD, COMPLETO, MODELOS, SOLO_INTERCEPTO,
                                 ajustar_modelos, ajustar_parametro, columnas_de, matrices,
                                 predecir_modelos)
from tfc_voz.modelo import ErrorConvergencia
from tfc_voz.parametros import PARAMETROS
from tfc_voz.poblacion import EFECTOS, configuracion_neutra

N = 200_000
TOLERANCIA_MEDIA = 0.02       # d, b y b + q de la linea base 2 (como la Etapa 2)
TOLERANCIA_DISPERSION = 0.03  # log r y c
TOLERANCIA_ALFA0 = 0.02       # 1/2 log(1 - h2) del completo
# Tolerancias de los coeficientes de g: 4 desvios entre corridas, fijadas una
# vez el 17/11 (respuesta del 12/11, opcion a; las del brief, 0,02 y 0,03,
# quedaban a 1-2,8 desvios y fallaban por azar con un modelo correcto). No se
# recalculan: si el modelo cambia, se vuelven a medir y se declaran de nuevo.
#   g permutado, 40 permutaciones por parametro, desvio del coeficiente de g:
#     f0_medio 0,0106  f0_variabilidad 0,0188  jitter 0,0142  hnr 0,0140
#     f1 0,0131  f2 0,0115  f3 0,0113  vtl 0,0132  -> 4 x 0,0188 = 0,075
#   c = 0, 40 semillas de fenotipos (20261019 + 5000 + k), desvio de g / g*sexo:
#     f0_medio 0,0090/0,0130  f0_variabilidad 0,0138/0,0180  jitter 0,0132/0,0171
#     hnr 0,0129/0,0166  f1 0,0108/0,0143  f2 0,0075/0,0114  f3 0,0120/0,0166
#     vtl 0,0107/0,0137  -> g: 4 x 0,0138 = 0,055; g*sexo: 4 x 0,0180 = 0,072
# Una fuga de informacion pondria el coeficiente de g permutado cerca de 1:
# 0,075 sigue a mas de un factor de diez de la falla que el test busca.
TOLERANCIA_G = 0.055          # coeficiente de g con c = 0
TOLERANCIA_G_SEXO = 0.072     # coeficiente de g*sexo con c = 0
TOLERANCIA_PERMUTADO = 0.075

# Los valores de prueba de la Etapa 2, definidos solo en los tests.
VALORES_PRUEBA = dict(d=-2.0, r=0.8, c=0.1, b_mujer=-0.3, b_hombre=0.1, q_mujer=0.2, q_hombre=0.4)


def efectos(**cambios):
    valores = {**VALORES_PRUEBA, **cambios}
    return {n: dataclasses.replace(ef, **valores) for n, ef in configuracion_neutra().items()}


@pytest.fixture(scope="module")
def cohorte_grande():
    return generar_cohorte(n=N)


def ajustes_por_parametro(cohorte, fenotipos, columna_g="g", permutar=False):
    resultado = {}
    for p in PARAMETROS:
        y, g = columnas_de(fenotipos, p.nombre, cohorte, ["y", columna_g])
        if permutar:
            g = np.random.default_rng(SEMILLA).permutation(g)
        resultado[p.nombre] = ajustar_parametro(cohorte, y, g, p.nombre)
    return resultado


@pytest.fixture(scope="module")
def ajustes_prueba(cohorte_grande):
    """Los tres modelos de cada parametro con los valores de prueba (c = 0,1)."""
    fen = generar_fenotipos(cohorte_grande, PARAMETROS, efectos(), SEMILLA)
    return ajustes_por_parametro(cohorte_grande, fen)


@pytest.fixture(scope="module")
def ajustes_c0(cohorte_grande):
    """Los mismos valores de prueba con c = 0: la media del completo es exacta."""
    fen = generar_fenotipos(cohorte_grande, PARAMETROS, efectos(c=0.0), SEMILLA)
    return ajustes_por_parametro(cohorte_grande, fen)


@pytest.fixture(scope="module")
def ajustes_permutados(cohorte_grande):
    fen = generar_fenotipos(cohorte_grande, PARAMETROS, efectos(), SEMILLA)
    return ajustes_por_parametro(cohorte_grande, fen, permutar=True)


def efectos_de_media(beta):
    """d, b y b + q de cada sexo, desde los coeficientes de la linea base 2.

    Columnas: 1, sexo, edad_c, sexo*edad_c, tramo60, sexo*tramo60, dummies.
    """
    return {
        "d": beta[1],
        "b_mujer": beta[2],
        "b_hombre": beta[2] + beta[3],
        "b+q_mujer": beta[2] + beta[4],
        "b+q_hombre": beta[2] + beta[3] + beta[4] + beta[5],
    }


ESPERADO_MEDIA = {
    "d": VALORES_PRUEBA["d"],
    "b_mujer": VALORES_PRUEBA["b_mujer"],
    "b_hombre": VALORES_PRUEBA["b_hombre"],
    "b+q_mujer": VALORES_PRUEBA["b_mujer"] + VALORES_PRUEBA["q_mujer"],
    "b+q_hombre": VALORES_PRUEBA["b_hombre"] + VALORES_PRUEBA["q_hombre"],
}


# --- Linea base 2 (ajustes del 29/10) -----------------------------------------

@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
@pytest.mark.parametrize("efecto", list(ESPERADO_MEDIA))
def test_linea_base_2_recupera_los_efectos_de_media(ajustes_prueba, p, efecto):
    estimado = efectos_de_media(ajustes_prueba[p.nombre][ANCESTRIA_SEXO_EDAD].beta)
    assert abs(estimado[efecto] - ESPERADO_MEDIA[efecto]) < TOLERANCIA_MEDIA


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_linea_base_2_recupera_la_dispersion(ajustes_prueba, p):
    """log r para el sexo, c para la edad y 0 para la constante: la varianza de g + e es 1."""
    alfa = ajustes_prueba[p.nombre][ANCESTRIA_SEXO_EDAD].alfa
    assert abs(alfa[0]) < TOLERANCIA_DISPERSION
    assert abs(alfa[1] - np.log(VALORES_PRUEBA["r"])) < TOLERANCIA_DISPERSION
    assert abs(alfa[2] - VALORES_PRUEBA["c"]) < TOLERANCIA_DISPERSION


# --- Modelo completo (Etapa 3) -----------------------------------------------

@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_completo_recupera_la_dispersion(ajustes_prueba, p):
    """alfa de sexo = log r, de edad = c y alfa_0 = 1/2 log(1 - h2)."""
    alfa = ajustes_prueba[p.nombre][COMPLETO].alfa
    assert abs(alfa[1] - np.log(VALORES_PRUEBA["r"])) < TOLERANCIA_DISPERSION
    assert abs(alfa[2] - VALORES_PRUEBA["c"]) < TOLERANCIA_DISPERSION
    assert abs(alfa[0] - 0.5 * np.log(1 - p.heredabilidad)) < TOLERANCIA_ALFA0


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_completo_con_c_0_recupera_g_y_g_por_sexo(ajustes_c0, p):
    """Con c = 0, mu = m + g + (r - 1) * sexo * g: el coeficiente de g da 1 y el de g*sexo, r - 1."""
    beta = ajustes_c0[p.nombre][COMPLETO].beta
    g, g_sexo = beta[-3], beta[-2]
    assert abs(g - 1.0) < TOLERANCIA_G
    assert abs(g_sexo - (VALORES_PRUEBA["r"] - 1.0)) < TOLERANCIA_G_SEXO


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
def test_g_permutado_anula_el_coeficiente_de_g(ajustes_permutados, p):
    assert abs(ajustes_permutados[p.nombre][COMPLETO].beta[-3]) < TOLERANCIA_PERMUTADO


# --- Forma de los modelos -----------------------------------------------------

def test_definiciones_compartidas_con_fenotipo():
    """edad_c y tramo60 son las de fenotipo.py, no una copia."""
    assert lineas_base.edad_centrada is fenotipo.edad_centrada
    assert lineas_base.tramo60 is fenotipo.tramo60


def test_columnas_de_cada_modelo():
    cohorte = generar_cohorte()
    g = np.arange(len(cohorte), dtype=float)
    formas = {m: tuple(X.shape[1] for X in matrices(m, cohorte, g)) for m in MODELOS}
    assert formas == {SOLO_INTERCEPTO: (1, 1), ANCESTRIA_SEXO_EDAD: (10, 3), COMPLETO: (13, 3)}
    X_mu, _ = matrices(COMPLETO, cohorte, g)
    ceu = (cohorte["subpoblacion"] == "CEU").to_numpy()
    assert np.all(X_mu[ceu, 6:10] == 0)                      # CEU es la referencia
    assert np.all(X_mu[~ceu, 6:10].sum(axis=1) == 1)
    assert np.array_equal(X_mu[:, 10], g)


def test_el_completo_exige_g():
    with pytest.raises(ValueError, match="puntaje genetico"):
        matrices(COMPLETO, generar_cohorte())


def test_los_nombres_de_las_lineas_base_son_los_del_paquete():
    from anima_spine import predictions
    assert (SOLO_INTERCEPTO, ANCESTRIA_SEXO_EDAD) == tuple(predictions.LINEAS_BASE)


# --- Sobre la cohorte compartida, con los efectos reales ----------------------

@pytest.fixture(scope="module")
def cohorte_real():
    from pathlib import Path
    ruta = Path(__file__).resolve().parents[1] / "cohorte_anima.csv"
    if not ruta.exists():
        pytest.skip("cohorte_anima.csv no esta en el repo")
    return leer_cohorte(ruta)


def test_ajusta_solo_con_entrenamiento(cohorte_real):
    """Cambiar y o g fuera de entrenamiento no cambia ningun ajuste."""
    fen = generar_fenotipos(cohorte_real, PARAMETROS[:2], EFECTOS, SEMILLA)
    otro = fen.copy()
    fuera = ~otro["individuo_id"].isin(cohorte_real.loc[cohorte_real["particion"] == "entrenamiento",
                                                        "individuo_id"])
    otro.loc[fuera, ["y", "g"]] = 99.0
    a, b = (ajustar_modelos(cohorte_real, f, PARAMETROS[:2]) for f in (fen, otro))
    for rasgo in a:
        for modelo in MODELOS:
            assert np.array_equal(a[rasgo][modelo].beta, b[rasgo][modelo].beta)


def test_convergen_los_24_modelos_con_los_efectos_reales(cohorte_real):
    fen = generar_fenotipos(cohorte_real, PARAMETROS, EFECTOS, SEMILLA)
    ajustes = ajustar_modelos(cohorte_real, fen, PARAMETROS)
    assert set(ajustes) == {p.nombre for p in PARAMETROS}
    assert all(set(a) == set(MODELOS) for a in ajustes.values())
    prueba = cohorte_real[cohorte_real["particion"] == "prueba"]
    for p in PARAMETROS:
        (g,) = columnas_de(fen, p.nombre, prueba, ["g"])
        for mu, sigma in predecir_modelos(ajustes[p.nombre], prueba, g).values():
            assert len(mu) == len(sigma) == 500 and np.all(sigma > 0) and np.all(np.isfinite(mu))


def test_sin_convergencia_el_error_nombra_parametro_y_modelo(cohorte_real, monkeypatch):
    def no_converge(*args, **kwargs):
        raise ErrorConvergencia("L-BFGS-B no convergio en 15000 iteraciones: ABNORMAL")
    monkeypatch.setattr(lineas_base, "ajustar", no_converge)
    fen = generar_fenotipos(cohorte_real, PARAMETROS[:1], EFECTOS, SEMILLA)
    with pytest.raises(ErrorConvergencia, match="parametro f0_medio, modelo 'solo intercepto': L-BFGS-B"):
        ajustar_modelos(cohorte_real, fen, PARAMETROS[:1])


def test_columna_g_elige_el_puntaje_del_completo(cohorte_real):
    """El segundo nivel le pasa al completo otra columna (la parte conocida de g).

    Con el doble de g, el coeficiente de g tiene que dar la mitad. La mitad es
    exacta en el optimo; L-BFGS-B se detiene antes, con un error relativo de
    2e-4 en este caso (con ftol = 1e-15 da 6e-8), asi que se pide 1e-3.
    """
    fen = generar_fenotipos(cohorte_real, PARAMETROS[:1], EFECTOS, SEMILLA)
    doble = ajustar_modelos(cohorte_real, fen.assign(g_doble=2 * fen["g"]), PARAMETROS[:1], columna_g="g_doble")
    normal = ajustar_modelos(cohorte_real, fen, PARAMETROS[:1])
    assert doble["f0_medio"][COMPLETO].beta[-3] == pytest.approx(normal["f0_medio"][COMPLETO].beta[-3] / 2,
                                                                  rel=1e-3)
