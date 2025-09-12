import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================
# 1. CONEXIÓN Y CREACIÓN DE TABLAS
# ==========================
def conectar_db():
    """Crea la base de datos y las tablas necesarias si no existen."""
    conn = sqlite3.connect("mayan_sunset.db")
    cursor = conn.cursor()

# Tabla de huéspedes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Huesped (
        HUE_Id_Huesped INTEGER PRIMARY KEY AUTOINCREMENT,
        HUE_Primer_Nombre TEXT,
        HUE_Primer_Apellido TEXT
    )
    """)

# Tabla de habitaciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Habitacion (
        HAB_Id_Habitacion INTEGER PRIMARY KEY AUTOINCREMENT,
        HAB_Tipo_Habitacion TEXT,
        HAB_Estado_Habitacion TEXT,
        HAB_Precio_Habitacion REAL
    )
    """)

# Tabla de reservas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reservas_Hotel (
        RES_Id_Reserva INTEGER PRIMARY KEY AUTOINCREMENT,
        RES_Fecha_Ingreso TEXT,
        RES_Fecha_Salida TEXT,
        RES_Estado_Reserva TEXT,
        RES_Precio_Total REAL,
        HUE_Id_Huesped INTEGER,
        HAB_Id_Habitacion INTEGER,
        FOREIGN KEY (HUE_Id_Huesped) REFERENCES Huesped(HUE_Id_Huesped),
        FOREIGN KEY (HAB_Id_Habitacion) REFERENCES Habitacion(HAB_Id_Habitacion)
    )
    """)
    conn.commit()
    conn.close()
    
    
# ==========================
# 2. FUNCIONES CRUD
# ==========================
def agregar_reserva():
    """Inserta una nueva reserva en la base de datos."""
    if not entry_fecha_ingreso.get() or not entry_fecha_salida.get():
        messagebox.showwarning("Validación", "Debe ingresar fechas de ingreso y salida")
        return
    conn = sqlite3.connect("mayan_sunset.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Reservas_Hotel 
        (RES_Fecha_Ingreso, RES_Fecha_Salida, RES_Estado_Reserva, RES_Precio_Total, HUE_Id_Huesped, HAB_Id_Habitacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        entry_fecha_ingreso.get(),
        entry_fecha_salida.get(),
        combo_estado.get(),
        float(entry_precio.get()),
        int(entry_huesped.get()),
        int(entry_habitacion.get())
    ))
    conn.commit()
    conn.close()
    listar_reservas()
    limpiar_campos()
    messagebox.showinfo("Éxito", "Reserva agregada correctamente")

def listar_reservas():
    """Carga todas las reservas en el Treeview."""
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("mayan_sunset.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Reservas_Hotel")
    for reserva in cursor.fetchall():
        tree.insert("", tk.END, values=reserva)
    conn.close()

def eliminar_reserva():
    """Elimina la reserva seleccionada."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Atención", "Seleccione una reserva para eliminar")
        return
    reserva_id = tree.item(selected[0])["values"][0]
    conn = sqlite3.connect("mayan_sunset.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Reservas_Hotel WHERE RES_Id_Reserva=?", (reserva_id,))
    conn.commit()
    conn.close()
    listar_reservas()
    messagebox.showinfo("Éxito", "Reserva eliminada")

def actualizar_reserva():
    """Actualiza la reserva seleccionada."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Atención", "Seleccione una reserva para actualizar")
        return
    reserva_id = tree.item(selected[0])["values"][0]
    conn = sqlite3.connect("mayan_sunset.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Reservas_Hotel
        SET RES_Fecha_Ingreso=?, RES_Fecha_Salida=?, RES_Estado_Reserva=?, RES_Precio_Total=?, HUE_Id_Huesped=?, HAB_Id_Habitacion=?
        WHERE RES_Id_Reserva=?
    """, (
        entry_fecha_ingreso.get(),
        entry_fecha_salida.get(),
        combo_estado.get(),
        float(entry_precio.get()),
        int(entry_huesped.get()),
        int(entry_habitacion.get()),
        reserva_id
    ))
    conn.commit()
    conn.close()
    listar_reservas()
    limpiar_campos()
    messagebox.showinfo("Éxito", "Reserva actualizada")

def limpiar_campos():
    """Limpia los campos de entrada."""
    entry_fecha_ingreso.delete(0, tk.END)
    entry_fecha_salida.delete(0, tk.END)
    entry_precio.delete(0, tk.END)
    entry_huesped.delete(0, tk.END)
    entry_habitacion.delete(0, tk.END)
    combo_estado.set("")

# ==========================
# 3. INTERFAZ TKINTER
# ==========================
root = tk.Tk()
root.title("Módulo de Reservaciones - Hotel Mayan Sunset")
root.geometry("900x500")

# Campos de entrada
tk.Label(root, text="Fecha Ingreso (YYYY-MM-DD)").grid(row=0, column=0)
entry_fecha_ingreso = tk.Entry(root)
entry_fecha_ingreso.grid(row=0, column=1)

tk.Label(root, text="Fecha Salida (YYYY-MM-DD)").grid(row=1, column=0)
entry_fecha_salida = tk.Entry(root)
entry_fecha_salida.grid(row=1, column=1)

tk.Label(root, text="Estado").grid(row=2, column=0)
combo_estado = ttk.Combobox(root, values=["Confirmada", "Pendiente", "Cancelada"])
combo_estado.grid(row=2, column=1)

tk.Label(root, text="Precio Total").grid(row=3, column=0)
entry_precio = tk.Entry(root)
entry_precio.grid(row=3, column=1)

tk.Label(root, text="ID Huésped").grid(row=4, column=0)
entry_huesped = tk.Entry(root)
entry_huesped.grid(row=4, column=1)

tk.Label(root, text="ID Habitación").grid(row=5, column=0)
entry_habitacion = tk.Entry(root)
entry_habitacion.grid(row=5, column=1)

# Botones
tk.Button(root, text="Agregar", command=agregar_reserva).grid(row=6, column=0, pady=5)
tk.Button(root, text="Actualizar", command=actualizar_reserva).grid(row=6, column=1, pady=5)
tk.Button(root, text="Eliminar", command=eliminar_reserva).grid(row=6, column=2, pady=5)
tk.Button(root, text="Limpiar", command=limpiar_campos).grid(row=6, column=3, pady=5)

# Tabla de reservas
tree = ttk.Treeview(root, columns=("ID", "Ingreso", "Salida", "Estado", "Precio", "Huesped", "Habitacion"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
tree.grid(row=7, column=0, columnspan=4, pady=10)
# Inicializar
conectar_db()
listar_reservas()
root.mainloop()
