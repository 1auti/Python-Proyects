"""
 Asistente personal mejorado que reconoce comandos de voz, ejecuta tareas en tu computadora,
 y vuelve automáticamente al modo de escucha después de cada comando.
"""

import speech_recognition as sr # Reconoce voz desde el micrófono.
import pyttsx3 #  Convierte texto a voz (Text-to-Speech).
import datetime #  Para obtener fecha y hora.
import webbrowser #  Para abrir sitios web
import os # o ejecutar aplicaciones locales.
import json # Para manejo de archivos json
import requests # Para manejo de apis
import pyautogui # automatiza el mouse y toma capturas de pantalla
import random # generar numero aletorios
import time
import smtplib  # para enviar correos
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AsistenteVirtual:
    def __init__(self, nombre="Ana"):
        self.nombre = nombre
        self.activo = False
        self.palabra_activacion = f"hola {self.nombre.lower()}"
        self.inicializar_voz()
        self.comandos = {
            "hora": self.dar_hora,
            "fecha": self.dar_fecha,
            "buscar": self.buscar_web,
            "abrir": self.abrir_aplicacion,
            "correo": self.enviar_correo,
            # "clima": self.obtener_clima,
            "captura": self.tomar_captura,
            "recordatorio": self.crear_recordatorio,
            "apagar": self.apagar_computadora,
            # "chiste": self.contar_chiste,
            # "luz": self.controlar_luz,
            "música": self.reproducir_musica
        }
        self.config = self.cargar_configuracion()

    def cargar_configuracion(self):
        """Carga la configuración del asistente desde un archivo JSON."""
        try:
            with open("config_asistente.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Crear configuración predeterminada
            config = {
                "correo": {
                    "smtp_servidor": "smtp.gmail.com",
                    "smtp_puerto": 587,
                    "correo": "",
                    "contraseña": ""
                },
                "clima": {
                    "api_key": "",
                    "ciudad_predeterminada": "Madrid"
                },
                "aplicaciones": {
                    "navegador": "chrome",
                    "editor": "notepad",
                    "musica": "spotify",
                    "idea":"idea"
                },
                "casa_inteligente": {
                    "api_url": "",
                    "token": "",
                    "dispositivos": {
                        "luz_sala": "id1234",
                        "luz_cocina": "id5678"
                    }
                }
            }
            with open("config_asistente.json", "w") as f:
                json.dump(config, f, indent=4)
            return config

    def inicializar_voz(self):
        """Inicializa el motor de text-to-speech."""
        self.motor_voz = pyttsx3.init()
        voces = self.motor_voz.getProperty('voices')
        # Buscar una voz en español
        for voz in voces:
            if "spanish" in voz.id.lower():
                self.motor_voz.setProperty('voice', voz.id)
                break
        self.motor_voz.setProperty('rate', 150)

    def hablar(self, texto):
        """Convierte texto a voz."""
        print(f"{self.nombre}: {texto}")
        self.motor_voz.say(texto)
        self.motor_voz.runAndWait()

    def escuchar(self):
        """Escucha el micrófono y convierte la voz a texto."""
        reconocedor = sr.Recognizer()

        with sr.Microphone() as fuente:
            print("Escuchando...")
            reconocedor.adjust_for_ambient_noise(fuente, duration=1)
            audio = reconocedor.listen(fuente)

        try:
            texto = reconocedor.recognize_google(audio, language="es-ES")
            print(f"Usuario: {texto}")
            return texto.lower()
        except sr.UnknownValueError:
            return "no_entendido"
        except sr.RequestError:
            self.hablar("Lo siento, no puedo acceder al servicio de reconocimiento de voz.")
            return "error"

    def procesar_comando(self, texto):
        """Procesa el comando de voz y ejecuta la acción correspondiente."""
        comando_ejecutado = False

        for palabra_clave, funcion in self.comandos.items():
            if palabra_clave in texto:
                resultado = funcion(texto)
                comando_ejecutado = resultado
                break

        if not comando_ejecutado:
            self.hablar("No entendí ese comando. ¿Puedes repetirlo?")
        else:
            # Después de ejecutar cualquier comando con éxito,
            # informar al usuario que debe volver a activar al asistente si lo necesita
            self.hablar("Si necesitas algo más, vuelve a decir 'Hola Ana'.")

        # Desactivar el asistente para que vuelva al modo de escucha de palabra de activación
        self.activo = False
        return comando_ejecutado

    def escuchar_activacion(self):
        """Escucha activamente hasta detectar la palabra de activacion"""
        reconocedor = sr.Recognizer()
        reconocedor.energy_threshold = 300 # Ajustamos la capacidad por el ruido ambiental

        print(f"Esperando palabra de activacion: '{self.palabra_activacion}'...")

        while True:
            try:
                with sr.Microphone() as fuente:
                    reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)
                    audio = reconocedor.listen(fuente, phrase_time_limit=3)

                texto = reconocedor.recognize_google(audio, language="es-ES").lower()
                print(f"Detectado: {texto}")

                if self.palabra_activacion in texto:
                    print("¡Palabra de activación detectada!")
                    self.hablar(f"Hola, soy {self.nombre}. ¿En qué puedo ayudarte?")
                    return True

            except sr.UnknownValueError:
                # No se detectó voz clara, seguir escuchando
                pass
            except sr.RequestError:
                print("Error de conexión al servicio de reconocimiento")
                time.sleep(5)  # Esperar antes de reintentar
            except Exception as e:
                print(f"Error: {str(e)}")
                time.sleep(2)

    def ejecutar_en_segundo_plano(self):
        """Ejecuta el asistente en modo de escucha continua."""
        self.inicializar_voz()
        print(f"Asistente {self.nombre} iniciado en modo de escucha continua")

        while True:
            if self.escuchar_activacion():
                # Entrar en modo conversación
                self.activo = True

                while self.activo:
                    texto = self.escuchar()

                    if texto == "no_entendido":
                        self.hablar("No te entendí. ¿Puedes repetirlo?")
                    elif texto == "error":
                        continue
                    elif any(palabra in texto for palabra in ["adiós", "adios", "chao", "hasta luego"]):
                        self.hablar("Hasta luego, estaré aquí si me necesitas.")
                        self.activo = False
                    else:
                        self.procesar_comando(texto)
                        # No es necesario un temporizador por inactividad ya que
                        # ahora el asistente vuelve automáticamente al modo de escucha


    # Funciones de comandos
    def dar_hora(self, texto):
        """Informa la hora actual."""
        hora_actual = datetime.datetime.now().strftime("%H:%M")
        self.hablar(f"Son las {hora_actual}")
        return True

    def dar_fecha(self, texto):
        """Informa la fecha actual."""
        fecha = datetime.datetime.now()
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        dia = fecha.day
        mes = meses[fecha.month - 1]
        año = fecha.year
        self.hablar(f"Hoy es {dia} de {mes} de {año}")
        return True

    def buscar_web(self, texto):
        """Realiza una búsqueda en la web."""
        palabras = texto.split("buscar")
        if len(palabras) > 1:
            busqueda = palabras[1].strip()
            url = f"https://www.google.com/search?q={busqueda}"
            self.hablar(f"Buscando {busqueda} en la web")
            webbrowser.open(url)
            return True
        self.hablar("¿Qué quieres buscar?")
        return False

    def abrir_aplicacion(self, texto):
        """Abre una aplicación mencionada en el comando."""
        apps_comunes = {
            "navegador": self.config["aplicaciones"]["navegador"],
            "chrome": "chrome",
            "firefox": "firefox",
            "excel": "excel",
            "word": "winword",
            "powerpoint": "powerpnt",
            "calculadora": "calc",
            "editor": self.config["aplicaciones"]["editor"],
            "música": self.config["aplicaciones"]["musica"],
            "spotify": "spotify",
            "idea":self.config["aplicaciones"]["idea"],
            "python":self.config["aplicaciones"]["python"]
        }

        for app_nombre, app_comando in apps_comunes.items():
            if app_nombre in texto:
                try:
                    self.hablar(f"Abriendo {app_nombre}")
                    os.system(f'powershell -Command "& {app_comando}"')
                    return True
                except:
                    self.hablar(f"No pude abrir {app_nombre}")
                    return False

        self.hablar("No reconozco esa aplicación")
        return False

    def enviar_correo(self, texto):
        """Envía un correo electrónico mediante comando de voz."""
        if not self.config["correo"]["correo"] or not self.config["correo"]["contraseña"]:
            self.hablar("Necesitas configurar tus credenciales de correo primero")
            return False

        # Extraer destinatario
        self.hablar("¿A quién quieres enviar el correo?")
        destinatario = self.escuchar()
        if destinatario in ["no_entendido", "error"]:
            return False

        # Extraer asunto
        self.hablar("¿Cuál es el asunto del correo?")
        asunto = self.escuchar()
        if asunto in ["no_entendido", "error"]:
            return False

        # Extraer contenido
        self.hablar("Dicta el contenido del correo")
        contenido = self.escuchar()
        if contenido in ["no_entendido", "error"]:
            return False

        # Confirmar
        self.hablar(f"Voy a enviar un correo a {destinatario} con asunto {asunto}. ¿Es correcto?")
        confirmacion = self.escuchar()
        if "sí" not in confirmacion and "si" not in confirmacion:
            self.hablar("Correo cancelado")
            return False

        # Enviar correo
        try:
            mensaje = MIMEMultipart()
            mensaje["From"] = self.config["correo"]["correo"]
            mensaje["To"] = destinatario
            mensaje["Subject"] = asunto
            mensaje.attach(MIMEText(contenido, "plain"))

            servidor = smtplib.SMTP(
                self.config["correo"]["smtp_servidor"],
                self.config["correo"]["smtp_puerto"]
            )
            servidor.starttls()
            servidor.login(
                self.config["correo"]["correo"],
                self.config["correo"]["contraseña"]
            )
            texto_mensaje = mensaje.as_string()
            servidor.sendmail(
                self.config["correo"]["correo"],
                destinatario,
                texto_mensaje
            )
            servidor.quit()

            self.hablar("Correo enviado con éxito")
            return True
        except Exception as e:
            self.hablar(f"No pude enviar el correo: {str(e)}")
            return False

    def obtener_clima(self, texto):
        """Obtiene la información del clima para una ciudad."""
        if not self.config["clima"]["api_key"]:
            self.hablar("Necesitas configurar tu API key para el clima")
            return False

        # Extraer ciudad
        palabras = texto.split("clima")
        ciudad = self.config["clima"]["ciudad_predeterminada"]
        if len(palabras) > 1 and palabras[1].strip():
            ciudad = palabras[1].strip()

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={self.config['clima']['api_key']}&units=metric&lang=es"
            respuesta = requests.get(url)
            datos = respuesta.json()

            if respuesta.status_code == 200:
                temperatura = datos["main"]["temp"]
                descripcion = datos["weather"][0]["description"]
                self.hablar(f"En {ciudad} la temperatura es de {temperatura} grados Celsius con {descripcion}")
                return True
            else:
                self.hablar(f"No pude obtener información del clima para {ciudad}")
                return False
        except Exception as e:
            self.hablar(f"Error al obtener el clima: {str(e)}")
            return False

    def tomar_captura(self, texto):
        """Toma una captura de pantalla."""
        try:
            nombre_archivo = f"captura_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.hablar("Tomando captura de pantalla")
            captura = pyautogui.screenshot()
            captura.save(nombre_archivo)
            self.hablar(f"Captura guardada como {nombre_archivo}")
            return True
        except Exception as e:
            self.hablar(f"Error al tomar captura: {str(e)}")
            return False

    def crear_recordatorio(self, texto):
        """Crea un recordatorio con temporizador."""
        # Extraer tiempo
        palabras = texto.split("recordatorio")
        if len(palabras) <= 1:
            self.hablar("¿En cuántos minutos quieres el recordatorio?")
            tiempo_texto = self.escuchar()
            try:
                minutos = int(''.join(filter(str.isdigit, tiempo_texto)))
            except:
                self.hablar("No pude entender el tiempo")
                return False
        else:
            # Intentar extraer número de minutos del comando
            try:
                minutos = int(''.join(filter(str.isdigit, palabras[1])))
            except:
                self.hablar("¿En cuántos minutos quieres el recordatorio?")
                tiempo_texto = self.escuchar()
                try:
                    minutos = int(''.join(filter(str.isdigit, tiempo_texto)))
                except:
                    self.hablar("No pude entender el tiempo")
                    return False

        # Extraer mensaje
        self.hablar("¿Cuál es el mensaje del recordatorio?")
        mensaje = self.escuchar()
        if mensaje in ["no_entendido", "error"]:
            return False

        self.hablar(f"Recordatorio establecido para {minutos} minutos a partir de ahora")

        # Crear hilo para el temporizador
        import threading
        def temporizador():
            time.sleep(minutos * 60)
            for _ in range(3):
                self.hablar(f"Recordatorio: {mensaje}")

        hilo = threading.Thread(target=temporizador)
        hilo.daemon = True
        hilo.start()
        return True

    def apagar_computadora(self, texto):
        """Apaga la computadora después de confirmar."""
        self.hablar("¿Estás seguro de que quieres apagar la computadora?")
        confirmacion = self.escuchar()

        if "sí" in confirmacion or "si" in confirmacion:
            self.hablar("Apagando la computadora en 30 segundos. Hasta pronto.")
            os.system("shutdown /s /t 30")
            return True
        else:
            self.hablar("Operación cancelada")
            return False

    def reproducir_musica(self, texto):
        """Reproduce música (simulación o integración real)."""
        if "spotify" in self.config["aplicaciones"]["musica"]:
            # Abrir Spotify
            try:
                os.system("start spotify")
                time.sleep(2)  # Esperar a que se abra

                # Simular reproducción
                if "pausa" in texto or "pausar" in texto:
                    pyautogui.press('space')  # Tecla espacio suele pausar/reproducir
                    self.hablar("Pausando música")
                elif "siguiente" in texto:
                    pyautogui.hotkey('ctrl', 'right')  # Siguiente canción
                    self.hablar("Reproduciendo siguiente canción")
                elif "anterior" in texto:
                    pyautogui.hotkey('ctrl', 'left')  # Canción anterior
                    self.hablar("Reproduciendo canción anterior")
                else:
                    pyautogui.press('space')  # Reproducir
                    self.hablar("Reproduciendo música")

                return True
            except Exception as e:
                self.hablar(f"Error al controlar la música: {str(e)}")
                return False
        else:
            self.hablar(f"Abriendo reproductor de música {self.config['aplicaciones']['musica']}")
            os.system(f"start {self.config['aplicaciones']['musica']}")
            return True

    def ejecutar(self):
        """Ejecuta el asistente y espera comandos."""
        self.hablar(f"Hola, soy {self.nombre}. ¿En qué puedo ayudarte?")

        while True:
            texto = self.escuchar()

            if texto == "no_entendido":
                self.hablar("No te entendí. ¿Puedes repetirlo?")
                continue
            elif texto == "error":
                continue

            if "adiós" in texto or "adios" in texto or "chao" in texto or "hasta luego" in texto:
                self.hablar("Hasta luego, que tengas un buen día")
                break

            self.procesar_comando(texto)


if __name__ == "__main__":
    asistente = AsistenteVirtual("Ana")
    asistente.ejecutar_en_segundo_plano()