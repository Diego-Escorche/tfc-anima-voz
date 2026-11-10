# Módulo de Voz — Proyecto Anima (TFC)

> **Si sos una IA leyendo esto:** este archivo es tu contexto completo. Leelo
> entero antes de escribir código o proponer cambios. Contiene decisiones ya
> tomadas con su justificación — varias parecen "mejorables" a primera vista y
> no lo son. La sección **Qué NO hacer** es la más importante.
>
> **Desde el 23/10/2026 el trabajo sigue el "Brief para IA programadora —
> prototipo autónomo del módulo de Voz"** (20/10/2026). Cuando contradice a
> este README, manda el brief. El README se actualiza completo en la Etapa 8.

---

## 1. Qué es esto en una frase

Un sistema que, dado un genotipo, estima ocho parámetros acústicos de una voz
**junto con su incertidumbre calibrada**, y mide cuánta información aporta
realmente el genotipo por encima de lo que ya se sabría sólo por sexo, edad y
ancestría.

---

## 2. Contexto académico

- **Qué es:** Trabajo Final de Carrera, Ingeniería en Informática, Universidad
  de Belgrano. Defensa: **febrero 2027** (semana del 9 al 15).
- **Proyecto grupal** llamado **Anima**, de tres integrantes, con tres dominios:
  - **Rostro** (morfología facial) — Audrey Barrientos. Repo aparte: `AnimaFace`.
  - **Voz** (parámetros vocales) — **Diego Escorche. Este repo.**
  - **Temperamento** (rasgos de personalidad) — Tomás Varas.
- **Tutor:** Pedro Brest. Hay weeklies de seguimiento.
- Cada integrante entrega un documento individual, pero el código, la cohorte
  compartida, la línea base poblacional y la capa de calibración son trabajo
  conjunto.

### El argumento científico (esto es lo que se defiende)

> **En revisión por el grupo (desde el 19/10/2026).** Con las h² de la S6 leídas
> con la regla agregada, el promedio de Voz (7,1 %) queda a 0,8 puntos del techo
> facial declarado (7,9 %). Cómo queda formulada la hipótesis (tres niveles, dos
> niveles o reordenada) es una decisión pendiente del grupo. **No reescribas el
> párrafo siguiente hasta que se decida.**

Anima no intenta que la reconstrucción se parezca a la persona real. Lo que
demuestra es un **gradiente de tres niveles**: cuánto reduce el genotipo la
incertidumbre fenotípica según el dominio. Mucho en pigmentación, intermedio en
rostro y voz, prácticamente nada en temperamento.

El aporte es **cuantificar y comunicar la incertidumbre**, algo que las
herramientas forenses comerciales (p. ej. Parabon Snapshot) no hacen: devuelven
una predicción puntual sin decir cuánto confiar en ella.

**Consecuencia práctica para quien programe acá:** un ΔR² chico **no es un bug**.
Es el resultado esperado y es el hallazgo. No optimices el modelo para
"mejorarlo".

---

## 3. Estado actual (al 20 de octubre de 2026)

El 19/10 el grupo acotó el alcance: salieron la síntesis de audio, la validación
contra un corpus de audio real y la interfaz web. El cronograma pasó a 150 horas
en 17 semanas (sección 10).

| Componente | Estado |
|---|---|
| Espacio de parámetros con h² de la S6 (regla agregada) | **Hecho** (`parametros.py`, contrastado contra el CSV por `tests/test_parametros.py`) |
| Generador de genotipo sintético | **Hecho** (`genotipo.py`, sólo para tests) |
| Chequeo de entorno | **Hecho** (`tests/test_setup.py`) |
| Casos VZ-01 a VZ-05 y VZ-07 sobre el generador | **Hechos** (`tests/test_generador.py`) |
| Medidor de parámetros desde audio | Escrito, fuera del flujo principal (`extraccion.py`) |
| Migración a `cohorte_anima.csv` | **Pendiente** (semana del 27/10) |
| `predicciones_voz.csv` según el contrato común | **Pendiente** (semana del 27/10, definitivo el 21/12) |
| Modelo heterocedástico | **Pendiente** (24-30/11) |
| Calibración conformal | **Pendiente** (capa de Tomás, 1-7/12) |
| ΔR² contra las dos líneas base | **Pendiente** (primeros resultados el 8/12) |

---

## 4. Arquitectura

```
  Tabla S6 (Gisladottir)              cohorte_anima.csv (compartida, v1.0)
  referencias/*.csv                   id, subpoblación, sexo, edad, partición
        │                             2.000 personas · 1.000 / 500 / 500
        ▼                                          │
  ┌──────────────────────────┐                     │
  │ parametros.py            │                     │
  │ 8 parámetros + h²-SNP    │                     │
  └──────────────────────────┘                     │
        │                                          │
        ▼                                          ▼
  ┌──────────────────────────────────────────────────────────┐
  │ [27/10] rasgos vocales sobre la cohorte compartida        │
  │ por parámetro: score = genético + ambiental (Opción A)    │
  └──────────────────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────────────────┐
  │ [24-30/11] modelo heterocedástico: μ y σ por parámetro    │
  │ contra 2 líneas base: intercepto solo / ancestría-sexo-edad│
  └──────────────────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────────────────┐
  │ [1-7/12] calibración conformal (capa común, de Tomás)     │
  │ cobertura empírica dentro de ±5 pp del 90 % nominal       │
  └──────────────────────────────────────────────────────────┘
        │
        ▼
  predicciones_voz.csv  ──▶  análisis integral de los tres módulos
  (contrato común,           ΔR² por dominio, bootstrap pareado
   partición de prueba)      sobre las mismas personas
```

`genotipo.py` genera su propia cohorte y sirve sólo para los tests del
generador: no reproduce `cohorte_anima.csv`. El CSV compartido es la fuente de
verdad para el modelo y los resultados.

### Contrato de salida

Cada módulo exporta `predicciones_<dominio>.csv`, con una fila por persona de la
partición de prueba, por rasgo y por línea base. Columnas: `individuo_id`,
`dominio`, `rasgo`, `y_real`, `mu`, `sigma`, `lo`, `hi` (con lo ≤ mu ≤ hi),
`mu_base`, `sigma_base` y `linea_base`. La especificación completa está en el
Anexo B de la Práctica 10. El archivo de pruebas de contrato es común a los tres
módulos.

### Archivos

| Archivo | Rol |
|---|---|
| `src/tfc_voz/parametros.py` | Define los 8 parámetros, su h², su IC95 %, su fila de la S6 y el nivel de evidencia |
| `src/tfc_voz/genotipo.py` | Generador sintético (Opción A), sólo para tests |
| `src/tfc_voz/extraccion.py` | Extrae los 8 parámetros de un WAV con parselmouth (fuera del flujo principal) |
| `referencias/tabla-s6-heredabilidades.csv` | Hoja S6_Heritability del material suplementario de Gisladottir et al. 2023 |
| `tests/test_setup.py` | Verifica que el entorno esté bien instalado |
| `tests/test_parametros.py` | Contrasta las h² cargadas contra la S6 |
| `tests/test_generador.py` | Casos VZ-01 a VZ-05 y VZ-07: recuperación de la h², permutación y 20 semillas |
| `decisiones-fase1.md` | Justificación bibliográfica de cada h² y regla de lectura |
| `seguimiento-modulo-voz.md` | Hitos del cronograma de 17 semanas |
| `historico-vctk.md` | Lo que se hizo con audio real antes del 19/10 (fuera de alcance) |
| `SETUP.md` | Instalación paso a paso |

---

## 5. Los 8 parámetros

Separados según la **teoría fuente-filtro** (Fant, 1960): la voz se produce en
dos etapas, una fuente (cuerdas vocales vibrando) y un filtro (el tracto vocal
que le da forma a ese sonido).

**Fuente** — F0 medio, variabilidad de F0, jitter, HNR
**Filtro** — F1, F2, F3, VTL (longitud del tracto vocal)

Todos los h² están en **escala h²-SNP**. Seis vienen de la tabla S6 de
Gisladóttir et al. 2023 y se leen con la **regla agregada de cinco vocales**
(aprobada por Diego el 20/10/2026): la fila medida sobre el conjunto de las
vocales [i, a, ɔ, u, ɛ], no el máximo entre tareas ni entre vocales sueltas.

| Parámetro | h² | IC95 % | Evidencia | Fila de la S6 |
|---|---|---|---|---|
| `f0_medio` | 0.1027 | 0.0335 a 0.1719 | directa | MedianF0_MeasureVowels |
| `f0_variabilidad` | 0.0410 | −0.0303 a 0.1123 | directa | StdF0_MeasureVowels |
| `f1` | 0.0619 | −0.0091 a 0.1329 | directa | MedianF1_MeasureVowels |
| `f2` | 0.1353 | 0.0655 a 0.2051 | directa | MedianF2_MeasureVowels |
| `f3` | 0.0644 | −0.0009 a 0.1297 | directa | MedianF3_MeasureVowels |
| `vtl` | 0.0606 | −0.0090 a 0.1302 | directa | VTL |
| `jitter` | 0.05 | — | **débil** | No está en la S6 (Van Lierde 2005 / Campos et al. 2024) |
| `hnr` | 0.05 | — | **débil** | No está en la S6 (Campos et al. 2024) |

Promedio de las 8: **0,0707**. Cuatro intervalos (f0_variabilidad, f1, f3, vtl)
cruzan el cero. Es lo que reporta la S6, no un error.

**Por qué la regla agregada.** Los valores que estaban cargados antes eran el
máximo de cada medida entre todas las tareas y vocales del estudio: una
envolvente superior, con el mismo sesgo de optimismo que el proyecto declara
combatir. La tarea de lectura no sirve como regla porque F1, F2 y F3 sólo se
midieron en vocales. Los máximos quedan en `H2_MAXIMOS`, sólo para un análisis
de sensibilidad.

**VTL.** Se toma el valor directo de la S6 (0,0606), que ya está en escala
h²-SNP. Reemplaza al valor anterior, que se derivaba de un h² de gemelos (Dediu
et al. 2022) con un factor 1/2 supuesto. Ese supuesto quedó descartado el
20/10: el cociente real entre el valor directo y el de gemelos es 0,23.

**Escala.** Gisladóttir ajustó cada rasgo por edad, IMC, altura y micrófono,
dentro de cada sexo, **antes** de estimar h². O sea que estas h² están por
encima de sexo, edad y altura, no incluidas en ellas.

`decisiones-fase1.md` tiene la justificación completa de cada valor.

---

## 6. Decisiones tomadas (no las deshagas sin hablarlo)

### Opción A: polygenic score simple, no SNPs individuales

```python
score_genetico  ~ N(0, h²)
score_ambiental ~ N(0, 1 - h²)
score_total = genetico + ambiental      # varianza total = 1
```

Se evaluó simular variantes individuales (p. ej. `rs11046212-T` del gen *ABCC9*,
frecuencia ~47,7 % en Europa, efecto +2,1 Hz por alelo) y **se descartó por
cronograma**, no por rigor.

### Cohorte compartida

Los tres módulos usan `cohorte_anima.csv` (2.000 personas, semilla 20261019,
particiones de 1.000 / 500 / 500), para que el contraste entre dominios se pueda
calcular con bootstrap pareado sobre las mismas personas. Los tres informan el
ΔR² contra las mismas dos líneas base. Si el archivo se regenera, todos los
resultados anteriores dejan de ser comparables.

### Los factores ambientales no se modelan individualmente

Fumar, envejecimiento, pubertad, trauma del nervio laríngeo, entrenamiento vocal
(canto/actuación), enfermedad — todos quedan absorbidos en `score_ambiental`
**por construcción**, porque la h²-SNP publicada ya se midió sobre poblaciones
reales que incluyen fumadores, cantantes, etc.

No hace falta código extra para "excluirlos". Ya están excluidos de la señal
genética.

---

## 7. Qué NO hacer

- **No agregues deep learning ni voice cloning neuronal.** Está explícitamente
  fuera de alcance. El enfoque es paramétrico.
- **No vuelvas a sumar `pyworld` ni Flask**, ni armes una interfaz web.
  Salieron del alcance el 19/10/2026. La única síntesis de audio en alcance es
  la vocal sostenida con KlattGrid (parselmouth) del brief del prototipo.
- **No busques ni descargues datasets de audio.** La validación contra audio
  real salió del alcance el 19/10/2026 (ver `historico-vctk.md`).
- **No busques un dataset que empareje genotipo y voz de las mismas personas.**
  No existe públicamente. Eso está documentado como hallazgo científico del
  proyecto, no como una limitación a resolver.
- **No "mejores" el modelo para subir el ΔR².** Un ΔR² chico es el resultado
  esperado: las h² de la voz van del 4 al 14 % por parámetro, con un promedio
  de 7,1 %.
- **No trates el resultado nulo de jitter/HNR como un bug.** Se espera ΔR² ≈ 0
  ahí.
- **No mezcles h² de gemelos con h²-SNP.** Todo el modelo está en escala h²-SNP.
- **No modifiques `cohorte_anima.csv` ni su semilla (20261019).** Es compartida
  por los tres módulos.
- **No uses los rangos de F0 por defecto de Praat** (75-600 Hz) si tocás
  `extraccion.py`. Usá los de `RANGO_F0`, tomados de Gisladóttir et al.

---

## 8. Problemas conocidos

### La h² puede ser fracción de la varianza residual

Gisladóttir estimó la h² sobre rasgos ya ajustados por edad, IMC, altura y
micrófono dentro de cada sexo. Probablemente sea fracción de la varianza
**residual**, no de la total. Si es así, el techo real del ΔR² sobre una línea
base que ya tiene sexo y edad es h² × (1 − R² de la línea base), y aplica igual
a Rostro. Se declara como limitación.

### `extraccion.py` y el tracking de formantes

El medidor se conserva, pero no hay audio real en el alcance. Si se vuelve a
usar: el algoritmo de Praat puede insertar un formante espurio y correr la
numeración. Por eso mide sólo frames sonoros, usa mediana y marca resultados
implausibles en `ParametrosExtraidos.advertencias`.

---

## 9. Cómo correr las cosas

```bash
# activar el entorno virtual primero (ver SETUP.md)

python tests/test_setup.py                        # verificar instalación
pytest                                            # todos los tests (~50 s)
pytest -m "not lento"                             # sin VZ-07 (~3 s)
python src/tfc_voz/parametros.py                  # ver el espacio de parámetros
python src/tfc_voz/genotipo.py                    # generar cohorte de prueba
python informes/generar_informe.py                # informe de estado en PDF
```

El informe de estado lee el avance por fase de `seguimiento-modulo-voz.md`; el
resto del texto se edita en la sección `CONTENIDO` del script antes de cada
informe nuevo. Necesita además `requirements-informes.txt`.

---

## 10. Lo que sigue

Cronograma de 150 horas en 17 semanas (~10 h por semana). El detalle está en
`seguimiento-modulo-voz.md`.

| Fecha | Hito |
|---|---|
| 20-26 oct | Entorno corriendo, h² recargadas, dato bibliográfico entregado al grupo |
| 27 oct-2 nov | Migración a `cohorte_anima.csv` y al contrato de salida |
| 24-30 nov | Modelo heterocedástico terminado y documentado (Tomás lo adapta) |
| 1-7 dic | Calibración aplicada, VZ-10 en verde |
| 8 dic | Primeros ΔR² de Voz |
| **21 dic** | **`predicciones_voz.csv` definitivo: los resultados de Voz cierran acá** |
| 22 dic-4 ene | Fiestas, nada comprometido |
| Enero | Prototipo y las 30 horas de redacción |
| 9-15 feb | Defensa |

Criterio de éxito de la calibración: cobertura empírica dentro de **±5 puntos
porcentuales** del nivel nominal declarado.

---

## 11. Bibliografía central

| Referencia | Para qué |
|---|---|
| Gisladóttir, R. S., et al. (2023). "Sequence variants affecting voice pitch in humans." *Science Advances* 9(23), eabq2969. DOI 10.1126/sciadv.abq2969 | Ancla principal: h²-SNP de voz (tabla S6), variante en *ABCC9* |
| Di et al. (2024), *Communications Biology* | Réplica de la misma variante en 7.654 mujeres chinas Han |
| Dediu et al. (2022), *Human Genetics* | h² de gemelos del tracto vocal. Ya no es la fuente del VTL; sirve para el cociente 0,23 |
| Angelopoulos & Bates (2022) | Conformal prediction (calibración de intervalos) |
| Gneiting et al. (2007) | Calibración y sharpness |
| Hou et al. (2024) / Xu et al. (2025), *Nature Genetics* | CalPred y PredInterval: mismo enfoque metodológico aplicado a riesgo poligénico clínico |
| Johnson, *Acoustic and Auditory Phonetics* (3ra ed.) | Teoría fuente-filtro; cap. 2 tiene la fórmula de los formantes |
| Lammert & Narayanan (2015), *PLOS ONE* | Estimación de VTL a partir de formantes |

---

## 12. Convenciones

- **Idioma:** código y comentarios en español sin acentos (evita problemas de
  encoding); documentación en markdown con acentos normales.
- **Nombres:** los parámetros usan los nombres de `parametros.py`
  (`f0_medio`, `f0_variabilidad`, `jitter`, `hnr`, `f1`, `f2`, `f3`, `vtl`).
- **Semilla:** `genotipo.py` usa por defecto 20261019, la misma de la cohorte
  compartida. Eso unifica el número declarado, pero **no** hace que
  `genotipo.py` genere los mismos datos que `cohorte_anima.csv`. Los barridos
  de 20 semillas usan 20261019 + 0, 1, …, 19.
- **Entregable:** prototipo funcional, no aplicación productiva. No hace falta
  autenticación, base de datos, ni deploy.
