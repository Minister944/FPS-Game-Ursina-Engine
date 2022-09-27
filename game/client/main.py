from ursina import *

import threading
import socket
from network import Network
import random
import json

app = Ursina(fullscreen=False, vsync=False)
window.windowed_size = 1.3
window.title = "FPS Ursina Multiplayer"
window.borderless = False

from player import Player, Enginer, Medic
from enemy import Enemy
from maps import Test, Map
from game.utils.utils import split_info

import globalVar

globalVar.initialize()

main_player = Enginer(Vec3(5, 0, 0))

prev_main_player = main_player.player_to_dict()
enemies = []
in_game = True

maps = {}
current_map = None
match = {}


# username = input("Enter your username: ")
username = "Kacper " + str(random.randint(1, 100))
# TODO scope change fov
# connect to server and negotiating map, class
while True:
    # server_addr = input("Enter server IP: ")
    # server_port = input("Enter server port: ")
    server_addr = "0.0.0.0"
    server_port = 1026
    try:
        server_port = int(server_port)
    except ValueError:
        print("\nThe port you entered was not a number, try again with a valid port...")
        continue

    globalVar.connection = Network(server_addr, server_port, username)
    globalVar.connection.settimeout(5)

    error_occurred = False

    try:
        globalVar.connection.connect()
    except ConnectionRefusedError:
        print(
            "\nConnection refused! This can be because server hasn't started or has reached it's player limit."
        )
        # error_occurred = True
    except socket.timeout:
        print("\nServer took too long to respond, please try again...")
        # error_occurred = True
    except socket.gaierror:
        print(
            "\nThe IP address you entered is invalid, please try again with a valid address..."
        )
        # error_occurred = True
    finally:
        globalVar.connection.settimeout(None)

    if not error_occurred:
        break


def object_trigger(msg_decoded):
    global match, current_map
    try:
        msg_json = json.loads(msg_decoded)
    except Exception as e:
        print(e)
        return

    print(f"Received message trigger{msg_json['object']}")
    print(msg_json)

    if msg_json["object"] == "join":
        enemy_id = msg_json["id"]

        new_enemy = Enemy(identifier=enemy_id, username=msg_json["username"])
        enemies.append(new_enemy)
        return

    if msg_json["object"] == "left":
        enemy_id = msg_json["id"]

        for e in enemies:
            if e.id == enemy_id:
                enemies.remove(e)
                destroy(e)
                return
        return

    if msg_json["object"] == "player":
        enemy_id = msg_json["id"]

        enemy = None
        for e in enemies:
            if e.id == enemy_id:
                enemy = e
                break

        if not enemy:
            return

        enemy.world_position = Vec3(*msg_json["position"])
        enemy.rotation_y = msg_json["rotation"]
        enemy.current_weapon = msg_json["current_weapon"]
        return

    if msg_json["object"] == "map":
        for map in Map.list_map():
            if map.__name__ == msg_json["current_map"]["name"]:
                current_map = msg_json["current_map"]
                a = map()
                return

    if msg_json["object"] == "match":
        match = msg_json["match"]
        return


# receive data and processing
def receive():
    while True:
        try:
            msg = globalVar.connection.receive_info()
        except Exception as e:
            print(e)
            continue

        if not msg:
            print("Server has stopped! Exiting...")
            sys.exit()

        for msg_decoded in split_info(msg.decode("utf8")):
            object_trigger(msg_decoded)


msg_thread = threading.Thread(target=receive, daemon=True)
msg_thread.start()


def input(key):

    if key == "escape":
        global in_game
        if in_game:
            mouse.locked = False
            mouse.visible = True
            in_game = False
            main_player.enabled = False
        else:
            main_player.enabled = True
            mouse.locked = True
            mouse.visible = False
            in_game = True

    if key == "q":
        quit()


def update():

    if main_player.hp > 0:
        global prev_main_player
        if prev_main_player != main_player.player_to_dict():
            globalVar.connection.send_player(main_player)
        prev_main_player = main_player.player_to_dict()


# enemy_test = Enemy(Vec3(5,0,-10),"asad","Winiarska ku***")
Test()
app.run()
