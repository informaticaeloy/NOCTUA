import subprocess
import sys
import os

def run(target, aggressiveness):
    # Construir el comando dig según agresividad
    cmd = ['dig', target, '+short']
    if aggressiveness == 10:
        cmd.append('ANY')
    elif aggressiveness == 5:
        cmd.append('MX')
    elif aggressiveness == 1:
        cmd.append('A')
    else:
        # Nivel por defecto si llega otro valor
        cmd.append('A')

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=10)
        output_dir = os.path.join("results")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"dns_{target}.txt")
        with open(output_file, "w") as f:
            f.write(result.stdout)
        return output_file
    except subprocess.TimeoutExpired:
        print(f"Timeout al ejecutar dig para {target}")
        return None
    except Exception as e:
        print(f"Error ejecutando dig: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python dns_enum.py <target> <aggressiveness>")
        sys.exit(1)
    target = sys.argv[1]
    try:
        aggressiveness = int(sys.argv[2])
    except ValueError:
        aggressiveness = 1
    run(target, aggressiveness)
