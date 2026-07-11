"""
Renderizado de cada pestaña de la aplicación MTP.

Cada función recibe el estado compartido que necesite y pinta
la interfaz correspondiente usando componentes nativos de Streamlit.
"""

import streamlit as st
import pandas as pd

from data_engine import obtener_metricas_maestro, obtener_consolidado_areas
from components.widgets import render_kpi_row
from components.maestro_cuentas import render_maestro_cuentas


# ---------------------------------------------------------------------------
# Pestaña: Inicio
# ---------------------------------------------------------------------------
def render_inicio() -> None:
    """Dashboard principal con KPIs y estado del proyecto."""
    st.title("Herramienta MTP – Planeación Presupuestal")
    st.write(
        "**Gestión centralizada del proceso presupuestal empresarial**, "
        "desde el Maestro de Cuentas hasta el historial de envíos por área, "
        "con trazabilidad y gobierno del dato."
    )
    st.write("Fuente principal del maestro: **Google BigQuery**")

    st.subheader("📊 Estado General")
    metricas = obtener_metricas_maestro()
    render_kpi_row(metricas)

    st.subheader("🧱 Estado del Proyecto")
    st.write("- Fase 1 - Maestro de Cuentas: ✅ **Operativa**")
    st.write("- Fase 2 - Áreas y Presupuesto: ✅ **Operativa**")


# ---------------------------------------------------------------------------
# Pestaña: Maestro de Cuentas  (→ app/components/maestro_cuentas.py)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Pestaña: Áreas
# ---------------------------------------------------------------------------
def render_areas() -> None:
    """Gestión de áreas organizacionales."""
    st.title("🏢 Áreas")
    st.info("Módulo en construcción — asignación de cuentas y responsables por área.")


# ---------------------------------------------------------------------------
# Pestaña: Presupuesto
# ---------------------------------------------------------------------------
def render_presupuesto() -> None:
    """Captura y revisión de presupuestos por área."""
    st.title("💰 Presupuesto")
    st.info("Módulo en construcción — carga y revisión de cifras presupuestales por área.")


# ---------------------------------------------------------------------------
# Pestaña: Historial
# ---------------------------------------------------------------------------
def render_historial() -> None:
    """Historial de envíos y trazabilidad."""
    st.title("📜 Historial")
    st.info("Módulo en construcción — trazabilidad de envíos, cambios y aprobaciones.")


# ---------------------------------------------------------------------------
# Pestaña: Consolidación
# ---------------------------------------------------------------------------
def render_consolidacion() -> None:
    """Vista gerencial con tabla resumen y gráfica de barras por área."""
    st.title("Consolidación Presupuestal por Área")
    st.write(
        "Vista gerencial del total de presupuesto solicitado "
        "por cada área de la compañía."
    )

    datos = obtener_consolidado_areas()

    if datos.empty:
        st.warning("No hay datos disponibles para mostrar la consolidación.")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Resumen Tabular")
        st.dataframe(
            datos.style.format({"Presupuesto_Solicitado": "${:,.0f}"}),
            hide_index=True,
            use_container_width=True,
        )

    with col2:
        st.subheader("Distribución Gráfica")
        st.bar_chart(
            data=datos,
            x="Area",
            y="Presupuesto_Solicitado",
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# Router: diccionario que mapea nombre de página → función render
# ---------------------------------------------------------------------------
TAB_ROUTER = {
    "Inicio":               render_inicio,
    "Maestro de Cuentas":   render_maestro_cuentas,
    "Áreas":                render_areas,
    "Presupuesto":          render_presupuesto,
    "Historial":            render_historial,
    "Consolidación":        render_consolidacion,
}
