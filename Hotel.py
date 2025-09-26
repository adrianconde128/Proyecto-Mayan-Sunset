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
# Validadores adicionales
# =========================
def validar_numero_habitacion(numero_habitacion: str):
    """
    Valida formato HNNN y presencia en la BD (mensaje exacto requerido).
    Lanza ValueError con "Número de habitación invalido" si hay problema.
    """
    if not numero_habitacion or not HABITACION_REGEX.match(numero_habitacion):
        raise ValueError("Número de habitación invalido")

def validar_nombres_apellidos(datos: dict):
    """
    Valida límites de 25 caracteres para:
    - primer_nombre, segundo_nombre, primer_apellido, segundo_apellido
    (Solo valida si las llaves existen en 'datos'.)
    """
    for llave, etiqueta, max_len in [
        ("primer_nombre", "1er nombre", MAX_NOMBRE),
        ("segundo_nombre", "2do nombre", MAX_NOMBRE),
        ("primer_apellido", "1er apellido", MAX_APELLIDO),
        ("segundo_apellido", "2do apellido", MAX_APELLIDO),
    ]:
        if llave in datos and datos[llave] is not None:
            valor = str(datos[llave])
            if len(valor) > max_len:
                raise ValueError(f"{etiqueta} supera {max_len} caracteres")

def validar_dpi_nit(datos: dict):
    """
    Valida DPI y NIT si están presentes en 'datos':
    - DPI: numérico, máximo 13 dígitos.
    - NIT: numérico, máximo 11 dígitos (sin verificador K).
    """
    if "dpi" in datos and datos["dpi"] is not None:
        dpi = str(datos["dpi"]).strip()
        if not dpi.isdigit():
            raise ValueError("DPI debe ser numérico")
        if len(dpi) > MAX_DPI:
            raise ValueError(f"DPI supera {MAX_DPI} dígitos")

    if "nit" in datos and datos["nit"] is not None:
        nit = str(datos["nit"]).strip()
        if not nit.isdigit():
            raise ValueError("NIT debe ser numérico")
        if len(nit) > MAX_NIT:
            raise ValueError(f"NIT supera {MAX_NIT} dígitos")

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
        "id_habitacion": int,           # opcional si se provee "numero_habitacion"
        "numero_habitacion": "HNNN",    # nuevo campo opcional (formato H001, H002, ...)
        "fecha_ingreso": "YYYY-MM-DD",
        "fecha_salida": "YYYY-MM-DD",
        "tipo": str,                    # tipo de habitación para precio
        "dpi": str,                     # opcional; validado si presente
        "nit": str,                     # opcional; validado si presente
        "primer_nombre": str,           # opcional; validado si presente
        "segundo_nombre": str,          # opcional; validado si presente
        "primer_apellido": str,         # opcional; validado si presente
        "segundo_apellido": str         # opcional; validado si presente
    }
    """
    # =========================
    # Validaciones de fechas
    # =========================
    noches = calcular_noches(datos["fecha_ingreso"], datos["fecha_salida"])
    if noches is None:
        return False, "Fechas inválidas"

    # =========================
    # Soporte de numero_habitacion a id_habitacion
    # =========================
    # Si viene el número de habitación (preferido en GUI), validar y mapear a ID.
    with hotel_db.get_connection() as conn:
        id_habitacion = datos.get("id_habitacion")
        if "numero_habitacion" in datos and datos["numero_habitacion"]:
            numero = str(datos["numero_habitacion"]).strip()
            validar_numero_habitacion(numero)
            # Obtener la habitación por número
            hab = hotel_db.get_habitacion_por_numero(conn, numero)
            if not hab:
                # Mensaje exacto solicitado
                return False, "Número de habitación invalido"
            # Asumimos que la función retorna (id_habitacion, numero_habitacion) o un row con id en índice 0
            id_habitacion = hab[0]
            # Mantener compatibilidad con el resto del flujo
            datos["id_habitacion"] = id_habitacion

        # Validación si no se logró establecer id_habitacion
        if not id_habitacion:
            return False, "Número de habitación invalido"

        # =========================
        # Validaciones de identidad opcionales
        # =========================
        # Se validan solo si las llaves existen en 'datos'.
        try:
            validar_nombres_apellidos(datos)
            validar_dpi_nit(datos)
        except ValueError as ve:
            return False, str(ve)

        # =========================
        # Disponibilidad antes de insertar
        # =========================
        disponible = hotel_db.validar_disponibilidad(
            conn, datos["id_habitacion"], datos["fecha_ingreso"], datos["fecha_salida"]
        )
        if not disponible:
            return False, "Habitación no disponible"

        # =========================
        # Precio por tipo y cálculo total
        # =========================
        precio_noche = hotel_db.get_precio_por_tipo(datos["tipo"])
        if precio_noche is None:
            return False, "Tipo de habitación no encontrado"

        total = noches * precio_noche

        # =========================
        # Inserción
        # =========================
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
