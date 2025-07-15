import sys
import socket
import os

def resolve(target, level):
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/dns_{target}.txt"
    try:
        result = socket.gethostbyname_ex(target)
        with open(output_file, "w") as f:
            f.write(str(result))
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python dns_resolver.py <target> <level>")
        sys.exit(1)
    target = sys.argv[1]
    try:
        level = int(sys.argv[2])
    except ValueError:
        level = 1
    resolve(target, level)
