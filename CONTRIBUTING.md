# 🛠️ Guía de Contribución y Flujo de Trabajo (Git)

¡Bienvenido al repositorio! Para mantener nuestro código limpio, evitar conflictos y asegurar que la rama `master` siempre funcione perfectamente, todo el equipo debe seguir este flujo de trabajo estándar (Feature Branch Workflow).

## 🏷️ 1. Nomenclatura de Ramas (Branches)
Nunca trabajamos en `master`. Siempre creamos una rama nueva usando uno de estos prefijos:
* `feat/nombre-funcionalidad`: Para crear algo nuevo (ej. `feat/panel-admin`).
* `fix/nombre-del-error`: Para arreglar un bug (ej. `fix/error-calculo-presupuesto`).
* `chore/nombre-tarea`: Para tareas de mantenimiento, limpieza o documentación (ej. `chore/actualizar-readme`).

## 🔄 2. El Ciclo de Trabajo Diario (Copiar y Pegar)

Sigue estos 5 pasos exactos cada vez que vayas a programar:

**Paso 1: Actualizar tu máquina (Siempre desde master)**
```bash
git checkout master
git pull origin master