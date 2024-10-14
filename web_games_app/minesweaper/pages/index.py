from typing import List

import reflex as rx

from ...style import BOX_STYLE
from ...templates.minesweaper import ms_pages
from .minesweaper import MineSweaperState


def difficulty_component(text: str, height: int, width: int, num_mines: int):
    txt = rx.text(f"{text} {height}x{width} {num_mines}")
    return rx.box(
        txt,
        on_click=[MineSweaperState.set_state(height, width, num_mines), rx.redirect("/minesweaper/play")],
        style=BOX_STYLE,
    )


@rx.page(route="/minesweaper", title="Mine Sweaper")
@ms_pages(head_text="Welcome to Mine Sweaper!", head_kwargs={"size": "9"}, need_back_t3=False)
def ms_index() -> List[rx.Component]:
    return [
        rx.vstack(
            difficulty_component("Beginner", 8, 10, 10),
            difficulty_component("Intermediate", 14, 18, 40),
            difficulty_component("Expert", 20, 24, 99),
            align="center",
        )
    ]
