"""
 Desarrolla un script para automatizar tareas repetitivas, como el procesamiento de archivos, envío de correos o generación de informes.
Requisitos:

Automatizar una tarea como monitoreo de directorios, procesamiento de archivos o generación de informes
Implementar un sistema de logging para seguimiento de actividades
Manejar excepciones y crear un sistema robusto
(Opcional) Agregar notificaciones por correo o mensajes
"""

import os
import sys
import time
import shutil
import logging
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AutomatizadorTareas:
    """Clase principal para automatización de tareas en directorios."""
    
    def __init__(self, directorio_monitoreo, directorio_procesados, directorio_rechazados):
        """Inicializa el automatizador."""
        self.directorio_monitoreo = Path(directorio_monitoreo)
        self.directorio_procesados = Path(directorio_procesados)
        self.directorio_rechazados = Path(directorio_rechazados)
        
        # Crear directorios si no existen
        for directorio in [self.directorio_monitoreo, self.directorio_procesados, self.directorio_rechazados]:
            directorio.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        self.configurar_logging()
        
        # Registro de archivos procesados
        self.registro_procesados = self.cargar_registro()
    
    def configurar_logging(self):
        """Configura el sistema de logging."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'automatizador_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def cargar_registro(self):
        """Carga el registro de archivos procesados."""
        registro_file = Path('registro_procesados.json')
        
        if registro_file.exists():
            with open(registro_file, 'r') as f:
                return json.load(f)
        return {}
    
    def guardar_registro(self):
        """Guarda el registro de archivos procesados."""
        with open('registro_procesados.json', 'w') as f:
            json.dump(self.registro_procesados, f, indent=4)
    
    def calcular_hash_archivo(self, ruta_archivo):
        """Calcula el hash SHA-256 de un archivo."""
        sha256_hash = hashlib.sha256()
        
        with open(ruta_archivo, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def procesar_archivo(self, ruta_archivo):
        """Procesa un archivo según su tipo."""
        try:
            archivo = Path(ruta_archivo)
            
            # Verificar si el archivo ya fue procesado
            hash_archivo = self.calcular_hash_archivo(archivo)
            
            if hash_archivo in self.registro_procesados:
                self.logger.info(f"Archivo '{archivo.name}' ya fue procesado anteriormente.")
                self.mover_archivo(archivo, self.directorio_procesados)
                return
            
            # Determinar el tipo de procesamiento según la extensión
            extension = archivo.suffix.lower()
            
            if extension in ['.txt', '.csv']:
                self.procesar_texto(archivo)
            elif extension in ['.jpg', '.jpeg', '.png']:
                self.procesar_imagen(archivo)
            elif extension in ['.pdf']:
                self.procesar_pdf(archivo)
            else:
                self.logger.warning(f"Tipo de archivo no soportado: {extension}")
                self.mover_archivo(archivo, self.directorio_rechazados)
                return
            
            # Registrar el archivo como procesado
            self.registro_procesados[hash_archivo] = {
                'nombre': archivo.name,
                'fecha_procesamiento': datetime.now().isoformat(),
                'tamaño': archivo.stat().st_size
            }
            
            self.guardar_registro()
            self.mover_archivo(archivo, self.directorio_procesados)
            
        except Exception as e:
            self.logger.error(f"Error al procesar {ruta_archivo}: {str(e)}")
            self.mover_archivo(Path(ruta_archivo), self.directorio_rechazados)
    
    def procesar_texto(self, archivo):
        """Procesa archivos de texto."""
        self.logger.info(f"Procesando archivo de texto: {archivo.name}")
        
        # Ejemplo: Contar líneas y palabras
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            lineas = len(contenido.splitlines())
            palabras = len(contenido.split())
        
        # Crear un informe
        informe_path = self.directorio_procesados / f"{archivo.stem}_informe.txt"
        with open(informe_path, 'w', encoding='utf-8') as f:
            f.write(f"Informe de procesamiento para: {archivo.name}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de líneas: {lineas}\n")
            f.write(f"Total de palabras: {palabras}\n")
        
        self.logger.info(f"Informe generado: {informe_path}")
    
    def procesar_imagen(self, archivo):
        """Procesa archivos de imagen."""
        self.logger.info(f"Procesando imagen: {archivo.name}")
        
        try:
            from PIL import Image
            
            # Ejemplo: Obtener información básica de la imagen
            with Image.open(archivo) as img:
                info = {
                    'formato': img.format,
                    'modo': img.mode,
                    'tamaño': img.size,
                    'ancho': img.width,
                    'alto': img.height
                }
            
            # Crear un informe
            informe_path = self.directorio_procesados / f"{archivo.stem}_info.json"
            with open(informe_path, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=4)
            
            self.logger.info(f"Información de imagen guardada: {informe_path}")
            
        except ImportError:
            self.logger.error("Librería PIL/Pillow no instalada. No se puede procesar la imagen.")
    
    def procesar_pdf(self, archivo):
        """Procesa archivos PDF."""
        self.logger.info(f"Procesando PDF: {archivo.name}")
        
        try:
            import PyPDF2
            
            # Ejemplo: Extraer texto del PDF
            with open(archivo, 'rb') as f:
                lector_pdf = PyPDF2.PdfReader(f)
                num_paginas = len(lector_pdf.pages)
                
                texto = ""
                for pagina in lector_pdf.pages:
                    texto += pagina.extract_text() + "\n"
            
            # Crear un informe
            informe_path = self.directorio_procesados / f"{archivo.stem}_texto.txt"
            with open(informe_path, 'w', encoding='utf-8') as f:
                f.write(f"Texto extraído de: {archivo.name}\n")
                f.write(f"Número de páginas: {num_paginas}\n")
                f.write("-" * 40 + "\n")
                f.write(texto)
            
            self.logger.info(f"Texto extraído y guardado: {informe_path}")
            
        except ImportError:
            self.logger.error("Librería PyPDF2 no instalada. No se puede procesar el PDF.")
    
    def mover_archivo(self, archivo, directorio_destino):
        """Mueve un archivo a un directorio destino."""
        try:
            destino = directorio_destino / archivo.name
            
            # Si el archivo ya existe, agregar timestamp al nombre
            if destino.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nueva_destino = directorio_destino / f"{archivo.stem}_{timestamp}{archivo.suffix}"
                shutil.move(str(archivo), str(nueva_destino))
                self.logger.info(f"Archivo movido a: {nueva_destino}")
            else:
                shutil.move(str(archivo), str(destino))
                self.logger.info(f"Archivo movido a: {destino}")
                
        except Exception as e:
            self.logger.error(f"Error al mover archivo {archivo}: {str(e)}")
    
    def enviar_notificacion_email(self, asunto, mensaje, destinatario):
        """Envía una notificación por correo electrónico."""
        try:
            # Configuración del servidor SMTP (ejemplo con Gmail)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            remitente = "tu_email@gmail.com"
            password = "tu_contraseña"  # Utilizar variables de entorno para seguridad
            
            msg = MIMEMultipart()
            msg['From'] = remitente
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            msg.attach(MIMEText(mensaje, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(remitente, password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Notificación enviada a {destinatario}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al enviar correo: {str(e)}")
            return False
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo de directorio usando watchdog."""
        event_handler = MonitorDirectorio(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.directorio_monitoreo), recursive=False)
        observer.start()
        
        self.logger.info(f"Iniciando monitoreo de {self.directorio_monitoreo}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info("Monitoreo detenido")
        
        observer.join()

class MonitorDirectorio(FileSystemEventHandler):
    """Manejador de eventos del sistema de archivos."""
    
    def __init__(self, automatizador):
        self.automatizador = automatizador
    
    def on_created(self, event):
        """Se ejecuta cuando se crea un nuevo archivo."""
        if not event.is_directory:
            # Esperar un momento para asegurar que el archivo esté completamente escrito
            time.sleep(1)
            self.automatizador.procesar_archivo(event.src_path)

# Ejemplo de uso
if __name__ == "__main__":
    automatizador = AutomatizadorTareas(
        directorio_monitoreo='archivos_entrada',
        directorio_procesados='archivos_procesados',
        directorio_rechazados='archivos_rechazados'
    )
    
    # Iniciar el monitoreo
    automatizador.iniciar_monitoreo()