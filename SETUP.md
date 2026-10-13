# Puesta en marcha del entorno -- modulo de Voz

Todo esto se hace una sola vez. Al final tenes que ver el mensaje
`Entorno listo para la Fase 1.`

---

## 0. Antes de empezar: la unica trampa real

De las cuatro librerias, tres se instalan sin drama. **`pyworld` es la
excepcion**: su ultima version solo publica paquetes precompilados para
Python 3.6, 3.7 y 3.8. En cualquier Python mas nuevo, pip lo va a
**compilar desde el codigo fuente**, y para eso necesita un compilador de
C++ instalado en el sistema.

Si no lo tenes, el error va a aparecer reciEn a mitad de la instalacion y
dice algo como `error: Microsoft Visual C++ 14.0 or greater is required`
(Windows) o `command 'gcc' failed` (Linux/macOS).

Por eso el paso 1 es instalar el compilador ANTES que nada.

---

## 1. Instalar el compilador de C++

**Windows**
1. Bajar **Microsoft C++ Build Tools**:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. En el instalador, tildar la carga de trabajo **"Desarrollo para el
   escritorio con C++"** (Desktop development with C++).
3. Instalar y **reiniciar la terminal** (no hace falta reiniciar Windows,
   pero si cerrar y abrir la consola).

**macOS**
```
xcode-select --install
```

**Linux (Ubuntu/Debian)**
```
sudo apt install build-essential python3-dev
```

---

## 2. Verificar la version de Python

```
python --version
```

Apuntar a **Python 3.11 o 3.12**. Es la zona segura: 3.11 esta verificado
funcionando con todo el stack. Evitar 3.13+ por ahora -- `pyworld` no tiene
paquetes precompilados y su compilacion en versiones muy nuevas es menos
probada.

Si tenes otra version instalada, se puede tener varias en paralelo sin
romper nada (en Windows con el instalador oficial, en macOS/Linux con
pyenv o el gestor del sistema).

---

## 3. Crear la carpeta del proyecto y el entorno virtual

El entorno virtual mantiene las librerias del TFC separadas del Python
del sistema. Si algo se rompe, se borra la carpeta `.venv` y se rehace,
sin tocar nada mas.

```
mkdir tfc-anima-voz
cd tfc-anima-voz
python -m venv .venv
```

Activarlo:

**Windows (PowerShell)**
```
.venv\Scripts\Activate.ps1
```
Si PowerShell se queja con `execution of scripts is disabled`, correr una
sola vez:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Windows (CMD)**
```
.venv\Scripts\activate.bat
```

**macOS / Linux**
```
source .venv/bin/activate
```

Cuando esta activo, el prompt arranca con `(.venv)`. **Hay que activarlo
cada vez que abris una terminal nueva** para trabajar en el proyecto.

---

## 4. Copiar los archivos del proyecto

Dejar esta estructura dentro de `tfc-anima-voz`:

```
tfc-anima-voz/
├── requirements.txt
├── SETUP.md
├── decisiones-fase1.md
├── src/
│   └── tfc_voz/
│       ├── __init__.py
│       ├── parametros.py
│       ├── genotipo.py
│       └── extraccion.py
└── tests/
    └── test_setup.py
```

---

## 5. Instalar las librerias

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

La instalacion de `pyworld` es la lenta (esta compilando). Es normal que
tarde y que escupa varias lineas de warnings del compilador; lo que importa
es que termine en `Successfully installed`.

---

## 6. Correr el chequeo

```
python tests/test_setup.py
```

Salida esperada:

```
    version: 0.4.7
[OK] parselmouth (import)
    version: 3.1.3
[OK] flask (import)
    numpy 2.4.4, scipy 1.17.1
[OK] numpy + scipy (import)
    analisis+sintesis OK -- 101 frames de F0 estimados
[OK] pyworld (analisis + sintesis real, no solo import)

Entorno listo para la Fase 1.
```

El ultimo chequeo es el importante: no alcanza con que `import pyworld`
no tire error, hay que confirmar que el binding en C++ realmente corre
haciendo un analisis + sintesis de verdad.

---

## 7. Descargar VCTK

https://datashare.ed.ac.uk/handle/10283/3443 (version 0.92)

Pesa varios GB, conviene dejarlo bajando en segundo plano mientras se hace
el resto. Al descomprimir, chequear que este el archivo `speaker-info.txt`
-- trae edad, sexo y acento por hablante, y el **sexo es obligatorio** para
la extraccion (define el rango de busqueda de F0).

---

## 8. Primera prueba de extraccion

Con el entorno activo y VCTK descargado:

```
python src/tfc_voz/extraccion.py <ruta-a-un-wav-de-vctk> F
```

(el ultimo argumento es `M` o `F` segun el hablante, sacado de
`speaker-info.txt`)

Deberia imprimir los 8 parametros y, al final, si paso los controles de
plausibilidad.

---

## Si algo falla

| Sintoma | Causa casi segura |
|---|---|
| `Microsoft Visual C++ 14.0 or greater is required` | Falta el paso 1 |
| `command 'gcc' failed` / `Python.h: No such file` | Falta `build-essential` / `python3-dev` |
| `execution of scripts is disabled` (PowerShell) | Ver el `Set-ExecutionPolicy` del paso 3 |
| `pip` instala pero `import` falla | El entorno virtual no esta activado |
| Extraccion con advertencias de plausibilidad | Ver la nota de abajo |

**Sobre las advertencias de plausibilidad:** `extraccion.py` chequea que F1,
F2, F3 y VTL caigan en rangos razonables. Si saltan advertencias, lo mas
probable NO es que la voz sea rara, sino que el tracking de formantes
inserto un formante espurio y corrio la numeracion (F2 pasa a ser F3, etc.).
Se corrige ajustando `maximum_formant` para ese hablante. Conviene contar
cuantos archivos del corpus disparan advertencias antes de decidir si hay
que afinar los parametros globalmente.
