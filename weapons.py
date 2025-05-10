import ressources
import entities
import pygame
import graphics
from math import *
import random # Needed for Mine Layer
import time # Potentially useful for cooldowns, using frame counter for now

#
#   Code for the weapons module:
#   This module contains the classes and functions related to the weapons in the game.
#

types = {
    "Laser": {
        "icon": "assets/weapons/laser.png",
        "ressources": { "Ultranium": 1, }
    },
    "MissileLauncher": {
        "icon": "assets/weapons/missile_launcher.png", # Placeholder path
        "ressources": { "Meganites": 5, "Charbonites": 2 } # Example costs
    },
    "PulseCannon": {
        "icon": "assets/weapons/pulse_cannon.png", # Placeholder path
        "ressources": { "Meganium": 3, "Meganites": 1 } # Example costs
    },
    "SlowField": {
        "icon": "assets/weapons/slow_field.png", # Placeholder path
        "ressources": { "Chromites": 4 } # Example costs
    },
    "MineLayer": {
        "icon": "assets/weapons/mine_layer.png", # Placeholder path
        "ressources": { "Meganites": 3, "Charbonium": 2 } # Example costs (assuming Explosium exists)
    }
}

# --- Base Weapon Class (Unchanged) ---
class Weapon:
    weapons = []

    def __init__(self, planet, target):
        self.name = "Weapon"
        self.planet = planet
        self.target = target # The main player/target the weapon system focuses on
        # Note: Some weapons (like Mines) might interact with targets differently
        #       or might not be directly 'aimed' in the traditional sense.

        # Add the weapon instance to the planet it belongs to (if planets track their weapons)
        if hasattr(planet, 'weapons_list'): # Check if planet has a list to store its weapons
             planet.weapons_list.append(self)

        Weapon.weapons.append(self)

    def __del__(self):
        # Remove from the global list
        if self in Weapon.weapons:
            Weapon.weapons.remove(self)
        # Remove from the planet's list if applicable
        if hasattr(self.planet, 'weapons_list') and self in self.planet.weapons_list:
            self.planet.weapons_list.remove(self)
        # Remove from target's list (if used)
        if hasattr(self.target, 'weapons') and self in self.target.weapons:
             self.target.weapons.remove(self) # Assuming target tracks weapons targeting it


    def drawTick(self):
        # Base draw method - does nothing unless overridden
        pass

    def onLand(self, target):
        # Called when a projectile hits a target (must be implemented by projectile types)
        pass

    def onNearPass(self, target):
        # Called periodically to check proximity/interactions with a target
        pass

    def update(self):
        # Default update calls onNearPass with the main target
        # Specific weapons might override this for more complex logic (e.g., projectile movement)
        self.onNearPass(self.target)

    def updateAll():
        # Use a copy of the list to avoid modification issues during iteration
        for weapon in list(Weapon.weapons):
            weapon.update()

    def drawAll():
        for weapon in Weapon.weapons:
            weapon.drawTick()

# --- Laser Weapon (Mostly Unchanged) ---
class Laser(Weapon):
    def __init__(self, planet, target):
        super().__init__(planet, target)
        self.name = "Laser"
        self.range = 400
        self.state = False
        self.current_target = None
        self.animation_timer = 0
        self.pulse_speed = 0.15
        self.core_color_bright = (255, 255, 255)
        self.core_color_dim = (255, 200, 200)
        self.core_thickness = 3
        self.glow_color = (255, 0, 0)
        self.glow_thickness_max = 12
        self.glow_thickness_min = 6
        self.damage_per_tick = 0.1 # Damage applied per frame when active

    def onNearPass(self, target):
        distance = hypot(target.x - self.planet.x, target.y - self.planet.y)

        if distance < self.range:
            if not self.state:
                self.animation_timer = 0
            self.state = True
            self.current_target = target
            # Apply damage directly here during the check
            # Ensure target has necessary attributes before trying to modify them
            if hasattr(target, 'ressources') and "Charbonites" in target.ressources and self.current_target.throw:
                 target.ressources["Charbonites"] -= self.damage_per_tick # Example: Drains Charbonites
                 if target.ressources["Charbonites"] < 0: target.ressources["Charbonites"] = 0 # Prevent negative resources
            # Alternatively, apply health damage:
            # if hasattr(target, 'health'):
            #    target.health -= self.damage_per_tick

        else:
            if self.state and self.current_target == target:
                self.state = False
                self.current_target = None

    def drawTick(self):
        if self.state and self.current_target:
            self.animation_timer += 1
            start_pos = (graphics.posX(self.planet.x), graphics.posY(self.planet.y))
            end_pos = (graphics.posX(self.current_target.x), graphics.posY(self.current_target.y))
            pulse_factor = (sin(self.animation_timer * self.pulse_speed) + 1) / 2.0
            current_glow_thickness = int(self.glow_thickness_min + (self.glow_thickness_max - self.glow_thickness_min) * pulse_factor)
            current_core_color = (
                int(self.core_color_dim[0] + (self.core_color_bright[0] - self.core_color_dim[0]) * pulse_factor),
                int(self.core_color_dim[1] + (self.core_color_bright[1] - self.core_color_dim[1]) * pulse_factor),
                int(self.core_color_dim[2] + (self.core_color_bright[2] - self.core_color_dim[2]) * pulse_factor)
            )
            pygame.draw.line(entities.screen, self.glow_color, start_pos, end_pos, current_glow_thickness)
            if self.core_thickness == 1:
                pygame.draw.aaline(entities.screen, current_core_color, start_pos, end_pos)
            else:
                pygame.draw.line(entities.screen, current_core_color, start_pos, end_pos, self.core_thickness)


class Missile(Weapon):
    def __init__(self, x, y, target):
        super().__init__(None, target)
        self.target = target
        self.x = x
        self.y = y
        self.speed = 5
        self.damage = 10
        # 'range' in the snippet seems like a very large trigger radius.
        # For a missile, this might be its direct collision radius or explosion radius.
        # Let's assume it's a collision/trigger radius.
        self.trigger_radius = 15 # More typical collision radius
        self.original_range_param = 100 # Storing the original 'range = 100' if it had another meaning

        self.angle = 0  # Current orientation of the missile
        self.is_active = True # To manage if the missile should be updated/drawn

        # Visual properties
        self.length = 15  # pixels
        self.width = 6    # pixels (at the base)
        self.body_color = (180, 180, 200)  # Light metallic grey
        self.outline_color = (100, 100, 120) # Darker outline
        self.flame_color1 = (255, 150, 0)   # Orange
        self.flame_color2 = (255, 255, 50)   # Yellow
        self.flame_length = 10
        self.flame_animation_tick = 0

    def onNearPass(self, target): # Renamed from onNearPass
        if not self.is_active or not self.target:
            return

        # 1. Update angle towards target
        self.angle = atan2(self.target.y - self.y, self.target.x - self.x)

        # 2. Move missile
        self.x += cos(self.angle) * self.speed
        self.y += sin(self.angle) * self.speed

        # 3. Check for collision/damage
        # The original snippet had: distance = hypot(target.x - self.planet.x, target.y - self.planet.y)
        # This is problematic as the missile itself doesn't have 'self.planet'.
        # Assuming it means distance between missile and target:
        distance_to_target = hypot(self.target.x - self.x, self.target.y - self.y)
        
        # Assuming target has a 'radius' attribute for more accurate collision
        target_radius = getattr(self.target, 'radius', 5) # Default to 5 if target has no radius

        # if distance_to_target < self.trigger_radius + target_radius:
        #     if hasattr(self.target, 'ressources') and "Charbonites" in self.target.ressources:
        #         self.target.ressources["Charbonites"] -= self.damage
        #     # print(f"Missile hit target {self.target}!")
        #     self.is_active = False # Destroy missile on impact

        # Animation tick for flame
        self.flame_animation_tick = (self.flame_animation_tick + 1) % 10


    def drawTick(self):
        if not self.is_active:
            return

        screen_x, screen_y = graphics.posX(self.x), graphics.posY(self.y)

        # --- Missile Body (Dart/Triangle Shape) ---
        # Define points relative to (0,0) as if missile points along positive X-axis
        # Then rotate and translate them.
        
        # Nose
        p_nose = (self.length * 0.7, 0)
        # Tail points (forming the base)
        p_tail1 = (-self.length * 0.3, self.width / 2)
        p_tail2 = (-self.length * 0.3, -self.width / 2)

        local_points = [p_nose, p_tail1, p_tail2]
        
        world_points = []
        for x_loc, y_loc in local_points:
            # Rotate
            x_rot = x_loc * cos(self.angle) - y_loc * sin(self.angle)
            y_rot = x_loc * sin(self.angle) + y_loc * cos(self.angle)
            # Translate to screen position
            world_points.append((screen_x + x_rot, screen_y + y_rot))
        
        pygame.draw.polygon(entities.screen, self.body_color, world_points)
        pygame.draw.polygon(entities.screen, self.outline_color, world_points, 1) # 1px outline

        # --- Exhaust Flame ---
        # Position flame at the missile's tail end
        flame_base_offset = -self.length * 0.3 # Behind the rearmost point of the body
        
        # Animate flame length slightly
        current_flame_length = self.flame_length * (0.8 + 0.4 * (self.flame_animation_tick / 10))

        # Flame tip (points away from missile body)
        flame_tip_loc = (flame_base_offset - current_flame_length, 0)
        # Flame base points (same width as missile tail, or slightly less)
        flame_base1_loc = (flame_base_offset, self.width / 2.5)
        flame_base2_loc = (flame_base_offset, -self.width / 2.5)

        flame_local_points = [flame_tip_loc, flame_base1_loc, flame_base2_loc]
        
        flame_world_points = []
        for x_loc, y_loc in flame_local_points:
            x_rot = x_loc * cos(self.angle) - y_loc * sin(self.angle)
            y_rot = x_loc * sin(self.angle) + y_loc * cos(self.angle)
            flame_world_points.append((screen_x + x_rot, screen_y + y_rot))

        # Draw outer flame (larger, orange)
        pygame.draw.polygon(entities.screen, self.flame_color1, flame_world_points)
        
        # Draw inner flame (smaller, yellow, slightly shorter)
        inner_flame_tip_loc = (flame_base_offset - current_flame_length * 0.6, 0)
        inner_flame_base1_loc = (flame_base_offset, self.width / 4)
        inner_flame_base2_loc = (flame_base_offset, -self.width / 4)
        
        inner_flame_local_points = [inner_flame_tip_loc, inner_flame_base1_loc, inner_flame_base2_loc]
        inner_flame_world_points = []
        for x_loc, y_loc in inner_flame_local_points:
            x_rot = x_loc * cos(self.angle) - y_loc * sin(self.angle)
            y_rot = x_loc * sin(self.angle) + y_loc * cos(self.angle)
            inner_flame_world_points.append((screen_x + x_rot, screen_y + y_rot))

        pygame.draw.polygon(entities.screen, self.flame_color2, inner_flame_world_points)


class Projectile(Weapon):
    def __init__(self, x, y, angle, speed, damage):
        super().__init__(None, None)
        self.x = x
        self.y = y
        self.basevx = entities.player.vx
        self.basevy = entities.player.vy
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.timeleft = entities.Object.t + 1

    def onNearPass(self, target):
        self.x += cos(self.angle) * self.speed + self.basevx/10
        self.y += sin(self.angle) * self.speed + self.basevy/10
        if(self.timeleft < entities.Object.t):
            self.is_active = False
            super().__del__()

    def drawTick(self):
        segment_length = 10
        end_x = self.x + cos(self.angle) * segment_length
        end_y = self.y + sin(self.angle) * segment_length

        # Draw the segment as a line
        start_pos = (graphics.posX(self.x), graphics.posY(self.y))
        end_pos = (graphics.posX(end_x), graphics.posY(end_y))
        pygame.draw.line(entities.screen, (255, 255, 255), start_pos, end_pos, 2)  # White line with 2px thickness



class DoubleLaser(Laser):
    def __init__(self, planet, target):
        super().__init__(planet, target)
        self.glow_color = (0, 0, 255)

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

            for i in range(2):
                angle = atan2(self.current_target.y - self.planet.y, self.current_target.x - self.planet.x) + i * pi
                new_x = self.planet.x + cos(angle) * self.range
                new_y = self.planet.y + sin(angle) * self.range
                new_end_pos = (graphics.posX(new_x), graphics.posY(new_y))
                pygame.draw.line(entities.screen, self.glow_color, start_pos, new_end_pos, current_glow_thickness)

                if self.core_thickness == 1:
                    pygame.draw.aaline(entities.screen, current_core_color, start_pos, new_end_pos)
                else:
                    pygame.draw.line(entities.screen, current_core_color, start_pos, new_end_pos, self.core_thickness)


class LaserGun(Weapon):
    def __init__(self, planet, target):
        super().__init__(planet, target)
        self.fire_rate = 10  # shots per second
        self.bullets = []
        self.last_shot_time = 0

    def shoot(self):
        current_time = time.time()
        if current_time - self.last_shot_time >= 1 / self.fire_rate:
            bullet = {
                "start_pos": (self.planet.x, self.planet.y),
                "direction": atan2(self.target.y - self.planet.y, self.target.x - self.planet.x),
                "speed": 300  # Arbitrary speed
            }
            self.bullets.append(bullet)
            self.last_shot_time = current_time

    def update(self):
        self.shoot()
        for bullet in self.bullets:
            bullet["start_pos"] = (
                bullet["start_pos"][0] + cos(bullet["direction"]) * bullet["speed"] * (1 / self.fire_rate),
                bullet["start_pos"][1] + sin(bullet["direction"]) * bullet["speed"] * (1 / self.fire_rate)
            )

    def drawTick(self):
        for bullet in self.bullets:
            start_pos = (graphics.posX(bullet["start_pos"][0]), graphics.posY(bullet["start_pos"][1]))
            end_pos = (
                graphics.posX(bullet["start_pos"][0] + cos(bullet["direction"]) * 10),
                graphics.posY(bullet["start_pos"][1] + sin(bullet["direction"]) * 10)
            )
            pygame.draw.line(entities.screen, (255, 0, 0), start_pos, end_pos, 3)

