import sqlite3
from hotel_db import create_connection
from datetime import datetime

def crear_reserva(data):
    """
    Función para crear una nueva reserva y registrar al huésped.
    `data` es un diccionario con toda la información del formulario.
    """
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        
        # 1. Insertar o actualizar huésped
        huesped_data = (data['dpi'], data['primer_nombre'], data['segundo_nombre'], data['primer_apellido'], data['segundo_apellido'], data['nit'])
        cursor.execute("""
            INSERT OR REPLACE INTO Huesped 
            (dpi, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, nit) 
            VALUES (?, ?, ?, ?, ?, ?);
        """, huesped_data)
        
        # 2. Insertar reserva
        reserva_data = (data['dpi'], data['id_habitacion'], data['fecha_ingreso'], data['fecha_salida'], data['precio_total'])
        cursor.execute("""
            INSERT INTO Reservas_Hotel (dpi_huesped, id_habitacion, fecha_ingreso, fecha_salida, precio_total) 
            VALUES (?, ?, ?, ?, ?);
        """, reserva_data)
        
        # 3. Actualizar estado de la habitación
        cursor.execute("""
            UPDATE Habitacion SET estado = ? WHERE id_habitacion = ?;
        """, ("Ocupada", data['id_habitacion']))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al crear reserva: {e}")
        return False
    finally:
        conn.close()

def calcular_precio_total(fecha_ingreso, fecha_salida, precio_por_noche):
    """
    Calcula el precio total de la estadía basado en las fechas.
    """
    try:
        formato_fecha = "%Y-%m-%d"
        inicio = datetime.strptime(fecha_ingreso, formato_fecha)
        fin = datetime.strptime(fecha_salida, formato_fecha)
        
        diferencia = fin - inicio
        dias = diferencia.days
        
        if dias < 0:
            return 0
        return dias * precio_por_noche
    except ValueError:
        return 0