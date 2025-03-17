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
import gui
import graphics

PLANET_NUMBER = 500
MOON_NUMBER = 5


fps = 0

imagelist = []
textlist = []
path_list = []
imageplanete = graphics.Image(pygame.image.load("assets/planets/planet1.png"),scale=0.1)
imagelune = graphics.Image(pygame.image.load("assets/moons/moon1.png"))

mytext = graphics.Text("Fuel: ", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.9, 50, relative=False, color=(255,255,255))
score = graphics.Text("Score: ", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.05, 50, relative=False, color=(255,255,255))
fps_text = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.1, 50, relative=False, color=(255,255,255))
update_fps = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.2, 50, relative=False, color=(255,255,255))
sonde_update = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.15, 50, relative=False, color=(255,255,255))	
sonde_time = graphics.Text("", graphics.SCREEN_WIDTH*0.05, graphics.SCREEN_HEIGHT*0.25, 50, relative=False, color=(255,255,255))

for i in range(PLANET_NUMBER):
    type = random.choice(planets.Planet.types)
    multiplier = random.randint(1, 2)

    reference = planets.Planet(random.randint(0, graphics.MAP_WIDTH), random.randint(0, graphics.MAP_WIDTH), type, entities.Object.objects, multiplier)

    o = entities.Object(random.randint(0, graphics.MAP_WIDTH), random.randint(0, graphics.MAP_WIDTH), multiplier)
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

graphics.player = entities.Player(entities.Object.objects[0])
entities.player = graphics.player
threading.Thread(target=entities.player.update,args=()).start()




while True:
    start = time.perf_counter()
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEWHEEL:
                
                if entities.player.zoom* ((event.y*0.2) +1) < 6 and entities.player.zoom* ((event.y*0.2) +1) > 0.1:
                    entities.player.zoom *= (event.y)*0.2 + 1

    graphics.screen.fill((0, 0, 0))
    entities.Object.time()

    for i in graphics.Image.imagelist:
        i.update()

    for i in entities.Object.objects:
        i.updateAll()
        i.drawAll()

        if entities.player.map:
            pygame.draw.circle(graphics.screen, (255, 0, 0), (graphics.posX(i.x), graphics.posY(i.y)), 20 * entities.player.zoom)

            if i == entities.player.selected_planet:
                pygame.draw.circle(graphics.screen, (0, 0, 255), (graphics.posX(i.x), graphics.posY(i.y)), 20 * entities.player.zoom)

    for i in graphics.Text.textlist:
        i.update()



    if entities.player.sonde is not None:
            for i in entities.player.sonde.sonde_history:
                    path = i[:entities.player.sonde.steps]
                    if len(path) >= 2:
                        points = np.column_stack((graphics.posX(path[:, 0]), graphics.posY(path[:, 1]))).astype(int)
                        if entities.player.path:
                            pygame.draw.aalines(graphics.screen, (255, 255, 255), False, points)
    mytext.setText("Fuel: " + str(round(entities.player.fuel,1)))
    score.setText("Score: " + str(entities.player.score))
    if entities.player.debug:
        fps_text.setText("FPS: " + str(round(1/fps)))
    else:
        fps_text.setText("")
        update_fps.setText("")
        sonde_update.setText("")
        sonde_time.setText("")
    
    entities.player.draw()
    time.sleep(1/60)
    pygame.display.update()
    fps = time.perf_counter() - start
    