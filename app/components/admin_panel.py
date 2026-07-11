"""
Panel de Administración de Accesos — RBAC.

Gestiona la base de datos de usuarios (data/usuarios.csv):
  - Editor interactivo con st.data_editor.
  - Correo de solo lectura (PK), estado y rol editables vía dropdowns.
  - Validación y persistencia al CSV.

En producción, el CSV será reemplazado por una tabla de BigQuery
manteniendo la misma interfaz de administración.
"""

import pandas as pd
import streamlit as st

from components.auth import cargar_usuarios, guardar_usuarios


# ---------------------------------------------------------------------------
# Punto de entrada — llamado desde tabs.py (solo para Admin)
# ---------------------------------------------------------------------------
def render_admin_panel() -> None:
    """
    Panel completo de gestión de accesos.

    Carga los usuarios desde CSV, los expone en un data_editor con
    columnas restringidas, y permite guardar los cambios de vuelta al
    archivo. Solo accesible para usuarios con rol 'Admin'.
    """
    st.title("🛡️ Gestión de Accesos")
    st.write(
        "Administración de cuentas de usuario, roles y estados de "
        "aprobación. Los cambios se reflejan inmediatamente en la app."
    )

    # ------------------------------------------------------------------
    # KPIs de resumen
    # ------------------------------------------------------------------
    df = cargar_usuarios()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total usuarios", len(df))
    k2.metric("✅ Aprobados", len(df[df["estado"] == "Aprobado"]))
    k3.metric("⏳ Pendientes", len(df[df["estado"] == "Pendiente"]))
    k4.metric("🚫 Rechazados", len(df[df["estado"] == "Rechazado"]))

    st.divider()

    # ------------------------------------------------------------------
    # Editor interactivo
    # ------------------------------------------------------------------
    st.subheader("✏️ Editor de usuarios")

    df_editado = st.data_editor(
        df,
        column_config={
            "correo": st.column_config.TextColumn(
                "Correo electrónico",
                disabled=True,
                help="El correo es la llave primaria y no se puede modificar.",
            ),
            "estado": st.column_config.SelectboxColumn(
                "Estado",
                options=["Pendiente", "Aprobado", "Rechazado"],
                help="Estado de aprobación del acceso.",
            ),
            "rol": st.column_config.SelectboxColumn(
                "Rol",
                options=["Admin", "Operador", "Lector"],
                help="Rol que determina los permisos dentro de la app.",
            ),
        },
        num_rows="fixed",
        use_container_width=True,
        hide_index=True,
        height=(len(df) + 1) * 38 + 3,
    )

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    st.divider()

    col_save, col_reset = st.columns([1, 4])

    if col_save.button("💾 Guardar Cambios", type="primary", use_container_width=True):
        errores = _validar(df_editado)
        if errores:
            for err in errores:
                st.error(err)
        else:
            guardar_usuarios(df_editado)
            st.success("✅ Cambios guardados correctamente en `data/usuarios.csv`.")
            st.rerun()

    if col_reset.button("↩ Descartar cambios", use_container_width=True):
        st.rerun()

    # ------------------------------------------------------------------
    # Nota informativa
    # ------------------------------------------------------------------
    st.caption(
        "💡 En producción, este panel se conectará a BigQuery. "
        "Por ahora, los datos persisten en `data/usuarios.csv`. "
        "Si modificas tu propio rol o estado, la interfaz reflejará "
        "el cambio en la siguiente recarga."
    )


# -----------------------------------------------------------------------
# Helpers internos
# -----------------------------------------------------------------------
def _validar(df: pd.DataFrame) -> list[str]:
    """
    Valida el DataFrame antes de guardar.

    Retorna una lista de mensajes de error (vacía si todo está bien).
    """
    errores = []

    if not df["correo"].is_unique:
        errores.append("Hay correos duplicados. Cada usuario debe tener un correo único.")

    if df["correo"].isna().any():
        errores.append("Hay correos vacíos. Todos los usuarios deben tener un correo.")

    if df["estado"].isna().any():
        errores.append("Hay estados vacíos. Todos los usuarios deben tener un estado asignado.")

    if df["rol"].isna().any():
        errores.append("Hay roles vacíos. Todos los usuarios deben tener un rol asignado.")

    # Validar que los estados y roles sean valores permitidos
    estados_validos = {"Pendiente", "Aprobado", "Rechazado"}
    roles_validos = {"Admin", "Operador", "Lector"}

    estados_invalidos = set(df["estado"].unique()) - estados_validos
    roles_invalidos = set(df["rol"].unique()) - roles_validos

    if estados_invalidos:
        errores.append(
            f"Estado(s) no válido(s): {', '.join(sorted(estados_invalidos))}. "
            f"Usa: {', '.join(sorted(estados_validos))}."
        )

    if roles_invalidos:
        errores.append(
            f"Rol(es) no válido(s): {', '.join(sorted(roles_invalidos))}. "
            f"Usa: {', '.join(sorted(roles_validos))}."
        )

    return errores
