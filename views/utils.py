from typing import Tuple


def get_size_from_screen(screen) -> Tuple[int, int]:
    height, width = screen.getmaxyx()
    if width % 2 == 0:
        width -= 1
    width = width // 2
    return height, width


def game_pos_to_screen_pos(pos: Tuple[int, int]) -> Tuple[int, int]:
    return pos[0], pos[1] * 2 + 1


def render_background(screen) -> None:
    height, width = get_size_from_screen(screen)

    for y in range(0, height):
        screen.hline(y, 0, " ", width - 1)
        for x in range(0, width):
            new_y, new_x = game_pos_to_screen_pos((y, x))
            screen.addstr(new_y, new_x, "*")


def draw_border(screen) -> None:
    height, width = screen.getmaxyx()
    for x in range(1, width - 1):
        screen.addstr(0, x, "═")
        screen.addstr(height - 1, x, "═")
    for y in range(1, height - 1):
        screen.addstr(y, 0, "║")
        screen.addstr(y, width - 1, "║")
    screen.addstr(0, 0, "╔")
    screen.addstr(0, width - 1, "╗")
    screen.addstr(height - 1, 0, "╚")
    screen.addstr(height - 1, width - 2, "╝")
    screen.insstr(height - 1, width - 2, "═")


def format_time(time: int) -> str:
    time = time // 10
    ms = time % 100
    s = time // 100
    if s < 60:
        return "%d'%02d" % (s, ms)
    else:
        m = s // 60
        s = s % 60
        return "%d:%02d'%02d" % (m, s, ms)


def ordinal(number: int) -> str:
    return "%d%s" % (number, "tsnrhtdd"[((number // 10) % 10 != 1) * (number % 10 < 4) * number % 10::4])
