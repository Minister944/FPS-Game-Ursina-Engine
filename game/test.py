from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


app = Ursina()

ground = Entity(model='plane', texture='grass', scale=10, collider='box')
player = FirstPersonController(model='cube', origin_y=-.5, color=color.orange, has_pickup=False)
camera.z = -5

pickup = Entity(model='sphere', position=(1,.5,3))

def update():
    print( distance(player, pickup))
    if not player.has_pickup and distance(player, pickup) < pickup.scale_x / 2:
        print('pickup')

        player.has_pickup = True
        pickup.animate_scale(0, duration=.1)
        destroy(pickup, delay=.1)

app.run()