import sys

import pygame
from pygame.locals import QUIT


class Game_Manager:
    def __init__(self) -> None:
        # initialising pygame window
        pygame.init()
        self.window = pygame.display.set_mode((720, 500))
        pygame.display.set_caption('Rythmn Game')
        self.clock = pygame.time.Clock()
        self.player = Player(self.window)
        self.song = Song('pulsar.wav',False)

        # initialising beats, each beats default colour is slightly different
        # from those adjacent to it
        self.beats = [Beat(self.window, x=i*90, colour_shift=abs((i-4))*10, active=False) for i in range(8)]

        self.__active_beat = self.beats[6]
        self.__active_range = self.__active_beat.set_active()
        
    def game_loop(self):
        while True:
            self.window.fill((255,255,255))
            for beat in self.beats:
                beat.draw_self()
            self.player.draw_self(6)

            if not self.song.playing:
              self.song.play()
              self.song.playing = True
          
            space_pressed = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                space_pressed = True
                self.player.disallow_direction_change()
            else:
                # only allows direction to be changed after the space bar is depressed
                self.player.allow_direction_change()

            match self.player_in_beat():
                case 0:
                    if space_pressed:
                        self.__active_beat.set_hit((252, 73, 73))
                case 1:
                    if space_pressed:
                        self.__active_beat.set_hit((73, 252, 73))
                        self.player.score += 5
                case 2:
                    if space_pressed:
                        self.__active_beat.set_hit((73, 252, 252))
                        self.player.score += 10
                case 3:
                    self.__active_beat.set_hit((252, 73, 73))
                    self.player.change_direction()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

            # running at 60 fps
            self.clock.tick(60)

    def player_in_beat(self):
        player_range = self.player.get_range()
        direction = self.player.get_direction()
        # 2: perfect score, 1: partial score, 0: no score, 3: player overshoot
        if direction == "right":
            if player_range[1] >= self.__active_range[1]:
                return 3
            elif player_range[1] >= self.__active_range[0]:
                if player_range[0] >= self.__active_range[0]:
                    return 2
                return 1
            return 0
        elif direction == "left":
            if player_range[0] <= self.__active_range[0]:
                return 3
            elif player_range[0] <= self.__active_range[1]:
                if player_range[1] <= self.__active_range[1]:
                    return 2
                return 1
            return 0


class Rectangle:
    def __init__(self, window, x, y, height, width, colour) -> None:
        self._window = window
        self._x = x
        self._y = y
        self._height = height
        self._width = width
        self._colour = colour

    def draw_self(self):
        rect = pygame.Rect(self._x, self._y, self._width, self._height)
        pygame.draw.rect(self._window, self._colour, rect)
        
    def get_range(self):
        return self._x, self._x+self._width


class Player(Rectangle):
    def __init__(self, window) -> None:
        super().__init__(window, window.get_width()//2 - 25, window.get_height()//2 - 25, 50, 50, (146, 99, 247))
        self.__direction = "right"
        self.__direction_change = True
        self.score = 0

    def draw_self(self, delta_x):
        self._x += self.__calculate_move(delta_x)
        super().draw_self()

    def change_direction(self):
        if self.__direction_change:
            self.__direction_change = False
            self.__direction = (lambda direction: "right" if direction == "left" else "left")(self.__direction)

    def get_direction(self):
        return self.__direction

    def disallow_direction_change(self):
        if self.__direction_change:
            self.__direction_change = False
        
    def allow_direction_change(self):
        if not self.__direction_change:
            self.__direction_change = True

    def __calculate_move(self, delta_x):
        match self.__direction:
            case "right":
                return delta_x
            case "left":
                return -delta_x


class Beat(Rectangle):
    def __init__(self, window, x, colour_shift, active) -> None:
        colour = (80 + colour_shift, 70 + colour_shift, 70 + colour_shift)
        super().__init__(window, x, 0, window.get_height(), 100, colour)
        self._default_colour = self._colour
        self._active = active

    def set_active(self):
        self._active = True
        self._colour = (252, 222, 90)
        return self.get_range()

    def set_hit(self, colour):
        if self._active:
            self._active = False
            self._colour = colour
    
    def set_inactive(self):
        self._active = False
        self._colour = self._default_colour


class Song:
  def __init__(self, source, playing):
    self.source = source
    self.sequence = []
    self.playing = playing
  def play(self):
      ...
    # audio.play_file(self.source)
    # Pygame audio doesn't work on replit. Might have to convert to github
        

if __name__ == '__main__':
    game_manager = Game_Manager()
    game_manager.game_loop()
