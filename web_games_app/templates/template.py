from typing import Callable, List

import reflex as rx

from ..style import BACK_COMPONENT_STYLE, BOX_STYLE


def back_component():
    return rx.button("Back to Top", on_click=rx.redirect("/"), class_name=BACK_COMPONENT_STYLE)


def template(head_text: str, head_kwargs: dict = {"size": "8"}, *args) -> Callable:
    def wrapper(page: Callable[[], List[rx.Component]]) -> rx.Component:
        return rx.container(
            rx.color_mode.button(position="top-right"),
            rx.vstack(
                rx.heading(head_text, **head_kwargs),
                rx.divider(),
                *(page()),
                align="center",
                style=BOX_STYLE,
            ),
            rx.logo(),
            *args,
        )

    return wrapper
