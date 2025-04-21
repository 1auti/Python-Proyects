"""Descripción: Crea un programa que utilice concurrencia para procesar múltiples tareas de forma eficiente.
Requisitos:

Implementar procesamiento paralelo usando threads, procesos o asyncio
Crear un pool de workers para procesar tareas en paralelo
Manejar sincronización y comunicación entre procesos/threads
Implementar rate limiting y control de recursos"""

import asyncio
import aiohttp
import aiofiles
import time
import json
from datetime import datetime
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from queue import Queue
import logging
from functools import partial
import sys


class DescargadorConcurrente:
    """Clase para descargar múltiples URLs de forma concurrente usando diferentes métodos."""

    def __init__(self, urls, metodo='asyncio', max_workers=5):
        self.urls = urls
        self.metodo = metodo
        self.max_workers = max_workers
        self.resultados = []
        self.config_logging()

    def config_logging(self):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('descargador_concurrente.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def descargar_url_async(self, session, url):
        """Descarga una URL usando aiohttp (asyncio)."""
        try:
            inicio = time.time()
            async with session.get(url) as response:
                contenido = await response.text()
                duracion = time.time() - inicio

                self.logger.info(f"Descargado {url} en {duracion:.2f} segundos")

                return {
                    'url': url,
                    'status': response.status,
                    'size': len(contenido),
                    'duracion': duracion,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error al descargar {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def descargar_con_asyncio(self):
        """Método principal para descargar usando asyncio."""
        async with aiohttp.ClientSession() as session:
            tareas = []

            for url in self.urls:
                tarea = asyncio.create_task(self.descargar_url_async(session, url))
                tareas.append(tarea)

            # Limitar concurrencia usando semáforo
            semaforo = asyncio.Semaphore(self.max_workers)

            async def tarea_con_semaforo(tarea):
                async with semaforo:
                    return await tarea

            tareas_limitadas = [tarea_con_semaforo(tarea) for tarea in tareas]
            self.resultados = await asyncio.gather(*tareas_limitadas)

    def descargar_url_thread(self, url):
        """Descarga una URL usando requests (para threading)."""
        import requests

        try:
            inicio = time.time()
            response = requests.get(url, timeout=10)
            contenido = response.text
            duracion = time.time() - inicio

            self.logger.info(f"Descargado {url} en {duracion:.2f} segundos")

            return {
                'url': url,
                'status': response.status_code,
                'size': len(contenido),
                'duracion': duracion,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error al descargar {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def descargar_con_threads(self):
        """Descarga usando ThreadPoolExecutor."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            self.resultados = list(executor.map(self.descargar_url_thread, self.urls))

    def descargar_con_procesos(self):
        """Descarga usando ProcessPoolExecutor."""
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            self.resultados = list(executor.map(self.descargar_url_thread, self.urls))

    def ejecutar(self):
        """Ejecuta el método de descarga seleccionado."""
        inicio_total = time.time()

        if self.metodo == 'asyncio':
            asyncio.run(self.descargar_con_asyncio())
        elif self.metodo == 'threads':
            self.descargar_con_threads()
        elif self.metodo == 'procesos':
            self.descargar_con_procesos()
        else:
            raise ValueError(f"Método no soportado: {self.metodo}")

        duracion_total = time.time() - inicio_total
        self.logger.info(f"Descarga total completada en {duracion_total:.2f} segundos usando {self.metodo}")

        return self.resultados


class ProcesamientoConcurrente:
    """Clase para demostrar diferentes técnicas de procesamiento concurrente."""

    def __init__(self):
        self.cola_tareas = Queue()
        self.resultados = []
        self.lock = threading.Lock()

    def tarea_cpu_intensiva(self, datos):
        """Simula una tarea que consume mucha CPU."""
        resultado = 0
        for i in range(datos['inicio'], datos['fin']):
            resultado += i * i

        return {
            'id': datos['id'],
            'resultado': resultado,
            'tiempo_proceso': time.time()
        }

    def productor(self, num_tareas=10):
        """Función productora que genera tareas."""
        for i in range(num_tareas):
            tarea = {
                'id': i,
                'inicio': i * 1000,
                'fin': (i + 1) * 1000
            }
            self.cola_tareas.put(tarea)
            logging.info(f"Tarea {i} agregada a la cola")

        # Señal de finalización
        for _ in range(multiprocessing.cpu_count()):
            self.cola_tareas.put(None)

    def consumidor(self):
        """Función consumidora que procesa tareas."""
        while True:
            tarea = self.cola_tareas.get()

            if tarea is None:
                self.cola_tareas.task_done()
                break

            resultado = self.tarea_cpu_intensiva(tarea)

            with self.lock:
                self.resultados.append(resultado)

            logging.info(f"Tarea {tarea['id']} completada")
            self.cola_tareas.task_done()

    def procesar_con_threads(self, num_tareas=10):
        """Procesamiento usando múltiples threads."""
        productor_thread = threading.Thread(target=self.productor, args=(num_tareas,))
        productor_thread.start()

        consumidores = []
        for i in range(multiprocessing.cpu_count()):
            consumidor_thread = threading.Thread(target=self.consumidor)
            consumidor_thread.start()
            consumidores.append(consumidor_thread)

        productor_thread.join()
        self.cola_tareas.join()

        for consumidor in consumidores:
            consumidor.join()

        return self.resultados


class ProcesadorAsyncIO:
    """Procesador que utiliza asyncio para tareas IO-bound."""

    def __init__(self, rate_limit=5):
        self.semaforo = asyncio.Semaphore(rate_limit)
        self.resultados = []

    async def procesar_url(self, session, url):
        """Procesa una URL con rate limiting."""
        async with self.semaforo:
            try:
                async with session.get(url) as response:
                    contenido = await response.text()
                    return {
                        'url': url,
                        'status': response.status,
                        'tamaño': len(contenido),
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                return {
                    'url': url,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }

    async def procesar_urls(self, urls):
        """Procesa múltiples URLs concurrentemente."""
        async with aiohttp.ClientSession() as session:
            tareas = []

            for url in urls:
                tarea = asyncio.create_task(self.procesar_url(session, url))
                tareas.append(tarea)

            self.resultados = await asyncio.gather(*tareas)
            return self.resultados


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo 1: Descargador concurrente
    urls = [
        'https://example.com',
        'https://github.com',
        'https://python.org',
        'https://google.com',
        'https://stackoverflow.com'
    ]

    # Probar diferentes métodos
    for metodo in ['asyncio', 'threads', 'procesos']:
        print(f"\n=== Probando con {metodo} ===")
        descargador = DescargadorConcurrente(urls, metodo=metodo, max_workers=3)
        resultados = descargador.ejecutar()

        # Guardar resultados
        with open(f'resultados_{metodo}.json', 'w') as f:
            json.dump(resultados, f, indent=4)

    # Ejemplo 2: Procesamiento concurrente con productor-consumidor
    print("\n=== Procesamiento con threads ===")
    procesador = ProcesamientoConcurrente()
    resultados_threads = procesador.procesar_con_threads(20)
    print(f"Procesadas {len(resultados_threads)} tareas")

    # Ejemplo 3: AsyncIO con rate limiting
    print("\n=== AsyncIO con rate limiting ===")
    procesador_async = ProcesadorAsyncIO(rate_limit=3)
    resultados_async = asyncio.run(procesador_async.procesar_urls(urls))
    print(f"URLs procesadas: {len(resultados_async)}")