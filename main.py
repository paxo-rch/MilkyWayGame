import pygame
import math
import random
import time
import imageio

G = 1

MAP_SCALE = 10
MAP_WIDTH = 1080 * MAP_SCALE
MAP_HEIGHT = 1080 * MAP_SCALE
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

PLANET_NUMBER = 500
MOON_NUMBER = 5

ROCKET_SPEED = 1
ROCKET_TURN_SPEED = 16
ROCKET_THROW_SPEED = 100
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
objects = []

def posX(x):
    return SCREEN_WIDTH//2 + (x - p.cursor[0]) * p.zoom

def posY(y):
    return SCREEN_HEIGHT//2 + (y - p.cursor[1]) * p.zoom

class Image:
    def __init__(self):
        self.scale = 0.05
        self.image = None
        self.scaled_image = None

    def setImage(self, image):
        if isinstance(image, str):
            self.image = pygame.image.load(image)
            
        else:
            self.image = image


    def update(self):
        if self.image is not None:
            self.scaled_image = pygame.transform.scale(self.image,(self.image.get_width()*p.zoom*self.scale,self.image.get_height()*p.zoom*self.scale))


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
        if self.parent is None:
            return self.x
        else:
            return self.parent.getAbsoluteX() + self.x
        
    def getAbsoluteY(self):
        if self.parent is None:
            return self.y
        else:
            return self.parent.getAbsoluteY() + self.y

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
        self.force = ROCKET_THROW_SPEED
        self.projection_length = 100
        self.throw = False
        self.thrust = False

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
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
                self.angle += ROCKET_TURN_SPEED * math.pi / 360
        elif keys[pygame.K_LEFT]:
                self.angle -= ROCKET_TURN_SPEED * math.pi / 360
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

                    if(dist != 0):
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

            if keys[pygame.K_SPACE]:
                self.thrust = True
                self.vx += math.cos(self.angle) * ROCKET_SPEED
                self.vy += math.sin(self.angle) * ROCKET_SPEED
            else:
                self.thrust = False

            self.x += self.vx/10
            self.y += self.vy/10

        if(not self.throw):
            if keys[pygame.K_SPACE]:
                self.throw = True
                self.vx = self.force * math.cos(self.angle)
                self.vy = self.force * math.sin(self.angle)
        
        mouseState = pygame.mouse.get_pressed()[0]

        # wheel for zoom


        if(mouseState and not self.oldMouseState):
            self.oldMousePosition = pygame.mouse.get_pos()
        
        if(pygame.mouse.get_pressed()[2] or self.throw):
            self.cursor = [self.x, self.y]
        
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


images = []
imageplanete = Image()
imagelune = Image()
imagelune.setImage(pygame.image.load("lune.png"))
imageplanete.setImage(pygame.image.load("planete.png"))
imageplanete.scale = 0.1
images.append(imagelune)
images.append(imageplanete)

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
    for i in images:
        i.update()
    for i in objects:
        i.updateAll()
        i.drawAll()
    
    p.update()
    p.draw()

    pygame.display.update()
    pygame.time.Clock().tick(60)