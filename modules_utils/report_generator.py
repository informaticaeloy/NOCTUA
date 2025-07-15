import os
import json
from datetime import datetime

def generate_report(scan_folder):
    info_path = os.path.join(scan_folder, "info.json")
    report_path = os.path.join(scan_folder, "reporte.txt")

    if not os.path.exists(info_path):
        raise FileNotFoundError("info.json no encontrado en el escaneo.")

    with open(info_path, "r") as f:
        info = json.load(f)

    lines = []
    lines.append("==== INFORME DE ESCANEO ====")
    lines.append(f"ID: {info['id']}")
    lines.append(f"Target: {info['target']}")
    lines.append(f"Fecha creación: {info.get('created_at', 'N/D')}")
    lines.append(f"Módulos: {', '.join(info['modules'])}")
    lines.append(f"Agresividad: {info['aggressiveness']}")
    lines.append(f"Estado: {info['status']}")
    lines.append("")

    lines.append("==== RESULTADOS DE MÓDULOS ====")

    for mod in info["modules"]:
        lines.append(f"\n[Módulo: {mod}]")
        # Soporta salida en .txt o .json (si existe)
        txt_file = os.path.join(scan_folder, f"{mod}.txt")
        json_file = os.path.join(scan_folder, f"{mod}.json")

        if os.path.exists(txt_file):
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                contenido = f.read().strip()
                lines.append(contenido if contenido else "(sin contenido)")
        elif os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8", errors="ignore") as f:
                try:
                    jdata = json.load(f)
                    lines.append(json.dumps(jdata, indent=2, ensure_ascii=False))
                except Exception:
                    lines.append("(JSON inválido)")
        else:
            lines.append("(sin archivo de salida encontrado)")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return report_path
