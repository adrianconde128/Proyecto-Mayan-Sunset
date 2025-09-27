"""
Capa de Persistencia del módulo Restaurante para Mayan Sunset.
Gestiona SQLite, creación de tablas, inserción de datos iniciales y operaciones CRUD.
"""

import sqlite3
from typing import List, Dict, Optional, Tuple


class RestauranteDB:
    """
    Gestor de la base de datos para el módulo Restaurante.
    Responsable de conexión, esquema y operaciones CRUD.
    """

    def __init__(self, db_path: str = "mayan_sunset.db") -> None:
        self.db_path = db_path
        self.conn = None

    def connect(self) -> None:
        """Abre la conexión y configura row_factory para dict-like access."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al conectar a la base de datos: {e}")

    def close(self) -> None:
        """Cierra la conexión si está abierta."""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                raise RuntimeError(f"Error al cerrar la conexión: {e}")
            finally:
                self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # --- Esquema y datos iniciales ---

    def create_tables(self) -> None:
        """Ejecuta el script de creación de tablas (idempotente)."""
        sql_script = """
        CREATE TABLE IF NOT EXISTS menu (
            id_plato INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plato TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            tipo TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
            id_habitacion INTEGER NOT NULL,
            fecha_pedido TEXT NOT NULL,
            hora_pedido TEXT NOT NULL,
            estado TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS detalle_pedidos (
            id_detalle_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pedido INTEGER NOT NULL,
            id_plato INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
            FOREIGN KEY (id_plato) REFERENCES menu(id_plato)
        );

        CREATE TABLE IF NOT EXISTS inventario (
            id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_ingrediente TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            unidad_medida TEXT NOT NULL,
            stock_minimo INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transacciones (
            id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pedido INTEGER NOT NULL,
            fecha_transaccion TEXT NOT NULL,
            monto_total REAL NOT NULL,
            metodo_pago TEXT,
            FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
        );
        """
        try:
            cur = self.conn.cursor()
            cur.executescript(sql_script)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al crear tablas: {e}")

    def seed_initial_data(self) -> None:
        """
        Inserta datos iniciales para 'menu' e 'inventario' si están vacíos.
        Evita duplicados verificando la cantidad de filas existentes.
        """
        try:
            cur = self.conn.cursor()
            # Verificar 'menu'
            cur.execute("SELECT COUNT(*) AS c FROM menu;")
            count_menu = cur.fetchone()["c"]
            if count_menu == 0:
                cur.executemany(
                    "INSERT INTO menu (nombre_plato, descripcion, precio, tipo) VALUES (?, ?, ?, ?);",
                    [
                        ("Tacos al Pastor",
                         "Tacos de cerdo marinado con piña y cilantro.", 15.50, "Principal"),
                        ("Enchiladas Suizas",
                         "Tortillas de maíz rellenas de pollo, cubiertas con salsa verde y queso.", 12.00, "Principal"),
                        ("Guacamole con Totopos",
                         "Aguacate machacado con tomate, cebolla, cilantro y un toque de limón.", 8.75, "Entrada"),
                        ("Sopa de Tortilla",
                         "Caldo de tomate con tiras de tortilla frita, queso y aguacate.", 7.50, "Entrada"),
                        ("Cochinita Pibil",
                         "Carne de cerdo marinada en achiote, cocinada lentamente y servida con cebolla morada.", 18.00, "Principal"),
                        ("Agua de Jamaica",
                         "Bebida refrescante hecha de la flor de hibisco.", 4.00, "Bebida"),
                    ],
                )

            # Verificar 'inventario'
            cur.execute("SELECT COUNT(*) AS c FROM inventario;")
            count_inv = cur.fetchone()["c"]
            if count_inv == 0:
                cur.executemany(
                    "INSERT INTO inventario (nombre_ingrediente, cantidad, unidad_medida, stock_minimo) VALUES (?, ?, ?, ?);",
                    [
                        ("Aguacate", 50, "unidades", 10),
                        ("Pollo", 20, "kg", 5),
                        ("Maíz", 100, "kg", 20),
                        ("Cilantro", 10, "kg", 2),
                        ("Piña", 30, "unidades", 5),
                        ("Carne de Cerdo", 25, "kg", 5),
                    ],
                )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al insertar datos iniciales: {e}")

    # --- CRUD: Menú ---

    def get_menu(self, tipo: Optional[str] = None) -> List[Dict]:
        """Obtiene platos del menú. Opcionalmente filtra por tipo."""
        try:
            cur = self.conn.cursor()
            if tipo:
                cur.execute("SELECT * FROM menu WHERE tipo = ? ORDER BY nombre_plato;", (tipo,))
            else:
                cur.execute("SELECT * FROM menu ORDER BY tipo, nombre_plato;")
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener menú: {e}")

    def get_plato_por_id(self, id_plato: int) -> Optional[Dict]:
        """Obtiene un plato por su ID."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM menu WHERE id_plato = ?;", (id_plato,))
            row = cur.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener plato: {e}")

    def add_plato(self, nombre: str, descripcion: str, precio: float, tipo: str) -> int:
        """Inserta un plato y retorna su ID."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO menu (nombre_plato, descripcion, precio, tipo) VALUES (?, ?, ?, ?);",
                (nombre, descripcion, precio, tipo),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al insertar plato: {e}")

    def update_plato(self, id_plato: int, nombre: str, descripcion: str, precio: float, tipo: str) -> None:
        """Actualiza un plato existente."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE menu SET nombre_plato = ?, descripcion = ?, precio = ?, tipo = ? WHERE id_plato = ?;",
                (nombre, descripcion, precio, tipo, id_plato),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al actualizar plato: {e}")

    def delete_plato(self, id_plato: int) -> None:
        """Elimina un plato por ID."""
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM menu WHERE id_plato = ?;", (id_plato,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al eliminar plato: {e}")

    # --- CRUD: Pedidos y detalle ---

    def create_pedido(self, id_habitacion: int, fecha: str, hora: str, estado: str) -> int:
        """Crea un pedido y retorna el ID."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO pedidos (id_habitacion, fecha_pedido, hora_pedido, estado) VALUES (?, ?, ?, ?);",
                (id_habitacion, fecha, hora, estado),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al crear pedido: {e}")

    def update_estado_pedido(self, id_pedido: int, estado: str) -> None:
        """Actualiza el estado de un pedido."""
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE pedidos SET estado = ? WHERE id_pedido = ?;", (estado, id_pedido))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al actualizar estado del pedido: {e}")

    def add_detalle_pedido(self, id_pedido: int, id_plato: int, cantidad: int, precio_unitario: float) -> int:
        """Agrega un detalle al pedido y retorna el ID del detalle."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO detalle_pedidos (id_pedido, id_plato, cantidad, precio_unitario) VALUES (?, ?, ?, ?);",
                (id_pedido, id_plato, cantidad, precio_unitario),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al agregar detalle de pedido: {e}")

    def get_detalles_pedido(self, id_pedido: int) -> List[Dict]:
        """Obtiene el detalle de un pedido (join con menú)."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT dp.id_detalle_pedido, dp.id_pedido, dp.id_plato, dp.cantidad, dp.precio_unitario,
                       m.nombre_plato, m.tipo
                FROM detalle_pedidos AS dp
                JOIN menu AS m ON m.id_plato = dp.id_plato
                WHERE dp.id_pedido = ?
                ORDER BY dp.id_detalle_pedido;
                """,
                (id_pedido,),
            )
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener detalles del pedido: {e}")

    # --- CRUD: Inventario ---

    def get_inventario(self) -> List[Dict]:
        """Lista el inventario completo."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM inventario ORDER BY nombre_ingrediente;")
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener inventario: {e}")

    def get_ingrediente_por_nombre(self, nombre: str) -> Optional[Dict]:
        """Busca ingrediente por nombre exacto."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM inventario WHERE nombre_ingrediente = ?;", (nombre,))
            row = cur.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al obtener ingrediente: {e}")

    def update_inventario_cantidad(self, nombre: str, delta: int) -> None:
        """
        Aplica un delta a la cantidad de un ingrediente (positivo o negativo).
        Lanza error si el resultado sería negativo.
        """
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT cantidad FROM inventario WHERE nombre_ingrediente = ?;", (nombre,))
            row = cur.fetchone()
            if not row:
                raise RuntimeError(f"Ingrediente '{nombre}' no existe.")
            nueva = row["cantidad"] + delta
            if nueva < 0:
                raise RuntimeError(f"Stock insuficiente para '{nombre}'. Operación cancelada.")
            cur.execute(
                "UPDATE inventario SET cantidad = ? WHERE nombre_ingrediente = ?;",
                (nueva, nombre),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al actualizar inventario: {e}")

    def get_bajo_stock(self) -> List[Dict]:
        """Retorna ingredientes cuyo stock está por debajo del mínimo."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "SELECT * FROM inventario WHERE cantidad < stock_minimo ORDER BY nombre_ingrediente;"
            )
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Error al verificar bajo stock: {e}")

    # --- CRUD: Transacciones ---

    def record_transaccion(self, id_pedido: int, fecha: str, monto_total: float, metodo_pago: Optional[str]) -> int:
        """Registra una transacción y retorna su ID."""
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO transacciones (id_pedido, fecha_transaccion, monto_total, metodo_pago) VALUES (?, ?, ?, ?);",
                (id_pedido, fecha, monto_total, metodo_pago),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Error al registrar transacción: {e}")
