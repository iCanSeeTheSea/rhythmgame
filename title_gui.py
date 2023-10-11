from sys import exit

import math
import pygame

from main import Score
from pathlib import Path

"""
Mintlify Doc Writer used to help write function docstrings
https://writer.mintlify.com/
"""

UI_PATH = Path("./UI")


class GuiManager:
    def __init__(self, stats: tuple = None) -> None:
        """
        Initializes a Pygame window and sets up various game elements such as the
        background, start prompt, and space bar image.
        """
        pygame.init()
        self.__window = pygame.display.set_mode((810, 500))
        pygame.display.set_caption('Rhythm Game')
        self.__clock = pygame.time.Clock()

        self.__bg_colour = 0
        self.__background = [Box(self.__window, x=i * 90, colour_shift=(i * 5) + self.__bg_colour) for i in range(9)]

        self.__press_start = Image(self.__window, UI_PATH / 'press_space.png', 249, 10, 4)
        self.__space_bar = Image(self.__window, UI_PATH / 'space_bar_1.png', 249, 300, 9.8)
        self.__frame_counter = 0
        self.start_game = False

        self.__score = None
        if stats is not None:
            (score, beat_stats) = stats
            self.__score = Score(self.__window, 30, score, beat_stats)

    def gui_loop(self) -> None:
        """
        The function `gui_loop` is a continuous loop that handles events, updates the GUI, and checks for the space bar key
        press to start the game.
        :return: The `start_game` variable is being returned.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.__window.fill((255, 255, 255))

            for beat in range(9):
                self.__background[beat].set_colour((beat * 5) + self.__bg_colour)
                self.__background[beat].draw()
            self.__press_start.draw()

            if self.__score is not None:
                self.__score.write_score((320, 150))
                self.__score.write_beat_stats((140, 200))

            # Space bar animation
            self.__frame_counter += 1
            self.__frame_counter = self.__frame_counter % 8
            match self.__frame_counter:
                case 0:
                    self.__space_bar._source = UI_PATH / 'space_bar_1.png'
                case 2:
                    self.__space_bar._source = UI_PATH / 'space_bar_2.png'
                case 4:
                    self.__space_bar._source = UI_PATH / 'space_bar_3.png'
                case 6:
                    self.__space_bar._source = UI_PATH / 'space_bar_2.png'
            self.__space_bar.draw()

            # Background animation
            self.__bg_colour += 1
            self.__bg_colour = self.__bg_colour % 360

            keys = pygame.key.get_pressed()

            if keys[pygame.K_SPACE]:
                self.start_game = True
                return

            pygame.display.update()
            self.__clock.tick(60)


class Box:
    def __init__(self, window: pygame.Surface, x: int, colour_shift: int) -> None:
        """
        The function initializes an object with a pygame surface, x-coordinate, and color shift.

        :param window: The `window` parameter is a pygame surface onto which the object will be drawn.
        :type window: pygame.Surface
        :param x: The x-coordinate of the top left corner of the object on the window.
        :type x: int
        :param colour_shift: Used to determine the initial color of the object. It is passed to the `set_colour` method to set the color of the object. The specific value of `colour_shift` will determine the color of the object
        :type colour_shift: int
        """
        self._colour = None
        self.set_colour(colour_shift)
        self._window = window
        self._x = x
        self._y = 0
        self._width = self._window.get_width() // 8
        self._height = self._window.get_height()

    def draw(self) -> None:
        rect = pygame.Rect(self._x, self._y, self._width, self._height)
        pygame.draw.rect(self._window, self._colour, rect)

    def set_colour(self, angle: int) -> None:
        """
        Converts an angle in degrees to a colour in RGB for the colour

        :param angle: The `angle` parameter represents an angle in degrees
        :type angle: int
        """

        # Calculate the value of each colour channel from the angle
        red = 256 * math.cos(math.radians(angle)) + 128
        green = 256 * math.cos(math.radians(angle - 120)) + 128
        blue = 256 * math.cos(math.radians(angle - 240)) + 128
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

        self._colour = (red, green, blue)


class Image:
    def __init__(self, window: pygame.Surface, source: Path, x: int, y: int, scale: float = 1.0) -> None:
        """
        The function initializes an object with attributes for a window, image source, position, velocity, and scale.

        :param window: pygame Surface object on which the image will be displayed
        :type window: pygame.Surface
        :param source: pathlib Path that represents the file path of the image file that you want to display on the window
        :type source: Path
        :param x: the x-coordinate of the object's position on the window
        :type x: int
        :param y: The parameter `y` represents the y-coordinate of the object's position on the window
        :type y: int
        :param scale: Used to determine the size of the image when it is displayed on the window. It is a floating-point value that represents the scaling factor
        :type scale: float
        """
        self._source = source
        self._x = x
        self._y = y

        self._scale = scale
        self._window = window

    def draw(self) -> None:
        """
        The `draw` function loads an image, scales it based on a given scale factor, and then blits it onto a window at a
        specified position.
        """
        img = pygame.image.load(self._source)
        img = pygame.transform.scale(img, (img.get_width() * self._scale, img.get_height() * self._scale))
        self._window.blit(img, (self._x, self._y))
