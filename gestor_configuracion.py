"""
Ejercicio 2: Gestor de Configuración
Descripción: Crea un gestor de configuración que pueda leer y modificar archivos de configuración en formato INI.
Requisitos:

Debe permitir leer archivos de configuración con secciones
Debe permitir modificar valores existentes
Debe permitir añadir nuevas secciones y valores
Debe poder guardar los cambios en el archivo
"""

# Esta librería sirve para leer, modificar y escribir archivos .ini.
import configparser
# La librería os permite interactuar con el sistema operativo
import os

class GestorConfiguracion:
    """ Clase para gestionar archivos de configuracion INI"""


    def __init__(self, ruta_archivo):
        """ Se inicializa el gestor con la ruta del archivo de configuracion"""
        self.ruta_archivo = ruta_archivo
        self.config = configparser.ConfigParser()

        if os.path.exists(ruta_archivo):
            self.config.read(ruta_archivo)

    def get_valor(self, seccion, clave, valor_predeterminado=None):
        """ Obtener un valor de la configuracion"""
        try:
            return self.config[seccion][clave]
        except (KeyError, configparser.NoSectionError):
            return  valor_predeterminado

    def set_valor(self,seccion, clave, valor):
        """ Establecer un valor en la configuracion"""
        if not self.config.has_section(seccion):
            self.config.add_section(seccion)

        self.config[seccion][clave] = str(valor)

    def eliminar_valor(self, seccion,clave):
        """ Eliminar un valor de la configuracion"""
        try:
            self.config.remove_option(seccion,clave)
            return  True
        except (configparser.NoSectionError,KeyError):
            return False

    def guardar(self):
        """ Guardar los cambios em el archivo de configuracion"""
        with open(self.ruta_archivo, 'w') as archivo:
            self.config.write(archivo)

    def mostrar_configuracion(self):
        """ Muestra la configuracion actual"""
        for seccion in self.config.sections():
            print(f"[{seccion}]")
            for clave, valor in self.config.items(seccion):
                print(f"{clave} = {valor}")
            print()


# Ejemplo de uso
if __name__ == "__main__":
    config = GestorConfiguracion("app_config.ini")

    # Establecer algunos valores
    config.set_valor("BASE_DE_DATOS", "usuario", "admin")
    config.set_valor("BASE_DE_DATOS", "contraseña", "admin123")
    config.set_valor("BASE_DE_DATOS", "host", "localhost")

    config.set_valor("APLICACION", "debug", "True")
    config.set_valor("APLICACION", "puerto", "8080")

    # Guardar la configuración
    config.guardar()

    # Mostrar la configuración
    config.mostrar_configuracion()