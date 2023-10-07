import sys

import pygame
from pygame.locals import QUIT

"""
Mintlify Doc Writer used to help write function docstrings
https://writer.mintlify.com/
"""

class GameManager:
    def __init__(self) -> None:
        """
        Initializes a Pygame window, sets the caption, and initializes a clock, player, song, and beats.
        """
        # initialising pygame window
        pygame.init()
        self.window = pygame.display.set_mode((810, 500))
        pygame.display.set_caption('Rhythm Game')
        self.clock = pygame.time.Clock()

        self.player = Player(self.window)
        self.song = Song('pulsar.wav', False)
        pygame.mixer.init()

        # initialising beats, each beats default colour is slightly different
        # from those adjacent to it
        self.beats = [Beat(self.window, x=i * 90, colour_shift=abs((i - 4)) * 10, active=False) for i in range(9)]

        self.__active_beat = self.beats[self.song.sequence[self.song.current_note]]
        self.__active_range = self.__active_beat.set_active()
        self.speed = 6

    def game_loop(self):
        """
        The `game_loop` function is responsible for running the main game loop, updating the game state, handling player
        input, and updating the display.
        """
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
        """
        The function `player_in_beat` checks if the player's range is within the active range and returns a code based on
        the direction and position of the player.
        :return: a code based on the player's position and direction in relation to the active range. The possible
        return values are:
        - 2: perfect score
        - 1: partial score
        - 0: no score
        - 3: player overshoot
        """
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
        """
        The function initializes an object with window, x, y, height, width, and colour attributes.

        :param window: The "window" parameter represents the pygame surface on which the object will be drawn.
        :param x: The x parameter represents the x-coordinate of the top left corner of the object
        :param y: The parameter "y" represents the y-coordinate of the top left corner of the object
        :param height: The "height" parameter represents the height (in pixels) of the object .
        :param width: The "width" parameter represents the width (in pixels) of the object.
        :param colour: The "colour" parameter represents the color of the object (Red, Green, Blue).
        """
        self._window = window
        self._x = x
        self._y = y
        self._height = height
        self._width = width
        self._colour = colour

    def draw_self(self, delta_x=0, isPlayer: bool = False):
        """
        The function draws a rectangle on a window and if the player is specified

        It also draws two additional rectangles for the player when they move off the screen
        to create the illusion of seamless movement from one side to the other.

        :param delta_x: amount the x value of the rectangle should change by between frames
        :param isPlayer: boolean value that indicates whether the object being drawn is the
        player or not. If `isPlayer` is `True`, then the player object will appear to move seamlessly from one side of the
        screen to the other, defaults to False
        :type isPlayer: bool (optional)
        """
        rect = pygame.Rect(self._x, self._y, self._width, self._height)
        pygame.draw.rect(self._window, self._colour, rect)
        if isPlayer:
            # the player appears to move seamlessly from one side of the screen to the other
            rect1 = pygame.Rect(self._x + self._window.get_width(), self._y, self._width, self._height)
            rect2 = pygame.Rect(self._x - self._window.get_width(), self._y, self._width, self._height)
            pygame.draw.rect(self._window, self._colour, rect1)
            pygame.draw.rect(self._window, self._colour, rect2)

    def get_range(self):
        """
        The function returns a tuple containing the minimum and maximum x values the rectangle spans.
        :return: The method is returning a tuple containing the starting and ending values of a range. The starting value is
        stored in the variable self._x, and the ending value is calculated by adding the width (stored in self._width) to
        the starting value.
        """
        return self._x, self._x + self._width


class Player(Rectangle):
    def __init__(self, window) -> None:
        """
        The function initializes a rectangle object with certain attributes and creates a score object.

        :param window: The "window" parameter is the pygame surface on which the player is drawn.
        """
        super().__init__(window, 425, window.get_height() // 2 - 25, 90, 90, (146, 99, 247))
        self.__direction = "right"
        self.__direction_change = True
        self.score = Score(window)
        self.score.update_score()

    def draw_self(self, delta_x=0, isPlayer=True):
        """
        The function updates the x-coordinate of an object, ensuring it stays within the window boundaries, and then calls a
        superclass method to draw the object.

        :param delta_x: The `delta_x` parameter represents the change in the x-coordinate of the object's position. It is
        used to calculate the new x-coordinate of the object after it moves, wraps around to 0 if it goes outside the screen width
        :param isPlayer: The `isPlayer` parameter is a boolean value that indicates whether the object being drawn is the
        player or not. It is used to allow the player to seamlessly wrap from one side of the screen to the other, defaults to True
        (optional)
        """
        self._x += self.__calculate_move(delta_x)
        if self._x > self._window.get_width():
            self._x -= self._window.get_width()
        elif self._x < 0:
            self._x += self._window.get_width()
        super().draw_self(isPlayer)

    def change_direction(self):
        """
        Changes the direction from "left" to "right" or vice versa.
        """
        if self.__direction_change:
            self.__direction_change = False
            self.__direction = (lambda direction: "right" if direction == "left" else "left")(self.__direction)

    def get_direction(self):
        """
        :return: The direction of the object.
        """
        return self.__direction

    def disallow_direction_change(self):
        """
        Sets the __direction_change attribute to False if it is currently True.
        """
        if self.__direction_change:
            self.__direction_change = False

    def allow_direction_change(self):
        """
        Sets the __direction_change attribute to True if it is currently False.
        """
        if not self.__direction_change:
            self.__direction_change = True

    def __calculate_move(self, delta_x):
        """
        The function calculates if the move should be in positive or negative x based on the direction.

        :param delta_x: The parameter `delta_x` represents the amount of movement in the x-direction.
        :return: The updated value of `delta_x` is being returned.
        """
        match self.__direction:
            case "right":
                return delta_x
            case "left":
                return -delta_x


class Beat(Rectangle):
    def __init__(self, window, x, colour_shift, active) -> None:
        """
        The function initializes an object with a specified window, x-coordinate, color shift, and active status.

        :param window: The "window" parameter is the pygame surface on which the beat is to be drawn
        :param x: The `x` parameter represents the x-coordinate of the object's position on the window
        :param colour_shift: The `colour_shift` parameter is used to adjust the RGB values of the `colour` attribute. It is
        added to each RGB value (red, green, and blue) to create a new color.
        :param active: The "active" parameter is a boolean value that determines whether the object is currently active or
        not. It is used to control the behavior or appearance of the object based on its active state
        """
        colour = (80 + colour_shift, 70 + colour_shift, 70 + colour_shift)
        super().__init__(window, x, 0, window.get_height(), 100, colour)
        self._default_colour = self._colour
        self._active = active

    def set_active(self):
        """
        The function sets an object as active and changes its color to yellow.
        :return: The method `get_range()` is being called and its return value is returned.
        """
        self._active = True
        self._colour = (252, 222, 90)
        return self.get_range()

    def set_hit(self, colour):
        """
        The function sets the active status to false and assigns a specified color to the beat.

        :param colour: The "colour" parameter is the color that will be set for the object
        """
        if self._active:
            self._active = False
            self._colour = colour

    def set_inactive(self):
        self._active = False
        self._colour = self._default_colour


class Score:
    def __init__(self, window):
        """
        The function initializes the class instance with a window, font, score, and update flag.

        :param window: The "window" parameter is the pygame surface where the score will be displayed
        """
        self.__window = window
        # monospace is the best font dont @ me :3
        self.__font = pygame.font.SysFont("monospace", 50)
        self.__score = 0
        self.__allow_update = True

    def __write_score(self):
        """
        The function renders the score text and blits it onto the window.
        """
        # score text has to be rendered every time it is updated
        score_surface = self.__font.render(f"{self.__score}", True, (146, 99, 247))
        self.__window.blit(score_surface, (0, 0))

    def __increase_score(self, beat_success):
        """
        The function increases the score based on the success of a beat, but only allows the score to update once per beat.

        :param beat_success: The parameter "beat_success" is a string that represents how close the player clicked to the beat. It can have
        three possible values: "perfect", "good", or "none"
        """
        # score can only update once per beat
        if self.__allow_update:
            match beat_success:
                case "perfect":
                    self.__score += 10
                case "good":
                    self.__score += 5
                case "none":
                    pass
            self.__allow_update = False

    def unlock_score_update(self):
        """
        Sets the `__allow_update` attribute of the object to `True`.
        """
        self.__allow_update = True

    def update_score(self, beat_success=""):
        """
        The function updates the score by increasing it and then writes the updated score.

        :param beat_success: The "beat_success" parameter is a string that represents whether the beat was successful or
        not. It is used to determine whether to increase the score or not
        """
        if beat_success:
            self.__increase_score(beat_success)
        self.__write_score()


class Song:
    def __init__(self, source, playing):
        """
        The function initializes an object with a source, a sequence of note lengths, a playing status, and a current note
        index.

        :param source: The `source` parameter is used to specify the source of the music. It could be a file path to a music
        file, a URL to a music stream, or any other valid source of music data
        :param playing: The "playing" parameter is a boolean value that indicates whether the song is currently playing or
        not. It is used to control the playback of the song
        """
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
                new_sequence.append((new_sequence[i] - self.sequence[i]) % 9)
            else:
                new_sequence.append((new_sequence[i] + self.sequence[i]) % 9)

        self.sequence = new_sequence

    def play(self):
        """
        The function loads and plays a music file using the pygame library.
        """
        pygame.mixer.music.load(self.source)
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()


if __name__ == '__main__':
    game_manager = GameManager()
    game_manager.game_loop()