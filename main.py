from ursina import *
from ursina.shaders import lit_with_shadows_shader

import random
from math import *

app = Ursina()

sky = Sky(texture='space.hdr')

points = []
numstars = 1000

class BlackHole(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        self.blackhole_gravity = 1
        self.update_number = 0
        self.update_rate = 1
    def update(self):
        if self.update_number % self.update_rate == 0:
            self.position += self.velocity
            for i in range(len(points)):
                points[i].velocity -= (points[i].position - Vec3(0, 0, 0)).normalized() * (1 / (distance(points[i].position, Vec3(0, 0, 0)) ** 2)) * self.blackhole_gravity
        self.update_number += 1

class Star(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        self.update_number = 0
        self.update_rate = 1
    def update(self):
        if self.update_number % self.update_rate == 0:
            self.position += self.velocity * time.dt
        self.update_number += 1
center = BlackHole(model='sphere', color=color.black, scale=1, shader=lit_with_shadows_shader)

for i in range (numstars):
    point = Star(model='sphere', color=color.red, scale=1, shader=lit_with_shadows_shader)
    
    r = random.uniform(5,200)
    v = sqrt(center.blackhole_gravity / r) * 5
    a = random.uniform(0, 2 * pi)
    point.velocity = Vec3(v * cos(a + pi / 2), v * sin(a + pi / 2), 0)
    
    point.position = Vec3(r * cos(a), r * sin(a), random.uniform(-10, 10))
    
    points.append(point)



EditorCamera()

class Player(Entity):
    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['z'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['q']) + self.up * (held_keys['space'] - held_keys['shift'])
        ).normalized()

app.run()