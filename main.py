from ursina import *
from ursina.shaders import lit_with_shadows_shader

import random
from math import *

app = Ursina()

points = []

class Star(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        
    def update(self):
        self.position += self.velocity

for i in range (100):
    point = Star(model='sphere', color=color.random_color(), scale=0.1, shader=lit_with_shadows_shader)
    point.position = Vec3(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-1, 1))
    points.append(point)

def update():
    global points
    for i in range(len(points)):
        for j in range(len(points)):
            if(i != j):
                points[i].velocity -= (points[i].position - points[j].position).normalized() * min((1 / (distance(points[i].position, points[j].position) ** 2)),0.01) * 0.001

EditorCamera()

class Player(Entity):
    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['z'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['q']) + self.up * (held_keys['space'] - held_keys['shift'])
        ).normalized()

app.run()