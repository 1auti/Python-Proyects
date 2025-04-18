"""
Ejercicio 3: Sistema de Inventario
Descripción: Crea un sistema de gestión de inventario para una tienda utilizando programación orientada a objetos.
Requisitos:

Debe tener clases para Producto, Inventario y Venta
Los productos deben tener atributos como id, nombre, precio, cantidad
El inventario debe permitir añadir, eliminar y buscar productos
Las ventas deben registrar qué productos se vendieron y actualizar el inventario
"""

from datetime import datetime
# crear clases más simples que actúan como contenedores de datos.
from dataclasses import dataclass
from typing import List, Dict, Optional
import json


@dataclass
class Producto:
    """Clase para representar un producto en el inventario."""
    id: int
    nombre: str
    precio: float
    cantidad: int
    categoria: str

    def to_dict(self):
        """Convierte el producto a un diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'cantidad': self.cantidad,
            'categoria': self.categoria
        }

    @classmethod
    def from_dict(cls, datos):
        """Crea un producto a partir de un diccionario."""
        return cls(
            id=datos['id'],
            nombre=datos['nombre'],
            precio=datos['precio'],
            cantidad=datos['cantidad'],
            categoria=datos['categoria']
        )


class Inventario:
    """Clase para gestionar el inventario de productos."""

    def __init__(self):
        """Inicializa el inventario vacío."""
        self.productos: Dict[int, Producto] = {}
        self.siguiente_id = 1

    def agregar_producto(self, nombre, precio, cantidad, categoria) -> Producto:
        """Agrega un nuevo producto al inventario."""
        producto = Producto(
            id=self.siguiente_id,
            nombre=nombre,
            precio=precio,
            cantidad=cantidad,
            categoria=categoria
        )

        self.productos[producto.id] = producto
        self.siguiente_id += 1
        return producto

    def obtener_producto(self, id_producto) -> Optional[Producto]:
        """Obtiene un producto por su ID."""
        return self.productos.get(id_producto)

    def actualizar_producto(self, id_producto, **kwargs):
        """Actualiza los atributos de un producto."""
        producto = self.obtener_producto(id_producto)
        if producto:
            for key, value in kwargs.items():
                if hasattr(producto, key):
                    setattr(producto, key, value)
            return True
        return False

    def eliminar_producto(self, id_producto) -> bool:
        """Elimina un producto del inventario."""
        if id_producto in self.productos:
            del self.productos[id_producto]
            return True
        return False

    def buscar_productos(self, texto_busqueda=None, categoria=None) -> List[Producto]:
        """Busca productos por texto o categoría."""
        resultados = []

        for producto in self.productos.values():
            # Filtrar por texto de búsqueda si se proporciona
            if texto_busqueda and texto_busqueda.lower() not in producto.nombre.lower():
                continue

            # Filtrar por categoría si se proporciona
            if categoria and producto.categoria != categoria:
                continue

            resultados.append(producto)

        return resultados

    def guardar_en_archivo(self, ruta_archivo):
        """Guarda el inventario en un archivo JSON."""
        datos = {
            'siguiente_id': self.siguiente_id,
            'productos': [p.to_dict() for p in self.productos.values()]
        }

        with open(ruta_archivo, 'w') as f:
            json.dump(datos, f, indent=4)

    def cargar_desde_archivo(self, ruta_archivo):
        """Carga el inventario desde un archivo JSON."""
        try:
            with open(ruta_archivo, 'r') as f:
                datos = json.load(f)

            self.siguiente_id = datos['siguiente_id']
            self.productos = {}

            for prod_dict in datos['productos']:
                producto = Producto.from_dict(prod_dict)
                self.productos[producto.id] = producto

            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False


class ElementoVenta:
    """Representa un elemento dentro de una venta."""

    def __init__(self, producto: Producto, cantidad: int):
        self.id_producto = producto.id
        self.nombre_producto = producto.nombre
        self.precio_unitario = producto.precio
        self.cantidad = cantidad
        self.subtotal = producto.precio * cantidad


class Venta:
    """Clase para representar una venta."""

    def __init__(self, inventario: Inventario):
        """Inicializa una nueva venta."""
        self.inventario = inventario
        self.elementos: List[ElementoVenta] = []
        self.fecha = datetime.now()
        self.total = 0.0

    def agregar_producto(self, id_producto: int, cantidad: int) -> bool:
        """Agrega un producto a la venta."""
        producto = self.inventario.obtener_producto(id_producto)

        if not producto:
            raise ValueError(f"Producto con ID {id_producto} no encontrado")

        if producto.cantidad < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {producto.cantidad}")

        # Crear elemento de venta
        elemento = ElementoVenta(producto, cantidad)
        self.elementos.append(elemento)

        # Actualizar total
        self.total += elemento.subtotal

        return True

    def finalizar_venta(self) -> bool:
        """Finaliza la venta y actualiza el inventario."""
        # Actualizar el inventario
        for elemento in self.elementos:
            producto = self.inventario.obtener_producto(elemento.id_producto)
            nueva_cantidad = producto.cantidad - elemento.cantidad
            self.inventario.actualizar_producto(elemento.id_producto, cantidad=nueva_cantidad)

        return True

    def generar_recibo(self) -> str:
        """Genera un recibo de la venta."""
        lineas = [
            "=== RECIBO DE VENTA ===",
            f"Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}",
            "------------------------",
            "PRODUCTOS:",
        ]

        for elemento in self.elementos:
            lineas.append(f"{elemento.nombre_producto} x{elemento.cantidad}: ${elemento.subtotal:.2f}")

        lineas.append("------------------------")
        lineas.append(f"TOTAL: ${self.total:.2f}")
        lineas.append("¡Gracias por su compra!")

        return "\n".join(lineas)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear inventario
    inventario = Inventario()

    # Añadir productos
    inventario.agregar_producto("Laptop HP", 799.99, 10, "Electrónica")
    inventario.agregar_producto("Mouse Inalámbrico", 24.99, 30, "Accesorios")
    inventario.agregar_producto("Teclado Mecánico", 59.99, 15, "Accesorios")

    # Realizar una venta
    try:
        venta = Venta(inventario)
        venta.agregar_producto(1, 2)  # 2 laptops
        venta.agregar_producto(2, 1)  # 1 mouse
        venta.finalizar_venta()

        print(venta.generar_recibo())

        print("\nInventario actualizado:")
        for producto in inventario.productos.values():
            print(f"{producto.nombre}: {producto.cantidad} unidades")

    except ValueError as e:
        print(f"Error: {e}")