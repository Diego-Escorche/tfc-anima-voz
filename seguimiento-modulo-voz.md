# Seguimiento — módulo de Voz

**Última actualización:** 26 oct 2026
**Estado general:** el alcance vigente es el del documento integrado del grupo. La síntesis de audio volvió al alcance: vocal sostenida con KlattGrid (parselmouth), VZ-08 vigente y VZ-09 retirado. La interfaz web la arma el grupo; el módulo expone `muestrear` y `sintetizar`. La validación contra audio real sigue afuera. El trabajo sigue el "Brief para IA programadora — prototipo autónomo del módulo de Voz", que manda sobre este archivo. Hecho al 23/10: Fase 1 completa (incluida la Etapa 0, que pasa) y la columna vertebral `anima_spine` 1.1 copiada y verificada.

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
- [ ] Formato de salida (adelantado de la Etapa 6): `salida.py` valida y escribe tres archivos — predicciones, intervalos en seis niveles y barrido de 20 réplicas
- [ ] Relevamiento de `extraccion.py` (sin cambiarlo) e informe de cierre del bloque, `informes/avance-bloque-1.md`

## Fase 3 — Modelo heterocedástico (3 nov – 30 nov)
- [ ] Etapa 3: `modelo.py` (genérico, máxima verosimilitud normal) y `lineas_base.py` (las dos líneas base y el modelo completo)
- [ ] Etapa 5: `metricas.py` — cobertura, ΔR², CRPS y bootstrap pareado (genérico); VZ-11 y VZ-13 con ΔR² total y parcial, VZ-13 ordenado por el parcial (decisión del 26/10)
- [ ] Modelo terminado y documentado para que Tomás lo adapte (semana del 24-30 nov)
- [ ] Redacción adelantada: metodología y límites (el diseño no depende de resultados)

## Fase 4 — Calibración y primeros ΔR² (1 dic – 8 dic)
- [ ] Etapa 4: calibración provisoria, split conformal normalizado (reemplazable por la capa de Tomás)
- [ ] VZ-10: cobertura promedio de 20 réplicas dentro de ±5 puntos del nivel nominal en los seis niveles, del 50 % al 95 %
- [ ] Primeros ΔR² de Voz contra las dos líneas base, con IC95 % (VZ-11, VZ-12) — 8 dic

## Fase 5 — Cierre de resultados de Voz (9 dic – 21 dic)
- [ ] VZ-13: tabla de los 8 parámetros ordenados por ΔR²
- [ ] Etapa 6: `prototipo.py` (un comando corre todo el circuito) y `reporte_voz.md`
- [ ] `predicciones_voz.csv`, `intervalos_voz.csv` y `barrido_voz.csv` definitivos entregados al análisis integral — 21 dic

## Fase 6 — Síntesis de audio y vista vocal (9 dic – 21 dic)
- [ ] Etapa 7: `muestreo.py` (`muestrear`) y `sintesis.py` (`sintetizar`), las funciones que llama la vista vocal del prototipo web
- [ ] Decisiones sobre la síntesis del 23/10 implementadas (ver "Decisiones tomadas")
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
| `cohorte_anima.csv` congelada | Grupo | 27 oct | **Existe:** v1.1 del paquete `anima_spine`, congelada con huella SHA-256 y copiada al repo el 23/10 |
| Línea base heterocedástica (OE2) | Grupo | 24-30 nov | El prototipo arma las dos líneas base en `lineas_base.py`; informar contra una sola si falta |
| Capa de calibración conformal (OE4) | Tomás | 1-7 dic | El prototipo usa una provisoria (`calibracion.py`, reemplazable) |
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

## Decisiones pendientes del grupo (bloquean)

- [ ] Con qué criterio se eligen las h² en los tres módulos. Queda vinculado a las decisiones 2 y 3 del documento integrado; Rostro mantiene 7,9 % por ahora
- [ ] Qué afirma el TFC: un gradiente entre dominios, o que la maquinaria funciona y cómo responde a la heredabilidad

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

## Correcciones del documento individual (.docx)

Sección cerrada el 23/10: las cuatro correcciones están hechas. El documento lo mantiene Claude, así que esta sección no se vuelve a usar.

- [x] Sacar la afirmación de que la línea base ya captura casi toda la señal heredable de la voz
- [x] Reemplazar el plan de ocho fases por el cronograma de 17 semanas
- [x] Sacar el corpus de audio de Herramientas (queda sólo la atribución de Praat, vía `parselmouth`)
- [x] Sección 1.2: falta un punto o un guión después de "en 3D"

---

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
