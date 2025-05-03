import numpy as np
import math
import random
import time
import threading
import multiprocessing

from graphics import *
import gui

import ressources

class Object:
    t = 0
    G = 1
    objects = []

    def time():
        Object.t = time.time()*1

    def __init__(self, x, y, m):
        self.x = x
        self.y = y
        self.m = m
        self.r = m
        self.transparent = False
        self.parent = None
        self.children = []
        self.reference = None
        self.rotation = random.random() * 2 * math.pi


    def setParent(self, parent, orbit_radius):
        self.parent = parent
        self.parent.children.append(self)

        self.orbit_radius = orbit_radius
        self.angular_velocity = math.sqrt(Object.G * 1 / self.orbit_radius) * 2 * math.pi
        self.first_angular_position = random.random() * 2 * math.pi


    def draw(self):
        x,y = posX(self.x), posY(self.y)

        if(x + self.r * player.zoom < 0 or x - self.r * player.zoom > MAP_WIDTH or y + self.r * player.zoom < 0 or y - self.r * player.zoom > MAP_HEIGHT):
            return

        if self.parent is not None:
            if self.image.scaled_image is not None:
                rotated_image = pygame.transform.rotate(self.image.scaled_image, math.degrees(self.rotation))
                screen.blit(rotated_image, (x-rotated_image.get_width()/2, y-rotated_image.get_height()/2))
        
        elif self.reference is not None:
            self.reference.icon
            rotated_image = pygame.transform.rotate(self.reference.icon.scaled_image, math.degrees(self.rotation))
            screen.blit(rotated_image,
                        (x-rotated_image.get_width()/2,
                         y-rotated_image.get_height()/2))

        if not self.transparent:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), self.r * player.zoom)


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

        #Ressources
        self.ressources = {i: 0 for i in ressources.types}
        
        #Path settings
        self.sonde_number = 360
        self.path = True
        self.path_step = 1
        self.clean_path = True

        #Path variables
        self.show_accessible_planets = True
        self.sonde = None
        self.accessible_planets = []
        self.selected_planet = None

        self.map = False
        self.score = 0
        self.calculating = False
        self.icon_rocket = pygame.image.load("assets/player/rocket.png")
        self.flame_animation = []
        self.i = 0

        self.debug = False
        # read the gif file
        for f in range(1, 29):
            self.flame_animation.append(pygame.image.load(f"assets/player/flame_gif/{f}.gif"))

        self.oldMouseState = False
        self.oldMousePosition = [0,0]

        self.cursor = [MAP_WIDTH/2, MAP_HEIGHT/2]
        self.zoom = 1


    def draw(self):
        #pygame.draw.circle(screen, (255, 0, 0), (posX(self.x), posY(self.y)), 10 * p.zoom)

        a_mvt = self.angle


        self.i = (self.i+1) % len(self.flame_animation)

        sprite_size = (int(self.icon_rocket.get_width()*player.zoom*0.05), int(self.icon_rocket.get_height()*player.zoom*0.05))
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
        clock = pygame.time.Clock()

        while True:
            start = time.perf_counter()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                    self.angle += self.turn_speed * math.pi / 360

            elif keys[pygame.K_LEFT]:
                    self.angle -= self.turn_speed * math.pi / 360

            if self.throw:

                for i in Object.objects:
                    
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

                            a = 20000 * Object.G / (dist**2)   # from F=ma and G=m1m2/r^2 as self.m = 1kg


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


            if(not self.throw):

                if (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]) and self.fuel > self.fuel_consumption_throw and self.calculating == False:
                    self.throw = True
                    self.landing_count += 1 
                    self.fuel -= self.fuel_consumption_throw
                    self.vx = self.throw_speed * math.cos(self.angle)
                    self.vy = self.throw_speed * math.sin(self.angle)


                elif keys[pygame.K_s] and self.calculating == False:
                    self.calculating = True
                    self.traj = Text("Calcul de trajectoire en cours...", SCREEN_HEIGHT/2, SCREEN_WIDTH/2, 100,relative=False, color=(255,255,255))
                    sd = Search(self.planet,self.selected_planet,self.throw_speed)
                    player.sonde = sd
                    threading.Thread(target=sd.run, args=()).start()

                elif keys[pygame.K_c] and self.calculating == False:
                    self.accessible_planets = []
                    self.sonde = None

                elif keys[pygame.K_m] and self.calculating == False:
                    self.map = not self.map
                    time.sleep(0.1)

                elif keys[pygame.K_d]:
                    self.debug = not self.debug
                    time.sleep(0.1)
            
                mouseState = pygame.mouse.get_pressed()[0]

                # wheel for zoom


                if(mouseState and not self.oldMouseState):
                    self.oldMousePosition = pygame.mouse.get_pos()
                
                
                if mouseState and not self.throw and not self.calculating and self.map:
                    
                    click_pos_screen = self.oldMousePosition 

                    for i in Object.objects:
                        planet_screen_x, planet_screen_y = posX(i.x), posY(i.y)
                        click_dist_sq = (click_pos_screen[0] - planet_screen_x)**2 + (click_pos_screen[1] - planet_screen_y)**2
                        
                        click_radius = max(20, i.r * self.zoom * 1.5) 

                        if i != self.planet and click_dist_sq < click_radius**2:
                            self.selected_planet = i

                            for accessible_planet, launch_angle in self.accessible_planets: 
                                if accessible_planet == i:
                                    self.angle = launch_angle
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
            clock.tick(60)
            end = time.perf_counter() - start
            if player.debug:
                gui.update_fps.setText("PUS: " + str(round(1/end)))
            else:
                gui.update_fps.setText("")
            

class Search:
    def __init__(self,start,target,throw_speed):
        self.target = target
        self.start = start
        self.throw_speed = throw_speed
    def sonde(self,angle):
        throw = False
        x,y = self.start.getAbsoluteX(), self.start.getAbsoluteY()
        start = time.perf_counter()
        while True:
            if throw:
                for i in Object.objects:
                    
                    if(i != self.start):
                        dist = math.sqrt((i.getAbsoluteX() - x)**2 + (i.getAbsoluteY() - y)**2)
                        
                        if(dist < 30):
                            x = i.getAbsoluteX()
                            y = i.getAbsoluteY()
                            vx = 0
                            vy = 0
                            throw = False
                            planet = i
                            print(time.perf_counter()-start)
                            return planet

                        elif(dist != 0):
                            dx = (i.getAbsoluteX() - x)
                            dy = (i.getAbsoluteY() - y)

                            angle = math.atan2(dy, dx)

                            a = 20000 * Object.G / (dist**2)   # from F=ma and G=m1m2/r^2 as self.m = 1kg


                            vx += math.cos(angle) * a
                            vy += math.sin(angle) * a

                if(x > MAP_WIDTH):
                    x = MAP_WIDTH
                    vx = - abs(vx * 0.5)

                if(x < 0):
                    x = 0
                    vx = abs(vx * 0.5)

                if(y > MAP_HEIGHT):
                    y = MAP_HEIGHT
                    vy = - abs(vy * 0.5)
                    
                if(y < 0):
                    y = 0
                    vy = abs(vy * 0.5)

                x += vx/10
                y += vy/10


            else:
                    throw = True
                    vx = self.throw_speed * math.cos(angle)
                    vy = self.throw_speed * math.sin(angle)
    def run(self):
        for i in range(360):
            print(self.sonde(i))