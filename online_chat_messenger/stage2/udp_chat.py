import socket
import threading
import sys

# Constants
SERVER_PORT = 9002
BUFFER_SIZE = 4096

# Get info from user
server_ip = input("Enter server IP (e.g., 127.0.0.1): ")
room_name = input("Enter chat room name: ")
token = input("Enter your token: ")

# Convert to bytes
room_bytes = room_name.encode("utf-8")
token_bytes = token.encode("utf-8")

# Prepare header
room_len = len(room_bytes)
token_len = len(token_bytes)
header = bytes([room_len, token_len])

# Start UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)
sock.bind(('', 0))  # Bind to an available local port

server_address = (server_ip, SERVER_PORT)

def receive():
    while True:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            print("\n📨 Received:", data.decode("utf-8"))
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            print("\nExiting receiver...")
            break

def send():
    try:
        while True:
            message = input("You: ")
            if message.lower() == "exit":
                print("Exiting chat...")
                break

            message_bytes = message.encode("utf-8")
            full_message = header + room_bytes + token_bytes + message_bytes
            sock.sendto(full_message, server_address)

    except KeyboardInterrupt:
        print("\nExiting sender...")

# Start receiver in a thread
threading.Thread(target=receive, daemon=True).start()

# Run sender
send()

sock.close()
