import socket
import threading

# Input your username
username = input("Enter your username: ")
username_bytes = username.encode('utf-8')
username_length = len(username_bytes)

# Set up client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', 0))  # OS chooses port
server_ip = input("Enter server IP (e.g., 127.0.0.1): ")
server_address = (server_ip, 9001)

def receive():
    while True:
        try:
            data, _ = client_socket.recvfrom(4096)
            name_len = data[0]
            name = data[1:1+name_len].decode('utf-8')
            msg = data[1+name_len:].decode('utf-8')
            print(f"\n{name}: {msg}")
        except:
            break

# Start receiving thread
threading.Thread(target=receive, daemon=True).start()

# Send messages
while True:
    try:
        msg = input()
        msg_bytes = msg.encode('utf-8')
        data = bytes([username_length]) + username_bytes + msg_bytes
        client_socket.sendto(data, server_address)
    except KeyboardInterrupt:
        print("\n👋 Exiting chat.")
        break
