## Gobang Based on Monte Carlo Tree Search
> Author: cnarutox
> Lanuage: Python
> Platform: MacOS, Windows, Linux

### gobang.py
> 程序启动的入口
- `Game`类管控游戏的启动，重启，悔棋与认输
  - 成员变量`board`对应**Board.py**中的棋盘类
  - 成员变量`player`取值为-1(**玩家**)与1(**电脑**)
  - 成员变量`last_p`为存储上一步走法的列表(最多两个元素：**玩家**与**电脑**)
  - 成员变量`queue`为存储**mcts.py**搜索结果的队列
  - 成员函数`waiting`负责从队列**queue**中获得搜索结果
    - 若**queue**为空则说明搜索未完成，需再次尝试获得
    - 若在等待过程中玩家选择`bf_regret`(悔棋)，`last_p`会被清空，此时程序会在拿到搜索结果后放弃该结果
  - 成员函数`cf_board`为界面的绑定触发函数
    - 玩家(**黑棋**)出棋后会有另外一个进程去执行`mcts`函数
    - `after`函数可以延迟指定时间(**100ms**)去执行`waiting`函数，防止阻塞负责渲染UI的主进程

Statistics by type
------------------
| type     | number | old number | difference | %documented | %badname |
| -------- | ------ | ---------- | ---------- | ----------- | -------- |
| module   | 4      | NC         | NC         | 0.00        | 50.00    |
| class    | 3      | NC         | NC         | 33.33       | 0.00     |
| method   | 22     | NC         | NC         | 54.55       | 0.00     |
| function | 6      | NC         | NC         | 0.00        | 0.00     |

External dependencies
---------------------
    Board (gobang,mcts)
    Node (mcts)
    mcts (gobang)

Raw metrics
-----------
| type      | number | %     | previous | difference |
| --------- | ------ | ----- | -------- | ---------- |
| code      | 322    | 77.78 | NC       | NC         |
| docstring | 31     | 7.49  | NC       | NC         |
| comment   | 7      | 1.69  | NC       | NC         |
| empty     | 54     | 13.04 | NC       | NC         |

Duplication
-----------
|                          | now   | previous | difference |
| ------------------------ | ----- | -------- | ---------- |
| nb duplicated lines      | 0     | NC       | NC         |
| percent duplicated lines | 0.000 | NC       | NC         |

Messages by category
--------------------
| type       | number | previous | difference |
| ---------- | ------ | -------- | ---------- |
| convention | 73     | NC       | NC         |
| refactor   | 6      | NC       | NC         |
| warning    | 16     | NC       | NC         |
| error      | 7      | NC       | NC         |

% errors / warnings by module
-----------------------------
| module | error | warning | refactor | convention |
| ------ | ----- | ------- | -------- | ---------- |
| gobang | 42.86 | 31.25   | 66.67    | 46.58      |
| mcts   | 28.57 | 56.25   | 16.67    | 24.66      |
| Board  | 14.29 | 6.25    | 16.67    | 21.92      |
| Node   | 14.29 | 6.25    | 0.00     | 6.85       |
