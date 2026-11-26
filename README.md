# ETL - Almacén ABC

Pipeline ETL en Python para extraer, transformar y cargar los datos de ventas de cuatro sucursales (CSV, JSON, TSV y XML) en una base de datos SQLite.

## Qué se entrega

La carpeta del proyecto contiene los archivos fuente de entrada, los módulos del pipeline, la especificación de dependencias y esta documentación:

```text
ETL_Almacen_ABC/
├── Input/
│   ├── ventas_sistema1.csv
│   ├── ventas_sistema2.json
│   ├── ventas_sistema3.tsv
│   └── ventas_sistema4.xml
├── main.py
├── extraer.py
├── transformar.py
├── cargar.py
├── mostrar.py
├── requirements.txt
└── README.md
```

## Requisitos

- **Python 3.10** o superior.
- Dependencias listadas en `requirements.txt` (si aplica, instalar con `pip install -r requirements.txt`).
- Un gestor o cliente compatible con SQLite (como **DBeaver** o `sqlite3` en terminal) para revisar las tablas creadas al ejecutar el proyecto.

## Paso a paso y comandos de ejecución

1. Abrir una terminal y ubicarse en la carpeta raíz del proyecto (`ETL_Almacen_ABC`):
   ```bash
   cd ruta/a/ETL_Almacen_ABC
   ```

2. *(Opcional)* Crear y activar un entorno virtual de Python:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   *(En Windows PowerShell: `.venv\Scripts\Activate.ps1`)*

3. *(Opcional)* Instalar dependencias si el entorno lo requiere:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar el pipeline ETL indicando el nombre de la base de datos SQLite a generar:
   ```bash
   python main.py --sqlite AlmacenABC.db
   ```

5. Abrir la base de datos generada en **DBeaver** (o mediante `sqlite3`) y ejecutar las consultas de verificación para inspeccionar los datos cargados.

## Resultados esperados

Al ejecutar el flujo sobre los archivos de `Input/` se procesan **225 registros** en total:

- **184 registros aceptados** almacenados en la tabla `Ventas` (con campos normalizados y cálculos/recálculos cuando corresponde).
- **41 registros rechazados** almacenados en la tabla `RegistrosRechazados` junto con su `motivoRechazo` y el `registroOriginal`.

## Consultas de verificación (SQLite / DBeaver)

```sql
-- Total de registros por tabla
SELECT 'Ventas' AS tabla, COUNT(*) AS total FROM Ventas
UNION ALL
SELECT 'RegistrosRechazados' AS tabla, COUNT(*) AS total FROM RegistrosRechazados;

-- Muestra de ventas aceptadas
SELECT * FROM Ventas LIMIT 10;

-- Muestra de registros rechazados y su motivo
SELECT id, idProducto, sucursal, archivoOrigen, motivoRechazo
FROM RegistrosRechazados
LIMIT 10;
```
