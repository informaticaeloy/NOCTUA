import os
import json

SCAN_DIR = "scans"

def save_scan_to_disk(scan_data):
    if not os.path.exists(SCAN_DIR):
        os.makedirs(SCAN_DIR, exist_ok=True)

    folder_name = f"{scan_data['target']}_{scan_data['id'][:8]}"
    folder_path = os.path.join(SCAN_DIR, folder_name)

    os.makedirs(folder_path, exist_ok=True)

    json_path = os.path.join(folder_path, "scan_info.json")
    with open(json_path, "w") as f:
        json.dump(scan_data, f, indent=2)
