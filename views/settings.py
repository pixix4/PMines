from sys import exit

from views.dialog import Dialog
from game import Game, Difficulty

class Settings(Dialog):

    def __init__(self, screen, top, bottom):
        super(Settings, self).__init__(screen, top, bottom)

    def init_menu(self):
        self.title = "Settings"

        self.add_entry("Easy", self.easy)
        self.add_entry("Normal", self.normal)
        self.add_entry("Hard", self.hard)

    def easy(self) -> bool:
        Game.difficulty = Difficulty.EASY
        return True

    def normal(self) -> bool:
        Game.difficulty = Difficulty.NORMAL
        return True

    def hard(self) -> bool:
        Game.difficulty = Difficulty.HARD
        return True
    
