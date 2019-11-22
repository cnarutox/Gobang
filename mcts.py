import numpy as np
from copy import deepcopy
from Board import Board
from Node import Node
from random import choice, randint, shuffle


def selection(node, total, path):
    while node.child:
        ucb = None
        if len(path) % 2:
            ucb = list(map(lambda c: 1 - c.succ / c.total + np.sqrt(1 * np.log(total) / c.total), node.child))
        else:
            ucb = list(map(lambda c: c.succ / c.total + np.sqrt(1 * np.log(total) / c.total), node.child))
        node = node.child[choice(np.argwhere(ucb == max(ucb)))[0]]
        path.append(node)
    return node


def expansion(node, vacuity, path):
    waiting = set(map(lambda v: tuple(v), vacuity)) - set(map(lambda p: tuple(p.pos), path + node.child))
    # waiting = list(np.setdiff1d(vacuity, list(map(lambda p: p.pos, path + node.child))).reshape(-1, 2))
    if waiting:
        node.child.append(Node(choice(list(waiting))))
        path.append(node.child[-1])
        return node.child[-1]
    return node


def stimulation(node, board, path):
    player = 1
    for p in path:
        board.move(p.pos, player)
        player *= -1
    result = board.end(-player)
    while len(board.vacuity) and not result:
        pos = choice(board.vacuity)
        board.move(pos, player)
        result = board.end(player)
        player *= -1
    # print(f'=> The player {player * -1} moves {pos} and {result}:\n{board.chess}')
    return result


def backdate(root, path, result):
    for n in path + [root]:
        n.succ_fail(result)


def intervene(root, board):
    ucb = list(map(lambda c: c.succ / c.total + np.sqrt(1 * np.log(root.total) / c.total), root.child))
    for i, u in enumerate(ucb):
        root.child[i].ucb = u
    root.child.sort(key=lambda u: u.ucb, reverse=True)
    pos = root.child[np.argmax(ucb)].pos
    possible_pos = board.has_danger()
    if possible_pos:
        possible_pos = [tuple(i) for i in possible_pos if tuple(i) in board.vacuity and 0 <= i[0] < board.size and 0 <= i[1] < board.size]
        possible_pos = max(filter(lambda x: x.pos in possible_pos, root.child), key=lambda x: x.ucb, default=None)
        if possible_pos: return possible_pos.pos
    return pos


def mcts(board, iteration=1000):
    root = Node()
    vacuity = board.vacuity  # 可选落子处
    for i in range(iteration):
        path = []  # 截止到当前节点的搜索路径
        node = root
        if len(path) + len(node.child) >= len(vacuity):
            node = selection(node, root.total, path)
        # 判断胜负
        player = -1 if len(path) % 2 else 1
        result = board.end(-(-1 if len(path) % 2 else 1))
        if result == 0:
            node = expansion(node, vacuity, path)
            result = stimulation(node, deepcopy(board), path)
        backdate(root, path, result)
    pos = intervene(root, board)
    board.move(pos, 1)
    print(f'=> The computer moves {pos}:\n{board.chess}')
    return pos


if __name__ == "__main__":
    board = Board()
    while True:
        x, y = [int(x) for x in input('=> you move ').split()]
        board.move((x, y), -1)
        mcts(board)
        if board.end(-1) is not 0:
            break