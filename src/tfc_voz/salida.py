"""
Escritura de los tres archivos de salida del modulo, segun el contrato del
paquete comun anima_spine 1.1:

  predicciones_voz.csv  una fila por persona de prueba, rasgo y linea base
  intervalos_voz.csv    una fila por persona de prueba, rasgo y nivel nominal
  barrido_voz.csv       una fila por replica, rasgo y nivel (conteos de cobertura)

Cada funcion valida con el verificador del paquete ANTES de escribir: si el
archivo no cumple el contrato, levanta el error del paquete y no escribe nada.
Los ids de prueba salen del DataFrame de cohorte.leer_cohorte.

REEMPLAZABLE si cambia el contrato: no tiene logica de voz, solo traduce
DataFrames al formato del paquete y llama a sus verificadores y exportadores.
"""

from anima_spine import predictions

DOMINIO = "voz"


def _ids_prueba(cohorte):
    return set(int(i) for i in cohorte.loc[cohorte["particion"] == "prueba", "individuo_id"])


def _filas(df, campos, nombre):
    """DataFrame -> lista de dicts, con las columnas exactas del contrato y en su orden."""
    if list(df.columns) != list(campos):
        raise AssertionError(f"{nombre}: columnas {list(df.columns)}, se esperaba {list(campos)}")
    return df.to_dict("records")


def _filas_predicciones(predicciones, cohorte, rasgos=None):
    filas = _filas(predicciones, predictions.CAMPOS, "predicciones")
    presentes = {f["rasgo"] for f in filas}
    if rasgos is not None and presentes != set(rasgos):
        raise AssertionError(f"predicciones: rasgos {sorted(presentes)}, se esperaba {sorted(rasgos)}")
    # El paquete exige que cada (rasgo, linea base) presente cubra la particion de
    # prueba, pero no que esten las dos lineas base: el contrato pide ambas.
    for rasgo in presentes:
        bases = {f["linea_base"] for f in filas if f["rasgo"] == rasgo}
        if bases != set(predictions.LINEAS_BASE):
            raise AssertionError(f"predicciones: rasgo {rasgo} sin las dos lineas base "
                                 f"{list(predictions.LINEAS_BASE)}")
    predictions.verificar(filas, _ids_prueba(cohorte), DOMINIO)
    return filas


def escribir_predicciones(predicciones, cohorte, directorio, rasgos=None):
    """Valida y escribe predicciones_voz.csv. Devuelve la ruta.

    rasgos: si se pasa, el archivo tiene que traer exactamente esos rasgos.
    """
    filas = _filas_predicciones(predicciones, cohorte, rasgos)
    return predictions.exportar(filas, DOMINIO, directorio)


def escribir_intervalos(intervalos, predicciones, cohorte, directorio):
    """Valida intervalos_voz.csv contra la cohorte y las predicciones, y lo escribe."""
    filas = _filas(intervalos, predictions.CAMPOS_INTERVALOS, "intervalos")
    predictions.verificar_intervalos(filas, _filas_predicciones(predicciones, cohorte),
                                     _ids_prueba(cohorte), DOMINIO)
    return predictions.exportar_intervalos(filas, DOMINIO, directorio)


def escribir_barrido(barrido, intervalos, predicciones, cohorte, directorio):
    """Valida barrido_voz.csv (20 replicas, replica 0 igual a los intervalos) y lo escribe."""
    filas = _filas(barrido, predictions.CAMPOS_BARRIDO, "barrido")
    predictions.verificar_barrido(filas, _filas(intervalos, predictions.CAMPOS_INTERVALOS, "intervalos"),
                                  _filas_predicciones(predicciones, cohorte), _ids_prueba(cohorte), DOMINIO)
    return predictions.exportar_barrido(filas, DOMINIO, directorio)
