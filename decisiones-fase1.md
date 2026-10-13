# Decisiones de la Fase 1 -- modulo de Voz

## Corpus de validacion
**VCTK Corpus** (no TIMIT -- sin acceso). Gratuito, sin membresia LDC,
109 hablantes con speaker-info.txt (edad, sexo, acento).
Fuente: https://datashare.ed.ac.uk/handle/10283/3443

## Espacio de parametros y heredabilidad

Todos los valores estan expresados en **escala h2-SNP** (fraccion de varianza
fenotipica explicada por variantes comunes), que es la escala en la que trabaja
el modelo.

| Parametro | Unidad | h2 | Evidencia | Fuente |
|---|---|---|---|---|
| f0_medio | Hz | 0.17 | directa | Gisladottir et al. 2023 (IC95% 9-24%) |
| f0_variabilidad | Hz (SD) | 0.13 | directa | Gisladottir et al. 2023 |
| f1 | Hz | 0.09 | directa | Gisladottir et al. 2023 |
| f2 | Hz | 0.14 | directa | Gisladottir et al. 2023 |
| f3 | Hz | 0.08 | directa | Gisladottir et al. 2023 |
| vtl | cm | 0.13 | **derivada** | Dediu et al. 2022, Tabla 2 (SVTh = 0.26 en gemelos, deflacionado) |
| jitter | % | 0.05 | **debil** | Van Lierde 2005 (n.s.) / Lima et al. 2024 (ICC MZ 0.374) |
| hnr | dB | 0.05 | **debil** | Lima et al. 2024 (ICC MZ 0.366) |

### Por que "derivada" y "debil" en vez de "placeholder"

Los tres valores que antes eran placeholder ciego ahora tienen respaldo
bibliografico, pero de distinta calidad que los cinco de Gisladottir:

**VTL (0.13).** Dediu et al. 2022 SI da el numero: en su Tabla 2, la medida
SVTh (largo del tracto vocal supralaringeo horizontal, usando prosthion y
atlas) tiene h2 = 0.26 (IC95% 0.03-0.62), clasificada como clase II
("evidencia fuerte"); la medida vertical SVTv da h2 = 0.24 (IC95% 0.00-0.74),
clase IV ("evidencia circunstancial"). El placeholder anterior (0.35) era
demasiado alto.

Pero **ese 0.26 no es h2-SNP**: es heredabilidad de sentido estrecho estimada
en un diseno de gemelos, que captura TODA la varianza genetica aditiva. El
h2-SNP solo captura la parte explicada por variantes comunes genotipadas y
suele ser bastante menor. Mezclar 0.26 (gemelos) con 0.17 (SNP) en el mismo
espacio inflaria artificialmente el aporte genetico de VTL frente a F0.

Decision: deflacionar a la mitad -> **0.13**. El factor 1/2 es un supuesto
explicito del proyecto, no un valor publicado, y debe declararse como tal en
la memoria. Es facilmente ajustable en `parametros.py` si mas adelante se
decide otro criterio.

**Jitter (0.05) y HNR (0.05).** La literatura de gemelos es chica y
contradictoria: Van Lierde et al. 2005 (Journal of Voice) explicitamente NO
obtuvo correlaciones significativas para jitter ni shimmer en gemelos
monocigoticos, mientras que Lima et al. 2024 (gemelas brasileras) reporta
correlaciones intra-par debiles pero significativas (ICC 0.374 para jitter,
0.366 para HNR). Ninguno de los dos da un h2-SNP.

Ese patron es consistente con lo que reporta Gisladottir et al. 2023: de sus
72 medidas acusticas, **41 tienen h2-SNP por debajo del 5%**. Un valor
conservador de 0.05 para jitter y HNR es coherente con esa distribucion y no
inventa senal donde la evidencia no la respalda.

**Implicacion para la hipotesis:** se espera que jitter y HNR muestren un
delta-R2 practicamente nulo. Eso NO es una falla del modelo, es el resultado
esperado, y refuerza el argumento del gradiente: incluso dentro del dominio
de Voz hay parametros donde el genotipo aporta y otros donde no.

### Pendiente menor
Confirmar si existe algun estudio posterior a 2024 con h2-SNP directo para
jitter/HNR. Si aparece, reemplaza el valor conservador.

## Representacion del genotipo sintetico -- Opcion A

Por parametro: `score_total = score_genetico + score_ambiental`, con
`score_genetico ~ N(0, h2)` y `score_ambiental ~ N(0, 1-h2)`.

Se decidio NO simular SNPs individuales (Opcion B) en esta primera version,
para no consumir tiempo de la Fase 2 en el parseo de 1000 Genomes. Si
sobra margen mas adelante, la variante rs11046212-T de *ABCC9* (AF ~47.7%
en Europa, efecto +2.1 Hz/alelo segun Gisladottir et al. 2023) queda como
candidata para una version mas fiel de f0_medio especificamente.

## Factores excluidos del alcance
Pubertad, envejecimiento, trauma/lesion nerviosa, enfermedad, tabaquismo,
entrenamiento vocal aprendido, trastornos funcionales. Todos quedan absorbidos
en el termino ambiental por construccion -- ver `factores-no-geneticos-voz.md`.
