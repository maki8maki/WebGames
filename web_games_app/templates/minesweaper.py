from typing import Callable

import reflex as rx

from ..style import BACK_COMPONENT_STYLE
from .template import back_component, template


def ms_back_component(need_back_t3: bool = True):
    if need_back_t3:
        return rx.vstack(
            rx.button("Back to Mine Sweaper", on_click=rx.redirect("/minesweaper")),
            rx.button("Back to Top", on_click=rx.redirect("/")),
            class_name=BACK_COMPONENT_STYLE,
            spacing="1",
            align="end",
        )
    else:
        return back_component()


def ms_pages(head_text: str, head_kwargs: dict = {"size": "8"}, need_back_t3: bool = True) -> Callable:
    return template(head_text, head_kwargs, ms_back_component(need_back_t3))
