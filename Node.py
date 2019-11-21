import numpy as np


class Node:
    # node类初始化
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

    def __truediv__(self, value):
        pass

    def __repr__(self):
        return f'{self.pos}=>{self.succ}/{self.total}={self.ucb}'

    def __eq__(self, node):
        return self.pos == node.pos

    # 重写__eq__后必须重写__hash__
    def __hash__(self):
        return id(self)

    # def __lt__(self, node):
    #     pass

    # def __le__(self, node):
    #     if self < node or self == node:
    #         return True
    #     else:
    #         return False


def selection(node, choise):
    all_selected = False

    # 当前节点不含所有元素
    while len(node.state) < len(choise):
        # 第一次访问新节点，初始化它的孩子节点
        if len(node.children) == 0:
            init_children(node, choise)
        # 如果当前节点存在没有访问过的孩子节点，则依据概率选择深度优先还是广度优先
        Q_max = 0
        is_random = False
        for i in node.children:
            if i.Q > Q_max:
                Q_max = i.Q
            if i.N == 0:
                is_random = True

        if is_random:
            if random.random() > Q_max:
                # 继续扩展node节点，选择未访问的操作，相当于广度搜索
                return node, all_selected

        # 否则依据UCB公式计算最优的孩子节点，重复这个过程
        node = best_child(node)

    # 当前节点包含所有元素，不再搜索并返回
    all_selected = True
    return node, all_selected


def init_children(node, choise):
    # 搜集不在当前节点中的元素，放入列表rest_e
    rest_e = []
    for i in choise:
        if i not in node.state:
            rest_e.append(i)
    # 取 rest_e 中的一个元素与当前节点状态组合，生成新的节点
    for e in rest_e:
        child = Node()
        id = next(g)
        child.name = f'{e}_{id}'
        for parent_e in node.state:
            child.state.append(parent_e)
        child.state.append(e)
        child.parents = node
        node.children.append(child)
        graph.edge(child.name, node.name, f'{id}')
        graph.node(child.name, f'{e}')


def best_child(node):
    # 依据UCB公式计算最优孩子节点
    best_score = -1
    best = None

    for sub_node in node.children:

        # 在可选的节点里面选择最优
        if sub_node.Q > 0:
            C = math.sqrt(2.0)
            left = sub_node.Q
            right = math.log(node.N) / sub_node.N
            score = left + C * math.sqrt(right)

            if score > best_score:
                best = sub_node
                best_score = score

    return best


def expansion(selection_node, score_single_e):
    # 得到所有孩子节点中的新元素
    e_field = []
    for i in selection_node.children:
        if i.N == 0:
            e_field.append(i.state[-1])

    # 在新元素中选择PS值最大的一个
    max_e = get_max_e_by_ps(e_field, score_single_e)
    return max_e


def get_max_e_by_ps(e_field, score_single_e):
    max_e = -1
    max_score = -1
    # for index in range(len(e_field)):
    #     # 避免重复计算，score_single_e在主函数中计算
    #     score = score_single_e[index]
    #     if score > max_score:
    #         max_score = score
    #         max_e = e_field[index]
    # return max_e
    for index in e_field:
        score = score_single_e[index[0]]
        if score > max_score:
            max_score = score
            max_e = index
    return max_e
    return e_field[score_single_e.index(max(score_single_e))]


def evalation(selection_node, max_e, forecast, real, v, f):
    new_set = copy.deepcopy(selection_node.state)
    new_set.append(max_e)
    # 对新状态计算PS值大小
    ps = get_scores(new_set, forecast, real, v, f)
    return ps


def get_scores(set, forecast, real, v, f):
    # 复制预测值为cp(copy)
    cp = copy.deepcopy(forecast[:-1])
    # 在cp的基础上，根据状态中的所有元素，将cp对应位置改变为计算值
    # 1维
    if len(set[0]) == 1:
        for i in set:
            for row in range(len(real) - 1):
                # 改变为计算值
                cp[row][i] = getVDesc(forecast[row][i], forecast[-1][i], real[-1][i])

    # 2维
    if len(set[0]) == 2:
        for i in set:
            # 直接改变为真实值
            cp[i[0]][i[1]] = real[i[0]][i[1]]

    # 去掉每行最后的累和，并把cp整理为一维
    a = []
    for l in range(len(cp)):
        a.extend(cp[l][:-1])
    # 计算PS值的最终公式
    result = max(1 - getDistance(v, a) / getDistance(v, f), 0)
    return result


def getVDesc(fDesc, f, v):
    # 公式(5): 计算v(x')
    return fDesc - (f - v) * float(fDesc) / f


def getDistance(u, w):
    # 计算两向量的距离
    return math.sqrt(reduce(lambda x, y: x + y, map(lambda x: (x[0] - x[1])**2, zip(u, w))))


def backup(selection_node, max_e, ps):
    index = -1
    # 获取计算节点在孩子中的序号
    for i in range(len(selection_node.children)):
        if selection_node.children[i].state[-1] == max_e:
            index = i
            break

    # 从最下层节点开始，对整条路径上的节点：N+1，Q赋值为路径中最大Q值
    node = selection_node.children[index]
    while node is not None:
        node.N += 1
        if ps > node.Q:
            node.Q = ps
        node = node.parents


def get_best_node(node):
    # 获得最大Q值的所有节点中的最下层的节点
    best_score = node.Q
    while len(node.children) is not 0:
        for index in range(len(node.children)):
            if node.children[index].Q == best_score:
                node = node.children[index]
                break
    return node


def MCTS(forecast, real, choise, M, PT):
    # 计算Q值公式中需要的真实向量v、预测向量f
    v = []
    f = []
    row_num = len(forecast) - 1

    for i in range(row_num):
        v.extend(real[i][:-1])
        f.extend(forecast[i][:-1])

    # 计算单元素 Potential Score值
    score_single_e = []
    for e in choise:
        score_single_e.append(get_scores([e], forecast, real, v, f))

    # 初始化根节点, PS值记录，最优节点
    node = Node('root')
    max_ps = 0
    best_node = None

    # 开始搜索，最大搜索次数可变
    for i in range(M):

        # 1、选择，如果所有节点搜索完毕，则跳出循环
        selection_node, all_selected = selection(node, choise)
        if all_selected:
            break

        # 2、扩展，获得剩余元素中的最大元素值
        max_e = expansion(selection_node, score_single_e)

        # 3、评价，原状态与最大元素值组合成新状态，获得新状态的Q值
        ps = evalation(selection_node, max_e, forecast, real, v, f)

        # 4、更新，新状态节点至根节点路径中的每个节点：N+1，Q赋值为路径中最大Q值
        backup(selection_node, max_e, ps)

        # 如果根节点Q值变大，则更新最优节点
        if node.Q > max_ps:
            best_node = get_best_node(node)
            max_ps = node.Q
        # 如果新节点的Q值超过预设阀值，则跳出循环
        if ps >= PT:
            break
    return best_node


def get_choise(forecast):
    return [[i] for i in range(len(forecast[0]) - 1)]
    choise = []
    for i in range(len(forecast[0]) - 1):
        choise.append([i])
    return choise


def get_result(row_name, column_name, forecast, real, M, PT):
    forecast = np.array(forecast, float)
    real = np.array(real, float)

    column_node = MCTS(forecast, real, get_choise(forecast), M, PT)
    row_node = MCTS(np.transpose(forecast), np.transpose(real), get_choise(np.transpose(forecast)), M, PT)
    print(column_node.Q, column_node.state)
    print(row_node.Q, row_node.state)
    mix_choise = []
    for row in row_node.state:
        for column in column_node.state:
            mix_choise.append([row[0], column[0]])
    mix_node = MCTS(forecast, real, mix_choise, M, PT)

    result_name = []
    result_Q = 0

    # # 返回综合结果
    # if row_node.Q >= column_node.Q and row_node.Q >= mix_node.Q:
    #     for i in row_node.state:
    #         result_name.append([row_name[i[0]]])
    #         result_Q = row_node.Q
    # elif column_node.Q >= row_node.Q and column_node.Q >= mix_node.Q:
    #     for i in column_node.state:
    #         result_name.append([column_name[i[0]]])
    #         result_Q = column_node.Q
    # elif mix_node.Q > row_node.Q and mix_node.Q > column_node.Q:
    #     for i in mix_node.state:
    #         result_name.append([row_name[i[0]], column_name[i[1]]])
    #         result_Q = mix_node.Q

    # 返回二维结果
    print
    for i in mix_node.state:
        result_name.append([row_name[i[0]], column_name[i[1]]])
        result_Q = mix_node.Q

    return result_name, result_Q


if __name__ == '__main__':
    # M 是最大搜索次数
    M = 1000
    # PT 是Q值的阀值
    PT = 0.75
    graph = Digraph('Node', format='png')
    g = (i for i in range(10000))

    # # 测试数据1
    row_name = ['Mobile', 'Unicom']
    column_name = ['Beijing', 'Shanghai', 'Guangzhou']
    forecast = [[20, 15, 10, 45], [10, 25, 20, 55], [30, 40, 30, 100]]
    real = [[14, 9, 10, 33], [7, 15, 20, 42], [21, 24, 30, 75]]

    # # 测试数据2
    # row_name = ['Mobile', 'Unicom']
    # column_name = ['Fujian', 'Jiangsu', 'Zhejiang']
    # forecast = [[20, 15, 10, 45], [10, 25, 20, 55], [30, 40, 30, 100]]
    # real = [[5, 15, 10, 30], [10, 13, 20, 43], [15, 28, 30, 73]]

    # # 测试数据3
    # row_name = ['联通', '电信', '移动', '长宽']
    # column_name = ['内蒙古', '山东省', '广东省', '新疆', '江西省', '河北省', '浙江省', '海南省', '湖北省', '湖南省', '辽宁省', '黑龙江省']
    # forecast = [[53, 0, 111, 0, 0, 203, 0, 0, 0, 0, 141, 87, 595], [0, 113, 0, 34, 0, 173, 0, 41, 0, 0, 0, 0, 361],
    #             [0, 236, 213, 0, 74, 94, 221, 0, 55, 49, 51, 0, 993], [0, 0, 73, 0, 0, 0, 0, 0, 0, 0, 0, 0, 73],
    #             [53, 349, 397, 34, 74, 470, 221, 41, 55, 49, 192, 87, 2022]]
    # real = [[32, 0, 70, 0, 0, 124, 0, 0, 0, 0, 75, 63, 364], [0, 61, 0, 9, 0, 78, 0, 15, 0, 0, 0, 0, 163],
    #         [0, 141, 112, 0, 44, 56, 127, 0, 29, 39, 15, 0, 563], [0, 0, 41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 41],
    #         [32, 202, 223, 9, 44, 258, 127, 15, 29, 39, 90, 63, 1131]]

    name, Q = get_result(row_name, column_name, forecast, real, M, PT)

    print("根因组合: ")
    print(json.dumps(name, ensure_ascii=False))
    print("组合得分: ")
    print(Q)
    graph.view()
