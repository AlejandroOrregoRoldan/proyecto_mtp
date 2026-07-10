"""
Herramienta MTP – Planeación Presupuestal
-------------------------------------------------
Punto de entrada de la aplicación Streamlit.
El renderizado de cada pestaña está delegado en app.components.tabs.
Los widgets reutilizables viven en app.components.widgets.
"""

import streamlit as st

from components.widgets import render_sidebar
from components.tabs import TAB_ROUTER


# ---------------------------------------------------------------------------
# Configuración global de la página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Herramienta MTP", layout="wide")


# ---------------------------------------------------------------------------
# 1. Sidebar — menú lateral único para toda la app
# ---------------------------------------------------------------------------
pagina_activa = render_sidebar()


# ---------------------------------------------------------------------------
# 2. Router — despacha a la función que pinta la pestaña seleccionada
# ---------------------------------------------------------------------------
render_func = TAB_ROUTER.get(pagina_activa)

if render_func is None:
    st.error(f"Pestaña desconocida: {pagina_activa}")
else:
    render_func()
