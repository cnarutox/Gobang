from itertools import cycle
from multiprocessing import Process, Queue
from tkinter import (BOTH, DISABLED, LEFT, NORMAL, RIGHT, YES, Button, Canvas, Frame, Label, Text, Tk)
from tkinter.messagebox import showinfo

import numpy as np

from Board import Board
from mcts import mcts


class Game:
    """Summary of Game here.

    Attributes:
        player: 1 or -1 indicating if player is person computer.
        grid: An integer count of the length of board grid.
    """
    def __init__(self):
        self.size = 11
        self.grid = 50
        self.shrink = 0.8
        self.player = 0
        self.board = None
        self.previous = []
        self.is_start = False
        self.half_grid = self.grid / 2
        self.chess_radius = self.half_grid * self.shrink
        self.special_point = self.half_grid * 0.3
        self.queue = Queue()
        self.board_color = "#FAD76E"
        self.func_bg = "#F0C896"
        self.font = ("Times New Roman", 20, "normal")
        # This is resposible for the GUI, so you do not need
        # to care more about this because they are mostly
        # formulated code
        self.tk = Tk()
        self.tk.title("Gobang 五子棋")
        self.tk.resizable(width=False, height=False)

        self.tk_header = Frame(self.tk, highlightthickness=0, bg=self.func_bg)
        self.tk_header.pack(fill=BOTH, ipadx=10)

        self.func_start = Button(self.tk_header, text="Start", command=self.start, font=self.font)
        self.func_restart = Button(self.tk_header, text="Restart", command=self.restart, state=DISABLED, font=self.font)
        self.info = Label(self.tk_header,
                          text="Starting",
                          bg=self.func_bg,
                          font=("Times New Roman", 20, "normal"),
                          fg="grey")
        self.func_regret = Button(self.tk_header, text="Regret", command=self.regret, state=DISABLED, font=self.font)
        self.func_giveup = Button(self.tk_header, text="GiveUp", command=self.giveup, state=DISABLED, font=self.font)

        self.func_start.pack(side=LEFT, padx=10)
        self.func_restart.pack(side=LEFT)
        self.info.pack(side=LEFT, expand=YES, fill=BOTH, pady=5)
        self.func_giveup.pack(side=RIGHT, padx=10)
        self.func_regret.pack(side=RIGHT)

        self.canvas = Canvas(self.tk,
                             bg=self.board_color,
                             width=(self.size + 1) * self.grid,
                             height=(self.size + 1) * self.grid,
                             highlightthickness=0)
        self.draw_board()
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.pack()

        self.tk.mainloop()

    def draw_grid(self, x, y):
        """Draw a grid of given x and y.

        Args:
            x: The x of a coordinate.
            y: The y of a coordinate.

        Returns:
            None.

        Raises:
            None.
        """
        shrink = (1 - self.shrink) + 1
        center_x, center_y = self.grid * (x + 1), self.grid * (y + 1)
        self.canvas.create_rectangle(center_y - self.half_grid,
                                     center_x - self.half_grid,
                                     center_y + self.half_grid,
                                     center_x + self.half_grid,
                                     fill=self.board_color,
                                     outline=self.board_color)
        a, b = [0, shrink] if y == 0 else [-shrink, 0] if y == self.size - 1 else [-shrink, shrink]
        c, d = [0, shrink] if x == 0 else [-shrink, 0] if x == self.size - 1 else [-shrink, shrink]
        self.canvas.create_line(center_y + a * self.half_grid, center_x, center_y + b * self.half_grid, center_x)
        self.canvas.create_line(center_y, center_x + c * self.half_grid, center_y, center_x + d * self.half_grid)
        [self.canvas.create_text(self.grid * (i + 1), self.grid * 0.8, text=f'{i}') for i in range(self.size)]
        [self.canvas.create_text(self.grid * 0.8, self.grid * (i + 1), text=f'{i}') for i in range(self.size)]

        # draw special points
        if ((x == 3 or x == 7) and (y == 3 or y == 7)):
            self.canvas.create_oval(center_y - self.special_point,
                                    center_x - self.special_point,
                                    center_y + self.special_point,
                                    center_x + self.special_point,
                                    fill="#555555")

    def draw_chess(self, x, y, color):
        """Draw a chess of given x and y with color.

        Args:
            x: The x of a coordinate.
            y: The y of a coordinate.
            color: The color of the chess (black or white).
        """
        center_x, center_y = self.grid * (x + 1), self.grid * (y + 1)
        self.canvas.create_oval(center_y - self.chess_radius,
                                center_x - self.chess_radius,
                                center_y + self.chess_radius,
                                center_x + self.chess_radius,
                                fill=color)

    def draw_board(self):
        """Draw a chess of given x and y with color."""
        [self.draw_grid(x, y) for y in range(self.size) for x in range(self.size)]

    def start(self):
        """Set the initial states of components and initialize the board."""
        self.set_state("start")
        self.is_start = True
        self.player = -1
        self.board = Board(self.size)
        self.draw_board()
        self.info.config(text="黑方下棋", fg='black')

    def restart(self):
        self.start()

    def regret(self):
        # Regretting when it's your turn to walk is not allowed (len(self.previous) == 2).
        if not self.previous or len(self.previous) == 2:
            showinfo("提示", "您已没有机会悔棋")
            self.previous = []
            return
        x, y = self.previous[0]
        self.draw_grid(x, y)
        self.board.chess[x, y] = 0
        self.info.config(text="黑方下棋", fg='#444444')
        self.previous = []
        self.player = -1

    def giveup(self):
        '''The player can choose to give up by his/her own.
        '''
        self.set_state("init")
        self.is_start = False
        self.info.config(text="The player gives up!", fg='red')

    def waiting(self):
        if not self.previous:
            print('\r')
            self.queue = Queue()
            return
        elif not self.queue.empty():
            pos = self.queue.get()
            self.draw_chess(*pos, "white")
            self.player = -1
            self.board.move(pos, 1)
            print(f' {pos}')
            self.info.config(text="黑方下棋", fg='#444444')
            self.previous.append(pos)
            return
        self.info.config(text="白方下棋" + next(self.points), fg='#ffffee')
        self.tk.after(1000, self.waiting)

    def click(self, e):
        if self.player != -1: return
        self.player = 1
        x, y = int((e.y - self.half_grid) / self.grid), int((e.x - self.half_grid) / self.grid)
        if not ((0, ) * 2 <= (x, y) < (self.size, ) * 2):
            self.player = -1
            return
        center_x, center_y = self.grid * (x + 1), self.grid * (y + 1)
        distance = np.linalg.norm(np.array([center_x, center_y]) - np.array([e.y, e.x]))
        if not self.is_start or distance > self.half_grid * 0.95 or self.board.chess[x, y] != 0:
            self.player = -1
            return
        self.draw_chess(x, y, "black")
        print(f'=> 黑方: {(x, y)}')
        self.board.move((x, y), -1)
        self.previous = [(x, y)]
        if self.player_win(x, y, -1):
            self.is_start = False
            self.set_state("init")
            self.info.config(text="Well done! You win", fg='yellow')
            return
        self.points = cycle(['.' * i for i in range(7)])
        self.info.config(text="白方下棋" + next(self.points), fg='#ffffee')
        print(f'=> 白方:', end='')
        self.queue.put(self.board)
        Process(target=mcts, args=(self.queue, 150)).start()
        self.tk.after(1000, self.waiting)

    def player_win(self, x, y, tag):
        four_direction = [[self.board.chess[i][y] for i in range(self.size)]]
        four_direction.append([self.board.chess[x][j] for j in range(self.size)])
        four_direction.append(self.board.chess.diagonal(y - x))
        four_direction.append(np.fliplr(self.board.chess).diagonal(self.size - 1 - y - x))
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

    def set_state(self, state):
        '''Set the states of functional buttons.
        '''
        state_list = [NORMAL, DISABLED, DISABLED, DISABLED] if state == "init" else [DISABLED, NORMAL, NORMAL, NORMAL]
        self.func_start.config(state=state_list[0])
        self.func_restart.config(state=state_list[1])
        self.func_regret.config(state=state_list[2])
        self.func_giveup.config(state=state_list[3])


if __name__ == '__main__':
    Game()
