"""
Tests de poblacion.py: valores del brief, fuentes, pendientes y configuracion neutra.
"""

import math

import pytest

from tfc_voz.parametros import PARAMETROS
from tfc_voz.poblacion import (CAMPOS_CON_FUENTE, EFECTOS, SUBPOBLACIONES, TIPOS_FUENTE,
                               EfectosPoblacionales, configuracion_neutra, pendientes,
                               tipo_de_fuente)

# Tabla "Valores de poblacion.py" del brief del prototipo, copiada tal cual.
# nombre: (d, r, b_mujer, b_hombre, q_mujer, q_hombre, media_ref, desvio_ref, escala)
BRIEF = {
    "f0_medio": (-4.03, 1.41, -0.32, 0, 0.32, 0.40, 5.2829, 0.1195, "log"),
    "f0_variabilidad": (-0.75, 1.02, 0, 0, 0, 0, 2.1051, 0.5957, "log"),
    "f1": (-1.91, 0.94, -0.10, 0.02, 0, 0, 6.2925, 0.0890, "log"),
    "f2": (-2.53, 1.02, -0.14, -0.03, 0, 0, 7.3506, 0.0576, "log"),
    "f3": (-2.45, 0.99, 0.02, -0.03, 0, 0, 7.9880, 0.0480, "log"),
    "vtl": (3.38, 1.06, 0.04, -0.02, 0, 0, 2.6985, 0.0413, "log"),
    "jitter": (0.26, 0.54, 0.07, 0.06, 0, 0, -1.1825, 0.6135, "log"),
    "hnr": (-0.77, 0.87, 0, -0.06, 0, 0, 25.3, 3.1, "dB"),
}


# Media y DE de las mujeres en unidades fisicas, verificadas el 26/10 contra las
# tablas originales (Gisladottir S2_Means; Goy et al. 2013, tabla 3).
# nombre: (media, DE, tipo de la fuente de media_ref y desvio_ref)
REFERENCIAS_FISICAS = {
    "f0_medio": (198.3467, 23.79237, "derivado"),
    "f0_variabilidad": (9.801441, 6.397369, "derivado"),
    "f1": (542.6445, 48.37267, "derivado"),
    "f2": (1559.675, 89.84026, "derivado"),
    "f3": (2948.821, 141.7478, "derivado"),
    "vtl": (14.87063, 0.614681, "derivado"),
    "jitter": (0.37, 0.25, "derivado"),
    "hnr": (25.3, 3.1, "dato"),
}
# Goy redondea el jitter a dos decimales: 0,37 (0,25) %.
TOLERANCIA_REFERENCIA = {"jitter": 0.001}


@pytest.mark.parametrize("nombre", list(REFERENCIAS_FISICAS))
def test_referencias_recalculadas_desde_la_fuente(nombre):
    """media_ref y desvio_ref salen de la media y el DE fisicos por momentos lognormales."""
    media, de, tipo = REFERENCIAS_FISICAS[nombre]
    ef = EFECTOS[nombre]
    if ef.escala == "dB":
        esperado_media, esperado_desvio = media, de
    else:
        esperado_desvio = math.sqrt(math.log(1 + (de / media) ** 2))
        esperado_media = math.log(media) - esperado_desvio ** 2 / 2
    tolerancia = TOLERANCIA_REFERENCIA.get(nombre, 0.0001)
    assert abs(ef.media_ref - esperado_media) < tolerancia
    assert abs(ef.desvio_ref - esperado_desvio) < tolerancia
    for campo in ("media_ref", "desvio_ref"):
        assert tipo_de_fuente(ef.fuente[campo]) == tipo
        assert f"media {media} " in ef.fuente[campo] and f"DE {de} " in ef.fuente[campo]


def test_hay_efectos_para_los_8_parametros():
    assert set(EFECTOS) == {p.nombre for p in PARAMETROS}


@pytest.mark.parametrize("nombre", list(BRIEF))
def test_valores_del_brief(nombre):
    ef = EFECTOS[nombre]
    obtenido = (ef.d, ef.r, ef.b_mujer, ef.b_hombre, ef.q_mujer, ef.q_hombre,
                ef.media_ref, ef.desvio_ref, ef.escala)
    assert obtenido == BRIEF[nombre]


@pytest.mark.parametrize("nombre", list(EFECTOS))
def test_c_y_subpoblacion_en_cero_declarado(nombre):
    ef = EFECTOS[nombre]
    assert ef.c == 0 and tipo_de_fuente(ef.fuente["c"]) == "0 declarado"
    assert set(ef.a) == set(SUBPOBLACIONES) and all(v == 0 for v in ef.a.values())
    assert tipo_de_fuente(ef.fuente["a"]) == "0 declarado"


@pytest.mark.parametrize("nombre", list(EFECTOS))
def test_cada_valor_tiene_fuente_con_tipo(nombre):
    fuente = EFECTOS[nombre].fuente
    assert set(fuente) == set(CAMPOS_CON_FUENTE)
    for texto in fuente.values():
        assert tipo_de_fuente(texto) in TIPOS_FUENTE


def test_el_quiebre_a_los_60_solo_en_f0_medio():
    for nombre, ef in EFECTOS.items():
        if nombre != "f0_medio":
            assert ef.q_mujer == 0 and ef.q_hombre == 0, nombre


def test_no_hay_pendientes():
    assert pendientes() == []


def test_pendientes_lista_los_valores_pendientes():
    ef = EFECTOS["f1"]
    fuente = {**ef.fuente, "c": "PENDIENTE: falta la fuente"}
    falsos = {"f1": EfectosPoblacionales(**{**ef.__dict__, "fuente": fuente})}
    assert pendientes(falsos) == [("f1", "c", "PENDIENTE: falta la fuente")]


def test_fuente_sin_tipo_es_un_error():
    with pytest.raises(ValueError):
        tipo_de_fuente("Gisladottir 2023")


def test_configuracion_neutra():
    for ef in configuracion_neutra().values():
        assert (ef.d, ef.r, ef.b_mujer, ef.b_hombre, ef.q_mujer, ef.q_hombre, ef.c) == (0, 1, 0, 0, 0, 0, 0)
        assert all(v == 0 for v in ef.a.values())
