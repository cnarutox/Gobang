import numpy as np


class Node:
    # node类初始化ƒ
    def __init__(self, pos=None):
        self.succ = 0
        self.total = 0
        self.child = []
        self.pos = pos
        self.ucb = 0

    def succ_fail(self, win):
        if win == 1:
            self.succ += 1
        self.total += 1

    def __repr__(self):
        return f'{self.pos}=>{self.succ}/{self.total}={self.ucb}'

    def __eq__(self, node):
        return self.pos == node.pos

    def __hash__(self):
        return id(self)