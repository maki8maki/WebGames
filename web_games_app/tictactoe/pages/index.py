from typing import List

import reflex as rx

from ...templates.tictactoe import t3_pages


@rx.page(route="/tictactoe", title="Tic Tac Toe")
@t3_pages(head_text="Welcome to Tic Tac Toe!", head_kwargs={"size": "9"}, need_back_t3=False)
def t3_index() -> List[rx.Component]:
    return [
        rx.hstack(
            rx.vstack(
                rx.button("2D"),
                rx.image(src="/tictactoe/2d_tictactoe.png", height="200px"),
                on_click=rx.redirect("/tictactoe/2d"),
                align="center",
            ),
            rx.vstack(
                rx.button("3D"),
                rx.image(src="/tictactoe/3d_tictactoe.png", height="200px"),
                on_click=rx.redirect("/tictactoe/3d"),
                align="center",
            ),
        )
    ]
