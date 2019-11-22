import numpy as np
from itertools import groupby


class Board:
    def __init__(self, size=7):
        self.size = size
        self.chess = np.array([
            [0, -1, -1, -1, 0, 0],
            [1, 1, 0, -1, 0, 0],
            [0, 0, -1, -1, -1, 0],
            [1, 1, 0, -1, 0, 0],
            [0, 1, -1, 0, -1, 0],
            [1, 0, 0, 0, 0, 0],
        ])
        # self.chess = np.array([
        #     [0, 0, 0, 0, 0, 0, 0],
        #     [0, 1, 0, -1, 0, 0, 1],
        #     [0, 0, -1, -1, -1, 0, 0],
        #     [0, 0, 0, -1, 0, 0, 0],
        #     [0, 0, -1, 0, -1, 0, 0],
        #     [0, 1, 0, 1, 1, 1, 0],
        #     [0, 0, 0, 0, 0, 0, 0],
        # ])
        self.chess = np.zeros((size, size), int)
        print(f'==> Board initializing:\n{self.chess}')
        self.update()
        self.three_seq = []

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

    def has_danger(self):
        seq = list(self.chess)
        seq.extend(self.chess.transpose())
        fliplr = np.fliplr(self.chess)
        for i in range(-self.size + 1, self.size):
            seq.append(self.chess.diagonal(i))
        if self.size % 2:
            for i in range(-self.size + 1, self.size):
                seq.append(fliplr.diagonal(i)[::-1])
        else:
            for i in range(-self.size + 1, self.size):
                seq.append(fliplr.diagonal(i))
        position = []
        for index, seq in enumerate(map(groupby, seq)):
            loc = 0
            for v, i in seq:
                i = list(i)
                if v != -1:
                    loc += len(i)
                    continue
                if len(i) >= 3:
                    if index < self.size:
                        pos = [index, loc, len(i)]
                        position.extend([(pos[0], p) for p in (pos[1] - 1, pos[1] + pos[-1]) if 0 <= p < self.size])
                    elif index < self.size * 2:
                        pos = [loc, index - self.size, len(i)]
                        position.extend([(p, pos[1]) for p in (pos[0] - 1, pos[0] + pos[-1]) if 0 <= p < self.size])
                    elif index < self.size * 4 - 1:
                        x = index - self.size * 2
                        if x > self.size - 1: pos = [loc, x + loc - (self.size - 1), len(i)]
                        else: pos = [loc + self.size - 1 - x, loc, len(i)]
                        position.extend([np.array(pos[:-1]) - 1, np.array(pos[:-1]) + pos[-1]])
                    else:
                        x = index - self.size * 4 + 1
                        if x > self.size - 1: pos = [self.size - 1 - (x + loc - (self.size - 1)), loc, len(i)]
                        else: pos = [self.size - 1 - loc, loc + self.size - 1 - x, len(i)]
                        position.extend([np.array(pos[:-1]) + [1, -1], np.array(pos[:-1]) - [pos[-1], -pos[-1]]])
                loc += len(i)
        return position


if __name__ == "__main__":
    Board()