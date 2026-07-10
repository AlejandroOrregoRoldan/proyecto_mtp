import pandas as pd
import random

print("Generando datos masivos, por favor espera...")

# Listas de opciones reales para una empresa financiera
areas = ["Finanzas", "Recursos Humanos", "Tecnología", "Marketing", "Operaciones", "Riesgos", "Legal", "Servicio al Cliente", "Comercial", "Auditoría"]
estados = ["Enviado", "Pendiente", "Rechazado", "En Revisión"]
tipos_cuenta = ["Fondo Voluntario", "Cesantías", "Pensión Obligatoria", "Nómina", "Inversión", "Infraestructura", "Licencias"]

# Vamos a generar 50,000 registros
cantidad = 50000

# Construimos los datos aleatorios
datos = {
    "ID_Cuenta": range(1000, 1000 + cantidad),
    "Nombre": [f"{random.choice(tipos_cuenta)} - {random.randint(100, 999)}" for _ in range(cantidad)],
    "Area": [random.choice(areas) for _ in range(cantidad)],
    "Estado_Envio": [random.choice(estados) for _ in range(cantidad)],
    "Presupuesto_Solicitado": [random.randint(5000000, 500000000) for _ in range(cantidad)]
}

# Convertimos a Pandas y guardamos el CSV
df = pd.DataFrame(datos)
df.to_csv("data/maestro_cuentas.csv", index=False)

print(f"¡Éxito! Se ha creado el archivo 'data/maestro_cuentas.csv' con {cantidad} filas.")