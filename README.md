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
- File "./gobang.py", line 81, in draw_mes, 此处为方便debug所画的坐标轴


<!-- ├── Board.py
├── Node.py
├── README.md
├── mcts.py
└── start.py -->