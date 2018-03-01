import curses
from typing import List, Optional

from game import Field
from game import calc_mine_count
from scoreboard import Scoreboard, Scorelist
from views.utils import get_size_from_screen, format_time, draw_border
from views.view import View


def slice_string(string, length):
    if len(string) > length:
        string = string[:length - 3] + '...'
    return string


class Score(View):

    def __init__(self, screen, top, bottom):
        super(Score, self).__init__(screen, top, bottom)

        height, width = get_size_from_screen(self._top)
        self._size: int = calc_mine_count(width, height)
        self.score_number: int = self._size

        self._scroll_pos: int = 0
        self._hl: int = -1
        self._list: Scorelist = []
        self._height: int = 0
        self._editing_name: str = None
        self._editing_time: int = None

        self._window = None

    def get_all_scores(self) -> List[int]:
        lis = Scoreboard.get_all_scores()
        if self._size not in lis:
            lis.append(self._size)
            lis.sort()
        return lis

    def can_increase_index(self) -> bool:
        return max(self.get_all_scores()) > self.score_number

    def increase_index(self):
        lis = self.get_all_scores()
        if self.can_increase_index():
            next_val = max(lis)
            for elem in lis:
                if self.score_number < elem < next_val:
                    next_val = elem
            self._scroll_pos = 0
            self._hl = -1
            self.score_number = next_val
            self._list = Scoreboard.get_score(self.score_number)

    def can_decrease_index(self) -> bool:
        return min(self.get_all_scores()) < self.score_number

    def decrease_index(self):
        lis = self.get_all_scores()
        if self.can_decrease_index():
            next_val = min(lis)
            for elem in lis:
                if self.score_number > elem > next_val:
                    next_val = elem
            self._scroll_pos = 0
            self._hl = -1
            self.score_number = next_val
            self._list = Scoreboard.get_score(self.score_number)

    def press_down(self):
        if self._hl < min(self._height - 2, len(self._list) - 1):
            self._hl += 1
        else:
            self._scroll_pos += 1
            if self._scroll_pos > len(self._list) - self._height:
                self._scroll_pos = max(0, len(self._list) - self._height)
                self._hl += 1
                if self._hl >= min(len(self._list), self._height):
                    self._hl = 0
                    self._scroll_pos = 0

    def press_up(self):
        if self._hl > 1:
            self._hl -= 1
        else:
            self._scroll_pos -= 1
            if self._scroll_pos < 0:
                self._scroll_pos = 0
                self._hl -= 1
                if self._hl < 0:
                    self._hl = min(len(self._list) - 1, self._height - 1)
                    self._scroll_pos = max(0, len(self._list) - self._height)

    @property
    def title(self):
        return "Scoreboard - " + str(self.score_number)

    def clean(self):
        height, width = self._window.getmaxyx()
        for y in range(0, height):
            self._window.hline(y, 0, " ", width - 1)
        draw_border(self._window)

        super().clean()

    def refresh(self):
        super().refresh()
        self._window.refresh()

    def setup(self):
        max_height, max_width = self._screen.getmaxyx()
        width = min(41, max_width - 2)
        height = min(14, max_height - 0)

        self._window = curses.newwin(height, width, max_height // 2 - height // 2,
                                     (max_width // 2 - width // 2) // 2 * 2 + 1)
        self._window.keypad(True)
        self._height = height - 4

    def start_width_new_value(self, new_time: int):
        self.setup()

        pos, self._list = Scoreboard.get_score_with_new_value(self.score_number, new_time)
        self._editing_name = self._list[pos][1]
        self._editing_time = new_time

        for x in range(0, pos + 1):
            self.press_down()

        super().start()

    def start(self):
        self.setup()

        self._list = Scoreboard.get_score(self.score_number)

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

        number_width = len(str(len(self._list)))

        for x in range(0, self._height):
            if x + self._scroll_pos >= len(self._list):
                self._window.hline(x + 3, 1, " ", width - 2)
            else:
                selected = curses.A_NORMAL
                if x == self._hl:
                    selected = curses.A_REVERSE

                if x == self._hl and self._editing_name is not None:
                    time, _ = self._list[x + self._scroll_pos]
                    time = format_time(time)

                    name = slice_string(self._editing_name, width - number_width - len(time) - 6)
                    s = str(x + self._scroll_pos + 1).rjust(number_width, " ") + " " + name.ljust(
                        width - 4 - len(time) - number_width - 1) + time

                    self._window.addstr(x + 3, 2, s)
                    self._window.addstr(x + 3, number_width + len(name) + 3, " ", selected)
                else:
                    time, name = self._list[x + self._scroll_pos]
                    time = format_time(time)
                    name = slice_string(name, width - number_width - len(time) - 6)

                    s = str(x + self._scroll_pos + 1).rjust(number_width, " ") + " " + name.ljust(
                        width - 4 - len(time) - number_width - 1) + time
                    self._window.addstr(x + 3, 2, s, selected)

    def closable(self):
        return self._editing_name is None

    def on_action(self, key: chr) -> Optional[List[Field]]:
        if self._editing_name is None:
            if key in [curses.KEY_UP, ord('w'), ord('k')]:
                self.press_up()
            elif key in [curses.KEY_LEFT, ord('a'), ord('h')]:
                self.decrease_index()
            elif key in [curses.KEY_RIGHT, ord('d'), ord('l')]:
                self.increase_index()
            elif key in [curses.KEY_DOWN, ord('s'), ord('j')]:
                self.press_down()
            elif key in [10, 27, ord(' ')]:
                self._active = False
        else:
            if key in [curses.KEY_BACKSPACE]:
                self._editing_name = self._editing_name[:-1]
            elif key in [10]:
                Scoreboard.add_score(self.score_number, self._editing_time, self._editing_name)
                self._list = Scoreboard.get_score(self.score_number)
                self._editing_name = None
                self._editing_time = None
            elif key in [27]:
                self._list = Scoreboard.get_score(self.score_number)
                self._editing_name = None
                self._editing_time = None
            elif key < 256 and chr(key).isprintable():
                self._editing_name += chr(key)
        return None
