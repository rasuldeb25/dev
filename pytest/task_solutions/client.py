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


def affine_enc(m, ka, kb, n):
    return (ka * m + kb) % n


def encrypt_text(text):
    data = text.encode()
    encrypted = []
    for b in data:
        c = affine_enc(b, KA, KB, N)
        encrypted.append(c)
    return bytes(encrypted).hex()


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
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    user_hex = encrypt_text(USERNAME)
    message = f"USER|{user_hex}\n"
    client.sendall(message.encode())
    print(f"Sent: {message.strip()}")

    response = read_line(client).strip("\n")
    print(f"Server: {response}")
    if response != "OK|send password":
        print("Login failed.")
        client.close()
        return

    pass_hex = encrypt_text(PASSWORD)
    message = f"PASS|{pass_hex}\n"
    client.sendall(message.encode())
    print(f"Sent: {message.strip()}")

    response = read_line(client).strip("\n")
    print(f"Server: {response}")
    if response == "OK|login complete":
        print("Protocol succeeded.")
    else:
        print("Protocol failed.")

    client.close()


if __name__ == "__main__":
    main()