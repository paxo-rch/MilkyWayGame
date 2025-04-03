from math import *
import pygame

import ressources
import graphics

class Planet:
    types = {
        "earth": 1,
        "norturn": 2,
        "jadea": 3,
        "nimboria": 4,
        "annelius": 5,
        "dorion": 6,
        "sucrelune": 7,
    }

    icons = {
        "earth": "assets/planets/planet1.png",
        "norturn": "assets/planets/planet2.png",
        "jadea": "assets/planets/planet3.png",
        "nimboria": "assets/planets/planet4.png",
        "annelius": "assets/planets/planet5.png",
        "dorion": "assets/planets/planet6.jpeg",
        "sucrelune": "assets/planets/planet7.png",
    }

    imgs =  {}

    def load_planets():
        Planet.imgs = {key: graphics.Image(
            pygame.transform.scale(pygame.image.load(Planet.icons[key]), (500, 500))
            ,scale=0.1) 
            for key in Planet.types.keys()}

    def update_images():
        for key in Planet.imgs.keys():
            Planet.imgs[key].update()

    def __init__(self, x, y, type, object, ressources):
        self.x = x
        self.y = y

        self.type = type    # name
        self.object_g = object

        self.ressources = ressources

        self.icon = Planet.imgs[type]