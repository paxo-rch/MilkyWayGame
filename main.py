from ursina import *
from ursina.shaders import lit_with_shadows_shader

import random
from math import *

app = Ursina()

sky = Sky(texture='space.hdr')

points = []
blackhole = 1
numstars = 1000

colors = [color.rgb(9, 165, 235) for _ in range(1)] + [color.rgb(245, 86, 75) for _ in range(1)] + [color.rgb(255, 200, 255) for _ in range(1)]

class Star(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        
    def update(self):
        self.position += self.velocity * time.dt

for i in range (numstars):
    point = Star(model='sphere', color=random.choice(colors), scale=0.2, shader=lit_with_shadows_shader, double_sided=True, render_mode=1, light_type='point', light_color=color.white, light_range=1000)
    
    r = random.uniform(5,200)
    v = sqrt(blackhole / r) * 8
    a = random.uniform(0, 2 * pi)
    point.velocity = Vec3(v * cos(a + pi / 2), 0, v * sin(a + pi / 2))
    
    point.position = Vec3(r * cos(a), random.uniform(-10, 10), r * sin(a))
    
    points.append(point)

def update():
    global points
    for i in range(len(points)):
        points[i].velocity -= (points[i].position - Vec3(0, 0, 0)).normalized() * (1 / (distance(points[i].position, Vec3(0, 0, 0)) ** 2)) * blackhole

EditorCamera()

class Player(Entity):
    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['z'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['q']) + self.up * (held_keys['space'] - held_keys['shift'])
        ).normalized()

app.run()