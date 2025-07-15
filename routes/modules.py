import os
import json
import copy

from flask import Blueprint, render_template, current_app

bp_modules = Blueprint('modules', __name__)

MODULES_DIR = os.path.join(os.path.dirname(__file__), '../modules')  # Ajusta ruta según tu estructura

def load_modules():
    modules = []
    for filename in os.listdir(MODULES_DIR):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(MODULES_DIR, filename)
        mod = None
        compatible = True
        error_msg = None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                mod = json.load(f)
            # Validación básica
            if not ('name' in mod and 'command' in mod and 'params' in mod):
                compatible = False
                error_msg = "Faltan claves necesarias"
        except Exception as e:
            compatible = False
            error_msg = f"Error JSON: {e}"
            # Cargar datos mínimos para mostrar el módulo como erróneo
            mod = {
                "name": filename,
                "description": error_msg or "JSON inválido",
                "command": "",
                "params": {},
                "enabled": False,
                "icon_color": "#dc3545"  # rojo bootstrap
            }
        mod['compatible'] = compatible
        modules.append(mod)
    return modules



def prepare_modules(modules):
    for mod in modules:
        aggr = mod.get('params', {}).get('aggressiveness', {})
        aggr_sorted = []
        for level_str, params_list in sorted(aggr.items(), key=lambda x: int(x[0])):
            args = mod.get('arguments', [])
            full_cmd_parts = [mod['command']] + params_list + args
            full_cmd = ' '.join(full_cmd_parts)
            aggr_sorted.append((level_str, full_cmd))
        mod['aggressiveness_sorted'] = aggr_sorted
        # Hacer copia profunda para evitar referencias circulares
        mod['raw_json'] = copy.deepcopy(mod)
    return modules

@bp_modules.route('/modules')
def list_modules():
    modules = load_modules()
    modules = prepare_modules(modules)
    return render_template('modules.html', modules=modules)

