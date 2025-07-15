import subprocess
import sys
import os

def run(target, level):
    # Mapea el nivel de agresividad al parámetro correcto de Nikto
    tuning_map = {
        "1": "1",
        "5": "5",
        "10": "9"  # Nivel máximo en Nikto (9)
    }

    tuning_level = tuning_map.get(str(level), "1")

    cmd = ["nikto", "-host", target, "-Tuning", tuning_level]

    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"nikto_{target}.txt")

    with open(output_path, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 nikto_scan.py <target> <aggressiveness>")
        sys.exit(1)
    target = sys.argv[1]
    level = sys.argv[2]
    run(target, level)
