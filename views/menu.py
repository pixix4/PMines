from sys import exit

from game import calc_mine_count
from views.dialog import Dialog
from views.player import Player
from views.utils import get_size_from_screen
from views.score import Score


class Menu(Dialog):

    def init_menu(self):
        self.title = "PMines"

        self.add_entry("Start game", self.start_game)
        self.add_entry("Scoreboard", self.score)
        self.add_entry("Settings", self.settings)
        self.add_entry("Quit", self.quit)

    def draw_footer(self):
        height, width = get_size_from_screen(self._top)
        return "", "", "Difficulty: " + str(calc_mine_count(width, height)), "1.0.0"

    def start_game(self) -> bool:
        player = Player(self._screen, self._top, self._bottom)
        player.start()
        return False

    def score(self) -> bool:
        score = Score(self._screen, self._top, self._bottom)
        score.start()
        return False

    @staticmethod
    def settings() -> bool:
        pass

    @staticmethod
    def quit() -> bool:
        exit()
        return True
