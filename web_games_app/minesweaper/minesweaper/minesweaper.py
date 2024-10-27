import random as rnd
from collections import deque
from typing import List, Tuple, Union

import numpy as np

IntOrArray = Union[int, np.ndarray, List[int]]


def check_state_num(num: int) -> bool:
    """
    状態として利用するのに有効な数字か判断する

    Args:
        num (int): 確認する数値

    Returns:
        bool: 有効な数字か
    """
    return not (0 <= num <= 8)


MINE_NUM = -1
FLAG_NUM = -2
NOT_SELECTED_NUM = -3
assert check_state_num(MINE_NUM), f"MINE_NUM (={MINE_NUM}) is invalid number"
assert check_state_num(FLAG_NUM), f"FLAG_NUM (={FLAG_NUM}) is invalid number"
assert check_state_num(NOT_SELECTED_NUM), f"NOT_SELECTED_NUM (={NOT_SELECTED_NUM}) is invalid number"
s = [MINE_NUM, FLAG_NUM, NOT_SELECTED_NUM]
assert len(set(s)) == len(s), (
    f"MINE_NUM (={MINE_NUM}), FLAG_NUM (={FLAG_NUM})" f" and NOT_SELECTED_NUM (={NOT_SELECTED_NUM}) must be differnt"
)
del s


class MineSweaper:
    height: int
    width: int
    num_cells: int
    num_mines: int
    num_remain_cells: int
    num_selected_cells: int
    is_initialized: bool
    # 実際の盤面...MINE_NUM：地雷、それ以外：周囲の地雷の数
    actual_board: np.ndarray
    # 表示用の盤面...MINE_NUM：地雷、FLAG_NUM：旗、NOT_SELECTED_NUM：未選択、それ以外：周囲の地雷の数
    showing_board: np.ndarray

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
        self.is_initialized = False
        self.actual_board = np.zeros((self.height, self.width), dtype=int)
        self.showing_board = np.full((self.height, self.width), NOT_SELECTED_NUM, dtype=int)

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

    def is_selected(self, cell: Union[int, tuple]) -> bool:
        assert isinstance(cell, (int, tuple))
        if isinstance(cell, int):
            idx = self.num2index(cell)
        else:
            idx = cell
        return self.showing_board[idx] != NOT_SELECTED_NUM and self.showing_board[idx] != FLAG_NUM

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
        self.actual_board[self.num2index(mines_nums)] = MINE_NUM

        # 周囲の地雷の数を数える
        for i in range(self.height):
            for j in range(self.width):
                if self.actual_board[i, j] == MINE_NUM:
                    continue
                surroundings = self.get_surroundings(self.index2num(i, j))
                sum = 0
                for n in surroundings:
                    if self.actual_board[self.num2index(n)] == MINE_NUM:
                        sum += 1
                self.actual_board[i, j] = sum

        self.is_initialized = True

    def open_cell(self, num: int) -> bool:
        """
        選択されたセルを開ける

        Args:
            num (int): 選択した数字

        Returns:
            bool: 地雷を選択したときのみFalseを返す
        """
        if self.actual_board[self.num2index(num)] == MINE_NUM:
            return False
        else:
            if not self.is_initialized:
                self.initialize(num)
            q = deque([num])
            while len(q) > 0:
                n = q.pop()
                idx = self.num2index(n)
                if self.is_selected(idx):
                    # 旗が置かれているか選択済みのときにスキップ
                    continue
                elif self.actual_board[idx] != MINE_NUM:
                    self.showing_board[idx] = self.actual_board[idx]  # 表示値を更新
                    self.num_selected_cells += 1  # 選択済みセルの数を更新
                    if self.actual_board[idx] == 0:
                        # 周囲のセルも開ける候補にする
                        surroundings = self.get_surroundings(n)
                        for s in surroundings:
                            if not self.is_selected(s):
                                q.append(s)
            return True

    def is_all_selected(self) -> bool:
        """
        地雷以外の全ての場所が選択されたか判定する

        Returns:
            bool: Trueのとき、全て選択されている
        """
        return self.num_selected_cells == self.num_remain_cells

    def put_or_unput_flag(self, num: int):
        """
        選択されたセルに旗を設置または排除する

        Args:
            num (int): 選択された数字
        """
        idx = self.num2index(num)
        if self.showing_board[idx] == FLAG_NUM:
            self.showing_board[idx] = NOT_SELECTED_NUM
        elif self.showing_board[idx] == NOT_SELECTED_NUM:
            self.showing_board[idx] = FLAG_NUM


if __name__ == "__main__":
    ms = MineSweaper(10, 8, 20)
    while True:
        print(ms.showing_board)
        num = int(input("select cell: "))
        if not ms.open_cell(num):
            exit()
