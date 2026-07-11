"""
Módulo de Autenticación y Control de Acceso Basado en Roles (RBAC).

Simula el comportamiento de Identity-Aware Proxy (IAP):
  - Lee la base de datos de usuarios desde data/usuarios.csv.
  - Expone un selectbox en la barra lateral para elegir el correo activo.
  - Provee funciones de verificación de estado (Pendiente / Aprobado / Rechazado)
    y de rol (Admin / Operador / Lector) para que el resto de la app aplique
    las restricciones correspondientes.
"""

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
USUARIOS_PATH = "data/usuarios.csv"
SESSION_KEY_USER = "auth_usuario_activo"

# ---------------------------------------------------------------------------
# Carga / persistencia
# ---------------------------------------------------------------------------
def cargar_usuarios() -> pd.DataFrame:
    """Lee la tabla de usuarios desde el CSV."""
    return pd.read_csv(USUARIOS_PATH)


def guardar_usuarios(df: pd.DataFrame) -> None:
    """Persiste la tabla de usuarios al CSV."""
    df.to_csv(USUARIOS_PATH, index=False)


# ---------------------------------------------------------------------------
# Simulador de sesión (reemplaza a IAP en desarrollo local)
# ---------------------------------------------------------------------------
def render_login_selector() -> None:
    """
    Muestra el selector de correo en la barra lateral.

    En producción, IAP inyecta el correo autenticado en los headers HTTP.
    Este selectbox emula ese mecanismo durante el desarrollo local.
    """
    df = cargar_usuarios()

    correos = df["correo"].tolist()

    # Determinar el índice por defecto
    correo_actual = st.session_state.get(SESSION_KEY_USER, correos[0])
    idx_default = correos.index(correo_actual) if correo_actual in correos else 0

    # --- Selector ---
    seleccion = st.sidebar.selectbox(
        "👤 Usuario activo",
        options=correos,
        index=idx_default,
        help="Simula el correo inyectado por IAP en producción.",
    )
    st.session_state[SESSION_KEY_USER] = seleccion

    # --- Badge de rol + estado ---
    usuario = df[df["correo"] == seleccion].iloc[0]
    estado = usuario["estado"]
    rol = usuario["rol"]

    if estado == "Aprobado":
        st.sidebar.success(f"✅ Rol: **{rol}**")
    elif estado == "Pendiente":
        st.sidebar.warning(f"⏳ Rol: {rol} — Pendiente de aprobación")
    else:
        st.sidebar.error(f"🚫 Rol: {rol} — Acceso rechazado")

    st.sidebar.divider()


# ---------------------------------------------------------------------------
# Consultas sobre el usuario activo
# ---------------------------------------------------------------------------
def _get_usuario() -> pd.Series | None:
    """Retorna la fila completa del usuario activo, o None si no hay sesión."""
    correo = st.session_state.get(SESSION_KEY_USER)
    if not correo:
        return None
    df = cargar_usuarios()
    match = df[df["correo"] == correo]
    return match.iloc[0] if not match.empty else None


def obtener_usuario_activo() -> pd.Series | None:
    """Acceso público a la fila del usuario activo."""
    return _get_usuario()


def usuario_aprobado() -> bool:
    """True si el usuario activo tiene estado 'Aprobado'."""
    u = _get_usuario()
    return u is not None and u["estado"] == "Aprobado"


def usuario_es_admin() -> bool:
    """True si el usuario activo tiene rol 'Admin'."""
    u = _get_usuario()
    return u is not None and u["rol"] == "Admin"


def usuario_es_lector() -> bool:
    """True si el usuario activo tiene rol 'Lector'."""
    u = _get_usuario()
    return u is not None and u["rol"] == "Lector"


def usuario_es_operador() -> bool:
    """True si el usuario activo tiene rol 'Operador'."""
    u = _get_usuario()
    return u is not None and u["rol"] == "Operador"
