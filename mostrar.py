import html
from pathlib import Path


RUTA_PROYECTO = Path(__file__).resolve().parent


def crear_pagina_web(total_extraidos, aceptados, rechazados, nombre_archivo="resultados.html"):
    ruta_salida = Path(nombre_archivo)
    if not ruta_salida.is_absolute():
        ruta_salida = RUTA_PROYECTO / ruta_salida

    filas_aceptadas = "\n".join(
        f"<tr>"
        f"<td>{html.escape(str(r.get('idProducto') or ''))}</td>"
        f"<td>{html.escape(str(r.get('Descripcion') or ''))}</td>"
        f"<td>{html.escape(str(r.get('Categoria') or ''))}</td>"
        f"<td>{html.escape(str(r.get('Unidad') or ''))}</td>"
        f"<td>{html.escape(str(r.get('Cantidad') or ''))}</td>"
        f"<td>{html.escape(str(r.get('vrUnitario') or ''))}</td>"
        f"<td>{html.escape(str(r.get('VrDetalle') or ''))}</td>"
        f"<td>{html.escape(str(r.get('sucursal') or ''))}</td>"
        f"<td>{html.escape(str(r.get('observaciones') or ''))}</td>"
        f"</tr>"
        for r in aceptados
    )

    filas_rechazadas = "\n".join(
        f"<tr>"
        f"<td>{html.escape(str(r.get('idProducto') or ''))}</td>"
        f"<td>{html.escape(str(r.get('sucursal') or ''))}</td>"
        f"<td>{html.escape(str(r.get('archivoOrigen') or ''))}</td>"
        f"<td>{html.escape(str(r.get('motivoRechazo') or ''))}</td>"
        f"</tr>"
        for r in rechazados
    )

    contenido_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Resultados ETL - Almacén ABC</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
    .resumen {{ display: flex; gap: 16px; margin-bottom: 24px; }}
    .tarjeta {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 12px 18px; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 28px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; font-size: 14px; }}
    th {{ background-color: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Resultados ETL - Almacén ABC</h1>
  <div class="resumen">
    <div class="tarjeta"><strong>Extraídos:</strong> {total_extraidos}</div>
    <div class="tarjeta"><strong>Aceptados:</strong> {len(aceptados)}</div>
    <div class="tarjeta"><strong>Rechazados:</strong> {len(rechazados)}</div>
  </div>

  <h2>Ventas aceptadas</h2>
  <table>
    <thead>
      <tr>
        <th>idProducto</th><th>Descripcion</th><th>Categoria</th><th>Unidad</th>
        <th>Cantidad</th><th>vrUnitario</th><th>VrDetalle</th><th>sucursal</th><th>observaciones</th>
      </tr>
    </thead>
    <tbody>
      {filas_aceptadas if filas_aceptadas else "<tr><td colspan='9'>Sin registros</td></tr>"}
    </tbody>
  </table>

  <h2>Registros rechazados</h2>
  <table>
    <thead>
      <tr>
        <th>idProducto</th><th>sucursal</th><th>archivoOrigen</th><th>motivoRechazo</th>
      </tr>
    </thead>
    <tbody>
      {filas_rechazadas if filas_rechazadas else "<tr><td colspan='4'>Sin registros</td></tr>"}
    </tbody>
  </table>
</body>
</html>
"""

    ruta_salida.write_text(contenido_html, encoding="utf-8")
    print(f"Página generada en: {ruta_salida}")