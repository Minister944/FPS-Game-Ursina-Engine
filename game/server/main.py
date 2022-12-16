import socket
import json
import time
import random
import threading
import os
import sys
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))[:-11]
sys.path.append(os.path.dirname(SCRIPT_DIR))


from game.client.maps import Map, Test

from logg_color import logg
from game.utils.utils import split_info

ADDR = "0.0.0.0"
PORT = 1026  # kill service on port: sudo lsof -i:1026
MAX_PLAYERS = 10
MSG_SIZE = 2048

TIME_BEFORE_ROUND = 7
TIME_ROUND = 180

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
        logg(
            "okgreen",
            f"add {players[id_player]['username']}  to team defenders",
        )
        return

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


def send_info_all(data):
    # TODO ignore
    for player_id in players:
        player_info = players[player_id]
        player_conn: socket.socket = player_info["socket"]
        send_info(player_conn, data)


def start_match():

    while True:
        logg(
            "HEADER",
            f"round {match['point_attacker'] + match['point_defenders']}",
        )
        match["state"] = "before_round"
        data = {"object": "match", "match": match}
        send_info_all(data)

        end_time_before_round = datetime.now().timestamp() + TIME_BEFORE_ROUND

        while True:
            if end_time_before_round < datetime.now().timestamp():
                break

        match["state"] = "in_round"
        data = {"object": "match", "match": match}
        send_info_all(data)

        end_time_in_round = datetime.now().timestamp() + TIME_ROUND

        while True:

            live_attacker = 0
            for a in match["attacker"]:
                for player_id in players:
                    if a == player_id and players[player_id]["hp"] >= 0:
                        live_attacker += 1

            live_defenders = 0
            for a in match["defenders"]:
                for player_id in players:
                    if a == player_id and players[player_id]["hp"] >= 0:
                        live_defenders += 1

            if live_attacker < 0:
                match["point_defenders"] += 1
                break

            if live_defenders < 0:
                match["point_attacker"] += 1
                break

            if end_time_in_round < datetime.now().timestamp():
                match["point_defenders"] += 1
                break

        if match["point_attacker"] + match["point_defenders"] > 10:
            if match["point_attacker"] - 2 < match["point_defenders"]:
                logg("WARNING", "win defenders")
                connection.close()
                break

            if match["point_defenders"] - 2 < match["point_attacker"]:
                logg("WARNING", "win attacker")
                connection.close()
                break


def object_trigger(msg_decoded, identifier, username):
    try:
        msg_json = json.loads(msg_decoded)
    except Exception as e:
        print(e)
        return

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

        for msg_decoded in split_info(msg.decode("utf8")):
            object_trigger(msg_decoded, identifier, username)

    # Tell other players about player leaving
    for player_id in players:
        if player_id != identifier:
            player_info = players[player_id]
            player_conn: socket.socket = player_info["socket"]

            data = {
                "object": "left",
                "id": identifier,
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
        time.sleep(0.1)
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
                    "object": "join",
                    "id": new_id,
                    "username": username,
                }
                send_info(player_conn, data)
        time.sleep(0.1)

        # Tell new player about existing players
        for player_id in players:
            if player_id != new_id:
                player_info = players[player_id]

                data = {
                    "object": "join",
                    "id": player_id,
                    "username": username,
                }
                send_info(conn, data)
        time.sleep(0.1)
        # Start thread to receive messages from client
        msg_thread = threading.Thread(
            target=handle_messages, args=(new_id,), daemon=True
        )
        msg_thread.start()

        if len(match["defenders"]) > 3 and len(match["attacker"]) > 3:
            msg_thread = threading.Thread(target=start_match, daemon=True)
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
