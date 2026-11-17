# model.md — contexto del módulo de Voz para la IA

Reúne en un solo archivo lo que antes estaba en `CLAUDE.md`, `SETUP.md`,
`decisiones-fase1.md`, `seguimiento-modulo-voz.md` e `historico-vctk.md`
(reorganización del 17/11/2026). `CLAUDE.md` sólo importa este archivo, para
que Claude Code lo cargue solo. `README.md` sigue aparte: es la portada del
repositorio y el brief pide actualizarlo en la Etapa 8.

| Sección | Qué tiene | Antes estaba en |
|---|---|---|
| 1. Instrucciones | Cómo trabajar, reglas que no se rompen, orden de precedencia | `CLAUDE.md` y el brief |
| 2. Dónde está cada cosa | Archivos del repositorio y qué queda sólo en disco | `SETUP.md` y el README |
| 3. Entorno | Instalación y cómo correr los tests | `SETUP.md` |
| 4. Decisiones de la Fase 1 | Justificación bibliográfica de cada h² | `decisiones-fase1.md` |
| 5. Seguimiento | Estado del módulo por fase, decisiones tomadas, reemplazos | `seguimiento-modulo-voz.md` |
| 6. Histórico VCTK | Lo que se hizo con audio real antes del 19/10 (fuera de alcance) | `historico-vctk.md` |

---

## 1. Instrucciones

**Orden de precedencia.** Manda el "Brief para IA programadora — prototipo
autónomo del módulo de Voz" y las entregas y respuestas de Diego que lo
actualizan (la más reciente gana). Después, el documento integrado del grupo y
el TFC individual de Diego (los mantiene Claude; Diego pasa los cambios).
Después, este archivo. Si este archivo contradice al brief, se corrige este
archivo. **Leé `README.md` completo** antes de escribir código o proponer
cambios: tiene el contexto académico, la arquitectura y la sección **"Qué NO
hacer"**.

Puntos críticos, en corto:

- Lo que se defiende es la **cuantificación de incertidumbre**, no la precisión
  de la reconstrucción. Un ΔR² chico es el resultado esperado, no un bug.
- Nada de deep learning ni voice cloning: el enfoque es paramétrico.
- No existe un dataset público que empareje genotipo y voz de las mismas
  personas. Es un hallazgo documentado, no un problema a resolver.
- Los h² de gemelos y los h²-SNP están en escalas distintas y no se mezclan.

Cómo se trabaja (brief y entregas de Diego):

- Diego Escorche es el dueño del módulo: decide el diseño; la IA lo implementa.
- **Una etapa o un punto por vez.** Al cerrar cada uno, `pytest` completo y un
  resumen de los archivos tocados. **Un commit por paso**, en español. No se
  empieza el siguiente sin que Diego lo confirme.
- **Ante una decisión de diseño que no esté en el brief, parar y preguntar.**
- **Si un test falla, no se ajusta la tolerancia sin diagnóstico** y no se cambia
  la semilla para que pase: se muestra el fallo y el diagnóstico.
- **No agregar dependencias** (sólo las de `requirements.txt`). Nada de pyworld,
  Flask, statsmodels ni scikit-learn sin preguntar.
- **No buscar ni descargar datasets.** Los genotipos de las tres variantes los
  pasa Diego como archivo (`datos/`).
- **No tocar `anima_spine/`** (paquete del grupo, se copia sin modificar) ni
  `cohorte_anima.csv` ni su semilla 20261019.
- **Los niveles declarados (h²) viven sólo en `config/niveles_declarados.json`.**
  Ningún `.py` los escribe a mano; `tests/test_niveles.py` lo controla. Se fijan
  antes de correr y no se eligen mirando resultados.
- **Las tolerancias de los criterios se fijan contra una simulación del nulo,
  antes de ver la corrida real**, y nunca se ajustan después de verla.
- Código y comentarios en español, sin tildes en los identificadores. Python
  3.11 o 3.12.

Cómo se mantiene la sección 5 (seguimiento): refleja el estado, no decide nada.
Se actualiza al cerrar cada paso, en el mismo commit, y cada vez que Diego
avisa una decisión; siempre se cambia la fecha de "Última actualización". No se
registran decisiones que no estén en el brief o que Diego no haya confirmado.
No se borra historia: lo reemplazado va a "Reemplazado el …", con la fecha.

Informes para el manager: `informes/avance-bloque-N.md`, actualizado al cerrar
cada semana. **La carpeta `informes/` es local** (está en `.gitignore` desde el
17/11): Diego pasa los informes a mano.

---

## 2. Dónde está cada cosa

```
tfc-anima-voz/
├── CLAUDE.md                  # importa model.md
├── model.md                   # este archivo
├── README.md                  # portada y contexto completo (se actualiza en la Etapa 8)
├── pyproject.toml             # pytest: pythonpath = src y la raiz; marker "lento"
├── requirements.txt
├── .gitattributes             # cohorte y genotipos sin conversion de finales de linea
├── anima_spine/               # paquete comun del grupo (2.2.1), copiado sin modificar
├── cohorte_anima.csv          # cohorte 2.0 congelada (+ .meta.json con la huella)
├── config/
│   └── niveles_declarados.json  # caso base, segundo nivel, criterio de recuperacion
├── datos/
│   └── genotipos_voz_1000g.csv  # 3 variantes x 503 personas reales (+ .meta.json)
├── referencias/
│   └── tabla-s6-heredabilidades.csv
├── src/tfc_voz/
│   ├── parametros.py          # los 8 parametros (h2 leidas de la configuracion)
│   ├── niveles.py             # cargador de la configuracion de niveles
│   ├── cohorte.py             # envoltorio de spine.cargar (reemplazable)
│   ├── poblacion.py           # efectos de sexo, edad y subpoblacion, con su fuente
│   ├── variantes.py           # g_conocida desde las tres variantes publicadas
│   ├── fenotipo.py            # modelo generativo y oraculo
│   ├── modelo.py              # maxima verosimilitud de media y log-desvio
│   ├── lineas_base.py         # las dos lineas base y el modelo completo
│   ├── replicas.py            # tabla predictiva y replicas
│   ├── metricas.py            # R2, DeltaR2, CRPS, bootstrap (sin cobertura)
│   ├── recuperacion.py        # recuperacion_voz.csv y criterio de recuperacion
│   ├── salida.py              # los tres archivos del contrato (reemplazable)
│   ├── genotipo.py            # generador viejo (Opcion A); su retiro se decide en la Etapa 8
│   └── extraccion.py          # medidor de los 8 parametros sobre un WAV
├── scripts/
│   ├── exportar_para_calibracion.py  # archivo para la capa de calibracion de Tomas
│   ├── calcular_segundo_nivel.py     # V por subpoblacion, se corre una vez
│   ├── simular_nulo.py               # simulacion del nulo del criterio
│   └── prueba_sintesis.py            # factibilidad de la sintesis (Etapa 0)
├── tests/                     # un archivo por modulo; test_setup.py se corre aparte
└── informes/                  # LOCAL, fuera de git: avances, archivos entregados y sus .meta.json
```

---

## 3. Entorno

Verificado en Windows 11 con Python 3.12.4, en un venv instalado sólo con
`requirements.txt`. Todas las librerías traen paquetes precompilados.

**1. Python 3.11 o 3.12.** En Windows, si `python --version` abre la Microsoft
Store, ese `python` es un acceso directo: usar el launcher `py` (`py -0p` lista
las versiones, `py -3.12 --version`). En macOS/Linux, `python3 --version`.

**2. Entorno virtual**, parado en `tfc-anima-voz`:

```
py -3.12 -m venv .venv          # Windows
python3.12 -m venv .venv        # macOS / Linux
```

Activarlo con `.venv\Scripts\Activate.ps1` (PowerShell; si se queja de la
política de ejecución, `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
una vez), `.venv\Scripts\activate.bat` (CMD) o `source .venv/bin/activate`.
Sin activar, se puede llamar directo a `.venv\Scripts\python.exe`. Si algo se
rompe, se borra `.venv` y se rehace.

**3. Librerías**

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**4. Chequeo y tests**

```
python tests/test_setup.py          # tiene que terminar en "Entorno listo."
python -m pytest                    # todo, unos 4 minutos
python -m pytest -m "not lento"     # sin VZ-07, alrededor de 1 minuto
```

El último chequeo de `test_setup.py` es el importante: confirma que
parselmouth estima bien el pitch de una señal conocida (~150 Hz), no sólo que
se importa. En la consola de Windows conviene `PYTHONIOENCODING=utf-8` para los
scripts que imprimen tildes.

| Síntoma | Causa casi segura |
|---|---|
| `no se encontro Python; ... Microsoft Store` | `python` es el acceso directo de la Store. Usar `py -3.12` |
| `execution of scripts is disabled` (PowerShell) | Ver `Set-ExecutionPolicy` arriba, o usar `.venv\Scripts\python.exe` |
| `pip` instala pero `import` falla | Se está usando otro Python, no el del entorno virtual |
| `ModuleNotFoundError: tfc_voz` al correr pytest | Correr pytest parado en la raíz, donde está `pyproject.toml` |
| El pitch estimado no da ~150 Hz | parselmouth roto. Reinstalar `praat-parselmouth` |

---

## 4. Decisiones de la Fase 1 (justificación de las h²)

**Actualizado:** 20/10/2026 (regla de lectura de la S6 y VTL directo).

### Espacio de parámetros y heredabilidad

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
que los valores cargados coincidan con ese CSV. **Desde el 9/11 los valores viven sólo en
`config/niveles_declarados.json`** (nivel `caso_base`); `parametros.py` los lee de ahí.

#### Regla de lectura de la S6 (adoptada el 20/10/2026)

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

#### Escala de las h²

Gisladóttir log-transformó cada rasgo y lo ajustó por edad, IMC, altura y
micrófono, por separado dentro de cada sexo, **antes** de estimar h². Estas h²
están entonces por encima de sexo, edad y altura, no incluidas en ellas. Esto
desarma la afirmación de que la línea base poblacional ya captura casi toda la
señal heredable de la voz.

Queda abierto si la h² es fracción de la varianza residual y no de la total. Si
es así, el techo del ΔR² sobre una línea base con sexo y edad es
h² × (1 − R² de la línea base), y aplica igual a Rostro.

#### VTL: valor directo de la S6

La fila VTL de la S6 mide el largo del tracto vocal (medida agregada de F1 a F4
sobre las cinco vocales) directamente en escala h²-SNP: **0.0606**
(IC95 % −0.009 a 0.130).

Hasta el 20/10/2026 el VTL estaba cargado como "derivado": se tomaba el h² de
gemelos de Dediu et al. 2022 (SVTh = 0.26) y se lo dividía por dos, con un
factor 1/2 supuesto por el proyecto. Con el valor directo, ese supuesto queda
descartado: el cociente real entre h²-SNP y h² de gemelos es 0.0606 / 0.26 =
**0,23**, no 0,5. El VTL estaba sobreestimado al doble.

#### Jitter y HNR (0.05, evidencia débil)

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

#### Pendiente menor

Confirmar si existe algún estudio posterior a 2024 con h²-SNP directo para
jitter/HNR. Si aparece, reemplaza el valor conservador.

### Representación del genotipo sintético — Opción A

> **Superado el 9/11 (punto 7 de la entrega):** desde entonces g = g_conocida + g_resto. La parte
> conocida sale de las tres variantes de la tabla S8 (rs11046212, rs369031872 y rs113499791), con los
> genotipos reales de las 503 personas de 1000 Genomes en `datos/` y sorteados en las simuladas;
> el resto sigue siendo la Opción A, con varianza h² − V. Ver `src/tfc_voz/variantes.py`. Lo de abajo
> queda como historia.

Por parámetro: `score_total = score_genetico + score_ambiental`, con
`score_genetico ~ N(0, h²)` y `score_ambiental ~ N(0, 1-h²)`.

Se decidió NO simular SNPs individuales (Opción B), para no consumir tiempo en
el parseo de 1000 Genomes. Si sobra margen más adelante, la variante
rs11046212-T de *ABCC9* (AF ~47.7 % en Europa, efecto +2.1 Hz/alelo según
Gisladóttir et al. 2023) queda como candidata para una versión más fiel de
f0_medio específicamente.

### Factores excluidos del alcance

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

---

## 5. Seguimiento del módulo

**Última actualización:** 17 nov 2026
**Estado general:** el alcance vigente es el del documento integrado del grupo. La síntesis de audio volvió al alcance: vocal sostenida con KlattGrid (parselmouth), VZ-08 vigente y VZ-09 retirado. La interfaz web la arma el grupo; el módulo expone `muestrear` y `sintetizar`. La validación contra audio real sigue afuera. El trabajo sigue el "Brief para IA programadora — prototipo autónomo del módulo de Voz", que manda sobre este archivo. Hecho al 9/11: Fases 1 y 2 completas. El bloque 2 arrancó el 9/11 con la entrega de Diego (paquete `anima_spine` 2.2 y cohorte 2.0); la Etapa 3, prevista para la semana del 3/11, quedó corrida a la semana del 9/11. Desde el 3/11 la hipótesis es la reformulada: por dominio, que el modelo recupera el nivel de señal declarado; ningún contraste entre dominios se afirma.

**Riesgo principal:** que el código no arranque. Venía sin avance desde fines de septiembre; la semana 1 es a propósito el hito más barato.

**Los resultados de Voz cierran el 21 de diciembre, no en febrero.** Enero queda para el prototipo y las 30 horas de redacción, con los números ya quietos.

---

### Fase 1 — Entorno y h² recargadas (20 oct – 26 oct)
- [x] Limpieza del alcance del 19/10: VCTK, `corpus.py`, `pyworld` y Flask fuera, documentados en la sección 6 de `model.md`
- [x] `tests/test_setup.py` en verde en un venv nuevo (Python 3.12.4, sólo `requirements.txt`) — brief del 20/10, tarea 1
- [x] h² recargadas con la regla agregada de cinco vocales, contrastadas contra la S6 (promedio 0,0707) — brief del 20/10, tarea 2
- [x] Casos VZ-01 a VZ-05 y VZ-07 sobre el generador, semilla 20261019 (51 tests en verde) — brief del 20/10, tarea 3
- [x] README, SETUP, decisiones y seguimiento actualizados al alcance del 19/10 — brief del 20/10, tarea 4
- [x] Dato bibliográfico con su regla de lectura entregado a Audrey, Tomás y Brest (confirmado por Diego el 23/10)
- [x] Etapa 0: factibilidad de la síntesis con KlattGrid. Pasa: F0 medida 120,00 Hz contra 120 pedidos (23/10, `informes/etapa0-factibilidad-sintesis.md`)

### Fase 2 — Cohorte compartida y contrato de salida (27 oct – 2 nov)
- [x] Columna vertebral `anima_spine` 1.1 en el repo: `cohorte_anima.csv` v1.1 (no la v1.0), congelada con huella SHA-256; `spine.verificar` pasa (23/10)
- [x] Etapa 1: `cohorte.py` (envoltorio de `spine.cargar`) y `poblacion.py` (efectos de sexo, edad y subpoblación con su fuente); VZ-06 en verde sobre la cohorte real y la generada (23/10)
- [x] Etapa 2: `fenotipo.py`, modelo generativo con heredabilidad residual; h², d, r, c y pendientes de edad recuperados en los 8 parámetros con 200.000 personas (23/10)
- [x] Datos de Voz para la capa de calibración de Tomás: `scripts/exportar_para_calibracion.py` escribe `informes/voz_para_calibracion.csv` (8.000 filas de calibración y prueba, media y desvío oráculo; validación OK). Columnas según la propuesta de Diego a Tomás del 26/10 (26/10)
- [x] VZ-01 a VZ-05 y VZ-07 sobre `fenotipo.py` (decisión del 26/10): VZ-01 a VZ-04 son el test de h² dentro de cada sexo de la Etapa 2; VZ-05 (permutación) y VZ-07 (20 semillas del barrido) agregados. Todos en verde (26/10)
- [x] Formato de salida (adelantado de la Etapa 6): `salida.py` valida con `anima_spine` y escribe tres archivos — predicciones, intervalos en seis niveles y barrido de 20 réplicas; rechaza fila duplicada, nivel faltante y 19 réplicas (29/10)
- [x] Relevamiento de `extraccion.py` (sin cambiarlo) e informe de cierre del bloque, `informes/avance-bloque-1.md`. Diferencias con Gisladóttir: f0_medio con promedio y no mediana, VTL por tubo sobre F1 a F3 (29/10). Las dos se corrigen en la Etapa 7 (decisiones 2 y 5)
- [x] Oráculo movido a `fenotipo.py` (`oraculo`), respuesta del 29/10: el script lo llama y un test confirma que el CSV regenerado es idéntico, byte a byte, al que se le mandó a Tomás (29/10)

### Fase 3 — Modelo heterocedástico (3 nov – 30 nov)
Es el bloque 2 del brief del prototipo. Informe semanal en `informes/avance-bloque-2.md`.

Semana del 9/11, en el orden de la entrega de Diego del 9/11 (cada punto habilita al siguiente):
- [x] 1. Paquete `anima_spine` 2.2 en el repo, con la cohorte 2.0 (503 personas de 1000 Genomes y 1.497 simuladas; huella `8203824a…`, coincide con los metadatos). Suite del paquete: 43 pasan, 16 salteadas (contrato de módulos que no exportaron) (9/11)
- [x] 2. Cohorte 1.1 reemplazada por la 2.0 en todo el módulo. `informes/voz_para_calibracion.csv` (hecho sobre la 1.1) retirado por obsoleto; queda en el historial de git (9/11)
- [x] 3. Los ocho h² en un único archivo de configuración, `config/niveles_declarados.json`, cargado por `niveles.py`; `parametros.py` ya no tiene literales y `tests/test_niveles.py` falla si un nivel aparece escrito a mano en un `.py` del módulo (9/11)
- [x] 4. Los dos niveles declarados en esa configuración: caso base (agregado 7,07 %) y segundo nivel por parámetro (V por subpoblación, agregado 0,148 %), los dos como entrada. La composición de la cohorte 2.0 queda registrada al lado; el cargador la verifica y no recalcula. V se calcula una vez con `scripts/calcular_segundo_nivel.py`. `describir` da el renglón del reporte con nivel, archivo, versión, fecha y verificación de la cohorte. Configuración en la versión 1.2 (9/11)
- [x] 5. `informes/voz_para_calibracion.csv` sobre la cohorte 2.0 con las 20 réplicas: 160.000 filas, columnas nuevas `replica`, `semilla`, `dominio` y `sexo`; caso base y puntaje genético enteramente simulado, declarado en `voz_para_calibracion.meta.json`. Validación OK. Se regenera cuando entre el punto 7 (9/11)
- [x] 6. Etapa 3: `modelo.py` (máxima verosimilitud normal, L-BFGS-B con gradiente analítico, error si no converge) y `lineas_base.py` (las dos líneas base y el modelo completo, sólo con entrenamiento). Los 24 modelos convergen sobre la cohorte 2.0, con 42 iteraciones como máximo. Tests de la Etapa 3 y de los ajustes del 29/10 en verde; el de g permutado es frágil (ver `informes/avance-bloque-2.md`) (9/11)
- [x] 7. Variantes conocidas: `variantes.py` y g = g_conocida + g_resto en `fenotipo.py`, con los genotipos de `datos/` en las 503 personas reales y sorteados en las simuladas. VZ-14 (tres partes) y VZ-15 en verde: Var(g_conocida) de f0_medio 0,00627 en la cohorte 2.0 y 0,00608 con 200.000 personas, contra 0,0062. `voz_para_calibracion.csv` regenerado (9/11)
- [ ] 8. `recuperacion_voz.csv` y criterio de recuperación, sobre el caso base. **Parcial (17/11):** `metricas.py`, `replicas.py` y `recuperacion.py` hechos, y la simulación del nulo (200 × 20 réplicas, corrimiento del parcial de −0,0024 a −0,0037) en `informes/simulacion_nulo_voz.csv`. Falta que el grupo fije la tolerancia en la configuración y, recién después, la corrida oficial
- [ ] 9. Análisis de dos niveles

Plan por semanas del 29/10 (se reordena con el brief del 5/11):
- [x] Semana del 3/11 (corrida a la del 9/11; hecha el 9/11) — Etapa 3: `modelo.py` (genérico, máxima verosimilitud normal; verifica la convergencia) y sus tests
- [x] Semana del 10/11 (adelantada al 9/11) — `lineas_base.py`: las dos líneas base y el modelo completo, con los "Ajustes del 29/10" (definiciones compartidas con `fenotipo.py`, test de la línea base 2, test con g permutado)
- [x] Semana del 17/11 — tabla predictiva (16.000 filas, contrato v2 de Tomás) y `correr_replica`, en un archivo nuevo, `replicas.py`, que se suma a la tabla de archivos del README (en la Etapa 8) (17/11)
- [x] Semana del 17/11 — Etapa 5: `metricas.py`, sólo funciones y tests (ΔR² total y parcial, CRPS, bootstrap pareado; sin cobertura, que la cuenta el paquete); VZ-11 a VZ-13 se corren en diciembre (17/11)
- [ ] Semana del 17/11 — control de integración: reemplazado por el criterio de recuperación (12/11), ver el punto 8
- [ ] Semana del 24/11 — adaptador de la Etapa 4 con datos oráculo, sólo si Diego pasó el contrato congelado y la v1 de la capa de Tomás está disponible; si no, pasa a diciembre
- [ ] Modelo terminado y documentado para que Tomás lo adapte (semana del 24-30 nov)
- [ ] Redacción adelantada: metodología y límites (el diseño no depende de resultados)

### Fase 4 — Calibración y primeros ΔR² (1 dic – 8 dic)
- [ ] Etapa 4: `calibracion.py` como adaptador a la capa común de Tomás (`anima_spine/calibracion.py`, contrato v2), sin lógica de calibración propia; con la salida del modelo como entrada
- [ ] VZ-10: cobertura promedio de 20 réplicas dentro de ±5 puntos del nivel nominal en los seis niveles, del 50 % al 95 %
- [ ] Primeros ΔR² de Voz contra las dos líneas base, con IC95 % (VZ-11, VZ-12) — 8 dic

### Fase 5 — Cierre de resultados de Voz (9 dic – 21 dic)
- [ ] VZ-13: tabla de los 8 parámetros ordenados por ΔR² parcial, con el total y la h² inyectada al lado
- [ ] Etapa 6: `prototipo.py` (un comando corre todo el circuito) y `reporte_voz.md`. `--generar-cohorte` con otra composición de subpoblaciones falla (lo verifica `niveles.cargar`); el reporte avisa si la composición no se verificó
- [ ] `predicciones_voz.csv`, `intervalos_voz.csv` y `barrido_voz.csv` definitivos entregados al análisis integral — 21 dic

### Fase 6 — Síntesis de audio y vista vocal (9 dic – 21 dic)
- [ ] Etapa 7: `muestreo.py` (`muestrear`) y `sintesis.py` (`sintetizar`), las funciones que llama la vista vocal del prototipo web
- [ ] Decisiones sobre la síntesis del 23/10 y del 29/10 implementadas (ver "Decisiones tomadas")
- [ ] VZ-08: ida y vuelta, F0 medida a menos de 5 Hz de la pedida en 20 realizaciones de ambos sexos

Corre en paralelo con la Fase 5 y tiene menos prioridad: si el tiempo aprieta, se termina después de VZ-10 a VZ-13 (ventana confirmada por Diego el 23/10).

Del 22 dic al 4 ene: fiestas, nada comprometido.

### Fase 7 — Prototipo y redacción (5 ene – 31 ene)
- [ ] Prototipo conjunto (OE6)
- [ ] Etapa 8: README y seguimiento al cierre del prototipo
- [ ] Redacción del documento individual (30 h, el bloque más grande del plan)
- [ ] Informe de validación consolidado (OE7)
- [ ] Iteración con Pedro Brest (tutor)

### Fase 8 — Defensa (1 feb – 15 feb)
- [ ] Ensayo de defensa
- [ ] Defensa (semana del 9 al 15 feb)

---

### Dependencias con el grupo

| Qué | De quién | Para cuándo | Estado o plan alternativo |
|---|---|---|---|
| `cohorte_anima.csv` congelada | Grupo | 27 oct | **Existe:** v2.0 (mixta: 503 personas de 1000 Genomes y 1.497 simuladas), congelada el 6/11 con huella SHA-256 y copiada al repo el 9/11 con el paquete `anima_spine` 2.2 |
| Línea base heterocedástica (OE2) | Grupo | 24-30 nov | El prototipo arma las dos líneas base en `lineas_base.py`; informar contra una sola si falta |
| Capa de calibración conformal (OE4) | Tomás | Contrato v2 congelado ~31/10; v1 de la capa en noviembre | **Voz usa la capa común de Tomás** (decisión del 27/10): `calibracion.py` es un adaptador sin lógica propia y se conecta con datos oráculo en la segunda quincena de noviembre. Plan B, sólo con el visto bueno de Diego: si a fin de noviembre la capa no está, calibración provisoria (split conformal normalizado, ~6 h) detrás de la misma firma del adaptador |
| ΔR² de Rostro y Temperamento sobre la misma cohorte | Audrey y Tomás | 26 ene | El documento individual se sostiene con el ΔR² de Voz y su IC |

La capa de calibración tiene que ser agnóstica del modelo (recibe μ y σ, devuelve el intervalo): Tomás la entrega a mediados de noviembre y el modelo de Voz recién está el 30.

### Decisiones tomadas

- **20/10 — Regla de lectura de la S6:** regla agregada de cinco vocales (Diego).
- **20/10 — Codificación de sexo:** 0 = mujer (referencia), 1 = hombre. Adoptada por el paquete común.
- **22/10 — Hipótesis en dos niveles:** Rostro y Voz contra Temperamento. El escalón Rostro–Voz se informa, pero no se afirma.
- **22/10 — Criterio de cobertura:** se evalúa sobre el promedio de 20 réplicas (opción A del grupo).
- **23/10 — Decisiones sobre la síntesis** (brief del prototipo, Etapa 7; aprobadas por Diego):
  1. **Medición de formantes:** `extraccion.py` recibe `n_formantes`, con 5 por defecto (configuración de Gisladóttir). VZ-08 mide el audio sintético con 4. Es un ajuste propio de medir audio sintético.
  2. **VTL con una sola definición:** espaciado de formantes sobre F1 a F4, como Gisladóttir, con c = 35.300 cm/s, tanto al medir como al sintetizar. Con 4 formantes, el VTL medido tiene un sesgo esperado de +3 % a +6 %.
  3. **Corrección iterativa** de jitter, variabilidad de F0 y HNR: hasta 3 iteraciones por realización, con el error residual informado. Plan B (pulsos con períodos exactos) sólo con aprobación de Diego.
- **23/10 — Semilla por parámetro:** el índice de `default_rng([semilla, indice])` es fijo por nombre (f0_medio 0, f0_variabilidad 1, jitter 2, hnr 3, f1 4, f2 5, f3 6, vtl 7). Un parámetro nuevo recibe el número siguiente, así que reordenar no cambia los valores (Diego).
- **23/10 — Ventana de la síntesis:** 9 a 21 dic, en paralelo con el cierre de resultados (Diego).
- **23/10 — Respuestas al avance del bloque 1** (brief del prototipo, "Respuestas al avance del 23/10"):
  - **Tests "a edad fija" de la Etapa 2:** se adopta la propuesta de `informes/propuesta-tests-edad-fija.md`, con un cambio: r y c se estiman de los residuos sin usar el c verdadero, y c suma un test propio.
  - **Fuentes de f0_medio en `poblacion.py`:** b_hombre = 0 y q_mujer quedan como "derivado", anotados como lectura de Gisladóttir (el cambio de los hombres empieza a los 60; el de las mujeres termina a los 60).
  - **`salida.py`:** las tres funciones reciben el DataFrame de `leer_cohorte` y toman de ahí los ids de prueba.
  - **Escala de `f0_variabilidad`:** si `extraccion.py` la da en Hz, la escala del módulo es el logaritmo de ese valor (se confirma en el relevamiento).
  - **Desvíos aprobados:** `n` en `generar_cohorte`, `pyproject.toml`, `.gitattributes` y `.gitignore`, y el criterio de tipos de fuente.
- **26/10 — Respuestas al avance del 26/10** (brief del prototipo, "Respuestas al avance del 26/10"):
  - **Media y desvío de referencia:** verificados contra las tablas originales (Gisladóttir S2_Means; Goy et al. 2013, tabla 3). Las fuentes informan en unidades físicas; los valores del brief son su conversión a logaritmo por momentos lognormales. Son "derivado", salvo hnr ("dato", ya en dB). Cada fuente anota fila, media, DE y fórmula; un test las recalcula.
  - **ΔR² parcial:** VZ-11 y VZ-13 informan, contra `ancestria sexo edad`, el ΔR² total y el parcial, (R² completo − R² base) / (1 − R² base), cada uno con su IC95 % por bootstrap pareado con los mismos remuestreos. **VZ-13 se ordena por el parcial.** Contra `solo intercepto`, sólo el total. Se implementa en la Etapa 5. El contraste entre dominios (`anima_spine/compare.py`) lo decide el grupo; no se toca el paquete.
  - **Casos VZ sobre `fenotipo.py`:** VZ-01 a VZ-04 pasan a ser el test de h² dentro de cada sexo de la Etapa 2, y se agregan VZ-05 (permutación) y VZ-07 (20 semillas, 20261019 + r) sobre `fenotipo.py`, con los mismos criterios. `genotipo.py` y sus tests quedan; si se retiran, se decide en la Etapa 8.
- **27/10 — Calibración con la capa común de Tomás** (brief del prototipo, Etapa 4): Voz no escribe una calibración propia. Usa `anima_spine/calibracion.py` (contrato v2 del 27/10, que se congela alrededor del 31/10). `calibracion.py` del módulo es un adaptador sin lógica de calibración; el intervalo al 90 % de `predicciones_voz.csv` sale de la salida de la capa en nivel 0,90. Lo que la capa no resuelva se anota como pedido para Tomás. Plan B (calibración provisoria) sólo si la capa no está a fin de noviembre y con el visto bueno de Diego.
- **29/10 — Ajustes de la Etapa 3** (brief del prototipo, "Ajustes del 29/10"): `lineas_base.py` usa `edad_centrada` y `tramo60` de `fenotipo.py`; se mantiene el término g · edad_c; `ajustar` levanta un error si el optimizador no converge; tests de la línea base 2 y con g permutado; `tabla_predictiva` (16.000 filas, columnas del contrato v2, oráculo reusado de `fenotipo.oraculo`); `correr_replica(cohorte, r)`; control de integración del ΔR² parcial sobre 20 réplicas (tolerancia 0,025).
- **29/10 — Unidad del jitter en la síntesis** (decisión 4 de la Etapa 7, sobre la observación del 26/10): `muestrear` devuelve el jitter en %; se convierte a fracción en un solo lugar, al entrar a `sintetizar`; la tabla de VZ-08 compara en la misma unidad y la declara; un test verifica que 0,37 % entra como 0,0037.
- **29/10 — Plan del bloque 2** (3 al 30 de noviembre): una semana por paso (modelo; líneas base; tabla predictiva, réplicas, métricas y control de integración; adaptador con datos oráculo). Si una semana se atrasa no se comprime la siguiente: se avisa en `informes/avance-bloque-2.md` y Diego decide.
- **29/10 — Respuestas al avance del 29/10** (brief del prototipo, "Respuestas al avance del 29/10"):
  - **Decisión 5 de la síntesis:** en el mismo cambio de `extraccion.py` de la Etapa 7, f0_medio pasa a la mediana de los frames sonoros (como `MedianF0`) y el paso de los formantes se fija en 0,01 s. El paso del pitch queda como está. Después, pytest completo y prueba de la Etapa 0 (F0 a menos de 5 Hz).
  - **`replicas.py`:** `tabla_predictiva` y `correr_replica` van en un archivo nuevo; `lineas_base.py` sólo arma los modelos.
  - **Oráculo en `fenotipo.py`:** el script lo llama; un test confirma que el CSV regenerado es idéntico al enviado a Tomás.
  - **Error de convergencia:** `modelo.py` levanta un error genérico con el mensaje del optimizador y `lineas_base.py` lo vuelve a levantar nombrando el parámetro y el modelo.
  - **Contrato y capa de Tomás:** si no llegan para la semana del 24/11, el adaptador pasa a diciembre.
  - **Desvíos de `salida.py` aprobados.** `predictions.verificar` no exige las dos líneas base; se corrige en `anima_spine` 1.2 y, hasta entonces, el control propio de `salida.py` queda.

- **1/11 — Cohorte 2.0** (grupo; congelada el 6/11): mixta, 503 personas reales de 1000 Genomes y 1.497 simuladas. Es la única cohorte; la 1.1 queda en el histórico y nada se calcula sobre ella. Los rasgos de todas las personas siguen siendo simulados.
- **3/11 — Hipótesis reformulada** (aprobada por el tutor): ningún contraste entre dominios se afirma. Por dominio, el modelo recupera el nivel de señal declarado, con una tolerancia que es un criterio verificable. `compare.comparar` ya no devuelve `hipotesis_dos_niveles`.
- **Entre el 1 y el 5/11 — Dos niveles declarados:** caso base 7,1 % (heredabilidad por variantes comunes, agregado de los ocho parámetros) y segundo nivel 0,15 % (lo que recuperan las tres variantes publicadas). No se elige ni se ajusta ningún nivel mirando resultados.
- **9/11 — Paquete `anima_spine` 2.2:** el criterio de recuperación tiene tolerancia 0,015 (antes 0,005) y se evalúa sobre el caso base; el segundo nivel se informa sin criterio. `predictions.verificar` exige las dos líneas base. Fuera de alcance: el puntaje poligénico de estatura y las dos variantes nuevas del meta-análisis entre poblaciones.

- **9/11 — Respuestas de Diego a las consultas de la entrega:**
  - **Genotipos:** la regla de no descargar datasets sigue en pie. Diego pasa los genotipos de las tres variantes como archivo (`genotipos_voz_1000g.csv`).
  - **CSV del punto 5:** se entrega con el puntaje genético enteramente simulado y el caso base, con una nota que lo declare; se regenera cuando entre el punto 7.
  - **Control propio de `salida.py`** sobre las dos líneas base: se queda, redundante a propósito.
  - **Niveles declarados:** en `config/niveles_declarados.json`. El caso base son las h² de siempre; el segundo nivel es por parámetro (0,006160 en f0_medio, 0,003433 en f2, 0,002247 en f1, cero en el resto), y el 0,148 % es su promedio. Los 0,0500 de jitter y hnr quedan como salvedad a confirmar antes de la entrega final.
  - **Variantes conocidas:** g = g_conocida + g_resto, con g_conocida centrada por la frecuencia de la subpoblación y g_resto con varianza h² − V. VZ-14 (tres partes) y VZ-15 (varianza de g_conocida en f0_medio ≈ 0,0062; si se va por más de un factor de dos, parar). Si la frecuencia observada se aparta más de 10 puntos de la configurada, error, sin corregir.
  - **Recuperación:** `recuperacion_voz.csv` con las funciones del paquete, tolerancia de `predictions.TOLERANCIA_RECUPERACION`, sobre el promedio de 20 réplicas y sólo en el caso base.
  - **Dos niveles:** fenotipos siempre con la g completa y el caso base; el modelo recibe la g completa (caso base) o sólo g_conocida (segundo nivel). Se informa el ΔR² parcial con IC y el angostamiento del intervalo, 1 − √(1 − ΔR² parcial).

- **9/11 — Respuestas de Diego, segunda vuelta:**
  - **Jitter y HNR:** no tienen heredabilidad SNP publicada; el 0,05 es un valor conservador declarado, apoyado en Van Lierde et al. (2005) y Campos et al. (2024). Se cierra como declarado, no como pendiente de verificar. La cita "Lima et al. 2024" era un error: es Campos, Luchesi, Lucci, Otta y Monticelli (2024), *Social Sciences & Humanities Open*, 10, 101062.
  - **Segundo nivel derivado:** V = Σ w_s · 2 · p_s · (1 − p_s) · β², con la misma p por subpoblación que centra g_conocida y w_s la composición de la cohorte, calculada del archivo al cargar. Con la cohorte 2.0: 0,006086 (f0_medio), 0,003436 (f2), 0,002278 (f1); agregado 0,148 %. Así Var(g) = h² exacto. Con el centrado por subpoblación, en el segundo nivel el ΔR² total y el parcial dan casi lo mismo.
  - **Test de literales:** recorre también `tests/`, con exención por línea anotada (`# nivel-literal-ok: <motivo>`). Los ceros del segundo nivel quedan fuera.
  - **CSV de calibración fuera de git:** aprobado, con su `.meta.json` (semilla, versiones, huella) y una regeneración verificada desde un clon limpio.
  - **Genotipos en `datos/`**, no en `anima_spine/datos/`, para no mezclar datos de Voz con el paquete del grupo.

- **9/11 — Respuestas de Diego, tercera vuelta:**
  - **Jitter y HNR:** Campos et al. (2024) no encuentran diferencia entre gemelas MZ y DZ en estos dos parámetros, así que la evidencia apunta a un valor pequeño o nulo. El 0,05 es una cota superior declarada, deliberadamente generosa, para no meter a mano el resultado nulo que el módulo espera. Las cifras atribuidas a Campos (0,374, 0,366, los intervalos) y las iniciales de la primera autora quedan pendientes de verificar: Diego lee el artículo esta semana.
  - **Segundo nivel otra vez como entrada:** calcularlo al cargar haría que el nivel declarado se moviera en silencio con la composición de la cohorte. Los valores (0,006086, 0,003436, 0,002278; agregado 0,001475) son entrada, con la composición de la cohorte 2.0 y su huella registradas al lado. El cargador verifica la composición: si difiere, error con la subpoblación; si falta la cohorte, carga y el reporte lo avisa. Cambiar la composición pasa por la Tabla 7 del documento integrado, no por una línea de comando.

- **10/11 — Actualización de Diego:**
  - **Contrato congelado del archivo para la calibración:** las 10 columnas `replica, semilla, dominio, sexo, individuo_id, particion, rasgo, y_real, mu_oraculo, sigma_oraculo`, 160.000 filas (sólo calibración y prueba), `individuo_id` entero y los ocho nombres de rasgo fijos. El archivo del 9/11 ya cumplía.
  - **Jitter y HNR:** las cifras de Campos et al. (2024) están verificadas contra su tabla 5 (46 pares MZ; 0,374, IC de 0,106 a 0,591, y 0,366, IC de 0,097 a 0,585; p = 0,004). Su grupo DZ es de 10 pares y no distingue genética de ambiente compartido. Salvedad con el texto definitivo (configuración 1.3).
  - **Paquete 2.2.1:** corrige `power_gradiente.py` (el ancla facial de 0,079 no es un techo); no toca `predictions.py`, `compare.py` ni la cohorte. Adoptado el 12/11, con las copias de la 2.2 del proyecto borradas.
  - **VZ-15:** el valor exacto es 0,006086, no "alrededor de 0,0062".
  - **Calibración:** no se construye; la capa es de otra persona y entra en el paquete 2.3. La forma de la sigma de Voz quedó congelada: logaritmo de sigma con sexo y edad centrada, la del modelo heterocedástico. Puede caer una calibración provisoria a fin de noviembre (unas 6 horas); no se empieza ni se deja andamiaje.

- **12/11 — Respuestas de Diego al informe del bloque 2:**
  - **Corrimiento del ΔR² parcial:** por encima con el modelo oráculo (lo que describe el README del paquete 2.2) y por debajo con el modelo estimado, que es el del módulo. La magnitud la da la simulación del nulo con `lineas_base.py`.
  - **Un solo criterio:** el criterio de recuperación reemplaza al control de integración. Su tolerancia se lee de la configuración y se fija una vez con la simulación del nulo, ANTES de ver la corrida real, nunca después.
  - **Tests de los coeficientes de g:** tolerancias de 4 desvíos, fijadas una vez con su derivación: 0,075 (g permutado), 0,055 (g con c = 0) y 0,072 (g · sexo con c = 0).
  - **`replicas.py` y `metricas.py`:** adelantados al punto 8.
  - **Genotipos de las simuladas:** se sortean de nuevo en cada réplica; las 503 reales tienen siempre los del archivo. La asimetría queda declarada en el `.meta.json` del CSV de calibración.
  - **Cobertura:** no va en `metricas.py`; la cuenta el paquete. VZ-10 y el `lo`/`hi` al 90 % esperan a la capa de calibración.
  - **Di et al. (2024):** sólo un control de orden de magnitud para VZ-15, no una validación.

### Decisiones pendientes del grupo (bloquean)

- [ ] Con qué criterio se eligen las h² en los tres módulos. Queda vinculado a las decisiones 2 y 3 del documento integrado; Rostro mantiene 7,9 % por ahora

### Datos a averiguar

- [x] Tabla S6 de Gisladóttir — en `referencias/tabla-s6-heredabilidades.csv`
- [ ] Criterio con el que se eligieron las h² de Rostro y de Temperamento
- [ ] Si el 7,9 % y el 2,89 % de Rostro están medidos sobre `cohorte_anima.csv`
- [ ] Calendario de entregas de la cátedra después de la Práctica 10 (las semanas que coincidan bajan a la mitad)
- [ ] Política de propiedad del código
- [ ] Elegibilidad de cada uno para la defensa de febrero (el único riesgo que no se arregla con horas)
- [ ] (menor) Algún estudio post-2024 con h²-SNP directo para jitter/HNR

### Riesgos de la síntesis de audio

Salieron de la Etapa 0 (23/10; tablas en `informes/etapa0-factibilidad-sintesis.md`). Los cinco quedaron **decididos el 23/10 y se implementan en la Etapa 7**: ver "Decisiones sobre la síntesis (23/10)" en "Decisiones tomadas".

- **El medidor de formantes falla sobre la vocal sintética** (con 5 formantes, F2 y F3 salen mal numerados). → Decisión 1: VZ-08 mide con 4 formantes.
- **El VTL no podía hacer ida y vuelta** (la síntesis lo usaba para F4 y F5; el medidor, sobre F1 a F3). → Decisión 2: una sola definición, por espaciado de formantes sobre F1 a F4.
- **El flutter mueve a la vez el jitter y la variabilidad de F0.** → Decisión 3: no usar flutter; un punto de pitch por período, más corrección iterativa.
- **El ruido de aspiración empeora la medición de formantes y el HNR está acoplado al jitter.** → Decisiones 1 y 3: formantes medidos con 4 y HNR ajustado por corrección iterativa.
- **La variabilidad de F0 necesita un contorno.** → Brief, Etapa 7: suma de 3 senoidales lentas (0,5 a 3 Hz), ajustada por corrección iterativa.
- **El jitter está en % en la referencia y en fracción en el medidor** (observación del 26/10). → Decisión 4 (29/10): conversión en un solo lugar, al entrar a `sintetizar`.

### Correcciones del documento individual (.docx)

Sección cerrada el 23/10: las cuatro correcciones están hechas. El documento lo mantiene Claude, así que esta sección no se vuelve a usar.

- [x] Sacar la afirmación de que la línea base ya captura casi toda la señal heredable de la voz
- [x] Reemplazar el plan de ocho fases por el cronograma de 17 semanas
- [x] Sacar el corpus de audio de Herramientas (queda sólo la atribución de Praat, vía `parselmouth`)
- [x] Sección 1.2: falta un punto o un guión después de "en 3D"

---

### Reemplazado el 17/11

- **Archivos de contexto (pedido de Diego del 17/11):** `CLAUDE.md`, `SETUP.md`, `decisiones-fase1.md`, `seguimiento-modulo-voz.md` e `historico-vctk.md` pasaron a ser las secciones de `model.md`; `CLAUDE.md` sólo lo importa. El seguimiento es ahora la sección 5, y sus fases quedaron un nivel más abajo (`### Fase N — nombre (inicio – fin)`). La sección "(Opcional) Informes de estado en PDF" de `SETUP.md` se retiró junto con `informes/generar_informe.py` y `requirements-informes.txt`.
- **`informes/` en git:** desde el 17/11 la carpeta es local y está en `.gitignore`. Se borraron el PDF del 13/10 y las dos propuestas ya resueltas (`propuesta-tests-edad-fija.md` y `propuestas-23-10-etapa2.md`), que siguen en el historial de git.

- **Tolerancias del brief para los coeficientes de g:** 0,02 (g permutado) y 0,03 (g y g · sexo con c = 0). Quedaban a 1–2,8 desvíos; desde el 12/11, 4 desvíos.
- **Control de integración del 29/10:** ΔR² parcial promedio a menos de 0,025 de la h², con un corrimiento esperado de 0,002 a 0,004 por debajo. Reemplazado por el criterio de recuperación, con la tolerancia que fije la simulación del nulo.
- **Punto 8 con "tolerancia 0,015":** la del paquete 2.2 se revisa con la simulación del nulo y se lee de la configuración.

### Reemplazado el 9/11

- **Niveles declarados 1.1:** el segundo nivel se derivaba al cargar, con la composición de la cohorte cargada, y los valores del JSON eran control (tolerancia 0,0002). Desde la 1.2 son entrada y la composición se verifica.
- **Salvedad de jitter y HNR (1.2):** "la evidencia de gemelos es débil y apunta a un valor pequeño o nulo… Campos et al. (2024) encuentran que las gemelas monocigóticas no se diferencian de las dicigóticas". Desde la 1.3, con el artículo verificado: su grupo DZ de 10 pares no permite distinguir genética de ambiente compartido.
- **Salvedad de jitter y HNR (1.1):** "valor conservador de 0,05, apoyado en estudios de gemelos (Van Lierde et al., 2005; Campos et al., 2024)". Desde la 1.2, cota superior declarada; la evidencia apunta a un valor pequeño o nulo.
- **Niveles declarados 1.0:** el segundo nivel era configurado, calculado con la frecuencia europea promedio (0,006160, 0,003433 y 0,002247). Desde la 1.1 es derivado por subpoblación y esos valores son control.

- **Fase 2:** "Columna vertebral `anima_spine` 1.1 en el repo: `cohorte_anima.csv` v1.1". Desde el 9/11 el paquete es el 2.2 y la cohorte, la 2.0.
- **Fase 2:** "Oráculo movido a `fenotipo.py`: un test confirma que el CSV regenerado es idéntico al que se le mandó a Tomás". Ese CSV era de la 1.1 y quedó obsoleto; el test se retiró y el archivo se regenera sobre la 2.0 (punto 5 de la entrega).
- **Dependencias:** la fila de la cohorte decía "v1.1 del paquete `anima_spine`, copiada al repo el 23/10".
- **Decisiones pendientes:** "Qué afirma el TFC: un gradiente entre dominios, o que la maquinaria funciona y cómo responde a la heredabilidad". Resuelta el 3/11 con la hipótesis reformulada.

### Reemplazado el 29/10

- **Fase 3:** "Etapa 3: `modelo.py` y `lineas_base.py`" y "Etapa 5: `metricas.py` …" en dos renglones. Pasaron a un renglón por semana del bloque 2.
- **Fase 4:** "Etapa 4: calibración provisoria, split conformal normalizado (reemplazable por la capa de Tomás)". Desde el 27/10, `calibracion.py` es un adaptador a la capa común; la provisoria quedó como plan B.
- **Fase 5:** "VZ-13: tabla de los 8 parámetros ordenados por ΔR²". Desde el 26/10 se ordena por el ΔR² parcial.
- **Dependencias:** la fila de la capa de calibración decía "El prototipo usa una provisoria (`calibracion.py`, reemplazable)", con fecha 1-7 dic.
- **Decisiones, ajustes de la Etapa 3:** "oráculo reusado de `exportar_para_calibracion.py`". Desde la respuesta del 29/10, el cálculo vive en `fenotipo.oraculo` y el script lo llama.

### Reemplazado el 23/10

- **Estado general del 20/10:** "el 19/10 se acotó el alcance (afuera: síntesis de audio, validación contra audio real e interfaz web)". La síntesis volvió al alcance con el documento integrado.
- **Fase 2:** "Migrar a `cohorte_anima.csv` v1.0". La cohorte vigente es la v1.1.
- **Fase 2:** "Primer `predicciones_voz.csv` que pase las pruebas de contrato comunes". Se exportan tres archivos, no uno.
- **Fase 3:** las tareas 5a y 5b del brief del 20/10 (`modelo.py` y `metricas.py`) pasaron a ser las Etapas 3 y 5 del brief del prototipo. "Las dos líneas base (OE2, del grupo)" pasó a `lineas_base.py`.
- **Fase 4:** "VZ-10 en verde (cobertura dentro de ±5 pp del 90 %)". Ahora es el promedio de 20 réplicas en seis niveles.
- **Fases 6 y 7** (prototipo y defensa) pasaron a ser las 7 y 8, por la fase nueva de síntesis.
- **Decisión pendiente cerrada el 22/10:** "Cómo queda formulada la hipótesis: tres niveles, dos niveles o reordenada".
- **Riesgos de la síntesis:** anotados como abiertos el 23/10 y decididos ese mismo día.

### Antes del 20/10: plan de ocho fases (reemplazado)

- **Fase 1 del plan viejo** cerrada el 12 oct: 8 parámetros, generador de cohorte, medidor y entorno.
- Lo que se hizo con audio real entre el 12 y el 13 oct salió del alcance el 19/10. Está documentado en la sección 6 de `model.md`.
- Secciones del documento individual adelantadas: portada, resumen e índice, y de 1.1 a 1.7 (problemática, antecedentes, alcance, hipótesis, supuestos, limitaciones y herramientas).

---

**Cómo usar este archivo:** refleja el estado del módulo, no decide nada; si contradice al brief, se corrige el seguimiento. Se actualiza al cerrar cada etapa, en el mismo commit, y cada vez que Diego avisa de una decisión. Lo reemplazado se mueve a "Reemplazado el …", con la fecha. `informes/generar_informe.py` lee las fases por el formato `## Fase N — nombre (inicio – fin)`: si agregás una, respetalo.

---

## 6. Histórico: VCTK y la extracción por lote (fuera de alcance desde el 19/10/2026)

**Estado:** archivado el 20/10/2026. **No usar como insumo del modelo.**

El 19/10 el grupo sacó del alcance el audio real: VCTK, `pyworld`, la síntesis WAV y Flask.
Este archivo deja constancia de lo que se hizo con VCTK entre el 12 y el 13 de octubre, porque
el código y los datos se borraron del disco el 20/10 para liberar espacio (~12 GB).

### Qué se borró

| Qué | Tamaño | Versionado en git |
|---|---|---|
| `data/VCTK-Corpus-0.92.zip` y `data/VCTK-Corpus-0.92/` | ~11,7 GB el zip, más lo descomprimido | No (`data/` está en `.gitignore`) |
| `data/derivados/` (`vctk_por_archivo.csv`, `vctk_por_hablante.csv`, `vctk_estadisticas.json`) | ~7,7 MB | No |
| `src/tfc_voz/corpus.py` (extracción por lote y estadísticas) | — | **No, nunca se commiteó** |
| `pyworld` y `flask` (con sus dependencias) en `.venv` | — | Se sacaron de `requirements.txt` |

`extraccion.py` (la extracción de un solo archivo con parselmouth) **se conserva sin cambios**.

### Qué hacía `corpus.py`

- Corría `extraccion.extraer_parametros` sobre todos los audios `mic1` de VCTK 0.92, con 10 procesos
  en paralelo y reanudable. No usaba `mic2` porque es la misma frase grabada con otro micrófono.
- La unidad de análisis era el **hablante** (110), no la frase: cada parámetro era la mediana sobre las
  frases sin advertencias ni error.
- Las correlaciones se calculaban sobre las medianas por hablante, **estandarizando dentro de cada sexo**,
  para que la diferencia entre sexos no fabricara correlaciones.
- Un F0 de frase por debajo de 0,6 o por encima de 1,6 veces la mediana del hablante se contaba
  como posible salto de octava.

### Resultados (13/10/2026)

- 44.455 audios de 110 hablantes (63 F, 47 M), 0 errores, ~75 min.
- 998 archivos con advertencias (2,2 %), 997 de ellos por VTL > 21 cm en hombres. Formantes fuera de rango: 4.
- **Sesgo del VTL:** el estimador de tubo uniforme promediando F1–F3 daba ~2 cm de más. El sesgo venía de F1
  (desde F1: 18,6 cm; M 21,7), mientras que F2 y F3 coincidían entre sí (F 15,1/15,4; M 17,6/17,6).
  Quedó sin resolver: el 20/10 el VTL pasó a tomarse directo de la S6 y dejó de medirse desde audio.
- p237 (F0 = 80,6 Hz) resultó una voz grave real: 339 frases estables entre 77,8 y 87,7 Hz, sin saltos.
  Ningún hablante tuvo más de 0,2 % de saltos de F0.

#### Media y desvío entre hablantes, por sexo

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

#### Correlaciones dentro de sexo (n = 110 hablantes)

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

### Si hubiera que rehacerlo

VCTK 0.92 está en https://datashare.ed.ac.uk/handle/10283/3443. Haría falta reescribir `corpus.py` y
reinstalar `pyworld` sólo si se vuelve a sintetizar audio. Las dos cosas están fuera de alcance; volver a
sumarlas lo tiene que decidir el grupo.
