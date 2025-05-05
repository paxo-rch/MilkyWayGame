import ressources
import entities
import pygame
import graphics
from math import *

#
#   Code for the weapons module:
#   This module contains the classes and functions related to the weapons in the game.
#

class Weapon:
    weapons = []

    def __init__(self, planet, target):
        self.name = "Weapon"
        self.planet = planet
        self.target = target

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
        self.onNearPass(self.target)

    def updateAll():
        for i in Weapon.weapons:
            i.update()

    def drawAll():
        for i in Weapon.weapons:
            i.drawTick()

class Laser(Weapon):
    def __init__(self, planet, target):
        super().__init__(planet, target) # Pass target to base if needed

        self.range = 400
        # self.angle = 0 # Angle is calculated dynamically in drawTick now if needed
        self.state = False # Is the laser currently firing?
        self.current_target = None # Store the target currently being fired upon

        # --- Animation Properties ---
        self.animation_timer = 0  # Timer for pulsating effect
        self.pulse_speed = 0.15   # How fast the laser pulsates (adjust as needed)

        # --- Visual Configuration ---
        self.core_color_bright = (255, 255, 255) # Bright white core
        self.core_color_dim = (255, 200, 200)     # Dimmer reddish-white core
        self.core_thickness = 3                   # Thickness of the central beam

        self.glow_color = (255, 0, 0)             # Red outer glow
        self.glow_thickness_max = 12              # Maximum thickness of the glow
        self.glow_thickness_min = 6               # Minimum thickness of the glow
        # --- End Visual Configuration ---

    def onNearPass(self, target):
        """Checks if the target is in range and updates the laser state."""
        distance = hypot(target.x - self.planet.x, target.y - self.planet.y)

        if distance < self.range:
            # If the laser wasn't active, reset the animation timer for a fresh pulse
            if not self.state:
                self.animation_timer = 0
            self.state = True
            self.current_target = target # Keep track of the specific target in range
        else:
            # If this specific target caused the laser to be on, turn it off
            if self.state and self.current_target == target:
                self.state = False
                self.current_target = None

    def drawTick(self):
        """Draws the laser if it's active, with animation and AA effects."""
        if self.state and self.current_target:
            self.animation_timer += 1

            # Calculate start and end points using graphics conversions
            start_pos = (graphics.posX(self.planet.x), graphics.posY(self.planet.y))
            end_pos = (graphics.posX(self.current_target.x), graphics.posY(self.current_target.y))

            # --- Pulsation Calculation ---
            pulse_factor = (sin(self.animation_timer * self.pulse_speed) + 1) / 2.0

            current_glow_thickness = int(self.glow_thickness_min + (self.glow_thickness_max - self.glow_thickness_min) * pulse_factor)

            current_core_color = (
            int(self.core_color_dim[0] + (self.core_color_bright[0] - self.core_color_dim[0]) * pulse_factor),
            int(self.core_color_dim[1] + (self.core_color_bright[1] - self.core_color_dim[1]) * pulse_factor),
            int(self.core_color_dim[2] + (self.core_color_bright[2] - self.core_color_dim[2]) * pulse_factor)
            )

            # Draw the outer glow normally (width > 1, so AA not directly applicable)
            pygame.draw.line(entities.screen, self.glow_color, start_pos, end_pos, current_glow_thickness)

            # Draw the core with AA when possible. If core_thickness == 1, use aaline for antialiasing.
            if self.core_thickness == 1:
                pygame.draw.aaline(entities.screen, current_core_color, start_pos, end_pos)
            else:
                pygame.draw.line(entities.screen, current_core_color, start_pos, end_pos, self.core_thickness)