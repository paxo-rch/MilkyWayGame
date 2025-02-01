import structure

from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.slider import Slider

app = Ursina()

window.fps_counter.enabled = False

sky = Sky(texture='space.hdr')

mass_star = 2e30        # kg
mass_planet = 5e24      # kg
radius_galaxy = 3e16    # m
radius_planet = 500e9   # m

factor = 1 #1e-25
time_factor = 10

objects = []

for i in range(1000):
    s = structure.Star(structure.u, 1, random.randint(10000, 100000)/1000)
    s.o = Entity(model='sphere', color=color.white, scale=0.5, shader=lit_with_shadows_shader, collider='box')
    s.o.o = s
    objects.append(s)
    
    for j in range(2):
        p = structure.Planet(s, 1, random.randint(500, 1000)/1000)
        p.o = Entity(model='sphere', color=color.azure, scale=0.1, shader=lit_with_shadows_shader, collider='box')
        p.o.visible
        p.o.o = p
        objects.append(p)

for i in objects:
    i.updateMass()
    i.o.on_click = lambda i=i: p.followEntity(i.o)

for i in objects:
    i.genetateOrbit(i.radius)

def update(t=True):
    #print(camera.zoom,camera.world_scale)
    if(t):
        structure.u.t = time.perf_counter() / time_factor

    for i in structure.u.children:
        i.updateAll()
    
    for i in objects:
        pos = i.getAbsolutePosition()
        i.o.position = Vec3(pos.x * factor, pos.y * factor, pos.z * factor)
    
    if held_keys['escape']:
        p.followEntity(None)
    
c = EditorCamera()

class Player(Entity):
    def __init__(self):
        self.follow = None
        self.script = c.add_script(SmoothFollow(target=objects[0].o, offset=Vec3(0, 0, 0), speed=5))
        
        super().__init__()
        
    def followEntity(self, e):
        if(self.follow == e):
            return
        
        self.script.target = e
        self.follow = e
        
        if e is None:
            for i in objects:
                if(isinstance(i, structure.Planet)):
                    i.o.visible = False
        else:
            if(isinstance(e.o, structure.Star)):
                for i in objects:
                    if(isinstance(i, structure.Planet)):
                        if(i.parent == e.o):
                            i.o.visible = True
                        else:
                            i.o.visible = False
    
    def update(self):
        self.direction = Vec3(
            self.forward * (held_keys['z'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['q']) + self.up * (held_keys['space'] - held_keys['shift'])
        ).normalized()
    
p = Player()

app.run()