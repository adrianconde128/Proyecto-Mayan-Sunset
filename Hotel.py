from datetime import datetime
import hotel_db
import re

# =========================
# Constantes de validación
# =========================
HABITACION_REGEX = re.compile(r"^H\d{3}$")  # Formato: H seguido de 3 dígitos

MAX_NOMBRE = 25         # límite 25 caracteres
MAX_APELLIDO = 25       # límite 25 caracteres
MAX_DPI = 13            # máximo 13 dígitos
MAX_NIT = 11            # máximo 11 dígitos (sin verificador K)

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

# Métodos de validación dentro de la clase Hotel

def _validar_numero_habitacion(self, numero_habitacion: str):
    if not numero_habitacion or not HABITACION_REGEX.match(numero_habitacion):
        # Mensaje solicitado textualmente
        raise ValueError("Número de habitación invalido")

def _validar_nombre(self, valor: str, etiqueta: str):
    if valor is None:
        valor = ""
    if len(valor) > MAX_NOMBRE:
        raise ValueError(f"{etiqueta} supera {MAX_NOMBRE} caracteres")

def _validar_apellido(self, valor: str, etiqueta: str):
    if valor is None:
        valor = ""
    if len(valor) > MAX_APELLIDO:
        raise ValueError(f"{etiqueta} supera {MAX_APELLIDO} caracteres")

def _validar_dpi(self, dpi: str):
    if dpi is None:
        dpi = ""
    if not dpi.isdigit():
        raise ValueError("DPI debe ser numérico")
    if len(dpi) > MAX_DPI:
        raise ValueError(f"DPI supera {MAX_DPI} dígitos")

def _validar_nit(self, nit: str):
    if nit is None:
        nit = ""
    if not nit.isdigit():
        raise ValueError("NIT debe ser numérico")
    if len(nit) > MAX_NIT:
        raise ValueError(f"NIT supera {MAX_NIT} dígitos")


# =========================
# Inicialización de la BD
# =========================
def inicializar_sistema():
    """
    Crea las tablas y llena datos iniciales.
    """
    hotel_db.init_db()
    hotel_db.seed_data()
