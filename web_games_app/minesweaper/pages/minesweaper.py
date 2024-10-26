import asyncio
from typing import List

import numpy as np
import reflex as rx

from ...style import RESULT_TOAST, THEME_BORDER
from ...templates.minesweaper import ms_pages
from ..minesweaper.minesweaper import FLAG_NUM, NOT_SELECTED_NUM, MineSweaper


class MineSweaperState(rx.State):
    height: int = 8
    width: int = 10
    num_mines: int = 10
    _game: MineSweaper = MineSweaper(height, width, num_mines)
    showing_board: List[int]
    focused_idx: int = -1
    _is_game_end: bool = False
    num_flags: int = 0
    elapsed_time: int = 0
    _is_running: bool = False

    # ** リセットなどの関数 **
    def on_load(self):
        self.apply_game_state()

    def reset_board(self):
        self._game.reset()
        self.apply_game_state()
        self._is_game_end = False
        self.num_flags = 0
        self.elapsed_time = 0
        self._is_running = False

    def set_state(self, height: int, width: int, num_mines: int):
        self.height = height
        self.width = width
        self.num_mines = num_mines
        self._game = MineSweaper(self.height, self.width, self.num_mines)
        self.reset_board()

    def apply_game_state(self):
        self.showing_board = self._game.showing_board.flatten().tolist()
        self.num_flags = np.count_nonzero(self._game.showing_board == FLAG_NUM)

    @rx.background
    async def update_elapsed_time(self):
        if self._is_running:
            return
        while True:
            await asyncio.sleep(1)
            if self._is_game_end or not self._is_running:
                break
            async with self:
                self.elapsed_time += 1

    # ** マウスイベントに関する関数 **
    def open_cell(self, index: int):
        if not self._is_game_end:
            self._is_running = True
            is_fail = self._game.open_cell(index)
            self.apply_game_state()
            if not is_fail:
                self._is_game_end = True
                return rx.toast.error("You failed...", **RESULT_TOAST)
            elif self._game.is_all_selected():
                self._is_game_end = True
                return rx.toast.success("You succeeded!!", **RESULT_TOAST)

    def put_or_unput_flag(self, index: int):
        if not self._is_game_end:
            self._game.put_or_unput_flag(index)
            self.apply_game_state()

    def focus_cell(self, index: int):
        self.focused_idx = index

    def unfocus_cell(self):
        self.focused_idx = -1


def display_info():
    return rx.hstack(
        rx.button("Reset", on_click=MineSweaperState.reset_board()),
        rx.hstack(
            rx.image(src="/minesweaper/flag.png", width="30px"),
            rx.text(f"{MineSweaperState.num_flags} / {MineSweaperState.num_mines}"),
            align="center",
            spacing="0",
        ),
        rx.hstack(
            rx.image(src="/minesweaper/clock.png", width="30px"),
            rx.text(f"{MineSweaperState.elapsed_time}"),
            align="center",
            spacing="1",
        ),
        align="center",
    )


def get_box_content(state: int):
    return rx.cond(
        (state != 0) & (state != NOT_SELECTED_NUM),
        rx.cond(state == FLAG_NUM, rx.image(src="/minesweaper/flag.png", width="20px"), rx.text(state)),
    )


def get_background_color(index: int):
    return rx.cond(
        (MineSweaperState.showing_board[index] != NOT_SELECTED_NUM)
        & (MineSweaperState.showing_board[index] != FLAG_NUM),
        "var(--gray-2)",
        rx.cond(MineSweaperState.focused_idx == index, "var(--gray-5)", "var(--gray-9)"),
    )
    # return rx.cond(MineSweaperState.focused_idx == index, rx.color("gray", shade=3), rx.color("gray", shade=7))


def render_box(state: int, index: int):
    return rx.box(
        get_box_content(state),
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
