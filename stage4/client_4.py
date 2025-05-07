import socket
import os
import threading
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
    return nonce + encryptor.tag + ciphertext  # 12 + 16 + ...

def decrypt_message(aes_key, encrypted_data):
    nonce = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ciphertext = encrypted_data[28:]
    decryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(nonce, tag)
    ).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# --- RSA KEY GENERATION ---
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
client_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# --- TCP CONNECTION + EXCHANGE ---
HOST = input("Enter server IP (e.g., 127.0.0.1): ")
PORT = 9003

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # Step 1: Send client public key
    sock.sendall(client_pem)
    print("📤 Sent client public key")

    # Step 2: Receive server public key
    server_pem = b''
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        server_pem += chunk
        if b"END PUBLIC KEY" in server_pem:
            break
    print("📥 Received server public key")

    server_public_key = serialization.load_pem_public_key(server_pem)

    # Step 3: Generate and send AES key
    aes_key = os.urandom(32)
    encrypted_key = server_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    sock.sendall(encrypted_key)
    print("🔐 Secure AES key sent")

    # --- CHAT LOOP ---
    def sender():
        while True:
            msg = input("📝 You: ")
            if msg.lower() == "exit":
                break
            encrypted = encrypt_message(aes_key, msg)
            sock.sendall(encrypted)

    def receiver():
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                plaintext = decrypt_message(aes_key, data)
                print("💬 Server:", plaintext.decode())
            except:
                break

    threading.Thread(target=receiver, daemon=True).start()
    sender()
