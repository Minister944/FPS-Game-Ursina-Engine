from ursina import *

class ParticleSystem():
    def __init__(self, 
        add_to_scene_entities=True, 
        position=Vec3(0,0,0), 
        color=color.black, 
        duration = 0.5, 
        speed = 0.1,
        number = 100,
        scale = 0.1):
        self.add_to_scene_entities=add_to_scene_entities 
        self.position=position
        self.color=color
        self.duration = duration
        self.speed = speed
        self.number = number
        self.scale = scale
        for x in range(number):
            Particl(position=self.position, 
            rotation=Vec3(random.randrange(0,360),random.randrange(0,360),random.randrange(0,360)),
            color = self.color,
            duration = self.duration,
            speed = self.speed,
            scale = self.scale
            )

class Particl(Entity):
    def __init__(self, 
        add_to_scene_entities=True, 
        position=Vec3(0,0,0), 
        rotation=Vec3(15,15,15),
        scale = 1,
        color=color.black, 
        duration = 1, 
        speed = 0.3):
        super().__init__(
            add_to_scene_entities,
            position = position,
            rotation = rotation,
            scale = scale,
            color = color,
            model = 'cube'

            )
        self.duration = duration
        self.t = 0
        self.speed = speed

    def update(self):
        self.t += time.dt
        if self.t >= self.duration:
            destroy(self)
            return

        self.position += self.forward * self.speed
        