
from title_gui import GuiManager
from main import GameManager

if __name__ == '__main__':
    gui_manager = GuiManager()
    gui_manager.gui_loop()

    while True:
        # waiting for space to be pressed on the title screen before game starts
        while not gui_manager.start_game:
            pass

        game_manager = GameManager()
        score = game_manager.game_loop()

        gui_manager = GuiManager(score)
        gui_manager.gui_loop()
