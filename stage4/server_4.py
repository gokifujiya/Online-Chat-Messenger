import socket
import threading
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# --- AES ENCRYPTION HELPERS ---
def encrypt_message(aes_key, plaintext):
    nonce = os.urandom(12)
    encryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(nonce)
    ).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return nonce + encryptor.tag + ciphertext

def decrypt_message(aes_key, encrypted_data):
    nonce = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ciphertext = encrypted_data[28:]
    decryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(nonce, tag)
    ).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# --- SERVER RSA KEY GENERATION ---
server_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
server_public_key = server_private_key.public_key()
server_pem = server_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

HOST = '0.0.0.0'
PORT = 9003

def handle_client(conn, addr):
    print(f"🔗 Connection from {addr}")

    # Step 1: Receive client's public key
    client_pem = conn.recv(2048)
    print("📥 Received client public key")

    # Step 2: Send server's public key
    conn.sendall(server_pem)
    print("📤 Sent server public key")

    # Step 3: Receive AES key from client
    encrypted_key = conn.recv(512)
    aes_key = server_private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print("🔑 AES key decrypted")

    # Step 4: Encrypted chat loop
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            msg = decrypt_message(aes_key, data)
            decoded = msg.decode()
            print(f"💬 {addr}: {decoded}")

            # Echo back encrypted message
            reply = f"Echo: {decoded}"
            conn.sendall(encrypt_message(aes_key, reply))
        except Exception as e:
            print("❌ Error:", e)
            break

    conn.close()
    print(f"🔌 Disconnected {addr}")

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"🚪 Secure Server listening on {PORT}...")

        while True:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    tcp_server()
