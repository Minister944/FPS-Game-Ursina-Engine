from ursina import Entity, load_texture, Vec3
from ursina.lights import DirectionalLight
from ursina.shaders import lit_with_shadows_shader

stone_texture = load_texture('assets/maps/Grid-Level2.png')
sky_texture = load_texture('assets/skybox.png')


class Map:
    def __init__(self):
        self.name = None
        self.description = None

    def load_map(self, map):

        if map == "test":
            self.name = "Test"
            self.description = "Map made for testing"
            Test.generate()
        else:
            return False
        return True

    # def list_map():
    #     return [cls for cls in Map.__subclasses__()]


class Test(Entity):
    def __init__(self, add_to_scene_entities=True, **kwargs):
        super().__init__(add_to_scene_entities, **kwargs)

    def generate():
        pivot = Entity()


        DirectionalLight(parent=pivot, y=4, z=4, shadows=True, rotation=(45, -45, 45))
        Entity(model='plane', collider='box', scale=64,
               texture=stone_texture, texture_scale=(16, 16), shader=lit_with_shadows_shader,)
        # Entity(
        #     model='sphere',
        #     texture=sky_texture,
        #     scale=1000,
        #     double_sided=True)

    def spawn_places():
        spawn_point = {
            "spawn_attacker": [
                Vec3(1, 0, 1), Vec3(2, 0, 2), Vec3(3, 0, 3), Vec3(4, 0, 4), Vec3(5, 0, 5)],
            "spawn_defenders": [
                Vec3(11, 0, 1), Vec3(12, 0, 2), Vec3(13, 0, 3), Vec3(14, 0, 4), Vec3(15, 0, 5)]}
        return spawn_point
