# Columna vertebral — proyecto Anima

Una sola cohorte de individuos que los tres módulos comparten, para que el
ΔR² de Rostro, Voz y Temperamento se pueda comparar entre sí.

## Por qué

La hipótesis del TFC es un gradiente: el genotipo informa más sobre rostro
que sobre voz, y más sobre voz que sobre temperamento. Para demostrar un
gradiente hay que comparar los tres ΔR² entre sí, y eso exige un intervalo
de confianza sobre la *diferencia*. Un IC sobre una diferencia se calcula
con bootstrap pareado, y pareado significa que el individuo 1 de Rostro es
el mismo individuo 1 de Voz y de Temperamento.

Si cada módulo arma su propia cohorte, los tres números existen pero no se
pueden comparar.

## Qué es de quién

La columna vertebral tiene **solo** los individuos: id, subpoblación, sexo,
edad y a qué partición cae cada uno. Nada de rostro, voz ni temperamento.

Cada módulo sigue siendo dueño de todo lo suyo:

| Módulo | Lo que sigue siendo propio |
|---|---|
| Rostro (Audrey) | el PCA de 28 componentes, el h² de Xiong, BRIM, su calibración |
| Voz (Diego) | los 8 parámetros source-filter, el h² de Gisladottir, su síntesis |
| Temperamento (Tomás) | los 5 rasgos Big Five, el h² de Schwaba, la correlación entre rasgos |

Lo único que cambia en cada módulo es de dónde salen los individuos: en vez
de generarlos, los lee.

## Versión 1.1 (22/10/2026)

| Cambio | Antes (1.0) | Ahora (1.1) |
|---|---|---|
| Subpoblaciones | Sorteadas con las proporciones del panel (GBR 376, IBS 413…) | Conteos exactos: CEU 394, FIN 394, GBR 362, IBS 425, TSI 425 |
| Sexo | Sorteado (1.020 / 980) y sin codificación declarada | 1.000 / 1.000, balanceado dentro de cada subpoblación. **0 = mujer, 1 = hombre** |
| Particiones | Al azar, sin estratificar | Estratificadas por subpoblación x sexo: cada estrato a ±1 persona de 50/25/25 |
| Reproducibilidad | Se comparaba regenerando con numpy | Huella SHA-256 del CSV y versión de numpy en los metadatos; `cargar` verifica la huella |
| Contrato | Solo el intervalo al 90 % | Además, `intervalos_<dominio>.csv` con los seis niveles de la hipótesis (50 % a 95 %) |
| Contraste | Dos colas | Una cola por defecto (sección 4.7 del documento integrado); el IC a dos colas se sigue informando |
| Calibración | Un intervalo, una corrida | `barrido_<dominio>.csv` con 20 réplicas; el criterio de ±5 puntos se evalúa sobre la cobertura promedio (opción A) |
| Potencia | Brechas desde 0,015 | Brechas desde 0,005, y `--voz-real` con los 8 h² publicados de Voz |

La versión 1.0 queda en `historico/` para trazabilidad. **Si algún módulo ya
calculó resultados sobre la 1.0, tiene que volver a correrlos sobre la 1.1.**

## Rango de edad (común a los tres módulos)

La edad es uniforme entera entre 18 y 80 años. Es un supuesto de diseño:

- **18**: los tres dominios ya tienen su forma adulta. La forma facial adulta
  aparece después de la pubertad (Kesterke et al., 2016); el estudio de voz
  empieza en 18 años (Gisladottir et al., 2023); los instrumentos de
  personalidad son de adultos.
- **80**: por encima, las poblaciones fuente tienen pocos datos y aparecen
  cambios de la vejez que ningún módulo modela.
- **Uniforme**: da la misma precisión en todas las edades para estimar el
  efecto de la edad. La media de la cohorte (≈49) es más joven que la de las
  fuentes (Voz: 54), y eso se declara.

Cada módulo modela el efecto de la edad sobre sus rasgos y supone que la
heredabilidad de su fuente vale en todo el rango.

## Cómo se usa

Generar la cohorte (una sola vez, ya está hecha):

```bash
python -m anima_spine.spine
```

Produce `cohorte_anima.csv` y `cohorte_anima.meta.json`. **No regenerarla**
sin avisar a los tres: todos los resultados calculados sobre la versión
anterior dejan de ser comparables.

Desde cada módulo:

```python
from anima_spine import spine, predictions

sp = spine.cargar("cohorte_anima.csv")
ids = sp.ids("entrenamiento")   # o "calibracion" / "prueba"

# ... acá va todo lo propio del módulo ...

predictions.exportar(filas, dominio="rostro")
```

Cada módulo exporta `predicciones_<dominio>.csv` con una fila por individuo
de la partición de prueba, por rasgo y por línea base. El formato está en
`predictions.CAMPOS` y se valida con `predictions.verificar`.

Además exporta `intervalos_<dominio>.csv`, con una fila por individuo de
prueba, por rasgo y por nivel nominal (`predictions.NIVELES`: 50, 60, 70, 80,
90 y 95 %). Se valida con `predictions.verificar_intervalos`, y la cobertura
la calcula `predictions.cobertura_por_nivel` contra el `y_real` de las
predicciones:

```python
predictions.exportar_intervalos(filas_intervalos, dominio="voz")
```

Y exporta `barrido_<dominio>.csv`: el módulo se corre completo
`predictions.REPLICAS` veces (20), cada vez con su semilla, y por réplica,
rasgo y nivel se guarda cuántas personas de prueba quedaron dentro de su
intervalo (`n` y `dentro`). La réplica 0 es la corrida principal, la misma de
los otros dos archivos, y `predictions.verificar_barrido` la recuenta de forma
central contra ellos. El criterio de calibración de la hipótesis (±5 puntos en
cada rasgo y cada nivel) se evalúa sobre `predictions.cobertura_promedio`, no
sobre una corrida suelta:

```python
filas = [predictions.fila_barrido(r, semilla, "voz", rasgo, nivel, y, lo, hi)
         for ...]   # una fila por réplica x rasgo x nivel
predictions.exportar_barrido(filas, dominio="voz")
```

Cada réplica tiene que repetir todo lo que depende del azar del módulo: la
generación de los rasgos y el ajuste. La cohorte y las particiones son
siempre las mismas.

Los textos de `linea_base` son exactamente `solo intercepto` y
`ancestria sexo edad` (con espacios). El Anexo C del documento integrado
tiene que usar los mismos.

Cuando los tres exportaron:

```python
from anima_spine import compare
resultados = compare.comparar_lineas_base(preds, rasgos)   # las dos líneas base
for r in resultados.values():
    compare.imprimir(r)
```

El contraste es a una cola por defecto, porque la hipótesis es direccional
(`colas=2` para el criterio a dos colas).

## Las dos líneas base

Los tres módulos reportan contra **las dos**: solo intercepto, y ancestría
+ sexo + edad. Es un número más por rasgo y evita que parte de la diferencia
entre dominios venga de que cada uno comparó contra otra cosa.

## Tests

```bash
pytest tests/test_contrato_compartido.py -q
```

Un módulo que todavía no exportó sale como `skipped`, no como error: cada
uno puede correrlo desde el primer día.

`demo_circuito.py` simula los tres módulos para verificar el circuito
completo. Exporta a propósito una sola línea base, así que hace fallar
`test_reporta_las_dos_lineas_base` — eso es el test funcionando, no un bug.

**Por qué el criterio va sobre el promedio (opción A, 22/10/2026).** En una
sola corrida, con 500 personas de calibración y 500 de prueba, la cobertura
al 50 % tiene un desvío de unos 3 puntos, y exigir ±5 puntos en cada rasgo y
cada nivel falla por azar aunque el modelo sea perfecto (simulado: 85 % de
las veces en Voz, 70 % en Temperamento y casi siempre en Rostro). Promediar
20 réplicas baja ese desvío a menos de 1 punto. En la demo, F0 al 50 % da
44,8 % en la corrida principal y 49,1 % en el promedio.

## Potencia

```bash
python -m anima_spine.power_gradiente            # grilla de brechas, por dominio
python -m anima_spine.power_gradiente --voz-real # Rostro contra los 8 h² publicados de Voz
```

Con la brecha que surge de los valores publicados (0,008), la potencia del
escalón Rostro–Voz es de 0,12 a 0,19 con 500 personas de prueba. Por eso la
hipótesis se formula en dos niveles (22/10/2026): Rostro y Voz por encima de
Temperamento son los contrastes que se afirman; la diferencia Rostro–Voz se
informa con su intervalo, pero no se afirma.

## Supuestos de diseño que hay que documentar en el informe

- 1000 Genomes no tiene edad. La edad se genera uniforme entre 18 y 80: es
  un supuesto de diseño, no un dato.
- El efecto de edad, sexo y ancestría sobre cada fenotipo lo define cada
  módulo y también es un supuesto.
- Los tamaños de subpoblación son los del panel europeo de 1000G (fase 3),
  usados como proporciones. Verificados contra Ensembl: 99, 91, 99, 107 y 107.
- De 1000 Genomes solo se toman esas proporciones: la cohorte no contiene
  genotipos. La sección 4.4.4 del documento integrado tiene que decirlo así.
- Sexo balanceado por diseño (0 = mujer, 1 = hombre).
