import os
import json

#SCANS_DIR = os.path.join(os.path.dirname(__file__), '../scans')  # Ajusta según estructura
SCANS_DIR = './scans'

def load_scan(scan_id):
    """
    Carga un escaneo por ID desde su carpeta.
    Devuelve (dict_scan_data, ruta_absoluta) o (None, None) si no existe.
    """
    for folder in os.listdir(SCANS_DIR):
        folder_path = os.path.join(SCANS_DIR, folder)
        scan_file = os.path.join(folder_path, 'scan_info.json')

        if os.path.isdir(folder_path) and os.path.isfile(scan_file):
            try:
                with open(scan_file, 'r', encoding='utf-8') as f:
                    scan_data = json.load(f)
                    if scan_data.get("id") == scan_id:
                        return scan_data, folder_path
            except json.JSONDecodeError:
                continue

    return None, None


def load_all_scans():
    """
    Carga todos los escaneos del directorio SCANS_DIR.
    Devuelve lista de diccionarios de escaneo.
    """
    scans = []
    if not os.path.exists(SCANS_DIR):
        return scans

    for folder in os.listdir(SCANS_DIR):
        folder_path = os.path.join(SCANS_DIR, folder)
        scan_file = os.path.join(folder_path, 'scan_info.json')

        if os.path.isdir(folder_path) and os.path.isfile(scan_file):
            try:
                with open(scan_file, encoding='utf-8') as f:
                    scan_data = json.load(f)

                    # Compatibilidad: convertir módulos antiguos
                    if 'flow' not in scan_data and 'modules' in scan_data:
                        scan_data['flow'] = [{"type": "mod", "name": m} for m in scan_data['modules']]

                    # Añadir campo de carpeta
                    scan_data['folder_name'] = folder
                    scans.append(scan_data)

            except json.JSONDecodeError:
                continue

    return scans



# Helper para guardar datos de un escaneo
def save_scan(scan_data, scan_folder):
    scan_file = os.path.join(scan_folder, 'scan_info.json')
    with open(scan_file, 'w') as f:
        json.dump(scan_data, f, indent=2)