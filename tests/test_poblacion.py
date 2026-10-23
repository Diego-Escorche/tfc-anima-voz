"""
Tests de poblacion.py: valores del brief, fuentes, pendientes y configuracion neutra.
"""

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
