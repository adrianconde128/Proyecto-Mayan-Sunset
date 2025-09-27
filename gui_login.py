# gui_login.py
# Capa de presentación: ventana de login, widgets y eventos.

import tkinter as tk
from tkinter import ttk
from logica import LogicaApp

class VentanaLogin(tk.Toplevel):
    """
    Ventana de Login simple:
    - Campo usuario
    - Campo contraseña (oculta caracteres)
    - Botón Ingresar
    """
    def __init__(self, root: tk.Tk, logica: LogicaApp):
        super().__init__(root)
        self.root = root
        self.logica = logica

        self.title("Mayan Sunset - Login")
        self.geometry("360x220")
        self.resizable(False, False)

        # Centrar ventana respecto al root
        self.transient(root)
        self.grab_set()

        # Variables de entrada
        self.var_usuario = tk.StringVar()
        self.var_contrasena = tk.StringVar()

        self._construir_ui()

        # Enfocar usuario al abrir
        self.entry_usuario.focus_set()

    def _construir_ui(self):
        frm = ttk.Frame(self, padding=16)
        frm.pack(expand=True, fill="both")

        lbl_titulo = ttk.Label(frm, text="Ingreso al sistema", font=("Segoe UI", 12, "bold"))
        lbl_titulo.pack(pady=(0, 12))

        # Usuario
        cont_usuario = ttk.Frame(frm)
        cont_usuario.pack(fill="x", pady=6)
        ttk.Label(cont_usuario, text="Usuario:").pack(anchor="w")
        self.entry_usuario = ttk.Entry(cont_usuario, textvariable=self.var_usuario)
        self.entry_usuario.pack(fill="x")

        # Contraseña
        cont_contrasena = ttk.Frame(frm)
        cont_contrasena.pack(fill="x", pady=6)
        ttk.Label(cont_contrasena, text="Contraseña:").pack(anchor="w")
        self.entry_contrasena = ttk.Entry(cont_contrasena, textvariable=self.var_contrasena, show="•")
        self.entry_contrasena.pack(fill="x")

        # Botón ingresar
        btn_ingresar = ttk.Button(frm, text="Ingresar", command=self._on_ingresar)
        btn_ingresar.pack(pady=12)

        # Atajos de teclado
        self.bind("<Return>", lambda e: self._on_ingresar())
        self.bind("<Escape>", lambda e: self.destroy())

    def _on_ingresar(self):
        usuario = self.var_usuario.get()
        contrasena = self.var_contrasena.get()

        es_valido, user_dict, mensaje = self.logica.validar_credenciales(usuario, contrasena)
        if not es_valido:
            self.logica.mostrar_error(mensaje)
            return

        # Cierra la ventana de login y abre el menú principal
        self.destroy()
        self.logica.abrir_menu_principal(user_dict)
