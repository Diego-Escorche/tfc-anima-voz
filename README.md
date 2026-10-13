# Módulo de Voz — Proyecto Anima (TFC)

> **Si sos una IA leyendo esto:** este archivo es tu contexto completo. Leelo
> entero antes de escribir código o proponer cambios. Contiene decisiones ya
> tomadas con su justificación — varias parecen "mejorables" a primera vista y
> no lo son. La sección **Qué NO hacer** es la más importante.

---

## 1. Qué es esto en una frase

Un sistema que, dado un genotipo, estima ocho parámetros acústicos de una voz
**junto con su incertidumbre calibrada**, y mide cuánta información aporta
realmente el genotipo por encima de lo que ya se sabría solo por sexo y altura.

---

## 2. Contexto académico

- **Qué es:** Trabajo Final de Carrera, Ingeniería en Informática, Universidad
  de Belgrano. Defensa: **febrero 2027**.
- **Proyecto grupal** llamado **Anima**, de tres integrantes, con tres dominios:
  - **Rostro** (morfología facial) — Audrey Barrientos. Repo aparte: `AnimaFace`.
  - **Voz** (parámetros vocales) — **Diego Escorche. Este repo.**
  - **Temperamento** (rasgos de personalidad) — Tomás Varas.
- **Tutor:** Pedro Brest. Hay weeklies de seguimiento.
- Cada integrante entrega un documento individual, pero el código, la línea base
  poblacional y la capa de calibración son trabajo conjunto.

### El argumento científico (esto es lo que se defiende)

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

## 3. Estado actual (al 12 de octubre de 2026)

| Componente | Estado |
|---|---|
| Diseño del espacio de parámetros | **Hecho** (`parametros.py`) |
| Generador de genotipo sintético | **Hecho** (`genotipo.py`) |
| Extracción acústica desde WAV | **Escrito, sin validar con audio real** (`extraccion.py`) |
| Chequeo de entorno | **Hecho** (`tests/test_setup.py`) |
| Corpus VCTK descargado | **Pendiente** |
| Cohorte sintética completa | **Pendiente** (Fase 2) |
| Modelo heterocedástico | **Pendiente** (Fase 2) |
| Calibración conformal | **Pendiente** (Fase 3) |
| Reconstrucción + síntesis WAV | **Pendiente** (Fase 4) |
| Interfaz Flask | **Pendiente** (Fase 4) |

**El próximo paso concreto** es seguir `SETUP.md`: instalar el entorno, bajar
VCTK y correr la primera extracción real.

---

## 4. Arquitectura

```
                    ┌─────────────────────────┐
  VCTK (audio real) │  extraccion.py          │
  ─────────────────▶│  parselmouth → 8 params │──┐
                    └─────────────────────────┘  │  rangos y correlaciones
                                                 │  reales de la población
                    ┌─────────────────────────┐  │
  h² publicada      │  parametros.py          │  │
  ─────────────────▶│  espacio + heredabilidad│──┤
                    └─────────────────────────┘  │
                                                 ▼
                    ┌─────────────────────────────────────┐
                    │  genotipo.py                        │
                    │  cohorte sintética                  │
                    │  score = genético + ambiental       │
                    └─────────────────────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │  [Fase 2] modelo heterocedástico     │
                    │  media e intervalo por parámetro    │
                    └─────────────────────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │  [Fase 3] split conformal prediction │
                    │  cobertura empírica ±5 pp            │
                    │  + bootstrap ΔR² vs. línea base      │
                    └─────────────────────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │  [Fase 4] reconstrucción individual  │
                    │  → mapa de incertidumbre (Flask)     │
                    │  → síntesis WAV (pyworld)            │
                    └─────────────────────────────────────┘
```

### Archivos

| Archivo | Rol |
|---|---|
| `src/tfc_voz/parametros.py` | Define los 8 parámetros, su h² y el nivel de evidencia que la respalda |
| `src/tfc_voz/genotipo.py` | Genera la cohorte sintética (Opción A) |
| `src/tfc_voz/extraccion.py` | Extrae los 8 parámetros de un WAV con parselmouth |
| `tests/test_setup.py` | Verifica que el entorno esté bien instalado |
| `decisiones-fase1.md` | Justificación bibliográfica detallada de cada h² |
| `SETUP.md` | Instalación paso a paso |

---

## 5. Los 8 parámetros

Separados según la **teoría fuente-filtro** (Fant, 1960): la voz se produce en
dos etapas, una fuente (cuerdas vocales vibrando) y un filtro (el tracto vocal
que le da forma a ese sonido).

**Fuente** — F0 medio, variabilidad de F0, jitter, HNR
**Filtro** — F1, F2, F3, VTL (longitud del tracto vocal)

Todos los h² están en **escala h²-SNP** y con su nivel de evidencia:

| Parámetro | h² | Evidencia | Fuente |
|---|---|---|---|
| `f0_medio` | 0.17 | directa | Gisladóttir et al. 2023 |
| `f0_variabilidad` | 0.13 | directa | Gisladóttir et al. 2023 |
| `f1` | 0.09 | directa | Gisladóttir et al. 2023 |
| `f2` | 0.14 | directa | Gisladóttir et al. 2023 |
| `f3` | 0.08 | directa | Gisladóttir et al. 2023 |
| `vtl` | 0.13 | **derivada** | Dediu et al. 2022 (0.26 en gemelos, deflacionado) |
| `jitter` | 0.05 | **débil** | Van Lierde 2005 (n.s.) / Lima et al. 2024 |
| `hnr` | 0.05 | **débil** | Lima et al. 2024 |

`decisiones-fase1.md` tiene la justificación completa de cada uno.

### VTL: la conversión de escala

El modelo del tracto vocal es un tubo cerrado en un extremo (glotis) y abierto
en el otro (labios). Sus resonancias son:

```
Fn = (2n - 1) · c / (4L)        c = 35.000 cm/s, L = largo en cm
```

Dediu et al. reportan h² = 0.26 para el largo del tracto vocal, **pero medido en
gemelos**, no por SNPs. La heredabilidad de gemelos captura toda la varianza
genética aditiva; la h²-SNP solo la de variantes comunes genotipadas, y es menor.
Mezclarlas sin convertir inflaría artificialmente el aporte genético de VTL.

Se deflaciona a la mitad → **0.13**. Ese factor 1/2 es un **supuesto explícito
del proyecto**, no un valor publicado, y está declarado como tal en la memoria.

---

## 6. Decisiones tomadas (no las deshagas sin hablarlo)

### Opción A: polygenic score simple, no SNPs individuales

```python
score_genetico  ~ N(0, h²)
score_ambiental ~ N(0, 1 - h²)
score_total = genetico + ambiental      # varianza total = 1
```

Se evaluó simular variantes individuales (p. ej. `rs11046212-T` del gen *ABCC9*,
frecuencia ~47,7% en Europa, efecto +2,1 Hz por alelo) y **se descartó por
cronograma**, no por rigor. Queda como mejora opcional si sobra tiempo, aplicada
solo a `f0_medio`.

### VCTK en vez de TIMIT

TIMIT requiere licencia LDC y no hay acceso. VCTK es gratuito, trae 109
hablantes y un `speaker-info.txt` con sexo y edad por hablante.
Descarga: https://datashare.ed.ac.uk/handle/10283/3443

**El sexo del hablante es obligatorio** para la extracción: define el rango de
búsqueda de F0.

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
  fuera de alcance: requiere datasets y cómputo que exceden el proyecto. El
  enfoque es paramétrico (parametrizar y resintetizar), tipo Soundgen.
- **No busques un dataset que empareje genotipo y voz de las mismas personas.**
  No existe públicamente. Eso está documentado como hallazgo científico del
  proyecto, no como una limitación a resolver.
- **No "mejores" el modelo para subir el ΔR².** Un ΔR² chico es el resultado
  esperado dado que la h² de la voz es 8-17%.
- **No trates el resultado nulo de jitter/HNR como un bug.** Se espera ΔR² ≈ 0
  ahí, y eso refuerza el argumento del gradiente.
- **No mezcles h² de gemelos con h²-SNP** sin convertir de escala (ver VTL).
- **No uses los rangos de F0 por defecto de Praat** (75-600 Hz). Usá los de
  `RANGO_F0` en `extraccion.py`, tomados de Gisladóttir et al.
- **No amplíes el alcance a más idiomas o acentos.** VCTK (inglés) alcanza para
  validar el pipeline de extracción.

---

## 8. Problemas conocidos

### Tracking de formantes (el más importante)

`extraccion.py` **está escrito pero no validado con audio real**. En pruebas con
señal sintética, el algoritmo de Praat insertó un formante espurio y corrió la
numeración: lo que debía ser F2 se leyó como F3, arruinando el cálculo de VTL.

Se le pusieron tres defensas:
1. Mide solo frames **sonoros** (en silencio el tracking devuelve basura).
2. Usa **mediana**, no promedio (resiste frames con formantes espurios).
3. **Control de plausibilidad** automático: `RANGOS_PLAUSIBLES` marca cuándo la
   extracción no es confiable, vía `ParametrosExtraidos.advertencias`.

**Tarea pendiente:** validar con VCTK y contar cuántos archivos disparan
advertencias antes de decidir si hay que ajustar `maximum_formant`.

### Pitch-halving / pitch-doubling

El algoritmo de autocorrelación puede reportar la mitad o el doble del F0 real si
el rango de búsqueda está mal. Por eso el rango por sexo es obligatorio.

### pyworld necesita compilador de C++

Solo publica paquetes precompilados hasta Python 3.8. En versiones modernas pip
lo compila desde el fuente. Ver `SETUP.md` paso 1. **Python 3.11 está
verificado funcionando.**

---

## 9. Cómo correr las cosas

```bash
# activar el entorno virtual primero (ver SETUP.md)

python tests/test_setup.py                        # verificar instalación
python src/tfc_voz/parametros.py                  # ver el espacio de parámetros
python src/tfc_voz/genotipo.py                    # generar cohorte de prueba
python src/tfc_voz/extraccion.py archivo.wav F    # extraer de un WAV (M o F)
python informes/generar_informe.py                # informe de estado en PDF
```

El informe de estado lee el avance por fase de `seguimiento-modulo-voz.md`; el
resto del texto se edita en la sección `CONTENIDO` del script antes de cada
informe nuevo. Necesita además `requirements-informes.txt`.

Los módulos funcionan tanto importados como paquete (`from tfc_voz.genotipo
import ...`, parado en `src/`) como corridos directo.

---

## 10. Lo que sigue (Fase 2)

1. Correr `extraccion.py` sobre VCTK completo → rangos y correlaciones reales.
2. Usar esas estadísticas para reescalar la cohorte sintética a unidades reales
   (hoy `genotipo.py` produce scores estandarizados, media 0 y varianza 1).
3. Ajustar el modelo heterocedástico: media **e intervalo** por parámetro,
   condicionados al genotipo. Heterocedástico porque la incertidumbre no es
   igual para todos los individuos ni para todos los parámetros.

Criterio de éxito de la Fase 3: cobertura empírica dentro de **±5 puntos
porcentuales** del nivel nominal declarado.

---

## 11. Bibliografía central

| Referencia | Para qué |
|---|---|
| Gisladóttir et al. (2023), *Science Advances* | Ancla principal: h²-SNP de voz, variante en *ABCC9*, 12.901 islandeses |
| Di et al. (2024), *Communications Biology* | Réplica de la misma variante en 7.654 mujeres chinas Han |
| Dediu et al. (2022), *Human Genetics* | Heredabilidad anatómica del tracto vocal (632 gemelos) — sustento de VTL |
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
- **Semilla:** `generar_cohorte_sintetica` usa semilla fija (42) para que los
  resultados sean reproducibles. No la saques.
- **Entregable:** prototipo funcional, no aplicación productiva. No hace falta
  autenticación, base de datos, ni deploy.
