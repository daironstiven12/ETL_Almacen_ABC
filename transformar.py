import json
import unicodedata
from decimal import Decimal, InvalidOperation


def _normalizar_nombre(nombre):
    nombre = unicodedata.normalize("NFKD", str(nombre))
    nombre = "".join(
        caracter for caracter in nombre if not unicodedata.combining(caracter)
    )
    return nombre.strip().lower().replace(" ", "")


def _mapear_campos(registro):
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
        nombre = _normalizar_nombre(campo)
        nombre_final = equivalencias.get(nombre, campo)
        resultado[nombre_final] = valor
    return resultado


def _convertir_decimal(valor):
    if valor is None or str(valor).strip() == "":
        return None

    limpio = str(valor).strip().replace("$", "").replace(",", "").replace(" ", "")
    try:
        return Decimal(limpio)
    except InvalidOperation:
        raise ValueError(f"Valor numérico inválido: {valor}")


def _transformar_registro(registro):
    original = registro.copy()
    mapeado = _mapear_campos(registro)

    motivos = []
    correcciones = []

    id_producto = mapeado.get("idProducto")
    descripcion = mapeado.get("Descripcion")
    categoria = mapeado.get("Categoria")
    unidad = mapeado.get("Unidad")

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

    for campo_clave, destino in [("Cantidad", "cantidad"), ("vrUnitario", "precio"), ("VrDetalle", "detalle")]:
        try:
            valor_dec = _convertir_decimal(mapeado.get(campo_clave))
            if destino == "cantidad":
                cantidad = valor_dec
            elif destino == "precio":
                precio = valor_dec
            else:
                detalle = valor_dec
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
        "sucursal": mapeado.get("_sucursal"),
        "archivoOrigen": mapeado.get("_archivo"),
        "observaciones": "; ".join(correcciones),
        "registroOriginal": json.dumps(original, ensure_ascii=False, default=str),
    }

    return limpio, motivos


def transformar_registros(registros_extraidos):
    aceptados = []
    rechazados = []

    print("\nINICIANDO TRANSFORMACION DE DATOS")

    for registro in registros_extraidos:
        limpio, motivos = _transformar_registro(registro)
        if motivos:
            rechazado = limpio.copy()
            rechazado["motivoRechazo"] = "; ".join(motivos)
            rechazados.append(rechazado)
        else:
            aceptados.append(limpio)

    print(f"Registros aceptados: {len(aceptados)}")
    print(f"Registros rechazados: {len(rechazados)}")
    return aceptados, rechazados