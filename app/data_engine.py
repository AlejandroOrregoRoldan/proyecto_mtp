import os
import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data
def obtener_metricas_maestro():
    try:
        # 1. Leer el archivo CSV real (Simulando la lectura de BigQuery)
        df = pd.read_csv("data/maestro_cuentas.csv")
        
        # 2. Procesamiento con Pandas:
        # Contamos cuántas filas (cuentas) hay en total
        total_cuentas = len(df)
        
        # Contamos cuántas áreas únicas existen
        total_areas = df["Area"].nunique()
        
        # Filtramos y contamos solo los que tienen estado "Enviado"
        total_envios = len(df[df["Estado_Envio"] == "Enviado"])
        
        # Capturamos la hora exacta en la que se leyó el archivo
        hora_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

        # 3. Retornamos el diccionario para que main.py lo pinte
        return {
            "cuentas": total_cuentas,
            "areas": total_areas,
            "envios": total_envios,
            "actualizacion": hora_actual
        }
        
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo 'maestro_cuentas.csv'.")
        return {"cuentas": 0, "areas": 0, "envios": 0, "actualizacion": "Error"}
    except Exception as e:
        st.error(f"Error crítico en el procesamiento: {e}")
        return {"cuentas": 0, "areas": 0, "envios": 0, "actualizacion": "Error"}
    
@st.cache_data
def obtener_consolidado_areas():
    try:
        df = pd.read_csv("data/maestro_cuentas.csv")
        
        # Agrupamos por área y sumamos el presupuesto
        consolidado = df.groupby("Area")["Presupuesto_Solicitado"].sum().reset_index()
        
        # Ordenamos de mayor a menor presupuesto para que la gráfica se vea mejor
        consolidado = consolidado.sort_values(by="Presupuesto_Solicitado", ascending=False)
        
        return consolidado
    except Exception as e:
        st.error(f"Error al calcular el consolidado: {e}")
        return pd.DataFrame() # Retorna una tabla vacía si hay error