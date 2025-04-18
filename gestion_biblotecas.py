"""
Ejercicio 4: Sistema de Gestión de Biblioteca
Descripción: Implementa un sistema de gestión de biblioteca que permita administrar libros, usuarios y préstamos.
Requisitos:

Debe tener clases para Libro, Usuario, Préstamo y Biblioteca
Debe permitir registrar nuevos libros y usuarios
Debe manejar préstamos y devoluciones de libros
Debe poder calcular multas por retrasos en las devoluciones
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
import json


class EstadoLibro(Enum):
    DISPONIBLE = "disponible"
    PRESTADO = "prestado"
    EN_REPARACION = "en_reparacion"
    PERDIDO = "perdido"


class Libro:
    """Representa un libro en la biblioteca."""

    def __init__(self, codigo: str, titulo: str, autor: str,
                 categoria: str, año_publicacion: int):
        self.codigo = codigo
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.año_publicacion = año_publicacion
        self.estado = EstadoLibro.DISPONIBLE

    def to_dict(self):
        """Convierte el libro a un diccionario."""
        return {
            'codigo': self.codigo,
            'titulo': self.titulo,
            'autor': self.autor,
            'categoria': self.categoria,
            'año_publicacion': self.año_publicacion,
            'estado': self.estado.value
        }

    @classmethod
    def from_dict(cls, datos):
        """Crea un libro a partir de un diccionario."""
        libro = cls(
            codigo=datos['codigo'],
            titulo=datos['titulo'],
            autor=datos['autor'],
            categoria=datos['categoria'],
            año_publicacion=datos['año_publicacion']
        )
        libro.estado = EstadoLibro(datos['estado'])
        return libro

    def __str__(self):
        return f"{self.titulo} por {self.autor} ({self.año_publicacion}) - {self.estado.value}"


class Usuario:
    """Representa un usuario de la biblioteca."""

    def __init__(self, id_usuario: str, nombre: str, email: str):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.fecha_registro = datetime.now()
        self.prestamos_activos = []
        self.historial_prestamos = []

    def to_dict(self):
        """Convierte el usuario a un diccionario."""
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat(),
            'prestamos_activos': self.prestamos_activos,
            'historial_prestamos': self.historial_prestamos
        }

    @classmethod
    def from_dict(cls, datos):
        """Crea un usuario a partir de un diccionario."""
        usuario = cls(
            id_usuario=datos['id_usuario'],
            nombre=datos['nombre'],
            email=datos['email']
        )
        usuario.fecha_registro = datetime.fromisoformat(datos['fecha_registro'])
        usuario.prestamos_activos = datos['prestamos_activos']
        usuario.historial_prestamos = datos['historial_prestamos']
        return usuario


class Prestamo:
    """Representa un préstamo de libro."""

    def __init__(self, id_prestamo: str, codigo_libro: str, id_usuario: str):
        self.id_prestamo = id_prestamo
        self.codigo_libro = codigo_libro
        self.id_usuario = id_usuario
        self.fecha_prestamo = datetime.now()
        self.fecha_devolucion_esperada = self.fecha_prestamo + timedelta(days=14)  # 2 semanas
        self.fecha_devolucion_real = None
        self.multa = 0.0

    def calcular_multa(self, tarifa_diaria=0.5):
        """Calcula la multa por retraso en la devolución."""
        if not self.fecha_devolucion_real:
            hoy = datetime.now()
            if hoy > self.fecha_devolucion_esperada:
                dias_retraso = (hoy - self.fecha_devolucion_esperada).days
                self.multa = dias_retraso * tarifa_diaria
        elif self.fecha_devolucion_real > self.fecha_devolucion_esperada:
            dias_retraso = (self.fecha_devolucion_real - self.fecha_devolucion_esperada).days
            self.multa = dias_retraso * tarifa_diaria

        return self.multa

    def to_dict(self):
        """Convierte el préstamo a un diccionario."""
        return {
            'id_prestamo': self.id_prestamo,
            'codigo_libro': self.codigo_libro,
            'id_usuario': self.id_usuario,
            'fecha_prestamo': self.fecha_prestamo.isoformat(),
            'fecha_devolucion_esperada': self.fecha_devolucion_esperada.isoformat(),
            'fecha_devolucion_real': self.fecha_devolucion_real.isoformat() if self.fecha_devolucion_real else None,
            'multa': self.multa
        }

    @classmethod
    def from_dict(cls, datos):
        """Crea un préstamo a partir de un diccionario."""
        prestamo = cls(
            id_prestamo=datos['id_prestamo'],
            codigo_libro=datos['codigo_libro'],
            id_usuario=datos['id_usuario']
        )
        prestamo.fecha_prestamo = datetime.fromisoformat(datos['fecha_prestamo'])
        prestamo.fecha_devolucion_esperada = datetime.fromisoformat(datos['fecha_devolucion_esperada'])
        if datos['fecha_devolucion_real']:
            prestamo.fecha_devolucion_real = datetime.fromisoformat(datos['fecha_devolucion_real'])
        prestamo.multa = datos['multa']
        return prestamo


class Biblioteca:
    """Sistema de gestión de la biblioteca."""

    def __init__(self):
        self.libros: Dict[str, Libro] = {}
        self.usuarios: Dict[str, Usuario] = {}
        self.prestamos: Dict[str, Prestamo] = {}
        self.contador_prestamos = 1

    def agregar_libro(self, libro: Libro) -> bool:
        """Agrega un nuevo libro a la biblioteca."""
        if libro.codigo in self.libros:
            return False

        self.libros[libro.codigo] = libro
        return True

    def registrar_usuario(self, usuario: Usuario) -> bool:
        """Registra un nuevo usuario en la biblioteca."""
        if usuario.id_usuario in self.usuarios:
            return False

        self.usuarios[usuario.id_usuario] = usuario
        return True

    def prestar_libro(self, codigo_libro: str, id_usuario: str) -> Optional[Prestamo]:
        """Realiza el préstamo de un libro a un usuario."""
        # Verificar que existan libro y usuario
        if codigo_libro not in self.libros or id_usuario not in self.usuarios:
            return None

        libro = self.libros[codigo_libro]
        usuario = self.usuarios[id_usuario]

        # Verificar que el libro esté disponible
        if libro.estado != EstadoLibro.DISPONIBLE:
            return None

        # Verificar que el usuario no tenga más de 3 préstamos activos
        if len(usuario.prestamos_activos) >= 3:
            return None

        # Crear el préstamo
        id_prestamo = f"P{self.contador_prestamos:04d}"
        self.contador_prestamos += 1

        prestamo = Prestamo(id_prestamo, codigo_libro, id_usuario)
        self.prestamos[id_prestamo] = prestamo

        # Actualizar estado del libro y lista de préstamos del usuario
        libro.estado = EstadoLibro.PRESTADO
        usuario.prestamos_activos.append(id_prestamo)

        return prestamo

    def devolver_libro(self, id_prestamo: str) -> float:
        """Registra la devolución de un libro y calcula multa si aplica."""
        if id_prestamo not in self.prestamos:
            return -1

        prestamo = self.prestamos[id_prestamo]

        # Verificar que el préstamo esté activo (sin fecha de devolución)
        if prestamo.fecha_devolucion_real:
            return -1

        # Registrar la devolución
        prestamo.fecha_devolucion_real = datetime.now()

        # Calcular multa si aplica
        multa = prestamo.calcular_multa()

        # Actualizar libro y usuario
        libro = self.libros[prestamo.codigo_libro]
        usuario = self.usuarios[prestamo.id_usuario]

        libro.estado = EstadoLibro.DISPONIBLE
        usuario.prestamos_activos.remove(id_prestamo)
        usuario.historial_prestamos.append(id_prestamo)

        return multa

    def buscar_libros(self, texto_busqueda=None, categoria=None, disponible=None) -> List[Libro]:
        """Busca libros según varios criterios."""
        resultados = []

        for libro in self.libros.values():
            # Filtrar por texto de búsqueda
            if texto_busqueda and texto_busqueda.lower() not in libro.titulo.lower() and texto_busqueda.lower() not in libro.autor.lower():
                continue

            # Filtrar por categoría
            if categoria and libro.categoria != categoria:
                continue

            # Filtrar por disponibilidad
            if disponible is not None and (libro.estado == EstadoLibro.DISPONIBLE) != disponible:
                continue

            resultados.append(libro)

        return resultados

    def generar_informe_prestamos(self, desde=None, hasta=None) -> str:
        """Genera un informe de préstamos en un periodo."""
        if not desde:
            desde = datetime.min
        if not hasta:
            hasta = datetime.now()

        prestamos_periodo = [p for p in self.prestamos.values()
                             if desde <= p.fecha_prestamo <= hasta]

        # Estadísticas
        total_prestamos = len(prestamos_periodo)
        prestamos_activos = sum(1 for p in prestamos_periodo if not p.fecha_devolucion_real)
        prestamos_devueltos = total_prestamos - prestamos_activos
        prestamos_con_retraso = sum(1 for p in prestamos_periodo
                                    if
                                    p.fecha_devolucion_real and p.fecha_devolucion_real > p.fecha_devolucion_esperada)
        total_multas = sum(p.multa for p in prestamos_periodo)

        # Generar informe
        informe = [
            "=== INFORME DE PRÉSTAMOS ===",
            f"Período: {desde.strftime('%Y-%m-%d')} a {hasta.strftime('%Y-%m-%d')}",
            f"Total de préstamos: {total_prestamos}",
            f"Préstamos activos: {prestamos_activos}",
            f"Préstamos devueltos: {prestamos_devueltos}",
            f"Préstamos con retraso: {prestamos_con_retraso}",
            f"Total de multas recaudadas: ${total_multas:.2f}",
            "\nDetalle de préstamos:",
        ]

        for prestamo in sorted(prestamos_periodo, key=lambda p: p.fecha_prestamo):
            libro = self.libros[prestamo.codigo_libro]
            usuario = self.usuarios[prestamo.id_usuario]

            estado = "DEVUELTO" if prestamo.fecha_devolucion_real else "ACTIVO"
            if prestamo.fecha_devolucion_real and prestamo.fecha_devolucion_real > prestamo.fecha_devolucion_esperada:
                estado = "DEVUELTO CON RETRASO"

            informe.append(f"- [{prestamo.id_prestamo}] {libro.titulo} - {usuario.nombre} - {estado}")

        return "\n".join(informe)

    def guardar_datos(self, ruta_archivo):
        """Guarda todos los datos de la biblioteca en un archivo JSON."""
        datos = {
            'libros': [libro.to_dict() for libro in self.libros.values()],
            'usuarios': [usuario.to_dict() for usuario in self.usuarios.values()],
            'prestamos': [prestamo.to_dict() for prestamo in self.prestamos.values()],
            'contador_prestamos': self.contador_prestamos
        }

        with open(ruta_archivo, 'w') as f:
            json.dump(datos, f, indent=4)

    def cargar_datos(self, ruta_archivo):
        """Carga los datos de la biblioteca desde un archivo JSON."""
        try:
            with open(ruta_archivo, 'r') as f:
                datos = json.load(f)

            # Cargar libros
            self.libros = {}
            for libro_dict in datos['libros']:
                libro = Libro.from_dict(libro_dict)
                self.libros[libro.codigo] = libro

            # Cargar usuarios
            self.usuarios = {}
            for usuario_dict in datos['usuarios']:
                usuario = Usuario.from_dict(usuario_dict)
                self.usuarios[usuario.id_usuario] = usuario

            # Cargar préstamos
            self.prestamos = {}
            for prestamo_dict in datos['prestamos']:
                prestamo = Prestamo.from_dict(prestamo_dict)
                self.prestamos[prestamo.id_prestamo] = prestamo

            self.contador_prestamos = datos['contador_prestamos']

            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False


# Ejemplo de uso
if __name__ == "__main__":
    biblioteca = Biblioteca()

    # Agregar libros
    libro1 = Libro("L001", "Cien años de soledad", "Gabriel García Márquez", "Novela", 1967)
    libro2 = Libro("L002", "El principito", "Antoine de Saint-Exupéry", "Infantil", 1943)
    libro3 = Libro("L003", "Python para todos", "Charles Severance", "Informática", 2016)

    biblioteca.agregar_libro(libro1)
    biblioteca.agregar_libro(libro2)
    biblioteca.agregar_libro(libro3)

    # Registrar usuarios
    usuario1 = Usuario("U001", "Juan Pérez", "juan@ejemplo.com")
    usuario2 = Usuario("U002", "María López", "maria@ejemplo.com")

    biblioteca.registrar_usuario(usuario1)
    biblioteca.registrar_usuario(usuario2)

    # Realizar préstamos
    prestamo1 = biblioteca.prestar_libro("L001", "U001")
    prestamo2 = biblioteca.prestar_libro("L002", "U002")

    print("Estado inicial de la biblioteca:")
    for libro in biblioteca.libros.values():
        print(f"- {libro}")

    print("\nPréstamos activos:")
    for prestamo_id in usuario1.prestamos_activos:
        prestamo = biblioteca.prestamos[prestamo_id]
        libro = biblioteca.libros[prestamo.codigo_libro]
        print(f"- {usuario1.nombre} tiene prestado: {libro.titulo}")

    # Devolver un libro
    multa = biblioteca.devolver_libro(prestamo1.id_prestamo)
    print(f"\nLibro devuelto. Multa: ${multa:.2f}")

    # Generar informe
    print("\n" + biblioteca.generar_informe_prestamos())

    # Guardar datos
    biblioteca.guardar_datos("biblioteca_datos.json")
    print("\nDatos guardados en 'biblioteca_datos.json'")

