import sys
import subprocess
import os

def run_whois(target, level):
    base_command = ["whois", target]
    if level == 5:
        base_command.append("--verbose")
    elif level == 10:
        base_command.extend(["--verbose", "--raw"])

    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/whois_{target}.txt"

    result = subprocess.run(base_command, capture_output=True, text=True)
    with open(output_file, "w") as f:
        f.write(result.stdout)

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python whois_lookup.py <target> <level>")
        sys.exit(1)
    run_whois(sys.argv[1], int(sys.argv[2]))
