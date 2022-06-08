from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina(fullscreen=False, vsync=False)
# my file
from player import *
from particleSystem import *

playerr = Enginer(Vec3(5, 0, 0))


grass_texture = load_texture('assets/grass_block.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/arm_texture.png')
ak_47_texture = load_texture('assets/gun/Tix_1.png')
block_pick = 1
build = False

# def update():
#     print(globalVar.Reload, globalVar.Aiming, globalVar.Shooting, globalVar.Crouch, globalVar.Running)


def input(key):
    global block_pick
    global build
    global prefabs
    # if key == 'e' and not build:
    #     build = True
    #     prefabs = Prefabs()
    # elif key == 'e' and build:
    #     build = False
    #     destroy(prefabs)

    if held_keys['1']:
        block_pick = 1
    if held_keys['2']:
        block_pick = 2
    if held_keys['3']:
        block_pick = 3
    if held_keys['4']:
        block_pick = 4


class Bullet(Entity):
    def __init__(self, distance=50, lifetime=10, **kwargs):
        super().__init__(**kwargs)
        self.distance = distance
        self.lifetime = lifetime
        self.start = time.time()

    def update(self, **kwargs):
        ray = raycast(self.world_position, self.forward,
                      distance=self.distance, ignore=(self, playerr))
        if not ray.hit and time.time() - self.start < self.lifetime:
            self.world_position += self.forward * self.distance * time.dt
        else:
            destroy(self)
        if ray.hit:
            #Particl(position=ray.world_point, rotation=Vec3(random.randrange(0,360),random.randrange(0,360),random.randrange(0,360)))
            ParticleSystem(position=ray.world_point,
                           number=10, speed=1, duration=0.03)
            try:
                ray.entities[-1].hit(damage=20, target=None)
            except:
                print("nothing method")
            destroy(self)


class Enemy(Entity):
    def __init__(self, position=(0, 0, 0), hp=100, **kwargs):
        super().__init__(
            position=position,
            model='cube',
            collider='box',
            shader=lit_with_shadows_shader,
            scale_y=2,
            origin_y=-.5,
            color=color.light_gray,
            **kwargs
        )
        self.hp = hp

    def hit(self, damage, target):
        print(target, "hit", self, "damage:", damage)
        self.hp -= damage
        if self.hp <= 0:
            destroy(self)

    def update2(self):
        dist = distance_xz(playerr.position, self.position)

        if dist > 40:
            return
        self.look_at_2d(playerr.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0),
                           self.forward, 30, ignore=(self,))
        if hit_info.entity == playerr:
            if dist > 2:
                self.position += self.forward * time.dt * 5


# class Prefabs(Entity):f
#     def __init__(self, **kwargs):
#         super().__init__(
#             model='cube',
#             color=color.black33,
#             **kwargs,
#         )

#     ray = None

#     def update(self, **kwargs):
#         self.ray = raycast(playerr.camera_pivot.world_position,
#                            playerr.camera_pivot.forward, distance=10, ignore=(playerr,))
#         if self.ray.hit:
#             self.world_position = self.ray.world_point + Vec3(0, 0.5, 0)

#     def input(self, key):
#         if key == 'left mouse down' and self.ray != None:
#             e = Entity(model='cube', color=color.orange, position=self.ray.world_point +
#                        Vec3(0, 0.5, 0), collider='box', shader=lit_with_shadows_shader)
#             global build
#             build = False
#             destroy(self)


class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='assets\\block',
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            scale=0.5,)

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                if block_pick == 3:
                    voxel = Voxel(position=self.position +
                                  mouse.normal, texture=stone_texture)
                if block_pick == 4:
                    voxel = Voxel(position=self.position +
                                  mouse.normal, texture=brick_texture)
                if block_pick == 5:
                    voxel = Voxel(position=self.position +
                                  mouse.normal, texture=dirt_texture)
            # if key == 'right mouse down':
            #     destroy(self)


class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150,
            double_sided=True)


class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=playerr.camera_pivot,
            model='assets\\gun\\ak_47.obj',
            texture=ak_47_texture,
            scale=0.8,
            rotation=Vec3(2, 88, 1),
            position=Vec3(0.6, -0.7, 0.85),
            shader=lit_with_shadows_shader
        )
        self.scope = False

    def update(self):
        if held_keys['right mouse']:
            self.rotation = Vec3(0, 90, 0)
            self.position = Vec3(0, -0.5, -0.07)
        else:
            self.rotation = Vec3(2, 88, 1)
            self.position = Vec3(0.6, -0.7, 0.85)

#Entity(model='plane', collider='box', texture=grass_texture, scale=100, color=color.gray, shader=lit_with_shadows_shader)


for x in range(16):
    for z in range(16):
        Voxel((x, 0, z))

#player = FirstPersonController(model='cube', color=color.orange, origin_y=-.5, speed=8)
#player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

#wepon = ak_47(who=playerr)

#skybox = Sky()
#hand = Hand()
enemy = Enemy()
pivot = Entity()
DirectionalLight(parent=pivot, y=4, z=4, shadows=True, rotation=(45, -45, 45))
app.run()
