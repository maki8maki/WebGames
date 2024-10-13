import asyncio
from typing import Dict, List

import reflex as rx

from ...style import RESULT_TOAST, THEME_BORDER
from ...templates.tictactoe import t3_pages
from ..style import CHANGE_TURN_TOAST, STATE_COLOR
from ..tictactoe import BitStrategicSelector, CubeTicTacToe, RandomSelector, Selector
from .config import BOX_SIZE, DEFAULT_SIZE, SCALE, SIZES


class CubeTicTacToeState(rx.State):
    _game: CubeTicTacToe
    _computer_selector: Selector
    colored_board: List[List[str]]
    HEIGHT: Dict[str, str]
    OFFSET: Dict[str, str]
    TRANS_Y: Dict[str, str]
    size: int = int(DEFAULT_SIZE)
    turn: int = 0
    player_turn: int = 0
    difficulty: int = 0
    _is_game_end: bool = False
    STATE_COLOR: Dict[int, str] = STATE_COLOR

    # *** 初期化やリセットに関する関数 ***
    def initialize(self):
        margin = 5
        for key in SIZES:
            size = int(key)
            self.HEIGHT[key] = str(BOX_SIZE * size**2 * SCALE + margin * (size - 1)) + "px"
            self.OFFSET[key] = str(-BOX_SIZE * size * (1 - SCALE) / 2) + "px"
            self.TRANS_Y[key] = str(-BOX_SIZE * size * (1 - SCALE) + margin) + "px"
        self.make_tictactoe()
        self.reset_selector()
        self.coloring()

    def make_tictactoe(self):
        self._game = CubeTicTacToe(self.size)

    def reset_board(self, sleep_time: float):
        self.turn = 0
        self._is_game_end = False
        self._game.reset()
        self.coloring()
        if self.player_turn == 1:
            return CubeTicTacToeState.computer_select(sleep_time)

    def reset_selector(self):
        if self.difficulty == 0:
            self._computer_selector = RandomSelector()
        elif self.difficulty == 1:
            self._computer_selector = BitStrategicSelector(
                self.size, self._game.num_cells, self._game.get_candidates()
            )

    # *** 便利関数 ***
    def coloring(self):
        sq = self.size**2
        colored_board = [[] for _ in range(self.size)]
        for i in range(len(self._game.board)):
            colored_board[i // sq].append(self.STATE_COLOR[self._game.board[i]])
        self.colored_board = colored_board

    def change_cell_color(self, index: int, color: str):
        sq = self.size**2
        div, mod = divmod(index, sq)
        self.colored_board[div][mod] = color

    # *** 選択に関する関数 ***
    def apply_select(self, num: int):
        self._is_game_end = self._game.apply_select(self.turn, num)
        self.coloring()
        if not self._is_game_end and len(self._game.rest) == 0:
            self._is_game_end = True
            return rx.toast.info("Draw", **RESULT_TOAST)
        elif self._is_game_end:
            if self.turn % 2 == self.player_turn:
                return rx.toast.success("You win!!", **RESULT_TOAST)
            else:
                return rx.toast.error("You lose...", **RESULT_TOAST)
        else:
            self.turn += 1

    def select_cell(self, index: int):
        if not self._is_game_end and self.turn % 2 == self.player_turn:
            if index not in self._game.rest:
                return rx.toast.warning("This cell is already selected", position="top-center", duration=1500)
            component = self.apply_select(index)
            if self._is_game_end:
                return component
            else:
                return CubeTicTacToeState.computer_select(1.0)

    async def computer_select(self, sleep_time: float):
        await asyncio.sleep(sleep_time)
        if isinstance(self._computer_selector, BitStrategicSelector):
            computer_turn = (self.player_turn + 1) % 2
            num = self._computer_selector.select(
                self._game.rest,
                self._game.players[computer_turn].candidates,
                self._game.players[self.player_turn].candidates,
            )
        else:
            num = self._computer_selector.select(self._game.rest)
        return self.apply_select(num)

    # *** インタラクションの関数 ***
    def change_size(self, size: str):
        self.size = int(size)
        self.make_tictactoe()
        self.reset_selector()
        return self.reset_board(0.5)

    def focus_cell(self, index: int):
        if self._game.board[index] == -1:
            self.change_cell_color(index, self.STATE_COLOR[self.turn % 2 + 2])

    def unfocus_cell(self, index: int):
        if self._game.board[index] == -1:
            self.change_cell_color(index, self.STATE_COLOR[-1])

    def change_turn(self):
        self.player_turn = (self.player_turn + 1) % 2
        turn = "first" if self.player_turn == 0 else "second"
        components = [rx.toast(f"Your turn is {turn}", **CHANGE_TURN_TOAST)]
        components.append(CubeTicTacToeState.reset_board(1.7))
        return components

    def change_difficulty(self):
        self.difficulty = (self.difficulty + 1) % 2
        self.reset_selector()
        return self.reset_board(0.5)


def render_box(color: str, layer: int, index: int):
    num = CubeTicTacToeState.size**2 * layer + index
    return rx.box(
        bg=color,
        width=f"{BOX_SIZE}px",
        height=f"{BOX_SIZE}px",
        border=THEME_BORDER,
        on_click=CubeTicTacToeState.select_cell(num),
        on_mouse_enter=CubeTicTacToeState.focus_cell(num),
        on_mouse_leave=CubeTicTacToeState.unfocus_cell(num),
    )


def setting():
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Board Size"),
                rx.select(
                    SIZES,
                    default_value=DEFAULT_SIZE,
                    on_change=lambda value: CubeTicTacToeState.change_size(value),
                    width="100%",
                    position="popper",
                ),
                align="center",
                spacing="0",
            ),
            rx.vstack(
                rx.text(f"Difficulty: Level {CubeTicTacToeState.difficulty.to_string()}"),
                rx.button("Change Difficulty", on_click=CubeTicTacToeState.change_difficulty()),
                align="center",
                spacing="0",
            ),
            align="end",
        ),
        rx.hstack(
            rx.button("Change Turn", on_click=CubeTicTacToeState.change_turn()),
            rx.button("Reset", on_click=CubeTicTacToeState.reset_board(0.5)),
        ),
        align="center",
    )


def turn_text():
    return rx.cond(
        CubeTicTacToeState.turn % 2 == CubeTicTacToeState.player_turn,
        rx.text("Your Turn", color=CubeTicTacToeState.STATE_COLOR[CubeTicTacToeState.player_turn], size="6"),
        rx.text(
            "Computer's Turn",
            color=CubeTicTacToeState.STATE_COLOR[(CubeTicTacToeState.player_turn + 1) % 2],
            size="6",
        ),
    )


def display_square(square: List[str], layer: int):
    return rx.grid(
        rx.foreach(square, lambda color, index: render_box(color, layer, index)),
        columns=CubeTicTacToeState.size.to_string(),
        border=THEME_BORDER,
        justify="center",
        class_name="panel",
        style={
            "--num": layer,
            "--scale": SCALE,
            "--offset": CubeTicTacToeState.OFFSET[CubeTicTacToeState.size.to_string()],
            "--trans-y": CubeTicTacToeState.TRANS_Y[CubeTicTacToeState.size.to_string()],
        },
    )


def display_board():
    return rx.vstack(
        rx.foreach(
            CubeTicTacToeState.colored_board,
            lambda square, layer: display_square(square, layer),
        ),
        spacing="0",
        class_name="cube",
        style={"--height": CubeTicTacToeState.HEIGHT[CubeTicTacToeState.size.to_string()]},
    )


@rx.page(route="/tictactoe/3d", title="Play Cube Tic Tac Toe", on_load=[CubeTicTacToeState.initialize()])
@t3_pages(head_text="Cube Tic Tac Toe")
def cube_t3_page() -> List[rx.Component]:
    return [setting(), turn_text(), display_board()]
