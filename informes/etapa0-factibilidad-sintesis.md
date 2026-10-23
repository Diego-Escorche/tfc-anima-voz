# Etapa 0 — Factibilidad de la síntesis con KlattGrid

**Fecha:** 23/10/2026 · **Veredicto: PASA.** F0 medida 120,00 Hz contra 120 Hz pedidos (diferencia 0,00 Hz; criterio < 5 Hz).

Script: `scripts/prueba_sintesis.py`. WAV: `informes/prueba_sintesis.wav` (1,5 s, 44.100 Hz).

## Versiones

| Componente | Versión |
|---|---|
| Python | 3.12.4 |
| parselmouth | 0.4.7 |
| Praat (dentro de parselmouth) | 6.1.38 |

## Comandos de KlattGrid probados

Todos se llamaron con `parselmouth.praat.call`. Ninguno falló.

| Comando | Argumentos usados | Resultado |
|---|---|---|
| `Create KlattGrid` | `"voz", 0, 1.5, 6, 1, 1, 6, 1, 1, 1` | Funciona |
| `Add pitch point` | t = 0 y t = 1,5; 120 Hz | Funciona |
| `Add voicing amplitude point` | t = 0 y t = 1,5; 90 dB | Funciona |
| `Add oral formant frequency point` | formantes 1 a 5 en t = 0 | Funciona |
| `Add oral formant bandwidth point` | formantes 1 a 5: 60, 90, 150, 200 y 200 Hz | Funciona |
| `To Sound` | sin argumentos | Funciona (44.100 Hz) |
| `Add flutter point` | t = 0; 0,25 | Funciona |
| `Add aspiration amplitude point` | t = 0; 60 dB | Funciona |
| `Add spectral tilt point` | t = 0; 10 dB | Funciona |

F4 y F5 se calcularon desde VTL = 17 cm con Fn = (2n − 1) · 35.000 / (4 · VTL): 3.602,9 y 4.632,4 Hz.

## Pedido contra medido

### Configuración de `extraccion.py`, sin cambios

Sexo hombre (`"M"`): pitch entre 60 y 220 Hz; formantes con Burg, 5 formantes, techo de 5.000 Hz y mediana sobre los frames sonoros.

| Parámetro | Pedido | Medido |
|---|---|---|
| F0 (Hz) | 120 | 120,000 |
| Variabilidad de F0 (Hz) | — | 0,001 |
| Jitter (fracción) | — | 0,000 |
| HNR (dB) | — | 83,1 |
| F1 (Hz) | 500 | 487,9 |
| F2 (Hz) | 1.500 | **1.344,9** |
| F3 (Hz) | 2.500 | **1.499,0** |
| VTL (cm) | 17 | **22,2** |

Advertencias de plausibilidad de `extraccion.py`: `f3=1499 fuera de [1800, 4000]` y `vtl=22 fuera de [10, 21]`. Con 5 formantes, Burg inserta uno espurio entre F1 y F2 y corre la numeración: el F2 real se lee como F3. Es el mismo problema que el README describe para audio real.

### Otra configuración: Burg con 4 formantes, techo de 5.000 Hz

Se calculó en el script, sin modificar `extraccion.py`.

| Parámetro | Pedido | Medido |
|---|---|---|
| F1 (Hz) | 500 | 486,2 |
| F2 (Hz) | 1.500 | 1.465,9 |
| F3 (Hz) | 2.500 | 2.423,3 |

### Variante con flutter, aspiración e inclinación espectral

Mismos valores, más flutter 0,25, aspiración 60 dB e inclinación de 10 dB. Medida con `extraccion.py` sin cambios.

| Parámetro | Pedido | Medido |
|---|---|---|
| F0 (Hz) | 120 | 120,028 |
| Variabilidad de F0 (Hz) | — | 0,728 |
| Jitter (fracción) | — | 0,003 |
| HNR (dB) | — | 20,9 |
| F1 (Hz) | 500 | 486,6 |
| F2 (Hz) | 1.500 | 953,6 |
| F3 (Hz) | 2.500 | 1.508,9 |
| VTL (cm) | 17 | 24,8 |

Sin flutter ni aspiración, el jitter da 0 y el HNR 83 dB, como anticipaba el brief.

## Riesgos para la Etapa 7

1. **El medidor de formantes falla sobre la vocal sintética.** Con la configuración actual de `extraccion.py` (5 formantes), F2 y F3 salen mal numerados y el VTL medido queda fuera de rango. Con 4 formantes, F2 y F3 quedan 2 a 3 % abajo de lo pedido. VZ-08 sólo exige la F0, así que no se bloquea. Pero la tabla de formantes pedidos contra medidos va a salir mala si no se cambia la configuración. Cambiar `extraccion.py` requiere el visto bueno de Diego.
2. **El ruido de aspiración empeora el tracking de formantes.** Con aspiración a 60 dB, F2 se midió en 954 Hz. Al armar la correspondencia del HNR, el ruido que baja el HNR también degrada la medición de formantes.
3. **El jitter no sale del flutter de forma directa.** El flutter es una modulación lenta del pitch, no una perturbación aleatoria por período. Con flutter 0,25, el jitter medido fue 0,3 % y la variabilidad de F0, 0,73 Hz: un mismo comando mueve dos de los 8 parámetros. Una alternativa que no se probó: agregar un punto de pitch por período con su perturbación aleatoria, como permite el brief. Se puede probar en la Etapa 7.
4. **El VTL no puede hacer ida y vuelta tal como está definido.** En la síntesis, el VTL fija sólo F4 y F5. `extraccion.py`, en cambio, calcula el VTL desde F1 a F3 con el modelo de tubo. Lo que mide es entonces el VTL implícito en F1 a F3, no el pedido. En esta prueba, F1 a F3 (500, 1.500 y 2.500 Hz) corresponden a 17,5 cm, no a 17. El brief no pone criterio de aprobación para el VTL, pero la tabla de la Etapa 7 lo va a mostrar.
5. **La variabilidad de F0 necesita un contorno.** Con dos puntos de pitch fijos da 0,001 Hz. La Etapa 7 ya prevé una variación lenta alrededor de la media.
