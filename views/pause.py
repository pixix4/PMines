from sys import exit

from views.dialog import Dialog
from game import Game
from views.score import Score


class Pause(Dialog):

    def __init__(self, screen, top, bottom, game:Game):
        super(Pause, self).__init__(screen, top, bottom)

        self._game = game

    def init_menu(self):
        self.title = "Pause"

        self.add_entry("Resume", self.resume)
        self.add_entry("Hint", self.hint)
        self.add_entry("Give up", self.give_up)
        self.add_entry("Scoreboard", self.score)
        self.add_entry("Quit", self.quit)

    @staticmethod
    def resume() -> bool:
        return True

    def score(self) -> bool:
        score = Score(self._screen, self._top, self._bottom)
        score.start()
        return False

    def hint(self) -> bool:
        self._game.hint()
        return True

    @staticmethod
    def give_up(self) -> bool:
        pass

    @staticmethod
    def quit() -> bool:
        exit()
        return True
