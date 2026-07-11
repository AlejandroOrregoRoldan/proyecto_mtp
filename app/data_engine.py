"""
Motor de datos — MTP.

Centraliza la lectura y escritura del maestro para que toda la app
comparta una ÚNICA copia cacheada del DataFrame.

Formato: Parquet (compresión Snappy).
  - ~70 % más pequeño que CSV.
  - Lectura 5× más rápida que CSV.
  - Preserva tipos nativos (int, float, string).
  - Compatible con la arquitectura GCS → Cloud Run de producción.

Optimización clave:
  - _cargar_df() es el ÚNICO punto que lee el archivo (caché unificada).
  - guardar_maestro() solo invalida las cachés afectadas, no TODAS.
"""

import pandas as pd
import streamlit as st
from datetime import datetime

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
DATA_PATH = "data/maestro_cuentas.parquet"


# ===================================================================
# Capa de acceso a datos — punto ÚNICO de lectura
# ===================================================================
@st.cache_data
def _cargar_df() -> pd.DataFrame:
    """
    Caché privada: carga el Parquet UNA SOLA VEZ y la comparte entre
    todas las funciones que necesitan los datos del maestro.

    Ninguna otra función debe leer el archivo directamente.
    """
    return pd.read_parquet(DATA_PATH)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def cargar_maestro() -> pd.DataFrame:
    """Carga completa del maestro (usa la caché unificada)."""
    return _cargar_df()


def guardar_maestro(df: pd.DataFrame) -> None:
    """
    Persiste el DataFrame como Parquet e invalida SELECTIVAMENTE
    solo las cachés que dependen de los datos del maestro.
    """
    df.to_parquet(DATA_PATH, index=False)

    # Invalidar solo las cachés que leen el archivo
    _cargar_df.clear()
    obtener_metricas_maestro.clear()
    obtener_consolidado_areas.clear()


# ===================================================================
# Vistas derivadas (usan _cargar_df(), no leen el archivo directamente)
# ===================================================================
@st.cache_data
def obtener_metricas_maestro() -> dict:
    """
    KPIs principales del maestro.

    Retorna un diccionario con: cuentas, areas, envios, actualizacion.
    """
    try:
        df = _cargar_df()

        total_cuentas = len(df)
        total_areas = df["Area"].nunique()
        total_envios = len(df[df["Estado_Envio"] == "Enviado"])
        hora_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

        return {
            "cuentas": total_cuentas,
            "areas": total_areas,
            "envios": total_envios,
            "actualizacion": hora_actual,
        }

    except FileNotFoundError:
        st.error(
            f"No se encontró el archivo de datos en '{DATA_PATH}'. "
            "Ejecuta `python scripts/generador.py` para generarlo."
        )
        return {"cuentas": 0, "areas": 0, "envios": 0, "actualizacion": "Error"}
    except Exception as e:
        st.error(f"Error crítico en el procesamiento: {e}")
        return {"cuentas": 0, "areas": 0, "envios": 0, "actualizacion": "Error"}


@st.cache_data
def obtener_consolidado_areas() -> pd.DataFrame:
    """
    Agrupación de presupuesto por área (para la vista de Consolidación).

    Retorna un DataFrame con columnas: Area, Presupuesto_Solicitado.
    """
    try:
        df = _cargar_df()

        consolidado = (
            df.groupby("Area")["Presupuesto_Solicitado"]
            .sum()
            .reset_index()
            .sort_values(by="Presupuesto_Solicitado", ascending=False)
        )

        return consolidado

    except Exception as e:
        st.error(f"Error al calcular el consolidado: {e}")
        return pd.DataFrame()
