import socket
import json
import time
import random
import threading

# export PYTHONPATH=/home/USERNAME/Desktop/ursina_engine
from game.client.maps import Map, Test
from logg_color import logg

ADDR = "0.0.0.0"
PORT = 1026  # kill service on port: sudo lsof -i:1026
MAX_PLAYERS = 10
MSG_SIZE = 2048

# Setup server socket
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.bind((ADDR, PORT))
connection.listen(MAX_PLAYERS)

players = {}
maps = {}
match = {
    "state": "waiting_start_game",
    "attacker": [],
    "point_attacker": 0,
    "defenders": [],
    "point_defenders": 0,
}
# type state: in_round, before_round, waiting_start_game

logg("okgreen", "MAP:")
for map in Map.list_map():
    map_info = map.map_info()
    maps[map_info["name"]] = map_info
    logg("okgreen", f" - {map_info['name']}  ({map_info['description']})")


current_map = random.choice(list(maps.values()))
logg("okgreen", f"Actual map: {current_map['name']}")


def assign_to_team(id_player: str):
    """assign to a team with fewer players"""
    if len(match["attacker"]) > len(match["defenders"]):
        match["defenders"].append(id_player)
        logg("okgreen", f"add {players[id_player]['username']}  to team defenders")

    match["attacker"].append(id_player)
    logg("okgreen", f"add {players[id_player]['username']}  to team attacker")


def generate_id(player_list: dict, max_players: int):
    for unique_id in range(max_players):
        if str(unique_id) not in player_list:
            return str(unique_id)
    return None


def send_info(conn, data):
    try:
        if type(data) == dict:
            conn.send(json.dumps(data).encode("utf8"))
            return True

        if type(data) == str:
            conn.send(data.encode("utf8"))
            return True

        return False

    except OSError:
        return False


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

        # nieraz kurwy sie sklejaja
        # example {"object": "player", "id": "6", "joined": false, "left": false, "position": [5.0, -0.4177, 0.0], "rotation": 35.4666633605957, "global_var": {"Crouch": false, "Running": false, "Reload": false, "Aiming": false, "Shooting": false, "Build": false}, "hp": 125, "weapons": ["ak_47", "ACP_Smith"], "current_weapon": 0}{"object": "player", "id": "6", "joined": false, "left": false, "position": [5.0, -0.5154, 0.0], "rotation": 81.39259338378906, "global_var": {"Crouch": false, "Running": false, "Reload": false, "Aiming": false, "Shooting": false, "Build": false}, "hp": 125, "weapons": ["ak_47", "ACP_Smith"], "current_weapon": 0}{"object": "player", "id": "6", "joined": false, "left": false, "position": [5.0, -0.7975, 0.0], "rotation": 81.39259338378906, "global_var": {"Crouch": false, "Running": false, "Reload": false, "Aiming": false, "Shooting": false, "Build": false}, "hp": 125, "weapons": ["ak_47", "ACP_Smith"], "current_weapon": 0}
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

        logg(text=f"Received message from player {username} with ID {identifier}")
        if msg_json["object"] == "player":
            players[identifier]["position"] = msg_json["position"]
            players[identifier]["rotation"] = msg_json["rotation"]
            players[identifier]["hp"] = msg_json["hp"]
            players[identifier]["global_var"] = msg_json["global_var"]
            players[identifier]["weapons"] = msg_json["weapons"]
            players[identifier]["current_weapon"] = msg_json["current_weapon"]

        if msg_json["object"] == "hit":
            logg(
                "header",
                f"Player {username} give {msg_json['damage']} damage to {players[msg_json['target_id']]['username']}",
            )
            players[msg_json["target_id"]]["hp"] -= msg_json["damage"]

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

            data = {
                "object": "player",
                "id": identifier,
                "joined": False,
                "left": True,
            }

            send_info(player_conn, data)

    logg(text=f"Player {username} with ID {identifier} has left the game...")
    del players[identifier]
    conn.close()


def main():
    logg(text="Server started, listening for new connections...")

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
            "rotation": 0,
            "global_var": {
                "Crouch": False,
                "Running": False,
                "Reload": False,
                "Aiming": False,
                "Shooting": False,
                "Build": False,
            },
            "hp": 100,
            "weapons": [],
            "current_weapon": 0,
        }

        # Add new player to players list, effectively allowing it to receive messages from other players
        players[new_id] = new_player_info
        assign_to_team(new_id)

        # return basic info (current map, match info points...)
        send_info(conn, {"object": "map", "current_map": current_map})
        time.sleep(0.1)
        send_info(conn, {"object": "match", "match": match})
        time.sleep(0.1)

        # Tell existing players about new player
        for player_id in players:
            if player_id != new_id:
                player_info = players[player_id]
                player_conn: socket.socket = player_info["socket"]

                data = {
                    "id": new_id,
                    "object": "player",
                    "username": new_player_info["username"],
                    "position": new_player_info["position"],
                    "hp": new_player_info["hp"],
                    "joined": True,
                    "left": False,
                }
                send_info(player_conn, data)

        # Tell new player about existing players
        for player_id in players:
            if player_id != new_id:
                player_info = players[player_id]

                data = {
                    "id": player_id,
                    "object": "player",
                    "username": player_info["username"],
                    "position": player_info["position"],
                    "hp": player_info["hp"],
                    "joined": True,
                    "left": False,
                }
                send_info(conn, data)

        # Start thread to receive messages from client
        msg_thread = threading.Thread(
            target=handle_messages, args=(new_id,), daemon=True
        )
        msg_thread.start()

        logg(text=f"New connection from {addr}, assigned ID: {new_id}...")


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
