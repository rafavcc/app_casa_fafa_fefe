from datetime import date

from nicegui import events, ui

from app import crud
from app.balance import calculate_month_detail, calculate_year_months
from app.components import (
    BRL_JS,
    COLORS,
    base_chart,
    category_axes,
    change_hint,
    kpi_card,
    money_input,
    person_split,
    settlement_banner,
    value_axis,
    year_select,
)
from app.database import get_session
from app.formatting import format_brl, format_number_br, format_pct, month_name, parse_money
from app.theme import card_classes, page_classes


CHART_VIEWS = {"spending": "Gastos", "payers": "Quem pagou", "saldo": "Saldo"}

SALDO_TOOLTIP_JS = """
const v = p[0].value;
const f = Math.abs(v).toLocaleString("pt-BR", {minimumFractionDigits: 2, maximumFractionDigits: 2});
const text = v > 0 ? `Fafa deve R$ ${f}` : v < 0 ? `Fafa pagou R$ ${f}` : "Contas iguais";
return p[0].name + "<br>" + text;
"""


def _labels(months: list[dict]) -> list[str]:
    return [month["month_short"] for month in months]


def spending_chart(months: list[dict]) -> dict:
    return base_chart(
        xaxis=category_axes(_labels(months)),
        yaxis=value_axis(),
        series=[
            {
                "name": "Variável",
                "type": "bar",
                "stack": "total",
                "data": [m["variable_total"] for m in months],
                "itemStyle": {"color": COLORS["variable"]},
            },
            {
                "name": "Fixo",
                "type": "bar",
                "stack": "total",
                "data": [m["regular_total"] for m in months],
                "itemStyle": {"color": COLORS["fixo"]},
            },
        ],
    )


def payers_chart(months: list[dict]) -> dict:
    def should_line(name: str, key: str, color: str) -> dict:
        return {
            "name": name,
            "type": "line",
            "data": [m[key] for m in months],
            "lineStyle": {"type": "dashed", "color": color},
        }

    return base_chart(
        xaxis=category_axes(_labels(months)),
        yaxis=value_axis(),
        series=[
            {
                "name": "Fafa pagou",
                "type": "bar",
                "data": [m["fafa_paid"] for m in months],
                "itemStyle": {"color": COLORS["FAFA"]},
                "showLine": False,
            },
            {
                "name": "Fefe pagou",
                "type": "bar",
                "data": [m["fefe_paid"] for m in months],
                "itemStyle": {"color": COLORS["FEFE"]},
                "showLine": False,
            },
            should_line("Fafa deveria", "fafa_should_pay", COLORS["FAFA"]),
            should_line("Fefe deveria", "fefe_should_pay", COLORS["FEFE"]),
        ],
    )


def saldo_chart(months: list[dict]) -> dict:
    """Bars: Fefe owes Fafa. Negative bars: Fafa owes Fefe."""
    data = [
        {
            "value": m["balance"],
            "itemStyle": {
                "color": COLORS["FAFA"] if m["balance"] >= 0 else COLORS["FEFE"]
            },
        }
        for m in months
    ]

    return base_chart(
        tooltip={"trigger": "axis", "confine": True, "formatter": SALDO_TOOLTIP_JS},
        grid={"left": 8, "right": 12, "top": 26, "bottom": 8, "containLabel": True},
        xaxis=category_axes(_labels(months)),
        yaxis=value_axis(),
        series=[
            {
                "name": "Saldo",
                "type": "bar",
                "data": data,
                "itemStyle": {"borderRadius": 4},
            }
        ],
    )


def category_chart(detail: dict) -> dict:
    items = [(c["name"], c, "variable") for c in detail["variable_categories"]]
    items += [(c["name"], c, "regular") for c in detail["regular_categories"]]

    items = [
        (f"{c["name"]}", c, "variable") for c in detail["variable_categories"]
    ]

    # ECharts draws the first category at the bottom
    items.reverse()

    return {
        "grid": {
            "left": 8,
            "right": 16,
            "top": 8,
            "bottom": 32,
            "containLabel": True,
        },
        "tooltip": {"trigger": "axis", "confine": True},
        "xAxis": value_axis(),
        "yAxis": category_axes([name for name, _, _ in items]),
        "series": [
            {
                "name": "Este mês",
                "type": "bar",
                "data": [
                    {
                        "value": c["total"],
                        "itemStyle": {
                            "color": COLORS[kind],
                            "borderRadius": [0, 4, 4, 0],
                        },
                    }
                    for _, c, kind in items
                ],
                "itemStyle": {"color": COLORS["variable"]},
            },
            {
                "name": "Mês anterior",
                "type": "bar",
                "data": [
                    {
                        "value": c["previous_total"],
                        "itemStyle": {
                            "color": COLORS["previous"],
                            "opacity": 0.5,
                            "borderRadius": [0, 4, 4, 0],
                        },
                    }
                    for _, c, _ in items
                ],
            },
        ],
    }


CHART_BUILDERS = {
    "spending": spending_chart,
    "payers": payers_chart,
    "saldo": saldo_chart,
}


def build_balance() -> None:
    today = date.today()
    state: dict = {"months": {}, "view": "spending"}
    sections: dict[int, ui.element] = {}
    holders: dict[int, ui.column] = {}

    with ui.page_container():
        ui.label("Balanço do mês").classes("casa-page-title text-2xl font-bold")

        with ui.row().classes("w-full gap-3 px-3"):
            year = year_select(today.year, on_change=lambda: load())
            ui.label("Ano").classes("text-xs casa-muted")

        with ui.row().classes("w-full gap-3"):
            with ui.card().classes(card_classes("w-full p-3 gap-2")) as chart_card:
                ui.toggle(
                    CHART_VIEWS,
                    value="spending",
                    on_change=lambda e: set_view(e.value),
                ).props("spread").mark("chart-view")

                chart_area = ui.column().classes("w-full")

                ui.label(
                    "Toque em um mês para ver os detalhes."
                ).classes("text-xs casa-muted")

        sections_column = ui.column().classes("w-full gap-3")

    def set_view(view: str) -> None:
        state["view"] = view
        render_chart()

    def ordered_months() -> list[int]:
        return [
            m for m in sorted(state["months"])
            if state["months"][m].get("month")
        ]

    def render_chart() -> None:
        chart_area.clear()
        months = ordered_months()

        chart_card.set_visibility(bool(months))

        if not months:
            return

        with chart_area:
            ui.echart(
                CHART_BUILDERS[state["view"]](months),
                on_point_click=open_month,
            ).classes("w-full h-72")

    def open_month(e: events.EChartPointClickEventArguments) -> None:
        month = ordered_months()[e.data_index]
        section = sections.get(month)

        if section is None:
            return

        if isinstance(section, ui.expansion):
            section.value = True

        ui.run_javascript(
            f'getHtmlElement("{section.id}").scrollIntoView({{behavior: "smooth", block: "start"}})'
        )

    def load_month(month: int) -> None:
        with get_session() as db:
            state["months"][month] = calculate_month_detail(
                db,
                month,
                int(year.value),
            )

        render_month(month, expanded=True)
        render_chart()

    def render_month(month: int, expanded: bool) -> None:
        detail = state["months"][month]
        holder = holders[month]

        holder.clear()

        with holder:
            if not detail:
                with ui.card().classes(card_classes("w-full p-3 casa-month")) as empty:
                    ui.label("Sem gastos").classes("text-sm casa-muted")

                sections[month] = empty
                return

            section = ui.expansion(
                value=expanded
            ).classes(card_classes("w-full casa-month")).mark(f"month-{month}")

            sections[month] = section

            with section.add_slot("header"):
                with ui.row().classes("w-full justify-between no-wrap gap-2"):
                    with ui.column().classes("gap-0"):
                        ui.label(
                            f"{month_name(month)} {detail['year']}"
                        ).classes("font-bold")
                        ui.label(
                            settlement_banner(detail)
                        )

                    ui.label(
                        format_brl(detail["total_expenses"])
                    ).classes("font-bold text-lg")

            # Charts inside closed sections would render at zero size, so build
            # the body only when the section is opened.
            built = {"done": False}

            def build_body() -> None:
                if built["done"]:
                    return

                built["done"] = True
                month_body(detail, on_ratio_saved=on_ratio_saved)

            section.on_value_change(
                lambda e: build_body() if e.value else None
            )

            if expanded:
                build_body()

    def load() -> None:
        state["months"].clear()
        sections_column.clear()
        sections.clear()
        holders.clear()

        with get_session() as db:
            months = calculate_year_months(db, int(year.value))

        for month in months:
            holders[month] = sections_column

        render_chart()


    load()


def month_body(detail: dict, on_ratio_saved) -> None:
    month, year = detail["month"], detail["year"]

    with ui.column().classes("w-full gap-3 px-3 pb-3"):
        hint, hint_classes = change_hint(detail)

        with ui.row().classes("w-full grid grid-cols-1 sm:grid-cols-3 gap-3 w-full"):
            kpi_card(
                "Total",
                format_brl(detail["total_expenses"]),
                hint,
                hint_classes,
            )
            kpi_card(
                "Variável",
                format_brl(detail["variable_total"]),
            )
            kpi_card(
                "Fixo",
                format_brl(detail["regular_total"]),
            )

        settlement_banner(detail)
        person_split(detail)

        n_categories = len(detail["variable_categories"]) + len(
            detail["regular_categories"]
        )

        with ui.card().classes(card_classes("w-full p-3 gap-1")):
            ui.label("Categorias").classes("font-bold")
            ui.echart(category_chart(detail)).classes("w-full").style(
                f"height: {max(160, 34 * n_categories + 60)}px"
            )

        with ui.card().classes(card_classes("w-full p-3 gap-2")):
            ui.label("Divisão do mês").classes("font-bold")

            with ui.row().classes("items-end gap-3"):
                fafa_pct = money_input(
                    "Fafa %",
                    format_number_br(detail["fafa_ratio"] * 100),
                ).classes("w-28").mark(f"fafa-pct-{month}")

                fefe_label = ui.label(
                    f"Fefe: {format_pct(detail['fefe_ratio'] * 100)}"
                ).classes("text-sm casa-muted mb-2")

            def update_fefe_label() -> None:
                value = parse_money(fafa_pct.value)
                fefe_label.set_text(
                    f"Fefe: {format_pct(100 - value)}"
                    if value is not None
                    else "Fefe: —"
                )

            fafa_pct.on_value_change(update_fefe_label)

            def save_ratio() -> None:
                value = parse_money(fafa_pct.value)

                if value is None or not 1 <= value <= 99:
                    ui.notify(
                        "Fafa deve estar entre 1 e 99.",
                        type="warning",
                    )
                    return

                with get_session() as db:
                    crud.set_month_ratio(db, month, year, value / 100)

                ui.notify("Divisão salva!", type="positive")
                on_ratio_saved(month)

            ui.button(
                "Salvar divisão",
                icon="save",
                on_click=save_ratio,
            ).props("unelevated no-caps").mark(f"save-ratio-{month}")