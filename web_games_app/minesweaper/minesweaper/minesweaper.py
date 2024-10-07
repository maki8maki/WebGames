import random as rnd
from collections import deque
from typing import List, Tuple, Union

import numpy as np

IntOrArray = Union[int, np.ndarray, List[int]]


class MineSweaper:
    height: int
    width: int
    num_cells: int
    num_mines: int
    num_remain_cells: int
    num_selected_cells: int
    board: np.ndarray  # -1：地雷、それ以外：周囲の地雷の数
    is_show: np.ndarray

    def __init__(self, height: int, width: int, num_mines: int) -> None:
        self.height = height
        self.width = width
        self.num_cells = height * width
        self.num_mines = num_mines
        self.reset()

    def reset(self):
        """
        盤面をリセットする
        """
        self.num_remain_cells = self.num_cells - self.num_mines
        self.num_selected_cells = 0
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.is_show = np.full((self.height, self.width), False, dtype=bool)

    def num2index(self, num: IntOrArray) -> Tuple[IntOrArray, IntOrArray]:
        """
        数字を2次元のインデックスに変換する

        Args:
            num (IntOrArray): セルを表す数字（0 - self.num_cells-1）

        Returns:
            Tuple[IntOrArray, IntOrArray]: 2次元のインデックスのタプル
        """
        if isinstance(num, int):
            assert 0 <= num < self.num_cells
        else:
            if isinstance(num, list):
                num = np.array(num)
            assert (0 <= num).all() and (num < self.num_cells).all()
        return num // self.width, num % self.width

    def index2num(self, i: IntOrArray, j: IntOrArray) -> IntOrArray:
        """
        2次元のインデックスを数字に変換する

        Args:
            i (IntOrArray): 1次元目のインデックス
            j (IntOrArray): 2次元目のインデックス

        Returns:
            IntOrArray: セルを表す数字
        """
        if isinstance(i, int):
            assert 0 <= i < self.height
        else:
            if isinstance(i, list):
                i = np.array(i)
            assert (0 <= i).all() and (i < self.height).all()
        if isinstance(j, int):
            assert 0 <= j < self.width
        else:
            if isinstance(j, list):
                j = np.array(j)
            assert (0 <= j).all() and (j < self.width).all()
        return i * self.width + j

    def get_surroundings(self, num: int) -> List[int]:
        """
        周囲8方向のセルを表す数字を取得する。ただし、範囲外のものは含まれない。

        Args:
            num (int): セルを表す数字

        Returns:
            List[int]: 周囲のセルを表す数字
        """
        diff = [-1, 0, 1]
        nums = []
        i, j = self.num2index(num)
        for dh in diff:
            for dw in diff:
                try:
                    nums.append(self.index2num(i + dh, j + dw))
                except AssertionError:
                    continue
        return nums

    def initialize(self, num: int):
        """
        選択した数字に応じてセルを初期化する。最初に選択した数字の周囲は地雷が設置されない。

        Args:
            num (int): 選択した数字
        """
        # 選択したマスの周囲を除いて地雷の位置を決める
        excluded_nums = self.get_surroundings(num)
        candidates = [i for i in range(self.num_cells) if i not in excluded_nums]
        mines_nums = rnd.sample(candidates, self.num_mines)
        self.board[self.num2index(mines_nums)] = -1

        # 周囲の地雷の数を数える
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i, j] == -1:
                    continue
                surroundings = self.get_surroundings(self.index2num(i, j))
                sum = 0
                for n in surroundings:
                    if self.board[self.num2index(n)] == -1:
                        sum += 1
                self.board[i, j] = sum

        assert self.select_cell(num)

    def select_cell(self, num: int) -> bool:
        """
        数字の選択を適用する

        Args:
            num (int): 選択した数字

        Returns:
            bool: 地雷を選択したときのみFalseを返す
        """
        if self.board[self.num2index(num)] == -1:
            return False
        q = deque([num])
        while len(q) > 0:
            n = q.pop()
            idxs = self.num2index(n)
            if self.is_show[idxs]:
                continue
            if self.board[idxs] != -1:
                self.is_show[idxs] = True
                self.num_selected_cells += 1
                if self.board[idxs] == 0:
                    surroundings = self.get_surroundings(n)
                    for s in surroundings:
                        if not self.is_show[self.num2index(s)]:
                            q.append(s)
        return True

    def is_all_selected(self) -> bool:
        """
        地雷以外の全ての場所が選択されたか判定する

        Returns:
            bool: Trueのとき、全て洗濯されている
        """
        return self.num_selected_cells == self.num_remain_cells


if __name__ == "__main__":
    ms = MineSweaper(10, 8, 20)
    ms.initialize(0)
    print(ms.board)
    while True:
        print(ms.board * ms.is_show)
        num = int(input("select cell: "))
        if not ms.select_cell(num):
            exit()
