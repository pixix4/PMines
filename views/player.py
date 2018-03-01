import curses
from typing import Optional, List, Set

import views.utils
from game import Field, Game, FieldState
from views.pause import Pause
from views.view import View


class Player(View):

    def __init__(self, screen, top, bottom):
        super(Player, self).__init__(screen, top, bottom)
        h, w = views.utils.get_size_from_screen(top)

        self._position = (w // 2, h // 2)

        self._game = Game(w, h)

    def render_point(self, p: Field) -> None:
        sel = curses.A_NORMAL
        if p == self._position and self._game.running:
            sel = curses.A_REVERSE
        state = self._game.field_state(p)
        x, y = p
        x = x * 2 + 1
        if state == FieldState.DEFAULT:
            self._top.addstr(y, x, '*', sel)
        elif state == FieldState.FLAG or state == FieldState.FLAG_RIGHT:
            self._top.addstr(y, x, '?', sel)
        elif state == FieldState.FLAG_HINT:
            self._top.addstr(y, x, '?', curses.color_pair(8) | sel)
        elif state == FieldState.OPEN:
            count = self._game.count_mines(p)
            if count == 0:
                self._top.addstr(y, x, ' ', sel)
            else:
                self._top.addstr(y, x, str(count), curses.color_pair(count) | sel)
        elif state == FieldState.MINE:
            self._top.addstr(y, x, 'X', curses.color_pair(9) | sel)
        elif state == FieldState.FLAG_FALSE:
            self._top.addstr(y, x, '!', curses.color_pair(9) | sel)

    def get_listen_window(self):
        return self._screen

    def draw(self, refresh: List[Field] = None):
        if refresh is None:
            for x in range(0, self._game.width):
                for y in range(0, self._game.height):
                    self.render_point((x, y))
        else:
            for p in refresh:
                self.render_point(p)

        self.clean_bottom()
        if self._game.running:
            self._bottom.addstr(0, 1, "live", curses.color_pair(8))
            self._bottom.addstr(1, 1, str(self._game.mines_left) + " mines remaining",
                                curses.color_pair(8))
        else:
            if self._game.won:
                self._bottom.addstr(0, 1, "won", curses.color_pair(2))
                self._bottom.addstr(1, 1,
                                    "Time: {} ({} place)".format(views.utils.format_time(self._game.duration),
                                                                 views.utils.ordinal(1)),
                                    curses.color_pair(2))
            else:
                self._bottom.addstr(0, 1, "lost", curses.color_pair(9))
                self._bottom.addstr(1, 1, str(self._game.mines_left) + " mines remaining",
                                    curses.color_pair(8))

    def pause(self):
        self._game.pause()

        pause = Pause(self._screen, self._top, self._bottom, self._game)
        pause.start()

        self._game.unpause()

    def action_on_running(self, key: chr) -> Optional[Set[Field]]:
        if key in [ord(' '), 10]:
            return self._game.click_field(self._position)

        refresh = set()
        x, y = self._position

        if key in [ord('f'), ord('F')]:
            self._game.flag_field(self._position)
        elif key in [curses.KEY_UP, ord('w'), ord('k')]:
            y -= 1
            if y < 0:
                y = 0
        elif key in [curses.KEY_LEFT, ord('a'), ord('h')]:
            x -= 1
            if x < 0:
                x = 0
        elif key in [curses.KEY_RIGHT, ord('d'), ord('l')]:
            x += 1
            if x >= self._game.width:
                x = self._game.width - 1
        elif key in [curses.KEY_DOWN, ord('s'), ord('j')]:
            y += 1
            if y >= self._game.height:
                y = self._game.height - 1
        elif key in [ord('p'), ord('P'), 27]:
            self.pause()
            self.clean()
            return None

        self._position = (x, y)
        refresh.add(self._position)
        return refresh

    def action_on_finished(self, key: chr) -> None:
        if key not in [curses.KEY_UP, ord('w'), ord('k'), curses.KEY_LEFT, ord('a'), ord('h'), curses.KEY_RIGHT, ord('d'), ord('l'), curses.KEY_DOWN, ord('s'), ord('j')]:
            self._active = False

    def on_action(self, key: chr) -> Optional[List[Field]]:
        if self._game.running:
            refresh = set()
            refresh.add(self._position)

            h = self.action_on_running(key)

            if h is None:
                return None
            else:
                refresh.update(h)
                return list(set(refresh))
        else:
            self.action_on_finished(key)
            return None
