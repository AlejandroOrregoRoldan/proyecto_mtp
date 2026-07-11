"""
Herramienta MTP – Planeación Presupuestal
-------------------------------------------------
Punto de entrada de la aplicación Streamlit.
El renderizado de cada pestaña está delegado en app.components.tabs.
Los widgets reutilizables viven en app.components.widgets.
El control de acceso RBAC está en app.components.auth.
"""

import streamlit as st

from components.widgets import render_sidebar
from components.tabs import get_tab_router
from components.auth import obtener_usuario_activo


# ---------------------------------------------------------------------------
# Configuración global de la página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Herramienta MTP", layout="wide")


# ---------------------------------------------------------------------------
# 1. Sidebar — usuario activo + menú de navegación
# ---------------------------------------------------------------------------
pagina_activa = render_sidebar()


# ---------------------------------------------------------------------------
# 2. Control de acceso RBAC
# ---------------------------------------------------------------------------
usuario = obtener_usuario_activo()

if usuario is None:
    st.error("No hay usuarios configurados en el sistema.")
    st.stop()

# --- Bloqueo por estado ---
if usuario["estado"] == "Pendiente":
    st.warning(
        "⏳ **Solicitud en revisión**\n\n"
        "Tu cuenta está pendiente de aprobación por un administrador. "
        "Recibirás un correo cuando sea procesada.\n\n"
        f"*Usuario:* {usuario['correo']}  \n"
        f"*Rol solicitado:* {usuario['rol']}"
    )
    st.stop()

if usuario["estado"] == "Rechazado":
    st.error(
        "🚫 **Acceso denegado**\n\n"
        "Tu solicitud de acceso ha sido rechazada. "
        "Contacta al administrador para más información.\n\n"
        f"*Usuario:* {usuario['correo']}"
    )
    st.stop()


# ---------------------------------------------------------------------------
# 3. Router — despacha a la función que pinta la pestaña seleccionada
# ---------------------------------------------------------------------------
router = get_tab_router()
render_func = router.get(pagina_activa)

if render_func is None:
    st.error(f"Pestaña desconocida: {pagina_activa}")
else:
    render_func()
