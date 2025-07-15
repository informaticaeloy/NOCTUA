import subprocess
import sys
import os

def run(target, level):
    flags = {
        "1": [],
        "5": ["--certinfo", "--compression", "--reneg"],
        "10": ["--regular"]
    }

    cmd = ["sslyze"] + flags.get(str(level), []) + [target]
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"sslyze_{target}.txt")

    with open(output_path, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python sslyze_scan.py <target> <aggressiveness>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
