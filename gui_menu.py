# gui_menu.py
# Capa de presentación: menú principal, botones y visibilidad por rol.

import tkinter as tk
from tkinter import ttk, messagebox

class VentanaMenu(tk.Toplevel):
    """
    Ventana de menú principal:
    - Muestra bienvenida con tipo de usuario.
    - Botones: Reservaciones, Restaurante (TODO), Hotel (TODO), Reportes (TODO).
    - Botón Gestión de Usuarios visible solo para Administrador (TODO).
    """
    def __init__(self, root: tk.Tk, datos_usuario: dict):
        super().__init__(root)
        self.root = root
        self.datos_usuario = datos_usuario

        self.title("Mayan Sunset - Menú Principal")
        self.geometry("500x320")
        self.resizable(False, False)

        # Estado del usuario
        self.usuario = datos_usuario.get("usuario", "Usuario")
        self.tipo_usuario = (datos_usuario.get("tipo_usuario") or "").strip().lower()

        self._construir_ui()

    def _construir_ui(self):
        frm = ttk.Frame(self, padding=16)
        frm.pack(expand=True, fill="both")

        # Bienvenida
        rol_texto = "Administrador" if self.tipo_usuario == "administrador" else "Empleado"
        lbl_bienvenida = ttk.Label(
            frm,
            text=f"¡Bienvenido, {rol_texto}! ({self.usuario})",
            font=("Segoe UI", 12, "bold"),
        )
        lbl_bienvenida.pack(pady=(0, 12))

        # Botones principales
        cont_botones = ttk.Frame(frm)
        cont_botones.pack(expand=True, fill="both")

        # Reservaciones
        btn_reservaciones = ttk.Button(cont_botones, text="Reservaciones", command=self._abrir_reservaciones)
        btn_reservaciones.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        # Restaurante (TODO)
        btn_restaurante = ttk.Button(cont_botones, text="Restaurante", command=self._restaurante_todo)
        btn_restaurante.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        # Hotel (TODO)
        btn_hotel = ttk.Button(cont_botones, text="Hotel", command=self._hotel_todo)
        btn_hotel.grid(row=0, column=2, padx=8, pady=8, sticky="ew")

        # Reportes (TODO)
        btn_reportes = ttk.Button(cont_botones, text="Reportes", command=self._reportes_todo)
        btn_reportes.grid(row=1, column=0, padx=8, pady=8, sticky="ew")

        # Gestión de Usuarios — visible solo para Administrador (TODO)
        if self.tipo_usuario == "administrador":
            btn_gestion_usuarios = ttk.Button(cont_botones, text="Gestión de Usuarios", command=self._gestion_usuarios_todo)
            btn_gestion_usuarios.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        # Configurar grid expansión
        for c in range(0, 3):
            cont_botones.columnconfigure(c, weight=1)

        # Pie
        lbl_pie = ttk.Label(frm, text="Mayan Sunset ©", font=("Segoe UI", 9))
        lbl_pie.pack(side="bottom", pady=(12, 0))

    # gui_menu.py (dentro de VentanaMenu)
    def _abrir_reservaciones(self):
        try:
            from gui_hotel_mayan_sunset import VentanaReservaciones
            VentanaReservaciones(self.root)
        except Exception as e:
            messagebox.showerror("Error al abrir Reservaciones", str(e))


    def _restaurante_todo(self):
        # TODO: Implementar formulario del restaurante
        messagebox.showinfo("Próximamente", "Módulo de Restaurante en desarrollo.")

    def _hotel_todo(self):
        # TODO: Implementar servicios del hotel
        messagebox.showinfo("Próximamente", "Módulo de Hotel en desarrollo.")

    def _reportes_todo(self):
        # TODO: Implementar generación de reportes (ventas, ocupación, etc.)
        messagebox.showinfo("Próximamente", "Módulo de Reportes en desarrollo.")

    def _gestion_usuarios_todo(self):
        # TODO: Implementar CRUD de usuarios (visible solo para Administrador)
        messagebox.showinfo("Próximamente", "Gestión de Usuarios en desarrollo (solo Administrador).")
