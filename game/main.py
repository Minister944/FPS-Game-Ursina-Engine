from ursina import *
from ursina.shaders import lit_with_shadows_shader

import threading
import socket
from network import Network

app = Ursina(fullscreen=False, vsync=False)
window.borderless = False 

from player import *
from particleSystem import *
window.title = "FPS Ursina"

main_player = Enginer(Vec3(5, 0, 0))
prev_pos = main_player.world_position
prev_dir = main_player.world_rotation_y
enemies = []

# username = input("Enter your username: ")
username = "Kacper"
while True:
    # server_addr = input("Enter server IP: ")
    # server_port = input("Enter server port: ")
    server_addr = "0.0.0.0"
    server_port = 1024
    try:
        server_port = int(server_port)
    except ValueError:
        print("\nThe port you entered was not a number, try again with a valid port...")
        continue

    n = Network(server_addr, server_port, username)
    n.settimeout(5)

    error_occurred = False

    try:
        n.connect()
    except ConnectionRefusedError:
        print("\nConnection refused! This can be because server hasn't started or has reached it's player limit.")
        # error_occurred = True
    except socket.timeout:
        print("\nServer took too long to respond, please try again...")
        # error_occurred = True
    except socket.gaierror:
        print("\nThe IP address you entered is invalid, please try again with a valid address...")
        # error_occurred = True
    finally:
        n.settimeout(None)

    if not error_occurred:
        break


class Enemy(Entity):
    def __init__(self, position: Vec3, identifier: str, username: str):
        super().__init__(
            position=position,
            model='cube',
            collider='box',
            shader=lit_with_shadows_shader,
            scale_y=2,
            origin_y=-.5,
            color=color.light_gray,
        )
        self.hp = 100
        self.id = identifier
        self.username = username

        self.name_tag = Text(
            parent=self,
            text=username,
            position=Vec3(0, 1.3, 0),
            scale=Vec2(5, 3),
            billboard=True,
            origin=Vec2(0, 0)
        )

    def hit(self, damage, target):
        print(target, "hit", self, "damage:", damage)
        self.hp -= damage
        if self.hp <= 0:
            destroy(self)

def receive():
    while True:
        try:
            info = n.receive_info()
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

        print(info)

msg_thread = threading.Thread(target=receive, daemon=True)
msg_thread.start()

grass_texture = load_texture('assets/grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/arm_texture.png')
ak_47_texture = load_texture('assets/gun/Tix_1.png')


def input(key):
    if key == 'escape':
        mouse.locked = False
        mouse.visible = True
    if key == 'q':
        quit()

def update():
    if main_player.hp > 0:
        global prev_pos, prev_dir
        
        if prev_pos != round(main_player.world_position) or prev_dir != round(main_player.world_rotation_y):
            n.send_player(main_player)
            prev_pos = round(main_player.world_position)
            prev_dir = round(main_player.world_rotation_y)

# def update():
#     if player.health > 0:
#         global prev_pos, prev_dir

#         if prev_pos != player.world_position or prev_dir != player.world_rotation_y:
#             n.send_player(player)

#         prev_pos = player.world_position
#         prev_dir = player.world_rotation_y


class Bullet(Entity):
    def __init__(self, distance=50, lifetime=10, **kwargs):
        super().__init__(**kwargs)
        self.distance = distance
        self.lifetime = lifetime
        self.start = time.time()

    def update(self, **kwargs):
        ray = raycast(self.world_position, self.forward,
                      distance=self.distance, ignore=(self, main_player))
        if not ray.hit and time.time() - self.start < self.lifetime:
            self.world_position += self.forward * self.distance * time.dt
        else:
            destroy(self)
        if ray.hit:
            ParticleSystem(position=ray.world_point,
                           number=10, speed=1, duration=0.03)
            try:
                ray.entities[-1].hit(damage=20, target=None)
            except:
                print("nothing method")
            destroy(self)



class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/block',
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            scale=0.5,)

    # def input(self, key):
    #     if self.hovered:
    #         if key == 'left mouse down':
    #             if block_pick == 3:
    #                 voxel = Voxel(position=self.position +
    #                               mouse.normal, texture=stone_texture)
    #             if block_pick == 4:
    #                 voxel = Voxel(position=self.position +
    #                               mouse.normal, texture=brick_texture)
    #             if block_pick == 5:
    #                 voxel = Voxel(position=self.position +
    #                               mouse.normal, texture=dirt_texture)
    #         if key == 'right mouse down':
    #             destroy(self)


class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150,
            double_sided=True)

# for x in range(16):
#     for z in range(16):
#         Voxel((x, 0, z))

plane = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
#player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

pivot = Entity()
DirectionalLight(parent=pivot, y=4, z=4, shadows=True, rotation=(45, -45, 45))


app.run()
