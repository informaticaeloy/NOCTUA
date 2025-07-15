import os
import re
import socket
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

bp_vpn = Blueprint('vpn_profiles', __name__)
VPN_PROFILES_DIR = 'vpn_profiles'
VPN_STATUS_FILE = os.path.join(VPN_PROFILES_DIR, '.connectivity_status.json')

os.makedirs(VPN_PROFILES_DIR, exist_ok=True)

def load_statuses():
    if os.path.exists(VPN_STATUS_FILE):
        with open(VPN_STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_statuses(data):
    with open(VPN_STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_ovpn_info(filepath):
    info = {
        'remote': '',
        'proto': '',
        'cipher': '',
        'dev': '',
        'auth': ''
    }
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('remote '):
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        info['remote'] = f"{parts[1]}:{parts[2]}"
                elif line.startswith('proto '):
                    info['proto'] = line.strip().split()[1]
                elif line.startswith('cipher '):
                    info['cipher'] = line.strip().split()[1]
                elif line.startswith('dev '):
                    info['dev'] = line.strip().split()[1]
                elif line.startswith('auth '):
                    info['auth'] = line.strip().split()[1]
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
    return info

def test_connectivity(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        match = re.search(r'remote\s+([\w\.-]+)\s+(\d+)', content)
        if not match:
            return False, 'Host no definido'

        host, port = match.groups()
        port = int(port)

        with socket.create_connection((host, port), timeout=3):
            return True, f"{host}:{port} activo"
    except Exception as e:
        return False, str(e)

@bp_vpn.route('/vpn_profiles/')
def list_profiles():
    profiles = []
    statuses = load_statuses()

    for filename in os.listdir(VPN_PROFILES_DIR):
        if not filename.endswith('.ovpn'):
            continue

        full_path = os.path.join(VPN_PROFILES_DIR, filename)
        info = parse_ovpn_info(full_path)

        status_entry = statuses.get(filename)
        if status_entry:
            state = status_entry['status']
            date = status_entry['date']
        else:
            state = "No comprobado"
            date = ""

        profiles.append({
            'name': filename,
            'info': info,
            'status': state,
            'date': date
        })

    return render_template('vpn_profiles.html', profiles=profiles)

@bp_vpn.route('/vpn_profiles/check/<profile_name>', methods=['POST'])
def check_profile(profile_name):
    filepath = os.path.join(VPN_PROFILES_DIR, profile_name)
    if not os.path.exists(filepath):
        flash(f'Perfil "{profile_name}" no encontrado.', 'danger')
        return redirect(url_for('vpn_profiles.list_profiles'))

    alive, message = test_connectivity(filepath)
    statuses = load_statuses()
    statuses[profile_name] = {
        'status': "Activo" if alive else "Inaccesible",
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_statuses(statuses)

    flash(f'Conectividad de "{profile_name}": {statuses[profile_name]["status"]}', 'info')
    return redirect(url_for('vpn_profiles.list_profiles'))

@bp_vpn.route('/vpn_profiles/upload', methods=['POST'])
def upload_profile():
    file = request.files.get('profile')
    if not file or not file.filename.endswith('.ovpn'):
        flash('Archivo no válido', 'danger')
        return redirect(url_for('vpn_profiles.list_profiles'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(VPN_PROFILES_DIR, filename)

    if os.path.exists(filepath):
        flash('Este perfil ya existe.', 'warning')
        return redirect(url_for('vpn_profiles.list_profiles'))

    file.save(filepath)
    flash('Perfil subido correctamente.', 'success')
    return redirect(url_for('vpn_profiles.list_profiles'))

@bp_vpn.route('/vpn_profiles/delete/<profile_name>', methods=['POST'])
def delete_profile(profile_name):
    filepath = os.path.join(VPN_PROFILES_DIR, profile_name)
    statuses = load_statuses()

    if os.path.exists(filepath):
        os.remove(filepath)
        statuses.pop(profile_name, None)
        save_statuses(statuses)
        flash(f'Perfil "{profile_name}" eliminado.', 'success')
    else:
        flash(f'Perfil "{profile_name}" no encontrado.', 'danger')

    return redirect(url_for('vpn_profiles.list_profiles'))

