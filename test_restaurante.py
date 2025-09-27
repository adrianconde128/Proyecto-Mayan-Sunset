# -*- coding: utf-8 -*-
"""
Pruebas automatizadas básicas para el módulo Restaurante.
Se enfocan en la interacción entre la capa de lógica y persistencia,
sin necesidad de GUI.
"""

import unittest
import os
from restaurante_db import RestauranteDB
from restaurante_logica import RestauranteLogica, ItemPedido


class TestRestauranteModulo(unittest.TestCase):

    def setUp(self):
        """Configura una BD temporal en disco y la inicializa con datos."""
        self.test_db_path = "test_restaurante.db"
        # Elimina archivo previo si existe
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        self.db = RestauranteDB(self.test_db_path)
        self.logica = RestauranteLogica(self.db)
        # Crear tablas e insertar datos iniciales
        self.logica.inicializar_esquema_y_datos()

    def tearDown(self):
        """Cierra la conexión y elimina la BD temporal."""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_menu_inicial(self):
        """Verifica que el menú inicial tenga platos cargados."""
        menu = self.logica.listar_menu_por_tipo()
        self.assertGreater(len(menu), 0, "El menú inicial debería tener platos")

    def test_inventario_inicial(self):
        """Verifica que el inventario inicial tenga ingredientes cargados."""
        inv = self.logica.listar_inventario()
        self.assertGreater(len(inv), 0, "El inventario inicial debería tener ingredientes")

    def test_procesar_pedido_simple(self):
        """Procesa un pedido de un solo plato y valida totales e inventario."""
        menu = self.logica.listar_menu_por_tipo("Principal")
        plato = menu[0]

        items = [ItemPedido(id_plato=plato["id_plato"], cantidad=2)]
        resumen = self.logica.procesar_pedido(id_habitacion=101, items=items, metodo_pago="Efectivo")

        # Validar totales
        esperado_subtotal = plato["precio"] * 2
        esperado_total = round(esperado_subtotal * 1.10, 2)  # con 10% servicio
        self.assertAlmostEqual(resumen["subtotal"], esperado_subtotal, places=2)
        self.assertAlmostEqual(resumen["total"], esperado_total, places=2)

        # Validar que se haya generado un ID de pedido
        self.assertIn("id_pedido", resumen)
        self.assertGreater(resumen["id_pedido"], 0)

    def test_inventario_bajo_stock(self):
        """Fuerza consumo de inventario hasta generar alerta de bajo stock."""
        menu = self.logica.listar_menu_por_tipo()
        plato_guacamole = next(p for p in menu if "Guacamole" in p["nombre_plato"])

        # Consumir 45 unidades (queda 5, menor al mínimo de 10)
        items = [ItemPedido(id_plato=plato_guacamole["id_plato"], cantidad=45)]
        resumen = self.logica.procesar_pedido(id_habitacion=102, items=items, metodo_pago="Tarjeta")

        # Debe haber advertencias de bajo stock
        self.assertTrue(len(resumen["advertencias"]) > 0, "Debería haber advertencias de bajo stock")


if __name__ == "__main__":
    unittest.main()
