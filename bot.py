from entities import *
import graphics
import pygame

class Bot(Player):
    def __init__(self, object):
        self.ai_state = 0 # 0=landed, 1=calculating, 2=throwing
        super().__init__(object)
    
    def update(self):
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
            # Here must be the code to make the AI make a decision
            
            if(self.ai_state == 0):
                self.ai_state = 1

                self.calculating = True
                sd = Sondes(Object.objects,10,self)
                self.sonde = sd
                threading.Thread(target=sd.run, args=()).start()

            elif(self.ai_state == 1 and self.calculating == False): # If the calculation is done
                self.ai_state = 2
            
                if(len(self.accessible_planets) > 0):
                    min_dist = 999999999
                    closest_planet = None
                    for i in self.accessible_planets:
                        dist = math.sqrt((i[0].getAbsoluteX() - graphics.player.x)**2 + (i[0].getAbsoluteY() - graphics.player.y)**2)
                        if(dist < min_dist):
                            min_dist = dist
                            closest_planet = i

                    if(closest_planet != None):
                        self.angle = closest_planet[1]

                        self.throw = True
                        self.landing_count += 1 
                        self.ressources["Charbonites"] -= self.fuel_consumption_throw
                        self.vx = self.throw_speed * math.cos(self.angle)
                        self.vy = self.throw_speed * math.sin(self.angle)
            pass