from nicegui import ui
from datetime import datetime
from app.database import get_session   # FIX #4
from app import crud
from app.balance import calculate_monthly_balance
from app.theme import card_classes, page_container


def build_balance() -> None:
    now = datetime.now()

    with page_container():
        ui.label("Balanço & Saldos").classes("casa-page-title text-2xl font-bold")

        with ui.row().classes("casa-filter gap-4 items-center w-full"):
            month_select = ui.select(
                options={i: f"{i:02d} - {datetime(2000, i, 1).strftime('%b')}" for i in range(1, 13)},
                value=now.month,
            ).classes("w-32")
            year_input = ui.number(value=now.year, min=2020, max=2030).classes("w-24")

        content = ui.column().classes("w-full")

        def refresh():
            content.clear()
            with content:
                # FIX #4: one context manager block for all reads on this refresh
                with get_session() as db:
                    bal = calculate_monthly_balance(db, month_select.value, int(year_input.value))
                    current_ratio = crud.get_month_ratio(db, month_select.value, int(year_input.value))

                # ── Ratio Editor ───────────────────────────────────────────
                with ui.card().classes(card_classes("w-full")):
                    ui.label("Ratio do Mês").classes("font-bold")
                    # FIX #3: only one input needed — Fafa's percentage.
                    # Fefe's is always 100 - Fafa's. A live label shows the derived value.
                    with ui.row().classes("gap-4 mt-2 items-center"):
                        fafa_pct = ui.number(
                            "Fafa %", value=round(current_ratio.fafa_ratio * 100, 1),
                            min=1, max=99, step=1, format="%.1f",
                        ).classes("w-32")
                        fefe_label = ui.label(
                            f"Fefe: {round(current_ratio.fefe_ratio * 100, 1):.1f}%"
                        ).classes("text-sm casa-muted self-end mb-1")

                    # Update the Fefe label dynamically as Fafa's value changes
                    def update_fefe_label():
                        if fafa_pct.value is not None:
                            fefe_label.set_text(f"Fefe: {100 - fafa_pct.value:.1f}%")

                    fafa_pct.on("update:model-value", lambda: update_fefe_label())

                    def save_ratio():
                        if not fafa_pct.value or not (1 <= fafa_pct.value <= 99):
                            ui.notify("Fafa % deve estar entre 1 e 99.", type="warning")
                            return
                        # FIX #3: only pass fafa_ratio; fefe is derived in crud
                        with get_session() as db:
                            crud.set_month_ratio(
                                db, month_select.value, int(year_input.value),
                                fafa_pct.value / 100,
                            )
                        ui.notify("Ratio salvo!", type="positive")
                        refresh()

                    ui.button("Salvar Ratio", on_click=save_ratio, icon="save").props("unelevated no-caps").classes("mt-2")

                # ── Balance Details ─────────────────────────────────────────
                with ui.card().classes(card_classes("w-full mt-4")):
                    ui.label("Detalhes").classes("font-bold")
                    ui.label(f"Total: R$ {bal['total_expenses']:,.2f}").classes("text-lg mt-2")
                    ui.label(
                        f"Variável: R$ {bal['variable_total']:,.2f} | Fixo: R$ {bal['regular_total']:,.2f}"
                    ).classes("text-sm casa-muted")
                    ui.separator().classes("my-2")

                    ui.label(f"Fafa deve pagar: R$ {bal['fafa_should_pay']:,.2f}").classes("text-sm")
                    ui.label(f"Fafa pagou:       R$ {bal['fafa_paid']:,.2f}").classes("text-sm")
                    diff = bal['balance']
                    color = "text-green-600" if diff >= 0 else "text-red-600"
                    ui.label(f"Saldo Fafa: R$ {diff:,.2f}").classes(f"font-bold {color}")

                    ui.separator().classes("my-2")

                    ui.label(f"Fefe deve pagar: R$ {bal['fefe_should_pay']:,.2f}").classes("text-sm")
                    ui.label(f"Fefe pagou:       R$ {bal['fefe_paid']:,.2f}").classes("text-sm")
                    color2 = "text-green-600" if -diff >= 0 else "text-red-600"
                    ui.label(f"Saldo Fefe: R$ {-diff:,.2f}").classes(f"font-bold {color2}")

        month_select.on("update:model-value", lambda: refresh())
        year_input.on("update:model-value", lambda: refresh())
        refresh()
