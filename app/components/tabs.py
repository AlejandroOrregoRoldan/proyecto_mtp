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
from components.auth import (
    usuario_es_admin,
    usuario_es_lector,
)
from components.admin_panel import render_admin_panel


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

    # --- Solicitar sincronización a BigQuery (protegido por rol) ---
    st.subheader("🔄 Sincronización BigQuery")

    es_lector = usuario_es_lector()

    if es_lector:
        st.warning(
            "🔒 Tu rol actual (**Lector**) no tiene permisos para solicitar "
            "sincronizaciones. Contacta a un Administrador u Operador."
        )

    st.button(
        "🔄 Solicitar Sincronización a BigQuery",
        type="primary",
        disabled=es_lector,
        use_container_width=True,
        help=(
            "No tienes permisos para ejecutar esta acción (requiere rol Admin u Operador)."
            if es_lector
            else "Envía los datos actuales del maestro a BigQuery."
        ),
    )

    st.divider()
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
# Pestaña: Panel de Administración  (→ app/components/admin_panel.py)
# Solo visible para Admin.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Router: diccionario dinámico que mapea nombre de página → función render.
# La pestaña «Panel de Administración» solo se incluye si el usuario es Admin.
# ---------------------------------------------------------------------------
def get_tab_router() -> dict:
    """Retorna el diccionario de enrutamiento según el rol del usuario activo."""
    rutas = {
        "Inicio":               render_inicio,
        "Maestro de Cuentas":   render_maestro_cuentas,
        "Áreas":                render_areas,
        "Presupuesto":          render_presupuesto,
        "Historial":            render_historial,
        "Consolidación":        render_consolidacion,
    }
    if usuario_es_admin():
        rutas["Panel de Administración"] = render_admin_panel
    return rutas
