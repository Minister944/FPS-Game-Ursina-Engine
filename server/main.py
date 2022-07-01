import socket
import json
import time
import random
import threading


ADDR = "0.0.0.0"
PORT = 944
MAX_PLAYERS = 10
MSG_SIZE = 2048

# Setup server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ADDR, PORT))
s.listen(MAX_PLAYERS)

players = {}

def generate_id(player_list: dict, max_players: int):
    while True:
        unique_id = str(random.randint(1, max_players))
        if unique_id not in player_list:
            return unique_id


def main():
    print("Server started, listening for new connections...")

    while True:
        # Accept new connection and assign unique ID
        conn, addr = s.accept()
        new_id = generate_id(players, MAX_PLAYERS)
        conn.send(new_id.encode("utf8"))
        username = conn.recv(MSG_SIZE).decode("utf8")
        new_player_info = {"socket": conn, "username": username, "position": (0, 1, 0), "rotation": 0, "health": 100}


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    finally:
        print("Exiting")
        s.close()