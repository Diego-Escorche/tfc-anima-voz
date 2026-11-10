"""
Tests de niveles.py y de la regla de la entrega del 9/11: los ocho h2 viven
en un unico archivo de datos, config/niveles_declarados.json.
"""

import io
import json
import re
import tokenize
from decimal import Decimal
from pathlib import Path

import pytest

from tfc_voz.cohorte import generar_cohorte, leer_cohorte
from tfc_voz.niveles import RUTA, RUTA_COHORTE, cargar, composicion_de
from tfc_voz.parametros import PARAMETROS

RAIZ = Path(__file__).resolve().parents[1]
# Los .py del modulo, tests incluidos: un test que escribe un nivel a mano
# pasaria aunque la configuracion cambie.
CARPETAS_DEL_MODULO = ("src/tfc_voz", "scripts", "informes", "tests")
# Una linea con un nivel escrito a proposito se saltea si termina con esta
# anotacion y un motivo.
EXENCION = re.compile(r"#\s*nivel-literal-ok:\s*\S")


@pytest.fixture(scope="module")
def niveles():
    return cargar()


@pytest.fixture(scope="module")
def json_niveles():
    return json.loads(RUTA.read_text(encoding="utf-8"))


def _normalizado(texto):
    """Texto de un numero en forma canonica: '0.0500', '.05' y '5e-2' dan '0.05'."""
    return format(Decimal(texto).normalize(), "f")


def literales_numericos(ruta):
    """(linea, texto) de cada literal numerico decimal del codigo, salvo en lineas exentas.

    tokenize da tokens completos: 0.05 no aparece dentro de 0.057, y los
    numeros dentro de strings o comentarios no cuentan.
    """
    fuente = ruta.read_text(encoding="utf-8")
    tokens = list(tokenize.generate_tokens(io.StringIO(fuente).readline))
    exentas = {t.start[0] for t in tokens if t.type == tokenize.COMMENT and EXENCION.search(t.string)}
    for tok in tokens:
        texto = tok.string.replace("_", "")
        if (tok.type == tokenize.NUMBER and tok.start[0] not in exentas
                and not texto.lower().endswith("j") and ("." in texto or "e" in texto.lower())):
            yield tok.start[0], texto


def niveles_buscados(json_niveles):
    """Los valores distintos de cero de los dos niveles, normalizados.

    Los ceros del segundo nivel no se buscan: 0.0 esta en todos lados, y el
    control del agregado ya los cubre.
    """
    return {_normalizado(repr(v)) for nivel in json_niveles["niveles"].values()
            for v in nivel.values() if v}


def test_ningun_py_escribe_un_nivel_a_mano(json_niveles):
    """Falla si un nivel aparece como literal en un .py del modulo, fuera de una linea exenta."""
    buscados = niveles_buscados(json_niveles)
    assert len(buscados) == 10  # 7 distintos del caso base (jitter y hnr comparten 0.05) + 3 del segundo
    encontrados = [f"{ruta.relative_to(RAIZ)}:{linea}: {texto}"
                   for carpeta in CARPETAS_DEL_MODULO
                   for ruta in sorted((RAIZ / carpeta).glob("*.py"))
                   for linea, texto in literales_numericos(ruta)
                   if _normalizado(texto) in buscados]
    assert not encontrados, "niveles escritos a mano:\n" + "\n".join(encontrados)


def test_el_buscador_detecta_un_literal_y_respeta_la_exencion(tmp_path, json_niveles):
    """Control del test anterior, sobre un archivo armado a proposito."""
    ruta = tmp_path / "malo.py"
    ruta.write_text(
        "h2 = .1027  # 0.1353 en un comentario no cuenta\n"
        "s = '0.0619'\n"
        "tolerancia = 0.057\n"
        "x = 0.0500  # nivel-literal-ok: tolerancia, coincide por casualidad\n"
        "y = 0.0500  # nivel-literal-ok:\n",
        encoding="utf-8")
    buscados = niveles_buscados(json_niveles)
    hallados = [(l, t) for l, t in literales_numericos(ruta) if _normalizado(t) in buscados]
    assert hallados == [(1, ".1027"), (5, "0.0500")]  # la exencion sin motivo no vale


def test_parametros_usa_el_caso_base(niveles):
    assert [p.nombre for p in PARAMETROS] == niveles.parametros
    assert {p.nombre: p.heredabilidad for p in PARAMETROS} == niveles.de("caso_base")


def test_agregados(niveles, json_niveles):
    """Caso base 7,07 % (el 7,1 % de los documentos) y segundo nivel 0,148 %."""
    esperados = json_niveles["agregados_esperados"]
    assert niveles.agregado("caso_base") == pytest.approx(esperados["caso_base"], abs=1e-6)
    assert niveles.agregado("segundo_nivel") == pytest.approx(esperados["segundo_nivel"], abs=1e-4)
    assert round(100 * niveles.agregado("segundo_nivel"), 3) == pytest.approx(0.148)


def test_segundo_nivel_derivado_coincide_con_su_control(niveles, json_niveles):
    """V por subpoblacion, con la composicion de la cohorte 2.0, contra los valores escritos."""
    escrito = json_niveles["niveles"]["segundo_nivel"]
    derivado = niveles.de("segundo_nivel")
    for nombre in niveles.parametros:
        assert derivado[nombre] == pytest.approx(escrito[nombre], abs=5e-7), nombre
    assert [n for n, x in derivado.items() if x == 0] == ["f0_variabilidad", "jitter", "hnr", "f3", "vtl"]


def test_v_se_calcula_con_la_composicion_de_la_cohorte(niveles):
    """V sale del archivo de cohorte, no de un valor fijo: otra composicion da otro V."""
    cohorte = leer_cohorte(RUTA_COHORTE)
    assert niveles.composicion == composicion_de(cohorte)
    assert sum(niveles.composicion.values()) == pytest.approx(1.0)
    solo_fin = cohorte.assign(subpoblacion="FIN")
    with pytest.raises(ValueError, match="subpoblaciones"):
        cargar(cohorte=solo_fin)


def test_v_con_una_cohorte_generada(niveles):
    """Con la cohorte generada (misma composicion por diseno), V da lo mismo."""
    otra = cargar(cohorte=generar_cohorte())
    assert otra.de("segundo_nivel") == pytest.approx(niveles.de("segundo_nivel"), abs=1e-12)


def test_describir_dice_nivel_archivo_version_y_fecha(niveles):
    texto = niveles.describir("segundo_nivel")
    for parte in ("segundo_nivel", "niveles_declarados.json", "version 1.1", "2026-11-09", "Tabla S8"):
        assert parte in texto


def test_salvedad_de_jitter_y_hnr(niveles):
    salvedad = niveles.salvedades["jitter_hnr"]
    assert "Campos et al., 2024" in salvedad and "Lima" not in salvedad
    assert "S6" not in salvedad


# --- El cargador rechaza archivos que no cierran -----------------------------

def _copia(tmp_path, cambiar):
    datos = json.loads(RUTA.read_text(encoding="utf-8"))
    cambiar(datos)
    ruta = tmp_path / "niveles_declarados.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def test_rechaza_agregado_que_no_cierra(tmp_path):
    def cambiar(d):
        d["niveles"]["caso_base"]["f3"] += 0.01
    with pytest.raises(ValueError, match="agregado"):
        cargar(_copia(tmp_path, cambiar))


def test_rechaza_parametro_faltante(tmp_path):
    def cambiar(d):
        del d["niveles"]["segundo_nivel"]["vtl"]
    with pytest.raises(ValueError, match="parametros"):
        cargar(_copia(tmp_path, cambiar))


def test_rechaza_v_que_no_coincide_con_su_control(tmp_path):
    def cambiar(d):
        d["variantes"][0]["beta"] *= 1.2
    with pytest.raises(ValueError, match="control escrito"):
        cargar(_copia(tmp_path, cambiar))


def test_rechaza_varianza_conocida_mayor_que_h2(tmp_path):
    def cambiar(d):
        base = d["niveles"]["caso_base"]
        corrimiento = base["f1"] - d["niveles"]["segundo_nivel"]["f1"] / 2
        base["f1"] -= corrimiento
        base["f3"] += corrimiento  # mantiene el agregado
    with pytest.raises(ValueError, match="supera la h2"):
        cargar(_copia(tmp_path, cambiar))
