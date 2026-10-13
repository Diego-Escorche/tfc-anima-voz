# Puesta en marcha del entorno -- modulo de Voz

Todo esto se hace una sola vez. Al final tenes que ver el mensaje
`Entorno listo para la Fase 1.`

**Verificado el 12 oct 2026** en Windows 11 con Python 3.12.4. Ver
`informe-fase1.md` para el detalle de esa instalacion y de la primera
extraccion sobre VCTK.

---

## 0. Antes de empezar: pyworld y el compilador de C++

De las cuatro librerias, tres se instalan sin drama. **`pyworld` era la
excepcion**: las versiones viejas solo publicaban paquetes precompilados
hasta Python 3.8, y en cualquier Python mas nuevo pip lo compilaba desde el
codigo fuente (lo que requiere un compilador de C++).

**Esto ya no es asi.** `pyworld` 0.3.5 publica paquetes precompilados para
Python 3.12 y 3.13 en Windows (`cp312`/`cp313-win_amd64`), asi que pip lo
baja listo y **no hace falta compilador**. Confirmado en la instalacion del
12 oct 2026: se instalo `pyworld-0.3.5-cp312-cp312-win_amd64.whl`, sin
compilar nada.

El compilador solo hace falta si pip no encuentra un paquete precompilado
para tu combinacion de sistema y version de Python. Te das cuenta porque la
instalacion de pyworld tarda mucho y aparece un error como
`error: Microsoft Visual C++ 14.0 or greater is required` (Windows) o
`command 'gcc' failed` (Linux/macOS). En ese caso instalalo asi:

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

## 1. Verificar la version de Python

Apuntar a **Python 3.11 o 3.12**. Las dos estan verificadas con todo el
stack (3.12.4 es la del entorno actual). 3.13 tiene paquete precompilado de
pyworld pero no esta probada con el resto del proyecto.

**Windows: ojo con `python`.** Si al correr `python --version` aparece
`no se encontro Python; ejecutar sin argumentos para instalar desde el
Microsoft Store`, ese `python` es un acceso directo de la Store, no un
interprete real. Usar el launcher `py`, que viene con el instalador oficial:

```
py -0p          # lista las versiones instaladas
py -3.12 --version
```

**macOS / Linux**
```
python3 --version
```

Se pueden tener varias versiones en paralelo sin romper nada (en Windows con
el instalador oficial, en macOS/Linux con pyenv o el gestor del sistema).

---

## 2. Crear el entorno virtual

El entorno virtual mantiene las librerias del TFC separadas del Python
del sistema. Si algo se rompe, se borra la carpeta `.venv` y se rehace,
sin tocar nada mas.

Parado en la carpeta del proyecto (`tfc-anima-voz`):

**Windows**
```
py -3.12 -m venv .venv
```

**macOS / Linux**
```
python3.12 -m venv .venv
```

### Activarlo (opcional)

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

**Alternativa sin activar:** llamar directo al Python del entorno. Es lo que
se uso en la instalacion verificada y evita el tema de la politica de
ejecucion de PowerShell:
```
.venv\Scripts\python.exe tests\test_setup.py      # Windows
.venv/bin/python tests/test_setup.py              # macOS / Linux
```
En el resto de esta guia, `python` significa "el Python del entorno", ya sea
con el venv activado o con la ruta completa.

---

## 3. Estructura del proyecto

```
tfc-anima-voz/
├── .gitignore               # excluye .venv/, data/ y __pycache__/
├── README.md                # contexto completo del proyecto
├── SETUP.md
├── decisiones-fase1.md
├── informe-fase1.md
├── seguimiento-modulo-voz.md
├── requirements.txt
├── src/
│   └── tfc_voz/
│       ├── __init__.py
│       ├── parametros.py
│       ├── genotipo.py
│       └── extraccion.py
├── tests/
│   └── test_setup.py
├── data/                    # NO versionado: corpus descargados
│   └── VCTK-Corpus-0.92/
└── .venv/                   # NO versionado: entorno virtual
```

---

## 4. Instalar las librerias

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Con paquetes precompilados la instalacion tarda menos de un minuto (lo mas
pesado es bajar scipy, ~37 MB). Tiene que terminar en `Successfully
installed ...`.

---

## 5. Correr el chequeo

```
python tests/test_setup.py
```

Salida esperada (las versiones son las de la instalacion del 12 oct 2026;
las tuyas pueden ser mas nuevas):

```
    version: 0.4.7
[OK] parselmouth (import)
    version: 3.1.3
[OK] flask (import)
    numpy 2.5.4, scipy 1.18.1
[OK] numpy + scipy (import)
    analisis+sintesis OK -- 101 frames de F0 estimados
[OK] pyworld (analisis + sintesis real, no solo import)

Entorno listo para la Fase 1.
```

El ultimo chequeo es el importante: no alcanza con que `import pyworld`
no tire error, hay que confirmar que el binding en C++ realmente corre
haciendo un analisis + sintesis de verdad.

Para confirmar que los modulos del proyecto andan:
```
python src/tfc_voz/parametros.py
python src/tfc_voz/genotipo.py
```

---

## 6. Descargar VCTK

Version **0.92**, zip de **10,94 GB** (11.747.302.977 bytes):
https://datashare.ed.ac.uk/handle/10283/3443

Va a `data/`, que esta en `.gitignore`. Se puede bajar por linea de
comandos. `-C -` hace que, si se corta, al volver a correr el mismo comando
siga desde donde quedo:

**Windows (PowerShell)**
```
New-Item -ItemType Directory -Force data
curl.exe -L -C - --retry 5 -o data\VCTK-Corpus-0.92.zip https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip
```

**macOS / Linux**
```
mkdir -p data
curl -L -C - --retry 5 -o data/VCTK-Corpus-0.92.zip https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip
```

Segun la conexion puede tardar horas. Para ver cuanto lleva (PowerShell):
```
"{0:N2} GB" -f ((Get-Item data\VCTK-Corpus-0.92.zip).Length/1GB)
```

Descomprimir (`tar` viene con Windows 10/11 y lee zip):
```
New-Item -ItemType Directory -Force data\VCTK-Corpus-0.92
tar -xf data\VCTK-Corpus-0.92.zip -C data\VCTK-Corpus-0.92
```
(macOS/Linux: `mkdir -p data/VCTK-Corpus-0.92 && unzip data/VCTK-Corpus-0.92.zip -d data/VCTK-Corpus-0.92`)

Que deberia haber adentro:

```
data/VCTK-Corpus-0.92/
├── speaker-info.txt         # edad, sexo y acento por hablante (110)
├── update.txt               # archivos eliminados por los autores
├── txt/pXXX/pXXX_NNN.txt    # transcripciones
└── wav48_silence_trimmed/pXXX/pXXX_NNN_mic1.flac   (y _mic2.flac)
```

Dos cosas a tener en cuenta:
- **El audio viene en FLAC, no en WAV**, grabado con dos microfonos (`mic1`
  y `mic2`). parselmouth lee FLAC directo; no hace falta convertir. Para la
  prueba de humo se uso `mic1`.
- **El sexo del hablante es obligatorio** para la extraccion (define el
  rango de busqueda de F0). Se saca de la columna `GENDER` de
  `speaker-info.txt`.

---

## 7. Primera prueba de extraccion

Con el entorno listo y VCTK descomprimido:

```
python src/tfc_voz/extraccion.py data/VCTK-Corpus-0.92/wav48_silence_trimmed/p225/p225_001_mic1.flac F
```

(el ultimo argumento es `M` o `F` segun el hablante; p225 es mujer)

Salida obtenida el 12 oct 2026:

```
  f0_medio              197.848
  f0_variabilidad        29.283
  jitter                  0.018
  hnr                    12.750
  f1                    415.388
  f2                   1617.044
  f3                   2632.530
  vtl                    17.972

  Todos los controles de plausibilidad OK
```

Si da exactamente esto, la extraccion esta funcionando igual que en la
instalacion verificada.

---

## Si algo falla

| Sintoma | Causa casi segura |
|---|---|
| `no se encontro Python; ... Microsoft Store` | `python` es el acceso directo de la Store. Usar `py -3.12` (paso 1) |
| `Microsoft Visual C++ 14.0 or greater is required` | pip no encontro paquete precompilado de pyworld y quiso compilar. Ver paso 0 |
| `command 'gcc' failed` / `Python.h: No such file` | Idem, en Linux: falta `build-essential` / `python3-dev` |
| `execution of scripts is disabled` (PowerShell) | Ver el `Set-ExecutionPolicy` del paso 2, o usar `.venv\Scripts\python.exe` sin activar |
| `pip` instala pero `import` falla | Se esta usando otro Python, no el del entorno virtual |
| El zip de VCTK pesa menos de 10,94 GB | La descarga se corto. Volver a correr el mismo `curl -C -` |
| Extraccion con advertencias de plausibilidad | Ver la nota de abajo |

**Sobre las advertencias de plausibilidad:** `extraccion.py` chequea que F1,
F2, F3 y VTL caigan en rangos razonables. Si saltan advertencias, lo mas
probable NO es que la voz sea rara, sino que el tracking de formantes
inserto un formante espurio y corrio la numeracion (F2 pasa a ser F3, etc.).
Se corrige ajustando `maximum_formant` para ese hablante. Conviene contar
cuantos archivos del corpus disparan advertencias antes de decidir si hay
que afinar los parametros globalmente. (En la prueba de humo del 12 oct, 0
de 10 archivos dispararon advertencias.)
