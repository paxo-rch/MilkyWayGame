import pygame

MAP_SCALE = 10
MAP_WIDTH = 1080 * MAP_SCALE
MAP_HEIGHT = 1080 * MAP_SCALE
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

player = None # Placeholder for the player object

def posX(x):
    return SCREEN_WIDTH//2 + (x - player.cursor[0]) * player.zoom


def posY(y):
    return SCREEN_HEIGHT//2 + (y - player.cursor[1]) * player.zoom


class Text:
    textlist = []

    def __init__(self, text, x, y, size, relative=True, color=(255,255,255)):
        self.font = pygame.font.SysFont(None, size)
        self.text = text
        self.color = color
        self.render = self.font.render(self.text, True,pygame.Color(color[0],color[1],color[2]))
        self.x = x
        self.y = y
        self.size = size
        self.relative = relative
        Text.textlist.append(self)


    def update(self):
        if self.relative:
            screen.blit(self.render, (posX(self.x)*player.zoom, posY(self.y)*player.zoom))

        else:
            screen.blit(self.render, (self.x, self.y))


    def setText(self, text):

        if self.text != text:
            self.text = text
            self.render = self.font.render(self.text, True,pygame.Color(self.color[0],self.color[1],self.color[2]))


    def remove(self):
        Text.textlist.remove(self)


class Image:
    imagelist = []

    def __init__(self,image,scale=0.05,fixed=False,x=0,y=0):
        self.x = x
        self.y = y
        self.fixed = fixed
        self.scale = scale
        self.image = image
        self.scaled_image = None
        Image.imagelist.append(self)


    def update(self):
        if(self.fixed):
            screen.blit(self.image, (self.x,self.y))
            return
        
        if self.image is not None:
            self.scaled_image = pygame.transform.scale(self.image,(self.image.get_width()*player.zoom*self.scale,self.image.get_height()*player.zoom*self.scale))


    def remove(self):
        Image.imagelist.remove(self)