import pygame
import math
import random
import time
import threading
import time
import socket
import numpy as np
import multiprocessing

# custom libraries
import planets
import entities
import bot
import weapons
import gui
import graphics
import ressources

PLANET_NUMBER = 500
MOON_NUMBER = 3

planets.Planet.load_planets()

fps = 0

imagelist = []
textRessources = []
textlist = []
path_list = []
imageplanete = graphics.Image(pygame.image.load("assets/planets/planet1.png"),scale=0.1)
imagelune = graphics.Image(pygame.image.load("assets/moons/moon1.png"))

mytext = graphics.Text("Fuel: ", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.9, 50, relative_coords=False,relative_zoom=False, color=(150,150,150))
score = graphics.Text("Score: ", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.05, 50, relative_coords=False,relative_zoom=False, color=(150,150,150))
fps_text = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.1, 50, relative_coords=False,relative_zoom=False, color=(150,150,150))
update_fps = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.2, 50, relative_coords=False,relative_zoom=False, color=(150,150,150))
sonde_update = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.15, 50, relative_coords=False,relative_zoom=False, color=(150,150,150))	
sonde_time = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.25, 50, relative_coords=False,relative_zoom=False, color=(150,150,150))

for i in range(PLANET_NUMBER):
    types = list(planets.Planet.types.keys())

    pad = random.random() * 100
    prob = [25, 25, 9, 15, 15, 10, 1]

    r = random.random() * sum(prob)
    for i in range(len(prob)):
        if r < prob[i]:
            type = types[i]
            break
        r -= prob[i]

    reference = planets.Planet(
         random.randint(0, graphics.MAP_WIDTH), # x
         random.randint(0, graphics.MAP_HEIGHT), # y
         type,                                  # type
         entities.Object.objects,               # object linked
         ressources.generate_ressources(type))                            # ressources dictionnary

    o = entities.Object(
         random.randint(0, graphics.MAP_WIDTH),
         random.randint(0, graphics.MAP_HEIGHT),
         1) # mass
    
    o.image = imageplanete
    o.transparent = True
    o.reference = reference

    for j in range(random.randint(0, MOON_NUMBER)):
        c = entities.Object(0, 0, 5)
        c.r = 5
        c.m = random.randint(1, 10)
        c.setParent(o,random.randint(50, 200))
        c.transparent = True
        c.image = imagelune

    entities.Object.objects.append(o)

# The player is responsible for updating its position and throw state
graphics.player = entities.Player(entities.Object.objects[0])
entities.player = graphics.player
bots = []
for i in range(1):
    bot_player = bot.Bot(random.choice(entities.Object.objects))
    threading.Thread(target=bot_player.update,args=()).start()
    bots.append(bot_player)

laser = weapons.Laser(entities.Object.objects[0], entities.player)

# Start the player thread
threading.Thread(target=entities.player.update,args=()).start()

# Affichage des ressources
for id, i in enumerate(ressources.types):
    icon = ressources.icons[i]
    if icon != "":
        img = graphics.Image(pygame.transform.scale(pygame.image.load(icon), (50, 50)),scale=0.1,fixed=True, x = 0, y = 50 * id)
        imagelist.append(img)
        txt = graphics.Text(i + ": " + str(int(graphics.player.ressources[i])), 50, 50 * id + 10, 40, relative_coords=False,relative_zoom=False, color=(150,150,150))
        textlist.append(txt)
        textRessources.append(txt)

def update_ressources_box():
    # Mise a jour de la boite de ressources
    for i,txt in enumerate(textRessources):
        txt.setText(ressources.types[i] + ": " + str(int(graphics.player.ressources[ressources.types[i]])))

r = 0

planets.Planet.update_images()
clock = pygame.time.Clock()
while True:
    start = time.perf_counter()
    
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEWHEEL:
            if entities.player.zoom* ((event.y*0.2) +1) < 6 and entities.player.zoom* ((event.y*0.2) +1) > 0.1:
                entities.player.zoom *= (event.y)*0.2 + 1
                planets.Planet.update_images()

    graphics.screen.fill((10, 15, 30))
    entities.Object.time()

    update_ressources_box()

    for i in graphics.Image.imagelist:
        i.update()

    for i in entities.Object.objects:
        i.updateAll()
        i.drawAll()

    for i in graphics.Image.imagelist:
        i.update()
    entities.player.draw()
    for i in bots:
        i.draw()
        i.update()
        
    weapons.Weapon.updateAll()
    weapons.Weapon.drawAll()
    
    for i in sorted(graphics.hierarchy_list.keys()):
        for j in graphics.hierarchy_list[i]:
            j.update()


    mytext.setText("Fuel: " + str(round(entities.player.ressources["Charbonites"],1)))
    score.setText("Score: " + str(entities.player.score))
    if entities.player.debug:
        fps_text.setText("FPS: " + str(round(1/fps)))
    else:
        fps_text.setText("")
        update_fps.setText("")
        sonde_update.setText("")
        sonde_time.setText("")
    
    clock.tick(60)

    pygame.display.update()
    fps = time.perf_counter() - start
    