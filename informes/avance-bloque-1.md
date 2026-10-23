# Avance del bloque 1 — módulo de Voz (23/10 al 2/11)

**Última actualización:** 23/10/2026 · **Estado del bloque:** en curso. Preparación, Etapa 0, seguimiento y Etapa 1 hechos; Etapa 2 frenada por una decisión de diseño (ver "Preguntas abiertas").

Informe pedido por el "Brief para IA programadora — prototipo autónomo del módulo de Voz", para que Diego se lo pase a Claude. Se completa al cerrar cada paso del bloque.

## Estado de cada paso

| Paso | Estado | Archivos tocados | Commit |
|---|---|---|---|
| Preparación: columna vertebral `anima_spine` 1.1 | **Hecho** (23/10) | `anima_spine/`, `cohorte_anima.csv`, `cohorte_anima.meta.json` (copiados sin modificar), `.gitattributes`, `pyproject.toml` | `d99591e` |
| Etapa 0: factibilidad de la síntesis | **Hecho** (23/10). Pasa | `scripts/prueba_sintesis.py`, `informes/etapa0-factibilidad-sintesis.md`, `informes/prueba_sintesis.wav` | `34a1120` |
| Seguimiento al día, antes de la Etapa 1 | **Hecho** (23/10) | `seguimiento-modulo-voz.md` | `862b8be`, `9598e4c` |
| Etapa 1: cohorte y efectos poblacionales | **Hecho** (23/10) | `src/tfc_voz/cohorte.py`, `src/tfc_voz/poblacion.py`, `tests/test_cohorte.py`, `tests/test_poblacion.py`, `seguimiento-modulo-voz.md` | `b3f8092` |
| Etapa 2: fenotipos | **Sin empezar.** Espera la decisión sobre los tests "a edad fija" | `informes/propuesta-tests-edad-fija.md` (la propuesta) | `0543223` |
| Formato de salida (`salida.py`) | **Sin empezar** | — | — |
| Relevamiento de `extraccion.py` | **Sin empezar** | — | — |

Antes del bloque se commiteó por separado el trabajo del brief del 20/10, que no estaba commiteado (`a96b1f9`).

### Preparación

- `spine.verificar(spine.cargar("cohorte_anima.csv"))` pasa. La huella SHA-256 coincide (`0f9567c4…19de33`).
- Cohorte: versión 1.1, 2.000 personas, particiones de 1.000 / 500 / 500, sexo 1.000 / 1.000.
- Los archivos copiados son idénticos byte a byte a los del zip.
- `.gitattributes` marca `cohorte_anima.csv` como `-text`. Este equipo tiene `core.autocrlf=true`: sin esa marca, un checkout en Windows le cambiaría los finales de línea y rompería la huella.

### Etapa 0

Pasa: F0 medida 120,00 Hz contra 120 Hz pedidos. Los 9 comandos de KlattGrid probados funcionan con parselmouth 0.4.7 (Praat 6.1.38). Las tablas y los riesgos para la Etapa 7 están en `informes/etapa0-factibilidad-sintesis.md`. Diego aprobó el 23/10 las decisiones que los resuelven ("Decisiones sobre la síntesis (23/10)", Etapa 7 del brief).

### Etapa 1

- **`cohorte.py`:**
  - `leer_cohorte` envuelve `spine.cargar` y `spine.verificar` sin repetir ninguna validación: si el paquete rechaza el archivo, su error pasa tal cual.
  - `generar_cohorte` llama a `spine.generar`.
- **`poblacion.py`:**
  - Los 8 parámetros, con los valores de la tabla del brief y una fuente por valor, con su tipo.
  - `pendientes()` devuelve la lista de valores PENDIENTE; hoy está vacía.
  - `configuracion_neutra()` queda sólo para tests.
- **VZ-06 en verde:** particiones disjuntas, que cubren a las 2.000 personas, con tamaños 1.000 / 500 / 500. Se comprobó sobre `cohorte_anima.csv` y sobre una cohorte generada.
- **`leer_cohorte` rechaza cuatro archivos mal formados**, con el error del paquete:
  - CSV que no coincide con la huella;
  - ids repetidos;
  - sexo fuera de la codificación;
  - columna faltante.

## Resultado del pytest completo

**89 tests: 89 pasan, 0 fallan, 0 salteados** (45 s, Python 3.12.4). `tests/test_setup.py` es un chequeo de entorno que se corre aparte, y también pasa.

| Archivo | Tests | Qué cubre |
|---|---|---|
| `tests/test_generador.py` | 36 | VZ-01 a VZ-05 y VZ-07 sobre el generador |
| `tests/test_poblacion.py` | 30 | Valores del brief, fuentes, pendientes, configuración neutra |
| `tests/test_parametros.py` | 15 | h² contra la tabla S6 |
| `tests/test_cohorte.py` | 8 | VZ-06 y rechazo de archivos mal formados |

## Tests de la Etapa 2

Sin empezar. Acá va la tabla de valor pedido, valor medido y tolerancia por parámetro.

## Decisiones consultadas a Diego

| Fecha | Pregunta | Respuesta |
|---|---|---|
| 23/10 | Ventana de la fase nueva de síntesis en el seguimiento | 9 a 21 dic, en paralelo con el cierre de resultados |
| 23/10 | ¿El dato bibliográfico ya se entregó? | Sí: se marcó como hecho en la Fase 1 |
| 23/10 | Índice de `default_rng([semilla, indice])` en la Etapa 2. Si es la posición en la lista, reordenar parámetros cambia los valores, cosa que el brief prohíbe | Índice fijo por nombre: f0_medio 0, f0_variabilidad 1, jitter 2, hnr 3, f1 4, f2 5, f3 6, vtl 7. Un parámetro nuevo recibe el siguiente |
| 23/10 | Cómo medir "a edad fija" en los tests de la Etapa 2 | Diego lo consulta con el manager. Propuesta en `informes/propuesta-tests-edad-fija.md` |
| 23/10 | Archivos `.md` que ya no hacían falta | Se borraron `informe-fase1.md` y el plan del brief del 20/10. Se conserva `historico-vctk.md`, único registro de lo borrado del disco |

## Desvíos respecto del brief

- **`generar_cohorte` tiene un argumento `n`** (por defecto 2.000) además de `semilla`. Sirve para generar las 200.000 personas de los tests de la Etapa 2 con el mismo paquete.
- **El criterio de tipos de fuente es propio.** El brief pide distinguir "dato" de "derivado" sin definirlos. Se usó: "dato", lo que sale de una celda o frase de la fuente, a lo sumo convertido a la escala del módulo; "derivado", lo que combina varios valores. Está en el encabezado de `poblacion.py`.
- **`pyproject.toml` suma la raíz del repo a `pythonpath`**, para que los tests importen `anima_spine`, que el brief pide copiar en la raíz.
- **`.gitattributes` y `*.zip` en `.gitignore`:** protegen la huella del CSV y dejan el zip del paquete fuera de git.
- **Etapa 0:** la variante con flutter, aspiración e inclinación espectral se midió en un archivo temporal. En `informes/` queda un solo WAV, como pide el brief.
- **README:** se agregó un aviso de que manda el brief del prototipo y se ajustó "Qué NO hacer" para que no prohíba la síntesis con KlattGrid. El resto del README se actualiza en la Etapa 8.

## Preguntas abiertas

1. **Tests "a edad fija" de la Etapa 2.** Con la lectura literal, un generador correcto fallaría el test de d el 52 % de las veces. La propuesta usa toda la muestra y descuenta la edad con el modelo, con las mismas tolerancias. Detalle en `informes/propuesta-tests-edad-fija.md`. **Bloquea la Etapa 2.**
2. **Casos dudosos en los tipos de fuente de `poblacion.py`:**
   - en f0_medio, b_hombre = 0 y q_mujer quedaron como "derivado", porque el texto de Gisladóttir no los da en forma explícita;
   - la media y el desvío de referencia se atribuyeron a la misma fila de la fuente que d y r, porque la tabla del brief no dice de dónde salen.
3. **Firma de `salida.py`.** Para validar, las funciones necesitan los ids de la partición de prueba. La idea es pasarles el DataFrame de la cohorte como argumento.
4. **Escala de `f0_variabilidad`.** `extraccion.py` la da en Hz, y el brief trabaja con el logaritmo de ese valor. Se confirma en el relevamiento de `extraccion.py`.
