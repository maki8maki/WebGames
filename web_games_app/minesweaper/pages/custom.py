from typing import Dict, List

import reflex as rx

from ...templates.minesweaper import ms_pages
from .minesweaper import MineSweaperState

KEY = ["height", "width", "num_mines"]
DEFAULT_STATE = {
    "height": 8,
    "width": 10,
    "num_mines": 10,
}


class CustomMSState(rx.State):
    state: Dict[str, int] = DEFAULT_STATE.copy()
    min_state: Dict[str, int] = {
        "height": 5,
        "width": 5,
        "num_mines": int(state["height"] * state["width"] * 0.1),
    }
    max_state: Dict[str, int] = {
        "height": 99,
        "width": 35,
        "num_mines": int(state["height"] * state["width"] * 0.8),
    }
    TEXT: Dict[str, str] = {
        "height": "Height",
        "width": "Width",
        "num_mines": "Number of Mines",
    }

    def reset_state(self):
        self.state = DEFAULT_STATE.copy()

    def change_state(self, key: str, value: str):
        if not value == "":
            self.state[key] = int(value)

    def clip_state(self, key: str, value: str):
        if value == "":
            self.state[key] = 0
        self.state[key] = max(self.min_state[key], min(self.state[key], self.max_state[key]))

    def increment(self, key: str):
        self.state[key] = min(self.state[key] + 1, self.max_state[key])

    def decrement(self, key: str):
        self.state[key] = max(self.state[key] - 1, self.min_state[key])

    def apply_state(self):
        return [
            MineSweaperState.set_state(self.state["height"], self.state["width"], self.state["num_mines"]),
            rx.redirect("/minesweaper/play"),
        ]


def render_input(key: str):
    return rx.hstack(
        rx.box(CustomMSState.TEXT[key], width="130px"),
        rx.input(
            value=CustomMSState.state[key].to_string(),
            default_value=CustomMSState.state[key].to_string(),
            on_change=CustomMSState.change_state(key),
            on_blur=CustomMSState.clip_state(key),
            width="35px",
        ),
        rx.button(
            "-",
            disabled=(CustomMSState.state[key] <= CustomMSState.min_state[key]),
            on_click=CustomMSState.decrement(key),
            type="button",
            color_scheme="gray",
        ),
        rx.button(
            "+",
            disabled=(CustomMSState.state[key] >= CustomMSState.max_state[key]),
            on_click=CustomMSState.increment(key),
            type="button",
            color_scheme="gray",
        ),
        spacing="0",
        align="center",
    )


def display_settings():
    return rx.form(
        rx.vstack(
            rx.foreach(KEY, render_input),
            rx.button(
                "Start playing",
                type="submit",
                width="200px",
            ),
            align="center",
        ),
        on_submit=CustomMSState.apply_state(),
    )


@rx.page(route="/minesweaper/custom", title="Mine Sweaper - Custom Settings", on_load=CustomMSState.reset_state())
@ms_pages(head_text="Mine Sweaper - Custom Settings")
def custom_ms_page() -> List[rx.Component]:
    return [display_settings()]
