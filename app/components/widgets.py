"""
Widgets reutilizables para la app MTP.
Sidebar, tarjetas de métricas, y otros componentes compuestos.
"""

import streamlit as st


def render_sidebar() -> str:
    """
    Construye el menú lateral completo y retorna la página seleccionada.

    Returns
    -------
    str
        Nombre de la página activa (valor del radio button).
    """
    # Logo corporativo
    st.sidebar.image("assets/logo.png", use_column_width=True)

    # Navegación principal
    st.sidebar.title("Navegación")
    paginas = [
        "Inicio",
        "Maestro de Cuentas",
        "Áreas",
        "Presupuesto",
        "Historial",
        "Consolidación",
    ]
    seleccion = st.sidebar.radio("Menú", paginas)

    # Botón de recarga y pie
    st.sidebar.button("🔄 Recargar datos")
    st.sidebar.caption("Gobierno del dato - BigQuery - Streamlit")

    return seleccion


def render_kpi_row(metricas: dict) -> None:
    """
    Muestra una fila de 4 tarjetas KPI con los indicadores del maestro.

    Parameters
    ----------
    metricas : dict
        Diccionario con claves "cuentas", "areas", "envios", "actualizacion".
    """
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cuentas en el Maestro", metricas["cuentas"])
    col2.metric("Áreas activas", metricas["areas"])
    col3.metric("Envíos de presupuesto", metricas["envios"])
    col4.metric("Última actualización", metricas["actualizacion"])
