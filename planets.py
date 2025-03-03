from math import *

import ressources

class Planet:
    types = [
        "Kansan",
        "Water"
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


Planet.ressources["Kansan"] = {
    "ressources": {
        "Coal": 1,
        "Silicium": 1,
        "Lava": 20,
        "Water": 0
    },
    "icon": "assets/planets/planet1.png"
}

Planet.ressources["Water"] = {
    "ressources": {
        "Coal": 1,
        "Silicium": 5,
        "Lava": 0,
        "Water": 20,
    },
    "icon": "assets/planets/planet2.png"
}

Planet.ressources["Stone"] = {
    "ressources": {
        "Coal": 10,
        "Silicium": 5,
        "Lava": 0,
        "Water": 0,
    },
    "icon": "assets/planets/planet3.png"
}
