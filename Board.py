from copy import deepcopy
from itertools import groupby

import numpy as np


class Board:
    def __init__(self, size=11):
        self.size = size
        self.chess = np.zeros((size, size), int)
        print(f'==> Board initializing:\n{self.chess}')
        self.update()

    def update(self):
        self.vacuity = list(map(lambda x: tuple(x), np.argwhere(self.chess == 0)))

    def move(self, pos, player):
        self.chess[pos[0], pos[1]] = player
        self.update()

    def end(self, player):
        seq = list(self.chess)
        seq.extend(self.chess.transpose())
        fliplr = np.fliplr(self.chess)
        for i in range(-self.size + 1, self.size):
            seq.append(self.chess.diagonal(i))
        for i in range(-self.size + 1, self.size):
            seq.append(fliplr.diagonal(i))
        for seq in map(groupby, seq):
            for v, i in seq:
                if v == 0: continue
                if v == player and len(list(i)) == 5:
                    return v
        return 0

    def defend(self):
        for x, y in self.vacuity:
            origin = map(groupby, [
                self.chess[x],
                self.chess.transpose()[y],
                self.chess.diagonal(y - x),
                np.fliplr(self.chess).diagonal(self.size - 1 - y - x)
            ])
            origin = [x for x in origin]
            chess = deepcopy(self.chess)
            chess[x][y] = -1
            for index, seq in enumerate(
                    map(groupby, [
                        chess[x],
                        chess.transpose()[y],
                        chess.diagonal(y - x),
                        np.fliplr(chess).diagonal(self.size - 1 - y - x)
                    ])):
                seq = [(v, len(list(i))) for v, i in seq]
                org_seq = [(v, len(list(i))) for v, i in origin[index]]
                for i, v in enumerate(seq):
                    if v[0] != -1: continue
                    if v[1] >= 5: return x, y
                    if v[1] == 4 and seq.count((-1, 4)) != org_seq.count((-1, 4)):
                        if i - 1 >= 0 and seq[i - 1][0] == 0 and i + 1 < len(seq) and seq[i + 1][0] == 0: return x, y
        return None


if __name__ == "__main__":
    Board()
