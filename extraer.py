import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path


RUTA_PROYECTO = Path(__file__).resolve().parent


def _resolver_carpeta_entrada(carpeta_datos: str) -> Path:
    candidata = Path(carpeta_datos)
    if not candidata.is_absolute():
        candidata = RUTA_PROYECTO / candidata

    if candidata.exists():
        return candidata

    alternativa = RUTA_PROYECTO / "Input"
    if alternativa.exists():
        return alternativa

    return candidata


def _leer_csv(ruta: Path):
    with open(ruta, "r", encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def _leer_json(ruta: Path):
    with open(ruta, "r", encoding="utf-8-sig") as archivo:
        datos = json.load(archivo)
    if not isinstance(datos, list):
        raise ValueError("El JSON debe contener una lista de registros.")
    return datos


def _leer_tsv(ruta: Path):
    with open(ruta, "r", encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo, delimiter="\t"))


def _leer_xml(ruta: Path):
    arbol = ET.parse(ruta)
    raiz = arbol.getroot()
    datos = []
    for elemento in raiz:
        registro = {}
        for campo in elemento:
            registro[campo.tag] = campo.text
        datos.append(registro)
    return datos


def _agregar_origen(registros, sucursal, nombre_archivo):
    resultado = []
    for registro in registros:
        if not isinstance(registro, dict):
            raise ValueError(f"Registro inválido en {nombre_archivo}.")
        nuevo = registro.copy()
        nuevo["_sucursal"] = sucursal
        nuevo["_archivo"] = nombre_archivo
        resultado.append(nuevo)
    return resultado


def extraer_todos_los_archivos(carpeta_datos="datos"):
    ruta_entrada = _resolver_carpeta_entrada(carpeta_datos)
    datos = []

    fuentes = [
        (_leer_csv, "Sucursal 1", "ventas_sistema1.csv"),
        (_leer_json, "Sucursal 2", "ventas_sistema2.json"),
        (_leer_tsv, "Sucursal 3", "ventas_sistema3.tsv"),
        (_leer_xml, "Sucursal 4", "ventas_sistema4.xml"),
    ]

    print("\nINICIANDO EXTRACCION DE DATOS")
    print(f"Carpeta de entrada: {ruta_entrada}")

    for lector, sucursal, nombre_archivo in fuentes:
        ruta_archivo = ruta_entrada / nombre_archivo
        try:
            registros = lector(ruta_archivo)
            registros = _agregar_origen(registros, sucursal, nombre_archivo)
            datos.extend(registros)
            print(f"{sucursal}: {len(registros)} registros extraídos")
        except (OSError, ValueError, ET.ParseError, json.JSONDecodeError, csv.Error) as error:
            print(f"Error leyendo {nombre_archivo}: {error}")

    print(f"\nTotal de registros extraídos: {len(datos)}")
    return datos
