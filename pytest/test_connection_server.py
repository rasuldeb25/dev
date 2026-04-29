import socket
import string
from crypto_utils import deserialize_key, decrypt_data

HOST = "127.0.0.1"   # localhost
PORT = 1234

# Charset used for decryption
charset = " " + string.punctuation + string.digits + string.ascii_letters
charset = list(charset)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Server listening on {HOST}:{PORT}")

conn, addr = server.accept()
print(f"Connected from {addr}")

try:
    # Receive key length
    header_data = b""
    while b"|" not in header_data:
        chunk = conn.recv(1)
        if not chunk:
            break
        header_data += chunk
    
    key_length = int(header_data.decode().strip("|"))
    print(f"Key length: {key_length}")
    
    # Receive the key
    key_data = conn.recv(key_length)
    key = deserialize_key(key_data.decode())
    print(f"Received encryption key")
    
    # Receive encrypted content
    encrypted_content = b""
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        encrypted_content += chunk
    
    encrypted_str = encrypted_content.decode()
    print(f"Received encrypted data: {len(encrypted_str)} bytes")
    
    # Decrypt the content
    decrypted_content = decrypt_data(encrypted_str, key, charset)
    print(f"Decrypted content ({len(decrypted_content)} bytes):")
    print("-" * 50)
    print(decrypted_content)
    print("-" * 50)
    
    # Save decrypted content to file
    output_file = "received_decrypted.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(decrypted_content)
    print(f"\nDecrypted file saved as: {output_file}")
    
    # Send acknowledgement
    conn.sendall("File received and decrypted successfully!".encode())

except Exception as e:
    print(f"Error: {e}")
    conn.sendall("Error processing encrypted file!".encode())

finally:
    conn.close()
    server.close()
    print("Connection closed.")