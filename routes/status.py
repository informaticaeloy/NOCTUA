from flask import Blueprint, render_template
import shutil
import subprocess
import json
import os

bp_status = Blueprint('status', __name__)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/dependencies.json')

def load_tools_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo leer el fichero de dependencias: {e}")
        return {}

def check_dependency(tool, command, max_chars=80):
    path = shutil.which(command[0])
    if not path:
        return {
            'available': False,
            'path': None,
            'version_full': 'No disponible',
            'version_short': 'No disponible'
        }
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=5)
        version_full = result.stdout.strip()
        version_short = version_full[:max_chars] + ('...' if len(version_full) > max_chars else '')
    except Exception:
        version_full = 'Error al obtener versión'
        version_short = version_full
    return {
        'available': True,
        'path': path,
        'version_full': version_full,
        'version_short': version_short
    }


@bp_status.route('/status')
def status_check():
    tools_to_check = load_tools_config()
    status = {
        tool: check_dependency(tool, cmd)
        for tool, cmd in tools_to_check.items()
    }
    return render_template('status.html', status=status)

