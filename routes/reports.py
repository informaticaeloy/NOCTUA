import os
import json
from datetime import datetime
from flask import Blueprint, render_template

from utils.utils import load_all_scans

bp_reports = Blueprint('reports', __name__)
SCANS_DIR = './scans'

@bp_reports.route('/report/<scan_id>')
def show_report(scan_id):
    print(f"[INFO] show_report ejecutado con scan_id = {scan_id}")

    scans = load_all_scans()
    scan = next((s for s in scans if s['id'] == scan_id), None)
    if not scan:
        return "Escaneo no encontrado", 404

    print("SCAN ENCONTRADO:")
    print(json.dumps(scan, indent=2))

    scan_name = scan.get('name', 'Sin nombre')
    scan_date_raw = scan.get('created_at', None)
    target = scan.get('target', 'Desconocido')
    description = scan.get('description', '')
    aggressiveness = scan.get('aggressiveness', 'N/A')
    modules = scan.get('modules', [])
    scan_folder = os.path.join(SCANS_DIR, scan['folder_name'])
    results_folder = os.path.join(scan_folder, 'results')

    # Formatear la fecha de inicio si viene como string ISO
    scan_date = scan_date_raw
    if scan_date_raw:
        try:
            dt = datetime.fromisoformat(scan_date_raw)
            scan_date = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    modules_results = []

    if os.path.isdir(results_folder):
        for filename in sorted(os.listdir(results_folder)):
            file_path = os.path.join(results_folder, filename)
            if not filename.endswith('.txt'):
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            bloques = []
            partes = content.split('[INICIO_MODULO')
            for bloque in partes[1:]:
                parsed = parse_module_block(bloque)
                if parsed:
                    bloques.append(parsed)

            # Dividir el contenido por líneas
            lines = content.splitlines()

            current_block = None

            for line in lines:
                # Detectar inicio de módulo
                if 'INICIO_MODULO' in line:
                    # Ejemplo de línea:
                    # [2025-07-07 14:37:45] INICIO_MODULO [ip_publica]
                    try:
                        # Extraer timestamp y nombre módulo con regex o split
                        import re
                        m = re.match(r'\[(.*?)\]\s+INICIO_MODULO\s+\[(.*?)\]', line)
                        if m:
                            timestamp_inicio = m.group(1)
                            modulo = m.group(2)
                            current_block = {
                                'timestamp_inicio': timestamp_inicio,
                                'modulo': modulo,
                                'comando': '',
                                'salida': '',
                                'timestamp_fin': ''
                            }
                    except Exception as e:
                        current_block = None
                    continue

                # Detectar fin de módulo
                if 'FIN_MODULO' in line and current_block is not None:
                    try:
                        # Extraer timestamp fin
                        m = re.match(r'\[(.*?)\]\s+FIN_MODULO\s+\[(.*?)\]', line)
                        if m:
                            timestamp_fin = m.group(1)
                            current_block['timestamp_fin'] = timestamp_fin
                    except Exception:
                        pass
                    bloques.append(current_block)
                    current_block = None
                    continue

                # Si estamos dentro de un bloque, acumular comando y salida
                if current_block is not None:
                    if '[Comando ejecutado]' in line:
                        # Siguiente líneas son comando (asumiendo línea siguiente)
                        current_block['comando'] = ''
                        continue
                    elif '[Salida]' in line:
                        # Siguiente líneas son salida
                        current_block['salida'] = ''
                        continue
                    else:
                        # Acumular comando o salida dependiendo de si ya se ha encontrado [Salida]
                        # Para simplificar, asumimos que el texto después de [Comando ejecutado] y antes de [Salida] es comando,
                        # y después de [Salida] es salida
                        if current_block['salida'] == '':
                            # Aún en comando
                            current_block['comando'] += line + '\n'
                        else:
                            current_block['salida'] += line + '\n'

            modules_results.append({
                'filename': filename,
                'modulo': filename.split('_')[0],
                'ejecuciones': bloques
            })

    # Calcular fecha fin del escaneo
    all_end_times = []
    for resultado in modules_results:
        for ejec in resultado['ejecuciones']:
            try:
                if ejec['timestamp_fin']:
                    dt = datetime.strptime(ejec['timestamp_fin'], "%Y-%m-%d %H:%M:%S")
                    all_end_times.append(dt)
            except Exception:
                continue
    scan_end = max(all_end_times).strftime("%Y-%m-%d %H:%M:%S") if all_end_times else 'Desconocido'

    # Asociar módulos a la fecha de su primera ejecución
    execution_dates = {}
    for resultado in modules_results:
        modulo = resultado.get('modulo')
        ejecuciones = resultado.get('ejecuciones', [])
        if ejecuciones:
            # Tomamos la fecha de inicio de la primera ejecución
            execution_dates[modulo] = ejecuciones[0].get('timestamp_inicio', 'Sin fecha')


    return render_template('report.html',
                           scan_name=scan_name,
                           scan_date=scan_date,
                           scan_end=scan_end,
                           target=target,
                           description=description,
                           aggressiveness=aggressiveness,
                           modules=modules,
                           modules_results=modules_results,
                           execution_dates=execution_dates)
    '''             
    return render_template('report.html',
                           scan_name=scan_name,
                           scan_date=scan_date,
                           scan_end=scan_end,
                           target=target,
                           description=description,
                           aggressiveness=aggressiveness,
                           modules=modules,
                           modules_results=modules_results)
    '''


def parse_module_block(bloque):
    try:
        inicio_line = bloque.split(']', 1)[0].strip()
        timestamp_inicio, modulo = inicio_line.split(']')[0].strip(), inicio_line.split('[')[-1].strip()

        resto = bloque.split(']', 1)[1]

        # Dividir contenido sin etiquetas en el resultado
        _, comando_y_resto = resto.split('[Comando ejecutado]', 1)
        comando, _, resto_salida = comando_y_resto.partition('[Salida]')
        comando = comando.strip()

        salida, _, fin_modulo = resto_salida.partition('[FIN_MODULO')
        salida = salida.strip()

        timestamp_fin = fin_modulo.split(']')[0].strip()

        return {
            'timestamp_inicio': timestamp_inicio,
            'timestamp_fin': timestamp_fin,
            'modulo': modulo,
            'comando': comando,
            'salida': salida
        }
    except Exception as e:
        print(f"[WARN] Error parseando bloque: {e}")
        return None

