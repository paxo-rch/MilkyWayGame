from math import *
import planets
import random

types = [
    "Chromites",
    "Chromium",
    "Charbonites",
    "Charbonium",
    "Meganites",
    "Meganium",
    "Ultranium"
]

icons = {
    "Chromites": "assets/ressources/Chromites.png",
    "Chromium": "assets/ressources/Chromium.png",
    "Charbonites": "assets/ressources/Charbonites.png",
    "Charbonium": "assets/ressources/Charbonium.png",
    "Meganites": "assets/ressources/Meganites.png",
    "Meganium": "assets/ressources/Meganium.png",
    "Ultranium": "assets/ressources/Ultranium.png",
}

def generate_ressources(planet_type):
    if(planet_type == "earth"):
        ressources = {
            "Chromites": 10,
            "Chromium": 10,
            "Charbonites": 60,
            "Charbonium": 20,
            "Meganites": 5,
            "Meganium": 5,
            "Ultranium": 0,
        }
    elif(planet_type == "norturn"):
        ressources = {
            "Chromites": 5,
            "Chromium": 5,
            "Charbonites": 20,
            "Charbonium": 0,
            "Meganites": 10,
            "Meganium": 10,
            "Ultranium": 1,
        }
    elif(planet_type == "jadea"):
        ressources = {
            "Chromites": 0,
            "Chromium": 0,
            "Charbonites": 0,
            "Charbonium": 0,
            "Meganites": 0,
            "Meganium": 0,
            "Ultranium": 10,
        }
    elif(planet_type == "nimboria"):
        ressources = {
            "Chromites": 10,
            "Chromium": 5,
            "Charbonites": 15,
            "Charbonium": 5,
            "Meganites": 20,
            "Meganium": 20,
            "Ultranium": 0,
        }
    elif(planet_type == "annelius"):
        ressources = {
            "Chromites": 10,
            "Chromium": 5,
            "Charbonites": 50,
            "Charbonium": 20,
            "Meganites": 5,
            "Meganium": 5,
            "Ultranium": 2,
        }
    elif(planet_type == "dorion"):
        ressources = {
            "Chromites": 5,
            "Chromium": 10,
            "Charbonites": 20,
            "Charbonium": 1,
            "Meganites": 10,
            "Meganium": 10,
            "Ultranium": 5,
        }
    elif(planet_type == "sucrelune"):
        ressources = {
            "Chromites": 0,
            "Chromium": 0,
            "Charbonites": -5,
            "Charbonium": -5,
            "Meganites": 0,
            "Meganium": 0,
            "Ultranium": 30,
        }

    for ressource in ressources:
        x = random.random() * 10
        ressources[ressource] *= 1 + 1 / ((x - 10.5)**2) - 1 / ((x + 0.5)**2)
        
        if(ressources[ressource] < 0):
            ressources[ressource] = 0

    return ressources