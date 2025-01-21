from ursina import *
from ursina.shaders import lit_with_shadows_shader

import random

app = Ursina()

points = []

for i in range (100):
    point = Entity(model='sphere', color=color.random_color(), scale=0.1, shader=lit_with_shadows_shader)
    point.position = Vec3(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10))

EditorCamera()  # add camera controls for orbiting and moving the camera

class Player(Entity):

    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()  # get the direction we're trying to walk in.

        origin = self.world_position + (self.up*.5) # the ray should start slightly up from the ground so we can walk up slopes or walk over small objects.
        hit_info = raycast(origin , self.direction, ignore=(self,), distance=.5, debug=False)
        if not hit_info.hit:
            self.position += self.direction * 5 * time.dt
        else:
            print(hit_info.entity)

Player(model='cube', origin_y=-.5, color=color.orange)
wall_left = Entity(model='cube', collider='box', scale_y=3, origin_y=-.5, color=color.azure, x=-4)
wall_right = duplicate(wall_left, x=4)
camera.y = 2
app.run()

