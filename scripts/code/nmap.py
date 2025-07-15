import subprocess
import sys
import os

def run(target, level):
    options = {
        "1": ["-sP"],
        "5": ["-sS", "-T3", "--top-ports", "100"],
        "10": ["-sS", "-T4", "-A"]
    }

    args = options.get(str(level), options["5"])
    output_path = f"results/nmap_{target}.txt"
    cmd = ["nmap"] + args + [target]

    with open(output_path, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

    return output_path

if __name__ == "__main__":
    target = sys.argv[1]
    level = sys.argv[2]
    run(target, level)
