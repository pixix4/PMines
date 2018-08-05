#!/bin/python

from operator import itemgetter
from os import path
from re import match
from typing import List, Tuple, Optional, Dict

Scorelist = List[Tuple[int, str]]


class Scoreboard:
    _filename = path.expanduser("~/.pmines.score")
    _list: Dict[int, Scorelist] = {}

    PLACEHOLDER = "-- Your score --"

    @staticmethod
    def load():
        if path.isfile(Scoreboard._filename):
            with open(Scoreboard._filename, "r") as file:
                Scoreboard._list = {}
                curr_list = None
                for line in file:
                    line = line.strip()
                    if len(line) > 0:
                        ma = match("-- ([0-9]*) --", line)
                        if ma is None:
                            li = line.split(" ", 1)
                            time = li[0]
                            name = ""
                            if len(li) == 2:
                                name = li[1]
                            curr_list.append((int(time), name))
                        else:
                            number = int(ma.group(1))
                            curr_list = []
                            Scoreboard._list[number] = curr_list

    @staticmethod
    def store():
        save = []
        for key in Scoreboard._list.keys():
            save.append("-- {} --".format(key))
            for x in Scoreboard._list[key]:
                save.append("{} {}".format(x[0], x[1]))

        with open(Scoreboard._filename, "w+") as file:
            file.write('\n'.join(save))

    @staticmethod
    def get_all_scores() -> List[int]:
        lis = list(Scoreboard._list.keys())
        lis.sort()
        return lis

    @staticmethod
    def get_score(score: int) -> Scorelist:
        if score in Scoreboard._list:
            return Scoreboard._list[score]
        else:
            return []

    @staticmethod
    def get_score_with_new_value(score: int, new_value: int) -> Tuple[int, Scorelist]:
        if score in Scoreboard._list:
            scorelist = list(Scoreboard._list[score])
        else:
            scorelist = []

        new = (new_value, Scoreboard.PLACEHOLDER)
        scorelist.append(new)

        scorelist = sorted(scorelist, key=itemgetter(0))

        return scorelist.index(new), scorelist

    @staticmethod
    def add_score(score: int, new_value: int, name: Optional[str]):
        if score in Scoreboard._list:
            scorelist = Scoreboard._list[score]
        else:
            scorelist = []

        scorelist.append((new_value, name))

        Scoreboard._list[score] = sorted(scorelist, key=itemgetter(0))
        Scoreboard.store()


if __name__ == "__main__":
    Scoreboard.load()

    for x in Scoreboard.get_all_scores():
        print(x)
        for h in Scoreboard.get_score(x):
            print(h)
