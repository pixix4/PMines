#!/bin/python

import curses
import string
from operator import itemgetter
from os import path, environ
from typing import Set, List, Tuple, Optional

from game import Game, Field, FieldState
from scoreboard import Scoreboard
from views.menu import Menu


def init_color():
    curses.init_pair(1, curses.COLOR_BLUE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_YELLOW, -1)
    curses.init_pair(7, curses.COLOR_YELLOW, -1)
    curses.init_pair(8, curses.COLOR_YELLOW, -1)
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_YELLOW)


def _score_file_name(game: Game = None) -> str:
    if game is None:
        game = generate_game()
    return ".pmines_{}_{}_{}.score".format(game.width, game.height, game.count)


def get_scores_for_game(game: Game) -> List[Tuple[int, str]]:
    scores = []
    if path.isfile(_score_file_name(game)):
        with open(_score_file_name(game), "r") as file:
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    li = line.split(" ", 1)
                    time = li[0]
                    name = ""
                    if len(li) == 2:
                        name = li[1]
                    scores.append((int(time), name))

    scores = sort_scores(scores)
    return scores


def sort_scores(scores: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    return sorted(scores, key=itemgetter(0))


def save_scores_for_game(game: Game, scores: List[Tuple[int, str]]):
    scores = sort_scores(scores)
    with open(_score_file_name(game), "w+") as file:
        file.write('\n'.join('{} {}'.format(x[0], x[1]) for x in scores))


def draw_border(scr, width, height):
    for x in range(1, width - 1):
        scr.addstr(0, x, "═")
        scr.addstr(height - 1, x, "═")
    for y in range(1, height - 1):
        scr.addstr(y, 0, "║")
        scr.addstr(y, width - 1, "║")
    scr.addstr(0, 0, "╔")
    scr.addstr(0, width - 1, "╗")
    scr.addstr(height - 1, 0, "╚")
    scr.addstr(height - 1, width - 2, "╝")
    scr.insstr(height - 1, width - 2, "═")


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


def get_place(game: Game) -> int:
    scores = get_scores_for_game(game)
    new_value = (game.duration, "")
    scores.append(new_value)
    scores = sort_scores(scores)
    return scores.index(new_value) + 1


def show_score(game: Game = None, time: int = None) -> bool:
    scores = get_scores_for_game(game)
    width = min(33, curses.COLS - 2)
    height = min(13, curses.LINES)
    if time is not None and len(scores) >= height - 4 and scores[height - 5][0] < time:
        return False

    curses.curs_set(0)
    score_scr = curses.newwin(height, width, (curses.LINES - 1) // 2 - height // 2,
                              (curses.COLS // 2 - width // 2) // 2 * 2 + 1)
    draw_border(score_scr, width, height)
    # score_scr.border()

    for x in range(1, width - 1):
        score_scr.addstr(2, x, "═")
    score_scr.addstr(2, 0, "╠")
    score_scr.addstr(2, width - 1, "╣")

    hs = "Highscore"
    score_scr.addstr(1, width // 2 - (len(hs) - 1) // 2, hs)

    new_position = None
    new_name = ""
    if time is not None:
        new_value = (time, "")
        scores.append(new_value)
        scores = sort_scores(scores)
        new_position = scores.index(new_value)
        curses.curs_set(1)

    for place in range(1, height - 3):
        score_scr.addstr(place + 2, 2, str(place) + ".")

        if len(scores) >= place:
            score_scr.addstr(place + 2, 5, scores[place - 1][1])
            t = format_time(scores[place - 1][0])
            score_scr.addstr(place + 2, width - 2 - len(t), t)

    score_scr.refresh()

    if new_position is not None:
        score_scr.addstr(3 + new_position, 5, new_name)
        score_scr.move(3 + new_position, 5 + len(new_name))

    show = True
    block_next = False
    while show:
        c = score_scr.getch()
        if block_next:
            block_next = False
            continue

        if new_position is None:
            if c == ord('p') or c == ord('P') or c == ord('i') or c == ord('I') or c == 27 or c == ord(' '):
                show = False
            elif c == ord('q'):
                return True
        else:
            if c == 10:
                if len(new_name) > 0:
                    scores[new_position] = (time, new_name)
                    save_scores_for_game(game, scores)
                else:
                    scores.pop(new_position)

                new_position = None
                curses.curs_set(0)
                continue
            elif c == 27:
                score_scr.hline(3 + new_position, 5, " ", width - len(format_time(time)) - 8)
                scores.pop(new_position)
                new_position = None
                curses.curs_set(0)
                continue
            elif c == 127:
                new_name = new_name[:-1]
            elif c == 91:
                block_next = True
            elif chr(c) in string.printable:
                new_name += chr(c)

            new_name = new_name[0:width - len(format_time(time)) - 8]
            if time is not None:
                score_scr.hline(3 + new_position, 5, " ", width - len(format_time(time)) - 8)
            score_scr.addstr(3 + new_position, 5, new_name)
            score_scr.move(3 + new_position, 5 + len(new_name))

    del score_scr
    curses.curs_set(1)
    return False


def generate_game() -> Game:
    return Game(curses.COLS // 2, curses.LINES - 3)


def render_point(stdscr, game: Game, p: Field) -> None:
    state = game.field_state(p)
    x, y = p
    x = x * 2 + 1
    if state == FieldState.DEFAULT or game.paused:
        stdscr.addstr(y, x, '*')
    elif state == FieldState.FLAG:
        stdscr.addstr(y, x, '?')
    elif state == FieldState.FLAG_HINT:
        stdscr.addstr(y, x, '?', curses.color_pair(8))
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


def render_all(stdscr, game: Game):
    if game is None:
        return

    for x in range(0, game.width):
        for y in range(0, game.height):
            render_point(stdscr, game, (x, y))


def ordinal(number: int) -> str:
    return "%d%s" % (number, "tsnrhtdd"[((number // 10) % 10 != 1) * (number % 10 < 4) * number % 10::4])


def render_foot(stdscr, game: Game):
    if game is None:
        return

    y, x = stdscr.getyx()

    stdscr.hline(game.height, 0, " ", curses.COLS - 1)
    stdscr.hline(game.height + 1, 0, " ", curses.COLS - 1)
    stdscr.hline(game.height + 2, 0, " ", curses.COLS - 1)

    if game.running:
        stdscr.addstr(game.height + 1, 1, "live", curses.color_pair(8))
        stdscr.addstr(game.height + 2, 1, str(game.mines_left) + " mines remaining", curses.color_pair(8))
    else:
        if game.won:
            stdscr.addstr(game.height + 1, 1, "won", curses.color_pair(2))
            stdscr.addstr(game.height + 2, 1,
                          "Time: {} ({} place)".format(format_time(game.duration), ordinal(get_place(game))),
                          curses.color_pair(2))
        else:
            stdscr.addstr(game.height + 1, 1, "lost", curses.color_pair(9))
            stdscr.addstr(game.height + 2, 1, str(game.mines_left) + " mines remaining", curses.color_pair(8))

    stdscr.move(y, x)


def game_round(stdscr) -> Optional[Game]:
    game = generate_game()

    render_all(stdscr, game)
    render_foot(stdscr, game)
    h = game.width
    if h % 2 == 0:
        h -= 1
    stdscr.move(game.height // 2, h)

    while game.running:
        y, x = stdscr.getyx()

        c = stdscr.getch()
        p = (x - 1) // 2, y
        refresh: Set[Field] = set()
        if c == ord(' '):
            h = game.click_field(p)
            if h is None:
                break
            refresh.update(h)
            render_all(stdscr, game)
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
            return None
        elif c == ord('R') and game.started:
            game.lose()
        elif c == ord('H'):
            if game.started:
                h = game.hint()
                if h is None:
                    break
                refresh.add(h)
        elif c == ord('p') or c == ord('P') or c == ord('i') or c == ord('I'):
            game.pause()
            render_all(stdscr, game)
            stdscr.refresh()
            if show_score(game):
                return None
            game.unpause()
            render_all(stdscr, game)
            render_foot(stdscr, game)

        for p in refresh:
            render_point(stdscr, game, p)

        render_foot(stdscr, game)
        stdscr.move(y, x)

    render_foot(stdscr, game)
    render_all(stdscr, game)

    return game


def main(stdscr):
    curses.use_default_colors()
    stdscr.clear()
    init_color()

    wants_playing = True

    while wants_playing:
        curses.curs_set(1)
        game = game_round(stdscr)
        if game is None:
            wants_playing = False
        curses.curs_set(0)

        if wants_playing and game.won:
            c = stdscr.getch()
            if c == ord('q'):
                wants_playing = False
            elif c == ord('r') or c == ord('R'):
                continue

            if wants_playing and show_score(game, game.duration):
                wants_playing = False
            curses.curs_set(0)

        render_all(stdscr, game)
        render_foot(stdscr, game)

        while wants_playing:
            c = stdscr.getch()
            if c == ord('q'):
                wants_playing = False
            elif c == ord('r') or c == ord('R'):
                break
            elif c == ord('p') or c == ord('P') or c == ord('i') or c == ord('I'):
                if show_score(game):
                    wants_playing = False
                curses.curs_set(0)
                render_all(stdscr, game)
                render_foot(stdscr, game)


def startup(screen):
    height = curses.LINES
    width = curses.COLS

    curses.use_default_colors()
    screen.clear()
    curses.curs_set(False)
    init_color()

    top = curses.newwin(height - 3, width, 0, 0)
    bottom = curses.newwin(2, width, height - 2, 0)

    Scoreboard.load()

    menu = Menu(screen, top, bottom)
    menu.start()


if __name__ == "__main__":
    environ.setdefault('ESCDELAY', '25')
    curses.wrapper(startup)

