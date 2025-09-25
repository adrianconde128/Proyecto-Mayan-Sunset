from datetime import datetime
import hotel_db

# =========================
# Funciones de negocio
# =========================
def calcular_noches(fecha_ingreso, fecha_salida):
    try:
        f1 = datetime.strptime(fecha_ingreso, "%Y-%m-%d")
        f2 = datetime.strptime(fecha_salida, "%Y-%m-%d")
        if f2 <= f1:
            return None
        return (f2 - f1).days
    except ValueError:
        return None

def obtener_tipos_habitacion():
    habitaciones = hotel_db.get_all_habitaciones()
    return list({h[2] for h in habitaciones})  # índice 2 = tipo

def obtener_precio_por_tipo(tipo):
    return hotel_db.get_precio_por_tipo(tipo)

def crear_reserva(datos):
    """
    datos = {
        "id_huesped": int,
        "id_habitacion": int,
        "fecha_ingreso": "YYYY-MM-DD",
        "fecha_salida": "YYYY-MM-DD"
    }
    """
    noches = calcular_noches(datos["fecha_ingreso"], datos["fecha_salida"])
    if noches is None:
        return False, "Fechas inválidas"

    disponible = hotel_db.validar_disponibilidad(
        datos["id_habitacion"], datos["fecha_ingreso"], datos["fecha_salida"]
    )
    if not disponible:
        return False, "Habitación no disponible"

    precio_noche = hotel_db.get_precio_por_tipo(datos["tipo"])
    if precio_noche is None:
        return False, "Tipo de habitación no encontrado"

    total = noches * precio_noche

    hotel_db.insert_reserva(
        datos["id_huesped"],
        datos["id_habitacion"],
        datos["fecha_ingreso"],
        datos["fecha_salida"],
        total
    )
    return True, f"Reserva creada con éxito. Total: {total:.2f}"

# =========================
# Inicialización de la BD
# =========================
def inicializar_sistema():
    """
    Crea las tablas y llena datos iniciales.
    """
    hotel_db.init_db()
    hotel_db.seed_data()
