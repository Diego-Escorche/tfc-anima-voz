# Propuesta de diseño: cómo medir "a edad fija" en los tests de la Etapa 2

**Fecha:** 23/10/2026 · **Estado:** a decidir con el manager antes de empezar la Etapa 2.

**Qué se pide decidir:** en los tests de `fenotipo.py`, comparar sexos "a edad fija" usando a toda la muestra y descontando la edad con el modelo, en vez de quedarse sólo con las personas de una misma edad. Las tolerancias del brief no cambian; cambia el método con que se estima cada valor.

## Resultado

Simulación: 200 repeticiones de 200.000 personas, con los valores de prueba de la Etapa 2 del brief (d = −2, r = 0,8, c = 0,1, b_mujer = −0,3, b_hombre = +0,1, q_hombre = +0,4). El generador simulado es correcto por construcción, así que cada falla es una falsa alarma del test.

| Forma de comparar | Personas que usa | Sesgo | Ruido (error típico) | Falla con tolerancia 0,02 |
|---|---|---|---|---|
| **d**, literal: sólo personas de 49 años | ~1.600 por sexo | +0,002 | 0,031 | **52 %** |
| **d**, cruda: todos, sin descontar la edad | ~100.000 por sexo | +0,134 | 0,005 | **100 %** |
| **d**, ajustada (propuesta) | ~100.000 por sexo | +0,001 | 0,006 | **0 %** |
| **r**, literal | ~1.600 por sexo | −0,002 | 0,019 | 33 % |
| **r**, cruda | ~100.000 por sexo | −0,017 | 0,003 | 12 % |
| **r**, ajustada (propuesta) | ~100.000 por sexo | −0,000 | 0,003 | 0 % |

Con la lectura literal, un generador perfecto fallaría el test de d la mitad de las veces. Con la propuesta, el error típico queda entre 4 y 7 veces por debajo de la tolerancia.

## El problema

El brief pide que, "a edad fija", la diferencia de medias entre sexos quede a menos de 0,02 de d y el cociente de desvíos a menos de 0,02 de r. En el modelo generativo, la media depende del sexo **y** de la edad, con pendientes distintas por sexo:

```
m = d·sexo + [b_mujer·(1−sexo) + b_hombre·sexo]·edad_c + [q_mujer·(1−sexo) + q_hombre·sexo]·tramo60
s = r^sexo · exp(c·edad_c)
```

d es la distancia entre hombres y mujeres **a una misma edad**. Hay tres maneras de estimarla:

1. **Literal: sólo las personas de una edad.** No tiene sesgo, pero con edades uniformes entre 18 y 80 quedan unas 1.600 personas por sexo de 200.000. El ruido (0,031) supera la tolerancia (0,02).
2. **Cruda: el promedio de todos los hombres menos el de todas las mujeres.** Tiene poco ruido, pero mezcla d con el efecto de la edad. Desde los 60, los hombres suben 0,5 por década y las mujeres no, y eso tira el promedio de los hombres hacia arriba: sale −1,866 en lugar de −2.
3. **Ajustada (propuesta): todos, descontando la edad con el modelo.** No tiene sesgo y tiene poco ruido.

## La propuesta

- **d y las pendientes de edad:** una regresión de y sobre sexo, edad_c y tramo60, con las dos últimas por separado en cada sexo. El coeficiente del sexo es la distancia entre sexos a los 49 años (edad_c = 0, tramo60 = 0), es decir, "a edad fija". Los coeficientes de edad dan b antes de los 60 y b + q después. Se estiman de los datos, sin usar los valores verdaderos.
- **r:** cada residuo de esa regresión se divide por exp(c · edad_c), con el c del test. Así todas las personas quedan como si tuvieran la misma edad, y se compara el desvío de los hombres con el de las mujeres.

## Por qué funciona

El error de un test tiene dos partes: **sesgo** (mide otra cosa, siempre igual) y **ruido** (el azar de qué personas tocaron). El ruido de un promedio baja con la raíz de la cantidad de personas: pasar de ~1.600 a ~100.000 por sexo es usar 63 veces más gente, y el ruido se divide por √63 ≈ 8. Descontar la edad es lo que permite usar a todos sin meter el sesgo de la forma cruda.

Traducido a probabilidad de falla, lo que cuenta es cuántos errores típicos entran en la tolerancia:

| Test | Tolerancia / ruido | Falsa alarma esperada |
|---|---|---|
| d literal | 0,02 / 0,031 ≈ 0,6 | ~1 de cada 2 corridas |
| d ajustada | 0,02 / 0,0056 ≈ 3,6 | ~1 de cada 3.000 corridas |
| r ajustada | 0,02 / 0,0028 ≈ 7 | prácticamente nunca |

La forma cruda de r falla sólo el 12 % de las veces, pero porque su sesgo (−0,017) queda justo debajo de la tolerancia: pasa sin medir r, y un cambio chico en los valores de prueba la haría fallar siempre.

## Alternativas descartadas

- **Mantener la lectura literal con una cohorte más grande.** Para que el ruido de d baje a 0,005 harían falta unas 65.000 personas por sexo **en cada edad**: unos 8 millones en total. No es práctico.
- **Mantener la lectura literal con una banda de edades** (por ejemplo, de 45 a 55). Gana personas, pero dentro de la banda las pendientes de edad siguen siendo distintas entre sexos y vuelve el sesgo.
- **Aflojar la tolerancia.** El brief no lo permite sin justificar, y un test con tolerancia 0,06 dejaría pasar errores reales del generador.

## Condición y límite

El ajuste usa la forma del modelo: edad y tramo de más de 60 años por sexo, y c para la dispersión. Es válido porque el test controla justamente que el generador aplique esa forma. Si el generador aplicara mal la edad, lo detectarían los tests de las pendientes, que el brief también pide.

## Cómo reproducir la simulación

```python
import numpy as np
d, r, c, bM, bH, qM, qH = -2, 0.8, 0.1, -0.3, 0.1, 0, 0.4
N, REP = 200_000, 200
rng = np.random.default_rng(1)
for _ in range(REP):
    edad = rng.integers(18, 81, N); sexo = rng.integers(0, 2, N)
    ec = (edad - 49) / 10; tr = np.maximum(0, edad - 60) / 10
    m = d*sexo + (bM*(1-sexo) + bH*sexo)*ec + (qM*(1-sexo) + qH*sexo)*tr
    y = m + r**sexo * np.exp(c*ec) * rng.standard_normal(N)
    # literal: solo edad == 49 · cruda: medias y desvios por sexo con todos
    # ajustada: regresion y ~ [1, sexo, ec(1-sexo), ec·sexo, tr(1-sexo), tr·sexo];
    #           d = coeficiente de sexo; r = cociente de desvios de residuo / exp(c·ec)
```
