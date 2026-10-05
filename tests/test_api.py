import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.main import (
    add_variable_expense,
    health,
    list_variable_expenses,
    remove_variable_expense,
)
from app.schemas import VariableExpenseCreate


def test_variable_expense_can_be_created_listed_and_deleted(db_session):
    data = VariableExpenseCreate(
        place="Supermercado",
        day=4,
        month=10,
        year=2026,
        value=120.5,
        paid_by="FAFA",
        category_name="Mercado",
        notes="  compra da semana  ",
    )

    expense = add_variable_expense(data, db_session)

    assert expense.place == "Supermercado"
    assert expense.notes == "compra da semana"
    assert list_variable_expenses(10, 2026, None, db_session) == [expense]

    assert remove_variable_expense(expense.id, db_session) == {"ok": True}
    assert list_variable_expenses(10, 2026, None, db_session) == []


def test_variable_expense_rejects_invalid_payer():
    with pytest.raises(ValidationError):
        VariableExpenseCreate(
            place="Supermercado",
            day=4,
            month=10,
            year=2026,
            value=120.5,
            paid_by="OTHER",
            category_name="Mercado",
        )


def test_deleting_missing_variable_expense_returns_not_found(db_session):
    with pytest.raises(HTTPException) as error:
        remove_variable_expense(999, db_session)

    assert error.value.status_code == 404
    assert error.value.detail == "Expense not found"


def test_health_endpoint_reports_server_status():
    assert health() == {"status": "ok"}
