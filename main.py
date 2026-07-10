import streamlit as st
from data_engine import obtener_metricas_maestro

# Configuración de la página
st.set_page_config(page_title="Herramienta MTP", layout="wide")

# 1. Menú Lateral (Sidebar)
st.sidebar.title("Navegación")
paginas = ["Inicio", "Maestro de Cuentas", "Áreas", "Presupuesto", "Historial", "Consolidación"]
seleccion = st.sidebar.radio("Menú", paginas)

st.sidebar.button("🔄 Recargar datos")
st.sidebar.caption("Gobierno del dato - BigQuery - Streamlit")

# 2. Pantalla Principal
if seleccion == "Inicio":
    st.title("Herramienta MTP – Planeación Presupuestal")
    st.write("**Gestión centralizada del proceso presupuestal empresarial**, desde el Maestro de Cuentas hasta el historial de envíos por área, con trazabilidad y gobierno del dato.")
    st.write("Fuente principal del maestro: **Google BigQuery**")
    
    st.subheader("📊 Estado General")
    
    # Llamamos a los datos (que están en caché)
    metricas = obtener_metricas_maestro()
    
    # Pintamos las 4 columnas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cuentas en el Maestro", metricas["cuentas"])
    col2.metric("Áreas activas", metricas["areas"])
    col3.metric("Envíos de presupuesto", metricas["envios"])
    col4.metric("Última actualización", metricas["actualizacion"])
    
    st.subheader("🧱 Estado del Proyecto")
    st.write("- Fase 1 - Maestro de Cuentas: ✅ **Operativa**")
    st.write("- Fase 2 - Áreas y Presupuesto: ✅ **Operativa**")