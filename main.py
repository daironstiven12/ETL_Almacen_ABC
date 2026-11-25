import csv
import json
import sqlite3
import unicodedata
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path


RUTA_PROYECTO = Path(__file__).resolve().parent
RUTA_ENTRADA = RUTA_PROYECTO / "Input"
RUTA_BD = RUTA_PROYECTO / "AlmacenABC.db"


def leer_csv():
    ruta = RUTA_ENTRADA / "ventas_sistema1.csv"
    with open(ruta, "r", encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def leer_json():
    ruta = RUTA_ENTRADA / "ventas_sistema2.json"
    with open(ruta, "r", encoding="utf-8-sig") as archivo:
        datos = json.load(archivo)
    if not isinstance(datos, list):
        raise ValueError("El JSON debe contener una lista de registros.")
    return datos


def leer_tsv():
    ruta = RUTA_ENTRADA / "ventas_sistema3.tsv"
    with open(ruta, "r", encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo, delimiter="\t"))


def leer_xml():
    ruta = RUTA_ENTRADA / "ventas_sistema4.xml"
    arbol = ET.parse(ruta)
    raiz = arbol.getroot()
    datos = []
    for elemento in raiz:
        registro = {}
        for campo in elemento:
            registro[campo.tag] = campo.text
        datos.append(registro)
    return datos


def agregar_origen(registros, sucursal, archivo):
    resultado = []
    for registro in registros:
        if not isinstance(registro, dict):
            raise ValueError(f"Registro inválido en {archivo}.")
        nuevo = registro.copy()
        nuevo["_sucursal"] = sucursal
        nuevo["_archivo"] = archivo
        resultado.append(nuevo)
    return resultado


def extraer_datos():
    datos = []
    archivos = [
        (leer_csv, "Sucursal 1", "ventas_sistema1.csv"),
        (leer_json, "Sucursal 2", "ventas_sistema2.json"),
        (leer_tsv, "Sucursal 3", "ventas_sistema3.tsv"),
        (leer_xml, "Sucursal 4", "ventas_sistema4.xml"),
    ]

    print("\nINICIANDO EXTRACCION DE DATOS")

    for funcion, sucursal, nombre_archivo in archivos:
        try:
            registros = funcion()
            registros = agregar_origen(registros, sucursal, nombre_archivo)
            datos.extend(registros)
            print(f"{sucursal}: {len(registros)} registros extraídos")
        except (OSError, ValueError, ET.ParseError, json.JSONDecodeError, csv.Error) as error:
            print(f"Error leyendo {nombre_archivo}: {error}")

    print(f"\nTotal de registros extraídos: {len(datos)}")
    return datos


def normalizar_nombre(nombre):
    nombre = unicodedata.normalize("NFKD", str(nombre))
    nombre = "".join(
        caracter for caracter in nombre if not unicodedata.combining(caracter)
    )
    return nombre.strip().lower().replace(" ", "")


def mapear_campos(registro):
    equivalencias = {
        "idproducto": "idProducto",
        "descripcion": "Descripcion",
        "categoria": "Categoria",
        "unidad": "Unidad",
        "cantidad": "Cantidad",
        "vrunitario": "vrUnitario",
        "vrdetalle": "VrDetalle",
    }
    resultado = {}
    for campo, valor in registro.items():
        nombre = normalizar_nombre(campo)
        nombre_final = equivalencias.get(nombre, campo)
        resultado[nombre_final] = valor
    return resultado


def convertir_decimal(valor):
    if valor is None or str(valor).strip() == "":
        return None

    valor = str(valor).strip()
    valor = valor.replace("$", "")
    valor = valor.replace(",", "")
    valor = valor.replace(" ", "")

    try:
        return Decimal(valor)
    except InvalidOperation:
        raise ValueError(f"Valor numérico inválido: {valor}")


def transformar_registro(registro):
    original = registro.copy()
    registro = mapear_campos(registro)

    motivos = []
    correcciones = []

    id_producto = registro.get("idProducto")
    descripcion = registro.get("Descripcion")
    categoria = registro.get("Categoria")
    unidad = registro.get("Unidad")

    if id_producto is not None:
        id_producto = str(id_producto).strip().upper()
    if descripcion is not None:
        descripcion = str(descripcion).strip()
    if categoria is not None:
        categoria = str(categoria).strip().title()
    if unidad is not None:
        unidad = str(unidad).strip().upper()

    if not id_producto:
        motivos.append("Identificador del producto vacío")
    if not descripcion:
        motivos.append("Descripción del producto vacía")
    if not categoria:
        motivos.append("Categoría vacía")
    if not unidad:
        motivos.append("Unidad de medida vacía")

    cantidad = None
    precio = None
    detalle = None

    try:
        cantidad = convertir_decimal(registro.get("Cantidad"))
    except ValueError as error:
        motivos.append(str(error))

    try:
        precio = convertir_decimal(registro.get("vrUnitario"))
    except ValueError as error:
        motivos.append(str(error))

    try:
        detalle = convertir_decimal(registro.get("VrDetalle"))
    except ValueError as error:
        motivos.append(str(error))

    if cantidad is not None and cantidad <= 0:
        motivos.append("La cantidad debe ser mayor que cero")

    if precio is not None and precio <= 0:
        motivos.append("El precio unitario debe ser mayor que cero")

    if precio is None and detalle is not None and cantidad is not None:
        if cantidad > 0 and detalle > 0:
            precio = detalle / cantidad
            correcciones.append("Precio unitario calculado")

    if detalle is None and cantidad is not None and precio is not None:
        if cantidad > 0 and precio > 0:
            detalle = cantidad * precio
            correcciones.append("Valor del detalle calculado")

    if cantidad is None:
        motivos.append("Cantidad no válida o ausente")
    if precio is None:
        motivos.append("Precio unitario no disponible")
    if detalle is None:
        motivos.append("Valor del detalle no disponible")

    if cantidad is not None and precio is not None and detalle is not None:
        if cantidad > 0 and precio > 0:
            detalle_calculado = cantidad * precio
            if detalle != detalle_calculado:
                detalle = detalle_calculado
                correcciones.append("Valor del detalle recalculado")

    limpio = {
        "idProducto": id_producto,
        "Descripcion": descripcion,
        "Categoria": categoria,
        "Unidad": unidad,
        "Cantidad": cantidad,
        "vrUnitario": precio,
        "VrDetalle": detalle,
        "sucursal": registro.get("_sucursal"),
        "archivoOrigen": registro.get("_archivo"),
        "observaciones": "; ".join(correcciones),
    }

    limpio["registroOriginal"] = json.dumps(
        original,
        ensure_ascii=False,
        default=str,
    )

    return limpio, motivos, correcciones


def transformar_datos(datos):
    aceptados = []
    rechazados = []

    print("\nINICIANDO TRANSFORMACION DE DATOS")

    for registro in datos:
        limpio, motivos, _ = transformar_registro(registro)

        if motivos:
            rechazado = limpio.copy()
            rechazado["motivoRechazo"] = "; ".join(motivos)
            rechazados.append(rechazado)
        else:
            aceptados.append(limpio)

    print(f"Registros aceptados: {len(aceptados)}")
    print(f"Registros rechazados: {len(rechazados)}")

    return aceptados, rechazados


def a_numero_sqlite(valor):
    if valor is None:
        return None
    return float(valor)


def conectar_sql():
    return sqlite3.connect(str(RUTA_BD))


def cargar_datos(aceptados, rechazados):
    conexion = conectar_sql()
    cursor = conexion.cursor()

    try:
        sql_ventas = """
            INSERT INTO Ventas (
                idProducto,
                Descripcion,
                Categoria,
                Unidad,
                Cantidad,
                vrUnitario,
                VrDetalle,
                sucursal,
                archivoOrigen,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        sql_rechazados = """
            INSERT INTO RegistrosRechazados (
                idProducto,
                Descripcion,
                Categoria,
                Unidad,
                Cantidad,
                vrUnitario,
                VrDetalle,
                sucursal,
                archivoOrigen,
                motivoRechazo,
                registroOriginal
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        filas_ventas = [
            (
                r["idProducto"],
                r["Descripcion"],
                r["Categoria"],
                r["Unidad"],
                a_numero_sqlite(r["Cantidad"]),
                a_numero_sqlite(r["vrUnitario"]),
                a_numero_sqlite(r["VrDetalle"]),
                r["sucursal"],
                r["archivoOrigen"],
                r["observaciones"],
            )
            for r in aceptados
        ]

        filas_rechazados = [
            (
                r["idProducto"],
                r["Descripcion"],
                r["Categoria"],
                r["Unidad"],
                a_numero_sqlite(r["Cantidad"]),
                a_numero_sqlite(r["vrUnitario"]),
                a_numero_sqlite(r["VrDetalle"]),
                r["sucursal"],
                r["archivoOrigen"],
                r["motivoRechazo"],
                r["registroOriginal"],
            )
            for r in rechazados
        ]

        if filas_ventas:
            cursor.executemany(sql_ventas, filas_ventas)

        if filas_rechazados:
            cursor.executemany(sql_rechazados, filas_rechazados)

        conexion.commit()

        print("\nCARGA COMPLETADA")
        print(f"Ventas almacenadas: {len(filas_ventas)}")
        print(f"Registros rechazados almacenados: {len(filas_rechazados)}")

    except Exception:
        conexion.rollback()
        print("Error durante la carga. Se revirtieron las operaciones.")
        raise

    finally:
        cursor.close()
        conexion.close()


def ejecutar_etl():
    print("\nINICIANDO ETL - ALMACEN ABC")

    datos = extraer_datos()
    aceptados, rechazados = transformar_datos(datos)

    print("\nRESUMEN DEL PROCESO")
    print(f"Total extraído: {len(datos)}")
    print(f"Total aceptado: {len(aceptados)}")
    print(f"Total rechazado: {len(rechazados)}")

    if datos:
        cargar_datos(aceptados, rechazados)
    else:
        print("No hay registros para procesar.")

    print("\nPROCESO ETL FINALIZADO")


if __name__ == "__main__":
    ejecutar_etl()
