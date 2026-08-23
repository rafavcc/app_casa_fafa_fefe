from sqlalchemy.orm import Session
from app.crud import get_month_totals, get_month_ratio

def calculate_monthly_balance(db: Session, month: int, year: int) -> dict:
    totals = get_month_totals(db, month, year)
    ratio = get_month_ratio(db, month, year)

    total = totals["variable_total"] + totals["regular_total"]
    fafa_should = total * ratio.fafa_ratio
    fefe_should = total * ratio.fefe_ratio

    balance = totals["fafa_paid"] - fafa_should

    return {
        "month": month,
        "year": year,
        "total_expenses": round(total, 2),
        "variable_total": round(totals["variable_total"], 2),
        "regular_total": round(totals["regular_total"], 2),
        "fafa_ratio": round(ratio.fafa_ratio, 4),
        "fefe_ratio": round(ratio.fefe_ratio, 4),   # derived via @property
        "fafa_should_pay": round(fafa_should, 2),
        "fefe_should_pay": round(fefe_should, 2),
        "fafa_paid": round(totals["fafa_paid"], 2),
        "fefe_paid": round(totals["fefe_paid"], 2),
        "balance": round(balance, 2),
    }