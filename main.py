#!/bin/python

import curses
from typing import Set

from game import Game, Field, FieldState


def init_color():
    curses.init_pair(1, curses.COLOR_BLUE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)
    curses.init_pair(7, curses.COLOR_YELLOW, -1)
    curses.init_pair(8, curses.COLOR_YELLOW, -1)
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_RED)


def game_round(stdscr) -> bool:
    game = Game(curses.COLS // 2, curses.LINES - 3)

    def render_point(p: Field) -> None:
        state = game.field_state(p)
        x, y = p
        x = x * 2 + 1
        if state == FieldState.DEFAULT:
            stdscr.addstr(y, x, '*')
        elif state == FieldState.FLAG:
            stdscr.addstr(y, x, '?')
        elif state == FieldState.OPEN:
            count = game.count_mines(p)
            if count == 0:
                stdscr.addstr(y, x, ' ')
            else:
                stdscr.addstr(y, x, str(count), curses.color_pair(count))
        elif state == FieldState.MINE:
            stdscr.addstr(y, x, 'X', curses.color_pair(9))
        elif state == FieldState.FLAG_FALSE:
            stdscr.addstr(y, x, '!', curses.color_pair(9))
        elif state == FieldState.FLAG_RIGHT:
            stdscr.addstr(y, x, '?')

    def render_all():
        for x in range(0, game.width):
            for y in range(0, game.height):
                render_point((x, y))

    render_all()
    h = game.width
    if h % 2 == 0:
        h -= 1
    stdscr.move(game.height // 2, h)

    while game.running:
        y, x = stdscr.getyx()
        stdscr.addstr(game.height + 1, 1, "live", curses.color_pair(8))
        stdscr.addstr(game.height + 2, 1, str(game.mines_left) + " mines remaining           ", curses.color_pair(8))
        stdscr.move(y, x)

        c = stdscr.getch()
        p = (x - 1) // 2, y
        refresh: Set[Field] = set()
        if c == ord(' '):
            h = game.click_field(p)
            if h is None:
                break
            refresh.update(h)
        elif c == ord('f') or c == ord('F'):
            game.flag_field(p)
            refresh.add(p)
        elif c == curses.KEY_UP or c == ord('w') or c == ord('k'):
            y -= 1
            if y < 0:
                y = 0
        elif c == curses.KEY_LEFT or c == ord('a') or c == ord('h'):
            x -= 2
            if x < 1:
                x = 1
        elif c == curses.KEY_RIGHT or c == ord('d') or c == ord('l'):
            x += 2
            if x >= game.width * 2:
                x = game.width * 2 - 1
        elif c == curses.KEY_DOWN or c == ord('s') or c == ord('j'):
            y += 1
            if y >= game.height:
                y = game.height - 1
        elif c == ord('q'):
            return False
        elif c == ord('R') and game.started:
            game.lose()
        elif c == ord('H'):
            if game.started:
                h = game.hint()
                if h is None:
                    break
                refresh.add(h)

        for p in refresh:
            render_point(p)

        stdscr.move(y, x)

    if game.won:
        stdscr.addstr(game.height + 1, 1, "won ", curses.color_pair(2))
    else:
        stdscr.addstr(game.height + 1, 1, "lost", curses.color_pair(9))
    stdscr.addstr(game.height + 2, 1, str(game.mines_left) + " mines remaining           ", curses.color_pair(8))

    render_all()
    return True


def main(stdscr):
    curses.use_default_colors()
    stdscr.clear()
    init_color()

    wants_playing = True

    while wants_playing:
        curses.curs_set(1)
        wants_playing = game_round(stdscr)
        curses.curs_set(0)

        while wants_playing:
            c = stdscr.getch()
            if c == ord('q'):
                wants_playing = False
            elif c == ord('r') or c == ord('R'):
                break


if __name__ == "__main__":
    curses.wrapper(main)
