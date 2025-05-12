import numpy as np
import math
import random
import time
import threading

from graphics import *
import gui
import ressources
import weapons

bot_players = []

class Object:
    t = 0 # Global time variable, updated externally
    G = 1 # Gravitational constant
    objects = [] # List to hold all game objects

    def time():
        Object.t = time.time()*1 # Updates the global time

    def __init__(self, x, y, m):
        self.x = x
        self.y = y
        self.m = m # Mass
        self.r = m # Radius (often tied to mass for visual representation)
        self.transparent = False # For drawing
        self.parent = None # Parent object in a hierarchical structure (e.g., planet orbiting sun)
        self.children = [] # Children objects
        self.reference = None # A linked object, possibly for data/type reference (e.g., a planet object referencing a PlanetType)
        self.weapons = [] # List of weapon instances on this object (if applicable)
        self.weapons_name = [] # List of weapon names on this object
        self.rotation = random.random() * 2 * math.pi # Initial random rotation

    def setParent(self, parent, orbit_radius):
        self.parent = parent
        self.parent.children.append(self)

        self.orbit_radius = orbit_radius
        # Calculate angular velocity for a circular orbit (simplified, assumes parent mass is 1 or absorbed into G)
        self.angular_velocity = math.sqrt(Object.G * 1 / self.orbit_radius) * 2 * math.pi
        self.first_angular_position = random.random() * 2 * math.pi # Initial random position in orbit

    def draw(self):
        # Get screen coordinates from world coordinates (using external functions)
        x,y = posX(self.x), posY(self.y)

        # Check if the object is outside the screen bounds
        if(x + self.r * player.zoom < 0 or x - self.r * player.zoom > MAP_WIDTH or y + self.r * player.zoom < 0 or y - self.r * player.zoom > MAP_HEIGHT):
            return # Don't draw if off-screen

        if self.parent is not None:
            if self.image.scaled_image is not None:
                # Rotate the scaled image based on the object's rotation
                rotated_image = pygame.transform.rotate(self.image.scaled_image, math.degrees(self.rotation))
                # Draw the rotated image centered on the object's screen position
                screen.blit(rotated_image, (x-rotated_image.get_width()/2, y-rotated_image.get_height()/2))

        elif self.reference is not None:
            # If no parent but a reference exists, use the reference's icon
            self.reference.icon
            rotated_image = pygame.transform.rotate(self.reference.icon.scaled_image, math.degrees(self.rotation))
            screen.blit(rotated_image,
                        (x-rotated_image.get_width()/2,
                         y-rotated_image.get_height()/2))

        if not self.transparent:
            # Draw a white circle representing the object if not transparent
            pygame.draw.circle(screen, (255, 255, 255), (x, y), self.r * player.zoom)

    def drawAll(self):
        self.draw() # Draw this object

        for i in self.children:
            i.drawAll() # Recursively draw children

    def getAbsoluteX(self):
        return self.x # Returns world X coordinate

    def getAbsoluteY(self):
        return self.y # Returns world Y coordinate

    def updateAll(self):
        self.update() # Update this object

        for i in self.children:
            i.updateAll() # Recursively update children

    def update(self):
        # Update position based on orbital parameters if it has a parent
        if(self.parent is not None):
            # Calculate position using polar coordinates relative to the parent
            self.x = self.parent.getAbsoluteX() + self.orbit_radius * math.cos(self.first_angular_position + self.angular_velocity * Object.t)
            self.y = self.parent.getAbsoluteY() + self.orbit_radius * math.sin(self.first_angular_position + self.angular_velocity * Object.t)


class Player:
    def __init__(self, planet):
        self.planet = planet # The planet the player is currently landed on
        self.spawn_planet = planet # The planet the player respawns on
        self.x = planet.getAbsoluteX() # Initial X position
        self.y = planet.getAbsoluteY() # Initial Y position
        self.vx = 0 # Velocity X
        self.vy = 0 # Velocity Y
        self.angle = 0 # Orientation angle (radians)
        self.speed = 2 # Thrust acceleration magnitude
        self.turn_speed = 16 # Turning speed (degrees per game tick)
        self.throw_speed = 100 # Initial velocity when launching from a planet
        self.fuel_consumption = 0.05 # Fuel consumed per tick when thrusting
        self.fuel_consumption_throw = 10 # Fuel consumed when launching
        self.projection_length = 100 # Length of the launch projection line
        self.throw = False # State: True if in flight, False if landed
        self.thrust = False # State: True if thrusting
        self.landing_count = 1 # Number of successful landings
        self.distance = 0 # Total distance traveled
        self.menu = True
        self.kills = 0 # Player kills
        self.death = 1 # Player deaths

        self.weapons = [] # Player's personal weapons (not implemented in this snippet)
        self.hull_hp = 100 # Hull hit points
        self.shield_hp = 100 # Shield hit points

        #Ship level
        self.detector_level = 10 # Level of the planet detector
        self.base_detection_range = 1000 # Base range for detecting planet info

        #Ressources
        self.ressources = {i: 0 for i in ressources.types} # Dictionary to hold resources
        self.ressources["Charbonites"] = 100 # Starting fuel

        #Inventory
        self.inventory_opened = False # State: True if inventory GUI is open
        self.inventory_items = [] # List to hold inventory GUI elements
        self.inventory_box = None # Main inventory GUI box
        self.box_ressource = None # Resource display box
        self.box_planet_defense = None # Planet defense purchase box
        self.inventory_text = None # Inventory title text

        #Path settings
        self.sonde_number = 360 # Number of probes used for trajectory calculation
        self.rcs = False # State: True if Reaction Control System (auto-orientation) is active

        #Path variables
        self.sonde = None # Holds the Sondes object during calculation
        self.accessible_planets = [] # List of reachable planets and their launch angles
        self.accessible_planets_object = [] # List of reachable planet objects
        self.selected_planet = None # The planet currently selected on the map

        self.map = False # State: True if map GUI is open
        self.map_objects = [] # List to hold map GUI elements (boxes around planets)
        self.text_obj = [] # List to hold map info text elements
        self.score = 0 # Player score (based on distance)
        self.calculating = False # State: True if trajectory calculation is in progress

        self.icon_rocket = pygame.image.load("assets/player/rocket.png") # Rocket sprite image
        self.flame_animation = [] # List to hold flame animation frames
        self.i = 0 # Current frame index for flame animation

        self.time_on_planet = 0 # Time spent landed on the current planet

        self.debug = False # Debug mode toggle

        # read the gif file
        for f in range(1, 29):
            self.flame_animation.append(pygame.image.load(f"assets/player/flame_gif/{f}.gif"))

        self.oldMouseState = False # Previous mouse button state for click detection
        self.oldMousePosition = [0,0] # Previous mouse position for panning

        self.cursor = [MAP_WIDTH/2, MAP_HEIGHT/2] # World coordinates of the camera center
        self.zoom = 1 # Camera zoom level
        self.btn_delay = 0.5 # Minimum time between button presses

        self.reloadTime = Object.t # Time when the weapon was last fired
        

    def die(self):
        # Reset player state upon death
        self.hull_hp = 100
        self.shield_hp = 100
        self.x = self.spawn_planet.getAbsoluteX() # Return to spawn planet
        self.y = self.spawn_planet.getAbsoluteY()
        self.vx = 0
        self.vy = 0
        self.score = 0
        self.distance = 0
        self.landing_count = 1
        self.ressources["Charbonites"] = 100 # Refuel
        self.throw = False # Ensure player is landed
        self.thrust = False
        self.death += 1 # Increment death count

    def applyDamage(self, damage):
        # Apply damage, prioritizing shields
        if self.shield_hp > 0 and (self.shield_hp - damage*0.5 <= 0):
            # If shield breaks, remaining damage goes to hull
            hull_damage = damage*0.5 - self.shield_hp
            self.shield_hp = 0
            self.hull_hp -= hull_damage
            # Visual feedback for shield breaking (optional, not in this snippet)

        elif self.shield_hp > 0:
            # Apply half damage to shield if shield is up
            self.shield_hp -= damage*0.5
            # Draw a visual indicator for shield hit
            pygame.draw.circle(screen, (0, 0, 255), (posX(self.x), posY(self.y)), 30 * player.zoom, width=3)
        # If shield is already down, apply full damage to hull
        else:
            self.hull_hp -= damage
        if self.hull_hp <= 0:
            self.die() # Die if hull is depleted

    def draw(self):
        a_mvt = self.angle # Angle for drawing the ship

        self.i = (self.i+1) % len(self.flame_animation) # Cycle through flame animation frames

        # Calculate scaled sprite size based on zoom
        sprite_size = (int(self.icon_rocket.get_width()*player.zoom*0.05), int(self.icon_rocket.get_height()*player.zoom*0.05))
        sprite_surface = pygame.Surface(sprite_size, pygame.SRCALPHA) # Create a transparent surface for the sprite
        rocket_scaled = pygame.transform.scale(player.icon_rocket, sprite_size) # Scale the rocket image
        sprite_surface.blit(rocket_scaled, (0, 0)) # Draw scaled rocket onto the surface

        if(self.thrust):
            # Scale and draw flame animation if thrusting
            flame_scaled = pygame.transform.scale(self.flame_animation[self.i], [sprite_size[0]/5, sprite_size[1]/3])
            sprite_surface.blit(flame_scaled, (sprite_size[0]*0.4, sprite_size[0]*0.7))

        # Rotate the combined sprite surface. -90 degrees likely aligns the sprite's default 'up' with angle 0 (right).
        rotated_sprite = pygame.transform.rotate(sprite_surface, -90 - math.degrees(a_mvt))
        # Draw the rotated sprite centered on the player's screen position
        screen.blit(rotated_sprite, (posX(self.x)-rotated_sprite.get_width()//2, posY(self.y)-rotated_sprite.get_height()//2))

        if(not self.throw):
            # Draw the launch projection line when landed
            pygame.draw.line(screen, (255, 255, 255), (posX(self.x), posY(self.y)), (posX(self.x + math.cos(self.angle) * self.projection_length), posY(self.y + math.sin(self.angle) * self.projection_length)))

    def ToggleInventory(self):
        # Toggle inventory GUI visibility
        self.inventory_opened = not self.inventory_opened
        if self.inventory_opened:
            # Create inventory GUI elements
            self.inventory_items = [] # Clear previous items
            # Create main inventory box
            self.inventory_box = Box(SCREEN_WIDTH/6,SCREEN_HEIGHT/6,(SCREEN_WIDTH/1.5,SCREEN_HEIGHT/1.5),relative_coords=False,relative_zoom=False,background_color=(102, 102, 102),border_color=(102, 102, 102),border_radius=20,border_width=20,z=4)
            # Create resource display box
            self.box_ressource = Box(SCREEN_WIDTH/6+15,SCREEN_HEIGHT/4,(SCREEN_WIDTH/3-30,SCREEN_HEIGHT/1.5-100),relative_coords=False,relative_zoom=False,border_color=(51,51,51),background_color=(51,51,51),border_radius=20,border_width=20,z=5)
            # Create planet defense purchase box
            self.box_planet_defense = Box(SCREEN_WIDTH/2+15,SCREEN_HEIGHT/4,(SCREEN_WIDTH/3-30,SCREEN_HEIGHT/1.5-100),relative_coords=False,relative_zoom=False,border_color=(51,51,51),background_color=(51,51,51),border_radius=20,border_width=20,z=5)
            # Add inventory title text
            self.inventory_text = Text("Inventory",SCREEN_WIDTH/6+15,SCREEN_HEIGHT/6+15,100,relative_coords=False,relative_zoom=False,z=5)
            n = 0
            # Add resource text and icons
            for i in self.ressources.keys():
                inventory_ressource = Text(str(i)+": "+str(round(self.ressources[i],1)),SCREEN_WIDTH/6+90,SCREEN_HEIGHT/4 + 15  + 50*n,50,relative_coords=False,relative_zoom=False,z=5)
                self.inventory_items.append(inventory_ressource)
                n += 1
            for id, i in enumerate(ressources.types):
                icon = ressources.icons[i]
                if icon != "":
                    img = Image(pygame.transform.scale(pygame.image.load(icon), (50, 50)),scale=1,fixed=True, x = SCREEN_WIDTH/6+30, y = SCREEN_HEIGHT/4 + 7 + 50 * id, z = 5)
                    self.inventory_items.append(img)
            # Calculate layout for weapon purchase buttons
            item_count = len(weapons.types)
            if item_count > 5:
                button_height = int((SCREEN_HEIGHT / 1.5 - 112) / item_count)
                text_size = max(25, button_height // 2)
            else:
                button_height = int((SCREEN_HEIGHT / 1.5 - 112)/5)
                text_size = max(25, button_height // 2)

            # Add weapon purchase buttons and text
            for id, i in enumerate(weapons.types):
                color = (0,255,0) # Default color (green)
                # Check if player has enough resources or if weapon is already on the planet
                for j in weapons.types[i]["ressources"].keys():
                    if self.ressources[j] < weapons.types[i]["ressources"][j] or i in self.planet.weapons_name:
                        color = (255,0,0) # Change color to red if requirements not met

                y_offset = SCREEN_HEIGHT / 4 + button_height * id - 12
                # Create button. The lambda function captures the current value of 'i' for the callback.
                btn = Button("", SCREEN_WIDTH / 2 + 30, y_offset + 25, 25, (SCREEN_WIDTH / 3 - 60, button_height - 25), background_color=color, border_color=color, relative_coords=False, relative_zoom=False, border_radius=20, border_width=20, z=5,callback=lambda i=i : self.Buy(i))
                defense_text = Text(i, SCREEN_WIDTH / 2 + 45, y_offset + 35, int(text_size), relative_coords=False, relative_zoom=False, z=5)
                cost_text = Text("Cost: " + str(weapons.types[i]["ressources"]), SCREEN_WIDTH / 2 + 45, y_offset + 35 + int(text_size), int(text_size // 2), relative_coords=False, relative_zoom=False, z=5)
                self.inventory_items.append(btn)
                self.inventory_items.append(defense_text)
                self.inventory_items.append(cost_text)
        else:
            # Destroy inventory GUI elements when closing
            for i in self.inventory_items:
                i.destroy()
            self.inventory_items = []
            self.box_planet_defense.destroy()
            self.box_ressource.destroy()
            self.inventory_text.destroy()
            self.inventory_box.destroy()

    def update(self):
        # Main player logic loop, runs continuously
        if(self.hull_hp <= 0 or self.ressources["Charbonites"] <= 0):
            self.die() # Die if hull or fuel is depleted

        box = None # Variable to hold the planet info box GUI element
        clock = pygame.time.Clock() # Clock for frame rate control
        button_delay = 0 # Timer for button press delay

        while True:
            start = time.perf_counter() # Start time for performance measurement
            keys = pygame.key.get_pressed() # Get current state of all keyboard keys

            if self.throw: # Logic when the player is in flight

                for i in Object.objects: # Iterate through all objects (planets, etc.)

                    if(i != self.planet): # Don't apply gravity from the planet the player just left
                        dist = math.sqrt((i.getAbsoluteX() - self.x)**2 + (i.getAbsoluteY() - self.y)**2) # Distance to the object

                        if(dist < 30): # Check for landing collision (distance less than 30)
                            self.x = i.getAbsoluteX() # Snap to planet position
                            self.y = i.getAbsoluteY()
                            self.vx = 0 # Stop movement
                            self.vy = 0
                            self.throw = False # Change state to landed
                            self.thrust = False
                            self.planet = i # Set current planet
                            self.time_on_planet = time.time() # Record landing time
                            # Transfer resources from the planet to the player
                            for j in self.ressources:
                                self.ressources[j] += i.reference.ressources[j]
                                i.reference.ressources[j] = 0

                        elif(dist != 0): # Apply gravity if not landed and distance is not zero
                            dx = (i.getAbsoluteX() - self.x) # Difference in x
                            dy = (i.getAbsoluteY() - self.y) # Difference in y

                            angle = math.atan2(dy, dx) # Angle towards the object

                            # Calculate acceleration due to gravity. 20000 seems like a scaling factor or assumed mass.
                            # This is a simplified gravity calculation (F=ma, F=G*m1*m2/r^2, assuming player mass m1=1 and object mass m2=20000/G or similar scaling)
                            a = 20000 * Object.G / (dist**2)

                            self.vx += math.cos(angle) * a # Add acceleration vector to velocity
                            self.vy += math.sin(angle) * a

                # Boundary checks: Bounce off map edges
                if(self.x > MAP_WIDTH):
                    self.x = MAP_WIDTH
                    self.vx = - abs(self.vx * 0.5) # Reverse and dampen velocity

                if(self.x < 0):
                    self.x = 0
                    self.vx = abs(self.vx * 0.5) # Reverse and dampen velocity

                if(self.y > MAP_HEIGHT):
                    self.y = MAP_HEIGHT
                    self.vy = - abs(self.vy * 0.5) # Reverse and dampen velocity

                if(self.y < 0):
                    self.y = 0
                    self.vy = abs(self.vy * 0.5) # Reverse and dampen velocity

                # Handle thrust input
                if keys[pygame.K_SPACE] and self.ressources["Charbonites"] > self.fuel_consumption:
                    self.thrust = True
                    self.ressources["Charbonites"] -= self.fuel_consumption # Consume fuel
                    self.vx += math.cos(self.angle) * self.speed # Add thrust vector to velocity
                    self.vy += math.sin(self.angle) * self.speed

                else:
                    self.thrust = False
                    # Consume a small amount of fuel even when not thrusting (e.g., life support)
                    if self.ressources["Charbonites"] < self.fuel_consumption /5:
                        self.die() # Die if fuel is critically low
                    else:
                        self.ressources["Charbonites"] -= self.fuel_consumption / 5

                # Toggle RCS (Reaction Control System)
                if keys[pygame.K_r] and (time.time() > button_delay + self.btn_delay):
                    button_delay = time.time()
                    self.rcs = not self.rcs

                if self.rcs: # If RCS is active
                    # Calculate the angle opposite to the current velocity vector (for braking/alignment)
                    target_angle = math.atan2(self.vy,self.vx) + math.pi
                    # Calculate the shortest angular difference between current angle and target angle
                    angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
                    if abs(angle_diff) > math.radians(self.turn_speed):
                        # Rotate towards the target angle
                        self.angle += math.copysign(math.radians(self.turn_speed), angle_diff)
                        self.angle %= (2 * math.pi) # Keep angle within 0 to 2*pi
                    elif abs(angle_diff) <= math.radians(self.turn_speed):
                             # If aligned, apply thrust (this seems to apply thrust even if not needed for braking, potentially a bug or feature)
                             self.thrust = True
                             self.ressources["Charbonites"] -= self.fuel_consumption
                             thrust_vx = math.cos(self.angle) * self.speed
                             thrust_vy = math.sin(self.angle) * self.speed
                             self.vx += thrust_vx
                             self.vy += thrust_vy
                             self.thrust # This line is redundant

                # Update position based on velocity. The /10 scales velocity per game tick.
                self.x += self.vx/10
                self.y += self.vy/10
                # Update distance traveled
                self.distance += math.sqrt((self.vx/10)**2 + (self.vy/10)**2)


            else: # Logic when the player is landed on a planet

                # Handle launching from the planet
                if (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]) and time.time() > button_delay + self.btn_delay and not self.calculating and not self.map and not self.inventory_opened:
                    if (self.ressources["Charbonites"] > self.fuel_consumption_throw):
                        button_delay = time.time()
                        self.throw = True # Change state to in flight
                        self.landing_count += 1 # Increment landing count
                        self.ressources["Charbonites"] -= self.fuel_consumption_throw # Consume fuel
                        # Set initial velocity based on current angle and throw speed
                        self.vx = self.throw_speed * math.cos(self.angle)
                        self.vy = self.throw_speed * math.sin(self.angle)
                    else:
                        self.die() # Die if not enough fuel to launch

                # Start trajectory calculation (Sondes)
                elif keys[pygame.K_s] and time.time() > button_delay + self.btn_delay and self.calculating == False:
                    button_delay = time.time()
                    self.calculating = True # Set calculating state
                    # Display calculation status text
                    self.traj = Text("Calcul de trajectoire en cours...", SCREEN_HEIGHT/2, SCREEN_WIDTH/2, 100,relative_coords=False,relative_zoom=False, color=(255,255,255))
                    # Create Sondes object and start the simulation in a separate thread
                    sd = Sondes(Object.objects,self.sonde_number,self)
                    player.sonde = sd
                    threading.Thread(target=sd.run, args=()).start()

                # Clear trajectory calculation results
                elif keys[pygame.K_c] and time.time() > button_delay + self.btn_delay and self.calculating == False:
                    button_delay = time.time()
                    self.accessible_planets = [] # Clear accessible planets list
                    self.parent.accessible_planets_object = [] # Clear accessible planet objects list
                    self.sonde = None # Clear Sondes object

                # Toggle map view
                elif keys[pygame.K_m] and time.time() > button_delay + self.btn_delay and self.calculating == False:
                    button_delay = time.time()
                    self.map = not self.map # Toggle map state
                    if self.map:
                        # Create map GUI elements when opening map
                        map_text = Text("Map",SCREEN_WIDTH/2.1, SCREEN_HEIGHT/15, 100,relative_coords=False,relative_zoom=False, color=(255,255,255),z=2)
                        for i in Object.objects:
                            if i in self.accessible_planets_object:
                                # Draw a green box around accessible planets on the map
                                map_box = Box(i.x-50,i.y-50,(110,110),relative_zoom=True,relative_coords=True,transparent_bg=True,border_color=(0,255,0),border_width=10,border_radius=10,z=1)
                                self.map_objects.append(map_box)
                    else:
                        # Destroy map GUI elements when closing map
                        map_text.destroy()
                        for i in self.map_objects:
                            i.destroy()
                        self.map_objects = []

                # Toggle debug mode
                elif keys[pygame.K_d] and time.time() > button_delay + self.btn_delay:
                    button_delay = time.time()
                    self.debug = not self.debug

                # Toggle inventory
                elif not self.calculating and keys[pygame.K_e] and time.time() > button_delay + self.btn_delay:
                    button_delay = time.time()
                    self.ToggleInventory()

                mouseState = pygame.mouse.get_pressed()[0] # Get state of left mouse button

                # wheel for zoom (not implemented in this snippet)


                if(mouseState and not self.oldMouseState):
                    # Record mouse position when left button is first pressed
                    self.oldMousePosition = pygame.mouse.get_pos()

                # Handle map panning and planet selection when map is open and left mouse button is held
                if mouseState and not self.throw and not self.calculating and self.map:
                    click_pos_screen = self.oldMousePosition # Use the position where the click started

                    for i in Object.objects: # Check each object
                        # Get object's screen coordinates
                        planet_screen_x, planet_screen_y = posX(i.x), posY(i.y)
                        # Calculate squared distance from the click origin to the object's screen center
                        click_dist_sq = (click_pos_screen[0] - planet_screen_x)**2 + (click_pos_screen[1] - planet_screen_y)**2

                        # Define a clickable radius around the object, scaled by zoom, with a minimum size
                        click_radius = max(20, i.r * self.zoom * 1.5)

                        # Check if the click was within the clickable radius of an object (and it's not the current planet)
                        if i != self.planet and click_dist_sq < click_radius**2:
                            self.selected_planet = i # Set the selected planet
                            # Create GUI box and text for planet information
                            box = Box(i.x+20,i.y+20,(400,200),relative_zoom=False,border_radius=20,border_width=20,background_color=(60,60,60),border_color=(60,60,60),z=2)
                            # Draw a blue box around the selected planet on the map
                            selected_box = Box(i.x-50,i.y-50,(110,110),relative_zoom=True,relative_coords=True,transparent_bg=True,border_color=(0,0,255),border_width=10,border_radius=10,z=1)
                            # Check if the planet is within the player's detection range (scaled by detector level)
                            if round(math.sqrt((i.getAbsoluteX() - self.x)**2 + (i.getAbsoluteY() - self.y)**2),1) < self.base_detection_range*1.5**self.detector_level:
                                # Display detailed info if detected
                                text = [f"Name: {i.reference.type}",f"Coords: x={i.x} y={i.y}",f"distance:{round(math.sqrt((i.getAbsoluteX() - self.x)**2 + (i.getAbsoluteY() - self.y)**2),1)}"]
                            else:
                                # Display '?' if not detected
                                text = [f"Name: ?",f"Coords: x=? y=?",f"distance:?"]
                            new_line_space = 0
                            for j in text:
                                txt = Text(j,i.x+25,i.y+25+new_line_space,20,relative_zoom=False,master_object=box,z=3)
                                new_line_space+=20
                                self.text_obj.append(txt)
                            # If the selected planet is in the list of accessible planets, set the player's launch angle
                            for accessible_planet, launch_angle in self.accessible_planets:
                                if accessible_planet == i:
                                    self.angle = launch_angle
                                    break # Found the angle, no need to check others

                            break # Exit the loop after finding a clicked planet
                        elif box != None:
                            # If no planet was clicked, destroy the info box if it exists
                            box.destroy()
                            selected_box.destroy()
                            for k in self.text_obj:
                                k.destroy()
                            self.text_obj = []
                            box = None # Clear the box variable

                # If map is closed, destroy the info box if it exists
                elif not self.map and box!= None:
                        box.destroy()
                        selected_box.destroy()
                        for k in self.text_obj:
                            k.destroy()
                        self.text_obj = []
                        box = None

                # Handle camera panning with left mouse drag
                if(mouseState):
                    pos = pygame.mouse.get_pos()
                    # Update cursor position based on mouse movement and zoom level
                    self.cursor[0] -= (pos[0] - self.oldMousePosition[0]) / self.zoom
                    self.cursor[1] -= (pos[1] - self.oldMousePosition[1]) / self.zoom

                    # Clamp cursor position to map boundaries
                    if(self.cursor[0] < 0):
                        self.cursor[0] = 0
                    if(self.cursor[0] > MAP_WIDTH):
                        self.cursor[0] = MAP_WIDTH
                    if(self.cursor[1] < 0):
                        self.cursor[1] = 0
                    if(self.cursor[1] > MAP_HEIGHT):
                        self.cursor[1] = MAP_HEIGHT

                else:
                    # Update old mouse position when not dragging
                    self.oldMousePosition = pygame.mouse.get_pos()

                # Update mouse state for the next frame
                self.oldMouseState = mouseState
                # This line seems redundant as oldMousePosition is updated above, but harmless.
                self.oldMousePosition = pygame.mouse.get_pos()

            # Handle player orientation
            # If in flight OR right mouse button is pressed, orient towards the mouse cursor
            if(self.throw or pygame.mouse.get_pressed()[2]):
                self.cursor = [self.x, self.y] # Center camera on player
                mouse_pos = pygame.mouse.get_pos() # Get current mouse position
                # Calculate mouse position relative to the screen center
                rel_x = mouse_pos[0] - SCREEN_WIDTH/2
                rel_y = mouse_pos[1] - SCREEN_HEIGHT/2
                # If right mouse button is pressed, set player angle directly to mouse direction
                if pygame.mouse.get_pressed()[2]:
                    self.angle = math.atan2(rel_y,rel_x)

            # Handle firing weapon when in flight and left mouse button is pressed (and reload time is met)
            if(self.throw and pygame.mouse.get_pressed()[0] and self.reloadTime < Object.t - 0.001):
                weapons.Projectile(self.x, self.y, self.angle, 60, 10, bot_players) # Create a projectile
                self.reloadTime = Object.t # Reset reload timer

            # Handle manual rotation with arrow keys
            if keys[pygame.K_LEFT]:
                    self.angle -= self.turn_speed * math.pi / 360 # Rotate left
            elif keys[pygame.K_RIGHT]:
                    self.angle += self.turn_speed * math.pi / 360 # Rotate right

            self.score = round(self.distance) # Update score based on distance
            clock.tick(60) # Limit frame rate to 60 FPS
            end = time.perf_counter() - start # Calculate duration of the current loop iteration
            # Update debug text for Player Update Speed (PUS)
            if player.debug:
                gui.update_fps.setText("PUS: " + str(round(1/end)))
            else:
                gui.update_fps.setText("") # Clear debug text if debug is off

    def Buy(self,weapon):
        # Handle purchasing a weapon for the current planet
        if weapon not in player.planet.weapons_name: # Check if the planet already has this weapon
            # Check if player has enough resources
            for j in weapons.types[weapon]["ressources"].keys():
                if player.ressources[j] < weapons.types[weapon]["ressources"][j]:
                    return # Cannot buy if resources are insufficient
            # If resources are sufficient and weapon is not already present:
            if weapon == "Laser":
                weapons.Laser(self.planet, bot_players) # Create the weapon instance (assuming Laser is the type bought)
            elif weapon == "MineLayer":
                weapons.MineLayer(self.planet, bot_players)
            player.planet.weapons_name.append(weapon) # Add weapon name to planet's list
            # Deduct resources
            for i in weapons.types[weapon]["ressources"].keys():
                player.ressources[i] -= weapons.types[weapon]["ressources"][i]
            # Refresh inventory GUI
            self.ToggleInventory()
            self.ToggleInventory()

class Sondes:

    def __init__(self,planets,n,parent=None):
        self.n = n # Number of sondes
        self.parent = parent # The player object that launched the sondes
        self.pos = np.zeros((n,2))   # NumPy array to store positions of sondes (n sondes, 2D coords)
        self.pos[:,0] = self.parent.x # Set initial X position for all sondes to player's X
        self.pos[:,1] = self.parent.y # Set initial Y position for all sondes to player's Y
        self.steps = 0 # Counter for simulation steps
        # NumPy array to store position history for drawing paths. Shape: (n sondes, 2D coords, max steps)
        self.position_history = np.zeros((n,2,10000))

        self.spe = np.zeros((n,2))   # NumPy array to store velocities of sondes (n sondes, 2D velocity)

        # Set initial velocities: spread sondes in a circle with player's throw speed
        for i in range(n):
            self.spe[i] = [math.cos(i*2*math.pi/n),math.sin(i*2*math.pi/n)]

        self.spe *= self.parent.throw_speed # Scale initial velocity vectors by throw speed

        self.planet_copy = planets # Copy the list of all objects

        # Remove the player's current planet from the list of potential targets
        for i in range(len(self.planet_copy)):
            if(self.planet_copy[i] == self.parent.planet):
                self.planet_copy = np.delete(self.planet_copy,i)
                break # Exit loop once found and removed

        if self.parent != None:
            # This initialization seems redundant with position_history and is overwritten later.
            # It might be intended to store history in a different shape (n, steps, 2) but position_history is used for raw data.
            self.sonde_history = np.zeros((n,10000, 2))

        self.planets = np.zeros((len(self.planet_copy),2))    # NumPy array to store positions of target planets

        # Array to store arrival data for each target planet: (sonde id, arrival time/step, launch angle)
        self.arrivals = np.zeros((len(self.planet_copy),3))
        self.arrivals[:,0] = -1 # Initialize sonde id to -1 (indicating no arrival yet)

        # Populate the planets array with target planet positions
        for i in range(len(self.planet_copy)):
            self.planets[i] = [self.planet_copy[i].x,self.planet_copy[i].y]

    def run(self):
        # Main simulation loop for sondes, runs in a separate thread
        s_time = time.perf_counter() # Start time for the entire simulation

        # Dictionary to store the *first* arrival data for each planet: {planet_object: (sonde_index, steps, angle)}
        first_arrivals_data = {}

        # Boolean array to keep track of which sondes are still active in the simulation
        active_sondes = np.ones(self.n, dtype=bool)

        while True:
            start = time.perf_counter() # Start time for the current simulation step

            # Get the global indices of currently active sondes
            current_active_indices = np.where(active_sondes)[0]
            if len(current_active_indices) == 0:
                 break # Exit loop if no sondes are active

            # Select positions and velocities only for active sondes using boolean indexing
            active_pos = self.pos[active_sondes]
            active_spe = self.spe[active_sondes]

            # Calculate difference vectors from each active sonde to each planet
            # np.newaxis adds a dimension for broadcasting (active_sondes, 1, 2) - (1, planets, 2) -> (active_sondes, planets, 2)
            diff = active_pos[:, np.newaxis, :] - self.planets[np.newaxis, :, :]
            # Calculate distances from each active sonde to each planet. axis=-1 sums over the last dimension (xy).
            dist = np.linalg.norm(diff, axis=-1)

            # Create a boolean mask indicating potential collisions (distance less than 30)
            collision_mask = dist < 30

            # Find indices (within the active_sondes subset) of sondes that collided with *any* planet
            # np.any(..., axis=1) checks if any planet column is True for a given sonde row
            collided_sondes_indices_local = np.where(np.any(collision_mask, axis=1))[0]

            if len(collided_sondes_indices_local) > 0: # If any collisions occurred in this step
                # Map local indices back to global sonde indices
                collided_sondes_indices_global = current_active_indices[collided_sondes_indices_local]

                # For each colliding sonde, find the index of the *first* planet it collided with
                # np.argmax returns the index of the first True value along the specified axis
                planets_hit_indices = np.argmax(collision_mask[collided_sondes_indices_local], axis=1)

                # Process each collision
                for i, sonde_global_idx in enumerate(collided_sondes_indices_global):
                    planet_hit_idx = planets_hit_indices[i]
                    planet_obj = self.planet_copy[planet_hit_idx] # Get the actual planet object

                    # If this planet hasn't been reached by any sonde yet
                    if planet_obj not in first_arrivals_data:
                         # Calculate the initial launch angle corresponding to this sonde's index
                         launch_angle = sonde_global_idx * 2 * math.pi / self.n
                         # Store the arrival data (sonde index, step count, launch angle)
                         first_arrivals_data[planet_obj] = (sonde_global_idx, self.steps, launch_angle)
                         # Store the position of the *colliding* sonde at the step *before* it was deactivated
                         if self.parent is not None:
                             self.position_history[sonde_global_idx, :, self.steps] = self.pos[sonde_global_idx]

                    active_sondes[sonde_global_idx] = False # Deactivate the sonde after it hits a planet

            # Re-get active indices after deactivating collided sondes
            current_active_indices = np.where(active_sondes)[0]
            if len(current_active_indices) == 0:
                 break # Exit loop if all sondes are now inactive

            # Select positions and velocities for the remaining active sondes
            active_pos = self.pos[active_sondes]
            active_spe = self.spe[active_sondes]

            # Recalculate difference vectors and distances for remaining active sondes
            diff = active_pos[:, np.newaxis, :] - self.planets[np.newaxis, :, :]
            # Add a small epsilon (1e-9) to distance to avoid division by zero if a sonde is exactly on a planet (shouldn't happen with collision check, but good practice)
            dist = np.linalg.norm(diff, axis=-1) + 1e-9

            # Calculate total gravitational acceleration on each active sonde from all planets
            # This is the core N-body simulation step using vectorized operations
            # (diff / dist[:, :, np.newaxis] ** 3) calculates normalized direction vectors scaled by inverse distance squared
            # .sum(axis=1) sums the acceleration vectors from all planets for each sonde
            # -Object.G * 20000 scales by gravity constant and assumed planet mass (20000) and applies attraction (-)
            accel = -Object.G * 20000 * (diff / dist[:, :, np.newaxis] ** 3).sum(axis=1)

            active_spe += accel # Update velocity based on acceleration

            # Boundary checks for active sondes: Bounce off map edges
            mask_right = active_pos[:, 0] > MAP_WIDTH
            mask_left = active_pos[:, 0] < 0
            mask_bottom = active_pos[:, 1] > MAP_HEIGHT
            mask_top = active_pos[:, 1] < 0

            active_spe[mask_right, 0] = -np.abs(active_spe[mask_right, 0]) * 0.5 # Reverse and dampen X velocity
            active_spe[mask_left, 0] = np.abs(active_spe[mask_left, 0]) * 0.5 # Reverse and dampen X velocity
            active_spe[mask_bottom, 1] = -np.abs(active_spe[mask_bottom, 1]) * 0.5 # Reverse and dampen Y velocity
            active_spe[mask_top, 1] = np.abs(active_spe[mask_top, 1]) * 0.5 # Reverse and dampen Y velocity

            # --- Store History & Update Position for active sondes ---
            # Store position history *before* updating position for this step
            if self.parent is not None and self.steps < self.position_history.shape[2]:
                 self.position_history[active_sondes, :, self.steps] = active_pos

            # Update position for active sondes based on velocity. The /10 scales velocity per simulation step.
            active_pos += active_spe / 10

            # --- Update global arrays ---
            self.pos[active_sondes] = active_pos # Update global positions for active sondes
            self.spe[active_sondes] = active_spe # Update global velocities for active sondes

            self.steps += 1 # Increment simulation step counter

            # --- Exit Conditions ---
            # Exit if max steps reached
            if self.steps >= self.position_history.shape[2]:
                print("Sonde simulation reached max steps.")
                break
            # Exit if no sondes left active
            if not np.any(active_sondes):
                # print(f"All sondes deactivated after {self.steps} steps.")
                break

            end = time.perf_counter() - start # Calculate duration of the current step
            # Update debug text for Sondes Update Speed (SUS)
            if self.parent is not None and hasattr(self.parent,"debug") and self.parent.debug:
                gui.sonde_update.setText("SUS: " + str(round(1/end)) if end > 0 else "SUS: inf")
            # Removed the else clause to keep the text if debug is turned off during calculation

        # --- Post-processing ---
        formated_arrivals_list = [] # List to store final accessible planets and angles
        formated_history_list = [] # This list is not used

        # Ensure history array is correctly sliced and transposed only for relevant sondes
        successful_sonde_indices = [] # List to store indices of sondes that successfully reached a planet
        for planet_obj, data in first_arrivals_data.items():
            sonde_idx, arrival_step, angle = data
            formated_arrivals_list.append((planet_obj, angle)) # Store only (planet, angle)
            successful_sonde_indices.append(sonde_idx)

        # Prepare history only for sondes that actually hit something recorded
        if self.parent is not None and len(successful_sonde_indices) > 0:
             # Get history up to the maximum arrival step found + buffer, or max steps
             max_hist_step = self.steps
             # Slice history for successful sondes up to max_hist_step. Shape: (successful sondes, 2, max_hist_step)
             relevant_history = self.position_history[successful_sonde_indices, :, :max_hist_step]
             # Transpose the history array from (sonde, xy, step) to (sonde, step, xy) for easier plotting/use
             self.parent.sonde_history = np.transpose(relevant_history, (0, 2, 1))

        elif self.parent is not None:
             self.parent.sonde_history = np.array([]) # Set history to an empty array if no successful sondes

        # Update parent player state *after* all calculations
        if self.parent is not None:
            self.parent.accessible_planets = formated_arrivals_list # Update the player's list of accessible planets

            self.parent.accessible_planets_object = [] # Populate list of just the planet objects
            for i in formated_arrivals_list:
                self.parent.accessible_planets_object.append(i[0])

            if self.parent == player:
                self.parent.traj.setText("") # Clear the "Calculating..." text
                if self.parent.traj in gui.textlist: # Check if text exists before removing
                    gui.textlist.remove(self.parent.traj)

            self.parent.calculating = False # Signal completion

            # Update debug texts for Recon Time and SUS
            if hasattr(self.parent,"debug"):
                gui.sonde_time.setText("Recon Time: " + str(round(time.perf_counter() - s_time, 3)))
                gui.sonde_update.setText("SUS: " + str(round(1/end)) if end > 0 else "SUS: inf")
            else: # Clear debug texts if debug is off
                 if hasattr(gui, "sonde_time"):
                     gui.sonde_time.setText("")
                 if hasattr(gui, "sonde_update"):
                     gui.sonde_update.setText("")