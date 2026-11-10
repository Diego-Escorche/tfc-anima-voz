# Seguimiento — módulo de Voz

**Última actualización:** 9 nov 2026
**Estado general:** el alcance vigente es el del documento integrado del grupo. La síntesis de audio volvió al alcance: vocal sostenida con KlattGrid (parselmouth), VZ-08 vigente y VZ-09 retirado. La interfaz web la arma el grupo; el módulo expone `muestrear` y `sintetizar`. La validación contra audio real sigue afuera. El trabajo sigue el "Brief para IA programadora — prototipo autónomo del módulo de Voz", que manda sobre este archivo. Hecho al 9/11: Fases 1 y 2 completas. El bloque 2 arrancó el 9/11 con la entrega de Diego (paquete `anima_spine` 2.2 y cohorte 2.0); la Etapa 3, prevista para la semana del 3/11, quedó corrida a la semana del 9/11. Desde el 3/11 la hipótesis es la reformulada: por dominio, que el modelo recupera el nivel de señal declarado; ningún contraste entre dominios se afirma.

**Riesgo principal:** que el código no arranque. Venía sin avance desde fines de septiembre; la semana 1 es a propósito el hito más barato.

**Los resultados de Voz cierran el 21 de diciembre, no en febrero.** Enero queda para el prototipo y las 30 horas de redacción, con los números ya quietos.

---

## Fase 1 — Entorno y h² recargadas (20 oct – 26 oct)
- [x] Limpieza del alcance del 19/10: VCTK, `corpus.py`, `pyworld` y Flask fuera, documentados en `historico-vctk.md`
- [x] `tests/test_setup.py` en verde en un venv nuevo (Python 3.12.4, sólo `requirements.txt`) — brief del 20/10, tarea 1
- [x] h² recargadas con la regla agregada de cinco vocales, contrastadas contra la S6 (promedio 0,0707) — brief del 20/10, tarea 2
- [x] Casos VZ-01 a VZ-05 y VZ-07 sobre el generador, semilla 20261019 (51 tests en verde) — brief del 20/10, tarea 3
- [x] README, SETUP, decisiones y seguimiento actualizados al alcance del 19/10 — brief del 20/10, tarea 4
- [x] Dato bibliográfico con su regla de lectura entregado a Audrey, Tomás y Brest (confirmado por Diego el 23/10)
- [x] Etapa 0: factibilidad de la síntesis con KlattGrid. Pasa: F0 medida 120,00 Hz contra 120 pedidos (23/10, `informes/etapa0-factibilidad-sintesis.md`)

## Fase 2 — Cohorte compartida y contrato de salida (27 oct – 2 nov)
- [x] Columna vertebral `anima_spine` 1.1 en el repo: `cohorte_anima.csv` v1.1 (no la v1.0), congelada con huella SHA-256; `spine.verificar` pasa (23/10)
- [x] Etapa 1: `cohorte.py` (envoltorio de `spine.cargar`) y `poblacion.py` (efectos de sexo, edad y subpoblación con su fuente); VZ-06 en verde sobre la cohorte real y la generada (23/10)
- [x] Etapa 2: `fenotipo.py`, modelo generativo con heredabilidad residual; h², d, r, c y pendientes de edad recuperados en los 8 parámetros con 200.000 personas (23/10)
- [x] Datos de Voz para la capa de calibración de Tomás: `scripts/exportar_para_calibracion.py` escribe `informes/voz_para_calibracion.csv` (8.000 filas de calibración y prueba, media y desvío oráculo; validación OK). Columnas según la propuesta de Diego a Tomás del 26/10 (26/10)
- [x] VZ-01 a VZ-05 y VZ-07 sobre `fenotipo.py` (decisión del 26/10): VZ-01 a VZ-04 son el test de h² dentro de cada sexo de la Etapa 2; VZ-05 (permutación) y VZ-07 (20 semillas del barrido) agregados. Todos en verde (26/10)
- [x] Formato de salida (adelantado de la Etapa 6): `salida.py` valida con `anima_spine` y escribe tres archivos — predicciones, intervalos en seis niveles y barrido de 20 réplicas; rechaza fila duplicada, nivel faltante y 19 réplicas (29/10)
- [x] Relevamiento de `extraccion.py` (sin cambiarlo) e informe de cierre del bloque, `informes/avance-bloque-1.md`. Diferencias con Gisladóttir: f0_medio con promedio y no mediana, VTL por tubo sobre F1 a F3 (29/10). Las dos se corrigen en la Etapa 7 (decisiones 2 y 5)
- [x] Oráculo movido a `fenotipo.py` (`oraculo`), respuesta del 29/10: el script lo llama y un test confirma que el CSV regenerado es idéntico, byte a byte, al que se le mandó a Tomás (29/10)

## Fase 3 — Modelo heterocedástico (3 nov – 30 nov)
Es el bloque 2 del brief del prototipo. Informe semanal en `informes/avance-bloque-2.md`.

Semana del 9/11, en el orden de la entrega de Diego del 9/11 (cada punto habilita al siguiente):
- [x] 1. Paquete `anima_spine` 2.2 en el repo, con la cohorte 2.0 (503 personas de 1000 Genomes y 1.497 simuladas; huella `8203824a…`, coincide con los metadatos). Suite del paquete: 43 pasan, 16 salteadas (contrato de módulos que no exportaron) (9/11)
- [x] 2. Cohorte 1.1 reemplazada por la 2.0 en todo el módulo. `informes/voz_para_calibracion.csv` (hecho sobre la 1.1) retirado por obsoleto; queda en el historial de git (9/11)
- [x] 3. Los ocho h² en un único archivo de configuración, `config/niveles_declarados.json`, cargado por `niveles.py`; `parametros.py` ya no tiene literales y `tests/test_niveles.py` falla si un nivel aparece escrito a mano en un `.py` del módulo (9/11)
- [x] 4. Los dos niveles declarados en esa configuración: caso base (agregado 7,07 %) y segundo nivel por parámetro (V por subpoblación, agregado 0,148 %), los dos como entrada. La composición de la cohorte 2.0 queda registrada al lado; el cargador la verifica y no recalcula. V se calcula una vez con `scripts/calcular_segundo_nivel.py`. `describir` da el renglón del reporte con nivel, archivo, versión, fecha y verificación de la cohorte. Configuración en la versión 1.2 (9/11)
- [x] 5. `informes/voz_para_calibracion.csv` sobre la cohorte 2.0 con las 20 réplicas: 160.000 filas, columnas nuevas `replica`, `semilla`, `dominio` y `sexo`; caso base y puntaje genético enteramente simulado, declarado en `voz_para_calibracion.meta.json`. Validación OK. Se regenera cuando entre el punto 7 (9/11)
- [x] 6. Etapa 3: `modelo.py` (máxima verosimilitud normal, L-BFGS-B con gradiente analítico, error si no converge) y `lineas_base.py` (las dos líneas base y el modelo completo, sólo con entrenamiento). Los 24 modelos convergen sobre la cohorte 2.0, con 42 iteraciones como máximo. Tests de la Etapa 3 y de los ajustes del 29/10 en verde; el de g permutado es frágil (ver `informes/avance-bloque-2.md`) (9/11)
- [x] 7. Variantes conocidas: `variantes.py` y g = g_conocida + g_resto en `fenotipo.py`, con los genotipos de `datos/` en las 503 personas reales y sorteados en las simuladas. VZ-14 (tres partes) y VZ-15 en verde: Var(g_conocida) de f0_medio 0,00627 en la cohorte 2.0 y 0,00608 con 200.000 personas, contra 0,0062. `voz_para_calibracion.csv` regenerado (9/11)
- [ ] 8. `recuperacion_voz.csv` y criterio de recuperación (tolerancia 0,015, sobre el caso base)
- [ ] 9. Análisis de dos niveles

Plan por semanas del 29/10 (se reordena con el brief del 5/11):
- [x] Semana del 3/11 (corrida a la del 9/11; hecha el 9/11) — Etapa 3: `modelo.py` (genérico, máxima verosimilitud normal; verifica la convergencia) y sus tests
- [x] Semana del 10/11 (adelantada al 9/11) — `lineas_base.py`: las dos líneas base y el modelo completo, con los "Ajustes del 29/10" (definiciones compartidas con `fenotipo.py`, test de la línea base 2, test con g permutado)
- [ ] Semana del 17/11 — tabla predictiva (16.000 filas, contrato v2 de Tomás) y `correr_replica`, en un archivo nuevo, `replicas.py`, que se suma a la tabla de archivos del README
- [ ] Semana del 17/11 — Etapa 5: `metricas.py`, sólo funciones y tests (cobertura, ΔR² total y parcial, CRPS, bootstrap pareado); VZ-11 a VZ-13 se corren en diciembre
- [ ] Semana del 17/11 — control de integración: ΔR² parcial promedio de 20 réplicas a menos de 0,025 de la h² de cada parámetro
- [ ] Semana del 24/11 — adaptador de la Etapa 4 con datos oráculo, sólo si Diego pasó el contrato congelado y la v1 de la capa de Tomás está disponible; si no, pasa a diciembre
- [ ] Modelo terminado y documentado para que Tomás lo adapte (semana del 24-30 nov)
- [ ] Redacción adelantada: metodología y límites (el diseño no depende de resultados)

## Fase 4 — Calibración y primeros ΔR² (1 dic – 8 dic)
- [ ] Etapa 4: `calibracion.py` como adaptador a la capa común de Tomás (`anima_spine/calibracion.py`, contrato v2), sin lógica de calibración propia; con la salida del modelo como entrada
- [ ] VZ-10: cobertura promedio de 20 réplicas dentro de ±5 puntos del nivel nominal en los seis niveles, del 50 % al 95 %
- [ ] Primeros ΔR² de Voz contra las dos líneas base, con IC95 % (VZ-11, VZ-12) — 8 dic

## Fase 5 — Cierre de resultados de Voz (9 dic – 21 dic)
- [ ] VZ-13: tabla de los 8 parámetros ordenados por ΔR² parcial, con el total y la h² inyectada al lado
- [ ] Etapa 6: `prototipo.py` (un comando corre todo el circuito) y `reporte_voz.md`. `--generar-cohorte` con otra composición de subpoblaciones falla (lo verifica `niveles.cargar`); el reporte avisa si la composición no se verificó
- [ ] `predicciones_voz.csv`, `intervalos_voz.csv` y `barrido_voz.csv` definitivos entregados al análisis integral — 21 dic

## Fase 6 — Síntesis de audio y vista vocal (9 dic – 21 dic)
- [ ] Etapa 7: `muestreo.py` (`muestrear`) y `sintesis.py` (`sintetizar`), las funciones que llama la vista vocal del prototipo web
- [ ] Decisiones sobre la síntesis del 23/10 y del 29/10 implementadas (ver "Decisiones tomadas")
- [ ] VZ-08: ida y vuelta, F0 medida a menos de 5 Hz de la pedida en 20 realizaciones de ambos sexos

Corre en paralelo con la Fase 5 y tiene menos prioridad: si el tiempo aprieta, se termina después de VZ-10 a VZ-13 (ventana confirmada por Diego el 23/10).

Del 22 dic al 4 ene: fiestas, nada comprometido.

## Fase 7 — Prototipo y redacción (5 ene – 31 ene)
- [ ] Prototipo conjunto (OE6)
- [ ] Etapa 8: README y seguimiento al cierre del prototipo
- [ ] Redacción del documento individual (30 h, el bloque más grande del plan)
- [ ] Informe de validación consolidado (OE7)
- [ ] Iteración con Pedro Brest (tutor)

## Fase 8 — Defensa (1 feb – 15 feb)
- [ ] Ensayo de defensa
- [ ] Defensa (semana del 9 al 15 feb)

---

## Dependencias con el grupo

| Qué | De quién | Para cuándo | Estado o plan alternativo |
|---|---|---|---|
| `cohorte_anima.csv` congelada | Grupo | 27 oct | **Existe:** v2.0 (mixta: 503 personas de 1000 Genomes y 1.497 simuladas), congelada el 6/11 con huella SHA-256 y copiada al repo el 9/11 con el paquete `anima_spine` 2.2 |
| Línea base heterocedástica (OE2) | Grupo | 24-30 nov | El prototipo arma las dos líneas base en `lineas_base.py`; informar contra una sola si falta |
| Capa de calibración conformal (OE4) | Tomás | Contrato v2 congelado ~31/10; v1 de la capa en noviembre | **Voz usa la capa común de Tomás** (decisión del 27/10): `calibracion.py` es un adaptador sin lógica propia y se conecta con datos oráculo en la segunda quincena de noviembre. Plan B, sólo con el visto bueno de Diego: si a fin de noviembre la capa no está, calibración provisoria (split conformal normalizado, ~6 h) detrás de la misma firma del adaptador |
| ΔR² de Rostro y Temperamento sobre la misma cohorte | Audrey y Tomás | 26 ene | El documento individual se sostiene con el ΔR² de Voz y su IC |

La capa de calibración tiene que ser agnóstica del modelo (recibe μ y σ, devuelve el intervalo): Tomás la entrega a mediados de noviembre y el modelo de Voz recién está el 30.

## Decisiones tomadas

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

## Decisiones pendientes del grupo (bloquean)

- [ ] Con qué criterio se eligen las h² en los tres módulos. Queda vinculado a las decisiones 2 y 3 del documento integrado; Rostro mantiene 7,9 % por ahora

## Datos a averiguar

- [x] Tabla S6 de Gisladóttir — en `referencias/tabla-s6-heredabilidades.csv`
- [ ] Criterio con el que se eligieron las h² de Rostro y de Temperamento
- [ ] Si el 7,9 % y el 2,89 % de Rostro están medidos sobre `cohorte_anima.csv`
- [ ] Calendario de entregas de la cátedra después de la Práctica 10 (las semanas que coincidan bajan a la mitad)
- [ ] Política de propiedad del código
- [ ] Elegibilidad de cada uno para la defensa de febrero (el único riesgo que no se arregla con horas)
- [ ] (menor) Algún estudio post-2024 con h²-SNP directo para jitter/HNR

## Riesgos de la síntesis de audio

Salieron de la Etapa 0 (23/10; tablas en `informes/etapa0-factibilidad-sintesis.md`). Los cinco quedaron **decididos el 23/10 y se implementan en la Etapa 7**: ver "Decisiones sobre la síntesis (23/10)" en "Decisiones tomadas".

- **El medidor de formantes falla sobre la vocal sintética** (con 5 formantes, F2 y F3 salen mal numerados). → Decisión 1: VZ-08 mide con 4 formantes.
- **El VTL no podía hacer ida y vuelta** (la síntesis lo usaba para F4 y F5; el medidor, sobre F1 a F3). → Decisión 2: una sola definición, por espaciado de formantes sobre F1 a F4.
- **El flutter mueve a la vez el jitter y la variabilidad de F0.** → Decisión 3: no usar flutter; un punto de pitch por período, más corrección iterativa.
- **El ruido de aspiración empeora la medición de formantes y el HNR está acoplado al jitter.** → Decisiones 1 y 3: formantes medidos con 4 y HNR ajustado por corrección iterativa.
- **La variabilidad de F0 necesita un contorno.** → Brief, Etapa 7: suma de 3 senoidales lentas (0,5 a 3 Hz), ajustada por corrección iterativa.
- **El jitter está en % en la referencia y en fracción en el medidor** (observación del 26/10). → Decisión 4 (29/10): conversión en un solo lugar, al entrar a `sintetizar`.

## Correcciones del documento individual (.docx)

Sección cerrada el 23/10: las cuatro correcciones están hechas. El documento lo mantiene Claude, así que esta sección no se vuelve a usar.

- [x] Sacar la afirmación de que la línea base ya captura casi toda la señal heredable de la voz
- [x] Reemplazar el plan de ocho fases por el cronograma de 17 semanas
- [x] Sacar el corpus de audio de Herramientas (queda sólo la atribución de Praat, vía `parselmouth`)
- [x] Sección 1.2: falta un punto o un guión después de "en 3D"

---

## Reemplazado el 9/11

- **Niveles declarados 1.1:** el segundo nivel se derivaba al cargar, con la composición de la cohorte cargada, y los valores del JSON eran control (tolerancia 0,0002). Desde la 1.2 son entrada y la composición se verifica.
- **Salvedad de jitter y HNR (1.1):** "valor conservador de 0,05, apoyado en estudios de gemelos (Van Lierde et al., 2005; Campos et al., 2024)". Desde la 1.2, cota superior declarada; la evidencia apunta a un valor pequeño o nulo.
- **Niveles declarados 1.0:** el segundo nivel era configurado, calculado con la frecuencia europea promedio (0,006160, 0,003433 y 0,002247). Desde la 1.1 es derivado por subpoblación y esos valores son control.

- **Fase 2:** "Columna vertebral `anima_spine` 1.1 en el repo: `cohorte_anima.csv` v1.1". Desde el 9/11 el paquete es el 2.2 y la cohorte, la 2.0.
- **Fase 2:** "Oráculo movido a `fenotipo.py`: un test confirma que el CSV regenerado es idéntico al que se le mandó a Tomás". Ese CSV era de la 1.1 y quedó obsoleto; el test se retiró y el archivo se regenera sobre la 2.0 (punto 5 de la entrega).
- **Dependencias:** la fila de la cohorte decía "v1.1 del paquete `anima_spine`, copiada al repo el 23/10".
- **Decisiones pendientes:** "Qué afirma el TFC: un gradiente entre dominios, o que la maquinaria funciona y cómo responde a la heredabilidad". Resuelta el 3/11 con la hipótesis reformulada.

## Reemplazado el 29/10

- **Fase 3:** "Etapa 3: `modelo.py` y `lineas_base.py`" y "Etapa 5: `metricas.py` …" en dos renglones. Pasaron a un renglón por semana del bloque 2.
- **Fase 4:** "Etapa 4: calibración provisoria, split conformal normalizado (reemplazable por la capa de Tomás)". Desde el 27/10, `calibracion.py` es un adaptador a la capa común; la provisoria quedó como plan B.
- **Fase 5:** "VZ-13: tabla de los 8 parámetros ordenados por ΔR²". Desde el 26/10 se ordena por el ΔR² parcial.
- **Dependencias:** la fila de la capa de calibración decía "El prototipo usa una provisoria (`calibracion.py`, reemplazable)", con fecha 1-7 dic.
- **Decisiones, ajustes de la Etapa 3:** "oráculo reusado de `exportar_para_calibracion.py`". Desde la respuesta del 29/10, el cálculo vive en `fenotipo.oraculo` y el script lo llama.

## Reemplazado el 23/10

- **Estado general del 20/10:** "el 19/10 se acotó el alcance (afuera: síntesis de audio, validación contra audio real e interfaz web)". La síntesis volvió al alcance con el documento integrado.
- **Fase 2:** "Migrar a `cohorte_anima.csv` v1.0". La cohorte vigente es la v1.1.
- **Fase 2:** "Primer `predicciones_voz.csv` que pase las pruebas de contrato comunes". Se exportan tres archivos, no uno.
- **Fase 3:** las tareas 5a y 5b del brief del 20/10 (`modelo.py` y `metricas.py`) pasaron a ser las Etapas 3 y 5 del brief del prototipo. "Las dos líneas base (OE2, del grupo)" pasó a `lineas_base.py`.
- **Fase 4:** "VZ-10 en verde (cobertura dentro de ±5 pp del 90 %)". Ahora es el promedio de 20 réplicas en seis niveles.
- **Fases 6 y 7** (prototipo y defensa) pasaron a ser las 7 y 8, por la fase nueva de síntesis.
- **Decisión pendiente cerrada el 22/10:** "Cómo queda formulada la hipótesis: tres niveles, dos niveles o reordenada".
- **Riesgos de la síntesis:** anotados como abiertos el 23/10 y decididos ese mismo día.

## Antes del 20/10: plan de ocho fases (reemplazado)

- **Fase 1 del plan viejo** cerrada el 12 oct: 8 parámetros, generador de cohorte, medidor y entorno.
- Lo que se hizo con audio real entre el 12 y el 13 oct salió del alcance el 19/10. Está documentado en `historico-vctk.md`.
- Secciones del documento individual adelantadas: portada, resumen e índice, y de 1.1 a 1.7 (problemática, antecedentes, alcance, hipótesis, supuestos, limitaciones y herramientas).

---

**Cómo usar este archivo:** refleja el estado del módulo, no decide nada; si contradice al brief, se corrige el seguimiento. Se actualiza al cerrar cada etapa, en el mismo commit, y cada vez que Diego avisa de una decisión. Lo reemplazado se mueve a "Reemplazado el …", con la fecha. `informes/generar_informe.py` lee las fases por el formato `## Fase N — nombre (inicio – fin)`: si agregás una, respetalo.
