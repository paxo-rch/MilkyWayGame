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


imageplanete = graphics.Image(pygame.image.load("assets/planets/planet1.png"),scale=0.1)
imagelune = graphics.Image(pygame.image.load("assets/moons/moon1.png"))




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

for i in range(10):
    bot_player = bot.Bot(random.choice(entities.Object.objects))
    threading.Thread(target=bot_player.update,args=()).start()
    entities.bot_players.append(bot_player)

laser = weapons.Laser(entities.Object.objects[0], entities.bot_players)

# Start the player thread
threading.Thread(target=entities.player.update,args=()).start()


for i in entities.Object.objects:
    MineLayer = weapons.MineLayer(i, entities.bot_players)


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


    for i in entities.Object.objects:
        i.updateAll()
        i.drawAll()

    entities.player.draw()
    for i in bot.bot_players:
        i.draw()
        i.update()
        
    weapons.Weapon.updateAll()
    weapons.Weapon.drawAll()
    
    for i in sorted(graphics.hierarchy_list.keys()):
        for j in graphics.hierarchy_list[i]:
            j.update()
    for i in graphics.buttons:
        i.update()

    gui.mytext.setText(str(round(entities.player.ressources["Charbonites"],1)))
    gui.score.setText("KDR ratio: " + str(entities.player.kills/entities.player.death))
    gui.hull_pv.setText(str(entities.player.hull_hp))
    gui.shield_pv.setText(str(entities.player.shield_hp))
    if entities.player.debug:
        gui.fps_text.setText("FPS: " + str(round(1/fps)))
    else:
        gui.fps_text.setText("")
        gui.update_fps.setText("")
        gui.sonde_update.setText("")
        gui.sonde_time.setText("")
    
    clock.tick(60)

    pygame.display.update()
    fps = time.perf_counter() - start
    