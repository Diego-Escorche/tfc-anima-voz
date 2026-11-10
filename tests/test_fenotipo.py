"""
Tests de fenotipo.py (Etapa 2 del brief del prototipo).

"A edad fija" se mide con toda la muestra, descontando la edad con la forma del
modelo, y no solo con las personas de una misma edad: con la lectura literal,
un generador correcto fallaba el test de d el 52 % de las veces (decision del
23/10, informes/propuesta-tests-edad-fija.md). r y c se estiman de los
residuos sin usar el c verdadero.

La semilla es fija. Si un test falla con ella, se diagnostica: no se cambia la
semilla para que pase.
"""

import dataclasses

import numpy as np
import pytest

from tfc_voz.cohorte import generar_cohorte
from tfc_voz.fenotipo import (INDICE_SEMILLA, edad_centrada, generar_fenotipos,
                              media_y_escala, oraculo, tramo60)
from tfc_voz.genotipo import SEMILLA
from tfc_voz.parametros import PARAMETROS
from tfc_voz.poblacion import configuracion_neutra

N = 200_000
TOLERANCIA_H2 = 0.01
TOLERANCIA_EFECTOS = 0.02

# Valores de prueba, definidos solo aca (no son los de poblacion.py).
# q_mujer distinto de 0 para que el quiebre de las mujeres tambien se pruebe.
VALORES_PRUEBA = dict(d=-2.0, r=0.8, c=0.1, b_mujer=-0.3, b_hombre=0.1, q_mujer=0.2, q_hombre=0.4)

# Lo que cada estimacion tiene que recuperar.
ESPERADO = {
    "d": VALORES_PRUEBA["d"],
    "b_mujer": VALORES_PRUEBA["b_mujer"],
    "b_hombre": VALORES_PRUEBA["b_hombre"],
    "b+q_mujer": VALORES_PRUEBA["b_mujer"] + VALORES_PRUEBA["q_mujer"],
    "b+q_hombre": VALORES_PRUEBA["b_hombre"] + VALORES_PRUEBA["q_hombre"],
    "r": VALORES_PRUEBA["r"],
    "c": VALORES_PRUEBA["c"],
}


def efectos_de_prueba():
    return {n: dataclasses.replace(ef, **VALORES_PRUEBA) for n, ef in configuracion_neutra().items()}


def estimar_efectos(y, sexo, edad):
    """d, pendientes, r y c estimados de los datos, sin usar los valores verdaderos.

    Media: minimos cuadrados de y sobre [1, sexo, edad_c(1-sexo), edad_c*sexo,
    tramo60(1-sexo), tramo60*sexo]. El coeficiente de sexo es la diferencia a
    los 49 anios (edad_c = 0, tramo60 = 0), es decir, a edad fija.
    Dispersion: minimos cuadrados de log|residuo| sobre [1, sexo, edad_c].
    log|residuo| = log s + log|z|; el promedio de log|z| es constante, asi que
    las pendientes dan log r y c.
    """
    sexo = np.asarray(sexo, dtype=float)
    ec, tr = edad_centrada(edad), tramo60(edad)
    uno = np.ones_like(sexo)
    X = np.column_stack([uno, sexo, ec * (1 - sexo), ec * sexo, tr * (1 - sexo), tr * sexo])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    residuo = y - X @ beta
    Z = np.column_stack([uno, sexo, ec])
    gamma, *_ = np.linalg.lstsq(Z, np.log(np.abs(residuo)), rcond=None)
    return {
        "d": beta[1],
        "b_mujer": beta[2],
        "b_hombre": beta[3],
        "b+q_mujer": beta[2] + beta[4],
        "b+q_hombre": beta[3] + beta[5],
        "r": float(np.exp(gamma[1])),
        "c": gamma[2],
    }


@pytest.fixture(scope="module")
def cohorte_grande():
    return generar_cohorte(n=N)


@pytest.fixture(scope="module")
def fenotipos(cohorte_grande):
    return generar_fenotipos(cohorte_grande, PARAMETROS, efectos_de_prueba(), SEMILLA)


def columna(fenotipos, rasgo, campo):
    """Una columna de un rasgo, en el orden de la cohorte."""
    return fenotipos.loc[fenotipos["rasgo"] == rasgo, campo].to_numpy()


def test_formato_largo(cohorte_grande, fenotipos):
    assert list(fenotipos.columns) == ["individuo_id", "rasgo", "g", "g_conocida", "e", "y"]
    assert len(fenotipos) == N * len(PARAMETROS)
    for p in PARAMETROS:
        assert np.array_equal(columna(fenotipos, p.nombre, "individuo_id"),
                              cohorte_grande["individuo_id"].to_numpy())


def r2_dentro_de_sexo(cohorte, fenotipos, p, sexo, g=None):
    """R2 de (y - m) / s explicado por g, en las personas de un sexo.

    g: el puntaje genetico a usar; por defecto, el de los fenotipos (VZ-05 pasa uno mezclado).
    """
    ef = efectos_de_prueba()[p.nombre]
    m, s = media_y_escala(ef, cohorte["sexo"].to_numpy(), cohorte["edad"].to_numpy(),
                          cohorte["subpoblacion"].to_numpy())
    z = (columna(fenotipos, p.nombre, "y") - m) / s
    g = columna(fenotipos, p.nombre, "g") if g is None else g
    del_sexo = cohorte["sexo"].to_numpy() == sexo
    return float(np.corrcoef(g[del_sexo], z[del_sexo])[0, 1] ** 2)


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
@pytest.mark.parametrize("sexo", [0, 1], ids=["mujeres", "hombres"])
def test_vz01_04_h2_dentro_de_cada_sexo(cohorte_grande, fenotipos, p, sexo):
    """VZ-01 a VZ-04: el R2 de (y - m) / s explicado por g queda a menos de 0,01 de la h2."""
    r2 = r2_dentro_de_sexo(cohorte_grande, fenotipos, p, sexo)
    assert abs(r2 - p.heredabilidad) < TOLERANCIA_H2


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
@pytest.mark.parametrize("sexo", [0, 1], ids=["mujeres", "hombres"])
def test_vz05_permutacion_anula_la_senal(cohorte_grande, fenotipos, p, sexo):
    """VZ-05: con g mezclado al azar entre personas, el R2 cae por debajo de 0,005."""
    g_mezclado = np.random.default_rng(SEMILLA).permutation(columna(fenotipos, p.nombre, "g"))
    assert r2_dentro_de_sexo(cohorte_grande, fenotipos, p, sexo, g=g_mezclado) < 0.005


@pytest.mark.lento
@pytest.mark.parametrize("replica", range(20))
def test_vz07_estabilidad_entre_semillas(cohorte_grande, replica):
    """VZ-07: VZ-01 a VZ-04 pasan en los 8 parametros y ambos sexos con las 20 semillas
    del barrido, 20261019 + r con r de 0 a 19."""
    fen = generar_fenotipos(cohorte_grande, PARAMETROS, efectos_de_prueba(), SEMILLA + replica)
    for p in PARAMETROS:
        for sexo in (0, 1):
            r2 = r2_dentro_de_sexo(cohorte_grande, fen, p, sexo)
            assert abs(r2 - p.heredabilidad) < TOLERANCIA_H2, (p.nombre, sexo)


@pytest.mark.parametrize("p", PARAMETROS, ids=lambda p: p.nombre)
@pytest.mark.parametrize("efecto", list(ESPERADO))
def test_efectos_a_edad_fija(cohorte_grande, fenotipos, p, efecto):
    """d, r, c y las pendientes de edad (b antes de los 60, b + q despues), a menos de 0,02."""
    estimado = estimar_efectos(columna(fenotipos, p.nombre, "y"), cohorte_grande["sexo"].to_numpy(),
                               cohorte_grande["edad"].to_numpy())
    assert abs(estimado[efecto] - ESPERADO[efecto]) < TOLERANCIA_EFECTOS


def test_misma_semilla_mismo_resultado():
    cohorte = generar_cohorte()
    a = generar_fenotipos(cohorte, PARAMETROS, efectos_de_prueba(), SEMILLA)
    b = generar_fenotipos(cohorte, PARAMETROS, efectos_de_prueba(), SEMILLA)
    assert a.equals(b)


def test_agregar_o_reordenar_parametros_no_cambia_los_demas():
    cohorte = generar_cohorte()
    todos = generar_fenotipos(cohorte, PARAMETROS, efectos_de_prueba(), SEMILLA)
    por_nombre = {p.nombre: p for p in PARAMETROS}
    algunos = generar_fenotipos(cohorte, [por_nombre["vtl"], por_nombre["jitter"]],
                                efectos_de_prueba(), SEMILLA)
    for rasgo in ("vtl", "jitter"):
        assert todos[todos["rasgo"] == rasgo].reset_index(drop=True).equals(
            algunos[algunos["rasgo"] == rasgo].reset_index(drop=True))


def test_configuracion_neutra_da_g_mas_e_exacto():
    fen = generar_fenotipos(generar_cohorte(), PARAMETROS, configuracion_neutra(), SEMILLA)
    assert np.array_equal(fen["y"].to_numpy(), (fen["g"] + fen["e"]).to_numpy())


def test_efecto_de_subpoblacion():
    cohorte = generar_cohorte()
    a = {"CEU": 0.0, "GBR": 0.1, "FIN": 0.5, "IBS": -0.3, "TSI": 0.0}
    efectos = {n: dataclasses.replace(ef, a=a) for n, ef in configuracion_neutra().items()}
    fen = generar_fenotipos(cohorte, PARAMETROS[:1], efectos, SEMILLA)
    esperado = cohorte["subpoblacion"].map(a).to_numpy()
    assert np.allclose(fen["y"] - fen["g"] - fen["e"], esperado, atol=1e-12)


def test_parametro_sin_indice_de_semilla_es_un_error():
    nuevo = dataclasses.replace(PARAMETROS[0], nombre="shimmer")
    with pytest.raises(KeyError, match="INDICE_SEMILLA"):
        generar_fenotipos(generar_cohorte(), [nuevo], {"shimmer": configuracion_neutra()["f0_medio"]},
                          SEMILLA)


def test_indices_de_semilla_fijos_y_distintos():
    assert set(INDICE_SEMILLA) == {p.nombre for p in PARAMETROS}
    assert len(set(INDICE_SEMILLA.values())) == len(INDICE_SEMILLA)


def test_oraculo_deja_solo_el_ruido_ambiental(cohorte_grande, fenotipos):
    """(y - mu_oraculo) / sigma_oraculo = e / sqrt(1 - h2), exacto, en cada parametro."""
    orac = oraculo(cohorte_grande, fenotipos, PARAMETROS, efectos_de_prueba())
    assert list(orac.columns) == ["individuo_id", "rasgo", "mu_oraculo", "sigma_oraculo"]
    assert orac[["individuo_id", "rasgo"]].equals(fenotipos[["individuo_id", "rasgo"]])
    for p in PARAMETROS:
        o = orac[orac["rasgo"] == p.nombre]
        z = (columna(fenotipos, p.nombre, "y") - o["mu_oraculo"].to_numpy()) / o["sigma_oraculo"].to_numpy()
        assert np.allclose(z, columna(fenotipos, p.nombre, "e") / np.sqrt(1 - p.heredabilidad), atol=1e-9)


def test_oraculo_rechaza_fenotipos_fuera_de_orden():
    cohorte = generar_cohorte()
    fen = generar_fenotipos(cohorte, PARAMETROS[:1], configuracion_neutra(), SEMILLA)
    with pytest.raises(ValueError, match="orden de la cohorte"):
        oraculo(cohorte, fen.iloc[::-1], PARAMETROS[:1], configuracion_neutra())
