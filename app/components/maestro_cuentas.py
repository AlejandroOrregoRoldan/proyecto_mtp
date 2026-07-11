"""
Maestro de Cuentas — Renderizado de las 5 sub-pestañas.

Sub-pestañas:
  1. Ver / Filtrar   — búsqueda, tabla paginada, conteo de filas/columnas
  2. Columnas         — selector de columnas visibles con persistencia
  3. Editar Cuenta    — crear, modificar y eliminar registros
  4. Calidad          — perfilado de datos: completitud, unicidad, distribución
  5. Exportar         — descarga del maestro en CSV
"""

from io import StringIO

import pandas as pd
import streamlit as st

from data_engine import cargar_maestro, guardar_maestro

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
DATA_PATH = "data/maestro_cuentas.parquet"
SESSION_KEY_DF = "mc_dataframe"
SESSION_KEY_COLS = "mc_columnas_visibles"
SESSION_KEY_FILTRO = "mc_filtro_texto"


# ---------------------------------------------------------------------------
# Helpers de estado de sesión
# ---------------------------------------------------------------------------
def _init_state() -> pd.DataFrame:
    """Inicializa las llaves de session_state y devuelve el DataFrame activo."""
    if SESSION_KEY_DF not in st.session_state:
        try:
            st.session_state[SESSION_KEY_DF] = cargar_maestro()
        except FileNotFoundError:
            st.error(
                f"No se encontró el archivo de datos en '{DATA_PATH}'. "
                "Ejecuta `python scripts/generador.py` para generarlo."
            )
            st.session_state[SESSION_KEY_DF] = pd.DataFrame()
        except Exception as exc:
            st.error(f"Error al cargar el maestro de cuentas: {exc}")
            st.session_state[SESSION_KEY_DF] = pd.DataFrame()

    df = st.session_state[SESSION_KEY_DF]

    if df.empty:
        return df

    if SESSION_KEY_COLS not in st.session_state:
        st.session_state[SESSION_KEY_COLS] = list(df.columns)

    return df


def _sync_columnas(df: pd.DataFrame) -> None:
    """Asegura que las columnas visibles existan en el DataFrame actual."""
    columnas_guardadas = st.session_state.get(SESSION_KEY_COLS, [])
    columnas_reales = list(df.columns)
    st.session_state[SESSION_KEY_COLS] = [
        c for c in columnas_guardadas if c in columnas_reales
    ]


# ---------------------------------------------------------------------------
# Punto de entrada principal (llamado desde tabs.py)
# ---------------------------------------------------------------------------
def render_maestro_cuentas() -> None:
    """Orquestador de las sub-pestañas del Maestro de Cuentas."""
    df = _init_state()

    st.title("📋 Maestro de Cuentas")
    st.write(
        "Exploración, edición y control de calidad del "
        "maestro de cuentas presupuestal."
    )

    subtabs = st.tabs([
        "🔍 Ver / Filtrar",
        "🧩 Columnas",
        "✏️ Editar Cuenta",
        "📊 Calidad",
        "📥 Exportar",
    ])

    with subtabs[0]:
        _render_ver_filtrar(df)
    with subtabs[1]:
        _render_columnas(df)
    with subtabs[2]:
        _render_editar_cuenta(df)
    with subtabs[3]:
        _render_calidad(df)
    with subtabs[4]:
        _render_exportar(df)


# ===================================================================
# Sub-pestaña 1 — Ver / Filtrar
# ===================================================================
def _render_ver_filtrar(df: pd.DataFrame) -> None:
    """Barra de búsqueda + tabla paginada + conteo de filas y columnas visibles."""
    st.subheader("🔍 Buscar y filtrar cuentas")

    if df.empty:
        st.warning("No hay datos disponibles. Carga un archivo CSV para empezar.")
        return

    # --- Barra de búsqueda ---
    filtro = st.text_input(
        "Buscar (nombre, área, estado, ID…)",
        value=st.session_state.get(SESSION_KEY_FILTRO, ""),
        placeholder="Ej: Finanzas, Pendiente, 1000…",
        key="mc_input_busqueda",
    )
    st.session_state[SESSION_KEY_FILTRO] = filtro

    # --- Aplicar filtro ---
    if filtro.strip():
        mask = pd.Series(False, index=df.index)
        for col in df.select_dtypes(include="object").columns:
            mask |= df[col].astype(str).str.contains(
                filtro, case=False, na=False
            )
        for col in df.select_dtypes(include="number").columns:
            mask |= df[col].astype(str).str.contains(
                filtro, case=False, na=False
            )
        df_filtrado = df[mask].copy()
    else:
        df_filtrado = df  # sin copia: usamos la misma referencia de session_state

    # --- Columnas visibles ---
    columnas_visibles = st.session_state.get(SESSION_KEY_COLS, list(df.columns))

    # --- Paginación ---
    total_filas = len(df_filtrado)
    filas_por_pagina = st.selectbox(
        "Filas por página",
        options=[25, 50, 100, 250],
        index=1,  # default 50
        key="mc_filas_por_pagina",
    )
    total_paginas = max(1, (total_filas + filas_por_pagina - 1) // filas_por_pagina)

    # Control de página
    if "mc_pagina_actual" not in st.session_state:
        st.session_state["mc_pagina_actual"] = 1

    # Si el filtro cambió, volver a página 1
    pagina = st.session_state["mc_pagina_actual"]
    if pagina > total_paginas:
        pagina = 1
        st.session_state["mc_pagina_actual"] = 1

    col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([1, 1, 2, 1, 1])
    if col_nav1.button("◀◀", key="mc_first", disabled=(pagina == 1), use_container_width=True):
        st.session_state["mc_pagina_actual"] = 1
        st.rerun()
    if col_nav2.button("◀", key="mc_prev", disabled=(pagina == 1), use_container_width=True):
        st.session_state["mc_pagina_actual"] = max(1, pagina - 1)
        st.rerun()
    col_nav3.markdown(
        f"<div style='text-align:center;padding-top:5px'>Página <b>{pagina}</b> de <b>{total_paginas}</b></div>",
        unsafe_allow_html=True,
    )
    if col_nav4.button("▶", key="mc_next", disabled=(pagina >= total_paginas), use_container_width=True):
        st.session_state["mc_pagina_actual"] = min(total_paginas, pagina + 1)
        st.rerun()
    if col_nav5.button("▶▶", key="mc_last", disabled=(pagina >= total_paginas), use_container_width=True):
        st.session_state["mc_pagina_actual"] = total_paginas
        st.rerun()

    # --- Slice de la página actual ---
    inicio = (pagina - 1) * filas_por_pagina
    fin = inicio + filas_por_pagina
    df_pagina = df_filtrado.iloc[inicio:fin]

    # --- Tabla ---
    st.dataframe(
        df_pagina[columnas_visibles],
        use_container_width=True,
        hide_index=True,
        height=min(35 * len(df_pagina) + 38, 900),
    )

    # --- Pie: conteo ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Filas visibles (filtro)", total_filas)
    c2.metric("Columnas visibles", len(columnas_visibles))
    c3.metric("Total filas en maestro", len(df))


# ===================================================================
# Sub-pestaña 2 — Columnas
# ===================================================================
def _render_columnas(df: pd.DataFrame) -> None:
    """Selector de columnas visibles con persistencia en session_state."""
    st.subheader("🧩 Personalizar columnas visibles")

    todas = list(df.columns)
    actuales = st.session_state.get(SESSION_KEY_COLS, todas)

    # --- Acciones rápidas ---
    c1, c2, c3 = st.columns(3)
    if c1.button("✅ Seleccionar todas", use_container_width=True):
        st.session_state[SESSION_KEY_COLS] = todas
        st.rerun()
    if c2.button("🫗 Desseleccionar todas", use_container_width=True):
        st.session_state[SESSION_KEY_COLS] = []
        st.rerun()
    if c3.button("↩ Restaurar por defecto", use_container_width=True):
        st.session_state[SESSION_KEY_COLS] = todas
        st.rerun()

    # --- Multiselect ---
    seleccion = st.multiselect(
        "Elige las columnas que quieres ver en las tablas:",
        options=todas,
        default=actuales,
        key="mc_multiselect_columnas",
    )

    # --- Guardar preferencia ---
    if st.button("💾 Guardar preferencia", type="primary", use_container_width=True):
        st.session_state[SESSION_KEY_COLS] = seleccion
        st.success("Preferencia guardada. Las tablas reflejarán tu selección.")
        st.rerun()

    # --- Vista previa ---
    st.caption("Vista previa con las columnas seleccionadas:")
    if seleccion:
        st.dataframe(df[seleccion].head(5), use_container_width=True, hide_index=True)
    else:
        st.warning("Selecciona al menos una columna.")


# ===================================================================
# Sub-pestaña 3 — Editar Cuenta (CRUD)
# ===================================================================
def _render_editar_cuenta(df: pd.DataFrame) -> None:
    """Crear, modificar y eliminar registros del maestro."""
    st.subheader("✏️ Editar cuentas")

    modo = st.radio(
        "Modo de edición",
        ["➕ Crear cuenta", "📝 Editar cuenta existente", "🗑 Eliminar cuenta"],
        horizontal=True,
    )

    # --- Crear ---
    if modo.startswith("➕"):
        _form_crear(df)
    # --- Editar ---
    elif modo.startswith("📝"):
        _form_editar(df)
    # --- Eliminar ---
    else:
        _form_eliminar(df)


# -------------------------------------------------------------------
# Sub-formularios CRUD
# -------------------------------------------------------------------
def _form_crear(df: pd.DataFrame) -> None:
    st.markdown("#### Nueva cuenta")
    with st.form("form_crear_cuenta", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        nuevo_id = col_a.number_input(
            "ID Cuenta",
            min_value=1,
            value=int(df["ID_Cuenta"].max()) + 1 if not df.empty else 1000,
            step=1,
        )
        nuevo_nombre = col_b.text_input("Nombre", placeholder="Ej: Fondo Voluntario - 500")
        nueva_area = st.selectbox(
            "Área",
            sorted(df["Area"].unique()) if not df.empty else ["Finanzas", "Tecnología"],
        )
        col_c, col_d = st.columns(2)
        nuevo_estado = col_c.selectbox(
            "Estado de envío",
            ["Pendiente", "Enviado", "Rechazado", "En Revisión"],
        )
        nuevo_presupuesto = col_d.number_input(
            "Presupuesto solicitado",
            min_value=0,
            value=0,
            step=1_000_000,
        )

        if st.form_submit_button("✅ Crear cuenta", type="primary", use_container_width=True):
            if nuevo_id in df["ID_Cuenta"].values:
                st.error(f"El ID {nuevo_id} ya existe. Usa un ID diferente.")
            else:
                nueva_fila = pd.DataFrame(
                    [[nuevo_id, nuevo_nombre, nueva_area, nuevo_estado, nuevo_presupuesto]],
                    columns=df.columns,
                )
                st.session_state[SESSION_KEY_DF] = pd.concat(
                    [df, nueva_fila], ignore_index=True
                )
                _sync_columnas(st.session_state[SESSION_KEY_DF])
                guardar_maestro(st.session_state[SESSION_KEY_DF])
                st.success(f"Cuenta {nuevo_id} creada correctamente.")
                st.rerun()


def _form_editar(df: pd.DataFrame) -> None:
    st.markdown("#### Modificar cuenta existente")

    id_a_editar = st.selectbox(
        "Selecciona una cuenta por ID",
        sorted(df["ID_Cuenta"].unique()),
    )

    fila = df[df["ID_Cuenta"] == id_a_editar].iloc[0]

    with st.form("form_editar_cuenta"):
        col_a, col_b = st.columns(2)
        nuevo_nombre = col_a.text_input("Nombre", value=str(fila["Nombre"]))
        nueva_area = col_b.selectbox(
            "Área",
            sorted(df["Area"].unique()),
            index=sorted(df["Area"].unique()).index(fila["Area"]),
        )
        col_c, col_d = st.columns(2)
        nuevo_estado = col_c.selectbox(
            "Estado de envío",
            ["Pendiente", "Enviado", "Rechazado", "En Revisión"],
            index=["Pendiente", "Enviado", "Rechazado", "En Revisión"].index(
                fila["Estado_Envio"]
            ),
        )
        nuevo_presupuesto = col_d.number_input(
            "Presupuesto solicitado",
            min_value=0,
            value=int(fila["Presupuesto_Solicitado"]),
            step=1_000_000,
        )

        if st.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True):
            idx = df[df["ID_Cuenta"] == id_a_editar].index[0]
            st.session_state[SESSION_KEY_DF].at[idx, "Nombre"] = nuevo_nombre
            st.session_state[SESSION_KEY_DF].at[idx, "Area"] = nueva_area
            st.session_state[SESSION_KEY_DF].at[idx, "Estado_Envio"] = nuevo_estado
            st.session_state[SESSION_KEY_DF].at[idx, "Presupuesto_Solicitado"] = nuevo_presupuesto
            guardar_maestro(st.session_state[SESSION_KEY_DF])
            st.success(f"Cuenta {id_a_editar} actualizada correctamente.")
            st.rerun()


def _form_eliminar(df: pd.DataFrame) -> None:
    st.markdown("#### Eliminar cuenta")

    id_a_eliminar = st.selectbox(
        "Selecciona una cuenta por ID para eliminar",
        sorted(df["ID_Cuenta"].unique()),
        key="mc_select_eliminar",
    )

    fila = df[df["ID_Cuenta"] == id_a_eliminar].iloc[0]
    st.warning(
        f"Vas a eliminar la cuenta **{id_a_eliminar}** — "
        f"_{fila['Nombre']}_ | {fila['Area']} | "
        f"${fila['Presupuesto_Solicitado']:,.0f}"
    )

    if st.button("🗑 Confirmar eliminación", type="secondary", use_container_width=True):
        st.session_state[SESSION_KEY_DF] = df[
            df["ID_Cuenta"] != id_a_eliminar
        ].reset_index(drop=True)
        _sync_columnas(st.session_state[SESSION_KEY_DF])
        guardar_maestro(st.session_state[SESSION_KEY_DF])
        st.success(f"Cuenta {id_a_eliminar} eliminada.")
        st.rerun()


# ===================================================================
# Sub-pestaña 4 — Calidad de datos
# ===================================================================
def _render_calidad(df: pd.DataFrame) -> None:
    """Panel de calidad: completitud, unicidad, distribución y perfilado."""
    st.subheader("📊 Calidad y perfilado de datos")

    # --- KPIs superiores ---
    total_filas = len(df)
    total_cols = len(df.columns)
    total_nulos = int(df.isna().sum().sum())
    celdas = total_filas * total_cols
    pct_completitud = (1 - total_nulos / celdas) * 100 if celdas else 100

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total filas", f"{total_filas:,}")
    k2.metric("Total columnas", total_cols)
    k3.metric("Valores nulos", f"{total_nulos:,}")
    k4.metric("Completitud", f"{pct_completitud:.1f} %")

    st.divider()

    # --- Tabla de perfil por columna ---
    st.subheader("🔬 Perfil por columna")

    perfiles = []
    for col in df.columns:
        serie = df[col]
        nulos = int(serie.isna().sum())
        unicos = serie.nunique()
        dtype = str(serie.dtype)
        completitud_col = (1 - nulos / total_filas) * 100 if total_filas else 100
        ejemplo = str(serie.dropna().iloc[0]) if nulos < total_filas else "—"
        perfiles.append(
            {
                "Columna": col,
                "Tipo": dtype,
                "Nulos": nulos,
                "Únicos": unicos,
                "Completitud %": round(completitud_col, 1),
                "Ejemplo": ejemplo[:60],
            }
        )

    df_perfil = pd.DataFrame(perfiles)
    st.dataframe(df_perfil, use_container_width=True, hide_index=True)

    # --- Gráfica de completitud ---
    st.subheader("📈 Completitud por columna")

    chart_data = pd.DataFrame(
        {
            "Columna": [p["Columna"] for p in perfiles],
            "Completitud %": [p["Completitud %"] for p in perfiles],
        }
    ).set_index("Columna")

    st.bar_chart(chart_data, use_container_width=True)

    # --- Distribuciones de columnas categóricas ---
    st.subheader("📊 Distribuciones categóricas")

    col_cat = st.selectbox(
        "Selecciona una columna para ver su distribución:",
        ["Area", "Estado_Envio"],
    )

    if col_cat in df.columns:
        distribucion = df[col_cat].value_counts().reset_index()
        distribucion.columns = [col_cat, "Cantidad"]

        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(distribucion, use_container_width=True, hide_index=True)
        with c2:
            st.bar_chart(
                distribucion.set_index(col_cat),
                use_container_width=True,
            )

    # --- Modificaciones recientes (registro simbólico vía session_state) ---
    st.divider()
    st.caption(
        "💡 La calidad se evalúa en tiempo real sobre los datos actuales. "
        "Al editar, crear o eliminar cuentas en la pestaña «Editar Cuenta», "
        "los indicadores de esta sección se actualizan automáticamente."
    )


# ===================================================================
# Sub-pestaña 5 — Exportar
# ===================================================================
def _render_exportar(df: pd.DataFrame) -> None:
    """Exportación del maestro en formato CSV descargable."""
    st.subheader("📥 Exportar Maestro de Cuentas")

    columnas_visibles = st.session_state.get(SESSION_KEY_COLS, list(df.columns))

    # Opciones de exportación
    st.radio(
        "¿Qué columnas quieres exportar?",
        ["Solo las columnas visibles", "Todas las columnas"],
        key="mc_export_scope",
        horizontal=True,
    )

    if st.session_state.get("mc_export_scope", "").startswith("Solo"):
        df_exportar = df[columnas_visibles]
    else:
        df_exportar = df

    st.write(f"Se exportarán **{len(df_exportar)} filas × {len(df_exportar.columns)} columnas**.")

    # Convertir a CSV en memoria
    buffer = StringIO()
    df_exportar.to_csv(buffer, index=False, encoding="utf-8")

    st.download_button(
        label="⬇ Descargar CSV",
        data=buffer.getvalue(),
        file_name="maestro_cuentas_export.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )

    # --- Vista previa de lo que se va a exportar ---
    with st.expander("Vista previa del archivo a exportar"):
        st.dataframe(df_exportar.head(20), use_container_width=True, hide_index=True)
