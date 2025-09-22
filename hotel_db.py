import sqlite3

DATABASE_NAME = "mayan_sunset.db"

def create_connection():
    """ Crea y retorna una conexión a la base de datos SQLite. """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Error conectando a la base de datos: {e}")
    return conn

def setup_database():
    """ Configura las tablas iniciales del módulo de hotel. """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        
        # Tabla de Habitaciones (asumiendo que ya tiene datos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Habitacion (
                id_habitacion TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                precio_por_noche REAL NOT NULL,
                estado TEXT NOT NULL
            );
        """)
        
        # Tabla de Huéspedes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Huesped (
                dpi TEXT PRIMARY KEY,
                primer_nombre TEXT NOT NULL,
                segundo_nombre TEXT,
                primer_apellido TEXT NOT NULL,
                segundo_apellido TEXT,
                nit TEXT
            );
        """)

        # Tabla de Reservas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Reservas_Hotel (
                id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
                dpi_huesped TEXT NOT NULL,
                id_habitacion TEXT NOT NULL,
                fecha_ingreso TEXT NOT NULL,
                fecha_salida TEXT NOT NULL,
                precio_total REAL NOT NULL,
                FOREIGN KEY (dpi_huesped) REFERENCES huespedes(dpi),
                FOREIGN KEY (id_habitacion) REFERENCES habitaciones(id_habitacion)
            );
        """)
        
        conn.commit()
        conn.close()

# Llamar a la función para asegurar que la base de datos esté lista
setup_database()