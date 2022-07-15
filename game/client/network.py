import socket
import json


class Network:
    def __init__(self, server_addr: str, server_port: int, username: str) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = server_addr
        self.port = server_port
        self.username = username
        self.recv_size = 2048
        self.id = 0

    def settimeout(self, value):
        self.client.settimeout(value)

    def connect(self):
        """
        Connect to the server and get a unique identifier
        """

        self.client.connect((self.addr, self.port))
        self.id = self.client.recv(self.recv_size).decode("utf8")
        self.client.send(self.username.encode("utf8"))

    def send_player(self, player):

        player_info = {
            "object": "player",
            "id": self.id,
            "joined": False,
            "left": False,
        }
        player_info = dict(player_info, **player.player_to_dict())
        player_info_encoded = json.dumps(player_info).encode("utf8")
        try:
            self.client.send(player_info_encoded)
        except socket.error as e:
            print(e)

    def receive_info(self):
        try:
            msg = self.client.recv(self.recv_size)
        except socket.error as e:
            print(e)

        if not msg:
            return None

        msg_decoded = msg.decode("utf8")

        msg_json = json.loads(msg_decoded)

        return msg_json

    def hit(self, target_id: str, damage: int, kill: bool = False):
        hit_info = {
            "object": "hit",
            "id": self.id,
            "target_id": target_id,
            "damage": damage,
            "kill": kill,
        }

        hit_info_encoded = json.dumps(hit_info).encode("utf8")
        try:
            self.client.send(hit_info_encoded)
        except socket.error as e:
            print(e)
