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
class Box:
    boxlist = []
    def __init__(self,x,y,size,relative_coords=True,relative_zoom=True,transparent_bg=False,transparent_border=False,border_color=(255,255,255),background_color=(255,255,255),border_radius=0,border_width=1,master_object=None):
        self.relative_coords = relative_coords
        self.relative_zoom = relative_zoom
        self.x = x
        self.y = y
        self.size = size
        self.transparent_bg = transparent_bg
        self.transparent_border = transparent_border
        self.border_color = border_color
        self.background_color = background_color
        self.border_radius = border_radius
        self.border_width = border_width
        self.master_object = master_object
        if self.master_object != None:
            self.coords_to_master = (master_object.x-self.x,master_object.y-self.y)
        Box.boxlist.append(self)
    def update(self):
        if self.master_object != None:
            self.x,self.y = (self.master_object.x-self.coords_to_master[0]/player.zoom,self.master_object.y-self.coords_to_master[1]/player.zoom)
        if self.relative_coords:
            x,y = (posX(self.x), posY(self.y))
        else:
            x,y = (self.x,self.y)
        if self.relative_zoom:
            width = round(self.border_width*player.zoom+0.99)
            radius = round(self.border_radius*player.zoom+0.99)
            size = ((self.size[0]*player.zoom-width),(self.size[1]*player.zoom-width))
        else:
            width = self.border_width
            radius = self.border_radius
            size = (self.size[0],self.size[1])
        self.render_bg = pygame.rect.Rect(x+width/2,y+width/2,size[0]-width,size[1]-width)
        self.render_border = pygame.rect.Rect(x,y,size[0],size[1])
        if not self.transparent_bg:
            pygame.draw.rect(screen,self.background_color,self.render_bg)
        if not self.transparent_border:
            pygame.draw.rect(screen,self.border_color,self.render_border,width,radius)
    def destroy(self):
        Box.boxlist.remove(self)

class Text:
    textlist = []

    def __init__(self, text, x, y, size, relative_coords=True, relative_zoom=True,color=(255,255,255),master_object = None):
        self.font = pygame.font.SysFont(None, size)
        self.text = str(text)
        self.color = color
        self.size = size
        self.relative_coords = relative_coords
        self.relative_zoom = relative_zoom
        self.render = self.font.render(self.text, True,pygame.Color(color[0],color[1],color[2]))
        self.x = x
        self.y = y
        self.master_object = master_object
        if self.master_object != None:
            self.coords_to_master = (master_object.x-self.x,master_object.y-self.y)
        self.size = size
        Text.textlist.append(self)


    def update(self):
        if self.master_object != None:
            self.x,self.y = (self.master_object.x-self.coords_to_master[0]/player.zoom,self.master_object.y-self.coords_to_master[1]/player.zoom)
        if self.relative_zoom:
            self.font = pygame.font.SysFont(None, round(self.size*player.zoom+0.99))
        
        self.render = self.font.render(self.text, True,pygame.Color(self.color[0],self.color[1],self.color[2]))
        if self.relative_coords:
            screen.blit(self.render, (posX(self.x), posY(self.y)))
        else:
            screen.blit(self.render, (self.x, self.y))


    def setText(self, text):

        if self.text != text:
            self.text = text
            self.render = self.font.render(self.text, True,pygame.Color(self.color[0],self.color[1],self.color[2]))


    def destroy(self):
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


    def destroy(self):
        Image.imagelist.remove(self)