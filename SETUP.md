# Puesta en marcha del entorno -- modulo de Voz

Todo esto se hace una sola vez. Al final tenes que ver el mensaje
`Entorno listo.`

**Verificado el 20 oct 2026** en Windows 11 con Python 3.12.4, en un venv
nuevo instalado solo con `requirements.txt`. Todas las librerias traen
paquetes precompilados: no hace falta compilador.

---

## 1. Verificar la version de Python

Apuntar a **Python 3.11 o 3.12**. La verificada es 3.12.4.

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

**Alternativa sin activar:** llamar directo al Python del entorno. Evita el
tema de la politica de ejecucion de PowerShell:
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
├── .gitignore               # excluye .venv/, data/, __pycache__/ y .pytest_cache/
├── pyproject.toml           # configuracion de pytest (pythonpath = src)
├── README.md                # contexto completo del proyecto
├── SETUP.md
├── decisiones-fase1.md
├── historico-vctk.md        # audio real: fuera de alcance desde el 19/10
├── seguimiento-modulo-voz.md
├── requirements.txt
├── requirements-informes.txt  # solo para los informes en PDF (paso 6)
├── referencias/
│   └── tabla-s6-heredabilidades.csv
├── informes/
│   ├── generar_informe.py
│   └── informe-estado-AAAA-MM-DD.pdf
├── src/
│   └── tfc_voz/
│       ├── __init__.py
│       ├── parametros.py
│       ├── genotipo.py
│       └── extraccion.py
├── tests/
│   ├── test_setup.py
│   ├── test_parametros.py
│   └── test_generador.py
└── .venv/                   # NO versionado: entorno virtual
```

---

## 4. Instalar las librerias

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Tarda menos de un minuto (lo mas pesado es bajar scipy y pandas). Tiene que
terminar en `Successfully installed ...`.

---

## 5. Correr el chequeo y los tests

```
python tests/test_setup.py
```

Salida esperada (versiones de la instalacion del 20 oct 2026; las tuyas
pueden ser mas nuevas):

```
    numpy 2.5.4, scipy 1.18.1
[OK] numpy + scipy (import)
    version: 3.0.6
[OK] pandas (import)
    version: 9.1.1
[OK] pytest (import)
    version: 0.4.7
    pitch estimado: 150.0 Hz sobre 47 frames sonoros
[OK] parselmouth (pitch real de una onda de 150 Hz, no solo import)

Entorno listo.
```

El ultimo chequeo es el importante: no alcanza con que `import parselmouth`
no tire error, hay que confirmar que estima bien el pitch de una senal
conocida.

Despues, los tests del proyecto:
```
python -m pytest                    # todos, ~50 s (VZ-07 genera 20 cohortes)
python -m pytest -m "not lento"     # sin VZ-07, ~3 s
```

Y para confirmar que los modulos andan corridos directo:
```
python src/tfc_voz/parametros.py
python src/tfc_voz/genotipo.py
```

---

## 6. (Opcional) Informes de estado en PDF

`informes/generar_informe.py` arma un PDF con el avance por fase (leido de
`seguimiento-modulo-voz.md`), los resultados y los proximos pasos. Necesita
dos librerias mas, en el mismo entorno:

```
python -m pip install -r requirements-informes.txt
python informes/generar_informe.py                    # fecha de hoy
python informes/generar_informe.py --fecha 2026-10-13 # otra fecha
```

Sale en `informes/informe-estado-AAAA-MM-DD.pdf`. Antes de generar uno nuevo,
editar la seccion `CONTENIDO` del script (resumen, resultados, hallazgos); el
cronograma y la tabla de fases se actualizan solos con los `[x]` del
seguimiento.

---

## Si algo falla

| Sintoma | Causa casi segura |
|---|---|
| `no se encontro Python; ... Microsoft Store` | `python` es el acceso directo de la Store. Usar `py -3.12` (paso 1) |
| `execution of scripts is disabled` (PowerShell) | Ver el `Set-ExecutionPolicy` del paso 2, o usar `.venv\Scripts\python.exe` sin activar |
| `pip` instala pero `import` falla | Se esta usando otro Python, no el del entorno virtual |
| `ModuleNotFoundError: tfc_voz` al correr pytest | Correr pytest parado en la raiz del proyecto, donde esta `pyproject.toml` |
| El pitch estimado no da ~150 Hz | parselmouth instalado pero roto. Reinstalar `praat-parselmouth` |
