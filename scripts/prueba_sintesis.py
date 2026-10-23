"""
Etapa 0: prueba de factibilidad de la sintesis con KlattGrid desde parselmouth.

No se integra al paquete: sirve para descubrir el riesgo tecnico de la Etapa 7
antes de llegar a ella.

Uso (parado en la raiz del proyecto):
    python scripts/prueba_sintesis.py
    python scripts/prueba_sintesis.py --salida informes/prueba_sintesis.wav

Genera 1,5 s de una vocal sostenida (F0 = 120 Hz, F1 = 500, F2 = 1500,
F3 = 2500 Hz, VTL = 17 cm), la mide con extraccion.py (sexo hombre) y muestra
lo pedido al lado de lo medido. Prueba cada comando de KlattGrid por separado
e informa cuales funcionaron.
"""

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
import parselmouth
from parselmouth.praat import call

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from tfc_voz.extraccion import C_SONIDO, extraer_parametros  # noqa: E402

DURACION = 1.5
PEDIDO = {"f0_medio": 120.0, "f1": 500.0, "f2": 1500.0, "f3": 2500.0, "vtl": 17.0}

# Formantes 4 y 5 desde el VTL, con el modelo de tubo: Fn = (2n - 1) * c / (4 * vtl).
F4 = 7 * C_SONIDO / (4 * PEDIDO["vtl"])
F5 = 9 * C_SONIDO / (4 * PEDIDO["vtl"])
FORMANTES = [PEDIDO["f1"], PEDIDO["f2"], PEDIDO["f3"], F4, F5]
# Anchos de banda de los formantes 1 a 5 (constantes del brief, Etapa 7).
ANCHOS_BANDA = [60.0, 90.0, 150.0, 200.0, 200.0]
AMPLITUD_SONORA_DB = 90.0

# Comandos opcionales, que la Etapa 7 va a necesitar para jitter y hnr.
# Valores de prueba: solo se verifica que el comando corra y cuanto mueve la medicion.
FLUTTER = 0.25             # fraccion, 0 a 1
ASPIRACION_DB = 60.0       # amplitud del ruido de aspiracion
INCLINACION_DB = 10.0      # spectral tilt


class Registro:
    """Corre cada comando de Praat por separado y anota si funciono."""

    def __init__(self):
        self.filas = []

    def correr(self, nombre, *args):
        try:
            resultado = call(*args)
            self.filas.append((nombre, "funciona", ""))
            return resultado
        except Exception as e:  # el mensaje de Praat es lo que hay que informar
            self.filas.append((nombre, "falla", str(e).strip().splitlines()[0]))
            return None


def crear_klattgrid(reg, con_extras=False):
    kg = reg.correr("Create KlattGrid", "Create KlattGrid", "voz", 0, DURACION, 6, 1, 1, 6, 1, 1, 1)
    if kg is None:
        return None
    for t in (0, DURACION):
        reg.correr("Add pitch point", kg, "Add pitch point", t, PEDIDO["f0_medio"])
        reg.correr("Add voicing amplitude point", kg, "Add voicing amplitude point", t, AMPLITUD_SONORA_DB)
    for n, (f, b) in enumerate(zip(FORMANTES, ANCHOS_BANDA), start=1):
        reg.correr("Add oral formant frequency point", kg, "Add oral formant frequency point", n, 0, f)
        reg.correr("Add oral formant bandwidth point", kg, "Add oral formant bandwidth point", n, 0, b)
    if con_extras:
        reg.correr("Add flutter point", kg, "Add flutter point", 0, FLUTTER)
        reg.correr("Add aspiration amplitude point", kg, "Add aspiration amplitude point", 0, ASPIRACION_DB)
        reg.correr("Add spectral tilt point", kg, "Add spectral tilt point", 0, INCLINACION_DB)
    return kg


def formantes_burg(ruta_wav, n_formantes, techo=5000.0, f0_min=60.0, f0_max=220.0):
    """Mediana de F1-F3 sobre frames sonoros, como extraccion.py, con otro numero de formantes."""
    snd = parselmouth.Sound(str(ruta_wav))
    pitch = snd.to_pitch(pitch_floor=f0_min, pitch_ceiling=f0_max)
    fmt = snd.to_formant_burg(max_number_of_formants=n_formantes, maximum_formant=techo)
    ts = [t for t in fmt.ts() if (pitch.get_value_at_time(t) or 0) > 0]
    medianas = []
    for n in (1, 2, 3):
        vals = [fmt.get_value_at_time(n, t) for t in ts]
        vals = [v for v in vals if v is not None and not np.isnan(v)]
        medianas.append(float(np.median(vals)) if vals else float("nan"))
    return medianas


def imprimir_tabla(titulo, medido):
    print(f"\n{titulo}")
    print(f"  {'parametro':16s} {'pedido':>10s} {'medido':>10s}")
    for k, v in medido.items():
        pedido = PEDIDO.get(k)
        print(f"  {k:16s} {pedido if pedido is not None else '-':>10} {v:10.3f}")


def main():
    ap = argparse.ArgumentParser(description="Etapa 0: factibilidad de la sintesis con KlattGrid")
    ap.add_argument("--salida", type=Path, default=RAIZ / "informes" / "prueba_sintesis.wav")
    args = ap.parse_args()

    print(f"Python {sys.version.split()[0]} · parselmouth {parselmouth.__version__} · "
          f"Praat {parselmouth.PRAAT_VERSION}")
    print(f"Formantes pedidos: {', '.join(f'{f:.1f}' for f in FORMANTES)} Hz "
          f"(F4 y F5 desde VTL = {PEDIDO['vtl']} cm)")

    reg = Registro()
    kg = crear_klattgrid(reg)
    snd = reg.correr("To Sound", kg, "To Sound") if kg is not None else None
    if snd is None:
        print("\nNo se pudo sintetizar. Comandos:")
        for fila in reg.filas:
            print("  ", fila)
        sys.exit(1)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    snd.save(str(args.salida), "WAV")
    print(f"WAV: {args.salida} ({snd.sampling_frequency:.0f} Hz, {snd.duration:.2f} s)")

    # Variante con flutter, aspiracion e inclinacion: solo para ver si corren y que mueven.
    reg_extra = Registro()
    kg_extra = crear_klattgrid(reg_extra, con_extras=True)
    snd_extra = reg_extra.correr("To Sound", kg_extra, "To Sound")
    # extraccion.py lee de un archivo; la variante no se guarda en informes/
    ruta_extra = Path(tempfile.mkdtemp()) / "prueba_sintesis_extras.wav"
    snd_extra.save(str(ruta_extra), "WAV")

    print("\nComandos de KlattGrid:")
    vistos = set()
    for nombre, estado, error in reg.filas + reg_extra.filas:
        if (nombre, estado) in vistos:
            continue
        vistos.add((nombre, estado))
        print(f"  {nombre:34s} {estado}{'  -- ' + error if error else ''}")

    p = extraer_parametros(args.salida, sexo="M")
    medido = {k: v for k, v in p.as_dict().items() if k != "advertencias"}
    imprimir_tabla("Medido con extraccion.py (sexo M: Burg, 5 formantes, techo 5000 Hz)", medido)
    print(f"  advertencias: {list(p.advertencias) or 'ninguna'}")

    f1, f2, f3 = formantes_burg(args.salida, n_formantes=4)
    imprimir_tabla("Formantes con Burg, 4 formantes, techo 5000 Hz (otra configuracion)",
                   {"f1": f1, "f2": f2, "f3": f3})

    pe = extraer_parametros(ruta_extra, sexo="M")
    medido_extra = {k: v for k, v in pe.as_dict().items() if k != "advertencias"}
    imprimir_tabla(f"Variante con flutter {FLUTTER}, aspiracion {ASPIRACION_DB} dB e inclinacion "
                   f"{INCLINACION_DB} dB (extraccion.py)", medido_extra)

    diferencia = abs(p.f0_medio - PEDIDO["f0_medio"])
    veredicto = "PASA" if diferencia < 5 else "NO PASA"
    print(f"\nVeredicto: {veredicto} (F0 medida {p.f0_medio:.2f} Hz, diferencia {diferencia:.2f} Hz)")
    sys.exit(0 if diferencia < 5 else 1)


if __name__ == "__main__":
    main()
