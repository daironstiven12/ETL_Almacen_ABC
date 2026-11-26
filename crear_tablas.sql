CREATE TABLE IF NOT EXISTS Ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idProducto TEXT,
    Descripcion TEXT,
    Categoria TEXT,
    Unidad TEXT,
    Cantidad REAL,
    vrUnitario REAL,
    VrDetalle REAL,
    sucursal TEXT,
    archivoOrigen TEXT,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS RegistrosRechazados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idProducto TEXT,
    Descripcion TEXT,
    Categoria TEXT,
    Unidad TEXT,
    Cantidad REAL,
    vrUnitario REAL,
    VrDetalle REAL,
    sucursal TEXT,
    archivoOrigen TEXT,
    motivoRechazo TEXT,
    registroOriginal TEXT
);

SELECT name FROM sqlite_master WHERE type = 'table';