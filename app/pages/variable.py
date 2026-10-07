from datetime import date
from typing import Optional

from nicegui import app, ui

from app import crud
from app.components import date_input, money_input, month_select, year_select
from app.database import get_session
from app.formatting import (
    format_brl, format_number_br, parse_date_br, parse_money,
)
from app.models import FAFA, PAYER_LABELS, VariableExpense
from app.theme import card_classes, page_container

QUICK_VALUES = [10, 20, 50, 70, 100, 200, 250, 500]
LAST_CATEGORY_KEY = "last_variable_category"


class ExpenseForm:
    """Reused by the 'new expense' card and the edit dialog."""

    def __init__(self, categories: list[str], values: Optional[dict] = None, placeholders: list[str] = ()):
        self.values = values or {}
        self.place = ui.input(label="Local", value=self.values.get("place", "")).classes("w-full").mark("place")
        with ui.row().classes("gap-2 items-end w-full"):
            self.day = date_input("Data", value=self.values.get("date", date.today())).classes("w-full").mark("date")
            self.value = ui.number(label="Valor", value=self.values.get("value"), format="%.2f", min=0, step=0.01).classes("w-full").mark("value")
        self.placeholders = placeholders or [
            "Ex: mercado", "Ex: farmácia", "Ex: gasolina", "Ex: almoço", "Ex: presente",
        ]
        with ui.row().classes("gap-1 flex-wrap"):
            for qv in QUICK_VALUES:
                ui.button(str(qv), on_click=lambda q=qv: self.value.set_value(q)).props("flat dense no-caps").classes("text-xs")
        self.category = ui.select(categories, label="Categoria", value=self.values.get("category_name", "")).classes("w-full").mark("category")
        self.payer = ui.select(
            list(PAYER_LABELS.keys()), label="Quem pagou", value=self.values.get("paid_by", "FAFA"),
        ).classes("w-full").mark("payer")
        self.notes = ui.input(label="Observações", value=self.values.get("notes", "")).classes("w-full").mark("notes")

    def read(self) -> Optional[dict]:
        """Validate and return data after verifying the user at the first problem."""
        place = (self.place.value or "").strip()
        if not place:
            ui.notify("Preencha o local.", type="warning")
            return None
        problem = None
        if not self.value.value:
            problem = "Preencha o valor."
        elif self.value.value < 0:
            problem = "Valor deve ser maior que zero."
        elif not self.category.value:
            problem = "Selecione um grupo."
        if problem:
            ui.notify(problem, type="warning")
            return None
        return {
            "place": place,
            "date": parse_date_br(self.day.value),
            "month": self.day.value.month,
            "year": self.day.value.year,
            "value": float(self.value.value),
            "paid_by": self.payer.value,
            "category_name": self.category.value,
            "notes": (self.notes.value or "").strip() or None,
        }


def build_variable_expenses() -> None:
    today = date.today()
    with get_session() as db:
        categories = [c.name for c in crud.get_variable_categories(db)]
        top_places = crud.get_top_places(db)

    last_category = app.storage.user.get(LAST_CATEGORY_KEY)

    with page_container():
        ui.label("Gastos Variáveis").classes("casa-page-title text-2xl font-bold")
        with ui.card().classes(card_classes("w-full p-3 gap-2")):
            ui.label("Novo gasto").classes("text-lg font-bold")
            form = ExpenseForm(
                categories,
                values={"category_name": last_category if last_category in categories else None},
                placeholders=top_places[:5],
            )
            def add_expense() -> None:
                data = form.read()
                if not data:
                    return
                app.storage.user[LAST_CATEGORY_KEY] = data["category_name"]
                with get_session() as db:
                    crud.create_variable_expense(db, data)
                ui.notify("Gasto adicionado!", type="positive")
                form.place.set_value("")
                form.value.set_value(None)
                form.notes.set_value("")
                refresh_list()

            ui.button("Adicionar", icon="add", on_click=add_expense).props("unelevated no-caps size=lg").classes("w-full")

        with ui.row().classes("casa-filter gap-3 items-center w-full"):
            filter_month = month_select(today.month, on_change=lambda: refresh_list())
            filter_year = year_select(today.year, on_change=lambda: refresh_list())
            filter_payer = ui.select(
                ["Todos"] + list(PAYER_LABELS.values()),
                value="Todos", label="Quem pagou",
            ).props("dense outlined").classes("w-full sm:w-48")
            filter_payer.on_value_change(lambda _: refresh_list())

        expenses_list = ui.column().classes("w-full gap-2")

        def refresh_list() -> None:
            expenses_list.clear()
            with get_session() as db:
                expenses = crud.get_variable_expenses(
                    db, month=filter_month.value, year=int(filter_year.value),
                )
            if filter_payer.value != "Todos":
                label = filter_payer.value
                expenses = [e for e in expenses if PAYER_LABELS.get(e.paid_by) == label]
            if not expenses:
                with expenses_list:
                    ui.label("Nenhum gasto variável neste mês.").classes("casa-muted")
                return
            total = sum(e.value for e in expenses)
            total_fafa = sum(e.value for e in expenses if e.paid_by == "FAFA")
            total_fefe = sum(e.value for e in expenses if e.paid_by == "FEFE")
            with expenses_list:
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(f"Total: {format_brl(total)}").classes("font-bold")
                with ui.row().classes("gap-2 text-sm casa-muted"):
                    ui.label(f"Fafa: {format_brl(total_fafa)}")
                    ui.label(f"Fefe: {format_brl(total_fefe)}")
                ui.separator()
                for e in expenses:
                    with ui.row().classes("w-full items-center gap-3 py-2 border-b flex-wrap"):
                        with ui.column().classes("flex-1 min-w-40"):
                            with ui.row().classes("items-center gap-2"):
                                ui.label(e.place).classes("font-medium")
                                ui.badge(PAYER_LABELS.get(e.paid_by, e.paid_by)).classes("text-xs")
                            ui.label(f"{parse_date_br(e.date).strftime('%d/%m')} - {e.category_name}").classes("text-xs casa-muted")
                        if e.notes:
                            ui.label(e.notes).classes("text-xs casa-muted truncate w-full")
                        ui.label(format_brl(e.value)).classes("font-bold whitespace-nowrap")
                        ui.button(icon="edit", on_click=lambda exp=e: open_edit_expense(exp)).props("flat dense round").classes("text-primary")
                        ui.button(icon="delete", on_click=lambda exp=e: delete_expense(exp.id)).props("flat dense round").classes("text-negative")

        def open_edit_expense(exp: VariableExpense) -> None:
            with get_session() as db:
                exp = db.get(VariableExpense, exp.id)
                if exp is None:
                    ui.notify("Gasto não encontrado.", type="negative")
                    return
                data = {
                    "place": exp.place,
                    "date": parse_date_br(exp.date),
                    "value": exp.value,
                    "paid_by": exp.paid_by,
                    "category_name": exp.category_name,
                    "notes": exp.notes,
                }
                edit_form = ExpenseForm(categories, values=data)

            dialog = ui.dialog()
            with dialog, ui.card().classes(card_classes("w-full max-w-lg p-4 gap-2")):
                ui.label("Editar gasto").classes("text-lg font-bold")
                edit_form.place.move(dialog)
                # Note: The code in the image moves 'place' but the
                # rest of the form elements would likely be moved
                # similarly, or the layout is handled differently.
                # The visible line is:
                # edit_form.place.move(dialog)

                def save_edit() -> None:
                    data = edit_form.read()
                    if not data:
                        return
                    with get_session() as db:
                        crud.update_variable_expense(db, exp.id, data)
                        dialog.close()
                        refresh_list()
                        ui.notify("Gasto atualizado!", type="positive")

                def confirm_delete() -> None:
                    with get_session() as db:
                        crud.delete_variable_expense(db, exp.id)
                        dialog.close()
                        refresh_list()
                        ui.notify("Gasto excluído.", type="positive")

                with ui.row().classes("w-full justify-between items-center mt-2"):
                    ui.button("Excluir", icon="delete", on_click=confirm_delete).props("flat no-caps color=negative")
                    with ui.row().classes("gap-2"):
                        ui.button("Cancelar", on_click=dialog.close).props("flat no-caps")
                        ui.button("Salvar", icon="save", on_click=save_edit).props("unelevated no-caps")

        def delete_expense(expense_id: int) -> None:
            with get_session() as db:
                crud.delete_variable_expense(db, expense_id)
            ui.notify("Gasto excluído.", type="positive")
            refresh_list()

        refresh_list()


def build_variable_income() -> None:
    today = date.today()
    with get_session() as db:
        categories = [c.name for c in crud.get_variable_categories(db)]

    with page_container():
        ui.label("Rendas Variáveis").classes("casa-page-title text-2xl font-bold")
        with ui.card().classes(card_classes("w-full p-3 gap-2")):
            ui.label("Nova renda").classes("text-lg font-bold")
            place = ui.input("Descrição").classes("w-full")
            with ui.row().classes("w-full gap-2"):
                date_in = date_input("Data", value=today).classes("flex-1")
                value_in = money_input("Valor").classes("flex-1")
            category = ui.select(categories, label="Categoria", value=last_category if last_category in categories else None).classes("w-full")
            payer = ui.select(list(PAYER_LABELS.keys()), label="Quem recebeu", value="FAFA").classes("w-full")
            notes = ui.input("Observações").classes("w-full")
            # Note: There is a visual artifact or partial code
            # for the 'Adicionar' button here.

        with ui.row().classes("casa-filter gap-3 items-center w-full"):
            filter_month = month_select(today.month, on_change=lambda: refresh_list())
            filter_year = year_select(today.year, on_change=lambda: refresh_list())
            filter_payer = ui.select(
                ["Todos"] + list(PAYER_LABELS.values()),
                value="Todos", label="Quem recebeu",
            ).props("dense outlined").classes("w-full sm:w-48")
            filter_payer.on_value_change(lambda _: refresh_list())

        income_list = ui.column().classes("w-full gap-2")

        def refresh_list() -> None:
            income_list.clear()
            with get_session() as db:
                incomes = crud.get_variable_incomes(
                    db, month=filter_month.value, year=int(filter_year.value),
                )
            # Filtering logic is implied here...
            if not incomes:
                with income_list:
                    ui.label("Nenhuma renda variável neste mês.").classes("casa-muted")
                return
            total = sum(i.value for i in incomes)
            # More list rendering logic...

        def open_edit_income(inc: VariableIncome) -> None:
            # Dialog setup logic...
            pass

        def delete_income(income_id: int) -> None:
            with get_session() as db:
                crud.delete_variable_income(db, income_id)
            ui.notify("Renda excluída.", type="positive")
            refresh_list()

        refresh_list()