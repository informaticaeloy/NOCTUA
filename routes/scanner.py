import json
import os
import subprocess
import threading
from datetime import datetime

# Ruta base donde están los módulos (relativa al proyecto)
MODULES_DIR = os.path.join(os.path.dirname(__file__), '..', 'modules')



# start_scan_sequence()
# └──▶ start_scan_modules()
#      └──▶ load_module_config()           ← se llama por cada módulo
#      └──▶ build_command()
#      └──▶ run_command_and_log_sync()
#           ├──▶ log_scan_event()  ← al inicio
#           ├──▶ subprocess.run()  ← ejecución real del comando
#           ├──▶ log_scan_event()  ← al final




def start_scan_modules(scan_folder, modules, target, aggressiveness):
    """
    Carga la configuración de un módulo desde su archivo JSON correspondiente.
    """
    print(f"[?] LLEGO A START_SCAN_MODULES")
    for module in modules:
        print(f"[?] Procesando módulo: {module} (tipo: {type(module)})")
        try:
            # Si es dict, usa solo el nombre
            module_name = module['name'] if isinstance(module, dict) else module
            config = load_module_config(module_name)
            cmd = build_command(config, target, aggressiveness)
            print(f"[->] Comando generado: {cmd}")
            success = run_command_and_log_sync(config, cmd, scan_folder, target)

            if not success:
                print(f"[!] Fallo en módulo {module_name}, abortando ejecución secuencial.")
                break
        except Exception as e:
            print(f"[!] Error iniciando módulo {module}: {e}")
            break


def load_module_config(module_name):
    """
    Carga la configuración de un módulo desde su archivo JSON correspondiente.
    """
    print(f"[?] LLEGO A LOAD_MODULE_CONFIG")

    module_file = os.path.join(MODULES_DIR, f'{module_name}.json')
    if not os.path.isfile(module_file):
        raise FileNotFoundError(f"Módulo no encontrado: {module_name}")
    with open(module_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_command(module_config, target, aggressiveness):
    """
    Construye la lista de argumentos para ejecutar el módulo con el target y nivel de agresividad indicados.
    """
    print(f"[?] LLEGO A BUILD_COMMAND")

    cmd = [module_config['command']]

    # === Parámetros según agresividad ===
    params = module_config.get('params', {})
    aggr_params = params.get('aggressiveness', {})
    default_params = params.get('default', [])

    # Buscar la clave más cercana a la agresividad actual
    if aggr_params:
        aggr_keys = list(map(int, aggr_params.keys()))
        closest = min(aggr_keys, key=lambda k: abs(k - aggressiveness))
        param_list = aggr_params.get(str(closest), default_params)
    else:
        param_list = default_params

    cmd.extend(param_list)

    # === Sustituir {target} en los argumentos ===
    args = module_config.get('arguments', target)
    if isinstance(args, str):
        cmd.append(args.replace("{target}", target))
    elif isinstance(args, list):
        cmd.extend([a.replace("{target}", target) for a in args])
    else:
        cmd.append(target)

    print(f"[->] Comando generado: {cmd}")
    return cmd


def log_scan_event(scan_folder, module_name, status):
    """
    Registra eventos de ejecución de módulos en un log común del escaneo.
    """
    print(f"[?] LLEGO A LOG_SCAN_EVENT")

    log_path = os.path.join(scan_folder, 'execution.log')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"[{timestamp}] {module_name}: {status}\n")


def run_command_and_log_sync(module_config, command, scan_folder, target):
    """
    Ejecuta el comando, guarda la salida en su output y registra inicio y fin en log.
    Actualiza el progreso del escaneo y el estado final.
    """
    print(f"[?] LLEGO A RUN_COMMAND_AND_LOG_SYNC")

    # Soporte flexible de campo "output"
    output_config = module_config.get('output', {})
    if isinstance(output_config, dict):
        raw_path = output_config.get('path', f"{module_config.get('name', 'module')}_output.txt")
    else:
        raw_path = output_config  # soporte legacy por si es string directamente

    # Reemplaza {target} y construye ruta completa
    output_filename = raw_path.format(target=target)
    output_path = os.path.join(scan_folder, output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    module_name = module_config.get('name', 'unknown_module')

    try:
        log_scan_event(scan_folder, module_name, 'start')

        print(f"[+] Ejecutando módulo: {module_name}")
        print(f"    Comando: {' '.join(command)}")
        print(f"    Output → {output_path}")

        timestamp_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Ejecutar el comando y capturar toda la salida en 'result'
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, text=True)

        timestamp_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Ahora abrir el fichero y escribir todo en modo append
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp_inicio}] INICIO_MODULO [{module_name}]\n")
            f.write("[Comando ejecutado]\n")
            f.write(f"{' '.join(command)}\n")
            f.write("[Salida]\n")
            f.write(result.stdout)
            f.write(f"\n[{timestamp_fin}] FIN_MODULO [{module_name}]\n")

        log_scan_event(scan_folder, module_name, 'end')

    except subprocess.CalledProcessError as e:
        log_scan_event(scan_folder, module_name, f'error: {e}')
        print(f"[!] Error ejecutando módulo {module_name}: {e}")

    # === Actualizar progreso en scan_info.json ===
    scan_info_file = os.path.join(scan_folder, 'scan_info.json')
    if os.path.exists(scan_info_file):
        with open(scan_info_file, 'r', encoding='utf-8') as f:
            scan_info = json.load(f)
    else:
        scan_info = {}

    # Incrementa contador de módulos ejecutados (inicializa si no está)
    scan_info['module_index'] = scan_info.get('module_index', 0) + 1

    total = len(scan_info.get('modules', []))
    completados = scan_info['module_index']
    if total == 0:
        scan_info['progress'] = 0
    else:
        scan_info['progress'] = int((completados / total) * 100)

    if completados >= total:
        scan_info['status'] = 'completed'
        scan_info['progress'] = 100

    with open(scan_info_file, 'w', encoding='utf-8') as f:
        json.dump(scan_info, f, indent=2)

    return True



def start_scan_modules(scan_folder, modules, target, aggressiveness):
    print(f"[?] LLEGO A START_SCAN_MODULES")
    for module_name in modules:
        print(f"[?] Procesando módulo: {module_name} (tipo: {type(module_name)})")
        try:
            # Adaptar si es dict
            if isinstance(module_name, dict):
                module_name = module_name.get('name', None)
                if not module_name:
                    raise ValueError("Nombre del módulo no encontrado en dict")
            config = load_module_config(module_name)
            cmd = build_command(config, target, aggressiveness)
            print( f"[->] Comando generado: {cmd}")
            success = run_command_and_log_sync(config, cmd, scan_folder, target)

            if not success:
                print(f"[!] Fallo en módulo {module_name}, abortando ejecución secuencial.")
                break
        except Exception as e:
            print(f"[!] Error iniciando módulo {module_name}: {e}")
            break



# Punto de entrada si lo quieres invocar desde otro archivo
def start_scan_sequence(scan_folder, modules, target, aggressiveness):
    """
    Alias de start_scan_modules para compatibilidad con el backend Flask.
    """
    print(f"[?] LLEGO A START_SCAN_SEQUENCE")

    start_scan_modules(scan_folder, modules, target, aggressiveness)

