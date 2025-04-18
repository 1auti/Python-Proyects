"""
 Crea una API REST básica para gestionar una lista de tareas (todo list) usando Flask.
Requisitos:

Implementar endpoints para obtener, crear, actualizar y eliminar tareas
Estructura de tareas con ID, título, descripción, fecha límite y estado
Almacenamiento temporal en memoria (opcional: usar una base de datos simple como SQLite)
Manejar errores adecuadamente y devolver códigos de estado HTTP apropiados
"""

from flask import Flask, request, jsonify, abort
from datetime import datetime
import uuid

app = Flask(__name__)

# Almacenamiento en memoria para las tareas
tareas = {}


@app.route('/api/tareas', methods=['GET'])
def obtener_tareas():
    """Devuelve todas las tareas o las filtra por estado."""
    # Filtrar por estado si se proporciona como parámetro de consulta
    estado = request.args.get('estado')

    if estado:
        tareas_filtradas = {id_tarea: tarea for id_tarea, tarea in tareas.items()
                            if tarea['estado'].lower() == estado.lower()}
        return jsonify(list(tareas_filtradas.values()))

    return jsonify(list(tareas.values()))


@app.route('/api/tareas/<string:id_tarea>', methods=['GET'])
def obtener_tarea(id_tarea):
    """Devuelve una tarea específica por su ID."""
    if id_tarea not in tareas:
        abort(404, description=f"Tarea con ID {id_tarea} no encontrada")

    return jsonify(tareas[id_tarea])


@app.route('/api/tareas', methods=['POST'])
def crear_tarea():
    """Crea una nueva tarea."""
    if not request.json:
        abort(400, description="Los datos de la tarea deben estar en formato JSON")

    # Validar campos requeridos
    if 'titulo' not in request.json:
        abort(400, description="El título de la tarea es obligatorio")

    # Generar ID único
    id_tarea = str(uuid.uuid4())

    # Fecha actual como fecha de creación
    fecha_creacion = datetime.now().isoformat()

    # Crear tarea con valores predeterminados para campos opcionales
    tarea = {
        'id': id_tarea,
        'titulo': request.json['titulo'],
        'descripcion': request.json.get('descripcion', ''),
        'fecha_creacion': fecha_creacion,
        'fecha_limite': request.json.get('fecha_limite', None),
        'estado': request.json.get('estado', 'pendiente')
    }

    # Guardar la tarea
    tareas[id_tarea] = tarea

    return jsonify(tarea), 201


@app.route('/api/tareas/<string:id_tarea>', methods=['PUT'])
def actualizar_tarea(id_tarea):
    """Actualiza una tarea existente."""
    if id_tarea not in tareas:
        abort(404, description=f"Tarea con ID {id_tarea} no encontrada")

    if not request.json:
        abort(400, description="Los datos de actualización deben estar en formato JSON")

    tarea = tareas[id_tarea]

    # Actualizar campos si se proporcionan
    if 'titulo' in request.json:
        tarea['titulo'] = request.json['titulo']

    if 'descripcion' in request.json:
        tarea['descripcion'] = request.json['descripcion']

    if 'fecha_limite' in request.json:
        tarea['fecha_limite'] = request.json['fecha_limite']

    if 'estado' in request.json:
        tarea['estado'] = request.json['estado']

    return jsonify(tarea)


@app.route('/api/tareas/<string:id_tarea>', methods=['DELETE'])
def eliminar_tarea(id_tarea):
    """Elimina una tarea."""
    if id_tarea not in tareas:
        abort(404, description=f"Tarea con ID {id_tarea} no encontrada")

    tarea_eliminada = tareas.pop(id_tarea)

    return jsonify({'mensaje': f"Tarea '{tarea_eliminada['titulo']}' eliminada correctamente"})


@app.errorhandler(404)
def resource_not_found(e):
    """Manejador para recursos no encontrados."""
    return jsonify(error=str(e)), 404


@app.errorhandler(400)
def bad_request(e):
    """Manejador para solicitudes incorrectas."""
    return jsonify(error=str(e)), 400


# Opcional: Crear algunas tareas de ejemplo al iniciar
def crear_tareas_ejemplo():
    """Crea algunas tareas de ejemplo."""
    ejemplos = [
        {
            'titulo': 'Completar informe mensual',
            'descripcion': 'Preparar el informe de ventas del mes.',
            'fecha_limite': '2023-06-05T00:00:00',
            'estado': 'pendiente'
        },
        {
            'titulo': 'Reunión con cliente',
            'descripcion': 'Presentar propuesta de proyecto.',
            'fecha_limite': '2023-06-02T14:30:00',
            'estado': 'pendiente'
        },
        {
            'titulo': 'Actualizar sitio web',
            'descripcion': 'Subir nuevos productos y actualizar precios.',
            'fecha_limite': '2023-06-10T00:00:00',
            'estado': 'en_progreso'
        }
    ]

    for ejemplo in ejemplos:
        id_tarea = str(uuid.uuid4())
        ejemplo['id'] = id_tarea
        ejemplo['fecha_creacion'] = datetime.now().isoformat()
        tareas[id_tarea] = ejemplo


if __name__ == '__main__':
    crear_tareas_ejemplo()
    app.run(debug=True)

    # Con este comando en la terminal podes probar directamente : curl

    """
    curl -X POST http://127.0.0.1:5000/api/tareas -H "Content-Type: application/json" -d '{"titulo": "Nueva tarea", "descripcion": "Descripción de la tarea", "fecha_limite": "2025-12-31", "estado": "pendiente"}'
    
    curl -X PUT http://127.0.0.1:5000/api/tareas/<id_tarea> -H "Content-Type: application/json" -d '{"titulo": "Tarea actualizada", "estado": "en_progreso"}'

    curl -X DELETE http://127.0.0.1:5000/api/tareas/<id_tarea>
    
    curl http://127.0.0.1:5000/api/tareas

    """