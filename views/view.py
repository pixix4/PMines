import curses
from abc import ABC, abstractmethod
from sys import exit
from typing import Optional, List

import views.utils as utils
from game import Field


class View(ABC):

    def __init__(self, screen, top, bottom):
        self._screen = screen
        self._top = top
        self._bottom = bottom
        self._active = True

    @abstractmethod
    def get_listen_window(self):
        pass

    def closable(self):
        return True

    def start(self):
        self.clean()
        self.draw()

        while self._active:
            self.refresh()
            key = self.get_listen_window().getch()
            draw = None
            if self.closable() and key in [ord("q"), ord("Q")]:
                exit()
            elif key == curses.KEY_EXIT:
                return
            else:
                draw = self.on_action(key)

            self.draw(draw)

    @abstractmethod
    def draw(self, refresh: List[Field] = None):
        pass

    @abstractmethod
    def on_action(self, key: chr) -> Optional[List[Field]]:
        pass

    def clean_top(self):
        utils.render_background(self._top)

    def clean_bottom(self):
        height, width = self._bottom.getmaxyx()
        for y in range(0, height):
            self._bottom.hline(y, 0, " ", width - 1)

    def clean(self):
        self.clean_top()
        self.clean_bottom()
        height, width = self._screen.getmaxyx()
        self._screen.hline(height - 3, 0, " ", width - 1)

    def refresh(self):
        self._screen.refresh()
        self._top.refresh()
        self._bottom.refresh()
