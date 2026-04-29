import socket
import os
import string
from crypto_utils import generate_key, encrypt_data, serialize_key

HOST = "127.0.0.1"
PORT = 1234

# File to encrypt and send
FILE_TO_SEND = "lesson_notes.txt"

# Check if file exists
if not os.path.exists(FILE_TO_SEND):
    print(f"Error: {FILE_TO_SEND} not found!")
    exit(1)

# Read the file
with open(FILE_TO_SEND, 'r', encoding='utf-8') as f:
    file_content = f.read()

# Generate encryption key
key, charset = generate_key()
key_str = serialize_key(key)

# Encrypt the file content
encrypted_content = encrypt_data(file_content, key, charset)

print(f"Encrypting {FILE_TO_SEND}...")
print(f"Original size: {len(file_content)} bytes")
print(f"Encrypted size: {len(encrypted_content)} bytes")

# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Send the key length, key, and encrypted content
# Format: [key_length][key][encrypted_content]
key_length = len(key_str)
header = f"{key_length}|"
client.sendall(header.encode())
client.sendall(key_str.encode())
client.sendall(encrypted_content.encode())

print("Encrypted file sent to server!")

# Wait for acknowledgement
ans = client.recv(1024)
print("Server response:", ans.decode())

client.close()
print("Connection closed.")