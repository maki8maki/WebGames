from typing import List

import reflex as rx

from ...templates.minesweaper import ms_pages

MAX_RECORD = 10


def to_state(height: int, width: int, num_mines: int) -> str:
    return f"{height}x{width}x{num_mines}"


class MSRecord(rx.Model, table=True):
    state: str
    time: int


class MSRecordState(rx.State):
    state: str = to_state(8, 10, 10)

    @rx.var(cache=False)
    def data(self) -> List[List[int]]:
        with rx.session() as session:
            records = session.exec(
                MSRecord.select().where(MSRecord.state == self.state).order_by(MSRecord.time.asc())
            ).all()

        data = []
        for i in range(min(10, len(records))):
            time = records[i].time
            if i > 0 and time == records[i - 1].time:
                rank = data[-1][0]
            else:
                rank = i + 1
            data.append([rank, time])

        return data

    @rx.var(cache=False)
    def states(self) -> List[str]:
        with rx.session() as session:
            return session.exec(
                MSRecord.select()
                .with_only_columns(MSRecord.state)
                .distinct(MSRecord.state)
                .order_by(MSRecord.state.asc())
            ).all()


def show_data(data: List[List[int]]):
    return rx.table.row(
        rx.table.cell(data[0]),
        rx.table.cell(data[1]),
    )


def states():
    return rx.select(MSRecordState.states, value=MSRecordState.state, on_change=MSRecordState.set_state)


def table():
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Rank"),
                rx.table.column_header_cell("Time"),
            ),
        ),
        rx.table.body(rx.foreach(MSRecordState.data, show_data)),
    )


@rx.page(route="/minesweaper/records", title="Mine Sweaper Records")
@ms_pages(head_text="Records")
def ms_records() -> List[rx.Component]:
    return [states(), table()]
