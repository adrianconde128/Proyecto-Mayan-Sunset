import Hotel  # Capa de negocio (valida, calcula y orquesta llamadas a hotel_db)
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, messagebox, ttk, StringVar
import re
from datetime import datetime
from hotel_db import listar_numeros_habitacion, get_connection as get_conn

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\Usua\OneDrive\Desktop\Proyecto Mayan Sunset\gui_mayan_sunset\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

#Inicializar base de datos
Hotel.inicializar_sistema()

# =========================
# Validaciones de entrada
# =========================

# Solo dígitos
def validar_numerico(char):
    return char.isdigit()

# Solo letras y espacios
def validar_texto(char):
    return char.isalpha() or char.isspace()

# Solo dígitos y guion (para fechas)
def validar_fecha_caracter(char):
    return char.isdigit() or char == "-"

# Validación de formato completo de fecha (YYYY-MM-DD)
def validar_formato_fecha(entry_widget):
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
# Ventana principal
# =========================
window = Tk()
window.title("Mayan Sunset - Creación de Reservas")
window.geometry("1200x1000")
window.configure(bg="#FFFFFF")
window.resizable(True, True)  # Ajustable

# =========================
# Configuración de validaciones
# =========================

# Registrar validadores en la ventana principal
vcmd_num = window.register(validar_numerico)
vcmd_texto = window.register(validar_texto)
vcmd_fecha = window.register(validar_fecha_caracter)


# =========================
# Scrollbar + Canvas contenedor
# =========================
scroll_canvas = Canvas(window, bg="#FFFFFF", highlightthickness=0)
scroll_canvas.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(window, orient="vertical", command=scroll_canvas.yview)
scrollbar.pack(side="right", fill="y")

scroll_canvas.configure(yscrollcommand=scrollbar.set)

# Canvas original (de Figma) dentro del canvas con scroll
inner_canvas = Canvas(
    scroll_canvas,
    bg="#FFFFFF",
    height=1000,
    width=1200,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
scroll_canvas.create_window((0, 0), window=inner_canvas, anchor="nw")

# Mantener referencias de imágenes para evitar GC
entry_image_1 = None
entry_image_2 = None
entry_image_3 = None
entry_image_4 = None
entry_image_5 = None
entry_image_6 = None
entry_image_7 = None
entry_image_8 = None
entry_image_9 = None
entry_image_10 = None
entry_image_11 = None
entry_image_12 = None
image_image_1 = None
button_image_1 = None
button_image_hover_1 = None
button_image_2 = None
button_image_hover_2 = None

# =========================
# Contenido original adaptado (TODOS los elementos)
# =========================

# Panel derecho verde
inner_canvas.create_rectangle(
    600.0,
    0.0,
    1200.0,
    1000.0,
    fill="#5D8D5A",
    outline=""
)

# entry_1 -> Precio Total (readonly)
entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
entry_bg_1 = inner_canvas.create_image(
    1044.5,
    709.5,
    image=entry_image_1
)
entry_1 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0,
    state="readonly"  # Bloqueado
)
entry_1.place(
    x=932.0,
    y=692.0,
    width=225.0,
    height=33.0
)

# Label Precio Total
inner_canvas.create_text(
    922.0,
    660.0,
    anchor="nw",
    text="Precio Total",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Label Tipo de Habitación
inner_canvas.create_text(
    632.0,
    660.0,
    anchor="nw",
    text="Tipo de Habitación",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# entry_2 -> Tipo de Habitación (Combobox)
entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
entry_bg_2 = inner_canvas.create_image(
    754.5,
    709.5,
    image=entry_image_2
)
combo_tipo_habitacion = ttk.Combobox(
    inner_canvas,
    values=[],  # Se llenará desde Hotel.py
    state="readonly",
)

# Variable interna para almacenar el precio por noche actual
precio_noche_actual = None

def cargar_tipos_habitacion():
    global precio_noche_actual
    tipos = Hotel.obtener_tipos_habitacion()
    combo_tipo_habitacion["values"] = tipos
    if tipos:
        combo_tipo_habitacion.current(0)
        # Inicializa el precio_noche_actual con el primer tipo
        precio_noche_actual = Hotel.obtener_precio_por_tipo(tipos[0])
        calcular_total()

def actualizar_precio_noche(event=None):
    global precio_noche_actual
    tipo = combo_tipo_habitacion.get()
    if not tipo:
        return
    precio_noche_actual = Hotel.obtener_precio_por_tipo(tipo)
    calcular_total()

def calcular_total(event=None):
    global precio_noche_actual
    fecha_ingreso = entry_6.get()   # Fecha de ingreso
    fecha_salida = entry_5.get()    # Fecha de salida
    noches = Hotel.calcular_noches(fecha_ingreso, fecha_salida)

    entry_1.config(state="normal")  # entry_1 = Precio Total
    entry_1.delete(0, "end")

    if noches is None:
        entry_1.insert(0, "Fechas inválidas")
        entry_1.config(state="readonly")
        return

    if precio_noche_actual is None:
        # Si aún no se ha definido, intenta obtenerlo del tipo actual
        tipo = combo_tipo_habitacion.get()
        if tipo:
            precio_noche_actual = Hotel.obtener_precio_por_tipo(tipo)

    if precio_noche_actual is None:
        entry_1.insert(0, "")
    else:
        total = noches * precio_noche_actual
        entry_1.insert(0, f"{total:.2f}")

    entry_1.config(state="readonly")

combo_tipo_habitacion.place(
    x=642.0,
    y=692.0,
    width=225.0,
    height=33.0
)

# Label Número de Habitación
inner_canvas.create_text(
    632.0,
    755.0,
    anchor="nw",
    text="Número de Habitación",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Combobox -> Número de Habitación
entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
entry_bg_3 = inner_canvas.create_image(
    754.5,
    804.5,
    image=entry_image_3
)

numero_hab_var = StringVar()
combo_numero_hab = ttk.Combobox(
    inner_canvas,
    textvariable=numero_hab_var,
    values=[],  # se llenará desde DB
    state="readonly"
)
combo_numero_hab.place(
    x=642.0,
    y=787.0,
    width=225.0,
    height=33.0
)

def cargar_numeros_habitacion():
    with get_conn() as conn:
        combo_numero_hab["values"] = listar_numeros_habitacion(conn)
    if combo_numero_hab["values"]:
        combo_numero_hab.current(0)

# Llamar al cargar números al inicio
cargar_numeros_habitacion()

# Label Estado
inner_canvas.create_text(
    922.0,
    755.0,
    anchor="nw",
    text="Estado",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# entry_4 -> Estado (Combobox)
entry_image_4 = PhotoImage(file=relative_to_assets("entry_4.png"))
entry_bg_4 = inner_canvas.create_image(
    1044.5,
    804.5,
    image=entry_image_4
)
combo_estado = ttk.Combobox(
    inner_canvas,
    values=["Disponible", "Ocupada", "Mantenimiento"],
    state="readonly"
)
combo_estado.place(
    x=932.0,
    y=787.0,
    width=225.0,
    height=33.0
)

# entry_5 -> Fecha de Salida
entry_image_5 = PhotoImage(file=relative_to_assets("entry_5.png"))
entry_bg_5 = inner_canvas.create_image(
    1044.5,
    614.5,
    image=entry_image_5
)
entry_5 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_5.place(
    x=932.0,
    y=597.0,
    width=225.0,
    height=33.0
)

entry_5.config(
    validate="key",
    validatecommand=(vcmd_fecha, "%S")
)   # Validación de restricción de campo Fecha salida

# Label Fecha de Ingreso
inner_canvas.create_text(
    632.0,
    540.0,
    anchor="nw",
    text="Fecha de Ingreso\nAAAA-MM-DD",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Label Datos de la Estadía (sección)
inner_canvas.create_text(
    632.0,
    496.0,
    anchor="nw",
    text="Datos de la Estadía",
    fill="#FFFFFF",
    font=("Lato Bold", 20 * -1)
)

# Label Fecha de Salida
inner_canvas.create_text(
    922.0,
    540.0,
    anchor="nw",
    text="Fecha de Salida\nAAAA-MM-DD",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# entry_6 -> Fecha de Ingreso
entry_image_6 = PhotoImage(file=relative_to_assets("entry_6.png"))
entry_bg_6 = inner_canvas.create_image(
    754.5,
    614.5,
    image=entry_image_6
)
entry_6 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_6.place(
    x=642.0,
    y=597.0,
    width=225.0,
    height=33.0
)

entry_6.config(
    validate="key",
    validatecommand=(vcmd_fecha, "%S")
)   # Validación de restricción de campo Fecha ingreso

# entry_7 -> NIT
entry_image_7 = PhotoImage(file=relative_to_assets("entry_7.png"))
entry_bg_7 = inner_canvas.create_image(
    1044.5,
    439.5,
    image=entry_image_7
)
entry_7 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_7.place(
    x=932.0,
    y=422.0,
    width=225.0,
    height=33.0
)

entry_7.config(
    validate="key",
    validatecommand=(vcmd_num, "%S")
)   # Validación de restricción del campo NIT

# Label NIT
inner_canvas.create_text(
    922.0,
    382.0,
    anchor="nw",
    text="NIT",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Label DPI
inner_canvas.create_text(
    632.0,
    382.0,
    anchor="nw",
    text="DPI",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# entry_8 -> DPI
entry_image_8 = PhotoImage(file=relative_to_assets("entry_8.png"))
entry_bg_8 = inner_canvas.create_image(
    754.5,
    439.5,
    image=entry_image_8
)
entry_8 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_8.place(
    x=642.0,
    y=422.0,
    width=225.0,
    height=33.0
)

entry_8.config(
    validate="key",
    validatecommand=(vcmd_num, "%S")
)   # Validación de restricción de campo de DPI

# entry_9 -> 2do Apellido
entry_image_9 = PhotoImage(file=relative_to_assets("entry_9.png"))
entry_bg_9 = inner_canvas.create_image(
    1044.5,
    329.5,
    image=entry_image_9
)
entry_9 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_9.place(
    x=932.0,
    y=312.0,
    width=225.0,
    height=33.0
)

entry_9.config(
    validate="key",
    validatecommand=(vcmd_texto, "%S")
)   # Validación de restricción de campo Segundo apellido

# Label 2do Apellido
inner_canvas.create_text(
    922.0,
    268.0,
    anchor="nw",
    text="2do Apellido",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Label 1er Apellido
inner_canvas.create_text(
    632.0,
    268.0,
    anchor="nw",
    text="1er Apellido",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# entry_10 -> 1er Apellido
entry_image_10 = PhotoImage(file=relative_to_assets("entry_10.png"))
entry_bg_10 = inner_canvas.create_image(
    754.5,
    329.5,
    image=entry_image_10
)
entry_10 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_10.place(
    x=642.0,
    y=312.0,
    width=225.0,
    height=33.0
)

entry_10.config(
    validate="key",
    validatecommand=(vcmd_texto, "%S")
)  # Validación de restricción de campo Primer apellido

# entry_11 -> 2do Nombre
entry_image_11 = PhotoImage(file=relative_to_assets("entry_11.png"))
entry_bg_11 = inner_canvas.create_image(
    1044.5,
    219.5,
    image=entry_image_11
)
entry_11 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_11.place(
    x=932.0,
    y=202.0,
    width=225.0,
    height=33.0
)

entry_11.config(
    validate="key",
    validatecommand=(vcmd_texto, "%S")
)  # Validación de restricción de campo de Segundo nombre


# Label 2do Nombre
inner_canvas.create_text(
    922.0,
    162.0,
    anchor="nw",
    text="2do Nombre",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Label 1er Nombre
inner_canvas.create_text(
    632.0,
    162.0,
    anchor="nw",
    text="1er Nombre",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Label Datos del Huésped (sección)
inner_canvas.create_text(
    632.0,
    113.0,
    anchor="nw",
    text="Datos del Huésped",
    fill="#FFFFFF",
    font=("Lato Bold", 20 * -1)
)

# Título Creación de Reservas
inner_canvas.create_text(
    710.0,
    31.0,
    anchor="nw",
    text="Creación de Reservas",
    fill="#FFFFFF",
    font=("Lato Bold", 40 * -1)
)

# entry_12 -> 1er Nombre
entry_image_12 = PhotoImage(file=relative_to_assets("entry_12.png"))
entry_bg_12 = inner_canvas.create_image(
    754.5,
    219.5,
    image=entry_image_12
)
entry_12 = Entry(
    inner_canvas,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_12.place(
    x=642.0,
    y=202.0,
    width=225.0,
    height=33.0
)

entry_12.config(
    validate="key",
    validatecommand=(vcmd_texto, "%S")
)  # Validación de restricción del campo de Primer nombre

# Imagen decorativa izquierda
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
image_1 = inner_canvas.create_image(
    300.0,
    500.0,
    image=image_image_1
)

combo_tipo_habitacion.bind("<<ComboboxSelected>>", actualizar_precio_noche)
entry_6.bind("<FocusOut>", calcular_total)  # Fecha ingreso
entry_5.bind("<FocusOut>", calcular_total)  # Fecha salida

# Inicializar combobox con datos desde Hotel.py
Hotel.inicializar_sistema()
cargar_tipos_habitacion()

# =========================
# Validación final en guardar_reserva
# =========================

def guardar_reserva():
    numero_habitacion = combo_numero_hab.get().strip()
    tipo = combo_tipo_habitacion.get().strip()
    fecha_ingreso = entry_6.get().strip()
    fecha_salida = entry_5.get().strip()
    dpi = entry_8.get().strip()
    nit = entry_7.get().strip()
    primer_nombre = entry_12.get().strip()
    segundo_nombre = entry_11.get().strip()
    primer_apellido = entry_10.get().strip()
    segundo_apellido = entry_9.get().strip()
    precio_total = entry_1.get().strip()

    # Validaciones básicas
    if not tipo:
        messagebox.showerror("Error", "Debe seleccionar un tipo de habitación.")
        return
    if not validar_formato_fecha(entry_6) or not validar_formato_fecha(entry_5):
        messagebox.showerror("Error", "Las fechas deben estar en formato YYYY-MM-DD válido.")
        return
    if "inválidas" in precio_total.lower() or not precio_total:
        messagebox.showerror("Error", "Las fechas son inválidas o falta calcular el total.")
        return
    if not dpi or len(dpi) < 8:
        messagebox.showerror("Error", "Debe ingresar un DPI válido.")
        return
    if not primer_nombre or not primer_apellido:
        messagebox.showerror("Error", "Debe ingresar al menos primer nombre y primer apellido.")
        return

    # Preparar datos para la capa de negocio
    datos = {
        "id_huesped": 1,  # 🔹 Ajustar cuando tengas gestión de huéspedes
        "numero_habitacion": numero_habitacion,  # Usar número de habitación,
        "tipo": tipo,
        "fecha_ingreso": fecha_ingreso,
        "fecha_salida": fecha_salida
    }

    exito, mensaje = Hotel.crear_reserva(datos)

    if exito:
        resumen = (
            f"Reserva creada con éxito:\n\n"
            f"Habitación ID: {numero_habitacion}\n"
            f"Tipo: {tipo}\n"
            f"Fecha ingreso: {fecha_ingreso}\n"
            f"Fecha salida: {fecha_salida}\n"
            f"Huésped: {primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}\n"
            f"DPI: {dpi}\n"
            f"NIT: {nit}\n"
            f"Total: Q{precio_total}"
        )
        messagebox.showinfo("Reserva Exitosa", resumen)
    else:
        messagebox.showerror("Error", mensaje)

# Botón 1 (Guardar)
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    inner_canvas,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.place(
    x=660.0,
    y=882.0,
    width=180.0,
    height=60.0
)

button_image_hover_1 = PhotoImage(file=relative_to_assets("button_hover_1.png"))

def button_1_hover(e):
    button_1.config(image=button_image_hover_1)

def button_1_leave(e):
    button_1.config(image=button_image_1)

button_1.bind('<Enter>', button_1_hover)
button_1.bind('<Leave>', button_1_leave)

button_1.config(command=guardar_reserva)

# Botón 2 (Cancelar)
button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(
    inner_canvas,
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    x=966.0,
    y=882.0,
    width=180.0,
    height=60.0
)

button_image_hover_2 = PhotoImage(file=relative_to_assets("button_hover_2.png"))

def button_2_hover(e):
    button_2.config(image=button_image_hover_2)

def button_2_leave(e):
    button_2.config(image=button_image_2)

button_2.bind('<Enter>', button_2_hover)
button_2.bind('<Leave>', button_2_leave)

# =========================
# Scrollregion dinámico
# =========================
def update_scrollregion(event=None):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

inner_canvas.bind("<Configure>", update_scrollregion)

# Opcional: scroll con rueda del mouse
def _on_mousewheel(event):
    # Windows/Mac usan delta, Linux suele usar Button-4/5
    scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

window.bind_all("<MouseWheel>", _on_mousewheel)

window.mainloop()