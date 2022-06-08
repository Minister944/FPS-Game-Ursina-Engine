from multiprocessing.sharedctypes import Value
from ursina import *
from particleSystem import *
from player import *
from globalVar import *

from ursina.shaders import lit_with_shadows_shader


ak_47_texture = load_texture('assets/gun/Tix_1.png')
ak_47_obj = 'assets/gun/ak_47.obj'
ACP_Smith_texture = load_texture('assets/gun/ACP_Smith.jpg')
ACP_Smith_obj = 'assets/gun/ACP_Smith.obj'


class Wepon(Entity):
    def __init__(self,
                 add_to_scene_entities=True,
                 distance=100,
                 who=None,
                 global_var=None,
                 **kwargs):
        super().__init__(add_to_scene_entities, **kwargs, shader=lit_with_shadows_shader,)

        self.global_var = global_var
        self.distance = distance
        self.maxAmo = 30
        self.amo = self.maxAmo
        self.magazine = 4
        self.hitTime = 0.05
        self.reloadTime = 3.0
        self.damage = 20
        self.recoil = 2
        self.startHit = time.time()
        self.startReload = time.time()
        self.who = who
        self.who.gui(self.amo, self.magazine)

    def on_enable(self):
        try:
            self.who.gui(self.amo, self.magazine)
        except:
            pass

    def update(self):
        if held_keys['left mouse'] and not self.global_var.Build and time.time() - self.startHit > self.hitTime and not self.global_var.Reload:
            self.global_var.Shooting = True
            self.startHit = time.time()
            self.hit()
        elif self.global_var.Shooting and not held_keys['left mouse']:
            self.global_var.Shooting = False
        elif not self.global_var.Reload and held_keys['r'] and self.magazine > 0 and time.time() - self.startReload > self.reloadTime:
            self.animate_rotation(value=Vec3(0, 50, 0), duration=self.reloadTime/2)
            self.global_var.Reload = True
            self.startReload = time.time()
            self.reload()
        elif self.global_var.Reload and not held_keys['r'] and time.time() - self.startReload > self.reloadTime:
            self.animate_rotation(value=Vec3(0, 90, 0),)
            self.global_var.Reload = False
            self.who.speed = 7
        elif not self.global_var.Aiming and held_keys['right mouse']:
            self.global_var.Aiming = True
            self.aiming()
        elif self.global_var.Aiming and not held_keys['right mouse']:
            self.global_var.Aiming = False
            self.aiming()

    def hit(self):
        if self.amo > 0:

            v1, v2, v3, rotation_x, rotation_y = self.recoiling(
                forward=self.who.camera_pivot.forward, rotation_x=self.who.camera_pivot.rotation_x, rotation_y=self.who.rotation_y)
            self.who.camera_pivot.animate(
                name='rotation_x', value=rotation_x, duration=.01)
            # self.who.camera_pivot.rotation_x = rotation_x
            self.who.rotation_y = rotation_y

            ray = raycast(
                origin=self.who.camera_pivot.world_position,
                direction=LVector3f(v1, v2, v3),
                distance=self.distance,
                ignore=(self.who,))

            if ray.hit:
                print(type(ray.entities[-1]).__name__ == 'Enemy')
                ParticleSystem(position=ray.world_point, number=10, speed=1, duration=0.03)        
                if type(ray.entities[-1]).__name__ == 'Enemy':   
                    ray.entities[-1].hit(self.damage, target=self)

            # if ray.hit:
            #     print(type(ray.entities[-1]).__name__ == 'Enemy')
            #     ParticleSystem(position=ray.world_point, number=10, speed=1, duration=0.03)        
            #     try:
            #          ray.entities[-1].hit(self.damage, target=self)
            #     except Exception:
            #         print("nothing")

            Audio("assets\\lututu.wav", volume=0.02)
            self.amo -= 1
            self.who.gui(self.amo, self.magazine)

    def recoiling(self, forward, rotation_x, rotation_y):
        rotation_x -= self.recoil * (random.randint(33, 66)/100)
        rotation_y -= self.recoil * (random.randint(33, 66)/100)
        v1, v2, v3 = forward
        v1, v2, v3 = v1+v1*(random.randint(-6, 6)/100), v2+v2 * \
            (random.randint(-6, 6)/100), v3+v3*(random.randint(-6, 6)/100)

        return v1, v2, v3, rotation_x, rotation_y

    def reload(self):
        self.who.speed = 3
        self.magazine -= 1
        self.amo = self.maxAmo
        Audio("assets\\gun-reload-sound-fx_C_minor", volume=0.1)
        self.who.gui(self.amo, self.magazine)

    def aiming(self):
        if self.global_var.Aiming:
            self.animate_position(value=Vec3(0, -0.5, -0.07), duration=0.07)
            self.animate_rotation(value=Vec3(0, 90, 0), duration=0.07)
            # self.rotation = Vec3(0, 90, 0)
            # self.position = Vec3(0, -0.5, -0.07)
        else:
            self.animate_position(value=Vec3(0.6, -0.7, 0.85), duration=0.07)
            self.animate_rotation(value=Vec3(2, 88, 1), duration=0.07)
            # self.rotation = Vec3(2, 88, 1)
            # self.position = Vec3(0.6, -0.7, 0.85)


class ak_47(Wepon):
    def __init__(self, who=None, global_var=None,):
        super().__init__(

            parent=who.camera_pivot,
            model=ak_47_obj,
            texture=ak_47_texture,
            scale=0.8,
            rotation=Vec3(2, 88, 1),
            position=Vec3(0.6, -0.7, 0.85),
            who=who,
        )
        self.global_var = global_var


class ACP_Smith(Wepon):
    def __init__(self, who=None, global_var=None,):
        super().__init__(
            parent=who.camera_pivot,
            model=ACP_Smith_obj,
            texture=ACP_Smith_texture,
            scale=0.8,
            rotation=Vec3(2, 88, 1),
            position=Vec3(0.6, -0.7, 0.85),
            who=who,
        )
        self.global_var = global_var
        self.hitTime = 0.2
        self.reloadTime = 2
        self.damage = 70
        self.maxAmo = 7
        self.amo = self.maxAmo
        self.magazine = 8
        self.recoil = 20
        self.who.gui(self.amo, self.magazine)

    def recoiling(self, forward, rotation_x, rotation_y):
        rotation_x -= self.recoil * (random.randint(33, 66)/100)
        rotation_y -= self.recoil * (random.randint(-3, 3)/100)
        v1, v2, v3 = forward
        return v1, v2, v3, rotation_x, rotation_y

class Prefabs(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.black33,
            **kwargs,
        )