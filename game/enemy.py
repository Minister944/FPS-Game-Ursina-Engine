from ursina import Entity, Text, Vec2, Vec3, color,load_texture
from ursina.shaders import lit_with_shadows_shader


class Enemy(Entity):
    def __init__(self, position: Vec3, identifier: str, username: str):
        super().__init__(position=position, shader=lit_with_shadows_shader)

        self.hp = 100
        self.id = identifier
        self.username = username

        self.name_tag = Text(
            parent=self,
            text=username,
            position=Vec3(0, 2.4, 0),
            scale=Vec2(5, 3),
            billboard=True,
            origin=Vec2(0, 0)
        )

        self.head = Entity(
            parent=self,
            position=Vec3(0, 2, 0),
            scale=Vec3(0.6, 0.6, 0.6),
            model="cube",
            collider="box",
            color=color.pink,
            texture="brick"
        )


        #TODO texture face ...


        self.body = Entity(
            parent=self,
            position=Vec3(0, 1.2, 0),
            scale=Vec3(1, 1, 0.5),
            model="cube",
            collider="box",
            color=color.blue
        )

        self.leg_left = Entity(
            parent=self,
            position=Vec3(0.3, 0.2, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray
        )

        self.leg_right = Entity(
            parent=self,
            position=Vec3(-0.3, 0.2, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray
        )

        self.arm_left = Entity(
            parent=self,
            position=Vec3(0.5, 1.15, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray
        )

        self.arm_right = Entity(
            parent=self,
            position=Vec3(-0.5, 1.15, 0),
            scale=Vec3(0.4, 1, 0.4),
            model="cube",
            collider="box",
            color=color.light_gray
        )


    # def hit(self, damage, target):
    #     print(target, "hit", self, "damage:", damage)
    #     self.hp -= damage
    #     if self.hp <= 0:
    #         destroy(self)
