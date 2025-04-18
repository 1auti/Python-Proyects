"""
Ejercicio 6: Expresiones Regulares para Validación
Descripción: Implementa un validador de datos que utilice expresiones regulares para verificar distintos tipos de datos comunes (email, teléfono, código postal, etc.).
Requisitos:

Crear funciones para validar diferentes formatos de datos
Implementar validadores para: email, número de teléfono, código postal, URL, tarjeta de crédito
Crear una función principal que valide una cadena según el tipo especificado
Proporcionar retroalimentación detallada en caso de error
"""

import re
from typing import Dict, Tuple, Callable

class Validator:
    """Clase para validar cualquier tipo de datos mediante expresiones regulares"""

    def __init__(self):
        """Inicializar los patrones de validacion"""

        # Patrón para email: usuario@dominio.extension
        self.patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        # Patrón para teléfono: +XX XXX XXX XXX o (XX) XXX-XXXX o XXX-XXX-XXXX
        self.patron_telefono = r'^(\+\d{1,3}\s)?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{3,4}$'

        # Patrón para código postal: 5 dígitos o 5+4 (ZIP+4)
        self.patron_codigo_postal = r'^\d{5}(-\d{4})?$'

        # Patrón para URL: http(s)://dominio.extension(/ruta)
        self.patron_url = r'^(https?:\/\/)?(www\.)?([a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+)(\/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?$'

        # Patrón para tarjeta de crédito: 13-19 dígitos, puede incluir espacios o guiones
        self.patron_tarjeta_credito = r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})$'

        # Patrón para fecha: YYYY-MM-DD, DD/MM/YYYY o MM/DD/YYYY
        self.patron_fecha = r'^(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})$'

        # Patrón para nombre: solo letras, espacios, guiones y apóstrofes
        self.patron_nombre = r'^[A-Za-zÀ-ÖØ-öø-ÿ]+([ \'-][A-Za-zÀ-ÖØ-öø-ÿ]+)*$'

        # Patrón para DNI/NIF español: 8 dígitos y letra
        self.patron_dni = r'^[0-9]{8}[A-Z]$'

        # Patrón para dirección IP: IPv4
        self.patron_ip = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    def validar_email(self, email: str) -> Tuple[bool, str]:
        """Valida un email."""
        if not email:
            return False, "El email no puede estar vacío"

        if re.match(self.patron_email, email):
            return True, "Email válido"

        # Verificaciones adicionales para dar retroalimentación específica
        if '@' not in email:
            return False, "El email debe contener el símbolo @"

        partes = email.split('@')
        if len(partes) != 2:
            return False, "El email debe contener exactamente un símbolo @"

        usuario, dominio = partes
        if not usuario:
            return False, "La parte del usuario no puede estar vacía"

        if '.' not in dominio:
            return False, "El dominio debe contener al menos un punto"

        extension = dominio.split('.')[-1]
        if len(extension) < 2:
            return False, "La extensión del dominio debe tener al menos 2 caracteres"

        return False, "El formato del email es incorrecto"

    def validar_telefono(self, telefono: str) -> Tuple[bool, str]:
        """Valida un número de teléfono."""
        if not telefono:
            return False, "El número de teléfono no puede estar vacío"

        # Eliminar espacios, guiones y paréntesis para verificar si son solo dígitos y el + opcional
        digitos_telefono = ''.join(c for c in telefono if c.isdigit() or c == '+')

        if re.match(self.patron_telefono, telefono):
            return True, "Número de teléfono válido"

        if not all(c.isdigit() or c in '()+-. ' for c in telefono):
            return False, "El teléfono solo puede contener dígitos, paréntesis, guiones, puntos, signo + y espacios"

        if len(digitos_telefono.replace('+', '')) < 7:
            return False, "El número de teléfono debe tener al menos 7 dígitos"

        return False, "El formato del número de teléfono es incorrecto"

    def validar_codigo_postal(self, codigo_postal: str) -> Tuple[bool, str]:
        """Valida un código postal estadounidense."""
        if not codigo_postal:
            return False, "El código postal no puede estar vacío"

        if re.match(self.patron_codigo_postal, codigo_postal):
            return True, "Código postal válido"

        if not all(c.isdigit() or c == '-' for c in codigo_postal):
            return False, "El código postal solo puede contener dígitos y guión"

        partes = codigo_postal.split('-')
        if len(partes) > 2:
            return False, "El código postal puede tener máximo un guión"

        if len(partes[0]) != 5 or not partes[0].isdigit():
            return False, "El código postal debe comenzar con 5 dígitos"

        if len(partes) == 2 and (len(partes[1]) != 4 or not partes[1].isdigit()):
            return False, "La segunda parte del código postal (ZIP+4) debe tener 4 dígitos"

        return False, "El formato del código postal es incorrecto"

    def validar_url(self, url: str) -> Tuple[bool, str]:
        """Valida una URL."""
        if not url:
            return False, "La URL no puede estar vacía"

        if re.match(self.patron_url, url):
            return True, "URL válida"

        # Verificaciones adicionales para dar retroalimentación específica
        if ' ' in url:
            return False, "La URL no puede contener espacios"

        if not any(prot in url.lower() for prot in ['http://', 'https://']) and not url.lower().startswith('www.'):
            return False, "La URL debe comenzar con http://, https:// o www."

        if '.' not in url:
            return False, "La URL debe contener al menos un punto en el dominio"

        return False, "El formato de la URL es incorrecto"

    def validar_tarjeta_credito(self, tarjeta: str) -> Tuple[bool, str]:
        """Valida un número de tarjeta de crédito."""
        if not tarjeta:
            return False, "El número de tarjeta no puede estar vacío"

        # Eliminar espacios y guiones para la validación
        tarjeta_limpia = tarjeta.replace(' ', '').replace('-', '')

        if not tarjeta_limpia.isdigit():
            return False, "El número de tarjeta solo puede contener dígitos, espacios o guiones"

        if len(tarjeta_limpia) < 13 or len(tarjeta_limpia) > 19:
            return False, "El número de tarjeta debe tener entre 13 y 19 dígitos"

        # Validación con expresión regular para los patrones comunes de tarjetas
        if re.match(self.patron_tarjeta_credito, tarjeta_limpia):
            # Algoritmo de Luhn (verificación de dígito de control)
            suma = 0
            num_digitos = len(tarjeta_limpia)
            paridad = num_digitos % 2

            for i in range(num_digitos):
                digito = int(tarjeta_limpia[i])
                if i % 2 == paridad:
                    digito *= 2
                    if digito > 9:
                        digito -= 9
                suma += digito

            if suma % 10 == 0:
                # Identificar el tipo de tarjeta
                if tarjeta_limpia.startswith('4'):
                    return True, "Tarjeta VISA válida"
                elif tarjeta_limpia.startswith('5') and 1 <= int(tarjeta_limpia[1]) <= 5:
                    return True, "Tarjeta MasterCard válida"
                elif tarjeta_limpia.startswith('34') or tarjeta_limpia.startswith('37'):
                    return True, "Tarjeta American Express válida"
                elif tarjeta_limpia.startswith('6011') or tarjeta_limpia.startswith('65'):
                    return True, "Tarjeta Discover válida"
                else:
                    return True, "Tarjeta de crédito válida"
            else:
                return False, "El número de tarjeta no supera la verificación de dígito de control (Luhn)"

        return False, "El formato del número de tarjeta es incorrecto"

    def validar(self, tipo: str, valor: str) -> Tuple[bool, str]:
        """Función principal que valida un valor según el tipo especificado."""
        validadores = {
            'email': self.validar_email,
            'telefono': self.validar_telefono,
            'codigo_postal': self.validar_codigo_postal,
            'url': self.validar_url,
            'tarjeta_credito': self.validar_tarjeta_credito
        }

        if tipo not in validadores:
            return False, f"Tipo de validación '{tipo}' no soportado"

        # Aquí va la llamada a la función del validador correspondiente
        try:
            return validadores[tipo](valor)
        except Exception as e:
            return False, f"Error al validar el tipo '{tipo}': {str(e)}"


if __name__ == "__main__":
        validador = Validator()

        # Ejemplos de validación
        datos_prueba = [
            ('email', 'usuario@dominio.com'),
            ('email', 'invalido@'),
            ('telefono', '+34 612 345 678'),
            ('telefono', '123'),
            ('codigo_postal', '12345'),
            ('codigo_postal', '1234'),
            ('url', 'https://www.ejemplo.com/ruta'),
            ('url', 'ejemplo..com'),
            ('tarjeta_credito', '4111 1111 1111 1111'),  # VISA de prueba
            ('tarjeta_credito', '1234567890123')
        ]

        for tipo, valor in datos_prueba:
            es_valido, mensaje = validador.validar(tipo, valor)
            estado = "✓" if es_valido else "✗"
            print(f"{estado} {tipo}: '{valor}' - {mensaje}")


