from graphics import *

fps = 0

imagelist = []
textlist = []
path_list = []
imageplanete = Image(pygame.image.load("assets/planets/planet1.png"),scale=0.1)
imagelune = Image(pygame.image.load("assets/moons/moon1.png"))

mytext = Text("Fuel: ", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.9, 50, relative=False, color=(255,255,255))
score = Text("Score: ", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.05, 50, relative=False, color=(255,255,255))
fps_text = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.1, 50, relative=False, color=(255,255,255))
update_fps = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.2, 50, relative=False, color=(255,255,255))
sonde_update = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.15, 50, relative=False, color=(255,255,255))	
sonde_time = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.25, 50, relative=False, color=(255,255,255))
