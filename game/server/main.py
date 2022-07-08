import socket
import json
import time
import random
import threading

# TODO in progres load map
# from .client.maps import Test

ADDR = "0.0.0.0"
PORT = 1026
MAX_PLAYERS = 10
MSG_SIZE = 2048

# Setup server socket
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.bind((ADDR, PORT))
connection.listen(MAX_PLAYERS)

players = {}
# maps = {"test": {Test.spawn_places()}}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def generate_id(player_list: dict, max_players: int):
    while True:
        unique_id = str(random.randint(1, max_players))
        if unique_id not in player_list:
            return unique_id


def handle_messages(identifier: str):
    client_info = players[identifier]
    conn: socket.socket = client_info["socket"]
    username = client_info["username"]

    while True:
        try:
            msg = conn.recv(MSG_SIZE)
        except ConnectionResetError:
            break

        if not msg:
            break

        msg_decoded = msg.decode("utf8")
        # try:
        #     left_bracket_index = msg_decoded.index("{")
        #     right_bracket_index = msg_decoded.index("}") + 1
        #     msg_decoded = msg_decoded[left_bracket_index:right_bracket_index]
        # except ValueError:
        #     continue
        try:
            msg_json = json.loads(msg_decoded)
        except Exception as e:
            print(e)
            continue

        print(f"Received message from player {username} with ID {identifier}")

        if msg_json["object"] == "player":
            players[identifier]["position"] = msg_json["position"]
            players[identifier]["rotation"] = msg_json["rotation"]
            players[identifier]["hp"] = msg_json["hp"]
            players[identifier]["global_var"] = msg_json["global_var"]
            players[identifier]["weapons"] = msg_json["weapons"]
            players[identifier]["current_weapon"] = msg_json["current_weapon"]

        if msg_json["object"] == "hit":
            print(
                f"Player {username} give {msg_json['damage']} damage to {players[msg_json['target_id']]['username']}")
            players[msg_json["target_id"]]["hp"] -= msg_json["damage"]

        print(bcolors.OKBLUE + str(players[identifier]) + bcolors.ENDC)

        # Tell other players about player changen
        for player_id in players:
            if player_id != identifier:
                player_info = players[player_id]
                player_conn: socket.socket = player_info["socket"]
                try:
                    player_conn.sendall(msg_decoded.encode("utf8"))
                except OSError:
                    pass

    # Tell other players about player leaving
    for player_id in players:
        if player_id != identifier:
            player_info = players[player_id]
            player_conn: socket.socket = player_info["socket"]
            try:
                player_conn.send(json.dumps(
                    {"id": identifier, "object": "player", "joined": False, "left": True}).encode("utf8"))
            except OSError:
                pass

    print(f"Player {username} with ID {identifier} has left the game...")
    del players[identifier]
    conn.close()


def main():
    print("Server started, listening for new connections...")

    while True:
        # Accept new connection and assign unique ID
        conn, addr = connection.accept()
        new_id = generate_id(players, MAX_PLAYERS)
        conn.send(new_id.encode("utf8"))

        username = conn.recv(MSG_SIZE).decode("utf8")

        new_player_info = {
            "socket": conn,
            "username": username,
            "position": (0, 1, 0),
            "rotation": 0, "global_var": {
                "Crouch": False,
                "Running": False,
                "Reload": False,
                "Aiming": False,
                "Shooting": False,
                "Build": False, },
            "hp": 100,
            "weapons": [],
            "current_weapon": 0}

        # Tell existing players about new player
        for player_id in players:
            if player_id != new_id:
                player_info = players[player_id]
                player_conn: socket.socket = player_info["socket"]
                try:
                    player_conn.send(json.dumps({
                        "id": new_id,
                        "object": "player",
                        "username": new_player_info["username"],
                        "position": new_player_info["position"],
                        "hp": new_player_info["hp"],
                        "joined": True,
                        "left": False

                    }).encode("utf8"))
                except OSError:
                    pass

        # Tell new player about existing players
        for player_id in players:
            if player_id != new_id:
                player_info = players[player_id]
                try:
                    conn.send(json.dumps({
                        "id": player_id,
                        "object": "player",
                        "username": player_info["username"],
                        "position": player_info["position"],
                        "hp": player_info["hp"],
                        "joined": True,
                        "left": False
                    }).encode("utf8"))
                    time.sleep(0.1)
                except OSError:
                    pass

        # Add new player to players list, effectively allowing it to receive messages from other players
        players[new_id] = new_player_info

        # Start thread to receive messages from client
        msg_thread = threading.Thread(
            target=handle_messages, args=(new_id,), daemon=True)
        msg_thread.start()
        print(f"New connection from {addr}, assigned ID: {new_id}...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    finally:
        print("Exiting")
        connection.close()
