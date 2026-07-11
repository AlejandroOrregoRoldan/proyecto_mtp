# Herramienta MTP — Planeación Presupuestal

Aplicación empresarial para la gestión centralizada del proceso presupuestal.  
Desde el **Maestro de Cuentas** hasta el historial de envíos por área, con trazabilidad,
gobierno del dato y control de acceso basado en roles (RBAC).

> **Stack:** Streamlit · Pandas · PyArrow (Parquet) · Docker · Google Cloud Run  
> **Fuente de datos:** BigQuery (producción) / Parquet local (desarrollo)  
> **Auth:** Google IAP (producción) / Simulador de sesión RBAC (desarrollo)

---

## 🧱 Arquitectura

```
usuarios ──IAP──▶ Cloud Run (Streamlit) ──▶ GCS (.parquet) ◀── Cloud Scheduler ──▶ BigQuery
                       │                          │
                       └── @st.cache_data         └── ETL cada hora
                           TTL = 10 min               (1 query, sin importar
                                                       cuántos usuarios haya)
```

**Principio de costo optimizado:** BigQuery solo se consulta una vez por hora (Cloud Scheduler),  
no por cada clic de usuario. Streamlit lee desde GCS (prácticamente gratis) y cachea en memoria.

---

## 📁 Estructura del proyecto

```
proyecto_mtp/
├── app/                          # Código fuente de la aplicación
│   ├── main.py                   # Punto de entrada + router RBAC
│   ├── data_engine.py            # Capa de datos (Parquet ↔ caché unificada)
│   └── components/               # Módulos de la interfaz
│       ├── tabs.py               # Router de pestañas principales
│       ├── widgets.py            # Sidebar, KPIs, navegación
│       ├── auth.py               # Motor RBAC + simulador de sesión (IAP)
│       ├── admin_panel.py        # Panel de gestión de accesos (Admin)
│       └── maestro_cuentas.py    # 5 sub-pestañas del Maestro de Cuentas
├── assets/
│   └── logo.png                  # Logo corporativo (Protección S.A.)
├── data/
│   ├── maestro_cuentas.parquet   # Datos del maestro (50k registros de prueba)
│   └── usuarios.csv              # Base de datos de usuarios RBAC
├── scripts/
│   └── generador.py              # Genera datos simulados para desarrollo
├── .streamlit/
│   └── config.toml               # Tema corporativo + fileWatcherType=poll
├── Dockerfile                    # Imagen multi-etapa con usuario no-root
├── cloudbuild.yaml               # CI/CD para Google Cloud Build
├── requirements.txt              # Dependencias Python
└── README.md
```

---

## 🚀 Funcionalidades

### Pestañas principales

| Pestaña | Descripción | Acceso |
|---|---|---|
| **Inicio** | Dashboard con KPIs (cuentas, áreas, envíos) y estado del proyecto | Todos |
| **Maestro de Cuentas** | Búsqueda, filtro, CRUD, calidad de datos y exportación | Admin, Operador |
| **Áreas** | Gestión de áreas organizacionales *(en construcción)* | Admin, Operador |
| **Presupuesto** | Sincronización con BigQuery + carga de cifras | Admin, Operador |
| **Historial** | Trazabilidad de envíos y cambios *(en construcción)* | Todos |
| **Consolidación** | Vista gerencial: tabla + gráfica de barras por área | Todos |
| **Panel de Administración** | `st.data_editor` para gestionar roles y estados de usuarios | Solo Admin |

### Maestro de Cuentas (5 sub-pestañas)

| Sub-pestaña | Funcionalidad |
|---|---|
| 🔍 **Ver / Filtrar** | Búsqueda full-text, tabla paginada (50 filas/pág), conteo en tiempo real |
| 🧩 **Columnas** | Selector de columnas visibles con persistencia en sesión |
| ✏️ **Editar Cuenta** | CRUD completo: crear, modificar y eliminar registros |
| 📊 **Calidad** | Perfilado de datos: completitud, unicidad, distribuciones |
| 📥 **Exportar** | Descarga filtrada en CSV (compatible con Excel/Sheets) |

### Sistema RBAC

| Rol | Sidebar | Editor de usuarios | Sync BigQuery | Maestro CRUD |
|---|---|---|---|---|
| **Admin** | 7 pestañas | ✅ Completo | ✅ Habilitado | ✅ Completo |
| **Operador** | 6 pestañas | ❌ | ✅ Habilitado | ✅ Completo |
| **Lector** | 6 pestañas | ❌ | 🔒 Deshabilitado | Solo lectura |

Los usuarios con estado **Pendiente** o **Rechazado** no pueden acceder a la app.

---

## 🔧 Instalación y uso

### Requisitos

- Python 3.11+
- Docker Desktop (para despliegue containerizado)
- Git

### Desarrollo local

```powershell
# 1. Clonar e instalar dependencias
git clone <repo-url>
cd proyecto_mtp
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Generar datos de prueba (50,000 registros)
python scripts/generador.py

# 3. Lanzar Streamlit
streamlit run app/main.py
```

Abre `http://localhost:8501`. Usa el selector **👤 Usuario activo** en la barra lateral
para cambiar entre roles y probar el sistema RBAC.

### Docker (recomendado para desarrollo en Windows)

```powershell
# Construir la imagen
docker build -t mtp-proteccion .

# Ejecutar con hot-reload (monta el código fuente como volumen)
docker run -p 8501:8501 -v "C:\Users\...\proyecto_mtp:/app" mtp-proteccion
```

> **Nota sobre Windows + WSL2:** El `fileWatcherType=poll` en `.streamlit/config.toml`
> es obligatorio para que el hot-reload funcione con volúmenes montados desde Windows.

---

## ☁️ Despliegue a Google Cloud

### CI/CD (Cloud Build)

El archivo `cloudbuild.yaml` define el pipeline:

```yaml
steps:
  - Construir imagen Docker
  - Subir a Google Container Registry
  - Desplegar en Cloud Run
```

### Arquitectura de producción

```
Google Cloud Scheduler        Google Cloud Run
        │                           │
        ▼                           ▼
   Cloud Run Job ──────▶ GCS Bucket ◀──── Streamlit (IAP)
        │                    │
        ▼                    ▼
    BigQuery           maestro.parquet
  (source of truth)    (caché en frío)
```

**Costo mensual estimado (20 usuarios):** ~$2-5/mes (vs $30-50/mes consultando BigQuery directamente).

### Variables de entorno necesarias en Cloud Run

| Variable | Descripción |
|---|---|
| `ENV` | `production` (activa la lectura desde GCS) |
| `GCS_BUCKET` | Nombre del bucket (ej. `mtp-proteccion-data`) |

---

## 🧑‍💻 Para desarrolladores

### Formato de datos: ¿Por qué Parquet?

| | CSV | Parquet |
|---|---|---|
| Tamaño (50k filas) | ~3.7 MB | **0.8 MB** |
| Lectura | ~0.3s | **~0.05s** |
| Tipos de datos | `object` genérico | `StringDtype` + `int64` nativos |
| Compresión | Ninguna | Snappy (automática) |
| GCS nativo | ❌ | ✅ (`pd.read_parquet("gs://...")`) |

La app usa una **caché unificada** (`_cargar_df()`) para que todas las funciones
compartan una sola copia del DataFrame en memoria, y `guardar_maestro()` invalida
selectivamente solo las cachés afectadas (sin `st.cache_data.clear()` global).

### Flujo de datos

```
CSV/Parquet en disco
      │
      ▼
_cargar_df()         ← @st.cache_data (caché unificada)
      │
      ├── cargar_maestro()          → session_state (CRUD)
      ├── obtener_metricas_maestro() → Dashboard Inicio
      └── obtener_consolidado_areas() → Vista Consolidación
```

### Migrar de IAP simulado a IAP real

Solo hay que modificar `app/components/auth.py` (~10 líneas):

```python
# Desarrollo (actual)
st.session_state["auth_usuario_activo"] = st.sidebar.selectbox(...)

# Producción (futuro)
email_iap = st.context.headers.get("X-Goog-Authenticated-User-Email")
st.session_state["auth_usuario_activo"] = email_iap
```

El resto de la app (`main.py`, `tabs.py`, `widgets.py`, `admin_panel.py`) **no se toca**.

---

## 📄 Licencia

Uso interno — Protección S.A.
