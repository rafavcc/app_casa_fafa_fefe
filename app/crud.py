from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from app.models import (User, VariableCategory, RegularCategory, VariableExpense, RegularExpense, 
MonthRatio)

def get_users(db: Session) -> List[User]:
    return db.query(User).all()

def create_user(db: Session, name : str, full_name = None) -> User:
    user = User(name = name, full_name = full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_variable_categories(db: Session) -> List[VariableCategory]:
    return db.query(VariableCategory).all()

def create_variable_category(db: Session, name: str) -> VariableCategory:
    cat = VariableCategory(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def get_regular_categories(db: Session) -> List[RegularCategory]:
    return db.query(RegularCategory).all()

def create_regular_category(db: Session, name: str) -> RegularCategory:
    cat = RegularCategory(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def create_variable_expense(db: Session, data: dict) -> VariableExpense:
    expense = VariableExpense(**data)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

def get_variable_expenses(
    db: Session,
    month: Optional[str] = None, 
    year: Optional[str] = None, 
    category: Optional[str] = None) -> List[VariableExpense]:
    q = db.query(VariableExpense)
    if month:
        q = q.filter(VariableExpense.month == month)
    if year:
        q = q.filter(VariableExpense.year == year)
    if category:
        q = q.filter(VariableExpense.category_name == category)
    return q.order_by(VariableExpense.created_at.desc()).all()

def delete_variable_expense(db: Session, expense_id: int) -> bool:
    expense = db.query(VariableExpense).filter(VariableExpense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
        return True
    return False

def create_regular_expense(db: Session, data: dict) -> RegularExpense:
    expense = RegularExpense(**data)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

def get_regular_expenses(db: Session, 
    month: Optional[int] = None,
    year: Optional[int] = None,
    category: Optional[str] = None)-> List[RegularExpense]:
    q = db.query(RegularExpense)
    if month:
        q = q.filter(RegularExpense.month == month)
    if year:
        q = q.filter(RegularExpense.year == year)
    if category:
        q = q.filter(RegularExpense.category_name == category)
    return q.order_by(RegularExpense.created_at.desc()).all()

def upsert_regular_expense(db: Session, data: dict) -> RegularExpense:
    """
    Create or update a regular expense for a given month/year/category.

    'Upsert' = UPDATE if exists, INSERT if not.
    Because regular expenses have a unique constraint on (month, year, category_name),
    inserting twice for the same category+month would crash without this logic.
    """
    existing = db.query(RegularExpense).filter(
        RegularExpense.month == data["month"],
        RegularExpense.year == data["year"],
        RegularExpense.category_name == data["category_name"],
    ).first()

    if existing:
        # setattr(obj, "field", value) is the same as obj.field = value
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        return create_regular_expense(db, data)

def autofill_current_month_regular_expenses(
    db: Session,
    today: Optional[date] = None,
) -> int:
    """
    Copy last month's regular expenses into the current month when missing.

    Existing current-month rows with value > 0 are treated as manually filled
    and are never changed. The copy is done per category, so one filled category
    does not prevent another empty category from being copied.
    """
    today = today or date.today()
    current_month = today.month
    current_year = today.year

    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year

    previous_expenses = db.query(RegularExpense).filter(
        RegularExpense.month == previous_month,
        RegularExpense.year == previous_year,
        RegularExpense.value > 0,
    ).all()

    if not previous_expenses:
        return 0

    current_by_category = {
        expense.category_name: expense
        for expense in db.query(RegularExpense).filter(
            RegularExpense.month == current_month,
            RegularExpense.year == current_year,
        ).all()
    }

    copied = 0
    for previous in previous_expenses:
        current = current_by_category.get(previous.category_name)
        if current and current.value > 0:
            continue

        data = {
            "day": previous.day,
            "month": current_month,
            "year": current_year,
            "value": previous.value,
            "paid_by": previous.paid_by,
            "category_name": previous.category_name,
            "notes": previous.notes,
        }

        if current:
            for key, value in data.items():
                setattr(current, key, value)
        else:
            db.add(RegularExpense(**data))
        copied += 1

    if copied:
        db.commit()

    return copied
    
def delete_regular_expense(db: Session, expense_id : int) -> bool:
    expense = db.query(RegularExpense).filter(RegularExpense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
        return True
    return False

def get_month_ratio(db: Session, month : int, year : int) -> MonthRatio:
    ratio = db.query(MonthRatio).filter(MonthRatio.month == month, MonthRatio.year == year).first()

    if ratio:
        return ratio
    return MonthRatio(month=month, year = year, fafa_ratio = 2/3)
                      
def set_month_ratio(db : Session, month: int, year: int, fafa: float) -> MonthRatio:

    existing = db.query(MonthRatio).filter(
        MonthRatio.month == month,
        MonthRatio.year == year,
    ).first()

    if existing:
        existing.fafa_ratio = fafa
    else:
        existing = MonthRatio(month=month, year=year, fafa_ratio=fafa)
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing

def get_month_totals(db: Session, month : int, year : int) -> dict:
    def payer_sums(model):
        rows = db.query(
            model.paid_by,
            func.coalesce(func.sum(model.value), 0).label("total")
        ).filter(
            model.month == month,
            model.year == year
        ).group_by(model.paid_by).all()

        return {
            row.paid_by: float(row.total) for row in rows
        }
    var = payer_sums(VariableExpense)
    reg = payer_sums(RegularExpense)
    return {
        "variable_total": sum(var.values()),
        "regular_total": sum(reg.values()),
        "fafa_paid": var.get("FAFA", 0.0) + reg.get("FAFA", 0.0),
        "fefe_paid": var.get("FEFE", 0.0) + reg.get("FEFE", 0.0)
    }
