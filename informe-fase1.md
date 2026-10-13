# Informe de cierre de la Fase 1 — módulo de Voz

**Proyecto:** Anima — módulo de Voz (Diego Escorche)
**Fecha:** 12 de octubre de 2026
**Alcance:** puesta en marcha del entorno, descarga del corpus VCTK y primera
extracción acústica sobre audio real (prueba de humo).

---

## 1. Resumen

Con esto se completan los tres pendientes de la Fase 1 que faltaban (vencía el 1 de octubre):

| Tarea | Resultado |
|---|---|
| Entorno (venv + dependencias + `tests/test_setup.py`) | Completo. Los 4 chequeos pasan, incluido el análisis y la síntesis reales con pyworld |
| Corpus VCTK 0.92 | Descargado y descomprimido en `data/VCTK-Corpus-0.92/` (110 hablantes) |
| Prueba de humo de `extraccion.py` | 10 archivos (5 mujeres y 5 hombres): **0 errores, 0 advertencias de plausibilidad** |

El pipeline de extracción funciona sobre audio real **sin modificar el código ni
sus parámetros** (`RANGO_F0`, `maximum_formant`). El problema que preocupaba de
la prueba con señal sintética no apareció en esta muestra: un formante espurio
que corre la numeración y arruina VTL.

Sí aparece algo a resolver en la Fase 2: **VTL da sistemáticamente más alto de
lo esperable** (sección 5.1).

---

## 2. Entorno

| Componente | Versión |
|---|---|
| Sistema | Windows 11 |
| Python | 3.12.4 (venv en `.venv/`) |
| praat-parselmouth | 0.4.7 |
| pyworld | 0.3.5 |
| flask | 3.1.3 |
| numpy / scipy | 2.5.4 / 1.18.1 |

Diferencias respecto de lo que preveía `SETUP.md`:

- **pyworld ya no necesita compilarse.** La versión 0.3.5 publica paquetes
  precompilados para Python 3.12 (y también 3.13) en Windows, así que la
  instalación no usó el compilador de C++. La advertencia de `SETUP.md` quedó
  desactualizada y se corrigió.
- **Python 3.12 queda verificado** además de 3.11, que era la única versión
  probada hasta ahora.
- En Windows, `python` puede abrir el acceso directo de Microsoft Store en vez de
  un intérprete real. Se usó el launcher `py -3.12`.

Salida de `tests/test_setup.py`:

```
    version: 0.4.7
[OK] parselmouth (import)
    version: 3.1.3
[OK] flask (import)
    numpy 2.5.4, scipy 1.18.1
[OK] numpy + scipy (import)
    analisis+sintesis OK -- 101 frames de F0 estimados
[OK] pyworld (analisis + sintesis real, no solo import)

Entorno listo para la Fase 1.
```

`parametros.py` y `genotipo.py` corren sin cambios. La cohorte de prueba es
reproducible con la semilla 42.

---

## 3. Corpus

- **VCTK Corpus 0.92** (University of Edinburgh), zip de 10,94 GB.
- `speaker-info.txt` lista **110 hablantes: 63 mujeres y 47 hombres**, con edad
  y acento.
- El audio de esta versión viene en **FLAC**, no en WAV
  (`wav48_silence_trimmed/pXXX/pXXX_NNN_mic1.flac`), grabado con dos micrófonos
  (`mic1`, `mic2`). parselmouth lee FLAC directo y no hace falta convertir.
- `update.txt` documenta 15 archivos que los autores eliminaron por silencio o
  corte. No afecta a esta prueba.

---

## 4. Método de la prueba de humo

- **Muestra:** los primeros 5 hablantes de cada sexo en el orden de
  `speaker-info.txt`, frase `_001`, micrófono `mic1`.
- **Texto controlado:** la frase `_001` es la misma para todos los hablantes
  (*"Please call Stella."*), así que las diferencias entre hablantes no vienen
  del contenido fonético. Duración de 2,0 a 3,4 s.
- **Extracción:** `extraer_parametros(ruta, sexo)` de `src/tfc_voz/extraccion.py`
  con los valores por defecto. El rango de F0 depende del sexo (M 60–220 Hz,
  F 100–300 Hz) y el techo de formantes es 5000 Hz (M) o 5500 Hz (F). El sexo se
  tomó de `speaker-info.txt`.
- **Control de calidad:** los rangos de `RANGOS_PLAUSIBLES` para F1, F2, F3 y VTL.

---

## 5. Resultados

### Por archivo

| Hablante | Sexo | Edad | Acento | F0 medio (Hz) | F0 var. (Hz) | Jitter | HNR (dB) | F1 (Hz) | F2 (Hz) | F3 (Hz) | VTL (cm) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| p225 | F | 23 | Southern England | 197,8 | 29,3 | 0,018 | 12,8 | 415 | 1617 | 2633 | 17,97 |
| p228 | F | 22 | Southern England | 222,8 | 27,2 | 0,019 | 14,0 | 470 | 1763 | 2809 | 16,36 |
| p229 | F | 23 | Southern England | 194,6 | 19,8 | 0,010 | 14,5 | 477 | 1696 | 3126 | 15,94 |
| p230 | F | 22 | Stockton-on-Tees | 209,4 | 20,0 | 0,027 | 15,2 | 590 | 1576 | 2899 | 15,52 |
| p231 | F | 23 | Southern England | 200,4 | 35,6 | 0,027 | 11,1 | 436 | 1391 | 3027 | 17,80 |
| p226 | M | 22 | Surrey | 124,2 | 22,3 | 0,032 | 9,6 | 377 | 1388 | 2723 | 19,39 |
| p227 | M | 38 | Cumbria | 121,6 | 19,2 | 0,015 | 10,4 | 527 | 1221 | 2749 | 18,01 |
| p232 | M | 23 | Southern England | 114,6 | 21,0 | 0,023 | 10,1 | 489 | 1265 | 2797 | 18,09 |
| p237 | M | 22 | Scottish (Fife) | 80,6 | 9,8 | 0,024 | 9,4 | 393 | 1154 | 2476 | 20,89 |
| p241 | M | 21 | Scottish (Perth) | 123,8 | 11,8 | 0,022 | 11,6 | 501 | 1249 | 2562 | 18,52 |

Jitter se expresa como fracción (0,018 = 1,8 %).

### Medias por sexo

| Parámetro | Mujeres | Hombres |
|---|---|---|
| F0 medio | 205,0 Hz | 113,0 Hz |
| Variabilidad de F0 | 26,4 Hz | 16,8 Hz |
| Jitter | 2,0 % | 2,3 % |
| HNR | 13,5 dB | 10,2 dB |
| F1 | 478 Hz | 457 Hz |
| F2 | 1608 Hz | 1256 Hz |
| F3 | 2899 Hz | 2661 Hz |
| VTL | 16,7 cm | 19,0 cm |

Lo que se comporta como se esperaba:

- **F0 separa bien por sexo:** 195–223 Hz en mujeres y 81–124 Hz en hombres, sin
  saltos que sugieran que el algoritmo leyó la mitad o el doble del pitch real,
  salvo el caso a revisar de p237 (5.3).
- **Los formantes están en orden y dentro de rango en los 10 archivos.** F2 y F3
  son más altos en mujeres, como corresponde a un tracto vocal más corto.
- **HNR es más alto en mujeres**, el patrón habitual.

### 5.1 VTL sobreestimado (lo importante para la Fase 2)

VTL da 16,7 cm de media en mujeres y 19,0 cm en hombres. Ambos valores están unos
2 cm por encima de los valores de referencia habituales en adultos (del orden de
14–15 cm en mujeres y 17 cm en hombres). La diferencia entre sexos sí se mantiene,
y ningún archivo salió del rango plausible (10–21 cm), así que el control de
calidad no lo detecta.

Desglosando la estimación que aporta cada formante,
`L_n = (2n−1)·c / (4·F_n)`:

| | L desde F1 | L desde F2 | L desde F3 | VTL (promedio) |
|---|---|---|---|---|
| Mujeres | 18,6 cm | 16,4 cm | 15,1 cm | 16,7 cm |
| Hombres | 19,5 cm | 21,0 cm | 16,5 cm | 19,0 cm |

- **La estimación desde F3 es la más estable y la más cercana a lo esperable** en
  ambos sexos.
- **F1 (en mujeres) y F2 (en hombres) inflan el promedio.** El modelo de tubo
  uniforme supone una vocal neutra, pero acá se aplica sobre la mediana de los
  formantes de una frase entera, cuyas vocales no son neutras. Las medianas de F1
  y F2 quedan bajas respecto del tubo neutro, y cada una se traduce en un largo
  mayor.

Es coherente con lo que ya advierte la docstring de `_vtl_desde_formantes`: el
tubo uniforme es una aproximación. **No se modificó nada.** Queda como decisión
para la Fase 2, antes de reescalar la cohorte sintética a unidades reales, con
dos caminos posibles:

1. Cambiar la estimación de VTL, por ejemplo con el método de Lammert & Narayanan
   (2015), que ya está en la bibliografía, o con un ajuste distinto sobre los
   formantes.
2. Mantenerla y declarar el sesgo en la memoria.

Como VTL es el parámetro de h² derivada (0,13), conviene que su medición sea la
más defendible del espacio.

### 5.2 Jitter alto

El jitter medio (2,0–2,3 %) supera el umbral de referencia de Praat para vocales
sostenidas (1,04 %). Es esperable en **habla leída continua** de 2–3 segundos,
donde las transiciones entre sonidos agregan perturbación. No indica una falla,
pero hay que tenerlo en cuenta al interpretar los rangos del corpus y al
comparar con la literatura, que suele medir sobre vocales sostenidas.

### 5.3 Caso a revisar: p237

Es un hombre escocés de 22 años, con F0 = 80,6 Hz (el más bajo, unos 33 Hz por
debajo de la media masculina) y la menor variabilidad de F0 (9,8 Hz). Está dentro
del rango de búsqueda y puede ser una voz genuinamente grave, pero también es el
patrón típico de un error en que el algoritmo lee la mitad del pitch real. Conviene
verificarlo sobre más frases del mismo hablante cuando se procese el corpus
completo.

---

## 6. Limitaciones de esta prueba

- **Es una prueba de humo, no una validación estadística:** 10 de 110 hablantes,
  una frase de ~2 s por hablante.
- **No hay valores de referencia por hablante** contra los cuales comparar.
  "Plausible" significa dentro de los rangos de `RANGOS_PLAUSIBLES`, no correcto.
- **La muestra es casi toda de acento inglés del sur de Inglaterra**, por el orden
  de `speaker-info.txt`. Para el objetivo del proyecto alcanza: el README excluye
  ampliar idiomas o acentos.

---

## 7. Próximos pasos (Fase 2)

1. Correr la extracción sobre el corpus VCTK completo y contar cuántos archivos
   disparan advertencias (pedido explícito del README, §8).
2. Decidir el tratamiento del sesgo de VTL (5.1) antes de reescalar la cohorte.
3. Revisar p237 con varias frases (5.3).
4. Con los rangos y correlaciones reales, reescalar la cohorte sintética de
   `genotipo.py` a unidades reales y ajustar el modelo heterocedástico.
