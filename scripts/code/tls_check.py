import sys
import ssl
import socket
import os

def get_cert_info(host, level):
    port = 443
    context = ssl.create_default_context()
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/tls_{host}.txt"
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                with open(output_file, "w") as f:
                    f.write(str(cert))
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tls_check.py <host> <level>")
        sys.exit(1)
    get_cert_info(sys.argv[1], int(sys.argv[2]))
