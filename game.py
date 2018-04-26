import itertools
import time
from enum import Enum
from random import sample
from typing import Optional
from typing import Set, Tuple, List

Field = Tuple[int, int]


def current_time():
    return int(round(time.time() * 1000))


class FieldState(Enum):
    DEFAULT = 0
    FLAG = 1
    OPEN = 2
    MINE = 3
    FLAG_RIGHT = 4
    FLAG_FALSE = 5
    FLAG_HINT = 6


class Direction(Enum):
    TOP = 0
    TOP_RIGHT = 1
    RIGHT = 2
    BOTTOM_RIGHT = 3
    BOTTOM = 4
    BOTTOM_LEFT = 5
    LEFT = 6
    TOP_LEFT = 7


def calc_mine_count(width: int, height: int) -> int:
    return int(width * height // 6.25)


class Game:

    def __init__(self, width: int, height: int, count: int = 0):
        if width * height - 8 < count:
            raise ValueError("Bomb count is bigger then allowed!")

        self._width: int = width
        self._height: int = height

        if count == 0:
            count = calc_mine_count(width, height)

        self._count: int = count

        self._mines: Set[Field] = None
        self._flags: Set[Field] = set()
        self._opened: Set[Field] = set()
        self._helped: Set[Field] = set()
        self._running: bool = True
        self._won: bool = None
        self._last_time = current_time()
        self._duration = 0
        self._pause = False

    def pause(self):
        if self.started and self._running and not self._pause:
            self._pause = True
            self._duration += current_time() - self._last_time

    def unpause(self):
        if self.started and self._running and self._pause:
            self._pause = False
            self._last_time = current_time()

    @property
    def paused(self):
        return self._pause

    @property
    def duration(self):
        if self.started and self._running and not self._pause:
            t = current_time()
            self._duration += t - self._last_time
            self._last_time = t
        return self._duration

    def translate_point(self, p: Field, d: Direction) -> Optional[Tuple[int, int]]:
        x, y = p
        if d == Direction.TOP:
            y -= 1
        elif d == Direction.TOP_RIGHT:
            x += 1
            y -= 1
        elif d == Direction.RIGHT:
            x += 1
        elif d == Direction.BOTTOM_RIGHT:
            x += 1
            y += 1
        elif d == Direction.BOTTOM:
            y += 1
        elif d == Direction.BOTTOM_LEFT:
            x -= 1
            y += 1
        elif d == Direction.LEFT:
            x -= 1
        elif d == Direction.TOP_LEFT:
            x -= 1
            y -= 1

        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return None
        return x, y

    def point_to_int(self, p: Field) -> int:
        x, y = p
        return x + self._width * y

    def int_to_point(self, i: int) -> Field:
        return i % self._width, i // self._width

    def init_mines(self, p: Field) -> None:
        lock: Set[int] = set()
        lock.add(self.point_to_int(p))
        for d in Direction:
            h = self.translate_point(p, d)
            if h is not None:
                lock.add(self.point_to_int(h))
        allowed: Set[int] = set(range(0, self._width * self._height)) - lock

        self._mines = set([self.int_to_point(x) for x in sample(list(allowed), self._count)])

    def hint(self):
        if self.running:
            copy = self.copy()
            changed = solve(copy)

            if changed:
                self.lose()
                return None
            else:
                for p in self._opened:
                    missing = self.count_mines(p) - self.count_flags(p)
                    if missing > 0:
                        for d in Direction:
                            h = self.translate_point(p, d)
                            if h in self._mines and h not in self._flags:
                                self.flag_field(h, True)
                                self._helped.add(h)
                                return h
        return None

    def _open(self, p: Field) -> Set[Field]:
        changed = set()

        if p in self._opened:
            return changed

        changed.add(p)
        self._opened.add(p)

        if self.count_mines(p) == 0:
            for d in Direction:
                h = self.translate_point(p, d)
                if h is not None:
                    changed.update(self._open(h))

        return changed

    def check_finished(self):
        if len(self._opened) + len(self._mines) == self._width * self._height:
            self._running = False
            self._won = True
            self._duration += current_time() - self._last_time

    def lose(self):
        self._running = False
        self._won = False
        self._duration += current_time() - self._last_time

    def click_field(self, p: Field) -> Optional[Set[Field]]:
        if not self.started:
            self.init_mines(p)
            self._last_time = current_time()
            self._duration = 0

        if p in self._flags:
            return set()

        if p in self._opened:
            mine_count: int = 0
            flag_count: int = 0
            for d in Direction:
                h = self.translate_point(p, d)
                if h in self._mines:
                    mine_count += 1
                if h in self._flags:
                    flag_count += 1

            if mine_count == flag_count:
                s = set()
                for d in Direction:
                    h = self.translate_point(p, d)
                    if h is not None and h not in self._flags:
                        if h in self._mines:
                            self.lose()
                            return None
                        else:
                            s.update(self._open(h))
                self.check_finished()
                return s

        if p in self._mines:
            self.lose()
            return None

        h = self._open(p)
        self.check_finished()
        return h

    def flag_field(self, p: Field, force: bool = None) -> None:
        if self.started and p not in self._opened:
            if force is None:
                if p in self._flags:
                    self._flags.remove(p)
                else:
                    self._flags.add(p)
                    self.check_finished()
            else:
                if force:
                    self._flags.add(p)
                    self.check_finished()
                else:
                    self._flags.remove(p)

    @property
    def mines_left(self) -> int:
        return max(0, self._count - len(self._flags))

    @property
    def running(self) -> bool:
        return self._running

    @property
    def won(self) -> bool:
        return self._won

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def count(self) -> int:
        return self._count

    @property
    def started(self) -> bool:
        return self._mines is not None

    @property
    def opened_fields(self) -> Set[Field]:
        return set(self._opened)

    def count_mines(self, p: Field) -> int:
        if p not in self._opened:
            raise ValueError("Count this field is not valid")

        c: int = 0
        for d in Direction:
            if self.translate_point(p, d) in self._mines:
                c += 1
        return c

    def count_flags(self, p: Field) -> int:
        c: int = 0
        for d in Direction:
            if self.translate_point(p, d) in self._flags:
                c += 1
        return c

    def field_state(self, p: Field) -> FieldState:
        if p in self._opened:
            return FieldState.OPEN

        if self._running:
            if p in self._flags:
                if p in self._helped:
                    return FieldState.FLAG_HINT
                return FieldState.FLAG
            return FieldState.DEFAULT
        else:
            if p in self._mines:
                if p in self._flags:
                    if p in self._helped:
                        return FieldState.FLAG_HINT
                    return FieldState.FLAG_RIGHT
                return FieldState.MINE
            else:
                if p in self._flags:
                    return FieldState.FLAG_FALSE
                return FieldState.DEFAULT

    def copy(self) -> 'Game':
        g = Game(self.width, self.height, self.count)
        g._mines = self._mines.copy()
        g._opened = self._opened.copy()
        g._flags = self._flags.copy()
        g._running = self._running
        g._won = self._won
        return g

    def print(self):
        h = "─"
        for y in range(0, self._height):
            h += "──"

        print("╭" + h + "╮")

        for x in range(0, self._width):
            line = "│ "
            for y in range(0, self._height):
                state = self.field_state((x, y))
                if state == FieldState.DEFAULT:
                    line += "*"
                elif state == FieldState.FLAG or state == FieldState.FLAG_FALSE \
                        or state == FieldState.FLAG_RIGHT or state == FieldState.FLAG_HINT:
                    line += "?"
                elif state == FieldState.MINE:
                    line += "X"
                else:
                    count = self.count_mines((x, y))
                    if count == 0:
                        line += " "
                    else:
                        line += str(count)
                line += " "
            print(line + "│")

        print("╰" + h + "╯")


def solve(game: Game) -> bool:
    changed = False

    if not game.started:
        game.click_field((0, 0))

    while _solve_game(game):
        changed = True

    return changed


def _solve_bands(game: Game, b1: Tuple[int, Set[Field]], b2: Tuple[int, Set[Field]]) -> bool:
    b1_missing, b1_fields = b1
    b2_missing, b2_fields = b2

    if len(b1_fields & b2_fields) == 0:
        return False

    changed = False

    if b2_fields <= b1_fields:
        h = b2_fields
        b2_fields = b1_fields
        b1_fields = h

        h = b2_missing
        b2_missing = b1_missing
        b1_missing = h

    if b1_fields <= b2_fields:
        outer = b2_fields - b1_fields
        if (b2_missing - b1_missing) == 0:
            for h in outer:
                changed = True
                game.click_field(h)
        elif len(outer) == (b2_missing - b1_missing):
            for h in outer:
                changed = True
                game.flag_field(h, True)

    return changed


def _solve_section(game: Game, section: Set[Field]) -> bool:
    bands: List[Tuple[int, Set[Field]]] = []
    changed = False

    for p in section:
        missing = game.count_mines(p) - game.count_flags(p)

        band = set()
        for d in Direction:
            h = game.translate_point(p, d)
            if h is not None and game.field_state(h) == FieldState.DEFAULT:
                band.add(h)

        if missing > 0:
            if len(band) == missing:
                for h in band:
                    game.flag_field(h, True)
                    changed = True
            else:
                bands.append((missing, band))
        else:
            for h in band:
                game.click_field(h)
                changed = True

    for b1, b2 in itertools.combinations(bands, 2):
        if _solve_bands(game, b1, b2):
            changed = True

    return changed


def _solve_game(game: Game) -> bool:
    opened = set([x for x in game.opened_fields if game.count_mines(x) > 0])

    def point_to_section(sec: Set[Field], p: Field):
        todo = [p]
        while len(todo) > 0:
            p = todo.pop()
            sec.add(p)
            opened.remove(p)
            for d in Direction:
                h = game.translate_point(p, d)
                if h is not None and h in opened and h not in todo:
                    todo.append(h)

    changed = False

    while len(opened) > 0:
        section = set()
        point_to_section(section, sample(opened, 1)[0])

        if _solve_section(game, section):
            changed = True

    return changed


if __name__ == "__main__":
    g = Game(25, 25)
    g.click_field((g.height // 2, g.width // 2))
    solve(g)
    g.print()

    print("Won: {} | Mines: {}/{}".format(g.won, g.count - g.mines_left, g.count))
