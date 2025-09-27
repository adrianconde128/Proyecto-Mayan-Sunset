# gui_hotel_mayan_sunset.py
# Refactor robusto: encapsula la UI en VentanaReservaciones(Toplevel),
# preserva validaciones, assets y lógica con Hotel/hotel_db,
# y corrige el handler de "Guardar" para evitar AttributeError.

import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Canvas, Entry, Button, PhotoImage, StringVar

import Hotel  # Capa de negocio (valida, calcula y orquesta llamadas a hotel_db)
from hotel_db import listar_numeros_habitacion, get_connection as get_conn

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\Usua\OneDrive\Desktop\Proyecto Mayan Sunset\gui_mayan_sunset\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


class VentanaReservaciones(tk.Toplevel):
    """
    Ventana de creación de reservas (Toplevel).
    - Mantiene layout Figma con Canvas y Scrollbar.
    - Validaciones por campo y cálculo de total por noches.
    - Integra con capa de negocio (Hotel) y DB (hotel_db).
    """

    def __init__(self, root: tk.Tk):
        super().__init__(root)
        self.root = root
        self.title("Mayan Sunset - Creación de Reservas")
        self.geometry("1200x1000")
        self.configure(bg="#FFFFFF")
        self.resizable(True, True)

        # Inicialización del sistema de Hotel al abrir la ventana (no en import)
        try:
            Hotel.inicializar_sistema()
        except Exception as e:
            messagebox.showwarning("Inicialización", f"No se pudo inicializar el sistema de Hotel.\n{e}")

        # Estado interno
        self.precio_noche_actual = None

        # Validadores registrados contra este Toplevel
        self.vcmd_num = self.register(self._validar_numerico)
        self.vcmd_texto = self.register(self._validar_texto)
        self.vcmd_fecha_char = self.register(self._validar_fecha_caracter)

        # Referencias de imágenes para evitar GC
        self.entry_image_1 = None
        self.entry_image_2 = None
        self.entry_image_3 = None
        self.entry_image_4 = None
        self.entry_image_5 = None
        self.entry_image_6 = None
        self.entry_image_7 = None
        self.entry_image_8 = None
        self.entry_image_9 = None
        self.entry_image_10 = None
        self.entry_image_11 = None
        self.entry_image_12 = None
        self.image_image_1 = None
        self.button_image_1 = None
        self.button_image_hover_1 = None
        self.button_image_2 = None
        self.button_image_hover_2 = None

        # Construcción de UI
        self._construir_ui()

        # Bind de scroll y wheel
        self.inner_canvas.bind("<Configure>", self._update_scrollregion)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        # Inicializaciones dependientes de datos
        self._cargar_tipos_habitacion()
        self._cargar_numeros_habitacion()

    # =========================
    # Validaciones de entrada
    # =========================
    def _validar_numerico(self, char: str) -> bool:
        return char.isdigit()

    def _validar_texto(self, char: str) -> bool:
        return char.isalpha() or char.isspace()

    def _validar_fecha_caracter(self, char: str) -> bool:
        return char.isdigit() or char == "-"

    def _validar_formato_fecha(self, entry_widget: tk.Entry) -> bool:
        valor = entry_widget.get().strip()
        if not valor:
            return False
        patron = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(patron, valor):
            return False
        try:
            datetime.strptime(valor, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # =========================
    # Construcción de UI (toda tu interfaz preservada)
    # =========================
    def _construir_ui(self):
        # Contenedor con scroll
        self.scroll_canvas = Canvas(self, bg="#FFFFFF", highlightthickness=0)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Canvas Figma dentro del contenedor
        self.inner_canvas = Canvas(
            self.scroll_canvas,
            bg="#FFFFFF",
            height=1000,
            width=1200,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.scroll_canvas.create_window((0, 0), window=self.inner_canvas, anchor="nw")

        # Panel derecho verde
        self.inner_canvas.create_rectangle(600.0, 0.0, 1200.0, 1000.0, fill="#5D8D5A", outline="")

        # entry_1 -> Precio Total (readonly)
        self.entry_image_1 = PhotoImage(master=self, file=relative_to_assets("entry_1.png"))
        self.inner_canvas.create_image(1044.5, 709.5, image=self.entry_image_1)
        self.entry_1 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, state="readonly")
        self.entry_1.place(x=932.0, y=692.0, width=225.0, height=33.0)

        # Label Precio Total
        self.inner_canvas.create_text(922.0, 660.0, anchor="nw", text="Precio Total", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # Label Tipo de Habitación
        self.inner_canvas.create_text(632.0, 660.0, anchor="nw", text="Tipo de Habitación", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # entry_2 -> Tipo de Habitación (Combobox)
        self.entry_image_2 = PhotoImage(master=self, file=relative_to_assets("entry_2.png"))
        self.inner_canvas.create_image(754.5, 709.5, image=self.entry_image_2)

        self.combo_tipo_habitacion = ttk.Combobox(self.inner_canvas, values=[], state="readonly")
        self.combo_tipo_habitacion.place(x=642.0, y=692.0, width=225.0, height=33.0)
        self.combo_tipo_habitacion.bind("<<ComboboxSelected>>", self._actualizar_precio_noche)

        # Label Número de Habitación
        self.inner_canvas.create_text(632.0, 755.0, anchor="nw", text="Número de Habitación", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # Combobox -> Número de Habitación
        self.entry_image_3 = PhotoImage(master=self, file=relative_to_assets("entry_3.png"))
        self.inner_canvas.create_image(754.5, 804.5, image=self.entry_image_3)

        self.numero_hab_var = StringVar()
        self.combo_numero_hab = ttk.Combobox(self.inner_canvas, textvariable=self.numero_hab_var, values=[], state="readonly")
        self.combo_numero_hab.place(x=642.0, y=787.0, width=225.0, height=33.0)

        # Label Estado
        self.inner_canvas.create_text(922.0, 755.0, anchor="nw", text="Estado", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # entry_4 -> Estado (Combobox)
        self.entry_image_4 = PhotoImage(master=self, file=relative_to_assets("entry_4.png"))
        self.inner_canvas.create_image(1044.5, 804.5, image=self.entry_image_4)

        self.combo_estado = ttk.Combobox(self.inner_canvas, values=["Disponible", "Ocupada", "Mantenimiento"], state="readonly")
        self.combo_estado.place(x=932.0, y=787.0, width=225.0, height=33.0)

        # entry_5 -> Fecha de Salida
        self.entry_image_5 = PhotoImage(master=self, file=relative_to_assets("entry_5.png"))
        self.inner_canvas.create_image(1044.5, 614.5, image=self.entry_image_5)
        self.entry_5 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_5.place(x=932.0, y=597.0, width=225.0, height=33.0)
        self.entry_5.config(validate="key", validatecommand=(self.vcmd_fecha_char, "%S"))
        self.entry_5.bind("<FocusOut>", self._calcular_total)

        # Label Fecha de Ingreso
        self.inner_canvas.create_text(632.0, 540.0, anchor="nw", text="Fecha de Ingreso\nAAAA-MM-DD", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # Label Datos de la Estadía (sección)
        self.inner_canvas.create_text(632.0, 496.0, anchor="nw", text="Datos de la Estadía", fill="#FFFFFF", font=("Lato Bold", 20 * -1))

        # Label Fecha de Salida
        self.inner_canvas.create_text(922.0, 540.0, anchor="nw", text="Fecha de Salida\nAAAA-MM-DD", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # entry_6 -> Fecha de Ingreso
        self.entry_image_6 = PhotoImage(master=self, file=relative_to_assets("entry_6.png"))
        self.inner_canvas.create_image(754.5, 614.5, image=self.entry_image_6)
        self.entry_6 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_6.place(x=642.0, y=597.0, width=225.0, height=33.0)
        self.entry_6.config(validate="key", validatecommand=(self.vcmd_fecha_char, "%S"))
        self.entry_6.bind("<FocusOut>", self._calcular_total)

        # entry_7 -> NIT
        self.entry_image_7 = PhotoImage(master=self, file=relative_to_assets("entry_7.png"))
        self.inner_canvas.create_image(1044.5, 439.5, image=self.entry_image_7)
        self.entry_7 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_7.place(x=932.0, y=422.0, width=225.0, height=33.0)
        self.entry_7.config(validate="key", validatecommand=(self.vcmd_num, "%S"))

        # Label NIT
        self.inner_canvas.create_text(922.0, 382.0, anchor="nw", text="NIT", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # Label DPI
        self.inner_canvas.create_text(632.0, 382.0, anchor="nw", text="DPI", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # entry_8 -> DPI
        self.entry_image_8 = PhotoImage(master=self, file=relative_to_assets("entry_8.png"))
        self.inner_canvas.create_image(754.5, 439.5, image=self.entry_image_8)
        self.entry_8 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_8.place(x=642.0, y=422.0, width=225.0, height=33.0)
        self.entry_8.config(validate="key", validatecommand=(self.vcmd_num, "%S"))

        # entry_9 -> 2do Apellido
        self.entry_image_9 = PhotoImage(master=self, file=relative_to_assets("entry_9.png"))
        self.inner_canvas.create_image(1044.5, 329.5, image=self.entry_image_9)
        self.entry_9 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_9.place(x=932.0, y=312.0, width=225.0, height=33.0)
        self.entry_9.config(validate="key", validatecommand=(self.vcmd_texto, "%S"))

        # Label 2do Apellido
        self.inner_canvas.create_text(922.0, 268.0, anchor="nw", text="2do Apellido", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # Label 1er Apellido
        self.inner_canvas.create_text(632.0, 268.0, anchor="nw", text="1er Apellido", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # entry_10 -> 1er Apellido
        self.entry_image_10 = PhotoImage(master=self, file=relative_to_assets("entry_10.png"))
        self.inner_canvas.create_image(754.5, 329.5, image=self.entry_image_10)
        self.entry_10 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_10.place(x=642.0, y=312.0, width=225.0, height=33.0)
        self.entry_10.config(validate="key", validatecommand=(self.vcmd_texto, "%S"))

        # entry_11 -> 2do Nombre
        self.entry_image_11 = PhotoImage(master=self, file=relative_to_assets("entry_11.png"))
        self.inner_canvas.create_image(1044.5, 219.5, image=self.entry_image_11)
        self.entry_11 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_11.place(x=932.0, y=202.0, width=225.0, height=33.0)
        self.entry_11.config(validate="key", validatecommand=(self.vcmd_texto, "%S"))

        # Label 2do Nombre
        self.inner_canvas.create_text(922.0, 162.0, anchor="nw", text="2do Nombre", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # Label 1er Nombre
        self.inner_canvas.create_text(632.0, 162.0, anchor="nw", text="1er Nombre", fill="#FFFFFF", font=("Lato Regular", 20 * -1))

        # Label Datos del Huésped (sección)
        self.inner_canvas.create_text(632.0, 113.0, anchor="nw", text="Datos del Huésped", fill="#FFFFFF", font=("Lato Bold", 20 * -1))

        # Título Creación de Reservas
        self.inner_canvas.create_text(710.0, 31.0, anchor="nw", text="Creación de Reservas", fill="#FFFFFF", font=("Lato Bold", 40 * -1))

        # entry_12 -> 1er Nombre
        self.entry_image_12 = PhotoImage(master=self, file=relative_to_assets("entry_12.png"))
        self.inner_canvas.create_image(754.5, 219.5, image=self.entry_image_12)
        self.entry_12 = Entry(self.inner_canvas, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_12.place(x=642.0, y=202.0, width=225.0, height=33.0)
        self.entry_12.config(validate="key", validatecommand=(self.vcmd_texto, "%S"))

        # Imagen decorativa izquierda
        self.image_image_1 = PhotoImage(master=self, file=relative_to_assets("image_1.png"))
        self.inner_canvas.create_image(300.0, 500.0, image=self.image_image_1)

        # Botón 1 (Guardar) — apunta a método existente
        self.button_image_1 = PhotoImage(master=self, file=relative_to_assets("button_1.png"))
        self.button_1 = Button(
            self.inner_canvas,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self._guardar_reserva,   # <- Método definido más abajo
            relief="flat"
        )
        self.button_1.place(x=660.0, y=882.0, width=180.0, height=60.0)

        self.button_image_hover_1 = PhotoImage(master=self, file=relative_to_assets("button_hover_1.png"))
        self.button_1.bind('<Enter>', lambda e: self.button_1.config(image=self.button_image_hover_1))
        self.button_1.bind('<Leave>', lambda e: self.button_1.config(image=self.button_image_1))

        # Botón 2 (Cancelar)
        self.button_image_2 = PhotoImage(master=self, file=relative_to_assets("button_2.png"))
        self.button_2 = Button(
            self.inner_canvas,
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.destroy,
            relief="flat"
        )
        self.button_2.place(x=966.0, y=882.0, width=180.0, height=60.0)

        self.button_image_hover_2 = PhotoImage(master=self, file=relative_to_assets("button_hover_2.png"))
        self.button_2.bind('<Enter>', lambda e: self.button_2.config(image=self.button_image_hover_2))
        self.button_2.bind('<Leave>', lambda e: self.button_2.config(image=self.button_image_2))

    # =========================
    # Scroll helpers
    # =========================
    def _update_scrollregion(self, event=None):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # =========================
    # Cargas de datos
    # =========================
    def _cargar_tipos_habitacion(self):
        try:
            tipos = Hotel.obtener_tipos_habitacion()
        except Exception as e:
            tipos = []
            messagebox.showerror("Tipos de habitación", f"No se pudieron cargar tipos de habitación.\n{e}")

        self.combo_tipo_habitacion["values"] = tipos
        if tipos:
            self.combo_tipo_habitacion.current(0)
            try:
                self.precio_noche_actual = Hotel.obtener_precio_por_tipo(tipos[0])
            except Exception:
                self.precio_noche_actual = None
            self._calcular_total()

    def _actualizar_precio_noche(self, event=None):
        tipo = self.combo_tipo_habitacion.get()
        if not tipo:
            return
        try:
            self.precio_noche_actual = Hotel.obtener_precio_por_tipo(tipo)
        except Exception as e:
            self.precio_noche_actual = None
            messagebox.showerror("Precio por noche", f"No se pudo obtener el precio para '{tipo}'.\n{e}")
        self._calcular_total()

    def _cargar_numeros_habitacion(self):
        try:
            with get_conn() as conn:
                self.combo_numero_hab["values"] = listar_numeros_habitacion(conn)
            if self.combo_numero_hab["values"]:
                self.combo_numero_hab.current(0)
        except Exception as e:
            messagebox.showerror("Habitaciones", f"No se pudieron cargar números de habitación.\n{e}")

    # =========================
    # Cálculo de total
    # =========================
    def _calcular_total(self, event=None):
        fecha_ingreso = (self.entry_6.get() or "").strip()
        fecha_salida = (self.entry_5.get() or "").strip()
        try:
            noches = Hotel.calcular_noches(fecha_ingreso, fecha_salida)
        except Exception:
            noches = None  # Si Hotel lanza excepción, mostramos inválidas abajo

        self.entry_1.config(state="normal")
        self.entry_1.delete(0, "end")

        if noches is None:
            self.entry_1.insert(0, "Fechas inválidas")
            self.entry_1.config(state="readonly")
            return

        if self.precio_noche_actual is None:
            tipo = self.combo_tipo_habitacion.get()
            if tipo:
                try:
                    self.precio_noche_actual = Hotel.obtener_precio_por_tipo(tipo)
                except Exception:
                    self.precio_noche_actual = None

        if self.precio_noche_actual is None:
            self.entry_1.insert(0, "")
        else:
            total = noches * self.precio_noche_actual
            self.entry_1.insert(0, f"{total:.2f}")

        self.entry_1.config(state="readonly")

    # =========================
    # Guardar reserva (método existente y correcto)
    # =========================
    def _guardar_reserva(self):
        numero_habitacion = (self.combo_numero_hab.get() or "").strip()
        tipo = (self.combo_tipo_habitacion.get() or "").strip()
        fecha_ingreso = (self.entry_6.get() or "").strip()
        fecha_salida = (self.entry_5.get() or "").strip()
        dpi = (self.entry_8.get() or "").strip()
        nit = (self.entry_7.get() or "").strip()
        primer_nombre = (self.entry_12.get() or "").strip()
        segundo_nombre = (self.entry_11.get() or "").strip()
        primer_apellido = (self.entry_10.get() or "").strip()
        segundo_apellido = (self.entry_9.get() or "").strip()
        precio_total_str = (self.entry_1.get() or "").strip()

        # Validaciones básicas
        if not tipo:
            messagebox.showerror("Error", "Debe seleccionar un tipo de habitación.")
            return
        if not self._validar_formato_fecha(self.entry_6) or not self._validar_formato_fecha(self.entry_5):
            messagebox.showerror("Error", "Las fechas deben estar en formato YYYY-MM-DD válido.")
            return
        if "inválidas" in precio_total_str.lower() or not precio_total_str:
            messagebox.showerror("Error", "Las fechas son inválidas o falta calcular el total.")
            return
        # DPI exactamente 13 dígitos
        if not re.fullmatch(r"\d{13}", dpi):
            messagebox.showerror("Error", "El DPI debe tener exactamente 13 dígitos.")
            return
        # NIT opcional: si viene, dígitos 7–12 (ajusta si tu regla es distinta)
        if nit and not re.fullmatch(r"\d{7,12}", nit):
            messagebox.showerror("Error", "El NIT debe contener solo dígitos (7–12).")
            return
        if not primer_nombre or not primer_apellido:
            messagebox.showerror("Error", "Debe ingresar al menos primer nombre y primer apellido.")
            return
        if not numero_habitacion:
            messagebox.showerror("Error", "Debe seleccionar un número de habitación.")
            return

        # Normaliza derivados
        try:
            precio_total = float(precio_total_str)
        except ValueError:
            messagebox.showerror("Error", "El total debe ser un número válido.")
            return

        try:
            noches = Hotel.calcular_noches(fecha_ingreso, fecha_salida)
            if noches is None or noches <= 0:
                messagebox.showerror("Error", "Las fechas deben producir al menos 1 noche válida.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular noches: {e}")
            return

        # Payload completo para Hotel.crear_reserva (ajusta claves si tu Hotel.py usa otras)
        datos = {
            "numero_habitacion": numero_habitacion,
            "tipo_habitacion": tipo,
            "fecha_ingreso": fecha_ingreso,
            "fecha_salida": fecha_salida,
            "noches": noches,
            "precio_total": precio_total,
            "dpi": dpi,
            "nit": nit or None,
            "primer_nombre": primer_nombre,
            "segundo_nombre": segundo_nombre,
            "primer_apellido": primer_apellido,
            "segundo_apellido": segundo_apellido,
            # "estado": self.combo_estado.get() or "Disponible",  # si tu capa de negocio lo requiere
            # "id_huesped": None,  # TODO: integrar cuando exista gestión de huéspedes
        }

        try:
            exito, mensaje = Hotel.crear_reserva(datos)
        except Exception as e:
            messagebox.showerror("Error al crear reserva", f"{e}")
            return

        if exito:
            resumen = (
                f"Reserva creada con éxito:\n\n"
                f"Habitación: {numero_habitacion}\n"
                f"Tipo: {tipo}\n"
                f"Fecha ingreso: {fecha_ingreso}\n"
                f"Fecha salida: {fecha_salida}\n"
                f"Huésped: {primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}\n"
                f"DPI: {dpi}\n"
                f"NIT: {nit or '—'}\n"
                f"Noches: {noches}\n"
                f"Total: Q{precio_total:.2f}"
            )
            messagebox.showinfo("Reserva Exitosa", resumen)
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje)


# Ejecución independiente de pruebas (no se ejecuta al importar)
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    VentanaReservaciones(root)
    root.mainloop()
