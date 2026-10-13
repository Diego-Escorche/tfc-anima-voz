"""
Extraccion de los 8 parametros acusticos desde un archivo WAV, con parselmouth.

parselmouth envuelve los mismos algoritmos de Praat que uso Gisladottir et al.
(2023), asi que los rangos de F0 por sexo se toman de ese paper para que las
mediciones sean comparables con la literatura de heredabilidad del proyecto.

Uso:
    from extraccion import extraer_parametros
    p = extraer_parametros("p225_001.wav", sexo="F")
"""

from dataclasses import dataclass, asdict

import numpy as np
import parselmouth
from parselmouth.praat import call

# Rangos de busqueda de F0 por sexo (Gisladottir et al. 2023, Science Advances).
# Usar los defaults de Praat (75-600 Hz) en vez de estos es la causa mas comun
# de errores de pitch-halving / pitch-doubling.
RANGO_F0 = {
    "M": (60.0, 220.0),
    "F": (100.0, 300.0),
}

# Velocidad del sonido en aire calido y humedo, cm/s (Johnson, cap. 2).
C_SONIDO = 35000.0


# Rangos de plausibilidad para control de calidad. Un valor fuera de rango
# casi siempre significa que el algoritmo fallo (formante espurio corriendo
# la numeracion, pitch-halving/doubling), no que la voz sea rara.
RANGOS_PLAUSIBLES = {
    "f1": (200.0, 1100.0),
    "f2": (700.0, 2800.0),
    "f3": (1800.0, 4000.0),
    "vtl": (10.0, 21.0),
}


@dataclass
class ParametrosExtraidos:
    f0_medio: float          # Hz
    f0_variabilidad: float   # Hz (desvio estandar)
    jitter: float            # fraccion (local jitter; x100 para %)
    hnr: float               # dB
    f1: float                # Hz
    f2: float                # Hz
    f3: float                # Hz
    vtl: float               # cm
    advertencias: tuple = ()  # controles de plausibilidad que no pasaron

    @property
    def confiable(self):
        return not self.advertencias

    def as_dict(self):
        return asdict(self)


def _revisar_plausibilidad(valores):
    """Devuelve la lista de parametros fuera de rango esperado.

    Pensado para filtrar automaticamente los casos dudosos al procesar el
    corpus completo, en vez de revisar cientos de archivos a mano.
    """
    fallas = []
    for nombre, (lo, hi) in RANGOS_PLAUSIBLES.items():
        v = valores.get(nombre)
        if v is None or np.isnan(v):
            fallas.append(f"{nombre}: sin valor")
        elif not (lo <= v <= hi):
            fallas.append(f"{nombre}={v:.0f} fuera de [{lo:.0f}, {hi:.0f}]")
    return tuple(fallas)


def _vtl_desde_formantes(f1, f2, f3):
    """Longitud del tracto vocal por el modelo de tubo uniforme cerrado-abierto.

    Fn = (2n-1)*c/(4L)  ->  L = (2n-1)*c/(4*Fn)

    Se promedia la estimacion que da cada formante, que es mas estable que
    usar solo F1. Es una aproximacion: el tracto vocal real no es un tubo
    uniforme (ver teoria de perturbacion, Johnson cap. 6), por eso VTL entra
    al modelo como una estimacion con incertidumbre, no como una medida exacta.
    """
    estimaciones = [
        (2 * n - 1) * C_SONIDO / (4 * f)
        for n, f in enumerate([f1, f2, f3], start=1)
        if f and not np.isnan(f) and f > 0
    ]
    return float(np.mean(estimaciones)) if estimaciones else float("nan")


def extraer_parametros(ruta_wav, sexo, max_formante=None):
    """Extrae los 8 parametros de un WAV.

    sexo: "M" o "F" -- define el rango de busqueda de F0 y el techo de
          formantes. Es obligatorio a proposito: sin el, el pitch tracking
          es poco confiable.
    """
    sexo = sexo.upper()
    if sexo not in RANGO_F0:
        raise ValueError(f"sexo debe ser 'M' o 'F', se recibio {sexo!r}")

    f0_min, f0_max = RANGO_F0[sexo]
    # Techo de formantes estandar de Praat: 5000 Hz voz masculina, 5500 femenina.
    if max_formante is None:
        max_formante = 5000.0 if sexo == "M" else 5500.0

    snd = parselmouth.Sound(str(ruta_wav))

    # --- Fuente: F0 y su variabilidad ---
    pitch = snd.to_pitch(pitch_floor=f0_min, pitch_ceiling=f0_max)
    valores = pitch.selected_array["frequency"]
    sonoros = valores[valores > 0]  # 0 = frame sordo
    if sonoros.size == 0:
        raise ValueError("no se detectaron frames sonoros; revisar audio o rango de F0")
    f0_medio = float(np.mean(sonoros))
    f0_var = float(np.std(sonoros))

    # --- Fuente: jitter (perturbacion periodo a periodo) ---
    pp = call(snd, "To PointProcess (periodic, cc)", f0_min, f0_max)
    jitter = call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)

    # --- Fuente: HNR (relacion armonicos/ruido) ---
    harm = snd.to_harmonicity_cc(minimum_pitch=f0_min)
    h_vals = harm.values[harm.values != -200]  # -200 = frame sin definir
    hnr = float(np.mean(h_vals)) if h_vals.size else float("nan")

    # --- Filtro: formantes ---
    # Dos decisiones que importan y no son el default obvio:
    #  1) solo se miden frames SONOROS -- en silencio o en consonantes sordas
    #     el tracking de formantes devuelve basura que arrastra el promedio.
    #  2) se usa MEDIANA, no media -- un puñado de frames con un formante
    #     espurio corre la numeracion y desplaza la media; la mediana aguanta.
    formantes = snd.to_formant_burg(max_number_of_formants=5,
                                    maximum_formant=max_formante)

    def _es_sonoro(t):
        f = pitch.get_value_at_time(t)
        return f is not None and not np.isnan(f) and f > 0

    tiempos_sonoros = [t for t in formantes.ts() if _es_sonoro(t)]

    def _fmt(n):
        vals = [formantes.get_value_at_time(n, t) for t in tiempos_sonoros]
        vals = [v for v in vals if v is not None and not np.isnan(v)]
        return float(np.median(vals)) if vals else float("nan")

    f1, f2, f3 = _fmt(1), _fmt(2), _fmt(3)
    vtl = _vtl_desde_formantes(f1, f2, f3)

    valores = {"f1": f1, "f2": f2, "f3": f3, "vtl": vtl}
    return ParametrosExtraidos(
        f0_medio=f0_medio,
        f0_variabilidad=f0_var,
        jitter=float(jitter),
        hnr=hnr,
        f1=f1, f2=f2, f3=f3,
        vtl=vtl,
        advertencias=_revisar_plausibilidad(valores),
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("uso: python extraccion.py <archivo.wav> <M|F>")
        sys.exit(1)
    p = extraer_parametros(sys.argv[1], sys.argv[2])
    for k, v in p.as_dict().items():
        if k == "advertencias":
            continue
        print(f"  {k:18s} {v:10.3f}")
    if p.advertencias:
        print("\n  ADVERTENCIAS (extraccion probablemente no confiable):")
        for a in p.advertencias:
            print(f"    - {a}")
    else:
        print("\n  Todos los controles de plausibilidad OK")
