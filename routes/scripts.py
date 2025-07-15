import os
import json
import importlib.util
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify

bp_scripts = Blueprint('scripts', __name__)

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '../scripts')
SCRIPTS_CODE_DIR = os.path.join(SCRIPTS_DIR, 'code')

def load_script_config(script_name):
    path = os.path.join(SCRIPTS_DIR, f'{script_name}.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_script(script_name, target, aggressiveness_level):
    config = load_script_config(script_name)
    base_params = config.get('params', {}).get('default', {})
    aggr_params = config.get('params', {}).get('aggressiveness', {}).get(str(aggressiveness_level), {})

    # Combina parámetros
    combined_params = {**base_params, **aggr_params}

    # Sustituye {target} en todos los valores strings
    for k, v in combined_params.items():
        if isinstance(v, str) and '{target}' in v:
            combined_params[k] = v.replace('{target}', target)

    # Ruta absoluta para output
    combined_params['output_path'] = os.path.abspath(combined_params['output_path'])

    # Ejecutar script Python embebido
    script_path = os.path.join(SCRIPTS_CODE_DIR, config['python_file'])
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    result = module.main(combined_params)
    return result

@bp_scripts.route('/run_script/<script_name>', methods=['POST'])
def run_script_route(script_name):
    data = request.json
    target = data.get('target')
    aggressiveness = data.get('aggressiveness', 5)

    try:
        output_file = run_script(script_name, target, aggressiveness)
        return jsonify({"status": "ok", "output": output_file})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def build_command(command, params, arguments):
    all_parts = [command]
    if isinstance(params, dict):
        for k, v in params.items():
            all_parts.append(str(k))
            all_parts.append(str(v))
    elif isinstance(params, list):
        all_parts.extend(params)
    if isinstance(arguments, list):
        all_parts.extend(arguments)
    return ' '.join(all_parts)

def prepare_scripts(scripts):
    for script in scripts:
        aggr = script.get('params', {}).get('aggressiveness', {})
        script['aggressiveness_sorted'] = []

        try:
            if isinstance(aggr, dict):
                for level, params in aggr.items():
                    level_int = int(level)
                    cmd = build_command(script.get('command', ''), params, script.get('arguments', []))
                    script['aggressiveness_sorted'].append((level_int, cmd))
                script['aggressiveness_sorted'].sort()
        except Exception as e:
            current_app.logger.warning(f"[WARN] Error procesando agresividad para {script.get('name')}: {e}")
            script['aggressiveness_sorted'] = []

        try:
            default_params = script.get('params', {}).get('default', {})
            script['base_command'] = build_command(script.get('command', ''), default_params, script.get('arguments', []))
        except Exception:
            script['base_command'] = 'N/A'

    return scripts





@bp_scripts.route('/scripts')
def list_scripts():
    scripts = []
    for filename in os.listdir(SCRIPTS_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(SCRIPTS_DIR, filename), 'r', encoding='utf-8') as f:
                    script = json.load(f)

                script['filename'] = filename
                script['compatible'] = True

                if not script.get('name') or not script.get('command'):
                    script['compatible'] = False

                if shutil.which(script.get('command', '')) is None:
                    script['compatible'] = False

                if not isinstance(script.get('params', {}).get('aggressiveness', {}), dict):
                    script['compatible'] = False

                scripts.append(script)
            except Exception as e:
                current_app.logger.warning(f"[WARN] Script inválido: {filename}: {e}")
                script = {
                    'name': filename.replace('.json', ''),
                    'description': 'No se pudo cargar el script.',
                    'command': None,
                    'arguments': [],
                    'enabled': False,
                    'icon_color': '#dc3545',
                    'filename': filename,
                    'compatible': False,
                    'aggressiveness_sorted': []
                }
                scripts.append(script)

    scripts = prepare_scripts(scripts)
    return render_template('scripts.html', scripts=scripts)


@bp_scripts.route('/scripts/edit/<script_name>', methods=['GET', 'POST'])
def edit_script(script_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if request.method == 'POST':
        content = request.form.get('content')
        try:
            json_data = json.loads(content)
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(json_data, indent=2))
            flash('Script guardado correctamente.', 'success')
            return redirect(url_for('scripts.list_scripts'))
        except json.JSONDecodeError as e:
            flash(f'Error en JSON: {e}', 'danger')
            return render_template('edit_script.html', content=content, script_name=script_name)
    else:
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            content = ''
        return render_template('edit_script.html', content=content, script_name=script_name)
