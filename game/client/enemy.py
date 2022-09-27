from ursina import Entity, Text, Vec2, Vec3, color, destroy
from ursina.shaders import lit_with_shadows_shader

import globalVar
from weapon import ACP_Smith_obj, ACP_Smith_texture, ak_47_obj, ak_47_texture


class EnemyWeapon_AK_47(Entity):
    def __init__(self, who=None):
        super().__init__(
            model=ak_47_obj,
            texture=ak_47_texture,
            scale=0.45,
            rotation=Vec3(2, 88, 1),
            position=Vec3(0.6, 1.4, 0.85),
            parent=who,
            enabled=False,
        )


class EnemyWeapon_ACP_Smith(Entity):
    def __init__(self, who=None):
        super().__init__(
            model=ACP_Smith_obj,
            texture=ACP_Smith_texture,
            scale=0.45,
            rotation=Vec3(2, 88, 1),
            position=Vec3(0.6, 1.4, 0.85),
            parent=who,
            enabled=False,
        )


class Enemy(Entity):
    def __init__(
        self,
        identifier: str,
        username: str,
        position: Vec3 = (0, 0, 0),
    ):
        super().__init__(position=position, shader=lit_with_shadows_shader)

        self.hp = 100
        self.id = identifier
        self.username = username
        self.global_var = globalVar.globalVariable()

        self.current_weapon_old = 0
        self.current_weapon = 0
        self.weapons = [
            EnemyWeapon_AK_47(who=self),
            EnemyWeapon_ACP_Smith(who=self),
        ]
        self.weapons[0].enabled = True

        self.name_tag = Text(
            parent=self,
            text=username,
            position=Vec3(0, 2.4, 0),
            scale=Vec2(5, 3),
            billboard=True,
            origin=Vec2(0, 0),
        )

        self.head = Entity(
            parent=self,
            position=Vec3(0, 2, 0),
            scale=Vec3(0.6, 0.6, 0.6),
            model="cube",
            collider="box",
            texture="brick",
        )

        # TODO texture face ...
        # TODO fix only hit head working

        self.body = Entity(
            parent=self,
            position=Vec3(0, 1.2, 0),
            scale=Vec3(1, 1, 0.5),
            model="cube",
            collider="box",
            color=color.blue,
        )

        self.leg_left = Entity(
            parent=self,
            position=Vec3(0.3, 0.2, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray,
        )

        self.leg_right = Entity(
            parent=self,
            position=Vec3(-0.3, 0.2, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray,
        )

        self.arm_left = Entity(
            parent=self,
            position=Vec3(0.5, 1.15, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray,
        )

        self.arm_right = Entity(
            parent=self,
            position=Vec3(-0.5, 1.15, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray,
        )

    def hit(self, damage, target):
        print(target, "hit", self, "damage:", damage)
        self.hp -= damage
        if self.hp <= 0:
            globalVar.connection.hit(target_id=self.id, damage=damage, kill=True)
            destroy(self)
            return
        globalVar.connection.hit(target_id=self.id, damage=damage)

    def update(self):

        if self.current_weapon_old != self.current_weapon:
            self.current_weapon_old = self.current_weapon
            self.switch_weapon()

    def switch_weapon(self):
        for i, v in enumerate(self.weapons):
            if i == self.current_weapon:
                v.enabled = True
            else:
                v.enabled = False
