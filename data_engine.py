import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Cargar variables de entorno (simulando seguridad)
load_dotenv()
db_user = os.getenv("DB_USER")

@st.cache_data
def obtener_metricas_maestro():
    try:
        # Aquí iría el intento de conexión a BigQuery usando db_user
        # Simulamos que la conexión es exitosa:
        return {
            "cuentas": 1088,
            "areas": 11,
            "envios": 24,
            "actualizacion": "10/07/2026 14:00"
        }
    except Exception as e:
        # Si falla, no tumbamos la página, mostramos un error controlado
        st.error(f"Error crítico al conectar con la base de datos: {e}")
        return {"cuentas": 0, "areas": 0, "envios": 0, "actualizacion": "Error"}