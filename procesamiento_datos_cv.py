"""
Procesamiento de Datos CSV
Descripción: Desarrolla un script para procesar archivos CSV que contengan datos de ventas, realizar análisis estadísticos y generar informes.
Requisitos:

Leer datos de un archivo CSV con información de ventas (fecha, producto, cantidad, precio, etc.)
Calcular estadísticas como ventas totales, productos más vendidos, ingresos por mes
Generar un informe en formato CSV o HTML
Crear visualizaciones básicas (opcional)
"""

import csv
from datetime import datetime
from collections import defaultdict
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


class ProcesadorVentas:
    """Clase para procesar datos de ventas desde archivos CSV"""

    def __init__(self, ruta_archivo):
        """Inicializa el procesador con la ruta del archivo CSV"""
        self.ruta_archivo = ruta_archivo
        self.datos = []
        self.productos = defaultdict(int)
        self.ventas_por_mes = defaultdict(float)
        self.ventas_por_categoria = defaultdict(float)

    def cargar_datos(self):
        """Carga los datos desde el archivo CSV"""
        try:
            with open(self.ruta_archivo, 'r', newline='', encoding='utf-8') as archivo_csv:
                lector = csv.DictReader(archivo_csv)
                for fila in lector:
                    # Convertir tipo de datos
                    fila['cantidad'] = int(fila['cantidad'])
                    fila['precio'] = float(fila['precio'])
                    fila['fecha'] = datetime.strptime(fila['fecha'], '%Y-%m-%d')

                    # Calcular el total de las ventas
                    fila['total'] = fila['cantidad'] * fila['precio']

                    self.datos.append(fila)
            return True
        except Exception as e:
            print(f"Error al cargar los datos: {e}")
            return False

    def analizar_datos(self):
        """Realiza análisis estadístico sobre los datos de ventas"""
        if not self.datos:
            return False

        # Reiniciar contadores
        self.productos = defaultdict(int)
        self.ventas_por_mes = defaultdict(float)
        self.ventas_por_categoria = defaultdict(float)

        # Procesar cada venta
        for venta in self.datos:
            # Contar productos vendidos
            self.productos[venta['producto']] += venta['cantidad']

            # Sumar ventas por mes
            mes_clave = venta['fecha'].strftime('%Y-%m')
            self.ventas_por_mes[mes_clave] += venta['total']

            # Sumar ventas por categoría
            self.ventas_por_categoria[venta['categoria']] += venta['total']

        return True

    def obtener_estadisticas(self):
        """Devuelve un diccionario con estadísticas de ventas."""
        if not self.datos:
            return None

        # Calcular estadísticas generales
        total_ventas = sum(venta['total'] for venta in self.datos)
        cantidad_total = sum(venta['cantidad'] for venta in self.datos)

        # Productos más vendidos
        productos_ordenados = sorted(
            self.productos.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Meses con más ventas
        meses_ordenados = sorted(
            self.ventas_por_mes.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Categorías más vendidas
        categorias_ordenadas = sorted(
            self.ventas_por_categoria.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            'total_ventas': total_ventas,
            'cantidad_total': cantidad_total,
            'productos_top': productos_ordenados[:5],
            'meses_top': meses_ordenados,
            'categorias': categorias_ordenadas
        }

    def generar_informe_csv(self, ruta_salida):
        """Genera un informe CSV con las estadísticas."""
        estadisticas = self.obtener_estadisticas()
        if not estadisticas:
            return False

        try:
            with open(ruta_salida, 'w', newline='', encoding='utf-8') as archivo_csv:
                escritor = csv.writer(archivo_csv)

                # Encabezado
                escritor.writerow(['Informe de Ventas', '', ''])
                escritor.writerow(['', '', ''])

                # Estadísticas generales
                escritor.writerow(['Estadísticas Generales', '', ''])
                escritor.writerow(['Total de ventas ($)', f"{estadisticas['total_ventas']:.2f}", ''])
                escritor.writerow(['Cantidad de productos vendidos', estadisticas['cantidad_total'], ''])
                escritor.writerow(['', '', ''])

                # Productos más vendidos
                escritor.writerow(['Productos más vendidos', '', ''])
                escritor.writerow(['Producto', 'Cantidad', ''])
                for producto, cantidad in estadisticas['productos_top']:
                    escritor.writerow([producto, cantidad, ''])
                escritor.writerow(['', '', ''])

                # Ventas por mes
                escritor.writerow(['Ventas por mes', '', ''])
                escritor.writerow(['Mes', 'Ventas ($)', ''])
                for mes, ventas in estadisticas['meses_top']:
                    mes_formateado = datetime.strptime(mes, '%Y-%m').strftime('%B %Y')
                    escritor.writerow([mes_formateado, f"{ventas:.2f}", ''])
                escritor.writerow(['', '', ''])

                # Ventas por categoría
                escritor.writerow(['Ventas por categoría', '', ''])
                escritor.writerow(['Categoría', 'Ventas ($)', ''])
                for categoria, ventas in estadisticas['categorias']:
                    escritor.writerow([categoria, f"{ventas:.2f}", ''])

            return True
        except Exception as e:
            print(f"ERROR al generar el informe de CSV: {e}")
            return False

    def generar_informe_html(self, ruta_salida):
        """Genera un informe HTML con las estadísticas."""
        estadisticas = self.obtener_estadisticas()
        if not estadisticas:
            return False

        try:
            with open(ruta_salida, 'w', encoding='utf-8') as archivo_html:
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Informe de Ventas</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        h2 {{ color: #3498db; margin-top: 20px; }}
                        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    </style>
                </head>
                <body>
                    <h1>Informe de Ventas</h1>

                    <h2>Estadísticas Generales</h2>
                    <table>
                        <tr>
                            <th>Métrica</th>
                            <th>Valor</th>
                        </tr>
                        <tr>
                            <td>Total de ventas ($)</td>
                            <td>{estadisticas['total_ventas']:.2f}</td>
                        </tr>
                        <tr>
                            <td>Cantidad de productos vendidos</td>
                            <td>{estadisticas['cantidad_total']}</td>
                        </tr>
                    </table>

                    <h2>Productos más vendidos</h2>
                    <table>
                        <tr>
                            <th>Producto</th>
                            <th>Cantidad</th>
                        </tr>
                """

                for producto, cantidad in estadisticas['productos_top']:
                    html += f"""
                        <tr>
                            <td>{producto}</td>
                            <td>{cantidad}</td>
                        </tr>
                    """

                html += """
                    </table>

                    <h2>Ventas por mes</h2>
                    <table>
                        <tr>
                            <th>Mes</th>
                            <th>Ventas ($)</th>
                        </tr>
                """

                for mes, ventas in estadisticas['meses_top']:
                    mes_formateado = datetime.strptime(mes, '%Y-%m').strftime('%B %Y')
                    html += f"""
                        <tr>
                            <td>{mes_formateado}</td>
                            <td>{ventas:.2f}</td>
                        </tr>
                    """

                html += """
                    </table>

                    <h2>Ventas por categoría</h2>
                    <table>
                        <tr>
                            <th>Categoría</th>
                            <th>Ventas ($)</th>
                        </tr>
                """

                for categoria, ventas in estadisticas['categorias']:
                    html += f"""
                        <tr>
                            <td>{categoria}</td>
                            <td>{ventas:.2f}</td>
                        </tr>
                    """

                html += """
                    </table>
                </body>
                </html>
                """

                archivo_html.write(html)

            return True
        except Exception as e:
            print(f"Error al generar el informe HTML: {e}")
            return False

    def generar_graficos(self, directorio_salida):
        """Genera gráficos de visualización de las estadísticas."""
        estadisticas = self.obtener_estadisticas()
        if not estadisticas or not os.path.exists(directorio_salida):
            return False

        try:
            # Gráfico de productos más vendidos
            productos = [p[0] for p in estadisticas['productos_top'][:5]]
            cantidades = [p[1] for p in estadisticas['productos_top'][:5]]

            plt.figure(figsize=(10, 6))
            plt.bar(productos, cantidades, color='skyblue')
            plt.title('Productos más vendidos')
            plt.xlabel('Producto')
            plt.ylabel('Cantidad')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(directorio_salida, 'productos_top.png'))
            plt.close()

            # Gráfico de ventas por mes
            meses = [datetime.strptime(m[0], '%Y-%m').strftime('%b %Y') for m in estadisticas['meses_top']]
            ventas_mes = [m[1] for m in estadisticas['meses_top']]

            plt.figure(figsize=(12, 6))
            plt.plot(meses, ventas_mes, marker='o', linestyle='-', color='green')
            plt.title('Ventas por Mes')
            plt.xlabel('Mes')
            plt.ylabel('Ventas ($)')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(directorio_salida, 'ventas_por_mes.png'))
            plt.close()

            # Gráfico de ventas por categoría
            categorias = [c[0] for c in estadisticas['categorias']]
            ventas_cat = [c[1] for c in estadisticas['categorias']]

            plt.figure(figsize=(10, 7))
            plt.pie(ventas_cat, labels=categorias, autopct='%1.1f%%', startangle=140, shadow=True)
            plt.title('Distribución de Ventas por Categoría')
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.tight_layout()
            plt.savefig(os.path.join(directorio_salida, 'ventas_por_categoria.png'))
            plt.close()

            return True
        except Exception as e:
            print(f"Error al generar los gráficos: {e}")
            return False


# Ejemplo de uso
if __name__ == "__main__":
    # Crear un CSV de ejemplo si no existe
    if not os.path.exists('ventas.csv'):
        with open('ventas.csv', 'w', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerow(['fecha', 'producto', 'categoria', 'cantidad', 'precio'])
            escritor.writerow(['2023-01-15', 'Laptop HP', 'Electrónica', 2, 899.99])
            escritor.writerow(['2023-01-20', 'Mouse Logitech', 'Accesorios', 5, 29.99])
            escritor.writerow(['2023-02-05', 'Teclado Mecánico', 'Accesorios', 3, 89.99])
            escritor.writerow(['2023-02-10', 'Monitor 27"', 'Electrónica', 2, 249.99])
            escritor.writerow(['2023-03-01', 'Laptop Dell', 'Electrónica', 1, 1299.99])
            escritor.writerow(['2023-03-15', 'Audífonos Sony', 'Audio', 4, 79.99])
            escritor.writerow(['2023-04-02', 'Smartphone Samsung', 'Móviles', 3, 699.99])
            escritor.writerow(['2023-04-20', 'Tablet iPad', 'Electrónica', 2, 499.99])
            escritor.writerow(['2023-05-10', 'Cámara Canon', 'Fotografía', 1, 649.99])
            escritor.writerow(['2023-05-25', 'Impresora HP', 'Oficina', 2, 199.99])

    # Crear directorio para gráficos si no existe
    if not os.path.exists('reportes'):
        os.makedirs('reportes')

    # Procesar ventas
    procesador = ProcesadorVentas('ventas.csv')
    if procesador.cargar_datos():
        procesador.analizar_datos()

        # Generar informes
        procesador.generar_informe_csv('reportes/informe_ventas.csv')
        procesador.generar_informe_html('reportes/informe_ventas.html')

        # Generar gráficos
        procesador.generar_graficos('reportes')

        print("Informes y gráficos generados en la carpeta 'reportes'")
    else:
        print("No se pudieron cargar los datos de ventas")