from app.balance import calculate_monthly_balance
from app.models import RegularExpense, VariableExpense


def test_monthly_balance_splits_expenses_and_calculates_settlement(db_session):
    db_session.add_all([
        VariableExpense(
            place="Mercado", day=1, month=10, year=2026,
            value=100, paid_by="FAFA", category_name="Mercado",
        ),
        RegularExpense(
            day=1, month=10, year=2026, value=50,
            paid_by="FEFE", category_name="Aluguel",
        ),
    ])
    db_session.commit()

    balance = calculate_monthly_balance(db_session, 10, 2026)

    assert balance.total_expenses == 150
    assert balance.variable_total == 100
    assert balance.regular_total == 50
    assert balance.fafa_should_pay == 100
    assert balance.fefe_should_pay == 50
    assert balance.fafa_paid == 100
    assert balance.fefe_paid == 50
    assert balance.balance == 0
