import ressources
import entities

#
#   Code for the weapons module:
#   This module contains the classes and functions related to the weapons in the game.
#

class Weapon:
    weapons = []

    def __init__(self):
        self.name = "Weapon"

        Weapon.weapons.append(self)
    
    def __del__(self):
        if self in Weapon.weapons:
            Weapon.weapons.remove(self)


    def drawTick(self):
        pass
    
    def onLand(self, target):
        pass

    def onNearPass(self, target: entities.Player):
        pass

    def update(self):
        pass

    def updateAll():
        for i in Weapon.weapons:
            i.update()


class Laser(Weapon):
    pass