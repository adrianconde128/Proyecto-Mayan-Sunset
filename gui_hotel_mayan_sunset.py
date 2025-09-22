from pathlib import Path

import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, StringVar
from tkinter import ttk
from Hotel import crear_reserva, calcular_precio_total

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\Usua\OneDrive\Desktop\Proyecto Mayan Sunset\gui_mayan_sunset\build\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1200x1000")
window.configure(bg = "#FFFFFF")

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 1000,
    width = 1200,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
canvas.create_rectangle(
    600.0,
    0.0,
    1200.0,
    1000.0,
    fill="#5D8D5A",
    outline="")

#Scrollbar para desplazarse verticalmente
# Crea un Frame que contendrá todos tus widgets del formulario.
# Este Frame se colocará DENTRO del Canvas.
form_frame = tk.Frame(canvas, bg="#5D8D5A", width=600, height=1000)

# Coloca el form_frame en el Canvas en las coordenadas (0, 0)
# y guarda el ID de la ventana que se crea en el Canvas.
canvas_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")

# Configura el scrollbar para el Canvas
scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

# Esta función se ejecutará cada vez que el form_frame cambie de tamaño
def on_frame_configure(event):
    # Ajusta el área de desplazamiento del Canvas para que coincida con el tamaño del form_frame
    canvas.configure(scrollregion=canvas.bbox("all"))

# Vincula el evento de cambio de tamaño del form_frame a la función on_frame_configure
form_frame.bind("<Configure>", on_frame_configure)


#ELEMENTOS DEL FORMULARIO
entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    1044.5,
    709.5,
    image=entry_image_1
)
entry_1 = Entry(
    form_frame,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0,
    state="readonly" # Solo lectura
)
entry_1.place(
    x=932.0,
    y=692.0,
    width=225.0,
    height=33.0
)

canvas.create_text(
    922.0,
    660.0,
    anchor="nw",
    text="Precio Total",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

canvas.create_text(
    632.0,
    660.0,
    anchor="nw",
    text="Tipo de Habitación",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    754.5,
    709.5,
    image=entry_image_2
)
entry_2 = Entry(
    form_frame,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(
    x=642.0,
    y=692.0,
    width=225.0,
    height=33.0
)

canvas.create_text(
    632.0,
    755.0,
    anchor="nw",
    text="ID Habitación",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    754.5,
    804.5,
    image=entry_image_3
)
entry_3 = Entry(
    form_frame,
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_3.place(
    x=642.0,
    y=787.0,
    width=225.0,
    height=33.0
)

canvas.create_text(
    922.0,
    755.0,
    anchor="nw",
    text="Estado",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

# Combobox para el estado de la habitación
estado_habitacion_var = StringVar()
estado_combobox = ttk.Combobox(
    form_frame,
    textvariable=estado_habitacion_var,
    state="readonly", # Bloqueado para solo lectura
    values=["Disponible", "Ocupada", "Mantenimiento"]
)
estado_combobox.place(
    x=932.0,
    y=787.0,
    width=225.0,
    height=33.0
)
estado_combobox.set("Disponible") # Valor inicial

entry_image_5 = PhotoImage(
    file=relative_to_assets("entry_5.png"))
entry_bg_5 = canvas.create_image(
    1044.5,
    614.5,
    image=entry_image_5
)
entry_5 = Entry(
    form_frame,
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

canvas.create_text(
    632.0,
    540.0,
    anchor="nw",
    text="Fecha de Ingreso\nAAAA-MM-DD",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

canvas.create_text(
    632.0,
    496.0,
    anchor="nw",
    text="Datos de la Estadía",
    fill="#FFFFFF",
    font=("Lato Bold", 20 * -1)
)

canvas.create_text(
    922.0,
    540.0,
    anchor="nw",
    text="Fecha de Salida\nAAAA-MM-DD",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

entry_image_6 = PhotoImage(
    file=relative_to_assets("entry_6.png"))
entry_bg_6 = canvas.create_image(
    754.5,
    614.5,
    image=entry_image_6
)
entry_6 = Entry(
    form_frame,
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

entry_image_7 = PhotoImage(
    file=relative_to_assets("entry_7.png"))
entry_bg_7 = canvas.create_image(
    1044.5,
    439.5,
    image=entry_image_7
)
entry_7 = Entry(
    form_frame,
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

canvas.create_text(
    922.0,
    382.0,
    anchor="nw",
    text="NIT",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

canvas.create_text(
    632.0,
    382.0,
    anchor="nw",
    text="DPI",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

entry_image_8 = PhotoImage(
    file=relative_to_assets("entry_8.png"))
entry_bg_8 = canvas.create_image(
    754.5,
    439.5,
    image=entry_image_8
)
entry_8 = Entry(
    form_frame,
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

entry_image_9 = PhotoImage(
    file=relative_to_assets("entry_9.png"))
entry_bg_9 = canvas.create_image(
    1044.5,
    329.5,
    image=entry_image_9
)
entry_9 = Entry(
    form_frame,
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

canvas.create_text(
    922.0,
    268.0,
    anchor="nw",
    text="2do Apellido",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

canvas.create_text(
    632.0,
    268.0,
    anchor="nw",
    text="1er Apellido",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

entry_image_10 = PhotoImage(
    file=relative_to_assets("entry_10.png"))
entry_bg_10 = canvas.create_image(
    754.5,
    329.5,
    image=entry_image_10
)
entry_10 = Entry(
    form_frame,
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

entry_image_11 = PhotoImage(
    file=relative_to_assets("entry_11.png"))
entry_bg_11 = canvas.create_image(
    1044.5,
    219.5,
    image=entry_image_11
)
entry_11 = Entry(
    form_frame,
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

canvas.create_text(
    922.0,
    162.0,
    anchor="nw",
    text="2do Nombre",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

canvas.create_text(
    632.0,
    162.0,
    anchor="nw",
    text="1er Nombre",
    fill="#FFFFFF",
    font=("Lato Regular", 20 * -1)
)

canvas.create_text(
    632.0,
    113.0,
    anchor="nw",
    text="Datos del Huésped",
    fill="#FFFFFF",
    font=("Lato Bold", 20 * -1)
)

canvas.create_text(
    710.0,
    31.0,
    anchor="nw",
    text="Creación de Reservas",
    fill="#FFFFFF",
    font=("Lato Bold", 40 * -1)
)

entry_image_12 = PhotoImage(
    file=relative_to_assets("entry_12.png"))
entry_bg_12 = canvas.create_image(
    754.5,
    219.5,
    image=entry_image_12
)
entry_12 = Entry(
    form_frame,
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

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    300.0,
    500.0,
    image=image_image_1
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))

def crear_reserva_click():
    """ Recopila los datos y llama a la función de backend. """
    data = {
        'primer_nombre': entry_12.get(),
        'segundo_nombre': entry_11.get(),
        'primer_apellido': entry_10.get(),
        'segundo_apellido': entry_9.get(),
        'dpi': entry_8.get(),
        'nit': entry_7.get(),
        'fecha_ingreso': entry_6.get(),
        'fecha_salida': entry_5.get(),
        'tipo_habitacion': entry_2.get(),
        'id_habitacion': entry_3.get(),
        'estado': estado_combobox.get(),
        'precio_total': entry_1.get()
    }

    if crear_reserva(data):
        print("Reserva creada con éxito.")
    else:
        print("Error al crear la reserva.")

# Botón para crear reserva
button_1 = Button(
    form_frame,
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=crear_reserva_click, #Llama a la función al hacer clic
    relief="flat"
)

button_1.place(
    x=660.0,
    y=882.0,
    width=180.0,
    height=60.0
)

button_image_hover_1 = PhotoImage(
    file=relative_to_assets("button_hover_1.png"))

def button_1_hover(e):
    button_1.config(
        image=button_image_hover_1
    )
def button_1_leave(e):
    button_1.config(
        image=button_image_1
    )

button_1.bind('<Enter>', button_1_hover)
button_1.bind('<Leave>', button_1_leave)


button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))

button_2 = Button(
    form_frame,
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

button_image_hover_2 = PhotoImage(
    file=relative_to_assets("button_hover_2.png"))

def button_2_hover(e):
    button_2.config(
        image=button_image_hover_2
    )
def button_2_leave(e):
    button_2.config(
        image=button_image_2
    )

button_2.bind('<Enter>', button_2_hover)
button_2.bind('<Leave>', button_2_leave)

window.resizable(True, True)
window.mainloop()
