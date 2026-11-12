# Avance del bloque 2 — módulo de Voz (desde el 9/11)

**Última actualización:** 12/11/2026 · **Estado:** puntos 1 a 7 de la entrega del 9/11 hechos, y la actualización del 10/11 atendida completa, incluido el paquete 2.2.1 (ver al final). Siguen el 8 (recuperación) y el 9 (análisis de dos niveles).

Informe pedido por el "Brief para IA programadora — prototipo autónomo del módulo de Voz", para que Diego se lo pase al manager y a Claude. Se actualiza al cerrar cada semana. Sirve para que los documentos del grupo queden sincronizados con el código: lo que cambió en el repositorio está en "Estado de cada paso" y en "Decisiones consultadas"; lo que hay que decidir, en "Preguntas abiertas".

## Estado de cada paso

Orden de la entrega de Diego del 9/11.

| Punto | Estado | Archivos tocados | Commit |
|---|---|---|---|
| 1. Paquete `anima_spine` 2.2 y cohorte 2.0 | **Hecho** (9/11) | `anima_spine/` (copiado sin modificar), `cohorte_anima.csv`, `cohorte_anima.meta.json` | `0bb843d` |
| 2. Cohorte 1.1 reemplazada por la 2.0 | **Hecho** (9/11) | `tests/test_cohorte.py`, `tests/test_exportar_para_calibracion.py`, `src/tfc_voz/salida.py`; se retira el `voz_para_calibracion.csv` de la 1.1 | `0bb843d` |
| 3. Los ocho h² en un único archivo de configuración | **Hecho** (9/11) | `config/niveles_declarados.json`, `src/tfc_voz/niveles.py` (nuevo), `src/tfc_voz/parametros.py`, `tests/test_niveles.py` (nuevo) | `2db407f`, `6ca0267`, `a0a865f` |
| 4. Los dos niveles declarados en esa configuración | **Hecho** (9/11) | los mismos, más `scripts/calcular_segundo_nivel.py` (nuevo) | `2db407f`, `6ca0267`, `a0a865f` |
| 5. `voz_para_calibracion.csv` con 20 réplicas | **Hecho** (9/11), cuatro días antes del plazo del 13/11 | `scripts/exportar_para_calibracion.py`, `informes/voz_para_calibracion.meta.json`, `tests/test_exportar_para_calibracion.py`, `.gitignore` | `2941452`, `6ca0267` |
| 6. Etapa 3: modelo heterocedástico | **Hecho** (9/11) | `src/tfc_voz/modelo.py` y `src/tfc_voz/lineas_base.py` (nuevos), `tests/test_modelo.py` y `tests/test_lineas_base.py` (nuevos) | `b1297cb`, `0367e6d` |
| 7. Variantes conocidas, VZ-14 y VZ-15 | **Hecho** (9/11) | `src/tfc_voz/variantes.py` y `tests/test_variantes.py` (nuevos), `src/tfc_voz/fenotipo.py`, `tests/test_fenotipo.py`, `tests/test_lineas_base.py`, `scripts/exportar_para_calibracion.py`; genotipos en `datos/` (de Diego) | `6ca0267`, `78d7a65` |
| 8. `recuperacion_voz.csv` y criterio de recuperación | Sin empezar | — | — |
| 9. Análisis de dos niveles | Sin empezar | — | — |

Además: respuestas al avance del 29/10 (el oráculo pasa a `fenotipo.py`), commit `daeb485`; y la corrección de la cita de Campos et al. (2024) en `parametros.py`, el JSON, el README y `decisiones-fase1.md`, commits `6ca0267` y `a0a865f`.

### Punto 1: paquete 2.2 y cohorte 2.0

- El zip 2.2 ya trae la cohorte 2.0 con sus metadatos, así que el zip 2.0 no hizo falta.
- Huella del CSV: `8203824aff641fb8…abb6`. Coincide con la de los metadatos y con la de la entrega.
- La carga pasa por `spine.cargar` y `spine.verificar`.
- Suite del paquete: 43 pasan y 16 salteados. Los salteados son las pruebas de contrato de los módulos que todavía no exportaron.
- El módulo nunca usó `compare`, así que la clave `hipotesis_dos_niveles`, que el paquete ya no devuelve, no rompe nada.

### Punto 2: la 1.1 ya no se usa

- **El código no necesitó cambios:** `cohorte.py` toma las columnas del paquete, así que `origen` y `muestra_1000g` entraron solas.
- **CSV de la 1.1 retirado:** `voz_para_calibracion.csv` era de la 1.1 y salió del repo. Queda en el historial de git, en el commit `333940a`.
- **Test nuevo:** exige que la cohorte del repo sea la 2.0, con 503 personas reales repartidas 253 / 125 / 125 entre las particiones.

### Puntos 3 y 4: niveles declarados (configuración en la versión 1.2)

- **Dónde viven los valores:** `config/niveles_declarados.json` es el único lugar de donde salen los h². `parametros.py` los lee de ahí y ya no tiene ningún literal.
- **Caso base:** sin cambios, son las h² de siempre. Agregado: 7,07 %.
- **Segundo nivel:** es por parámetro y es entrada de la configuración.

  | Parámetro | Segundo nivel |
  |---|---|
  | f0_medio | 0,006086 |
  | f2 | 0,003436 |
  | f1 | 0,002278 |
  | Los otros cinco | 0 |
  | Agregado | 0,001475 (el 0,148 % de los documentos) |

  Los calcula una vez `scripts/calcular_segundo_nivel.py` (V por subpoblación). La composición de la cohorte 2.0 y su huella quedan registradas al lado.
- **El cargador verifica, no recalcula:**
  - Si la cohorte tiene otra composición, falla con un error que nombra la subpoblación y dice que hay que recalcular y volver a declarar el nivel.
  - Si `cohorte_anima.csv` no está, carga igual y el renglón del reporte dice "NO VERIFICADA".
- **Controles al cargar:**
  - los agregados;
  - que los conteos de la composición sumen n;
  - que el segundo nivel no supere la h² del caso base;
  - que el segundo nivel sea distinto de cero sólo donde hay una variante.
- **Renglón para el reporte:** `describir` da el nivel, el archivo, la versión, la fecha de fijación y si la composición se verificó.
- **Test de literales:** falla si uno de los niveles aparece escrito a mano en un `.py` del módulo, incluidos los tests.
  - Compara tokens completos y normalizados: `.1027` salta y `0.057` no cuenta como `0.05`.
  - Una línea se saltea sólo si termina en `# nivel-literal-ok: <motivo>`, con un motivo escrito.
  - Hoy hay tres líneas exentas, todas tolerancias de 0,05: dos en `test_exportar_para_calibracion.py` y una en `test_modelo.py`.
  - La de `test_modelo.py` la detectó el propio test al agregar `modelo.py`: el control funciona.
- **Salvedad de jitter y HNR:** quedó con la redacción de la tercera vuelta (0,05 como cota superior declarada). Hay una segunda salvedad que deja pendientes de verificar las cifras atribuidas a Campos et al.

### Punto 5: archivo para la capa de calibración

Esta tabla describe la **primera versión** del archivo, la de antes del punto 7. La vigente, con la misma forma y otra huella, está en "Punto 7".

| Dato | Valor |
|---|---|
| Archivo | `informes/voz_para_calibracion.csv` (15 MB, fuera de git) y `informes/voz_para_calibracion.meta.json` (en git) |
| Filas | 160.000: 1.000 personas de calibración y prueba × 8 parámetros × 20 réplicas |
| Columnas | `replica, semilla, dominio, sexo, individuo_id, particion, rasgo, y_real, mu_oraculo, sigma_oraculo` |
| Semilla | 20261019 + réplica |
| Nivel declarado | Caso base, configuración 1.2, composición verificada |
| Puntaje genético | Enteramente simulado, también en las 503 personas reales. Con el punto 7 se regeneró: ver "Nuevo `voz_para_calibracion.csv`" |
| Validación | OK: una fila por (individuo_id, rasgo, réplica), las 20 réplicas, la semilla de cada una, `dominio` = `voz`, ids, particiones y sexo iguales a los de la cohorte, valores finitos y `sigma_oraculo` > 0 |
| Huella SHA-256 | `b6f8d2d8867cf2f8a87945ac075558104315c508740b5c9400e7683db7631941` (primera versión; la vigente es `16ad6332…`) |
| Regeneración desde un clon limpio | **Idéntica byte a byte** (misma huella), con anima_spine 2.2, numpy 2.5.4, pandas 3.0.6 y Python 3.12.4. Las versiones quedan en el `.meta.json` |

El CSV no cambió con las versiones 1.1 y 1.2 de la configuración, porque el caso base es el mismo. Sólo se actualizó su `.meta.json`.

### Punto 6: Etapa 3

**`modelo.py`** es genérico y no sabe nada de voz:
- Estima la media y el logaritmo del desvío por máxima verosimilitud normal, con L-BFGS-B y gradiente analítico.
- Parte de mínimos cuadrados.
- Si el optimizador no converge, levanta `ErrorConvergencia` con el mensaje del optimizador. Nunca devuelve un ajuste sin convergencia.
- `ajustar` devuelve un objeto que se desempaqueta como `(beta, alfa)`, como dice el brief, y además guarda las iteraciones, que este informe tiene que reportar.

**`lineas_base.py`** arma los tres modelos de cada parámetro y los ajusta sólo con `entrenamiento`:
- `solo intercepto`, `ancestria sexo edad` (los nombres salen del paquete) y `completo`.
- Usa `edad_centrada` y `tramo60` de `fenotipo.py`. Un test verifica que son las mismas funciones y no una copia.
- Si el ajuste no converge, el error nombra el parámetro y el modelo.
- El modelo completo recibe la columna de puntaje genético que se le indique. Así el análisis de dos niveles (punto 9) puede pasarle sólo la parte conocida de g sin cambiar el código.

### Punto 7: variantes conocidas

**Cómo se arma g:** g = g_conocida + g_resto, en `fenotipo.py`, con los genotipos de `datos/genotipos_voz_1000g.csv`.
- **g_conocida** existe sólo en f0_medio, f1 y f2. Es β · (copias − 2·p_s), donde p_s es la frecuencia de la subpoblación de la persona según la configuración.
  - En las 503 personas reales, las copias salen del archivo.
  - En las simuladas, se sortean con una binomial de n = 2 y la p de su subpoblación.
- **g_resto** se genera con varianza h² − V, donde V es el segundo nivel declarado.
- **En los otros cinco parámetros** g_conocida vale 0 y g no cambia respecto del generador anterior.

**Qué no cambió:**
- Los números al azar se generan en el mismo orden que antes: primero g_resto, después e, y al final las copias de las simuladas.
- Por eso e quedó idéntica en los ocho parámetros, y los cinco sin variante dan exactamente los mismos valores que antes del punto 7.

**Guardas:**
- **Archivo de genotipos:** se verifica su huella contra el `.meta.json`, que haya una columna por variante y que las copias sean 0, 1 o 2.
- **Alineación del alelo de efecto:** la frecuencia observada en las reales se compara con la configurada, subpoblación por subpoblación. El mayor desvío es 0,0049, contra una tolerancia de 0,10.
- **Errores que levanta:** un alelo invertido (nombra la variante y no corrige nada), una persona real sin genotipo y V > h².

| Caso | Criterio | Medido |
|---|---|---|
| VZ-14.1 | En las 503 reales, g_conocida igual a la suma calculada a mano desde el archivo, persona por persona | Idéntica en las tres variantes, en las réplicas 0 y 7 |
| VZ-14.2 | En las simuladas, con 200.000 personas, frecuencia recuperada por subpoblación a menos de 0,01 de la configurada | Error máximo: 0,0025 (f0_medio), 0,0024 (f2), 0,0009 (f1) |
| VZ-14.3 | g_conocida = 0 en los cinco sin variante, y Var(g) = h² en los ocho (tolerancia 0,01, la de VZ-01 a VZ-04) | Cero exacto. Var(g) con 200.000 personas: error máximo 0,0005 (jitter, 0,0505 contra 0,0500). La varianza esperada cierra exacta: V + (h² − V) = h² con error menor que 10⁻⁶ |
| VZ-15 | Var(g_conocida) de f0_medio cerca de 0,006086, el valor exacto con el centrado por subpoblación (actualización del 10/11; coincide con el 0,61 % de Di et al., 2024); parar si se va por más de un factor de dos | 0,00627 en la cohorte 2.0, 0,00608 con 200.000 personas y 0,00608 en las 503 reales solas |

Var(g_conocida) en los otros dos parámetros, en la cohorte 2.0: f2 0,00344 (declarado 0,003436) y f1 0,00227 (declarado 0,002278).

**Nuevo `voz_para_calibracion.csv`:**
- Cambian `y_real` y `mu_oraculo` en f0_medio, f1 y f2; las columnas y la distribución son las mismas.
- Huella nueva: `16ad6332b03e46dbdf59b8871a2b2de123e1570e73837bcc42611052388a7a33`. La regeneración desde un clon limpio da idéntica byte a byte.
- El `.meta.json` describe g = g_conocida + g_resto y nombra la versión anterior. La anterior (huella `b6f8d2d8…`, con g enteramente simulado) se reproduce con el commit `577a0e5`.
- **Para Diego:** si todavía no se la mandaste a Tomás, conviene mandar la nueva. Si ya le mandaste la anterior, sigue siendo válida para sus tests: es la que acordamos para el viernes.

## Resultado del pytest completo

**388 tests: 388 pasan, 0 fallan, 0 salteados** (198 s, Python 3.12.4).

| Archivo | Tests | Qué cubre |
|---|---|---|
| `tests/test_fenotipo.py` | 117 | Etapa 2, VZ-01 a VZ-05 y VZ-07, oráculo |
| `tests/test_variantes.py` | 39 | Punto 7: VZ-14 (tres partes), VZ-15, réplicas, guardas de alineación, huella, persona sin genotipo y V > h² |
| `tests/test_lineas_base.py` | 80 | Etapa 3: línea base 2, modelo completo, g permutado, forma de los modelos, sólo entrenamiento, convergencia |
| `tests/test_poblacion.py` | 38 | Efectos poblacionales y referencias |
| `tests/test_generador.py` | 36 | VZ-01 a VZ-05 y VZ-07 sobre `genotipo.py` (su retiro se decide en la Etapa 8) |
| `tests/test_exportar_para_calibracion.py` | 20 | Archivo para la capa de calibración: contrato congelado del 10/11, forma, réplicas, sexo, metadatos y once rechazos |
| `tests/test_niveles.py` | 16 | Configuración de los niveles, verificación de la composición, test de literales |
| `tests/test_parametros.py` | 15 | h² contra la tabla S6 |
| `tests/test_modelo.py` | 10 | `modelo.py` con datos simulados, gradiente analítico contra numérico, error de convergencia |
| `tests/test_cohorte.py` | 9 | VZ-06, la cohorte del repo es la 2.0, rechazo de archivos mal formados |
| `tests/test_salida.py` | 8 | Formato de salida |

## Tests de la Etapa 3: pedido contra medido

`modelo.py`, con 20.000 casos simulados y una variable binaria que lleva σ de 1,0 a 1,5:

| Qué | Pedido | Medido | Tolerancia |
|---|---|---|---|
| α de la binaria | log 1,5 = 0,405 | 0,381 | 0,05 |
| β (constante, binaria, continua) | 0,5 / −1,0 / 0,3 | 0,511 / −1,016 / 0,291 | 0,05 |

`lineas_base.py`, con los valores de prueba de la Etapa 2 (d = −2, r = 0,8, c = 0,1, b_mujer = −0,3, b_hombre = 0,1, q_mujer = 0,2, q_hombre = 0,4) y 200.000 personas. Error máximo sobre los 8 parámetros, medido otra vez después del punto 7 (cambiaron f0_medio, f1 y f2):

| Qué | Pedido | Error máximo | Tolerancia |
|---|---|---|---|
| Línea base 2, media: d, b_mujer, b_hombre y b + q de cada sexo | los valores de prueba | 0,0139 | 0,02 |
| Línea base 2, dispersión: constante, sexo y edad | 0, log r, c | 0,0051 | 0,03 |
| Completo, dispersión: sexo y edad | log r, c | 0,0044 | 0,03 |
| Completo, α₀ | ½ · log(1 − h²) | 0,0036 | 0,02 |
| Completo con c = 0, coeficiente de g | 1 | 0,0212 | 0,03 |
| Completo con c = 0, coeficiente de g · sexo | r − 1 = −0,2 | 0,0174 | 0,03 |
| Completo con g permutado, coeficiente de g | 0 | 0,0184 | 0,02 |

## Convergencia del optimizador

Máximo de iteraciones sobre los 8 parámetros, medido después del punto 7. Ningún ajuste dejó de converger.

| Modelo | Valores de prueba, 200.000 personas | Efectos reales, cohorte 2.0 (1.000 de entrenamiento), réplica 0 |
|---|---|---|
| `solo intercepto` | Convergió, 0 iteraciones | Convergió, 0 iteraciones |
| `ancestria sexo edad` | Convergió, 22 | Convergió, 33 |
| `completo` | Convergió, 31 | Convergió, 42 |

`solo intercepto` termina en 0 iteraciones porque el punto de partida ya es su máximo de verosimilitud: la media y el desvío de la muestra.

**Coeficiente de g · edad_c con los efectos reales** (c = 0, así que tiene que dar cerca de 0): f0_medio 0,016, f0_variabilidad 0,065, jitter −0,123, hnr −0,029, f1 −0,043, f2 −0,059, f3 0,030, vtl −0,037. Con 1.000 personas de entrenamiento, su error típico calculado es de alrededor de 0,08 en los parámetros de h² más baja. Todos son compatibles con cero; el mayor, jitter, queda a 1,6 errores típicos.

## Decisiones consultadas

| Fecha | Consulta | Respuesta |
|---|---|---|
| 9/11 | ¿El punto 7 choca con la regla de no descargar datasets? | Sí. La regla sigue en pie y Diego pasa los genotipos como archivo. Llegaron el 9/11 y están en `datos/`, no en `anima_spine/datos/`, para no mezclar datos de Voz con el paquete del grupo |
| 9/11 | ¿El CSV del punto 5 puede salir antes de las variantes conocidas? | Sí, con una nota que lo declare. Se regenera cuando entre el punto 7 |
| 9/11 | ¿Se saca el control propio de `salida.py` sobre las dos líneas base, ahora que lo exige el paquete? | No: queda, redundante a propósito |
| 9/11 | Formato y valores de los niveles declarados | `config/niveles_declarados.json`. El caso base son las h² de siempre; el segundo nivel es por parámetro, y el 0,148 % es su promedio |
| 9/11 | La salvedad de jitter y HNR pedía confirmarlos contra la S6 | No están en la S6. Se cierra como valor declarado: 0,05 como cota superior, deliberadamente generosa, porque Campos et al. (2024) no encuentran diferencia entre gemelas monocigóticas y dicigóticas |
| 9/11 | La cita "Lima et al. 2024" | Era un error. Es Campos, Luchesi, Lucci, Otta y Monticelli (2024), *Social Sciences & Humanities Open*, 10, 101062. Corregida en cuatro archivos |
| 9/11 | Nota del CSV en `.meta.json` en vez de `LEEME.md` | Aprobado |
| 9/11 | CSV de 15 MB fuera de git | Aprobado, con la condición de verificar la regeneración desde un clon limpio. Verificada: idéntica |
| 9/11 | El test de literales excluía `tests/` | Demasiado amplio. Ahora recorre `tests/`, con exención por línea anotada. Los ceros del segundo nivel siguen fuera |
| 9/11 | El centrado de g_conocida por subpoblación no cerraba con V calculado con la frecuencia europea promedio (diferencia de 0,00007 en f0_medio) | Error de especificación. V se calcula con la misma p por subpoblación, ponderada por la composición de la cohorte |
| 9/11 | Calcular V al cargar ataba la configuración a la cohorte | Tercera vuelta: calcularlo al cargar haría que el nivel declarado se moviera en silencio. Los valores vuelven a ser entrada, la composición queda registrada y el cargador la verifica. `--generar-cohorte` con otra composición tiene que fallar |

## Desvíos respecto de la entrega y del brief

- **Decisión tomada sin consultar (punto 7): en cada réplica se vuelven a sortear las copias de las personas simuladas.** Las de las reales son siempre las del archivo. La entrega no lo dice. Lo resolví así porque cada réplica regenera todo lo que depende del azar del módulo, como pide el paquete. Si se prefiere que las simuladas tengan un genotipo fijo, como si fueran personas con genoma, es un cambio de pocas líneas: sortearlas con una semilla que no dependa de la réplica.
- **Cambié la tolerancia de un test que había escrito yo**, `test_columna_g_elige_el_puntaje_del_completo`, de 10⁻⁴ a 10⁻³. Con la g nueva, duplicar g dejó el coeficiente en la mitad con un error relativo de 2·10⁻⁴. Diagnóstico: con un criterio de parada más estricto en L-BFGS-B (ftol = 10⁻¹⁵), el error baja a 6·10⁻⁸, así que es la precisión con la que se detiene el optimizador. Equivale a unos 0,0003 en el coeficiente, mucho menos que su error típico (alrededor de 0,08). No es una tolerancia del brief.
- **`ajustar` devuelve un objeto que guarda las iteraciones.** El brief dice que devuelve β y α; el objeto se desempaqueta así, como pide el brief. Hacía falta porque este informe tiene que reportar las iteraciones. También acepta `max_iteraciones`, que usa el test de no convergencia.
- **`ajustar` controla que la primera columna de `X_sigma` sea la constante**, porque el punto de partida pone ahí el logaritmo del desvío.
- **`lineas_base.py` se hizo en la semana del 9/11**, junto con `modelo.py`, como parte del punto 6. El plan del 29/10 lo ponía en la semana del 10/11.
- **La cita de Campos se corrigió en cuatro archivos**, no en los dos que se pidieron: el README y `decisiones-fase1.md` tenían el mismo error.
- **La tabla de archivos del README no está al día:** faltan `niveles.py`, `modelo.py`, `lineas_base.py`, `config/` y `scripts/calcular_segundo_nivel.py`. Se completa en la Etapa 8, o antes si se prefiere.

## Preguntas abiertas

1. **El test de g permutado es frágil, aunque hoy pase.** Con la semilla fija, el peor parámetro da 0,0184 contra una tolerancia de 0,02. Para diagnosticarlo, reajusté el modelo completo con 40 permutaciones distintas por parámetro, sin cambiar la semilla del test:

   | Parámetro | h² | Coeficiente con la semilla del test | Desvío entre permutaciones | Permutaciones con \|coef\| > 0,02 |
   |---|---|---|---|---|
   | f0_medio | 0,1027 | −0,0065 | 0,0106 | 5 % |
   | f0_variabilidad | 0,0410 | +0,0071 | 0,0188 | 30 % |
   | jitter | 0,0500 | −0,0169 | 0,0142 | 15 % |
   | hnr | 0,0500 | −0,0068 | 0,0140 | 15 % |
   | f1 | 0,0619 | +0,0036 | 0,0131 | 8 % |
   | f2 | 0,1353 | +0,0005 | 0,0115 | 5 % |
   | f3 | 0,0644 | +0,0081 | 0,0113 | 10 % |
   | vtl | 0,0606 | +0,0184 | 0,0132 | 18 % |

   Valores medidos con el generador del punto 7. La tolerancia de 0,02 queda entre 1 y 1,9 desvíos, y con 8 parámetros, un modelo correcto falla en alguno con la mayoría de las permutaciones posibles. El desvío es alto porque las interacciones g · sexo y g · edad_c le restan precisión al coeficiente de g.

   El test con c = 0 tiene el mismo problema, aunque más chico: el coeficiente de g tiene un desvío del mismo orden, y su tolerancia de 0,03 queda en 1,6 a 2,8 desvíos (el error medido fue 0,0212).

   No cambié la tolerancia. Hay tres alternativas para que decida el manager:
   - (a) fijar la tolerancia en desvíos, por ejemplo 4 desvíos, que da entre 0,045 y 0,075;
   - (b) evaluar el promedio sobre las 20 semillas del barrido, como se hace con la cobertura;
   - (c) dejarlo como está, sabiendo que es un control débil.

2. **Hay una contradicción sobre el corrimiento esperado del ΔR² parcial.** Conviene resolverla antes del punto 8.
   - El control de integración del brief (ajustes del 29/10) dice que el promedio de 20 réplicas queda **entre 0,002 y 0,004 por debajo** de la h², según una simulación de Claude.
   - El README de `anima_spine` 2.2 dice que, en el dominio vocal, el parcial sale **entre 0,0064 y 0,0087 por encima** del nivel declarado. La causa es que la línea base se estima en entrenamiento y se evalúa fuera de la muestra.

   Las dos no pueden ser ciertas a la vez. No cambia el código, pero sí qué resultado se espera.

3. **El control de integración y el criterio de recuperación miden casi lo mismo.**
   - El control de integración del 29/10 compara el ΔR² parcial promedio con la h², con tolerancia 0,025.
   - El criterio de recuperación del paquete 2.2 compara el mismo ΔR² parcial promedio con el nivel declarado del caso base, que es la misma h², con tolerancia 0,015.

   Propuesta: el criterio de recuperación reemplaza al control de integración, y la tabla por parámetro que pedía el control se informa con la tolerancia del paquete. Si se quieren los dos, conviene declarar para qué sirve cada uno.

4. **Los puntos 8 y 9 necesitan piezas que el plan del 29/10 ponía en la semana del 17/11:** `replicas.py` (tabla predictiva y réplicas) y las funciones de ΔR² de `metricas.py`. Con el orden de la entrega, las adelanto a esta semana como parte del punto 8. Si se prefiere mantener el calendario anterior, el punto 8 pasa a la semana del 17/11.

5. **Confirmar una decisión del punto 7, tomada sin consultar:** en cada réplica se vuelven a sortear los genotipos de las personas simuladas; los de las reales son siempre los del archivo (ver "Desvíos"). No frena el punto 8.
   - Si se confirma, no hay nada que cambiar.
   - Si se prefiere que las simuladas tengan un genotipo fijo, es un cambio chico, pero cambia el CSV para Tomás.

6. **Pendiente de Diego, ya anotado:**
   - ~~verificar las cifras de Campos et al. y las iniciales~~: cerrado el 10/11, las cifras son exactas;
   - la nota de jitter y HNR en el Anexo B del integrado y en el individual, con el texto definitivo del 10/11;
   - los porcentajes que se mueven: 0,61 % en f0_medio y 0,23 % en f1.

7. **"Estas once" columnas, pero la lista trae diez** (actualización del 10/11, punto 1). El archivo tiene exactamente las diez listadas, en ese orden. Si falta una undécima, hay que decir cuál.

8. **¿`metricas.py` lleva la función de cobertura?** La actualización del 10/11 dice "nada de q̂, intervalos conformales ni cobertura en tu código". Pero la Etapa 5 del brief pide `cobertura(y, lo, hi)` en `metricas.py`, y la Etapa 4 hace que VZ-10 se informe desde el módulo. Mi lectura es que la cobertura la calcula el paquete (`predictions.cobertura_promedio` y `fila_barrido`) y `metricas.py` queda sólo con ΔR², CRPS y bootstrap. Necesito que lo confirmen antes de escribir `metricas.py`, que es parte del punto 8.

## Actualización del 10/11 (atendida el 12/11)

| Punto | Qué se hizo | Commit |
|---|---|---|
| 1. Formato exacto del archivo para la calibración | **Ya cumplía, no hubo que regenerarlo.** Lo verifiqué sobre el archivo: las 10 columnas con esos nombres y en ese orden, 160.000 filas sólo de `calibracion` y `prueba`, `individuo_id` entero en todas las filas y los ocho nombres de rasgo exactos. Un test nuevo fija ese contrato y que los ids se escriban como enteros. Huella sin cambios: `16ad6332…`. **Estaba listo desde el 9/11, así que no hace falta el plan B** | `a0c5ef5` |
| 2. Jitter y HNR | Salvedad del JSON reemplazada por el texto definitivo, y las cifras de Campos dejan de figurar como pendientes. Corregí también `parametros.py` y `decisiones-fase1.md`: decían "sin diferencia entre MZ y DZ", que el estudio no permite afirmar. Configuración 1.3, sin cambios de valores | `a0c5ef5` |
| 3. Paquete 2.2.1 | **Hecho el 12/11.** Comparado archivo por archivo con la 2.2, sólo cambian `power_gradiente.py` y el número de versión: `predictions.py`, `compare.py`, `spine.py`, el panel y la cohorte son idénticos. Suite del paquete: 43 pasan y 16 salteados. Borré el zip 2.2 del repo y su copia extraída. Las copias que hay en Descargas (2.1 y 2.2) no las toqué, porque están fuera del proyecto. El `.meta.json` del CSV ahora dice 2.2.1; la huella del CSV no cambió | `8301e8f` |
| 4. VZ-15 | La referencia del test es ahora el segundo nivel declarado de f0_medio (0,006086), leído de la configuración. Los valores medidos no cambian | `a0c5ef5` |
| 5. Calibración | Nada que hacer: el módulo no tiene q̂, intervalos conformales ni cálculo de cobertura. La forma congelada de la sigma (logaritmo de sigma con sexo y edad centrada) es la que ya usa `lineas_base.py`: `X_sigma` = 1, sexo, edad_c | — |

## Siguiente paso

Punto 8: `recuperacion_voz.csv` y el criterio de recuperación. Para arrancarlo necesito respuesta a las preguntas abiertas 2, 3, 4 y 8. La 1, la 5 y la 7 no lo frenan.
