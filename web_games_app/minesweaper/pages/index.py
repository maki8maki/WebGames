from typing import List

import reflex as rx

from ...templates.minesweaper import ms_pages


@rx.page(route="/minesweaper", title="Mine Sweaper")
@ms_pages(head_text="Welcome to Mine Sweaper!", head_kwargs={"size": "9"}, need_back_t3=False)
def ms_index() -> List[rx.Component]:
    return []
