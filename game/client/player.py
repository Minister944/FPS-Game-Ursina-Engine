from ursina import *
from weapon import ak_47, ACP_Smith, Prefabs
from ursina.prefabs.first_person_controller import FirstPersonController
from globalVar import globalVariable
from ursina.shaders import lit_with_shadows_shader


class Player(FirstPersonController):
    def __init__(self, position: Vec3(0, 0, 0)):
        super().__init__(
            position=position,
            model="cube",
            jump_height=2.5,
            jump_duration=0.4,
            origin_y=-1,
            collider="box",
            speed=7,
        )
        self.global_var = globalVariable()

        self.hp = 100

        self.text = Text(text="0/0", x=0.8, y=-0.45)
        self.hp = Text(
            text="<image:assets/NewImage-2>   " + str(self.hp), x=-0.85, y=-0.45
        )
        self.weapons = [
            ak_47(who=self, global_var=self.global_var),
            ACP_Smith(who=self, global_var=self.global_var),
        ]
        self.weapons[0].enabled = False
        self.weapons[0].enabled = True

        self.current_weapon = 0
        self.switch_weapon()

    def player_to_dict(self):
        resultat = {
            "position": (self.world_x, round(self.world_y, 4), self.world_z),
            "rotation": self.rotation_y,
            "global_var": {
                "Crouch": self.global_var.Crouch,
                "Running": self.global_var.Running,
                "Reload": self.global_var.Reload,
                "Aiming": self.global_var.Crouch,
                "Shooting": self.global_var.Crouch,
                "Build": self.global_var.Crouch,
            },
            "hp": self.hp,
            "weapons": [type(wepon).__name__ for wepon in self.weapons],
            "current_weapon": self.current_weapon,
        }
        return resultat

    def switch_weapon(self):
        for i, v in enumerate(self.weapons):
            if i == self.current_weapon:
                v.enabled = True
            else:
                v.enabled = False

    def update(self):
        if (
            not self.global_var.Reload
            and not self.global_var.Running
            and held_keys["shift"]
        ):
            self.global_var.Running = True
            self.speed = 10
        elif (
            not self.global_var.Reload
            and self.global_var.Running
            and not held_keys["shift"]
        ):
            self.global_var.Running = False
            self.speed = 7
        elif held_keys["control"]:
            self.camera_pivot.position = Vec3(0, 1.5, 0)
        elif not held_keys["control"]:
            self.camera_pivot.position = Vec3(0, 2, 0)
        return super().update()

    def input(self, key):
        try:
            self.current_weapon = int(key) - 1
            self.switch_weapon()
        except ValueError:
            pass

        if key == "scroll up":
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
            self.switch_weapon()
        if key == "scroll down":
            self.switch_weapon()
            self.current_weapon = (self.current_weapon - 1) % len(self.weapons)

        return super().input(key)

    def update_hud(self, ammo, magazine):
        self.text.text = str(ammo) + "/" + str(magazine)


class Enginer(Player):
    def __init__(self, position: Vec3(0, 0, 0)):
        super().__init__(position)
        self.hp = 125
        self.barrier = Prefabs()
        self.barrier_count = 3
        self.barrier_count_old = self.barrier_count

    def update(self):
        if held_keys["f"] and self.barrier_count > 0:

            self.global_var.Build = True
            if self.barrier_count == self.barrier_count_old:
                self.barrier.visible = True

            ray = raycast(
                self.camera_pivot.world_position,
                self.camera_pivot.forward,
                distance=10,
                ignore=(self,),
            )
            if ray.hit:
                self.barrier.world_position = ray.world_point + Vec3(0, 0.5, 0)
                if self.barrier_count == self.barrier_count_old and mouse.left:
                    self.barrier_count -= 1
                    e = Entity(
                        model="cube",
                        color=color.orange,
                        position=ray.world_point + Vec3(0, 0.5, 0),
                        collider="box",
                        shader=lit_with_shadows_shader,
                    )
                    self.barrier.visible = False

        else:
            self.barrier_count_old = self.barrier_count
            self.barrier.visible = False
            self.global_var.Build = False
        return super().update()


class Medic(Player):
    pass
