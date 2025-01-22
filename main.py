from ursina import *
from ursina.shaders import lit_with_shadows_shader
import random
from math import *

time_speed = 1 # secondes (r) par seconde (g)
time_rate = 1 * time_speed # (250000000*365*24*3600*10000) * time_speed
base_time = time.time()
time_count = 0

scale = 100 / 5e20

class BlackHole(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        self.blackhole_gravity = 1.9884e30
        self.update_number = 0
        self.update_rate = 1
    def update(self):
        global time_count, base_time
        
        
        time_count += time.dt*time_rate
        
        #print(time_count)

class Star(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vec3(0, 0, 0)
        self.update_number = 0
        self.update_rate = 1
        
        self.initial_angle = 0
        self.orbit_radius = 0
        self.angular_velocity = 0
        
    def update(self):
        self.x = self.orbit_radius * scale * cos(self.initial_angle + self.angular_velocity * time_count)
        self.z = self.orbit_radius * scale * sin(self.initial_angle + self.angular_velocity * time_count)

app = Ursina()

sky = Sky(texture='space.hdr')

points = []
numstars = 1000

center = BlackHole(model='sphere', color=color.black, scale=0.01, shader=lit_with_shadows_shader)

for i in range (numstars):
    point = Star(model='sphere', color=color.red, scale=1, shader=lit_with_shadows_shader)
    #1 unitée = 100 parsecs = 326 années lumière

    rm = 5e20 # en m
    r = random.uniform(rm/20,rm)
    v = sqrt(center.blackhole_gravity * 6.674e-11 / r)
    a = random.uniform(0, 2 * pi)
    
    point.angular_velocity = v / r
    print(point.angular_velocity)
    point.orbit_radius = r
    point.initial_angle = a
    
    point.position = Vec3(0, 1 / (1 + exp((r * scale)/50*3 - 3))*random.uniform(-20, 20), 0)
    
    points.append(point)

"""distances = []

for i in range(len(points)):
    for j in range(len(points)):
        if i != j:
            distances.append(distance(points[i].position, points[j].position))
            
print(max(distances))
print(min(distances))
print(sum(distances) / len(distances))"""
EditorCamera()

class Player(Entity):
    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['z'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['q']) + self.up * (held_keys['space'] - held_keys['shift'])
        ).normalized()

app.run()