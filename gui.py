from graphics import *

fps = 0

imagelist = []
textlist = []
path_list = []
imageplanete = Image(pygame.image.load("assets/planets/planet1.png"),scale=0.1)
imagelune = Image(pygame.image.load("assets/moons/moon1.png"))

mytext = Text("", SCREEN_WIDTH*0.19, SCREEN_HEIGHT*0.9, 50, relative_coords=False,relative_zoom=False, color=(255,255,255))
fuel_img = Image(pygame.image.load("assets/emoji/fuelpump.png"),scale=0.2,x=SCREEN_WIDTH*0.23,y=SCREEN_HEIGHT*0.9,fixed=True)
score = Text("KDR ratio: ", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.05, 50, relative_coords=False,relative_zoom=False, color=(255,255,255))
fps_text = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.1, 50, relative_coords=False,relative_zoom=False, color=(255,255,255))
update_fps = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.2, 50, relative_coords=False,relative_zoom=False, color=(255,255,255))
sonde_update = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.15, 50, relative_coords=False,relative_zoom=False, color=(255,255,255))	
sonde_time = Text("", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.25, 50, relative_coords=False,relative_zoom=False, color=(255,255,255))

hull_pv = Text("100", SCREEN_WIDTH*0.05, SCREEN_HEIGHT*0.9, 50, relative_coords=False,relative_zoom=False, color=(0,255,0))
hull_pv_image = Image(pygame.image.load("assets/emoji/heart.png"),scale=0.2,x=SCREEN_WIDTH*0.09,y=SCREEN_HEIGHT*0.9,fixed=True)
shield_pv = Text("100", SCREEN_WIDTH*0.12, SCREEN_HEIGHT*0.9, 50, relative_coords=False,relative_zoom=False, color=(0,0,255))
shield_pv_image = Image(pygame.image.load("assets/emoji/shield.png"),scale=0.2,x=SCREEN_WIDTH*0.16,y=SCREEN_HEIGHT*0.9,fixed=True)
