from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import socket

# Set up socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 9003))
sock.listen(1)
print("🚀 Server ready on port 9003...")

while True:
    conn, addr = sock.accept()
    print("📥 Connection from", addr)

    # Receive public key
    public_key_pem = conn.recv(2048)
    public_key = serialization.load_pem_public_key(public_key_pem)

    # Encrypt a message
    message = b"Hello from the server!"
    encrypted = public_key.encrypt(
        message,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    # Send encrypted message
    conn.send(encrypted)
    conn.close()
