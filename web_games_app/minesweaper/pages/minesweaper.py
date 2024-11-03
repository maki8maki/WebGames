import asyncio
from typing import List

import numpy as np
import reflex as rx

from ...style import RESULT_TOAST, THEME_BORDER
from ...templates.minesweaper import ms_pages
from ..minesweaper.minesweaper import (
    FLAG_NUM,
    MINE_NUM,
    NOT_SELECTED_NUM,
    MineSweaper,
    check_state_num,
)

NOT_SELECTED_MINE_NUM = -10
FAILED_FLAG_NUM = -11
assert check_state_num(NOT_SELECTED_MINE_NUM), f"NOT_SELECTED_MINE_NUM (={NOT_SELECTED_MINE_NUM}) is invalid number"
assert check_state_num(FAILED_FLAG_NUM), f"FAILED_FLAG_NUM (={FAILED_FLAG_NUM}) is invalid number"
s = [MINE_NUM, FLAG_NUM, NOT_SELECTED_NUM, NOT_SELECTED_MINE_NUM, FAILED_FLAG_NUM]
assert len(set(s)) == len(s), (
    f"MINE_NUM (={MINE_NUM}), FLAG_NUM (={FLAG_NUM})"
    f", NOT_SELECTED_NUM (={NOT_SELECTED_NUM}), NOT_SELECTED_MINE_NUM (={NOT_SELECTED_MINE_NUM})"
    f" and FAILED_FLAG_NUM (={FAILED_FLAG_NUM}) must be differnt"
)
del s


class MineSweaperState(rx.State):
    height: int = 8
    width: int = 10
    num_mines: int = 10
    _game: MineSweaper = MineSweaper(height, width, num_mines)
    showing_board: List[int]
    focused_idx: int = -1
    _is_game_end: bool = False
    num_flags: int = 0
    _elapsed_time: int = 0
    _is_running: bool = False

    # ** リセットなどの関数 **
    def on_load(self):
        self.apply_game_state()

    def reset_board(self):
        self._game.reset()
        self.apply_game_state()
        self._is_game_end = False
        self.num_flags = 0
        self._elapsed_time = 0
        self._is_running = False

    def set_state(self, height: int, width: int, num_mines: int):
        self.height = height
        self.width = width
        self.num_mines = num_mines
        self._game = MineSweaper(self.height, self.width, self.num_mines)
        self.reset_board()

    def apply_game_state(self, is_fail=False):
        self.showing_board = self._game.showing_board.flatten().tolist()
        self.num_flags = np.count_nonzero(self._game.showing_board == FLAG_NUM)
        if is_fail:
            actual = self._game.actual_board.flatten().tolist()
            for i in range(len(self.showing_board)):
                if actual[i] == MINE_NUM and self.showing_board[i] == NOT_SELECTED_NUM:
                    self.showing_board[i] = NOT_SELECTED_MINE_NUM
                elif self.showing_board[i] == FLAG_NUM and 0 <= actual[i] <= 8:
                    self.showing_board[i] = FAILED_FLAG_NUM

    # ** 経過時間に関する関数 **
    @rx.background
    async def update_elapsed_time(self):
        if self._is_running:
            return
        while True:
            await asyncio.sleep(1)
            if self._is_game_end or not self._is_running:
                break
            async with self:
                self._elapsed_time += 1

    @rx.var(cache=True)
    def display_elapsed_time(self):
        return str(self._elapsed_time).zfill(3)

    # ** マウスイベントに関する関数 **
    def open_cell(self, index: int):
        if not self._is_game_end:
            self._is_running = True
            is_not_fail = self._game.open_cell(index)
            if not is_not_fail or self._game.is_all_selected():
                self._is_game_end = True
            self.apply_game_state(not is_not_fail)
            if not is_not_fail:
                return rx.toast.error("You failed...", **RESULT_TOAST)
            elif self._game.is_all_selected():
                return rx.toast.success("You succeeded!!", **RESULT_TOAST)

    def put_or_unput_flag(self, index: int):
        if not self._is_game_end:
            self._game.put_or_unput_flag(index)
            self.apply_game_state()

    def focus_cell(self, index: int):
        if not self._is_game_end:
            self.focused_idx = index

    def unfocus_cell(self):
        self.focused_idx = -1


def display_info():
    return rx.hstack(
        rx.button("Reset", on_click=MineSweaperState.reset_board()),
        rx.box(
            rx.hstack(
                rx.image(src="/minesweaper/flag.png", width="30px"),
                rx.text(
                    f"{MineSweaperState.num_flags} / {MineSweaperState.num_mines}",
                    font_family="Instrument Sans",
                    size="4",
                    weight="medium",
                ),
                align="center",
                spacing="1",
            ),
            width="95px",
        ),
        rx.box(
            rx.hstack(
                rx.image(src="/minesweaper/clock.png", width="30px"),
                rx.text(
                    MineSweaperState.display_elapsed_time, font_family="Instrument Sans", size="4", weight="medium"
                ),
                align="center",
                spacing="1",
            ),
            width="70px",
        ),
        align="center",
    )


def get_box_content(state: int):
    return rx.cond(
        (state != 0) & (state != NOT_SELECTED_NUM),
        rx.cond(
            (state == FLAG_NUM) | (state == FAILED_FLAG_NUM),
            rx.image(src="/minesweaper/flag.png", width="20px"),
            rx.cond(
                state == NOT_SELECTED_MINE_NUM,
                rx.image(src="/minesweaper/mine.png", width="20px"),
                rx.text(state),
            ),
        ),
    )


def get_background_color(index: int):
    return rx.cond(
        (MineSweaperState.showing_board[index] != NOT_SELECTED_NUM)
        & (MineSweaperState.showing_board[index] != FLAG_NUM)
        & (MineSweaperState.showing_board[index] != FAILED_FLAG_NUM)
        & (MineSweaperState.showing_board[index] != NOT_SELECTED_MINE_NUM),
        rx.color("gray", shade=2),
        rx.cond(
            (MineSweaperState.showing_board[index] == FAILED_FLAG_NUM)
            | (MineSweaperState.showing_board[index] == NOT_SELECTED_MINE_NUM),
            rx.color("red", shade=7),
            rx.cond(MineSweaperState.focused_idx == index, rx.color("gray", shade=5), rx.color("gray", shade=9)),
        ),
    )


def render_box(state: int, index: int):
    return rx.box(
        rx.center(get_box_content(state)),
        bg=get_background_color(index),
        width="25px",
        height="25px",
        border=THEME_BORDER,
        on_click=[MineSweaperState.update_elapsed_time(), MineSweaperState.open_cell(index)],
        on_context_menu=MineSweaperState.put_or_unput_flag(index).prevent_default,
        on_mouse_enter=MineSweaperState.focus_cell(index),
        on_mouse_leave=MineSweaperState.unfocus_cell(),
        text_align="center",
    )


def display_board():
    return rx.grid(
        rx.foreach(MineSweaperState.showing_board, lambda state, index: render_box(state, index)),
        columns=MineSweaperState.width.to_string(),
        border=THEME_BORDER,
        justify="center",
    )


@rx.page(route="/minesweaper/play", title="Play Mine Sweaper", on_load=MineSweaperState.on_load())
@ms_pages(head_text="Mine Sweaper")
def ms_page() -> List[rx.Component]:
    return [display_info(), display_board()]
