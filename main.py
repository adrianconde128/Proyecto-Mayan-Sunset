# main.py
# Punto de entrada de la aplicación.
# Inicia la raíz de Tkinter, prepara la base de datos y muestra la ventana de login.

import tkinter as tk
from logica import LogicaApp
from gui_login import VentanaLogin
from datos import seed_usuario   # <-- Importamos la función de inicialización

def main():
    # Inicializa la base de datos y usuarios semilla
    seed_usuario()

    root = tk.Tk()
    root.title("Mayan Sunset - Inicio")
    root.geometry("360x220")
    root.resizable(False, False)

    # Instancia de la capa de lógica (intermediario entre GUI y datos)
    logica = LogicaApp(root)

    # Crea la ventana de login como Toplevel (hija de root)
    VentanaLogin(root, logica)

    # Muestra el loop principal
    root.mainloop()

if __name__ == "__main__":
    main()
