import curses
import sys
from abc import abstractmethod
from typing import List, Tuple, Callable, Optional

from game import Field
from views.utils import draw_border
from views.view import View


class Dialog(View):

    def __init__(self, screen, top, bottom):
        super(Dialog, self).__init__(screen, top, bottom)

        self.title = ""
        self._entries: List[Tuple[str, Callable[[], bool]]] = []
        self._window = None
        self._active_entry = None

        self.init_menu()

    @abstractmethod
    def init_menu(self):
        pass

    def add_entry(self, name: str, callback: Callable[[], bool]) -> None:
        self._entries.append((name, callback))

    def clean(self):
        height, width = self._window.getmaxyx()
        for y in range(0, height):
            self._window.hline(y, 0, " ", width - 1)
        draw_border(self._window)

        super().clean()

    def refresh(self):
        super().refresh()
        self._window.refresh()

    def start(self):
        width = len(self.title)
        for line in self._entries:
            if len(line[0]) > width:
                width = len(line[0])
        width = (width + 12) // 2 * 2 + 1
        height = len(self._entries) + 6

        max_height, max_width = self._screen.getmaxyx()
        height = min(height, max_height)

        print("---------------", file=sys.stderr, flush=True)
        print(height, file=sys.stderr, flush=True)
        print(width, file=sys.stderr, flush=True)
        print(max_height // 2 - height // 2, file=sys.stderr, flush=True)
        print((max_width // 2 - width // 2) // 2 * 2 + 1, file=sys.stderr, flush=True)

        self._window = curses.newwin(height, width, max_height // 2 - height // 2,
                                     (max_width // 2 - width // 2) // 2 * 2 + 1)
        self._window.keypad(True)
        super().start()

    def get_listen_window(self):
        return self._window

    def draw(self, refresh: List[Field] = None):
        height, width = self._window.getmaxyx()
        draw_border(self._window)
        self._window.addstr(1, 1, self.title.center(width - 2, " "))

        for x in range(1, width - 1):
            self._window.addstr(2, x, "═")
        self._window.addstr(2, 0, "╠")
        self._window.addstr(2, width - 1, "╣")

        pos = 0
        for i, line in enumerate(self._entries):
            if pos > 0 and height < 6 and self._active_entry is not None:
                continue
            if pos + 6 >= height and i != self._active_entry and (pos != 0 or self._active_entry is not None):
                continue

            selected = curses.A_NORMAL
            if i == self._active_entry:
                selected = curses.A_REVERSE
            self._window.addstr(pos + 4, 2, line[0].center(width - 4, " "), selected)
            pos += 1

        self.clean_bottom()
        _, footer_width = self._bottom.getmaxyx()
        footer = self.draw_footer()
        self._bottom.addstr(0, 1, footer[0])
        self._bottom.addstr(0, footer_width - 1 - len(footer[1]), footer[1])
        self._bottom.addstr(1, 1, footer[2])
        self._bottom.addstr(1, footer_width - 1 - len(footer[3]), footer[3])

    def draw_footer(self) -> Tuple[str, str, str, str]:
        return "", "", "", ""

    def on_action(self, key: chr) -> Optional[List[Field]]:
        if key in [curses.KEY_UP]:
            if self._active_entry is None or self._active_entry == 0:
                self._active_entry = len(self._entries) - 1
            else:
                self._active_entry -= 1
        elif key in [curses.KEY_DOWN]:
            if self._active_entry is None or self._active_entry == len(self._entries) - 1:
                self._active_entry = 0
            else:
                self._active_entry += 1
        elif key in [27]:
            self._active = False
        elif key in [10, ord(' ')]:
            if self._active_entry is None:
                self._active_entry = 0
            self._active = not self._entries[self._active_entry][1]()
            self.clean()

        return None
