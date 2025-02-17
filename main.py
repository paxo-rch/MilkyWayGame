import pygame
import math
import random
import time

G = 1

MAP_SCALE = 10
MAP_WIDTH = 1080 * MAP_SCALE
MAP_HEIGHT = 1080 * MAP_SCALE
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
objects = []

def posX(x):
    return SCREEN_WIDTH//2 + (x - p.cursor[0]) * p.zoom

def posY(y):
    return SCREEN_HEIGHT//2 + (y - p.cursor[1]) * p.zoom

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
        self.image = None
        self.image_scale = 0.05
        self.transparent = False
        self.parent = None
        self.children = []
    def setImage(self, image):
        if isinstance(image, str):
            self.image = pygame.image.load(image)
        else:
            self.image = image
        
    def setParent(self, parent, orbit_radius):
        self.parent = parent
        self.parent.children.append(self)

        self.orbit_radius = orbit_radius
        self.angular_velocity = 1 # math.sqrt(G * 1 / self.orbit_radius) * 2 * math.pi
        self.first_angular_position = random.random() * 2 * math.pi
    
    def draw(self):
        x,y = posX(self.x), posY(self.y)
        if self.image is not None:
            screen.blit(pygame.transform.scale(self.image,(self.image.get_width()*p.zoom*self.image_scale,self.image.get_width()*p.zoom*self.image_scale)),(x-(self.image.get_height()/2)*p.zoom*self.image_scale,y-(self.image.get_width()/2)*p.zoom*self.image_scale))
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
        self.force = 100
        self.projection_length = 100
        self.throw = False

        self.oldMouseState = False
        self.oldMousePosition = [0,0]

        self.cursor = [MAP_WIDTH/2, MAP_HEIGHT/2]
        self.zoom = 1
    
    def draw(self):
        pygame.draw.circle(screen, (255, 0, 0), (posX(self.x), posY(self.y)), 10 * p.zoom)

        pygame.draw.line(screen, (255, 255, 255), (posX(self.x), posY(self.y)), (posX(self.x + math.cos(self.angle) * self.projection_length), posY(self.y + math.sin(self.angle) * self.projection_length)))

    def update(self):
        keys = pygame.key.get_pressed()
        if(not self.throw):
            if keys[pygame.K_RIGHT]:
                self.angle += 4 * math.pi / 360
            if keys[pygame.K_LEFT]:
                self.angle -= 4 * math.pi / 360
        else:
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

            if keys[pygame.K_RIGHT]:
                self.vx += 0.2 * 10
            if keys[pygame.K_LEFT]:
                self.vx -= 0.2 * 10
            if keys[pygame.K_UP]:
                self.vy -= 0.2 * 10
            if keys[pygame.K_DOWN]:
                self.vy += 0.2 * 10
            

            self.x += self.vx/10
            self.y += self.vy/10

        if(not self.throw):
            if keys[pygame.K_SPACE]:
                self.throw = True
                self.vx = self.force * math.cos(self.angle)
                self.vy = self.force * math.sin(self.angle)
        
        mouseState = pygame.mouse.get_pressed()[0]

        # wheel for zoom
        print(self.zoom)


        if(mouseState and not self.oldMouseState):
            self.oldMousePosition = pygame.mouse.get_pos()
        
        if(pygame.mouse.get_pressed()[2] or self.throw):
            self.cursor = [self.x, self.y]
            print(self.cursor)
        
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

imageplanete = pygame.image.load("planete1.png")
imageetoile = pygame.image.load("etoile.jpg")
for i in range(500):
    o = Object(random.randint(0, MAP_WIDTH), random.randint(0, MAP_WIDTH), 10)
    #o.setImage("etoile.jpg")
    for j in range(3):
        c = Object(0, 0, 5)
        c.r = 5
        c.m = random.randint(1, 10)
        c.setParent(o,random.randint(50, 200))
        c.setImage(imageplanete)
        c.transparent = True
    
    objects.append(o)

p = Player(objects[0])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEWHEEL:
            p.zoom *= (event.y)*0.2 + 1

    screen.fill((0, 0, 0))

    Object.time()
    for i in objects:
        i.updateAll()
        i.drawAll()

    p.update()
    p.draw()

    pygame.display.update()
    pygame.time.Clock().tick(60)