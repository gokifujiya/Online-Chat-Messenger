import socket
import time

# UDP socket setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 9001)
server_socket.bind(server_address)

print("🔌 UDP Chat Server started on port 9001...")

clients = {}  # Stores: {address: last_message_time}

TIMEOUT = 60  # seconds

while True:
    try:
        data, address = server_socket.recvfrom(4096)
        if not data:
            continue

        # Register or update the client
        clients[address] = time.time()

        # Extract username length and actual message
        username_length = data[0]
        username = data[1:1+username_length].decode('utf-8')
        message = data[1+username_length:].decode('utf-8')

        print(f"📨 {username} ({address}): {message}")

        # Relay to other clients
        for client in list(clients.keys()):
            if time.time() - clients[client] > TIMEOUT:
                print(f"⛔ Timeout: Removing inactive client {client}")
                del clients[client]
                continue
            if client != address:
                server_socket.sendto(data, client)

    except KeyboardInterrupt:
        print("\n🛑 Server shutting down.")
        break
