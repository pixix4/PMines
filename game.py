from enum import Enum
from random import sample
from typing import Set, Tuple, Optional

Point = Tuple[int, int]


class FieldState(Enum):
    DEFAULT = 0
    FLAG = 1
    OPEN = 2
    MINE = 3
    FLAG_RIGHT = 4
    FLAG_FALSE = 5


class Direction(Enum):
    TOP = 0
    TOP_RIGHT = 1
    RIGHT = 2
    BOTTOM_RIGHT = 3
    BOTTOM = 4
    BOTTOM_LEFT = 5
    LEFT = 6
    TOP_LEFT = 7


class Game:

    def __init__(self, width: int, height: int, count: int = 0):
        if width * height - 8 < count:
            raise ValueError("Bomb count is bigger then allowed!")

        self._width: int = width
        self._height: int = height

        if count == 0:
            count = int(width * height // 6.25)

        self._count: int = count

        self._mines: Set[Point] = None
        self._flags: Set[Point] = set()
        self._opened: Set[Point] = set()
        self._running: bool = True
        self._won: bool = None

    def translate_point(self, p: Point, d: Direction) -> Optional[Tuple[int, int]]:
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

    def point_to_int(self, p: Point) -> int:
        x, y = p
        return x + self._width * y

    def int_to_point(self, i: int) -> Point:
        return i % self._width, i // self._width

    def init_mines(self, p: Point) -> None:
        lock: Set[int] = set()
        lock.add(self.point_to_int(p))
        for d in Direction:
            h = self.translate_point(p, d)
            if h is not None:
                lock.add(self.point_to_int(h))
        allowed: Set[int] = set(range(0, self._width * self._height)) - lock

        self._mines = set()
        for i in sample(list(allowed), self._count):
            self._mines.add(self.int_to_point(i))

    def _open(self, p: Point) -> Set[Point]:
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
        if (len(self._mines - self._flags) == 0) and len(self._opened) + len(self._mines) == self._width * self._height:
            self._running = False
            self._won = True

    def lose(self):
        self._running = False
        self._won = False

    def click_field(self, p: Point) -> Optional[Set[Point]]:
        if self._mines is None:
            self.init_mines(p)

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

    def flag_field(self, p: Point) -> None:
        if p not in self._opened:
            if p in self._flags:
                self._flags.remove(p)
            else:
                self._flags.add(p)
                self.check_finished()

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

    def count_mines(self, p: Point) -> int:
        if p not in self._opened:
            raise ValueError("Count this field is not valid")

        c: int = 0
        for d in Direction:
            if self.translate_point(p, d) in self._mines:
                c += 1
        return c

    def field_state(self, p: Point) -> FieldState:
        if p in self._opened:
            return FieldState.OPEN

        if self._running:
            if p in self._flags:
                return FieldState.FLAG
            return FieldState.DEFAULT
        else:
            if p in self._mines:
                if p in self._flags:
                    return FieldState.FLAG_RIGHT
                return FieldState.MINE
            else:
                if p in self._flags:
                    return FieldState.FLAG_FALSE
                return FieldState.DEFAULT
