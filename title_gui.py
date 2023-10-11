import pygame, math
from sys import exit

class guiManager:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((810,500))
        self.clock = pygame.time.Clock()
        self.bg_colour = 0
        self.background = [box(self.window, x=i * 90, colour_shift= (i * 5)+self.bg_colour) for i in range(9)]
        self.press_start = image('press_space.png', 249, 10, 4)
        self.space_bar = image('space_bar_1.png', 249, 300, 9.8)
        self.frame_counter = 0
        self.start_game = False

    def gui_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.window.fill((255,255,255))
            for beat in range(9):
                self.background[beat]._colour = angleToColour((beat * 5)+self.bg_colour)
                self.background[beat].draw()
            self.press_start.draw()

            self.frame_counter += 1
            self.frame_counter = self.frame_counter%8
            match self.frame_counter:
                case 0:
                    self.space_bar.source = 'space_bar_1.png'
                case 2:
                    self.space_bar.source = 'space_bar_2.png'
                case 4:
                    self.space_bar.source = 'space_bar_3.png'
                case 6:
                    self.space_bar.source = 'space_bar_2.png' 
            self.space_bar.draw()
            self.bg_colour += 0.5
            self.bg_colour = self.bg_colour%360
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.start_game = True
                exit()

            pygame.display.update()
            self.clock.tick(60)

def angleToColour(angle):
    """
    Convert an angle in degrees to a colour in RGB
    """
    def rad(angle):
        return (angle/180)*math.pi
    red = 256*math.cos(rad(angle))+128
    green = 256*math.cos(rad(angle-120))+128
    blue = 256*math.cos(rad(angle-240))+128
    if red > 255:
        red = 255
    elif red < 0:
        red = 0
    if green > 255:
        green = 255
    elif green < 0:
        green = 0
    if blue > 255:
        blue = 255
    elif blue < 0:
        blue = 0
    return red,green,blue

class box:
    def __init__(self, window, x, colour_shift):
        self._colour = angleToColour(colour_shift)
        self._window = window
        self._x = x
        self._y = 0
        self._width = self._window.get_width()//8
        self._height = self._window.get_height()
    def draw(self):
        rect = pygame.Rect(self._x, self._y, self._width, self._height)
        pygame.draw.rect(self._window,self._colour,rect)

class image:
    def __init__(self, source, x, y, scale = 1):
        self.source = source
        self.x = x
        self.y = y
        self.xv = 0
        self.yv = 0
        self.scale = scale
    def draw(self):
        img = pygame.image.load(self.source)
        img = pygame.transform.scale(img,(img.get_width()*self.scale,img.get_height()*self.scale))
        gui_manager.window.blit(img, (self.x, self.y))

if __name__ == '__main__':
    gui_manager = guiManager()
    gui_manager.gui_loop()