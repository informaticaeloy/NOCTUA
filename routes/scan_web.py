from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import json
import uuid
from datetime import datetime
from utils.utils import load_all_scans

bp_web = Blueprint('scan_web', __name__)

SCANS_DIR = './scans'
MODULES_DIR = './modules'
SCRIPTS_DIR = './scripts'


@bp_web.route('/')
def index():
    scans = load_all_scans()

    # Cargar módulos con nombre real, icono, color y estado
    modules_info = {}
    try:
        for f in os.listdir(MODULES_DIR):
            if f.endswith('.json') and not f.startswith('__'):
                try:
                    with open(os.path.join(MODULES_DIR, f), 'r', encoding='utf-8') as mf:
                        data = json.load(mf)
                    name_real = data.get('name', os.path.splitext(f)[0])
                    icon = data.get('icon', 'fa-cube')
                    icon_color = data.get('icon_color', '#0d6efd')
                    modules_info[name_real] = {
                        'icon': icon,
                        'icon_color': icon_color,
                        'filename': f,
                        'valid': True,
                        'error': None
                    }
                except Exception as e:
                    modules_info[os.path.splitext(f)[0]] = {
                        'icon': 'fa-cube',
                        'icon_color': '#6c757d',
                        'valid': False,
                        'error': str(e),
                        'filename': f
                    }
    except FileNotFoundError:
        pass

    # Cargar scripts con nombre real, icono, color y estado
    scripts_info = {}
    try:
        for f in os.listdir(SCRIPTS_DIR):
            if f.endswith('.json') and not f.startswith('__'):
                try:
                    with open(os.path.join(SCRIPTS_DIR, f), 'r', encoding='utf-8') as sf:
                        data = json.load(sf)
                    name_real = data.get('name', os.path.splitext(f)[0])
                    icon = data.get('icon', 'fa-cube')
                    icon_color = data.get('icon_color', '#198754')
                    scripts_info[name_real] = {
                        'icon': icon,
                        'icon_color': icon_color,
                        'filename': f,
                        'valid': True,
                        'error': None
                    }
                except Exception as e:
                    scripts_info[os.path.splitext(f)[0]] = {
                        'icon': 'fa-cube',
                        'icon_color': '#6c757d',
                        'valid': False,
                        'error': str(e),
                        'filename': f
                    }
    except FileNotFoundError:
        pass

    return render_template(
        'index.html',
        scans=scans,
        modules_info=modules_info,
        scripts_info=scripts_info,
        enumerate=enumerate  # Necesario para Jinja
    )



@bp_web.route('/new_scan', methods=['GET', 'POST'])
def new_scan():
    modules_available = []
    try:
        for f in os.listdir(MODULES_DIR):
            if f.endswith('.json') and not f.startswith('__'):
                path = os.path.join(MODULES_DIR, f)
                try:
                    with open(path, encoding='utf-8') as mf:
                        data = json.load(mf)
                        modules_available.append({
                            'name': data.get('name', os.path.splitext(f)[0]),
                            'icon_color': data.get('icon_color', '#0d6efd'),
                            'icon': data.get('icon', 'fa-cube'),
                            'valid': True
                        })
                except Exception as e:
                    modules_available.append({
                        'name': os.path.splitext(f)[0],
                        'valid': False,
                        'error': str(e),
                        'icon_color': '#6c757d',
                        'icon': 'fa-exclamation-circle'
                    })
        modules_available.sort(key=lambda m: m['name'].lower())
    except FileNotFoundError:
        modules_available = []

    scripts_available = []
    try:
        for f in os.listdir(SCRIPTS_DIR):
            if f.endswith('.json') and not f.startswith('__'):
                path = os.path.join(SCRIPTS_DIR, f)
                try:
                    with open(path, encoding='utf-8') as sf:
                        data = json.load(sf)
                        scripts_available.append({
                            'name': data.get('name', os.path.splitext(f)[0]),
                            'icon_color': data.get('icon_color', '#198754'),
                            'icon': data.get('icon', 'fa-cube'),
                            'valid': True
                        })
                except Exception as e:
                    scripts_available.append({
                        'name': os.path.splitext(f)[0],
                        'valid': False,
                        'error': str(e),
                        'icon_color': '#6c757d',
                        'icon': 'fa-exclamation-circle'
                    })
        scripts_available.sort(key=lambda s: s['name'].lower())
    except FileNotFoundError:
        scripts_available = []

    if request.method == 'POST':
        scan_name = request.form.get('scan_name', '').strip()
        description = request.form.get('description', '').strip()
        target = request.form.get('target', '').strip()
        flow_raw = request.form.get("flow", "[]")

        if not scan_name:
            flash('Debe indicar un nombre para el escaneo', 'danger')
            return redirect(url_for('scan_web.new_scan'))

        if not target:
            flash('Debe indicar un dominio o IP', 'danger')
            return redirect(url_for('scan_web.new_scan'))

        try:
            flow = json.loads(flow_raw)
            if not flow:
                raise ValueError("Flujo vacío")
        except Exception:
            flash('Error al interpretar el flujo del escaneo', 'danger')
            return redirect(url_for('scan_web.new_scan'))

        try:
            aggressiveness = int(request.form.get('aggressiveness', 5))
            if not (0 <= aggressiveness <= 10):
                raise ValueError()
        except ValueError:
            flash('Valor de agresividad inválido', 'danger')
            return redirect(url_for('scan_web.new_scan'))

        # Validación de elementos del flujo
        valid_names = set(
            [m['name'] for m in modules_available if m.get('valid')] +
            [s['name'] for s in scripts_available if s.get('valid')]
        )
        for step in flow:
            if step['name'] not in valid_names:
                flash(f'Elemento inválido en el flujo: {step["name"]}', 'danger')
                return redirect(url_for('scan_web.new_scan'))

        # Guardar escaneo
        scan_id = str(uuid.uuid4())[:8]
        folder_name = f"{target}_{scan_id}".replace("://", "_").replace("/", "_")
        scan_folder = os.path.join(SCANS_DIR, folder_name)
        os.makedirs(scan_folder, exist_ok=True)

        scan_data = {
            'id': scan_id,
            'name': scan_name,
            'description': description,
            'target': target,
            'flow': flow,
            'aggressiveness': aggressiveness,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending',
            'progress': 0,
            'folder_name': folder_name
        }

        with open(os.path.join(scan_folder, 'scan_info.json'), 'w', encoding='utf-8') as f:
            json.dump(scan_data, f, indent=2)

        flash(f'Escaneo creado con ID: {scan_id}', 'success')
        return redirect(url_for('scan_web.index'))

    return render_template(
        'new_scan.html',
        modules=modules_available,
        scripts=scripts_available
    )


@bp_web.route('/delete/<scan_id>')
def delete_scan(scan_id):
    target_folder = None
    scans = load_all_scans()
    for scan in scans:
        if scan.get('id') == scan_id:
            target_folder = scan.get('folder_name')
            break

    if target_folder:
        try:
            full_path = os.path.join(SCANS_DIR, target_folder)
            if os.path.exists(full_path):
                for root, dirs, files in os.walk(full_path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(full_path)
            flash(f'Escaneo {scan_id} eliminado correctamente.', 'success')
        except Exception as e:
            flash(f'Error al eliminar el escaneo: {e}', 'danger')
    else:
        flash('Escaneo no encontrado.', 'warning')

    return redirect(url_for('scan_web.index'))

