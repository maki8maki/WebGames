from typing import List

import reflex as rx

from ...style import BOX_STYLE
from ...templates.minesweaper import ms_pages
from .minesweaper import MineSweaperState

CUSTOM_BOX_STYLE = BOX_STYLE.copy()
CUSTOM_BOX_STYLE.update({"padding": "0em"})


def difficulty_component(text: str, height: int, width: int, num_mines: int):
    return rx.box(
        rx.vstack(
            rx.text(text, weight="bold"),
            rx.text(f"{height} x {width}"),
            rx.text(f"{num_mines} mines"),
            align="center",
            spacing="0",
        ),
        on_click=[MineSweaperState.set_state(height, width, num_mines), rx.redirect("/minesweaper/play")],
        style=CUSTOM_BOX_STYLE,
        width="200px",
    )


def custom_component():
    return rx.box(
        rx.text("\nCustom\n\n", weight="bold", white_space="pre"),
        on_click=rx.redirect("/minesweaper/custom"),
        style=CUSTOM_BOX_STYLE,
        width="200px",
        text_align="center",
    )


@rx.page(route="/minesweaper", title="Mine Sweaper")
@ms_pages(head_text="Welcome to Mine Sweaper!", head_kwargs={"size": "9"}, need_back_t3=False)
def ms_index() -> List[rx.Component]:
    return [
        rx.vstack(
            difficulty_component("Beginner", 8, 10, 10),
            difficulty_component("Intermediate", 14, 18, 40),
            difficulty_component("Expert", 20, 24, 99),
            custom_component(),
            align="center",
        )
    ]
