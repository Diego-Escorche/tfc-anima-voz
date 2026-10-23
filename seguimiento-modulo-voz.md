# Seguimiento — módulo de Voz

**Última actualización:** 20 oct 2026
**Estado general:** el 19/10 se acotó el alcance (afuera: síntesis de audio, validación contra audio real e interfaz web) y se rearmó el cronograma: de 218 horas a **150 horas en 17 semanas** (~10 h/semana; las dos semanas de fiestas, 2 h). Las tareas de código de la semana 1 están hechas: entorno corriendo, h² recargadas con la regla agregada de la S6 y los primeros casos VZ en verde. Falta entregar el dato bibliográfico al grupo.

**Riesgo principal:** que el código no arranque. Venía sin avance desde fines de septiembre; la semana 1 es a propósito el hito más barato.

**Los resultados de Voz cierran el 21 de diciembre, no en febrero.** Enero queda para el prototipo y las 30 horas de redacción, con los números ya quietos.

---

## Fase 1 — Entorno y h² recargadas (20 oct – 26 oct)
- [x] Limpieza del alcance del 19/10: VCTK, `corpus.py`, `pyworld` y Flask fuera, documentados en `historico-vctk.md`
- [x] `tests/test_setup.py` en verde en un venv nuevo (Python 3.12.4, sólo `requirements.txt`) — brief, tarea 1
- [x] h² recargadas con la regla agregada de cinco vocales, contrastadas contra la S6 (promedio 0,0707) — brief, tarea 2
- [x] Casos VZ-01 a VZ-05 y VZ-07 sobre el generador, semilla 20261019 (51 tests en verde) — brief, tarea 3
- [x] README, SETUP, decisiones y seguimiento actualizados al alcance del 19/10 — brief, tarea 4
- [ ] Dato bibliográfico con su regla de lectura entregado a Audrey, Tomás y Brest

## Fase 2 — Cohorte compartida y contrato de salida (27 oct – 2 nov)
- [ ] Migrar a `cohorte_anima.csv` v1.0 (2.000 personas, particiones 1.000 / 500 / 500)
- [ ] VZ-06: particiones de entrenamiento y calibración disjuntas
- [ ] Primer `predicciones_voz.csv` que pase las pruebas de contrato comunes

## Fase 3 — Modelo heterocedástico (3 nov – 30 nov)
- [ ] Ajuste por máxima verosimilitud de μ y log σ por parámetro (`modelo.py`, genérico) — brief, tarea 5a
- [ ] ΔR² con bootstrap pareado (`metricas.py`, genérico) — brief, tarea 5b
- [ ] Las dos líneas base: intercepto solo y ancestría-sexo-edad (OE2, del grupo)
- [ ] Modelo terminado y documentado para que Tomás lo adapte (semana del 24-30 nov)
- [ ] Redacción adelantada: metodología y límites (el diseño no depende de resultados)

## Fase 4 — Calibración y primeros ΔR² (1 dic – 8 dic)
- [ ] Calibración conformal aplicada; VZ-10 en verde (cobertura dentro de ±5 pp del 90 %)
- [ ] Primeros ΔR² de Voz contra las dos líneas base, con IC95 % (VZ-11, VZ-12) — 8 dic

## Fase 5 — Cierre de resultados de Voz (9 dic – 21 dic)
- [ ] VZ-13: tabla de orden de los 8 parámetros por ΔR²
- [ ] `predicciones_voz.csv` definitivo entregado al análisis integral — 21 dic

Del 22 dic al 4 ene: fiestas, nada comprometido.

## Fase 6 — Prototipo y redacción (5 ene – 31 ene)
- [ ] Prototipo conjunto (OE6)
- [ ] Redacción del documento individual (30 h, el bloque más grande del plan)
- [ ] Informe de validación consolidado (OE7)
- [ ] Iteración con Pedro Brest (tutor)

## Fase 7 — Defensa (1 feb – 15 feb)
- [ ] Ensayo de defensa
- [ ] Defensa (semana del 9 al 15 feb)

---

## Dependencias con el grupo

| Qué | De quién | Para cuándo | Plan alternativo |
|---|---|---|---|
| `cohorte_anima.csv` v1.0 congelada | Grupo | 27 oct | Ya existe; el pedido es que no cambie |
| Línea base heterocedástica (OE2) | Grupo | 24-30 nov | Informar contra una sola línea base y declararlo |
| Capa de calibración conformal (OE4) | Tomás | 1-7 dic | La escribe Diego: split conformal son ~6 h |
| ΔR² de Rostro y Temperamento sobre la misma cohorte | Audrey y Tomás | 26 ene | El documento individual se sostiene con el ΔR² de Voz y su IC |

La capa de calibración tiene que ser agnóstica del modelo (recibe μ y σ, devuelve el intervalo): Tomás la entrega a mediados de noviembre y el modelo de Voz recién está el 30.

## Decisiones pendientes del grupo (bloquean)

- [ ] Con qué criterio se eligen las h² en los tres módulos (si Voz usa la regla agregada y los otros máximos, el contraste queda sesgado)
- [ ] Cómo queda formulada la hipótesis: tres niveles, dos niveles o reordenada. Recomendación: dos niveles, decidido antes de ver resultados
- [ ] Qué afirma el TFC: un gradiente entre dominios, o que la maquinaria funciona y cómo responde a la heredabilidad

## Datos a averiguar

- [x] Tabla S6 de Gisladóttir — en `referencias/tabla-s6-heredabilidades.csv`
- [ ] Criterio con el que se eligieron las h² de Rostro y de Temperamento
- [ ] Si el 7,9 % y el 2,89 % de Rostro están medidos sobre `cohorte_anima.csv`
- [ ] Calendario de entregas de la cátedra después de la Práctica 10 (las semanas que coincidan bajan a la mitad)
- [ ] Política de propiedad del código
- [ ] Elegibilidad de cada uno para la defensa de febrero (el único riesgo que no se arregla con horas)
- [ ] (menor) Algún estudio post-2024 con h²-SNP directo para jitter/HNR

## Riesgos abiertos para la síntesis de audio (Etapa 7 del brief del prototipo)

Salieron de la prueba de factibilidad del 23/10 (Etapa 0: pasa, F0 medida 120,00 Hz contra 120 pedidos). Detalle y tablas en `informes/etapa0-factibilidad-sintesis.md`.

- [ ] **El medidor de formantes falla sobre la vocal sintética.** Con la configuración de `extraccion.py` (Burg, 5 formantes, techo 5.000 Hz), F2 y F3 salen mal numerados (1.345 y 1.499 Hz en vez de 1.500 y 2.500) y el VTL medido queda fuera de rango. Con 4 formantes dan 1.466 y 2.423 Hz. Cambiar `extraccion.py` lo decide Diego.
- [ ] **El VTL no puede hacer ida y vuelta tal como está definido.** En la síntesis, el VTL sólo fija F4 y F5, pero `extraccion.py` lo calcula desde F1 a F3. Lo que mide es el VTL implícito en F1 a F3 (en la prueba, 17,5 cm en vez de 17).
- [ ] **El flutter mueve dos parámetros a la vez.** Con flutter 0,25 cambian el jitter (0,3 %) y la variabilidad de F0 (0,73 Hz). Falta probar un punto de pitch por período con perturbación aleatoria, que el brief admite.
- [ ] **El ruido de aspiración empeora la medición de formantes.** Con aspiración a 60 dB el HNR baja a 21 dB, pero F2 se mide en 954 Hz. La correspondencia del HNR tiene que tenerlo en cuenta.
- [ ] **La variabilidad de F0 necesita un contorno.** Con dos puntos de pitch fijos da 0,001 Hz. La Etapa 7 ya prevé una variación lenta alrededor de la media.

## Correcciones pendientes en el documento individual (.docx)

- [ ] Sacar la afirmación de que la línea base ya captura casi toda la señal heredable de la voz (es falsa: las h² están netas de sexo, edad y altura)
- [ ] Reemplazar el plan de ocho fases por el cronograma de 17 semanas
- [ ] Sacar el corpus de audio de Herramientas (queda sólo la atribución de Praat, vía `parselmouth`)
- [ ] Sección 1.2: falta un punto o un guión después de "en 3D"

---

## Antes del 20/10: plan de ocho fases (reemplazado)

- **Fase 1 del plan viejo** cerrada el 12 oct: 8 parámetros, generador de cohorte, medidor y entorno.
- Lo que se hizo con audio real entre el 12 y el 13 oct salió del alcance el 19/10. Está documentado en `historico-vctk.md`.
- Secciones del documento individual adelantadas: portada, resumen e índice, y de 1.1 a 1.7 (problemática, antecedentes, alcance, hipótesis, supuestos, limitaciones y herramientas).

---

**Cómo usar este archivo:** marcá `[x]` a medida que termines cada tarea, o simplemente decime "marcá tal cosa como hecha" en el chat y lo actualizo yo. `informes/generar_informe.py` lee las fases por el formato `## Fase N — nombre (inicio – fin)`: si agregás una, respetalo.
