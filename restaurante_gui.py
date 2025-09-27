# restaurante_gui.py

"""
Capa de GUI del módulo Restaurante para Mayan Sunset.
La ventana está encapsulada en la función VentanaRestaurante(root: tk.Toplevel).
Interactúa únicamente con la capa de lógica del negocio.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

from restaurante_logica import RestauranteLogica, ItemPedido


def VentanaRestaurante(root: tk.Toplevel) -> None:
    """
    Construye la ventana secundaria del módulo Restaurante dentro de root (tk.Toplevel).
    No crea Tk() ni mainloop; se integra como subventana del proyecto principal.
    """
    root.title("Mayan Sunset - Restaurante")
    root.geometry("900x600")
    root.resizable(True, True)

    logica = RestauranteLogica()
    # Asegurar esquema y datos iniciales (idempotente)
    try:
        logica.inicializar_esquema_y_datos()
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", str(e), parent=root)
        return

    # --- Estado interno ---
    carrito: List[Dict] = []  # [{id_plato, nombre_plato, cantidad, precio_unitario}]
    subtotal_var = tk.StringVar(value="0.00")
    servicio_var = tk.StringVar(value="0.00")
    total_var = tk.StringVar(value="0.00")

    # --- Callbacks ---

    def cargar_menu_tabla() -> None:
        """Recarga el menú en la tabla según filtro seleccionado."""
        for item in tree_menu.get_children():
            tree_menu.delete(item)

        tipo_sel = combo_tipo.get()
        tipo_aplicar = tipo_sel if tipo_sel and tipo_sel != "Todos" else None
        try:
            menu = logica.listar_menu_por_tipo(tipo_aplicar)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el menú:\n{e}", parent=root)
            return

        for m in menu:
            tree_menu.insert(
                "",
                tk.END,
                iid=f"plato-{m['id_plato']}",
                values=(m["id_plato"], m["nombre_plato"], m["descripcion"], f"{m['precio']:.2f}", m["tipo"]),
            )

    def actualizar_totales_visual() -> None:
        """Actualiza subtotal, servicio y total en la UI."""
        try:
            subtotal = sum(ci["precio_unitario"] * ci["cantidad"] for ci in carrito)
            servicio = round(subtotal * logica.CARGO_SERVICIO_PORCENTAJE, 2)
            total = round(subtotal + servicio, 2)

            subtotal_var.set(f"{subtotal:.2f}")
            servicio_var.set(f"{servicio:.2f}")
            total_var.set(f"{total:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular totales:\n{e}", parent=root)

    def agregar_al_carrito() -> None:
        """Agrega el plato seleccionado con la cantidad indicada."""
        try:
            sel = tree_menu.selection()
            if not sel:
                messagebox.showwarning("Selección requerida", "Seleccione un plato del menú.", parent=root)
                return

            id_plato = int(tree_menu.item(sel[0], "values")[0])
            nombre = tree_menu.item(sel[0], "values")[1]
            precio_unitario = float(tree_menu.item(sel[0], "values")[3])

            cantidad_txt = entry_cantidad.get().strip()
            if not cantidad_txt.isdigit() or int(cantidad_txt) <= 0:
                messagebox.showwarning("Cantidad inválida", "Ingrese una cantidad entera mayor a cero.", parent=root)
                return
            cantidad = int(cantidad_txt)

            # Si el plato ya está en el carrito, acumular cantidad
            for ci in carrito:
                if ci["id_plato"] == id_plato:
                    ci["cantidad"] += cantidad
                    break
            else:
                carrito.append(
                    {"id_plato": id_plato, "nombre_plato": nombre, "cantidad": cantidad, "precio_unitario": precio_unitario}
                )

            # actualizar tabla carrito
            recargar_carrito()
            actualizar_totales_visual()
            entry_cantidad.delete(0, tk.END)
            entry_cantidad.insert(0, "1")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar al carrito:\n{e}", parent=root)

    def recargar_carrito() -> None:
        """Recarga la tabla del carrito."""
        for item in tree_carrito.get_children():
            tree_carrito.delete(item)

        for idx, ci in enumerate(carrito, start=1):
            tree_carrito.insert(
                "",
                tk.END,
                iid=f"car-{ci['id_plato']}",
                values=(idx, ci["nombre_plato"], ci["cantidad"], f"{ci['precio_unitario']:.2f}",
                        f"{ci['cantidad'] * ci['precio_unitario']:.2f}"),
            )

    def quitar_del_carrito() -> None:
        """Quita el plato seleccionado del carrito."""
        sel = tree_carrito.selection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Seleccione un item del carrito.", parent=root)
            return
        iid = sel[0]
        nombre_sel = tree_carrito.item(iid, "values")[1]
        # Remover por nombre
        for i, ci in enumerate(carrito):
            if ci["nombre_plato"] == nombre_sel:
                carrito.pop(i)
                break
        recargar_carrito()
        actualizar_totales_visual()

    def procesar_pedido() -> None:
        """Envía el pedido a la lógica, actualiza inventario, registra transacción."""
        try:
            if not carrito:
                messagebox.showwarning("Carrito vacío", "Agregue al menos un plato.", parent=root)
                return

            habit_txt = entry_habitacion.get().strip()
            if not habit_txt.isdigit() or int(habit_txt) <= 0:
                messagebox.showwarning("Habitación inválida", "Ingrese un número de habitación válido.", parent=root)
                return
            id_habitacion = int(habit_txt)

            metodo_pago = combo_pago.get().strip() or None

            items = [ItemPedido(id_plato=ci["id_plato"], cantidad=ci["cantidad"]) for ci in carrito]
            resumen = logica.procesar_pedido(id_habitacion=id_habitacion, items=items, metodo_pago=metodo_pago)

            # Mostrar resumen
            msg = (
                f"Pedido #{resumen['id_pedido']} procesado.\n"
                f"Subtotal: Q{resumen['subtotal']:.2f}\n"
                f"Servicio (10%): Q{resumen['cargo_servicio']:.2f}\n"
                f"Total: Q{resumen['total']:.2f}\n"
            )

            if resumen["advertencias"]:
                msg += "\nAdvertencias:\n- " + "\n- ".join(resumen["advertencias"])

            messagebox.showinfo("Éxito", msg, parent=root)

            # Reset de carrito
            carrito.clear()
            recargar_carrito()
            actualizar_totales_visual()

            # Recargar inventario tab
            cargar_inventario_tabla()

        except Exception as e:
            messagebox.showerror("Error al procesar pedido", str(e), parent=root)

    def cargar_inventario_tabla() -> None:
        """Recarga la tabla de inventario y muestra alertas de bajo stock."""
        for item in tree_inv.get_children():
            tree_inv.delete(item)

        try:
            inv = logica.listar_inventario()
            for r in inv:
                tree_inv.insert(
                    "",
                    tk.END,
                    iid=f"ing-{r['id_ingrediente']}",
                    values=(r["nombre_ingrediente"], r["cantidad"], r["unidad_medida"], r["stock_minimo"]),
                )

            # Alertas
            advertencias = logica.verificar_bajo_stock()
            if advertencias:
                messagebox.showwarning("Inventario - Bajo stock", "\n".join(advertencias), parent=root)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar inventario:\n{e}", parent=root)

    # --- Layout principal: Notebook con dos pestañas ---

    notebook = ttk.Notebook(root)
    frame_pedidos = ttk.Frame(notebook)
    frame_inventario = ttk.Frame(notebook)
    notebook.add(frame_pedidos, text="Pedidos")
    notebook.add(frame_inventario, text="Inventario")
    notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # --- Pestaña Pedidos ---

    # Filtro de tipo
    ttk.Label(frame_pedidos, text="Tipo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    combo_tipo = ttk.Combobox(frame_pedidos, values=["Todos", "Entrada", "Principal", "Bebida"], state="readonly")
    combo_tipo.current(0)
    combo_tipo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    ttk.Button(frame_pedidos, text="Cargar menú", command=cargar_menu_tabla).grid(row=0, column=2, padx=5, pady=5)

    # Tabla de menú
    columns_menu = ("ID", "Nombre", "Descripción", "Precio", "Tipo")
    tree_menu = ttk.Treeview(frame_pedidos, columns=columns_menu, show="headings", height=10)
    for col in columns_menu:
        tree_menu.heading(col, text=col)
        tree_menu.column(col, width=150 if col != "Descripción" else 300, stretch=True)
    tree_menu.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

    # Scrollbars
    scroll_y = ttk.Scrollbar(frame_pedidos, orient="vertical", command=tree_menu.yview)
    tree_menu.configure(yscrollcommand=scroll_y.set)
    scroll_y.grid(row=1, column=4, sticky="ns")

    # Cantidad y agregar
    ttk.Label(frame_pedidos, text="Cantidad:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_cantidad = ttk.Entry(frame_pedidos, width=10)
    entry_cantidad.insert(0, "1")
    entry_cantidad.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    ttk.Button(frame_pedidos, text="Agregar al carrito", command=agregar_al_carrito).grid(row=2, column=2, padx=5, pady=5)

    # Carrito
    ttk.Label(frame_pedidos, text="Carrito:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    columns_car = ("#", "Plato", "Cantidad", "Precio Unitario", "Total")
    tree_carrito = ttk.Treeview(frame_pedidos, columns=columns_car, show="headings", height=8)
    for col in columns_car:
        tree_carrito.heading(col, text=col)
        tree_carrito.column(col, width=120 if col != "Plato" else 250, stretch=True)
    tree_carrito.grid(row=4, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

    ttk.Button(frame_pedidos, text="Quitar del carrito", command=quitar_del_carrito).grid(row=5, column=0, padx=5, pady=5)

    # Totales
    ttk.Label(frame_pedidos, text="Subtotal: Q").grid(row=6, column=0, sticky="e", padx=5, pady=2)
    ttk.Label(frame_pedidos, textvariable=subtotal_var).grid(row=6, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(frame_pedidos, text="Servicio (10%): Q").grid(row=7, column=0, sticky="e", padx=5, pady=2)
    ttk.Label(frame_pedidos, textvariable=servicio_var).grid(row=7, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(frame_pedidos, text="Total: Q").grid(row=8, column=0, sticky="e", padx=5, pady=2)
    ttk.Label(frame_pedidos, textvariable=total_var).grid(row=8, column=1, sticky="w", padx=5, pady=2)

    # Datos del pedido
    ttk.Label(frame_pedidos, text="Habitación:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
    entry_habitacion = ttk.Entry(frame_pedidos, width=10)
    entry_habitacion.grid(row=9, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(frame_pedidos, text="Método de pago:").grid(row=9, column=2, sticky="e", padx=5, pady=5)
    combo_pago = ttk.Combobox(frame_pedidos, values=["Efectivo", "Tarjeta", "Cargo a habitación"], state="readonly")
    combo_pago.grid(row=9, column=3, sticky="w", padx=5, pady=5)

    ttk.Button(frame_pedidos, text="Procesar pedido", command=procesar_pedido).grid(row=10, column=0, columnspan=2, padx=5, pady=10)

    # Configurar pesos del grid
    for r in range(11):
        frame_pedidos.grid_rowconfigure(r, weight=0)
    frame_pedidos.grid_rowconfigure(1, weight=1)
    frame_pedidos.grid_rowconfigure(4, weight=1)
    for c in range(4):
        frame_pedidos.grid_columnconfigure(c, weight=1)

    # --- Pestaña Inventario ---

    ttk.Button(frame_inventario, text="Recargar inventario", command=cargar_inventario_tabla).grid(row=0, column=0, padx=5, pady=5)

    columns_inv = ("Ingrediente", "Cantidad", "Unidad", "Mínimo")
    tree_inv = ttk.Treeview(frame_inventario, columns=columns_inv, show="headings", height=18)
    for col in columns_inv:
        tree_inv.heading(col, text=col)
        tree_inv.column(col, width=180, stretch=True)
    tree_inv.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

    scroll_inv_y = ttk.Scrollbar(frame_inventario, orient="vertical", command=tree_inv.yview)
    tree_inv.configure(yscrollcommand=scroll_inv_y.set)
    scroll_inv_y.grid(row=1, column=3, sticky="ns")

    frame_inventario.grid_rowconfigure(1, weight=1)
    for c in range(3):
        frame_inventario.grid_columnconfigure(c, weight=1)

    # Inicialización de tablas al abrir
    cargar_menu_tabla()
    cargar_inventario_tabla()
