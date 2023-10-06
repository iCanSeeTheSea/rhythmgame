import sys

import pygame
from pygame.locals import QUIT


class GameManager:
    def __init__(self) -> None:
        # initialising pygame window
        pygame.init()
        self.window = pygame.display.set_mode((720, 500))
        pygame.display.set_caption('Rythmn Game')
        self.clock = pygame.time.Clock()
        self.player = Player(self.window)
        self.song = Song('pulsar.wav', False)
        pygame.mixer.init()

        # initialising beats, each beats default colour is slightly different
        # from those adjacent to it
        self.beats = [Beat(self.window, x=i * 90, colour_shift=abs((i - 4)) * 10, active=False) for i in range(8)]

        self.__active_beat = self.beats[self.song.sequence[self.song.current_note]]
        self.__active_range = self.__active_beat.set_active()
        self.speed = 6

    def game_loop(self):
        while True:
            self.window.fill((255, 255, 255))
            for beat in self.beats:
                beat.draw_self()
            self.player.draw_self(self.speed)
            self.player.score.update_score()

            if not self.song.playing:
                self.song.play()
                self.song.playing = True

            space_pressed = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not space_pressed:
                space_pressed = True
                # self.player.disallow_direction_change()
            else:
                # only allows direction to be changed after the space bar is depressed
                # self.player.allow_direction_change()
                space_pressed = False

            match self.player_in_beat():
                case 0:
                    if space_pressed:
                        self.__active_beat.set_hit((252, 73, 73))
                        self.player.score.update_score("none")
                case 1:
                    if space_pressed:
                        self.__active_beat.set_hit((73, 252, 73))
                        self.player.score.update_score("good")
                case 2:
                    if space_pressed:
                        self.__active_beat.set_hit((73, 252, 252))
                        self.player.score.update_score("perfect")
                case 3:
                    self.__active_beat.set_hit((252, 73, 73))
                    self.player.score.update_score("none")
                    self.player.change_direction()
                    self.player.allow_direction_change()
                    self.__active_beat.set_inactive()

                    # selecting the next active note
                    self.song.current_note += 1
                    self.__active_beat = self.beats[self.song.sequence[self.song.current_note]]
                    self.__active_range = self.__active_beat.set_active()
                    self.player.score.unlock_score_update()

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
            if player_range[1] + self.speed >= self.__active_range[1]:
                return 3
            elif player_range[1] + self.speed >= self.__active_range[0]:
                if player_range[0] + self.speed >= self.__active_range[0]:
                    return 2
                return 1
            return 0
        elif direction == "left":
            if player_range[0] - self.speed <= self.__active_range[0]:
                return 3
            elif player_range[0] - self.speed <= self.__active_range[1]:
                if player_range[1] - self.speed <= self.__active_range[1]:
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

    def draw_self(self, isPlayer: bool = False):
        rect = pygame.Rect(self._x, self._y, self._width, self._height)
        pygame.draw.rect(self._window, self._colour, rect)
        if isPlayer:
            # the player appears to move seamlessly from one side of the screen to the other
            rect1 = pygame.Rect(self._x + 720, self._y, self._width, self._height)
            rect2 = pygame.Rect(self._x - 720, self._y, self._width, self._height)
            pygame.draw.rect(self._window, self._colour, rect1)
            pygame.draw.rect(self._window, self._colour, rect2)

    def get_range(self):
        return self._x, self._x + self._width


class Player(Rectangle):
    def __init__(self, window) -> None:
        super().__init__(window, window.get_width() // 2, window.get_height() // 2 - 25, 90, 90, (146, 99, 247))
        self.__direction = "right"
        self.__direction_change = True
        self.score = Score(window)
        self.score.update_score()

    def draw_self(self, delta_x):
        self._x += self.__calculate_move(delta_x)
        if self._x > 720:
            self._x -= 720
        elif self._x < 0:
            self._x += 720
        super().draw_self(True)

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

class Score:
    def __init__(self, window):
        self.__window = window
        # monospace is the best font dont @ me :3
        self.__font = pygame.font.SysFont("monospace", 50)
        self.__score = 0
        self.__allow_update = True

    def __write_score(self):
        # score text has to be rendered every time it is updated
        score_surface = self.__font.render(f"{self.__score}", True, (146, 99, 247))
        self.__window.blit(score_surface, (0,0))

    def __increase_score(self, beat_success):
        # score can only update once per beat
        if self.__allow_update and beat_success:
            match beat_success:
                case "perfect":
                    self.__score += 10
                case "good":
                    self.__score += 5
                case "none":
                    pass
            self.__allow_update = False

    def unlock_score_update(self):
        self.__allow_update = True

    def update_score(self, beat_success=""):
        self.__increase_score(beat_success)
        self.__write_score()


class Song:
    def __init__(self, source, playing):
        self.source = source
        self.sequence = [  # Song sequence in note length form
            2, 2, 2, 2, 2, 2, 2, 2,
            2, 2, 2, 2, 2, 2, 2, 2,
            2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1,
            2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1,
            2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1,
            2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1,
            2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1,
            2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1,
            2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1,
            2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        ]
        self.playing = playing
        self.current_note = 0
        # Calculate which beats correspond to the note lengths above
        new_sequence = [4]

        for i in range(len(self.sequence)):
            if i % 2 == 0:
                new_sequence.append((new_sequence[i] - self.sequence[i]) % 8)
            else:
                new_sequence.append((new_sequence[i] + self.sequence[i]) % 8)

        self.sequence = new_sequence

    def play(self):
        pygame.mixer.music.load('pulsar.wav')
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()


if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.game_loop()
