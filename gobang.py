# 用数组定义一个棋盘，棋盘大小为 15×15
# 数组索引代表位置，
# 元素值代表该位置的状态：0代表没有棋子，1代表有黑棋，-1代表有白棋。
from Board import Board
from mcts import mcts
from tkinter import *
from tkinter.messagebox import *
from multiprocessing import Process, Queue


class Game:
    def __init__(self):
        #############
        # param #
        #######################################
        self.row, self.column = 11, 11
        self.mesh = 50
        self.ratio = 0.9
        self.board_color = "#CDBA96"
        self.header_bg = "#CDC0B0"
        self.btn_font = ("黑体", 20, "bold")
        self.step = self.mesh / 2
        self.chess_r = self.step * self.ratio
        self.point_r = self.step * 0.2
        self.board = None
        self.is_start = False
        self.player = 0
        self.last_p = []
        self.queue = Queue()

        ###########
        # GUI #
        #######################################
        self.root = Tk()
        self.root.title("Gobang 五子棋")
        self.root.resizable(width=False, height=False)

        self.f_header = Frame(self.root, highlightthickness=0, bg=self.header_bg)
        self.f_header.pack(fill=BOTH, ipadx=10)

        self.b_start = Button(self.f_header, text="Start", command=self.bf_start, font=self.btn_font)
        self.b_restart = Button(self.f_header, text="Restart", command=self.bf_restart, state=DISABLED, font=self.btn_font)
        self.l_info = Label(self.f_header, text="Waiting", bg=self.header_bg, font=("楷体", 20, "bold"), fg="white")
        self.b_regret = Button(self.f_header, text="Regret", command=self.bf_regret, state=DISABLED, font=self.btn_font)
        self.b_lose = Button(self.f_header, text="GiveUp", command=self.bf_lose, state=DISABLED, font=self.btn_font)

        self.b_start.pack(side=LEFT, padx=20)
        self.b_restart.pack(side=LEFT)
        self.l_info.pack(side=LEFT, expand=YES, fill=BOTH, pady=10)
        self.b_lose.pack(side=RIGHT, padx=20)
        self.b_regret.pack(side=RIGHT)

        self.c_chess = Canvas(self.root,
                              bg=self.board_color,
                              width=(self.column + 1) * self.mesh,
                              height=(self.row + 1) * self.mesh,
                              highlightthickness=0)
        self.draw_board()
        self.c_chess.bind("<Button-1>", self.cf_board)
        self.c_chess.pack()

        self.root.mainloop()

    # 画x行y列处的网格
    def draw_mesh(self, x, y):
        # 一个倍率，由于tkinter操蛋的GUI，如果不加倍率，悔棋的时候会有一点痕迹，可以试试把这个改为1，就可以看到
        ratio = (1 - self.ratio) * 0.99 + 1
        center_x, center_y = self.mesh * (x + 1), self.mesh * (y + 1)
        # 先画背景色
        self.c_chess.create_rectangle(center_y - self.step,
                                      center_x - self.step,
                                      center_y + self.step,
                                      center_x + self.step,
                                      fill=self.board_color,
                                      outline=self.board_color)
        # 再画网格线，这里面a b c d是不同的系数，根据x,y不同位置确定，需要一定推导。
        a, b = [0, ratio] if y == 0 else [-ratio, 0] if y == self.row - 1 else [-ratio, ratio]
        c, d = [0, ratio] if x == 0 else [-ratio, 0] if x == self.column - 1 else [-ratio, ratio]
        self.c_chess.create_line(center_y + a * self.step, center_x, center_y + b * self.step, center_x)
        self.c_chess.create_line(center_y, center_x + c * self.step, center_y, center_x + d * self.step)
        ### 调试需求
        [self.c_chess.create_text(self.mesh * (i + 1), self.mesh * 0.8, text=f'{i}') for i in range(self.column)]
        [self.c_chess.create_text(self.mesh * 0.8, self.mesh * (i + 1), text=f'{i}') for i in range(self.column)]

        # 有一些特殊的点要画小黑点
        if ((x == 3 or x == 11) and (y == 3 or y == 11)) or (x == 7 and y == 7):
            self.c_chess.create_oval(center_y - self.point_r, center_x - self.point_r, center_y + self.point_r, center_x + self.point_r, fill="black")

    # 画x行y列处的棋子，color指定棋子颜色
    def draw_chess(self, x, y, color):
        center_x, center_y = self.mesh * (x + 1), self.mesh * (y + 1)
        # 就是画个圆
        self.c_chess.create_oval(center_y - self.chess_r, center_x - self.chess_r, center_y + self.chess_r, center_x + self.chess_r, fill=color)

    # 画整个棋盘
    def draw_board(self):
        [self.draw_mesh(x, y) for y in range(self.column) for x in range(self.row)]

    # 在正中间显示文字
    def center_show(self, text):
        width, height = int(self.c_chess['width']), int(self.c_chess['height'])
        self.c_chess.create_text(int(width / 2), int(height / 2), text=text, font=("黑体", 30, "bold"), fill="red")

    # 开始的时候设置各个组件，变量的状态，初始化board矩阵，初始化棋盘，初始化信息
    def bf_start(self):
        self.set_btn_state("start")
        self.is_start = True
        self.player = -1
        self.board = Board(self.row)
        self.draw_board()
        self.l_info.config(text="黑方下棋")

    # 重来跟开始的效果一样
    def bf_restart(self):
        self.bf_start()

    # 用last_p来标识上一步的位置。先用网格覆盖掉棋子，操作相应的变量，board.chess[x][y]要置空，只能悔一次棋
    def bf_regret(self):
        if not self.last_p or len(self.last_p) == 2:
            showinfo("提示", "现在不能悔棋")
            self.last_p = []
            return
        x, y = self.last_p[0]
        self.draw_mesh(x, y)
        self.board.chess[x][y] = 0
        self.l_info.config(text="黑方下棋")
        self.last_p = []
        self.player = -1

    # 几个状态改变，还有显示文字，没什么说的
    def bf_lose(self):
        self.set_btn_state("init")
        self.is_start = False
        self.l_info.config(text="黑方认输" if self.player == -1 else "白方认输")
        self.center_show("蔡")

    def waiting(self):
        if not self.last_p and not self.queue.empty():
            print('\r')
            self.queue.get()
            return
        elif not self.queue.empty():
            pos = self.queue.get()
            self.draw_chess(*pos, "white")
            self.player = -1
            self.board.move(pos, 1)
            print(f'{pos}')
            self.l_info.config(text="黑方下棋")
            self.last_p.append(pos)
            return
        self.root.after(100, self.waiting)

    # Canvas的click事件
    def cf_board(self, e):
        if self.player != -1: return
        self.player = 1
        # 找到离点击点最近的坐标
        x, y = int((e.y - self.step) / self.mesh), int((e.x - self.step) / self.mesh)
        if x >= self.row or y >= self.column or x < 0 or y < 0:
            self.player = -1
            return
        # 找到该坐标的中心点位置ƒ
        center_x, center_y = self.mesh * (x + 1), self.mesh * (y + 1)
        # 计算点击点到中心的距离
        distance = ((center_x - e.y)**2 + (center_y - e.x)**2)**0.5
        # 如果距离不在规定的圆内，退出//如果这个位置已经有棋子，退出//如果游戏还没开始，退出
        if not self.is_start or distance > self.step * 0.95 or self.board.chess[x][y] != 0:
            self.player = -1
            return
        # 先画棋子，在修改board相应点的值，用last_p记录本次操作点
        self.draw_chess(x, y, "black")
        print(f'=> 黑方: {(x, y)}')
        self.board.move((x, y), -1)
        self.last_p = [(x, y)]
        # 如果赢了，则游戏结束，修改状态，中心显示某方获胜
        if self.is_win(x, y, -1):
            self.is_start = False
            self.set_btn_state("init")
            self.center_show("黑方获胜")
            self.l_info.config(text="已结束")
            return
        # 如果游戏继续，则交换棋手
        self.l_info.config(text="白方下棋")
        print(f'=> 白方:', end='')
        Process(target=mcts, args=(self, self.queue, 200)).start()
        self.root.after(100, self.waiting)

    def is_win(self, x, y, tag):
        # 获取斜方向的列表
        def direction(i, j, di, dj, row, column, chess):
            temp = []
            while 0 <= i < row and 0 <= j < column:
                i, j = i + di, j + dj
            i, j = i - di, j - dj
            while 0 <= i < row and 0 <= j < column:
                temp.append(chess[i][j])
                i, j = i - di, j - dj
            return temp

        four_direction = []
        # 获取水平和竖直方向的列表
        four_direction.append([self.board.chess[i][y] for i in range(self.row)])
        four_direction.append([self.board.chess[x][j] for j in range(self.column)])
        # 获取斜方向的列表
        four_direction.append(direction(x, y, 1, 1, self.row, self.column, self.board.chess))
        four_direction.append(direction(x, y, 1, -1, self.row, self.column, self.board.chess))

        # 一一查看这四个方向，有没有满足五子连珠
        for v_list in four_direction:
            count = 0
            for v in v_list:
                if v == tag:
                    count += 1
                    if count == 5:
                        return True
                else:
                    count = 0
        return False

    # 设置四个按钮是否可以点击
    def set_btn_state(self, state):
        state_list = [NORMAL, DISABLED, DISABLED, DISABLED] if state == "init" else [DISABLED, NORMAL, NORMAL, NORMAL]
        self.b_start.config(state=state_list[0])
        self.b_restart.config(state=state_list[1])
        self.b_regret.config(state=state_list[2])
        self.b_lose.config(state=state_list[3])

    # 因为有很多和self.black相关的三元操作，所以就提取出来
    def ternary_operator(self, true, false):
        return true if self.is_black else false


if __name__ == '__main__':
    Game()
