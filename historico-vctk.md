# Histórico: VCTK y la extracción por lote (fuera de alcance desde el 19/10/2026)

**Estado:** archivado el 20/10/2026. **No usar como insumo del modelo.**

El 19/10 el grupo sacó del alcance el audio real: VCTK, `pyworld`, la síntesis WAV y Flask.
Este archivo deja constancia de lo que se hizo con VCTK entre el 12 y el 13 de octubre, porque
el código y los datos se borraron del disco el 20/10 para liberar espacio (~12 GB).

## Qué se borró

| Qué | Tamaño | Versionado en git |
|---|---|---|
| `data/VCTK-Corpus-0.92.zip` y `data/VCTK-Corpus-0.92/` | ~11,7 GB el zip, más lo descomprimido | No (`data/` está en `.gitignore`) |
| `data/derivados/` (`vctk_por_archivo.csv`, `vctk_por_hablante.csv`, `vctk_estadisticas.json`) | ~7,7 MB | No |
| `src/tfc_voz/corpus.py` (extracción por lote y estadísticas) | — | **No, nunca se commiteó** |
| `pyworld` y `flask` (con sus dependencias) en `.venv` | — | Se sacaron de `requirements.txt` |

`extraccion.py` (la extracción de un solo archivo con parselmouth) **se conserva sin cambios**.

## Qué hacía `corpus.py`

- Corría `extraccion.extraer_parametros` sobre todos los audios `mic1` de VCTK 0.92, con 10 procesos
  en paralelo y reanudable. No usaba `mic2` porque es la misma frase grabada con otro micrófono.
- La unidad de análisis era el **hablante** (110), no la frase: cada parámetro era la mediana sobre las
  frases sin advertencias ni error.
- Las correlaciones se calculaban sobre las medianas por hablante, **estandarizando dentro de cada sexo**,
  para que la diferencia entre sexos no fabricara correlaciones.
- Un F0 de frase por debajo de 0,6 o por encima de 1,6 veces la mediana del hablante se contaba
  como posible salto de octava.

## Resultados (13/10/2026)

- 44.455 audios de 110 hablantes (63 F, 47 M), 0 errores, ~75 min.
- 998 archivos con advertencias (2,2 %), 997 de ellos por VTL > 21 cm en hombres. Formantes fuera de rango: 4.
- **Sesgo del VTL:** el estimador de tubo uniforme promediando F1–F3 daba ~2 cm de más. El sesgo venía de F1
  (desde F1: 18,6 cm; M 21,7), mientras que F2 y F3 coincidían entre sí (F 15,1/15,4; M 17,6/17,6).
  Quedó sin resolver: el 20/10 el VTL pasó a tomarse directo de la S6 y dejó de medirse desde audio.
- p237 (F0 = 80,6 Hz) resultó una voz grave real: 339 frases estables entre 77,8 y 87,7 Hz, sin saltos.
  Ningún hablante tuvo más de 0,2 % de saltos de F0.

### Media y desvío entre hablantes, por sexo

VTL con el estimador sesgado (F1–F3).

| Parámetro | Media F | Desvío F | Media M | Desvío M |
|---|---|---|---|---|
| f0_medio (Hz) | 200.6 | 17.3 | 110.7 | 16.1 |
| f0_variabilidad (Hz) | 26.85 | 6.87 | 14.65 | 4.51 |
| jitter (fracción) | 0.02226 | 0.00437 | 0.02876 | 0.0038 |
| hnr (dB) | 13.25 | 1.68 | 9.596 | 1.19 |
| f1 (Hz) | 473 | 39.1 | 404.3 | 25.4 |
| f2 (Hz) | 1741 | 85.4 | 1496 | 57.8 |
| f3 (Hz) | 2847 | 128 | 2494 | 100 |
| vtl (cm) | 16.46 | 0.734 | 19.06 | 0.603 |

### Correlaciones dentro de sexo (n = 110 hablantes)

| | f0_medio | f0_var | jitter | hnr | f1 | f2 | f3 | vtl |
|---|---|---|---|---|---|---|---|---|
| f0_medio | 1 | 0.692 | -0.378 | 0.264 | 0.321 | 0.230 | 0.241 | -0.393 |
| f0_var | | 1 | -0.067 | 0.018 | 0.336 | 0.189 | 0.147 | -0.366 |
| jitter | | | 1 | -0.635 | -0.286 | -0.000 | 0.126 | 0.169 |
| hnr | | | | 1 | -0.142 | 0.022 | -0.042 | 0.120 |
| f1 | | | | | 1 | 0.100 | 0.107 | -0.806 |
| f2 | | | | | | 1 | 0.441 | -0.566 |
| f3 | | | | | | | 1 | -0.572 |
| vtl | | | | | | | | 1 |

La correlación de VTL con F1 a F3 es en parte mecánica: el VTL se calculaba a partir de esos formantes.

## Si hubiera que rehacerlo

VCTK 0.92 está en https://datashare.ed.ac.uk/handle/10283/3443. Haría falta reescribir `corpus.py` y
reinstalar `pyworld` sólo si se vuelve a sintetizar audio. Las dos cosas están fuera de alcance; volver a
sumarlas lo tiene que decidir el grupo.
