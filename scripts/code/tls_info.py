import ssl
import socket
import sys
import os

def run(target, aggressiveness):
    port = 443
    context = ssl.create_default_context()
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/tls_{target}.txt"

    try:
        with socket.create_connection((target, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()

        with open(output_file, "w") as f:
            f.write("Subject: " + str(cert.get('subject')) + "\n")
            f.write("Issuer: " + str(cert.get('issuer')) + "\n")
            f.write("Valid From: " + cert.get('notBefore') + "\n")
            f.write("Valid Until: " + cert.get('notAfter') + "\n")
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"Error: {e}")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tls_info.py <target> <aggressiveness>")
        sys.exit(1)
    run(sys.argv[1], int(sys.argv[2]))
