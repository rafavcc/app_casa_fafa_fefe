from nicegui import ui
from app.balance import calculate_monthly_balance
from app.database import get_session
from datetime import datetime
from app.theme import card_classes, page_container


def build_home() -> None:
    now = datetime.now()

    with page_container():
        ui.label("Casa Fafa & Fefe").classes("casa-page-title text-2xl font-bold")

        with ui.row().classes("casa-filter gap-4 items-center w-full"):
            month_select = ui.select(
                options={i: f"{i:02d} - {datetime(2000, i, 1).strftime('%b')}" for i in range(1, 13)},
                value=now.month,
            ).classes("w-32")
            year_input = ui.number(value=now.year, min=2020, max=2030).classes("w-24")
            ui.button("Ver", icon="bar_chart", on_click=lambda: refresh()).props("unelevated no-caps")

        balance_container = ui.column().classes("w-full")

        def refresh():
            balance_container.clear()
            with balance_container:
                # FIX #4: context manager guarantees session is closed even on error
                with get_session() as db:
                    bal = calculate_monthly_balance(db, month_select.value, int(year_input.value))

                with ui.row().classes("gap-4 w-full"):
                    with ui.card().classes(card_classes("flex-1")):
                        ui.label("Total").classes("text-sm casa-muted")
                        ui.label(f"R$ {bal['total_expenses']:,.2f}").classes("text-2xl font-bold")
                    with ui.card().classes(card_classes("flex-1")):
                        ui.label("Fafa deve pagar").classes("text-sm casa-muted")
                        ui.label(f"R$ {bal['fafa_should_pay']:,.2f}").classes("text-2xl font-bold")
                    with ui.card().classes(card_classes("flex-1")):
                        ui.label("Fefe deve pagar").classes("text-sm casa-muted")
                        ui.label(f"R$ {bal['fefe_should_pay']:,.2f}").classes("text-2xl font-bold")

                with ui.row().classes("gap-4 w-full mt-4"):
                    with ui.card().classes(card_classes("flex-1")):
                        ui.label(f"Fafa pagou: R$ {bal['fafa_paid']:,.2f}").classes("text-sm")
                        color = "text-green-600" if bal['balance'] >= 0 else "text-red-600"
                        ui.label(f"Diferença: R$ {bal['balance']:,.2f}").classes(f"font-bold {color}")
                    with ui.card().classes(card_classes("flex-1")):
                        ui.label(f"Fefe pagou: R$ {bal['fefe_paid']:,.2f}").classes("text-sm")
                        diff = -bal['balance']
                        color = "text-green-600" if diff >= 0 else "text-red-600"
                        ui.label(f"Diferença: R$ {diff:,.2f}").classes(f"font-bold {color}")

                with ui.card().classes(card_classes("w-full mt-4")):
                    if bal['balance'] > 0:
                        ui.label(f"Fefe deve R$ {bal['balance']:,.2f} para Fafa").classes("text-lg")
                    elif bal['balance'] < 0:
                        ui.label(f"Fafa deve R$ {-bal['balance']:,.2f} para Fefe").classes("text-lg")
                    else:
                        ui.label("Contas iguais este mês!").classes("text-lg text-green-600")

                ui.label(
                    f"Ratio: Fafa {bal['fafa_ratio']*100:.1f}% / Fefe {bal['fefe_ratio']*100:.1f}%"
                ).classes("text-sm casa-muted mt-2")

        refresh()
