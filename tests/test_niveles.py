"""
Tests de niveles.py y de la regla de la entrega del 9/11: los ocho h2 viven
en un unico archivo de datos, config/niveles_declarados.json.
"""

import io
import json
import tokenize
from decimal import Decimal
from pathlib import Path

import pytest

from tfc_voz.niveles import RUTA, cargar
from tfc_voz.parametros import PARAMETROS

RAIZ = Path(__file__).resolve().parents[1]
# Los .py del modulo: el paquete, los scripts y el generador del informe. Los
# tests quedan afuera porque usan tolerancias (0,05) que coinciden como texto
# con el h2 de jitter y hnr.
CARPETAS_DEL_MODULO = ("src/tfc_voz", "scripts", "informes")


@pytest.fixture(scope="module")
def niveles():
    return cargar()


def _normalizado(texto):
    """Texto de un numero en forma canonica: '0.0500', '.05' y '5e-2' dan '0.05'."""
    return format(Decimal(texto).normalize(), "f")


def literales_numericos(ruta):
    """(linea, texto) de cada literal numerico del codigo, sin comentarios ni strings."""
    fuente = ruta.read_text(encoding="utf-8")
    for tok in tokenize.generate_tokens(io.StringIO(fuente).readline):
        if tok.type == tokenize.NUMBER and not tok.string.lower().endswith("j"):
            yield tok.start[0], tok.string.replace("_", "")


def test_ningun_py_escribe_un_nivel_a_mano():
    """Falla si alguno de los niveles (distintos de cero) aparece como literal en un .py del modulo.

    Compara textos normalizados, no flotantes: 0.1027 salta aunque este escrito
    .1027 o 0.10270. Los ceros del segundo nivel no se buscan: 0.0 esta en todos lados.
    """
    datos = json.loads(RUTA.read_text(encoding="utf-8"))
    buscados = {_normalizado(repr(v)) for nivel in datos["niveles"].values() for v in nivel.values() if v}
    assert len(buscados) == 10  # 7 distintos del caso base (jitter y hnr comparten 0.05) + 3 del segundo
    encontrados = []
    for carpeta in CARPETAS_DEL_MODULO:
        for ruta in sorted((RAIZ / carpeta).glob("*.py")):
            for linea, texto in literales_numericos(ruta):
                if "." in texto or "e" in texto.lower():
                    if _normalizado(texto) in buscados:
                        encontrados.append(f"{ruta.relative_to(RAIZ)}:{linea}: {texto}")
    assert not encontrados, "niveles escritos a mano:\n" + "\n".join(encontrados)


def test_el_buscador_detecta_un_literal(tmp_path):
    """Control del test anterior: un archivo con .1027 escrito a mano se detecta."""
    ruta = tmp_path / "malo.py"
    ruta.write_text("h2 = .1027  # 0.1353 en un comentario no cuenta\ns = '0.0619'\n", encoding="utf-8")
    assert [(1, ".1027")] == [(l, t) for l, t in literales_numericos(ruta)]
    assert _normalizado(".1027") == _normalizado(repr(0.1027)) == "0.1027"
    assert _normalizado("0.0500") == _normalizado("5e-2") == "0.05"


def test_parametros_usa_el_caso_base(niveles):
    assert [p.nombre for p in PARAMETROS] == niveles.parametros
    assert {p.nombre: p.heredabilidad for p in PARAMETROS} == niveles.de("caso_base")


def test_agregados(niveles):
    """Caso base 7,07 % (el 7,1 % de los documentos) y segundo nivel 0,148 %."""
    assert niveles.agregado("caso_base") == pytest.approx(0.070737, abs=1e-6)
    assert niveles.agregado("segundo_nivel") == pytest.approx(0.001480, abs=1e-6)


def test_segundo_nivel_es_2pq_beta2(niveles):
    """El segundo nivel es por parametro, no 0,15 % en cada uno: solo f0_medio, f2 y f1."""
    v = niveles.varianza_conocida()
    assert v["f0_medio"] == pytest.approx(0.006160, abs=1e-6)
    assert v["f2"] == pytest.approx(0.003433, abs=1e-6)
    assert v["f1"] == pytest.approx(0.002247, abs=1e-6)
    assert [n for n, x in v.items() if x == 0] == ["f0_variabilidad", "jitter", "hnr", "f3", "vtl"]


def test_describir_dice_nivel_archivo_version_y_fecha(niveles):
    texto = niveles.describir("segundo_nivel")
    for parte in ("segundo_nivel", "niveles_declarados.json", "version 1.0", "2026-11-09", "Tabla S8"):
        assert parte in texto


# --- El cargador rechaza archivos que no cierran -----------------------------

def _copia(tmp_path, cambiar):
    datos = json.loads(RUTA.read_text(encoding="utf-8"))
    cambiar(datos)
    ruta = tmp_path / "niveles_declarados.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def test_rechaza_agregado_que_no_cierra(tmp_path):
    def cambiar(d):
        d["niveles"]["caso_base"]["f3"] = 0.07
    with pytest.raises(ValueError, match="agregado"):
        cargar(_copia(tmp_path, cambiar))


def test_rechaza_parametro_faltante(tmp_path):
    def cambiar(d):
        del d["niveles"]["segundo_nivel"]["vtl"]
    with pytest.raises(ValueError, match="parametros"):
        cargar(_copia(tmp_path, cambiar))


def test_rechaza_segundo_nivel_distinto_de_2pq_beta2(tmp_path):
    def cambiar(d):
        d["variantes"][0]["beta"] = 0.2
    with pytest.raises(ValueError, match="2pq"):
        cargar(_copia(tmp_path, cambiar))


def test_rechaza_varianza_conocida_mayor_que_h2(tmp_path):
    def cambiar(d):
        d["niveles"]["caso_base"]["f1"] = 0.002
        d["niveles"]["caso_base"]["f3"] += 0.0619 - 0.002  # mantiene el agregado
    with pytest.raises(ValueError, match="supera la h2"):
        cargar(_copia(tmp_path, cambiar))
