# Avance del bloque 1 — módulo de Voz (23/10 al 2/11)

**Última actualización:** 29/10/2026 · **Estado del bloque: completo, a la espera de que Diego confirme el cierre.** Todos los pasos del bloque están hechos. El bloque 2 (3 al 30 de noviembre) no empieza sin esa confirmación.

Informe pedido por el "Brief para IA programadora — prototipo autónomo del módulo de Voz", para que Diego se lo pase a Claude. Se completa al cerrar cada paso del bloque.

## Estado de cada paso

| Paso | Estado | Archivos tocados | Commit |
|---|---|---|---|
| Preparación: columna vertebral `anima_spine` 1.1 | **Hecho** (23/10) | `anima_spine/`, `cohorte_anima.csv`, `cohorte_anima.meta.json` (copiados sin modificar), `.gitattributes`, `pyproject.toml` | `d99591e` |
| Etapa 0: factibilidad de la síntesis | **Hecho** (23/10). Pasa | `scripts/prueba_sintesis.py`, `informes/etapa0-factibilidad-sintesis.md`, `informes/prueba_sintesis.wav` | `34a1120` |
| Seguimiento al día, antes de la Etapa 1 | **Hecho** (23/10) | `seguimiento-modulo-voz.md` | `862b8be`, `9598e4c` |
| Etapa 1: cohorte y efectos poblacionales | **Hecho** (23/10), con los ajustes que pidió el manager | `src/tfc_voz/cohorte.py`, `src/tfc_voz/poblacion.py`, `tests/test_cohorte.py`, `tests/test_poblacion.py`, `seguimiento-modulo-voz.md` | `b3f8092`, `1791981` |
| Etapa 2: fenotipos | **Hecho** (23/10) | `src/tfc_voz/fenotipo.py`, `tests/test_fenotipo.py`, `seguimiento-modulo-voz.md` | `76008fb` |
| Datos de Voz para la calibración de Tomás | **Hecho** (26/10) | `scripts/exportar_para_calibracion.py`, `informes/voz_para_calibracion.csv`, `tests/test_exportar_para_calibracion.py`, `seguimiento-modulo-voz.md` | `333940a` |
| Respuesta 1 del 26/10: referencias verificadas | **Hecho** (26/10) | `src/tfc_voz/poblacion.py`, `tests/test_poblacion.py`, `seguimiento-modulo-voz.md` | `9eeedc3` |
| Respuesta 3 del 26/10: VZ-01 a VZ-05 y VZ-07 sobre `fenotipo.py` | **Hecho** (26/10) | `tests/test_fenotipo.py`, `seguimiento-modulo-voz.md` | `63b15c4` |
| Formato de salida (`salida.py`) | **Hecho** (29/10) | `src/tfc_voz/salida.py`, `tests/test_salida.py`, `seguimiento-modulo-voz.md` | `f91ba46` |
| Relevamiento de `extraccion.py` | **Hecho** (29/10), sin cambiar el archivo | `informes/avance-bloque-1.md` | `7bedeaa` |

Antes del bloque se commiteó por separado el trabajo del brief del 20/10, que no estaba commiteado (`a96b1f9`). Las propuestas de diseño están en `0543223` (edad fija) y en el commit de este informe (`informes/propuestas-23-10-etapa2.md`).

### Preparación

- `spine.verificar(spine.cargar("cohorte_anima.csv"))` pasa. La huella SHA-256 coincide (`0f9567c4…19de33`).
- Cohorte: versión 1.1, 2.000 personas, particiones de 1.000 / 500 / 500, sexo 1.000 / 1.000.
- Los archivos copiados son idénticos byte a byte a los del zip.
- `.gitattributes` marca `cohorte_anima.csv` como `-text`: este equipo tiene `core.autocrlf=true`, y sin esa marca un checkout en Windows rompería la huella.

### Etapa 0

Pasa: F0 medida 120,00 Hz contra 120 Hz pedidos. Los 9 comandos de KlattGrid probados funcionan con parselmouth 0.4.7 (Praat 6.1.38). Tablas y riesgos en `informes/etapa0-factibilidad-sintesis.md`. Diego aprobó el 23/10 las decisiones que resuelven los riesgos ("Decisiones sobre la síntesis (23/10)", Etapa 7 del brief).

### Etapa 1

- **`cohorte.py`:**
  - `leer_cohorte` envuelve `spine.cargar` y `spine.verificar` sin repetir validaciones: si el paquete rechaza el archivo, su error pasa tal cual.
  - `generar_cohorte(semilla, n)` llama a `spine.generar`.
- **`poblacion.py`:**
  - Los 8 parámetros, con los valores de la tabla del brief y una fuente por valor con su tipo (dato, derivado, 0 declarado, PENDIENTE).
  - `pendientes()` devuelve la lista de valores PENDIENTE; hoy está vacía.
  - `configuracion_neutra()` queda sólo para tests.
- **VZ-06 en verde** sobre `cohorte_anima.csv` y sobre una cohorte generada: particiones disjuntas, que cubren a las 2.000 personas, con tamaños 1.000 / 500 / 500.
- **`leer_cohorte` rechaza** un CSV que no coincide con la huella, ids repetidos, un sexo fuera de la codificación y una columna faltante.
- **Ajuste del 23/10, pedido por el manager:** en f0_medio, las fuentes de b_hombre = 0 y q_mujer dicen que son la lectura de Gisladóttir (el cambio de los hombres empieza a los 60; el de las mujeres termina a los 60).

### Etapa 2

- **`fenotipo.py`:**
  - `generar_fenotipos(cohorte, parametros, efectos, semilla)` aplica y = m + s · (g + e) con los efectos de `poblacion.py` y devuelve un DataFrame largo (`individuo_id`, `rasgo`, `g`, `e`, `y`).
  - Cada parámetro tiene su generador, `default_rng([semilla, indice])`, con el índice fijo por nombre de `INDICE_SEMILLA` (f0_medio 0 … vtl 7).
- **Tests**, con 200.000 personas de `generar_cohorte(n=200_000)` y semilla 20261019:
  - h² dentro de cada sexo;
  - d, r, c y pendientes de edad "a edad fija", por regresión sobre toda la muestra, con r y c sacados de log|residuo| sin usar el c verdadero (como pidió el manager);
  - misma semilla, mismo resultado;
  - agregar o reordenar parámetros no cambia los demás;
  - con la configuración neutra, y = g + e exacto;
  - efecto de subpoblación exacto.
- Todos pasan con la semilla fija. El peor desvío es 0,0125 (b + q de mujeres en f3) contra una tolerancia de 0,02.

### Datos de Voz para la calibración de Tomás

- **Archivo:** `informes/voz_para_calibracion.csv`, generado con `python scripts/exportar_para_calibracion.py`.
- **Filas: 8.000.** Son las 500 personas de `calibracion` y las 500 de `prueba` de `cohorte_anima.csv`, por los 8 parámetros.
- **Columnas, en este orden:** `individuo_id`, `particion`, `rasgo`, `y_real`, `mu_oraculo`, `sigma_oraculo`. Siguen la propuesta que Diego le mandó a Tomás el 26/10; si el contrato congelado usa otros nombres, se cambian en `COLUMNAS`, sin tocar la lógica.
- **Fenotipos:** efectos reales de `poblacion.py` y semilla 20261019, la de la réplica 0. `y_real` coincide exactamente con el `y` de `generar_fenotipos`.
- **Validación antes de escribir: OK.** Comprueba una fila por (`individuo_id`, `rasgo`), ids y particiones iguales a los de la cohorte, valores finitos y `sigma_oraculo` > 0. Un test confirma que pasa y otros seis, que rechaza un archivo con una fila duplicada, una partición cambiada, un individuo faltante, un valor no finito, un sigma en 0 o las columnas en otro orden.
- **`mu_oraculo` y `sigma_oraculo` no son predicciones de ningún modelo.** Son la media y el desvío verdaderos de cada persona, conocidos por diseño: `mu_oraculo` = m + s · g y `sigma_oraculo` = s · √(1 − h²). Con ellos, (y_real − mu_oraculo) / sigma_oraculo es normal estándar (el test lo verifica: media y desvío a menos de 0,05 de 0 y 1). Una capa de calibración probada con estos datos parte de intervalos ya bien calibrados; las 8.000 filas sirven para probar la forma y el flujo, no para medir cuánto corrige.

### Referencias de `poblacion.py` verificadas (respuesta 1 del 26/10)

- La media y el desvío de referencia salen de la media y el DE de las mujeres en unidades físicas, tal como los informan las fuentes (Gisladóttir, tabla S2 `S2_Means`; Goy et al. 2013, tabla 3), convertidos a logaritmo por momentos lognormales: desvio_ref = √ln(1 + (DE / media)²) y media_ref = ln(media) − desvio_ref² / 2.
- Tipo: **"derivado"** en los siete parámetros convertidos; **"dato"** en hnr, que ya está en dB. Cada fuente anota la fila, la media, el DE y la fórmula. Los valores físicos quedan en `REFERENCIA_FISICA`.
- Un test recalcula las referencias desde la tabla del manager. Mayor diferencia: 0,00005 (tolerancia 0,0001); en jitter, 0,00026 (tolerancia 0,001, porque Goy redondea a dos decimales).

### VZ-01 a VZ-05 y VZ-07 sobre `fenotipo.py` (respuesta 3 del 26/10)

Sobre el generador del prototipo, con 200.000 personas (100.000 por sexo). El criterio de cada caso es el mismo que tenía sobre `genotipo.py`, cuyos tests quedan como están.

| Caso | Qué verifica | Criterio | Medido | Estado |
|---|---|---|---|---|
| VZ-01 a VZ-04 | La h² pedida se recupera: R² de (y − m) / s explicado por g, dentro de cada sexo | Error menor a 0,01 en los 8 parámetros y ambos sexos | Error máximo 0,0044 | Pasó |
| VZ-05 | Control de permutación: g mezclado al azar entre personas | R² menor a 0,005 en los 8 parámetros y ambos sexos | R² máximo 0,00006 | Pasó |
| VZ-07 | Estabilidad: VZ-01 a VZ-04 con las 20 semillas del barrido, 20261019 + r (r de 0 a 19) | Error menor a 0,01 en las 20 semillas, 8 parámetros y ambos sexos | Error máximo 0,0049 | Pasó |

Detalle por parámetro (VZ-01 a VZ-05 con la semilla 20261019):

| Parámetro | h² pedida | VZ-01 a VZ-04: R² medido (mujeres / hombres) | VZ-05: R² con g mezclado (mujeres / hombres) | VZ-07: mayor error en 20 semillas |
|---|---|---|---|---|
| f0_medio | 0,1027 | 0,1063 / 0,1012 | 0,00001 / 0,00001 | 0,0049 |
| f0_variabilidad | 0,0410 | 0,0415 / 0,0419 | 0,00000 / 0,00006 | 0,0036 |
| jitter | 0,0500 | 0,0502 / 0,0513 | 0,00001 / 0,00000 | 0,0030 |
| hnr | 0,0500 | 0,0492 / 0,0506 | 0,00000 / 0,00000 | 0,0035 |
| f1 | 0,0619 | 0,0621 / 0,0633 | 0,00000 / 0,00001 | 0,0029 |
| f2 | 0,1353 | 0,1397 / 0,1348 | 0,00000 / 0,00001 | 0,0044 |
| f3 | 0,0644 | 0,0626 / 0,0600 | 0,00001 / 0,00000 | 0,0044 |
| vtl | 0,0606 | 0,0600 / 0,0589 | 0,00002 / 0,00000 | 0,0025 |

VZ-07 tarda unos 3 s por semilla y está marcado como lento (`pytest -m "not lento"` lo saltea), igual que el VZ-07 sobre `genotipo.py`.

### Formato de salida (`salida.py`)

- `escribir_predicciones(predicciones, cohorte, directorio, rasgos=None)`, `escribir_intervalos(intervalos, predicciones, cohorte, directorio)` y `escribir_barrido(barrido, intervalos, predicciones, cohorte, directorio)`. Reciben el DataFrame de `leer_cohorte` y toman de ahí los ids de prueba.
- Validan con `predictions.verificar`, `verificar_intervalos` y `verificar_barrido` **antes** de escribir, y escriben con los exportadores del paquete. Si la validación falla, levantan el error del paquete y no escriben nada.
- Tests con filas sintéticas armadas dentro del test sobre los 500 ids de prueba de `cohorte_anima.csv`:
  - **los tres archivos pasan** y se escriben: 8.000 filas de predicciones, 24.000 de intervalos (500 × 8 × 6 niveles) y 960 de barrido (20 réplicas × 8 × 6);
  - **se rechazan**, sin escribir el archivo: una fila duplicada, un nivel faltante (sin 95 %), 19 réplicas, un rasgo sin una de las dos líneas base, un id que no es de prueba, columnas fuera de orden y rasgos distintos de los pedidos.

### Relevamiento de `extraccion.py`

Sin cambios en el archivo. Se comparó contra la configuración de Gisladóttir que describe el brief. Los pasos de tiempo se verificaron corriendo el medidor sobre `informes/prueba_sintesis.wav`.

**(a) F0: método y rango.**
- Método: `Sound.to_pitch` sin método explícito, que en parselmouth es el comando "To Pitch..." de Praat: **autocorrelación (AC)**, con los parámetros por defecto (15 candidatos, umbrales estándar). Se verificó que da exactamente lo mismo que `to_pitch_ac`. **Coincide con Gisladóttir.**
- Rango por sexo: hombres de 60 a 220 Hz, mujeres de 100 a 300 Hz (`RANGO_F0`). **Coincide con Gisladóttir.**
- Paso de tiempo: el de Praat por defecto, 0,75 / piso de pitch (12,5 ms en hombres, 7,5 ms en mujeres).
- **Difiere de Gisladóttir: f0_medio es el promedio (`np.mean`) de los frames sonoros, no la mediana.** El parámetro corresponde a `MedianF0` en la S6 (h²) y en la S2 (referencias y efectos de sexo). Los formantes sí usan mediana. No se cambió.

**(b) Unidad de `f0_variabilidad`.**
- Es el desvío estándar (`np.std`, ddof = 0) del F0 de los frames sonoros, **en Hz**, no en semitonos.
- Coincide con `parametros.py` (unidad "Hz (SD)") y con Gisladóttir: `Vowels.StdF0` informa 9,80 (6,40) Hz en mujeres, valores que sólo tienen sentido en Hz. Según la respuesta del 23/10, la escala del módulo es el logaritmo de ese valor en Hz, como el resto. **Confirmado.**

**(c) Fórmula del VTL.**
- Modelo de tubo uniforme cerrado-abierto, L = (2n − 1) · c / (4 · Fn), calculado por separado desde F1, F2 y F3 y **promediado**, con **c = 35.000 cm/s**.
- **Difiere de Gisladóttir**, que usa espaciado de formantes sobre **F1 a F4** con c = 35.300 cm/s. Ya está decidido corregirlo en la Etapa 7 (decisión 2 sobre la síntesis, 23/10).

**Otras diferencias de configuración** (sin cambio):
- Formantes: Burg, 5 formantes, techo de 5.000 Hz en hombres y 5.500 Hz en mujeres, ventana de 0,025 s y mediana sobre frames sonoros, como Gisladóttir. Pero el **paso de tiempo es el de Praat por defecto, 6,25 ms** (25 % de la ventana); la configuración de Gisladóttir que cita la decisión 1 es de 0,01 s.
- Jitter: "local", sobre `To PointProcess (periodic, cc)` con los parámetros estándar de Praat (0,0001; 0,02; 1,3). Devuelve **fracción**, no % (ver la decisión 4 sobre la síntesis).
- HNR: `to_harmonicity_cc`, con piso igual al piso de pitch del sexo, paso de 0,01 s y 1 período por ventana; promedio de los frames definidos.

## Resultado del pytest completo

**230 tests: 230 pasan, 0 fallan, 0 salteados** (149 s, Python 3.12.4; sin los lentos, `pytest -m "not lento"`, alrededor de 50 s). `tests/test_setup.py` es un chequeo de entorno que se corre aparte, y también pasa.

| Archivo | Tests | Qué cubre |
|---|---|---|
| `tests/test_fenotipo.py` | 115 | Etapa 2 (h² por sexo, d, r, c y pendientes en los 8 parámetros, semillas, configuración neutra) y VZ-01 a VZ-05 y VZ-07 sobre `fenotipo.py` |
| `tests/test_poblacion.py` | 38 | Valores del brief, fuentes, referencias recalculadas desde las tablas, pendientes, configuración neutra |
| `tests/test_generador.py` | 36 | VZ-01 a VZ-05 y VZ-07 sobre `genotipo.py` (se conservan; su retiro se decide en la Etapa 8) |
| `tests/test_salida.py` | 8 | Formato de salida: los tres archivos pasan la validación del paquete; siete errores puestos a propósito se rechazan |
| `tests/test_exportar_para_calibracion.py` | 10 | Datos para la calibración de Tomás: forma, coincidencia con los fenotipos, oráculo calibrado y rechazo de archivos mal armados |
| `tests/test_parametros.py` | 15 | h² contra la tabla S6 |
| `tests/test_cohorte.py` | 8 | VZ-06 y rechazo de archivos mal formados |

## Tests de la Etapa 2: pedido contra medido

200.000 personas (100.000 por sexo), semilla 20261019. Valores de prueba propios del test, iguales para los 8 parámetros: d = −2, r = 0,8, c = 0,1, b_mujer = −0,3, b_hombre = +0,1, q_mujer = +0,2, q_hombre = +0,4. **Tolerancias:** 0,01 para la h²; 0,02 para d, r, c y las pendientes.

| Parámetro | h² pedida | h² medida (mujeres / hombres) | d | r | c | b mujer | b hombre | b+q mujer | b+q hombre |
|---|---|---|---|---|---|---|---|---|---|
| **Pedido** | — | — | −2,0000 | 0,8000 | 0,1000 | −0,3000 | 0,1000 | −0,1000 | 0,5000 |
| f0_medio | 0,1027 | 0,1063 / 0,1012 | −2,0062 | 0,8022 | 0,0996 | −0,3002 | 0,0998 | −0,1067 | 0,5006 |
| f0_variabilidad | 0,0410 | 0,0415 / 0,0419 | −1,9946 | 0,7987 | 0,0990 | −0,3035 | 0,0995 | −0,0972 | 0,5051 |
| jitter | 0,0500 | 0,0502 / 0,0513 | −1,9898 | 0,7954 | 0,0983 | −0,3000 | 0,1033 | −0,1017 | 0,4939 |
| hnr | 0,0500 | 0,0492 / 0,0506 | −1,9990 | 0,8019 | 0,0992 | −0,2991 | 0,1017 | −0,0999 | 0,4971 |
| f1 | 0,0619 | 0,0621 / 0,0633 | −1,9973 | 0,8012 | 0,0991 | −0,3024 | 0,1014 | −0,0907 | 0,5001 |
| f2 | 0,1353 | 0,1397 / 0,1348 | −1,9981 | 0,8001 | 0,1012 | −0,2974 | 0,1009 | −0,1060 | 0,4878 |
| f3 | 0,0644 | 0,0626 / 0,0600 | −2,0070 | 0,8020 | 0,1001 | −0,2990 | 0,0975 | −0,0875 | 0,5113 |
| vtl | 0,0606 | 0,0600 / 0,0589 | −2,0020 | 0,8028 | 0,1004 | −0,2985 | 0,1023 | −0,1099 | 0,4906 |

Los 144 valores están dentro de su tolerancia. El mayor desvío de la h² es 0,0044 (f2 en mujeres y f3 en hombres); el mayor de los efectos, 0,0125 (b+q de mujeres en f3), coherente con el brief, que anticipa que la pendiente de las mujeres después de los 60 es la estimación más ruidosa.

## Decisiones consultadas

| Fecha | Pregunta | Respuesta |
|---|---|---|
| 23/10 | Ventana de la fase nueva de síntesis en el seguimiento | Diego: 9 a 21 dic, en paralelo con el cierre de resultados |
| 23/10 | ¿El dato bibliográfico ya se entregó? | Diego: sí. Se marcó como hecho en la Fase 1 |
| 23/10 | Índice de `default_rng([semilla, indice])`. Si es la posición en la lista, reordenar cambia los valores, cosa que el brief prohíbe | Diego: índice fijo por nombre (f0_medio 0 … vtl 7); un parámetro nuevo recibe el siguiente |
| 23/10 | Archivos `.md` que ya no hacían falta | Diego: borrarlos. Se borraron `informe-fase1.md` y el plan del brief del 20/10; se conserva `historico-vctk.md` |
| 23/10 | Cómo medir "a edad fija" en la Etapa 2 (`informes/propuesta-tests-edad-fija.md`) | Manager: se adopta, con r y c estimados de los residuos sin el c verdadero, y un test propio para c. Implementado |
| 23/10 | Tipos de fuente dudosos en `poblacion.py` | Manager: b_hombre = 0 y q_mujer de f0_medio quedan como "derivado", anotados como lectura de Gisladóttir. Implementado |
| 23/10 | Firma de `salida.py` | Manager: las tres funciones reciben el DataFrame de `leer_cohorte` |
| 23/10 | Escala de `f0_variabilidad` | Manager: si `extraccion.py` la da en Hz, la escala es su logaritmo. Se confirma en el relevamiento |
| 23/10 | Desvíos de la Etapa 1 | Manager: los cuatro aprobados |
| 26/10 | ¿La media y el desvío de referencia son "dato" o "derivado"? | Manager, verificado contra las tablas originales: "derivado" (conversión de unidades físicas a logaritmo por momentos lognormales), salvo hnr, "dato". Implementado, con un test que las recalcula |
| 26/10 | El orden por ΔR² de VZ-13 refleja el efecto del sexo (`informes/propuestas-23-10-etapa2.md`, punto 1) | Manager: se informa también el ΔR² parcial contra `ancestria sexo edad`, con su IC95 %, y VZ-13 se ordena por el parcial. Se implementa en la Etapa 5. El contraste entre dominios lo decide el grupo |
| 26/10 | VZ-01 a VZ-05 y VZ-07 prueban `genotipo.py` (mismo documento, punto 2) | Manager: pasan a `fenotipo.py`, antes de `salida.py`. Implementado; `genotipo.py` y sus tests se conservan |
| 29/10 | Unidad del jitter: % en la referencia, fracción en el medidor (observación del 26/10) | Manager: decisión 4 sobre la síntesis. La conversión se hace en un solo lugar, al entrar a `sintetizar` (Etapa 7), con un test |

## Desvíos respecto del brief

Aprobados el 23/10: `n` en `generar_cohorte`, la raíz en el `pythonpath` de `pyproject.toml`, `.gitattributes` y `*.zip` en `.gitignore`, y el criterio de tipos de fuente.

Nuevos en la Etapa 2:

- **q_mujer = +0,2 en los valores de prueba.** El ejemplo del brief no da q_mujer. Con 0, un generador que ignorara q_mujer pasaría el test igual.
- **Los tests de d, r, c y pendientes corren en los 8 parámetros**, no en uno solo: cada parámetro usa su propio generador. Con la semilla fija pasan todos.
- **Tests agregados:** efecto de subpoblación exacto (el brief no pide ninguno para a), error claro si un parámetro no tiene índice de semilla, e índices de semilla fijos y distintos.
- **`fenotipo.py` expone `edad_centrada`, `tramo60` y `media_y_escala`.** Los usan los tests y los va a usar `lineas_base.py` en la Etapa 3, para que las dos definiciones no se separen.

En los datos para la calibración de Tomás:

- **Dos tests además de la validación que pide el brief:** que `y_real` sea exactamente el fenotipo de la réplica 0, y que el oráculo esté calibrado. El test importa el script con `importlib`, porque `scripts/` no está en el `pythonpath`.

En el formato de salida:

- **Las funciones reciben también los archivos de los que dependen.** `escribir_intervalos` recibe las predicciones, y `escribir_barrido` los intervalos y las predicciones, porque los verificadores del paquete los necesitan (el intervalo al 90 % tiene que coincidir con el de las predicciones, y la réplica 0 del barrido con los intervalos).
- **Dos controles además de los del paquete:** columnas exactas y en el orden del contrato, y las dos líneas base para cada rasgo. `predictions.verificar` controla que cada (rasgo, línea base) presente cubra la partición de prueba, pero no que estén las dos, que es lo que pide el contrato. Con `rasgos=` se exige además el conjunto exacto de rasgos.

Otros, sin efecto sobre el código del prototipo:

- **Etapa 0:** la variante con flutter, aspiración e inclinación espectral se midió en un archivo temporal; en `informes/` queda un solo WAV.
- **README:** se agregó un aviso de que manda el brief del prototipo y se ajustó "Qué NO hacer" para que no prohíba la síntesis con KlattGrid. El resto se actualiza en la Etapa 8.

## Preguntas abiertas

Las tres preguntas del 23/10 quedaron respondidas el 26/10, y la de la unidad del jitter el 29/10: ver "Decisiones consultadas". La escala de `f0_variabilidad` quedó confirmada en el relevamiento.

1. **f0_medio se mide con el promedio y no con la mediana.** `extraccion.py` toma el promedio de los frames sonoros, pero el parámetro y todas sus fuentes (S6 para la h², S2 para las referencias y el efecto del sexo) son `MedianF0`. Hoy sólo afecta a VZ-08, que mide el audio sintético. En una vocal sostenida con un contorno lento, promedio y mediana deberían dar casi lo mismo, pero la definición no coincide con la del rasgo. **Propuesta:** pasar a mediana en el mismo cambio de `extraccion.py` de la Etapa 7 (decisiones 1 y 2), y declararlo. No se cambió nada.
2. **Paso de tiempo de los formantes.** `extraccion.py` usa el de Praat por defecto (6,25 ms); la configuración de Gisladóttir que cita la decisión 1 es de 0,01 s. Con la mediana sobre una vocal sintética estable no debería cambiar el resultado. ¿Se fija en 0,01 s en el mismo cambio de la Etapa 7?

## Aclaraciones para el bloque 2

No bloquean el arranque (`modelo.py`, semana del 3/11), pero conviene tenerlas antes de la semana del 17/11:

1. **Dónde van `tabla_predictiva` y `correr_replica`.** La tabla de archivos del brief no las ubica. Propuesta: en `lineas_base.py`, que ya arma los tres modelos. Alternativa: un archivo nuevo, `replicas.py`.
2. **Reusar el oráculo.** El brief pide que la tabla predictiva calcule el oráculo "con la misma función que `exportar_para_calibracion.py`". Esa función está hoy dentro del script, y un módulo de `src/` no debería importar de `scripts/`. Propuesta: mover el cálculo a `fenotipo.py` (por ejemplo, `oraculo(cohorte, fenotipos, parametros, efectos)`) y que el script lo llame. El CSV que se le mandó a Tomás no cambia.
3. **Error de convergencia con nombres.** `modelo.py` es genérico y no conoce los nombres de los parámetros. Plan: `ajustar` levanta un error genérico de no convergencia con el mensaje del optimizador, y `lineas_base.py` lo vuelve a levantar con el parámetro y el modelo. Sin pregunta, salvo que prefieras otra cosa.
4. **Contrato v2 congelado y v1 de la capa de Tomás:** hacen falta para la semana del 24/11. Si no llegan, el adaptador pasa a diciembre, como dice el brief.

## Respuestas del 29/10

El manager respondió las dos preguntas y las cuatro aclaraciones (brief del prototipo, "Respuestas al avance del 29/10"):

- **Preguntas 1 y 2:** se adoptan. Mediana de F0 y paso de formantes de 0,01 s, en el cambio de `extraccion.py` de la Etapa 7 (decisión 5). No se tocó `extraccion.py`.
- **Aclaración 1:** `tabla_predictiva` y `correr_replica` van en un archivo nuevo, `replicas.py`.
- **Aclaración 2: hecha.** El cálculo pasó a `fenotipo.oraculo` y `scripts/exportar_para_calibracion.py` lo llama. Un test nuevo regenera el CSV y compara su SHA-256 con el del archivo enviado a Tomás (`22fb376e…`, commit `333940a`): es idéntico. Otros dos tests cubren `oraculo`: deja exactamente e / √(1 − h²) y rechaza fenotipos que no estén en el orden de la cohorte.
- **Aclaraciones 3 y 4:** de acuerdo con el plan; si el contrato y la capa no llegan para el 24/11, el adaptador pasa a diciembre.
- **Desvíos de `salida.py`:** aprobados.
