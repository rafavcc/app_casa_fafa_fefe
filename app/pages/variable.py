# app/pages/variable.py
from nicegui import ui
from datetime import datetime
from app.database import get_session
from app import crud
from app.models import VariableExpense
from sqlalchemy import func
from app.theme import card_classes, page_container

_last_category: str | None = None


def build_variable_expenses() -> None:
    global _last_category
    now = datetime.now()

    with page_container():
        ui.label("Gastos Variáveis").classes("casa-page-title text-2xl font-bold")

        with ui.card().classes(card_classes("w-full")):
            ui.label("Novo Gasto").classes("text-lg font-bold mb-2")

            with get_session() as db:
                categories = [c.name for c in crud.get_variable_categories(db)]

            # ── Local (campo em cima, atalhos embaixo em botões) ──────
            place = ui.input("Local").classes("w-full")
            place_shortcuts = ui.row().classes("gap-1 flex-wrap mt-1")

            # ── Dia / Mês / Ano ───────────────────────────────────────
            with ui.row().classes("gap-2 mt-2"):
                day = ui.select(
                    options={i: f"{i:02d}" for i in range(1, 32)},
                    value=now.day,
                    label="Dia",
                ).classes("w-24")
                month = ui.select(
                    options={i: f"{i:02d}" for i in range(1, 13)},
                    value=now.month,
                    label="Mês",
                ).classes("w-24")
                year = ui.select(
                    options={2025: "2025", 2026: "2026"},
                    value=now.year if now.year in (2025, 2026) else 2026,
                    label="Ano",
                ).classes("w-24")

            # ── Valor + botões de atalho ──────────────────────────────
            with ui.column().classes("w-full mt-2"):
                value_input = ui.number(
                    "Valor (R$)", min=0.01, step=1.0, format="%.2f"
                ).classes("w-full")
                with ui.row().classes("gap-1 flex-wrap mt-1"):
                    for quick in [10, 20, 50, 70, 100, 200, 250, 500]:
                        def make_setter(v):
                            return lambda: value_input.set_value(float(v))
                        ui.button(
                            f"R${quick}", on_click=make_setter(quick)
                        ).props("flat dense no-caps")

            # ── Grupo ─────────────────────────────────────────────────
            category_select = ui.select(
                options=categories,
                label="Grupo",
                value=_last_category if _last_category in categories else None,
            ).classes("w-full mt-2")

            # ── Pago por ──────────────────────────────────────────────
            paid_by_value: dict = {"v": None}

            with ui.row().classes("gap-2 items-center mt-2"):
                ui.label("Pago por").classes("text-sm casa-muted")
                btn_fafa = ui.button("FAFA").props("outline").classes("w-24")
                btn_fefe = ui.button("FEFE").props("outline").classes("w-24")

                def select_fafa():
                    paid_by_value["v"] = "FAFA"
                    btn_fafa.props("color=blue")
                    btn_fefe.props("color=grey outline")

                def select_fefe():
                    paid_by_value["v"] = "FEFE"
                    btn_fefe.props("color=red")
                    btn_fafa.props("color=grey outline")

                btn_fafa.on_click(select_fafa)
                btn_fefe.on_click(select_fefe)

            notes = ui.input("Notas").classes("w-full mt-2")

            # ── Função: atualiza botões de atalho do Local ────────────
            def refresh_place_shortcuts():
                place_shortcuts.clear()
                with place_shortcuts:
                    with get_session() as db:
                        top_places = db.query(
                            VariableExpense.place,
                            func.count(VariableExpense.place).label("total")
                        ).group_by(VariableExpense.place) \
                         .order_by(func.count(VariableExpense.place).desc()) \
                         .limit(5).all()

                    for row in top_places:
                        def make_place_setter(p):
                            return lambda: place.set_value(p)
                        ui.button(row.place, on_click=make_place_setter(row.place)) \
                          .props("flat dense no-caps")

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
                        "month":         int(month.value),
                        "year":          int(year.value),
                        "value":         float(value_input.value),
                        "paid_by":       paid_by_value["v"],
                        "category_name": category_select.value,
                        "notes":         notes.value.strip() if notes.value else None,
                    })

                _last_category = category_select.value

                ui.notify("Adicionado!", type="positive")
                place.set_value("")
                value_input.set_value(None)
                notes.set_value("")
                paid_by_value["v"] = None
                btn_fafa.props("outline color=primary")
                btn_fefe.props("outline color=primary")
                refresh_list()

            ui.button("Adicionar", icon="add", on_click=add_expense).props("unelevated no-caps").classes("mt-3")

        # ── Delete por ID ─────────────────────────────────────────────
        with ui.row().classes("casa-filter gap-2 items-center w-full"):
            delete_id = ui.number("Deletar ID", min=1, step=1).classes("w-32")
            def delete_expense():
                if not delete_id.value:
                    ui.notify("Digite um ID.", type="warning")
                    return
                with get_session() as db:
                    deleted = crud.delete_variable_expense(db, int(delete_id.value))
                if deleted:
                    ui.notify(f"ID {int(delete_id.value)} deletado.", type="positive")
                    delete_id.set_value(None)
                    refresh_list()
                else:
                    ui.notify(f"ID {int(delete_id.value)} não encontrado.", type="negative")
            ui.button("Deletar", icon="delete", on_click=delete_expense).props("color=red outline no-caps")

        # ── Filtro ────────────────────────────────────────────────────
        with ui.row().classes("casa-filter gap-4 items-center w-full"):
            ui.label("Filtrar:").classes("text-sm")
            filter_month = ui.select(
                options={i: f"{i:02d}" for i in range(1, 13)},
                value=now.month,
            ).classes("w-20")
            filter_year = ui.select(
                options={2025: "2025", 2026: "2026"},
                value=now.year if now.year in (2025, 2026) else 2026,
            ).classes("w-20")

        expense_list = ui.column().classes("w-full")

        # ── Tabela de despesas ────────────────────────────────────────
        def refresh_list():
            expense_list.clear()
            with expense_list:
                with get_session() as db:
                    expenses = crud.get_variable_expenses(
                        db, month=filter_month.value, year=int(filter_year.value)
                    )

                if not expenses:
                    ui.label("Nenhum gasto este mês.").classes("casa-muted mt-4")
                else:
                    # Header
                    with ui.row().classes("casa-card w-full px-2 py-1 font-bold text-xs gap-2"):
                        ui.label("ID").classes("w-8")
                        ui.label("Dia").classes("w-8")
                        ui.label("Local").classes("flex-1")
                        ui.label("Grupo").classes("w-20")
                        ui.label("Quem").classes("w-10")
                        ui.label("Valor").classes("w-20 text-right")

                    total = 0
                    for e in expenses:
                        total += e.value
                        with ui.row().classes("w-full border-b px-2 py-1 text-sm gap-2 items-center"):
                            ui.label(str(e.id)).classes("w-8 casa-muted")
                            ui.label(f"{e.day:02d}").classes("w-8")
                            with ui.column().classes("flex-1 gap-0"):
                                ui.label(e.place).classes("font-medium leading-tight")
                                if e.notes:
                                    ui.label(e.notes).classes("text-xs casa-muted leading-tight")
                            ui.label(e.category_name).classes("w-20 text-xs casa-muted")
                            ui.label(e.paid_by).classes("w-10 text-xs")
                            ui.label(f"R${e.value:,.2f}").classes("w-20 text-right font-bold text-blue-600")

                    with ui.row().classes("w-full px-2 py-1 font-bold text-sm gap-2 mt-1"):
                        ui.label("Total").classes("flex-1")
                        ui.label(f"R${total:,.2f}").classes("w-20 text-right text-blue-700")

            refresh_place_shortcuts()

        filter_month.on("update:model-value", lambda: refresh_list())
        filter_year.on("update:model-value", lambda: refresh_list())
        refresh_place_shortcuts()
        refresh_list()
