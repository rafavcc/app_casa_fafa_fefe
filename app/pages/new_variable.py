# app/pages/variable.py
from nicegui import ui
from datetime import datetime
from sqlalchemy import func
from app.database import get_session
from app.models import VariableExpense
from app import crud

# Guarda o último grupo usado durante a sessão
_last_category: str | None = None


def build_variable_expenses() -> None:
    global _last_category
    now = datetime.now()

    with ui.column().classes("w-full max-w-3xl mx-auto p-4"):
        ui.label("💸 Gastos Variáveis").classes("text-2xl font-bold")

        with ui.card().classes("w-full mt-4"):
            ui.label("Novo Gasto").classes("text-lg font-bold mb-2")

            # Busca categorias para o dropdown de Grupo
            with get_session() as db:
                categories = [c.name for c in crud.get_variable_categories(db)]

            # ── Local + botões de atalho (top 5) ─────────────────────
            with ui.row().classes("gap-2 items-end w-full"):
                place = ui.input("Local").classes("flex-1")
                place_shortcuts = ui.row().classes("gap-1 items-end")

            # ── Dia / Mês / Ano ───────────────────────────────────────
            with ui.row().classes("gap-2"):
                day   = ui.number("Dia", value=now.day, min=1, max=31).classes("w-20")
                month = ui.select(
                    options={i: f"{i:02d}" for i in range(1, 13)},
                    value=now.month,
                ).classes("w-20")
                year  = ui.number("Ano", value=now.year, min=2020, max=2030).classes("w-24")

            # ── Valor + botões de atalho ──────────────────────────────
            with ui.row().classes("gap-2 items-end"):
                value_input = ui.number(
                    "Valor (R$)", min=0.01, step=1.0, format="%.2f"
                ).classes("w-48")
                for quick in [10, 50, 100]:
                    def make_value_setter(v):
                        return lambda: value_input.set_value(float(v))
                    ui.button(
                        f"R${quick}", on_click=make_value_setter(quick)
                    ).classes("mb-1").props("flat dense color=grey-7")

            # ── Grupo (pré-seleciona o último usado) ──────────────────
            category_select = ui.select(
                options=categories,
                label="Grupo",
                value=_last_category if _last_category in categories else None,
            ).classes("w-48")

            # ── Pago por ──────────────────────────────────────────────
            paid_by_value: dict = {"v": None}

            with ui.row().classes("gap-2 items-center mt-1"):
                ui.label("Pago por").classes("text-sm text-gray-500")
                btn_fafa = ui.button("FAFA").props("outline")
                btn_fefe = ui.button("FEFE").props("outline")

                def select_fafa():
                    paid_by_value["v"] = "FAFA"
                    btn_fafa.props("outline color=blue")
                    btn_fefe.props("outline color=grey")

                def select_fefe():
                    paid_by_value["v"] = "FEFE"
                    btn_fefe.props("outline color=red")
                    btn_fafa.props("outline color=grey")

                btn_fafa.on_click(select_fafa)
                btn_fefe.on_click(select_fefe)

            notes = ui.input("Notas").classes("w-full mt-2")

            # ── Função: atualiza botões de atalho do Local ────────────
            def refresh_place_shortcuts():
                """Rebuilda os botões com os 5 locais mais inseridos."""
                place_shortcuts.clear()
                with place_shortcuts:
                    with get_session() as db:
                        top_places = db.query(
                            VariableExpense.place,
                            func.count(VariableExpense.place).label("total")
                        ).group_by(VariableExpense.place)\
                         .order_by(func.count(VariableExpense.place).desc())\
                         .limit(5).all()

                    for row in top_places:
                        def make_place_setter(p):
                            return lambda: place.set_value(p)
                        ui.button(row.place, on_click=make_place_setter(row.place))\
                          .classes("mb-1").props("flat dense color=grey-7")

            # ── Adicionar despesa ─────────────────────────────────────
            def add_expense():
                global _last_category

                if not place.value or not place.value.strip():
                    ui.notify("Por favor, preencha o local.", type="warning")
                    return
                if not category_select.value:
                    ui.notify("Selecione uma categoria.", type="warning")
                    return
                if not paid_by_value["v"]:
                    ui.notify("Selecione quem pagou (FAFA ou FEFE).", type="warning")
                    return
                if not value_input.value or value_input.value <= 0:
                    ui.notify("Valor deve ser maior que zero.", type="warning")
                    return

                with get_session() as db:
                    crud.create_variable_expense(db, {
                        "place":         place.value.strip(),
                        "day":           int(day.value),
                        "month":         month.value,
                        "year":          int(year.value),
                        "value":         float(value_input.value),
                        "paid_by":       paid_by_value["v"],
                        "category_name": category_select.value,
                        "notes":         notes.value.strip() if notes.value else None,
                    })

                _last_category = category_select.value

                ui.notify("✅ Adicionado!", type="positive")
                place.set_value("")
                value_input.set_value(None)
                notes.set_value("")
                paid_by_value["v"] = None
                btn_fafa.props("outline color=primary")
                btn_fefe.props("outline color=primary")

                refresh_list()  # atualiza lista e atalhos do Local

            ui.button("+ Adicionar", on_click=add_expense).classes("mt-3 bg-blue-600 text-white")

        # ── Filtro ────────────────────────────────────────────────────
        with ui.row().classes("gap-4 mt-4 items-center"):
            ui.label("Filtrar:").classes("text-sm")
            filter_month = ui.select(
                options={i: f"{i:02d}" for i in range(1, 13)},
                value=now.month,
            ).classes("w-20")
            filter_year = ui.number(value=now.year, min=2020, max=2030).classes("w-24")

        expense_list = ui.column().classes("w-full mt-2")

        # ── Lista de despesas ─────────────────────────────────────────
        def refresh_list():
            expense_list.clear()
            with expense_list:
                with get_session() as db:
                    expenses = crud.get_variable_expenses(
                        db, month=filter_month.value, year=int(filter_year.value)
                    )

                if not expenses:
                    ui.label("Nenhum gasto este mês.").classes("text-gray-500 mt-4")
                else:
                    total = 0
                    for e in expenses:
                        total += e.value
                        with ui.card().classes("w-full"):
                            with ui.row().classes("justify-between items-center"):
                                with ui.column():
                                    ui.label(f"{e.category_name} — {e.place}").classes("font-bold")
                                    ui.label(f"Dia {e.day} — Pago por {e.paid_by}").classes("text-sm text-gray-500")
                                    if e.notes:
                                        ui.label(e.notes).classes("text-xs text-gray-400")
                                ui.label(f"R$ {e.value:,.2f}").classes("text-lg font-bold text-blue-600")
                    ui.label(f"Total: R$ {total:,.2f}").classes("text-lg font-bold mt-2")

            # Atualiza os atalhos do Local junto com a lista
            refresh_place_shortcuts()

        filter_month.on("update:model-value", lambda: refresh_list())
        filter_year.on("update:model-value", lambda: refresh_list())

        # Carga inicial
        refresh_place_shortcuts()
        refresh_list()