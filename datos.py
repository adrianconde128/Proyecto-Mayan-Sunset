# datos.py
# Capa de persistencia: acceso a SQLite.
# Incluye funciones de inicialización, creación y validación de usuarios.

import sqlite3
from typing import Optional, Dict

DB_PATH = "mayan_sunset.db"

def _crear_conexion() -> sqlite3.Connection:
    """
    Crea y retorna una conexión a la base de datos SQLite.
    Usa row_factory para acceder por nombre de columna.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# Funciones de inicialización
# ---------------------------

def seed_usuario() -> None:
    """
    Crea la tabla Usuario si no existe y agrega usuarios básicos.
    Basado en el script adjunto de creación y llenado.
    """
    script_creacion = """
    CREATE TABLE IF NOT EXISTS Usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL UNIQUE,
        contraseña TEXT NOT NULL,
        tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('Administrador', 'Empleado'))
    );
    """

    script_insercion = """
    INSERT OR IGNORE INTO Usuario (usuario, contraseña, tipo_usuario)
    VALUES 
        ('admin', 'admin123', 'Administrador'),
        ('empleado1', 'empleado123', 'Empleado'),
        ('empleado2', 'empleado456', 'Empleado');
    """

    try:
        conn = _crear_conexion()
        with conn:
            conn.executescript(script_creacion)
            conn.executescript(script_insercion)
    except sqlite3.Error as e:
        print(f"[ERROR] seed_usuario: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ---------------------------
# Funciones CRUD de Usuario
# ---------------------------

def crear_usuario(usuario: str, contrasena: str, tipo_usuario: str) -> bool:
    """
    Inserta un nuevo usuario en la tabla Usuario.
    Retorna True si se creó correctamente, False en caso de error.
    """
    query = """
        INSERT INTO Usuario (usuario, contraseña, tipo_usuario)
        VALUES (?, ?, ?);
    """
    try:
        conn = _crear_conexion()
        with conn:
            conn.execute(query, (usuario, contrasena, tipo_usuario))
        return True
    except sqlite3.IntegrityError:
        # Usuario duplicado o tipo_usuario inválido
        return False
    except sqlite3.Error as e:
        print(f"[ERROR] crear_usuario: {e}")
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ---------------------------
# Funciones de autenticación
# ---------------------------

def obtener_usuario_por_credenciales(usuario: str, contrasena: str) -> Optional[Dict]:
    """
    Consulta la tabla Usuario y verifica si coinciden usuario y contraseña.
    Retorna un diccionario con las columnas relevantes si hay coincidencia; de lo contrario, None.
    """
    query = """
        SELECT id, usuario, contraseña, tipo_usuario
        FROM Usuario
        WHERE usuario = ? AND contraseña = ?
        LIMIT 1;
    """
    try:
        conn = _crear_conexion()
        with conn:
            cur = conn.execute(query, (usuario, contrasena))
            row = cur.fetchone()
            if row is None:
                return None
            return {
                "id": row["id"],
                "usuario": row["usuario"],
                "contrasena": row["contraseña"],
                "tipo_usuario": row["tipo_usuario"],
            }
    except sqlite3.Error as e:
        print(f"[ERROR] obtener_usuario_por_credenciales: {e}")
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass
