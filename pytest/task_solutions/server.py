import socket

HOST = "127.0.0.1"
PORT = 12345
KA = 21
KB = 9
N = 256
USERNAME = "student"
PASSWORD = "python"


def ext_euclidean(a, b):
    r0, r1 = a, b
    u0, v0 = 1, 0
    u1, v1 = 0, 1
    while r1 != 0:
        q = r0 // r1
        r0, r1, u0, u1, v0, v1 = r1, r0 - q * r1, u1, u0 - q * u1, v1, v0 - q * v1
    return r0, u0, v0


def invert(a, n):
    _, u, _ = ext_euclidean(a, n)
    return u % n


def affine_dec(c, ka, kb, n):
    return (invert(ka, n) * (c - kb)) % n


def decrypt_hex_string(hex_string):
    data = bytes.fromhex(hex_string)
    plaintext = ""
    for b in data:
        p = affine_dec(b, KA, KB, N)
        plaintext += chr(p)
    return plaintext


def read_line(conn):
    data = b""
    while True:
        chunk = conn.recv(1)
        if not chunk:
            break
        data += chunk
        if chunk == b"\n":
            break
    return data.decode(errors="replace")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = server.accept()
    print(f"Connected by {addr}")

    try:
        message = read_line(conn).strip("\n")
        print(f"Received: {message}")

        if message.startswith("USER|"):
            _, encrypted = message.split("|", 1)
            username = decrypt_hex_string(encrypted)
            if username == USERNAME:
                response = "OK|send password\n"
                conn.sendall(response.encode())
                print(f"Sent: {response.strip()}")
            else:
                response = "ERROR|login failed\n"
                conn.sendall(response.encode())
                print(f"Sent: {response.strip()}")
                print("Final decision: login failed")
                return
        else:
            response = "ERROR|login failed\n"
            conn.sendall(response.encode())
            print(f"Sent: {response.strip()}")
            print("Final decision: login failed")
            return

        message = read_line(conn).strip("\n")
        print(f"Received: {message}")

        if message.startswith("PASS|"):
            _, encrypted = message.split("|", 1)
            password = decrypt_hex_string(encrypted)
            if password == PASSWORD:
                response = "OK|login complete\n"
                conn.sendall(response.encode())
                print(f"Sent: {response.strip()}")
                print("Final decision: login complete")
            else:
                response = "ERROR|login failed\n"
                conn.sendall(response.encode())
                print(f"Sent: {response.strip()}")
                print("Final decision: login failed")
        else:
            response = "ERROR|login failed\n"
            conn.sendall(response.encode())
            print(f"Sent: {response.strip()}")
            print("Final decision: login failed")
    finally:
        conn.close()
        server.close()


if __name__ == "__main__":
    main()