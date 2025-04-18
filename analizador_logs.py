"""
Requisitos:

El programa debe leer un archivo de registro con formato: [FECHA] [NIVEL] [MENSAJE]
Debe contar la frecuencia de cada nivel de log (ERROR, WARNING, INFO, etc.)
Debe identificar los mensajes de error más frecuentes
Debe generar un informe resumido
"""

import re
from collections import Counter
from datetime import datetime

def analizar_logs(ruta_archivo):
    """
    Analiza un archivo de log y genera estadísticas.
    """

    # Esta expresión regular divide cada línea en tres grupos: fecha, nivel del log y mensaje.
    patron = r'\[(.*?)\] \[(.*?)\] (.*)'

    #niveles: Contabiliza cuántas veces aparece cada nivel (ERROR, INFO, WARNING)
    #errores: Registra los mensajes de error específicos y su frecuencia
    #fechas: Guarda todas las fechas para análisis temporal

    niveles = Counter()
    errores = Counter()
    fechas = []

    try:
        with open(ruta_archivo, 'r') as archivo:
            for linea in archivo:
                match = re.match(patron, linea.strip())
                if match:
                    fecha_str, nivel, mensaje = match.groups()

                    # Contador niveles
                    niveles[nivel] += 1

                    # Contador mensajes de error
                    if nivel == "ERROR":  # corregido "ERRROR"
                        errores[mensaje] += 1

                    # Guardar fechas para análisis
                    try:
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                        fechas.append(fecha)
                    except ValueError:
                        pass

        # Mostrar informe solo una vez, después de procesar todo
        print("=== INFORME DE ANÁLISIS DE LOG ===")
        print(f"Total de líneas procesadas: {sum(niveles.values())}")

        print("\nDistribución por nivel:")
        for nivel, count in niveles.most_common():
            print(f"  {nivel}: {count}")

        print("\nMensajes de ERROR más frecuentes:")
        for mensaje, count in errores.most_common(5):
            print(f"  [{count}] {mensaje}")

        if fechas:
            print(f"\nPrimer registro: {min(fechas)}")
            print(f"Último registro: {max(fechas)}")
            print(f"Duración del log: {max(fechas) - min(fechas)}")

        return {
            'niveles': niveles,
            'errores': errores,
            'fechas': fechas
        }

    except FileNotFoundError:
        print(f"Error: El archivo {ruta_archivo} no existe.")
        return None



# Esta sección es crucial para ejecutar el script directamente
if __name__ == "__main__":
    resultado = analizar_logs("app_server.log")
    # Si quieres usar los resultados para análisis adicional:
    if resultado:
        # Por ejemplo, puedes acceder a los contadores
        print("\nAcceso programático a los resultados:")
        print(f"Total de errores: {sum(resultado['errores'].values())}")