import sqlite3

DB_PATH = "mayan_sunset.db"

# =========================
# Conexión centralizada
# =========================
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# =========================
# Inicialización de la BD
# =========================
def init_db():
    """
    Crea todas las tablas con la versión mejorada de los CREATE.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Activar claves foráneas
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Crear tabla habitacion
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habitacion (
        id_habitacion INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_habitacion TEXT UNIQUE NOT NULL,
        tipo TEXT NOT NULL,
        precio_por_noche REAL NOT NULL,
        estado TEXT NOT NULL
    );
    """)

    # Crear tabla huesped
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS huesped (
        id_huesped INTEGER PRIMARY KEY AUTOINCREMENT,
        dpi TEXT UNIQUE NOT NULL,
        primer_nombre TEXT NOT NULL,
        segundo_nombre TEXT,
        primer_apellido TEXT NOT NULL,
        segundo_apellido TEXT,
        nit TEXT
    );
    """)

    # Crear tabla reserva
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reserva (
        id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
        id_huesped INTEGER NOT NULL,
        dpi_huesped TEXT NOT NULL,
        id_habitacion INTEGER NOT NULL,
        numero_habitacion TEXT NOT NULL,
        estado_reserva TEXT NOT NULL,
        fecha_ingreso TEXT NOT NULL,
        fecha_salida TEXT NOT NULL,
        precio_total REAL NOT NULL,
        FOREIGN KEY (id_huesped) REFERENCES huesped(id_huesped),
        FOREIGN KEY (id_habitacion) REFERENCES habitacion(id_habitacion),
        UNIQUE (dpi_huesped, numero_habitacion, fecha_ingreso)
    );
    """)
    conn.commit()
    conn.close()

def seed_data():
    """
    Inserta los datos iniciales (habitaciones, huéspedes, etc.).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Insertar datos en habitacion
    habitaciones = [
        ("H101", "Individual", 250.0, "Disponible"),
        ("H102", "Doble", 400.0, "Ocupada"),
        ("H103", "Suite", 600.0, "Disponible"),
        ("H104", "Individual", 260.0, "Disponible"),
        ("H105", "Doble", 420.0, "Ocupada"),
        ("H106", "Suite", 620.0, "Disponible"),
        ("H107", "Individual", 255.0, "Disponible"),
        ("H108", "Doble", 410.0, "Disponible"),
        ("H109", "Suite", 610.0, "Ocupada"),
        ("H110", "Individual", 270.0, "Disponible"),
        ("H111", "Doble", 430.0, "Disponible"),
        ("H112", "Suite", 630.0, "Disponible"),
        ("H113", "Individual", 265.0, "Ocupada"),
        ("H114", "Doble", 440.0, "Disponible"),
        ("H115", "Suite", 640.0, "Disponible")
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO habitacion (numero_habitacion, tipo, precio_por_noche, estado)
        VALUES (?, ?, ?, ?);
    """, habitaciones)

    # Insertar datos en huesped
    huespedes = [
        ("1000000000101", "Luis", "Alberto", "García", "Méndez", "1234567-1"),
        ("1000000000202", "María", "José", "Pérez", "López", "1234567-2"),
        ("1000000000303", "Carlos", None, "Ramírez", "Gómez", "1234567-3"),
        ("1000000000404", "Ana", "Lucía", "Martínez", "Rodríguez", "1234567-4"),
        ("1000000000505", "Jorge", "Enrique", "Hernández", "Cruz", "1234567-5"),
        ("1000000000606", "Sofía", None, "Morales", "Díaz", "1234567-6"),
        ("1000000000707", "Pedro", "Antonio", "Castillo", "Ruiz", "1234567-7"),
        ("1000000000808", "Laura", "Beatriz", "Flores", "Santos", "1234567-8"),
        ("1000000000909", "Diego", None, "Navarro", "Torres", "1234567-9"),
        ("1000000001010", "Valeria", "Isabel", "Cabrera", "Ramírez", "1234567-10"),
        ("1000000001111", "Andrés", "Felipe", "Molina", "González", "1234567-11"),
        ("1000000001212", "Camila", None, "Reyes", "Ortiz", "1234567-12"),
        ("1000000001313", "Fernando", "Esteban", "Salazar", "Vásquez", "1234567-13"),
        ("1000000001414", "Patricia", "Elena", "Mejía", "Pineda", "1234567-14"),
        ("1000000001515", "Ricardo", None, "Aguilar", "Fuentes", "1234567-15")
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO huesped (dpi, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, nit)
        VALUES (?, ?, ?, ?, ?, ?);
    """, huespedes)

    # Insertar datos en reserva (usando numero_habitacion directamente)
    import datetime

    reservas = [
        # (dpi_huesped, numero_habitacion, estado_reserva, fecha_ingreso, fecha_salida)
        ("1000000000101", "H101", "Activa", "2025-10-01", "2025-10-05"),
        ("1000000000202", "H102", "Activa", "2025-10-02", "2025-10-06"),
        ("1000000000303", "H103", "Finalizada", "2025-09-20", "2025-09-25"),
        ("1000000000404", "H104", "Activa", "2025-10-03", "2025-10-07"),
        ("1000000000505", "H105", "Cancelada", "2025-10-04", "2025-10-08"),
        ("1000000000606", "H106", "Activa", "2025-10-05", "2025-10-09"),
        ("1000000000707", "H107", "Finalizada", "2025-09-15", "2025-09-20"),
        ("1000000000808", "H108", "Activa", "2025-10-06", "2025-10-10"),
        ("1000000000909", "H109", "Activa", "2025-10-07", "2025-10-11"),
        ("1000000001010", "H110", "Cancelada", "2025-10-08", "2025-10-12"),
        ("1000000001111", "H111", "Activa", "2025-10-09", "2025-10-13"),
        ("1000000001212", "H112", "Finalizada", "2025-09-10", "2025-09-15"),
        ("1000000001313", "H113", "Activa", "2025-10-10", "2025-10-14"),
        ("1000000001414", "H114", "Activa", "2025-10-11", "2025-10-15"),
        ("1000000001515", "H115", "Activa", "2025-10-12", "2025-10-16")
    ]

    for dpi, num_hab, estado, ingreso, salida in reservas:
        cursor.execute("SELECT id_huesped FROM huesped WHERE dpi = ?", (dpi,))
        huesped = cursor.fetchone()

        cursor.execute("SELECT id_habitacion, precio_por_noche FROM habitacion WHERE numero_habitacion = ?", (num_hab,))
        habitacion = cursor.fetchone()

        if huesped and habitacion:
            id_huesped = huesped[0]
            id_habitacion = habitacion[0]
            fecha1 = datetime.datetime.strptime(ingreso, "%Y-%m-%d")
            fecha2 = datetime.datetime.strptime(salida, "%Y-%m-%d")                
            noches = (fecha2 - fecha1).days
            precio_total = habitacion[1] * noches

            try:
                cursor.execute("""
                INSERT INTO reserva (id_huesped, dpi_huesped, id_habitacion, numero_habitacion, estado_reserva, fecha_ingreso, fecha_salida, precio_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (id_huesped, dpi, id_habitacion, num_hab, estado, ingreso, salida, precio_total))
            except sqlite3.IntegrityError as e:
                print(f"Error al insertar reserva para {dpi} en {num_hab}: {e}")
        else:
            print(f"Datos no válidos para reserva: {dpi}, {num_hab}")

    conn.commit()
    conn.close()

# =========================
# Funciones de inserción
# =========================
def insert_habitacion(tipo, precio, estado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO habitacion (tipo, precio_por_noche, estado) VALUES (?, ?, ?);",
        (tipo, precio, estado)
    )
    conn.commit()
    conn.close()

def insert_huesped(nombre, apellido, dpi, nit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO huesped (nombre, apellido, dpi, nit) VALUES (?, ?, ?, ?);",
        (nombre, apellido, dpi, nit)
    )
    conn.commit()
    conn.close()

def insert_reserva(conn, id_habitacion: int, dpi: str, nit: str,
                     primer_nombre: str, segundo_nombre: str,
                     primer_apellido: str, segundo_apellido: str,
                     fecha_inicio: str, fecha_fin: str):
    """
    Inserta una reserva y retorna el id generado.
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reserva (id_habitacion, dpi, nit, primer_nombre, segundo_nombre,
                             primer_apellido, segundo_apellido, fecha_inicio, fecha_fin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_habitacion, dpi, nit, primer_nombre, segundo_nombre,
          primer_apellido, segundo_apellido, fecha_inicio, fecha_fin))
    conn.commit()
    return cur.lastrowid

# =========================
# Funciones de consulta
# =========================
def get_all_habitaciones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_habitacion, numero_habitacion, tipo, precio_por_noche, estado FROM habitacion;")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_precio_por_tipo(tipo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT precio_por_noche FROM habitacion WHERE tipo = ? LIMIT 1;", (tipo,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_estado_habitacion(id_habitacion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM habitacion WHERE id_habitacion = ?;", (id_habitacion,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_habitacion_por_numero(conn, numero_habitacion: str):
    """
    Retorna (id_habitacion, numero_habitacion) si existe; None si no existe.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT id_habitacion, numero_habitacion
        FROM habitacion
        WHERE numero_habitacion = ?
    """, (numero_habitacion,))
    return cur.fetchone()

def listar_numeros_habitacion(conn):
    """
    Retorna lista de strings con los números de habitación disponibles: ['H001', 'H002', ...]
    """
    cur = conn.cursor()
    cur.execute("SELECT numero_habitacion FROM habitacion ORDER BY numero_habitacion ASC")
    return [row[0] for row in cur.fetchall()]

def validar_disponibilidad(conn, id_habitacion: int, fecha_inicio: str, fecha_fin: str):
    """
    Verifica si la habitación está libre en el rango de fechas.
    Retorna True si no hay reservas que se solapen.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*)
        FROM reserva
        WHERE id_habitacion = ?
          AND (
                (fecha_inicio <= ? AND fecha_fin >= ?) OR
                (fecha_inicio <= ? AND fecha_fin >= ?) OR
                (? <= fecha_inicio AND ? >= fecha_fin)
              )
    """, (id_habitacion, fecha_inicio, fecha_inicio,
          fecha_fin, fecha_fin,
          fecha_inicio, fecha_fin))
    count = cur.fetchone()[0]
    return count == 0
