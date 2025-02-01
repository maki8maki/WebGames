from typing import List

import reflex as rx

from .style import APP_THEME, STYLESHEETS
from .templates.template import template


@rx.page(route="/", title="Web Games")
@template(head_text="Welcome to My Web Games!", head_kwargs={"size": "9"})
def index() -> List[rx.Component]:
    return [
        rx.vstack(
            rx.vstack(
                rx.text("Tic Tac Toe", size="7", weight="bold"),
                rx.hstack(
                    rx.image(src="/tictactoe/2d_tictactoe.png", height="100px"),
                    rx.image(src="/tictactoe/3d_tictactoe.png", height="100px"),
                ),
                on_click=rx.redirect("/tictactoe"),
                align="center",
            ),
            rx.vstack(
                rx.text("Mine Sweaper", size="7", weight="bold"),
                rx.image(src="/minesweaper/minesweaper.png", height="150px"),
                on_click=rx.redirect("/minesweaper"),
                align="center",
            ),
            align="center",
        )
    ]


app = rx.App(stylesheets=STYLESHEETS, theme=rx.theme(**APP_THEME))
