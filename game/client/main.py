from ursina import *

import threading
import socket
from network import Network
from random import random

app = Ursina(fullscreen=False, vsync=False)
window.windowed_size = 1.3
window.title = "FPS Ursina Multiplayer"
window.borderless = False

from player import Player, Enginer, Medic
from enemy import Enemy
from maps import Test, Map
import globalVar

globalVar.initialize()

main_player = Enginer(Vec3(5, 0, 0))

prev_main_player = main_player.player_to_dict()
enemies = []
in_game = True

maps = {}
current_map = None
match = {}


# for map in Map.list_map():
#     map_info = map.map_info()
#     maps[map_info["name"]] = map_info


# username = input("Enter your username: ")
username = "Kacper" + str(random())
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

# receive data and processing
def receive():
    global current_map, match
    while True:
        try:
            info = globalVar.connection.receive_info()
        except Exception as e:
            print(e)
            continue

        if not info:
            print("Server has stopped! Exiting...")
            sys.exit()

        if info["object"] == "player":
            enemy_id = info["id"]
            if info["joined"]:
                new_enemy = Enemy(Vec3(*info["position"]), enemy_id, info["username"])
                new_enemy.health = info["hp"]
                enemies.append(new_enemy)
                continue

            enemy = None

            for e in enemies:
                if e.id == enemy_id:
                    enemy = e
                    break

            if not enemy:
                continue

            enemy.world_position = Vec3(*info["position"])
            enemy.rotation_y = info["rotation"]
            enemy.current_weapon = info["current_weapon"]
            continue

        if info["object"] == "map":
            for map in Map.list_map():
                if map.__name__ == info["current_map"]["name"]:
                    current_map = info["current_map"]
                    a = map()
                    continue

        if info["object"] == "match":
            match = info["match"]
            continue


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

app.run()
