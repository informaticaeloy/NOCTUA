import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, abort

from utils.utils import load_scan, load_all_scans, save_scan
from routes.scanner import start_scan_modules, load_module_config, build_command


bp_api = Blueprint('scan_api', __name__)

#SCANS_DIR = './scans'




# Listar todos los escaneos
@bp_api.route('/scans', methods=['GET'])
def list_scans():
    scans = load_all_scans()
    return jsonify({'scans': scans})


# Añadir un nuevo escaneo
@bp_api.route('/scans', methods=['POST'])
def add_scan():

    data = request.get_json()
    target = data.get('target', '').strip()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    modules = data.get('modules', [])
    aggressiveness = data.get('aggressiveness')

    if not target:
        return jsonify({'error': 'Target requerido'}), 400
    if not isinstance(modules, list) or not modules:
        return jsonify({'error': 'Debe seleccionar al menos un módulo'}), 400
    if not isinstance(aggressiveness, int) or not (0 <= aggressiveness <= 10):
        return jsonify({'error': 'Agresividad inválida'}), 400

    scan_id = str(uuid.uuid4())[:8]
    folder_name = f"{target}_{scan_id}".replace("://", "_").replace("/", "_")

    os.makedirs(SCANS_DIR, exist_ok=True)
    scan_folder = os.path.join(SCANS_DIR, folder_name)
    os.makedirs(scan_folder, exist_ok=True)

    now = datetime.utcnow().isoformat()

    '''scan_data = {
        'id': scan_id,
        'name': name,
        'description': description,
        'target': target,
        'modules': modules,
        'modules_running': modules.copy(),  # Lista de módulos pendientes o en ejecución
        'completed_modules': 0,  # Contador de módulos finalizados
        'aggressiveness': aggressiveness,
        'created_at': now,
        'status': 'pending',  # Estado inicial
        'progress': 0,
        'folder_name': folder_name
    }'''

    flow = data.get('flow', [])

    scan_data = {
        'id': scan_id,
        'name': name,
        'description': description,
        'target': target,
        'modules': modules,
        'flow': flow,
        'modules_running': modules.copy(),
        'completed_modules': 0,
        'aggressiveness': aggressiveness,
        'created_at': now,
        'status': 'pending',
        'progress': 0,
        'folder_name': folder_name
    }
    ### save_scan(scan_data, scan_folder)
    #scan_file = os.path.join(scan_folder, 'scan_info.json')
    #with open(scan_file, 'w') as f:
    #    import json
    #    json.dump(scan_data, f, indent=2)
    save_scan(scan_data, scan_folder)

    return jsonify({'scan_id': scan_id}), 201

# Obtener detalle de un escaneo
@bp_api.route('/scans/<scan_id>', methods=['GET'])
def get_scan(scan_id):
    scan_data, _ = load_scan(scan_id)
    if not scan_data:
        abort(404, description='Escaneo no encontrado')
    return jsonify(scan_data)

# Iniciar escaneo
@bp_api.route('/scans/<scan_id>/start', methods=['POST'])
def start_scan(scan_id):
    scan_data, scan_folder = load_scan(scan_id)
    if not scan_data:
        abort(404, description='Escaneo no encontrado')

    if scan_data['status'] == 'running':
        return jsonify({'message': 'Escaneo ya está en ejecución'}), 400

    data = request.get_json()
    modules_to_run = data.get('modules')
    if not modules_to_run or not isinstance(modules_to_run, list):
        return jsonify({'error': 'Lista de módulos inválida o vacía'}), 400

    # Actualiza el estado y reinicia progreso
    scan_data['status'] = 'running'
    scan_data['progress'] = 0
    scan_data['modules_running'] = modules_to_run  # Guarda los módulos en ejecución (opcional)
    save_scan(scan_data, scan_folder)

    # Aquí lanzarías el proceso real en background con modules_to_run
    from threading import Thread
    from routes.scanner import start_scan_sequence  # función que debes tener definida

    def worker():
        target = scan_data['target']
        aggr = scan_data.get('aggressiveness', 0)
        start_scan_modules(scan_folder, modules_to_run, target, aggr)

    Thread(target=worker).start()
    return jsonify({'message': 'Escaneo iniciado', 'modules': modules_to_run})


# Pausar escaneo
@bp_api.route('/scans/<scan_id>/pause', methods=['POST'])
def pause_scan(scan_id):
    scan_data, scan_folder = load_scan(scan_id)
    if not scan_data:
        abort(404, description='Escaneo no encontrado')
    if scan_data['status'] != 'running':
        return jsonify({'message': 'Escaneo no está en ejecución'}), 400

    scan_data['status'] = 'paused'
    save_scan(scan_data, scan_folder)
    # Aquí implementarías la lógica para pausar el proceso real
    return jsonify({'message': 'Escaneo pausado'})

# Detener escaneo
@bp_api.route('/scans/<scan_id>/stop', methods=['POST'])
def stop_scan(scan_id):
    scan_data, scan_folder = load_scan(scan_id)
    if not scan_data:
        abort(404, description='Escaneo no encontrado')
    if scan_data['status'] not in ['running', 'paused']:
        return jsonify({'message': 'Escaneo no está activo'}), 400

    scan_data['status'] = 'stopped'
    save_scan(scan_data, scan_folder)
    # Aquí implementarías lógica para detener proceso real
    return jsonify({'message': 'Escaneo detenido'})

# Eliminar escaneo
@bp_api.route('/scans/<scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    scan_data, scan_folder = load_scan(scan_id)
    if not scan_data:
        abort(404, description='Escaneo no encontrado')
    try:
        # Borrado de carpeta completa
        import shutil
        shutil.rmtree(scan_folder)
        return jsonify({'message': 'Escaneo eliminado'})
    except Exception as e:
        return jsonify({'error': f'Error al eliminar: {str(e)}'}), 500
