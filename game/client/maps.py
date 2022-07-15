from ursina import Entity, load_texture
from ursina.lights import DirectionalLight
from ursina.shaders import lit_with_shadows_shader

stone_texture = load_texture("assets/maps/Grid-Level2.png")
sky_texture = load_texture("assets/skybox.png")


class Map:
    def __init__(self):
        self.name = None
        self.description = None

    def list_map():
        return [cls for cls in Map.__subclasses__()]


class Test(Map, Entity):
    def __init__(self):
        super().__init__()

        self.name = "Test"
        self.description = "Map made for testing"

        pivot = Entity()

        DirectionalLight(parent=pivot, y=4, z=4, shadows=True, rotation=(45, -45, 45))
        Entity(
            model="plane",
            collider="box",
            scale=64,
            texture=stone_texture,
            texture_scale=(16, 16),
            shader=lit_with_shadows_shader,
        )

        # Light Sky not working

        # Entity(
        #     model='sphere',
        #     texture=sky_texture,
        #     scale=1000,
        #     double_sided=True)

    def map_info():
        map_info = {
            "name": "Test",
            "description": "Map made for testing",
            "spawn_attacker": [
                (1, 0, 1),
                (2, 0, 2),
                (3, 0, 3),
                (4, 0, 4),
                (5, 0, 5),
            ],
            "spawn_defenders": [
                (11, 0, 1),
                (12, 0, 2),
                (13, 0, 3),
                (14, 0, 4),
                (15, 0, 5),
            ],
        }

        return map_info
