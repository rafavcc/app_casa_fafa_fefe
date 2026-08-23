from nicegui import ui
from datetime import datetime
from app.database import get_session   # FIX #4
from app import crud
from app.theme import card_classes, page_container

def build_regular_expenses() -> None:
    now = datetime.now()

    with page_container():
        ui.label("Gastos Fixos").classes("casa-page-title text-2xl font-bold")

        with ui.row().classes("casa-filter gap-4 items-center w-full"):
            month_select = ui.select(
                options={i: f"{i:02d} - {datetime(2000, i, 1).strftime('%b')}" for i in range(1, 13)},
                value=now.month,
            ).classes("w-32")
            year_input = ui.number(value=now.year, min=2020, max=2030).classes("w-24")

        form_container = ui.column().classes("w-full")
        result_label = ui.label("")

        def build_form():
            form_container.clear()

            # FIX #4: context manager
            with get_session() as db:
                categories = crud.get_regular_categories(db)
                existing = {
                    e.category_name: e
                    for e in crud.get_regular_expenses(
                        db, month=month_select.value, year=int(year_input.value)
                    )
                }

            inputs = {}

            with form_container:          # ← esta linha estava faltando

                with ui.card().classes(card_classes("w-full")):
                    with ui.row().classes("font-bold text-sm border-b pb-2 w-full"):
                        ui.label("Categoria").classes("flex-1")
                        ui.label("Dia").classes("w-16")
                        ui.label("Valor (R$)").classes("w-32")
                        ui.label("Pago por").classes("w-24")

                    for cat in categories:
                        exp = existing.get(cat.name)
                        with ui.row().classes("items-center gap-2 py-1 w-full"):
                            ui.label(cat.name).classes("flex-1 text-sm")
                            day_input = ui.number(
                                value=exp.day if exp else 15, min=1, max=31
                            ).classes("w-16").props("dense")
                            value_input = ui.number(
                                value=exp.value if exp else 0.0, min=0.0, step=1.0, format="%.2f"
                            ).classes("w-32").props("dense")
                            paid_input = ui.select(
                                options=["FAFA", "FEFE"],
                                value=exp.paid_by if exp else "FAFA",
                            ).classes("w-24").props("dense")
                            inputs[cat.name] = (day_input, value_input, paid_input)

                    def save_all():
                        # FIX #4: context manager
                        with get_session() as db:
                            for cat_name, (day_in, val_in, paid_in) in inputs.items():
                                if val_in.value and val_in.value > 0:
                                    crud.upsert_regular_expense(db, {
                                        "day": int(day_in.value),
                                        "month": month_select.value,
                                        "year": int(year_input.value),
                                        "value": float(val_in.value),
                                        "paid_by": paid_in.value,
                                        "category_name": cat_name,
                                    })
                        result_label.set_text("✅ Salvo!")
                        result_label.classes("text-green-600 mt-2")

                    with ui.row().classes("gap-2 mt-4"):
                        ui.button("Salvar Tudo", on_click=save_all, icon="save").props("unelevated no-caps")
                        ui.button("Recarregar", on_click=build_form, icon="refresh").props("flat no-caps")

                    existing_values = [v for v in existing.values() if v and v.value]
                    if existing_values:
                        total = sum(v.value for v in existing_values)
                        ui.label(f"Total: R$ {total:,.2f}").classes("text-lg font-bold mt-2")

        month_select.on("update:model-value", lambda: build_form())
        year_input.on("update:model-value", lambda: build_form())
        build_form()
