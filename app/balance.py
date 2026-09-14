from sqlalchemy.orm import Session
from dataclasses import dataclass
from app.crud import get_month_totals, get_month_ratio
from app.models import FAFA, FEFE

def money (value: float) -> float:
    return round(value, 2)

@dataclass(frozen=True, slots = True)
class MonthlyBalanceResult:
    month: int
    year: int
    total_expenses: float
    variable_total: float
    regular_total : float
    fafa_ratio: float
    fefe_ratio: float
    fafa_should_pay: float
    fefe_should_pay: float
    fafa_paid: float
    fefe_paid: float
    balance: float

    @property
    def debtor(self) -> str | None:
        '''
        Who still owes money, or None when no one owes
        '''
        if self.balance > 0:
            return FEFE
        if self.balance < 0:
            return FAFA
        return None

    @property
    def creditor(self) -> str | None:
        return FAFA if self.balance > 0 else FEFE if self.balance < 0 else None

    @property
    def settlement(self) -> float:
        return abs(self.balance)
    
def calculate_monthly_balance(db: Session, month: int, year: int) -> MonthlyBalanceResult:
    totals = get_month_totals(db, month, year)
    ratio = get_month_ratio(db, month, year)

    total = totals.total
    fafa_should = money(total * ratio.fafa_ratio)
    fefe_should = money(total * ratio.fefe_ratio)

    balance = totals["fafa_paid"] - fafa_should