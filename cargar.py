import sqlite3
from pathlib import Path


RUTA_PROYECTO = Path(__file__).resolve().parent


def _a_numero_sqlite(valor):
    if valor is None:
        return None
    return float(valor)


def _resolver_ruta_sqlite(ruta_sqlite: str) -> Path:
    ruta = Path(ruta_sqlite)
    if not ruta.is_absolute():
        ruta = RUTA_PROYECTO / ruta
    return ruta


def cargar_en_base_de_datos(aceptados, rechazados, ruta_sqlite=None):
    if not ruta_sqlite:
        raise ValueError(
            "Debes indicar la ruta del archivo SQLite (por ejemplo: --sqlite AlmacenABC.db)."
        )

    ruta_bd = _resolver_ruta_sqlite(ruta_sqlite)
    conexion = sqlite3.connect(str(ruta_bd))
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
                _a_numero_sqlite(r["Cantidad"]),
                _a_numero_sqlite(r["vrUnitario"]),
                _a_numero_sqlite(r["VrDetalle"]),
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
                _a_numero_sqlite(r["Cantidad"]),
                _a_numero_sqlite(r["vrUnitario"]),
                _a_numero_sqlite(r["VrDetalle"]),
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

        print("\nCARGA COMPLETADA EN SQLITE")
        print(f"Base de datos: {ruta_bd}")
        print(f"Ventas almacenadas: {len(filas_ventas)}")
        print(f"Registros rechazados almacenados: {len(filas_rechazados)}")

    except Exception:
        conexion.rollback()
        print("Error durante la carga en SQLite. Se revirtieron las operaciones.")
        raise

    finally:
        cursor.close()
        conexion.close()