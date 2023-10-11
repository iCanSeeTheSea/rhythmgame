
from title_gui import GuiManager
from main_new import GameManager

if __name__ == '__main__':
    gui_manager = GuiManager()
    gui_manager.gui_loop()
    while not gui_manager.start_game:
        pass
    game_manager = GameManager()
    game_manager.game_loop()
