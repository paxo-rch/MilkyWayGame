from entities import *
import graphics
import pygame
import entities

min_bot_ressources = {
    "Chromites": 25,
    "Chromium": 25,
    "Charbonites": 30,
    "Charbonium": 20,
    "Meganites": 15,
    "Meganium": 15,
    "Ultranium": 0,
}

class Bot(Player):
    def __init__(self, planet):
        self.ai_state = 0 # 0=landed, 1=calculating, 2=throwing
        self.planet = planet
        self.spawn_planet = planet
        self.x = planet.getAbsoluteX()
        self.y = planet.getAbsoluteY()
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.speed = 1
        self.turn_speed = 16
        self.throw_speed = 100
        self.fuel_consumption = 0.05
        self.fuel_consumption_throw = 10
        self.projection_length = 100
        self.throw = False
        self.thrust = False
        self.landing_count = 1
        self.distance = 0
        self.hp = 100
        self.imprecision = 0.1
        #Ship level
        self.detector_level = 10
        self.base_detection_range = 1000

        #Ressources
        self.ressources = {i: 0 for i in ressources.types}
        self.ressources["Charbonites"] = 100

        #Path settings
        self.sonde_number = 10

        #Path variables
        self.accessible_planets = []

        self.reloadTime = entities.Object.t

        self.calculating = False
        self.icon_rocket = pygame.image.load("assets/player/rocket.png")
        self.flame_animation = []
        # read the gif file
        for f in range(1, 29):
            self.flame_animation.append(pygame.image.load(f"assets/player/flame_gif/{f}.gif"))

        self.i = 0
    
    def draw(self):
        a_mvt = self.angle

        self.i = (self.i+1) % len(self.flame_animation)

        sprite_size = (int(self.icon_rocket.get_width()*entities.player.zoom*0.05), int(self.icon_rocket.get_height()*entities.player.zoom*0.05))
        sprite_surface = pygame.Surface(sprite_size, pygame.SRCALPHA)
        rocket_scaled = pygame.transform.scale(self.icon_rocket, sprite_size)
        sprite_surface.blit(rocket_scaled, (0, 0))
        
        if(self.thrust):
            flame_scaled = pygame.transform.scale(self.flame_animation[self.i], [sprite_size[0]/5, sprite_size[1]/3])
            sprite_surface.blit(flame_scaled, (sprite_size[0]*0.4, sprite_size[0]*0.7))
            
        rotated_sprite = pygame.transform.rotate(sprite_surface, -90 - math.degrees(a_mvt))
        screen.blit(rotated_sprite, (posX(self.x)-rotated_sprite.get_width()//2, posY(self.y)-rotated_sprite.get_height()//2))

    def update(self):
        if(self.hp <= 0 or self.ressources["Charbonites"] <= 0):
            self.die()
            self.ai_state = 0
        
        if self.throw:
            for i in Object.objects:    # physics
                if(i != self.planet):
                    dist = math.sqrt((i.getAbsoluteX() - self.x)**2 + (i.getAbsoluteY() - self.y)**2)
                    
                    if(dist < 30):
                        self.x = i.getAbsoluteX()
                        self.y = i.getAbsoluteY()
                        self.vx = 0
                        self.vy = 0
                        self.throw = False
                        self.planet = i
                        self.ai_state = 0

                        for j in self.ressources:
                            self.ressources[j] += i.reference.ressources[j]
                            i.reference.ressources[j] = 0

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


        
            self.thrust = False
            self.ressources["Charbonites"] -= self.fuel_consumption / 2

            self.x += self.vx/10
            self.y += self.vy/10
            self.distance += math.sqrt((self.vx/10)**2 + (self.vy/10)**2)

        else:
            
            if(self.ai_state == 0):
                self.ai_state = 1

                self.calculating = True
                sd = Sondes(Object.objects,self.sonde_number,self)
                self.sonde = sd
                threading.Thread(target=sd.run, args=()).start()

            elif(self.ai_state == 1 and self.calculating == False): # If the calculation is done
                self.ai_state = 2
            
                if(len(self.accessible_planets) > 0):

                    min_dist = 999999999
                    closest_planet = None

                    if all(self.ressources[key] >= min_bot_ressources[key] for key in self.ressources):
                        for i in self.accessible_planets:
                            dist = math.sqrt((i[0].getAbsoluteX() - graphics.player.x)**2 + (i[0].getAbsoluteY() - graphics.player.y)**2)
                            if(dist < min_dist):
                                min_dist = dist
                                closest_planet = i
                    
                    else:
                        closest_planet = self.accessible_planets[random.randint(0, len(self.accessible_planets)-1)]
                                

                    if(closest_planet != None):
                        self.angle = closest_planet[1]

                        self.throw = True
                        self.landing_count += 1
                        
                        self.ressources["Charbonites"] -= self.fuel_consumption_throw
                        self.vx = self.throw_speed * math.cos(self.angle)
                        self.vy = self.throw_speed * math.sin(self.angle)
        
        if(self.ai_state == 2 and self.reloadTime < Object.t - 0.15):
            self.angle = math.atan2(graphics.player.y - self.y, graphics.player.x - self.x)
            weapons.Projectile(self.x, self.y, self.angle+random.uniform(-self.imprecision, self.imprecision), 20, 5, graphics.player)
            self.reloadTime = Object.t
