# Propuestas de diseño que surgieron en la Etapa 2

**Fecha:** 23/10/2026 · **Estado:** a decidir con el manager. Ninguna bloquea el bloque actual: la 1 importa en la Etapa 5 y en el contraste entre dominios; la 2, en cómo se informan los casos VZ.

## 1. El orden por ΔR² (VZ-13) refleja el tamaño del efecto del sexo, no la h²

**Qué se pide decidir:** si, además del ΔR² sobre la varianza total que pide el brief, se informa el **ΔR² parcial**, ΔR² / (1 − R² de la línea base). No reemplaza al ΔR²: se agrega como columna en VZ-11 y VZ-13 y, si el grupo lo ve útil, en el contraste entre dominios.

### Resultado

Techo teórico con los efectos reales de `poblacion.py`, 200.000 personas, semilla 20261019. Como predictores se usaron la media y el score genético **verdaderos**, así que es el máximo que podría dar el modelo, no un resultado del prototipo. Ordenado por ΔR²:

| Parámetro | h² | R² de la línea base (sexo + edad) | ΔR² sobre varianza total | Orden por ΔR² | ΔR² parcial | Orden por h² |
|---|---|---|---|---|---|---|
| f2 | 0,1353 | 0,613 | 0,0531 | 1 | 0,1372 | 1 |
| jitter | 0,0500 | 0,047 | 0,0480 | 2 | 0,0504 | 6–7 |
| hnr | 0,0500 | 0,149 | 0,0424 | 3 | 0,0498 | 6–7 |
| f0_variabilidad | 0,0410 | 0,120 | 0,0367 | 4 | 0,0417 | 8 |
| f1 | 0,0619 | 0,498 | 0,0315 | 5 | 0,0626 | 4 |
| f0_medio | 0,1027 | 0,736 | 0,0272 | 6 | 0,1029 | 2 |
| f3 | 0,0644 | 0,604 | 0,0243 | 7 | 0,0613 | 3 |
| vtl | 0,0606 | 0,730 | 0,0161 | 8 | 0,0594 | 5 |

- **f0_medio**, con la segunda h² más alta, queda **sexto** por ΔR². **jitter**, con una de las más bajas, queda **segundo**.
- El ΔR² parcial recupera la h² inyectada en los 8 parámetros, con diferencias menores a 0,005.
- Promedio de Voz: ΔR² sobre varianza total **0,035**; h² **0,071**. Con este cálculo, el aporte del genotipo en Voz sale a la mitad de su h².

### Por qué pasa

El brief ya lo anticipa en la Etapa 5: contra la línea base de ancestría, sexo y edad, el ΔR² da aproximadamente h² · (1 − R² de la línea base). La consecuencia que no está escrita es que **el orden entre parámetros queda gobernado por cuánto explica el sexo**:

- f0_medio, VTL y los formantes tienen una diferencia muy grande entre sexos (d de −4 a +3,4 desvíos). La línea base les explica entre el 50 % y el 74 % de la varianza, y lo que queda para el genotipo se achica en esa proporción.
- jitter, hnr y la variabilidad de F0 casi no difieren entre sexos. La línea base explica poco y el ΔR² queda cerca de la h².

VZ-13 ("tabla de los 8 parámetros ordenados por ΔR² decreciente") va a mostrar ese orden, y se puede leer como "el genotipo informa más sobre el jitter que sobre la F0", que no es lo que dice la h².

### Por qué importa para el grupo

El contraste entre dominios promedia el ΔR² de cada dominio sobre la varianza total. Si en un dominio la línea base explica mucho (Voz, por la diferencia entre sexos) y en otro poco (por ejemplo, Temperamento), parte de la diferencia de ΔR² entre dominios viene de la línea base y no del genotipo. No cambia la dirección de la hipótesis de dos niveles, pero conviene tenerlo en cuenta al leer el contraste.

### Opciones

1. **Informar las dos columnas (recomendado).** ΔR² sobre varianza total, como pide el brief, y ΔR² parcial al lado. VZ-13 se ordena por el ΔR² del brief y la columna de h² inyectada, que el brief ya pide, deja ver la diferencia.
2. **Dejarlo como está y declararlo en el reporte:** el orden de VZ-13 depende del tamaño de los efectos poblacionales.
3. **Llevarlo al grupo** para que el contraste entre dominios (`anima_spine/compare.py`) decida si usa también el parcial. Es una decisión común a los tres módulos, no de Voz.

Ninguna de las tres cambia el modelo ni sube el ΔR²: son formas de informar el mismo resultado.

## 2. VZ-01 a VZ-05 y VZ-07 prueban un generador que el prototipo no usa

**Qué se pide decidir:** si los casos VZ-01 a VZ-05 y VZ-07 pasan a probarse sobre `fenotipo.py`, que es el generador del prototipo, en lugar de (o además de) `genotipo.py`.

### Situación

- Hoy VZ-01 a VZ-05 y VZ-07 corren sobre `genotipo.py`, el generador de la Opción A del brief anterior. El brief del prototipo lo deja como está ("Existe, no tocar").
- El prototipo genera sus fenotipos con `fenotipo.py`, que tiene otra semilla por parámetro, otro modelo (efectos de sexo, edad y subpoblación) y otro formato.
- La Etapa 2 ya prueba sobre `fenotipo.py` lo mismo que VZ-01 a VZ-04: con 200.000 personas, la h² recuperada dentro de cada sexo queda a menos de 0,01 de la pedida en los 8 parámetros.
- Sobre `fenotipo.py` **no** hay un control de permutación (VZ-05) ni un barrido de 20 semillas (VZ-07).

### Opciones

1. **Pasar los casos a `fenotipo.py` (recomendado).** VZ-01 a VZ-04 apuntan al test de h² dentro de cada sexo de la Etapa 2, y se agregan VZ-05 (permutación) y VZ-07 (20 semillas, 20261019 + 0…19) sobre `fenotipo.py`, con los mismos criterios de hoy. `genotipo.py` y sus tests quedan como están hasta que el grupo decida retirarlos.
2. **Dejarlo como está y declararlo:** VZ-01 a VZ-05 y VZ-07 validan el generador de la Opción A, no el del prototipo.

Con la opción 1, los resultados que se informan en la Práctica y en el documento individual corresponden al código que produce `predicciones_voz.csv`.
