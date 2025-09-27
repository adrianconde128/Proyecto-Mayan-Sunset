import Hotel

def run_tests():
    print("=== PRUEBAS AUTOMATIZADAS DE RESERVAS ===")

    # Caso 1: Reserva válida
    exito, mensaje = Hotel.crear_reserva({
        "numero_habitacion": "H107",
        "dpi": "1234567890123",
        "nit": "12345678901",
        "primer_nombre": "Carlos",
        "segundo_nombre": "Eduardo",
        "primer_apellido": "Pérez",
        "segundo_apellido": "Garcia",
        "fecha_ingreso": "2025-11-01",
        "fecha_salida": "2025-11-05",
        "id_huesped": 1,
        "tipo": "Individual"
    })
    print(f"[OK] {mensaje}" if exito else f"[FAIL] {mensaje}")

    # Caso 2: Número de habitación inválido
    exito, mensaje = Hotel.crear_reserva({
        "numero_habitacion": "H999",
        "dpi": "1234567890123",
        "nit": "12345678901",
        "primer_nombre": "Ana",
        "segundo_nombre": "",
        "primer_apellido": "García",
        "segundo_apellido": "",
        "fecha_ingreso": "2025-10-10",
        "fecha_salida": "2025-10-12",
        "id_huesped": 2,
        "tipo": "Sencilla"
    })
    print("[OK] Rechazado número inválido" if not exito else "[FAIL] Se aceptó número inválido")

    # Caso 3: Validación de longitudes
    exito, mensaje = Hotel.crear_reserva({
        "numero_habitacion": "H001",
        "dpi": "12345678901234",  # 14 dígitos
        "nit": "12345678901",
        "primer_nombre": "NombreMuyLargoQueSupera25Caracteres",
        "segundo_nombre": "",
        "primer_apellido": "Apellido",
        "segundo_apellido": "",
        "fecha_ingreso": "2025-11-01",
        "fecha_salida": "2025-11-03",
        "id_huesped": 3,
        "tipo": "Sencilla"
    })
    print("[OK] Rechazado por validación de longitudes" if not exito else "[FAIL] Se aceptaron datos fuera de rango")

    # Caso 4: Disponibilidad (reserva solapada)
    Hotel.crear_reserva({
        "numero_habitacion": "H002",
        "dpi": "1234567890999",
        "nit": "12345678901",
        "primer_nombre": "Luis",
        "segundo_nombre": "",
        "primer_apellido": "Santos",
        "segundo_apellido": "",
        "fecha_ingreso": "2025-12-01",
        "fecha_salida": "2025-12-05",
        "id_huesped": 4,
        "tipo": "Sencilla"
    })
    exito, mensaje = Hotel.crear_reserva({
        "numero_habitacion": "H002",
        "dpi": "1234567890888",
        "nit": "12345678901",
        "primer_nombre": "Miguel",
        "segundo_nombre": "",
        "primer_apellido": "Ruiz",
        "segundo_apellido": "",
        "fecha_ingreso": "2025-12-03",
        "fecha_salida": "2025-12-04",
        "id_huesped": 5,
        "tipo": "Sencilla"
    })
    print("[OK] Rechazada reserva solapada" if not exito else "[FAIL] Se aceptó reserva solapada")

if __name__ == "__main__":
    run_tests()
