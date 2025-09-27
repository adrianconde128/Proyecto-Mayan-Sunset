# restaurante_logica.py
# -*- coding: utf-8 -*-
"""
Capa de Lógica del Negocio del módulo Restaurante para Mayan Sunset.
Coordina pedidos, inventario y facturación con un cargo por servicio del 10%.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from restaurante_db import RestauranteDB


@dataclass(frozen=True)
class ItemPedido:
    """
    Representa un item de pedido.
    - id_plato: ID del plato en la tabla 'menu'.
    - cantidad: Unidades solicitadas del plato.
    """
    id_plato: int
    cantidad: int


class RestauranteLogica:
    """
    Orquestador de la lógica del módulo Restaurante.
    Interactúa con la capa de persistencia y aplica reglas de negocio.
    """

    CARGO_SERVICIO_PORCENTAJE = 0.10  # 10%

    def __init__(self, db: Optional[RestauranteDB] = None) -> None:
        self.db = db or RestauranteDB()

        # Mapa de recetas: plato -> consumo de ingredientes por unidad
        # Nota: Este mapping es demostrativo para los platos iniciales.
        # Puede externalizarse a otra tabla en el futuro.
        self.recetas_por_plato: Dict[str, Dict[str, float]] = {
            "Tacos al Pastor": {"Carne de Cerdo": 0.20, "Piña": 0.10, "Cilantro": 0.05},  # kg / unidades
            "Enchiladas Suizas": {"Pollo": 0.25, "Maíz": 0.20, "Cilantro": 0.03},
            "Guacamole con Totopos": {"Aguacate": 1.00, "Maíz": 0.10, "Cilantro": 0.02},
            "Sopa de Tortilla": {"Maíz": 0.15, "Aguacate": 0.20, "Cilantro": 0.02},
            "Cochinita Pibil": {"Carne de Cerdo": 0.30, "Cilantro": 0.03},
            "Agua de Jamaica": {},  # sin ingredientes del inventario controlado
        }

    # --- Utilidades de tiempo ---

    @staticmethod
    def _fecha_hora_actual() -> Tuple[str, str]:
        ahora = datetime.now()
        return ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")

    @staticmethod
    def _fecha_actual() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    # --- Cálculo de totales ---

    def calcular_subtotal(self, items: List[ItemPedido]) -> float:
        """
        Calcula el subtotal sumando precio_unitario * cantidad de cada ítem.
        Obtiene precios desde la tabla 'menu'.
        """
        subtotal = 0.0
        with self.db as db:
            for item in items:
                plato = db.get_plato_por_id(item.id_plato)
                if not plato:
                    raise ValueError(f"Plato con id {item.id_plato} no existe.")
                precio = float(plato["precio"])
                subtotal += precio * item.cantidad
        return round(subtotal, 2)

    def calcular_total_con_servicio(self, subtotal: float) -> float:
        """Aplica cargo por servicio del 10%."""
        total = subtotal * (1.0 + self.CARGO_SERVICIO_PORCENTAJE)
        return round(total, 2)

    # --- Inventario ---

    def _consumir_inventario_por_plato(self, nombre_plato: str, cantidad_platos: int) -> List[str]:
        """
        Aplica consumo al inventario según la receta declarada.
        Retorna una lista de advertencias de bajo stock tras el consumo.
        """
        advertencias = []
        receta = self.recetas_por_plato.get(nombre_plato, {})
        if not receta:
            return advertencias  # plato sin ingredientes controlados

        with self.db as db:
            # Convertir consumos en unidades coherentes con inventario:
            # - Para 'kg', delta es negativo y en unidades decimales.
            # - Para 'unidades', delta negativo entero (redondeado).
            for ingrediente, consumo_por_unidad in receta.items():
                ing = db.get_ingrediente_por_nombre(ingrediente)
                if not ing:
                    # Si el ingrediente no existe, levantamos error para mantener integridad.
                    raise RuntimeError(f"Ingrediente requerido no encontrado: {ingrediente}")

                unidad = ing["unidad_medida"]
                consumo_total = consumo_por_unidad * cantidad_platos

                # Normalizar delta según unidad
                if unidad == "kg":
                    # Permitimos flotantes para kg.
                    delta = -consumo_total
                else:
                    # Para 'unidades', redondeamos al entero más cercano hacia arriba.
                    delta = -int(round(consumo_total))

                db.update_inventario_cantidad(ingrediente, delta)

            # Verificar bajo stock tras consumo
            bajos = db.get_bajo_stock()
            for b in bajos:
                advertencias.append(
                    f"Stock bajo: {b['nombre_ingrediente']} ({b['cantidad']} {b['unidad_medida']} < mínimo {b['stock_minimo']})"
                )
        return advertencias

    # --- Procesamiento de pedidos ---

    def procesar_pedido(
        self,
        id_habitacion: int,
        items: List[ItemPedido],
        metodo_pago: Optional[str] = None,
    ) -> Dict:
        """
        Crea el pedido, agrega detalles, actualiza inventario y registra la transacción.
        Retorna un resumen con total y posibles advertencias.
        """
        if not items:
            raise ValueError("El pedido no tiene ítems.")

        fecha, hora = self._fecha_hora_actual()

        with self.db as db:
            # Crear pedido en estado 'Pendiente'
            id_pedido = db.create_pedido(id_habitacion=id_habitacion, fecha=fecha, hora=hora, estado="Pendiente")

            # Agregar detalles y consumir inventario por cada ítem
            advertencias: List[str] = []
            subtotal = 0.0

            for item in items:
                plato = db.get_plato_por_id(item.id_plato)
                if not plato:
                    raise ValueError(f"Plato con id {item.id_plato} no existe.")

                precio_unitario = float(plato["precio"])
                subtotal += precio_unitario * item.cantidad

                db.add_detalle_pedido(
                    id_pedido=id_pedido,
                    id_plato=item.id_plato,
                    cantidad=item.cantidad,
                    precio_unitario=precio_unitario,
                )

                # Consumir inventario según receta
                advert = self._consumir_inventario_por_plato(plato["nombre_plato"], item.cantidad)
                advertencias.extend(advert)

            subtotal = round(subtotal, 2)
            total = self.calcular_total_con_servicio(subtotal)

            # Registrar transacción
            db.record_transaccion(id_pedido=id_pedido, fecha=self._fecha_actual(), monto_total=total, metodo_pago=metodo_pago)

            # Actualizar estado del pedido a 'Completado'
            db.update_estado_pedido(id_pedido=id_pedido, estado="Completado")

            detalles = db.get_detalles_pedido(id_pedido)

        return {
            "id_pedido": id_pedido,
            "fecha": fecha,
            "hora": hora,
            "subtotal": subtotal,
            "cargo_servicio": round(subtotal * self.CARGO_SERVICIO_PORCENTAJE, 2),
            "total": total,
            "detalles": detalles,
            "advertencias": advertencias,
        }

    # --- Consultas auxiliares para GUI ---

    def listar_menu_por_tipo(self, tipo: Optional[str] = None) -> List[Dict]:
        """Retorna el menú filtrado (o completo)."""
        with self.db as db:
            return db.get_menu(tipo)

    def listar_inventario(self) -> List[Dict]:
        """Retorna el inventario completo."""
        with self.db as db:
            return db.get_inventario()

    def verificar_bajo_stock(self) -> List[str]:
        """Genera mensajes de bajo stock actuales."""
        with self.db as db:
            bajos = db.get_bajo_stock()
        return [
            f"Stock bajo: {b['nombre_ingrediente']} ({b['cantidad']} {b['unidad_medida']} < mínimo {b['stock_minimo']})"
            for b in bajos
        ]

    def inicializar_esquema_y_datos(self) -> None:
        """Conveniencia: crea tablas e inserta datos iniciales."""
        with self.db as db:
            db.create_tables()
            db.seed_initial_data()
