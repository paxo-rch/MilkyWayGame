from math import *
from random import *

seed()

class vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def angle(ry, rz, l):
        return vec(l * cos(ry) * cos(rz), l * cos(ry) * sin(rz), l * sin(ry))

    def distance(self, other):
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    
    def normalize(self):
        length = sqrt(self.x**2 + self.y**2 + self.z**2)
        return vec(self.x / length, self.y / length, self.z / length)
    
    def __add__(self, other):
        return vec(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return vec(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, n):
        return vec(self.x * n, self.y * n, self.z * n)

class Universe:
    def __init__(self):
        self.t = 0

        self.mass = 1
        self.children = []
        self.G = 1 # 6.67408e-11
        self.position = vec(0, 0, 0)

    def generateMap(self):
        pass
    
    def updateAll(self):
        for i in self.children:
            i.updateAll()

u = Universe()

class Transaction:
    transactions = []

    def __init__(self, sender, receiver, ressource, time): # ressource is a dictionary
        self.sender = sender
        self.receiver = receiver

        self.sender.ressources -= ressource
        self.ressources = ressource
        self.time = u.t + time # when the transaction should be ended

        Transaction.transactions.append(self)
    
    def update(self):
        if u.t > self.time:
            self.receiver.ressources += self.sender.ressources
            self.ressources = {}
            Transaction.transactions.remove(self)
    
    def hasEnded(self):
        return u.t > self.time

class Object:
    id_counter = 0

    def __init__(self, parent, mass, radius):
        self.parent = parent
        self.parent.children.append(self)
        self.mass = mass
        self.radius = radius

        self.angular_velocity = 0
        self.first_angular_position = 0
        self.angular_position = 0
        self.orbit_radius = 0
        self.orbit_angle = [(random()-0.5) * 2 * pi / 360 * 10, (random()-0.5) * 2 * pi / 360 * 10]
        self.position = vec(0, 0, 0)

        self.children = []

        self.visible = False
        self.visible_ressources = False
    
        self.id = Object.id_counter
        Object.id_counter+=1

    def genetateOrbit(self, radius, y_deviation=10, z_deviation=10):
        self.orbit_radius = radius
        self.first_angular_position = random()*2*pi
        self.angular_velocity = sqrt(u.G * self.parent.mass / self.orbit_radius) * 2 * pi

    def updatePosition(self):
        self.angular_position = self.first_angular_position + self.angular_velocity * u.t
        
        x = self.orbit_radius * cos(self.orbit_angle[1]) * cos(self.angular_position) + self.orbit_radius * sin(self.orbit_angle[1]) * sin(self.orbit_angle[0]) * sin(self.angular_position)
        y = self.orbit_radius * sin(self.orbit_angle[1]) * cos(self.angular_position) - self.orbit_radius * cos(self.orbit_angle[1]) * sin(self.orbit_angle[0]) * sin(self.angular_position)
        z = self.orbit_radius * cos(self.orbit_angle[0]) * sin(self.angular_position)
        self.position = vec(x, y, z)

    def getAbsolutePosition(self):
        if(self.parent and not isinstance(self.parent, Universe)):
            return self.parent.getAbsolutePosition() + self.position
        else:
            return self.position

    def updateMass(self):
        for i in self.children:
            i.updateMass()
            self.mass += i.mass
    
    def updateAll(self):
        self.updatePosition()
        for i in self.children:
            i.updateAll()

class System (Object):
    # Can contain stars, planets, astroids

    def __init__(self):
        super().__init__()

        self.stars = []
        self.planets = []
        self.astroids = []

    def ressources(self):
        return sum([i.ressources for i in self.children])

class Star (Object):
    def __init__(self, parent, mass, radius):
        super().__init__(parent, mass, radius)

        self.ressources = {
            'energy_rate': 1000, # Joules
            'helium': 1000, # kg
            'hydrogen': 1000 # Kg
        }

class Planet (Object):
    def __init__(self, parent, mass, radius):
        super().__init__(parent, mass, radius)

        self.ressources = {
            'energy_rate': 1000, # Joules
            'helium': 1000, # kg
            'hydrogen': 1000 # Kg
        }
        
