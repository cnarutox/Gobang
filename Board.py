import numpy as np
from itertools import groupby


class Board:
    def __init__(self, size=6):
        self.size = size
        # self.chess = np.array([[0, -1, -1, -1, 0, 0], [1, 1, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0], [1, 1, 0, 1, 0, 0], [0, 1, 0, 0, 0, 0],
        #                        [1, 0, 0, 0, 0, 0]])
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
        transpose = self.chess.transpose()
        seq.extend(transpose)
        for i in range(-self.size + 1, self.size):
            seq.extend([self.chess.diagonal(i), transpose.diagonal(i)])
        for seq in map(groupby, seq):
            for v, i in seq:
                s = list(i)
                if v == 0: continue
                if v == player and len(s) == 5:
                    return v
        return 0


if __name__ == "__main__":
    Board()