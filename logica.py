# logica.py
# Capa de lógica del negocio: valida usuarios y gestiona navegación entre pantallas.

from typing import Tuple, Optional, Dict
import tkinter as tk
from tkinter import messagebox

from datos import obtener_usuario_por_credenciales
from gui_menu import VentanaMenu

class LogicaApp:
    """
    Intermediario entre GUI y capa de datos.
    Expone métodos de validación y navegación.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        # Estado de sesión simple (podría evolucionar a un objeto más rico)
        self.usuario_actual: Optional[Dict] = None

    def validar_credenciales(self, usuario: str, contrasena: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Valida las credenciales contra la base de datos.
        Retorna (es_valido, usuario_dict, mensaje).
        """
        if not usuario.strip():
            return False, None, "El nombre de usuario es obligatorio."
        if not contrasena.strip():
            return False, None, "La contraseña es obligatoria."

        user = obtener_usuario_por_credenciales(usuario.strip(), contrasena.strip())
        if user is None:
            return False, None, "Credenciales incorrectas. Verifique usuario y contraseña."

        # Normalizamos tipo de usuario para comparaciones futuras
        tipo = (user.get("tipo_usuario") or "").strip().lower()
        if tipo not in {"administrador", "empleado"}:
            # Si el tipo no es válido, lo tratamos como error de negocio
            return False, None, "El tipo de usuario no es válido. Contacte al administrador."

        self.usuario_actual = user
        return True, user, "Acceso concedido."

    def abrir_menu_principal(self, datos_usuario: Dict) -> None:
        """
        Abre la ventana del menú principal con base en los datos del usuario autenticado.
        La ventana de menu es un Toplevel, hija de root.
        """
        VentanaMenu(self.root, datos_usuario)

    def mostrar_error(self, mensaje: str) -> None:
        """
        Muestra un error de negocio en un messagebox.
        """
        messagebox.showerror("Error de autenticación", mensaje)

    def mostrar_info(self, titulo: str, mensaje: str) -> None:
        """
        Muestra información general.
        """
        messagebox.showinfo(titulo, mensaje)
