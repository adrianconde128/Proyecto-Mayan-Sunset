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

# Hotel.py
# Hotel.py
def crear_reserva(datos):
    """
    datos esperados (mínimos):
        - numero_habitacion: str (ej. 'H107')  [requerido]
        - fecha_ingreso: 'YYYY-MM-DD'
        - fecha_salida: 'YYYY-MM-DD'
        - dpi: str  (para identificar/crear huésped)
        - primer_nombre, primer_apellido: str
        - segundo_nombre, segundo_apellido: str (opcionales)
        - nit: str (opcional)
    """
    # 1) Validación de fechas y cálculo de noches
    noches = calcular_noches(datos["fecha_ingreso"], datos["fecha_salida"])
    if noches is None:
        return False, "Fechas inválidas"

    # 2) Validación de numero_habitacion (obligatorio)
    numero_habitacion = datos.get("numero_habitacion", "").strip()
    if not numero_habitacion:
        return False, "Número de habitación invalido"
    validar_numero_habitacion(numero_habitacion)

    with hotel_db.get_connection() as conn:
        # 3) Obtener habitación por número (id, tipo, precio, estado)
        hab = hotel_db.get_habitacion_por_numero(conn, numero_habitacion)
        if not hab:
            return False, "Número de habitación invalido"

        # Orden esperado: (id_habitacion, numero_habitacion, tipo, precio_por_noche, estado)
        id_habitacion = hab[0]
        numero_habitacion = hab[1]
        precio_por_noche = float(hab[3])

        # 4) Validaciones de identidad (nombres y DPI/NIT)
        try:
            validar_nombres_apellidos(datos)  # requiere: primer_/segundo_ nombre/apellido
            validar_dpi_nit(datos)            # requiere: dpi, nit
        except ValueError as ve:
            return False, str(ve)

        # 5) Resolver id_huesped (buscar por DPI; crear si no existe)
        huesped = hotel_db.get_huesped_por_dpi(conn, datos["dpi"])
        if huesped:
            id_huesped = huesped[0]  # id_huesped
        else:
            # Inserta huésped con argumentos POSICIONALES (evita kwargs)
            id_huesped = hotel_db.insert_huesped(
                conn,
                datos["dpi"],
                datos["primer_nombre"],
                datos.get("segundo_nombre", ""),
                datos["primer_apellido"],
                datos.get("segundo_apellido", ""),
                datos.get("nit", None)
            )

        # 6) Validar disponibilidad por fechas (usa id_habitacion + fechas reales)
        disponible = hotel_db.validar_disponibilidad(
            conn, id_habitacion, datos["fecha_ingreso"], datos["fecha_salida"]
        )
        if not disponible:
            return False, "Habitación no disponible"

        # 7) Calcular precio total
        total = noches * precio_por_noche

        # 8) Estado de la reserva
        estado_reserva = "Confirmada"  # ajusta según tu flujo

        # 9) Insertar reserva acorde al esquema actual de la tabla 'reserva'
        reserva_id = hotel_db.insert_reserva(
            conn,
            id_huesped,
            datos["dpi"],             # dpi_huesped
            id_habitacion,
            numero_habitacion,
            estado_reserva,
            datos["fecha_ingreso"],
            datos["fecha_salida"],
            total
        )

    return True, f"Reserva creada con éxito (ID: {reserva_id}). Total: {total:.2f}"

# =========================
# Inicialización de la BD
# =========================
def inicializar_sistema():
    """
    Crea las tablas y llena datos iniciales.
    """
    hotel_db.init_db()
    hotel_db.seed_data()
