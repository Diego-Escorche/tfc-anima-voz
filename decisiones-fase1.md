# Decisiones de diseño — módulo de Voz

**Actualizado:** 20/10/2026 (regla de lectura de la S6 y VTL directo).

## Espacio de parámetros y heredabilidad

Todos los valores están expresados en **escala h²-SNP** (fracción de varianza
fenotípica explicada por variantes comunes), que es la escala en la que trabaja
el modelo.

| Parámetro | Unidad | h² | IC95 % | Evidencia | Fuente |
|---|---|---|---|---|---|
| f0_medio | Hz | 0.1027 | 0.0335 a 0.1719 | directa | Gisladóttir et al. 2023, S6: MedianF0_MeasureVowels |
| f0_variabilidad | Hz (SD) | 0.0410 | −0.0303 a 0.1123 | directa | Gisladóttir et al. 2023, S6: StdF0_MeasureVowels |
| f1 | Hz | 0.0619 | −0.0091 a 0.1329 | directa | Gisladóttir et al. 2023, S6: MedianF1_MeasureVowels |
| f2 | Hz | 0.1353 | 0.0655 a 0.2051 | directa | Gisladóttir et al. 2023, S6: MedianF2_MeasureVowels |
| f3 | Hz | 0.0644 | −0.0009 a 0.1297 | directa | Gisladóttir et al. 2023, S6: MedianF3_MeasureVowels |
| vtl | cm | 0.0606 | −0.0090 a 0.1302 | directa | Gisladóttir et al. 2023, S6: VTL |
| jitter | % | 0.05 | — | **débil** | Van Lierde 2005 (n.s.) / Campos et al. 2024 (ICC MZ 0.374) |
| hnr | dB | 0.05 | — | **débil** | Campos et al. 2024 (ICC MZ 0.366) |

Promedio: **0,0707**. Fuente de la S6: hoja S6_Heritability de
`abq2969_Tables_S1_to_S11.xlsx`, volcada a
`referencias/tabla-s6-heredabilidades.csv`. `tests/test_parametros.py` verifica
que los valores cargados en `parametros.py` coincidan con ese CSV.

### Regla de lectura de la S6 (adoptada el 20/10/2026)

**Regla agregada de cinco vocales**, aprobada por Diego el 20/10/2026: para cada
parámetro se toma la fila medida sobre el conjunto de las vocales
[i, a, ɔ, u, ɛ].

- **Por qué no los máximos.** Los valores que estaban cargados eran el más alto de
  cada medida entre todas las tareas y vocales. De las 72 medidas del estudio, 41
  quedan por debajo del 5 %, así que tomar el mejor valor de cada rasgo es una
  envolvente superior: el mismo sesgo de optimismo que el proyecto declara
  combatir. Los cinco máximos tenían IC95 % que excluían el cero; con la regla
  agregada, tres de esos cinco lo cruzan.
- **Por qué no la tarea de lectura.** F1, F2 y F3 se midieron sólo en tareas de
  vocales, nunca en lectura. La medida agregada de vocales es la única que existe
  para todos los rasgos.
- **Los máximos no se borran.** Quedan en `H2_MAXIMOS` (`parametros.py`) para un
  análisis de sensibilidad. El modelo no los usa.

| Parámetro | Máximo anterior | Fila del máximo |
|---|---|---|
| f0_medio | 0.1675 | MedianF0_MeasureReading |
| f0_variabilidad | 0.1276 | StdF0_MeasureReading |
| f1 | 0.0872 | MedianF1_MeasureA |
| f2 | 0.1353 | MedianF2_MeasureVowels (coincide con la regla) |
| f3 | 0.0815 | MedianF3_MeasureO |

Promedio de Voz según la regla: 10,4 % con máximos y el VTL viejo; 9,6 % con
máximos y el VTL corregido; **7,1 % con la regla agregada y el VTL corregido**.

### Escala de las h²

Gisladóttir log-transformó cada rasgo y lo ajustó por edad, IMC, altura y
micrófono, por separado dentro de cada sexo, **antes** de estimar h². Estas h²
están entonces por encima de sexo, edad y altura, no incluidas en ellas. Esto
desarma la afirmación de que la línea base poblacional ya captura casi toda la
señal heredable de la voz.

Queda abierto si la h² es fracción de la varianza residual y no de la total. Si
es así, el techo del ΔR² sobre una línea base con sexo y edad es
h² × (1 − R² de la línea base), y aplica igual a Rostro.

### VTL: valor directo de la S6

La fila VTL de la S6 mide el largo del tracto vocal (medida agregada de F1 a F4
sobre las cinco vocales) directamente en escala h²-SNP: **0.0606**
(IC95 % −0.009 a 0.130).

Hasta el 20/10/2026 el VTL estaba cargado como "derivado": se tomaba el h² de
gemelos de Dediu et al. 2022 (SVTh = 0.26) y se lo dividía por dos, con un
factor 1/2 supuesto por el proyecto. Con el valor directo, ese supuesto queda
descartado: el cociente real entre h²-SNP y h² de gemelos es 0.0606 / 0.26 =
**0,23**, no 0,5. El VTL estaba sobreestimado al doble.

### Jitter y HNR (0.05, evidencia débil)

No están en la S6. La literatura de gemelos es chica y contradictoria: Van
Lierde et al. 2005 (Journal of Voice) explícitamente NO obtuvo correlaciones
significativas para jitter ni shimmer en gemelos monocigóticos, mientras que
Campos et al. 2024 (Social Sciences & Humanities Open, 10, 101062;
gemelas brasileras) reporta correlaciones intra-par débiles
pero significativas en 46 pares de gemelas monocigóticas (tabla 5): ICC 0.374
para jitter (IC 95 % de 0.106 a 0.591) y 0.366 para HNR (de 0.097 a 0.585),
las dos con p = 0.004. Verificado contra el artículo por Diego el 10/11. Ninguno
de los dos da un h²-SNP. En el texto se cita **Campos et al. (2024)**, como el
encabezado de página de la revista ("P. Bruna Campos et al.").

**Lectura corregida (10/11).** El grupo dicigótico de Campos et al. es de 10
pares, con intervalos de alrededor de −0,6 a +0,8, así que no permite distinguir
si la similitud de las monocigóticas es genética o de ambiente compartido.
Ninguna de las dos fuentes estima una heredabilidad. El 0,05 es una
**cota superior declarada por el proyecto**, deliberadamente generosa, para no
dar por supuesto el resultado nulo que el módulo espera encontrar: con 0,05 hay
señal que el sistema podría recuperar si estuviera, y un ΔR² nulo pasa a ser un
hallazgo y no una consecuencia aritmética del supuesto.

Ese patrón es consistente con Gisladóttir et al. 2023: de sus 72 medidas
acústicas, **41 tienen h²-SNP por debajo del 5 %**. Un valor conservador de 0.05
para jitter y HNR es coherente con esa distribución y no inventa señal donde la
evidencia no la respalda.

**Implicación para la hipótesis:** se espera que jitter y HNR muestren un ΔR²
prácticamente nulo. Eso NO es una falla del modelo, es el resultado esperado:
incluso dentro del dominio de Voz hay parámetros donde el genotipo aporta y otros
donde no.

### Pendiente menor

Confirmar si existe algún estudio posterior a 2024 con h²-SNP directo para
jitter/HNR. Si aparece, reemplaza el valor conservador.

## Representación del genotipo sintético — Opción A

Por parámetro: `score_total = score_genetico + score_ambiental`, con
`score_genetico ~ N(0, h²)` y `score_ambiental ~ N(0, 1-h²)`.

Se decidió NO simular SNPs individuales (Opción B), para no consumir tiempo en
el parseo de 1000 Genomes. Si sobra margen más adelante, la variante
rs11046212-T de *ABCC9* (AF ~47.7 % en Europa, efecto +2.1 Hz/alelo según
Gisladóttir et al. 2023) queda como candidata para una versión más fiel de
f0_medio específicamente.

## Factores excluidos del alcance

Estos factores modifican la voz pero no se modelan uno por uno:

- Pubertad
- Envejecimiento
- Trauma o lesión nerviosa (p. ej. del nervio laríngeo)
- Enfermedad
- Tabaquismo
- Entrenamiento vocal aprendido (canto, actuación)
- Trastornos funcionales de la voz

Todos quedan absorbidos en el término ambiental **por construcción**: la h²-SNP
publicada se midió sobre poblaciones reales que ya los incluyen, así que no forman
parte de la señal genética y no hace falta código extra para excluirlos.
