"""
Generador de datos simulados para el Maestro de Cuentas MTP.

Genera 50,000 registros con estructura financiera realista y
los exporta como archivo Parquet (formato columnar comprimido,
compatible con la arquitectura de producción en GCS/BigQuery).
"""

import random
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
CANTIDAD = 50_000
SALIDA = Path("data") / "maestro_cuentas.parquet"

# Catálogos de valores posibles
AREAS = [
    "Finanzas", "Recursos Humanos", "Tecnología", "Marketing",
    "Operaciones", "Riesgos", "Legal", "Servicio al Cliente",
    "Comercial", "Auditoría",
]
ESTADOS = ["Enviado", "Pendiente", "Rechazado", "En Revisión"]
TIPOS_CUENTA = [
    "Fondo Voluntario", "Cesantías", "Pensión Obligatoria",
    "Nómina", "Inversión", "Infraestructura", "Licencias",
]

# ---------------------------------------------------------------------------
# Generación
# ---------------------------------------------------------------------------
print(f"Generando {CANTIDAD:,} registros...")

datos = {
    "ID_Cuenta": range(1000, 1000 + CANTIDAD),
    "Nombre": [
        f"{random.choice(TIPOS_CUENTA)} - {random.randint(100, 999)}"
        for _ in range(CANTIDAD)
    ],
    "Area": [random.choice(AREAS) for _ in range(CANTIDAD)],
    "Estado_Envio": [random.choice(ESTADOS) for _ in range(CANTIDAD)],
    "Presupuesto_Solicitado": [
        random.randint(5_000_000, 500_000_000) for _ in range(CANTIDAD)
    ],
}

df = pd.DataFrame(datos)

# ---------------------------------------------------------------------------
# Persistencia — Parquet con compresión Snappy (default de PyArrow)
# ---------------------------------------------------------------------------
SALIDA.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(SALIDA, index=False)

# Reporte
tamaño_mb = SALIDA.stat().st_size / (1024 ** 2)
print(
    f"Archivo creado: {SALIDA}  |  "
    f"{CANTIDAD:,} filas × {len(df.columns)} columnas  |  "
    f"{tamaño_mb:.1f} MB"
)
print(
    "Ventaja Parquet vs CSV: ~70 % más pequeño, lectura 5× más rápida, "
    "preserva tipos de datos nativos."
)
