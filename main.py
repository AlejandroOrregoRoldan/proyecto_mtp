import streamlit as st
from data_engine import obtener_metricas_maestro, obtener_consolidado_areas

# Configuración de la página
st.set_page_config(page_title="Herramienta MTP", layout="wide")

# 1. Menú Lateral (Sidebar)
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("Navegación")
paginas = ["Inicio", "Maestro de Cuentas", "Áreas", "Presupuesto", "Historial", "Consolidación"]
seleccion = st.sidebar.radio("Menú", paginas)

st.sidebar.button("🔄 Recargar datosss")
st.sidebar.caption("Gobierno del dato - BigQuery - Streamlit")

# 2. Pantalla Principal
if seleccion == "Inicio":
    st.title("Herramienta MTP – Planeación Presupuestal")
    st.write("**Gestión centralizada del proceso presupuestal empresarial**, desde el Maestro de Cuentas hasta el historial de envíos por área, con trazabilidad y gobierno del dato.")
    st.write("Fuente principal del maestro: **Google BigQuery**")
    
    st.subheader("📊 Estadoo General")
    
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
# ... (código anterior de la página Inicio)

elif seleccion == "Consolidación":
    st.title("Consolidación Presupuestal por Área")
    st.write("Vista gerencial del total de presupuesto solicitado por cada área de la compañía.")
    
    # Llamamos a nuestro motor de datos
    datos_consolidados = obtener_consolidado_areas()
    
    if not datos_consolidados.empty:
        col1, col2 = st.columns([1, 2]) # Dividimos la pantalla: 1 tercio tabla, 2 tercios gráfica
        
        with col1:
            st.subheader("Resumen Tabular")
            # Mostramos la tabla formateando los números como moneda (pesos)
            st.dataframe(
                datos_consolidados.style.format({"Presupuesto_Solicitado": "${:,.0f}"}),
                hide_index=True,
                use_container_width=True
            )
            
        with col2:
            st.subheader("Distribución Gráfica")
            # Pintamos una gráfica de barras nativa de Streamlit
            st.bar_chart(
                data=datos_consolidados, 
                x="Area", 
                y="Presupuesto_Solicitado",
                use_container_width=True
            )