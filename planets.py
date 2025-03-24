from math import *

import ressources

class Planet:
    types = [
        "earth": 1,
        "norturn": 2,
        "jadea": 3,
        "nimboria": 4,
        "annelius": 5,
        "dorion": 6,
        "sucrelune": 7,
    ]

    ressources = {}

    def __init__(self, x, y, type, object, ressource_multiplier = 1):
        self.x = x
        self.y = y

        self.type = type
        self.object_g = object

        self.ressources = Planet.ressources[type]["ressources"]
        for ressource in self.ressources:
            self.ressources[ressource] *= ressource_multiplier

        self.icon = Planet.ressources[type]["icon"]