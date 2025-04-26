"""
Crea un script que monitoree una carpeta y cada vez que aparezca un nuevo archivo de texto, lo procese contando palabras,
 líneas y caracteres, guardando las estadísticas en un archivo CSV.
Conceptos: Monitoreo de sistema de archivos, procesamiento de texto, escritura/lectura de archivos
"""

import os
import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent


class ArchivoNuevoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.txt'):
            self.procesar_archivo(event.src_path)

    def procesar_archivo(self, ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
                lineas = contenido.split('\n')
                palabras = contenido.split()
                caracteres = len(contenido)

                estadisticas = {
                    'archivo': os.path.basename(ruta_archivo),
                    'lineas': len(lineas),
                    'palabras': len(palabras),
                    'caracteres': caracteres
                }

                self.guardar_estadisticas(estadisticas)
                print(f"Procesado: {ruta_archivo}")
        except Exception as e:
            print(f"Error procesando {ruta_archivo}: {e}")

    def guardar_estadisticas(self, estadisticas):
        archivo_existe = os.path.exists('estadisticas.csv')

        with open('estadisticas.csv', 'a', newline='', encoding='utf-8') as csvfile:
            campos = ['archivo', 'lineas', 'palabras', 'caracteres']
            writer = csv.DictWriter(csvfile, fieldnames=campos)

            if not archivo_existe:
                writer.writeheader()

            writer.writerow(estadisticas)

    def monitorear_carpeta(ruta):
        event_handler = ArchivoNuevoHandler()
        observer = Observer()
        observer.schedule(event_handler, ruta, recursive=False)
        observer.start()

        try:
            print(f"Monitoreando la carpeta: {ruta}")
            print("Presiona Ctrl+C para detener")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    if __name__ == "__main__":
        carpeta_a_monitorear = "archivos"  # Cambia esto a la ruta que deseas monitorear
        if not os.path.exists(carpeta_a_monitorear):
            os.makedirs(carpeta_a_monitorear)
        monitorear_carpeta(carpeta_a_monitorear)
