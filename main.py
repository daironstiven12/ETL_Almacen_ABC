
# Programa principal de la ETL de ventas de Almacén ABC.

# Ejecución:
# python main.py
# python main.py --sqlite AlmacenABC.db
# python main.py --sin-base-de-datos

import argparse

from extraer import extraer_todos_los_archivos
from transformar import transformar_registros
from cargar import cargar_en_base_de_datos
from mostrar import crear_pagina_web


def main():

    parser = argparse.ArgumentParser(
        description="Proceso ETL de ventas - Almacén ABC"
    )

    parser.add_argument(
        "--datos",
        default="Input",
        help="Carpeta que contiene los archivos de entrada."
    )

    parser.add_argument(
        "--sqlite",
        default="AlmacenABC.db",
        help="Ruta de la base de datos SQLite."
    )

    parser.add_argument(
        "--sin-base-de-datos",
        action="store_true",
        help="Ejecutar ETL sin guardar información en SQLite."
    )

    argumentos = parser.parse_args()

    # 1. EXTRACCIÓN
    registros_extraidos = extraer_todos_los_archivos(
        argumentos.datos
    )

    # 2. TRANSFORMACIÓN
    registros_aceptados, registros_rechazados = transformar_registros(
        registros_extraidos
    )

    # 3. CARGA
    if not argumentos.sin_base_de_datos:

        cargar_en_base_de_datos(
            registros_aceptados,
            registros_rechazados,
            argumentos.sqlite
        )

    # 4. GENERACIÓN DEL INFORME HTML
    crear_pagina_web(
        len(registros_extraidos),
        registros_aceptados,
        registros_rechazados,
        "resultados.html"
    )

    print("\nPROCESO ETL FINALIZADO CORRECTAMENTE")


if __name__ == "__main__":
    main()
