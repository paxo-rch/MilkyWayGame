from ursina import *
from ursina.shaders import lit_with_shadows_shader
import random
from math import *


time_speed = 1
class BlackHole(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        self.blackhole_gravity = 1
        self.update_number = 0
        self.update_rate = 1
    def update(self):
        if self.update_number % self.update_rate == 0:
            self.position += self.velocity * time_speed
            for i in range(len(points)):
                points[i].velocity -= (points[i].position - Vec3(0, 0, 0)).normalized() * (1 / (distance(points[i].position, Vec3(0, 0, 0)) ** 2)) * self.blackhole_gravity * time_speed
        self.update_number += 1

class Star(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        self.update_number = 0
        self.update_rate = 1
    def update(self):
        if self.update_number % self.update_rate == 0:
            self.position += self.velocity * time.dt * time_speed
        self.update_number += 1

app = Ursina()

sky = Sky(texture='space.hdr')

points = []
numstars = 1000

center = BlackHole(model='sphere', color=color.black, scale=0.01, shader=lit_with_shadows_shader)

for i in range (numstars):
    point = Star(model='sphere', color=color.red, scale=1, shader=lit_with_shadows_shader)
    #1 unitée = 100 parsecs = 326 années lumière

    r = random.uniform(10,162.2)
    v = sqrt(center.blackhole_gravity / r) * 8
    a = random.uniform(0, 2 * pi)
    point.velocity = Vec3(v * cos(a + pi / 2), 0, v * sin(a + pi / 2))
    
    point.position = Vec3(r * cos(a), random.uniform(-10, 10), r * sin(a))
    
    points.append(point)
    
distances = []

for i in range(len(points)):
    for j in range(len(points)):
        if i != j:
            distances.append(distance(points[i].position, points[j].position))
            
print(max(distances))
print(min(distances))
print(sum(distances) / len(distances))
EditorCamera()

class Player(Entity):
    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['z'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['q']) + self.up * (held_keys['space'] - held_keys['shift'])
        ).normalized()

app.run()