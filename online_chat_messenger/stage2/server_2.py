import socket
import threading
import secrets

PORT = 9002
HOST = '0.0.0.0'

rooms = {}  # Format: {room_name: {"host_token": ..., "clients": {token: address}, "password": None}}

def handle_client(connection):
    try:
        header = connection.recv(32)
        room_name_size = header[0]
        operation = header[1]  # 1 = create, 2 = join
        state = header[2]
        payload_size = int.from_bytes(header[3:], 'big')

        data = connection.recv(room_name_size + payload_size)
        room_name = data[:room_name_size].decode()
        payload = data[room_name_size:].decode()

        if operation == 1 and state == 0:
            # Create room
            token = secrets.token_hex(8)
            rooms[room_name] = {"host_token": token, "clients": {token: None}, "password": None}
            print(f"Room '{room_name}' created with host token {token}")
            connection.sendall(token.encode())
        elif operation == 2 and state == 0:
            # Join room
            if room_name in rooms:
                token = secrets.token_hex(8)
                rooms[room_name]["clients"][token] = None
                connection.sendall(token.encode())
                print(f"Client joined room '{room_name}' with token {token}")
            else:
                connection.sendall(b"ROOM_NOT_FOUND")
    finally:
        connection.close()

def tcp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"🚪 TCP Server listening on {PORT}...")

    while True:
        conn, _ = sock.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == '__main__':
    tcp_listener()
