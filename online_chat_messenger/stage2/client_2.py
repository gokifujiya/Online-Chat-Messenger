import socket

HOST = input("Enter server IP (e.g. 127.0.0.1): ")
PORT = 9002

def create_room(room_name, username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    room_name_bytes = room_name.encode()
    username_bytes = username.encode()

    header = bytearray(32)
    header[0] = len(room_name_bytes)
    header[1] = 1  # Create
    header[2] = 0  # Init state
    header[3:] = len(username_bytes).to_bytes(29, 'big')

    sock.sendall(header + room_name_bytes + username_bytes)

    token = sock.recv(255).decode()
    print(f"Room created! Your host token is: {token}")
    sock.close()

def join_room(room_name, username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    room_name_bytes = room_name.encode()
    username_bytes = username.encode()

    header = bytearray(32)
    header[0] = len(room_name_bytes)
    header[1] = 2  # Join
    header[2] = 0  # Init state
    header[3:] = len(username_bytes).to_bytes(29, 'big')

    sock.sendall(header + room_name_bytes + username_bytes)

    token = sock.recv(255).decode()
    if token == "ROOM_NOT_FOUND":
        print("❌ Room not found.")
    else:
        print(f"Joined room '{room_name}'! Your token is: {token}")
    sock.close()

if __name__ == '__main__':
    print("1: Create Room\n2: Join Room")
    option = input("Choose: ")
    room = input("Enter room name: ")
    name = input("Enter username: ")

    if option == '1':
        create_room(room, name)
    else:
        join_room(room, name)
