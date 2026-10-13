# Seguimiento — módulo de Voz

**Última actualización:** 12 oct 2026
**Estado general:** Fase 1 **atrasada** — el diseño está cerrado y el código base escrito, pero el entorno no se instaló y VCTK no se descargó. La Fase 1 vencía el 1 de octubre.

**Situación del cronograma:** la Fase 2 (la más pesada) lleva ~35% de su ventana consumida sin haber arrancado. Para terminarla el 1 de noviembre harían falta ~25 hs/semana en vez de las 16 planificadas. En volumen total el proyecto sigue viable (~190 hs en 18 semanas ≈ 11 hs/semana promedio), gracias al adelanto de la redacción del documento individual. El riesgo es el efecto dominó hacia diciembre, que es el mes con menos margen.

**Decisión pendiente si no se recupera el atraso:** recortar alcance en la Fase 2 (menos parámetros, o cohorte sintética más chica) antes que empujar el atraso hacia adelante.

---

## Fase 1 — Congelar diseño y armar entorno (17 sep – 1 oct)
- [x] Fijar los 8 parámetros acústicos con nombre/unidad/heredabilidad (`parametros.py` + `decisiones-fase1.md`)
- [x] Definir el esquema del genotipo sintético (Opción A confirmada, `genotipo.py`)
- [x] Definir cómo se representa un individuo (`IndividuoSintetico`)
- [x] Resolver el corpus de validación (VCTK en vez de TIMIT)
- [x] Instalar el entorno (venv + `requirements.txt`) y correr `test_setup.py` — 12 oct, Python 3.12.4, todo en verde (pyworld 0.3.5 ya trae paquete precompilado para 3.12, no hizo falta compilar)
- [x] Descargar VCTK — 12 oct, v0.92 en `data/VCTK-Corpus-0.92/` (110 hablantes; audio en FLAC, parselmouth lo lee directo)
- [x] Prueba de humo end-to-end (parselmouth sobre 5-10 archivos de VCTK) — 12 oct, 10 archivos (5 F, 5 M): 0 con advertencias, 0 errores. Ojo para Fase 2: VTL da ~2 cm más alto que lo típico de la literatura (media F 16.7, M 19.0)

## Fase 2 — Pipeline + cohorte + modelo base (1 oct – 1 nov)
- [ ] Extraer los 8 parámetros de VCTK completo con parselmouth
- [ ] Generar la cohorte sintética completa (no solo el esqueleto de código)
- [ ] Ajustar el modelo heterocedástico base

## Fase 3 — Calibración y evaluación (1 nov – 15 nov)
- [ ] Split conformal prediction, verificar cobertura ±5pp
- [ ] Sharpness (Gneiting et al. 2007) + bootstrap ΔR²
- [ ] Primer reporte de validación

## Fase 4 — Reconstrucción + síntesis + interfaz mínima (15 nov – 1 dic)
- [ ] Reconstrucción individual (punto + intervalo)
- [ ] Síntesis WAV vía pyworld
- [ ] Interfaz Flask mínima

## Fase 5 — Integración con Rostro/Temperamento (1 dic – 15 dic)
- [ ] Acordar formato de intercambio de datos con Audrey y Tomás
- [ ] Consolidar API/app conjunta
- [ ] Primer informe de validación integrado

## Fase 6 — Redacción de la documentación individual (15 dic – 15 ene)
- [x] Portada, Resumen, Índice (`TFC-DiegoEscorche-2027.docx`) — *adelantado*
- [x] 1.1 Problemática y Contexto — *adelantado*
- [x] 1.2 Antecedentes y Trabajos Relacionados — *adelantado*
- [x] 1.3 Alcance — *adelantado*
- [x] 1.4 Hipótesis — *adelantado*
- [x] 1.5 Supuestos — *adelantado*
- [x] 1.6 Limitaciones — *adelantado*
- [x] 1.7 Herramientas — *adelantado*
- [ ] Metodología detallada (una vez que el pipeline esté construido)
- [ ] Resultados
- [ ] Iteración con Pedro Brest (tutor)

## Fase 7 — Pruebas finales y pulido (15 ene – 1 feb)
- [ ] Revisión del informe de validación completo
- [ ] Pulido de la interfaz (revelación secuencial)
- [ ] Corrección de inconsistencias detectadas tarde

## Fase 8 — Buffer y defensa (1 feb – 15 feb)
- [ ] Ensayo de defensa
- [ ] Explicación preparada para la inconsistencia conocida de P2

## Pendientes puntuales (no atados a una fase específica)
- [x] Sacar el h² exacto de VTL de Dediu et al. (2022) — Tabla 2: SVTh = 0.26 (gemelos), deflacionado a 0.13 en escala h²-SNP
- [x] Revisar si Van Lierde et al. (2005) da números usables para jitter/HNR — no da h²; junto con Lima et al. (2024) justifica el valor conservador de 0.05
- [ ] (menor) Buscar si aparece algún estudio post-2024 con h²-SNP directo para jitter/HNR
- [ ] Confirmar con el equipo si algo de esto corresponde subir hoy (Práctica 7 — Clase 9)

---

**Cómo usar este archivo:** marcá `[x]` a medida que termines cada tarea, o simplemente decime "marcá tal cosa como hecha" en el chat y lo actualizo yo.
