import pygame
import math
import random
import time
import threading
import time
import socket
import numpy as np
import multiprocessing

G = 1

MAP_SCALE = 10
MAP_WIDTH = 1080 * MAP_SCALE
MAP_HEIGHT = 1080 * MAP_SCALE
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

PLANET_NUMBER = 500
MOON_NUMBER = 5




pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
objects = []
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 986))
    return s
def posX(x):
    return SCREEN_WIDTH//2 + (x - p.cursor[0]) * p.zoom

def posY(y):
    return SCREEN_HEIGHT//2 + (y - p.cursor[1]) * p.zoom

class Text:
    def __init__(self, text, x, y, size, relative=True, color=(255,255,255)):
        self.font = pygame.font.SysFont(None, size)
        self.text = text
        self.color = color
        self.render = self.font.render(self.text, True,pygame.Color(color[0],color[1],color[2]))
        self.x = x
        self.y = y
        self.size = size
        self.relative = relative
        textlist.append(self)
    def update(self):
        if self.relative:
            screen.blit(self.render, (posX(self.x)*p.zoom, posY(self.y)*p.zoom))
        else:
            screen.blit(self.render, (self.x, self.y))
    def setText(self, text):
        if self.text != text:
            self.text = text
            self.render = self.font.render(self.text, True,pygame.Color(self.color[0],self.color[1],self.color[2]))
    def remove(self):
        textlist.remove(self)
        
        

class Image:
    def __init__(self,image,scale=0.05):
        self.scale = scale
        self.image = image
        self.scaled_image = None
        imagelist.append(self)

    def update(self):
        if self.image is not None:
            self.scaled_image = pygame.transform.scale(self.image,(self.image.get_width()*p.zoom*self.scale,self.image.get_height()*p.zoom*self.scale))
    def remove(self):
        imagelist.remove(self)

class Object:
    t = 0

    def time():
        Object.t = time.time()*1
        #print(t)

    def __init__(self, x, y, m):
        self.x = x
        self.y = y
        self.m = m
        self.r = m
        self.transparent = False
        self.parent = None
        self.children = []
        
    def setParent(self, parent, orbit_radius):
        self.parent = parent
        self.parent.children.append(self)

        self.orbit_radius = orbit_radius
        self.angular_velocity = math.sqrt(G * 1 / self.orbit_radius) * 2 * math.pi
        self.first_angular_position = random.random() * 2 * math.pi
    
    def draw(self):
        x,y = posX(self.x), posY(self.y)
        if self.image is not None:
            screen.blit(self.image.scaled_image,(x-(self.image.image.get_height()/2)*p.zoom*self.image.scale,y-(self.image.image.get_width()/2)*p.zoom*self.image.scale))
        if not self.transparent:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), self.r * p.zoom)

    def drawAll(self):
        self.draw()
        for i in self.children:
            i.drawAll()

    def getAbsoluteX(self):
        return self.x

    def getAbsoluteY(self):
        return self.y

    def updateAll(self):
        self.update()

        for i in self.children:
            i.updateAll()

    def update(self):
        if(self.parent is not None):
            self.x = self.parent.getAbsoluteX() + self.orbit_radius * math.cos(self.first_angular_position + self.angular_velocity * Object.t)
            self.y = self.parent.getAbsoluteY() + self.orbit_radius * math.sin(self.first_angular_position + self.angular_velocity * Object.t)

class Player:
    def __init__(self, planet):
        self.planet = planet
        self.x = planet.getAbsoluteX()
        self.y = planet.getAbsoluteY()
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.speed = 1
        self.turn_speed = 16
        self.throw_speed = 100
        self.fuel = 100
        self.fuel_consumption = 0.1
        self.fuel_consumption_throw = 10
        self.projection_length = 100
        self.throw = False
        self.thrust = False
        self.landing_count = 1
        self.distance = 0
        #Path settings
        self.sonde_number = 360
        self.path = True
        self.path_step = 1
        self.path_antialiasing = False
        self.clean_path = True
        #Path variables
        self.show_accessible_planets = True
        self.sonde = None
        self.accessible_planets = []
        self.selected_planet = None

        self.map = False
        self.score = 0
        self.calculating = False
        self.icon_rocket = pygame.image.load("rocket.png")
        self.flame_animation = []
        self.i = 0

        # read the gif file
        for f in range(1, 29):
            self.flame_animation.append(pygame.image.load(f"flame_gif/{f}.gif"))

        self.oldMouseState = False
        self.oldMousePosition = [0,0]

        self.cursor = [MAP_WIDTH/2, MAP_HEIGHT/2]
        self.zoom = 1
    
    def draw(self):
        #pygame.draw.circle(screen, (255, 0, 0), (posX(self.x), posY(self.y)), 10 * p.zoom)

        a_mvt = self.angle


        self.i = (self.i+1) % len(self.flame_animation)

        sprite_size = (int(self.icon_rocket.get_width()*p.zoom*0.05), int(self.icon_rocket.get_height()*p.zoom*0.05))
        sprite_surface = pygame.Surface(sprite_size, pygame.SRCALPHA)
        rocket_scaled = pygame.transform.scale(self.icon_rocket, sprite_size)
        sprite_surface.blit(rocket_scaled, (0, 0))
        
        if(self.thrust):
            flame_scaled = pygame.transform.scale(self.flame_animation[self.i], [sprite_size[0]/5, sprite_size[1]/3])
            sprite_surface.blit(flame_scaled, (sprite_size[0]*0.4, sprite_size[0]*0.7))
            
        rotated_sprite = pygame.transform.rotate(sprite_surface, -90 - math.degrees(a_mvt))
        screen.blit(rotated_sprite, (posX(self.x)-rotated_sprite.get_width()//2, posY(self.y)-rotated_sprite.get_height()//2))

        if(not self.throw):
            pygame.draw.line(screen, (255, 255, 255), (posX(self.x), posY(self.y)), (posX(self.x + math.cos(self.angle) * self.projection_length), posY(self.y + math.sin(self.angle) * self.projection_length)))

    def update(self):
        start = time.perf_counter()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
                self.angle += self.turn_speed * math.pi / 360
        elif keys[pygame.K_LEFT]:
                self.angle -= self.turn_speed * math.pi / 360
        if self.throw:
            for i in objects:
                if(i != self.planet):
                    dist = math.sqrt((i.getAbsoluteX() - self.x)**2 + (i.getAbsoluteY() - self.y)**2)
                    
                    if(dist < 30):
                        self.x = i.getAbsoluteX()
                        self.y = i.getAbsoluteY()
                        self.vx = 0
                        self.vy = 0
                        self.throw = False
                        self.planet = i

                    elif(dist != 0):
                        dx = (i.getAbsoluteX() - self.x)
                        dy = (i.getAbsoluteY() - self.y)

                        angle = math.atan2(dy, dx)

                        a = 20000 * G / (dist**2)   # from F=ma and G=m1m2/r^2 as self.m = 1kg


                        self.vx += math.cos(angle) * a
                        self.vy += math.sin(angle) * a

            if(self.x > MAP_WIDTH):
                self.x = MAP_WIDTH
                self.vx = - abs(self.vx * 0.5)
            if(self.x < 0):
                self.x = 0
                self.vx = abs(self.vx * 0.5)
            if(self.y > MAP_HEIGHT):
                self.y = MAP_HEIGHT
                self.vy = - abs(self.vy * 0.5)
            if(self.y < 0):
                self.y = 0
                self.vy = abs(self.vy * 0.5)

            if keys[pygame.K_SPACE] and self.fuel > self.fuel_consumption:
                self.thrust = True
                self.fuel -= self.fuel_consumption
                self.vx += math.cos(self.angle) * self.speed
                self.vy += math.sin(self.angle) * self.speed
            else:
                self.thrust = False

            self.x += self.vx/10
            self.y += self.vy/10
            self.distance += math.sqrt((self.vx/10)**2 + (self.vy/10)**2)


        if(not self.throw) and self.calculating == False:

            if (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]) and self.fuel > self.fuel_consumption_throw:
                self.throw = True
                self.landing_count += 1 
                self.fuel -= self.fuel_consumption_throw
                self.vx = self.throw_speed * math.cos(self.angle)
                self.vy = self.throw_speed * math.sin(self.angle)


            elif keys[pygame.K_UP]:
                self.calculating = True
                self.pathdraw.clear()
                self.accessible_planets = []
                self.traj = Text("Calcul de trajectoire en cours...", SCREEN_HEIGHT/2, SCREEN_WIDTH/2, 100,relative=False, color=(255,255,255))
                threading.Thread(target=self.Trajectory, args=(p.planet,)).start()
            elif keys[pygame.K_s]:  # TEST ONLY
                self.calculating = True
                self.traj = Text("Calcul de trajectoire en cours...", SCREEN_HEIGHT/2, SCREEN_WIDTH/2, 100,relative=False, color=(255,255,255))
                sd = Sondes(objects,self.sonde_number,self)
                p.sonde = sd
                threading.Thread(target=sd.run, args=()).start()
            elif keys[pygame.K_c]:
                self.accessible_planets = []
                self.sonde = None
            elif keys[pygame.K_m]:
                self.map = not self.map
                time.sleep(0.1)
            elif keys[pygame.K_p]:
                self.path = not self.path
                time.sleep(0.1)


        
            mouseState = pygame.mouse.get_pressed()[0]

            # wheel for zoom


            if(mouseState and not self.oldMouseState):
                self.oldMousePosition = pygame.mouse.get_pos()
            
            
            if mouseState and not self.throw and not self.calculating:
                for i in objects:
                    if  i != self.planet and math.sqrt((self.oldMousePosition[0] - posX(i.x))**2 + (self.oldMousePosition[1] - posY(i.y))**2) < 20:
                        self.selected_planet = i
                        for j in self.accessible_planets:    
                            if j[0] == i:
                                self.angle = j[1]
                                break
                        break


            if(mouseState):
                pos = pygame.mouse.get_pos()
                self.cursor[0] -= (pos[0] - self.oldMousePosition[0]) / self.zoom
                self.cursor[1] -= (pos[1] - self.oldMousePosition[1]) / self.zoom

                if(self.cursor[0] < 0):
                    self.cursor[0] = 0
                if(self.cursor[0] > MAP_WIDTH - SCREEN_WIDTH):
                    self.cursor[0] = MAP_WIDTH - SCREEN_WIDTH
                if(self.cursor[1] < 0):
                    self.cursor[1] = 0
                if(self.cursor[1] > MAP_HEIGHT - SCREEN_HEIGHT):
                    self.cursor[1] = MAP_HEIGHT - SCREEN_HEIGHT
            else:
                self.oldMousePosition = pygame.mouse.get_pos()
            self.oldMouseState = mouseState
            self.oldMousePosition = pygame.mouse.get_pos()
        if(self.throw or pygame.mouse.get_pressed()[2]):
            self.cursor = [self.x, self.y]
        self.score = round(self.distance)
        end = time.perf_counter() - start

    def Trajectory(self,planet):
        distance_list = []
        angle_list = []
        liste_sonde = []
        for i in range(0,self.sonde_number):
            sonde = Sonde(planet,i)
            if self.path:
                self.pathdraw[sonde] = [[],[]]

            liste_sonde.append(sonde)

        while len(distance_list) < self.sonde_number:
            for i in liste_sonde:
                rsult = i.update()
                if self.path:
                    self.pathdraw[i][0].append((i.x, i.y))

                if rsult != None:
                    if self.path:
                        self.pathdraw[i][1].append((i.planete,rsult[1],rsult[0]))

                    if self.show_accessible_planets:
                        for j in self.accessible_planets:
                            if j[0] == i.planete and j[2] > rsult[1]:
                                self.accessible_planets.remove(j)
                        self.accessible_planets.append((i.planete,rsult[0],rsult[1]))
                    distance_list.append(rsult[1])
                    angle_list.append(rsult[0])
                    liste_sonde.remove(i)

        if self.clean_path and self.path:
            for i in self.pathdraw.keys():
                for j in self.pathdraw.keys():
                    if i != j and len(self.pathdraw[i]) != 0 and len(self.pathdraw[j]) != 0:
                        if self.pathdraw[i][1][0][0] == self.pathdraw[j][1][0][0]:
                            if self.pathdraw[i][1][0][1] < self.pathdraw[j][1][0][1]:
                                self.pathdraw[j][0] = []

                            else:
                                self.pathdraw[i][0] = []

        best_distance = max(distance_list)
        self.angle = angle_list[distance_list.index(best_distance)]
        textlist.remove(self.traj)
        self.calculating = False

class Sondes:
    def __init__(self,planets,n,parent=None):
        self.n = n
        self.parent = parent
        self.pos = np.zeros((n,2))   # positions of objects
        self.pos[:,0] = self.parent.x # set all sondes to player position
        self.pos[:,1] = self.parent.y
        self.steps = 0
        self.position_history = np.zeros((n,2,10000))

        self.spe = np.zeros((n,2))   # speed of objects
        for i in range(n):
            self.spe[i] = [math.cos(i*2*math.pi/n),math.sin(i*2*math.pi/n)]
        self.spe *= self.parent.throw_speed
    
        self.planet_copy = planets
        for i in range(len(self.planet_copy)):
            if(self.planet_copy[i] == self.parent.planet):
                self.planet_copy = np.delete(self.planet_copy,i)
                break

        if self.parent != None and self.parent.path:
            self.sonde_history = [np.zeros((10000, 2)) for i in range(n)]

        
        self.planets = np.zeros((len(self.planet_copy),2))    # positions of planets
        
        self.arrivals = np.zeros((len(self.planet_copy),3))  # for each planet, (sonde id, arrival time, angle)  # angle not calculated during simulation
        self.arrivals[:,0] = -1
        for i in range(len(self.planet_copy)):
            self.planets[i] = [self.planet_copy[i].x,self.planet_copy[i].y]

    def run(self):
        while True:
            diff = self.pos[:, np.newaxis, :] - self.planets[np.newaxis, :, :]
            dist = np.linalg.norm(diff, axis=-1)    # (n, planets) -> distance

            comp = np.where(np.any(dist < 30, axis=1), 0, 1)[:, None]
            
            mask = dist < 30  # shape: (n, number_of_planets)
            planet_reached = np.any(mask, axis=0)  # shape: (number_of_planets,)
            not_arrived = self.arrivals[:, 0] == -1
            to_record = planet_reached & not_arrived
            if np.any(to_record):
                first_sonde_ids = np.argmax(mask, axis=0)  # shape: (number_of_planets,)
                self.arrivals[to_record, 0] = first_sonde_ids[to_record]    # sonde id
                self.arrivals[to_record, 1] = self.steps

            self.spe -= G * (diff / dist[:, :, np.newaxis] ** 3).sum(axis=1) * 20000
            self.spe *= comp

            # Check if the sonde is out of the map, if yes, v <- -v/2 (v is spe)
            mask_right = self.pos[:, 0] > MAP_WIDTH
            mask_left = self.pos[:, 0] < 0
            mask_bottom = self.pos[:, 1] > MAP_HEIGHT
            mask_top = self.pos[:, 1] < 0

            self.spe[mask_right, 0] = -np.abs(self.spe[mask_right, 0]) / 2
            self.spe[mask_left, 0] = np.abs(self.spe[mask_left, 0]) / 2
            self.spe[mask_bottom, 1] = -np.abs(self.spe[mask_bottom, 1]) / 2
            self.spe[mask_top, 1] = np.abs(self.spe[mask_top, 1]) / 2



            self.pos += self.spe/10

            self.position_history[:, :, self.steps] = self.pos
            
            if self.parent != None and self.parent.path:
                for i in range(len(self.pos)):
                    self.sonde_history[i][self.steps] = self.pos[i]
            self.steps += 1
            if(comp.sum() == 0 or self.steps > 10000):
                break


        formated_arrivals = []
        formated_history = []
        if self.parent != None:
            self.parent.calculating = False
            textlist.remove(self.parent.traj)
        for i,v in enumerate(self.arrivals):
            if v[0] != -1:
                formated_arrivals.append((self.planet_copy[int(v[0])],v[1],v[0]*2*math.pi/self.n))
                formated_history.append(self.position_history[int(v[0]),:,:])

        return (formated_arrivals, formated_history) # each row is a sonde that reached a planet first, (planet, arrival_time, angle)
                        # ATTENTION: l'historique est en format [ [[x,x,x,x,x,x,x],[y,y,y,y,y,y,y]], [[x,x,x,x,x,x,x],[y,y,y,y,y,y,y]] ...]


class Sonde:
    def __init__(self,planet,angle):
        self.x = planet.x
        self.y = planet.y
        self.prevx = planet.x
        self.prevy = planet.y
        self.angle = angle * math.pi/(p.sonde_number/2)
        self.throwspeed = p.throw_speed
        self.vx = 0
        self.vy = 0
        self.planete = planet
        self.throw = False
        self.distance = 0
        
    def update(self):
        start = time.perf_counter()
        if self.throw == False:
                self.throw = True
                self.vx = self.throwspeed * math.cos(self.angle)
                self.vy = self.throwspeed * math.sin(self.angle)

        for i in objects:
                if(i != self.planete):
                    dist = math.sqrt((i.getAbsoluteX() - self.x)**2 + (i.getAbsoluteY() - self.y)**2)
                    if(dist < 30):
                        self.x = i.getAbsoluteX()
                        self.y = i.getAbsoluteY()
                        self.vx = 0
                        self.vy = 0
                        self.throw = False
                        self.planete = i
                        return (self.angle,self.distance)

                    elif(dist != 0):
                        dx = (i.getAbsoluteX() - self.x)
                        dy = (i.getAbsoluteY() - self.y)
                        angle = math.atan2(dy, dx)
                        a = 20000 * G / (dist**2) 
                        self.vx += math.cos(angle) * a
                        self.vy += math.sin(angle) * a

        if(self.x > MAP_WIDTH):
                self.x = MAP_WIDTH
                self.vx = - abs(self.vx * 0.5)
        if(self.x < 0):
                self.x = 0
                self.vx = abs(self.vx * 0.5)
        if(self.y > MAP_HEIGHT):
                self.y = MAP_HEIGHT
                self.vy = - abs(self.vy * 0.5)
        if(self.y < 0):
                self.y = 0
                self.vy = abs(self.vy * 0.5)

        self.prevx = self.x
        self.prevy = self.y
        self.x += self.vx/10
        self.y += self.vy/10
        self.distance += math.sqrt((self.vx/10)**2 + (self.vy/10)**2)
        end = time.perf_counter() - start


imagelist = []
textlist = []
path_list = []
imageplanete = Image(pygame.image.load("planete.png"),scale=0.1)
imagelune = Image(pygame.image.load("lune.png"))

mytext = Text("Fuel: ", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.9, 50, relative=False, color=(255,255,255))
score = Text("Score: ", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.05, 50, relative=False, color=(255,255,255))

for i in range(PLANET_NUMBER):
    o = Object(random.randint(0, MAP_WIDTH), random.randint(0, MAP_WIDTH), 10)
    o.image = imageplanete
    o.transparent = True
    for j in range(random.randint(0, MOON_NUMBER)):
        c = Object(0, 0, 5)
        c.r = 5
        c.m = random.randint(1, 10)
        c.setParent(o,random.randint(50, 200))
        c.transparent = True
        c.image = imagelune
    objects.append(o)

p = Player(objects[0])

def test(path1,sonde,sonde_history,steps,cursor,output):
    while True:
        path1 = path1.get()
        sonde = sonde.get()
        sonde_history = sonde_history.get()
        steps = steps.get()
        cursor = cursor.get()
        if path1 and sonde is not None and sonde_history != []:
            for i in sonde_history:
                    path = i[:sonde.steps]
                    if len(path) >= 2:
                        coordsx = path[:, 0]
                        coordsy = path[:, 1]    # Transpose to (2, N) shape
                        x = SCREEN_WIDTH//2 + (coordsx - cursor[0]) * p.zoom
                        y = SCREEN_HEIGHT//2 + (coordsy - cursor[1]) * p.zoom
                        points = np.column_stack((x, y)).astype(int)
                        output.put(points)
                        
path,sonde,sonde_history,steps,cursor,output = [multiprocessing.Queue() for i in range(6)]
multiprocessing.Process(target=test, args=(path,sonde,sonde_history,steps,cursor,output)).start()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEWHEEL:
                if p.zoom* ((event.y*0.2) +1) < 6 and p.zoom* ((event.y*0.2) +1) > 0.1:
                    p.zoom *= (event.y)*0.2 + 1

    screen.fill((0, 0, 0))
    Object.time()
    for i in imagelist:
        i.update()

    for i in objects:
        i.updateAll()
        i.drawAll()
        if p.map:
            pygame.draw.circle(screen, (255, 0, 0), (posX(i.x), posY(i.y)), 20 * p.zoom)
            if i == p.selected_planet:
                pygame.draw.circle(screen, (0, 0, 255), (posX(i.x), posY(i.y)), 20 * p.zoom)
    for i in textlist:
        i.update()

    
        
                    
    if p.map:    
        for i in p.accessible_planets:
            if i[0] != p.selected_planet:
                pygame.draw.circle(screen, (0, 255, 0), (posX(i[0].x), posY(i[0].y)), 20 * p.zoom)
    mytext.setText("Fuel: " + str(round(p.fuel,1)))
    score.setText("Score: " + str(p.score))
    p.update()
    p.draw()
    pygame.display.update()
    pygame.time.Clock().tick(60)
