import os
from copy import deepcopy
from functools import reduce
from multiprocessing import Pool, Queue, managers
from random import choice, randint, shuffle

import numpy as np

from Board import Board
from Node import Node

managers.BaseManager.register('Board', Board)
manager = managers.BaseManager()
manager.start()


def selection(node, total, path):
    while node.child:
        ucb = None
        if len(path) % 2:
            ucb = list(map(lambda c: 1 - c.succ / c.total + 2 * np.sqrt(np.log(total) / c.total), node.child))
        else:
            ucb = list(map(lambda c: c.succ / c.total + 2 * np.sqrt(np.log(total) / c.total), node.child))
        node = node.child[choice(np.argwhere(ucb == max(ucb)))[0]]
        path.append(node)
    return node


def expansion(node, vacuity, path):
    waiting = set(map(lambda v: tuple(v), vacuity)) - set(map(lambda p: tuple(p.pos), path + node.child))
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
    return result


def backdate(root, path, result):
    for n in path + [root]:
        n.succ_fail(result)


def intervene(root, board):
    pos = board.defend()
    if pos:
        print(f' defend', end='')
        return pos
    ucb = list(
        map(lambda c: (c.succ / c.total + 2 * np.sqrt(np.log(root.total) / c.total), c.succ / c.total), root.child))
    for i, u in enumerate(ucb):
        root.child[i].ucb = u[0]
    pos = root.child[np.argmax(ucb)].pos
    return pos


def search(board, iteration):
    root = Node()
    vacuity = board.get_vacuity()  # 可选落子处
    for i in range(iteration):
        path = []  # 截止到当前节点的搜索路径
        node = root
        if len(path) + len(node.child) >= len(vacuity):
            node = selection(node, root.total, path)
        player = -1 if len(path) % 2 else 1
        # 判断胜负
        result = board.end(-(-1 if len(path) % 2 else 1))
        if result == 0:
            node = expansion(node, vacuity, path)
            result = stimulation(node, deepcopy(board), path)
        backdate(root, path, result)
    return root


def integration(node):
    for n in node:
        n.child.sort(key=lambda x: x.pos)
    child = []
    for z in zip(*[n.child for n in node]):
        child.append(reduce(lambda x, y: x.add(y), z))
    return child.copy()


def mcts(queue, iteration=100):
    board = queue.get()
    pool = Pool(os.cpu_count() - 1)
    results = []
    # pool.starmap_async(search, [(board, iteration)])
    for i in range(os.cpu_count() - 1):
        results.append(pool.apply_async(search, (board, iteration)))
    pool.close()
    pool.join()
    results = [res.get() for res in results]
    root = results[0].add(*results[1:])
    root.child = integration(results)
    print(root.child)
    pos = intervene(root, board)
    queue.put(pos)
    # print(root, root.child)
    return pos


if __name__ == "__main__":
    managers.BaseManager.register('Board', Board)
    manager = managers.BaseManager()
    manager.start()
    board = manager.Board()
    queue = Queue()
    while True:
        x, y = [int(x) for x in input('=> you move ').split()]
        board.move((x, y), -1)
        queue.put(board)
        pos = mcts(queue)
        board.move(pos, 1)
        if board.end(-1) is not 0:
            break
